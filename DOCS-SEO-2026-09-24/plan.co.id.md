# plan.co.id.md — Rencana Implementasi beriklan.co.id

> ## ✅ DOMAIN AKTIF — tapi tunggu aba-aba user (keputusan 24 Sep 2026)
> co.id dikerjakan **lebih dulu**; `.my` ditunda (lihat banner di `plan.my.md`).
> **Status sekarang:** Fase 0.1/0.3/0.4 ✅ · 0.5 🔄 (tinggal revoke key lama di dashboard Groq) ·
> 0.6+ **belum boleh dijalankan** — user meminta semua dokumen clear dulu sebelum eksekusi lanjutan
> (tracker §KEPUTUSAN butir 11). Yang sudah dikerjakan bersifat backup/catatan, bukan perubahan perilaku situs.
> **Langkah pertama setelah aba-aba:** selesaikan Fase 0 co.id (0.6 → 0.8 → 0.9 → 0.11 → 0.13),
> lalu Fase 1 dimulai dari **1.1 (cap publish 600 → 15/hari)**.

> **Acuan bukti:** `SEO-AUDIT-2026-09-24.md` (semua angka di sini merujuk ke sana, tidak diulang).
> **Baca wajib sebelum Fase 1:** audit **§6.5** — generate artikel terjadi **di lokal**, Worker hanya
> refill buffer dari R2 (`publish-queue/queue_NNNNN.ndjson`) lalu publish harian. Limit publish ada di
> `cron_settings` kolom **`cron`** (`publish_daily_limit=600`, `publish_batch_size=25`).
> **Tracker eksekusi:** `TASKTRACKER-SEO-MASTER.md` — jangan eksekusi dari dokumen ini tanpa update tracker.
> **Cakupan:** backend/SEO/infrastruktur co.id. **BUKAN** perubahan visual.
> **Bahasa:** Indonesia (pakem `../COPY-BIBLE.md` untuk konten yang dihasilkan).

---

## A. Aturan main (berlaku untuk SEMUA fase)

1. **Tidak ada deploy tanpa persetujuan eksplisit user**, dan hanya jika verifikasi fase lulus.
2. **Build gagal = STOP.** Tidak boleh diakali, tidak boleh deploy.
3. **Tidak ada `DELETE` pada data artikel** (`posts_meta`, `posts_content`, `generated_drafts`, `keyword_queue`)
   sampai Fase 4 menyetujui, dan tidak pernah tanpa backup terverifikasi.
4. **Backup sebelum menulis.** File krusial disalin ke `.bak-<timestamp>`:
   ```bash
   cd /Volumes/macmini/Desktop/beriklan.co.id/web
   ts=$(date +%Y%m%d-%H%M%S)
   cp src/worker-entry.js "src/worker-entry.js.bak-$ts"
   cp wrangler.jsonc "wrangler.jsonc.bak-$ts"
   ```
5. **Catat versi stabil sebelum perubahan live:**
   ```bash
   cd /Volumes/macmini/Desktop/beriklan.co.id/web
   npx wrangler deployments list | head -20   # simpan version_id teratas = jalur mundur
   ```
6. **Produksi rusak = rollback sekarang**, bukan "perbaiki maju":
   ```bash
   npx wrangler rollback <version-id>
   ```
7. **Jangan tambah cron ke `wrangler.jsonc`.** Cap 5 slot/account sudah 2 terpakai co.id + 1 .my.
   Job baru masuk lewat time-gate di dalam slot hourly `0 * * * *`.
8. **Jangan ubah `run_worker_first: ["/*"]`** di `wrangler.jsonc` co.id.
9. **Query D1 baru wajib `EXPLAIN QUERY PLAN` → hasil harus SEARCH, bukan SCAN.**
10. **Jangan menulis rahasia ke dokumen/kode.** Pakai placeholder (§H).
11. Setiap fase punya **Exit Criteria**. Fase berikutnya tidak dimulai sebelum exit criteria fase ini tercentang
    di tracker dengan bukti output perintah (bukan klaim).

Urutan fase: **0 → 1 → 2 → 3 → 4 → 5 → 6 → 7**. Fase 0 dan 1 wajib lebih dulu; Fase 5–7 bisa paralel setelah Fase 3.

---

## B. FASE 0 — Stabilisasi & pengaman (tanpa deploy worker)

**Tujuan:** punya jalur mundur nyata sebelum apa pun diubah. Menutup temuan §9.5 (build VPS invalid)
dan §14 (rahasia bocor).

### 0.1 Backup D1 penuh
```bash
cd /Volumes/macmini/Desktop/beriklan.co.id/web
ts=$(date +%Y%m%d)
npx wrangler d1 export beriklan-seo --remote --output "../backup/beriklan-seo-$ts.sql"
ls -lh "../backup/beriklan-seo-$ts.sql"
grep -c 'INSERT INTO' "../backup/beriklan-seo-$ts.sql"
```
**Exit:** file > 0 B, jumlah `INSERT INTO` > 0, dan tercatat di tracker.

### 0.2 Hitung baseline yang akan dijaga (angka penyelamat)
```bash
cd /Volumes/macmini/Desktop/beriklan.co.id/web
for q in \
 "SELECT COUNT(*) AS posts_meta FROM posts_meta" \
 "SELECT COUNT(*) AS posts_content FROM posts_content" \
 "SELECT COUNT(*) AS drafts FROM generated_drafts" \
 "SELECT status, COUNT(*) AS n FROM keyword_queue GROUP BY status" \
 "SELECT COUNT(*) AS pending_index FROM pending_indexing"; do
  npx wrangler d1 execute beriklan-seo --remote --command "$q"
done
curl -s https://beriklan.co.id/sitemap-blog.xml | grep -c '<loc>'
```
Simpan semua angka ini di tracker sebagai **BASELINE**. Aturan: setelah migrasi apa pun,
jumlah artikel tersaji **tidak boleh kurang** dari baseline ini.

