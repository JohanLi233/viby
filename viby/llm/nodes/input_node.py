from pocketflow import Node

class InputNode(Node):
    """获取用户输入并将其添加到消息历史中"""
    
    def exec(self, prep_res):
        # 获取用户输入
        user_input = input("<|: ")
        return user_input
    
    def post(self, shared, prep_res, exec_res):
        # 添加用户消息到历史
        shared["messages"].append({
            "role": "user",
            "content": exec_res
        })
        
        return "reply"  # 下一步操作