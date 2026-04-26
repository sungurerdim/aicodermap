/* AICoderMap — vanilla, no build step.
   Strict no-innerHTML policy: textContent + createElement only. */
'use strict';

const STORAGE = {
  weights: 'acm.v1.weights',
  language: 'acm.v1.language',
  vram: 'acm.v1.vram',
  gpu: 'acm.v1.gpu',
  filters: 'acm.v1.filters',
  sort: 'acm.v1.sort',
  theme: 'acm.v1.theme'
};

const BENCH_KEYS = [
  'aaIdx',
  'swePro', 'sweV', 'sweMulti',
  'lcbV6', 'tb2',
  'tau2', 'mcpA', 'aaCoding', 'aaAgentic',
  'gpqa', 'hle', 'aider'
];

const DEFAULT_WEIGHTS = {
  swePro: 22, tb2: 15, lcbV6: 15, sweV: 10, aider: 10,
  aaCoding: 7, aaAgentic: 5, tau2: 5, mcpA: 5,
  gpqa: 2, sweMulti: 2, hle: 2
};

const PRESETS = {
  'balanced': { ...DEFAULT_WEIGHTS },
  'swe-focused': {
    swePro: 30, sweV: 20, sweMulti: 15, tb2: 10, lcbV6: 10, aider: 10,
    aaCoding: 5, aaAgentic: 0, tau2: 0, mcpA: 0, gpqa: 0, hle: 0
  },
  'agentic-focused': {
    tb2: 25, mcpA: 20, tau2: 15, aaAgentic: 15, swePro: 10, lcbV6: 10,
    gpqa: 5, sweV: 0, aider: 0, aaCoding: 0, sweMulti: 0, hle: 0
  },
  'benchmark-only': {
    swePro: 20, sweV: 15, tb2: 15, lcbV6: 15, aider: 10, gpqa: 10,
    sweMulti: 10, hle: 5, aaCoding: 0, aaAgentic: 0, tau2: 0, mcpA: 0
  }
};

const CONTRADICTION_WARN = 3.0;
const CONTRADICTION_BLOCK = 5.0;

const TIER_ORDER = { 'frontier': 0, 'open-tier1': 1, 'openrouter': 2, 'gemma': 3, 'ollama': 4 };

const State = {
  models: [],
  sources: {},
  gpu: { nvidia: {}, apple: {}, amd: {}, intel: {}, webgpuVendorMap: {} },
  i18n: null,
  i18nFallback: null,
  lang: 'tr',
  weights: { ...DEFAULT_WEIGHTS },
  filters: { deployment: 'all', openOnly: false, tier: 'all', search: '' },
  sort: { col: 'composite', dir: 'desc' },
  vram: null,
  selectedGpu: 'auto',
  detectedGpu: null
};

function scoreClass(v) {
  if (v == null || !Number.isFinite(v)) return 'score-na';
  if (v >= 70) return 'score-high';
  if (v >= 50) return 'score-mid';
  return 'score-low';
}

/* ---------- storage helpers ---------- */

function readStorage(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    if (raw == null) return fallback;
    return JSON.parse(raw);
  } catch (e) {
    return fallback;
  }
}

function writeStorage(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (e) {
    /* quota or disabled — silent */
  }
}

/* ---------- schema validation ---------- */

function isValidModel(m) {
  if (!m || typeof m !== 'object') return false;
  if (typeof m.id !== 'string' || !m.id) return false;
  if (typeof m.name !== 'string') return false;
  if (typeof m.tier !== 'string') return false;
  if (!m.bench || typeof m.bench !== 'object') return false;
  return true;
}

function validateModels(arr) {
  if (!Array.isArray(arr)) return [];
  return arr.filter(isValidModel);
}

function validateWeights(w) {
  if (!w || typeof w !== 'object') return null;
  const out = {};
  for (const k of BENCH_KEYS) {
    const v = Number(w[k]);
    if (!Number.isFinite(v) || v < 0 || v > 100) return null;
    out[k] = v;
  }
  return out;
}

/* ---------- i18n ---------- */

function t(path) {
  const parts = path.split('.');
  let cur = State.i18n;
  for (const p of parts) {
    if (cur && typeof cur === 'object' && p in cur) cur = cur[p];
    else { cur = null; break; }
  }
  if (cur != null) return cur;
  if (State.i18nFallback) {
    let fb = State.i18nFallback;
    for (const p of parts) {
      if (fb && typeof fb === 'object' && p in fb) fb = fb[p];
      else { fb = null; break; }
    }
    if (fb != null) return fb;
  }
  return path;
}

function applyI18n(root) {
  const scope = root || document;
  document.documentElement.setAttribute('lang', State.lang);
  scope.querySelectorAll('[data-i18n-key]').forEach((el) => {
    const key = el.getAttribute('data-i18n-key');
    const val = t(key);
    if (typeof val === 'string') el.textContent = val;
  });
  scope.querySelectorAll('[data-i18n-tip]').forEach((el) => {
    const key = el.getAttribute('data-i18n-tip');
    const val = t(key);
    if (typeof val === 'string') el.setAttribute('data-tip', val);
  });
  scope.querySelectorAll('[data-i18n-aria-label]').forEach((el) => {
    const key = el.getAttribute('data-i18n-aria-label');
    const val = t(key);
    if (typeof val === 'string') el.setAttribute('aria-label', val);
  });
  scope.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
    const key = el.getAttribute('data-i18n-placeholder');
    const val = t(key);
    if (typeof val === 'string') el.setAttribute('placeholder', val);
  });
}

async function loadI18n(lang) {
  try {
    const res = await fetch(`./i18n/${lang}.json`, { cache: 'no-cache' });
    if (!res.ok) throw new Error('i18n fetch failed');
    return await res.json();
  } catch (e) {
    return null;
  }
}

/* ---------- data load ---------- */

async function fetchJson(path) {
  const res = await fetch(path, { cache: 'no-cache' });
  if (!res.ok) throw new Error(`${path} ${res.status}`);
  return res.json();
}

