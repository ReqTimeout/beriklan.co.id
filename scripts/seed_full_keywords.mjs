#!/usr/bin/env node
/**
 * seed_full_keywords.mjs
 * Seed remaining keywords from web/src/data/keyword-queue.json into D1 keyword_queue.
 * - Dedupes by keyword_normalized against existing D1 rows (dumped to /tmp/existing_norm_set.json)
 *   AND within the JSON itself.
 * - Emits chunked `INSERT OR IGNORE` SQL files under scripts/db/chunks_full/.
 * - IDs use `kwx_<i>` prefix to avoid PK collision with existing `kw_...` rows.
 * - has_post / generated items keep status='generated' + article_slug to avoid regeneration.
 */
import fs from 'fs';
import path from 'path';

const ROOT = path.resolve(process.cwd());
const JSON_PATH = path.join(ROOT, 'web/src/data/keyword-queue.json');
const EXISTING_SET = '/tmp/existing_norm_set.json';
const OUT_DIR = path.join(ROOT, 'scripts/db/chunks_full');

const ROWS_PER_STATEMENT = 100;
const ROWS_PER_FILE = 20000;

function sqlStr(v) {
  if (v === null || v === undefined) return 'NULL';
  return "'" + String(v).replace(/'/g, "''") + "'";
}
function sqlInt(v) {
  const n = parseInt(v, 10);
  return Number.isFinite(n) ? String(n) : '0';
}

const existing = new Set(JSON.parse(fs.readFileSync(EXISTING_SET, 'utf8')));
const data = JSON.parse(fs.readFileSync(JSON_PATH, 'utf8'));
console.log('JSON items:', data.length, '| existing D1 normalized:', existing.size);

const seen = new Set(existing);
const rows = [];
for (const k of data) {
  const norm = String(k.keyword_normalized || k.keyword || '').toLowerCase().trim();
  const kw = String(k.keyword || '').trim();
  if (!norm || !kw) continue;
  if (seen.has(norm)) continue;       // already in D1 or duplicate within JSON
  seen.add(norm);
  const hasPost = !!k.has_post || k.status === 'generated';
  rows.push({
    keyword: kw,
    keyword_normalized: norm,
    source: k.source || 'miner',
    discovered_at: k.created_at || k.discovered_at || new Date().toISOString(),
    status: hasPost ? 'generated' : 'pending',
    priority_score: k.priority_score || 0,
    service: k.service || null,
    article_slug: hasPost ? (k.slug || null) : null,
  });
}
console.log('NEW rows to seed:', rows.length);

if (fs.existsSync(OUT_DIR)) fs.rmSync(OUT_DIR, { recursive: true, force: true });
fs.mkdirSync(OUT_DIR, { recursive: true });

const COLS = '(id, keyword, keyword_normalized, source, discovered_at, status, priority_score, service, article_slug)';
let fileIdx = 0, fileBuf = [], stmtVals = [];
let flushed = 0;

function flushStatement() {
  if (!stmtVals.length) return;
  fileBuf.push('INSERT OR IGNORE INTO keyword_queue ' + COLS + ' VALUES\n' + stmtVals.join(',\n') + ';');
  stmtVals = [];
}
function flushFile() {
  flushStatement();
  if (!fileBuf.length) return;
  const name = 'chunk_' + String(fileIdx).padStart(3, '0') + '.sql';
  fs.writeFileSync(path.join(OUT_DIR, name), fileBuf.join('\n'));
  fileIdx++;
  fileBuf = [];
}

for (let i = 0; i < rows.length; i++) {
  const r = rows[i];
  const id = 'kwx_' + i;
  stmtVals.push('(' + [
    sqlStr(id), sqlStr(r.keyword), sqlStr(r.keyword_normalized), sqlStr(r.source),
    sqlStr(r.discovered_at), sqlStr(r.status), sqlInt(r.priority_score),
    sqlStr(r.service), sqlStr(r.article_slug),
  ].join(',') + ')');
  if (stmtVals.length >= ROWS_PER_STATEMENT) flushStatement();
  flushed++;
  if (flushed >= ROWS_PER_FILE) { flushFile(); flushed = 0; }
}
flushFile();

console.log('Wrote', fileIdx, 'chunk files to', OUT_DIR);
