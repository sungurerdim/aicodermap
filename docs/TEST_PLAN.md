# Test Plan

This is the manual smoke + acceptance runbook for AICoderMap. The project's
"no npm" discipline rules out heavyweight test frameworks; this document plus
`assets/test/smoke.html` is the test surface.

## Quick start

1. From the project root, start a static server: `python -m http.server 8000`.
2. Open `http://localhost:8000/assets/test/smoke.html` — the unit smoke runs
   automatically and prints PASS/FAIL counts.
3. Open `http://localhost:8000/index.html` and walk through the AC scenarios
   below.

## Unit smoke (`assets/test/smoke.html`)

Covers the data layer in isolation:

- Schema validation (`validateModels`, `validateWeights`, `isValidModel`)
- Composite score weighted-average math
- Score-class thresholds + formatters (`fmtScore`, `fmtContext`)
- Multi-provider pricing legacy-bridge
- Contradiction detection (≥2 sources, Δ thresholds)
- Local-runnable detection
- GPU compatibility branches: cloud, unknown, fits, too-large
- Live data fetch (`loadData`) — requires HTTP server

Expected: ~50+ assertions pass when served over HTTP (the harness counts
each `row()` call). The summary line at the bottom shows `N pass · 0 fail`.
Opening via `file://` will fail the live-data and i18n-parity tests
(modules + fetch require HTTP).

## End-to-end acceptance (manual)

Walk through every row in a single browser session. Both Chromium (WebGPU
support) and Firefox (no WebGPU) recommended for parity coverage.

| AC | Scenario | Expected |
|----|----------|----------|
| AC1 | First load with empty `localStorage` | TR locale if browser lang starts with `tr`, otherwise EN. Dark theme. Default weights sum 100. 55 models render with `loading` placeholder gone. |
| AC2 | Switch language EN ↔ TR via segmented control | All `data-i18n-key` text updates, `<html lang>` updates, persisted to `localStorage`. |
| AC3 | Switch theme dark ↔ light | `html[data-theme]` flips, palette swaps, persisted to `localStorage`. Subsequent reload honours the choice. |
| AC4 | Move a weight slider | Numeric input mirrors slider, total badge updates, "Custom" preset is selected, table + cards re-rank. |
| AC5 | Apply a preset (Balanced / SWE-focused / Agentic / Benchmark only) | Weights update to preset values; total = 100; rankings update. |
| AC6 | Reset weights | Defaults restored, preset = Balanced, total = 100. |
| AC7 | Filter — search | Typing "claude" narrows table + cards (debounced ~200 ms). Empty search restores all. |
| AC8 | Filter — deployment = local + Auto-detect GPU (Chromium only) | Models that exceed VRAM are hidden; remaining show `fits`/`offload` badge. |
| AC9 | Filter — deployment = local + manual VRAM (e.g., 12 GB) | Same behaviour without WebGPU detection. |
| AC10 | Tier filter (Frontier / Open Tier-1 / Local Ollama) + Open weights only | Compound filtering works — both predicates apply. |
| AC11 | Click a contradiction flag (⚠ or 🚨) | Tooltip appears with provenance list (source URL, tier, date, value). |
| AC12 | Sort by any column header | Ascending / descending toggle; visual indicator (▲/▼) updates. |
| AC13 | PNG export — section + full page | `html2canvas` produces a PNG download for weights, comparison-table, model card, full page. UI chrome (`[data-no-export]`) is hidden during export. Failure path → toast (no blocking `alert`). |
| AC14 | Privacy & Compliance section | `#privacy` table renders rows (cookies, analytics, localStorage scope) sourced from `i18n/{lang}.json`. No console errors. |
| AC15 | Freshness banner | Force a stale `data/models.json` lastUpdated > 14 days ago via DevTools edit — banner appears with `Refresh` + `Dismiss` buttons; clicking Refresh cache-busts the fetch; Dismiss persists for the session. |
| AC16 | Pricing baseline filter | When more than one provider exists for a model, the `Compare prices to` dropdown is shown; picking a baseline rewrites per-row delta columns; `none` restores raw prices. |
| AC17 | Skip-to-content link | Tab once from the page top — `Skip to content` appears at top-left, focuses; pressing Enter jumps focus into the `#filters` section. |
| AC18 | SEO — structured data | Open the page in [Google Rich Results Test](https://search.google.com/test/rich-results) — Dataset + WebSite + SoftwareApplication schemas detected with no errors. |
| AC19 | SEO — sitemap & robots | `GET /sitemap.xml` returns valid XML with TR + EN + x-default; `GET /robots.txt` references the sitemap and disallows `/assets/test/`. |
| AC20 | Lighthouse — Chromium DevTools, mobile preset, performance + a11y + best-practices + SEO ≥ 90 each | All four scores ≥ 90; archive HTML report under `docs/lighthouse/<YYYY-MM-DD>.html` (gitignored). |

## Regression checks per refresh

After running `/aicodermap` and committing:

- Smoke test still passes (`smoke.html`)
- 55+ models render with no console errors
- TR ↔ EN parity preserved (`scripts/regex-lint.js` for whitelist; manual scan for new keys)
- Dark + light themes both legible (visual check)
- Screen reader: tab through header → filters → weights → table → cards (NVDA / VoiceOver / Orca)
- Lighthouse a11y ≥ 90, Best Practices ≥ 90 (Chromium DevTools)

## Lighthouse runbook (M4 polish gate)

1. Serve locally: `python -m http.server 8000`.
2. In Chromium / Edge: open DevTools → **Lighthouse** tab.
3. Categories: Performance + Accessibility + Best Practices + SEO. Mode: Navigation. Device: Mobile (default Lighthouse preset).
4. **Analyze** — capture the four scores. All four MUST be ≥ 90.
5. Save the HTML report under `docs/lighthouse/<YYYY-MM-DD>-mobile.html` (gitignored).
6. Repeat with Device: Desktop. Save as `<YYYY-MM-DD>-desktop.html`.
7. If any score drops below 90:
   - Performance — check for layout shift, oversized images, blocking scripts.
   - Accessibility — verify focus rings, ARIA labels, contrast (especially light theme).
   - Best Practices — CSP / SRI / referrer-policy / permissions-policy / no console errors.
   - SEO — canonical / hreflang / meta description / structured data validity.
8. Re-run after every fix until all four ≥ 90; commit only when both reports clean.

## Known limitations

- No automated browser harness (Playwright / Puppeteer would require npm,
  which violates `CLAUDE.md` "no node_modules" discipline). The smoke harness
  catches regressions in pure functions; UI behaviour requires manual sweep.
- WebGPU detection works only on Chromium-class browsers. Firefox falls back
  to manual VRAM input — exercise both paths.
- The Lighthouse runbook is manual-only — no CI integration is planned
  (see `CLAUDE.md` "no GitHub Actions" policy).
