# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`portico` renders an arbitrary input (text, code, URL, repo) as a **portico** -- a three-layer ASCII visualization (`roof` / `pillars` / `base`). An LLM decides what each layer means for that input; the renderer is a pure JSON-to-ASCII function.

The brand is **always lowercase**. The wordmark is `portico`, the mark is `_ii^`. **`portico` is both the product name and the noun for the rendered output** ("render any input as a portico"). Don't capitalize in code, comments, prose, or commit messages.

## Commands

```bash
uv sync                         # install deps
uv run ruff check .             # lint
uv run pyright                  # type-check
uv run pytest                   # mocked tests (live tests auto-skip without ANTHROPIC_API_KEY)
uv run pytest tests/test_cli.py::test_name  # single test
uv run pytest -m "not live"     # skip live tests explicitly
uv run portico README.md        # exercise the CLI on an input
```

## Architecture

The pipeline runs strictly in order, each stage owning one responsibility:

```
Loader -> Summarizer -> Cache -> Analyzer -> Renderer
                                    |
                                    v
                                 (LLM)
```

- **Loaders** (`src/portico/loaders/`) -- one per input type (`text`, `file`, `dir`, `url`, `repo`). All return a `LoadedInput`. Auto-detection lives in `cli.detect_input_type`. Failures raise `F1*` (access) or `F2NotParseable` (parse) exceptions defined in `loaders/base.py`.
- **Summarizer** (`summarize.py`) -- chunks oversized inputs and recursively summarizes via the same provider. `TARGET_CHARS`/`HARD_CAP_CHARS` are char-based proxies for tokens. Hits `F2TooLarge` above the hard cap.
- **Cache** (`cache.py`) -- sha256 of `(text, provider, model)` -> JSON file under `~/.cache/portico/`. F3 refusals are cached; F1/F2/F4 are not.
- **Providers** (`providers/`) -- `LLMProvider` ABC with concrete `claude`, `openai`, `gemini` implementations. Provider failures normalize to `ProviderAuthError` (don't retry) or `ProviderTransportError` (retryable).
- **Analyzer** (`analyzer.py`) -- builds the prompt from `PROMPT_TEMPLATE`, calls the provider, parses + validates JSON against `PorticoJSON`, and retries up to `max_retries` times on `JSONDecodeError`/`ValidationError`. Final failure raises `F4MalformedJSON`.
- **Schema** (`schema.py`) -- `PorticoJSON` is the single LLM contract. The reasoning-first fields (`input_type`, `type_rationale`, `decomposition_strategy`, `scratch_outline`, `mece_check`) come **before** the output fields by design -- they reduce format tax and improve label quality. Don't reorder them.
- **Renderer** (`render/`) -- pure JSON-to-string. `render/__init__.py` is the entry point; `styles/default.py` is the only style implemented; `apex.py` generates the optional ornamental finial; `color.py` handles ANSI. Renderer never touches the LLM.

The CLI (`cli.py`) is the only place that wires stages together and translates exceptions to **exit codes** per the failure taxonomy:

```
0 ok / deliberate refusal   5 F2 not parseable      8 F4 transport
2 F1 not found              6 F2 too large          9 F4 auth/quota
3 F1 remote inaccessible    7 F4 malformed JSON
4 F1 network unavailable
```

`fit_quality` in the schema (`good` | `stretched` | `forced` | `not_applicable`) drives F3 routing in `cli.run`: `not_applicable` always refuses; `forced` refuses unless `--force`; `stretched` renders unless `--strict`. F3 refusals exit 0 -- they are successful runs that produced a deliberate non-result.

## Conventions

- Python 3.12+. Package layout is `src/`-style with `[project.scripts] portico = "portico.cli:main"`.
- ruff selects `E F I B UP SIM RUF`; line length 100. pyright in `standard` mode over `src` and `tests`.
- Live tests are gated by the `live` pytest marker (declared in `pyproject.toml`).
- Env vars for provider/model overrides use the `PORTICO_` prefix (`PORTICO_PROVIDER`, `PORTICO_MODEL`). The product is `portico` everywhere user-facing.
- Prose style: avoid em dashes (`—`); `--` and en dashes (`–`) are fine. Lowercase `portico`. The output noun is also `portico` (not `structure`); reserve "structure" for generic English usage like "structural decomposition" or "the input's internal structure".
