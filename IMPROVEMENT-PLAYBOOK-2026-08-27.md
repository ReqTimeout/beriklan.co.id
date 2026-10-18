# Beriklan.co.id ↔ Beriklan.my — Master Improvement Playbook

> Snapshot semua improvement yang sudah di-deploy ke `beriklan.co.id` (via
> `beriklanweb` worker) per 27 Agustus 2026. Tujuan: panduan replikasi ke
> `beriklan.my` (via `beriklanmy` worker) + audit gap.

---

## A. Blog Rendering Architecture

| # | Improvement | File / Handler | Dampak |
|---|---|---|---|
| A1 | **Worker D1-first blog index** (`/blog/`, `/blog/page/N/`, `/blog/category/<cat>/`) | `worker-entry.js:renderBlogIndex` | Single source of truth dari D1 `posts_meta` (12.676 artikel) — bukan static build. Hapus inkonsistensi `/blog/` (24 post) vs `/blog/page/N/` (4.306 post). |
| A2 | **Chrome islands only** (filter Navbar/StickyCTA/FloatingWhatsApp/CookieBanner) — JANGAN inject HeroVisual/PainPoints/Services | `_getBlogTpl` + `_injectPageExtras` | Tanpa filter, blog index muncul mockup dashboard homepage (bug visual fatal). |
| A3 | **bodyPre injection** (Astro hydration scripts: `astro-island{display:contents}` + `Astro.only` + renderer) | `_getBlogTpl` (capture) + `_injectPageExtras` (inject) | Tanpa bodyPre, `<astro-island>` tetap HTMLUnknownElement → navbar tidak pernah hydrate → TagError "Y". |
| A4 | **AdSense head script injection** | `_injectPageExtras` | Template reference `/` (homepage) tidak punya showAdsense → single post ads tidak load. Sekarang inject `pagead2.googlesyndication.com` ke head. |

---

## B. Featured Image Logic (Paling Penting!)

| # | Improvement | File | Dampak |
|---|---|---|---|
| B1 | **`_featuredImageFor` category-first** | `worker-entry.js:11382+` | Kalau `category` di posts_meta match `SVC_IMG` → pakai itu. Tanpa ini, artikel "Jasa View Live..." dengan `service=jasa-iklan-tiktok` di-DB keluar image TikTok Ads (salah). Sekarang: category menang. |
| B2 | **`_resolveCategory(service, title, fallback)` di publish flow** | `worker-entry.js:11375+` | Sync-posts INSERT pakai resolver: `inferred > service` berdasarkan SPECIFICITY. Article baru auto-kategori benar. |
| B3 | **Inference rules dengan ordering spesifik → umum** | `_inferSvcFromTitle` (worker + utils) | Aturan disusun paling spesifik (landing page → 5, website → 4, paid ads → 3, organic → 2, dm → 1, view-live → 0). Rule "ads → google" generik DIBUANG (greedy). |
| B4 | **SVC_IMG expansion** (+12 service) | worker + utils | Tambah: `jasa-view-live-tiktok/youtube/instagram/shopee/twitch`, `jasa-buzzer*`, `jasa-viewers-*`. |
| B5 | **File content swap fix** (rename `jasapembuatanwebsite.webp` ↔ `jasaviewlivetiktok.webp`) | `public/images/blog/` | 2 file konten-nya tertukar dari upload awal. Sekarang landing page article tampil image landing page (bukan TikTok Live). |
| B6 | **Mandatory: verify file content vs filename** | (workflow) | Buka file sebelum pakai. Map nama → konten harus cocok. |

---

## C. Category System

| # | Improvement | Dampak |
|---|---|---|
| C1 | **Recategorize migration** (UPDATE `posts_meta.category` by title inference) | 8.487 artikel tadinya `jasa-iklan-tiktok` (salah) → 862 jadi `jasa-pembuatan-landing-page`, 776 jadi `jasa-iklan-youtube`, dll. |
| C2 | **BLOG_CAT_META** (label rapi per slug) | 30 kategori punya label: Facebook Ads, Live TikTok, Live YouTube, Buzzer Live, Kelola Instagram, dll. |
| C3 | **Subkategori view-live per platform** | `jasa-view-live-tiktok`, `jasa-view-live-youtube`, `jasa-view-live-instagram`, `jasa-view-live-shopee`, `jasa-view-live-twitch`. Masing-masing punya image sendiri. |
| C4 | **Jasa Buzzer** (branding alternatif) | `jasa-buzzer` + 5 platform-specific. URL Navbar tetap `/jasa-view-live/<platform>`, tapi kategori internal bisa `jasa-buzzer-*` sesuai judul. |
| C5 | **Chip filter blog lengkap** | 15 chip dengan label rapi (sebelumnya 2 keluar slug mentah). |
| C6 | **Single-post sidebar** +6 link Live TikTok/YouTube/Instagram/Shopee + Buzzer Live | Internal linking dari artikel ke kategori spesifik. |

---

## D. SEO / Indexing

