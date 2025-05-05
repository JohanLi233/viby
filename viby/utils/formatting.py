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
    LaTeX 渲染，将常见 LaTeX 数学符号转换为终端可显示的 Unicode。
    """
    text = text.replace("\\left", "").replace("\\right", "")

    latex_symbols = {
        "\\Gamma": "Γ", "\\Delta": "Δ", "\\Theta": "Θ", "\\Lambda": "Λ", "\\Xi": "Ξ",
        "\\Pi": "Π", "\\Sigma": "Σ", "\\Phi": "Φ", "\\Psi": "Ψ", "\\Omega": "Ω",
        "\\alpha": "α", "\\beta": "β", "\\gamma": "γ", "\\delta": "δ", "\\epsilon": "ε",
        "\\zeta": "ζ", "\\eta": "η", "\\theta": "θ", "\\iota": "ι", "\\kappa": "κ",
        "\\lambda": "λ", "\\mu": "μ", "\\nu": "ν", "\\xi": "ξ", "\\omicron": "ο",
        "\\pi": "π", "\\rho": "ρ", "\\sigma": "σ", "\\tau": "τ", "\\upsilon": "υ",
        "\\phi": "φ", "\\chi": "χ", "\\psi": "ψ", "\\omega": "ω",
        "\\infty": "∞", "\\approx": "≈", "\\neq": "≠", "\\leq": "≤", "\\geq": "≥",
        "\\le": "≤", "\\ge": "≥", "\\pm": "±",
        "\\times": "×", "\\cdot": "·",
        "\\rightarrow": "→", "\\leftarrow": "←", "\\to": "→",
        "\\Rightarrow": "⇒", "\\Leftarrow": "⇐",
        "\\subset": "⊂", "\\supset": "⊃", "\\subseteq": "⊆", "\\supseteq": "⊇",
        "\\in": "∈", "\\notin": "∉", "\\cup": "∪", "\\cap": "∩", "\\emptyset": "∅",
        "\\forall": "∀", "\\exists": "∃", "\\neg": "¬", "\\land": "∧", "\\lor": "∨",
        "\\sqrt": "√", "\\sum": "∑", "\\prod": "∏", "\\int": "∫", "\\partial": "∂", "\\nabla": "∇",
        "\\sin": "sin", "\\cos": "cos", "\\tan": "tan",
        "\\ldots": "…", "\\cdots": "⋯",
        "\\langle": "⟨", "\\rangle": "⟩", "\\ket": "|", "\\bra": "⟨",
        "\\,": "", "\\;": " ", "\\:": "", "\\!": "", "\\quad": "", "\\qquad": ""
    }

    # 先全局处理 \frac{a}{b} -> (a)/(b)
    text = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1)/(\2)", text)

    # 超/下标映射
    supers = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
        '+': '⁺', '-': '⁻', '=': '⁼', '(': '⁽', ')': '⁾',
        'n': 'ⁿ', 'i': 'ⁱ', 'k': 'ᵏ', 'm': 'ᵐ', 'o': 'ᵒ',
        'p': 'ᵖ', 'r': 'ʳ', 's': 'ˢ', 't': 'ᵗ', 'u': 'ᵘ',
        'v': 'ᵛ', 'x': 'ˣ', 'y': 'ʸ', 'z': 'ᶻ'
    }
    subs = {
        '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄', '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
        '+': '₊', '-': '₋', '=': '₌', '(': '₍', ')': '₎',
        'n': 'ₙ', 'i': 'ᵢ', 'k': 'ₖ', 'm': 'ₘ', 'o': 'ₒ',
        'p': 'ₚ', 'r': 'ᵣ', 's': 'ₛ', 't': 'ₜ', 'u': 'ᵤ',
        'v': 'ᵥ', 'x': 'ₓ'
    }

    def _to_super(s: str) -> str:
        return "".join(supers.get(ch, ch) for ch in s)

    def _to_sub(s: str) -> str:
        return "".join(subs.get(ch, ch) for ch in s)

    # 行内公式 $...$
    def _replace_inline(match):
        formula = match.group(1)
        for latex in sorted(latex_symbols, key=len, reverse=True):
            formula = formula.replace(latex, latex_symbols[latex])
        return formula

    # 块级公式 $$...$$
    def _replace_block(match):
        formula = match.group(1).strip()
        for latex in sorted(latex_symbols, key=len, reverse=True):
            formula = formula.replace(latex, latex_symbols[latex])
        return "\n" + formula + "\n"

    # 处理量子态符号 |ψ⟩、⟨ψ|
    text = re.sub(r'\|([^>]+)\\rangle', r'|\1⟩', text)
    text = re.sub(r'\\langle([^|]+)\|', r'⟨\1|', text)

    # 应用公式替换
    text = re.sub(r'\$\$(.*?)\$\$', _replace_block, text, flags=re.DOTALL)
    text = re.sub(r'\$(.*?)\$', _replace_inline, text)

    # 全局符号替换（处理未包裹在 $ 中的命令）
    for latex, uni in sorted(latex_symbols.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(latex, uni)

    # 处理 ^{...}、_{...} 以及单字符 ^x/_x
    text = re.sub(r'\^\{([^}]+)\}', lambda m: _to_super(m.group(1)), text)
    text = re.sub(r'_\{([^}]+)\}', lambda m: _to_sub(m.group(1)), text)
    text = re.sub(r'\^([A-Za-z0-9+\-=])', lambda m: _to_super(m.group(1)), text)
    text = re.sub(r'_([A-Za-z0-9+\-=])', lambda m: _to_sub(m.group(1)), text)

    return text

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

def stream_render_response(model_manager, messages, tools=None):
    """
    流式获取模型回复并使用 Rich 渲染 Markdown 输出到终端。
    自动按段落（以空行分隔）分块渲染，支持表格、列表、代码块及保留 <think> 标签。
    支持简单的 LaTeX 数学公式渲染。
    显示 Markdown 链接的原始 URL。
    
    Args:
        model_manager: 模型管理器
        input: 消息列表或用户输入
        tools: 可选，要传递给模型的工具列表
    """
    console = Console()
    raw_response = ""
    buf = ""
    for chunk in model_manager.stream_response(messages, tools):
        raw_response += chunk
        # Ensure <think> tags occupy their own lines
        formatted_chunk = chunk.replace("<think>", "\n<think>\n").replace("</think>", "\n</think>\n")
        buf += formatted_chunk
        # 渲染完整段落
        while "\n\n" in buf:
            part, buf = buf.split("\n\n", 1)
            escaped = part.replace("<think>", "`<think>`").replace("</think>", "`</think>`")
            # 处理 LaTeX 公式
            escaped = process_latex(escaped)
            # 处理 Markdown 链接，使其显示原始 URL
            escaped = process_markdown_links(escaped)
            console.print(Markdown(escaped, justify="left"))
    # 渲染剩余内容
    if buf.strip():
        escaped = buf.replace("<think>", "`<think>`").replace("</think>", "`</think>`")
        # 处理 LaTeX 公式
        escaped = process_latex(escaped)
        # 处理 Markdown 链接，使其显示原始 URL
        escaped = process_markdown_links(escaped)
        console.print(Markdown(escaped, justify="left"))

    return raw_response