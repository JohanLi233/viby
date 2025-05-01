from rich.console import Console
from rich.markdown import Markdown

class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def extract_answer(raw_text: str) -> str:
    clean_text = raw_text.strip()
    
    # 去除所有 <think>...</think> 块
    while "<think>" in clean_text and "</think>" in clean_text:
        think_start = clean_text.find("<think>")
        think_end = clean_text.find("</think>") + len("</think>")
        clean_text = clean_text[:think_start] + clean_text[think_end:]
    
    # 最后再清理一次空白字符
    return clean_text.strip()

def response(model_manager, user_input, return_raw):
    """
    流式获取模型回复并使用Rich渲染Markdown输出到终端。
    """
    console = Console()
    raw_response = ""
    line_buffer = ""
    for chunk in model_manager.stream_response(user_input):
        raw_response += chunk
        line_buffer += chunk
        while '\n' in line_buffer:
            line, line_buffer = line_buffer.split('\n', 1)
            # 处理<think>标签并渲染该行
            formatted_line = line.replace("<think>", "`<think>`").replace("</think>", "`</think>`")
            if formatted_line.strip():
                console.print(Markdown(formatted_line, justify="left"))
    # 打印最后一行（如果没有以换行结尾）
    if line_buffer.strip():
        formatted_line = line_buffer.replace("<think>", "`<think>`").replace("</think>", "`</think>`")
        console.print(Markdown(formatted_line, justify="left"))
    console.print("")

    if return_raw:
        return raw_response
    return 0