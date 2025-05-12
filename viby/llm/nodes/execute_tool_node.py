from pocketflow import Node
from viby.mcp import call_tool
from viby.locale import get_text
from viby.utils.formatting import print_markdown
from viby.tools import AVAILABLE_TOOLS, TOOL_EXECUTORS


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
        print_markdown(get_text("MCP", "executing_tool"))
        print_markdown(tool_call_info)

        try:
            # 检查是否是viby自有工具
            if selected_server == "viby":
                viby_tool_names = [
                    tool_def["name"] for tool_def in AVAILABLE_TOOLS.values()
                ]
                if tool_name in viby_tool_names:
                    if tool_name in TOOL_EXECUTORS:
                        # 使用注册的执行函数处理工具
                        executor = TOOL_EXECUTORS[tool_name]
                        result = executor(parameters)
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
        tool_name, parameters, selected_server = prep_res
        shared["messages"].append({"role": "tool", "content": str(exec_res)})

        # 打印工具执行结果，但跳过shell命令结果（shell结果已经在终端中显示了）
        if not (selected_server == "viby" and tool_name == "execute_shell"):
            print_markdown(str(exec_res))

        # 处理search_relevant_tools结果并更新工具-服务器映射
        if tool_name == "search_relevant_tools":
            tool_servers = shared.get("tool_servers", {})
            tools_list = shared.get("tools", [])
            
            # search_relevant_tools直接返回工具列表
            tools_to_process = exec_res
            
            # 如果返回值是字典且包含tools字段（旧格式），则使用其tools字段
            if isinstance(exec_res, dict) and "tools" in exec_res:
                tools_to_process = exec_res.get("tools", [])
            
            # 如果返回值是列表（新格式），则直接使用
            elif isinstance(exec_res, list):
                tools_to_process = exec_res
                
            # 处理工具列表
            for tool_info in tools_to_process:
                if not isinstance(tool_info, dict):
                    continue

                t_name = tool_info.get("name")
                srv_name = tool_info.get("server_name")

                if not t_name or not srv_name:
                    continue

                # 更新服务器映射
                tool_servers[t_name] = srv_name

                # 同时将工具定义追加到 tools 列表，方便后续在 system_prompt 中引用
                definition = (
                    tool_info.get("definition")
                    or tool_info.get("tool")
                    or {
                        "name": t_name,
                        "description": tool_info.get("description", ""),
                        "parameters": tool_info.get("parameters", {}),
                    }
                )

                tools_list.append({"server_name": srv_name, "tool": definition})

            shared["tool_servers"] = tool_servers
            shared["tools"] = tools_list

        # 检查是否是shell命令的特殊状态
        if isinstance(exec_res, dict) and "status" in exec_res:
            # 如果是复制到剪贴板(y)或取消操作(q)，不需要再调用LLM
            if exec_res["status"] in ["completed"]:
                return "completed"

        return "call_llm"
