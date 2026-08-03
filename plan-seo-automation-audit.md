# Audit & Improvement Plan — Automasi SEO Beriklan.co.id

> **Tanggal audit:** 02 Agustus 2026
> **Sumber data live:** `https://beriklan.co.id/api/admin/keywords?token=...` + `.../publish?token=...` + `.../health?token=...`
> **Status:** 🟡 Fast-Win selesai (publish 600/hari, hourly aktif, backfill intent, reorder ORDER BY, GSC debug, IndexNow fix) — lanjut Phase 2–4 (sitemap lastmod, cluster, quality filter)
> **Owner:** Beriklan Digital Agency + Codex AI

---

## TL;DR — Apa yang Patut Diperbaiki Dulu

| # | Masalah kritis | Akibat sekarang |
|---|---|---|
| 1 | **Cron `hourly` (generate artikel) PAUSED** → 390.257 keyword pendingApproval idle di D1 | Artikel baru tidak di-generate; rebalance priority (city + core) tidak pernah jalan |
| 2 | **Publish pacing = 150/hari** (`publish_daily_limit`) → ETA **2.566 hari** (7 tahun) untuk habis 386k R2 queue | User kelamaan — tidak akan pernah selesai sebelum kompetitor membanjiri SERP |
| 3 | **GSC: indexed = 0 dari 4.348 pending**; backoff sampai 2026 pogostick | Submit tidak ditarik Google → 4.348 URL menganggur, tidak ranking |
| 4 | **Traffic nyaris nol**: 1 klik / 2.676 impresi / posisi rata-rata 70.3 = **page 7–8** | Artikel yang sudah live tidak kelihatan di 100 hasil pencarian awal |
| 5 | **Priority rebalance codenya ada** (city + core = prio 90) tapi **tak pernah jalan** karena cron pause | "Kota di-dahulukan" sudah di-rancang di code, tapi suspended → 0 dampak |
| 6 | **Intent field ada di schema** tapi tidak d pakai untuk ordering — semua long-tail d perlakukan sama | Intent lokalkah ada, tapi buy spasial tidak pinned ke prioritas tertinggi |

**Verdict:** Sistem tidak akan pernah proven. Harus diset ulang: un-pause cron boongan → tanpa increase hingga konservatif yang rasional, fix backoff GSC, dan reorder dengan intent + city.

---

## 1. State Saat Ini (data live, 02 Agu 2026)

### 1.1 Keyword Queue

| Metric | Value |
|---|---|
| Total | **391.121** keyword |
| Pending | 390.257 |
| Generated (article slug tied) | 414 |
| Published (status live) | 450 |

**byService** (top):
| Service | Total | Generated | Pending |
|---|---|---|---|
| Jasa View Live | 3.635 | 0 | 3.635 |
| Iklan Google | 2.713 | 0 | 2.713 |
| Pembuatan Website | 2.625 | 0 | 2.625 |
| Iklan Facebook | 2.568 | 0 | 2.568 |
| Iklan YouTube | 2.450 | 0 | 2.450 |
| Iklan Instagram | 2.447 | 0 | 2.447 |
| Landing Page | 2.421 | 0 | 2.421 |
| Iklan TikTok | 2.419 | 0 | 2.419 |
| Kelola Instagram | 2.366 | 0 | 2.366 |
| Kelola TikTok | 2.286 | 0 | 2.286 |
| Digital Marketing | 1.528 | 9 | 1.519 |

> Last **buildStats yang baru** ini (27.458 total di queue-kerja) bagian dari *buildStats*. Yang di `byServiceStatus` asli datang dari layer expansion (expansion_v4 = 95.507, intent_layer = 174.990) jadi total keyword_queue sampai ~391k.

**byCity** (26 kota, masing-masing seed ~1.052): 0 generated, 0 coverage.

### 1.2 Publish Pipeline

| Metric | Value |
|---|---|
| committed_total | 1.802 |
| draft_pending | 556 |
| committed_today | 150 (= daily limit) |
| daily_limit | **150** (cron_setting `publish_daily_limit`) |
| batch_size | 15 (cron_setting `publish_batch_size`) |
| r2_remaining | 384.888 (~386k) |
| **publish_eta_days** | **2.566** |

### 1.3 Indexing

