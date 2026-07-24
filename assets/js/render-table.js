// Comparison table + model list render. Columns are split into helper builders;
// renderAll wires both surfaces together.

import {
  State, TIER_ORDER, STORAGE, writeStorage, DEFAULT_PRESET, DEFAULT_SCORE_FN,
  isRecentRelease, daysSinceRelease,
} from './core.js';
import {
  buildContradictionFlag, buildSingleSourceFlag, buildProvisionalFlag, buildNewBadge,
  uncertaintySpan, coverageClass, lastUpdatedNode,
} from './render-shared.js';
import { contradictionFor, isSingleSourceCell, provisionalBenches } from './data.js';
import { coverageOf, effectiveScore, rankBands, presetTiersFor } from './scoring.js';
import {
  fmtScore, scoreClass, pricingView, fmtPriceRange, fmtContext,
  orderedBenchKeys,
} from './format.js';
import { gpuCompat, getActiveVram, passesFilters } from './gpu.js';
import { el, clear } from './dom.js';
import { t, tierLabel } from './i18n.js';
import { buildModelCard } from './render-card.js';

function staticColumns() {
  return [
    { key: 'rank', i18n: 'ui.table.rank', sortable: false, num: true,
      get: (_m, ctx) => ctx.band ? ctx.band.rank : ctx.index + 1,
      render: (_m, ctx) => {
        // Granular ordinal composite rank (stable across sort column). The ±σ on
        // the score + significance-break dividers carry the uncertainty story;
        // the rank number stays discriminating and familiar.
        const span = document.createElement('span');
        span.className = 'rank-num';
        span.textContent = String(ctx.band ? ctx.band.rank : ctx.index + 1);
        span.title = t('ui.rankTip');
        return span;
      }, cls: 'col-rank' },
    { key: 'name', i18n: 'ui.table.name', sortable: true, sticky: true,
      get: (m) => m.name.toLowerCase(),
      render: (m) => {
        // F6 (2026-05-18): name → card anchor link. Clicking jumps to the
        // model card in #models grid + adds a brief :target highlight.
        const a = document.createElement('a');
        a.href = `#card-${m.id}`;
        a.className = 'model-name-link';
        a.textContent = m.name;
        a.addEventListener('click', (ev) => {
          ev.preventDefault();
          const target = document.getElementById(`card-${m.id}`);
          if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            target.classList.remove('is-target');
            // restart animation
            // eslint-disable-next-line no-void
            void target.offsetWidth;
            target.classList.add('is-target');
            setTimeout(() => target.classList.remove('is-target'), 1800);
          }
        });
        return a;
      },
      // Gated rows show HOW MANY required benches are missing (the band header
      // alone read as "one missing test" even when a model lacks four). The
      // count marker's tooltip lists the missing benches by short label.
      renderExtra: (m, ctx) => {
        const tiers = presetTiersFor(m, State.activePresetName || DEFAULT_PRESET);
        const frag = document.createDocumentFragment();
        // Recency first: a fresh release is the one thing a reader scanning for
        // news needs to spot without reading the date column.
        if (isRecentRelease(m)) frag.appendChild(buildNewBadge(m));
        if (!ctx.band || !ctx.band.gated) {
          // A model ranking on the new-release grace says so explicitly — it is
          // competing with cells the older models were also measured on, but
          // the leaderboard-only benches simply don't exist for it yet.
          if (ctx.band && ctx.band.newGrace) {
            frag.appendChild(el('span', {
              class: 'prelim-chip is-new-grace',
              'data-tip': t('ui.badge.newGraceTip'),
            }, t('ui.badge.newGrace')));
            return frag;
          }
          // G3 (2026-07-15): LMArena-style "Preliminary" chip — model ranks
          // normally but its evidence base is thin (missing critical benches
          // or <50% profile coverage). Distinct from the gated band below.
          const cov = ctx.band ? ctx.band.coverage : null;
          const thin = tiers.isLimitedCoverage || (Number.isFinite(cov) && cov < 0.5);
          if (thin) {
            frag.appendChild(el('span', {
              class: 'prelim-chip',
              'data-tip': t('ui.badge.preliminaryTip'),
            }, t('ui.badge.preliminary')));
          }
          return frag.childNodes.length ? frag : null;
        }
        const missing = [...new Set([...tiers.missingRequired, ...tiers.missingCritical])];
        if (missing.length) {
          const labels = missing.map(k => t(`benchmarks.${k}.short`) || k).join(', ');
          frag.appendChild(el('span', {
            class: 'gated-missing-count',
            'data-tip': `${t('vendorPanel.missingTip') || 'missing benches'}: ${labels}`,
          }, `⚠${missing.length}`));
        }
        return frag.childNodes.length ? frag : null;
      } },
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
        if (ctx.band && Number.isFinite(ctx.band.sigma) && ctx.score != null) {
          wrap.appendChild(uncertaintySpan(ctx.band.sigma, ctx.band.hasCI));
        }
        const cov = coverageOf(m, State.weights);
        if (cov != null) {
          const pct = Math.round(cov * 100);
          const cls = `coverage-mini cov-${coverageClass(pct)}`;
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
  // Preset-weighted order: in-preset benches first (weight desc), then the
  // excluded ones grouped at the right. firstExcluded marks the boundary so
  // the header/body can draw a divider between the two groups.
  const { included, excluded } = orderedBenchKeys(State.weights);
  const firstExcluded = excluded.length ? excluded[0] : null;
  return [...included, ...excluded].map(k => ({
    key: `bench.${k}`,
    benchKey: k,
    i18n: `benchmarks.${k}.short`,
    i18nTitle: `benchmarks.${k}.name`,
    sortable: true,
    num: true,
    cls: 'bench-cell-td',
    groupDivider: k === firstExcluded,
    get: (m) => m.bench?.[k],
    render: (m) => renderBenchValue(m, k),
  }));
}

function renderBenchValue(m, k) {
  const v = m.bench?.[k];
  const wrap = document.createDocumentFragment();
  // Contradiction flag sits to the LEFT of the value: these cells are
  // right-aligned, so a trailing flag pushed every flagged number off the
  // right edge and broke the decimal-column alignment. Flag-then-value keeps
  // the number flush-right and aligned across all rows.
  const c = contradictionFor(m.id, k);
  if (c) {
    wrap.appendChild(buildContradictionFlag(c, m.id, k));
  } else if (v != null && provisionalBenches(m).has(k)) {
    wrap.appendChild(buildProvisionalFlag());
  } else if (v != null && isSingleSourceCell(m.id, k)) {
    wrap.appendChild(buildSingleSourceFlag());
  }
  const span = document.createElement('span');
  span.className = scoreClass(v);
  span.textContent = fmtScore(v);
  wrap.appendChild(span);
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
    { key: 'blended', i18n: 'pricing.blended', sortable: true, num: true,
      get: (m) => pricingView(m).blended ?? null,
      render: (m) => {
        const b = pricingView(m).blended;
        if (b == null) return '—';
        return `$${b.toFixed(2)}`;
      } },
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
    // Release date is sortable so "what shipped recently" is one click away —
    // lastUpdated answers "when did WE refresh this", which is a different
    // question and was previously the only date a user could sort on.
    { key: 'released', i18n: 'ui.table.released', sortable: true,
      get: (m) => m.released || '',
      render: (m) => m.released || '—' },
    { key: 'lastUpdated', i18n: 'ui.table.lastUpdated', sortable: true,
      get: (m) => m.lastUpdated || '',
      render: (m) => lastUpdatedNode(m.lastUpdated) },
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

// Sort clicks/keys are delegated: two listeners on the persistent header row
// instead of 2×N per-column listeners re-created every render.
function wireHeaderSort(headerRow) {
  if (headerRow.dataset.sortWired) return;
  headerRow.dataset.sortWired = 'true';
  const colOf = (e) => {
    const th = e.target.closest && e.target.closest('th[data-sortable="true"]');
    return th ? th.dataset.col : null;
  };
  headerRow.addEventListener('click', (e) => {
    const col = colOf(e);
    if (col) onSortClick(col);
  });
  headerRow.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    const col = colOf(e);
    if (col) { e.preventDefault(); onSortClick(col); }
  });
}

