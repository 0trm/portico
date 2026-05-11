---
title: portico
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
python_version: "3.12"
pinned: false
license: mit
short_description: Render any input as a three-layer ASCII portico.
---

# portico demo

Interactive Gradio demo for [portico](https://github.com/0trm/portico).

Paste text or a URL and the app renders it as a three-layer ASCII portico
(roof / pillars / base), powered by Llama 3.3 70B via Groq.

## Layout

The Space bundles portico's source as a sibling `portico/` package next to
`app.py` (rather than pip-installing it). To deploy, copy `src/portico/` from
the main repo into the Space root as `portico/`.

## Local run

From the portico repo root:

```bash
uv pip install -r demo/requirements.txt
GROQ_API_KEY=... uv run python demo/app.py
```

## Hugging Face Spaces

Set `GROQ_API_KEY` under **Settings -> Variables and secrets**.
Optional: set `PORTICO_DEMO_MODEL` to override the default model.
