# AutoTune: aicodermap PER_MODEL_URL_EXPANSION cascade

## Objective

PER_MODEL_URL_EXPANSION cascade'in slug-variation listelerini öyle tune et ki, fixture'daki (modelId, leaderboard|vendor) çiftlerinin ÇOĞU **ilk denemede** (rank 1) doğru slug'ı yakalasın. Cycle-2'de gözlenen kör noktalar:

- AA: `opus-4-7` → `claude-opus-4-7` (slug claude- prefix gerekiyor — şu an rank 2)
- AA: `gemini-3-1-flash` → `gemini-3-1-flash-lite-preview` (var olan slugVariations'ta yok; rank 99)
- Epoch: `grok-4-20` → `grok-4` (Epoch major-version kanonikleştirme; şu an rank 99)
- Anthropic news: `claude-haiku-4-5` zaten claude- prefix taşır → `claude-{id}` çift prefix üretiyor (`claude-claude-haiku-4-5` 404)

## Metric

- Primary: `hit_rate_at_1` (higher better) — fixture'daki çiftlerin yüzde kaçında doğru slug ilk variation'da yakalanıyor
- Secondary: `hit_rate_at_3` (monitoring) — ilk 3 variation içinde

## Files

| File | Permission | Purpose |
|------|-----------|---------|
| data/sources-whitelist.json | EDITABLE | Optimization target — slugVariations / modelCardSlugVariations / postSlugVariations alanları tune edilir |
| auto/bench.sh | read-only | Evaluation harness |
| auto/eval.py | read-only | Metric extraction (slug expansion simulation) |
| auto/fixtures.json | read-only | Verified (modelId, source, correctSlug) triples |
| auto/.autotune.json | read-only | Configuration |
| auto/results.tsv | append-only | Experiment log |
| All other files | read-only | Keep unchanged |

## Baseline

Set after Phase 5 measurement. Recorded as the first row in `auto/results.tsv`.

## Experiment Loop

Repeat forever:

1. Read `data/sources-whitelist.json` — özellikle `leaderboards[].slugVariations`, `vendors.<v>.modelCardSlugVariations`, `vendors.<v>.postSlugVariations` alanları.
2. Read `auto/run.log` — son misses listesini incele, hangi fixture rank-1 değil görür gör.
3. Hipotez kur. ÖRN: "Anthropic news için `claude-{id}` öne al, ama claude- prefix tekrarı varsa atla" → variation listesini güncelle.
4. Edit `data/sources-whitelist.json` — sadece slugVariations dizilerini değiştir. Diğer alanlar dokunulmaz.
5. Commit: `git add data/sources-whitelist.json && git commit -m "<hipotez kısa>"`
6. Run: `bash auto/bench.sh`
7. Read results: `grep "^hit_rate_at_1:" auto/run.log`
8. Append to `auto/results.tsv` (tab-separated):
   `<ISO8601 timestamp>\t<commit_7char>\t<status>\t<hit_rate_at_1>\t<hit_rate_at_3>\t<HH:MM:SS>\t<description>`
9. Decision:
   - hit_rate_at_1 IMPROVED (strictly higher) → KEEP. Branch advances.
   - hit_rate_at_1 same or worse → DISCARD. `git reset HEAD~1 --hard`
10. Go to step 1. Continue without interruption.

## Rules

1. ONLY modify `data/sources-whitelist.json`. Diğer her şey read-only — özellikle agent.md / SKILL.md / models.json / fixtures.json.
2. Slug variation listelerinin yapısı: array of strings, her string `{id}`, `{family}`, `{N}`, `{variant}` placeholder'larından bir veya birkaçı içerebilir. Eval bu placeholder'ları substitute eder.
3. Each experiment must complete within 30 seconds. Eval ~1s; commit + grep overhead ile 10s altında tamamlanmalı.
4. Simplicity criterion: 6 variation'la rank-1 hit_rate %100 = 12 variation'la %100'den iyi (daha az fetch). Aynı metrikte daha kısa liste tercih edilir.
5. Crash handling: eval Python error → `metric=0.000000`, `status=crash`, sıradaki hipoteze geç. Schema-breaking JSON → `git reset --hard` zorunlu.
6. Continue without interruption — durmadan deneye devam et. Stuck olursan `auto/results.tsv`'yi tara, başka açıdan dene.
7. Daha önce DISCARD edilen yaklaşımları tekrar deneme — `results.tsv` description'larını oku, dedupla.
8. Procedure-vs-data invariant: agent.md'deki cascade prosedürüne dokunmuyoruz; sadece whitelist'teki veri (slug listesi) tune ediliyor. Bu invariant'ın bir parçası.

## Hypothesis Backlog (loop'a başlangıç ipuçları)

- **H1**: AA için `claude-{id}` rank 1, `{id}` rank 2 (mevcut tersine) — Anthropic ailesinde doğru ama OpenAI/xAI/DeepSeek için bozucu olabilir → conditional approach lazım.
- **H2**: Anthropic vendor postSlugVariations'a `{id}` (olduğu gibi) ekle — `claude-haiku-4-5` zaten `claude-` prefix taşır.
- **H3**: AA için Google ailesi slug'ı `{id}-lite-preview` ve `{id}-preview` variant'larını sıraya ekle.
- **H4**: Epoch için `{family}-{N}` (e.g., grok-4) variant'ı ekle — major-version kanonikleştirme.
- **H5**: AA için Qwen ailesi slug'ı `{id}-a35b-instruct` (qwen3-coder-480b → qwen3-coder-480b-a35b-instruct).

## Stop conditions

- hit_rate_at_1 ≥ 0.95 ve 5 ardışık experiment improvement bulamıyor → loop'u durdur, `.audit/tune.json`'u sil, başarıyla bitir.
- 30 ardışık DISCARD → re-read fixtures + analyze, fundamentally different approach dene.
- Context exhaustion / user interrupt → state persist, sonraki `/ds-tune run` resume eder.
