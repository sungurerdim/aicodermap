// URL state codec — turns the live filters/weights/sort/lang into shareable
// query-string parameters and back. Named query keys (no opaque base64) so
// CLI consumers (curl + jq) can construct deep-links by hand and humans can
// read the URL. State precedence at bootstrap: URL params override
// localStorage; localStorage seeds the defaults.
//
// Keys:
//   lang        — tr | en
//   preset      — balanced | swe-focused | agentic-focused | reasoning-focused | benchmark-only | custom
//   w           — comma-separated benchKey:weight pairs; only honoured when preset=custom
//   tier        — frontier | open-flagship | coder-specialized | gemma | ollama-local | all
//   deployment  — all | cloud | local
//   provider    — vendor name (URL-encoded) | all
//   vram        — integer GB (1..256)
//   gpu         — webgpu vendor key from gpu-database.json | auto
//   open        — 1 | 0 (open-license only filter)
//   search      — substring (URL-encoded)
//   sort        — <colKey>-<asc|desc>
//   theme       — dark | light

import { State, BENCH_KEYS, DEFAULT_WEIGHTS, validateWeights } from './core.js';

const VALID_PRESETS = new Set([
  'balanced', 'swe-focused', 'agentic-focused', 'reasoning-focused', 'benchmark-only', 'custom',
]);
const VALID_TIERS = new Set([
  'all', 'frontier', 'open-flagship', 'coder-specialized', 'gemma', 'ollama-local',
]);
const VALID_DEPLOY = new Set(['all', 'cloud', 'local']);
const VALID_THEME = new Set(['dark', 'light']);
const VALID_LANG = new Set(['tr', 'en']);

function parseWeights(raw) {
  if (!raw) return null;
  const out = {};
  for (const pair of raw.split(',')) {
    const [k, v] = pair.split(':');
    if (!k || v == null) return null;
    const n = Number(v);
    if (!Number.isFinite(n)) return null;
    out[k.trim()] = n;
  }
  // Fill missing keys with 0 so validateWeights sees the full BENCH_KEYS shape.
  const full = Object.fromEntries(BENCH_KEYS.map((k) => [k, 0]));
  for (const k of Object.keys(out)) if (BENCH_KEYS.includes(k)) full[k] = out[k];
  return validateWeights(full);
}

function serializeWeights(weights) {
  // Emit only non-zero keys, ordered by weight desc, then key alpha — keeps URL short.
  const entries = BENCH_KEYS
    .map((k) => [k, weights[k] || 0])
    .filter(([, v]) => v > 0)
    .sort(([ka, va], [kb, vb]) => (vb - va) || ka.localeCompare(kb));
  return entries.map(([k, v]) => `${k}:${v}`).join(',');
}

export function readUrlState() {
  const out = {};
  let params;
  try {
    params = new URLSearchParams(window.location.search);
  } catch (_) {
    return out;
  }

  const lang = params.get('lang');
  if (lang && VALID_LANG.has(lang)) out.lang = lang;

  const theme = params.get('theme');
  if (theme && VALID_THEME.has(theme)) out.theme = theme;

  const preset = params.get('preset');
  if (preset && VALID_PRESETS.has(preset)) out.preset = preset;

  if (out.preset === 'custom') {
    const w = parseWeights(params.get('w'));
    if (w) out.weights = w;
  }

  const tier = params.get('tier');
  if (tier && VALID_TIERS.has(tier)) out.tier = tier;

  const deployment = params.get('deployment');
  if (deployment && VALID_DEPLOY.has(deployment)) out.deployment = deployment;

  const provider = params.get('provider');
  if (provider) out.provider = provider;

  const vramRaw = params.get('vram');
  if (vramRaw != null && vramRaw !== '') {
    const n = Number(vramRaw);
    if (Number.isFinite(n) && n >= 0 && n <= 256) out.vram = Math.round(n);
  }

  const gpu = params.get('gpu');
  if (gpu) out.gpu = gpu;

  const open = params.get('open');
  if (open === '1' || open === 'true') out.openOnly = true;
  else if (open === '0' || open === 'false') out.openOnly = false;

  const search = params.get('search');
  if (search != null) out.search = search;

  const sort = params.get('sort');
  if (sort && /^[a-zA-Z0-9_-]+-(asc|desc)$/.test(sort)) {
    const idx = sort.lastIndexOf('-');
    out.sort = { col: sort.slice(0, idx), dir: sort.slice(idx + 1) };
  }

  return out;
}

