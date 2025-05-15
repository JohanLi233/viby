<div align="center">
  <img src="https://raw.githubusercontent.com/JohanLi233/viby/main/assets/viby-icon.png" alt="Viby Logo" width="120" height="120">
  <h1>Viby</h1>
  <!-- <p><strong>Viby vibes everything</strong> - Your universal agent for solving any task</p> -->
  <p><strong>Viby vibes everything</strong></p>
</div>

<p align="center">
  <a href="https://github.com/JohanLi233/viby"><img src="https://img.shields.io/badge/GitHub-viby-181717?logo=github" alt="GitHub Repo"></a>
  <a href="https://pypi.org/project/viby/"><img src="https://img.shields.io/pypi/v/viby?color=brightgreen" alt="PyPI version"></a>
  <a href="https://www.python.org/downloads/release/python-3100/"><img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python Version"></a>
  <a href="https://www.gnu.org/licenses/gpl-3.0"><img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License: GPL v3"></a>
  <a href="https://github.com/astral-sh/uv"><img src="https://img.shields.io/badge/UV-Package%20Manager-blueviolet" alt="UV"></a>
  <a href="https://github.com/estitesc/mission-control-link"><img src="https://img.shields.io/badge/MCP-Compatible-brightgreen" alt="MCP"></a>
  <a href="https://deepwiki.com/JohanLi233/viby"><img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki"></a>
</p>

<p align="center">
  <a href="https://github.com/JohanLi233/viby/blob/main/README.md">English</a> |
  <a href="https://github.com/JohanLi233/viby/blob/main/README.zh-CN.md">中文</a>
</p>

## 🚀 Overview

Viby is a powerful AI agent that lives in your terminal, designed to solve virtually any task you throw at it. Whether you need code assistance, shell commands, information retrieval, or creative content - Viby vibes with your needs and delivers solutions instantly.

## ✨ Features

- **Intelligent Conversations** - Engage in natural multi-turn dialogues
- **Automatic Shell Command Generation** - Get optimized shell commands when needed
- **Pipeline Integration** - Process data from other commands (e.g., `git diff | viby "write a commit message"`)
- **MCP Tools** - Extended capabilities through Model Context Protocol integration
- **Smart Tool Discovery** - Automatically finds and uses the most relevant tools within configured MCP servers
- **Enhanced History Management** - Complete interaction history with search, export, and management
- **Multiple Model Support** - Configure and use different models for various tasks
- **Command Embeddings** - Semantic search in tools using embedded vectors for accurate tool selection
- **Multi-language Support** - Full interface in English and Chinese with easy language switching

