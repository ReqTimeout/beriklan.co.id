# SEO INDEXING + LLM-WINNING BLUEPRINT — Beriklan.co.id / .my

> **Untuk AI agent lain:** file ini adalah deep-dive sistem SEO yang sudah berjalan
> + hasil riset 2026 tentang cara menang di Google AI Overviews/AI Mode, ChatGPT,
> Perplexity, Gemini, Copilot — dan mapping eksekusinya ke VPS Coolify (project
> `seo-pipeline`) vs Cloudflare Edge.
> Ditulis: 15 Sep 2026. Verifikasi live: §8. Dokumen induk: `AGENTS.md`,
> `SEO-SYSTEM-REPLICATION.md` (replikasi infra), `plan.md` (eksekusi VPS).

---

## 1. CARA PAKAI FILE INI

1. Baca §2 (arsitektur funnel) untuk peta besar.
2. Baca §3 untuk lokasi kode presisi (file + fungsi + endpoint) sebelum menyentuh apa pun.
3. Baca §4 (hasil riset) SEBELUM mengusulkan perubahan konten — berisi data 2026,
   termasuk temuan "apa yang TIDAK berpengaruh" agar tidak buang effort.
4. Eksekusi via §5 (checklist berprioritas) dan catat hasilnya di §8.

---

## 2. ARSITEKTUR SISTEM EXISTING (funnel)

```
keyword_queue (391k co.id / 304k .my)
  │  import: /api/admin/keywords/import · rebalance harian 03:00 UTC
  ▼
GENERATE — hourly AI (Zen free → Groq fallback) · .my: bank 80 template → assembly lokal
  │  co.id: buffer hourly_candidates (hemat quota, 2026-09-15)
  ▼
PUBLISH — sync-posts lean (30/jam, max 300/hari co.id · 50/hari .my) → posts_meta/posts_content
  │
  ├─► INDEXING (§3D): sitemap-blog.xml + news.xml + IndexNow + GSC Indexing API + index-verify
  │
  └─► GROWTH (§3E): gsc-loop → enrich → ctr-fix → freshness (tulis langsung ke D1, live tanpa deploy)
```

Prinsip: semua yang berat (scan/mass-write) dilarang di request path; cron bertingkat;
gagal-aman (fallback static + auto-pause + self-heal 00:00 UTC). Detail infra di
`SEO-SYSTEM-REPLICATION.md`.

---

## 3. DEEP DIVE KOMPONEN (lokasi kode presisi)

Semua path di bawah ada di `web/src/worker-entry.js` kecuali disebut lain.
Token admin: co.id `beriklan-admin-2026`, .my `beriklan-my-admin-2026`.

### 3A. Keyword engine
- Tabel `keyword_queue` (service, city, intent, priority_score, status, article_slug).
- Import massal: `POST /api/admin/keywords/import` (dedupe by keyword_normalized).
- Rebalance prioritas: cron harian 03:00 UTC `/api/cron/priority-rebalance`
  (city+industri→90, view-live/marketplace→25). **Sengaja TIDAK hourly** (2026-09-15:
  3 UPDATE full-scan 391k rows/jam = penyebab lock kuota).
- Pick murah: tabel `hourly_candidates` (co.id) — refill ±1×/2 minggu, pick/jam indexed.

### 3B. Generation
- co.id `handleHourlyGenerate`: round-robin per core service dari buffer → artikel via
  `generateWithZenOrGroq` (Zen free non-reasoning → Groq `gpt-oss` dengan
  `reasoning_effort:low`, `max_tokens` ≥ 2048).
- .my `scripts/bulk_generate_all.py`: 80 bank template LLM (16 service × 5 varian) →
  assembly deterministik lokal 245k artikel (tanpa LLM per artikel) → push bertahap ke D1.
- Advancement: `UPDATE keyword_queue SET status='generated' ... WHERE keyword=?`
  (key by keyword — `id` NULL di seed rows).

### 3C. Publish
- `GET /api/admin/sync/posts` — mode **lean** default (tanpa GitHub, aman CPU free);
  `?mirror=1` = full mirror posts.json (berat, manual saja).
