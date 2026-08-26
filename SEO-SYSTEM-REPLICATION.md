# SEO-SYSTEM-REPLICATION.md

> **Panduan lengkap untuk agent coding** yang ingin **menduplikasi sistem SEO otomatis** milik
> `beriklan.co.id` ke website lain. Dokumen ini adalah self-contained blueprint: arsitektur,
> skema database, cron, pipeline keyword → artikel → publish → index → growth-loop, semua
> endpoint API, cara deploy, kuota, dan gotcha. Cukup ganti domain/niche/layanan.

Dokumen pendamping: `AGENTS.md` (design & engineering), `SEO-GROWTH-SYSTEM.md` (desain growth loop).

---

## 1. RINGKASAN SISTEM (apa yang direplikasi)

Sebuah **content-engine SEO otomatis** tanpa GitHub Actions, jalan 100% di **Cloudflare Workers
gratis**, dengan alur:

```
keyword seeds ─► keyword_queue (D1, 391K+ rows)
                     │  (cron hourly generate)
                     ▼
              generated_drafts (AI: Zen deepseek-v4-flash-free → fallback Groq gpt-oss)
                     │  (cron hourly sync-posts, publish bertahap)
                     ▼
          posts_meta + posts_content (D1)  ──►  /blog/<slug>/  LIVE (D1-first dynamic render)
                     │                              │
                     ▼                              ▼
   pending_indexing ─► GSC Indexing API + IndexNow + sitemap ping   (indeks cepat)
                     │
                     ▼
   GSC searchAnalytics ─► growth loop (gsc-loop, enrich, ctr-fix, freshness) ─► optimasi balik
```

Kunci desain:
- **D1-first rendering** — artikel live begitu ditulis ke `posts_meta`/`posts_content`,
  tanpa perlu rebuild statis. File statis (`src/data/posts.json` → GitHub) hanyalah
  fallback/mirror dan TIDAK boleh menghambat publish.
- **Tanpa GitHub Actions** — semua otomasi via Cloudflare Cron Triggers (gratis, max 5 cron/account).
- **Publish bertahap (gradual)** — dibatasi per hari & per batch agar Google tidak melihat burst massal.
- **AI gratis dulu, fallback berbayar** — Zen free → Groq gpt-oss → (opsional) model lain.

---

## 2. STACK & PRASYARAT

| Komponen | Dipakai | Catatan |
|---|---|---|
| Static site | Astro 5 + Svelte 5 + Tailwind | `/blog/[slug].astro` dynamic route |
| Compute | Cloudflare Workers (free) | `src/worker-entry.js`, ~14k baris |
| DB | Cloudflare D1 (SQLite) | binding `DB` |
| Object storage | Cloudflare R2 | binding `QUEUE` (buffer draft) |
| AI gratis | Zen `deepseek-v4-flash-free` | sering 429, selalu siapkan fallback |
| AI fallback | Groq `openai/gpt-oss-120b`, `qwen/qwen3.6-27b`, `openai/gpt-oss-20b` | 3 API key dirotasi |
| Search Console | Service Account (GCP) + Indexing API | SA harus Owner di GSC property |
| Indexing cepat | Google Indexing API + IndexNow + sitemap ping | |
| Email (opsional) | Resend free (100/hari) | untuk alert/follow-up |
| Mirror statis | GitHub (best-effort) | hanya untuk static rebuild, jangan blocking |

**Wajib punyai sebelum mulai:**
1. Domain + Cloudflare zone (DNS aktif).
2. GitHub repo + PAT (untuk mirror & deploy config).
3. GCP project + service account JSON + **service account sudah jadi Owner di Search Console**
   (Settings → Users & permissions) untuk property yang akan dipakai (apex/domain/www).
4. Zen API key + Groq API key(s).
5. (Opsional) Resend API key, IndexNow key.

---

## 3. ARSITEKTUR RENDERING (paling penting dipahami)

`fetch()` di Worker menangani `/blog/<slug>/` dengan urutan:

