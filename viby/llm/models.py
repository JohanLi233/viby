"""
Model management for viby - handles interactions with LLM providers
"""

from typing import Dict, Any, List, Optional, Tuple
from viby.config import config
from viby.locale import get_text
from viby.utils.history import SessionManager
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
        self.model_name = None

    def reset(self):
        """重置所有计数器"""
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.start_time = time.time()
        self.end_time = None

    def update_counters(self, usage):
        """从响应中更新token计数"""
        try:
            if not usage:
                return False

            # 更新提示tokens
            if hasattr(usage, "prompt_tokens"):
                self.prompt_tokens = usage.prompt_tokens

            # 更新完成tokens
            if hasattr(usage, "completion_tokens"):
                self.completion_tokens = usage.completion_tokens

            # 更新或计算总tokens
            if hasattr(usage, "total_tokens"):
                self.total_tokens = usage.total_tokens
            else:
                self.total_tokens = self.prompt_tokens + self.completion_tokens

            return True
        except (AttributeError, TypeError):
            return False

    def update_from_response(self, response):
        """从完整响应中更新token计数"""
        usage = getattr(response, "usage", None)
        return self.update_counters(usage)

    def update_from_chunk(self, chunk):
        """从流式响应块中更新token计数"""
        usage = getattr(chunk, "usage", None)
        return self.update_counters(usage)

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
        stats.append(
            get_text("GENERAL", "token_usage_duration").format(f"{duration:.2f}s")
        )

        return stats


