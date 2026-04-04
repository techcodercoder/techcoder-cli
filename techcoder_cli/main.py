"""
TechCoder CLI — entry point.
All business logic lives in core/, tools/, mcp/, config/, utils/.
"""

import os
import shlex

from .config import build_system_prompt
from .core import (
    chat, chat_with_tools,
    cmd_edit, cmd_implement, cmd_smart, apply_changes,
    load_memory, clear_memory, memory_to_prompt, print_memory, summarise_and_save,
)
from .tools import (
    read_file, read_files, write_file, extract_code, scan_project,
    detect_file_paths, is_action_prompt,
    show_and_confirm,
    detect_stack,
)
from .mcp import MCPClient
from .utils import get_logger
from .autocomplete import (
    make_prompt_session, get_input, extract_at_mentions, strip_at_mentions,
    PROMPT_TOOLKIT_AVAILABLE,
)

log = get_logger(__name__)


def _print_help():
    print("""Commands:
  /ls                              List files in current directory
  /project                         Scan & analyze full project structure
  /read <file> [file2 ...]         Read one or more files
  /save <filepath>                 Save last response to file
  /edit <filepath> "<instruction>" Edit a file directly with Gemma
  /implement "<feature>"           Agentic: implement a feature across files
  /memory                          View saved memory
  /memory clear                    Reset memory
  /mcp                             Show MCP server status
  /mcp enable <server>             Enable an MCP server
  /mcp disable <server>            Disable an MCP server
  /clear                           Clear chat history
  exit                             Quit
""")


