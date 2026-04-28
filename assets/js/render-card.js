// Model card render. buildModelCard is the orchestrator; each section has
// its own builder function so individual concerns stay <50 lines and brace
// nesting stays ≤3.

import { State, BENCH_KEYS } from './core.js';
import {
  compositeScore, coverageOf, disputedCount, fmtScore, contradictionFor,
  pricingView, fmtPriceMoney, fmtPriceRange, fmtPriceCell, fmtContext,
  fmtLastUpdated,
} from './data.js';
import { gpuCompat, getActiveVram } from './gpu.js';
import { el, cameraIconButton, docIconButton } from './dom.js';
import { t } from './i18n.js';
import { showContradictionTooltip, hideTooltip, exportElement } from './overlay.js';
import { modelSourcesSummary, exportSourcesMarkdown } from './sources.js';

function tierLabel(tier) {
  return t(`ui.tier.${tier}`) || tier;
}

function metaCell(label, value) {
  const cell = el('div', { class: 'meta-cell' });
  cell.appendChild(el('span', { class: 'label' }, String(label)));
  if (value && typeof value === 'object' && value.nodeType === 1) {
    const v = el('span', { class: 'value' });
    v.appendChild(value);
    cell.appendChild(v);
  } else {
    cell.appendChild(el('span', { class: 'value' }, String(value ?? '—')));
  }
  return cell;
}

export function buildBenchCell(model, key) {
  const score = model.bench?.[key];
  const cell = el('div', { class: score == null ? 'bench-cell empty' : 'bench-cell' });
  cell.appendChild(el('span', { class: 'name' }, t(`benchmarks.${key}.name`)));
  cell.appendChild(el('span', { class: 'value' }, score != null ? fmtScore(score) : '—'));

  const c = contradictionFor(model.id, key);
  if (!c) return cell;

  cell.classList.add(c.severity === 'danger' ? 'flag-danger' : 'flag-warn');
  const flag = el('span', {
    class: 'flag',
    tabindex: '0',
    role: 'button',
    'aria-label': t('ui.contradiction.title'),
  }, c.severity === 'danger' ? '🚨' : '⚠');
  flag.dataset.modelId = model.id;
  flag.dataset.benchKey = key;
  flag.addEventListener('mouseenter', (e) => showContradictionTooltip(e.currentTarget, c));
  flag.addEventListener('focus', (e) => showContradictionTooltip(e.currentTarget, c));
  flag.addEventListener('mouseleave', hideTooltip);
  flag.addEventListener('blur', hideTooltip);
  cell.appendChild(flag);
  return cell;
}

function cardHead(model, composite, coverage, disputed) {
  const head = el('div', { class: 'model-card-head' });
  head.appendChild(el('div', { class: 'model-name' },
    el('span', { class: 'model-rank' }, `#${model.__rank}`),
    el('h3', null, model.name),
    el('span', { class: `tier-badge ${model.tier}` }, tierLabel(model.tier)),
  ));
  const score = el('div', { class: 'composite-score' },
    el('span', { class: 'label' }, t('ui.table.composite')),
    el('span', { class: 'value' }, fmtScore(composite, 1)),
  );
  if (coverage != null) {
    const pct = Math.round(coverage * 100);
    const covClass = `coverage cov-${pct >= 75 ? 'full' : pct >= 40 ? 'partial' : 'low'}`;
    score.appendChild(el('span', {
      class: covClass,
      title: t('ui.coverageTip'),
    }, `${t('ui.coverage')} ${pct}%`));
  }
  if (disputed > 0) {
    score.appendChild(el('span', {
      class: 'disputed',
      title: t('ui.disputedTip'),
    }, `${disputed} ${t('ui.disputed')}`));
  }
  head.appendChild(score);
  return head;
}

function providerRow(model) {
  const row = el('div', { class: 'model-provider' });
  row.appendChild(el('span', null, `${model.provider || '—'} · ${model.released || '—'} · ${model.license || '—'}`));

  if (model.open === true) {
    row.appendChild(el('span', { class: 'open-badge', title: t('ui.openWeights') || 'Open weights' },
      t('ui.openShort') || 'OPEN'));
  } else if (model.open === false) {
    row.appendChild(el('span', { class: 'closed-badge', title: t('ui.closedWeights') || 'Closed weights' },
      t('ui.closedShort') || 'CLOSED'));
  }

  if (model.status === 'deprecated') {
    const tip = model.successor ? `Successor: ${model.successor}` : 'Deprecated by vendor';
    const dateTxt = model.deprecatedAt ? ` ${model.deprecatedAt}` : '';
    row.appendChild(el('span', { class: 'deprecated-badge', title: tip },
      `${t('ui.deprecated') || 'DEPRECATED'}${dateTxt}`));
  } else if (model.status === 'archived') {
    row.appendChild(el('span', { class: 'archived-badge', title: 'Archived' },
      t('ui.archived') || 'ARCHIVED'));
  }
  return row;
}

