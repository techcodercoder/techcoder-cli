"""
Structured logging: colorized terminal + rotating file log.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

_LOG_DIR  = os.path.expanduser('~/.techcoder/logs')
_LOG_FILE = os.path.join(_LOG_DIR, 'techcoder.log')

# ANSI colors for terminal handler
_COLORS = {
    'DEBUG':    '\033[36m',   # cyan
    'INFO':     '\033[32m',   # green
    'WARNING':  '\033[33m',   # yellow
    'ERROR':    '\033[31m',   # red
    'CRITICAL': '\033[35m',   # magenta
}
_RESET = '\033[0m'


class _ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        color = _COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname:<8}{_RESET}"
        return super().format(record)


def get_logger(name: str = 'techcoder', level: str = 'INFO') -> logging.Logger:
    """
    Return a logger with:
    - Colorized StreamHandler for the terminal
    - RotatingFileHandler writing to ~/.techcoder/logs/techcoder.log
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger   # already configured

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    fmt       = '%(asctime)s %(levelname)s %(name)s — %(message)s'
    date_fmt  = '%H:%M:%S'
    formatter = logging.Formatter(fmt, datefmt=date_fmt)

    # Terminal
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(_ColorFormatter(fmt, datefmt=date_fmt))
    logger.addHandler(stream_handler)

    # File (rotate at 1 MB, keep 3 backups)
    try:
        os.makedirs(_LOG_DIR, exist_ok=True)
        file_handler = RotatingFileHandler(
            _LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError:
        pass   # silently skip file logging if dir isn't writable

    logger.propagate = False
    return logger


# Module-level default logger
log = get_logger()
