// Stale-data banner: detect when a fresh build has been deployed to Pages
// while the user's tab is still showing the previous build. The signal is
// the ETag header on data/models.json — GitHub Pages computes it from the
// served file's contents, so two distinct deploys never share an ETag.
//
// Probe strategy:
//  - On bootstrap, schedule a delayed HEAD request (avoids racing the
//    initial GET) plus a 5-minute interval and a visibility-change trigger.
//  - HEAD is body-less and CDN-cached, so polling is cheap.
//  - If the live ETag differs from State.dataEtag, fetch GitHub's
//    /commits/main once for the short SHA and surface a banner. The SHA is
//    informational; the freshness decision is purely ETag-based, so a
//    GitHub API rate-limit hit doesn't suppress the warning.

import { State } from './core.js';
import { t } from './i18n.js';

const COMMITS_API = 'https://api.github.com/repos/sungurerdim/aicodermap/commits/main';
const POLL_INTERVAL_MS = 5 * 60 * 1000;
const INITIAL_DELAY_MS = 30 * 1000;

let started = false;
let bannerShown = false;

function applyTemplate(template, vars) {
  return template.replace(/\{(\w+)\}/g, (_, k) => (k in vars ? String(vars[k]) : `{${k}}`));
}

async function fetchLatestCommitSha() {
  try {
    const res = await fetch(COMMITS_API, {
      headers: { Accept: 'application/vnd.github+json' },
      cache: 'no-store',
    });
    if (!res.ok) return null;
    const j = await res.json();
    if (typeof j.sha !== 'string') return null;
    const commitDate = j.commit && j.commit.committer && j.commit.committer.date;
    return { sha: j.sha.slice(0, 7), date: commitDate };
  } catch (_) {
    return null;
  }
}

async function fetchLiveModelsEtag() {
  // Cache-bust the URL so a stale CDN cache entry can't mask a fresh deploy.
  const url = new URL('data/models.json', location.href);
  url.searchParams.set('_freshness', String(Date.now()));
  try {
    const res = await fetch(url, { method: 'HEAD', cache: 'no-store' });
    if (!res.ok) return null;
    return {
      etag: res.headers.get('ETag'),
      lastModified: res.headers.get('Last-Modified'),
    };
  } catch (_) {
    return null;
  }
}

function showStaleBanner({ servedShort, liveSha, ageMin }) {
  const banner = document.getElementById('freshness-banner');
  if (!banner) return;
  const msg = banner.querySelector('.freshness-message');
  const refreshBtn = banner.querySelector('.freshness-refresh');
  const dismissBtn = banner.querySelector('.freshness-dismiss');
  if (!msg || !refreshBtn || !dismissBtn) return;
  const template = t('ui.freshness.stale')
    || 'Newer build is live (commit {liveSha} vs served {servedShort}, {ageMin} min ago). Refresh.';
  msg.textContent = applyTemplate(template, {
    liveSha: liveSha || '?',
    servedShort: servedShort || '?',
    ageMin: ageMin != null ? ageMin : '?',
  });
  refreshBtn.textContent = t('ui.freshness.refresh') || 'Refresh';
  refreshBtn.onclick = () => location.reload();
  dismissBtn.onclick = () => { banner.hidden = true; };
  banner.hidden = false;
  bannerShown = true;
}

function shortHash(etag) {
  if (!etag || typeof etag !== 'string') return null;
  // GitHub Pages ETag form: `"<hex>-<hex>"` — keep the first hex chunk's
  // last 7 chars to mirror git short-SHA conventions.
  const hex = etag.replace(/^W\//, '').replace(/^"|"$/g, '').split('-')[0] || '';
  if (!hex) return null;
  return hex.slice(-7);
}

async function probe() {
  if (bannerShown) return;
  if (!State.dataEtag) return;
  const live = await fetchLiveModelsEtag();
  if (!live || !live.etag) return;
  if (live.etag === State.dataEtag) return;

  // Fresh deploy detected. Pull the SHA + age for human-readable banner copy.
  let liveSha = null;
  let ageMin = null;
  const commit = await fetchLatestCommitSha();
  if (commit) {
    liveSha = commit.sha;
    if (commit.date) {
      const ms = Date.now() - new Date(commit.date).getTime();
      if (Number.isFinite(ms) && ms > 0) ageMin = Math.max(1, Math.round(ms / 60_000));
    }
  }
  const servedShort = shortHash(State.dataEtag);
  showStaleBanner({ servedShort, liveSha, ageMin });
}

export function startFreshnessWatch() {
  if (started) return;
  started = true;
  setTimeout(probe, INITIAL_DELAY_MS);
  setInterval(probe, POLL_INTERVAL_MS);
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') probe();
  });
}
