import json
from pathlib import Path

from arqii.cache import Cache, cache_key
from arqii.schema import PorticoJSON

FIXTURE = Path(__file__).parent / "fixtures" / "json" / "codebase_3pillars.json"


def _data() -> PorticoJSON:
    return PorticoJSON.model_validate(json.loads(FIXTURE.read_text()))


def test_cache_key_is_deterministic() -> None:
    a = cache_key("hello", provider="claude", model="m1")
    b = cache_key("hello", provider="claude", model="m1")
    assert a == b


def test_cache_key_differs_on_content_provider_model() -> None:
    base = cache_key("hello", provider="claude", model="m1")
    assert cache_key("HELLO", provider="claude", model="m1") != base
    assert cache_key("hello", provider="openai", model="m1") != base
    assert cache_key("hello", provider="claude", model="m2") != base


def test_cache_miss_returns_none(tmp_path: Path) -> None:
    cache = Cache(root=tmp_path)
    assert cache.get("anykey") is None


def test_cache_put_then_get(tmp_path: Path) -> None:
    cache = Cache(root=tmp_path)
    data = _data()
    cache.put("k1", data)
    out = cache.get("k1")
    assert out is not None
    assert out.theme == data.theme
    assert len(out.pillars) == len(data.pillars)


def test_cache_invalidate(tmp_path: Path) -> None:
    cache = Cache(root=tmp_path)
    cache.put("k1", _data())
    cache.invalidate("k1")
    assert cache.get("k1") is None


def test_cache_corrupt_entry_is_silently_dropped(tmp_path: Path) -> None:
    cache = Cache(root=tmp_path)
    cache.root.mkdir(parents=True, exist_ok=True)
    (cache.root / "k1.json").write_text("not valid json")
    assert cache.get("k1") is None
    # And the corrupt file should be gone.
    assert not (cache.root / "k1.json").exists()
