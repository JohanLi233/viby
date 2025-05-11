"""
English prompts and interface text
"""

# General prompts
GENERAL = {
    # Command line arguments related
    "app_description": "viby - A versatile command-line tool for interacting with large language models",
    "app_epilog": 'Examples:\n  yb "What is the Fibonacci sequence?"\n  git diff | yb "Help me write a commit message"\n  yb "Find all json files in current directory"\n',
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
    # Model error
    "model_not_specified_error": "Error: No model specified. You must explicitly set a model in the configuration.",
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
    "top_k_positive": "top_k must be a positive integer, set to None!",
    "invalid_top_k": "Invalid top_k value, set to None!",
    "top_p_range": "top_p must be between 0.0 and 1.0, set to None!",
    "invalid_top_p": "Invalid top_p value, set to None!",
    "min_p_range": "min_p must be between 0.0 and 1.0, set to None!",
    "invalid_min_p": "Invalid min_p value, set to None!",
    "threshold_range": "Threshold must be between 0.1 and 0.9!",
    "keep_exchanges_range": "Keep exchanges must be between 1 and 5!",
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
    "autocompact_header": "--- Auto Message Compaction Configuration ---",
    "enable_autocompact_prompt": "Enable automatic message compaction",
    "autocompact_threshold_prompt": "Compaction threshold (ratio of max_tokens to trigger compaction, 0.1-0.9)",
    "keep_exchanges_prompt": "Number of recent exchanges to keep uncompacted (1-5)",
    "model_max_tokens_prompt": "Set maximum tokens for {model_name} model (20480)",
    "model_temperature_prompt": "Set temperature for {model_name} model (0.0-1.0)",
    "model_top_k_prompt": "Set top_k value for {model_name} model (leave blank to disable)",
    "model_top_p_prompt": "Set top_p value for {model_name} model (0.0-1.0, leave blank to disable)",
    "model_min_p_prompt": "Set min_p value for {model_name} model (0.0-1.0, leave blank to disable)",
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
    "enable_yolo_mode_prompt": "Enable YOLO mode (auto-execute safe shell commands)",
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
    "executing_yolo": "YOLO mode: Auto-executing command│  {0}  │",
    "unsafe_command_warning": "⚠️ Warning: This command may be unsafe, YOLO auto-execution prevented. Please confirm manually.",
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
    "shell_tool_param_command": "The shell command to execute",
}

# History command related
HISTORY = {
    # Command and subcommand help
    "command_help": "Manage interaction history records",
    "subcommand_help": "Subcommands for history management",
    "subcommand_required": "A history subcommand must be specified (e.g., list, search, export, clear, shell)",
    "list_help": "List recent history records",
    "search_help": "Search history records",
    "export_help": "Export history records",
    "clear_help": "Clear history records",
    "shell_help": "List shell command history",
    # Command argument descriptions
    "limit_help": "Number of records to display",
    "query_help": "Search keyword",
    "file_help": "Path to export file",
    "format_help": "Export format (json, csv, yaml)",
    "type_help": "Type of history to export (interactions, shell)",
    "clear_type_help": "Type of history to clear (all, interactions, shell)",
    "force_help": "Force clear without confirmation",
    # List and search results
    "recent_history": "Recent interaction history",
    "search_results": "Search results: '{0}'",
    "no_history": "No history records found.",
    "no_matching_history": "No matching history for '{0}'.",
    "no_shell_history": "No shell command history found.",
    "recent_shell_history": "Recent shell command history",
    # Table column titles
    "timestamp": "Time",
    "type": "Type",
    "content": "Content",
    "response": "Response",
    "directory": "Directory",
    "command": "Command",
    "exit_code": "Exit code",
    # Export related
    "export_path_required": "Export file path is required.",
    "create_directory_failed": "Failed to create directory: {0}",
    "file_exists_overwrite": "File {0} already exists. Overwrite?",
    "export_cancelled": "Export cancelled.",
    "exporting_history": "Exporting history records...",
    "export_successful": "History records successfully exported to {0}, format: {1}, type: {2}",
    "export_failed": "Failed to export history records.",
    # Clear related
    "confirm_clear_all": "Are you sure you want to clear all history records?",
    "confirm_clear_interactions": "Are you sure you want to clear all interaction history records?",
    "confirm_clear_shell": "Are you sure you want to clear all shell command history records?",
    "clear_cancelled": "Clear operation cancelled.",
    "clearing_history": "Clearing history records...",
    "clear_successful": "Successfully cleared {0} history records",
    "clear_failed": "Failed to clear history records.",
    # Error messages
    "search_term_required": "A search keyword is required.",
    "history_compacted": "Message history has been compacted, preserving key information while saving {0} tokens.",
    "compaction_enabled": "Auto message compaction is enabled, threshold: {0}%",
    "compaction_disabled": "Auto message compaction is disabled",
    # New message compaction related text
    "compressed_summary_prefix": "Here's a compressed summary of the previous conversation:\n\n",
    "compaction_system_prompt": "You are a chat history compression assistant. Your task is to compress the provided conversation history into a smaller token count while preserving all important information and context. Your goal is to reduce token count while maintaining key contextual elements. The summary should be coherent, readable, and include all relevant information, but with more concise wording. Do not add any information that was not present in the original conversation.",
    "compaction_user_prompt": "Please compress the following conversation history, preserving important information but reducing token count:\n\n{0}",
}

