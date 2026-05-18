// Data layer: HTTP fetch, score compute, contradiction detect, pricing
// view + formatters, filter predicates.

import {
  State, BENCH_KEYS, CONTRADICTION_WARN, CONTRADICTION_BLOCK,
  validateModels, normalizeBenchScore,
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
  const [models, sources, gpu, meta, reliability] = await Promise.all([
    fetchJson('models.json'),
    fetchJson('sources.json'),
    fetchJson('gpu-database.json'),
    // _meta.json is best-effort — older deploys lack it, so a 404 is silent.
    fetchJson('_meta.json').catch(() => null),
    // Phase R3: per-(source, bench) reliability posterior. Older deploys
    // lack the file, so a 404 falls back to an empty ledger that yields
    // neutral 1.0 multipliers everywhere (no behavior change).
    fetchJson('source-reliability.json').catch(() => null),
  ]);
  State.models = validateModels(models);
  State.sources = (sources && typeof sources === 'object') ? sources : {};
  if (gpu && typeof gpu === 'object') State.gpu = { ...State.gpu, ...gpu };
  if (meta && typeof meta === 'object') State.meta = meta;
  State.reliability = (reliability && typeof reliability === 'object')
    ? reliability
    : { schemaVersion: 'v1', halfLifeCycles: 3, coldStartN: 10, sources: {} };
}

// Phase R5: mirror of scripts/lib/tiers.py:INTERVAL_DECAY_CURVES. Exposed
// so future card/tooltip rendering can label per-source recency curves
// without duplicating the lookup. Each curve is a list of
// [maxAgeDays, weight] pairs in ascending threshold order.
export const INTERVAL_DECAY_CURVES = Object.freeze({
  default: [[30, 1.00], [90, 0.85], [180, 0.70], [365, 0.50], [1e9, 0.30]],
  weekly:  [[30, 0.80], [90, 0.40], [180, 0.10], [1e9, 0.00]],
  monthly: [[30, 0.95], [90, 0.75], [180, 0.50], [365, 0.20], [1e9, 0.05]],
  quarterly: [[30, 1.00], [90, 0.95], [180, 0.85], [365, 0.60], [1e9, 0.30]],
  annual:  [[30, 1.00], [90, 1.00], [180, 0.95], [365, 0.85], [1e9, 0.60]],
});

// Mirror of scripts/lib/reliability.py:source_identity — canonical hostname,
// lowercased, www-stripped. Returns empty string when the URL is unusable.
function sourceIdentity(url) {
  if (!url) return '';
  try {
    const u = new URL(String(url).trim());
    let host = (u.hostname || '').toLowerCase().trim();
    if (host.startsWith('www.')) host = host.slice(4);
    return host;
  } catch {
    return '';
  }
}

// Mirror of scripts/lib/reliability.py:posterior_accuracy.
// Beta(1+a, 1+d) posterior mean.
function posteriorMean(agree, disagree) {
  const a = 1 + Number(agree || 0);
  const b = 1 + Number(disagree || 0);
  const denom = a + b;
  return denom > 0 ? a / denom : 0.5;
}

// Mirror of scripts/lib/reliability.py:reliability_multiplier with the
// same hierarchical fallback: per-(source, bench) -> per-source global ->
// cold-start neutral 1.0. Clamped to [0.3, 1.0]. Returns 1.0 when the
// ledger is missing or empty.
export function sourceReliability(url, benchKey) {
  const ledger = State.reliability;
  if (!ledger || typeof ledger !== 'object') return 1.0;
  const sid = sourceIdentity(url);
  if (!sid) return 1.0;
  const src = (ledger.sources || {})[sid];
  if (!src) return 1.0;
  const coldStart = Number(ledger.coldStartN || 10);
  if (benchKey) {
    const bench = (src.byBench || {})[benchKey];
    if (bench) {
      const n = Number(bench.agree || 0) + Number(bench.disagree || 0);
      if (n >= coldStart) {
        const p = posteriorMean(bench.agree, bench.disagree);
        return Math.max(0.3, Math.min(1.0, p));
      }
    }
  }
  const g = src.global || {};
  const gn = Number(g.agree || 0) + Number(g.disagree || 0);
  if (gn >= coldStart) {
    const p = posteriorMean(g.agree, g.disagree);
    return Math.max(0.3, Math.min(1.0, p));
  }
  return 1.0;
}

export function scoreClass(v) {
  if (v == null || !Number.isFinite(v)) return 'score-na';
  if (v >= 70) return 'score-high';
  if (v >= 50) return 'score-mid';
  return 'score-low';
}

