"""G-Eval judge: score generated porticos on the 5-dimension rubric.

Usage:
    uv run python -m tests.eval.judge --run-id <id>

Reads tests/eval/outputs/runs/{run_id}/ (must already contain JSON outputs from
run_eval.py) and writes per-input scores to tests/eval/outputs/judgments/{run_id}/.

Defaults to OpenAI gpt-4o for judging (different model family from the Claude
generator, per llm-as-judge.md). Override via JUDGE_PROVIDER and JUDGE_MODEL env
vars: JUDGE_PROVIDER in {openai, claude, ollama}, JUDGE_MODEL the model name.
For ollama, JUDGE_BASE_URL also overrides the daemon URL (default
http://localhost:11434/v1).

The 5 dimensions (Faithfulness, Distinctness, Non-vacuity, Layer-appropriateness,
Label quality) are scored 1-5 with auto-CoT "evaluation steps" preceding the
score, per Liu et al. 2023.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from arqii.providers.base import LLMProvider, ProviderAuthError, ProviderTransportError
from arqii.providers.claude import ClaudeProvider
from arqii.providers.openai import OpenAIProvider

EVAL_DIR = Path(__file__).parent
RUNS_DIR = EVAL_DIR / "outputs" / "runs"
JUDGMENTS_DIR = EVAL_DIR / "outputs" / "judgments"

DIMENSIONS = (
    "faithfulness",
    "distinctness",
    "non_vacuity",
    "layer_appropriateness",
    "label_quality",
)

JUDGE_PROMPT = """\
You are evaluating an arqii portico, a 3-layer hierarchical decomposition of an
input into roof / pillars / base. Score the portico on ONE dimension. Use a
1-5 integer scale (1 = poor, 5 = excellent). Length is NOT a quality signal.

Dimension: {dimension_name}
Definition: {dimension_def}

Evaluation Steps (think step by step before scoring):
{evaluation_steps}

INPUT TEXT:
---
{input_text}
---

PORTICO (JSON):
---
{portico_json}
---

