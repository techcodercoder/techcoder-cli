.PHONY: run ui install test lint format clean

run:
	techcoder

ui:
	techcoder --ui

install:
	python3 -m venv venv
	venv/bin/pip install -e ".[dev]" --quiet
	pipx install -e . --force

test:
	venv/bin/pip install pytest --quiet
	venv/bin/pytest tests/ -v

lint:
	venv/bin/pip install ruff --quiet
	venv/bin/ruff check techcoder_cli/

format:
	venv/bin/pip install ruff --quiet
	venv/bin/ruff format techcoder_cli/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
