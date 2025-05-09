"""
Logging utilities for viby
"""

import os
import logging
import platform
from pathlib import Path


def get_logs_path() -> Path:
    """
    获取适合当前操作系统的日志文件路径
    确保跨平台兼容性
    """
    system = platform.system()

    if system == "Windows":
        # Windows 上使用 %APPDATA%
        base_dir = Path(os.environ.get("APPDATA", os.path.expanduser("~")))
    else:
        base_dir = Path.home() / ".local" / "share" / "logs"

    # 确保目录存在
    logs_dir = base_dir / "viby"
    logs_dir.mkdir(parents=True, exist_ok=True)

    return logs_dir / "viby.log"


def setup_logging(
    level: int = logging.INFO, log_to_file: bool = False
) -> logging.Logger:
    """
    设置和配置日志器

    Args:
        level: 日志级别，默认为INFO
        log_to_file: 是否将日志写入文件

    Returns:
        配置好的日志器
    """
    logger = logging.getLogger("viby")
    logger.setLevel(level)

    # 清除现有处理器
    if logger.handlers:
        logger.handlers.clear()

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 如果需要，添加文件处理器
    if log_to_file:
        try:
            log_path = get_logs_path()
            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            # logger.info(f"日志文件路径: {log_path}")
        except Exception as e:
            logger.error(f"无法设置文件日志: {str(e)}")

    return logger


def get_logger() -> logging.Logger:
    """获取已配置的viby日志器，如果尚未配置则创建一个"""
    logger = logging.getLogger("viby")
    if not logger.handlers:
        return setup_logging()
    return logger
