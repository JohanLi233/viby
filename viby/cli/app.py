"""
viby 命令行界面 - 使用 Typer 框架重构
默认行为：如果用户没有显式写出一级子命令，则自动当作 `vibe` 处理。
"""

import importlib
import sys
from typing import Dict, List, Type, Any
import typer
from rich.console import Console
from viby.locale import get_text, init_text_manager
from viby.config import config
from viby.utils.logging import setup_logging
from viby.utils.keyboard_shortcuts import install_shortcuts, detect_shell


# ---------------------------------------------------------
# 1) 预处理 argv：把默认未指定的情况映射到 vibe ---------
# ---------------------------------------------------------
def _inject_default_subcommand() -> None:
    """
    如果用户输入形如 `yb <something>`，而 <something> 既不是选项也不是
    已知一级子命令，则在 argv 中自动插入 'vibe'，变成
    `yb vibe <something>`。这样用户可以直接 `yb 提示词 ...`。
    """
    # 没有任何额外参数 → 不处理（让 Typer 去显示帮助等）
    if len(sys.argv) <= 1:
        return

    # 已知的一级子命令名称
    _known_root_cmds = {
        "vibe",
        "chat",
        "history",
        "tools",
        "embed",
        "shortcuts",
    }

    # 扫描 argv[1:]，找到第一个既不是 -option 也不是一级子命令的 token
    for idx, arg in enumerate(sys.argv[1:], start=1):
        # 1. 以 - 开头的是全局 / 子命令选项，跳过
        if arg.startswith("-"):
            continue
        # 2. 如果本身就是已知一级子命令，则无需插入，直接返回
        if arg in _known_root_cmds:
            return
        # 3. 既不是选项也不是子命令 → 把 vibe 插进去
        sys.argv.insert(idx, "vibe")
        return

_inject_default_subcommand()
init_text_manager(config)

def create_typer(help_text, add_completion: bool = True):
    """创建定制的 Typer 实例，统一配置帮助选项等"""
    return typer.Typer(
        help=help_text,
        add_help_option=False,
        add_completion=add_completion,
        context_settings={"help_option_names": ["-h", "--help"]},
    )


def default_callback(
    ctx: typer.Context,
    help_opt: bool = typer.Option(
        False,
        "--help",
        "-h",
        help=get_text("GENERAL", "help_text"),
        is_eager=True,
        expose_value=False,
    ),
):
    """默认回调：显示帮助并退出"""
    if help_opt or ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


# 创建 Typer 实例
app = create_typer(get_text("GENERAL", "app_description"))

# 创建子命令组
history_app = create_typer(get_text("HISTORY", "command_help"))
tools_app = create_typer(get_text("TOOLS", "command_help", "管理工具相关命令"))
embed_app = create_typer(
    get_text("TOOLS", "update_embeddings_help", "更新 MCP 工具的嵌入向量")
)

# 添加子命令组到主应用
app.add_typer(history_app, name="history")
app.add_typer(tools_app, name="tools")
tools_app.add_typer(embed_app, name="embed")

# 设置默认回调，显示帮助
history_app.callback(invoke_without_command=True)(default_callback)
tools_app.callback(invoke_without_command=True)(default_callback)
embed_app.callback(invoke_without_command=True)(default_callback)

# 控制台实例
console = Console()

# 日志记录器
logger = setup_logging(log_to_file=True)

# 命令注册表
command_registry: Dict[str, Dict] = {
    "vibe": {"module": "viby.commands.vibe", "class": "Vibe"},
    "chat": {"module": "viby.commands.chat", "class": "ChatCommand"},
    "history": {"module": "viby.commands.history", "class": "HistoryCommand"},
    "shortcuts": {"module": "viby.commands.shortcuts", "class": "ShortcutsCommand"},
    "tools": {"module": "viby.commands.tools", "class": "ToolsCommand"},
    "embed": {
        "module": "viby.viby_tool_search.commands",
        "class": "EmbedServerCommand",
    },
}

# 命令类型缓存，避免重复导入同一命令
_command_class_cache = {}


def get_version_string() -> str:
    """
    获取版本信息字符串，采用懒加载方式检测

    Returns:
        带有格式的版本信息字符串
    """
    import importlib.metadata
    import json

    version = importlib.metadata.version("viby")
    dist = importlib.metadata.distribution("viby")

    # 检测是否为可编辑安装 (dev 版本)
    suffix = ""
    direct_url_text = dist.read_text("direct_url.json")
    if direct_url_text:
        data = json.loads(direct_url_text)
        if data.get("dir_info", {}).get("editable", False):
            suffix = "(dev)"

    version_string = f"Viby {version}{suffix}"
    return version_string


