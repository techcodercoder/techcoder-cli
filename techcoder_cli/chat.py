import ollama
import threading
import itertools
import time

from config import MODEL


def chat(messages):
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    stop_event = threading.Event()
    chunks = []

    def fetch():
        stream = ollama.chat(
            model=MODEL,
            messages=messages,
            stream=True
        )
        for chunk in stream:
            chunks.append(chunk['message']['content'])
        stop_event.set()

    fetch_thread = threading.Thread(target=fetch)
    fetch_thread.start()

    # Spinner while waiting for first chunk
    while not stop_event.is_set() and len(chunks) == 0:
        print(f'\r🤖 Gemma: {next(spinner)} Thinking...', end='', flush=True)
        time.sleep(0.1)

    # Clear spinner line
    print('\r' + ' ' * 40 + '\r', end='', flush=True)
    print('🤖 Gemma: ', end='', flush=True)

    # Print buffered chunks
    full_response = ""
    for content in chunks:
        print(content, end='', flush=True)
        full_response += content

    fetch_thread.join()
    print("\n")
    return full_response
