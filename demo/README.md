---
title: portico
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
license: mit
short_description: Render any input as a three-layer ASCII portico.
---

# portico demo

Interactive Gradio demo for [portico](https://github.com/0trm/portico).

Paste text or a URL and the app renders it as a three-layer ASCII portico
(roof / pillars / base), powered by Llama 3.3 70B via Groq.

## Local run

```bash
cd demo
uv venv
uv pip install -r requirements.txt
GROQ_API_KEY=... uv run python app.py
```

## Hugging Face Spaces

Set `GROQ_API_KEY` under **Settings -> Variables and secrets**.
Optional: set `PORTICO_DEMO_MODEL` to override the default model.
