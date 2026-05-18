"""Shared utility helpers — stdlib-only.

Consolidates functions previously duplicated across:
  - scripts/lib/whitelist.py   (URL parsing)
  - scripts/merge.py           (URL normalization, JSON load)
  - scripts/verification-map.py (domain extraction)
  - scripts/prefetch-leaderboards.py (retry/backoff)
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def normalize_url(url: str) -> str:
    """Return a canonical URL string: strip trailing slashes + lowercase scheme+host."""
    if not url:
        return ""
    try:
        p = urlparse(url.strip())
        host = (p.hostname or "").lower()
        path = p.path.rstrip("/")
        rest = f"{p.params}{'?' + p.query if p.query else ''}{'#' + p.fragment if p.fragment else ''}"
        return f"{p.scheme.lower()}://{host}{path}{rest}"
    except Exception:
        return url.strip().rstrip("/")


def extract_domain(url: str) -> str:
    """Return hostname without www. prefix."""
    if not url:
        return ""
    try:
        host = urlparse(url.strip()).hostname or ""
        return host.lower().lstrip("www.")
    except Exception:
        return ""


def safe_json_load(path: str | Path, default: Any = None) -> Any:
    """Load JSON from path; return default on any error (file missing, parse error)."""
    try:
        with open(path, encoding="utf-8") as fp:
            return json.load(fp)
    except (OSError, json.JSONDecodeError, ValueError):
        return default


def retry_with_backoff(
    fn,
    *args,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    backoff: float = 2.0,
    **kwargs,
) -> Any:
    """Call fn(*args, **kwargs) up to max_attempts times with exponential backoff.

    Raises the last exception when all attempts are exhausted.
    """
    delay = base_delay
    last_exc: Exception | None = None
    for attempt in range(max_attempts):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            last_exc = exc
            if attempt < max_attempts - 1:
                time.sleep(delay)
                delay *= backoff
    raise last_exc  # type: ignore[misc]


def ensure_list(value: Any) -> list:
    """Coerce scalar / None to a list; pass through existing lists."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base; returns a new dict."""
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result