1. Cek slug ada di `posts_meta` → render **dinamis** dari `posts_meta` (judul/meta/SEO override)
   + `posts_content` (isi HTML). Ini jalur LIVE.
2. Jika tidak ada di D1 → fallback ke **static asset** hasil build (Astro SSG dari `src/data/posts.json`).
3. Jika tidak ada juga → 404.

**Implikasi untuk replikasi:**
- Simpan konten di **dua tabel** (`posts_meta` tanpa konten; `posts_content` khusus konten) agar
  query meta ringan dan konten di-load hanya saat dibutuhkan.
- Jangan pernah menunggu GitHub/static rebuild untuk menerbitkan artikel.
- `run_worker_first` di `wrangler` harus mencakup path blog & redirect agar Worker tidak di-bypass asset.

Kolom growth di `posts_meta` (di-set oleh growth loop, dibaca renderer):
- `seo_title`, `seo_description` → override `<title>`/meta/OG (H1 tidak berubah).
- `refreshed_at` → badge "Diperbarui" + `dateModified` di schema Article (`datePublished` tidak diubah).
- `enriched_at`, `ctr_fixed_at` → cooldown agar growth loop tidak mengedit ulang terlalu sering.

---

## 4. SKEMA D1 (inti)

Buat dengan `CREATE TABLE IF NOT EXISTS` + `ALTER` idempotent (jalankan ulang aman). Tabel inti:

### 4.1 Konten blog
```sql
-- Metadata (tanpa konten) — ringan untuk list/feed/sitemap
CREATE TABLE IF NOT EXISTS posts_meta (
  slug TEXT PRIMARY KEY, title TEXT, excerpt TEXT,
  date TEXT, iso_date TEXT, category TEXT, readTime TEXT,
  tags TEXT, service TEXT, city TEXT, featured INTEGER DEFAULT 0,
  generated INTEGER DEFAULT 0, iso_updated TEXT,
  -- growth loop
  seo_title TEXT, seo_description TEXT,
  enriched_at TEXT, ctr_fixed_at TEXT, refreshed_at TEXT
);

-- Isi HTML (pisah dari meta)
CREATE TABLE IF NOT EXISTS posts_content (
  slug TEXT PRIMARY KEY, content TEXT
);
```

### 4.2 Draft hasil AI (sebelum publish)
```sql
CREATE TABLE IF NOT EXISTS generated_drafts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT UNIQUE NOT NULL, title TEXT NOT NULL, content TEXT NOT NULL,
  service TEXT, city TEXT, source TEXT,
  status TEXT DEFAULT 'pending',         -- pending|draft|committed|rejected
  intent TEXT, priority_score INTEGER DEFAULT 50,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP, committed_at TEXT
);
```

### 4.3 Antrian keyword
```sql
CREATE TABLE IF NOT EXISTS keyword_queue (
  id TEXT PRIMARY KEY,                    -- imp-/seed-/exp-<slug>-<rand>
  keyword TEXT NOT NULL, keyword_normalized TEXT,
  source TEXT,                            -- curated_import|expand_v2|admin_seed_v1|gsc-impression|...
  seed TEXT, discovered_at TEXT,
  status TEXT DEFAULT 'pending',          -- pending|published|skipped
  service TEXT, city TEXT,
  priority_score INTEGER DEFAULT 50,
  intent TEXT,                            -- commercial|transactional|informational|pain-point
  article_slug TEXT, published_at TEXT
);
CREATE INDEX idx_kq_status ON keyword_queue(status);
CREATE INDEX idx_kq_service ON keyword_queue(service);
```

### 4.4 Antrian indexing
```sql
CREATE TABLE IF NOT EXISTS pending_indexing (
  url TEXT PRIMARY KEY, status TEXT DEFAULT 'pending',
  created_at TEXT, gsc_submitted_at TEXT, indexnow_at TEXT,
  index_state TEXT, index_checked_at TEXT, resubmit_count INTEGER DEFAULT 0
);
```

