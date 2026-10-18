# SEO GROWTH SYSTEM — ForYouTour (25 Agu 2026)

> Sistem untuk **foryoutours.com** (pasar Indonesia). Versi **foryoutours.my**
> (pasar Malaysia, bahasa Melayu) berdiri sendiri: `SEO-GROWTH-SYSTEM-MY.md`.

Dokumen hidup: cara sistem ini mencari keyword, menulis artikel hemat token
tanpa thin content, dan loop otomatis yang konsisten mendorong ranking Google.
Prinsip growth-hack: **coverage dulu (semua keyword punya halaman), lalu
indexing secepat mungkin, lalu dorong ranking lewat internal link + freshness
— semuanya otomatis.**

---

## 1. ARSITEKTUR BESAR

```
RISET KEYWORD ──► QUEUE (seo-keyword-opportunities.json)
                        │  P0/P1/P2 + status + anti-cannibalization
                        ▼
GENERATOR ──► SHARD KONTEN (src/data/posts-part-*.json)
                        │  template + data matrix, TANPA LLM per artikel
                        ▼
PUBLISH ──► ① build statis (dist terkunci e774cd92, 15.668 URL)
            ② D1 hybridge worker → /blog/<slug> live tanpa build
                        │
                        ▼
INDEXING ──► sitemap(-d1).xml + IndexNow (Bing/Seznam) + ping GSC
                        │
                        ▼
RANKING ──► internal link rotation + pillar promotion + freshness
            + GSC feedback (promosi kandidat posisi 5–15)
                        │
                        └──► balik ke RISET (query GSC baru = keyword baru)
```

Dua jalur tayang:
- **Statis** — 15.668 halaman dari build terkunci e774cd92 (design-lock:
  JANGAN di-rebuild/deploy ulang; rollback ID e774cd92-... jika berubah).
- **D1 hybrid** — worker `scripts/d1-blog/worker-overlay.js` di Pages;
  artikel baru tayang detik itu juga via `POST /~fytpub/publish`, tanpa
  build & tanpa deploy. Format artikel = template yang SAMA dengan halaman
  statis (CSS/struktur identik, JSON-LD Article + FAQPage + Breadcrumb,
  breadcrumb Home→Blog→Judul) → tetap AEO-ready dan tampil seragam di
  `/blog/<slug>`.

Skala target saat ini: **19.969 slug keyword target** (posts-meta ∪
posts-auto). 15.668 sudah live statis; **10.540 sisanya sedang di-rollout
via D1** (lihat §7 batch-publish).

---

## 2. PENCARIAN KEYWORD (sumber + pipeline)

### 2.1 Sumber keyword (5 lapis)

| Lapis | Sumber | Script | Output |
|---|---|---|---|
| 1 | Seed bisnis: 6 armada × 12 paket × bulan madu × hub (bandara/stasiun/terminal) × base kota × acara | `scripts/keyword_research.py`, `scripts/keyword_research_paket.py` | kombinatorik matrix → slug + prioritas |
| 2 | Matriks destinasi (kota wisata × durasi × origin × harga × acara × segmen) | `scripts/generate_seo_opportunities.py` | `src/data/seo-keyword-opportunities.json` (6.771 entri) |
| 3 | Ekspansi pola terbukti (contoh: "stasiun X", "bandara buka lagi") | `scripts/expand_stasiun_husein.py` | batch ribuan slug dari 1 pola |
| 4 | **GSC feedback** (query riil yang sudah dapat impresi/klik) | `.github/workflows/gsc-sync.yml` + `scripts/gsc_sync.py` | kandidat `gsc-proven` + 1.276 kandidat promosi posisi 5–15 |
| 5 | Kompetitor (happytour, happybus, dll: pola rute × armada × acara) | riset manual/plan.md §1 | seed pola baru |

### 2.2 Filter sebelum jadi artikel (hemat usaha, anti sampah)

Semua kandidat masuk queue `seo-keyword-opportunities.json` dengan field:
- `priority`: P0 (money langsung) / P1 (high intent) / P2 (noise/booster)
- `intent`, `service`, `cluster`, `target_url` (pillar mana yang didukung)
- `commercial_signal` (true/false)
- `cannibalization`: dicek terhadap halaman yang sudah ada — slug yang
  menabrak halaman pilar/existing DILARANG tayang (mencegah saling makan
  ranking). Ini sebabnya 214 kandidat P2 & yang cannibal tidak diotomasi.
