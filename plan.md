# PLAN — Push Rank Page 1 + Killer Feature Beriklan.co.id

> **Tujuan:** Maksimalkan peluang ranking page 1 Google untuk keyword long-tail digital marketing Indonesia, via automasi SEO yang sudah jalan + 1 fitur killer yang gathered traffic organik berlipat.
> **Mulai:** 02 Agustus 2026
> **Status:** 🔴 Belum dimulai
> **Owner:** Beriklan Digital Agency + Codex AI

---

## 0. Realita (baca sekali, lalu eksekusi)

- **#1 di Google tidak bisa dijanjikan.** Yang bisa dijamin: setiap halaman punya *peluang terbaik* di keyword long-tail (volume rendah, kompetitor lemah).
- **358.863 keyword di queue = 358.863 medan perang.** Kalau di-publish semua → buru-buru Google flag *scaled-content abuse* (update 2024–2025) → situs turun massal, bukan naik. Strategi: **publikasi terkurasi**, bukan burst massal.
- **Kalkulator sudah standar.** Ia hanya Tools menu yang user pakai sekali lalu pergi. Killer feature harus: (a) dicari UMKM高频, (b) dipakai berulang, (c) membedakan dari kompetitor, (d) men-chanel ke konsultasi WA.

Setiap keputusan di bawah diuji ke 4 kriteria itu.

---

## 1. KILLER FEATURE: "Spionase Iklan" — Ad Spy Tool Bahasa Indonesia Gratis

### Kenapa ini (bukan kalkulator lain)

| Aspek | Realita Pasar |
|---|---|
| **Pain UMKM** | "Tetangga saya jualan lebih laku, kok iklannya menang? Mau tiru tapi nggak ngerti." — ini pertanyaan yang Google utk UMKM Indonesia tiap hari. |
| **Gap** | Tidak ada ad spy tool **gratis berbahasa Indonesia**. AdSpy $149/bln, BigSpy $79/bln, PowerAdSpy $49/bln — semua English UI, kartu kredit wajib. UMKM Indonesia gak akan bayar. |
| **Volume pencarian** | "cara lihat iklan kompetitor", "spionase iklan facebook", "cek iklan kompetitor tiktok", "contoh iklan facebook yang laku" — long-tail, volume sedang, kompetitor tipis (blog rejeki adsense, bukan tool). |
| **Stickiness** | User cek kompetitor tiap minggu (saat plan iklan baru) → return visit tinggi → sinyal authority ke Google. |
| **Reusalf infra** | Worker AI (Zen/Groq) + scraper pipeline + email-send cron → semua sudah jalan. Tambahan kode = stitch, bukan rebuild. |
| **Lead channel** | Tiap laporan AI akhirnya ujungnya: "Mau kami bantu implementasi pattern ini? → WA". Persis formula follow-up WA yang sekarang sudah jalan. |

### Spec MVP (6 minggu)

```
/alat/spionase-iklan       ← hub page (SEO landing)
/spionase-iklan-facebook  ← SEO cluster landing (long-tail)
/spionase-iklan-tiktok
/spionase-iklan-google-ads
/cek-iklan-kompetitor     ← pain keyword
```

**Flow user:**
1. Input: nama bisnis / domain / username IG (gratis, tanpa daftar)
2. Sistem: tarik iklan aktif dari 3 sumber (free):
   - Meta Ad Library (public search) → aktif 90 hari terakhir
   - TikTok Top Ads / Creative Center → ads terpopuler per kategori
   - Google Ads Transparency Center → ads aktif dari domain
3. AI breakdown dalam Bahasa:
   - Hook pattern (curiosity / fear / social proof / price-anchor)
   - Angle kampanye (problem-solution / lifestyle / testimonial / promo)
   - Estimasi segmen (umur/gender dari visual text lead)
   - Active lifetime (berapa hari aktif → budget proxy)
   - 3 swipeable insight (apa yang gue bisa pakek buat iklan gua)
4. Optional: simpan pantauan → email mingguan saat kompetitor ubah iklan.

**Use case video demo (Instagram):** "Pakek Spionase Iklan buat ngelihat kenapa iklan brand A laku 8 bulan."

### Arsitektur (di Worker, biaya ≈ Rp 0)

```
Astro page (/alat/spionase-iklan) ── Svelte island interaktif
              │
              ▼ POST /api/spionase/lookup
   ┌──────────────────────────────────────┐
   │ Worker route handler                 │
   ├──────────────────────────────────────┤
   │ /api/spionase/meta    → Meta Ad Lib  │  (Graph API /public教育与_ads_archive)
   │ /api/spionase/tiktok  → TT Top Ads   │  (scrape Creative Center, headless)
   │ /api/spionase/google  → Ads Transp.  │  (scrape adstransparency.google.com)
   │ /api/spionase/analyze → AI (Zen/Groq)│  (sudah ada helper generateWithZenOrGroq)
   └──────────────────────────────────────┘
              │
              ▼ insert ke D1
   spionase_searches  (user_email, target_domain, created_at, ip_hash)
   spionase_reports   (cache per target_platform, JSON payload, expires_at)
   spionase_monitors  (saved pantauan, last_sha, alert_status)
              │
              ▼ cron mingguan (baru) `spionase-pantau`
   Bandingkan ad_sha baru vs lama → kirim email alert via email_queue
```

### Data source — SEMUA gratis

| Sumber | Cara access | Status ToS | Volume/menit |
|---|---|---|---|
| Meta Ad Library API (`/ads_archive`) | App review + page perms (7–30 hari) | Resmi (Meta-offered) | 200 req/jam |
| Meta Ad Library web public | scrape via headless Playwright | grey — pakai residential proxy free tier | 1 req/5 detik |
| TikTok Creative Center Top Ads | public scrape `/business/creativecenter/inspiration/popular` | grey | 1 req/detik |
| Google Ads Transparency Center | public scrape `adstransparency.google.com/?region=ID&q=` | grey (sama seperti `trawl` repo) | 1 req/detik |
| Google Places (kompetitor bisnis lokal) | **sudah ada** di pipeline | resmi API | 20 req/detik |

### GitHub repos yang bisa di-leverage / study

| Repo | Untuk |
|---|---|
| `facebook/python-business-sdk` | Wrapper resmi Graph API (Ads Archive endpoint) |
| `mcspr/fb-ad-library` | reference scrape pattern (Python) |
| `braedonsaunders/trawl` | pattern: Google Maps + Playwright + LLM enrich + cold outreach. Sangat mirip. |
| `nando0x/ProspectOS` | pattern: scraping Google Maps + pesan AI. |
| `DotJK/selenium-toolkit` | stealth scraper untuk TikTok/G Ads (residential proxy rotation) |

**Tidak perlu fork** — kita hanya pinjam patternnya. Worker Astro + Svelte sudah cukup infra.

### Roadmap Spionase Iklan

| Minggu | Milestone |
|---|---|
| 1 | Hub page + SEO copy + 3 cluster landing pages (`/spionase-iklan-{fb,tt,ga}`) |
| 2 | Worker endpoint `/api/spionase/meta` + D1 tables + cache 7 hari |
| 3 | Integrasi Meta Graph API (apply app review paralel) + UI form |
| 4 | TikTok scrape (Creative Center) + Google Ads Transparency scrape |
| 5 | AI breakdown endpoint (pake helper `generateWithZenOrGroq` yang udah ada) |
| 6 | Monitor + email alert + WA-CRO card (push ke konsultasi) |
| 7+ | Cluster spionase "per industri" (kuliner, fashion, properti) untuk long-tail programmatik |

