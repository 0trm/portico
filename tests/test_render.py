import json
from pathlib import Path

import pytest

from arqii.render import render
from arqii.schema import PorticoJSON

FIXTURES = Path(__file__).parent / "fixtures"
JSON_DIR = FIXTURES / "json"
EXPECTED_DIR = FIXTURES / "expected"

SNAPSHOT_WIDTH = 80


def _load(name: str) -> PorticoJSON:
    return PorticoJSON.model_validate(json.loads((JSON_DIR / name).read_text()))


@pytest.mark.parametrize(
    "fixture",
    sorted(p.name for p in JSON_DIR.glob("*.json")),
)
def test_render_matches_snapshot(fixture: str) -> None:
    data = _load(fixture)
    expected = (EXPECTED_DIR / (Path(fixture).stem + ".txt")).read_text()
    assert render(data, width=SNAPSHOT_WIDTH) == expected


def test_render_verbose_includes_legend() -> None:
    data = _load("codebase_3pillars.json")
    expected = (EXPECTED_DIR / "codebase_3pillars_verbose.txt").read_text()
    assert render(data, width=SNAPSHOT_WIDTH, verbose=True) == expected


def test_stretched_includes_caveat() -> None:
    data = _load("survey_9pillars_stretched.json")
    out = render(data, width=SNAPSHOT_WIDTH)
    assert out.startswith("note: the portico metaphor is stretched")


def test_good_omits_caveat() -> None:
    data = _load("codebase_3pillars.json")
    out = render(data, width=SNAPSHOT_WIDTH)
    assert "stretched" not in out.splitlines()[0]


def test_long_labels_truncated_with_ellipsis() -> None:
    data = _load("long_labels_4pillars.json")
    out = render(data, width=SNAPSHOT_WIDTH)
    assert "…" in out
    # Original full labels should not appear; truncation must have kicked in.
    assert "Authentication subsystem" not in out
