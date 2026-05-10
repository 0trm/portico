> The mark _is_ the [[analogy]]. The notation _is_ the vocabulary. Key visual -> [[structure.jpg]]. Key a

---

## The mark

```
_ii^
```

Three characters. Three layers. Each character is the minimal glyph of the layer it represents — the logo deconstructs into its own documentation.

| Glyph | Layer   | Why this character                                                                   |
| :---: | ------- | ------------------------------------------------------------------------------------ |
|  `_`  | base    | sits on the baseline; reads as ground                                                |
| `ii`  | pillars | the most pillar-shaped letter, doubled -- vertical, narrow, with capitals (the dots) |
|  `^`  | roof    | a triangle pointing up; the pediment of a temple front                               |

---

## The wordmark

```
portico
```

Lowercase. Always. No capitalization at sentence start, no title case, no all-caps. Treated as a proper noun typeset in lowercase — like `git`, `npm`, `curl`.

---

## The lockup

The canonical pairing of mark and wordmark is **stacked, with the mark above**:

```
_ii^
portico
```

This is the form a portico takes in the world: mark on top, name underneath. Use this in README heroes, social cards, presentation title slides, anywhere the brand needs to land with weight.

When stacked is impossible (one-line contexts: badges, taglines, terminal banners), use the **inline lockup** with three spaces of breathing room:

```
portico   _ii^
```

A single en-dash or hyphen between the two (`portico – _ii^`) collapses visually and should be avoided.

---

## Notation

The mark is also the project's working vocabulary. When referring to a layer in code, docs, issues, commit messages, or conversation, the glyph is a valid shorthand:

- `_` — the base
- `ii` — the pillars (collectively); a single pillar is an `i`
- `^` — the roof

These are interchangeable with the English words. Both forms are first-class:

> "The `_` summary should describe the foundational substrate, not the background context."
> 
> "The `_` should describe the foundational substrate, not the background context."

Both read correctly. Pick whichever fits the surrounding sentence.

### In code

Field names in JSON / Python / configs use the **English** forms (`base`, `pillars`, `roof`) because identifiers should be readable by people who haven't met the brand yet:

```json
{
  "roof":    { "label": "...", "summary": "..." },
  "pillars": [ { "label": "...", "summary": "..." } ],
  "base":    { "label": "...", "summary": "..." }
}
```

### In prose / commits / issues

The **glyphs** are welcome and encouraged. They are tighter and on-brand:

```
fix: ^ label truncation in narrow terminals
feat: support 9 i in wide-mode rendering
docs: clarify what counts as a _ vs. background context
```

### In CLI flags

English. Glyphs are not shell-safe.

```
portico --verbose            # ok
portico --no-^               # not ok
```

---

## Voice & register

The product is precise, slightly classical, quietly technical. Three rules:

1. **Don't oversell the metaphor.** A portico is a useful frame, not a sacred one. Avoid temple-religion language ("sacred portico," "the temple of your code," "enlightenment"). The product is an analysis tool with a good visual hook, not a philosophy.
2. **Be specific, not architectural.** "Roof" is concrete. "Apex" or "crown" or "pinnacle" is reaching. When in doubt, use the simpler word.
3. **Lowercase, terse, calm.** Headlines without exclamation points. Sentences that fit on one line. The mark is small; the voice should match.

---

## Color

There is no brand color.

`portico` lives in terminals, READMEs, and code. Both render in whatever palette the reader has chosen. Imposing a brand color on top of that is noise. The mark is monochrome by definition: it's three characters in whatever color the surrounding text is.

When color is unavoidable (a social card, a slide), default to:

- **Foreground:** the reader's text color (terminal default, GitHub markdown default).
- **Accent (sparingly):** a single muted accent for hover/active states in docs sites. Pick once, document it here, never add a second.

This section is intentionally short. The lack of a color system is itself a design choice — `portico` is a tool that runs inside other people's environments, and good guests don't redecorate.

---

## Typography

Monospace, always, when the mark or any portico render is involved. Proportional fonts collapse the alignment of `_`, `i`, and `^` and break the metaphor.

Recommended stack for any surface that renders the mark:

```
"JetBrains Mono", "Fira Code", "SF Mono", Menlo, Consolas, monospace
```

For the wordmark in non-monospace contexts (a hero illustration, a sticker), any clean, lowercase-friendly sans-serif works. The wordmark is not locked to monospace; only the mark is.

---

## Repo treatment

The mark and wordmark show up in specific places across the GitHub surface:

|Surface|Treatment|
|---|---|
|README hero|Stacked lockup, centered, in a fenced code block|
|Repo description|Inline lockup: `_ii^ Take any input. See its layered shape.`|
|Social preview image|Full ASCII portico + wordmark + glyph (custom OG image)|
|`assets/logo.txt`|Canonical mark and full portico, committed as files (one source of truth)|
|CLI `--version`|Small portico + version number|
|CLI banner (TTY)|Tiny mark before the first line of output, optional, off by default|

---

## What not to do

- Don't redraw the mark in different characters (`_||^`, `_II^`, `-ii-`). The specific glyphs `_`, `i`, `^` are the brand. Substitutes break the "minimal element of each layer" logic.
- Don't add a fourth element. No floor, no sky, no decorations.
- Don't capitalize `portico`. Not even at the start of a sentence. The word is always lowercase.
- Don't use the mark inside running prose as if it were punctuation. It's a logo, not a bullet.
- Don't translate the mark. `_ii^` is the same in every language.
- Don't put the mark in URL slugs, package names, or shell commands. The repo is `portico`. The CLI is `portico`. The mark is for display only.

---

## One-line summary

> `portico — _ii^` -- three characters, three layers, no decoration.