---

## 2. SEO Push Strategy (Minggu 1 → 12)

### 2.1 Inventory & prune (Minggu 1–2)

**Realita:** keyword-queue 358k = masalah, bukan opportunity.

Aksi:
1. Worker cron baru `gsc-rank-audit` (tiap hari) → panggil GSC API `searchanalytics.query` 7 hari last + simpan `rank_audits` D1.
2. Klasifikasi tiap URL jadi 3 keranjang:
   - **Pemenang** (impresi > 10, posisi < 20) → boozt: tambah internal link, FAQ schema, konten refresh
   - **Sedang** (impresi 1–10) → awasi 4 minggu
   - **Matte** (impresi 0, indeks 30 hari+) → kandidat canonical/410/robots disallow
3. Threshold: **publish maks 30 artikel baru/minggu** (cron `hourly` sekarang 3/jam = 504/minggu → turunkan ke 4/hari = 28/minggu, kualiti naik). Matiin auto-burst yang pakek 358k keyword queue.

D1 tabel baru:
```sql
CREATE TABLE rank_audits (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT, url TEXT, query TEXT,
  impressions INTEGER, clicks INTEGER, position REAL,
  cluster TEXT,  -- 'pemenang'|'sedang'|'mati'
  logged_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_rank_audits_url ON rank_audits (url, date);
CREATE INDEX idx_rank_audits_cluster ON rank_audits (cluster);
```

### 2.2 Internal linking otomatis (Minggu 2–3)

- Build D1 graph dari `posts.json`: tag → multimap post.
- Endpoint worker `/api/related-links?slug=X` → return 5 slug relevan (TF-IDF simple di tags).
- Inject di `[slug].astro` dan `index.astro` section "Related".
- **Efek:** PageRank internal naik ke *pemenang* cluster.

### 2.3 Schema boost per pillar (Minggu 3)

- Pilar (10 layanan + 1 homepage + 1 spionase hub + 4 cluster) → generate `FAQPage` + `HowTo` JSON-LD dari konten via AI.
- Cron baru `schema-boost` mingguan: tiap pilar → AI generate 5 Q&A dari body → tulis ke `schema_injections` D1 → Layout.astro baca & inject.

### 2.4 Topic cluster programmatik (Minggu 4–6)

Untuk long-tail tanpa burst:
- Pilih 20 niche keyword cluster (misal "iklanfacebook-umkm-kuliner-bandung")
- Untuk tiap cluster: 1 hub page + 5 spoke (variasi lokasi/segmen)
- Cron `cluster-generator` mingguan: ambil keyword dari queue, di-assign ke cluster, generate spoke via AI helper yang udah ada

### 2.5 IndexNow + Bing Webmaster (Minggu 2)

- Cron `indexnow` (sudah ada) → sekalian submit ke Bing Webmaster via `https://ssl.bing.com/webmaster/api.svc/json/SubmitUrls`
- Tambah satu baris di cron `gsc-indexing` (sudah ada) → sekaligus submit Bing.

---

## 3. Authority & Backlink Gratis (Minggu 4–10)

Tidak ada backlink premium gratis. Tapi authority bisa dipanen:

1. **Direktori tools listicle inbound** — Spionase Iklan di-pitch ke "best marketing tools Indonesia 2026" listicle lokal (DailySocial, Bisnis Indonesia, IDN Media subsidiary blogs).
2. **Guest expert posts** — 8 guest posts di blog marketing Indonesian (Marketeers, SWA, Bisnis.com lifestyle) — angle "formance marketing buat UMKM".
3. **Google Business Profile** — fully optimize: post mingguan, foto tim, review request → trust signal lokal yang banyak orang lewatin.
4. **Direktori tools github** — submit Spionase Iklan ke `serpapi/awesome-seo-tools` + `openalternative.co` → free traffic dari komunitas developer.
5. **Quora/Reddit** — jawab pertanyaan "cara lihat iklan kompetitor" → link ke Spionase Iklan (jangan spam, 1 link per 5 jawaban bermanfaat).
6. **Sekolah konten** — 1 video YouTube pendek/teng bulan, embed di hub page → dwell time naik.

---

## 4. Analytics & Monitoring (Minggu 2 onward)

Worker admin tambah tab `📈 SEO Rank` (`/api/admin/email?tab=seo`):
- Tabel: top 100 queries GSC 30 hari last, posisi, bytes uploaded/indexed.
- Graf: jumlah query di posisi 1–3, 4–10, 11–50 (chart.js inline).
- Tabel `rank_changes`: tonjolkan keyword yang naik/turun > 5 posisi vs minggu kemarin.
- Cron аудяр mingguan `seo-weekly-summary` → email summary ke admin@beriklan.co.id.

---

## 5. Cron Baru untuk Di-add

| Cron | Trigger | Fungsi |
|---|---|---|
| `gsc-rank-audit` | `0 3 * * *` (harian) | Tarik GSC search analytics last 7d → klasifikasi cluster → tulis `rank_audits` |
| `internal-link-sync` | `0 4 * * 1` (mingguan) | Re-build D1 graph dari `posts.json` (kalau ada penambahan) |
| `schema-boost` | `0 5 * * 1` | AI generate FAQ+HowTo untuk pilar yang belum → inject |
| `cluster-generator` | `30 5 * * 1` | Ambil 20 keyword baru dari queue, assign cluster, generate spoke via AI |
| `bing-submit` | pasangan `gsc-indexing` | Submit URL ke Bing Webmaster API |
| `spionase-pantau` | `0 6 * * 1` | Bandingkan ad_sha kompetitor yang di-monitor → kirim email alert kalau berubah |
| `seo-weekly-summary` | `0 7 * * 1` | Email summary rank delta + cluster report ke admin |

## Cron yang perlu TURUNKAN

| Cron | Sekarang | Usulan | Alasan |
|---|---|---|---|
| `hourly` (generate artikel) | 3/jam = 504/minggu | 4/hari = 28/minggu (`0 9,12,15,18 * * *`) | Hindari scaled-content flag; naikkan kualitas |

---

## 6. Eksekusi 12 Minggu

| Minggu | Fokus | Deliverable |
|---|---|---|
| 1 | Inventory + prune + Spionase hub pages | `gsc-rank-audit` cron + 4 SEO landing Spionase |
| 2 | Internal linking + Meta Ad Lib app review | `/api/related-links` endpoint + applikasi Meta Graph |
| 3 | Schema boost + TikTok scrape pattern | `schema-boost` cron, 10 pilar FAQ-enriched |
| 4 | Meta `/api/spionase/meta` + Bing submit | Endpoint meta live, Bing automation |
| 5 | Google Ads Transparency scrape + UI form | `/api/spionase/google`, form input |
| 6 | AI breakdown + Monitor + email alert | `/api/spionase/analyze`, monitor + alert |
| 7 | Cluster programmatik + Bing SEO | 20 spoke cluster published |
| 8 | Guest post outreach + listicle pitch | 5 outreach email per minggu |
| 9 | SEO dashboard tab `📈 SEO Rank` | Live di admin |
| 10 | YouTube pendek + indexnow quota scale | 4 video pendek embed |
| 11 | Quarterly audit — mati URL yang matte | 410/canonical 30% URL matte |
| 12 | Retrospective: cluster pemenang di-scale | Keranjang pemenang jadi prioritas Q2 |

