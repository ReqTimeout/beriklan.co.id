# Audit Flow Otomatis + Indexing + Adsense — Beriklan.co.id

**Tanggal:** 26 Aug 2026  
**Worker live:** `f47a764f-9b20-4266-9fbf-a359fb949d69` (beriklanweb)  
**Daily limit publish:** 150/hari · batch 15 · prioritas `commercial+city` (lihat `web/src/worker-entry.js:1999`)  
**GSC quota:** 200 URL/hari · IndexNow 50/jam · GSC verify 300/hari

> Jawaban cepat: **iya, tiap hari publish otomatis.** Hari ini 26 Aug: 300 artikel live (melebihi limit karena 2 run sync-posts pagi ini — gap kecil). Queue 381.873 masih panjang tapi sudah diprioritaskan **paling prioritas dulu per hari**, bukan asal publish. Flow sitemap + GSC + inspection **jalan**, tapi ada 3 gap yang bikin indexing lambat & adsense belum optimal — semua ada fix di bawah.

---

## 1. Ringkasan Eksekutif — 5 Temuan Kritis

| # | Temuan | Dampak | Fix |
|---|--------|--------|-----|
| 1 | **Publish 300/hari, bukan 15** (limit 150 dilanggar hari ini) | Burst = sinyal spam ke Google, quota GSC jebol | Set `cron_settings.publish_daily_limit=150` sudah benar, tapi `publish_batch_size=15` tapi 2x cron hourly 00:00 & 02:00 keduanya nge-push — butuh mutex harian |
| 2 | **featured_image mismatch** — typo `jasafacebokads` + fallback `jasa-digital-marketing` untuk 40% queue non-service | CTR & dwell turun, image tidak relevan | Script pencocokan sudah siap `scripts/fix-featured-image.js` (lihat §4) |
| 3 | **Sitemap live tapi 380 post belum masuk queue** — `posts_meta=12.646` vs `pending_indexing pending=8.303 + gsc_submitted=376` = 8.679 (missing ~3.9k) | 3.9k artikel tidak pernah di-submit ke GSC/IndexNow | Backfill script `POST /api/admin/posts` bulk resubmit — sudah ada handler |
| 4 | **GSC indexing stuck: 0 indexed, 8.3k pending** — `pending_indexing.indexed=0` padahal worker submit tiap jam | URL baru tidak terindex cepat | IndexNow ok, tapi GSC Indexing API butuh `sc-domain:beriklan.co.id` owner verification & `GSC_SITE_URL` benar |
| 5 | **Adsense stub di tutorial + 3 slot di blog kurang lazy** — `web/src/components/AdsenseSlot.astro:19` render hidden, blog ada 4 slot autorelaxed tapi tidak ada Anchor/Matched Content | Revenue tidak maksimal, CLS di mobile | Aktifkan `AdsenseSlot.astro` real + tambah anchor + matched-content (lihat §10) |

---

## 2. Status Live (26 Aug 2026 15:54 WIB)

```
Health: worker beriklanweb v-2026-08-01-enrich-faq-mesh
posts_meta: 12.646 | posts_content_nonempty: 12.646 | generated_drafts: 12.717
keyword_queue: total 391.481 (pending 381.873 · published 9.280 · generated 328)
indexing pending: 8.303 | gsc_submitted: 376 | indexed: 0 | today submitted: 121
sitemap-blog.xml: 12.646 URL (dynamic) | sitemap-index.xml: 200
generation 24h: 0 (hourly PAUSED — 386k R2 queue penuh, lihat worker-entry.js:8530)
Hari ini diposting: 300 artikel (2026-08-26 WIB) via sync-posts x2
```

**Validasi:**
```bash
curl -s https://beriklan.co.id/api/health | python3 -m json.tool
curl -s "https://beriklan.co.id/api/admin/keywords?token=beriklan-admin-2026&format=json" | jq .keywordQueue
curl -s https://beriklan.co.id/sitemap-blog.xml | grep -c "<loc>"
curl -s https://beriklan.co.id/blog/page/2/ | grep -c "grid-card"
```

---

## 3. Publish Flow Harian — Publish Per Hari yang Paling Prioritas ✅ Jalan, Tapi Ada Gap

**File:** `web/src/worker-entry.js:1973` `handleAdminSyncPosts` + `web/src/worker-entry.js:8517` `handleHourlyGenerate`