### 4.5 Rank & growth log
```sql
CREATE TABLE IF NOT EXISTS keyword_ranks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  keyword TEXT NOT NULL, page_url TEXT NOT NULL,
  position REAL, clicks INTEGER DEFAULT 0, impressions INTEGER DEFAULT 0, ctr REAL DEFAULT 0,
  date TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(keyword, page_url, date)
);

CREATE TABLE IF NOT EXISTS growth_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  action TEXT NOT NULL, slug TEXT, keyword TEXT,
  position REAL, ctr REAL, impressions INTEGER,
  static_page INTEGER DEFAULT 0,
  before_json TEXT, after_json TEXT, ai_model TEXT, error TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### 4.6 Pengaturan cron (tune tanpa deploy)
```sql
CREATE TABLE IF NOT EXISTS cron_settings (
  name TEXT NOT NULL UNIQUE, cron TEXT NOT NULL, enabled INTEGER DEFAULT 1, label TEXT
);
-- Nilai pacing publish disimpan sebagai angka di kolom `cron`:
INSERT OR IGNORE INTO cron_settings (name, cron, enabled, label)
  VALUES ('publish_daily_limit', '300', 1, 'Publish harian maksimum');
INSERT OR IGNORE INTO cron_settings (name, cron, enabled, label)
  VALUES ('publish_batch_size', '30', 1, 'Publish per sync-posts run');
```

### 4.7 (Opsional) email, lead, WA tracker, scrape, rate-limit, api_keys
Lihat `src/worker-entry.js` untuk `email_templates`, `campaigns`, `email_queue`,
`lead_*`, `wa_clicks`, `wa_followups`, `scrape_*`, `rate_limits`, `api_keys`.
Tidak wajib untuk replikasi inti SEO.

---

## 5. CRON SYSTEM (Cloudflare Workers Free = 5 cron/account)

Workers Free hanya boleh **5 ekspresi cron per account** (bukan per script). Strategi: pakai 5 slot,
dan "selundupkan" lebih banyak job ke dalam slot hourly `0 * * * *` pakai **time-gate** (cek jam/hari di kode).

### 5.1 Lima slot yang dipakai (`wrangler.jsonc` → `triggers.crons`)
```
0 * * * *        # hourly block (banyak job + growth time-gate)
*/15 * * * *     # email-send
30 6 * * *       # scrape-indonetwork
0 7 * * *        # scrape-google-places
0 3 * * 1        # snippet-optimize
```

### 5.2 Isi slot hourly `0 * * * *` (jalankan via `ctx.waitUntil`)
Tiap jam:
- `hourly-generate` (generate 1 draft AI → `generated_drafts`, mode=draft)
- `sync-posts` (publish bertahap draft → D1 + index; **lean, tanpa mirror GitHub**)
- `indexnow` (submit IndexNow, count=50)
- `gsc-indexing` (submit Indexing API, count=50 → 50×24 = 1200 target, dibatasi quota 200/hari di core)
- `sitemap-ping` (kirim sitemap ke GSC)

Time-gate dalam slot yang sama:
```
h % 6 === 0  →  index-verify, trending-fetch, rank-sync, pending-cleanup,
                growth-gsc-loop, trending-generate, snippet-optimize, lead-pipeline
