#!/usr/bin/env node
/**
 * push-rank.js — Audit harian posisi 4-20 di GSC dan resubmit ke GSC Indexing API.
 *
 * Tujuan: naikkan ranking halaman yang sudah di page-1 tapi belum top-3.
 * Strategi: refresh crawl dengan re-submit URL ke Google (signals "update").
 *
 * Cara pakai (sudah ter-deploy cron di worker):
 *   curl -s "https://beriklan.co.id/api/cron/push-rank?token=beriklan-admin-2026&posMin=4&posMax=20&count=30"
 *
 * Cron: jalan tiap jam via `0 * * * *` di `worker-entry.js:667` (run push-rank).
 * Hasil: candidates → submitted ke GSC, log di growth_log dengan action='push-rank'.
 *
 * Script ini opsional (untuk run lokal / inspeksi manual via D1):
 *   node scripts/push-rank.js --dry-run
 */
import { execSync } from 'node:child_process';

const API_TOKEN = process.env.CLOUDFLARE_API_TOKEN;
if (!API_TOKEN) {
  console.error('CLOUDFLARE_API_TOKEN belum diset. Export dulu (lihat DEPLOY_OPERATIONS.md) sebelum menjalankan script ini.');
  process.exit(1);
}
const isDryRun = process.argv.includes('--dry-run');

console.log(`\n=== push-rank ${isDryRun ? 'DRY RUN (cuma baca D1)' : 'LIVE'} ===\n`);

// Query URL posisi 4-20 dengan impresi >=30/14hari
const q = `
  SELECT page_url, ROUND(AVG(position), 1) as pos, SUM(impressions) as impr, SUM(clicks) as clicks
  FROM keyword_ranks
  WHERE position BETWEEN 4 AND 20
    AND date >= date('now', '-14 days')
  GROUP BY page_url
  HAVING impr >= 30
  ORDER BY pos ASC, impr DESC
  LIMIT 50
`;

const out = execSync(
  `npx wrangler d1 execute beriklan-seo --remote --json --command "${q.replace(/\n/g, ' ')}"`,
  { encoding: 'utf-8', stdio: 'pipe', env: { ...process.env, CLOUDFLARE_API_TOKEN: API_TOKEN } }
);

const rows = JSON.parse(out)[0]?.results || [];
console.log(`Kandidat posisi 4-20 dengan impresi >=30/14hari: ${rows.length}\n`);

for (const r of rows) {
  const ctr = ((r.clicks / r.impr) * 100).toFixed(1);
  console.log(`  pos ${r.pos} · ${r.impr} imp · ${r.clicks} clicks · CTR ${ctr}%  ${r.page_url}`);
}

if (isDryRun || rows.length === 0) {
  console.log(`\n${isDryRun ? 'Dry run selesai.' : 'Tidak ada kandidat. Tunggu rank-sync (cron 6jam) untuk isi data dari GSC.'}`);
  process.exit(0);
}

console.log(`\nUntuk eksekusi live, jalankan:`);
console.log(`  curl -s "https://beriklan.co.id/api/cron/push-rank?token=beriklan-admin-2026&posMin=4&posMax=20&count=30" | jq`);
