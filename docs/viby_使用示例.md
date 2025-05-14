# Viby - 详细使用示例

<div align="center">
  <img src="https://raw.githubusercontent.com/JohanLi233/viby/main/assets/viby-icon.png" alt="Viby Logo" width="120" height="120">
</div>

## 目录

- [简介](#简介)
- [安装](#安装)
- [基本问答](#基本问答)
- [交互式聊天模式](#交互式聊天模式)
- [处理管道内容](#处理管道内容)
- [Shell命令生成](#shell命令生成)
- [模型选择](#模型选择)
- [Shell命令魔法集成](#shell命令魔法集成)
- [智能工具发现](#智能工具发现)
- [使用MCP工具](#使用mcp工具)
- [历史记录管理](#历史记录管理)
- [键盘快捷键](#键盘快捷键)
- [配置设置](#配置设置)
- [额外技巧与窍门](#额外技巧与窍门)

## 简介

Viby是一款强大的命令行工具，将大型语言模型直接集成到你的终端中。凭借其多功能特性，Viby可以协助编码、回答问题、生成shell命令等等，无需离开你的终端环境。

本文档提供详细的使用示例，帮助你充分利用Viby的各项功能。

## 安装

### 标准安装

安装Viby最简单的方法是通过PyPI：

```bash
pip install viby
```

### 开发安装

如果你想从源代码安装或为Viby做贡献：

```bash
# 克隆仓库
git clone https://github.com/JohanLi233/viby.git
cd viby

# 使用uv安装（推荐）
uv pip install -e .

# 或使用传统pip
pip install -e .
```

## 基本问答

使用Viby的最简单方式是通过`yb`命令直接提问：

```bash
yb "什么是斐波那契数列？"
```

Viby会给出斐波那契数列的简明解释。

对于代码示例：

```bash
yb "用Python实现快速排序算法"
```

它会提供一个干净、带注释的Python快速排序算法实现。

你也可以使用Viby进行翻译：

```bash
yb "将'你好，最近怎么样？'翻译成英文"
```

## 交互式聊天模式

对于多轮对话，使用聊天模式，带上`-c`或`--chat`标志：

```bash
yb -c
# 或
yb --chat
```

这会打开一个交互式会话，你可以进行来回的对话：

```
欢迎使用Viby对话模式，输入'exit'可退出对话
|> 什么是量子计算？
[AI关于量子计算的解释]

|> 有哪些实际应用？
[AI回应量子计算的应用场景]

|> 量子纠缠是如何工作的？
[AI解释量子纠缠原理]

|> exit
```

退出聊天模式可以通过输入`exit`、`/exit`或`/quit`。

## 处理管道内容

Viby可以通过管道处理其他命令的内容，使其在工作流集成方面极为灵活：

### 分析Git差异

```bash
git diff | yb "生成一个简洁的提交信息"
```

这将git diff的输出传递给Viby，它会分析变更并建议一个适当的提交信息。

### 总结文件内容

```bash
cat README.md | yb "总结这个文档"
# 或
yb "总结这个文档" < README.md
```

这两个命令达到同样的效果：Viby读取README.md的内容并生成一个摘要。

### 分析命令输出

```bash
ls -la | yb "这个目录中哪些文件最大？"
```

Viby接收目录列表并识别最大的文件。

### 处理多个命令输出

```bash
(find . -name "*.js" | wc -l && find . -name "*.py" | wc -l) | yb "比较JavaScript和Python文件的数量"
```

这结合了多个命令的输出，供Viby一起分析。

## Shell命令生成

Viby特别擅长根据自然语言描述生成shell命令：

```bash
yb "找出所有在过去3天内修改过的Python文件"
# -> find . -name "*.py" -mtime -3
# -> [r]运行, [e]编辑, [y]复制, [c]聊天, [q]放弃 (默认: 运行):
```

当Viby生成shell命令时，它提供几个选项：
- `r`（或回车）：立即运行命令
- `e`：在运行前编辑命令
- `y`：复制命令到剪贴板而不运行
- `c`：进入聊天模式以优化命令
- `q`：退出而不执行

### YOLO模式

如果你经常执行生成的命令，可以在配置中启用YOLO模式。启用YOLO模式后，Viby将自动执行"安全"的shell命令而不提示（潜在危险的命令仍需确认）：

```bash
# 启用YOLO模式后
yb "列出所有markdown文件"
# -> [自动执行] find . -name "*.md"
```

要启用YOLO模式，运行配置向导并在提示YOLO模式时选择"是"：

```bash
yb --config
```

## 模型选择

Viby支持为不同类型的查询使用不同的模型配置：

### 思考模型

对于复杂分析或深度推理，使用`--think`或`-t`标志：

```bash
yb --think "分析微服务架构的优缺点"
```

思考模型通常使用更强大的模型，具有更高的令牌数和针对深思熟虑分析优化的温度设置。

### 快速模型

对于速度比深度更重要的简单查询，使用`--fast`或`-f`标志：

```bash
yb --fast "将42°C转换为华氏度"
```

快速模型使用更小、更快的模型，具有针对速度优化的设置。

## 智能工具发现

Viby包含智能工具发现系统，可以自动在您配置的MCP服务器中查找并使用最相关的工具来回答您的查询：

### 自动工具选择

```bash
# 天气信息
yb "今天东京的天气怎么样？"
# -> [Viby自动识别这是一个天气查询并使用适当的工具]

# 单位转换
yb "把5公里转换成英里"
# -> [Viby使用转换工具，无需您特别指定]

# 货币转换
yb "100美元等于多少人民币？"
# -> [Viby使用货币转换工具]
```

### 管理工具嵌入

Viby使用嵌入向量语义匹配您的查询与您已配置的MCP服务器中的合适工具。在使用此功能之前，您需要设置嵌入服务器：

```bash
# 步骤1：下载嵌入模型（使用嵌入功能前需要执行一次）
# 嵌入模型可以通过 yb --config 管理
yb tools embed download

# 步骤2：启动嵌入服务器
yb tools embed start

# 步骤3：检查服务器状态
yb tools embed status
# -> 这会显示服务器是否正在运行、PID、URL、运行时间等信息

# 步骤4：更新工具嵌入向量（在向MCP服务器添加新工具后运行）
yb tools embed update

# 查看可用工具
yb tools list

# 当您不再需要时，可以停止嵌入服务器以释放资源
yb tools embed stop
```

嵌入服务器进程在后台运行，提供快速的工具发现功能，无需为每次查询重新加载模型。整个流程是：

1. 下载嵌入模型（一次性设置）
2. 启动服务器（工具发现功能需要）
3. 当您的工具发生变化时更新嵌入向量
4. 正常使用Viby - 它会自动连接到运行中的服务器
5. 需要时停止服务器（可选）
```

### 工具分类

Viby将工具组织成不同的类别以便更好地发现：

- **信息检索**：天气、新闻、搜索等
- **计算**：数学、货币转换、单位转换
- **系统**：文件操作、网络任务
- **开发**：代码生成、调试、分析
- **实用工具**：时间、日期、随机生成器

工具发现系统会随着时间的推移自动改进，因为它会从您的使用模式中学习。

## Shell命令魔法集成

Viby可以使用`$()`语法在提示中直接集成命令输出：

### 分析当前目录

```bash
yb "$(ls -la) 这个目录中哪些文件可能占用最多空间？"
```

这会先执行`ls -la`，并将其输出作为Viby的上下文的一部分。

### 处理Git操作

```bash
yb "$(git status) 我应该如何处理这些更改？"
```

Viby获取当前git状态并提供如何进行的建议。

### 调试代码

```bash
yb "$(cat main.py) 这段代码有什么问题？"
```

Viby分析main.py的内容并为任何问题提供修复建议。

### 多个命令

你可以组合多个命令：

```bash
yb "$(ps aux | grep python) $(free -h) 为什么我的系统运行缓慢？"
```

这提供了进程和内存信息，帮助Viby诊断性能问题。

## 使用MCP工具

模型上下文协议（MCP）工具允许Viby访问外部功能：

### 获取当前时间

```bash
yb "现在几点了？"
```

Viby会使用时间工具获取并显示当前时间。

### 查询天气

```bash
yb "北京现在天气如何？"
```

如果配置了适当的MCP工具，Viby可以获取实时天气信息。

### 网络搜索

如果配置了搜索工具：

```bash
yb "昨天有哪些重要的科技新闻？"
```

### 工具调用可视化

当Viby使用MCP工具时，它会显示工具调用信息：

```
正在执行工具调用
{
  "tool": "time_now",
  "server": "time",
  "parameters": {}
}

工具调用结果
"2023-05-03T00:49:57+08:00"
```

## 键盘快捷键

Viby提供便捷的键盘快捷键（Ctrl+Q），可将当前命令行转换为Viby查询：

### 安装快捷键

```bash
yb shortcuts
```

这会自动检测你的shell类型（bash、zsh或fish）并在你的shell配置文件中添加适当的配置。

### 使用快捷键

安装后重新加载shell：

1. 在终端输入命令或描述：
   ```
   查找所有包含"import requests"的python文件
   ```

2. 按下Ctrl+Q，它会转换为：
   ```
   yb 查找所有包含"import requests"的python文件
   ```

3. Viby处理请求并可能回应：
   ```
   grep -r "import requests" --include="*.py" .
   ```

## 配置设置

Viby可以通过交互式向导进行配置：

```bash
yb --config
```

这个向导将指导你设置：

1. 界面语言（英文或中文）
2. 默认模型设置（名称、API端点、API密钥）
3. 思考模型设置（可选）
4. 快速模型设置（可选）
5. MCP工具启用
6. Shell命令的YOLO模式

### 配置位置

Viby将配置存储在：
- `~/.config/viby/config.yaml`（Linux/macOS）
- `%APPDATA%\viby\config.yaml`（Windows）

### 语言设置

你可以临时切换界面语言：

```bash
yb --language en-US "你的查询"
# 或
yb --language zh-CN "你的查询"
```

### 令牌使用跟踪

要查看查询的令牌使用情况：

```bash
yb --tokens "解释量子计算"
```

这将在响应后显示输入令牌、输出令牌、总令牌数和响应时间。

## 历史记录管理

Viby会跟踪你的交互，并可以显示、搜索、导出或清除你的历史记录：

### 查看历史

```bash
# 列出最近的交互
yb history list

# 使用自定义限制列出
yb history list --limit 20
```

### 搜索历史

```bash
# 搜索特定术语
yb history search "python"
```

### 导出历史

```bash
# 导出为JSON（默认）
yb history export ~/viby_history.json

# 导出为CSV
yb history export ~/viby_history.csv --format csv

# 只导出shell命令
yb history export ~/shell_history.json --type shell
```

### 清除历史

```bash
# 清除所有历史（需确认）
yb history clear

# 只清除shell命令
yb history clear --type shell

# 强制清除，不需确认
yb history clear --force
```

### 查看Shell命令历史

```bash
# 查看最近的shell命令
yb history shell
```

## 额外技巧与窍门

### 组合功能

你可以组合多个Viby功能：

```bash
# 使用思考模型和令牌跟踪
yb --think --tokens "分析归并排序与快速排序的复杂度"

# 使用快速模型处理管道内容
cat large_log.txt | yb --fast "总结这个日志文件"
```

### 环境变量

Viby遵循以下环境变量：
- `VIBY_DEBUG`：启用详细日志记录进行故障排除
- `VIBY_DEV_MODE`：启用开发模式

### 常见任务的一行命令

```bash
# 生成随机密码
yb "生成一个16字符的安全随机密码"

# 解释命令
yb "命令'find . -type f -name \"*.py\" | xargs grep \"import\"'做什么？"

# 正则表达式帮助
yb "编写一个匹配有效电子邮件地址的正则表达式"

# 代码审查
cat my_file.py | yb "审查这段代码并建议改进"
```

### 与版本控制一起使用

```bash
# 解释提交中的更改
git show | yb "解释这个提交做了哪些更改"

# 生成发布说明
git log --pretty=format:"%h %s" v1.0..HEAD | yb "从这些提交中生成发布说明"
```

---

本文档涵盖了Viby的主要功能和使用示例。对于更具体的用例或问题，你随时可以询问Viby本身：

```bash
yb "我如何使用你来[特定任务]？"
```

获取更新和更多信息，请访问[Viby的GitHub仓库](https://github.com/JohanLi233/viby)。 