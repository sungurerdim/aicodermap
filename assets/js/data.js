// Data layer: HTTP fetch, score compute, contradiction detect, pricing
// view + formatters, filter predicates.

import {
  State, BENCH_KEYS, CONTRADICTION_WARN, CONTRADICTION_BLOCK,
  validateModels, normalizeBenchScore,
  getContradictionThresholds, getBenchKind, isAtomicBench, isVendorComposite,
  getVendorCompositeMeta, getCompositePolicy, getPresetTiers,
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
  const [models, sources, gpu, meta, reliability, whitelist] = await Promise.all([
    fetchJson('models.json'),
    fetchJson('sources.json'),
    fetchJson('gpu-database.json'),
    // _meta.json is best-effort — older deploys lack it, so a 404 is silent.
    fetchJson('_meta.json').catch(() => null),
    // Phase R3: per-(source, bench) reliability posterior. Older deploys
    // lack the file, so a 404 falls back to an empty ledger that yields
    // neutral 1.0 multipliers everywhere (no behavior change).
    fetchJson('source-reliability.json').catch(() => null),
    // F1+F2 (2026-05-18): sources-whitelist.json _schema drives normalize/
    // confidence/presets/benchKind/vendorComposites. Best-effort — older
    // deploys lack the file (or new schema blocks); JS falls back to
    // hardcoded literals in core.js so no behavior change on miss.
    fetchJson('sources-whitelist.json').catch(() => null),
  ]);
  State.models = validateModels(models);
  State.sources = (sources && typeof sources === 'object') ? sources : {};
  if (gpu && typeof gpu === 'object') State.gpu = { ...State.gpu, ...gpu };
  if (meta && typeof meta === 'object') State.meta = meta;
  State.reliability = (reliability && typeof reliability === 'object')
    ? reliability
    : { schemaVersion: 'v1', halfLifeCycles: 3, coldStartN: 10, sources: {} };
  // F1+F2: extract _schema; rest of whitelist (vendors/leaderboards/…) is
  // skill+agent territory and not needed at render time.
  State.schema = (whitelist && typeof whitelist === 'object' && whitelist._schema)
    ? whitelist._schema
    : {};
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

// Phase R6: badge state for a source link. Returns null when cold-start
// (no badge), otherwise an object describing how the link should render:
//   kind:     'exceptional' (>=0.85) | 'low' (<=0.55) | 'normal' (between)
//   accuracy: posterior mean in [0,1]
//   n:        decayed sample count (audit visibility)
// Frontend wraps each source link in `data-reliability="<kind>"` so CSS
// can prefix a glyph and tooltip can show the percentage.
export function sourceReliabilityBadge(url, benchKey = '') {
  const ledger = State.reliability;
  if (!ledger || typeof ledger !== 'object') return null;
  const sid = sourceIdentity(url);
  if (!sid) return null;
  const src = (ledger.sources || {})[sid];
  if (!src) return null;
  const coldStart = Number(ledger.coldStartN || 10);
  let agree = 0;
  let disagree = 0;
  if (benchKey) {
    const bench = (src.byBench || {})[benchKey];
    if (bench) {
      agree = Number(bench.agree || 0);
      disagree = Number(bench.disagree || 0);
    }
  }
  let n = agree + disagree;
  if (n < coldStart) {
    const g = src.global || {};
    agree = Number(g.agree || 0);
    disagree = Number(g.disagree || 0);
    n = agree + disagree;
  }
  if (n < coldStart) return null;
  const accuracy = posteriorMean(agree, disagree);
  let kind = 'normal';
  if (accuracy >= 0.85) kind = 'exceptional';
  else if (accuracy <= 0.55) kind = 'low';
  return { kind, accuracy, n };
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
// F1+F2 (2026-05-18): schema-driven. State.schema.confidence overrides
// hardcoded constants when present; fallback values match prior behavior.
export function cellConfidence(modelId, benchKey) {
  const entries = State.sources[`${modelId}.${benchKey}`];
  if (!Array.isArray(entries) || !entries.length) return 1.0;
  const cfg = (State.schema && State.schema.confidence) || {};
  const verifDivisor = Number(cfg.verifDivisor) || 3;
  const warnPen = Number.isFinite(cfg.contradictionWarnPenalty) ? cfg.contradictionWarnPenalty : 0.15;
  const blockPen = Number.isFinite(cfg.contradictionBlockPenalty) ? cfg.contradictionBlockPenalty : 0.40;
  const floor = Number.isFinite(cfg.confidenceFloor) ? cfg.confidenceFloor : 0.05;
  const ceiling = Number.isFinite(cfg.confidenceCeiling) ? cfg.confidenceCeiling : 1.0;
  const fallbackTrust = Number.isFinite(cfg.fallbackTrust) ? cfg.fallbackTrust : 0.40;
  const PSEUDO = new Set(Array.isArray(cfg.pseudoSources) && cfg.pseudoSources.length
    ? cfg.pseudoSources
    : ['snapshot-extraction', 'auto-resolution candidate', 'synth-backfill']);
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
  const verif = Math.min((urls.size || 1) / verifDivisor, 1);
  const trust = maxTrust > 0 ? maxTrust : fallbackTrust;
  const c = contradictionFor(modelId, benchKey);
  const thr = getContradictionThresholds();
  let penalty = 0;
  if (c) {
    if (c.delta >= thr.block) penalty = blockPen;
    else if (c.delta >= thr.warn) penalty = warnPen;
  }
  const conf = verif * trust * (1 - penalty);
  return Math.max(floor, Math.min(ceiling, conf));
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
// F1+F2 (2026-05-18): atomic-only aggregation. Vendor composites
// (aaIdx/aaCoding/aaAgentic/aaOmni) are excluded by getBenchKind — they
// surface separately via vendorComposites() in the cross-validation panel
// so we don't double-count benches they already aggregate. Coverage
// shrinkage exponent is now schema-driven (default 2 = sqrt).
export function compositeScore(model, weights) {
  let coveredWeight = 0;
  let activeWeight = 0;
  let weightedSum = 0;
  const quarantined = quarantinedBenches(model);
  const policy = getCompositePolicy();
  const expo = Number.isFinite(policy.coverageShrinkageExponent) && policy.coverageShrinkageExponent > 0
    ? policy.coverageShrinkageExponent : 2;
  for (const k of BENCH_KEYS) {
    const w = weights[k];
    if (!w) continue;
    // Atomic-only — vendor composites contribute to cross-validation panel,
    // not the AICoderMap composite (their componentBenches are already
    // counted at the atomic layer; including them = double counting).
    if (isVendorComposite(k)) continue;
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
  return raw * Math.pow(coverage, 1 / expo);
}

// Coverage as a 0..1 fraction of profile weight that the model has scores for.
// UI uses this for the "Coverage XX%" badge so users can read why a composite
// is low without reverse-engineering the formula.
// F1+F2: vendor composites excluded (atomic-only) to match compositeScore().
export function coverageOf(model, weights) {
  let coveredWeight = 0;
  let activeWeight = 0;
  for (const k of BENCH_KEYS) {
    const w = weights[k];
    if (!w) continue;
    if (isVendorComposite(k)) continue;
    activeWeight += w;
    const s = model.bench?.[k];
    if (s == null || !Number.isFinite(s)) continue;
    coveredWeight += w;
  }
  if (activeWeight === 0) return null;
  return coveredWeight / activeWeight;
}

// Bench-key display ordering shared by the comparison table (columns) and the
// model card (grid). Splits BENCH_KEYS into the benches the active preset
// scores (weight > 0) and those it excludes (weight 0). The in-preset group is
// sorted by weight descending so the heaviest benchmark sits first (leftmost);
// ties keep BENCH_KEYS order (stable sort). The excluded group keeps BENCH_KEYS
// order. Recomputed on every render, so switching preset re-orders both surfaces.
export function orderedBenchKeys(weights) {
  const w = weights || State.weights || {};
  const included = [];
  const excluded = [];
  for (const k of BENCH_KEYS) {
    if ((Number(w[k]) || 0) > 0) included.push(k);
    else excluded.push(k);
  }
  included.sort((a, b) => (Number(w[b]) || 0) - (Number(w[a]) || 0));
  return { included, excluded };
}

// ============================================================================
// F1+F2 (2026-05-18): VENDOR COMPOSITE + CROSS-VALIDATION layer.
// AICoderMap composite uses only atomic benches. Vendor-aggregated composites
// (aaIdx, aaCoding, aaAgentic, aaOmni) are shown as independent reference
// signals in a side panel — not mixed into our weighted average.
// ============================================================================

// Returns the vendor composite values + normalized scores + metadata for
// the keys listed in preset.vendorCompositeView (or all 4 AA composites
// when preset is null). Empty array when no schema present.
export function vendorComposites(model, presetName) {
  const tiers = presetName ? getPresetTiers(presetName) : null;
  const keys = tiers && tiers.vendorView.length ? tiers.vendorView : ['aaIdx', 'aaCoding', 'aaAgentic', 'aaOmni'];
  const out = [];
  for (const key of keys) {
    if (!isVendorComposite(key)) continue;
    const raw = model.bench?.[key];
    const normalized = normalizeBenchScore(key, raw);
    const meta = getVendorCompositeMeta(key);
    out.push({
      key,
      raw,
      normalized,
      label: meta?.label || key,
      labelShort: meta?.labelShort || key,
      publisher: meta?.publisher || null,
      publisherUrl: meta?.publisherUrl || null,
      domain: meta?.domain || null,
      missing: raw == null || !Number.isFinite(raw),
    });
  }
  return out;
}

// Vendor consensus score = coverage-penalized average of normalized vendor
// composites. F1+F2 bugfix (2026-05-18): early version averaged only present
// values which let a single-bench model (e.g., qwen3-32b with only aaIdx)
// outrank a 3-vendor model (opus-4-7 with aaIdx + aaCoding + aaOmni). Now
// applies coverage shrinkage = sqrt(present / expected) so sparse-but-strong
// values are honestly discounted. Also requires at least 1 vendor present
// AND coverage >= minConsensusCoverage (default 0.34 = at least 1 of 3, but
// 1-of-3 gets a 0.58 shrinkage which significantly demotes it).
export function vendorConsensusScore(model, presetName) {
  const vc = vendorComposites(model, presetName);
  const expected = vc.length;                          // size of preset.vendorCompositeView
  if (!expected) return null;
  const vals = vc.filter(v => v.normalized != null && Number.isFinite(v.normalized))
                 .map(v => v.normalized);
  if (!vals.length) return null;
  const raw = vals.reduce((a, b) => a + b, 0) / vals.length;
  const coverage = vals.length / expected;
  const policy = getCompositePolicy();
  const expo = policy.coverageShrinkageExponent > 0 ? policy.coverageShrinkageExponent : 2;
  return raw * Math.pow(coverage, 1 / expo);
}

// Agreement indicator between AICoderMap composite rank and vendor consensus
// rank for `model`, computed across `allModels`. Returns:
//   { aicmRank, consensusRank, gap, flag }
// flag ∈ {'consensus','mild-disagreement','controversy'} mapped from gap ≤5, ≤15, >15.
// Returns null if either rank cannot be computed.
export function crossValidationAgreement(model, allModels, weights, presetName) {
  if (!Array.isArray(allModels) || !allModels.length) return null;
  const aicmScores = allModels.map(m => ({ id: m.id, s: compositeScore(m, weights) }));
  const consScores = allModels.map(m => ({ id: m.id, s: vendorConsensusScore(m, presetName) }));
  const aicmRanked = aicmScores.filter(x => x.s != null).sort((a, b) => b.s - a.s);
  const consRanked = consScores.filter(x => x.s != null).sort((a, b) => b.s - a.s);
  const aicmRank = aicmRanked.findIndex(x => x.id === model.id);
  const consRank = consRanked.findIndex(x => x.id === model.id);
  if (aicmRank < 0 || consRank < 0) return null;
  const gap = Math.abs(aicmRank - consRank);
  let flag;
  if (gap <= 5) flag = 'consensus';
  else if (gap <= 15) flag = 'mild-disagreement';
  else flag = 'controversy';
  return { aicmRank: aicmRank + 1, consensusRank: consRank + 1, gap, flag };
}

// Score resolver — dispatches to the right scoring function based on
// State.scoreFn (set by applyPreset). UI consumers (render-table /
// render-card) can call this single helper instead of branching on
// preset kind. Returns null when score cannot be computed.
// F1+F2 (2026-05-18): when policy.imputationEnabled, AICM path uses
// compositeScoreImputed (peer-tier median fill for missing imputable cells,
// capped by maxImputedWeightShare). Vendor consensus path unaffected.
export function effectiveScore(model, weights, presetName) {
  const fn = State.scoreFn || 'aicm';
  if (fn === 'vendorConsensus') return vendorConsensusScore(model, presetName || State.activePresetName);
  const policy = getCompositePolicy();
  if (policy.imputationEnabled) {
    const out = compositeScoreImputed(model, weights, State.models, presetName);
    return out.score;
  }
  return compositeScore(model, weights);
}

// Same as effectiveScore but also returns the imputedKeys list (for UI
// "estimated" badge). Returns { score, imputedKeys, mode }.
export function effectiveScoreInfo(model, weights, presetName) {
  const fn = State.scoreFn || 'aicm';
  if (fn === 'vendorConsensus') {
    return { score: vendorConsensusScore(model, presetName || State.activePresetName), imputedKeys: [], mode: 'vendorConsensus' };
  }
  const policy = getCompositePolicy();
  if (policy.imputationEnabled) {
    const out = compositeScoreImputed(model, weights, State.models, presetName);
    return { score: out.score, imputedKeys: out.imputedKeys, mode: 'aicm-imputed' };
  }
  return { score: compositeScore(model, weights), imputedKeys: [], mode: 'aicm' };
}

// Tiered missing-data analysis for a model under a preset. Used by UI to
// show "limited data" badges and route models with ≥2 missing critical
// benches into the "Limited Coverage" section.
//   missingRequired: required benches missing → ⚠ rozet
//   missingCritical: critical benches missing — when ≥2, model is "limited coverage"
//   imputable:       benches eligible for peer-tier median fill (advisory)
export function presetTiersFor(model, presetName) {
  const tiers = getPresetTiers(presetName);
  const bench = model.bench || {};
  const has = (k) => {
    const v = bench[k];
    return v != null && Number.isFinite(v);
  };
  const missingRequired = [...tiers.required].filter(k => !has(k));
  const missingCritical = [...tiers.critical].filter(k => !has(k));
  const missingImputable = [...tiers.imputable].filter(k => !has(k));
  return {
    missingRequired,
    missingCritical,
    missingImputable,
    isLimitedCoverage: missingCritical.length >= 2,
    isLimitedData: missingRequired.length > 0,
  };
}

// Leaderboard rank gate (2026-06-07). A model is GATED — demoted out of the main
// ranking into a contiguous "Limited Coverage" band at the bottom — when it is
// missing any of the active preset's requiredBenches, or when its coverage falls
// below policy.rankGate.coverageFloor. Pure (no side effects). Reuses the SSOT
// missingRequired computation from presetTiersFor so the gate and the card badge
// can never disagree. `coverage` is the 0..1 fraction already computed by
// compositeUncertainty (passed in to avoid recomputing). Returns
// { gated, reason } where reason ∈ {'missing-required','low-coverage', null}.
//
// Why a gate on top of EB shrinkage: EB pulls missing benches toward the global
// median rather than zeroing them, so a model with a couple of extreme cells but
// a missing heaviest-weighted required bench (e.g. swePro in swe-focused) can
// float into the top. The gate enforces the preset's already-declared
// requiredBenches policy that the EB score alone ignores.
export function rankGateStatus(model, presetName, coverage) {
  const gate = getCompositePolicy().rankGate;
  if (!gate.enabled) return { gated: false, reason: null };
  if (gate.demoteMissingRequired) {
    const tiers = presetTiersFor(model, presetName);
    if (tiers.missingRequired.length > 0) return { gated: true, reason: 'missing-required' };
  }
  if (Number.isFinite(coverage) && coverage < gate.coverageFloor) {
    return { gated: true, reason: 'low-coverage' };
  }
  return { gated: false, reason: null };
}

// Count of cells in the active preset that actually trigger a confidence
// haircut — same-tier disputes with ≥3pp intra-tier disagreement on top of
// the ≥5pp BLOCK threshold. Cells with cross-tier-only disagreement are
// excluded because autoResolveWinner already settled them, so a UI badge
// based on them would mislead the user about score reductions.
export function disputedCount(model, weights) {
  let n = 0;
  const thr = getContradictionThresholds();
  for (const k of BENCH_KEYS) {
    const w = weights[k];
    if (!w) continue;
    const s = model.bench?.[k];
    if (s == null || !Number.isFinite(s)) continue;
    const c = contradictionFor(model.id, k);
    if (!c || c.delta < thr.block) continue;
    const intra = intraTierMaxDelta(c);
    if (intra >= thr.warn) n++;
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
  return t < 0 ? s : `${s.slice(0, t)} ${s.slice(t + 1, t + 6)}`;
}

// ISO datetime (or YYYY-MM-DD) → "2 gün 4 saat 13 dk önce" / "2d 4h 13m ago".
// Returns '' for invalid input. Uses i18n keys: ui.timeAgo.{justNow,suffix,d,h,m}
export function fmtTimeAgo(s, tFn) {
  if (!s || typeof s !== 'string') return '';
  const iso = s.includes('T') ? s : `${s}T00:00:00Z`;
  const then = new Date(iso);
  if (Number.isNaN(then.getTime())) return '';
  const diffMs = Date.now() - then.getTime();
  if (diffMs < 0) return '';
  const totalMin = Math.floor(diffMs / 60000);
  if (totalMin < 1) return tFn('ui.timeAgo.justNow');
  const days = Math.floor(totalMin / 1440);
  const hours = Math.floor((totalMin % 1440) / 60);
  const mins = totalMin % 60;
  const parts = [];
  if (days) parts.push(`${days}${tFn('ui.timeAgo.d')}`);
  if (hours) parts.push(`${hours}${tFn('ui.timeAgo.h')}`);
  if (mins && days === 0) parts.push(`${mins}${tFn('ui.timeAgo.m')}`);
  if (!parts.length) parts.push(`${totalMin}${tFn('ui.timeAgo.m')}`);
  return `${parts.join(' ')} ${tFn('ui.timeAgo.suffix')}`;
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
  const thr = getContradictionThresholds();
  let severity = null;
  if (delta >= thr.block) severity = 'danger';
  else if (delta >= thr.warn) severity = 'warn';
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
  // A quarantined own-value is untrusted (single-source / dispersed / low
  // confidence) — fall through to peer estimation instead of returning it.
  if (model.bench?.[key] != null && !quarantinedBenches(model).has(key)) return model.bench[key];
  const peers = (allModels || []).filter(
    m => m.id !== model.id
      && m.tier === model.tier
      && m.bench?.[key] != null
      && !quarantinedBenches(m).has(key),   // peers' quarantined values don't anchor the median
  );
  if (peers.length < 3) return null;
  const vals = peers.map(p => normalizeBenchScore(key, p.bench[key])).filter(v => v != null);
  if (vals.length < 3) return null;
  return vals.reduce((a, b) => a + b, 0) / vals.length;
}

// ── Empirical-Bayes leaderboard scoring (2026-06-06) ────────────────────────
// Replaces the blunt raw×√coverage penalty: a model's score is its observed-cell
// mean shrunk toward a conservative global-median baseline by `priorWeight`
// pseudo-weight, then docked a nonlinear penalty only once confidence drops
// below `confThreshold`. Missing benches are neither zeroed (penalty) nor scored
// as full marks — they pull toward "average until proven otherwise", with the
// pull inversely proportional to how much real data the model has. This fixes
// the case where a model dominating every measured bench ranked below a fully-
// covered weaker model purely from a √coverage haircut on a couple of gaps.

// Per-bench global median cache, keyed by the allModels array identity so it
// recomputes only when the dataset changes, not on every weight/sort tweak.
let _priorMedianCache = { token: null, byKey: new Map() };

function globalBenchMedian(key, allModels) {
  if (_priorMedianCache.token !== allModels) {
    _priorMedianCache = { token: allModels, byKey: new Map() };
  }
  if (_priorMedianCache.byKey.has(key)) return _priorMedianCache.byKey.get(key);
  const vals = [];
  for (const m of (allModels || [])) {
    if ((m.status || 'active') !== 'active') continue;
    if (quarantinedBenches(m).has(key)) continue;
    const raw = m.bench?.[key];
    if (raw == null || !Number.isFinite(raw)) continue;
    const s = normalizeBenchScore(key, raw);
    if (s != null && Number.isFinite(s)) vals.push(s);
  }
  let med = null;
  if (vals.length) {
    vals.sort((a, b) => a - b);
    const mid = Math.floor(vals.length / 2);
    med = vals.length % 2 ? vals[mid] : (vals[mid - 1] + vals[mid]) / 2;
  }
  _priorMedianCache.byKey.set(key, med);
  return med;
}

// Conservative prior = the weighted global-median profile under these weights
// (tier-agnostic on purpose: a sparse model shrinks toward the "average model",
// not the average elite, so cherry-picked sparse data cannot coast). Null when
// no bench has data (caller then falls back to the model's own mean = no shrink).
function globalPriorMean(weights, allModels) {
  let aw = 0, ws = 0;
  for (const k of BENCH_KEYS) {
    const w = weights[k];
    if (!w || isVendorComposite(k)) continue;
    const med = globalBenchMedian(k, allModels);
    if (med == null) continue;
    aw += w; ws += w * med;
  }
  return aw ? ws / aw : null;
}

// EB shrinkage toward priorMean + nonlinear low-confidence penalty. The penalty
// is ZERO while confidence ≥ confThreshold (a model missing a couple of benches
// is unpenalized) and grows quadratically below it (genuinely sparse models are
// pulled down). See getCompositePolicy().eb.
function ebTransform(realMean, observedWeight, activeWeight, priorMean, ebCfg) {
  const pm = (priorMean != null && Number.isFinite(priorMean)) ? priorMean : realMean;
  const eb = (observedWeight * realMean + ebCfg.priorWeight * pm) / (observedWeight + ebCfg.priorWeight);
  const confidence = activeWeight > 0 ? observedWeight / activeWeight : 0;
  const deficit = Math.max(0, (ebCfg.confThreshold - confidence) / ebCfg.confThreshold);
  return Math.max(0, eb - ebCfg.sigmaPenaltyMax * deficit * deficit);
}

// Composite score with peer-tier imputation for missing cells.
// F1+F2 (2026-05-18): atomic-only contract + respects preset.imputableBenches
// (only imputable keys get filled) + caps imputed share via policy.maxImputedWeightShare.
// Returns { score, imputedKeys } where imputedKeys lists which bench keys
// were imputed (so UI can show the "estimated" badge).
export function compositeScoreImputed(model, weights, allModels, presetName) {
  const policy = getCompositePolicy();
  const tiers = getPresetTiers(presetName || State.activePresetName || 'balanced');
  const expo = policy.coverageShrinkageExponent > 0 ? policy.coverageShrinkageExponent : 2;
  const quarantined = quarantinedBenches(model);
  let observedWeight = 0, activeWeight = 0, weightedSum = 0;
  const imputedKeys = [];
  for (const k of BENCH_KEYS) {
    const w = weights[k];
    if (!w || isVendorComposite(k)) continue;   // atomic-only (no double-count)
    activeWeight += w;
    // Quarantined cells (merge.py flagged: single-source / dispersed / low
    // confidence) are untrusted — treated as missing so EB shrinks them toward
    // the baseline instead of distorting the mean at full weight.
    const raw = quarantined.has(k) ? null : model.bench?.[k];
    const s = (raw != null && Number.isFinite(raw)) ? normalizeBenchScore(k, raw) : null;
    if (s != null && Number.isFinite(s)) {
      observedWeight += w;
      weightedSum += w * s;
    } else if (tiers.imputable.has(k)) {
      imputedKeys.push(k);   // surfaced as "estimated" in UI; EB supplies the value
    }
  }
  if (activeWeight === 0 || observedWeight === 0) return { score: null, imputedKeys };
  const realMean = weightedSum / observedWeight;
  const score = policy.eb.enabled
    ? ebTransform(realMean, observedWeight, activeWeight, globalPriorMean(weights, allModels), policy.eb)
    : realMean * Math.pow(observedWeight / activeWeight, 1 / expo);
  return { score, imputedKeys };
}

// CI-overlap rank-band engine (AA/LMArena-inspired, 2026-05-27). Propagates an
// EPISTEMIC uncertainty (sigma) for the composite from per-cell evidence quality
// (cellConfidence + contradiction spread + imputation) through the SAME
// weighted-mean × coverage^(1/expo) formula compositeScoreImputed uses, so the
// returned `score` matches effectiveScore exactly. Confidence widens the band
// but does not move the point score (parity with compositeScoreImputed, which
// weights observed cells at full w). NOT a frequentist 95% CI — band labelled
// "uncertainty range"; hasCI flags whether enough distinct sources back it.
// Constants: _schema.composite.uncertainty (getCompositePolicy().uncertainty).
export function compositeUncertainty(model, weights, allModels, presetName) {
  const policy = getCompositePolicy();
  const u = policy.uncertainty;
  const expo = policy.coverageShrinkageExponent > 0 ? policy.coverageShrinkageExponent : 2;
  const quarantined = quarantinedBenches(model);
  let observedWeight = 0, activeWeight = 0, weightedSum = 0;
  let varAccum = 0, coveredCells = 0, sourcedCells = 0;
  for (const k of BENCH_KEYS) {
    const w = weights[k];
    if (!w) continue;
    if (isVendorComposite(k)) continue;       // atomic-only (no double-count)
    activeWeight += w;
    const raw = quarantined.has(k) ? null : model.bench?.[k];
    const s = (raw != null && Number.isFinite(raw)) ? normalizeBenchScore(k, raw) : null;
    if (s == null || !Number.isFinite(s)) continue;
    const conf = cellConfidence(model.id, k);
    const sConf = u.sigmaMax * (1 - conf);
    const c = contradictionFor(model.id, k);
    const sContra = (c && Number.isFinite(c.delta)) ? (c.delta / u.contraDivisor) : 0;
    const sigmaCell = Math.sqrt(sConf * sConf + sContra * sContra);
    const entries = State.sources[`${model.id}.${k}`];
    if (Array.isArray(entries)) {
      const urls = new Set(entries.filter(e => e && e.url).map(e => String(e.url).toLowerCase()));
      if (urls.size >= u.minSourcesForCI) sourcedCells++;
    }
    observedWeight += w;            // parity with compositeScoreImputed (full w)
    weightedSum += w * s;
    varAccum += (w * w) * (sigmaCell * sigmaCell);
    coveredCells++;
  }
  if (activeWeight === 0 || observedWeight === 0) {
    return { score: null, sigma: null, lower: null, upper: null, hasCI: false, coverage: 0, imputedShare: 0 };
  }
  const realMean = weightedSum / observedWeight;
  const coverage = observedWeight / activeWeight;
  // EB point score — IDENTICAL formula to compositeScoreImputed so rank bands
  // sort on the same number the table renders.
  const score = policy.eb.enabled
    ? ebTransform(realMean, observedWeight, activeWeight, globalPriorMean(weights, allModels), policy.eb)
    : realMean * Math.pow(coverage, 1 / expo);
  const sigmaMean = Math.sqrt(varAccum) / observedWeight;          // SD of the observed weighted mean
  const sigmaSparsity = score * u.sparsityAlpha * (1 - coverage);  // missing-profile epistemic width
  const sigma = Math.sqrt(sigmaMean * sigmaMean + sigmaSparsity * sigmaSparsity);
  const half = u.bandMult * sigma;
  return {
    score,
    sigma,
    lower: Math.max(0, score - half),
    upper: Math.min(100, score + half),
    hasCI: coveredCells > 0 && sourcedCells >= Math.ceil(coveredCells / 2),
    coverage,
    imputedShare: 0,
  };
}

// Assign CI-overlap rank bands across `models` for the active preset.
// rank(M) = 1 + |{ N : N.lower > M.upper }| (LMArena rule): models whose
// uncertainty bands overlap share a rank, so within-noise differences are not
// shown as strict ordering. Returns entries sorted by point score desc with
// { id, score, sigma, lower, upper, hasCI, coverage, imputedShare, rank,
//   tied } where `tied` = another model shares this rank.
export function rankBands(models, weights, presetName) {
  const byId = new Map((models || []).map(m => [m.id, m]));
  const rows = (models || [])
    .filter(m => (m.status || 'active') !== 'archived')
    .map(m => ({ id: m.id, ...compositeUncertainty(m, weights, State.models, presetName) }))
    .filter(r => r.score != null);
  // Rank gate (2026-06-07): stamp each row's gate status (missing a required
  // bench for this preset, or below the coverage floor), then sort GATED rows
  // into a contiguous block at the bottom. The gate is the PRIMARY sort key;
  // score is secondary within each group. This is what keeps a sparse-but-
  // extreme model (EB-shrunk into the top) out of the main leaderboard.
  for (const r of rows) {
    const m = byId.get(r.id);
    r.gate = m ? rankGateStatus(m, presetName, r.coverage) : { gated: false, reason: null };
    r.gated = r.gate.gated;
  }
  rows.sort((a, b) => {
    if (a.gated !== b.gated) return a.gated ? 1 : -1;   // gated → bottom
    return b.score - a.score;
  });
  // Granular ordinal rank (1..N) keeps the table discriminating + familiar; the
  // ±σ band on each score carries the honesty (overlapping bands = close). A
  // `cluster` id increments only at a SIGNIFICANCE BREAK — where a model's
  // uncertainty band no longer overlaps the current cluster leader's band
  // (upper < leaderLower) — so the UI can draw a divider between statistically
  // distinct groups WITHOUT collapsing ranks into opaque tiers. The gate
  // boundary (ranked → gated) is ALWAYS forced to a new cluster so the UI can
  // draw the "Limited Coverage" band divider there.
  let cluster = 0;
  let leaderLower = Infinity;
  let prevGated = null;
  rows.forEach((r, i) => {
    r.rank = i + 1;
    const gateBoundary = prevGated !== null && r.gated !== prevGated;
    if (gateBoundary || r.upper < leaderLower) {
      cluster += 1;
      r.cluster = cluster;
      leaderLower = r.lower;
    } else {
      r.cluster = cluster;
    }
    prevGated = r.gated;
  });
  return rows;
}

export function isLocalRunnable(m) {
  if (m.tier === 'ollama-local' || m.tier === 'gemma') return true;
  if (Number.isFinite(m.vramRequirement)) return true;
  if (Array.isArray(m.unslothVariants) && m.unslothVariants.length > 0) return true;
  return false;
}
