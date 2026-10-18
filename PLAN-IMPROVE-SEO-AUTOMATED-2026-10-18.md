# PLAN — Perbaikan SEO Automated beriklan.co.id
**Tanggal:** 18 Oktober 2026 · **Status:** DRAFT (belum dieksekusi) · **Sifat:** backend/data/worker SAJA — **0 perubahan tampilan**

> Dokumen ini adalah hasil audit penuh 18 Okt 2026 (read-only) + rencana improve.
> Semua angka di sini terverifikasi via D1 remote, live HTTP, SSH VPS, dan git — bukan asumsi.
> ⚠️ Aturan SOP berlaku: tidak ada deploy/rebuild tanpa persetujuan eksplisit user. Tidak menyentuh
> `Layout.astro`, komponen Svelte, CSS, copy UI, gambar, font — kecuali diminta eksplisit.

---

## 1. Jawaban 3 Pertanyaan Utama

### Q1: "Semua artikel sudah punya keyword?"
| Fakta terverifikasi (18 Okt 2026) | Angka |
|---|---|
| Artikel AI (`posts_meta.generated=1`) | **16.299** |
| Artikel WordPress lama (`generated=0`) | 827 |
| Keyword dengan `article_slug` terisi (ter-link ke artikel) | **14.409 (88,4% dari artikel AI)** |
| Artikel AI lama (pra-pipeline, tanpa baris keyword) | ≈ 1.890 |
| Keyword total di queue | 391.482 |
| ↘ sudah jadi artikel (`published`) | 13.794 (3,5%) |
| ↘ draft generated menunggu publish | ~615 |
| ↘ pending | 374.973 |

**Kesimpulan:**
- ✅ Setiap artikel **baru** yang terbit otomatis punya baris keyword (`article_slug` terisi) — pipeline keyword→artikel tersambung rapi.
- ⚠️ Tapi dari sisi sebaliknya: **374k keyword belum jadi artikel** — ini normal untuk strategi long-tail, dan **329k di antaranya priority <70** (long-tail tipis). Yang bernilai komersial tinggal: **20.095 @p90–94** + **24.715 @p70–79** + 7 @p95+.
- ⚠️ Anomali: `jasa-view-live-tiktok` (740 pending, **0 publish**) dan `jasa-shopee` (240, 30 publish); plus 3.091 baris `service=''`/NULL (junk).

### Q2: "Publish & indexing konsisten berjalan?"
| Kanal | Status | Bukti |
|---|---|---|
| **Publish 15/hari** | ✅ KONSISTEN | `generated=1` per hari: **15, 15, 15, …, 15** (5–18 Okt, 14 hari berturut tanpa bolong) |
| IndexNow (Bing/Yandex/DDG/Seznam/Naver) | ✅ 100% backlog ter-ping | `indexnow_at IS NULL` tinggal **12 dari 17.769**; rotasi ulang >14 hari jalan; kapasitas 50/jam (1.200/hari) >> 15 artikel baru/hari |
| Artikel baru → Google | ✅ | masuk `gsc_submitted` dalam **≤1 hari** (24–25/hari, cocok dgn laju publish) |
| Sitemap | ✅ | 4 sitemap ping harian (204), `sitemap-blog.xml` + `news.xml` live & ter-cache |
| Verifikasi index Google | ⚠️ lambat | `indexed` terverifikasi baru **488**; 583 `gsc_submitted`; **16.698 backlog** belum disubmit ke GSC API |
| **Akar backlog** | — | Kuota **Google Indexing API = 200 URL/hari (hard limit Google)**. Dengan prioritas "terbaru dulu", backlog 16,7k butuh **≈90 hari**. IndexNow sudah cover semua, tapi Google tetap butuh jalur API/sitemap-nya sendiri. |

### Q3: "LLM — sudah pasti semua keyword terindex?"
**Tidak ada jaminan dapat 100%, dan itu wajar — tapi posisi kita sudah benar:**
- ✅ `robots.txt` mengizinkan SEMUA AI crawler (GPTBot, OAI-SearchBot, ClaudeBot, Claude-SearchBot, anthropic-ai, PerplexityBot/User, Google-Extended, CCBot).
- ✅ `llms.txt` (27 KB) + `llms-full.txt` (135 KB, 300 artikel terbaru + services + FAQ) live & serve dari D1.
- **Coverage crawler nyata** (tabel `ai_crawler_log`, 18 Okt):

