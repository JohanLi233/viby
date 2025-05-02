from pocketflow import Node
from viby.utils.formatting import Colors, extract_answer, stream_render_response
from viby.locale import get_text

class CommandNode(Node):
    """
    处理 shell 命令生成的节点
    
    负责：
    1. 构建 shell 命令生成prompt
    2. 调用 LLM 生成命令
    3. 提取命令内容
    """
    def prep(self, shared):
        return {
            "model_manager": shared.get("model_manager"),
            "user_input": shared.get("user_input")
        }
    
    def exec(self, prep_res):
        if not prep_res or not prep_res.get("user_input") or not prep_res.get("model_manager"):
            return None
            
        user_input = prep_res["user_input"]
        model_manager = prep_res["model_manager"]
        
        shell_prompt = [
            {
                "role": "user", 
                "content": get_text("SHELL", "command_prompt", user_input)
            }
        ]
        
        # 流式获取命令内容
        print(f"{Colors.BLUE}{get_text('SHELL', 'generating_command')}{Colors.END}")
        raw_response = stream_render_response(model_manager, shell_prompt)
        
        # 提取纯命令文本
        command = extract_answer(raw_response)
        
        return command
    
    def post(self, shared, prep_res, exec_res):
        # 保存生成的命令到共享状态
        if exec_res:
            shared["command"] = exec_res
            
        # 进入执行环节
        return "execute"
