// GPU compatibility, WebGPU detect, select population, VRAM resolution,
// status indicator, filter predicate.

import { State } from './core.js';
import { t } from './i18n.js';

const RAM_OFFLOAD_FACTOR = 2;
const MIN_OFFLOAD_LIMIT_GB = 8;
// OS + apps keep a slice of system RAM for themselves; only the remainder is
// realistically available to spill model weights into. 6GB VRAM + 8GB RAM →
// budget 6 + (8-4) = 10GB, so a 14GB model is correctly "too large".
const RAM_OS_RESERVE_GB = 4;

// System RAM realistically available for weight spill (OS reserve deducted).
function availableRam() {
  return Math.max(State.ram - RAM_OS_RESERVE_GB, 0);
}

// Spill budget beyond VRAM. Known system RAM (dropdown pick, else the
// navigator.deviceMemory floor — browsers cap it at 8, which only ever
// UNDER-estimates) → usable = ram - OS reserve. Unknown → the legacy
// 2×VRAM heuristic.
function offloadBudget(vram) {
  if (Number.isFinite(State.ram) && State.ram > 0) {
    return availableRam();
  }
  return Math.max(vram * RAM_OFFLOAD_FACTOR, MIN_OFFLOAD_LIMIT_GB);
}

export function resolveSystemRam() {
  const sel = document.getElementById('filter-ram-select');
  const picked = sel ? Number(sel.value) : NaN;
  if (Number.isFinite(picked) && picked > 0) {
    State.ram = picked;
    return;
  }
  const dm = (typeof navigator !== 'undefined' && Number(navigator.deviceMemory)) || NaN;
  State.ram = Number.isFinite(dm) && dm > 0 ? dm : null;
}

// A model is locally runnable when it ships a local tier, a known VRAM
// requirement, or at least one Unsloth quant variant. Lives here (not in the
// data layer) because GPU compatibility is its only consumer.
export function isLocalRunnable(m) {
  if (m.tier === 'ollama-local' || m.tier === 'gemma') return true;
  if (Number.isFinite(m.vramRequirement)) return true;
  // Variants without a real vram number can't participate in fit math
  // (gpuCompat filters them out and then labels the model "cloud"), so they
  // must not count as local-runnable either — else the fit view shows
  // cloud-badged rows.
  if (Array.isArray(m.unslothVariants) && m.unslothVariants.some(v => Number.isFinite(v.vram))) return true;
  return false;
}