| Bot | Slug unik terlihat | Interpretasi |
|---|---|---|
| **ClaudeBot** | **16.918** (≈98,8% katalog 17.126!) | hampir seluruh situs sudah "dibaca" Claude |
| OAI-SearchBot / PerplexityBot / CCBot | 181 / 187 / 46 | parsial, berputar |
| GPTBot | fetch sitemap 19× (semua sitemap), crawl artikel ~1 | baru tahap discovery |

**Kesimpulan:** samping "Google terindeks", LLM-side coverage sangat bergantung perilaku crawler masing-masing vendor. Tugas kita: **jaga keterbacaan (sudah ✅), pantau coverage mingguan, dan perkuat konten komersial** agar lebih sering dikutip.

---

## 2. Kondisi Sistem Terverifikasi (baseline 18 Okt)

| Mesin | Status | Catatan |
|---|---|---|
| Worker `beriklanweb` (1 cron `0 * * * *`, 24 job time-gate) | ✅ semua `ok` (20 run terakhir) | health ok; pending_indexing 16.649→ sekarang 17.769 total; posts_meta 17.126 |
| Email | ✅ | last sent 18 Okt 00:01; pending 12.953 (≈129 hari @100/hari — by design vs Resend free 100/hari) |
| Lead pipeline | ✅ | 15.343 queued; scrape jalan |
| Growth loop (enrich/ctr/freshness/winner) | ✅ | growth_log aktif; winner 17 Okt |
| VPS Coolify seo-pipeline | ✅ | tunnel `/v1/health` 200; news-ping/distribute/freshness OK |
| VPS host cron (geo-searxng, probe, gsc-pull) | ✅ | geo-searxng 240 baris/hari; fix domain berhasil (provider `searxng:<domain>`) |
| Socio engine (socio.id) | ✅ | log publish/measure harian rc=0 |
| GitHub automation | ✅ | commit harian `chore(gsc): pull stats` |
| Quick-win GSC | 📈 | 154 klik / 10.037 impressions (window terakhir) — tumbuh pelan, normal utk konten 1–2 bulan |
| **D1 quota** | ⚠️ mepet | top-20 query = **3,64M read/hari** dari kuota 5M/hari **AKUN** (7 DB); meter §8.2 sempat >500M → auto-pause nyala 13 & 16 Okt |

**Risiko struktural (dari audit):**
1. 🔴 Kode §8.2 (meter D1 + auto-pause) hanya ada di bundle live — tidak ada di git/lokal. Deploy lokal berikutnya = menghapus proteksi D1.
2. 🟠 D1 3,64M/5M/hari — margin tipis.
3. 🟠 Web repo +2.528 baris uncommitted; root repo 21 commit di belakang.

---

## 3. Rencana Perbaikan (7 fase, urut prioritas)

> 🚫 **SEMUA fase TIDAK mengubah tampilan** — tidak ada edit `Layout.astro`, Svelte, CSS, copy UI, gambar.
> ✅ Setiap perubahan produksi: backup `.bak-<ts>` → build/verify → deploy HANYA setelah izin user → verifikasi curl → rollback siap.

### FASE 1 — Proteksi & Housekeeping (P0, tanpa deploy visual)
1. **Recover §8.2** (meter `d1_read_meter` + gate auto-pause + sync-posts `auto_paused`) dari bundle live ke `web/src/worker-entry.js` → build → **deploy worker dengan `keep_assets` (script-only via CF API)** supaya dist/assets live TIDAK tersentuh.
2. **Commit + push** pekerjaan web yang menggantung (+2.528 baris; backup dulu) — version control, bukan deploy.
3. **`git pull` root repo** (21 commit) + commit dokumen audit/plan ini.
4. Jangan build/deploy `dist/` statis — perubahan halaman (view-live dll.) ditahan sampai user approve visual-nya nanti (di luar scope "no visual change").

