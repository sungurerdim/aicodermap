// Display formatters: score/price/context/date strings, CSS class mapping,
// pricing view model and bench-key display ordering. No scoring math here
// (scoring.js) and no fetch/provenance logic (data.js).

import { State, BENCH_KEYS } from './core.js';

export function scoreClass(v) {
  if (v == null || !Number.isFinite(v)) return 'score-na';
  if (v >= 70) return 'score-high';
  if (v >= 50) return 'score-mid';
  return 'score-low';
}

// Per-bench unit metadata — keys that deviate from the default "percent" scale.
const BENCH_UNITS = { cfElo: 'elo', webDevElo: 'elo' };
const BENCH_DIRECTION = { aaOmni: 'lower_better' };

export function formatBenchValue(key, value) {
  if (value == null || !Number.isFinite(value)) return '—';
  const unit = BENCH_UNITS[key] || 'percent';
  const dir = BENCH_DIRECTION[key] || 'higher_better';
  if (unit === 'elo') return `${Math.round(value)} ELO`;
  const pct = `${value.toFixed(1)}%`;
  return dir === 'lower_better' ? `${pct} ↓` : pct;
}

export function fmtScore(v, digits = 1) {
  if (v == null || !Number.isFinite(v)) return '—';
  return v.toFixed(digits);
}

// ISO 8601 datetime ("2026-04-28T17:23:45Z") → "2026-04-28 17:23".
export function fmtLastUpdated(s) {
  if (!s || typeof s !== 'string') return '';
  const t = s.indexOf('T');
  return t < 0 ? s : `${s.slice(0, t)} ${s.slice(t + 1, t + 6)}`;
}

// ISO datetime (or YYYY-MM-DD) → "2 gün 4 saat 13 dk önce" / "2d 4h 13m ago".
// Returns '' for invalid input. Uses i18n keys: ui.timeAgo.{justNow,suffix,d,h,m}
export function fmtTimeAgo(s, tFn) {
  if (!s || typeof s !== 'string') return '';
  const iso = s.includes('T') ? s : `${s}T00:00:00Z`;
  const then = new Date(iso);
  if (Number.isNaN(then.getTime())) return '';
  const diffMs = Date.now() - then.getTime();
  if (diffMs < 0) return '';
  const totalMin = Math.floor(diffMs / 60000);
  if (totalMin < 1) return tFn('ui.timeAgo.justNow');
  const days = Math.floor(totalMin / 1440);
  const hours = Math.floor((totalMin % 1440) / 60);
  const mins = totalMin % 60;
  const parts = [];
  if (days) parts.push(`${days}${tFn('ui.timeAgo.d')}`);
  if (hours) parts.push(`${hours}${tFn('ui.timeAgo.h')}`);
  if (mins && days === 0) parts.push(`${mins}${tFn('ui.timeAgo.m')}`);
  if (!parts.length) parts.push(`${totalMin}${tFn('ui.timeAgo.m')}`);
  return `${parts.join(' ')} ${tFn('ui.timeAgo.suffix')}`;
}

// HTTP-date string ("Tue, 28 Apr 2026 14:07:20 GMT") → "2026-04-28 14:07 UTC".
// Returns '' on parse failure so callers can fall back to a static label.
export function fmtDeployTime(httpDate) {
  if (!httpDate) return '';
  const d = new Date(httpDate);
  if (Number.isNaN(d.getTime())) return '';
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())} `
    + `${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())} UTC`;
}

// PERF (2026-06-10): pricing inputs are immutable at runtime (models.json is
// regenerated offline by merge.py), so the derived view is cached per model
// object. The WeakMap drops entries automatically when a reload replaces
// State.models.
const _pricingViewCache = new WeakMap();

// Multi-provider pricing view. Schema is canonical: `pricing.api` is an
// array of provider entries; `pricing.subscription` is an array of tier
// entries; `pricing.range` is the precomputed min/max envelope. Anything
// else is a contract violation that the SSOT audit catches.
export function pricingView(model) {
  const cached = _pricingViewCache.get(model);
  if (cached) return cached;
  const p = model.pricing || {};
  const api = Array.isArray(p.api) ? p.api : [];
  const ins = api.map(e => e?.in).filter(v => v != null);
  const outs = api.map(e => e?.out).filter(v => v != null);
  const chs = api.map(e => e?.cacheHit).filter(v => v != null);
  const range = p.range || {
    in: ins.length ? [Math.min(...ins), Math.max(...ins)] : null,
    out: outs.length ? [Math.min(...outs), Math.max(...outs)] : null,
    cacheHit: chs.length ? [Math.min(...chs), Math.max(...chs)] : null,
  };
  const subs = Array.isArray(p.subscription) ? p.subscription : [];
  // Blended: cheapest input + cheapest output combined via 3:1 input:output ratio.
  // Represents a typical mixed workload (3 input tokens per 1 output token).
  const minIn = range.in?.[0];
  const minOut = range.out?.[0];
  const blended = (minIn != null && minOut != null)
    ? (minIn * 3 + minOut) / 4
    : null;
  const view = { providers: api, range, subscriptions: subs, blended };
  _pricingViewCache.set(model, view);
  return view;
}

export function fmtPriceMoney(v) {
  if (v == null) return '—';
  return `$${Number(v).toString()}`;
}

export function fmtPriceRange(pair) {
  if (!pair) return '—';
  const [a, b] = pair;
  if (a == null && b == null) return '—';
  if (a === b || b == null) return fmtPriceMoney(a);
  return `${fmtPriceMoney(a)}–${fmtPriceMoney(b)}`;
}

export function fmtPriceCell(model) {
  const v = pricingView(model);
  const inS = fmtPriceRange(v.range?.in);
  const outS = fmtPriceRange(v.range?.out);
  if (inS === '—' && outS === '—') return '—';
  return `${inS} / ${outS}`;
}

export function fmtContext(n) {
  if (!Number.isFinite(n)) return '—';
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(n % 1_000_000 === 0 ? 0 : 1)}M`;
  if (n >= 1000) return `${Math.round(n / 1000)}K`;
  return String(n);
}

// Bench-key display ordering shared by the comparison table (columns) and the
// model card (grid). Splits BENCH_KEYS into the benches the active preset
// scores (weight > 0) and those it excludes (weight 0). The in-preset group is
// sorted by weight descending so the heaviest benchmark sits first (leftmost);
// ties keep BENCH_KEYS order (stable sort). The excluded group keeps BENCH_KEYS
// order. Recomputed on every render, so switching preset re-orders both surfaces.
export function orderedBenchKeys(weights) {
  const w = weights || State.weights || {};
  const included = [];
  const excluded = [];
  for (const k of BENCH_KEYS) {
    if ((Number(w[k]) || 0) > 0) included.push(k);
    else excluded.push(k);
  }
  included.sort((a, b) => (Number(w[b]) || 0) - (Number(w[a]) || 0));
  return { included, excluded };
}
