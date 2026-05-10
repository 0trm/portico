from pathlib import Path

import pytest

from portico.loaders.base import F1NotFound, F2NotParseable
from portico.loaders.file import load_file
from portico.loaders.text import load_text


def test_load_text_happy_path() -> None:
    out = load_text("hello world")
    assert out.text == "hello world"
    assert out.input_type == "text"
    assert out.source == "<text>"
    assert out.metadata["chars"] == 11


def test_load_text_empty_rejected() -> None:
    with pytest.raises(F2NotParseable):
        load_text("")


def test_load_file_happy_path(tmp_path: Path) -> None:
    f = tmp_path / "essay.txt"
    f.write_text("a short essay")
    out = load_file(f)
    assert out.text == "a short essay"
    assert out.input_type == "file"
    assert out.source == str(f)
    assert out.metadata["bytes"] == 13


def test_load_file_missing_raises_f1(tmp_path: Path) -> None:
    with pytest.raises(F1NotFound):
        load_file(tmp_path / "nope.txt")


def test_load_file_directory_raises_f1(tmp_path: Path) -> None:
    with pytest.raises(F1NotFound):
        load_file(tmp_path)


def test_load_file_binary_raises_f2(tmp_path: Path) -> None:
    f = tmp_path / "blob.bin"
    f.write_bytes(b"\x00\x01\x02hello\x00")
    with pytest.raises(F2NotParseable):
        load_file(f)


def test_load_file_invalid_utf8_raises_f2(tmp_path: Path) -> None:
    f = tmp_path / "latin.txt"
    # 0xff is invalid UTF-8 but is not \x00, so binary heuristic doesn't catch it.
    f.write_bytes(b"\xff\xfe\xff\xfe text-ish")
    with pytest.raises(F2NotParseable):
        load_file(f)


def test_load_file_empty_raises_f2(tmp_path: Path) -> None:
    f = tmp_path / "empty.txt"
    f.write_text("")
    with pytest.raises(F2NotParseable):
        load_file(f)
