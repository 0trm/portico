> Take any input. See its layered shape as a classical [[structure]].

---

## 1. What it is

`portico` converts an arbitrary input (text, code, URL, repo) into a **structure** — a three-layer ASCII/Unicode visualization with the structure of a Greek/Roman temple front:

```
        roof       ← the apex / unifying idea
        ──────
   ║ ║ ║ ║ ║ ║   ← pillars (variable count, the load-bearing parts)
   ──────────
        base       ← the foundation / what everything rests on
```

The **mapping of meaning to layers is free-form**: an LLM inspects the input, decides what kind of thing it is, and decides what `roof`, `pillars`, and `base` should represent for _that_ input.

Examples of what the layers might mean:

|Input type|Roof|Pillars|Base|
|---|---|---|---|
|Essay|Thesis|Supporting arguments|Evidence / premises|
|Codebase|Public API / entry|Core modules|Runtime / dependencies|
|Business plan|Vision|Strategic pillars|Operational foundations|
|Research paper|Conclusion|Findings / methods|Data / prior work|

The user does not pick the mapping. The LLM does, per input.

---

## 2. Form factor

Two surfaces, one engine:

1. **Python package + CLI** — `portico` installable via pip. The package exposes both a Python API and a `portico` shell command. This is where all the work happens.
2. **Claude Code slash command** — `/portico` is a thin wrapper that invokes the CLI from inside Claude Code, with sensible defaults for that environment.

The package is the source of truth. The slash command is ergonomics.

---

## 3. Inputs

`portico` accepts:

|Source|How it's passed|Notes|
|---|---|---|
|Raw text|`portico "some text"` or stdin|`cat foo \| portico`|
|Local file|`portico path/to/file`|Supports `.txt`, `.md`, `.rtf`, source code|
|Local dir|`portico path/to/dir`|Treated as a codebase / project|
|URL|`portico https://example.com/article`|Fetches and uses page content|
|Git repo|`portico https://github.com/user/repo`|Clones (shallow) or uses API|

Auto-detection determines which mode applies. Explicit override available via `--type {text,file,dir,url,repo}`.

### Input size handling

Inputs larger than the model's effective context window are summarized/sampled before being sent to the LLM (strategy: head + tail + structural skeleton for code; head + section headings for text). The user is informed when this happens via a one-line note above the structure.

---

## 4. The LLM call

### Provider abstraction

`portico` supports multiple LLM providers, configurable via flag, env var, or config file:

|Provider|Default model|Env var|
|---|---|---|
|Claude|`claude-sonnet-4` (default)|`ANTHROPIC_API_KEY`|
|OpenAI|(configurable)|`OPENAI_API_KEY`|
|Gemini|(configurable)|`GEMINI_API_KEY`|

Default behavior: when invoked as `/portico` inside Claude Code, use the Claude Code session's Sonnet model (no separate API key required). When invoked as a standalone CLI, use Claude via API key by default.

### What the LLM returns

**Structured JSON only.** This separates "understanding" from "drawing" so the renderer is pure, testable, and replaceable.

```json
{
  "theme": "codebase",
  "title": "my-repo",
  "roof": {
    "label": "Public API",
    "summary": "What external callers depend on."
  },
  "pillars": [
    { "label": "Auth",      "summary": "JWT issuance & validation."     },
    { "label": "Routing",   "summary": "Request dispatch & middleware." },
    { "label": "Storage",   "summary": "Postgres + Redis access layer." }
  ],
  "base": {
    "label": "Runtime",
    "summary": "Python 3.12, FastAPI, asyncio."
  }
}
```

### Constraints the LLM must follow

- **Pillar count: 2–9.** Fewer than 2 isn't a structure; more than 9 doesn't render legibly.
- **Labels are short.** Target ≤ 16 characters per label. The renderer truncates with `…` if longer.
- **Summaries are one sentence.** Used in `--verbose` legend, not in the structure itself.
- **`theme` is a free-form short string** the LLM picks (e.g., `essay`, `codebase`, `argument`, `business-plan`). It may be displayed in the title bar.

A schema-validated retry loop handles malformed responses (max 2 retries).

---

## 5. Output

A static, single-shot render to stdout:

```
── codebase: my-repo ──────────────────────────────

           [ structure render ]

```

### What goes inside each element

- **Inside the structure:** labels only (terse).
- **Below the structure (with `--verbose`):** a legend listing each element's label + summary.

### Sizing

- Up to **9 pillars** maximum.
- The renderer detects terminal width (`shutil.get_terminal_size()`).
- Width is capped at a sensible maximum (default 100 cols) regardless of terminal width.
- If the rendered structure would exceed terminal width, the renderer shrinks pillar width / spacing before truncating labels.

