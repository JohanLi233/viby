from pocketflow import Node
from viby.utils.formatting import render_markdown_stream
from viby.locale import get_text
import threading
import sys
import select

class LLMNode(Node):
    """通用的模型回复节点，负责调用LLM获取回复并处理工具调用"""

    def prep(self, shared):
        """准备模型调用所需的参数"""
        interrupt_event = threading.Event()

        def _listen_for_enter(event):
            while not event.is_set():
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    sys.stdin.readline()
                    event.set()
                    break

        listener_thread = threading.Thread(target=_listen_for_enter, args=(interrupt_event,), daemon=True)
        listener_thread.start()

        return {
            "model_manager": shared.get("model_manager"),
            "messages": shared.get("messages"),
            "tools": shared.get("tools"),
            "interrupt_event": interrupt_event,
            "listener_thread": listener_thread,
        }

    def exec(self, prep_res):
        """执行模型调用并渲染输出，直接获取工具调用信息"""
        manager = prep_res.get("model_manager")
        messages = prep_res.get("messages")
        tools = prep_res.get("tools")
        interrupt_event = prep_res.get("interrupt_event")
        listener_thread = prep_res.get("listener_thread")

        if not manager or not messages:
            return None

        chunks, tool_calls = [], []
        was_interrupted = False

        def _stream_response():
            nonlocal was_interrupted
            for text, tool in manager.get_response(messages, tools):
                if interrupt_event and interrupt_event.is_set():
                    was_interrupted = True
                    break
                if tool:
                    tool_calls.extend(tool)
                if text:
                    chunks.append(text)
                    yield text

        render_markdown_stream(_stream_response())

        return {
            "text_content": "".join(chunks),
            "tool_calls": tool_calls,
            "interrupt_event": interrupt_event,
            "listener_thread": listener_thread,
            "was_interrupted": was_interrupted
        }

    def post(self, shared, prep_res, exec_res):
        """处理模型响应，处理工具调用（如果有），清理监听线程"""
        text_content = exec_res.get("text_content", "")
        tool_calls = exec_res.get("tool_calls", [])
        interrupt_event = exec_res.get("interrupt_event")
        listener_thread = exec_res.get("listener_thread")
        was_interrupted = exec_res.get("was_interrupted", False)

        if listener_thread:
            if interrupt_event:
                interrupt_event.set()
            listener_thread.join(timeout=0.2)

        shared["response"] = text_content
        shared["messages"].append({"role": "assistant", "content": text_content})
        
        if tool_calls:
            return self._handle_tool_call(shared, tool_calls[0])
        if was_interrupted:
            return "interrupt"
        return "continue"

    def _handle_tool_call(self, shared, tool_call):
        """处理工具调用"""
        try:
            tool_name = tool_call["name"]
            parameters = tool_call["parameters"]
            selected_server = next(
                (t.get("server_name") for t in shared.get("tools", [])
                 if t.get("function", {}).get("name") == tool_name),
                None
            )
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
