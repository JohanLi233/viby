"""
工具管理命令

提供与viby工具相关的CLI命令
"""

import logging
import textwrap
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from viby.locale import get_text
from viby.config import Config
from viby.viby_tool_search.commands import EmbedServerCommand
from viby.viby_tool_search.utils import get_mcp_tools_from_cache

logger = logging.getLogger(__name__)
console = Console()


class ToolsCommand:
    """
    工具管理命令类，提供工具嵌入向量更新和列出工具信息功能
    支持以下子命令:
    - embed - 嵌入向量管理，包含update、start、stop、status子命令
    - list - 列出所有可用的MCP工具
    """

    def __init__(self):
        """初始化工具命令"""
        self.config = Config()
        self.embed_server_command = EmbedServerCommand()

    def execute(self, subcommand: str, args: any) -> int:
        """
        执行工具命令

        Args:
            subcommand: 子命令名称（embed, list）
            args: 命令行参数

        Returns:
            命令退出码
        """
        if subcommand == "embed":
            # 处理embed子命令
            embed_subcommand = getattr(args, "embed_subcommand", None)

            # 如果没有子命令，默认为update（向后兼容）
            if embed_subcommand is None:
                return self.embed_server_command.update_embeddings()

            # 委托给嵌入服务器命令类处理
            return self.embed_server_command.execute(embed_subcommand, args)
        elif subcommand == "list":
            return self.list_tools()
        else:
            console.print(
                f"[bold red]{get_text('COMMANDS', 'unknown_subcommand').format(subcommand)}[/bold red]"
            )
            return 1

    def list_tools(self) -> int:
        """列出所有可用的MCP工具"""
        try:
            console.print(
                Panel.fit(
                    get_text("TOOLS", "listing_tools"),
                    title=get_text("TOOLS", "tools_list_title"),
                )
            )

            # 使用viby_tool_search模块获取工具信息
            try:
                # 获取工具信息 - 现在返回的是按服务器分组的工具列表
                server_tools_dict = get_mcp_tools_from_cache()

                # 如果没有工具，显示提示并返回成功
                if not server_tools_dict:
                    console.print(
                        f"[bold yellow]{get_text('TOOLS', 'no_tools_found')}[/bold yellow]"
                    )
                    return 0
            except Exception as e:
                console.print(
                    f"[bold red]{get_text('TOOLS', 'error_listing_tools')}: {str(e)}[/bold red]"
                )
                logger.exception(get_text("TOOLS", "tools_listing_failed"))
                return 1

            # 显示工具信息表格
            table = Table(title=get_text("TOOLS", "available_tools_table_title"))
            table.add_column(get_text("TOOLS", "tool_name_column"), style="cyan")
            table.add_column(get_text("TOOLS", "description_column"))
            table.add_column(get_text("TOOLS", "param_count_column"), justify="right")
            table.add_column(get_text("TOOLS", "server_column"), style="dim")

            # 创建展平的工具列表，以便按名称排序
            all_tools = []
            for server_name, tools in server_tools_dict.items():
                for tool in tools:
                    all_tools.append((tool.name, tool, server_name))

            # 按名称排序工具
            for name, tool, server_name in sorted(all_tools, key=lambda x: x[0]):
                description = tool.description if hasattr(tool, "description") else ""
                if callable(description):
                    try:
                        description = description()
                    except Exception:
                        description = get_text("TOOLS", "description_unavailable")

                # 获取参数数量
                parameters = tool.inputSchema if hasattr(tool, "inputSchema") else {}
                param_properties = (
                    parameters.get("properties", {})
                    if isinstance(parameters, dict)
                    else {}
                )
                param_count = len(param_properties)

                # 使用textwrap简化描述截断
                short_desc = textwrap.shorten(description, width=60, placeholder="...")

                table.add_row(
                    name,
                    short_desc,
                    str(param_count),
                    server_name,
                )

            console.print(table)

            # 显示总工具数量
            total_tools = sum(len(tools) for tools in server_tools_dict.values())
            console.print(
                f"\n{get_text('TOOLS', 'total_tools')}: [bold cyan]{total_tools}[/bold cyan]"
            )
            return 0

        except Exception as e:
            console.print(
                f"[bold red]{get_text('TOOLS', 'error_listing_tools')}: {str(e)}[/bold red]"
            )
            logger.exception(get_text("TOOLS", "tools_listing_failed"))
            return 1
