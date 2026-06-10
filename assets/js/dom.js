// DOM helpers + toast notification. Strict no-innerHTML policy: textContent
// + createElement only. Toast accepts a pre-translated string so this module
// stays leaf (no i18n import).

export function el(tag, attrs, ...children) {
  const node = document.createElement(tag);
  if (attrs) {
    for (const [k, v] of Object.entries(attrs)) {
      if (v == null || v === false) continue;
      if (k === 'class') node.className = v;
      else if (k === 'dataset') Object.assign(node.dataset, v);
      else if (k.startsWith('on') && typeof v === 'function') node.addEventListener(k.slice(2).toLowerCase(), v);
      else if (k === 'i18nKey') node.setAttribute('data-i18n-key', v);
      else node.setAttribute(k, v === true ? '' : String(v));
    }
  }
  for (const c of children) {
    if (c == null || c === false) continue;
    if (Array.isArray(c)) c.forEach(x => x != null && node.appendChild(typeof x === 'string' ? document.createTextNode(x) : x));
    else node.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
  }
  return node;
}

export function clear(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
}

// Generic icon button factory — used by the camera (PNG export) and doc
// (Markdown export) buttons. Pass a list of {tag, attrs} objects to draw
// inside the SVG so each call site declares its own glyph.
function iconButton(titleText, glyph) {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'btn-icon-only';
  btn.setAttribute('data-tip', titleText);
  btn.setAttribute('aria-label', titleText);

  const svgNS = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(svgNS, 'svg');
  svg.setAttribute('class', 'icon');
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('width', '16');
  svg.setAttribute('height', '16');
  svg.setAttribute('fill', 'none');
  svg.setAttribute('stroke', 'currentColor');
  svg.setAttribute('stroke-width', '2');
  svg.setAttribute('stroke-linecap', 'round');
  svg.setAttribute('stroke-linejoin', 'round');
  svg.setAttribute('aria-hidden', 'true');
  svg.setAttribute('focusable', 'false');

  for (const part of glyph) {
    const node = document.createElementNS(svgNS, part.tag);
    for (const [k, v] of Object.entries(part.attrs)) node.setAttribute(k, v);
    svg.appendChild(node);
  }
  btn.appendChild(svg);

  const sr = document.createElement('span');
  sr.className = 'sr-only';
  sr.textContent = titleText;
  btn.appendChild(sr);
  return btn;
}

export function docIconButton(titleText) {
  return iconButton(titleText, [
    { tag: 'path', attrs: { d: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z' } },
    { tag: 'polyline', attrs: { points: '14 2 14 8 20 8' } },
    { tag: 'line', attrs: { x1: '16', y1: '13', x2: '8', y2: '13' } },
    { tag: 'line', attrs: { x1: '16', y1: '17', x2: '8', y2: '17' } },
    { tag: 'line', attrs: { x1: '10', y1: '9', x2: '8', y2: '9' } },
  ]);
}

export function cameraIconButton(titleText) {
  return iconButton(titleText, [
    { tag: 'path', attrs: { d: 'M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z' } },
    { tag: 'circle', attrs: { cx: '12', cy: '13', r: '4' } },
  ]);
}

let _toastTimer = null;

export function showToast(message, kind = 'info', durationMs = 3500) {
  let host = document.getElementById('toast-host');
  if (!host) {
    host = document.createElement('div');
    host.id = 'toast-host';
    host.className = 'toast-host';
    host.setAttribute('role', 'status');
    host.setAttribute('aria-live', 'polite');
    document.body.appendChild(host);
  }
  clear(host);
  const safeKind = kind === 'error' || kind === 'warn' || kind === 'success' ? kind : 'info';
  const t = document.createElement('div');
  t.className = `toast toast-${safeKind}`;
  t.textContent = String(message ?? '');
  host.appendChild(t);
  if (_toastTimer) clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => {
    if (t.parentNode === host) host.removeChild(t);
  }, Math.max(1500, durationMs));
}
