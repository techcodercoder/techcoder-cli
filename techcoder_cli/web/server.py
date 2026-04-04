"""
Web UI server — placeholder for future implementation.
Run with: techcoder --ui  or  make ui
"""

from ..config.settings import DEFAULT_PORT
from ..utils.logger import get_logger

log = get_logger(__name__)


def run(port: int = DEFAULT_PORT, debug: bool = False):
    """Start the web UI server."""
    log.info("Web UI coming soon (port %d)", port)
    print(f"🌐 Web UI is not yet implemented.")
    print(f"   Follow the roadmap at https://github.com/techcodercoder/techcoder-cli")
