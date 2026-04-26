#!/usr/bin/env node
/*
 * whitelist-format-migration.js — one-shot schema migration.
 *
 * Walks every entry in data/sources-whitelist.json under {leaderboards,
 * aggregators, community, local, registries} and:
 *   1. Sets `format` to a canonical taxonomy key, derived in priority order:
 *        a) signal from `_runtime.healthChecks[<domain>].status`
 *        b) legacy entry.format (`unknown`/`static`/`spa`/...) mapped to canonical
 *        c) URL heuristics (raw.githubusercontent.com → github_raw_*)
 *        d) default: `static_html_table`
 *   2. Populates `fallbacks[]` from
 *        _schema.formatTaxonomy[<canonical>].defaultFallbacks  (deep-cloned)
 *      so each entry carries its own cascade — entries can later be tuned
 *      per-vendor without re-running migration.
 *   3. Stamps `format_lastVerified` to today (so the next stale-check has a
 *      datum to age against).
 *   4. Initialises `extractor` from formatTaxonomy[<canonical>].extractor when
 *      not already set.
 *
 * Vendors object is left untouched — its URL bundles are typed by phase, not
 * format; per-URL format is decided by the agent at fetch-time using the same
 * formatTaxonomy/healthChecks signals.
 *
 * Output:
 *   - Mutates data/sources-whitelist.json in place after rotating .bak.
 *   - Prints a per-entry diff to stdout (terse).
 *
 * DEVELOPER: this script is one-shot. AFTER reviewing the diff and committing
 * the migrated whitelist, DELETE this file in the same commit
 * (`git rm scripts/whitelist-format-migration.js`).  Leaving migration scripts
 * lying around violates the project's "no version-suffix files" rule.
 */

const fs = require('fs');
const path = require('path');

const PROJECT = path.resolve(__dirname, '..');
const WHITELIST = path.join(PROJECT, 'data', 'sources-whitelist.json');

const TODAY = new Date().toISOString().slice(0, 10);

// Map of `_runtime.healthChecks[*].status` → canonical formatTaxonomy key.
const HEALTH_TO_FORMAT = {
  'spa_no_data':       'spa_full',
  'spa_partial':       'spa_partial',
  'partial_static':    'spa_partial',
  'static':            'static_html_article',
  '403_blocked':       'bot_blocked',
  '404_or_404':        'bot_blocked',
  'image_embedded':    'image_embedded',
};

// Map of legacy entry.format values → canonical formatTaxonomy key.
const LEGACY_TO_FORMAT = {
  'unknown':         'static_html_table',
  'static':          'static_html_article',
  'spa':             'spa_full',
  'spa_partial':     'spa_partial',
  'partial_static':  'spa_partial',
  // pass-throughs (already canonical)
  'static_html_table':   'static_html_table',
  'static_html_article': 'static_html_article',
  'static_markdown':     'static_markdown',
  'static_json_api':     'static_json_api',
  'github_raw_json':     'github_raw_json',
  'github_raw_markdown': 'github_raw_markdown',
  'spa_full':            'spa_full',
  'meta_tag_extract':    'meta_tag_extract',
  'image_embedded':      'image_embedded',
  'bot_blocked':         'bot_blocked',
  'pdf_report':          'pdf_report',
  'websearch_snippet':   'websearch_snippet',
};

