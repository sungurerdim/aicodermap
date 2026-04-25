---
description: "AICoderMap update orchestrator — research agent → cross-source validation → contradiction flagging → diff preview → JSON write → git commit → GitHub Pages deploy. Manuel update workflow, no API cost."
argument-hint: "[refresh-all | model <id> | new-release | validate | stale-check | changelog]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, TaskCreate, TaskUpdate
---

# aicodermap

Manuel update orchestrator for **AICoderMap** living document. Tek komutla research agent'ı tetikler, validation gate'ler uygular, kullanıcı onayıyla `data/*.json` dosyalarını günceller, GitHub'a push eder.

**Project root:** `D:\GitHub\aicodermap\`
**Agent:** `.claude/agents/aicodermap-research-agent.md` (project-scoped, terzi-dikim)
**Veri:** `data/models.json`, `data/sources.json`, `data/gpu-database.json`
**i18n:** `i18n/tr.json`, `i18n/en.json`
**Live:** https://sungurerdim.github.io/aicodermap/

---

## Komutlar (concrete)

| Argüman | Aksiyon |
|---------|---------|
| (boş) | Interactive: scope sorulur (refresh-all / model <id> / new-release) |
| `refresh-all` | Tüm modeller için agent delegation, full data refresh |
| `model <id>` | Spesifik model deep refresh (örn `model opus-4-7`) |
| `new-release` | Yeni model detection (provider blogs + r/LocalLLaMA + HN son 14 gün) |
| `validate` | Sadece mevcut data/sources.json üzerinde coverage check (no fetch) |
| `stale-check` | 14 gün+ eski model entry'leri listele (M5 disiplini) |
| `changelog` | Son 5 release entry preview |

### Concrete invocation örnekleri

```
/aicodermap                          # Interactive menu
/aicodermap refresh-all              # Full refresh
/aicodermap model deepseek-v4-flash  # Tek model deep update
/aicodermap new-release              # Son 14 gün yeni model var mı?
/aicodermap stale-check              # Hangi modeller bayatladı?
```

---

## Workflow (14 adım)

```
1. Read project root data/ + idea state
2. Argüman parse → scope belirle
3. Idea context oluştur (model count, lastUpdated dates, benchmark defs)
4. Agent delegation:
   Agent({
     subagent_type: "aicodermap-research-agent",
     model: "sonnet",  // full/specific scope; "haiku" sadece search
     prompt: STRUCTURED_PROMPT (scope/query/idea_context/target_model_ids/include_unsloth)
   })
5. Agent return → JSON parse + schema validate
6. Validation gate:
   - validationCoverage >= 0.95 (M4 metric, hard gate)
   - contradictions[] içinde severity="RED" varsa block
7. Contradiction triage:
   - YELLOW (3-5pp): UI'da ⚠ flag, otomatik kabul
   - RED (>5pp): Source breakdown göster, manuel pick
8. Diff preview (markdown table):
   - Updated models + changed fields per model
   - newModels[] (yeni eklenenler)
   - Contradictions (severity + sources + delta)
   - validationCoverage %
9. User onay (text input: approve / partial / decline / detail <id>)
10. Atomic write (.bak backup):
    - data/models.json (merge updates)
    - data/sources.json (append new entries)
    - i18n/tr.json + i18n/en.json (strengthsKey/weaknessesKey content)
    - lastUpdated auto-set today (YYYY-MM-DD)
11. CHANGELOG.md append (Keep a Changelog format):
    ## [Unreleased]
    ### Updated (YYYY-MM-DD)
    ### Added
    ### Flagged (contradictions)
12. Git workflow (skill prompts user, NOT auto):
    git add data/ i18n/ CHANGELOG.md
    git commit -m "data: <description>"
    git push
13. Wait 90sn for GitHub Pages deploy
14. Post-deploy verification (curl + JSON schema check) → "✓ Live"
```

---

## Kullanıcının ne göreceği (Output snapshots)

### ✓ Success (typical refresh)

```
🚀 AICoderMap update başlıyor...
📊 Mevcut state: 35 model, son update 7 gün önce (M5 ≤14gün ✓)
🤖 Agent delegation: scope=refresh-all, sonnet model
   ⏳ ~2-3 dk (15+ source paralel fetch)

