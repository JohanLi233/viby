"""
Model management for viby - handles interactions with LLM providers
"""

import openai
import json
from typing import Dict, Any, Iterator
from viby.config.app_config import Config
from viby.locale import get_text


class ModelManager:
    
    def __init__(self, config: Config, args = None):
        self.config = config
        # 从命令行参数中获取是否使用 think model 和 fast model
        self.use_think_model = args.think if args and hasattr(args, 'think') else False
        self.use_fast_model = args.fast if args and hasattr(args, 'fast') else False
        
    def stream_response(self, messages, tools) -> Iterator[str]:
        """
        流式获取模型回复
        """
        model_name = None
        # 优先级：fast > think > 默认模型
        if self.use_fast_model and getattr(self.config, 'fast_model', None):
            model_name = self.config.fast_model
        elif self.use_think_model and getattr(self.config, 'think_model', None):
            model_name = self.config.think_model
        
        model_config = self.config.get_model_config(model_name)
        yield from self._call_llm(messages, model_config, tools)
    
    def _call_llm(self, messages, model_config: Dict[str, Any], tools) -> Iterator[str]:
        
        model = model_config["model"]
        base_url = model_config["base_url"].rstrip("/")
        api_key = model_config.get("api_key", "")
        
        try:
            client = openai.OpenAI(
                api_key=api_key or "EMPTY",
                base_url=f"{base_url}/v1"
            )

            # 准备请求参数
            params = {
                "model": model,
                "messages": messages,
                "temperature": model_config["temperature"],
                "max_tokens": model_config["max_tokens"],
                "stream": True,
                "tools": tools,
                "tool_choice": "auto",
            }
            
            # 创建流式处理
            stream = client.chat.completions.create(**params)

            yielded = False  # 标记是否输出过内容
            tool_calls = {}
            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta

                if delta.content:
                    yielded = True
                    yield delta.content

                if getattr(delta, "tool_calls", None):
                    yielded = True
                    for tc in delta.tool_calls:
                        idx = tc.index or 0
                        call = tool_calls.setdefault(idx, {"name": "", "args": ""})
                        if tc.function:
                            if tc.function.name:
                                call["name"] = tc.function.name
                            if tc.function.arguments:
                                call["args"] += tc.function.arguments
            # 若模型无输出，提示
            if not yielded:
                yield get_text("GENERAL", "llm_empty_response")
            # 输出工具调用 JSON
            for call in tool_calls.values():
                if call["name"]:
                    try:
                        params = json.loads(call["args"]) if call["args"].strip() else {}
                    except Exception:
                        params = {}
                    payload = json.dumps({"tool": call["name"], "parameters": params}, ensure_ascii=False)
                    yield f"```tool\n{payload}\n```"
                
        except Exception as e:
            yield f"Error: {str(e)}"
