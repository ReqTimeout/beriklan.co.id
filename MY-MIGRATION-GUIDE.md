# MY-MIGRATION-GUIDE.md — Panduan Replikasi Sistem SEO ke beriklan.my

> **Audience:** coding agent yang akan melanjutkan migrasi ke `beriklan.my`.
> **Status:** `beriklan.co.id` Fase 0–3 selesai 2026-09-25 06:10 UTC. `.my` siap dimulai.
> **Acuan utama:** `DOCS-SEO-2026-09-24/plan.my.md` (rencana 494 baris, lebih detail per fase).
>
> Dokumen ini = **HOW** (pelajaran co.id yang sudah dibuktikan). `plan.my.md` = **WHAT** (per fase).

---

## 0. STATUS SEKARANG (2026-09-25 06:10 UTC)

### ✅ Sudah selesai di co.id (reusable untuk .my)
| # | Task | Worker version | Pelajaran |
|---|---|---|---|
| 3.1 | R2 backfill endpoint + writer | `68493827` | Parallelization concurrency=8 fit 30s CF Worker CPU |
| 3.2 | 16.819 posts ke R2 (71.7 MB) | `68493827` | 15.7 posts/s; idempotent slug overwrite |
| 3.3 | Manifest R2 | DEFER | posts_meta sudah cukup cepat untuk sitemap |
| 3.4 | Dual-read worker `R2 → D1 → static → 404` | `e890a733` | Header `X-Source: d1\|r2`; cache HIT/MISS jalan |
| 3.5 | Kill-switch `USE_R2` | bundled | `env.USE_R2 !== '0'` default ON |
| 3.7 | 50/50 slug random 200, bogus 404 | `40b5d9bc` | Cache HIT/MISS jalan normal |
| 3.8a | Cache query dashboard (5 hit = 0 row reads) | `56799ee8` | Cache 1 jam di `cron_settings.value` |
| 3.8b | Token rotation (kurangi mystery queries ~1.5M rows/day) | `5e8a8138` | External callers pakai token lama bocor |
| 3.8c | Refactor `${env.ADMIN_TOKEN}` template literal | `40b5d9bc` | Next rotasi = 1 command |

### ⏸️ Yang belum di .my (sudah punya plan, tinggal eksekusi)
Lihat `plan.my.md` §B–§G.

### Resource yang sudah ada untuk .my
- **CF Worker `beriklanmy`** (10 deployment historis, terstabil `ad44986d-94ce-4425-a4ac-511e6db83cc7`).
- **D1 database `beriklan-my-seo`** (sudah di-backup 24 Sep 2026).
- **R2 bucket `myberiklan`** (binding `QUEUE`, sudah ada).
- **Pages project `beriklanmy`** (custom domain belum di-attach ke `beriklan.my`).
- **1 cron slot** (`0 * * * *`) — sudah dipakai. **TIDAK ADA** di `wrangler.jsonc` → pasang manual via API tiap deploy.
- **Repo lokal:** `/Volumes/macmini/Desktop/beriklan.my` (terpisah dari co.id).

---

## 1. PERBEDAAN KRITIS co.id vs .my (BUKAN copy-paste!)

| Aspek | co.id | .my | Konsekuensi agent |
|---|---|---|---|
| Worker name | `beriklanweb` | `beriklanmy` | wrangler.jsonc pakai name berbeda |
| D1 name | `beriklan-seo` | `beriklan-my-seo` | Setiap query pakai nama yang benar |
| D1 ID | `0e71d6e3-231f-40a1-ac6b-6defc3976efd` | **(perlu dicek via wrangler)** | Backup & restore butuh ID yang benar |
| R2 bucket | `idberiklan` | `myberiklan` | Test endpoint path berbeda |
| Cron di jsonc | 2 cron | **0 cron** | Setelah `wrangler deploy`, schedules di-reset jadi kosong → PUT manual |
| `run_worker_first` | `["/*"]` (semua path) | **20 path eksplisit** (perlu diverifikasi) | Route/halaman baru **wajib** didaftarkan |
| Bahasa | Indonesia | Inggris (`lang="en"`) | Riset keyword `hl=en&gl=my` |
| URL blog live | 16.872 | 1.337 | Static-first masih layak |
| Konten | 16.819 posts (71.7 MB) | 6.060 entri / 32.5 MB | 4.723 belum jadi URL |
| `INDEXNOW_KEY` | ada (default benar) | **TIDAK ADA** → fallback ke co.id (BUG) | Set secret sebelum deploy |
| `GSC_SITE_URL` | salah (`www`) | **TIDAK ADA** → default kode benar | Jangan "memperbaiki" |
| `GROQ_API_KEY` | ada (3 key rotasi) | **TIDAK ADA** | Tambah ≥1 key |
| Email pipeline | aktif (Resend 100/hari) | **DIMATIKAN** | Jangan aktifkan tanpa izin |
| Publish rate | 15/hari (post-refactor) | 40/hari (perlu turun ke 15) | `daily_publish_limit` di cron_settings |
| Posts/Indonesia | ada | **TIDAK ADA** | `category` field beda |
| WhatsApp CTA | `62811919328` | **SAMA** (14.543×) | Keputusan user: 1 pintu semua pasar |

