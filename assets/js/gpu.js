// GPU compatibility, WebGPU detect, select population, VRAM resolution,
// status indicator, filter predicate.

import { State } from './core.js';
import { t } from './i18n.js';
import { isLocalRunnable } from './data.js';

const RAM_OFFLOAD_FACTOR = 2;
const MIN_OFFLOAD_LIMIT_GB = 8;

export function gpuCompat(model, vram) {
  const hasUnsloth = Array.isArray(model.unslothVariants) && model.unslothVariants.length > 0;
  const hasVramReq = Number.isFinite(model.vramRequirement);

  if (model.tier !== 'ollama-local' && !hasVramReq && !hasUnsloth) {
    return { kind: 'cloud', label: t('ui.compat.cloud') };
  }
  if (vram == null) {
    return { kind: 'unknown', label: '—' };
  }

  const offloadLimit = Math.max(vram * RAM_OFFLOAD_FACTOR, MIN_OFFLOAD_LIMIT_GB);

  let bestVariant = null;
  if (hasUnsloth) {
    const sorted = [...model.unslothVariants].sort((a, b) => b.vram - a.vram);
    bestVariant = sorted.find(v => v.vram <= vram) || null;
  }

  if (bestVariant) {
    const needed = bestVariant.vram;
    const detail = `${needed} GB · ${bestVariant.name}`;
    if (needed <= vram - 1) return { kind: 'fits', label: `${t('ui.compat.fits')} (${detail})`, variant: bestVariant };
    return { kind: 'offload', label: `${t('ui.compat.offload')} (${detail})`, variant: bestVariant };
  }

  if (hasVramReq) {
    const needed = model.vramRequirement;
    if (needed <= vram - 1) return { kind: 'fits', label: `${t('ui.compat.fits')} (${needed} GB)`, variant: null };
    if (needed <= vram) return { kind: 'offload', label: `${t('ui.compat.offload')} (${needed} GB)`, variant: null };
    const offload = needed - vram;
    if (offload <= offloadLimit) {
      return { kind: 'offload', label: `${t('ui.compat.offload')} (${needed} GB · +${offload} GB RAM)`, variant: null };
    }
  }

  if (hasUnsloth) {
    const smallest = [...model.unslothVariants].sort((a, b) => a.vram - b.vram)[0];
    const offload = smallest.vram - vram;
    if (offload <= offloadLimit) {
      return {
        kind: 'offload',
        label: `${t('ui.compat.offload')} (${smallest.vram} GB · ${smallest.name} · +${offload} GB RAM)`,
        variant: smallest,
      };
    }
    return {
      kind: 'too-large',
      label: `${t('ui.compat.tooLarge')} (min ${smallest.vram} GB · ${smallest.name})`,
      variant: null,
    };
  }
  if (hasVramReq) {
    return {
      kind: 'too-large',
      label: `${t('ui.compat.tooLarge')} (${model.vramRequirement} GB)`,
      variant: null,
    };
  }
  return { kind: 'unknown', label: '—' };
}

export async function detectGpu() {
  try {
    if (!('gpu' in navigator) || !navigator.gpu) return null;
    const adapter = await navigator.gpu.requestAdapter();
    if (!adapter) return null;
    let info = adapter.info;
    if (!info && typeof adapter.requestAdapterInfo === 'function') {
      info = await adapter.requestAdapterInfo();
    }
    if (!info) return null;
    const vendor = (info.vendor || '').toLowerCase().replace(/\s+/g, '_');
    const arch = (info.architecture || info.device || '').toLowerCase().replace(/\s+/g, '_');
    const candidates = [`${vendor}_${arch}`, vendor, arch];
    for (const c of candidates) {
      const path = State.gpu.webgpuVendorMap?.[c];
      if (path) {
        const [g, m] = path.split('.');
        const found = State.gpu[g]?.[m];
        if (found) return { id: path, ...found };
      }
    }
    return { id: null, vendor, arch, raw: info };
  } catch (_) {
    return null;
  }
}

export function populateGpuSelect() {
  const sel = document.getElementById('filter-gpu-select');
  if (!sel) return;
  while (sel.options.length > 1) sel.remove(1);

  const groups = [
    ['nvidia', 'NVIDIA'],
    ['apple', 'Apple Silicon'],
    ['amd', 'AMD'],
    ['intel', 'Intel'],
  ];
  for (const [g, label] of groups) {
    const list = State.gpu[g];
    if (!list) continue;
    const og = document.createElement('optgroup');
    og.label = label;
    for (const [id, info] of Object.entries(list)) {
      const opt = document.createElement('option');
      opt.value = `${g}.${id}`;
      opt.textContent = `${info.displayName || id} — ${info.vram} GB`;
      og.appendChild(opt);
    }
    sel.appendChild(og);
  }
}

export function effectiveVram(info) {
  if (!info) return null;
  const v = Number(info.vram);
  if (!Number.isFinite(v)) return null;
  return v;
}

export function resolveGpuVram() {
  const overrideEl = document.getElementById('filter-vram-override');
  const override = overrideEl ? Number(overrideEl.value) : NaN;
  if (Number.isFinite(override) && override > 0) {
    State.vram = override;
    return;
  }
  if (State.selectedGpu === 'auto') {
    if (State.detectedGpu && Number.isFinite(State.detectedGpu.vram)) {
      State.vram = effectiveVram(State.detectedGpu);
      return;
    }
    State.vram = null;
    return;
  }
  const [g, m] = State.selectedGpu.split('.');
  const info = State.gpu[g]?.[m];
  State.vram = info ? effectiveVram(info) : null;
}

export function updateGpuStatus() {
  const status = document.getElementById('gpu-status');
  const sel = document.getElementById('filter-gpu-select');
  if (!status || !sel) return;

  const autoOpt = sel.querySelector('option[value="auto"]');
  const detected = State.detectedGpu;

  if (autoOpt) {
    if (detected && Number.isFinite(detected.vram)) {
      autoOpt.disabled = false;
      autoOpt.title = `${detected.id || detected.raw || ''} (~${detected.vram} GB)`;
    } else {
      autoOpt.disabled = true;
      autoOpt.title = t('ui.filter.gpuAutoUnavailable') || 'Auto-detect unavailable in this browser';
      if (sel.value === 'auto') sel.value = '';
    }
  }

  if (State.vram == null) {
    status.textContent = autoOpt && autoOpt.disabled
      ? (t('ui.filter.gpuAutoUnavailable') || 'Auto-detect unavailable')
      : '';
  } else {
    status.textContent = `~${State.vram} GB`;
  }
}

export function getActiveVram() {
  if (State.filters.deployment === 'local') {
    if (Number.isFinite(State.vram) && State.vram > 0) return State.vram;
  }
  return null;
}

export function passesFilters(model) {
  const f = State.filters;
  if (f.openOnly && !model.open) return false;
  if (f.tier !== 'all' && model.tier !== f.tier) return false;
  if (f.provider && f.provider !== 'all' && model.provider !== f.provider) return false;

  if (f.search) {
    const q = f.search.toLowerCase();
    const haystack = [model.name, model.id, model.provider, model.license]
      .filter(Boolean).join(' ').toLowerCase();
    if (!haystack.includes(q)) return false;
  }

  const local = isLocalRunnable(model);
  if (f.deployment === 'cloud') {
    if (local) return false;
  } else if (f.deployment === 'local') {
    if (!local) return false;
    if (Number.isFinite(State.vram) && State.vram > 0) {
      const c = gpuCompat(model, State.vram);
      if (c.kind === 'too-large') return false;
    }
  }
  return true;
}
