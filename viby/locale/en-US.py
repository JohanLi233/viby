"""
English prompts and interface text
"""

# General prompts
GENERAL = {
    # Command line arguments related
    "app_description": "viby - A versatile command-line tool for interacting with large language models",
    "app_epilog": "Examples:\n  viby \"What is the Fibonacci sequence?\"\n  git diff | viby \"Help me write a commit message\"\n  viby --shell \"Find all json files in current directory\"\n",
    "prompt_help": "Prompt content to send to the model",
    "shell_help": "Generate and optionally execute shell commands",
    "config_help": "Launch interactive configuration wizard",
    
    # Interface text
    "generating": "[AI is generating response...]",
    "operation_cancelled": "Operation cancelled.",
    "copy_success": "Content copied to clipboard!",
    "copy_fail": "Copy failed: {0}",
    
    # Error messages
    "config_load_error": "Warning: Could not load config from {0}: {1}",
    "config_save_error": "Warning: Could not save config to {0}: {1}",
}

# Shell command related
SHELL = {
    "command_prompt": "Please generate only a shell command for: {0}. Return only the command itself, no explanation, no markdown.",
    "generating_command": "[AI is generating command...]",
    "execute_prompt": "Execute command│  {0}  │?",
    "choice_prompt": "[r]run, [e]edit, [y]copy, [q]quit (default: quit): ",
    "edit_prompt": "Edit command (original: {0}):\n> ",
    "executing": "Executing command: {0}",
    "command_complete": "Command completed [Return code: {0}]",
    "command_error": "Command execution error: {0}",
}