### 0.3 Rotate rahasia yang bocor
1. Groq: buat key baru di dashboard Groq → **revoke** key lama yang ada di `../plan.md`.
2. Ganti `../plan.md` supaya tidak memuat key; tambahkan ke `.gitignore` bila masih berisi catatan sensitif.
3. Admin token: pindahkan dari `wrangler.jsonc` ke secret.
   ```bash
   cd /Volumes/macmini/Desktop/beriklan.co.id/web
   printf '%s' "$ADMIN_TOKEN" | npx wrangler secret put ADMIN_TOKEN
   printf '%s' "$PIPELINE_TOKEN" | npx wrangler secret put PIPELINE_TOKEN
   ```
   Lalu hapus nilainya dari `wrangler.jsonc` (sisakan nama var tanpa nilai hanya jika worker membaca dari `vars`;
   lebih aman: hapus entri dan andalkan secret).
4. Sweep sebelum commit apa pun:
   ```bash
   cd /Volumes/macmini/Desktop/beriklan.co.id
   git status --porcelain
   git diff | grep -nEi 'sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|BEGIN PRIVATE KEY' || echo "diff bersih"
   git check-ignore -v cool-component-463913-b7-fa49902b181d.json
   ```

### 0.4 Perbaiki sync repo ke VPS (prasyarat build)
Kondisi sekarang: `/opt/migration/repo-coid/web/src` = **0 file**.
```bash
# dari laptop — pakai rsync resumable + verifikasi, JANGAN scp/tar biasa
cd /Volumes/macmini/Desktop/beriklan.co.id
rsync -avz --partial --progress --delete \
  --exclude 'node_modules' --exclude 'dist' --exclude '.astro' --exclude '.git' \
  --exclude 'backup' --exclude '*.bak-*' \
  web/ root@130.254.47.93:/opt/migration/repo-coid/web/
```
Verifikasi di VPS:
```bash
ssh root@130.254.47.93 'cd /opt/migration/repo-coid/web && \
  find src -type f | wc -l && ls src/pages/blog/ && wc -l src/worker-entry.js'
```
**Exit:** `find src -type f | wc -l` > 100, `src/pages/blog/[slug].astro` ada, `worker-entry.js` ±808.930 B.

### 0.5 Buktikan build Astro bisa jalan di VPS (tanpa deploy)
```bash
ssh root@130.254.47.93 'cd /opt/migration/repo-coid/web && \
  rm -rf dist node_modules/.vite .astro && \
  npm ci && npm run build 2>&1 | tail -30 && \
  echo "blog_dirs=$(find dist/blog -maxdepth 1 -type d | wc -l)" && du -sh dist'
```
**Exit:** build sukses **dan** `blog_dirs` mendekati jumlah slug yang diharapkan dari `posts.json`
(bukan 0). Kalau `npm ci` gagal karena memori/disk, hentikan dan laporkan — jangan pakai `dist` hasil rsync
sebagai "bukti build".

> **Jangan** lanjut ke Fase 2/3 kalau 0.4 atau 0.5 gagal: pabrik konten harus bisa dibangun ulang.

---

## C. FASE 1 — Hentikan pendarahan (1× deploy worker, risiko rendah)

**Tujuan:** turunkan publish ke 10–15/hari, hidupkan growth loop, hilangkan 69% beban D1,
perbaiki `news.xml`, pangkas `posts-index.json`. Semua lewat konfigurasi + patch kecil.

### 1.1 Turunkan laju publish (target user: 10–15/hari)

**Mekanisme nyata (terverifikasi — audit §6.5):** generate artikel terjadi **di lokal**, bukan di Worker.
Worker hanya *mempublish* dari antrian yang sudah jadi:

```
lokal : scripts/gen_articles.py + article_render.py (NO-LLM) → drafts/ (2.014 file)
lokal : scripts/build_publish_queue.py → drafts_patched/queue_*.ndjson (79 shard, 386.690 record)
R2    : publish-queue/queue_NNNNN.ndjson  (bucket idberiklan, binding QUEUE)
worker: /api/admin/queue/refill → buffer generated_drafts ≤ 2.000 (cursor: cron_settings.queue_cursor)
worker: cron sync-posts (lean, tiap jam) → publish batch_size/run, dibatasi daily_limit/hari → posts_meta
```

Jadi yang diatur di Fase 1.1 adalah **keran publish Worker**, bukan generator. Draft di R2 tetap menumpuk
sebagai backlog — itu aman dan memang by design.

**Nilai limit disimpan di kolom `cron`, bukan `value`.** Skema:
`cron_settings (id, name, cron, enabled, label, value)`. Kondisi sekarang:

| name | cron (sekarang) | target |
|---|---|---|
| `publish_daily_limit` | **600** | **15** |
| `publish_batch_size` | **25** | **5** |
| `queue_cursor` | `{"shard":2,"line":4951}` | **jangan disentuh** (posisi baca antrian) |

```bash
cd /Volumes/macmini/Desktop/beriklan.co.id/web
# baca dulu (bukti sebelum ubah)
npx wrangler d1 execute beriklan-seo --remote --command \
 "SELECT name, cron, enabled FROM cron_settings WHERE name IN ('publish_daily_limit','publish_batch_size','queue_cursor');"
# ubah keran publish
npx wrangler d1 execute beriklan-seo --remote --command \
 "UPDATE cron_settings SET cron='15' WHERE name='publish_daily_limit';"
npx wrangler d1 execute beriklan-seo --remote --command \
 "UPDATE cron_settings SET cron='5'  WHERE name='publish_batch_size';"
```

**Wajib ikut diubah di kode**, kalau tidak seed migrate menulis ulang `600`/`25`:
```bash
grep -n "publish_daily_limit\|publish_batch_size" src/worker-entry.js
```
- Baris **3734–3737** (seed): `VALUES ('publish_daily_limit','600',…)` dan `UPDATE … SET cron='600'` → ganti ke `'15'`;
  `publish_batch_size` `'25'` → `'5'`.
