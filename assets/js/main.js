// Bootstrap entry. Split into focused phases so each phase reads top-to-bottom
// at <50 lines.

import {
  State, STORAGE, DEFAULT_WEIGHTS, PRESETS, readStorage, validateWeights,
} from './core.js';
import { loadI18n, applyI18n } from './i18n.js';
import { loadData } from './data.js';
import {
  detectGpu, populateGpuSelect, resolveGpuVram, resolveSystemRam, updateGpuStatus,
} from './gpu.js';
import { el, clear } from './dom.js';
import {
  applyTheme, syncLangToggleUi, renderWeightsEditor, syncPresetSelect,
  renderDeployStamp, populateProviderFilter, applyPreset,
} from './render-controls.js';
import { renderAll } from './render-table.js';
import { renderPrivacyTable } from './render-privacy.js';
import { wireEvents } from './events.js';
import { startFreshnessWatch } from './freshness.js';
import { readUrlState, applyUrlState, pushUrlState } from './url-state.js';

function bootstrapTheme() {
  const storedTheme = readStorage(STORAGE.theme, null);
  let initialTheme;
  if (storedTheme === 'light' || storedTheme === 'dark') {
    initialTheme = storedTheme;
  } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
    initialTheme = 'light';
  } else {
    initialTheme = 'dark';
  }
  applyTheme(initialTheme);

  if (window.matchMedia && !storedTheme) {
    try {
      window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', (e) => {
        if (!readStorage(STORAGE.theme, null)) applyTheme(e.matches ? 'light' : 'dark');
      });
    } catch (_) { /* older browsers ignore */ }
  }
}

function bootstrapPrefs() {
  const storedLang = readStorage(STORAGE.language, null);
  const navLang = (navigator.language || '').toLowerCase();
  State.lang = (storedLang === 'en' || storedLang === 'tr')
    ? storedLang
    : (navLang.startsWith('tr') ? 'tr' : 'en');

  const storedWeights = readStorage(STORAGE.weights, null);
  const validW = validateWeights(storedWeights);
  // Default preset is swe-focused for first-time visitors (product decision
  // 2026-06-10: coding lens by default; vendor-consensus preset stays one
  // click away). The schema-driven weights need loadData(), so bootstrap()
  // re-applies the preset after data lands; the literal here is only a
  // pre-data placeholder. Track whether the user has stored weights so we
  // know whether to overwrite.
  State.weights = validW || (function buildPlaceholder() {
    const out = Object.fromEntries(
      Object.keys(DEFAULT_WEIGHTS).map(k => [k, 0]),
    );
    Object.assign(out, PRESETS['swe-focused'] || {});
    return out;
  }());
  State._weightsAreDefault = !validW;

  const storedFilters = readStorage(STORAGE.filters, null);
  if (storedFilters && typeof storedFilters === 'object') {
    State.filters = { ...State.filters, ...storedFilters };
    if (storedFilters.gpuOnly === true && !storedFilters.deployment) {
      State.filters.deployment = 'local';
    }
    delete State.filters.gpuOnly;
    if (!['all', 'cloud', 'local'].includes(State.filters.deployment)) {
      State.filters.deployment = 'all';
    }
    if (typeof State.filters.search !== 'string') State.filters.search = '';
  }

  const storedSort = readStorage(STORAGE.sort, null);
  if (storedSort && typeof storedSort === 'object'
      && typeof storedSort.col === 'string'
      && (storedSort.dir === 'asc' || storedSort.dir === 'desc')) {
    State.sort = { col: storedSort.col, dir: storedSort.dir };
  }

  State.selectedGpu = readStorage(STORAGE.gpu, 'auto');
  const storedVram = readStorage(STORAGE.vram, null);
  if (Number.isFinite(storedVram)) State.vram = storedVram;
  const storedRam = readStorage(STORAGE.ram, null);
  if (Number.isFinite(storedRam)) State.ram = storedRam;
}

async function bootstrapI18n() {
  const [primary, fallback] = await Promise.all([
    loadI18n(State.lang),
    State.lang === 'tr' ? null : loadI18n('tr'),
  ]);
  State.i18n = primary || (await loadI18n('tr')) || {};
  State.i18nFallback = fallback || State.i18n;
  applyI18n(document);
  syncLangToggleUi();
}

async function bootstrapData() {
  try {
    await loadData();
    return true;
  } catch (e) {
    console.error('data load failed', e);
    const errMsg = (State.i18n?.ui?.errors?.fetchFailed) || 'Failed to load data';
    const list = document.getElementById('models-list');
    if (list) {
      clear(list);
      list.appendChild(el('p', { class: 'loading' }, errMsg));
    }
    // The comparison table renders nothing on failure — surface the same
    // message there so the section isn't a silent blank.
    const tbody = document.querySelector('#comparison-table tbody');
    if (tbody) {
      clear(tbody);
      const td = el('td', { class: 'loading' }, errMsg);
      tbody.appendChild(el('tr', {}, td));
    }
    return false;
  }
}