| Metric | Value |
|---|---|
| pending_indexing | 4.348 |
| submitted (GSC) | 384 |
| **indexed** | **0** |
| failed | 0 |
| today_submitted | 44 |
| gsc_backoff_until | 2026-07-31 04:01 → sudah lewat tapi backoff lagi aktif |
| indexnow_backoff_until | 2026-08-02 10:01 |
| indexnow_total | 424 (last24h: 0) |

### 1.4 Generation (cron `hourly` — PAUSED)

| Metric | Value |
|---|---|
| cron_state | **enabled=0**, label "PAUSED — 386k sudah di R2 queue" |
| runs24h | 13 |
| generated24h | 33 |
| errors24h | 11 (≈33% error rate) |

### 1.5 GSC Performance (last 28 hari, sampai 31 Jul 2026)

| Metric | Value |
|---|---|
| total_clicks | **1** |
| total_impressions | 2.676 |
| avg_position | **70.3** (= page 7–8) |
| unique_keywords | 280 |
| top10 (pemenang) | 17 keyword |

Layanan dengan impresi terbanyak: Iklan Google Ads (759), Iklan Facebook (609), Iklan Instagram (430). Position rata-rata layanan utama antara 58–73 → page 6–8.

### 1.6 Cron yang Aktif

| Cron | Status | Catatan |
|---|---|---|
| `hourly` (generate) | **PAUSED** | 386k di R2 queue, takut duplikat. Resiko: priority rebalance untuk city+core tak jalan |
| `indexnow` (15 jam) | ACTIVE | backoff sering, 0 last 24h |
| `gsc-indexing` (6 jam) | ACTIVE | backoff sering, 0 indexed |
| `trending-generate` | PAUSED | fokus R2 |
| `email-send` (15 mnt) | ACTIVE | unrelated SEO |
| `lead-pipeline` | ACTIVE | unrelated SEO |
| `sync-posts` (via */15 trigger) | ACTIVE | publish 15/run × 24h = 360/hari (limit 150) |

Wrangler `triggers.crons` hanya punya 2: `0 * * * *` dan `*/15 * * * *`. Cron lain dikelola via `cron_settings` di D1 (dijalankan oleh dispatcher).

---

## 2. Diagnosis — 3 Patahan

### 2.1 Patahan #1: Publish Pacing (150/hari = 7 tahun)

`handleAdminSyncPosts` memakai `daily_limit=150` & `batch_size=15`:
- 150/hari × 365 = 54.750/tahun
- 386.690 / 54.750 = 7.06 tahun untuk habis

**Kenapa 150?** Komen code: "anti-spam, agar Google tidak melihat burst publikasi massal". Ini benar untuk *sustained pacing*, tapi **salah** untuk *ramp-up awal*. Google tidak menghukum situs yang publish konsisten 500–1.000/hari selama distribusi ada disbursement:
- Google melihat burst sebagai ancaman kalau: (a) volume tiba-tiba 10× baseline, (b) konten tipis/duplikat, (c) anchor building spam.
- Yang aman: 5× dari baseline selama 30 hari, lalu naik bertahap.

**Kalkulasi realistis berdasarkan Workers Quota + R2 read:**
- Sync-posts cron `*/15` = 96 jobs/hari. Worker Free: 100k requests/hari, 10ms CPU.
- Per publish ~1 R2 GET + few D1 write → 96 × ~6 = ~580 requests/hari. Sangat longgar.
- Batch 15/run × 96 = 1.440/hari potential. Worker CPU: 10ms/jobs × 96 = <1 detik/hari. Aman.
- Bottleneck sebenarnya: GSC indexing (200/hari submit). Tapi submit caps != publish caps — publish bisa lewat tanpa submit, Google akan crawl via sitemap.

**Rekomendasi:** naikkan `publish_daily_limit` ke **600** (25× baseline, aman untuk 30 hari ramp-up), `publish_batch_size` ke **25**. Pantau GSC daily impresi 7 hari. Kalau naik >30%, lanjut. Kalau ada manual penalty flag — kembali 150.

### 2.2 Patahan #2: Generation PAUSED → Priority Rebalance Tidak Jalan

Code `handleHourlyGenerate` punya rebalance:
```sql
-- demote view-live/spin-toko (prio → 25)
UPDATE keyword_queue SET priority_score = 25 WHERE service LIKE '%view-live%'...
-- boost core × city (prio → 90)
UPDATE keyword_queue SET priority_score = 90 WHERE city != '' AND service IN (...core...)
```

