<div align="center">

# 🤖 TechCoder CLI

**Local AI coding assistant powered by Gemma 4 + Ollama**

*Free. Offline. Private. No token limits.*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Ollama](https://img.shields.io/badge/Ollama-latest-black?style=flat-square&logo=ollama&logoColor=white)](https://ollama.com)
[![Gemma](https://img.shields.io/badge/Gemma-4-4285F4?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev/gemma)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

</div>

---

## 💡 Why TechCoder CLI?

| | TechCoder CLI | GitHub Copilot | ChatGPT |
|---|---|---|---|
| **Cost** | Free | $10/mo | $20/mo |
| **Internet required** | No | Yes | Yes |
| **Private** | 100% | No | No |
| **Token limit** | None | Limited | Limited |
| **Runs on your machine** | Yes | No | No |

> Your code never leaves your machine. No API keys. No subscriptions. No rate limits.

---

## ✨ Features

- 💬 **Chat with Gemma 4** — context-aware coding assistant, locally
- ⚡ **Streaming responses** — real-time output with loading spinner
- **`@filename` autocomplete** — type `@` to get file suggestions with Tab completion
- 🔍 **Smart file detection** — mention a file in your prompt, it gets auto-read
- 👁️ **Diff preview** — review changes before any file is written (y/n/s)
- 🤖 **Agentic workflow** — scans, reads, and edits files automatically
- 🧠 **Auto memory** — learns from each session, remembers your preferences
- 🔌 **MCP integration** — filesystem, GitHub, web search, SQLite
- 🏗️ **Auto stack detection** — detects Flutter, Python, React, Node, Go, Rust and more
- 🌍 **Global CLI** — run `techcoder` from any project folder
- 🔒 **100% offline & private** — zero data leaves your machine

---

## 📋 Requirements

- Python 3.10+
- [Ollama](https://ollama.com) installed
- Gemma 4 model pulled (`gemma4:e4b`)
- 8GB RAM minimum (16GB recommended)

---

## 🚀 Installation

### 1. Install Ollama
Download and install from [ollama.com](https://ollama.com)

### 2. Pull Gemma 4
```bash
ollama run gemma4:e4b
```

### 3. Clone this repo
```bash
git clone https://github.com/techcodercoder/techcoder-cli.git
cd techcoder-cli
```

### 4. Install pipx
```bash
brew install pipx
pipx ensurepath
```

### 5. Install techcoder-cli
```bash
pipx install -e .
```

### 6. Run from anywhere
```bash
cd /any/project/folder
techcoder
```

---

## 🖥️ Usage

### Startup
```
🤖 TechCoder CLI - Powered by Gemma 4
🔍 Detected stack: Flutter/Dart
🧠 Memory loaded — I remember you!
🔌 MCP Connected: filesystem, web_search
💡 Tip: type @ to autocomplete filenames  |  ↑↓ for history
```

### `@filename` autocomplete
Type `@` followed by any part of a filename — press **Tab** to see suggestions:
```
You: can you review @
> main.py
  lib/main.dart
  pubspec.yaml
  README.md

You: can you review @main.py and suggest improvements
📎 Reading: main.py
🤖 Gemma: Here's my review...
```

Mention multiple files in one prompt:
```
You: compare @lib/auth.dart and @lib/login_screen.dart
📎 Reading: lib/auth.dart, lib/login_screen.dart
🤖 Gemma: Here's the comparison...
```

### Smart file detection (natural language)
```
You: fix the bug in lib/main.dart
📎 Detected files: lib/main.dart
  📄 Reading lib/main.dart
🤖 Planning changes...

─────────────────────────────────────────────────────────
  [MODIFIED] lib/main.dart
─────────────────────────────────────────────────────────
--- a/lib/main.dart
+++ b/lib/main.dart
@@ -12,7 +12,7 @@
-  if (user = null) {
+  if (user == null) {

Apply changes? [y/n/s]  (y=all  n=cancel  s=select): y

🤖 Done!
  ✅ Modified: lib/main.dart
```

### Agentic workflow (no file needed)
```
You: add Google Sign In
🔍 No files mentioned. Scanning project...
🤖 Identifying relevant files...
  📄 Reading lib/main.dart
  📄 Reading pubspec.yaml
🤖 Planning changes...

3 files to change.
Apply changes? [y/n/s]  (y=all  n=cancel  s=select): y

🤖 Done!
  ✅ Created: lib/screens/login_screen.dart
  ✅ Modified: lib/main.dart
  ✅ Modified: pubspec.yaml
```

### Auto memory
```
# Session 1
You: I prefer type hints and FastAPI for Python projects
exit
🧠 Saving memory... ✅

# Session 2
techcoder
🧠 Memory loaded — I remember you!
# Gemma already knows your preferences
```

### MCP — push to GitHub
```
You: push my changes with message "feat: add login screen"
⚠️  MCP wants to run: github_push
   Allow? [y/N]: y
🔌 Using GitHub MCP...
✅ Pushed to github.com/techcodercoder/my-app
```

### MCP — web search
```
You: search for Flutter best practices 2025
🔌 Using Web Search MCP...
🤖 Gemma: Here are the top results...
```

---

## 🛠️ Commands

| Command | Description |
|---|---|
| `@filename` | Autocomplete + auto-read file into context |
| `/read <file> [file2 ...]` | Read one or more files |
| `/save <filepath>` | Save last response to a file |
| `/edit <filepath> "<instruction>"` | Edit a file directly with Gemma |
| `/implement "<feature>"` | Agentic: implement a feature across files |
| `/project` | Scan and analyze full project structure |
| `/ls` | List files in current directory |
| `/memory` | View saved memory |
| `/memory clear` | Reset memory |
| `/mcp` | Show MCP server status |
| `/mcp enable <server>` | Enable an MCP server |
| `/mcp disable <server>` | Disable an MCP server |
| `/clear` | Clear chat history |
| `exit` | Quit |

---

## 🧠 Auto Stack Detection

Automatically detects your tech stack on startup and adjusts Gemma's expertise:

| Marker file | Detected stack |
|---|---|
| `pubspec.yaml` | Flutter / Dart |
| `package.json` | Node.js / React / Vue |
| `requirements.txt` / `pyproject.toml` | Python |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `build.gradle` | Kotlin / Android |
| `pom.xml` | Java / Maven |
| `Gemfile` | Ruby / Rails |
| `composer.json` | PHP |

---

## 🔌 MCP Servers

Configure at `~/.techcoder/mcp_config.json`:

| Server | What it does | Default |
|---|---|---|
| `filesystem` | Read/write files outside current dir | ✅ Enabled |
| `web_search` | Search DuckDuckGo for docs & answers | ✅ Enabled |
| `github` | Stage, commit, push via git | ⭕ Disabled |
| `sqlite` | Query local SQLite databases | ⭕ Disabled |

---

## 📁 Project Structure

```
techcoder-cli/
├── pyproject.toml
├── requirements.txt
├── Makefile
├── .env.example
├── docs/
│   └── ARCHITECTURE.md
├── tests/
│   ├── test_file_handler.py
│   ├── test_file_detector.py
│   ├── test_memory.py
│   └── test_chat.py
└── techcoder_cli/
    ├── main.py           — CLI loop & command routing
    ├── autocomplete.py   — @filename autocomplete (prompt_toolkit)
    ├── config/
    │   ├── settings.py   — constants & paths
    │   └── prompts.py    — all LLM system prompts
    ├── core/
    │   ├── chat.py       — Ollama streaming + tool-calling loop
    │   ├── agent.py      — /edit, /implement, smart changes
    │   └── memory.py     — auto memory (load, save, summarise)
    ├── tools/
    │   ├── file_handler.py   — read, write, scan project
    │   ├── file_detector.py  — detect paths in natural language
    │   ├── differ.py         — diff preview & y/n/s confirm
    │   └── stack_detector.py — auto detect tech stack
    ├── mcp/
    │   ├── client.py     — MCPClient, /mcp commands
    │   ├── tools.py      — filesystem, github, web_search, sqlite
    │   └── config.py     — mcp_config.json loader
    └── utils/
        ├── logger.py     — colorized terminal + file logging
        └── helpers.py    — shared pure functions
```

---

## 🧪 Testing

```bash
# Install dependencies
pipx install -e . --force

# Run all tests
make test

# Run specific test file
pytest tests/test_file_handler.py -v
pytest tests/test_file_detector.py -v
pytest tests/test_memory.py -v

# Lint & format
make lint
make format
```

---

## 🗺️ Roadmap

- [x] Basic CLI chat
- [x] Streaming response with spinner
- [x] Smart file detection from natural language
- [x] Diff preview before file changes (y/n/s)
- [x] Agentic workflow (scan → read → edit → confirm)
- [x] Auto detect tech stack
- [x] Global CLI (`techcoder` from any folder)
- [x] Auto memory (learn from each session)
- [x] MCP integration (filesystem, GitHub, web search, SQLite)
- [x] Clean architecture (core / tools / mcp / config / utils)
- [x] `@filename` autocomplete with prompt_toolkit
- [x] Command history (↑↓ arrows)
- [x] Unit tests
- [ ] VS Code extension
- [ ] Web UI
- [ ] Multi-agent support

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a PR.
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the codebase structure.

---

## 📄 License

MIT License — use it however you like.

---

<div align="center">

Built with ❤️ by [@techcodercoder](https://github.com/techcodercoder)

*Local AI for developers who care about privacy.*

</div>
