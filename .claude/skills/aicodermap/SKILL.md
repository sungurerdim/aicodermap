---
description: "AICoderMap update orchestrator. Project-scoped. Manuel trigger, zero API cost."
argument-hint: "[refresh-all|model <id>|new-release|validate|stale-check|changelog]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, TaskCreate, TaskUpdate
---

# aicodermap

## ROLE
Orchestrate AI coding LLM tracker updates: invoke `aicodermap-research-agent` → validate (≥2 source/score, contradiction detect) → diff preview → user approve → atomic write `data/*.json` + `i18n/*.json` + `CHANGELOG.md` → prompt git commit → verify GitHub Pages deploy.

## CONTEXT
- Project root: `D:\GitHub\aicodermap\`
- Agent: `.claude/agents/aicodermap-research-agent.md`
- Data files: `data/{models,sources,gpu-database}.json`
- i18n: `i18n/{tr,en}.json`
- Live URL: `https://sungurerdim.github.io/aicodermap/`

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
5. Parse return → validate JSON schema
6. Gate: validationCoverage >= 0.95 → proceed; else WARN+force-override
7. Gate: contradictions[].severity="RED" count > 0 → BLOCK, prompt manual pick per RED
8. Render diff (markdown table): models[].updates fields, newModels[], contradictions[], coverage%
9. User input: approve | partial <ids> | decline | detail <id>
10. Atomic write (.bak backup):
    - data/models.json (merge models[].updates)
    - data/sources.json (append sourcesAdded[])
    - i18n/{tr,en}.json (merge i18nUpdates)
    - lastUpdated := today (YYYY-MM-DD) per touched entry
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
```

## ERRORS
| condition | action |
|-----------|--------|
| Agent timeout/HTTP fail | retry 1× → fallback WebSearch → prompt "partial data, continue?" |
| Agent return invalid JSON | log to ~/.aicodermap-debug.log, prompt retry |
| coverage < 0.95 | display missing scores list, options: [A]force-override [B]re-research [C]manual-add |
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
- NO GitHub Actions / CI / workflows (manuel only)
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
