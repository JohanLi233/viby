# viby

[English](./README.md) | 中文

一个用于与大语言模型交互的多功能命令行工具。

## 功能特点

- 提问并获取 AI 生成的答案
- 生成 shell 命令及其解释
- 处理管道输入（例如：来自 git diff 的内容）
- 支持Open AI 格式接口调用

## 安装

```sh
# 使用 uv 安装（推荐）
uv pip install -e .

# 或使用 pip
pip install -e .
```

## 使用示例

### 基本提问

```sh
yb "用python写一个快速排序"
# -> 当然可以！下面是一个用 **Python** 实现的 **快速排序（Quick Sort）** 算法：
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
# -> [r]运行, [e]编辑, [y]复制, [q]放弃: r
```

## 配置

Viby 从 `~/.config/viby/config.json` 读取配置。你可以在此设置模型和参数。

## 语言切换

Viby 默认使用英文界面。首次启动或通过 `--config` 参数可以进入交互式配置向导，在其中选择中文或其他支持的语言。

- 默认语言：English (en-US)
- 切换到中文：在配置向导中选择 `中文 (zh-CN)` 即可。

**示例：**

```sh
yb --config
# 按提示选择语言（中文或英文）
```
