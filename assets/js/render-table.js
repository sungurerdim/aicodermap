// Comparison table + model list render. Columns are split into helper builders;
// renderAll wires both surfaces together.

import { State, BENCH_KEYS, TIER_ORDER, STORAGE, writeStorage } from './core.js';
import {
  compositeScore, coverageOf, fmtScore, scoreClass, contradictionFor,
  pricingView, fmtPriceRange, fmtContext, fmtLastUpdated,
} from './data.js';
import { gpuCompat, getActiveVram, passesFilters } from './gpu.js';
import { el, clear } from './dom.js';
import { t } from './i18n.js';
import { showContradictionTooltip, hideTooltip } from './overlay.js';
import { buildModelCard } from './render-card.js';

function tierLabel(tier) {
  return t(`ui.tier.${tier}`) || tier;
}

function staticColumns() {
  return [
    { key: 'rank', i18n: 'ui.table.rank', sortable: false, num: true,
      get: (_m, ctx) => ctx.index + 1,
      render: (_m, ctx) => String(ctx.index + 1), cls: 'col-rank' },
    { key: 'name', i18n: 'ui.table.name', sortable: true, sticky: true,
      get: (m) => m.name.toLowerCase(),
      render: (m) => m.name },
    { key: 'provider', i18n: 'ui.table.provider', sortable: true,
      get: (m) => (m.provider || '').toLowerCase(),
      render: (m) => m.provider || '—' },
    { key: 'tier', i18n: 'ui.table.tier', sortable: true,
      get: (m) => TIER_ORDER[m.tier] ?? 99,
      render: (m) => {
        const span = document.createElement('span');
        span.className = `tier-badge ${m.tier}`;
        span.textContent = tierLabel(m.tier);
        return span;
      } },
    { key: 'composite', i18n: 'ui.table.composite', sortable: true, num: true,
      get: (_m, ctx) => ctx.score,
      render: (m, ctx) => {
        const wrap = document.createDocumentFragment();
        const span = document.createElement('span');
        span.className = scoreClass(ctx.score);
        span.textContent = fmtScore(ctx.score);
        wrap.appendChild(span);
        const cov = coverageOf(m, State.weights);
        if (cov != null) {
          const pct = Math.round(cov * 100);
          const cls = `coverage-mini ${pct >= 75 ? 'cov-full' : pct >= 40 ? 'cov-partial' : 'cov-low'}`;
          const covSpan = document.createElement('span');
          covSpan.className = cls;
          covSpan.textContent = `${pct}%`;
          covSpan.title = t('ui.coverageTip');
          wrap.appendChild(covSpan);
        }
        return wrap;
      } },
  ];
}

function benchColumns() {
  return BENCH_KEYS.map(k => ({
    key: `bench.${k}`,
    benchKey: k,
    i18n: `benchmarks.${k}.short`,
    i18nTitle: `benchmarks.${k}.name`,
    sortable: true,
    num: true,
    cls: 'bench-cell-td',
    get: (m) => m.bench?.[k],
    render: (m) => renderBenchValue(m, k),
  }));
}

function renderBenchValue(m, k) {
  const v = m.bench?.[k];
  const wrap = document.createDocumentFragment();
  const span = document.createElement('span');
  span.className = scoreClass(v);
  span.textContent = fmtScore(v);
  wrap.appendChild(span);
  const c = contradictionFor(m.id, k);
  if (!c) return wrap;
  const flag = document.createElement('span');
  flag.className = 'flag';
  flag.textContent = c.severity === 'danger' ? '🚨' : '⚠';
  flag.tabIndex = 0;
  flag.setAttribute('role', 'button');
  flag.setAttribute('aria-label', t('ui.contradiction.title'));
  flag.addEventListener('mouseenter', (e) => showContradictionTooltip(e.currentTarget, c));
  flag.addEventListener('focus', (e) => showContradictionTooltip(e.currentTarget, c));
  flag.addEventListener('mouseleave', hideTooltip);
  flag.addEventListener('blur', hideTooltip);
  wrap.appendChild(flag);
  return wrap;
}

function tailColumns() {
  return [
    { key: 'context', i18n: 'ui.table.context', sortable: true, num: true,
      get: (m) => m.context,
      render: (m) => fmtContext(m.context) },
    { key: 'priceIn', i18n: 'ui.table.priceIn', sortable: true, num: true,
      get: (m) => pricingView(m).range?.in?.[0] ?? null,
      render: (m) => fmtPriceRange(pricingView(m).range?.in) },
    { key: 'priceOut', i18n: 'ui.table.priceOut', sortable: true, num: true,
      get: (m) => pricingView(m).range?.out?.[0] ?? null,
      render: (m) => fmtPriceRange(pricingView(m).range?.out) },
    { key: 'vram', i18n: 'ui.table.vram', sortable: true, num: true,
      get: (m) => m.vramRequirement,
      render: (m) => m.vramRequirement != null ? `${m.vramRequirement} GB` : '—' },
    { key: 'gpuFit', i18n: 'ui.table.gpu', sortable: false,
      get: () => 0,
      render: (m) => {
        const c = gpuCompat(m, getActiveVram());
        const span = document.createElement('span');
        span.className = `compat-badge ${c.kind}`;
        span.textContent = c.label;
        return span;
      } },
    { key: 'lastUpdated', i18n: 'ui.table.lastUpdated', sortable: true,
      get: (m) => m.lastUpdated || '',
      render: (m) => fmtLastUpdated(m.lastUpdated) || '—' },
  ];
}

