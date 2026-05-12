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


def test_render_no_legend_omits_legend() -> None:
    data = _load("codebase_3pillars.json")
    out = render(data, width=SNAPSHOT_WIDTH, legend=False)
    assert "legend:" not in out
    assert "Public API" in out  # the portico itself still rendered


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


# --- Width 97 / height 54 fit-the-window refactor ---

LONG_SUMMARY = (
    "Rocky endures because of what it means, not what it literally shows the audience, "
    "and that meaning compounds across rewatches into something larger than the movie itself."
)


def _make_data(num_pillars: int, summary: str) -> PorticoJSON:
    return PorticoJSON.model_validate({
        "input_type": "essay",
        "type_rationale": "test",
        "decomposition_strategy": "test",
        "scratch_outline": ["test"],
        "mece_check": "test",
        "theme": "test",
        "title": "wrap-fixture",
        "roof": {"label": "Roof", "summary": summary},
        "pillars": [
            {"label": f"Pillar {i}", "summary": summary} for i in range(num_pillars)
        ],
        "base": {"label": "Base", "summary": summary},
        "fit_quality": "good",
        "notes_on_fit": "",
    })


def test_legend_wraps_long_summary_at_width_97() -> None:
    data = _make_data(num_pillars=3, summary=LONG_SUMMARY)
    out = render(data, width=97)
    legend_idx = next(i for i, ln in enumerate(out.splitlines()) if ln == "legend:")
    legend_block = out.splitlines()[legend_idx + 1 :]
    # No legend line exceeds the width.
    assert all(len(ln) <= 97 for ln in legend_block if ln), legend_block
    # At least one entry wrapped (we have 5 entries; wrapped count > 5 means wrap engaged).
    non_empty = [ln for ln in legend_block if ln.strip()]
    assert len(non_empty) > 5
    # Continuation lines hang-indent 5 spaces (under the label, past the glyph).
    assert any(ln.startswith("     ") and not ln.startswith("      ") for ln in non_empty)


def test_render_fits_height_budget_when_set() -> None:
    data = _make_data(num_pillars=3, summary=LONG_SUMMARY)
    out = render(data, width=97, height=54)
    assert len(out.splitlines()) <= 54


def test_compact_legend_collapses_when_over_budget() -> None:
    data = _make_data(num_pillars=9, summary=LONG_SUMMARY * 3)
    out = render(data, width=97, height=54)
    assert len(out.splitlines()) <= 54
    # Compact legend: lines between "legend:" and the following blank, 1 line each.
    lines = out.splitlines()
    legend_idx = next(i for i, ln in enumerate(lines) if ln == "legend:")
    entries = []
    for ln in lines[legend_idx + 1 :]:
        if not ln.strip():
            break
        entries.append(ln)
    # 1 roof + 9 pillars + 1 base = 11 entries.
    assert len(entries) == 9 + 2
    # Every entry truncated to width with an ellipsis (summaries were too long).
    assert all("…" in ln for ln in entries)
    assert all(len(ln) <= 97 for ln in entries)


def test_render_without_height_unchanged() -> None:
    """Calling render() without height (today's default) is byte-identical to the snapshot."""
    data = _load("codebase_3pillars.json")
    expected = (EXPECTED_DIR / "codebase_3pillars.txt").read_text()
    assert render(data, width=SNAPSHOT_WIDTH) == expected
