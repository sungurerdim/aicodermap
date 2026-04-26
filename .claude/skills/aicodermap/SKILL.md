---
description: "AICoderMap update orchestrator. Project-scoped. Manual trigger, zero API cost."
argument-hint: "[refresh-all|model <id>|new-release|validate|stale-check|changelog|lineup-sync]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, TaskCreate, TaskUpdate
---

# aicodermap

## ROLE
Orchestrate AI coding LLM tracker updates: discover **official vendor lineup** → reconcile current data → invoke `aicodermap-research-agent` (lineup-driven, trusted-source whitelist, parallel) → auto-resolve contradictions via `trustScore` → atomic schema-complete merge → atomic write `data/*.json` + `i18n/*.json` + `CHANGELOG.md` → prompt git commit → verify GitHub Pages deploy.

**Autonomy principle:** the skill must NOT pause for user input on routine decisions. Every edge case below has a default behavior; the user is asked only when a default cannot be resolved (e.g., new schema-breaking discovery).

## CONTEXT
- Project root: `D:\GitHub\aicodermap\`
- Agent: `.claude/agents/aicodermap-research-agent.md`
- Data files: `data/{models,sources,gpu-database,known-gaps}.json`
- i18n: `i18n/{tr,en}.json`
- Live URL: `https://sungurerdim.github.io/aicodermap/`
- **Known-gaps registry:** `data/known-gaps.json` — vendor opt-outs, not-applicable benchmarks, out-of-scope variants. Agent skips these during exhaustive mining; UI surfaces them as "vendor opt-out" / "not applicable" markers instead of generic "—". When the agent prompt is built, `known-gaps.json` MUST be included in the agent context.
- **Sources whitelist:** `data/sources-whitelist.json` — single source of truth for every URL the research agent is allowed to fetch (vendors / leaderboards / aggregators / local-runtime catalogs / registries / community). Skill loads this and injects it into `idea_context.sourcesWhitelist` for every agent run. Agent NEVER hardcodes URLs.

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
0. LINEUP DISCOVERY (always run first on refresh-all):
   - Agent fetches each vendor's official "active models" page from VENDOR_LINEUP_SOURCES table
   - Returns canonical lineup: { vendorId: { active: [...], deprecated: [...], renamed: [{from,to}] } }
   - Skill diffs against current data/models.json:
     * NEW (in lineup, not in data) → flag for newModels[] survey in Step 4
     * DEPRECATED (in data, marked deprecated by vendor) → set status="deprecated", retain entry, gray-out in UI
     * RENAMED (vendor changed canonical id) → auto-rename per WRONG_ID_AUTO_FIX rule
     * REMOVED (no longer on vendor page after grace period) → archive to data/archive/<id>.json
   - This step CANNOT be skipped on refresh-all; it's the source of truth for "what models exist".

1. Read data/{models,sources,known-gaps}.json + lineup result from Step 0
2. Parse arg → resolve scope + target_model_ids
3. Build idea_context (DATA-DRIVEN — agent never hardcodes data, only procedure):
   {
     title: "AICoderMap",
     total_models: <count from data/models.json>,
     last_refresh: <max(lastUpdated) from data/models.json>,
     currentIds: [<every id in data/models.json, including status='deprecated'>],
     familyGrouping: <models grouped by (provider, tier) for parallel batches>,
     knownGaps: <inline data/known-gaps.json>,
     sourcesWhitelist: <inline data/sources-whitelist.json>,
     lineup: <Step 0 result>
   }
   - `data/models.json` is SSOT for "what models we track"
   - `data/sources-whitelist.json` is SSOT for "what URLs the agent is allowed to fetch"
   - `data/known-gaps.json` is SSOT for per-pair skip rules
   - The agent file (.claude/agents/aicodermap-research-agent.md) only carries PROCEDURE (how) — every list of URLs, vendors, or model IDs lives in data files