Now write a short reasoning paragraph (under 80 words), then on a new line
write exactly: SCORE: <integer 1-5>
"""

DIMENSION_DEFS: dict[str, str] = {
    "faithfulness": (
        "Are the labels and summaries supported by the input? Each claim in the "
        "summaries should be entailed by, or directly extractable from, the input."
    ),
    "distinctness": (
        "Are the pillars MECE (mutually exclusive, collectively exhaustive)? Do "
        "any two pillars overlap conceptually? Lower the score by the worst pair."
    ),
    "non_vacuity": (
        "Could this portico apply to many other inputs of the same type, or is it "
        "specific to THIS input? Generic, swappable porticos score low."
    ),
    "layer_appropriateness": (
        "Does the roof unify the whole input (not just topic-restate)? Are the "
        "pillars load-bearing structural elements? Is the base genuinely "
        "foundational (preconditions / substrate), not just background detail?"
    ),
    "label_quality": (
        "Are labels concise (≤16 chars), distinctive, noun-phrase-like? Are "
        "summaries 1-2 sentences? Do labels match what their summaries describe?"
    ),
}

DIMENSION_STEPS: dict[str, str] = {
    "faithfulness": (
        "1. List 3-5 atomic claims from the roof, pillars, and base summaries.\n"
        "2. For each claim, check whether the input text supports it.\n"
        "3. Score: 5 if all claims supported; 1 if multiple claims are unsupported "
        "or contradicted."
    ),
    "distinctness": (
        "1. List the pillar labels.\n"
        "2. For each pair (pillar_i, pillar_j), check whether they could overlap.\n"
        "3. Identify the worst pair.\n"
        "4. Score: 5 if pairs are clearly disjoint; 1 if multiple pairs overlap."
    ),
    "non_vacuity": (
        "1. Imagine the roof / pillars / base swapped with another input of the "
        "same type but different content.\n"
        "2. Would the portico still be plausible? If yes, vacuity is high.\n"
        "3. Score: 5 if the portico is clearly THIS input's; 1 if it could fit "
        "almost any input of the type."
    ),
    "layer_appropriateness": (
        "1. Roof: does it unify the whole input?\n"
        "2. Pillars: are they load-bearing components, not topical groupings?\n"
        "3. Base: is it foundational (preconditions / substrate), not background?\n"
        "4. Score: 5 if all three roles are clean; 1 if a layer is misused."
    ),
    "label_quality": (
        "1. Check label lengths (target ≤16 chars).\n"
        "2. Check label-summary correspondence.\n"
        "3. Check that labels are noun-phrase-like, not full sentences.\n"
        "4. Score: 5 if all labels follow the conventions; 1 if conventions are "
        "broken throughout."
    ),
}


@dataclass
class DimensionScore:
    dimension: str
    score: int
    reasoning: str


@dataclass
class Judgment:
    input_path: str
    input_type: str
    scores: dict[str, int]
    reasoning: dict[str, str]
    judge_provider: str
    judge_model: str


OLLAMA_DEFAULT_BASE_URL = "http://localhost:11434/v1"
OLLAMA_DEFAULT_MODEL = "qwen2.5:7b"


def _make_judge() -> tuple[LLMProvider, str, str]:
    name = os.environ.get("JUDGE_PROVIDER", "openai").lower()
    if name == "openai":
        from arqii.providers.openai import DEFAULT_MODEL as OPENAI_DEFAULT_MODEL

        if not os.environ.get("OPENAI_API_KEY"):
            raise SystemExit("error: OPENAI_API_KEY not set")
        provider: LLMProvider = OpenAIProvider()
        model = os.environ.get("JUDGE_MODEL", OPENAI_DEFAULT_MODEL)
        return provider, name, model
    if name == "claude":
        from arqii.config import get_anthropic_api_key
        from arqii.providers.claude import DEFAULT_MODEL as CLAUDE_DEFAULT_MODEL

        api_key = get_anthropic_api_key()
        if not api_key:
            raise SystemExit("error: ANTHROPIC_API_KEY not set")
        provider = ClaudeProvider(api_key=api_key)
        model = os.environ.get("JUDGE_MODEL", CLAUDE_DEFAULT_MODEL)
        return provider, name, model
    if name == "ollama":
        base_url = os.environ.get("JUDGE_BASE_URL", OLLAMA_DEFAULT_BASE_URL)
        model = os.environ.get("JUDGE_MODEL", OLLAMA_DEFAULT_MODEL)
        provider = OpenAIProvider(api_key="ollama", base_url=base_url)
        return provider, name, model
    raise SystemExit(
        f"error: JUDGE_PROVIDER={name!r} not supported (use openai, claude, or ollama)"
    )


def _parse_score(text: str) -> tuple[int, str]:
    """Extract a 1-5 score from the judge's response. Returns (score, reasoning).

    Accepts SCORE: N, Score: N, or `**Score:** N`. Falls back to the LAST 1-5
    integer in the text so weaker judges that bury the score in prose still parse.
    """
    m = re.search(r"\*?\*?[Ss][Cc][Oo][Rr][Ee]\*?\*?\s*:\s*\*?\*?\s*([1-5])\b", text)
    if m:
        return int(m.group(1)), text[: m.start()].strip()

    # Fallback: last 1-5 digit in the text. Brittle but better than crashing.
    matches = list(re.finditer(r"\b([1-5])\b", text))
    if matches:
        last = matches[-1]
        return int(last.group(1)), text[: last.start()].strip()

    raise ValueError(f"judge response missing parseable score:\n{text}")


def judge_one(
    input_text: str,
    portico_json: dict,
    *,
    provider: LLMProvider,
    model: str,
) -> tuple[dict[str, int], dict[str, str]]:
    portico_str = json.dumps(portico_json, indent=2)
    scores: dict[str, int] = {}
    reasoning: dict[str, str] = {}
    for dim in DIMENSIONS:
        prompt = JUDGE_PROMPT.format(
            dimension_name=dim,
            dimension_def=DIMENSION_DEFS[dim],
            evaluation_steps=DIMENSION_STEPS[dim],
            input_text=input_text[:8000],  # cap to keep prompts reasonable
            portico_json=portico_str,
        )
        text = provider.generate(prompt, model=model)
        score, why = _parse_score(text)
        scores[dim] = score
        reasoning[dim] = why
    return scores, reasoning


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="judge", description=(__doc__ or "").splitlines()[0]
    )
    parser.add_argument("--run-id", required=True, help="Run id under outputs/runs/.")
    parser.add_argument("--max", type=int, help="Cap inputs (for testing).")
    args = parser.parse_args(argv)

    run_dir = RUNS_DIR / args.run_id
    if not run_dir.exists():
        print(f"error: run dir not found: {run_dir}", file=sys.stderr)
        return 1

    inputs_dir = EVAL_DIR / "inputs"
    json_files = sorted(run_dir.rglob("*.json"))
    json_files = [p for p in json_files if p.name != "manifest.json"]
    if args.max:
        json_files = json_files[: args.max]

    provider, provider_name, model = _make_judge()

    judgments_dir = JUDGMENTS_DIR / args.run_id
    judgments_dir.mkdir(parents=True, exist_ok=True)

    judgments: list[Judgment] = []
    for i, jp in enumerate(json_files, 1):
        type_name = jp.parent.name
        input_text_path = inputs_dir / type_name / f"{jp.stem}.txt"
        if not input_text_path.exists():
            print(f"[{i}/{len(json_files)}] skip {type_name}/{jp.stem} (no input text)", flush=True)
            continue
        out_path = judgments_dir / type_name / f"{jp.stem}.json"
        if out_path.exists():
            print(
                f"[{i}/{len(json_files)}] skip {type_name}/{jp.stem} (already judged)",
                flush=True,
            )
            judgments.append(Judgment(**json.loads(out_path.read_text())))
            continue

        portico = json.loads(jp.read_text())
        input_text = input_text_path.read_text()
        print(f"[{i}/{len(json_files)}] judging {type_name}/{jp.stem}", flush=True)
        t0 = time.monotonic()
        try:
            scores, reasoning = judge_one(
                input_text, portico, provider=provider, model=model
            )
        except (ProviderAuthError, ProviderTransportError) as e:
            print(f"  -> provider error: {e}", flush=True)
            return 2
        print(f"  scores={scores} ({time.monotonic() - t0:.1f}s)", flush=True)

        judgment = Judgment(
            input_path=f"{type_name}/{jp.stem}.txt",
            input_type=type_name,
            scores=scores,
            reasoning=reasoning,
            judge_provider=provider_name,
            judge_model=model,
        )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(judgment.__dict__, indent=2) + "\n")
        judgments.append(judgment)

    summary = {
        "run_id": args.run_id,
        "judge_provider": provider_name,
        "judge_model": model,
        "judged_at": datetime.now().isoformat(),
        "inputs_total": len(json_files),
        "judgments_count": len(judgments),
    }
    (judgments_dir / "manifest.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"\nwrote {len(judgments)} judgments to {judgments_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
