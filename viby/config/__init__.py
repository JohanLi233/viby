"""
viby 配置包
"""

from viby.config.app_config import Config
from viby.config.wizard import run_config_wizard

config = Config.get_instance()

__all__ = ["Config", "run_config_wizard", "config"]