---

## 7. Success Metrics (realistik)

| Metric | Baseline (Aug 2026) | Target 12 minggu | Target 24 minggu |
|---|---|---|---|
| Total clicks/bulan (GSC) | ? (audit minggu 1) | +50% | +200% |
| Query di posisi 1–10 | ? | +30% | +100% |
| URL indexed vs sitemap | ? | >85% | >95% |
| Backlink domain (referring) | ? | +20 | +80 |
| Monthly organic visits | ? | +40% | +150% |
| Tool user (Spionase baru) | 0 | 200/minggu | 1.000/minggu |
| Lead WA dari Spionase | 0 | 10/bulan | 50/bulan |

> Baseline diambil minggu 1 setelah `gsc-rank-audit` jalan.

---

## 8. Anti-patterns (JANGAN)

- ❌ Publish burst 358k artikel → scaled-content abuse
- ❌ Cloaked PBN backlinks → manual penalty
- ❌ AI konten tanpa human verify → EEAT zero → rangking turun
- ❌ Tool yang butuh daftar + kartu kredit → bounce tinggi
- ❌ Klaim "#1 di Google" → janji kosong, buang kepercayaan klien
- ❌ Scraping Meta/TikTok tanpa rate-limit / anti-detection → IP banned, akun DNA kalau pakek akun production

---

## 9. Yang Saya Butuh dari User buat Start Phase 1

| Item | Untuk |
|---|---|
| **Meta App** (Facebook Developer account) | Apply app review buat Ads Archive read permission |
| **Bing Webmaster** login | Submit sitemap, enable API submit |
| **Konfirmasi**: stop burst hourly article | Turunkan dari 3/jam → 4/hari |
| **Konfirmasi**: prune URL matte | 11 minggu, target 30% |

Saya bisa mulai tanpa 4 di atas — Phase 1 (gsc-rank-audit + internal link + Spionase hub) jalan pakai yang udah ada.

---

**Versi:** 1.0 (Aug 02 2026)
**Maintainer:** Beriklan Digital Agency + Codex AI
---

## Addendum 25 Agustus 2026 — Growth System (GSC feedback loop) DIIMPLEMENTASI

Sesuai `SEO-GROWTH-SYSTEM.md`, 4 loop yang menutup siklus publish→rank→belajar→perbaiki
sudah ditulis di `src/worker-entry.js` (tanpa GitHub Actions; jalan via CF Workers cron time-gate):

| Cron | Jadwal | Endpoint | Fungsi |
|---|---|---|---|
| `growth-gsc-loop` | tiap 6 jam | `/api/cron/growth/gsc-loop` | Query GSC [query,page] 14 hari; query komersial ber-impresi TANPA halaman blog → `keyword_queue` (source `gsc-impression`) |
| `growth-enrich` | harian 09:00 UTC | `/api/cron/growth/enrich` | Halaman posisi 3-18 → rewrite intro (`growth-intro`) + FAQ spesifik-query (`growth-faq`) di `posts_content`; cooldown 21 hari |
| `growth-ctr-fix` | harian 09:00 UTC | `/api/cron/growth/ctr-fix` | Impresi≥50 & CTR≤2% → `seo_title`≤60 + `seo_description`≤155 di `posts_meta` (renderer pakai override SERP; H1 tidak berubah); cooldown 30 hari |
| `growth-freshness` | Senin 02:00 UTC | `/api/cron/growth/freshness` | Artikel >90 hari ber-impresi → callout "Update {tahun}" (`freshness-update`) + `refreshed_at` → badge "Diperbarui" + `dateModified` jujur |

**Keputusan arsitektur penting:**
- Semua loop MENULIS LANGSUNG KE D1 (`posts_meta`/`posts_content`) — efek live tanpa build,
  karena `fetch()` sudah D1-first untuk `/blog/<slug>/` yang ada di `posts_meta` (render
  dinamis baca D1 saat request; static asset hanya fallback kalau slug tak ada di D1).
- Audit trail lengkap di tabel `growth_log`; schema auto-ensure di tiap handler + migrasi.
- `renderBlogPost` dibuat defensif: fetch kolom growth terpisah (try/catch) supaya tidak
  500 kalau kolom belum ada.
- `/api/cron/index-cascade` ditambahkan ulang (kontrak live lama, submit via
  `pending_indexing` agar quota GSC 200/hari tetap terkontrol).

**STATUS DEPLOY — SELESAI, growth system LIVE & terverifikasi (2026-08-25).**
CF auto-build via GitHub tidak terpasang (repo tanpa webhook); deploy sekarang via
`wrangler deploy` lokal dengan token account-scope baru `cfut_wUtY...` (lihat
`account.md`). Code live = HEAD repo + patch lokal (lihat commit list).

Hasil verifikasi end-to-end:
- 301 `www→apex` WORKS untuk API/static/blog — syaratnya `assets.run_worker_first: ["/*"]`
  di `wrangler.jsonc` (kalau hanya `/blog/*`, asset-first mem-bypass Worker → 301 gagal).
- Build Astro 10.416 file (893MB dist: 7497 blog + 4952 tag + 500 kota) deploy ±30s incremental.
- `rank-sync` OK (103 rows); `gsc-loop` OK (168 rows GSC, 3 relevan, dedupe jalan).
- `growth/enrich` OK — intro + 3 FAQ live di `/blog/<slug>/` (`growth-intro` + `growth-faq`).
- `growth/freshness` OK — badge "Diperbarui" + callout "Update 2026" live (`freshness-update`).
- `growth/ctr-fix` OK (0 kandidat: belum ada artikel imps≥10 & CTR≤2% di data www property).
- Audit trail: `/api/admin/growth-log?token=...` menampilkan action/slug/model/error.
- AI: Zen `deepseek-v4-flash-free` sering 429 → fallback Groq. Model `llama-3.3-70b-versatile`
  sudah DIHAPUS Groq; konstanta `GROQ_CHAT_MODELS` = `openai/gpt-oss-120b`,
  `qwen/qwen3.6-27b`, `openai/gpt-oss-20b` (3 API key dirotasi). gpt-oss butuh
  `reasoning_effort: "low"` + max_tokens lebih besar (output reasoning ikut memakan budget).
- Debug: `/api/admin/ai-test?token=...` (tambah `&models=1` untuk list model Groq live).

Gotchas operasional yang ditemukan:
1. **Schedule API** PUT `/accounts/{id}/workers/scripts/{name}/schedules` — body harus
   **array mentah** `[{"cron":"..."}]`, BUKAN objek `{"schedules":[...]}` (error 10026).
