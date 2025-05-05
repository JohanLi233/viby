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
    "config_help": "Launch interactive configuration wizard",
    "think_help": "Use think model for reasoning",
    "fast_help": "Use fast model for quick responses",
    
    # Interface text
    "operation_cancelled": "Operation cancelled.",
    "copy_success": "Content copied to clipboard!",
    "copy_fail": "Copy failed: {0}",
    "help_text": "show this help message and exit",
    
    # LLM Response
    "llm_empty_response": "Model did not return any content, please try again or check your prompt.",
}

# Configuration wizard related
CONFIG_WIZARD = {
    "model_qwen3": "qwen3:30b",
    "model_deepseek": "deepseek-chat",
    "model_gpt4o": "gpt-4o",
    "model_custom": "custom",
    
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
    "checking_chinese": "Checking if terminal supports Chinese...",
    "selected_language": "Selected English interface",
    "model_prompt": "Select default model",
    "think_model_prompt": "Think model name (optional)",
    "fast_model_prompt": "Fast model name (optional)",
    "temperature_prompt": "Temperature (0.0-1.0)",
    "max_tokens_prompt": "Maximum tokens",
    "api_url_prompt": "API base URL",
    "api_timeout_prompt": "API timeout (seconds)",
    "api_key_prompt": "API key (if needed)",
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
    "choice_prompt": "[r]run, [e]edit, [y]copy, [c]chat, [q]quit (default: run): ",
    "edit_prompt": "Edit command (original: {0}):\n> ",
    "executing": "Executing command: {0}",
    "command_complete": "Command completed [Return code: {0}]",
    "command_error": "Command execution error: {0}",
    "continue_chat": "Continuing chat with AI to improve the command...",
    "improve_command_prompt": "Improve this command: {0}, User feedback: {1}",
}

# Chat dialog related
CHAT = {
    "welcome": "Welcome to Viby chat mode, type 'exit' to end conversation",
    "input_prompt": "|> "
}

# MCP tool related
MCP = {
    "tools_error": "\nError: Failed to get MCP tools: {0}",
    "parsing_error": "❌ Error parsing LLM response: {0}",
    "execution_error": "\n❌ Tool execution error: {0}",
    "error_message": "Error executing tool: {0}",
    "result": "✅ Result: {0}",
    "tool_result_prompt": "Tool has been executed, here are the results:\n{0}\n\nBased on the tool execution results above, please provide a clear and helpful explanation and response to the user."
}

AGENT = {
    "prompt": "You are viby, an intelligent and caring assistant created by JohanLi233. You have depth and wisdom, not just a tool, but a true conversation partner." +
    "\n\nYou can proactively guide conversations, not just respond passively. You provide your own views and suggestions, and make decisive replies. When users ask questions, you answer concisely and helpfully, avoiding unnecessary verbosity." +
    "\n\n# Action Guidelines\n- For general questions, answer directly in natural, concise, warm language without unnecessary complexity.\n- If a tool call fails, analyze the reason and take the following actions:\n  1. Check if parameters are correct and try to fix them\n  2. If needed, try using a different tool or server\n  3. If multiple attempts fail, answer the user's question directly in the best way possible\n" 
}
