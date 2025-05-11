"""
viby 配置管理模块
"""

import os
import yaml
import platform
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ModelProfileConfig:
    name: str = ""
    api_base_url: Optional[str] = None
    api_key: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None


class Config:
    """viby 应用的配置管理器"""

    def __init__(self):
        # 全局设置
        self.api_timeout: int = 300
        self.language: str = "en-US"  # options: en-US, zh-CN
        self.enable_mcp: bool = True
        self.mcp_config_folder: Optional[str] = None
        self.enable_yolo_mode: bool = False  # yolo模式默认关闭

        # 模型配置
        self.default_model: ModelProfileConfig = ModelProfileConfig(name="qwen3:30b")
        self.think_model: Optional[ModelProfileConfig] = ModelProfileConfig(
            name=""
        )  # 使用空名称初始化
        self.fast_model: Optional[ModelProfileConfig] = ModelProfileConfig(
            name=""
        )  # 使用空名称初始化

        # 配置文件路径
        self.config_dir: Path = self._get_config_dir()
        self.config_path: Path = self.config_dir / "config.yaml"

        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.is_first_run: bool = not self.config_path.exists()
        if self.is_first_run:
            self.save_config()  # 保存初始配置

        self.load_config()

    def _get_config_dir(self) -> Path:
        """获取适合当前操作系统的配置目录路径"""
        system = platform.system()

        if system == "Windows":
            # Windows上使用 %APPDATA%\viby
            base_dir = Path(os.environ.get("APPDATA", str(Path.home())))
            return base_dir / "viby"
        else:
            return Path.home() / ".config" / "viby"

    def _to_dict(self, obj: Any) -> Any:
        """将对象转换为字典，处理嵌套对象"""
        if hasattr(obj, "__dict__"):
            # 对ModelProfileConfig，保留所有字段，即使是None
            if isinstance(obj, ModelProfileConfig):
                return {k: self._to_dict(v) for k, v in obj.__dict__.items()}
            else:
                return {
                    k: self._to_dict(v)
                    for k, v in obj.__dict__.items()
                    if v is not None
                }
        elif isinstance(obj, list):
            return [self._to_dict(i) for i in obj]
        return obj

    def load_config(self) -> None:
        """从YAML文件加载配置"""
        try:
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config_data = yaml.safe_load(f) or {}

                # 加载模型配置
                default_model_data = config_data.get("default_model")
                if default_model_data and isinstance(default_model_data, dict):
                    model_profile = ModelProfileConfig()
                    model_profile.name = default_model_data.get("name", "")
                    model_profile.api_base_url = default_model_data.get("api_base_url")
                    model_profile.api_key = default_model_data.get("api_key")
                    model_profile.max_tokens = default_model_data.get("max_tokens")
                    model_profile.temperature = default_model_data.get("temperature")
                    model_profile.top_p = default_model_data.get("top_p")
                    self.default_model = model_profile

                think_model_data = config_data.get("think_model")
                if think_model_data and isinstance(think_model_data, dict):
                    model_profile = ModelProfileConfig()
                    model_profile.name = think_model_data.get("name", "")
                    model_profile.api_base_url = think_model_data.get("api_base_url")
                    model_profile.api_key = think_model_data.get("api_key")
                    model_profile.max_tokens = think_model_data.get("max_tokens")
                    model_profile.temperature = think_model_data.get("temperature")
                    model_profile.top_p = think_model_data.get("top_p")
                    self.think_model = model_profile
                elif not think_model_data:
                    self.think_model = None

                fast_model_data = config_data.get("fast_model")
                if fast_model_data and isinstance(fast_model_data, dict):
                    model_profile = ModelProfileConfig()
                    model_profile.name = fast_model_data.get("name", "")
                    model_profile.api_base_url = fast_model_data.get("api_base_url")
                    model_profile.api_key = fast_model_data.get("api_key")
                    model_profile.max_tokens = fast_model_data.get("max_tokens")
                    model_profile.temperature = fast_model_data.get("temperature")
                    model_profile.top_p = fast_model_data.get("top_p")
                    self.fast_model = model_profile
                elif not fast_model_data:
                    self.fast_model = None

                # 加载全局设置
                self.api_timeout = int(
                    config_data.get("api_timeout", self.api_timeout)
                )
                self.language = config_data.get("language", self.language)
                self.enable_mcp = bool(
                    config_data.get("enable_mcp", self.enable_mcp)
                )
                self.mcp_config_folder = config_data.get(
                    "mcp_config_folder", self.mcp_config_folder
                )
                self.enable_yolo_mode = bool(
                    config_data.get("enable_yolo_mode", self.enable_yolo_mode)
                )

        except Exception as e:
            print(f"警告: 无法从 {self.config_path} 加载配置: {e}。使用默认值。")
            if not isinstance(self.default_model, ModelProfileConfig):
                self.default_model = ModelProfileConfig(name="qwen3:30b")
            # 确保think_model和fast_model总是有有效值或者为None
            if self.think_model and not isinstance(self.think_model, ModelProfileConfig):
                self.think_model = None
            if self.fast_model and not isinstance(self.fast_model, ModelProfileConfig):
                self.fast_model = None

    def save_config(self) -> None:
        """将当前配置保存到 YAML 文件"""
        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)

        config_data = {
            "default_model": self._to_dict(self.default_model)
            if self.default_model
            else None,
            "think_model": self._to_dict(self.think_model)
            if self.think_model and self.think_model.name
            else None,
            "fast_model": self._to_dict(self.fast_model)
            if self.fast_model and self.fast_model.name
            else None,
            "api_timeout": self.api_timeout,
            "language": self.language,
            "enable_mcp": self.enable_mcp,
            "mcp_config_folder": self.mcp_config_folder,
            "enable_yolo_mode": self.enable_yolo_mode,
        }

        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(
                    config_data, f, sort_keys=False, default_flow_style=False
                )
        except Exception as e:
            print(f"警告: 无法保存配置到 {self.config_path}: {e}")

    def get_model_config(self, model_type: str = "default") -> Dict[str, Any]:
        """获取指定模型类型的完整配置，回退到全局默认值"""
        profile_to_use: Optional[ModelProfileConfig] = None

        if model_type == "default":
            profile_to_use = self.default_model
        elif model_type == "think" and self.think_model and self.think_model.name:
            profile_to_use = self.think_model
        elif model_type == "fast" and self.fast_model and self.fast_model.name:
            profile_to_use = self.fast_model
        else:
            profile_to_use = self.default_model

        if not profile_to_use or not profile_to_use.name:
            return {
                "model": None,  # 不再提供默认模型，必须明确指定
                "temperature": None,
                "top_p": None,
                "max_tokens": None,
                "base_url": "http://localhost:1234/v1",  # 默认API基础URL
                "api_key": None,
                "api_timeout": self.api_timeout,
            }

        resolved_base_url = profile_to_use.api_base_url or "http://localhost:1234/v1"
        resolved_api_key = profile_to_use.api_key

        # 使用配置中的值
        resolved_max_tokens = profile_to_use.max_tokens
        resolved_temperature = profile_to_use.temperature
        resolved_top_p = profile_to_use.top_p

        return {
            "model": profile_to_use.name,
            "temperature": resolved_temperature,
            "max_tokens": resolved_max_tokens,
            "base_url": resolved_base_url,
            "api_key": resolved_api_key,
            "api_timeout": self.api_timeout,
            "top_p": resolved_top_p,
        }
