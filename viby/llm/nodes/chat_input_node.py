import os
import platform
from pathlib import Path

from pocketflow import Node
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

from viby.locale import get_text


class ChatInputNode(Node):
    """获取用户输入并将其添加到消息历史中"""

    COMMANDS = {
        "/exit": "exit",
        "/quit": "exit",
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
        # No extra key bindings needed except default for exit
        self.key_bindings = KeyBindings()

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

    def exec(self, prep_res):
        # 获取用户输入提示
        input_prompt_formatted = HTML(
            f'<span class="input-prompt">{get_text("CHAT", "input_prompt")}</span>'
        )

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

            cmd = self.COMMANDS.get(user_input.lower())
            if cmd == "exit":
                return "exit"

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
