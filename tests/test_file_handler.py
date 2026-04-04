"""Tests for tools/file_handler.py"""

import os
import tempfile
import pytest

from techcoder_cli.tools.file_handler import (
    read_file, write_file, extract_code, scan_project
)


def test_write_and_read_roundtrip():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        path = f.name
    try:
        assert write_file(path, "hello") is True
        assert read_file(path) == "hello"
    finally:
        os.unlink(path)


def test_read_missing_file_returns_none():
    assert read_file("/nonexistent/file.py") is None


def test_extract_code_from_fenced_block():
    response = "Sure!\n```python\nprint('hi')\n```\nDone."
    assert extract_code(response) == "print('hi')"


def test_extract_code_no_block_returns_empty():
    assert extract_code("Just some text") == ""


def test_scan_project_returns_string():
    with tempfile.TemporaryDirectory() as tmpdir:
        open(os.path.join(tmpdir, "main.py"), 'w').close()
        result = scan_project(tmpdir)
        assert "main.py" in result
