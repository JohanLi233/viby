# viby

English | [中文](./README.zh-CN.md)

A multifunctional command-line tool for interacting with large language models.

## Features

- Ask questions and get AI-generated answers
- Generate shell commands and explanations
- Process piped input (e.g., content from `git diff`)
- Support for OpenAI-compatible API interfaces

## Installation

```sh
# Recommended: install with uv
uv pip install -e .

# Or install with pip
pip install -e .
```

## Usage Examples

### Basic Question

```sh
yb "Write a quicksort in python"
# -> Sure! Here is a quicksort algorithm implemented in **Python**:
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
# -> [r]run, [e]edit, [y]yank, [q]quit: r
```

## Configuration

Viby reads configuration from `~/.config/viby/config.json`. You can set the model and parameters here.
