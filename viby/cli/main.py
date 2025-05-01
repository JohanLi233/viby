#!/usr/bin/env python3
"""
viby CLI 入口点 - 处理命令行交互
"""


from viby.cli.arguments import parse_arguments, process_input, get_parser
from viby.config import Config
from viby.llm.models import ModelManager
from viby.commands.shell import ShellExecutor
from viby.utils.logging import setup_logging
from viby.utils.formatting import response


# Setup logging early
logger = setup_logging()


def main():
    """viby CLI 的主入口"""
    try:
        # 提前创建 config 以获取默认值
        config = Config()
        
        # 解析命令行参数
        args = parse_arguments()
        
        # 初始化模型管理器
        model_manager = ModelManager(config)
        
        # 处理输入来源（组合命令行参数和管道输入）
        user_input, has_input = process_input(args)
        
        if not has_input:
            get_parser().print_help()
            return 1
            
        if args.shell:
            # shell 命令生成与执行模式
            shell_executor = ShellExecutor(model_manager)
            return shell_executor.generate_and_execute(user_input)
        else:
            return response(model_manager, user_input, return_raw=False)
            
    except KeyboardInterrupt:
        print("\n用户取消操作")
        return 130
    except Exception as e:
        logger.error(f"错误: {str(e)}")
        return 1
