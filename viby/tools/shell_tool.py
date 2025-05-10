"""
Shell命令执行工具定义
"""

from viby.locale import get_text

# Shell工具定义 - 符合FastMCP标准
SHELL_TOOL = {
    "name": "execute_shell",
    "description": lambda: get_text("MCP", "shell_tool_description"),
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": lambda: get_text("MCP", "shell_tool_param_command"),
            }
        },
        "required": ["command"],
    },
}
