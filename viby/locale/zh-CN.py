"""
中文提示和界面文本
"""

# 通用提示
GENERAL = {
    # 命令行参数相关
    "app_description": "viby - 一个与大语言模型交互的多功能命令行工具",
    "app_epilog": "示例:\n  viby \"什么是斐波那契数列?\"\n  git diff | viby \"帮我写一个commit消息\"\n  viby --shell \"找当前目录下所有json文件\"\n",
    "prompt_help": "要发送给模型的提示内容",
    "shell_help": "生成并可选执行 shell 命令",
    "config_help": "启动交互式配置向导",
    
    # The following line is empty in the input text
    # 界面文本
    "generating": "[AI 正在生成回复...]",
    "operation_cancelled": "操作已取消。",
    "copy_success": "内容已复制到剪贴板！",
    "copy_fail": "复制失败: {0}",
    
    # 错误信息
    "config_load_error": "警告：无法从 {0} 加载配置：{1}",
    "config_save_error": "警告：无法保存配置到 {0}：{1}",
    # LLM相关
    "llm_empty_response": "【提示】模型没有返回任何内容，请尝试重新提问或检查您的提示。",
}

# 配置向导相关
CONFIG_WIZARD = {
    # 模型名称本地化
    "model_qwen3": "qwen3:30b",
    "model_deepseek": "deepseek-v3",
    "model_gpt4o": "gpt-4o",
    "model_custom": "自定义",
    # 标题和提示
    "header_title": "Viby 配置向导",
    "checking_chinese": "正在检查终端是否支持中文...",
    
    # 输入验证
    "invalid_number": "请输入有效数字!",
    "number_range_error": "请输入 1-{0} 之间的数字!",
    "url_error": "URL 必须以 http:// 或 https:// 开头!",
    "input_error": "输入错误！请从以下选项中选择: {0}",
    "temperature_range": "温度值必须在 0.0 到 1.0 之间!",
    "invalid_decimal": "请输入有效的小数!",
    "tokens_positive": "令牌数必须大于 0!",
    "invalid_integer": "请输入有效的整数!",
    "timeout_positive": "超时时间必须大于 0!",
    
    # 提示文本
    "language_prompt": "请选择界面语言:",
    "selected_language": "已选择中文界面",
    "model_prompt": "选择默认模型",
    "temperature_prompt": "温度参数 (0.0-1.0)",
    "max_tokens_prompt": "最大令牌数",
    "api_url_prompt": "API 基础URL",
    "api_timeout_prompt": "API 超时时间(秒)",
    "api_key_prompt": "API 密钥(如需)",
    "custom_model_prompt": "选择默认模型 (自定义)",
    "config_saved": "配置已保存至",
    "continue_prompt": "按 Enter 键继续...",
}

# Shell 命令相关
SHELL = {
    "command_prompt": "请只生成一个用于：{0} 的 shell 命令。只返回命令本身，不要解释，不要 markdown。",
    "generating_command": "[AI 正在生成命令...]",
    "execute_prompt": "执行命令│  {0}  │?",
    "choice_prompt": "[r]运行, [e]编辑, [y]复制, [q]放弃 (默认: 放弃): ",
    "edit_prompt": "编辑命令（原命令: {0}）:\n> ",
    "executing": "执行命令: {0}",
    "command_complete": "命令完成 [返回码: {0}]",
    "command_error": "命令执行出错: {0}",
}
