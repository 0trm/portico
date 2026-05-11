</div>

<p align="center">
<img width="405" height="280" alt="portico" src="https://github.com/user-attachments/assets/e15a3845-9e80-4edb-a038-19afb81b4649" />
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

–> **[Hugging Face Space](https://huggingface.co/spaces/0trm/portico)** <–

*The space uses 🦙 Llama 3.3 70B via Groq. Paste [input](#inputs) and render.*

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
portico "https://en.wikipedia.org/wiki/Transformer_(deep_learning_architecture)"
```

```
── encyclopedia article: Transformer ───────────────────────────────────────────────

                                        ***
                                    ===  ◇  ===
     ╔════════════════════════════════════════════════════════════════════════╗
     ║                       Attention Is All You Need                        ║
     ╚════════════════════════════════════════════════════════════════════════╝
  ////º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~\\\\
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
        ▀██▀            ▀██▀            ▀██▀            ▀██▀            ▀██▀
         ██              ██              ██              ██              ██
         ██              ██              ██              ██              ██
       RNN to       Architecture      Training       Efficient      Applications
    Transformer          ██              ██          Inference           ██
         ██              ██              ██              ██              ██
         ██              ██              ██              ██              ██
        ▄██▄            ▄██▄            ▄██▄            ▄██▄            ▄██▄
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
╔══════════════════════════════════════════════════════════════════════════════════╗
║                               Multi-head attention                               ║
╚══════════════════════════════════════════════════════════════════════════════════╝

legend:
  ^  Attention Is All You Need: Replacing recurrence with multi-head self-attention enables fully
     parallel sequence processing, making transformers the dominant architecture for language and
     beyond.
  ii RNN to Transformer: The article traces how vanishing-gradient limitations in RNNs and seq2seq
     models motivated the removal of recurrence in favour of parallelisable attention.
  ii Architecture: The transformer is built from tokenization, positional encoding, stacked encoder
     and decoder layers with self- and cross-attention, feedforward networks, and an un-embedding
     layer, with encoder-only, decoder-only, and encoder-decoder variants.
  ii Training: Transformers are trained via masked, autoregressive, or prefixLM tasks, typically
     using large-scale self-supervised pretraining followed by supervised fine-tuning, with layer
     normalisation placement critical for convergence.
  ii Efficient Inference: KV caching, FlashAttention, multi-query attention, speculative decoding,
     and sub-quadratic attention variants reduce the memory and compute costs of running large
     transformer models.
  ii Applications: Transformers have been applied across NLP, computer vision, speech, robotics,
     multimodal generation, and reinforcement learning, powering systems from BERT and GPT to DALL-E
     and AlphaFold.
  _  Multi-head attention: Scaled dot-product multi-head attention is the single load-bearing
     mechanism from which the transformer's parallelism, contextualisation, and cross-modal
     flexibility all derive.

───────────────────────────────────────────────────────────────── built with _ii^ ──
```

Rendered with `claude-sonnet-4-6`.

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
