#!/usr/bin/env python3
"""
测试viby/commands/sessions.py模块中的SessionsCommand类
"""

import pytest
from unittest.mock import patch, MagicMock

# 模拟文本管理器初始化
with patch("viby.locale.text_manager", MagicMock()):
    with patch("viby.locale.get_text", return_value="测试文本"):
        from viby.commands.sessions import (
            SessionsCommand,
            cli_list,
            cli_search,
            cli_export,
            cli_clear,
        )


@pytest.fixture
def mock_session_manager():
    """创建一个模拟的SessionManager实例"""
    return MagicMock()


@pytest.fixture
def mock_console():
    """创建一个模拟的Console实例"""
    return MagicMock()


@pytest.fixture
def sessions_command(mock_session_manager, mock_console):
    """创建一个SessionsCommand实例并注入模拟对象"""
    with patch(
        "viby.commands.sessions.SessionManager", return_value=mock_session_manager
    ):
        with patch("viby.commands.sessions.Console", return_value=mock_console):
            return SessionsCommand()


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


class TestSessionsCommand:
    """测试SessionsCommand类"""

    def test_truncate(self, sessions_command):
        """测试_truncate方法"""
        # 测试不需要截断的情况
        assert sessions_command._truncate("短文本", 10) == "短文本"

        # 测试需要截断的情况
        # 根据实际实现，可能会有不同的截断方式，这里使用模糊断言
        truncated = sessions_command._truncate("这是一个很长的文本需要被截断", 10)
        assert truncated.startswith("这是")
        assert truncated.endswith("...")
        assert len(truncated) <= 10 + 3  # 长度不超过限制加省略号

        # 测试边界情况
        assert sessions_command._truncate("正好十个字符", 10) == "正好十个字符"
        # 边界情况下不应截断，因为长度小于等于限制
        truncated_edge = sessions_command._truncate("正好十个字符加一", 10)
        assert truncated_edge == "正好十个字符加一"

    @patch("viby.commands.sessions.Table")
    def test_format_records(
        self, mock_table, sessions_command, sample_records, mock_console
    ):
        """测试_format_records方法"""
        # 模拟Table实例
        mock_table_instance = MagicMock()
        mock_table.return_value = mock_table_instance

        # 调用被测试方法
        sessions_command._format_records(sample_records, "测试标题", 50)

        # 验证Table创建
        mock_table.assert_called_once_with(title="测试标题")

        # 验证列添加
        assert mock_table_instance.add_column.call_count == 5

        # 验证行添加
        assert mock_table_instance.add_row.call_count == len(sample_records)

        # 验证Console打印
        mock_console.print.assert_called_once_with(mock_table_instance)

    def test_show_history_with_records(
        self, sessions_command, sample_records, mock_session_manager
    ):
        """测试show_history方法（有记录）"""
        # 设置mock返回值
        mock_session_manager.get_history.return_value = sample_records

        # 调用被测试方法
        with patch.object(sessions_command, "_format_records") as mock_format:
            result = sessions_command.show_history(5)

        # 验证调用和返回值
        mock_session_manager.get_history.assert_called_once_with(
            limit=5, session_id=None
        )
        mock_format.assert_called_once()
        assert result == 0

    @patch("viby.commands.sessions.print_markdown")
    def test_show_history_no_records(
        self, mock_print_markdown, sessions_command, mock_session_manager
    ):
        """测试show_history方法（无记录）"""
        # 设置mock返回值
        mock_session_manager.get_history.return_value = []

        # 调用被测试方法
        result = sessions_command.show_history()

        # 验证调用和返回值
        mock_session_manager.get_history.assert_called_once_with(
            limit=10, session_id=None
        )
        mock_print_markdown.assert_called_once()
        assert result == 0

    def test_search_history_with_results(
        self, sessions_command, sample_records, mock_session_manager
    ):
        """测试search_history方法（有结果）"""
        # 设置mock返回值
        mock_session_manager.get_history.return_value = sample_records

        # 调用被测试方法
        with patch.object(sessions_command, "_format_records") as mock_format:
            result = sessions_command.search_history("测试", 5)

        # 验证调用和返回值
        mock_session_manager.get_history.assert_called_once_with(
            limit=5, search_query="测试", session_id=None
        )
        mock_format.assert_called_once()
        assert result == 0

    @patch("viby.commands.sessions.print_markdown")
    def test_search_history_no_results(
        self, mock_print_markdown, sessions_command, mock_session_manager
    ):
        """测试search_history方法（无结果）"""
        # 设置mock返回值
        mock_session_manager.get_history.return_value = []

        # 调用被测试方法
        result = sessions_command.search_history("找不到", 5)

        # 验证调用和返回值
        mock_session_manager.get_history.assert_called_once_with(
            limit=5, search_query="找不到", session_id=None
        )
        mock_print_markdown.assert_called_once()
        assert result == 0

    @patch("viby.commands.sessions.print_markdown")
    def test_search_history_empty_query(self, mock_print_markdown, sessions_command):
        """测试search_history方法（空查询）"""
        # 调用被测试方法
        result = sessions_command.search_history("", 5)

        # 验证调用和返回值
        mock_print_markdown.assert_called_once()
        assert result == 1

    @patch("viby.commands.sessions.os.path.exists")
    @patch("viby.commands.sessions.os.path.dirname")
    @patch("viby.commands.sessions.print_markdown")
    def test_export_history_success(
        self,
        mock_print_markdown,
        mock_dirname,
        mock_exists,
        sessions_command,
    ):
        """测试export_history方法（成功）"""
        # 重新设置session_manager以解决调用问题
        mock_session_manager = MagicMock()
        sessions_command.session_manager = mock_session_manager
        mock_session_manager.export_history.return_value = True

        # 设置mock返回值
        # 让dirname返回空字符串以跳过目录创建路径
        mock_dirname.return_value = ""
        mock_exists.return_value = False

        # 调用被测试方法
        with patch("viby.commands.sessions.Progress") as mock_progress:
            mock_progress_instance = MagicMock()
            mock_progress.return_value.__enter__.return_value = mock_progress_instance
            result = sessions_command.export_history("output.json", "json", None)

        # 验证调用和返回值
        mock_session_manager.export_history.assert_called_once_with(
            "output.json", "json", None
        )
        mock_print_markdown.assert_called_once()
        assert result == 0

    @patch("viby.commands.sessions.os.path.exists")
    @patch("viby.commands.sessions.os.makedirs")
    @patch("viby.commands.sessions.print_markdown")
    def test_export_history_directory_creation(
        self,
        mock_print_markdown,
        mock_makedirs,
        mock_exists,
        sessions_command,
        mock_session_manager,
    ):
        """测试export_history方法（创建目录）"""
        # 设置mock返回值
        mock_exists.return_value = False
        mock_session_manager.export_history.return_value = True

        # 调用被测试方法
        with patch("viby.commands.sessions.Progress") as mock_progress:
            mock_progress_instance = MagicMock()
            mock_progress.return_value.__enter__.return_value = mock_progress_instance
            with patch(
                "viby.commands.sessions.os.path.dirname", return_value="/fake/path"
            ):
                result = sessions_command.export_history("/fake/path/output.json")

        # 验证目录创建
        mock_makedirs.assert_called_once_with("/fake/path")
        assert result == 0

    @patch("viby.commands.sessions.Confirm.ask")
    @patch("viby.commands.sessions.print_markdown")
    def test_clear_history_confirmed(
        self, mock_print_markdown, mock_confirm, sessions_command, mock_session_manager
    ):
        """测试clear_history方法（确认）"""
        # 设置mock返回值
        mock_confirm.return_value = True
        mock_session_manager.clear_history.return_value = True

        # 调用被测试方法
        with patch("viby.commands.sessions.Progress") as mock_progress:
            mock_progress_instance = MagicMock()
            mock_progress.return_value.__enter__.return_value = mock_progress_instance
            result = sessions_command.clear_history()

        # 验证调用和返回值
        mock_confirm.assert_called_once()
        mock_session_manager.clear_history.assert_called_once_with(None)
        assert result == 0

    def test_list_sessions(self, sessions_command, mock_session_manager, mock_console):
        """测试list_sessions方法"""
        # 创建样本会话列表
        sample_sessions = [
            {
                "id": "1",
                "name": "测试会话1",
                "created_at": "2023-01-01T10:00:00",
                "last_used": "2023-01-01T12:00:00",
                "is_active": 1,
                "interaction_count": 5,
            },
            {
                "id": "2",
                "name": "测试会话2",
                "created_at": "2023-01-02T10:00:00",
                "last_used": "2023-01-02T12:00:00",
                "is_active": 0,
                "interaction_count": 3,
            },
        ]

        # 设置mock返回值
        mock_session_manager.get_sessions.return_value = sample_sessions

        # 使用Table模拟
        with patch("viby.commands.sessions.Table") as mock_table:
            mock_table_instance = MagicMock()
            mock_table.return_value = mock_table_instance

            # 调用被测试方法
            result = sessions_command.list_sessions()

            # 验证调用和返回值
            mock_session_manager.get_sessions.assert_called_once()
            mock_table.assert_called_once()
            assert mock_table_instance.add_column.call_count == 6
            assert mock_table_instance.add_row.call_count == 2
            mock_console.print.assert_called_once_with(mock_table_instance)
            assert result == 0

    @patch("viby.commands.sessions.print_markdown")
    def test_list_sessions_no_sessions(
        self, mock_print_markdown, sessions_command, mock_session_manager
    ):
        """测试list_sessions方法（无会话）"""
        # 设置mock返回值
        mock_session_manager.get_sessions.return_value = []

        # 调用被测试方法
        result = sessions_command.list_sessions()

        # 验证调用和返回值
        mock_session_manager.get_sessions.assert_called_once()
        mock_print_markdown.assert_called_once()
        assert result == 0


