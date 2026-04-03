"""
Agentic commands:
  /edit <filepath> "<instruction>"   — read file, apply instruction, write back
  /implement "<feature>"             — scan project, read relevant files, write changes
  cmd_smart()                        — natural-language smart detection + diff + confirm
"""

import os
import re

import ollama

from config import MODEL
from file_handler import read_file, write_file, extract_code, scan_project
from file_detector import detect_file_paths


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _llm(messages: list[dict]) -> str:
    """Call Ollama and return the full response text."""
    response = ollama.chat(model=MODEL, messages=messages)
    return response['message']['content']


def _extract_fenced(text: str, hint: str = '') -> str:
    """
    Return content of the first fenced code block whose language tag
    contains `hint` (case-insensitive). Falls back to first block found.
    Falls back to the full text if no block exists.
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


def _guess_lang(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lstrip('.')
    return {'dart': 'dart', 'py': 'python', 'ts': 'typescript',
            'tsx': 'typescript', 'js': 'javascript', 'jsx': 'javascript',
            'kt': 'kotlin', 'swift': 'swift', 'go': 'go',
            'rs': 'rust', 'rb': 'ruby'}.get(ext, ext)


def _parse_file_blocks(response: str) -> list[tuple[str, str]]:
    """
    Parse Gemma's response for blocks like:

    ### FILE: lib/screens/login_screen.dart
    ```dart
    ...code...
    ```

    Returns list of (filepath, code) tuples.
    """
    results = []
    # Match ### FILE: <path> followed by a fenced code block
    pattern = re.compile(
        r'###\s*FILE:\s*(.+?)\n```\w*\n(.*?)```',
        re.DOTALL
    )
    for match in pattern.finditer(response):
        filepath = match.group(1).strip()
        code = match.group(2).strip()
        results.append((filepath, code))
    return results


# ---------------------------------------------------------------------------
# /edit command
# ---------------------------------------------------------------------------

def cmd_edit(filepath: str, instruction: str) -> str:
    """
    Read `filepath`, ask Gemma to apply `instruction`, write result back.
    Returns a status message.
    """
    print(f"📖 Reading {filepath}...")
    current = read_file(filepath)
    if current is None:
        # File doesn't exist yet — create from scratch
        current = ''
        print(f"  (file not found — will create)")

    lang = _guess_lang(filepath)
    prompt = (
        f"You are editing the file `{filepath}`.\n\n"
        f"Current content:\n```{lang}\n{current}\n```\n\n"
        f"Instruction: {instruction}\n\n"
        f"Return ONLY the complete updated file content inside a single "
        f"```{lang} ... ``` code block. No explanations outside the block."
    )

    print("🤖 Thinking...")
    response = _llm([{'role': 'user', 'content': prompt}])
    new_content = _extract_fenced(response, hint=lang)

    result = write_file(filepath, new_content)
    if result is True:
        return f"✅ Edited and saved: {filepath}"
    return f"❌ {result}"


# ---------------------------------------------------------------------------
# /implement command
# ---------------------------------------------------------------------------

_IMPLEMENT_SYSTEM = """You are an agentic coding assistant. When asked to implement a feature:
1. Identify which files need to be created or modified.
2. Output each file using this exact format:

### FILE: <relative/path/to/file>
```<language>
<complete file content>
```