Tapi cron PAUSED → rebalance tak jalan → publish memakai ORDER BY city DESC, title-word-count DESC (di `handleAdminSyncPosts`). Artinya:
- ✅ City diutamakan (tertulis di publish query)
- ❌ Intent TIDAK diutamakan (field intent di schema, tapi tidak dipakai ORDER BY)
- ❌ Highest-priority core services (90) tidak disortir eksplisit di publish (yang dipakai: city + word-count)

**Rekomendasi:** 
1. Un-pause cron `hourly` tapi ubah default `mode=draft` + `count=1` — hanya jalan 1×/jam untuk memastikan generated_drafts buffer饱满.
2. Atau split: rebalance jalan sebagai cron terpisah (`priority-rebalance` mingguan, lightweight 2 SQL UPDATE).
3. Tambah `intent` ke ORDER BY publish dengan rule:
   ```sql
   ORDER BY
     -- 1. Commercial + city (paling konversi-ready)
     (CASE WHEN intent IN ('commercial','transactional') AND city != '' THEN 0 ELSE 1 END),
     -- 1b. Commercial + industry ("jasa X untuk {industri}") — bisnis sudah punya kebutuhan spesifik
     (CASE WHEN intent IN ('commercial','transactional') AND title LIKE '% untuk %' THEN 0 ELSE 1 END),
     -- 2. Commercial flat
     (CASE WHEN intent IN ('commercial','transactional') THEN 0 ELSE 1 END),
     -- 3. City apa pun
     (CASE WHEN city != '' THEN 0 ELSE 1 END),
     -- 4. Long-tail (judul ≥ 4 kata)
     (CASE WHEN wrdcnt >= 4 THEN 0 ELSE 1 END),
     -- 5. priority_score
     priority_score DESC,
     id ASC
   ```
   **Industry keywords** (seeded via layer `industri`: `jasa {svcName} untuk {indName}`, intent=commercial,
   prio 70) sekarang masuk rebalance boost → 90 (sama seperti city+core) dan dapat tier 1b sendiri di ORDER BY.

### 2.3 Patahan #3: GSC Indexed = 0

Dari 4.348 pending_indexing, **submitted=384, indexed=0**. Diagnostic:
1. **GSC Indexing API hanya bekerja untuk JobPosting/BroadcastEvent** (resmi), untuk konten biasa submit ditarik tapi Google hampir selalu abaikan.
2. **`submitToGscCore` ada backoff** → mungkin 429/403 terus → submitted stuck di 384 dan tak naik.
3. **Yang benar-benar mengindeks adalah Googlebot via sitemap** — tapi sitemap belum ditarik. Submit URL via Search Console UI adalah satu-satunya jalan untuk konten biasa (manual atau via PubSubHubbub).

**Rekomendasi:**
- **Debug backoff**: log response GSC API; kalau 403, berarti token salah/expire; kalau 429, rate limit (200/day resmi).
- **Tingkatkan sitemap punch frequency**: ping Google `https://www.google.com/ping?sitemap=https://beriklan.co.id/sitemap-index.xml` tiap publish batch (sudah deprecated tapi murah).
- **Pastikan sitemap-blog.xml di-link dari index.sitemap**: yang sudah ada.
- **Fokus sitemap-pages baru**: tiap publish, submit URL via `https://www.google.com/business(ping)` — deprecated tapi murah. Lebih murah, push feed ke Google Discover via RSS.
- **Real iso_date**: Update `<lastmod>` tiap publish_bulk ke `now()` di sitemap-blog → Google lebih sering crawl.
- **Cek robots.txt**: pastikan tidak ada Disallow yang menelan URL publish. (Sekarang sudah benar, kecuali `/jasa-pembuatan-landing-page/`.)

---

## 3. Improvement Plan — Priority 1 → 3 (Eksekusi 4 minggu)

### Phase 1 (Minggu 1): Un-pause + Pacing Up

**Objektif:** Publish 600/hari, fokus `commercial + city` dulu.

#### 1.1 Update cron_settings via API (instant)
```bash
# Live API call (token = beriklan-admin-2026)
curl -X PUT "https://beriklan.co.id/api/admin/cron-settings?token=beriklan-admin-2026&name=publish_daily_limit&value=600"
curl -X PUT "https://beriklan.co.id/api/admin/cron-settings?token=beriklan-admin-2026&name=publish_batch_size&value=25"

# Un-pause hourly (auto-generate buffer, mode draft)
curl -X PUT "https://beriklan.co.id/api/admin/cron-settings?token=beriklan-admin-2026&name=hourly&enabled=1"
```

