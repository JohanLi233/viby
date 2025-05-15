"""
历史管理命令 - 提供历史记录的查询、导出和管理功能
"""

import os
from pathlib import Path
from datetime import datetime
from rich.table import Table
from rich.console import Console
from rich.prompt import Confirm
from rich.progress import Progress

from viby.utils.history import HistoryManager
from viby.utils.renderer import print_markdown
from viby.locale import get_text
import typer


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
        self.history_manager = HistoryManager()
        self.console = Console()

    def _truncate(self, text: str, limit: int) -> str:
        return text if len(text) <= limit else text[: limit - 3] + "..."

    def _format_records(
        self, records, title: str, content_limit: int, response_limit: int = None
    ) -> None:
        if response_limit is None:
            response_limit = content_limit
        table = Table(title=title)
        table.add_column("ID", justify="right", style="cyan")
        table.add_column(get_text("HISTORY", "timestamp"), style="green")
        table.add_column(get_text("HISTORY", "type"), style="magenta")
        table.add_column(get_text("HISTORY", "content"), style="white")
        table.add_column(get_text("HISTORY", "response"), style="yellow")
        for record in records:
            dt = datetime.fromisoformat(record["timestamp"])
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            content = self._truncate(record["content"], content_limit)
            response = self._truncate(record.get("response", ""), response_limit)
            table.add_row(
                str(record["id"]), formatted_time, record["type"], content, response
            )
        self.console.print(table)

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

        self._format_records(
            records, get_text("HISTORY", "recent_history"), content_limit=256
        )
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

        self._format_records(
            records,
            get_text("HISTORY", "search_results").format(query),
            content_limit=50,
        )
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

    def clear_history(self) -> int:
        """
        清除历史记录

        Returns:
            命令退出码
        """
        # 确认清除
        confirmation = get_text("HISTORY", "confirm_clear_all")
        if not Confirm.ask(confirmation):
            print_markdown(get_text("HISTORY", "clear_cancelled"), "")
            return 0

        # 显示清除进度
        with Progress() as progress:
            task = progress.add_task(get_text("HISTORY", "clearing_history"), total=1)

            # 清除历史记录
            success = self.history_manager.clear_history()

            progress.update(task, completed=1)

        if success:
            print_markdown(get_text("HISTORY", "clear_successful"), "success")
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


app = typer.Typer(
    help=get_text("HISTORY", "command_help"),
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command("list")
def cli_list(
    limit: int = typer.Option(
        10, "--limit", "-n", help=get_text("HISTORY", "limit_help")
    ),
):
    """列出历史记录。"""
    code = HistoryCommand().list_history(limit)
    raise typer.Exit(code=code)


@app.command("search")
def cli_search(
    query: str = typer.Argument(..., help=get_text("HISTORY", "query_help")),
    limit: int = typer.Option(
        10, "--limit", "-n", help=get_text("HISTORY", "limit_help")
    ),
):
    """搜索历史记录。"""
    code = HistoryCommand().search_history(query, limit)
    raise typer.Exit(code=code)


@app.command("export")
def cli_export(
    file: str = typer.Argument(..., help=get_text("HISTORY", "file_help")),
):
    """导出历史记录到文件。"""
    code = HistoryCommand().export_history(file)
    raise typer.Exit(code=code)


@app.command("clear")
def cli_clear(
    force: bool = typer.Option(
        False, "--force", "-f", help=get_text("HISTORY", "force_help")
    ),
):
    """清除历史记录。"""
    code = HistoryCommand().clear_history()
    raise typer.Exit(code=code)


@app.command("shell")
def cli_shell(
    limit: int = typer.Option(
        10, "--limit", "-n", help=get_text("HISTORY", "limit_help")
    ),
):
    """列出shell命令历史。"""
    code = HistoryCommand().list_shell_history(limit)
    raise typer.Exit(code=code)
