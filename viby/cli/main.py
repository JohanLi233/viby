#!/usr/bin/env python3
"""
viby CLI 入口点 - 处理命令行交互
"""


from viby.cli.arguments import parse_arguments, process_input, get_parser
from viby.config.app_config import Config
from viby.config.wizard import run_config_wizard
from viby.llm.models import ModelManager
from viby.commands.shell import ShellCommand
from viby.commands.ask import AskCommand
from viby.commands.chat import ChatCommand
from viby.utils.logging import setup_logging
from viby.locale import init_text_manager, get_text

logger = setup_logging()

def main():
    """viby CLI 的主入口"""
    try:
        # 提前创建 config 以获取默认值
        config = Config()
        # 初始化文本管理器，保证所有命令都能安全使用 get_text

        init_text_manager(config)
        
        # 解析命令行参数
        args = parse_arguments()
        
        # 首次运行或指定 --config 参数时启动交互式配置向导
        if config.is_first_run or args.config:
            run_config_wizard(config)
        
        # 初始化模型管理器，传递 args 参数以支持 -t/--think 模式
        model_manager = ModelManager(config, args)
        
        # 处理输入来源（组合命令行参数和管道输入）
        user_input, has_input = process_input(args)
        
        # 如果是聊天模式，即使没有提示内容也可以继续
        if args.chat:
            chat_command = ChatCommand(model_manager)
            return chat_command.execute()
        
        if not has_input:
            get_parser().print_help()
            return 1
            
        if args.shell:
            # shell 命令生成与执行模式
            shell_command = ShellCommand(model_manager)
            return shell_command.execute(user_input)
        else:
            ask_command = AskCommand(model_manager)
            return ask_command.execute(user_input)
            
    except KeyboardInterrupt:
        print(f"\n{get_text('GENERAL', 'operation_cancelled')}")
        return 130
    except Exception as e:
        logger.error(f"{str(e)}")
        return 1
