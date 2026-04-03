# 🤖 TechCoder CLI

> Local AI coding assistant powered by Gemma 4.
> Run AI on your machine — offline, free, and 100% private.

## ✨ Features
- 💬 Chat with AI locally
- 💻 Generate & debug code offline
- 🔒 100% private, no data leaves your machine
- ⚡ Powered by Gemma 4 + Ollama
- 🌍 Works on Mac, Windows & Linux

## 📋 Requirements
- Python 3.x
- [Ollama](https://ollama.com)
- 8GB+ RAM recommended

## 🚀 Installation

### 1. Install Ollama
Download at [ollama.com](https://ollama.com) and install

### 2. Download Gemma 4
```bash
ollama run gemma4:e4b
```

### 3. Clone this repo
```bash
git clone https://github.com/techcodercoder/techcoder-cli.git
cd techcoder-cli
```

### 4. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### 5. Install dependencies
```bash
pip install ollama
```

### 6. Run it!
```bash
python3 main.py
```

## 💬 Usage
```
🤖 TechCoder CLI - Powered by Gemma 4
Type 'exit' to quit

You: write a function to reverse a string in python
🤖 Gemma: Thinking...
🤖 Gemma: [response here]
```

## 🗺️ Roadmap
- [x] Basic CLI chat
- [x] Code generation
- [ ] Read & edit files
- [ ] MCP integration
- [ ] VS Code extension

## 🤝 Contributing
Contributions are welcome! Feel free to open an issue or submit a PR.

## 📄 License
MIT License

## 👨‍💻 Author
Built with ❤️ by [@techcodercoder](https://github.com/techcodercoder)