// Per-bench unit metadata — keys that deviate from the default "percent" scale.
const BENCH_UNITS = { cfElo: 'elo', webDevElo: 'elo' };
const BENCH_DIRECTION = { aaOmni: 'lower_better' };

export function formatBenchValue(key, value) {
  if (value == null || !Number.isFinite(value)) return '—';
  const unit = BENCH_UNITS[key] || 'percent';
  const dir = BENCH_DIRECTION[key] || 'higher_better';
  if (unit === 'elo') return `${Math.round(value)} ELO`;
  const pct = `${value.toFixed(1)}%`;
  return dir === 'lower_better' ? `${pct} ↓` : pct;
}

// Returns the most recent `fetched` ISO date across all sources for a cell,
// or null if no sources exist.
export function getCellFreshness(modelId, benchKey) {
  const entries = (State.sources[`${modelId}.${benchKey}`]) || [];
  if (!entries.length) return null;
  let latest = null;
  for (const e of entries) {
    const f = e.fetched || e.lastChecked || null;
    if (f && (!latest || f > latest)) latest = f;
  }
  return latest;
}

// Returns true if the cell's freshness is older than STALE_DAYS (14).
export function isCellStale(modelId, benchKey) {
  const freshness = getCellFreshness(modelId, benchKey);
  if (!freshness) return false;
  const age = (Date.now() - new Date(freshness).getTime()) / 86400000;
  return age > 14;
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

// Cell-level confidence in [0.05, 1.0]. Combines verification depth
// (#distinct sources), winning-source trustScore, and contradiction
// severity penalty. GREEN cells short-circuit to 1.0 so well-covered
// new models aren't penalized by the absence of cross-source disputes.
//
//   verif   = min(N_distinct_sources / 3, 1)
//   trust   = max(trustScore per source, fallback 0.4)
//   penalty = 0 (GREEN) | 0.15 (warn) | 0.4 (block)
//   conf    = max(0.05, verif * trust * (1 - penalty))
export function cellConfidence(modelId, benchKey) {
  const entries = State.sources[`${modelId}.${benchKey}`];
  if (!Array.isArray(entries) || !entries.length) return 1.0;
  // Distinct primary URLs (drop pseudo-source rescue entries from the count).
  const PSEUDO = new Set(['snapshot-extraction', 'auto-resolution candidate', 'synth-backfill']);
  const urls = new Set();
  let maxTrust = 0;
  for (const e of entries) {
    if (!e || PSEUDO.has(e.source)) continue;
    if (e.url) urls.add(String(e.url).toLowerCase());
    const t = Number(e.trustScore);
    // Phase R3: weight per-source trust by its Beta-Binomial reliability
    // posterior on this bench (cold-start sources stay at 1.0 neutral).
    const rel = sourceReliability(e.url, benchKey);
    const tw = Number.isFinite(t) ? t * rel : 0;
    if (tw > maxTrust) maxTrust = tw;
  }
  const verif = Math.min((urls.size || 1) / 3, 1);
  const trust = maxTrust > 0 ? maxTrust : 0.4;
  const c = contradictionFor(modelId, benchKey);
  let penalty = 0;
  if (c) {
    if (c.delta >= CONTRADICTION_BLOCK) penalty = 0.4;
    else if (c.delta >= CONTRADICTION_WARN) penalty = 0.15;
  }
  const conf = verif * trust * (1 - penalty);
  return Math.max(0.05, Math.min(1.0, conf));
}

// Returns the set of bench keys flagged as quarantined for this model.
// merge.py stamps `model.benchQuarantine[bench] = true` whenever the
// pick_winner.quarantine flag fires (scaffold variants, confidence<0.2,
// or excessive value dispersion). compositeScore() skips these cells.
export function quarantinedBenches(model) {
  const q = model?.benchQuarantine;
  if (!q || typeof q !== 'object') return new Set();
  const out = new Set();
  for (const [k, v] of Object.entries(q)) if (v) out.add(k);
  return out;
}

// Weighted composite combining three honesty mechanisms:
//
//   raw       = weightedSum / coveredWeight   (confidence-weighted average
//                                              of available scores)
//   coverage  = coveredWeight / activeWeight  (fraction of profile covered)
//   score     = raw × √coverage               (sparse data pulls score down)
//
// Coverage penalty: 100% → ×1.00, 50% → ×0.71, 25% → ×0.50. Stops a 1-test
// cherry-picked high score from outranking a broader, verified model.
//
// FAZ 8.A.3c (2026-05-18): replaced the prior fixed-cap confidence haircut
// with per-cell confidence weighting. Each cell's contribution scales by
// cellConfidence(); low-confidence cells (single-source RED contradictions)
// still count but with reduced influence. Mitigates the bug where new
// frontier models with sparse-but-clean GREEN coverage were ranked below
// older models with contested but verbose provenance.
//
// Quarantined cells (model.benchQuarantine) are excluded entirely.
export function compositeScore(model, weights) {
  let coveredWeight = 0;
  let activeWeight = 0;
  let weightedSum = 0;
  const quarantined = quarantinedBenches(model);
  for (const k of BENCH_KEYS) {
    const w = weights[k];
    if (!w) continue;
    activeWeight += w;
    if (quarantined.has(k)) continue;
    const raw = model.bench?.[k];
    const s = normalizeBenchScore(k, raw);
    if (s == null || !Number.isFinite(s)) continue;
    const conf = cellConfidence(model.id, k);
    coveredWeight += w * conf;
    weightedSum += w * s * conf;
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
export function fmtLastUpdated(s) {
  if (!s || typeof s !== 'string') return '';
  const t = s.indexOf('T');
  return t < 0 ? '' : `${s.slice(0, t)} ${s.slice(t + 1, t + 6)}`;
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

// Multi-provider pricing view. Schema is canonical: `pricing.api` is an
// array of provider entries; `pricing.subscription` is an array of tier
// entries; `pricing.range` is the precomputed min/max envelope. Anything
// else is a contract violation that the SSOT audit catches.
export function pricingView(model) {
  const p = model.pricing || {};
  const api = Array.isArray(p.api) ? p.api : [];
  const ins = api.map(e => e?.in).filter(v => v != null);
  const outs = api.map(e => e?.out).filter(v => v != null);
  const chs = api.map(e => e?.cacheHit).filter(v => v != null);
  const range = p.range || {
    in: ins.length ? [Math.min(...ins), Math.max(...ins)] : null,
    out: outs.length ? [Math.min(...outs), Math.max(...outs)] : null,
    cacheHit: chs.length ? [Math.min(...chs), Math.max(...chs)] : null,
  };
  const subs = Array.isArray(p.subscription) ? p.subscription : [];
  // Blended: cheapest input + cheapest output combined via 3:1 input:output ratio.
  // Represents a typical mixed workload (3 input tokens per 1 output token).
  const minIn = range.in?.[0];
  const minOut = range.out?.[0];
  const blended = (minIn != null && minOut != null)
    ? (minIn * 3 + minOut) / 4
    : null;
  return { providers: api, range, subscriptions: subs, blended };
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

// Tier-2 imputation: for a null cell, return the mean of same-tier+provider peers
// that have a real value. Requires ≥3 peers; otherwise returns null (no guess).
// Imputed values are never written to storage — only used in compositeScoreImputed().
export function impute(model, key, allModels) {
  if (model.bench?.[key] != null) return model.bench[key];
  const peers = (allModels || []).filter(
    m => m.id !== model.id
      && m.tier === model.tier
      && m.bench?.[key] != null,
  );
  if (peers.length < 3) return null;
  const vals = peers.map(p => normalizeBenchScore(key, p.bench[key])).filter(v => v != null);
  if (vals.length < 3) return null;
  return vals.reduce((a, b) => a + b, 0) / vals.length;
}

// Composite score computed with Tier-2 imputed values for empty cells.
// Returns { score, imputedKeys } where imputedKeys lists which bench keys
// were imputed (so UI can show the toggle badge).
export function compositeScoreImputed(model, weights, allModels) {
  let coveredWeight = 0;
  let activeWeight = 0;
  let weightedSum = 0;
  const imputedKeys = [];
  for (const k of BENCH_KEYS) {
    const w = weights[k];
    if (!w) continue;
    activeWeight += w;
    const raw = model.bench?.[k] ?? impute(model, k, allModels);
    const s = normalizeBenchScore(k, raw);
    if (s == null || !Number.isFinite(s)) continue;
    coveredWeight += w;
    weightedSum += w * s;
    if (model.bench?.[k] == null) imputedKeys.push(k);
  }
  if (activeWeight === 0 || coveredWeight === 0) return { score: null, imputedKeys };
  const coverage = coveredWeight / activeWeight;
  return { score: (weightedSum / coveredWeight) * Math.sqrt(coverage), imputedKeys };
}

export function isLocalRunnable(m) {
  if (m.tier === 'ollama-local' || m.tier === 'gemma') return true;
  if (Number.isFinite(m.vramRequirement)) return true;
  if (Array.isArray(m.unslothVariants) && m.unslothVariants.length > 0) return true;
  return false;
}
