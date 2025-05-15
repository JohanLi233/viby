# Viby 使用示例

本文档提供了 Viby 的详细使用示例，帮助你充分发挥其潜力。

## 目录

- [Viby 使用示例](#viby-使用示例)
  - [目录](#目录)
  - [基本用法](#基本用法)
  - [交互式聊天模式](#交互式聊天模式)
  - [管道输入](#管道输入)
  - [Shell 命令生成](#shell-命令生成)
  - [历史记录管理](#历史记录管理)
  - [MCP 工具集成](#mcp-工具集成)
    - [配置 MCP 服务器](#配置-mcp-服务器)
  - [嵌入模型与工具发现](#嵌入模型与工具发现)
  - [键盘快捷键](#键盘快捷键)
  - [语言切换](#语言切换)
  - [多模型支持](#多模型支持)
  - [配置](#配置)

## 基本用法

最简单的方式是直接提问：

```sh
yb "用Python写一个二分查找算法"
```

你也可以使用显式的 `vibe` 命令：

```sh
# 基本问答
yb vibe "用Python写一个二分查找算法"

# 直接运行作为默认命令 - 不需要显式指定引号
yb vibe 推荐几个Python学习资源
```

## 交互式聊天模式

交互式模式允许你进行多轮连续对话，每次会话中的所有上下文都会被保留：

```sh
# 启动交互式聊天
yb --chat
# 或
yb -c

|> 介绍一下机器学习
# -> [AI 介绍机器学习]

|> 监督学习和无监督学习有什么区别？
# -> [AI 解释区别，利用之前的上下文]

|> exit
# 或者使用 Ctrl+D 退出聊天模式
```

## 管道输入

Viby 可以接收来自管道的输入数据：

```sh
# 分析 git diff
git diff | yb vibe "这些代码变更的主要内容是什么？"

# 读取文件内容并分析
cat complex_code.py | yb vibe "简化这段代码"

# 分析命令输出
ls -la | yb vibe "哪些文件最近被修改？"

# 使用重定向输入
yb vibe "总结这篇文章" < article.txt
```

## Shell 命令生成

Viby 可以自动分析你的问题并生成相应的 Shell 命令：

```sh
# 寻找大文件
yb vibe "找出我的系统中占用空间最大的5个文件"
# -> find / -type f -exec du -h {} \; | sort -rh | head -n 5
# -> [r]运行, [e]编辑, [y]复制, [c]对话, [q]放弃 (默认: 运行): 

# 生成并直接执行命令
yb vibe "压缩当前目录下所有的日志文件"
# -> tar -czvf logs.tar.gz *.log
# -> 按回车直接执行，或选择其他选项
```

你也可以使用 Shell 命令魔法将当前环境信息传递给 Viby：

```sh
# 分析当前目录内容
yb vibe "$(ls -la) 解释一下这些文件的用途"

# 结合多个命令输出
yb vibe "$(ps aux | grep python) $(free -h) 哪些 Python 进程占用内存较多？"

# 分析 Git 仓库状态
yb vibe "$(git status) $(git log --oneline -5) 建议我接下来应该做什么？"
```

## 历史记录管理

Viby 提供了完整的历史记录管理功能：

```sh
# 列出最近的交互历史（默认10条）
yb history list

# 列出更多历史记录
yb history list --limit 20

# 按筛选条件搜索历史
yb history search "Python"

# 导出历史记录到文件
yb history export history.json

# 导出特定时间范围的历史
yb history export --from "2024-01-01" --to "2024-01-31" jan_history.json

# 查看通过Viby生成并执行过的Shell命令
yb history shell

# 清除所有历史记录（会提示确认）
yb history clear
```

## MCP 工具集成

Viby 集成了 MCP（模型上下文协议），可以使用各种强大的工具：

```sh
# 自动使用工具
yb vibe "巴黎现在的天气怎么样？"
# -> [AI 使用天气工具，返回实时天气信息]

# 使用 TaviyAI 搜索工具
yb vibe "最近有关量子计算的研究进展"
# -> [AI 使用 Tavily 搜索工具获取最新信息]
```

### 配置 MCP 服务器

```sh
# 在交互式配置中启用 MCP 工具
yb --config
# 选择 MCP 设置部分并启用
```

## 嵌入模型与工具发现

Viby 使用嵌入模型进行工具的语义搜索，实现智能工具发现：

```sh
# 下载嵌入模型（首次使用前需要）
yb tools embed download

# 启动嵌入服务器（使用工具发现功能时需要）
yb tools embed start

# 查看嵌入服务器状态
yb tools embed status

# 更新工具嵌入
yb tools embed update

# 列出可用工具
yb tools list

# 使用特定工具（无需嵌入服务）
yb tools use weather "北京的天气"

# 停止嵌入服务器
yb tools embed stop
```

## 键盘快捷键

Viby 提供了方便的键盘快捷键集成：

```sh
# 安装键盘快捷键
yb shortcuts

# 安装后，在命令行输入内容并按 Ctrl+Q
git log  # 按 Ctrl+Q
# -> 变为: yb git log
# -> [AI 解析并解释 Git 日志]

# 也可以输入问题并使用快捷键
分析系统内存使用情况  # 按 Ctrl+Q
# -> 变为: yb 分析系统内存使用情况
```

支持的 shell：Bash、Zsh 和 Fish

## 语言切换

Viby 支持多种界面语言：

```sh
# 在配置中切换语言
yb --config
# 然后选择语言设置部分
```

## 多模型支持

Viby 支持使用不同的模型来处理不同类型的查询：

```sh
# 使用思考模型进行深入分析
yb --think vibe "分析这个复杂算法的时间复杂度和可能的优化方向"

# 使用快速模型获取简单答案
yb --fast vibe "将'Hello, World!'翻译成中文"

# 在配置中设置默认模型
yb --config
# 选择模型设置部分
```

## 配置

通过交互式配置向导设置 Viby：

```sh
# 启动配置向导
yb --config
```

配置向导允许你设置：
- API密钥和端点
- 默认模型和备用模型
- 模型参数（温度、最大token等）
- MCP工具集成选项
- 界面语言
- 嵌入模型设置

配置保存在 `~/.config/viby/config.yaml`，MCP 服务器配置保存在 `~/.config/viby/mcp_servers.json`。 