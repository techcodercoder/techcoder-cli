"""
Detect file paths mentioned in a user prompt, and decide whether
the prompt is a code-change action vs a plain question.
"""

import os
import re

_KNOWN_EXTS = {
    'dart', 'py', 'ts', 'tsx', 'js', 'jsx', 'kt', 'swift',
    'go', 'rs', 'rb', 'java', 'c', 'cpp', 'h', 'hpp',
    'yaml', 'yml', 'toml', 'json', 'html', 'css', 'scss',
    'xml', 'gradle', 'md', 'sh', 'env',
}

_PATH_RE = re.compile(
    r'(?<![:/\\])'
    r'\b'
    r'('
    r'(?:[\w.-]+/)+[\w.-]+'
    r'|'
    r'[\w][\w.-]*\.(?:' + '|'.join(_KNOWN_EXTS) + r')'
    r')'
    r'\b'
)

_ACTION_VERBS = {
    'fix', 'implement', 'add', 'update', 'refactor', 'create',
    'write', 'edit', 'remove', 'delete', 'modify', 'change',
    'build', 'make', 'generate', 'integrate', 'connect', 'migrate',
    'rename', 'move', 'replace', 'improve', 'optimize',
}

_QUESTION_WORDS = {
    'what', 'why', 'how', 'when', 'where', 'which', 'who',
    'explain', 'describe', 'tell', 'show', 'list', 'compare',
    'difference', 'meaning', 'define',
}


def detect_file_paths(text: str, cwd: str = '.') -> list[str]:
    """Return file paths mentioned in text that actually exist under cwd."""
    candidates = _PATH_RE.findall(text)
    found, seen = [], set()
    for raw in candidates:
        path = raw.strip().rstrip('.,;:)')
        if path in seen:
            continue
        seen.add(path)
        if os.path.isfile(os.path.join(cwd, path)):
            found.append(path)
    return found


def is_action_prompt(text: str) -> bool:
    """Return True if the prompt looks like a request to change code."""
    words = set(re.findall(r'\b\w+\b', text.lower()))
    first = text.strip().split()[0].lower().rstrip('?') if text.strip() else ''
    if first in _QUESTION_WORDS and not (words & _ACTION_VERBS):
        return False
    if _PATH_RE.search(text):
        return True
    return bool(words & _ACTION_VERBS)