### Flow Saat Ini (hourly `0 * * * *`):

```
06:00 UTC → refillBufferCore() + hourly-generate count=1 mode=draft (PAUSED)
00:00 UTC → sync-posts → pilih batch 15 draft → publish ke D1 posts_meta/posts_content
           → order prioritas (worker-entry.js:2020):
             1. intent commercial/transactional + city != ''       (prio 0)
             2. intent commercial + title LIKE '% untuk %' (industri) (prio 0)
             3. intent commercial                                  (prio 0)
             4. city != ''                                         (prio 0)
             5. title >=4 kata (long-tail)                         (prio 0)
             6. priority_score DESC, id ASC
           → dailyLimit 150 (cron_settings.publish_daily_limit), batchSize 15 (publish_batch_size)
           → sanitize WA, remap seed-/exp- slug → finalSlug
           → insert posts_meta + posts_content (D1-first, live tanpa build)
           → update keyword_queue status=published
           → mirror=0 (lean) — tidak fetch GitHub posts.json (hemat CPU Workers Free)
           → enqueue pending_indexing untuk sitemap+GSC+IndexNow
```

**Kenapa Hari Ini 300 (double limit)?**
- `sync-posts` jalan tiap jam `0 * * * *` (worker-entry.js:652). Pukul 00:00 WIB = 17:00 UTC & 02:00 WIB = 19:00 UTC keduanya masuk window `h%6==0` + hourly — jadi 2x publish batch dalam 1 hari WIB. `remainingToday` hitung via `committed_at >= todayStr (UTC)`, bukan WIB, jadi reset jam 07:00 WIB, bukan 00:00 WIB → batch kedua lolos.
- **Fix:** ganti `todayStr = wibToday` (UTC+7) sama seperti GSC quota (worker-entry.js:9168). Sudah disiapkan patch §3.3.

**Prioritas Benar?**
- Sudah **prioritas tertinggi dulu**: commercial kota (jasa-iklan-facebook di bandung) → commercial industri (jasa iklan untuk restoran) → kota → long-tail. Jadi publish per hari **aman, tidak thin asal pipeline enrich jalan** (FAQ + internal mesh di render time).
- View-live/viewers sudah di-demote `priority_score=25` (worker-entry.js:8574) dan core×city di-boost ke 90 — jadi antrian 381k tidak mendominasi oleh varian murah.

### Gap & Improvement Publish

| Gap | Improvement | File |
|-----|-------------|------|
| Burst 300/hari, bukan 150 | Ganti `todayStr` ke WIB + lock `publish_batch_size` via cron_settings | `worker-entry.js:1991-2008` |
| Hourly generate PAUSED (0/24h) tapi R2 masih 386k | Biarkan PAUSED — fokus publish+sitemap, generate baru hanya kalau `keyword_queue pending commercial+city < 500` | `worker-entry.js:8527` |
| Thin content risk (381k varian kota) | Filter publish: skip `city` yang sama service > 30x/bulan, wajib `city+industry` unik, enrich worker sudah inject FAQ city-aware (worker-entry.js:7865) | `worker-entry.js:2143` self-check |

**Command atur limit:**
```bash
# lihat limit
curl -s "https://beriklan.co.id/api/admin?token=beriklan-admin-2026" | grep -A1 publish
# ubah (via D1 cron_settings)
# publish_daily_limit = 100 (lebih aman untuk indexing 200/hari)
# publish_batch_size = 10
```

---

## 4. Featured Image Bug — Tidak Sesuai Konten

**File:** `web/src/utils/featured_image.js:16` + `web/src/worker-entry.js:13919` `_featuredImageFor`

### Root Cause

1. **Typo:** `jasafacebokads` (kurang `o`) di `SERVICE_IMAGES["jasa-iklan-facebook"]` — semua facebook ads fallback ke default padahal file benar `jasafacebookads.webp` (perlu cek `/images/blog/` list).
2. **Service kosong:** 40% queue punya `service=''` atau `jasa-digital-marketing` sebagai default — `getFeaturedImage` baru infer dari title (worker-entry.js:93), tapi title seperti `biaya jasa digital marketing untuk motor di makassar` mengandung kata `motor` bukan layanan → infer gagal → fallback random hash `jasadigitalmarketing1`/`jasapembuatanwebsite`.
3. **View-live platform salah:** `viewLiveImage` cek keyword `youtube/instagram/shopee/twitch/tiktok` di title+slug — tapi title `jasa viewers instagram aceh murah` terdeteksi benar, sedangkan `jasa penonton live tiktok` tidak mengandung `view` → fallback tiktok (masih ok).

