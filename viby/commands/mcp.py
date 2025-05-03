"""
MCP命令 - 使用Model Context Protocol工具的命令
"""
import sys
from typing import Optional

from viby.llm.models import ModelManager
from viby.config.app_config import Config
from viby.llm.nodes.mcp_nodes import GetToolsNode, ExecuteToolNode
from viby.llm.nodes.llm_node import LLMNode
from pocketflow import Flow

class MCPCommand:
    """
    MCP命令类 - 通过Model Context Protocol调用工具
    
    负责：
    1. 解析命令行参数
    2. 初始化模型和共享状态
    3. 执行MCP流程
    """
    def __init__(self, model_manager):
        """初始化MCP命令流程，构建完整的MCP流程"""
        self.config = Config()
        self.model_manager: ModelManager = model_manager
        
        # 构建完整的MCP流程：获取工具 -> 决策 -> 执行
        get_tools_node = GetToolsNode()
        decide_node = LLMNode()
        execute_node = ExecuteToolNode()
        
        # 配置流程转换
        get_tools_node - "decide" >> decide_node
        decide_node - "execute_tool" >> execute_node
        
        # 保存流程实例
        self.flow = Flow(start=get_tools_node)
    
    def execute(self, prompt: Optional[str] = None) -> int:
        """执行MCP命令 - 与其他命令保持一致的接口"""
        # 从参数或管道中获取提示内容
        if not prompt:
            if not sys.stdin.isatty():
                prompt = sys.stdin.read().strip()
                if not prompt.strip():
                    return 1
            else:
                return 1
        
        # 准备共享状态
        shared = {
            "model_manager": self.model_manager,
            "user_input": prompt,
            "task_type": "mcp_decide",
            "mcp_server": None
        }
        
        self.flow.run(shared)
        
        return 0
