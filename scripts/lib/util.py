"""Shared utility helpers — stdlib-only.

Consolidates functions previously duplicated across:
  - scripts/lib/whitelist.py   (URL parsing)
  - scripts/merge.py           (JSON load)
  - scripts/verification-map.py (domain extraction)
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def configure_utf8_output() -> None:
    """Force UTF-8 stdout/stderr on Windows (cp1254 default mangles ✓/⚠/✗).

    getattr keeps the type checker happy (reconfigure is missing from the
    TextIO stub). SSOT — was duplicated in ~20 scripts with 3 idioms."""
    for stream in (sys.stdout, sys.stderr):
        reconf = getattr(stream, "reconfigure", None)
        if callable(reconf):
            try:
                reconf(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


def utc_now_iso() -> str:
    """Current UTC instant as `YYYY-MM-DDTHH:MM:SSZ`. SSOT — was duplicated as
    _utc_now_iso() in prefetch-leaderboards.py + source-health-probe.py."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_iso() -> str:
    """Local calendar date as `YYYY-MM-DD`. SSOT for the per-cell date stamp
    convention (`fetched`/`benchUpdated` fields)."""
    return date.today().isoformat()


def read_json(path: str | Path) -> Any:
    """Strict UTF-8 JSON load — raises on missing file / parse error.
    Use `safe_json_load` when a default-on-error is wanted."""
    with open(path, encoding="utf-8") as fp:
        return json.load(fp)


def write_json(path: str | Path, obj: Any, *, indent: int = 2) -> None:
    """UTF-8 JSON dump with trailing newline (matches repo convention)."""
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(obj, fp, ensure_ascii=False, indent=indent)
        fp.write("\n")


def slug_norm(s: str) -> str:
    """Aggressive slug/name normalization for fuzzy matching: lowercase + drop
    every non-alphanumeric so 'Qwen3.6-Max', 'qwen3-6-max', 'Qwen 3.6 Max'
    collapse to the same key. SSOT — was duplicated as _norm() in
    extract-aa-rsc.py + gen-bench-keys.py."""
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def extract_domain(url: str | None) -> str:
    """Return hostname without the `www.` prefix. None/empty → "".

    Uses removeprefix (exact-prefix strip), NOT lstrip — lstrip("www.") strips
    the CHARACTER SET {w,.,o}, so it mangled openrouter.ai->penrouter.ai,
    openai.com->penai.com, ollama.com->llama.com. removeprefix is Py3.9+."""
    if not url:
        return ""
    try:
        host = (urlparse(url.strip()).hostname or "").lower()
        return host.removeprefix("www.")
    except Exception:
        return ""


def safe_json_load(path: str | Path, default: Any = None) -> Any:
    """Load JSON from path; return default on any error (file missing, parse error)."""
    try:
        with open(path, encoding="utf-8") as fp:
            return json.load(fp)
    except (OSError, json.JSONDecodeError, ValueError):
        return default


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


# A name that is still a raw id-slug: all-lowercase, hyphen-separated, no spaces
# (e.g. "minimax-m3" that leaked from the id because lineup discovery supplied no
# display name). Already-human-formatted names ("MiniMax M2.7", "Gemma 3 27B",
# "GPT-5.5") have uppercase and/or spaces, so they never match — that is what
# makes the slug-repair below safe to run on every model unconditionally.
_SLUG_NAME_PAT = re.compile(r"[a-z0-9]+(?:-[a-z0-9.]+)+")
# A version-ish token: optional letter prefix + a digit (+ dotted minors).
# "m2", "m2.7", "v4", "5", "0528" — used both to join digit fragments with a dot
# and to decide uppercasing. NOT "pro"/"max"/"flash" (no digit → Title-cased).
_VERSION_TOKEN_PAT = re.compile(r"^[a-z]*\d[\d.]*$")


def _compact(s: str) -> str:
    """Lowercased alphanumerics only — for matching a provider against id tokens
    ("MiniMax" -> "minimax", "Z AI" -> "zai")."""
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _case_token(tok: str) -> str:
    """Title-case one designator token. Version tokens uppercase their letter
    prefix ("m2.7"->"M2.7", "v4"->"V4", "0528"->"0528"); param sizes keep their
    unit ("27b"->"27B"); plain words Title-case ("pro"->"Pro")."""
    if re.match(r"^[a-z]+\d", tok):
        return re.sub(r"^[a-z]+", lambda m: m.group().upper(), tok)
    if re.match(r"^\d", tok):
        return tok.upper()
    return tok[:1].upper() + tok[1:]


def _slug_to_display(slug: str, provider: str | None) -> str:
    """Rebuild a human display name from a raw id-slug, model-agnostic.

    "minimax-m3"   + provider "MiniMax" -> "MiniMax M3"
    "minimax-m2-7" + provider "MiniMax" -> "MiniMax M2.7"
    Brand casing is taken verbatim from `provider` when it prefixes the slug
    (the provider field is the canonical brand); otherwise the leading token is
    Title-cased generically. Version digit-fragments are joined with a dot.
    """
    tokens = slug.split("-")
    # Join trailing pure-digit fragments onto the preceding version token so
    # "m2","7" becomes "m2.7" (the id splits a minor version across a hyphen).
    merged: list[str] = []
    for t in tokens:
        if t.isdigit() and merged and _VERSION_TOKEN_PAT.match(merged[-1]):
            merged[-1] = f"{merged[-1]}.{t}"
        else:
            merged.append(t)
    # Consume the leading tokens that spell out the provider, and substitute the
    # provider's exact casing for them.
    brand_tokens = 0
    if provider:
        pc = _compact(provider)
        acc = ""
        for i, t in enumerate(merged):
            acc += _compact(t)
            if acc == pc:
                brand_tokens = i + 1
                break
            if not pc.startswith(acc):
                break
    parts = [provider] if brand_tokens else []
    parts += [_case_token(t) for t in merged[brand_tokens:]]
    return " ".join(p for p in parts if p).strip()


def canonical_display_name(name: str, provider: str | None = None) -> str:
    """Standardize a model display name (model-agnostic, SSOT).

    Two layers, both safe to run on every model on every refresh:
      1. Version-dot fix: "Qwen3 7 Max" -> "Qwen3.7 Max" (leaves "Gemma 3 27B",
         "Qwen 3.5 9B", "GPT-5.5" untouched).
      2. Slug repair: a name that is still a raw lowercase id-slug
         ("minimax-m3") is rebuilt into "<Brand> <Designator>" ("MiniMax M3"),
         using `provider` for the brand's canonical casing. Already-formatted
         names (any uppercase or space) skip this layer entirely, so it can
         never corrupt a good name — only promote a leaked slug.

    Applied in merge.py before each refresh write + enforced by AC12, so every
    path (agent output, lineup stubs, synth) self-corrects without per-model
    patches and new/unknown models are covered the moment they land.
    """
    if not name or not isinstance(name, str):
        return name
    fixed = _VERSION_DOT_PAT.sub(r"\1.\2", name)
    if _SLUG_NAME_PAT.fullmatch(fixed):
        return _slug_to_display(fixed, provider)
    return fixed


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