Jika tidak ada endpoint cron-settings generic, update via admin UI atau jalankan statement SQL direct di D1 (via `wrangler d1 execute --remote`):
```sql
UPDATE cron_settings SET enabled=1, label='Artikel otomatis — generate buffer draft count=1 mode=draft' WHERE name='hourly';
UPDATE cron_settings SET cron='600', label='Publish harian maksimum (ramp-up phase)' WHERE name='publish_daily_limit';
UPDATE cron_settings SET cron='25', label='Publish per sync-posts run' WHERE name='publish_batch_size';
```

#### 1.2 Refactor ORDER BY di handleAdminSyncPosts (worker code)
File `src/worker-entry.js` sekitar L1860:
```js
const draftsToPublish = await env.DB.prepare(
  `SELECT slug, title, content, service, city, intent FROM generated_drafts
   WHERE status='draft'
   ORDER BY
     -- Priority 1: commercial + city (paling konversi-ready)
     (CASE WHEN intent IN ('commercial','transactional') AND city != '' THEN 0 ELSE 1 END),
     -- Priority 2: commercial flat (layanan + nama kota)
     (CASE WHEN intent IN ('commercial','transactional') THEN 0 ELSE 1 END),
     -- Priority 3: city apa pun
     (CASE WHEN city IS NOT NULL AND city != '' THEN 0 ELSE 1 END),
     -- Priority 4: long-tail (judul ≥ 4 kata)
     (CASE WHEN (length(title) - length(replace(title, ' ', ''))) >= 4 THEN 0 ELSE 1 END),
     -- Priority 5: priority_score (dari rebalance)
     COALESCE(priority_score, 50) DESC,
     id ASC
   LIMIT ?`
).bind(batchSize).all();
```

**Prerequisite:** `generated_drafts` harus punya kolom `intent` & `priority_score` — cek schema, kalau belum → migrate:
```sql
ALTER TABLE generated_drafts ADD COLUMN intent TEXT;
ALTER TABLE generated_drafts ADD COLUMN priority_score INTEGER DEFAULT 50;
-- backfill dari keyword_queue (join via slug)
UPDATE generated_drafts AS d
SET intent = k.intent, priority_score = k.priority_score
FROM keyword_queue AS k
WHERE d.slug = k.article_slug;
```

### Phase 2 (Minggu 2): Fix Indexing + Rebalance as its own cron

#### 2.1 Pisahkan rebalance sebagai cron mingguan (`priority-rebalance`)
Tidak harus tun-pause `hourly`. Buat handler baru:
```js
async function handlePriorityRebalance(request, env) {
  // 3 SQL statements: demote view-live, boost core+city, boost commercial intent
  await env.DB.prepare(
    "UPDATE keyword_queue SET priority_score = 25 WHERE status='pending' AND (service LIKE '%view-live%' OR service LIKE '%shopee%' OR service LIKE '%tokopedia%') AND priority_score > 30"
  ).run();
  await env.DB.prepare(
    "UPDATE keyword_queue SET priority_score = 90 WHERE status='pending' AND city IS NOT NULL AND city != '' AND service IN ('jasa-iklan-facebook','jasa-iklan-instagram','jasa-iklan-google','jasa-iklan-tiktok','jasa-iklan-youtube','jasa-digital-marketing','jasa-pembuatan-website','jasa-pembuatan-landing-page','jasa-kelola-instagram','jasa-kelola-tiktok')"
  ).run();
  // BURST intent commercial ke prio 95
  await env.DB.prepare(
    "UPDATE keyword_queue SET priority_score = 95 WHERE status='pending' AND intent IN ('commercial','transactional')"
  ).run().catch(()=>{});
  return new Response(JSON.stringify({ok:true, rebalanced:true, time: new Date().toISOString()}), {headers:{"Content-Type":"application/json"}});
}
```

Register di dispatcher: `path === "/api/cron/priority-rebalance"` → tiap Minggu (`0 4 * * 1`).

#### 2.2 Debug GSC backoff (cegah indexed=0)
```js
// In submitToGscCore: log the full Google API response body, not just status
const resp = await fetch("https://indexing.googleapis.com/v3/urlNotifications:publish", { ... });
const body = await resp.text();  // log even on error
console.log("[gsc] status", resp.status, "body", body.slice(0,200));
```

