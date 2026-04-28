// Stale-data banner: compare GitHub's latest commit timestamp against the
// Pages CDN's deploy time (Last-Modified header on data/models.json captured
// in State.dataDeployedAt). When the commit is materially newer than the
// served data, surface a non-blocking banner with a Refresh button so the
// reader knows the build they see isn't current.

import { State } from './core.js';
import { t } from './i18n.js';

const CACHE_KEY = 'acm.freshness.v1';
const CACHE_TTL_MS = 5 * 60 * 1000;
const STALE_TOLERANCE_MS = 60 * 1000;
const COMMITS_API = 'https://api.github.com/repos/sungurerdim/aicodermap/commits/main';

function readCache() {
  try {
    const raw = localStorage.getItem(CACHE_KEY);
    if (!raw) return null;
    const c = JSON.parse(raw);
    if (!c || typeof c !== 'object') return null;
    if (Date.now() - (c.fetchedAt || 0) > CACHE_TTL_MS) return null;
    return c;
  } catch (_) { return null; }
}

function writeCache(payload) {
  try { localStorage.setItem(CACHE_KEY, JSON.stringify(payload)); } catch (_) { /* ignore */ }
}

async function fetchLatestCommit() {
  try {
    const res = await fetch(COMMITS_API, {
      headers: { Accept: 'application/vnd.github+json' },
      cache: 'no-store',
    });
    if (!res.ok) return null;
    const j = await res.json();
    const sha = typeof j.sha === 'string' ? j.sha.slice(0, 7) : null;
    const date = j.commit && j.commit.committer && j.commit.committer.date;
    if (!sha || !date) return null;
    return { sha, date, fetchedAt: Date.now() };
  } catch (_) { return null; }
}

function applyTemplate(template, vars) {
  return template.replace(/\{(\w+)\}/g, (_, k) => (k in vars ? String(vars[k]) : `{${k}}`));
}

function showBanner(sha, ageMin) {
  const banner = document.getElementById('freshness-banner');
  if (!banner) return;
  const msg = banner.querySelector('.freshness-message');
  const refreshBtn = banner.querySelector('.freshness-refresh');
  const dismissBtn = banner.querySelector('.freshness-dismiss');
  if (!msg || !refreshBtn || !dismissBtn) return;
  const template = t('ui.freshness.stale')
    || 'A newer update was published (commit {sha}, {ageMin} min ago). Refresh the page.';
  msg.textContent = applyTemplate(template, { sha, ageMin });
  refreshBtn.textContent = t('ui.freshness.refresh') || 'Refresh';
  refreshBtn.onclick = () => location.reload();
  dismissBtn.onclick = () => { banner.hidden = true; };
  banner.hidden = false;
}

export async function checkFreshness() {
  if (!State.dataDeployedAt) return;
  const deployMs = new Date(State.dataDeployedAt).getTime();
  if (!Number.isFinite(deployMs)) return;

  let info = readCache();
  if (!info) {
    info = await fetchLatestCommit();
    if (!info) return;
    writeCache(info);
  }
  const commitMs = new Date(info.date).getTime();
  if (!Number.isFinite(commitMs)) return;

  const drift = commitMs - deployMs;
  if (drift <= STALE_TOLERANCE_MS) return;

  const ageMin = Math.max(1, Math.round(drift / 60_000));
  showBanner(info.sha, ageMin);
}
