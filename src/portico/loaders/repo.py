"""Repo loader. v1: same file-walking strategy as dir loader, type tagged 'repo'."""

from pathlib import Path

from portico.loaders.base import LoadedInput
from portico.loaders.dir import load_dir


def load_repo(path: str | Path) -> LoadedInput:
    out = load_dir(path)
    return LoadedInput(
        text=out.text,
        source=out.source,
        input_type="repo",
        metadata={**out.metadata, "loader_strategy": "file-walk"},
    )
