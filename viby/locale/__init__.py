"""
多语言提示管理模块
"""

import importlib


class TextManager:
    """管理多语言提示和界面文本"""
    
    def __init__(self, config):
        self.config = config
        self.texts = {}
        self.load_texts()
    
    def load_texts(self) -> None:
        """根据配置加载对应语言的文本"""
        try:
            # 动态导入语言模块
            lang_module = importlib.import_module(f"viby.locale.{self.config.language}")
            
            # 加载所有文本组
            for key in dir(lang_module):
                if key.isupper() and not key.startswith("__"):
                    self.texts[key] = getattr(lang_module, key)
        except ImportError:
            # 如果找不到语言模块，回退到英文
            print(f"警告: 未找到语言 '{self.config.language}'，使用默认语言 'en-US'")
            self.config.language = "en-US"
            lang_module = importlib.import_module("viby.locale.en-US")
            
            for key in dir(lang_module):
                if key.isupper() and not key.startswith("__"):
                    self.texts[key] = getattr(lang_module, key)

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
        raise RuntimeError("Text manager not initialized, please call init_text_manager(config) first.")
    return text_manager.get(group, key, *args)
