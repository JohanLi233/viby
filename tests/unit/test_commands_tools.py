#!/usr/bin/env python3
"""
测试viby/commands/tools.py模块中的ToolsCommand类
"""

import pytest
from unittest.mock import patch, MagicMock
import logging

# 禁用viby.commands.tools模块的logger
logging.getLogger("viby.commands.tools").disabled = True

# 模拟文本管理器初始化
with patch("viby.locale.text_manager", MagicMock()):
    with patch("viby.locale.get_text", return_value="测试文本"):
        from viby.commands.tools import ToolsCommand, cli_list, cli_embed


@pytest.fixture
def mock_config():
    """创建一个模拟的Config实例"""
    return MagicMock()


@pytest.fixture
def mock_embed_server_command():
    """创建一个模拟的EmbedServerCommand实例"""
    return MagicMock()


@pytest.fixture
def tools_command(mock_config, mock_embed_server_command):
    """创建一个ToolsCommand实例并注入模拟对象"""
    with patch("viby.commands.tools.config", mock_config):
        with patch(
            "viby.commands.tools.EmbedServerCommand",
            return_value=mock_embed_server_command,
        ):
            with patch("viby.commands.tools.console", MagicMock()) as mock_console:
                tool_cmd = ToolsCommand()
                tool_cmd.console = mock_console  # 确保console是模拟对象
                return tool_cmd


class TestToolsCommand:
    """测试ToolsCommand类"""

    @patch("viby.commands.tools.get_mcp_tools_from_cache")
    @patch("viby.commands.tools.Panel")
    @patch("viby.commands.tools.Table")
    def test_list_tools_success(
        self, mock_table, mock_panel, mock_get_tools, tools_command
    ):
        """测试list_tools方法（成功）"""
        # 创建样本工具列表
        tool1 = MagicMock()
        tool1.name = "tool1"
        tool1.description = "工具1的描述"
        tool1.inputSchema = {"properties": {"param1": {}, "param2": {}}}

        tool2 = MagicMock()
        tool2.name = "tool2"
        tool2.description = "工具2的描述"
        tool2.inputSchema = {"properties": {"param1": {}}}

        server_tools = {"server1": [tool1], "server2": [tool2]}

        # 设置mock返回值
        mock_get_tools.return_value = server_tools
        mock_table_instance = MagicMock()
        mock_table.return_value = mock_table_instance
        mock_panel_instance = MagicMock()
        mock_panel.fit.return_value = mock_panel_instance

        # 调用被测试方法
        result = tools_command.list_tools()

        # 验证调用和返回值
        mock_get_tools.assert_called_once()
        mock_panel.fit.assert_called_once()
        mock_table.assert_called_once()
        assert mock_table_instance.add_column.call_count == 4
        assert mock_table_instance.add_row.call_count == 2
        assert result == 0

    @patch("viby.commands.tools.get_mcp_tools_from_cache")
    @patch("viby.commands.tools.Panel")
    def test_list_tools_no_tools(self, mock_panel, mock_get_tools, tools_command):
        """测试list_tools方法（无工具）"""
        # 设置mock返回值为空字典，触发无工具分支
        mock_get_tools.return_value = {}
        mock_panel_instance = MagicMock()
        mock_panel.fit.return_value = mock_panel_instance
        # 模拟console全局变量
        with patch("viby.commands.tools.console") as mock_console:
            result = tools_command.list_tools()
            mock_console.print.assert_called()
        mock_get_tools.assert_called_once()
        mock_panel.fit.assert_called_once()
        assert result == 0

    @patch("viby.commands.tools.get_mcp_tools_from_cache")
    @patch("viby.commands.tools.Panel")
    def test_list_tools_exception(self, mock_panel, mock_get_tools, tools_command):
        """测试list_tools方法（异常）"""
        # 设置mock抛出异常，触发异常分支
        mock_get_tools.side_effect = Exception("测试异常")
        mock_panel_instance = MagicMock()
        mock_panel.fit.return_value = mock_panel_instance
        # 模拟console全局变量
        with patch("viby.commands.tools.console") as mock_console:
            result = tools_command.list_tools()
            mock_console.print.assert_called()
        mock_get_tools.assert_called_once()
        mock_panel.fit.assert_called_once()
        assert result == 1

    def test_run_without_subcommand(self, tools_command, mock_embed_server_command):
        """测试run方法（无子命令）"""
        # 设置mock返回值
        mock_embed_server_command.update_embeddings.return_value = 0

        # 调用被测试方法
        result = tools_command.run()

        # 验证调用和返回值
        mock_embed_server_command.update_embeddings.assert_called_once()
        mock_embed_server_command.run.assert_not_called()
        assert result == 0

    def test_run_with_subcommand(self, tools_command, mock_embed_server_command):
        """测试run方法（有子命令）"""
        # 设置mock返回值
        mock_embed_server_command.run.return_value = 0

        # 调用被测试方法
        result = tools_command.run("start")

        # 验证调用和返回值
        mock_embed_server_command.update_embeddings.assert_not_called()
        mock_embed_server_command.run.assert_called_once_with("start")
        assert result == 0


