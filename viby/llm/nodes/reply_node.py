from pocketflow import Node
from viby.utils.formatting import stream_render_response, extract_answer

class ReplyNode(Node):
    """
    通用的模型回复节点 - 支持多种任务类型
    
    负责：
    1. 根据任务类型决定提示内容
    2. 调用LLM生成回复并渲染到终端
    3. 将回复添加到消息历史中
    4. 根据任务类型决定后续行为
    """
    def prep(self, shared):
        # 从共享状态获取必要的数据
        return {
            "model_manager": shared.get("model_manager"),
            "messages": shared.get("messages"),
            "user_input": shared.get("user_input"),
            "task_type": shared.get("task_type", "chat")  # 默认为聊天模式
        }

    def exec(self, prep_res):
        """
        使用 LLM 流式渲染执行，直接使用已构建好的 messages
        """
        manager = prep_res.get("model_manager")
        messages = prep_res.get("messages")
        if not manager or not messages:
            return None
        t = prep_res.get("task_type", "chat")
        
        # 直接使用构建好的消息历史调用模型
        full = stream_render_response(manager, messages)
        
        # Shell 模式需要提取命令文本
        return extract_answer(full) if t == "shell" else full
    
    def post(self, shared, prep_res, exec_res):
        """
        存储结果并确定下一步动作
        """
        # 所有回复都存储到 response 中
        shared["response"] = exec_res
        shared["messages"].append({"role":"assistant","content":exec_res})
        
        # Shell 任务存储命令并执行，其他任务继续对话
        if prep_res.get("task_type","chat") == "shell":
            shared["command"] = exec_res
            return "execute"
        return "continue"
    
    def exec_fallback(self, prep_res, exc):
        # 错误处理：提供友好的错误信息
        return f"Error: {str(exc)}"