- `status`: candidate → generated (append-only; slug tidak pernah diganti)

### 2.3 Loop balik GSC → keyword baru (growth engine tertutup)

1. gsc-sync fetch query+URL dari Search Console → `gsc_data.json` (D1/KV).
2. Query yang punya impresi tapi belum ada halamannya → ditulis sebagai
   kandidat `gsc-proven` (sinyal permintaan NYATA, bukan tebakan).
3. Cron worker `/auto-seo` mempublish 2 artikel/hari dari kandidat itu.
4. Setelah tayang → IndexNow → Google meng-crawl → balik ke langkah 1.

CATATAN: gsc-sync saat ini MATI karena secret `GSC_CREDENTIALS` belum
dipasang di GitHub (Settings → Secrets → Actions). Ini prioritas #1 untuk
accelerator indexing (2.000 URL Inspection/hari).

---

## 3. GENERATOR ARTIKEL — HEMAT TOKEN, BUKAN THIN CONTENT

Strategi inti: **template + variabel, BUKAN LLM per artikel.** LLM hanya
untuk lapisan pengayaan (enrichment), bukan produksi massal.

### 3.1 Jalur template (gratis token, tetap 600–1.200 kata)

- `scripts/generate_article.py` / `generate_article_paket.py` /
  `generate_article_paket.py`: mengisi template HTML per tipe (armada,
  paket, transfer, destinasi) dengan variabel (kota, armada, rute, acara,
  FAQ generik-terarah, tabel rencana, checklist penawaran, CTA WhatsApp).
- Hasil: artikel 650+ kata dengan struktur H2, tabel, FAQ <details>,
  internal link ke pillar, JSON-LD. Disimpan ke shard
  `src/data/posts-part-*.json` + `posts-auto.json`.
- Quality gate di worker: `content.split(/\s+/).length < 650` → ditolak
  (lihat `opportunityArticle()` di `cloudflare-cron/worker.js`). Di
  batch-publish: konten bersih < 1.500 karakter → skip.
- Kenapa tidak thin: strukturnya lengkap (answer-first, tabel perbandingan,
  checklist, FAQ, CTA), fokus pada 1 intent per halaman, dan setiap artikel
  memuat info spesifik kota/rute — bukan spun-text generik.

### 3.2 Jalur LLM — hanya enrichment, kuota terkontrol

- Kandidat: halaman yang sudah ranking posisi 5–15 di GSC (1.276 URL di
  `gsc_data.json`) — halaman yang SELANGKAH lagi masuk top 10.
- Workers AI (binding AI, free 10K neurons/hari ≈ beberapa artikel/hari):
  perbaiki intro agar menjawab query lebih langsung + tambah FAQ dari
  query People-Also-Ask → UPDATE konten → `/refresh?slugs=`.
- Status: belum dideploy (butuh binding AI + keputusan budget). Ini
  pengungkit ranking terbesar per-token: sedikit artikel, dampak besar.

### 3.3 Token cost per jalur

| Jalur | Biaya LLM | Volume |
|---|---|---|
| Template matrix | 0 | 19.969 halaman |
| D1 opportunity article (worker `opportunityArticle`) | 0 | 2/hari otomatis |
| batch-publish konten lama | 0 | 10.540 halaman |
| Workers AI enrichment | ~beberapa ribu token/artikel | 3–10/hari (kuota free) |

---

## 4. FLOW DORONG RANKING (loop konsisten, tanpa tangan manusia)

```
TAYANG (detik 0)
  └─ publish endpoint otomatis: rebuild sitemap-d1.xml
     + IndexNow Bing & Seznam (URL baru dikirim <1 menit)
     + (kalau GSC secret aktif) URL Inspection request

HARI 1–7: Google crawl via sitemap + IndexNow
  └─ Durable Object cron (alarm tiap jam, hemat kuota free plan):
     - freshness: update ringan + lastmod pada artikel lama (sinyal hidup)
     - rotate_links: internal link antar artikel terkait (distribusi authority)
     - promote_pillars: semua artikel baru WAJIB link ke pillar money
       (/sewa-*, /paket-wisata, /paket-bulan-madu)

MINGGU 2+: GSC feedback loop
  └─ gsc-sync baca posisi; posisi 5–15 → enrichment (Workers AI)
  └─ query baru tanpa halaman → jadi artikel baru (auto, 2/hari)
  └─ query dengan CTR rendah → perbaiki title/intro (antre enrichment)

BULANAN: coverage sweep
  └─ generate_seo_opportunities.py → kandidat baru ke queue
  └─ batch-publish merollout apa pun yang belum live
```

