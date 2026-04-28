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

export function cameraIconButton(titleText) {
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

  const path = document.createElementNS(svgNS, 'path');
  path.setAttribute('d', 'M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z');
  svg.appendChild(path);

  const circle = document.createElementNS(svgNS, 'circle');
  circle.setAttribute('cx', '12');
  circle.setAttribute('cy', '13');
  circle.setAttribute('r', '4');
  svg.appendChild(circle);

  btn.appendChild(svg);

  const sr = document.createElement('span');
  sr.className = 'sr-only';
  sr.textContent = titleText;
  btn.appendChild(sr);

  return btn;
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
