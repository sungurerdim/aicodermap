# Security Policy

## Reporting a vulnerability

Please report security issues privately by emailing
**sungurerdim@gmail.com** rather than opening a public issue. Include:

- A clear description of the issue
- Steps to reproduce or a proof-of-concept
- Impact assessment (what an attacker could do)

You can expect an initial reply within 7 days. Coordinated disclosure
timelines will be agreed before any public write-up.

## In scope

- The static site at <https://sungurerdim.github.io/aicodermap/>
- The data pipeline under `scripts/` and `auto/` and the JSON files
  under `data/`
- The vendored copy of `assets/vendor/html2canvas.min.js` (SHA-256
  pinned in `docs/IMPLGUIDE.md` and via SRI in `index.html`)

## Out of scope

- Third-party services we only link to (vendor leaderboards, Ollama,
  Hugging Face, etc.) — please report directly to those projects
- Issues requiring physical access or social engineering
- Reports against the public benchmark numbers themselves — open a
  normal data-correction issue instead

## Supported versions

This is a single rolling deployment from `main`. Only the latest
commit is supported. There are no LTS branches.
