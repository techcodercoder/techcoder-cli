"""
Unified diff generation, colored terminal display, and confirm prompt.
"""

import difflib

_RED    = '\033[31m'
_GREEN  = '\033[32m'
_CYAN   = '\033[36m'
_YELLOW = '\033[33m'
_BOLD   = '\033[1m'
_RESET  = '\033[0m'

Change = tuple[str, str, str]   # (filepath, old_content, new_content)


def make_diff(old: str, new: str, filepath: str) -> str:
    return '\n'.join(difflib.unified_diff(
        old.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile=f"a/{filepath}",
        tofile=f"b/{filepath}",
        lineterm='',
    ))


def print_diff(diff: str):
    if not diff.strip():
        print(f"  {_YELLOW}(no changes){_RESET}")
        return
    for line in diff.splitlines():
        if line.startswith(('---', '+++')):
            print(f"{_BOLD}{_CYAN}{line}{_RESET}")
        elif line.startswith('@@'):
            print(f"{_CYAN}{line}{_RESET}")
        elif line.startswith('+'):
            print(f"{_GREEN}{line}{_RESET}")
        elif line.startswith('-'):
            print(f"{_RED}{line}{_RESET}")
        else:
            print(line)


def _file_header(filepath: str, old: str):
    tag = f"{_BOLD}{_GREEN}[NEW]{_RESET}" if old == '' else f"{_BOLD}[MODIFIED]{_RESET}"
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
    Show colored diffs for all changes, prompt y/n/s, return confirmed subset.

      y — apply all
      n — cancel all
      s — select file by file
    """
    if not changes:
        print("  (nothing to change)")
        return []

    print()
    for filepath, old, new in changes:
        _file_header(filepath, old)
        print_diff(make_diff(old, new, filepath))
        print()

    n = len(changes)
    print(f"{_BOLD}{n} {'file' if n == 1 else 'files'} to change.{_RESET}")
    answer = _ask("Apply changes? [y/n/s]  (y=all  n=cancel  s=select): ")

    if answer in ('y', 'yes'):
        return changes
    if answer in ('s', 'select'):
        return _select_individually(changes)
    return []


def _select_individually(changes: list[Change]) -> list[Change]:
    confirmed: list[Change] = []
    for i, (filepath, old, new) in enumerate(changes, 1):
        print(f"\n{_BOLD}File {i}/{len(changes)}{_RESET}")
        _file_header(filepath, old)
        print_diff(make_diff(old, new, filepath))
        print()
        if _ask(f"Apply {filepath}? [y/N]: ") in ('y', 'yes'):
            confirmed.append((filepath, old, new))
        else:
            print(f"  {_YELLOW}↩ Skipped{_RESET}")
    return confirmed