function cardMeta(model, compat) {
  const meta = el('div', { class: 'model-meta' });
  const pview = pricingView(model);

  meta.appendChild(metaCell(t('ui.table.context'), fmtContext(model.context)));
  meta.appendChild(metaCell(t('ui.table.pricingApi'), fmtPriceCell(model)));
  if (pview.range?.cacheHit) {
    meta.appendChild(metaCell(t('ui.table.cacheHit') || 'Cache hit', fmtPriceRange(pview.range.cacheHit)));
  }

  const subText = pview.subscriptions.length
    ? pview.subscriptions.map(s => s.price != null
        ? `${s.tier} $${s.price}/${s.billing === 'annual' ? 'yr' : 'mo'}`
        : (s.notes || s.tier)).join(' · ')
    : '—';
  meta.appendChild(metaCell(t('ui.table.pricingSub'), subText));
  meta.appendChild(metaCell(t('ui.table.lastUpdated'), fmtLastUpdated(model.lastUpdated) || '—'));

  if (model.providers != null) {
    const uptimeNote = model.uptime != null ? ` (uptime ${fmtScore(model.uptime, 1)}%)` : '';
    meta.appendChild(metaCell(t('ui.table.providers') || 'Providers', `${model.providers}${uptimeNote}`));
  }
  if (model.vramRequirement != null) meta.appendChild(metaCell(t('ui.table.vram'), `${model.vramRequirement} GB`));
  if (model.ollamaSize && !model.ollama) {
    meta.appendChild(metaCell(t('ui.table.ollamaSize') || 'Ollama size', model.ollamaSize));
  }

  meta.appendChild(metaCell(t('ui.table.gpu'), el('span', { class: `compat-badge ${compat.kind}` }, compat.label)));
  return meta;
}

function pricingProvidersBlock(pview) {
  if (pview.providers.length < 2) return null;
  const block = el('details', { class: 'pricing-providers' });
  block.appendChild(el('summary', null, t('ui.pricing.byProvider') || 'Pricing by provider'));
  const list = el('div', { class: 'pricing-providers-list' });
  for (const e of pview.providers) {
    list.appendChild(buildPricingProviderRow(e));
  }
  block.appendChild(list);
  return block;
}

function buildPricingProviderRow(e) {
  const row = el('div', { class: 'pricing-provider-row' });
  row.appendChild(el('span', { class: 'prov-name' }, e.provider || '—'));
  const cache = e.cacheHit != null ? ` · cache ${fmtPriceMoney(e.cacheHit)}` : '';
  const tput = e.throughput != null ? ` · ${e.throughput} tok/s` : '';
  row.appendChild(el('span', { class: 'prov-price' },
    `${fmtPriceMoney(e.in)} / ${fmtPriceMoney(e.out)}${cache}${tput}`));
  if (e.url) {
    row.appendChild(el('a', {
      class: 'prov-link',
      href: e.url,
      target: '_blank',
      rel: 'noopener noreferrer',
      title: e.url,
    }, '↗'));
  }
  return row;
}

function benchGridSection(model) {
  const head = el('div', { class: 'meta-cell' }, el('span', { class: 'label' }, t('ui.table.bench')));
  const grid = el('div', { class: 'bench-grid' });
  for (const k of BENCH_KEYS) grid.appendChild(buildBenchCell(model, k));
  return [head, grid];
}

function unslothListBlock(model, compat) {
  if (!Array.isArray(model.unslothVariants) || !model.unslothVariants.length) return null;
  const list = el('ul', { class: 'unsloth-list' });
  for (const v of model.unslothVariants) {
    const li = el('li', null, `${v.name} · ${v.size} · ~${v.vram} GB`);
    if (compat.variant && compat.variant.name === v.name) li.classList.add('recommended');
    list.appendChild(li);
  }
  return list;
}

function ollamaBlock(model) {
  if (!model.ollama || typeof model.ollama !== 'object') return null;
  const o = model.ollama;
  const block = el('div', { class: 'ollama-block' });
  block.appendChild(buildOllamaTitle(o));
  if (o.pullCmd) block.appendChild(buildOllamaCmdRow(o.pullCmd));

  const meta = [o.pullCount, o.license, o.releasedISO].filter(Boolean);
  if (meta.length) block.appendChild(el('div', { class: 'ollama-meta' }, meta.join(' · ')));

  if (o.ollamaUrl) {
    block.appendChild(el('a', {
      class: 'ollama-link',
      href: o.ollamaUrl,
      target: '_blank',
      rel: 'noopener noreferrer',
    }, (t('ui.ollama.viewOn') || 'View on Ollama') + ' →'));
  }
  return block;
}

