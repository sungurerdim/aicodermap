// Model card render. buildModelCard is the orchestrator; each section has
// its own builder function so individual concerns stay <50 lines and brace
// nesting stays ≤3.

import { State, BENCH_KEYS, BENCH_CATEGORIES } from './core.js';
import {
  compositeScore, coverageOf, disputedCount, fmtScore, contradictionFor,
  pricingView, fmtPriceMoney, fmtPriceRange, fmtPriceCell, fmtContext,
  fmtLastUpdated, formatBenchValue, isCellStale, getCellFreshness,
  sourceReliabilityBadge,
  effectiveScore, vendorComposites, vendorConsensusScore,
  crossValidationAgreement, presetTiersFor,
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
  const weight = Number(State.weights?.[key]) || 0;
  const sources = State.sources[`${model.id}.${key}`] || [];
  const topSource = sources.slice().sort((a, b) =>
    (b.trustScore || 0) - (a.trustScore || 0))[0];

  const classes = ['bench-cell'];
  if (score == null) {
    // N/A retired: an empty cell is either a pending gap (in this cycle's gap
    // list) or simply not-yet-researched — there is no opt-out state.
    const inGap = (State.gaps || []).some(g =>
      (g.key === `${model.id}.${key}`) ||
      (g.modelId === model.id && g.field === key));
    classes.push(inGap ? 'gap-pending' : 'empty');
  } else {
    // Provenance tier badge
    if (topSource) {
      const tier = topSource.tier || '';
      if (tier === 'C') classes.push('tier-c');
    } else if (score != null) {
      classes.push('tier-unknown');
    }
    // Freshness — stale >14d, very-stale >60d
    if (isCellStale(model.id, key)) {
      const freshness = getCellFreshness(model.id, key);
      const ageDays = freshness
        ? (Date.now() - new Date(freshness).getTime()) / 86400000
        : 0;
      classes.push(ageDays > 60 ? 'cell-very-stale' : 'stale');
    }
  }
  if (weight === 0) classes.push('excluded');
  const cell = el('div', { class: classes.join(' ') });

  const nameWrap = el('span', { class: 'name' }, t(`benchmarks.${key}.name`));
  if (weight > 0) {
    nameWrap.appendChild(el('span', {
      class: 'bench-weight',
      title: `${t('ui.weights.weightLabel') || 'Weight'}: ${weight}`,
    }, String(weight)));
  } else {
    nameWrap.title = t('ui.weights.excluded') || 'Excluded by active preset';
  }
  cell.appendChild(nameWrap);

  const desc = t(`benchmarks.${key}.desc`);
  if (desc) cell.dataset.tip = desc;

  cell.appendChild(el('span', { class: 'value' }, score != null ? formatBenchValue(key, score) : '—'));

  const c = contradictionFor(model.id, key);
  if (c) {
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
  }
  return cell;
}

function cardHead(model) {
  const head = el('div', { class: 'model-card-head' });
  head.appendChild(el('span', { class: 'model-rank' }, `#${model.__rank}`));
  head.appendChild(el('h3', { class: 'model-name-title' }, model.name));
  head.appendChild(el('span', { class: `tier-badge ${model.tier}` }, tierLabel(model.tier)));

  // Provider line — was its own row beneath the title; now folded into the
  // head as a small separator-prefixed span. Wraps below on narrow widths
  // because the head is `flex-wrap: wrap`.
  const providerText = `${model.provider || '—'} · ${model.released || '—'} · ${model.license || '—'}`;
  head.appendChild(el('span', { class: 'model-provider-inline' }, providerText));

  if (model.open === true) {
    head.appendChild(el('span', { class: 'open-badge', title: t('ui.openWeights') || 'Open weights' },
      t('ui.openShort') || 'OPEN'));
  } else if (model.open === false) {
    head.appendChild(el('span', { class: 'closed-badge', title: t('ui.closedWeights') || 'Closed weights' },
      t('ui.closedShort') || 'CLOSED'));
  }
  if (model.status === 'deprecated') {
    const tip = model.successor ? `Successor: ${model.successor}` : 'Deprecated by vendor';
    const dateTxt = model.deprecatedAt ? ` ${model.deprecatedAt}` : '';
    head.appendChild(el('span', { class: 'deprecated-badge', title: tip },
      `${t('ui.deprecated') || 'DEPRECATED'}${dateTxt}`));
  } else if (model.status === 'archived') {
    head.appendChild(el('span', { class: 'archived-badge', title: 'Archived' },
      t('ui.archived') || 'ARCHIVED'));
  }
  return head;
}

