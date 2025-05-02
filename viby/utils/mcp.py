"""
MCP (Model Context Protocol) utilities for Viby
"""
import asyncio
from typing import Dict, Any, List, Optional

from fastmcp import Client
from viby.utils.mcp_config import get_server_config

def get_client(server_name: Optional[str] = None) -> Client:
    """获取MCP客户端
    
    Args:
        server_name: 服务器名称，如果为None则使用完整配置
        
    Returns:
        配置好的MCP客户端
    """
    # 直接获取服务器配置，自动配置已在get_server_config中处理
    server_config = get_server_config(server_name)
    return Client(server_config)

def get_tools(server_name: Optional[str] = None) -> List[Any]:
    """同步获取所有可用工具
    
    Args:
        server_name: 服务器名称，如果为None则使用默认服务器
        
    Returns:
        工具列表
    """
    async def _get():
        async with get_client(server_name) as client:
            return await client.list_tools()
    return asyncio.run(_get())

def call_tool(server_name: Optional[str] = None, tool_name: str = None, arguments: Dict[str, Any] = None):
    """同步调用指定工具
    
    Args:
        server_name: 服务器名称，如果为None则使用默认服务器
        tool_name: 工具名称
        arguments: 工具参数
        
    Returns:
        工具执行结果
    """
    async def _call():
        async with get_client(server_name) as client:
            return await client.call_tool(tool_name, arguments)
    return asyncio.run(_call())
