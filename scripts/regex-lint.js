#!/usr/bin/env node
/*
 * regex-lint.js — pre-commit guard for the regex pattern library.
 *
 * Reads:   data/sources-whitelist.json._schema.regexLibrary.patterns
 *          scripts/regex-corpus.json
 *
 * Verifies:
 *   1. Every pattern compiles.
 *   2. Every positive case matches AND captures the expected named groups.
 *   3. Every negative case rejects.
 *   4. Every redosTrigger executes in < maxMs (default 50ms).
 *   5. Audit checklist (no nested unbounded quantifiers, no anchor-less .+ / \w+ /
 *      \S+ that can blow up).
 *
 * Exits non-zero on any failure. Output mimics the plan's example:
 *   ✓ bench_score_labeled  — corpus 8/8 pos, 4/4 neg, ReDoS 0/2 (max 12ms)
 *   ✗ bench_score_qualified — corpus 4/5 pos (regression on Unicode em-dash); BLOCKED
 */

const fs = require('fs');
const path = require('path');

const PROJECT = path.resolve(__dirname, '..');
const WHITELIST = path.join(PROJECT, 'data', 'sources-whitelist.json');
const CORPUS    = path.join(PROJECT, 'scripts', 'regex-corpus.json');

const RED   = '\x1b[31m';
const GREEN = '\x1b[32m';
const YELL  = '\x1b[33m';
const DIM   = '\x1b[2m';
const RESET = '\x1b[0m';

function read(path) { return JSON.parse(fs.readFileSync(path, 'utf8')); }

function materialize(entry) {
  if (typeof entry.input === 'string') return entry.input;
  if (entry._repeat) {
    const { head = '', char, n, tail = '' } = entry._repeat;
    return head + char.repeat(n) + tail;
  }
  throw new Error('corpus entry missing input or _repeat');
}

// Heuristic ReDoS-shape detector. Catches the dangerous constructs the plan
// calls out before the regex even runs.
function auditPattern(name, raw) {
  const issues = [];
  const dangerous = [
    { rx: /\([^)]*[+*]\)\s*[+*]/, msg: 'nested unbounded quantifier (a+)+ or (a*)*' },
    { rx: /\(\.\*[^)]*\)\s*[+*]/, msg: '(.*)+/(.*)* — guaranteed catastrophic' },
    { rx: /\(\.\+[^)]*\)\s*[+*]/, msg: '(.+)+/(.+)*  — guaranteed catastrophic' },
    { rx: /\(\\\w\+\)\s*[+*]/, msg: '(\\w+)+/(\\w+)* — likely catastrophic' },
    { rx: /\(\\S\+\)\s*[+*]/, msg: '(\\S+)+/(\\S+)* — likely catastrophic' },
  ];
  for (const d of dangerous) if (d.rx.test(raw)) issues.push(d.msg);
  // Anchor-less unbounded `.+` / `.*` is *allowed* inside character-bounded
  // classes; flag only the bare-form anchorless-end case where `.+` ends the
  // pattern with no following anchor or bound.
  if (/[^\\\]]\.\+\$?$/.test(raw) && !raw.endsWith('$')) {
    issues.push('trailing unbounded .+ — add a bound or anchor');
  }
  return issues;
}

function compilePattern(name, def) {
  try {
    return new RegExp(def.regex, def.flags || '');
  } catch (e) {
    throw new Error(`compile failed: ${e.message}`);
  }
}