function compositeBlock(composite, coverage, disputed) {
  const pct = coverage != null ? Math.round(coverage * 100) : null;
  const isLowCov = pct != null && pct < 40;
  const valueText = fmtScore(composite, 1);
  const valueEl = el('span', {
    class: isLowCov ? 'value value-low-confidence' : 'value',
    title: isLowCov ? t('ui.lowConfidenceTip') : '',
  }, isLowCov ? `${valueText}*` : valueText);
  const score = el('div', { class: 'composite-score' },
    el('span', { class: 'label' }, t('ui.table.composite')),
    valueEl,
  );
  if (pct != null) {
    const covClass = `coverage cov-${pct >= 75 ? 'full' : pct >= 40 ? 'partial' : 'low'}`;
    score.appendChild(el('span', { class: covClass, title: t('ui.coverageTip') },
      `${t('ui.coverage')} ${pct}%`));
  }
  if (isLowCov) {
    score.appendChild(el('span', { class: 'low-confidence-note' }, t('ui.lowConfidence')));
  }
  if (disputed > 0) {
    score.appendChild(el('span', { class: 'disputed', title: t('ui.disputedTip') },
      `${disputed} ${t('ui.disputed')}`));
  }
  return score;
}

function cardMeta(model, compat) {
  const meta = el('div', { class: 'model-meta' });
  const pview = pricingView(model);

  meta.appendChild(metaCell(t('ui.table.context'), fmtContext(model.context)));
  meta.appendChild(metaCell(t('ui.table.pricingApi'), fmtPriceCell(model)));
  if (pview.blended != null) {
    meta.appendChild(metaCell(t('pricing.blended'), `$${pview.blended.toFixed(2)}`));
  }
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
  const categorised = new Set();
  for (const cat of BENCH_CATEGORIES) {
    const catLabel = t(`benchCategories.${cat.id}.label`) || cat.id;
    grid.appendChild(el('div', { class: 'bench-cat-header' }, catLabel));
    for (const k of cat.keys) {
      if (BENCH_KEYS.includes(k)) {
        grid.appendChild(buildBenchCell(model, k));
        categorised.add(k);
      }
    }
  }
  // Uncategorised keys fallback (should not occur if BENCH_CATEGORIES is complete)
  for (const k of BENCH_KEYS) {
    if (!categorised.has(k)) grid.appendChild(buildBenchCell(model, k));
  }
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
        const badge = sourceReliabilityBadge(s.url);
        const attrs = {
          href: s.url, target: '_blank', rel: 'noopener noreferrer', title: s.url,
          class: 'source-link',
        };
        if (badge) {
          attrs['data-reliability'] = badge.kind;
          const accPct = Math.round(badge.accuracy * 100);
          const nStr = badge.n.toFixed(1);
          let qualifier = '';
          if (badge.kind === 'exceptional') qualifier = ' ' + (t('reliability.exceptional') || 'exceptional source');
          else if (badge.kind === 'low') qualifier = ' ' + (t('reliability.lowConfidence') || 'low confidence');
          attrs['data-tip'] = `${t('reliability.label') || 'Reliability'}: ${accPct}% (n=${nStr})${qualifier}`;
        }
        list.appendChild(el('a', attrs, text));
      } else {
        list.appendChild(document.createTextNode(text));
      }
    });
    row.appendChild(list);
    block.appendChild(row);
  }
  return block;
}

// F1+F2 (2026-05-18): vendor composite + agreement panel. Surfaces the
// vendor-aggregated composites (aaIdx / aaCoding / aaAgentic / aaOmni) that
// the AICoderMap composite intentionally excludes (to avoid double-counting
// of their componentBenches). Shown as a small badge row + an agreement
// indicator vs AICoderMap composite rank.
function vendorPanelBlock(model) {
  const presetName = State.activePresetName || 'balanced';
  const vc = vendorComposites(model, presetName);
  if (!vc.length) return null;
  // F6 (2026-05-18): wrapped in a visually distinct group with header label,
  // explicit border + background so users see this is NOT part of AICM score.
  const block = el('section', { class: 'vendor-composite-group', 'data-group': 'vendor' });
  const header = el('div', { class: 'vendor-group-header' });
  header.appendChild(el('span', { class: 'vendor-group-title' }, t('vendorPanel.title') || 'Vendor view'));
  header.appendChild(el('span', { class: 'vendor-group-tag', 'data-tip': t('vendorPanel.notInScore') || 'Independent reference — NOT part of AICoderMap composite score' },
    t('vendorPanel.notInScoreTag') || 'not in score'));
  block.appendChild(header);
  const list = el('div', { class: 'vendor-badges' });
  for (const v of vc) {
    const badge = el('span', {
      class: `vendor-badge${v.missing ? ' is-missing' : ''}`,
      'data-tip': v.missing
        ? `${v.label}: —`
        : `${v.label}: ${v.raw} (raw) → ${(v.normalized ?? 0).toFixed(0)}/100 (norm)  •  ${v.publisher || ''}`,
    });
    badge.appendChild(el('span', { class: 'vendor-badge-label' }, v.labelShort || v.key));
    badge.appendChild(el('span', { class: 'vendor-badge-value' },
      v.missing ? '—' : (v.normalized ?? 0).toFixed(0)));
    list.appendChild(badge);
  }
  block.appendChild(list);
  // Agreement indicator — only meaningful for non-consensus presets that
  // have a separate AICM composite to compare against.
  if ((State.scoreFn || 'aicm') !== 'vendorConsensus') {
    const agreement = crossValidationAgreement(model, State.models, State.weights, presetName);
    if (agreement && agreement.flag) {
      const dot = ({ 'consensus': '🟢', 'mild-disagreement': '🟡', 'controversy': '🔴' })[agreement.flag] || '';
      const lbl = ({
        'consensus': t('vendorPanel.consensus') || 'consensus',
        'mild-disagreement': t('vendorPanel.mild') || 'mild gap',
        'controversy': t('vendorPanel.controversy') || 'controversy',
      })[agreement.flag];
      const tip = `${t('vendorPanel.agreementTip') || 'AICM rank'} #${agreement.aicmRank} vs ${t('vendorPanel.consensusRank') || 'consensus rank'} #${agreement.consensusRank} (Δ${agreement.gap})`;
      const ind = el('span', { class: `vendor-agreement is-${agreement.flag}`, 'data-tip': tip },
        `${dot} ${lbl}`);
      block.appendChild(ind);
    }
  }
  return block;
}