- Baris **2167/2173**, **5173/5178**, **5721/5726** (pembaca): `SELECT cron FROM cron_settings WHERE name=…`
  — biarkan, tapi pastikan **fallback constant** di sekitarnya tidak lebih besar dari 15/5.

**Jangan lakukan:**
- Jangan mengaktifkan `cron_settings.hourly` (label `AUTO-PAUSED`) atau `trending-generate`
  ("PAUSED — fokus publish R2 queue"). Generate AI di Worker memang sengaja mati; menyalakannya
  menghasilkan artikel di luar kendali kualitas lokal **dan** sudah terbukti gagal
  (`AI generation failed - no models worked`).
- Jangan mengubah tabel `settings` (`articles_per_hour=10`, `auto_generate=true`, dst.) — sisa konfigurasi
  lama yang tidak dipakai jalur R2 queue; mengubahnya tidak berpengaruh.
- Jangan reset `queue_cursor` (mengulang shard = duplikasi/lonjakan publish).

**Verifikasi:**
```bash
npx wrangler d1 execute beriklan-seo --remote --command \
 "SELECT name, cron FROM cron_settings WHERE name IN ('publish_daily_limit','publish_batch_size');"
# setelah ≥1 jam: run sync-posts harus melaporkan d1_published ≤ 5
npx wrangler d1 execute beriklan-seo --remote --command \
 "SELECT started_at, substr(output,1,120) FROM cron_runs WHERE cron_name='sync-posts' ORDER BY id DESC LIMIT 3;"
# setelah 24 jam: total terbit ≤ 15 (status cron_runs = 'ok', BUKAN 'success')
npx wrangler d1 execute beriklan-seo --remote --command \
 "SELECT COUNT(*) FROM posts_meta WHERE date(iso_date)=date('now');"
```
**Exit:** cap harian 15 · batch 5 · `queue_cursor` maju normal · 0 artikel duplikat.

### 1.2 Hidupkan growth loop (1 perintah, dampak terbesar)
```bash
cd /Volumes/macmini/Desktop/beriklan.co.id/web
printf 'sc-domain:beriklan.co.id' | npx wrangler secret put GSC_SITE_URL
npx wrangler secret list | grep GSC_SITE_URL
```
Uji tanpa deploy:
```bash
curl -s "https://beriklan.co.id/api/cron/growth/gsc-loop?token=$ADMIN_TOKEN&count=20" | head -c 600
curl -s "https://beriklan.co.id/api/cron/growth/ctr-fix?token=$ADMIN_TOKEN&minImp=50" | head -c 600
```
**Exit:** `gsc-loop` mengembalikan kandidat > 0; `ctr-fix` menemukan kandidat (bukan `candidates: 0`).

### 1.3 Pangkas ±69% baca D1 — 4 perbaikan query (angka re-verify audit §8.1/§8.1b)
Beban `pending_indexing` = 2.483.010 + 886.815 + 300.318 = **3.670.143 dari 5.360.539 rows read/24 jam (68,5%)**.

```bash
cd /Volumes/macmini/Desktop/beriklan.co.id/web
grep -n "pending_indexing\|keyword_queue WHERE status\|FROM posts_meta ORDER BY\|generated_drafts WHERE status" src/worker-entry.js
```

**Fix A — query terberat (2,48 jt rows/51 run, efficiency 0,00103).** Sekitar baris **7018–7022**:
```sql
-- SEBELUM (OR antar-status membatalkan index → SCAN)
WHERE status='pending' OR (status IN ('submitted','gsc_submitted', …))
-- SESUDAH (satu IN, tanpa OR antar-status)
WHERE status IN ('pending','submitted','gsc_submitted', …)
```

**Fix B — query #2 (886 rb rows/27 run).** Sudah `IN (…)` tapi masih SCAN karena
`url LIKE 'https://…%' OR url LIKE …` dan `ORDER BY CASE …` tidak bisa di-index.
Tambahkan kolom `host` (atau `domain`) yang di-populate saat insert, lalu:
```sql
WHERE status IN (…) AND host = 'beriklan.co.id'
  AND (gsc_submitted_at IS NULL OR gsc_submitted_at < datetime('now','-1 day'))
ORDER BY rowid ASC LIMIT 50
```
Urutan prioritas `admin-manual` dipindah ke kolom integer (`prio`) agar bisa di-index, bukan `ORDER BY CASE`.

**Fix C — `SELECT COUNT(*) FROM keyword_queue WHERE status=?`** membaca **377.883 baris untuk satu angka**
(efficiency 0,0000026). Pasang index, atau lebih baik: hitung di Postgres setelah Fase 2.

**Fix D — query tanpa `LIMIT`:** `posts_meta ORDER BY iso_date DESC` (16.341 baris/run × 35),
`generated_drafts WHERE status='committed'` (14.521 × 51), `SELECT url FROM pending_indexing` (16.684 × 18).
Efficiency-nya ≈ 1,0 → bukan query rusak, tapi **tanpa batas**. Tambahkan `LIMIT` + cache hasil per-run.