### Color

- **No color by default.**
- `--color {auto,always,never}` toggles ANSI color output.
- When color is on, each layer (roof / pillars / base) gets a distinct accent. Color never carries semantic meaning the user must decode.

### Visual style

To be decided. The renderer is built to support multiple styles selectable via `--style <name>`, with one as the default. Styles are static files / pure functions — adding a new one does not touch the LLM layer.

---

## 6. CLI surface

```
portico [INPUT] [OPTIONS]

Inputs (one of):
  INPUT                       Path, URL, or raw text. Or pipe via stdin.
  --type {text,file,dir,url,repo}   Override auto-detection.

Output:
  --style <name>              Visual style for the structure.
  --color {auto,always,never} ANSI color. Default: never.
  --verbose, -v               Add legend with summaries below the structure.
  --width <cols>              Override max width (default: min(terminal, 100)).
  --json                      Emit the LLM's JSON instead of rendering. Useful for piping.

Model:
  --provider {claude,openai,gemini}
  --model <name>              Override default model for the chosen provider.

Misc:
  --no-cache                  Skip cache lookup.
  --version
  --help
```

### Examples

```bash
portico README.md
portico ./src --verbose
cat essay.txt | portico --style fluted --color always
portico https://github.com/user/repo --json | jq .pillars
/portico @file.py            # inside Claude Code
```

---

## 7. Architecture

```
┌──────────────┐    ┌────────────┐    ┌──────────────┐    ┌──────────┐
│   Loader     │ →  │ Summarizer │ →  │   Analyzer   │ →  │ Renderer │
│ (text/file/  │    │ (if input  │    │ (LLM call,   │    │ (JSON →  │
│  url/repo)   │    │  too big)  │    │  → JSON)     │    │  ASCII)  │
└──────────────┘    └────────────┘    └──────────────┘    └──────────┘
                                              ↓
                                        ┌──────────┐
                                        │  Cache   │
                                        └──────────┘
```

Module layout (proposed):

```
portico/
├── __init__.py
├── cli.py              # argparse / typer entry point
├── loaders/
│   ├── text.py
│   ├── file.py
│   ├── dir.py
│   ├── url.py
│   └── repo.py
├── summarize.py        # context-window-fitting strategies
├── providers/
│   ├── base.py         # LLMProvider ABC
│   ├── claude.py
│   ├── openai.py
│   └── gemini.py
├── analyzer.py         # builds prompt, calls provider, validates JSON
├── schema.py           # Pydantic models for the JSON contract
├── render/
│   ├── base.py         # StructureRenderer ABC
│   ├── styles/         # one file per style
│   └── color.py
├── cache.py            # content-hash → JSON cache
└── config.py           # config file + env var resolution
```

### Caching

Inputs are hashed (content + provider + model). Repeated runs on the same input hit the cache and skip the LLM call. Cache lives in `~/.cache/portico/`.

---

## 8. Configuration

In priority order (later overrides earlier):

1. Built-in defaults
2. `~/.config/portico/config.toml`
3. Environment variables (`ARQII_PROVIDER`, `ARQII_MODEL`, etc.)
4. CLI flags

---

## 9. Out of scope for v1

These are explicitly deferred:

- **Recursion.** A pillar zooming into its own sub-structure. Worth testing post-v1; the JSON schema should be designed so a `pillars[].sub_structure` field can be added without breaking changes.
- **Interactive TUI.** Static render only. No navigation, no expand-on-click.
- **Image / SVG export.** Terminal-native only.
- **Multi-language UI.** English only.
- **Streaming render.** Output is computed in full, then printed.

---

## 10. Open decisions

The following remain to be decided before implementation:

- **Visual style(s) to ship in v1** — the default and any alternates. Five candidates were sketched; the call is open.
- **Label placement** — inside the pillar (vertical or short code) vs. underneath the pillar.
- **Title-bar format** — how prominently to display the LLM-detected theme and the input identifier.
- **Cache eviction policy** — TTL, size cap, or manual-only.
- **Exact prompt** sent to the LLM, including how strictly the JSON contract is enforced and what guidance is given for picking a `theme`.

---

## 11. Success criteria for v1

- Running `portico` on a typical input (under ~5k tokens) returns a structure in under 5 seconds end-to-end.
- The same input produces the same structure (cache hit) instantly on subsequent runs.
- The structure renders correctly in a standard 80-column terminal without truncation artifacts.
- A user can swap providers (`--provider openai`) without other changes and get a comparable result.
- The renderer is fully tested without any LLM calls (JSON fixtures → expected ASCII).