async function loadData() {
  const [models, sources, gpu] = await Promise.all([
    fetchJson('./data/models.json'),
    fetchJson('./data/sources.json'),
    fetchJson('./data/gpu-database.json')
  ]);
  State.models = validateModels(models);
  State.sources = (sources && typeof sources === 'object') ? sources : {};
  if (gpu && typeof gpu === 'object') State.gpu = { ...State.gpu, ...gpu };
}

/* ---------- composite score ---------- */

function compositeScore(model, weights) {
  let totalW = 0;
  let weightedSum = 0;
  for (const k of BENCH_KEYS) {
    const score = model.bench?.[k];
    const w = weights[k];
    if (score == null || !Number.isFinite(score) || !w) continue;
    totalW += w;
    weightedSum += w * score;
  }
  if (totalW === 0) return null;
  return weightedSum / totalW;
}

function fmtScore(v, digits = 1) {
  if (v == null || !Number.isFinite(v)) return '—';
  return v.toFixed(digits);
}

/* ---------- contradiction detection ---------- */

function contradictionFor(modelId, benchKey) {
  const key = `${modelId}.${benchKey}`;
  const list = State.sources[key];
  if (!Array.isArray(list) || list.length < 2) return null;
  const values = list.map(s => Number(s.value)).filter(Number.isFinite);
  if (values.length < 2) return null;
  const max = Math.max(...values);
  const min = Math.min(...values);
  const delta = max - min;
  let severity = null;
  if (delta >= CONTRADICTION_BLOCK) severity = 'danger';
  else if (delta >= CONTRADICTION_WARN) severity = 'warn';
  if (!severity) return null;
  return { delta, severity, sources: list };
}

/* ---------- GPU compatibility ---------- */

function gpuCompat(model, vram) {
  const hasUnsloth = Array.isArray(model.unslothVariants) && model.unslothVariants.length > 0;
  const hasVramReq = Number.isFinite(model.vramRequirement);

  if (model.tier !== 'ollama' && !hasVramReq && !hasUnsloth) {
    return { kind: 'cloud', label: t('ui.compat.cloud') };
  }
  if (vram == null) {
    return { kind: 'unknown', label: '—' };
  }

  // RAM offload tolerance: model can use up to 2× user VRAM via system RAM
  const OFFLOAD_LIMIT = Math.max(vram * 2, 8);

  // Best Unsloth variant fitting current VRAM (largest that still fits in VRAM)
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

  // Try base vramRequirement
  if (hasVramReq) {
    const needed = model.vramRequirement;
    if (needed <= vram - 1) {
      return { kind: 'fits', label: `${t('ui.compat.fits')} (${needed} GB)`, variant: null };
    }
    if (needed <= vram) {
      return { kind: 'offload', label: `${t('ui.compat.offload')} (${needed} GB)`, variant: null };
    }
    const offload = needed - vram;
    if (offload <= OFFLOAD_LIMIT) {
      return {
        kind: 'offload',
        label: `${t('ui.compat.offload')} (${needed} GB · +${offload} GB RAM)`,
        variant: null
      };
    }
  }

  // Smallest Unsloth variant with RAM offload
  if (hasUnsloth) {
    const smallest = [...model.unslothVariants].sort((a, b) => a.vram - b.vram)[0];
    const offload = smallest.vram - vram;
    if (offload <= OFFLOAD_LIMIT) {
      return {
        kind: 'offload',
        label: `${t('ui.compat.offload')} (${smallest.vram} GB · ${smallest.name} · +${offload} GB RAM)`,
        variant: smallest
      };
    }
    return {
      kind: 'too-large',
      label: `${t('ui.compat.tooLarge')} (min ${smallest.vram} GB · ${smallest.name})`,
      variant: null
    };
  }
  if (hasVramReq) {
    return {
      kind: 'too-large',
      label: `${t('ui.compat.tooLarge')} (${model.vramRequirement} GB)`,
      variant: null
    };
  }
  return { kind: 'unknown', label: '—' };
}

/* ---------- DOM helpers ---------- */

function el(tag, attrs, ...children) {
  const node = document.createElement(tag);
  if (attrs) {
    for (const [k, v] of Object.entries(attrs)) {
      if (v == null || v === false) continue;
      if (k === 'class') node.className = v;
      else if (k === 'dataset') Object.assign(node.dataset, v);
      else if (k.startsWith('on') && typeof v === 'function') node.addEventListener(k.slice(2).toLowerCase(), v);
      else if (k === 'i18nKey') node.setAttribute('data-i18n-key', v);
      else node.setAttribute(k, v === true ? '' : String(v));
    }
  }
  for (const c of children) {
    if (c == null || c === false) continue;
    if (Array.isArray(c)) c.forEach(x => x != null && node.appendChild(typeof x === 'string' ? document.createTextNode(x) : x));
    else node.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
  }
  return node;
}

function clear(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
}

function cameraIconButton(titleText) {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'btn-icon-only';
  btn.setAttribute('data-tip', titleText);
  btn.setAttribute('aria-label', titleText);

  const svgNS = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(svgNS, 'svg');
  svg.setAttribute('class', 'icon');
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('width', '16');
  svg.setAttribute('height', '16');
  svg.setAttribute('fill', 'none');
  svg.setAttribute('stroke', 'currentColor');
  svg.setAttribute('stroke-width', '2');
  svg.setAttribute('stroke-linecap', 'round');
  svg.setAttribute('stroke-linejoin', 'round');
  svg.setAttribute('aria-hidden', 'true');
  svg.setAttribute('focusable', 'false');

  const path = document.createElementNS(svgNS, 'path');
  path.setAttribute('d', 'M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z');
  svg.appendChild(path);

  const circle = document.createElementNS(svgNS, 'circle');
  circle.setAttribute('cx', '12');
  circle.setAttribute('cy', '13');
  circle.setAttribute('r', '4');
  svg.appendChild(circle);

  btn.appendChild(svg);

  const sr = document.createElement('span');
  sr.className = 'sr-only';
  sr.textContent = titleText;
  btn.appendChild(sr);

  return btn;
}

/* ---------- weights editor ---------- */

