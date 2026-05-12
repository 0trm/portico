from unittest.mock import patch

import httpx
import pytest

from portico.loaders.base import (
    F1NetworkUnavailable,
    F1RemoteInaccessible,
    F2NotParseable,
)
from portico.loaders.url import load_url

SAMPLE_HTML = """
<!doctype html>
<html><body>
<article>
  <h1>The Title</h1>
  <p>Quick brown fox. The lazy dog. A second sentence to give trafilatura something to extract.</p>
  <p>And a third paragraph with another distinct claim worth quoting in a structure.</p>
</article>
</body></html>
"""


class _Resp:
    def __init__(self, status: int, text: str) -> None:
        self.status_code = status
        self.text = text


def test_load_url_happy_path() -> None:
    with patch("portico.loaders.url.httpx.get", return_value=_Resp(200, SAMPLE_HTML)):
        out = load_url("https://example.com/article")
    assert "Quick brown fox" in out.text
    assert out.input_type == "url"
    assert out.source == "https://example.com/article"
    assert out.metadata["status"] == 200


def test_load_url_4xx_raises_f1_remote() -> None:
    with (
        patch("portico.loaders.url.httpx.get", return_value=_Resp(404, "")),
        pytest.raises(F1RemoteInaccessible),
    ):
        load_url("https://example.com/missing")


def test_load_url_5xx_raises_f1_remote() -> None:
    with (
        patch("portico.loaders.url.httpx.get", return_value=_Resp(503, "")),
        pytest.raises(F1RemoteInaccessible),
    ):
        load_url("https://example.com/down")


def test_load_url_connect_error_raises_f1_network() -> None:
    def boom(*args: object, **kwargs: object) -> _Resp:
        raise httpx.ConnectError("dns failed")

    with (
        patch("portico.loaders.url.httpx.get", side_effect=boom),
        pytest.raises(F1NetworkUnavailable),
    ):
        load_url("https://no-such-host.invalid/")


def test_load_url_timeout_raises_f1_network() -> None:
    def boom(*args: object, **kwargs: object) -> _Resp:
        raise httpx.ConnectTimeout("slow")

    with (
        patch("portico.loaders.url.httpx.get", side_effect=boom),
        pytest.raises(F1NetworkUnavailable),
    ):
        load_url("https://slow.example/")


def test_load_url_unextractable_raises_f2() -> None:
    with (
        patch("portico.loaders.url.httpx.get", return_value=_Resp(200, "<html></html>")),
        pytest.raises(F2NotParseable),
    ):
        load_url("https://empty.example/")


@pytest.mark.live
def test_load_url_live_smoke() -> None:
    """Real network call to a stable URL. Skipped by default unless `-m live`."""
    out = load_url("https://example.com")
    assert out.text
    assert out.metadata["status"] == 200
