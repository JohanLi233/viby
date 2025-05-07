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
</p>

<p align="center">
  <a href="https://github.com/JohanLi233/viby/blob/main/README.md">English</a> | 
  <a href="https://github.com/JohanLi233/viby/blob/main/README.zh-CN.md">中文</a>
</p>

<!-- ## 🚀 Overview

Viby is a powerful AI agent that lives in your terminal, designed to solve virtually any task you throw at it. Whether you need code assistance, shell commands, information retrieval, or creative content - Viby vibes with your needs and delivers solutions instantly. -->

## ✨ Features

- **Intelligent Conversations** - Engage in natural multi-turn dialogues
- **Command Generation** - Get optimized shell commands
- **Pipeline Integration** - Process data from other commands (e.g., `git diff | viby "write a commit message"`)
- **MCP Tools** - Extended capabilities through Model Context Protocol integration

## 🔧 Installation

```sh
# Install from PyPI
pip install viby
```

### Alternative Installation

```sh
# Install from source with uv
uv pip install -e .
```

## Usage Examples

### Basic Question

```sh
yb "Write a quicksort in python"
# -> Sure! Here is a quicksort algorithm implemented in **Python**:
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
git diff | yb "Generate a commit message"
# -> Added information to the README
```

```sh
yb "What is this project about?" < README.md
# -> This project is about...
```

### Generate Shell Command

```sh
yb --shell "How many lines of python code did I write?"
# or
yb -s "How many lines of python code did I write?"
# -> find . -type f -name "*.py" | xargs wc -l
# -> [r]run, [e]edit, [y]copy, [c]chat, [q]quit (default: run): 
```

### Advanced Model Selection

```sh
# Use think model for complex analysis
yb --think "Analyze this complex algorithm and suggest optimizations"

# Use fast model for quick responses
yb --fast "Translate 'Hello, World!' to French"
```

### Automatically Use MCP Tools When Needed

```sh
yb "What time is it now?"
# -> [AI uses time tool to get current time]
# -> "datetime": "2025-05-03T00:49:57+08:00"
```

For more detailed examples and advanced usage, see the [Usage Examples](./docs/viby_usage_examples.md) documentation.

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