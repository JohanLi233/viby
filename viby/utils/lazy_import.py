"""
懒加载和延迟导入工具

提供延迟导入机制，避免在启动时加载所有依赖，
只在实际需要时才导入相关模块。
"""

import importlib
import sys
import types
from typing import Any, Callable, Set, cast, List

# 跟踪已加载的延迟模块，用于调试和监控
_LOADED_LAZY_MODULES: Set[str] = set()


def lazy_import(module_name: str) -> types.ModuleType:
    """
    创建一个延迟加载的模块代理。
    只有在首次访问模块属性时才会实际导入模块。

    Args:
        module_name: 要导入的模块名称，如 "openai"

    Returns:
        一个模块代理对象，行为类似于已导入的模块
    """
    return LazyModule(module_name)


class LazyModule(types.ModuleType):
    """延迟加载的模块代理类"""

    def __init__(self, name: str):
        super().__init__(name)
        self.__actual_module = None
        self.__name = name

    def __getattr__(self, attr: str) -> Any:
        if self.__actual_module is None:
            self.__actual_module = importlib.import_module(self.__name)
            _LOADED_LAZY_MODULES.add(self.__name)

        return getattr(self.__actual_module, attr)

    def __dir__(self) -> List[str]:
        if self.__actual_module is None:
            self.__actual_module = importlib.import_module(self.__name)
            _LOADED_LAZY_MODULES.add(self.__name)

        return dir(self.__actual_module)


class LazyCallable:
    """延迟可调用对象，在首次调用时导入并执行实际函数"""

    def __init__(self, module_name: str, func_name: str):
        self.module_name = module_name
        self.func_name = func_name
        self._real_func = None

    def __call__(self, *args, **kwargs):
        if self._real_func is None:
            module = importlib.import_module(self.module_name)
            _LOADED_LAZY_MODULES.add(self.module_name)
            self._real_func = getattr(module, self.func_name)

        return self._real_func(*args, **kwargs)


def lazy_function(module_name: str, func_name: str) -> Callable:
    """
    创建一个延迟加载的函数。
    只有在首次调用函数时才会导入相关模块。

    Args:
        module_name: 模块名称
        func_name: 函数名称

    Returns:
        一个包装函数，行为类似于目标函数
    """
    return LazyCallable(module_name, func_name)


def lazy_class(module_name: str, class_name: str) -> type:
    """
    创建一个延迟加载的类引用。
    只有在首次实例化或访问类属性时才会导入相关模块。

    Args:
        module_name: 模块名称
        class_name: 类名称

    Returns:
        一个类代理，行为类似于目标类
    """

    class LazyClass:
        def __new__(cls, *args, **kwargs):
            real_class = getattr(importlib.import_module(module_name), class_name)
            _LOADED_LAZY_MODULES.add(module_name)
            return real_class(*args, **kwargs)

        def __init_subclass__(cls, **kwargs):
            real_class = getattr(importlib.import_module(module_name), class_name)
            _LOADED_LAZY_MODULES.add(module_name)
            return type(f"LazySubclassOf{class_name}", (real_class,), {})

        @classmethod
        def __class_getattr__(cls, name):
            real_class = getattr(importlib.import_module(module_name), class_name)
            _LOADED_LAZY_MODULES.add(module_name)
            return getattr(real_class, name)

    # 使用元类增强LazyClass
    class LazyMetaclass(type):
        def __getattr__(cls, name):
            real_class = getattr(importlib.import_module(module_name), class_name)
            _LOADED_LAZY_MODULES.add(module_name)
            return getattr(real_class, name)

    return cast(type, LazyMetaclass(f"Lazy{class_name}", (LazyClass,), {}))


def get_loaded_modules() -> Set[str]:
    """获取已经实际加载的延迟模块列表，用于监控和调试"""
    return _LOADED_LAZY_MODULES.copy()


def inject_lazy_module(name: str) -> None:
    """
    将延迟加载的模块注入到sys.modules中，
    这样其他试图导入该模块的代码将获得懒加载版本。

    Args:
        name: 模块名称
    """
    if name not in sys.modules:
        sys.modules[name] = lazy_import(name)
