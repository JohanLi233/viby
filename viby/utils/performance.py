"""
性能监控工具 - 追踪模块加载和内存使用情况
"""

import time
import sys
import os
from typing import Dict, List, Set, Optional, Tuple
import tracemalloc
from viby.utils.lazy_import import get_loaded_modules


class ImportTracker:
    """跟踪模块导入情况的工具"""

    def __init__(self):
        self.initial_modules: Set[str] = set(sys.modules.keys())
        self.new_modules: Set[str] = set()
        self.start_time = time.time()

    def update(self) -> Tuple[Set[str], float]:
        """
        更新跟踪状态，返回新导入的模块和经过的时间

        Returns:
            Tuple[Set[str], float]: (新导入的模块集合, 经过的秒数)
        """
        current_modules = set(sys.modules.keys())
        self.new_modules = current_modules - self.initial_modules
        elapsed = time.time() - self.start_time
        return self.new_modules, elapsed

    def get_module_details(self) -> List[Dict[str, str]]:
        """
        获取已加载模块的详细信息

        Returns:
            List[Dict[str, str]]: 模块信息列表
        """
        self.update()
        details = []
        for module_name in sorted(self.new_modules):
            module = sys.modules.get(module_name)
            if module:
                # 尝试获取模块文件路径
                file_path = getattr(module, "__file__", "Unknown")
                details.append({"name": module_name, "path": file_path})
        return details

    def print_report(self, title: str = "导入跟踪报告") -> None:
        """
        打印模块导入跟踪报告

        Args:
            title: 报告标题
        """
        new_modules, elapsed = self.update()
        print(f"\n==== {title} ====")
        print(f"经过时间: {elapsed:.3f}秒")
        print(f"新导入的模块数量: {len(new_modules)}")

        # 计算懒加载模块的数量
        lazy_modules = get_loaded_modules()
        print(f"懒加载的模块数量: {len(lazy_modules)}")

        # 显示前10个模块名称
        if new_modules:
            print("\n前10个导入的模块:")
            for i, module in enumerate(sorted(new_modules)[:10]):
                print(f"  {i + 1}. {module}")

        # 显示懒加载的模块
        if lazy_modules:
            print("\n懒加载的模块:")
            for i, module in enumerate(sorted(lazy_modules)):
                print(f"  {i + 1}. {module}")

        print("=" * (len(title) + 10))


class MemoryTracker:
    """内存使用跟踪工具"""

    def __init__(self):
        self.start_snapshot = None
        # 默认不启用，只有在明确调用 start() 时才启动
        self.enabled = False
        self.peak_memory = 0

    def start(self) -> None:
        """开始跟踪内存使用"""
        if not self.enabled:
            tracemalloc.start()
            self.enabled = True
        self.start_snapshot = tracemalloc.take_snapshot()
        self.peak_memory = 0

    def update_peak(self) -> int:
        """更新并返回峰值内存使用量"""
        if self.enabled:
            current = tracemalloc.get_traced_memory()[1]
            self.peak_memory = max(self.peak_memory, current)
            return self.peak_memory
        return 0

    def get_memory_usage(self) -> Tuple[int, int, Optional[List]]:
        """
        获取内存使用详情

        Returns:
            Tuple[int, int, Optional[List]]: (当前使用内存, 峰值内存, 差异统计)
        """
        if not self.enabled:
            return 0, 0, None

        current, peak = tracemalloc.get_traced_memory()
        self.peak_memory = max(self.peak_memory, peak)

        diff_stats = None
        if self.start_snapshot:
            current_snapshot = tracemalloc.take_snapshot()
            diff_stats = current_snapshot.compare_to(self.start_snapshot, "lineno")

        return current, self.peak_memory, diff_stats

    def print_report(self, title: str = "内存使用报告", top_n: int = 5) -> None:
        """
        打印内存使用报告

        Args:
            title: 报告标题
            top_n: 显示的差异统计数量
        """
        if not self.enabled:
            print(f"\n==== {title} ====")
            print("内存跟踪未启用。请先调用 start() 方法。")
            print("=" * (len(title) + 10))
            return

        current, peak, diff_stats = self.get_memory_usage()

        print(f"\n==== {title} ====")
        print(f"当前内存使用: {current / 1024 / 1024:.2f} MB")
        print(f"峰值内存使用: {peak / 1024 / 1024:.2f} MB")

        if diff_stats and top_n > 0:
            print(f"\n内存增长 Top {top_n}:")
            for stat in diff_stats[:top_n]:
                print(f"  {stat}")

        print("=" * (len(title) + 10))

    def stop(self) -> None:
        """停止内存跟踪"""
        if self.enabled:
            tracemalloc.stop()
            self.enabled = False
            self.start_snapshot = None


# 全局跟踪器实例，可在整个应用中使用
import_tracker = ImportTracker()
memory_tracker = MemoryTracker()


def get_performance_stats() -> Dict[str, any]:
    """
    获取当前的性能统计信息

    Returns:
        Dict: 性能统计信息
    """
    stats = {
        "modules": {
            "total": len(sys.modules),
            "new": len(import_tracker.new_modules),
            "lazy_loaded": len(get_loaded_modules()),
            "lazy_modules_list": list(get_loaded_modules()),
        },
        "memory": {},
    }

    if memory_tracker.enabled:
        current, peak, _ = memory_tracker.get_memory_usage()
        stats["memory"] = {
            "current_mb": current / 1024 / 1024,
            "peak_mb": peak / 1024 / 1024,
        }

    return stats


def enable_debugging() -> None:
    """启用性能调试"""
    # 设置环境变量，让其他模块知道调试已启用
    os.environ["VIBY_DEBUG_PERFORMANCE"] = "1"
    memory_tracker.start()


def is_debugging_enabled() -> bool:
    """检查性能调试是否已启用"""
    return os.environ.get("VIBY_DEBUG_PERFORMANCE") == "1"