export function gpuCompat(model, vram) {
  // Only variants with a real numeric vram are usable for fit math. A variant
  // whose vram is null/missing (extraction gap) must NOT participate: in JS
  // `null <= 16` is true (null→0), so an unfiltered null-vram variant would
  // falsely "fit" any GPU and render "Fits (null GB · <quant>)".
  const variants = (Array.isArray(model.unslothVariants) ? model.unslothVariants : [])
    .filter(v => Number.isFinite(v.vram));
  const hasUnsloth = variants.length > 0;
  const hasVramReq = Number.isFinite(model.vramRequirement);

  if (model.tier !== 'ollama-local' && !hasVramReq && !hasUnsloth) {
    return { kind: 'cloud', label: t('ui.compat.cloud') };
  }
  if (vram == null) {
    return { kind: 'unknown', label: '—' };
  }

  const offloadLimit = offloadBudget(vram);

  let bestVariant = null;
  if (hasUnsloth) {
    const sorted = [...variants].sort((a, b) => b.vram - a.vram);
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
    const smallest = [...variants].sort((a, b) => a.vram - b.vram)[0];
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

// WebGL renderer-string fallback. Browsers redact WebGPU adapter info far more
// aggressively than the long-standing WEBGL_debug_renderer_info extension, and
// Firefox ships no usable WebGPU at all — so when the WebGPU path yields
// nothing, the ANGLE/driver renderer string ("ANGLE (NVIDIA, NVIDIA GeForce
// RTX 4090 Direct3D11 ...)", "Apple M3 Pro") is matched generically against
// the gpu-database entry ids. No GPU names are hardcoded here: an entry id
// like "rtx-4090" or "m3-pro-18gb" is split into word tokens (RAM-size
// suffixes dropped) and every token must appear as a whole word in the
// renderer string; the most-specific match wins. Same-token entries that
// differ only by RAM size (Apple unified memory tiers) collapse into one
// 'approximate' result with the conservative (lowest) VRAM so a "fits" verdict
// is never optimistic.
const RAM_SUFFIX_RE = /^\d+gb$/;

function matchRendererString(raw) {
  const words = new Set(
    String(raw).toLowerCase().replace(/[^a-z0-9.]+/g, ' ').split(' ').filter(Boolean)
  );
  let best = null;
  for (const group of ['nvidia', 'apple', 'amd', 'intel']) {
    const list = State.gpu[group];
    if (!list) continue;
    for (const [id, info] of Object.entries(list)) {
      const tokens = id.split('-').filter(t => t && !RAM_SUFFIX_RE.test(t));
      if (!tokens.length || !tokens.every(t => words.has(t))) continue;
      const key = `${group}:${tokens.join('-')}`;
      const cand = { group, id, info, specificity: tokens.length, key };
      if (!best || cand.specificity > best.specificity) {
        best = { key, specificity: cand.specificity, matches: [cand] };
      } else if (cand.specificity === best.specificity && cand.key === best.key) {
        best.matches.push(cand);
      }
    }
  }
  if (!best) return null;
  const sorted = [...best.matches].sort(
    (a, b) => (Number(a.info.vram) || 0) - (Number(b.info.vram) || 0)
  );
  const low = sorted[0];
  if (sorted.length === 1) {
    return { id: `${low.group}.${low.id}`, detectionMode: 'exact', ...low.info };
  }
  const vrams = sorted.map(v => Number(v.info.vram)).filter(Number.isFinite);
  return {
    id: `${low.group}.${low.id}`,
    detectionMode: 'approximate',
    architectureLabel: String(low.info.displayName || '').replace(/\s*\d+\s*GB$/i, ''),
    vramRange: [vrams[0], vrams[vrams.length - 1]],
    ...low.info,
    vram: vrams[0],
  };
}

function detectGpuWebGL() {
  try {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (!gl) return null;
    const ext = gl.getExtension('WEBGL_debug_renderer_info');
    const raw = gl.getParameter(ext ? ext.UNMASKED_RENDERER_WEBGL : gl.RENDERER);
    if (!raw) return null;
    return matchRendererString(raw);
  } catch (_) {
    return null;
  }
}

export async function detectGpu() {
  try {
    if (!('gpu' in navigator) || !navigator.gpu) return detectGpuWebGL();
    const adapter = await navigator.gpu.requestAdapter();
    if (!adapter) return detectGpuWebGL();
    let info = adapter.info;
    if (!info && typeof adapter.requestAdapterInfo === 'function') {
      info = await adapter.requestAdapterInfo();
    }
    if (!info) return detectGpuWebGL();

    const vendor = (info.vendor || '').toLowerCase().replace(/\s+/g, '_');
    const arch = (info.architecture || '').toLowerCase();
    const device = (info.device || '').toLowerCase().replace(/\s+/g, '_');
    const vmap = State.gpu.webgpuVendorMap || {};
    // Support old flat format (no byModel key) for backwards compat during transition
    const byModel = (vmap.byModel && typeof vmap.byModel === 'object') ? vmap.byModel : vmap;
    const byArch = vmap.byArchitecture || null;

    // 1. byModel exact match — tries vendor+device, vendor+arch, vendor alone, device alone
    const modelKeys = [
      vendor && device ? `${vendor}_${device}` : '',
      vendor && arch ? `${vendor}_${arch.replace(/-/g, '_')}` : '',
      vendor,
      device,
    ].filter(Boolean);
    for (const c of modelKeys) {
      const path = byModel[c];
      if (!path) continue;
      const [g, m] = path.split('.');
      const found = State.gpu[g]?.[m];
      if (found) return { id: path, detectionMode: 'exact', ...found };
    }

    // 2. byArchitecture family fallback — WebGPU returns arch strings like "ada-lovelace"
    if (byArch && arch) {
      const entry = byArch[arch];
      if (entry) {
        const [g, m] = entry.fallbackId.split('.');
        const base = State.gpu[g]?.[m] || {};
        const vram = base.vram ?? (entry.vramRange
          ? Math.round((entry.vramRange[0] + entry.vramRange[1]) / 2)
          : null);
        return {
          id: entry.fallbackId,
          detectionMode: 'approximate',
          architectureLabel: entry.label,
          vramRange: entry.vramRange,
          ...base,
          vram,
        };
      }
    }

    // 3. WebGL renderer-string fallback — WebGPU exposed an adapter but its
    // info matched nothing in the database (or was redacted to empty strings).
    const webgl = detectGpuWebGL();
    if (webgl) return webgl;

    // 4. Privacy-stripped: both paths yielded no usable device identity
    if (!vendor && !arch && !device) {
      return { id: null, detectionMode: 'privacy-stripped' };
    }

    return { id: null, detectionMode: 'unknown', vendor, arch };
  } catch (_) {
    return detectGpuWebGL();
  }
}

export function populateGpuSelect() {
  const sel = document.getElementById('filter-gpu-select');
  if (!sel) return;
  while (sel.options.length > 1) sel.remove(1);

  // ⭐ Featured presets — the eight everyday hardware tiers the dropdown
  // surfaces first so the user can pick "RTX 4090 24GB" without scrolling
  // through 100+ entries. Each id resolves to a canonical vendor.entry row.
  const featured = Array.isArray(State.gpu.featuredPresets) ? State.gpu.featuredPresets : [];
  if (featured.length) {
    const popLabel = t('ui.filter.gpuPopular') || 'Popular hardware';
    const ogPop = document.createElement('optgroup');
    ogPop.label = '⭐ ' + popLabel;
    const ordered = [...featured].sort((a, b) => (a.orderHint || 99) - (b.orderHint || 99));
    for (const p of ordered) {
      const path = String(p.id || '');
      const dot = path.indexOf('.');
      if (dot < 0) continue;
      const g = path.slice(0, dot);
      const id = path.slice(dot + 1);
      const info = State.gpu[g] && State.gpu[g][id];
      if (!info) continue;
      const opt = document.createElement('option');
      opt.value = path;
      opt.textContent = `${info.displayName || id} — ${info.vram} GB`;
      ogPop.appendChild(opt);
    }
    if (ogPop.children.length) sel.appendChild(ogPop);
  }

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

// One-click bridge from "VRAM is known" (auto-detected OR picked) to the
// local-fit list view. Auto-detect resolves a VRAM silently on page load, but
// flipping the Deploy filter for the user unasked would be surprising — the
// button makes the action explicit and single-click instead of hunting the
// Deploy select. Label toggles to "show all" while the fit view is active.
function syncGpuFitToggle() {
  const btn = document.getElementById('gpu-fit-toggle');
  if (!btn) return;
  if (!Number.isFinite(State.vram) || State.vram <= 0) {
    btn.hidden = true;
    return;
  }
  btn.hidden = false;
  btn.textContent = State.filters.deployment === 'local'
    ? (t('ui.filter.showAllDeploy') || 'Show all models')
    : `${t('ui.filter.showFitting') || 'Show models that fit'} (~${State.vram} GB)`;
}

export function updateGpuStatus() {
  syncGpuFitToggle();
  const status = document.getElementById('gpu-status');
  const sel = document.getElementById('filter-gpu-select');
  if (!status || !sel) return;

  const detected = State.detectedGpu;
  const detectedUsable = !!(detected && (Number.isFinite(detected.vram) || detected.vramRange));

  const autoOpt = sel.querySelector('option[value="auto"]');

  // webgpuUnsupported — only when WebGPU is absent AND the WebGL renderer
  // fallback also failed; a successful WebGL detection keeps auto usable.
  // Only show the error message (and return) when VRAM is also unknown —
  // a manually-typed VRAM value should still produce a budget note below.
  if ((!('gpu' in navigator) || !navigator.gpu) && !detectedUsable) {
    if (autoOpt) {
      autoOpt.disabled = true;
      autoOpt.title = t('ui.filter.gpuAutoUnavailable') || '';
      if (sel.value === 'auto') sel.value = '';
    }
    if (State.vram == null) {
      status.textContent = t('compat.errors.webgpuUnsupported') || 'WebGPU not supported — select GPU manually';
      return;
    }
    // VRAM was typed manually — fall through to show budget note below.
  }

  // Privacy-stripped path: WebGPU present but browser hid all device info.
  // Same logic: only exit early when there is no manual VRAM to display.
  if (detected?.detectionMode === 'privacy-stripped') {
    if (autoOpt) {
      autoOpt.disabled = true;
      if (sel.value === 'auto') sel.value = '';
    }
    if (State.vram == null) {
      status.textContent = t('ui.filter.gpuPrivacyStripped') || 'GPU detected — browser hides device info, select GPU manually';
      return;
    }
  }

  if (autoOpt) {
    if (detected && (Number.isFinite(detected.vram) || detected.vramRange)) {
      autoOpt.disabled = false;
      const suffix = detected.detectionMode === 'approximate'
        ? ` · ${detected.architectureLabel || ''}`
        : '';
      autoOpt.title = `${detected.id || '?'}${suffix} (~${detected.vram ?? '?'} GB)`;
    } else {
      autoOpt.disabled = true;
      autoOpt.title = t('ui.filter.gpuAutoUnavailable') || 'Auto-detect unavailable in this browser';
      if (sel.value === 'auto') sel.value = '';
    }
  }

  // Update the RAM dropdown's "Auto" option to show the detected/inferred value
  // so users can see what budget is actually being applied.
  const ramSel = document.getElementById('filter-ram-select');
  if (ramSel) {
    const ramAutoOpt = ramSel.querySelector('option[value=""]');
    if (ramAutoOpt && ramSel.value === '') {
      const autoBase = t('ui.filter.ramAuto') || 'Auto';
      ramAutoOpt.textContent = Number.isFinite(State.ram) && State.ram > 0
        ? `${autoBase} (~${State.ram} GB)`
        : autoBase;
    }
  }

  const vramKnown = Number.isFinite(State.vram) && State.vram > 0;
  const ramKnown  = Number.isFinite(State.ram)  && State.ram  > 0;
  const budget = vramKnown && ramKnown
    ? State.vram + availableRam()
    : null;
  const totalSuffix = budget != null
    ? ` + RAM → ~${budget} GB ${t('ui.filter.totalBudget') || 'total'}`
    : '';

  if (!vramKnown) {
    if (ramKnown) {
      const offload = availableRam();
      status.textContent = `RAM: ~${offload} GB ${t('ui.filter.ramOffload') || 'offload budget'}`;
    } else {
      status.textContent = autoOpt && autoOpt.disabled
        ? (t('ui.filter.gpuAutoUnavailable') || 'Auto-detect unavailable')
        : '';
    }
  } else if (detected?.detectionMode === 'approximate') {
    const approxLabel = t('ui.filter.gpuApproximate') || 'approx.';
    status.textContent = `~${State.vram} GB · ${detected.architectureLabel || ''} (${approxLabel})${totalSuffix}`;
  } else {
    status.textContent = `~${State.vram} GB${totalSuffix}`;
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
      // Fit view keeps ONLY models with a positive verdict. 'unknown'/'cloud'
      // (no usable VRAM data) are as unactionable as 'too-large' here — a row
      // the user can't actually run must not survive the fit filter.
      const c = gpuCompat(model, State.vram);
      if (c.kind !== 'fits' && c.kind !== 'offload') return false;
    }
  }
  return true;
}
