# Viby Usage Examples

This document provides detailed usage examples for Viby to help you make the most of its capabilities.

## Table of Contents

- [Viby Usage Examples](#viby-usage-examples)
  - [Table of Contents](#table-of-contents)
  - [Basic Usage](#basic-usage)
  - [Interactive Chat Mode](#interactive-chat-mode)
  - [Pipe Input](#pipe-input)
  - [Shell Command Generation](#shell-command-generation)
  - [History Management](#history-management)
  - [MCP Tool Integration](#mcp-tool-integration)
    - [Configuring MCP Servers](#configuring-mcp-servers)
  - [Embeddings and Tool Discovery](#embeddings-and-tool-discovery)
  - [Keyboard Shortcuts](#keyboard-shortcuts)
  - [Language Switching](#language-switching)
  - [Multi-Model Support](#multi-model-support)
  - [Configuration](#configuration)

## Basic Usage

The simplest way to use Viby is to directly ask questions:

```sh
yb "Write a binary search algorithm in Python"
```

You can also use the explicit `vibe` command:

```sh
# Basic Q&A
yb vibe "Write a binary search algorithm in Python"

# Direct run as default command - with explicit "vibe" command
yb vibe Recommend some Python learning resources
```

## Interactive Chat Mode

Interactive mode allows you to have multi-turn continuous conversations, with all context from the session preserved:

```sh
# Start interactive chat
yb --chat
# or
yb -c

|> Introduce machine learning
# -> [AI explains machine learning]

|> What's the difference between supervised and unsupervised learning?
# -> [AI explains differences, utilizing previous context]

|> exit
# or use Ctrl+D to exit chat mode
```

## Pipe Input

Viby can receive input data from pipes:

```sh
# Analyze git diff
git diff | yb vibe "What are the main changes in this code?"

# Read file content and analyze
cat complex_code.py | yb vibe "Simplify this code"

# Analyze command output
ls -la | yb vibe "Which files were modified recently?"

# Use redirect input
yb vibe "Summarize this article" < article.txt
```

## Shell Command Generation

Viby can automatically analyze your question and generate appropriate Shell commands:

```sh
# Find large files
yb vibe "Find the 5 largest files on my system"
# -> find / -type f -exec du -h {} \; | sort -rh | head -n 5
# -> [r]un, [e]dit, cop[y], [c]hat, [q]uit (default: run): 

# Generate and directly execute command
yb vibe "Compress all log files in the current directory"
# -> tar -czvf logs.tar.gz *.log
# -> Press Enter to execute, or choose other options
```

You can also use Shell command magic to pass current environment information to Viby:

```sh
# Analyze current directory contents
yb vibe "$(ls -la) Explain what these files are for"

# Combine multiple command outputs
yb vibe "$(ps aux | grep python) $(free -h) Which Python processes are using the most memory?"

# Analyze Git repository status
yb vibe "$(git status) $(git log --oneline -5) What should I do next?"
```

## History Management

Viby provides complete history management functionality:

```sh
# List recent interaction history (default 10)
yb history list

# List more history records
yb history list --limit 20

# Search history by filter criteria
yb history search "Python"

# Export history to a file
yb history export history.json

# Export history for a specific time range
yb history export --from "2024-01-01" --to "2024-01-31" jan_history.json

# View Shell commands generated and executed through Viby
yb history shell

# Clear all history (will prompt for confirmation)
yb history clear
```

## MCP Tool Integration

Viby integrates with MCP (Model Context Protocol) to use various powerful tools:

```sh
# Automatic tool usage
yb vibe "What's the weather like in Paris right now?"
# -> [AI uses weather tool, returns real-time weather information]

# Using TaviyAI search tool
yb vibe "Recent research advances in quantum computing"
# -> [AI uses Tavily search tool to get latest information]
```

### Configuring MCP Servers

```sh
# Enable MCP tools in interactive configuration
yb --config
# Select MCP settings section and enable
```

## Embeddings and Tool Discovery

Viby uses embedding models for semantic search of tools, enabling intelligent tool discovery:

```sh
# Download embedding model (needed before first use)
yb tools embed download

# Start embedding server (needed for tool discovery)
yb tools embed start

# Check embedding server status
yb tools embed status

# Update tool embeddings
yb tools embed update

# List available tools
yb tools list

# Use specific tool (no embedding server needed)
yb tools use weather "Weather in Beijing"

# Stop embedding server
yb tools embed stop
```

## Keyboard Shortcuts

Viby provides convenient keyboard shortcut integration:

```sh
# Install keyboard shortcuts
yb shortcuts

# After installation, type something in the command line and press Ctrl+Q
git log  # press Ctrl+Q
# -> becomes: yb vibe git log
# -> [AI parses and explains the Git log]

# You can also type a question and use the shortcut
Analyze system memory usage  # press Ctrl+Q
# -> becomes: yb vibe Analyze system memory usage
```

Supported shells: Bash, Zsh, and Fish

## Language Switching

Viby supports multiple interface languages:

```sh
# Switch language in configuration
yb --config
# Then select language settings section
```

## Multi-Model Support

Viby supports using different models to handle different types of queries:

```sh
# Use thinking model for deep analysis
yb --think vibe "Analyze the time complexity of this algorithm and possible optimization directions"

# Use fast model for simple answers
yb --fast vibe "Translate 'Hello, World!' to Chinese"

# Set default model in configuration
yb --config
# Select model settings section
```

## Configuration

Set up Viby through the interactive configuration wizard:

```sh
# Launch configuration wizard
yb --config
```

The configuration wizard allows you to set:
- API keys and endpoints
- Default and fallback models
- Model parameters (temperature, max tokens, etc.)
- MCP tool integration options
- Interface language
- Embedding model settings

Configuration is saved in `~/.config/viby/config.yaml`, while MCP server configuration is stored in `~/.config/viby/mcp_servers.json`. 