from pathlib import Path

# 默认端口
DEFAULT_PORT = 6789


# 缓存目录相关函数
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


def get_log_file_path() -> Path:
    """获取日志文件路径"""
    log_dir = get_cache_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "embed_server.log"