Index yang harus dibuat (dan **dimasukkan ke array migration permanen** di `worker-entry.js`):
```bash
npx wrangler d1 execute beriklan-seo --remote --command \
 "CREATE INDEX IF NOT EXISTS idx_pending_status_created ON pending_indexing(status, created_at);"
npx wrangler d1 execute beriklan-seo --remote --command \
 "CREATE INDEX IF NOT EXISTS idx_pending_status_gsc ON pending_indexing(status, gsc_submitted_at);"
npx wrangler d1 execute beriklan-seo --remote --command \
 "CREATE INDEX IF NOT EXISTS idx_keyword_queue_status ON keyword_queue(status);"
npx wrangler d1 execute beriklan-seo --remote --command \
 "CREATE INDEX IF NOT EXISTS idx_drafts_status ON generated_drafts(status);"
```
Wajib dibuktikan sebelum deploy:
```bash
npx wrangler d1 execute beriklan-seo --remote --command \
 "EXPLAIN QUERY PLAN SELECT id,url FROM pending_indexing WHERE status IN ('pending','submitted') ORDER BY rowid LIMIT 50;"
npx wrangler d1 execute beriklan-seo --remote --command \
 "EXPLAIN QUERY PLAN SELECT COUNT(*) FROM keyword_queue WHERE status='pending';"
```
**Exit:** kedua `EXPLAIN` menampilkan `SEARCH … USING INDEX` (bukan `SCAN`), dan setelah deploy
`d1 insights --time-period 1h` menunjukkan total < 200.000 rows read.

### 1.4 Perbaiki `news.xml` (10 → maksimal 1.000 URL < 48 jam)
Cari batasnya:
```bash
grep -n "news.xml\|NEWS_LIMIT\|slice(0, *10)" src/worker-entry.js | head -20
```
Ubah limit ke 1.000 **dengan filter `pubDate` ≤ 48 jam** (aturan Google News). Tanpa filter waktu,
menaikkan limit justru melanggar pedoman news sitemap.

### 1.5 Pangkas `/data/posts-index.json` (8,3 MB → < 200 KB)
- Batasi ke **24–50 entri terbaru** (sesuai kebutuhan `BlogFilter.svelte`), field minimal:
  `slug,title,excerpt,date,category,readTime`.
- Sisa daftar disediakan sebagai file ter-paginasi di R2 (Fase 3), bukan di endpoint ini.
- **Jangan** mengubah `BlogFilter.svelte` secara visual; kalau perlu perubahan komponen, tanyakan user dulu
  (pagar §A dan SOP ../AGENTS.md).

### 1.6 Perbaiki `ReferenceError: queue`
```bash
grep -n "queue" src/worker-entry.js | sed -n '1,40p'
```
Pada baris **9166** variabel dipakai di luar scope. Angkat deklarasi atau ganti nama — patch minimal,
tanpa refactor besar.

### 1.7 Deploy & verifikasi Fase 1
```bash
cd /Volumes/macmini/Desktop/beriklan.co.id/web
npm run build && npx wrangler deploy
```
Runbook verifikasi (GET ×2, jangan HEAD):
```bash
curl -s -D - -o /dev/null "https://beriklan.co.id/data/posts-index.json" | grep -i 'x-cache\|content-length'
curl -s -D - -o /dev/null "https://beriklan.co.id/data/posts-index.json" | grep -i x-cache
curl -s https://beriklan.co.id/news.xml | grep -c '<loc>'
curl -s -o /dev/null -w "home %{http_code}\n" https://beriklan.co.id/
npx wrangler d1 insights beriklan-seo --time-period 1h --sort-by reads --limit 5 --json
```
**Exit Criteria Fase 1 (semua harus benar):**
- [ ] `/` = 200, `x-cache` MISS → HIT
- [ ] `news.xml` > 10 URL (atau 10 jika memang tidak ada artikel < 48 jam — catat alasannya)
- [ ] `posts-index.json` < 200 KB
- [ ] `d1 insights` 1 jam: total < 200.000 rows read
- [ ] `growth` gsc-loop/ctr-fix mengembalikan kandidat > 0
- [ ] publish harian ≤ 15
- [ ] 0 error 500 baru di runtime log

---

## D. FASE 2 — Postgres VPS jadi source of truth (tanpa hapus D1)

**Tujuan:** memindahkan *pabrik* (antrian keyword, draft, backlog indexasi, log growth, rank)
ke Postgres VPS. D1 berhenti jadi tempat antrian besar. **Artikel belum dipindah di fase ini** —
artikel pindah di Fase 3 (R2). Fase ini tidak mengubah jalur serve, jadi risiko ke pengguna = nol.

### 2.1 Skema Postgres (idempotent)
Simpan sebagai `/opt/migration/seo-pipeline/sql/001_schema.sql` di VPS, lalu:
```bash
ssh root@130.254.47.93 'docker exec -i <POSTGRES_CONTAINER> psql -U <PG_USER> -d <PG_DB>' < sql/001_schema.sql
```
Isi skema (Postgres, bukan SQLite):
```sql
CREATE TABLE IF NOT EXISTS posts_meta (
  id            BIGSERIAL PRIMARY KEY,
  slug          TEXT NOT NULL UNIQUE,
  title         TEXT NOT NULL,
  excerpt       TEXT,
  category      TEXT,
  service       TEXT,
  city          TEXT,
  tags          TEXT,
  iso_date      TIMESTAMPTZ,
  seo_title     TEXT,
  seo_description TEXT,
  enriched_at   TIMESTAMPTZ,
  ctr_fixed_at  TIMESTAMPTZ,
  refreshed_at  TIMESTAMPTZ,
  r2_key        TEXT,
  migrated_at   TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_posts_meta_service_iso ON posts_meta(service, iso_date DESC);
CREATE INDEX IF NOT EXISTS idx_posts_meta_city_iso    ON posts_meta(city, iso_date DESC);

CREATE TABLE IF NOT EXISTS posts_content (
  slug       TEXT PRIMARY KEY REFERENCES posts_meta(slug) ON DELETE CASCADE,
  content    TEXT NOT NULL,
  faq_json   JSONB,
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS keyword_queue (
  id                  BIGSERIAL PRIMARY KEY,
  keyword             TEXT NOT NULL,
  keyword_normalized  TEXT NOT NULL UNIQUE,
  service             TEXT,
  city                TEXT,
  intent              TEXT,
  priority            INTEGER DEFAULT 0,
  status              TEXT NOT NULL DEFAULT 'pending',
  source              TEXT,
  created_at          TIMESTAMPTZ DEFAULT now(),
  published_at        TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_kw_status_priority ON keyword_queue(status, priority DESC);

CREATE TABLE IF NOT EXISTS generated_drafts (
  id         BIGSERIAL PRIMARY KEY,
  slug       TEXT,
  keyword_id BIGINT REFERENCES keyword_queue(id),
  title      TEXT,
  content    TEXT,
  status     TEXT NOT NULL DEFAULT 'draft',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS pending_indexing (
  id         BIGSERIAL PRIMARY KEY,
  url        TEXT NOT NULL,
  status     TEXT NOT NULL DEFAULT 'pending',
  channel    TEXT,
  attempts   INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now(),
  sent_at    TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_pending_status_created ON pending_indexing(status, created_at);

CREATE TABLE IF NOT EXISTS keyword_ranks (
  id BIGSERIAL PRIMARY KEY, keyword TEXT, url TEXT,
  position NUMERIC, impressions INTEGER, clicks INTEGER, ctr NUMERIC,
  captured_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS growth_log (
  id BIGSERIAL PRIMARY KEY, action TEXT, slug TEXT, keyword TEXT,
  position NUMERIC, ctr NUMERIC, impressions INTEGER,
  before_json JSONB, after_json JSONB, ai_model TEXT, error TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS geo_probes (
  id BIGSERIAL PRIMARY KEY, domain TEXT, query TEXT, engine TEXT,
  url_ranked TEXT, position INTEGER, cited BOOLEAN, snippet TEXT,
  captured_at TIMESTAMPTZ DEFAULT now()
);
```
**Exit:** semua `CREATE TABLE` tanpa error; `\dt` menampilkan **8 tabel** (posts_meta, posts_content, keyword_queue, generated_drafts, pending_indexing, keyword_ranks, growth_log, geo_probes).

