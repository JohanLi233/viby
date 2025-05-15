"""
viby命令行界面 - 使用Typer框架重构
"""

import importlib
import os
import pathlib
import sys
from typing import List

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress
from rich.prompt import Confirm

# 导入viby模块
from viby.locale import get_text, init_text_manager
from viby.config import config
from viby.utils.logging import setup_logging
from viby.utils.keyboard_shortcuts import install_shortcuts, detect_shell
from viby.utils.history import HistoryManager
from viby.utils.renderer import print_markdown
from viby.viby_tool_search.commands import EmbedServerCommand
from viby.viby_tool_search.utils import get_mcp_tools_from_cache

# 在使用get_text之前初始化文本管理器
init_text_manager(config)

# 创建Typer实例
app = typer.Typer(
    help="Viby - 智能命令行助手",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)

# 创建子命令组
history_app = typer.Typer(
    help=get_text("HISTORY", "command_help"),
    context_settings={"help_option_names": ["-h", "--help"]},
)
tools_app = typer.Typer(
    help=get_text("TOOLS", "command_help", "管理工具相关命令"),
    context_settings={"help_option_names": ["-h", "--help"]},
)
embed_app = typer.Typer(
    help=get_text("TOOLS", "update_embeddings_help", "更新MCP工具的嵌入向量"),
    context_settings={"help_option_names": ["-h", "--help"]},
)


# 当未指定history子命令时打印历史帮助
@history_app.callback(invoke_without_command=True)
def history_main(ctx: typer.Context):
    """历史管理帮助"""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


# 添加子命令组到主应用
app.add_typer(history_app, name="history")
app.add_typer(tools_app, name="tools")
tools_app.add_typer(embed_app, name="embed")


# 当未指定tools子命令时打印工具帮助
@tools_app.callback(invoke_without_command=True)
def tools_main(ctx: typer.Context):
    """工具管理帮助"""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


# 当未指定embed子命令时打印embed帮助
@embed_app.callback(invoke_without_command=True)
def embed_main(ctx: typer.Context):
    """嵌入管理帮助"""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


# 控制台实例
console = Console()

# 日志记录器
logger = setup_logging(log_to_file=True)

# 命令类型缓存，避免重复导入同一命令
_command_class_cache = {}


def get_version_string() -> str:
    """
    获取版本信息字符串，采用懒加载方式检测

    Returns:
        带有格式的版本信息字符串
    """
    # 获取基本版本 - 这很轻量，不需要懒加载
    import importlib.metadata

    base_version = importlib.metadata.version("viby")
    version_string = f"Viby {base_version}"

    # 仅在必要时执行开发检查
    def lazy_check_dev_mode() -> bool:
        """懒加载检查是否为开发模式"""
        try:
            # __file__ in this context is .../viby/cli/typer_cli.py
            # Project root should be three levels up from the directory of this file.
            current_file_path = pathlib.Path(__file__).resolve()
            project_root_marker = (
                current_file_path.parent.parent.parent / "pyproject.toml"
            )
            return project_root_marker.is_file()
        except Exception:
            return False

    # 快速检查环境变量，这比文件检查更快
    if os.environ.get("VIBY_DEV_MODE"):
        version_string += " (dev)"
    # 否则，如果需要更准确，检查文件结构
    elif lazy_check_dev_mode():
        version_string += " (dev)"

    return version_string


def get_command_class(command_name: str) -> any:
    """
    按需导入并获取命令类，减少启动时的导入开销

    Args:
        command_name: 命令名称，如 'shell', 'ask', 'chat'

    Returns:
        命令类
    """
    # 使用缓存避免重复导入
    if command_name in _command_class_cache:
        return _command_class_cache[command_name]

    # 动态导入命令模块
    module_name = f"viby.commands.{command_name.lower()}"
    class_name = f"{command_name.capitalize()}Command"

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


