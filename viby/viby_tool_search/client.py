"""
MCP工具检索工具

基于embedding的MCP工具智能检索系统，根据用户查询返回最相关的MCP工具
"""

import logging
import os
import json
import signal
import time
import sys
import enum
import subprocess
from typing import Dict, Any, List, Optional, NamedTuple
import requests

# 导入locale模块
from viby.locale import get_text

# 从common模块导入共享常量和函数
from viby.viby_tool_search.common import (
    DEFAULT_PORT,
    get_pid_file_path,
    get_status_file_path,
)

logger = logging.getLogger(__name__)


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
        logger.error(
            f"{get_text('TOOLS', 'read_status_failed', '读取状态文件失败')}: {e}"
        )
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
                        uptime_parts.append(
                            f"{int(days)}{get_text('TOOLS', 'days', '天')}"
                        )
                    if hours > 0 or days > 0:
                        uptime_parts.append(
                            f"{int(hours)}{get_text('TOOLS', 'hours', '小时')}"
                        )
                    if minutes > 0 or hours > 0 or days > 0:
                        uptime_parts.append(
                            f"{int(minutes)}{get_text('TOOLS', 'minutes', '分钟')}"
                        )
                    uptime_parts.append(
                        f"{int(seconds)}{get_text('TOOLS', 'seconds', '秒')}"
                    )

                    uptime = " ".join(uptime_parts)
                except Exception as e:
                    logger.warning(
                        f"{get_text('TOOLS', 'calc_uptime_failed', '计算运行时间失败')}: {e}"
                    )

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
        logger.error(
            f"{get_text('TOOLS', 'check_status_failed', '检查服务器状态失败')}: {e}"
        )
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
            False,
            pid=status.get("pid"),
            error=get_text(
                "TOOLS", "server_already_running", "嵌入模型服务器已在运行中"
            ),
        )
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "viby.viby_tool_search.server", "--server"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        # 使用轮询方式检查服务器是否启动，最多等待10秒
        max_wait_time = 100  # 最大等待时间（秒）
        check_interval = 1  # 每次检查的间隔时间（秒）
        wait_count = 0

        while wait_count < max_wait_time:
            # 检查进程是否仍然存在，如果已经退出，则表示启动失败（很可能是模型加载失败）
            if proc.poll() is not None:
                return ServerOperationResult(
                    False,
                    error=get_text(
                        "TOOLS",
                        "server_crashed",
                        "嵌入模型服务器启动失败: 请检查嵌入模型是否下载成功",
                    ),
                )

            if is_server_running():
                return ServerOperationResult(True, pid=proc.pid)
            time.sleep(check_interval)
            wait_count += check_interval

        # 超时仍未启动
        return ServerOperationResult(
            False,
            error=get_text(
                "TOOLS", "server_start_timeout", "启动嵌入模型服务器失败: 服务未响应"
            ),
        )
    except Exception as e:
        logger.error(
            f"{get_text('TOOLS', 'server_start_error', '启动服务器失败')}: {e}"
        )
        return ServerOperationResult(False, error=str(e))


def stop_embedding_server() -> ServerOperationResult:
    """
    停止嵌入模型服务器
    返回:
        操作结果
    """
    if not is_server_running():
        return ServerOperationResult(
            success=False,
            error=get_text("TOOLS", "server_not_running", "嵌入模型服务器未运行"),
        )
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


def search_similar_tools(query: str, top_k: int = 5) -> Dict[str, List]:
    """
    根据查询文本搜索相似的工具

    Args:
        query: 搜索查询
        top_k: 返回的最大结果数

    Returns:
        按服务器名称分组的工具列表，格式为 {server_name: [Tool对象, ...], ...}
    """
    if not is_server_running():
        # 如果服务未运行，返回空列表
        logger.warning(
            get_text(
                "TOOLS",
                "embedding_server_not_running",
                "嵌入模型服务未运行，无法搜索工具",
            )
        )
        return {}

    try:
        logger.debug(
            f"{get_text('TOOLS', 'sending_search_request', '向嵌入服务器发送搜索请求')}: query='{query}', top_k={top_k}"
        )
        response = requests.post(
            f"http://localhost:{DEFAULT_PORT}/search",
            json={"query": query, "top_k": top_k},
            timeout=30,  # 增加超时时间，避免复杂查询超时
        )

        if response.status_code == 200:
            results = response.json()
            logger.debug(
                f"{get_text('TOOLS', 'search_success', '搜索成功，找到')} {len(results)} {get_text('TOOLS', 'related_tools', '个相关工具')}"
            )
            return results
        else:
            logger.error(
                f"{get_text('TOOLS', 'search_failed', '搜索工具失败')}: {get_text('TOOLS', 'status_code', '状态码')}={response.status_code}, {get_text('TOOLS', 'response', '响应')}={response.text}"
            )
            return {}
    except requests.Timeout:
        logger.error(get_text("TOOLS", "search_timeout", "搜索请求超时"))
        return {}
    except requests.ConnectionError:
        logger.error(get_text("TOOLS", "connect_server_failed", "连接嵌入服务器失败"))
        return {}
    except Exception as e:
        logger.error(
            f"{get_text('TOOLS', 'call_server_failed', '调用嵌入模型服务失败')}: {str(e)}",
            exc_info=True,
        )
        return {}


def update_tools() -> bool:
    """
    更新工具嵌入向量

    Returns:
        是否成功更新
    """
    if not is_server_running():
        # 如果服务未运行，返回False
        logger.warning(
            get_text(
                "TOOLS",
                "embedding_server_not_running_cannot_update",
                "嵌入模型服务未运行，无法更新工具",
            )
        )
        return False

    try:
        # 调用服务器的更新端点
        response = requests.post(
            f"http://localhost:{DEFAULT_PORT}/update",
            timeout=300,  # 更新可能需要更长时间
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("success", False)
        else:
            logger.error(
                f"{get_text('TOOLS', 'update_failed', '更新工具失败')}: {response.status_code} {response.text}"
            )
            return False
    except Exception as e:
        logger.error(
            f"{get_text('TOOLS', 'call_server_failed', '调用嵌入模型服务失败')}: {e}"
        )
        return False
