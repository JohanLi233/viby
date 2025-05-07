from pocketflow import Node
from viby.utils.formatting import render_markdown_stream
from viby.locale import get_text

class LLMNode(Node):
    """通用的模型回复节点，负责调用LLM获取回复并处理工具调用"""
    
    def prep(self, shared):
        """准备模型调用所需的参数"""
        return {
            "model_manager": shared.get("model_manager"),
            "messages": shared.get("messages"),
            "tools": shared.get("tools")
        }

    def exec(self, prep_res):
        """执行模型调用并渲染输出，直接获取工具调用信息"""
        manager, messages, tools = (
            prep_res.get("model_manager"),
            prep_res.get("messages"),
            prep_res.get("tools"),
        )
        if not (manager and messages):
            return None

        chunks, calls = [], []

        def stream():
            for text, tool in manager.get_response(messages, tools):
                if tool:
                    calls[:] = tool
                if text:
                    chunks.append(text)
                    yield text

        render_markdown_stream(stream())
        return {"text_content": "".join(chunks), "tool_calls": calls}
    
    def post(self, shared, prep_res, exec_res):
        """处理模型响应，处理工具调用（如果有）"""
        # 从 exec_res 中提取文本内容和工具调用
        text_content = exec_res.get("text_content")
        tool_calls = exec_res.get("tool_calls", [])
        
        # 保存模型响应到共享状态
        shared["response"] = text_content
        shared["messages"].append({"role": "assistant", "content": text_content})
        
        if tool_calls:
            return self._handle_tool_call(shared, tool_calls[0])
                
        return "continue"
    
    def _handle_tool_call(self, shared, tool_call):
        """处理工具调用"""
        try:
            # 获取工具名称和参数
            tool_name = tool_call["name"]
            parameters = tool_call["parameters"]
            
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
            return None
    
    def exec_fallback(self, prep_res, exc):
        """错误处理：提供友好的错误信息"""
        return f"Error: {str(exc)}"
