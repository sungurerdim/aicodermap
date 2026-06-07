---
description: "AICoderMap update orchestrator. Project-scoped. Manual trigger, zero API cost."
argument-hint: "[refresh-all|model <id>|new-release|validate|stale-check|changelog|lineup-sync]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, TaskCreate, TaskUpdate
---

# aicodermap

## ROLE
Orchestrate AI coding LLM tracker updates: discover **official vendor lineup** → reconcile current data → invoke `aicodermap-research-agent` (lineup-driven, trusted-source whitelist, parallel) → auto-resolve contradictions via `trustScore` → atomic schema-complete merge → atomic write `data/*.json` + `i18n/*.json` + `CHANGELOG.md` → prompt git commit → verify GitHub Pages deploy.

**Autonomy principle (HARD DEFAULT — non-negotiable):** the skill NEVER pauses for user input on data-quality decisions. Missing data, weak coverage, contradicted scores, unreachable sources, partial vendor reachability — none of these are deal-breakers. Every uncertainty path resolves to: **iterate → retry → fall back to alternate source → emit `gaps[]` entry → CONTINUE writing/committing/pushing**. The only halts are: (a) git push conflict (user must resolve via `git pull --rebase`), (b) full schema-breaking discovery never seen before. All other "halt" cases in prior versions of this spec are now "log warning + continue".

## CONTEXT
- Project root: `D:\GitHub\aicodermap\`
- Agent: `.claude/agents/aicodermap-research-agent.md`
- Data files: `data/{models,sources,gpu-database,sources-whitelist}.json`
- i18n: `i18n/{tr,en}.json`
- Live URL: `https://sungurerdim.github.io/aicodermap/`
- **No skip registry** — every (modelId, benchKey) pair is re-attempted on every refresh. If a vendor previously opt-out and later submits to a leaderboard, the next refresh will catch it without manual registry updates.
- **Sources whitelist:** `data/sources-whitelist.json` — single source of truth for every URL the research agent is allowed to fetch. Skill loads this and injects it into `idea_context.sourcesWhitelist` for every agent run. Agent NEVER hardcodes URLs.

## ARGS
| arg | scope | model | typical_duration |
|-----|-------|-------|------------------|
| (none) | interactive prompt | — | — |
| `refresh-all` | full (lineup + bench + pricing + local) | sonnet | 20-60min (N waves × batches, all sonnet gather; per-batch wallclock 5-15min) |
| `lineup-sync` | vendor lineup discovery only (Step 0) | sonnet | 3-6min (single batch, vendors in parallel) |
| `model <id>` | specific | sonnet | 3-8min (single-batch, single-model deep sweep) |
| `new-release` | new-release detection | sonnet | 4-10min |
| `validate` | (no fetch) | — | <10s |
| `stale-check` | (no fetch) | — | <5s |
| `changelog` | (no fetch) | — | <5s |

**`refresh-all` baseline:** Agent's `MODEL_FAMILIES` table is non-negotiable — every family must be surveyed, missing ones emit a `gaps[]` entry. Skill rejects returns whose `models[]` + `newModels[]` cardinality < 30 unless agent explains via `gaps[]`.