2. **Cap cron 5/account** (bukan per-script) — SELESAI 2026-08-25: user memutuskan
   `beriklan-app` (dashboard Google Ads `app.beriklan.co.id`, project `capi-gateway-v2`)
   TIDAK dipakai → cron-nya di-PUT `[]` via API schedules. Kelima slot kini milik
   `beriklanweb`: `0 * * * *` (hourly + time-gate growth), `*/15 * * * *` (email-send),
   `30 6 * * *` (scrape-indonetwork), `0 7 * * *` (scrape-google-places),
   `0 3 * * 1` (snippet-optimize) — persis `wrangler.jsonc` triggers.
   **2026-08-26: script `beriklan-app` dihapus total** via
   `DELETE /accounts/{id}/workers/scripts/beriklan-app`. Tidak ada route zone yang
   pointing ke script itu sejak awal (semua 9 route di `beriklan.co.id` point ke
   `beriklanweb`), jadi tidak ada yang putus. `app.beriklan.co.id` sekarang 522.
3. **GSC permission**: service account HANYA punya akses property `https://www.beriklan.co.id/`
   (prefix URL). Apex `https://beriklan.co.id/` → 403; `sc-domain:beriklan.co.id` → 0 rows.
   Secret `GSC_SITE_URL` saat ini = `https://www.beriklan.co.id/` (satu-satunya yang data).
   Retest 2026-08-25: secret di-switch ke apex → tetap 403 (SA belum ditambahkan),
   lalu di-revert ke www dan diverifikasi hidup lagi (gsc-loop 71 rows, rank-sync 63 rows).
   Retest 2026-08-26 (setelah user menyatakan SA sudah ditambahkan): apex `https://beriklan.co.id/`
   masih 403; domain property `sc-domain:beriklan.co.id` sudah bisa diakses (bukan 403)
   tapi 0 rows window 14/28 hari (kemungkinan property baru, data belum tersedia).
   Secret `GSC_SITE_URL` tetap `https://www.beriklan.co.id/` (satu-satunya yang punya data).
   **`rank-sync` www = 295 rows / 14 hari**, `growth/gsc-loop` jalan.
   → Menunggu user memastikan `beriklan-seo-bot@lgc-indexer.iam.gserviceaccount.com` sudah
   ditambahkan sebagai **Owner** (bukan Full/User) di GSC property apex `https://beriklan.co.id/`
   (Search Console → Settings → Users & permissions). Domain property baru mungkin butuh waktu
   untuk akumulasi data historis; alternatif: setup SA Owner di apex URL-prefix lalu
   `printf 'https://beriklan.co.id/' | npx wrangler secret put GSC_SITE_URL`,
   test `rank-sync` + `growth/gsc-loop` untuk pastikan data apex terbaca.
   Catatan: data www masih tipis (~295 rows/14d, growth/ctr-fix butuh ≥50 imp/keyword
   sehingga 0 kandidat; clamp produksi minImp=50, maxCtr=0.02) — akan terisi setelah data
   apex/domain masuk.
4. **Root www bisa HIT cache lama** (token tidak punya scope cache purge): `www.beriklan.co.id/`
   kadang 200 HIT; path lain 301. Menunggu expire atau purge manual via dashboard.
5. Renderer blog sudah D1-first + fallback asset statis, jadi semua job growth live tanpa rebuild.
6. **`sync-posts` mirror gate** — `/api/admin/sync/posts` sebelumnya kena `1102` karena mode
   penalu memuat `posts_meta` + `posts_content` (~40MB), fetch/merge/PUT `src/data/posts.json`
   ke GitHub. Sekarang ada query param `mirror`: default `lean` (publish D1 saja, aman di
   Workers Free), `mirror=1` full GitHub mirror (manual only). Cron `0 * * * *` pakai lean;
   full mirror dipanggil manual saat perlu rebuild static. Lean run terakhir:
   `d1_published:30`, `auto_index_enqueued:30`, `published_today:90`, `remaining_today:210`,
   `daily_limit:300`, `batch_size:30`, `total_drafts_pending:380`, `elapsed:9.4s`.
7. **Bulk keyword import** — `POST /api/admin/keywords/import?token=…&source=…` (JSON array atau
   `{keywords:[…]}`). Handler `handleAdminKeywordsImport` normalisasi `keyword_normalized`
   (lowercase + trim + collapse space), dedupe by `keyword`/`keyword_normalized`, insert ke
   `keyword_queue` status `pending`. Riset v2 (`web/public/data/keyword-research-v2.json`,
   583 keyword unik, fokus jasa live & website + layanan inti × industri/kota) diimport:
   359 inserted, 224 skipped. Cek via `GET /api/admin/keywords/list`.
8. **Stat pipeline (cek 2026-08-26 sebelum sync manual)**:
   - `generated_drafts` total ~11.007; committed ~10.627; pending ~380.
   - `keyword_queue` total ~391.121; pending ~381.783; published ~9.010 (+359 baru setelah
     import riset v2 → pending ~382.142).
   - Audit konten: `total_committed 10567`, `avg_len 3813`, `min 2448`, `max 9133`,
     `thin_count 198` (threshold 3000 char) di checkpoint sebelumnya.
9. **Endpoint utama debug baru** — `/api/admin/sync/posts?mirror=1`,
   `/api/admin/keywords/import?source=curated_research_v2`,
   `/api/admin/audit/content?format=json`, `/api/admin/drafts?format=json`.

---

# BAGIAN II — HYBRID SEO AUTOMATION (VPS Coolify + Edge)
_(ditambahkan 15 Sep 2026; Bagian I di atas tetap berlaku, tidak diubah)_

> 3 domain: **beriklan.co.id**, **beriklan.my**, **foryoutours.com**
> Status: RENCANA — belum dieksekusi. Eksekusi mulai setelah akses VPS diberikan.
> Ditulis: 15 Sep 2026. Maintainer: Beriklan Digital Agency + Codex AI.
> **Dokumen pendamping (wajib dibaca): `SEO-INDEX-LLM-BLUEPRINT.md`** — deep-dive
> seluruh script/workflow SEO existing (lokasi kode presisi) + hasil riset 2026 cara
> menang indexing & sitasi LLM (AI Overviews, ChatGPT, Perplexity, Gemini, Copilot)
> + checklist aksi Edge-vs-VPS. Ringkasannya: fondasi indexing (sitemap/IndexNow/GSC)
> sudah jalan; gap terbesar = quick-answer blocks, listicle Top-N, comparison table,
> ItemList schema, GEO monitor, dan 2 job yang belum ada di kode (news-ping,
> distribute → dibangun di VPS sebagai job C1/C2 blueprint).

## STATUS BOARD (update: 15 Sep 2026 ~05:50 UTC)

