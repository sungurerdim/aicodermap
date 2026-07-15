import { State, BENCH_KEYS } from './core.js';
import { clear, el } from './dom.js';
import { t } from './i18n.js';

// G7 (2026-07-15): plain-language benchmark glossary (Vellum pattern) — one
// row per bench key with its full name and one-line description from i18n.
// Lives here with the other static informational section renderers.
export function renderBenchGlossary() {
  const host = document.getElementById('bench-glossary');
  if (!host) return;
  clear(host);
  const benchTypes = (State.schema && State.schema.benchTypes) || {};
  for (const k of BENCH_KEYS) {
    const name = t(`benchmarks.${k}.name`);
    const desc = t(`benchmarks.${k}.desc`);
    if (!name || !desc) continue;
    const term = el('span', { class: 'glossary-term' }, name);
    // G5: contamination-risk taxonomy chip — static splits age into
    // contamination risk; rotating/temporal are resistant by construction.
    const bt = benchTypes[k];
    if (bt === 'rotating' || bt === 'temporal' || bt === 'static') {
      term.appendChild(el('span', {
        class: `benchtype-chip is-${bt}`,
        'data-tip': t(`methodology.benchType.${bt}Tip`),
      }, t(`methodology.benchType.${bt}`)));
    }
    host.appendChild(el('div', { class: 'glossary-row' },
      term,
      el('span', { class: 'glossary-desc' }, desc),
    ));
  }
}

const COLS = [
  { key: 'model',           i18n: 'privacy.col.model' },
  { key: 'trainingOptOut',  i18n: 'privacy.col.trainingOptOut' },
  { key: 'dataResidency',   i18n: 'privacy.col.dataResidency' },
  { key: 'soc2',            i18n: 'privacy.col.soc2' },
  { key: 'gdpr',            i18n: 'privacy.col.gdpr' },
  { key: 'apiLogging',      i18n: 'privacy.col.apiLogging' },
];

function fmtBool(v) {
  if (v === true)  return { text: t('privacy.val.yes'),  cls: 'priv-yes' };
  if (v === false) return { text: t('privacy.val.no'),   cls: 'priv-no' };
  return { text: t('privacy.val.unknown'), cls: 'priv-unknown' };
}

function fmtOptOut(v) {
  if (!v) return { text: t('privacy.val.unknown'), cls: 'priv-unknown' };
  if (v === 'available') return { text: t('privacy.val.available'), cls: 'priv-yes' };
  if (v === 'none')      return { text: t('privacy.val.none'),      cls: 'priv-no' };
  return { text: t('privacy.val.unknown'), cls: 'priv-unknown' };
}

function fmtResidency(v) {
  if (!v || !Array.isArray(v) || v.length === 0) return t('privacy.val.unknown');
  return v.join(', ');
}

function fmtLogging(v) {
  if (!v) return { text: t('privacy.val.unknown'), cls: 'priv-unknown' };
  if (v === 'not_logged' || v === 'off')
    return { text: t('privacy.val.notLogged'), cls: 'priv-yes' };
  if (v === 'default_off' || v === 'opt_out')
    return { text: t('privacy.val.optOut'), cls: 'priv-partial' };
  if (v === 'default_on')
    return { text: t('privacy.val.defaultOn'), cls: 'priv-no' };
  return { text: t('privacy.val.unknown'), cls: 'priv-unknown' };
}

function renderCell(key, model) {
  const p = model.privacy || {};
  const td = document.createElement('td');
  if (key === 'model') {
    td.classList.add('priv-model');
    td.textContent = model.name;
    return td;
  }
  let info;
  if (key === 'trainingOptOut') info = fmtOptOut(p.trainingDataOptOut);
  else if (key === 'dataResidency') {
    const text = fmtResidency(p.dataResidency);
    td.textContent = text;
    return td;
  }
  else if (key === 'soc2')       info = fmtBool(p.soc2);
  else if (key === 'gdpr')       info = fmtBool(p.gdpr);
  else if (key === 'apiLogging') info = fmtLogging(p.apiLogging);
  else return td;

  const span = document.createElement('span');
  span.className = `priv-badge ${info.cls}`;
  span.textContent = info.text;
  td.appendChild(span);
  return td;
}

export function renderPrivacyTable() {
  const table = document.getElementById('privacy-table');
  if (!table) return;
  const thead = table.querySelector('thead tr');
  const tbody = table.querySelector('tbody');
  if (!thead || !tbody) return;

  clear(thead);
  for (const col of COLS) {
    const th = document.createElement('th');
    th.textContent = t(col.i18n);
    thead.appendChild(th);
  }

  clear(tbody);
  const models = State.models.filter(m => m.status !== 'deprecated' && m.status !== 'archived');
  if (models.length === 0) return;

  for (const m of models) {
    const tr = document.createElement('tr');
    tr.dataset.modelId = m.id;
    for (const col of COLS) {
      tr.appendChild(renderCell(col.key, m));
    }
    tbody.appendChild(tr);
  }

  const note = document.querySelector('.privacy-note');
  if (note) note.textContent = t('privacy.note');
}
