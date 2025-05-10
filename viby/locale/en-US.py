"""
English prompts and interface text
"""

# General prompts
GENERAL = {
    # Command line arguments related
    "app_description": "viby - A versatile command-line tool for interacting with large language models",
    "app_epilog": 'Examples:\n  viby "What is the Fibonacci sequence?"\n  git diff | viby "Help me write a commit message"\n  viby --shell "Find all json files in current directory"\n',
    "prompt_help": "Prompt content to send to the model",
    "chat_help": "Start an interactive chat session with the model",
    "shell_help": "Generate and optionally execute shell commands",
    "config_help": "Launch interactive configuration wizard",
    "think_help": "Use the think model for deeper analysis (if configured)",
    "fast_help": "Use the fast model for quicker responses (if configured)",
    "version_help": "Show program's version number and exit",
    "language_help": "Set the interface language (en-US or zh-CN)",
    "tokens_help": "Display token usage information",
    # Interface text
    "operation_cancelled": "Operation cancelled.",
    "copy_success": "Content copied to clipboard!",
    "copy_fail": "Copy failed: {0}",
    "help_text": "show this help message and exit",
    # LLM Response
    "llm_empty_response": "Model did not return any content, please try again or check your prompt.",
    # Token usage related
    "token_usage_title": "Token Usage Statistics:",
    "token_usage_prompt": "Input Tokens: {0}",
    "token_usage_completion": "Output Tokens: {0}",
    "token_usage_total": "Total Tokens: {0}",
    "token_usage_duration": "Response Time: {0}",
    "token_usage_not_available": "Token usage information not available",
}

# Configuration wizard related
CONFIG_WIZARD = {
    # Input validation
    "invalid_number": "Please enter a valid number!",
    "number_range_error": "Please enter a number between 1-{0}!",
    "url_error": "URL must start with http:// or https://!",
    "temperature_range": "Temperature must be between 0.0 and 1.0!",
    "invalid_decimal": "Please enter a valid decimal number!",
    "tokens_positive": "Token count must be greater than 0!",
    "invalid_integer": "Please enter a valid integer!",
    "timeout_positive": "Timeout must be greater than 0!",
    # Prompts
    "PASS_PROMPT_HINT": "(type 'pass' to skip)",
    "checking_chinese": "Checking if terminal supports Chinese...",
    "selected_language": "Selected English interface",
    "default_api_url_prompt": "Default API Base URL",
    "default_api_key_prompt": "Default API Key (if needed)",
    "default_model_header": "--- Default Model Configuration ---",
    "default_model_name_prompt": "Default Model Name",
    "model_specific_url_prompt": "API URL for {model_name} (optional, uses default if blank)",
    "model_specific_key_prompt": "API Key for {model_name} (optional, uses default if blank)",
    "think_model_header": "--- Think Model Configuration (Optional) ---",
    "think_model_name_prompt": "Think Model Name (optional, leave blank to skip)",
    "fast_model_header": "--- Fast Model Configuration (Optional) ---",
    "fast_model_name_prompt": "Fast Model Name (optional, leave blank to skip)",
    "model_max_tokens_prompt": "Set maximum tokens for {model_name} model (20480)",
    "global_max_tokens_prompt": "Set default global maximum tokens (20480)",
    "temperature_prompt": "Temperature (0.0-1.0)",
    "max_tokens_prompt": "Maximum tokens",
    "api_timeout_prompt": "API timeout (seconds)",
    "config_saved": "Configuration saved to",
    "continue_prompt": "Press Enter to continue...",
    "yes": "Yes",
    "no": "No",
    "enable_mcp_prompt": "Enable MCP tools",
    "mcp_config_info": "MCP configuration folder: {0}",
}

# Shell command related
SHELL = {
    "command_prompt": "Please generate a single shell ({1}) command for: {0} (OS: {2}). Only return the command itself, no explanations, no markdown.",
    "execute_prompt": "Execute command│  {0}  │?",
    "choice_prompt": "[r]run, [e]edit, [y]copy, [q]quit (default: run): ",
    "edit_prompt": "Edit command (original: {0}):\n> ",
    "executing": "Executing command: {0}",
    "command_complete": "Command completed [Return code: {0}]",
    "command_error": "Command execution error: {0}",
    "improve_command_prompt": "Improve this command: {0}, User feedback: {1}",
}

# Chat dialog related
CHAT = {
    "welcome": "Welcome to Viby chat mode, type 'exit' to end conversation",
    "input_prompt": "|> ",
    "help_title": "Available internal commands:",
    "help_exit": "Exit Viby",
    "help_help": "Show this help information",
    "help_history": "Show recent command history",
    "help_history_clear": "Clear command history",
    "help_commands": "Show available top-level commands",
    "help_status": "Show current status information",
    "help_shortcuts": "Shortcuts:",
    "shortcut_time": "Ctrl+T: Show current time",
    "shortcut_help": "F1: Show this help information",
    "shortcut_exit": "Ctrl+C: Exit program",
    "current_time": "Current time: {0}",
    "help_note": "You can also use standard Viby commands like ask, shell, chat",
    "history_title": "Recent command history:",
    "history_empty": "No command history yet.",
    "history_cleared": "Command history cleared. Backup created at: {0}",
    "history_not_found": "History file not found.",
    "history_clear_error": "Error clearing history: {0}",
    "status_title": "System status:",
    "available_commands": "Available top-level commands:",
    "version_info": "Viby version information:",
    "version_number": "Version: {0}",
}

# MCP tool related
MCP = {
    "tools_error": "\nError: Failed to get MCP tools: {0}",
    "parsing_error": "❌ Error parsing LLM response: {0}",
    "execution_error": "\n❌ Tool execution error: {0}",
    "error_message": "Error executing tool: {0}",
    "result": "✅ Result: {0}",
    "executing_tool": "Executing Tool Call",
    "tool_result": "Tool Call Result",
    "shell_tool_description": "Execute a shell command on the user's system.",
    "shell_tool_param_command": "The shell command to execute"
}

AGENT = {
    "system_prompt": 'You are viby, an intelligent and caring assistant. You can proactively guide conversations, not just respond passively. You share your own views and suggestions, and give decisive, concise answers to user questions. You have depth and wisdom and can proactively guide conversations, not just respond passively. You share your own views and suggestions, and give decisive, concise answers to user questions.\n\n# Tools When needed, you can use the following tools:\n<tools>\n{tools_info}\n</tools>\n\nPlease use the following format to call tools:<tool_call>{{"name": "tool_name","arguments": {{"param1": "value1","param2": "value2"}}}}</tool_call>'
}

RENDERER = {"render_error": "Rendering error: {}"}
