from pocketflow import Flow
from viby.llm.nodes.input_node import InputNode
from viby.llm.nodes.reply_node import ReplyNode
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
        input_node = InputNode()
        reply_node = ReplyNode()
        
        # 连接节点以创建流程
        input_node - "reply" >> reply_node
        reply_node - "continue" >> input_node  # ReplyNode 现在直接循环到输入节点
        input_node >> DummyNode()
        
        # 保存流程实例
        self.flow = Flow(start=input_node)
    
    def execute(self):
        # 准备共享状态
        shared = {
            "model_manager": self.model_manager,
        }
        
        # 执行流程
        self.flow.run(shared)
        
        return 0