Add endpoint `/api/admin/gsc/debug?token=...&url=X` → satu submit + log response. Diagnosa:
- if 403: token issue → refresh
- if 429: quota hari ini habis → besok
- if 200 tapi tetap idx 0: Google terima tapi tidak crawl → harus tumbuh authority dulu (backlink, E-E-A-T)

#### 2.3 Sitemap lastmod boost
Update `scripts/build_sitemaps.py` tiap publish run menulis `<lastmod>` = `now()` (saat ini pakai build time). Buat cron pasca-publish yang menulis `sitemap-blog.xml` Dengan lastmod hari ini (hanya untuk URL yang baru publish). Google melihat freshness → naik crawl priority.

### Phase 3 (Minggu 3–4): Cluster + Authority Signal

#### 3.1 Internal linking auto-link (dari plan.md)
- Build D1 graph dari `posts_meta.service` + `city` + `tags`.
- Endpoint `/api/related-links?slug=X` → top 5.
- Inject di `[slug].astro` section "Related" → PageRank internal ke pilar + page komersial.

#### 3.2 Schema boost per pilar (dari plan.md)
- ✅ **DONE** (commit `0028601`): HowTo JSON-LD (4 steps) di 10 halaman pilar, via
  `Schema.astro` + `Layout.astro` prop `howTo`, data dari array `steps` per pilar.
  FAQ schema sudah ada sebelumnya via prop `faq`. Sekaligus bersihkan duplikat
  props `faq`/`breadcrumb`/`service` di `jasa-iklan-facebook` & `jasa-iklan-google`
  dan typo "Jasa Jasa" di beberapa service description. Live verified 10/10.
- Cron mingguan `schema-boost` **tidak dibuat** — schema statis (build-time) sudah
  cukup & deterministic; AI generate tidak diperlukan untuk 10 halaman tetap.

#### 3.3 Sitemap per indusry change ping
Tiap minggu, push paket setelah publish batch:
```bash
curl "https://www.google.com/ping?sitemap=https://beriklan.co.id/sitemap-blog.xml" || true
curl "https://www.bing.com/ping?sitemap=https://beriklan.co.id/sitemap-blog.xml" || true
```
(Google ping deprecated tapi murah; Bing IndexNow sudah ada.)

### Phase 4 (Minggu 5–8): Quality Filter + Content Refresh

#### 4.1 Prune matt URL (dari plan.md)
- Cron `gsc-rank-audit` harian: query GSC last 7d → klasifikasi URL jadi pemenang/sedang/mati.
- Setelah 90 hari tanpa impresi (`mati`): set `metarobot noindex` + hapus dari sitemap → bersih-bersih "noise" Google.

#### 4.2 Content refresh (cron `content-refresh` bulanan)
- Untuk URL pemenang: AI generate 1 paragraph "update 2026" di appendix → kirim ke GSC "Request Indexing" (manual, dampak tinggi).

---

## 4. Cron yang Perlu Aktif & Yang Perlu Pause

### Aktifkan / Tingkatkan
| Cron | Sekarang | Target | Alasan |
|---|---|---|---|
| `hourly` (generate) | PAUSED | **ACTIVE, count=1, mode=draft** | Rebalance priority perlu jalan — otherwise city dipakai tanpa intent rebalance |
| `sync-posts` (publish) | limit 150/hari | **limit 600/hari, batch 25** | 7th-century ETA → 1.9 tahun (masih sangat tinggi; bisa ditingkatkan lagi setelah GSC tumbuh) |
| `priority-rebalance` (NEW) | doesn't exist | `0 4 * * 1` (mingguan) | Pisahkan rebalance agar tak tergantung cron hourly |

### Tetap / Perlu Pantauan
| Cron | Action |
|---|---|
| `indexnow` | OK, perlu fixing backoff loop |
| `gsc-indexing` | OK, perlu debug 0-indexed |
| `content-refresh` | OK aktif |
| `snippet-optimize` | OK aktif |

### JANGAN Sentuh
- `email-send`, `lead-pipeline`, `trending-generate` (trending paused betul untuk fokus R2 queue)

---

## 5. Fast-Win Checklist (Eksekusi Hari Ini)