### FASE 2 — Hemat D1 ≥1,5 juta read/hari (P0 — prerequisite semua volume)
| # | Aksi | Hemat |
|---|---|---|
| 2.1 | Index `lead_contacts(source_id)` (kolom 30×/hari tanpa index) | −465k/hari |
| 2.2 | Cache `COUNT(*)` berulang (email_queue, pending_indexing, drafts, dll.) ke `cron_settings`, update saat transisi status | −630k/hari |
| 2.3 | `generated_drafts WHERE status='committed'` → cursor `id > last` / simpan daftar ringkas di R2 | −700k/hari |
| 2.4 | `pending_indexing` scan: keyset + filter `indexnow_at`/`gsc_submitted_at` (sudah sebagian), audit sisa query | −400k/hari |
| 2.5 | `posts_meta ORDER BY iso_date DESC` (47×/hari full scan) → cache daftar slug di edge/R2 TTL pendek | −600k/hari |
| 2.6 | Hapus 3 index redundan di `keyword_queue` (idx_q_priority / idx_kq_priority / idx_keyword_queue_status_priority) | beban write ↓ |
| 2.7 | Setelah F2: verifikasi `wrangler d1 insights` (target <1,5M/hari) → baru boleh naikkan volume F3 | — |

### FASE 3 — Volume Publish & Coverage Keyword (P1)
1. **Naikkan publish 15 → 30/hari bertahap** (`PUBLISH_DAILY_LIMIT` secret) SETELAH F2 terbukti hemat. Target: 30/hari = 900/bulan; kapasitas IndexNow (1.200/hari) & GSC (200/hari) masih aman.
2. **Urutan prioritas keyword** untuk buffer: p90–94 (20.095) + p70–79 (24.715) dulu; p95+ (7) langsung.
3. **Long-tail p<70 (329k)**: tetap di queue TAPI tidak di-refill (status `deferred`/prioritas efektif) → buffer tidak "diganggu" long-tail.
4. **"Sepi viewers" (sesuai keputusan user: tidak penting)** → turunkan prioritas seed pain-point itu (prioritas <50 / tandai `rejected`) & stop generate varian baru di seed function.
5. **Fix mapping service kosong**: 3.091 baris `service=''`/NULL → reassign atau `rejected`. `jasa-view-live-tiktok` (740) → wire ke generator atau defer. `jasa-shopee` → review intent.
6. **Backfill mapping artikel lama** (opsional): 827 WP + ~1.890 AI lama → buat baris keyword sintetis dari title agar coverage mapping mendekati 100% (tanpa publish ulang).

### FASE 4 — Indexing Google (P1)
1. **Kebijakan rotasi GSC 200/hari tetap** (limit Google), tapi urutan diubah: `baru (≤7 hari)` → `prioritas komersial layanan inti` → `backlog` (bukan murni id DESC).
2. Tambah KPI mingguan dari `index-verify` (quota 300/hari): **% indexed terverifikasi per batch publish** (baseline: 488 indexed / 583 submitted).
3. Backlog `backfill-2026-08-26` (8.614) + `coverage-backfill` (1.769): setelah F2, evaluasi: tetap submit bertahap ATAU tandai prioritas rendah (mereka halaman lama; IndexNow sudah ping semua).
4. Verifikasi ulang quota guard `gsc_quota_used` (single-writer UTC — sudah benar per kode 1.12).

### FASE 5 — LLM/AEO (P1, tanpa UI)
1. **Monitor mingguan** `ai_crawler_log`: hitung % katalog per bot (ClaudeBot baseline 98,8%) → simpan snapshot di `growth_log` untuk tren.
2. Pastikan `llms-full.txt` regenerate otomatis tiap publish (verifikasi handler; kalau manual → jadikan D1-driven penuh).
3. Normalisasi nama bot di log (`claudebot` vs `ClaudeBot` — data hygiene filter).
4. Aksi manual user (sekali): submit `news.xml` + `sitemap-blog.xml` + `sitemap-index.xml` di **Bing Webmaster Tools** (IndexNow hub) — instruksi ada di AGENTS.md §News Sitemap.