class ModelManager:
    def __init__(self, args=None):
        args = args or {}
        self.use_think_model = args.get("think", False)
        self.use_fast_model = args.get("fast", False)
        self.track_tokens = args.get("tokens", False)
        self.token_tracker = TokenTracker() if self.track_tokens else None

        # 历史记录和会话管理
        self.session_manager = SessionManager()
        self.compaction_manager = CompactionManager()

        # 当前交互状态
        self.current_user_input = None
        self.interaction_id = None
        self.interaction_recorded = False
        self.last_user_message_ref = None
        self.last_interaction_id = None

    def get_response(self, messages):
        """
        获取模型回复

        Args:
            messages: 消息历史

        Returns:
            生成器，返回文本块
        """
        # 确定使用的模型类型
        model_type = self._determine_model_type()
        model_config = config.get_model_config(model_type)

        # 准备调用所需的所有参数
        prepared_messages, user_input = self._prepare_messages(messages, model_config)

        # 调用LLM并返回生成器
        response_generator = self._call_llm(prepared_messages, model_config)

        # 创建包装生成器来记录历史
        return self._wrap_response_with_history(response_generator, user_input)

    def _determine_model_type(self) -> str:
        """确定要使用的模型类型"""
        if self.use_fast_model:
            return "fast"
        elif self.use_think_model:
            return "think"
        return "default"

    def _prepare_messages(
        self, messages, model_config
    ) -> Tuple[List[Dict], Optional[str]]:
        """准备消息并处理用户输入"""
        # 重置token跟踪器
        if self.track_tokens:
            self.token_tracker.reset()
            self.token_tracker.model_name = model_config["model"]

        # 提取用户输入用于历史记录
        user_input = None
        if messages:
            last_user_message = next(
                (m for m in reversed(messages) if m.get("role") == "user"), None
            )
            if last_user_message:
                user_input = last_user_message.get("content", "")

                # 判断是否为新的用户输入
                if last_user_message is not self.last_user_message_ref:
                    logger.debug("检测到新的用户输入")
                    self.last_user_message_ref = last_user_message
                    self.current_user_input = user_input
                    self.interaction_id = int(time.time() * 1000)
                    self.interaction_recorded = False

                    # 应用消息压缩
                    messages, _ = self.compaction_manager.compact_messages(
                        messages, model_config
                    )

        return messages, user_input

    def _wrap_response_with_history(self, generator, user_input):
        """包装响应生成器以记录历史记录"""
        full_response = ""

        # 遍历并收集响应
        for chunk in generator:
            full_response += chunk
            yield chunk

        # 处理历史记录
        self._update_history(full_response, user_input)

    def _update_history(self, full_response, user_input=None):
        """更新交互历史记录"""
        # 如果是新的交互且有用户输入
        if (
            self.current_user_input
            and not self.interaction_recorded
            and self.interaction_id
        ):
            # 记录新交互
            self.last_interaction_id = self.session_manager.add_interaction(
                self.current_user_input,
                full_response,
                metadata={"interaction_id": self.interaction_id},
            )
            self.interaction_recorded = True
        # 如果是同一交互的后续调用，追加到已有记录
        elif (
            self.interaction_recorded
            and self.last_interaction_id
            and self.last_interaction_id > 0
        ):
            # 获取上一条交互记录
            history = self.session_manager.get_history(limit=1)
            if history and len(history) > 0:
                # 追加新内容
                previous_response = history[0].get("response", "")
                updated_response = previous_response + "\n\n" + full_response
                # 更新记录
                self.session_manager.update_interaction(
                    self.last_interaction_id, updated_response
                )

    def update_last_interaction(self, additional_content):
        """更新最后一次交互的响应内容"""
        if not self.last_interaction_id or self.last_interaction_id <= 0:
            return False

        # 获取上一次交互的回复内容
        history = self.session_manager.get_history(limit=1)
        if not history or len(history) == 0:
            return False

        # 准备更新内容
        previous_response = history[0].get("response", "")
        updated_response = previous_response
        if updated_response and not updated_response.endswith("\n\n"):
            updated_response += "\n\n"
        updated_response += additional_content

        # 更新交互记录
        return self.session_manager.update_interaction(
            self.last_interaction_id, updated_response
        )

    def _call_llm(self, messages, model_config: Dict[str, Any]):
        """
        调用LLM并返回流式响应
        """
        model = model_config["model"]

        # 检查模型名是否为None
        if model is None:
            yield get_text("GENERAL", "model_not_specified_error")
            return

        # 准备API客户端和请求参数
        client = self._create_api_client(model_config)
        params = self._prepare_api_parameters(messages, model_config)

        try:
            # 创建流式处理
            stream = client.chat.completions.create(**params)

            # 处理响应
            yield from self._process_stream_response(stream)

        except Exception as e:
            # 处理错误
            yield f"Error: {str(e)}"

            # 显示token跟踪信息（如果启用）
            if self.track_tokens:
                yield "\n\n"
                yield get_text("GENERAL", "token_usage_not_available")

    def _create_api_client(self, model_config):
        """创建API客户端"""
        base_url = model_config["base_url"].rstrip("/")
        api_key = model_config.get("api_key", "")

        return create_openai_client(
            api_key,
            base_url,
            http_referer="https://github.com/JohanLi233/viby",
            app_title="Viby",
        )

    def _prepare_api_parameters(self, messages, model_config):
        """准备API请求参数"""
        params = {
            "model": model_config["model"],
            "messages": messages,
            "stream": True,
        }

        # 添加可选参数
        for param_name in ["temperature", "max_tokens", "top_p"]:
            if model_config.get(param_name) is not None:
                params[param_name] = model_config[param_name]

        # 如果跟踪tokens，添加相关选项
        if self.track_tokens:
            params["stream_options"] = {"include_usage": True}

        return params

    def _process_stream_response(self, stream):
        """处理流式响应"""
        has_output = False
        think_mode = False

        for chunk in stream:
            logger.debug(f"OpenAI API响应块: {chunk}")

            # 更新token计数
            if self.track_tokens:
                self.token_tracker.update_from_chunk(chunk)

            # 处理响应内容
            delta = chunk.choices[0].delta
            reasoning = getattr(delta, "reasoning", None)
            content = delta.content

            # 处理思考模式
            if reasoning:
                if not think_mode:
                    yield "<think>"
                    think_mode = True
                has_output = True
                yield reasoning

            # 处理内容
            if content:
                if think_mode:
                    yield "</think>"
                    think_mode = False
                has_output = True
                yield content

        # 完成思考模式
        if think_mode:
            yield "</think>"

        # 如果没有输出，返回空响应消息
        if not has_output:
            yield get_text("GENERAL", "llm_empty_response")

        # 添加token统计信息
        if self.track_tokens:
            yield "\n\n"
            for stat_line in self.token_tracker.get_formatted_stats():
                yield stat_line + "\n"