| # | Item | Status | Bukti |
|---|---|---|---|
| 1 | socio.id + app.socio.id + DB socio | ✅ AMAN — tidak tersentuh | `docker ps` read-only; uptime semua container socio/Coolify tidak berubah |
| 2 | VPS Postgres + API internal :18743 | ✅ BERJALAN | health 200 lokal, query DB nyata, IP luar 403 |
| 3 | Fix kuota D1 (co.id `a4012f8d`, .my `15fd2dae`) | ✅ BERJALAN (efek penuh pasca-reset) | versions list cocok; smoke 200 semua |
| 4 | robots.txt +2 bot (A1) | ✅ BERJALAN | curl isi live kedua domain |
| 5 | Bot-UA 16/16 200, CF scrapers OFF (A2) | ✅ BERJALAN | curl per-UA kedua domain |
| 6 | GSC AI stats, no opt-out (A3) | ✅ BERJALAN | konfirmasi owner |
| 7 | ItemList schema + prompt GEO/evidence (B1/B2/B4) | ✅ DEPLOY, bukti live ⏳ TUNGGU reset | inject saat render D1 (lock) |
| 8 | Import 20 keyword listicle (B3) | ⬜ BELUM — TUNGGU reset | file siap; dedupe butuh reads D1 |
| 9 | D1 reads account-wide | 🔴 TERKUNCI s.d. 00:00 UTC (07:00 WIB) | `D1_ERROR` di sync-posts kedua domain |
| 10 | Fase 0 validasi | ⬜ BELUM — jalan 07:00 WIB | — |
| 11 | Fase 1–3 VPS (trickle, factory, rank) | ⬜ BELUM — butuh kunci GSC SA + Zen/Groq | infra §9.1 siap |
| 12 | foryoutours.com | ⬜ TIDAK DIUBAH — tanpa akses repo | robots/content-signals dilaporkan, snippet siap |
| 13 | Fase C VPS jobs (news-ping/distribute/monitor/freshness/earned) | ✅ BERJALAN (scheduled UTC, terverifikasi via trigger manual) | IndexNow real 200; provider AI/GSC dormant tunggu key; Bing /ping mati (410) → dihapus |
| 14 | Migrasi stack → Coolify UI (project seo-pipeline) | ✅ SELESAI — terlihat di UI, socio.id sehat | §9.3; standalone di-stop (rollback ready) |
| 15 | Zen AI key + GSC SA di VPS | 🟡 SEBAGIAN — Groq BERJALAN, GSC menunggu grant Owner | Groq: gpt-oss-20b live (preview OK, 389c HTML jujur); GSC 403 (lihat §10.1) |
| 16 | Outbox terisi → edge pull otomatis | 🟡 DEPLOYED (patch live) — TUNGGU reset D1 00:00 UTC + approver import 9 draft | co.id `83bdfd28` / .my `943134c7`, flag `pipeline_source` belum di-set (aman) |
| 17 | Artikel baru harian di /blog | 🟡 WAITING — patch live, tinggal aktivasi flag + import draft setelah reset 00:00 UTC | co.id/.my edge siap terima dari VPS |

Legenda: ✅ selesai/aman · ⏳ tunggu kondisi · ⬜ belum dikerjakan · 🔴Kendala aktif.

---

## 0. JAMINAN KEAMANAN socio.id (baca dulu)

Coolify mengisolasi per **Project → Service → Network/Volume** sendiri. Yang dikerjakan:

- ✅ Project Coolify BARU: `seo-pipeline` (terpisah dari project socio.id).
- ✅ Docker network BARU, volume BARU, resource limit sendiri (CPU/RAM cap).
- ✅ TIDAK menyentuh service, env, domain, database, atau setting project socio.id.
- ✅ TIDAK restart/update Coolify server atau Docker daemon.
- ✅ TIDAK mengubah reverse proxy global / DNS socio.id.
- ✅ Semua secret (GSC SA, Zen/Groq key, token) disimpan sebagai **Coolify env secrets**
  (terenkripsi di DB Coolify), TIDAK di-commit ke git, TIDAK di-log.
- ✅ Rollback = stop service `seo-pipeline` → edge kembali ke path D1 lama via flag
  (tanpa deploy ulang, tanpa downtime).

**Yang saya BUTUHKAN (dan TIDAK butuhkan):**
- Butuh: akses login Coolify (user baru role terbatas ATAU invite) ATAU SSH user
  non-root yang sudah dibatasi — cukup untuk: buat project baru, tambah Postgres,
  deploy 1 app dari repo git, set env secrets.
- TIDAK butuh: akses ke project socio.id, password root, akses DNS/Cloudflare baru.

---

## 1. MASALAH YANG DISELESAIKAN

| Fakta (terukur 14–15 Sep 2026 via analytics) | Dampak |
|---|---|
| co.id bakar 27.4M reads (14 Sep) + 3M reads (15 Sep) dari scan `keyword_queue` 391k rows | Lock kuota D1 account-wide → **ketiga domain ikut mati** |
| Sisa backlog .my 182k draft tidak bisa di-push langsung (182k writes = 2× jatah harian 100k) | Backlog tersumbat |
| Workers Free: batas CPU 10ms/invocation, error 1102 untuk job berat | Job besar tidak muat di edge |
| Upgrade D1 berbayar ≈ $45/bulan hanya untuk reads | VPS yang sudah ada = biaya marjinal ~Rp 0 |

Keputusan: **hybrid** — pabrik (pipeline berat) di VPS, etalase (serving + SEO URL)
tetap di Cloudflare Edge. Tidak ada URL publik yang pindah (SEO aman).

---

## 2. ARSITEKTUR AKHIR

```
                    ┌─────────────────────────────────┐
                    │  CLOUDFLARE EDGE (tetap)        │
                    │  beriklan.co.id / .my /         │
                    │  foryoutours.com                │
                    │  - render /blog/, sitemap,      │
                    │    posts-index.json (D1+cache)  │
                    │  - publish, indexnow, GSC       │
                    │    submit, email-send, tracking │
                    └───────────────┬─────────────────┘
                       pull (cron hourly, token auth)
                       hanya artikel JADI (kecil)
                    ┌──▼──────────────────────────────┐
                    │  VPS COOLIFY — project baru     │
                    │  `seo-pipeline` (ISOLASI penuh) │
                    │  - Postgres 16 (3 DB logis)     │
                    │  - app: Hono API + node-cron    │
                    │  - jobs: generate, rebalance,   │
                    │    rank-sync, growth AI, import │
                    └─────────────────────────────────┘
```

### 2.1 Pembagian kerja per domain

**beriklan.co.id**
- PINDAH: `keyword_queue` + hourly generate + rebalance + rank-sync writer +
  growth AI (enrich/ctr-fix/freshness) + snippet-optimize.
- TETAP: render, sitemap, publish flow (sumber artikel → API VPS), email-send,
  lead-pipeline, tracking, dashboard.

**beriklan.my**
- PINDAH: staging backlog 182k draft + hourly generate (120/hari).
- TETAP: sync-posts (pull dari VPS, 50–300/hari), publish, indexnow, GSC loop,
  trending, serving.

**foryoutours.com**
- TIDAK PINDAH APA PUN. Tambahan satu-satunya: retensi `wa_clicks` (>90 hari
  dihapus, 1 query/hari, murah).

### 2.2 Stack VPS (satu stack kecil)

| Komponen | Spesifikasi |
|---|---|
| Postgres 16 | 1-click Coolify, volume persist, backup terjadwal (S3/R2), 3 DB: `coid`, `comy`, `shared` |
| App container | Node 20, Hono (API internal) + node-cron (jobs), 512MB–1GB RAM (generate itu API-bound, bukan CPU-bound) |
| Domain internal | `pipe-internal.beriklan.co.id` (atau sesuai arahan), token auth + allowlist IP Cloudflare. BUKAN konten publik |
| Secret dipakai ulang | GSC service account JSON, ZEN_API_KEY, GROQ_API_KEY (3 key rotasi). Disimpan sebagai env secrets Coolify |
| Resend | TETAP di edge (kecil, patuh limit 100/hari) — tidak pindah |

