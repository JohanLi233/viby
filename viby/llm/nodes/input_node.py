from pocketflow import Node
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from viby.locale import get_text

class InputNode(Node):
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
        shared["messages"].append({
            "role": "user",
            "content": exec_res
        })
        
        return "call_llm"  # 下一步操作