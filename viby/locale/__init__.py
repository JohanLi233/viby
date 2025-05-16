"""
多语言提示管理模块
"""

import os
import yaml


class TextManager:
    """管理多语言提示和界面文本"""

    def __init__(self, config):
        self.config = config
        self.texts = {}
        self.load_texts()

    def load_texts(self) -> None:
        """根据配置加载对应语言的文本，只支持 YAML 格式"""
        base_dir = os.path.dirname(__file__)
        lang = self.config.language
        yaml_file = os.path.join(base_dir, f"{lang}.yaml")
        if not os.path.isfile(yaml_file):
            yaml_file = os.path.join(base_dir, "en-US.yaml")
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        self.texts = data

    def get(self, group: str, key: str, *args) -> str:
        """
        获取指定组和键的文本

        Args:
            group: 文本组名称，如 'GENERAL', 'SHELL'
            key: 文本键名
            *args: 格式化参数

        Returns:
            格式化后的文本
        """
        if group in self.texts and key in self.texts[group]:
            text = self.texts[group][key]
            if args:
                return text.format(*args)
            return text
        return f"[missing:{group}.{key}]"


# 全局文本管理器实例，在应用启动时初始化
text_manager = None


def init_text_manager(config) -> None:
    """初始化全局文本管理器"""
    global text_manager
    text_manager = TextManager(config)


def get_text(group: str, key: str, *args) -> str:
    """便捷函数，获取文本"""
    global text_manager
    if text_manager is None:
        raise RuntimeError(
            "Text manager not initialized, please call init_text_manager(config) first."
        )
    return text_manager.get(group, key, *args)
