from viby.llm.models import ModelManager
from viby.llm.nodes.prompt_node import PromptNode
from viby.llm.nodes.execute_tool_node import ExecuteToolNode
from viby.llm.nodes.llm_node import LLMNode
from viby.llm.nodes.dummy_node import DummyNode
from pocketflow import Flow


class Vibe:
    """单次提问命令，用于向 AI 发送单个问题并获取回答"""

    def __init__(self, model_manager: ModelManager):
        """初始化单次提问命令流程"""
        self.model_manager = model_manager
        self.llm_node = LLMNode()
        self.prompt_node = PromptNode()
        self.execute_tool_node = ExecuteToolNode()

        self.prompt_node - "call_llm" >> self.llm_node
        self.llm_node - "execute_tool" >> self.execute_tool_node
        self.llm_node - "continue" >> DummyNode()
        self.llm_node - "interrupt" >> DummyNode()
        self.execute_tool_node - "call_llm" >> self.llm_node
        self.execute_tool_node - "completed" >> DummyNode()
        self.flow = Flow(start=self.prompt_node)

    def vibe(self, user_input: str) -> int:
        # 准备共享状态
        shared = {
            "model_manager": self.model_manager,
            "user_input": user_input,
            "messages": [],
        }

        self.flow.run(shared)

        return 0
