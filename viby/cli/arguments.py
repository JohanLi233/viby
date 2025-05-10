"""
Command line argument parsing for viby
"""

import argparse
import sys
from typing import Tuple
import importlib.metadata
import pathlib
import os

from viby.locale import get_text


def get_version_string() -> str:
    """
    获取版本信息字符串，采用懒加载方式检测

    Returns:
        带有格式的版本信息字符串
    """
    # 获取基本版本 - 这很轻量，不需要懒加载
    base_version = importlib.metadata.version("viby")
    version_string = f"Viby {base_version}"

    # 仅在必要时执行开发检查
    def lazy_check_dev_mode() -> bool:
        """懒加载检查是否为开发模式"""
        try:
            # __file__ in this context is .../viby/cli/arguments.py
            # Project root should be three levels up from the directory of this file.
            current_file_path = pathlib.Path(__file__).resolve()
            project_root_marker = (
                current_file_path.parent.parent.parent / "pyproject.toml"
            )
            return project_root_marker.is_file()
        except Exception:
            return False

    # 快速检查环境变量，这比文件检查更快
    if os.environ.get("VIBY_DEV_MODE"):
        version_string += " (dev)"
    # 否则，如果需要更准确，检查文件结构
    elif lazy_check_dev_mode():
        version_string += " (dev)"

    return version_string


def get_parser() -> argparse.ArgumentParser:
    # 禁用默认的帮助选项，以便我们可以添加自定义的中文帮助选项
    parser = argparse.ArgumentParser(
        description=get_text("GENERAL", "app_description"),
        epilog=get_text("GENERAL", "app_epilog"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,  # 禁用默认的英文帮助选项
    )

    # 添加自定义的中文帮助选项
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help=get_text("GENERAL", "help_text"),
    )

    # 使用懒加载方式获取版本字符串
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=get_version_string(),
        help=get_text("GENERAL", "version_help"),
    )
    parser.add_argument("prompt", nargs="?", help=get_text("GENERAL", "prompt_help"))
    parser.add_argument(
        "--chat", "-c", action="store_true", help=get_text("GENERAL", "chat_help")
    )
    parser.add_argument(
        "--config", action="store_true", help=get_text("GENERAL", "config_help")
    )
    parser.add_argument(
        "--think", "-t", action="store_true", help=get_text("GENERAL", "think_help")
    )
    parser.add_argument(
        "--fast", "-f", action="store_true", help=get_text("GENERAL", "fast_help")
    )
    parser.add_argument(
        "--language",
        "-l",
        choices=["en-US", "zh-CN"],
        help=get_text("GENERAL", "language_help"),
    )

    # 添加token使用跟踪选项
    parser.add_argument(
        "--tokens",
        "-k",
        action="store_true",
        help=get_text("GENERAL", "tokens_help"),
    )

    # 添加性能调试参数，开发者选项，不需要本地化
    parser.add_argument(
        "--debug-performance",
        action="store_true",
        help="启用性能调试模式（开发者选项）",
    )

    return parser


def parse_arguments() -> argparse.Namespace:
    return get_parser().parse_args()


def process_input(args: argparse.Namespace) -> Tuple[str, bool]:
    """
    处理命令行参数和标准输入，组合成完整的用户输入

    Args:
        args: 解析后的命令行参数

    Returns:
        Tuple[str, bool]: (用户输入, 是否有效输入)
    """
    # 获取命令行提示词和管道上下文
    prompt = args.prompt.strip() if args.prompt else ""
    pipe_content = sys.stdin.read().strip() if not sys.stdin.isatty() else ""

    # 构造最终输入，过滤空值
    user_input = "\n".join(filter(None, [prompt, pipe_content]))

    return user_input, bool(user_input)