# 主入口和全局选项
@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", "-v", help=get_text("GENERAL", "version_help")
    ),
    chat: bool = typer.Option(
        False, "--chat", "-c", help=get_text("GENERAL", "chat_help")
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
def ask(ctx: typer.Context, prompt_args: List[str] = typer.Argument(None)):
    """向AI发送单个问题并获取回答。"""
    user_input, has_input = process_input(prompt_args)

    if not has_input:
        if not sys.stdout.isatty():
            return
        typer.echo("请提供问题内容")
        return

    # 懒加载模型管理器
    from viby.llm.models import ModelManager

    model_manager = ModelManager(ctx.obj)

    # 创建AskCommand实例
    AskCommand = get_command_class("ask")
    ask_command = AskCommand(model_manager)

    # 执行命令
    return ask_command.execute(user_input)


@app.command(help=get_text("GENERAL", "chat_help"))
def chat(ctx: typer.Context):
    """启动交互式聊天模式与AI进行多轮对话。"""
    # 懒加载模型管理器
    from viby.llm.models import ModelManager

    model_manager = ModelManager(ctx.obj)

    # 创建ChatCommand实例
    ChatCommand = get_command_class("chat")
    chat_command = ChatCommand(model_manager)

    # 执行命令
    return chat_command.execute()


@app.command(help=get_text("SHORTCUTS", "command_help"))
def shortcuts():
    """安装和管理键盘快捷键。"""
    # 检测shell类型
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


# History命令组
@history_app.command("list")
def history_list(
    limit: int = typer.Option(
        10, "--limit", "-n", help=get_text("HISTORY", "limit_help")
    ),
):
    """列出历史记录。"""
    history_manager = HistoryManager()
    records = history_manager.get_history(limit=limit)

    if not records:
        print_markdown(get_text("HISTORY", "no_history"), "")
        return

    table = Table(title=get_text("HISTORY", "recent_history"))
    table.add_column("ID", justify="right", style="cyan")
    table.add_column(get_text("HISTORY", "timestamp"), style="green")
    table.add_column(get_text("HISTORY", "type"), style="magenta")
    table.add_column(get_text("HISTORY", "content"), style="white")
    table.add_column(get_text("HISTORY", "response"), style="yellow")

    from datetime import datetime

    for record in records:
        # 格式化时间戳
        dt = datetime.fromisoformat(record["timestamp"])
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")

        # 限制内容长度
        content = record["content"]
        if len(content) > 256:
            content = content[:256] + "..."

        # 添加响应内容，同样限制长度
        response = record.get("response", "")
        if response and len(response) > 256:
            response = response[:256] + "..."

        table.add_row(
            str(record["id"]), formatted_time, record["type"], content, response
        )

    console.print(table)


@history_app.command("search")
def history_search(
    query: str = typer.Argument(..., help=get_text("HISTORY", "query_help")),
    limit: int = typer.Option(
        10, "--limit", "-n", help=get_text("HISTORY", "limit_help")
    ),
):
    """搜索历史记录。"""
    history_manager = HistoryManager()

    if not query:
        print_markdown(get_text("HISTORY", "search_term_required"), "error")
        raise typer.Exit(code=1)

    records = history_manager.get_history(limit=limit, search_query=query)

    if not records:
        print_markdown(get_text("HISTORY", "no_matching_history").format(query), "")
        return

    table = Table(title=get_text("HISTORY", "search_results").format(query))
    table.add_column("ID", justify="right", style="cyan")
    table.add_column(get_text("HISTORY", "timestamp"), style="green")
    table.add_column(get_text("HISTORY", "type"), style="magenta")
    table.add_column(get_text("HISTORY", "content"), style="white")
    table.add_column(get_text("HISTORY", "response"), style="yellow")

    from datetime import datetime

    for record in records:
        # 格式化时间戳
        dt = datetime.fromisoformat(record["timestamp"])
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")

        # 限制内容长度
        content = record["content"]
        if len(content) > 50:
            content = content[:47] + "..."

        # 添加响应内容，同样限制长度
        response = record.get("response", "")
        if response and len(response) > 50:
            response = response[:47] + "..."

        table.add_row(
            str(record["id"]), formatted_time, record["type"], content, response
        )

    console.print(table)


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
    history_manager = HistoryManager()

    if not file:
        print_markdown(get_text("HISTORY", "export_path_required"), "error")
        raise typer.Exit(code=1)

    # 确保目录存在
    output_dir = os.path.dirname(file)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except OSError as e:
            print_markdown(
                get_text("HISTORY", "create_directory_failed").format(e), "error"
            )
            raise typer.Exit(code=1)

    # 如果文件已存在，确认是否覆盖
    if os.path.exists(file):
        if not Confirm.ask(get_text("HISTORY", "file_exists_overwrite").format(file)):
            print_markdown(get_text("HISTORY", "export_cancelled"), "")
            return

    # 显示导出进度
    with Progress() as progress:
        task = progress.add_task(get_text("HISTORY", "exporting_history"), total=1)

        # 导出历史记录
        success = history_manager.export_history(file, format_type, history_type)

        progress.update(task, completed=1)

    if success:
        print_markdown(
            get_text("HISTORY", "export_successful").format(
                file, format_type, history_type
            ),
            "success",
        )
    else:
        print_markdown(get_text("HISTORY", "export_failed"), "error")
        raise typer.Exit(code=1)


@history_app.command("clear")
def history_clear(
    history_type: str = typer.Option(
        "all", "--type", "-t", help=get_text("HISTORY", "clear_type_help")
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help=get_text("HISTORY", "force_help")
    ),
):
    """清除历史记录。"""
    history_manager = HistoryManager()

    if not force:
        confirmation = get_text("HISTORY", "confirm_clear_all")
        if history_type == "interactions":
            confirmation = get_text("HISTORY", "confirm_clear_interactions")
        elif history_type == "shell":
            confirmation = get_text("HISTORY", "confirm_clear_shell")

        if not Confirm.ask(confirmation):
            print_markdown(get_text("HISTORY", "clear_cancelled"), "")
            return

    # 显示清除进度
    with Progress() as progress:
        task = progress.add_task(get_text("HISTORY", "clearing_history"), total=1)

        # 清除历史记录
        success = history_manager.clear_history(history_type)

        progress.update(task, completed=1)

    if success:
        print_markdown(
            get_text("HISTORY", "clear_successful").format(history_type), "success"
        )
    else:
        print_markdown(get_text("HISTORY", "clear_failed"), "error")
        raise typer.Exit(code=1)


@history_app.command("shell")
def history_shell(
    limit: int = typer.Option(
        10, "--limit", "-n", help=get_text("HISTORY", "limit_help")
    ),
):
    """列出shell命令历史。"""
    history_manager = HistoryManager()
    records = history_manager.get_shell_history(limit=limit)

    if not records:
        print_markdown(get_text("HISTORY", "no_shell_history"), "")
        return

    table = Table(title=get_text("HISTORY", "recent_shell_history"))
    table.add_column("ID", justify="right", style="cyan")
    table.add_column(get_text("HISTORY", "timestamp"), style="green")
    table.add_column(get_text("HISTORY", "directory"), style="magenta")
    table.add_column(get_text("HISTORY", "command"), style="white")
    table.add_column(get_text("HISTORY", "exit_code"), style="yellow")

    from datetime import datetime
    from pathlib import Path

    for record in records:
        # 格式化时间戳
        dt = datetime.fromisoformat(record["timestamp"])
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")

        # 限制命令长度
        command = record["command"]
        if len(command) > 50:
            command = command[:47] + "..."

        # 格式化目录，从绝对路径转为相对路径或~
        directory = record["directory"] or ""
        if directory:
            home = str(Path.home())
            if directory.startswith(home):
                directory = "~" + directory[len(home) :]

        # 格式化退出码
        exit_code = str(record["exit_code"]) if record["exit_code"] is not None else ""

        table.add_row(str(record["id"]), formatted_time, directory, command, exit_code)

    console.print(table)


# Tools命令组
@tools_app.command("list")
def tools_list():
    """列出所有可用的MCP工具。"""
    try:
        console.print(
            Panel.fit(
                get_text("TOOLS", "listing_tools"),
                title=get_text("TOOLS", "tools_list_title"),
            )
        )

        # 使用viby_tool_search模块获取工具信息
        try:
            # 获取工具信息 - 现在返回的是按服务器分组的工具列表
            server_tools_dict = get_mcp_tools_from_cache()

            # 如果没有工具，显示提示并返回成功
            if not server_tools_dict:
                console.print(
                    f"[bold yellow]{get_text('TOOLS', 'no_tools_found')}[/bold yellow]"
                )
                return
        except Exception as e:
            console.print(
                f"[bold red]{get_text('TOOLS', 'error_listing_tools')}: {str(e)}[/bold red]"
            )
            logger.exception(get_text("TOOLS", "tools_listing_failed"))
            raise typer.Exit(code=1)

        # 显示工具信息表格
        table = Table(title=get_text("TOOLS", "available_tools_table_title"))
        table.add_column(get_text("TOOLS", "tool_name_column"), style="cyan")
        table.add_column(get_text("TOOLS", "description_column"))
        table.add_column(get_text("TOOLS", "param_count_column"), justify="right")
        table.add_column(get_text("TOOLS", "server_column"), style="dim")

        # 创建展平的工具列表，以便按名称排序
        all_tools = []
        for server_name, tools in server_tools_dict.items():
            for tool in tools:
                all_tools.append((tool.name, tool, server_name))

        # 按名称排序工具
        import textwrap

        for name, tool, server_name in sorted(all_tools, key=lambda x: x[0]):
            description = tool.description if hasattr(tool, "description") else ""
            if callable(description):
                try:
                    description = description()
                except Exception:
                    description = get_text("TOOLS", "description_unavailable")

            # 获取参数数量
            parameters = tool.inputSchema if hasattr(tool, "inputSchema") else {}
            param_properties = (
                parameters.get("properties", {}) if isinstance(parameters, dict) else {}
            )
            param_count = len(param_properties)

            # 使用textwrap简化描述截断
            short_desc = textwrap.shorten(description, width=60, placeholder="...")

            table.add_row(
                name,
                short_desc,
                str(param_count),
                server_name,
            )

        console.print(table)

        # 显示总工具数量
        total_tools = sum(len(tools) for tools in server_tools_dict.values())
        console.print(
            f"\n{get_text('TOOLS', 'total_tools')}: [bold cyan]{total_tools}[/bold cyan]"
        )

    except Exception as e:
        console.print(
            f"[bold red]{get_text('TOOLS', 'error_listing_tools')}: {str(e)}[/bold red]"
        )
        logger.exception(get_text("TOOLS", "tools_listing_failed"))
        raise typer.Exit(code=1)


# Embed子命令组
@embed_app.command("update")
def embed_update():
    """更新MCP工具的嵌入向量。"""
    embed_server_command = EmbedServerCommand()
    result = embed_server_command.update_embeddings()
    if result != 0:
        raise typer.Exit(code=result)


@embed_app.command("start")
def embed_start():
    """启动嵌入模型服务。"""
    embed_server_command = EmbedServerCommand()
    result = embed_server_command.start_embed_server()
    if result != 0:
        raise typer.Exit(code=result)


@embed_app.command("stop")
def embed_stop():
    """停止嵌入模型服务。"""
    embed_server_command = EmbedServerCommand()
    result = embed_server_command.stop_embed_server()
    if result != 0:
        raise typer.Exit(code=result)


@embed_app.command("status")
def embed_status():
    """查看嵌入模型服务状态。"""
    embed_server_command = EmbedServerCommand()
    result = embed_server_command.check_embed_server_status()
    if result != 0:
        raise typer.Exit(code=result)


@embed_app.command("download")
def embed_download():
    """下载嵌入模型。"""
    embed_server_command = EmbedServerCommand()
    result = embed_server_command.download_embedding_model()
    if result != 0:
        raise typer.Exit(code=result)


if __name__ == "__main__":
    app()
