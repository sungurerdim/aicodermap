---
description: "AICoderMap update orchestrator. Project-scoped. Manual trigger, zero API cost."
argument-hint: "[refresh-all|model <id>|new-release|validate|stale-check|changelog]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, TaskCreate, TaskUpdate
---

# aicodermap

## ROLE
Orchestrate AI coding LLM tracker updates: invoke `aicodermap-research-agent` → validate (≥2 source/score, contradiction detect) → diff preview → user approve → atomic write `data/*.json` + `i18n/*.json` + `CHANGELOG.md` → prompt git commit → verify GitHub Pages deploy.

## CONTEXT
- Project root: `D:\GitHub\aicodermap\`
- Agent: `.claude/agents/aicodermap-research-agent.md`
- Data files: `data/{models,sources,gpu-database,known-gaps}.json`
- i18n: `i18n/{tr,en}.json`
- Live URL: `https://sungurerdim.github.io/aicodermap/`
- **Known-gaps registry:** `data/known-gaps.json` — vendor opt-outs, not-applicable benchmarks, out-of-scope variants. Agent skips these during exhaustive mining; UI surfaces them as "vendor opt-out" / "not applicable" markers instead of generic "—". When the agent prompt is built, `known-gaps.json` MUST be included in the agent context so it can honor the skip rule.

## ARGS
| arg | scope | model | typical_duration |
|-----|-------|-------|------------------|
| (none) | interactive prompt | — | — |
| `refresh-all` | full | sonnet | 3-5min |
| `model <id>` | specific | sonnet | 1-2min |
| `new-release` | new-release | sonnet | 2-3min |
| `validate` | (no fetch) | — | <10s |
| `stale-check` | (no fetch) | — | <5s |
| `changelog` | (no fetch) | — | <5s |

**`refresh-all` baseline:** Agent's `DEFAULT_TARGETS` table (5 families, ≥35 models) is non-negotiable — every family must be surveyed, missing ones emit a `gaps[]` entry. Skill rejects returns whose `models[]` + `newModels[]` cardinality < 30 unless agent explains via `gaps[]`.

## WORKFLOW
```
1. Read data/models.json + data/sources.json
2. Parse arg → resolve scope + target_model_ids
3. Build idea_context: {title:"AICoderMap", total_models:<n>, last_refresh:<iso>}
4. Agent({
     subagent_type: "aicodermap-research-agent",
     model: "sonnet",
     prompt: structured(scope, query, idea_context, target_model_ids?, include_unsloth:true)
   })
   For scope=full: prompt must explicitly reference DEFAULT_TARGETS (5 families × ≥35 models) so the agent cannot drop a family silently.
   **Exhaustive coverage contract** — the prompt must require: "For EVERY surveyed model, attempt to populate EVERY field in the OUTPUT_SCHEMA whitelist (all 13 bench keys, pricing.api.in/out/cacheHit, pricing.subscription, released, context, providers, uptime, license, open, vramRequirement, ollamaSize, ollama (rich obj when local), unslothVariants when applicable). A field is omitted from `updates` ONLY when (a) the value matches the current data/models.json exactly, OR (b) no source on web could be found — in which case it goes into `gaps[]` with the modelId.field key. Do NOT skip fields just because they're 'sparse' or 'rare' — that is exactly the data the user needs."
   Delivery contract: agent MUST return the JSON as its final text message (never write to file, never narrate). The skill parses the Task tool's return value directly via JSON.parse. Reinforce this in the prompt: "Final message = pure JSON, first char `{`, last char `}`, no markdown fences, no narration."
5. Parse return → validate JSON schema (strip surrounding whitespace, locate first `{` and last `}` if narration leaked)
6. Gate: validationCoverage >= 0.95 → proceed; else WARN+force-override
7. Gate: contradictions[].severity="RED" count > 0 → BLOCK, prompt manual pick per RED
8. Render diff (markdown table): models[].updates fields, newModels[], contradictions[], coverage%
9. User input: approve | partial <ids> | decline | detail <id>
10. Atomic write — **SCHEMA-COMPLETE MERGE** (rotated .bak backup):
    Merge MUST cover EVERY field in OUTPUT_SCHEMA (per agent definition), not just bench/pricing.
    See MERGE_RULES section below for the full field list and per-field policy.
    Outputs:
    - data/models.json (schema-complete merge — bench[*], pricing.api.*, pricing.subscription, released, context, providers, uptime, license, open, vramRequirement, ollamaSize, ollama, unslothVariants, name, tier, strengthsKey, weaknessesKey)
    - data/sources.json (append sourcesAdded[] + contradiction values, dedup by (key, url, value))
    - i18n/{tr,en}.json (merge i18nUpdates into models[id]={strengths,weaknesses})
    - lastUpdated := today (YYYY-MM-DD) per touched entry only
11. Append CHANGELOG.md (Keep a Changelog):
    ## [Unreleased] / ### Updated|Added|Flagged
12. Print git commands for user (DO NOT auto-commit):
    git add data/ i18n/ CHANGELOG.md
    git commit -m "data: <gen description>"
    git push
13. Sleep 90s
14. Verify: curl <live_url>/data/models.json → 200 + valid schema → "✓ Live"
```

