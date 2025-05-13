from typing import Iterable, Optional

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
import re
from flatlatex import converter

# 本地工具函数
from viby.utils.formatting import process_markdown_links, print_markdown

__all__ = ["render_markdown_stream", "print_markdown"]


def _is_interactive(console: Console) -> bool:
    """判断当前 ``console`` 是否连接到交互式 TTY。"""

    # 一些环境（如 Jupyter Notebook）虽然 is_terminal 为 True，但不支持 ANSI 控制码
    is_jupyter = getattr(console, "_is_jupyter", False)
    return console.is_terminal and not is_jupyter


# math converter for LaTeX rendering
MATH_CONVERTER = converter()


def _process_latex_tokens(text: str) -> str:
    """Convert LaTeX math ($...$ and $$...$$) to unicode using flatlatex."""

    # convert display math $$...$$
    def _convert_display(m):
        expr = m.group(1)
        try:
            return MATH_CONVERTER.convert(expr)
        except Exception:
            return m.group(0)

    text = re.sub(r"\$\$(.+?)\$\$", _convert_display, text, flags=re.DOTALL)

    # convert inline math $...$
    def _convert_inline(m):
        expr = m.group(1)
        try:
            return MATH_CONVERTER.convert(expr)
        except Exception:
            return m.group(0)

    text = re.sub(r"\$(.+?)\$", _convert_inline, text)
    return text


def render_markdown_stream(
    text_stream: Iterable[str],
    *,
    console: Optional[Console] = None,
    refresh_per_second: int = 120,
    enhance_links: bool = True,
) -> str:
    console = console or Console()
    accumulated: list[str] = []  # 使用列表收集字符串，效率更高

    # 对于非交互终端（如重定向到文件），直接顺序输出即可。
    if not _is_interactive(console):
        for chunk in text_stream:
            if chunk:
                accumulated.append(chunk)
                # 保留 <think> 标记但确保其独占一行
                printable = _process_think_tokens(_process_latex_tokens(chunk))
                console.print(printable, end="", soft_wrap=True)
        console.print()  # 最后补一个换行
        return "".join(accumulated)

    # 交互式终端使用 Live 动态刷新，获得更流畅的体验。
    with Live(
        Markdown(""),
        console=console,
        refresh_per_second=refresh_per_second,
        transient=True,  # 退出时清理 Live 区域，随后输出最终结果
        auto_refresh=True,
    ) as live:
        content_so_far = ""
        for chunk in text_stream:
            if not chunk:
                continue
            accumulated.append(chunk)
            content_so_far = "".join(accumulated)

            # 处理 <think> 标记以确保独立成行并用特殊样式显示
            processed_content = _process_think_tokens(
                _process_latex_tokens(content_so_far)
            )

            if enhance_links:
                processed_content = process_markdown_links(processed_content)

            # 保证内容可见: 通过确保较大的内容不会被截断
            # 这里使用空行确保内容显示在终端高度的最下方
            # 注意：这与 transient=True 配合使用可正常工作
            extra_lines = max(0, console.height - 10)

            # 滚动到最后一行的技巧
            content_to_display = processed_content
            if "\n" in content_to_display:
                lines = content_to_display.splitlines()
                if len(lines) > console.height - 5:
                    # 若内容太长，只显示最后几行
                    content_to_display = "\n".join(lines[-(console.height - 5) :])

            # 确保内容始终保持在视野内
            content_with_padding = content_to_display + "\n" * extra_lines

            live.update(Markdown(content_with_padding))

    # Live 区域已被清理，再次打印最终内容供用户滚动查看
    final_text = "".join(accumulated)
    final_text = _process_think_tokens(_process_latex_tokens(final_text))
    if enhance_links:
        final_text = process_markdown_links(final_text)
    console.print(Markdown(final_text))

    return final_text


def _process_think_tokens(text: str) -> str:
    # 检查文本是否以 <think> 开头
    if text.startswith("<think>"):
        # 移除开头的 <think> 标签并在适当位置添加格式化的标签
        text = text.replace("<think>", "`<think>`\n\n")

    # 检查文本是否包含 </think> 结尾标签
    if "</think>" in text:
        # 将 </think> 替换为格式化的标签
        text = text.replace("</think>", "\n`</think>`\n\n")

    return text