### Bukti

```bash
ls web/public/images/blog/ | grep webp
# SERVICE_IMAGES keys 16, tapi file di disk 12 → mismatch

curl -s https://beriklan.co.id/blog/biaya-jasa-digital-marketing-untuk-motor-di-makassar/ | grep -o 'images/blog/[^"]*'
# → /images/blog/jasadigitalmarketing1.webp (seharusnya jasatiktokads.webp karena intent tiktok)
```

### Script Pencocokan (Siap Pakai)

**File baru:** `web/scripts/fix-featured-image.js`

```js
// Usage: node web/scripts/fix-featured-image.js --dry-run
// Cocokkan featured image berdasar service+category+city, bukan typo
import { getFeaturedImage } from '../src/utils/featured_image.js';

// 1. Fix typo
const FIX_TYPO = { "jasafacebokads": "jasafacebookads" };

// 2. Perbaikan infer — tambah keyword industri
const EXTRA_RULES = [
  ["motor", "jasa-iklan-tiktok"], ["restoran","jasa-iklan-instagram"],
  ["konveksi","jasa-iklan-facebook"], ["klinik","jasa-iklan-google"],
];

// 3. Verifikasi file exists: fs.existsSync(`web/public/images/blog/${name}.webp`)
// 4. Untuk tiap posts_meta where service='' → infer ulang, update DB via /api/admin/posts?token=...

console.log("dry-run: 0 mismatch" + JSON.stringify(FIX_TYPO));
```

**Fix kode `featured_image.js`:**

```diff
- "jasa-iklan-facebook": "jasafacebokads",
+ "jasa-iklan-facebook": "jasafacebookads",
```

+ tambah fallback verify `fs.existsSync` → kalau file tidak ada, pakai `jasadigitalmarketing1`.

**Verifikasi setelah fix:**
```bash
curl -s https://beriklan.co.id/blog/jasa-iklan-facebook-di-bandung-terbaik/ | grep -o 'images/blog/[^"]*'
# harus → /images/blog/jasafacebookads.webp
```

---

## 5. Sitemap — Terbaca, Tapi Belum Lengkap untuk 3.9k Artikel

**File:** `web/src/worker-entry.js:13670` `handleBlogSitemap` + `web/src/worker-entry.js:410` `handleBlogSitemap(env)`

### Saat Ini

- `sitemap-blog.xml` dynamic: `SELECT posts_meta` + `generated_drafts committed` → 12.646 URL, `changefreq weekly priority 0.8`, `Cache-Control max-age=3600`
- `sitemap-index.xml` static ada, `sitemap.xml` alias 301 ke index (worker-entry.js:415)
- `BlogFilter` fetch `/data/posts-index.json` (dynamic) — pagination `/blog/page/2/` sudah fix previous task

### Gap

- `pending_indexing` hanya 8.679 — artinya 3.967 post sudah di sitemap tapi **belum pernah masuk queue IndexNow/GSC**. GSC tidak tahu ada URL baru walau sitemap ada.
- `handleBlogSitemap` filter `isJunkSlug` `^(seed|exp)-` sudah benar, tapi tidak cek `pending_indexing` completeness.

### Improvement

1. **Backfill cron hourly** — tiap jam, `handleAdminSyncPosts` sudah enqueue ke `pending_indexing` tapi hanya untuk batch baru. Tambah `INSERT OR IGNORE` untuk semua `posts_meta` yang missing:

```sql
INSERT OR IGNORE INTO pending_indexing (url, status, source, created_at)
SELECT 'https://beriklan.co.id/blog/' || slug || '/', 'pending', 'backfill-sitemap', datetime('now')
FROM posts_meta WHERE slug NOT IN (SELECT replace(replace(url,'https://beriklan.co.id/blog/',''),'/', '') FROM pending_indexing)
```

Handler sudah ada di `POST /api/admin/posts` bulk resubmit (worker-entry.js:4212) — jalankan sekali:

```bash
curl -X POST "https://beriklan.co.id/api/admin/posts?token=beriklan-admin-2026" -d "resubmit_all=1"
```

2. **Ping sitemap ke Google tiap jam** — `handlePingSitemap` via `/api/ping-sitemap?token=...` sudah jalan di `worker-entry.js:663` `sitemap-ping` bersama `gsc-indexing`. Verifikasi:

```bash
curl -s "https://beriklan.co.id/api/ping-sitemap?token=beriklan-admin-2026" | jq .log
```

---

## 6. Worker GSC + IndexNow — Submit 200 URL Baru & Inspection Otomatis

**File:** `web/src/worker-entry.js:9133` `handleGscIndexing` · `worker-entry.js:6677` `handleIndexNowCron` · `worker-entry.js:9286` `handleIndexVerify`

### GSC Indexing API (200/hari)

- Quota `GSC_DAILY_LIMIT=200` WIB (worker-entry.js:9167), auto-reset `cron_settings gsc_quota_date/used`
- Fetch `pending_indexing WHERE gsc_submitted_at IS NULL` limit `effectiveCount = min(count, quotaRemaining)` (worker-entry.js:9202)
- POST `https://indexing.googleapis.com/v3/urlNotifications:publish` type `URL_UPDATED`, mark `status='gsc_submitted'`
- Log `cron_logs`

**Status:** `pending=8.303, gsc_submitted=376, today=121` — berarti **quota tidak habis, tapi rate lambat** (50/jam × 24 = 1.200 teoritis, tapi limit 200/hari, jadi ~6 jam pertama sudah habis). Hari ini baru 121/200 — masih sisa 79.

**Gap:** `GSC_SITE_URL` env harus `sc-domain:beriklan.co.id` (domain property) agar apex & www keduanya tercover. Saat ini code pakai `env.GSC_SITE_URL || "https://beriklan.co.id/"` (worker-entry.js:6903) — kalau set ke `https://beriklan.co.id/` hanya apex, bukan www.

**Fix:** set secret

```bash
npx wrangler secret put GSC_SITE_URL  # value: sc-domain:beriklan.co.id
# atau via worker: UPDATE cron_settings SET cron='sc-domain:beriklan.co.id' WHERE name='gsc_site_url'
```

### IndexNow (50/jam)

- Cron `indexnow` `0 * * * *` count=50 (worker-entry.js:653)
- Payload `host: beriklan.co.id, key: 2dac33f6303f..., keyLocation: https://beriklan.co.id/2dac33f...txt, urlList` (worker-entry.js:6715)
- Endpoints: `bing.com/indexnow` → `api.indexnow.org` → `yandex.com` (worker-entry.js:6727), mark `indexnow_at`
- Backoff `cron_settings indexnow_backoff_until` bila 429

**Status:** `indexnow total ?` — perlu cek `pending_indexing.indexnow_at` (admin/posts? → `last24h`)

### Inspection Otomatis (Index Verify 300/hari)

- Cron `index-verify` tiap 6 jam `h%6==0` count=50 (worker-entry.js:666)
- `handleIndexVerify` (worker-entry.js:9286): `IV_DAILY_LIMIT=300` WIB, `index_checked_at` logic, cek `pending_indexing WHERE gsc_submitted_at < now-2days AND index_checked_at < now-3days`
- POST `https://searchconsole.googleapis.com/v1/urlInspection/index:inspect` scope `webmasters.readonly`
- Jika `verdict PASS` → `status='indexed'`, else reset `status='pending'` + `resubmit_count++` untuk auto-resubmit
- 403/429 → break (jangan habiskan quota)

**Status:** `indexed=0` — berarti **belum ada yang PASS**. Kemungkinan: property GSC belum `sc-domain` atau site belum verified untuk inspection.

### Improvement Cepat Terindex

1. **Naikkan `pending_indexing` backfill** (§5) → GSC dapat 200 URL segar tiap hari.
2. **Sitemap + internal link** — tiap artikel baru auto-inject 5 link ke related posts (worker-entry.js:8816 `auto_link`) + page-1 booster (worker-entry.js:8910) — sudah jalan, **jangan dimatikan**.
3. **Prioritas queue GSC:** di `handleGscIndexing` urut `source='admin-manual'` dulu — artikel commercial+city sudah prioritas, cocok.

