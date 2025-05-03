"""MCP服务器配置管理模块"""
import os
import json
from typing import Dict, Any, Optional

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.expanduser("~/.config/viby"), "mcp_servers.json")

# 默认MCP服务器配置
DEFAULT_SERVERS = {
    "mcpServers": {
        "time": {
            "command": "uvx",
            "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"]
        }
    }
}

def get_server_config(server_name: Optional[str] = None) -> Dict[str, Any]:
    # 如果配置文件不存在，创建默认配置
    if not os.path.exists(CONFIG_FILE):
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_SERVERS, f, indent=2, ensure_ascii=False)
        return DEFAULT_SERVERS if not server_name else {
            "mcpServers": {
                server_name: DEFAULT_SERVERS["mcpServers"].get(server_name, {})
            }
        }
    
    # 读取配置
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            servers = json.load(f)
    except Exception:
        return DEFAULT_SERVERS
        
    # 返回指定服务器配置
    if not server_name:
        return servers
    
    # 假设配置正确
    return {
        "mcpServers": {
            server_name: servers.get("mcpServers", {}).get(server_name, {})
        }
    }
