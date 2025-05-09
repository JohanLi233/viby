"""
Pytest 配置文件，提供通用的测试夹具和配置
"""

import os
import sys
import pytest
from pathlib import Path

# 确保能够导入viby模块
sys.path.insert(0, str(Path(__file__).parent.parent))


# 测试环境配置
@pytest.fixture(scope="session")
def test_config():
    """提供测试配置"""
    return {
        "test_temp_dir": Path(__file__).parent / "temp",
        "test_resources_dir": Path(__file__).parent / "resources",
    }


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(test_config):
    """设置测试环境"""
    # 创建测试所需的临时目录
    test_config["test_temp_dir"].mkdir(exist_ok=True)
    test_config["test_resources_dir"].mkdir(exist_ok=True)

    # 设置测试环境变量
    os.environ["VIBY_TEST_MODE"] = "1"

    yield

    # 清理测试环境
    os.environ.pop("VIBY_TEST_MODE", None)


@pytest.fixture
def mock_logger(mocker):
    """模拟日志记录器"""
    return mocker.patch("viby.utils.logging.get_logger")


@pytest.fixture
def isolated_filesystem(tmp_path):
    """提供隔离的文件系统"""
    original_dir = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(original_dir)
