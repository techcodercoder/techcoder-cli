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

            seen = set()
            for filepath in self._files:
                basename = os.path.basename(filepath)
                # Match full relative path OR just the filename
                if filepath.startswith(partial) or basename.startswith(partial):
                    if filepath not in seen:
                        seen.add(filepath)
                        yield Completion(
                            filepath,
                            start_position=-len(partial),
                            display=filepath,
                            display_meta=os.path.dirname(filepath) or '.',
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
            complete_while_typing=True,    # show suggestions automatically after '@'
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
    Supports short names: @login_screen.dart resolves to lib/screens/login_screen.dart.
    Example: "review @lib/main.dart and @pubspec.yaml" → ['lib/main.dart', 'pubspec.yaml']
    """
    import re
    pattern = re.compile(r'@([\w./\\-]+)')
    all_files = None   # lazy-loaded if needed
    found = []
    for match in pattern.finditer(text):
        rel = match.group(1).rstrip('.,;:)')
        if os.path.isfile(os.path.join(cwd, rel)):
            found.append(rel)
        else:
            # Short name: search project for a file whose basename matches
            if all_files is None:
                all_files = _scan_files(cwd)
            name = os.path.basename(rel)
            matches = [f for f in all_files if os.path.basename(f) == name]
            if len(matches) == 1:
                found.append(matches[0])
            elif len(matches) > 1:
                # Prefer the closest match (fewest path segments)
                found.append(min(matches, key=lambda f: f.count(os.sep)))
    return found


def strip_at_mentions(text: str) -> str:
    """Remove @filename tokens from a prompt string."""
    import re
    return re.sub(r'@[\w./\\-]+', '', text).strip()
