"""
工具管理命令

提供与viby工具相关的CLI命令
"""

import logging
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from viby.locale import get_text
from viby.config import Config
from viby.tools.tool_retrieval import get_embedding_manager, collect_mcp_tools

logger = logging.getLogger(__name__)
console = Console()


class ToolsCommand:
    """
    工具管理命令类，提供工具嵌入向量更新和列出工具信息功能
    支持以下子命令:
    - embed - 更新工具嵌入向量
    - list - 列出所有可用的MCP工具
    """

    def __init__(self):
        """初始化工具命令"""
        self.config = Config()

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
            return self.update_embeddings()
        elif subcommand == "list":
            return self.list_tools()
        else:
            console.print(
                f"[bold red]{get_text('COMMANDS', 'unknown_subcommand').format(subcommand)}[/bold red]"
            )
            return 1

    def update_embeddings(self) -> int:
        """更新MCP工具的嵌入向量"""
        try:
            # 直接更新嵌入
            console.print(
                Panel.fit(
                    get_text("TOOLS", "updating_embeddings"),
                    title=get_text("TOOLS", "embeddings_update_title"),
                )
            )

            # 检查MCP是否启用
            if not self.config.enable_mcp:
                console.print(
                    f"[bold red]{get_text('TOOLS', 'mcp_not_enabled')}[/bold red]"
                )
                return 1

            # 收集MCP工具（公用函数）
            console.print(f"{get_text('TOOLS', 'collecting_tools')}...")
            tools_dict = collect_mcp_tools()

            tool_count = len(tools_dict)
            if tool_count == 0:
                console.print(f"[bold yellow]{get_text('TOOLS', 'no_tools_found')}[/bold yellow]")
                return 0

            console.print(
                get_text('TOOLS', 'start_updating_embeddings').format(tool_count=f"[bold cyan]{tool_count}[/bold cyan]")
            )

            # 获取嵌入管理器并更新
            manager = get_embedding_manager()

            console.print(
                f"[bold yellow]{get_text('TOOLS', 'loading_embedding_model')}[/bold yellow]"
            )
            # 先清空现有缓存，强制重新生成嵌入向量
            manager.tool_embeddings = {}
            console.print(
                f"[bold yellow]{get_text('TOOLS', 'clearing_cache')}[/bold yellow]"
            )
            updated = manager.update_tool_embeddings(tools_dict)

            if updated:
                console.print(f"[bold green]✓[/bold green] {get_text('TOOLS', 'embeddings_update_success')}")

                # 显示工具信息表格
                table = Table(title=get_text('TOOLS', 'updated_tools_table_title'))
                table.add_column(get_text('TOOLS', 'tool_name_column'), style="cyan")
                table.add_column(get_text('TOOLS', 'description_column'))

                for tool_name, tool in tools_dict.items():
                    description = tool.get("description", "")
                    if callable(description):
                        try:
                            description = description()
                        except Exception:
                            description = get_text('TOOLS', 'description_unavailable')
                    table.add_row(
                        tool_name,
                        description[:60] + ("..." if len(description) > 60 else ""),
                    )

                console.print(table)
            else:
                # 检查是否是因为模型问题导致的更新失败
                if manager.model is None and not manager.tool_embeddings:
                    # 没有缓存且模型为空，确实是模型加载失败
                    console.print(
                        f"[bold red]❌ {get_text('TOOLS', 'embedding_model_load_failed')}[/bold red]"
                    )
                else:
                    # 有缓存或模型不为空，不是模型加载失败，而是不需要更新
                    console.print(
                        f"[bold yellow]!{get_text('TOOLS', 'embeddings_already_updated')}[/bold yellow]"
                    )

            return 0

        except Exception as e:
            console.print(f"[bold red]{get_text('TOOLS', 'error_updating_embeddings')}: {str(e)}[/bold red]")
            logger.exception(get_text('TOOLS', 'embeddings_update_failed'))
            return 1

    def list_tools(self) -> int:
        """列出所有可用的MCP工具"""
        try:
            from viby.tools import AVAILABLE_TOOLS

            table = Table(title=get_text('TOOLS', 'available_tools_table_title'))
            table.add_column(get_text('TOOLS', 'tool_name_column'), style="cyan")
            table.add_column(get_text('TOOLS', 'description_column'))
            table.add_column(get_text('TOOLS', 'param_count_column'), justify="right")

            for name, tool in AVAILABLE_TOOLS.items():
                description = tool.get("description", "")
                if callable(description):
                    try:
                        description = description()
                    except Exception:
                        description = get_text('TOOLS', 'description_unavailable')

                # 使用标准的工具参数格式
                parameters = tool.get("parameters", {})
                param_count = len(parameters.get("properties", {}))

                table.add_row(
                    name,
                    description[:60] + ("..." if len(description) > 60 else ""),
                    str(param_count),
                )

            console.print(table)
            return 0

        except Exception as e:
            console.print(f"[bold red]{get_text('TOOLS', 'error_listing_tools')}: {str(e)}[/bold red]")
            logger.exception(get_text('TOOLS', 'tools_listing_failed'))
            return 1