function renderWeightsEditor() {
  const grid = document.getElementById('weights-grid');
  if (!grid) return;
  clear(grid);
  for (const k of BENCH_KEYS) {
    const row = el('div', { class: 'weight-row' });
    const benchName = t(`benchmarks.${k}.name`);
    const label = el('span', { class: 'label' }, benchName);
    row.appendChild(label);

    const controls = el('div', { class: 'controls' });
    const range = el('input', {
      type: 'range', min: '0', max: '100', step: '1',
      'aria-label': benchName
    });
    const num = el('input', {
      type: 'number', min: '0', max: '100', step: '1',
      inputmode: 'numeric',
      'aria-label': `${benchName} (numeric)`
    });
    const startVal = String(State.weights[k] ?? 0);
    range.value = startVal;
    num.value = startVal;
    range.style.setProperty('--val', startVal);

    range.addEventListener('input', () => {
      num.value = range.value;
      range.style.setProperty('--val', range.value);
      onWeightChange(k, range);
    });
    num.addEventListener('input', () => {
      range.value = num.value;
      range.style.setProperty('--val', range.value);
      onWeightChange(k, num);
    });

    controls.appendChild(range);
    controls.appendChild(num);
    row.appendChild(controls);
    grid.appendChild(row);
  }
  updateWeightsTotal();
}

function onWeightChange(key, input) {
  let v = Number(input.value);
  if (!Number.isFinite(v)) v = 0;
  v = Math.max(0, Math.min(100, Math.round(v)));
  input.value = String(v);
  State.weights[key] = v;
  syncPresetSelect();
  writeStorage(STORAGE.weights, State.weights);
  updateWeightsTotal();
  renderAll();
}

function updateWeightsTotal() {
  const total = BENCH_KEYS.reduce((a, k) => a + (State.weights[k] || 0), 0);
  const totalEl = document.getElementById('weights-total');
  totalEl.textContent = String(total);
  totalEl.classList.toggle('invalid', total !== 100);
  totalEl.title = total !== 100 ? t('ui.weights.totalWarn') : '';
}

function applyPreset(name) {
  const preset = PRESETS[name];
  if (!preset) return;
  State.weights = { ...DEFAULT_WEIGHTS, ...preset };
  for (const k of BENCH_KEYS) if (State.weights[k] == null) State.weights[k] = 0;
  writeStorage(STORAGE.weights, State.weights);
  renderWeightsEditor();
  renderAll();
}

function detectMatchingPreset(weights) {
  for (const [name, preset] of Object.entries(PRESETS)) {
    if (BENCH_KEYS.every(k => (weights[k] || 0) === (preset[k] || 0))) return name;
  }
  return 'custom';
}

function syncPresetSelect() {
  const sel = document.getElementById('weights-preset');
  if (!sel) return;
  sel.value = detectMatchingPreset(State.weights);
}

function resetWeights() {
  State.weights = { ...DEFAULT_WEIGHTS };
  writeStorage(STORAGE.weights, State.weights);
  document.getElementById('weights-preset').value = 'balanced';
  renderWeightsEditor();
  renderAll();
}

/* ---------- filters ---------- */

function isLocalRunnable(m) {
  if (m.tier === 'ollama' || m.tier === 'gemma') return true;
  if (Number.isFinite(m.vramRequirement)) return true;
  if (Array.isArray(m.unslothVariants) && m.unslothVariants.length > 0) return true;
  return false;
}

function getActiveVram() {
  if (State.filters.deployment === 'local') {
    if (Number.isFinite(State.vram) && State.vram > 0) return State.vram;
  }
  return null;
}

