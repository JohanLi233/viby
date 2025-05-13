"""
嵌入服务相关命令

包含嵌入服务器启动、停止、状态检查和更新等命令
"""

import logging
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from viby.locale import get_text
from viby.config import Config
from viby.mcp.client import list_tools
from viby.viby_tool_search.client import (
    start_embedding_server,
    stop_embedding_server,
    check_server_status,
    EmbeddingServerStatus,
    is_server_running,
    update_tools,
)

logger = logging.getLogger(__name__)
console = Console()


class EmbedServerCommand:
    """
    嵌入服务器管理命令类，提供嵌入向量服务器的启动、停止、状态检查和更新功能
    支持以下子命令:
    - start - 启动嵌入服务器
    - stop - 停止嵌入服务器
    - status - 检查嵌入服务器状态
    - update - 更新工具嵌入向量
    """

    def __init__(self):
        """初始化嵌入服务器命令"""
        self.config = Config()

    def execute(self, subcommand: str, args: any) -> int:
        """
        执行嵌入服务器命令

        Args:
            subcommand: 子命令名称（start, stop, status, update）
            args: 命令行参数

        Returns:
            命令退出码
        """
        # 根据子命令分派
        if subcommand == "start":
            return self.start_embed_server()
        elif subcommand == "stop":
            return self.stop_embed_server()
        elif subcommand == "status":
            return self.check_embed_server_status()
        elif subcommand == "update":
            return self.update_embeddings()
        else:
            console.print(
                f"[bold red]{get_text('COMMANDS', 'unknown_subcommand').format(subcommand)}[/bold red]"
            )
            return 1

    def update_embeddings(self) -> int:
        """更新MCP工具的嵌入向量"""
        try:
            console.print(
                Panel.fit(
                    get_text("TOOLS", "updating_embeddings"),
                    title=get_text("TOOLS", "embeddings_update_title"),
                )
            )
            if not self.config.enable_mcp:
                console.print(
                    f"[bold red]{get_text('TOOLS', 'mcp_not_enabled')}[/bold red]"
                )
                return 1
            tools_dict = list_tools()
            tool_count = sum(len(lst) for lst in tools_dict.values())
            if tool_count == 0:
                console.print(
                    f"[bold yellow]{get_text('TOOLS', 'no_tools_found')}[/bold yellow]"
                )
                return 0
            console.print(
                get_text("TOOLS", "start_updating_embeddings").format(
                    tool_count=f"[bold cyan]{tool_count}[/bold cyan]"
                )
            )
            if not is_server_running():
                console.print(
                    f"[bold yellow]{get_text('TOOLS', 'embedding_server_not_running')}[/bold yellow]"
                )
                console.print(
                    f"[bold yellow]{get_text('TOOLS', 'start_server_suggestion')}[/bold yellow]"
                )
                return 1
            console.print(
                f"[bold yellow]{get_text('TOOLS', 'using_embedding_server')}[/bold yellow]"
            )
            updated = update_tools()
            if updated:
                console.print(
                    f"[bold green]✓[/bold green] {get_text('TOOLS', 'embeddings_update_success')}"
                )
                self._display_tools_table(tools_dict)
                return 0
            console.print(
                f"[bold yellow]!{get_text('TOOLS', 'embeddings_update_via_server_failed')}[/bold yellow]"
            )
            console.print(
                f"[bold yellow]{get_text('TOOLS', 'start_server_suggestion')}[/bold yellow]"
            )
            return 1
        except Exception as e:
            console.print(
                f"[bold red]{get_text('TOOLS', 'error_updating_embeddings')}: {e}[/bold red]"
            )
            logger.exception(get_text("TOOLS", "embeddings_update_failed"))
            return 1

    def _print_panel(self, key: str, default: str):
        console.print(
            Panel.fit(
                get_text("TOOLS", key, default),
                title=get_text("TOOLS", "embed_server_title", "嵌入模型服务"),
            )
        )

    def _display_tools_table(self, tools_dict):
        table = Table(title=get_text("TOOLS", "updated_tools_table_title"))
        table.add_column(get_text("TOOLS", "tool_name_column"), style="cyan")
        table.add_column(get_text("TOOLS", "description_column"))
        for lst in tools_dict.values():
            for tool in lst:
                name = getattr(tool, "name", "未知工具")
                desc = getattr(tool, "description", "")
                if callable(desc):
                    try:
                        desc = desc()
                    except Exception:
                        desc = get_text("TOOLS", "description_unavailable")
                        logger.exception(f"获取工具 {name} 描述时出错")
                short_desc = desc[:60] + ("..." if len(desc) > 60 else "")
                table.add_row(name, short_desc)
        console.print(table)

    def start_embed_server(self) -> int:
        """启动嵌入模型服务器"""
        try:
            self._print_panel("starting_embed_server", "启动嵌入模型服务器")

            # 检查服务器是否已经在运行
            status = check_server_status()
            if status.status == EmbeddingServerStatus.RUNNING:
                console.print(
                    f"[bold yellow]{get_text('TOOLS', 'embed_server_already_running', '嵌入模型服务器已经在运行')}[/bold yellow]"
                )
                console.print(f"PID: {status.pid}")
                console.print(f"URL: {status.url}")
                if status.uptime:
                    console.print(
                        f"{get_text('TOOLS', 'embed_server_uptime', '运行时间')}: {status.uptime}"
                    )
                return 0

            # 启动服务器
            console.print(
                f"{get_text('TOOLS', 'starting_server', '正在启动服务器')}..."
            )
            result = start_embedding_server()

            if result.success:
                console.print(
                    f"[bold green]✓[/bold green] {get_text('TOOLS', 'embed_server_started', '嵌入模型服务器已启动')}"
                )
                console.print(f"PID: {result.pid}")
                return 0
            else:
                console.print(
                    f"[bold red]❌ {get_text('TOOLS', 'embed_server_start_failed', '嵌入模型服务器启动失败')}: {result.error}[/bold red]"
                )
                return 1

        except Exception as e:
            console.print(
                f"[bold red]{get_text('TOOLS', 'error_starting_server', '启动服务器时出错')}: {str(e)}[/bold red]"
            )
            logger.exception(
                get_text("TOOLS", "embed_server_start_failed", "嵌入模型服务器启动失败")
            )
            return 1

    def stop_embed_server(self) -> int:
        """停止嵌入模型服务器"""
        try:
            self._print_panel("stopping_embed_server", "停止嵌入模型服务器")

            # 检查服务器是否在运行
            status = check_server_status()
            if status.status != EmbeddingServerStatus.RUNNING:
                console.print(
                    f"[bold yellow]{get_text('TOOLS', 'embed_server_not_running', '嵌入模型服务器未运行')}[/bold yellow]"
                )
                return 0

            # 停止服务器
            console.print(
                f"{get_text('TOOLS', 'stopping_server', '正在停止服务器')}..."
            )
            result = stop_embedding_server()

            if result.success:
                console.print(
                    f"[bold green]✓[/bold green] {get_text('TOOLS', 'embed_server_stopped', '嵌入模型服务器已停止')}"
                )
                return 0
            else:
                console.print(
                    f"[bold red]❌ {get_text('TOOLS', 'embed_server_stop_failed', '嵌入模型服务器停止失败')}: {result.error}[/bold red]"
                )
                return 1

        except Exception as e:
            console.print(
                f"[bold red]{get_text('TOOLS', 'error_stopping_server', '停止服务器时出错')}: {str(e)}[/bold red]"
            )
            logger.exception(
                get_text("TOOLS", "embed_server_stop_failed", "嵌入模型服务器停止失败")
            )
            return 1

    def check_embed_server_status(self) -> int:
        """检查嵌入模型服务器状态"""
        try:
            self._print_panel("checking_embed_server", "检查嵌入模型服务器状态")

            # 获取服务器状态
            status = check_server_status()

            if status.status == EmbeddingServerStatus.RUNNING:
                console.print(
                    f"[bold green]✓[/bold green] {get_text('TOOLS', 'embed_server_running', '嵌入模型服务器正在运行')}"
                )
                console.print(f"PID: {status.pid}")
                console.print(f"URL: {status.url}")
                if status.uptime:
                    console.print(
                        f"{get_text('TOOLS', 'embed_server_uptime', '运行时间')}: {status.uptime}"
                    )
                return 0
            elif status.status == EmbeddingServerStatus.STOPPED:
                console.print(
                    f"[bold yellow]{get_text('TOOLS', 'embed_server_not_running', '嵌入模型服务器未运行')}[/bold yellow]"
                )
                return 0
            else:
                console.print(
                    f"[bold red]{get_text('TOOLS', 'embed_server_status_unknown', '嵌入模型服务器状态未知')}[/bold red]"
                )
                return 1

        except Exception as e:
            console.print(
                f"[bold red]{get_text('TOOLS', 'error_checking_server', '检查服务器状态时出错')}: {str(e)}[/bold red]"
            )
            logger.exception(
                get_text(
                    "TOOLS",
                    "embed_server_status_check_failed",
                    "嵌入模型服务器状态检查失败",
                )
            )
            return 1
