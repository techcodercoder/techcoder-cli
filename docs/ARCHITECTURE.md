# TechCoder CLI — Architecture

## Overview

TechCoder CLI follows a **layered clean architecture**. Each layer has a
single responsibility and strict import rules — inner layers never import
from outer layers.

```
┌─────────────────────────────────────┐
│              main.py                │  ← Entry point & CLI loop
├───────────┬─────────────────────────┤
│   core/   │   mcp/   │   web/       │  ← Feature layers
├───────────┴──────────┴──────────────┤
│                tools/               │  ← File, diff, detection
├─────────────────────────────────────┤
│         config/   utils/            │  ← Foundation (no internal deps)
└─────────────────────────────────────┘
```

---

## Dependency Rules

| Layer      | May import from                         |
|------------|-----------------------------------------|
| `config/`  | stdlib only                             |
| `utils/`   | stdlib only                             |
| `tools/`   | `config/`, `utils/`, stdlib             |
| `core/`    | `config/`, `utils/`, `tools/`, stdlib   |
| `mcp/`     | `config/`, `utils/`, `tools/`, stdlib   |
| `web/`     | everything                              |
| `main.py`  | everything                              |

**Rule:** `core/` has **no** dependency on `mcp/` or `web/`.

---

## Module Responsibilities

### `config/`
- **`settings.py`** — all constants: `MODEL_NAME`, file paths, limits
- **`prompts.py`** — all LLM system prompts and `build_system_prompt()`
- **`__init__.py`** — re-exports for convenience

### `utils/`
- **`logger.py`** — colorized terminal + rotating file logger
- **`helpers.py`** — pure functions: `extract_fenced_code`, `parse_file_blocks`, `guess_lang`, etc.
- **`__init__.py`** — re-exports

### `tools/`
- **`file_handler.py`** — `read_file`, `write_file`, `scan_project`, `extract_code`
- **`file_detector.py`** — regex-based path detection + action intent heuristic
- **`differ.py`** — unified diff, colored output, y/n/s confirm prompt
- **`stack_detector.py`** — detect Flutter/React/Python/Go/Rust etc from marker files

### `core/`
- **`chat.py`** — Ollama streaming (`chat`) + tool-calling loop (`chat_with_tools`)
- **`agent.py`** — agentic workflows: `cmd_edit`, `cmd_implement`, `cmd_smart`, `apply_changes`
- **`memory.py`** — load/save/clear JSON memory, Gemma-powered session summariser

### `mcp/`
- **`config.py`** — load/save `~/.techcoder/mcp_config.json`, enable/disable servers
- **`tools.py`** — tool implementations: filesystem, GitHub, web search, SQLite
- **`client.py`** — `MCPClient`: tool schemas, dispatcher, `/mcp` commands, action log

### `web/`
- **`server.py`** — future Flask/FastAPI web UI *(placeholder)*

### `main.py`
- CLI loop only: reads input, routes to the right module, prints output
- No business logic — all logic lives in `core/`, `tools/`, `mcp/`

---

## Data Flow

### Plain chat
```
User input → main.py → core/chat.py → Ollama → stdout
```

### Smart file detection
```
User input
  → tools/file_detector.py   (detect paths + action intent)
  → core/agent.py            (read files, call LLM, get FILE blocks)
  → tools/differ.py          (show diff, y/n/s confirm)
  → tools/file_handler.py    (write files)
```

### MCP tool call
```
User input → main.py → core/chat.py (chat_with_tools)
  → Ollama returns tool_call
  → mcp/client.py (dispatch)
  → mcp/tools.py  (execute)
  → result fed back to Ollama
  → loop until final text response
```

### Auto memory (on exit)
```
Session messages
  → core/memory.py (summarise_and_save)
  → Ollama         (extract JSON)
  → ~/.techcoder/memory.json
```

---

## File Structure

```
techcoder-cli/
├── pyproject.toml        ← installable package, entry point
├── requirements.txt
├── Makefile              ← make run / test / lint / format
├── .env.example
├── README.md
├── docs/
│   ├── ARCHITECTURE.md   ← this file
│   ├── CONTRIBUTING.md
│   └── API.md
├── tests/
│   ├── test_file_handler.py
│   ├── test_file_detector.py
│   ├── test_memory.py
│   └── test_chat.py
└── techcoder_cli/
    ├── main.py
    ├── config/
    │   ├── settings.py
    │   └── prompts.py
    ├── utils/
    │   ├── logger.py
    │   └── helpers.py
    ├── tools/
    │   ├── file_handler.py
    │   ├── file_detector.py
    │   ├── differ.py
    │   └── stack_detector.py
    ├── core/
    │   ├── chat.py
    │   ├── agent.py
    │   └── memory.py
    ├── mcp/
    │   ├── config.py
    │   ├── tools.py
    │   └── client.py
    └── web/
        └── server.py
```
