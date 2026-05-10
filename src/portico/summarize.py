"""Recursive summarizer for inputs that exceed the analyzer's context budget.

Tiered strategy (per wiki/recursive-summarization.md):
- text <= TARGET_CHARS  → passthrough
- text >  HARD_CAP      → raise F2TooLarge
- otherwise             → chunk + summarize per chunk, then recurse up to MAX_LEVELS

Char counts are used as a proxy for tokens (rough 4:1 ratio) to keep the
summarizer free of tiktoken-specific dependencies. Replace with a real token
counter when accuracy becomes load-bearing.
"""

from portico.loaders.base import F2TooLarge, LoadedInput
from portico.providers.base import LLMProvider
from portico.providers.claude import DEFAULT_MODEL

TARGET_CHARS = 120_000        # ~30k tokens
HARD_CAP_CHARS = 20_000_000   # ~5M tokens
CHUNK_CHARS = 32_000          # ~8k tokens
MAX_LEVELS = 2

CHUNK_PROMPT = """\
Summarize the text fragment below into a compact, structurally-faithful summary
that preserves the load-bearing claims, components, or sections. Keep the
original ordering. Aim for roughly 1/4 the original length. Output prose only,
no preamble.

Fragment:

{chunk}
"""


def _split_into_chunks(text: str, chunk_size: int = CHUNK_CHARS) -> list[str]:
    """Slice text into chunks at paragraph boundaries when possible."""
    paragraphs = text.split("\n\n")
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for p in paragraphs:
        if current_len + len(p) + 2 > chunk_size and current:
            chunks.append("\n\n".join(current))
            current = [p]
            current_len = len(p)
        else:
            current.append(p)
            current_len += len(p) + 2
    if current:
        chunks.append("\n\n".join(current))
    # Fallback: a single oversized paragraph -- hard-slice it.
    out: list[str] = []
    for c in chunks:
        if len(c) <= chunk_size:
            out.append(c)
        else:
            for i in range(0, len(c), chunk_size):
                out.append(c[i : i + chunk_size])
    return out


def _summarize_chunk(chunk: str, *, provider: LLMProvider, model: str) -> str:
    prompt = CHUNK_PROMPT.replace("{chunk}", chunk)
    return provider.generate(prompt, model=model).strip()


def summarize(
    loaded: LoadedInput,
    *,
    provider: LLMProvider,
    model: str = DEFAULT_MODEL,
) -> LoadedInput:
    """Reduce loaded.text to <= TARGET_CHARS, recursively if needed."""
    text = loaded.text
    if len(text) <= TARGET_CHARS:
        return loaded
    if len(text) > HARD_CAP_CHARS:
        raise F2TooLarge(
            f"input is {len(text)} chars (~{len(text) // 4} tokens); "
            f"hard cap is {HARD_CAP_CHARS} chars"
        )

    original_chars = len(text)
    levels_used = 0
    while len(text) > TARGET_CHARS and levels_used < MAX_LEVELS:
        chunks = _split_into_chunks(text)
        summaries = [_summarize_chunk(c, provider=provider, model=model) for c in chunks]
        text = "\n\n".join(summaries)
        levels_used += 1

    return LoadedInput(
        text=text,
        source=loaded.source,
        input_type=loaded.input_type,
        metadata={
            **loaded.metadata,
            "summarized": True,
            "summarize_levels": levels_used,
            "original_chars": original_chars,
            "summarized_chars": len(text),
        },
    )
