"""
CLI命令的端到端测试
"""

import os
import io
import pytest
from unittest import mock

# 导入CLI入口点
from viby.cli.main import main


# 公共修饰器，用于所有测试中的stdin模拟
def with_stdin_mocked(func):
    def wrapper(*args, **kwargs):
        with mock.patch("sys.stdin.isatty", return_value=True):
            return func(*args, **kwargs)

    return wrapper


@with_stdin_mocked
def test_version_command():
    """测试版本命令"""
    with mock.patch("sys.exit") as mock_exit:
        with mock.patch("sys.argv", ["viby", "-v"]):
            with mock.patch("importlib.metadata.version") as mock_version:
                mock_version.return_value = "0.1.3"

                # 捕获标准输出
                with mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                    try:
                        main()
                    except SystemExit:
                        pass
                    except Exception as e:
                        print(f"捕获到异常: {e}")

                    # 检查是否打印了版本号
                    stdout_value = mock_stdout.getvalue()
                    assert "0.1.3" in stdout_value


@with_stdin_mocked
def test_help_command():
    """测试帮助命令"""
    with mock.patch("sys.exit") as mock_exit:
        with mock.patch("sys.argv", ["viby", "-h"]):
            # 捕获标准输出
            with mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                try:
                    main()
                except SystemExit:
                    pass
                except Exception as e:
                    print(f"捕获到异常: {e}")

                # 验证结果
                stdout_value = mock_stdout.getvalue()
                assert "usage:" in stdout_value.lower()
                assert "--help" in stdout_value


@with_stdin_mocked
def test_invalid_command():
    """测试无效命令"""
    with mock.patch("sys.exit") as mock_exit:
        with mock.patch("sys.argv", ["viby", "invalid_command"]):
            # 直接模拟ArgumentParser的parse_args返回值
            with mock.patch("viby.cli.arguments.parse_arguments") as mock_parse_args:
                args_mock = mock.MagicMock()
                args_mock.version = False
                args_mock.shell = False
                args_mock.chat = False
                args_mock.config = False
                args_mock.prompt = "invalid_command"
                args_mock.think = False
                args_mock.fast = False
                args_mock.language = None
                mock_parse_args.return_value = args_mock

                # 模拟process_input结果
                with mock.patch("viby.cli.arguments.process_input") as mock_process:
                    mock_process.return_value = ("invalid_command", True)

                    # 模拟AskCommand.execute以避免实际执行引起线程问题
                    with mock.patch(
                        "viby.commands.ask.AskCommand.execute"
                    ) as mock_ask_execute:
                        mock_ask_execute.return_value = 0

                        # 运行main函数
                        exit_code = main()

                        # 验证AskCommand.execute被调用，不验证输出内容
                        assert mock_ask_execute.called


@with_stdin_mocked
@pytest.mark.skipif(os.environ.get("SKIP_API_TESTS"), reason="需要API密钥的测试被跳过")
def test_basic_ask_command():
    """测试基本的ask命令"""
    with mock.patch("sys.argv", ["viby", "什么是Python?"]):
        # 模拟AskCommand.execute
        with mock.patch("viby.commands.ask.AskCommand.execute") as mock_execute:
            mock_execute.return_value = 0

            # 运行
            exit_code = main()

            # 验证结果
            assert exit_code == 0
            assert mock_execute.called


def test_full_cli_workflow():
    """
    完整的CLI工作流测试

    注意：此测试默认被跳过，因为它需要实际的环境和API访问
    要运行此测试，请去掉skipif装饰器并确保环境已正确设置
    """
    # 模拟版本命令
    with mock.patch("sys.argv", ["viby", "-v"]):
        with mock.patch("sys.stdin.isatty", return_value=True):
            with mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with mock.patch("importlib.metadata.version") as mock_version:
                    mock_version.return_value = "0.1.0-test"
                    try:
                        main()
                    except SystemExit:
                        pass
                    assert "0.1.0-test" in mock_stdout.getvalue()

    # 模拟简单查询
    with mock.patch("sys.argv", ["viby", "你好，Viby！"]):
        with mock.patch("sys.stdin.isatty", return_value=True):
            with mock.patch("viby.commands.ask.AskCommand.execute") as mock_execute:
                mock_execute.return_value = 0
                exit_code = main()
                assert exit_code == 0
                assert mock_execute.called