- Gradual: co.id 30/jam max 300/hari; .my 50/hari (tunable `daily_publish_limit`).
- Tiap publish: posts_meta + posts_content + advance keyword + enqueue `pending_indexing`.
- .my: promosi `pending→draft` 60/run (di-gate: hanya saat buffer <120).

### 3D. Indexing acceleration (tujuan: cepat terindex)
| Lapisan | Implementasi | Catatan kuota |
|---|---|---|
| Sitemap master | `sitemap-index.xml` → 6 sub-sitemap (static, blog, city, pillar, harga, tag) + auto-ping tiap 6 jam (`sitemap-ping`) | murah (cached) |
| `sitemap-blog.xml` | Dinamis dari D1 (termasuk artikel AI di luar static build) + edge cache | murah |
| `news.xml` | 10 artikel <36 jam + edge cache 30 mnt; empty tidak di-cache | murah; submit manual ke Bing Webmaster + Google Publisher Center (sekali) |
| IndexNow | `/api/cron/indexnow?count=50` tiap jam (Bing/Yandex/Seznam; key `2dac33f6…`) | gratis, tanpa kuota ketat |
| GSC Indexing API | `/api/cron/gsc-indexing?count=50` tiap 6 jam | **200 URL/hari** — prioritas untuk URL baru/penting |
| index-verify | `/api/cron/index-verify?count=50` — cek status index via GSC | **300 cek/hari** |
| index-cascade | `/api/cron/index-cascade?count=50&dry=1` — backfill katalog lama yang belum pernah diqueue | manual |

### 3E. Growth loop (feedback GSC → konten, langsung live)
- `growth-gsc-loop` (6 jam): query komersial ber-impresi tanpa halaman layak → `keyword_queue`.
- `growth-enrich` (harian 09:00): posisi 3–18 → rewrite intro (`class="growth-intro"`) + FAQ (`class="growth-faq"`), cooldown 21 hari.
- `growth-ctr-fix` (harian): impresi≥50 & CTR≤2% → rewrite `seo_title`/`seo_description` (H1 tidak berubah), cooldown 30 hari.
- `growth-freshness` (Senin 02:00): artikel >90 hari ber-impresi → callout update + `dateModified` jujur (`datePublished` tidak diubah).
- Audit: tabel `growth_log`, UI `/api/admin/growth-log`, probe AI `/api/admin/ai-test`.

### 3F. Fitur GEO-ready yang SUDAH ada (fondasi LLM)
- **FAQ deterministik 5 item/service+city** (`_buildFaqItems`) + **`FAQPage` schema**
  (`_buildFaqSchema`) — dirender di setiap artikel walau artikel asli tanpa FAQ.
- **Schema stack**: Organization + ProfessionalService (Layout) + BreadcrumbList +
  Article (otomatis per post) + FAQPage (opsional per halaman).
- **Internal-link mesh** (`_buildInternalLinksHtml`) — service page + artikel tetangga.
- **`llms.txt` + `llms-full.txt`** — Quick Facts brand, tabel 10 layanan, FAQ AI,
  100 artikel terbaru (cache 6 jam). Lihat §4.5 untuk penilaian jujur efektivitasnya.
- **`robots.txt`** — allow eksplisit 13 AI crawler + 9 Sitemap + pointer llms.
  Terverifikasi live §8.
- Freshness jujur (`growth-freshness`), `dateModified`, badge "Diperbarui".

### 3G. Monitoring
- Health email harian 00:00 UTC, auto-pause 3× gagal + alert, self-heal 00:00 UTC
  (migrate + resume + retry-clean), `cron_runs` + `cron_retry_queue`.

---

## 4. HASIL RISET 2026 — CARA MENANG DI LLM/AI SEARCH

> Sumber utama: Princeton GEO paper (Aggarwal et al. 2024, +40% visibility),
> Ranqo/arxiv 2606.20065 (100k+ prompt, Mar–Mei 2026), Chen et al. arxiv 2509.08919,
> GenOptima tracking Q1 2026, Search Engine Land, llmstxt.org v2, Limy.ai (500M events),
> 9to5Google/Mashable (GSC AI opt-out Jun 2026). Detail URL tersimpan di log riset sesi ini.

### 4.1 Fakta kunci (yang mengubah prioritas)
1. **Overlap sitasi antar-platform kecil** (~14% shared domains bahkan antara AI
   Overviews vs AI Mode milik Google sendiri). → Strategi harus multi-platform,
   tidak bisa mengandalkan satu mesin.
