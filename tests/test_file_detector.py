"""Tests for tools/file_detector.py"""

import os
import tempfile
import pytest

from techcoder_cli.tools.file_detector import detect_file_paths, is_action_prompt


def test_detect_existing_file(tmp_path):
    f = tmp_path / "lib" / "main.dart"
    f.parent.mkdir()
    f.write_text("")
    result = detect_file_paths("fix the bug in lib/main.dart", cwd=str(tmp_path))
    assert "lib/main.dart" in result


def test_detect_nonexistent_file_ignored(tmp_path):
    result = detect_file_paths("fix lib/ghost.dart", cwd=str(tmp_path))
    assert result == []


def test_is_action_prompt_fix():
    assert is_action_prompt("fix the bug in main.py") is True


def test_is_action_prompt_question():
    assert is_action_prompt("what does this function do?") is False


def test_is_action_prompt_add():
    assert is_action_prompt("add authentication to the app") is True


def test_is_action_prompt_explain():
    assert is_action_prompt("explain how the router works") is False
