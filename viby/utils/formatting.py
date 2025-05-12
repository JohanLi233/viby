import re
import json
from rich.console import Console
from rich.markdown import Markdown


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


def print_separator(char="─"):
    """
    根据终端宽度打印一整行分隔线。
    Args:
        char: 分隔线字符，默认为"─"
    """
    import shutil

    width = shutil.get_terminal_size().columns
    print(char * width)


def extract_answer(raw_text: str) -> str:
    clean_text = raw_text.strip()

    # 去除所有 <think>...</think> 块
    while "<think>" in clean_text and "</think>" in clean_text:
        think_start = clean_text.find("<think>")
        think_end = clean_text.find("</think>") + len("</think>")
        clean_text = clean_text[:think_start] + clean_text[think_end:]

    # 最后再清理一次空白字符
    return clean_text.strip()


def process_markdown_links(text):
    """
    处理 Markdown 链接，使其同时显示链接文本和 URL。
    将 [text](url) 格式转换为 [text (url)](url) 格式，这样 Rich 渲染时会同时显示文本和 URL。

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


def format_markdown(content):
    if isinstance(content, (dict, list)):
        text = json.dumps(content, ensure_ascii=False, indent=2)
        return f"```json\n{text}\n```"
    else:
        return str(content)


def print_markdown(content, style=None):
    """
    以 Markdown 格式打印内容或使用特定样式直接打印文本。

    Args:
        content: 要打印的内容，可以是字符串、字典、列表等
        style: 可选的样式（error, warning, success等），用于简单文本着色
    """
    console = Console()

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
