#!/usr/bin/env python3
"""
测试viby/commands/shortcuts.py模块中的ShortcutsCommand类
"""

import pytest
from unittest.mock import patch, MagicMock

# 模拟文本管理器初始化
with patch("viby.locale.text_manager", MagicMock()):
    with patch("viby.locale.get_text", return_value="测试文本"):
        from viby.commands.shortcuts import ShortcutsCommand, cli


class TestShortcutsCommand:
    """测试ShortcutsCommand类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.command = ShortcutsCommand()

    @patch("viby.commands.shortcuts.detect_shell")
    @patch("viby.commands.shortcuts.install_shortcuts")
    def test_run_with_shell(self, mock_install, mock_detect):
        """测试指定shell的run方法"""
        # 设置返回值
        mock_install.return_value = {"status": "success", "message": "快捷键已成功安装"}

        # 调用被测试方法
        with patch.object(self.command, "_print_result") as mock_print:
            result = self.command.run("bash")

        # 验证调用和返回值
        mock_detect.assert_not_called()  # 不应该检测shell
        mock_install.assert_called_once_with("bash")
        mock_print.assert_called_once()
        assert result == 0

    @patch("viby.commands.shortcuts.detect_shell")
    @patch("viby.commands.shortcuts.install_shortcuts")
    def test_run_auto_detect_success(self, mock_install, mock_detect):
        """测试自动检测shell成功的run方法"""
        # 设置返回值
        mock_detect.return_value = "zsh"
        mock_install.return_value = {"status": "success", "message": "快捷键已成功安装"}

        # 调用被测试方法
        with patch("builtins.print") as mock_print:
            with patch.object(self.command, "_print_result") as mock_print_result:
                result = self.command.run()

        # 验证调用和返回值
        mock_detect.assert_called_once()
        mock_install.assert_called_once_with("zsh")
        mock_print.assert_called_once()  # 应该打印检测到的shell
        mock_print_result.assert_called_once()
        assert result == 0

    @patch("viby.commands.shortcuts.detect_shell")
    @patch("viby.commands.shortcuts.install_shortcuts")
    def test_run_auto_detect_fail(self, mock_install, mock_detect):
        """测试自动检测shell失败的run方法"""
        # 设置返回值
        mock_detect.return_value = None
        mock_install.return_value = {"status": "error", "message": "无法安装快捷键"}

        # 调用被测试方法
        with patch("builtins.print") as mock_print:
            with patch.object(self.command, "_print_result") as mock_print_result:
                result = self.command.run()

        # 验证调用和返回值
        mock_detect.assert_called_once()
        mock_install.assert_called_once_with(None)
        mock_print.assert_called_once()  # 应该打印检测失败消息
        mock_print_result.assert_called_once()
        assert result == 1

    @patch("builtins.print")
    def test_print_result_success(self, mock_print):
        """测试打印成功结果"""
        result = {"status": "success", "message": "快捷键已成功安装"}

        self.command._print_result(result)

        # 验证打印调用
        assert mock_print.call_count == 2  # 一次状态消息，一次激活提示

    @patch("builtins.print")
    def test_print_result_info(self, mock_print):
        """测试打印信息结果"""
        result = {"status": "info", "message": "快捷键已经安装"}

        self.command._print_result(result)

        # 验证打印调用
        assert mock_print.call_count == 1  # 只打印状态消息，没有激活提示

    @patch("builtins.print")
    def test_print_result_error(self, mock_print):
        """测试打印错误结果"""
        result = {
            "status": "error",
            "message": "无法安装快捷键",
            "action_required": "请手动安装",
        }

        self.command._print_result(result)

        # 验证打印调用
        assert mock_print.call_count == 2  # 状态消息和操作建议


@patch("viby.commands.shortcuts.ShortcutsCommand")
@patch("viby.commands.shortcuts.typer")
def test_cli(mock_typer, mock_shortcuts_command):
    """测试cli函数"""
    # 设置模拟对象
    mock_command_instance = MagicMock()
    mock_shortcuts_command.return_value = mock_command_instance
    mock_command_instance.run.return_value = 0

    # 创建一个MagicMock作为typer.Exit异常
    mock_exit = MagicMock()
    mock_typer.Exit = mock_exit

    # 设置typer.Exit被调用时抛出异常
    mock_exit.side_effect = Exception("Mocked typer.Exit")

    # 调用cli函数
    with pytest.raises(Exception):
        cli("bash")

    # 验证函数调用
    mock_shortcuts_command.assert_called_once()
    mock_command_instance.run.assert_called_once_with("bash")
    mock_exit.assert_called_once_with(code=0)

    # 测试错误情况
    mock_shortcuts_command.reset_mock()
    mock_command_instance.reset_mock()
    mock_typer.reset_mock()
    mock_exit.reset_mock()

    # 重新设置mock
    mock_command_instance = MagicMock()
    mock_shortcuts_command.return_value = mock_command_instance
    mock_command_instance.run.return_value = 1

    # 创建一个新的MagicMock作为typer.Exit异常
    mock_exit = MagicMock()
    mock_typer.Exit = mock_exit

    # 设置typer.Exit被调用时抛出异常
    mock_exit.side_effect = Exception("Mocked typer.Exit")

    with pytest.raises(Exception):
        cli(None)

    mock_shortcuts_command.assert_called_once()
    mock_command_instance.run.assert_called_once_with(None)
    mock_exit.assert_called_once_with(code=1)
