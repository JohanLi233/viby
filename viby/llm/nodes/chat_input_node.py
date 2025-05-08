import os
import platform
from pathlib import Path
from pocketflow import Node
from prompt_toolkit import prompt, print_formatted_text
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.styles import Style
from viby.locale import get_text


class ChatInputNode(Node):
    """获取用户输入并将其添加到消息历史中"""

    def __init__(self):
        super().__init__()
        # 根据不同操作系统选择合适的历史文件位置
        self.history_path: Path = self._get_history_path()
        # 确保目录存在
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.history = FileHistory(str(self.history_path))
        self.command_completer = WordCompleter(
            [
                "/exit",
                "/help",
                "/history_view",
                "/history_clear",
                "/status",
                "/version",
            ],
            ignore_case=True,
        )
        self._internal_commands_output = None
        # 自定义样式
        self.style = Style.from_dict(
            {
                "input-prompt": "ansicyan bold",
                "command": "ansigreen",
                "help-title": "ansimagenta bold",
                "help-command": "ansigreen",
                "help-desc": "ansicyan",
                "history-title": "ansimagenta bold",
                "history-item": "ansiwhite",
                "history-current": "ansiyellow bold",
                "warning": "ansiyellow",
                "error": "ansired bold",
            }
        )
        # 设置键绑定
        self.key_bindings = self._create_key_bindings()

    @staticmethod
    def _get_history_path() -> Path:
        """根据操作系统返回历史文件存储路径"""
        system = platform.system()
        if system == "Windows":
            base_dir = Path(os.environ.get("APPDATA", str(Path.home())))
        elif system == "Darwin":
            base_dir = Path.home() / ".config"
        else:
            # Linux 及其他类 Unix 系统
            base_dir = Path.home() / ".config"

        viby_dir = base_dir / "viby"
        return viby_dir / "history"

    def _create_key_bindings(self):
        """创建自定义键绑定"""
        bindings = KeyBindings()

        @bindings.add("c-t")
        def _(event):
            """Ctrl+T 显示当前时间和状态"""

            def print_time():
                from datetime import datetime

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print_formatted_text(
                    HTML(f'<span class="ansicyan">当前时间: {now}</span>')
                )

            run_in_terminal(print_time)

        @bindings.add("f1")
        def _(event):
            """F1 显示帮助"""
            # 将光标内容设置为 /help 并执行
            event.app.current_buffer.text = "/help"
            event.app.current_buffer.validate_and_handle()

        return bindings

    def _print_internal_command_output(self):
        """如果存在内部命令的输出，则打印它并清除。"""
        if self._internal_commands_output:
            print_formatted_text(HTML(self._internal_commands_output))
            self._internal_commands_output = None

    def _show_help(self):
        """显示帮助信息"""
        self._internal_commands_output = (
            f'<span class="help-title">{get_text("CHAT", "help_title", "可用内部命令:")}</span>\n'
            f'  <span class="help-command">/exit, /quit</span> - <span class="help-desc">{get_text("CHAT", "help_exit", "退出Viby")}</span>\n'
            f'  <span class="help-command">/help</span>      - <span class="help-desc">{get_text("CHAT", "help_help", "显示此帮助信息")}</span>\n'
            f'  <span class="help-command">/history_view</span> - <span class="help-desc">{get_text("CHAT", "help_history", "显示最近命令历史")}</span>\n'
            f'  <span class="help-command">/history_clear</span> - <span class="help-desc">{get_text("CHAT", "help_history_clear", "清除命令历史")}</span>\n'
            f'  <span class="help-command">/status</span>    - <span class="help-desc">{get_text("CHAT", "help_status", "显示当前状态信息")}</span>\n'
            f'  <span class="help-command">/version</span>   - <span class="help-desc">{get_text("GENERAL", "version_help", "显示程序版本信息")}</span>\n\n'
            f'<span class="help-desc">{get_text("CHAT", "help_shortcuts", "快捷键:")}</span>\n'
            f'  <span class="help-desc">Ctrl+T: 显示当前时间</span>\n'
            f'  <span class="help-desc">F1: 显示此帮助信息</span>\n'
            f'  <span class="help-desc">Ctrl+C: 退出程序</span>'
        )

    def _show_history(self, limit=20):
        """显示命令历史"""
        history_items = list(self.history.load_history_strings())
        if history_items:
            # 显示最近的指定条数，或者全部如果少于限制数量
            display_items = history_items[-limit:]
            history_text = "\n".join(
                [
                    f'  <span class="history-item">{i + 1}. {item}</span>'
                    for i, item in enumerate(display_items)
                ]
            )
            self._internal_commands_output = (
                f'<span class="history-title">{get_text("CHAT", "history_title", "最近命令历史:")}\n'
                f"{history_text}</span>"
            )
        else:
            self._internal_commands_output = f'<span class="warning">{get_text("CHAT", "history_empty", "还没有命令历史。")}</span>'

    def _clear_history(self):
        """清除命令历史"""
        try:
            if self.history_path.exists():
                # 创建备份
                backup_path = f"{self.history_path}.bak"
                import shutil

                shutil.copy2(self.history_path, backup_path)

                # 清空历史文件
                # 覆盖为空
                self.history_path.write_text("")
                self._internal_commands_output = f'<span class="command">{get_text("CHAT", "history_cleared", "命令历史已清除。已创建备份：")} {backup_path}</span>'
            else:
                self._internal_commands_output = f'<span class="warning">{get_text("CHAT", "history_not_found", "没有找到历史文件。")}</span>'
        except Exception as e:
            self._internal_commands_output = f'<span class="error">{get_text("CHAT", "history_clear_error", "清除历史时出错:")} {str(e)}</span>'

    def _show_status(self):
        """显示当前状态信息"""
        from datetime import datetime
        import platform

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        status_text = (
            f'<span class="help-title">{get_text("CHAT", "status_title", "系统状态:")}</span>\n'
            f'  <span class="help-command">时间:</span> <span class="help-desc">{now}</span>\n'
            f'  <span class="help-command">系统:</span> <span class="help-desc">{platform.system()} {platform.release()}</span>\n'
            f'  <span class="help-command">Python:</span> <span class="help-desc">{platform.python_version()}</span>\n'
            f'  <span class="help-command">历史条目:</span> <span class="help-desc">{len(list(self.history.load_history_strings()))}</span>\n'
        )
        self._internal_commands_output = status_text

    def exec(self, prep_res):
        # 在每次提示前，先打印之前内部命令可能产生的输出
        self._print_internal_command_output()

        # 获取用户输入
        input_prompt_text = get_text("CHAT", "input_prompt")
        # 确保我们总是从共享状态或配置中获取最新的提示符样式（如果适用）
        # 这里简化为直接使用HTML格式化
        input_prompt_formatted = HTML(
            f'<span class="input-prompt">{input_prompt_text}</span>'
        )

        while True:  # 添加循环以处理内部命令并重新提示
            user_input = prompt(
                input_prompt_formatted,
                history=self.history,
                completer=self.command_completer,
                key_bindings=self.key_bindings,
                style=self.style,
            )

            # 检查是否是退出命令
            if user_input.lower() in ["/exit", "/quit"]:
                return "exit"
            elif user_input.lower() == "/help":
                self._show_help()
                self._print_internal_command_output()  # 立即打印帮助信息
                continue  # 重新提示输入
            elif user_input.lower() == "/history_view":
                self._show_history()
                self._print_internal_command_output()  # 立即打印历史
                continue  # 重新提示输入
            elif user_input.lower() == "/history_clear":
                self._clear_history()
                self._print_internal_command_output()
                continue  # 重新提示输入
            elif user_input.lower() == "/status":
                self._show_status()
                self._print_internal_command_output()
                continue
            elif user_input.lower() == "/version":
                # 处理版本信息显示
                try:
                    from importlib.metadata import version

                    viby_version = version("viby")
                    version_text = (
                        f'<span class="help-title">Viby 版本信息:</span>\n'
                        f'  <span class="help-desc">版本: {viby_version}</span>'
                    )
                except ImportError:
                    # 如果无法通过metadata获取，提供一个备用方式
                    version_text = (
                        '<span class="help-title">Viby 版本信息:</span>\n'
                        '  <span class="help-desc">版本: 无法获取版本信息</span>'
                    )
                self._internal_commands_output = version_text
                self._print_internal_command_output()
                continue

            if not user_input.strip():  # 如果用户只输入了空格或回车，则重新提示
                continue

            return user_input  # 返回有效的用户输入

    def post(self, shared, prep_res, exec_res):
        # 检查是否退出
        if exec_res == "exit":
            return "exit"

        # 添加用户消息到历史
        # 如果还没有消息历史，初始化它
        if "messages" not in shared:
            shared["messages"] = []

        # 将用户输入存到 shared 中，便于 PromptNode 使用
        shared["user_input"] = exec_res

        # 添加用户消息到历史
        shared["messages"].append({"role": "user", "content": exec_res})

        # 如果消息历史只有一条（当前消息），说明是第一次输入
        if len(shared["messages"]) == 1:
            return "first_input"  # 路由到 PromptNode 获取工具
        else:
            return "call_llm"  # 直接到 LLM 节点
