# Coding Models Tracker — Workflow Documentation

**Sürüm:** 1.0 | **24 Nisan 2026** | **Audience:** Sungur (operational reference)

---

## 1. Update Workflow — 14 Happy Path Steps

```
┌──────────────────────────────────────────────────────────────────┐
│  HAPPY PATH                                                      │
├──────────────────────────────────────────────────────────────────┤
│ 1. User → Claude Code → /ledger-tracker-update (skill invoke)    │
│ 2. Skill reads idea context (son launch, bilinen modeller, defs) │
│ 3. Skill asks: "Full refresh? Specific model? New release?"      │
│ 4. Scope seçim:                                                  │
│    - Full refresh → tüm modeller                                 │
│    - Specific model → single-model deep                          │
│    - New release → new model detection + full profile            │
│ 5. Skill → coding-models-research-agent (structured prompt)      │
│ 6. Agent: web scraping + cross-source + validation               │
│ 7. Agent returns JSON {models[], contradictions[], coverage}     │
│ 8. Skill validation:                                             │
│    - ≥2 source per score (M4 release gate)                       │
│    - Contradictions flag (>3pp ⚠, >5pp 🚨)                       │
│    - lastUpdated auto-set to today                               │
│ 9. Skill diff preview:                                           │
│    - Changed fields highlight                                    │
│    - New models list                                             │
│    - Contradictions table                                        │
│10. User review + approve (or override per-entry)                 │
│11. Skill write data/models.json + data/sources.json              │
│12. Skill append CHANGELOG.md entry                               │
│13. User git commit + push (or skill auto with confirmation)      │
│14. GitHub Pages auto-deploy (~1-2 dk) → confirmation             │
└──────────────────────────────────────────────────────────────────┘
```

**Tipik süre:** 10-15 dakika (full refresh) / 3-5 dakika (single model update).

---

## 2. Exception Handling — 5 Senaryo

| # | Senaryo | Detection | Davranış |
|---|---------|-----------|----------|
| **a** | Agent HTTP fetch fail | Network error caught | Retry 1× → fallback WebSearch → user prompt: "Kısmi veri elde edildi, devam etmek ister misin?" |
| **b** | Validation coverage <%95 | M4 gate check | ⚠ Warning + missing source list göster + user force-override seçeneği |
| **c** | Contradiction >5pp | sources.json delta calc | 🚨 Red flag + source breakdown göster → user manual pick (hangi kaynak doğru?) veya flag both |
| **d** | User decline diff | User input "no" / iptal | Rollback (no file write, no commit) — tracker önceki state'te kalır |
| **e** | Git conflict (parallel edit) | `git push` failure | Skill abort + "Önce `git pull` yap, sonra yeniden dene" message |

---

## 3. Roller (Solo Model)

**Tam solo — tüm 4 sorumluluk Sungur'da.** MVP'de ve Faz 2'de collaborator yok.

| Rol | Sorumluluk | Cadence |
|-----|------------|---------|
| **Trigger** | Skill invoke, scope seçimi, update başlatma | Haftalık + event-driven (yeni model launch) |
| **Approve** | Diff preview review, contradiction resolution, override decisions, git commit confirmation | Her update'de |
| **Moderate** | Community issue/PR triage (yanıt + yönlendirme); collaborator merge yetki yok | Haftalık (issues), günlük (Twitter mentions) |
| **Publish** | Git push → GitHub Pages auto-deploy, asset serving | Her update'de (otomatik) |

### SPOF Mitigation
- Skill + research agent **self-contained + documented** → hastalık/tatil sonrası hızlı geri dönüş
- M5 metric: ≤14 gün buffer 1 atlanan update'i tolerates
- Editorial integrity > continuity tradeoff **bilinçli accept edildi**

---

## 4. Tools & Systems (Minimal Stack)

**Tek external service: GitHub Pages.** Tüm geri kalanı ya browser-native ya repo-içi ya yerel araç.

| Item | Where | Cost |
|------|-------|------|
| GitHub Pages | github.com | $0 (public repo) |
| Claude Code CLI | yerel makine `~/.claude/` | mevcut subscription |
| html2canvas | repo `assets/vendor/html2canvas.min.js` | $0 |
| WebGPU API | browser-native | platform |
| GitHub Insights (M1 traffic) | github.com built-in Traffic sekmesi | $0 |

**Maliyet:** $0 sürekli.
**External dependency:** 1 (GitHub).
**Custom domain:** opsiyonel ($12/yıl), MVP'de `*.github.io` yeterli.

---

## 5. Acceptance Criteria

### Workflow Gates (5)

| Gate | Pass Criteria | Fail Action |
|------|---------------|-------------|
| **AC1** Agent research | ≥15 source fetch + structured JSON return + confidence field set | Retry 1× → fallback WebSearch |
| **AC2** Validation ≥2 source | Coverage ≥%95 (M4 release gate) | Force-override user onayı gerek |
| **AC3** Contradiction flag | >3pp işaret, >5pp red flag, source breakdown tooltip | UI render test fail → block |
| **AC4** Diff preview | Changed fields highlight + new models list + contradictions table | User iptal → rollback |
| **AC5** GitHub Pages deploy | 2 dk içinde live + 0 404 + JSON fetch <2sn | Deploy fail → manual retry |

