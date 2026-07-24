# AICoderMap Scoring Methodology

**Version 1.0 — 2026-07-15.** This document is the published, versioned reference
for how AICoderMap turns raw benchmark evidence into the ranking on the site.
Any change to a formula, threshold, or weight vector bumps this version and is
recorded in CHANGELOG.md. (Field precedent: Artificial Analysis publishes and
versions its Intelligence Index weights; we hold ourselves to the same bar.)

## 1. Data model

- **Atomic benches** (SWE-bench Pro, LiveCodeBench, τ²-Bench, GPQA, …) are
  primary measurements. Only these enter the composite.
- **Vendor composites** (AA Index, AA Coding, AA Agentic, AA Omniscience) are
  themselves aggregates of atomic benches. They are **excluded** from our
  composite (double-counting) and surface separately in the per-model
  "Vendor View" panel and the cross-validation flag (§7).
- Every `(model, bench)` cell carries provenance in `data/sources.json`:
  source URL, tier, trustScore, fetch date. Target: **≥2 independent sources
  per cell**; single-source or high-dispersion cells are quarantined (§6).

## 2. Normalization

Heterogeneous scales (percentages, Elo, inverse ranks) are mapped to a common
0–100 scale per bench via schema-driven rules in
`data/sources-whitelist.json → _schema.normalization` (piecewise for Elo-like
scales, linear for percentages, inverted for lower-is-better metrics).
There is no single universally-correct normalization for heterogeneous
benchmarks (min-max is outlier-sensitive; z-scores penalize models measured
only on harder subsets — see arXiv 2509.22472); per-bench-type rules with
explicit directionality correction are the defensible middle ground, so that
is what we use, and each rule is data (reviewable, versioned), not code.

## 3. Composite score (empirical-Bayes path — the default)

For a model with observed normalized scores `s_k` and preset weights `w_k`:

```
realMean       = Σ(w_k · s_k) / Σ(w_k)            over observed cells
priorMean      = Σ(w_k · median_k) / Σ(w_k)       global per-bench medians
eb             = (W_obs · realMean + P · priorMean) / (W_obs + P)
confidence     = W_obs / W_active
deficit        = max(0, (T − confidence) / T)
score          = max(0, eb − S · deficit²)
```

with `P = priorWeight` (default 30), `T = confThreshold` (default 0.65),
`S = sigmaPenaltyMax` (default 18) — all in
`sources-whitelist.json → _schema.composite.eb`.

**Why shrinkage instead of a raw coverage haircut:** small-sample estimates
produce false extremes; shrinking toward the population mean is the
century-tested fix (James-Stein / Efron-Morris; regularized estimators
outperform MLE in small-data regimes — arXiv 1807.09236). The prior is the
**global median profile**, deliberately tier-agnostic: a sparse model shrinks
toward the *average* model, not the average frontier model, so cherry-picked
sparse results cannot coast to the top.

**Disclosed imputation:** no surveyed T1 leaderboard silently imputes missing
scores (LMArena tags low-vote models "Preliminary"; LLM-Stats flags unverified
scores and excludes them from composites). We keep EB fill — it is
statistically stronger than dropping cells — but every imputed bench is
labeled **"estimated"** directly on the score block, and only benches the
active preset declares `imputable` may be filled, capped by
`maxImputedWeightShare` (default 0.30).

## 4. Rank gate and Preliminary status

EB alone would let a sparse model missing its preset's heaviest **required**
bench float on a few extreme scores elsewhere. That risk is real only when the
model is *also* thin on overall evidence — a well-covered model missing one
required bench (e.g. a vendor that genuinely never published that one metric)
isn't gaming anything. So the gate is coverage-aware (2026-07-16):

- Coverage below `rankGate.coverageFloor` (default 0.40) → **gated**,
  regardless of which benches are missing.
- Missing any `requiredBenches` of the active preset **and** coverage below
  `rankGate.missingRequiredCoverageFloor` (default 0.50) → **gated**.
- Missing a required bench but coverage at or above that floor → **not**
  gated on that basis alone; the model ranks normally on its EB-shrunk score,
  with a ⚠N marker on the card still listing what is missing.
- Gated → demoted into the contiguous "Limited Coverage" band below the main
  ranking (never hidden), with a ⚠N marker listing what is missing.
