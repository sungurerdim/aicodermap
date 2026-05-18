// i18n: translate by dotted path, apply across DOM, fetch locale JSON.

import { State } from './core.js';

export function t(path) {
  const parts = path.split('.');
  let cur = State.i18n;
  for (const p of parts) {
    if (cur && typeof cur === 'object' && p in cur) cur = cur[p];
    else { cur = null; break; }
  }
  if (cur != null) return cur;
  if (State.i18nFallback) {
    let fb = State.i18nFallback;
    for (const p of parts) {
      if (fb && typeof fb === 'object' && p in fb) fb = fb[p];
      else { fb = null; break; }
    }
    if (fb != null) return fb;
  }
  return null;
}

export function applyI18n(root) {
  const scope = root || document;
  document.documentElement.setAttribute('lang', State.lang);
  scope.querySelectorAll('[data-i18n-key]').forEach((el) => {
    const key = el.getAttribute('data-i18n-key');
    const val = t(key);
    if (typeof val === 'string') el.textContent = val;
  });
  scope.querySelectorAll('[data-i18n-tip]').forEach((el) => {
    const key = el.getAttribute('data-i18n-tip');
    const val = t(key);
    if (typeof val === 'string') el.setAttribute('data-tip', val);
  });
  scope.querySelectorAll('[data-i18n-aria-label]').forEach((el) => {
    const key = el.getAttribute('data-i18n-aria-label');
    const val = t(key);
    if (typeof val === 'string') el.setAttribute('aria-label', val);
  });
  scope.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
    const key = el.getAttribute('data-i18n-placeholder');
    const val = t(key);
    if (typeof val === 'string') el.setAttribute('placeholder', val);
  });
}

// Module-relative so it works from any HTML entry point (index.html, smoke.html).
const I18N_BASE = new URL('../../i18n/', import.meta.url);
const FALLBACK_BUST = String(Date.now());

export async function loadI18n(lang) {
  try {
    const bust = (typeof window !== 'undefined' && window.__ACM_CACHE_BUST__)
      || FALLBACK_BUST;
    const url = new URL(`${lang}.json?v=${encodeURIComponent(bust)}`, I18N_BASE);
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) throw new Error('i18n fetch failed');
    return await res.json();
  } catch (_) {
    return null;
  }
}
