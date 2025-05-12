"""
Shell命令执行工具定义
"""

import os
import subprocess
import platform
import pyperclip
import re
import logging
from typing import Dict, Any
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML

from viby.locale import get_text
from viby.utils.formatting import Colors, print_separator
from viby.utils.history import HistoryManager
from viby.config.app_config import Config

logger = logging.getLogger(__name__)

# 获取全局配置实例
_config = Config()
# 初始化历史管理器
_history_manager = HistoryManager()

# 不安全命令黑名单
UNSAFE_COMMANDS = [
    "rm",
    "rm -rf",
    "rm -r",
    "rm -f",
    "rmdir",
    "mkfs",
    "dd",
    ":(){ :|:& };:",
    "chmod -R 777",
    "> /dev/sda",
    "mv /* /dev/null",
    "wget",
    "curl",
    "sudo rm",
    "> /etc/passwd",
    "shutdown",
    "reboot",
    "halt",
    "poweroff",
    "find / -delete",
    ":(){ :|:& };:",
    "eval",
    "sudo",
    "chown",
    "> /dev/null",
    "shred",
]

# 高危命令模式，使用正则表达式
UNSAFE_PATTERNS = [
    r"^rm\s+(-[a-zA-Z]*[fr][a-zA-Z]*\s+|--recursive\s+|--force\s+)",  # rm命令带有-f或-r参数
    r"^sudo\s+",  # 以sudo开头的命令
    r">\s*/dev/",  # 重定向到设备文件
    r">\s*/etc/",  # 重定向到系统配置文件
    r"mv\s+/\S+\s+/dev/null",  # 移动文件到/dev/null
]

# Shell工具定义 - 符合FastMCP标准
SHELL_TOOL = {
    "name": "execute_shell",
    "description": lambda: get_text("MCP", "shell_tool_description"),
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": lambda: get_text("MCP", "shell_tool_param_command"),
            }
        },
        "required": ["command"],
    },
}


def execute_shell(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行shell命令工具处理函数

    Args:
        params: 包含command参数的字典

    Returns:
        执行结果
    """
    command = params.get("command", "")
    if not command:
        return {"success": False, "error": "命令不能为空"}

    try:
        # 调用shell处理器执行命令
        result = handle_shell_command(command)

        # 转换结果为MCP工具格式
        return {
            "success": result.get("status") == "executed",
            "code": result.get("code", 1),
            "output": result.get("output", ""),
            "error": result.get("error", ""),
            "command": command,
        }
    except Exception as e:
        logger.error(f"执行shell命令失败: {e}", exc_info=True)
        return {"success": False, "error": f"执行失败: {str(e)}"}


def set_yolo_mode(enabled: bool) -> bool:
    """
    开启或关闭yolo模式

    Args:
        enabled: 是否开启yolo模式

    Returns:
        当前yolo模式状态
    """
    global _config
    _config.enable_yolo_mode = enabled
    _config.save_config()
    return _config.enable_yolo_mode


def is_yolo_mode_enabled() -> bool:
    """
    获取当前yolo模式状态

    Returns:
        当前yolo模式是否开启
    """
    global _config
    return _config.enable_yolo_mode


def _is_unsafe_command(command: str) -> bool:
    """
    检查命令是否不安全

    Args:
        command: 要检查的命令

    Returns:
        如果命令可能不安全则返回True
    """
    # 分割命令，获取主命令
    cmd_parts = command.strip().split()
    if not cmd_parts:
        return False

    main_cmd = cmd_parts[0]

    # 安全命令白名单检查
    safe_commands = ["ls", "echo", "cat", "grep", "pwd", "cd", "mkdir", "touch"]
    if main_cmd in safe_commands:
        return False

    # 检查命令是否匹配危险模式
    if any(re.search(pattern, command) for pattern in UNSAFE_PATTERNS):
        return True

    # 检查命令是否包含黑名单中的字符串
    # 只检查主命令和选项，避免误判文件名或echo内容
    command_prefix = " ".join(cmd_parts[:2] if len(cmd_parts) > 1 else cmd_parts)
    if any(unsafe_cmd in command_prefix for unsafe_cmd in UNSAFE_COMMANDS):
        return True

    return False


def handle_shell_command(command: str):
    """
    处理并执行shell命令

    Args:
        command: 要执行的shell命令

    Returns:
        命令执行结果
    """
    # 检查命令是否安全
    is_unsafe = _is_unsafe_command(command)

    # 检查是否启用yolo模式并且命令是安全的
    if is_yolo_mode_enabled() and not is_unsafe:
        print(
            f"{Colors.BLUE}{get_text('SHELL', 'executing_yolo', command)}{Colors.END}"
        )
        result = _execute_command(command)
        # 记录shell命令及其结果到历史记录
        _history_manager.add_shell_command(
            command,
            os.getcwd(),  # 当前工作目录作为directory参数
            result.get("code", 1),
            {
                "output": result.get("output", ""),
                "error": result.get("error", ""),
            },  # 将输出作为元数据
        )
        return result

    # 不是yolo模式或命令不安全，使用交互模式
    print(f"{Colors.BLUE}{get_text('SHELL', 'execute_prompt', command)}{Colors.END}")

    # 如果命令不安全且yolo模式开启，显示警告
    if is_yolo_mode_enabled() and is_unsafe:
        print(f"{Colors.RED}{get_text('SHELL', 'unsafe_command_warning')}{Colors.END}")

    choice_prompt_html = HTML(
        f'<span class="ansiyellow">{get_text("SHELL", "choice_prompt")}</span>'
    )
    choice = prompt(choice_prompt_html).strip().lower()

    # 根据用户选择执行不同操作
    result = _handle_choice(choice, command)

    # 只有在实际执行了命令时才记录历史
    if result.get("status") == "executed":
        _history_manager.add_shell_command(
            command,
            os.getcwd(),  # 当前工作目录作为directory参数
            result.get("code", 1),
            {
                "output": result.get("output", ""),
                "error": result.get("error", ""),
            },  # 将输出作为元数据
        )

    return result


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