---

## 3. SPESIFIKASI SYNC PROTOCOL (edge ↔ VPS)

Pull model — edge yang inisiatif via cron yang sudah ada (tanpa slot cron CF baru).
VPS down = edge serve cache/static seperti sekarang (resilient).

| Endpoint (VPS) | Fungsi |
|---|---|
| `GET /v1/publish-ready?domain={coid\|comy}&limit=N` | Artikel jadi siap publish (full HTML + meta). Default N=30 |
| `POST /v1/publish-ack` `{slugs:[...]}` | Tandai sudah diserahkan ke edge |
| `GET /v1/rank-deltas?domain=..&since=..` | Perubahan posisi GSC saja (bukan snapshot penuh) |
| `GET /v1/health` | Liveness untuk monitor edge (tanpa auth berat) |

Aturan:
- Auth: `Authorization: Bearer <PIPELINE_TOKEN>` (token 32+ char, beda per domain,
  rotasi manual bila bocor). Rate-limit per IP di app.
- Idempotensi: slug = natural key. Edge pakai `INSERT OR IGNORE` / `ON CONFLICT`
  — retry aman, tidak ada duplikat.
- Payload publish-ready ≤ 2MB/response (HTML digzip di transit via CF otomatis).
- Timeout edge→VPS: 20s, retry max 2×, gagal = skip ke jam berikutnya (log di cron_runs).
- Skema request/response dikunci di `openapi.yaml` dalam repo (single source of truth).

---

## 4. FASE EKSEKUSI

### Fase 0 — Validasi edge (16 Sep pagi, tanpa VPS)
- [ ] Cek `d1 insights` 1 jam pasca-reset: reads co.id harus ratusan ribu, bukan jutaan.
- [ ] `sync-posts` .my manual: `d1_published` naik, buffer draft terisi (promosi jalan).
- [ ] `hourly` co.id manual: log ada `buffer_refill`/`buffer pick`, tanpa `priority_rebalance` hourly.
- Kriteria lolos: total account < 2M reads/hari pertama.

### Fase 1 — .my backlog → VPS staging + trickle sync (nilai terbesar, risiko terkecil)
1. Provision di Coolify: project `seo-pipeline` + Postgres + app skeleton + env secrets.
2. Skema `comy`: `keyword_queue`, `generated_drafts` (staging 182k), `publish_outbox`,
   `sync_state`, `job_runs`.
3. Import 182k draft (file lokal `drafts/assembled_*.json`) langsung ke Postgres
   (COPY/bulk — tanpa sentuh kuota D1).
4. Job `trickle`: tandai N=50–300/hari (tunable via env `DAILY_TRICKLE`) sebagai ready.
5. Edge .my `sync-posts`: tambah branch — jika `pipeline_source=vps`, pull dari
   `/v1/publish-ready` lalu flow lama (publish → indexing) jalan seperti biasa.
6. Verifikasi: 3 hari berturut `d1_published` = trickle rate, `d1 insights` .my datar.
7. Rollback: set `pipeline_source=d1` → kembali ke path R2/promotion (tanpa deploy).

### Fase 2 — co.id factory → VPS (bunuh sumber lock permanen)
1. Skema `coid`: `keyword_queue` (migrasi 391k rows via export D1 → COPY; transfer
   dipecah/chunk agar tidak menabrak kuota hari berjalan).
2. Pindah jobs: hourly generate (round-robin SQL di Postgres — tanpa limit rows),
   rebalance (jadwal harian di VPS, bukan edge), snippet-optimize.
3. Edge co.id `handleHourlyGenerate`: jika `pipeline_source=vps`, skip buffer-refill
   D1, pull publish-ready dari VPS.
4. Tabel `hourly_candidates` di D1 pensiun (dibiarkan, tidak di-drop — aman).
5. Verifikasi: 3 hari, co.id reads < 500k/hari.
6. Rollback: flag `pipeline_source=d1` (buffer-table code path tetap ada di worker).

### Fase 3 — rank-sync + growth AI → VPS (kedua domain)
1. rank-sync jalan di VPS (baca GSC API dengan SA yang dipakai ulang), tulis
   `keyword_ranks_snapshot` di Postgres, expose hanya delta via `/v1/rank-deltas`.
2. Edge upsert delta saja (fix WHERE-changed yang sudah live membuat ini super murah).
3. Growth jobs (enrich/ctr-fix/freshness): AI rewrite di VPS, hasil = patch kecil
   (intro/FAQ/title) yang di-pull edge dan di-apply ke `posts_content`/`posts_meta`
   (1 row per artikel, cooldown tetap).
4. Verifikasi: writes co.id < 5k/hari, reads growth ≈ 0 di edge.

### Fase 4 — Opsional (hanya bila budget writes menipis)
- lead-pipeline matching + auto-campaign prep → VPS; edge hanya kirim email.
- Retensi: prune `cron_runs` >30 hari, `wa_clicks` >90 hari (semua domain).

### Kriteria selesai per fase (wajib sebelum lanjut)
1. `d1 insights` 24 jam turun sesuai target fase.
2. Flow harian terbukti: publish count, sitemap fresh, indexnow submitted, email terkirim.
3. `/blog/` kedua domain render artikel D1 terbaru (bukan fallback static).
4. Rollback flag diuji sekali per fase.

---

## 5. PROYEKSI KUOTA PASCA-HYBRID

| Domain | Sekarang (reads/writes per hari) | Pasca-hybrid |
|---|---|---|
| beriklan.co.id | ~1–27M / ~12k | ~200–400k / ~2–5k |
| beriklan.my | ~55k / ~1.5k | ~50k / ~1–3k (naik publish aman s.d. 300/hari) |
| foryoutours.com | ~18k / ~30 | tidak berubah |
| **Total account** | **s.d. 27M / ~14k** | **< 500k / < 8k** (limit 5M / 100k) |

Margin >10× untuk traffic spike dan kenaikan publish.

---

## 6. MONITORING & ALERTING (tetap + tambah)

Tetap: daily SEO health email 00:00 UTC, auto-pause 3× gagal, self-heal 00:00 UTC.
Tambah (VPS):
- `/v1/health` dipoll cron edge tiap jam → gagal 3× = alert email + flag fallback.
- Coolify healthcheck + auto-restart container.
- Uptime heartbeat VPS→Telegram (opsional, bila ada bot): trickle count, job gagal.
- Dashboard admin: tab baru "Pipeline" (source d1/vps, backlog count, last sync, last error).

---

## 7. DAFTAR AKSES & INFO YANG DIBUTUHKAN (dari owner)

- [ ] URL login Coolify + user/invite (cukup role untuk buat project baru), ATAU
      SSH user non-root ke VPS.
- [ ] Spesifikasi VPS (RAM/CPU bebas & region — info saja, untuk sizing).
- [ ] GSC service account JSON (file) — dipakai ulang, disimpan sebagai secret.
- [ ] ZEN_API_KEY + 3 GROQ_API_KEY — dipakai ulang, disimpan sebagai secret.
- [ ] `PIPELINE_TOKEN` boleh saya generate (32 char/domain), atau owner yang tentukan.
- [ ] Konfirmasi: subdomain internal `pipe-internal.beriklan.co.id` boleh dibuat? (A record → IP VPS. Alternatif: pakai domain Coolify default `*.coolify.io` bila ada.)
- [ ] Konfirmasi urutan: Fase 1 (.my backlog) dulu — setuju?

