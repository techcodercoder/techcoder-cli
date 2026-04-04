"""
MCP client: builds Ollama tool schemas, dispatches tool calls, /mcp commands.
"""

import os

from .config import load_config, get_enabled_servers, set_server_enabled
from .tools import (
    filesystem_read, filesystem_write, filesystem_list,
    github_status, github_push, github_log,
    web_search, sqlite_query, log_action,
)

# ── Ollama tool definitions ───────────────────────────────────────────────────

_FS_TOOLS = [
    {'type': 'function', 'function': {
        'name': 'filesystem_read',
        'description': 'Read a file anywhere on the system.',
        'parameters': {'type': 'object', 'properties': {
            'path': {'type': 'string', 'description': 'Absolute or ~ path'},
        }, 'required': ['path']},
    }},
    {'type': 'function', 'function': {
        'name': 'filesystem_write',
        'description': 'Write content to a file anywhere on the system.',
        'parameters': {'type': 'object', 'properties': {
            'path':    {'type': 'string'},
            'content': {'type': 'string'},
        }, 'required': ['path', 'content']},
    }},
    {'type': 'function', 'function': {
        'name': 'filesystem_list',
        'description': 'List files and folders in a directory.',
        'parameters': {'type': 'object', 'properties': {
            'path': {'type': 'string'},
        }, 'required': ['path']},
    }},
]

_GH_TOOLS = [
    {'type': 'function', 'function': {
        'name': 'github_status',
        'description': 'Show current git branch, remote, and changed files.',
        'parameters': {'type': 'object', 'properties': {}, 'required': []},
    }},
    {'type': 'function', 'function': {
        'name': 'github_push',
        'description': 'Stage all changes, commit, and push to remote.',
        'parameters': {'type': 'object', 'properties': {
            'message': {'type': 'string', 'description': 'Commit message'},
        }, 'required': ['message']},
    }},
    {'type': 'function', 'function': {
        'name': 'github_log',
        'description': 'Show recent git commit history.',
        'parameters': {'type': 'object', 'properties': {
            'n': {'type': 'integer', 'description': 'Number of commits (default 5)'},
        }, 'required': []},
    }},
]

_WEB_TOOLS = [
    {'type': 'function', 'function': {
        'name': 'web_search',
        'description': 'Search the web for documentation or answers.',
        'parameters': {'type': 'object', 'properties': {
            'query':       {'type': 'string'},
            'num_results': {'type': 'integer'},
        }, 'required': ['query']},
    }},
]

_SQL_TOOLS = [
    {'type': 'function', 'function': {
        'name': 'sqlite_query',
        'description': 'Run a SELECT query against a local SQLite database.',
        'parameters': {'type': 'object', 'properties': {
            'query': {'type': 'string'},
        }, 'required': ['query']},
    }},
]

_SERVER_TOOLS = {
    'filesystem': _FS_TOOLS,
    'github':     _GH_TOOLS,
    'web_search': _WEB_TOOLS,
    'sqlite':     _SQL_TOOLS,
}

_DESTRUCTIVE = {'github_push', 'filesystem_write'}


# ── MCPClient ─────────────────────────────────────────────────────────────────

class MCPClient:
    def __init__(self, cwd: str = '.'):
        self.cwd     = cwd
        self.config  = load_config()
        self._enabled = get_enabled_servers(self.config)

    @property
    def enabled_servers(self) -> list[str]:
        return self._enabled

    @property
    def has_tools(self) -> bool:
        return bool(self._enabled)

    def tool_definitions(self) -> list[dict]:
        tools = []
        for server in self._enabled:
            tools.extend(_SERVER_TOOLS.get(server, []))
        return tools

    def execute_tool(self, name: str, arguments: dict) -> str:
        cfg     = self.config['servers']
        allowed = [os.path.expanduser(p) for p in cfg.get('filesystem', {}).get('allowed_paths', [])]
        if self.cwd not in allowed:
            allowed.append(self.cwd)

        if name == 'filesystem_read':
            result = filesystem_read(arguments['path'], allowed)
        elif name == 'filesystem_write':
            result = filesystem_write(arguments['path'], arguments['content'], allowed)
        elif name == 'filesystem_list':
            result = filesystem_list(arguments['path'], allowed)
        elif name == 'github_status':
            result = github_status(self.cwd)
        elif name == 'github_push':
            result = github_push(arguments['message'], self.cwd)
        elif name == 'github_log':
            result = github_log(arguments.get('n', 5), self.cwd)
        elif name == 'web_search':
            result = web_search(arguments['query'], arguments.get('num_results', 5))
        elif name == 'sqlite_query':
            db = cfg.get('sqlite', {}).get('db_path', '')
            result = sqlite_query(db, arguments['query']) if db else \
                "Error: sqlite db_path not set in ~/.techcoder/mcp_config.json"
        else:
            result = f"Error: unknown tool '{name}'"

        server = next(
            (s for s, tools in _SERVER_TOOLS.items()
             if any(t['function']['name'] == name for t in tools)),
            'unknown'
        )
        log_action(server, name, arguments, result)
        return result

    def needs_confirmation(self, tool_name: str) -> bool:
        return tool_name in _DESTRUCTIVE

    # ── /mcp commands ──────────────────────────────────────────────────────────

    def print_status(self):
        print("\n🔌 MCP Server Status\n" + "─" * 40)
        for server in _SERVER_TOOLS:
            icon = "✅" if server in self._enabled else "⭕"
            cfg  = self.config['servers'].get(server, {})
            note = ''
            if server == 'filesystem' and server in self._enabled:
                note = f"  allowed: {', '.join(cfg.get('allowed_paths', []))}"
            elif server == 'sqlite' and server in self._enabled:
                note = f"  db: {cfg.get('db_path') or '(not set)'}"
            print(f"  {icon} {server}{note}")
        print()

    def _reload(self):
        self.config   = load_config()
        self._enabled = get_enabled_servers(self.config)

    def cmd_enable(self, server: str) -> str:
        if server not in _SERVER_TOOLS:
            return f"❌ Unknown server '{server}'. Options: {', '.join(_SERVER_TOOLS)}"
        set_server_enabled(server, True)
        self._reload()
        return f"✅ Enabled: {server}"

    def cmd_disable(self, server: str) -> str:
        if server not in _SERVER_TOOLS:
            return f"❌ Unknown server '{server}'. Options: {', '.join(_SERVER_TOOLS)}"
        set_server_enabled(server, False)
        self._reload()
        return f"⭕ Disabled: {server}"
