from pocketflow import Node
from viby.utils.mcp import call_tool
from viby.locale import get_text

class ExecuteToolNode(Node):
    def prep(self, shared):
        """Prepare tool execution parameters"""
        server_name = shared.get("selected_server")
        return shared["tool_name"], shared["parameters"], server_name

    def exec(self, inputs):
        """Execute the chosen tool"""
        tool_name, parameters, server_name = inputs
        try:
            result = call_tool(server_name, tool_name, parameters)
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