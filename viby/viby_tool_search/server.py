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
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from datetime import datetime

from viby.viby_tool_search.embedding_manager import EmbeddingManager
from viby.mcp import list_tools
from viby.locale import get_text
from viby.viby_tool_search.common import (
    DEFAULT_PORT,
    get_pid_file_path,
    get_status_file_path,
    get_log_file_path,
)

# 配置日志
logger = logging.getLogger(__name__)


# 配置日志格式和处理器
def setup_logging():
    """配置日志记录器"""
    log_file = get_log_file_path()

    # 创建格式化器
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 清除已有的处理器，避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 添加处理器
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logger.info(f"嵌入服务日志将保存到: {log_file}")


# 请求模型
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


def run_server():
    """运行FastAPI服务器"""
    # 配置日志
    setup_logging()

    # 创建FastAPI应用
    app = FastAPI(title="Viby Embedding Server")

    # 创建并预热模型
    embedding_manager = EmbeddingManager()
    if not embedding_manager._load_model():  # 预加载模型
        logger.error(
            get_text(
                "TOOLS",
                "model_load_failed_server_exit",
                "嵌入模型加载失败，服务器启动终止",
            )
        )
        sys.exit(1)  # 模型加载失败，退出程序

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

    logger.info(f"嵌入服务器已启动: PID={os.getpid()}, 端口={DEFAULT_PORT}")

    # 健康检查端点
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "tools_count": len(embedding_manager.tool_embeddings)}

    # 搜索工具端点
    @app.post("/search")
    async def search(request: SearchRequest):
        if not request.query:
            raise HTTPException(
                status_code=400,
                detail=get_text("TOOLS", "query_cannot_be_empty", "查询文本不能为空"),
            )

        try:
            logger.info(f"搜索请求: query='{request.query}', top_k={request.top_k}")
            results = embedding_manager.search_similar_tools(
                request.query, request.top_k
            )
            logger.info(
                f"搜索完成: 找到 {sum(len(tools) for tools in results.values())} 个结果"
            )
            return results
        except Exception as e:
            logger.error(f"{get_text('TOOLS', 'search_failed', '搜索失败')}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # 更新工具端点
    @app.post("/update")
    async def update_tools():
        try:
            logger.info("开始更新工具嵌入向量")
            # 确保缓存目录存在
            embedding_manager.cache_dir.mkdir(parents=True, exist_ok=True)

            # 收集并检查MCP工具
            tools_by_server = list_tools()
            total_tools = sum(len(tools) for tools in tools_by_server.values())
            if total_tools == 0:
                logger.warning(get_text("TOOLS", "no_mcp_tools", "没有可用的MCP工具"))
                return {
                    "success": False,
                    "message": get_text("TOOLS", "no_mcp_tools", "没有可用的MCP工具"),
                }

            # 更新嵌入向量
            logger.info(f"准备更新 {total_tools} 个工具的嵌入向量")
            updated = embedding_manager.update_tool_embeddings(tools_by_server)
            logger.info(
                f"{get_text('TOOLS', 'embedding_update', '嵌入向量更新')}{get_text('TOOLS', 'success' if updated else 'failed', '成功' if updated else '失败')}"
            )

            # 更新状态文件（如果需要）
            if updated:
                status_file = get_status_file_path()
                if status_file.exists():
                    try:
                        with open(status_file, "r+") as f:
                            status = json.load(f)
                            status["tools_count"] = len(
                                embedding_manager.tool_embeddings
                            )
                            status["last_update"] = datetime.now().isoformat()
                            f.seek(0)
                            json.dump(status, f)
                            f.truncate()
                    except Exception as e:
                        logger.error(
                            f"{get_text('TOOLS', 'update_status_failed', '更新状态文件失败')}: {e}"
                        )

            return {
                "success": updated,
                "tool_count": total_tools,
                "server_count": len(tools_by_server),
            }
        except Exception as e:
            logger.error(
                get_text("TOOLS", "update_tools_failed", "更新工具失败"), exc_info=True
            )
            raise HTTPException(status_code=500, detail=str(e))

    # 关闭服务器端点
    def shutdown_server():
        # 延迟1秒关闭，确保响应能够正常返回
        time.sleep(1)
        logger.info("嵌入服务器正在关闭...")
        os.kill(os.getpid(), signal.SIGTERM)

    @app.post("/shutdown")
    async def shutdown(background_tasks: BackgroundTasks):
        background_tasks.add_task(shutdown_server)
        return {
            "message": get_text("TOOLS", "server_shutting_down", "服务器正在关闭...")
        }

    # 启动服务器
    uvicorn.run(app, host="localhost", port=DEFAULT_PORT)


if __name__ == "__main__":
    from viby.config import Config
    from viby.locale import init_text_manager

    config = Config()
    init_text_manager(config)
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        # 启动作为独立服务器
        run_server()
