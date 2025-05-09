"""
测试帮助函数，提供通用的测试辅助功能
"""

import json
import time
import tempfile
from typing import Dict, Any, Callable
from pathlib import Path


def create_temp_config(config_data: Dict[str, Any]) -> Path:
    """
    创建临时配置文件用于测试

    Args:
        config_data: 配置数据

    Returns:
        临时配置文件路径
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".yaml")
    temp_file.close()

    config_path = Path(temp_file.name)
    with open(config_path, "w", encoding="utf-8") as f:
        import yaml

        yaml.dump(config_data, f)

    return config_path


def get_test_resource_path(filename: str) -> Path:
    """
    获取测试资源文件路径

    Args:
        filename: 资源文件名

    Returns:
        资源文件完整路径
    """
    resource_dir = Path(__file__).parent / "resources"
    return resource_dir / filename


def load_test_data(filename: str) -> Dict[str, Any]:
    """
    加载测试数据

    Args:
        filename: 数据文件名

    Returns:
        加载的数据
    """
    data_path = get_test_resource_path(filename)
    with open(data_path, "r", encoding="utf-8") as f:
        if filename.endswith(".json"):
            return json.load(f)
        elif filename.endswith(".yaml") or filename.endswith(".yml"):
            import yaml

            return yaml.safe_load(f)
    raise ValueError(f"不支持的文件格式: {filename}")


class PerformanceTimer:
    """用于测量代码性能的计时器"""

    def __init__(self, name: str = ""):
        self.name = name
        self.start_time = 0
        self.end_time = 0
        self.duration = 0

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time

    def result(self) -> Dict[str, Any]:
        """返回计时结果"""
        return {
            "name": self.name,
            "duration": self.duration,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }


def measure_performance(
    func: Callable, iterations: int = 1, **kwargs
) -> Dict[str, Any]:
    """
    测量函数性能

    Args:
        func: 要测量的函数
        iterations: 迭代次数
        **kwargs: 传递给函数的参数

    Returns:
        性能测量结果
    """
    results = []
    total_time = 0

    for i in range(iterations):
        start_time = time.time()
        func(**kwargs)
        end_time = time.time()
        duration = end_time - start_time
        results.append(duration)
        total_time += duration

    return {
        "function_name": func.__name__,
        "iterations": iterations,
        "total_time": total_time,
        "average_time": total_time / iterations,
        "min_time": min(results),
        "max_time": max(results),
        "all_times": results,
    }