h === 9      →  growth-enrich, growth-ctr-fix       (harian 09:00 UTC)
dow===1 && h===2 → growth-freshness                 (Senin 02:00 UTC)
d===1 && h===0   → content-refresh                  (bulanan)
```

### 5.3 Cara pasang cron via API (gotcha penting!)
```
PUT /accounts/{ACCOUNT_ID}/workers/scripts/{SCRIPT}/schedules
Body HARUS array mentah: [{"cron":"0 * * * *"}, ...]
JANGAN {"schedules":[...]}  → error 10026.
Error 10072 = cap 5 cron/account sudah penuh.
```
Jika cap penuh, kosongkan dulu cron script lain dengan PUT body `[]`.

---

## 6. PIPELINE KEYWORD

### 6.1 Sumber keyword (semua masuk `keyword_queue` dengan dedupe)
1. **Seed manual** — `POST /api/admin/keywords/seed?target=view-live|shopee|tokopedia|all` (template per layanan × kota).
2. **Expansion v2** — `POST /api/admin/keywords/expand?layer=all|industri|question|comparison|pain|view-live`
   (9 industri × 10 layanan × 25 kota + varian pertanyaan/perbandingan/pain-point).
3. **Import terkurasi (baru, direkomendasikan)** — `POST /api/admin/keywords/import?source=nama`
   dengan body JSON array `[{keyword, service, city, intent, priority}]`. Dedupe otomatis.
   Contoh hasil riset tersimpan di `web/public/data/keyword-research-v2.json` (583 keyword:
   live-streaming, pembuatan website, 25 industri × 8 layanan inti).
4. **GSC feedback loop** — `growth-gsc-loop` menangkap query GSC ber-impresi tapi belum ada halaman
   blog layak → insert `source='gsc-impression'`.

**Dedupe rule:** cek `keyword` DAN `keyword_normalized` sebelum insert.
**Slug:** `keyword.toLowerCase().replace(/[^a-z0-9]+/g,'-')`, strip leading/trailing `-`, max 80 char.

### 6.2 Skoring / prioritas saat publish
Urutan publish (low-competition dulu) dalam `sync-posts`:
```
commercial/transactional + city  →  commercial + "untuk {industri}"  →  commercial
→  punya city  →  judul long-tail (≥4 kata)  →  priority_score DESC  →  id ASC
```
Rebalance tiap jam: turunkan priority service jenuh (view-live/shopee/tokopedia) agar
layanan inti × kota tetap dapat jatah generate.

---

## 7. GENERATE ARTIKEL + PUBLISH BERTAHAP

### 7.1 Generate (hourly)
`handleHourlyGenerate(count, mode=draft)`:
- Ambil N keyword `status='pending'` (prioritas sesuai §6.2).
- Generate via `generateArticleForKeyword` — AI Zen dulu, fallback Groq.
  - **Prompt menghasilkan JSON**: judul, slug, excerpt, content HTML (beberapa `<h2>`), dsb.
  - Self-check: tolak content `<1000 char`, mengandung `<h1>`/`<!DOCTYPE`/`<script``, atau pola rusak.
  - Sanitasi nomor WA placeholder.
- Simpan ke `generated_drafts` (status=`draft`). Log ke `hourly_generate_runs`.
- **Rate-limit**: Zen sering 429 → tangani `RATE_LIMITED`, lanjut di jam berikutnya.

### 7.2 Publish bertahap (hourly, `sync-posts`)
`handleAdminSyncPosts` — **dua mode** (fix penting, lihat §12 gotcha "1102"):
- **`?mirror=1` (JARANG, on-demand)** — mode penuh: muat semua `posts_meta`+`posts_content`,
  merge dengan `posts.json` GitHub, PUT balik ke GitHub untuk static rebuild. **Berat** — hanya
  jalankan manual sesekali, JANGAN hourly.
- **default / `?mirror=0` (HOURLY, ringan)** — hanya: refill buffer R2 + publish batch draft ke D1
  (`posts_meta`+`posts_content`) + advance `keyword_queue` → `published` + enqueue `pending_indexing`
  + submit GSC/IndexNow. Tidak menyentuh GitHub → cepat, tidak kena CPU ceiling.

Pacing:
- `dailyLimit` dari `cron_settings.publish_daily_limit` (misal 300).
- `batchSize` dari `publish_batch_size` (misal 30), `min(batch, sisa_hari)`.
- `publishedToday` dihitung dari `committed_at >= hari_ini`.

