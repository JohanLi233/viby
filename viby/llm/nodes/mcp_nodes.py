"""
MCP (Model Context Protocol) 节点 - 提供工具调用功能
"""
from pocketflow import Node
from viby.utils.mcp import call_tool, get_tools, list_servers
from viby.locale import get_text

class GetToolsNode(Node):
    def prep(self, shared):
        """Initialize and get tools"""
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
        
        formatted_tools = ""
        for server, tools in server_tools.items():
            tool_descriptions = "\n".join([f"- {t.name}: {t.description}" for t in tools])
            formatted_tools += get_text("MCP", "format_server_tools", server, tool_descriptions)
        
        system_prompt = get_text("MCP", "system_prompt")
        user_prompt = get_text("MCP", "tool_prompt", formatted_tools, shared.get("user_input", ""))
        
        shared["messages"] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return "decide"

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
        shared["messages"].append({"role": "assistant", "content": str(exec_res)})
        return "done"
