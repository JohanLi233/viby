"""
Model management for viby - handles interactions with LLM providers
"""

import openai
from typing import Dict, Any
from viby.config.app_config import Config
from viby.locale import get_text


class ModelManager:
    def __init__(self, config: Config, args=None):
        self.config = config
        # 从命令行参数中获取是否使用 think model 和 fast model
        self.use_think_model = args.think if args and hasattr(args, "think") else False
        self.use_fast_model = args.fast if args and hasattr(args, "fast") else False

    def get_response(self, messages):
        """
        获取模型回复

        Args:
            messages: 消息历史

        Returns:
            生成器，返回 (text_content, None) 的元组
        """
        model_type_to_use = "default"  # Default to "default"

        if self.use_fast_model:
            model_type_to_use = "fast"
        elif self.use_think_model:
            model_type_to_use = "think"

        # model_type_to_use will be "fast", "think", or "default".
        # get_model_config will correctly select the profile or fall back
        # to the default_model if "fast" or "think" are requested but not
        # properly configured (e.g., name is empty in config.yaml).
        model_config = self.config.get_model_config(model_type_to_use)
        return self._call_llm(messages, model_config)

    def _call_llm(self, messages, model_config: Dict[str, Any]):
        """
        调用LLM并返回文本内容

        Args:
            messages: 消息历史
            model_config: 模型配置

        Returns:
            生成器，流式返回 (text_chunks, None)
        """
        model = model_config["model"]
        base_url = model_config["base_url"].rstrip("/")
        api_key = model_config.get("api_key", "")

        try:
            client = openai.OpenAI(
                api_key=api_key or "EMPTY", base_url=f"{base_url}/v1"
            )

            # 准备请求参数
            params = {
                "model": model,
                "messages": messages,
                "temperature": model_config["temperature"],
                "max_tokens": model_config["max_tokens"],
                "stream": True,
            }

            # 创建流式处理
            stream = client.chat.completions.create(**params)
            text_seen = False
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    text_seen = True
                    yield delta.content

            # 如果没有内容，添加提示
            if not text_seen:
                empty = get_text("GENERAL", "llm_empty_response")
                yield empty

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield error_ms
            return
