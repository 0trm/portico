import json
from pathlib import Path

import pytest

from arqii.render import render
from arqii.render.apex import (
    CENTERS,
    FINIALS,
    KEYSTONE_WIDTH,
    RULES,
    generate_apex,
)
from arqii.schema import PorticoJSON

FIXTURES = Path(__file__).parent / "fixtures" / "json"
SNAPSHOT_WIDTH = 80


def _load(name: str) -> PorticoJSON:
    return PorticoJSON.model_validate(json.loads((FIXTURES / name).read_text()))


def test_generate_apex_deterministic_given_seed() -> None:
    a = generate_apex(seed=42)
    b = generate_apex(seed=42)
    assert a == b


def test_generate_apex_returns_seed_when_random() -> None:
    finial, keystone, seed = generate_apex(seed=None)
    assert isinstance(seed, int)
    # Re-rolling with the returned seed reproduces the same output.
    assert generate_apex(seed=seed) == (finial, keystone, seed)


def test_generate_apex_keystone_width_invariant() -> None:
    """Keystone is always exactly 11 chars regardless of seed."""
    for seed in range(0, 200):
        _, keystone, _ = generate_apex(seed=seed)
        assert len(keystone) == KEYSTONE_WIDTH == 11


def test_generate_apex_rows_are_symmetric() -> None:
    """Every roll produces bilaterally-symmetric rows (palindromes)."""
    for seed in range(0, 200):
        finial, keystone, _ = generate_apex(seed=seed)
        assert finial == finial[::-1], f"asymmetric finial at seed {seed}: {finial!r}"
        assert keystone == keystone[::-1], (
            f"asymmetric keystone at seed {seed}: {keystone!r}"
        )


def test_generate_apex_uses_only_curated_glyphs() -> None:
    """Every non-space character must come from the curated pools."""
    allowed = set(RULES) | set(FINIALS) | set(CENTERS)
    for seed in range(0, 200):
        finial, keystone, _ = generate_apex(seed=seed)
        for ch in finial.replace(" ", "") + keystone.replace(" ", ""):
            assert ch in allowed, f"unexpected glyph {ch!r} at seed {seed}"


def test_render_apex_override_replaces_locked_apex() -> None:
    """When apex_override is supplied, the locked v1 apex is not rendered."""
    data = _load("essay_2pillars.json")
    custom = ("· · ·", "═══  ★  ═══")
    out = render(data, width=SNAPSHOT_WIDTH, apex_override=custom)
    assert "· · ·" in out
    assert "═══  ★  ═══" in out
    # Locked apex glyphs (◇ in the keystone) should be gone.
    # (Ensure the override actually replaced rather than added.)
    keystone_lines = [ln for ln in out.splitlines() if "===" in ln or "═══" in ln]
    assert any("★" in ln for ln in keystone_lines)
    assert not any("===  ◇  ===" in ln for ln in keystone_lines)


def test_render_apex_seed_label_above_signature() -> None:
    """When apex_seed_label is supplied, it appears left-justified above the signature."""
    data = _load("essay_2pillars.json")
    out = render(data, width=SNAPSHOT_WIDTH, apex_seed_label="apex seed: 1234")
    lines = out.rstrip("\n").splitlines()
    # Last line is the signature; second-to-last is the seed label.
    assert "apex seed: 1234" in lines[-2]
    assert lines[-2].startswith("apex seed: 1234")  # left-justified, no indent
    # Signature is on the last line.
    assert "built with _ii^" in lines[-1]


def test_render_no_seed_label_when_omitted() -> None:
    """Seed label only appears when passed explicitly."""
    data = _load("essay_2pillars.json")
    out = render(data, width=SNAPSHOT_WIDTH)
    assert "apex seed:" not in out


@pytest.mark.parametrize("seed", [0, 1, 7, 42, 100, 999, 99999])
def test_apex_renders_within_width_at_80(seed: int) -> None:
    """Generated apex composition fits in the standard portico width."""
    data = _load("codebase_3pillars.json")
    finial, keystone, _ = generate_apex(seed=seed)
    out = render(data, width=SNAPSHOT_WIDTH, apex_override=(finial, keystone))
    for line in out.splitlines():
        assert len(line) <= SNAPSHOT_WIDTH, f"line too wide at seed {seed}: {line!r}"
