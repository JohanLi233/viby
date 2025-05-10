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
        # 使用标准Markdown格式打印结果
        title = get_text("MCP", "tool_result")

        # 处理可能的TextContent对象
        try:
            # 尝试将结果转为字符串
            if hasattr(exec_res, "__str__"):
                result_content = str(exec_res)
            else:
                result_content = exec_res
            print_markdown(result_content, title)
        except Exception as e:
            # 如果序列化失败，防止崩溃
            print(f"{get_text('MCP', 'execution_error', str(e))}")
            print_markdown(str(exec_res), title)

        # 保存响应到共享状态
        shared["response"] = exec_res

        shared["messages"].append({"role": "tool", "content": result_content})

        return "call_llm"
