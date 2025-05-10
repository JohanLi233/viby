"""
测试shell命令处理器的yolo模式功能
"""

from unittest.mock import patch

from viby.llm.nodes.handlers.shell_handler import (
    set_yolo_mode,
    is_yolo_mode_enabled,
    _is_unsafe_command,
    handle_shell_command,
    UNSAFE_COMMANDS,
)


def test_yolo_mode_config():
    """测试yolo模式的配置功能"""
    # 保存初始状态以便测试后恢复
    initial_state = is_yolo_mode_enabled()

    try:
        # 开启yolo模式
        assert set_yolo_mode(True) is True
        assert is_yolo_mode_enabled() is True

        # 关闭yolo模式
        assert set_yolo_mode(False) is False
        assert is_yolo_mode_enabled() is False
    finally:
        # 恢复初始状态
        set_yolo_mode(initial_state)


def test_unsafe_command_detection():
    """测试不安全命令检测功能"""
    # 安全命令
    assert _is_unsafe_command("ls -la") is False
    assert _is_unsafe_command("echo 'Hello World'") is False
    assert _is_unsafe_command("grep -r 'pattern' .") is False

    # 不安全命令
    for unsafe_cmd in UNSAFE_COMMANDS:
        # 在命令前后添加内容以测试子字符串匹配
        assert _is_unsafe_command(f"prefix {unsafe_cmd} suffix") is True


@patch("viby.llm.nodes.handlers.shell_handler.is_yolo_mode_enabled")
@patch("viby.llm.nodes.handlers.shell_handler._execute_command")
@patch("viby.llm.nodes.handlers.shell_handler.prompt")
@patch("viby.llm.nodes.handlers.shell_handler.print")
def test_handle_shell_command_yolo_safe(
    mock_print, mock_prompt, mock_execute, mock_is_yolo_enabled
):
    """测试yolo模式下处理安全命令"""
    # 模拟yolo模式开启
    mock_is_yolo_enabled.return_value = True
    mock_execute.return_value = {"status": "executed", "code": 0}

    # 测试安全命令自动执行
    safe_command = "ls -la"
    result = handle_shell_command(safe_command)

    # 验证结果
    assert result["status"] == "executed"
    mock_execute.assert_called_once_with(safe_command)
    # 不应该提示用户
    mock_prompt.assert_not_called()


@patch("viby.llm.nodes.handlers.shell_handler.is_yolo_mode_enabled")
@patch("viby.llm.nodes.handlers.shell_handler._execute_command")
@patch("viby.llm.nodes.handlers.shell_handler.prompt")
@patch("viby.llm.nodes.handlers.shell_handler.print")
def test_handle_shell_command_yolo_unsafe(
    mock_print, mock_prompt, mock_execute, mock_is_yolo_enabled
):
    """测试yolo模式下处理不安全命令"""
    # 模拟yolo模式开启
    mock_is_yolo_enabled.return_value = True
    mock_prompt.return_value = "r"  # 用户选择运行
    mock_execute.return_value = {"status": "executed", "code": 0}

    # 测试不安全命令不会自动执行
    unsafe_command = "rm -rf /tmp/test"
    result = handle_shell_command(unsafe_command)

    # 验证结果
    assert result["status"] == "executed"
    # 应该要求用户确认
    mock_prompt.assert_called_once()
    # 确认后才执行
    mock_execute.assert_called_once_with(unsafe_command)


@patch("viby.llm.nodes.handlers.shell_handler.is_yolo_mode_enabled")
@patch("viby.llm.nodes.handlers.shell_handler._execute_command")
@patch("viby.llm.nodes.handlers.shell_handler.prompt")
@patch("viby.llm.nodes.handlers.shell_handler.print")
def test_handle_shell_command_no_yolo(
    mock_print, mock_prompt, mock_execute, mock_is_yolo_enabled
):
    """测试非yolo模式下处理命令"""
    # 模拟yolo模式关闭
    mock_is_yolo_enabled.return_value = False
    mock_prompt.return_value = "r"  # 用户选择运行
    mock_execute.return_value = {"status": "executed", "code": 0}

    # 测试任何命令都需要确认
    command = "ls -la"
    result = handle_shell_command(command)

    # 验证结果
    assert result["status"] == "executed"
    # 应该要求用户确认
    mock_prompt.assert_called_once()
    # 确认后才执行
    mock_execute.assert_called_once_with(command)
