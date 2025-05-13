"""
MCP工具检索工具

基于embedding的MCP工具智能检索系统，根据用户查询返回最相关的MCP工具
"""

import logging
from typing import Dict, Any, Optional, List

from viby.locale import get_text
from viby.viby_tool_search.manager import ToolEmbeddingManager
from viby.viby_tool_search.server import is_server_running, search_tools_remote

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


# 保持向后兼容的别名
search_tools = search_similar_tools


def get_mcp_tool_matches(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    搜索匹配查询的MCP工具

    Args:
        query: a查询文本
        top_k: 返回结果的最大数量

    Returns:
        匹配的工具列表
    """
    try:
        # 检查嵌入服务器是否运行
        if not is_server_running():
            logger.warning(
                get_text(
                    "MCP",
                    "embed_server_not_running",
                    "嵌入模型服务器未运行，无法搜索工具",
                )
            )
            return []

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
    # 检查嵌入服务器是否正在运行
    try:
        from viby.viby_tool_search.server import is_server_running, DEFAULT_PORT

        if is_server_running():
            import requests

            logger.info("检测到嵌入服务器运行中，尝试更新嵌入向量")
            try:
                response = requests.post(
                    f"http://localhost:{DEFAULT_PORT}/update",
                    json={},
                    timeout=60,  # 更新可能需要较长时间
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"远程更新失败，状态码: {response.status_code}")
                    return {
                        "success": False,
                        "message": get_text(
                            "MCP",
                            "embeddings_update_via_server_failed",
                            "通过服务器更新嵌入向量失败",
                        ),
                        "status_code": response.status_code,
                    }
            except Exception as e:
                logger.warning(f"远程更新请求失败: {e}")
                return {
                    "success": False,
                    "message": get_text(
                        "MCP",
                        "embeddings_update_via_server_failed",
                        "通过服务器更新嵌入向量失败",
                    ),
                    "error": str(e),
                }
        else:
            # 服务器未运行
            return {
                "success": False,
                "message": get_text(
                    "MCP", "embed_server_not_running", "嵌入模型服务器未运行"
                ),
                "suggestion": get_text(
                    "MCP",
                    "start_server_suggestion",
                    "请使用 'yb tools embed start' 命令启动嵌入服务器，然后再试",
                ),
            }
    except ImportError:
        logger.error("无法导入嵌入服务器模块")
        return {
            "success": False,
            "message": "无法访问嵌入服务器模块",
        }
    except Exception as e:
        logger.error(f"检查远程嵌入服务器状态失败: {e}")
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


def get_tools_for_listing():
    """
    获取所有工具信息用于列表显示，优先从缓存中读取

    Returns:
        dict: 包含工具信息的字典，格式为 {tool_name: tool_definition}
        str: 消息（成功、警告或建议）
        bool: 是否成功获取工具信息
    """
    from viby.config import Config
    
    config = Config()
    if not config.enable_mcp:
        return {}, get_text("TOOLS", "mcp_not_enabled"), False
    
    tools_dict = {}
    message = ""
    success = True
    
    # 首先尝试从缓存中读取
    try:
        # 创建embedding管理器实例以访问缓存
        manager = ToolEmbeddingManager()
        
        # 检查是否有缓存的工具信息
        if not manager.tool_info:
            message = get_text("TOOLS", "no_cached_tools") + "\n" + get_text("TOOLS", "suggest_update_embeddings")
            return {}, message, False
        
        # 使用缓存的工具信息
        for name, info in manager.tool_info.items():
            tools_dict[name] = info.get("definition", {})
        
        # 如果成功获取工具信息
        tool_count = len(manager.tool_info)
        message = get_text("TOOLS", "tools_loaded_from_cache", "工具信息已从缓存加载") + f" ({tool_count}个)"
        success = True
    except Exception as e:
        # 如果无法读取缓存，返回错误信息
        logger.warning(f"从缓存读取工具信息失败: {e}")
        message = get_text("TOOLS", "cache_read_failed") + "\n" + get_text("TOOLS", "suggest_update_embeddings")
        success = False
    
    return tools_dict, message, success 