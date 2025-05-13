"""
MCP工具检索工具

基于embedding的MCP工具智能检索系统，根据用户查询返回最相关的MCP工具
"""

import logging
from typing import Dict, Any, Optional, List

from viby.locale import get_text
from viby.tools.embedding_utils import ToolEmbeddingManager
from viby.tools.embedding_server import is_server_running, search_tools_remote

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


def search_similar_tools(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    根据查询文本搜索相似的工具

    优先使用远程嵌入服务器进行搜索，如果服务器不可用，则回退到本地模式

    Args:
        query: 搜索查询文本
        top_k: 返回的最大结果数

    Returns:
        相关工具列表
    """
    # 首先尝试使用远程服务
    if is_server_running():
        logger.debug("使用远程嵌入服务器搜索工具")
        results = search_tools_remote(query, top_k)
        if results:
            return results
        logger.warning("远程服务器返回空结果，回退到本地模式")

    # 回退到本地模式
    logger.debug("使用本地嵌入模型搜索工具")
    embedding_manager = get_embedding_manager()
    return embedding_manager.search_similar_tools(query, top_k)


# 保持向后兼容的别名
search_tools = search_similar_tools


def get_mcp_tool_matches(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    搜索匹配查询的MCP工具

    Args:
        query: 查询文本
        top_k: 返回结果的最大数量

    Returns:
        匹配的工具列表
    """
    try:
        # 直接返回搜索结果，不添加额外包装
        return search_similar_tools(query, top_k)
    except Exception as e:
        logger.error(
            get_text("MCP", "tool_search_failed", "工具检索失败: %s"), e, exc_info=True
        )
        return []


def execute_update_embeddings(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    更新工具嵌入向量，由tools embed命令或其他流程显式调用
    """
    # 优先尝试更新远程服务器的嵌入向量
    try:
        from viby.tools.embedding_server import is_server_running

        if is_server_running():
            import requests
            from viby.tools.embedding_server import DEFAULT_PORT

            logger.info("检测到嵌入服务器运行中，尝试远程更新嵌入向量")
            try:
                response = requests.post(
                    f"http://localhost:{DEFAULT_PORT}/update",
                    json={},
                    timeout=60,  # 更新可能需要较长时间
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(
                        f"远程更新失败，状态码: {response.status_code}，回退到本地更新"
                    )
            except Exception as e:
                logger.warning(f"远程更新请求失败 ({e})，回退到本地更新")
    except ImportError:
        logger.debug("无法导入嵌入服务器模块，使用本地更新")
    except Exception as e:
        logger.warning(f"检查远程嵌入服务器状态失败 ({e})，回退到本地更新")

    # 回退到本地更新
    try:
        # 收集工具定义
        tools_dict = collect_mcp_tools()
        if not tools_dict:
            return {
                "success": False,
                "message": get_text(
                    "MCP",
                    "no_tools_or_mcp_disabled",
                    "没有可用的MCP工具或MCP功能未启用",
                ),
            }

        # 更新嵌入
        manager = get_embedding_manager()
        updated = manager.update_tool_embeddings(tools_dict)

        return {
            "success": updated,
            "message": get_text(
                "MCP", "embeddings_updated", "已成功更新MCP工具嵌入向量"
            )
            if updated
            else get_text(
                "MCP", "embeddings_up_to_date", "MCP工具嵌入向量已是最新，无需更新"
            ),
            "tool_count": len(tools_dict),
        }
    except Exception as e:
        logger.error(
            get_text("MCP", "update_embeddings_failed", "更新MCP工具嵌入向量失败: %s"),
            e,
            exc_info=True,
        )
        return {
            "success": False,
            "error": get_text("MCP", "update_error", "更新失败: {0}").format(str(e)),
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
