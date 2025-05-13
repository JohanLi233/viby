"""
Viby 工具模块

注册和管理各种工具，包括CLI工具、LLM工具、Web工具等
"""

# 导入工具模块
from viby.tools.shell_tool import SHELL_TOOL, execute_shell
from viby.tools.tool_retrieval import (
    TOOL_RETRIEVAL_TOOL,
    execute_tool_retrieval,
)

# 注册工具处理函数
TOOL_EXECUTORS = {
    "execute_shell": execute_shell,
    "search_relevant_tools": execute_tool_retrieval,
}

# 所有可用的MCP工具定义
AVAILABLE_TOOLS = {
    "execute_shell": SHELL_TOOL,
    "search_relevant_tools": TOOL_RETRIEVAL_TOOL,
}

# 导出所有公共接口
__all__ = [
    "SHELL_TOOL",
    "execute_shell",
    "TOOL_RETRIEVAL_TOOL",
    "execute_tool_retrieval",
    "TOOL_EXECUTORS",
    "AVAILABLE_TOOLS",
]
