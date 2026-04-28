// Data layer: HTTP fetch, score compute, contradiction detect, pricing
// view + formatters, filter predicates.

import {
  State, BENCH_KEYS, CONTRADICTION_WARN, CONTRADICTION_BLOCK,
  validateModels,
} from './core.js';

// Resolve data URLs against this module's location so loadData() works whether
// the caller is index.html (project root) or assets/test/smoke.html (deeper).
// import.meta.url here = .../assets/js/data.js, so '../../data/' lands at
// .../data/.
const DATA_BASE = new URL('../../data/', import.meta.url);

// Page-load cache-bust token. GitHub Pages CDN respects Cache-Control no-cache
// inconsistently; appending ?v=<timestamp> guarantees a fresh asset each load
// even when the CDN holds a long-TTL copy. main.js sets State.cacheBust before
// data fetch; if missing (e.g. smoke.html harness), fall back to import time.
const FALLBACK_BUST = String(Date.now());

export async function fetchJson(name) {
  const bust = (typeof window !== 'undefined' && window.__ACM_CACHE_BUST__)
    || FALLBACK_BUST;
  const url = new URL(`${name}?v=${encodeURIComponent(bust)}`, DATA_BASE);
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) throw new Error(`${name} ${res.status}`);
  // models.json's response headers fingerprint the served deploy:
  // - Last-Modified: when Pages CDN last refreshed the file (deploy time).
  // - ETag: GitHub Pages' content-derived hash; two distinct file contents
  //   produce two distinct ETags. freshness.js polls HEAD requests and
  //   compares ETag against State.dataEtag to detect a fresh deploy without
  //   reloading the body or hitting GitHub's API rate limit.
  if (name === 'models.json') {
    const lm = res.headers.get('Last-Modified');
    if (lm) State.dataDeployedAt = lm;
    const et = res.headers.get('ETag');
    if (et) State.dataEtag = et;
  }
  return res.json();
}

export async function loadData() {
  const [models, sources, gpu] = await Promise.all([
    fetchJson('models.json'),
    fetchJson('sources.json'),
    fetchJson('gpu-database.json'),
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

// Worst within-tier disagreement for a contested cell. We separate same-tier
// disputes (real residual uncertainty: two equally-trusted observers landing
// on different numbers) from cross-tier disputes (already settled by the
// autoResolveWinner picking the higher-trust tier). Returns 0 when every
// disagreement is purely between tiers.
function intraTierMaxDelta(contradiction) {
  const byTier = {};
  for (const s of contradiction.sources) {
    const v = Number(s.value);
    if (!Number.isFinite(v)) continue;
    const tier = s.tier || '?';
    (byTier[tier] = byTier[tier] || []).push(v);
  }
  let maxDelta = 0;
  for (const tier of Object.keys(byTier)) {
    const vs = byTier[tier];
    if (vs.length < 2) continue;
    const d = Math.max(...vs) - Math.min(...vs);
    if (d > maxDelta) maxDelta = d;
  }
  return maxDelta;
}

// Weighted composite combining three honesty mechanisms:
//
//   raw       = weightedSum / coveredWeight   (avg of available scores, minus
//                                              a confidence haircut on cells
//                                              with same-tier disagreement)
//   coverage  = coveredWeight / activeWeight  (fraction of profile covered)
//   score     = raw × √coverage               (sparse data pulls score down)
//
// Coverage penalty: 100% → ×1.00, 50% → ×0.71, 25% → ×0.50. Stops a 1-test
// cherry-picked high score from outranking a broader, verified model.
//
// Confidence haircut: applied only when the *same tier* disagrees by ≥3pp.
// Cross-tier disputes (e.g. I-tier 80 vs S-tier 85) are already resolved by
// autoResolveWinner picking the higher-trust source — counting them again
// here would be double-counting. Same-tier disputes (e.g. I-tier 80 vs
// I-tier 86) reflect genuine measurement uncertainty: subtract
// `min((intra − 3) / 2, 5)` from that cell's score. Cap = 5pp/cell so a
// single extreme outlier cannot dominate the composite.
export function compositeScore(model, weights) {
  let coveredWeight = 0;
  let activeWeight = 0;
  let weightedSum = 0;
  let confidenceHaircut = 0;
  for (const k of BENCH_KEYS) {
    const w = weights[k];
    if (!w) continue;
    activeWeight += w;
    const s = model.bench?.[k];
    if (s == null || !Number.isFinite(s)) continue;
    coveredWeight += w;
    weightedSum += w * s;

    const c = contradictionFor(model.id, k);
    if (c && c.delta >= CONTRADICTION_BLOCK) {
      const intra = intraTierMaxDelta(c);
      if (intra >= CONTRADICTION_WARN) {
        const excess = intra - CONTRADICTION_WARN;
        const haircut = Math.min(excess / 2, 5);
        confidenceHaircut += w * haircut;
      }
    }
  }
  if (activeWeight === 0 || coveredWeight === 0) return null;
  const raw = (weightedSum - confidenceHaircut) / coveredWeight;
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

// Count of cells in the active preset that actually trigger a confidence
// haircut — same-tier disputes with ≥3pp intra-tier disagreement on top of
// the ≥5pp BLOCK threshold. Cells with cross-tier-only disagreement are
// excluded because autoResolveWinner already settled them, so a UI badge
// based on them would mislead the user about score reductions.
export function disputedCount(model, weights) {
  let n = 0;
  for (const k of BENCH_KEYS) {
    const w = weights[k];
    if (!w) continue;
    const s = model.bench?.[k];
    if (s == null || !Number.isFinite(s)) continue;
    const c = contradictionFor(model.id, k);
    if (!c || c.delta < CONTRADICTION_BLOCK) continue;
    const intra = intraTierMaxDelta(c);
    if (intra >= CONTRADICTION_WARN) n++;
  }
  return n;
}

export function fmtScore(v, digits = 1) {
  if (v == null || !Number.isFinite(v)) return '—';
  return v.toFixed(digits);
}

// ISO 8601 datetime ("2026-04-28T17:23:45Z") → "2026-04-28 17:23".
// Date-only legacy ("2026-04-28") passes through unchanged.
export function fmtLastUpdated(s) {
  if (!s || typeof s !== 'string') return '';
  const t = s.indexOf('T');
  if (t < 0) return s;
  return `${s.slice(0, t)} ${s.slice(t + 1, t + 6)}`;
}

// HTTP-date string ("Tue, 28 Apr 2026 14:07:20 GMT") → "2026-04-28 14:07 UTC".
// Returns '' on parse failure so callers can fall back to a static label.
export function fmtDeployTime(httpDate) {
  if (!httpDate) return '';
  const d = new Date(httpDate);
  if (Number.isNaN(d.getTime())) return '';
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())} `
    + `${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())} UTC`;
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
