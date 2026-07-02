// Data layer: HTTP fetch + evidence quality (provenance, reliability,
// freshness, contradiction, per-cell confidence). Pure scoring math lives in
// scoring.js; display formatters live in format.js.

import {
  State, BENCH_KEYS, getContradictionThresholds, validateModels, cacheBustUrl,
} from './core.js';

// Resolve data URLs against this module's location so loadData() works whether
// the caller is index.html (project root) or assets/test/smoke.html (deeper).
// import.meta.url here = .../assets/js/data.js, so '../../data/' lands at
// .../data/.
const DATA_BASE = new URL('../../data/', import.meta.url);

export async function fetchJson(name) {
  const url = cacheBustUrl(name, DATA_BASE);
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
  // PERF (2026-06-10): sources.json (~2MB) no longer blocks first render.
  // It loads in the background; State.sourcesReady resolves once parsed and
  // main.js re-renders so provenance counts / contradiction flags / per-cell
  // confidence appear the moment they're available. Until then State.sources
  // is empty, which every consumer already treats as "no provenance yet"
  // (cellConfidence → 1.0 neutral, contradictionFor → null).
  State.sources = {};
  State.sourcesReady = fetchJson('sources.json')
    .then((sources) => {
      State.sources = (sources && typeof sources === 'object') ? sources : {};
      return State.sources;
    })
    .catch((e) => {
      console.warn('sources.json load failed — provenance detail unavailable', e);
      return State.sources;
    });
  const [models, gpu, meta, reliability, whitelist] = await Promise.all([
    fetchJson('models.json'),
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
  // Serving-speed variants (byte-for-byte identical weights + precision to a
  // base model, e.g. kimi-k2-7-code-highspeed) carry NO independent bench
  // measurements in storage (SSOT). Their benchmark QUALITY scores are the
  // base's by construction, so mirror them at load. State.benchMirror lets
  // cellConfidence()/contradiction lookups redirect to the base id so a mirror
  // scores identically to its base instead of falling back to the neutral
  // no-provenance confidence. matrix.active_models excludes them from research.
  State.benchMirror = {};
  {
    const byId = new Map(State.models.map((m) => [m.id, m]));
    for (const m of State.models) {
      const baseId = m.benchMirrorOf;
      if (!baseId) continue;
      const base = byId.get(baseId);
      if (!base || !base.bench || typeof base.bench !== 'object') continue;
      m.bench = { ...base.bench };
      if (m.benchUpdated == null && base.benchUpdated) m.benchUpdated = base.benchUpdated;
      m.benchMirroredFrom = baseId;
      State.benchMirror[m.id] = baseId;
    }
  }
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
  // A bench-mirror (serving-speed variant) has no provenance under its own id;
  // resolve to the base model so it inherits the base's confidence + any
  // contradiction penalty rather than defaulting to neutral 1.0.
  const realId = (State.benchMirror && State.benchMirror[modelId]) || modelId;
  const entries = State.sources[`${realId}.${benchKey}`];
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
  const c = contradictionFor(realId, benchKey);
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