✓ Agent return:
  • Confidence: HIGH
  • 3 model güncellendi (opus-4-7, kimi-k2-7, deepseek-v4-pro)
  • 1 yeni model: Qwen3.7-Coder (Alibaba, MIT)
  • 2 contradiction: 1 YELLOW + 0 RED
  • Validation coverage: 0.97 ✓ (M4 ≥0.95 ✓)

📋 Diff preview:
  opus-4-7:
    bench.swePro: 64.3 → 65.1 (Δ +0.8) ✓ AA + Anthropic agree
    pricing.api.in: 5.00 → 5.00 (no change)
    lastUpdated: 2026-04-16 → 2026-04-25
  kimi-k2-7:
    bench.lcbV6: 89.6 → 91.2 (Δ +1.6)
    bench.aaIdx: 54 → 55
  deepseek-v4-pro:
    pricing.api.cacheHit: 0.145 → 0.130 (Δ -0.015) ⚠ pricing change
    bench.tb2: 67.9 → 71.4 (Δ +3.5) ⚠ YELLOW: HF 71.4 vs Scale SEAL 67.9 (Δ 3.5pp)
  Qwen3.7-Coder (NEW):
    SWE-Pro 58.4, LCB 92.1, MIT, Ollama: ollama pull qwen3.7-coder

📝 Onay? (approve / partial <ids> / decline / detail <id>)
> approve

✓ data/models.json yazıldı (3 update + 1 add)
✓ data/sources.json yazıldı (12 yeni source entry)
✓ i18n yazıldı (qwen3.7-coder strengths/weaknesses TR+EN)
✓ CHANGELOG.md eklendi: ## 2026-04-25
✓ git önerilen komutlar:
   git add data/ i18n/ CHANGELOG.md
   git commit -m "data: refresh April 25 — 3 model updated, Qwen3.7-Coder added"
   git push

⏳ GitHub Pages deploy bekleniyor (~90sn)...
✓ Live: https://sungurerdim.github.io/aicodermap/
✓ M5 disiplin: bu update 7 gün ara (≤14 gün ✓)
```

### ⚠ Coverage Düşük (M4 gate fail)

```
⚠ Validation coverage düşük: 0.91 (M4 ≥0.95 hedefi altında)
   Eksik source'lu skorlar (4):
     - opus-4-7.tau2: tek kaynak (Anthropic, S tier)
     - kimi-k2-7.aaCoding: tek kaynak (AA, I tier)
     - deepseek-v4-pro.aider: tek kaynak (HF model card, S tier)
     - qwen3-7-coder.mcpA: hiç kaynak yok

Seçenekler:
  [A] Force-override: yine de yayınla, eksikler "S" badge ile flag'lenecek
  [B] Re-research: agent'ı eksik (modelId, benchmark) çiftleri için yeniden tetikle (önerilen)
  [C] Manuel ekle: data/sources.json'da entry oluştur, sonra yeniden validate
> 
```

### 🚨 RED Contradiction (block)

```
🚨 Critical contradiction (>5pp): opus-4-7.swePro
   Anthropic official:    64.3  (S tier, 2026-04-16)
   Scale SEAL:            56.8  (I tier, 2026-04-20)
   Delta: 7.5pp 🚨 RED

Manuel resolution gerekli — hangi kaynak baz alınsın?
  [1] Anthropic 64.3 (S — self-reported, possible inflation)
  [2] Scale SEAL 56.8 (I — independent, contamination-resistant) ⭐ ÖNERİLEN
  [3] Both flag, ortalama (60.55) ⚠ ile göster
  [4] Skip bu model bu update'te
> 2

✓ opus-4-7.swePro = 56.8 (Scale SEAL primary, Anthropic flagged secondary)
   Devam ediyor...
