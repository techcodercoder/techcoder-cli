"""
Agentic workflows: /edit, /implement, and smart natural-language changes.
"""

import os

import ollama

from ..config.settings import MODEL_NAME
from ..config.prompts import IMPLEMENT_SYSTEM, SMART_SYSTEM
from ..tools.file_handler import read_file, write_file, scan_project
from ..tools.file_detector import detect_file_paths
from ..utils.helpers import extract_fenced_code, parse_file_blocks, guess_lang
from ..utils.logger import get_logger

log = get_logger(__name__)


def _llm(messages: list[dict]) -> str:
    response = ollama.chat(model=MODEL_NAME, messages=messages)
    return response['message']['content']


# ── /edit ─────────────────────────────────────────────────────────────────────

def cmd_edit(filepath: str, instruction: str) -> str:
    """Read filepath, ask Gemma to apply instruction, write result back."""
    print(f"📖 Reading {filepath}...")
    current = read_file(filepath) or ''
    if not current:
        print("  (file not found — will create)")

    lang   = guess_lang(filepath)
    prompt = (
        f"You are editing `{filepath}`.\n\n"
        f"Current content:\n```{lang}\n{current}\n```\n\n"
        f"Instruction: {instruction}\n\n"
        f"Return ONLY the complete updated file in a single ```{lang} ... ``` block."
    )
    print("🤖 Thinking...")
    response    = _llm([{'role': 'user', 'content': prompt}])
    new_content = extract_fenced_code(response, hint=lang)

    result = write_file(filepath, new_content)
    if result is True:
        log.info("Edited: %s", filepath)
        return f"✅ Edited and saved: {filepath}"
    return f"❌ {result}"


# ── /implement ────────────────────────────────────────────────────────────────

def cmd_implement(feature: str, cwd: str = '.') -> list[str]:
    """
    Full agentic implementation:
    scan → identify files → read → implement → write all changed files.
    Returns list of status strings.
    """
    print("🔍 Scanning project structure...")
    structure = scan_project(cwd)

    print("🤖 Identifying relevant files...")
    identify_resp = _llm([{'role': 'user', 'content': (
        f"Project structure:\n{structure}\n\n"
        f"Feature: {feature}\n\n"
        "List the relative file paths most relevant to this feature "
        "(context files + files to create/modify). One path per line, no bullets."
    )}])

    candidate_paths = [
        line.strip().lstrip('- ')
        for line in identify_resp.splitlines()
        if line.strip() and not line.strip().startswith('#')
    ]

    context_parts = []
    for path in candidate_paths:
        content = read_file(os.path.join(cwd, path))
        if content is not None:
            print(f"  📄 Reading {path}")
            context_parts.append(f"--- {path} ---\n{content}")

    context = '\n\n'.join(context_parts) or '(no existing files read)'

    print(f"🤖 Implementing: {feature}...")
    response = _llm([
        {'role': 'system', 'content': IMPLEMENT_SYSTEM},
        {'role': 'user',   'content': (
            f"Project structure:\n{structure}\n\n"
            f"Existing files:\n{context}\n\n"
            f"Feature: {feature}\n\n"
            "Implement this feature completely using the ### FILE: format."
        )},
    ])

    file_blocks = parse_file_blocks(response)
    if not file_blocks:
        debug_path = os.path.join(cwd, '.techcoder_last.txt')
        write_file(debug_path, response)
        return [f"❌ No FILE blocks returned. Raw output → {debug_path}"]

    statuses = []
    for rel_path, code in file_blocks:
        full_path = os.path.join(cwd, rel_path)
        action    = 'Modified' if os.path.exists(full_path) else 'Created'
        result    = write_file(full_path, code)
        if result is True:
            log.info("%s: %s", action, rel_path)
            statuses.append(f"  ✅ {action}: {rel_path}")
        else:
            statuses.append(f"  ❌ {rel_path}: {result}")
    return statuses


# ── Smart natural-language change ─────────────────────────────────────────────

def cmd_smart(
    prompt: str,
    cwd: str = '.',
    explicit_paths: list[str] | None = None,
) -> list[tuple[str, str, str]]:
    """
    Natural-language → (filepath, old, new) triples. Does NOT write files.
    Caller shows diff and confirms before calling apply_changes().
    """
    paths = explicit_paths or detect_file_paths(prompt, cwd)

    if not paths:
        print("🔍 No files mentioned. Scanning project...")
        structure   = scan_project(cwd)
        identify_resp = _llm([{'role': 'user', 'content': (
            f"Project structure:\n{structure}\n\n"
            f"Request: {prompt}\n\n"
            "List ONLY the relative file paths most relevant to this request. "
            "One path per line, no bullets."
        )}])
        paths = [
            line.strip().lstrip('- ')
            for line in identify_resp.splitlines()
            if line.strip() and '.' in line.strip()
        ]

    context_parts: list[str] = []
    original: dict[str, str] = {}

    for rel in paths:
        content = read_file(os.path.join(cwd, rel))
        if content is not None:
            print(f"  📄 Reading {rel}")
            original[rel] = content
            context_parts.append(f"--- {rel} ---\n{content}")
        else:
            original[rel] = ''

    context = '\n\n'.join(context_parts) or '(no existing files read)'

    print("🤖 Planning changes...")
    response = _llm([
        {'role': 'system', 'content': SMART_SYSTEM},
        {'role': 'user',   'content': f"Files:\n{context}\n\nRequest: {prompt}"},
    ])

    changes: list[tuple[str, str, str]] = []
    for rel_path, new_code in parse_file_blocks(response):
        old_code = original.get(rel_path, '')
        if old_code != new_code:
            changes.append((rel_path, old_code, new_code))
    return changes


def apply_changes(changes: list[tuple[str, str, str]], cwd: str = '.') -> list[str]:
    """Write confirmed changes to disk. Returns status lines."""
    statuses = []
    for rel_path, old, new in changes:
        full   = os.path.join(cwd, rel_path)
        action = 'Created' if old == '' else 'Modified'
        result = write_file(full, new)
        if result is True:
            log.info("%s: %s", action, rel_path)
            statuses.append(f"  ✅ {action}: {rel_path}")
        else:
            statuses.append(f"  ❌ {rel_path}: {result}")
    return statuses
