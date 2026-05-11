</div>

<p align="center">
<img width="425" height="300" alt="portico" src="https://github.com/user-attachments/assets/e15a3845-9e80-4edb-a038-19afb81b4649" />
</p>

<p align="center">
Render input as a portico: a three-layered visual abstraction.
</p>

<p align="center">
  <a href="https://pypi.org/project/portico-cli/"><img src="https://img.shields.io/pypi/v/portico-cli?style=flat&color=blue" alt="PyPI"></a>
  <a href="https://pypi.org/project/portico-cli/"><img src="https://img.shields.io/pypi/pyversions/portico-cli?style=flat&color=lightgrey" alt="Python"></a>
  <a href="https://huggingface.co/spaces/0trm/portico"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-lightgreen?style=flat" alt="HF Space"></a>
</p>

<p align="center">
  <a href="#try-it-online">Try it online</a> •
  <a href="#try-it-locally">Try it locally</a> •
  <a href="#example">Example</a> •
  <a href="#inputs">Inputs</a> •
  <a href="#customization">Customization</a>
</p>

---

## About

An LLM reads your input, classifies it, and decomposes it into three layers `_ii^`: roof, pillars, base. <br>
The renderer turns those layers into a fixed ASCII shape that resembles [a portico](docs/structure.jpg). <br>
You build a tiny monument for the thing you're trying to understand.

|  Glyph  | Layer   | Meaning                                       |
| :-----: | ------- | --------------------------------------------- |
|   `^`   | Roof    | The unifying idea                             |
|  `ii`   | Pillars | The load-bearing components                   |
|   `_`   | Base    | The foundation everything rests on            |

## Try it online

Run `portico` in your browser, no install required:

-> **[Hugging Face Space](https://huggingface.co/spaces/0trm/portico)** <-

*The Space uses 🦙 Llama 3.3 70B via Groq. Paste text or a URL and render.*

## Try it locally

### Install

```bash
uv tool install portico-cli
```

```bash
portico README.md
portico https://example.com/article
portico ./src --no-legend
echo "your text here" | portico -
```

## Example

```bash
portico https://trm.bearblog.dev/data-science-at-camp-nou/
```

```
── essay: Data Science at Camp Nou ─────────────────

                        ***
                    ===  ◇  ===
     ╔════════════════════════════════════════╗
     ║         Data-Driven Ticketing          ║
     ╚════════════════════════════════════════╝
  ////º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~\\\\
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
        ▀██▀            ▀██▀            ▀██▀
         ██              ██              ██
         ██              ██              ██
     Analytics    Experimentation    Predictive
         ██              ██           Modeling
         ██              ██              ██
         ██              ██              ██
        ▄██▄            ▄██▄            ▄██▄
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
╔══════════════════════════════════════════════════╗
║                   Fan Behavior                   ║
╚══════════════════════════════════════════════════╝

legend:
  ^  Data-Driven Ticketing: Using data science to optimize ticket sales and fan
     experience at FC Barcelona
  ii Analytics: Extracting insights from fan interactions with digital products
     to inform strategic decisions
  ii Experimentation: Testing hypotheses and validating results to drive product
     innovation
  ii Predictive Modeling: Building models to forecast ticket demand and optimize
     sales strategies
  _  Fan Behavior: Understanding fan interactions and preferences to inform
     data-driven decisions

───────────────────────────────── built with _ii^ ──
```

Rendered with `llama-3.3-70b-versatile`.

## Inputs

- Raw text or stdin
- Local files and directories
- URLs (page content is extracted)
- Git repositories

When an input doesn't fit a three-layer shape – poems, flat lists, gibberish – `portico` refuses honestly rather than fake one.

## Customization

| Flag                            | What it does                                                            |
| ------------------------------- | ----------------------------------------------------------------------- |
| `--no-legend`                   | Hide the per-layer summary (legend renders by default)                  |
| `--reapex[=N]`                  | Roll a random apex ornament; pin seed `N` to reproduce                  |
| `--json`                        | Emit the analyzer's JSON instead of rendering                           |
| `--diagnose`                    | Print a pipeline report (input type, model, fit quality) and exit       |

Run `portico --help` for the full list.

### Random apex

🎲 `--reapex` rolls a different ornament above the title each run. Pin the seed to reproduce the exact composition.

```bash
portico https://trm.bearblog.dev/data-science-at-camp-nou/ --reapex=0
```

```
── essay: Data Science at Camp Nou ─────────────────

                       ▲ * ▲
                    ~~~  ▲  ~~~
     ╔════════════════════════════════════════╗
     ║         Data-Driven Ticketing          ║
     ╚════════════════════════════════════════╝
  ////º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~\\\\
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
        ▀██▀            ▀██▀            ▀██▀
         ██              ██              ██
         ██              ██              ██
     Analytics    Experimentation    Predictive
         ██              ██           Modeling
         ██              ██              ██
         ██              ██              ██
        ▄██▄            ▄██▄            ▄██▄
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
╔══════════════════════════════════════════════════╗
║                   Fan Behavior                   ║
╚══════════════════════════════════════════════════╝
```

```bash
portico https://trm.bearblog.dev/data-science-at-camp-nou/ --reapex=1
```

```
── essay: Data Science at Camp Nou ─────────────────

                        ◆ ◆
                    ═══  ◆  ═══
     ╔════════════════════════════════════════╗
     ║         Data-Driven Ticketing          ║
     ╚════════════════════════════════════════╝
  ////º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~\\\\
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
        ▀██▀            ▀██▀            ▀██▀
         ██              ██              ██
         ██              ██              ██
     Analytics    Experimentation    Predictive
         ██              ██           Modeling
         ██              ██              ██
         ██              ██              ██
        ▄██▄            ▄██▄            ▄██▄
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
╔══════════════════════════════════════════════════╗
║                   Fan Behavior                   ║
╚══════════════════════════════════════════════════╝
```

```bash
portico https://trm.bearblog.dev/data-science-at-camp-nou/ --reapex=7
```

```
── essay: Data Science at Camp Nou ─────────────────

                       · · ·
                    ░░░  ▲  ░░░
     ╔════════════════════════════════════════╗
     ║         Data-Driven Ticketing          ║
     ╚════════════════════════════════════════╝
  ////º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~\\\\
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
        ▀██▀            ▀██▀            ▀██▀
         ██              ██              ██
         ██              ██              ██
     Analytics    Experimentation    Predictive
         ██              ██           Modeling
         ██              ██              ██
         ██              ██              ██
        ▄██▄            ▄██▄            ▄██▄
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
╔══════════════════════════════════════════════════╗
║                   Fan Behavior                   ║
╚══════════════════════════════════════════════════╝
```
---

## License

MIT

</br>
<p align="center" style="color: grey; font-size: 0.92em;">© 2026 trm</p>
