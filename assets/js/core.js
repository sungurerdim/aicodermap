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
  'lcbV6', 'tb2',
  'tau2', 'mcpA', 'bfcl', 'aaCoding', 'aaAgentic',
  'gpqa', 'aime26', 'hle', 'aider', 'aaOmni',
];

export const DEFAULT_WEIGHTS = {
  swePro: 22, tb2: 15, lcbV6: 15, sweV: 10, aider: 10,
  aaCoding: 7, aaAgentic: 5, tau2: 5, mcpA: 5,
  gpqa: 2, sweMulti: 2, hle: 2,
};

export const PRESETS = {
  'balanced': { ...DEFAULT_WEIGHTS },
  'swe-focused': {
    swePro: 30, sweV: 20, sweMulti: 15, tb2: 10, lcbV6: 10, aider: 10,
    aaCoding: 5, aaAgentic: 0, tau2: 0, mcpA: 0, gpqa: 0, hle: 0,
  },
  'agentic-focused': {
    tb2: 22, mcpA: 18, tau2: 13, aaAgentic: 12, swePro: 10, lcbV6: 10,
    bfcl: 10, gpqa: 5, sweV: 0, aider: 0, aaCoding: 0, sweMulti: 0, hle: 0,
  },
  'benchmark-only': {
    swePro: 20, sweV: 15, tb2: 15, lcbV6: 15, aider: 10, gpqa: 10,
    sweMulti: 10, hle: 5, aaCoding: 0, aaAgentic: 0, tau2: 0, mcpA: 0,
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
  filters: { deployment: 'all', openOnly: false, tier: 'all', search: '' },
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

// DATA_CONTRACT guard: bench.<k> must be number|null. Defensively unwrap
// {value, trustScore} wrappers if they slip in from agent emit shape.
export function unwrapBenchGuard(arr) {
  let unwrapped = 0;
  for (const m of arr) {
    if (!m.bench || typeof m.bench !== 'object') continue;
    for (const k of Object.keys(m.bench)) {
      const v = m.bench[k];
      if (v && typeof v === 'object' && !Array.isArray(v) && 'value' in v) {
        m.bench[k] = (typeof v.value === 'number' ? v.value : null);
        unwrapped++;
      }
    }
  }
  if (unwrapped > 0) {
    console.warn(`[aicodermap] DATA_CONTRACT violation: ${unwrapped} bench cell(s) arrived wrapped — defensively unwrapped.`);
  }
}

export function validateModels(arr) {
  if (!Array.isArray(arr)) return [];
  const filtered = arr.filter(isValidModel);
  unwrapBenchGuard(filtered);
  return filtered;
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
