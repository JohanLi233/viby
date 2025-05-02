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

def process_latex(text):
    """
    简单处理LaTeX数学公式，将其转换为可在终端中显示的Unicode字符
    """
    
    # LaTeX 符号到 Unicode 的映射
    latex_symbols = {
        '\\Gamma': 'Γ', '\\Delta': 'Δ', '\\Theta': 'Θ', '\\Lambda': 'Λ', '\\Xi': 'Ξ',
        '\\Pi': 'Π', '\\Sigma': 'Σ', '\\Phi': 'Φ', '\\Psi': 'Ψ', '\\Omega': 'Ω',
        '\\alpha': 'α', '\\beta': 'β', '\\gamma': 'γ', '\\delta': 'δ', '\\epsilon': 'ε',
        '\\zeta': 'ζ', '\\eta': 'η', '\\theta': 'θ', '\\iota': 'ι', '\\kappa': 'κ',
        '\\lambda': 'λ', '\\mu': 'μ', '\\nu': 'ν', '\\xi': 'ξ', '\\omicron': 'ο',
        '\\pi': 'π', '\\rho': 'ρ', '\\sigma': 'σ', '\\tau': 'τ', '\\upsilon': 'υ',
        '\\phi': 'φ', '\\chi': 'χ', '\\psi': 'ψ', '\\omega': 'ω',
        '\\infty': '∞', '\\approx': '≈', '\\neq': '≠', '\\leq': '≤', '\\geq': '≥',
        '\\times': '×', '\\cdot': '·', '\\pm': '±', '\\rightarrow': '→', '\\leftarrow': '←',
        '\\Rightarrow': '⇒', '\\Leftarrow': '⇐', '\\subset': '⊂', '\\supset': '⊃',
        '\\in': '∈', '\\notin': '∉', '\\cup': '∪', '\\cap': '∩', '\\emptyset': '∅',
        '\\sqrt': '√', '\\sum': '∑', '\\prod': '∏', '\\int': '∫', '\\partial': '∂', '\\nabla': '∇',
        '\\sin': 'sin', '\\cos': 'cos',
        '^2': '²', '^3': '³', '^n': 'ⁿ', '_1': '₁', '_2': '₂', '_3': '₃',
        '\\langle': '⟨', '\\rangle': '⟩', '\\ket': '|', '\\bra': '⟨'
    }

    # 先全局处理 \frac
    text = re.sub(r'\\frac\{([^}]*)\}\{([^}]*)\}', r'(\1)/(\2)', text)

    # 处理行内公式 $...$
    def replace_inline_latex(match):
        formula = match.group(1)
        # 按长度降序替换，避免前缀冲突
        for latex in sorted(latex_symbols.keys(), key=len, reverse=True):
            formula = formula.replace(latex, latex_symbols[latex])
        return formula

    # 处理块级公式 $$...$$
    def replace_block_latex(match):
        formula = match.group(1).strip()
        # 按长度降序替换，避免前缀冲突
        for latex in sorted(latex_symbols.keys(), key=len, reverse=True):
            formula = formula.replace(latex, latex_symbols[latex])
        return "\n" + formula + "\n"

    # 处理 |ψ⟩ 这样的量子态符号
    text = re.sub(r'\|([^>]+)\\rangle', r'|\1⟩', text)
    text = re.sub(r'\\langle([^|]+)\|', r'⟨\1|', text)

    # 应用替换规则
    text = re.sub(r'\$\$(.*?)\$\$', replace_block_latex, text, flags=re.DOTALL)
    text = re.sub(r'\$(.*?)\$', replace_inline_latex, text)

    # 全局替换未在 $ 内的 LaTeX 命令
    for latex, unicode in sorted(latex_symbols.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(latex, unicode)

    return text

def response(model_manager, user_input, return_raw):
    """
    流式获取模型回复并使用 Rich 渲染 Markdown 输出到终端。
    自动按段落（以空行分隔）分块渲染，支持表格、列表、代码块及保留 <think> 标签。
    支持简单的 LaTeX 数学公式渲染。
    """
    console = Console()
    raw_response = ""
    buf = ""
    for chunk in model_manager.stream_response(user_input):
        raw_response += chunk
        buf += chunk
        # 渲染完整段落
        while "\n\n" in buf:
            part, buf = buf.split("\n\n", 1)
            escaped = part.replace("<think>", "`<think>`\n").replace("</think>", "\n`</think>`")
            # 处理 LaTeX 公式
            escaped = process_latex(escaped)
            console.print(Markdown(escaped, justify="left"))
    # 渲染剩余内容
    if buf.strip():
        escaped = buf.replace("<think>", "`<think>`").replace("</think>", "`</think>`")
        # 处理 LaTeX 公式
        escaped = process_latex(escaped)
        console.print(Markdown(escaped, justify="left"))

    if return_raw:
        return raw_response
    else:
        return 0