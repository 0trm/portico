# arqii eval inputs

Stratified eval set, organised by input type per
[`wiki/input-taxonomy.md`](../../../../../Library/Mobile%20Documents/iCloud~md~obsidian/Documents/arqii/wiki/input-taxonomy.md).

```
inputs/
├── essay/             # opinion / argument essays (good fit)
├── academic_paper/    # IMRAD / abstracts (good fit)
├── codebase/          # multi-file repo trees (good fit)
├── source_file/       # single-file code (stretched)
├── readme/            # READMEs / docs (good)
├── business_plan/     # pitches, plans (good)
├── rfc/               # technical specs (excellent)
├── transcript/        # threads, conversations (good)
├── news/              # inverted pyramid (good*)
├── fiction/           # short stories (good)
├── poetry/            # poems (stretched)
├── slide_deck/        # decks rendered as text (good)
├── dataset/           # CSV / dataset descriptions (stretched)
├── legal/             # contracts, clauses (good)
└── adversarial/       # gibberish, flat lists, recipes (forced / not_applicable)
```

## Sizing

Starter set is small (~17 inputs) -- enough to exercise the framework and
exercise each type at least once. Per `wiki/evaluation-rubric.md` the production
target is **100 inputs** (8 per type × 13 types), grow to 250 as the system
matures. Add inputs incrementally; every production failure should become a new
eval item.

## Adding a new input

1. Pick the type subdirectory.
2. Write a short text file (`<NN>_<short_name>.txt`); content typically 100–500
   words is enough. Keep it under 8KB so the judge prompts stay reasonable.
3. The next `run_eval.py` invocation will pick it up automatically.
