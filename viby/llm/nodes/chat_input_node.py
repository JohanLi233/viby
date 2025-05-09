import os
import platform
from datetime import datetime
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

    COMMANDS = {
        "/exit": "exit",
        "/quit": "exit",
        "/help": "help",
        "/history_view": "history_view",
        "/history_clear": "history_clear",
        "/status": "status",
        "/version": "version",
    }

    def __init__(self):
        super().__init__()
        # 设置历史文件和目录
        self.history_path = self._get_history_path()
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.history = FileHistory(str(self.history_path))

        # 命令自动完成和输出缓存
        self.command_completer = WordCompleter(
            list(self.COMMANDS.keys()), ignore_case=True
        )
        self._internal_commands_output = None

        # 样式和键绑定
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
        self.key_bindings = self._create_key_bindings()

    @staticmethod
    def _get_history_path() -> Path:
        """根据操作系统返回历史文件存储路径"""
        # Windows 使用 APPDATA，其他系统使用 ~/.config
        base_dir = (
            Path(os.environ.get("APPDATA", str(Path.home())))
            if platform.system() == "Windows"
            else Path.home() / ".config"
        )
        return base_dir / "viby" / "history"

    def _create_key_bindings(self):
        """创建自定义键绑定"""
        bindings = KeyBindings()

        @bindings.add("c-t")
        def _(event):
            """Ctrl+T 显示当前时间和状态"""
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            run_in_terminal(
                lambda: print_formatted_text(
                    HTML(
                        f'<span class="ansicyan">{get_text("CHAT", "current_time", current_time)}</span>'
                    )
                )
            )

        @bindings.add("f1")
        def _(event):
            """F1 显示帮助"""
            event.app.current_buffer.text = "/help"
            event.app.current_buffer.validate_and_handle()

        return bindings

    def _format_output(self, text):
        """格式化并显示输出"""
        self._internal_commands_output = text
        print_formatted_text(HTML(text))
        self._internal_commands_output = None

    def _command_help(self):
        """显示帮助信息"""
        help_items = [
            ("/exit, /quit", get_text("CHAT", "help_exit", "退出Viby")),
            ("/help", get_text("CHAT", "help_help", "显示此帮助信息")),
            ("/history_view", get_text("CHAT", "help_history", "显示最近命令历史")),
            ("/history_clear", get_text("CHAT", "help_history_clear", "清除命令历史")),
            ("/status", get_text("CHAT", "help_status", "显示当前状态信息")),
            ("/version", get_text("GENERAL", "version_help", "显示程序版本信息")),
        ]

        command_text = "\n".join(
            [
                f'  <span class="help-command">{cmd}</span> - <span class="help-desc">{desc}</span>'
                for cmd, desc in help_items
            ]
        )
        shortcuts = [
            get_text("CHAT", "shortcut_time"),
            get_text("CHAT", "shortcut_help"),
            get_text("CHAT", "shortcut_exit"),
        ]
        shortcuts_text = "\n".join(
            [f'  <span class="help-desc">{shortcut}</span>' for shortcut in shortcuts]
        )

        self._format_output(
            f'<span class="help-title">{get_text("CHAT", "help_title", "可用内部命令:")}</span>\n'
            f"{command_text}\n\n"
            f'<span class="help-desc">{get_text("CHAT", "help_shortcuts", "快捷键:")}</span>\n'
            f"{shortcuts_text}"
        )

    def _command_history_view(self, limit=20):
        """显示命令历史"""
        history_items = list(self.history.load_history_strings())
        if not history_items:
            self._format_output(
                f'<span class="warning">{get_text("CHAT", "history_empty", "还没有命令历史。")}</span>'
            )
            return

        display_items = history_items[-limit:]
        history_text = "\n".join(
            [
                f'  <span class="history-item">{i + 1}. {item}</span>'
                for i, item in enumerate(display_items)
            ]
        )
        self._format_output(
            f'<span class="history-title">{get_text("CHAT", "history_title", "最近命令历史:")}\n'
            f"{history_text}</span>"
        )

    def _command_history_clear(self):
        """清除命令历史"""
        try:
            if not self.history_path.exists():
                self._format_output(
                    f'<span class="warning">{get_text("CHAT", "history_not_found", "没有找到历史文件。")}</span>'
                )
                return

            # 创建备份并清空历史文件
            import shutil

            backup_path = f"{self.history_path}.bak"
            shutil.copy2(self.history_path, backup_path)
            self.history_path.write_text("")

            self._format_output(
                f'<span class="command">{get_text("CHAT", "history_cleared", "命令历史已清除。已创建备份：")} {backup_path}</span>'
            )
        except Exception as e:
            self._format_output(
                f'<span class="error">{get_text("CHAT", "history_clear_error", "清除历史时出错:")} {str(e)}</span>'
            )

    def _command_status(self):
        """显示当前状态信息"""
        status_items = [
            ("时间", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("系统", f"{platform.system()} {platform.release()}"),
            ("Python", platform.python_version()),
            ("历史条目", str(len(list(self.history.load_history_strings())))),
        ]

        status_text = "\n".join(
            [
                f'  <span class="help-command">{name}:</span> <span class="help-desc">{value}</span>'
                for name, value in status_items
            ]
        )

        self._format_output(
            f'<span class="help-title">{get_text("CHAT", "status_title", "系统状态:")}</span>\n'
            f"{status_text}"
        )

    def _command_version(self):
        """显示版本信息"""
        try:
            from importlib.metadata import version

            viby_version = version("viby")
        except ImportError:
            viby_version = "无法获取版本信息"

        self._format_output(
            f'<span class="help-title">{get_text("CHAT", "version_info")}</span>\n'
            f'  <span class="help-desc">{get_text("CHAT", "version_number", viby_version)}</span>'
        )

    def exec(self, prep_res):
        # 获取用户输入提示
        input_prompt_formatted = HTML(
            f'<span class="input-prompt">{get_text("CHAT", "input_prompt")}</span>'
        )

        # 命令处理映射
        command_handlers = {
            "help": self._command_help,
            "history_view": self._command_history_view,
            "history_clear": self._command_history_clear,
            "status": self._command_status,
            "version": self._command_version,
            "exit": lambda: "exit",
        }

        while True:
            user_input = prompt(
                input_prompt_formatted,
                history=self.history,
                completer=self.command_completer,
                key_bindings=self.key_bindings,
                style=self.style,
            )

            # 忽略空输入
            if not user_input.strip():
                continue

            # 检查是否是内部命令
            cmd = self.COMMANDS.get(user_input.lower())
            if cmd:
                result = command_handlers.get(cmd)
                if result:
                    # 执行命令处理函数
                    cmd_result = result()
                    # 如果返回值是 "exit"，则退出
                    if cmd_result == "exit":
                        return "exit"
                    # 否则继续提示
                    continue

            # 不是内部命令，返回用户输入
            return user_input

    def post(self, shared, prep_res, exec_res):
        # 检查是否退出
        if exec_res == "exit":
            return "exit"

        # 初始化消息历史（如果不存在）
        if "messages" not in shared:
            shared["messages"] = []

        # 保存用户输入并添加到消息历史
        shared["user_input"] = exec_res
        shared["messages"].append({"role": "user", "content": exec_res})

        # 路由到合适的节点
        return "first_input" if len(shared["messages"]) == 1 else "call_llm"