---
## 12. Edge cases & failure modes

`portico` runs against arbitrary inputs, which means it will routinely encounter content that resists 3-layer decomposition. The system must fail in ways that are honest, predictable, and useful. This section enumerates the failure classes and specifies the response for each.

### Design principles

Three rules govern every edge case in this section:

1. **Honesty over coverage.** A bad structure is worse than no structure. When the metaphor doesn't fit, say so.
2. **Useful failure.** Every refusal must tell the user _what_ failed and _what they could do about it_. No silent exits, no generic errors.
3. **Single exit channel.** All failure modes terminate in one of three states — `rendered`, `rendered_with_caveat`, or `refused` — surfaced via exit code and structured output. No hidden third paths.

### Failure taxonomy

Failures fall into four classes, ordered roughly by where in the pipeline they occur:

|Class|Stage|Example|Response|
|---|---|---|---|
|F1|Input access|URL 404, file not found, repo private|refuse, exit ≠ 0|
|F2|Input parsing|Binary blob, encrypted PDF, empty file|refuse, exit ≠ 0|
|F3|Content fit|Flat list, single line, gibberish|refuse with reason, exit 0|
|F4|Decomposition|LLM returns malformed JSON, fit forced|retry, then caveat or refuse|

Classes F1 and F2 are _technical_ failures — the input never reached the LLM. Classes F3 and F4 are _semantic_ failures — the LLM saw the input but couldn't or shouldn't produce a useful structure.

### F1 — Input access failures

Input cannot be read at all. The system never reaches the analyzer.

|Condition|Behavior|
|---|---|
|File path does not exist|`error: no input found at <path>` — exit code 2|
|File path exists but is unreadable|`error: cannot read <path>: permission denied` — exit code 2|
|URL returns non-2xx|`error: <url> returned <status>` — exit code 3|
|URL times out|`error: <url> did not respond within <N>s` — exit code 3|
|Git repo private / 404|`error: cannot access <repo>` — exit code 3|
|Git clone fails|`error: git clone failed: <reason>` — exit code 3|
|Stdin closed with no input|`error: no input on stdin` — exit code 2|
|Network disabled, URL given|`error: network access required for URL inputs` — exit code 4|

All F1 errors print to stderr. Stdout is empty. No JSON is emitted. No LLM call is made.

### F2 — Input parsing failures

Input was retrieved but cannot be turned into something the LLM can read.

|Condition|Behavior|
|---|---|
|Binary file with no extractable text|`error: <path> appears to be binary; portico does not support this format` — exit 5|
|Encrypted / password-protected file|`error: <path> is encrypted` — exit 5|
|Empty file or zero-byte input|`error: input is empty` — exit 5|
|Unsupported file type (e.g., `.psd`, `.dwg`)|`error: file type <ext> is not supported` — exit 5, lists supported types|
|Directory contains no readable files|`error: <dir> contains no readable files` — exit 5|
|URL fetched but readability extraction empty|`error: could not extract readable content from <url>` — exit 5|
|Input exceeds hard upper bound (see §below)|`error: input exceeds maximum size; consider --type override or summarization` — exit 6|

All F2 errors print to stderr. Same contract as F1: stdout empty, no JSON, no LLM call.

#### Size limits

`portico` enforces an upper bound on input size _before_ any summarization is attempted:

- **Soft cap:** ~50,000 tokens estimated. Above this, the summarization step in §3 kicks in.
- **Hard cap:** ~5,000,000 tokens estimated. Above this, refuse with F2 error code 6.

The hard cap exists to prevent runaway cost on accidental inputs (e.g., piping a 2GB log file). Configurable via `--max-tokens`.

### F3 — Content does not fit the structure

