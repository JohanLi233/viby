from pocketflow import Node
from viby.locale import get_text
from viby.mcp import list_tools  # 仅使用 list_tools
from viby.config import Config
import os
import platform

class PromptNode(Node):
    def prep(self, shared):
        self.config = Config()

    def exec(self, server_name):
        """Retrieve tools from the MCP server"""
        result = {
            "tools": []
        }
        
        if not self.config.enable_mcp:
            return result
            
        try:
            # 使用同步接口获取工具列表，结果为 {server_name: [tool1, tool2, ...], ...}
            tools_dict = list_tools(server_name)
            
            # 展平所有工具列表并直接在每个工具中添加服务器信息
            result["tools"] = [
                {**tool, "server_name": srv_name}
                for srv_name, tools in tools_dict.items()
                for tool in tools
            ]
            
            return result
        except Exception as e:
            print(get_text("MCP", "tools_error", e))
            return result

    def post(self, shared, prep_res, exec_res):
        """Store tools and process to decision node"""
        shared["tools"] = exec_res["tools"]
        user_input = shared.get("user_input", "")
        
        # 检查是否是 shell 命令模式
        if shared.get("command_type") == "shell":
            # 为 shell 命令构建特殊提示
            shell = os.environ.get("SHELL") or os.environ.get("COMSPEC") or "unknown"
            shell_name = os.path.basename(shell) if shell else "unknown"
            os_name = platform.system()
            shell_prompt = get_text("SHELL", "command_prompt", user_input, shell_name, os_name)
            
            # 构建 shell 命令的消息
            shared["messages"] = [
                {"role": "system", "content": get_text("AGENT", "prompt")},
                {"role": "user", "content": shell_prompt},
            ]
        else:
            # 常规命令的消息构建
            shared["messages"] = [
                {"role": "system", "content": get_text("AGENT", "prompt")},
                {"role": "user", "content": user_input},
            ]
        
        return "call_llm"