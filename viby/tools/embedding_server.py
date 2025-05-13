"""
嵌入模型后台服务

提供嵌入模型HTTP服务，避免每次工具搜索时重新加载模型
"""

import os
import json
import signal
import logging
import subprocess
import time
import requests
import sys
import enum
import uvicorn
from pathlib import Path
from typing import Optional, Dict, List, Any, NamedTuple
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel

from viby.tools.embedding_utils import ToolEmbeddingManager

# 配置日志
logger = logging.getLogger(__name__)

# 默认服务端口
DEFAULT_PORT = 8765


# 服务器状态枚举
class EmbeddingServerStatus(enum.Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    UNKNOWN = "unknown"


# 服务器状态结果类
class ServerStatusResult(NamedTuple):
    status: EmbeddingServerStatus
    pid: Optional[int] = None
    url: Optional[str] = None
    uptime: Optional[str] = None
    start_time: Optional[str] = None
    tools_count: Optional[int] = None
    error: Optional[str] = None


# 服务器操作结果类
class ServerOperationResult(NamedTuple):
    success: bool
    pid: Optional[int] = None
    error: Optional[str] = None


# 请求模型
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class ShutdownRequest(BaseModel):
    pass


# 统一缓存目录
def get_cache_dir() -> Path:
    cache_dir = Path.home() / ".config" / "viby" / "embedding_server"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_pid_file_path() -> Path:
    """获取PID文件路径"""
    return get_cache_dir() / "embed_server.pid"


def get_status_file_path() -> Path:
    """获取状态文件路径"""
    return get_cache_dir() / "status.json"


def is_server_running() -> bool:
    """
    检查嵌入服务器是否正在运行

    返回:
        是否运行
    """
    try:
        response = requests.get(f"http://localhost:{DEFAULT_PORT}/health", timeout=100)
        return response.status_code == 200
    except requests.RequestException:
        return False


def get_server_status() -> Dict[str, Any]:
    """
    获取服务器状态

    返回:
        状态信息字典
    """
    status_file = get_status_file_path()
    default_status = {
        "running": False,
        "pid": None,
        "port": DEFAULT_PORT,
        "start_time": None,
        "tools_count": 0,
    }

    if not status_file.exists():
        return default_status

    try:
        with open(status_file, "r") as f:
            status = json.load(f)
        # 更新并返回运行状态
        status["running"] = is_server_running()
        return status
    except Exception as e:
        logger.error(f"读取状态文件失败: {e}")
        return default_status


def check_server_status() -> ServerStatusResult:
    """
    检查嵌入服务器状态

    返回:
        服务器状态结果
    """
    try:
        is_running = is_server_running()
        if is_running:
            status_data = get_server_status()
            pid = status_data.get("pid")
            port = status_data.get("port", DEFAULT_PORT)
            start_time = status_data.get("start_time")
            tools_count = status_data.get("tools_count", 0)

            # 计算运行时间
            uptime = None
            if start_time:
                try:
                    start_timestamp = time.mktime(
                        time.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                    )
                    uptime_seconds = time.time() - start_timestamp

                    # 格式化运行时间
                    days, remainder = divmod(uptime_seconds, 86400)
                    hours, remainder = divmod(remainder, 3600)
                    minutes, seconds = divmod(remainder, 60)

                    uptime_parts = []
                    if days > 0:
                        uptime_parts.append(f"{int(days)}天")
                    if hours > 0 or days > 0:
                        uptime_parts.append(f"{int(hours)}小时")
                    if minutes > 0 or hours > 0 or days > 0:
                        uptime_parts.append(f"{int(minutes)}分钟")
                    uptime_parts.append(f"{int(seconds)}秒")

                    uptime = " ".join(uptime_parts)
                except Exception as e:
                    logger.warning(f"计算运行时间失败: {e}")

            return ServerStatusResult(
                status=EmbeddingServerStatus.RUNNING,
                pid=pid,
                url=f"http://localhost:{port}",
                uptime=uptime,
                start_time=start_time,
                tools_count=tools_count,
            )
        else:
            return ServerStatusResult(status=EmbeddingServerStatus.STOPPED)
    except Exception as e:
        logger.error(f"检查服务器状态失败: {e}")
        return ServerStatusResult(status=EmbeddingServerStatus.UNKNOWN, error=str(e))


def start_embedding_server() -> ServerOperationResult:
    """
    启动嵌入模型服务器
    返回:
        操作结果
    """
    if is_server_running():
        status = get_server_status()
        return ServerOperationResult(
            False, pid=status.get("pid"), error="嵌入模型服务器已在运行中"
        )
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "viby.tools.embedding_server", "--server"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        
        # 使用轮询方式检查服务器是否启动，最多等待10秒
        max_wait_time = 100  # 最大等待时间（秒）
        check_interval = 1  # 每次检查的间隔时间（秒）
        wait_count = 0
        
        while wait_count < max_wait_time:
            if is_server_running():
                return ServerOperationResult(True, pid=proc.pid)
            time.sleep(check_interval)
            wait_count += check_interval
            
        # 超时仍未启动
        return ServerOperationResult(
            False, error="启动嵌入模型服务器失败: 服务未响应"
        )
    except Exception as e:
        logger.error(f"启动服务器失败: {e}")
        return ServerOperationResult(False, error=str(e))


def stop_embedding_server() -> ServerOperationResult:
    """
    停止嵌入模型服务器
    返回:
        操作结果
    """
    if not is_server_running():
        return ServerOperationResult(success=False, error="嵌入模型服务器未运行")
    try:
        requests.post(f"http://localhost:{DEFAULT_PORT}/shutdown", timeout=100)
    except requests.RequestException:
        pass
    pid = None
    pid_file = get_pid_file_path()
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            os.kill(pid, signal.SIGTERM)
        except (ValueError, OSError, PermissionError):
            pass
        pid_file.unlink()
    status_file = get_status_file_path()
    if status_file.exists():
        status_file.unlink()
    return ServerOperationResult(success=True, pid=pid)


def search_tools_remote(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    远程调用嵌入服务器搜索工具

    Args:
        query: 搜索查询
        top_k: 返回的最大结果数

    Returns:
        相关工具列表
    """
    if not is_server_running():
        # 如果服务未运行，返回空列表
        logger.warning("嵌入模型服务未运行，无法搜索工具")
        return []

    try:
        response = requests.post(
            f"http://localhost:{DEFAULT_PORT}/search",
            json={"query": query, "top_k": top_k},
            timeout=100,
        )

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"搜索工具失败: {response.status_code} {response.text}")
            return []
    except Exception as e:
        logger.error(f"调用嵌入模型服务失败: {e}")
        return []


def run_server():
    """运行FastAPI服务器"""
    # 创建FastAPI应用
    app = FastAPI(title="Viby Embedding Server")

    # 创建并预热模型
    embedding_manager = ToolEmbeddingManager()
    embedding_manager._load_model()  # 预加载模型

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
        from viby.tools.tool_retrieval import collect_mcp_tools

        try:
            tools_dict = collect_mcp_tools()
            if not tools_dict:
                return {"success": False, "message": "没有可用的MCP工具或MCP功能未启用"}

            updated = embedding_manager.update_tool_embeddings(tools_dict)

            if updated:
                # 更新状态文件中的工具数量
                status_file = get_status_file_path()
                if status_file.exists():
                    try:
                        with open(status_file, "r") as f:
                            status = json.load(f)
                        status["tools_count"] = len(embedding_manager.tool_embeddings)
                        with open(status_file, "w") as f:
                            json.dump(status, f)
                    except Exception:
                        pass

            return {
                "success": updated,
                "message": "已成功更新MCP工具嵌入向量"
                if updated
                else "MCP工具嵌入向量已是最新，无需更新",
                "tool_count": len(tools_dict),
            }
        except Exception as e:
            logger.error(f"更新工具失败: {e}")
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
        run_server()
