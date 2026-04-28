// Event wiring split by concern. Each wireXxx returns void; they are called
// once at bootstrap. switchLanguage lives here because it bridges language
// state into all visible surfaces.

import { State, STORAGE, writeStorage } from './core.js';
import { applyI18n, loadI18n } from './i18n.js';
import {
  applyPreset, resetWeights, syncPresetSelect, switchTheme, syncLangToggleUi,
  renderWeightsEditor, renderDeployStamp,
} from './render-controls.js';
import { renderAll, renderTable } from './render-table.js';
import { resolveGpuVram, updateGpuStatus, populateGpuSelect } from './gpu.js';
import { exportElement, hideTooltip } from './overlay.js';

export async function switchLanguage(lang) {
  const next = await loadI18n(lang);
  if (!next) return;
  State.i18n = next;
  State.lang = lang;
  writeStorage(STORAGE.language, lang);
  applyI18n(document);
  syncLangToggleUi();
  renderWeightsEditor(renderAll);
  renderAll();
  populateGpuSelect();
  syncPresetSelect();
  renderDeployStamp();
}

function wireLangToggle() {
  document.querySelectorAll('.lang-toggle button[data-lang]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const next = btn.dataset.lang;
      if (next && next !== State.lang) await switchLanguage(next);
    });
  });
}

function wireThemeToggle() {
  document.querySelectorAll('.theme-toggle button[data-theme]').forEach((btn) => {
    btn.addEventListener('click', () => switchTheme(btn.dataset.theme));
  });
}

function wirePresetSelect() {
  const sel = document.getElementById('weights-preset');
  if (!sel) return;
  sel.addEventListener('change', (e) => {
    const v = e.target.value;
    if (v && v !== 'custom') applyPreset(v, renderAll);
  });
}

function wireWeightsReset() {
  const btn = document.getElementById('weights-reset');
  if (!btn) return;
  btn.addEventListener('click', () => {
    resetWeights(renderAll);
    syncPresetSelect();
  });
}

function wireFiltersReset() {
  const btn = document.getElementById('filters-reset');
  if (!btn) return;
  btn.addEventListener('click', () => {
    const search = document.getElementById('filter-search');
    const deployment = document.getElementById('filter-deployment');
    const gpuSel = document.getElementById('filter-gpu-select');
    const vramOverride = document.getElementById('filter-vram-override');
    const tier = document.getElementById('filter-tier');
    const openOnly = document.getElementById('filter-open-only');

    if (search) search.value = '';
    if (deployment) deployment.value = 'all';
    if (vramOverride) vramOverride.value = '';
    if (tier) tier.value = 'all';
    if (openOnly) openOnly.checked = false;

    if (gpuSel) {
      const autoOpt = gpuSel.querySelector('option[value="auto"]');
      if (autoOpt && !autoOpt.disabled) gpuSel.value = 'auto';
      else gpuSel.selectedIndex = 0;
    }
    State.filters = { search: '', deployment: 'all', tier: 'all', openOnly: false };
    State.selectedGpu = gpuSel ? gpuSel.value : 'auto';
    resolveGpuVram();
    updateGpuStatus();
    writeStorage(STORAGE.filters, State.filters);
    writeStorage(STORAGE.gpu, State.selectedGpu);
    writeStorage(STORAGE.vram, State.vram);
    renderAll();
  });
}

function wireSearchInput() {
  const searchInput = document.getElementById('filter-search');
  if (!searchInput) return;
  let searchTimer = null;
  searchInput.addEventListener('input', (e) => {
    State.filters.search = String(e.target.value || '').trim();
    writeStorage(STORAGE.filters, State.filters);
    if (searchTimer) clearTimeout(searchTimer);
    searchTimer = setTimeout(renderAll, 200);
  });
}

function wireFilterControls() {
  const dep = document.getElementById('filter-deployment');
  if (dep) {
    dep.addEventListener('change', (e) => {
      State.filters.deployment = e.target.value;
      writeStorage(STORAGE.filters, State.filters);
      resolveGpuVram();
      updateGpuStatus();
      renderAll();
    });
  }
  const open = document.getElementById('filter-open-only');
  if (open) {
    open.addEventListener('change', (e) => {
      State.filters.openOnly = e.target.checked;
      writeStorage(STORAGE.filters, State.filters);
      renderAll();
    });
  }
  const tier = document.getElementById('filter-tier');
  if (tier) {
    tier.addEventListener('change', (e) => {
      State.filters.tier = e.target.value;
      writeStorage(STORAGE.filters, State.filters);
      renderAll();
    });
  }
}

function wireGpuControls() {
  const sel = document.getElementById('filter-gpu-select');
  if (sel) {
    sel.addEventListener('change', (e) => {
      State.selectedGpu = e.target.value;
      writeStorage(STORAGE.gpu, State.selectedGpu);
      resolveGpuVram();
      updateGpuStatus();
      renderAll();
    });
  }
  const vram = document.getElementById('filter-vram-override');
  if (vram) {
    vram.addEventListener('input', () => {
      resolveGpuVram();
      writeStorage(STORAGE.vram, State.vram);
      updateGpuStatus();
      renderAll();
    });
  }
}

function wireExports() {
  document.querySelectorAll('[data-export-trigger]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const sectionId = btn.getAttribute('data-export-trigger');
      const target = document.querySelector(`[data-export-section="${sectionId}"]`);
      if (target) exportElement(target, `aicodermap-${sectionId}`);
    });
  });
  const fullBtn = document.getElementById('export-full');
  if (fullBtn) {
    fullBtn.addEventListener('click', () => {
      const main = document.querySelector('main.app-main');
      if (main) exportElement(main, 'aicodermap-full');
    });
  }
}

function wireWindowEvents() {
  window.addEventListener('scroll', hideTooltip, { passive: true });
  window.addEventListener('resize', hideTooltip);
}

// Auto-clamp [data-tip] tooltips inside the viewport. CSS centers them on the
// host by default; when a host sits near the right or left edge the centered
// tooltip would overflow. We measure on hover/focus, estimate the tooltip's
// rendered width from the text length (the CSS max-width is 260px), and pick
// `start`, `end`, or default-center alignment so the tooltip never extends
// past the visible area.
function clampTooltip(host) {
  const text = host.getAttribute('data-tip') || '';
  if (!text) return;
  const r = host.getBoundingClientRect();
  const margin = 8;
  const estW = Math.min(260, text.length * 7 + 24);
  const cx = r.left + r.width / 2;
  if (cx - estW / 2 < margin) host.setAttribute('data-tip-align', 'start');
  else if (cx + estW / 2 > window.innerWidth - margin) host.setAttribute('data-tip-align', 'end');
  else host.removeAttribute('data-tip-align');
}

function wireTooltipClamp() {
  document.addEventListener('mouseover', (e) => {
    const t = e.target.closest && e.target.closest('[data-tip]');
    if (t) clampTooltip(t);
  }, { passive: true });
  document.addEventListener('focusin', (e) => {
    const t = e.target.closest && e.target.closest('[data-tip]');
    if (t) clampTooltip(t);
  });
}

export function wireEvents() {
  wireLangToggle();
  wireThemeToggle();
  wirePresetSelect();
  wireWeightsReset();
  wireFiltersReset();
  wireSearchInput();
  wireFilterControls();
  wireGpuControls();
  wireExports();
  wireWindowEvents();
  wireTooltipClamp();
  // Re-export for sort wiring inside renderTable; keeps reference live.
  void renderTable;
}