Output ALL files that need to change. Do not truncate file contents.
Do not add commentary between file blocks — put any notes AFTER all FILE blocks.
"""


def cmd_implement(feature: str, cwd: str = '.') -> list[str]:
    """
    Agentic implementation:
      1. Scan project structure
      2. Ask Gemma which files are relevant
      3. Read those files
      4. Ask Gemma to implement the feature
      5. Parse and write all modified/created files
    Returns list of status messages.
    """
    print("🔍 Scanning project structure...")
    structure = scan_project(cwd)

    # Step 1: identify relevant files
    print("🤖 Identifying relevant files...")
    identify_prompt = (
        f"Project structure:\n{structure}\n\n"
        f"Feature to implement: {feature}\n\n"
        f"List the relative file paths that are most relevant to this feature "
        f"(files to read for context AND files to create/modify). "
        f"Output ONLY a plain list, one path per line, no bullets or numbering."
    )
    file_list_response = _llm([{'role': 'user', 'content': identify_prompt}])

    # Parse paths from response
    candidate_paths = [
        line.strip().lstrip('- ').strip()
        for line in file_list_response.splitlines()
        if line.strip() and not line.strip().startswith('#')
    ]

    # Read files that actually exist (context files)
    context_parts = []
    for path in candidate_paths:
        full = os.path.join(cwd, path)
        content = read_file(full)
        if content is not None:
            print(f"  📄 Reading {path}")
            context_parts.append(f"--- {path} ---\n{content}")

    context = '\n\n'.join(context_parts) if context_parts else '(no existing files read)'

    # Step 2: implement
    print(f"🤖 Implementing: {feature}...")
    implement_prompt = (
        f"Project structure:\n{structure}\n\n"
        f"Existing file contents:\n{context}\n\n"
        f"Feature to implement: {feature}\n\n"
        f"Implement this feature completely. Use the ### FILE: format for every file."
    )
    response = _llm([
        {'role': 'system', 'content': _IMPLEMENT_SYSTEM},
        {'role': 'user', 'content': implement_prompt},
    ])

    # Step 3: parse and write files
    file_blocks = _parse_file_blocks(response)
    if not file_blocks:
        return ["❌ Gemma did not return any FILE blocks. Raw response saved to .techcoder_last.txt",
                _save_debug(response, cwd)]

    statuses = []
    for rel_path, code in file_blocks:
        full_path = os.path.join(cwd, rel_path)
        action = 'Modified' if os.path.exists(full_path) else 'Created'
        result = write_file(full_path, code)
        if result is True:
            statuses.append(f"  ✅ {action}: {rel_path}")
        else:
            statuses.append(f"  ❌ {rel_path}: {result}")

    return statuses


def _save_debug(content: str, cwd: str) -> str:
    path = os.path.join(cwd, '.techcoder_last.txt')
    write_file(path, content)
    return f"  (debug output → {path})"


# ---------------------------------------------------------------------------
# Smart detection (natural language → diff → confirm)
# ---------------------------------------------------------------------------

_SMART_SYSTEM = """You are an agentic coding assistant. The user wrote a natural-language request.
Implement exactly what was asked. For EVERY file that must be created or modified, output it using:

### FILE: <relative/path/to/file>
```<language>
<complete file content — never truncate>
```

Put ALL files first. Any brief explanation goes AFTER the last FILE block.
"""


def cmd_smart(
    prompt: str,
    cwd: str = '.',
    explicit_paths: list[str] | None = None,
) -> list[tuple[str, str, str]]:
    """
    Natural-language smart workflow:
      1. Use explicit_paths if provided, else detect paths from prompt
      2. If still no paths → scan project, ask Gemma which files are relevant
      3. Read all found files as context
      4. Ask Gemma to implement the change
      5. Return list of (filepath, old_content, new_content) — NOT written yet

    The caller is responsible for showing diffs and confirming before writing.
    """
    # Step 1: resolve which files to use as context
    paths = explicit_paths or detect_file_paths(prompt, cwd)

    if not paths:
        # No file mentioned — scan project and let Gemma identify relevant ones
        print("🔍 No files mentioned. Scanning project...")
        structure = scan_project(cwd)
        identify_resp = _llm([{
            'role': 'user',
            'content': (
                f"Project structure:\n{structure}\n\n"
                f"User request: {prompt}\n\n"
                f"List ONLY the relative file paths most relevant to this request "
                f"(context files + files to modify/create). One path per line, no bullets."
            ),
        }])
        paths = [
            line.strip().lstrip('- ').strip()
            for line in identify_resp.splitlines()
            if line.strip() and '.' in line.strip()
        ]

    # Step 2: read existing content for context
    context_parts = []
    original: dict[str, str] = {}   # path → original content ('' if new)
    for rel in paths:
        full = os.path.join(cwd, rel)
        content = read_file(full)
        if content is not None:
            print(f"  📄 Reading {rel}")
            original[rel] = content
            context_parts.append(f"--- {rel} ---\n{content}")
        else:
            original[rel] = ''   # will be created

    context = '\n\n'.join(context_parts) if context_parts else '(no existing files read)'

    # Step 3: ask Gemma to implement
    print("🤖 Planning changes...")
    response = _llm([
        {'role': 'system', 'content': _SMART_SYSTEM},
        {'role': 'user', 'content': (
            f"Existing file contents:\n{context}\n\n"
            f"Request: {prompt}"
        )},
    ])

    # Step 4: parse FILE blocks
    file_blocks = _parse_file_blocks(response)
    if not file_blocks:
        # Gemma replied without FILE blocks — surface the raw response
        return []

    # Step 5: build (filepath, old, new) triples
    changes: list[tuple[str, str, str]] = []
    for rel_path, new_code in file_blocks:
        old_code = original.get(rel_path, '')
        if old_code != new_code:          # skip truly unchanged files
            changes.append((rel_path, old_code, new_code))

    return changes


def apply_changes(changes: list[tuple[str, str, str]], cwd: str = '.') -> list[str]:
    """Write confirmed changes to disk. Returns status lines."""
    statuses = []
    for rel_path, old, new in changes:
        full = os.path.join(cwd, rel_path)
        action = 'Created' if old == '' else 'Modified'
        result = write_file(full, new)
        if result is True:
            statuses.append(f"  ✅ {action}: {rel_path}")
        else:
            statuses.append(f"  ❌ {rel_path}: {result}")
    return statuses
