# Beriklan SEO Full Domination — Complete Plan (with Wireframes)

## 🎯 Tujuan Utama (2 sasaran SEJAJAR)
1. **Ranking #1** semua keyword layanan + kota + industri di Google + menang **AI Overviews**.
2. **Boost pendapatan AdSense** (`ca-pub-4438184351486735`) — makin banyak halaman ter-index + traffic informational → impresi & RPM naik.

> Semua keputusan (keyword, konten, indexing, link) diarahkan ke 2 sasaran ini sekaligus. Traffic informational = mesin AdSense; keyword komersial = lead WhatsApp.

## Business Context (Verified from Codebase)

| Dimension | Detail |
|-----------|--------|
| **Brand** | Beriklan.co.id — "Senior Performance Marketing Partner", sejak 2016, Bandung (Jl. Arcamanik Endah No.76) |
| **Voice** | Formal-measured Indonesia, "Anda" predominant, industry terms English (ROAS/CPA/funnel) dijelaskan; NO slang, NO overclaim |
| **Target** | UMKM & bisnis menengah, budget iklan Rp 5jt–50jt/bulan |
| **11 Lini Layanan** | Digital Marketing, Facebook Ads, Instagram Ads, TikTok Ads, Google Ads, YouTube Ads, Kelola IG, Kelola TikTok, Pembuatan Website, Landing Page, **+ View Live (lini terpisah, 5 platform)** |
| **25 Kota** | jakarta, bandung, surabaya, medan, semarang, makassar, palembang, tangerang, depok, bekasi, bogor, batam, pekanbaru, denpasar, yogyakarta, malang, solo, balikpapan, samarinda, pontianak, banjarmasin, manado, padang, sidoarjo (+jakarta variants) |
| **Konversi** | Lead-gen via WhatsApp (wa.me/62811919328), hubungi kami untuk konsultasi |
| **Monetisasi** | AdSense `ca-pub-4438184351486735` (lazy-load) — slot in-article di **city pages** (slot 6162580059), homepage, blog. **Traffic = mesin AdSense.** |
| **City pages** | Tiap layanan × 25 kota pakai `CityContentBlock.astro`: LocalBusiness schema + AdSense in-article + internal link (pillar + related cities) |
| **Harga pages** | Tiap `/jasa-*/` punya `PricingCards` (tier + harga nyata) — target keyword komersial "harga/biaya/paket [layanan] [kota]" |

### ⚠️ Angka Aktual (Koreksi Penting — sudah diverifikasi ulang)
| Metrik | Nilai Nyata Sekarang |
|--------|----------------------|
| **Worker aktif yang ter-deploy** | `web/src/worker-entry.js` (**9.708 baris**) — BUKAN root `src/` (5.075 baris, stale). Commit terbaru ada di folder `web/` (23 Jul: "tambah 2 cron baru"). |
| Cron triggers aktif (`web/wrangler.jsonc`) | **11 cron** (bukan 5) |
| Throughput hourly-generate | **3 artikel/jam = 72/hari** (cron `count=3`, max 5) |
| Blog posts sudah live (`web/src/data/posts.json`) | **1.966 artikel** |
| Halaman `.astro` statis | **430** (10 layanan × 26 [1+25 kota] + view-live 136 + core) |
| Keyword-queue.json saat ini | **100 keyword** (97 pending, 3 has_post) |
| Base keywords (`keywords.json`) | **1.478** |
| Tabel D1 `generated_drafts` | **SUDAH ADA** (dibuat di `handleHourlyGenerate`) — tinggal dipakai sebagai buffer publish |
| Sistem email (Resend + retry + drip) | **SUDAH ADA & jalan** — lihat §Email Retry System |
| **Kesimpulan** | Queue harus di-**expand** dulu via miner+expand. "29K" adalah potensi teoretis, bukan antrean aktual. |

---

## System Wireframe — CURRENT (Apa yang Ada Sekarang)

