// Shared render builders used by both the comparison table and the model
// cards. Each was previously duplicated in render-card.js + render-table.js;
// the 75/40 coverage thresholds and the ±σ formatting live only here.

import { el } from './dom.js';
import { t } from './i18n.js';
import { daysSinceRelease } from './core.js';
import { fmtLastUpdated, fmtTimeAgo } from './format.js';
import { showContradictionTooltip, hideTooltip } from './overlay.js';

// Contradiction flag (⚠/🚨) with tooltip wiring + screen-reader label.
// FE-03: the delta + source-count the tooltip shows is folded into the label
// itself so screen-reader users get the detail without hover/focus reveal.
export function buildContradictionFlag(c, modelId, benchKey) {
  const flagLabel = `${t('ui.contradiction.title')}: ${t('ui.contradiction.delta')} ${c.delta.toFixed(1)} pp (${c.sources.length})`;
  const flag = el('span', {
    class: 'flag',
    tabindex: '0',
    role: 'button',
    'aria-label': flagLabel,
  }, c.severity === 'danger' ? '🚨' : '⚠');
  if (modelId != null) flag.dataset.modelId = modelId;
  if (benchKey != null) flag.dataset.benchKey = benchKey;
  flag.addEventListener('mouseenter', (e) => showContradictionTooltip(e.currentTarget, c));
  flag.addEventListener('focus', (e) => showContradictionTooltip(e.currentTarget, c));
  flag.addEventListener('mouseleave', hideTooltip);
  flag.addEventListener('blur', hideTooltip);
  return flag;
}

// Single-source pending-corroboration badge — visually distinct from the
// contradiction flag (⚠/🚨): this cell isn't disputed, it just has thin
// evidence (one verified source) that counts toward the composite via the
// exceptional-source-override. Native title tooltip only (no overlay wiring
// needed — this is informational, not interactive detail like a contradiction).
export function buildSingleSourceFlag() {
  return el('span', {
    class: 'flag flag-single-source',
    tabindex: '0',
    role: 'img',
    'aria-label': t('ui.singleSource.title'),
    title: t('ui.singleSource.title'),
  }, '①');
}

// Provisional (vendor-reported) badge — the cell's only source is the vendor's
// own page, admitted because that vendor's raw record on this bench is clean
// (see data.js::provisionalBenches). Distinct from ① single-source: this says
// WHO the single source is, which is the part a reader needs to discount by.
export function buildProvisionalFlag() {
  return el('span', {
    class: 'flag flag-provisional',
    tabindex: '0',
    role: 'img',
    'aria-label': t('ui.provisional.title'),
    title: t('ui.provisional.title'),
  }, 'ⓥ');
}

// "NEW" release badge — the only recency signal on a model row/card. Carries
// the release date in its tooltip so the claim is checkable.
export function buildNewBadge(model) {
  const days = daysSinceRelease(model);
  const tip = `${t('ui.badge.newTip')} · ${model.released || ''}`.trim();
  return el('span', {
    class: 'new-badge',
    title: tip,
    'aria-label': tip,
    'data-days': days == null ? '' : String(days),
  }, t('ui.badge.new'));
}

// Uncertainty range (±σ) — honest precision. Labelled "uncertainty range",
// not a 95% CI; flagged when backed mostly by a single source.
export function uncertaintySpan(sigma, hasCI) {
  return el('span', {
    class: hasCI ? 'composite-unc' : 'composite-unc single-src',
    title: t(hasCI ? 'ui.uncertaintyTip' : 'ui.uncertaintySingleTip'),
  }, `±${sigma.toFixed(1)}`);
}

// Coverage badge tier — the 75/40 percent thresholds in ONE place.
export function coverageClass(pct) {
  return pct >= 75 ? 'full' : pct >= 40 ? 'partial' : 'low';
}

// "last updated" cell: bold date + relative-age suffix.
export function lastUpdatedNode(iso) {
  const wrap = el('span', { class: 'last-updated' });
  const dateStr = fmtLastUpdated(iso);
  if (!dateStr) {
    wrap.textContent = '—';
    return wrap;
  }
  wrap.appendChild(el('strong', { class: 'last-updated-date' }, dateStr));
  const ago = fmtTimeAgo(iso, t);
  if (ago) {
    wrap.appendChild(el('span', { class: 'last-updated-ago' }, ` · ${ago}`));
  }
  return wrap;
}