## CONSTANTS
```
CONTRADICTION_WARN = 3.0    // pp delta → YELLOW
CONTRADICTION_BLOCK = 5.0   // pp delta → RED (block)
COVERAGE_MIN = 0.95         // M4 release gate
STALE_DAYS = 14             // M5 freshness gate
DEPLOY_WAIT_SEC = 90
AGENT_RETRY = 1
FAMILY_BASELINE_MIN = 30    // refresh-all: |models[]+newModels[]| floor
```

## MERGE_RULES

**Why this section exists:** prior runs lost data because the merge step only touched `bench`/`pricing`/`provider`/`license`. Sparse fields (`vramRequirement`, `ollamaSize`, `pricing.api.cacheHit`, `uptime`, `subscription`) were silently skipped — visible in the resulting `data/models.json` as missing values that the user then had to flag manually. Never again.

### A. Artifact reconciliation (BEFORE primary agent run merge)

Before applying the current run's `models[].updates`, scan for prior artifacts that may carry data the current run omitted:

```
prior_artifacts = glob('.aicodermap-*.json') ∪ {.aicodermap-merged.json, .aicodermap-targeted-out.json, .aicodermap-agent-out{,2,3}.json, .aicodermap-agent-out-fresh.json}
```

These exist when a prior refresh failed mid-flow OR when targeted gap-fill produced a separate artifact OR when the user manually merged earlier runs. Treat their `models[].updates`, `newModels[]`, and `sourcesAdded[]` as **lower-priority backfill** candidates for any field the current run leaves null.

### B. Per-field merge policy (priority order, top wins)

For every `(modelId, field)` pair, walk this priority list and apply the first non-null value found:

```
1. User-resolved RED contradictions (always canonical, never overridden)
2. Independent-source override (per memory rule: I-tier > S-tier when both exist for the same bench)
3. Current run's models[].updates value (newest authoritative agent return)
4. Prior artifact value (recover any field the current run omitted)
5. Existing data/models.json value (preserve)
```

### C. Field whitelist (every refresh MUST iterate ALL of these)

```
SCALAR FIELDS:    name, provider, released, tier, open, license, context, providers, uptime, vramRequirement, ollamaSize, strengthsKey, weaknessesKey

NESTED FIELDS:    pricing.api.in, pricing.api.out, pricing.api.cacheHit, pricing.subscription

OBJECT FIELDS:    ollama (full pullCmd/tags/pullCount/architecture/parameters/license/releasedISO/ollamaUrl block — preserve atomically; replace only if new object has more keys)

ARRAY FIELDS:     unslothVariants[] (replace if new has ≥ existing length)

BENCH KEYS (13):  swePro, sweV, tb2, lcbV6, aider, tau2, aaCoding, aaAgentic, mcpA, gpqa, sweMulti, hle, aaIdx
                  → independent-source rule applies per bench key
```

A field whose current value is `null`, `undefined`, `"?"`, or `"Unknown"` is treated as **empty** for fill purposes. Any artifact value beats empty.

### D. Provenance (data/sources.json)

After the field merge, every `(modelId, bench)` value that ended up in `data/models.json` must have at least one matching entry in `data/sources.json[<modelId>.<bench>]`. If the chosen value is provider-self-reported (no I-tier source) AND no sources entry exists, append the S-tier provenance pointing at the announcement URL (so UI can render the "self-reported" marker).

### E. lastUpdated discipline

