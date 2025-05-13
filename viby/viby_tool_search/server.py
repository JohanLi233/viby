"""
嵌入模型后台服务

提供嵌入模型HTTP服务，避免每次工具搜索时重新加载模型
"""

import os
import json
import signal
import logging
import time
import sys
import uvicorn
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from datetime import datetime

from viby.viby_tool_search.embedding_manager import EmbeddingManager
from viby.mcp import list_tools
from viby.viby_tool_search.common import (
    DEFAULT_PORT,
    get_pid_file_path,
    get_status_file_path
)

# 配置日志
logger = logging.getLogger(__name__)


# 请求模型
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class ShutdownRequest(BaseModel):
    pass


def run_server():
    """运行FastAPI服务器"""
    # 创建FastAPI应用
    app = FastAPI(title="Viby Embedding Server")

    # 确保工具嵌入目录存在

    tool_embeddings_dir = Path.home() / ".config" / "viby" / "tool_embeddings"
    tool_embeddings_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"确保工具嵌入目录存在: {tool_embeddings_dir}")

    # 创建并预热模型
    embedding_manager = EmbeddingManager()
    embedding_manager._load_model()  # 预加载模型

    # 确保嵌入文件目录结构完整
    embedding_manager.cache_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"确保嵌入管理器缓存目录存在: {embedding_manager.cache_dir}")

    # 记录PID
    pid_file = get_pid_file_path()
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))

    # 记录状态
    status_file = get_status_file_path()
    status = {
        "running": True,
        "pid": os.getpid(),
        "port": DEFAULT_PORT,
        "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tools_count": len(embedding_manager.tool_embeddings),
    }
    with open(status_file, "w") as f:
        json.dump(status, f)

    # 健康检查端点
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "tools_count": len(embedding_manager.tool_embeddings)}

    # 搜索工具端点
    @app.post("/search")
    async def search(request: SearchRequest):
        if not request.query:
            raise HTTPException(status_code=400, detail="查询文本不能为空")

        try:
            results = embedding_manager.search_similar_tools(
                request.query, request.top_k
            )
            return results
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # 更新工具端点
    @app.post("/update")
    async def update_tools():
        import os
        from pathlib import Path

        try:
            # 再次确保所有必要的目录都存在
            tool_embeddings_dir = Path.home() / ".config" / "viby" / "tool_embeddings"
            tool_embeddings_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"更新操作：确保工具嵌入目录存在: {tool_embeddings_dir}")

            # 确保嵌入文件目录结构完整
            embedding_manager.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(
                f"更新操作：确保嵌入管理器缓存目录存在: {embedding_manager.cache_dir}"
            )

            # 检查目录权限
            if not os.access(embedding_manager.cache_dir, os.W_OK):
                logger.warning(f"警告：没有{embedding_manager.cache_dir}的写入权限")
                # 尝试修复权限
                try:
                    os.chmod(embedding_manager.cache_dir, 0o755)
                    logger.info(f"已尝试修复目录权限: {embedding_manager.cache_dir}")
                except Exception as perm_err:
                    logger.error(f"修复权限失败: {perm_err}")

            # 收集MCP工具 - 注意这行的缩进，之前的代码缩进错误
            logger.info("开始收集MCP工具...")
            # list_tools() 返回格式是 {server_name: [...tools]}
            tools_by_server = list_tools()
            logger.info(f"成功收集了 {len(tools_by_server)} 个MCP服务器的工具")
            
            # 检查返回的数据结构
            for server_name, tools in tools_by_server.items():
                logger.info(f"服务器 {server_name}: {len(tools)} 个工具")
            
            # 判断是否有工具
            total_tools = sum(len(tools) for tools in tools_by_server.values())
            if total_tools == 0:
                logger.warning("没有可用的MCP工具或MCP功能未启用")
                return {"success": False, "message": "没有可用的MCP工具或MCP功能未启用"}
            
            logger.info(f"工具总数: {total_tools}")
            
            # 这里直接将按服务器分组的工具传给embedding_manager
            tools_dict = tools_by_server

            # 输出详细的工具信息用于调试
            logger.debug(f"收集到的工具列表: {list(tools_dict.keys())}")

            # 创建工具嵌入文件备份
            try:
                tool_info_file = embedding_manager.tool_info_file
                if tool_info_file.exists():
                    import shutil

                    backup_file = tool_info_file.with_suffix(".json.bak")
                    shutil.copy2(tool_info_file, backup_file)
                    logger.info(f"已创建工具信息备份: {backup_file}")
            except Exception as e:
                logger.warning(f"创建工具信息备份失败: {e}")

            # 在更新嵌入向量前记录目录状态
            tool_embeddings_dir = embedding_manager.cache_dir
            logger.info(
                f"更新嵌入向量前目录状态: {tool_embeddings_dir}，是否存在: {tool_embeddings_dir.exists()}，是否可写: {os.access(tool_embeddings_dir, os.W_OK)}"
            )

            # 列出已存在的文件
            if tool_embeddings_dir.exists():
                existing_files = list(tool_embeddings_dir.glob("*"))
                logger.info(f"目录中的文件: {[f.name for f in existing_files]}")

            # 更新嵌入向量
            try:
                updated = embedding_manager.update_tool_embeddings(tools_dict)
                logger.info(f"嵌入向量更新结果: {'成功' if updated else '失败'}")
            except Exception as update_err:
                logger.error(f"更新嵌入向量时出现异常: {update_err}", exc_info=True)
                # 尽管出错，继续执行以获取更多诊断信息
                updated = False

            # 更新后再次检查目录状态
            logger.info(
                f"更新嵌入向量后目录状态: {tool_embeddings_dir}，是否存在: {tool_embeddings_dir.exists()}"
            )
            if tool_embeddings_dir.exists():
                after_files = list(tool_embeddings_dir.glob("*"))
                logger.info(f"更新后目录中的文件: {[f.name for f in after_files]}")

            # 验证更新结果
            verification_result = {"verified": False, "missing_tools": []}
            try:
                # 读取更新后的工具信息文件
                with open(embedding_manager.tool_info_file, "r", encoding="utf-8") as f:
                    saved_data = json.load(f)

                # 计算所有工具名称
                all_tool_names = []
                for server_name, tools_list in tools_dict.items():
                    for tool in tools_list:
                        if isinstance(tool, dict) and "name" in tool:
                            all_tool_names.append(tool["name"])
                
                # 比较工具数量
                missing_tools = set(all_tool_names) - set(saved_data.keys())
                verification_result["verified"] = len(missing_tools) == 0
                verification_result["missing_tools"] = list(missing_tools)
                
                # 记录实际保存和期望的工具数量
                verification_result["saved_count"] = len(saved_data)
                verification_result["expected_count"] = len(all_tool_names)

            except Exception as e:
                logger.error(f"验证工具更新结果时出错: {e}")
                verification_result["error"] = str(e)

            # 如果更新了嵌入向量，还需要更新状态文件
            if updated:
                # 更新状态文件中的工具数量
                status_file = get_status_file_path()
                if status_file.exists():
                    try:
                        with open(status_file, "r") as f:
                            status = json.load(f)
                        status["tools_count"] = len(embedding_manager.tool_embeddings)
                        status["last_update"] = datetime.now().isoformat()
                        logger.info(f"更新状态文件，工具数量: {status['tools_count']}")
                        with open(status_file, "w") as f:
                            json.dump(status, f)
                    except Exception as e:
                        logger.error(f"更新状态文件失败: {e}")

            result = {
                "success": updated,
                "message": "已成功更新MCP工具嵌入向量"
                if updated
                else "MCP工具嵌入向量已是最新，无需更新",
                "tool_count": len(all_tool_names),
                "server_count": len(tools_dict),
                "tools": all_tool_names,  # 返回工具名称列表以便于调试
                "verification": verification_result,
            }
            logger.info(
                f"更新结果: {result['message']}, 服务器: {result['server_count']}, 工具: {result['tool_count']}"
            )
            return result
        except Exception as e:
            logger.error(f"更新工具失败: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"更新工具失败: {str(e)}")

    # 关闭服务器端点
    def shutdown_server():
        # 延迟1秒关闭，确保响应能够正常返回
        time.sleep(1)
        os.kill(os.getpid(), signal.SIGTERM)

    @app.post("/shutdown")
    async def shutdown(background_tasks: BackgroundTasks):
        background_tasks.add_task(shutdown_server)
        return {"message": "服务器正在关闭..."}

    # 启动服务器
    uvicorn.run(app, host="localhost", port=DEFAULT_PORT)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        # 启动作为独立服务器
        run_server() 