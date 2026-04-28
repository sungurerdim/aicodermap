// Bootstrap entry. Split into focused phases so each phase reads top-to-bottom
// at <50 lines.

import {
  State, STORAGE, DEFAULT_WEIGHTS, readStorage, validateWeights,
} from './core.js';
import { loadI18n, applyI18n } from './i18n.js';
import { loadData } from './data.js';
import {
  detectGpu, populateGpuSelect, resolveGpuVram, updateGpuStatus,
} from './gpu.js';
import { el, clear } from './dom.js';
import {
  applyTheme, syncLangToggleUi, renderWeightsEditor, syncPresetSelect,
  renderDeployStamp, populateProviderFilter,
} from './render-controls.js';
import { renderAll } from './render-table.js';
import { wireEvents } from './events.js';
import { startFreshnessWatch } from './freshness.js';

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
  State.weights = validW || { ...DEFAULT_WEIGHTS };

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
    const list = document.getElementById('models-list');
    if (list) {
      clear(list);
      const errMsg = (State.i18n?.ui?.errors?.fetchFailed) || 'Failed to load data';
      list.appendChild(el('p', { class: 'loading' }, errMsg));
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

  resolveGpuVram();
  updateGpuStatus();
}

async function bootstrap() {
  // Single page-load cache-bust token applied to every JSON fetch (data + i18n)
  // so GitHub Pages CDN cannot serve stale data after a refresh push. Same
  // token across every fetch keeps the page's view internally consistent.
  window.__ACM_CACHE_BUST__ = String(Date.now());
  bootstrapTheme();
  bootstrapPrefs();
  await bootstrapI18n();

  const ok = await bootstrapData();
  if (!ok) return;

  renderDeployStamp();
  populateProviderFilter();
  restoreFilterUi();
  await bootstrapGpu();

  renderWeightsEditor(renderAll);
  syncPresetSelect();
  renderAll();
  wireEvents();

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