Touch `lastUpdated := today` ONLY on models that gained at least one new field value during merge. Models with zero deltas keep their prior `lastUpdated` (the M5 freshness gate then accurately reflects what's actually fresh).

### F. Backup rotation

```
data/models.json     → data/models.json.bak (most recent prior)
data/models.json.bak → data/models.json.bak2 (the one before that)
```

Same rotation for `data/sources.json` and `i18n/*.json`. Two layers of `.bak` lets the user undo two refreshes back. Both .bak / .bak2 are gitignored via `*.bak`.

### G. Self-check (BEFORE prompting the user to git commit)

Run this verification pass:
```
for each model in data/models.json:
  for each field in (whitelist above):
    if field is null AND any artifact has a non-null value:
      → MERGE BUG. Halt, log model+field+artifact path, prompt user.
```

A passing self-check is the gate for printing git commands at Step 12. If it fails, the answer is never "let the user catch it later" — fix the merge in-place.

## ERRORS
| condition | action |
|-----------|--------|
| Agent timeout/HTTP fail | retry 1× → fallback WebSearch → prompt "partial data, continue?" |
| Agent return invalid JSON | log to ~/.aicodermap-debug.log, prompt retry |
| coverage < 0.95 | display missing scores list, options: [A]force-override [B]re-research [C]manual-add |
| refresh-all family count < 30 (FAMILY_BASELINE_MIN) | block: list missing families per DEFAULT_TARGETS, options: [A]re-research with explicit family list [B]force-override (mark gaps[]) |
| RED contradiction (>5pp) | per-RED prompt: [1]source-A [2]source-B [3]flag-both-avg [4]skip-model |
| User decline at step 9 | restore from .bak, no commit |
| Git push fail (conflict) | prompt "git pull --rebase first" |
| Pages deploy >5min | suggest githubstatus.com check |

## OUTPUT_TEMPLATE_SUCCESS
```
🚀 AICoderMap update | scope:<scope> | last_refresh:<n>d ago (M5 ≤14d ✓)
🤖 Agent → sonnet | ETA ~<n>min

✓ Return: confidence:<HIGH|MED|LOW> | <n_updated> updated | <n_new> new | <n_yellow>Y/<n_red>R contradictions | coverage:<%>

📋 Diff:
  <model_id>:
    <field>: <old> → <new> (Δ <delta>) [✓ agree | ⚠ YELLOW <Apros>vs<Bpros>]
  <new_model_id> (NEW): <summary>

📝 approve|partial <ids>|decline|detail <id>?

✓ Wrote: data/models.json (<n>upd+<n>add)
✓ Wrote: data/sources.json (<n> entries)
✓ Wrote: i18n/{tr,en}.json (<n> entries)
✓ Appended: CHANGELOG.md ## <date>

📦 Run:
  git add data/ i18n/ CHANGELOG.md
  git commit -m "data: <description>"
  git push

⏳ Pages deploy ~90s...
✓ Live: <url> | M5: <n>d ago (≤14d ✓)
```

## OUTPUT_TEMPLATE_COVERAGE_LOW
```
⚠ Coverage: <%> (M4 ≥0.95 fail)
   Missing source for <n> scores:
     - <model_id>.<benchmark>: <n_sources> source(s), tier=<S|I|C>
[A] force-override (mark as 'S' tier)
[B] re-research missing pairs (recommended)
[C] manual add to data/sources.json
```

## OUTPUT_TEMPLATE_RED_CONTRADICTION
```
🚨 RED contradiction (>5pp): <model_id>.<benchmark>
   <source_A> (tier:<t>): <value_A> | <date>
   <source_B> (tier:<t>): <value_B> | <date>
   delta: <pp>pp 🚨
[1] <source_A> primary | [2] <source_B> primary ⭐ if higher tier
[3] flag both, avg = <calc> ⚠ | [4] skip model this update
```

## SUBCOMMANDS
### `validate` (no fetch)
Read data/sources.json → compute coverage, list contradictions, check stale entries.
Output:
```
total_models:<n> | coverage:<%> | contradictions:<n>Y/<n>R | stale:<n>
```

### `stale-check`
Iterate data/models.json → list entries with `(today - lastUpdated) > STALE_DAYS`.
Output:
```
- <model_id>: <n>d ago ⚠⚠⚠ if >2× threshold
```

### `changelog`
tail -50 CHANGELOG.md → parse last 5 release entries.

## DISCIPLINES
- M4 gate enforced; force-override requires explicit user input
- M5 ≤14 day discipline (Aider 5-month-stale antipattern defense)
- R3 burnout: ≤4 content posts/month hard cap (separate, not skill scope)
- Editorial integrity: contradictions surfaced, never hidden
- **Schema-complete merge** — every refresh applies MERGE_RULES to ALL whitelisted fields, reconciles against ALL prior `.aicodermap-*.json` artifacts, and runs the self-check before printing git commands. No silent field drops.
- **Independent-source canonical rule** — I-tier leaderboard values override S-tier provider self-reports; see memory `feedback_independent_bench_priority`
- **Agent delivery contract** — agent returns JSON as final text message (no narration, no file write); see memory `feedback_agent_output_delivery_contract`
- NO GitHub Actions / CI / workflows (manual only)
- NO external monitoring (GitHub Insights Traffic = M1 source)
- Project-scoped: skill+agent only in `D:\GitHub\aicodermap\` session

## E2E_TEST_MATRIX
| test | trigger | pass |
|------|---------|------|
| invoke | `/aicodermap` | menu <1s |
| delegate | `/aicodermap model <id>` | agent start <5s, sonnet |
| coverage_gate | force <0.95 | warn + override prompt |
| red_block | mock 7pp delta | manual pick required |
| diff_render | post-refresh | full markdown table |
| atomic | decline mid-write | data/* unchanged, .bak preserved |
| deploy_verify | post-push 90s | live URL 200 + schema valid |
| stale | entry 15d old | listed in stale-check |