2. **Format listicle "Top N/Best X" mendominasi**: ~21% seluruh sitasi; di satu dataset,
   100% halaman onsite yang disitasi AI berformat ranking/listicle. Service page dan
   case study standalone ≈ nol sitasi langsung.
3. **78% sitasi mengarah ke corporate website** (sumber non-korporat: YouTube >
   Reddit > media editorial > Wikipedia). → Situs sendiri adalah senjata utama.
4. **AI Overviews mengutip dari 30% pertama konten 55% waktu** → blok jawaban cepat
   di 200 kata pertama bersifat kritis.
5. **Freshness diberi bobot eksplisit** — halaman baru/diperbarui diprioritaskan.
6. **Earned media bias**: AI search sistematis memilih media ketiga otoritatif
   dibanding konten brand-owned (tantangan terbesar untuk niche brand: brand kecil
   muncul hanya ~11% vs 73% household names).
7. **Sentimen tidak stabil** (flip 6.7× lebih sering dari mention) → monitor sentimen,
   bukan cuma mention.

### 4.2 Teknik konten yang terbukti (prioritas eksekusi)
1. **Definition lead** — awali tiap section dengan 1 kalimat definisi mandiri
   (mesin ekstrak definisi ringkas secara preferensial).
2. **Quick-answer block ≤200 kata pertama** — jawaban langsung 40–60 kata per H2
   sebelum elaborasi.
3. **Stacked JSON-LD**: Article + FAQPage + Organization (+ ItemList untuk listicle)
   dalam satu blok per halaman konten. (Sistem sudah punya 4 dari ini — tinggal +ItemList.)
