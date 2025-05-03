<div align="center">
  <img src="./assets/viby-icon.svg" alt="Viby Logo" width="120" height="120">
</div>

# viby

[![GitHub Repo](https://img.shields.io/badge/GitHub-viby-181717?logo=github)](https://github.com/JohanLi233/viby)
[![PyPI version](https://img.shields.io/pypi/v/viby?color=brightgreen)](https://pypi.org/project/viby/)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/release/python-3100/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![UV](https://img.shields.io/badge/UV-Package%20Manager-blueviolet)](https://github.com/astral-sh/uv)
[![MCP](https://img.shields.io/badge/MCP-Compatible-brightgreen)](https://github.com/estitesc/mission-control-link)


English | [中文](https://github.com/JohanLi233/viby/blob/main/README.zh-CN.md)
Viby agent at your terminal

## Features

- Ask questions and get AI-generated answers
- Interactive chat mode for multi-turn conversations
- Generate shell commands and explanations
- Process piped input (e.g., content from `git diff`)
- Support for OpenAI-compatible API interfaces
- MCP (Model Context Protocol) tools integration for extended capabilities

## Installation

```sh
pip install viby
```
### OR install from source

```sh
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
yb -c
|> Tell me about quantum computing
# -> [AI responds about quantum computing]
|> What are the practical applications?
# -> [AI responds with follow-up information]
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
yb -s "How many lines of python code did I write?"
# -> find . -type f -name "*.py" | xargs wc -l
# -> [r]run, [e]edit, [y]copy, [c]chat, [q]quit (default: run): 
```

### Automatically Use MCP Tools When Needed

```sh
yb "What time is it now?"
# -> [AI uses time tool to get current time]
# -> "datetime": "2025-05-03T00:49:57+08:00"
```

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
