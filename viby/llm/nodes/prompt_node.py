from pocketflow import Node
from viby.locale import get_text
from viby.mcp import list_tools
from viby.viby_tool_search.utils import get_mcp_tools_from_cache
from viby.config import Config
from viby.tools import AVAILABLE_TOOLS
import platform
import os


class PromptNode(Node):
    """
    准备系统提示和工具的节点
    从MCP服务器获取工具，准备系统提示并初始化消息历史
    """

    def prep(self, shared):
        """准备节点执行所需的参数"""
        # 获取用户输入以供执行时使用
        user_input = shared.get("user_input", "")

        # 获取MCP服务器名称，默认为"default"
        server_name = shared.get("mcp_server", "default")

        return user_input, server_name, Config()

    def exec(self, inputs):
        """获取工具列表并准备系统提示"""
        user_input, server_name, config = inputs

        # 准备结果结构
        result = {"tools": [], "tool_servers": {}, "user_input": user_input}

        # 准备viby内置工具
        viby_tools = self._prepare_viby_tools(config)

        # 初始化结果，先只包含viby工具
        all_tools = viby_tools
        tool_servers = {tool["tool"]["name"]: "viby" for tool in viby_tools}

        # 如果启用了MCP，处理MCP工具
        if config.enable_mcp:
            all_tools, tool_servers = self._fetch_mcp_tools(
                config, all_tools, tool_servers, server_name
            )

        result["tools"] = all_tools
        result["tool_servers"] = tool_servers

        # 获取系统和shell信息用于系统提示
        result["os_info"] = platform.system() + " " + platform.release()
        result["shell_info"] = os.environ.get("SHELL", "Unknown")

        return result

    def _prepare_viby_tools(self, config):
        """准备Viby内置工具列表"""
        viby_tools = []

        for tool_name, tool_def in AVAILABLE_TOOLS.items():
            # 处理可调用的描述
            if callable(tool_def["description"]):
                tool_def["description"] = tool_def["description"]()

            # 处理可调用的参数描述
            for _, param_def in tool_def["parameters"]["properties"].items():
                if callable(param_def["description"]):
                    param_def["description"] = param_def["description"]()

            # 如果工具搜索功能被禁用，跳过搜索工具
            if tool_name == "search_relevant_tools" and not config.enable_tool_search:
                continue

            viby_tools.append({"server_name": "viby", "tool": tool_def})

        return viby_tools

    def _fetch_mcp_tools(self, config, all_tools, tool_servers, server_name):
        """获取MCP工具列表"""
        try:
            # 根据工具搜索功能状态选择不同的工具获取方式
            if config.enable_tool_search:
                # 从缓存中获取工具
                tools_dict = get_mcp_tools_from_cache()
            else:
                # 直接使用list_tools获取工具
                tools_dict = list_tools(server_name)

            # 更新工具服务器映射
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

            return all_tools, tool_servers

        except Exception as e:
            print(get_text("MCP", "tools_error", e))
            return all_tools, tool_servers

    def post(self, shared, prep_res, exec_res):
        """存储工具和初始化消息历史"""
        # 保存获取到的工具信息
        shared["tools"] = exec_res["tools"]
        shared["tool_servers"] = exec_res["tool_servers"]

        # 获取用户输入
        user_input = exec_res["user_input"]

        # 为系统提示准备工具信息
        tools_info = [tool_wrapper.get("tool") for tool_wrapper in shared["tools"]]

        # 获取系统提示并格式化工具信息和系统信息
        system_prompt = get_text("AGENT", "system_prompt").format(
            tools_info=tools_info,
            os_info=exec_res["os_info"],
            shell_info=exec_res["shell_info"],
        )

        # 初始化消息历史
        shared["messages"] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]

        return "call_llm"

    def exec_fallback(self, prep_res, exc):
        """处理执行过程中的错误"""
        user_input = (
            prep_res[0] if isinstance(prep_res, tuple) and len(prep_res) > 0 else ""
        )

        # 准备最小化的结果，包含默认值
        return {
            "tools": [],
            "tool_servers": {},
            "user_input": user_input,
            "os_info": platform.system(),
            "shell_info": "Unknown",
        }