### 2.2 Backfill dari D1 → Postgres (keyset, bukan OFFSET)
Lakukan dari laptop dengan `wrangler d1 execute --json`, hasil NDJSON di-rsync ke VPS, lalu `\copy`.
```bash
cd /Volumes/macmini/Desktop/beriklan.co.id/web
mkdir -p ../backup/ndjson && cd ../backup/ndjson
LAST=0
while : ; do
  npx wrangler d1 execute beriklan-seo --remote --json --command \
   "SELECT rowid AS id, slug, title, excerpt, category, service, city, tags, iso_date,
           seo_title, seo_description, enriched_at, ctr_fixed_at, refreshed_at
    FROM posts_meta WHERE rowid > $LAST ORDER BY rowid LIMIT 500" > "batch-$LAST.json"
  n=$(python3 -c "import json,sys;d=json.load(open('batch-$LAST.json'));r=d[0]['results'];print(len(r))")
  [ "$n" -eq 0 ] && break
  LAST=$(python3 -c "import json;d=json.load(open('batch-$LAST.json'));print(d[0]['results'][-1]['id'])")
  echo "last=$LAST rows=$n"
  [ "$LAST" -gt 1000000 ] && break
done
```
Ulangi pola yang sama untuk `posts_content` (join by slug), `keyword_queue`, `generated_drafts`,
`pending_indexing`, `growth_log`, `keyword_ranks` — **satu tabel satu loop**, file terpisah.
Lalu muat di VPS:
```bash
rsync -avz --partial backup/ndjson/ root@130.254.47.93:/opt/migration/backfill/coid/
ssh root@130.254.47.93 'cd /opt/migration/backfill/coid && python3 flatten_to_csv.py && \
  docker exec -i <POSTGRES_CONTAINER> psql -U <PG_USER> -d <PG_DB> -c "\copy posts_meta FROM '"'"'posts_meta.csv'"'"' CSV HEADER"'
```
> `flatten_to_csv.py` = script kecil di repo `seo-pipeline` untuk mengubah JSON wrangler → CSV.
> Kalau belum ada, **buat dulu** dan uji pada satu batch; jangan pakai `OFFSET` untuk tabel besar —
> `keyword_queue` **391.482 baris** adalah yang terbesar, jadi keyset pagination wajib di sana.
> (Catatan koreksi 24 Sep: `pending_indexing` **bukan** 3,8 jt baris — terukur **17.026**.
> Angka lama salah dan sudah dikoreksi di audit §8.2.)

### 2.3 Verifikasi hitung 3-arah (wajib sebelum lanjut)
```bash
# D1
npx wrangler d1 execute beriklan-seo --remote --command "SELECT COUNT(*) FROM posts_meta"
# Postgres
ssh root@130.254.47.93 'docker exec -i <PG_CONTAINER> psql -U <PG_USER> -d <PG_DB> -tAc "SELECT COUNT(*) FROM posts_meta"'
# Live
curl -s https://beriklan.co.id/sitemap-blog.xml | grep -c '<loc>'
```
**Exit Criteria Fase 2:**
- [ ] `posts_meta` Postgres == D1 == **16.686** (baseline terkunci 0.3; bukan 16.797 yang merupakan snapshot sitemap lama)
- [ ] `posts_content` Postgres == D1
- [ ] `keyword_queue` Postgres ≥ D1 pending (377.882)
- [ ] Tidak ada baris D1 yang dihapus/diubah pada fase ini
- [ ] Sampling 20 slug acak: judul+konten identik antara D1 dan Postgres

---

## E. FASE 3 — R2 sebagai content store + dual-read worker

**Tujuan:** jalur serve tidak lagi menyentuh D1. D1 tetap utuh sebagai cadangan.

### 3.1 Layout objek R2 (bucket `idberiklan`, binding sudah ada)
```
blog/<slug>.json          # { meta:{...}, contentHtml:"...", faq:[...], updatedAt }
manifest/posts.json       # ringkas: slug,title,date,category,service,city  (untuk sitemap & blog index)
manifest/posts-<n>.json   # paginasi 5.000 entri bila manifest > 2 MB
sitemap/blog-<n>.xml      # chunk 10.000 URL per file
```

