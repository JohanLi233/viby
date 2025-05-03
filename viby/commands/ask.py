from viby.llm.models import ModelManager
from viby.llm.nodes.llm_node import LLMNode

class AskCommand:
    """
    单次提问命令，用于向 AI 发送单个问题并获取回答。
    与 Chat 不同，该命令不维护会话状态，每次调用都是独立的交互。
    """
    def __init__(self, model_manager: ModelManager):
        """初始化单次提问命令流程"""
        self.model_manager = model_manager
        self.reply_node = LLMNode()
    
    def execute(self, user_input: str) -> int:
        # 准备共享状态
        shared = {
            "model_manager": self.model_manager,
            "task_type": "chat",  # 指定任务类型为对话
            "messages": [
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        }
        
        self.reply_node.run(shared)
        
        return 0
