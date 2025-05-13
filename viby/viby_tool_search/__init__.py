"""
MCP工具检索与嵌入服务模块

提供高效的工具检索、嵌入向量生成和服务管理功能
"""

__version__ = "0.1.0"

# 导出公共API
from viby.viby_tool_search.server import (
    is_server_running,
    check_server_status,
    start_embedding_server,
    stop_embedding_server,
    search_tools_remote,
    update_tools_remote,
    EmbeddingServerStatus,
    ServerStatusResult,
    ServerOperationResult,
)
from viby.viby_tool_search.embedding_manager import EmbeddingManager
from viby.viby_tool_search.retrieval import (
    search_similar_tools,
    collect_mcp_tools,
    execute_update_embeddings,
    get_tools_for_listing,
) 