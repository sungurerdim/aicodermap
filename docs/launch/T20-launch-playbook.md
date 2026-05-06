# M5 Launch Playbook (T20)

**Owner:** Sungur Erdim · solo, no collaborators.
**Goal:** simultaneous TR + Global soft launch · 10–15 channel intro · 2-week post-launch validation (GO / PIVOT / LITE).

---

## Pre-launch checklist (T-1 day)

- [ ] `git status` clean on `main`; `git push` succeeded; GitHub Pages live URL responds < 2 s.
- [ ] `python scripts/audit-data-coherence.py` exit 0.
- [ ] `python scripts/audit-bench-source-mapping.py` exit 0.
- [ ] `assets/test/smoke.html` over `python -m http.server 8000` — N pass · 0 fail.
- [ ] Lighthouse mobile + desktop both ≥ 90 across Performance / Accessibility / Best Practices / SEO; reports archived under `docs/lighthouse/`.
- [ ] `https://search.google.com/test/rich-results` against the live URL — Dataset + WebSite + SoftwareApplication detected, no errors.
- [ ] `https://sungurerdim.github.io/aicodermap/sitemap.xml` and `/robots.txt` resolve.
- [ ] OG image renders correctly on `https://www.opengraph.xyz/url/` preview.
- [ ] All three CP1 / CP2 / CP3 launch posts ready in TR + EN (T17, T18, T19).
- [ ] Pinned issue drafted: "Launch Day [date] — feedback / data corrections welcome".
- [ ] Repo description and topics set (`gh repo edit --description "…" --add-topic llm-benchmarks --add-topic coding-llm --add-topic ai-tools`).

---

## Channel matrix — TR (Turkish-speaking community)

| # | Channel | Format | Owner action | Notes |
|---|---|---|---|---|
| TR-1 | **AI LAB Discord** (40K members) | #general intro post | one paragraph + link + screenshot PNG export | Mention "tek tıkla PNG paylaş" |
| TR-2 | **YazılımaOrg Discord** (59K members) | #projeler-tanitim | same template | Pin GPU-VRAM filter feature |
| TR-3 | **Patika.dev Discord** (200K members) | #komunite-paylasimlari | same template + brief | Tone: educational, low-marketing |
| TR-4 | **Eksisozluk** | new entry under "yapay zeka kodlama modeli karşılaştırma" | 5–6 line entry, link, no aggressive marketing | Eksi rules — let the entry stand on substance |
| TR-5 | **Twitter/X — Utku Şen** | reply / mention thread | factual mention + link, no DM | Utku posts about LLM tooling regularly |
| TR-6 | **Twitter/X — Ali Tekin** | reply on a relevant thread | technical reply with link | Look for SWE-bench / Cursor threads |
| TR-7 | **Twitter/X — Erhan Meydan** | mention with screenshot | TR Twitter strong signal | Tag with `#YapayZeka #Kodlama` |
| TR-8 | **DonanımHaber** | tip submission | factual product tip | DH editorial tone preferred |

### TR template (post body, 4-6 lines)

```
Merhaba — kodlama-LLM seçimini saniyeler içinde yapan açık-kaynak bir
takipçi yayınladım: AICoderMap. SWE-bench Pro / Verified çelişkilerini
işaretliyor, GPU'na sığacak Unsloth quant'ını yazıyor, ağırlıklarını
sürükleyerek kendi sıralamanı çıkartıyorsun. Her 14 günde bir tazeleniyor,
55 model + 25 benchmark, TR + EN. Geri bildirim çok kıymetli:
https://sungurerdim.github.io/aicodermap/?lang=tr
```

---

## Channel matrix — Global (English-speaking community)

| # | Channel | Format | Owner action | Notes |
|---|---|---|---|---|
| G-1 | **Hacker News — Show HN** | "Show HN: AICoderMap — pick coding LLM by your own weights" | post Tuesday 9-11 ET window | One link + first comment with technical detail |
| G-2 | **r/LocalLLaMA — Show** | self post, flair "Resources" | post weekend morning ET | Lead with VRAM-fitting feature; show GIF of WebGPU detect |
| G-3 | **simonw blog — Tools mention** | email pitch | 200-word pitch, two paragraphs | Cite the SWE-V vs Pro analysis post (T19) as the editorial position |
| G-4 | **awesome-llm-benchmarks** | PR adding repo to README | small PR, single line | Plain markdown, no marketing |
| G-5 | **BenchGecko** | PR adding repo as related project | small PR | If accepted, generates organic backlink |
| G-6 | **Twitter/X announcement thread** | 5-tweet thread | Tuesday post-HN window | Tweet 1: hook · 2: weights demo · 3: VRAM demo · 4: contradiction demo · 5: link |
| G-7 | **dev.to crosspost** | T17 + T18 + T19 republish | use canonical link to GitHub Pages | dev.to community amplification |
| G-8 | **Lobste.rs** | submit only if invited | community gating | Skip if no invite — high noise penalty |
| G-9 | **Latent Space podcast / Swyx blog** | email pitch | 150-word pitch | Cite the editorial weight rationale (d13) |