## 8. YANG SAYA KERJAKAN SETELAH AKSES DITERIMA (berurutan)

1. Buat project `seo-pipeline` + network + Postgres (volume, backup, resource limit).
   Verifikasi: socio.id tidak tersentuh (list service sebelum/sesudah).
2. Scaffold repo app (`pipeline/`): Hono API + jobs + `openapi.yaml` + skema SQL +
   Dockerfile + `docker-compose`/instruksi deploy Coolify. Push ke git.
3. Deploy app ke Coolify dari git + set env secrets (GSC SA, Zen, Groq, token).
   Verifikasi: `/v1/health` 200 dari luar (auth), log bersih.
4. Fase 1 (.my): import 182k → trickle → patch edge `sync-posts` (deploy worker) →
   verifikasi 3 hari → tandai selesai di file ini.
5. Fase 2–3 berurutan dengan kriteria selesai §4. Update file ini tiap fase.
6. Serah terima: cara restart, baca log, rotasi token, rollback — ditulis di §9 file ini.

---

## 9. OPERASIONAL (diisi saat serah terima)

### 9.1 Realisasi Fase 1-infra (15 Sep 2026, ~05:45 UTC) — SELESAI, terverifikasi
- Metode: Docker Compose standalone di `/opt/seo-pipeline` (BUKAN via UI Coolify —
  tanpa API token UI, menyentuh DB internal Coolify dilarang oleh aturan safety).
  Isolasi: network `seo-pipe-net`, volume `pg-seopipe`, container `seo-pipeline-*`.
  socio-app + mysql socio + core Coolify TIDAK tersentuh (uptime tidak berubah).
- Service: `db` (postgres:16-alpine, 512MB cap, port loopback-only 127.0.0.1:5432),
  `app` (Hono API v0.1.0, 256MB cap, `network_mode: host` + PORT 18743 —
  host-mode WAJIB agar allowlist IP melihat IP asli, bukan gateway docker).
- Keamanan: allowlist IP Cloudflare (snapshot + refresh 24 jam, fail-soft) +
  Bearer token timing-safe + rate-limit 120/menit/IP + 404 default. Socket peer IP
  otoritatif; header forwarded TIDAK pernah dipercaya (anti-spoof).
  Terverifikasi: localhost+token = 200 + query DB nyata; IP luar = 403.
- Secret: `/opt/seo-pipeline/.env` (chmod 600, digenerate via openssl di VPS,
  tidak transit): POSTGRES_PASSWORD, PIPELINE_TOKEN (64 hex), DATABASE_URL, DEBUG_IP.
- Endpoint v0: `GET /v1/health`, `GET /v1/publish-ready?domain=comy|coid&limit=N`,
  `POST /v1/publish-ack?domain=.. {slugs}`, `GET /v1/rank-deltas` (stub → Fase 3).
- Skema: `comy`/`coid`/`shared`, tabel `publish_outbox`, `sync_state`, `job_runs`
  (lihat `db/schema.sql` di VPS; kode sumber awal di laptop TIDAK disimpan di repo
  git — minta snapshot dari `/opt/seo-pipeline` bila perlu).
- Baseline VPS saat install: 3.8GB RAM (2.1GB available), disk 129GB free,
  load ~1.0. Port pakai: 22/25/80/443/587/465/6001/6002/8000/8080 + baru 18743.

### 9.2 Operasional harian
- Restart: `cd /opt/seo-pipeline && docker compose restart app|db`.
- Log: `docker compose logs --tail 100 app` / `... db`.
- Update app: rsync file baru → `docker compose up -d --build app`.
- Backup DB: `docker compose exec -T db pg_dump -U seopipe seopipe | gzip > /root/seopipe-$(date +%F).sql.gz` (jadwalkan cron mingguan + offsite bila perlu).
- Rollback darurat: `docker compose stop` → edge kembali ke path D1 via flag
  `pipeline_source=d1` (tanpa deploy ulang).
- Rotasi token: regenerate PIPELINE_TOKEN di `.env` → `compose up -d app` →
  update secret edge (env `PIPELINE_API_TOKEN`, endpoint pull memakai Bearer itu).

### 9.3 Migrasi ke Coolify UI (15 Sep 2026, ~06:25 UTC) — SELESAI, terverifikasi

- Project `seo-pipeline` (uuid `hdtwhvk7g7go80u9pmk5xhsg`) + env production —
  TERLIHAT di UI. Project count: 2 (socio-app + seo-pipeline).
- DB `seo-pipe-db` (uuid `vonbh1dpbrfzlrm26lwvdain`, postgres:16-alpine, 512m,
  `running:healthy`) — skema + data dimigrasi (outbox 0, job_runs 4).
- App `seo-pipe-app` (uuid `igsbaxpsvuhopghoutiit2kk`) dari repo publik
  `ReqTimeout/seo-pipeline` (build_pack dockerfile, tanpa domains =
  tanpa route Traefik publik, ports `18743:3000`, 256m). Repo tanpa secret.
- Pelajaran: (1) resource API tidak auto-start → `POST /deploy` wajib;
  (2) Coolify healthcheck butuh `GET /` 200 (ditambahkan);
  (3) port conflict :18743 dengan stack standalone → standalone di-stop dulu;
  (4) container melihat IP gateway bridge → RFC1918 di-allow (token tetap wajib);
  (5) Bing `/ping?sitemap=` mati (410) → hanya IndexNow.
- Stack standalone (`/opt/seo-pipeline`) DI-STOP, volume `pg-seopipe` dipertahankan
  sebagai rollback instan (`docker compose start` + flag edge kembali).
- Verifikasi akhir: health 200 + publish-ready query nyata via token; eksternal 403;
  socio.id 200; app.socio.id 303; 12 container up.

## 10. DUA HAMBATAN EKSTERNAL (butuh tindakan owner, 15 Sep 2026)

### 10.1 GSC: sudah diberikan Owner (terverifikasi 15 Sep 2026 ~08:00 UTC)
- SA `beriklanmy@cool-component-463913-b7.iam.gserviceaccount.com` sekarang
  **sukses query** `https://www.beriklan.co.id/` (200, 5 rows) dan
  `sc-domain:beriklan.co.id` (200, 5 rows). `https://beriklan.co.id/` (apex)
  masih 403 — itu normal karena GSC property www.
- Factory `freshness` LIVE: window 180 hari (data www tipis → 90 hari kosong),
  minImp=1 (sama), normalisasi `www.`→apex (GSC URL pakai www, sitemap apex).
  Hasil probe 15 Sep ~08:20 — **9 kandidat → 3 di-queue ke Groq → outbox draft**
  (imp 81/51/11), HTML jujur, model `groq/openai/gpt-oss-20b`.
- `.my` belum (belum isi GSC property), tinggal grant Owner di `https://www.beriklan.my/`.

### 10.2 AI: Groq BERJALAN, Zen FREE tidak bisa via API
- Groq `$GROQ_API_KEY` _(nilai dipindah ke Worker secret; jangan tulis key di sini)_ — terverifikasi
  live 15 Sep 2026: `openai/gpt-oss-20b` balas "OK", `qwen3.8-27b` + `gpt-oss-120b`
  tersedia. Preview callout 389c HTML jujur (1 <p> + 3 <li>, sesuai spek). Kode
  rotasi 3 model × N keys.