function buildOllamaTitle(o) {
  const titleParts = [t('ui.ollama.title') || 'Local (Ollama)'];
  if (o.architecture) titleParts.push(o.architecture);
  if (o.parameters) titleParts.push(o.parameters);
  const title = el('div', { class: 'ollama-title' });
  title.appendChild(el('span', { class: 'ollama-icon' }, '💻'));
  title.appendChild(el('span', { class: 'ollama-title-text' }, titleParts.join(' · ')));
  return title;
}

function buildOllamaCmdRow(pullCmd) {
  const row = el('div', { class: 'ollama-cmd-row' });
  row.appendChild(el('code', { class: 'pull-cmd' }, pullCmd));
  const copyLabel = t('ui.ollama.copy') || 'Copy';
  const copy = el('button', { class: 'copy-btn', type: 'button', 'aria-label': copyLabel }, '⧉');
  copy.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(pullCmd);
      copy.textContent = '✓';
      setTimeout(() => { copy.textContent = '⧉'; }, 1500);
    } catch (_) { /* clipboard unavailable */ }
  });
  row.appendChild(copy);
  return row;
}

function notesBlock(model) {
  const strengths = t(`models.${model.strengthsKey}`);
  const weaknesses = t(`models.${model.weaknessesKey}`);
  const hasStrengths = strengths && strengths !== `models.${model.strengthsKey}`;
  const hasWeaknesses = weaknesses && weaknesses !== `models.${model.weaknessesKey}`;
  if (!hasStrengths && !hasWeaknesses) return null;

  const notes = el('div', { class: 'notes' });
  if (hasStrengths) notes.appendChild(el('div', { class: 'strengths' }, strengths));
  if (hasWeaknesses) notes.appendChild(el('div', { class: 'weaknesses' }, weaknesses));
  return notes;
}

function cardActions(model, card) {
  const actions = el('div', { class: 'model-actions' });
  const sourcesBtn = docIconButton(t('ui.export.sources'));
  sourcesBtn.addEventListener('click', () => exportSourcesMarkdown(model));
  actions.appendChild(sourcesBtn);
  const exportBtn = cameraIconButton(t('ui.export.model'));
  exportBtn.addEventListener('click', () => exportElement(card, `aicodermap-${model.id}`));
  actions.appendChild(exportBtn);
  return actions;
}

function sourcesFooter(model) {
  const { byTier, totalUnique, totalDatapoints } = modelSourcesSummary(model);
  if (totalUnique === 0) return null;

  const block = el('div', { class: 'sources-footer' });
  block.appendChild(el('div', { class: 'sources-header' },
    el('span', { class: 'sources-label' }, t('ui.sources')),
    el('span', { class: 'sources-count' },
      `${totalUnique} ${t('ui.sourcesUnique')} · ${totalDatapoints} ${t('ui.sourcesDatapoints')}`),
  ));

  for (const tier of ['I', 'S', 'C', '?']) {
    if (!byTier[tier].length) continue;
    const row = el('div', { class: `sources-row tier-${tier}` });
    row.appendChild(el('span', { class: 'sources-tier' }, `${tier}-tier (${byTier[tier].length}):`));
    const list = el('span', { class: 'sources-list' });
    byTier[tier].forEach((s, i) => {
      if (i > 0) list.appendChild(document.createTextNode(', '));
      const text = s.count > 1 ? `${s.source} ×${s.count}` : s.source;
      if (s.url) {
        list.appendChild(el('a', {
          href: s.url, target: '_blank', rel: 'noopener noreferrer', title: s.url,
        }, text));
      } else {
        list.appendChild(document.createTextNode(text));
      }
    });
    row.appendChild(list);
    block.appendChild(row);
  }
  return block;
}

export function buildModelCard(model, rank) {
  model.__rank = rank;
  const composite = compositeScore(model, State.weights);
  const coverage = coverageOf(model, State.weights);
  const disputed = disputedCount(model, State.weights);
  const status = model.status || 'active';
  const statusClass = status === 'active' ? '' : ` is-${status}`;
  const card = el('article', {
    class: `model-card${statusClass}`,
    dataset: { modelId: model.id, tier: model.tier, status },
    'data-export-section': `model-${model.id}`,
    'aria-label': model.name,
  });
  const compat = gpuCompat(model, getActiveVram());

  card.appendChild(cardHead(model, composite, coverage, disputed));
  card.appendChild(providerRow(model));
  card.appendChild(cardMeta(model, compat));

  const provBlock = pricingProvidersBlock(pricingView(model));
  if (provBlock) card.appendChild(provBlock);

  benchGridSection(model).forEach(n => card.appendChild(n));

  const unsloth = unslothListBlock(model, compat);
  if (unsloth) card.appendChild(unsloth);

  const ollama = ollamaBlock(model);
  if (ollama) card.appendChild(ollama);

  const notes = notesBlock(model);
  if (notes) card.appendChild(notes);

  const sources = sourcesFooter(model);
  if (sources) card.appendChild(sources);

  card.appendChild(cardActions(model, card));
  return card;
}
