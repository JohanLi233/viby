"""
Embedding生成和相似度搜索工具

用于MCP工具检索系统的embedding相关功能
"""

import os
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# 避免在没有GPU时出现警告
os.environ["TOKENIZERS_PARALLELISM"] = "false"

logger = logging.getLogger(__name__)


class ToolEmbeddingManager:
    """工具embedding管理器，负责生成、存储和检索工具的embedding向量"""

    def __init__(self, cache_dir: Optional[str] = None):
        """
        初始化工具embedding管理器

        Args:
            cache_dir: embedding缓存目录，默认为~/.config/viby/tool_embeddings
        """
        self.model = None  # 延迟加载模型
        self.tool_embeddings: Dict[str, np.ndarray] = {}
        self.tool_info: Dict[str, Dict] = {}

        # 从配置中获取设置
        from viby.config import Config

        config = Config()
        self.embedding_config = config.get_embedding_config()

        # 设置缓存目录
        if cache_dir is None:
            cache_dir = self.embedding_config.get("cache_dir")
            if cache_dir is None:
                self.cache_dir = Path.home() / ".config" / "viby" / "tool_embeddings"
            else:
                self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path(cache_dir)

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_file = self.cache_dir / "tool_embeddings.npz"
        self.tool_info_file = self.cache_dir / "tool_info.json"
        self.meta_file = self.cache_dir / "meta.json"

        # 尝试加载缓存的embeddings
        self._load_cached_embeddings()

    def _load_model(self):
        """
        延迟加载sentence-transformer模型

        Returns:
            bool: 是否成功加载模型
        """
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer

                # 从配置中获取模型名称
                model_name = self.embedding_config.get("model_name", "BAAI/bge-m3")
                logger.info(f"加载sentence-transformer模型: {model_name}...")

                # 添加超时处理，避免模型下载过久阻塞程序
                self.model = SentenceTransformer(model_name, trust_remote_code=True)

                # 检查模型是否加载成功
                if self.model:
                    logger.info("模型加载完成")
                    return True
                else:
                    logger.error("模型加载失败，返回了空对象")
                    return False
            except Exception as e:
                logger.error(f"加载模型失败: {e}")
                self.model = None
                return False
        return True

    def _load_cached_embeddings(self):
        """从缓存加载工具embeddings"""
        try:
            if self.embedding_file.exists() and self.tool_info_file.exists():
                # 加载embeddings
                with np.load(self.embedding_file) as data:
                    for name in data.files:
                        self.tool_embeddings[name] = data[name]

                # 加载工具信息
                with open(self.tool_info_file, "r", encoding="utf-8") as f:
                    self.tool_info = json.load(f)

                logger.info(
                    f"从缓存加载了 {len(self.tool_embeddings)} 个工具的embeddings"
                )
        except Exception as e:
            logger.warning(f"加载缓存的embeddings失败: {e}")
            # 重置状态，后续会重新生成
            self.tool_embeddings = {}
            self.tool_info = {}

    def _save_embeddings_to_cache(self):
        """将embeddings保存到缓存"""
        try:
            # 保存embeddings
            np.savez(self.embedding_file, **self.tool_embeddings)

            # 创建可序列化的工具信息副本
            serializable_tool_info = {}
            for name, info in self.tool_info.items():
                serializable_info = {}
                # 只需保存文本描述和定义（标准MCP格式）
                serializable_info["text"] = info.get("text", "")
                serializable_info["definition"] = info.get("definition", {})
                serializable_tool_info[name] = serializable_info

            # 保存工具信息
            with open(self.tool_info_file, "w", encoding="utf-8") as f:
                json.dump(serializable_tool_info, f, ensure_ascii=False, indent=2)

            # 保存元数据
            meta = {
                "last_update": datetime.now().isoformat(),
                "model_name": self.embedding_config.get("model_name", "BAAI/bge-m3"),
                "tool_count": len(self.tool_embeddings),
            }
            with open(self.meta_file, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)

            logger.info(
                f"已将 {len(self.tool_embeddings)} 个工具的embeddings保存到缓存"
            )
        except Exception as e:
            logger.warning(f"保存embeddings到缓存失败: {e}")
            # 即使保存失败，也不应该中断整个流程

    def _get_tool_description_text(self, tool_name: str, tool_def: Dict) -> str:
        """
        生成工具的描述文本，包含工具名称、描述和参数信息 - 仅处理标准MCP格式

        Args:
            tool_name: 工具名称
            tool_def: 工具定义字典

        Returns:
            包含工具完整信息的文本
        """
        # 获取工具描述
        description = tool_def.get("description", "")
        if callable(description):
            try:
                description = description()
            except Exception as e:
                logger.warning(f"获取工具 {tool_name} 的描述时出错: {e}")
                description = ""

        # 构建基本文本
        text = f"工具名称: {tool_name}\n描述: {description}\n参数:\n"

        # 添加参数信息 - 标准MCP工具格式
        parameters = tool_def.get("parameters", {})
        properties = parameters.get("properties", {})
        required = parameters.get("required", [])

        for param_name, param_info in properties.items():
            param_type = param_info.get("type", "unknown")
            param_desc = param_info.get("description", "")
            if callable(param_desc):
                try:
                    param_desc = param_desc()
                except Exception as e:
                    logger.warning(
                        f"获取工具 {tool_name} 参数 {param_name} 的描述时出错: {e}"
                    )
                    param_desc = ""

            is_required = "是" if param_name in required else "否"
            text += (
                f"  - {param_name} ({param_type}, 必需: {is_required}): {param_desc}\n"
            )

        return text

    def update_tool_embeddings(self, tools: Dict[str, Dict]):
        """
        更新工具embeddings - 假设所有工具都是标准MCP格式

        Args:
            tools: 工具定义字典，格式为 {tool_name: tool_definition, ...}

        Returns:
            bool: 是否成功更新了embeddings
        """
        # 确保模型已完全加载
        try:
            self._load_model()
            if self.model is None:
                logger.error("嵌入模型加载失败，无法继续更新embeddings")
                return False
        except Exception as e:
            logger.error(f"嵌入模型加载失败: {e}")
            return False

        # 获取需要更新的工具列表
        tools_to_update = {}
        for name, definition in tools.items():
            tool_text = self._get_tool_description_text(name, definition)
            current_info = {"definition": definition, "text": tool_text}
            tools_to_update[name] = current_info

        # 清理不存在的工具
        for name in list(self.tool_embeddings.keys()):
            if name not in tools:
                del self.tool_embeddings[name]
                if name in self.tool_info:
                    del self.tool_info[name]

        logger.info(f"需要更新 {len(tools_to_update)} 个工具的embeddings")

        try:
            # 批量生成embeddings
            texts = [info["text"] for info in tools_to_update.values()]
            embeddings = self.model.encode(texts, convert_to_numpy=True)

            # 更新工具embeddings和信息
            for i, (name, info) in enumerate(tools_to_update.items()):
                self.tool_embeddings[name] = embeddings[i]
                self.tool_info[name] = info

            self._save_embeddings_to_cache()
            return True
        except Exception as e:
            logger.error(f"生成嵌入向量失败: {e}")
            return False

    def search_similar_tools(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        搜索与查询最相关的工具

        Args:
            query: 查询文本
            top_k: 返回的最相关工具数量

        Returns:
            相关工具列表，每个工具包含名称、描述、参数、相似度得分等信息
        """
        self._load_model()

        if not self.tool_embeddings:
            logger.warning("没有可用的工具embeddings，请先调用update_tool_embeddings")
            return []

        # 生成查询embedding
        query_embedding = self.model.encode(query, convert_to_numpy=True)

        # 计算所有工具与查询的相似度
        similarities = {}
        for name, embedding in self.tool_embeddings.items():
            # 计算余弦相似度
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )
            similarities[name] = float(similarity)

        # 按相似度降序排序
        sorted_tools = sorted(similarities.items(), key=lambda x: x[1], reverse=True)

        # 获取top_k个工具
        result = []
        for name, score in sorted_tools[:top_k]:
            # 从缓存的工具信息中获取定义
            if name not in self.tool_info:
                logger.warning(f"工具 {name} 在tool_info中不存在，跳过")
                continue

            tool_info = self.tool_info[name]
            definition = tool_info.get("definition", {})

            # 构建结果
            tool_result = {
                "name": name,
                "score": score,
                "definition": definition,
                "server_name": definition.get("server_name", "unknown"),
            }
            result.append(tool_result)

        return result
