"""Codebase loader: file-walking + text concatenation.

Simple v1 strategy: walk the directory, skip ignored paths, always include a
small allowlist of orientation files (README, LICENSE, manifests), concatenate
text contents with path headers. RepoMapper / repomix integration is a
post-v0.1.0 enhancement that can replace this without changing the CLI surface.

Safety: when the directory is a git repository, defer to `git ls-files
--exclude-standard` so .gitignore is honored (this is how secrets like .env
get filtered). The hardcoded IGNORE_NAMES below is defense-in-depth for
non-git directories or repos that forget to ignore the file.
"""

import shutil
import subprocess
from pathlib import Path

from portico.loaders.base import F1NotFound, F2NotParseable, LoadedInput

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
    ".pem",
    ".key",
    ".cert",
    ".crt",
    ".p12",
    ".pfx",
}

# Defense-in-depth filenames -- always exclude regardless of .gitignore status.
IGNORE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    ".env.staging",
    ".env.test",
    "id_rsa",
    "id_rsa.pub",
    "id_dsa",
    "id_ed25519",
    "id_ed25519.pub",
    "credentials.json",
    "service-account.json",
    "secrets.yaml",
    "secrets.yml",
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


def _git_ls_files(root: Path) -> list[Path] | None:
    """List tracked + untracked-but-not-ignored files via git, or None if not a git repo."""
    if not (root / ".git").exists():
        return None
    if shutil.which("git") is None:
        return None
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
    except (subprocess.SubprocessError, OSError):
        return None
    return [root / line for line in result.stdout.splitlines() if line]


def _walk(root: Path) -> list[Path]:
    git_listed = _git_ls_files(root)
    if git_listed is not None:
        candidates = [p for p in git_listed if p.is_file()]
    else:
        candidates = [p for p in root.rglob("*") if p.is_file()]

    files: list[Path] = []
    for p in candidates:
        rel = p.relative_to(root)
        if _is_ignored_dir(rel.parent):
            continue
        if rel.name in IGNORE_NAMES:
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
    name = root.name or root.resolve().name or "."
    sections: list[str] = [f"# Tree of {name}\n\n{tree}\n"]

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
