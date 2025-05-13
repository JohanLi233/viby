from pocketflow import Node
from viby.locale import get_text
from viby.mcp import list_tools
from viby.viby_tool_search.utils import get_mcp_tools_from_cache
from viby.config import Config
from viby.tools import AVAILABLE_TOOLS
import platform
import os


class PromptNode(Node):
    def exec(self, server_name):
        """Retrieve tools from the MCP server"""
        result = {"tools": []}

        # 获取配置
        config = Config()

        # 准备viby内置工具
        viby_tools = []
        for tool_name, tool_def in AVAILABLE_TOOLS.items():
            if callable(tool_def["description"]):
                tool_def["description"] = tool_def["description"]()

            for _, param_def in tool_def["parameters"]["properties"].items():
                if callable(param_def["description"]):
                    param_def["description"] = param_def["description"]()

            # 检查是否是搜索工具，如果工具搜索功能被禁用，则不添加搜索工具
            if tool_name == "search_relevant_tools" and not config.enable_tool_search:
                continue

            viby_tools.append({"server_name": "viby", "tool": tool_def})

        # 初始化结果，先只包含viby工具
        all_tools = viby_tools
        tool_servers = {tool["tool"]["name"]: "viby" for tool in viby_tools}

        # 如果启用了MCP，处理MCP工具
        if not config.enable_mcp:
            result["tools"] = all_tools
            result["tool_servers"] = tool_servers
            return result

        try:
            # 根据工具搜索功能状态选择不同的工具获取方式
            if config.enable_tool_search:
                # 如果启用了工具搜索，从缓存中获取工具
                tools_dict = get_mcp_tools_from_cache()
            else:
                # 如果禁用了工具搜索，直接使用list_tools获取工具
                tools_dict = list_tools(server_name)

            # 将所有MCP工具对应的服务器名称添加到tool_servers字典
            for srv_name, tools in tools_dict.items():
                for tool in tools:
                    tool_name = tool.name if hasattr(tool, "name") else tool.get("name")
                    if tool_name:
                        tool_servers[tool_name] = srv_name

            # 如果禁用了工具搜索，将MCP工具添加到all_tools列表
            if not config.enable_tool_search:
                for srv_name, tools in tools_dict.items():
                    for tool in tools:
                        all_tools.append({"server_name": srv_name, "tool": tool})

            result["tools"] = all_tools
            result["tool_servers"] = tool_servers
            return result
        except Exception as e:
            print(get_text("MCP", "tools_error", e))
            return result

    def post(self, shared, prep_res, exec_res):
        """Store tools and process to decision node"""
        shared["tools"] = exec_res["tools"]
        shared["tool_servers"] = exec_res.get(
            "tool_servers", {}
        )  # 保存工具到服务器的映射
        user_input = shared.get("user_input", "")

        tools_info = [tool_wrapper.get("tool") for tool_wrapper in shared["tools"]]

        # 获取系统和shell信息
        os_info = platform.system() + " " + platform.release()
        shell_info = os.environ.get("SHELL", "Unknown")

        # 获取系统提示并格式化工具信息和系统信息
        system_prompt = get_text("AGENT", "system_prompt").format(
            tools_info=tools_info, os_info=os_info, shell_info=shell_info
        )

        # 使用格式化后的系统提示构建消息
        shared["messages"] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]

        return "call_llm"
