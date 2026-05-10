"""Aggregate judgments into a Markdown report; compute Spearman vs gold if available.

Usage:
    uv run python -m tests.eval.report --run-id <id>

Reads tests/eval/outputs/judgments/{run_id}/ and (optionally) tests/eval/gold/.
Writes tests/eval/outputs/reports/{run_id}.md with:
- Per-dimension distribution (mean, median, count)
- Per-input-type breakdown
- Spearman correlation between judge and gold (if any inputs have gold scores)

Spearman is computed without scipy: rank-based, ties broken by average rank.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path

from tests.eval.judge import DIMENSIONS

EVAL_DIR = Path(__file__).parent
JUDGMENTS_DIR = EVAL_DIR / "outputs" / "judgments"
REPORTS_DIR = EVAL_DIR / "outputs" / "reports"
GOLD_DIR = EVAL_DIR / "gold"


@dataclass
class Item:
    input_path: str
    input_type: str
    scores: dict[str, int]


def _load_judgments(run_dir: Path) -> list[Item]:
    items: list[Item] = []
    for jp in sorted(run_dir.rglob("*.json")):
        if jp.name == "manifest.json":
            continue
        d = json.loads(jp.read_text())
        items.append(
            Item(
                input_path=d["input_path"],
                input_type=d["input_type"],
                scores=d["scores"],
            )
        )
    return items


def _load_gold() -> dict[str, dict[str, int]]:
    """Returns {input_path -> {dimension -> score}} for every gold file present."""
    gold: dict[str, dict[str, int]] = {}
    if not GOLD_DIR.exists():
        return gold
    for jp in sorted(GOLD_DIR.rglob("*.json")):
        d = json.loads(jp.read_text())
        ip = d.get("input_path")
        if not ip:
            continue
        gold[ip] = {
            k: int(v) for k, v in d.get("scores", {}).items() if isinstance(v, (int, float))
        }
    return gold


def _ranks(values: list[float]) -> list[float]:
    """Return the rank of each value, with ties broken by average rank."""
    indexed = sorted(enumerate(values), key=lambda iv: iv[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg_rank
        i = j + 1
    return ranks


def spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 2:
        return None
    rx = _ranks(xs)
    ry = _ranks(ys)
    mx = statistics.mean(rx)
    my = statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry, strict=True))
    den = (
        (sum((a - mx) ** 2 for a in rx) ** 0.5)
        * (sum((b - my) ** 2 for b in ry) ** 0.5)
    )
    if den == 0:
        return None
    return num / den


def _format_dist(values: list[int]) -> str:
    if not values:
        return "n=0"
    mean = statistics.mean(values)
    median = statistics.median(values)
    return f"n={len(values)}  mean={mean:.2f}  median={median:.1f}"


def build_report(items: list[Item], gold: dict[str, dict[str, int]]) -> str:
    lines: list[str] = ["# portico eval report", ""]

    lines.append(f"Inputs judged: {len(items)}")
    lines.append("")

    # Per-dimension distribution.
    lines.append("## Per-dimension distribution")
    lines.append("")
    lines.append("| Dimension | Stats |")
    lines.append("| --- | --- |")
    for dim in DIMENSIONS:
        vals = [it.scores[dim] for it in items if dim in it.scores]
        lines.append(f"| {dim} | {_format_dist(vals)} |")
    lines.append("")

    # Per-input-type breakdown.
    types = sorted({it.input_type for it in items})
    if types:
        lines.append("## Per-input-type breakdown")
        lines.append("")
        header = "| type | n | " + " | ".join(DIMENSIONS) + " |"
        sep = "| --- | --- | " + " | ".join(["---"] * len(DIMENSIONS)) + " |"
        lines.append(header)
        lines.append(sep)
        for t in types:
            sub = [it for it in items if it.input_type == t]
            row = [f"| {t}", f"{len(sub)}"]
            for dim in DIMENSIONS:
                vals = [it.scores[dim] for it in sub if dim in it.scores]
                row.append(f"{statistics.mean(vals):.2f}" if vals else "-")
            lines.append(" | ".join(row) + " |")
        lines.append("")

    # Spearman vs gold.
    lines.append("## Spearman correlation vs gold annotations")
    lines.append("")
    if not gold:
        lines.append("_No gold annotations found at `tests/eval/gold/`. Add hand-scored")
        lines.append("JSON files there to enable judge-vs-human calibration._")
        lines.append("")
    else:
        paired_items = [it for it in items if it.input_path in gold]
        lines.append(f"Paired (judge ∩ gold): {len(paired_items)} of {len(items)}")
        lines.append("")
        lines.append("| Dimension | Spearman | n |")
        lines.append("| --- | --- | --- |")
        for dim in DIMENSIONS:
            xs = []
            ys = []
            for it in paired_items:
                g = gold.get(it.input_path, {})
                if dim in it.scores and dim in g:
                    xs.append(float(it.scores[dim]))
                    ys.append(float(g[dim]))
            corr = spearman(xs, ys)
            corr_str = f"{corr:.3f}" if corr is not None else "—"
            flag = "  ⚠ drift" if corr is not None and corr < 0.4 else ""
            lines.append(f"| {dim} | {corr_str}{flag} | {len(xs)} |")
        lines.append("")
        lines.append(
            "_Drift threshold: 0.4 (per llm-as-judge.md); below this the judge is unreliable._"
        )
        lines.append("")

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="report", description=(__doc__ or "").splitlines()[0]
    )
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args(argv)

    judgments_dir = JUDGMENTS_DIR / args.run_id
    if not judgments_dir.exists():
        print(f"error: judgments dir not found: {judgments_dir}", file=sys.stderr)
        return 1

    items = _load_judgments(judgments_dir)
    gold = _load_gold()
    report = build_report(items, gold)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORTS_DIR / f"{args.run_id}.md"
    out.write_text(report)
    print(f"wrote {out}")
    print()
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
