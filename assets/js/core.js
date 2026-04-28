// AICoderMap — state container, constants, storage, schema validation.
// Leaf module: zero imports.

export const STORAGE = {
  weights: 'acm.v1.weights',
  language: 'acm.v1.language',
  vram: 'acm.v1.vram',
  gpu: 'acm.v1.gpu',
  filters: 'acm.v1.filters',
  sort: 'acm.v1.sort',
  theme: 'acm.v1.theme',
};

export const BENCH_KEYS = [
  'aaIdx',
  'swePro', 'sweV', 'sweMulti',
  'lcb', 'tb2', 'tbHard',
  'tau2', 'mcpA', 'bfcl', 'aaCoding', 'aaAgentic', 'browseComp',
  'cfElo',
  'gpqa', 'aime26', 'hle', 'aaOmni',
  'mmluPro', 'simpleQa', 'mrcr', 'arcAgi2',
];

// cfElo stores raw Codeforces ELO (~1000-3500). compositeScore() needs every
// bench on a 0-100 scale, so this helper normalizes ELO into a percentile.
// (elo - 1000) / 25 → 1500=20, 2500=60, 3000=80, 3500=100. Clamped at edges.
// Every other bench is already 0-100, so it's returned as-is.
export function normalizeBenchScore(key, value) {
  if (value == null || !Number.isFinite(value)) return null;
  if (key === 'cfElo') {
    const pct = (value - 1000) / 25;
    return Math.max(0, Math.min(100, pct));
  }
  return value;
}

export const DEFAULT_WEIGHTS = {
  swePro: 20, tb2: 13, lcb: 13, sweV: 10, tbHard: 7, cfElo: 7,
  aaCoding: 5, mcpA: 5, aaAgentic: 4, tau2: 4,
  browseComp: 3, arcAgi2: 3,
  gpqa: 2, sweMulti: 2, hle: 1, mmluPro: 1,
};

export const PRESETS = {
  'balanced': { ...DEFAULT_WEIGHTS },
  'swe-focused': {
    swePro: 25, sweV: 18, sweMulti: 15, lcb: 12, tb2: 10, tbHard: 10,
    cfElo: 5, aaCoding: 5,
  },
  'agentic-focused': {
    tb2: 18, mcpA: 15, tbHard: 12, browseComp: 12, aaAgentic: 12, tau2: 10,
    swePro: 8, lcb: 8, bfcl: 5,
  },
  // Reasoning / knowledge breadth — covers the bench keys (aaIdx, aime26,
  // aaOmni, mmluPro, simpleQa, mrcr, arcAgi2) the coding-centric presets
  // above leave at zero. Anchors on independent-evaluator composites
  // (GPQA Diamond + AIME 2026 + HLE + ARC-AGI-2) plus knowledge breadth
  // (MMLU-Pro + AA-Omniscience + SimpleQA + MRCR long-context).
  'reasoning-focused': {
    gpqa: 18, aime26: 15, hle: 15, arcAgi2: 12, mmluPro: 10,
    aaIdx: 7, aaOmni: 8, simpleQa: 5, mrcr: 5,
    swePro: 3, lcb: 2,
  },
  'benchmark-only': {
    swePro: 18, sweV: 15, tb2: 13, lcb: 13, tbHard: 10, cfElo: 8,
    sweMulti: 8, gpqa: 7, hle: 5, mmluPro: 3,
  },
};

export const CONTRADICTION_WARN = 3.0;
export const CONTRADICTION_BLOCK = 5.0;

export const TIER_ORDER = { 'frontier': 0, 'open-flagship': 1, 'coder-specialized': 2, 'gemma': 3, 'ollama-local': 4 };

export const State = {
  models: [],
  sources: {},
  gpu: { nvidia: {}, apple: {}, amd: {}, intel: {}, webgpuVendorMap: {} },
  i18n: null,
  i18nFallback: null,
  lang: 'tr',
  weights: { ...DEFAULT_WEIGHTS },
  filters: { deployment: 'all', openOnly: false, tier: 'all', provider: 'all', search: '' },
  sort: { col: 'composite', dir: 'desc' },
  vram: null,
  selectedGpu: 'auto',
  detectedGpu: null,
  dataDeployedAt: null,
  dataEtag: null,
};

export function readStorage(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    if (raw == null) return fallback;
    return JSON.parse(raw);
  } catch (_) {
    return fallback;
  }
}

export function writeStorage(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (_) {
    /* quota or disabled — silent (preferences are best-effort) */
  }
}

export function isValidModel(m) {
  if (!m || typeof m !== 'object') return false;
  if (typeof m.id !== 'string' || !m.id) return false;
  if (typeof m.name !== 'string') return false;
  if (typeof m.tier !== 'string') return false;
  if (!m.bench || typeof m.bench !== 'object') return false;
  // benchUpdated is optional per-cell timestamp map; reject only if present
  // and the wrong shape (must be object of ISO date strings).
  if (m.benchUpdated != null
      && (typeof m.benchUpdated !== 'object' || Array.isArray(m.benchUpdated))) {
    return false;
  }
  return true;
}

export function validateModels(arr) {
  if (!Array.isArray(arr)) return [];
  return arr.filter(isValidModel);
}

export function validateWeights(w) {
  if (!w || typeof w !== 'object') return null;
  const out = {};
  for (const k of BENCH_KEYS) {
    const v = Number(w[k]);
    if (!Number.isFinite(v) || v < 0 || v > 100) return null;
    out[k] = v;
  }
  return out;
}