export function applyUrlState(urlState) {
  if (!urlState || typeof urlState !== 'object') return;
  if (urlState.lang) State.lang = urlState.lang;
  if (urlState.weights) State.weights = urlState.weights;
  if (urlState.tier) State.filters.tier = urlState.tier;
  if (urlState.deployment) State.filters.deployment = urlState.deployment;
  if (urlState.provider) State.filters.provider = urlState.provider;
  if (urlState.search != null) State.filters.search = urlState.search;
  if (typeof urlState.openOnly === 'boolean') State.filters.openOnly = urlState.openOnly;
  if (Number.isFinite(urlState.vram)) State.vram = urlState.vram;
  if (urlState.gpu) State.selectedGpu = urlState.gpu;
  if (urlState.sort) State.sort = urlState.sort;
  // theme + preset are applied via callers (theme requires DOM mutation,
  // preset requires the preset registry; both happen in main.js after this).
}

function presetOf(weights) {
  // Returns the preset name when current weights exactly match a registered
  // preset; otherwise 'custom'. Used to keep URL share-string compact.
  // Imported here so we can avoid a top-level circular dependency.
  // eslint-disable-next-line global-require
  // (we can't require in module land — fall back to 'custom' if no match)
  if (!weights) return 'custom';
  const sumA = Object.values(weights).reduce((a, b) => a + (b || 0), 0);
  if (Math.abs(sumA - 100) > 0.01) return 'custom';
  // Compare with DEFAULT_WEIGHTS first (most common case).
  let allMatch = true;
  for (const k of BENCH_KEYS) {
    if ((weights[k] || 0) !== (DEFAULT_WEIGHTS[k] || 0)) { allMatch = false; break; }
  }
  return allMatch ? 'balanced' : 'custom';
}

export function buildShareUrl({ presets, theme } = {}) {
  // presets: optional registry of named presets to detect non-balanced matches
  // theme:   optional explicit theme to embed (defaults to current document theme)
  const params = new URLSearchParams();

  if (State.lang) params.set('lang', State.lang);

  let presetName = presetOf(State.weights);
  if (presetName === 'custom' && presets && typeof presets === 'object') {
    for (const [name, w] of Object.entries(presets)) {
      let match = true;
      for (const k of BENCH_KEYS) {
        if ((State.weights[k] || 0) !== (w[k] || 0)) { match = false; break; }
      }
      if (match) { presetName = name; break; }
    }
  }
  params.set('preset', presetName);
  if (presetName === 'custom') {
    const wStr = serializeWeights(State.weights);
    if (wStr) params.set('w', wStr);
  }

  const f = State.filters || {};
  if (f.tier && f.tier !== 'all') params.set('tier', f.tier);
  if (f.deployment && f.deployment !== 'all') params.set('deployment', f.deployment);
  if (f.provider && f.provider !== 'all') params.set('provider', f.provider);
  if (f.openOnly) params.set('open', '1');
  if (f.search) params.set('search', f.search);

  if (Number.isFinite(State.vram)) params.set('vram', String(State.vram));
  if (State.selectedGpu && State.selectedGpu !== 'auto') params.set('gpu', State.selectedGpu);

  const s = State.sort || {};
  if (s.col && s.dir && !(s.col === 'composite' && s.dir === 'desc')) {
    params.set('sort', `${s.col}-${s.dir}`);
  }

  const themeOut = theme || document.documentElement.getAttribute('data-theme') || 'dark';
  if (themeOut && themeOut !== 'dark') params.set('theme', themeOut);

  const base = window.location.origin + window.location.pathname;
  const qs = params.toString();
  return qs ? `${base}?${qs}` : base;
}

let pushTimer = null;
export function pushUrlState({ presets, theme, immediate } = {}) {
  // Debounced replaceState. Avoids URL-bar churn during slider drag while
  // still committing the final state quickly enough that copy-share works.
  const run = () => {
    pushTimer = null;
    try {
      const url = buildShareUrl({ presets, theme });
      const next = url.replace(window.location.origin, '');
      if (next !== window.location.pathname + window.location.search) {
        window.history.replaceState(null, '', next);
      }
    } catch (_) { /* SecurityError on file:// — silent */ }
  };
  if (immediate) {
    if (pushTimer) { clearTimeout(pushTimer); pushTimer = null; }
    run();
    return;
  }
  if (pushTimer) clearTimeout(pushTimer);
  pushTimer = setTimeout(run, 250);
}