# CLI适配器测试


@patch("viby.commands.tools.ToolsCommand")
@patch("viby.commands.tools.typer")
def test_cli_list(mock_typer, mock_tools_command):
    """测试cli_list函数"""
    # 设置模拟对象
    mock_command_instance = MagicMock()
    mock_tools_command.return_value = mock_command_instance
    mock_command_instance.list_tools.return_value = 0

    # 创建一个MagicMock作为typer.Exit异常
    mock_exit = MagicMock()
    mock_typer.Exit = mock_exit

    # 设置typer.Exit被调用时抛出异常
    mock_exit.side_effect = Exception("Mocked typer.Exit")

    # 调用cli_list函数
    with pytest.raises(Exception):
        cli_list()

    # 验证函数调用
    mock_tools_command.assert_called_once()
    mock_command_instance.list_tools.assert_called_once()
    mock_exit.assert_called_once_with(code=0)


@patch("viby.commands.tools.ToolsCommand")
@patch("viby.commands.tools.typer")
def test_cli_embed(mock_typer, mock_tools_command):
    """测试cli_embed函数"""
    # 设置模拟对象
    mock_command_instance = MagicMock()
    mock_tools_command.return_value = mock_command_instance
    mock_command_instance.run.return_value = 0

    # 创建一个MagicMock作为typer.Exit异常
    mock_exit = MagicMock()
    mock_typer.Exit = mock_exit

    # 设置typer.Exit被调用时抛出异常
    mock_exit.side_effect = Exception("Mocked typer.Exit")

    # 调用cli_embed函数
    with pytest.raises(Exception):
        cli_embed("start")

    # 验证函数调用
    mock_tools_command.assert_called_once()
    mock_command_instance.run.assert_called_once_with("start")
    mock_exit.assert_called_once_with(code=0)

    # 测试无子命令
    mock_tools_command.reset_mock()
    mock_command_instance.reset_mock()
    mock_typer.reset_mock()
    mock_exit.reset_mock()

    # 重新设置mock
    mock_command_instance = MagicMock()
    mock_tools_command.return_value = mock_command_instance
    mock_command_instance.run.return_value = 0

    # 创建一个新的MagicMock作为typer.Exit异常
    mock_exit = MagicMock()
    mock_typer.Exit = mock_exit

    # 设置typer.Exit被调用时抛出异常
    mock_exit.side_effect = Exception("Mocked typer.Exit")

    with pytest.raises(Exception):
        cli_embed(None)

    mock_tools_command.assert_called_once()
    mock_command_instance.run.assert_called_once_with(None)
    mock_exit.assert_called_once_with(code=0)