![Viby Terminal Demo](https://raw.githubusercontent.com/JohanLi233/viby/main/assets/screenshot.png)

## 🔧 Installation

```sh
# Install from PyPI
pip install viby
# OR
uv tool install viby
```

### Alternative Installation

```sh
# Install from source with uv
uv pip install -e .
```

## Usage Examples

### Basic Question

```sh
yb vibe "Write a quicksort in python"
# -> Sure! Here is a quicksort algorithm implemented in **Python**:
```

### Simplified Command

```sh
yb "Write a quicksort in python"
# -> Same result as above
```

### Interactive Chat Mode

```sh
yb --chat
# or
yb -c
|> Tell me about quantum computing
# -> [AI responds about quantum computing]
|> What are the practical applications?
# -> [AI responds with follow-up information]
|> exit
```

### Process Piped Content

```sh
git diff | yb vibe "Generate a commit message"
# -> Added information to the README
```

```sh
yb vibe "What is this project about?" < README.md
# -> This project is about...
```

### Generate Shell Command

```sh
yb vibe "How many lines of python code did I write?"
# -> find . -type f -name "*.py" | xargs wc -l
# -> [r]run, [e]edit, [y]copy, [c]chat, [q]quit (default: run): 
```

### Advanced Model Selection

```sh
# Use think model for complex analysis
yb --think vibe "Analyze this complex algorithm and suggest optimizations"

# Use fast model for quick responses
yb --fast vibe "Translate 'Hello, World!' to French"
```

### Shell Command Magic Integration

```sh
# List directory contents
yb vibe "$(ls) What files are in the current directory?"
# -> The current directory contains: file1.txt, file2.py, directory1/...

# Analyze Git status
yb vibe "$(git status) Which files should I commit first?"

# View code files
yb vibe "$(cat main.py) How can I improve this code?"
```

### Smart Tool Discovery

```sh
# Viby will automatically discover and use relevant tools
yb vibe "What's the weather in San Francisco?"
# -> [Viby identifies and uses weather tools]
# -> The current weather in San Francisco is 68°F and partly cloudy...

# Embedding Model Management
# First download the embedding model (required once before using embedding features)
# Embed model configurable with yb --config
yb tools embed download

# Start the embedding server (required for tool discovery)
yb tools embed start

# Check embedding server status
yb tools embed status

# Update tool embeddings from configured MCP servers
yb tools embed update

# List available tools (udpate before listing)
yb tools list

# Stop the embedding server when not needed
yb tools embed stop
```

### History Management

```sh
# View recent interactions
yb history list

# Search your history
yb history search "python"

# Export your interaction history
yb history export history.json

# View shell command history
yb history shell

# Clear history (with confirmation)
yb history clear
```

### Automatically Use MCP Tools When Needed

```sh
yb vibe "What time is it now?"
# -> [AI uses time tool to get current time]
# -> "datetime": "2025-05-03T00:49:57+08:00"
```

### Keyboard Shortcuts

Viby provides a convenient keyboard shortcut (Ctrl+Q) that allows you to quickly use Viby with the current command line content:

```sh
# Install the keyboard shortcuts (auto-detects your shell)
yb shortcuts

# After installation, type any command and press Ctrl+Q
help me analyze my readme file  # Now press Ctrl+Q
# -> This transforms into: yb vibe help me analyze my readme file
# -> [AI analyzes and responds to question]
```

Supported shells:

- Bash
- Zsh
- Fish

After installing shortcuts, you'll need to reload your shell configuration (`source ~/.bashrc`, `source ~/.zshrc`, or equivalent) or restart your terminal for the shortcuts to take effect.

## Command Structure

Viby uses a simple command structure:

```
yb [OPTIONS] [COMMAND] [ARGS]...
```

Main commands:
- `yb [prompt]` - Ask a question (alias for `yb vibe "your question"`; **recommended**)
- `yb vibe "your question"` - Ask a question (default command for questions)
- `yb --chat` or `yb -c` - Start interactive chat mode
- `yb --think vibe "complex question"` - Use the think model for deeper analysis
- `yb --fast vibe "simple question"` - Use the fast model for quick responses
- `yb history` - Manage interaction history
- `yb tools` - Manage tool-related commands
- `yb shortcuts` - Install keyboard shortcuts

Use `yb --help` to see all available commands and options.

## Configuration

Viby reads configuration from `~/.config/viby/config.yaml`. You can set the model, parameters, and MCP options here.

### Interactive Configuration

Use the configuration wizard to set up your preferences:

```sh
yb --config
```

This allows you to configure:

- API endpoint and key
- Model
- Temperature and token settings
- MCP tools enablement
- Interface language
- Embedding model settings

### MCP Server Configuration

Viby supports Model Context Protocol (MCP) servers for extended capabilities. MCP configurations are stored in `~/.config/viby/mcp_servers.json`.

## ⭐ Star History

<div align="center">
  <a href="https://star-history.com/#JohanLi233/viby&Date">
    <img src="https://api.star-history.com/svg?repos=JohanLi233/viby&type=Date" alt="Star History Chart" style="max-width:100%;">
  </a>
</div>

## 📄 Documentation

- [Usage Examples](./docs/viby_usage_examples.md) - Detailed examples of all Viby features
- [Project Design Document](./docs/viby_project_design.md) - Technical architecture and design

## 🤝 Contributing

Contributions are welcome! Feel free to submit a Pull Request or create an Issue.
