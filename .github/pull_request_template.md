## Summary

<!-- One paragraph: what changes and why. -->

## Type of change

- [ ] Data refresh (output of `/aicodermap` skill — `data/*.json` + `CHANGELOG.md`)
- [ ] Code change (`assets/js/`, `assets/css/`, `index.html`)
- [ ] Tooling change (`scripts/`, `auto/`)
- [ ] Documentation change (`docs/`, `README.md`, `CLAUDE.md`)
- [ ] Repo config / metadata

## Constraints respected

- [ ] No new runtime dependency added (vanilla HTML/CSS/JS only)
- [ ] No build step introduced (must work directly off `main` on GitHub Pages)
- [ ] No GitHub Actions / workflows / CI files added
- [ ] If a vendored library was changed, its SHA-256 in `docs/IMPLGUIDE.md`
      and the SRI hash in `index.html` are both updated
- [ ] If UI strings were touched, both `i18n/tr.json` and `i18n/en.json`
      were updated (parity is enforced)

## Testing

- [ ] Opened the site under `python -m http.server 8000` and walked through
      `docs/TEST_PLAN.md` (or the affected ACs)
- [ ] `assets/test/smoke.html` passes (14/14)
- [ ] Lint clean (`ruff check scripts/ auto/` + `node scripts/regex-lint.js`)
- [ ] If schema changed, `data/models.json` still validates against
      `assets/js/core.js` `validateModels()` (smoke covers this)

## Screenshots

<!-- Required for any visible UI change. Light + dark themes if applicable. -->
