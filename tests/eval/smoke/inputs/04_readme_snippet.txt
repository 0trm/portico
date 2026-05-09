# httpx

A next-generation HTTP client for Python.

httpx builds on the requests API but adds support for HTTP/2, async/await, automatic connection pooling, and full type annotations. It is suitable for both library authors who need a sync-and-async pair and application authors who want a single client across both worlds.

## Install

    pip install httpx

## Sync

    import httpx
    r = httpx.get("https://example.org")
    r.status_code

## Async

    import httpx
    async with httpx.AsyncClient() as client:
        r = await client.get("https://example.org")

## Features

- HTTP/1.1 and HTTP/2 support
- Sync and async APIs from the same client surface
- Connection pooling and timeouts
- Type-checked: full mypy / pyright annotations
- Tested against the same compliance suite as requests
