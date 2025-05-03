import asyncio
import json
import os
from typing import Any, Dict, List, Optional
from fastmcp import Client
from viby.config.mcp_config import CONFIG_FILE, get_server_config
from viby.locale import get_text

class MCPManager:
    def __init__(self, servers: Optional[List[str]] = None):
        cfg = get_server_config()
        self.servers = servers or list(cfg.get("mcpServers", {}))
        self._clients = {
            n: Client({"mcpServers": {n: cfg["mcpServers"][n]}})
            for n in self.servers
            if n in cfg.get("mcpServers", {})
        }

    async def _with_client(self, name: str, func):
        client = self._clients[name]
        async with client:
            return await func(client)

    async def list_tools_async(self) -> Dict[str, Any]:
        tasks = {
            n: asyncio.create_task(self._with_client(n, lambda c: c.list_tools()))
            for n in self._clients
        }
        results = {}
        for n, t in tasks.items():
            try:
                results[n] = await t
            except Exception as e:
                results[n] = {"error": str(e)}
        return results

    async def call_tool_async(self, tool: str, args: Dict[str, Any]=None, server: Optional[str]=None) -> Any:
        if server:
            return await self._with_client(server, lambda c: c.call_tool(tool, args))
        tools = await self.list_tools_async()
        for n, lst in tools.items():
            if isinstance(lst, list) and any(t.name == tool for t in lst):
                return await self._with_client(n, lambda c: c.call_tool(tool, args))
        raise KeyError(get_text("mcp", "no_server_for_tool", tool))

    def list_tools(self, server: Optional[str]=None) -> List[Any]:
        if server:
            return asyncio.run(self._with_client(server, lambda c: c.list_tools()))
        all_tools = asyncio.run(self.list_tools_async())
        return [t for sub in all_tools.values() if isinstance(sub, list) for t in sub]

    def call_tool(self, tool_name: str, arguments: Dict[str,Any]=None, server: Optional[str]=None):
        return asyncio.run(self.call_tool_async(tool_name, arguments, server=server))

    def save_config(self, cfg: Dict[str, Any]):
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE,'w',encoding='utf-8') as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        self.__init__(self.servers)

    def add_server(self, name: str, command: str, args: List[str]):
        cfg = get_server_config()
        cfg.setdefault("mcpServers", {})[name] = {"command":command, "args":args}
        self.save_config(cfg)

    def remove_server(self, name: str):
        cfg = get_server_config()
        cfg.get("mcpServers",{}).pop(name, None)
        self.save_config(cfg)

    def list_servers(self) -> List[str]:
        return list(self._clients.keys())

# 全局单例
_manager = MCPManager()

def get_client(server: Optional[str]=None) -> Client:
    return _manager._clients.get(server or (_manager.servers[0] if _manager.servers else None))

def get_tools(server: Optional[str]=None):
    return _manager.list_tools(server)

def call_tool(server: Optional[str]=None, tool_name: str=None, arguments: Dict[str,Any]=None):
    return _manager.call_tool(tool_name, arguments, server=server)

def add_server(name: str, command: str, args: List[str]):
    return _manager.add_server(name, command, args)

def remove_server(name: str):
    return _manager.remove_server(name)

def list_servers():
    return _manager.list_servers()

