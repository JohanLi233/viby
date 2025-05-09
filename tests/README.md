# Viby 测试框架

本文档描述了Viby项目的测试框架结构和使用方法。

## 测试目录结构

```
tests/
├── unit/           - 单元测试
├── integration/    - 集成测试
├── e2e/            - 端到端测试
├── resources/      - 测试资源文件
├── conftest.py     - Pytest共享配置
├── helpers.py      - 测试辅助函数
└── run_tests.py    - 测试运行脚本
```

## 测试类型

1. **单元测试**：测试单个组件的功能，如函数、类或方法。
   - 位置：`tests/unit/`
   - 命名模式：`test_*.py`
   - 运行命令：`python -m pytest tests/unit`

2. **集成测试**：测试多个组件之间的交互，如模块间协作。
   - 位置：`tests/integration/`
   - 命名模式：`test_*.py`
   - 运行命令：`python -m pytest tests/integration`

3. **端到端测试**：模拟用户行为的完整流程测试。
   - 位置：`tests/e2e/`
   - 命名模式：`test_*.py`
   - 运行命令：`python -m pytest tests/e2e`


## 运行测试

可以使用以下方式运行测试：

### 使用测试运行脚本

```bash
# 运行所有单元测试
./tests/run_tests.py --unit

# 运行所有集成测试
./tests/run_tests.py --integration

# 运行端到端测试
./tests/run_tests.py --e2e

# 运行所有测试
./tests/run_tests.py --all

# 运行单元测试和生成覆盖率报告
./tests/run_tests.py --unit --coverage
```

### 直接使用pytest

```bash
# 运行所有测试
python -m pytest

# 运行特定测试模块
python -m pytest tests/unit/test_logging.py

# 运行匹配特定名称的测试
python -m pytest -k "logging"

# 生成覆盖率报告
python -m pytest --cov=viby --cov-report=html
```

## 编写测试

### 单元测试示例

```python
import pytest
from viby.utils import some_module

def test_some_function():
    # 准备测试数据
    input_data = "test input"
    
    # 执行被测函数
    result = some_module.some_function(input_data)
    
    # 验证结果
    assert result == "expected output"
```

### 使用模拟对象

```python
def test_with_mock(mocker):
    # 创建模拟对象
    mock_dependency = mocker.patch("viby.module.dependency")
    mock_dependency.some_method.return_value = "mocked result"
    
    # 执行使用依赖的代码
    result = some_module.function_using_dependency()
    
    # 验证结果和交互
    assert result == "expected with mock"
    mock_dependency.some_method.assert_called_once()
```