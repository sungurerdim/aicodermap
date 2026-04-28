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
| `refresh-all` | full (lineup + bench + pricing + local) | sonnet | 4-7min |
| `lineup-sync` | vendor lineup discovery only (Step 0) | sonnet | 1-2min |
| `model <id>` | specific | sonnet | 1-2min |
| `new-release` | new-release detection | sonnet | 2-3min |
| `validate` | (no fetch) | — | <10s |
| `stale-check` | (no fetch) | — | <5s |
| `changelog` | (no fetch) | — | <5s |

**`refresh-all` baseline:** Agent's `MODEL_FAMILIES` table is non-negotiable — every family must be surveyed, missing ones emit a `gaps[]` entry. Skill rejects returns whose `models[]` + `newModels[]` cardinality < 30 unless agent explains via `gaps[]`.

## WORKFLOW
```
PRELIM. SOURCE_HEALTH_CHECK (auto, every refresh — now format-aware):
   - Skill instructs agent to run quick HEAD/GET probes on a 3-URL sample of leaderboards[]
   - Agent reports for each probe: `runtime.healthChecks[<domain>]: { status: 'ok'|'unhealthy:<reason>', observedFormat: <format-key> }`
   - **Format consistency check:** if `entry.format` says `static_html_table` but `observedFormat` says `spa_full` (or vice versa), increment `entry.consecutiveFailures`. After 3 consecutive cycles of the same drift, auto-demote `entry.format` to the observed value (e.g., `static_*` → `spa_full`). This is self-healing format classification — the agent does not need a manual whitelist edit when a vendor migrates a leaderboard from server-rendered to SPA.
   - Skill writes results to data/sources-whitelist.json `_runtime.healthChecks` block AND updates per-entry `format` + `format_lastVerified` when drift is confirmed
   - Persistent-unhealthy domains (≥3 cycles consecutive) get `_runtime.unhealthy: true` — agent skips them in this cycle's Phase 1 until next health-check passes
   - This step prevents wasted fetch budget on guaranteed-SPA/403 URLs AND keeps the whitelist's format classification accurate without human intervention

0. LINEUP DISCOVERY (always run first on refresh-all):
   - Agent fetches each vendor's official "active models" page from VENDOR_LINEUP_SOURCES table
   - Returns canonical lineup: { vendorId: { active: [...], deprecated: [...], renamed: [{from,to}] } }
   - Skill diffs against current data/models.json:
     * NEW (in lineup, not in data) → flag for newModels[] survey in Step 4
     * DEPRECATED (in data, marked deprecated by vendor) → set status="deprecated", retain entry, gray-out in UI
     * RENAMED (vendor changed canonical id) → auto-rename per WRONG_ID_AUTO_FIX rule
     * REMOVED (no longer on vendor page after grace period) → archive to data/archive/<id>.json
   - This step CANNOT be skipped on refresh-all; it's the source of truth for "what models exist".
   - **Mandatory retry (added 2026-04-28):** if Step 4 returns with `lineup` empty/missing/`{}` AND this is not the first-ever run, the orchestrator dispatches ONE retry agent (sonnet) restricted to Step 0 (fetch vendor lineup pages only, no bench/pricing). On second-cycle empty, log `gaps[]` entry `lineup:incomplete` with reason and continue. Same retry policy applies when `runtime.healthChecks` covers fewer than 3 leaderboard domains.

1. Read data/{models,sources,sources-whitelist}.json + lineup result from Step 0
2. Parse arg → resolve scope + target_model_ids
3. Build idea_context (DATA-DRIVEN — agent never hardcodes data, only procedure):
   {
     title: "AICoderMap",
     total_models: <count from data/models.json>,
     last_refresh: <max(lastUpdated) from data/models.json>,
     currentIds: [<every id in data/models.json, including status='deprecated'>],
     familyGrouping: <models grouped by (provider, tier) for parallel batches>,
     sourcesWhitelist: <inline data/sources-whitelist.json>,
     verificationMap: <inline .aicodermap-verification-map.json (or {} on first run)>,
     lineup: <Step 0 result>
   }
   - `.aicodermap-verification-map.json` is the historical audit log of every (model, bench) cell observation across cycles (value, sources[], lastChecked). Used for contradiction analysis only — never read for skip decisions, since every cell is re-fetched every cycle (UNCAPPED + UNCACHED doctrine, reformed 2026-04-28). Skill creates it (empty {}) on first cycle if missing.
   - `data/models.json` is SSOT for "what models we track"
   - `data/sources-whitelist.json` is SSOT for "what URLs the agent is allowed to fetch"
   - No skip registry: every (modelId, benchKey) pair is re-attempted every cycle so vendor opt-outs that close are surfaced immediately
   - The agent file (.claude/agents/aicodermap-research-agent.md) only carries PROCEDURE (how) — every list of URLs, vendors, or model IDs lives in data files
4. Agent({
     subagent_type: "aicodermap-research-agent",
     model: "sonnet",
     prompt: structured(
       scope, query, idea_context, target_model_ids?,
       include_unsloth: true,
       trusted_sources_only: true,           // per FETCH_WHITELIST
       // UNCAPPED + UNCACHED doctrine — no fetch/wallclock caps, no
       // confirmed-cell skip. Agent terminates ONLY on
       // COMPLETENESS_TERMINATION (every source walked, every cell re-fetched,
       // every gap documented). See SKILL.md CONSTANTS.
       parallel_sources: 5,                  // parallelism (not a cap)
       parallel_models: 5,                   // parallelism (not a cap)
       verification_map_path: ".aicodermap-verification-map.json",  // audit log only
       trust_score_required: true,           // every value carries a trustScore
       termination: "completeness",          // explicit: not "wallclock", not "fetch_budget"
       require_lineup_populated: true,       // Step 0 lineup MUST be non-empty (orchestrator retries if not)
       require_health_checks: true           // runtime.healthChecks MUST cover ≥3 leaderboard domains
     )
   })
5. Parse return → validate JSON schema (strip surrounding whitespace, locate first `{` and last `}` if narration leaked)

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

7.5. DYNAMIC_WHITELIST_DISCOVERY (self-healing whitelist mutation):
   - Skill reads `artifact.whitelistAdditions[]` (agent emits when it finds high-quality new sources)
   - For each addition:
     * tier='C' → append to data/sources-whitelist.json `community[]` with format='static', lastVerifiedDate=today, consecutiveFailures=0
     * tier='I' → append to `aggregators[]` with phase='discovery' (not promoted without manual review)
     * tier='S' → only if matches existing vendor; ignored otherwise
   - Skill scans `artifact.runtime.healthChecks` and updates `data/sources-whitelist.json._runtime.healthChecks` per-domain
   - Domains with consecutiveFailures ≥ 3 across cycles get `_runtime.unhealthy: true`; auto-skipped in next 2 cycles' Phase 1 (still tried via WebSearch fallback)
   - Whitelist mutations are committed alongside data/* changes — versioned and reversible.

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
   - The `confirmed` flag is **audit-only** — used for contradiction analysis and human review. It is NEVER read by the agent or orchestrator to skip a fetch (every cell is re-fetched every cycle).

8. Render diff summary (markdown table) to user-visible output: models[].updates fields, newModels[], lineup changes (NEW/DEPRECATED/RENAMED/REMOVED), contradictions auto-resolved, coverage% achieved, partialCoverage flag.
9. AUTO-APPROVE — NO USER PROMPT. The workflow proceeds straight from Step 8 to Step 10. The only halt at this stage is schema-breaking discovery (a brand-new top-level field in a model entry not in the existing whitelist) — and even then, the unrecognized field is logged to gaps[] and merge continues with the recognized fields. RED contradictions are already auto-resolved at Step 7. REMOVED entries are auto-archived per LIFECYCLE_STATES.

10. ATOMIC WRITE — schema-complete merge per MERGE_RULES (rotated .bak backup):
    Outputs:
    - data/models.json (multi-provider pricing array, subscription array, status field, full bench, ollama, unslothVariants, etc.)
    - data/sources.json (append sourcesAdded[] + every contradiction's losing candidate, dedup by (key, url, value), include trustScore per entry)
    - i18n/{tr,en}.json (merge i18nUpdates into models[id]={strengths,weaknesses})
    - data/archive/<id>.json (when REMOVED from vendor lineup past grace period)
    - lastUpdated := today (YYYY-MM-DD) per touched entry only
11. Append CHANGELOG.md (Keep a Changelog):
    ## [Unreleased] / ### Updated|Added|Deprecated|Removed|Flagged
12. AUTO-EXECUTE git (no user prompt):
    git add data/ i18n/ CHANGELOG.md scripts/ .claude/skills/aicodermap/SKILL.md .claude/agents/aicodermap-research-agent.md
    git commit -m "data: <generated description>"
    git push
    On hook failure: fix root cause + new commit (NEVER --amend, NEVER --no-verify)
    On push conflict (only halt path in entire workflow): prompt user "git pull --rebase first" — this is the sole user-blocking step because remote-state reconciliation is genuinely outside skill authority.
13. Sleep DEPLOY_WAIT_SEC (90s)
14. Verify: curl <live_url>/data/models.json → 200 + valid schema → "✓ Live". On non-200: log warning, declare workflow done — Pages will eventually finish, no halt.
```

