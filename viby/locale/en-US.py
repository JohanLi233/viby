"""
English prompts and interface text
"""

# General prompts
GENERAL = {
    # Command line arguments related
    "app_description": "viby - A versatile command-line tool for interacting with large language models",
    "app_epilog": "Examples:\n  viby \"What is the Fibonacci sequence?\"\n  git diff | viby \"Help me write a commit message\"\n  viby --shell \"Find all json files in current directory\"\n",
    "prompt_help": "Prompt content to send to the model",
    "chat_help": "Start an interactive chat session with the model",
    "shell_help": "Generate and optionally execute shell commands",
    "mcp_help": "Use MCP (Model Context Protocol) tools to solve problems",
    "server_help": "Specify MCP server path or URL (default: simple_server.py)",
    "config_help": "Launch interactive configuration wizard",
    
    # Interface text
    "generating": "[AI is generating response...]",
    "operation_cancelled": "Operation cancelled.",
    "copy_success": "Content copied to clipboard!",
    "copy_fail": "Copy failed: {0}",
    
    # Error messages
    "config_load_error": "Warning: Could not load config from {0}: {1}",
    "config_save_error": "Warning: Could not save config to {0}: {1}",
    "help_text": "show this help message and exit",

    # LLM Response
    "llm_empty_response": "Model did not return any content, please check your config",
}

# Configuration wizard related
CONFIG_WIZARD = {
    "model_qwen3": "qwen3:30b",
    "model_deepseek": "deepseek-v3",
    "model_gpt4o": "gpt-4o",
    "model_custom": "custom",
    # Headers and titles
    "header_title": "Viby Configuration Wizard",
    "checking_chinese": "Checking if terminal supports Chinese...",
    
    # Input validation
    "invalid_number": "Please enter a valid number!",
    "number_range_error": "Please enter a number between 1-{0}!",
    "url_error": "URL must start with http:// or https://!",
    "input_error": "Input error! Please choose from: {0}",
    "temperature_range": "Temperature must be between 0.0 and 1.0!",
    "invalid_decimal": "Please enter a valid decimal number!",
    "tokens_positive": "Token count must be greater than 0!",
    "invalid_integer": "Please enter a valid integer!",
    "timeout_positive": "Timeout must be greater than 0!",
    
    # Prompts
    "language_prompt": "Please select interface language:",
    "selected_language": "Selected English interface",
    "model_prompt": "Select default model",
    "temperature_prompt": "Temperature (0.0-1.0)",
    "max_tokens_prompt": "Maximum tokens",
    "api_url_prompt": "API base URL",
    "api_timeout_prompt": "API timeout (seconds)",
    "api_key_prompt": "API key (if needed)",
    "custom_model_prompt": "Select default model (custom)",
    "config_saved": "Configuration saved to",
    "continue_prompt": "Press Enter to continue...",
}

# Shell command related
SHELL = {
    "command_prompt": "Please generate a single shell ({1}) command for: {0} (OS: {2}). Only return the command itself, no explanations, no markdown.",
    "generating_command": "[AI is generating command...]",
    "execute_prompt": "Execute command│  {0}  │?",
    "choice_prompt": "[r]run, [e]edit, [y]copy, [c]chat, [q]quit (default: run): ",
    "edit_prompt": "Edit command (original: {0}):\n> ",
    "executing": "Executing command: {0}",
    "command_complete": "Command completed [Return code: {0}]",
    "command_error": "Command execution error: {0}",
    "continue_chat": "Continuing chat with AI to improve the command...",
    "command_generated": "Generated command: {0}",
    "improve_command_prompt": "Improve this command: {0}, User feedback: {1}",
}

# Chat dialog related
CHAT = {
    "welcome": "Welcome to Viby chat mode, type 'exit' to end conversation",
    "input_prompt": "|> "
}

# MCP tool related
MCP = {
    # GetToolsNode
    "getting_tools": "🔍 Getting available tools...",
    "tools_error": "\nError: Failed to get MCP tools: {0}",
    "format_server_tools": "Server '{0}':\n{1}\n",
    
    # DecideToolNode
    "analyzing": "🤔 Analyzing question and deciding which tool to use...",
    "system_prompt": "You are a helpful assistant that can use tools to solve problems.",
    "tool_prompt": """\n### CONTEXT\nYou are an assistant that can use tools via Model Context Protocol (MCP).\n\n### AVAILABLE SERVERS AND TOOLS\n{0}\n\n### TASK\nAnswer this question: \"{1}\"\n\n## NEXT ACTION\nAnalyze the question, extract any numbers or parameters, and decide which server and tool to use.\nReturn your response in this format:\n\n```yaml\nserver: <name of the server to use>\ntool: <name of the tool to use>\nparameters:\n    <parameter_name>: <parameter_value>\n    <parameter_name>: <parameter_value>\n```""",
    "parsing_error": "❌ Error parsing LLM response: {0}",
    "selected_tool": "💡 Selected tool: {0}",
    "selected_server": "🖥️ Selected server: {0}",
    "extracted_params": "🔢 Extracted parameters: {0}",
    
    # ExecuteToolNode
    "executing_tool": "🔧 Executing tool '{0}' with parameters: {1}",
    "auto_selecting_server": "🔄 Auto-selecting server: {0}",
    "execution_error": "\n❌ Tool execution error: {0}",
    "error_message": "Error executing tool: {0}",
    "result": "✅ Result: {0}"
}