---

## 2. ATURAN MAIN AGENT (sudah terbukti penting di co.id)

### 2.1 JANGAN sebelum dapat izin user
- ❌ Deploy worker / Pages
- ❌ Edit `wrangler.jsonc`
- ❌ Edit `src/worker-entry.js`
- ❌ Set/rotate secrets
- ❌ Update D1 schema
- ❌ Publish artikel baru ke produksi
- ❌ Kirim email campaign

**Wajib izin eksplisit dulu**, baru eksekusi. Beda dengan co.id = tidak ada fallback "kami sudah pernah".

### 2.2 BACKUP sebelum edit
```bash
TS=$(date +%Y%m%d-%H%M%S)
cp web/src/worker-entry.js web/src/worker-entry.js.bak-my-${TS}
cp web/wrangler.jsonc web/wrangler.jsonc.bak-my-${TS}
```
Selalu `.bak-my-<ts>` (bukan `.bak-<ts>`) supaya tidak konflik dengan backup co.id.

### 2.3 Catat `version_id` sebelum perubahan live
```bash
npx wrangler deployments list 2>&1 | grep -E "Version|ad44986" | head -5
# Simpan version_id stabil untuk rollback
```

### 2.4 Build gagal = STOP, tidak deploy
- Lihat error, fix code, rebuild, baru deploy.
- Tidak ada "perbaiki maju" saat live rusak.

### 2.5 Produksi rusak = rollback, bukan fix
```bash
cd web && npx wrangler rollback <version-id>
```

### 2.6 Mode kerja step-by-step
1. User kasih perintah besar
2. Agent **pilih sendiri & eksekusi** (tidak tanya A/B/C)
3. Lapor hasil + next step
4. Lanjut

**Kecuali:** keputusan strategis besar (budget, delete data, ganti domain) → tanya dengan rekomendasi + alasan.

---

## 3. QUICK-START CHECKLIST (urutan eksekusi yang sudah terbukti)

### Step 0: Baseline & backup (30 menit)
```bash
cd /Volumes/macmini/Desktop/beriklan.my/web

# 1. Backup D1 .my (sudah pernah, tetap ulangi sebelum eksekusi)
ts=$(date +%Y%m%d)
mkdir -p ../backup
npx wrangler d1 export beriklan-my-seo --remote --output "../backup/beriklan-my-seo-${ts}-preMyFase.sql"

# 2. Catat version stabil saat ini
npx wrangler deployments list 2>&1 | tee /tmp/my-deployments-$(date +%s).log

# 3. Catat baseline metrics
echo "Posts published:" && npx wrangler d1 execute beriklan-my-seo --remote --command "SELECT COUNT(*) FROM posts_meta" 2>&1 | tail -5
echo "Drafts pending:"  && npx wrangler d1 execute beriklan-my-seo --remote --command "SELECT COUNT(*) FROM generated_drafts WHERE status='draft'" 2>&1 | tail -5
echo "Cron settings:"   && npx wrangler d1 execute beriklan-my-seo --remote --command "SELECT name, cron, enabled FROM cron_settings" 2>&1 | tail -30

# 4. Test 5 endpoint publik
for p in "/" "/blog/" "/tiktok-live-viewers/" "/sitemap-blog.xml" "/data/posts-index.json"; do
  curl -s -o /dev/null -w "$p → %{http_code}\n" "https://beriklan.my$p"
done
```

**Lock-in baseline:**
- posts_meta count: ______
- generated_drafts pending: ______
- sitemap-blog URLs: ______
- Worker version stabil: ______

### Step 1: Cek setup (read-only, tidak ada perubahan)
```bash
# Cek secrets yang sudah ada
npx wrangler secret list

# Cek cron schedules saat ini (perlu CF API token, mungkin belum ada)
curl -s -X GET "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/workers/scripts/beriklanmy/schedules" \
  -H "Authorization: Bearer $CF_API_TOKEN" | python3 -m json.tool

# Cek D1 indexes
npx wrangler d1 execute beriklan-my-seo --remote --command \
  "SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND tbl_name LIKE 'posts%'"
```

**Goal:** tahu state sekarang sebelum sentuh apapun.

