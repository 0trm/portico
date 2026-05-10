"""Curated combinatorial generator for symmetric apex ornaments.

Used by the --reapex flag to roll an alternative 2-row apex composition that
fits the locked v1 portico's slot. Outputs are bilaterally symmetric by
construction. The keystone row is always exactly 11 chars wide so the apex
occupies the same horizontal footprint regardless of the roll.
"""

from __future__ import annotations

import random

# Pools (structure-coherent; every glyph is bilaterally self-symmetric).
RULES: tuple[str, ...] = ("═", "─", "~", "░", "=", "^")
FINIALS: tuple[str, ...] = ("*", "·", "◇", "▲", "◆")
CENTERS: tuple[str, ...] = ("◇", "◆", "▲")

# Bottom row keystone: 3 R's, 2 spaces, C, 2 spaces, 3 R's. 11 chars total.
_KEYSTONE_RULE_COUNT = 3
KEYSTONE_WIDTH = 2 * _KEYSTONE_RULE_COUNT + 2 + 1 + 2  # 11

_FINIAL_TEMPLATES = ("repeat_1", "repeat_2", "repeat_3", "aba")


def _make_finial(rng: random.Random) -> str:
    template = rng.choice(_FINIAL_TEMPLATES)
    if template == "repeat_1":
        return rng.choice(FINIALS)
    if template == "repeat_2":
        g = rng.choice(FINIALS)
        return f"{g} {g}"
    if template == "repeat_3":
        g = rng.choice(FINIALS)
        return f"{g} {g} {g}"
    # ABA: two distinct self-symmetric glyphs flanking a different center one.
    a, b = rng.sample(FINIALS, 2)
    return f"{a} {b} {a}"


def _make_keystone(rng: random.Random) -> str:
    rule = rng.choice(RULES)
    center = rng.choice(CENTERS)
    flank = rule * _KEYSTONE_RULE_COUNT
    return f"{flank}  {center}  {flank}"


def generate_apex(seed: int | None = None) -> tuple[str, str, int]:
    """Generate a random symmetric apex composition.

    Returns (finial_row, keystone_row, seed_used). If seed is None, picks one
    in [0, 2**31). The same seed always yields the same apex.
    """
    if seed is None:
        seed = random.randrange(2**31)
    rng = random.Random(seed)
    finial = _make_finial(rng)
    keystone = _make_keystone(rng)
    return finial, keystone, seed
