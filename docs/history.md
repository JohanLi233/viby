# Viby 历史管理系统

Viby历史管理系统提供了完整的交互历史记录和Shell命令历史功能，允许用户查看、搜索和导出历史记录。

## 基本功能

历史管理系统具有以下主要功能：

1. **交互历史记录**：自动记录用户与LLM的所有交互，包括用户输入和模型响应
2. **Shell命令历史**：跟踪通过Viby执行的所有Shell命令及其输出和退出代码
3. **历史查询**：查看最近的交互历史和命令历史
4. **历史搜索**：按关键词搜索历史记录
5. **历史导出**：将历史记录导出为多种格式（JSON、CSV、YAML）
6. **历史清除**：清除全部或部分历史记录

## 命令行使用

Viby提供了简单的命令行界面来管理历史记录：

### 查看历史

显示最近的交互历史记录：

```bash
yb history list
```

显示指定数量的历史记录：

```bash
yb history list --limit 20
```

### 查看Shell命令历史

显示最近执行的Shell命令：

```bash
yb history shell
```

显示指定数量的Shell命令历史：

```bash
yb history shell --limit 10
```

### 搜索历史

按关键词搜索历史记录：

```bash
yb history search "关键词"
```

限制搜索结果数量：

```bash
yb history search "关键词" --limit 5
```

### 导出历史

导出历史记录为JSON格式：

```bash
yb history export history.json
```

导出为其他格式（支持CSV和YAML）：

```bash
yb history export history.csv --format csv
yb history export history.yaml --format yaml
```

### 清除历史

清除所有交互历史记录：

```bash
yb history clear
```

清除所有Shell命令历史：

```bash
yb history clear --shell
```

## 数据存储

历史记录存储在SQLite数据库中，默认路径为：

- **macOS/Linux**: `~/.config/viby/_history.db`

可以通过环境变量`VIBY_HISTORY_DB_PATH`自定义数据库路径。

## 隐私考虑

历史记录包含用户与LLM的所有交互，可能包含敏感信息。请注意：

1. 历史记录仅存储在本地，不会上传到任何服务器
2. 如果需要共享日志或报告问题，请先检查历史记录并移除敏感信息
3. 可以随时使用`yb history clear`命令清除历史记录