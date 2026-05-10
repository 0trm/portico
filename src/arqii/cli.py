"""arqii CLI -- single entry point that wires the pipeline together.

Loader -> Summarizer (if oversized) -> Cache check -> Analyzer -> Renderer.
Failure classes route to exit codes per the spec failure taxonomy.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from arqii import __version__
from arqii.analyzer import F4MalformedJSON, analyze
from arqii.cache import Cache, cache_key
from arqii.config import (
    get_anthropic_api_key,
    get_default_model,
    get_default_provider,
)
from arqii.loaders.base import (
    F1NetworkUnavailable,
    F1NotFound,
    F1RemoteInaccessible,
    F2NotParseable,
    F2TooLarge,
    LoadedInput,
)
from arqii.loaders.dir import load_dir
from arqii.loaders.file import load_file
from arqii.loaders.repo import load_repo
from arqii.loaders.text import load_stdin, load_text
from arqii.loaders.url import load_url
from arqii.providers.base import (
    LLMProvider,
    ProviderAuthError,
    ProviderTransportError,
)
from arqii.providers.claude import DEFAULT_MODEL, ClaudeProvider
from arqii.providers.gemini import GeminiProvider
from arqii.providers.openai import OpenAIProvider
from arqii.render import MAX_WIDTH, render
from arqii.render.apex import generate_apex
from arqii.render.color import ColorMode
from arqii.schema import FitQuality, PorticoJSON
from arqii.summarize import summarize

REFUSAL_TEMPLATE = """\
arqii could not build a portico for this input.

reason: {reason}

input type detected: {theme}

what you can try:
  • run with --force to render anyway
  • narrow the input and try again
  • verify the input is what you intended
