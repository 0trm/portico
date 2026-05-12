import pytest

from portico.loaders.base import F2TooLarge, LoadedInput
from portico.providers.base import LLMProvider
from portico.summarize import (
    CHUNK_CHARS,
    HARD_CAP_CHARS,
    TARGET_CHARS,
    _split_into_chunks,
    summarize,
)


class FakeProvider(LLMProvider):
    """Returns a fixed-length compressed summary for any chunk."""

    def __init__(self, summary_chars: int = 1000) -> None:
        self.summary_chars = summary_chars
        self.calls: list[str] = []

    def generate(self, prompt: str, *, model: str) -> str:
        self.calls.append(prompt)
        return "x" * self.summary_chars


def _input(text: str) -> LoadedInput:
    return LoadedInput(text=text, source="test", input_type="text", metadata={})


def test_passthrough_when_under_target() -> None:
    out = summarize(_input("hello"), provider=FakeProvider(), model="m")
    assert out.text == "hello"
    assert "summarized" not in out.metadata


def test_above_hard_cap_raises_f2() -> None:
    huge = "a" * (HARD_CAP_CHARS + 1)
    with pytest.raises(F2TooLarge):
        summarize(_input(huge), provider=FakeProvider(), model="m")


def test_summarizes_when_above_target_one_level() -> None:
    # Just over target -> single level of summarization is enough.
    text_size = TARGET_CHARS + 50_000
    text = "para.\n\n" * (text_size // 7)
    provider = FakeProvider(summary_chars=500)
    out = summarize(_input(text), provider=provider, model="m")
    assert out.metadata["summarized"] is True
    assert out.metadata["summarize_levels"] == 1
    assert len(out.text) <= TARGET_CHARS
    assert provider.calls  # at least one chunk summarized


def test_summarizes_recursively_when_one_level_insufficient() -> None:
    # Force two levels: each chunk summary still totals more than TARGET.
    chunk_count_needed = (TARGET_CHARS // 5_000) + 5
    huge = ("para.\n\n" * (CHUNK_CHARS // 7)) * chunk_count_needed
    provider = FakeProvider(summary_chars=5_000)  # each summary still big
    out = summarize(_input(huge), provider=provider, model="m")
    assert out.metadata["summarize_levels"] == 2


def test_split_respects_paragraph_boundaries() -> None:
    text = "a" * 1000 + "\n\n" + "b" * 1000 + "\n\n" + "c" * 1000
    chunks = _split_into_chunks(text, chunk_size=2500)
    # The first chunk should hold a + b (under 2500 chars combined), c alone in second.
    assert len(chunks) == 2
    assert chunks[0].startswith("a")
    assert chunks[1].startswith("c")


def test_split_hard_slices_oversized_paragraph() -> None:
    text = "x" * 5000  # one paragraph, larger than chunk_size
    chunks = _split_into_chunks(text, chunk_size=2000)
    assert len(chunks) == 3  # 2000 + 2000 + 1000
    assert all(len(c) <= 2000 for c in chunks)
