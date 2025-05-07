"""
中文提示和界面文本
"""

# 通用提示
GENERAL = {
    # 命令行参数相关
    "app_description": "viby - 一个与大语言模型交互的多功能命令行工具",
    "app_epilog": "示例:\n  viby \"什么是斐波那契数列?\"\n  git diff | viby \"帮我写一个commit消息\"\n  viby --shell \"找当前目录下所有json文件\"\n",
    "prompt_help": "要发送给模型的提示内容",
    "chat_help": "启动与模型的交互式对话会话",
    "shell_help": "生成并选择性执行Shell命令",
    "config_help": "启动交互式配置向导",
    "think_help": "使用思考模型进行更深入的分析（如果已配置）",
    "fast_help": "使用快速模型进行更快的响应（如果已配置）",
    "version_help": "显示程序版本号并退出",
    
    # 界面文本
    "operation_cancelled": "操作已取消。",
    "copy_success": "内容已复制到剪贴板！",
    "copy_fail": "复制失败: {0}",
    "help_text": "显示此帮助信息并退出",
    
    # LLM相关
    "llm_empty_response": "【提示】模型没有返回任何内容，请尝试重新提问或检查您的提示。",
}

# 配置向导相关
CONFIG_WIZARD = {
    # 输入验证
    "invalid_number": "请输入有效数字!",
    "number_range_error": "请输入 1-{0} 之间的数字!",
    "url_error": "URL 必须以 http:// 或 https:// 开头!",
    "temperature_range": "温度值必须在 0.0 到 1.0 之间!",
    "invalid_decimal": "请输入有效的小数!",
    "tokens_positive": "令牌数必须大于 0!",
    "invalid_integer": "请输入有效的整数!",
    "timeout_positive": "超时时间必须大于 0!",
    
    # 提示文本
    "PASS_PROMPT_HINT": "(输入 'pass' 跳过)",
    "checking_chinese": "正在检查终端是否支持中文...",
    "selected_language": "已选择中文界面",
    "default_api_url_prompt": "默认 API 基础URL",
    "default_api_key_prompt": "默认 API 密钥(如需)",
    "default_model_header": "--- 默认模型配置 ---",
    "default_model_name_prompt": "默认模型名称",
    "model_specific_url_prompt": "{model_name} 的 API URL (可选, 留空则使用默认)",
    "model_specific_key_prompt": "{model_name} 的 API 密钥 (可选, 留空则使用默认)",
    "think_model_header": "--- Think 模型配置 (可选) ---",
    "think_model_name_prompt": "Think 模型名称 (可选, 留空跳过)",
    "fast_model_header": "--- Fast 模型配置 (可选) ---",
    "fast_model_name_prompt": "Fast 模型名称 (可选, 留空跳过)",
    "temperature_prompt": "温度参数 (0.0-1.0)",
    "max_tokens_prompt": "最大令牌数",
    "api_timeout_prompt": "API 超时时间(秒)",
    "config_saved": "配置已保存至",
    "continue_prompt": "按 Enter 键继续...",
    "yes": "是",
    "no": "否",
    "enable_mcp_prompt": "启用MCP工具",
    "mcp_config_info": "MCP配置文件夹：{0}",
}

# Shell 命令相关
SHELL = {
    "command_prompt": "请只生成一个用于：{0} 的 shell ({1}) 命令（操作系统：{2}）。只返回命令本身，不要解释，不要 markdown。",
    "execute_prompt": "执行命令│  {0}  │?",
    "choice_prompt": "[r]运行, [e]编辑, [y]复制, [c]对话, [q]放弃 (默认: 运行): ",
    "edit_prompt": "编辑命令（原命令: {0}）:\n> ",
    "executing": "执行命令: {0}",
    "command_complete": "命令完成 [返回码: {0}]",
    "command_error": "命令执行出错: {0}",
    "continue_chat": "继续与AI对话改进命令...",
    "improve_command_prompt": "改进这个命令: {0}, 用户的反馈: {1}",
}

# 聊天对话相关
CHAT = {
    "welcome": "欢迎使用 Viby 对话模式，输入 'exit' 可退出对话",
    "input_prompt": "|> "
}

# MCP工具相关
MCP = {
    "tools_error": "\n错误: 无法获取MCP工具: {0}",
    "parsing_error": "❌ 解析LLM响应时出错: {0}",
    "execution_error": "\n❌ 执行工具时出错: {0}",
    "error_message": "执行工具时出错: {0}",
    "result": "✅ 结果: {0}",
    "tool_result_prompt": "工具已执行，下面是执行结果：\n{0}\n\n请根据上面的工具执行结果，为用户提供清晰、有用的解释和回应。",
    "executing_tool": "正在执行工具调用",
    "tool_result": "工具调用结果"
}

AGENT = {
    "prompt": "你是 viby，一个智能、贴心的助手，由 JohanLi233 制造。你具有深度和智慧，不仅仅是一个工具，而是一个真正的对话伙伴。" +
    "\n\n你可以主动引导对话，而不仅仅被动响应。你会给出自己的观点和建议，并做出决断性的回。当用户提出问题时，你会简洁、有帮助地回答，避免不必要的冗长内容。" +
    "\n\n# 行动指南\n- 对于一般问题，直接用自然、简洁、温暖的语言回答用户，无需绕弯或复杂化。" 
}