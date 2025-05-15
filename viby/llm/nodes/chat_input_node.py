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
    """
    获取用户输入并将其添加到消息历史中
    支持命令处理和历史记录功能
    """

    # 支持的命令及其对应的操作
    COMMANDS = {
        "/exit": "exit",
        "/quit": "exit",
    }

    def prep(self, shared):
        """准备用户输入所需的配置和组件"""
        # 配置路径、自动完成、样式和键绑定
        config = {
            "history_path": self._get_history_path(),
            "commands": self.COMMANDS,
            "style": self._create_style(),
        }

        # 确保历史文件目录存在
        config["history_path"].parent.mkdir(parents=True, exist_ok=True)

        # 创建历史记录对象
        config["history"] = FileHistory(str(config["history_path"]))

        # 创建命令自动完成器
        config["command_completer"] = WordCompleter(
            list(config["commands"].keys()), ignore_case=True
        )

        # 创建键绑定
        config["key_bindings"] = KeyBindings()

        return config

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

    @staticmethod
    def _create_style() -> Style:
        """创建输入界面的样式"""
        return Style.from_dict(
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

    def exec(self, config):
        """获取用户输入，处理命令"""
        # 获取输入提示
        input_prompt = HTML(
            f'<span class="input-prompt">{get_text("CHAT", "input_prompt")}</span>'
        )

        while True:
            # 获取用户输入
            user_input = prompt(
                input_prompt,
                history=config["history"],
                completer=config["command_completer"],
                key_bindings=config["key_bindings"],
                style=config["style"],
            )

            # 忽略空输入
            if not user_input.strip():
                continue

            # 检查是否是内部命令
            cmd = config["commands"].get(user_input.lower())
            if cmd == "exit":
                return {"action": "exit"}

            # 不是内部命令，返回用户输入
            return {"action": "input", "content": user_input}

    def exec_fallback(self, config, exc):
        """处理获取输入时发生的错误"""
        print(f"Error getting input: {str(exc)}")
        return {"action": "exit"}

    def post(self, shared, prep_res, exec_res):
        """处理用户输入结果并确定下一步流程"""
        # 检查是否应该退出
        if exec_res["action"] == "exit":
            return "exit"

        # 初始化消息历史（如果不存在）
        if "messages" not in shared:
            shared["messages"] = []

        # 保存用户输入并添加到消息历史
        user_input = exec_res["content"]
        shared["user_input"] = user_input
        shared["messages"].append({"role": "user", "content": user_input})

        # 确定下一个节点：首次输入还是继续对话
        return "first_input" if len(shared["messages"]) == 1 else "call_llm"
