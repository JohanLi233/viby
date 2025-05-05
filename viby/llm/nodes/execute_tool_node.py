from pocketflow import Node
from viby.mcp import call_tool
from viby.locale import get_text
from viby.utils.formatting import print_markdown

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
            "parameters": parameters
        }
        # 使用本地化文本
        title = get_text("MCP", "executing_tool")
        print_markdown(tool_call_info, title, "json")
        
        try:
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
            print(f"\n{get_text('MCP', 'execution_error', str(e))}")
            print_markdown(str(exec_res), title)
        
        # 保存响应到共享状态
        shared["response"] = exec_res
        
        # 将工具结果添加为助手消息
        shared["messages"].append({"role": "assistant", "content": str(exec_res)})
        
        # Add a follow-up prompt asking the LLM to interpret the tool result
        result_prompt = get_text("MCP", "tool_result_prompt", exec_res)
        shared["messages"].append({"role": "user", "content": result_prompt})

        return "call_llm"