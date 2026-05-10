import json
from pathlib import Path

import pytest

from portico.render import render
from portico.render.styles.default import _split_label
from portico.schema import PorticoJSON

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


def test_long_labels_wrap_to_two_rows() -> None:
    """Labels longer than cw-1 wrap to 2 rows; no truncation footer when 2 rows suffice."""
    data = _load("long_labels_4pillars.json")
    out = render(data, width=SNAPSHOT_WIDTH)
    # Split parts appear on their own lines.
    assert "Authentication" in out
    assert "subsystem" in out
    # No ellipsis — labels fit in 2 rows.
    assert "…" not in out
    # No truncation footer.
    assert "truncated labels:" not in out


def test_short_label_in_wrap_render_uses_shaft_fill() -> None:
    """In a wrap-active render, short labels show a shaft segment on row 2 instead of a gap."""
    data = _load("survey_9pillars_stretched.json")
    out = render(data, width=SNAPSHOT_WIDTH)
    lines = out.splitlines()
    refine_idx = next(i for i, ln in enumerate(lines) if "Refine" in ln)
    row2 = lines[refine_idx + 1]
    # Row 2 has wrapped-label fragments AND a shaft for Refine's column.
    assert "██" in row2
    assert "fing" in row2 or "reduce" in row2


def test_split_label_word_boundary_preferred() -> None:
    line1, line2, safety = _split_label("Map-reduce", cw=8)
    assert (line1, line2, safety) == ("Map-", "reduce", False)


def test_split_label_balanced_when_no_word_boundary() -> None:
    line1, line2, safety = _split_label("Stuffing", cw=8)
    assert (line1, line2, safety) == ("Stuf", "fing", False)


def test_split_label_safety_net_for_extra_long() -> None:
    """Labels > 2*(cw-1) get ellipsized on row 2 (and trigger the truncation footer)."""
    line1, line2, safety = _split_label("X" * 30, cw=8)
    assert safety is True
    assert "…" in line2
    assert len(line1) <= 7
    assert len(line2) <= 7
