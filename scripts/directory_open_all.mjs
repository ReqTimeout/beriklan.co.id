#!/usr/bin/env node
/**
 * directory_open_all.mjs — Open all directory submit URLs in browser tabs.
 *
 * Usage:
 *   node scripts/directory_open_all.mjs                    # Open top 10 high-DR pending
 *   node scripts/directory_open_all.mjs --limit 5
 *   node scripts/directory_open_all.mjs --id clutch-co
 *
 * For each directory, opens the submit URL + a markdown packet side-by-side.
 * User manually fills out each form (captcha-protected, requires manual entry).
 */
import fs from 'node:fs';
import path from 'node:path';
import { exec } from 'node:child_process';

const ROOT = path.dirname(new URL(import.meta.url).pathname).replace('/scripts', '');
const DATA = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/directory-progress.json'), 'utf-8'));

const args = process.argv.slice(2);
let limit = 10;
let idFilter = null;
let dryRun = false;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--limit') limit = parseInt(args[++i]);
  if (args[i] === '--id') idFilter = args[++i];
  if (args[i] === '--dry-run') dryRun = true;
}

let pending = DATA.items.filter(i => i.status === 'pending');
if (idFilter) pending = pending.filter(i => i.id === idFilter);
pending.sort((a, b) => (b.domain_rating || 0) - (a.domain_rating || 0));
pending = pending.slice(0, limit);

console.log(`Opening ${pending.length} directory submit URLs in browser...\n`);

const open = dryRun ? (url) => console.log(`  [dry-run] would open: ${url}`) : (url) => exec(`open "${url}"`);

for (const item of pending) {
  const dr = item.domain_rating || 0;
  const priority = item.priority === 'high' ? '🔴 HIGH' : '⚪ med';
  console.log(`  ${priority} ${item.id.padEnd(28)} DR=${String(dr).padStart(3)} → ${item.submit_url}`);
  open(item.submit_url);
}

if (!dryRun) {
  console.log(`\n✓ ${pending.length} URLs opened in your default browser.`);
  console.log(`\n📋 Submission packets are in: scripts/submissions/`);
  console.log(`   Read each .md file while filling out the form.`);
}