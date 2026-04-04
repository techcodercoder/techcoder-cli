"""
Shared helper functions with no dependencies on other techcoder_cli modules.
"""

import json
import os
import re


def extract_fenced_code(text: str, hint: str = '') -> str:
    """
    Return content of the first fenced code block whose language tag contains
    `hint` (case-insensitive). Falls back to the first block found, then to
    the full text if no block exists.
    """
    pattern = re.compile(r'```(\w*)\n(.*?)```', re.DOTALL)
    matches = pattern.findall(text)
    if not matches:
        return text.strip()
    if hint:
        for lang, body in matches:
            if hint.lower() in lang.lower():
                return body.strip()
    return matches[0][1].strip()


def parse_file_blocks(response: str) -> list[tuple[str, str]]:
    """
    Parse LLM response for blocks formatted as:

        ### FILE: relative/path/to/file
        ```lang
        ...code...
        ```

    Returns list of (filepath, code) tuples.
    """
    pattern = re.compile(r'###\s*FILE:\s*(.+?)\n```\w*\n(.*?)```', re.DOTALL)
    return [
        (m.group(1).strip(), m.group(2).strip())
        for m in pattern.finditer(response)
    ]


def extract_json(text: str) -> dict:
    """Parse JSON from an LLM response, stripping surrounding markdown fences."""
    text = text.strip()
    if text.startswith('```'):
        lines = text.splitlines()
        inner = lines[1:-1] if lines[-1].strip() == '```' else lines[1:]
        text = '\n'.join(inner)
    return json.loads(text)


def guess_lang(filepath: str) -> str:
    """Map a file extension to its language name for LLM prompts."""
    ext = os.path.splitext(filepath)[1].lstrip('.')
    return {
        'dart':  'dart',
        'py':    'python',
        'ts':    'typescript',
        'tsx':   'typescript',
        'js':    'javascript',
        'jsx':   'javascript',
        'kt':    'kotlin',
        'swift': 'swift',
        'go':    'go',
        'rs':    'rust',
        'rb':    'ruby',
        'java':  'java',
        'cpp':   'cpp',
        'c':     'c',
        'sh':    'bash',
        'yaml':  'yaml',
        'yml':   'yaml',
        'toml':  'toml',
        'json':  'json',
        'html':  'html',
        'css':   'css',
    }.get(ext, ext)


def ensure_dir(path: str):
    """Create directory (and parents) if it does not exist."""
    os.makedirs(path, exist_ok=True)
