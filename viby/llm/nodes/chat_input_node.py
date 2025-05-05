from pocketflow import Node
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from viby.locale import get_text

class ChatInputNode(Node):
    """获取用户输入并将其添加到消息历史中"""
    
    def exec(self, prep_res):
        # 获取用户输入
        input_prompt = HTML(f'<ansigreen>{get_text("CHAT", "input_prompt")}</ansigreen>')
        user_input = prompt(input_prompt)
        
        # 检查是否是退出命令
        if user_input.lower() == "exit":
            return 'exit'
            
        return user_input
    
    def post(self, shared, prep_res, exec_res):
        # 检查是否退出
        if exec_res == 'exit':
            return 'exit'
            
        # 添加用户消息到历史
        # 如果还没有消息历史，初始化它
        if "messages" not in shared:
            shared["messages"] = []
            
        # 将用户输入存到 shared 中，便于 PromptNode 使用
        shared["user_input"] = exec_res
            
        # 添加用户消息到历史
        shared["messages"].append({
            "role": "user",
            "content": exec_res
        })
        
        # 如果消息历史只有一条（当前消息），说明是第一次输入
        if len(shared["messages"]) == 1:
            return "first_input"  # 路由到 PromptNode 获取工具
        else:
            return "call_llm"  # 直接到 LLM 节点