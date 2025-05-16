<div align="center">
  <img src="https://raw.githubusercontent.com/JohanLi233/viby/main/assets/viby-icon.png" alt="Viby 图标" width="120" height="120">
  <h1>Viby</h1>
  <p><strong>Viby vibes everything</strong></p>
</div>

<p align="center">
  <a href="https://github.com/JohanLi233/viby"><img src="https://img.shields.io/badge/GitHub-viby-181717?logo=github" alt="GitHub 仓库"></a>
  <a href="https://pypi.org/project/viby/"><img src="https://img.shields.io/pypi/v/viby?color=brightgreen" alt="PyPI 版本"></a>
  <a href="https://www.python.org/downloads/release/python-3100/"><img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 版本"></a>
  <a href="https://www.gnu.org/licenses/gpl-3.0"><img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="许可证: GPL v3"></a>
  <a href="https://github.com/astral-sh/uv"><img src="https://img.shields.io/badge/UV-Package%20Manager-blueviolet" alt="UV"></a>
  <a href="https://github.com/estitesc/mission-control-link"><img src="https://img.shields.io/badge/MCP-Compatible-brightgreen" alt="MCP"></a>
  <a href="https://deepwiki.com/JohanLi233/Viby"><img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki"></a>
</p>

<p align="center">
  <a href="https://github.com/JohanLi233/viby/blob/main/README.md">English</a> | 
  <a href="https://github.com/JohanLi233/viby/blob/main/README.zh-CN.md">中文</a>
</p>

## 🚀 概述

Viby 是一个强大的人工智能体，它存在于你的终端中，旨在解决你抛给它的任何任务。无论你需要代码帮助、Shell 命令、信息检索还是创意内容 - Viby 都能与你的需求产生共鸣，并立即提供解决方案。

## ✨ 特性

- **智能对话** - 进行自然的多回合对话
- **自动Shell命令生成** - 在需要时自动获取优化的 Shell 命令
- **管道集成** - 处理来自其他命令的数据（例如，`git diff | viby "写一个提交消息"`）
- **MCP 工具** - 通过模型上下文协议集成扩展能力
- **智能工具发现** - 自动在配置的MCP服务器中查找并使用最相关的工具来回答您的查询
- **增强的历史记录管理** - 完整的交互历史，支持查询、搜索、导出和管理
- **多模型支持** - 配置和使用不同模型执行各种任务
- **多语言支持** - 支持英文和中文界面，可轻松切换语言

