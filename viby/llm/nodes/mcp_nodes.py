"""
MCP (Model Context Protocol) 节点 - 提供工具调用功能
"""
import yaml
from pocketflow import Node
from viby.utils.mcp import call_tool, get_tools, list_servers
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
            if server_name:
                # 如果指定了服务器，只获取该服务器的工具
                tools = get_tools(server_name)
                return {server_name: tools}
            else:
                # 获取所有服务器的工具
                all_servers = list_servers()
                result = {}
                for server in all_servers:
                    try:
                        server_tools = get_tools(server)
                        result[server] = server_tools
                    except Exception as e:
                        print(get_text("MCP", "tools_error", e))
                return result
        except Exception as e:
            print(get_text("MCP", "tools_error", e))
            return {}

    def post(self, shared, prep_res, exec_res):
        """Store tools and process to decision node"""
        server_tools = exec_res
        shared["server_tools"] = server_tools
        
        # 格式化服务器和工具信息供模型使用
        formatted_tools = ""
        for server, tools in server_tools.items():
            tool_descriptions = "\n".join([f"- {t.name}: {t.description}" for t in tools])
            formatted_tools += get_text("MCP", "format_server_tools", server, tool_descriptions)
        
        shared["formatted_tools"] = formatted_tools
        return "decide"

class DecideToolNode(Node):
    def prep(self, shared):
        """Prepare the prompt for LLM to process the question"""
        formatted_tools = shared.get("formatted_tools", "")
        question = shared.get("user_input")
        model_manager = shared.get("model_manager")
        
        prompt = get_text("MCP", "tool_prompt", formatted_tools, question)
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
            
            # 提取工具名称和参数
            shared["tool_name"] = decision["tool"]
            shared["parameters"] = decision["parameters"]
            
            if "server" in decision:
                shared["selected_server"] = decision["server"]
                print(get_text("MCP", "selected_server", decision['server']))
            
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
        server_name = shared.get("selected_server")
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