function restoreFilterUi() {
  const dep = document.getElementById('filter-deployment');
  if (dep) dep.value = State.filters.deployment;
  const open = document.getElementById('filter-open-only');
  if (open) open.checked = !!State.filters.openOnly;
  const tier = document.getElementById('filter-tier');
  if (tier) tier.value = State.filters.tier;
  const provider = document.getElementById('filter-provider');
  if (provider && State.filters.provider
      && [...provider.options].some(o => o.value === State.filters.provider)) {
    provider.value = State.filters.provider;
  }
  const searchEl = document.getElementById('filter-search');
  if (searchEl) searchEl.value = State.filters.search || '';
}

async function bootstrapGpu() {
  populateGpuSelect();
  State.detectedGpu = await detectGpu();

  const sel = document.getElementById('filter-gpu-select');
  if (!sel) return;

  if (State.detectedGpu) {
    if (State.selectedGpu && State.selectedGpu !== 'auto'
        && [...sel.options].some(o => o.value === State.selectedGpu)) {
      sel.value = State.selectedGpu;
    } else {
      sel.value = 'auto';
      State.selectedGpu = 'auto';
    }
  } else {
    sel.value = State.selectedGpu;
  }

  if (Number.isFinite(State.vram) && State.selectedGpu === 'auto' && !State.detectedGpu) {
    const vramEl = document.getElementById('filter-vram-override');
    if (vramEl) vramEl.value = String(State.vram);
  }

  // Stored RAM pick (storage holds only explicit dropdown picks; Auto = null →
  // resolveSystemRam falls back to navigator.deviceMemory).
  const ramSel = document.getElementById('filter-ram-select');
  if (ramSel && Number.isFinite(State.ram)
      && [...ramSel.options].some(o => Number(o.value) === State.ram)) {
    ramSel.value = String(State.ram);
  }

  resolveGpuVram();
  resolveSystemRam();
  updateGpuStatus();
}

async function bootstrap() {
  // Single page-load cache-bust token applied to every JSON fetch (data + i18n)
  // so GitHub Pages CDN cannot serve stale data after a refresh push. Same
  // token across every fetch keeps the page's view internally consistent.
  window.__ACM_CACHE_BUST__ = String(Date.now());
  bootstrapTheme();
  bootstrapPrefs();

  // URL params override localStorage at first load — this is what makes a
  // shared link reproducible across machines / browsers / sessions.
  const urlState = readUrlState();
  if (urlState.theme) {
    applyTheme(urlState.theme);
  }
  applyUrlState(urlState);
  // Preset application is deferred until renderWeightsEditor is bound below,
  // so urlState.preset just gets recorded and consumed at sync time.
  window.__ACM_URL_PRESET__ = urlState.preset || null;

  await bootstrapI18n();

  const ok = await bootstrapData();
  if (!ok) return;

  renderDeployStamp();
  populateProviderFilter();
  restoreFilterUi();
  await bootstrapGpu();

  renderWeightsEditor(renderAll);
  // Preset resolution order: URL deep link > stored preset name > swe-focused
  // default for first-time visitors. The stored NAME (not just weights) is
  // needed to restore consensus, which has no atomic weights to match on.
  // `?preset=custom` is already covered: applyUrlState() set the weights.
  const urlPreset = window.__ACM_URL_PRESET__;
  const storedPreset = readStorage(STORAGE.preset, null);
  if (urlPreset && urlPreset !== 'custom') {
    applyPreset(urlPreset);
  } else if (!urlPreset && storedPreset === 'consensus') {
    applyPreset('consensus');
  } else if (!urlPreset && State._weightsAreDefault) {
    applyPreset('swe-focused');
  }
  syncPresetSelect();
  renderAll();
  renderPrivacyTable();
  wireEvents();
  // Push the resolved state back into the URL so that the address bar always
  // reflects what the page is showing — including localStorage-driven defaults.
  pushUrlState({ immediate: true });

  // sources.json loads in the background (2MB — no longer blocks first
  // render). Re-render once provenance lands so contradiction flags, source
  // counts and confidence-weighted scores appear.
  if (State.sourcesReady) {
    State.sourcesReady.then((sources) => {
      if (sources && Object.keys(sources).length) renderAll();
    });
  }

  // Watch for a fresh deploy by polling models.json's ETag (GitHub Pages
  // content hash) on a delay + 5min interval + tab-visibility change.
  // Triggers the banner the moment the user's tab is visible after a push.
  startFreshnessWatch();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootstrap);
} else {
  bootstrap();
}
