"""
会话管理命令 - 提供会话管理和历史记录的查询、导出功能
"""

import os
from datetime import datetime
from rich.table import Table
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.progress import Progress

from viby.utils.history import SessionManager
from viby.utils.ui import print_markdown
from viby.locale import get_text
import typer


class SessionsCommand:
    """
    会话管理命令类，提供会话管理和历史记录的查询、导出功能
    支持以下子命令：
    - list - 列出所有会话
    - create - 创建新会话
    - activate - 设置活跃会话
    - rename - 重命名会话
    - delete - 删除会话
    - show - 显示会话历史记录
    - search - 搜索会话历史记录
    - export - 导出会话历史记录
    - clear - 清除会话历史记录
    """

    def __init__(self):
        """初始化会话命令"""
        self.session_manager = SessionManager()
        self.console = Console()

    def _truncate(self, text: str, limit: int) -> str:
        """截断文本，超过长度限制的部分用省略号表示"""
        return text if len(text) <= limit else text[: limit - 3] + "..."

    def _format_records(
        self, records, title: str, content_limit: int, response_limit: int = None
    ) -> None:
        """格式化历史记录显示为表格"""
        if response_limit is None:
            response_limit = content_limit

        table = Table(title=title)
        table.add_column("ID", justify="right", style="cyan")
        table.add_column(get_text("SESSIONS", "timestamp"), style="green")
        table.add_column(get_text("SESSIONS", "type"), style="magenta")
        table.add_column(get_text("SESSIONS", "content"), style="white")
        table.add_column(get_text("SESSIONS", "response"), style="yellow")

        for record in records:
            dt = datetime.fromisoformat(record["timestamp"])
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            content = self._truncate(record["content"], content_limit)
            response = self._truncate(record.get("response", ""), response_limit)
            table.add_row(
                str(record["id"]), formatted_time, record["type"], content, response
            )
        self.console.print(table)

    def list_sessions(self) -> int:
        """
        列出所有会话

        Returns:
            命令退出码
        """
        sessions = self.session_manager.get_sessions()

        if not sessions:
            print_markdown(get_text("SESSIONS", "no_sessions"), "")
            return 0

        table = Table(title=get_text("SESSIONS", "sessions_list"))
        table.add_column("ID", style="cyan")
        table.add_column(get_text("SESSIONS", "name"), style="green")
        table.add_column(get_text("SESSIONS", "created_at"), style="magenta")
        table.add_column(get_text("SESSIONS", "last_used"), style="yellow")
        table.add_column(get_text("SESSIONS", "interactions"), style="blue")
        table.add_column(get_text("SESSIONS", "status"), style="white")

        for session in sessions:
            # 格式化时间
            created_at = datetime.fromisoformat(session["created_at"]).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            last_used = datetime.fromisoformat(session["last_used"]).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            # 获取交互次数
            interaction_count = session.get("interaction_count", 0)

            # 状态（活跃/非活跃）
            status = get_text("SESSIONS", "active") if session["is_active"] == 1 else ""

            table.add_row(
                session["id"],
                session["name"],
                created_at,
                last_used,
                str(interaction_count),
                status,
            )

        self.console.print(table)
        return 0

    def create_session(self, name: str = None, description: str = None) -> int:
        """
        创建新的会话，如果名称为空使用默认命名方案

        Args:
            name: 会话名称，可选
            description: 会话描述，可选

        Returns:
            命令退出码
        """
        # 传入原始name参数，让session_manager负责生成默认名称
        session_id = self.session_manager.create_session(name, description)

        if session_id:
            # 获取创建的会话实际名称
            sessions = self.session_manager.get_sessions()
            session = next((s for s in sessions if s["id"] == session_id), None)
            if session:
                session_name = session["name"]
            else:
                session_name = name or "New Session"  # 防御性编程

            print_markdown(
                get_text("SESSIONS", "create_session_success").format(
                    session_name, session_id
                ),
                "success",
            )
            return 0
        else:
            print_markdown(get_text("SESSIONS", "create_session_failed"), "error")
            return 1

    def set_active_session(self, session_id: str = None) -> int:
        """
        设置活跃会话

        Args:
            session_id: 会话ID，如未提供则显示交互式选择

        Returns:
            命令退出码
        """
        sessions = self.session_manager.get_sessions()

        if not sessions:
            print_markdown(get_text("SESSIONS", "no_sessions"), "error")
            return 1

        # 如果未提供会话ID，显示交互式选择
        if not session_id:
            # 创建选项列表
            options = {}
            for i, session in enumerate(sessions, 1):
                is_active = "✓" if session["is_active"] == 1 else " "
                options[str(i)] = f"{is_active} {session['name']} ({session['id']})"

            # 显示选项
            self.console.print(get_text("SESSIONS", "select_session"))
            for key, value in options.items():
                self.console.print(f"[cyan]{key}[/cyan]: {value}")

            # 获取用户选择
            choice = Prompt.ask(
                get_text("SESSIONS", "enter_selection"),
                choices=list(options.keys()),
                show_choices=False,
            )

            # 获取所选会话ID
            session_id = sessions[int(choice) - 1]["id"]

        # 验证会话ID是否存在
        session = next((s for s in sessions if s["id"] == session_id), None)
        if not session:
            print_markdown(
                get_text("SESSIONS", "session_not_found").format(session_id), "error"
            )
            return 1

        # 如果会话已经是活跃的，不需要切换
        if session["is_active"] == 1:
            print_markdown(
                get_text("SESSIONS", "session_already_active").format(session["name"]),
                "",
            )
            return 0

        success = self.session_manager.set_active_session(session_id)

        if success:
            print_markdown(
                get_text("SESSIONS", "session_activated").format(session["name"]),
                "success",
            )
            return 0
        else:
            print_markdown(get_text("SESSIONS", "session_activation_failed"), "error")
            return 1

    def rename_session(self, session_id: str, new_name: str) -> int:
        """
        重命名会话

        Args:
            session_id: 会话ID
            new_name: 新名称

        Returns:
            命令退出码
        """
        if not new_name:
            print_markdown(get_text("SESSIONS", "new_name_required"), "error")
            return 1

        sessions = self.session_manager.get_sessions()

        # 验证会话ID是否存在
        session = next((s for s in sessions if s["id"] == session_id), None)
        if not session:
            print_markdown(
                get_text("SESSIONS", "session_not_found").format(session_id), "error"
            )
            return 1

        success = self.session_manager.rename_session(session_id, new_name)

        if success:
            print_markdown(
                get_text("SESSIONS", "session_renamed").format(
                    session["name"], new_name
                ),
                "success",
            )
            return 0
        else:
            print_markdown(get_text("SESSIONS", "session_rename_failed"), "error")
            return 1

    def delete_session(self, session_id: str = None) -> int:
        """
        删除会话及其历史记录

        Args:
            session_id: 会话ID，如未提供则显示交互式选择

        Returns:
            命令退出码
        """
        sessions = self.session_manager.get_sessions()

        if not sessions:
            print_markdown(get_text("SESSIONS", "no_sessions"), "error")
            return 1

        # 如果未提供会话ID，显示交互式选择
        if not session_id:
            # 创建选项列表
            options = {}
            for i, session in enumerate(sessions, 1):
                is_active = "✓" if session["is_active"] == 1 else " "
                options[str(i)] = f"{is_active} {session['name']} ({session['id']})"

            # 显示选项
            self.console.print(get_text("SESSIONS", "select_session_delete"))
            for key, value in options.items():
                self.console.print(f"[cyan]{key}[/cyan]: {value}")

            # 获取用户选择
            choice = Prompt.ask(
                get_text("SESSIONS", "enter_selection"),
                choices=list(options.keys()),
                show_choices=False,
            )

            # 获取所选会话ID
            session_id = sessions[int(choice) - 1]["id"]

        # 验证会话ID是否存在
        session = next((s for s in sessions if s["id"] == session_id), None)
        if not session:
            print_markdown(
                get_text("SESSIONS", "session_not_found").format(session_id), "error"
            )
            return 1

        # 确认删除
        confirmation = get_text("SESSIONS", "confirm_delete_session").format(
            session["name"]
        )
        if not Confirm.ask(confirmation):
            print_markdown(get_text("SESSIONS", "delete_cancelled"), "")
            return 0

        # 如果只有一个会话，不允许删除
        if len(sessions) <= 1:
            print_markdown(get_text("SESSIONS", "cannot_delete_last_session"), "error")
            return 1

        success = self.session_manager.delete_session(session_id)

        if success:
            print_markdown(
                get_text("SESSIONS", "session_deleted").format(session["name"]),
                "success",
            )
            return 0
        else:
            print_markdown(get_text("SESSIONS", "session_delete_failed"), "error")
            return 1

    def show_history(self, limit: int = 10, session_id: str = None) -> int:
        """
        显示会话历史记录

        Args:
            limit: 显示的最大记录数量
            session_id: 指定会话ID，默认为当前活跃会话

        Returns:
            命令退出码
        """
        records = self.session_manager.get_history(limit=limit, session_id=session_id)

        if not records:
            print_markdown(get_text("SESSIONS", "no_history"), "")
            return 0

        # 获取会话名称
        if session_id:
            sessions = self.session_manager.get_sessions()
            session_name = next(
                (s["name"] for s in sessions if s["id"] == session_id), "未知会话"
            )
            title = f"{get_text('SESSIONS', 'recent_history')} - {session_name}"
        else:
            # 从第一条记录获取会话名称
            title = f"{get_text('SESSIONS', 'recent_history')} - {records[0].get('session_name', '默认会话')}"

        self._format_records(records, title, content_limit=256)
        return 0

    def search_history(
        self, query: str, limit: int = 10, session_id: str = None
    ) -> int:
        """
        搜索会话历史记录

        Args:
            query: 搜索关键词
            limit: 显示的最大记录数量
            session_id: 指定会话ID，默认为当前活跃会话

        Returns:
            命令退出码
        """
        if not query:
            print_markdown(get_text("SESSIONS", "search_term_required"), "error")
            return 1

        records = self.session_manager.get_history(
            limit=limit, search_query=query, session_id=session_id
        )

        if not records:
            print_markdown(
                get_text("SESSIONS", "no_matching_history").format(query), ""
            )
            return 0

        # 获取会话名称
        if session_id:
            sessions = self.session_manager.get_sessions()
            session_name = next(
                (s["name"] for s in sessions if s["id"] == session_id), "未知会话"
            )
            title = f"{get_text('SESSIONS', 'search_results').format(query)} - {session_name}"
        else:
            # 从第一条记录获取会话名称，如果有记录的话
            title = f"{get_text('SESSIONS', 'search_results').format(query)} - {records[0].get('session_name', '默认会话')}"

        self._format_records(records, title, content_limit=50)
        return 0

    def export_history(
        self,
        file_path: str,
        format_type: str = "json",
        session_id: str = None,
    ) -> int:
        """
        导出会话历史记录到文件

        Args:
            file_path: 导出文件路径
            format_type: 导出格式（json, csv, yaml）
            session_id: 指定会话ID，默认为当前活跃会话

        Returns:
            命令退出码
        """
        if not file_path:
            print_markdown(get_text("SESSIONS", "export_path_required"), "error")
            return 1

        # 确保目录存在
        output_dir = os.path.dirname(file_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                print_markdown(
                    get_text("SESSIONS", "create_directory_failed").format(e), "error"
                )
                return 1

        # 如果文件已存在，确认是否覆盖
        if os.path.exists(file_path):
            if not Confirm.ask(
                get_text("SESSIONS", "file_exists_overwrite").format(file_path)
            ):
                print_markdown(get_text("SESSIONS", "export_cancelled"), "")
                return 0

        # 显示导出进度
        with Progress() as progress:
            task = progress.add_task(get_text("SESSIONS", "exporting_history"), total=1)

            # 获取会话名称
            session_name = "当前会话"
            if session_id:
                sessions = self.session_manager.get_sessions()
                session_name = next(
                    (s["name"] for s in sessions if s["id"] == session_id), "未知会话"
                )

            # 导出历史记录
            success = self.session_manager.export_history(
                file_path, format_type, session_id
            )

            progress.update(task, completed=1)

        if success:
            print_markdown(
                get_text("SESSIONS", "export_successful").format(
                    file_path, format_type, session_name
                ),
                "success",
            )
            return 0
        else:
            print_markdown(get_text("SESSIONS", "export_failed"), "error")
            return 1

    def clear_history(self, session_id: str = None) -> int:
        """
        清除会话历史记录

        Args:
            session_id: 指定会话ID，默认为当前活跃会话

        Returns:
            命令退出码
        """
        # 获取会话名称
        session_name = "当前会话"
        if session_id:
            sessions = self.session_manager.get_sessions()
            session_name = next(
                (s["name"] for s in sessions if s["id"] == session_id), "未知会话"
            )

        # 确认清除
        confirmation = get_text("SESSIONS", "confirm_clear_session").format(
            session_name
        )
        if not Confirm.ask(confirmation):
            print_markdown(get_text("SESSIONS", "clear_cancelled"), "")
            return 0

        # 显示清除进度
        with Progress() as progress:
            task = progress.add_task(get_text("SESSIONS", "clearing_history"), total=1)

            # 清除历史记录
            success = self.session_manager.clear_history(session_id)

            progress.update(task, completed=1)

        if success:
            print_markdown(
                get_text("SESSIONS", "clear_session_successful").format(session_name),
                "success",
            )
            return 0
        else:
            print_markdown(get_text("SESSIONS", "clear_failed"), "error")
            return 1


app = typer.Typer(
    help=get_text("SESSIONS", "sessions_help"),
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command("list")
def cli_list():
    """列出所有会话。"""
    code = SessionsCommand().list_sessions()
    raise typer.Exit(code=code)


@app.command("create")
def cli_create(
    name: str = typer.Option(
        None, "--name", "-n", help=get_text("SESSIONS", "session_name_help")
    ),
    description: str = typer.Option(
        None,
        "--description",
        "-d",
        help=get_text("SESSIONS", "session_description_help"),
    ),
):
    """创建新会话。如果不指定名称则使用自动生成的名称。"""
    code = SessionsCommand().create_session(name, description)
    raise typer.Exit(code=code)


@app.command("activate")
def cli_activate(
    session_id: str = typer.Argument(
        ..., help=get_text("SESSIONS", "session_id_activate_help")
    ),
):
    """设置活跃会话。"""
    code = SessionsCommand().set_active_session(session_id)
    raise typer.Exit(code=code)


@app.command("rename")
def cli_rename(
    session_id: str = typer.Argument(..., help=get_text("SESSIONS", "session_id_help")),
    new_name: str = typer.Argument(..., help=get_text("SESSIONS", "new_name_help")),
):
    """重命名会话。"""
    code = SessionsCommand().rename_session(session_id, new_name)
    raise typer.Exit(code=code)


@app.command("delete")
def cli_delete(
    session_id: str = typer.Argument(
        ..., help=get_text("SESSIONS", "session_id_delete_help")
    ),
):
    """删除会话及其历史记录。"""
    code = SessionsCommand().delete_session(session_id)
    raise typer.Exit(code=code)


@app.command("show")
def cli_show(
    limit: int = typer.Option(
        10, "--limit", "-n", help=get_text("SESSIONS", "limit_help")
    ),
    session: str = typer.Option(
        None, "--session", "-s", help=get_text("SESSIONS", "session_id_help")
    ),
):
    """显示会话的历史记录。"""
    code = SessionsCommand().show_history(limit, session)
    raise typer.Exit(code=code)


@app.command("search")
def cli_search(
    query: str = typer.Argument(..., help=get_text("SESSIONS", "query_help")),
    limit: int = typer.Option(
        10, "--limit", "-n", help=get_text("SESSIONS", "limit_help")
    ),
    session: str = typer.Option(
        None, "--session", "-s", help=get_text("SESSIONS", "session_id_help")
    ),
):
    """搜索会话中的历史记录。"""
    code = SessionsCommand().search_history(query, limit, session)
    raise typer.Exit(code=code)


@app.command("export")
def cli_export(
    file: str = typer.Argument(..., help=get_text("SESSIONS", "file_help")),
    format_type: str = typer.Option(
        "json", "--format", "-f", help=get_text("SESSIONS", "format_help")
    ),
    session: str = typer.Option(
        None, "--session", "-s", help=get_text("SESSIONS", "session_id_help")
    ),
):
    """导出会话历史记录到文件。"""
    code = SessionsCommand().export_history(file, format_type, session)
    raise typer.Exit(code=code)


@app.command("clear")
def cli_clear(
    session: str = typer.Option(
        None, "--session", "-s", help=get_text("SESSIONS", "session_id_help")
    ),
):
    """清除会话历史记录。"""
    code = SessionsCommand().clear_history(session)
    raise typer.Exit(code=code)