4. Agent({
     subagent_type: "aicodermap-research-agent",
     model: "sonnet",
     prompt: structured(
       scope, query, idea_context, target_model_ids?,
       include_unsloth: true,
       trusted_sources_only: true,           // per FETCH_WHITELIST
       per_model_fetch_budget: 6,            // max fetches per model
       per_model_wallclock_budget: 90,       // seconds
       parallel_models: 5,                   // concurrent model surveys
       trust_score_required: true            // every value carries a trustScore
     )
   })
5. Parse return → validate JSON schema (strip surrounding whitespace, locate first `{` and last `}` if narration leaked)

6. COVERAGE TRIGGER — **MANDATORY when fired** (not a block, not a "may"):
   if validationCoverage < COVERAGE_DEEPEN_THRESHOLD (0.95):
     MUST identify (modelId, field) pairs missing ≥2 sources
     MUST spawn DEEP-FETCH agent pass: targeted, single-pair retrieval per gap
     budget: ≤30s per pair, ≤10 pairs total per cycle, ≤2 cycles
     MUST merge deep-fetch returns into pending updates
     MUST stamp the deep-fetch artifact with `deepFetchCycle: <n>` (1, then 2 if a 2nd cycle ran)
   if validationCoverage still < COVERAGE_PARTIAL_WARN after deep-fetch cycles:
     write anyway, append "⚠ partial coverage: <%>" warning to CHANGELOG
   else proceed.

   ENFORCEMENT: `scripts/merge.py` HALTS the commit if `validationCoverage < 0.95`
   in the artifact AND `deepFetchCycle` is absent — proving Step 6 was skipped.
   Orchestrator never silently bypasses Step 6.

7. CONTRADICTION AUTO-RESOLUTION (NOT manual prompt):
   for each contradiction in contradictions[]:
     winner = argmax(trustScore(value) for value in candidates)
     write winner.value to data/models.json
     append all candidates to data/sources.json with their trustScores
     log to CHANGELOG: "<modelId>.<bench>: <winner.value> (trust=<score>) over <loser.value> (trust=<score>) [Δ<delta>pp <severity>]"
   no user prompt is issued for any severity

8. Render diff (markdown table): models[].updates fields, newModels[], lineup changes (NEW/DEPRECATED/RENAMED), contradictions auto-resolved, coverage% achieved
9. User input: approve | partial <ids> | decline | detail <id>
   default behavior: auto-approve when (no schema-breaking change) AND (no RED unresolved-by-trustScore) AND (lineup-discovery had no REMOVED entries)

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
    git add data/ i18n/ CHANGELOG.md scripts/
    git commit -m "data: <generated description>"
    git push
    On hook failure: fix root cause + new commit (NEVER --amend, NEVER --no-verify)
    On push conflict: prompt user "git pull --rebase first"