def get_command_class(command_name: str) -> Type:
    """
    按需导入并获取命令类，减少启动时的导入开销

    Args:
        command_name: 命令名称，如 'shell', 'vibe', 'chat'

    Returns:
        命令类
    """
    # 使用缓存避免重复导入
    if command_name in _command_class_cache:
        return _command_class_cache[command_name]

    # 查找命令注册信息
    if command_name not in command_registry:
        logger.error(f"未知命令: {command_name}")
        raise ImportError(f"未知命令: {command_name}")

    # 动态导入命令模块
    cmd_info = command_registry[command_name]
    module_name = cmd_info["module"]
    class_name = cmd_info["class"]

    try:
        module = importlib.import_module(module_name)
        command_class = getattr(module, class_name)
        # 缓存命令类
        _command_class_cache[command_name] = command_class
        return command_class
    except (ImportError, AttributeError) as e:
        logger.error(f"导入命令 {command_name} 失败: {e}")
        raise


def lazy_load_wizard():
    """懒加载配置向导模块"""
    try:
        from viby.config.wizard import run_config_wizard

        return run_config_wizard
    except ImportError as e:
        logger.error(f"导入配置向导模块失败: {e}")
        raise


def process_input(prompt_args: List[str] = None) -> tuple[str, bool]:
    """
    处理命令行输入，包括管道输入

    Args:
        prompt_args: 命令行提示词参数

    Returns:
        (输入文本, 是否有输入)的元组
    """
    # 获取命令行提示词和管道上下文
    prompt = " ".join(prompt_args) if prompt_args else ""
    pipe_content = sys.stdin.read().strip() if not sys.stdin.isatty() else ""

    # 构造最终输入，过滤空值
    user_input = "\n".join(filter(None, [prompt, pipe_content]))

    return user_input, bool(user_input)


def load_model_manager(ctx_obj: Dict[str, Any]):
    """懒加载模型管理器"""
    from viby.llm.models import ModelManager

    return ModelManager(ctx_obj)


# 主入口和全局选项
@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    help_opt: bool = typer.Option(
        False,
        "--help",
        "-h",
        help=get_text("GENERAL", "help_text"),
        is_eager=True,
        expose_value=False,
    ),
    version: bool = typer.Option(
        False, "--version", "-v", help=get_text("GENERAL", "version_help")
    ),
    config_mode: bool = typer.Option(
        False, "--config", help=get_text("GENERAL", "config_help")
    ),
    think: bool = typer.Option(
        False, "--think", "-t", help=get_text("GENERAL", "think_help")
    ),
    fast: bool = typer.Option(
        False, "--fast", "-f", help=get_text("GENERAL", "fast_help")
    ),
    tokens: bool = typer.Option(
        False, "--tokens", "-k", help=get_text("GENERAL", "tokens_help")
    ),
):
    """Viby - 智能命令行助手"""
    # 本地化帮助选项
    if help_opt:
        typer.echo(ctx.get_help())
        raise typer.Exit()
    # 版本参数
    if version:
        typer.echo(get_version_string())
        raise typer.Exit()

    # 首次运行或指定 --config 参数时启动交互式配置向导
    if config.is_first_run or config_mode:
        # 懒加载配置向导
        run_config_wizard = lazy_load_wizard()
        run_config_wizard(config)
        init_text_manager(config)  # 如果语言等配置更改，重新初始化

    # 保存选项到上下文，以便在命令中使用
    ctx.obj = {
        "chat": chat,
        "think": think,
        "fast": fast,
        "tokens": tokens,
    }
    # 如果没有指定子命令，则打印帮助并退出
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


# 通用命令
@app.command(help=get_text("GENERAL", "prompt_help"))
def vibe(ctx: typer.Context, prompt_args: List[str] = typer.Argument(None)):
    """向 AI 发送单个问题并获取回答。"""
    user_input, has_input = process_input(prompt_args)

    if not has_input:
        if not sys.stdout.isatty():
            return
        typer.echo("请提供问题内容")
        return

    # 懒加载模型管理器
    model_manager = load_model_manager(ctx.obj)

    Vibe = get_command_class("vibe")
    vibe = Vibe(model_manager)

    # 执行命令
    return vibe.vibe(user_input)


