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
    "enable_tool_search_prompt": "Enable MCP tool search feature (intelligently select relevant tools based on query)",
    # Add embedding model configuration related text
    "embedding_model_header": "--- Embedding Model Configuration ---",
    "embedding_model_name_prompt": "Embedding Model Name",
    "embedding_cache_dir_prompt": "Embedding Model Cache Directory (optional, leave blank for default)",
    "embedding_update_choices": "On change, Manual",
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
    "execution_error": "\n❌ Error executing tool: {0}",
    "error_message": "Error executing tool: {0}",
    "result": "✅ Result: {0}",
    "executing_tool": "## Executing tool call",
    "tool_result": "Tool call result",
    "shell_tool_description": "Execute a shell command on the user's system",
    "shell_tool_param_command": "The shell command to execute",
    # Tool retrieval
    "tool_retrieval_description": "Search for most relevant MCP tools based on user query, returning tool names, descriptions, parameters, and similarity scores",
    "tool_retrieval_param_query": "Search query text describing needed tool functionality or user needs",
    "tool_retrieval_param_top_k": "Number of most relevant tools to return, default is 5",
    # Update embeddings
    "update_tool_embeddings_description": "Update tool embeddings. Regenerates all tool embeddings",
}

# Tools management related
TOOLS = {
    "command_help": "Manage tools related commands",
    "update_embeddings_help": "Update MCP tool embeddings",
    "list_help": "List all available MCP tools",
    "subcommand_help": "Tool management subcommands",
    "subcommand_required": "A tool subcommand must be specified (e.g., embed, list)",
    # Embedding update
    "embeddings_update_title": "Embedding Update",
    "updating_embeddings": "Updating all tool embeddings",
    "mcp_not_enabled": "MCP functionality is not enabled, unable to retrieve tools",
    "collecting_tools": "Collecting MCP tools",
    "no_tools_found": "No MCP tools found",
    "start_updating_embeddings": "Starting to update embeddings for {tool_count} MCP tools...",
    "loading_embedding_model": "Loading sentence-transformer model",
    "model_load_complete": "Model loading complete",
    "model_load_empty": "Model loading failed, returned empty object",
    "model_load_failed": "Failed to load model",
    "clearing_cache": "Clearing existing cache, regenerating embeddings...",
    "embedding_model_load_failed": "Failed to load embedding model, cannot generate embeddings",
    "embeddings_already_updated": "Embeddings are already up to date, no update needed",
    "embeddings_update_success": "Tool embeddings have been successfully updated",
    "error_updating_embeddings": "Error updating embeddings",
    "embeddings_update_failed": "Embedding update failed",
    "updated_tools_table_title": "Updated Tools List",
    "tool_name_column": "Tool Name",
    "description_column": "Description",
    "param_count_column": "Parameters",
    "server_column": "Server",
    "description_unavailable": "[Description Unavailable]",
    "available_tools_table_title": "Available MCP Tools",
    "error_listing_tools": "Error listing tools",
    "tools_listing_failed": "Failed to list tools",
    # Embedding server
    "embed_subcommand_help": "Embedding vector management subcommands",
    "embed_update_help": "Update embeddings for MCP tools",
    "embed_start_help": "Start the embedding model service",
    "embed_stop_help": "Stop the embedding model service",
    "embed_status_help": "Check the status of the embedding model service",
    "download_help": "Download embedding model",
    "embed_server_title": "Embedding Model Service",
    "starting_embed_server": "Starting embedding model server",
    "stopping_embed_server": "Stopping embedding model server",
    "checking_embed_server": "Checking embedding model server status",
    "downloading_embed_model": "Downloading embedding model",
    "embed_server_already_running": "Embedding model server is already running",
    "embed_server_not_running": "Embedding model server is not running",
    "starting_server": "Starting server",
    "stopping_server": "Stopping server",
    "embed_server_started": "Embedding model server started",
    "embed_server_stopped": "Embedding model server stopped",
    "embed_server_start_failed": "Failed to start embedding model server",
    "embed_server_stop_failed": "Failed to stop embedding model server",
    "error_starting_server": "Error starting server",
    "error_stopping_server": "Error stopping server",
    "embed_server_running": "Embedding model server is running",
    "embed_server_status_unknown": "Embedding model server status unknown",
    "embed_server_status_check_failed": "Failed to check embedding model server status",
    "error_checking_server": "Error checking server status",
    "embed_server_uptime": "Uptime",
    # New key-value pairs
    "using_embedding_server": "Using embedding model server to update embeddings",
    "embeddings_update_via_server_failed": "Failed to update embeddings via server",
    "trying_local_update": "Trying local update method",
    "using_local_update": "Using local method to update embeddings",
    "start_server_suggestion": "Please use 'yb tools embed start' command to start the embedding model server and try again",
    "retrieving_from_server": "Retrieving tool information from embedding model server",
    "reading_from_cache": "Reading tool information from local cache",
    "no_cached_tools": "No cached tool information found",
    "suggest_update_embeddings": "Please use 'yb tools embed' command first to update tool embeddings",
    "fallback_collect_tools": "Cannot read from cache, falling back to direct tool collection",
    "successfully_collected": "Successfully collected tool data",
    "fallback_to_cached": "Cannot directly collect tools, trying to read from cache",
    "cache_read_failed": "Failed to read tool information from cache",
    "total_tools": "Total tools",
    "tools_loaded_from_cache": "Tool information loaded from cache",
    "listing_tools": "Listing available tools",
    "tools_list_title": "Tools List",
    # Model download related
    "using_default_model": "Using default embedding model",
    "model_already_downloaded": "Model already downloaded",
    "model_not_downloaded": "Embedding model not downloaded yet",
    "download_model_suggestion": 'Please use "yb tools embed download" command to download the model first, then start the server',
    "downloading_model": "Downloading embedding model",
    "downloading": "Downloading",
    "model_download_success": "Model download successful",
    "model_download_failed": "Model download failed",
    "model_download_error": "Error downloading model",
    # New additions for embedding_manager.py
    "loaded_from_cache": "Loaded from cache",
    "tools_embeddings": "tool embeddings",
    "load_cache_failed": "Failed to load cache embeddings",
    "saving_to_cache": "About to save",
    "tools_to_cache": "tool information to cache",
    "tool_list": "Tool list",
    "save_count_mismatch": "Warning: Saved tool count mismatch!",
    "expected": "Expected",
    "actual": "Actual",
    "missing_tools": "Missing tools",
    "validate_error": "Error validating saved tool info",
    "saved_to_cache": "Saved",
    "tools_saved": "tool embeddings to cache",
    "save_cache_failed": "Failed to save embeddings to cache",
    "error_occurred": " error occurred",
    "get_tool_desc": "Getting tool",
    "description": "Description",
    "parameters": "Parameters",
    "get_param_desc": "Getting tool",
    "param": "parameter",
    "required_yes": "Yes",
    "required_no": "No",
    "required": "Required",
    "prepare_update": "Preparing to update",
    "tools_embedding": "tool embeddings",
    "generate_embedding_failed": "Failed to generate embedding vector",
    "no_embeddings": "No tool embeddings available, please call update_tool_embeddings first",
    "query_embedding_failed": "Query embedding generation failed",
    "tool_not_exist": "Tool",
    "not_in_tool_info": "does not exist in tool_info, skipping",
    # New additions for server.py
    "query_cannot_be_empty": "Query text cannot be empty",
    "search_failed": "Search failed",
    "no_mcp_tools": "No MCP tools available",
    "embedding_update": "Embedding update",
    "success": "successful",
    "failed": "failed",
    "update_status_failed": "Failed to update status file",
    "update_tools_failed": "Failed to update tools",
    "server_shutting_down": "Server is shutting down...",
    # New additions for client.py
    "read_status_failed": "Failed to read status file",
    "days": "days",
    "hours": "hours",
    "minutes": "minutes",
    "seconds": "seconds",
    "calc_uptime_failed": "Failed to calculate uptime",
    "check_status_failed": "Failed to check server status",
    "server_already_running": "Embedding model server is already running",
    "server_start_timeout": "Failed to start embedding model server: service not responding",
    "server_start_error": "Error starting server",
    "server_crashed": "Failed to start embedding model server: Server process exi",
    "server_not_running": "Embedding model server is not running",
    "embedding_server_not_running": "Embedding model server is not running, check if the model is downloaded",
    "sending_search_request": "Sending search request to embedding server",
    "search_success": "Search successful, found",
    "related_tools": "related tools",
    "status_code": "status code",
    "response": "response",
    "search_timeout": "Search request timed out",
    "connect_server_failed": "Failed to connect to embedding server",
    "call_server_failed": "Failed to call embedding model service",
    "embedding_server_not_running_cannot_update": "Embedding model server is not running, cannot update tools",
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
        "You can also search for available tools, and the tools retrieved are all available."
        "Always strive to solve the user's needs efficiently and thoroughly."
    )
}

RENDERER = {"render_error": "Rendering error: {}"}

# 命令相关
COMMANDS = {
    "unknown_subcommand": "unknown subcommand:{0}",
    "available_commands": "Available Commands:",
}
