# viby/mcp/client.py
import asyncio
import os
import threading
import atexit
import time
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

from fastmcp import Client
from viby.mcp.config import get_server_config


# --- Global Async Event Loop Manager ---
_async_loop_thread: Optional[threading.Thread] = None
_persistent_loop: Optional[asyncio.AbstractEventLoop] = None
_global_mcp_client_singleton: Optional["MCPClient"] = None  # Forward declaration
_loop_startup_lock = threading.Lock()  # Lock for initializing the loop and client


def _start_persistent_loop():
    global _persistent_loop
    try:
        _persistent_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_persistent_loop)
        _persistent_loop.run_forever()
    except Exception as e:
        print(f"Exception in persistent event loop thread: {e}")
    finally:
        if _persistent_loop and _persistent_loop.is_running():
            _persistent_loop.close()
        _persistent_loop = None


def get_persistent_loop() -> asyncio.AbstractEventLoop:
    global _async_loop_thread, _persistent_loop
    if _persistent_loop is None or not _persistent_loop.is_running():
        with _loop_startup_lock:  # Ensure only one thread initializes the loop
            if _persistent_loop is None or not _persistent_loop.is_running():
                if _async_loop_thread and _async_loop_thread.is_alive():
                    pass

                _async_loop_thread = threading.Thread(
                    target=_start_persistent_loop,
                    name="MCPAsyncLoopThread",
                    daemon=True,
                )
                _async_loop_thread.start()

                # Wait for the loop to be actually set and running
                # Add a timeout to prevent indefinite blocking
                timeout_seconds = 10
                start_time = time.monotonic()
                while (
                    _persistent_loop is None or not _persistent_loop.is_running()
                ) and (time.monotonic() - start_time < timeout_seconds):
                    time.sleep(0.05)

                if _persistent_loop is None or not _persistent_loop.is_running():
                    raise RuntimeError(
                        "Failed to start the persistent event loop within timeout."
                    )
    return _persistent_loop


def _run_coroutine_in_persistent_loop(coro):
    loop = get_persistent_loop()
    if threading.current_thread() == _async_loop_thread:
        # 不允许从事件循环自己的线程调用，这会导致死锁
        raise RuntimeError(
            "_run_coroutine_in_persistent_loop should not be called from the loop's own thread."
        )

    future = asyncio.run_coroutine_threadsafe(coro, loop)
    try:
        return future.result(timeout=60)  # Add a reasonable timeout
    except asyncio.TimeoutError:
        # 超时后取消任务
        future.cancel()
        raise
    except Exception:
        raise


def _shutdown_persistent_loop():
    global _persistent_loop, _global_mcp_client_singleton, _async_loop_thread

    if not _persistent_loop or not _persistent_loop.is_running():
        if _async_loop_thread and _async_loop_thread.is_alive():
            _async_loop_thread.join(timeout=5)
        return

    if _global_mcp_client_singleton:
        try:
            future = asyncio.run_coroutine_threadsafe(
                _global_mcp_client_singleton.close(), _persistent_loop
            )
            future.result(timeout=15)  # Wait for close to complete
        except Exception:
            pass
        finally:
            _global_mcp_client_singleton = None

    if _persistent_loop.is_running():
        _persistent_loop.call_soon_threadsafe(_persistent_loop.stop)

    if (
        _async_loop_thread
        and _async_loop_thread.is_alive()
        and threading.current_thread() != _async_loop_thread
    ):
        _async_loop_thread.join(timeout=10)

    _persistent_loop = None  # Mark as None after it's stopped and thread joined.
    _async_loop_thread = None


# Register cleanup at program exit, but only if not in a worker thread that might not own atexit
if threading.current_thread() is threading.main_thread():
    atexit.register(_shutdown_persistent_loop)
else:
    pass
# --- End Global Async Event Loop Manager ---


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


