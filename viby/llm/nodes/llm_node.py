from pocketflow import Node
from viby.utils.renderer import (
    render_markdown_stream_optimized,
    RenderConfig,
)
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

        def _listen_for_enter_tty(event):
            try:
                # 在类 Unix 系统上尝试直接打开终端设备
                if platform.system() != "Windows":
                    with open("/dev/tty", "r") as tty:
                        while not event.is_set():
                            if select.select([tty], [], [], 0.1)[0]:
                                tty.readline()
                                event.set()
                                break
                else:
                    # Windows 平台上使用 msvcrt 模块监听键盘输入
                    try:
                        import msvcrt

                        while not event.is_set():
                            if msvcrt.kbhit():  # 检查是否有键盘输入
                                char = msvcrt.getch()  # 读取一个字符
                                if char in (b"\r", b"\n", b" "):  # 回车、换行或空格
                                    event.set()
                                    break
                            # 短暂休眠，减少 CPU 使用
                            import time

                            time.sleep(0.1)
                    except ImportError:
                        pass  # 如果 msvcrt 不可用，则不监听
            except (OSError, IOError):
                # 如果无法打开终端设备，直接返回，不阻塞线程
                pass

        def _listen_for_enter_stdin(event):
            while not event.is_set():
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    sys.stdin.readline()
                    event.set()
                    break

        # 如果 stdin 是终端，使用标准的监听方法
        if sys.stdin.isatty():
            listener_thread = threading.Thread(
                target=_listen_for_enter_stdin, args=(interrupt_event,), daemon=True
            )
        else:
            # 在管道模式下，尝试直接监听终端设备
            listener_thread = threading.Thread(
                target=_listen_for_enter_tty, args=(interrupt_event,), daemon=True
            )

        # 启动监听线程
        listener_thread.start()

        return {
            "model_manager": shared.get("model_manager"),
            "messages": shared.get("messages"),
            "tools": shared.get("tools"),
            "interrupt_event": interrupt_event,
            "listener_thread": listener_thread,
            "config": shared.get("config"),  # 获取配置
        }

    def exec(self, prep_res):
        """执行模型调用并渲染输出，直接获取工具调用信息"""
        manager = prep_res.get("model_manager")
        messages = prep_res.get("messages")
        tools = prep_res.get("tools")
        interrupt_event = prep_res.get("interrupt_event")
        listener_thread = prep_res.get("listener_thread")
        config = prep_res.get("config")  # 获取配置

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

        # 使用优化的渲染器
        if config and hasattr(config, "render_config"):
            # 使用配置的渲染设置
            render_config = RenderConfig(
                typing_effect=config.render_config.typing_effect,
                typing_speed=config.render_config.typing_speed,
                smooth_scroll=config.render_config.smooth_scroll,
                throttle_ms=config.render_config.throttle_ms,
                buffer_size=config.render_config.buffer_size,
                show_cursor=config.render_config.show_cursor,
                cursor_char=config.render_config.cursor_char,
                cursor_blink=config.render_config.cursor_blink,
                enable_animations=config.render_config.enable_animations,
                code_block_instant=config.render_config.code_block_instant,
                theme=config.render_config.theme,
            )
            render_markdown_stream_optimized(_stream_response(), render_config)
        else:
            # 使用默认设置
            render_markdown_stream_optimized(_stream_response())

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
            
            # 查找匹配的工具
            selected_server = None
            for tool_wrapper in shared.get("tools", []):
                tool = tool_wrapper.get("tool")
                if hasattr(tool, "name") and tool.name == tool_name:
                    selected_server = tool_wrapper.get("server_name")
                    break
            
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