- Ranked normally but thin evidence (≥2 missing critical benches, or coverage
  < 50%) → **PRELIM** chip (LMArena's "Preliminary" pattern): the rank is
  real but provisional.

**New-release grace (2026-07-24).** Both gate arms measure evidence that only
*exists* weeks after a launch: `swePro` comes from Scale SEAL, `sweMulti` and
`cfElo` from independent harness runs that queue new models for days. Applied to
a model released this week, the gate stops measuring the model and starts
measuring the calendar — every fresh flagship was demoted into the Limited
Coverage band during exactly the window when readers came looking for it
(Claude Opus 5 ranked #4 on its EB score but sat in the bottom band at 39%
coverage on launch day). So inside `recency.newWindowDays` (default 30) a model
with at least `recency.graceMinCoverage` (default 0.25) real coverage ranks on
its EB-shrunk score and carries a **DATA FILLING** chip stating why. Below that
floor — a stub with nothing measured yet — the gate still applies: the grace
exempts a model from benches *nobody has published for it*, never from having
evidence at all. The flag is set only when the grace changed the verdict.

## 5. Uncertainty bands

Every composite ships with an epistemic ±σ band
(`compositeUncertainty` in `assets/js/scoring.js`):

- per-cell σ from evidence quality (`cellConfidence`) and contradiction
  spread, propagated through the same weighted mean;
- a sparsity term `score · α · (1 − coverage)`;
- displayed as `±x.x` next to the score. Models whose bands overlap are
  **statistically indistinguishable** — the cluster divider in the table marks
  significance breaks (`upper < leaderLower`), the same CI-overlap rule
  LMArena uses for its rank column and Epoch AI's ±1 SE error bars express.
  The band is epistemic (evidence quality), not a frequentist 95% CI, and the
  UI labels it "uncertainty range" accordingly.

## 6. Evidence discipline (provenance, contradictions, quarantine)

- **≥2 independent sources** per filled cell is the target contract
  (`MIN_SOURCES_PER_FILLED_CELL: 2`).
- Cross-source delta **> 3pp raises ⚠** (contradiction flag on the cell),
  **> 5pp raises 🚨** (release-blocking review).
- `merge.py` quarantines cells that are single-source, high-dispersion, or
  low-confidence; quarantined cells are treated as missing by the composite
  (EB shrinks them toward the median instead of trusting them at full weight).
- **Exceptional-source override (reliability, not count):** a single-source
  cell is not automatically quarantined for low confidence when the sole
  source has an earned Beta-Binomial track record on the reliability ledger.
  I-tier (independent leaderboard) singletons need ≥20 prior samples,
  posterior accuracy ≥0.90, and recency ≥0.85 (≲90 days old). S-tier
  (vendor self-report) singletons face a materially stricter bar — ≥40
  samples, posterior ≥0.97, recency ≥0.90 — because self-reports carry
  inflation/cherry-picking risk independent leaderboards don't.
  (`scripts/lib/winner.py::should_quarantine`, `_exceptional_source_override`.)
- **Earned-trust provisional admission (2026-07-24).** Those override
  thresholds are counted in *decay-weighted* units, where the highest vendor
  figure in the entire ledger is `anthropic.com × tb2 = 8.37` — so the S-tier
  ladder could never fire for any vendor on any bench, and in practice every
  launch-day official number fell into the confidence floor. That is blanket
  caution, not earned caution, and the ledger's own record contradicts it:
  `anthropic.com` is 97/97 agree, `deepmind.google` 228/228, while the real
  misses are bench-specific (`openai.com × cfElo` 0/6, `× hle` 3/3). A second
  ladder therefore judges a vendor on its **raw record for that specific
  bench**: ≥20 raw prior observations with posterior ≥0.90, falling back to the
  vendor's global record (≥40 raw) only when the bench itself has no
  disagreement history, plus the same freshness requirement. Raw rather than
  weighted counts, because decay measures current *influence* and collapses the
  posterior for small-but-perfect records (23/0 on swePro → 0.886 weighted vs
  0.960 raw). Clearing it does not make the cell verified — it marks it
  **provisional**: the value counts toward the composite at the reduced
  confidence a single source already earns, and carries a ⓥ "vendor-reported,
  awaiting independent verification" badge that clears the moment an
  independent source corroborates it. A vendor caught wrong on that bench is
  still refused, so caution stays targeted at demonstrated inaccuracy rather
  than at officialdom in general.
  (`scripts/lib/winner.py::s_tier_earned_trust`, `merge.py` stamps
  `model.benchProvisional`.)
- Source trustScores decay via the reliability ledger
  (`data/source-reliability.json`) when a source's values keep losing
  contradiction resolutions.
- **Benchmark staleness** (v1.0, G5): each bench carries a `benchType` in
  `sources-whitelist.json → _schema.benchTypes` — `rotating` (LiveBench-style
  pool refresh), `temporal` (LiveCodeBench-style cutoff filtering), or
  `static` (frozen split). Static splits accumulate contamination risk as
  they age (the 2026 SWE-bench Verified controversy is the canonical
  example). The taxonomy is disclosed as a chip in the site glossary and is
  a standing input to preset weight retunes (sweV's demotion to weight 9 is
  the precedent); it is deliberately *not* a trustScore multiplier, because
  all sources of one cell share the bench and a flat per-bench factor cannot
  change winner selection within that cell.

## 7. Cross-validation against vendor consensus

Because our composite deliberately excludes vendor aggregates, they form an
independent second opinion. Per model we compute a vendor-consensus rank
(coverage-shrunk mean of normalized vendor composites) and compare:

| rank gap | flag |
|---|---|
| ≤ 5 | 🟢 consensus |
| ≤ 15 | 🟡 mild disagreement |
| > 15 | 🔴 controversy |

A 🔴 does not mean we are wrong — it means *look at the provenance footer
before trusting either number*.

## 8. Presets and weights

Preset weight vectors live in `data/sources-whitelist.json → _schema.presets`
(schema-driven; `assets/js/core.js` carries fallback literals). Each sums
to 100. Rationale follows **swing-weighting** logic (rank criteria by
importance for the persona, then assign relative swings) — chosen over AHP
because AHP's O(n²) pairwise matrix is infeasible for 25+ criteria in a
slider UI, and comparative MCDA studies find no consistent output-quality
winner between the two (Pöyhönen et al.).

| Preset | Anchor rationale (2026-05-18 retune, 2026-05-28 rebalance) |
|---|---|
| **swe-focused** (default) | SWE-bench Pro 32 (contamination-resistant gold standard) + TB2 17 + SWE-Multilingual 14 + LCB 13; sweV demoted to 9 (saturated, <1.3pp frontier spread + 2026 contamination findings) |
| **agentic-focused** | τ²-Bench 21 (top multi-turn reliability) + TB2 18 + MCP-Atlas 17 + browsing/tool-use |
| **reasoning-focused** | HLE 27 (non-saturated frontier) + GPQA 16 + AIME 13 + ARC-AGI-2 9 |
| **balanced** | The site-wide default blend across coding/agentic/reasoning |
| **benchmark-only** | Spread over every active bench, skewed to ≥70%-coverage benches to limit coverage-penalty distortion |
| **consensus** | No atomic weights — pure vendor-composite median as an honest second opinion |

Weights are user-editable; the published vectors are our editorial defaults,
not ground truth. **No surveyed competitor (16 products, 2026-07) offers
user-adjustable weights — this is AICoderMap's differentiator, kept.**

## 9. Known limitations

- We aggregate published numbers; we do not run benchmarks ourselves
  ($0-infrastructure constraint). Provenance tiering is the mitigation.
- Amber/orange/red status tiers cannot clear CVD ΔE floors between
  themselves; every status therefore ships with an icon + label, never
  color alone.
- The ±σ band is epistemic (evidence quality), not a sampling CI.
- Coverage currently ~69% of the active cell matrix vs the 85% target;
  gap cells are re-queried every refresh cycle and never silently skipped.

## References

- Chatbot Arena / Bradley-Terry + bootstrap CIs: arXiv 2403.04132; lmsys.org blog 2023-12-07
- Empirical-Bayes shrinkage: arXiv 1807.09236; Efron & Morris (1977)
- Epoch AI repeat-run ±1 SE methodology: epoch.ai/benchmarks/about
- Normalization pitfalls across heterogeneous benchmarks: arXiv 2509.22472
- Swing weighting vs AHP in MCDA: Pöyhönen et al.; INCOSE swing-weight matrix
- Contamination and rotating benchmarks: LiveBench (ICLR 2025); LiveCodeBench release-date filtering; SWE-rebench post-cutoff sourcing
- Weight renormalization for missing components in composite indexes: arXiv 2604.12368
- Research artifacts backing this document: `ds/research/competitors-part{1,2}.json`, `ds/research/methodology.json`