class MCPClient:
    """MCP 客户端，提供与 MCP 服务器的连接管理和工具调用"""

    def __init__(self, default_config: Optional[Dict[str, ConnectionConfig]] = None):
        """
        初始化 MCP 客户端

        Args:
            default_config: 服务器配置字典，格式为 {"server_name": server_config, ...}
        """
        self.default_config = default_config if default_config is not None else {}
        self.exit_stack = AsyncExitStack()
        self.active_clients: Dict[str, Client] = {}
        self._initialized_overall = False
        self._lock = asyncio.Lock()  # Lock for initializing specific server clients

    async def initialize_singleton(self):
        if not self._initialized_overall:
            self._initialized_overall = True

    async def _ensure_server_client_initialized(self, server_name: str):
        async with (
            self._lock
        ):  # Protect access to self.active_clients and shared config
            if server_name not in self.active_clients:
                config_to_use = self.default_config.get(server_name)
                if not config_to_use:
                    print(
                        f"Config for {server_name} not in initial default. Fetching dynamically."
                    )
                    dynamic_configs = get_server_config(
                        server_name
                    )  # Fetches {"server_name": conf} or {}
                    config_to_use = dynamic_configs.get(server_name)

                if not config_to_use:
                    raise ValueError(
                        f"Configuration for server {server_name} not found."
                    )

                transport = config_to_use.get("transport", "stdio")
                fastmcp_client_instance: Optional[Client] = None

                try:
                    if transport == "stdio":
                        env = config_to_use.get("env", {})
                        env.setdefault("PATH", os.environ.get("PATH", ""))
                        client_arg = {
                            "mcpServers": {
                                server_name: {
                                    "transport": "stdio",
                                    "command": config_to_use["command"],
                                    "args": config_to_use["args"],
                                    "env": env,
                                    "cwd": config_to_use.get("cwd"),
                                }
                            }
                        }
                        fastmcp_client_instance = Client(client_arg)
                    elif transport in ["sse", "websocket"]:
                        fastmcp_client_instance = Client(config_to_use["url"])
                    else:
                        raise ValueError(f"Unsupported transport type: {transport}")

                    await self.exit_stack.enter_async_context(fastmcp_client_instance)
                    self.active_clients[server_name] = fastmcp_client_instance
                except Exception as e:
                    print(f"Failed to initialize server {server_name}: {str(e)}")
                    raise

    async def list_servers(self) -> List[str]:
        """列出所有可用的服务器名称"""
        return list(self.default_config.keys())

    async def list_tools(self, server_name: Optional[str] = None) -> Dict[str, Any]:
        """列出指定服务器或所有服务器的工具"""
        result = {}
        servers_to_query = []

        if server_name:
            await self._ensure_server_client_initialized(server_name)
            if server_name not in self.active_clients:
                raise ValueError(
                    f"Server {server_name} client not available after init attempt."
                )
            servers_to_query.append(server_name)
        else:
            for s_name in self.default_config.keys():
                try:
                    await self._ensure_server_client_initialized(s_name)
                    if s_name in self.active_clients:
                        servers_to_query.append(s_name)
                    else:
                        print(
                            f"Skipping server {s_name} for list_tools as it's not active after init attempt."
                        )
                except Exception as e:
                    print(
                        f"Skipping server {s_name} for list_tools due to init error: {e}"
                    )

        for s_name_to_query in servers_to_query:
            if s_name_to_query in self.active_clients:
                raw_tools = await self.active_clients[s_name_to_query].list_tools()
                result[s_name_to_query] = raw_tools
            else:
                print(
                    f"Warning: Server {s_name_to_query} was in servers_to_query but not in active_clients."
                )
        return result

    async def call_tool(
        self, server_name: str, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """调用指定服务器的工具并返回统一格式{name, content}"""
        await self._ensure_server_client_initialized(server_name)
        if server_name not in self.active_clients:
            raise ValueError(f"Server {server_name} is not active. Cannot call tool.")
        return await self.active_clients[server_name].call_tool(tool_name, arguments)

    async def get_prompt(
        self,
        server_name: str,
        prompt_name: str,
        arguments: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """获取指定服务器的提示模板"""
        await self._ensure_server_client_initialized(server_name)
        if server_name not in self.active_clients:
            raise ValueError(f"Server {server_name} is not active. Cannot get prompt.")

        mcp_client = self.active_clients[server_name]
        prompt_result = await mcp_client.get_prompt(prompt_name, arguments or {})
        return [
            {"role": m.role, "content": getattr(m.content, "text", m.content)}
            for m in prompt_result.messages
        ]

    async def get_resource(
        self, server_name: str, resource_uri: str
    ) -> List[Dict[str, Any]]:
        """获取指定服务器的资源"""
        await self._ensure_server_client_initialized(server_name)
        if server_name not in self.active_clients:
            raise ValueError(
                f"Server {server_name} is not active. Cannot get resource."
            )

        mcp_client = self.active_clients[server_name]
        resource_result = await mcp_client.read_resource(resource_uri)
        return [
            {
                "type": "text" if hasattr(c, "text") else "blob",
                "mime_type": c.mimeType,
                "content": getattr(c, "text", c.blob),
            }
            for c in resource_result.contents
            if hasattr(c, "text") or hasattr(c, "blob")
        ]

    async def close(self):
        """关闭所有服务器连接"""
        async with self._lock:  # Ensure no new clients are added during close
            await self.exit_stack.aclose()
            self.active_clients = {}
            self._initialized_overall = False


async def _get_or_create_global_mcp_client_async() -> MCPClient:
    global _global_mcp_client_singleton
    if _global_mcp_client_singleton is None:
        all_server_configs = get_server_config()
        if not isinstance(all_server_configs, dict):
            print(
                f"Warning: get_server_config() returned type {type(all_server_configs)}, expected dict. Using empty config."
            )
            all_server_configs = {}

        _global_mcp_client_singleton = MCPClient(default_config=all_server_configs)
        await _global_mcp_client_singleton.initialize_singleton()
    return _global_mcp_client_singleton


def list_servers() -> List[str]:
    """同步获取所有服务器名称"""

    async def _coro():
        client = await _get_or_create_global_mcp_client_async()
        return await client.list_servers()

    try:
        return _run_coroutine_in_persistent_loop(_coro())
    except Exception as e:
        print(f"Error in list_servers: {e}")
        return []


def list_tools(server_name: Optional[str] = None) -> Dict[str, Any]:
    """同步获取工具列表"""

    async def _coro():
        client = await _get_or_create_global_mcp_client_async()
        return await client.list_tools(server_name)

    try:
        return _run_coroutine_in_persistent_loop(_coro())
    except Exception as e:
        print(f"Error in list_tools for '{server_name}': {e}")
        return {}


def call_tool(
    tool_name: str,
    server_name: str,
    arguments: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """同步调用工具，必须指定服务器"""

    async def _coro():
        client = await _get_or_create_global_mcp_client_async()
        return await client.call_tool(server_name, tool_name, arguments or {})

    try:
        return _run_coroutine_in_persistent_loop(_coro())
    except Exception as e:
        print(f"Error in call_tool '{tool_name}' on '{server_name}': {e}")
        return {
            "is_error": True,
            "content": [{"type": "text", "text": f"Failed to call tool: {str(e)}"}],
        }
