<div align="center">

<img src="https://raw.githubusercontent.com/0trm/portico/main/docs/structure.jpg" alt="portico" width="640">

<pre>_ii^
portico</pre>

<em>render any input as a portico -- a three-layer ASCII visualization</em>

</div>

---

## install

```bash
pipx install portico-cli
```

## try it

```bash
portico README.md
portico https://example.com/article
portico ./src --verbose
echo "your text here" | portico -
```

## what is a portico

An LLM reads your input, decides what kind of thing it is, and decomposes it into three layers. The renderer turns those layers into a fixed ASCII shape.

|  glyph  | layer   | meaning                                       |
| :-----: | ------- | --------------------------------------------- |
|   `^`   | roof    | the unifying idea                             |
|  `ii`   | pillars | the load-bearing components (2-9 of them)     |
|   `_`   | base    | the foundation everything rests on            |

## example

`portico` on a small codebase:

```
── codebase: my-repo ───────────────────────────────────────────────────────────

                                      ***
                                  ===  ◇  ===
                    //════════════════════════════════════\\
                   ╔════════════════════════════════════════╗
                   ║               Public API               ║
                   ╚════════════════════════════════════════╝
                //~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\\
                 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
                      ▀██▀            ▀██▀            ▀██▀
                       ██              ██              ██
                       ██              ██              ██
                      Auth          Routing         Storage
                       ██              ██              ██
                       ██              ██              ██
                      ▄██▄            ▄██▄            ▄██▄
                 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
              ╔══════════════════════════════════════════════════╗
              ║                     Runtime                      ║
              ╚══════════════════════════════════════════════════╝

───────────────────────────────────────────────────────────── built with _ii^ ──
```

## inputs

- raw text or stdin
- local files and directories
- URLs (page content is extracted)
- git repositories

When an input doesn't fit a three-layer shape -- poems, flat lists, gibberish -- `portico` refuses honestly rather than fake one.

## customization

| flag                            | what it does                                                            |
| ------------------------------- | ----------------------------------------------------------------------- |
| `--verbose`, `-v`               | add a legend with a one-line summary for each layer                     |
| `--color {auto,always,never}`   | colorize roof / pillars / base. default: `never`                        |
| `--reapex[=N]`                  | roll a random apex ornament; pin seed `N` to reproduce                  |
| `--json`                        | emit the analyzer's JSON instead of rendering                           |
| `--diagnose`                    | print a pipeline report (input type, model, fit quality) and exit       |

Run `portico --help` for the full list.
