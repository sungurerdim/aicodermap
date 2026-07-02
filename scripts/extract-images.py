#!/usr/bin/env python3
"""
Vendor-blog image extractor for OCR pipeline.

Given one or more vendor blog/announcement URLs, fetches each page,
extracts every <img src=...> URL (incl. Next.js _next/image proxy →
underlying CDN URL via the `url=` query param), downloads to
/tmp/aicodermap-img-<sha8>.<ext>, and prints a JSON map:

    {
      "<page_url>": [
        {"local": "/tmp/aicodermap-img-abc12345.png", "src": "https://...", "size": 42762},
        ...
      ]
    }

The skill orchestrator then Reads each local file (vision-aware) to
extract bench tables from images that vendor blogs ship as PNG.

Usage: python scripts/extract-images.py <url1> [<url2> ...]
"""

import argparse
import hashlib
import json
import os
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request

CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 AICoderMap/extract-images"}

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".aicodermap-images"
)
os.makedirs(OUT_DIR, exist_ok=True)


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
        return r.read(), r.headers.get("Content-Type", "")


def resolve_next_image(src):
    if "_next/image" not in src:
        return src
    qs = urllib.parse.urlparse(src).query
    params = urllib.parse.parse_qs(qs)
    inner = params.get("url", [None])[0]
    return inner or src


def absolutize(base, src):
    if src.startswith("http"):
        return src
    if src.startswith("//"):
        return "https:" + src
    if src.startswith("/"):
        return (
            urllib.parse.urlparse(base)
            ._replace(path=src, query="", fragment="")
            .geturl()
        )
    return src


def extract_image_urls(page_html, page_url):
    pat = re.compile(r'<img[^>]+src=["\']([^"\']+\.(?:png|jpg|jpeg|webp))', re.I)
    raw = pat.findall(page_html)
    out = []
    seen = set()
    for s in raw:
        if s.startswith("data:"):
            continue
        u = absolutize(page_url, s)
        u = resolve_next_image(u)
        if u in seen:
            continue
        seen.add(u)
        out.append(u)
    return out


def download(url):
    try:
        data, ct = fetch(url)
        if not (ct.startswith("image/") or len(data) > 2000):
            return None
        digest = hashlib.sha1(url.encode()).hexdigest()[:8]
        ext = "png"
        m = re.search(r"\.(png|jpg|jpeg|webp)(\?|$)", url, re.I)
        if m:
            ext = m.group(1).lower()
        if ext == "jpeg":
            ext = "jpg"
        local = os.path.join(OUT_DIR, f"aicodermap-img-{digest}.{ext}")
        with open(local, "wb") as f:
            f.write(data)
        return {"local": local, "src": url, "size": len(data)}
    except urllib.error.HTTPError as e:
        return {"src": url, "error": f"HTTP {e.code}"}
    except Exception as e:
        return {"src": url, "error": f"{type(e).__name__}: {str(e)[:80]}"}


def main(urls):
    results = {}
    for page_url in urls:
        try:
            html_bytes, _ = fetch(page_url)
            html = html_bytes.decode("utf-8", "replace")
        except Exception as e:
            results[page_url] = {
                "error": f"page fetch failed: {type(e).__name__}: {str(e)[:80]}"
            }
            continue
        img_urls = extract_image_urls(html, page_url)
        downloads = []
        for u in img_urls[:8]:  # cap per page
            d = download(u)
            if d:
                downloads.append(d)
        results[page_url] = downloads
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download bench-bearing images referenced by the given pages."
    )
    parser.add_argument("urls", nargs="+", help="page URLs to scan")
    main(parser.parse_args().urls)
