"""Skill constants — single source of truth.

FAZ 3.2 (2026-05-07): consolidated from SKILL.md CONSTANTS block.

Numeric thresholds primarily live in `data/sources-whitelist.json._schema.contracts`
and are loaded via `scripts/lib/whitelist.contracts(whitelist)`. The values
below are the SAFE_DEFAULTS the runtime falls back to when the contracts
block is missing/incomplete. SKILL.md, agent.md, and merge.py reference this
module rather than duplicating values.

Categories:
  - Coverage gates (advisory + hard)
  - Resource ceilings (FAZ 1 — hard, per-dispatch)
  - Freshness contract (FAZ 2.2)
  - Cycle metadata (deploy wait, retry counts, family floor)
  - Quality rules (NOT effort caps)
  - File paths (gitignored artifacts)
"""

from __future__ import annotations

# ── Contradiction & coverage gates ─────────────────────────────────────────
CONTRADICTION_WARN_PP = 3.0  # pp delta → YELLOW (auto-resolve via trustScore)
CONTRADICTION_BLOCK_PP = 5.0  # pp delta → RED (auto-resolve, log loudly)
COVERAGE_TARGET = 0.85  # ADVISORY. Cumulative provenance coverage; never blocks commit.
COVERAGE_HARD_BLOCK = 0.50  # ADVISORY. Below → louder CHANGELOG warning, still commits.
ABSOLUTE_COVERAGE_FLOOR = (
    0.30  # HARD BLOCK after AICODERMAP_MX2_BLOCK=1; .bak rollback below.
)
MIN_SOURCES_PER_FILLED_CELL = 2  # MX5: <2 distinct URLs → benchQuarantine[key]=true.
COMPLETENESS_RETRY_LIMIT = 1  # Single retry per refresh.

# ── Resource ceilings (FAZ 1 — HARD, per-dispatch) ─────────────────────────
BATCH_WALLCLOCK_SEC = 600  # FAZ 1.3: per-batch wallclock cap (10 min).
BATCH_WALLCLOCK_SOFT_STOP_SEC = 30  # FAZ 1.3: agent self-stops at deadline-30s.
AGENT_BUDGET_BUFFER = 50  # FAZ 1: tool-call ceiling per agent.
MAX_PARALLEL = 16  # 2026-06-06: 10→16. With FFD batch-packing a 76-model cycle
# is ~13 batches, so 16 fits the whole plan in ONE wave — the orchestrator
# dispatches every batch in a single message and the harness schedules them
# continuously (a finishing agent frees a slot immediately), eliminating the
# wave-barrier idle time where fast agents waited ~290s for the slowest in their
# wave. 16 also matches the workflow concurrency ceiling (min(16, cores-2)).

# ── Confirmed-cell skip (TTL removed 2026-06-27) ───────────────────────────
# Bench-LEVEL skip (T2) applies ONLY to FILLED+confirmed cells. GAP (never-found)
# cells are re-queried every full-run — there is no gap-level skip tier.
#
# Doctrine: a released model's published benchmark score is FROZEN, so a cell
# confirmed by ≥MIN_VERIFICATIONS_FOR_SKIP agreeing sources is settled and never
# re-fetched on a clock. Skip iff `confirmed and not contradicted` — there is no
# time backstop (the prior FRESHNESS_TTL_DAYS window was removed: it only slowed
# the cycle, since a frozen score doesn't drift). Re-validation is EVENT-driven —
# detect-anomalies runs on live data every cycle and a contradiction/peer-outlier
# flips `contradicted`, re-opening the cell. MIN_VERIFICATIONS_FOR_SKIP stays as
# part of the `confirmed` flag's definition (derived in verification-map.py).
MIN_VERIFICATIONS_FOR_SKIP = 3  # ≥3 agreeing numeric sources → `confirmed`.

# ── Hybrid dispatch (FAZ 4.C) ──────────────────────────────────────────────
HAIKU_GATHER_MIN_AVG_OBS = 3  # Avg observations per target_model. Below → sonnet retry.

# ── Cycle metadata ─────────────────────────────────────────────────────────
STALE_DAYS = 14  # M5 freshness gate.
DEPRECATION_GRACE_DAYS = 60  # vendor deprecated → archive after this.
DEPLOY_WAIT_SEC = 90  # GitHub Pages settle time.
AGENT_RETRY = 1  # Single agent retry per cycle.
FAMILY_BASELINE_MIN = 30  # refresh-all: |models[]+newModels[]| floor.

# ── Bench-key family sets (SSOT — were duplicated across scripts) ──────────
# Elo-scale benches (raw rating, NOT 0-100): drive the Elo-sibling-misfile
# filter (local-synth C1) + the anomaly source-mismatch detector. Was defined
# as ELO_FAMILY / _ELO_SIBLINGS in detect-anomalies.py + local-synth.py.
ELO_BENCH_KEYS = frozenset({"cfElo", "webDevElo", "lmArenaElo"})
# Artificial Analysis OWN definitional composite indices (no one else computes
# them → a stored value disagreeing with AA's is a misfile). Was duplicated in
# apply-aa-authoritative.py + audit-agent-misfiles.py.
AA_COMPOSITE_KEYS = frozenset({"aaIdx", "aaCoding", "aaAgentic"})
# Benches AA MEASURES (independent variance allowed; only corrected when outside
# AA's observed envelope). Same two scripts duplicated this.
AA_MEASURED_KEYS = frozenset({"gpqa", "hle", "tau2", "tbHard"})

# ── Quality rules (correctness, NOT effort caps) ───────────────────────────
VERIFICATION_AGREEMENT_PP = 1.5  # Within 1.5pp = agreement; otherwise contradiction.
PARALLEL_SOURCES = 5  # Concurrent source fetches (parallelism guideline).
PARALLEL_MODELS = 5  # Concurrent model surveys (parallelism guideline).
COMPLETENESS_TERMINATION = True  # Sole research termination condition.

# ── Termination conditions (all four MUST hold before agent emits) ─────────
# 1. Every leaderboards[] entry visited (200 + extract OR unreachable + fallback OR _runtime.unhealthy).
# 2. Every vendors[] entry with perModelUrl/modelCardUrl/postUrl attempted per model.
# 3. Every priorityCells[] entry attempted (FAZ 2.3 authoritative work list).
# 4. Every still-empty cell carries a gaps[] entry; advisory GAP_VALIDITY_GATE never strips.

# ── Source format fetch-quality weights (SSOT — merge.py + eval.py) ────────
# Mirrors the orchestrator's deep-fetch quality assessment: static sources
# score 1.0; image-embedded / SPA sources score lower; bot-blocked lowest.
FORMAT_WEIGHTS: dict[str, float] = {
    "static_html_table": 1.0,
    "static_html_article": 1.0,
    "static_markdown": 1.0,
    "static_json_api": 1.0,
    "github_raw_json": 1.0,
    "github_raw_markdown": 1.0,
    "meta_tag_extract": 1.0,
    "pdf_report": 0.7,
    "spa_partial": 0.5,
    "image_embedded": 0.5,
    "spa_full": 0.3,
    "bot_blocked": 0.1,
}

# ── File paths (gitignored artifacts) ──────────────────────────────────────
VERIFICATION_MAP_PATH = ".aicodermap-verification-map.json"
SINGLE_ARTIFACT_PATH = ".aicodermap-agent-out.json"
LEADERBOARD_SNAPSHOTS_DIR = "data/.leaderboard-snapshots/"
LEADERBOARD_INDEX_PATH = "data/.leaderboard-snapshots/_index.json"
TELEMETRY_DIR = "data/_telemetry/"
