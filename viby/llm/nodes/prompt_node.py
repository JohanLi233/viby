from pocketflow import Node
from viby.locale import get_text
from viby.mcp import list_tools
from viby.viby_tool_search.utils import get_mcp_tools_from_cache
from viby.config import Config
from viby.tools import AVAILABLE_TOOLS
from viby.utils.history import SessionManager
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
        result = {
            "tools": [],
            "tool_servers": {},
            "user_input": user_input,
            "os_info": platform.system() + " " + platform.release(),
            "shell_info": os.environ.get("SHELL", "Unknown"),
            "current_dir": os.getcwd(),
        }

        # 获取Viby工具和MCP工具
        result["tools"], result["tool_servers"] = self._get_all_tools(
            server_name, config
        )

        return result

    def _get_all_tools(self, server_name, config):
        """获取所有可用工具（Viby工具和MCP工具）"""
        # 准备Viby内置工具
        viby_tools = self._prepare_viby_tools(config)
        tool_servers = {tool["tool"]["name"]: "viby" for tool in viby_tools}

        # 合并所有工具
        all_tools = viby_tools

        # 如果启用了MCP，添加MCP工具
        if config.enable_mcp:
            mcp_tools = self._fetch_mcp_tools(config, server_name)

            # 更新工具服务器映射
            for srv_name, tools in mcp_tools.items():
                for tool in tools:
                    tool_name = tool.name if hasattr(tool, "name") else tool.get("name")
                    if tool_name:
                        tool_servers[tool_name] = srv_name

            # 添加MCP工具到列表
            if not config.enable_tool_search:
                for srv_name, tools in mcp_tools.items():
                    for tool in tools:
                        all_tools.append({"server_name": srv_name, "tool": tool})

        return all_tools, tool_servers

    def _prepare_viby_tools(self, config):
        """准备Viby内置工具列表"""
        viby_tools = []

        for tool_name, tool_def in AVAILABLE_TOOLS.items():
            # 跳过禁用的工具搜索功能
            if tool_name == "search_relevant_tools" and not config.enable_tool_search:
                continue

            # 处理工具描述
            tool_def_copy = self._process_tool_descriptions(tool_def)
            viby_tools.append({"server_name": "viby", "tool": tool_def_copy})

        return viby_tools

    def _process_tool_descriptions(self, tool_def):
        """处理工具定义中的可调用描述"""
        # 创建副本，避免修改原始对象
        tool_def = tool_def.copy()

        # 处理可调用的描述
        if callable(tool_def["description"]):
            tool_def["description"] = tool_def["description"]()

        # 处理可调用的参数描述
        for param_name, param_def in tool_def["parameters"]["properties"].items():
            if callable(param_def["description"]):
                param_def["description"] = param_def["description"]()

        return tool_def

    def _fetch_mcp_tools(self, config, server_name):
        """获取MCP工具列表"""
        try:
            # 根据工具搜索功能状态选择不同的工具获取方式
            if config.enable_tool_search:
                return get_mcp_tools_from_cache()
            else:
                return list_tools(server_name)
        except Exception as e:
            print(get_text("MCP", "tools_error", e))
            return {}

    def _get_recent_history(self, max_rounds=5):
        """获取最近的对话历史"""
        try:
            # 初始化会话管理器
            session_manager = SessionManager()

            # 获取当前活跃会话的历史记录
            history = session_manager.get_history(limit=max_rounds)

            # 转换为消息格式
            messages = []
            for item in reversed(history):  # 从最旧的开始处理
                if item.get("content"):
                    messages.append({"role": "user", "content": item.get("content")})
                    if item.get("response"):
                        messages.append(
                            {"role": "assistant", "content": item.get("response")}
                        )

            # 限制轮次数量
            if len(messages) > max_rounds:
                messages = messages[-max_rounds:]

            return messages
        except Exception as e:
            print(f"获取历史对话失败: {e}")
            return []

    def _prepare_system_prompt(self, tools_info, system_info):
        """准备系统提示"""
        return get_text("AGENT", "system_prompt").format(
            tools_info=tools_info,
            os_info=system_info["os_info"],
            shell_info=system_info["shell_info"],
            current_dir=system_info["current_dir"],
        )

    def post(self, shared, prep_res, exec_res):
        """存储工具和初始化消息历史"""
        # 保存获取到的工具信息
        shared["tools"] = exec_res["tools"]
        shared["tool_servers"] = exec_res["tool_servers"]

        # 为系统提示准备工具信息
        tools_info = [tool_wrapper.get("tool") for tool_wrapper in shared["tools"]]

        # 获取系统提示
        system_prompt = self._prepare_system_prompt(
            tools_info,
            {
                "os_info": exec_res["os_info"],
                "shell_info": exec_res["shell_info"],
                "current_dir": exec_res["current_dir"],
            },
        )

        # 初始化消息历史，首先是系统提示
        messages = [{"role": "system", "content": system_prompt}]

        # 获取前三轮对话历史并添加到消息中
        previous_messages = self._get_recent_history(max_rounds=3)
        if previous_messages:
            messages.extend(previous_messages)

        # 添加当前用户输入
        messages.append({"role": "user", "content": exec_res["user_input"]})

        # 保存消息历史
        shared["messages"] = messages

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
            "current_dir": os.getcwd(),
        }
