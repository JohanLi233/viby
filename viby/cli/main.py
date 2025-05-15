#!/usr/bin/env python3
"""
viby CLI入口点 - 基于Typer框架的命令行接口
"""

import sys
from typing import NoReturn

from viby.cli.app import app


def main() -> int:
    """
    viby CLI主入口函数

    Returns:
        退出状态码
    """
    try:
        return app(standalone_mode=False) or 0
    except Exception as e:
        print(e)
        return 1


def entry_point() -> NoReturn:
    """
    作为命令行工具的入口点
    """
    sys.exit(main())


if __name__ == "__main__":
    entry_point()
