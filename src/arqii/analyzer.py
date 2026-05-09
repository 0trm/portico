import json
import re
from dataclasses import dataclass

from pydantic import ValidationError

from arqii.providers.base import LLMProvider
from arqii.providers.claude import DEFAULT_MODEL
from arqii.schema import PorticoJSON

PROMPT_TEMPLATE = """\
You are arqii. You decompose any input into a three-layer "portico" structure: a roof \
(the unifying idea), pillars (the load-bearing components), and a base (the foundation \
everything rests on).

Read the input below and emit STRICTLY VALID JSON matching the schema.

The JSON is a SINGLE FLAT OBJECT with these top-level keys, in this exact order. None \
of the keys nest under category headers; do not introduce wrapper objects like \
"reasoning" or "output".

Top-level keys:

1. "input_type": string. What kind of artifact this is (essay, codebase, business plan, ...).
2. "type_rationale": string. One sentence on why you classified it that way.
3. "decomposition_strategy": string. One sentence on how you'll split it into roof / pillars / base.
4. "scratch_outline": array of 3-7 short strings capturing the load-bearing parts before you label.
5. "mece_check": string. One sentence: are the pillars mutually exclusive and collectively \
exhaustive at the same level of abstraction?
6. "theme": string. A short free-form label for the input type ("essay", "codebase", ...).
7. "title": string. The input's title or a 1-3 word identifier.
8. "roof": object {"label": string, "summary": string}. The unifying idea on top.
9. "pillars": array of 2-9 objects, each {"label": string, "summary": string}. STRONGLY PREFER 3-5.
10. "base": object {"label": string, "summary": string}. The foundation that everything rests on.
11. "fit_quality": one of "good", "stretched", "forced", "not_applicable".
12. "notes_on_fit": string. If not "good", explain why in one sentence.

Concrete example of the exact shape (illustrative content; do not copy the values):

{
  "input_type": "essay",
  "type_rationale": "Argumentative prose with thesis and supporting reasoning.",
  "decomposition_strategy": "Thesis on top; two arguments as pillars; evidence at base.",
  "scratch_outline": ["Thesis ...", "Argument 1 ...", "Argument 2 ...", "Evidence ..."],
  "mece_check": "Two pillars are non-overlapping causal mechanisms.",
  "theme": "essay",
  "title": "trust at scale",
  "roof": {"label": "Thesis", "summary": "Small institutions outperform large at trust."},
  "pillars": [
    {"label": "Feedback loops", "summary": "Smaller groups close feedback faster."},
    {"label": "Dunbar limit", "summary": "Diffusion of responsibility past ~150."}
  ],
  "base": {"label": "Evidence", "summary": "Empirical work on team size and trust."},
  "fit_quality": "good",
  "notes_on_fit": "Essay decomposes cleanly into thesis / arguments / evidence."
}

Rules:

- MECE: pillars must NOT overlap; together they must cover the load-bearing parts.
- Same abstraction level: roof, each pillar, and base operate at one consistent level.
- Load-bearing test: if you remove a pillar, the input's central purpose collapses.
- Pillar count: 2-9 allowed; STRONGLY PREFER 3-5 (Minto's Rule of 3, working memory).
- Labels: target <= 16 characters. Concise noun phrases.
- Summaries: one sentence each.
- fit_quality:
  - "good" -- the metaphor lands cleanly.
  - "stretched" -- the metaphor is forced but still informative.
  - "forced" -- you had to invent structure that is not really there.
  - "not_applicable" -- nothing to decompose (gibberish, empty, single sentence).

Emit ONLY the JSON object. No markdown fences. No commentary. No preamble.

Input to analyze:

{input}
"""

RETRY_FEEDBACK_HEADER = """\
Your previous response could not be parsed: {error}

Re-emit the JSON object correctly. Output ONLY the JSON object, no fences, no prose.
Schema and input below remain the same.

"""

_FENCE_RE = re.compile(r"^```(?:json)?\s*(.*?)\s*```\s*$", re.DOTALL)


class AnalyzerError(Exception):
    """Base for analyzer failures."""


class F4MalformedJSON(AnalyzerError):
    """LLM produced unparseable / schema-invalid JSON after the retry budget (F4)."""


@dataclass
class AnalyzeResult:
    data: PorticoJSON
    raw_response: str
    attempts: int


def build_prompt(text: str) -> str:
    return PROMPT_TEMPLATE.replace("{input}", text)


def build_retry_prompt(base_prompt: str, error: str) -> str:
    header = RETRY_FEEDBACK_HEADER.format(error=error)
    return header + base_prompt


def _strip_fence(s: str) -> str:
    s = s.strip()
    m = _FENCE_RE.match(s)
    if m:
        return m.group(1).strip()
    return s


def _parse_and_validate(raw: str) -> PorticoJSON:
    cleaned = _strip_fence(raw)
    data = json.loads(cleaned)
    return PorticoJSON.model_validate(data)


def analyze(
    text: str,
    *,
    provider: LLMProvider,
    model: str = DEFAULT_MODEL,
    max_retries: int = 2,
) -> AnalyzeResult:
    """Send `text` to the LLM, parse + validate JSON, retry on malformed output.

    Raises F4MalformedJSON after `max_retries` retries (so up to 1 + max_retries calls).
    Provider-side errors (auth, transport) propagate unchanged from the provider.
    """
    base_prompt = build_prompt(text)
    prompt = base_prompt
    last_error: Exception | None = None
    last_raw = ""

    for attempt in range(max_retries + 1):
        last_raw = provider.generate(prompt, model=model)
        try:
            data = _parse_and_validate(last_raw)
            return AnalyzeResult(data=data, raw_response=last_raw, attempts=attempt + 1)
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e
            prompt = build_retry_prompt(base_prompt, str(e))

    raise F4MalformedJSON(
        f"LLM returned unusable output after {max_retries + 1} attempts: {last_error}"
    )