### Step 2: Secrets yang WAJIB di-set (rencana §B.0.5)
```bash
cd /Volumes/macmini/Desktop/beriklan.my/web

# 1. ADMIN_TOKEN — generate baru (JANGAN pakai yang sama dengan co.id)
NEW_TOKEN=$(openssl rand -hex 24)
echo "NEW token for .my: $NEW_TOKEN"
echo "ADMIN_TOKEN_MY=$NEW_TOKEN" >> /Volumes/macmini/Desktop/beriklan.co.id/.env.admin
printf '%s' "$NEW_TOKEN" | npx wrangler secret put ADMIN_TOKEN

# 2. INDEXNOW_KEY — pakai key berbeda dari co.id
#    co.id key: 2dac33f6303f4041b9ec7e2f2910ea80
#    my key (sudah dilayani): 2f22c16be9437a90ad2285a4af043e10
printf '%s' "2f22c16be9437a90ad2285a4af043e10" | npx wrangler secret put INDEXNOW_KEY

# 3. GROQ_API_KEY — tambah minimal 1 key (boleh reuse key co.id, tidak masalah)
#    Key ada di: /Volumes/macmini/Desktop/beriklan.co.id/.env.admin
printf '%s' "$GROQ_API_KEY_1" | npx wrangler secret put GROQ_API_KEY

# 4. Verify
npx wrangler secret list
```

**Verifikasi:**
- ADMIN_TOKEN test: `curl -s -o /dev/null -w "%{http_code}\n" "https://beriklan.my/api/admin/email?token=$NEW_TOKEN&tab=overview"` → 200
- INDEXNOW_KEY test: `curl -s "https://beriklan.my/api/cron/indexnow?token=$NEW_TOKEN&count=5" | head -c 300` → `"submitted": > 0`
- GROQ_API_KEY test: jalankan `growth-gsc-loop` cron manual, harusnya tidak 401

### Step 3: Refactor token hardcoded (sebelum edit apapun)
Mengikuti lesson co.id 3.8c, **WAJIB** refactor semua hardcoded `?token=beriklan-my-admin-2026` jadi `${env.ADMIN_TOKEN}` template literal di awal, BUKAN setelahnya.

```bash
cd /Volumes/macmini/Desktop/beriklan.my/web

# 1. Backup
TS=$(date +%Y%m%d-%H%M%S)
cp src/worker-entry.js src/worker-entry.js.bak-my-${TS}

# 2. Add const TOKEN = env.ADMIN_TOKEN; di awal handler
# (lokasi: setelah fakeReq definition, sekitar line 580)

# 3. Replace SEMUA cron path dengan template literal
#    Pattern: find semua `/api/cron/...?token=OLD_TOKEN` di dalam string
#    Replace jadi `/api/cron/...?token=${TOKEN}` di dalam BACKTICK (`` ` ``)
#    JANGAN pakai double-quote! Perl gotcha (co.id 3.8c):
perl -i -pe 's{"(/api/cron/[^"]+?token=)[^"]+("}{`$1\${TOKEN}`}g' src/worker-entry.js

# 4. Validate (JANGAN skip)
node -c src/worker-entry.js 2>&1 | head -20
# ATAU lebih aman:
npx wrangler deploy --dry-run --outdir=/tmp/wrangler-dry 2>&1 | tail -10
```

**Critical:** Validate syntax SEBELUM deploy. Co.id sempat downtime 1.5 jam karena broken template literal.

### Step 4: Apply fix bug yang sudah ditemukan (rencana §C.1.1–1.4)
```bash
# 1.1 Fix IndexNow fallback — jangan pakai key co.id
# Cari line: const key = env.INDEXNOW_KEY || "2dac33f6303f4041b9ec7e2f2910ea80";
# Replace jadi:
#   const key = env.INDEXNOW_KEY;
#   if (!key) return { submitted: 0, error: "INDEXNOW_KEY not set" };

# 1.2 Fix normalizePhoneForWa — prefix Malaysia `60`
# Cari function, ubah logika prefix dari `62` jadi `60` (untuk nomor visitor, BUKAN CTA)

# 1.4 Fix sitemap-tag.xml yang kosong
# Investigasi root cause: tag route getStaticPaths tidak populate
```

### Step 5: Turunkan publish rate (rencana §C.1.7)
```bash
cd /Volumes/macmini/Desktop/beriklan.my/web

# Backup cron_settings sebelum edit
npx wrangler d1 execute beriklan-my-seo --remote --command \
  "SELECT name, cron FROM cron_settings WHERE name='daily_publish_limit'"

# Update ke 15/hari
npx wrangler d1 execute beriklan-my-seo --remote --command \
  "UPDATE cron_settings SET cron='15' WHERE name='daily_publish_limit'"

