# viby/mcp/client.py
import asyncio
import os
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

from fastmcp import Client
from viby.mcp.config import get_server_config


class StdioConfig(TypedDict):
    """标准输入输出连接配置"""
    transport: Literal["stdio"]
    command: str
    args: List[str]
    env: Optional[Dict[str, str]]
    cwd: Optional[Union[str, Path]]


class SSEConfig(TypedDict):
    """SSE连接配置"""
    transport: Literal["sse"]
    url: str
    headers: Optional[Dict[str, Any]]


class WebsocketConfig(TypedDict):
    """Websocket连接配置"""
    transport: Literal["websocket"]
    url: str


ConnectionConfig = Union[StdioConfig, SSEConfig, WebsocketConfig]


# 全局连接池，用于保存已初始化的客户端连接
_connection_pool = {}


class MCPClient:
    """MCP 客户端，提供与 MCP 服务器的连接管理和工具调用"""

    def __init__(self, config: Optional[Dict[str, ConnectionConfig]] = None):
        """
        初始化 MCP 客户端

        Args:
            config: 服务器配置字典，格式为 {"server_name": server_config, ...}
        """
        self.config = config or {}
        self.exit_stack = AsyncExitStack()
        self.clients: Dict[str, Client] = {}
        self._initialized = False

    @classmethod
    async def get_connection(
        cls, server_name: str, config: Optional[Dict[str, ConnectionConfig]] = None
    ):
        """
        从连接池获取指定服务器的连接，如果不存在则创建

        Args:
            server_name: 服务器名称
            config: 服务器配置字典

        Returns:
            Client 实例
        """
        if server_name in _connection_pool and _connection_pool[server_name]:
            return _connection_pool[server_name]

        client = cls(config)
        await client.initialize()
        
        if server_name in client.clients:
            _connection_pool[server_name] = client.clients[server_name]
            return client.clients[server_name]
        
        return None

    async def initialize(self):
        """初始化所有配置的服务器连接"""
        if self._initialized:
            return

        for server_name, config in self.config.items():
            transport = config.get("transport", "stdio")
            
            try:
                if transport == "stdio":
                    env = config.get("env", {})
                    env.setdefault("PATH", os.environ.get("PATH", ""))
                    client_arg = {
                        "mcpServers": {
                            server_name: {
                                "transport": "stdio",
                                "command": config["command"],
                                "args": config["args"],
                                "env": env
                            }
                        }
                    }
                    client = Client(client_arg)
                elif transport in ["sse", "websocket"]:
                    client = Client(config["url"])
                else:
                    raise ValueError(f"不支持的传输类型: {transport}")
                
                await self.exit_stack.enter_async_context(client)
                self.clients[server_name] = client
            except Exception as e:
                print(f"初始化服务器 {server_name} 失败: {str(e)}")
                
        self._initialized = True

    async def close(self):
        """关闭所有服务器连接"""
        await self.exit_stack.aclose()
        self.clients = {}
        self._initialized = False

    async def list_servers(self) -> List[str]:
        """列出所有可用的服务器名称"""
        if not self._initialized:
            await self.initialize()
        return list(self.clients.keys())

    def _convert_tools_to_standard_format(self, tools_response):
        """将MCP工具响应转换为符合OpenAI标准的工具格式"""
        standard_tools = []
        
        for tool in tools_response:
            function_obj = {
                "name": getattr(tool, "name", str(tool)),
                "description": getattr(tool, "description", "")
            }

            if hasattr(tool, "parameters"):
                function_obj["parameters"] = tool.parameters
            elif hasattr(tool, "inputSchema"):
                function_obj["parameters"] = tool.inputSchema

            standard_tools.append({"type": "function", "function": function_obj})
            
        return standard_tools
    
    async def list_tools(self, server_name: Optional[str] = None) -> Dict[str, Any]:
        """列出指定服务器或所有服务器的工具"""
        if not self._initialized:
            await self.initialize()

        result = {}

        if server_name:
            if server_name not in self.clients:
                raise ValueError(f"服务器 {server_name} 不存在")
            tools_response = await self.clients[server_name].list_tools()
            result[server_name] = self._convert_tools_to_standard_format(tools_response)
        else:
            for name, client in self.clients.items():
                tools_response = await client.list_tools()
                result[name] = self._convert_tools_to_standard_format(tools_response)

        return result

    async def call_tool(
        self, server_name: str, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """调用指定服务器的工具并返回统一格式{name, content}"""
        if not self._initialized:
            await self.initialize()
        if server_name not in self.clients:
            raise ValueError(f"服务器 {server_name} 不存在")
            
        return await self.clients[server_name].call_tool(tool_name, arguments)

    async def get_prompt(
        self,
        server_name: str,
        prompt_name: str,
        arguments: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """获取指定服务器的提示模板"""
        if not self._initialized:
            await self.initialize()

        result = await self.clients[server_name].get_prompt(prompt_name, arguments or {})
        return [{"role": m.role, "content": getattr(m.content, "text", m.content)} 
                for m in result.messages]

    async def get_resource(
        self, server_name: str, resource_uri: str
    ) -> List[Dict[str, Any]]:
        """获取指定服务器的资源"""
        if not self._initialized:
            await self.initialize()

        result = await self.clients[server_name].read_resource(resource_uri)
        return [{
            "type": "text" if hasattr(c, "text") else "blob",
            "mime_type": c.mimeType,
            "content": getattr(c, "text", c.blob),
        } for c in result.contents if hasattr(c, "text") or hasattr(c, "blob")]

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()


def _run_sync(awaitable):
    """在新的事件循环中运行 awaitable 并返回结果"""
    return asyncio.run(awaitable)


def list_servers(config: Optional[Dict[str, Any]] = None) -> List[str]:
    """同步获取所有服务器名称"""
    config = config or get_server_config()
    if not config:
        return []

    async def _runner():
        async with MCPClient(config) as client:
            return await client.list_servers()

    return _run_sync(_runner())


def list_tools(
    server_name: Optional[str] = None, config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """同步获取工具列表"""
    config = config or get_server_config(server_name)
    if not config:
        return {}

    async def _runner():
        async with MCPClient(config) as client:
            return await client.list_tools(server_name)

    return _run_sync(_runner())


def call_tool(
    tool_name: str,
    server_name: str,
    arguments: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """同步调用工具，必须指定服务器"""
    server_config = get_server_config(server_name)
    if not server_config:
        return {
            "is_error": True,
            "content": [{"type": "text", "text": f"服务器 {server_name} 配置不存在"}],
        }

    async def _runner():
        async with MCPClient(server_config) as client:
            try:
                return await client.call_tool(server_name, tool_name, arguments or {})
            except Exception as e:
                return {
                    "is_error": True,
                    "content": [{
                        "type": "text",
                        "text": f"服务器 {server_name} 调用失败: {str(e)}",
                    }],
                }

    return _run_sync(_runner())
