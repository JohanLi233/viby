"""
Model management for viby - handles interactions with LLM providers
"""

from typing import Dict, Any, List
from viby.config import config
from viby.locale import get_text
from viby.utils.history import HistoryManager
from viby.utils.logging import get_logger
from viby.llm.compaction import CompactionManager
from viby.llm.client import create_openai_client
import time

# 创建日志记录器
logger = get_logger()


class TokenTracker:
    """记录和跟踪LLM API调用的token使用情况"""

    def __init__(self):
        self.reset()

    def reset(self):
        """重置所有计数器"""
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
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
                return True
            return False
        except (AttributeError, TypeError):
            return False

    def update_from_chunk(self, chunk):
        """从流式返回的块中更新token计数"""
        try:
            # 从API直接提供的token信息更新计数
            usage = getattr(chunk, "usage", None)
            if usage:
                # 新的API响应格式可能包含完整的token计数信息
                if hasattr(usage, "prompt_tokens"):
                    self.prompt_tokens = usage.prompt_tokens

                if hasattr(usage, "completion_tokens"):
                    self.completion_tokens = usage.completion_tokens

                if hasattr(usage, "total_tokens"):
                    self.total_tokens = usage.total_tokens
                else:
                    # 如果没有提供total_tokens，则自行计算
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
    def __init__(self, args=None):
        self.use_think_model = args.get("think", False)
        self.use_fast_model = args.get("fast", False)
        self.track_tokens = args.get("tokens", False)
        self.token_tracker = TokenTracker() if self.track_tokens else None
        # 历史管理器
        self.history_manager = HistoryManager()
        # 当前用户输入（用于历史记录）
        self.current_user_input = None
        # 当前交互会话ID，用于标识一次完整的用户交互
        self.interaction_id = None
        # 标记当前交互是否已记录到历史
        self.interaction_recorded = False
        # 上一次处理过的用户消息引用，用于检测新输入
        self.last_user_message_ref = None
        # 添加消息压缩管理器
        self.compaction_manager = CompactionManager()

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
        model_config = config.get_model_config(model_type_to_use)

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
                user_input = last_user_message.get("content", "")

                # 判断是否为新的用户输入：通过比较消息对象引用
                if last_user_message is not self.last_user_message_ref:
                    logger.debug("检测到新的用户输入")
                    # 新的用户输入
                    self.last_user_message_ref = last_user_message
                    self.current_user_input = user_input
                    self.interaction_id = int(time.time() * 1000)
                    self.interaction_recorded = False

                    compressed_messages, compression_stats = (
                        self.compaction_manager.compact_messages(messages, model_config)
                    )

                    # 如果消息被压缩了，使用压缩后的消息
                    if compression_stats.get("compressed", False):
                        messages = compressed_messages

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

        # 保存到历史记录（如果有用户输入且未记录过当前交互，或者是新的用户输入）
        if (
            self.current_user_input
            and not self.interaction_recorded
            and self.interaction_id
        ):
            # 记录当前交互，并标记为已记录
            self.history_manager.add_interaction(
                self.current_user_input,
                full_response,
                metadata={"interaction_id": self.interaction_id},
            )
            self.interaction_recorded = True
            # 注意：不重置current_user_input，因为在工具调用过程中可能再次调用LLM
            # 只有当用户发送新消息时才会重置

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

        # 检查模型名是否为None，如果是则抛出错误
        if model is None:
            error_msg = get_text("GENERAL", "model_not_specified_error")
            yield error_msg
            return

        base_url = model_config["base_url"].rstrip("/")
        api_key = model_config.get("api_key", "")

        try:
            client = create_openai_client(
                api_key,
                base_url,
                http_referer="https://github.com/JohanLi233/viby",
                app_title="Viby",
            )

            # 准备请求参数
            params = {
                "model": model,
                "messages": messages,
                "stream": True,
            }

            # 只有当参数有值时才添加到请求中
            if model_config.get("temperature") is not None:
                params["temperature"] = model_config["temperature"]

            if model_config.get("max_tokens") is not None:
                params["max_tokens"] = model_config["max_tokens"]

            if model_config.get("top_p") is not None:
                params["top_p"] = model_config["top_p"]

            if self.track_tokens:
                params["stream_options"] = {"include_usage": True}

            # 创建流式处理
            stream = client.chat.completions.create(**params)
            has_output = False
            think_mode = False

            for chunk in stream:
                logger.debug(f"OpenAI API响应块: {chunk}")

                delta = chunk.choices[0].delta
                reasoning = getattr(delta, "reasoning", None)
                content = delta.content

                if self.track_tokens:
                    self.token_tracker.update_from_chunk(chunk)

                if reasoning:
                    if not think_mode:
                        yield "<think>"
                        think_mode = True
                    has_output = True
                    yield reasoning

                if content:
                    if think_mode:
                        yield "</think>"
                        think_mode = False
                    has_output = True
                    yield content

            if think_mode:
                yield "</think>"

            if not has_output:
                yield get_text("GENERAL", "llm_empty_response")

            if self.track_tokens:
                yield "\n\n"
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