## WORKFLOW
```
PRELIM. SOURCE_HEALTH_CHECK (auto, every refresh — now format-aware):
   - **PRIMARY (2.6):** the deterministic `scripts/source-health-probe.py` in PRELIM-B
     now performs this check across ALL categories in one urllib pass and refreshes
     `_runtime.healthChecks`. The agent-based sample below is the FALLBACK used only
     when that script cannot run. Format-drift auto-demote logic still applies to
     whichever source produced the observedFormat.
   - Skill instructs agent to run quick HEAD/GET probes on a 3-URL sample of leaderboards[]
   - Agent reports for each probe: `runtime.healthChecks[<domain>]: { status: 'ok'|'unhealthy:<reason>', observedFormat: <format-key> }`
   - **Format consistency check:** if `entry.format` says `static_html_table` but `observedFormat` says `spa_full` (or vice versa), increment `entry.consecutiveFailures`. After 3 consecutive cycles of the same drift, auto-demote `entry.format` to the observed value (e.g., `static_*` → `spa_full`). This is self-healing format classification — the agent does not need a manual whitelist edit when a vendor migrates a leaderboard from server-rendered to SPA.
   - Skill writes results to data/sources-whitelist.json `_runtime.healthChecks` block AND updates per-entry `format` + `format_lastVerified` when drift is confirmed
   - Persistent-unhealthy domains (≥3 cycles consecutive) get `_runtime.unhealthy: true` — agent skips them in this cycle's Phase 1 until next health-check passes
   - This step prevents wasted fetch budget on guaranteed-SPA/403 URLs AND keeps the whitelist's format classification accurate without human intervention

PRELIM-B. SOURCE_HEALTH_PROBE + LEADERBOARD_PREFETCH (orchestrator-side single-pass):
   ```
   python scripts/source-health-probe.py        # 2.6: probe ALL categories, refresh healthChecks
   python scripts/prefetch-leaderboards.py --max 12
   ```
   - **2.6 SOURCE_HEALTH_PROBE (deterministic, supersedes the agent 3-URL sample):**
     `source-health-probe.py` fetches EVERY whitelist category in ONE stdlib-urllib
     pass — vendors (lineup + news), leaderboards, aggregators, local, registries,
     complianceAggregators, community — classifies each URL's OBSERVED format, and
     refreshes `_runtime.healthChecks[<domain>]` + `_runtime.lastFullCycle`. It
     reports the four reachability problems in one place
     (`data/_runtime-health-report.json`): `format-drift` (declared static but now
     SPA/bot/dead), `redirect` (cross-host 30x → `redirectedTo`), `spa`, `bot-block`.
     SSL-trust failures from the local cert bundle are tagged `ssl-env` and do NOT
     count as a reachability failure (environment artifact, not a dead source).
     Because it runs FIRST, the prefetch below already sees the refreshed
     healthChecks and skips drifted/dead URLs. The agent-side probe in PRELIM
     remains a fallback only if this script can't run (network/tooling outage).
     Non-fatal: a probe failure logs + CONTINUEs.
   - **What:** stdlib `urllib` HTTP-GET pass over every healthy whitelist leaderboard/aggregator/community/registries URL whose format is NOT in the FAZ 1.4 banned-list. Writes snapshots to `data/.leaderboard-snapshots/<host>__<sha8>.{html,json}` and a manifest to `data/.leaderboard-snapshots/_index.json`.
   - **Why:** the prior cycle had 18 sub-agents each running their own Phase 1 sweep, fetching ~37 leaderboards × 18 batches = ~666 duplicated WebFetches per refresh-all. This pass collapses that into ONE prefetch (~15s wallclock for 73 URLs). Each batch agent then `Read`s the snapshot from disk instead of WebFetching — saves 1 tool-call + 5–30s per leaderboard per agent.
   - **TTL:** snapshots stay fresh for 24h. Re-runs within TTL no-op (`fresh: N to-fetch: 0`). Use `--force` to ignore TTL (rare; only when whitelist URLs change).
   - **Failure tolerance:** prefetch is non-fatal. SSL/DNS/404 misses are logged in `_index.json._meta.totalFailed`; agent's Phase 1 transparently falls back to WebFetch for any URL absent from `leaderboardSnapshots` map.
   - **Output to skill:** the orchestrator reads `_index.json` and injects `idea_context.leaderboardSnapshots = { <url>: { path: "<rel>", contentType, contentLength, fetchedAt } }` into every batch dispatch (Step 3).
   - This step CANNOT be skipped on `refresh-all` and `lineup-sync`. It is opt-out via `AICODERMAP_NO_PREFETCH=1` env var only for emergency manual reruns.

PRELIM-C. STALE_ARTIFACT_PRUNE (FAZ 7.A, 2026-05-10):
   ```
   python scripts/prune-stale-artifacts.py
   ```
   - Renames prior-cycle artifacts to `<name>.stale-<epoch>` so dispatched agents cannot reuse them. Patterns: `.aicodermap-agent-out-batch*.gather.json`, `.aicodermap-agent-out-batch*-gather.json`, `.aicodermap-agent-out-synth.json`, `.aicodermap-agent-out.json`, `.aicodermap-ctx-batch*.json` (added 2026-06-06 — the dispatch plan can split providers into DIFFERENT batchIds cycle-to-cycle, so a prior-cycle ctx whose batchId is gone from the fresh plan is never overwritten and pollutes the fresh ctx glob with stale/duplicate model slices).
   - Defends against the cycle 2026-05-10 failure mode: gather/synth agents observed prior-cycle artifacts, deemed them complete, emitted EMITTED status without fresh fetches.
   - Orchestrator records `cycle_started_unix = time.time()` AFTER prune; this flows into `idea_context.cycleStartedUnix` and into gather validator's `--cycle-started-unix`.
   - **6.4 — verificationMap file-age guard.** Before computing `priorityCells`/
     `skipCells`, stat `.aicodermap-verification-map.json`. If its mtime predates
     `cycle_started_unix - STALE_DAYS×86400` (i.e. the audit log is older than one
     full refresh interval), its `confirmed` flags are no longer trustworthy — a
     long-stale map would otherwise let PRELIM-E's fast-path skip a real refresh on
     outdated "confirmed ≤7d" evidence. In that case DEGRADE every cell to Tier-1:
     pass `skip_confirmed_within_days=0` to `priority_cells(...)` so NO cell is
     skipped as confirmed, and force the full Stage A/B path (bypass the
     LINEUP_ONLY_MINI_CYCLE_GATE) this cycle. Log `⚠ verification-map stale
     (age >STALE_DAYS) — all cells re-verified T1`. Missing file → same treatment.
   - Non-fatal. Opt-out via `AICODERMAP_NO_PRUNE=1`.

PRELIM-D. SNAPSHOT_ROW_EXTRACTION (FAZ 7.F, 2026-05-10):
   ```
   python scripts/extract-snapshot-rows.py
   ```
   - Walks every `data/.leaderboard-snapshots/*.html|json`, applies the schema's regex/JSON extractors with strict bench-value heuristics (% sign required, value ∈ [5..100]), emits `data/.leaderboard-snapshots/_rows.json` with shape `{ byModel: { <id>: [{benchKey, value, sourceUrl, tier, confidence: "regex-hint", snippet}] } }`.
   - Why: each gather agent previously re-read the same raw HTML snapshot when looking for its target models. Cycle 2026-05-10 measured ~16 agents × ~75 snapshots = ~1200 redundant Read+parse operations. Pre-extraction does the parse ONCE; agents read the slim `_rows.json` (10-30 KB total).
   - **Hint quality:** `confidence: "regex-hint"` — the agent verifies any used row by Reading its sourceUrl snapshot OR by an independent fetch. Multi-bench tables can produce duplicate values across keys (e.g., a single 80.2 attributed to both swePro+sweV); the agent's row-validator (FORMAT_DISPATCH) drops these unless an independent source confirms the bench-key assignment.
   - **6.5 — `confidence: "confirmed"` fast-path:** a row from a page advertising EXACTLY ONE bench key, captured in strict mode (explicit `%` anchor), is emitted as `confirmed` (non-ambiguous: no cross-key duplication is possible). The agent MAY promote a `confirmed` row directly to `observations[]` and SKIP the re-verify fetch — it still counts as one I-tier source toward the ≥2 distinct-source requirement. `regex-hint` rows still require verification.
   - **Quality gate:** rows are NOT auto-promoted to observations[]. The agent must verify before emitting. `_rows.json` is a STARTING POINT, not a source of record.
   - Non-fatal. Opt-out via `AICODERMAP_NO_ROW_EXTRACT=1`.

PRELIM-G. AA_STRUCTURED_EXTRACT (2026-05-31) — deterministic Artificial Analysis pull:
   ```
   python scripts/extract-aa-rsc.py
   ```
   - Artificial Analysis is the single richest source for the indices that are
     otherwise systematically empty (aaCoding, aaAgentic) plus a strong I-tier
     cross-check for gpqa/hle/tau2/tbHard. It is `spa_partial`, so live WebFetch
     returns the page shell without the numbers — the 2026-05-30 cycle left 108
     aaCoding/aaAgentic gaps that had ALL reached AA. This script decodes AA's
     Next.js RSC streaming chunks (`self.__next_f`) to read the embedded
     per-model dataset directly, maps 7 high-confidence fields with correct
     scale, resolves AA slug/name → our id by exact-normalized match (ZERO
     fuzzy matching → no cross-model misattribution), and writes:
       * `data/.leaderboard-snapshots/_aa-rows.json` (agents may Read it)
       * `.aicodermap-agent-out-batch90-aa-rsc.gather.json` — a gather-schema
         artifact (real epoch startedAt) auto-discovered by local-synth +
         gen_unified's `batch*` glob, so AA flows through synth/merge exactly
         like an agent's gather output, deterministic + I-tier.
   - Why FIRST (before gather): agents read `_aa-rows.json` as confirmed I-tier
     rows; synth consumes the gather artifact. Cuts wasted AA WebFetch budget.
   - Non-fatal. Opt-out via `AICODERMAP_NO_AA=1`. If AA changes its RSC format
     the script emits `parsed 0` + exits 1 (logged, CONTINUE — agents fall back
     to live WebFetch as before).

PRELIM-F. ANOMALY_VERIFICATION_QUEUE (2026-05-27):
   ```
   python scripts/detect-anomalies.py
   ```
   - Runs the Layer-3 detector over CURRENT data/{models,sources}.json +
     `_schema.benchRanges`/`publishes[]`, writing `data/_anomalies.json` — a queue
     of cells needing DEEP VERIFICATION (not silent acceptance or rejection; a
     genuine breakthrough IS an outlier). Classes: `source-mismatch` (Elo-family
     metric misfiled), `out-of-band` (outside soft plausibility band),
     `single-source` (<2 distinct URLs on a core bench), `peer-outlier` (far from
     same-tier peers via robust MAD).
   - Orchestrator injects the top entries into every gather batch's
     `idea_context.anomalies = [{modelId, benchKey, value, reasons[]}, ...]`
     (sliced to the batch's modelIds). The agent resolves these FIRST per
     agent.md "OUTLIERS -> INVESTIGATE": find the primary source + exact
     metric/scale, then CONFIRM (keep), RECLASSIFY (correct cell/scale), or FLAG
     (rawGaps note) — never auto-dismiss for being "too high/low".
   - Advisory: never mutates data. Non-fatal. Opt-out via `AICODERMAP_NO_ANOMALY=1`.
   - This is the systematic backbone of "investigate outliers, don't reject them".
     (Full auto-dispatch of a research sub-agent the instant an anomaly surfaces
     mid-merge is future work; v1 = detect + queue + next-cycle research priority.)

PRELIM-E. LINEUP_ONLY_MINI_CYCLE_GATE (FAZ 7.I, 2026-05-10) — orchestrator-only fast path:
   - Computes `priorityCells = priority_cells(active, coreBenchKeys, limit=200, vmap, ttl=FRESHNESS_TTL_DAYS)`. If `priorityCells == []` AND every active model's `lastUpdated` is within `contracts.STALE_DAYS - 7` (default 7 days), the orchestrator switches the cycle to **lineup-sync only**: dispatches a single sonnet lineup agent (`scope=lineup-sync`, Step 0 only) and skips Stage A + Stage B + merge entirely. Output is whatever vendor-lineup deltas surface; data/{models,sources}.json values are unchanged.
   - **Full Phase 0 still runs in this fast path** — `lineup-sync` is the COMPLETE Phase 0, not a bare lineup-URL fetch: the agent still runs the WebSearch new-release net (agent.md step 3b, per-vendor templated probes) and the Phase 0 sub-probes (unknown-vendor / unknown-leaderboard discovery). Only Stage A/B (per-cell bench/pricing fill) and merge are skipped. This is what guarantees a brand-new model (e.g. an Opus-family bump) is still caught on a fully-fresh-matrix cycle even though no cell needs re-research.
   - Why: when the matrix is fully covered AND fresh, there is nothing for gather agents to research that the verification map doesn't already mark `confirmed=true ≤7d`. The cycle's only value is detecting NEW/DEPRECATED/RENAMED models from vendor lineup pages.
   - **Quality preserved:** the gate is hit only when EVERY active model was fully refreshed within the freshness TTL window. If even one cell is starved, full Stage A/B runs. The freshness check uses the verification map's `confirmed` flag (≥3 distinct sources within VERIFICATION_AGREEMENT_PP); not just the date.
   - Opt-out: `AICODERMAP_FULL_REFRESH=1` env var forces the full Stage A/B regardless. `--force` flag on `/aicodermap refresh-all --force` does the same.

0. LINEUP DISCOVERY (always run first on refresh-all):
   - Agent fetches each vendor's official "active models" page from VENDOR_LINEUP_SOURCES table
   - Returns canonical lineup: { vendorId: { active: [...], deprecated: [...], renamed: [{from,to}] } }
   - Skill diffs against current data/models.json:
     * NEW (in lineup, not in data) → flag for newModels[] survey in Step 4
     * DEPRECATED (in data, marked deprecated by vendor) → set status="deprecated", retain entry, gray-out in UI
     * RENAMED (vendor changed canonical id) → auto-rename per WRONG_ID_AUTO_FIX rule
     * REMOVED (no longer on vendor page after grace period) → archive to data/archive/<id>.json
   - This step CANNOT be skipped on refresh-all; it's the source of truth for "what models exist".
   - **Gather-hint harvest (MANDATORY, added 2026-06-06) — second new-model detection channel:**
     after Stage A gather returns, run `python scripts/harvest-new-models.py`. It unions
     every gather artifact's `lineupHints[event='new']` into `.aicodermap-lineup.json`'s
     `newModels[]`, deduped against `currentIds`. ROOT CAUSE this closes: the dedicated
     lineup agent depends on a vendor's lineup page being reachable; when it is SPA/403/dead
     and the WebSearch fallback misses the release, a genuinely-new model is dropped even
     though a gather agent researching that vendor's slice SAW it (e.g. `minimax-m3`,
     released 2026-06-01, was flagged by batch04-minimax's gather but absent from the lineup
     file). Harvesting makes detection robust to any single source failing. The harvested
     entries flow into the same stub-add + CHANGELOG path as lineup-agent newModels.
   - **Mandatory retry (added 2026-04-28):** if Step 4 returns with `lineup` empty/missing/`{}` AND this is not the first-ever run, the orchestrator dispatches ONE retry agent (sonnet) restricted to Step 0 (fetch vendor lineup pages only, no bench/pricing). On second-cycle empty, log `gaps[]` entry `lineup:incomplete` with reason and continue. Same retry policy applies when `runtime.healthChecks` covers fewer than 3 leaderboard domains.

1. Read data/{models,sources,sources-whitelist}.json + lineup result from Step 0
2. Parse arg → resolve scope + target_model_ids
3. Build idea_context (DATA-DRIVEN — agent never hardcodes data, only procedure):

   **FAZ 7.B/7.C (2026-05-10) — single-helper build:**
   ```python
   from lib.idea_context import build_per_batch_ctx
   # B (2026-06-07): gap-freshness-tier skip set (no-op until cells accrue
   # >=3 cycles of gap history in the verification map).
   gap_sk = compute_gap_skip_cells(vm, active_ids, core_keys)
   ctx = build_per_batch_ctx(
       batch_spec=batch,
       full_whitelist=wl,
       matrix_state=ms,
       priority_cells=pc,
       skip_cells=sk,
       gap_skip_cells=gap_sk,
       verification_map=vm,
       leaderboard_snapshots=snap,
       contracts=ctr,
       banned_fetch_patterns=bp,
       cycle_started_unix=time.time(),
       total_models=len(models),
       last_refresh=max(...),
       current_ids=[m['id'] for m in models],
       bench_keys=core_keys,
   )
   # Per-batch ctx: ~25-30 KB (vs 156 KB pre-7.B). Cuts batch ctx I/O 51%+.
   ```

   The helper writes a slim per-batch dict that:
   - Filters `sourcesWhitelist` via `lib.whitelist.filter_for_batch(...)`:
     keeps `_schema` in full, filters `vendors` to providers in this batch,
     filters `leaderboards`/`aggregators`/`local` `publishes[]` to bench_keys
     universe, drops `community`/`registries` (rarely used; agent reads
     directly from data/sources-whitelist.json on demand).
   - Slices `verificationMap.cells` to ONLY this batch's modelIds (was 93 KB
     full inline → ~3 KB slice).
   - Slices `priorityCells` and `skipCells` similarly.
   - Slims `leaderboardSnapshots` to URL→path only (drops contentLength,
     contentType, fetchedAt, etag — saves ~10-15 KB).
   - Adds `cycleStartedUnix` from PRELIM-C anchor (drives validator stale check).
   - Carries `_batchSpec` (modelIds, providers, expectedCells) for agent self-audit.

   The OUTPUT_SCHEMA below documents the agent-facing keys; the per-batch
   ctx file is read by the agent via `Read(.aicodermap-ctx-<batchId>.json)`.

   {
     title: "AICoderMap",
     total_models: <count from data/models.json>,
     last_refresh: <max(lastUpdated) from data/models.json>,
     currentIds: [<every id in data/models.json, including status='deprecated'>],
     cycleStartedUnix: <epoch seconds from PRELIM-C>,
     familyGrouping: <models grouped by (provider, tier) for parallel batches>,
     // sourcesWhitelist is now SLICED per batch — see helper above.
     sourcesWhitelist: filter_for_batch(wl, providers, bench_keys=core_keys),
     // verificationMap is now SLICED per batch — only batch's modelIds' cells.
     verificationMap: { cells: { ... } },  // batch-slice only, not full
     lineup: <Step 0 result>,

     // Matrix-aware context (P7+C plan reform — added 2026-04-29):
     // Computed via scripts/lib/matrix.py {matrix_snapshot, priority_cells}.
     // Skill MUST inject these so the agent sees the contract reality:
     // expected_total cells, current per-bench/per-model fill state, and
     // a top-N starvation queue to resolve FIRST.
     matrixState: <matrix_snapshot(active_models, coreBenchKeys)>,
     // Shape: {
     //   activeModels: <int>, coreKeys: <int>,
     //   totalCells: <int>, filledCells: <int>,
     //   expectedTotal: <int>,
     //   fillRatio: <float 0..1>,
     //   byBench: { <key>: {filled, total} },
     //   byModel: { <id>:  {filled, total} }
     // }
     priorityCells: <priority_cells(active_models, coreBenchKeys, limit=200, verification_map=vm, skip_confirmed_within_days=contracts.FRESHNESS_TTL_DAYS)>,
     // FAZ 4.A (2026-05-08): ORDERING (advisory), NOT scope.
     // Top-N empty (modelId, benchKey) pairs ranked by starvation. Agent
     // resolves priorityCells FIRST inside its slice, then sweeps the rest
     // of `target_model_ids × coreBenchKeys`.
     //
     // Pre-FAZ-4.A (FAZ 2.3 reform): priorityCells was AUTHORITATIVE — agent
     // walked ONLY this list, ignoring the rest of its slice. Cycle 2026-05-08
     // measured the cost: 18 batches used 591/900 tool-calls (~33%) and
     // produced 51 fills (~4% slice coverage) because top-200 priority queue
     // ÷ 18 batches ≈ 11 cells/batch — agents stopped early.
     //
     // FAZ 4.A restores full-slice target. Wallclock cap (FAZ 1.3) +
     // tool-call ceiling (FAZ 1) independently prevent runaway sweep (the
     // problem the 2.3 reform tried to fix).
     contracts: <data/sources-whitelist.json._schema.contracts>,
     // Numeric thresholds (ABSOLUTE_COVERAGE_FLOOR, MIN_SOURCES_PER_FILLED_CELL,
     // VERIFICATION_AGREEMENT_PP, etc.) — single source of truth; agent reads
     // these values rather than hardcoding any number in agent.md.

     // FAZ 1.4: hard WebFetch ban list. Agent FORMAT_DISPATCH refuses these URLs.
     // Sources: skipWebFetch=true formats (spa_full/image_embedded/bot_blocked),
     // _runtime.unhealthy=true entries, and vendor URLs whose format matches.
     // Computed via scripts/lib/whitelist.banned_fetch_patterns(whitelist).
     bannedFetchPatterns: banned_fetch_patterns(sourcesWhitelist),

     // FAZ 2.1: pre-fetched leaderboard snapshots from PRELIM-B.
     // Agent uses Read(path) instead of WebFetch(url) when URL is in map.
     // Cuts ~666 duplicated WebFetches/cycle (18 agents × 37 leaderboards) to
     // 73 single-pass HTTP gets in ~15s. Loaded from
     // data/.leaderboard-snapshots/_index.json.
     leaderboardSnapshots: load_snapshot_index(),
       // Shape: { <url>: { path, contentType, contentLength, fetchedAt, etag } }

     // FAZ 2.2: freshness-tier skip cells (T2 only — T1 always re-fetches).
     // T2 = confirmed=true AND verifs≥3 AND age≤FRESHNESS_TTL_DAYS AND no contradiction.
     // Agent FORMAT_DISPATCH treats T2 cells as already-filled and emits cached
     // value + provenance without any fetch. Computed via
     // scripts/lib/freshness.compute_skip_cells(). NOT a known-gaps registry redux:
     // any cell with <3 verifs, missing freshness, or any contradiction is T1
     // (re-fetched every cycle). Drift surfaces within ≤7d for confirmed cells.
     skipCells: compute_skip_cells(
       verification_map,
       today,
       active_model_ids,
       coreBenchKeys,
       ttl_days=contracts.FRESHNESS_TTL_DAYS or 7,
       min_verifs=contracts.MIN_VERIFICATIONS_FOR_SKIP or 3,
     )
       // Shape: { <modelId>: { <benchKey>: {value, sources[], lastChecked, ageDays, verifications} } }
       // Plus _meta: {t1Count, t2Count, totalConsidered}

     // B (2026-06-07): gap-freshness-tier skip cells. A cell empty for
     // >=GAP_SKIP_MIN_CYCLES (3) consecutive cycles, each with
     // >=GAP_SKIP_MIN_SOURCES (2) distinct triedSources, is re-checked only
     // every GAP_RECHECK_EVERY-th (4th) cycle — the ~435 perma-empty cells
     // (cfElo for non-competitive models, nl2Repo, mrcr) dominate gather
     // tool-calls re-confirming "still empty". TIME-BASED, never permanent: a
     // vendor opt-in surfaces within <=4 cycles. Driven by the verification
     // map's per-cell gapCycles/gapTriedSources (stamped at Step 7.6 from the
     // merge artifact's gaps[]). The agent emits the carried gap WITHOUT a
     // fetch, so merge.py's MX1 (filled+gaps+na==total) still holds. No-op until
     // cells accrue >=3 cycles of gap history. Computed via
     // scripts/lib/freshness.compute_gap_skip_cells().
     gapSkipCells: compute_gap_skip_cells(verification_map, active_model_ids, coreBenchKeys)
       // Shape: { <modelId>: { <benchKey>: {gapCycles, gapSince, triedSources, reason} } }
       // Plus _meta: {skipCount, eligibleCount, recheckCount}
   }
   - `.aicodermap-verification-map.json` is the historical audit log of every (model, bench) cell observation across cycles (value, sources[], lastChecked). Used for contradiction analysis only — never read for skip decisions, since every cell is re-fetched every cycle (UNCAPPED + UNCACHED doctrine, reformed 2026-04-28). Skill creates it (empty {}) on first cycle if missing.
   - `data/models.json` is SSOT for "what models we track" — `currentIds` MUST be derived from this file at the moment the skill runs. Hardcoding the id list in a prompt or agent message is a contract violation (any drift between models.json and what the agent receives surfaces as silent omission of new/renamed models).
   - `data/sources-whitelist.json` is SSOT for "what URLs the agent is allowed to fetch" AND for the bench-key universe (`_schema.coreBenchKeys`). Frontend `BENCH_KEYS` (assets/js/core.js), i18n `benchmarks.*`, and the data-file `bench` cells all mirror this canonical set. `scripts/audit-data-coherence.py` enforces the mirroring by failing loudly on any drift.
   - No skip registry: every (modelId, benchKey) pair is re-attempted every cycle so vendor opt-outs that close are surfaced immediately
   - The agent file (.claude/agents/aicodermap-research-agent.md) only carries PROCEDURE (how) — every list of URLs, vendors, or model IDs lives in data files
// FAZ 4.C (2026-05-09) → A3 (2026-05-31): SONNET GATHER + DETERMINISTIC SYNTH.
   // Two-stage pipeline: gather (N batches × sonnet) + synth (1 × local-synth.py).
   //   Stage A (gather): N batches × SONNET agent (mode="gather").
   //     Full research quality from the first pass; emits raw observations
   //     + naCandidates + lineupHints. NO contradiction analysis, NO trustScore
   //     math, NO autoResolveWinner — that stays in Stage B.
   //   Stage B (synth):   `python scripts/local-synth.py` (DETERMINISTIC, A3).
   //     Reads ALL gather artifacts, applies trustScore + contradictions +
   //     autoResolveWinner over real observations. Emits full OUTPUT_SCHEMA
   //     artifact. The prior sonnet synth agent is RETIRED — it fabricated bench
   //     values every cycle and always fell back to local-synth anyway.
   //
   // Rationale for dropping haiku gather (FAZ 4.C.2 retired):
   //   Empirical result — 14/18 haiku batches came back weak (avg_obs < 3),
   //   triggering sonnet escalation anyway. Net result: haiku cost + sonnet
   //   cost + 2× latency. Models without leaderboard presence (MiniMax, MiMo,
   //   GLM, Mistral-small) are data-sparse regardless of model quality;
   //   haiku didn't help. Going straight to sonnet eliminates the escalation
   //   loop, halves cycle latency, and simplifies the orchestrator.
   //   The 0-fill auto-retry (FAZ 2.4) remains as the sole safety net.
   //
   // Quality: edge cases (WRONG_ID, cross-model misattribution, contradiction
   // detection) concentrate in the single sonnet synth pass.
   //
   // Adaptive multi-batch dispatch (FAZ 1.2 — unchanged): every batch fits
   // under AGENT_BUDGET_BUFFER=50 tool-call ceiling. Plan source:
   // scripts/lib/dispatch.compute_dispatch_plan(active, coreKeys).
   //
   // Stage A artifact path: .aicodermap-agent-out-<batchId>.gather.json
   // Stage B artifact path: .aicodermap-agent-out-synth.json (consumed by
   //                        gen_unified_artifact.py before merge).

   plan = compute_dispatch_plan(active_models, coreBenchKeys)  // dispatch.py
   per_batch_artifacts = []
   wave_state = {"pending": list(range(len(plan["waves"]))), "completed": []}

   // ─── Stage A: SONNET GATHER (parallel waves) ─────────────────────────
   for wave_index in range(len(plan["waves"])):
     // Sequential between waves; parallel within a wave.
     wave_results = parallel([
       Agent({
         subagent_type: "aicodermap-research-agent",
         model: "sonnet",  // FAZ 4.C revised: sonnet directly — haiku escalation retired
         prompt: structured(
           scope, query,
           mode: "gather",  // HARD: no contradiction/autoResolve/WRONG_ID
           idea_context: filtered_for_bucket(idea_context, batch_spec),  // F5
           target_model_ids: batch_spec.modelIds,
           batch_id: batch_spec.batchId,
           expected_total: batch_spec.expectedCells,
           agent_budget_buffer: plan.agentBudgetBuffer,
           wallclock_deadline_unix: now() + BATCH_WALLCLOCK_SEC,
           include_unsloth: true,
           trusted_sources_only: true,
           parallel_sources: 5,
           parallel_models: 5,
           verification_map_path: ".aicodermap-verification-map.json",
           termination: "completeness",
           require_priority_first: true,  // ordering only (FAZ 4.A)
           require_full_matrix: true,
         ),
         output_path: f".aicodermap-agent-out-{batch_spec.batchId}.gather.json"
       })
       for batch_spec in [b for b in plan.batches if b.waveIndex == wave_index]
     ])
     // Stamp each artifact with the REAL file it was written to, so Stage B reads
     // exactly these (and any retry replacement below) — never a reconstructed path.
     for art, bspec in zip(wave_results,
                           [b for b in plan.batches if b.waveIndex == wave_index]):
       art._source_path = f".aicodermap-agent-out-{bspec.batchId}.gather.json"
     per_batch_artifacts.extend(wave_results)
     wave_state["completed"].append(wave_index)
     wave_state["pending"].remove(wave_index)
     log(f"✓ wave {wave_index}/{len(plan.waves)} complete: "
         f"{len(wave_results)} batches returned")

     // FAZ 2.4 (2026-05-07): 0-fill batch auto-retry — single retry per batch.
     // After each wave completes, scan its results for batches with fills==0
     // (and cellsAttempted > 0 — distinguish "agent ran but found nothing" from
     // "agent crashed before any fetch"). For each such batch, dispatch ONE
     // fresh-context retry with the same params. Retry returns merge into
     // per_batch_artifacts; if the retry also yields fills==0, log a CHANGELOG
     // warn and accept the empty result. Cycle 2026-05-06 batch03-google_deepm
     // 0-fill was the canonical case this protects against.
     zero_fill = [r for r in wave_results
                  if (r.runtime.cellsAttempted or 0) > 0 and r.runtime.fills == 0
                  and not r._retry_attempted]
     if zero_fill:
       log(f"⚠ {len(zero_fill)} batches returned 0 fills — dispatching retries")
       retry_results = parallel([
         Agent({
           subagent_type: "aicodermap-research-agent", model: "sonnet",
           prompt: structured(... same params as original ...,
                              retry_of: r.batchId,
                              wallclock_deadline_unix: now() + BATCH_WALLCLOCK_SEC),
           // Retry writes a GATHER artifact (same .gather.json convention) so
           // Stage B's synth_input_paths can consume it directly. CRITICAL fix
           // 2026-05-29: previously '-retry.json' (non-gather) + path rebuilt
           // from plan.batches → synth read the STALE 0-fill gather, never the
           // retry's fills.
           output_path: f".aicodermap-agent-out-{r.batchId}-retry.gather.json"
         })
         for r in zero_fill
       ])
       for orig, ret in zip(zero_fill, retry_results):
         ret._retry_attempted = true
         ret._source_path = f".aicodermap-agent-out-{orig.batchId}-retry.gather.json"
         if ret.runtime.fills > 0:
           // Replace zero-fill result with retry's productive output (carries its
           // own _source_path, so Stage B reads the retry file, not the original).
           replace_in_list(per_batch_artifacts, orig, ret)
           log(f"  ✓ {orig.batchId} retry recovered {ret.runtime.fills} fills")
         else:
           log(f"  ✗ {orig.batchId} retry also 0 fills; logging warn")
           changelog_warns.append(f"⚠ {orig.batchId}: 0 fills × 2 (genuinely unreachable)")

   // HARD GUARD — never advance with missing waves.
   if len(wave_state["completed"]) != len(plan["waves"]):
     log_error(f"✗ wave dispatch incomplete: completed={wave_state['completed']} "
               f"of {list(range(len(plan.waves)))}. Halting BEFORE Stage B.")
     halt_workflow()

   // Stage A.5 (RETIRED 2026-05-17): haiku weak-batch escalation removed.
   // Sonnet gather runs first-pass; FAZ 2.4 0-fill retry is the sole safety net.

   // ─── Stage B: SONNET SYNTH (single dispatch, post-gather) ──────────────
   // FAZ 4.C: synth agent reads ALL gather artifacts, applies analytical
   // work (trustScore, contradictions, autoResolveWinner, WRONG_ID, N/A
   // citation), emits unified OUTPUT_SCHEMA artifact.
   //
   // Synth does NOT fetch — it consumes pre-fetched observations. This
   // keeps the expensive sonnet pass focused on reasoning, not extraction.
   // Build from the REAL per_batch_artifacts paths (post-retry-replacement), NOT
   // a reconstruction from plan.batches — that ignored retry swaps and fed synth
   // stale 0-fill gathers (CRITICAL, fixed 2026-05-29).
   gather_paths = [a._source_path for a in per_batch_artifacts if a._source_path]
   // 3.6 — ZERO-OBS / WEAK-BATCH FILTER + per-batch coverage. Validate each
   // gather before it enters synth: validate_gather flags `zero valid
   // observations` (valid=False) and computes per-batch cardinality
   // (`perModelObs`, `avgObs`, `isWeakBatch`, MIN_AVG_OBS_PER_MODEL floor).
   // A zero-obs gather contributes NOTHING to synth but burns its context
   // budget, so drop it from synth input (its cells already persist as
   // gaps[]/priorityCells for the next cycle). coverageMatrix stays OUT of the
   // gather schema (flat-schema discipline — it's a FULL_SCHEMA_BLEED_KEY); the
   // per-batch coverage signal is derived here from perModelObs instead.
   kept_paths, dropped = [], []
   for a in per_batch_artifacts:
     if not a._source_path:
       continue
     v = validate_gather_file(a._source_path, batch_model_ids_of(a),
                              cycle_started_unix=idea_context.cycleStartedUnix)
     if v["stats"].get("observations", 0) == 0:
       dropped.append(a._source_path)        // zero-obs (already retried via FAZ 2.4)
     else:
       kept_paths.append(a._source_path)
       if v["stats"].get("isWeakBatch"):
         log("⚠ weak batch into synth: " + a._source_path +
             " avgObs=" + str(v["stats"].get("avgObs")) +
             " weakModels=" + str(len(v["stats"].get("weakModels", []))))
   if dropped:
     log("ℹ dropped " + str(len(dropped)) + " zero-obs gather(s) from synth input: " + str(dropped))
   gather_paths = kept_paths
   // ─── Stage B: LOCAL-SYNTH PRIMARY (deterministic — 2026-05-31, A3) ─────────
   // The sonnet synth agent is RETIRED as the primary path. Empirical result
   // across 2026-05-28 → 2026-05-30: the sonnet synth FABRICATED bench values
   // every cycle (68 ungrounded values on 2026-05-28; 1 + under-production of
   // 32 fills on 2026-05-30) and ALWAYS fell back to local-synth via the
   // traceability gate. So the sonnet dispatch was pure cost + latency + risk
   // with no surviving output. local-synth.py is now the PRIMARY synth: it is
   // deterministic, CANNOT hallucinate (only picks trust-winners from real
   // gather observations), and out-produced the sonnet synth (716 vs 32 fills
   // on the same inputs). It reads every `.aicodermap-agent-out-batch*.gather.json`
   // (incl. the deterministic batch90-aa-rsc) and writes the unified artifact.
   //   python scripts/local-synth.py     // → .aicodermap-agent-out-synth.json
   // The expensive analytical edge cases the sonnet synth was meant to own
   // (WRONG_ID, cross-model misattribution) are covered deterministically by
   // gen_unified + merge audits (AC12 id-canon, MX-rules) + the AA cross-check
   // (apply-aa-authoritative / audit-agent-misfiles). If a future need for
   // LLM-grade narrative synthesis arises, dispatch a NARROW sonnet pass that
   // only ANNOTATES contradictions[] — it must never emit bench fills.
   run("python scripts/local-synth.py")
   synth_result = read(".aicodermap-agent-out-synth.json")

   // ─── Stage B GATE: synth bench-value traceability (2026-05-28) ──────────
   // Now that local-synth is PRIMARY (A3), this gate is a CONFIRMATION rather
   // than a fallback trigger: local-synth cannot fabricate (it only emits
   // trust-winners from real gather observations), so the gate should pass
   // clean every cycle. It is RETAINED as a cheap invariant check — it still
   // classifies every non-null updates.bench[k] against the cell's EVIDENCE
   // ENVELOPE (fresh gather observations ∪ historical sources.json); a value
   // outside [min,max] would indicate a local-synth bug, and --auto-fallback
   // simply re-runs local-synth (idempotent). It also still emits the advisory
   // divergences[] (grounded values that disagree with THIS cycle's fresh
   // observations by > CONTRADICTION_WARN_PP) into data/_synth-traceability.json
   // for the Step 7.7 anomaly→research loop. (Historical note: when a sonnet
   // synth was primary it fabricated 68 values on 2026-05-28 + under-produced on
   // 2026-05-30, which is exactly why A3 retired it.)
   //   python scripts/validate-synth-traceability.py --auto-fallback
   // Exit 0 = clean (expected). Exit 2 = local-synth bug → loud CHANGELOG warn;
   // merge.py's own MX/anomaly audits remain the backstop.

   // gen_unified_artifact.py prefers synth output when present, falls back
   // to gather union otherwise.
   artifact = merge_batch_artifacts(per_batch_artifacts)

   **Prompt header MUST surface (verbatim, not paraphrased):**
   ```
   MATRIX REALITY (this cycle):
     active models: <matrixState.activeModels>
     core bench keys: <matrixState.coreKeys>
     expected_total cells: <matrixState.expectedTotal>
     currently filled: <matrixState.filledCells> (<fillRatio*100>%)
     missing-or-stale: <expectedTotal - filledCells>

   PRIORITY QUEUE (top <N>; resolve these FIRST in Phase 2/3 cascade):
     <modelId>.<benchKey>  (bench fill <ratio>, model fill <ratio>)
     ...

   EMISSION RULES (HARD, see agent.md SUCCESS_CRITERIA):
     - every cell ends as: bench[k]=value | gaps[].entry (N/A retired 2026-05-26)
     - gaps[] entries: triedSources[]>=1, triedQueries[]>=2, triedFormats[]>=1
     - silent omission triggers MX1 rollback in merge.py
   ```
5. Parse return:
   - **PRIMARY (post-2026-05-07):** read `.aicodermap-agent-out-<batchId>.json` (agent wrote it via `Write` tool)
   - **WRITE-SKIP RECOVERY (FAZ 8.A, 2026-05-18):** the orchestrator FIRST
     checks `Path(out_path).exists()` against the freshly-dispatched agent
     return. When the agent finished (returned status) but no file appears
     on disk, that's a write-skip contract violation (cycles 2026-05-13
     and 2026-05-18 measured this in ~25% of haiku gather batches).
     Recovery dispatch — small, cheap, max 3 tool calls:
     ```python
     if not Path(out_path).exists() and agent_finished:
         from scripts.lib.telemetry import record_write_skip
         record_write_skip(batch_id, cycle_date)
         recovery = Agent({
             subagent_type: "aicodermap-research-agent",
             prompt: (
                 f"Previous run for batch {batch_id} did not Write the "
                 f"artifact. Write a minimal valid stub NOW to {out_path} "
                 f"using the structure documented in HARD RULE 11. Return "
                 f"EMITTED. Do not re-fetch sources."
             ),
             output_path: out_path,
             max_tool_calls: 3,
         })
         # If still missing → proceed to FALLBACK A (transcript replay)
     ```
   - **STALE-VIOLATION RECOVERY (3.2, 2026-05-29):** a file that EXISTS but whose
     content predates this cycle is just as corrupting as a missing one — the
     agent reused a prior-cycle artifact without re-running. After reading
     `out_path`, validate it against the cycle anchor:
     ```python
     from scripts.lib.gather_validator import validate_gather_file
     v = validate_gather_file(out_path, batch_model_ids,
                              cycle_started_unix=idea_context.cycleStartedUnix)
     if v["stats"].get("stale") or v["stats"].get("missingStartedAt"):
         # runtime.startedAt < cycleStartedUnix - grace, OR startedAt absent →
         # treat EXACTLY like a write-skip: re-dispatch (same recovery as above),
         # never feed the stale content into synth.
         record_write_skip(batch_id, cycle_date)   # same telemetry channel
         <re-dispatch the batch fresh, then re-validate once>
     ```
     This is the content-based twin of the mtime stale guard in PRELIM (prune +
     `--cycle-started-unix`): mtime can be refreshed by a touch/partial write, but
     `runtime.startedAt` is the agent's own claim of when it began.
   - **FALLBACK A:** if file missing/unparseable AFTER recovery dispatch,
     run `python scripts/extract-agent-output.py <subagent-jsonl-path> <out-path>` against the agent's transcript at `~/.claude/projects/<projid>/<sessionid>/subagents/agent-<agentId>.jsonl`
   - **FALLBACK B:** if persisted tool-result file exists at `<projid>/<sessionid>/tool-results/toolu_*.json`, run `extract-agent-output.py <persisted-json> <out-path>`
   - validate JSON schema after extraction; on parse failure log to `~/.aicodermap-debug.log` and CONTINUE with whatever fragment is recoverable

5-F6. PARTIAL_RETURN_GATE (F6 reform — 2026-04-30):
    For each sub-agent artifact:
    ```
    partial_reason = artifact.partialReason  // may be string or structured object
    cells_attempted = partial_reason?.cellsAttempted if isinstance(dict) else null
    batch_expected = len(batch_i) * len(coreBenchKeys)  // na cells not yet subtracted (conservative)

    completeness_ratio = cells_attempted / batch_expected if cells_attempted else null

    if completeness_ratio != null and completeness_ratio < 0.30:
        if wallclock < 480s and completeness_ratio > 0 and not artifact._partial_continued:
            // Agent stopped too early but has wallclock left — SendMessage to
            // SAME agent (cheapest: keeps its warmed context) to continue.
            artifact._partial_continued = true
            SendMessage(agent_id, "Continue from where you stopped. You attempted " +
              cells_attempted + "/" + batch_expected + " cells (" + round(completeness_ratio*100) +
              "%). Process the remaining cells before emitting final JSON.")
            // Wait for second return, then re-evaluate completeness_ratio below.
        if completeness_ratio < 0.30 and not artifact._partial_retry_attempted:
            // STILL < 30% (SendMessage didn't help, OR wallclock exceeded, OR
            // zero cells attempted). Do NOT silently accept — dispatch ONE
            // FRESH-CONTEXT sonnet retry, identical policy to the FAZ 2.4 0-fill
            // retry (a fresh context often clears the wedged-state that made the
            // first agent stall). Reuse the same batch params + gather output_path
            // so the retry REPLACES this artifact in per_batch_artifacts.
            artifact._partial_retry_attempted = true
            log("⚠ batch " + bucket + " completeness " + completeness_ratio +
                " < 0.30 — dispatching fresh-context sonnet retry")
            retry = Agent({
                subagent_type: "aicodermap-research-agent", model: "sonnet",
                prompt: structured(... same params as original batch ...,
                                   retry_of: batch_id, reason: "partial<0.30",
                                   wallclock_deadline_unix: now() + BATCH_WALLCLOCK_SEC),
                output_path: f".aicodermap-agent-out-{batch_id}-partialretry.gather.json"
            })
            retry._source_path = f".aicodermap-agent-out-{batch_id}-partialretry.gather.json"
            retry._partial_retry_attempted = true
            if (retry.runtime.cellsAttempted or 0) / batch_expected >= completeness_ratio:
                replace_in_list(per_batch_artifacts, artifact, retry)   // keep the better return
                log("  ✓ " + batch_id + " partial-retry improved coverage")
            else:
                changelog_warns.append("⚠ " + batch_id + ": partial<0.30 ×2 — next cycle picks up via gaps[]/priorityCells")
        // After at most one SendMessage + one fresh retry, accept whatever we have
        // and CONTINUE — never halt; unfilled cells persist as gaps[]/priorityCells.
    ```
    This ensures agents cannot cheaply exit after surveying only 8/882 cells —
    a <30% return is escalated (continue → fresh sonnet retry), never silently merged.

5a. MATRIX_SNAPSHOT (P7 reform):
    Before consuming the artifact, snapshot the pre-merge state of
    `data/models.json` so step 5b can detect partial returns + zero-delta
    silence:
    ```
    pre_snapshot := {
       totals: { models: |active|, coreKeys: |coreBenchKeys| },
       perModel: { id: { filled: <int>, gapKeys: [] } for id in active }
    }
    ```
    Skill computes via scripts/lib/matrix.py helpers (active_models +
    filled_cells_from_models). `pre_snapshot` is held in skill
    memory only; never written to disk.

5b. GAP_GEN SUPPLEMENT (mandatory — runs ALWAYS after agent return, not just on failure):
    ```
    // Architectural reform 2026-04-29: the agent emits only what it FOUND.
    // Gap enumeration for all remaining unfilled cells is the orchestrator's job.
    // The agent's gaps[] contains only cells it actively attempted and failed;
    // it does NOT enumerate cells it never touched (that caused infinite loops).

    python scripts/gap_gen.py
    // gap-gen reads data/models.json (current state) + sources-whitelist.json
    // and writes .aicodermap-agent-out.json, MERGING the agent's found values
    // into the existing artifact and adding gaps[] for all remaining unfilled cells.
    // This ensures merge.py MX1 invariant (filled+gaps+na == totalCells) always holds.

    // gap-gen merge policy (in .aicodermap-gap-gen.py):
    //   1. Read .aicodermap-agent-out.json (agent artifact, may not exist if agent looped)
    //   2. For each (active_model, bench_key):
    //      - If artifact has a fill for this cell → keep fill
    //      - Else if artifact has an explicit gap → keep gap
    //      - Else → add auto-gap with appropriate triedSources/triedQueries/triedFormats
    //   3. Write merged artifact back to .aicodermap-agent-out.json

    // No retry agent needed. next cycle re-attempts all cells anyway (UNCAPPED doctrine).
    // CHANGELOG records gap count: "⚠ gap-gen supplemented <N> cells"
    CONTINUE to Step 5c
    ```

5c. DELTA_CHECK (P7 reform):
    Compare artifact against `pre_snapshot`:
    ```
    for id in pre_snapshot.perModel.keys:
        delta := artifact.models[id].sourcesAdded[]
                 ∪ artifact.models[id].updates
                 ∪ gaps[].(modelId==id)
                 ∪ notApplicable[].(modelId==id)
        if delta is empty:
            runtime.modelAudit[id] := "zero-delta-no-gap"
    ```
    Zero-delta-no-gap models are NOT halts — they surface in the CHANGELOG
    "⚠ silent omission suspects" section so the next cycle prioritizes them.

6. COVERAGE LOG — **advisory only (reformed 2026-04-28)**:
   The agent already walks every source for every (modelId, benchKey) cell in
   one pass (UNCAPPED + UNCACHED doctrine). There is no separate deep-fetch
   loop. The orchestrator just records:
     - validationCoverage (cumulative — see agent.md VALIDATION_RULES rule 2)
     - if < COVERAGE_TARGET (0.85): set artifact.partialCoverage=true, append
       "⚠ cumulative provenance coverage: <%>" line to CHANGELOG
     - if < COVERAGE_HARD_BLOCK (0.50): append a louder
       "⚠ very low cumulative provenance coverage" warning, but still commit
   No loop, no halt. Every gap from this cycle stays in artifact.gaps[] for
   audit; the next cycle re-attempts every cell anyway (no skip cache).

   ENFORCEMENT: `scripts/merge.py` MUST NOT halt the commit on low coverage.
   Coverage is advisory only.

   **Hard rule:** missing data is NEVER a reason to skip Step 10–12 (write+commit+push). Partial coverage merges are normal; the next cycle re-fetches everything anyway.

7. CONTRADICTION AUTO-RESOLUTION (NOT manual prompt):
   for each contradiction in contradictions[]:
     winner = argmax(trustScore(value) for value in candidates)
     write winner.value to data/models.json
     append all candidates to data/sources.json with their trustScores
     log to CHANGELOG: "<modelId>.<bench>: <winner.value> (trust=<score>) over <loser.value> (trust=<score>) [Δ<delta>pp <severity>]"
   no user prompt is issued for any severity

7.4. IMAGE_OCR_AUTO_TRIGGER (whitelist-driven, NO hardcoded vendor list):
   - For every artifact `models[].sourcesAdded[]` entry, the orchestrator looks up the source URL's hostname in `sourcesWhitelist.vendors.*.imageOCRPatterns[]` (or any whitelist entry whose `format == "image_embedded"`):
     ```
     for each addedSource in artifact.models[].sourcesAdded[]:
       vendorEntry := find_vendor_by_hostname(addedSource.url, sourcesWhitelist.vendors)
       imagePatterns := vendorEntry?.imageOCRPatterns
                       || (lookup_whitelist_entry(addedSource.url).format == "image_embedded" ? [".+"] : null)
       if imagePatterns AND any(re.match(p, addedSource.url) for p in imagePatterns)
         AND model_null_bench_count(addedSource.modelId) >= 3:
         dispatch scripts/extract-images.py <url>
     ```
   - `scripts/extract-images.py <url>` downloads embedded PNGs to `.aicodermap-images/`.
   - Skill orchestrator (vision-aware Read tool) reads each PNG and extracts (modelName, benchName, score) via the bench alias table in agent.md EXTRACTION_DISCIPLINE.
   - Extracted values get S-tier provenance pointing to the page URL. Merged into pending updates before Step 10.
   - Image OCR is opt-out per vendor: omit `imageOCRPatterns` (or set to `[]`) in the vendor's whitelist entry — no flag needed.
   - **Adding a new image-embedded vendor** = appending `imageOCRPatterns: ["<regex>"]` to that vendor's whitelist entry; no SKILL.md or agent.md change required.
   - **DECISION (2.7, 2026-05-29) — image-OCR stays a need-gated dispatch, NOT a blanket PRELIM step.** Per agent.md IMAGE_OCR_FALLBACK's empirical finding (2026-04-26): the coreBenchKeys universe (SWE-bench Verified, GPQA, HLE, Terminal-Bench, LCB, tau-bench, MCP-Atlas) lives in vendor-page TEXT lead summaries or on independent leaderboards — NOT in the announcement PNG charts, which carry mostly AUXILIARY benches. So `image_embedded`'s `static_html_article → websearch_snippet` fallback is sufficient for our scored benches, and OCR is reserved for the residual case (this step, gated on `model_null_bench_count ≥ 3`). Promoting OCR to an unconditional PRELIM pass would burn vision-Read budget on auxiliary-bench charts we do not score. Re-evaluate only if a future vendor ships core benches image-only.

7.5. DYNAMIC_WHITELIST_DISCOVERY (self-healing whitelist mutation, post-fact persistence):
   - Reform 2026-04-28 rev3: the agent already FETCHED any non-whitelisted HTTPS source that surfaced during Phase 3 step 4 (in-cycle promotion — see agent.md TRUSTED_SOURCE_WHITELIST rule 6). Values from those fetches are already in `artifact.models[*].sourcesAdded[]` with tier=C and were merged into data/models.json + data/sources.json by step 10. This step's job is no longer to gate when the source is USED — it is to harden the source into the whitelist file so subsequent cycles can fetch it without rediscovery.
   - Skill reads `artifact.whitelistAdditions[]` (agent emits ONE entry per non-whitelisted URL it fetched in-cycle, plus any URL it would have fetched but couldn't due to the safety gates)
   - For each addition:
     * tier='C' (default for in-cycle-promoted sources) → append to data/sources-whitelist.json `community[]` with format=`addition.observedFormat || 'static_html_article'`, lastVerifiedDate=today, consecutiveFailures=0
     * tier='I' → append to `aggregators[]` with phase='discovery' (not promoted without manual review)
     * tier='S' → only if matches existing vendor; ignored otherwise
   - Skill scans `artifact.runtime.healthChecks` and updates `data/sources-whitelist.json._runtime.healthChecks` per-domain
   - Domains with consecutiveFailures ≥ 3 across cycles get `_runtime.unhealthy: true`; auto-skipped in next 2 cycles' Phase 1 (still tried via WebSearch fallback)
   - Whitelist mutations are committed alongside data/* changes — versioned and reversible.
   - **No data is "deferred" to next cycle.** The whitelist mutation is purely operational — it lets future cycles skip rediscovery and treat the source as a known starting point. The actual values discovered this cycle are committed this cycle.

7.6. VERIFICATION_MAP_UPDATE (audit log, reformed 2026-04-28):
   - After merge writes data/models.json, run `python scripts/verification-map.py update`
   - The script reads `.aicodermap-agent-out.json` sourcesAdded[] entries, groups by (modelId, benchKey), and appends to the historical audit log:
     ```
     for each (modelId, benchKey) cell observed this cycle:
       map.cells[modelId.benchKey].verifications[].append({source, url, value, tier, fetched})
       if all values agree within VERIFICATION_AGREEMENT_PP (=1.5pp) AND len >= 3:
         map.cells[modelId.benchKey].confirmed = true   // audit flag only
       else if values disagree:
         map.cells[modelId.benchKey].confirmed = false  // contradiction analysis input
       map.cells[modelId.benchKey].lastChecked = TODAY (only if at least one new verification appended this cycle)
     ```
   - Persists `.aicodermap-verification-map.json` (gitignored — historical record, regeneratable from sources.json via `bootstrap`)
   - The `confirmed` flag is **audit-only** — used for contradiction analysis and human review. It is NEVER read to skip a FILLED-cell fetch (filled cells re-fetch every cycle; the T2 filled-skip stays dormant while `confirmed` is unset).
   - **B (2026-06-07) — gap-history stamping (powers the gap-freshness-tier).** The same `update` pass also reads the merge artifact's `gaps[]`: each still-empty cell gets `gapCycles += 1`, `gapSince` set on the first gap of a run, and `gapTriedSources` = the MIN distinct triedSources across the run (conservative). A cell FILLED this cycle has its gap run reset (`gapCycles = 0`). `compute_gap_skip_cells` reads these at the next cycle's ctx build. (This pass also fixed a latent bug — the prior `"bench" not in key` filter skipped EVERY `<modelId>.<benchKey>` sourcesAdded entry, so the incremental verification append was a silent no-op every cycle; now filtered against the bench-key universe.)

7.6b. AA_AUTHORITATIVE_CORRECTION (2026-05-31, post-merge deterministic corrector):
   ```
   python scripts/apply-aa-authoritative.py --apply   # fix AA-composite misfiles + fill empties
   python scripts/audit-agent-misfiles.py             # advisory sweep report
   python scripts/audit-data-coherence.py             # re-verify SSOT after correction
   ```
   - `aaIdx`/`aaCoding`/`aaAgentic` are Artificial Analysis's OWN definitional
     composite indices — no one else computes them, so a stored value that
     disagrees with AA's current value (from PRELIM-G's `_aa-rows.json`) by >2pp
     is a misfile (an agent misread AA, or filed a different metric). Confirmed
     empirically 2026-05-31: AA's aaIdx ceiling is ~61 yet agents had stored
     71-79 (physically impossible). The corrector deterministically adopts AA's
     value (override misfile OR fill empty) and replaces provenance with the AA
     I-tier entry. It ALSO corrects AA-MEASURED externals (gpqa/hle/tau2/tbHard)
     ONLY when the stored value is outside AA's observed envelope for that bench
     (physically impossible, e.g. hle=79 when AA's ceiling is 45.7) — plausible
     source variance is left untouched.
   - Runs AFTER merge so it corrects the final written data (like
     apply-anomaly-verdicts). Rotates .bak. If `audit-data-coherence.py` then
     fails, roll back to .bak and log loud (same pattern as 7.7a). Non-fatal.
     Opt-out `AICODERMAP_NO_AA_AUTHORITATIVE=1`.
   - `audit-agent-misfiles.py` is advisory only — writes `data/_misfile-audit.json`
     with the AA-MEASURED moderate disagreements (plausible, not auto-corrected)
     for the next cycle's anomaly→research loop to verify against primary sources.

7.7. ANOMALY_RESOLUTION (auto-dispatch, 2026-05-27 — closes the Layer-3 loop):
   ```
   python scripts/detect-anomalies.py        # refresh the queue post-merge
   ```
   - If `data/_anomalies.json` has entries in the HIGH-PRIORITY classes
     (`source-mismatch`, `out-of-band`), the orchestrator
     dispatches ONE research sub-agent (`scope=anomaly-verify`, `model: "sonnet"`)
     with `idea_context.anomalies` = the top-N such cells. The agent applies
     agent.md rule 9 (OUTLIERS→INVESTIGATE) per cell — primary-source +
     exact-metric check — and writes `.aicodermap-anomaly-verdicts.json` with
     `confirm | reclassify | clear` verdicts (a simply-wrong VALUE is NOT
     verdicted; it is re-recorded as a normal observation so merge recomputes
     trustScore).
   - Orchestrator GATES, applies the mechanical verdicts, then re-audits with
     rollback (3.5 traceability gate, 2026-05-29):
     ```
     # GATE FIRST — reject any reclassify/confirm whose value is wrong-scale for
     # its target bench (band) or contradicts every shred of evidence for that
     # cell (envelope). --filter drops the bad verdicts so apply only runs safe
     # ones; the dropped ones are quarantined in data/_anomaly-verdict-traceability.json.
     python scripts/validate-anomaly-verdicts.py --filter
     # Snapshot for rollback (apply writes its own .bak, but capture pre-apply too)
     cp data/models.json data/models.json.preanomaly ; cp data/sources.json data/sources.json.preanomaly
     python scripts/apply-anomaly-verdicts.py     # confirm/reclassify/clear (filtered)
     # POST-APPLY AUDIT — if the coherence audit now FAILS (a verdict the gate's
     # band/envelope check could not foresee still broke an AC/MX invariant),
     # ROLL BACK to the pre-apply snapshot and log loudly; never ship a verdict
     # that breaks coherence.
     if ! python scripts/audit-data-coherence.py ; then
         mv data/models.json.preanomaly data/models.json
         mv data/sources.json.preanomaly data/sources.json
         echo "⚠ anomaly verdicts rolled back — post-apply audit failed" >> CHANGELOG.md
     else
         rm -f data/models.json.preanomaly data/sources.json.preanomaly
     fi
     # NO re-merge here (FIX 2026-06-06). apply-anomaly-verdicts already writes
     # coherent data/{models,sources}.json directly (clear removes bench+sources,
     # reclassify moves provenance) and the audit above is the SSOT gate. A
     # refresh-finalize re-merge would re-read .aicodermap-agent-out.json and
     # RE-FILL the cleared cells from the still-present artifact observations —
     # undoing the clear AND tripping merge.py's MX1 (the cleared cell is neither
     # a fill nor a gap in the live data). The clear/reclassify must be the FINAL
     # post-merge mutation; the audit-data-coherence.py call above already proved
     # coherence, so the cycle proceeds straight to git commit.
     ```
   - `single-source` AND `peer-outlier` anomalies are NOT auto-dispatched —
     they stay in `idea_context.anomalies` for the next full gather to pick up
     a 2nd source. `single-source` is a coverage signal (too many). `peer-outlier`
     was DEMOTED from auto-dispatch on 2026-06-07: the 2026-06-07 cycle measured
     22 peer-outlier verdicts → 17 confirm / 0 reclassify, i.e. ~100%
     confirm-as-legit. Peer-outlier is overwhelmingly a tier-grouping artifact
     (a 2026 reasoning model sitting far above its tier median, or genuine
     no-tools-vs-tooled benchmark variance) — NOT a misfile. Auto-dispatching it
     cost ~11 min of serial sonnet time for ~0 data change. The scale/metric
     errors a verify pass DOES catch live in `source-mismatch` (wrong-publisher
     Elo) + `out-of-band` (impossible value) — those two remain auto-dispatched.
     Advisory; never blocks. Opt-out `AICODERMAP_NO_ANOMALY_RESOLVE=1`. This is
     the automated form of the manual cfElo investigation (2026-05-27): an
     anomaly triggers RESEARCH, not rejection.

8. Render diff summary (markdown table) to user-visible output: models[].updates fields, newModels[], lineup changes (NEW/DEPRECATED/RENAMED/REMOVED), contradictions auto-resolved, coverage% achieved, partialCoverage flag.
9. AUTO-APPROVE — NO USER PROMPT. The workflow proceeds straight from Step 8 to Step 10. The only halt at this stage is schema-breaking discovery (a brand-new top-level field in a model entry not in the existing whitelist) — and even then, the unrecognized field is logged to gaps[] and merge continues with the recognized fields. RED contradictions are already auto-resolved at Step 7. REMOVED entries are auto-archived per LIFECYCLE_STATES.

9b. SSOT_COHERENCE_AUDIT (scripts/audit-data-coherence.py — runs inside merge.py post-write):
    Verifies every surface that mirrors a SSOT set is still aligned:
    - assets/js/core.js BENCH_KEYS == data/sources-whitelist.json _schema.coreBenchKeys
    - i18n/{tr,en}.json benchmarks.* keys == BENCH_KEYS (label sets identical)
    - DEFAULT_WEIGHTS / PRESETS keys ⊆ BENCH_KEYS
    - data/models.json bench cells use only canonical keys
    - data/sources.json keys reference only known model IDs and canonical bench keys
    - tier values ∈ {frontier, open-flagship, coder-specialized, gemma, ollama-local}
    - status values ∈ {active, deprecated, archived}
    - **benchAliases ⇄ extraction-regex (4.1):** also run
      `python scripts/gen-bench-keys.py --check-regex-drift` in this step — it
      exits 1 when `_schema.regexLibrary.patterns.bench_score_labeled` references
      a bench name no longer grounded in `_schema.benchAliases` (a rename/removal
      the regex didn't follow, e.g. the retired `Aider` token caught 2026-05-29).
      Treat a non-zero exit as a coherence HARD BLOCK like the rows above.
    **HARD BLOCK** — drift is a single explicit exception to the UNCAPPED "never block"
    doctrine. On audit failure, merge.py rolls data/{models,sources}.json back to their
    .bak snapshots and exits non-zero. No CHANGELOG entry is written, the artifact is
    NOT committed, and the skill workflow halts at this step. The user must fix the
    drift in `.aicodermap-agent-out.json` (or the underlying SSOT files) and re-run the
    merge before any commit can proceed. The same audit is wired into the
    `scripts/hooks/pre-commit` hook (installed via `bash scripts/install-hooks.sh`),
    so any commit path — manual, scripted, or skill-driven — is gated. Override is
    `git commit --no-verify` and only acceptable for documented emergencies.

10. ATOMIC WRITE — schema-complete merge per MERGE_RULES (rotated .bak backup):

    **FAZ 7.E (2026-05-10) — single-script finalize wrapper:**
    ```
    python scripts/refresh-finalize.py
    ```
    Combines the previously-separate `gen_unified_artifact.py` + `.aicodermap-gap-gen.py` + `merge.py` calls into ONE process invocation. Each underlying script is unchanged (idempotent + same logic); the wrapper saves 2 redundant Python interpreter spawns + 2 file load/parse cycles. Failure of any inner step propagates exit code; merge.py's audit (SSOT coherence + MX1 invariant) still gates the commit. Use `--skip-merge` for dry-run preview.

    Outputs (unchanged from per-script behavior):
    - data/models.json (multi-provider pricing array, subscription array, status field, full bench, ollama, unslothVariants, etc.)
    - data/sources.json (append sourcesAdded[] + every contradiction's losing candidate, dedup by (key, url, value), include trustScore per entry)
    - i18n/{tr,en}.json (merge i18nUpdates into models[id]={strengths,weaknesses})
    - data/archive/<id>.json (when REMOVED from vendor lineup past grace period)
    - lastUpdated := now (ISO 8601 UTC, "YYYY-MM-DDTHH:MM:SSZ") per touched entry only — same-day reruns disambiguate by wallclock time
11. Append CHANGELOG.md (Keep a Changelog):
    ## [Unreleased] / ### Updated|Added|Deprecated|Removed|Flagged
    If agent emitted Phase 0b/0c discovery candidates, append:
    "🔎 New vendor candidates: N (review queue)" and/or
    "🔎 New benchmark candidates: M (review queue)"

11a. CYCLE_TELEMETRY (FAZ 2.4, 2026-05-07) — **MANDATORY every refresh-all/model cycle; do NOT skip:**
    Without it the batch auto-tune (below) starves — the 2026-06-07 cycle ran with
    the last telemetry file dated 2026-05-28 because this step was silently skipped.
    Inject `_batchId` + `_wallclockSec` (from the dispatch wall-clock measurements)
    into each artifact BEFORE aggregating, then write — even on partial/failed cycles.
    ```
    from lib.telemetry import aggregate_per_batch_telemetry, write_cycle_telemetry
    # IMPORTANT: orchestrator MUST inject `_batchId` (and ideally `_wallclockSec`,
    # `_startedAt`, `_endedAt`) into each artifact dict before passing to the
    # aggregator. Agent JSON output may omit these; orchestrator derives them
    # from the artifact filename (`.aicodermap-agent-out-<batchId>.json`)
    # and the dispatch wallclock measurements:
    #   for art, batch_id in artifact_pairs:
    #     art["_batchId"] = batch_id
    #     art["_wallclockSec"] = dispatch_timings[batch_id].sec
    telemetry = aggregate_per_batch_telemetry(per_batch_artifacts)
    write_cycle_telemetry(today_ymd, telemetry)
    ```
    Writes `data/_telemetry/<YYYY-MM-DD>.json` with per-batch wallclock,
    tool-call counts, fills/gaps/na, partialReason, and cycle-level totals
    (max + p95 wallclock, toolCallSum, zeroFillBatches list).
    The next cycle's orchestrator MAY read this to auto-tune
    `dispatch.MAX_BATCH_MODELS` (e.g., shrink batch size if p95 wallclock
    spent > 540s, expand if p95 < 300s and fills/batch averaged < 80).
    Auto-tune is opt-in; default behavior is "log telemetry, do not adjust".
    Telemetry write is non-fatal — failure logs WARN + CONTINUE.

11b. Ensure git hooks installed (idempotent):
    bash scripts/install-hooks.sh
12. AUTO-EXECUTE git (no user prompt):
    git add data/ i18n/ CHANGELOG.md scripts/ .claude/skills/aicodermap/SKILL.md .claude/agents/aicodermap-research-agent.md
    git commit -m "data: <generated description>"
    git push
    On hook failure: fix root cause + new commit (NEVER --amend, NEVER --no-verify)
    On push conflict (only halt path in entire workflow): prompt user "git pull --rebase first" — this is the sole user-blocking step because remote-state reconciliation is genuinely outside skill authority.
13. Sleep DEPLOY_WAIT_SEC (90s)
14. Run `python scripts/verify-deploy.py` (added 2026-05-06). Three nested checks in one binary:
      (a) GitHub commits API confirms `origin/main` HEAD == local HEAD
      (b) Pages-served `data/models.json` ETag rotated vs `data/_meta.json.prevPushEtag`
      (c) Served `data/_meta.json` `modelCount` + `benchKeyCount` match local
    Exit 0 → "✓ DEPLOY VERIFIED", workflow complete.
    Exit 1 → log "DEPLOY VERIFICATION FAILED" + last error to CHANGELOG (cycle still considered closed; next cycle will re-push), surface URL + GitHub status link.
    Exit 2 → tooling/network unavailable → log "DEPLOY VERIFICATION UNAVAILABLE", do not flag failure.
    The script handles its own retry budget (60s warm-up + 3 × 30s retries, ~2.5 min total). Skill MUST NOT skip this step on `refresh-all`; on partial-scope refresh the script also runs (cheap, idempotent).
```

## CONSTANTS

Single source of truth: `scripts/lib/constants.py`. Runtime values fetch from
`data/sources-whitelist.json._schema.contracts` via `lib/whitelist.contracts()`,
falling back to `constants.py` defaults. SKILL.md, agent.md, and merge.py
reference the module — never duplicate values.

UNCAPPED applies to RESEARCH QUALITY (which sources to attempt, fallback
chains, gap fabrication policy). Per-dispatch resource budgets remain HARD:
`AGENT_BUDGET_BUFFER` and `BATCH_WALLCLOCK_SEC` enforce themselves; when
either fires, agent emits + `partialReason`. Next cycle re-attempts unfilled
cells (gaps[] preserved across cycles).

Termination — all four MUST hold before agent emits final JSON:
1. Every `leaderboards[]` entry visited (200+extract OR unreachable+fallback
   exhausted OR `_runtime.unhealthy` auto-skip).
2. Every vendor with perModelUrl/modelCardUrl/postUrl attempted per model.
3. Every cell in `target_model_ids × coreBenchKeys` attempted — the WHOLE slice,
   not just priorityCells. Under FAZ 4.A priorityCells is ORDERING-only (resolve
   first), NOT the scope; `require_full_matrix:true` makes the full slice the
   termination target. (Superseded the FAZ 2.3 "authoritative work list" reading,
   which let agents stop after ~11 priority cells/batch — see PRELIM ctx note.)
4. Every still-empty cell carries a gaps[] entry; advisory GAP_VALIDITY_GATE
   surfaces low-effort suspicions but REPAIRS rather than strips entries (3.3).

## SILENT_FAIL_PREVENTION (loud failures + auto-recovery, halts only at git push conflict)

| Step | Success criterion | On failure (auto-recovery, never user prompt unless noted) |
|------|-------------------|------------------------------------------------------------|
| 0 Lineup discovery | **Per-vendor:** EVERY `sourcesWhitelist.vendors` id appears as a key in `lineup` AND has a non-empty `active[]` OR a loud `gaps[]` `lineup:<vendor>: empty`. (Global "≥10 parsed" is NOT sufficient — a globally-non-empty lineup that silently drops a broken vendor is a failure.) | Compute the set of vendors with empty/missing `active[]` (NOT global-empty). For EACH such vendor → dispatch ONE retry agent restricted to Step 0 scoped to that vendor (forces the agent.md step-1 per-vendor WebSearch fallback). Still empty after retry → log `gaps[]` `lineup:<vendor>: empty` and CONTINUE. Unreachable vendors → also `lineup:<vendor>: unreachable`. Never block on stale lineup; never drop a vendor silently. |
| 0b Source health check | `runtime.healthChecks` covers ≥3 leaderboard domains with status entries | If <3 domains → dispatch retry agent restricted to PRELIM SOURCE_HEALTH_CHECK. On second-cycle <3: log `gaps[]` entry `health-check:incomplete` and CONTINUE. |
| 0c Leaderboard prefetch | `data/.leaderboard-snapshots/_index.json` exists AND `_meta.totalSucceeded ≥ 0.5×totalAttempted` | FAZ 2.1 (2026-05-07): non-fatal. Each agent independently falls back to WebFetch for any URL absent from `idea_context.leaderboardSnapshots`. Prefetch is a wallclock optimization, not a correctness gate. If `prefetch-leaderboards.py` exits non-zero → log warning + CONTINUE without `leaderboardSnapshots` map. |
| 4 Agent survey | `.aicodermap-agent-out-<batchId>.json` exists and parses; `models[]+newModels[]` ≥ FAMILY_BASELINE_MIN OR explicit gaps[] | (1) agent-written file primary; (2) FALLBACK A: `extract-agent-output.py` against subagent jsonl; (3) FALLBACK B: persisted tool-result extraction; (4) on all-3 failure: log to `~/.aicodermap-debug.log` + CONTINUE merge with available data. Family-count shortfall logged to gaps[], never halts. |
| 4w Wallclock cap | Every batch returns within BATCH_WALLCLOCK_SEC (600s) | FAZ 1.3 (2026-05-07): orchestrator wraps each Agent call with `subprocess.run(timeout=BATCH_WALLCLOCK_SEC)`. On timeout: SIGKILL the agent, attempt Read of partial-written `.aicodermap-agent-out-<batchId>.json`. If file exists with valid JSON head → use it, set `partialReason:{code:'timeout', wallclockSec:BATCH_WALLCLOCK_SEC}`. If file missing/corrupt → emit empty stub `{batchId, models:[], gaps:[], partialReason:{code:'timeout-no-write'}}` and CONTINUE to next wave. Never block on a single batch's timeout. |
| 4d Wave dispatch completeness | All `plan["waves"]` indices present in `wave_state.completed` | FAZ 1.1 (2026-05-07): hard guard at end of Step 4 wave loop. If incomplete → `halt_workflow()` BEFORE Step 5. gap-gen would mask missing waves as auto-gaps; that pattern slipped the 2026-05-06 partial commit through. SOLE non-push halt path. |
| 4s Synth traceability gate | Every non-null `updates.bench[k]` in `.aicodermap-agent-out-synth.json` lies within its cell's evidence envelope (fresh gather obs ∪ historical sources.json) | 2026-05-28: `validate-synth-traceability.py --auto-fallback` runs after Stage B, before gen_unified. On FABRICATION (value outside envelope / zero evidence — the Stage-B sonnet synth hallucinated 68 such values in the 2026-05-28 cycle) → auto-regenerate the artifact via deterministic `local-synth.py` (cannot hallucinate) + re-validate. If fallback also dirty → loud CHANGELOG warn + CONTINUE (merge.py MX/anomaly audits backstop). `divergences[]` (grounded but disagree with fresh obs > CONTRADICTION_WARN_PP) are advisory → feed Step 7.7 anomaly→research loop, never block. |
| 7.7a Anomaly verdict gate | Every `reclassify`/`confirm` verdict in `.aicodermap-anomaly-verdicts.json` is traceable: moved value within the TARGET bench's hard band (scale guard) AND its evidence envelope (fresh ∪ historical) | 2026-05-29: `validate-anomaly-verdicts.py --filter` runs BEFORE `apply-anomaly-verdicts.py`. A reclassify into a wrong-scale bench (e.g. cfElo 3052 → sweV's 0-100) or a confirm contradicting all evidence is dropped (quarantined in `data/_anomaly-verdict-traceability.json`); apply runs only the safe verdicts. Post-apply `audit-data-coherence.py` failure → ROLL BACK to the pre-apply snapshot + loud CHANGELOG warn. Never ship a verdict that breaks coherence. |
| 6 Coverage log | `validationCoverage` is a number 0..1 in artifact | Below COVERAGE_TARGET (0.85): set artifact.partialCoverage=true, append "⚠ cumulative provenance coverage" line to CHANGELOG, CONTINUE. Below COVERAGE_HARD_BLOCK (0.50): louder warning, still CONTINUE. No deep-fetch loop (retired 2026-04-28) — agent already walks every cell every cycle. |
| 7 Contradiction auto-resolve | Every contradiction has autoResolveWinner | TrustScore ties within 0.05 with no I-tier present: prefer most-recent value, then most-verified, then alphabetical-by-source as deterministic tiebreaker — never user prompt |
| 10 Atomic write | `data/{models,sources}.json` parse-valid + self-check passes | On parse failure: restore from `.bak` + log root cause + retry the merge once with relaxed self-check. On second failure: write the artifact's known-good fields only, mark unhealable fields in gaps[]. CONTINUE — never leave repo in restored-only state |
| 12 git push | Exit code 0 AND remote ref advanced | On hook fail: fix root cause + new commit (NEVER --amend, NEVER --no-verify). On push conflict: SOLE USER-BLOCKING step — print "git pull --rebase first" and exit cleanly so user can resolve. This is the only halt in the entire workflow because remote state is genuinely outside skill authority |
| 14 Live deploy verify | `curl <live_url>/data/models.json` returns 200 AND parses as JSON | Wait + retry up to 5min. On still-not-live: log warning + declare workflow done (commit was successful; Pages will eventually catch up). Never halt on Pages latency |

**Cardinal rule (revised):** the workflow ALWAYS reaches Step 12 (git push) as long as Step 0+4 produced any usable JSON. Halts above Step 12 are eliminated by design. The artifact's machine-checkable flags (`partialCoverage`, `error`, `gaps[]`, `runtime.fabricatedSuspicions[]`) record what was incomplete so the next cycle picks it up.

## VENDOR_LINEUP_SOURCES (Step 0 — official "what models exist now")

The vendor URL list is canonical in **`data/sources-whitelist.json`** under `vendors.<vendor>.urls.lineup`. Every entry there with a `lineup` URL is fetched on `refresh-all` and `lineup-sync`.

The skill iterates `sourcesWhitelist.vendors` and dispatches one parallel fetch per vendor.lineup URL. New vendors are added by editing `data/sources-whitelist.json` only — never by editing this spec.

Lineup return shape (per vendor):
```json
{
  "<vendorId>": {
    "active": [{ "id": "<official-id>", "name": "...", "released": "YYYY-MM-DD", "context": <int>, "open": <bool> }],
    "deprecated": [{ "id": "...", "deprecationDate": "YYYY-MM-DD", "successor": "<id>?" }],
    "renamed": [{ "from": "<old-id>", "to": "<new-id>", "evidenceUrl": "..." }]
  }
}
```

## TRUST_SCORE_FORMULA (used by Step 7 auto-resolution + every sources.json entry)

```
trustScore(obs) = tierWeight × verif_factor(v) × reliability(s, b) × recencyDecay(date, type)

tierWeight:
  I = 1.0   (independent leaderboard: Scale SEAL, SWE-bench Verified, Terminal-Bench, Aider, tau-bench, MCP-Atlas, Artificial Analysis, Vellum, livecodebench.com, lmarena.ai, livebench.ai, BFCL, BigCodeBench, EvalPlus, paperswithcode.com, BenchLM, Open LLM Leaderboard, swebench.com)
  S = 0.7   (vendor self-report: official blog, docs, model card, technical report)
  C = 0.4   (community/3rd-party: aggregator blog, walkthrough, review)
  U = 0.1   (forum/social: Reddit, Twitter — never written to data, only as cross-check signal)

verif_factor(v)        — Phase R2 (replaced linear min(v,3)/3)
  = min(log(1+v)/log(4), 1.5)
  v=1 → 0.50  v=3 → 1.00  v=5 → 1.29  v≥10 → 1.50 (capped)

reliability(s, b)      — Phase R3 (per-(source, bench) Beta-Binomial posterior)
  = (1 + decayedAgree) / (2 + decayedAgree + decayedDisagree)   if n(s,b) ≥ 10
  = global posterior of source                                  if n(s)  ≥ 10
  = 1.0                                                         else (cold-start neutral)

recencyDecay(date, type) — Phase R5 (per-source-type curve)
  default:   <30d=1.00  <90d=0.85  <180d=0.70  <365d=0.50  else 0.30
  quarterly: <30d=1.00  <90d=0.95  <180d=0.85  <365d=0.60  else 0.30
  weekly:    <30d=0.80  <90d=0.40  <180d=0.10  else 0.00
  (vendor whitelist supplies `vendorUpdateInterval` per source)

Exceptional single-source override — Phase R4
  bypasses _single_outlier_guard when a single I-tier observation satisfies
  all of: n(s,b) ≥ 20, posterior accuracy ≥ 0.90, recency_decay ≥ 0.85
  override_mode = "exceptional-source-override"

Tiebreak (when trustScores within 0.05): prefer I-tier, then most recent, then highest verifications.

Variant-ambiguity penalty (4.4): an observation tagged `_variantAmbiguous` (a bare
"SWE-bench" with no Verified/Pro/Multilingual qualifier) → trustScore = max(0,
trustScore − 0.5). merge.py enforces this at ingestion and records the cell in
`runtime.variantAmbiguous[]`; detect-anomalies.py surfaces it as an anomaly.
```

**Application:**
- Every entry in `data/sources.json` MUST carry a `trustScore` field (computed at write time).
- For multi-source same-value cluster: aggregate verifications, take the max recency.
- For multi-source disagreement (a contradiction): each candidate gets its own trustScore; winner has max(trustScore).

**FAZ 8.A.3b refinements (2026-05-18):**
- `I_TIER_MIN_VERIFICATIONS = 2`: a single fresh I-tier observation
  (verifications < 2) **cannot** override an existing multi-source S-tier
  consensus. The independent-override rule still fires when ≥2 distinct
  I-tier sources exist or average I-tier trust ≥ 0.6 — but single-shot
  outliers are quarantined for the next cycle instead of immediately
  promoted.
- **Pseudo-source exclusion**: observations whose `source` ∈
  `{snapshot-extraction, auto-resolution candidate, synth-backfill}` are
  filtered out of clustering before pick_winner runs. They survive in
  the artifact for audit but never anchor consensus. `effective_trust_score(..., is_pseudo=True)`
  multiplies their weight by 0.2 when used as last-evidence rescue
  entries (FAZ 3a purge already removed historical pseudo entries).
- **Cell confidence + quarantine**: `pick_winner` returns
  `{confidence, quarantine, bayesianPoint}` on every result. Frontend
  `compositeScore` weights each cell by confidence; quarantined cells
  are excluded entirely.

## PRICING_SCHEMA (multi-provider array — replaces flat numbers)

```json
{
  "pricing": {
    "api": [
      {
        "provider": "<official|openrouter|together|fireworks|deepinfra|groq|cerebras|...>",
        "in": <number $/1M>,
        "out": <number $/1M>,
        "cacheHit": <number $/1M | null>,
        "throughput": <number tok/s | null>,
        "url": "<source url>",
        "fetched": "YYYY-MM-DD"
      }
    ],
    "range": {
      "in":  [<min>, <max>],            // computed from api[]
      "out": [<min>, <max>],
      "cacheHit": [<min>, <max>] | null
    },
    "subscription": [
      {
        "tier": "Free|Plus|Pro|Team|Enterprise|Max|Coding|...",
        "price": <number>,
        "currency": "USD",
        "billing": "monthly|annual",
        "notes": "..."
      }
    ]
  }
}
```

**UI rendering rules:**
- **Card view:** show `pricing.api[]` as a per-provider list (provider name + price + url chip).
- **Table view:** show `pricing.range.in` / `pricing.range.out` as `$<min>–$<max>` (or single number if min==max).
- **Sort by price:** sort by `pricing.range.in[0]` (cheapest input price).
- **Subscription:** card shows lowest paid tier + a "see all tiers" expandable.

**Schema enforcement:** `pricing.api` is always an array, `pricing.subscription` is always an array, `pricing.range` is computed from `api[]` at write time. Any other shape is a contract violation that the SSOT audit (step 9b) blocks via hard rollback. There is no legacy-shape handling.

## LIFECYCLE_STATES (deprecated/active/archived handling per #2A)

Every model carries a `status` field:

| Status | When set | UI behavior | Survey behavior |
|--------|----------|-------------|-----------------|
| `active` | Default; vendor lineup includes it | Normal rendering | Full bench/pricing refresh every cycle |
| `deprecated` | Vendor lineup explicitly marks it deprecated OR vendor has named a successor and grace period started | Gray-out, "⚠ Deprecated <date>" badge, sortable but visually de-emphasized; tooltip points to successor | Pricing/availability refresh only (no bench re-survey unless user requests) |
| `archived` | Vendor removed from lineup AND > DEPRECATION_GRACE_DAYS (60d) since deprecation | Hidden by default; visible only via "Show archived" filter | Skip in refresh; data/archive/<id>.json holds full last-known snapshot |

**Transition rules (auto, no user prompt):**
- `active` → `deprecated`: when Step 0 lineup marks deprecated. Set `deprecatedAt: today`, `successor: <id>?` from vendor announcement.
- `deprecated` → `archived`: when `today - deprecatedAt > DEPRECATION_GRACE_DAYS`. Move full entry to `data/archive/<id>.json`, leave only stub `{ id, name, status:"archived", archivedAt, deprecatedAt }` in main models.json.
- `deprecated` → `active`: when vendor re-lists. Restore from main entry, clear `deprecatedAt`.
- `archived` → `active`: never automatic; requires manual `/aicodermap restore <id>`.

## WRONG_ID_AUTO_FIX (handles cases like devstral-medium holding Devstral Small 2 data)

When Step 0 lineup discovery flags an `id` mismatch (current data carries wrong-canonical id):

```
1. Verify with ≥2 vendor-official sources that the official id differs from current data id
2. If verified:
   a. Move current entry to data/archive/<old-id>.json
   b. Create new entry with official id, populate from current data + lineup info
   c. Append rename to data/sources.json: { "key": "rename:<old-id>→<new-id>", "evidence": [<urls>], "date": today }
   d. Append to CHANGELOG: "### Renamed\n- `<old-id>` → `<new-id>` (vendor canonical, evidence: <url>)"
3. If single-source-only (cannot verify): emit `gaps[]` entry, leave id unchanged, surface in diff for user awareness
```

User is NOT prompted for the rename. Default is auto-execute when verified ≥2 sources.

## DATA_CONTRACT (canonical — agent ⇄ skill ⇄ data ⇄ frontend)

Single source of truth for the unified shape between every layer. Mirrored verbatim in `.claude/agents/aicodermap-research-agent.md → DATA_CONTRACT`. Updates to either file MUST update both.

| Layer        | File / channel        | Shape                                                                                                                         |
|--------------|-----------------------|-------------------------------------------------------------------------------------------------------------------------------|
| **Storage**  | `data/models.json`    | Flat scalars. `bench.<key>` = number, `context` = number, `pricing.api[].in/out/cacheHit/throughput` = number. `privacy.<field>` = canonical value (see AC11). NO `{value, trustScore}` wrappers. |
| **Provenance** | `data/sources.json` | Wrapped: `{value, source, url, tier, date, verifications, trustScore, contradictionRole?}`. Sole on-disk home of `trustScore`. |
| **Transit**  | agent → skill JSON    | `models[].updates.<field>` = Storage shape; `models[].sourcesAdded[]` = Provenance shape; `privacyObs[]` = independent gather array (top-level, NOT under models[]); NEVER cross-mix. |
| **Verification** | `.aicodermap-verification-map.json` (gitignored) | **Cross-cycle cache:** `cells.<modelId>.<benchKey> = {value, verifications[], confirmed, lastChecked}`. Skill reads at cycle start (skip confirmed cells), updates post-merge from sourcesAdded[]. NOT a render input — purely orchestrator state. |
| **Render**   | `assets/js/render-card.js` + `render-table.js` | Reads Storage scalars; looks up Provenance for tooltips by `<modelId>.<field>`. Entry: `assets/js/main.js` (ES module). |

Contradictions: `field` = **bare** bench key (`swePro`, never `bench.swePro`); `candidates[]` wrapped; `autoResolveWinner` wrapped dict — skill extracts `.value` for Storage, keeps full dict for Provenance.

**Enforcement** (3 layers):
1. Agent self-check before emit (Storage-shape validation on every `updates.bench.<k>`)
2. `scripts/audit-data-coherence.py` post-merge (HARD BLOCK + .bak rollback if any drift; pre-commit hook re-runs the audit so even manual commits can't introduce a contract violation)
3. `scripts/verification-map.py update` post-merge (rebuilds verification cells from sourcesAdded[]; computes `confirmed` flag per VERIFICATION_AGREEMENT_PP rule)

A wrapper-shaped value in storage is no longer "graceful-unwrapped" — it fails the audit and rolls the merge back. The verification map is the cross-cycle persistence layer used for contradiction analysis (audit-only; never reads for skip decisions).

## MERGE_RULES

**Why this section exists:** prior runs lost data because the merge step only touched `bench`/`pricing`/`provider`/`license`. Sparse fields (`vramRequirement`, `ollamaSize`, `pricing.api.cacheHit`, `uptime`, `subscription`) were silently skipped. Never again.

### A. Single-artifact policy (replaces prior multi-artifact reconciliation)

There is ONE artifact: `.aicodermap-agent-out.json` (gitignored). Every agent run overwrites it. No multi-artifact reconciliation, no numbered suffixes.

Reconciliation against the FILE SYSTEM (`data/models.json`) replaces the prior multi-artifact dance:
- Existing values in `data/models.json` are preserved unless the current run has a higher-trustScore replacement
- A field that was non-null before but is null in the current return is NOT cleared — it stays. Additionally, the field's `(modelId, field)` key is added to a deep-fetch retry queue: the next cycle MUST attempt to re-find that value from a different source. Existing data is never silently lost.

### B. Per-field merge policy (priority order, top wins)

For every `(modelId, field)` pair, walk this priority list and apply the first non-null value found:

```
1. Step 7 contradiction-auto-resolved value (winner via trustScore)
2. Highest-trustScore source from current run's sourcesAdded[]
3. Current run's models[].updates value (when no contradiction)
4. Prior artifact value (recover any field the current run omitted)
5. Existing data/models.json value (preserve)
```

### C. Field whitelist (every refresh MUST iterate ALL of these)

```
SCALAR FIELDS:    name, provider, released, tier, status, deprecatedAt, archivedAt, successor,
                  open, license, context, providers, uptime, vramRequirement, ollamaSize,
                  strengthsKey, weaknessesKey

ARRAY FIELDS (NEW SCHEMA):
                  pricing.api[]            (per-provider {provider, in, out, cacheHit, throughput, url, fetched})
                  pricing.subscription[]   (per-tier {tier, price, currency, billing, notes})
                  unslothVariants[]        (replace if new has ≥ existing length)

COMPUTED FIELDS:  pricing.range            (computed from pricing.api[] at write time)

OBJECT FIELDS:    ollama (full pullCmd/tags/pullCount/architecture/parameters/license/releasedISO/ollamaUrl block — preserve atomically; replace only if new object has more keys)
                  privacy (per-field dict merge: {trainingDataOptOut, dataResidency[], soc2, gdpr, apiLogging}. synth's _build_privacy_block clusters by (modelId, field) and picks highest-tier observation (I > S > C) with most-recent fetched as tiebreak. I-tier audit registry overrides S-tier vendor self-report; sources in data/sources-whitelist.json `complianceAggregators[]` + vendor-discovered `urls.privacy`/`urls.trust`. Canonical values enforced by audit-data-coherence.py AC11 — drift → merge rollback.)

BENCH KEYS (dynamic universe = whitelist `_schema.coreBenchKeys` ∪ `_schema.emergingBenchKeys`):
                  DO NOT hardcode the list here — it drifts (the retired
                  simpleQa/tau3/programBench snapshot hard-blocked merge on
                  2026-05-30). SOLE SSOT = data/sources-whitelist.json
                  `_schema.coreBenchKeys` (currently 17, includes mrcr) ∪
                  `_schema.emergingBenchKeys` (currently 12). Stub builders +
                  audit + agent all derive from there; the set extends
                  automatically when a leaderboard's publishes[] adds a key.
                  → trustScore-driven contradiction resolution per bench key
```

A field whose current value is `null`, `undefined`, `"?"`, or `"Unknown"` is treated as **empty** for fill purposes. Any artifact value beats empty.

### D. Pricing array merge

When current run returns `pricing.api[]` for a model:
- For each new entry, dedupe by `provider` against existing array
- If `provider` matches: replace if new `fetched` date is newer, OR if new `in/out/cacheHit` differ AND new is from higher-tier source
- Append new providers as new array elements
- Recompute `pricing.range` after merge

Same dedupe-by-tier-name discipline for `pricing.subscription[]`.

### E. Provenance (data/sources.json)

After the field merge, every value in `data/models.json` must have at least one matching entry in `data/sources.json[<modelId>.<field>]` with computed `trustScore`. Contradiction losers are also written so the UI can surface "alternate-source" indicators.

### F. lastUpdated discipline

Touch `lastUpdated := now` (ISO 8601 UTC datetime, e.g. `2026-04-28T17:23:45Z`) ONLY on models that gained at least one new field value during merge. Wallclock-precision so multiple same-day reruns are distinguishable in the UI sort + provenance audit. Frontend renders via `fmtLastUpdated()` (assets/js/data.js) as `YYYY-MM-DD HH:MM` for compact display while the raw ISO string remains the sort key.

### G. Backup rotation

```
data/models.json     → data/models.json.bak (most recent prior)
data/models.json.bak → data/models.json.bak2 (the one before that)
```

Same for `data/sources.json` and `i18n/*.json`. Two layers of `.bak`. Both gitignored via `*.bak`.

### H. Self-check (BEFORE prompting the user to git commit)

```
for each model in data/models.json:
  for each field in (whitelist above):
    if field is null AND any artifact has a non-null value:
      → MERGE BUG. Halt, log model+field+artifact path, prompt user.
  validate pricing.api is an array — fail merge if not
  validate pricing.subscription is an array — fail merge if not
  validate pricing.range is computed and matches min/max of pricing.api[]
  validate every (model, bench) value has a sources.json entry with trustScore
  validate status is one of {active, deprecated, archived}
```

A passing self-check is the gate for printing git commands at Step 12.

## ERRORS

Per-step error handling lives in **SILENT_FAIL_PREVENTION** above (single source). Cross-cutting failure modes not tied to a specific step — all auto-recovered, never deal-breakers:

| Condition | Action |
|-----------|--------|
| Agent return invalid JSON | log to `~/.aicodermap-debug.log`, retry 1× with stricter delivery contract; on second fail extract any recoverable fragment via regex `\{.*\}` + CONTINUE with what's recoverable + log uncovered models to gaps[] |
| `refresh-all` family count < `FAMILY_BASELINE_MIN` | log shortfall to gaps[] with `family:<name>: undersampled`, CONTINUE merge — orchestrator does NOT re-run; next refresh re-attempts |
| Step 9 (no longer interactive) | n/a — Step 9 is auto-approve; no decline path |
| Git push conflict | SOLE user-blocking exception: print "git pull --rebase first" once and exit cleanly (do NOT force-push). User resolves remote state and re-runs `/aicodermap`. |

## OUTPUT_TEMPLATE_SUCCESS
```
🚀 AICoderMap update | scope:<scope> | last_refresh:<n>d ago (M5 ≤14d ✓)
📋 Lineup sync: <new>+<deprecated>+<renamed>+<removed>
🤖 Agent → sonnet | parallel:5 | budget:6×90s/model | cycle:<n>/5

✓ Return: confidence:<HIGH|MED|LOW> | <n_updated> updated | <n_new> new
          | <n_resolved> contradictions auto-resolved | coverage:<%>

📋 Diff:
  <model_id>:
    <field>: <old> → <new> (Δ <delta>) [trust=<score>]
  <new_model_id> (NEW): <summary>
  <deprecated_id> (DEPRECATED): successor=<id?>
  <renamed_id> (RENAMED): <old> → <new>

✓ Wrote: data/models.json (<n>upd+<n>add+<n>renamed+<n>deprecated)
✓ Wrote: data/sources.json (<n> entries)
✓ Wrote: i18n/{tr,en}.json (<n> entries)
✓ Appended: CHANGELOG.md

✓ Pushed: <commit-hash> → main
⏳ Pages deploy ~90s...
✓ Live: <url> | M5: <n>d ago (≤14d ✓)
```

## SUBCOMMANDS

| Arg | Action |
|-----|--------|
| `lineup-sync` | Phase 0 only — vendor diff (NEW/DEPRECATED/RENAMED/REMOVED) without bench/pricing survey |
| `validate` (no fetch) | Read `data/sources.json` → compute coverage + list contradictions + stale entries |
| `stale-check` | List `data/models.json` entries with `today - lastUpdated > STALE_DAYS` |
| `changelog` | tail -50 CHANGELOG.md → last 5 release entries |

## INVARIANTS

- **Procedure vs data:** spec files carry HOW; data files carry WHAT. URLs, IDs, format keys, regex patterns live in `data/sources-whitelist.json._schema.{formatTaxonomy, extractors, regexLibrary}`. Spec never hardcodes them.
- **Autonomous-by-default:** orchestrator+agent iterate, retry, fall back, emit gap[]; SOLE user-blocking exception is git push conflict.
- **Loud failures + auto-recovery:** every step has explicit success criterion (see SILENT_FAIL_PREVENTION). Failures emit log + gap[] + CONTINUE.
- **Partial-coverage merges normal:** never block write/commit/push on low coverage.
- **No GitHub Actions / CI / workflows** (manual orchestration is the contract).
- **M5 ≤14-day freshness gate.**
- **Project-scoped:** skill + agent only in `D:\GitHub\aicodermap\` session.
- **Explicit `model: "sonnet"` on every Agent() dispatch (HARD):** orchestrator MUST pass the `model` parameter explicitly on EVERY `aicodermap-research-agent` call — gather, synth, lineup-retry, health-check-retry, 0-fill-retry. Omitting it causes the subagent to inherit the parent's model (Opus) at ~60x cost per call. The pre-tool-use hook surfaces this mistake; treat its warning as a HARD STOP — kill the agents and re-dispatch with `model: "sonnet"`. Synth higher-budget exception still uses `sonnet` (FAZ 4.C); no dispatch path in this spec routes to opus or haiku.
- **Explicit `wallclock_deadline_unix` in EVERY gather/anomaly prompt (HARD, 2026-06-07):** the dispatch contract's `wallclock_deadline_unix: now() + BATCH_WALLCLOCK_SEC` is the ONLY wallclock enforcement — there is NO orchestrator SIGKILL/subprocess timeout on the Agent-tool path. If the orchestrator omits the deadline string from the actual prompt (not just the pseudo-code), the agent runs uncapped and the slowest batch sets the whole wave's wall-clock. The 2026-06-07 cycle proved this: deadline omitted → batch06 ran 1023s vs a 600s target, making Stage A 17 min instead of ~10. Every `aicodermap-research-agent` gather/anomaly prompt MUST literally carry the computed epoch deadline + the instruction to hard-stop at `deadline-30`. agent.md enforces the self-stop; the orchestrator MUST supply the number.
- **`sourcesAdded[].key` canonical form (HARD):** every Provenance-shape entry written by the agent OR post-hoc patched by the orchestrator MUST use `key: "<modelId>.<benchKey>"` (e.g., `"opus-4-7.sweV"`). Forms like `"bench.swePro"` (canonical-bench-prefix) or `"sweV"` (bare key) are contract violations — they cause `sources.json` to nest entries under `"bench.swePro"` as if it were a modelId, which MX-audit then flags as "unknown model id" and rolls the merge back. `gen_unified_artifact.py` is the SSOT for this format; any pipeline outside it that writes `sourcesAdded[]` (e.g., recovery patches) MUST mirror the same scheme.
