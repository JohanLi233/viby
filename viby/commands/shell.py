"""
Shell command execution for viby
"""

import os
import subprocess
import pyperclip

from prompt_toolkit import prompt

from viby.llm.models import ModelManager
from viby.utils.formatting import Colors
from viby.utils.formatting import extract_answer
from viby.utils.formatting import response
from viby.locale import get_text
from viby.utils.formatting import print_separator


class ShellExecutor:
    """Handles shell command generation and execution"""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
    
    def generate_and_execute(self, user_prompt: str) -> int:
        """生成 shell 命令并支持流式输出，用户可选择执行"""
        # 强化提示，要求只返回 shell 命令
        shell_prompt = get_text("SHELL", "command_prompt", user_prompt)

        # 流式获取命令内容
        print(f"{Colors.BLUE}{get_text('SHELL', 'generating_command')}{Colors.END}")
        raw_response = response(self.model_manager, shell_prompt, return_raw=True)
        command = extract_answer(raw_response)

        # 清理 markdown 包裹
        if command.startswith('```') and command.endswith('```'):
            command = command[3:-3].strip()
        if command.startswith('`') and command.endswith('`'):
            command = command[1:-1].strip()
        
        print(f"{Colors.BLUE}{get_text('SHELL', 'execute_prompt', command)}{Colors.END}")

        choice = input(f"{Colors.YELLOW}{get_text('SHELL', 'choice_prompt')}").strip().lower()

        if choice in ('r', 'run'):
            return self._execute_command(command)
        elif choice == 'e':
            new_command = prompt(get_text('SHELL', 'edit_prompt', command), default=command)
            if new_command:
                command = new_command
            return self._execute_command(command)
        elif choice == 'y':
            try:
                pyperclip.copy(command)
                print(f"{Colors.GREEN}{get_text('GENERAL', 'copy_success')}{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}{get_text('GENERAL', 'copy_fail', str(e))}{Colors.END}")
            return 0
        else:
            print(f"{Colors.YELLOW}{get_text('GENERAL', 'operation_cancelled')}{Colors.END}")
            return 0
    
    def _execute_command(self, command: str) -> int:
        """执行 shell 命令并返回其退出代码"""
        try:
            # 使用用户的 shell 执行
            shell = os.environ.get('SHELL', '/bin/sh')
            
            print(f"{Colors.BOLD}{Colors.BLUE}{get_text('SHELL', 'executing', command)}{Colors.END}")
            print(f"{Colors.BLUE}", end="")
            print_separator()
            print(Colors.END, end="")
            
            process = subprocess.run(
                command,
                shell=True,
                executable=shell
            )
            
            # 根据返回码显示不同颜色
            status_color = Colors.GREEN if process.returncode == 0 else Colors.RED
            print(f"{Colors.BLUE}", end="")
            print_separator()
            print(Colors.END, end="")
            print(f"{status_color}{get_text('SHELL', 'command_complete', process.returncode)}{Colors.END}")
            
            return process.returncode
        except Exception as e:
            print(f"{Colors.RED}{get_text('SHELL', 'command_error', str(e))}{Colors.END}")
            return 1
