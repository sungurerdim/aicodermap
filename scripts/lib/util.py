"""Shared utility helpers — stdlib-only.

Consolidates functions previously duplicated across:
  - scripts/lib/whitelist.py   (URL parsing)
  - scripts/merge.py           (URL normalization, JSON load)
  - scripts/verification-map.py (domain extraction)
  - scripts/prefetch-leaderboards.py (retry/backoff)
"""

from __future__ import annotations

import json
import re
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


# A bare minor-version number written with a space after a token that ends in
# a digit. The trailing negative lookahead `(?![\w.])` deliberately skips
# numbers followed by a unit letter (param sizes: "27B", "9B") or another dot
# (already-dotted versions: "3.5"), so only true version-dot anomalies match.
_VERSION_DOT_PAT = re.compile(r"(\b\w*\d)[ ]+(\d+)(?![\w.])")


# Whitespace that doubles as a thousands separator (BIPM): space, tab, NBSP,
# thin-space, narrow-no-break, figure-space.
_THOUSANDS_WS = "\t     "
_WS_RE = re.compile(f"[{re.escape(_THOUSANDS_WS)}]")
_COMMA_THOUSANDS_RE = re.compile(r"^\d{1,3}(,\d{3})+$")


def parse_locale_decimal(raw: str | float | int | None) -> float | None:
    """Parse a captured numeric string under `_localeDecimalRule` (SSOT in
    sources-whitelist.json `_schema.regexLibrary`). Returns a float or None.

    Handles 87.6, 87,6, 1,234.56, 1.234,56, 1 234,56 (BIPM thin-space + EU
    decimal). Rule: strip whitespace thousands separators; if both '.' and ','
    are present the RIGHTMOST is the decimal separator and the other is
    thousands (stripped); if only ',' is present it is thousands when it matches
    the d{1,3}(,d{3})+ grouping, else decimal. Apply ONLY to an already-captured
    numeric token — never inside the extraction regex.
    """
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    if not isinstance(raw, str):
        return None
    s = _WS_RE.sub("", raw.strip())
    if not s:
        return None
    # Keep a leading sign + percent stripped.
    s = s.rstrip("%")
    has_dot, has_comma = "." in s, "," in s
    if has_dot and has_comma:
        # Rightmost separator is the decimal point; the other is thousands.
        dec = "." if s.rfind(".") > s.rfind(",") else ","
        other = "," if dec == "." else "."
        s = s.replace(other, "")
        s = s.replace(dec, ".")
    elif has_comma:
        if _COMMA_THOUSANDS_RE.match(s):
            s = s.replace(",", "")  # thousands grouping
        else:
            s = s.replace(",", ".")  # decimal comma
    # '.'-only or digits-only fall through unchanged (treated as decimal).
    try:
        return float(s)
    except ValueError:
        return None


def canonical_display_name(name: str) -> str:
    """Standardize a model display name's version separator (model-agnostic).

    "Qwen3 7 Max" -> "Qwen3.7 Max"; leaves "Gemma 3 27B", "Qwen 3.5 9B" and
    "GPT-5.5" untouched. Verified against the full model set to change only the
    two genuine version-dot anomalies. Applied in merge.py before each refresh
    write so future slug-derived names self-correct without per-model patches.
    """
    if not name or not isinstance(name, str):
        return name
    return _VERSION_DOT_PAT.sub(r"\1.\2", name)


def normalize_anomaly_verdict(v: dict) -> dict:
    """Coerce an anomaly-verify verdict to the canonical schema the
    validate/apply scripts consume, tolerating the natural shape an LLM agent
    emits. Maps: `verdict`->`action`; list `evidence`->'; '-joined string;
    `correctedBenchKey`->`toBench`; `correctedValue`->`toValue`; `note`->`reason`
    (kept only if `reason` absent). Idempotent — re-normalizing is a no-op."""
    if not isinstance(v, dict):
        return v
    out = dict(v)
    if not out.get("action") and out.get("verdict"):
        out["action"] = out["verdict"]
    ev = out.get("evidence")
    if isinstance(ev, list):
        out["evidence"] = "; ".join(str(u) for u in ev if u)
    elif ev is None:
        out["evidence"] = ""
    if not out.get("toBench") and out.get("correctedBenchKey"):
        out["toBench"] = out["correctedBenchKey"]
    if out.get("toValue") is None and out.get("correctedValue") is not None:
        out["toValue"] = out["correctedValue"]
    if not (out.get("reason") or "").strip() and (out.get("note") or "").strip():
        out["reason"] = out["note"]
    return out
