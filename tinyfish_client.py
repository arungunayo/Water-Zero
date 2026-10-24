"""TinyFish Search and Fetch REST client for WaterZero."""
from __future__ import annotations

import os
from typing import Any
import httpx
from dotenv import load_dotenv

load_dotenv()

SEARCH_URL = "https://api.search.tinyfish.ai"
FETCH_URL = "https://api.fetch.tinyfish.ai"


class TinyFishError(RuntimeError):
    """Raised for TinyFish configuration or API errors."""


def _api_key() -> str:
    key = os.getenv("TINYFISH_API_KEY", "").strip()
    if not key or key.lower().startswith(("replace_", "your_")):
        raise TinyFishError(
            "TinyFish API key is not configured. Copy .env.example to .env and set TINYFISH_API_KEY."
        )
    return key


def _headers() -> dict[str, str]:
    return {"X-API-Key": _api_key(), "Accept": "application/json"}


def _timeout() -> float:
    try:
        return max(10.0, min(float(os.getenv("TINYFISH_TIMEOUT_SECONDS", "45")), 120.0))
    except ValueError:
        return 45.0


def _check(response: httpx.Response) -> None:
    if response.is_error:
        # Don't include request headers or API key in the exception.
        body = response.text[:700]
        raise TinyFishError(f"TinyFish returned HTTP {response.status_code}: {body}")


async def search(query: str) -> dict[str, Any]:
    """GET Search API; response contains structured results with title/snippet/url."""
    if not query.strip():
        raise TinyFishError("Search query cannot be empty.")
    async with httpx.AsyncClient(timeout=_timeout(), follow_redirects=True) as client:
        response = await client.get(
            SEARCH_URL,
            params={"query": query.strip()},
            headers=_headers(),
        )
    _check(response)
    try:
        data = response.json()
    except ValueError as exc:
        raise TinyFishError("TinyFish Search returned non-JSON data.") from exc
    if isinstance(data, list):
        return {"results": data}
    if not isinstance(data, dict):
        return {"results": []}
    return data


async def fetch(urls: list[str]) -> dict[str, Any]:
    """POST Fetch API using the documented {'urls': [...]} request body."""
    clean = list(dict.fromkeys(u.strip() for u in urls if isinstance(u, str) and u.strip()))[:10]
    if not clean:
        return {"results": []}
    for url in clean:
        if not url.startswith(("https://", "http://")):
            raise TinyFishError(f"Invalid source URL: {url!r}")
    async with httpx.AsyncClient(timeout=_timeout(), follow_redirects=True) as client:
        response = await client.post(
            FETCH_URL,
            headers={**_headers(), "Content-Type": "application/json"},
            json={"urls": clean},
        )
    _check(response)
    try:
        data = response.json()
    except ValueError as exc:
        raise TinyFishError("TinyFish Fetch returned non-JSON data.") from exc
    if isinstance(data, list):
        return {"results": data}
    if not isinstance(data, dict):
        return {"results": []}
    return data
