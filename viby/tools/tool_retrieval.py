"""
MCP工具检索工具

基于embedding的MCP工具智能检索系统，根据用户查询返回最相关的MCP工具
"""

import logging
from typing import Dict, List, Any, Optional

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
        # 首次初始化时不在这里更新工具embeddings，避免循环导入
    return _embedding_manager

def search_tools(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    根据查询搜索相关工具
    
    Args:
        query: 查询文本
        top_k: 返回的最相关工具数量
    
    Returns:
        相关工具列表
    """
    # 获取embedding管理器
    manager = get_embedding_manager()
    
    # 导入这里以避免循环导入
    from viby.tools import AVAILABLE_TOOLS
    from viby.config import get_config
    
    # 检查更新策略
    config = get_config()
    update_frequency = config.embedding.update_frequency
    
    # 更新工具embeddings（确保工具列表是最新的）
    # 如果是手动模式，依然检查是否需要更新，但不强制更新
    force = False  # 这里不强制更新，在手动更新模式下由用户通过系统命令显式触发
    updated = manager.update_tool_embeddings(AVAILABLE_TOOLS, force=force)
    
    if updated:
        logger.info("已更新工具嵌入向量")
    elif update_frequency == "manual" and not manager.tool_embeddings:
        # 特殊情况：手动模式但没有嵌入缓存，进行初始化
        logger.info("手动更新模式下首次初始化嵌入向量")
        manager.update_tool_embeddings(AVAILABLE_TOOLS, force=True)
    
    # 搜索相关工具
    return manager.search_similar_tools(query, top_k)

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
            }
        },
        "required": ["query"],
    },
}

# 更新嵌入工具
UPDATE_EMBEDDINGS_TOOL = {
    "name": "update_tool_embeddings",
    "description": lambda: get_text("MCP", "update_tool_embeddings_description", "更新工具嵌入向量。在手动更新模式下使用此工具重新生成嵌入。"),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

def execute_update_embeddings(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    更新工具嵌入向量
    
    Args:
        params: 空参数
    
    Returns:
        更新结果
    """
    try:
        # 获取embedding管理器
        manager = get_embedding_manager()
        
        # 导入这里以避免循环导入
        from viby.tools import AVAILABLE_TOOLS
        
        # 从配置中获取更新策略
        from viby.config import get_config
        config = get_config()
        update_frequency = config.embedding.update_frequency
        
        # 更新工具embeddings（如果是手动模式，则强制更新）
        force = update_frequency == "manual"
        updated = manager.update_tool_embeddings(AVAILABLE_TOOLS, force=force)
        
        if updated:
            return {
                "success": True,
                "message": "已成功更新工具嵌入向量",
                "tool_count": len(AVAILABLE_TOOLS),
                "update_mode": "强制更新" if force else "检测到变化更新"
            }
        else:
            return {
                "success": False,
                "message": "工具嵌入向量已是最新，无需更新",
                "tool_count": len(AVAILABLE_TOOLS)
            }
    except Exception as e:
        logger.error(f"更新工具嵌入向量失败: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"更新失败: {str(e)}"
        }

# 工具检索处理函数
def execute_tool_retrieval(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行工具检索
    
    Args:
        params: 包含query和可选的top_k参数
    
    Returns:
        搜索结果
    """
    query = params.get("query", "")
    top_k = params.get("top_k", 5)
    
    if not query:
        return {
            "error": "查询文本不能为空"
        }
    
    try:
        # 搜索相关工具
        results = search_tools(query, top_k)
        
        # 从配置中获取更新策略信息
        from viby.config import get_config
        config = get_config()
        update_frequency = config.embedding.update_frequency
        
        # 格式化结果
        formatted_results = []
        for tool in results:
            name = tool["name"]
            score = tool["score"]
            definition = tool["definition"]
            
            # 获取描述文本
            description = definition.get("description", "")
            if callable(description):
                try:
                    description = description()
                except Exception as e:
                    logger.warning(f"获取工具 {name} 的描述时出错: {e}")
                    description = ""
            
            # 格式化工具信息
            formatted_tool = {
                "name": name,
                "score": round(score, 4),
                "description": description,
                "parameters": definition.get("parameters", {})
            }
            formatted_results.append(formatted_tool)
        
        response = {
            "tools": formatted_results,
            "query": query,
            "total": len(formatted_results),
            "update_frequency": update_frequency
        }
        
        # 如果是手动更新模式，添加提示信息
        if update_frequency == "manual":
            response["update_hint"] = "当前处于手动更新模式，需使用命令 'viby tools update-embeddings' 更新工具嵌入向量"
        
        return response
    except Exception as e:
        logger.error(f"工具检索失败: {e}", exc_info=True)
        return {
            "error": f"工具检索失败: {str(e)}"
        } 