### 3.2 Writer (jalan di VPS, bukan di worker)
Alur: `Postgres → render JSON/HTML → upload R2 → tulis r2_key + status`.
```bash
ssh root@130.254.47.93 'cd /opt/migration/seo-pipeline && \
  node scripts/r2-publish-coid.mjs --batch 200 --dry-run'
```
- `--dry-run` wajib dijalankan lebih dulu; output = jumlah objek yang **akan** ditulis.
- Upload memakai kredensial R2 (S3-compatible) yang disimpan sebagai env di container pipeline —
  **jangan** hardcode di repo.
- Idempotent: menulis ulang slug yang sama menimpa objek, tidak menduplikasi.

### 3.3 Dual-read di worker (patch minimal, ada kill-switch)
Cari jalur render blog:
```bash
cd /Volumes/macmini/Desktop/beriklan.co.id/web
grep -n "posts_content\|renderBlogPost\|X-Cache" src/worker-entry.js | head -40
```
Urutan baca yang harus dipasang:
```
1) flag USE_R2 (secret/vars) == "0"  → langsung ke langkah 3 (kill-switch)
2) R2.get(`blog/${slug}.json`)       → ada: render dari R2 (X-Cache: HIT/MISS + X-Source: r2)
3) D1 posts_meta/posts_content       → ada: render (X-Source: d1)   [jalur sekarang]
4) static dist/                      → ada: serve
5) tidak ada di mana pun             → 404 JUJUR (bukan homepage!)
```
Poin 5 memperbaiki soft-404 (§10.2 audit). Implementasi 404 jujur harus mengembalikan
`Response(..., { status: 404 })` dengan template halaman 404, **bukan** redirect ke `/`.

### 3.4 Verifikasi Fase 3
```bash
# jumlah objek vs jumlah baris
ssh root@130.254.47.93 'cd /opt/migration/seo-pipeline && node scripts/r2-count-coid.mjs'
npx wrangler d1 execute beriklan-seo --remote --command "SELECT COUNT(*) FROM posts_meta"

# sampel 50 slug D1-only (yang TIDAK ada di dist) harus 200 + X-Source: r2
curl -s https://beriklan.co.id/sitemap-blog.xml | grep -o '<loc>[^<]*' | tail -50 | sed 's|<loc>||' > /tmp/slugs.txt
while read -r u; do
  printf "%s %s\n" "$(curl -s -o /dev/null -w '%{http_code}' "$u")" \
                   "$(curl -s -D - -o /dev/null "$u" | grep -i 'x-source' || echo '-')"
done < /tmp/slugs.txt | sort | uniq -c

# slug ngawur harus 404 JUJUR
curl -s -o /dev/null -w "bogus %{http_code}\n" https://beriklan.co.id/blog/ini-slug-tidak-ada-xyz/
```
**Exit Criteria Fase 3:**
- [ ] jumlah objek R2 == `posts_meta` count == jumlah `<loc>` sitemap
- [ ] 50/50 sampel slug D1-only = **200** dengan `X-Source: r2`
- [ ] slug tidak dikenal = **404** (bukan 200 berisi homepage)
- [ ] `d1 insights` 1 jam: rows read turun drastis (< 50.000) karena serve tak lagi menyentuh D1
- [ ] kill-switch teruji: set `USE_R2=0` → situs tetap hidup dari D1
- [ ] tidak ada artikel baseline §B.0.2 yang hilang

---

## F. FASE 4 — Rampingkan D1 (HANYA setelah Fase 3 lulus + persetujuan user)

1. Backup ulang (§B.0.1) dengan tanggal baru.
2. Bandingkan ulang hitung 3-arah. **Selisih harus 0.**
3. Minta persetujuan user secara eksplisit sebelum `DELETE` apa pun.
4. Yang boleh dihapus lebih dulu (paling aman → paling berisiko), **dengan koreksi ukuran terukur 24 Sep**:
   - ~~`pending_indexing` baris `sent`/`expired` (backlog 3,8 jt)~~ → **revisi: nyaris tidak ada gunanya.**
     Tabel ini cuma **17.026 baris** (`pending` 16.754 · `gsc_submitted` 264 · `indexed` 8); status
     `sent`/`expired` **tidak ada**, jadi maksimal 272 baris bisa dihapus. Beban kuota datang dari
     scan berulang tanpa index (audit §8.2) → kerjakan **Fix A (§C.1.4)** dulu, bukan DELETE.
   - `keyword_queue` status `published` (**13.397** baris dari total **391.482**) — sudah ada di Postgres.
     Penghematan nyata ada di pemindahan **377.7xx baris `pending`** ke PG (Fase 2.3), bukan di delete ini.
   - `growth_log`, `keyword_ranks` lama (`keyword_ranks` **12.001** baris) — volume kecil, efek kuota kecil.
   - `posts_content` (**16.686** baris, payload terbesar per baris) → **terakhir**, dan hanya setelah
     7 hari R2 stabil tanpa fallback D1.
   > Kesimpulan revisi: urutan di atas **tidak** menurunkan kuota D1 secara berarti kecuali
   > `keyword_queue pending` dan `posts_content` ikut dipindah. Karena itu Fase 5 baru layak dikerjakan
   > setelah Fase 2 (PG = source of truth) dan Fase 3 (R2) terbukti, dan tetap butuh izin eksplisit user (Q4).
5. Setelah tiap DELETE: jalankan runbook verifikasi + `d1 insights`.
6. **Jangan pernah** `DROP TABLE`. Biarkan tabel kosong; worker masih punya jalur fallback.

**Exit:** D1 rows read/hari < 500.000 (dari 5.597.457), 0 error 7500 selama 7 hari,
jumlah artikel live tidak berubah.

---

