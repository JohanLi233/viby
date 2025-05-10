from pocketflow import Node
from viby.locale import get_text
from viby.mcp import list_tools
from viby.config import Config
from viby.tools import AVAILABLE_TOOLS
import platform
import os


class PromptNode(Node):
    def exec(self, server_name):
        """Retrieve tools from the MCP server"""
        result = {"tools": []}

        viby_tools = []
        for _, tool_def in AVAILABLE_TOOLS.items():
            if callable(tool_def["description"]):
                tool_def["description"] = tool_def["description"]()

            for _, param_def in tool_def["parameters"]["properties"].items():
                if callable(param_def["description"]):
                    param_def["description"] = param_def["description"]()

            viby_tools.append({"server_name": "viby", "tool": tool_def})

        # 初始化结果，先只包含viby工具
        all_tools = viby_tools
        tool_servers = {tool["tool"]["name"]: "viby" for tool in viby_tools}

        # 如果启用了MCP，添加MCP工具
        config = Config()
        if not config.enable_mcp:
            result["tools"] = all_tools
            result["tool_servers"] = tool_servers
            return result

        try:
            # 直接获取工具字典
            tools_dict = list_tools(server_name)

            # 将MCP工具和对应的服务器名称添加到列表中
            for srv_name, tools in tools_dict.items():
                for tool in tools:
                    all_tools.append({"server_name": srv_name, "tool": tool})
                    tool_servers[tool.name] = srv_name

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