function buildTableColumns() {
  return [...staticColumns(), ...benchColumns(), ...tailColumns()];
}

function compareValues(a, b, dir) {
  const aNull = a == null || a === '' || (typeof a === 'number' && !Number.isFinite(a));
  const bNull = b == null || b === '' || (typeof b === 'number' && !Number.isFinite(b));
  if (aNull && bNull) return 0;
  if (aNull) return 1;
  if (bNull) return -1;
  let cmp;
  if (typeof a === 'number' && typeof b === 'number') cmp = a - b;
  else cmp = String(a).localeCompare(String(b));
  return dir === 'asc' ? cmp : -cmp;
}

function onSortClick(colKey) {
  if (State.sort.col === colKey) {
    State.sort.dir = State.sort.dir === 'asc' ? 'desc' : 'asc';
  } else {
    State.sort.col = colKey;
    State.sort.dir = 'desc';
  }
  writeStorage(STORAGE.sort, State.sort);
  renderTable();
}

function renderTableHeader(thead, cols) {
  clear(thead);
  for (const col of cols) {
    const th = document.createElement('th');
    th.dataset.col = col.key;
    if (col.num) th.classList.add('num');
    if (col.sticky) th.classList.add('col-name');
    if (col.sortable) {
      th.dataset.sortable = 'true';
      th.addEventListener('click', () => onSortClick(col.key));
      th.tabIndex = 0;
      th.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSortClick(col.key); }
      });
    }
    if (State.sort.col === col.key) th.classList.add('sorted', State.sort.dir);
    th.textContent = t(col.i18n);
    if (col.i18nTitle) {
      const fullName = t(col.i18nTitle);
      if (fullName && fullName !== col.i18nTitle) {
        th.setAttribute('data-tip', fullName);
        th.setAttribute('data-tip-position', 'bottom');
      }
    }
    thead.appendChild(th);
  }
}

function rankedModels() {
  return State.models
    .filter(passesFilters)
    .map(m => ({ model: m, score: compositeScore(m, State.weights) }));
}

function sortRanked(ranked, cols) {
  const sortCol = cols.find(c => c.key === State.sort.col);
  if (sortCol && sortCol.sortable !== false) {
    ranked.sort((A, B) => {
      const va = sortCol.get(A.model, { score: A.score });
      const vb = sortCol.get(B.model, { score: B.score });
      return compareValues(va, vb, State.sort.dir);
    });
  } else {
    ranked.sort((A, B) => compareValues(A.score, B.score, 'desc'));
  }
}

function renderTableBody(tbody, ranked, cols) {
  clear(tbody);
  ranked.forEach((entry, index) => {
    const tr = document.createElement('tr');
    tr.dataset.modelId = entry.model.id;
    const ctx = { index, score: entry.score };
    for (const col of cols) {
      const td = document.createElement('td');
      if (col.num) td.classList.add('num');
      if (col.sticky) td.classList.add('col-name');
      if (col.cls) td.classList.add(col.cls);
      const out = col.render(entry.model, ctx);
      if (out instanceof Node) td.appendChild(out);
      else td.textContent = String(out ?? '—');
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  });
}

export function renderTable() {
  const table = document.getElementById('comparison-table');
  if (!table) return;
  const thead = table.querySelector('thead tr');
  const tbody = table.querySelector('tbody');
  const cols = buildTableColumns();

  renderTableHeader(thead, cols);
  const ranked = rankedModels();
  sortRanked(ranked, cols);
  renderTableBody(tbody, ranked, cols);

  const count = document.getElementById('table-count');
  if (count) count.textContent = `${ranked.length} / ${State.models.length}`;
}

export function renderModelCards() {
  const list = document.getElementById('models-list');
  if (!list) return;
  clear(list);

  const ranked = rankedModels().sort((a, b) => {
    const sa = a.score == null ? -1 : a.score;
    const sb = b.score == null ? -1 : b.score;
    if (sa !== sb) return sb - sa;
    const ta = TIER_ORDER[a.model.tier] ?? 99;
    const tb = TIER_ORDER[b.model.tier] ?? 99;
    if (ta !== tb) return ta - tb;
    return a.model.name.localeCompare(b.model.name);
  });

  if (ranked.length === 0) {
    list.appendChild(el('p', { class: 'loading' }, t('ui.noData')));
  } else {
    ranked.forEach((entry, i) => list.appendChild(buildModelCard(entry.model, i + 1)));
  }

  const count = document.getElementById('models-count');
  if (count) count.textContent = `${ranked.length} / ${State.models.length}`;
}

export function renderAll() {
  renderTable();
  renderModelCards();
}