function renderTableHeader(thead, cols) {
  wireHeaderSort(thead);
  clear(thead);
  for (const col of cols) {
    const th = document.createElement('th');
    th.dataset.col = col.key;
    if (col.num) th.classList.add('num');
    if (col.sticky) th.classList.add('col-name');
    if (col.groupDivider) th.classList.add('bench-group-divider');
    if (col.sortable) {
      th.dataset.sortable = 'true';
      th.tabIndex = 0;
      th.setAttribute('aria-sort', 'none');
    }
    if (State.sort.col === col.key) {
      th.classList.add('sorted', State.sort.dir);
      th.setAttribute('aria-sort', State.sort.dir === 'asc' ? 'ascending' : 'descending');
    }
    th.textContent = t(col.i18n);
    if (col.i18nTitle) {
      const fullName = t(col.i18nTitle);
      if (fullName && fullName !== col.i18nTitle) {
        th.setAttribute('data-tip', fullName);
        th.setAttribute('data-tip-position', 'bottom');
      }
    }
    // Bench column: dynamic weight badge + dim out when excluded by preset.
    if (col.benchKey) {
      const weight = Number(State.weights?.[col.benchKey]) || 0;
      if (weight > 0) {
        const badge = document.createElement('span');
        badge.className = 'th-weight';
        badge.textContent = String(weight);
        badge.title = `${t('ui.weights.weightLabel') || 'Weight'}: ${weight}`;
        th.appendChild(document.createTextNode(' '));
        th.appendChild(badge);
      } else {
        th.classList.add('th-excluded');
        th.setAttribute('data-tip', t('ui.weights.excluded') || 'Excluded by active preset');
        th.setAttribute('data-tip-position', 'bottom');
      }
    }
    thead.appendChild(th);
  }
}

