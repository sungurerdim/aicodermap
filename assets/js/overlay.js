// Tooltip + PNG export. Both are visual overlays on top of the base UI.

import { el, showToast } from './dom.js';
import { fmtScore } from './format.js';
import { t } from './i18n.js';

export function showContradictionTooltip(anchor, contradiction) {
  const tt = document.getElementById('tooltip');
  if (!tt) return;
  while (tt.firstChild) tt.removeChild(tt.firstChild);
  tt.appendChild(el('h4', null, t('ui.contradiction.title')));
  tt.appendChild(el('p', null, `${t('ui.contradiction.delta')}: ${contradiction.delta.toFixed(1)} pp`));
  const dl = el('dl');
  for (const s of contradiction.sources) {
    const dt = el('dt', null, `${fmtScore(s.value, 1)}`);
    const dd = el('dd');
    const tierLabel = t(`ui.contradiction.tier.${s.tier}`) || s.tier;
    if (s.url) {
      dd.appendChild(el('a', { href: s.url, target: '_blank', rel: 'noopener noreferrer' }, s.source));
    } else {
      dd.appendChild(document.createTextNode(s.source));
    }
    dd.appendChild(document.createTextNode(` · ${tierLabel} · ${s.date || ''}`));
    dl.appendChild(dt);
    dl.appendChild(dd);
  }
  tt.appendChild(dl);
  tt.hidden = false;
  positionTooltip(tt, anchor);
}

export function positionTooltip(tt, anchor) {
  const rect = anchor.getBoundingClientRect();
  const ttRect = tt.getBoundingClientRect();
  const margin = 8;
  let x = rect.left + rect.width / 2 - ttRect.width / 2;
  let y = rect.bottom + margin;
  if (y + ttRect.height > window.innerHeight) y = rect.top - ttRect.height - margin;
  if (x < margin) x = margin;
  if (x + ttRect.width > window.innerWidth - margin) x = window.innerWidth - ttRect.width - margin;
  tt.style.left = `${Math.max(0, x)}px`;
  tt.style.top = `${Math.max(0, y)}px`;
}

export function hideTooltip() {
  const tt = document.getElementById('tooltip');
  if (tt) tt.hidden = true;
}

export async function exportElement(element, filename) {
  if (typeof window.html2canvas !== 'function') {
    showToast(t('ui.errors.exportFailed'), 'error');
    return;
  }
  const wasExporting = document.body.classList.contains('exporting');
  if (!wasExporting) document.body.classList.add('exporting');
  try {
    const bg = (getComputedStyle(document.body).getPropertyValue('--bg').trim()) || '#0b0d10';
    const canvas = await window.html2canvas(element, {
      scale: 2,
      backgroundColor: bg,
      useCORS: true,
      logging: false,
      windowWidth: document.documentElement.scrollWidth,
    });
    await new Promise((resolve) => {
      canvas.toBlob((blob) => {
        if (!blob) { resolve(); return; }
        const url = URL.createObjectURL(blob);
        const a = el('a', { href: url, download: `${filename}.png` });
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
        resolve();
      }, 'image/png');
    });
  } catch (e) {
    console.error('export failed', e);
    showToast(t('ui.errors.exportFailed'), 'error');
  } finally {
    if (!wasExporting) document.body.classList.remove('exporting');
  }
}
