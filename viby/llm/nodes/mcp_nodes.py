"""
MCP (Model Context Protocol) 节点 - 提供工具调用功能
"""
import yaml
from pocketflow import Node
from viby.utils.mcp import get_tools, call_tool
from viby.utils.formatting import stream_render_response
from viby.locale import get_text

class GetToolsNode(Node):
    def prep(self, shared):
        """Initialize and get tools"""
        # The question is now passed from main via shared
        print(get_text("MCP", "getting_tools"))
        mcp_server = shared.get("mcp_server") # 从shared获取服务器名称，可为None默认
        return mcp_server

    def exec(self, server_name):
        """Retrieve tools from the MCP server"""
        try:
            tools = get_tools(server_name)
            return tools
        except Exception as e:
            print(get_text("MCP", "tools_error", e))
            return []

    def post(self, shared, prep_res, exec_res):
        """Store tools and process to decision node"""
        tools = exec_res
        shared["tools"] = tools
        
        return "decide"

class DecideToolNode(Node):
    def prep(self, shared):
        """Prepare the prompt for LLM to process the question"""
        tools = shared.get("tools")
        question = shared.get("user_input")
        model_manager = shared.get("model_manager")
        
        prompt = get_text("MCP", "tool_prompt", tools, question)
        messages = [
            {"role": "system", "content": get_text("MCP", "system_prompt")},
            {"role": "user", "content": prompt}
        ]
        
        return {
            "messages": messages,
            "model_manager": model_manager
        }

    def exec(self, prep_res):
        """Call LLM to process the question and decide which tool to use"""
        print(get_text("MCP", "analyzing"))
        manager = prep_res.get("model_manager")
        messages = prep_res.get("messages")
        
        if not manager or not messages:
            return None
            
        response = stream_render_response(manager, messages)
        return response

    def post(self, shared, prep_res, exec_res):
        """Extract decision from YAML and save to shared context"""
        try:
            yaml_str = exec_res.split("```yaml")[1].split("```")[0].strip()
            decision = yaml.safe_load(yaml_str)
            
            shared["tool_name"] = decision["tool"]
            shared["parameters"] = decision["parameters"]
            shared["thinking"] = decision.get("thinking", "")
            
            print(get_text("MCP", "selected_tool", decision['tool']))
            print(get_text("MCP", "extracted_params", decision['parameters']))
            
            return "execute"
        except Exception as e:
            print(get_text("MCP", "parsing_error", e))
            print("Raw response:", exec_res)
            return None

class ExecuteToolNode(Node):
    def prep(self, shared):
        """Prepare tool execution parameters"""
        server_name = shared.get("mcp_server")  # 可为None，使用默认服务器
        return shared["tool_name"], shared["parameters"], server_name

    def exec(self, inputs):
        """Execute the chosen tool"""
        tool_name, parameters, server_name = inputs
        print(get_text("MCP", "executing_tool", tool_name, parameters))
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
        shared["messages"].append({"role": "assistant", "content": str(exec_res)})
        return "done"
