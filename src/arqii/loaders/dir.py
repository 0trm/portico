"""Codebase loader: file-walking + text concatenation.

Simple v1 strategy: walk the directory, skip ignored paths, always include a
small allowlist of orientation files (README, LICENSE, manifests), concatenate
text contents with path headers. RepoMapper / repomix integration is a
post-v0.1.0 enhancement that can replace this without changing the CLI surface.
"""

from pathlib import Path

from arqii.loaders.base import F1NotFound, F2NotParseable, LoadedInput

IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".pyright",
    "dist",
    "build",
    "target",
    ".next",
    ".cache",
}

IGNORE_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".so",
    ".dylib",
    ".dll",
    ".exe",
    ".lock",
    ".min.js",
    ".min.css",
    ".map",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
}

# Files to always include verbatim if present, in this order.
ALWAYS_INCLUDE = [
    "README.md",
    "README",
    "LICENSE",
    "LICENSE.md",
    "pyproject.toml",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "Makefile",
    "justfile",
    ".env.example",
]

PER_FILE_MAX_BYTES = 50_000
TOTAL_MAX_BYTES = 500_000


def _is_ignored_dir(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)


def _is_text_file(path: Path) -> bool:
    if path.suffix.lower() in IGNORE_SUFFIXES:
        return False
    try:
        sample = path.read_bytes()[:8192]
    except OSError:
        return False
    if b"\x00" in sample:
        return False
    try:
        sample.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def _walk(root: Path) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        rel = p.relative_to(root)
        if _is_ignored_dir(rel.parent):
            continue
        if not _is_text_file(p):
            continue
        files.append(p)
    return files


def load_dir(path: str | Path) -> LoadedInput:
    root = Path(path)
    if not root.exists():
        raise F1NotFound(f"directory not found: {root}")
    if not root.is_dir():
        raise F1NotFound(f"not a directory: {root}")

    files = _walk(root)
    if not files:
        raise F2NotParseable(f"no readable text files in {root}")

    # Build concatenation: tree first, then orientation files, then everything else.
    tree = "\n".join(sorted(str(f.relative_to(root)) for f in files))
    sections: list[str] = [f"# Tree of {root.name}\n\n{tree}\n"]

    orientation: list[Path] = []
    others: list[Path] = []
    always_set = set(ALWAYS_INCLUDE)
    for f in files:
        if f.relative_to(root).name in always_set:
            orientation.append(f)
        else:
            others.append(f)

    # Stable order for orientation per ALWAYS_INCLUDE; alphabetical for the rest.
    orient_order = {name: i for i, name in enumerate(ALWAYS_INCLUDE)}
    orientation.sort(key=lambda p: orient_order.get(p.relative_to(root).name, 999))
    others.sort(key=lambda p: str(p.relative_to(root)))

    total_bytes = 0
    truncated_files: list[str] = []
    for f in orientation + others:
        body = f.read_text(encoding="utf-8", errors="replace")
        if len(body) > PER_FILE_MAX_BYTES:
            body = body[:PER_FILE_MAX_BYTES] + "\n... [truncated]\n"
        section = f"\n## {f.relative_to(root)}\n\n{body}\n"
        if total_bytes + len(section) > TOTAL_MAX_BYTES:
            truncated_files.append(str(f.relative_to(root)))
            continue
        sections.append(section)
        total_bytes += len(section)

    text = "".join(sections)
    return LoadedInput(
        text=text,
        source=str(root),
        input_type="dir",
        metadata={
            "files": len(files),
            "files_included": len(files) - len(truncated_files),
            "files_truncated_by_total_cap": len(truncated_files),
            "chars": len(text),
        },
    )
