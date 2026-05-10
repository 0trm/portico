from pathlib import Path

from portico.loaders.base import F1NotFound, F2NotParseable, LoadedInput


def _looks_binary(sample: bytes) -> bool:
    """Heuristic: a NUL byte in the first chunk means the file is binary."""
    return b"\x00" in sample


def load_file(path: str | Path) -> LoadedInput:
    """Read a text file from disk."""
    p = Path(path)
    if not p.exists():
        raise F1NotFound(f"file not found: {p}")
    if p.is_dir():
        raise F1NotFound(f"path is a directory, not a file: {p}")
    try:
        sample = p.read_bytes()[:8192]
    except PermissionError as e:
        raise F1NotFound(f"file not readable: {p}") from e

    if _looks_binary(sample):
        raise F2NotParseable(f"file appears to be binary: {p}")

    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        raise F2NotParseable(f"file is not valid UTF-8: {p}") from e

    if not text:
        raise F2NotParseable(f"file is empty: {p}")

    return LoadedInput(
        text=text,
        source=str(p),
        input_type="file",
        metadata={"chars": len(text), "bytes": p.stat().st_size},
    )
