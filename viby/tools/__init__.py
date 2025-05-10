"""
Viby内置工具集

此模块提供了Viby的内置工具定义，遵循FastMCP工具标准
"""

from viby.tools.shell_tool import SHELL_TOOL

# 工具规范:
# {
#     "name": "工具名称",
#     "description": "工具描述" 或 lambda函数返回描述,
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "参数名": {
#                 "type": "参数类型(string/integer/boolean/etc)",
#                 "description": "参数描述" 或 lambda函数返回描述
#             },
#             ...更多参数...
#         },
#         "required": ["必需参数名列表"]
#     }
# }

# 收集所有可用工具
AVAILABLE_TOOLS = {
    "execute_shell": SHELL_TOOL
    # 这里可以添加更多工具
}
