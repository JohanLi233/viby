"""
测试shell命令处理器的yolo模式功能
"""

from unittest.mock import patch

from viby.tools.shell_tool import (
    set_yolo_mode,
    is_yolo_mode_enabled,
    _is_unsafe_command,
    handle_shell_command,
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
    assert _is_unsafe_command("cat file.txt") is False
    assert _is_unsafe_command("mkdir test_dir") is False
    assert _is_unsafe_command("echo rm -f") is False  # echo命令是安全的
    assert _is_unsafe_command("echo 'rm -rf /'") is False  # echo命令内容不会被检测

    # 测试不安全的主命令
    assert _is_unsafe_command("rm -f test.txt") is True  # rm命令带-f参数
    assert _is_unsafe_command("rm -rf /tmp/folder") is True  # rm命令带-rf参数
    assert _is_unsafe_command("rm -r folder") is True  # rm命令带-r参数
    assert _is_unsafe_command("sudo apt update") is True  # sudo命令
    assert _is_unsafe_command("chown user:group file") is True  # chown命令
    assert _is_unsafe_command("mkfs.ext4 /dev/sda1") is True  # mkfs命令

    # 测试复杂的rm命令
    assert _is_unsafe_command("rm -rfv /tmp/test") is True  # 带v选项的rm命令
    assert _is_unsafe_command("rm -v -f test.txt") is True  # 多个选项的rm命令

    # 测试命令选项模式
    assert _is_unsafe_command("rm --force file.txt") is True  # --force选项
    assert _is_unsafe_command("rm --recursive directory") is True  # --recursive选项

    # 测试普通rm命令 - 所有rm命令都是不安全的
    assert _is_unsafe_command("rm test.txt") is True  # 普通的rm命令，无选项
    assert _is_unsafe_command("rm test_rm-f") is True  # 文件名包含rm-f


@patch("viby.locale.text_manager")
@patch("viby.utils.history.logger")
@patch("viby.tools.shell_tool.is_yolo_mode_enabled")
@patch("viby.tools.shell_tool._execute_command")
@patch("viby.tools.shell_tool.prompt")
@patch("viby.tools.shell_tool.print")
def test_handle_shell_command_yolo_safe(
    mock_print,
    mock_prompt,
    mock_execute,
    mock_is_yolo_enabled,
    mock_logger,
    mock_text_manager,
):
    """测试yolo模式下处理安全命令"""
    # 模拟yolo模式开启
    mock_is_yolo_enabled.return_value = True
    mock_execute.return_value = {"status": "executed", "code": 0}

    # 设置日志模拟对象属性，避免类型错误
    mock_logger.debug.return_value = None

    # 配置文本管理器模拟
    mock_text_manager.get.return_value = "执行命令: {0}"

    # 测试安全命令自动执行
    safe_command = "ls -la"
    result = handle_shell_command(safe_command)

    # 验证结果
    assert result["status"] == "executed"
    mock_execute.assert_called_once_with(safe_command)
    # 不应该提示用户
    mock_prompt.assert_not_called()


@patch("viby.locale.text_manager")
@patch("viby.utils.history.logger")
@patch("viby.tools.shell_tool.is_yolo_mode_enabled")
@patch("viby.tools.shell_tool._execute_command")
@patch("viby.tools.shell_tool.prompt")
@patch("viby.tools.shell_tool.print")
def test_handle_shell_command_yolo_unsafe(
    mock_print,
    mock_prompt,
    mock_execute,
    mock_is_yolo_enabled,
    mock_logger,
    mock_text_manager,
):
    """测试yolo模式下处理不安全命令"""
    # 模拟yolo模式开启
    mock_is_yolo_enabled.return_value = True
    mock_prompt.return_value = "r"  # 用户选择运行
    mock_execute.return_value = {"status": "executed", "code": 0}

    # 设置日志模拟对象属性，避免类型错误
    mock_logger.debug.return_value = None

    # 配置文本管理器模拟
    mock_text_manager.get.return_value = "是否执行: {0}"

    # 测试不安全命令不会自动执行
    unsafe_command = "rm -rf /tmp/test"
    result = handle_shell_command(unsafe_command)

    # 验证结果
    assert result["status"] == "executed"
    # 应该要求用户确认
    mock_prompt.assert_called_once()
    # 确认后才执行
    mock_execute.assert_called_once_with(unsafe_command)


@patch("viby.locale.text_manager")
@patch("viby.utils.history.logger")
@patch("viby.tools.shell_tool.is_yolo_mode_enabled")
@patch("viby.tools.shell_tool._execute_command")
@patch("viby.tools.shell_tool.prompt")
@patch("viby.tools.shell_tool.print")
def test_handle_shell_command_yolo_rm_f(
    mock_print,
    mock_prompt,
    mock_execute,
    mock_is_yolo_enabled,
    mock_logger,
    mock_text_manager,
):
    """测试yolo模式下处理rm -f命令"""
    # 模拟yolo模式开启
    mock_is_yolo_enabled.return_value = True
    mock_prompt.return_value = "r"  # 用户选择运行
    mock_execute.return_value = {"status": "executed", "code": 0}

    # 设置日志模拟对象属性，避免类型错误
    mock_logger.debug.return_value = None

    # 配置文本管理器模拟
    mock_text_manager.get.return_value = "是否执行: {0}"

    # 测试rm -f命令不会自动执行
    unsafe_command = "rm -f test.txt"
    result = handle_shell_command(unsafe_command)

    # 验证结果
    assert result["status"] == "executed"
    # 应该要求用户确认
    mock_prompt.assert_called_once()
    # 确认后才执行
    mock_execute.assert_called_once_with(unsafe_command)


@patch("viby.locale.text_manager")
@patch("viby.utils.history.logger")
@patch("viby.tools.shell_tool.is_yolo_mode_enabled")
@patch("viby.tools.shell_tool._execute_command")
@patch("viby.tools.shell_tool.prompt")
@patch("viby.tools.shell_tool.print")
def test_handle_shell_command_no_yolo(
    mock_print,
    mock_prompt,
    mock_execute,
    mock_is_yolo_enabled,
    mock_logger,
    mock_text_manager,
):
    """测试非yolo模式下处理命令"""
    # 模拟yolo模式关闭
    mock_is_yolo_enabled.return_value = False
    mock_prompt.return_value = "r"  # 用户选择运行
    mock_execute.return_value = {"status": "executed", "code": 0}

    # 设置日志模拟对象属性，避免类型错误
    mock_logger.debug.return_value = None

    # 配置文本管理器模拟
    mock_text_manager.get.return_value = "是否执行: {0}"

    # 测试任何命令都需要确认
    command = "ls -la"
    result = handle_shell_command(command)

    # 验证结果
    assert result["status"] == "executed"
    # 应该要求用户确认
    mock_prompt.assert_called_once()
    # 确认后才执行
    mock_execute.assert_called_once_with(command)
