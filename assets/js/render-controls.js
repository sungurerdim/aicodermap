// Weights editor: slider/number rows, total badge, preset application,
// preset detection. Theme + lang sync helpers also live here since they
// drive control surfaces.

import {
  State, BENCH_KEYS, DEFAULT_WEIGHTS, PRESETS, STORAGE, writeStorage, readStorage,
  getPresets,
} from './core.js';
import { el, clear } from './dom.js';
import { t } from './i18n.js';
import { fmtDeployTime } from './data.js';

export function renderWeightsEditor(onChange) {
  const grid = document.getElementById('weights-grid');
  if (!grid) return;
  clear(grid);
  const activePreset = detectMatchingPreset(State.weights);
  const presets = getPresets();
  const presetMap = (activePreset !== 'custom')
    ? (presets[activePreset] || PRESETS[activePreset])
    : null;
  for (const k of BENCH_KEYS) {
    const row = el('div', { class: 'weight-row' });
    if (presetMap && !(presetMap[k] > 0)) row.classList.add('excluded');
    const benchName = t(`benchmarks.${k}.name`);
    row.appendChild(el('span', { class: 'label' }, benchName));

    const controls = el('div', { class: 'controls' });
    const range = el('input', {
      type: 'range', min: '0', max: '100', step: '1',
      'aria-label': benchName,
    });
    const num = el('input', {
      type: 'number', min: '0', max: '100', step: '1',
      inputmode: 'numeric',
      'aria-label': `${benchName} (numeric)`,
    });
    const startVal = String(State.weights[k] ?? 0);
    range.value = startVal;
    num.value = startVal;
    range.style.setProperty('--val', startVal);

    range.addEventListener('input', () => {
      num.value = range.value;
      range.style.setProperty('--val', range.value);
      onWeightChange(k, range, onChange);
    });
    num.addEventListener('input', () => {
      range.value = num.value;
      range.style.setProperty('--val', range.value);
      onWeightChange(k, num, onChange);
    });

    controls.appendChild(range);
    controls.appendChild(num);
    row.appendChild(controls);
    grid.appendChild(row);
  }
  updateWeightsTotal();
}

function onWeightChange(key, input, onChange) {
  let v = Number(input.value);
  if (!Number.isFinite(v)) v = 0;
  v = Math.max(0, Math.min(100, Math.round(v)));
  input.value = String(v);
  State.weights[key] = v;
  syncPresetSelect();
  writeStorage(STORAGE.weights, State.weights);
  updateWeightsTotal();
  if (typeof onChange === 'function') onChange();
}

export function updateWeightsTotal() {
  const total = BENCH_KEYS.reduce((a, k) => a + (State.weights[k] || 0), 0);
  const totalEl = document.getElementById('weights-total');
  if (!totalEl) return;
  totalEl.textContent = String(total);
  totalEl.classList.toggle('invalid', total !== 100);
  totalEl.title = total !== 100 ? t('ui.weights.totalWarn') : '';
}

export function applyPreset(name, onChange) {
  // F1+F2 (2026-05-18): prefer schema-driven presets via getPresets() if
  // available; fallback to literal PRESETS. New 'consensus' preset is
  // vendorConsensus kind — no atomic weights; render uses vendorConsensusScore.
  const presetSource = getPresets();
  const preset = (presetSource && presetSource[name]) || PRESETS[name];
  if (!preset) return;
  const kind = preset.__kind || 'atomicComposite';
  State.scoreFn = (kind === 'vendorConsensus') ? 'vendorConsensus' : 'aicm';
  State.activePresetName = name;
  // Zero-base merge: every preset is the full intended distribution.
  State.weights = Object.fromEntries(BENCH_KEYS.map(k => [k, preset[k] || 0]));
  writeStorage(STORAGE.weights, State.weights);
  renderWeightsEditor(onChange);
  if (typeof onChange === 'function') onChange();
}

export function detectMatchingPreset(weights) {
  for (const [name, preset] of Object.entries(PRESETS)) {
    if (BENCH_KEYS.every(k => (weights[k] || 0) === (preset[k] || 0))) return name;
  }
  return 'custom';
}

export function syncPresetSelect() {
  const sel = document.getElementById('weights-preset');
  if (!sel) return;
  sel.value = detectMatchingPreset(State.weights);
}

export function resetWeights(onChange) {
  // Reset = default preset = swe-focused (was balanced).
  applyPreset('swe-focused', onChange);
}

