import os
import shlex

from config import build_system_prompt
from chat import chat
from file_handler import read_file, read_files, write_file, extract_code, scan_project
from stack_detector import detect_stack
from file_detector import detect_file_paths, is_action_prompt
from agent import cmd_edit, cmd_implement, cmd_smart, apply_changes
from differ import show_and_confirm


def _print_help():
    print("""Commands:
  /ls                              List files in current directory
  /project                         Scan & analyze full project structure
  /read <file> [file2 ...]         Read one or more files
  /save <filepath>                 Save last response to file
  /edit <filepath> "<instruction>" Edit a file directly with Gemma
  /implement "<feature>"           Agentic: implement a feature across files
  /clear                           Clear chat history
  exit                             Quit
""")


def main():
    cwd = os.getcwd()
    stack, stack_prompt = detect_stack(cwd)

    print("🤖 TechCoder CLI - Powered by Gemma 4")
    print("Your personal coding assistant.")
    if stack:
        print(f"🔍 Detected stack: {stack}")
    _print_help()

    system_prompt = build_system_prompt(stack_prompt)
    messages = [{'role': 'system', 'content': system_prompt}]
    last_response = ""

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye! Happy coding! 👋")
            break

        if not user_input:
            continue

        # ── Exit ──────────────────────────────────────────────────────────────
        if user_input.lower() == 'exit':
            print("Bye! Happy coding! 👋")
            break

        # ── Clear history ──────────────────────────────────────────────────────
        if user_input.lower() == '/clear':
            messages = [{'role': 'system', 'content': system_prompt}]
            print("✅ Chat history cleared!\n")
            continue

        # ── /ls ───────────────────────────────────────────────────────────────
        if user_input.lower() == '/ls':
            files = sorted(os.listdir('.'))
            file_list = '\n'.join(files)
            print(f"📁 {os.getcwd()}\n{file_list}\n")
            user_input = (f"Files in my current directory:\n{file_list}\n"
                          f"What can you tell me about this project structure?")

        # ── /project ──────────────────────────────────────────────────────────
        elif user_input.lower() == '/project':
            structure = scan_project(cwd)
            print(f"📁 Project structure:\n{structure}\n")
            user_input = (f"Here is my project structure:\n{structure}\n"
                          f"Please analyze this and suggest improvements.")

        # ── /read <file> [file2 ...] ──────────────────────────────────────────
        elif user_input.startswith('/read '):
            paths = shlex.split(user_input)[1:]
            if len(paths) == 1:
                content = read_file(paths[0])
                if content is None:
                    print(f"❌ File not found: {paths[0]}\n")
                    continue
                print(f"✅ Loaded: {paths[0]}\n")
                user_input = (f"Here is my code from {paths[0]}:\n\n{content}\n\n"
                              f"Please review it and suggest improvements.")
            else:
                combined, loaded, failed = read_files(paths)
                if failed:
                    print(f"⚠️  Not found: {', '.join(failed)}")
                if not loaded:
                    print("❌ No files could be read.\n")
                    continue
                print(f"✅ Loaded: {', '.join(loaded)}\n")
                user_input = (f"Here are my files:\n\n{combined}\n\n"
                              f"Please review them and suggest improvements.")

        # ── /save <filepath> ──────────────────────────────────────────────────
        elif user_input.startswith('/save '):
            filepath = shlex.split(user_input)[1]
            if not last_response:
                print("❌ No response to save yet!\n")
                continue
            code = extract_code(last_response) or last_response
            result = write_file(filepath, code)
            if result is True:
                print(f"✅ Saved to: {filepath}\n")
            else:
                print(f"❌ {result}\n")
            continue

        # ── /edit <filepath> "<instruction>" ──────────────────────────────────
        elif user_input.startswith('/edit '):
            parts = shlex.split(user_input)[1:]
            if len(parts) < 2:
                print('Usage: /edit <filepath> "<instruction>"\n')
                continue
            filepath, instruction = parts[0], ' '.join(parts[1:])
            status = cmd_edit(filepath, instruction)
            print(f"{status}\n")
            continue

        # ── /implement "<feature>" ────────────────────────────────────────────
        elif user_input.startswith('/implement '):
            parts = shlex.split(user_input)[1:]
            if not parts:
                print('Usage: /implement "<feature description>"\n')
                continue
            feature = ' '.join(parts)
            print(f"\n🚀 Implementing: {feature}\n")
            statuses = cmd_implement(feature, cwd=cwd)
            print("\n🤖 Done! Changes made:")
            for s in statuses:
                print(s)
            print()
            continue

        # ── Smart file detection (natural language) ───────────────────────────
        elif is_action_prompt(user_input):
            explicit = detect_file_paths(user_input, cwd)
            if explicit:
                print(f"📎 Detected files: {', '.join(explicit)}")

            changes = cmd_smart(user_input, cwd=cwd, explicit_paths=explicit or None)

            if not changes:
                # Gemma returned no FILE blocks — fall back to plain chat
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
                    summary = "Applied changes to: " + ", ".join(p for p, _, _ in confirmed)
                    messages.append({'role': 'user', 'content': user_input})
                    messages.append({'role': 'assistant', 'content': summary})
                    last_response = summary
                else:
                    print("↩️  Cancelled. No files written.\n")

        # ── Normal chat ───────────────────────────────────────────────────────
        else:
            messages.append({'role': 'user', 'content': user_input})
            last_response = chat(messages)
            messages.append({'role': 'assistant', 'content': last_response})


if __name__ == "__main__":
    main()
