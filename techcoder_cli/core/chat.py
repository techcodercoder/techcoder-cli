"""
Ollama chat: plain streaming and tool-calling loop.
"""

import itertools
import json
import threading
import time

import ollama

from ..config.settings import MODEL_NAME, MAX_TOOL_ITERATIONS
from ..utils.logger import get_logger

log = get_logger(__name__)


def chat(messages: list[dict]) -> str:
    """Stream a response from Gemma. Prints to stdout, returns full text."""
    spinner    = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    stop_event = threading.Event()
    chunks: list[str] = []

    def fetch():
        stream = ollama.chat(model=MODEL_NAME, messages=messages, stream=True)
        for chunk in stream:
            chunks.append(chunk['message']['content'])
        stop_event.set()

    thread = threading.Thread(target=fetch, daemon=True)
    thread.start()

    while not stop_event.is_set() and not chunks:
        print(f'\r🤖 Gemma: {next(spinner)} Thinking...', end='', flush=True)
        time.sleep(0.1)

    print('\r' + ' ' * 40 + '\r', end='', flush=True)
    print('🤖 Gemma: ', end='', flush=True)

    full = ''
    for content in chunks:
        print(content, end='', flush=True)
        full += content

    thread.join()
    print('\n')
    log.debug("chat() returned %d chars", len(full))
    return full


def chat_with_tools(messages: list[dict], mcp_client) -> tuple[str, list[dict]]:
    """
    Ollama tool-calling loop. Runs up to MAX_TOOL_ITERATIONS rounds.
    Returns (final_response_text, updated_messages).
    Falls back to plain chat() if mcp_client has no tools.
    """
    if mcp_client is None or not mcp_client.has_tools:
        response = chat(messages)
        return response, messages + [{'role': 'assistant', 'content': response}]

    tool_defs       = mcp_client.tool_definitions()
    working         = list(messages)
    spinner         = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    final_text      = ''

    for _ in range(MAX_TOOL_ITERATIONS):
        stop_event    = threading.Event()
        result_holder: list = []

        def fetch(msgs=working, tools=tool_defs):
            result_holder.append(ollama.chat(model=MODEL_NAME, messages=msgs, tools=tools))
            stop_event.set()

        thread = threading.Thread(target=fetch, daemon=True)
        thread.start()
        while not stop_event.is_set():
            print(f'\r🤖 Gemma: {next(spinner)} Thinking...', end='', flush=True)
            time.sleep(0.1)
        thread.join()

        response = result_holder[0]
        msg      = response['message']

        if not msg.get('tool_calls'):
            print('\r' + ' ' * 40 + '\r', end='', flush=True)
            print('🤖 Gemma: ', end='', flush=True)
            final_text = msg.get('content', '')
            print(final_text, end='', flush=True)
            print('\n')
            working.append({'role': 'assistant', 'content': final_text})
            break

        # Record the assistant turn that includes tool_calls
        print('\r' + ' ' * 40 + '\r', end='', flush=True)
        working.append({
            'role':       'assistant',
            'content':    msg.get('content', ''),
            'tool_calls': msg['tool_calls'],
        })

        for tool_call in msg['tool_calls']:
            fn   = tool_call['function']
            name = fn['name']
            args = fn.get('arguments', {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except Exception:
                    args = {}

            if mcp_client.needs_confirmation(name):
                print(f"\n⚠️  MCP wants to run: {name}")
                print(f"   Args: {args}")
                try:
                    ans = input("   Allow? [y/N]: ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    ans = 'n'
                if ans not in ('y', 'yes'):
                    tool_result = f"User cancelled: {name}"
                    print("   ↩ Cancelled\n")
                else:
                    print(f"🔌 Using {_server_label(name)} MCP...")
                    tool_result = mcp_client.execute_tool(name, args)
                    print("   ✅ Done\n")
            else:
                print(f"🔌 Using {_server_label(name)} MCP...")
                tool_result = mcp_client.execute_tool(name, args)

            working.append({'role': 'tool', 'content': tool_result})

    return final_text, working


def _server_label(tool_name: str) -> str:
    if tool_name.startswith('filesystem'):
        return 'Filesystem'
    if tool_name.startswith('github'):
        return 'GitHub'
    if tool_name == 'web_search':
        return 'Web Search'
    if tool_name.startswith('sqlite'):
        return 'SQLite'
    return tool_name
