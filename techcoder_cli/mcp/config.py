"""
MCP config loader/saver for ~/.techcoder/mcp_config.json
"""

import json
import os

from ..config.settings import MCP_CONFIG, MEMORY_DIR

_DEFAULTS: dict = {
    "servers": {
        "filesystem": {
            "enabled": True,
            "allowed_paths": ["~/projects", "~/Desktop", "~/Documents"]
        },
        "github":     {"enabled": False, "token": ""},
        "web_search": {"enabled": True},
        "sqlite":     {"enabled": False, "db_path": ""}
    }
}


def load_config() -> dict:
    if not os.path.isfile(MCP_CONFIG):
        save_config(_DEFAULTS)
        return json.loads(json.dumps(_DEFAULTS))
    try:
        with open(MCP_CONFIG) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return json.loads(json.dumps(_DEFAULTS))


def save_config(config: dict):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    with open(MCP_CONFIG, 'w') as f:
        json.dump(config, f, indent=2)


def get_enabled_servers(config: dict) -> list[str]:
    return [n for n, c in config.get('servers', {}).items() if c.get('enabled')]


def set_server_enabled(name: str, enabled: bool) -> bool:
    config = load_config()
    if name not in config.get('servers', {}):
        return False
    config['servers'][name]['enabled'] = enabled
    save_config(config)
    return True
