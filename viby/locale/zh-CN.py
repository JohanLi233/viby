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
    
    # 界面文本
    "generating": "[AI 正在生成回复...]",
    "operation_cancelled": "操作已取消。",
    "copy_success": "内容已复制到剪贴板！",
    "copy_fail": "复制失败: {0}",
    
    # 错误信息
    "config_load_error": "警告：无法从 {0} 加载配置：{1}",
    "config_save_error": "警告：无法保存配置到 {0}：{1}",
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
