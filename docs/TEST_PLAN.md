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

Expected: 14 tests pass when served over HTTP. Opening via `file://` will
fail the live-data test (modules + fetch require HTTP).

## End-to-end acceptance (manual)

Walk through every row in a single browser session. Both Chromium (WebGPU
support) and Firefox (no WebGPU) recommended for parity coverage.

| AC | Scenario | Expected |
|----|----------|----------|
| AC1 | First load with empty `localStorage` | TR locale if browser lang starts with `tr`, otherwise EN. Dark theme. Default weights sum 100. 53 models render with `loading` placeholder gone. |
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

## Regression checks per refresh

After running `/aicodermap` and committing:

- Smoke test still passes (`smoke.html`)
- 53+ models render with no console errors
- TR ↔ EN parity preserved (`scripts/regex-lint.js` for whitelist; manual scan for new keys)
- Dark + light themes both legible (visual check)
- Screen reader: tab through header → filters → weights → table → cards (NVDA / VoiceOver / Orca)
- Lighthouse a11y ≥ 90, Best Practices ≥ 90 (Chromium DevTools)

## Known limitations

- No automated browser harness (Playwright / Puppeteer would require npm,
  which violates `CLAUDE.md` "no node_modules" discipline). The smoke harness
  catches regressions in pure functions; UI behaviour requires manual sweep.
- WebGPU detection works only on Chromium-class browsers. Firefox falls back
  to manual VRAM input — exercise both paths.
