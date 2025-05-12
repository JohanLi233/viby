"""
工具管理命令

提供与viby工具相关的CLI命令
"""

import logging
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from viby.utils.formatting import print_separator
from viby.locale import get_text
from viby.config import get_config
from viby.tools.tool_retrieval import get_embedding_manager

logger = logging.getLogger(__name__)
console = Console()

class ToolsCommand:
    """
    工具管理命令类，提供工具嵌入向量更新和列出工具信息功能
    支持以下子命令:
    - update-embeddings - 更新工具嵌入向量
    - list - 列出所有可用的MCP工具
    """
    
    def __init__(self):
        """初始化工具命令"""
        self.config = get_config()
    
    def execute(self, subcommand: str, args: any) -> int:
        """
        执行工具命令
        
        Args:
            subcommand: 子命令名称（update-embeddings, list）
            args: 命令行参数
            
        Returns:
            命令退出码
        """
        if subcommand == "update-embeddings":
            return self.update_embeddings()
        elif subcommand == "list":
            return self.list_tools()
        else:
            console.print(f"[bold red]未知子命令: {subcommand}[/bold red]")
            return 1
    
    def update_embeddings(self) -> int:
        """更新MCP工具的嵌入向量"""
        try:
            # 获取当前配置
            update_freq = self.config.embedding.update_frequency
            
            # 显示当前更新策略
            console.print(Panel.fit(
                f"当前嵌入更新策略: [bold cyan]{update_freq}[/bold cyan]", 
                title="嵌入配置"
            ))
            
            # 获取工具列表
            from viby.tools import AVAILABLE_TOOLS
            tool_count = len(AVAILABLE_TOOLS)
            
            console.print(f"开始更新 [bold cyan]{tool_count}[/bold cyan] 个工具的嵌入向量...")
            
            # 获取嵌入管理器并更新
            manager = get_embedding_manager()
            # 在手动模式下，我们总是强制更新
            force = (update_freq == "manual")
            updated = manager.update_tool_embeddings(AVAILABLE_TOOLS, force=force)
            
            if updated:
                console.print("[bold green]✓[/bold green] 工具嵌入向量更新成功！")
                
                # 显示工具信息表格
                table = Table(title="已更新工具")
                table.add_column("工具名称", style="cyan")
                table.add_column("描述")
                
                for name, tool in AVAILABLE_TOOLS.items():
                    description = tool.get("description", "")
                    if callable(description):
                        try:
                            description = description()
                        except Exception:
                            description = "[无法获取描述]"
                    table.add_row(name, description[:60] + ("..." if len(description) > 60 else ""))
                
                console.print(table)
            else:
                console.print("[bold yellow]!工具嵌入向量已是最新，无需更新[/bold yellow]")
                
            return 0
                
        except Exception as e:
            console.print(f"[bold red]更新工具嵌入向量时出错: {str(e)}[/bold red]")
            logger.exception("更新工具嵌入向量失败")
            return 1

    def list_tools(self) -> int:
        """列出所有可用的MCP工具"""
        try:
            from viby.tools import AVAILABLE_TOOLS
            
            table = Table(title="MCP可用工具")
            table.add_column("工具名称", style="cyan")
            table.add_column("描述")
            table.add_column("参数数量", justify="right")
            
            for name, tool in AVAILABLE_TOOLS.items():
                description = tool.get("description", "")
                if callable(description):
                    try:
                        description = description()
                    except Exception:
                        description = "[无法获取描述]"
                
                params = tool.get("parameters", {}).get("properties", {})
                param_count = len(params)
                
                table.add_row(
                    name, 
                    description[:60] + ("..." if len(description) > 60 else ""),
                    str(param_count)
                )
            
            console.print(table)
            return 0
            
        except Exception as e:
            console.print(f"[bold red]列出工具时出错: {str(e)}[/bold red]")
            logger.exception("列出工具失败")
            return 1