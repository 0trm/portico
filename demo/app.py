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
from portico.render.apex import generate_apex
from portico.schema import FitQuality

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = os.environ.get("PORTICO_DEMO_MODEL", "llama-3.3-70b-versatile")
RENDER_WIDTH = 80
GROQ_MAX_TOKENS = 3000  # leaves headroom under the free-tier 12K TPM cap
GROQ_INPUT_CHAR_BUDGET = 18_000  # ~4.5K tokens; fits with prompt overhead + output


def _build_provider() -> LLMProvider:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise gr.Error(
            "GROQ_API_KEY is not set. In Hugging Face Spaces, add it under "
            "Settings -> Variables and secrets."
        )
    return OpenAIProvider(
        api_key=api_key, base_url=GROQ_BASE_URL, max_tokens=GROQ_MAX_TOKENS
    )


def _load(value: str) -> LoadedInput:
    value = value.strip()
    if not value:
        raise gr.Error("Paste some text or a URL first.")
    if value.startswith(("http://", "https://")):
        return load_url(value)
    return load_text(value)


def _truncate(loaded: LoadedInput) -> LoadedInput:
    """Cap input to Groq free-tier per-request budget. Lossy but reliable."""
    if len(loaded.text) <= GROQ_INPUT_CHAR_BUDGET:
        return loaded
    return LoadedInput(
        text=loaded.text[:GROQ_INPUT_CHAR_BUDGET],
        source=loaded.source,
        input_type=loaded.input_type,
        metadata={
            **loaded.metadata,
            "truncated": True,
            "original_chars": len(loaded.text),
        },
    )


def build_portico(value: str) -> tuple[str, str]:
    """Run the portico pipeline and return (rendered, diagnostics)."""
    try:
        loaded = _load(value)
    except (F1NotFound, F1RemoteInaccessible, F1NetworkUnavailable) as e:
        raise gr.Error(f"Could not load input: {e}") from e
    except F2NotParseable as e:
        raise gr.Error(f"Could not parse input: {e}") from e

    loaded = _truncate(loaded)
    provider = _build_provider()

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
        finial, keystone, _ = generate_apex()
        rendered = render(
            data,
            width=RENDER_WIDTH,
            height=None,
            legend=True,
            apex_override=(finial, keystone),
        )

    diagnostics = (
        f"input_type:  {loaded.input_type}\n"
        f"chars:       {len(loaded.text)}\n"
        f"truncated:   {loaded.metadata.get('truncated', False)}\n"
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

INTRO_HTML = """
<div class="portico-intro">
  <p>An LLM reads your input, classifies it, and decomposes it into three
  layers. The renderer turns those layers into a fixed ASCII in the shape of
  <a href="https://github.com/0trm/portico/blob/main/docs/structure.jpg"
     target="_blank">a portico</a>.</p>

  <table class="portico-glyph-table">
    <thead><tr><th>Glyph</th><th>Layer</th><th>Meaning</th></tr></thead>
    <tbody>
      <tr><td><code>^</code></td><td>Roof</td><td>The unifying idea</td></tr>
      <tr><td><code>ii</code></td><td>Pillars</td>
        <td>The load-bearing components (2-9 of them)</td></tr>
      <tr><td><code>_</code></td><td>Base</td><td>The foundation everything rests on</td></tr>
    </tbody>
  </table>

  <p class="portico-refusal"><em>When an input doesn't fit a three-layer shape
  &ndash; poems, flat lists, gibberish &ndash; <code>portico</code> refuses
  honestly rather than fake one.</em></p>
</div>
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
    max-width: 620px;
    margin: 0 auto 18px;
    text-align: center;
    font-size: 13px;
}
.portico-intro p {
    margin: 8px auto;
    line-height: 1.5;
}
.portico-glyph-table {
    margin: 14px auto;
    font-size: 12px;
    border-collapse: collapse;
}
.portico-glyph-table th,
.portico-glyph-table td {
    padding: 6px 14px;
    border: 1px solid var(--border-color-primary);
    text-align: left;
}
.portico-glyph-table th {
    text-align: center;
    font-weight: 500;
}
.portico-glyph-table td:first-child {
    text-align: center;
}
.portico-intro code {
    font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
    background: transparent;
    padding: 0 2px;
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
    gr.HTML(INTRO_HTML)

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
