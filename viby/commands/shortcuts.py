#!/usr/bin/env python3
"""
Viby 键盘快捷键命令
处理快捷键的安装和管理
"""

from typing import Optional
import typer
from viby.utils.keyboard_shortcuts import install_shortcuts, detect_shell
from viby.locale import get_text


class ShortcutsCommand:
    """处理快捷键安装和管理的命令"""

    def __init__(self):
        """初始化快捷键命令"""
        pass

    def run(self, shell: Optional[str] = None) -> int:
        """
        安装并管理快捷键
        """
        if not shell:
            detected_shell = detect_shell()
            if detected_shell:
                print(f"{get_text('SHORTCUTS', 'auto_detect_shell')}: {detected_shell}")
            else:
                print(get_text("SHORTCUTS", "auto_detect_failed"))
            shell = detected_shell

        result = install_shortcuts(shell)
        self._print_result(result)
        return 0 if result.get("status") in ["success", "info"] else 1

    def _print_result(self, result: dict) -> None:
        """
        打印操作结果

        Args:
            result: 操作结果字典
        """
        # 根据状态使用不同颜色
        if result["status"] == "success":
            status_color = "\033[92m"  # 绿色
        elif result["status"] == "info":
            status_color = "\033[94m"  # 蓝色
        else:
            status_color = "\033[91m"  # 红色

        reset_color = "\033[0m"

        print(
            f"{status_color}[{result['status'].upper()}]{reset_color} {result['message']}"
        )

        # 如果需要用户操作，显示提示
        if "action_required" in result:
            print(
                f"\n{get_text('SHORTCUTS', 'action_required').format(result['action_required'])}"
            )

        if result["status"] == "success":
            print(f"\n{get_text('SHORTCUTS', 'activation_note')}")


app = typer.Typer(
    help=get_text("SHORTCUTS", "command_help"), invoke_without_command=True
)


@app.callback(invoke_without_command=True)
def cli(
    shell: Optional[str] = typer.Option(
        None, "--shell", "-s", help=get_text("SHORTCUTS", "auto_detect_shell")
    ),
):
    """安装和管理键盘快捷键。"""
    code = ShortcutsCommand().run(shell)
    raise typer.Exit(code=code)