@app.command(help=get_text("GENERAL", "chat_help"))
def chat(ctx: typer.Context):
    """启动交互式聊天模式与 AI 进行多轮对话。"""
    # 懒加载模型管理器
    model_manager = load_model_manager(ctx.obj)

    # 创建 ChatCommand 实例
    ChatCommand = get_command_class("chat")
    chat_command = ChatCommand(model_manager)

    # 执行命令
    return chat_command.run()


@app.command(help=get_text("SHORTCUTS", "command_help"))
def shortcuts():
    """安装和管理键盘快捷键。"""
    # 检测 shell 类型
    detected_shell = detect_shell()
    if detected_shell:
        typer.echo(f"{get_text('SHORTCUTS', 'auto_detect_shell')}: {detected_shell}")
    else:
        typer.echo(get_text("SHORTCUTS", "auto_detect_failed"))

    # 安装快捷键
    result = install_shortcuts(detected_shell)

    # 显示安装结果
    if result["status"] == "success":
        status_color = typer.colors.GREEN
    elif result["status"] == "info":
        status_color = typer.colors.BLUE
    else:
        status_color = typer.colors.RED

    typer.echo(
        typer.style(f"[{result['status'].upper()}]", fg=status_color)
        + f" {result['message']}"
    )

    # 如果需要用户操作，显示提示
    if "action_required" in result:
        typer.echo(
            f"\n{get_text('SHORTCUTS', 'action_required').format(result['action_required'])}"
        )

    if result["status"] == "success":
        typer.echo(f"\n{get_text('SHORTCUTS', 'activation_note')}")


# History 命令组
@history_app.command("list")
def history_list(
    limit: int = typer.Option(
        10, "--limit", "-n", help=get_text("HISTORY", "limit_help")
    ),
):
    """列出历史记录。"""
    HistoryCommand = get_command_class("history")
    return HistoryCommand().list_history(limit)


@history_app.command("search")
def history_search(
    query: str = typer.Argument(..., help=get_text("HISTORY", "query_help")),
    limit: int = typer.Option(
        10, "--limit", "-n", help=get_text("HISTORY", "limit_help")
    ),
):
    """搜索历史记录。"""
    HistoryCommand = get_command_class("history")
    return HistoryCommand().search_history(query, limit)


@history_app.command("export")
def history_export(
    file: str = typer.Argument(..., help=get_text("HISTORY", "file_help")),
    format_type: str = typer.Option(
        "json", "--format", "-f", help=get_text("HISTORY", "format_help")
    ),
    history_type: str = typer.Option(
        "interactions", "--type", "-t", help=get_text("HISTORY", "type_help")
    ),
):
    """导出历史记录到文件。"""
    HistoryCommand = get_command_class("history")
    return HistoryCommand().export_history(file, format_type, history_type)


@history_app.command("clear")
def history_clear():
    """清除历史记录。"""
    HistoryCommand = get_command_class("history")
    return HistoryCommand().clear_history()


@history_app.command("shell")
def history_shell(
    limit: int = typer.Option(
        10, "--limit", "-n", help=get_text("HISTORY", "limit_help")
    ),
):
    """列出 shell 命令历史。"""
    HistoryCommand = get_command_class("history")
    return HistoryCommand().list_shell_history(limit)


# Tools 命令组
@tools_app.command("list")
def tools_list():
    """列出所有可用的 MCP 工具。"""
    ToolsCommand = get_command_class("tools")
    return ToolsCommand().list_tools()


# Embed 子命令组
@embed_app.command("update")
def embed_update():
    """更新 MCP 工具的嵌入向量。"""
    EmbedServerCommand = get_command_class("embed")
    return EmbedServerCommand().update_embeddings()


@embed_app.command("start")
def embed_start():
    """启动嵌入模型服务。"""
    EmbedServerCommand = get_command_class("embed")
    return EmbedServerCommand().start_embed_server()


@embed_app.command("stop")
def embed_stop():
    """停止嵌入模型服务。"""
    EmbedServerCommand = get_command_class("embed")
    return EmbedServerCommand().stop_embed_server()


@embed_app.command("status")
def embed_status():
    """查看嵌入模型服务状态。"""
    EmbedServerCommand = get_command_class("embed")
    return EmbedServerCommand().check_embed_server_status()


@embed_app.command("download")
def embed_download():
    """下载嵌入模型。"""
    EmbedServerCommand = get_command_class("embed")
    return EmbedServerCommand().download_embedding_model()


if __name__ == "__main__":
    app()
