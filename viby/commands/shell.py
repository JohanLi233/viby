"""
Shell command execution for viby - 使用 pocketflow 框架的重构版本
"""

from pocketflow import Flow
from viby.llm.models import ModelManager
from viby.llm.nodes.command_node import CommandNode
from viby.llm.nodes.dummy_node import DummyNode
from viby.llm.nodes.execute_shell_command_node import ExecuteShellCommandNode


class ShellCommand:
    """
    处理 shell 命令生成和执行的命令类
    
    使用 pocketflow 框架实现了以下流程：
    用户输入 -> 生成 shell 命令 -> 用户交互(执行/编辑/复制/放弃)
    
    每个节点负责其特定的功能：
    - ShellPromptNode: 生成 shell 命令
    - ExecuteShellCommandNode: 处理用户交互和命令执行
    """
    
    def __init__(self, model_manager: ModelManager):
        """初始化 Shell 命令流程"""
        # 保存模型管理器
        self.model_manager = model_manager
        
        # 创建节点
        shell_prompt_node = CommandNode()
        execute_command_node = ExecuteShellCommandNode()
        
        # 连接节点以创建流程
        shell_prompt_node - "execute" >> execute_command_node
        
        # 添加对话循环：如果用户选择'c'，直接返回到命令节点继续对话
        execute_command_node - "chat" >> shell_prompt_node
        
        # 默认结束映射，避免Flow警告
        execute_command_node >> DummyNode()
        
        # 保存流程实例
        self.flow = Flow(start=shell_prompt_node)
    
    def execute(self, user_prompt: str) -> int:
        """
        执行 shell 命令生成和交互流程
        """
        shared = {
            "model_manager": self.model_manager,
            "user_input": user_prompt,
            "messages": []
        }
        
        # 先添加用户的初始输入到消息历史
        shared["messages"].append({
            "role": "user",
            "content": user_prompt
        })
        
        # 执行流程
        self.flow.run(shared)
        
        if "shell_result" in shared:
            return shared["shell_result"].get("code", 0)
        
        return 0
