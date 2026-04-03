import os


def read_file(filepath):
    """Read file contents and return as string, or None if not found."""
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
    parts = []
    loaded = []
    failed = []

    for filepath in filepaths:
        content = read_file(filepath)
        if content is None:
            failed.append(filepath)
        else:
            loaded.append(filepath)
            parts.append(f"--- {filepath} ---\n{content}")

    combined = '\n\n'.join(parts)
    return combined, loaded, failed


def write_file(filepath, content):
    """Write content to file. Returns True on success, error string on failure."""
    try:
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        return f"Error writing file: {e}"


def extract_code(response):
    """Extract the first code block from a Gemma response."""
    lines = response.split('\n')
    code_lines = []
    in_code_block = False

    for line in lines:
        if line.startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            code_lines.append(line)

    return '\n'.join(code_lines)


def scan_project(path: str = '.') -> str:
    """Scan directory tree, skipping hidden dirs, venv, and __pycache__."""
    result = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not d.startswith('.')
                   and d not in ('venv', '__pycache__', 'node_modules', '.dart_tool', 'build')]
        level = os.path.relpath(root, path).count(os.sep)
        indent = '  ' * level
        result.append(f"{indent}📁 {os.path.basename(root)}/")
        subindent = '  ' * (level + 1)
        for file in files:
            result.append(f"{subindent}📄 {file}")
    return '\n'.join(result)
