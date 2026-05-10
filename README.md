<div align="center">

<img src="https://raw.githubusercontent.com/0trm/portico/main/docs/portico.png" alt="portico" width="640">

<pre>_ii^
portico</pre>

<em>render any input as a portico -- a three-layer ASCII visualization</em>

<sub><a href="https://pypi.org/project/portico-cli/">pypi</a> · <a href="https://github.com/0trm/portico">github</a> · <a href="https://github.com/0trm/portico/blob/main/LICENSE">mit</a></sub>

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
portico ./src --no-legend
echo "your text here" | portico -
```

## what is a portico

An LLM reads your input, decides what kind of thing it is, and decomposes it into three layers. The renderer turns those layers into a fixed ASCII shape.

|  glyph  | layer   | meaning                                       |
| :-----: | ------- | --------------------------------------------- |
|   `^`   | roof    | the unifying idea                             |
|  `ii`   | pillars | the load-bearing components (2-9 of them)     |
|   `_`   | base    | the foundation everything rests on            |

## examples

short, medium, long.

### hello world

```
echo "hello world" | portico -
```

```
── snippet: hello world ────────────────────────────────────────────────────────

                                      ***
                               __ ===  ◇  === __
                           ╔════════════════════════╗
                           ║       salutation       ║
                           ╚════════════════════════╝
                        //~~~~~~~~~~~~~~~~~~~~~~~~~~~~\\
                         ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
                              ▀██▀            ▀██▀
                               ██              ██
                               ██              ██
                             hello           world
                               ██              ██
                               ██              ██
                              ▄██▄            ▄██▄
                         ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                      ╔══════════════════════════════════╗
                      ║        coding convention         ║
                      ╚══════════════════════════════════╝

legend:
  ^  salutation: a greeting addressed at the world.
  ii hello: the act of greeting.
  ii world: the recipient.
  _  coding convention: the canonical first program in any toolchain.

───────────────────────────────────────────────────────────── built with _ii^ ──
```

### a github repo

```
portico https://github.com/binwiederhier/ntfy
```

```
── software README: ntfy ───────────────────────────────────────────────────────

                                      ***
                               __ ===  ◇  === __
           ╔════════════════════════════════════════════════════════╗
           ║                Scriptable Notifications                ║
           ╚════════════════════════════════════════════════════════╝
        //~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\\
         ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
              ▀██▀            ▀██▀            ▀██▀            ▀██▀
               ██              ██              ██              ██
               ██              ██              ██              ██
         Service Access  Apps & Clients   Community &    Contributions
               ██              ██           Support            ██
               ██              ██              ██              ██
               ██              ██              ██              ██
              ▄██▄            ▄██▄            ▄██▄            ▄██▄
         ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      ╔══════════════════════════════════════════════════════════════════╗
      ║          Open-source licensing | Third-party libraries           ║
      ╚══════════════════════════════════════════════════════════════════╝

legend:
  ^  Scriptable Notifications: Send phone or desktop notifications from any script via a simple HTTP pub-sub service, with no sign-up required.
  ii Service Access: ntfy is available as a hosted free tier at ntfy.sh, a paid ntfy Pro plan, or a self-hosted open-source instance.
  ii Apps & Clients: Native Android and iOS apps, plus a web app, let users subscribe to and receive notifications across platforms.
  ii Community & Support: Discord, Matrix, and GitHub Issues provide channels for chat, bug reports, feature requests, and beta announcements.
  ii Contributions: Code PRs, issue reports, and Weblate translations are welcomed, with larger features discussed on Discord or Matrix first.
  _  Open-source licensing | Third-party libraries: The project is dual-licensed under Apache 2.0 and GPLv2, and is built on a stack of open-source libraries covering the CLI, web app, database, push delivery, and more.

───────────────────────────────────────────────────────────── built with _ii^ ──
```

### a long-form essay

```
portico https://www.wiisfi.com/
```

```
── technical guide: Wi-Fi Upgrade Guide ────────────────────────────────────────

                                      ***
                               __ ===  ◇  === __
        ╔══════════════════════════════════════════════════════════════╗
        ║                     Client-Limited Wi-Fi                     ║
        ╚══════════════════════════════════════════════════════════════╝
     //~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\\
      ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
          ▀██▀          ▀██▀          ▀██▀          ▀██▀          ▀██▀
           ██            ██            ██            ██            ██
           ██            ██            ██            ██            ██
         Speed         Wi-Fi       Deployment   Alternative  Diagnostics &
      Fundamentals  Generations   Architecture    Backhaul       Config
           ██            ██            ██            ██            ██
           ██            ██            ██            ██            ██
          ▄██▄          ▄██▄          ▄██▄          ▄██▄          ▄██▄
      ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   ╔════════════════════════════════════════════════════════════════════════╗
   ║              Educational purpose | Empirical measurement               ║
   ╚════════════════════════════════════════════════════════════════════════╝

legend:
  ^  Client-Limited Wi-Fi: Real-world Wi-Fi performance is governed by client device constraints and physical distance, not by router marketing figures, and informed decisions require cutting through manufacturer hype.
  ii Speed Fundamentals: PHY speed is determined by channel width, MIMO level, and QAM modulation; the Throughput-to-PHY Ratio runs ~70%, and advertised aggregate speeds are fictional sums irrelevant to any real 2×2 client.
  ii Wi-Fi Generations: Wi-Fi 4 through Wi-Fi 7 each advanced primarily through wider channels and higher QAM rather than generation changes alone, with Wi-Fi 6's 160 MHz support and Wi-Fi 7's 320 MHz channels being the meaningful inflection points.
  ii Deployment Architecture: Wired access points on non-overlapping channels outperform range extenders and mesh systems; the preferred model is a 4×4 MIMO router plus Ethernet-connected APs following the 'Wi-Fi AIR' philosophy.
  ii Alternative Backhaul: When Ethernet cannot be run, MoCA 2.5 over coax, powerline adapters, buried fiber, and wireless bridges provide progressively capable substitutes, each with specific limitations and use conditions.
  ii Diagnostics & Config: PHY speed checks, channel analysis, DFS verification, router configuration best practices, and systematic troubleshooting steps enable readers to confirm whether any upgrade actually improved real-world throughput.
  _  Educational purpose | Empirical measurement: The guide is grounded in a commitment to ad-free reader education and in direct measurement—checking PHY speeds, running speed tests before and after changes, and verifying specs against FCC filings—rather than trusting manufacturer claims.

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
| `--no-legend`                   | hide the per-layer summary (legend renders by default)                  |
| `--color {auto,always,never}`   | colorize roof / pillars / base. default: `never`                        |
| `--reapex[=N]`                  | roll a random apex ornament; pin seed `N` to reproduce                  |
| `--json`                        | emit the analyzer's JSON instead of rendering                           |
| `--diagnose`                    | print a pipeline report (input type, model, fit quality) and exit       |

Run `portico --help` for the full list.