13. Sleep DEPLOY_WAIT_SEC (90s)
14. Verify: curl <live_url>/data/models.json → 200 + valid schema → "✓ Live"
```

## CONSTANTS
```
CONTRADICTION_WARN              = 3.0   // pp delta → YELLOW (auto-resolve via trustScore)
CONTRADICTION_BLOCK             = 5.0   // pp delta → RED (auto-resolve via trustScore, log loudly)
COVERAGE_TARGET                 = 0.85  // hard floor — Step 6 cycles run until reached
COVERAGE_DEEPEN_THRESHOLD       = 0.95  // ideal — Step 6 also triggers below this
COVERAGE_HARD_BLOCK             = 0.50  // <0.50 BLOCKS commit; orchestrator MUST iterate
STALE_DAYS                      = 14    // M5 freshness gate
DEPRECATION_GRACE_DAYS          = 60    // vendor "deprecated" → still listed for 60d before archive
DEPLOY_WAIT_SEC                 = 90
AGENT_RETRY                     = 1
FAMILY_BASELINE_MIN             = 30    // refresh-all: |models[]+newModels[]| floor
PER_MODEL_FETCH_BUDGET          = 6     // max fetches per model in agent
PER_MODEL_WALLCLOCK_BUDGET      = 90    // seconds per model in agent
PARALLEL_MODELS                 = 5     // concurrent model surveys in agent
DEEP_FETCH_MAX_PAIRS_PER_CYCLE  = 25    // up from 10 — user feedback "data definitely exists somewhere"
DEEP_FETCH_MAX_CYCLES           = 5     // up from 2 — keep iterating until COVERAGE_TARGET hit OR no progress
SINGLE_ARTIFACT_PATH            = ".aicodermap-agent-out.json"  // ONE artifact, overwritten each run
```

## SILENT_FAIL_PREVENTION (every step completes or halts loudly)

| Step | Success criterion | On failure |
|------|-------------------|------------|
| 0 Lineup discovery | ≥10 vendor pages successfully parsed; `lineupChanges` populated (even if all empty) | Retry once with narrower target; if still failing, halt with the unreachable vendor list — never proceed with stale lineup |
| 4 Agent survey | Pure JSON return; `models[]+newModels[]` ≥ FAMILY_BASELINE_MIN OR explicit gaps[] entries | Retry once with reinforced delivery contract; if still bad, log to `~/.aicodermap-debug.log` + halt |
| 6 Deep-fetch loop | `coverage ≥ COVERAGE_TARGET (0.85)` OR all remaining gaps in `data/known-gaps.json` OR `cycles == DEEP_FETCH_MAX_CYCLES (5)` | Run until terminal condition; if cycles exhausted with coverage <0.85, halt with explicit per-pair "tried these N sources, none had it" report |
| 7 Contradiction auto-resolve | Every contradiction has `autoResolveWinner` written to data + all candidates in sources | If trustScores tie within 0.05 AND no I-tier present: halt with manual-pick prompt (only escape hatch) |
| 10 Atomic write | `data/{models,sources}.json` parse-valid + self-check passes | Restore from `.bak`, halt with diff of what failed |
| 12 git push | Exit code 0 AND remote ref advanced | On hook fail: fix root cause + new commit (NEVER --amend, NEVER --no-verify); on push conflict: halt with "git pull --rebase first" |
| 14 Live deploy verify | `curl <live_url>/data/models.json` returns 200 AND parses as JSON | Wait + retry up to 5min; if still failing, halt with githubstatus.com pointer |

**Cardinal rule:** a step never returns "OK" while having silently skipped its work. The artifact's machine-checkable flags (`deepFetchCycle`, `error`, etc.) are the source of truth, not the orchestrator's narration.

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

BENCH KEYS (13):  swePro, sweV, tb2, lcbV6, aider, tau2, aaCoding, aaAgentic, mcpA, gpqa, sweMulti, hle, aaIdx
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

Per-step error handling lives in **SILENT_FAIL_PREVENTION** above (single source). Cross-cutting failure modes not tied to a specific step:

| Condition | Action |
|-----------|--------|
| Agent return invalid JSON | log to `~/.aicodermap-debug.log`, retry 1× with stricter delivery contract; on second fail halt with the raw return |
| `refresh-all` family count < `FAMILY_BASELINE_MIN` | halt with the missing-family list; orchestrator either re-runs with explicit families or marks `gaps[]` |
| User decline at Step 9 | restore from `.bak`, no commit |
| Git push conflict | prompt user "git pull --rebase first"; do NOT force-push |

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

- **Procedure vs data**: spec files (this file + agent.md) carry HOW; data files carry WHAT (model roster, source URLs, known gaps, GPU DB). Spec never hardcodes IDs/URLs.
- **No silent fails**: every step has an explicit success criterion (see SILENT_FAIL_PREVENTION); failure halts with diagnostic, never proceeds quietly with partial data.
- **No GitHub Actions / CI / workflows** (manual orchestration is the contract).
- **M5 ≤14-day freshness gate** (Aider 5-month-stale antipattern defense).
- **Project-scoped**: skill + agent only in `D:\GitHub\aicodermap\` session.
