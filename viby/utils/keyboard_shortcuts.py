#!/usr/bin/env python3
"""
Viby 键盘快捷键集成模块
提供终端快捷键绑定功能
"""

import os
import logging
from pathlib import Path
from typing import Dict, Optional

# 导入语言文本获取函数
from viby.locale import get_text

# 获取日志记录器
logger = logging.getLogger(__name__)

# 定义不同shell的配置文件路径和命令
SHELL_CONFIG = {
    "bash": {
        "path": "~/.bashrc",
        "command": '\n# Viby keyboard shortcut\nbind -x \'"\\C-q": "yb $READLINE_LINE"\'\n',
    },
    "zsh": {
        "path": "~/.zshrc",
        "command": '\n# Viby keyboard shortcut\nviby-shortcut() { [[ -n "$BUFFER" ]] && BUFFER="yb $BUFFER" || BUFFER="yb"; zle accept-line; }\nzle -N viby-shortcut\nbindkey "^q" viby-shortcut\n',
    },
    "fish": {
        "path": "~/.config/fish/config.fish",
        "command": '\n# Viby keyboard shortcut\nfunction viby_shortcut\n  set -l cmd (commandline)\n  if test -n "$cmd"\n    commandline -r "yb $cmd"\n  else\n    commandline -r "yb"\n  end\n  commandline -f execute\nend\nbind \\cq viby_shortcut\n',
    },
}


def detect_shell() -> Optional[str]:
    """
    检测用户使用的shell

    Returns:
        shell名称（bash, zsh, fish）或None（如果无法检测）
    """
    shell_path = os.environ.get("SHELL", "")
    if not shell_path:
        return None

    shell_name = os.path.basename(shell_path).lower()
    return shell_name if shell_name in SHELL_CONFIG else None


def install_shortcuts(shell: Optional[str] = None) -> Dict[str, str]:
    """
    安装Viby键盘快捷键到用户的shell配置

    Args:
        shell: 可选指定shell名称（否则自动检测）

    Returns:
        包含操作结果的字典
    """
    # 自动检测shell类型
    if not shell:
        shell = detect_shell()

    # 验证shell类型
    if not shell or shell not in SHELL_CONFIG:
        return {
            "status": "error",
            "message": get_text("SHORTCUTS", "shell_not_supported").format(shell),
        }

    # 获取配置信息
    config_info = SHELL_CONFIG[shell]
    config_path = Path(os.path.expanduser(config_info["path"]))
    shortcut_command = config_info["command"]

    # 检查快捷键是否已存在
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                if shortcut_command.strip() in f.read():
                    return {
                        "status": "info",
                        "message": get_text("SHORTCUTS", "install_exists").format(
                            config_path
                        ),
                    }
        except Exception as e:
            logger.error(f"{get_text('SHORTCUTS', 'read_config_error')}: {e}")

    # 添加快捷键绑定
    try:
        # 确保配置文件所在目录存在
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # 添加快捷键配置
        with open(config_path, "a", encoding="utf-8") as f:
            f.write(shortcut_command)

        return {
            "status": "success",
            "message": get_text("SHORTCUTS", "install_success").format(config_path),
            "action_required": f"{config_path}",
        }
    except Exception as e:
        logger.error(f"{get_text('SHORTCUTS', 'install_error_log')}: {e}")
        return {
            "status": "error",
            "message": get_text("SHORTCUTS", "install_error").format(str(e)),
        }


def main():
    """
    主函数，直接从命令行运行时使用
    """
    result = install_shortcuts()
    print(f"{get_text('SHORTCUTS', 'status')}: {result['status']}")
    print(f"{get_text('SHORTCUTS', 'message')}: {result['message']}")
    if "action_required" in result:
        print(
            get_text("SHORTCUTS", "action_instructions").format(
                result["action_required"]
            )
        )


if __name__ == "__main__":
    main()