```

### ❌ Hata Senaryoları

| Hata | Skill aksiyonu |
|------|---------------|
| Agent timeout | Retry 1× → fallback WebSearch → "kısmi veri, devam?" |
| JSON parse fail | "Agent return geçersiz, log: ~/.aicodermap-debug.log; tekrar dene?" |
| Git conflict | "git pull --rebase önce, sonra yeniden çalıştır" |
| User decline | Rollback (.bak'tan restore, no commit) |
| Pages deploy 5dk+ | "GitHub status check: https://www.githubstatus.com/" |

---

## Sabit konfigürasyon (kod içi, no config file)

```javascript
const CONTRADICTION_WARN = 3.0;        // ≥3pp ⚠ YELLOW
const CONTRADICTION_BLOCK = 5.0;       // ≥5pp 🚨 RED (block)
const VALIDATION_COVERAGE_MIN = 0.95;  // M4 metric
const STALE_THRESHOLD_DAYS = 14;       // M5 metric
const POST_DEPLOY_WAIT_SEC = 90;
const AGENT_RETRY_COUNT = 1;
```

---

## Yardımcı komutlar

### `validate` (no fetch, mevcut state check)

```
✓ Mevcut state validation
   Total models: 35
   Coverage:     0.97 ✓ (M4 ≥0.95)
   Contradictions: 1 ⚠ YELLOW, 0 🚨 RED
     - opus-4-7.swePro: AA 65.1 vs Scale SEAL 62.4 (Δ 2.7pp)
   Stale entries: 0 (M5 ≤14 gün ✓)
```

### `stale-check`

```
⚠ Bayatlamış model entry'leri:
   • aider-polyglot:  45 gün önce ⚠⚠⚠
   • codestral-22b:   18 gün önce ⚠
   • Diğer 33 model:  ≤14 gün ✓
```

### `changelog`

```
📝 Son 5 release:
   2026-04-25: 3 update, 1 add (Qwen3.7-Coder)
   2026-04-18: 5 update, RED resolved (opus-4-7.swePro)
   2026-04-11: Full refresh, 35 model
   2026-04-04: 2 add (DeepSeek V4-Pro/Flash)
   2026-03-28: Initial v1.0 launch
```

---

## Kabul Kriterleri (E2E acceptance test)

| Test | Komut | Pass Criteria |
|------|-------|---------------|
| Skill invoke | `/aicodermap` | Interactive menu açılır <1sn |
| Agent delegation | `/aicodermap model opus-4-7` | Agent <5sn başlar, sonnet model |
| Validation gate | Force coverage <0.95 | Warning + force-override seçeneği |
| RED contradiction | Mock 7pp delta | 🚨 + manuel pick zorunlu |
| Diff preview | Refresh-all sonrası | Markdown table renderleniyor |
| Atomic write | User decline mid-write | data/*.json değişmedi, .bak korundu |
| Deploy verify | Push sonrası | 90sn sonra live URL 200 OK |
| Stale check | 15 gün önce update edilmiş entry | ⚠ flag listede |

---

## Disiplinler (operational)

- **M4 release gate:** validationCoverage <0.95 → user explicit force-override gerek
- **M5 update freshness:** ≤14 gün max ara, anti-Aider-stale (Aider 5 ay stale antipattern)
- **R3 burnout savunması:** ≤4 content post/ay hard cap (separate, content workflow için)
- **Editorial integrity:** Default weights commit message'ta rationale ile, contradiction'lar açık flag
- **No GitHub Actions:** Skill manuel tetik, push manuel — CI/CD complexity yok ($0 sürekli)
- **No external monitoring:** GitHub Insights Traffic built-in M1 ölçüm için yeterli

---

## See Also

- `D:\GitHub\aicodermap\docs\WORKFLOW.md` — Detaylı 14 happy + 5 exception
- `D:\GitHub\aicodermap\docs\IMPLGUIDE.md` — Code-ready implementation
- `D:\GitHub\aicodermap\docs\TECHSPEC.md` — System architecture
- `.claude/agents/aicodermap-research-agent.md` — Domain-specialized research agent
- `~/.ideas/coding-models-tracker.json` — BrainLedger idea entry (45 decisions traceable)