### FASE 6 — VPS Coolify (P1)
1. **Commit patch `geo-searxng` runner ke repo `seo-pipeline`** + rebuild container via Coolify (izin user; restart = sentuh sistem berjalan) — hilangkan ketergantungan host-cron/docker-exec.
2. **Fix bug** `operator does not exist: text >= date` di job geo-searxng (cast `::date`).
3. Prune 3 baris junk `geo_mentions` (provider `searxng` tanpa domain).
4. (Opsional) alert Telegram saat seo-watchdog recreate container — sekarang diam-diam saja.
5. Dokumentasikan 3 host cron (probe `*/5`, watchdog `*/10`, gsc-pull `0 8`) ke `DEPLOY_OPERATIONS.md`.

### FASE 7 — Kebersihan & Monitoring (P2)
1. Email backlog 12.953: kebijakan — prioritaskan lead ber-`score` tinggi & dedupe; long-term turunkan (skip send) untuk kontak duplikat.
2. Hapus baris `cron_settings` inert (`distribute`, `news-ping` — bukan jalur worker).
3. Rapikan 3 salinan `worker-entry.js` usang (`/src`, `dryrun/`) + update `.last-deployed-sha` otomatis tiap deploy.
4. Laporan mingguan otomatis (email sudah ada utk SEO health harian) → tambah: publish count, % indexed terverifikasi, meter D1 tertinggi, coverage LLM.

---

## 4. KPI & Target

| KPI | Baseline 18 Okt | Target 30 hari | Target 90 hari |
|---|---|---|---|
| Read D1/hari (top-20) | 3,64M | < 1,5M | < 1,0M |
| Auto-pause triggered | 2× (13 & 16 Okt) | 0 | 0 |
| Publish/hari | 15 | 30 (setelah F2) | 30–45 terkontrol |
| Keyword high-intent tersisa (p≥70) | 44.859 | ~44.000 | ~42.000 |
| Indexed terverifikasi (GSC) | 488 | +2.000 | +5.000 |
| Coverage ClaudeBot | 98,8% | ≥98% (jaga) | ≥98% |
| Klik GSC (window) | 154 | 2× | 5× |

---

## 5. Guardrails (WAJIB selama eksekusi)
1. **Tanpa perubahan tampilan** — no edit Layout/Svelte/CSS/copy/gambar. Deploy worker = script-only (`keep_assets`) supaya assets live tak tersentuh.
2. **Backup** `.bak-<timestamp>` untuk setiap file krusial sebelum edit.
3. **Deploy hanya setelah**: build sukses + izin user + catat version_id stabil (rollback path).
4. **D1: verifikasi `EXPLAIN QUERY PLAN` = SEARCH** untuk setiap query baru (pelajaran insiden 2 Sep).
5. Rollback siap: `npx wrangler rollback <version-id>`; VPS rollback = Coolify redeploy versi sebelumnya.
6. Dokumen ini & hasil eksekusi di-commit ke git (root repo).

## 6. Checklist Eksekusi
- [ ] F1.1 Recover §8.2 dari bundle → file lokal (backup dulu)
- [ ] F1.2 Commit+push web working tree; pull root repo; commit docs
- [ ] F2.1 Index lead_contacts(source_id) + EXPLAIN verify
- [ ] F2.2–2.5 Cache COUNT + cursor + keyset + slug-list cache
- [ ] F2.6 Hapus 3 index redundan keyword_queue
- [ ] F2.7 Verifikasi insights < 1,5M; deploy worker script-only (izin)
- [ ] F3.1 Naikkan publish ke 30/hari (setelah F2, izin)
- [ ] F3.2–3.5 Prioritas buffer + demote sepi viewers + fix service kosong
- [ ] F4 Kebijakan rotasi GSC + KPI index-verify
- [ ] F5 Monitor LLM mingguan + llms auto + Bing sitemap (manual user)
- [ ] F6 VPS: commit runner + rebuild (izin) + fix trend query + prune
- [ ] F7 Housekeeping email/cron_settings/sha/backup files

**Berhenti dan tanya user untuk:** deploy worker, naikkan volume publish, rebuild VPS, dan keputusan quality-gate.
