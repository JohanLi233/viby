from pocketflow import Node
from viby.utils.formatting import stream_render_response

class ReplyNode(Node):
    """
    处理模型回复的节点
    
    负责：
    1. 调用LLM生成回复并渲染到终端
    2. 将回复添加到消息历史中
    3. 处理错误情况
    """
    def prep(self, shared):
        # 从共享状态获取必要的数据
        return {
            "model_manager": shared.get("model_manager"),
            "messages": shared.get("messages")
        }

    def exec(self, prep_res):
        # 执行计算逻辑，不访问shared
        if not prep_res or not prep_res.get("messages") or not prep_res.get("model_manager"):
            return None
        
        # 调用LLM生成回复
        model_manager = prep_res["model_manager"]
        messages = prep_res["messages"]
        
        # 渲染响应并收集完整回复文本
        full_response = stream_render_response(model_manager, messages)
        
        # 返回生成的完整响应
        return full_response
    
    def post(self, shared, prep_res, exec_res):
        # 将助手消息添加到历史中
        if exec_res:
            # 存储响应方便其他节点使用
            shared["response"] = exec_res
            
            # 如果有消息历史，添加助手回复
            if "messages" in shared and isinstance(shared["messages"], list):
                shared["messages"].append({
                    "role": "assistant",
                    "content": exec_res
                })
        
        # 直接返回继续动作，无需经过ResponseNode
        return "continue"  # 继续对话
    
    def exec_fallback(self, prep_res, exc):
        # 错误处理：提供友好的错误信息
        return f"Error: {str(exc)}"
