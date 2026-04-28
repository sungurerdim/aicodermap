// Data layer: HTTP fetch, score compute, contradiction detect, pricing
// view + formatters, filter predicates.

import {
  State, BENCH_KEYS, CONTRADICTION_WARN, CONTRADICTION_BLOCK,
  validateModels,
} from './core.js';

export async function fetchJson(path) {
  const res = await fetch(path, { cache: 'no-cache' });
  if (!res.ok) throw new Error(`${path} ${res.status}`);
  return res.json();
}

export async function loadData() {
  const [models, sources, gpu] = await Promise.all([
    fetchJson('./data/models.json'),
    fetchJson('./data/sources.json'),
    fetchJson('./data/gpu-database.json'),
  ]);
  State.models = validateModels(models);
  State.sources = (sources && typeof sources === 'object') ? sources : {};
  if (gpu && typeof gpu === 'object') State.gpu = { ...State.gpu, ...gpu };
}

export function scoreClass(v) {
  if (v == null || !Number.isFinite(v)) return 'score-na';
  if (v >= 70) return 'score-high';
  if (v >= 50) return 'score-mid';
  return 'score-low';
}

// Weighted composite with sqrt-coverage penalty so a model with one cherry-
// picked high score does not outrank a broader model with more verified data.
//
//   raw      = weightedSum / coveredWeight   (avg of available scores)
//   coverage = coveredWeight / activeWeight  (fraction of profile covered, 0..1)
//   score    = raw × √coverage               (smoother than raw × coverage)
//
// Decay: 100% cov → ×1.00, 50% → ×0.71, 25% → ×0.50, 10% → ×0.32. Active weight
// is the sum of weights[k] for benchmarks the *current profile* enables (>0);
// missing scores within an active profile pull the score down without zeroing.
export function compositeScore(model, weights) {
  let coveredWeight = 0;
  let activeWeight = 0;
  let weightedSum = 0;
  for (const k of BENCH_KEYS) {
    const w = weights[k];
    if (!w) continue;
    activeWeight += w;
    const s = model.bench?.[k];
    if (s == null || !Number.isFinite(s)) continue;
    coveredWeight += w;
    weightedSum += w * s;
  }
  if (activeWeight === 0 || coveredWeight === 0) return null;
  const raw = weightedSum / coveredWeight;
  const coverage = coveredWeight / activeWeight;
  return raw * Math.sqrt(coverage);
}

// Coverage as a 0..1 fraction of profile weight that the model has scores for.
// UI uses this for the "Coverage XX%" badge so users can read why a composite
// is low without reverse-engineering the formula.
export function coverageOf(model, weights) {
  let coveredWeight = 0;
  let activeWeight = 0;
  for (const k of BENCH_KEYS) {
    const w = weights[k];
    if (!w) continue;
    activeWeight += w;
    const s = model.bench?.[k];
    if (s == null || !Number.isFinite(s)) continue;
    coveredWeight += w;
  }
  if (activeWeight === 0) return null;
  return coveredWeight / activeWeight;
}

export function fmtScore(v, digits = 1) {
  if (v == null || !Number.isFinite(v)) return '—';
  return v.toFixed(digits);
}

export function contradictionFor(modelId, benchKey) {
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

// Schema v2 multi-provider pricing view. Backward-compatible with legacy flat
// `pricing.api: {in,out,cacheHit}` shape — wrapped as single-element array.
export function pricingView(model) {
  const p = model.pricing || {};
  let api = p.api;
  if (api && !Array.isArray(api) && typeof api === 'object') {
    api = [{
      provider: 'official', in: api.in ?? null, out: api.out ?? null,
      cacheHit: api.cacheHit ?? null, throughput: null, url: null,
      fetched: model.lastUpdated,
    }];
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

export function fmtPriceMoney(v) {
  if (v == null) return '—';
  return `$${Number(v).toString()}`;
}

export function fmtPriceRange(pair) {
  if (!pair) return '—';
  const [a, b] = pair;
  if (a == null && b == null) return '—';
  if (a === b || b == null) return fmtPriceMoney(a);
  return `${fmtPriceMoney(a)}–${fmtPriceMoney(b)}`;
}

export function fmtPriceCell(model) {
  const v = pricingView(model);
  const inS = fmtPriceRange(v.range?.in);
  const outS = fmtPriceRange(v.range?.out);
  if (inS === '—' && outS === '—') return '—';
  return `${inS} / ${outS}`;
}

export function fmtContext(n) {
  if (!Number.isFinite(n)) return '—';
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(n % 1_000_000 === 0 ? 0 : 1)}M`;
  if (n >= 1000) return `${Math.round(n / 1000)}K`;
  return String(n);
}

export function isLocalRunnable(m) {
  if (m.tier === 'ollama' || m.tier === 'gemma') return true;
  if (Number.isFinite(m.vramRequirement)) return true;
  if (Array.isArray(m.unslothVariants) && m.unslothVariants.length > 0) return true;
  return false;
}