## CONSTANTS
```
CONTRADICTION_WARN              = 3.0   // pp delta → YELLOW (auto-resolve via trustScore)
CONTRADICTION_BLOCK             = 5.0   // pp delta → RED (auto-resolve via trustScore, log loudly)
COVERAGE_TARGET                 = 0.85  // ADVISORY (reformed 2026-04-28). Cumulative provenance coverage; never blocks commit. Below-target → CHANGELOG warning.
COVERAGE_HARD_BLOCK             = 0.50  // ADVISORY (reformed 2026-04-28). <0.50 logs a "⚠ very low cumulative provenance coverage" note in CHANGELOG and proceeds; gaps[] preserved for next cycle
STALE_DAYS                      = 14    // M5 freshness gate
DEPRECATION_GRACE_DAYS          = 60    // vendor "deprecated" → still listed for 60d before archive
DEPLOY_WAIT_SEC                 = 90
AGENT_RETRY                     = 1
FAMILY_BASELINE_MIN             = 30    // refresh-all: |models[]+newModels[]| floor
// =====================================================================
// UNCAPPED RESEARCH DOCTRINE (added 2026-04-27 rev3)
// User policy: "do not put budget/limit/cap on the agent's research effort.
// Use every available capacity to find every available data point. No
// timeout. Stop only when research is structurally complete."
//
// All previous fetch/wallclock budgets are REMOVED. The agent walks every
// advertised source, attempts every reachable per-model URL + vendor card,
// runs every fallback chain, and only terminates on COMPLETENESS_TERMINATION.
// =====================================================================

// Quality controls (kept — these are correctness rules, not effort caps)
VERIFICATION_AGREEMENT_PP       = 1.5   // values within 1.5pp count as agreement; otherwise contradiction[]. Used ONLY for contradiction detection — never for skip decisions.
PARALLEL_SOURCES                = 5     // concurrent source fetches (parallelism, NOT a cap — agent may go higher if useful)
PARALLEL_MODELS                 = 5     // concurrent model surveys (parallelism only)

// Termination — ONLY way the agent stops research:
// All four conditions MUST hold before agent emits final JSON:
//   1. Every leaderboard in sources-whitelist.json `leaderboards[]` has been
//      visited (status: 200 + extract attempted, OR documented unreachable
//      with fallback chain exhausted, OR _runtime.unhealthy auto-skip).
//   2. Every vendor in `vendors[]` with a perModelUrl/modelCardUrl/postUrl
//      has been attempted for every model in that vendor's family.
//   3. Every (modelId, benchKey) cell — across all active models × all
//      bench_keys_universe — has been re-attempted this cycle (no skip on
//      prior confirmation; vendor scores can be revised between refreshes).
//   4. Every still-empty cell carries a gaps[] entry with whatever provenance
//      could be gathered. GAP_VALIDITY_GATE is now ADVISORY ONLY: low-effort
//      gaps surface in `runtime.fabricatedSuspicions[]` for human review but
//      are never stripped (reformed 2026-04-28).
COMPLETENESS_TERMINATION        = true  // sole termination condition

// Cross-cycle persistence (audit only — reformed 2026-04-28):
// The verification map is a HISTORICAL log: it records every (modelId, benchKey)
// cell the cycle observed, with all sources/values that backed it. Used by
// contradiction analysis to spot scores that drift between cycles. Never read
// for skip decisions — every cell is re-fetched every cycle.
VERIFICATION_MAP_PATH           = ".aicodermap-verification-map.json"  // gitignored

SINGLE_ARTIFACT_PATH            = ".aicodermap-agent-out.json"  // ONE artifact, overwritten each run
```

