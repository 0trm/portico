import json
from pathlib import Path

import pytest

from portico.analyzer import (
    F4MalformedJSON,
    analyze,
    build_prompt,
)
from portico.providers.base import LLMProvider

FIXTURES = Path(__file__).parent / "fixtures" / "json"


def _good_json() -> str:
    return (FIXTURES / "codebase_3pillars.json").read_text()


class FakeProvider(LLMProvider):
    """Returns scripted responses one per call."""

    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[str, str]] = []

    def generate(self, prompt: str, *, model: str) -> str:
        self.calls.append((prompt, model))
        if not self.responses:
            raise AssertionError("FakeProvider exhausted (test wanted more calls)")
        return self.responses.pop(0)


def test_build_prompt_includes_mece_and_pillar_guidance() -> None:
    prompt = build_prompt("hello world")
    assert "MECE" in prompt
    assert "Minto" in prompt
    assert "load-bearing" in prompt
    assert "STRONGLY PREFER 3-5" in prompt
    assert "hello world" in prompt


def test_build_prompt_lists_schema_in_reasoning_first_order() -> None:
    prompt = build_prompt("x")
    order = [
        "input_type",
        "type_rationale",
        "decomposition_strategy",
        "scratch_outline",
        "mece_check",
        "theme",
        "title",
        "roof",
        "pillars",
        "base",
        "fit_quality",
        "notes_on_fit",
    ]
    positions = [prompt.index(f'"{key}"') for key in order]
    assert positions == sorted(positions), f"schema fields out of order: {positions}"


def test_analyze_happy_path() -> None:
    provider = FakeProvider([_good_json()])
    result = analyze("anything", provider=provider, model="claude-mock")
    assert result.attempts == 1
    assert result.data.theme == "codebase"
    assert len(result.data.pillars) == 3


def test_analyze_strips_markdown_fences() -> None:
    fenced = f"```json\n{_good_json()}\n```"
    provider = FakeProvider([fenced])
    result = analyze("anything", provider=provider, model="claude-mock")
    assert result.data.theme == "codebase"


def test_analyze_retries_on_malformed_json() -> None:
    provider = FakeProvider(["not json at all", _good_json()])
    result = analyze("anything", provider=provider, model="claude-mock")
    assert result.attempts == 2
    # Retry prompt should mention the parse error.
    assert "could not be parsed" in provider.calls[1][0]


def test_analyze_retries_on_schema_violation() -> None:
    invalid = json.loads(_good_json())
    invalid["pillars"] = []  # below minimum
    provider = FakeProvider([json.dumps(invalid), _good_json()])
    result = analyze("anything", provider=provider, model="claude-mock")
    assert result.attempts == 2


def test_analyze_raises_f4_after_retry_budget() -> None:
    provider = FakeProvider(["bad", "still bad", "still bad again"])
    with pytest.raises(F4MalformedJSON):
        analyze("anything", provider=provider, model="claude-mock", max_retries=2)
    assert len(provider.calls) == 3  # initial + 2 retries


def test_analyze_passes_model_through() -> None:
    provider = FakeProvider([_good_json()])
    analyze("anything", provider=provider, model="claude-sonnet-4-6")
    assert provider.calls[0][1] == "claude-sonnet-4-6"
