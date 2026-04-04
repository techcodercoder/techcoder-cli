"""
File I/O and project scanning.
"""

import os

from ..config.settings import SCAN_IGNORE_DIRS


def read_file(filepath: str) -> str | None:
    """Return file contents, or None if not found."""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None
    except Exception as e:
        return f"Error reading file: {e}"


def read_files(filepaths: list[str]) -> tuple[str, list[str], list[str]]:
    """
    Read multiple files.
    Returns (combined_context, loaded_paths, failed_paths).
    """
    parts, loaded, failed = [], [], []
    for filepath in filepaths:
        content = read_file(filepath)
        if content is None:
            failed.append(filepath)
        else:
            loaded.append(filepath)
            parts.append(f"--- {filepath} ---\n{content}")
    return '\n\n'.join(parts), loaded, failed


def write_file(filepath: str, content: str) -> bool | str:
    """Write content to file. Returns True on success, error string on failure."""
    try:
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        return f"Error writing file: {e}"


def extract_code(response: str) -> str:
    """Extract the first fenced code block from a response."""
    lines = response.split('\n')
    code_lines, in_block = [], False
    for line in lines:
        if line.startswith('```'):
            in_block = not in_block
            continue
        if in_block:
            code_lines.append(line)
    return '\n'.join(code_lines)


def scan_project(path: str = '.') -> str:
    """Recursively scan a directory tree, skipping common noise dirs."""
    result = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [
            d for d in dirs
            if d not in SCAN_IGNORE_DIRS and not d.startswith('.')
        ]
        level   = os.path.relpath(root, path).count(os.sep)
        indent  = '  ' * level
        result.append(f"{indent}📁 {os.path.basename(root)}/")
        subindent = '  ' * (level + 1)
        for file in files:
            result.append(f"{subindent}📄 {file}")
    return '\n'.join(result)
