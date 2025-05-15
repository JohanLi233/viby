#!/usr/bin/env python3
"""
测试viby/commands/history.py模块中的HistoryCommand类
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

# 模拟文本管理器初始化
with patch("viby.locale.text_manager", MagicMock()):
    with patch("viby.locale.get_text", return_value="测试文本"):
        from viby.commands.history import (
            HistoryCommand,
            cli_list,
            cli_search,
            cli_export,
            cli_clear,
            cli_shell,
        )


@pytest.fixture
def mock_history_manager():
    """创建一个模拟的HistoryManager实例"""
    return MagicMock()


@pytest.fixture
def mock_console():
    """创建一个模拟的Console实例"""
    return MagicMock()


@pytest.fixture
def history_command(mock_history_manager, mock_console):
    """创建一个HistoryCommand实例并注入模拟对象"""
    with patch(
        "viby.commands.history.HistoryManager", return_value=mock_history_manager
    ):
        with patch("viby.commands.history.Console", return_value=mock_console):
            return HistoryCommand()


@pytest.fixture
def sample_records():
    """创建样本历史记录用于测试"""
    return [
        {
            "id": 1,
            "timestamp": "2023-01-01T12:00:00",
            "type": "chat",
            "content": "测试问题1",
            "response": "测试回答1",
        },
        {
            "id": 2,
            "timestamp": "2023-01-02T12:00:00",
            "type": "ask",
            "content": "测试问题2",
            "response": "测试回答2",
        },
    ]


class TestHistoryCommand:
    """测试HistoryCommand类"""

    def test_truncate(self, history_command):
        """测试_truncate方法"""
        # 测试不需要截断的情况
        assert history_command._truncate("短文本", 10) == "短文本"

        # 测试需要截断的情况
        # 根据实际实现，可能会有不同的截断方式，这里使用模糊断言
        truncated = history_command._truncate("这是一个很长的文本需要被截断", 10)
        assert truncated.startswith("这是")
        assert truncated.endswith("...")
        assert len(truncated) <= 10 + 3  # 长度不超过限制加省略号

        # 测试边界情况
        assert history_command._truncate("正好十个字符", 10) == "正好十个字符"
        # 边界情况下不应截断，因为长度小于等于限制
        truncated_edge = history_command._truncate("正好十个字符加一", 10)
        assert truncated_edge == "正好十个字符加一"

    @patch("viby.commands.history.Table")
    def test_format_records(
        self, mock_table, history_command, sample_records, mock_console
    ):
        """测试_format_records方法"""
        # 模拟Table实例
        mock_table_instance = MagicMock()
        mock_table.return_value = mock_table_instance

        # 调用被测试方法
        history_command._format_records(sample_records, "测试标题", 50)

        # 验证Table创建
        mock_table.assert_called_once_with(title="测试标题")

        # 验证列添加
        assert mock_table_instance.add_column.call_count == 5

        # 验证行添加
        assert mock_table_instance.add_row.call_count == len(sample_records)

        # 验证Console打印
        mock_console.print.assert_called_once_with(mock_table_instance)

    def test_list_history_with_records(
        self, history_command, sample_records, mock_history_manager
    ):
        """测试list_history方法（有记录）"""
        # 设置mock返回值
        mock_history_manager.get_history.return_value = sample_records

        # 调用被测试方法
        with patch.object(history_command, "_format_records") as mock_format:
            result = history_command.list_history(5)

        # 验证调用和返回值
        mock_history_manager.get_history.assert_called_once_with(limit=5)
        mock_format.assert_called_once()
        assert result == 0

    @patch("viby.commands.history.print_markdown")
    def test_list_history_no_records(
        self, mock_print_markdown, history_command, mock_history_manager
    ):
        """测试list_history方法（无记录）"""
        # 设置mock返回值
        mock_history_manager.get_history.return_value = []

        # 调用被测试方法
        result = history_command.list_history()

        # 验证调用和返回值
        mock_history_manager.get_history.assert_called_once_with(limit=10)
        mock_print_markdown.assert_called_once()
        assert result == 0

    def test_search_history_with_results(
        self, history_command, sample_records, mock_history_manager
    ):
        """测试search_history方法（有结果）"""
        # 设置mock返回值
        mock_history_manager.get_history.return_value = sample_records

        # 调用被测试方法
        with patch.object(history_command, "_format_records") as mock_format:
            result = history_command.search_history("测试", 5)

        # 验证调用和返回值
        mock_history_manager.get_history.assert_called_once_with(
            limit=5, search_query="测试"
        )
        mock_format.assert_called_once()
        assert result == 0

    @patch("viby.commands.history.print_markdown")
    def test_search_history_no_results(
        self, mock_print_markdown, history_command, mock_history_manager
    ):
        """测试search_history方法（无结果）"""
        # 设置mock返回值
        mock_history_manager.get_history.return_value = []

        # 调用被测试方法
        result = history_command.search_history("找不到", 5)

        # 验证调用和返回值
        mock_history_manager.get_history.assert_called_once_with(
            limit=5, search_query="找不到"
        )
        mock_print_markdown.assert_called_once()
        assert result == 0

    @patch("viby.commands.history.print_markdown")
    def test_search_history_empty_query(self, mock_print_markdown, history_command):
        """测试search_history方法（空查询）"""
        # 调用被测试方法
        result = history_command.search_history("", 5)

        # 验证调用和返回值
        mock_print_markdown.assert_called_once()
        assert result == 1

    @patch("viby.commands.history.os.path.exists")
    @patch("viby.commands.history.os.path.dirname")
    @patch("viby.commands.history.print_markdown")
    def test_export_history_success(
        self,
        mock_print_markdown,
        mock_dirname,
        mock_exists,
        history_command,
    ):
        """测试export_history方法（成功）"""
        # 重新设置history_manager以解决调用问题
        mock_history_manager = MagicMock()
        history_command.history_manager = mock_history_manager
        mock_history_manager.export_history.return_value = True

        # 设置mock返回值
        # 让dirname返回空字符串以跳过目录创建路径
        mock_dirname.return_value = ""
        mock_exists.return_value = False

        # 调用被测试方法
        with patch("viby.commands.history.Progress") as mock_progress:
            mock_progress_instance = MagicMock()
            mock_progress.return_value.__enter__.return_value = mock_progress_instance
            result = history_command.export_history(
                "output.json", "json", "interactions"
            )

        # 验证调用和返回值
        mock_history_manager.export_history.assert_called_once_with(
            "output.json", "json", "interactions"
        )
        mock_print_markdown.assert_called_once()
        assert result == 0

    @patch("viby.commands.history.os.path.exists")
    @patch("viby.commands.history.os.makedirs")
    @patch("viby.commands.history.print_markdown")
    def test_export_history_directory_creation(
        self,
        mock_print_markdown,
        mock_makedirs,
        mock_exists,
        history_command,
        mock_history_manager,
    ):
        """测试export_history方法（创建目录）"""
        # 设置mock返回值
        mock_exists.return_value = False
        mock_history_manager.export_history.return_value = True

        # 调用被测试方法
        with patch("viby.commands.history.Progress") as mock_progress:
            mock_progress_instance = MagicMock()
            mock_progress.return_value.__enter__.return_value = mock_progress_instance
            with patch(
                "viby.commands.history.os.path.dirname", return_value="/fake/path"
            ):
                result = history_command.export_history("/fake/path/output.json")

        # 验证目录创建
        mock_makedirs.assert_called_once_with("/fake/path")
        assert result == 0

    @patch("viby.commands.history.Confirm.ask")
    @patch("viby.commands.history.print_markdown")
    def test_clear_history_confirmed(
        self, mock_print_markdown, mock_confirm, history_command, mock_history_manager
    ):
        """测试clear_history方法（确认）"""
        # 设置mock返回值
        mock_confirm.return_value = True
        mock_history_manager.clear_history.return_value = True

        # 调用被测试方法
        with patch("viby.commands.history.Progress") as mock_progress:
            mock_progress_instance = MagicMock()
            mock_progress.return_value.__enter__.return_value = mock_progress_instance
            result = history_command.clear_history()

        # 验证调用和返回值
        mock_confirm.assert_called_once()
        mock_history_manager.clear_history.assert_called_once_with()
        assert result == 0

    @patch("viby.commands.history.Table")
    def test_list_shell_history(
        self, mock_table, history_command, mock_history_manager, mock_console
    ):
        """测试list_shell_history方法"""
        # 创建样本shell历史记录
        shell_records = [
            {
                "id": 1,
                "timestamp": "2023-01-01T12:00:00",
                "directory": "/home/user",
                "command": "ls -la",
                "exit_code": 0,
            }
        ]

        # 设置mock返回值
        mock_history_manager.get_shell_history.return_value = shell_records
        mock_table_instance = MagicMock()
        mock_table.return_value = mock_table_instance

        # 设置Path.home()的返回值
        with patch.object(Path, "home", return_value=Path("/home")):
            result = history_command.list_shell_history(5)

        # 验证调用和返回值
        mock_history_manager.get_shell_history.assert_called_once_with(limit=5)
        mock_table.assert_called_once()
        assert mock_table_instance.add_column.call_count == 5
        assert mock_table_instance.add_row.call_count == 1
        mock_console.print.assert_called_once_with(mock_table_instance)
        assert result == 0


# CLI适配器测试


@patch("viby.commands.history.HistoryCommand")
@patch("viby.commands.history.typer")
def test_cli_list(mock_typer, mock_history_command):
    """测试cli_list函数"""
    # 设置模拟对象
    mock_command_instance = MagicMock()
    mock_history_command.return_value = mock_command_instance
    mock_command_instance.list_history.return_value = 0

    # 创建一个MagicMock作为typer.Exit异常
    mock_exit = MagicMock()
    mock_typer.Exit = mock_exit

    # 设置typer.Exit被调用时抛出异常
    mock_exit.side_effect = Exception("Mocked typer.Exit")

    # 调用cli_list函数
    with pytest.raises(Exception):
        cli_list(5)

    # 验证函数调用
    mock_history_command.assert_called_once()
    mock_command_instance.list_history.assert_called_once_with(5)
    mock_exit.assert_called_once_with(code=0)


@patch("viby.commands.history.HistoryCommand")
@patch("viby.commands.history.typer")
def test_cli_search(mock_typer, mock_history_command):
    """测试cli_search函数"""
    # 设置模拟对象
    mock_command_instance = MagicMock()
    mock_history_command.return_value = mock_command_instance
    mock_command_instance.search_history.return_value = 0

    # 创建一个MagicMock作为typer.Exit异常
    mock_exit = MagicMock()
    mock_typer.Exit = mock_exit

    # 设置typer.Exit被调用时抛出异常
    mock_exit.side_effect = Exception("Mocked typer.Exit")

    # 调用cli_search函数
    with pytest.raises(Exception):
        cli_search("测试查询", 5)

    # 验证函数调用
    mock_history_command.assert_called_once()
    mock_command_instance.search_history.assert_called_once_with("测试查询", 5)
    mock_exit.assert_called_once_with(code=0)


@patch("viby.commands.history.HistoryCommand")
@patch("viby.commands.history.typer")
def test_cli_export(mock_typer, mock_history_command):
    """测试cli_export函数"""
    # 设置模拟对象
    mock_command_instance = MagicMock()
    mock_history_command.return_value = mock_command_instance
    mock_command_instance.export_history.return_value = 0

    # 创建一个MagicMock作为typer.Exit异常
    mock_exit = MagicMock()
    mock_typer.Exit = mock_exit

    # 设置typer.Exit被调用时抛出异常
    mock_exit.side_effect = Exception("Mocked typer.Exit")

    # 调用cli_export函数
    with pytest.raises(Exception):
        cli_export("output.json")

    # 验证函数调用
    mock_history_command.assert_called_once()
    mock_command_instance.export_history.assert_called_once_with("output.json")
    mock_exit.assert_called_once_with(code=0)


@patch("viby.commands.history.HistoryCommand")
@patch("viby.commands.history.typer")
def test_cli_clear(mock_typer, mock_history_command):
    """测试cli_clear函数"""
    # 设置模拟对象
    mock_command_instance = MagicMock()
    mock_history_command.return_value = mock_command_instance
    mock_command_instance.clear_history.return_value = 0

    # 创建一个MagicMock作为typer.Exit异常
    mock_exit = MagicMock()
    mock_typer.Exit = mock_exit

    # 设置typer.Exit被调用时抛出异常
    mock_exit.side_effect = Exception("Mocked typer.Exit")

    # 调用cli_clear函数
    with pytest.raises(Exception):
        cli_clear()

    # 验证函数调用
    mock_history_command.assert_called_once()
    mock_command_instance.clear_history.assert_called_once_with()
    mock_exit.assert_called_once_with(code=0)


@patch("viby.commands.history.HistoryCommand")
@patch("viby.commands.history.typer")
def test_cli_shell(mock_typer, mock_history_command):
    """测试cli_shell函数"""
    # 设置模拟对象
    mock_command_instance = MagicMock()
    mock_history_command.return_value = mock_command_instance
    mock_command_instance.list_shell_history.return_value = 0

    # 创建一个MagicMock作为typer.Exit异常
    mock_exit = MagicMock()
    mock_typer.Exit = mock_exit

    # 设置typer.Exit被调用时抛出异常
    mock_exit.side_effect = Exception("Mocked typer.Exit")

    # 调用cli_shell函数
    with pytest.raises(Exception):
        cli_shell(5)

    # 验证函数调用
    mock_history_command.assert_called_once()
    mock_command_instance.list_shell_history.assert_called_once_with(5)
    mock_exit.assert_called_once_with(code=0)
