"""
MCP命令 - 使用Model Context Protocol工具的命令
"""
import sys

from viby.llm.models import ModelManager
from viby.config import Config
from viby.llm.nodes.mcp_nodes import GetToolsNode, DecideToolNode, ExecuteToolNode
from pocketflow import Flow

class MCPCommand:
    """
    MCP命令类 - 通过Model Context Protocol调用工具
    
    负责：
    1. 解析命令行参数
    2. 初始化模型和共享状态
    3. 执行MCP流程
    """
    def __init__(self, model_manager=None):
        # 与其他命令保持一致的接口
        self.config = Config()
        self.model_manager = model_manager if model_manager else ModelManager(self.config)

    def create_mcp_flow(self):
        """创建MCP工具流程 - 获取工具、决策、执行"""
        get_tools_node = GetToolsNode()
        decide_tool_node = DecideToolNode()
        execute_tool_node = ExecuteToolNode()
        
        # 配置流程转换
        get_tools_node - "decide" >> decide_tool_node
        decide_tool_node - "execute" >> execute_tool_node
        
        # 开始节点为get_tools_node
        return Flow(start=get_tools_node)
    
    def execute(self, prompt=None):
        """执行MCP命令 - 与其他命令保持一致的接口"""
        # 从参数或管道中获取提示内容
        if not prompt:
            if not sys.stdin.isatty():
                prompt = sys.stdin.read().strip()
                if not prompt.strip():
                    print("错误: 没有输入内容")
                    return 1
            else:
                print("错误: 请提供问题内容")
                return 1
        
        # 准备共享状态
        shared = {
            "model_manager": self.model_manager,
            "messages": [{"role": "user", "content": prompt}],
            "user_input": prompt,
            # 不指定具体服务器，使用Config中的默认设置
            "mcp_server": None
        }
        
        # 创建并执行MCP流程
        flow = self.create_mcp_flow()
        flow.run(shared)
        
        return 0
