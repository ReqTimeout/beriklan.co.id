# Sistem SEO Beriklan.co.id — Dokumentasi Teknis Lengkap

**Untuk:** Agent coding penerus (beriklan.co.id + beriklan.my)  
**Tanggal:** 26 Aug 2026  
**Worker live:** `fdf75271-d53d-414d-b6cc-179d61cc8059` (beriklanweb)  
**Domain canonical:** `https://beriklan.co.id` (apex, `www` 301)  
**Tujuan:** 1) dapat client (lead) + 2) revenue Adsense dari blog long-tail  

---

## Daftar Isi
1. [Gambaran & Tujuan](#1-gambaran--tujuan)
2. [Keyword — Dari Mana & Disimpan Dimana](#2-keyword--dari-mana--disimpan-dimana)
3. [Generator Artikel — Pakai Apa & File Dimana](#3-generator-artikel--pakai-apa--file-dimana)
4. [Publish Pipeline — Draft → Live](#4-publish-pipeline--draft--live)
5. [Sitemap — Dinamis dari D1](#5-sitemap--dinamis-dari-d1)
6. [Worker CF & Semua Loop Cron](#6-worker-cf--semua-loop-cron)
7. [Growth Loops — GSC → Keyword → Enrich → CTR → Freshness](#7-growth-loops--gsc--keyword--enrich--ctr--freshness)
8. [Frontend Blog — Static + D1-First](#8-frontend-blog--static--d1-first)
9. [Adsense & Funnel Client](#9-adsense--funnel-client)
10. [File Penting & Secret](#10-file-penting--secret)
11. [State Live Saat Ini](#11-state-live-saat-ini)
12. [Rekomendasi Improvement — Push SEO untuk Client & Adsense](#12-rekomendasi-improvement--push-seo-untuk-client--adsense)
13. [Perintah Penting untuk Agent](#13-perintah-penting-untuk-agent)

---

## 1. Gambaran & Tujuan

**Arsitektur:** Astro 5.17 static + Cloudflare Worker `beriklanweb` yang serve `dist/` + render blog dinamis dari D1. Tanpa build, artikel baru langsung live lewat Worker.

```
keyword_queue (391k) ──► hourly-generate (AI) ──► generated_drafts (12k)
                                                    │
                                                    ▼
                                            sync-posts (15/hari, prioritas commercial+city)
                                                    │
                                                    ▼
                                   posts_meta + posts_content (12.6k live)
                                                    │
                              ┌─────────────────────┼─────────────────────┐
                              ▼                     ▼                     ▼
                        sitemap-blog.xml   pending_indexing (13k)   BlogFilter /blog/
                              │                     │
                              ▼                     ▼
                        GSC ping 60m        GSC Indexing 200/hari + IndexNow 50/jam + verify 300/hari
                              │                     │
                              └─────────┬───────────┘
                                        ▼
                                  Google Index → Traffic → Adsense + WA lead → Client
```

**Kenapa 391k keyword?** Programmatic SEO long-tail: `jasa × kota × industri` (contoh: `jasa iklan facebook di bandung untuk restoran`). Tiap keyword = 1 artikel = 1 URL yang bisa ranking.

**Dua tujuan, satu mesin:**
- **Client:** artikel commercial intent (`jasa iklan facebook di bandung`) → CTA WhatsApp di artikel → lead pipeline (`lead_pipeline` → email/WA follow-up)
- **Adsense:** semua artikel ada 4 slot Adsense (`ca-pub-4438184351486735`) — makin banyak artikel terindex → makin banyak pageview long-tail → revenue

---

## 2. Keyword — Dari Mana & Disimpan Dimana

### Sumber Keyword

| Sumber | File / Endpoint | Jumlah | Intent |
|--------|-----------------|--------|--------|
| `keyword-research-v2.json` curated (layanan inti × kota/industri) | `web/public/data/keyword-research-v2.json` (583 keyword, priority 85-95, city, service) | 583 | commercial/transactional |
| GSC impression tanpa halaman layak (auto) | `growth-gsc-loop` → `keyword_queue` source `gsc-impression` | ~10/hari | mixed |
| Expansi programmatic (view-live, viewers, dll) | `POST /api/admin/keywords/import` bulk import | 391k total | low→25 setelah rebalance |
| Trending Google Trends | `trending-generate` | 1/6 jam | informational |

### Tabel D1 `keyword_queue`

```sql
-- web/src/worker-entry.js:3260 (migrate)
CREATE TABLE keyword_queue (
  id INTEGER PRIMARY KEY,
  keyword TEXT UNIQUE,
  keyword_normalized TEXT UNIQUE, -- lower + trim + collapse space
  service TEXT,  -- jasa-iklan-facebook, jasa-pembuatan-website, dll (10 core)
  city TEXT,     -- bandung, jakarta, kosong untuk nasional
  intent TEXT,   -- commercial, transactional, informational
  priority_score INTEGER, -- 0-100 (90 core+city, 25 view-live)
  status TEXT,   -- pending, published, generated, draft
  source TEXT,   -- curated_research_v2, gsc-impression, etc
  article_slug TEXT, -- slug artikel setelah generate
  published_at TEXT
);
CREATE INDEX idx_kq_status ON keyword_queue(status);
CREATE INDEX idx_kq_service ON keyword_queue(service);
```

**File terkait:**
- `web/src/worker-entry.js:8571` — rebalance prioritas tiap hourly: view-live 25, core×city 90, industri `untuk` 90
- `web/src/worker-entry.js:8602` — round-robin per CORE_SERVICES (10 layanan inti) agar facebook/google tidak kelaparan
- `web/scripts/keyword_research*.js` — generator riset (lihat `web/public/data/`)

### Cara Tambah Keyword

```bash
# Bulk import (tanpa build)
curl -X POST "https://beriklan.co.id/api/admin/keywords/import?token=beriklan-admin-2026" \
  -H "Content-Type: application/json" \
  -d '[{"keyword":"jasa iklan facebook di cirebon untuk klinik","service":"jasa-iklan-facebook","city":"cirebon","intent":"commercial","priority":90}]'

# Lihat queue
curl -s "https://beriklan.co.id/api/admin/keywords?token=beriklan-admin-2026&format=json" | jq .keywordQueue.byStatus
curl -s "https://beriklan.co.id/api/admin/keywords/list?token=beriklan-admin-2026&status=pending&perPage=10" | jq
```

**Prioritas publish (penting):** `web/src/worker-entry.js:2020` ORDER BY commercial+city → commercial+untuk → commercial → city → long-tail → priority DESC

---

## 3. Generator Artikel — Pakai Apa & File Dimana

### AI Provider

**File:** `web/src/worker-entry.js:4186`

```js
const ZEN_FREE_MODELS = ["big-pickle","x-preview-f-free","mimo-v2.5-free","hy3-free","nemotron-3.5-lightning-free","nemotron-3-ultra-free"];
const ZEN_ENDPOINT = "https://opencode.ai/zen/v1/chat/completions"; // FREE 6 rotasi
const GROQ_CHAT_MODELS = ["openai/gpt-oss-20b","openai/gpt-oss-120b","qwen/qwen3.6-27b"];
const GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"; // fallback
// Keys: ZEN_API_KEY + GROQ_API_KEY + GROQ_API_KEY_2/3 (env-check: 3 keys OK)
```

**Handler:** `web/src/worker-entry.js:8517` `handleHourlyGenerate`

- Input: 1 keyword dari `keyword_queue` (round-robin core, `makeSlug` dari keyword, bukan `id` — fix `seed-xxx` bug `worker-entry.js:8562`)
- Prompt: `generateArticleForKeyword(item, env)` → system prompt SEO Indonesia formal, H1 keyword, 1500-1800 kata, 5 H2, FAQ 5, CTA WA, internal link
- Timeout: 120s per artikel (`perArticleTimeoutMs`)
- Output: `generated_drafts` D1 (status `draft`), foto `featuredImage` via `featured_image.js`

### Tabel `generated_drafts`

```sql
CREATE TABLE generated_drafts (
  slug TEXT UNIQUE, title TEXT, content TEXT, -- content HTML
  service TEXT, city TEXT, intent TEXT, priority_score INT,
  status TEXT, -- draft, committed, rejected
  created_at TEXT, committed_at TEXT
);
```

**Status:** `hourly` saat ini **PAUSED** (`cron_settings enabled=0`, `worker-entry.js:8530`) karena R2 queue 386k sudah penuh. Publish & indexing tetap jalan. Generate baru hanya jika `pending commercial+city < 500`.

### File Template Artikel

- Static: `web/src/pages/blog/[slug].astro:1` (4306 post WordPress import, 4 slot Adsense, getFeaturedImage)
- Dynamic Worker: `web/src/worker-entry.js:13776` `_buildArticleBody` — inject FAQ deterministik `_buildFaqItems` + internal mesh `_buildInternalLinksHtml` + 3 Adsense slot + related

---

## 4. Publish Pipeline — Draft → Live

**File:** `web/src/worker-entry.js:1973` `handleAdminSyncPosts` — cron `sync-posts` tiap jam `0 * * * *`

```js
// Pseudocode:
refillBufferCore()
drafts = SELECT * FROM generated_drafts WHERE status='draft' ORDER BY (commercial+city ...) LIMIT batchSize // 15
dailyLimit 150 WIB (wibTodayStr = UTC+7, fix 26 Aug, worker-entry.js:1991), remainingToday
for draft in drafts:
  if content <1000 or has <h1>/<script> → status='rejected'
  finalSlug = remap seed-/exp- → keyword slug
  sanitizeWaNumber(content)
  INSERT posts_meta (slug,title,excerpt,date,iso_date,category,readTime,tags,service,city)
  INSERT posts_content (slug,content)
  UPDATE generated_drafts status='committed'
  UPDATE keyword_queue status='published'
  INSERT pending_indexing url='https://beriklan.co.id/blog/'+finalSlug+'/' status='pending'
```

- **Lean mode:** `?mirror=0` (default cron) — **tidak** fetch `posts.json` GitHub, langsung D1. `?mirror=1` baru sync ke GitHub `src/data/posts.json` untuk static rebuild (berat, jangan pakai di cron).
- **WIB fix:** `wibTodayStr = new Date(Date.now()+7*3600*1000).toISOString().slice(0,10)` — sebelumnya UTC, bikin burst 300/hari.
- **Daily 150 + batch 15** via `cron_settings` `publish_daily_limit` / `publish_batch_size` — bisa di-tune tanpa deploy.

**Verifikasi:**

```bash
curl -s "https://beriklan.co.id/api/admin/sync/posts?token=beriklan-admin-2026" | jq
curl -s https://beriklan.co.id/api/health | jq '.counts, .pending_count'
```

---

## 5. Sitemap — Dinamis dari D1

**File:** `web/src/worker-entry.js:13670` `handleBlogSitemap` + route `web/src/worker-entry.js:410` `GET /sitemap-blog.xml`

```sql
SELECT slug, iso_date FROM posts_meta ORDER BY iso_date DESC  -- 12.646
UNION SELECT slug, committed_at FROM generated_drafts WHERE status='committed'
-- filter isJunkSlug ^(seed|exp)- , sort, XML <url><loc>https://beriklan.co.id/blog/<slug>/</loc><lastmod>...</lastmod><changefreq>weekly</changefreq><priority>0.8</priority>
```

- `Cache-Control: public, max-age=3600`
- `sitemap-index.xml` static (5 sub-sitemaps: blog 4306 static + city 500 + pillar 10 + tag 4952 + index)
- Worker alias `GET /sitemap.xml` → 301 ke `/sitemap-index.xml` (`worker-entry.js:415`)
- **Backfill:** `INSERT OR IGNORE INTO pending_indexing SELECT 'https://beriklan.co.id/blog/'||slug||'/' FROM posts_meta WHERE slug NOT IN (SELECT ... FROM pending_indexing)` — sudah jalan 26 Aug (12.988 pending)

**Ping:** `web/src/worker-entry.js:663` `sitemap-ping` tiap jam `handlePingSitemap` → `https://www.google.com/ping?sitemap=https://beriklan.co.id/sitemap-index.xml`

---

## 6. Worker CF & Semua Loop Cron

**File:** `web/src/worker-entry.js:480` `scheduled(event,env)` + `web/src/worker-entry.js:640` `cronMap` + `web/wrangler.jsonc` triggers

**Wrangler:** `web/wrangler.jsonc` — `main src/worker-entry.js`, `assets directory dist`, `run_worker_first ["/blog/*","/data/*","/sitemap-blog.xml"]`, `d1 DB beriklan-seo`, `r2 QUEUE idberiklan`

**Trigger fisik (Workers Free max 5, dipakai 2):**

| Trigger | Job Virtual |
|---------|-------------|
| `0 * * * *` hourly | semua di bawah |
| `*/15 * * * *` | `email-send` (Resend 100/hari) |

**Loop di dalam `0 * * * *` (`web/src/worker-entry.js:649`):**

| Jam | Handler | Endpoint | Tujuan |
|-----|---------|----------|--------|
| tiap jam | `hourly` | `handleHourlyGenerate?count=1&mode=draft` | generate 1 draft (PAUSED) |
| tiap jam | `sync-posts` | `handleAdminSyncPosts` | publish 15/hari |
| tiap jam | `indexnow` | `handleIndexNowCron?count=50` | IndexNow Bing/Yandex 50/jam |
| tiap jam | `gsc-indexing` | `handleGscIndexing?count=50` | GSC Indexing API 200/hari WIB |
| tiap jam | `sitemap-ping` | `handlePingSitemap` | ping sitemap ke Google |
| `h%6==0` (0,6,12,18 UTC) | `index-verify` | `handleIndexVerify?count=50` | URL Inspection 300/hari, auto-resubmit |
| `h%6==0` | `trending-fetch` | `handleTrendingCron` | fetch Google Trends |
| `h%6==0` | `rank-sync` | `handleRankSync?days=5` | GSC Search Analytics → keyword_ranks |
| `h%6==0` | `pending-cleanup` | `handlePendingIndexingCleanup` | hapus gsc_submitted >90 hari |
| `h%6==0` | `growth-gsc-loop` | `handleGrowthGscLoop?days=14&minImp=20` | GSC query tanpa halaman → keyword_queue |
| `h%6==0` | `trending-generate` | `handleTrendingGenerate?count=1` | 1 artikel trending/6jam |
| `h%6==0` | `snippet-optimize` | `handleSnippetOptimizer?count=3` | optimize sitemap? |
| `h%6==0` | `lead-pipeline` | `handleLeadPipeline?limit=100&ai=10` | match lead → email/WA |
| `h==9` UTC | `growth-enrich` | `handleGrowthEnrich?count=3` | posisi 3-18 tambah FAQ city |
| `h==9` UTC | `growth-ctr-fix` | `handleGrowthCtrFix?count=3` | CTR ≤2% rewrite title |
| `dow==1 && h==2` | `growth-freshness` | `handleGrowthFreshness?count=2` | artikel >90 hari refresh |
| `d==1 && h==0` | `content-refresh` | `handleRefreshContent?count=3` | refresh bulanan |
| `h==6` | `scrape-indonetwork` | `handleScrapeIndonetwork` | scrape lead |
| `h==7` | `scrape-google-places` | `handleScrapeGooglePlaces` | scrape lead |

**Retry & Pause:** `web/src/worker-entry.js:502` cleanup `cron_runs timeout >2h` + `cron_retry_queue` exponential backoff + auto-pause 3 gagal berturut + email alert ke `aramadhi92@gmail.com`

---

## 7. Growth Loops — GSC → Keyword → Enrich → CTR → Freshness

Semua D1-first, tanpa build, langsung live.

| Loop | File | Logic |
|------|------|-------|
| `growth-gsc-loop` | `worker-entry.js:1850` | `SELECT keyword,page,impressions FROM keyword_ranks WHERE impressions>=20 + date -14d` → keyword tanpa `posts_meta` → `INSERT keyword_queue source gsc-impression priority 40+imps/5` |
| `growth-enrich` | `worker-entry.js:2200` | `SELECT slug FROM keyword_ranks WHERE position 3-18 AND enriched_at IS NULL limit 3` → AI rewrite FAQ city-aware → `posts_content` + `posts_meta.enriched_at` |
| `growth-ctr-fix` | `worker-entry.js:2500` | `SELECT slug WHERE impressions>=50 AND ctr<=0.02 AND position<=30 limit 3` → AI rewrite title/meta description |
| `growth-freshness` | `worker-entry.js:2800` | `SELECT slug WHERE iso_date < now-90d AND impressions>0 limit 2` → AI refresh 1 paragraf + update `refreshed_at` |

**Tujuan:** naikkan ranking tanpa generate baru.

---

## 8. Frontend Blog — Static + D1-First

| File | Fungsi |
|------|--------|
| `web/src/data/posts.json` (4306) | WordPress import, static build |
| `web/src/pages/blog/[slug].astro:38` | `getStaticPaths` dari posts.json, 4 slot Adsense, `getFeaturedImage` |
| `web/src/utils/featured_image.js:16` | `SERVICE_IMAGES` 16 mapping → `/images/blog/*.webp`, infer dari title, `viewLiveImage` |
| `web/src/pages/blog/page/[n].astro:1` | pagination static 24/page (180 pages), ItemList + BreadcrumbList, windowed `1 2 … 179 180`, `ADENSE`-ready |
| `web/src/components/BlogFilter.svelte` | client filter `fetch /data/posts-index.json` |
| `web/src/worker-entry.js:382` | `blogMatch` D1-first: cek `matchRedirect` dulu (fix 26 Aug, `web/src/worker-entry.js:387`), lalu `renderBlogPost` dari `posts_meta+posts_content` |
| `web/src/worker-entry.js:405` | `GET /data/posts-index.json` dynamic dari `posts_meta` (14030 URL) |
| `web/src/worker-entry.js:13752` | `_getBlogTpl` template cache |

**Featured image fix 26 Aug:** typo `jasafacebokads` → `jasafacebookads` di `featured_image.js:17` + `worker-entry.js:1090` + copy file `jasafacebookads.webp`

---

## 9. Adsense & Funnel Client

### Adsense

- **Client:** `ca-pub-4438184351486735` (`web/src/pages/blog/[slug].astro:10`, `worker-entry.js:13936`)
- **Slots:** `inlineTop 1101825065` autorelaxed, `inlineMid 6162580059` fluid, `afterArticle 4505315237` autorelaxed, `sidebar 1237556436` auto (`web/src/pages/blog/[slug].astro:12`)
- **Lazy:** `window.__loadAdSense` on scroll/click/touch + 3s (`blog/[slug].astro:192`), `adsbygoogle.push({})`
- **Worker:** 3 slot + sidebar (`worker-entry.js:13936`)
- **Stub:** `web/src/components/AdsenseSlot.astro:19` hidden (tutorial pages) — perlu diaktifkan

### Client Funnel

- **CTA:** tiap artikel `_buildInternalLinksHtml` + FAQ + `wa.me/62811919328` dengan `text` keyword
- **Lead pipeline:** `web/src/worker-entry.js:665` `lead-pipeline` → `lead_pipeline` table → `personalizeLead` AI → `email_queue` + `wa_link`
- **Track:** `POST /api/track/wa` beacon + `wa_clicks` + `wa_followups`

---

## 10. File Penting & Secret

**File:**

| Path | Baris | Isi |
|------|-------|-----|
| `web/src/worker-entry.js` | 1-14270 | semua handler, scheduled, sitemap, indexing |
| `web/src/utils/featured_image.js` | 1-130 | mapping image |
| `web/src/data/posts.json` | — | 4306 static |
| `web/public/data/keyword-research-v2.json` | — | 583 curated |
| `web/public/images/blog/*.webp` | — | 14 image (106K avg) |
| `web/wrangler.jsonc` | — | triggers, assets, d1 |
| `web/src/pages/blog/[slug].astro` | 1-527 | static blog |
| `web/src/pages/blog/page/[n].astro` | 1-200 | pagination |
| `web/src/components/AdsenseSlot.astro` | 1-19 | stub |
| `web/scripts/fix-featured-image.js` | — | script dry-run (baru) |

**Secret (CF `wrangler secret`):**

| Secret | Isi | Wajib |
|--------|-----|-------|
| `ADMIN_TOKEN` | `beriklan-admin-2026` | ya |
| `GITHUB_TOKEN` | `ghp_...` | untuk mirror=1 |
| `ZEN_API_KEY` | `zen_...` | generate |
| `GROQ_API_KEY` + `_2/_3` | `gsk_...` | fallback |
| `GSC_SERVICE_ACCOUNT_JSON` | `{"type":"service_account",...}` | ya (`lgc-indexer`) |
| `GSC_SITE_URL` | `sc-domain:beriklan.co.id` | **wajib sc-domain** |
| `RESEND_API_KEY` | `re_...` | email 100/hari |

**D1:** `beriklan-seo` (binding `DB`), **R2:** `idberiklan`

**Endpoints admin:**

```
GET  /api/health
GET  /api/admin/keywords?token=...&format=json
GET  /api/admin/drafts?token=...&format=json&limit=5
GET  /api/admin/posts?token=...
POST /api/admin/posts?token=...&resubmit_all=1
POST /api/admin/keywords/import?token=...
GET  /api/cron/gsc-indexing?token=...&count=50&debug=1
GET  /api/cron/index-verify?token=...&count=50
GET  /api/admin/gsc-whoami?token=...
GET  /api/admin/env-check?token=...
GET  /sitemap-blog.xml
GET  /data/posts-index.json
```

---

## 11. State Live Saat Ini (26 Aug 16:16 WIB)

```
posts_meta 12.646 | pending_indexing pending 12.988 | gsc_submitted 11 | quota 200/200 (hari ini habis)
keyword_queue pending 381.873 | published 9.280 | indexing today 121
generation 0/24h (PAUSED sengaja)
worker fdf75271 WIB fix + image fix live
```

**Sudah fix 26 Aug:** WIB burst, image typo, backfill 8.6k, dedup 5k, /blog/page/2/ SEO (`f47a764f`)

**Belum fix (P1):** `AdsenseSlot.astro` stub, anchor meta Layout, script fix-featured-image dry-run

---

## 12. Rekomendasi Improvement — Push SEO untuk Client & Adsense

> Tujuan = `client datang` + `adsense revenue`. Semua di bawah tanpa nambah keyword 391k sia-sia.

### A. Untuk Client — Ranking Service Pages (Commercial)

| # | Improvement | Kenapa | File | Effort |
|---|-------------|--------|------|--------|
| A1 | **Jangan publish 381k, publish 150/hari paling commercial+city dulu** — queue sudah priority benar (`worker-entry.js:2020`), jangan override dengan publish bulk. 150/hari × 60 hari = 9k artikel city komersial yang benar-benar dicari. | Thin city-swap = Google Helpful Content penalty, 381k tidak habis 7 tahun (`12.988/200` butuh 65 hari, 391k butuh 5 tahun) | `worker-entry.js:1991` wibTodayStr | done |
| A2 | **Internal mesh: tiap artikel baru auto 5 link + page-1 booster** — sudah jalan `worker-entry.js:8816` + `8910`, JANGAN dimatikan. Ini bikin artikel baru terindex dalam 1 hop dari page yang sudah ranking top-10. | Crawl discovery, bukan cuma sitemap | `worker-entry.js:8816` | keep |
| A3 | **Growth loops jangan pause** — `growth-gsc-loop` (tangkap query GSC tanpa halaman) + `growth-enrich` (posisi 3-18 tambah FAQ city) + `growth-ctr-fix` (CTR≤2% rewrite title) + `growth-freshness` (>90 hari) = naik posisi tanpa generate baru. | Naik dari posisi 8 → 3 butuh FAQ, bukan artikel baru | `worker-entry.js:665,677` | enable |
| A4 | **Pillar hub per service:** `/jasa-iklan-facebook/pilar/` sudah ada link di blog (`blog/[slug].astro:339`), tapi `/jasa-iklan-facebook/bandung/` belum. Buat 10 hub city (1 per layanan × kota besar) yang list 20 artikel kota — jadi 1 hub ranking untuk 20 long-tail, bukan 20 doorway. | Konsolidasi authority, bukan doorway | `web/src/pages/jasa-*.astro` | baru |
| A5 | **Lead magnet di artikel commercial:** di `_buildInternalLinksHtml` tambah `Calon client: cek harga paket` → `/order/` dengan `wa_package` cookie (sudah ada `bk_wa_package`). | Artikel → lead, bukan bounce | `worker-entry.js:13818` | 5 baris |
| A6 | **Trending reduce:** `trending-generate` 1/6jam habiskan quota AI untuk informational low-value. Set `count=1` jadi `0` atau pause via `cron_settings enabled=0 WHERE name='trending-generate'`. | Hemat quota untuk commercial | `worker-entry.js:672` | 1 SQL |

### B. Untuk Adsense — Pageview Long-Tail

| # | Improvement | Kenapa | File | Effort |
|---|-------------|--------|------|--------|
| B1 | **Aktifkan AdsenseSlot real** — ganti `AdsenseSlot.astro:19` stub `display:none` → real `ins adsbygoogle` dengan `data-ad-client` + lazy. Tutorial 35+ halaman jadi monetized. | +20% inventory | `AdsenseSlot.astro` | 1 file |
| B2 | **Anchor + Auto ads:** tambah `<meta name="google-adsense-account" content="ca-pub-...">` di `Layout.astro <head>` + `enable_page_level_ads:true` (`blog/[slug].astro:192`). Ini aktifkan anchor mobile sticky + vignette otomatis. | +15% RPM tanpa nambah slot | `Layout.astro` | 2 baris |
| B3 | **Jangan tambah slot >4:** sudah 3 in-article + 1 sidebar (`worker-entry.js:13936`). Google auto ads isi sisanya. Lebih dari 4 = CLS + viewability turun. | Keep 4 | — | — |
| B4 | **Featured image relevan:** fix sudah, tapi cek `viewLiveImage` — title `jasa penonton live tiktok` tidak mengandung `view` → fallback benar tiktok, tapi cek 100 sample via `scripts/fix-featured-image.js --dry-run`. | CTR image di SERP & Discover | `featured_image.js:60` | script |
| B5 | **Speed:** `blog/[slug].astro` sudah lazy Adsense 3s + `fetchpriority high` image, `prose` `overflow-x-clip`. Jangan load `pagead` di pagination `/blog/page/*` — cuma di `/blog/<slug>/`. | Core Web Vitals | `blog/[slug].astro:192` | keep |
| B6 | **Indexing velocity:** backfill done, quota 200/hari, IndexNow 50/jam (`worker-entry.js:653` bing primary). Target 7.500 URL/bulan → 6.3M pv/bulan (12.646×500) × Rp5 CPM = Rp31jt/bulan. Bottleneck bukan slot, tapi **terindex**. | Revenue = indexed × pv | §6 | done |

### B7. Adsense **HANYA di artikel blog** (26 Aug 2026 fix)

Home `/`, service pages `/jasa-*/`, dan `/order/` sekarang **0 slot Adsense** (diverifikasi live). `Layout.astro` prop `showAdsense` default `false`; blog post + tag archive set `showAdsense={true}`. `google-adsense-account` meta juga conditional — hanya render di blog.

**Alasan:** Adsense autorelaxed/fluid di funnel (home, service, order) **mengganggu** conversion path. Orang cari "jasa iklan facebook bandung" → masuk service page → adsense di tengah CTA = bounce naik. Blog = informational, iklan boleh; service = transactional, iklan jangan.

**Verifikasi:** `curl https://beriklan.co.id/ | grep -c data-ad-slot` → `0`. `curl https://beriklan.co.id/blog/cara-jualan-di-shopee-depok/ | grep -c data-ad-slot` → `4`.

### B8. Push-rank: re-submit URL posisi 4-20 ke GSC tiap jam

Worker `handlePushRankCron` di `worker-entry.js:7677` jalan tiap jam `0 * * * *` (`worker-entry.js:667`). Query `keyword_ranks` posisi 4-20 dengan `impressions >= 30/14hari`, re-submit ke GSC Indexing API untuk refresh crawl.

**Tujuan:** Halaman yang sudah di page-1 tapi belum top-3 — Google crawl sinyal "URL_UPDATED" sering naikkan posisi 1-3 rank.

**Manual:** `curl -s "https://beriklan.co.id/api/cron/push-rank?token=beriklan-admin-2026&posMin=4&posMax=20&count=30" | jq`

### B9. AI Search Indexing (AEO/GEO)

`/llms.txt` dan `/llms-full.txt` sudah live (`worker-entry.js:4469`, `4547`) — format llmstxt.org dengan 100 artikel terbaru + FAQ untuk AI Overview. `robots.txt` sudah allow `GPTBot`, `ClaudeBot`, `PerplexityBot`, `anthropic-ai`.

FAQ schema di tiap artikel (`worker-entry.js:13828` `_buildFaqSchema`) sekarang 8 item, termasuk definisi & how-to (penting untuk AI Overview snippet).

**Untuk AEO (Answer Engine Optimization) lebih lanjut:**
- Submit juga ke `api.yandex.com` IndexNow (Yandex feed ke ChatGPT via Bing)
- Daftar `beriklan.co.id` di Bing Webmaster Tools (URL Inspection API aktif, gampang integration)
- Author markup `Person` sudah ada (`blog/[slug].astro:155`)
- `SpeakableSpecification` schema sudah ada di Article (`worker-entry.js:13903`)

### C. Untuk Keduanya — Index Cepat

| # | Improvement | File |
|---|-------------|------|
| C1 | **Pastikan `GSC_SITE_URL=sc-domain:beriklan.co.id`** via `wrangler secret put` + SA Owner (lihat `GUIDE-SC-DOMAIN-GSC.md`) | secret |
| C2 | **Sitemap lastmod harian** — sudah `iso_date DESC` + `iso_updated`, ping hourly | `worker-entry.js:13670,663` |
| C3 | **Jangan ubah `run_worker_first` `["/blog/*","/data/*","/sitemap-blog.xml"]`** — tanpa ini, static build bypass worker → FAQ enrich tidak tampil | `wrangler.jsonc` |
| C4 | **Monitor:** `GET /api/admin/keywords?format=json` → `indexing.pending` harus turun 200/hari, `keyword_ranks avg_position` harus <15 dalam 60 hari | endpoint |

**Urutan eksekusi untuk agent baru:**

```
P0 (hari ini): B1+B2 (adsense) + C1 (sc-domain) — 1 deploy
P1 (minggu ini): A4 (10 hub city) + A5 (order CTA) — 1 deploy
P2 (ongoing): A3 growth loops observe + C4 monitor — tanpa deploy
```

---

## 13. Perintah Penting untuk Agent

```bash
# Health
curl -s https://beriklan.co.id/api/health | jq
curl -s "https://beriklan.co.id/api/admin/keywords?token=beriklan-admin-2026&format=json" | jq '.keywordQueue.byStatus, .indexing, .publish'
curl -s "https://beriklan.co.id/api/admin/env-check?token=beriklan-admin-2026" | jq
curl -s "https://beriklan.co.id/api/admin/gsc-whoami?token=beriklan-admin-2026" | jq

# Publish
curl -s "https://beriklan.co.id/api/admin/sync/posts?token=beriklan-admin-2026" | jq
curl -s "https://beriklan.co.id/api/admin/drafts?token=beriklan-admin-2026&format=json&limit=5" | jq

# Indexing
curl -s "https://beriklan.co.id/api/cron/gsc-indexing?token=beriklan-admin-2026&count=5&debug=1" | jq
curl -s "https://beriklan.co.id/api/cron/index-verify?token=beriklan-admin-2026&count=5&debug=1" | jq
curl -s "https://beriklan.co.id/api/cron/indexnow?token=beriklan-admin-2026&count=5&debug=1" | jq
curl -s https://beriklan.co.id/sitemap-blog.xml | head -20
curl -s https://beriklan.co.id/sitemap-index.xml | head -20

# D1
CLOUDFLARE_API_TOKEN="cfut_wUtY…" npx wrangler d1 execute beriklan-seo --remote --command "SELECT status, COUNT(*) as n FROM pending_indexing GROUP BY status"
CLOUDFLARE_API_TOKEN="cfut_wUtY…" npx wrangler d1 execute beriklan-seo --remote --command "SELECT COUNT(*) as n FROM posts_meta"

# Build & Deploy
cd /Users/maabook/Desktop/beriklan.co.id/web && npm run build
CLOUDFLARE_API_TOKEN="cfut_wUtY…" CLOUDFLARE_ACCOUNT_ID="766dfffa7e5dcd8ba246ebfa60bc10ba" npx wrangler deploy
```

**SOP Darurat:** `AGENTS.md` — jangan ubah visual tanpa diminta, jangan deploy tanpa approval, backup `.bak-<timestamp>` sebelum edit, catat `version_id` rollback.

**Versi doc:** 1.0 — 26 Aug 2026 — untuk agent penerus beriklan.co.id + beriklan.my