# Verify
npx wrangler d1 execute beriklan-my-seo --remote --command \
  "SELECT name, cron FROM cron_settings WHERE name='daily_publish_limit'"

# Update default di kode (line 2023: let dailyLimit = 50; → 15)
```

### Step 6: Build & deploy (rencana §C.1.8)
```bash
cd /Volumes/macmini/Desktop/beriklan.my/web

# 1. Build
npm run build 2>&1 | tail -30

# 2. Verify build sukses
echo "blog_dirs=$(find dist/blog -maxdepth 1 -type d | wc -l)"
echo "total_files=$(find dist -type f | wc -l)"
echo "size=$(du -sh dist)"
# Expected: blog_dirs ≈ 1.337 (existing), total < 20.000 files

# 3. Backup before deploy
TS=$(date +%Y%m%d-%H%M%S)
cp src/worker-entry.js src/worker-entry.js.bak-my-pre-deploy-${TS}

# 4. Deploy (butuh izin user dulu)
npx wrangler deploy 2>&1 | tail -20

# 5. WAJIB: re-attach cron schedules (di-reset tiap deploy)
curl -s -X PUT "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/workers/scripts/beriklanmy/schedules" \
  -H "Authorization: Bearer $CF_API_TOKEN" -H 'Content-Type: application/json' \
  -d '[{"cron":"0 * * * *"}]'
# Verify:
curl -s -X GET "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/workers/scripts/beriklanmy/schedules" \
  -H "Authorization: Bearer $CF_API_TOKEN" | python3 -m json.tool
```

### Step 7: Verifikasi post-deploy (rencana §J runbook)
```bash
NEW_TOKEN=$(grep ADMIN_TOKEN_MY /Volumes/macmini/Desktop/beriklan.co.id/.env.admin | cut -d= -f2)

# 1. HTTP codes
for p in "/" "/blog/" "/tiktok-live-viewers/" "/sitemap-blog.xml" "/sitemap-tag.xml" \
         "/news.xml" "/data/posts-index.json"; do
  curl -s -o /dev/null -w "$p → %{http_code}\n" "https://beriklan.my$p"
done
# Expected: semua 200

# 2. Cache HIT/MISS
curl -s -D - -o /dev/null "https://beriklan.my/data/posts-index.json" | grep -i "x-cache"
sleep 2
curl -s -D - -o /dev/null "https://beriklan.my/data/posts-index.json" | grep -i "x-cache"
# Expected: MISS → HIT

# 3. Bogus slug → 404
curl -s -o /dev/null -w "%{http_code}\n" "https://beriklan.my/blog/this-slug-does-not-exist-$(date +%s)/"

# 4. Token test
echo "New token:" $(curl -s -o /dev/null -w "%{http_code}" "https://beriklan.my/api/admin/email?token=$NEW_TOKEN&tab=overview")
echo "Old token:" $(curl -s -o /dev/null -w "%{http_code}" "https://beriklan.my/api/admin/email?token=beriklan-my-admin-2026&tab=overview")
# Expected: 200 vs 401

# 5. IndexNow test
curl -s "https://beriklan.my/api/cron/indexnow?token=$NEW_TOKEN&count=5" | head -c 300
# Expected: submitted > 0, NO error key

# 6. Cron_runs check (tunggu sampai :05 menit berikutnya)
sleep 60
npx wrangler d1 execute beriklan-my-seo --remote --command \
  "SELECT cron_name, status, started_at, substr(error,1,80) FROM cron_runs WHERE started_at > '$(date -u +%Y-%m-%d)' ORDER BY id DESC LIMIT 10"
# Expected: semua crons OK, 0 error

