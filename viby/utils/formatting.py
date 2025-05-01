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
    流式获取模型回复并输出到终端。
    """
    raw_response = ""
    for chunk in model_manager.stream_response(user_input):
        print(chunk, end="", flush=True)
        raw_response += chunk
    print()
    if return_raw:
        return raw_response
    return 0