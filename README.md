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
- 🔍 **Smart file detection** — mention a file in your prompt, it gets auto-read
- 👁️ **Diff preview** — review changes before any file is written
- 🤖 **Agentic workflow** — scans, reads, and edits files automatically
- 🧠 **Auto stack detection** — detects Flutter, Python, React, Node, Go, Rust and more
- 🌍 **Global CLI** — run `techcoder` from any project folder
- 🔒 **100% offline & private** — zero data leaves your machine

---

## 📋 Requirements

- Python 3.10+
- [Ollama](https://ollama.com) installed
- Gemma 4 model pulled (`gemma4:e4b`)
- 8GB RAM minimum (16GB recommended for best performance)

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

### 4. Install as global CLI
```bash
pip install -e .
```

### 5. Run from anywhere
```bash
cd /any/project/folder
techcoder
```

---

## 🖥️ Usage

### Basic chat
```
🤖 TechCoder CLI - Powered by Gemma 4
🔍 Detected stack: Flutter/Dart

You: write a function to reverse a string in python
🤖 Gemma: ⠙ Thinking...
🤖 Gemma: Here's a clean implementation...
```

### Smart file detection
Mention a file path naturally — TechCoder reads it automatically:
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

### Multi-file changes
```
You: implement login in lib/screens/login_screen.dart and update lib/main.dart
📎 Detected files: lib/screens/login_screen.dart, lib/main.dart
  📄 Reading lib/screens/login_screen.dart
  📄 Reading lib/main.dart
🤖 Planning changes...

2 files to change.
Apply changes? [y/n/s]  (y=all  n=cancel  s=select): s

File 1/2
  [MODIFIED] lib/screens/login_screen.dart
Apply lib/screens/login_screen.dart? [y/N]: y

File 2/2
  [MODIFIED] lib/main.dart
Apply lib/main.dart? [y/N]: n
  ↩ Skipped
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

---

## 🛠️ Commands

| Command | Description |
|---|---|
| `/read <filepath>` | Read a file and send it as context |
| `/read <file1> <file2>` | Read multiple files at once |
| `/save <filepath>` | Save last response to a file |
| `/edit <filepath> "<instruction>"` | Edit a file directly with Gemma |
| `/implement "<feature>"` | Agentic: implement a feature across files |
| `/project` | Scan and analyze full project structure |
| `/ls` | List files in current directory |
| `/clear` | Clear chat history |
| `exit` | Quit |

---

## 🧠 Auto Stack Detection

TechCoder CLI automatically detects your tech stack on startup and adjusts its expertise accordingly:

| Marker file | Detected stack |
|---|---|
| `pubspec.yaml` | Flutter / Dart |
| `package.json` | Node.js / React / Vue |
| `requirements.txt` / `pyproject.toml` | Python |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `build.gradle` | Kotlin / Android |
| `pom.xml` | Java / Maven |

---

## 📁 Project Structure

```
techcoder-cli/
├── pyproject.toml        — global CLI entry point
├── requirements.txt
└── techcoder_cli/
    ├── main.py           — CLI loop & command routing
    ├── chat.py           — Ollama streaming + spinner
    ├── config.py         — model settings & system prompt
    ├── agent.py          — agentic workflow (smart, edit, implement)
    ├── differ.py         — diff preview & confirm (y/n/s)
    ├── file_detector.py  — detect file paths in natural language
    ├── file_handler.py   — read, write, scan project
    └── stack_detector.py — auto detect tech stack
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
- [ ] Auto memory (learn from each session)
- [ ] MCP integration
- [ ] VS Code extension
- [ ] Web UI
- [ ] Multi-agent support

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a PR.

---

## 📄 License

MIT License — use it however you like.

---

<div align="center">

Built with ❤️ by [@techcodercoder](https://github.com/techcodercoder)

*Local AI for developers who care about privacy.*

</div>