## G. FASE 5 — Ekspansi industri wave 1 (detail di `INDUSTRY-EXPANSION.md`)

Ringkas untuk co.id:
1. Import **2.291 keyword** dari `web/src/data/industry-keywords.json` ke **Postgres** `keyword_queue`
   (bukan ke D1 — antrian besar tidak boleh balik ke D1). Endpoint import yang ada
   (`POST /api/admin/keywords/import`) harus diarahkan ke Postgres lebih dulu, atau dipakai sekali
   dengan batch kecil sambil dual-write.
2. Wave 1 = **kontraktor**. Wave 2 = **toko bangunan / bahan bangunan**. Wave 3 = **konveksi/garmen/kain/benang**.
   Wave 4 = **perumahan / agen properti**.
3. Pakai `web/src/data/clusters.json` (215 KB, selama ini menganggur) untuk membangun **topical cluster**:
   1 pillar + 8–12 supporting per industri, saling internal-link.
4. Gerbang validasi per wave: wave berikutnya **tidak dimulai** sebelum wave sebelumnya menghasilkan
   ≥ 1 URL dengan impressions > 100 di GSC, atau ≥ 3 klik.
5. Semua artikel baru tunduk pada cap 10–15/hari (Fase 1.1) dan pakem bahasa `../COPY-BIBLE.md`
   (tanpa klaim palsu, tanpa "pasti/garansi 100%", tanpa angka sosial proof fiktif).

**Exit Fase 5 wave 1:** 1 cluster kontraktor live (pillar + ≥ 8 artikel), semua URL 200,
terkirim ke IndexNow + GSC, dan tercatat di `keyword_ranks`/`geo_probes`.

---

## H. FASE 6 — GEO / LLM visibility tanpa API key

**Prinsip:** keyless, volume rendah, hasil di-cache, dan kegagalan dibaca sebagai *unknown* (bukan *absent*).

### H.1 Mesin: SearXNG self-hosted di VPS (pilihan utama)
```bash
ssh root@130.254.47.93 'cd /opt/migration && \
  docker run -d --name searxng --restart unless-stopped -p 127.0.0.1:8888:8080 \
  -e SEARXNG_BASE_URL=http://127.0.0.1:8888/ searxng/searxng:latest'
# aktifkan format json di settings.yml (formats: [html, json]), lalu:
curl -s "http://127.0.0.1:8888/search?q=jasa+iklan+facebook+bandung&format=json&language=id_ID" \
  | python3 -c "import json,sys;d=json.load(sys.stdin);print(len(d['results']));[print(r['url']) for r in d['results'][:5]]"
```
Alasan: tanpa API key, bisa agregasi google/bing/duckduckgo, rate-limit kita yang pegang,
hanya bind ke `127.0.0.1` (tidak terbuka ke internet).

Fallback bila SearXNG bermasalah: `html.duckduckgo.com/html/?q=`, `lite.duckduckgo.com/lite/?q=`,
`www.mojeek.com/search?q=`. **Jangan** menghantam Google HTML langsung dari IP datacenter dalam volume besar.

### H.2 Yang diukur
| Metrik | Cara |
|---|---|
| Kehadiran brand di 10 hasil organik | cek `beriklan.co.id` / `beriklan.my` di `results[].url` |
| Posisi | indeks kemunculan |
| Snippet yang dikutip | simpan `content` |
| Kehadiran blok AI | deteksi teks `AI Overview` / `People also ask` pada HTML SERP; kalau tidak terdeteksi → `unknown` |
| Sitasi LLM | jalankan probe yang sama lewat mesin yang menampilkan jawaban (bila tersedia keyless); kalau tidak, catat `not_measurable` |

### H.3 Skala & jadwal
- Maksimal **200 query/hari**, jitter 5–15 detik, dari VPS, UA realistis.
- Daftar query: 50 query komersial inti + 50 query industri wave aktif + 50 query brand + 50 query `.my`.
- Simpan ke Postgres `geo_probes` (skema §D.2.1) → tren mingguan, bukan angka tunggal.
- Job: time-gate di slot hourly (mis. `h == 22 UTC`), **bukan** cron baru.

### H.4 Sisi konten yang membuat kita layak dikutip (tanpa biaya)
- `llms.txt` (28 KB) dan `llms-full.txt` (48 KB) sudah live → pertahankan, perbarui isinya tiap wave industri.
- Schema `Article` + `FAQPage` + `ProfessionalService` + `Organization` sudah ada → lengkapi `sameAs`,
  `areaServed`, dan alamat NAP yang konsisten.
- Tambahkan blok jawaban ringkas (40–60 kata) di awal artikel untuk query berniat informasi —
  ini yang paling sering diambil mesin/LLM.
- FAQ harus spesifik-query (sudah dilakukan `growth-enrich`), dengan heading yang sama persis dengan query.

**Exit Fase 6:** 200 probe/hari tersimpan 7 hari berturut-turut, dashboard/tabel tren bisa dibaca,
0 banned/block permanen dari mesin pencari.

---

## I. FASE 7 — Monitoring & guardrail otomatis

1. **Email kesehatan harian** (sudah ada, 00:00 UTC) — pastikan isinya mencakup:
   publish hari ini, rows read D1, jumlah 404 jujur, jumlah soft-404 (harus 0), error 7500, kuota Resend,
   status growth loop, jumlah objek R2 vs `posts_meta`.
2. **Auto-pause publish** bila rows read D1 > 3.000.000/hari atau terdeteksi error 7500 —
   tulis label `AUTO-PAUSED` agar filter resume bisa menemukannya (pola yang sudah dipakai di worker).
3. **Probe eksternal 5 menit**: `/`, `/blog/`, satu slug D1-only, `/sitemap-blog.xml`, `/data/posts-index.json`.
   Alert bila ada yang bukan 200 atau bila slug D1-only kembali jadi soft-404.