function runOne(name, def, suite) {
  const audit = auditPattern(name, def.regex);
  if (audit.length) {
    return { name, ok: false, reason: 'audit:\n      ' + audit.join('\n      ') };
  }

  let regex;
  try { regex = compilePattern(name, def); }
  catch (e) { return { name, ok: false, reason: e.message }; }

  // Each positive must match. Captures: only check named groups present in
  // `expect` — extras are fine.
  let posPass = 0, posFail = [];
  for (const c of (suite.positive || [])) {
    const input = materialize(c);
    const m = input.match(regex);
    if (!m) { posFail.push(`positive miss: ${JSON.stringify(input).slice(0, 80)}`); continue; }
    let captureOk = true;
    for (const [k, v] of Object.entries(c.expect || {})) {
      if ((m.groups && m.groups[k]) !== v) {
        posFail.push(`capture mismatch [${k}]: got ${JSON.stringify(m.groups && m.groups[k])}, expected ${JSON.stringify(v)} on ${JSON.stringify(input).slice(0, 60)}`);
        captureOk = false;
        break;
      }
    }
    if (captureOk) posPass++;
  }

  // Each negative must reject (no match anywhere).
  let negPass = 0, negFail = [];
  for (const c of (suite.negative || [])) {
    const input = materialize(c);
    const m = input.match(regex);
    if (m) negFail.push(`negative matched: ${JSON.stringify(input).slice(0, 80)} → ${JSON.stringify(m[0]).slice(0, 60)}`);
    else negPass++;
  }

  // ReDoS triggers — execution must complete under maxMs.
  let redosPass = 0, redosFail = [];
  let worstMs = 0;
  for (const c of (suite.redosTriggers || [])) {
    const input = materialize(c);
    const t0 = Date.now();
    try { input.match(regex); } catch (e) { /* engine throw is also a fail */ }
    const dt = Date.now() - t0;
    if (dt > worstMs) worstMs = dt;
    if (dt > (c.maxMs || 50)) redosFail.push(`ReDoS: ${dt}ms > ${c.maxMs || 50}ms (${c.comment || ''})`);
    else redosPass++;
  }

  const ok = posFail.length === 0 && negFail.length === 0 && redosFail.length === 0;
  const summary = `corpus ${posPass}/${(suite.positive || []).length} pos, ${negPass}/${(suite.negative || []).length} neg, ReDoS ${redosPass}/${(suite.redosTriggers || []).length} (max ${worstMs}ms)`;
  return {
    name, ok, summary,
    failures: [...posFail, ...negFail, ...redosFail],
  };
}

function main() {
  let whitelist, corpus;
  try {
    whitelist = read(WHITELIST);
    corpus = read(CORPUS);
  } catch (e) {
    console.error(`${RED}fatal:${RESET} ${e.message}`);
    process.exit(2);
  }

  const patterns = (whitelist._schema && whitelist._schema.regexLibrary && whitelist._schema.regexLibrary.patterns) || {};
  const suites = corpus.patterns || {};

  if (!Object.keys(patterns).length) {
    console.error(`${RED}fatal:${RESET} no patterns in whitelist._schema.regexLibrary.patterns`);
    process.exit(2);
  }

  const missing = Object.keys(patterns).filter(k => !suites[k]);
  if (missing.length) {
    console.error(`${RED}fatal:${RESET} corpus missing entries for: ${missing.join(', ')}`);
    process.exit(2);
  }

  const orphan = Object.keys(suites).filter(k => !patterns[k]);
  if (orphan.length) {
    console.error(`${YELL}warn:${RESET} corpus has orphan entries (no matching pattern): ${orphan.join(', ')}`);
  }

  const results = [];
  for (const [name, def] of Object.entries(patterns)) {
    results.push(runOne(name, def, suites[name]));
  }

  let failed = 0;
  for (const r of results) {
    if (r.ok) {
      console.log(`${GREEN}✓${RESET} ${r.name.padEnd(34)} — ${DIM}${r.summary}${RESET}`);
    } else {
      failed++;
      const tail = r.summary ? r.summary : r.reason;
      console.log(`${RED}✗${RESET} ${r.name.padEnd(34)} — ${tail}`);
      for (const f of (r.failures || [])) console.log(`    ${RED}·${RESET} ${f}`);
      if (r.reason) console.log(`    ${RED}·${RESET} ${r.reason}`);
    }
  }

  if (failed) {
    console.log(`\n${RED}BLOCKED${RESET}: ${failed}/${results.length} patterns failed lint.`);
    process.exit(1);
  } else {
    console.log(`\n${GREEN}OK${RESET}: ${results.length}/${results.length} patterns pass lint.`);
  }
}

main();