# 7. D1 quota check
npx wrangler d1 insights beriklan-my-seo --time-period 1h --sort-by reads --limit 5 --json
# Expected: avgRowsRead < 1000/query (kalau > 5000, ada SCAN tanpa index)
```

### Step 8: Replikasi Fase 3 (R2 backfill + dual-read)
Sama persis dengan co.id 3.1–3.4, dengan perbedaan:
- R2 prefix: `my/blog/<slug>.json` (bukan `coid/blog/...`)
- R2 bucket: `myberiklan` (bukan `idberiklan`)
- D1: `beriklan-my-seo` (bukan `beriklan-seo`)
- worker-entry.js: replicate helper `_renderBlogFromR2` tapi **test 5 sample dulu** sebelum full upload
- posts_meta .my sudah ada (1.337 published) — backfill untuk sisa 4.723 entri `posts.json`

---

## 4. PELAJARAN DARI co.id (BAKED INTO THIS GUIDE)

### 4.1 D1 quota burn — JANGAN ulangi
- Free tier: **5M rows/day per ACCOUNT** (bukan per DB). Divided among 7 DB.
- Insiden 1 (Sep 2): query related-posts tanpa index → 166M rows/day → 7500 error → cron hang.
- Insiden 2 (Sep 4): `/api/admin/migrate` dipanggil 48×/hari external monitor → 745k reads/call = 5M/hari = lock tiap hari.
- **Fix pattern (WAJIB):**
  1. Setiap query baru → `EXPLAIN QUERY PLAN` dulu, hasil harus **SEARCH** bukan SCAN
  2. Cek `wrangler d1 insights <name> --time-period 1h --sort-by reads --limit 5 --json`
  3. Index untuk: `posts_meta (service, iso_date DESC)`, `posts_meta (city, iso_date DESC)`, `email_queue (status, sent_at)`
- Gotcha `wrangler d1 insights`: TIDAK ada flag `--remote`. Output field = `avgRowsRead`/`totalRowsRead`/`queryEfficiency` (bukan `rowsRead`).

### 4.2 CF Worker CPU 30s limit
- R2 backfill perlu parallelization. Concurrency=8 fit 30s untuk ~150 posts.
- Untuk bulk upload: pakai endpoint `?source=d1` paginated by slug (bukan single PUT).

### 4.3 Cron schedule reset setiap `wrangler deploy`
- Symptom: deploy sukses, tapi crons tidak firing.
- Cause: wrangler deploy sync schedules dengan `wrangler.jsonc` triggers section. Jika jsonc kosong/crons beda, schedules di-reset.
- Fix: **setelah deploy, PUT manual** schedules via API.
- Gotcha API: PUT body harus **array mentah** `[{"cron":"..."}]`, BUKAN `{"schedules":[...]}` (error 10026).
- Gotcha kedua: error 10072 = cap 5 cron/account tercapai. Untuk .my, slot sudah dipakai `beriklanweb` (2) + `beriklanmy` (1) = 3/5. Aman.

### 4.4 Template literal `${TOKEN}` gotcha
- Hanya evaluasi di dalam **backtick** (`` ` ``). Di double-quote (`"..."`) jadi literal text.
- Pattern aman:
  ```js
  const TOKEN = env.ADMIN_TOKEN; // declared ONCE
  
  // ✅ Cron paths (top-level strings)
  const path = `/api/cron/foo?token=${TOKEN}`;
  
  // ✅ HTML template (inside outer template literal)
  const html = `<a href="/admin?token=${TOKEN}">link</a>`;
  
  // ✅ String concat (when inside another template literal)
  const html2 = `<a href="/admin?token=" + TOKEN + '">link</a>`;
  ```

### 4.5 D1 `all()` return `{ results: [...] }` (plural)
- Jangan baca `.result` (singular), selalu `.results`.

### 4.6 Worker entry sebagai mirror gate
- `/api/admin/sync/posts` punya mode lean (`?mirror=0`) dan full (`?mirror=1`).
- Cron lean = refill buffer + publish + indexing (aman CPU free).
- Manual full = sync ke GitHub static mirror (berat, hanya untuk build terjadwal).

### 4.7 Mystery queries dari external callers
- Token bocor (`beriklan-admin-2026` ditemukan dipakai script eksternal yang scrape endpoint dashboard).
- Pre-rotation: 14 runs/jam query `priority_score >= 90` = 290k rows/jam.
- Post-rotation: 0 runs (token lama ditolak 401).
- **Mitigasi:**
  1. Rotasi token berkala (tiap 3-6 bulan, atau setelah insiden).
  2. Refactor jadi `${env.ADMIN_TOKEN}` (lesson 3.8c) — next rotasi = 1 command.

### 4.8 Asset desync (recurring)
- Gejala: `/` & static file 404, tapi `/data/posts-index.json`, `/blog/<slug>/`, `/api/*` = 200.
- **BUKAN** salah code/DNS.
- Fix: `cd web && npx wrangler deploy` (re-sync asset manifest). OAuth sudah login.

### 4.9 Resend quota = 100/hari (FIXED asumsi lama "500/hari")
- Hard limit. Email-send cron max 4 batch/hari @ batch=25 (atau @ batch=10 kalau perlu safety).
- Default handler skip cron kalau `daily_sent >= 100`. Reset jam 00:00 UTC.
- Untuk .my yang TIDAK kirim email (sudah di-disable), ini tidak relevan.

### 4.10 CF Worker Free tier: 50 subrequest per invocation
- Email batch > 25 + Resend call per email → kalau paralel, batch >25 bisa trigger `Too many subrequests by single Worker invocation`.
- 1.150 email dari campaign 9 co.id GAGAL PERMANEN karena batch terlalu besar.
- **Solusi untuk .my kalau nanti aktifkan email**:
  - Batch max=10 (aman untuk 5 subrequest/email × 10 = 50, at limit)
  - Atau pakai Queues service (tidak free tier)
  - Atau sequential (lambat tapi aman)

### 4.11 CF cron auto-disable setelah 3× fail + cron_settings auto-pause (2 layer safety)
- **Layer 1 (Cloudflare)**: cron expression yang fail 3× berturut-turut di-auto-disable oleh CF.
- **Layer 2 (worker code)**: handler `handleScheduled()` (line ~663) cek `cron_settings.enabled === 0` → skip. Logic ini auto-pause cron job setelah 3× gagal berturut-turut, label jadi `AUTO-PAUSED: <error>`.
- **Recovery**:
  - Layer 1: TIDAK BISA recover via `wrangler triggers deploy`. Solusi: pindahkan ke time-gate `if (m % 15 === 0)` di dalam slot cron yang masih hidup.
  - Layer 2: manual `UPDATE cron_settings SET enabled=1 WHERE name='<cron>'`. Self-heal loop (line ~794) HANYA untuk D1 lock pause, bukan app-level pause.
- **Lesson untuk .my**: SELALU pakai pattern time-gate (jangan pakai banyak slot cron). Kalau ada 1 cron disabled, semua jobs di slot itu ikut mati.

### 4.12 Audit jujur ≠ status report (anti-halusinasi)
- Cerita user 25 Sep: "are you sure .co.id done?" — padahal publish pipeline jalan, TAPI 4 issues tersembunyi (email-send cron auto-paused, pending_indexing backlog, email queue failed, growth system cold).
- **Prinsip**: jangan klaim "stabil" hanya karena cron terakhir jalan. Selalu cek:
  1. `cron_runs` terakhir per cron_name (apakah ada gap >1 jam?)
  2. `cron_settings.enabled` per cron (apakah ada yang enabled=0?)
  3. Backlog counter (pending_indexing, email_queue, keyword_queue)
  4. Self-healing jobs yang stuck (campaigns status='sending' > 24 jam, draft 'committed' > 7 hari tanpa publish)
- **Tool**: buat `audit-co-id.sh` script yang print 10 signal di atas dalam 1 call.

### 4.13 Growth thresholds untuk GSC data tipis
- www property co.id cuma ~295 rows/14 hari. Default thresholds (`growth-enrich minImp=10`, `growth-ctr-fix minImp=50`, `growth-gsc-loop minImp=20 maxQueue=10`) = 0 candidates SELALU.
- **Fix untuk data tipis**: enrich `minImp=5`, ctr-fix `minImp=5` (floor=1), gsc-loop `minImp=10 maxQueue=15`.
- `.my` GSC kemungkinan data lebih kaya (property dedicated), default mungkin works. Monitor dulu via `curl /api/cron/growth/ctr-fix?token=...&count=1` — kalau 0 candidates terus 7 hari, turunkan threshold.
- **Alternative**: query BOTH www + apex (kalau apex bisa diakses), merge hasil. Belum di-implement di co.id — catatan untuk v2.

---

## 5. CRON JOBS YANG PERLU DI .my

Berikut daftar job yang sudah jalan di co.id via time-gate di scheduled() (`0 * * * *`).
Untuk .my, **tidak boleh duplicate semua** — hanya yang relevan untuk pasar Malaysia.

| Cron | Tujuan | .my perlu? | Catatan |
|---|---|---|---|
| `hourly` (0 * * * *) | generate artikel AI (3/jam) | **TIDAK** | `.my` punya `trending-generate` yang masih aktif, jangan double |
| `email-send` (*/15) | kirim antrian email | **TIDAK** | email pipeline dimatikan di .my |
| `gsc-indexing` (0 */6) | submit sitemap + GSC | **YA** | Indexing penting untuk .my |
| `trending-generate` (30 */6) | trending dari Google Trends | **YA** | sudah aktif di .my via cron_settings |
| `lead-pipeline` (0 */6) | match lead + AI personalize | **YA** | pasar MY perlu leads juga |
| `indexnow` (15 *) | IndexNow submit | **YA** | fix bug dulu (§C.1.1) |
| `growth-gsc-loop` (tiap 6 jam) | GSC feedback loop | **YA** | ambil dari GSC `.my` |
| `growth-enrich` (harian 09 UTC) | rewrite intro + FAQ | **YA** | cek cooldown 21 hari |
| `growth-ctr-fix` (harian 09 UTC) | rewrite title/description SERP | **YA** | cek minImp=50 |
| `growth-freshness` (Senin 02 UTC) | update callout artikel >90 hari | **YA** | |
| `scrape-indonetwork` (h==6 UTC) | scrape Indonetwork | **TIDAK** | pasar Indonesia |
| `scrape-google-places` (h==7 UTC) | scrape Google Places | **OPSIONAL** | bisa untuk cari leads MY |
| `content-refresh` (bulanan) | refresh artikel lama | **YA** | |
| `snippet-optimize` (mingguan) | optimasi snippet | **YA** | |

