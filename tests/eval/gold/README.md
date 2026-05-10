# Gold annotations

Hand-scored reference judgments used to calibrate the LLM judge.

`tests/eval/report.py` reads every `*.json` under this directory and (when an
input is present in both gold and judge output) computes Spearman correlation
between the LLM judge and the human gold scores per dimension. A correlation
below **0.4** flags judge drift -- per `wiki/llm-as-judge.md` G-Eval's reported
0.514 with humans is the target floor.

## File format

One file per annotated input, named after the input it scores. Mirror the
`inputs/` directory layout:

```
gold/
├── essay/
│   ├── 01_trust_at_scale.json
│   └── 02_dynamic_parking.json
├── codebase/
│   └── 01_repo_tree.json
└── ...
```

Each file:

```json
{
  "input_path": "essay/01_trust_at_scale.txt",
  "scores": {
    "faithfulness": 5,
    "distinctness": 4,
    "non_vacuity": 5,
    "layer_appropriateness": 4,
    "label_quality": 5
  },
  "annotator": "tom",
  "notes": "Optional. Why these scores; what was hard to judge; ambiguities."
}
```

`input_path` MUST match the value `judge.py` writes (the relative path under
`inputs/`). Scores are integers 1–5. Missing dimensions are allowed and skipped
in correlation.

## Workflow

1. Run `run_eval.py` then `judge.py` on a run.
2. Pick ~5 inputs you have strong opinions about.
3. Open the JSON structure (`outputs/runs/{run_id}/{type}/{name}.json`) and the
   input text side by side, score each dimension 1–5 by hand against the rubric
   in `judge.py`'s `DIMENSION_DEFS`.
4. Save the file under `gold/{type}/{name}.json`.
5. Re-run `report.py` -- the Spearman row populates once you have ≥2 paired
   inputs per dimension.

Target gold-set size: **30–50 inputs**, stratified across types. Lower agreement
on `non_vacuity` and `layer_appropriateness` than on `faithfulness` is normal
and expected (per `evaluation-rubric.md`).
