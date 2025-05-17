from pocketflow import Node
from viby.mcp import call_tool
from viby.locale import get_text
from viby.utils.ui import print_markdown
from viby.tools import AVAILABLE_TOOLS, TOOL_EXECUTORS


class ExecuteToolNode(Node):
    """
    执行指定工具的节点
    支持viby内置工具和MCP工具的执行
    """

    def prep(self, shared):
        """准备工具执行所需的参数"""
        # 从共享状态中获取必要的参数
        tool_name = shared.get("tool_name", "")
        parameters = shared.get("parameters", {})
        selected_server = shared.get("selected_server", "")

        # 验证必要的参数是否存在
        if not tool_name or not selected_server:
            return None

        return {
            "tool_name": tool_name,
            "parameters": parameters,
            "selected_server": selected_server,
        }

    def exec(self, tool_info):
        """执行指定的工具"""
        # 如果准备阶段返回None，表示参数缺失
        if tool_info is None:
            return {"status": "error", "message": get_text("MCP", "missing_params")}

        tool_name = tool_info["tool_name"]
        parameters = tool_info["parameters"]
        selected_server = tool_info["selected_server"]

        # 显示工具调用信息
        self._print_tool_call_info(tool_name, selected_server, parameters)

        try:
            # 使用合适的方式执行工具
            if selected_server == "viby":
                return self._execute_viby_tool(tool_name, parameters)
            else:
                # 使用MCP工具调用
                return call_tool(tool_name, selected_server, parameters)
        except Exception as e:
            return self._handle_execution_error(e)

    def _print_tool_call_info(self, tool_name, server, parameters):
        """打印工具调用信息"""
        tool_call_info = {
            "tool": tool_name,
            "server": server,
            "parameters": parameters,
        }
        print_markdown(get_text("MCP", "executing_tool"))
        print_markdown(tool_call_info)

    def _handle_execution_error(self, exception):
        """处理工具执行中的错误"""
        error_message = str(exception)
        print(get_text("MCP", "execution_error", error_message))
        return {
            "status": "error",
            "message": get_text("MCP", "error_message", exception),
        }

    def _execute_viby_tool(self, tool_name, parameters):
        """执行viby内置工具"""
        # 获取所有viby工具名称
        viby_tool_names = [tool_def["name"] for tool_def in AVAILABLE_TOOLS.values()]

        # 检查是否是viby工具
        if tool_name in viby_tool_names:
            if tool_name in TOOL_EXECUTORS:
                # 使用注册的执行函数处理工具
                executor = TOOL_EXECUTORS[tool_name]
                return executor(parameters)
            else:
                raise ValueError(f"未实现的Viby工具: {tool_name}")

        raise ValueError(f"未知的Viby工具: {tool_name}")

    def exec_fallback(self, tool_info, exc):
        """处理工具执行过程中的错误"""
        return self._handle_execution_error(exc)

    def post(self, shared, prep_res, exec_res):
        """处理工具执行结果"""
        tool_call_id = "0"  # 固定的工具调用ID
        tool_result = str(exec_res)

        # 将工具执行结果添加到消息历史
        shared["messages"].append(
            {"role": "tool", "tool_call_id": tool_call_id, "content": tool_result}
        )

        # 如果准备阶段失败，返回下一个节点为错误处理
        if prep_res is None:
            print_markdown(tool_result)
            return "call_llm"

        tool_name = prep_res["tool_name"]
        selected_server = prep_res["selected_server"]

        # 尝试更新历史交互记录
        self._update_interaction_history(shared, tool_name, tool_result)

        # 打印工具执行结果，但跳过shell命令结果（shell结果已经在终端中显示了）
        if not (selected_server == "viby" and tool_name == "execute_shell"):
            print_markdown(tool_result)

        # 检查是否是特殊状态
        if isinstance(exec_res, dict) and exec_res.get("status") == "completed":
            return "completed"

        return "call_llm"

    def _update_interaction_history(self, shared, tool_name, tool_result):
        """更新历史交互记录，记录工具执行结果"""
        if "model_manager" in shared and hasattr(
            shared["model_manager"], "update_last_interaction"
        ):
            # 工具调用结果的格式
            tool_call_record = f"`{tool_name}`\n{tool_result}"
            shared["model_manager"].update_last_interaction(tool_call_record)
