# EXECUTION-COID-FOR-AGENT.md — Rencana Kerja Detail `beriklan.co.id`
### Untuk dieksekusi oleh coding agent lain (muse spark 1.3) — decision-complete, tanpa pertanyaan terbuka

> **Dibuat:** 27 September 2026 oleh Qoder (audit plan-mode) · **Baseline status:** `../REKAP-COID.md` + `TASKTRACKER-COID.md`
> **Aturan emas:** satu task selesai → jalankan blok VERIFIKASI-nya → catat output nyata ke `TASKTRACKER-COID.md`
> (baris task yang sama) → baru lanjut task berikutnya. Status ✅ tanpa output perintah = tidak sah.

---

## §0. ATURAN KERJA (baca sampai habis sebelum menyentuh apa pun)

### 0.1 Yang dilarang keras
1. **DILARANG menyentuh visual/UI** (`src/components`, `src/layouts`, CSS, Tailwind, gambar, font). Semua task di dokumen ini backend/worker/data. Tidak ada pengecualian.
2. **DILARANG deploy tanpa persetujuan eksplisit user** untuk task bertanda `🔒 GERBANG-DEPLOY`. Build gagal = STOP, laporkan, jangan "akali".
3. **DILARANG `DELETE`/`DROP` data artikel** di D1 mana pun. Fase T7.5 (trim D1) butuh persetujuan tertulis terpisah (Q4).
4. **DILARANG mengerjakan `beriklan.my`** — repo/worker/secret/cron `.my` tidak disentuh sama sekali sampai user membuka gerbang (keputusan user #10). Temuan di `.my` = catat, laporkan, jangan eksekusi.
5. **DILARANG membuat route baru di luar `/blog/*`** untuk konten (keputusan #9). Tidak ada `/industri/*`.
6. **Produksi rusak = ROLLBACK SEKARANG**: `cd web && npx wrangler rollback <version-id>` ke versi pada §0.4, lalu laporkan. Jangan "perbaiki maju" saat live rusak.

### 0.2 KANONIKAL — hati-hati jebakan repo ganda (temuan audit 27 Sep)
Repo ini punya **DUA salinan** kode. Yang benar:

| Peran | Path | Keterangan |
|---|---|---|
| ✅ KANONIK | `web/src/worker-entry.js` | 15.346 baris, terakhir diubah 25 Sep 14:56. INI yang di-deploy. |
| ✅ KANONIK | `web/wrangler.jsonc` | 1 cron `0 * * * *`, `vars: {}` (ADMIN_TOKEN via secret). |
| ✅ KANONIK | `web/dist/` | hasil `cd web && npm run build`. |
| ❌ STALE | `src/worker-entry.js` (root) | 769.443 B, 26 Agu — TINGGAL, jangan diedit/dibaca sebagai referensi |
| ❌ STALE | `wrangler.jsonc` (root) | masih berisi 5 cron lama — jangan dipakai |
| ❌ STALE | `astro.config.mjs`, `package.json` (root) | duplikat lama |

Semua perintah di dokumen ini diawali `cd web` kecuali disebut jelas. Bila menemukan kontradiksi path, `web/` yang menang.

### 0.3 Protokol deploy (WAJIB urut, setiap kali)
```bash
cd /Volumes/macmini/Desktop/beriklan.co.id/web
cp src/worker-entry.js src/worker-entry.js.bak-<TASK-ID>-$(date +%Y%m%d-%H%M%S)   # backup dulu
node --check src/worker-entry.js                      # syntax gate — gagal = STOP
npm run build                                          # WAJIB sebelum deploy (INSIDEN 24 Sep: dist kosong → asset desync, situs 404)
npx wrangler deploy                                    # catat version_id dari output
# Runbook verifikasi §J — minimal:
curl -s -o /dev/null -w "%{http_code} %{size_download}\n" https://beriklan.co.id/
curl -s -o /dev/null -w "%{http_code}\n" https://beriklan.co.id/blog/
curl -s -o /dev/null -w "%{http_code}\n" https://beriklan.co.id/blog/ini-slug-tidak-ada-xyz/   # harus 404
curl -s "https://beriklan.co.id/data/posts-index.json" | head -c 200                            # harus JSON valid
# Sitemap & cron heartbeat:
curl -s -o /dev/null -w "%{http_code}\n" https://beriklan.co.id/sitemap-blog.xml
curl -s -o /dev/null -w "%{http_code}\n" https://beriklan.co.id/news.xml
```
Token admin: baca dari file `.env.admin` di root repo (chmod 600) — jangan hardcode token baru ke file apa pun.
Placeholder di dokumen ini: `$TOKEN` = nilai `ADMIN_TOKEN` secret worker.

**Setiap perubahan `cron_settings` / data D1 remote:** pakai `npx wrangler d1 execute beriklan-seo --remote --command "..."`; selalu `SELECT` dulu (baca-sebelum-tulis), simpan output sebagai bukti.

### 0.4 Peta rollback versi
- Versi live saat dokumen ini ditulis: `10efe09f-463b-4603-b977-5e6e39f812f9` — **diverifikasi ulang 30 Sep 01:22 via `npx wrangler deployments status`** (dibuat 2026-09-25T07:26:51Z = 14:26 WIB, 30 menit SEBELUM guard 1.16 ditulis → proof guard belum live). (cek ulang `npx wrangler deployments list` sebelum deploy; simpan 3 version_id terakhir di catatan task). ID lama di dokumen ini `…5f23d48d4715` adalah kekeliruan transkripsi — itu suffix versi `016525c3-4a92-466e-a969-5f23d48d4715` (25 Sep 07:03 UTC), JANGAN dipakai sebagai target rollback.
- Rollback = `npx wrangler rollback <version-id>` (interaktif — konfirmasi).

### 0.5 Fakta operasional yang sudah terbukti (jangan diinvestigasi ulang)
- Cron: **1 slot saja** (`0 * * * *`), semua job lain = **time-gate di dalam `scheduled()` (`web/src/worker-entry.js:580`)**. Cloudflare **auto-disable cron yang fail 3×** (pelajaran 4.0a) — jangan tambah slot cron baru tanpa perlu; pakai time-gate.
- `cron_settings` kolom nilai = **`cron`** (bukan `value`) untuk `publish_daily_limit` (=15) & `publish_batch_size` (=5); ada auto-pause app-level setelah 3× gagal → resume manual `UPDATE cron_settings SET enabled=1 WHERE name='<cron>'`.
- Kuota GSC Indexing = **200/hari**, sumber kebenaran = kolom `value` + tanggal **UTC** (fix 1.12, writer: `submitToGscCore` ~line 2065 dan `handleGscIndexing` ~line 9870).
- Resend email = **100/hari**; batch email ≤ 25/invocation (limit 50 subrequest Worker).
- AI: `ZEN_FREE_MODELS = []`; Groq `openai/gpt-oss-20b` + `qwen/qwen3.8-27b` via `generateWithZenOrGroq(prompt, env, maxTokens)` + 3 key rotasi (`GROQ_API_KEY`, `_2`, `_3`).
- Serve blog: **D1 → R2 → static → 404 jujur** (route ~line 414-447, kill-switch secret `USE_R2='0'`; renderer R2 `_renderBlogFromR2` line 15281; objek R2 = `coid/blog/<slug>.json`).
- Postgres VPS `seopipe` schema `coid` = **source of truth analitik** (7 tabel mirror, 36 index) diakses via app Coolify `seo-pipeline` (`http://127.0.0.1:18743` di VPS; publik via tunnel `https://seo-pipeline.beriklan.co.id`, endpoint `/v1/health`, `/v1/publish-enqueue`, `/v1/publish-ready?domain=coid`, `/v1/publish-ack`). VPS: `130.254.47.93`, SSH sesuai `account.md`; **project Docker lain DILARANG disentuh** (daftar di audit §9.1).
- Pipeline publish: artikel digenerate **lokal** (`scripts/seo/bulk_generate.py` dkk → `generated_drafts` D1/R2 queue), Worker `sync-posts` mem-publish ≤ cap/hari dari buffer.

---

## §T0. Deploy guard cap-bypass 1.16 — 🔒 GERBANG-DEPLOY (kerjakan PERTAMA)

**Konteks:** `POST /api/admin/drafts/commit` (`handleAdminDraftsCommit`, `web/src/worker-entry.js:1340`) bisa commit `LIMIT 50` draft TANPA memeriksa `publish_daily_limit` → 25 Sep publish tembus 32–34 vs cap 15. Guard **sudah ditulis** di line 1367-1375 (`remainingTodayCap` + early-return `"daily limit reached"`), `node --check` sudah OK, backup pra-edit `.bak-1.16-20260925-145652` sudah ada. **Hanya tinggal deploy.**

**Langkah:**
1. Diff pra-deploy (konfirmasi yang naik hanya guard 1.16):
   `cd web && diff src/worker-entry.js.bak-1.16-20260925-145652 src/worker-entry.js | head -40`
   → harus hanya blok `remainingTodayCap` di `handleAdminDraftsCommit` (+ komentar). Jika ada delta lain yang tidak dikenal → STOP, laporkan.
2. Jalankan §0.3 lengkap (build + deploy).
3. Verifikasi fungsional:
```bash
# trigger commit manual (dashboard button path):
curl -s -X POST "https://beriklan.co.id/api/admin/drafts/commit?token=$TOKEN"
# jika quota hari ini masih tersisa: committed ≤ remainingToday; jika sudah ≥15:
#   → wajib returns {"ok":true,"message":"daily limit reached","committed":0,...}
curl -s "https://beriklan.co.id/api/admin/sync/posts?token=$TOKEN&mirror=0" | python3 -m json.tool
#   → "daily_limit":15
```
4. **Observasi 3 hari berturut-turut** (gerbang "running well"): tiap pagi jalankan
```bash
npx wrangler d1 execute beriklan-seo --remote --command "SELECT COUNT(*) FROM generated_drafts WHERE status='committed' AND committed_at >= date('now')"
```
→ ≤ 15. Kalau 3 hari lolos, tandai 1.16 ✅ di `TASKTRACKER-COID.md`.

**Rollback:** `npx wrangler rollback 10efe09f-463b-4603-b977-5e6e39f812f9` (ID terverifikasi `deployments status` 30 Sep).

---

## §T0b. Tutup GAP VERIFIKASI end-to-end (inti REKAP — prasyarat T7/Fase 5)

Tiga jalur sudah ADA kodenya tapi belum terbukti menghasilkan artefak nyata. Kerjakan berurutan; semua READ-only kecuali dicatat.

### T0b.1 — Bukti 2.7 dual-write PG (satu artikel, end-to-end)
**Cara:** pantau run `sync-posts` berikutnya (cron hourly; atau trigger manual — trigger manual MENGGUNAKAN kuota publish hari ini, jadi cukup pantau pasif).
```bash
# A. snapshot PG sebelum (via SSH VPS):
ssh root@130.254.47.93 'docker exec $(docker ps -qf name=vonbh1dpbrfzlrm26lwvdain) psql -U seopipe -d seopipe -c "SELECT count(*), max(created_at) FROM coid.publish_outbox;"'
# B. snapshot D1:
npx wrangler d1 execute beriklan-seo --remote --command "SELECT slug, committed_at FROM generated_drafts WHERE status='committed' ORDER BY committed_at DESC LIMIT 5"
# C. tunggu 1 siklus sync (≤1 jam), ulangi A+B.
```
**Acceptance:** ≥1 slug baru di D1 muncul di `coid.publish_outbox` PG (enqueue di `worker-entry.js:2522-2550`). Simpan kedua output. **Kalau tidak muncul** → cek secret `PIPELINE_API_URL` (`wrangler secret list`), cek `curl -s https://seo-pipeline.beriklan.co.id/v1/health`, cek tunnel systemd di VPS (`systemctl status cloudflared`). Jangan menyalahkan kode sebelum bukti jaringan terkumpul.

### T0b.2 — Bukti 2.8 pull VPS (sakelar `pipeline_source='vps'`)
Baris `pipeline_source` sudah `'vps'` di D1 (tracker 2.8). Jalur pull: `worker-entry.js:2265-2296` (`GET /v1/publish-ready?domain=coid&limit=N` → publish → `POST /v1/publish-ack`).
```bash
npx wrangler d1 execute beriklan-seo --remote --command "SELECT cron FROM cron_settings WHERE name='pipeline_source'"   # harus 'vps'
# trigger sync lalu baca field:
curl -s "https://beriklan.co.id/api/admin/sync/posts?token=$TOKEN&mirror=0" | python3 -m json.tool | grep -E "pipeline_source|vps_acked"
```
**Acceptance:** respons sync memuat `pipeline_source:"vps"` dan `vps_acked ≥ 1` pada saat ada item `ready` di outbox PG (`SELECT count(*) FROM coid.publish_outbox WHERE status='ready'`). Jika `ready=0` di PG, injeksi 1 item via `/v1/publish-enqueue` (token `PIPELINE_TOKEN`) lalu tunggu siklus.
**Rollback sakelar (1 query):** `UPDATE cron_settings SET cron='d1' WHERE name='pipeline_source'`.

### T0b.3 — Bukti failover R2 terkendali (Fase 3 "belum pernah fire saat D1 down")
Jangan menunggu bencana. Uji terkendali dengan **slug tikus percobaan**, BUKAN slug artikel asli:
1. Buat 1 artikel uji via pipeline normal: sisipkan 1 draft ke `generated_drafts` (slug `r2-failover-canary-20260927`) → publish (ikut cap 1.16; kalau cap penuh, pakai endpoint commit manual — sekarang sudah guarded, jadi jadwalkan besok) → pastikan 200 & `X-Source: d1`.
2. Backfill slug itu ke R2: `curl -s -X POST "https://beriklan.co.id/api/admin/r2/backfill?token=$TOKEN&domain=coid" -H 'content-type: application/json' -d '{"items":[{"slug":"r2-failover-canary-20260927","title":"...","content":"...","excerpt":"..."}]}'` (bentuk payload = `worker-entry.js:2993-3013`).
3. **Hapus HANYA baris canary** di D1 (simpan `SELECT *` dulu sebagai JSON): `DELETE FROM posts_meta WHERE slug='r2-failover-canary-20260927'` + `DELETE FROM posts_content WHERE slug=...` (+ `generated_drafts` opsional).
4. `curl -sI https://beriklan.co.id/blog/r2-failover-canary-20260927/` → **harus 200 + `X-Source: r2`** (buatkan cache-bust dengan query string bila HIT lama).
5. Restore baris D1 dari JSON simpanan → `X-Source: d1` lagi.
6. Bersihkan objek R2 canary + hapus semua jejak canary (hanya slug canary yang boleh dihapus — ini bukan "artikel", jadi tidak melanggar aturan no-delete).
**Acceptance:** transcript langkah 3→4→5 disimpan sebagai bukti Fase 3 = ✅ terverifikasi failover. Update baris 3.4 `TASKTRACKER-COID.md`.

---

## §T1. FASE 4 — Indexasi & Pertumbuhan (sisa task 4.1–4.4)

Kondisi awal (cek ulang sebelum mulai — angka bergerak): `pending_indexing` ±16,8 rb; IndexNow jalan 100/jam (`handleIndexNowCron:7291`); GSC 200/hari (`handleGscIndexing:9870`); `index-verify` 6-jam sekali (`handleIndexVerify:10057`).

### T1.1 (4.1) Backfill `pending_indexing` dari POSTGRES (bukan D1)
Tujuan: semua 16.872 URL blog masuk antrian indexing **satu kali** tanpa scan D1 berat.
1. Hitung yang belum ada: bandingkan `SELECT url FROM pending_indexing` (D1, 17 rb baris — murah dengan index) vs `SELECT slug FROM coid.posts_meta` (PG).
2. Buat sisanya via **endpoint existing** `GET /api/cron/index-cascade?token=$TOKEN&count=200&dry=1` (`handleIndexCascade:8405`; dry-run dulu, baca output, baru eksekusi bertahap). JANGAN tulis SQL INSERT manual ke D1 dari laptop — pakai endpoint agar status/source konsisten.
3. **Acceptance:** `SELECT status, COUNT(*) FROM pending_indexing GROUP BY status` menunjukkan pending naik ≈ jumlah URL blog live (±16,8 rb) dan **turun terus** setiap hari (drain rate ≈ IndexNow 2.400/hari + GSC 200/hari). Jangan panik kalau backlog butuh ±1 minggu — itu desain (quota-controlled).
4. **Rollback:** tidak ada (menambah antrian, bukan menghapus). Kalau salah satu jalur error key/429 → pause cron-nya via `cron_settings.enabled=0`, jangan hapus baris.

### T1.2 (4.2) IndexNow key sehat
`curl -s "https://beriklan.co.id/api/cron/indexnow?token=$TOKEN&count=5"` → `{"ok":true,"submitted":>0,"failed":0}`; kunci terverifikasi (`https://beriklan.co.id/<INDEXNOW_KEY>.txt` = 200). Acceptance: 3 hari berturut `failed=0`.

### T1.3 (4.3) Growth loop menghasilkan entri baru
Setelah T0 (deploy guard) beres: pantau `growth_log`:
```bash
npx wrangler d1 execute beriklan-seo --remote --command "SELECT action, COUNT(*), MAX(created_at) FROM growth_log GROUP BY action"
```
**Acceptance:** `ctr-fix`/`enrich`/`gsc-loop` bertambah **tiap hari** selama 7 hari (thresholds sudah diturunkan di 4.0d). Kalau 0 kandidat lagi → cek secret `GSC_SITE_URL` (harus property yang datanya kaya: `sc-domain:beriklan.co.id`; cross-check 5 konsumennya — pola `env.GSC_SITE_URL || fallback` sudah aman) SEBELUM mengubah threshold lagi.

### T1.4 (4.4) Re-inspeksi 20 artikel baru
Ambil 20 slug `posts_meta ORDER BY iso_date DESC LIMIT 20` → jalankan `handleIndexVerify` (endpoint cron existing, `count=20`). **Acceptance (≤7 hari setelah terbit):** tidak ada lagi `"URL is unknown to Google"` untuk 20 slug itu; simpan JSON respons.

**Exit Fase 4:** 4 angka di atas tercatat di `TASKTRACKER-COID.md` + GSC 28-hari clicks naik vs baseline 159 (diukur saat T7.4 laporan mingguan).

---

## §T2. BUG (temuan audit 27 Sep) — Update growth TIDAK menulis ulang R2 → 🔒 GERBANG-DEPLOY

**Masalah:** `handleGrowthFreshness:8315` (`UPDATE posts_content SET content=...` ~line 8390), `handleGrowthCtrFix:8226` (rewrite title), `handleGrowthEnrich:8118`, `handleSnippetOptimizer:7127` menulis **hanya ke D1**. Objek R2 `coid/blog/<slug>.json` jadi basi. Hari ini tak terlihat (D1 menang di dual-read), tapi **setelah T7.5 menghapus `posts_content` dari D1, semua update 2026 hilang permanen** dan fallback R2 menyajikan versi lama.

**Fix (1 helper + 4 call-site):**
1. Tambah helper tepat setelah `_renderBlogFromR2` (line ~15271):
```js
// T2: sinkronkan 1 post ke R2 setelah growth-update (payload shape identik dengan /api/admin/r2/backfill)
async function _syncPostToR2(slug, env) {
  if (!env.QUEUE) return 'skipped';
  try {
    const meta = await env.DB.prepare("SELECT slug,title,excerpt,service,city,category,iso_date,readTime,tags,featured FROM posts_meta WHERE slug=?").bind(slug).first();
    const cont = await env.DB.prepare("SELECT content FROM posts_content WHERE slug=?").bind(slug).first();
    if (!meta || !cont) return 'missing';
    const payload = { slug: meta.slug, title: meta.title || "", content: cont.content || "", excerpt: meta.excerpt || "",
      meta: { service: meta.service || "", city: meta.city || "", category: meta.category || "", iso_date: meta.iso_date || "", readTime: meta.readTime || "", tags: meta.tags ? (typeof meta.tags === "string" ? JSON.parse(meta.tags) : meta.tags) : [], featured: !!meta.featured },
      synced_at: new Date().toISOString() };
    await env.QUEUE.put(`coid/blog/${slug}.json`, JSON.stringify(payload), { httpMetadata: { contentType: "application/json" }, customMetadata: { domain: "coid", slug, version: "3.0" } });
    return 'ok';
  } catch { return 'fail'; }
}
```
2. Panggil `await _syncPostToR2(slug, env)` **setelah** setiap UPDATE sukses di 4 handler di atas (freshness: setelah `UPDATE posts_content`; ctr-fix/enrich/snippet: setelah UPDATE title/meta terkait). Sertakan hasilnya ke log entry growth (`r2_sync: 'ok'|'fail'|...`) tanpa menggagalkan request kalau gagal.
3. (Opsional, direkomendasikan) rekonsiliasi harian: blok time-gate `h===5` yang memilih 20 slug dengan `posts_meta.refreshed_at`/`iso_date` terbaru dan membandingkan `synced_at` objek R2 → re-PUT yang beda. Simpel: mulai tanpa ini; tambah kalau audit R2-vs-D1 mingguan menemukan drift.

**Verifikasi:** trigger `growth-freshness` manual `count=1` → `curl` objek R2 slug yang di-refresh (via `GET /api/admin/r2/status?token=$TOKEN&slug=...` bila ada, atau `wrangler r2 object get idberiklan/coid/blog/<slug>.json --file -`) → `synced_at` baru + callout "Update 2026" ada di `content`. **Rollback:** restore `.bak` + rollback version.

**Catat hasil di baris baru `TASKTRACKER-COID.md` Fase 3: "3.9 R2 write-back growth updates ✅/⬜".**

---

## §T3. TOOL BARU — Winner Keyword Engine (target: winning keyword di SEMUA industri) → 🔒 GERBANG-DEPLOY

**Filosofi:** berhenti menebak keyword. Google sudah memberitahu query apa yang menampilkan kita (tabel `keyword_ranks`, di-sync 6-jam sekali dari GSC, `handleRankSync:7466`). Mesin ini mengubah data itu jadi aksi setiap hari.

### Desain (semua di `web/src/worker-entry.js`, pola meniru `handleGrowthGscLoop:7925`)
Endpoint baru `GET /api/cron/winner-engine?token=$TOKEN&days=28&dry=1` + time-gate **harian `h===10` UTC** di `scheduled()` (bukan slot cron baru).

Logika (SQL-friendly, semua tabel D1 existing — tidak ada tabel baru):
1. **Candidate query** = `keyword_ranks` 28 hari terakhir, `GROUP BY query`:
   `SUM(impressions) ≥ 30` AND `AVG(position) BETWEEN 4 AND 25` AND `SUM(clicks) ≥ 0`. (Threshold rendah dulu — pelajaran 4.0d: data tipis; naikkan setelah 2 minggu.)
2. **Klasifikasi tiap query:**
   a. `pos 4–10` + punya halaman → **aksi TITLE-REWRITE**: push slug ke jalur `ctr-fix` existing (TIDAK usah duplikasi logika — cukup INSERT ke antrian yang dibaca `handleGrowthCtrFix`, atau panggil internal function-nya).
   b. `pos 11–25` + punya halaman → **aksi ENRICH**: lewat `handleGrowthEnrich` existing (cooldown-nya menghormati duplikat).
   c. `pos > 15` ATAU tanpa halaman relevan (`NOT EXISTS posts_meta` yang slug/title-nya contain kata kunci) → **aksi NEW-ARTICLE**: `INSERT OR IGNORE INTO keyword_queue (id,keyword,keyword_normalized,source,seed,discovered_at,status,service,city,priority_score,intent) VALUES ('win-<hash>', q, lower(q), 'winner-engine', 0, datetime('now'), 'pending', <service terbaik dari rank rows>, <city atau NULL>, 85, 'commercial')` — kolom identik dengan insert di `worker-entry.js:8014`; priority 85 supaya menang atas antrian generik (rebalance 03:00 UTC tidak menurunkan di bawah 80 untuk source `winner-engine` — verifikasi `handlePriorityRebalance:9809` tidak me-resetnya; kalau me-reset, tambahkan pengecualian `source IN ('winner-engine','gsc-impression')`).
3. **Laporan mingguan** (time-gate `dow===3 && h===10`): tabel TOP-50 (query, imp, clicks, pos, aksi yang diambil minggu ini) → `sendEmailViaResend(env, OWNER_EMAIL, "[Beriklan] Winner Keywords mingguan", html, 'winner-weekly-'+Date.now())`.OWNER email: `aramadhi92@gmail.com` (sudah dipakai self-heal; jadikan konstanta `OWNER_EMAIL` di file, jangan hardcode ganda).
4. Setiap aksi dicatat `growthLogInsert(env,{action:'winner-<rewrite|enrich|new>', ...})` supaya terlihat di `growth_log` dan dashboard.

### Acceptance (ukur, jangan klaim)
- Minggu 1 (mode dry dulu 2 hari → lihat daftar kandidat, baru live): ≥10 aksi tercatat di `growth_log` `action LIKE 'winner-%'`.
- Distribusi industri: minimal 4 industri berbeda muncul di TOP-50 mingguan pertama (kalau menumpuk di 1 industri, turunkan ambang impresi per grup: `PARTITION` manual per `service`).
- Email mingguan diterima (cek `email_queue status='sent'`).
**Rollback:** `UPDATE cron_settings SET enabled=0 WHERE name='winner-engine'` (_daftar-kan row cron_settings-nya saat implement_ ) + rollback version.

---

## §T4. TOOL BARU — Industry Wave Runner (Fase 6: ekspansi kontraktor → toko bangunan → tekstil → perumahan)

**Bahan baku terverifikasi 27 Sep:** `web/src/data/industry-keywords.json` = **list 2.291 item** `{keyword,slug,industri,sub_niche,service,formula,intent,score,tier}` — belum pernah di-import. `web/src/data/clusters.json` = dict 10 service × cluster — belum terpakai. Detail aturan: `INDUSTRY-EXPANSION.md` (WAJIB baca §3,5,6,7,8 sebelum mulai).

### Urutan task
1. **6.1 Validasi frasa** — script lokal `scripts/validate_suggest.py` (baru): untuk tiap ~300 frasa teratas wave-1 (industri=kontraktor), panggil `https://suggestqueries.google.com/complete/search?client=firefox&hl=id&q=<frasa>`; simpan `industry-keywords.suggest-validation.json` (frasa, in_suggest: bool, n_suggestions). Frasa tanpa suggest → tandai `weak`. **Acceptance:** file validasi ada; ≥70% frasa wave-1 lolos (kalau <70%, corek daftar dan lapor user).
2. **6.3 Koreksi intent** — distribusi saat ini didominasi informational (lihat §1.2 INDUSTRY-EXPANSION: 3 kelemahan). Rule-based lokal: frasa mengandung `jasa|harga|biaya| murah|terdekat|untuk` → `commercial/transactional`. **Acceptance:** cetak distribusi; ≥40% commercial/transactional per wave.
3. **6.2 Import ke antrian** — via endpoint EXISTING `POST /api/admin/keywords/import?token=$TOKEN&source=industry-wave1` (`handleAdminKeywordsImport:1496`; menerima `{keywords:[{keyword,service,city,intent,priority}]}`, dedup otomatis). Import HANYA wave-1 (kontraktor) dulu, ±400–700 keyword dengan priority 70–85, BUKAN 2.291 sekaligus. (Catatan: target ideal dokumen lama "import ke Postgres" — untuk operasional publish harian, D1 `keyword_queue` tetap jalur resmi; POST replika ke `coid.keyword_queue` terjadi via sinkronisasi Fase 2 — jangan bikin jalur kedua.) **Acceptance:** `SELECT source, COUNT(*) FROM keyword_queue WHERE source='industry-wave1' GROUP BY status` naik sesuai jumlah; 0 duplikat (endpoint menjamin).
4. **Generate draft wave-1 (lokal, BUKAN worker)** — pakai `scripts/seo/bulk_generate.py` yang sudah ada; aktifkan filter `source='industry-wave1'` agar yang digenerate hanya antrian wave ini; target buffer: **tambah 300–500 draft berkualitas** (bukan 400/hari). Model: Groq via pipeline yang sama.
5. **6.9 quality gate** — script baru `scripts/quality-gate.mjs` (VPS-boleh, lokal-boleh): tolak draft bila < 900 kata ATAU tanpa FAQ ≥3 Q&A ATAU tanpa minimal 1 angka/kutipan realistis ATAU duplikat >85% dengan draft lain (jaccard 3-gram > 0.85) ATAU tanpa internal link ≥3 ke cluster yang sama (`clusters.json` → pilih 1 pillar + 8–12 supporting per wave, 6.4). Draft gagal → `generated_drafts.status='draft-gated'` + kolom alasan di JSON internal script (JANGAN commit yang gagal). **Acceptance:** laporan `gate-report-wave1.json` dengan jumlah lolos/tolak + alasan.
6. **Publish & ukur (6.7 gerbang 45 hari):** wave-1 terbit natural lewat cap 15/hari. Setelah 45 hari: minimal **1 URL wave-1 dengan impressions>100 ATAU ≥3 klik** → wave-2 (toko bangunan) boleh diulang dari langkah 1. Kalau gagal → STOP, lapor, jangan wave-2. **Rollback batch:** `UPDATE generated_drafts SET status='draft' WHERE ...` (unpublish = stop commit, bukan hapus).

**Batas keras:** semua artikel baru lewat `/blog/<slug>/` saja; bahasa Indonesia formal sesuai `COPY-BIBLE.md`/AGENTS.md §4; nomor WA CTA tetap `62811919328`.

---

## §T5. TOOL BARU — LLM Visibility Suite (Fase 7: terindex & dikutip di ChatGPT/Gemini/Perplexity/Claude, keyless)

### T5.1 AI Crawler Tracker (ukur dulu, baru klaim) → 🔒 GERBANG-DEPLOY
- Tabel baru D1 (tambah ke array migrasi `worker-entry.js` ~line 3785, pola `CREATE TABLE IF NOT EXISTS` yang sama — auto-apply via self-heal `/api/admin/migrate` 00:00 UTC):
```sql
CREATE TABLE IF NOT EXISTS ai_crawler_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  bot TEXT NOT NULL, path TEXT NOT NULL, slug TEXT,
  ua TEXT, day TEXT NOT NULL, created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_ai_crawler_day_bot ON ai_crawler_log(day, bot);
```
- Instrumentasi di fetch handler awal (setelah routing blog/asset, SEBELUM render): match UA terhadap `GPTBot|OAI-SearchBot|ChatGPT-User|ClaudeBot|Claude-SearchBot|PerplexityBot|Perplexity-User|Google-Extended|CCBot|Bytespider|Applebot-Extended|meta-externalagent` → extract bot pertama + slug (regex `/blog/([^/]+)/`) → **catat maksimal 1 baris per (bot,day,slug)** (cek row existing hari itu untuk hemat write — tabel kecil). Jangan blocking response; `ctx.waitUntil`.
- Aggregasi: tambah 1 seksi ke admin dashboard existing (`handleAdminDashboard:4370` — render tabel sederhana, BUKAN redesign UI) + field `ai_crawlers_7d` di health email (T7.1).
- **Acceptance:** setelah 7 hari, `SELECT bot, COUNT(*) FROM ai_crawler_log WHERE day >= date('now','-7 days') GROUP BY bot` non-kosong minimal 1 bot (biasanya GPTBot/Perplexity datang kalau robots mengizinkan — sudah dicek allow, §13 audit).

### T5.2 llms.txt & llms-full.txt per industri (7.4) → 🔒 GERBANG-DEPLOY (bisa digabung deploy T5.1)
`handleLlmsTxt:5060` saat ini hanya 100 artikel terbaru. Ubah (patch kecil, struktur sama):
1. Tambah blok `## Panduan per Industri` — daftar manual per wave: kontraktor, toko bangunan/material, tekstil/konveksi/garmen, perumahan + link 5 artikel terbaik per industri (`posts_meta WHERE service LIKE ... ORDER BY iso_date DESC LIMIT 5`, fallback: query LIKE `%kontraktor%` di title/slug).
2. Tambah baris `**Last-Updated:** <tanggal ISO>` (di-generate runtime) dan link `news.xml` + `sitemap-blog.xml`.
3. `handleLlmsFullTxt:5135`: naikkan 100 → 300 artikel + kolom `service` + `city` (sudah ada polanya di file), cache tetap 6 jam.
4. **Per-wave otomatiskan:** fungsi pembentuk blok industri membaca `cron_settings` row baru `industry_wave_state` (`cron` = `'kontraktor,toko-bangunan'`) supaya wave berikutnya tidak perlu edit kode. (Opsional tapi murah.)
- **Acceptance:** `curl -s https://beriklan.co.id/llms.txt | grep -c "kontraktor"` > 0 setelah wave-1 live; `Last-Updated` = hari ini; ukuran llms-full naik tapi < 1 MB.

### T5.3 Schema entitas (7.5)
- Di `Layout.astro`/generator artikel: LARANG sentuh Layout (UI). Yang boleh: JSON-LD per artikel di `[slug].astro` build-time dan/atau yang di-render worker — tambah `about`/`mentions` (ItemList dari `service`+`city`+`tags`), dan `sameAs` (profil sosial agency) di Organization. Verifikasi: Rich Results Test / `curl /blog/<x>/ | python3 -c "import sys,re,json; ..."` extract JSON-LD → tidak error. **Acceptance:** 1 sampel per 3 tipe halaman lolos validator.
- FAQ per artikel: `scripts/inject_paa.py` sudah ada — jalankan untuk artikel wave-1 SEBELUM publish (integrasikan ke quality gate T4.5: tanpa FAQ → ditolak).

### T5.4 SearXNG keyless probe (7.1–7.3, 7.6) — jalan di VPS, BUKAN worker
- `docker run -d --name searxng -p 127.0.0.1:8888:8080 searxng/searxng`; aktifkan `formats: [html, json]` di `settings.yml`; **verifikasi** `curl -s "http://127.0.0.1:8888/search?format=json&q=ujian" | head -c 200` ada `results`. (RAM VPS sempit 404 MB free — bila searxng >200 MB, swap-kan atau tunda; laporkan dulu.)
- Job probe harian (extend app Coolify `seo-pipeline`, folder `app/jobs/geo-monitor` SUDAH ADA — modifikasi, jangan bikin service baru): ≤200 query/hari dari daftar `winner-engine` TOP + 20 query komersial inti ("jasa iklan facebook bandung", dst), catat apakah `beriklan.co.id` muncul di hasil & posisi → tabel `shared.geo_mentions` (sudah ada di PG). Status pakai `unknown` bila engine tidak mengembalikan hasil sama sekali (bukan `absent`) — spec 7.3.
- Laporan mingguan tabel tren 7-hari (7.6) → tambahkan ke email mingguan T7.1.
- **Acceptance:** 7 hari berturut baris `geo_mentions` bertambah; 0 pemblokiran permanen engine (rotasi delay antar query ≥ 2 detik, jitter).

---

## §T6. Freshness at Scale ("selalu update") → 🔒 GERBANG-DEPLOY (gabungkan dengan T2)

Sekarang: 2 artikel/minggu (`dow===1 && h===2`). Target: semua artikel **berimpresi** tetap segar.
1. Ubah kandidat `handleGrowthFreshness:8315`: tetap urut `imps DESC`, tapi jalankan **harian** time-gate `h===4` dengan `count=2` (≈60/bulan) + perluas jendela: `ageDays` default 90 → ambil juga artikel `imps=0` yang umurnya 120–365 hari bila kandidat berimpresi < 2 (biaya AI kecil, cegah halaman zombie).
2. WAJIB digabung T2 (write-back R2) — kalau tidak, jangan jalankan sama sekali.
3. `news.xml` (`handleNewsSitemap:14611`): artikel yang di-refresh TIDAK mengubah `iso_date` (jujur — jangan memalsukan tanggal terbit, itu pelanggaran pakem copywriting & Google). Yang boleh: pastikan callout "Update <tahun>" terlihat di konten (sudah). Jangan naikkan `lastmod` blog sitemap untuk refresh kecuali Konten bertambah >30% (cek `posts_meta.refreshed_at` — sudah dipakai sitemap bila memang ada kolomnya). **Decision:** tetap konservatif — freshness = konten tambah, bukan tanggal ganti.
- **Acceptance:** `growth_log action='freshness'` ≥ 50/bulan; `SELECT COUNT(*) FROM posts_meta WHERE refreshed_at >= date('now','-30 days')` naik mingguan.

---

## §T7. Fase 5 (gerbang Q4) + Fase 8 (monitoring & serah terima)

### T7.5 — Trim D1 (JANGAN SENTUH TANPA "YA" TERTULIS USER, Q4)
Prasyarat keras: T0b.1-3 ✅ + T2 ✅ + 7 hari R2 stabil (health email tidak melaporkan anomali `X-Source`) + backup baru via `/api/admin/backup` existing + hitung 3-arah (D1 = PG = sitemap live, selisih 0).
Eksekusi bertahap (masing-masing tahap jeda ≥3 hari + verifikasi situs): (1) `keyword_queue` status `published`/`rejected` lama → pindah ke PG dulu, baru DELETE; (2) prune `pending_indexing` status `indexed`/`gsc_submitted` lama; (3) `growth_log`/`keyword_ranks` > 90 hari → ke PG, DELETE; (4) PALING AKHIR: `posts_content` D1 — setelah 14 hari dual-read tanpa satu pun `X-Source: d1` untuk konten (monitor header). **Aturan: tidak pernah `DROP TABLE`; selalu DELETE bertahap ≤5.000 baris/query dengan SELECT count konfirmasi sebelum & sesudah.**

### T7.8 — Monitoring & serah terima (Fase 8)
1. **8.1 Health email lebih kaya** (blok self-heal `h===0`, ~line 810-870): tambah field `d1_rows_read_24h` (dari `d1 insights`? TIDAK bisa dari worker — gunakan proksi: total `SELECT COUNT(*) cron_runs WHERE started_at>-24h AND status='failed'` + kuota-check ringan; cukup tambah: published vs cap, pending_indexing (sudah), soft-404 probe lokal, R2-vs-posts_meta count (`/api/admin/r2/status` sudah ada — panggil internal), ai_crawler_7d, winner aksi).
2. **8.2 Auto-pause publish:** di `sync-posts`, sebelum publish: `if (approxRowsReadHariIni > 3_000_000) → skip + label 'AUTO-PAUSED: D1 budget'`. Proksi rows-read: jumlahkan `rowsRead` dari `D1 result.meta` setiap query (`meta.rows_read` tersedia di binding D1 — akumulasi di global per-invocation dan tulis ke `cron_settings.d1_read_meter_<date>`).
3. **8.3 Probe eksternal 5 menit:** repo lama `00-deploy.yml.disabled` tidak dipakai. Solusi paling murah: workflow GitHub Actions `cron: */5` (di repo privat ini, hanya `curl` + bandingkan) ATAU UptimeRobot free (manual, catat di docs). Alarm: `/` != 200, `/blog/<slug-d1-only>/` != 200, `sitemap-blog.xml` != 200, atau **soft-404 terdeteksi** (respons `/blog/slug-tidak-ada-<random>/` harus 404 — kalau 200 = desync → alarm + dokumen `DEPLOY_OPERATIONS.md` §ASSET DESYNC). Kirim alert ke email via endpoint internal `/api/test-alert` (sudah ada `handleTestAlert:2705`) — GitHub Actions tinggal `curl "$WEBHOOK"`. Keputusan alat: **GitHub Actions cron** (gratis, repo sudah ada workflows folder). **Butuh izin user untuk enable repo Actions + menyimpan token di secrets — tandai GERBANG.**
4. **8.5/8.6** Update `AGENTS.md` + `DEPLOY_OPERATIONS.md` dengan: arsitektur R2+PG+Worker, fakta cron 1-slot time-gate, larangan root-kanonik (SOP 0.2 di atas), dan `arsip/TASKTRACKER-MIGRATION-VPS.md` banner superseded (sudah ada, verifikasi saja).

---

## §9. URUTAN EKSEKUSI + GRAFIK DEPENDENSI

```
T0 (deploy guard 1.16) ─┬─> T0b.1 ─┐
                        ├─> T0b.2 ─┼─> [GERBANG RUNNING WELL] ─> T7.5 (izin Q4)
                        └─> T0b.3 ─┘
T1.1..T1.4 (Fase 4) ── independent, mulai setelah T0
T2 (bug R2 write-back) ──> T6 (freshness at scale)
T3 (winner engine)     ──> bagian dari T4 & laporan T7.8.1
T4 (wave runner)       ──> T5.2 (llms per industri) ──> gerbang 45 hari ──> wave-2
T5.1 (AI crawler) ──> T5.4 (searxng) ──> T7.8 laporan
T7.8 (monitoring) ── terakhir sebelum SERAH TERIMA
```
Sesi deploy gabungan yang boleh: T2+T6 (1 deploy), T3+T5.1 (1 deploy) — kurangi jumlah gerbang deploy.
Setiap task live = minta persetujuan user satu per satu (kecuali yang sudah di-approve ber-batch oleh user di awal sesi).

## §10. DEFINITION OF DONE — co.id "running well" (salinan operasional §URUTAN EKSEKUSI butir 5)
1. Fase 0 ✅ (sudah) ; 2. publish ≤15/hari stabil ≥3 hari (T0); 3. D1 insights 1-jam < 200 rb rows tanpa error 7500; 4. `growth_log` bertambah harian (T1.3); 5. situs sehat: `/` 200, slug D1-only 200, slug palsu 404, sitemap 200, 0 soft-404, 0 asset desync (runbook §J/§K `plan.co.id.md`); 6. backup + version_id rollback tercatat valid.
**PLUS (tambahan audit 27 Sep):** T0b.1-3 terbukti + T2 terpasang → baru `.my` boleh dibuka (`MY-DUPLICATION-PLAN.md`).

## §11. PLACEHOLDER RAHASIA (jangan tulis nilai asli ke dokumen/commit apa pun)
`$TOKEN` ADMIN_TOKEN (nilai di `.env.admin`) · `$PIPELINE_TOKEN` · `$CF_API_TOKEN` (OAuth wrangler sudah login) · `$VPS_PASS`/SSH key (di `account.md`) · `GROQ_API_KEY(_2/_3)` · `INDEXNOW_KEY` · `RESEND_API_KEY` · `SA_JSON` (`cool-component-*.json`, sudah gitignored).
Sebelum commit dokumen baru: `grep -nE "gsk_|cfut_|beriklan-admin-|eyJ[0-9A-Za-z_.-]{20,}" DOCS-SEO-2026-09-24/*.md ../REKAP-COID.md` → harus kosong.

<!--END-->
