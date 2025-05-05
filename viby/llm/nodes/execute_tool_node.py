from pocketflow import Node
from viby.mcp import call_tool
from viby.locale import get_text

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
        try:
            result = call_tool(tool_name, selected_server, parameters)
            return result
        except Exception as e:
            print(get_text("MCP", "execution_error", e))
            return get_text("MCP", "error_message", e)

    def post(self, shared, prep_res, exec_res):
        """Process the final result"""
        print(get_text("MCP", "result", exec_res))
        shared["response"] = exec_res
        
        # Add the tool result as an assistant message
        shared["messages"].append({"role": "assistant", "content": str(exec_res)})
        
        # Add a follow-up prompt asking the LLM to interpret the tool result
        result_prompt = get_text("MCP", "tool_result_prompt", exec_res)
        shared["messages"].append({"role": "user", "content": result_prompt})

        return "call_llm"