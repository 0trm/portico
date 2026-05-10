import httpx
import trafilatura

from arqii import __version__
from arqii.loaders.base import (
    F1NetworkUnavailable,
    F1RemoteInaccessible,
    F2NotParseable,
    LoadedInput,
)

DEFAULT_TIMEOUT = 15.0
SHORT_RESPONSE_THRESHOLD = 200  # below this, the page may be JS-rendered

# A few hosts (Wikipedia notably) reject the default httpx User-Agent. Identify
# politely as ourselves so requests succeed while staying honest about who we are.
USER_AGENT = f"arqii/{__version__} (CLI portico renderer; +https://github.com)"
DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def load_url(url: str, *, timeout: float = DEFAULT_TIMEOUT) -> LoadedInput:
    """Fetch a URL and extract its main content via trafilatura.

    Maps HTTP errors to F1RemoteInaccessible (exit 3), network errors to
    F1NetworkUnavailable (exit 4), and unparseable bodies to F2NotParseable
    (exit 5). Playwright fallback for JS-rendered pages is deferred.
    """
    try:
        response = httpx.get(
            url, timeout=timeout, follow_redirects=True, headers=DEFAULT_HEADERS
        )
    except (httpx.ConnectError, httpx.ConnectTimeout) as e:
        raise F1NetworkUnavailable(f"could not reach {url}: {e}") from e
    except httpx.RequestError as e:
        raise F1NetworkUnavailable(f"network error fetching {url}: {e}") from e

    if response.status_code >= 400:
        raise F1RemoteInaccessible(f"{url} returned HTTP {response.status_code}")

    extracted = trafilatura.extract(response.text)
    if not extracted:
        raise F2NotParseable(f"could not extract main content from {url}")

    return LoadedInput(
        text=extracted,
        source=url,
        input_type="url",
        metadata={
            "chars": len(extracted),
            "status": response.status_code,
            "short_response": len(extracted) < SHORT_RESPONSE_THRESHOLD,
        },
    )
