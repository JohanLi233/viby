from typing import Dict, List
from viby.viby_tool_search.embedding_manager import EmbeddingManager, Tool
from viby.locale import get_text
from viby.config import config
import logging

logger = logging.getLogger(__name__)


def get_mcp_tools_from_cache() -> Dict[str, List]:
    """
    获取所有工具信息用于列表显示，优先从缓存中读取

    直接返回与list_tools()相同格式的按服务器分组的工具列表

    Returns:
        Dict[str, List]: 按服务器名称分组的工具列表，格式为 {server_name: [Tool对象, ...], ...}
    """
    if not config.enable_mcp:
        print(get_text("TOOLS", "mcp_not_enabled"))
        return {}

    # 初始化服务器分组的工具字典
    server_grouped_tools = {}

    # 首先尝试从缓存中读取
    try:
        # 创建embedding管理器实例以访问缓存
        manager = EmbeddingManager()

        # 检查是否有缓存的工具信息
        if not manager.tool_info:
            message = (
                get_text("TOOLS", "no_cached_tools")
                + "\n"
                + get_text("TOOLS", "suggest_update_embeddings")
            )
            print(message)
            return {}

        # 将工具转换为按服务器名称分组的格式
        for tool_name, tool_info in manager.tool_info.items():
            definition = tool_info.get("definition", {})
            server_name = definition.get("server_name", "unknown")

            # 创建Tool对象
            tool = Tool(
                name=tool_name,
                description=definition.get("description", ""),
                inputSchema=definition.get("parameters", {}),
                annotations=None,
            )

            # 添加到对应的服务器分组
            if server_name not in server_grouped_tools:
                server_grouped_tools[server_name] = []

            server_grouped_tools[server_name].append(tool)

    except Exception as e:
        # 如果无法读取缓存，返回错误信息
        logger.warning(
            f"{get_text('TOOLS', 'cache_read_failed', '从缓存读取工具信息失败')}: {e}"
        )

    return server_grouped_tools
