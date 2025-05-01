"""
Shell command execution for viby
"""

import os
import subprocess
import shutil
import pyperclip

from prompt_toolkit import prompt

from viby.llm.models import ModelManager
from viby.utils.formatting import Colors
from viby.utils.formatting import extract_answer
from viby.utils.formatting import response


class ShellExecutor:
    """Handles shell command generation and execution"""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
    
    def generate_and_execute(self, user_prompt: str) -> int:
        """生成 shell 命令并支持流式输出，用户可选择执行"""
        # 强化提示，要求只返回 shell 命令
        shell_prompt = f"请只生成一个用于：{user_prompt} 的 shell 命令。只返回命令本身，不要解释，不要 markdown。"

        # 流式获取命令内容
        print(f"{Colors.BLUE}[AI 正在生成命令...]{Colors.END}")
        raw_response = response(self.model_manager, shell_prompt, return_raw=True)
        command = extract_answer(raw_response)

        # 清理 markdown 包裹
        if command.startswith('```') and command.endswith('```'):
            command = command[3:-3].strip()
        if command.startswith('`') and command.endswith('`'):
            command = command[1:-1].strip()
        
        print(f"{Colors.BLUE}执行命令│  {Colors.GREEN}{command}{Colors.BLUE}  │?")

        choice = input(f"{Colors.YELLOW}[r]运行, [e]编辑, [y]复制, [q]放弃 (默认: 放弃): ").strip().lower()

        if choice in ('r', 'run'):
            return self._execute_command(command)
        elif choice == 'e':
            new_command = prompt(f"编辑命令（原命令: {command}）:\n> ", default=command)
            if new_command:
                command = new_command
            return self._execute_command(command)
        elif choice == 'y':
            try:
                pyperclip.copy(command)
                print(f"{Colors.GREEN}命令已复制到剪贴板！{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}复制失败: {e}{Colors.END}")
            return 0
        else:
            print(f"{Colors.YELLOW}操作已取消。{Colors.END}")
            return 0
    
    def _execute_command(self, command: str) -> int:
        """执行 shell 命令并返回其退出代码"""
        try:
            # 使用用户的 shell 执行
            shell = os.environ.get('SHELL', '/bin/sh')
            
            # 获取终端宽度，用于分隔线
            terminal_width = shutil.get_terminal_size().columns
            separator = "─" * terminal_width
            
            print(f"\n{Colors.BOLD}{Colors.BLUE}执行命令:{Colors.END} {Colors.YELLOW}{command}{Colors.END}")
            print(f"{Colors.BLUE}{separator}{Colors.END}")
            
            process = subprocess.run(
                command,
                shell=True,
                executable=shell
            )
            
            # 根据返回码显示不同颜色
            status_color = Colors.GREEN if process.returncode == 0 else Colors.RED
            print(f"{Colors.BLUE}{separator}{Colors.END}")
            print(f"{status_color}命令完成 [返回码: {process.returncode}]{Colors.END}\n")
            
            return process.returncode
        except Exception as e:
            print(f"{Colors.RED}命令执行出错: {str(e)}{Colors.END}")
            return 1
