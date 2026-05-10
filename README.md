# portico

Render any input -- text, code, URL, repo -- as a **structure**: a three-layer ASCII visualization (`roof` / `pillars` / `base`).

Pronounced **AR-kee**. Always lowercase. The brand mark is `_ii^`.

## Status

Phase 0 (bootstrap) complete. The package skeleton compiles; no functionality is wired up yet. See the phased roadmap for what lands when.

## Develop

```bash
uv sync                         # install dev deps
uv run ruff check .             # lint
uv run pyright                  # type-check
uv run pytest                   # mocked tests; smoke eval auto-skips
```

The smoke eval (10 live Claude calls + rendered structures in `tests/eval/smoke/report/`) needs `ANTHROPIC_API_KEY`. With the key in 1Password CLI, run via:

```bash
op run --env-file=.env -- arch -arm64 uv run pytest
```

The `arch -arm64` is required because the 1Password CLI is x86_64 and would otherwise force a Rosetta child.