Kenapa loop ini menaikkan rank secara konsisten (growth-hack logic):
1. **Coverage total dulu** — 19.969 halaman = 19.969 taruhan ranking;
   long-tail (mis. "sewa elf untuk pernikahan") kompetisinya rendah →
   menang cepat, tarik authority ke pillar.
2. **Indexing secepat mungkin** — halaman tak terindeks = nol. IndexNow +
   sitemap ping memangkas hitungan minggu jadi jam/hari.
3. **Authority mengalir ke money pages** — semua artikel info/booster
   link ke 6 pilar armada + paket + bulan madu (pillar-cluster klasik).
4. **Freshness** — update berkala membuat Google sering revisit; lastmod
   baru = sinyal konten terawat, penting untuk query harga/jadwal.
5. **Data-driven** — yang menentukan artikel berikutnya BUKAN tebakan,
   tapi query riil Google (GSC). Sistem belajar dari demand sendiri.
6. **Konsisten gratis** — semua jalan di free tier (CF Workers cron via
   DO alarm, KV, D1, GitHub Actions) tanpa biaya bulanan.

---

## 5. FITUR AUTOMATED SEO YANG SUDAH JALAN

| Fitur | Lokasi | Jadwal/Trigger |
|---|---|---|
| Scheduler hourly tanpa cron trigger (DO alarm + window gate 2×/hari) | `cloudflare-cron/worker.js` (PaketScheduler) | otomatis |
| Publish artikel → live detik itu + sitemap + IndexNow | overlay `/~fytpub/publish` | on-demand + otomatis |
| Auto-publish 2 artikel opportunity/hari | worker `/auto-seo` (DO) | harian (gate KV); `?force=1&dry=1` |
| IndexNow dedup via KV (hanya URL baru) | runCron + STATE_KV | 2×/hari |
| `/refresh?slugs=` — IndexNow targeted (feedback rank tracker) | worker cron | manual/otomatis |
| Internal link rotation & pillar promotion | `rotate_links.py`, `internal_linker.py`, `promote_pillars.py` + worker | runCron |
| Freshness update konten lama | `freshness.py` | runCron |
| Sitemap: index + child statis + child D1 (`sitemap-d1.xml`) | overlay | tiap publish |
| Dashboard monitoring | `https://foryoutour-seo-cron.3smedianet.workers.dev/dashboard(/tech,/keywords)` | selalu |
| Anti-tabrakan canonical (409 jika slug sudah statis) | overlay publish | selalu |
| Delete + invalidasi cache | `/~fytpub/delete` | manual |
| JSON-LD Article/FAQPage/Breadcrumb di semua artikel | overlay template.js | selalu |
| llms.txt | overlay `/llms.txt` | selalu |

### Yang akan/telah dideploy oleh asisten di sesi ini

1. **batch-publish.mjs v2 (AKTIF SEKARANG)** — rollout 10.540 artikel gap
   (ada di queue, konten siap, tapi tak pernah ikut build). Source of truth
   "sudah live" = sitemap produksi. Background, state di
   `scripts/d1-blog/.batch-state.json`, log `.batch-run.log`.
2. **worker cron v1f3f25e3** — `processOpportunityKeywords` publish via
   D1 (dulu cuma commit GitHub → tak pernah live di build terkunci).
3. **Rencana deploy berikutnya (butuh keputusan/akses user):**
   - a. Injeksi daftar artikel D1 ke halaman index `/blog/` + category
     pages via overlay agar artikel baru MUNCUL di daftar blog (menyentuh
     output frontend → sesuai AGENTS.md perlu konfirmasi user dulu).
   - b. `GSC_CREDENTIALS` secret → gsc-sync hidup lagi (2K Inspection/hari,
     data posisi untuk loop promosi).
   - c. Binding Workers AI + job enrichment posisi 5–15.
   - d. Matikan "Managed robots" Cloudflare untuk bot AI (GPTBot,
     PerplexityBot, ClaudeBot, dll) jika ingin muncul di AI search
     (ChatGPT/Perplexity/Claude answers).
   - e. Cron `/auto-seo` dinaikkan dari 2 → 10/hari setelah batch selesai
     (kuota IndexNow & CPU masih aman).

