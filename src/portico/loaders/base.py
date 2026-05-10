"""Loader contract and shared exception hierarchy.

Every loader returns a `LoadedInput`. Failure cases map to F1/F2 categories
per the spec failure taxonomy and surface as specific exception subclasses
the CLI can route to exit codes 2-6.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LoadedInput:
    """Output of a loader -- raw text plus diagnostic metadata."""

    text: str
    source: str
    input_type: str  # text | file | dir | url | repo
    metadata: dict[str, Any] = field(default_factory=dict)


class LoaderError(Exception):
    """Base for all loader-side failures."""


# F1: input access (no LLM call)
class F1NotFound(LoaderError):
    """Local input does not exist or is unreadable. Exit 2."""


class F1RemoteInaccessible(LoaderError):
    """Remote input returned 4xx/5xx or DNS failed. Exit 3."""


class F1NetworkUnavailable(LoaderError):
    """Network required but unavailable. Exit 4."""


# F2: input parsing (no LLM call)
class F2NotParseable(LoaderError):
    """Input cannot be parsed as text (binary blob, encrypted, etc.). Exit 5."""


class F2TooLarge(LoaderError):
    """Input exceeds the hard size cap. Exit 6."""