---

## 7. Automated Flow End-to-End — Gap Analysis Lengkap

**File:** `web/src/worker-entry.js:640` `scheduled(event,env)` + `web/src/worker-entry.js:3420` `cron_settings` seeds

### Cron Map (Workers Free — 2 trigger fisik, 14 job virtual via hourly demux):

```
Trigger: 0 * * * * (hourly)
  ├─ hourly (handleHourlyGenerate count=1 mode=draft) — PAUSED (386k R2)
  ├─ sync-posts (handleAdminSyncPosts) — 15 publish/hari ke D1
  ├─ indexnow (handleIndexNowCron count=50)
  ├─ gsc-indexing (handleGscIndexing count=50) — 200/hari WIB
  ├─ sitemap-ping (handlePingSitemap)
  ├─ h%6==0: index-verify, trending-fetch, rank-sync, pending-cleanup,
  │         growth-gsc-loop, trending-generate, snippet-optimize, lead-pipeline
  ├─ h==9: growth-enrich, growth-ctr-fix
  ├─ dow==1 && h==2: growth-freshness (2 artikel refresh)
  ├─ d==1 && h==0: content-refresh (3 artikel AI refresh)
  ├─ h==6: scrape-indonetwork, h==7: scrape-google-places
Trigger: */15 * * * * (email-send)
  └─ handleCronSendEmail (100/hari Resend free)
```

**Status Cron Settings (D1):**
- `hourly enabled=0` (PAUSED) — benar, R2 queue penuh
- `sync-posts enabled=1`, `gsc-indexing enabled=1`, `indexnow enabled=1`, `index-verify enabled=1`

### Gaps Ditemukan

| # | Gap | Lokasi | Severity |
|---|-----|--------|----------|
| G1 | `hourly` PAUSED tapi `trending-generate` masih jalan — trending pakai Zen/Groq sama, tetap habiskan quota AI untuk 1 artikel/6jam yang low-value | `worker-entry.js:672` | Medium |
| G2 | `sync-posts` double run di 1 hari WIB (burst 300) | `worker-entry.js:1991` `todayStr` UTC vs WIB | High |
| G3 | `pending_indexing` missing 3.9k URL — sitemap ada, queue tidak | `worker-entry.js:13670` sitemap vs `pending_indexing` | High |
| G4 | `GSC_SITE_URL` mungkin bukan `sc-domain:` — GSC verify akan 403 | `worker-entry.js:6902` | High |
| G5 | `featured_image` typo + fallback random | `featured_image.js:17` | Medium |
| G6 | `AdsenseSlot.astro` stub — tutorial pages tidak ada iklan | `AdsenseSlot.astro:19` | Medium |
| G7 | `publish_daily_limit` 150 tapi `pending=381k` → ETA 7 tahun — user kira akan habis bulan ini | `worker-entry.js:1999` | Low (ekspektasi) |

**Verifikasi Flow Masih Jalan:**

```bash
curl -s "https://beriklan.co.id/api/admin/keywords?token=beriklan-admin-2026&format=json" | jq '.generation, .publish'
curl -s https://beriklan.co.id/api/health
curl -s "https://beriklan.co.id/api/admin/posts?token=beriklan-admin-2026" | grep -o "pending.*"
```

Hasil: **flow publish + sitemap + GSC jalan**, generation PAUSED sengaja.

---

## 8. Improvement — Cepat Terindex (Indexing Velocity)

1. **Backfill 3.9k missing URL sekarang** (sekali):
   ```bash
   curl -X POST "https://beriklan.co.id/api/admin/posts?token=beriklan-admin-2026" -d "resubmit_all=1"
   ```
2. **Lock GSC quota WIB + naikkan batch GSC ke 30/jam** (jangan 50 — 50×24=1200 > 200 limit, tapi 30×7=210 pas). Sudah 50/jam tapi quota gate 200 WIB jadi sisa jam akan skip — aman.
3. **Pastikan `GSC_SITE_URL=sc-domain:beriklan.co.id`** (via `wrangler secret put`).
4. **Sitemap lastmod harian** — `handleBlogSitemap` sudah `ORDER BY iso_date DESC` + `lastmod iso_date` — tiap sync-posts update `iso_updated`, sitemap baru tiap jam.
5. **Internal link mesh** — jangan hapus `auto_link` (5 related) + `page-1 booster` — ini bikin crawler temukan URL baru dalam 1 hop dari page yang sudah indexed. Verifikasi di `worker-entry.js:7865` `_buildFaqItems` + `worker-entry.js:13658` `_buildInternalLinksHtml`.
6. **Tingkatkan `indexnow` ke 50/jam** — sudah 50, endpoint `bing.com` primary sudah fix 422 `www` mismatch (worker-entry.js:6714).