4. **Evidence-dense writing** — angka, statistik, kutip sumber otoritatif; buang bahasa marketing.
5. **FAQ spesifik-query** (bukan generik) — pertanyaan = parafrase prompt user nyata.
6. **Comparison table** — sinyal sitasi terkuat di ChatGPT.
7. **Buat halaman listicle "Top N"** per vertikal (mis. "7 Jasa Iklan Facebook Terbaik
   untuk UMKM 2026") — format dengan probabilitas sitasi tertinggi.
8. **Freshness protocol** — update + `dateModified` jujur (sudah ada via growth-freshness).

### 4.3 Crawler access (robots + edge) — KRITIS
Pisahkan **training crawlers** vs **search/answer crawlers**:

| ALLOW (sitasi) | FUNGSI |
|---|---|
| `Googlebot`, `Bingbot` | Index dasar — AI Overviews di-grounding dari index Search |
| `OAI-SearchBot` | Index untuk ChatGPT Search/sitasi (**belum ada di robots kita — TAMBAHKAN**) |
| `ChatGPT-User` | Fetch saat user meminta (sudah ada ✅) |
| `PerplexityBot` + `Perplexity-User` | Search + fetch Perplexity (sudah ada ✅) |
| `Claude-SearchBot` | Discovery Claude (**belum ada — TAMBAHKAN**) |
| `Google-Extended` | Token training Gemini (sudah Allow ✅ — pertahankan; opt-out training ≠ opt-out sitasi) |

Catatan presisi:
- Block `GPTBot` (training) sambil Allow `OAI-SearchBot` (search) = mungkin dan
  didokumentasikan OpenAI. Keputusan saat ini: **Allow semua** (visibilitas > kekhawatiran training).
- **JANGAN PERNAH opt-out dari toggle GSC "AI Overviews/AI Mode"** (rollout global
  pasca UK Jun 2026) — opt-out = hilang dari sitasi AI Google, ranking biasa tidak naik.
- **Gotcha Cloudflare**: fitur "Block AI Scrapers"/Pay-Per-Crawl bisa me-403/402 bot
  walau robots.txt Allow. **Terverifikasi BERSIH** 15 Sep 2026: GPTBot, OAI-SearchBot,
  PerplexityBot, ClaudeBot semua dapat HTTP 200 di co.id + .my (§8).

### 4.4 Preferred Sources + GSC AI stats (peluang 2026)
- Google menambah **Preferred Sources** (user memilih situs favorit → muncul prominen
  di AI response) + **statistik AI di GSC** (impresi, halaman muncul di AI, per negara).
  → Aksi: pantau tab AI di GSC tiap minggu; CTA "jadikan sumber pilihan" di artikel
  (non-intrusif); brand query monitoring.
- AI Mode + agentic checkout/search-agent (I/O 2026) → halaman harga/paket harus
  machine-readable (tabel harga HTML bersih + Offer schema — backlog).

### 4.5 Penilaian jujur `llms.txt` (agar effort tidak salah arah)
Data Limy.ai (500M events/90 hari): hanya **408 request** ke /llms.txt dari AI search
crawler; Google menyatakan bukan faktor ranking. **llms.txt ≈ tidak berpengaruh ke
sitasi AI search.** Fungsinya nyata untuk coding agent (Cursor/Claude Code/Copilot).
Keputusan: **pertahankan** (murah, auto-generate) tapi JANGAN jadikan andalan —
kemenangan LLM ditentukan oleh struktur HTML + schema + freshness + earned media (§4.2).

### 4.6 GAP sistem sekarang vs riset (urut dampak)
1. ❌ Belum ada quick-answer block / definition lead di template artikel & bank template.
2. ❌ Belum ada halaman listicle "Top N" (format sitasi tertinggi).
3. ❌ Belum ada comparison table (sinyal ChatGPT).
4. ❌ Schema belum ada `ItemList` (+ `Offer` untuk halaman harga).
5. ❌ `OAI-SearchBot`, `Claude-SearchBot` belum eksplisit di robots.txt.
6. ❌ Belum ada GEO monitor (tracking mention/sitasi brand di 6 platform).
7. ❌ Earned media minim (YouTube deskripsi ber-link, direktori bisnis, profil konsisten).
8. ⚠️ news-ping + distribute (auto-ping artikel fresh ke IndexNow/webhook/Telegram)
   terdokumentasi di AGENTS.md tapi **tidak ada di kode** → bangun di VPS.

---

## 5. RENCANA AKSI (mapping Coolify vs Edge)

### Fase A — Edge, tanpa VPS (cepat, murah)
- [x] A1. robots.txt: tambah `OAI-SearchBot` + `Claude-SearchBot` eksplisit (Allow, Disallow /api/). DONE 15 Sep 2026 — live co.id (`1f05ce77`) + .my (`ece45456`).
- [ ] A2. Verifikasi ulang bot-UA (skrip §8) tiap deploy + pastikan CF "Block AI Scrapers" OFF.
- [x] A3. JANGAN sentuh toggle opt-out AI di GSC; cek tab AI stats mingguan. Owner konfirmasi 15 Sep 2026: tab AI stats ENABLE, tidak opt-out. ✅
- [x] A4a. `ItemList` schema otomatis untuk artikel listicle (deteksi judul Top-N → dari <h3>, kedua domain, deploy `a4012f8d`/`15fd2dae`). `Offer` halaman harga = backlog (butuh push frontend).

### Fase B — Template konten (pengungkit GEO terbesar, sekali ubah → semua artikel baru)
- [x] B1. Generator co.id: quick-answer 40–60 kata + definition lead tiap H3 + tabel (prompt, deploy `0df598ee`). Varian listicle Top-N otomatis by keyword (deploy `a4012f8d`).
- [x] B2. Prompt generator .my (EN+MS): quick-answer + definition lead + tabel (script lokal, berlaku generasi bank berikutnya).
- [ ] B3. 10 keyword listicle per domain SIAP import pasca-reset (`listicle-keywords-id.json`, `listicle-keywords-en.json`) — import via `/api/admin/keywords/import` setelah 00:00 UTC. (File DONE 15 Sep; import ditahan karena dedupe SELECT butuh reads D1 yang sedang lock.)
- [x] B4. Evidence rule MASUK prompt (co.id + .my EN/MS, deploy menyusul): tiap angka/statistik/perbandingan wajib sumber. Tanggal terbit sudah tampil di metadata bar semua artikel; badge "Diperbarui" + `dateModified` untuk artikel refresh (growth-freshness). ✅

### Fase C — VPS `seo-pipeline` (jobs baru, tanpa beban D1)
Status 15 Sep 2026: SEMUA TER-DEPLOY + scheduled (UTC) + terverifikasi trigger manual.
IndexNow real → HTTP 200 (Bing + api.indexnow.org). Temuan: Bing `/ping?sitemap=`
MATI (410) → dihapus dari kode, IndexNow penggantinya.
- [x] C1. **news-ping** tiap 2 jam (`7 */2 * * *`): news.xml + sitemap-blog.xml →
      fresh<36h → IndexNow batch (≤50). Terverifikasi: submit real 200.
- [x] C2. **distribute** tiap 6 jam (`23 */6 * * *`): IndexNow + webhook/IFTTT +
      Telegram — env-gated (skip tercatat bila kosong).
- [x] C3. **GEO monitor** Senin (`0 4 * * 1`): 24 prompt → Gemini/OpenAI/Perplexity
      (env-gated) → `shared.geo_mentions` + alert kompetitor. DORMANT tunggu API key.
- [x] C4. **Freshness rewriter** harian (`0 5 * * *`): kandidat GSC → draft AI →
      outbox `status='draft'` (approve manual → 'ready'). Preview deterministik
      always-on. DORMANT tunggu GSC_SA_JSON + Zen/Groq key.
- [x] C5. **Earned-media helper**: endpoint YouTube desc + NAP — FULLY WORKING, manual.

### Fase D — Pengukuran (tanpa ini = buta)
- [ ] D1. GSC: impressions + tab AI stats mingguan (simpan snapshot).
- [ ] D2. `index-verify` state per URL (sudah ada) → dashboard tab Indexing.
- [ ] D3. GEO monitor §C3 sebagai KPI sitasi (target awal: muncul di ≥1 platform
      untuk 10 prompt uang dalam 90 hari).
- [ ] D4. Atribusi: UTM/link khusus di llms-full + halaman listicle untuk deteksi
      referral AI (ChatGPT/Perplexity mengirim referrer).

---

## 6. ATURAN ANTI-RUSAK (untuk agent berikutnya)

1. Berita/penelitian di §4 kedaluwarsa cepat — verifikasi ulang klaim >6 bulan sebelum dipakai.
2. Jangan mengorbankan readability manusia demi mesin (keyword stuffing = mati dua-duanya).
3. `datePublished` tidak pernah diubah; freshness selalu via `dateModified` + konten visible.
4. Setiap klaim "AI mengutip kita" wajib bukti (screenshot/response log + tanggal), bukan asumsi.
5. Semua job baru default di VPS; edge hanya untuk serving + write kecil. Lihat `plan.md` §0
   untuk isolasi socio.id.

---

## 7. REFERENSI SILANG

- `AGENTS.md` — playbook harian (copy, SEO, deployment, email, lead pipeline).
- `SEO-SYSTEM-REPLICATION.md` — blueprint replikasi infra ke domain baru.
- `plan.md` — eksekusi hybrid VPS (fase, akses, serah terima).
- `SEO-GROWTH-SYSTEM.md`, `SEO-PLAYBOOK.md`, `COPY-BIBLE.md` — standar konten.

## 8. LOG VERIFIKASI LIVE

| Tanggal (UTC) | Cek | Hasil |
|---|---|---|
| 2026-09-15 ~04:40 | UA GPTBot/OAI-SearchBot/PerplexityBot/ClaudeBot → `/blog/` co.id + .my | **200 semua** (tidak ada edge block) |
| 2026-09-15 ~04:40 | `robots.txt`, `llms-full.txt`, `news.xml`, `sitemap-blog.xml` co.id + .my | **200 semua** |
| 2026-09-15 ~05:30 | A1: `OAI-SearchBot` + `Claude-SearchBot` Allow di robots.txt live co.id + .my | **OK kedua domain** |
| 2026-09-15 ~05:30 | A2: 8 bot-UA × 2 domain (GPTBot, OAI-SearchBot, ChatGPT-User, PerplexityBot, Perplexity-User, ClaudeBot, Claude-SearchBot, Google-Extended) | **16/16 HTTP 200** — CF "Block AI Scrapers" OFF terbukti |
| — | A4-ItemList live proof (butuh render D1, lock sampai 00:00 UTC) | PENDING reset |
| — | Ulangi tabel ini tiap ada perubahan robots/CF/worker | — |
