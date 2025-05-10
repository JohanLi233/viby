"""
历史管理命令 - 提供历史记录的查询、导出和管理功能
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Any

from rich.table import Table
from rich.console import Console
from rich.prompt import Confirm
from rich.progress import Progress

from viby.utils.history import HistoryManager
from viby.utils.renderer import print_markdown
from viby.locale import get_text
from viby.config.app_config import Config


class HistoryCommand:
    """
    历史管理命令类，提供历史记录的查询、导出和管理功能
    支持以下子命令：
    - list - 列出历史记录
    - search - 搜索历史记录
    - export - 导出历史记录
    - clear - 清除历史记录
    - shell - 显示shell命令历史
    """

    def __init__(self):
        """初始化历史命令"""
        self.config = Config()
        self.history_manager = HistoryManager(self.config)
        self.console = Console()

    def execute(self, subcommand: str, args: Any) -> int:
        """
        执行历史命令

        Args:
            subcommand: 子命令名称（list, search, export, clear, shell）
            args: 命令行参数

        Returns:
            命令退出码
        """
        if subcommand == "list":
            return self.list_history(args.limit)
        elif subcommand == "search":
            return self.search_history(args.query, args.limit)
        elif subcommand == "export":
            return self.export_history(args.file, args.format, args.type)
        elif subcommand == "clear":
            return self.clear_history(args.type, args.force)
        elif subcommand == "shell":
            return self.list_shell_history(args.limit)
        else:
            print(get_text("COMMANDS", "unknown_subcommand").format(subcommand))
            return 1

    def list_history(self, limit: int = 10) -> int:
        """
        列出历史记录

        Args:
            limit: 显示的最大记录数量

        Returns:
            命令退出码
        """
        records = self.history_manager.get_history(limit=limit)

        if not records:
            print_markdown(get_text("HISTORY", "no_history"), "")
            return 0

        table = Table(title=get_text("HISTORY", "recent_history"))
        table.add_column("ID", justify="right", style="cyan")
        table.add_column(get_text("HISTORY", "timestamp"), style="green")
        table.add_column(get_text("HISTORY", "type"), style="magenta")
        table.add_column(get_text("HISTORY", "content"), style="white")
        table.add_column(get_text("HISTORY", "response"), style="yellow")

        for record in records:
            # 格式化时间戳
            dt = datetime.fromisoformat(record["timestamp"])
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")

            # 限制内容长度
            content = record["content"]
            if len(content) > 256:
                content = content[:256] + "..."

            # 添加响应内容，同样限制长度
            response = record.get("response", "")
            if response and len(response) > 256:
                response = response[:256] + "..."

            table.add_row(
                str(record["id"]), formatted_time, record["type"], content, response
            )

        self.console.print(table)
        return 0

    def search_history(self, query: str, limit: int = 10) -> int:
        """
        搜索历史记录

        Args:
            query: 搜索关键词
            limit: 显示的最大记录数量

        Returns:
            命令退出码
        """
        if not query:
            print_markdown(get_text("HISTORY", "search_term_required"), "error")
            return 1

        records = self.history_manager.get_history(limit=limit, search_query=query)

        if not records:
            print_markdown(get_text("HISTORY", "no_matching_history").format(query), "")
            return 0

        table = Table(title=get_text("HISTORY", "search_results").format(query))
        table.add_column("ID", justify="right", style="cyan")
        table.add_column(get_text("HISTORY", "timestamp"), style="green")
        table.add_column(get_text("HISTORY", "type"), style="magenta")
        table.add_column(get_text("HISTORY", "content"), style="white")
        table.add_column(get_text("HISTORY", "response"), style="yellow")

        for record in records:
            # 格式化时间戳
            dt = datetime.fromisoformat(record["timestamp"])
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")

            # 限制内容长度
            content = record["content"]
            if len(content) > 50:
                content = content[:47] + "..."

            # 添加响应内容，同样限制长度
            response = record.get("response", "")
            if response and len(response) > 50:
                response = response[:47] + "..."

            table.add_row(
                str(record["id"]), formatted_time, record["type"], content, response
            )

        self.console.print(table)
        return 0

    def export_history(
        self,
        file_path: str,
        format_type: str = "json",
        history_type: str = "interactions",
    ) -> int:
        """
        导出历史记录到文件

        Args:
            file_path: 导出文件路径
            format_type: 导出格式（json, csv, yaml）
            history_type: 导出的历史类型（interactions, shell）

        Returns:
            命令退出码
        """
        if not file_path:
            print_markdown(get_text("HISTORY", "export_path_required"), "error")
            return 1

        # 确保目录存在
        output_dir = os.path.dirname(file_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                print_markdown(
                    get_text("HISTORY", "create_directory_failed").format(e), "error"
                )
                return 1

        # 如果文件已存在，确认是否覆盖
        if os.path.exists(file_path):
            if not Confirm.ask(
                get_text("HISTORY", "file_exists_overwrite").format(file_path)
            ):
                print_markdown(get_text("HISTORY", "export_cancelled"), "")
                return 0

        # 显示导出进度
        with Progress() as progress:
            task = progress.add_task(get_text("HISTORY", "exporting_history"), total=1)

            # 导出历史记录
            success = self.history_manager.export_history(
                file_path, format_type, history_type
            )

            progress.update(task, completed=1)

        if success:
            print_markdown(
                get_text("HISTORY", "export_successful").format(
                    file_path, format_type, history_type
                ),
                "success",
            )
            return 0
        else:
            print_markdown(get_text("HISTORY", "export_failed"), "error")
            return 1

    def clear_history(self, history_type: str = "all", force: bool = False) -> int:
        """
        清除历史记录

        Args:
            history_type: 要清除的历史类型（all, interactions, shell）
            force: 是否强制清除，不提示确认

        Returns:
            命令退出码
        """
        if not force:
            confirmation = get_text("HISTORY", "confirm_clear_all")
            if history_type == "interactions":
                confirmation = get_text("HISTORY", "confirm_clear_interactions")
            elif history_type == "shell":
                confirmation = get_text("HISTORY", "confirm_clear_shell")

            if not Confirm.ask(confirmation):
                print_markdown(get_text("HISTORY", "clear_cancelled"), "")
                return 0

        # 显示清除进度
        with Progress() as progress:
            task = progress.add_task(get_text("HISTORY", "clearing_history"), total=1)

            # 清除历史记录
            success = self.history_manager.clear_history(history_type)

            progress.update(task, completed=1)

        if success:
            print_markdown(
                get_text("HISTORY", "clear_successful").format(history_type), "success"
            )
            return 0
        else:
            print_markdown(get_text("HISTORY", "clear_failed"), "error")
            return 1

    def list_shell_history(self, limit: int = 10) -> int:
        """
        列出shell命令历史

        Args:
            limit: 显示的最大记录数量

        Returns:
            命令退出码
        """
        records = self.history_manager.get_shell_history(limit=limit)

        if not records:
            print_markdown(get_text("HISTORY", "no_shell_history"), "")
            return 0

        table = Table(title=get_text("HISTORY", "recent_shell_history"))
        table.add_column("ID", justify="right", style="cyan")
        table.add_column(get_text("HISTORY", "timestamp"), style="green")
        table.add_column(get_text("HISTORY", "directory"), style="magenta")
        table.add_column(get_text("HISTORY", "command"), style="white")
        table.add_column(get_text("HISTORY", "exit_code"), style="yellow")

        for record in records:
            # 格式化时间戳
            dt = datetime.fromisoformat(record["timestamp"])
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")

            # 限制命令长度
            command = record["command"]
            if len(command) > 50:
                command = command[:47] + "..."

            # 格式化目录，从绝对路径转为相对路径或~
            directory = record["directory"] or ""
            if directory:
                home = str(Path.home())
                if directory.startswith(home):
                    directory = "~" + directory[len(home) :]

            # 格式化退出码
            exit_code = (
                str(record["exit_code"]) if record["exit_code"] is not None else ""
            )

            table.add_row(
                str(record["id"]), formatted_time, directory, command, exit_code
            )

        self.console.print(table)
        return 0
