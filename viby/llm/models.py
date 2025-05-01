"""
Model management for viby - handles interactions with LLM providers
"""

import openai
from typing import Iterator, Dict, Any
from viby.config import Config


class ModelManager:
    
    def __init__(self, config: Config):
        self.config = config
    
    def stream_response(self, prompt: str) -> Iterator[str]:
        """流式获取模型回复"""
        model_config = self.config.get_model_config()
        yield from self._call_llm(prompt, model_config)
    
    def _call_llm(self, prompt: str, model_config: Dict[str, Any]) -> Iterator[str]:
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
                "messages": [{"role": "user", "content": prompt}],
                "temperature": model_config["temperature"],
                "max_tokens": model_config["max_tokens"],
                "stream": True,
            }
            
            stream = client.chat.completions.create(**params)
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except openai.APIError as e:
            raise RuntimeError(f"API 错误: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"API 调用出错: {str(e)}")
