// Scoring layer: weighted composite, Empirical-Bayes shrinkage, vendor
// composite cross-validation, rank gate and CI-overlap rank bands. Evidence
// quality (per-cell confidence, contradictions) comes from data.js; display
// formatting lives in format.js.

import {
  State, BENCH_KEYS, normalizeBenchScore, isVendorComposite,
  getVendorCompositeMeta, getCompositePolicy, getPresetTiers,
  getRecencyPolicy, isRecentRelease,
  DEFAULT_PRESET, DEFAULT_SCORE_FN,
} from './core.js';

// Coverage-shrinkage exponent with the shared >0 guard (default 2 = sqrt).
// Was inlined at 4 call sites with drifting guard strictness.
function shrinkExponent(policy) {
  const e = policy.coverageShrinkageExponent;
  return (Number.isFinite(e) && e > 0) ? e : 2;
}
import { cellConfidence, contradictionFor, quarantinedBenches } from './data.js';

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
  const expo = shrinkExponent(policy);
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
  const expo = shrinkExponent(policy);
  return raw * Math.pow(coverage, 1 / expo);
}

// PERF (2026-06-10): full-dataset AICM + consensus rankings are memoized per
// (models identity+size, weights, preset) so crossValidationAgreement is O(1)
// per card instead of two full map+sort passes — previously O(N²) scoring work
// per render cycle when called once per rendered card.
let _xvalCache = { token: null, size: 0, key: '', aicm: null, cons: null };

function xvalRankings(allModels, weights, presetName) {
  const key = `${presetName || ''}|${BENCH_KEYS.map(k => weights[k] || 0).join(',')}`;
  if (_xvalCache.token !== allModels || _xvalCache.size !== allModels.length || _xvalCache.key !== key) {
    const aicm = new Map();
    const cons = new Map();
    allModels
      .map(m => ({ id: m.id, s: compositeScore(m, weights) }))
      .filter(x => x.s != null)
      .sort((a, b) => b.s - a.s)
      .forEach((x, i) => aicm.set(x.id, i + 1));
    allModels
      .map(m => ({ id: m.id, s: vendorConsensusScore(m, presetName) }))
      .filter(x => x.s != null)
      .sort((a, b) => b.s - a.s)
      .forEach((x, i) => cons.set(x.id, i + 1));
    _xvalCache = { token: allModels, size: allModels.length, key, aicm, cons };
  }
  return _xvalCache;
}

// Agreement indicator between AICoderMap composite rank and vendor consensus
// rank for `model`, computed across `allModels`. Returns:
//   { aicmRank, consensusRank, gap, flag }
// flag ∈ {'consensus','mild-disagreement','controversy'} mapped from gap ≤5, ≤15, >15.
// Returns null if either rank cannot be computed.
export function crossValidationAgreement(model, allModels, weights, presetName) {
  if (!Array.isArray(allModels) || !allModels.length) return null;
  const { aicm, cons } = xvalRankings(allModels, weights, presetName);
  const aicmRank = aicm.get(model.id);
  const consRank = cons.get(model.id);
  if (!aicmRank || !consRank) return null;
  const gap = Math.abs(aicmRank - consRank);
  let flag;
  if (gap <= 5) flag = 'consensus';
  else if (gap <= 15) flag = 'mild-disagreement';
  else flag = 'controversy';
  return { aicmRank, consensusRank: consRank, gap, flag };
}

