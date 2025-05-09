from pocketflow import Node
from viby.locale import get_text
from viby.mcp import list_tools  # 仅使用 list_tools
from viby.config import Config
import os
import platform


class PromptNode(Node):
    def exec(self, server_name):
        """Retrieve tools from the MCP server"""
        result = {"tools": []}

        config = Config()
        if not config.enable_mcp:
            return result

        try:
            # 直接获取工具字典
            tools_dict = list_tools(server_name)

            # 保存工具和服务器名称的映射关系
            tool_servers = {}
            all_tools = []

            # 将工具和对应的服务器名称存储在字典中
            for srv_name, tools in tools_dict.items():
                for tool in tools:
                    all_tools.append({"server_name": srv_name, "tool": tool})
                    tool_servers[tool.name] = srv_name

            result["tools"] = all_tools
            result["tool_servers"] = tool_servers  # 添加工具名称到服务器的映射
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

        # 检查是否是 shell 命令模式
        if shared.get("command_type") == "shell":
            # 为 shell 命令构建特殊提示
            shell = os.environ.get("SHELL") or os.environ.get("COMSPEC") or "unknown"
            shell_name = os.path.basename(shell) if shell else "unknown"
            os_name = platform.system()
            shell_prompt = get_text(
                "SHELL", "command_prompt", user_input, shell_name, os_name
            )
            system_prompt = get_text("AGENT", "system_prompt").format(
                tools_info=tools_info
            )

            # 构建 shell 命令的消息
            shared["messages"] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": shell_prompt},
            ]
        else:
            # 获取系统提示并格式化工具信息
            system_prompt = get_text("AGENT", "system_prompt").format(
                tools_info=tools_info
            )

            # 使用格式化后的系统提示构建消息
            shared["messages"] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ]

        return "call_llm"
