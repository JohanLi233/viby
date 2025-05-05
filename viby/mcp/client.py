# viby/mcp/client.py
import asyncio
import os
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

from fastmcp import Client
from viby.mcp.config import get_server_config

EncodingErrorHandler = Literal["strict", "ignore", "replace"]

DEFAULT_ENCODING = "utf-8"
DEFAULT_ENCODING_ERROR_HANDLER: EncodingErrorHandler = "strict"
DEFAULT_HTTP_TIMEOUT = 5
DEFAULT_SSE_READ_TIMEOUT = 60 * 5


class StdioConfig(TypedDict):
    """标准输入输出连接配置"""

    transport: Literal["stdio"]
    command: str
    args: List[str]
    env: Optional[Dict[str, str]]
    cwd: Optional[Union[str, Path]]
    encoding: str
    encoding_error_handler: EncodingErrorHandler


class SSEConfig(TypedDict):
    """SSE连接配置"""

    transport: Literal["sse"]
    url: str
    headers: Optional[Dict[str, Any]]
    timeout: float
    sse_read_timeout: float


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
    async def get_connection(cls, server_name: str, config: Optional[Dict[str, ConnectionConfig]] = None):
        """
        从连接池获取指定服务器的连接，如果不存在则创建
        
        Args:
            server_name: 服务器名称
            config: 服务器配置字典
            
        Returns:
            Client 实例
        """
        global _connection_pool
        
        # 如果连接池中已有此服务器的客户端，直接返回
        if server_name in _connection_pool and _connection_pool[server_name] is not None:
            return _connection_pool[server_name]
            
        # 否则创建新的客户端并初始化
        client = cls(config)
        await client.initialize()
        
        # 获取对应服务器的Client实例
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
            if transport == "stdio":
                env = config.get("env") or {}
                env.setdefault("PATH", os.environ.get("PATH", ""))
                server_cfg = {
                    "command": config["command"],
                    "args": config["args"],
                    "env": env,
                    "encoding": config.get("encoding", DEFAULT_ENCODING),
                    "encodingErrorHandler": config.get(
                        "encoding_error_handler", DEFAULT_ENCODING_ERROR_HANDLER
                    ),
                    "transport": "stdio",
                }
            elif transport == "sse":
                server_cfg = {
                    "url": config["url"],
                    "headers": config.get("headers", {}),
                    "timeout": config.get("timeout", DEFAULT_HTTP_TIMEOUT),
                    "sseReadTimeout": config.get(
                        "sse_read_timeout", DEFAULT_SSE_READ_TIMEOUT
                    ),
                    "transport": "sse",
                }
            elif transport == "websocket":
                server_cfg = {
                    "url": config["url"],
                    "transport": "websocket",
                }
            else:
                raise ValueError(f"不支持的传输类型: {transport}")

            client_config = {"mcpServers": {server_name: server_cfg}}
            client = Client(client_config)
            await self.exit_stack.enter_async_context(client)
            self.clients[server_name] = client

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

    async def list_tools(self, server_name: Optional[str] = None) -> Dict[str, Any]:
        """
        列出指定服务器或所有服务器的工具

        Args:
            server_name: 服务器名称，如果为None则列出所有服务器的工具

        Returns:
            工具信息字典
        """
        if not self._initialized:
            await self.initialize()

        result = {}

        if server_name:
            if server_name not in self.clients:
                raise ValueError(f"服务器 {server_name} 不存在")

            tools_response = await self.clients[server_name].list_tools()

            # 转换为符合 OpenAI 的工具格式
            standard_tools = []
            for tool in tools_response:
                # 构建符合 OpenAI 格式的工具对象
                function_obj = {
                    "name": tool.name if hasattr(tool, "name") else str(tool),
                    "description": tool.description
                    if hasattr(tool, "description")
                    else "",
                }

                # 处理参数
                if hasattr(tool, "parameters"):
                    function_obj["parameters"] = tool.parameters
                elif hasattr(tool, "inputSchema"):
                    function_obj["parameters"] = tool.inputSchema

                # 添加到工具列表
                standard_tools.append({"type": "function", "function": function_obj})

            result[server_name] = standard_tools
        else:
            for name, client in self.clients.items():
                tools_response = await client.list_tools()

                # 转换为符合 OpenAI 的工具格式
                standard_tools = []
                for tool in tools_response:
                    # 构建符合 OpenAI 格式的工具对象
                    function_obj = {
                        "name": tool.name if hasattr(tool, "name") else str(tool),
                        "description": tool.description
                        if hasattr(tool, "description")
                        else "",
                    }

                    # 处理参数
                    if hasattr(tool, "parameters"):
                        function_obj["parameters"] = tool.parameters
                    elif hasattr(tool, "inputSchema"):
                        function_obj["parameters"] = tool.inputSchema

                    # 添加到工具列表
                    standard_tools.append(
                        {"type": "function", "function": function_obj}
                    )

                result[name] = standard_tools

        return result

    async def call_tool(
        self, server_name: str, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """调用指定服务器的工具并返回统一格式{name, content}"""
        if not self._initialized:
            await self.initialize()
        if server_name not in self.clients:
            raise ValueError(f"服务器 {server_name} 不存在")

        result = await self.clients[server_name].call_tool(tool_name, arguments)
        return result

    async def get_prompt(
        self,
        server_name: str,
        prompt_name: str,
        arguments: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        if not self._initialized:
            await self.initialize()

        result = await self.clients[server_name].get_prompt(
            prompt_name, arguments or {}
        )
        return [
            {"role": m.role, "content": getattr(m.content, "text", m.content)}
            for m in result.messages
        ]

    async def get_resource(
        self, server_name: str, resource_uri: str
    ) -> List[Dict[str, Any]]:
        if not self._initialized:
            await self.initialize()

        result = await self.clients[server_name].read_resource(resource_uri)
        return [
            {
                "type": "text" if hasattr(c, "text") else "blob",
                "mime_type": c.mimeType,
                "content": getattr(c, "text", c.blob),
            }
            for c in result.contents
            if hasattr(c, "text") or hasattr(c, "blob")
        ]

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
    if config is None:
        config = get_server_config()
        if not config:
            return []

    async def _runner():
        # 使用临时客户端获取服务器列表
        async with MCPClient(config) as client:
            return await client.list_servers()

    return _run_sync(_runner())


def list_tools(
    server_name: Optional[str] = None, config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """同步获取工具列表"""
    if config is None:
        config = get_server_config(server_name)
        if not config:
            return {}

    async def _runner():
        # 使用临时客户端获取工具列表
        async with MCPClient(config) as client:
            return await client.list_tools(server_name)

    return _run_sync(_runner())


def call_tool(
    tool_name: str,
    server_name: str,
    arguments: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    同步调用工具，必须指定服务器

    参数:
        tool_name: 要调用的工具名称
        server_name: 服务器名称
        arguments: 传递给工具的参数

    返回:
        工具调用结果，格式为统一的{name, content}结构
    """
    # 获取指定服务器的配置
    server_config = get_server_config(server_name)
    if not server_config:
        return {"is_error": True, "content": [{"type": "text", "text": f"服务器 {server_name} 配置不存在"}]}

    async def _runner():
        # 使用临时客户端调用工具
        async with MCPClient(server_config) as client:
            try:
                return await client.call_tool(server_name, tool_name, arguments or {})
            except Exception as e:
                return {
                    "is_error": True,
                    "content": [{"type": "text", "text": f"服务器 {server_name} 调用失败: {str(e)}"}],
                }

    return _run_sync(_runner())
