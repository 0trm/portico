import sys

from portico.loaders.base import F2NotParseable, LoadedInput


def load_text(text: str, *, source: str = "<text>") -> LoadedInput:
    """Wrap a string as a LoadedInput. No I/O."""
    if not text:
        raise F2NotParseable("input is empty")
    return LoadedInput(
        text=text,
        source=source,
        input_type="text",
        metadata={"chars": len(text)},
    )


def load_stdin() -> LoadedInput:
    """Read all of stdin as text."""
    text = sys.stdin.read()
    return load_text(text, source="<stdin>")
