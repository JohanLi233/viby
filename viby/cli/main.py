#!/usr/bin/env python3
"""
viby CLI 入口点 - 处理命令行交互
"""

import os
import sys
import platform
import locale
import signal
from typing import Optional, Dict, Any
import importlib

from viby.cli.arguments import parse_arguments, process_input, get_parser
from viby.config.app_config import Config
from viby.utils.logging import setup_logging, get_logger
from viby.locale import init_text_manager, get_text

# 性能监控工具导入
from viby.utils.performance import (
    import_tracker,
    memory_tracker,
    enable_debugging,
    is_debugging_enabled,
)

# 创建日志记录器
logger = setup_logging(log_to_file=True)

# 命令类型缓存，避免重复导入同一命令
_command_class_cache: Dict[str, Any] = {}


def get_command_class(command_name: str) -> Any:
    """
    按需导入并获取命令类，减少启动时的导入开销

    Args:
        command_name: 命令名称，如 'shell', 'ask', 'chat'

    Returns:
        命令类
    """
    # 使用缓存避免重复导入
    if command_name in _command_class_cache:
        return _command_class_cache[command_name]

    # 动态导入命令模块
    module_name = f"viby.commands.{command_name.lower()}"
    class_name = f"{command_name.capitalize()}Command"

    try:
        module = importlib.import_module(module_name)
        command_class = getattr(module, class_name)
        # 缓存命令类
        _command_class_cache[command_name] = command_class
        return command_class
    except (ImportError, AttributeError) as e:
        logger.error(f"导入命令 {command_name} 失败: {e}")
        raise


def lazy_load_wizard() -> None:
    """懒加载配置向导模块"""
    try:
        from viby.config.wizard import run_config_wizard

        return run_config_wizard
    except ImportError as e:
        logger.error(f"导入配置向导模块失败: {e}")
        raise


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
    global logger

    # 检查是否启用性能调试
    if "--debug-performance" in sys.argv:
        enable_debugging()
        sys.argv.remove("--debug-performance")

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

        # 如果启用了性能调试，更新导入跟踪
        if is_debugging_enabled() and "--version" in sys.argv:
            import_tracker.print_report("Version命令导入报告")
            memory_tracker.print_report("Version命令内存报告")

        # 处理语言参数
        if args.language and args.language != config.language:
            config.language = args.language
            config.save_config()
            # 重新初始化文本管理器以应用新语言
            init_text_manager(config)

        # 首次运行或指定 --config 参数时启动交互式配置向导
        if config.is_first_run or args.config:
            # 懒加载配置向导
            run_config_wizard = lazy_load_wizard()
            run_config_wizard(config)
            # 配置向导后重新加载配置
            config = Config()  # 重新加载配置以确保更改生效
            init_text_manager(config)  # 如果语言等配置更改，重新初始化

        # 处理输入来源（组合命令行参数和管道输入）
        user_input, has_input = process_input(args)

        # 懒加载模型管理器
        if args.chat or has_input:
            # 只有在需要时才导入模型管理器
            from viby.llm.models import ModelManager

            model_manager = ModelManager(config, args)

            # 如果是聊天模式 (显式指定 --chat 或默认进入的交互模式)
            if args.chat:
                ChatCommand = get_command_class("chat")
                chat_command = ChatCommand(model_manager)

                # 如果启用性能调试，打印报告
                if is_debugging_enabled():
                    import_tracker.print_report("Chat命令初始化报告")
                    memory_tracker.print_report("Chat命令初始化内存报告")

                return chat_command.execute()

            # 如果有输入但不是聊天或shell模式，则认为是 ask 命令
            if has_input:
                AskCommand = get_command_class("ask")
                ask_command = AskCommand(model_manager)

                # 如果启用性能调试，打印报告
                if is_debugging_enabled():
                    import_tracker.print_report("Ask命令初始化报告")
                    memory_tracker.print_report("Ask命令初始化内存报告")

                return ask_command.execute(user_input)

        # 如果没有输入且没有指定其他模式，显示帮助
        # 或者以上条件都不满足（例如，只提供了无效的参数组合），显示帮助
        get_parser().print_help()

        # 如果启用性能调试，打印帮助性能报告
        if is_debugging_enabled():
            import_tracker.print_report("帮助命令报告")
            memory_tracker.print_report("帮助命令内存报告")

        return 0

    except KeyboardInterrupt:
        print(f"\n{get_text('GENERAL', 'operation_cancelled')}")
        return 130
    except EOFError:
        # 处理Ctrl+D（EOF），将其视为退出命令
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
    finally:
        # 程序退出前，如果启用了性能调试，打印最终报告
        if is_debugging_enabled():
            import_tracker.print_report("程序结束总报告")
            memory_tracker.print_report("程序结束内存报告")
            memory_tracker.stop()


if __name__ == "__main__":
    exit(main())