Setelah publish (lean), otomatis:
- Insert URL baru ke `pending_indexing`.
- Submit ke GSC Indexing API (`submitToGscCore`, quota 200/hari, auto-retry 429).
- Submit ke IndexNow (`submitToIndexNowCore`, backoff rate-limit).
- Kirim email alert (Resend) jika 0 publish padahal ada draft, atau ada gagal.

---

## 8. INDEXING (GSC + IndexNow + sitemap)

- **Google Indexing API**: quota **200 URL/hari**. Kirim bertahap (50/jam sampai cap). Simpan
  `gsc_submitted_at`, track `index_state` via `index-verify` (300/hari).
- **IndexNow**: submit ke Bing/Yandex, pakai IndexNow key, backoff saat rate-limit.
- **Sitemap ping**: `handlePingSitemap` kirim `sitemap-blog.xml` ke GSC tiap jam; catat di `gsc_sitemaps`.
- `pending_indexing` = sumber kebenaran URL yang belum terindeks; `pending-cleanup` bersihkan yang sudah indexed.

**Normalisasi URL**: gunakan varian yang **sama dengan GSC property** (www vs apex) saat submit,
kalau tidak GSC menolak/"0 rows". Di beriklan: property yang hidup = `https://www.beriklan.co.id/`.

---

## 9. GROWTH LOOP (GSC feedback, tanpa GitHub Actions)

Semua handler baca GSC `searchAnalytics` lalu **tulis langsung ke D1** → live tanpa rebuild.

| Job | Endpoint | Jadwal | Fungsi |
|---|---|---|---|
| gsc-loop | `/api/cron/growth/gsc-loop` | tiap 6 jam | Query GSC 14 hari; keyword komersial ber-impresi tanpa halaman blog layak → `keyword_queue` (`source=gsc-impression`) |
| enrich | `/api/cron/growth/enrich` | harian 09:00 | Artikel posisi 3–18 → rewrite paragraf pembuka + FAQ spesifik-query (`growth-intro`, `growth-faq`) |
| ctr-fix | `/api/cron/growth/ctr-fix` | harian 09:00 | Impresi≥`minImp` & CTR≤`maxCtr` & posisi≤30 → rewrite `seo_title`+`seo_description` (override SERP, H1 tetap) |
| freshness | `/api/cron/growth/freshness` | Senin 02:00 | Artikel >N hari ber-impresi → sisip callout "Update {tahun}" (`freshness-update`), set `refreshed_at` |

**Cooldown** (via `posts_meta.*_at`): enrich 21 hari, ctr-fix 30 hari, freshness mingguan.
**Audit trail**: semua aksi ke `growth_log` (action/slug/keyword/position/ctr/impressions/before_json/after_json/ai_model/error).

Parameter penting (bisa di-tune):
```
gsc-loop  : days, minImp, maxQueue
enrich    : count, minImp, posMin, posMax
ctr-fix   : count, minImp (clamp min 10), maxCtr (clamp max 0.1)
freshness : count, ageDays
```

---

## 10. AI PROVIDER & PROMPT

- Urutan: `Zen deepseek-v4-flash-free` (gratis, sering 429) → `Groq` via `GROQ_CHAT_MODELS`
  `["openai/gpt-oss-120b","qwen/qwen3.6-27b","openai/gpt-oss-20b"]` (3 key dirotasi).
- Helper `generateWithZenOrGroq(prompt, env)`: tangani 429/timeout, fallback antar provider.
- Prompt artikel menghasilkan **JSON** (title/slug/excerpt/content-html). Parse JSON defensif.
- Prompt growth (enrich/ctr/fresh) juga JSON + batasan (misal `seo_title` ≤60 char, `seo_description` ≤155 char).
- **Self-check konten** sebelum publish/simpan: panjang minimum, dilarang `<h1>`/doctype/script, pola rusak.

---

## 11. DAFTAR ENDPOINT API (admin & cron)

Semua butuh `?token=ADMIN_TOKEN` kecuali yang publik.

