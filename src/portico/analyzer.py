import json
import re
from dataclasses import dataclass

from pydantic import ValidationError

from portico.providers.base import LLMProvider
from portico.providers.claude import DEFAULT_MODEL
from portico.schema import PorticoJSON

PROMPT_TEMPLATE = """\
You are portico. You decompose any input into a three-layer "portico": a roof \
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
10. "base": object {"labels": array of 1-4 strings, "summary": string}. The foundation that \
everything rests on. Use 1 label for a single foundation; add a 2nd/3rd/4th ONLY when each \
names a distinct foundational course that earns its place. Redundancy is noise.
11. "fit_quality": one of "good", "stretched", "forced", "not_applicable".
12. "notes_on_fit": string. If not "good", explain why in one sentence.

Concrete example of the exact shape (illustrative content; do not copy the values):

{
  "input_type": "essay",
  "type_rationale": "Argumentative prose with thesis and supporting reasoning.",
  "decomposition_strategy": "Thesis on top; two arguments as pillars; evidence at base.",
  "scratch_outline": ["Sub-linear trust ...", "Feedback loops ...", "Dunbar ...", "Evidence ..."],
  "mece_check": "Two pillars are non-overlapping causal mechanisms.",
  "theme": "essay",
  "title": "trust at scale",
  "roof": {"label": "Sub-linear Trust", "summary": "Trust scales sub-linearly with size."},
  "pillars": [
    {"label": "Feedback loops", "summary": "Smaller groups close feedback faster."},
    {"label": "Dunbar limit", "summary": "Diffusion of responsibility past ~150."}
  ],
  "base": {"labels": ["Empirical evidence"], "summary": "Observed work on team size and trust."},
  "fit_quality": "good",
  "notes_on_fit": "Essay decomposes cleanly into thesis / arguments / evidence."
}

Notice the roof uses "Sub-linear Trust" (the actual claim from the input), NOT a generic \
"Thesis". This is the most important rule below.

Rules:

LABELS (calibrate between two failure modes):

Failure mode A -- TOO GENERIC: labels that could apply to any input of the same type \
("Hypothesis", "Methodology", "Findings", "Seed Thesis", "Central Claim"). These add no \
value because they describe the slot, not the contents.

Failure mode B -- TOO CRYPTIC: labels so specific they need the input to decode \
("5→15→30→60", "Gini-NIAH Tie", "Re-found Each Doubling"). These add no value because the \
reader has to consult the source to make sense of them.

The sweet spot: short noun phrases that are *recognizable from the input* but *readable on \
their own*. Bias slightly toward the abstract side -- when in doubt between "too specific \
to read at a glance" and "a bit generic but clear", choose clear.

Concrete rules:
- USE THE INPUT'S OWN VOCABULARY: when the input names a concept ("Dunbar limit", \
  "tragedy of the commons", "loaders"), reuse those terms. Don't invent synonyms.
- ROOF MUST NOT EQUAL THE TITLE: the banner above the portico already names the input \
  (e.g. "── software README: httpx ──"). The roof must do different work -- name the \
  central claim, the unifying idea, what the input is *about* one rung up from what it \
  *is*. Title `httpx` + roof `Modern HTTP Client` is correct; title `httpx` + roof \
  `httpx` is wrong. EXCEPTION: codebase inputs where the repo/module name is the \
  natural roof and no higher abstraction is available.
- READABLE AT A GLANCE: every label should make sense to a reader who has not seen the \
  input. If a pillar label is a numerical range, an abbreviation, a coined phrase, or \
  requires recall of a specific passage to decode -- abstract one rung up.
- NO INVENTED ADJECTIVES: do not modify a noun with an adjective unless that adjective \
  appears in the input or is directly entailed. "Resilient", "Modern", "Robust", \
  "Comprehensive", "Strategic" are red flags -- if the input does not use them, drop them.
- NO HALLUCINATED CONCEPTS: every label and every summary clause must trace back to \
  language or ideas in the input. Do not extend the author's metaphors or coin new ones.
- Plain language: when the input uses everyday words, prefer everyday words in the labels. \
  Reach for jargon only if the input itself does.
- Length: target <= 16 characters per label. Concise noun phrases. Summaries are one sentence.

PORTICO:
- MECE: pillars must NOT overlap; together they must cover the load-bearing parts.
- Same abstraction level: roof, each pillar, and base operate at one consistent level.
- Load-bearing test: if you remove a pillar, the input's central purpose collapses.
- Pillars are not steps: if the input has temporal/sequential structure (recipes, \
  walkthroughs, ordered instructions), the portico is the wrong metaphor -- set \
  fit_quality to "stretched" or worse rather than forcing steps into pillars.
- Pillar-base separation: pillars and base must not overlap. A core ingredient of the input \
  belongs in the base, not also as a pillar.
- Pillar count: 2-9 allowed; STRONGLY PREFER 3-5 (Minto's Rule of 3, working memory).

FIT (push back when the metaphor does not earn its keep):
- "good" -- the metaphor lands cleanly.
- "stretched" -- the metaphor is forced but still informative.
- "forced" -- you had to invent structure that is not really there.
- "not_applicable" -- nothing to decompose. Use for: gibberish, random words, flat lists \
  with no organizing principle, single sentences with no internal structure, very short \
  conventional inputs (greetings, idioms), or any content that lacks the kind of \
  structural decomposition the portico models.
- POETRY ALWAYS REFUSES: lyric and narrative poems do not admit portico decomposition. \
  Poems work through image, rhythm, and meaning-by-accumulation -- they have no \
  load-bearing pillars in the architectural sense. Set fit_quality to "not_applicable" \
  for any poem and explain briefly in notes_on_fit.
- FLAT LISTS REFUSE: simple lists (shopping lists, word lists, enumerations) lack the \
  structural decomposition the portico models. Set fit_quality to "not_applicable" rather \
  than inventing categorical pillars.
- When torn between "forced" and "not_applicable", choose "not_applicable" and explain \
  briefly in notes_on_fit. Refusing is a feature; the portico is not for everything.

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
