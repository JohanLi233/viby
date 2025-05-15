#!/usr/bin/env python3
"""
测试viby/commands/chat.py模块中的ChatCommand类
"""

import pytest
from unittest.mock import patch, MagicMock
from pocketflow import Flow

# 模拟文本管理器初始化
with patch("viby.locale.text_manager", MagicMock()):
    with patch("viby.locale.get_text", return_value="测试文本"):
        from viby.commands.chat import ChatCommand, cli_chat


@pytest.fixture
def mock_model_manager():
    """创建一个模拟的ModelManager实例"""
    return MagicMock()


@pytest.fixture
def mock_flow():
    """创建一个模拟的Flow实例"""
    return MagicMock(spec=Flow)


class TestChatCommand:
    """测试ChatCommand类"""

    @patch("viby.commands.chat.Flow")
    @patch("viby.commands.chat.ChatInputNode")
    @patch("viby.commands.chat.PromptNode")
    @patch("viby.commands.chat.LLMNode")
    @patch("viby.commands.chat.ExecuteToolNode")
    @patch("viby.commands.chat.DummyNode")
    def test_init(
        self,
        mock_dummy_node,
        mock_execute_tool,
        mock_llm_node,
        mock_prompt_node,
        mock_input_node,
        mock_flow,
        mock_model_manager,
    ):
        """测试ChatCommand的初始化"""
        # 创建节点的模拟实例
        mock_input_instance = MagicMock()
        mock_prompt_instance = MagicMock()
        mock_llm_instance = MagicMock()
        mock_execute_tool_instance = MagicMock()
        mock_dummy_instance = MagicMock()

        # 设置mock的返回值
        mock_input_node.return_value = mock_input_instance
        mock_prompt_node.return_value = mock_prompt_instance
        mock_llm_node.return_value = mock_llm_instance
        mock_execute_tool.return_value = mock_execute_tool_instance
        mock_dummy_node.return_value = mock_dummy_instance

        # 模拟Flow类
        mock_flow_instance = MagicMock()
        mock_flow.return_value = mock_flow_instance

        # 创建ChatCommand实例
        chat_command = ChatCommand(mock_model_manager)

        # 验证节点创建
        mock_input_node.assert_called_once()
        mock_prompt_node.assert_called_once()
        mock_llm_node.assert_called_once()
        mock_execute_tool.assert_called_once()

        # 验证流程创建
        mock_flow.assert_called_once_with(start=mock_input_instance)

        # 验证属性赋值
        assert chat_command.model_manager == mock_model_manager
        assert chat_command.input_node == mock_input_instance
        assert chat_command.prompt_node == mock_prompt_instance
        assert chat_command.llm_node == mock_llm_instance
        assert chat_command.execute_tool_node == mock_execute_tool_instance
        assert chat_command.flow == mock_flow_instance

        # 验证节点连接
        # 在实际代码中，我们会有类似 node1 - "event" >> node2 的连接
        # 这里的连接是通过运算符重载实现的，在测试中可能无法直接验证
        # 但我们可以检查Flow实例是否被正确创建和保存

    def test_run(self, mock_model_manager):
        """测试ChatCommand的run方法"""
        # 创建一个带有模拟flow的ChatCommand实例
        chat_command = MagicMock(spec=ChatCommand)
        chat_command.model_manager = mock_model_manager
        chat_command.flow = MagicMock()
        # 恢复原始run方法
        chat_command.run = ChatCommand.run.__get__(chat_command)

        # 执行run方法
        result = chat_command.run()

        # 验证流程运行
        chat_command.flow.run.assert_called_once()
        # 检查传递给flow.run的字典是否包含model_manager
        args, kwargs = chat_command.flow.run.call_args
        assert "model_manager" in args[0]
        assert args[0]["model_manager"] == mock_model_manager

        # 验证返回值
        assert result == 0


@patch("viby.commands.chat.ChatCommand")
@patch("viby.commands.chat.ModelManager")
@patch("viby.commands.chat.typer")
def test_cli_chat(mock_typer, mock_model_manager, mock_chat_command):
    """测试cli_chat函数"""
    # 设置模拟对象
    mock_model_manager_instance = MagicMock()
    mock_model_manager.return_value = mock_model_manager_instance

    mock_command_instance = MagicMock()
    mock_chat_command.return_value = mock_command_instance
    mock_command_instance.run.return_value = 0

    # 创建一个MagicMock作为typer.Exit异常
    mock_exit = MagicMock()
    mock_typer.Exit = mock_exit

    # 设置typer.Exit被调用时抛出异常，这样我们可以在with pytest.raises中捕获它
    mock_exit.side_effect = Exception("Mocked typer.Exit")

    # 调用cli_chat函数
    with pytest.raises(Exception):
        cli_chat()

    # 验证函数调用
    mock_model_manager.assert_called_once()
    mock_chat_command.assert_called_once_with(mock_model_manager_instance)
    mock_command_instance.run.assert_called_once()
    mock_exit.assert_called_once_with(code=0)