function passesFilters(model) {
  const f = State.filters;
  if (f.openOnly && !model.open) return false;
  if (f.tier !== 'all' && model.tier !== f.tier) return false;

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

/* ---------- model card render ---------- */

function tierLabel(tier) {
  return t(`ui.tier.${tier}`) || tier;
}

/**
 * Read pricing in schema v2 (multi-provider array). Returns a normalized view
 * with computed ranges, per-provider list, and subscription tiers. Backward-
 * compatible with legacy flat schema (single `{in, out, cacheHit}` object).
 */
function pricingView(model) {
  const p = model.pricing || {};
  let api = p.api;
  // Legacy bridge: wrap flat object as single-element array.
  if (api && !Array.isArray(api) && typeof api === 'object') {
    api = [{ provider: 'official', in: api.in ?? null, out: api.out ?? null,
             cacheHit: api.cacheHit ?? null, throughput: null, url: null,
             fetched: model.lastUpdated }];
  }
  api = Array.isArray(api) ? api : [];
  const ins = api.map(e => e?.in).filter(v => v != null);
  const outs = api.map(e => e?.out).filter(v => v != null);
  const chs = api.map(e => e?.cacheHit).filter(v => v != null);
  const range = p.range || {
    in: ins.length ? [Math.min(...ins), Math.max(...ins)] : null,
    out: outs.length ? [Math.min(...outs), Math.max(...outs)] : null,
    cacheHit: chs.length ? [Math.min(...chs), Math.max(...chs)] : null,
  };
  let subs = p.subscription;
  if (typeof subs === 'string' && subs) subs = [{ tier: subs, price: null, billing: 'monthly', notes: subs }];
  if (!Array.isArray(subs)) subs = [];
  return { providers: api, range, subscriptions: subs };
}

function fmtPriceMoney(v) {
  if (v == null) return '—';
  return `$${Number(v).toString()}`;
}

function fmtPriceRange(pair) {
  if (!pair) return '—';
  const [a, b] = pair;
  if (a == null && b == null) return '—';
  if (a === b || b == null) return fmtPriceMoney(a);
  return `${fmtPriceMoney(a)}–${fmtPriceMoney(b)}`;
}

function fmtPriceCell(model) {
  const v = pricingView(model);
  const inS = fmtPriceRange(v.range?.in);
  const outS = fmtPriceRange(v.range?.out);
  if (inS === '—' && outS === '—') return '—';
  return `${inS} / ${outS}`;
}

function fmtContext(n) {
  if (!Number.isFinite(n)) return '—';
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(n % 1_000_000 === 0 ? 0 : 1)}M`;
  if (n >= 1000) return `${Math.round(n / 1000)}K`;
  return String(n);
}

function buildBenchCell(model, key) {
  const score = model.bench?.[key];
  const cellClasses = ['bench-cell'];
  if (score == null) cellClasses.push('empty');
  const cell = el('div', { class: cellClasses.join(' ') });
  cell.appendChild(el('span', { class: 'name' }, t(`benchmarks.${key}.name`)));
  const valueText = score != null ? fmtScore(score) : '—';
  const valueSpan = el('span', { class: 'value' }, valueText);
  cell.appendChild(valueSpan);

  const contradiction = contradictionFor(model.id, key);
  if (contradiction) {
    cell.classList.add(contradiction.severity === 'danger' ? 'flag-danger' : 'flag-warn');
    const flag = el('span', {
      class: 'flag',
      tabindex: '0',
      role: 'button',
      'aria-label': t('ui.contradiction.title')
    }, contradiction.severity === 'danger' ? '🚨' : '⚠');
    flag.dataset.modelId = model.id;
    flag.dataset.benchKey = key;
    flag.addEventListener('mouseenter', (e) => showContradictionTooltip(e.currentTarget, contradiction));
    flag.addEventListener('focus', (e) => showContradictionTooltip(e.currentTarget, contradiction));
    flag.addEventListener('mouseleave', hideTooltip);
    flag.addEventListener('blur', hideTooltip);
    cell.appendChild(flag);
  }
  return cell;
}

function buildModelCard(model, rank) {
  const composite = compositeScore(model, State.weights);
  const status = model.status || 'active';
  const statusClass = status === 'active' ? '' : ` is-${status}`;
  const card = el('article', {
    class: `model-card${statusClass}`,
    dataset: { modelId: model.id, tier: model.tier, status },
    'data-export-section': `model-${model.id}`,
    'aria-label': model.name
  });

  // Head: rank + name + tier + composite + actions
  const head = el('div', { class: 'model-card-head' });
  const nameWrap = el('div', { class: 'model-name' },
    el('span', { class: 'model-rank' }, `#${rank}`),
    el('h3', null, model.name),
    el('span', { class: `tier-badge ${model.tier}` }, tierLabel(model.tier))
  );
  head.appendChild(nameWrap);

  const composite2 = el('div', { class: 'composite-score' },
    el('span', { class: 'label' }, t('ui.table.composite')),
    el('span', { class: 'value' }, fmtScore(composite, 1))
  );
  head.appendChild(composite2);
  card.appendChild(head);

  // Provider + license + open badge row
  const providerRow = el('div', { class: 'model-provider' });
  providerRow.appendChild(el('span', null, `${model.provider || '—'} · ${model.released || '—'} · ${model.license || '—'}`));
  if (model.open === true) {
    providerRow.appendChild(el('span', { class: 'open-badge', title: t('ui.openWeights') || 'Open weights' },
      t('ui.openShort') || 'OPEN'));
  } else if (model.open === false) {
    providerRow.appendChild(el('span', { class: 'closed-badge', title: t('ui.closedWeights') || 'Closed weights' },
      t('ui.closedShort') || 'CLOSED'));
  }
  if (model.status === 'deprecated') {
    const tip = model.successor ? `Successor: ${model.successor}` : 'Deprecated by vendor';
    const dateTxt = model.deprecatedAt ? ` ${model.deprecatedAt}` : '';
    providerRow.appendChild(el('span', { class: 'deprecated-badge', title: tip },
      `${t('ui.deprecated') || 'DEPRECATED'}${dateTxt}`));
  } else if (model.status === 'archived') {
    providerRow.appendChild(el('span', { class: 'archived-badge', title: 'Archived' },
      t('ui.archived') || 'ARCHIVED'));
  }
  card.appendChild(providerRow);

  // Meta grid
  const meta = el('div', { class: 'model-meta' });
  const pview = pricingView(model);
  meta.appendChild(metaCell(t('ui.table.context'), fmtContext(model.context)));
  meta.appendChild(metaCell(t('ui.table.pricingApi'), fmtPriceCell(model)));
  if (pview.range?.cacheHit) {
    meta.appendChild(metaCell(t('ui.table.cacheHit') || 'Cache hit', fmtPriceRange(pview.range.cacheHit)));
  }
  const subText = pview.subscriptions.length
    ? pview.subscriptions.map(s => s.price != null ? `${s.tier} $${s.price}/${s.billing === 'annual' ? 'yr' : 'mo'}` : (s.notes || s.tier)).join(' · ')
    : '—';
  meta.appendChild(metaCell(t('ui.table.pricingSub'), subText));
  meta.appendChild(metaCell(t('ui.table.lastUpdated'), model.lastUpdated || '—'));
  if (model.providers != null) meta.appendChild(metaCell(t('ui.table.providers') || 'Providers', `${model.providers}${model.uptime != null ? ` (uptime ${fmtScore(model.uptime, 1)}%)` : ''}`));
  if (model.vramRequirement != null) meta.appendChild(metaCell(t('ui.table.vram'), `${model.vramRequirement} GB`));
  // Legacy ollamaSize fallback — only if no rich ollama object
  if (model.ollamaSize && !model.ollama) {
    meta.appendChild(metaCell(t('ui.table.ollamaSize') || 'Ollama size', model.ollamaSize));
  }

  // GPU compat
  const compat = gpuCompat(model, getActiveVram());
  const compatWrap = el('span', { class: `compat-badge ${compat.kind}` }, compat.label);
  meta.appendChild(metaCell(t('ui.table.gpu'), compatWrap));

  card.appendChild(meta);

  // Multi-provider pricing breakdown (only when ≥2 providers)
  if (pview.providers.length >= 2) {
    const provBlock = el('details', { class: 'pricing-providers' });
    provBlock.appendChild(el('summary', null, t('ui.pricing.byProvider') || 'Pricing by provider'));
    const list = el('div', { class: 'pricing-providers-list' });
    for (const e of pview.providers) {
      const row = el('div', { class: 'pricing-provider-row' });
      row.appendChild(el('span', { class: 'prov-name' }, e.provider || '—'));
      const priceTxt = `${fmtPriceMoney(e.in)} / ${fmtPriceMoney(e.out)}${e.cacheHit != null ? ` · cache ${fmtPriceMoney(e.cacheHit)}` : ''}${e.throughput != null ? ` · ${e.throughput} tok/s` : ''}`;
      row.appendChild(el('span', { class: 'prov-price' }, priceTxt));
      if (e.url) {
        const link = document.createElement('a');
        link.href = e.url;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.className = 'prov-link';
        link.textContent = '↗';
        link.title = e.url;
        row.appendChild(link);
      }
      list.appendChild(row);
    }
    provBlock.appendChild(list);
    card.appendChild(provBlock);
  }

  // Bench grid
  const benchHead = el('div', { class: 'meta-cell' },
    el('span', { class: 'label' }, t('ui.table.bench'))
  );
  card.appendChild(benchHead);
  const benchGrid = el('div', { class: 'bench-grid' });
  for (const k of BENCH_KEYS) benchGrid.appendChild(buildBenchCell(model, k));
  card.appendChild(benchGrid);

  // Unsloth variants
  if (Array.isArray(model.unslothVariants) && model.unslothVariants.length) {
    const list = el('ul', { class: 'unsloth-list' });
    for (const v of model.unslothVariants) {
      const li = el('li', null, `${v.name} · ${v.size} · ~${v.vram} GB`);
      if (compat.variant && compat.variant.name === v.name) {
        li.classList.add('recommended');
      }
      list.appendChild(li);
    }
    card.appendChild(list);
  }

  // Local Ollama metadata (rich object: pullCmd, tags, pullCount, architecture, parameters, license, releasedISO, ollamaUrl)
  if (model.ollama && typeof model.ollama === 'object') {
    const o = model.ollama;
    const block = el('div', { class: 'ollama-block' });

    const titleParts = [t('ui.ollama.title') || 'Local (Ollama)'];
    if (o.architecture) titleParts.push(o.architecture);
    if (o.parameters) titleParts.push(o.parameters);
    const title = el('div', { class: 'ollama-title' });
    title.appendChild(el('span', { class: 'ollama-icon' }, '💻'));
    title.appendChild(el('span', { class: 'ollama-title-text' }, titleParts.join(' · ')));
    block.appendChild(title);

    if (o.pullCmd) {
      const cmdRow = el('div', { class: 'ollama-cmd-row' });
      cmdRow.appendChild(el('code', { class: 'pull-cmd' }, o.pullCmd));
      const copyLabel = t('ui.ollama.copy') || 'Copy';
      const copy = el('button', { class: 'copy-btn', type: 'button', 'aria-label': copyLabel }, '⧉');
      copy.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(o.pullCmd);
          copy.textContent = '✓';
          setTimeout(() => copy.textContent = '⧉', 1500);
        } catch (_) { /* clipboard unavailable */ }
      });
      cmdRow.appendChild(copy);
      block.appendChild(cmdRow);
    }

    const meta = [];
    if (o.pullCount) meta.push(o.pullCount);
    if (o.license) meta.push(o.license);
    if (o.releasedISO) meta.push(o.releasedISO);
    if (meta.length) block.appendChild(el('div', { class: 'ollama-meta' }, meta.join(' · ')));

    if (o.ollamaUrl) {
      block.appendChild(el('a', {
        class: 'ollama-link',
        href: o.ollamaUrl,
        target: '_blank',
        rel: 'noopener noreferrer'
      }, (t('ui.ollama.viewOn') || 'View on Ollama') + ' →'));
    }

    card.appendChild(block);
  }

  // Notes
  const strengths = t(`models.${model.strengthsKey}`);
  const weaknesses = t(`models.${model.weaknessesKey}`);
  if ((strengths && strengths !== `models.${model.strengthsKey}`) || (weaknesses && weaknesses !== `models.${model.weaknessesKey}`)) {
    const notes = el('div', { class: 'notes' });
    if (strengths && strengths !== `models.${model.strengthsKey}`) {
      notes.appendChild(el('div', { class: 'strengths' }, strengths));
    }
    if (weaknesses && weaknesses !== `models.${model.weaknessesKey}`) {
      notes.appendChild(el('div', { class: 'weaknesses' }, weaknesses));
    }
    card.appendChild(notes);
  }

  // Per-card export (icon-only, native tooltip)
  const actions = el('div', { class: 'model-actions' });
  const exportBtn = cameraIconButton(t('ui.export.model'));
  exportBtn.addEventListener('click', () => exportElement(card, `aicodermap-${model.id}`));
  actions.appendChild(exportBtn);
  card.appendChild(actions);

  return card;
}