---

## 6. INVENTARIS SCRIPT (pendukung apa)

| Script | Peran | Dipakai oleh |
|---|---|---|
| `keyword_research.py`, `keyword_research_paket.py` | riset kombinatorik → queue | manual (awal) |
| `generate_seo_opportunities.py` | matrix destinasi + status queue + append konten | manual + sumber worker |
| `expand_stasiun_husein.py` | ekspansi 1 pola terbukti → ribuan slug | manual |
| `gsc_sync.py`, `gsc_diagnose.py` | tarik data GSC (query, posisi, indexing) | GitHub Action 6-jam |
| `rank_tracker.py` | pantau posisi keyword uang | manual/cron |
| `paket_seo_pipeline.py`, `content_quality_pipeline.py` | orkestrasi generate+QC | manual |
| `internal_linker.py`, `rotate_links.py`, `promote_pillars.py` | arus authority ke money pages | runCron |
| `freshness.py` | sinyal konten hidup (lastmod) | runCron |
| `indexnow_submit.py`, `ping_sitemaps.py`, `auto_index.py` | dorong indexing | runCron/manual |
| `backlink_outreach.py` | daftar prospek backlink (manual) | manual |
| `scripts/d1-blog/batch-publish.mjs` | rollout massal tanpa build | CLI (sekarang jalan) |
| `scripts/d1-blog/publish.mjs`, `selftest.mjs`, `clean-content.mjs` | publish satuan, self-test, bersih HTML | CLI |
| `scripts/d1-blog/worker-overlay.js` | otak D1 hybrid di produksi | deployed |

Endpoint penting:
- `https://foryoutour-seo-cron.3smedianet.workers.dev/auto-seo?dry=1` — cek kandidat
- `.../auto-seo?force=1` — paksa publish batch harian
- `.../dashboard/tech` — status cron, commit, indexing
- `https://www.foryoutours.com/~fytpub/status` (butuh token) — jumlah posts D1

---

## 7. STATUS ROLLOUT 10.540 (25 Agu 2026)

- Ditemukan: 19.969 slug target vs 15.668 di sitemap produksi → gap 10.540
  (404 live), semua punya konten lengkap ≥1.500 char bersih.
- batch 20 validasi: 200 OK, title benar, masuk sitemap-d1, IndexNow OK.
- Rollout penuh: background 27 chunk × 400 (±1.3 artikel/detik, ETA ±2.5 jam).
- Cek selesai: `grep -c SEMUA_CHUNK_SELESAI scripts/d1-blog/.batch-run.log`
- Verifikasi akhir: jumlah slug di `state.published` vs jumlah URL di
  `https://www.foryoutours.com/sitemap-d1.xml`.

Catatan tampilan: artikel D1 hidup di `/blog/<slug>` dengan format IDENTIK
halaman statis, dan masuk sitemap. Daftar di `/blog/` (halaman index blog)
masih versi build lama sehingga belum memuat artikel baru — fitur injeksi
daftar menunggu konfirmasi user (§5.3a).

---

## 8. CHECKLIST GROWTH-HACK (urutan eksekusi)

- [x] Coverage: semua keyword target PUNYA halaman (statis + rollout D1)
- [x] Uniform format + schema di semua artikel (AEO-ready)
- [x] Indexing push otomatis tiap publish (IndexNow + sitemap)
- [x] Auto-publish harian dari queue (cron, tanpa tangan)
- [ ] **GSC_CREDENTIALS secret dipasang** → inspection 2K/hari + data loop
- [ ] Injeksi artikel D1 ke index `/blog/` (butuh approve)
- [ ] Enrichment Workers AI untuk posisi 5–15 (butuh approve binding)
- [ ] Buka bot AI di Managed robots (opsional, tergantung target AI search)
- [ ] Naikkan auto-seo 2→10/hari bila batch selesai & IndexNow stabil
- [ ] Backlink outreach (satu-satunya langkah manual: `backlink_outreach.py`
      kasih daftar prospek; kirim email/WA dari sana) — authority eksternal
      adalah batas akhir yang tidak bisa diotomasi penuh.

Prinsip akhir: **jangan kejar viral, kejar akumulasi.** 19.969 halaman yang
terindeks rapi + internal link disiplin + freshness = compounding ranking.
Nomor 1 datang dari sistem yang tidak pernah berhenti, bukan dari 1 artikel
sempurna.