function urlHeuristic(url) {
  if (!url) return null;
  if (/raw\.githubusercontent\.com.*\.json/i.test(url)) return 'github_raw_json';
  if (/raw\.githubusercontent\.com.*\.(md|markdown)/i.test(url)) return 'github_raw_markdown';
  if (/github\.com\/[^/]+\/[^/]+\/blob\/.*\.json/i.test(url)) return 'github_raw_json';
  if (/github\.com\/[^/]+\/[^/]+(?:$|\/$|\/tree)/i.test(url)) return 'github_raw_markdown';
  if (/arxiv\.org\/(?:pdf|abs)/i.test(url)) return 'pdf_report';
  if (/huggingface\.co\/datasets\/.*\/raw\//i.test(url)) return 'static_json_api';
  if (/\.pdf(?:[?#]|$)/i.test(url)) return 'pdf_report';
  return null;
}

function domainOf(url) {
  if (!url) return null;
  try { return new URL(url).hostname.replace(/^www\./, ''); }
  catch (_) { return null; }
}

function lookupHealth(healthChecks, url) {
  if (!healthChecks || !url) return null;
  const dom = domainOf(url);
  if (!dom) return null;
  // healthChecks keys are domain or domain+path prefixes
  // exact-domain match preferred; otherwise prefix match.
  for (const key of Object.keys(healthChecks)) {
    const k = key.replace(/^https?:\/\//, '').replace(/^www\./, '');
    if (k === dom) return healthChecks[key].status;
  }
  for (const key of Object.keys(healthChecks)) {
    const k = key.replace(/^https?:\/\//, '').replace(/^www\./, '');
    if (url.includes(k)) return healthChecks[key].status;
  }
  return null;
}

function inferFormat(entry, healthChecks) {
  const url = entry.url;
  const healthSignal = lookupHealth(healthChecks, url);
  if (healthSignal && HEALTH_TO_FORMAT[healthSignal]) {
    return { format: HEALTH_TO_FORMAT[healthSignal], source: `health:${healthSignal}` };
  }
  if (entry.format && LEGACY_TO_FORMAT[entry.format]) {
    return { format: LEGACY_TO_FORMAT[entry.format], source: `legacy:${entry.format}` };
  }
  const heur = urlHeuristic(url);
  if (heur) return { format: heur, source: 'url-heuristic' };
  return { format: 'static_html_table', source: 'default' };
}

function deepClone(o) { return JSON.parse(JSON.stringify(o)); }

function migrateList(list, label, formatTaxonomy, healthChecks, diffLog) {
  if (!Array.isArray(list)) return 0;
  let touched = 0;
  for (const entry of list) {
    const { format, source } = inferFormat(entry, healthChecks);
    const oldFormat = entry.format || '<unset>';
    const taxon = formatTaxonomy[format] || {};
    const fallbacks = deepClone(taxon.defaultFallbacks || []);
    const extractor = taxon.extractor || 'regex_extract';

    const beforeFmt = entry.format;
    const beforeFallbacksLen = Array.isArray(entry.fallbacks) ? entry.fallbacks.length : 0;

    entry.format = format;
    if (!entry.extractor) entry.extractor = extractor;
    if (!entry.fallbacks || !Array.isArray(entry.fallbacks) || entry.fallbacks.length === 0) {
      entry.fallbacks = fallbacks;
    }
    entry.format_lastVerified = entry.format_lastVerified || TODAY;
    if (entry.consecutiveFailures === undefined) entry.consecutiveFailures = 0;
    if (entry.lastVerifiedDate === undefined) entry.lastVerifiedDate = null;

    if (beforeFmt !== format || beforeFallbacksLen !== fallbacks.length) {
      diffLog.push(`[${label}] ${entry.name || entry.url}: format ${oldFormat} → ${format} (${source}); fallbacks ${beforeFallbacksLen}→${entry.fallbacks.length}`);
      touched++;
    }
  }
  return touched;
}

function main() {
  const blob = JSON.parse(fs.readFileSync(WHITELIST, 'utf8'));
  const formatTaxonomy = (blob._schema && blob._schema.formatTaxonomy) || {};
  const healthChecks   = (blob._runtime && blob._runtime.healthChecks) || {};

  if (!Object.keys(formatTaxonomy).length) {
    console.error('fatal: _schema.formatTaxonomy missing — run schema extension first.');
    process.exit(2);
  }

  const diff = [];
  let total = 0;
  for (const cat of ['leaderboards', 'aggregators', 'community', 'local', 'registries']) {
    if (!Array.isArray(blob[cat])) continue;
    total += migrateList(blob[cat], cat, formatTaxonomy, healthChecks, diff);
  }

  // Rotate .bak before writing.
  const bak = WHITELIST + '.bak';
  if (fs.existsSync(bak)) fs.unlinkSync(bak);
  fs.copyFileSync(WHITELIST, bak);

  fs.writeFileSync(WHITELIST, JSON.stringify(blob, null, 2) + '\n', 'utf8');

  console.log('whitelist-format-migration:');
  for (const line of diff) console.log('  ' + line);
  console.log(`\n${total} entries touched. Backup: ${path.relative(PROJECT, bak)}`);
  console.log('REMINDER: review diff above, commit, then `git rm scripts/whitelist-format-migration.js` in the same commit.');
}

main();