### EN template (Show HN body, 5-7 lines)

```
AICoderMap — open-source benchmark tracker for coding LLMs that lets you
weight benchmarks yourself. Drag SWE-Pro to 30 %, agentic to 5 %; ranking
updates instantly. Cross-source contradiction flags (>3pp warn, >5pp red).
WebGPU detect → every local model labeled with the exact Unsloth quant
that fits your card. 55 models × 25 benchmarks, refreshed every 14 days.
TR + EN. MIT, $0/mo (GitHub Pages). Feedback welcome.
https://sungurerdim.github.io/aicodermap/
```

---

## Day-of timing (Tuesday recommended)

| Local hour | Action |
|---|---|
| 09:00 IST | TR Twitter announcement thread + pinned tweet on personal account |
| 10:00 IST | TR Discord posts (AI LAB → YazılımaOrg → Patika in that order; 30-min spacing) |
| 11:00 IST | DonanımHaber tip submission |
| 12:00 IST | Eksisozluk entry |
| 16:00 IST / 09:00 ET | Show HN submit |
| 16:30 IST / 09:30 ET | First-comment seed (technical detail) — only if HN post lands at all |
| 17:00 IST | r/LocalLLaMA Show post |
| 18:00 IST | Twitter EN thread |
| 19:00 IST | dev.to T17 (DeepSeek V4) crosspost |
| 20:00 IST | simonw + Latent Space pitches sent |

If Show HN does not flag → wait 4 hours, retry; do NOT submit twice from the same IP within 30 days.

---

## Validation checkpoint (T+14 days)

Decision tree, run on the 14-day mark:

```
Traffic ≥ 200 unique cumulative AND ≥ 5 stars AND ≥ 1 organic mention?
├── YES → GO  (continue CP2, CP3 cadence; queue Phase 2 features S1-S4)
└── NO  → check distribution depth
    │
    ├── ≥ 3 channels seeded but < 100 unique → PIVOT
    │   • Reword tagline (try "VRAM-aware" instead of "weights editor" lead)
    │   • Lead with the GPU feature in next thread cycle
    │   • Re-pitch Latent Space / simonw with the SWE-V vs Pro angle
    │
    └── < 3 channels seeded → LITE
        • Reduce content cadence to CP3-only (1 / quarter)
        • Keep refresh discipline (≤ 14 days) — that's the moat
        • Re-evaluate at T+60 days
```

Source for traffic: GitHub Insights → Traffic tab. Source for stars: GitHub repo header. Source for mentions: manual search "AICoderMap" on Twitter / HN / Reddit / Eksisozluk weekly.

---

## Anti-patterns to avoid

- **Do not** post the same body across all channels in one minute. The Twitter algorithm penalises and the HN community downvotes.
- **Do not** reply to every HN comment. Top three substantive replies, ignore the rest. Save bandwidth.
- **Do not** push after the launch sprint. Refresh discipline (≤ 14 days) is the only thing that compounds; daily content does not.
- **Do not** monetize. Bias-free editorial integrity is compound moat D; sponsorship offers will arrive within 60 days — decline politely, keep the integrity bond.

---

## Post-launch follow-ups (week 3+)

- Open the pinned issue to crowdsource bench corrections with strict format: model id + bench key + source URL + your reading.
- Refresh cycle on a frontier-launch trigger (Kimi K2.7 / Sonnet 4.7 / o5 — whichever ships first).
- T18-style evergreen guides on a quarterly cadence: "Top 5 for 16 GB VRAM", "Top 5 for Apple Silicon", "Top 5 for cost-per-PR".
- T19-style explainer on a quarterly cadence: pick one structural benchmark question per quarter (LCB v6 retirement, BFCL v4 vs v3 scoring shift, MCP-Atlas methodology).