**Quota cap:** CF Workers free = 5 cron expressions per account.
- co.id: 2 (`0 *` + `*/15`)
- .my: 1 (`0 *`)
- Total: 3 — masih punya 2 slot kosong kalau perlu tambah.

---

## 6. GSC SETUP UNTUK .my

`.my` GSC property saat ini:
- `sc-domain:beriklan.my` — service account `beriklanmy@cool-component-463913-b7.iam.gserviceaccount.com` sudah punya akses.

Verifikasi:
```bash
# Test akses (asumsi env GSC_SERVICE_ACCOUNT_JSON sudah di-set)
NEW_TOKEN=$(grep ADMIN_TOKEN_MY /Volumes/macmini/Desktop/beriklan.co.id/.env.admin | cut -d= -f2)
curl -s "https://beriklan.my/api/cron/gsc/gsc-loop?token=$NEW_TOKEN" | head -c 500
# Expected: 200 dengan data impressions (kalau 0 rows, berarti property masih baru)

# Cek secret GSC_SITE_URL
npx wrangler secret list | grep GSC
# Jangan set GSC_SITE_URL untuk .my — default kode sudah benar (sc-domain:beriklan.my)
```

---

## 7. SCHEDULED() — PATTERN TIME-GATE

Co.id pakai pattern ini di worker-entry.js line ~744:
```js
export default {
  async scheduled(event, env, ctx) {
    const TOKEN = env.ADMIN_TOKEN;
    const cron = event.cron; // "0 * * * *" atau "*/15 * * * *"
    const fakeReq = (path) => fetch(`https://beriklan.my${path}`, {
      headers: { "X-Cron-Source": "scheduled" }
    });
    
    if (cron === "0 * * * *") {
      // Hourly job
      const runs = [
        { name: "hourly", path: `/api/cron/hourly?token=${TOKEN}` },
        { name: "gsc-indexing", path: `/api/cron/gsc/indexing?token=${TOKEN}` },
        { name: "lead-pipeline", path: `/api/cron/leads/process?token=${TOKEN}&limit=100&ai=15&campaign=1` },
        // Time-gate: hanya jalan di jam tertentu
        ...(new Date().getUTCHours() % 6 === 0 ? [{ name: "growth-gsc-loop", path: `/api/cron/growth/gsc-loop?token=${TOKEN}` }] : []),
        ...(new Date().getUTCHours() === 6 ? [{ name: "scrape-indonetwork", path: `/api/cron/scrape/indonetwork?token=${TOKEN}` }] : []),
        // ...
      ];
      await Promise.all(runs.map(r => ctx.waitUntil(fakeReq(r.path).catch(console.error))));
    }
    if (cron === "*/15 * * * *") {
      // 15-min job
      await ctx.waitUntil(fakeReq(`/api/cron/email/send?token=${TOKEN}`).catch(console.error));
    }
  },
  // ...
};
```

**Untuk .my:** copy pola ini, tapi **skip job yang tidak relevan** (lihat tabel §5).
`lead-pipeline` perlu set `LEAD_SERVICE_RULES` berbeda untuk pasar MY (keyword Bahasa Inggris + nama kota MY).

---

## 8. RUNBOOK ROLLBACK .my

```bash
# Sebelum perubahan live
cd /Volumes/macmini/Desktop/beriklan.my/web
npx wrangler deployments list 2>&1 | tee /tmp/my-pre-deploy.log
# Simpan version_id stabil

