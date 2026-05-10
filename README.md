</div>

<p align="center">
  <img src="https://raw.githubusercontent.com/0trm/portico/main/docs/portico.png" alt="portico" width="340" />
</p>

<h1 align="center">portico _ii^</h1>

<p align="center">
  <strong>Render any input as a portico – a three-layer visual abstraction.</strong>
</p>

<p align="center">
  <a href="https://github.com/0trm/portico/stargazers"><img src="https://img.shields.io/github/stars/0trm/portico?style=flat&color=yellow" alt="Stars"></a>
  <a href="https://github.com/0trm/portico/commits/main"><img src="https://img.shields.io/github/last-commit/0trm/portico?style=flat" alt="Last Commit"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/0trm/portico?style=flat" alt="License"></a>
</p>

---

## Install

```bash
pipx install portico-cli
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
echo "The plot of Rocky (1976) hinges on three relationships: Rocky's tentative romance with the shy, awkward Adrian; his mentorship under the cantankerous old trainer Mickey; and his match against world heavyweight champion Apollo Creed. Rocky is a club fighter from a working-class corner of Philadelphia who gets a million-to-one title shot and resolves not to win, but to go the full fifteen rounds." | portico -
```

```
── plot summary: Rocky (1976) ──────────────────────────────────────────────────────────────────────

                                                ***
                                            ===  ◇  ===
                             ╔════════════════════════════════════════╗
                             ║           Going the Distance           ║
                             ╚════════════════════════════════════════╝
                          ////~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\\\\
                           ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
                                ▀██▀            ▀██▀            ▀██▀
                                 ██              ██              ██
                                 ██              ██              ██
                           Rocky & Adrian  Rocky & Mickey  Rocky & Apollo
                                 ██              ██              ██
                                 ██              ██              ██
                                ▄██▄            ▄██▄            ▄██▄
                           ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                        ╔══════════════════════════════════════════════════╗
                        ║          Working-class underdog premise          ║
                        ╚══════════════════════════════════════════════════╝

legend:
  ^  Going the Distance: A club fighter's self-worth is tested not by winning but by surviving fifteen rounds against the world heavyweight champion.
  ii Rocky & Adrian: A tentative romance with a shy, awkward woman gives Rocky an emotional anchor outside the ring.
  ii Rocky & Mickey: A cantankerous old trainer offers hard-edged mentorship that prepares Rocky for the title shot.
  ii Rocky & Apollo: The million-to-one match against the world heavyweight champion is the film's central dramatic confrontation.
  _  Working-class underdog premise: Rocky's identity as a small-time Philadelphia club fighter makes the title shot implausible and the goal of merely lasting fifteen rounds meaningful.

───────────────────────────────────────────────────────────────────────────────── built with _ii^ ──
```

## Inputs

- Raw text or stdin
- Local files and directories
- URLs (page content is extracted)
- Git repositories

When an input doesn't fit a three-layer shape -- poems, flat lists, gibberish -- `portico` refuses honestly rather than fake one.

## Customization

| Flag                            | What it does                                                            |
| ------------------------------- | ----------------------------------------------------------------------- |
| `--no-legend`                   | Hide the per-layer summary (legend renders by default)                  |
| `--color {auto,always,never}`   | Colorize roof / pillars / base. default: `never`                        |
| `--reapex[=N]`                  | Roll a random apex ornament; pin seed `N` to reproduce                  |
| `--json`                        | Emit the analyzer's JSON instead of rendering                           |
| `--diagnose`                    | Print a pipeline report (input type, model, fit quality) and exit       |

Run `portico --help` for the full list.