// Score resolver — dispatches to the right scoring function based on
// State.scoreFn (set by applyPreset). UI consumers (render-table /
// render-card) can call this single helper instead of branching on
// preset kind. Returns null when score cannot be computed.
// F1+F2 (2026-05-18): when policy.imputationEnabled, AICM path uses
// compositeScoreImputed (EB shrinkage for missing imputable cells,
// capped by maxImputedWeightShare). Vendor consensus path unaffected.
export function effectiveScore(model, weights, presetName) {
  const fn = State.scoreFn || DEFAULT_SCORE_FN;
  if (fn === 'vendorConsensus') return vendorConsensusScore(model, presetName || State.activePresetName);
  const policy = getCompositePolicy();
  if (policy.imputationEnabled) {
    const out = compositeScoreImputed(model, weights, State.models, presetName);
    return out.score;
  }
  return compositeScore(model, weights);
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
//
// Coverage-aware missing-required (2026-07-16): that gaming risk only applies
// when the model is ALSO sparse overall — a handful of real cells plus EB fill
// on the rest. A model with solid coverage (>= missingRequiredCoverageFloor)
// missing just one required bench isn't gaming anything (e.g. a vendor that
// genuinely never published that one metric at launch) — it competes on its
// EB-shrunk score instead of being hidden in the bottom band. Below that floor,
// missing-required still gates regardless of which specific bench is absent.
//
// New-release grace (2026-07-24): both gate arms measure evidence that only
// EXISTS weeks after a launch — swePro comes from Scale SEAL, sweMulti/cfElo
// from independent harness runs. Applying them to a model released days ago
// doesn't measure gaming, it measures the calendar, and it buried every fresh
// flagship in the bottom band precisely when users came looking for it. Inside
// `newWindowDays` a model with at least `graceMinCoverage` real coverage ranks
// on its EB-shrunk score, flagged `newGrace` so the UI can say "new — data
// still filling" instead of silently promoting thin evidence. A stub with
// nothing measured yet still fails the floor and stays in the band. The flag is
// only set when the grace CHANGED the verdict — a fresh model that clears the
// gate on its own merits is not labelled as needing an exemption.
export function rankGateStatus(model, presetName, coverage) {
  const gate = getCompositePolicy().rankGate;
  if (!gate.enabled) return { gated: false, reason: null };
  let reason = null;
  if (gate.demoteMissingRequired) {
    const tiers = presetTiersFor(model, presetName);
    const belowMissingRequiredFloor = !Number.isFinite(coverage) || coverage < gate.missingRequiredCoverageFloor;
    if (tiers.missingRequired.length > 0 && belowMissingRequiredFloor) {
      reason = 'missing-required';
    }
  }
  if (!reason && Number.isFinite(coverage) && coverage < gate.coverageFloor) {
    reason = 'low-coverage';
  }
  if (!reason) return { gated: false, reason: null };
  if (
    isRecentRelease(model)
    && Number.isFinite(coverage)
    && coverage >= getRecencyPolicy().graceMinCoverage
  ) {
    return { gated: false, reason: null, newGrace: true };
  }
  return { gated: true, reason };
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

// Per-bench global median cache. Keyed by the allModels array identity AND
// length: medians depend only on bench values (not weights), so identity is the
// correct invalidation signal — the length guard additionally catches in-place
// mutation (push) that identity alone would miss.
let _priorMedianCache = { token: null, size: 0, byKey: new Map() };

function globalBenchMedian(key, allModels) {
  const size = (allModels || []).length;
  if (_priorMedianCache.token !== allModels || _priorMedianCache.size !== size) {
    _priorMedianCache = { token: allModels, size, byKey: new Map() };
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

// Composite score with EB shrinkage for missing cells.
// F1+F2 (2026-05-18): atomic-only contract + respects preset.imputableBenches
// (only imputable keys get filled) + caps imputed share via policy.maxImputedWeightShare.
// Returns { score, imputedKeys } where imputedKeys lists which bench keys
// were imputed (so UI can show the "estimated" badge).
export function compositeScoreImputed(model, weights, allModels, presetName) {
  const policy = getCompositePolicy();
  const tiers = getPresetTiers(presetName || State.activePresetName || DEFAULT_PRESET);
  const expo = shrinkExponent(policy);
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
  const expo = shrinkExponent(policy);
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

// Rank gate (2026-06-07): stamp each row's gate status (missing a required
// bench for this preset, or below the coverage floor). The gate is the PRIMARY
// sort key; score is secondary within each group. This is what keeps a sparse-
// but-extreme model (EB-shrunk into the top) out of the main leaderboard.
function stampGateStatus(rows, byId, presetName) {
  for (const r of rows) {
    const m = byId.get(r.id);
    r.gate = m ? rankGateStatus(m, presetName, r.coverage) : { gated: false, reason: null };
    r.gated = r.gate.gated;
    r.newGrace = !!r.gate.newGrace;
  }
}

// Granular ordinal rank (1..N) keeps the table discriminating + familiar; the
// ±σ band on each score carries the honesty (overlapping bands = close). A
// `cluster` id increments only at a SIGNIFICANCE BREAK — where a model's
// uncertainty band no longer overlaps the current cluster leader's band
// (upper < leaderLower) — so the UI can draw a divider between statistically
// distinct groups WITHOUT collapsing ranks into opaque tiers. The gate
// boundary (ranked → gated) is ALWAYS forced to a new cluster so the UI can
// draw the "Limited Coverage" band divider there.
function assignRanksAndClusters(rows) {
  let cluster = 0;
  let leaderLower = Infinity;
  let prevGated = null;
  rows.forEach((r, i) => {
    r.rank = i + 1;
    const gateBoundary = prevGated !== null && r.gated !== prevGated;
    if (gateBoundary || r.upper < leaderLower) {
      cluster += 1;
      leaderLower = r.lower;
    }
    r.cluster = cluster;
    prevGated = r.gated;
  });
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
  stampGateStatus(rows, byId, presetName);
  rows.sort((a, b) => {
    if (a.gated !== b.gated) return a.gated ? 1 : -1;   // gated → bottom
    return b.score - a.score;
  });
  assignRanksAndClusters(rows);
  return rows;
}
