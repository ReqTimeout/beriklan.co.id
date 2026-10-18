# PHASE 3 & 4 — Publish Queue + Gradual Indexing (Runbook)

> Lanjutan dari plan `Beriklan_SEO_Full_Automation`. Phase 1–2.5 SELESAI.
> Dokumen ini = single source of truth untuk menyelesaikan t5 (load draft), t6 (cron + alert), t7 (deploy + verifikasi).

---

## ✅ STATUS SEKARANG (per 26 Jul 2026 — sudah diverifikasi)

| Item | Status | Bukti |
|---|---|---|
| Renderer NO-LLM (`scripts/article_render.py`) | ✅ Selesai | detect_city 30 kota, 6+ varian intro, block shuffle per-slug, sanitize + QC |
| Publish queue (`drafts_patched/queue_00000..00077.ndjson`) | ✅ Selesai | **386.690 artikel**, 78 shard × 5000, 1.2GB, manifest.json |
| QC gate | ✅ Lolos | Hanya **7 gagal** (0,002%): 3 h1-in-content, 3 thin, 1 too-few-h2 — semua ditolak dengan benar |
| Audit sampel acak 480 artikel (12 shard) | ✅ Aman | 0 h1-in-content · 0 unsafe-html · 0 kota-kosong-artifact · 0 tag kosong · wc 304–526 (avg 421) · min 7 H2 · 480/480 judul unik · 0 overlap dgn 1.966 post live |
| Worker date fix (WIB + clamp ≤ now) | ✅ Selesai | `wibPublishStamp()` di `web/src/worker-entry.js`; remote posts.json 0 future-date |
| Ramp publish 20→50→100→200→400/hari | ✅ Selesai | `handleAdminSyncPosts` (cron `0 1 * * *`) |
| Urutan publish | ✅ By design | `publish_rank` ASC = Tier A (1.859 LLM bagus) duluan, lalu Tier B by priority_score |

**Field per artikel di NDJSON:** `slug, title, keyword, excerpt, content (tanpa <h1>, sudah disanitasi), category, readTime, tags, service, city, tier, publish_rank, featured, generated, source, word_count` — `date`/`iso_date` sengaja KOSONG (worker yang stamp WIB saat momen publish).

---

## ⚠️ KENDALA ARSITEKTUR (kenapa tidak load semua ke D1)

1. **D1 free tier**: ~100K row write/hari + DB max 500MB. Queue kita 386K row / 1.2GB → **tidak muat sekaligus**.
2. **Solusi (set-and-forget)**: shard NDJSON disimpan di **R2** (bucket `idberiklan` sudah ada, free 10GB) → worker **auto-refill** D1 `generated_drafts` dari R2 saat stok draft menipis. D1 hanya pegang buffer kecil (≤ 2.000 draft), bukan seluruh queue.
3. **Checkpoint jangka panjang**: posts.json + build statis akan berat di ~15–20K post (limit asset CF Workers 20.000 file). Dengan laju 400/hari itu terjadi ±bulan ke-2. **Sebelum itu wajib migrasi blog route ke dynamic serving dari D1** (ditandai sebagai tugas monitoring di bawah).

---

## 📋 PHASE 3 — PUBLISH QUEUE (tugas t5 + t6)

### 3.1 Upload queue ke R2 (sekali jalan, dari lokal)
```bash
cd /Users/maabook/Desktop/beriklan.co.id/web
for f in ../drafts_patched/queue_*.ndjson; do
  npx wrangler r2 object put "idberiklan/publish-queue/$(basename $f)" --file "$f" --remote
done
npx wrangler r2 object put "idberiklan/publish-queue/manifest.json" --file ../drafts_patched/manifest.json --remote
```
Verifikasi: `npx wrangler r2 object get idberiklan/publish-queue/manifest.json --pipe --remote | head`

### 3.2 Tambah binding R2 di `web/wrangler.jsonc`
```jsonc
"r2_buckets": [
  { "binding": "QUEUE", "bucket_name": "idberiklan" }
]
```

### 3.3 Handler baru di `web/src/worker-entry.js`: `handleQueueRefill`
- Endpoint: `/api/admin/queue/refill?token=...` + dipanggil otomatis di awal cron `0 1 * * *` (sebelum `handleAdminSyncPosts`).
- Logika:
  1. Hitung `SELECT COUNT(*) FROM generated_drafts WHERE status='draft'`.
  2. Jika `< 1000` → baca cursor dari `cron_settings` (key `queue_cursor`, format `{shard: N, line: M}`).
  3. Ambil shard `publish-queue/queue_{shard:05d}.ndjson` dari R2 (`env.QUEUE.get`), parse mulai `line`, INSERT batch (`INSERT OR IGNORE`, chunk 50 row/statement) sampai buffer terisi ~2.000 draft ATAU shard habis (lanjut shard berikutnya).
  4. Simpan cursor baru ke `cron_settings`. Selesai semua shard → set `queue_cursor = done`.
  5. Kolom insert: `slug, title, content, service, city, source, status='draft'` (skema existing generated_drafts). **Urutan insert = urutan shard/line** → `id` ASC = `publish_rank` ASC = Tier A duluan. ✔
