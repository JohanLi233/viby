#!/usr/bin/env python3
"""
viby CLI 入口点 - 处理命令行交互
"""

import os
import sys
import platform
import locale
import signal
from typing import Optional

from viby.cli.arguments import parse_arguments, process_input, get_parser
from viby.config.app_config import Config
from viby.config.wizard import run_config_wizard
from viby.llm.models import ModelManager
from viby.commands.shell import ShellCommand
from viby.commands.ask import AskCommand
from viby.commands.chat import ChatCommand
from viby.utils.logging import setup_logging, get_logger
from viby.locale import init_text_manager, get_text

# 创建日志记录器
logger = setup_logging(log_to_file=True)


def setup_platform_specific() -> None:
    """
    设置特定平台的配置和信号处理
    """
    system = platform.system()

    # 在Windows上处理控制台编码
    if system == "Windows":
        # 尝试设置控制台编码为UTF-8，以正确显示Unicode字符
        try:
            # Windows需要特殊处理以支持UTF-8和ANSI转义序列
            os.system("")  # 启用ANSI转义序列处理

            # 检查是否在IDLE或其他不支持ANSI的环境中运行
            if sys.stdout.isatty():
                import ctypes

                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except (ImportError, AttributeError):
            logger.warning("Windows控制台UTF-8支持配置失败")

    # 设置信号处理器
    # Windows不支持SIGPIPE
    if system != "Windows":
        # 忽略SIGPIPE，防止在管道关闭时程序崩溃
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def check_environment() -> Optional[str]:
    """
    检查运行环境
    返回任何发现的警告消息
    """
    warnings = []

    # 检查Python版本
    if sys.version_info < (3, 10):
        warnings.append(f"Python版本({sys.version.split()[0]})低于建议的3.10+版本")

    # 检查系统信息
    system = platform.system()
    if system == "Windows" and int(platform.version().split(".")[0]) < 10:
        warnings.append("Windows版本低于Windows 10，某些特性可能不可用")

    # 检查区域设置
    try:
        current_locale = locale.getlocale()[0]
        if not current_locale or current_locale.startswith("C"):
            warnings.append("系统使用默认区域设置，可能影响Unicode字符处理")
    except (AttributeError, ValueError):
        pass

    return "\n".join(warnings) if warnings else None


def main() -> int:
    """viby CLI 的主入口，返回退出码"""
    try:
        # 设置平台特定配置
        setup_platform_specific()

        # 检查环境并记录任何警告
        env_warnings = check_environment()
        if env_warnings:
            logger.warning(f"环境检查发现以下警告:\n{env_warnings}")

        # 提前创建 config 以获取默认值
        config = Config()

        # 初始化文本管理器，保证所有命令都能安全使用 get_text
        init_text_manager(config)

        # 解析命令行参数
        args = parse_arguments()

        # 首次运行或指定 --config 参数时启动交互式配置向导
        if config.is_first_run or args.config:
            run_config_wizard(config)
            # 配置向导后重新加载配置
            config = Config()  # 重新加载配置以确保更改生效
            init_text_manager(config)  # 如果语言等配置更改，重新初始化

        # 初始化模型管理器，传递 args 参数以支持 -t/--think 模式
        model_manager = ModelManager(config, args)

        # 处理输入来源（组合命令行参数和管道输入）
        user_input, has_input = process_input(args)

        # 优先处理特定模式，如 --shell
        if args.shell:
            if not has_input:
                get_parser().print_help()
                return 1
            shell_command = ShellCommand(model_manager, config)
            return shell_command.execute(user_input)

        # 如果是聊天模式 (显式指定 --chat 或默认进入的交互模式)
        # 或者没有管道输入，也不是其他特定命令（如--version, --help已被argparse处理）
        # 并且没有提供位置参数作为 ask 命令的输入
        if args.chat:
            chat_command = ChatCommand(model_manager, config)
            return chat_command.execute()
        # 如果没有输入且没有指定其他模式，显示帮助
        elif not has_input and not args.prompt:
            get_parser().print_help()
            return 0

        # 如果有输入但不是聊天或shell模式，则认为是 ask 命令
        if has_input:
            ask_command = AskCommand(model_manager, config)
            return ask_command.execute(user_input)

        # 如果以上条件都不满足（例如，只提供了无效的参数组合），显示帮助
        get_parser().print_help()
        return 1

    except KeyboardInterrupt:
        print(f"\n{get_text('GENERAL', 'operation_cancelled')}")
        return 130
    except Exception as e:
        logger = get_logger()
        logger.exception(f"Error: {e}")

        # 如果是开发环境，重新抛出异常以获取完整堆栈跟踪
        if os.environ.get("VIBY_DEBUG"):
            raise

        print(f"\n{str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