function metaCell(label, value) {
  const cell = el('div', { class: 'meta-cell' });
  cell.appendChild(el('span', { class: 'label' }, String(label)));
  if (value && typeof value === 'object' && value.nodeType === 1) {
    const v = el('span', { class: 'value' });
    v.appendChild(value);
    cell.appendChild(v);
  } else {
    cell.appendChild(el('span', { class: 'value' }, String(value ?? '—')));
  }
  return cell;
}

/* ---------- comparison table ---------- */

function buildTableColumns() {
  const cols = [
    { key: 'rank', i18n: 'ui.table.rank', sortable: false, num: true,
      get: (m, ctx) => ctx.index + 1,
      render: (m, ctx) => String(ctx.index + 1), cls: 'col-rank' },
    { key: 'name', i18n: 'ui.table.name', sortable: true, sticky: true,
      get: (m) => m.name.toLowerCase(),
      render: (m) => m.name },
    { key: 'provider', i18n: 'ui.table.provider', sortable: true,
      get: (m) => (m.provider || '').toLowerCase(),
      render: (m) => m.provider || '—' },
    { key: 'tier', i18n: 'ui.table.tier', sortable: true,
      get: (m) => TIER_ORDER[m.tier] ?? 99,
      render: (m) => {
        const span = document.createElement('span');
        span.className = `tier-badge ${m.tier}`;
        span.textContent = tierLabel(m.tier);
        return span;
      } },
    { key: 'composite', i18n: 'ui.table.composite', sortable: true, num: true,
      get: (m, ctx) => ctx.score,
      render: (m, ctx) => {
        const span = document.createElement('span');
        span.className = scoreClass(ctx.score);
        span.textContent = fmtScore(ctx.score);
        return span;
      } },
    ...BENCH_KEYS.map(k => ({
      key: `bench.${k}`,
      benchKey: k,
      i18n: `benchmarks.${k}.short`,
      sortable: true,
      num: true,
      cls: 'bench-cell-td',
      get: (m) => m.bench?.[k],
      render: (m) => {
        const v = m.bench?.[k];
        const wrap = document.createDocumentFragment();
        const span = document.createElement('span');
        span.className = scoreClass(v);
        span.textContent = fmtScore(v);
        wrap.appendChild(span);
        const c = contradictionFor(m.id, k);
        if (c) {
          const flag = document.createElement('span');
          flag.className = 'flag';
          flag.textContent = c.severity === 'danger' ? '🚨' : '⚠';
          flag.tabIndex = 0;
          flag.setAttribute('role', 'button');
          flag.setAttribute('aria-label', t('ui.contradiction.title'));
          flag.addEventListener('mouseenter', (e) => showContradictionTooltip(e.currentTarget, c));
          flag.addEventListener('focus', (e) => showContradictionTooltip(e.currentTarget, c));
          flag.addEventListener('mouseleave', hideTooltip);
          flag.addEventListener('blur', hideTooltip);
          wrap.appendChild(flag);
        }
        return wrap;
      }
    })),
    { key: 'context', i18n: 'ui.table.context', sortable: true, num: true,
      get: (m) => m.context,
      render: (m) => fmtContext(m.context) },
    { key: 'priceIn', i18n: 'ui.table.priceIn', sortable: true, num: true,
      get: (m) => pricingView(m).range?.in?.[0] ?? null,
      render: (m) => fmtPriceRange(pricingView(m).range?.in) },
    { key: 'priceOut', i18n: 'ui.table.priceOut', sortable: true, num: true,
      get: (m) => pricingView(m).range?.out?.[0] ?? null,
      render: (m) => fmtPriceRange(pricingView(m).range?.out) },
    { key: 'vram', i18n: 'ui.table.vram', sortable: true, num: true,
      get: (m) => m.vramRequirement,
      render: (m) => m.vramRequirement != null ? `${m.vramRequirement} GB` : '—' },
    { key: 'gpuFit', i18n: 'ui.table.gpu', sortable: false,
      get: () => 0,
      render: (m) => {
        const c = gpuCompat(m, getActiveVram());
        const span = document.createElement('span');
        span.className = `compat-badge ${c.kind}`;
        span.textContent = c.label;
        return span;
      } },
    { key: 'lastUpdated', i18n: 'ui.table.lastUpdated', sortable: true,
      get: (m) => m.lastUpdated || '',
      render: (m) => m.lastUpdated || '—' }
  ];
  return cols;
}

