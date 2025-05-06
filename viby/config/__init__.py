"""
viby 配置包
"""

from viby.config.app_config import Config
from viby.config.wizard import run_config_wizard

__all__ = ["Config", "get_server_config", "run_config_wizard"]
