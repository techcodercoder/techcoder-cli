"""Tests for core/memory.py (I/O only — no Ollama calls)"""

import json
import os
import pytest

from techcoder_cli.core.memory import load_memory, save_memory, clear_memory, memory_to_prompt


@pytest.fixture(autouse=True)
def _temp_memory_file(tmp_path, monkeypatch):
    """Redirect MEMORY_FILE and MEMORY_DIR to a temp location."""
    import techcoder_cli.core.memory as mem_module
    import techcoder_cli.config.settings as settings

    tmp_file = str(tmp_path / "memory.json")
    monkeypatch.setattr(settings, "MEMORY_FILE", tmp_file)
    monkeypatch.setattr(settings, "MEMORY_DIR",  str(tmp_path))
    monkeypatch.setattr(mem_module, "MEMORY_FILE", tmp_file)
    monkeypatch.setattr(mem_module, "MEMORY_DIR",  str(tmp_path))
    yield


def _sample():
    return {
        'user_preferences': {'languages': ['Python'], 'style': 'clean', 'frameworks': ['FastAPI']},
        'projects':         [{'name': 'myapp', 'stack': 'Python', 'last_seen': '2026-04-05'}],
        'learned_context':  ['User prefers type hints'],
        'session_count':    3,
        'last_updated':     '2026-04-05',
    }


def test_save_and_load_roundtrip():
    save_memory(_sample())
    loaded = load_memory()
    assert loaded is not None
    assert loaded['session_count'] == 3
    assert 'Python' in loaded['user_preferences']['languages']


def test_load_missing_returns_none():
    assert load_memory() is None


def test_clear_removes_file(tmp_path, monkeypatch):
    import techcoder_cli.core.memory as mem_module
    import techcoder_cli.config.settings as settings
    tmp_file = str(tmp_path / "memory.json")
    monkeypatch.setattr(settings, "MEMORY_FILE", tmp_file)
    monkeypatch.setattr(mem_module, "MEMORY_FILE", tmp_file)

    save_memory(_sample())
    assert os.path.isfile(tmp_file)
    clear_memory()
    assert not os.path.isfile(tmp_file)


def test_memory_to_prompt_contains_key_info():
    prompt = memory_to_prompt(_sample())
    assert 'Python' in prompt
    assert 'FastAPI' in prompt
    assert 'myapp' in prompt
