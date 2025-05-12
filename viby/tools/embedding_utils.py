"""
Embedding生成和相似度搜索工具

用于MCP工具检索系统的embedding相关功能
"""

import os
import json
import time
import numpy as np
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
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
            cache_dir: embedding缓存目录，默认为~/.viby/tool_embeddings
        """
        self.model = None  # 延迟加载模型
        self.tool_embeddings: Dict[str, np.ndarray] = {}
        self.tool_info: Dict[str, Dict] = {}
        self.tools_hash: str = ""  # 工具定义的哈希值，用于检测变化
        
        # 从配置中获取设置
        from viby.config import get_config
        config = get_config()
        self.embedding_config = config.get_embedding_config()
        
        # 设置缓存目录
        if cache_dir is None:
            cache_dir = self.embedding_config.get("cache_dir")
            if cache_dir is None:
                self.cache_dir = Path.home() / ".viby" / "tool_embeddings"
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
        """延迟加载sentence-transformer模型"""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                # 从配置中获取模型名称
                model_name = self.embedding_config.get("model_name", "jinaai/jina-embeddings-v3")
                logger.info(f"加载sentence-transformer模型: {model_name}...")
                self.model = SentenceTransformer(model_name)
                logger.info("模型加载完成")
            except Exception as e:
                logger.error(f"加载模型失败: {e}")
    
    def _load_cached_embeddings(self):
        """从缓存加载工具embeddings"""
        try:
            if self.meta_file.exists():
                with open(self.meta_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                    self.tools_hash = meta.get("tools_hash", "")
            
            if self.embedding_file.exists() and self.tool_info_file.exists():
                # 加载embeddings
                with np.load(self.embedding_file) as data:
                    for name in data.files:
                        self.tool_embeddings[name] = data[name]
                
                # 加载工具信息
                with open(self.tool_info_file, 'r', encoding='utf-8') as f:
                    self.tool_info = json.load(f)
                
                logger.info(f"从缓存加载了 {len(self.tool_embeddings)} 个工具的embeddings")
        except Exception as e:
            logger.warning(f"加载缓存的embeddings失败: {e}")
            # 重置状态，后续会重新生成
            self.tool_embeddings = {}
            self.tool_info = {}
            self.tools_hash = ""
    
    def _save_embeddings_to_cache(self, tools_hash: str):
        """将embeddings保存到缓存"""
        try:
            # 保存embeddings
            np.savez(self.embedding_file, **self.tool_embeddings)
            
            # 保存工具信息
            with open(self.tool_info_file, 'w', encoding='utf-8') as f:
                json.dump(self.tool_info, f, ensure_ascii=False, indent=2)
            
            # 保存元数据
            meta = {
                "tools_hash": tools_hash,
                "last_update": datetime.now().isoformat(),
                "model_name": self.embedding_config.get("model_name", "jinaai/jina-embeddings-v3")
            }
            with open(self.meta_file, 'w', encoding='utf-8') as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
            
            logger.info(f"已将 {len(self.tool_embeddings)} 个工具的embeddings保存到缓存")
        except Exception as e:
            logger.warning(f"保存embeddings到缓存失败: {e}")
    
    def _get_tool_description_text(self, tool_name: str, tool_def: Dict) -> str:
        """
        生成工具的描述文本，包含工具名称、描述和参数信息
        
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
        
        # 添加参数信息
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
                    logger.warning(f"获取工具 {tool_name} 参数 {param_name} 的描述时出错: {e}")
                    param_desc = ""
            
            is_required = "是" if param_name in required else "否"
            text += f"  - {param_name} ({param_type}, 必需: {is_required}): {param_desc}\n"
        
        return text
    
    def _calculate_tools_hash(self, tools: Dict[str, Dict]) -> str:
        """
        计算工具定义的哈希值，用于检测工具列表是否发生变化
        
        Args:
            tools: 工具定义字典
        
        Returns:
            工具定义的哈希值
        """
        # 构建一个描述所有工具的字符串
        tools_str = ""
        for name in sorted(tools.keys()):  # 按名称排序，确保稳定性
            definition = tools[name]
            tools_str += f"{name}:{self._get_tool_description_text(name, definition)}\n"
        
        # 计算哈希值
        return hashlib.md5(tools_str.encode('utf-8')).hexdigest()
    
    def should_update_embeddings(self, tools: Dict[str, Dict]) -> bool:
        """
        根据配置和工具变化情况，判断是否需要更新embeddings
        
        Args:
            tools: 工具定义字典
        
        Returns:
            是否需要更新
        """
        # 计算当前工具列表的哈希值
        current_hash = self._calculate_tools_hash(tools)
        
        # 检查更新频率
        update_frequency = self.embedding_config.get("update_frequency", "on_change")
        
        # 如果是手动模式，除非没有缓存或工具hash为空，否则不更新
        if update_frequency == "manual":
            if not self.tool_embeddings or not self.tools_hash:
                logger.info("手动更新模式，但没有现有embeddings，将进行初始化")
                return True
            return False
        
        # 如果是有变化时更新模式，检查哈希值是否变化
        if update_frequency == "on_change":
            if current_hash != self.tools_hash:
                logger.info("检测到工具定义变化，需要更新embeddings")
                return True
            return False
        
        # 默认情况
        return False
    
    def update_tool_embeddings(self, tools: Dict[str, Dict], force: bool = False):
        """
        更新工具embeddings
        
        Args:
            tools: 工具定义字典，格式为 {tool_name: tool_definition, ...}
            force: 是否强制更新所有工具的embeddings
        """
        # 计算工具哈希值
        current_hash = self._calculate_tools_hash(tools)
        
        # 检查是否需要更新
        if not force and not self.should_update_embeddings(tools):
            logger.info("根据配置和工具状态，当前不需要更新embeddings")
            return False
        
        self._load_model()
        
        # 获取需要更新的工具列表
        tools_to_update = {}
        for name, definition in tools.items():
            # 如果强制更新，或者工具不在缓存中，或者定义发生了变化，则需要更新
            tool_text = self._get_tool_description_text(name, definition)
            current_info = {
                "definition": definition,
                "text": tool_text
            }
            
            if (force or 
                name not in self.tool_info or 
                self.tool_info[name].get("text") != tool_text):
                tools_to_update[name] = current_info
            else:
                # 保留已有的工具信息和embedding
                self.tool_info[name] = current_info
        
        # 清理不存在的工具
        for name in list(self.tool_embeddings.keys()):
            if name not in tools:
                del self.tool_embeddings[name]
                if name in self.tool_info:
                    del self.tool_info[name]
        
        if not tools_to_update:
            logger.info("所有工具embeddings都是最新的，无需更新")
            # 更新哈希值
            self.tools_hash = current_hash
            self._save_embeddings_to_cache(current_hash)
            return False
        
        logger.info(f"需要更新 {len(tools_to_update)} 个工具的embeddings")
        
        # 批量生成embeddings
        texts = [info["text"] for info in tools_to_update.values()]
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        
        # 更新工具embeddings和信息
        for i, (name, info) in enumerate(tools_to_update.items()):
            self.tool_embeddings[name] = embeddings[i]
            self.tool_info[name] = info
        
        # 更新哈希值
        self.tools_hash = current_hash
        
        # 保存到缓存
        self._save_embeddings_to_cache(current_hash)
        return True
    
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
            tool_info = self.tool_info[name]
            definition = tool_info["definition"]
            
            # 构建结果
            tool_result = {
                "name": name,
                "score": score,
                "definition": definition
            }
            result.append(tool_result)
        
        return result 