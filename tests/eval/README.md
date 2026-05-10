# portico eval

Three-stage pipeline that measures structure quality:

```
inputs/  ──run_eval──>  outputs/runs/  ──judge──>  outputs/judgments/  ──report──>  outputs/reports/
                                                          │
                                                          └── compared against ──>  gold/  (hand-scored)
```

Stages are decoupled by `--run-id`. Re-running with the same id is resumable;
already-completed work is skipped.

## Generator config (locked)

| Setting           | Value                  | Why                                                                                       |
| ----------------- | ---------------------- | ----------------------------------------------------------------------------------------- |
| Model             | `claude-sonnet-4-6`    | Current default for the analyzer; pinned in `portico.providers.claude.DEFAULT_MODEL`        |
| Extended thinking | enabled                | Hard inputs (adversarial, mixed-genre, ambiguous fit) reward deeper deliberation          |
| Effort            | `xhigh` (32k budget)   | We want the quality ceiling, not the cost-optimized floor                                 |

Constants live in `portico.providers.claude.THINKING_EFFORT` (`low: 2048`,
`medium: 4096`, `high: 8192`, `xhigh: 32000`). The eval-default is set by
`EVAL_THINKING_EFFORT` at the top of `run_eval.py`. The CLI (`portico ...`) does
not enable thinking by default -- it stays cheap. Eval is the heavy mode.

The choice is recorded in every run's `manifest.json` (`thinking_effort`,
`thinking_budget` fields) so old vs new runs can be told apart.

## Judge config (current)

| Setting   | Default              | Override via                        |
| --------- | -------------------- | ----------------------------------- |
| Provider  | `openai` (`gpt-4o`)  | `JUDGE_PROVIDER`                    |
| Model     | provider default     | `JUDGE_MODEL`                       |
| Base URL  | provider default     | `JUDGE_BASE_URL` (ollama only)      |

Local-OSS judging is supported: `JUDGE_PROVIDER=ollama` (default model
`qwen2.5:7b`). 7B sits below G-Eval's reported 0.514 floor for human
correlation -- expect leniency bias on the upper end of the scale. Calibrate
with gold annotations before trusting absolute scores.

## Workflow

```bash
# 1. Generate (Claude analyzer with xhigh thinking)
op run --env-file=.env -- arch -arm64 uv run python -m tests.eval.run_eval --run-id r02

# 2. Judge (local Ollama OR hosted OpenAI)
JUDGE_PROVIDER=ollama uv run python -m tests.eval.judge --run-id r02

# 3. Aggregate
uv run python -m tests.eval.report --run-id r02
```

## Calibrating against gold

Gold annotations measure whether the judge's *ranking* matches yours. Even with
absolute leniency, a judge that ranks structures in the same order you do is
useful; one that doesn't is broken. See `gold/README.md` for the format.

Drift threshold: **Spearman < 0.4** flags an unreliable judge per dimension
(per `wiki/llm-as-judge.md`).
