from pocketflow import Node
from viby.mcp import call_tool
from viby.locale import get_text
from viby.utils.formatting import print_markdown
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
        tool_call_info = {
            "tool": tool_name,
            "server": selected_server,
            "parameters": parameters,
        }
        print_markdown(get_text("MCP", "executing_tool"))
        print_markdown(tool_call_info)

        try:
            # 使用合适的方式执行工具
            if selected_server == "viby":
                return self._execute_viby_tool(tool_name, parameters)
            else:
                # 使用MCP工具调用
                return call_tool(tool_name, selected_server, parameters)
        except Exception as e:
            print(get_text("MCP", "execution_error", e))
            return {"status": "error", "message": get_text("MCP", "error_message", e)}

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
        error_message = str(exc)
        print(get_text("MCP", "execution_error", error_message))
        return {"status": "error", "message": error_message}

    def post(self, shared, prep_res, exec_res):
        """处理工具执行结果"""
        # 如果准备阶段失败，返回下一个节点为错误处理
        if prep_res is None:
            shared["messages"].append(
                {"role": "tool", "tool_call_id": "0", "content": str(exec_res)}
            )
            print_markdown(str(exec_res))
            return "call_llm"

        tool_name = prep_res["tool_name"]
        selected_server = prep_res["selected_server"]

        # 将工具执行结果添加到消息历史
        shared["messages"].append(
            {"role": "tool", "tool_call_id": "0", "content": str(exec_res)}
        )

        # 打印工具执行结果，但跳过shell命令结果（shell结果已经在终端中显示了）
        if not (selected_server == "viby" and tool_name == "execute_shell"):
            print_markdown(str(exec_res))

        # 检查是否是shell命令的特殊状态
        if isinstance(exec_res, dict) and "status" in exec_res:
            if exec_res["status"] in ["completed"]:
                return "completed"

        return "call_llm"