![Viby 终端演示](https://raw.githubusercontent.com/JohanLi233/viby/main/assets/screenshot.png)

## 🔧 安装

```sh
# 从 PyPI 安装
pip install viby
# 或者
uv tool install viby
```

### 替代安装方式

```sh
# 使用 uv 从源代码安装
uv pip install -e .
```

## 使用示例

### 基本问题

```sh
yb vibe "用 Python 写一个快速排序"
# -> 当然！以下是用 **Python** 实现的快速排序算法：
```

### 简化命令

```sh
yb "用 Python 写一个快速排序"
# -> 同上
```

### 交互式对话模式

```sh
yb --chat
# 或
yb -c
|> 告诉我量子计算的相关信息
# -> [AI 回答量子计算相关内容]
|> 有哪些实际应用？
# -> [AI 回答后续信息]
|> exit
```

### 处理管道内容

```sh
git diff | yb vibe "生成一个提交消息"
# -> 添加了 README 的相关信息
```

```sh
yb vibe "这个项目是关于什么的？" < README.md
# -> 这个项目是关于...
```

### 生成 Shell 命令

```sh
yb vibe "我写了多少行 Python 代码？"
# -> find . -type f -name "*.py" | xargs wc -l
# -> [r]运行, [e]编辑, [y]复制, [c]对话, [q]放弃 (默认: 运行): 
```

### 高级模型选择

```sh
# 使用思考模型进行复杂分析
yb --think vibe "分析这个复杂算法并提出优化建议"

# 使用快速模型获取快速响应
yb --fast vibe "将'Hello, World!'翻译成中文"
```

### Shell命令魔法集成

```sh
# 列出目录内容
yb vibe "$(ls) 当前目录下都有哪些文件？"
# -> 当前目录下的文件和文件夹包括：文件1.txt, 文件2.py, 目录1/...

# 分析Git状态
yb vibe "$(git status) 我应该先提交哪些文件？"

# 查看代码文件
yb vibe "$(cat main.py) 如何改进这段代码？"
```

### 智能工具发现

```sh
# Viby 会自动发现并使用相关工具
yb vibe "旧金山的天气怎么样？"
# -> [Viby 识别并使用天气工具]
# -> 旧金山当前天气是20°C，多云...

# 嵌入模型管理
# 首先下载嵌入模型（使用嵌入功能前需要执行一次）
yb tools embed download

# 启动嵌入服务器（工具发现功能需要）
yb tools embed start

# 检查嵌入服务器状态
yb tools embed status

# 更新来自已配置MCP服务器的工具嵌入向量
yb tools embed update

# 列出可用工具
yb tools list

# 不需要时停止嵌入服务器
yb tools embed stop
```

### 历史记录管理

```sh
# 查看最近的交互
yb history list

# 搜索历史记录
yb history search "python"

# 导出交互历史
yb history export history.json

# 查看Shell命令历史
yb history shell

# 清除历史记录（需确认）
yb history clear
```

### 自动使用 MCP 工具

```sh
yb vibe "现在几点了？"
# -> [AI 使用时间工具获取当前时间]
# -> "datetime": "2025-05-03T00:49:57+08:00"
```

### 键盘快捷键

Viby 提供了一个便捷的键盘快捷键（Ctrl+Q），让你可以快速将当前命令行内容传递给 Viby：

```sh
# 安装键盘快捷键（自动检测你的 shell 类型）
yb shortcuts

# 安装后，输入任何命令并按下 Ctrl+Q
帮我分析readme文件  # 现在按 Ctrl+Q
# -> 这会转变为: yb vibe 帮我分析readme文件
# -> [AI 分析readme文件并提供反馈]
```

支持的 shell：
- Bash
- Zsh
- Fish

安装快捷键后，你需要重新加载 shell 配置（`source ~/.bashrc`、`source ~/.zshrc` 或类似命令）或重启终端才能使快捷键生效。

## 命令结构

Viby 使用简单的命令结构：

```
yb [选项] [命令] [参数]...
```

主要命令：
- `yb [prompt]` - 提问
- `yb vibe "你的问题"` - 提问（默认命令）
- `yb --chat` 或 `yb -c` - 启动交互式聊天模式
- `yb --think vibe "复杂问题"` - 使用思考模型进行深入分析
- `yb --fast vibe "简单问题"` - 使用快速模型获取快速响应
- `yb history` - 管理交互历史记录
- `yb tools` - 管理工具相关命令
- `yb shortcuts` - 安装键盘快捷键

使用 `yb --help` 查看所有可用的命令和选项。

## 配置

Viby 从 `~/.config/viby/config.yaml` 读取配置。你可以在此设置模型、参数和MCP选项。

### 交互式配置

使用配置向导设置你的偏好：

```sh
yb --config
```

这允许你配置：
- API端点和密钥
- 模型
- 温度和token设置
- MCP工具启用选项
- 界面语言
- 嵌入模型设置

### MCP服务器配置

Viby支持模型上下文协议(MCP)服务器以提供扩展功能。MCP配置存储在 `~/.config/viby/mcp_servers.json` 文件中。

## ⭐ Star 历史

<div align="center">
  <a href="https://star-history.com/#JohanLi233/viby&Date">
    <img src="https://api.star-history.com/svg?repos=JohanLi233/viby&type=Date" alt="Star 历史图表" style="max-width:100%;">
  </a>
</div>

## 文档

- [使用示例](./docs/viby_使用示例.md) - 所有 Viby 功能的详细示例
- [项目设计文档](./docs/viby_项目设计文档.md) - 技术架构和设计


## 🤝 贡献

欢迎贡献！请随时提交 Pull Request 或创建 Issue。
