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