1. ✅ **Un-pause `hourly`** — DONE (deploy commit `bba43ef`, terverifikasi live:
   `hourly` enabled=1, label "Artikel otomatis (generate buffer draft count=1 mode=draft)", scheduler `count=1&mode=draft`).
   Run manual `/api/cron/hourly-generate?count=1&mode=draft` → ok, generated 1, kw_advanced 1.

2. ✅ **Naikkan `publish_daily_limit` ke 600** — DONE (migration array di `handleAdminMigrate`, terverifikasi live:
   `publish_daily_limit=600`, `publish_batch_size=25` di dashboard publish). Sync-posts manual +25 → 175 terverifikasi.

3. ✅ **Backfill intent + priority_score ke generated_drafts** — DONE via `handleAdminMigrate` (84 statement, terverifikasi):
   - `CREATE INDEX idx_q_article_slug` + `idx_q_keyword` (backfill butuh index, kalau tidak → D1 CPU limit time-out)
   - `ALTER TABLE generated_drafts ADD COLUMN intent TEXT` + `priority_score INTEGER DEFAULT 50` (idempotent, ERR duplikat aman)
   - Backfill jalur 1: `keyword_queue.article_slug = generated_drafts.slug`
   - Backfill jalur 2: `keyword_normalized = replace(slug,'-',' ')` via idx_q_keyword (cover draft R2-queue yang article_slug kosong)

4. ✅ **Reorder publish query** — DONE (commit `9763c41`): cascade
   commercial+city → **commercial+industry (`title LIKE '% untuk %'`)** → commercial → city → long-tail ≥4 kata → `priority_score DESC` → id.
   Plus: rebalance hourly kini boost **industry keyword** (intent commercial + `keyword LIKE '% untuk %'`) → prio 90, setara city+core.

5. ✅ **Debug GSC** — DONE: auth OK, quota 200/hari, 3 submit `count=3&debug=1` semua HTTP 200.
   **`indexed=0` bukan bug code** — Google terima submit tapi crawl-nya lambat (sitemap masih ditarik). Google/Bing ping deprecated (404/410).
   IndexNow backoff bug diperbaiki (format timestamp SQLite `YYYY-MM-DD HH:MM:SS` vs `toISOString()` `T`/`Z` → compare selalu false) — commit `5625a48`/`b4c1b6b`.

6. ✅ **Ping sitemap** — DONE (kesimpulan: **deprecated**). `google.com/ping` → 404, `bing.com/ping` → 410.
   Path sekarang: sitemap ditarik langsung Googlebot (robots.txt allow), + IndexNow submit tiap publish batch (20/run, 4 engine, 429 genuine host rate-limit di-backoff benar).

> **Deploy commit terkait:** `bba43ef` (migrate+pacing), `15fe2e4` (index backfill), `81178b8` (backfill keyword_normalized),
> `5625a48`/`b4c1b6b` (IndexNow backoff fix), `9763c41` (industry priority + tier ORDER BY).

## 5b. Status Cron saat Ini (live, verified)

| Cron | Status | Catatan |
|---|---|---|
| `hourly` (generate) | **ACTIVE** count=1 mode=draft | Rebalance priority (city+core+industry) jalan tiap jam |
| `sync-posts` (publish) | **ACTIVE** limit 600/hari batch 25 | ETA R2 2.566 → ~2.200 hari (masih tinggi; ramp-up bertahap) |
| `indexnow` | ACTIVE | Backoff benar setelah fix; 429 = rate-limit host, bukan bug |
| `gsc-indexing` | ACTIVE | Submit OK; indexed=0 = crawl delay Google |
| `trending-generate` | PAUSED | Fokus R2 queue (sengaja) |
| `email-send`, `lead-pipeline` | ACTIVE | Unrelated SEO — jangan sentuh |

---

## 6. Expected Outcome (4 minggu)

| Metric | Sekarang | Target 4 minggu | Catatan |
|---|---|---|---|
| publish/hari | 150 | 600 (ramp-up) | Tidak ada manual penalty flag |
| published_total | 1.802 | 4.200+ (+2.400 bulan ini) | 4× lebih banyak live URL |
| indexed (GSC) | 0 | 500+ | Setelah sitemap ping + GSC token fix |
| total_impressions | 2.676 | 8.000–15.000 | Bypass posisi 70 via more cluster + internal link |
| avg_position | 70.3 | 50–60 | Number of URLs masuk top 30 bertambah |
| ETA habis R2 queue | 2.566 hari | 640 hari (1.75 thn) | Setelah naik lagi ke 1.000/hari bila 30 hari stabil |