```
        LOCAL (Python scripts)          CLOUDFLARE WORKER — web/src/worker-entry.js (9.708 baris)
┌──────────────────────────┐      ┌──────────────────────────────────────────────────┐
│ keyword_miner.py +       │      │  11 CRON TRIGGERS (web/wrangler.jsonc)             │
│ expand_keywords.py       │      │  ├ 0 * * * *    → hourly-generate (3 artikel/jam)  │
│  11 svc × 26 kota ×      │      │  ├ 15 * * * *   → IndexNow (50 URL)                │
│  intent matrix           │      │  ├ 0 */6 * * *  → GSC index50 + trending + rank    │
│  → keyword-queue.json    │      │  ├ 30 */6       → trending-generate (1)            │
│    (SAAT INI 100 kw)     │      │  ├ 0 0 1 * *    → content-refresh (3 lama)         │
└───────────┬──────────────┘      │  ├ 0 0 * * 1    → snippet-optimize (3)             │
            │ commit                │  ├ 30 6 * * *   → scrape Indonetwork               │
            ▼                       │  ├ 0 7 * * *    → scrape Google Places             │
┌──────────────────────────┐      │  ├ */15 * * * * → email-send (batch 25, Resend)    │
│  GitHub repo             │◄─────┤  ├ 0 1 * * *    → sync D1 → posts.json (commit)    │
│  ReqTimeout/beriklan     │commit │  └ 0 3 * * *    → seed-keywords (all svc, harian)  │
│  src/data/posts.json     │(LIVE) │                                                    │
└───────────┬──────────────┘      │  AI: Zen(deepseek-v4-flash-free) → Groq (5 key)    │
            │ push trigger          │  D1: generated_drafts (SUDAH ADA) · email_queue    │
            ▼                       │      cron_retry_queue (backoff) · cron_settings    │
┌──────────────────────────┐      │  EMAIL: Resend 100/hari, kuota habis → lanjut besok│
│  CF Workers Build        │      │  RETRY: gagal 3× → auto-pause + email alert admin  │
│  npm build → dist/ ASSETS│      │  INDEX: GSC API 200/hari + IndexNow · RANK → D1    │
└──────────────────────────┘      └──────────────────────────────────────────────────┘
```

**3 Masalah utama:** (1) throughput 72/hari (3 art/jam) untuk isi ~12K keyword masih lambat; (2) `hourly-generate` commit LANGSUNG ke `posts.json` (artikel live seketika) — tabel `generated_drafts` sudah ada tapi belum dipakai sebagai buffer publish bertahap → risiko spam saat mass-generate; (3) Batch4 & City-enrich (script lokal) belum pakai Zen (buang provider gratis).

---

## System Wireframe — PROPOSED (Target Akhir)