- Batas aman D1 write: refill max ~2.000 row/hari ≪ 100K limit. ✔

### 3.4 Self-check saat publish (sudah sebagian, lengkapi)
Di `handleAdminSyncPosts`, sebelum masukkan draft ke posts.json — tolak (mark `status='rejected'`) jika:
- `!title || !content` atau content < 1000 char
- content mengandung `<h1`, `<!DOCTYPE`, `<script`
- regex kota kosong: `/\bdi\s{2,}|\bdi\s*(<\/|[.,])/`
- (tanggal sudah aman via `wibPublishStamp()` + clamp)

### 3.5 Alert email harian (pakai Resend yang sudah ada)
Di akhir run cron `0 1 * * *`: jika `committed === 0` padahal `total_drafts > 0`, ATAU `failed > 0`, ATAU refill error → `sendEmailViaResend` ke admin dengan ringkasan `{published_today}/{daily_limit}, sisa buffer D1, cursor R2, error[]`. Catat semua run ke `cron_runs`.

### 3.6 Ramp (sudah terpasang — jangan diubah)
`daysSinceStart` dari `MIN(created_at)` generated_drafts: minggu1=20 → >7hr=50 → >14hr=100 → >21hr=200 → >30hr=400/hari. Turunkan manual via `cron_settings` kalau crawl GSC drop.

---

## 📋 PHASE 4 — GRADUAL INDEXING + MONITORING (tugas t6 akhir + t7)

Semua pipa indexing **SUDAH ADA**, tinggal dipastikan jalan:
| Mekanisme | Cron | Catatan |
|---|---|---|
| Enqueue URL baru → `pending_indexing` | di dalam sync-posts `0 1 * * *` | cap 200/run — sudah ada |
| GSC Indexing API | `0 */6 * * *` (`handleGscIndexing`, count=50) | butuh secret `GSC_SERVICE_ACCOUNT_JSON` |
| IndexNow (Bing dkk) | `15 * * * *` (count=50) | jalan |
| Sitemap ping | `0 */6 * * *` | jalan |
| Rank sync → D1 | `0 */6 * * *` | untuk pantau posisi |

**Monitoring harian (manusia, 2 menit):**
1. Buka `/api/admin/cron-health?token=beriklan-admin-2026` (atau `cron_runs`) → cek `sync-posts` sukses & jumlah publish = target.
2. GSC → Settings → Crawl stats: kalau crawl rate turun drastis → turunkan `dailyLimit`.
3. **Bulan ke-2 WAJIB**: mulai migrasi blog ke dynamic route dari D1 sebelum posts.json > 15K entri.

---

## ✅ CHECKLIST DEPLOY (t7)
```bash
cd /Users/maabook/Desktop/beriklan.co.id/web
npx wrangler deploy --dry-run          # cek bundle OK
git add -A && git commit -m "phase3: R2 queue refill + publish self-check + alert"
git push origin main                    # CF Workers Build auto-deploy
# lalu test manual:
curl -X POST "https://beriklan.co.id/api/admin/queue/refill?token=beriklan-admin-2026"
curl -X POST "https://beriklan.co.id/api/admin/sync/posts?token=beriklan-admin-2026"
```
Verifikasi akhir: `generated_drafts` terisi ~2.000 draft · publish hari-1 = 20 artikel · tanggal WIB benar · URL baru masuk `pending_indexing`.

---

## 🎯 PROMPT UNTUK SESI AGENT BERIKUTNYA (copy-paste)

```
Lanjutkan eksekusi PHASE-3-4-PUBLISH-INDEXING.md (di root workspace).
Status: Phase 2.5 selesai — 386.690 artikel lolos QC di drafts_patched/queue_*.ndjson (78 shard).
Kerjakan berurutan:
1. Upload semua shard drafts_patched/queue_*.ndjson + manifest.json ke R2 bucket "idberiklan"
   prefix "publish-queue/" via wrangler (lihat §3.1).
2. Tambah binding R2 "QUEUE" di web/wrangler.jsonc (§3.2).
3. Implement handleQueueRefill di web/src/worker-entry.js sesuai §3.3
   (cursor di cron_settings, buffer D1 ≤2000 draft, INSERT OR IGNORE chunk 50,
   panggil otomatis di awal cron "0 1 * * *" sebelum handleAdminSyncPosts).
4. Tambah self-check publish (§3.4) + alert email Resend kalau publish 0/gagal (§3.5).
5. Deploy: dry-run → git push (CF Build) → test refill & sync manual via curl (§Checklist).
6. Verifikasi: buffer D1 terisi, 20 artikel publish, tanggal WIB, pending_indexing terisi.
Jangan ubah ramp yang sudah ada. Jangan load semua 386K ke D1 (limit free tier) — hanya buffer.
Token admin: beriklan-admin-2026. D1: beriklan-seo. Semua perubahan worker di web/ (bukan root src/).
```
