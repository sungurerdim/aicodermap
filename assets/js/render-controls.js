// Weights editor: slider/number rows, total badge, preset application,
// preset detection. Theme + lang sync helpers also live here since they
// drive control surfaces.

import {
  State, BENCH_KEYS, DEFAULT_WEIGHTS, PRESETS, STORAGE, writeStorage,
} from './core.js';
import { el, clear } from './dom.js';
import { t } from './i18n.js';
import { fmtDeployTime } from './data.js';

export function renderWeightsEditor(onChange) {
  const grid = document.getElementById('weights-grid');
  if (!grid) return;
  clear(grid);
  for (const k of BENCH_KEYS) {
    const row = el('div', { class: 'weight-row' });
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
  const preset = PRESETS[name];
  if (!preset) return;
  State.weights = { ...DEFAULT_WEIGHTS, ...preset };
  for (const k of BENCH_KEYS) if (State.weights[k] == null) State.weights[k] = 0;
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
  State.weights = { ...DEFAULT_WEIGHTS };
  writeStorage(STORAGE.weights, State.weights);
  const sel = document.getElementById('weights-preset');
  if (sel) sel.value = 'balanced';
  renderWeightsEditor(onChange);
  if (typeof onChange === 'function') onChange();
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
  const node = document.getElementById('footer-deployed-at');
  if (!node) return;
  const formatted = fmtDeployTime(State.dataDeployedAt);
  if (!formatted) return;
  const label = t('ui.footer.deployed') || 'Deployed';
  const sha = shortBuildHash(State.dataEtag);
  node.textContent = sha
    ? `${label}: ${formatted} · build ${sha}`
    : `${label}: ${formatted}`;
  node.title = `${State.dataDeployedAt}${State.dataEtag ? ` (etag ${State.dataEtag})` : ''}`;
  node.hidden = false;
}
