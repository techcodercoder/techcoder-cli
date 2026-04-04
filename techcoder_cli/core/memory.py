"""
Auto memory — persist user preferences and project context across sessions.
Storage: ~/.techcoder/memory.json
"""

import json
import os
from datetime import date

import ollama

from ..config.settings import MODEL_NAME, MEMORY_FILE, MEMORY_DIR, MAX_MEMORY_LEARNED
from ..config.prompts import MEMORY_SUMMARISE_PROMPT
from ..utils.helpers import extract_json
from ..utils.logger import get_logger

log = get_logger(__name__)

_EMPTY: dict = {
    'user_preferences': {'languages': [], 'style': '', 'frameworks': []},
    'projects':         [],
    'learned_context':  [],
    'session_count':    0,
    'last_updated':     '',
}


# ── I/O ───────────────────────────────────────────────────────────────────────

def load_memory() -> dict | None:
    """Return memory dict if file exists and is valid, else None."""
    if not os.path.isfile(MEMORY_FILE):
        return None
    try:
        with open(MEMORY_FILE) as f:
            data = json.load(f)
        return data if 'session_count' in data else None
    except (json.JSONDecodeError, OSError):
        return None


def save_memory(memory: dict):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    memory['last_updated'] = str(date.today())
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)
    log.debug("Memory saved (%d learned items)", len(memory.get('learned_context', [])))


def clear_memory():
    if os.path.isfile(MEMORY_FILE):
        os.remove(MEMORY_FILE)
        log.info("Memory cleared")


# ── Prompt injection ──────────────────────────────────────────────────────────

def memory_to_prompt(memory: dict) -> str:
    """Convert memory to a compact string for injection into the system prompt."""
    parts = []
    prefs = memory.get('user_preferences', {})
    if prefs.get('languages'):
        parts.append(f"Preferred languages: {', '.join(prefs['languages'])}")
    if prefs.get('frameworks'):
        parts.append(f"Preferred frameworks: {', '.join(prefs['frameworks'])}")
    if prefs.get('style'):
        parts.append(f"Coding style: {prefs['style']}")
    projects = memory.get('projects', [])
    if projects:
        names = ', '.join(p.get('name', '?') for p in projects[-3:])
        parts.append(f"Recent projects: {names}")
    for item in memory.get('learned_context', [])[-5:]:
        parts.append(f"  - {item}")
    parts.append(f"This is session #{memory.get('session_count', 0) + 1} together.")
    return '\n'.join(parts)


# ── Display ───────────────────────────────────────────────────────────────────

def print_memory(memory: dict):
    print("\n🧠 TechCoder Memory\n" + "─" * 40)
    prefs = memory.get('user_preferences', {})
    print(f"Languages  : {', '.join(prefs.get('languages', [])) or '—'}")
    print(f"Frameworks : {', '.join(prefs.get('frameworks', [])) or '—'}")
    print(f"Style      : {prefs.get('style') or '—'}")
    projects = memory.get('projects', [])
    if projects:
        print("\nProjects:")
        for p in projects[-5:]:
            print(f"  • {p.get('name', '?')}  [{p.get('stack', '')}]  {p.get('last_seen', '')}")
    learned = memory.get('learned_context', [])
    if learned:
        print("\nLearned context:")
        for item in learned:
            print(f"  • {item}")
    print(f"\nSessions   : {memory.get('session_count', 0)}")
    print(f"Updated    : {memory.get('last_updated', '—')}")
    print()


# ── Session summarise ─────────────────────────────────────────────────────────

def summarise_and_save(messages: list[dict], stack: str, cwd: str, existing: dict | None):
    """
    Ask Gemma to summarise the session, merge into existing memory, save.
    Silently skips if fewer than 2 user turns.
    """
    user_turns = [m for m in messages if m['role'] == 'user']
    if len(user_turns) < 2:
        return

    recent = messages[-30:]
    conversation = '\n'.join(
        f"{m['role'].upper()}: {m['content'][:300]}"
        for m in recent if m['role'] in ('user', 'assistant')
    )

    print("🧠 Saving memory...", end='', flush=True)
    try:
        resp = ollama.chat(
            model=MODEL_NAME,
            messages=[{'role': 'user', 'content': MEMORY_SUMMARISE_PROMPT.format(conversation=conversation)}],
        )
        extracted = extract_json(resp['message']['content'])
    except Exception as exc:
        log.warning("Memory summarise failed: %s", exc)
        print(" (skipped)")
        return

    memory = json.loads(json.dumps(existing)) if existing else json.loads(json.dumps(_EMPTY))

    prefs = memory.setdefault('user_preferences', {})
    for key in ('languages', 'frameworks'):
        existing_list = prefs.get(key, [])
        prefs[key] = existing_list + [x for x in extracted.get(key, []) if x not in existing_list]
    if extracted.get('style'):
        prefs['style'] = extracted['style']

    proj_name  = extracted.get('project_name', '').strip()
    proj_stack = extracted.get('project_stack', stack).strip()
    if proj_name:
        projects = memory.setdefault('projects', [])
        for p in projects:
            if p.get('name') == proj_name:
                p.update({'stack': proj_stack, 'last_seen': str(date.today())})
                break
        else:
            projects.append({'name': proj_name, 'stack': proj_stack, 'last_seen': str(date.today())})

    learned = memory.setdefault('learned_context', [])
    for item in extracted.get('learned', []):
        if item and item not in learned:
            learned.append(item)
    memory['learned_context'] = learned[-MAX_MEMORY_LEARNED:]
    memory['session_count']   = memory.get('session_count', 0) + 1

    save_memory(memory)
    print(" ✅")
