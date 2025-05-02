"""
viby 配置管理模块
"""

import os
import yaml
from typing import Dict, Any, Optional


class Config:
    """viby 应用的配置管理器"""
    
    def __init__(self):
        # Default configuration parameters
        self.model = "qwen3:30b"
        self.temperature = 0.7
        self.max_tokens = 40960
        self.base_url = "http://localhost:11434"
        self.api_timeout = 300
        self.api_key = ""
        self.language = "en-US"  # options: en-US, zh-CN

        self.config_dir = os.path.join(os.path.expanduser("~"), ".config", "viby")
        self.config_path = os.path.join(self.config_dir, "config.yaml")

        # 确保配置目录存在
        os.makedirs(self.config_dir, exist_ok=True)

        # 如果配置文件不存在，标记为首次启动
        self.is_first_run = not os.path.exists(self.config_path)
        if self.is_first_run:
            # 先保存默认配置，稍后会被通过向导替换
            self.save_config()
        
        # 如果存在则加载配置
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from YAML file"""
        path = self.config_path
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                if not config_data:
                    return
                # Update instance attributes from config file
                for key, value in config_data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
        except Exception as e:
            print(f"Warning: Could not load config from {path}: {e}")
    
    def save_config(self) -> None:
        """将当前配置保存到 YAML 文件"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        config_data = {
            key: value for key, value in self.__dict__.items()
            if not key.startswith('_') and key != 'config_path' and key != 'config_dir' and key != 'is_first_run'
        }
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(config_data, f, sort_keys=False)
        except Exception as e:
            print(f"Warning: Could not save config to {self.config_path}: {e}")
    
    def get_model_config(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """获取指定模型的配置"""
        model = model_name or self.model
        model_config = {
            "model": model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "base_url": self.base_url,
            "api_key": self.api_key,
        }
        return model_config