# CLI适配器测试


@patch("viby.commands.sessions.SessionsCommand")
@patch("viby.commands.sessions.typer")
def test_cli_list(mock_typer, mock_sessions_command):
    """测试cli_list函数"""
    # 设置模拟对象
    mock_command_instance = MagicMock()
    mock_sessions_command.return_value = mock_command_instance
    mock_command_instance.list_sessions.return_value = 0

    # 创建一个MagicMock作为typer.Exit异常
    mock_exit = MagicMock()
    mock_typer.Exit = mock_exit

    # 设置typer.Exit被调用时抛出异常
    mock_exit.side_effect = Exception("Mocked typer.Exit")

    # 调用cli_list函数
    with pytest.raises(Exception):
        cli_list()

    # 验证函数调用
    mock_sessions_command.assert_called_once()
    mock_command_instance.list_sessions.assert_called_once()
    mock_exit.assert_called_once_with(code=0)


@patch("viby.commands.sessions.SessionsCommand")
@patch("viby.commands.sessions.typer")
def test_cli_search(mock_typer, mock_sessions_command):
    """测试cli_search函数"""
    # 设置模拟对象
    mock_command_instance = MagicMock()
    mock_sessions_command.return_value = mock_command_instance
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
    mock_sessions_command.assert_called_once()
    # 不能直接检查参数值，因为第三个参数是typer.Option
    mock_command_instance.search_history.assert_called_once()
    # 检查前两个参数值是否匹配
    assert mock_command_instance.search_history.call_args[0][0] == "测试查询"
    assert mock_command_instance.search_history.call_args[0][1] == 5
    mock_exit.assert_called_once_with(code=0)


@patch("viby.commands.sessions.SessionsCommand")
@patch("viby.commands.sessions.typer")
def test_cli_export(mock_typer, mock_sessions_command):
    """测试cli_export函数"""
    # 设置模拟对象
    mock_command_instance = MagicMock()
    mock_sessions_command.return_value = mock_command_instance
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
    mock_sessions_command.assert_called_once()
    # 不能直接检查参数值，因为第二个和第三个参数是typer.Option
    mock_command_instance.export_history.assert_called_once()
    # 检查第一个参数值是否匹配
    assert mock_command_instance.export_history.call_args[0][0] == "output.json"
    mock_exit.assert_called_once_with(code=0)


@patch("viby.commands.sessions.SessionsCommand")
@patch("viby.commands.sessions.typer")
def test_cli_clear(mock_typer, mock_sessions_command):
    """测试cli_clear函数"""
    # 设置模拟对象
    mock_command_instance = MagicMock()
    mock_sessions_command.return_value = mock_command_instance
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
    mock_sessions_command.assert_called_once()
    # 不能直接检查参数值，因为参数是typer.Option
    mock_command_instance.clear_history.assert_called_once()
    mock_exit.assert_called_once_with(code=0)