function compareValues(a, b, dir) {
  const aNull = a == null || a === '' || (typeof a === 'number' && !Number.isFinite(a));
  const bNull = b == null || b === '' || (typeof b === 'number' && !Number.isFinite(b));
  if (aNull && bNull) return 0;
  if (aNull) return 1;
  if (bNull) return -1;
  let cmp;
  if (typeof a === 'number' && typeof b === 'number') cmp = a - b;
  else cmp = String(a).localeCompare(String(b));
  return dir === 'asc' ? cmp : -cmp;
}

function onSortClick(colKey) {
  if (State.sort.col === colKey) {
    State.sort.dir = State.sort.dir === 'asc' ? 'desc' : 'asc';
  } else {
    State.sort.col = colKey;
    State.sort.dir = 'desc';
  }
  writeStorage(STORAGE.sort, State.sort);
  renderTable();
}

function renderTable() {
  const table = document.getElementById('comparison-table');
  if (!table) return;
  const thead = table.querySelector('thead tr');
  const tbody = table.querySelector('tbody');

  const cols = buildTableColumns();

  // Header
  clear(thead);
  for (const col of cols) {
    const th = document.createElement('th');
    th.dataset.col = col.key;
    if (col.num) th.classList.add('num');
    if (col.sticky) th.classList.add('col-name');
    if (col.sortable) {
      th.dataset.sortable = 'true';
      th.addEventListener('click', () => onSortClick(col.key));
      th.tabIndex = 0;
      th.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSortClick(col.key); }
      });
    }
    if (State.sort.col === col.key) {
      th.classList.add('sorted', State.sort.dir);
    }
    th.textContent = t(col.i18n);
    thead.appendChild(th);
  }

  // Rows
  clear(tbody);
  const ranked = State.models
    .filter(passesFilters)
    .map(m => ({ model: m, score: compositeScore(m, State.weights) }));

  const sortCol = cols.find(c => c.key === State.sort.col);
  if (sortCol && sortCol.sortable !== false) {
    ranked.sort((A, B) => {
      const va = sortCol.get(A.model, { score: A.score });
      const vb = sortCol.get(B.model, { score: B.score });
      return compareValues(va, vb, State.sort.dir);
    });
  } else {
    // Default fallback
    ranked.sort((A, B) => compareValues(A.score, B.score, 'desc'));
  }

  ranked.forEach((entry, index) => {
    const tr = document.createElement('tr');
    tr.dataset.modelId = entry.model.id;
    const ctx = { index, score: entry.score };
    for (const col of cols) {
      const td = document.createElement('td');
      if (col.num) td.classList.add('num');
      if (col.sticky) td.classList.add('col-name');
      if (col.cls) td.classList.add(col.cls);
      const out = col.render(entry.model, ctx);
      if (out instanceof Node) td.appendChild(out);
      else td.textContent = String(out ?? '—');
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  });

  const count = document.getElementById('table-count');
  if (count) count.textContent = `${ranked.length} / ${State.models.length}`;
}

function renderAll() {
  renderTable();
  renderModelCards();
}

/* ---------- main render ---------- */

