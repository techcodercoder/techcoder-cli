"""
Detect file paths mentioned in a user prompt, and decide whether
the prompt is a code-change action vs a plain question.
"""

import os
import re

# Known source/config extensions worth tracking
_KNOWN_EXTS = {
    'dart', 'py', 'ts', 'tsx', 'js', 'jsx', 'kt', 'swift',
    'go', 'rs', 'rb', 'java', 'c', 'cpp', 'h', 'hpp',
    'yaml', 'yml', 'toml', 'json', 'html', 'css', 'scss',
    'xml', 'gradle', 'md', 'sh', 'env',
}

# Matches:  lib/main.dart  |  src/auth/login.tsx  |  pubspec.yaml
_PATH_RE = re.compile(
    r'(?<![:/\\])'                          # not after URL-like prefix
    r'\b'
    r'('
    r'(?:[\w.-]+/)+[\w.-]+'               # path with at least one /
    r'|'
    r'[\w][\w.-]*\.(?:' + '|'.join(_KNOWN_EXTS) + r')'  # bare filename.ext
    r')'
    r'\b'
)

# Words that signal the user wants code to be written / changed
_ACTION_VERBS = {
    'fix', 'implement', 'add', 'update', 'refactor', 'create',
    'write', 'edit', 'remove', 'delete', 'modify', 'change',
    'build', 'make', 'generate', 'integrate', 'connect', 'migrate',
    'rename', 'move', 'replace', 'improve', 'optimize',
}

# Words that strongly signal a plain question — no file changes needed
_QUESTION_WORDS = {
    'what', 'why', 'how', 'when', 'where', 'which', 'who',
    'explain', 'describe', 'tell', 'show', 'list', 'compare',
    'difference', 'meaning', 'define',
}


def detect_file_paths(text: str, cwd: str = '.') -> list[str]:
    """
    Return file paths mentioned in `text` that actually exist under `cwd`.
    Paths are returned relative to `cwd`.
    """
    candidates = _PATH_RE.findall(text)
    found = []
    seen = set()
    for raw in candidates:
        path = raw.strip().rstrip('.,;:)')
        if path in seen:
            continue
        seen.add(path)
        full = os.path.join(cwd, path)
        if os.path.isfile(full):
            found.append(path)
    return found


def is_action_prompt(text: str) -> bool:
    """
    Return True if the prompt looks like a request to change code.

    Heuristic:
    - Contains an action verb (fix, implement, add …)
    - AND does not start with a question word
    - OR explicitly mentions a file path (always treat as action)
    """
    words = set(re.findall(r'\b\w+\b', text.lower()))

    # A bare question word at the start is a strong "no-action" signal
    first_word = text.strip().split()[0].lower().rstrip('?') if text.strip() else ''
    if first_word in _QUESTION_WORDS and not (words & _ACTION_VERBS):
        return False

    # Explicit file path mention → always treat as action
    if _PATH_RE.search(text):
        return True

    return bool(words & _ACTION_VERBS)
