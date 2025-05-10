"""
Model management for viby - handles interactions with LLM providers
"""

from typing import Dict, Any, List
from viby.config.app_config import Config
from viby.locale import get_text
from viby.utils.lazy_import import lazy_import
from viby.utils.history import HistoryManager
import time

# 懒加载openai库，只有在实际使用时才会导入
openai = lazy_import("openai")


class TokenTracker:
    """记录和跟踪LLM API调用的token使用情况"""

    def __init__(self):
        self.reset()

    def reset(self):
        """重置所有计数器"""
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.model_name = ""
        self.start_time = time.time()
        self.end_time = None

    def update_from_response(self, response):
        """从OpenAI响应中更新token计数"""
        try:
            # 尝试从完成对象的usage字段中获取token计数
            usage = getattr(response, "usage", None)
            if usage:
                self.prompt_tokens += getattr(usage, "prompt_tokens", 0)
                self.completion_tokens += getattr(usage, "completion_tokens", 0)
                self.total_tokens = self.prompt_tokens + self.completion_tokens
                self.model_name = getattr(response, "model", self.model_name)
                return True
            return False
        except (AttributeError, TypeError):
            return False

    def update_from_chunk(self, chunk):
        """从流式返回的块中更新token计数"""
        try:
            # 有些API在流式块中也会提供token信息
            usage = getattr(chunk, "usage", None)
            if usage and hasattr(usage, "completion_tokens"):
                self.completion_tokens = usage.completion_tokens
                self.total_tokens = self.prompt_tokens + self.completion_tokens
                return True

            # 如果没有直接提供token信息，增加一个估算
            # 假设每个包含内容的块大约是1个token（非常粗略的估计）
            delta = getattr(chunk, "choices", [{}])[0].get("delta", {})
            content = delta.get("content", "")
            if content:
                self.completion_tokens += max(
                    1, len(content) // 4
                )  # 粗略估计4个字符约为1个token
                self.total_tokens = self.prompt_tokens + self.completion_tokens
                return True

            return False
        except (AttributeError, TypeError):
            return False

    def get_formatted_stats(self) -> List[str]:
        """获取格式化的统计信息行"""
        self.end_time = time.time()
        duration = self.end_time - self.start_time

        stats = []
        stats.append(get_text("GENERAL", "token_usage_title"))
        stats.append(
            get_text("GENERAL", "token_usage_prompt").format(self.prompt_tokens)
        )
        stats.append(
            get_text("GENERAL", "token_usage_completion").format(self.completion_tokens)
        )
        stats.append(get_text("GENERAL", "token_usage_total").format(self.total_tokens))

        # 添加通话时长
        stats.append(
            get_text("GENERAL", "token_usage_duration").format(f"{duration:.2f}s")
        )

        return stats


class ModelManager:
    def __init__(self, config: Config, args=None):
        self.config = config
        # 从命令行参数中获取是否使用 think model 和 fast model
        self.use_think_model = args.think if args and hasattr(args, "think") else False
        self.use_fast_model = args.fast if args and hasattr(args, "fast") else False
        # 新增：跟踪token使用情况
        self.track_tokens = args.tokens if args and hasattr(args, "tokens") else False
        self.token_tracker = TokenTracker() if self.track_tokens else None
        # 历史管理器
        self.history_manager = HistoryManager()
        # 当前用户输入（用于历史记录）
        self.current_user_input = None

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

        # 重置token跟踪器
        if self.track_tokens:
            self.token_tracker.reset()
            self.token_tracker.model_name = model_config["model"]

        # 提取用户输入用于历史记录
        if messages and len(messages) > 0:
            last_user_message = next(
                (m for m in reversed(messages) if m.get("role") == "user"), None
            )
            if last_user_message:
                self.current_user_input = last_user_message.get("content", "")

        # 调用LLM并返回生成器
        response_generator = self._call_llm(messages, model_config)

        # 创建包装生成器来记录历史
        return self._response_with_history(response_generator)

    def _response_with_history(self, generator):
        """
        包装响应生成器以记录历史记录

        Args:
            generator: 原始响应生成器

        Returns:
            包装的生成器
        """
        # 收集完整响应用于保存到历史记录
        full_response = ""

        # 遍历并收集响应
        for chunk in generator:
            full_response += chunk
            yield chunk

        # 保存到历史记录（如果有用户输入）
        if self.current_user_input:
            # 检查是否已有该用户输入的记录
            existing_records = self.history_manager.get_history(limit=5)
            record = next(
                (
                    r
                    for r in existing_records
                    if r.get("content") == self.current_user_input
                ),
                None,
            )
            if record:
                # 更新已有记录的response字段，追加本次响应
                prev_response = record.get("response") or ""
                combined_response = prev_response + full_response
                # 更新历史记录
                self.history_manager.update_interaction(
                    record.get("id"), combined_response
                )
            else:
                # 新交互，添加记录
                self.history_manager.add_interaction(
                    self.current_user_input, full_response
                )
            # 重置当前用户输入，准备下一次记录
            self.current_user_input = None

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
            # 只有在实际调用LLM时才会加载OpenAI库
            client = openai.OpenAI(api_key=api_key or "EMPTY", base_url=f"{base_url}")

            # 准备请求参数
            params = {
                "model": model,
                "messages": messages,
                "temperature": model_config["temperature"],
                "max_tokens": model_config["max_tokens"],
                "stream": True,
            }

            # 如果跟踪token，估算提示tokens（实际值将在响应中获取）
            if self.track_tokens:
                # 简单估算，实际值会在响应中获取
                self.token_tracker.prompt_tokens = sum(
                    len(m.get("content", "")) // 4 for m in messages
                )

            # 创建流式处理
            stream = client.chat.completions.create(**params)
            saw_any = False
            in_think = False
            accumulated_content = ""  # 收集所有内容用于在结束时估算tokens

            for chunk in stream:
                delta = chunk.choices[0].delta
                reasoning = getattr(delta, "reasoning", None)
                content = delta.content

                # 更新token计数
                if self.track_tokens:
                    self.token_tracker.update_from_chunk(chunk)
                    if content:
                        accumulated_content += content

                # 思考内容
                if reasoning:
                    if not in_think:
                        yield "<think>"
                        in_think = True
                    saw_any = True
                    yield reasoning

                # 普通内容
                if content:
                    if in_think:
                        yield "</think>"
                        in_think = False
                    saw_any = True
                    yield content

            # 流结束后如果仍在思考模式，闭合标签
            if in_think:
                yield "</think>"

            # 如果没有任何输出，添加提示
            if not saw_any:
                empty = get_text("GENERAL", "llm_empty_response")
                yield empty

            # 如果跟踪token，再次确保completion_tokens正确更新
            if self.track_tokens and accumulated_content:
                # 如果前面的方法没有正确更新completion_tokens，使用粗略估计
                if self.token_tracker.completion_tokens == 0:
                    self.token_tracker.completion_tokens = len(accumulated_content) // 4
                # 确保总tokens正确
                self.token_tracker.total_tokens = (
                    self.token_tracker.prompt_tokens
                    + self.token_tracker.completion_tokens
                )

                yield "\n\n"  # 添加空行分隔
                for stat_line in self.token_tracker.get_formatted_stats():
                    yield stat_line + "\n"

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield error_msg

            # 如果跟踪token但发生错误，显示无法获取信息
            if self.track_tokens:
                yield "\n\n"
                yield get_text("GENERAL", "token_usage_not_available")

            return