## SILENT_FAIL_PREVENTION (loud failures + auto-recovery, halts only at git push conflict)

| Step | Success criterion | On failure (auto-recovery, never user prompt unless noted) |
|------|-------------------|------------------------------------------------------------|
| 0 Lineup discovery | `lineup` populated AND ≥10 vendor pages successfully parsed (or all reachable vendors attempted) | If `lineup` empty/missing AND not first run → dispatch ONE retry agent restricted to Step 0. On second-cycle empty: log `gaps[]` entry `lineup:incomplete` and CONTINUE. Unreachable vendors → log `lineup:<vendor>: unreachable`, never block on stale lineup. |
| 0b Source health check | `runtime.healthChecks` covers ≥3 leaderboard domains with status entries | If <3 domains → dispatch retry agent restricted to PRELIM SOURCE_HEALTH_CHECK. On second-cycle <3: log `gaps[]` entry `health-check:incomplete` and CONTINUE. |
| 4 Agent survey | JSON return parseable (first `{`, last `}`); `models[]+newModels[]` ≥ FAMILY_BASELINE_MIN OR explicit gaps[] entries explaining shortfall | Retry once with reinforced delivery contract. On second failure: extract whatever JSON fragment is recoverable + log debug to `~/.aicodermap-debug.log` + CONTINUE merge with available data. Family-count shortfall logged to gaps[], never halts. |
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
trustScore(value) = tierWeight × min(verifications, 3)/3 × recencyDecay(date)

