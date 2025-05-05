"""
MCP 配置模块 - 管理 MCP 服务器配置
"""
import os
import json
from typing import Any, Dict, Optional

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.expanduser("~/.config/viby"), "mcp_servers.json")

# 默认MCP服务器配置
DEFAULT_SERVERS = {
    "mcpServers": {
        "time": {
            "transport": "stdio",
            "command": "uvx",
            "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"]
        }
    }
}

def load_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """
    加载 MCP 服务器配置
    
    Args:
        config_file: 配置文件路径，默认为 ~/.config/viby/mcp_servers.json
        
    Returns:
        服务器配置字典
    """
    file_path = config_file or CONFIG_FILE
    
    # 如果配置文件不存在，创建默认配置
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_SERVERS, f, indent=2, ensure_ascii=False)
        return DEFAULT_SERVERS
    
    # 读取配置
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return DEFAULT_SERVERS

def get_server_config(server_name: Optional[str] = None) -> Dict[str, Any]:
    """
    获取指定服务器或所有服务器的配置
    
    Args:
        server_name: 服务器名称，如果为 None 则返回所有服务器配置
        
    Returns:
        服务器配置字典
    """
    config = load_config()
    servers = config.get("mcpServers", {})
    
    if not server_name:
        return servers
    
    # 返回指定服务器配置
    if server_name in servers:
        return {server_name: servers[server_name]}
    return {}

def save_config(config: Dict[str, Any], config_file: Optional[str] = None) -> None:
    """
    保存 MCP 服务器配置
    
    Args:
        config: 服务器配置字典
        config_file: 配置文件路径，默认为 ~/.config/viby/mcp_servers.json
    """
    file_path = config_file or CONFIG_FILE
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