"""


# --- Exit codes ---
EXIT_OK = 0
EXIT_F1_NOT_FOUND = 2
EXIT_F1_REMOTE = 3
EXIT_F1_NETWORK = 4
EXIT_F2_NOT_PARSEABLE = 5
EXIT_F2_TOO_LARGE = 6
EXIT_F4_MALFORMED = 7
EXIT_F4_TRANSPORT = 8
EXIT_F4_AUTH = 9


@dataclass
class Args:
    input_value: str | None
    input_type: str | None
    style: str
    color: ColorMode
    verbose: bool
    width: int
    json_out: bool
    provider: str
    model: str
    no_cache: bool
    diagnose: bool
    force: bool
    strict: bool
    reapex: bool
    reapex_seed: int | None


def make_provider(name: str) -> LLMProvider:
    if name == "claude":
        return ClaudeProvider(api_key=get_anthropic_api_key())
    if name == "openai":
        return OpenAIProvider()
    if name == "gemini":
        return GeminiProvider()
    raise ValueError(f"unknown provider: {name}")


def detect_input_type(value: str) -> str:
    if value.startswith(("http://", "https://")):
        return "url"
    p = Path(value)
    if p.exists():
        return "dir" if p.is_dir() else "file"
    if "/" in value or "\\" in value:
        # Looks like a path even though it doesn't exist; let the file loader
        # surface the F1 instead of silently treating the path string as text.
        return "file"
    return "text"


def load(value: str | None, *, input_type: str | None) -> LoadedInput:
    if value is None:
        return load_stdin()
    if value == "-":
        return load_stdin()
    t = input_type or detect_input_type(value)
    if t == "url":
        return load_url(value)
    if t == "file":
        return load_file(value)
    if t == "dir":
        return load_dir(value)
    if t == "repo":
        return load_repo(value)
    return load_text(value)


def resolve_width(arg_width: int | None) -> int:
    if arg_width is not None:
        return arg_width
    return min(shutil.get_terminal_size((MAX_WIDTH, 24)).columns, MAX_WIDTH)


def render_refusal(data: PorticoJSON) -> str:
    return REFUSAL_TEMPLATE.format(reason=data.notes_on_fit, theme=data.theme)


def render_diagnostics(
    loaded: LoadedInput, data: PorticoJSON, *, model: str, provider_name: str
) -> str:
    return (
        f"input:        {loaded.source}\n"
        f"type:         {loaded.input_type}\n"
        f"chars:        {loaded.metadata.get('chars', len(loaded.text))}\n"
        f"summarized:   {loaded.metadata.get('summarized', False)}\n"
        f"provider:     {provider_name}\n"
        f"model:        {model}\n"
        f"fit_quality:  {data.fit_quality.value}\n"
        f"notes_on_fit: {data.notes_on_fit}\n"
    )


def run(args: Args, *, provider: LLMProvider | None = None) -> int:
    """The pipeline. `provider` injection is for tests."""
    try:
        loaded = load(args.input_value, input_type=args.input_type)
    except F1NotFound as e:
        print(f"arqii: {e}", file=sys.stderr)
        return EXIT_F1_NOT_FOUND
    except F1RemoteInaccessible as e:
        print(f"arqii: {e}", file=sys.stderr)
        return EXIT_F1_REMOTE
    except F1NetworkUnavailable as e:
        print(f"arqii: {e}", file=sys.stderr)
        return EXIT_F1_NETWORK
    except F2NotParseable as e:
        print(f"arqii: {e}", file=sys.stderr)
        return EXIT_F2_NOT_PARSEABLE

    prov = provider or make_provider(args.provider)

    try:
        loaded = summarize(loaded, provider=prov, model=args.model)
    except F2TooLarge as e:
        print(f"arqii: {e}", file=sys.stderr)
        return EXIT_F2_TOO_LARGE

    cache = Cache()
    key = cache_key(loaded.text, provider=args.provider, model=args.model)
    data: PorticoJSON | None = None
    if not args.no_cache:
        data = cache.get(key)

    if data is None:
        try:
            result = analyze(loaded.text, provider=prov, model=args.model)
        except F4MalformedJSON as e:
            print(f"arqii: {e}", file=sys.stderr)
            return EXIT_F4_MALFORMED
        except ProviderAuthError as e:
            print(f"arqii: {e}", file=sys.stderr)
            return EXIT_F4_AUTH
        except ProviderTransportError as e:
            print(f"arqii: {e}", file=sys.stderr)
            return EXIT_F4_TRANSPORT
        data = result.data
        if not args.no_cache:
            cache.put(key, data)

    if args.diagnose:
        print(render_diagnostics(loaded, data, model=args.model, provider_name=args.provider))
        return EXIT_OK

    if args.json_out:
        print(json.dumps(data.model_dump(mode="json"), indent=2))
        return EXIT_OK

    # F3 routing -- abstain when fit_quality demands it.
    fq = data.fit_quality
    if fq == FitQuality.NOT_APPLICABLE:
        print(render_refusal(data))
        return EXIT_OK
    if fq == FitQuality.FORCED and not args.force:
        print(render_refusal(data))
        return EXIT_OK
    if fq == FitQuality.STRETCHED and args.strict:
        print(render_refusal(data))
        return EXIT_OK

    apex_override: tuple[str, str] | None = None
    apex_seed_label: str | None = None
    if args.reapex:
        finial, keystone, used_seed = generate_apex(args.reapex_seed)
        apex_override = (finial, keystone)
        apex_seed_label = f"apex seed: {used_seed}"

    print(
        render(
            data,
            width=args.width,
            color=args.color,
            verbose=args.verbose,
            apex_override=apex_override,
            apex_seed_label=apex_seed_label,
        ),
        end="",
    )
    return EXIT_OK


def parse_args(argv: list[str] | None = None) -> Args:
    parser = argparse.ArgumentParser(prog="arqii", description="Render any input as a portico.")
    parser.add_argument("input", nargs="?", help="Path, URL, raw text, or '-' for stdin.")
    parser.add_argument("--type", dest="input_type", choices=["text", "file", "dir", "url", "repo"])
    parser.add_argument("--style", default="default")
    parser.add_argument(
        "--color",
        choices=[c.value for c in ColorMode],
        default=ColorMode.NEVER.value,
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--width", type=int, default=None)
    parser.add_argument("--json", dest="json_out", action="store_true")
    parser.add_argument(
        "--provider",
        choices=["claude", "openai", "gemini"],
        default=get_default_provider(),
    )
    parser.add_argument("--model", default=get_default_model() or DEFAULT_MODEL)
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--diagnose", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--reapex",
        nargs="?",
        const="__random__",
        default=None,
        help="Roll a random symmetric apex ornament. Pass --reapex=SEED to pin one.",
    )
    parser.add_argument("--version", action="version", version=f"arqii {__version__}")
    parsed = parser.parse_args(argv)

    reapex = parsed.reapex is not None
    reapex_seed: int | None = None
    if reapex and parsed.reapex != "__random__":
        try:
            reapex_seed = int(parsed.reapex)
        except ValueError:
            parser.error(
                f"--reapex value must be an integer seed, got {parsed.reapex!r}"
            )

    return Args(
        input_value=parsed.input,
        input_type=parsed.input_type,
        style=parsed.style,
        color=ColorMode(parsed.color),
        verbose=parsed.verbose,
        width=resolve_width(parsed.width),
        json_out=parsed.json_out,
        provider=parsed.provider,
        model=parsed.model,
        no_cache=parsed.no_cache,
        diagnose=parsed.diagnose,
        force=parsed.force,
        strict=parsed.strict,
        reapex=reapex,
        reapex_seed=reapex_seed,
    )


def main() -> None:
    args = parse_args()
    sys.exit(run(args))