**Admin / dashboard**
- `/api/admin` — dashboard HTML
- `/api/admin/health` — JSON status sistem + hitungan tabel
- `/api/admin/env-check`, `/api/admin/gsc-whoami` — cek env & identitas service account
- `/api/admin/audit/content?threshold=3000` — deteksi thin-content
- `/api/admin/drafts?format=json`, `/api/admin/drafts/commit` — lihat/commit draft
- `/api/admin/keywords`, `/api/admin/keywords/list?status=&service=&page=` — browser keyword
- `/api/admin/keywords/seed`, `/api/admin/keywords/expand?layer=`, `/api/admin/keywords/import` (POST, body JSON array)
- `/api/admin/sync/posts?mirror=0|1` — publish bertahap (+mirror statis opsional)
- `/api/admin/rank-tracker`, `/api/admin/growth-log`, `/api/admin/posts`, `/api/admin/publish`
- `/api/admin/cron/toggle` — enable/disable job via `cron_settings`
- `/api/admin/backup`, `/api/admin/migrate` (jalankan semua CREATE/ALTER idempotent)

**Cron (bisa dipanggil manual untuk testing)**
- `/api/cron/hourly-generate?count=1&mode=draft`
- `/api/cron/indexing`, `/api/cron/indexnow?count=50`, `/api/cron/index-verify?count=50`
- `/api/cron/gsc-indexing?count=50`, `/api/ping-sitemap`
- `/api/cron/rank-sync?days=5`, `/api/cron/gsc-pull`, `/api/cron/index-cascade?count=50&dry=1`
- `/api/cron/growth/gsc-loop|enrich|ctr-fix|freshness` (§9)
- `/api/cron/trending`, `/api/cron/trending-generate?count=1`, `/api/cron/snippet-optimize?count=3`
- `/api/cron/refresh?count=3`, `/api/cron/email/send`, `/api/cron/leads/process`
- `/api/cron/scrape/indonetwork`, `/api/cron/scrape/google-places`

---

## 12. CARA DEPLOY & GOTCHA

### 12.1 Deploy
```
export CLOUDFLARE_API_TOKEN=...
export CLOUDFLARE_ACCOUNT_ID=...
npx wrangler deploy          # upload worker + sync triggers cron
npx wrangler secret put GSC_SERVICE_ACCOUNT_JSON   # isi service account JSON
npx wrangler secret put GITHUB_TOKEN
npx wrangler secret put GSC_SITE_URL               # property GSC yang dipakai (www/apex/sc-domain)
```
Jalankan `npx wrangler d1 execute` / panggil `/api/admin/migrate` sekali untuk bikin tabel.

### 12.2 Gotcha yang sudah terbukti (WAJIB tahu)
1. **Cap 5 cron/account** — pakai 5 slot + time-gate; kosongkan script lain (`PUT []`) kalau penuh.
2. **Schedules API** body harus array mentah `[{"cron":...}]`, bukan `{"schedules":[...]}` (10026).
3. **Error 1102 (CPU ceiling)** — `sync-posts` mode penuh (muat ~40MB content + serialize+PUT posts.json
   40MB) melampaui limit Workers Free. **Solusi**: hourly pakai `mirror=0` (lean, D1 saja);
   mirror GitHub hanya `?mirror=1` manual sesekali. Blog tetap live via D1.
4. **GSC property mismatch** — SA harus Owner di property yang dipakai. Apex bisa 403 / domain
   property 0 rows; property yang aktif di beriklan = `https://www.beriklan.co.id/`. Set `GSC_SITE_URL`
   ke property yang benar-benar punya data.
5. **D1 `all()`** hasilnya `{results:[...]}` (plural).
6. **Slug remap** — draft dengan slug `seed-*`/`exp-*` (artefak id) dipetakan ulang ke slug SEO
   dari keyword saat publish, supaya URL yang di-submit/index bukan 404.
