"""
Application-wide settings and constants.
No imports from other techcoder_cli modules.
"""

import os

# ── Model ─────────────────────────────────────────────────────────────────────
MODEL_NAME = 'gemma4:e4b'

# ── Paths ─────────────────────────────────────────────────────────────────────
MEMORY_DIR  = os.path.expanduser('~/.techcoder')
MEMORY_FILE = os.path.join(MEMORY_DIR, 'memory.json')
MCP_CONFIG  = os.path.join(MEMORY_DIR, 'mcp_config.json')
MCP_LOG     = os.path.join(MEMORY_DIR, 'mcp_log.json')
LOG_DIR     = os.path.join(MEMORY_DIR, 'logs')
LOG_FILE    = os.path.join(LOG_DIR, 'techcoder.log')

# ── Memory ────────────────────────────────────────────────────────────────────
MAX_MEMORY_WORDS    = 500
MAX_MEMORY_LEARNED  = 20
MAX_MEMORY_PROJECTS = 10

# ── Web UI ────────────────────────────────────────────────────────────────────
DEFAULT_PORT = 3000

# ── Agent ─────────────────────────────────────────────────────────────────────
MAX_TOOL_ITERATIONS = 6   # max Ollama tool-call loops before giving up

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_LEVEL = 'INFO'

# ── Scan ignore list ──────────────────────────────────────────────────────────
SCAN_IGNORE_DIRS = {
    '.git', '.dart_tool', '.idea', '__pycache__',
    'venv', '.venv', 'node_modules', 'build', '.build',
    'dist', '.pytest_cache', '.mypy_cache',
}