```
PHASE 1 — KEYWORD EXPANSION (jalankan miner + layer industri)
┌──────────────────────────────────────────────────────────────────────┐
│ keyword_miner.py --all  +  expand_keywords.py  +  LAYER INDUSTRI BARU  │
│                                                                        │
│  Base:       10 layanan × 25 kota × 20 template     ≈ 5.000            │
│  + Industri: 9 industri × 10 layanan                = 90               │
│  + Ind×Kota: 9 industri × 25 kota (layanan utama)   ≈ 1.125           │
│  + Question: apa/bagaimana/berapa/kenapa × svc×kota ≈ 3.000           │
│  + Compare:  A vs B (facebook vs google, dst)       ≈ 1.500           │
│  + Pain:     boncos/rugi/tidak closing × svc        ≈ 1.500           │
│  ─────────────────────────────────────────────────────────           │
│  TARGET QUEUE: ~12.000 keyword unik (dedupe vs 1.966 post existing)   │
│  Output: keyword-queue.json (priority_score ranked)                   │
└───────────────────────────────┬────────────────────────────────────────┘
                                ▼
PHASE 2 — BULK GENERATE (cepat, TIDAK langsung publish)
┌──────────────────────────────────────────────────────────────────────┐
│ scripts/bulk_generate_all.py (BARU) — orkestrasi dari lokal           │
│   loop → POST Worker /api/cron/hourly-generate?count=5&mode=draft     │
│   AI: Zen (gratis unlimited) → Groq fallback                          │
│   Simpan ke D1 `generated_drafts` (BUKAN posts.json)                  │
│   Policy filter + topic guard sebelum & sesudah generate              │
│   Target: 500–1000 artikel/hari → ~12K selesai dalam 2–4 minggu       │
└───────────────────────────────┬────────────────────────────────────────┘
                                ▼
PHASE 3 — PUBLISH QUEUE (BARU — rilis bertahap, anti-spam)
┌──────────────────────────────────────────────────────────────────────┐
│ Cron harian: D1 generated_drafts → posts.json (GitHub) → CF Build      │
│   Minggu 1: 10/hari  → Minggu 2: 20  → Minggu 3: 30  → Minggu 4+: 50  │
│   Tiap publish: mark has_post, update posts-index, auto-link 5 related │
│   + enqueue D1 pending_indexing                                        │
└───────────────────────────────┬────────────────────────────────────────┘
                                ▼
PHASE 4 — GRADUAL INDEXING + MONITORING
┌──────────────────────────────────────────────────────────────────────┐
│ GSC Indexing API: ramp 20→50→100→200/hari                             │
│ IndexNow: batch 50 URL + jeda                                          │
│ Monitor GSC crawl stats → jika crawl turun, perlambat publish          │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Jawaban Strategi Publish (Konfirmasi Anda BENAR)

**Anda benar.** Strategi: **generate semua dulu (simpan draft) → publish harian bertahap**.

| Opsi | Risiko |
|------|--------|
| Generate + submit semua sekaligus | Google lihat ribuan halaman baru dalam semalam → **sinyal spam**, risiko sandbox / crawl throttle |
| ✅ Generate semua (draft) → publish 10→50/hari | Pola pertumbuhan natural untuk domain 9 tahun → **aman**, crawl budget naik stabil |

Ini yang dipakai di plan (Phase 2 = generate cepat ke draft; Phase 3 = rilis harian bertahap).

---

## Layer Industri (Ekspansi ke Semua Halaman — Disetujui)

**9 Industri (untuk lini Ads / Social / Web):** E-commerce/Online Shop · Properti · Pendidikan/Edutech · Kesehatan/Klinik · F&B/Restoran · Fashion/Apparel · Travel/Hospitality · Otomotif · Jasa Profesional

**6 Segmen (khusus lini View Live — model berbeda):** Live Commerce Seller (Shopee Live / TikTok Shop) · Fashion & Beauty Live · F&B/Kuliner Live · Gaming/Streamer (Twitch/YouTube) · Brand Launching & Event · Affiliate / Content Creator

Diterapkan di 3 lapisan:
1. **Industri × Layanan** — "jasa iklan facebook untuk klinik", "google ads untuk properti", "jasa view live tiktok untuk seller shopee"
2. **Industri × Kota** — "jasa digital marketing F&B di Bandung", "jasa view live shopee di Surabaya"
3. **Section di halaman layanan existing** — tiap `/jasa-*/` (termasuk 136 halaman view-live) dapat blok "Cocok untuk industri/segmen: [chips]" + internal link ke artikel terkait

**Intent layering** tiap keyword: Commercial (harga/biaya/paket/beli) · Question (apa/bagaimana/berapa) · Comparison (vs) · Pain-point (boncos/tidak closing/sepi viewers).

---

## Industri Detailing per Layanan (11 Lini — LENGKAP, termasuk View Live)

> **PENTING (revisi):** SEMUA layanan digenerate untuk SEMUA 9 industri — **tidak dibatasi**. Daftar di bawah = **prioritas relevansi** (urutan generate lebih dulu / volume lebih tinggi), **BUKAN pembatas**. Semua kombinasi layanan×industri×kota tetap masuk queue. Lini View Live pakai 6 segmen sendiri karena modelnya beda (boosting viewers, bukan iklan).

| # | Lini / Layanan | URL | Industri / Segmen yang di-detailing |
|---|----------------|-----|--------------------------------------|
| 1 | Digital Marketing | `/jasa-digital-marketing/` | **SEMUA 9 industri** (payung/pillar) |
| 2 | Facebook/Meta Ads | `/jasa-iklan-facebook/` | E-commerce, Fashion, F&B, Properti, Kesehatan/Klinik, Otomotif, Jasa Profesional |
| 3 | Instagram Ads | `/jasa-iklan-instagram/` | Fashion, Beauty, F&B, Travel/Hospitality, E-commerce, Wedding/Event |
| 4 | TikTok Ads | `/jasa-iklan-tiktok/` | Fashion, Beauty, F&B, E-commerce, Produk viral, Edutech |
| 5 | Google Ads | `/jasa-iklan-google/` | Properti, Kesehatan/Klinik, Jasa Profesional/B2B, Otomotif, Pendidikan, Travel |
| 6 | YouTube Ads | `/jasa-iklan-youtube/` | Otomotif, Properti, Pendidikan, Travel, F&B, Brand awareness |
| 7 | Kelola Instagram | `/jasa-kelola-instagram/` | Fashion, Beauty, F&B, Klinik, Hotel/Travel, Personal brand |
| 8 | Kelola TikTok | `/jasa-kelola-tiktok/` | Fashion, Beauty, F&B, E-commerce, Personal brand, Edutech |
| 9 | Pembuatan Website | `/jasa-pembuatan-website/` | Company profile (semua), E-commerce, Properti, Sekolah, Klinik, Restoran |
| 10 | Landing Page | `/jasa-pembuatan-landing-page/` | E-commerce, Properti, Edutech (webinar), Kesehatan, Event, Jasa Profesional |
| 11 | **View Live** (lini terpisah) | `/jasa-view-live/` | **6 segmen:** Live Commerce Seller (Shopee Live/TikTok Shop), Fashion & Beauty Live, F&B/Kuliner Live, Gaming/Streamer, Brand Launching/Event, Affiliate/Creator |

### View Live — Detail Lini (JANGAN terlewat)
- **Model:** boosting penonton live real-time (bukan iklan) — dijual **per sesi live / per viewer-jam**, harga jauh lebih murah dari ads.
- **5 Platform × 25 kota = 136 halaman existing:** TikTok · Shopee · YouTube · Instagram · Twitch (`/jasa-view-live/{platform}/{kota}/`).
- **Keyword pattern khusus:** "jasa view live tiktok [kota]", "beli viewers shopee live", "jasa penonton live [platform] murah", "cara naikin viewers live shopee", "harga jasa live viewers youtube [kota]".
- **Intent modifier khusus view-live:** beli, jasa, murah, penonton, viewers, naikin, boost, aman, real.
- **Copy pakem view-live:** tekankan "viewers real aktif, no bot, aman untuk akun", "masuk 5-15 menit", "multi-platform" — tanpa overclaim.
- **Gap saat ini:** view-live BELUM masuk `keyword_miner.py` (10 layanan) tapi SUDAH ada di `expand_keywords.py` (`jasa-view-live` + `VIEW_LIVE_PLATFORMS`). Perlu disatukan + di-detailing per segmen.


---

## Keyword System (Deep Dive — Yang Sudah Dibangun)

Pipeline 2 lapis (SUDAH ADA, tinggal dijalankan + diperluas):

**1. `keyword_miner.py`** — 10 layanan × 25 kota × 20 template long-tail + Google Suggest + import Excel → base keywords.

**2. `expand_keywords.py`** — intent matrix eksplosif (target 7.000+): 11 svc × 26 kota × modifier:
| Kategori intent | Modifier |
|-----------------|----------|
| COMMERCIAL | murah, harga, biaya, tarif, paket, promo |
| QUALITY | terbaik, profesional, berpengalaman, terpercaya |
| ACTION | cara, tips, tutorial, langkah, strategi |
| QUESTION | apa itu, bagaimana, kenapa, berapa biaya |
| YEAR | 2026, 2027 |
| PAINPOINT | gagal, tidak closing, roas rendah, boncos |
| SERVICE_MODIFIERS (industri parsial sdh ada) | umkm, toko online, fashion, beauty, fnb, b2b, startup, dll |

- Output: `keyword-queue.json` ber-`priority_score`; `hourly-generate` pilih top-N `pending` (skip `has_post`).
- **Cron `seed-keywords` (0 3 * * *)** sudah auto-nambah keyword harian untuk semua layanan.
- **Gap:** modifier industri baru sebagian (fashion/beauty/fnb). Tambah **9 industri penuh + industri×kota**.
- **Dedupe wajib** vs 1.966 posts existing (slug-based) → hindari kanibalisasi.

**Sumber keyword (multi-source):**
- **Google Suggest / autocomplete** (sudah di `keyword_miner.py`) — real search demand
- **Scrape Indonetwork** (cron 30 6 * * *) — keyword bisnis B2B Indonesia (jalan)
- Import Excel `Keyword Beriklan.xlsx` + `keyword_suggestions_expanded.json`
- ⚠️ **Scrape Google Places (cron 0 7 * * *) TIDAK jalan** — butuh `GOOGLE_PLACES_API_KEY` (berbayar) & tak bisa scrape langsung → handler langsung return error tanpa key. **Set OFF/opsional, jangan diandalkan.**

---

## Harga Layanan & Fase Pekerjaan (dipakai untuk copy artikel + internal link)

**Harga aktual (dari halaman `/jasa-*/`):**
| Layanan | Tier / Harga (per 30 hari, belum termasuk ad spend) |
|---------|------|
| Digital Marketing | Starter (Konsultasi) · Custom Package (Custom) · Enterprise (Custom) |
| Facebook Ads | Standart Rp 1.750.000 · Business Rp 3.750.000 |
| Instagram Ads | Rp 1.750.000 · Rp 3.750.000 |
| TikTok Ads | Rp 1.000.000 · Rp 1.600.000 · Rp 3.750.000 |
| Google Ads | Rp 1.750.000 · Rp 3.750.000 · Rp 6.000.000 |
| YouTube Ads | Rp 1.250.000 · 2.500.000 · 3.750.000 · 4.750.000 |
| Kelola Instagram | Rp 2.500.000 · Rp 3.500.000 |
| Kelola TikTok | Rp 1.500.000 · 3.000.000 · 4.000.000 |
| Pembuatan Website | mulai Rp 999.000 |
| Landing Page | mulai Rp 1.999.000 |
| **View Live** (per sesi live) | Pemanasan Rp 12.000 (20 viewers) · Starter 25.000 (50) · Basic 45.000 (100) · Pro 80.000 (200) · Bisnis 115.000 (300) · Premium 175.000 (500) — multi-platform, ≈Rp 383-500/viewer/jam |

**Fase pekerjaan (dari `steps` di tiap halaman layanan)** — dipakai untuk struktur artikel "proses/cara kerja":
1. **Minggu 1** — Brief & Riset (produk, target market, objective)
2. **Minggu 1-2** — Setup & Kreatif (akun iklan, pixel, materi foto/video/copy)
3. **Minggu 2+** — Launch 30 hari (tayang penuh + laporan mingguan)
4. **Ongoing** — Optimasi & ganti iklan (yang perform di-scale)

**Aturan copy:** artikel keyword komersial (harga/biaya/paket) WAJIB menyebut angka paket nyata + "belum termasuk ad spend" + "tanpa kontrak minimum" — sesuai pakem, tanpa overclaim.

---

## Copywriting Pakem untuk Artikel AI (dari COPY-BIBLE.md)

- **Voice:** "Anda" dominan, formal-measured; istilah English (ROAS/CPA/funnel) dijelaskan saat pertama muncul; "kami" (bukan "kita"); NO slang (gak/bikin/handle iklan).
- **Banned (overclaim):** "pasti", "garansi 100%", angka palsu, "50+ bisnis", rating palsu. **Boleh:** "9 tahun mengelola campaign".
- **Power words:** terukur, transparan, teruji, real-time, end-to-end, berbasis data, laporan mingguan.
- **CTA:** WhatsApp `wa.me/62811919328` dengan konteks spesifik, sopan, tidak memaksa ("minta info", bukan "beli sekarang").
- Prompt `generateArticleForKeyword` WAJIB menanam pakem ini + **definisi 40-60 kata di awal** + **FAQ 3-4 Q&A** + author line "Tim Beriklan (9 tahun)".

---

## Internal Linking System (Yang Sudah Dibangun)

- **`internal_link_optimizer.py`** — max 2 link/artikel, HANYA di `<p>`, first-occurrence, topical-relevant ke `/jasa-*/` + `/jasa-*/pilar/`, idempotent (skip jika sudah ada link).
- **`retrofit_internal_links.py`** — untuk artikel lama.
- `SERVICE_MAP` = keyword→url mapping per 10 layanan.
- **Gap:** belum ada link kota↔kota & industri↔layanan. Tambah mapping industri + kota untuk perkuat topical cluster.
- **Aturan artikel baru:** 2-3 internal link → 1 ke halaman layanan, 1 ke kota terkait, 1 ke artikel industri/pilar.

---

## Matrix: Industri × Kota × Layanan × Fase (Cara Ekspansi Dirakit)

Tiap dari **9 industri**, keyword & artikel dirakit dari 4 sumbu:
| Sumbu | Contoh |
|-------|--------|
| **Layanan cocok** | F&B → IG Ads + Kelola IG + TikTok Ads · Properti → Google Ads + Landing Page · Klinik → Google Ads + Meta Ads · E-commerce → Meta + TikTok + Google |
| **Kota (25)** | "jasa iklan instagram untuk fnb di bandung" |
| **Intent** | commercial / question / comparison / pain-point |
| **Fase konten (funnel)** | awareness (apa/kenapa) → consideration (cara/tips/vs) → decision (harga/paket/terbaik) |

Tiap halaman `/jasa-*/` existing dapat blok **"Industri yang kami tangani" (9 chips)** → internal link ke pillar industri (perkuat topical authority tanpa buat halaman berlebihan).

---

## Email Retry System (SUDAH ADA — JANGAN DIHAPUS, tinggal disempurnakan)

Sistem email lengkap sudah **live** di `web/src/worker-entry.js`:
- **`handleCronSendEmail`** (cron `*/15`) — Resend free **100/hari**, batch 25 (smart-scale 20-40 sesuai antrean).
- Kuota habis → `skipped:true`, queue tetap `pending` di D1 → **auto-lanjut besok** (cron tiap 15 menit → resume max 15 menit setelah 00:00 UTC).
- **`cron_retry_queue`** — exponential backoff untuk kegagalan cron.
- **Auto-pause** setelah 3 gagal berturut + **email alert ke admin** (`sendEmailViaResend` → aramadhi92@gmail.com).
- Endpoint reset: `/api/admin/email/queue/reset` (failed → pending).
- **Drip 3-email** (NEWSLETTER-DRIP.md): welcome → 3 kesalahan Meta → studi kasus.

**Penyempurnaan (BUKAN bangun ulang):**
1. **Auto-reset** email `status='failed'` → `'pending'` saat kuota pulih (sekarang failed TIDAK auto-retry, perlu reset manual).
2. **Verifikasi `RESEND_API_KEY`** ter-set (kalau belum: drip & alert mati).
3. **Aktifkan cron `email-send`** (default PAUSED) setelah subscriber terkumpul.

---

## Peningkatan per Area

### A. Website
- Blok "Industri yang kami tangani" (chips) di tiap halaman layanan → internal link ke artikel industri
- 136 halaman view-live dapat blok "Segmen yang kami bantu" (6 chips: seller, streamer, dll)
- Breadcrumb + schema `Service`/`FAQPage` konsisten di semua halaman
- Hub/pillar page per industri (link ke semua artikel industri terkait)

### B. Artikel / Konten (AI Overviews + E-E-A-T)
- **Definisi 40–60 kata** di awal tiap artikel (target featured snippet / AI Overview)
- **FAQ terstruktur** 3–4 Q&A + schema FAQPage
- **E-E-A-T**: "Ditulis oleh Tim Beriklan (9 tahun)" + tanggal update terlihat
- Data konkret (%, Rp) sesuai pakem COPY-BIBLE (tanpa overclaim/angka palsu)
- Internal link 2–3 ke halaman layanan + kota terkait

### C. Keyword
- Jalankan `keyword_miner.py --all` (**sumber: Google Suggest/autocomplete + Indonetwork**) + `expand_keywords.py` untuk isi queue dari 100 → ~12K
- Tambah template industri, question, comparison, pain-point ke miner
- **SEMUA layanan × SEMUA 9 industri × 25 kota** (tidak dibatasi; prioritas hanya urutan)
- **View Live: tambah 5 platform (TikTok/Shopee/YouTube/IG/Twitch) × 6 segmen × 25 kota** + modifier khusus (beli/viewers/penonton/murah/aman)
- Dedupe ketat vs 1.966 posts existing (hindari kanibalisasi)
- ⚠️ Google Places scrape (0 7 * * *) OFF — butuh API berbayar; jangan diandalkan

### D. Sistem Indexer & Link Distribution (biar SEMUA keyword #1)
**Indexing (sudah ada, tinggal di-ramp):**
- **GSC Indexing API** (`handleGscIndexing`, butuh `GSC_SERVICE_ACCOUNT_JSON`) — ramp 20→50→100→200/hari dari D1 `pending_indexing` (jangan langsung 200)
- **IndexNow** (cron 15 * * * *, count 50) — Bing dkk + monitoring crawl stats GSC
- Ping + re-submit sitemap tiap 50 halaman baru

**Link distribution otomatis (BARU — kunci ranking #1):**
- Tiap artikel baru → auto internal link 2-3 ke halaman **layanan + kota + pillar/industri** (mesh dua arah)
- **Retro-link:** artikel LAMA relevan otomatis dapat link KE artikel baru (backlink internal) → sebar link equity merata
- **Hub/pillar** per layanan & industri jadi pusat authority; artikel anak nge-link ke hub, hub nge-link balik ke anak
- Related-posts (3/artikel) sudah ada → perkuat relevansi kota+industri
- (Opsional) auto-submit direktori via `directory_auto_submit.py` yang sudah ada

### E. Monetisasi AdSense (TUJUAN UTAMA — sejajar ranking)
- AdSense sudah terpasang (`ca-pub-4438184351486735`, lazy-load) di city pages, homepage, blog
- **Skala impresi = jumlah halaman ter-index × traffic** → bulk publish + indexing = RPM naik
- Target juga keyword **informational high-traffic** (apa/cara/tips), bukan cuma komersial → volume AdSense
- Pasang slot in-article di artikel blog baru (samakan pola city page: 1 slot mid-content, non-intrusif)
- **Policy safety WAJIB:** `checkPolicyViolation` (sudah ada) blokir topik terlarang sebelum publish → lindungi akun AdSense. JANGAN dimatikan
- Monitor RPM/CTR per kategori; scale kategori paling cuan

### F. Trending Artikel Harian (sudah ada — pastikan jalan)
- `handleTrendingCron` (0 */6) tarik topik Google Trends → D1 `trending_topics`
- `handleTrendingGenerate` (30 */6, s/d 4/hari) generate dari topik pending → `trending_articles` + commit GitHub
- Kalau "trending harian hilang": cek `trending_topics` kosong (fetch gagal) atau cron paused di `cron_settings` → aktifkan kembali
- Trending = konten fresh harian → sinyal freshness ke Google + magnet traffic AdSense

---

## Perubahan Kode (Ringkas)

| Area | File | Perubahan |
|------|------|-----------|
| Draft mode | `web/src/worker-entry.js` `handleHourlyGenerate` | Tambah `?mode=draft` → simpan ke `generated_drafts` (tabel SUDAH ada), tidak commit posts.json |
| Publish queue | `web/src/worker-entry.js` (handler baru `handlePublishQueue`) + cron baru | D1 `generated_drafts` → posts.json bertahap (N/hari naik mingguan); manfaatkan pola cron `sync-posts` (0 1 * * *) yang sudah ada |
| Zen di Batch4/City | `scripts/batch4_generate.py`, `scripts/enrich_city_content.py` | Tambah Zen sebagai provider utama sebelum Groq |
| Bulk orchestrator | `scripts/bulk_generate_all.py` (baru) | Loop panggil Worker `/api/cron/hourly-generate?count=5&mode=draft`, jeda aman |
| Keyword expansion | `scripts/expand_keywords.py` + `keyword_miner.py` | Tambah 9 industri penuh + industri×kota; **view-live: 5 platform × 6 segmen × 25 kota** + modifier khusus (beli/viewers/penonton) |
| AI Overview + E-E-A-T | `generateArticleForKeyword` prompt | Wajibkan definisi 40-60 kata, FAQ, author line, pakem COPY-BIBLE, harga paket |
| Internal link industri | `scripts/internal_link_optimizer.py` | Tambah mapping industri + kota (link cluster antar-artikel) + **retro-link artikel lama → artikel baru** (backlink internal dua arah) |
| AdSense in-article blog | `web/src/pages/blog/[slug].astro` (atau komponen blog) | Tambah 1 slot AdSense mid-content (pola `CityContentBlock`) untuk artikel baru → boost impresi |
| Google Places OFF | `web/wrangler.jsonc` / dashboard | Tandai cron `0 7 * * *` OFF/opsional (butuh API berbayar, tak bisa scrape) |
| Email penyempurnaan | `web/src/worker-entry.js` `handleCronSendEmail` | Auto-reset failed→pending saat kuota pulih; verifikasi `RESEND_API_KEY`; aktifkan cron email-send |

---

## Prasyarat (Verifikasi Dulu)
> Semua perubahan Worker di **`web/src/worker-entry.js`** (folder `web/` = repo yang ter-deploy), bukan root `src/`.
1. `ZEN_API_KEY` ter-set di CF Worker secrets (cek `/api/admin/env-check`)
2. `GITHUB_TOKEN` aktif (untuk commit dari Worker)
3. `GSC_SERVICE_ACCOUNT_JSON` aktif (indexing + rank sync)
4. `RESEND_API_KEY` ter-set (untuk drip + email alert cron)
5. Deploy = git push (dari folder `web/`) → CF Build (sudah terhubung)

## Urutan Eksekusi
```
URGENT: verify secrets (Zen/GitHub/GSC/Resend) → expand keyword queue → tambah draft mode + publish queue
HIGH:   bulk_generate_all.py → Zen di Batch4/City → AI-Overview prompt + E-E-A-T + pakem COPY-BIBLE
MEDIUM: email auto-reset failed→pending → gradual indexing ramp → industri hub pages + internal link cluster
```

## Test Plan
- `/api/admin/env-check` → semua secret true
- Miner dry-run → cek jumlah keyword hasil expand
- Generate 5 draft → verifikasi masuk `generated_drafts` (bukan live)
- Publish cron manual → 10 artikel pindah ke posts.json, CF Build sukses, halaman live
- Cek policy filter memblok topik terlarang
- Pantau `/api/admin/keywords` (coverage) & `/api/admin/rank-tracker`

## Asumsi
- Zen (deepseek-v4-flash-free) tetap gratis & stabil; Groq sebagai fallback
- Workers Free tier cukup dengan orkestrasi count=5 dari lokal + jeda
- Rollout target ~12K keyword; publish penuh butuh beberapa bulan (by design, anti-spam)