| # | Improvement | Endpoint / Cron | Dampak |
|---|---|---|---|
| D1 | **news.xml (Google News sitemap)** | `/news.xml` (worker dynamic) | 1.000 URL freshest per file × 13 halaman = 12.756 URL. Include `<news:image>`, `<news:keywords>`, `<news:genres>Blog</news:genres>`. Pagination `?page=N`. Submit ke Bing Webmaster (manual) + (opsional) Google Publisher Center. |
| D2 | **News ping cron** | `GET /api/cron/news/ping?token=...` | Submit freshest 100 ke IndexNow. Tiap 2 jam (`h%2===0`). |
| D3 | **Multi-channel distribute** | `GET /api/cron/distribute?token=...&limit=30` | Tiap 3 jam (`h%3===0`). Share ke IndexNow + (optional) Telegram + generic webhook (Buffer/IFTTT/Zapier). Mark `posts_meta.last_distributed_at` supaya tidak duplikat. |
| D4 | **Env vars** (opsional) | `DISTRIBUTE_WEBHOOK`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL_ID` | Set via `wrangler secret put`. Tanpa env: hanya IndexNow yang aktif (default). |
| D5 | **Growth loops** (sudah ada sebelumnya) | `growth-gsc-loop`, `growth-enrich`, `growth-ctr-fix`, `growth-freshness` | Tangkap long-tail query GSC → keyword_queue. Enrich intro+FAQ. Rewrite SERP untuk CTR. Refresh badge. |

---

## E. AdSense / Monetization

| # | Improvement | Dampak |
|---|---|---|
| E1 | **AdSense head script injection** di single post + blog index | Sebelumnya head tidak punya script → ads blank. |
| E2 | **AdSense slot layout** (4 slot per post: in-feed top, in-article, in-article bottom, sidebar) | Layout polisensi ads. |
| E3 | **showAdsense prop** di Layout.astro | True di `blog/[slug].astro` + `blog/tag/[tag].astro`. False di home/service/order. |
| E4 | **Auto-ads on by default** (Anchor + Vignette + Matched content) | Enable di AdSense dashboard, +20-40% CTR mobile. |

---

## F. Anti-Spam / Indexing Quality

| # | Improvement | Dampak |
|---|---|---|
| F1 | **WIB burst fix** | `wibTodayStr` di worker-entry.js (UTC+7) — avoid double-publish saat UTC midnight rollover. |
| F2 | **Fix 404 internal links** (`fixBrokenInternalLinks` di render-time + 6 redirect rules di `_redirects`) | Mis. `/blog/cara-jualan-di-shopee-depok/` link `/social-media-management/` → redirect ke `/jasa-kelola-instagram/`. |
| F3 | **Cleanup junk slug** | `DELETE FROM pending_indexing WHERE url LIKE '%/blog/seed-%' OR url LIKE '%/blog/exp-%'`. |
| F4 | **WA number sanitization** | Replace placeholder AI `6281234567890` → `62811919328` di semua posts_content. |
| F5 | **Lean mirror gate** di sync-posts | `?mirror=0` (default): tidak fetch posts.json, tidak PUT ke GitHub. Aman dari `1102` CPU limit. `?mirror=1` (manual): full mirror ke dist/. |

---

## G. Operational / Docs

| # | File | Fungsi |
|---|---|---|
| G1 | `web/AGENTS.md §9.1` | Worker Blog Template — lesson learned JANGAN diulang. |
| G2 | `web/AGENTS.md §9.2` | Featured image file content verification. |
| G3 | `TRAFFIC-BOOST-STRATEGY-2026-08-27.md` | Strategi boost AdSense (Bing Webmaster, Pinterest, Medium, dll). |
| G4 | `AUDIT-FLOW-INDEXING-ADSENSE-2026-08-27.md` (root) | Audit flow indexing + AdSense per 27 Agt 2026. |

---

## H. Worker Cron State (beriklanweb)

| Cron | Schedule | Status |
|---|---|---|
| `hourly` | `0 * * * *` | ✅ Sync-posts + IndexNow + GSC + sitemap-ping + push-rank + (h%2) news-ping + (h%3) distribute + (h%6) growth loops |
| `email-send` | `*/15 * * * *` | ✅ Resend 25/batch (max 100/hari) |

---

## I. Yang BELUM di .com (TODO future)

- [ ] Auto-generate artikel baru tiap jam (hourly generate, paused sejak 27 Agt)
- [ ] Pinterest auto-pin (perlu OAuth setup manual)
- [ ] Medium canonical repost (perlu akun Medium + manual setup)
- [ ] Backlink outreach automation
- [ ] Auto-translate content ke bahasa lain (multi-region)
- [ ] Yandex Metrica integration (saat ini Bing Webmaster via IndexNow)

---

## J. Deploy History

| Version | Tanggal | Major Change |
|---|---|---|
| `bdf133f6` | 26 Agt | Backup rollback |
| `e969d14a` | 27 Agt 00:51 | news.xml expand 10 → 1000, news-ping + distribute |
| `a64bc7b1` | 27 Agt 01:11 | Cron news-ping h%2, distribute h%3 |
| `5901b6be` | 27 Agt 01:21 | View-live platform + buzzer categories |
| `6a15e70f` | 27 Agt 01:30 | BLOG_CAT_META full label rapi |

Stable rollback: `bdf133f6-9892-47b6-a485-a5d1bbfca0aa`
