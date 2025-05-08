"""
优化的流式渲染器模块，提供更流畅的终端输出体验。

提供以下功能：
1. 输出缓冲和节流，减少闪烁
2. 打字机效果
3. 平滑动画
4. 自定义样式
5. 性能监控
"""

import time
from typing import Iterator, Optional, Dict, Any
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from rich.style import Style
from rich.spinner import Spinner
from viby.utils.formatting import process_markdown_links
from viby.locale import get_text


# 导入配置中的RenderConfig，但也提供一个本地版本用于兼容和单独使用
try:
    from viby.config.app_config import RenderConfig
except ImportError:
    # 当从app_config导入失败时使用本地定义的版本
    class RenderConfig:
        """渲染配置类，控制渲染器的行为"""

        def __init__(
            self,
            typing_effect: bool = False,
            typing_speed: float = 0.01,
            smooth_scroll: bool = True,
            throttle_ms: int = 50,
            buffer_size: int = 10,
            show_cursor: bool = True,
            cursor_char: str = "▌",
            cursor_blink: bool = True,
            enable_animations: bool = True,
            code_block_instant: bool = True,
            theme: Dict[str, Any] = None,
        ):
            """
            初始化渲染配置

            Args:
                typing_effect: 是否启用打字机效果
                typing_speed: 打字机效果的字符间延迟（秒）
                smooth_scroll: 是否启用平滑滚动
                throttle_ms: 渲染节流时间（毫秒）
                buffer_size: 缓冲区大小（字符数），决定多少字符作为一个批次处理
                show_cursor: 是否显示光标
                cursor_char: 光标字符
                cursor_blink: 光标是否闪烁
                enable_animations: 是否启用动画效果
                code_block_instant: 代码块是否立即渲染（不使用打字机效果）
                theme: 自定义主题设置
            """
            self.typing_effect = typing_effect
            self.typing_speed = typing_speed
            self.smooth_scroll = smooth_scroll
            self.throttle_ms = throttle_ms
            self.buffer_size = buffer_size
            self.show_cursor = show_cursor
            self.cursor_char = cursor_char
            self.cursor_blink = cursor_blink
            self.enable_animations = enable_animations
            self.code_block_instant = code_block_instant

            # 默认主题
            self._default_theme = {
                "paragraph_style": Style(),
                "code_style": Style(color="bright_blue"),
                "heading_style": Style(bold=True),
            }

            # 合并自定义主题
            self.theme = self._default_theme.copy()
            if theme:
                self.theme.update(theme)


class MarkdownStreamRenderer:
    """优化的Markdown流式渲染器"""

    def __init__(self, config: Optional[RenderConfig] = None):
        """
        初始化渲染器

        Args:
            config: 渲染配置，为None则使用默认配置
        """
        self.config = config or RenderConfig()
        self.console = Console()
        self.buffer = []
        self.last_render_time = 0
        self.in_code_block = False
        self.content = {"text": "", "para": [], "code": []}

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
        if (
            time_passed >= self.config.throttle_ms
            or len(self.buffer) >= self.config.buffer_size
        ):
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
        if self.config.typing_effect:
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
        if self.config.typing_effect and not self.config.code_block_instant:
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
                    cursor = self.config.cursor_char if self.config.show_cursor else ""
                    live.update(
                        Markdown(rendered_text + cursor, justify="left"), refresh=True
                    )

                # 控制速度
                if not is_code or not self.config.code_block_instant:
                    time.sleep(self.config.typing_speed)

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
        if self.config.enable_animations:
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

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        获取性能统计信息

        Returns:
            包含性能统计的字典
        """
        total_time = self.end_time - self.start_time

        return {
            "total_time": total_time,
            "render_count": self.render_count,
            "avg_render_time": self.total_render_time / max(1, self.render_count),
            "total_render_time": self.total_render_time,
            "rendering_efficiency": 1
            - (self.total_render_time / max(0.001, total_time)),
        }


# 默认渲染器实例，方便直接使用
default_renderer = MarkdownStreamRenderer()


def render_markdown_stream_optimized(
    text_stream: Iterator[str],
    config: Optional[RenderConfig] = None,
    return_full: bool = True,
) -> Optional[str]:
    """
    优化版的流式Markdown渲染函数

    Args:
        text_stream: 文本流迭代器
        config: 渲染配置，为None则使用默认配置
        return_full: 是否返回完整内容

    Returns:
        完整内容（如果return_full为True）
    """
    renderer = MarkdownStreamRenderer(config or RenderConfig())
    return renderer.render_stream(text_stream, return_full)


# 便于直接导入的工厂函数
def create_renderer(
    typing_effect: bool = False,
    typing_speed: float = 0.01,
    smooth_scroll: bool = True,
    throttle_ms: int = 50,
    buffer_size: int = 10,
    show_cursor: bool = True,
    cursor_char: str = "▌",
    cursor_blink: bool = True,
    enable_animations: bool = True,
    code_block_instant: bool = True,
    theme: Dict[str, Any] = None,
) -> MarkdownStreamRenderer:
    """
    创建自定义配置的渲染器

    Args:
        typing_effect: 是否启用打字机效果
        typing_speed: 打字机效果的字符间延迟（秒）
        smooth_scroll: 是否启用平滑滚动
        throttle_ms: 渲染节流时间（毫秒）
        buffer_size: 缓冲区大小（字符数）
        show_cursor: 是否显示光标
        cursor_char: 光标字符
        cursor_blink: 光标是否闪烁
        enable_animations: 是否启用动画效果
        code_block_instant: 代码块是否立即渲染
        theme: 自定义主题设置

    Returns:
        配置好的渲染器实例
    """
    config = RenderConfig(
        typing_effect=typing_effect,
        typing_speed=typing_speed,
        smooth_scroll=smooth_scroll,
        throttle_ms=throttle_ms,
        buffer_size=buffer_size,
        show_cursor=show_cursor,
        cursor_char=cursor_char,
        cursor_blink=cursor_blink,
        enable_animations=enable_animations,
        code_block_instant=code_block_instant,
        theme=theme,
    )
    return MarkdownStreamRenderer(config)
