---
title: portico
sdk: gradio
sdk_version: 6.14.0
app_file: app.py
python_version: "3.12"
pinned: false
license: mit
short_description: "Render any input as a portico: a three-layered abstraction."
---

# portico

Render any input as a `portico`: a three-layered abstraction.

An LLM reads your input, decides what kind of thing it is, and decomposes it into
three layers -- roof (the unifying idea), pillars (the load-bearing components),
base (the foundation everything rests on). The renderer turns those layers into a
fixed ASCII shape.

Powered by Llama 3.3 70B via Groq. Source: [github.com/0trm/portico](https://github.com/0trm/portico).

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