4. **Weekly**: jalankan ulang §18 audit (`SEO-AUDIT-2026-09-24.md`) dan bandingkan dengan baseline KPI.

---

## J. Runbook verifikasi (dipakai setelah SETIAP deploy)

```bash
# 1. Worker hidup + cache (GET ×2, jangan HEAD)
curl -s -D - -o /dev/null "https://beriklan.co.id/data/posts-index.json" | grep -i x-cache
curl -s -D - -o /dev/null "https://beriklan.co.id/data/posts-index.json" | grep -i x-cache

# 2. Halaman inti
for p in "" blog/ order/ jasa-iklan-facebook/; do
  curl -s -o /dev/null -w "%{http_code} /$p\n" "https://beriklan.co.id/$p"
done

# 3. Sitemap & news
for p in sitemap.xml sitemap-blog.xml news.xml llms.txt; do
  curl -s -o /dev/null -w "%{http_code} $p\n" "https://beriklan.co.id/$p"
done

# 4. Slug D1-only (wajib 200, bukan homepage) + slug ngawur (wajib 404)
curl -s -o /dev/null -w "d1only %{http_code}\n" \
  "https://beriklan.co.id/blog/biaya-jasa-iklan-tiktok-untuk-bimbel-di-medan/"
curl -s -o /dev/null -w "bogus  %{http_code}\n" "https://beriklan.co.id/blog/ini-slug-tidak-ada-xyz/"

# 5. D1 sehat? (D1_ERROR = quota lock → tunggu 00:00 UTC, JANGAN perbaiki apa pun)
curl -s "https://beriklan.co.id/api/admin/email?token=$ADMIN_TOKEN&tab=overview" | head -c 300

# 6. Beban D1
cd /Volumes/macmini/Desktop/beriklan.co.id/web
npx wrangler d1 insights beriklan-seo --time-period 1h --sort-by reads --limit 5 --json

# 7. Cron heartbeat (idempotent karena time-gate)
curl -s "https://beriklan.co.id/api/cron/hourly?token=$ADMIN_TOKEN" | head -c 400
```

**ASSET DESYNC** (gejala: `/` dan static 404, tapi `/data/posts-index.json`, `/blog/<slug>/`, `/api/*` = 200)
→ **bukan** salah kode/DNS. Fix: `cd web && npx wrangler deploy`, lalu loop `curl -sI`
(jangan pakai variabel `$path` di zsh — reserved).

## K. Runbook rollback

```bash
cd /Volumes/macmini/Desktop/beriklan.co.id/web
npx wrangler deployments list | head -10      # ambil version_id stabil
npx wrangler rollback <version-id>
# matikan jalur R2 tanpa rollback kode:
printf '0' | npx wrangler secret put USE_R2
```
Rollback worker **tidak** mengubah `dist/` statis dan **tidak** me-reset cron schedules
(terverifikasi 2026-09-02: live schedules tetap 2 cron setelah deploy).

## L. Placeholder & sumber nilai

| Placeholder | Sumber |
|---|---|
| `$ADMIN_TOKEN` | secret worker (Fase 0.3) — jangan tulis di repo/dokumen |
| `$PIPELINE_TOKEN` | secret worker, sudah terpasang |
| `$CF_API_TOKEN` | `../DEPLOY_OPERATIONS.md` |
| `$VPS_PASS` | password manager |
| `<POSTGRES_CONTAINER>`, `<PG_USER>`, `<PG_DB>` | `ssh root@130.254.47.93 'docker ps'` + env container Coolify (`vonbh1rm26lwvdain`) |
| `$GROQ_API_KEY` | **rotate dulu** (Fase 0.3) |

ID non-rahasia yang boleh ditulis: account `766dfffa7e5dcd8ba246ebfa60bc10ba`,
zone co.id `47f87944d6d690eb388e7be1143c14a2`, D1 `beriklan-seo` / `0e71d6e3-231f-40a1-ac6b-6defc3976efd`,
bucket R2 `idberiklan`, app Coolify `igsbaxpsvuhopghoutiit2kk`.

## M. Target terukur (dibandingkan baseline §15 audit)

| KPI | Baseline | Target 30 hari | Target 90 hari |
|---|---|---|---|
| D1 rows read/hari | 5.597.457 | < 500.000 | < 200.000 |
| Publish/hari | 400 | 10–15 | 10–15 |
| Soft-404 | **9.373** URL berisiko | **0** | 0 |
| Artikel live (URL sitemap) | **16.872** | ≥ 16.872 | ≥ 17.500 |
| Clicks 28 hari (`sc-domain`) | 159 | > 220 | > 400 |
| Impressions 28 hari | 12.923 | > 16.000 | > 25.000 |
| `growth_log` ctr-fix | 0 | > 20 | > 100 |
| Error 7500 (quota lock) | berulang | 0 | 0 |

Target ini **bukan janji hasil**; ini ambang untuk memutuskan lanjut/berhenti per fase.

## N. Definition of done (seluruh plan co.id)

- [ ] Fase 0–4 selesai dengan bukti output di tracker
- [ ] 0 soft-404, slug tak dikenal = 404 jujur
- [ ] Serve artikel berjalan dari R2 dengan kill-switch teruji
- [ ] D1 hanya ops kecil; backlog besar ada di Postgres
- [ ] Growth loop hidup (`GSC_SITE_URL` = `sc-domain:`) dan menghasilkan entri `growth_log` baru tiap hari
- [ ] Publish stabil 10–15/hari, tidak ada artikel lama yang hilang
- [ ] Wave 1 industri (kontraktor) live dan terindex
- [ ] GEO probe keyless berjalan 200/hari dan tersimpan di Postgres
- [ ] Tidak ada rahasia di repo/dokumen; key Groq lama sudah di-revoke
- [ ] `arsip/TASKTRACKER-MIGRATION-VPS.md` sudah ditandai superseded

<!--END-->

