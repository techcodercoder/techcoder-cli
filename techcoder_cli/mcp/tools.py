"""
Tool implementations for each MCP server type.
Each function returns a plain string fed back to Gemma.
"""

import json
import os
import sqlite3
import subprocess
from datetime import datetime

from ..config.settings import MCP_LOG
from ..utils.logger import get_logger

log = get_logger(__name__)


# ── Filesystem ────────────────────────────────────────────────────────────────

def _resolve(path: str, allowed_paths: list[str]) -> str | None:
    expanded = os.path.realpath(os.path.expanduser(path))
    for allowed in allowed_paths:
        if expanded.startswith(os.path.realpath(os.path.expanduser(allowed))):
            return expanded
    return None


def filesystem_read(path: str, allowed_paths: list[str]) -> str:
    real = _resolve(path, allowed_paths)
    if real is None:
        return f"Error: '{path}' is outside allowed paths"
    try:
        with open(real) as f:
            lines = f.readlines()
        if len(lines) > 300:
            lines = lines[:300] + [f'\n... [{len(lines) - 300} more lines]']
        return ''.join(lines)
    except FileNotFoundError:
        return f"Error: file not found: {path}"
    except Exception as e:
        return f"Error reading: {e}"


def filesystem_write(path: str, content: str, allowed_paths: list[str]) -> str:
    real = _resolve(path, allowed_paths)
    if real is None:
        return f"Error: '{path}' is outside allowed paths"
    try:
        os.makedirs(os.path.dirname(real) or '.', exist_ok=True)
        with open(real, 'w') as f:
            f.write(content)
        return f"Written: {path}"
    except Exception as e:
        return f"Error writing: {e}"


def filesystem_list(path: str, allowed_paths: list[str]) -> str:
    real = _resolve(path, allowed_paths)
    if real is None:
        return f"Error: '{path}' is outside allowed paths"
    try:
        entries = sorted(os.listdir(real))
        return '\n'.join(
            f"{'📁' if os.path.isdir(os.path.join(real, e)) else '📄'} {e}"
            for e in entries
        ) or "(empty)"
    except Exception as e:
        return f"Error listing: {e}"


# ── GitHub ────────────────────────────────────────────────────────────────────

def _git(args: list[str], cwd: str) -> tuple[str, str, int]:
    r = subprocess.run(['git'] + args, capture_output=True, text=True, cwd=cwd)
    return r.stdout.strip(), r.stderr.strip(), r.returncode


def github_status(cwd: str = '.') -> str:
    stdout, stderr, rc = _git(['status', '--short'], cwd)
    if rc != 0:
        return f"Error: {stderr or 'not a git repo'}"
    branch, _, _ = _git(['branch', '--show-current'], cwd)
    remote, _, _ = _git(['remote', 'get-url', 'origin'], cwd)
    return f"Branch : {branch}\nRemote : {remote}\nChanges:\n{stdout or '(clean)'}"


def github_push(message: str, cwd: str = '.') -> str:
    for args in [['add', '-A'], ['commit', '-m', message]]:
        _, stderr, rc = _git(args, cwd)
        if rc != 0 and 'nothing to commit' not in (stderr or ''):
            return f"Error: {stderr}"
    _, stderr, rc = _git(['push'], cwd)
    if rc != 0:
        return f"Error pushing: {stderr}"
    remote, _, _ = _git(['remote', 'get-url', 'origin'], cwd)
    return f"Pushed to {remote}\nCommit: {message}"


def github_log(n: int = 5, cwd: str = '.') -> str:
    stdout, stderr, rc = _git(['log', f'-{n}', '--oneline', '--decorate'], cwd)
    return stdout if rc == 0 else f"Error: {stderr}"


# ── Web search ────────────────────────────────────────────────────────────────

def web_search(query: str, num_results: int = 5) -> str:
    try:
        import re
        import requests
        resp = requests.post(
            'https://lite.duckduckgo.com/lite/',
            data={'q': query},
            headers={'User-Agent': 'Mozilla/5.0 (techcoder-cli)'},
            timeout=10,
        )
        resp.raise_for_status()

        def clean(html: str) -> str:
            return re.sub(r'<[^>]+>', '', html).strip()

        titles   = re.findall(r'class="result-link"[^>]*>(.*?)</a>', resp.text, re.DOTALL)
        snippets = re.findall(r'class="result-snippet"[^>]*>(.*?)</td>', resp.text, re.DOTALL)
        results  = [
            f"{i}. {clean(t)}\n   {clean(s)}"
            for i, (t, s) in enumerate(zip(titles[:num_results], snippets[:num_results]), 1)
        ]
        return f"Results for '{query}':\n\n" + '\n\n'.join(results) if results else f"No results for: {query}"
    except ImportError:
        return "Error: 'requests' not installed. Run: pip install requests"
    except Exception as e:
        return f"Search error: {e}"


# ── SQLite ────────────────────────────────────────────────────────────────────

def sqlite_query(db_path: str, query: str) -> str:
    expanded = os.path.expanduser(db_path)
    if not os.path.isfile(expanded):
        return f"Error: database not found: {db_path}"
    if any(query.strip().upper().startswith(kw) for kw in ('DROP', 'DELETE', 'TRUNCATE', 'ALTER')):
        return "Error: destructive SQL not allowed via MCP"
    try:
        con = sqlite3.connect(expanded)
        cur = con.execute(query)
        rows      = cur.fetchmany(50)
        col_names = [d[0] for d in cur.description] if cur.description else []
        con.close()
        if not rows:
            return "(no rows)"
        header = ' | '.join(col_names)
        body   = '\n'.join(' | '.join(str(v) for v in row) for row in rows)
        return f"{header}\n{'-' * len(header)}\n{body}"
    except Exception as e:
        return f"SQL error: {e}"


# ── Action log ────────────────────────────────────────────────────────────────

def log_action(server: str, tool: str, args: dict, result: str):
    entry = {
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'server': server, 'tool': tool,
        'args': args, 'result': result[:200],
    }
    history: list = []
    if os.path.isfile(MCP_LOG):
        try:
            with open(MCP_LOG) as f:
                history = json.load(f)
        except Exception:
            pass
    history.append(entry)
    history = history[-500:]
    with open(MCP_LOG, 'w') as f:
        json.dump(history, f, indent=2)
    log.debug("MCP action logged: %s.%s", server, tool)
