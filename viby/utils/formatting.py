import re
from rich.console import Console
from rich.markdown import Markdown

class Colors:
    # 基本颜色
    GREEN = '\033[32m'     # 标准绿色
    BLUE = '\033[34m'      # 标准蓝色
    YELLOW = '\033[33m'    # 标准黄色
    RED = '\033[31m'       # 标准红色
    CYAN = '\033[36m'      # 青色
    MAGENTA = '\033[35m'   # 紫色
    
    # 高亮色（更明亮）
    BRIGHT_GREEN = '\033[92m'  # 亮绿色
    BRIGHT_BLUE = '\033[94m'   # 亮蓝色
    BRIGHT_YELLOW = '\033[93m' # 亮黄色
    BRIGHT_RED = '\033[91m'    # 亮红色
    BRIGHT_CYAN = '\033[96m'   # 亮青色
    BRIGHT_MAGENTA = '\033[95m' # 亮紫色
    
    # 格式
    BOLD = '\033[1;1m'     # 粗体，使用1;1m增加兼容性
    UNDERLINE = '\033[4m'  # 下划线
    ITALIC = '\033[3m'     # 斜体（部分终端支持）
    
    # 重置
    END = '\033[0m'

def print_separator(char="─"):
    """
    根据终端宽度打印一整行分隔线。
    Args:
        char: 分隔线字符，默认为“─”
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
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    
    def replace_link(match):
        text = match.group(1)
        url = match.group(2)
        # 如果链接文本中已经包含 URL，则不做修改
        if url in text:
            return f'[{text}]({url})'
        # 否则将 URL 添加到链接文本中
        return f'[{text} ({url})]({url})'
    
    # 替换所有链接
    return re.sub(link_pattern, replace_link, text)

def format_markdown(content, title=None, code_type=None):
    """
    将内容格式化为标准的 Markdown 格式。
    
    Args:
        content: 要格式化的内容，可以是字符串、字典、列表等
        title: 可选的标题
        code_type: 代码块的类型，如 "json", "python" 等，为 None 则按纯文本处理
        
    Returns:
        格式化后的 Markdown 字符串
    """
    import json
    
    result = []
    
    # 添加标题
    if title:
        result.append(f"## {title}\n")
    
    # 处理内容
    if code_type:
        # 如果提供了代码类型，则格式化为代码块
        if isinstance(content, (dict, list)) and code_type == "json":
            # 字典或列表转为JSON
            formatted_content = json.dumps(content, ensure_ascii=False, indent=2)
            result.append(f"```{code_type}\n{formatted_content}\n```")
        else:
            # 其他内容转为字符串
            result.append(f"```{code_type}\n{str(content)}\n```")
    else:
        # 没有代码类型，直接添加内容
        if isinstance(content, (dict, list)):
            # 字典或列表转为JSON
            formatted_content = json.dumps(content, ensure_ascii=False, indent=2)
            result.append(f"```json\n{formatted_content}\n```")
        else:
            # 其他内容直接转为字符串
            result.append(str(content))
    
    return "\n".join(result)

def print_markdown(content, title=None, code_type=None):
    """
    以标准的 Markdown 格式打印内容。
    
    Args:
        content: 要打印的内容，可以是字符串、字典、列表等
        title: 可选的标题
        code_type: 代码块的类型，如 "json", "python" 等，为 None 则按纯文本处理
    """
    from rich.console import Console
    from rich.markdown import Markdown
    
    console = Console()
    md_text = format_markdown(content, title, code_type)
    console.print(Markdown(md_text, justify="left"))

def render_markdown_stream(text_stream, return_full=True):
    console = Console()
    raw, para, code = [], [], []
    in_code = False

    def flush_para():
        if para:
            text = ''.join(para)
            console.print(Markdown(process_markdown_links(text), justify="left"))
            para.clear()

    def flush_code():
        if code:
            console.print(Markdown(''.join(code), justify="left"))
            code.clear()

    for chunk in text_stream:
        if return_full:
            raw.append(chunk)
        chunk = chunk.replace("<think>", "\n<think>\n").replace("</think>", "\n</think>\n")
        for line in chunk.splitlines(keepends=True):
            line = line.replace("<think>", "`<think>`").replace("</think>", "`</think>`")
            if line.lstrip().startswith("```"):
                flush_para() if not in_code else None
                in_code = not in_code
                code.append(line)
                if not in_code:
                    flush_code()
                continue
            if in_code:
                code.append(line)
            else:
                if not line.strip():
                    flush_para()
                else:
                    para.append(line)

    # flush remaining
    (flush_code() if in_code else flush_para())
    if return_full:
        return ''.join(raw)