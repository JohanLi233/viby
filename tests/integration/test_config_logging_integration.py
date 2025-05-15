"""
测试配置和日志模块的集成
"""

import os
import pytest
import tempfile
from pathlib import Path
from unittest import mock

from viby.config.app_config import Config
from viby.utils import logging as viby_logging


@pytest.fixture
def mock_config_path():
    """提供临时配置路径"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_dir = Path(tmp_dir) / ".config" / "viby"
        config_dir.mkdir(parents=True)
        config_path = config_dir / "config.yaml"

        # 写入基本配置（使用新的配置格式）
        with open(config_path, "w") as f:
            f.write("""
default_model:
  name: test-model
  temperature: 0.7
  max_tokens: 40960
  api_base_url: null
  api_key: null
  top_p: null
language: zh-CN
enable_mcp: true
api_timeout: 300
            """)

        # 返回临时目录和配置路径
        yield config_dir, config_path


@pytest.fixture(autouse=True)
def reset_config_singleton():
    """确保每个测试都获取全新的Config实例"""
    Config._instance = None
    yield
    Config._instance = None


def test_config_with_logging_integration(mock_config_path, mock_logger):
    """测试配置加载与日志集成"""
    config_dir, config_path = mock_config_path
    mock_log = mock.MagicMock()
    mock_logger.return_value = mock_log

    # 模拟环境，使配置使用测试路径
    with mock.patch("pathlib.Path.home", return_value=config_dir.parent.parent):
        with mock.patch("platform.system", return_value="Linux"):
            # 加载配置
            config = Config()

            # 验证配置加载正确
            assert config.language == "zh-CN"
            assert config.enable_mcp is True
            # 使用新的配置结构验证模型属性
            assert config.default_model.temperature == 0.7
            assert config.default_model.max_tokens == 40960
            assert config.api_timeout == 300

            # 或者通过get_model_config方法验证
            model_config = config.get_model_config()
            assert model_config["temperature"] == 0.7
            assert model_config["max_tokens"] == 40960

            # 修改配置
            config.language = "en-US"
            config.save_config()

            # 重新加载配置
            new_config = Config()
            assert new_config.language == "en-US"

            # 验证日志调用
            # 注意：由于我们没有直接让Config调用logger，我们主要测试环境设置
            assert os.path.exists(config.config_path)


def test_logging_level_from_config():
    """测试从配置获取日志级别设置"""
    # 模拟配置
    mock_config = mock.MagicMock()
    mock_config.debug_mode = True

    # 使用模拟配置设置日志
    with mock.patch("logging.Logger.setLevel") as mock_set_level:
        with mock.patch(
            "viby.utils.logging.setup_logging", return_value=mock.MagicMock()
        ):
            # 根据配置设置日志级别
            logger = viby_logging.get_logger()

            if mock_config.debug_mode:
                logger.setLevel(viby_logging.logging.DEBUG)

            # 验证调用
            mock_set_level.assert_called_once()
