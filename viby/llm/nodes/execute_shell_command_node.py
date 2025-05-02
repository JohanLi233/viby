import os
import subprocess
import pyperclip
from pocketflow import Node
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from viby.utils.formatting import Colors, print_separator
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
        # 从共享状态获取生成的命令
        return {
            "command": shared.get("command")
        }
    
    def exec(self, prep_res):
        if not prep_res or not prep_res.get("command"):
            return {"status": "cancelled", "code": 0}
            
        command = prep_res["command"]
        
        # 显示命令并获取用户选择
        print(f"{Colors.BLUE}{get_text('SHELL', 'execute_prompt', command)}{Colors.END}")
        # 使用prompt_toolkit的HTML标记来添加颜色
        choice_prompt_html = HTML(f'<ansiyellow>{get_text("SHELL", "choice_prompt")}</ansiyellow>')
        choice = prompt(choice_prompt_html).strip().lower()
        
        # 根据用户选择执行不同操作
        if choice == 'e':
            new_command = prompt(get_text('SHELL', 'edit_prompt', command), default=command)
            if new_command:
                command = new_command
            return self._execute_command(command)
        elif choice == 'y':
            try:
                pyperclip.copy(command)
                print(f"{Colors.GREEN}{get_text('GENERAL', 'copy_success')}{Colors.END}")
                return {"status": "copied", "code": 0}
            except Exception as e:
                print(f"{Colors.RED}{get_text('GENERAL', 'copy_fail', str(e))}{Colors.END}")
                return {"status": "copy_failed", "code": 1}
        elif choice == 'q':
            print(f"{Colors.YELLOW}{get_text('GENERAL', 'operation_cancelled')}{Colors.END}")
            return {"status": "cancelled", "code": 0}
        elif choice == 'c':
            print(f"{Colors.GREEN}{get_text('SHELL', 'continue_chat')}{Colors.END}")
            # 获取用户对命令的反馈或问题
            feedback_prompt = HTML('<ansicyan>|> </ansicyan>')
            user_feedback = prompt(feedback_prompt)
            return {"status": "chat", "command": command, "user_feedback": user_feedback, "code": 0}
        else:
            # 默认行为：执行命令（包括 'r'/'run' 选项或直接回车）
            return self._execute_command(command)
    
    def _execute_command(self, command: str) -> dict:
        """执行 shell 命令并返回结果"""
        try:
            # 使用用户的 shell 执行
            shell = os.environ.get('SHELL', '/bin/sh')
            
            print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}{get_text('SHELL', 'executing', command)}{Colors.END}")
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
            
            return {"status": "executed", "code": process.returncode}
        except Exception as e:
            print(f"{Colors.RED}{get_text('SHELL', 'command_error', str(e))}{Colors.END}")
            return {"status": "error", "code": 1}
    
    def post(self, shared, prep_res, exec_res):
        # 将执行结果保存到共享状态
        if exec_res:
            shared["shell_result"] = exec_res
            
            # 如果用户选择继续对话，返回chat动作
            if exec_res.get("status") == "chat":
                # 更新用户输入，这样命令节点可以看到最新的对话内容
                command = exec_res.get('command', '')
                feedback = exec_res.get('user_feedback', '')
                shared["user_input"] = get_text('SHELL', 'improve_command_prompt', command, feedback)
                
                return "chat"