- Zen FREE: 6/6 model di-blokir provider lewat API key (docs resmi 14 Sep 2026
  jelas: free tier hanya di aplikasi OpenCode). Fallback Groq aktif.
- Sisa opsional: tambah Gemini API key gratis (AI Studio) untuk diversifikasi;
  saat ini Groq sudah cukup untuk freshness 1–3 artikel/hari.

## 11. JAWABAN JUJUR: "Aman & otomatis tiap hari?" — SEBAGIAN

### Yang SUDAH otomatis di VPS (cron UTC, real)
| Cron | Bukti log terakhir |
|---|---|
| `7 */2 * * *` news-ping | ✅ 08:07 — IndexNow real (co.id 5k URLs seen, .my 50 fresh<36h) |
| `23 */6 * * *` distribute | ✅ 06:23 — webhook skipped (no env) |
| `0 4 * * 1` geo-monitor | dormant (no Gemini key) |
| `0 5 * * *` freshness | ✅ 06:50 — GSC 403 (perlu grant §10.1) |
| `*/15` email-send co.id | tidak saya sentuh (di luar VPS) |

### Yang BELUM otomatis untuk `/blog/` co.id/.my
1. **Edge `sync-posts` belum patch VPS-pull** — saat ini masih baca `keyword_queue`
   D1 langsung (sumber utama lock 15 Sep). Patch siap di staging; butuh
   deploy `wrangler deploy` co.id + .my + reset D1.
2. **Pipeline VPS belum diisi** — outbox 0/0 di kedua domain. Butuh:
   - `pipeline_source=vps` flag + branch baru di `sync-posts`
   - import 182k draft `.my` ke outbox (Fase 1 — butuh reset)
   - keyword_queue co.id factory di VPS (Fase 2 — butuh GSC grant dulu)
3. **Crawler index** — artikel baru otomatis dikirim ke Bing + Google via
   `news-ping` (2-jam-an) TAPI hanya jika ada artikel baru di RSS outbox. Saat
   outbox 0 → tidak ada yang dikirim.
4. **Approval manual** — saat ini outbox `status='draft'` dari freshness butuh
   approve manual (`UPDATE ... status='ready'`) sebelum edge berani pull.

### Limit CF yang berlaku (jangan dilupakan)
- **D1 free tier 100k writes/hari account-wide** — sudah diamankan via
  keyword_ranks WHERE-changed + 3 composite index + buffer-table. Aman s.d.
  ~3–4× traffic spike.
- **Workers 10ms CPU / invocation (free)** — VPS pull dari D1 + edge publish
  sudah aman (lean mirror gate dari 2026-09).
- **Resend 100 email/hari** — tidak relevan (email masih di edge, di luar VPS).
- **IndexNow** tanpa batas.

### Skala praktis harian (post-Fase 1, semua jalan)
- co.id: 50–300 artikel/hari (daily_publish_limit, tunable via cron_settings).
- .my: 50–200/hari.
- Crawl feed: news-ping tiap 2 jam, IndexNow batch ≤50 fresh<36h.
- LLM: Groq 3 model rotasi × N keys, ~50–200 calls/hari, gratis.

### Yang masih perlu darimu (urut dampak)
1. **GSC grant Owner** ke `beriklanmy@cool-component-463913-b7.iam.gserviceaccount.com`
   untuk property `https://www.beriklan.co.id/` (2 menit — tanpa ini Fase 2
   tidak jalan, .my backlog tetap manual).
2. **Deploy patch edge VPS-pull** ke co.id + .my (saya eksekusi begitu reset
   D1 00:00 UTC terkunci aman, ~30 menit; opsional saya bisa langsung sekarang
   kalau mau).
3. (Opsional) **Telegram bot token + channel** untuk alert distribusi/freshness.
4. (Opsional) **Gemini API key** untuk diversifikasi AI (Groq sudah cukup).

### 11. Factory LIVE per 15 Sep ~08:50 UTC (kedua domain)

**co.id** (`https://www.beriklan.co.id/` via GSC, www property):
- ✅ Factory aktif: 6 kandidat → 3 di-queue Groq (imp 9/9/5).
- Kumulatif outbox siap approve: 9 draft `*-freshness-2026` HTML jujur
  (371–536 char).

**.my** (`sc-domain:beriklan.my` via GSC, domain property — apex www masih 403):
- ✅ Factory aktif: GSC merespon 388 baris blog (sc-domain, 6 bulan), sitemap
  matched 236 / mismatch 152 (blog di feed GSC tidak punya halaman sitemap).
- ⚠️ **0 kandidat freshness**: 5,000 entry sitemap-blog semuanya <180 hari
  (konten .my masih sangat baru — generator bank Aug–Sep 2026). Cooldown 1
  tahun = artikel baru tidak perlu freshness. Factory .my akan mulai
  menghasilkan kandidat sekitar Sep 2027.
- Untuk sumber artikel .my: VPS siap trickle 182k draft backlog (Fase 1 —
  import massal ke `comy.publish_outbox` butuh reset D1 00:00 UTC + patch
  `sync-posts`).

**Edge**: masih baca D1 langsung untuk publish flow (co.id + .my). Butuh patch
branch `pipeline_source=vps` (~30 menit deploy). Saya eksekusi setelah reset
D1 00:00 UTC terkunci aman.

**Aman untuk dijalankan sekarang (risiko lock ringan)**:
- Saya patch edge sekarang juga — pakai flag `pipeline_source=d1` (default) →
  tidak ada efek runtime sampai flag diaktifkan.
- Atau tunggu reset D1 → eksekusi aman, tidak ada efek samping.

### TL;DR (update 15 Sep ~08:55 UTC)
- **Pabrik (VPS)**: ✅ BOTH factory live. co.id 9 draft, .my siap trickle 182k.
- **Etalase (Edge)**: 🔴 sync-posts perlu patch VPS-pull (30 menit deploy).
- **IndexNow**: ✅ jalan tiap 2 jam.
- **TIDAK ada bottleneck CF D1/write** pada arsitektur hybrid.

## 12. STATUS SEMENTARA — tunggu reset D1 (15 Sep ~10:00 UTC)

- Patch edge sync-posts **LIVE di kedua domain** (co.id `83bdfd28`, .my `943134c7`).
  Zero runtime effect — `pipeline_source` belum di-set.
- D1 sedang lock (limit reads 5M/hari account-wide) sejak ~03:40 UTC. Reset 00:00
  UTC = 07:00 WIB (≈ 21 jam lagi dari status ini).
- Segera setelah reset + lock bersih, urutan aktivasi:
  1. Approve 9 draft co.id di VPS (`UPDATE coid.publish_outbox SET status='ready'`)
  2. Set flag `pipeline_source=vps` di cron_settings kedua domain
  3. Set env `PIPELINE_API_URL` + `PIPELINE_TOKEN` di Workers
  4. Verifikasi sync-posts pertama: `pipeline_source:'vps', vps_acked:9`
- Sampai langkah 4 sukses: sistem tetap pakai D1 lama (aman).