def main():
    cwd = os.getcwd()

    stack, stack_prompt = detect_stack(cwd)
    memory              = load_memory()
    mcp                 = MCPClient(cwd=cwd)

    print("🤖 TechCoder CLI - Powered by Gemma 4")
    print("Your personal coding assistant.")
    if stack:
        print(f"🔍 Detected stack: {stack}")
    print("🧠 Memory loaded — I remember you!" if memory else "No previous memory found. Starting fresh!")
    if mcp.enabled_servers:
        print(f"🔌 MCP Connected: {', '.join(mcp.enabled_servers)}")
    if PROMPT_TOOLKIT_AVAILABLE:
        print("💡 Tip: type @ to autocomplete filenames  |  ↑↓ for history")
    _print_help()

    session, completer = make_prompt_session(cwd)

    system_prompt = build_system_prompt(stack_prompt, memory_to_prompt(memory) if memory else '')
    messages      = [{'role': 'system', 'content': system_prompt}]
    last_response = ''

    while True:
        # Refresh file list for autocomplete each turn
        if completer is not None:
            completer.refresh()

        try:
            user_input = get_input("You: ", session).strip()
        except (EOFError, KeyboardInterrupt):
            summarise_and_save(messages[1:], stack, cwd, memory)
            print("\nBye! Happy coding! 👋")
            break

        if not user_input:
            continue

        # ── @filename mention → auto-read files ───────────────────────────────
        at_files = extract_at_mentions(user_input, cwd)
        if at_files:
            combined, loaded, failed = read_files(at_files)
            if failed:
                print(f"⚠️  Not found: {', '.join(failed)}")
            if loaded:
                print(f"📎 Reading: {', '.join(loaded)}")
                clean_prompt = strip_at_mentions(user_input)
                user_input = (
                    f"{clean_prompt}\n\n"
                    + '\n\n'.join(f"--- {p} ---\n{c}" for p, c in zip(loaded, combined.split('\n\n')))
                ) if clean_prompt else combined

        # ── Exit ──────────────────────────────────────────────────────────────
        if user_input.lower() == 'exit':
            summarise_and_save(messages[1:], stack, cwd, memory)
            print("Bye! Happy coding! 👋")
            break

        # ── /memory ───────────────────────────────────────────────────────────
        if user_input.lower() == '/memory clear':
            clear_memory()
            memory = None
            print("🧠 Memory cleared!\n")
            continue

        if user_input.lower() == '/memory':
            print_memory(memory) if memory else print("🧠 No memory yet.\n")
            continue

        # ── /mcp ─────────────────────────────────────────────────────────────
        if user_input.lower() == '/mcp':
            mcp.print_status()
            continue

        if user_input.lower().startswith('/mcp enable '):
            print(mcp.cmd_enable(user_input.split(None, 2)[2].strip()) + '\n')
            continue

        if user_input.lower().startswith('/mcp disable '):
            print(mcp.cmd_disable(user_input.split(None, 2)[2].strip()) + '\n')
            continue

        # ── /clear ────────────────────────────────────────────────────────────
        if user_input.lower() == '/clear':
            messages = [{'role': 'system', 'content': system_prompt}]
            print("✅ Chat history cleared!\n")
            continue

        # ── /ls ───────────────────────────────────────────────────────────────
        if user_input.lower() == '/ls':
            file_list = '\n'.join(sorted(os.listdir('.')))
            print(f"📁 {os.getcwd()}\n{file_list}\n")
            user_input = f"Files in my current directory:\n{file_list}\nWhat can you tell me about this project structure?"

        # ── /project ──────────────────────────────────────────────────────────
        elif user_input.lower() == '/project':
            structure = scan_project(cwd)
            print(f"📁 Project structure:\n{structure}\n")
            user_input = f"Here is my project structure:\n{structure}\nPlease analyze this and suggest improvements."

        # ── /read ─────────────────────────────────────────────────────────────
        elif user_input.startswith('/read '):
            paths = shlex.split(user_input)[1:]
            if len(paths) == 1:
                content = read_file(paths[0])
                if content is None:
                    print(f"❌ File not found: {paths[0]}\n")
                    continue
                print(f"✅ Loaded: {paths[0]}\n")
                user_input = f"Here is my code from {paths[0]}:\n\n{content}\n\nPlease review it and suggest improvements."
            else:
                combined, loaded, failed = read_files(paths)
                if failed:
                    print(f"⚠️  Not found: {', '.join(failed)}")
                if not loaded:
                    print("❌ No files could be read.\n")
                    continue
                print(f"✅ Loaded: {', '.join(loaded)}\n")
                user_input = f"Here are my files:\n\n{combined}\n\nPlease review them and suggest improvements."

        # ── /save ─────────────────────────────────────────────────────────────
        elif user_input.startswith('/save '):
            filepath = shlex.split(user_input)[1]
            if not last_response:
                print("❌ No response to save yet!\n")
                continue
            code   = extract_code(last_response) or last_response
            result = write_file(filepath, code)
            print(f"✅ Saved to: {filepath}\n" if result is True else f"❌ {result}\n")
            continue

        # ── /edit ─────────────────────────────────────────────────────────────
        elif user_input.startswith('/edit '):
            parts = shlex.split(user_input)[1:]
            if len(parts) < 2:
                print('Usage: /edit <filepath> "<instruction>"\n')
                continue
            print(cmd_edit(parts[0], ' '.join(parts[1:])) + '\n')
            continue

        # ── /implement ────────────────────────────────────────────────────────
        elif user_input.startswith('/implement '):
            parts = shlex.split(user_input)[1:]
            if not parts:
                print('Usage: /implement "<feature>"\n')
                continue
            feature  = ' '.join(parts)
            print(f"\n🚀 Implementing: {feature}\n")
            statuses = cmd_implement(feature, cwd=cwd)
            print("\n🤖 Done! Changes made:")
            for s in statuses:
                print(s)
            print()
            continue

        # ── Smart file detection ──────────────────────────────────────────────
        elif is_action_prompt(user_input):
            explicit = detect_file_paths(user_input, cwd)
            if explicit:
                print(f"📎 Detected files: {', '.join(explicit)}")

            changes = cmd_smart(user_input, cwd=cwd, explicit_paths=explicit or None)

            if not changes:
                print("⚠️  No file changes proposed. Answering as chat...\n")
                messages.append({'role': 'user', 'content': user_input})
                last_response = chat(messages)
                messages.append({'role': 'assistant', 'content': last_response})
            else:
                confirmed = show_and_confirm(changes)
                if confirmed:
                    statuses = apply_changes(confirmed, cwd=cwd)
                    print("\n🤖 Done!")
                    for s in statuses:
                        print(s)
                    print()
                    last_response = "Applied changes to: " + ", ".join(p for p, _, _ in confirmed)
                    messages.append({'role': 'user',      'content': user_input})
                    messages.append({'role': 'assistant', 'content': last_response})
                else:
                    print("↩️  Cancelled. No files written.\n")

        # ── Normal chat (with MCP tools when enabled) ─────────────────────────
        else:
            messages.append({'role': 'user', 'content': user_input})
            if mcp.has_tools:
                last_response, messages = chat_with_tools(messages, mcp)
            else:
                last_response = chat(messages)
                messages.append({'role': 'assistant', 'content': last_response})

        log.debug("Turn complete. History length: %d", len(messages))


if __name__ == '__main__':
    main()
