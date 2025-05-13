
def search_similar_tools(self, query: str, top_k: int = 5) -> Dict[str, List[Tool]]:
    """
    搜索与查询最相关的工具

    Args:
        query: 查询文本
        top_k: 返回的最相关工具数量

    Returns:
        按服务名称分组的工具列表字典，格式为 {server_name: [Tool对象, ...], ...}
    """
    self._load_model()

    if not self.tool_embeddings:
        logger.warning("没有可用的工具embeddings，请先调用update_tool_embeddings")
        return {}

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
    
    # 获取top_k个工具并按服务器名称分组
    result_dict = {}
    
    for name, score in sorted_tools[:top_k]:
        # 从缓存的工具信息中获取定义
        if name not in self.tool_info:
            logger.warning(f"工具 {name} 在tool_info中不存在，跳过")
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
        
        result_dict[server_name].append(tool)

    return result_dict