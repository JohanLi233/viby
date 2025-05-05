from pocketflow import Flow
from viby.llm.nodes.chat_input_node import ChatInputNode
from viby.llm.nodes.prompt_node import PromptNode
from viby.llm.nodes.execute_tool_node import ExecuteToolNode
from viby.llm.nodes.llm_node import LLMNode
from viby.llm.nodes.dummy_node import DummyNode
from viby.llm.models import ModelManager

class ChatCommand:
    """
    多轮对话命令，使用 pocketflow 实现的一个完整对话流程。
    流程：用户输入 -> 模型响应 -> 继续对话
    每个节点负责各自的功能，遵循关注点分离原则。
    """
    def __init__(self, model_manager: ModelManager):
        """初始化并创建对话流程"""
        # 保存模型管理器
        self.model_manager = model_manager

        # 创建节点
        self.input_node = ChatInputNode()
        self.prompt_node = PromptNode()
        self.llm_node = LLMNode()
        self.execute_tool_node = ExecuteToolNode()
        
        # 根据配置决定是否启用MCP工具
        # 初始化流程从输入节点开始
        self.flow = Flow(start=self.input_node)
        
        # 先获取输入再初始化工具
        self.input_node - "first_input" >> self.prompt_node
        self.prompt_node - "call_llm" >> self.llm_node
        self.input_node - "call_llm" >> self.llm_node
        self.llm_node - "execute_tool" >> self.execute_tool_node
        self.llm_node - "continue" >> self.input_node
        self.execute_tool_node - "call_llm" >> self.llm_node
        self.input_node - "exit" >> DummyNode()
    
    def execute(self):
        # 准备共享状态
        shared = {
            "model_manager": self.model_manager,
        }
        
        # 执行流程
        self.flow.run(shared)
        
        return 0