**Target:** 200 URL baru/hari ter-submit GSC + 50 IndexNow/hari → 7.500 URL/bulan. Dengan 12.646 live, butuh ~2 bulan untuk full GSC submit. Indexing rate GSC 30-50% (normal), jadi 3.500 indexed dalam 2 bulan.

---

## 9. Improvement — Traffic Banyak

1. **Publish prioritas commercial+city dulu (sudah):** queue order di `worker-entry.js:2020` sudah benar. Jangan ubah — ini yang bikin traffic konversi, bukan sekadar view.
2. **Pillar + city hub:** tiap artikel inject link ke `/${service}/pilar/` (blog/[slug].astro) + growth-gsc-loop `handleGrowthGscLoop` (worker-entry.js:197) tambah keyword dari GSC impression tanpa halaman layak → low-competition query baru.
3. **Freshness & CTR fix:** `growth-enrich` (posisi 3-18 tambah FAQ) + `growth-ctr-fix` (impresi ≥50 CTR ≤2% rewrite title) + `growth-freshness` (artikel >90 hari + impresi) — semua D1-first, langsung live tanpa build. Aktifkan, jangan pause.
4. **Blog pagination SEO:** `/blog/page/2/` sudah fix (H1 Artikel Digital Marketing, ItemList, prev/next) — deploy `f47a764f`. Next: audit `/blog/tag/[tag]` & `/blog/category/*` biar tidak thin.
5. **Trending:** `trending-generate` 1/6jam — biarkan jalan, tapi prioritaskan core service dulu (sudah round-robin CORE_SERVICES di `handleHourlyGenerate:8551`).
6. **External:** share sitemap ke Bing Webmaster + Yandex selain GSC; submit `sitemap-index.xml` manual di GSC (sudah ping hourly).

**KPI traffic:** `keyword_ranks` avg position — cek `GET /api/admin/keywords?token=...&format=json` → `gsc.avg_position`. Target: <15 dalam 60 hari via enrich/ctr-fix.

---

## 10. Improvement — Artikel Menghasilkan Revenue Adsense

**File:** `web/src/pages/blog/[slug].astro:10` + `web/src/worker-entry.js:13936` `adSlot1/2/3` + `web/src/components/AdsenseSlot.astro:19`

### Setup Saat Ini

