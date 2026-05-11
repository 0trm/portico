"""Gradio demo for portico, powered by an open-source LLM via Groq.

Users paste text or a URL; the app routes through portico's existing pipeline
(loader -> analyzer -> renderer) and returns the rendered portico as plain text.
"""

from __future__ import annotations

import os

import gradio as gr

from portico.analyzer import F4MalformedJSON, analyze
from portico.loaders.base import (
    F1NetworkUnavailable,
    F1NotFound,
    F1RemoteInaccessible,
    F2NotParseable,
    F2TooLarge,
    LoadedInput,
)
from portico.loaders.text import load_text
from portico.loaders.url import load_url
from portico.providers.base import (
    LLMProvider,
    ProviderAuthError,
    ProviderTransportError,
)
from portico.providers.openai import OpenAIProvider
from portico.render import render
from portico.render.color import ColorMode
from portico.schema import FitQuality
from portico.summarize import summarize

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = os.environ.get("PORTICO_DEMO_MODEL", "llama-3.3-70b-versatile")
RENDER_WIDTH = 80


def _build_provider() -> LLMProvider:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise gr.Error(
            "GROQ_API_KEY is not set. In Hugging Face Spaces, add it under "
            "Settings -> Variables and secrets."
        )
    return OpenAIProvider(api_key=api_key, base_url=GROQ_BASE_URL)


def _load(value: str) -> LoadedInput:
    value = value.strip()
    if not value:
        raise gr.Error("Paste some text or a URL first.")
    if value.startswith(("http://", "https://")):
        return load_url(value)
    return load_text(value)


def build_portico(value: str) -> tuple[str, str]:
    """Run the portico pipeline and return (rendered, diagnostics)."""
    try:
        loaded = _load(value)
    except (F1NotFound, F1RemoteInaccessible, F1NetworkUnavailable) as e:
        raise gr.Error(f"Could not load input: {e}") from e
    except F2NotParseable as e:
        raise gr.Error(f"Could not parse input: {e}") from e

    provider = _build_provider()

    try:
        loaded = summarize(loaded, provider=provider, model=DEFAULT_MODEL)
    except F2TooLarge as e:
        raise gr.Error(f"Input too large: {e}") from e
    except ProviderAuthError as e:
        raise gr.Error(f"LLM auth error: {e}") from e
    except ProviderTransportError as e:
        raise gr.Error(f"LLM transport error: {e}") from e

    try:
        result = analyze(loaded.text, provider=provider, model=DEFAULT_MODEL)
    except F4MalformedJSON as e:
        raise gr.Error(f"LLM returned unusable output: {e}") from e
    except ProviderAuthError as e:
        raise gr.Error(f"LLM auth error: {e}") from e
    except ProviderTransportError as e:
        raise gr.Error(f"LLM transport error: {e}") from e

    data = result.data

    if data.fit_quality == FitQuality.NOT_APPLICABLE:
        rendered = (
            "portico declined to render this input.\n\n"
            f"reason: {data.notes_on_fit}\n"
            f"input type detected: {data.theme}"
        )
    else:
        rendered = render(
            data,
            width=RENDER_WIDTH,
            height=None,
            color=ColorMode.NEVER,
            legend=True,
        )

    diagnostics = (
        f"input_type:  {loaded.input_type}\n"
        f"chars:       {loaded.metadata.get('chars', len(loaded.text))}\n"
        f"summarized:  {loaded.metadata.get('summarized', False)}\n"
        f"model:       {DEFAULT_MODEL}\n"
        f"fit_quality: {data.fit_quality.value}\n"
        f"attempts:    {result.attempts}"
    )
    return rendered, diagnostics


EXAMPLES = [
    [
        "Trust scales sub-linearly with team size. Past Dunbar's ~150, feedback loops"
        " stretch and diffusion of responsibility sets in. Smaller groups close loops"
        " faster, which is why high-trust teams stay small."
    ],
    ["https://en.wikipedia.org/wiki/Brier_score"],
    [
        "httpx is a fully featured HTTP client for Python 3, which provides sync and"
        " async APIs, and support for both HTTP/1.1 and HTTP/2."
    ],
]

DESCRIPTION = """\
**portico** decomposes any input -- prose, code, a URL -- into a three-layer ASCII
visualization: a roof (the unifying idea), pillars (the load-bearing components),
and a base (the foundation everything rests on).

This demo runs on **Llama 3.3 70B** via Groq. Paste text or a URL and submit.
"""

with gr.Blocks(title="portico demo", theme=gr.themes.Base()) as demo:
    gr.Markdown("# portico")
    gr.Markdown(DESCRIPTION)

    input_box = gr.Textbox(
        label="input",
        placeholder="Paste text, or a URL starting with https://",
        lines=8,
        max_lines=20,
    )
    submit = gr.Button("render portico", variant="primary")

    output_box = gr.Code(label="portico", language=None, interactive=False)
    diag_box = gr.Code(label="diagnostics", language=None, interactive=False)

    submit.click(fn=build_portico, inputs=input_box, outputs=[output_box, diag_box])
    input_box.submit(fn=build_portico, inputs=input_box, outputs=[output_box, diag_box])

    gr.Examples(examples=EXAMPLES, inputs=input_box)


if __name__ == "__main__":
    demo.launch()