function renderModelCards() {
  const list = document.getElementById('models-list');
  if (!list) return;
  clear(list);

  const ranked = State.models
    .filter(passesFilters)
    .map(m => ({ model: m, score: compositeScore(m, State.weights) }))
    .sort((a, b) => {
      const sa = a.score == null ? -1 : a.score;
      const sb = b.score == null ? -1 : b.score;
      if (sa !== sb) return sb - sa;
      const ta = TIER_ORDER[a.model.tier] ?? 99;
      const tb = TIER_ORDER[b.model.tier] ?? 99;
      if (ta !== tb) return ta - tb;
      return a.model.name.localeCompare(b.model.name);
    });

  if (ranked.length === 0) {
    list.appendChild(el('p', { class: 'loading' }, t('ui.noData')));
  } else {
    ranked.forEach((entry, i) => {
      list.appendChild(buildModelCard(entry.model, i + 1));
    });
  }

  const count = document.getElementById('models-count');
  if (count) count.textContent = `${ranked.length} / ${State.models.length}`;
}

/* ---------- tooltip ---------- */

function showContradictionTooltip(anchor, contradiction) {
  const tt = document.getElementById('tooltip');
  if (!tt) return;
  clear(tt);
  tt.appendChild(el('h4', null, t('ui.contradiction.title')));
  tt.appendChild(el('p', null, `${t('ui.contradiction.delta')}: ${contradiction.delta.toFixed(1)} pp`));
  const dl = el('dl');
  for (const s of contradiction.sources) {
    const dt = el('dt', null, `${fmtScore(s.value, 1)}`);
    const dd = el('dd');
    const tierLabel2 = t(`ui.contradiction.tier.${s.tier}`) || s.tier;
    if (s.url) {
      const a = el('a', { href: s.url, target: '_blank', rel: 'noopener noreferrer' }, s.source);
      dd.appendChild(a);
    } else {
      dd.appendChild(document.createTextNode(s.source));
    }
    dd.appendChild(document.createTextNode(` · ${tierLabel2} · ${s.date || ''}`));
    dl.appendChild(dt);
    dl.appendChild(dd);
  }
  tt.appendChild(dl);
  tt.hidden = false;
  positionTooltip(tt, anchor);
}

function positionTooltip(tt, anchor) {
  const rect = anchor.getBoundingClientRect();
  const ttRect = tt.getBoundingClientRect();
  const margin = 8;
  let x = rect.left + rect.width / 2 - ttRect.width / 2;
  let y = rect.bottom + margin;
  if (y + ttRect.height > window.innerHeight) y = rect.top - ttRect.height - margin;
  if (x < margin) x = margin;
  if (x + ttRect.width > window.innerWidth - margin) x = window.innerWidth - ttRect.width - margin;
  tt.style.left = `${Math.max(0, x)}px`;
  tt.style.top = `${Math.max(0, y)}px`;
}

function hideTooltip() {
  const tt = document.getElementById('tooltip');
  if (tt) tt.hidden = true;
}

/* ---------- GPU detect + select ---------- */

async function detectGpu() {
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
    const candidates = [
      `${vendor}_${arch}`,
      vendor,
      arch
    ];
    for (const c of candidates) {
      const path = State.gpu.webgpuVendorMap?.[c];
      if (path) {
        const [g, m] = path.split('.');
        const found = State.gpu[g]?.[m];
        if (found) return { id: path, ...found };
      }
    }
    return { id: null, vendor, arch, raw: info };
  } catch (e) {
    return null;
  }
}

function populateGpuSelect() {
  const sel = document.getElementById('filter-gpu-select');
  if (!sel) return;
  // Clean (keep first 'auto' option)
  while (sel.options.length > 1) sel.remove(1);

  const groups = [
    ['nvidia', 'NVIDIA'],
    ['apple', 'Apple Silicon'],
    ['amd', 'AMD'],
    ['intel', 'Intel']
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

function resolveGpuVram() {
  const override = Number(document.getElementById('filter-vram-override').value);
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
  if (info) State.vram = effectiveVram(info);
  else State.vram = null;
}

function effectiveVram(info) {
  if (!info) return null;
  const v = Number(info.vram);
  if (!Number.isFinite(v)) return null;
  return v;
}

function updateGpuStatus() {
  const status = document.getElementById('gpu-status');
  if (!status) return;
  if (State.vram == null) {
    status.textContent = State.selectedGpu === 'auto' ? t('ui.errors.webgpuUnsupported') : '';
  } else {
    status.textContent = `VRAM: ~${State.vram} GB`;
  }
}

/* ---------- export ---------- */

async function exportElement(element, filename) {
  if (typeof window.html2canvas !== 'function') {
    alert(t('ui.errors.exportFailed'));
    return;
  }
  const wasExporting = document.body.classList.contains('exporting');
  if (!wasExporting) document.body.classList.add('exporting');
  try {
    const bg = (getComputedStyle(document.body).getPropertyValue('--bg').trim()) || '#0b0d10';
    const canvas = await window.html2canvas(element, {
      scale: 2,
      backgroundColor: bg,
      useCORS: true,
      logging: false,
      windowWidth: document.documentElement.scrollWidth
    });
    await new Promise((resolve) => {
      canvas.toBlob((blob) => {
        if (!blob) { resolve(); return; }
        const url = URL.createObjectURL(blob);
        const a = el('a', { href: url, download: `${filename}.png` });
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
        resolve();
      }, 'image/png');
    });
  } catch (e) {
    console.error('export failed', e);
    alert(t('ui.errors.exportFailed'));
  } finally {
    if (!wasExporting) document.body.classList.remove('exporting');
  }
}

/* ---------- event wiring ---------- */

function wireEvents() {
  // Lang toggle (segmented)
  document.querySelectorAll('.lang-toggle button[data-lang]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const next = btn.dataset.lang;
      if (next && next !== State.lang) await switchLanguage(next);
    });
  });

  // Theme toggle (segmented)
  document.querySelectorAll('.theme-toggle button[data-theme]').forEach((btn) => {
    btn.addEventListener('click', () => switchTheme(btn.dataset.theme));
  });

  // Preset
  document.getElementById('weights-preset').addEventListener('change', (e) => {
    const v = e.target.value;
    if (v && v !== 'custom') applyPreset(v);
  });

  // Reset
  document.getElementById('weights-reset').addEventListener('click', () => {
    resetWeights();
    syncPresetSelect();
  });

  // Search filter
  const searchInput = document.getElementById('filter-search');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      State.filters.search = String(e.target.value || '').trim();
      writeStorage(STORAGE.filters, State.filters);
      renderAll();
    });
  }

  // Filters
  document.getElementById('filter-deployment').addEventListener('change', (e) => {
    State.filters.deployment = e.target.value;
    writeStorage(STORAGE.filters, State.filters);
    resolveGpuVram();
    updateGpuStatus();
    renderAll();
  });
  document.getElementById('filter-open-only').addEventListener('change', (e) => {
    State.filters.openOnly = e.target.checked;
    writeStorage(STORAGE.filters, State.filters);
    renderAll();
  });
  document.getElementById('filter-tier').addEventListener('change', (e) => {
    State.filters.tier = e.target.value;
    writeStorage(STORAGE.filters, State.filters);
    renderAll();
  });

  // GPU selection
  document.getElementById('filter-gpu-select').addEventListener('change', (e) => {
    State.selectedGpu = e.target.value;
    writeStorage(STORAGE.gpu, State.selectedGpu);
    resolveGpuVram();
    updateGpuStatus();
    renderAll();
  });
  document.getElementById('filter-vram-override').addEventListener('input', () => {
    resolveGpuVram();
    writeStorage(STORAGE.vram, State.vram);
    updateGpuStatus();
    renderAll();
  });

  // Section export buttons
  document.querySelectorAll('[data-export-trigger]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const sectionId = btn.getAttribute('data-export-trigger');
      const target = document.querySelector(`[data-export-section="${sectionId}"]`);
      if (target) exportElement(target, `aicodermap-${sectionId}`);
    });
  });

  // Full page export
  document.getElementById('export-full').addEventListener('click', () => {
    const main = document.querySelector('main.app-main');
    if (main) exportElement(main, 'aicodermap-full');
  });

  // Hide tooltip on scroll/resize
  window.addEventListener('scroll', hideTooltip, { passive: true });
  window.addEventListener('resize', hideTooltip);
}