# Produksi rusak
npx wrangler rollback <version-id>

# Re-attach cron (rollback TIDAK reset schedules, tapi verify)
curl -s -X PUT "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/workers/scripts/beriklanmy/schedules" \
  -H "Authorization: Bearer $CF_API_TOKEN" -H 'Content-Type: application/json' \
  -d '[{"cron":"0 * * * *"}]'

# Verify
NEW_TOKEN=$(grep ADMIN_TOKEN_MY /Volumes/macmini/Desktop/beriklan.co.id/.env.admin | cut -d= -f2)
for p in "/" "/blog/" "/sitemap-blog.xml" "/data/posts-index.json"; do
  curl -s -o /dev/null -w "$p → %{http_code}\n" "https://beriklan.my$p"
done
```

---

## 9. CHECKLIST BEFORE DECLARE DONE

### Fase 0 (Stabilisasi)
- [ ] D1 backup `.sql` tersimpan di `/Volumes/macmini/Desktop/beriklan.my/backup/`
- [ ] Baseline posts/drafts/sitemap dicatat
- [ ] Worker version stabil dicatat
- [ ] Token .my baru disimpan di `/Volumes/macmini/Desktop/beriklan.co.id/.env.admin` (format `ADMIN_TOKEN_MY=...`)

### Fase 1 (Quick wins)
- [ ] Secrets: ADMIN_TOKEN, INDEXNOW_KEY, GROQ_API_KEY ter-set
- [ ] Token lama `beriklan-my-admin-2026` ditolak (401)
- [ ] Token baru working (200)
- [ ] IndexNow test: `submitted > 0`, NO error key
- [ ] `normalizePhoneForWa` returns prefix `60` untuk nomor MY
- [ ] `sitemap-tag.xml` > 0 URL
- [ ] publish rate turun ke 15/hari
- [ ] Cron schedules terpasang (`GET /schedules` shows `0 * * * *`)
- [ ] Semua endpoint publik 200
- [ ] Bogus slug → 404
- [ ] Cache HIT/MISS jalan

### Fase 2 (Postgres VPS — optional untuk .my, hanya kalau mau replikasi penuh)
- [ ] Schema Postgres `.my` dibuat
- [ ] Backfill posts_meta + posts_content selesai
- [ ] Verify count sama dengan D1

### Fase 3 (R2 backfill + dual-read)
- [ ] Endpoint `POST /api/admin/r2/backfill` works
- [ ] Sample 5 posts uploaded ke `myberiklan/my/blog/<slug>.json`
- [ ] Full backfill 4.723 entri selesai (estimated ~5 menit)
- [ ] Worker dual-read: D1 → R2 → static → 404
- [ ] Header `X-Source: d1|r2` jalan
- [ ] USE_R2 kill-switch tested

### Fase 4 (D1 rampung)
- [ ] Tidak ada artikel yang baru di-publish 30 hari terakhir
- [ ] Free up quota

---

## 10. QUICK REFERENCE COMMANDS

```bash
# Set environment
export CF_ACCOUNT_ID=766dfffa7e5dcd8ba246ebfa60bc10ba
export CF_API_TOKEN=cfut_wUtY…
# Note: token ini zone-scoped ke co.id. Untuk .my perlu token berbeda.
# Saran: pakai Global API token dengan scope Workers Scripts:Edit.

