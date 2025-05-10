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
    """
    创建命令行参数解析器

    Returns:
        命令行参数解析器
    """
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

    # === 添加子命令支持 ===
    subparsers = parser.add_subparsers(dest="command", required=False)

    # === 历史命令 ===
    history_parser = subparsers.add_parser(
        "history", help=get_text("HISTORY", "command_help")
    )
    history_subparsers = history_parser.add_subparsers(
        dest="history_subcommand", help=get_text("HISTORY", "subcommand_help")
    )

    # 历史列表子命令
    list_parser = history_subparsers.add_parser(
        "list", help=get_text("HISTORY", "list_help")
    )
    list_parser.add_argument(
        "--limit", "-n", type=int, default=10, help=get_text("HISTORY", "limit_help")
    )

    # 历史搜索子命令
    search_parser = history_subparsers.add_parser(
        "search", help=get_text("HISTORY", "search_help")
    )
    search_parser.add_argument("query", help=get_text("HISTORY", "query_help"))
    search_parser.add_argument(
        "--limit", "-n", type=int, default=10, help=get_text("HISTORY", "limit_help")
    )

    # 历史导出子命令
    export_parser = history_subparsers.add_parser(
        "export", help=get_text("HISTORY", "export_help")
    )
    export_parser.add_argument("file", help=get_text("HISTORY", "file_help"))
    export_parser.add_argument(
        "--format",
        "-f",
        choices=["json", "csv", "yaml"],
        default="json",
        help=get_text("HISTORY", "format_help"),
    )
    export_parser.add_argument(
        "--type",
        "-t",
        choices=["interactions", "shell"],
        default="interactions",
        help=get_text("HISTORY", "type_help"),
    )

    # 历史清除子命令
    clear_parser = history_subparsers.add_parser(
        "clear", help=get_text("HISTORY", "clear_help")
    )
    clear_parser.add_argument(
        "--type",
        "-t",
        choices=["all", "interactions", "shell"],
        default="all",
        help=get_text("HISTORY", "clear_type_help"),
    )
    clear_parser.add_argument(
        "--force", "-f", action="store_true", help=get_text("HISTORY", "force_help")
    )

    # Shell历史子命令
    shell_parser = history_subparsers.add_parser(
        "shell", help=get_text("HISTORY", "shell_help")
    )
    shell_parser.add_argument(
        "--limit", "-n", type=int, default=10, help=get_text("HISTORY", "limit_help")
    )

    return parser


def parse_arguments() -> argparse.Namespace:
    """
    解析命令行参数，支持解析已知参数和值以及剩余位置参数
    Returns:
        解析后的参数命名空间，额外属性 prompt_args 为剩余位置参数
    """
    parser = get_parser()
    # 如果调用 history 子命令，使用 parse_args 来支持子命令解析
    import sys

    raw = sys.argv[1:]
    if raw and raw[0] == "history":
        return parser.parse_args()
    # 否则，解析已知参数并收集剩余位置参数为 prompt_args
    args, unknown = parser.parse_known_args()
    setattr(args, "prompt_args", unknown)
    return args


def process_input(args: argparse.Namespace) -> Tuple[str, bool]:
    """
    处理命令行输入，包括管道输入

    Args:
        args: 命令行参数命名空间

    Returns:
        (输入文本, 是否有输入)的元组
    """
    # 获取命令行提示词和管道上下文
    prompt = (
        " ".join(args.prompt_args)
        if hasattr(args, "prompt_args") and args.prompt_args
        else ""
    )
    pipe_content = sys.stdin.read().strip() if not sys.stdin.isatty() else ""

    # 构造最终输入，过滤空值
    user_input = "\n".join(filter(None, [prompt, pipe_content]))

    return user_input, bool(user_input)