7. **`run_worker_first`** di wrangler harus mencakup path blog & redirect agar Worker tidak di-bypass.
8. **Tanpa GitHub Actions** — jangan andalkan CI; semua via cron + Worker. GitHub hanya mirror statis.
9. **Rate limit AI** — Zen 429 ditangani dengan fallback Groq; gunakan timeout per artikel.
10. **Jangan commit secret** (token CF, GitHub PAT, service account JSON, API keys) ke repo.

---

## 13. CHECKLIST REPLIKASI (langkah demi langkah)

1. [ ] Provision Cloudflare: buat D1 (`wrangler d1 create`), R2 bucket, Worker.
2. [ ] Buat semua tabel (§4) via `migrate` idempotent; seed `cron_settings` (publish_daily_limit, publish_batch_size).
3. [ ] Set secrets: `GSC_SERVICE_ACCOUNT_JSON`, `GSC_SITE_URL`, `GITHUB_TOKEN`, Zen/Groq keys, `ADMIN_TOKEN`.
4. [ ] Tambahkan service account sebagai **Owner** di Search Console property target.
5. [ ] Siapkan seed keyword sesuai niche (buat `SERVICES`, `INDUSTRIES`, `CITIES`, template per layanan)
      lalu jalankan `expand` + `import` (pakai file JSON terkurasi).
6. [ ] Deploy Worker + pasang 5 cron trigger + time-gate hourly.
7. [ ] Uji manual satu per satu: `hourly-generate` → cek `generated_drafts`;
      `sync/posts` (mirror=0) → cek artikel LIVE di `/blog/<slug>/`; `indexnow`/`gsc-indexing`.
8. [ ] Aktifkan growth loop setelah data GSC cukup (butuh impresi): `gsc-loop`, lalu `enrich`/`ctr-fix`/`freshness`.
9. [ ] Monitor via `/api/admin/health`, `/api/admin/drafts?format=json`, `/api/admin/growth-log`,
      `/api/admin/audit/content`.
10. [ ] Opsional: mirror statis ke GitHub (`sync/posts?mirror=1`) seminggu sekali untuk rebuild.

---

## 14. KUOTA & LIMIT YANG HARUS DIHORMATI

| Resource | Limit | Strategi |
|---|---|---|
| Workers Free CPU | ~10ms CPU/req (dapat 1102 kalau berat) | lean sync-posts, batch kecil |
| Cron triggers | 5/account | time-gate di slot `0 * * * *` |
| GSC Indexing API | 200 URL/hari | 50/jam, auto-retry 429 |
| index-verify | 300/hari | tiap 6 jam |
| Resend email | 100/hari | batch, skip kalau kuota habis |
| Zen free | rate-limit 429 | fallback Groq otomatis |
| GitHub contents API | file ≤100MB, tapi CPU Worker | hanya mirror sesekali |

---

## 15. STATUS SAAT INI (beriklan.co.id, snapshot 2026-08-26)

- `keyword_queue`: **~391.000** keyword, ~381.000 pending, ~9.000 published.
- `generated_drafts`: **~11.000** total, ~10.600 committed (live), ~380 pending (dipublish bertahap 300/hari, batch 30).
- `sync-posts` lean berjalan normal (publish 30 draft dalam ~9 detik, tanpa 1102).
- GSC: property aktif `https://www.beriklan.co.id/` (rank-sync 295 rows/14 hari). Apex 403, domain property 0 rows.
- Growth: enrich/freshness sudah terverifikasi menulis ke D1 & live; `ctr-fix` masih 0 kandidat (data www tipis, clamp minImp=50) — akan terisi saat data apex/domain masuk.
- Riset keyword terkurasi v2 sudah di-import (359 baru): fokus **live-streaming**, **pembuatan website**, + 25 industri × 8 layanan. File: `web/public/data/keyword-research-v2.json`.

---

**Versi:** 1.0 · 2026-08-26
**Sumber acuan kode:** `src/worker-entry.js`, `wrangler.jsonc`, `web/GSC-INDEXER-SETUP.md`
