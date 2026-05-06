# AICoderMap

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Live demo](https://img.shields.io/badge/live-sungurerdim.github.io%2Faicodermap-67e8a4)](https://sungurerdim.github.io/aicodermap/)

> **Decide which coding model to use, in seconds.** Ranked by your priorities, source contradictions surfaced, local options labeled with the exact quant that fits your GPU. Available in English and Turkish in the live UI.

---

## Why AICoderMap?

A new coding LLM ships every two weeks — Opus 4.7, Kimi K2.6, Qwen3.6-27B, DeepSeek V4 in just the last month. When you actually need to pick one, today's trackers leave you stuck:

- **artificialanalysis.ai / llm-stats / BenchLM** force you into hours of review — no opinion, conflicting scores side by side, you interpret them.
- **aider.chat** has not updated since November 2025 (5 months stale). You are deciding from rotten data.
- **No Turkish coverage anywhere.** Translating each global benchmark page is a separate time tax.

AICoderMap answers the questions that actually shape the decision:

| Question | AICoderMap's answer |
|----------|---------------------|
| **"Which model fits my workflow?"** | Slide the weights to your priorities (SWE-focused, agentic-focused, balanced, or custom) — ranking updates instantly. Four built-in presets plus your own custom mix. |
| **"SWE-Verified 87 vs SWE-Pro 64 — which is real?"** | Every score carries a ⚠ / 🚨 flag when sources disagree. The tooltip lists each source (Anthropic / Scale SEAL / community) with its tier (S = self-reported, I = independent, C = community). Decide on raw evidence, not inflated headlines. |
| **"What runs on my RTX 3070?"** | WebGPU auto-detects your hardware on page load. Every local model gets a label like *"Fits (10 GB · UD-IQ2_XXS)"* — exact quant name plus GB. For models that overflow, you also see *"+3 GB RAM"* offload recommendations. |
| **"How fresh is the data?"** | Each row shows its last-updated date. Refreshed every 14 days at most — none of Aider's 5-month staleness. |
| **"I want to share this on Twitter/Discord."** | One click → PNG export for a card, the comparison table, or the full page. No screenshot fiddling. |
| **"I want to read it in Turkish."** | Every UI label and every benchmark description is written in TR — no translation tax to use the tool. |

---

## 🚀 Status

**Pre-launch — implementation in progress.** 5-week solo part-time plan (M1 Foundation → M5 Launch).

| Document | What it covers |
|----------|----------------|
| [PRD](docs/PRD.md) | Product Requirements (users, features, metrics) |
| [TechSpec](docs/TECHSPEC.md) | Technical Specification (architecture, data, API, security) |
| [ImplGuide](docs/IMPLGUIDE.md) | ⭐ Coding-ready implementation guide |
| [Tasks](docs/TASKS.md) | 23-task / 5-milestone breakdown |
| [Workflow](docs/WORKFLOW.md) | Update workflow (14 happy-path + 5 exception steps) |
| [Pitch](docs/PITCH.md) | Short pitch — for sharing |

---

## 🛠️ Stack

**Single external service: GitHub Pages.** Ongoing cost: $0.

- Vanilla HTML/CSS/JS (no build step, no framework)
- Static JSON data files (the skill regenerates them)
- WebGPU API (browser-native GPU detect)
- html2canvas (vendored, PNG export)
- Local Claude Code skill + research agent (manual update workflow)

---

## 🧰 Development setup

A fresh clone needs only Python 3.10+, Node 18+ (for the linter), and Git Bash on Windows (or any POSIX shell). No package manager, no build step.

**Prerequisites:**
- Python 3.10+ (uses `re.fullmatch`, walrus operator, modern type hints) — standard library only, no `pip install` needed.
- Node 18+ — only for `scripts/regex-lint.js` (validates the regex corpus). Skip if you don't touch the regex library.
- Git Bash / WSL / Linux / macOS for `auto/bench.sh`. On native Windows cmd.exe, use `auto\bench.bat` instead.
- Claude Code (any recent version) for `/aicodermap` skill triggers — the skill + agent are project-scoped and load automatically when you open this directory.

**Local commands** (no install required, all stdlib / vendored):

```bash
# Run the ds-tune evaluation (slug correctness + coverage proxy):
bash auto/bench.sh        # POSIX
auto\bench.bat            # Windows native

# Update verification map from the latest agent artifact:
python scripts/verification-map.py update

# Bootstrap verification map from accumulated sources.json (one-shot):
python scripts/verification-map.py bootstrap

# Merge an agent run into data/* (called by the skill, but also runnable standalone):
python scripts/merge.py

# Lint the regex corpus (Node):
node scripts/regex-lint.js

# Migrate schema (rare, one-shot):
python scripts/migrate-schema.py

# OCR images embedded in vendor blog posts:
python scripts/extract-images.py <url>

# Regenerate sources-whitelist.json `format` keys from the schema:
node scripts/whitelist-format-migration.js
```

**Live preview:** open `index.html` in any modern browser, no server needed. The site reads `data/*.json` over `file://`. For deploy verification, use `https://sungurerdim.github.io/aicodermap/`.

**What is NOT in the repo (gitignored, regenerated on demand):**
- `.aicodermap-agent-out.json` — last research-agent return (overwritten every cycle)
- `.aicodermap-verification-map.json` — cross-cycle confirmed-cell cache (run `python scripts/verification-map.py bootstrap` to rebuild from `data/sources.json`)
- `.aicodermap-images/` — temporary PNG downloads for OCR
- `*.bak`, `*.bak2`, `*.bak3` — rotated backups created by `merge.py`
- `auto/run.log` — eval output (regenerated by `bench.sh`/`bench.bat`)
- `.ruff_cache/`, `__pycache__/` — linter / Python bytecode caches

Everything else (skill, agent, scripts, data, vendor JS, docs, i18n, auto/ folder including fixtures + program.md + results.tsv) is tracked. A fresh clone is reproducible end-to-end.

---

## 📋 Roadmap (5 weeks)

- [x] **M1 Foundation** (Week 1) — Repo + 4 JSON schemas + research agent
- [x] **M2 Core** (Week 2) — Live tracker static render, TR/EN toggle
- [x] **M3 Integration** (Week 3) — 13 must-have features (weights editor + GPU VRAM + contradiction flags + PNG). Bench cross-source coverage continues to climb each refresh — current M4 floor is 30 %, target ≥ 95 %.
- [x] **M4 Polish** (Week 4) — SEO (sitemap, robots, JSON-LD, hreflang, OG/Twitter), a11y skip-link + focus rings, mobile card-stack, doc drift sweep, smoke harness.
- [ ] **M5 Launch** (Week 5) — Simultaneous TR + Global soft launch + 2-week validation

---

## 🔗 Shareable deep-links

Every page state is reflected in the URL — copy the address bar (or click
**Copy share link** in the Export section) and you've shared the exact
ranking the other person will see. The state schema is human-readable and
stable; CLI consumers can construct URLs by hand.

| Param        | Values                                                                            |
|--------------|-----------------------------------------------------------------------------------|
| `lang`       | `tr` \| `en`                                                                      |
| `theme`      | `dark` \| `light`                                                                  |
| `preset`     | `balanced` \| `swe-focused` \| `agentic-focused` \| `reasoning-focused` \| `benchmark-only` \| `custom` |
| `w`          | comma-separated `benchKey:weight` pairs; honoured only when `preset=custom`       |
| `tier`       | `frontier` \| `open-flagship` \| `coder-specialized` \| `gemma` \| `ollama-local` \| `all` |
| `deployment` | `all` \| `cloud` \| `local`                                                       |
| `provider`   | vendor name (URL-encoded) \| `all`                                                |
| `vram`       | integer GB (1..256)                                                               |
| `gpu`        | webgpu vendor key (e.g. `nvidia.rtx-4090`) \| `auto`                              |
| `open`       | `1` \| `0` (open-license-only filter)                                             |
| `search`     | substring (URL-encoded)                                                           |
| `sort`       | `<columnKey>-<asc\|desc>` (e.g. `swePro-desc`, `composite-asc`)                   |

**Example deep-link** — Turkish UI, SWE-focused preset, only models that
fit a 16 GB RTX 4080, sorted by SWE-bench Pro descending:

```
https://sungurerdim.github.io/aicodermap/?lang=tr&preset=swe-focused&deployment=local&vram=16&sort=swePro-desc
```

## 🧪 Programmatic Access (CLI / agent friendly)

The site is a static GitHub Pages deploy backed by stable JSON files. Any
shell tool that can curl + jq can consume it; no auth, no rate limit, no
WAF. The schemas are documented in [`docs/TECHSPEC.md`](docs/TECHSPEC.md) §3.

```bash
BASE=https://sungurerdim.github.io/aicodermap

# All models, just id + provider + tier + composite-relevant scores:
curl -s "$BASE/data/models.json" | jq '
  [.[] | {id, name, provider, tier, open,
          swePro: .bench.swePro, sweV: .bench.sweV,
          lcb:    .bench.lcb,    tb2:  .bench.tb2,
          priceIn: .pricing.api[0].in, priceOut: .pricing.api[0].out}]
'

# Top-10 frontier models by SWE-bench Pro:
curl -s "$BASE/data/models.json" | jq '
  [.[] | select(.tier=="frontier" and .bench.swePro != null)
       | {id, swePro: .bench.swePro, priceIn: .pricing.api[0].in}]
  | sort_by(-.swePro) | .[:10]
'

# Models that fit a 16 GB GPU (vramRequirement <= 16, including null = cloud):
curl -s "$BASE/data/models.json" | jq '
  [.[] | select(.vramRequirement != null and .vramRequirement <= 16)
       | {id, vram: .vramRequirement, license, swePro: .bench.swePro}]
'

# Cross-source contradictions for a model (≥3pp delta):
curl -s "$BASE/data/sources.json" | jq '
  to_entries | map(select(
    (.key | startswith("opus-4-7."))
    and ([.value[].value] | (max - min)) >= 3
  ))
'

# Pull provenance for a single (model, bench) cell:
curl -s "$BASE/data/sources.json" | jq '."opus-4-7.swePro"'
```

A consumer that wants the same view a sharable URL produces can fetch the
URL directly and read the `<script type="application/ld+json">` block — it
contains the `Dataset` schema with `distribution[]` pointing at the three
canonical JSON files.

```bash
# Discover the dataset distribution from JSON-LD:
curl -s "$BASE/" | grep -oP 'application/ld\+json[^<]*<[^>]*>([\s\S]+?)</script>' | head -200
```

## 📚 Data Sources

Every value the tracker shows comes from one of the sources below. Each value carries a `trustScore` based on its tier (I > S > C > U), the number of confirming sources, and recency. Independent sources outweigh vendor self-reports; community sources are used only when no independent or official source exists; forum/social signals are never written into the data.

### I-tier — Independent benchmarks & leaderboards

| Source | URL | Authority for |
|--------|-----|---------------|
| Scale SEAL | [labs.scale.com/leaderboard](https://labs.scale.com/leaderboard) | SWE-bench Pro (1865 tasks), HLE |
| SWE-bench (canonical) | [swebench.com](https://www.swebench.com/) · [github.com/SWE-bench/experiments](https://github.com/SWE-bench/experiments) | SWE-bench Verified, full SWE-bench |
| LiveCodeBench | [livecodebench.github.io](https://livecodebench.github.io/leaderboard.html) · [livecodebench.com](https://livecodebench.com/) | LCB v6 (contamination-free) |
| Terminal-Bench | [tbench.ai](https://tbench.ai/leaderboard) · [terminal-bench.io](https://terminal-bench.io/) | TB2 agentic execution |
| tau-bench | [tau-bench.dev](https://tau-bench.dev/) | tau2 agentic API-use |
| Aider Polyglot | [aider.chat/docs/leaderboards](https://aider.chat/docs/leaderboards/) | aider (warn: stale since Nov 2025) |
| MCP-Atlas | mcp-atlas.dev | mcpA tool-chain quality |
| Artificial Analysis | [artificialanalysis.ai/leaderboards](https://artificialanalysis.ai/leaderboards/models) | aaIdx, aaCoding, aaAgentic, throughput, pricing |
| Vellum Leaderboard | [vellum.ai/llm-leaderboard](https://www.vellum.ai/llm-leaderboard) | independent SWE-V, GPQA, cost+latency |
| llm-stats | [llm-stats.com](https://llm-stats.com/) | broad model catalog |
| LMArena | [lmarena.ai](https://lmarena.ai/) | blind human preference (formerly LMSYS) |
| LiveBench | [livebench.ai](https://livebench.ai/) | contamination-resistant rotating evals |
| Berkeley BFCL | [gorilla.cs.berkeley.edu](https://gorilla.cs.berkeley.edu/leaderboard.html) | function-calling v3/v4 |
| BigCodeBench | [bigcode-bench.github.io](https://bigcode-bench.github.io/) · [HF leaderboard](https://huggingface.co/spaces/bigcode/bigcode-models-leaderboard) | code generation gold standard |
| EvalPlus | [evalplus.github.io](https://evalplus.github.io/leaderboard.html) | HumanEval+ / MBPP+ rigorous |
| HF Open LLM Leaderboard | [huggingface.co/spaces/open-llm-leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard) | open-weight canonical aggregation |
| Klu.ai | [klu.ai/llm-leaderboard](https://klu.ai/llm-leaderboard) | broader benchmark aggregator |
| Papers with Code | [paperswithcode.com/area/code-generation](https://paperswithcode.com/area/code-generation) | peer-reviewed leaderboards |
| arXiv | [arxiv.org](https://arxiv.org/) | original benchmark papers |
| BenchLM | [benchlm.ai](https://benchlm.ai/) | verified vs provisional transparency; ProgramBench tracker |
| ProgramBench | [programbench.com](https://programbench.com/) · [arXiv 2605.03546](https://arxiv.org/abs/2605.03546) | cleanroom program reconstruction (Meta + Stanford + Harvard, 2026-05-05) |
| AgentBench | agentbench.ai | multi-domain agentic |
| MathArena | [matharena.ai](https://matharena.ai/) | AIME math reasoning (auxiliary) |
| Vals.ai | [vals.ai/benchmarks](https://www.vals.ai/benchmarks/) | enterprise-gated benchmark sets |
| LMMarketCap | [lmmarketcap.com](https://lmmarketcap.com/) | hourly market table |

### I-tier — Multi-provider pricing & availability

Models are often hosted on multiple providers at different prices. The tracker shows per-provider pricing in each card and a price range in the comparison table — these are the sources surveyed.

| Source | URL | Extracts |
|--------|-----|----------|
| OpenRouter | [openrouter.ai](https://openrouter.ai/) | provider count, uptime%, alt pricing, throughput |
| Together AI | [together.ai/models](https://www.together.ai/models) | quant variants, $/1M, batch tier |
| Fireworks AI | [fireworks.ai/models](https://fireworks.ai/models) | tier, throughput, batch pricing |
| DeepInfra | [deepinfra.com/models](https://deepinfra.com/models) | $/1M, throughput |
| Groq | [console.groq.com/docs/models](https://console.groq.com/docs/models) · [groq.com/pricing](https://groq.com/pricing) | extreme-fast inference rates |
| Cerebras | [inference-docs.cerebras.ai](https://inference-docs.cerebras.ai/) · [cerebras.ai/inference](https://cerebras.ai/inference) | ultra-fast inference |
| SambaNova Cloud | [cloud.sambanova.ai/models](https://cloud.sambanova.ai/models) | catalog, throughput |
| Replicate | [replicate.com](https://replicate.com/) | open-weight hosting, $/sec |
| Lepton AI | [lepton.ai/pricing](https://www.lepton.ai/pricing) | enterprise pricing |
| Novita AI | [novita.ai/model-api](https://novita.ai/model-api) | catalog + pricing |
| SiliconFlow | [siliconflow.cn/models](https://siliconflow.cn/models) | Chinese providers — Qwen / DeepSeek / MiMo |
| Anyscale | [anyscale.com/endpoints](https://www.anyscale.com/endpoints) | enterprise endpoints |
| Cloudflare Workers AI | [developers.cloudflare.com/workers-ai/models](https://developers.cloudflare.com/workers-ai/models/) | edge regions, free tier |
| AWS Bedrock | [aws.amazon.com/bedrock](https://aws.amazon.com/bedrock/) | enterprise + region matrix |
| Azure AI Foundry | [ai.azure.com/explore/models](https://ai.azure.com/explore/models) | enterprise + region |
| HuggingFace Inference Endpoints | [huggingface.co](https://huggingface.co/) | author canonical card |
| OpenCode Zen / Go | [opencode.ai](https://opencode.ai/) | edge endpoints, latency |
| Lambda Cloud | [lambda.ai/inference](https://lambda.ai/inference) | enterprise throughput |
| Tensorix | [tensorix.ai](https://tensorix.ai/) | infrastructure / niche frontier hosting |

### I-tier — Local runtimes, quants, GPU compatibility

| Source | URL | Extracts |
|--------|-----|----------|
| Ollama Library | [ollama.com/library](https://ollama.com/library) | tags, pullCount, architecture, parameters, license, releasedISO |
| HuggingFace Unsloth | [huggingface.co/unsloth](https://huggingface.co/unsloth) | UD dynamic quants (UD-IQ1_S → UD-Q4_K_XL) |
| HuggingFace bartowski | [huggingface.co/bartowski](https://huggingface.co/bartowski) | most-active quant maintainer |
| HuggingFace mradermacher | [huggingface.co/mradermacher](https://huggingface.co/mradermacher) | high-quality quant set |
| HuggingFace lmstudio-community | [huggingface.co/lmstudio-community](https://huggingface.co/lmstudio-community) | LM Studio-curated GGUFs |
| LM Studio | [lmstudio.ai/models](https://lmstudio.ai/models) | desktop catalog |
| llama.cpp | [github.com/ggerganov/llama.cpp/discussions](https://github.com/ggerganov/llama.cpp/discussions) | empirical VRAM/throughput data |
| MLX (Apple Silicon) | [huggingface.co/mlx-community](https://huggingface.co/mlx-community) | mlx-quantized variants |
| vLLM | [docs.vllm.ai/en/latest/models/supported_models](https://docs.vllm.ai/en/latest/models/supported_models.html) | server-side support matrix |
| sglang | [github.com/sgl-project/sglang](https://github.com/sgl-project/sglang) | structured-output throughput |
| llmfit | [github.com/AlexsJones/llmfit](https://github.com/AlexsJones/llmfit) | 148-model HF curated DB (mirrored locally) |

### S-tier — Vendor official sources

These are the canonical announcements, model cards, pricing pages, and API docs from each model's maker. Used as primary source for release dates, license, context window, and API pricing — and as cross-check against independent benchmarks.

| Vendor | Sources |
|--------|---------|
| Anthropic | [anthropic.com/news](https://www.anthropic.com/news) · [docs.claude.com](https://docs.claude.com/en/docs/about-claude/models) · [pricing](https://platform.claude.com/docs/en/about-claude/pricing) |
| OpenAI | [openai.com/blog](https://openai.com/blog/) · [platform.openai.com/docs/models](https://platform.openai.com/docs/models) |
| Google DeepMind | [deepmind.google/discover](https://deepmind.google/discover/) · [ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models) |
| Mistral | [mistral.ai/news](https://mistral.ai/news) · [docs.mistral.ai](https://docs.mistral.ai/getting-started/models/models_overview/) |
| DeepSeek | [deepseek.com/news](https://www.deepseek.com/) · [api-docs.deepseek.com](https://api-docs.deepseek.com/) |
| xAI | [x.ai/news](https://x.ai/news) · [docs.x.ai/docs/models](https://docs.x.ai/docs/models) |
| Alibaba (Qwen) | [qwenlm.github.io/blog](https://qwenlm.github.io/blog/) · [qwen-lm.github.io](https://qwen-lm.github.io/) |
| Moonshot (Kimi) | [kimi.com/blog](https://www.kimi.com/blog) · [platform.moonshot.cn](https://platform.moonshot.cn/) |
| Z.ai (GLM) | [z.ai/news](https://z.ai/news) · [docs.z.ai](https://docs.z.ai/) |
| Xiaomi (MiMo) | [mimo.xiaomi.com](https://mimo.xiaomi.com/) · [xiaomimimo.github.io](https://xiaomimimo.github.io/) |
| MiniMax | [minimaxi.com/news](https://www.minimaxi.com/news) · [platform.minimaxi.com](https://platform.minimaxi.com/) |
| Nvidia | [build.nvidia.com](https://build.nvidia.com/) · [blogs.nvidia.com](https://blogs.nvidia.com/) |
| Meta (Llama) | [huggingface.co/meta-llama](https://huggingface.co/meta-llama) · [ai.meta.com/blog](https://ai.meta.com/blog/) |
| Google (Gemma) | [huggingface.co/google](https://huggingface.co/google) · [ai.google.dev/gemma](https://ai.google.dev/gemma) |
| StepFun | [stepfun.com](https://www.stepfun.com/) |
| All Hands AI (Devstral) | [all-hands.dev](https://www.all-hands.dev/) |

### C-tier — Aggregators & expert commentary (used only when I/S sources absent)

[ApiDog Blog](https://apidog.com/blog/) · [The Decoder](https://the-decoder.com/) · [DataCamp Blog](https://www.datacamp.com/blog) · [Build Fast With AI](https://www.buildfastwithai.com/) · [Simon Willison](https://simonwillison.net/) · [Latent Space](https://www.latent.space/) · [Swyx](https://www.swyx.io/) · [Awesome-LLM](https://github.com/Hannibal046/Awesome-LLM) · [Awesome-Efficient-LLM](https://github.com/horseee/Awesome-Efficient-LLM) · [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/) (community VRAM reports only) · [Design Arena](https://designarena.ai/leaderboard) (UI auxiliary)

### Trust hierarchy at a glance

```
trustScore = tierWeight × min(verifications, 3)/3 × recencyDecay(date)

  I-tier (independent)  weight 1.0
  S-tier (vendor)       weight 0.7
  C-tier (community)    weight 0.4
  U-tier (forum/social) weight 0.1   ← never written, cross-check only

  recency: <30d=1.0 · <90d=0.85 · <180d=0.70 · <365d=0.50 · ≥365d=0.30
```

When two sources disagree on a value, the one with the higher `trustScore` wins. The losing value still appears in `data/sources.json` with its tier and score, so you can audit every decision.

---

## 🤝 Contributing

Currently pre-launch / solo development. Issues and discussions will open in Phase 2. For now:

- ⭐ Star the repo to follow progress
- 🐛 Open an issue for benchmark-data corrections (after launch)
- 💡 Open a discussion for feature requests

---

## 📜 License

MIT — see [LICENSE](./LICENSE). Code and data are public; attribution appreciated; no takedown power (public benchmark data).

---

## 🧠 Built with

A reusable Claude Code skill + research-agent template — domain-agnostic, cloneable to other tracker projects.

**Author:** [Sungur Erdim](https://github.com/sungurerdim) · sungurerdim@gmail.com
