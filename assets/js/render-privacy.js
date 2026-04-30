import { State } from './core.js';
import { clear } from './dom.js';
import { t } from './i18n.js';

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