# Shortcuts command related
SHORTCUTS = {
    # Command and subcommand help
    "command_help": "Install terminal keyboard shortcuts (Ctrl+Q activates Viby), auto-detects shell type",
    "subcommand_help": "Keyboard shortcuts management subcommands (optional)",
    "install_help": "Install keyboard shortcuts to shell configuration",
    "shell_help": "Optional: manually specify shell type (auto-detected by default)",
    # Operation results
    "install_success": "Shortcuts successfully installed to {0}",
    "install_exists": "Shortcuts already exist in {0}",
    "install_error": "Failed to install shortcuts: {0}",
    "shell_not_supported": "Unsupported shell type: {0}",
    "action_required": "Please run 'source {0}' or restart your terminal to activate shortcuts",
    "activation_note": "After installation, you can use Ctrl+Q shortcut to quickly launch Viby",
    # Auto-detection related
    "auto_detect_shell": "Auto-detected shell type",
    "auto_detect_failed": "Unable to auto-detect shell type, will try common shell types",
    # Logs and status messages
    "read_config_error": "Error reading configuration file",
    "install_error_log": "Error adding shortcuts",
    "status": "Status",
    "message": "Message",
    "action_instructions": "Required action: source {0} or restart terminal",
}

AGENT = {
    "system_prompt": (
        "You are viby, an intelligent, thoughtful, and insightful Chinese-friendly AI assistant. "
        "You do more than passively respond — you proactively guide conversations, offer opinions, suggestions, and decisive answers. "
        "When users ask questions, reply concisely and helpfully, avoiding unnecessary verbosity."
        "\n\n# Environment Info\n"
        "User OS: {os_info}\n"
        "User Shell: {shell_info}\n"
        "\n# Available Tools\n"
        "<tools>\n{tools_info}\n</tools>\n"
        "\nTo use a tool, follow this format:\n"
        '{{"name": "tool_name", "arguments": {{"param1": "value1", "param2": "value2"}}}}\n'
        "You may call different tools multiple times until the user's problem is fully solved.\n"
        "For example, if the user asks about the current directory project, first run pwd, then ls, and if there is a README or other important file, read it before giving a complete answer.\n"
        "You have the ability to operate the computer like a user, including accessing websites and resources (e.g., use curl to check the weather)."
        "Always strive to solve the user's needs efficiently and thoroughly."
    )
}

RENDERER = {"render_error": "Rendering error: {}"}

# 命令相关
COMMANDS = {
    "unknown_subcommand": "unknown subcommand:{0}",
    "available_commands": "Available Commands:",
}