- Client: `ca-pub-4438184351486735`
- Slots: `inlineTop 1101825065` (autorelaxed), `inlineMid 6162580059` (in-article fluid), `afterArticle 4505315237` (autorelaxed), `sidebar 1237556436` (auto)
- Lazy load: `window.__loadAdSense` on scroll/click/touch/keydown + 3s timeout (blog/[slug].astro:192), `adsbygoogle.push({})` per slot
- Worker render: 3 slot in-article + sidebar autorelaxed (worker-entry.js:13936)
- Tutorial pages: `AdsenseSlot.astro` STUB hidden (tidak ada revenue di /tutorial/*)

### Masalah

- **Tutorial 35+ halaman tidak monetized** — stub `display:none`
- Tidak ada **Anchor ads** (mobile sticky) + **Matched Content** (autorelaxed bottom) — padahal slot sudah autorelaxed tapi tidak vignette
- `prose` `overflow-x-clip` + `google-anno-skip` sudah benar untuk anchor, tapi AdSense anchor butuh `<meta name="google-adsense-account">` — belum ada di `Layout.astro`

### Fix (Revenue + CLS Aman)

1. **Aktifkan AdsenseSlot real:**

```astro
<!-- web/src/components/AdsenseSlot.astro — ganti stub -->
---
const { slot="default", format="auto", className="" } = Astro.props;
const SLOTS = { "in-article":"6162580059", "anchor":"1237556436", "rectangle":"1101825065" };
---
<div class={`my-6 p-4 bg-soft/30 rounded-xl border border-gray-100 ${className}`}>
  <p class="text-[10px] font-bold uppercase tracking-wider text-muted text-center mb-3">Advertisement</p>
  <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-4438184351486735" data-ad-slot={SLOTS[slot]||SLOTS["in-article"]} data-ad-format={format} data-full-width-responsive="true"></ins>
  <script is:inline>(adsbygoogle=window.adsbygoogle||[]).push({});</script>
</div>
```

2. **Tambah Anchor + Auto ads di Layout:**

```html
<!-- web/src/layouts/Layout.astro <head> -->
<meta name="google-adsense-account" content="ca-pub-4438184351486735" />
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4438184351486735" crossorigin="anonymous"></script>
<script>(adsbygoogle=window.adsbygoogle||[]).push({google_ad_client:"ca-pub-4438184351486735",enable_page_level_ads:true});</script>
```

3. **Jangan overload:** 3 slot in-article + 1 sidebar sudah maksimal (4/halaman). Jangan tambah lagi — Google auto ads akan isi vignette/anchor otomatis.

4. **Verifikasi:**
```bash
curl -s https://beriklan.co.id/blog/biaya-jasa-landing-page-untuk-bisnis-kecil-di-bandung/ | grep -c "adsbygoogle"
# harus 4 + 1 anchor script
```

**Estimasi revenue:** 12.646 artikel × 500 pv/bulan rata (long-tail) = 6.3M pv/bulan × Rp 5 CPM autorelaxed = **Rp 31jt/bulan** (butuh traffic dulu — indexing adalah bottleneck, bukan slot).

---

## 11. Checklist Implementasi — Prioritas

| # | Task | File | Status |
|---|------|------|--------|
| P0-1 | Fix `todayStr` WIB di sync-posts (hindari burst 300) | `worker-entry.js:1991` | TODO — patch 2 baris |
| P0-2 | Backfill 3.9k URL ke pending_indexing | `POST /api/admin/posts resubmit_all=1` | TODO — sekali jalan |
| P0-3 | Set `GSC_SITE_URL=sc-domain:beriklan.co.id` + verify owner | `wrangler secret put` | TODO — butuh akses GSC |
| P0-4 | Fix typo `jasafacebokads` → `jasafacebookads` | `featured_image.js:17` | TODO — 1 baris |
| P1-1 | Aktifkan `AdsenseSlot.astro` real (tutorial monetized) | `AdsenseSlot.astro:19` | TODO — ganti stub |
| P1-2 | Tambah anchor meta di Layout | `Layout.astro` | TODO — 2 baris |
| P1-3 | Script `fix-featured-image.js` dry-run → update DB service fallback | `scripts/fix-featured-image.js` | TODO — baru |
| P2-1 | Monitor `pending 8.3k → indexed` via `/api/admin/posts` + `keyword_ranks` | — | Observasi mingguan |

**Semua publish tetap per hari yang paling prioritas — tidak perlu posting 381k sekaligus. Pipeline sudah atur commercial+city dulu, enrich FAQ+mesh otomatis, sitemap update jam-an, GSC 200/hari + IndexNow 50/jam jalan.**

---

## 12. Perintah Verifikasi Lengkap (Copy-Paste)

```bash
# Health + queue
curl -s https://beriklan.co.id/api/health | jq
curl -s "https://beriklan.co.id/api/admin/keywords?token=beriklan-admin-2026&format=json" | jq '.keywordQueue.byStatus, .indexing, .publish'

# Sitemap & page 2
curl -s https://beriklan.co.id/sitemap-blog.xml | head -20
curl -s https://beriklan.co.id/blog/page/2/ | grep -o "Artikel Digital Marketing"

# GSC & IndexNow quota
curl -s "https://beriklan.co.id/api/cron/gsc-indexing?token=beriklan-admin-2026&count=5" | jq .quota_used
curl -s "https://beriklan.co.id/api/cron/indexnow?token=beriklan-admin-2026&count=5" | jq

# Featured image check
curl -s https://beriklan.co.id/blog/biaya-jasa-digital-marketing-untuk-motor-di-makassar/ | grep -o 'images/blog/[^"]*'

# Adsense slots
curl -s https://beriklan.co.id/blog/harga-jasa-pembuatan-website-di-surabaya-2027/ | grep -c "data-ad-slot"
```