/* ---------- language switch ---------- */

function syncLangToggleUi() {
  document.querySelectorAll('.lang-toggle button[data-lang]').forEach((btn) => {
    const active = btn.dataset.lang === State.lang;
    btn.classList.toggle('active', active);
    btn.setAttribute('aria-pressed', String(active));
  });
}

function applyTheme(theme) {
  const t = (theme === 'light' || theme === 'dark') ? theme : 'dark';
  document.documentElement.setAttribute('data-theme', t);
  document.querySelectorAll('.theme-toggle button[data-theme]').forEach((btn) => {
    const active = btn.dataset.theme === t;
    btn.classList.toggle('active', active);
    btn.setAttribute('aria-pressed', String(active));
  });
}

function switchTheme(theme) {
  if (theme !== 'dark' && theme !== 'light') return;
  applyTheme(theme);
  writeStorage(STORAGE.theme, theme);
}

async function switchLanguage(lang) {
  const next = await loadI18n(lang);
  if (!next) return;
  State.i18n = next;
  State.lang = lang;
  writeStorage(STORAGE.language, lang);
  applyI18n(document);
  syncLangToggleUi();
  renderWeightsEditor();
  renderAll();
  populateGpuSelect();
  syncPresetSelect();
}

/* ---------- bootstrap ---------- */

async function bootstrap() {
  // Theme — apply before any paint to avoid flash
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

  // Follow system theme changes only if user hasn't explicitly chosen
  if (window.matchMedia && !storedTheme) {
    try {
      window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', (e) => {
        if (!readStorage(STORAGE.theme, null)) {
          applyTheme(e.matches ? 'light' : 'dark');
        }
      });
    } catch (_) { /* older browsers ignore */ }
  }

  // Restore prefs
  const storedLang = readStorage(STORAGE.language, null);
  const navLang = (navigator.language || '').toLowerCase();
  const initialLang = (storedLang === 'en' || storedLang === 'tr')
    ? storedLang
    : (navLang.startsWith('tr') ? 'tr' : 'en');
  State.lang = initialLang;

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

  // Load i18n (with fallback)
  const [primary, fallback] = await Promise.all([
    loadI18n(State.lang),
    State.lang === 'tr' ? null : loadI18n('tr')
  ]);
  State.i18n = primary || (await loadI18n('tr')) || {};
  State.i18nFallback = fallback || State.i18n;

  applyI18n(document);
  syncLangToggleUi();

  // Load data
  try {
    await loadData();
  } catch (e) {
    console.error('data load failed', e);
    const list = document.getElementById('models-list');
    if (list) {
      clear(list);
      list.appendChild(el('p', { class: 'loading' }, t('ui.errors.fetchFailed')));
    }
    return;
  }

  // Restore filter UI state
  document.getElementById('filter-deployment').value = State.filters.deployment;
  document.getElementById('filter-open-only').checked = !!State.filters.openOnly;
  document.getElementById('filter-tier').value = State.filters.tier;
  const searchEl = document.getElementById('filter-search');
  if (searchEl) searchEl.value = State.filters.search || '';

  populateGpuSelect();

  // Detect GPU (best-effort, async)
  State.detectedGpu = await detectGpu();
  if (State.detectedGpu) {
    const sel = document.getElementById('filter-gpu-select');
    // If user previously selected explicit GPU, honor it
    if (State.selectedGpu && State.selectedGpu !== 'auto' && [...sel.options].some(o => o.value === State.selectedGpu)) {
      sel.value = State.selectedGpu;
    } else {
      sel.value = 'auto';
      State.selectedGpu = 'auto';
    }
  } else {
    document.getElementById('filter-gpu-select').value = State.selectedGpu;
  }

  // Restore VRAM override input
  if (Number.isFinite(State.vram) && State.selectedGpu === 'auto' && !State.detectedGpu) {
    document.getElementById('filter-vram-override').value = String(State.vram);
  }

  resolveGpuVram();
  updateGpuStatus();

  renderWeightsEditor();
  syncPresetSelect();
  renderAll();
  wireEvents();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootstrap);
} else {
  bootstrap();
}
