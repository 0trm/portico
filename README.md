</div>

<p align="center">
<img width="400" height="275" alt="portico" src="https://github.com/user-attachments/assets/e15a3845-9e80-4edb-a038-19afb81b4649" />
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

**`portico` renders input as three-layered visual abstraction.**

1. An LLM reads your input, classifies it, and decomposes it into three layers `_ii^`: roof, pillars, base. <br>
2. The renderer turns those layers into a fixed ASCII shape that resembles [a portico](docs/structure.jpg). <br>
3. It builds a tiny monument for the thing you're trying to understand.

|  Glyph  | Layer   | Meaning                                       |
| :-----: | ------- | --------------------------------------------- |
|   `^`   | Roof    | The unifying idea                             |
|  `ii`   | Pillars | The load-bearing components                   |
|   `_`   | Base    | The foundation everything rests on            |

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
## Try it online

Run `portico` in your browser, no install required:

–> **[Hugging Face Space](https://huggingface.co/spaces/0trm/portico)** <–

*The space uses 🦙 Llama 3.3 70B via Groq. Paste [input](#inputs) and render.*

## Example

```bash
portico "https://en.wikipedia.org/wiki/Transformer_(deep_learning_architecture)"
```
```
── encyclopedia article: Transformer ──────────────────────────────────────────

                                      ***
                                  ===  ◇  ===
     ╔═══════════════════════════════════════════════════════════════════╗
     ║                     Attention Is All You Need                     ║
     ╚═══════════════════════════════════════════════════════════════════╝
  ////º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º~~º\\\\
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
       ▀██▀           ▀██▀           ▀██▀           ▀██▀           ▀██▀
        ██             ██             ██             ██             ██
        ██             ██             ██             ██             ██
   Predecessors   Architecture     Training      Efficiency    Applications
        ██             ██             ██             ██             ██
        ██             ██             ██             ██             ██
       ▄██▄           ▄██▄           ▄██▄           ▄██▄           ▄██▄
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
╔═════════════════════════════════════════════════════════════════════════════╗
║                        Scaled dot-product attention                         ║
╚═════════════════════════════════════════════════════════════════════════════╝

legend:
  ^  Attention Is All You Need: The 2017 thesis that pure attention, with neither
     recurrence nor convolution, suffices for sequence-to-sequence modeling —
     yielding parallel training and the foundational architecture of modern AI.
  ii Predecessors: RNN and LSTM seq2seq models suffered from vanishing gradients and
     sequential bottlenecks; Bahdanau and Luong attention bolted onto these
     recurrent backbones in 2014-15 set up the 2017 Vaswani et al. paper to drop
     recurrence entirely.
  ii Architecture: Tokenization, learned embeddings, and sinusoidal or learned
     positional encoding feed stacks of multi-head self- and cross-attention plus
     position-wise feedforward sublayers, composed into encoder-only, decoder-only,
     or full encoder-decoder variants with residual connections and layer
     normalization throughout.
  ii Training: Self-supervised pretraining on masked, autoregressive, or prefix-LM
     objectives followed by supervised fine-tuning, with Adam-family optimizers and
     warmup schedules, and pre- vs post-norm placement materially shaping
     convergence at depth.
  ii Efficiency: KV caching, FlashAttention's I/O-aware kernels, multi-query and
     grouped-query attention, speculative decoding, and sub-quadratic variants such
     as Linformer, Performer, and state-space hybrids cut the memory and compute
     costs of training and inference.
  ii Applications: Transformers underpin systems across NLP (BERT, GPT, T5), vision
     (ViT), speech (Whisper), code, multimodal generation (DALL-E, GPT-4o),
     structural biology (AlphaFold), robotics, and reinforcement learning.
  _  Scaled dot-product attention: The atomic operation that computes a softmax-
     weighted average of value vectors, with weights given by scaled query-key dot
     products — the single load-bearing mechanism from which multi-head, self-,
     masked, and cross-attention all derive.

──────────────────────────────────────────────────────────── built with _ii^ ──
```
*Run with `claude-sonnet-4-6`.*

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

The apex is the ornament crowning the portico, picked at render time from a pool of 600+ variants.
🎲 --reapex rolls a different one each run. Pin the seed to reproduce.

```bash
portico https://0trm.blog/data-science-at-camp-nou/ --reapex=0
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
portico https://0trm.blog/data-science-at-camp-nou/ --reapex=1
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
portico https://0trm.blog/data-science-at-camp-nou/ --reapex=7
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

<br>

*Built ~~by~~ with AI.*

</br>
<p align="center" style="color: grey; font-size: 0.92em;">© 2026 trm</p>