### Feature-Level AC (8)

| Feature | Pass Criteria |
|---------|---------------|
| **F1** Skill+agent | `/ledger-tracker-update` invoke edilebilir, agent delegation <5sn başlar |
| **F3** i18n switch | Anında değişim no reload, localStorage persist |
| **F7** Cross-source validation | Release gate enforce edilir (<%95 ise warning) |
| **F9** Weights editor | Total=100% constraint, live recalc <100ms, 4 preset çalışır, reset-to-default çalışır |
| **F10** PNG export | Section export no clipping, full page scroll-aware, iOS Safari + Chrome Android test pass |
| **F11** Responsive | Mobile <640px + tablet 641-1024 + desktop >1024 her birinde overflow=0 |
| **F12** Contradiction flagging | ≥3pp delta UI'da ⚠ render, tooltip source breakdown |
| **F13** GPU VRAM | WebGPU supported'da auto detect + unsupported'da manual fallback; compatibility badge ✓/⚠/✗ her local model için doğru |

**Diğer must-have feature'lar (F2/F4/F5/F6/F8) implicit AC'lerde karşılanıyor:**
- F2 data regen → AC1 + AC4
- F4 deploy → AC5
- F5 GitHub Insights → built-in (no custom AC)
- F6 changelog → workflow step 12
- F8 README → documentation audit

---

## 6. Operational Disciplines

### Update Discipline (M5 metric: ≤14 gün)
- **Hedef cadence:** haftalık (event-triggered: yeni frontier model çıktığında zaten yapılır)
- **Hard cap:** 14 gün max aralık → stale badge UI'da görünür
- **Anti-pattern referans:** Aider 5-ay-stale (Kasım 2025'ten beri leaderboard güncellenmedi)

### Content Discipline (R3 burnout savunması)
- **Hard cap:** ≤4 post/ay
- **Cadence:** CP1 event-triggered + CP2 ayda 1-2 + CP3 quarterly
- **Burnout signals:** 1 update miss → recovery sprint, 2 update miss → LITE mode aktive

### Editorial Discipline (compound moat D)
- Cross-source ≥2 zorunlu (M4 ≥%95 coverage)
- Contradictions açıkça flag'le, gizleme
- Default weights editorial — değişikliği rationale ile commit message'ta belge

---

## 7. Update Walkthrough Örneği

**Senaryo:** Yeni Kimi K2.7 release, mevcut tracker güncel değil.

```
1. /ledger-tracker-update
2. Skill: "Önceki update 9 gün önce. Hangi kapsamda?"
3. User: "New release: Kimi K2.7"
4. Skill → agent (scope: full, target_model_ids: ["kimi-k2-7"], include_unsloth: true)
5. Agent fetches: Moonshot blog + AA + llm-stats + BenchLM + LiveCodeBench + r/LocalLLaMA mentions
6. Agent returns: { confidence: HIGH, models: [{ id: "kimi-k2-7", updates: {...} }], contradictions: [], coverage: 0.97 }
7. Skill validates: ✓ ≥2 source per score, no contradictions, coverage 97%
8. Skill diff preview:
   "Kimi K2.7 yeni eklendi. SWE-Pro: 60.2 (Moonshot), 58.9 (Scale SEAL). Δ=1.3pp OK.
    Bench coverage: 8/12 ✓"
9. User: "Approve, weight K2.7 entry standard"
10. Skill writes data/models.json (entry eklendi) + data/sources.json (sources)
11. Skill appends CHANGELOG.md:
    ## 2026-04-24
    ### Added
    - Kimi K2.7 (Moonshot AI) — SWE-Pro 60.2, LCB 89.4, MIT license
12. User: git commit -m "data: add Kimi K2.7" && git push
13. GitHub Pages deploy ~1.5 dk
14. Skill: "✓ Live: https://sungurerdim.github.io/coding-models-tracker/"
```

---

## 8. Troubleshooting

| Problem | Çözüm |
|---------|-------|
| Skill çalışmıyor | `~/.claude/skills/coding-models-tracker/SKILL.md` var mı kontrol et |
| Agent timeout | Retry, sonra fallback WebSearch (skill otomatik yapar) |
| GitHub Pages 404 | Settings → Pages → Source `main` branch / `/ (root)` doğrula |
| Weights editor 100% değil | Reset-to-default butonu, localStorage temizle |
| WebGPU detect hatalı | Manual fallback dropdown kullan |
| PNG export bozuk | iOS Safari'de scale: 1, Chrome'da scale: 2 dene |
| TR/EN switch çalışmıyor | i18n/{tr,en}.json dosyalarını kontrol et, localStorage temizle |
| Validation <%95 warning | Eksik source'ları manuel ekle veya force-override + risk kabul et |
| Git conflict | `git pull --rebase` sonra yeniden push |
