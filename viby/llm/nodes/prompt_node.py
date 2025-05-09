from pocketflow import Node
from viby.locale import get_text
from viby.mcp import list_tools  # 仅使用 list_tools
from viby.config import Config
import os
import platform
import json


class PromptNode(Node):
    def prep(self, shared):
        self.config = Config()

    def exec(self, server_name):
        """Retrieve tools from the MCP server"""
        result = {"tools": []}

        if not self.config.enable_mcp:
            return result

        try:
            tools_dict = list_tools(server_name)

            all_tools = []
            for srv_name, tools in tools_dict.items():
                for tool in tools:
                    tool_dict = {"server_name": srv_name, "tool": tool}
                    all_tools.append(tool_dict)
            
            result["tools"] = all_tools
            return result
        except Exception as e:
            print(get_text("MCP", "tools_error", e))
            return result

    def post(self, shared, prep_res, exec_res):
        """Store tools and process to decision node"""
        shared["tools"] = exec_res["tools"]
        user_input = shared.get("user_input", "")

        tools_info = []
        for tool_wrapper in shared["tools"]:
            # 获取原始工具对象并直接添加到工具列表
            tool = tool_wrapper.get("tool")
            tools_info.append(tool)

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
