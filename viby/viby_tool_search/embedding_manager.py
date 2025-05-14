"""
Embedding生成和相似度搜索工具

用于MCP工具检索系统的embedding相关功能
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass

# 导入locale模块提供的get_text函数
from viby.locale import get_text

# 导入配置单例
from viby.config import config

logger = logging.getLogger(__name__)


# 定义Tool类，与标准格式保持一致
@dataclass
class Tool:
    name: str
    description: str
    inputSchema: Dict[str, Any]
    annotations: Optional[Any] = None


class EmbeddingManager:
    """工具embedding管理器，负责生成、存储和检索工具的embedding向量"""

    def __init__(self, cache_dir: Optional[str] = None):
        """
        初始化工具embedding管理器
        """
        self.model = None  # 延迟加载模型
        self.tool_embeddings: Dict[str, np.ndarray] = {}
        self.tool_info: Dict[str, Dict] = {}

        # 使用全局配置单例
        self.embedding_config = config.get_embedding_config()

        # 简化缓存目录逻辑
        cache_path = cache_dir or self.embedding_config.get("cache_dir")
        self.cache_dir = (
            Path(cache_path)
            if cache_path
            else Path.home() / ".config" / "viby" / "tool_embeddings"
        )

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_file = self.cache_dir / "tool_embeddings.npz"
        self.tool_info_file = self.cache_dir / "tool_info.json"
        self.meta_file = self.cache_dir / "meta.json"

        # 尝试加载缓存的embeddings
        self._load_cached_embeddings()

    def _load_model(self):
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer

                # 从配置中获取模型名称
                model_name = self.embedding_config.get(
                    "model_name", "paraphrase-multilingual-MiniLM-L12-v2"
                )
                logger.info(
                    f"{get_text('TOOLS', 'loading_embedding_model', '加载sentence-transformer模型')}: {model_name}..."
                )

                self.model = SentenceTransformer(model_name, local_files_only=True)

                # 检查模型是否加载成功
                if self.model:
                    logger.info(
                        get_text("TOOLS", "model_load_complete", "模型加载完成")
                    )
                    return True
                else:
                    logger.error(
                        get_text(
                            "TOOLS", "model_load_empty", "模型加载失败，返回了空对象"
                        )
                    )
                    return False
            except Exception as e:
                logger.error(
                    f"{get_text('TOOLS', 'model_load_failed', '加载模型失败')}: {e}"
                )
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

                logger.debug(
                    f"{get_text('TOOLS', 'loaded_from_cache', '从缓存加载了')} {len(self.tool_embeddings)} {get_text('TOOLS', 'tools_embeddings', '个工具的embeddings')}"
                )
        except Exception as e:
            logger.warning(
                f"{get_text('TOOLS', 'load_cache_failed', '加载缓存的embeddings失败')}: {e}"
            )
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

            # 记录即将保存的工具数量和名称
            logger.info(
                f"{get_text('TOOLS', 'saving_to_cache', '即将保存')} {len(serializable_tool_info)} {get_text('TOOLS', 'tools_to_cache', '个工具信息到缓存')}"
            )
            logger.info(
                f"{get_text('TOOLS', 'tool_list', '工具列表')}: {sorted(list(serializable_tool_info.keys()))}"
            )

            # 保存工具信息
            with open(self.tool_info_file, "w", encoding="utf-8") as f:
                json.dump(serializable_tool_info, f, ensure_ascii=False, indent=2)

            # 保存元数据
            meta = {
                "last_update": datetime.now().isoformat(),
                "model_name": self.embedding_config.get(
                    "model_name", "paraphrase-multilingual-MiniLM-L12-v2"
                ),
                "tool_count": len(self.tool_embeddings),
                "tool_names": sorted(list(self.tool_embeddings.keys())),
            }
            with open(self.meta_file, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)

            # 验证保存后的文件
            try:
                with open(self.tool_info_file, "r", encoding="utf-8") as f:
                    saved_data = json.load(f)
                saved_count = len(saved_data)
                if saved_count != len(serializable_tool_info):
                    logger.warning(
                        f"{get_text('TOOLS', 'save_count_mismatch', '警告: 保存的工具数量不匹配!')} {get_text('TOOLS', 'expected', '预期')}: {len(serializable_tool_info)}, {get_text('TOOLS', 'actual', '实际')}: {saved_count}"
                    )
                    missing = set(serializable_tool_info.keys()) - set(
                        saved_data.keys()
                    )
                    if missing:
                        logger.warning(
                            f"{get_text('TOOLS', 'missing_tools', '缺失的工具')}: {missing}"
                        )
            except Exception as e:
                logger.warning(
                    f"{get_text('TOOLS', 'validate_error', '验证保存的工具信息时出错')}: {e}"
                )

            logger.info(
                f"{get_text('TOOLS', 'saved_to_cache', '已将')} {len(self.tool_embeddings)} {get_text('TOOLS', 'tools_saved', '个工具的embeddings保存到缓存')}"
            )
        except Exception as e:
            logger.error(
                f"{get_text('TOOLS', 'save_cache_failed', '保存embeddings到缓存失败')}: {e}",
                exc_info=True,
            )
            # 即使保存失败，也不应该中断整个流程

    def _safe_call(self, value, context: str, fallback=""):
        """安全调用可调用对象或返回值，出错时记录警告并返回fallback"""
        try:
            return value() if callable(value) else value
        except Exception as e:
            logger.warning(
                f"{context}{get_text('TOOLS', 'error_occurred', '时出错')}: {e}"
            )
            return fallback

    def _get_tool_description_text(self, tool_name: str, tool_def: Dict) -> str:
        """
        生成工具的描述文本，包含工具名称、描述和参数信息
        """
        # 获取工具描述
        description = self._safe_call(
            tool_def.get("description", ""),
            f"{get_text('TOOLS', 'get_tool_desc', '获取工具')} {tool_name} {get_text('TOOLS', 'description', '描述')}",
        )

        # 构建基本文本
        text = f"{get_text('TOOLS', 'tool_name', '工具名称')}: {tool_name}\n{get_text('TOOLS', 'description', '描述')}: {description}\n{get_text('TOOLS', 'parameters', '参数')}:\n"

        # 添加参数信息
        parameters = tool_def.get("parameters", {})
        properties = parameters.get("properties", {})
        required = parameters.get("required", [])

        for param_name, param_info in properties.items():
            param_type = param_info.get("type", "unknown")
            param_desc = self._safe_call(
                param_info.get("description", ""),
                f"{get_text('TOOLS', 'get_param_desc', '获取工具')} {tool_name} {get_text('TOOLS', 'param', '参数')} {param_name} {get_text('TOOLS', 'description', '描述')}",
            )

            is_required = (
                get_text("TOOLS", "required_yes", "是")
                if param_name in required
                else get_text("TOOLS", "required_no", "否")
            )
            text += f"  - {param_name} ({param_type}, {get_text('TOOLS', 'required', '必需')}: {is_required}): {param_desc}\n"

        return text

    def update_tool_embeddings(self, tools):
        """
        更新工具embeddings

        Args:
            tools: 标准格式: Dict[str, List[Tool]] - {server_name: [Tool对象, ...], ...}

        Returns:
            bool: 是否成功更新了embeddings
        """
        # 构建工具定义映射
        processed_tools = {
            tool.name: {
                "description": getattr(tool, "description", ""),
                "parameters": getattr(tool, "inputSchema", {}),
                "server_name": server_name,
            }
            for server_name, tools_list in tools.items()
            for tool in tools_list
            if hasattr(tool, "name")
        }
        logger.info(
            f"{get_text('TOOLS', 'prepare_update', '准备更新')} {len(processed_tools)} {get_text('TOOLS', 'tools_embedding', '个工具的嵌入')}"
        )

        # 确保嵌入模型加载
        if not self._load_model():
            logger.error(
                get_text("TOOLS", "embedding_model_load_failed", "嵌入模型加载失败")
            )
            return False

        # 生成文本和嵌入
        names, texts = (
            zip(
                *[
                    (name, self._get_tool_description_text(name, definition))
                    for name, definition in processed_tools.items()
                ]
            )
            if processed_tools
            else ([], [])
        )
        try:
            embeddings = self.model.encode(list(texts), convert_to_numpy=True)
        except Exception as e:
            logger.error(
                f"{get_text('TOOLS', 'generate_embedding_failed', '生成嵌入向量失败')}: {e}"
            )
            return False

        # 更新embeddings和info，忽略数量不匹配的情况
        self.tool_embeddings = {
            n: embeddings[i] for i, n in enumerate(names) if i < len(embeddings)
        }
        self.tool_info = {
            n: {"definition": processed_tools[n], "text": texts[i]}
            for i, n in enumerate(names)
            if i < len(embeddings)
        }
        self._save_embeddings_to_cache()
        return True

    def search_similar_tools(self, query: str, top_k: int = 5) -> Dict[str, List[Tool]]:
        """
        搜索与查询最相关的工具

        Args:
            query: 查询文本
            top_k: 返回的最相关工具数量

        Returns:
            按服务名称分组的工具列表字典，格式为 {server_name: [Tool对象, ...], ...}
        """
        # 确保模型可用
        if not self._load_model():
            logger.error(get_text("TOOLS", "model_load_failed", "加载模型失败"))
            return {}

        if not self.tool_embeddings:
            logger.warning(
                get_text(
                    "TOOLS",
                    "no_embeddings",
                    "没有可用的工具embeddings，请先调用update_tool_embeddings",
                )
            )
            return {}

        # 生成查询embedding
        try:
            query_embedding = self.model.encode(query, convert_to_numpy=True)
        except Exception as e:
            logger.error(
                f"{get_text('TOOLS', 'query_embedding_failed', '查询嵌入生成失败')}: {e}"
            )
            return {}

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

        # 获取top_k个工具并按服务器名称分组
        result_dict = {}

        for name, score in sorted_tools[:top_k]:
            # 从缓存的工具信息中获取定义
            if name not in self.tool_info:
                logger.warning(
                    f"{get_text('TOOLS', 'tool_not_exist', '工具')} {name} {get_text('TOOLS', 'not_in_tool_info', '在tool_info中不存在，跳过')}"
                )
                continue

            tool_info = self.tool_info[name]
            definition = tool_info.get("definition", {})

            # 获取服务器名称
            server_name = definition.get("server_name", "unknown")

            # 创建Tool对象
            tool = Tool(
                name=name,
                description=definition.get("description", ""),
                inputSchema=definition.get("parameters", {}),
            )

            # 将工具添加到对应的服务器分组
            if server_name not in result_dict:
                result_dict[server_name] = []

            logger.info(f"相似度: {score}")
            result_dict[server_name].append(tool)

        return result_dict
