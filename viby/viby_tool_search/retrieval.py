"""
MCP工具检索工具

基于embedding的MCP工具智能检索系统，根据用户查询返回最相关的MCP工具
"""

import logging
from typing import Dict, Any, List
from viby.viby_tool_search.server import is_server_running, search_tools_remote

logger = logging.getLogger(__name__)

def search_similar_tools(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    根据查询文本搜索相似的工具

    只使用远程嵌入服务器进行搜索，服务器不可用时返回空列表

    Args:
        query: 搜索查询文本
        top_k: 返回的最大结果数

    Returns:
        相关工具列表
    """
    # 只使用远程服务
    if is_server_running():
        logger.debug("使用远程嵌入服务器搜索工具")
        results = search_tools_remote(query, top_k)
        if not results:
            logger.warning("远程服务器返回空结果")
        return results
    else:
        logger.warning("嵌入服务器未运行，无法搜索工具")
        return [] 