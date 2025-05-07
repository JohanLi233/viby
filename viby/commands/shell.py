"""
Shell command execution for viby - 使用 pocketflow 框架的重构版本
"""

from pocketflow import Flow
from viby.llm.models import ModelManager
from viby.llm.nodes.prompt_node import PromptNode
from viby.llm.nodes.execute_tool_node import ExecuteToolNode
from viby.llm.nodes.llm_node import LLMNode
from viby.llm.nodes.dummy_node import DummyNode
from viby.llm.nodes.execute_shell_command_node import ExecuteShellCommandNode


class ShellCommand:
    """
    处理 shell 命令生成和执行的命令类
    
    使用 pocketflow 框架实现了以下流程：
    用户输入 -> 生成 shell 命令 -> 用户交互(执行/编辑/复制/放弃)
    
    每个节点负责其特定的功能：
    - PromptNode: 处理用户输入和命令调用
    - LLMNode: 处理 LLM 相关逻辑
    - ExecuteToolNode: 处理 MCP 工具调用
    - ExecuteShellCommandNode: 处理用户交互和命令执行
    """
    
    def __init__(self, model_manager: ModelManager):
        """初始化 Shell 命令流程"""
        # 保存模型管理器
        self.model_manager = model_manager
        
        # 创建节点
        self.prompt_node = PromptNode()
        self.llm_node = LLMNode()
        self.execute_command_node = ExecuteShellCommandNode()
        self.execute_tool_node = ExecuteToolNode()

        
        # 启动 LLM 调用
        self.prompt_node - "call_llm" >> self.llm_node

        # 工具调用流程：来自 LLM 的 execute_tool 事件
        self.llm_node - "execute_tool" >> self.execute_tool_node
        self.execute_tool_node - "call_llm" >> self.llm_node

        # Shell 命令执行流程：来自 LLM 的 continue 事件
        self.llm_node - "continue" >> self.execute_command_node
        self.execute_command_node - "call_llm" >> self.llm_node
        self.execute_command_node >> DummyNode()
        
        self.flow = Flow(start=self.prompt_node)
    
    def execute(self, user_prompt: str) -> int:
        """
        执行 shell 命令生成和交互流程
        """
        shared = {
            "model_manager": self.model_manager,
            "user_input": user_prompt,
            "command_type": "shell"
        }
        
        # 执行流程
        self.flow.run(shared)
        
        if "shell_result" in shared:
            return shared["shell_result"].get("code", 0)
        
        return 0