The input was successfully read and sent to the LLM, but the LLM determines (per the schema's `fit_quality` field) that no useful 3-layer decomposition exists.

The LLM's JSON contract includes:

```json
{
  "fit_quality": "good" | "stretched" | "forced" | "not_applicable",
  "notes_on_fit": "..."
}
```

Behavior depends on `fit_quality`:

|Value|Default behavior|Override|
|---|---|---|
|`good`|Render the structure normally|—|
|`stretched`|Render, with a one-line caveat above the structure|`--strict` makes this F3|
|`forced`|Refuse by default, show `notes_on_fit`|`--force` renders anyway|
|`not_applicable`|Refuse, show `notes_on_fit`|`--force` is ignored here|

When refusing on F3, exit code is **0** (this is a successful run that produced a deliberate non-result), and a structured message is printed:

```
portico could not build a structure for this input.

reason: <notes_on_fit from the LLM>

input type detected: <theme>

what you can try:
  • run with --force to render anyway (output may be vacuous)
  • narrow the input (a section, a single file) and try again
  • verify the input is what you intended
```

The `--json` flag still emits the LLM's full JSON output even on F3, so downstream tools can introspect the refusal.

#### What counts as `not_applicable`

The LLM is instructed to return `not_applicable` only when the input is one of:

- Effectively empty (whitespace, single token, gibberish without structure)
- A flat enumeration with no internal hierarchy (a glossary, a list of links, a CSV with no description)
- So short that any 3-layer decomposition would be trivial (e.g., a tweet, a one-line function)
- Adversarial or non-substantive (random characters, intentional noise)

#### What counts as `forced`

The LLM is instructed to return `forced` when it _can_ produce three layers but doing so requires inventing structure not in the input. Examples:

- A poem where "base" would have to mean something arbitrary
- A dataset where pillars would just be column groupings without semantic load
- A procedural document (recipe, instructions) where the natural shape is sequential, not hierarchical

`forced` is the honest middle: the model is signaling "I built this, but I don't endorse it."

### F4 — Decomposition pipeline failures

The LLM was called but returned something the system cannot use.

|Condition|Behavior|
|---|---|
|Malformed JSON|Retry once with stricter prompt; if still fails, exit 7|
|JSON valid but schema invalid|Retry once; if still fails, exit 7|
|Pillar count outside 2–9|Retry once asking the model to revise; if still fails, exit 7|
|LLM API timeout|Retry once; if still fails, exit 8|
|LLM API rate limit|Wait + retry per provider's `retry-after`; max 2 retries|
|LLM API auth failure|`error: <provider> authentication failed` — exit 9|
|LLM API quota exceeded|`error: <provider> quota exceeded` — exit 9|
|Network failure mid-call|Retry once; if still fails, exit 8|
|Provider returns refusal / safety stop|Render the refusal as F3 `not_applicable` with the provider's reason as `notes_on_fit`|

F4 retries are bounded: **maximum 2 retries per call, no recursion, no exponential explosion**. After retries are exhausted, the system fails cleanly with the appropriate exit code.

### Exit code summary

```
0   success (rendered, rendered_with_caveat, or deliberate F3 refusal)
1   reserved (generic error, should not occur)
2   F1: local input not found / unreadable
3   F1: remote input not accessible
4   F1: network required but unavailable
5   F2: input not parseable
6   F2: input exceeds hard size cap
7   F4: LLM returned unusable output after retries
8   F4: LLM call failed (network / timeout)
9   F4: LLM provider auth or quota
```

### Caveat rendering

When `fit_quality` is `stretched` and a structure is rendered anyway, a single caveat line appears immediately above the title bar:

```
note: the structure metaphor is stretched for this input — see --verbose for why.

── poetry: <title> ─────────────────────────────────

           [ structure render ]
```

`--verbose` expands the caveat into the `notes_on_fit` text below the legend.

### Diagnostic flag

`--diagnose` runs the full pipeline but, instead of rendering, prints a structured report:

```
input:        <path or url>
type:         <auto-detected>
size:         <tokens>
loader:       <which loader handled it>
summarized:   <yes/no, original size, summarized size>
provider:     <claude | openai | gemini>
model:        <name>
fit_quality:  <good | stretched | forced | not_applicable>
notes_on_fit: <text>
```

This is the user's first stop when something feels wrong. It also makes bug reports actionable — a `--diagnose` dump tells a maintainer almost everything needed to reproduce.

### What `portico` will _not_ do

- **Will not silently force a structure** when `fit_quality` is `forced` or `not_applicable`. The `--force` flag exists as an explicit user-side override.
- **Will not invent content** to fill missing layers. If a pillar has no real label, no pillar is rendered — better a 2-pillar structure than a fabricated third.
- **Will not hide LLM uncertainty.** If the model expresses low confidence in `notes_on_fit`, that note is surfaced to the user verbatim.
- **Will not retry indefinitely.** All retry loops are bounded at 2.
- **Will not cache failed runs by default.** F1, F2, and F4 failures are not cached. F3 refusals _are_ cached (the input genuinely doesn't fit; re-running won't change that) but the cache entry can be invalidated with `--no-cache`.

### Open questions for v1

- Should `--force` on `forced` inputs add a watermark to the rendered output (e.g., `[forced render]` in the title bar) so downstream consumers can tell? Likely yes; deferred to implementation.
- Should `not_applicable` ever be overridable? Current spec says no. May relax if real-world usage shows the LLM being too conservative.
- Where does the line between `stretched` and `forced` actually sit? This will be calibrated against the eval set during development, not pre-decided here.