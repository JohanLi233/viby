"""
viby.utils.logging 模块的单元测试
"""

import logging
from pathlib import Path
from unittest import mock

from viby.utils import logging as viby_logging


def test_get_logs_path():
    """测试日志路径获取函数"""
    log_path = viby_logging.get_logs_path()
    assert isinstance(log_path, Path)
    assert log_path.name == "viby.log"
    assert "viby" in str(log_path)


def test_setup_logging_default():
    """测试默认日志设置"""
    with mock.patch("logging.StreamHandler") as mock_handler:
        mock_handler.return_value = mock.MagicMock()
        logger = viby_logging.setup_logging()

        assert logger.level == logging.INFO
        mock_handler.assert_called_once()
        assert len(logger.handlers) == 1


def test_setup_logging_with_level():
    """测试自定义日志级别"""
    with mock.patch("logging.StreamHandler") as mock_handler:
        mock_handler.return_value = mock.MagicMock()
        logger = viby_logging.setup_logging(level=logging.DEBUG)

        assert logger.level == logging.DEBUG


def test_get_logger():
    """测试获取日志器函数"""
    # 先清除现有日志器
    with mock.patch("logging.getLogger") as mock_get_logger:
        mock_logger = mock.MagicMock()
        mock_logger.handlers = []  # 模拟没有处理器的日志器
        mock_get_logger.return_value = mock_logger

        # 第一次调用应该创建新的日志器
        with mock.patch("viby.utils.logging.setup_logging") as mock_setup:
            mock_setup_logger = mock.MagicMock()
            mock_setup.return_value = mock_setup_logger
            logger1 = viby_logging.get_logger()

            mock_setup.assert_called_once()
            assert logger1 == mock_setup_logger

    # 第二次调用应该使用已存在的日志器
    with mock.patch("logging.getLogger") as mock_get_logger:
        mock_logger = mock.MagicMock()
        mock_logger.handlers = [mock.MagicMock()]  # 模拟已存在的处理器
        mock_get_logger.return_value = mock_logger

        with mock.patch("viby.utils.logging.setup_logging") as mock_setup:
            logger2 = viby_logging.get_logger()

            mock_get_logger.assert_called_once_with("viby")
            mock_setup.assert_not_called()
            assert logger2 == mock_logger
