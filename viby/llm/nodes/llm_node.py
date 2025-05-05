import json
from pocketflow import Node
from viby.utils.formatting import stream_render_response, extract_answer
from viby.locale import get_text

class LLMNode(Node):
    """通用的模型回复节点"""
    
    def prep(self, shared):
        """通用提取共享状态，消息构建在 prompt_node 完成"""
        return {
            "model_manager": shared.get("model_manager"),
            "messages": shared.get("messages"),
            "task_type": shared.get("task_type", "chat"),
            "tools": shared.get("tools")
        }

    def exec(self, prep_res):
        manager = prep_res.get("model_manager")
        messages = prep_res.get("messages")
        tools = prep_res.get("tools")
        if not manager or not messages:
            return None
        t = prep_res.get("task_type", "chat")
        raw = stream_render_response(manager, messages, tools)
        return extract_answer(raw) if t == "shell" else raw
    
    def post(self, shared, prep_res, exec_res):
        shared["response"] = exec_res
        task_type = prep_res.get("task_type", "chat")
        shared["messages"].append({"role": "assistant", "content": exec_res})
        # 自动检测 tool 调用
        if "```tool" in exec_res:
            return self._handle_tool_call(shared, exec_res)
        if task_type == "shell":
            shared["command"] = exec_res
            return "execute"
        return "continue"
    
    def _handle_tool_call(self, shared, exec_res):
        try:
            json_block = exec_res.split("```tool")[1].split("```")[0].strip()
            decision = json.loads(json_block)
            
            # 获取工具名称和参数
            tool_name = decision["tool"]
            parameters = decision["parameters"]
            
            # 从工具列表中找到对应的工具及其服务器
            selected_server = next(
                (tool.get("server_name") for tool in shared.get("tools", [])
                 if tool.get("function", {}).get("name") == tool_name),
                None
            )
            
            # 更新共享状态
            shared.update({
                "tool_name": tool_name,
                "parameters": parameters,
                "selected_server": selected_server
            })
            
            return "execute_tool"
        except Exception as e:
            print(get_text("MCP", "parsing_error", e))
            print("Raw response:", exec_res)
            return None
    
    def exec_fallback(self, prep_res, exc):
        # 错误处理：提供友好的错误信息
        return f"Error: {str(exc)}"
