from pocketflow import Node
from viby.utils.renderer import render_markdown_stream
from viby.locale import get_text
import threading
import sys
import select
import platform
import json
import re


class LLMNode(Node):
    """通用的模型回复节点，负责调用LLM获取回复并处理工具调用"""

    def prep(self, shared):
        """准备模型调用所需的参数"""
        interrupt_event = threading.Event()
        listener_thread = None

        def _listen_for_interrupt(event):
            try:
                # 根据平台和环境选择合适的监听方式
                if sys.stdin.isatty():
                    # 标准输入是终端，直接监听标准输入
                    while not event.is_set():
                        if select.select([sys.stdin], [], [], 0.1)[0]:
                            sys.stdin.readline()
                            event.set()
                            break
                elif platform.system() != "Windows":
                    # 非 Windows 系统，尝试打开 TTY 设备
                    try:
                        with open("/dev/tty", "r") as tty:
                            while not event.is_set():
                                if select.select([tty], [], [], 0.1)[0]:
                                    tty.readline()
                                    event.set()
                                    break
                    except (OSError, IOError):
                        # 无法打开 TTY 设备，不进行监听
                        pass
                else:
                    # Windows 系统，尝试使用 msvcrt
                    try:
                        import msvcrt
                        import time

                        while not event.is_set():
                            if msvcrt.kbhit():
                                char = msvcrt.getch()
                                if char in (b"\r", b"\n", b" "):
                                    event.set()
                                    break
                            time.sleep(0.1)
                    except ImportError:
                        pass
            except Exception:
                # 捕获所有异常，确保线程不会崩溃
                pass

        # 创建并启动监听线程
        listener_thread = threading.Thread(
            target=_listen_for_interrupt, args=(interrupt_event,), daemon=True
        )
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
        interrupt_event = prep_res.get("interrupt_event")
        listener_thread = prep_res.get("listener_thread")

        if not manager or not messages:
            return None

        chunks = []
        was_interrupted = False

        def _stream_response():
            nonlocal was_interrupted
            for text in manager.get_response(messages):
                if interrupt_event and interrupt_event.is_set():
                    was_interrupted = True
                    break
                if text:
                    chunks.append(text)
                    yield text

        render_markdown_stream(_stream_response())

        return {
            "text_content": "".join(chunks),
            "interrupt_event": interrupt_event,
            "listener_thread": listener_thread,
            "was_interrupted": was_interrupted,
        }

    def post(self, shared, prep_res, exec_res):
        """处理模型响应，处理工具调用（如果有），清理监听线程"""
        text_content = exec_res.get("text_content", "")
        interrupt_event = exec_res.get("interrupt_event")
        listener_thread = exec_res.get("listener_thread")
        was_interrupted = exec_res.get("was_interrupted", False)

        # 只有当监听线程存在时才尝试清理
        if listener_thread and listener_thread.is_alive():
            if interrupt_event:
                interrupt_event.set()
            listener_thread.join(timeout=0.2)

        shared["response"] = text_content
        shared["messages"].append({"role": "assistant", "content": text_content})

        # 尝试解析XML格式的工具调用
        tool_call = self._extract_xml_tool_call(text_content)
        if tool_call:
            return self._handle_xml_tool_call(shared, tool_call)

        if was_interrupted:
            return "interrupt"
        return "continue"

    def _extract_xml_tool_call(self, text):
        """从文本中提取XML格式的工具调用"""
        try:
            # 使用正则表达式匹配<tool_call>和</tool_call>之间的内容
            tool_pattern = r"<tool_call>(.*?)</tool_call>"
            tool_match = re.search(tool_pattern, text, re.DOTALL)

            if tool_match:
                tool_content = tool_match.group(1).strip()
                # 解析JSON内容
                tool_data = json.loads(tool_content)
                return tool_data
            return None
        except Exception as e:
            print(get_text("MCP", "parsing_error", e))
            return None

    def _handle_xml_tool_call(self, shared, tool_data):
        """处理XML格式的工具调用"""
        try:
            tool_name = tool_data.get("name", "")
            arguments = tool_data.get("arguments", {})

            if not tool_name:
                print(get_text("MCP", "parsing_error", "No tool name specified in XML"))
                return "continue"

            # 使用 tool_servers 映射直接查找服务器名称
            tool_servers = shared.get("tool_servers", {})
            selected_server = tool_servers.get(tool_name)

            if not selected_server:
                print(get_text("MCP", "parsing_error", f"Tool '{tool_name}' not found"))
                return "continue"

            shared.update(
                {
                    "tool_name": tool_name,
                    "parameters": arguments,
                    "selected_server": selected_server,
                }
            )
            return "execute_tool"
        except Exception as e:
            print(get_text("MCP", "parsing_error", e))
            return "continue"

    def exec_fallback(self, prep_res, exc):
        """错误处理：提供友好的错误信息"""
        return f"Error: {str(exc)}"
