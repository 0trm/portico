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
    ["https://en.wikipedia.org/wiki/Photosynthesis"],
    ["https://en.wikipedia.org/wiki/Bitcoin"],
    ["https://en.wikipedia.org/wiki/Stoicism"],
    ["https://trm.bearblog.dev/three-spaces-of-context/"],
]

HERO_HTML = """
<div class="portico-hero">
  <div class="portico-mark">_ii^</div>
  <div class="portico-wordmark">portico</div>
  <div class="portico-tagline">render input as a three-layered visual abstraction</div>
</div>
"""

INTRO_MD = """\
An LLM reads your input, classifies it, and decomposes it into three layers. The
renderer turns those layers into a fixed ASCII in the shape of
[a portico](https://github.com/0trm/portico/blob/main/docs/structure.jpg).

| Glyph | Layer   | Meaning                                       |
| :---: | ------- | --------------------------------------------- |
| `^`   | Roof    | The unifying idea                             |
| `ii`  | Pillars | The load-bearing components (2-9 of them)     |
| `_`   | Base    | The foundation everything rests on            |

*When an input doesn't fit a three-layer shape – poems, flat lists, gibberish –
`portico` refuses honestly rather than fake one.*
"""

FOOTER_HTML = """
<div class="portico-footer">
  powered by Llama 3.3 70B via Groq ·
  <a href="https://github.com/0trm/portico" target="_blank">source</a> ·
  <a href="https://pypi.org/project/portico-cli/" target="_blank">pypi</a>
</div>
"""

CUSTOM_CSS = """
.portico-hero {
    text-align: center;
    padding: 28px 0 8px;
}
.portico-mark {
    font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 45px;
    letter-spacing: 0.18em;
    line-height: 1;
    margin: 0;
    user-select: none;
}
.portico-wordmark {
    font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 17px;
    letter-spacing: 0.04em;
    margin-top: 16px;
    font-weight: 500;
}
.portico-tagline {
    font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 12px;
    color: var(--body-text-color-subdued);
    margin-top: 6px;
}
.portico-intro {
    max-width: 720px;
    margin: 0 auto 18px;
    font-size: 13px;
}
.portico-intro table {
    font-size: 12px;
    margin: 10px auto;
}
.portico-output textarea,
.portico-output pre,
.portico-output code,
.portico-output .cm-content,
.portico-output .cm-line {
    font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace !important;
    font-size: 13px !important;
    line-height: 1.35 !important;
}
.portico-diag textarea,
.portico-diag pre,
.portico-diag code,
.portico-diag .cm-content,
.portico-diag .cm-line {
    font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace !important;
    font-size: 12px !important;
}
.portico-submit button {
    font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace !important;
    letter-spacing: 0.08em;
    font-weight: 500;
}
.portico-footer {
    text-align: center;
    padding: 16px 0 4px;
    font-size: 11px;
    color: var(--body-text-color-subdued);
    letter-spacing: 0.03em;
}
.portico-footer a {
    color: var(--body-text-color-subdued);
    text-decoration: underline;
    text-underline-offset: 2px;
}
"""

theme = gr.themes.Base(
    primary_hue="stone",
    neutral_hue="stone",
    radius_size=gr.themes.sizes.radius_sm,
    font=[gr.themes.GoogleFont("JetBrains Mono"), "ui-monospace", "monospace"],
    font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "ui-monospace", "monospace"],
)

with gr.Blocks(title="portico") as demo:
    gr.HTML(HERO_HTML)
    gr.Markdown(INTRO_MD, elem_classes=["portico-intro"])

    with gr.Row(equal_height=False):
        with gr.Column(scale=4):
            input_box = gr.Textbox(
                label="input",
                placeholder="paste text, or a url starting with https://",
                lines=10,
                max_lines=24,
            )
            submit = gr.Button(
                "_ii^   render",
                variant="primary",
                elem_classes=["portico-submit"],
            )
            gr.Examples(examples=EXAMPLES, inputs=input_box, label="examples")

        with gr.Column(scale=6):
            output_box = gr.Code(
                label="portico",
                language=None,
                interactive=False,
                elem_classes=["portico-output"],
            )
            with gr.Accordion("diagnostics", open=False):
                diag_box = gr.Code(
                    label="",
                    language=None,
                    interactive=False,
                    elem_classes=["portico-diag"],
                )

    gr.HTML(FOOTER_HTML)

    submit.click(fn=build_portico, inputs=input_box, outputs=[output_box, diag_box])
    input_box.submit(fn=build_portico, inputs=input_box, outputs=[output_box, diag_box])


if __name__ == "__main__":
    demo.launch(theme=theme, css=CUSTOM_CSS)
