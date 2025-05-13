"""Viby - Viby vibes everything"""

__version__ = "0.2.2"

# 使用延迟导入方式，避免立即加载所有依赖
from viby.utils.lazy_import import lazy_function

# 懒加载main函数，只在实际调用时才导入
main = lazy_function("viby.cli.main", "main")

__all__ = ["main"]