tierWeight:
  I = 1.0   (independent leaderboard: Scale SEAL, SWE-bench Verified, Terminal-Bench, Aider, tau-bench, MCP-Atlas, Artificial Analysis, Vellum, livecodebench.com, lmarena.ai, livebench.ai, BFCL, BigCodeBench, EvalPlus, paperswithcode.com, BenchLM, Open LLM Leaderboard, swebench.com)
  S = 0.7   (vendor self-report: official blog, docs, model card, technical report)
  C = 0.4   (community/3rd-party: aggregator blog, walkthrough, review)
  U = 0.1   (forum/social: Reddit, Twitter — never written to data, only as cross-check signal)

verifications: number of distinct sources reporting the same value (capped at 3)

recencyDecay(date):
  age <  30d → 1.00
  age <  90d → 0.85
  age < 180d → 0.70
  age < 365d → 0.50
  age ≥ 365d → 0.30

Tiebreak (when trustScores within 0.05): prefer I-tier, then most recent, then highest verifications.
```

**Application:**
- Every entry in `data/sources.json` MUST carry a `trustScore` field (computed at write time).
- For multi-source same-value cluster: aggregate verifications, take the max recency.
- For multi-source disagreement (a contradiction): each candidate gets its own trustScore; winner has max(trustScore).

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

**Migration policy** (one-time + every refresh until done):
- If `pricing.api` is a flat object `{in, out, cacheHit}` (legacy schema), wrap it as `[{provider:"official", in, out, cacheHit, url:"<vendor docs>", fetched:"<lastUpdated>"}]` and compute `pricing.range`.
- If `pricing.subscription` is a string (legacy), parse to `[{tier:<extracted>, price:<extracted>, billing:"monthly"}]`.
- Self-check at end of every refresh validates all entries are in new schema.

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
| **Storage**  | `data/models.json`    | Flat scalars. `bench.<key>` = number, `context` = number, `pricing.api[].in/out/cacheHit/throughput` = number. NO `{value, trustScore}` wrappers. |
| **Provenance** | `data/sources.json` | Wrapped: `{value, source, url, tier, date, verifications, trustScore, contradictionRole?}`. Sole on-disk home of `trustScore`. |
| **Transit**  | agent → skill JSON    | `models[].updates.<field>` = Storage shape; `models[].sourcesAdded[]` = Provenance shape; NEVER cross-mix.                    |
| **Verification** | `.aicodermap-verification-map.json` (gitignored) | **Cross-cycle cache:** `cells.<modelId>.<benchKey> = {value, verifications[], confirmed, lastChecked}`. Skill reads at cycle start (skip confirmed cells), updates post-merge from sourcesAdded[]. NOT a render input — purely orchestrator state. |
| **Render**   | `assets/js/render-card.js` + `render-table.js` | Reads Storage scalars; looks up Provenance for tooltips by `<modelId>.<field>`. Entry: `assets/js/main.js` (ES module). |

Contradictions: `field` = **bare** bench key (`swePro`, never `bench.swePro`); `candidates[]` wrapped; `autoResolveWinner` wrapped dict — skill extracts `.value` for Storage, keeps full dict for Provenance.

**Enforcement** (4 layers, defense in depth):
1. Agent self-check before emit (Storage-shape validation on every `updates.bench.<k>`)
2. `scripts/merge.py` defensive unwrap (graceful degrade if a wrapper slips through — see MERGE_RULES section H)
3. `scripts/verification-map.py update` post-merge (rebuilds verification cells from sourcesAdded[]; computes `confirmed` flag per VERIFICATION_AGREEMENT_PP rule)
4. Frontend render guard (warn on non-scalar bench cells)

The 2026-04-26 cycle 2 regression (live table blanked) was a contract violation at layer 1 + missing defense at layer 2. Both are now patched. Verification map (added 2026-04-27) is the cross-cycle persistence layer that powers SOURCE_FIRST_SWEEP's confirmed-cell skip.

## MERGE_RULES

**Why this section exists:** prior runs lost data because the merge step only touched `bench`/`pricing`/`provider`/`license`. Sparse fields (`vramRequirement`, `ollamaSize`, `pricing.api.cacheHit`, `uptime`, `subscription`) were silently skipped. Never again.

### A. Single-artifact policy (replaces prior multi-artifact reconciliation)

There is ONE artifact: `.aicodermap-agent-out.json` (gitignored). Every agent run overwrites it. No `.aicodermap-merged.json`, no `.aicodermap-targeted-out.json`, no numbered suffixes — those legacy filenames are deleted; never re-created.

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

BENCH KEYS (dynamic universe = whitelist `_schema.coreBenchKeys` ∪ `leaderboards[].publishes[]`):
                  swePro, sweV, sweMulti, tb2, lcbV6, aider, tau2, mcpA, bfcl,
                  aaCoding, aaAgentic, aaIdx, aaOmni, gpqa, aime26, hle, …
                  (extends automatically when a leaderboard's publishes[] adds a key)
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

Touch `lastUpdated := today` ONLY on models that gained at least one new field value during merge.

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
  validate pricing.api is an array (not flat object) — auto-migrate if not
  validate pricing.subscription is an array (not string) — auto-migrate if not
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

## INVARIANTS (cross-cutting rules; specifics live in their canonical sections above)

- **Procedure vs data**: spec files (this file + agent.md) carry HOW; data files carry WHAT (model roster, source URLs, known gaps, GPU DB, **format taxonomy + regex library**). Spec never hardcodes IDs/URLs/regex patterns/format keywords.
- **Format taxonomy reference**: 12 canonical format keys + adapter selection rules + 16 named extractor patterns live in `data/sources-whitelist.json._schema.{formatTaxonomy, extractors, regexLibrary}`. Adding a new source format = appending a key there + (rare) a new extractor pattern via `scripts/regex-corpus.json` + `scripts/regex-lint.js`. No code change required in agent.md / SKILL.md.
- **Autonomous-by-default**: orchestrator + agent iterate, retry, fall back to alternate source, emit gap[] — never deal-break on missing data. The ONE user-blocking exception is git push conflict.
- **Loud failures, never silent**: every step has an explicit success criterion (see SILENT_FAIL_PREVENTION); failures emit log + gap[] entry + CONTINUE — never halt the workflow short of Step 12.
- **Partial-coverage merges are normal**: low coverage marks `partialCoverage=true` + populates gaps[] for next cycle, but never blocks write/commit/push.
- **No GitHub Actions / CI / workflows** (manual orchestration is the contract).
- **M5 ≤14-day freshness gate** (Aider 5-month-stale antipattern defense).
- **Project-scoped**: skill + agent only in `D:\GitHub\aicodermap\` session.
