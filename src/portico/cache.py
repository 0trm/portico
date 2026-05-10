"""Content-hashed cache for analyzer outputs.

The cache is keyed on (text, provider, model) -- the same input through the
same model returns the same JSON. Per the failure taxonomy, F3 refusals are
cached (the input genuinely doesn't fit); F1/F2/F4 failures are not (re-run
may succeed). Caching policy is enforced by the caller, not this module.
"""

import hashlib
from dataclasses import dataclass
from pathlib import Path

from portico.schema import PorticoJSON

DEFAULT_CACHE_DIR = Path.home() / ".cache" / "portico"


def cache_key(text: str, *, provider: str, model: str) -> str:
    payload = f"{provider}|{model}|{text}".encode()
    return hashlib.sha256(payload).hexdigest()


@dataclass
class Cache:
    root: Path = DEFAULT_CACHE_DIR

    def _path(self, key: str) -> Path:
        return self.root / f"{key}.json"

    def get(self, key: str) -> PorticoJSON | None:
        path = self._path(key)
        if not path.exists():
            return None
        try:
            return PorticoJSON.model_validate_json(path.read_text())
        except Exception:
            # Corrupt cache entry: drop it and miss.
            path.unlink(missing_ok=True)
            return None

    def put(self, key: str, data: PorticoJSON) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self._path(key).write_text(data.model_dump_json(indent=2))

    def invalidate(self, key: str) -> None:
        self._path(key).unlink(missing_ok=True)
