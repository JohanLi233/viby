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
    with mock.patch("sys.exit"):
        with mock.patch("sys.argv", ["viby", "-v"]):
            with mock.patch("importlib.metadata.version") as mock_version:
                mock_version.return_value = "0.2.2"

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
                    assert "0.2.2" in stdout_value


@with_stdin_mocked
def test_help_command():
    """测试帮助命令"""
    # 模拟配置不是首次运行，避免触发配置向导
    with mock.patch("viby.config.config.is_first_run", False):
        with mock.patch("sys.exit"):
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
                    assert "usage:" in stdout_value.lower() or "Usage:" in stdout_value
                    assert "--help" in stdout_value


@with_stdin_mocked
def test_invalid_command():
    """测试无效命令"""
    # 模拟配置不是首次运行，避免触发配置向导
    with mock.patch("viby.config.config.is_first_run", False):
        with mock.patch("sys.exit"):
            with mock.patch("sys.argv", ["viby", "invalid_command"]):
                # 捕获标准输出
                with mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                    try:
                        main()
                    except SystemExit:
                        pass
                    except Exception as e:
                        print(f"捕获到异常: {e}")

                    # 检查输出是否包含错误消息
                    stdout_value = mock_stdout.getvalue()
                    assert "No such command" in stdout_value or "Error" in stdout_value


@with_stdin_mocked
@pytest.mark.skipif(os.environ.get("SKIP_API_TESTS"), reason="需要API密钥的测试被跳过")
def test_basic_vibe_command():
    """测试基本的vibe命令"""
    # 模拟配置不是首次运行，避免触发配置向导
    with mock.patch("viby.config.config.is_first_run", False):
        with mock.patch("sys.argv", ["viby", "vibe", "什么是Python?"]):
            # 模拟Vibe.vibe
            with mock.patch("viby.commands.vibe.Vibe.vibe") as mock_run:
                mock_run.return_value = 0

                # 运行
                exit_code = main()

                # 验证结果
                assert exit_code == 0
                assert mock_run.called


def test_full_cli_workflow():
    """
    完整的CLI工作流测试

    注意：此测试默认被跳过，因为它需要实际的环境和API访问
    要运行此测试，请去掉skipif装饰器并确保环境已正确设置
    """
    # 模拟配置不是首次运行，避免触发配置向导
    with mock.patch("viby.config.config.is_first_run", False):
        # 模拟版本命令
        with mock.patch("sys.argv", ["viby", "-v"]):
            with mock.patch("sys.stdin.isatty", return_value=True):
                with mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                    with mock.patch("importlib.metadata.version") as mock_version:
                        mock_version.return_value = "0.2.2"
                        try:
                            main()
                        except SystemExit:
                            pass
                        assert "0.2.2" in mock_stdout.getvalue()

        # 模拟简单查询
        with mock.patch("sys.argv", ["viby", "vibe", "你好，Viby！"]):
            with mock.patch("sys.stdin.isatty", return_value=True):
                with mock.patch("viby.commands.vibe.Vibe.vibe") as mock_run:
                    mock_run.return_value = 0
                    exit_code = main()
                    assert exit_code == 0
                    assert mock_run.called
