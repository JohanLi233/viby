"""
MCP工具检索工具

基于embedding的MCP工具智能检索系统，根据用户查询返回最相关的MCP工具
"""

import logging
from typing import Dict, Any

from viby.locale import get_text
from viby.viby_tool_search.client import search_similar_tools

logger = logging.getLogger(__name__)

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
        return search_similar_tools(query, top_k)
    except Exception as e:
        logger.error(
            get_text("MCP", "tool_search_failed", "工具检索失败: %s"), e, exc_info=True
        )
        return {
            "error": get_text("MCP", "tool_search_error", "工具检索失败: {0}").format(
                str(e)
            )
        }
