from pathlib import Path

import pytest

from arqii.loaders.base import F1NotFound, F2NotParseable
from arqii.loaders.dir import load_dir
from arqii.loaders.repo import load_repo


def _make_sample_repo(root: Path) -> None:
    (root / "README.md").write_text("# sample repo\n\nA tiny test fixture.\n")
    (root / "pyproject.toml").write_text("[project]\nname = 'sample'\n")
    src = root / "src"
    src.mkdir()
    (src / "main.py").write_text("def main():\n    print('hi')\n")
    (src / "util.py").write_text("def helper(): pass\n")
    # Things that should be skipped:
    (root / ".git").mkdir()
    (root / ".git" / "config").write_text("ignored")
    (root / "binary.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x01")
    venv = root / ".venv"
    venv.mkdir()
    (venv / "junk.py").write_text("should not appear")


def test_load_dir_happy_path(tmp_path: Path) -> None:
    _make_sample_repo(tmp_path)
    out = load_dir(tmp_path)
    assert out.input_type == "dir"
    assert "# Tree of" in out.text
    assert "README.md" in out.text
    assert "pyproject.toml" in out.text
    assert "main.py" in out.text
    # Skipped paths should not leak in.
    assert "ignored" not in out.text
    assert "should not appear" not in out.text
    assert out.metadata["files"] >= 4


def test_load_dir_orientation_files_first(tmp_path: Path) -> None:
    _make_sample_repo(tmp_path)
    out = load_dir(tmp_path)
    readme_idx = out.text.index("## README.md")
    pyproject_idx = out.text.index("## pyproject.toml")
    main_idx = out.text.index("## src/main.py")
    assert readme_idx < pyproject_idx < main_idx


def test_load_dir_missing_raises_f1(tmp_path: Path) -> None:
    with pytest.raises(F1NotFound):
        load_dir(tmp_path / "nope")


def test_load_dir_file_path_raises_f1(tmp_path: Path) -> None:
    f = tmp_path / "a.txt"
    f.write_text("hi")
    with pytest.raises(F1NotFound):
        load_dir(f)


def test_load_dir_no_text_files_raises_f2(tmp_path: Path) -> None:
    (tmp_path / "blob.png").write_bytes(b"\x89PNG\r\n")
    with pytest.raises(F2NotParseable):
        load_dir(tmp_path)


def test_load_repo_happy_path(tmp_path: Path) -> None:
    _make_sample_repo(tmp_path)
    out = load_repo(tmp_path)
    assert out.input_type == "repo"
    assert out.metadata["loader_strategy"] == "file-walk"
    assert "README.md" in out.text
