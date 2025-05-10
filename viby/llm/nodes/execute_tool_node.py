from pocketflow import Node
from viby.mcp import call_tool
from viby.locale import get_text
from viby.utils.formatting import print_markdown
from viby.llm.nodes.handlers import handle_shell_command
from viby.tools import AVAILABLE_TOOLS


class ExecuteToolNode(Node):
    def prep(self, shared):
        """Prepare tool execution parameters"""
        # 同时获取工具名称、参数和服务器名称
        tool_name = shared["tool_name"]
        parameters = shared["parameters"]
        selected_server = shared["selected_server"]
        return tool_name, parameters, selected_server

    def exec(self, inputs):
        """Execute the chosen tool"""
        tool_name, parameters, selected_server = inputs

        tool_call_info = {
            "tool": tool_name,
            "server": selected_server,
            "parameters": parameters,
        }
        # 使用本地化文本
        title = get_text("MCP", "executing_tool")
        print_markdown(tool_call_info, title, "json")

        try:
            # 检查是否是viby自有工具
            if selected_server == "viby":
                viby_tool_names = [
                    tool_def["name"] for tool_def in AVAILABLE_TOOLS.values()
                ]
                if tool_name in viby_tool_names:
                    if tool_name == "execute_shell":
                        command = parameters.get("command", "")
                        result = handle_shell_command(command)
                        return result
                    else:
                        raise ValueError(f"未实现的Viby工具: {tool_name}")

            # 否则使用标准MCP工具调用
            result = call_tool(tool_name, selected_server, parameters)
            return result
        except Exception as e:
            print(get_text("MCP", "execution_error", e))
            return get_text("MCP", "error_message", e)

    def post(self, shared, prep_res, exec_res):
        """Process the final result"""
        shared["messages"].append({"role": "tool", "content": str(exec_res)})

        # 检查是否是shell命令的特殊状态
        if isinstance(exec_res, dict) and "status" in exec_res:
            # 如果是复制到剪贴板(y)或取消操作(q)，不需要再调用LLM
            if exec_res["status"] in ["completed"]:
                return "completed"

        return "call_llm"
