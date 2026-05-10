"""Run portico against the eval input set; save JSON + ASCII bundles per input.

Usage:
    uv run python -m tests.eval.run_eval                # run all inputs
    uv run python -m tests.eval.run_eval --type essay   # filter by type
    uv run python -m tests.eval.run_eval --max 5        # cap input count
    uv run python -m tests.eval.run_eval --run-id rXX   # name the run; default = timestamp

Outputs land at tests/eval/outputs/runs/{run_id}/{type}/{input_name}.{json,txt}
plus a manifest.json with run metadata. Re-running with the same --run-id skips
inputs that already have output (resumable).

Generator config (locked for evals -- see tests/eval/README.md):
- Model: claude-sonnet-4-6
- Extended thinking: enabled, xhigh effort (32k token budget)
This is heavier than the default CLI behavior (no thinking) and reflects the
quality target we want to measure against, not the cost-optimized config.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from portico.analyzer import F4MalformedJSON, analyze
from portico.config import get_anthropic_api_key, get_default_model
from portico.providers.base import ProviderAuthError, ProviderTransportError
from portico.providers.claude import DEFAULT_MODEL, THINKING_EFFORT, ClaudeProvider
from portico.render import render

EVAL_THINKING_EFFORT = "xhigh"

EVAL_DIR = Path(__file__).parent
INPUTS_DIR = EVAL_DIR / "inputs"
OUTPUTS_DIR = EVAL_DIR / "outputs" / "runs"


@dataclass
class RunResult:
    input_path: str
    input_type: str
    status: str  # "ok" | "f4_malformed" | "auth" | "transport" | "skipped"
    attempts: int = 0
    error: str = ""
    elapsed_s: float = 0.0


def discover_inputs(type_filter: str | None) -> list[Path]:
    """Walk inputs/{type}/*.txt; optionally filter by type."""
    if not INPUTS_DIR.exists():
        return []
    inputs: list[Path] = []
    for type_dir in sorted(INPUTS_DIR.iterdir()):
        if not type_dir.is_dir():
            continue
        if type_filter and type_dir.name != type_filter:
            continue
        inputs.extend(sorted(type_dir.glob("*.txt")))
    return inputs


def run_one(
    input_path: Path,
    *,
    provider: ClaudeProvider,
    model: str,
    output_dir: Path,
) -> RunResult:
    type_name = input_path.parent.name
    rel = f"{type_name}/{input_path.name}"
    out_subdir = output_dir / type_name
    out_subdir.mkdir(parents=True, exist_ok=True)
    json_path = out_subdir / f"{input_path.stem}.json"
    txt_path = out_subdir / f"{input_path.stem}.txt"

    if json_path.exists() and txt_path.exists():
        return RunResult(input_path=rel, input_type=type_name, status="skipped")

    text = input_path.read_text()
    t0 = time.monotonic()
    try:
        result = analyze(text, provider=provider, model=model)
    except F4MalformedJSON as e:
        return RunResult(
            input_path=rel,
            input_type=type_name,
            status="f4_malformed",
            error=str(e),
            elapsed_s=time.monotonic() - t0,
        )
    except ProviderAuthError as e:
        return RunResult(
            input_path=rel,
            input_type=type_name,
            status="auth",
            error=str(e),
            elapsed_s=time.monotonic() - t0,
        )
    except ProviderTransportError as e:
        return RunResult(
            input_path=rel,
            input_type=type_name,
            status="transport",
            error=str(e),
            elapsed_s=time.monotonic() - t0,
        )

    elapsed = time.monotonic() - t0
    json_path.write_text(json.dumps(result.data.model_dump(mode="json"), indent=2) + "\n")
    txt_path.write_text(render(result.data, width=80))
    return RunResult(
        input_path=rel,
        input_type=type_name,
        status="ok",
        attempts=result.attempts,
        elapsed_s=elapsed,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="run_eval", description=(__doc__ or "").splitlines()[0]
    )
    parser.add_argument("--type", help="Filter by input-type subdirectory name.")
    parser.add_argument("--max", type=int, help="Cap the number of inputs to run.")
    parser.add_argument(
        "--run-id",
        default=datetime.now().strftime("%Y%m%dT%H%M%S"),
        help="Run identifier; reused to resume.",
    )
    parser.add_argument("--model", default=get_default_model() or DEFAULT_MODEL)
    args = parser.parse_args(argv)

    if not get_anthropic_api_key():
        print("error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        return 1

    inputs = discover_inputs(args.type)
    if args.max:
        inputs = inputs[: args.max]
    if not inputs:
        print(f"no inputs found under {INPUTS_DIR}", file=sys.stderr)
        return 1

    output_dir = OUTPUTS_DIR / args.run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    provider = ClaudeProvider(
        api_key=get_anthropic_api_key(),
        thinking_budget=THINKING_EFFORT[EVAL_THINKING_EFFORT],
    )
    results: list[RunResult] = []
    for i, ip in enumerate(inputs, 1):
        print(f"[{i}/{len(inputs)}] {ip.parent.name}/{ip.name}", flush=True)
        res = run_one(ip, provider=provider, model=args.model, output_dir=output_dir)
        results.append(res)
        if res.status not in ("ok", "skipped"):
            print(f"  -> {res.status}: {res.error}", flush=True)

    manifest = {
        "run_id": args.run_id,
        "model": args.model,
        "thinking_effort": EVAL_THINKING_EFFORT,
        "thinking_budget": THINKING_EFFORT[EVAL_THINKING_EFFORT],
        "started_at": datetime.now().isoformat(),
        "inputs_total": len(inputs),
        "by_status": {
            s: sum(1 for r in results if r.status == s)
            for s in ("ok", "skipped", "f4_malformed", "auth", "transport")
        },
        "results": [asdict(r) for r in results],
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"\nrun complete: {output_dir}")
    print(f"  ok: {manifest['by_status']['ok']}, "
          f"skipped: {manifest['by_status']['skipped']}, "
          f"errors: {sum(manifest['by_status'][s] for s in ('f4_malformed', 'auth', 'transport'))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
