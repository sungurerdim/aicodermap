# Contributing to AICoderMap

AICoderMap is a solo, manually-curated coding-LLM tracker. Contributions are
welcome — please keep them focused and small.

## Issues

Open an issue for:
- Stale or incorrect benchmark data (link the source you checked)
- Missing models that meet the inclusion criteria (see `docs/PRD.md`)
- Cross-source contradictions we should flag
- UI bugs or accessibility regressions

## Pull requests

- **Code:** vanilla HTML / CSS / JS only — no build step, no runtime
  dependencies. New libraries must be vendored under `assets/vendor/` with
  the SHA-256 recorded in `docs/IMPLGUIDE.md`.
- **Schema:** any `data/*.json` change must follow the schema in
  `docs/TECHSPEC.md` (multi-provider pricing, schema v2).
- **Provenance:** every benchmark score added or changed needs ≥ 2
  independent sources cited in `data/sources.json`.
- **i18n:** new UI copy must be added to both `i18n/tr.json` and
  `i18n/en.json` — TR/EN parity is enforced.
- **Changelog:** append a date-stamped entry to `CHANGELOG.md`.

## Data refresh workflow

`data/*.json` files are regenerated through the project skill described in
`docs/WORKFLOW.md`. Please do **not** hand-edit `models.json` or
`sources.json` for routine data refreshes — submit source-tier changes
(`data/sources-whitelist.json`) instead and let the skill recompute the rest.

## License

By contributing you agree your contribution is licensed under the MIT
License (see `LICENSE`).
