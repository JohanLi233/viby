"""
Shell命令执行处理器
"""

import os
import subprocess
import platform
import pyperclip
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from viby.utils.formatting import Colors, print_separator
from viby.locale import get_text


def handle_shell_command(command: str):
    """
    处理并执行shell命令

    Args:
        command: 要执行的shell命令

    Returns:
        命令执行结果
    """
    # 交互模式，显示命令并等待用户确认
    print(f"{Colors.BLUE}{get_text('SHELL', 'execute_prompt', command)}{Colors.END}")
    choice_prompt_html = HTML(
        f'<span class="ansiyellow">{get_text("SHELL", "choice_prompt")}</span>'
    )
    choice = prompt(choice_prompt_html).strip().lower()

    # 根据用户选择执行不同操作
    return _handle_choice(choice, command)


def _execute_command(command: str) -> dict:
    """执行shell命令并返回结果"""
    try:
        # 根据操作系统决定shell执行方式
        system = platform.system()
        if system == "Windows":
            # Windows下不指定executable，让shell=True自动使用cmd.exe
            shell_exec = None
        else:
            # Linux/macOS使用用户的shell或默认/bin/sh
            shell_exec = os.environ.get("SHELL", "/bin/sh")

        print(
            f"{Colors.BOLD}{Colors.BRIGHT_CYAN}{get_text('SHELL', 'executing', command)}{Colors.END}"
        )
        print(f"{Colors.BLUE}", end="")
        print_separator()
        print(Colors.END, end="")

        # 根据操作系统决定是否传递executable参数
        if shell_exec:
            process = subprocess.run(
                command,
                shell=True,
                executable=shell_exec,
                capture_output=True,
                text=True,
            )
        else:
            process = subprocess.run(
                command, shell=True, capture_output=True, text=True
            )

        # 输出命令结果
        if process.stdout:
            print(process.stdout)
        if process.stderr:
            print(f"{Colors.RED}{process.stderr}{Colors.END}")

        # 根据返回码显示不同颜色
        status_color = Colors.GREEN if process.returncode == 0 else Colors.RED
        print(f"{Colors.BLUE}", end="")
        print_separator()
        print(Colors.END, end="")
        print(
            f"{status_color}{get_text('SHELL', 'command_complete', process.returncode)}{Colors.END}"
        )

        return {
            "status": "executed",
            "code": process.returncode,
            "output": process.stdout,
            "error": process.stderr,
        }
    except Exception as e:
        print(f"{Colors.RED}{get_text('SHELL', 'command_error', str(e))}{Colors.END}")
        return {"status": "error", "code": 1, "message": str(e)}


def _handle_choice(choice: str, command: str) -> dict:
    """根据用户输入分发处理器"""
    handlers = {
        "e": _edit_and_execute,
        "y": _copy_to_clipboard,
        "q": _cancel_operation,
        "": _execute_command,  # 默认操作
        "r": _execute_command,
    }

    handler = handlers.get(choice, _execute_command)
    return handler(command)


def _edit_and_execute(command: str) -> dict:
    """编辑并执行命令"""
    new_cmd = prompt(get_text("SHELL", "edit_prompt", command), default=command)
    return _execute_command(new_cmd or command)


def _copy_to_clipboard(command: str) -> dict:
    """复制命令到剪贴板"""
    try:
        pyperclip.copy(command)
        print(f"{Colors.GREEN}{get_text('GENERAL', 'copy_success')}{Colors.END}")
        return {"status": "completed", "code": 0}
    except Exception as e:
        print(f"{Colors.RED}{get_text('GENERAL', 'copy_fail', str(e))}{Colors.END}")
        return {"status": "completed", "code": 1, "message": str(e)}


def _cancel_operation(command: str) -> dict:
    """取消操作"""
    print(f"{Colors.YELLOW}{get_text('GENERAL', 'operation_cancelled')}{Colors.END}")
    return {"status": "completed", "code": 0}