# Common
cd /Volumes/macmini/Desktop/beriklan.my/web

# Tail logs
npx wrangler tail beriklanmy --format json

# Deploy
npx wrangler deploy

# Re-attach cron (WAJIB setelah deploy)
curl -s -X PUT "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/workers/scripts/beriklanmy/schedules" \
  -H "Authorization: Bearer $CF_API_TOKEN" -H 'Content-Type: application/json' \
  -d '[{"cron":"0 * * * *"}]'

# Manual cron triggers
NEW_TOKEN=$(grep ADMIN_TOKEN_MY /Volumes/macmini/Desktop/beriklan.co.id/.env.admin | cut -d= -f2)
curl -s "https://beriklan.my/api/cron/hourly?token=$NEW_TOKEN" | head -c 300
curl -s "https://beriklan.my/api/cron/gsc/indexing?token=$NEW_TOKEN" | head -c 300
curl -s "https://beriklan.my/api/cron/indexnow?token=$NEW_TOKEN&count=10" | head -c 300

# D1 inspect
npx wrangler d1 execute beriklan-my-seo --remote --command "SELECT name FROM sqlite_master WHERE type='table'"
npx wrangler d1 insights beriklan-my-seo --time-period 1h --sort-by reads --limit 10 --json

# Worker versions
npx wrangler deployments list

# D1 backup
npx wrangler d1 export beriklan-my-seo --remote --output "../backup/beriklan-my-seo-$(date +%Y%m%d).sql"
```

---

## 11. RELATED DOCS

- `DOCS-SEO-2026-09-24/plan.my.md` — **rencana lengkap per fase** (494 baris).
- `DOCS-SEO-2026-09-24/SEO-AUDIT-2026-09-24.md` — audit 24 Sep, sumber `version_id` stabil & perbedaan.
- `DOCS-SEO-2026-09-24/TASKTRACKER-SEO-MASTER.md` — tracker eksekusi, update baris 3.6/4.x untuk .my.
- `DOCS-SEO-2026-09-24/plan.co.id.md` — referensi pola co.id (yang sudah terbukti).
- `AGENTS.md` §AGENTS global rules (apply untuk .my juga).
- `DEPLOY_OPERATIONS.md` — gotcha Cloudflare deployment.

---

**Maintainer:** Beriklan Digital Agency + Codex AI
**Last updated:** 2026-09-25 06:10 UTC (co.id Fase 3 done)
**Versi:** 1.0
