"""
Command line argument parsing for viby
"""

import argparse
import sys
from typing import Tuple

from viby.locale import get_text


def get_parser() -> argparse.ArgumentParser:
    # 禁用默认的帮助选项，以便我们可以添加自定义的中文帮助选项
    parser = argparse.ArgumentParser(
        description=get_text("GENERAL", "app_description"),
        epilog=get_text("GENERAL", "app_epilog"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False  # 禁用默认的英文帮助选项
    )
    
    # 添加自定义的中文帮助选项
    parser.add_argument(
        "-h", "--help", action="help", default=argparse.SUPPRESS,
        help=get_text("GENERAL", "help_text")
    )
    parser.add_argument(
        "prompt", nargs="?", 
        help=get_text("GENERAL", "prompt_help")
    )
    parser.add_argument(
        "--chat", "-c", action="store_true",
        help=get_text("GENERAL", "chat_help")
    )
    parser.add_argument(
        "--shell", "-s", action="store_true",
        help=get_text("GENERAL", "shell_help")
    )
    parser.add_argument(
        "--config", action="store_true",
        help=get_text("GENERAL", "config_help")
    )
    parser.add_argument(
        "--think", "-t", action="store_true",
        help=get_text("GENERAL", "think_help")
    )
    parser.add_argument(
        "--fast", "-f", action="store_true",
        help=get_text("GENERAL", "fast_help")
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
    prompt = args.prompt.strip() if args.prompt else ''
    pipe_content = sys.stdin.read().strip() if not sys.stdin.isatty() else ''

    # 构造最终输入，过滤空值
    user_input = '\n'.join(filter(None, [prompt, pipe_content]))

    return user_input, bool(user_input)
