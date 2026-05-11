import os
import sys
from enum import StrEnum


class ColorMode(StrEnum):
    AUTO = "auto"
    ALWAYS = "always"
    NEVER = "never"


# ANSI accents per layer. No semantic meaning -- ergonomic only.
ROOF_ACCENT = "\x1b[33m"     # yellow
PILLAR_ACCENT = "\x1b[36m"   # cyan
BASE_ACCENT = "\x1b[35m"     # magenta
RESET = "\x1b[0m"


def paint(s: str, accent: str, *, enabled: bool) -> str:
    if not enabled:
        return s
    return f"{accent}{s}{RESET}"


def resolve(mode: ColorMode) -> bool:
    """Resolve a ColorMode to a concrete on/off decision.

    AUTO honors NO_COLOR (https://no-color.org) and the stdout TTY check.
    """
    if mode == ColorMode.ALWAYS:
        return True
    if mode == ColorMode.NEVER:
        return False
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()
