"""
Viby 应用统一 UI 界面模块

提供统一的界面元素、格式化输出和渲染功能，确保应用整体风格统一。
"""

import re
import json
import shutil
from typing import Iterable, Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from flatlatex import converter


# 基本颜色定义
class Colors:
    # 基本颜色
    GREEN = "\033[32m"  # 标准绿色
    BLUE = "\033[34m"  # 标准蓝色
    YELLOW = "\033[33m"  # 标准黄色
    RED = "\033[31m"  # 标准红色
    CYAN = "\033[36m"  # 青色
    MAGENTA = "\033[35m"  # 紫色

    # 高亮色（更明亮）
    BRIGHT_GREEN = "\033[92m"  # 亮绿色
    BRIGHT_BLUE = "\033[94m"  # 亮蓝色
    BRIGHT_YELLOW = "\033[93m"  # 亮黄色
    BRIGHT_RED = "\033[91m"  # 亮红色
    BRIGHT_CYAN = "\033[96m"  # 亮青色
    BRIGHT_MAGENTA = "\033[95m"  # 亮紫色

    # 格式
    BOLD = "\033[1;1m"  # 粗体，使用1;1m增加兼容性
    UNDERLINE = "\033[4m"  # 下划线
    ITALIC = "\033[3m"  # 斜体（部分终端支持）

    # 重置
    END = "\033[0m"


# 统一的输出方式
console = Console()

# LaTeX 渲染器
MATH_CONVERTER = converter()


# 基本界面元素
def print_separator(char="─"):
    """
    根据终端宽度打印一整行分隔线。

    Args:
        char: 分隔线字符，默认为"─"
    """
    width = shutil.get_terminal_size().columns
    console.print(char * width)


def print_header(title, char="="):
    """
    打印格式化的标题，带有分隔线框

    Args:
        title: 要显示的标题文本
        char: 分隔线字符，默认为"="
    """
    print()
    print_separator(char)
    width = shutil.get_terminal_size().columns
    console.print(f"{title:^{width}}")
    print_separator(char)
    print()


def colorize(text, color=None, style=None):
    """
    为文本添加颜色和样式

    Args:
        text: 要格式化的文本
        color: 颜色名称 (例如 "green", "red", "blue")
        style: 样式 (例如 "bold", "italic", "underline")

    Returns:
        格式化后的文本
    """
    if not color and not style:
        return text

    rich_style = []
    if color:
        rich_style.append(color)
    if style:
        rich_style.append(style)

    style_str = " ".join(rich_style)
    return f"[{style_str}]{text}[/{style_str}]"


# Markdown 处理函数
def process_markdown_links(text):
    """
    处理 Markdown 链接，使其同时显示链接文本和 URL。
    将 [text](url) 格式转换为 [text (url)](url) 格式。

    Args:
        text: 原始 Markdown 文本

    Returns:
        处理后的 Markdown 文本，链接同时显示文本和 URL
    """
    # 正则表达式匹配 Markdown 链接 [text](url)
    link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"

    def replace_link(match):
        text = match.group(1)
        url = match.group(2)
        # 如果链接文本中已经包含 URL，则不做修改
        if url in text:
            return f"[{text}]({url})"
        # 否则将 URL 添加到链接文本中
        return f"[{text} ({url})]({url})"

    # 替换所有链接
    return re.sub(link_pattern, replace_link, text)


def _process_latex_tokens(text: str) -> str:
    """转换 LaTeX 数学公式 ($...$ 和 $$...$$) 为 Unicode。"""

    # 转换 display math $$...$$
    def _convert_display(m):
        expr = m.group(1)
        try:
            return MATH_CONVERTER.convert(expr)
        except Exception:
            return m.group(0)

    text = re.sub(r"\$\$(.+?)\$\$", _convert_display, text, flags=re.DOTALL)

    # 转换 inline math $...$
    def _convert_inline(m):
        expr = m.group(1)
        try:
            return MATH_CONVERTER.convert(expr)
        except Exception:
            return m.group(0)

    text = re.sub(r"\$(.+?)\$", _convert_inline, text)
    return text


def _process_think_tokens(text: str) -> str:
    """处理思考标记，格式化 <think> 和 </think> 标签。"""
    # 检查文本是否以 <think> 开头
    if text.startswith("<think>"):
        # 移除开头的 <think> 标签并在适当位置添加格式化的标签
        text = text.replace("<think>", "`<think>`\n\n")

    # 检查文本是否包含 </think> 结尾标签
    if "</think>" in text:
        # 将 </think> 替换为格式化的标签
        text = text.replace("</think>", "\n`</think>`\n\n")

    return text


def _is_interactive(console: Console) -> bool:
    """判断当前 console 是否连接到交互式 TTY。"""
    # 一些环境（如 Jupyter Notebook）虽然 is_terminal 为 True，但不支持 ANSI 控制码
    is_jupyter = getattr(console, "_is_jupyter", False)
    return console.is_terminal and not is_jupyter


def extract_answer(raw_text: str) -> str:
    """
    从原始文本中提取答案，去除思考块

    Args:
        raw_text: 原始文本，可能包含 <think> 块

    Returns:
        清理后的文本
    """
    clean_text = raw_text.strip()

    # 去除所有 <think>...</think> 块
    while "<think>" in clean_text and "</think>" in clean_text:
        think_start = clean_text.find("<think>")
        think_end = clean_text.find("</think>") + len("</think>")
        clean_text = clean_text[:think_start] + clean_text[think_end:]

    # 最后再清理一次空白字符
    return clean_text.strip()


def format_markdown(content):
    """
    格式化内容为 Markdown 字符串

    Args:
        content: 要格式化的内容，可以是字符串、字典、列表等

    Returns:
        格式化后的 Markdown 字符串
    """
    if isinstance(content, (dict, list)):
        text = json.dumps(content, ensure_ascii=False, indent=2)
        return f"```json\n{text}\n```"
    else:
        return str(content)


