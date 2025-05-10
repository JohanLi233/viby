"""
中文提示和界面文本
"""

# 通用提示
GENERAL = {
    # 命令行参数相关
    "app_description": "viby - 一个与大语言模型交互的多功能命令行工具",
    "app_epilog": '示例:\n  viby "什么是斐波那契数列?"\n  git diff | viby "帮我写一个commit消息"\n  viby --shell "找当前目录下所有json文件"\n',
    "prompt_help": "要发送给模型的提示内容",
    "chat_help": "启动与模型的交互式对话会话",
    "shell_help": "生成并选择性执行Shell命令",
    "config_help": "启动交互式配置向导",
    "think_help": "使用思考模型进行更深入的分析（如果已配置）",
    "fast_help": "使用快速模型进行更快的响应（如果已配置）",
    "version_help": "显示程序版本号并退出",
    "language_help": "设置界面语言（en-US或zh-CN）",
    "tokens_help": "显示token使用情况",
    # 界面文本
    "operation_cancelled": "操作已取消。",
    "copy_success": "内容已复制到剪贴板！",
    "copy_fail": "复制失败: {0}",
    "help_text": "显示此帮助信息并退出",
    "invalid_command": "无效的命令",
    # LLM相关
    "llm_empty_response": "【提示】模型没有返回任何内容，请尝试重新提问或检查您的提示。",
    # Token使用相关
    "token_usage_title": "Token使用统计：",
    "token_usage_prompt": "输入Tokens: {0}",
    "token_usage_completion": "输出Tokens: {0}",
    "token_usage_total": "总Tokens: {0}",
    "token_usage_duration": "响应时间: {0}",
    "token_usage_not_available": "无法获取Token使用信息",
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
    "model_max_tokens_prompt": "为{model_name}模型设置最大令牌数 (20480)",
    "global_max_tokens_prompt": "设置默认全局最大令牌数 (20480)",
    "temperature_prompt": "温度参数 (0.0-1.0)",
    "max_tokens_prompt": "最大令牌数",
    "api_timeout_prompt": "API 超时时间(秒)",
    "config_saved": "配置已保存至",
    "continue_prompt": "按 Enter 键继续...",
    "yes": "是",
    "no": "否",
    "enable_mcp_prompt": "启用MCP工具",
    "mcp_config_info": "MCP配置文件夹：{0}",
    "enable_yolo_mode_prompt": "启用YOLO模式（自动执行安全的shell命令）",
}

# Shell 命令相关
SHELL = {
    "command_prompt": "请只生成一个用于：{0} 的 shell ({1}) 命令（操作系统：{2}）。只返回命令本身，不要解释，不要 markdown。",
    "execute_prompt": "执行命令│  {0}  │?",
    "choice_prompt": "[r]运行, [e]编辑, [y]复制, [q]放弃 (默认: 运行): ",
    "edit_prompt": "编辑命令（原命令: {0}）:\n> ",
    "executing": "执行命令: {0}",
    "command_complete": "命令完成 [返回码: {0}]",
    "command_error": "命令执行出错: {0}",
    "improve_command_prompt": "改进这个命令: {0}, 用户的反馈: {1}",
    "executing_yolo": "YOLO模式: 自动执行命令│  {0}  │",
    "unsafe_command_warning": "⚠️ 警告: 该命令可能不安全，已禁止YOLO自动执行。请手动确认执行。",
}

# 聊天对话相关
CHAT = {
    "welcome": "欢迎使用 Viby 对话模式，输入 'exit' 可退出对话",
    "input_prompt": "|> ",
    "help_title": "可用内部命令:",
    "help_exit": "退出Viby",
    "help_help": "显示此帮助信息",
    "help_history": "显示最近命令历史",
    "help_history_clear": "清除命令历史",
    "help_commands": "显示可用的顶级命令",
    "help_status": "显示当前状态信息",
    "help_shortcuts": "快捷键:",
    "shortcut_time": "Ctrl+T: 显示当前时间",
    "shortcut_help": "F1: 显示此帮助信息",
    "shortcut_exit": "Ctrl+C: 退出程序",
    "current_time": "当前时间: {0}",
    "help_note": "您也可以使用标准Viby命令，如ask、shell、chat",
    "history_title": "最近命令历史:",
    "history_empty": "还没有命令历史。",
    "history_cleared": "命令历史已清除。已创建备份：{0}",
    "history_not_found": "没有找到历史文件。",
    "history_clear_error": "清除历史时出错: {0}",
    "status_title": "系统状态:",
    "available_commands": "可用的顶级命令:",
    "version_info": "Viby 版本信息:",
    "version_number": "版本: {0}",
}