export function applyTheme(theme) {
  const t2 = (theme === 'light' || theme === 'dark') ? theme : 'dark';
  document.documentElement.setAttribute('data-theme', t2);
  document.querySelectorAll('.theme-toggle button[data-theme]').forEach((btn) => {
    const active = btn.dataset.theme === t2;
    btn.classList.toggle('active', active);
    btn.setAttribute('aria-pressed', String(active));
  });
}

export function switchTheme(theme) {
  if (theme !== 'dark' && theme !== 'light') return;
  applyTheme(theme);
  writeStorage(STORAGE.theme, theme);
}

// Provider/vendor filter dropdown — options derived at bootstrap time from
// data/models.json so adding a new vendor surfaces in the filter without UI
// edits. Sorted by descending model count, ties alphabetical.
export function populateProviderFilter() {
  const sel = document.getElementById('filter-provider');
  if (!sel) return;
  while (sel.options.length > 1) sel.remove(1);
  const counts = new Map();
  for (const m of State.models) {
    const p = m.provider;
    if (!p) continue;
    counts.set(p, (counts.get(p) || 0) + 1);
  }
  const sorted = [...counts.entries()].sort(
    (a, b) => b[1] - a[1] || a[0].localeCompare(b[0]),
  );
  for (const [name, n] of sorted) {
    const opt = document.createElement('option');
    opt.value = name;
    opt.textContent = `${name} (${n})`;
    sel.appendChild(opt);
  }
  if (State.filters.provider && State.filters.provider !== 'all'
      && [...sel.options].some(o => o.value === State.filters.provider)) {
    sel.value = State.filters.provider;
  }
}

// F6 (2026-05-18): "Compare prices to" baseline dropdown removed — feature
// only affected the table's blended-price column and was not discoverable.
// Single price baseline (cheapest) is more honest + simpler UX.

export function syncLangToggleUi() {
  document.querySelectorAll('.lang-toggle button[data-lang]').forEach((btn) => {
    const active = btn.dataset.lang === State.lang;
    btn.classList.toggle('active', active);
    btn.setAttribute('aria-pressed', String(active));
  });
}

// Footer chip "Deployed: 2026-04-28 14:07 UTC · build a1b2c3d" — Last-Modified
// timestamp from the Pages CDN plus a short hash derived from the ETag (GitHub
// Pages computes ETag from file contents, so distinct deploys never share it).
// Re-rendered on language switch so the prefix follows the active locale.
function shortBuildHash(etag) {
  if (!etag || typeof etag !== 'string') return null;
  const hex = etag.replace(/^W\//, '').replace(/^"|"$/g, '').split('-')[0] || '';
  return hex ? hex.slice(-7) : null;
}

export function renderDeployStamp() {
  const node = document.getElementById('deployed-at');
  if (!node) return;
  const formatted = fmtDeployTime(State.dataDeployedAt);
  if (!formatted) return;
  const label = t('ui.footer.deployed') || 'Deployed';
  const meta = State.meta && typeof State.meta === 'object' ? State.meta : null;
  // Prefer the build SHA + cycle telemetry the merge step writes into
  // data/_meta.json. Fall back to the ETag-derived short hash (legacy).
  const sha = (meta && typeof meta.buildSha === 'string' && meta.buildSha !== 'unknown')
    ? meta.buildSha
    : shortBuildHash(State.dataEtag);
  const fillRatioPct = (meta && Number.isFinite(meta.fillRatio))
    ? Math.round(meta.fillRatio * 100)
    : null;
  const cellLine = (meta && Number.isFinite(meta.filledCells) && Number.isFinite(meta.totalCells))
    ? ` · ${meta.filledCells}/${meta.totalCells}`
    : '';
  const ratioLine = (fillRatioPct != null) ? ` · ${fillRatioPct}%` : '';
  const buildLine = sha ? ` · build ${sha}` : '';
  node.textContent = `${label}: ${formatted}${buildLine}${ratioLine}${cellLine}`;
  const titleParts = [State.dataDeployedAt];
  if (State.dataEtag) titleParts.push(`etag ${State.dataEtag}`);
  if (meta && meta.cycleId) titleParts.push(`cycle ${meta.cycleId}`);
  if (meta && meta.lastCycleToolCallCount != null) {
    titleParts.push(`tools=${meta.lastCycleToolCallCount}`);
  }
  if (meta && meta.lastCycleBatchCount != null) {
    titleParts.push(`batches=${meta.lastCycleBatchCount}`);
  }
  node.title = titleParts.filter(Boolean).join(' · ');
  node.hidden = false;
}
