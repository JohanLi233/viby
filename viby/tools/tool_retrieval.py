"""
MCP工具检索工具

基于embedding的MCP工具智能检索系统，根据用户查询返回最相关的MCP工具
"""

import logging
from typing import Dict, Any, Optional, List

from viby.locale import get_text
from viby.tools.embedding_utils import ToolEmbeddingManager

logger = logging.getLogger(__name__)

# 全局唯一的embedding管理器实例
_embedding_manager: Optional[ToolEmbeddingManager] = None


def get_embedding_manager() -> ToolEmbeddingManager:
    """获取全局embedding管理器实例"""
    global _embedding_manager
    if _embedding_manager is None:
        _embedding_manager = ToolEmbeddingManager()
    return _embedding_manager


# 公共工具收集函数，避免各处重复实现


def collect_mcp_tools() -> Dict[str, Dict[str, Any]]:
    """收集启用状态下的所有 MCP 工具，返回标准格式的工具字典。"""
    from viby.config import Config
    from viby.mcp import list_tools as list_mcp_tools

    config = Config()
    if not config.enable_mcp:
        return {}

    tools: Dict[str, Dict[str, Any]] = {}
    try:
        mcp_tools_dict = list_mcp_tools()
        for server_name, tools_list in mcp_tools_dict.items():
            for tool in tools_list:
                tools[tool.name] = {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": getattr(tool, "inputSchema", {}),
                    "server_name": server_name,
                }
    except Exception as exc:
        logger.error(get_text("MCP", "tools_error").replace("{0}", str(exc)))
    return tools


def search_tools(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    根据查询搜索相关工具定义

    Args:
        query: 查询文本
        top_k: 最大返回结果数量

    Returns:
        匹配的工具定义列表，按相关性排序
    """
    manager = get_embedding_manager()

    # 检查是否有工具嵌入缓存
    if not manager.tool_embeddings:
        logger.warning(get_text("MCP", "no_embeddings_cache"))
        return []

    # 执行相似度搜索并直接返回相似工具信息
    return manager.search_similar_tools(query, top_k)


def execute_update_embeddings(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    更新工具嵌入向量，由tools embed命令或其他流程显式调用
    """
    try:
        # 收集工具定义
        tools_dict = collect_mcp_tools()
        if not tools_dict:
            return {
                "success": False, 
                "message": get_text("MCP", "no_tools_or_mcp_disabled", "没有可用的MCP工具或MCP功能未启用")
            }
        
        # 更新嵌入
        manager = get_embedding_manager()
        updated = manager.update_tool_embeddings(tools_dict)
        
        return {
            "success": updated,
            "message": get_text("MCP", "embeddings_updated", "已成功更新MCP工具嵌入向量") if updated else get_text("MCP", "embeddings_up_to_date", "MCP工具嵌入向量已是最新，无需更新"),
            "tool_count": len(tools_dict),
        }
    except Exception as e:
        logger.error(get_text("MCP", "update_embeddings_failed", "更新MCP工具嵌入向量失败: %s"), e, exc_info=True)
        return {
            "success": False, 
            "error": get_text("MCP", "update_error", "更新失败: {0}").format(str(e))
        }


# 工具检索工具定义 - 符合FastMCP标准
TOOL_RETRIEVAL_TOOL = {
    "name": "search_relevant_tools",
    "description": lambda: get_text("MCP", "tool_retrieval_description"),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": lambda: get_text("MCP", "tool_retrieval_param_query"),
            },
            "top_k": {
                "type": "integer",
                "description": lambda: get_text("MCP", "tool_retrieval_param_top_k"),
            },
        },
        "required": ["query"],
    },
}


# 工具检索处理函数
def execute_tool_retrieval(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行工具检索

    Args:
        params: 包含query和可选的top_k参数

    Returns:
        搜索结果 - 相似工具列表
    """
    query = params.get("query", "")
    top_k = params.get("top_k", 5)

    if not query:
        return {"error": get_text("MCP", "empty_query", "查询文本不能为空")}

    try:
        # 直接返回搜索结果，不添加额外包装
        return search_tools(query, top_k)
    except Exception as e:
        logger.error(get_text("MCP", "tool_search_failed", "工具检索失败: %s"), e, exc_info=True)
        return {"error": get_text("MCP", "tool_search_error", "工具检索失败: {0}").format(str(e))}