# MCP工具相关
MCP = {
    "tools_error": "\n错误: 无法获取MCP工具: {0}",
    "parsing_error": "❌ 解析LLM响应时出错: {0}",
    "execution_error": "\n❌ 执行工具时出错: {0}",
    "error_message": "执行工具时出错: {0}",
    "result": "✅ 结果: {0}",
    "executing_tool": "正在执行工具调用",
    "tool_result": "工具调用结果",
    "shell_tool_description": "在用户系统上执行shell命令",
    "shell_tool_param_command": "要执行的shell命令",
}

# 历史命令相关
HISTORY = {
    # 命令和子命令帮助
    "command_help": "管理交互历史记录",
    "subcommand_help": "历史管理的子命令",
    "subcommand_required": "必须指定一个历史子命令（如 list、search、export、clear、shell）",
    "list_help": "列出最近的历史记录",
    "search_help": "搜索历史记录",
    "export_help": "导出历史记录",
    "clear_help": "清除历史记录",
    "shell_help": "列出shell命令历史",
    # 命令参数描述
    "limit_help": "显示的记录数量",
    "query_help": "搜索关键词",
    "file_help": "导出文件的路径",
    "format_help": "导出格式 (json, csv, yaml)",
    "type_help": "导出的历史类型 (interactions, shell)",
    "clear_type_help": "要清除的历史类型 (all, interactions, shell)",
    "force_help": "强制清除，不提示确认",
    # 列表和搜索结果
    "recent_history": "最近交互历史",
    "search_results": "搜索结果：'{0}'",
    "no_history": "没有找到历史记录。",
    "no_matching_history": "没有找到匹配 '{0}' 的历史记录。",
    "no_shell_history": "没有找到Shell命令历史记录。",
    "recent_shell_history": "最近Shell命令历史",
    # 表格列标题
    "timestamp": "时间",
    "type": "类型",
    "content": "内容",
    "response": "回复",
    "directory": "目录",
    "command": "命令",
    "exit_code": "退出码",
    # 导出相关
    "export_path_required": "必须指定导出文件路径。",
    "create_directory_failed": "创建目录失败: {0}",
    "file_exists_overwrite": "文件 {0} 已存在，是否覆盖?",
    "export_cancelled": "导出已取消。",
    "exporting_history": "正在导出历史记录...",
    "export_successful": "历史记录已成功导出到 {0}，格式: {1}，类型: {2}",
    "export_failed": "导出历史记录失败。",
    # 清除相关
    "confirm_clear_all": "确定要清除所有历史记录吗?",
    "confirm_clear_interactions": "确定要清除所有交互历史记录吗?",
    "confirm_clear_shell": "确定要清除所有Shell命令历史记录吗?",
    "clear_cancelled": "清除操作已取消。",
    "clearing_history": "正在清除历史记录...",
    "clear_successful": "已成功清除 {0} 历史记录",
    "clear_failed": "清除历史记录失败。",
    # 错误信息
    "search_term_required": "必须提供搜索关键词。",
}

AGENT = {
    "system_prompt": (
        "你是 viby，一位智能、贴心且富有洞察力的中文 AI 助手。你不仅被动响应，更能主动引导对话，提出见解、建议和明确的决策。"
        "面对用户问题时，请用简明、实用的方式作答，避免冗余。"
        "\n\n# 环境信息\n"
        "用户操作系统: {os_info}\n"
        "用户Shell: {shell_info}\n"
        "\n# 可用工具\n"
        "<tools>\n{tools_info}\n</tools>\n"
        "\n如需使用工具，请遵循以下格式：\n"
        '<tool_call>{{"name": "工具名称", "arguments": {{"参数1": "值1", "参数2": "值2"}}}}</tool_call>\n'
        "你可多次调用不同的的工具，直到彻底解决用户问题。单是每次只能调用一个工具。\n"
        "例如，用户询问当前目录项目内容，你应先执行 pwd，再执行 ls，若有 README 等文件需进一步阅读后再完整答复。\n"
        "你具备像用户操作电脑一样的能力，可访问网站和各类资源（如查询天气可用 curl）。"
        "始终以高效、全面的流程解决用户需求。"
    )
}

# 渲染器相关信息
RENDERER = {"render_error": "渲染错误: {}"}

# 命令相关
COMMANDS = {
    "unknown_subcommand": "未知子命令：{0}",
    "available_commands": "可用命令：",
}
