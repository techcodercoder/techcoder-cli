"""
@filename autocomplete for the TechCoder CLI prompt.

Uses prompt_toolkit when available; falls back silently to plain input().
"""

import os

from .config.settings import SCAN_IGNORE_DIRS

# ── File scanner ──────────────────────────────────────────────────────────────

def _scan_files(cwd: str) -> list[str]:
    """Return relative paths of all files under cwd, skipping noise dirs."""
    files = []
    for root, dirs, filenames in os.walk(cwd):
        dirs[:] = [
            d for d in dirs
            if d not in SCAN_IGNORE_DIRS and not d.startswith('.')
        ]
        for name in filenames:
            rel = os.path.relpath(os.path.join(root, name), cwd)
            files.append(rel)
    return sorted(files)


# ── prompt_toolkit integration ────────────────────────────────────────────────

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    import os

    _HISTORY_FILE = os.path.expanduser('~/.techcoder/history')

    class _AtCompleter(Completer):
        """Trigger on '@' — complete with relative file paths."""

        def __init__(self, cwd: str):
            self.cwd = cwd
            self._files: list[str] = []

        def refresh(self):
            self._files = _scan_files(self.cwd)

        def get_completions(self, document, complete_event):
            text = document.text_before_cursor

            # Find the last '@' that starts a file mention
            at_pos = text.rfind('@')
            if at_pos == -1:
                return

            partial = text[at_pos + 1:]   # what user typed after @

            if not self._files:
                self.refresh()

            for filepath in self._files:
                if filepath.startswith(partial):
                    # Replace the partial text after '@'
                    yield Completion(
                        filepath,
                        start_position=-len(partial),
                        display=filepath,
                        display_meta='file',
                    )

    def make_prompt_session(cwd: str) -> tuple:
        """
        Return (session, completer).
        Call session.prompt("You: ") to get user input with autocomplete.
        """
        os.makedirs(os.path.expanduser('~/.techcoder'), exist_ok=True)
        completer = _AtCompleter(cwd)
        session   = PromptSession(
            history=FileHistory(_HISTORY_FILE),
            auto_suggest=AutoSuggestFromHistory(),
            completer=completer,
            complete_while_typing=False,   # only complete on Tab
            mouse_support=False,
        )
        return session, completer

    PROMPT_TOOLKIT_AVAILABLE = True

except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False

    def make_prompt_session(cwd: str) -> tuple:
        return None, None


# ── Unified get_input() ───────────────────────────────────────────────────────

def get_input(prompt_text: str, session=None) -> str:
    """
    Get a line of user input.
    Uses prompt_toolkit session when available, else falls back to input().
    Raises EOFError / KeyboardInterrupt on Ctrl-D / Ctrl-C.
    """
    if session is not None:
        return session.prompt(prompt_text)
    return input(prompt_text)


# ── @mention extraction ───────────────────────────────────────────────────────

def extract_at_mentions(text: str, cwd: str) -> list[str]:
    """
    Return file paths from @filename mentions in text that exist on disk.
    Example: "review @lib/main.dart and @pubspec.yaml" → ['lib/main.dart', 'pubspec.yaml']
    """
    import re
    pattern = re.compile(r'@([\w./\\-]+)')
    found = []
    for match in pattern.finditer(text):
        rel = match.group(1).rstrip('.,;:)')
        if os.path.isfile(os.path.join(cwd, rel)):
            found.append(rel)
    return found


def strip_at_mentions(text: str) -> str:
    """Remove @filename tokens from a prompt string."""
    import re
    return re.sub(r'@[\w./\\-]+', '', text).strip()