function rankedModels() {
  // F1+F2 (2026-05-18): effectiveScore dispatches to compositeScore (atomic)
  // or vendorConsensusScore based on State.scoreFn (set by applyPreset).
  // FE-04: exclude archived models here so table rows and both count badges
  // match what the card grid shows (models.css hides archived cards; rankBands
  // already excludes them from the leaderboard band computation below).
  const filtered = State.models.filter(m => (m.status || 'active') !== 'archived' && passesFilters(m));
  // CI-overlap rank bands (2026-05-27) — only on the AICM atomic path; the
  // vendorConsensus path scores differently so bands would mismatch. bandById
  // gives each row its composite tier + uncertainty (sigma) regardless of which
  // column the table is sorted by.
  let bandById = null;
  if ((State.scoreFn || DEFAULT_SCORE_FN) !== 'vendorConsensus') {
    const bands = rankBands(filtered, State.weights, State.activePresetName);
    bandById = new Map(bands.map(b => [b.id, b]));
  }
  return filtered.map(m => ({
    model: m,
    score: effectiveScore(m, State.weights, State.activePresetName),
    band: bandById ? (bandById.get(m.id) || null) : null,
  }));
}

function sortRanked(ranked, cols) {
  const sortCol = cols.find(c => c.key === State.sort.col);
  // Gate-aware composite ordering: in the canonical leaderboard view (composite
  // desc) rank-gated models (missing a required bench / below coverage floor)
  // always sink below the ranked set, mirroring rankBands so the band divider
  // lines up. Other sorts leave gated rows in place (they keep the is-rank-gated
  // marker but are not repositioned), consistent with cluster-break handling.
  const gateAware = State.sort.col === 'composite' && State.sort.dir === 'desc';
  if (sortCol && sortCol.sortable !== false) {
    ranked.sort((A, B) => {
      if (gateAware) {
        const ag = A.band && A.band.gated ? 1 : 0;
        const bg = B.band && B.band.gated ? 1 : 0;
        if (ag !== bg) return ag - bg;
      }
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
  // Significance-break dividers only make sense in composite-descending order
  // (the band clusters are computed in that order). Other sorts keep the stable
  // composite rank number but draw no dividers.
  const showBreaks = State.sort.col === 'composite' && State.sort.dir === 'desc';
  let bandHeaderShown = false;
  ranked.forEach((entry, index) => {
    // Limited-coverage band header — inserted once, before the first gated row,
    // in the composite-desc view (the only order where gated rows are pooled at
    // the bottom). Spans the full table width.
    if (showBreaks && !bandHeaderShown && entry.band && entry.band.gated) {
      const hr = document.createElement('tr');
      hr.className = 'limited-coverage-band-header';
      const td = document.createElement('td');
      td.colSpan = cols.length;
      td.textContent = t('ui.table.limitedCoverageBand');
      hr.appendChild(td);
      tbody.appendChild(hr);
      bandHeaderShown = true;
    }
    const tr = document.createElement('tr');
    tr.dataset.modelId = entry.model.id;
    if (entry.band && entry.band.gated) tr.classList.add('is-rank-gated');
    if (showBreaks && index > 0 && entry.band && ranked[index - 1].band
        && entry.band.cluster !== ranked[index - 1].band.cluster) {
      tr.classList.add('cluster-break');
    }
    const ctx = { index, score: entry.score, band: entry.band };
    for (const col of cols) {
      const td = document.createElement('td');
      if (col.num) td.classList.add('num');
      if (col.sticky) td.classList.add('col-name');
      if (col.cls) td.classList.add(col.cls);
      if (col.groupDivider) td.classList.add('bench-group-divider');
      // Bench column body cells dim out when the preset excludes the bench
      // (weight === 0). Keeps them visible (data is real) but visually
      // de-emphasises so the user sees what's actually counted.
      if (col.benchKey && (Number(State.weights?.[col.benchKey]) || 0) === 0) {
        td.classList.add('excluded');
      }
      const out = col.render(entry.model, ctx);
      if (out instanceof Node) td.appendChild(out);
      else td.textContent = String(out ?? '—');
      if (typeof col.renderExtra === 'function') {
        const extra = col.renderExtra(entry.model, ctx);
        if (extra instanceof Node) td.appendChild(extra);
      }
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  });
}

export function renderTable(precomputed) {
  const table = document.getElementById('comparison-table');
  if (!table) return;
  const thead = table.querySelector('thead tr');
  const tbody = table.querySelector('tbody');
  const cols = buildTableColumns();

  renderTableHeader(thead, cols);
  // renderAll passes the ranked rows it already computed (sortRanked sorts in
  // place, so it hands over a copy); direct callers still compute locally.
  const ranked = precomputed || rankedModels();
  sortRanked(ranked, cols);
  renderTableBody(tbody, ranked, cols);

  const count = document.getElementById('table-count');
  if (count) count.textContent = `${ranked.length} / ${State.models.length}`;
}

export function renderModelCards(precomputed) {
  const list = document.getElementById('models-list');
  if (!list) return;
  clear(list);

  const ranked = (precomputed || rankedModels()).sort((a, b) => {
    // Rank-gated cards (limited coverage) sink to the bottom, matching the table
    // band ordering. Within each group: score desc, then tier, then name.
    const ag = a.band && a.band.gated ? 1 : 0;
    const bg = b.band && b.band.gated ? 1 : 0;
    if (ag !== bg) return ag - bg;
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
    // G10 (2026-07-15): progressive render. Building all ~96 cards up front
    // made the initial DOM ~87k px tall and dominated first-render cost. The
    // first chunk renders synchronously; the rest append when the sentinel
    // scrolls near the viewport (single rAF chunk per intersection).
    const CHUNK = 12;
    const buildCard = (entry, i) => buildModelCard(entry.model, i + 1, {
      gated: !!(entry.band && entry.band.gated),
      score: entry.score,
      band: entry.band,
    });
    ranked.slice(0, CHUNK).forEach((entry, i) => list.appendChild(buildCard(entry, i)));
    if (ranked.length > CHUNK && 'IntersectionObserver' in window) {
      let next = CHUNK;
      const sentinel = el('div', { class: 'cards-sentinel', 'aria-hidden': 'true' });
      list.appendChild(sentinel);
      const io = new IntersectionObserver((entries) => {
        if (!entries.some(e => e.isIntersecting)) return;
        const end = Math.min(next + CHUNK, ranked.length);
        for (let i = next; i < end; i++) list.insertBefore(buildCard(ranked[i], i), sentinel);
        next = end;
        if (next >= ranked.length) { io.disconnect(); sentinel.remove(); }
      }, { rootMargin: '1200px 0px' });
      io.observe(sentinel);
    } else {
      ranked.slice(CHUNK).forEach((entry, i) => list.appendChild(buildCard(entry, CHUNK + i)));
    }
  }

  const count = document.getElementById('models-count');
  if (count) count.textContent = `${ranked.length} / ${State.models.length}`;
}

// New-releases strip — the site's news channel. Deliberately reads State.models
// rather than the filtered/ranked rows: "what shipped in the last 30 days" must
// not disappear because the user has a VRAM filter on, and a model whose data
// is still filling in must still be reachable from here.
export function renderNewReleases() {
  const section = document.getElementById('new-releases');
  const list = document.getElementById('new-releases-list');
  if (!section || !list) return;
  clear(list);
  const fresh = (State.models || [])
    .filter(m => (m.status || 'active') === 'active' && isRecentRelease(m))
    .sort((a, b) => String(b.released || '').localeCompare(String(a.released || '')));
  section.hidden = fresh.length === 0;
  if (!fresh.length) return;
  for (const m of fresh) {
    const link = el('a', { class: 'new-release-chip', href: `#card-${m.id}` });
    link.appendChild(el('strong', {}, m.name));
    link.appendChild(el('span', { class: 'new-release-meta' },
      `${m.provider || '—'} · ${m.released || '—'}`));
    const days = daysSinceRelease(m);
    if (days != null) {
      link.appendChild(el('span', { class: 'new-release-age' },
        days === 0 ? t('ui.newReleases.today') : t('ui.newReleases.daysAgo').replace('{n}', String(days))));
    }
    link.addEventListener('click', (ev) => {
      const target = document.getElementById(`card-${m.id}`);
      if (!target) return;
      ev.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      target.classList.remove('is-target');
      void target.offsetWidth;
      target.classList.add('is-target');
      setTimeout(() => target.classList.remove('is-target'), 1800);
    });
    list.appendChild(el('li', {}, link));
  }
}

export function renderAll() {
  // Compute the ranked rows (rankBands + effectiveScore over all models) ONCE
  // and hand copies to both surfaces — each sorts its copy in place.
  const ranked = rankedModels();
  renderTable(ranked.slice());
  renderModelCards(ranked.slice());
  renderNewReleases();
}
