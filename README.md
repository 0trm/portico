</div>

<p align="center">
  <img src="https://raw.githubusercontent.com/0trm/portico/main/docs/portico.png" alt="portico" width="340" />
</p>

<h1 align="center">portico _ii^</h1>

<p align="center">
  <strong>Render any input as a portico: a three-layered abstraction.</strong>
</p>

<p align="center">
  <a href="https://github.com/0trm/portico/stargazers"><img src="https://img.shields.io/github/stars/0trm/portico?style=flat&color=yellow" alt="Stars"></a>
  <a href="https://github.com/0trm/portico/commits/main"><img src="https://img.shields.io/github/last-commit/0trm/portico?style=flat" alt="Last Commit"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/0trm/portico?style=flat" alt="License"></a>
</p>

---

## Install

```bash
uv tool install portico-cli
```

## Try it

```bash
portico README.md
portico https://example.com/article
portico ./src --no-legend
echo "your text here" | portico -
```

## What is a portico

An LLM reads your input, decides what kind of thing it is, and decomposes it into three layers. The renderer turns those layers into a fixed ASCII shape.

|  Glyph  | Layer   | Meaning                                       |
| :-----: | ------- | --------------------------------------------- |
|   `^`   | Roof    | The unifying idea                             |
|  `ii`   | Pillars | The load-bearing components (2-9 of them)     |
|   `_`   | Base    | The foundation everything rests on            |

## Example

```
echo "What makes Rocky (1976) endure is not what it shows you but what it means. A nobody from the neighborhood discovers that he is capable of love, that he is brave enough to step into a fight he can't win, and that his self-worth is something he can earn through effort rather than receive from victory. The film is the story of a man who refuses to be invisible -- and earns, by the end, the right to be seen." | portico -
```

```
── essay: Rocky Endures ────────────────────────────────────────────────────────────────────────────

                                                ***
                                            ===  ◇  ===
                             ╔════════════════════════════════════════╗
                             ║           Meaning Over Image           ║
                             ╚════════════════════════════════════════╝
                          ////~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\\\\
                           ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
                                ▀██▀            ▀██▀            ▀██▀
                                 ██              ██              ██
                                 ██              ██              ██
                            Capacity for     Unwinnable     Earned Self-
                                Love           Fight           Worth
                                 ██              ██              ██
                                 ██              ██              ██
                                ▄██▄            ▄██▄            ▄██▄
                           ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                        ╔══════════════════════════════════════════════════╗
                        ║              Refusing Invisibility               ║
                        ╚══════════════════════════════════════════════════╝

legend:
  ^  Meaning Over Image: Rocky endures because of what it means, not what it literally shows the audience.
  ii Capacity for Love: Rocky discovers he is capable of love, giving him a reason beyond himself.
  ii Unwinnable Fight: He is brave enough to step into a fight he cannot win, which is its own form of victory.
  ii Earned Self-Worth: He learns his self-worth is something he can earn through effort rather than receive from the outcome.
  _  Refusing Invisibility: Everything rests on Rocky's core refusal to remain invisible and his drive to earn the right to be seen.

───────────────────────────────────────────────────────────────────────────────── built with _ii^ ──
```

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
| `--color {auto,always,never}`   | Colorize roof / pillars / base. default: `never`                        |
| `--reapex[=N]`                  | Roll a random apex ornament; pin seed `N` to reproduce                  |
| `--json`                        | Emit the analyzer's JSON instead of rendering                           |
| `--diagnose`                    | Print a pipeline report (input type, model, fit quality) and exit       |

Run `portico --help` for the full list.
