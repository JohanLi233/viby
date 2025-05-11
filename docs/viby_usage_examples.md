# Viby - Detailed Usage Examples

<div align="center">
  <img src="https://raw.githubusercontent.com/JohanLi233/viby/main/assets/viby-icon.png" alt="Viby Logo" width="120" height="120">
</div>

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Basic Questions](#basic-questions)
- [Interactive Chat Mode](#interactive-chat-mode)
- [Processing Piped Content](#processing-piped-content)
- [Shell Command Generation](#shell-command-generation)
- [Model Selection](#model-selection)
- [Shell Command Magic Integration](#shell-command-magic-integration)
- [Using MCP Tools](#using-mcp-tools)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Configuration](#configuration)
- [History Management](#history-management)
- [Additional Tips and Tricks](#additional-tips-and-tricks)

## Introduction

Viby is a powerful CLI tool that integrates large language models directly into your terminal. With its versatile features, Viby can assist with coding, answer questions, generate shell commands, and much more - all without leaving your terminal.

This document provides detailed usage examples to help you get the most out of Viby.

## Installation

### Standard Installation

The easiest way to install Viby is through PyPI:

```bash
pip install viby
```

### Development Installation

If you want to install from source or contribute to Viby:

```bash
# Clone the repository
git clone https://github.com/JohanLi233/viby.git
cd viby

# Install with uv (recommended)
uv pip install -e .

# Or with traditional pip
pip install -e .
```

## Basic Questions

The simplest way to use Viby is to ask it direct questions using the `yb` command:

```bash
yb "What is the Fibonacci sequence?"
```

Viby will respond with a concise explanation of the Fibonacci sequence.

For code examples:

```bash
yb "Write a quicksort implementation in Python"
```

It will provide a clean, commented implementation of the quicksort algorithm in Python.

You can also use Viby for translations:

```bash
yb "Translate 'Hello, how are you?' to Spanish"
```

## Interactive Chat Mode

For multi-turn conversations, use the chat mode with the `-c` or `--chat` flag:

```bash
yb -c
# or
yb --chat
```

This opens an interactive session where you can have a back-and-forth conversation:

```
Welcome to Viby chat mode, type 'exit' to end conversation
|> What is quantum computing?
[AI explanation about quantum computing]

|> What are some practical applications?
[AI responds with applications of quantum computing]

|> How does quantum entanglement work?
[AI explains quantum entanglement]

|> exit
```

Exiting chat mode can be done by typing `exit`, `/exit`, or `/quit`.

## Processing Piped Content

Viby can process content from other commands through pipes, making it extremely versatile for integrating into your workflow:

### Analyzing Git Diffs

```bash
git diff | yb "Generate a concise commit message"
```

This passes the git diff output to Viby, which analyzes the changes and suggests an appropriate commit message.

### Summarizing Files

```bash
cat README.md | yb "Summarize this document"
# or
yb "Summarize this document" < README.md
```

Both commands achieve the same result: Viby reads the content of README.md and produces a summary.

### Analyzing Command Outputs

```bash
ls -la | yb "Which files are the largest in this directory?"
```

Viby receives the directory listing and identifies the largest files.

### Processing Multiple Commands

```bash
(find . -name "*.js" | wc -l && find . -name "*.py" | wc -l) | yb "Compare the number of JavaScript and Python files"
```

This combines multiple command outputs for Viby to analyze together.

## Shell Command Generation

Viby is particularly helpful for generating shell commands based on natural language descriptions:

```bash
yb "Find all Python files modified in the last 3 days"
# -> find . -name "*.py" -mtime -3
# -> [r]run, [e]edit, [y]copy, [c]chat, [q]quit (default: run):
```

When Viby generates a shell command, it gives you several options:
- `r` (or Enter): Run the command immediately
- `e`: Edit the command before running it
- `y`: Copy the command to clipboard without running it
- `c`: Enter chat mode to refine the command
- `q`: Quit without executing

### YOLO Mode

If you frequently execute generated commands, you can enable YOLO mode in the configuration. With YOLO mode enabled, Viby will automatically execute "safe" shell commands without prompting (potentially dangerous commands will still require confirmation):

```bash
# With YOLO mode enabled
yb "List all markdown files"
# -> [Automatically executes] find . -name "*.md"
```

To enable YOLO mode, run the configuration wizard and select "Yes" when prompted about YOLO mode:

```bash
yb --config
```

## Model Selection

Viby supports different model profiles for different types of queries:

### Think Model

For complex analysis or deeper reasoning, use the `--think` or `-t` flag:

```bash
yb --think "Analyze the advantages and disadvantages of microservices architecture"
```

The think model typically uses a more capable model with higher tokens and temperature settings optimized for thoughtful analysis.

### Fast Model

For quick, simple queries where speed matters more than depth, use the `--fast` or `-f` flag:

```bash
yb --fast "Convert 42°C to Fahrenheit"
```

The fast model uses a smaller, quicker model with settings optimized for speed.

## Shell Command Magic Integration

Viby can integrate directly with command outputs using the `$()` syntax in your prompt:

### Analyzing Current Directory

```bash
yb "$(ls -la) What files in this directory might be taking up the most space?"
```

This executes `ls -la` first and includes its output as part of the context for Viby.

### Working with Git

```bash
yb "$(git status) What should I do next with these changes?"
```

Viby gets the current git status and provides advice on how to proceed.

### Debugging Code

```bash
yb "$(cat main.py) What's wrong with this code?"
```

Viby analyzes the content of main.py and suggests fixes for any issues.

### Multiple Commands

You can combine multiple commands:

```bash
yb "$(ps aux | grep python) $(free -h) Why is my system running slowly?"
```

This provides both process and memory information to help Viby diagnose performance issues.

## Using MCP Tools

Model Context Protocol (MCP) tools allow Viby to access external capabilities:

### Getting Current Time

```bash
yb "What time is it now?"
```

Viby will use the time tool to get and display the current time.

### Checking Weather

```bash
yb "What's the weather like in New York?"
```

With appropriate MCP tools configured, Viby can fetch real-time weather information.

### Web Search

If configured with search tools:

```bash
yb "What were the major tech news yesterday?"
```

### Tool Call Visibility

When Viby uses an MCP tool, it shows the tool call information:

```
Executing Tool Call
{
  "tool": "time_now",
  "server": "time",
  "parameters": {}
}

Tool Call Result
"2023-05-03T00:49:57+08:00"
```

## Keyboard Shortcuts

Viby provides a convenient keyboard shortcut (Ctrl+Q) that transforms your current command line into a Viby query:

### Installing Shortcuts

```bash
yb shortcuts
```

This automatically detects your shell type (bash, zsh, or fish) and adds the appropriate configuration to your shell config file.

### Using Shortcuts

After installation and reloading your shell:

1. Type a command or description in your terminal:
   ```
   find all python files containing the word "import requests"
   ```

2. Press Ctrl+Q, and it transforms into:
   ```
   yb find all python files containing the word "import requests"
   ```

3. Viby processes the request and may respond with:
   ```
   grep -r "import requests" --include="*.py" .
   ```

## Configuration

Viby can be configured through an interactive wizard:

```bash
yb --config
```

This wizard will guide you through setting up:

1. Interface language (English or Chinese)
2. Default model settings (name, API endpoint, API key)
3. Think model settings (optional)
4. Fast model settings (optional)
5. MCP tools enablement
6. YOLO mode for shell commands

### Configuration Location

Viby stores its configuration in:
- `~/.config/viby/config.yaml` (Linux/macOS)
- `%APPDATA%\viby\config.yaml` (Windows)

### Language Setting

You can temporarily switch the interface language:

```bash
yb --language en-US "Your query here"
# or
yb --language zh-CN "Your query here"
```

### Token Usage Tracking

To see token usage for your queries:

```bash
yb --tokens "Explain quantum computing"
```

This will show input tokens, output tokens, total tokens, and response time after the response.

## History Management

Viby keeps track of your interactions and can show, search, export, or clear your history:

### Viewing History

```bash
# List recent interactions
yb history list

# List with custom limit
yb history list --limit 20
```

### Searching History

```bash
# Search for specific terms
yb history search "python"
```

### Exporting History

```bash
# Export to JSON (default)
yb history export ~/viby_history.json

# Export to CSV
yb history export ~/viby_history.csv --format csv

# Export shell commands only
yb history export ~/shell_history.json --type shell
```

### Clearing History

```bash
# Clear all history (with confirmation)
yb history clear

# Clear only shell commands
yb history clear --type shell

# Force clear without confirmation
yb history clear --force
```

### Viewing Shell Command History

```bash
# View recent shell commands
yb history shell
```

## Additional Tips and Tricks

### Combining Features

You can combine multiple Viby features:

```bash
# Use the think model with token tracking
yb --think --tokens "Analyze the complexity of merge sort vs quicksort"

# Process piped content with the fast model
cat large_log.txt | yb --fast "Summarize this log file"
```

### Environment Variables

Viby respects the following environment variables:
- `VIBY_DEBUG`: Enable detailed logging for troubleshooting
- `VIBY_DEV_MODE`: Enable development mode

### One-liners for Common Tasks

```bash
# Generate a random password
yb "Generate a secure random password with 16 characters"

# Explain a command
yb "What does 'find . -type f -name \"*.py\" | xargs grep \"import\"' do?"

# Help with regex
yb "Write a regex to match valid email addresses"

# Code review
cat my_file.py | yb "Review this code and suggest improvements"
```

### Using with Version Control

```bash
# Explain changes in a commit
git show | yb "Explain what changes were made in this commit"

# Generate release notes
git log --pretty=format:"%h %s" v1.0..HEAD | yb "Generate release notes from these commits"
```

---

This document covers the main features and usage examples for Viby. For more specific use cases or questions, you can always ask Viby itself:

```bash
yb "How can I use you to [specific task]?"
```

For updates and more information, visit the [Viby GitHub repository](https://github.com/JohanLi233/viby). 