def print_markdown(content, style=None):
    """
    以 Markdown 格式打印内容或使用特定样式直接打印文本

    Args:
        content: 要打印的内容，可以是字符串、字典、列表等
        style: 可选的样式（error, warning, success等），用于简单文本着色
    """
    # 使用样式直接打印
    if style in ["error", "warning", "success"]:
        style_map = {
            "error": "bold red",
            "warning": "bold yellow",
            "success": "bold green",
        }
        console.print(f"[{style_map[style]}]{content}[/{style_map[style]}]")
        return

    # 使用Markdown渲染
    md_text = format_markdown(content)
    console.print(Markdown(md_text, justify="left"))


def render_markdown_stream(
    text_stream: Iterable[str],
    *,
    console_instance: Optional[Console] = None,
    refresh_per_second: int = 120,
    enhance_links: bool = True,
) -> str:
    """
    流式渲染 Markdown 文本

    Args:
        text_stream: 文本流迭代器
        console_instance: 可选的 Console 实例，默认使用全局 console
        refresh_per_second: 刷新频率，默认 120 Hz
        enhance_links: 是否增强链接显示，默认为 True

    Returns:
        完整渲染后的文本
    """
    console_instance = console_instance or console
    accumulated: list[str] = []  # 使用列表收集字符串，效率更高

    # 对于非交互终端（如重定向到文件），直接顺序输出即可
    if not _is_interactive(console_instance):
        for chunk in text_stream:
            if chunk:
                accumulated.append(chunk)
                # 保留 <think> 标记但确保其独占一行
                printable = _process_think_tokens(_process_latex_tokens(chunk))
                console_instance.print(printable, end="", soft_wrap=True)
        console_instance.print()  # 最后补一个换行
        return "".join(accumulated)

    # 交互式终端使用 Live 动态刷新，获得更流畅的体验
    with Live(
        Markdown(""),
        console=console_instance,
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
            extra_lines = max(0, console_instance.height - 10)

            # 滚动到最后一行的技巧
            content_to_display = processed_content
            if "\n" in content_to_display:
                lines = content_to_display.splitlines()
                if len(lines) > console_instance.height - 5:
                    # 若内容太长，只显示最后几行
                    content_to_display = "\n".join(
                        lines[-(console_instance.height - 5) :]
                    )

            # 确保内容始终保持在视野内
            content_with_padding = content_to_display + "\n" * extra_lines

            live.update(Markdown(content_with_padding))

    # Live 区域已被清理，再次打印最终内容供用户滚动查看
    final_text = "".join(accumulated)
    final_text = _process_think_tokens(_process_latex_tokens(final_text))
    if enhance_links:
        final_text = process_markdown_links(final_text)
    console_instance.print(Markdown(final_text))

    return final_text


# 用户交互函数
def get_input(
    prompt,
    default=None,
    validator=None,
    choices=None,
    allow_pass_keyword=False,
    pass_keyword="pass",
    pass_hint="(输入 'pass' 跳过)",
):
    """
    获取用户输入，支持默认值和验证

    Args:
        prompt: 提示文本
        default: 默认值
        validator: 验证函数，返回 True/False
        choices: 可选项列表
        allow_pass_keyword: 是否允许跳过关键字
        pass_keyword: 跳过的关键字，默认为 'pass'
        pass_hint: 跳过提示文本

    Returns:
        用户输入或 PASS_SENTINEL
    """
    PASS_SENTINEL = "_viby_internal_pass_"

    base_prompt_text = prompt
    if allow_pass_keyword:
        base_prompt_text = f"{prompt} {pass_hint}"

    if default is not None:
        prompt_text = f"{base_prompt_text} [{default}]: "
    else:
        prompt_text = f"{base_prompt_text}: "

    while True:
        user_input = input(prompt_text).strip()

        if allow_pass_keyword and user_input.lower() == pass_keyword:
            return PASS_SENTINEL

        # 用户未输入，使用默认值
        if not user_input and default is not None:
            return default

        # 如果有选项限制，验证输入
        if choices and user_input not in choices:
            print(f"输入错误！请从以下选项中选择: {', '.join(choices)}")
            continue

        # 如果有验证函数，验证输入
        if validator and not validator(user_input):
            continue

        return user_input


def number_choice(choices, prompt, default_index=0):
    """
    显示编号选项并获取用户选择

    Args:
        choices: 选项列表
        prompt: 提示文本
        default_index: 默认选项索引（从0开始）

    Returns:
        用户选择的选项
    """
    if not choices:
        raise ValueError("选项列表不能为空")

    default_num = default_index + 1  # 用户看到的编号从1开始

    print(prompt)
    for i, choice in enumerate(choices, 1):
        print(f"  {i}. {choice}")

    while True:
        try:
            choice = input(f"[{default_num}]: ").strip()
            if not choice:
                return choices[default_index]  # 默认选项

            choice_num = int(choice)
            if 1 <= choice_num <= len(choices):
                return choices[choice_num - 1]
            else:
                print(f"请输入1到{len(choices)}之间的数字")
        except ValueError:
            print("请输入有效的数字")


# 显示状态和提示
def show_success(message):
    """显示成功消息"""
    console.print(f"[bold green]✓ {message}[/bold green]")


def show_error(message):
    """显示错误消息"""
    console.print(f"[bold red]✗ {message}[/bold red]")


def show_warning(message):
    """显示警告消息"""
    console.print(f"[bold yellow]! {message}[/bold yellow]")


def show_info(message):
    """显示信息消息"""
    console.print(f"[bold blue]ℹ {message}[/bold blue]")