// F1+F2 (2026-05-18): tiered missing-data badge. Surfaces "limited data"
// (required bench missing) and "limited coverage" (≥2 critical benches
// missing) under the current preset. Returns null when no tier issues.
function limitedDataBadge(model) {
  const presetName = State.activePresetName || 'balanced';
  const tiers = presetTiersFor(model, presetName);
  if (!tiers.isLimitedData && !tiers.isLimitedCoverage) return null;
  const cls = tiers.isLimitedCoverage ? 'limited-coverage' : 'limited-data';
  const lbl = tiers.isLimitedCoverage
    ? (t('vendorPanel.limitedCoverage') || 'limited coverage')
    : (t('vendorPanel.limitedData') || 'limited data');
  const missing = [...tiers.missingCritical, ...tiers.missingRequired];
  const tip = `${t('vendorPanel.missingTip') || 'missing benches'}: ${missing.join(', ')}`;
  return el('span', { class: `bench-tier-badge is-${cls}`, 'data-tip': tip }, `⚠ ${lbl}`);
}

export function buildModelCard(model, rank) {
  model.__rank = rank;
  // F1+F2 (2026-05-18): effectiveScore dispatches based on State.scoreFn.
  // 'consensus' preset → vendorConsensusScore; otherwise → compositeScore.
  const composite = effectiveScore(model, State.weights, State.activePresetName);
  const coverage = coverageOf(model, State.weights);
  const disputed = disputedCount(model, State.weights);
  const status = model.status || 'active';
  const statusClass = status === 'active' ? '' : ` is-${status}`;
  const card = el('article', {
    class: `model-card${statusClass}`,
    id: `card-${model.id}`,
    dataset: { modelId: model.id, tier: model.tier, status },
    'data-export-section': `model-${model.id}`,
    'aria-label': model.name,
  });
  const compat = gpuCompat(model, getActiveVram());

  // Card layout — three grid areas: head (title row), score (right
  // sidebar), main (everything else stacked). Score sits at align-self:
  // start so its small height never pushes main content down; main flows
  // freely from the top of the card alongside the score column.
  card.appendChild(cardHead(model));
  card.appendChild(compositeBlock(composite, coverage, disputed));

  const main = el('div', { class: 'model-card-main' });
  main.appendChild(cardMeta(model, compat));

  // F1+F2 (2026-05-18): limited-data / limited-coverage tier badge sits
  // close to the top so users notice it before drilling into bench grid.
  const limitedBadge = limitedDataBadge(model);
  if (limitedBadge) main.appendChild(limitedBadge);

  const provBlock = pricingProvidersBlock(pricingView(model));
  if (provBlock) main.appendChild(provBlock);

  benchGridSection(model).forEach(n => main.appendChild(n));

  // F1+F2: vendor composite + agreement panel — independent reference
  // signals (NOT included in AICM composite). Surfaces below bench grid
  // because it's secondary information.
  const vendorPanel = vendorPanelBlock(model);
  if (vendorPanel) main.appendChild(vendorPanel);

  const unsloth = unslothListBlock(model, compat);
  if (unsloth) main.appendChild(unsloth);

  const ollama = ollamaBlock(model);
  if (ollama) main.appendChild(ollama);

  const notes = notesBlock(model);
  if (notes) main.appendChild(notes);

  const sources = sourcesFooter(model);
  if (sources) main.appendChild(sources);

  card.appendChild(main);
  card.appendChild(cardActions(model, card));
  return card;
}
