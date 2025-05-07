import os
import subprocess
import platform
import pyperclip
from pocketflow import Node
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from viby.utils.formatting import Colors, print_separator, extract_answer
from viby.locale import get_text


class ExecuteShellCommandNode(Node):
    """
    执行 Shell 命令的节点
    
    负责：
    1. 显示生成的 shell 命令
    2. 提供用户交互选项（运行、编辑、复制、放弃）
    3. 执行命令并显示结果
    """
    def prep(self, shared):
        # 从共享状态获取生成的message
        return shared.get("messages")[-1].get("content")
    
    def exec(self, prep_res):
        """纯计算步骤：直接返回命令字符串，不做任何 I/O 或共享状态访问"""
        command = extract_answer(prep_res)
        return command
    
    def post(self, shared, prep_res, exec_res):
        """根据用户交互执行命令或其他操作，并写回 shared"""
        # 若 exec_res 为空，则无有效命令，直接退出
        if not exec_res:
            shared["shell_result"] = {"status": "cancelled", "code": 0}
            return None

        command = exec_res

        # 显示命令并获取用户选择
        print(f"{Colors.BLUE}{get_text('SHELL', 'execute_prompt', command)}{Colors.END}")
        choice_prompt_html = HTML(f'<ansiyellow>{get_text("SHELL", "choice_prompt")}</ansiyellow>')
        choice = prompt(choice_prompt_html).strip().lower()

        # 根据用户选择执行操作
        exec_res_dict = self._handle_choice(choice, command)

        # 保存结果到 shared
        shared["shell_result"] = exec_res_dict

        # 如果用户选择继续对话，则追加改进提示并返回动作
        if exec_res_dict.get("status") == "call_llm":
            improve_prompt = get_text('SHELL', 'improve_command_prompt', command, exec_res_dict.get('user_feedback', ''))
            # 初始化 messages 如果不存在
            if "messages" not in shared:
                shared["messages"] = []
            shared["messages"].append({"role": "user", "content": improve_prompt})
            return "call_llm"

        return None

    def _execute_command(self, command: str) -> dict:
        """执行 shell 命令并返回结果"""
        try:
            # 根据操作系统决定 shell 执行方式
            system = platform.system()
            if system == "Windows":
                # Windows 下不指定 executable，让 shell=True 自动使用 cmd.exe
                shell_exec = None
            else:
                # Linux/macOS 使用用户的 shell 或默认 /bin/sh
                shell_exec = os.environ.get('SHELL', '/bin/sh')
            
            print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}{get_text('SHELL', 'executing', command)}{Colors.END}")
            print(f"{Colors.BLUE}", end="")
            print_separator()
            print(Colors.END, end="")
            
            # 根据操作系统决定是否传递 executable 参数
            if shell_exec:
                process = subprocess.run(
                    command,
                    shell=True,
                    executable=shell_exec
                )
            else:
                process = subprocess.run(
                    command,
                    shell=True
                )
            
            # 根据返回码显示不同颜色
            status_color = Colors.GREEN if process.returncode == 0 else Colors.RED
            print(f"{Colors.BLUE}", end="")
            print_separator()
            print(Colors.END, end="")
            print(f"{status_color}{get_text('SHELL', 'command_complete', process.returncode)}{Colors.END}")
            
            return {"status": "executed", "code": process.returncode}
        except Exception:
            # 让 exec_fallback 统一处理异常
            raise

    def exec_fallback(self, prep_res, exc):
        """命令执行异常时回退处理"""
        print(f"{Colors.RED}{get_text('SHELL', 'command_error', str(exc))}{Colors.END}")
        return {"status": "error", "code": 1}

    def _handle_choice(self, choice: str, command: str) -> dict:
        """根据用户输入分发处理器"""
        return {
            'e': self._edit_and_execute,
            'y': self._copy_to_clipboard,
            'q': self._cancel_operation,
            'c': self._continue_chat
        }.get(choice, self._execute_command)(command)

    def _edit_and_execute(self, command: str) -> dict:
        """编辑并执行命令"""
        new_cmd = prompt(get_text('SHELL', 'edit_prompt', command), default=command)
        return self._execute_command(new_cmd or command)

    def _copy_to_clipboard(self, command: str) -> dict:
        """复制命令到剪贴板"""
        try:
            pyperclip.copy(command)
            print(f"{Colors.GREEN}{get_text('GENERAL', 'copy_success')}{Colors.END}")
            return {"status": "copied", "code": 0}
        except Exception as e:
            print(f"{Colors.RED}{get_text('GENERAL', 'copy_fail', str(e))}{Colors.END}")
            return {"status": "copy_failed", "code": 1}

    def _cancel_operation(self, command: str) -> dict:
        """取消操作"""
        print(f"{Colors.YELLOW}{get_text('GENERAL', 'operation_cancelled')}{Colors.END}")
        return {"status": "cancelled", "code": 0}

    def _continue_chat(self, command: str) -> dict:
        """继续对话"""
        print(f"{Colors.GREEN}{get_text('SHELL', 'continue_chat')}{Colors.END}")
        feedback = prompt(HTML('<ansicyan>|> </ansicyan>'))
        return {"status": "call_llm", "command": command, "user_feedback": feedback, "code": 0}