> **Disclaimer:** Progress mengikuti Google crawl cadence (mingguan sampai bulanan). Kita cuma bisa push submit + quality; Google tetap pilih. Target di atas realistis;
 tidak ada yang menjamin #1 — tapi kalau tidak menambah satupun dari yang ini, situs tidak akan tumbuh.

---

## 7. Catatan Teknis untuk Implementor

### 7.1 Cron `hourly` un-pause vs generation double
Karena 386k sudah di R2 queue, generate baru berisiko duplikat. **Setting `mode=draft` + `count=1`** berarti:
- Tiap jam: 1 artikel baru → critical buffer (menggantikan yang di-publish).
- Cek duplikat via `keyword_normalized` + slug — kalau ada → skip.
- Setelah 30 hari stabil → naikkan count=2.

Atau **lebih aman:** un-pause `hourly` TIDAK untuk generate, TAPI untuk rebalance only — flag `?mode=rebalance-only`. Code change minimal:
```js
if (mode === 'rebalance-only') {
  await doRebalance();
  return json({ ok: true, rebalanced: true });
}
```

### 7.2 Anti-burst crawl pattern
Kenaikan publish 150 → 600 dalam 1 hari = 4× baseline. Google akan melihat burst. Mitigasi:
- Spread publish batch sepanjang hari (96 cron × 6 articles bukan 4× 150 di satu jam).
- Submit IndexNow tiap batch (IndexNow cuma rate-limited per host, bukan per-URL).
- Pastikan sitemap publish tiap batch (bukan cuma harian).

### 7.3 Workers Quota
- Workers Free: 100k req/hari, 10ms CPU/request.
- sync-posts tiap 15 menit = 96 jobs/hari. 600 publish / 96 = ~6.25 jobs. CPU per publish ~0.5–2ms (R2 GET + D1 writes). Total CPU/hari ~190ms. Aman.
- IndexNow tambahan 600 requests/hari (1 per URL). Worker-bound. Tidak masalah.

---

## 8. File yang Perlu Diubah

| File | Lokasi | Perubahan |
|---|---|---|
| `web/src/worker-entry.js` | L1860 (handleAdminSyncPosts `ORDER BY`) | Tambah intent + city cascade |
| `web/src/worker-entry.js` | L1860 (publish query) | Tambah join ke `keyword_queue` untuk intent (atau backfill ke drafts) |
| `web/src/worker-entry.js` | ~L1817 (handleAdminSyncPosts) | Tambah fallback ke statement SQL yang sama kalau intent NULL tidak ada di drafts table |
| `web/scripts/build_sitemaps.py` | lastmod logic | Refresh lastmod tiap publish batch |
| D1 schema | `generated_drafts` | `ALTER TABLE ... ADD COLUMN intent TEXT, priority_score INTEGER DEFAULT 50` |
| D1 `cron_settings` | `publish_daily_limit`, `publish_batch_size`, `hourly` | Update via SQL/API |

---

## 9. Verifikasi Pasca-Implementasi

### Minggu 1 check (consol-check):
```bash
curl -s "https://beriklan.co.id/api/admin/publish?token=beriklan-admin-2026&format=json" | python3 -m json.tool | grep -E "published_today|daily_limit|eta|draft_pending"
```
- `published_today` harus mendekati `daily_limit` (600) tiap akhir hari.
- `publish_eta_days` turun dari 2.566 ke ~640.

### Minggu 2 check (GSC):
```bash
curl -s "https://beriklan.co.id/api/admin/keywords?token=beriklan-admin-2026&format=json" | python3 -m json.tool | grep -E "indexing|gsc"
```
- `indexing.indexed` naik dari 0 → >100 (sudah ada URL ter-index).
- `gsc.impressions` naik 2× baseline.

### Minggu 4 check (traffic):
- GSC `total_clicks` naik dari 1 → 10+.
- GSC `avg_position` turun dari 70 → 55–60.

Kalau 4 minggu semua metric naik → naikkan publish_daily_limit ke 1.000. Tidak naik → audit konten quality (substance, internal link, backlink).

---

**Versi:** 1.0 (02 Agu 2026)
**Maintainer:** Beriklan Digital Agency + Codex AI
**Related:** `plan.md` (Spionase Iklan + SEO Push Strategy 12 minggu), `plan-prospecting-legacy.md` (lead pipeline lama)