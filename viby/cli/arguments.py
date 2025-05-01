"""
Command line argument parsing for viby
"""

import argparse
import sys
from typing import Tuple


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="yb - 一个与大模型交互的多功能命令行工具",
        epilog="示例:\n"
               "  yb \"什么是斐波那契数列?\"\n"
               "  git diff | yb \"帮我写一个commit消息\"\n"
               "  yb --shell \"找当前目录下所有json文件\"\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "prompt", nargs="?", 
        help="要发送给模型的提示内容"
    )
    parser.add_argument(
        "--shell", "-s", action="store_true",
        help="生成并可选执行 shell 命令"
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
    prompt = args.prompt.strip() if args.prompt else None
    pipe_content = sys.stdin.read().strip() if not sys.stdin.isatty() else None

    # 构造最终输入
    user_input = (
        f"{prompt}\n{pipe_content}" if prompt and pipe_content
        else prompt or pipe_content
    )
    
    return user_input, bool(user_input)
