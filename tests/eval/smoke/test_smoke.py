"""Smoke eval: run analyzer + renderer against 10 stratified inputs.

Auto-runs in default pytest if ANTHROPIC_API_KEY is set, else skips.
Outputs go to tests/eval/smoke/report/ for human spot-check.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from portico.analyzer import analyze
from portico.config import get_anthropic_api_key
from portico.providers.claude import DEFAULT_MODEL, ClaudeProvider
from portico.render import render

INPUTS_DIR = Path(__file__).parent / "inputs"
REPORT_DIR = Path(__file__).parent / "report"


@pytest.fixture(scope="module")
def provider() -> ClaudeProvider:
    if not get_anthropic_api_key():
        pytest.skip("ANTHROPIC_API_KEY not set; smoke eval requires live LLM calls")
    return ClaudeProvider()


@pytest.fixture(scope="module")
def report_dir() -> Path:
    REPORT_DIR.mkdir(exist_ok=True)
    return REPORT_DIR


@pytest.mark.parametrize(
    "input_file",
    sorted(INPUTS_DIR.glob("*.txt")),
    ids=lambda p: p.stem,
)
def test_smoke_input_produces_valid_structure(
    input_file: Path,
    provider: ClaudeProvider,
    report_dir: Path,
) -> None:
    text = input_file.read_text()
    model = os.environ.get("ARQII_MODEL", DEFAULT_MODEL)
    result = analyze(text, provider=provider, model=model)
    rendered = render(result.data, width=80)

    stem = input_file.stem
    (report_dir / f"{stem}.json").write_text(
        json.dumps(result.data.model_dump(mode="json"), indent=2) + "\n"
    )
    (report_dir / f"{stem}.txt").write_text(rendered)

    assert result.attempts <= 3
    assert 2 <= len(result.data.pillars) <= 9
