import time
from typing import Iterator, Optional
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner
from viby.utils.formatting import process_markdown_links
from viby.locale import get_text


class MarkdownStreamRenderer:
    """优化的Markdown流式渲染器"""

    def __init__(self):
        """初始化渲染器"""
        self.console = Console()
        self.buffer = []
        self.last_render_time = 0
        self.in_code_block = False
        self.content = {"text": "", "para": [], "code": []}

        # 默认配置
        self.typing_effect = True
        self.typing_speed = 0.001
        self.smooth_scroll = True
        self.throttle_ms = 0
        self.buffer_size = 10
        self.show_cursor = False
        self.cursor_char = "▌"
        self.cursor_blink = True
        self.enable_animations = True
        self.code_block_instant = True

        # 性能监控
        self.render_count = 0
        self.total_render_time = 0
        self.start_time = 0
        self.end_time = 0

    def _should_render(self) -> bool:
        """
        决定是否应该执行渲染操作
        基于节流时间和缓冲区大小
        """
        now = time.time() * 1000  # 转换为毫秒
        time_passed = now - self.last_render_time

        # 如果已经过了节流时间或缓冲区满了，就应该渲染
        if time_passed >= self.throttle_ms or len(self.buffer) >= self.buffer_size:
            self.last_render_time = now
            return True
        return False

    def _process_buffer(self):
        """处理缓冲区内容"""
        if not self.buffer:
            return

        # 合并缓冲区内容
        chunk = "".join(self.buffer)
        self.buffer.clear()

        # 处理特殊标签
        chunk = chunk.replace("<think>", "\n<think>\n").replace(
            "</think>", "\n</think>\n"
        )

        # 处理每一行
        for line in chunk.splitlines(keepends=True):
            line = line.replace("<think>", "`<think>`").replace(
                "</think>", "`</think>`"
            )

            # 处理代码块标记
            if line.lstrip().startswith("```"):
                if not self.in_code_block:
                    self._flush_paragraph()
                self.in_code_block = not self.in_code_block
                self.content["code"].append(line)
                if not self.in_code_block:
                    self._flush_code_block()
                continue

            # 根据当前状态添加内容
            if self.in_code_block:
                self.content["code"].append(line)
            else:
                if not line.strip():
                    self._flush_paragraph()
                else:
                    self.content["para"].append(line)

        # 更新完整内容
        self.content["text"] += chunk

    def _flush_paragraph(self):
        """将段落内容渲染到控制台"""
        if not self.content["para"]:
            return

        text = "".join(self.content["para"])
        processed_text = process_markdown_links(text)

        # 使用打字机效果或直接渲染
        if self.typing_effect:
            self._render_with_typing_effect(processed_text, False)
        else:
            self.console.print(Markdown(processed_text, justify="left"))

        self.content["para"].clear()

    def _flush_code_block(self):
        """将代码块内容渲染到控制台"""
        if not self.content["code"]:
            return

        code_text = "".join(self.content["code"])

        # 代码块可以选择是否使用打字机效果
        if self.typing_effect and not self.code_block_instant:
            self._render_with_typing_effect(code_text, True)
        else:
            self.console.print(Markdown(code_text, justify="left"))

        self.content["code"].clear()

    def _render_with_typing_effect(self, text: str, is_code: bool):
        """
        使用打字机效果渲染文本

        Args:
            text: 要渲染的文本
            is_code: 是否是代码块
        """
        # 预处理为Markdown，但不立即渲染
        Markdown(text, justify="left")

        with Live(auto_refresh=False) as live:
            rendered_text = ""
            i = 0
            while i < len(text):
                # 显示更多的字符
                rendered_text += text[i]
                i += 1

                # 刷新显示
                if i % 3 == 0 or i == len(text):  # 为提高性能，每3个字符刷新一次
                    cursor = self.cursor_char if self.show_cursor else ""
                    live.update(
                        Markdown(rendered_text + cursor, justify="left"), refresh=True
                    )

                # 控制速度
                if not is_code or not self.code_block_instant:
                    time.sleep(self.typing_speed)

    def render_stream(
        self, text_stream: Iterator[str], return_full: bool = True
    ) -> Optional[str]:
        """
        渲染流式文本内容

        Args:
            text_stream: 文本流迭代器
            return_full: 是否返回完整内容

        Returns:
            完整内容（如果return_full为True）
        """
        self.start_time = time.time()

        # 显示加载指示器
        if self.enable_animations:
            spinner = Spinner("dots")
            with Live(spinner, auto_refresh=True, transient=True) as live:
                live.update(spinner)
                time.sleep(0.5)  # 让用户看到加载动画

        try:
            for chunk in text_stream:
                # 将块添加到缓冲区
                self.buffer.append(chunk)

                # 判断是否应该渲染
                if self._should_render():
                    render_start = time.time()
                    self._process_buffer()
                    self.render_count += 1
                    self.total_render_time += time.time() - render_start

            # 确保所有内容都被处理
            if self.buffer:
                self._process_buffer()

            # 刷新剩余内容
            if self.in_code_block:
                self._flush_code_block()
                # 确保重置代码块状态，处理未闭合的代码块情况
                self.in_code_block = False
            else:
                self._flush_paragraph()

        except Exception as e:
            self.console.print(
                f"[bold red]{get_text('RENDERER', 'render_error', str(e))}[/bold red]"
            )

        self.end_time = time.time()

        if return_full:
            return self.content["text"]
        return None


# 默认渲染器实例，方便直接使用
default_renderer = MarkdownStreamRenderer()


def print_markdown(text: str, style: str = None) -> None:
    """
    打印Markdown格式的文本

    Args:
        text: 要打印的Markdown文本
        style: 可选的样式（error, warning, success等）
    """
    console = Console()

    # 根据样式应用不同的颜色
    if style == "error":
        console.print(f"[bold red]{text}[/bold red]")
    elif style == "warning":
        console.print(f"[bold yellow]{text}[/bold yellow]")
    elif style == "success":
        console.print(f"[bold green]{text}[/bold green]")
    else:
        # 默认使用Markdown渲染
        md = Markdown(text)
        console.print(md)


def render_markdown_stream(
    text_stream: Iterator[str],
    return_full: bool = True,
) -> Optional[str]:
    """
    优化版的流式Markdown渲染函数

    Args:
        text_stream: 文本流迭代器
        return_full: 是否返回完整内容

    Returns:
        完整内容（如果return_full为True）
    """
    return default_renderer.render_stream(text_stream, return_full)
