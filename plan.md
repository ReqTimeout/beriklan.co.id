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
   `0 3 * * 1` (snippet-optimize) — persis `wrangler.jsonc` triggers. Script
   `beriklan-app` tetap ter-deploy; job-nya punya HTTP fallback
   (`/api/cron/anomaly-all|brain-all|audit-all`) kalau mau dihidupkan lagi.
3. **GSC permission**: service account HANYA punya akses property `https://www.beriklan.co.id/`
   (prefix URL). Apex `https://beriklan.co.id/` → 403; `sc-domain:beriklan.co.id` → 0 rows.
   Secret `GSC_SITE_URL` saat ini = `https://www.beriklan.co.id/` (satu-satunya yang data).
   Retest langsung 2026-08-25: secret di-switch ke apex → tetap 403 (SA belum ditambahkan),
   lalu di-revert ke www dan diverifikasi hidup lagi (gsc-loop 71 rows, rank-sync 63 rows).
   → Menunggu user menambahkan `beriklan-seo-bot@lgc-indexer.iam.gserviceaccount.com` sebagai
   Owner di GSC property apex/domain (Search Console → Settings → Users & permissions).
   Setelah selesai: `echo "https://beriklan.co.id/" | npx wrangler secret put GSC_SITE_URL`,
   lalu test `rank-sync` + `growth/gsc-loop` untuk pastikan data apex terbaca.
   Catatan: data www tipis (~60-70 rows), sehingga `growth-ctr-fix` masih 0 kandidat
   (clamp produksi minImp=50, maxCtr=0.02) — akan terisi setelah data apex masuk.
4. **Root www bisa HIT cache lama** (token tidak punya scope cache purge): `www.beriklan.co.id/`
   kadang 200 HIT; path lain 301. Menunggu expire atau purge manual via dashboard.
5. Renderer blog sudah D1-first + fallback asset statis, jadi semua job growth live tanpa rebuild.
