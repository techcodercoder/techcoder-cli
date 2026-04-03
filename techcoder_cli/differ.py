"""
Unified diff generation and colored terminal display.
"""

import difflib

# ANSI color codes
_RED    = '\033[31m'
_GREEN  = '\033[32m'
_CYAN   = '\033[36m'
_YELLOW = '\033[33m'
_BOLD   = '\033[1m'
_RESET  = '\033[0m'

Change = tuple[str, str, str]   # (filepath, old_content, new_content)


def make_diff(old: str, new: str, filepath: str) -> str:
    """Return a unified diff string between old and new content."""
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    diff = difflib.unified_diff(
        old_lines, new_lines,
        fromfile=f"a/{filepath}",
        tofile=f"b/{filepath}",
        lineterm='',
    )
    return '\n'.join(diff)


def print_diff(diff: str):
    """Print a colored unified diff to stdout."""
    if not diff.strip():
        print(f"  {_YELLOW}(no changes){_RESET}")
        return

    for line in diff.splitlines():
        if line.startswith('---') or line.startswith('+++'):
            print(f"{_BOLD}{_CYAN}{line}{_RESET}")
        elif line.startswith('@@'):
            print(f"{_CYAN}{line}{_RESET}")
        elif line.startswith('+'):
            print(f"{_GREEN}{line}{_RESET}")
        elif line.startswith('-'):
            print(f"{_RED}{line}{_RESET}")
        else:
            print(line)


def _print_file_header(filepath: str, old: str):
    is_new = old == ''
    tag = f"{_BOLD}{_GREEN}[NEW]{_RESET}" if is_new else f"{_BOLD}[MODIFIED]{_RESET}"
    print(f"{_BOLD}{_CYAN}{'─' * 60}{_RESET}")
    print(f"  {tag} {filepath}")
    print(f"{_BOLD}{_CYAN}{'─' * 60}{_RESET}")


def _ask(prompt: str) -> str:
    try:
        return input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return ''


def show_and_confirm(changes: list[Change]) -> list[Change]:
    """
    Show colored diffs for all changes, then ask:

      Apply changes? [y/n/s]
        y — apply all
        n — cancel all
        s — select file by file

    Returns the subset of `changes` the user confirmed.
    `old_content=''` means the file is newly created.
    """
    if not changes:
        print("  (nothing to change)")
        return []

    # ── Show all diffs ────────────────────────────────────────────────────────
    print()
    for filepath, old, new in changes:
        _print_file_header(filepath, old)
        print_diff(make_diff(old, new, filepath))
        print()

    # ── Summary line ──────────────────────────────────────────────────────────
    n = len(changes)
    files_word = "file" if n == 1 else "files"
    print(f"{_BOLD}{n} {files_word} to change.{_RESET}")

    # ── Prompt ────────────────────────────────────────────────────────────────
    answer = _ask("Apply changes? [y/n/s]  (y=all  n=cancel  s=select): ")

    if answer in ('y', 'yes'):
        return changes

    if answer in ('s', 'select'):
        return _select_individually(changes)

    # 'n' or anything else → cancel
    return []


def _select_individually(changes: list[Change]) -> list[Change]:
    """Show each diff one at a time and ask y/n per file."""
    confirmed: list[Change] = []

    for i, (filepath, old, new) in enumerate(changes, 1):
        print(f"\n{_BOLD}File {i}/{len(changes)}{_RESET}")
        _print_file_header(filepath, old)
        print_diff(make_diff(old, new, filepath))
        print()

        answer = _ask(f"Apply {filepath}? [y/N]: ")
        if answer in ('y', 'yes'):
            confirmed.append((filepath, old, new))
        else:
            print(f"  {_YELLOW}↩ Skipped{_RESET}")

    return confirmed
