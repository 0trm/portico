import json
from pathlib import Path

from arqii.cli import (
    EXIT_F1_NOT_FOUND,
    EXIT_F2_NOT_PARSEABLE,
    EXIT_F4_TRANSPORT,
    EXIT_OK,
    parse_args,
    run,
)
from arqii.providers.base import LLMProvider, ProviderTransportError

FIXTURES = Path(__file__).parent / "fixtures" / "json"


class FakeProvider(LLMProvider):
    """Returns a scripted JSON response on every call."""

    def __init__(self, response_path: str) -> None:
        self.response = (FIXTURES / response_path).read_text()
        self.calls = 0

    def generate(self, prompt: str, *, model: str) -> str:
        self.calls += 1
        return self.response


_FLAG_OVERRIDES = {
    "json_out": "--json",
    "input_type": "--type",
}


def _args(input_value: str, **overrides):
    argv = [input_value]
    for k, v in overrides.items():
        flag = _FLAG_OVERRIDES.get(k, "--" + k.replace("_", "-"))
        if isinstance(v, bool):
            if v:
                argv.append(flag)
        else:
            argv.extend([flag, str(v)])
    return parse_args(argv)


def test_text_input_renders_portico(capsys, tmp_path) -> None:
    args = _args("hello world", no_cache=True, width=80)
    rc = run(args, provider=FakeProvider("codebase_3pillars.json"))
    assert rc == EXIT_OK
    out = capsys.readouterr().out
    assert "── codebase: my-repo ──" in out


def test_json_flag_outputs_validated_json(capsys) -> None:
    args = _args("anything", no_cache=True, json_out=True)
    rc = run(args, provider=FakeProvider("codebase_3pillars.json"))
    assert rc == EXIT_OK
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["theme"] == "codebase"
    assert len(parsed["pillars"]) == 3


def test_diagnose_flag_prints_pipeline_report(capsys) -> None:
    args = _args("anything", no_cache=True, diagnose=True)
    rc = run(args, provider=FakeProvider("codebase_3pillars.json"))
    assert rc == EXIT_OK
    out = capsys.readouterr().out
    for key in ("input:", "type:", "provider:", "model:", "fit_quality:"):
        assert key in out


def test_missing_file_exits_2(tmp_path) -> None:
    args = _args(str(tmp_path / "nope.txt"), no_cache=True)
    rc = run(args, provider=FakeProvider("codebase_3pillars.json"))
    assert rc == EXIT_F1_NOT_FOUND


def test_bare_filename_with_extension_is_treated_as_file() -> None:
    """`arqii nonexistent.txt` shouldn't silently fall through to load_text."""
    from arqii.cli import detect_input_type

    assert detect_input_type("nonexistent.txt") == "file"
    assert detect_input_type("essay.md") == "file"
    assert detect_input_type("config.toml") == "file"


def test_sentence_with_period_is_text_not_file() -> None:
    """A sentence with a period shouldn't be misread as a path."""
    from arqii.cli import detect_input_type

    assert detect_input_type("Trust scales sub-linearly with size.") == "text"
    assert detect_input_type("hello world") == "text"


def test_no_args_with_tty_stdin_exits_F2_with_help_hint(monkeypatch) -> None:
    """`arqii` with no args + interactive terminal should not block on stdin."""
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    parsed = parse_args([])
    rc = run(parsed, provider=FakeProvider("codebase_3pillars.json"))
    assert rc == EXIT_F2_NOT_PARSEABLE


class _BoomProvider(LLMProvider):
    """Raises a transport error from generate (covers summarize + analyze paths)."""

    def generate(self, prompt: str, *, model: str) -> str:
        raise ProviderTransportError("simulated network failure")


def test_provider_transport_error_during_summarize_exits_cleanly(tmp_path) -> None:
    """If summarize's chunk call fails, surface F4 transport instead of crashing."""
    long_text = ("paragraph.\n\n" * 20_000)  # well above TARGET_CHARS
    f = tmp_path / "long.txt"
    f.write_text(long_text)
    args = _args(str(f), no_cache=True)
    rc = run(args, provider=_BoomProvider())
    assert rc == EXIT_F4_TRANSPORT


def test_binary_file_exits_5(tmp_path) -> None:
    f = tmp_path / "blob.bin"
    f.write_bytes(b"\x00\x01\x02hello\x00")
    args = _args(str(f), no_cache=True)
    rc = run(args, provider=FakeProvider("codebase_3pillars.json"))
    assert rc == EXIT_F2_NOT_PARSEABLE


def test_forced_fit_quality_refuses_without_force(capsys) -> None:
    args = _args("anything", no_cache=True)
    rc = run(args, provider=FakeProvider("flat_list_forced.json"))
    assert rc == EXIT_OK
    assert "could not build a portico" in capsys.readouterr().out


def test_forced_fit_quality_renders_with_force(capsys) -> None:
    args = _args("anything", no_cache=True, force=True, width=80)
    rc = run(args, provider=FakeProvider("flat_list_forced.json"))
    assert rc == EXIT_OK
    assert "── list: shopping ──" in capsys.readouterr().out


def test_not_applicable_refuses_even_with_force(capsys) -> None:
    args = _args("anything", no_cache=True, force=True)
    rc = run(args, provider=FakeProvider("gibberish_not_applicable.json"))
    assert rc == EXIT_OK
    assert "could not build a portico" in capsys.readouterr().out


def test_strict_upgrades_stretched_to_refusal(capsys) -> None:
    args = _args("anything", no_cache=True, strict=True)
    rc = run(args, provider=FakeProvider("survey_9pillars_stretched.json"))
    assert rc == EXIT_OK
    assert "could not build a portico" in capsys.readouterr().out


def test_stretched_renders_with_caveat_by_default(capsys) -> None:
    args = _args("anything", no_cache=True, width=80)
    rc = run(args, provider=FakeProvider("survey_9pillars_stretched.json"))
    assert rc == EXIT_OK
    out = capsys.readouterr().out
    assert "stretched" in out
    assert "── survey: context fitting ──" in out


def test_cache_hit_skips_provider_call(capsys, tmp_path, monkeypatch) -> None:
    # Redirect cache to a temp dir.
    from arqii.cache import Cache as _Cache
    monkeypatch.setattr("arqii.cli.Cache", lambda: _Cache(root=tmp_path))

    p1 = FakeProvider("codebase_3pillars.json")
    args = _args("hello world", width=80)
    rc1 = run(args, provider=p1)
    assert rc1 == EXIT_OK
    assert p1.calls == 1
    capsys.readouterr()

    p2 = FakeProvider("codebase_3pillars.json")
    rc2 = run(args, provider=p2)
    assert rc2 == EXIT_OK
    assert p2.calls == 0  # cached


def test_no_cache_skips_cache_lookup(capsys, tmp_path, monkeypatch) -> None:
    from arqii.cache import Cache as _Cache
    monkeypatch.setattr("arqii.cli.Cache", lambda: _Cache(root=tmp_path))

    p1 = FakeProvider("codebase_3pillars.json")
    args = _args("hello world", no_cache=True, width=80)
    run(args, provider=p1)
    capsys.readouterr()

    p2 = FakeProvider("codebase_3pillars.json")
    run(args, provider=p2)
    assert p2.calls == 1  # called again because --no-cache
