# viby

[![GitHub Repo](https://img.shields.io/badge/GitHub-viby-181717?logo=github)](https://github.com/JohanLi233/viby)
[![PyPI version](https://img.shields.io/pypi/v/viby?color=brightgreen)](https://pypi.org/project/viby/)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/release/python-3100/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![UV](https://img.shields.io/badge/UV-Package%20Manager-blueviolet)](https://github.com/astral-sh/uv)
[![MCP](https://img.shields.io/badge/MCP-Compatible-brightgreen)](https://github.com/estitesc/mission-control-link)

[English](https://github.com/JohanLi233/viby/blob/main/README.md) | 中文

一个用于与大语言模型交互的多功能命令行工具。

## 功能特点

- 提问并获取 AI 生成的答案
- 交互式对话模式进行多轮对话
- 生成 shell 命令及其解释
- 处理管道输入（例如：来自 git diff 的内容）
- 支持Open AI 格式接口调用

## 安装

```sh
pip install viby
```

## 使用示例

### 基本提问

```sh
yb "用python写一个快速排序"
# -> 当然可以！下面是一个用 **Python** 实现的 **快速排序（Quick Sort）** 算法：
```

### 交互式对话模式

```sh
yb -c
|> 解释一下量子计算的基本原理
# -> [AI 回复关于量子计算的解释]
|> 它在实际中有哪些应用？
# -> [AI 提供后续相关信息]
```

### 处理管道内容

```sh
git diff | yb "生成一个commit message"
# -> 在README中新增了信息
```

```sh
yb 这个项目是关于什么的 < README.md 
# -> 这个项目是关于...
```

### 生成 shell 命令

```sh
yb -s "我写了多少行python代码"
# -> find . -type f -name "*.py" | xargs wc -l
# -> [r]运行, [e]编辑, [y]复制, [c]对话, [q]放弃 (默认: 运行): 
```

### 使用MCP工具

```sh
yb -t "现在几点了？"
# -> [AI使用时间工具获取当前时间]
# -> "datetime": "2025-05-03T00:49:57+08:00",
```

## 配置

Viby 从 `~/.config/viby/config.json` 读取配置。你可以在此设置模型和参数。

### MCP服务器配置

Viby支持模型上下文协议(MCP)服务器以提供扩展功能。MCP配置存储在 `~/.config/viby/mcp_servers.json` 文件中。

## 语言切换

Viby 默认使用英文界面。首次启动或通过 `--config` 参数可以进入交互式配置向导，在其中选择中文或其他支持的语言。

- 默认语言：English (en-US)
- 切换到中文：在配置向导中选择 `中文 (zh-CN)` 即可。

**示例：**

```sh
yb --config
# 按提示选择语言（中文或英文）
```
