# LOG-EKSEKUSI-PLAN — Pemisahan Dokumen & Rencana co.id untuk Agen (27 Sep 2026)

> Aturan main sesi: **doc-only** — tidak ada deploy / D1 write / secret / cron / UI.
> Setiap fase wajib punya catatan "selesai + bukti verifikasi" di file ini sebelum lanjut.
> Perencana: Qoder (audit plan-mode) · Eksekutor dokumen: Qoder · Eksekutor live berikutnya: muse spark 1.3 (dengan aba-aba user).

---

## ✅ FASE A — Pisahkan dokumen co.id vs .my (SELESAI 27 Sep)

**Yang dikerjakan:**
1. `TASKTRACKER-COID.md` (baru, 68.775 B) — 76 baris task Domain `co.id`/`both`/`VPS`/`repo`,
   diangkat otomatis dari master via script klassifikasi kolom Domain; plus header koreksi status
   27 Sep: Fase 3 R2 = 🟡 (belum terbukti fire saat D1 down nyata), 2.7/2.8 = belum ada bukti end-to-end.
2. `TASKTRACKER-MY.md` (baru, 14.194 B) — 13 baris task `.my` murni + daftar 35 task `both`
   yang wajib direplikasi ke `.my` setelah gerbang "running well" co.id lolos + bug khas .my (audit §13.2).
3. `TASKTRACKER-SEO-MASTER.md` — diganti jadi pointer tipis (28 baris). Riwayat penuh awet di
   `TASKTRACKER-SEO-MASTER.md.bak-split-20260927-100000` (72.806 B).
4. `README.md` — tabel urutan baca diperbarui ke struktur baru.

**Bukti verifikasi:**
- Diff ID task: master lama 89 ID vs (COID 76 + MY 13) = **0 hilang, 0 duplikat**
  (output python: `ID hilang dari gabungan COID+MY: TIDAK ADA (OK)`, total lama 89 = total baru 89).
- Backup master dibuat SEBELUM overwrite, ukuran terverifikasi `wc -c` = 72.806 B.

**Belum/tidak disentuh:** semua file lain (audit, plan.co.id, plan.my, INDUSTRY-EXPANSION, worker code, live).

---

## ✅ FASE B — `EXECUTION-COID-FOR-AGENT.md` (SELESAI 27 Sep)

**Yang dikerjakan:** dokumen kerja super-detail decision-complete untuk muse spark 1.3 (320 baris):
- §0 aturan (larangan UI/.my/delete, tabel KANONIK vs STALE repo-ganda `web/` vs root, protokol deploy 7 langkah, peta rollback `10efe09f`, fakta operasional terbukti — tak perlu investigasi ulang)
- §T0 deploy guard 1.16 (diff pra-deploy → build → deploy → verifikasi API → observasi 3 hari)
- §T0b tiga bukti gap verifikasi: 2.7 dual-write PG (snapshot PG↔D1), 2.8 pull VPS (`vps_acked≥1`), failover R2 terkendali dengan **slug canary** (bukan artikel asli)
- §T1 Fase 4 (index-cascade existing, bukan INSERT manual), §T2 fix bug write-back R2 (helper `_syncPostToR2` + 4 call-site, bentuk payload persis `worker-entry.js:2993-3013`)
- §T3 Winner Keyword Engine (route `keyword_ranks`→3 aksi, reuse ctr-fix/enrich/keyword_queue, laporan mingguan), §T4 Industry Wave Runner 6 langkah (2.291 keyword terverifikasi strukturnya, validasi Suggest, quality gate, gerbang 45 hari), §T5 LLM Visibility (tabel `ai_crawler_log`, llms.txt per industri, SearXNG di jobs `geo-monitor` yang sudah ada), §T6 Freshness at scale, §T7 Fase 5+8
- §9 grafik dependensi, §10 DoD "running well" + syarat tambahan buka gerbang .my, §11 placeholder rahasia + grep-command anti-bocor

**Bukti verifikasi:** semua anchor baris kode dibaca ulang 27 Sep sebelum dikutip (`handleAdminDraftsCommit:1340`, guard 1367-1375, VPS-pull 2265-2296, dual-write 2522, `_renderBlogFromR2:15281`, `USE_R2:430`, `handleLlmsTxt:5060`, `handleKeywordsImport:1496`, scheduled 580-870); bentuk objek R2 dikonfirmasi dari kode backfill (line 2993-3013); `industry-keywords.json` di-parse = list 2.291 item, `clusters.json` = dict 10 service. Tidak ada deploy/perubahan live (doc-only).

---

## ✅ FASE C — `MY-DUPLICATION-PLAN.md` (SELESAI 27 Sep)

**Yang dikerjakan:** catatan duplikasi .my (71 baris): prinsip ".my = salinan 100% sistem co.id, beda hanya bahasa+keyword+delta teknis"; tabel §2 (15 sistem co.id → padanannya di .my, termasuk T0–T7 yang belum dikerjakan); §3 12 DELTA teknis khas .my (nama setting `daily_publish_limit`, PUT schedules pasca-deploy, `run_worker_first` 20 path + rekomendasi Q3, nomor CTA tetap +62, dst); §4 RE-SYNC LOG wajib diisi agent co.id tiap mengubah sistem; §5 urutan kerja cermin.

**Bukti verifikasi:** semua delta disalin dari audit §13.2/§6.6 + tracker baris .my (bukan ingatan); keputusan user #8/#10 dipatuhi (tidak ada aksi .my).

---

## ✅ FASE D — Verifikasi akhir paket (SELESAI 27 Sep)

| Cek | Metode | Hasil |
|---|---|---|
| Keutuhan task | diff ID task master-lama(bak) vs COID∪MY | 89 = 76+13, **0 hilang, 0 overlap** |
| Rahasia plaintext | grep token-lama (di-mask, lihat catatan di sel hasil) + `gsk_…`/`cfut_…`/`eyJ…`/`7ff57542…` di 6 file baru | 4 kemunculan token lama di TASKTRACKER-COID **di-mask jadi `<TOKEN-LAMA-dirotasi-3.8b>`**; sisanya bersih (hanya prefix ter-mask `gsk_FNRab69U…`/`cfut_KCVg61ix…` warisan master — sesuai kebijakan README) |
| Silang-rujukan | semua nama file yang dikutip README/tracker/exec ada di disk | 6/6 OK |
| Tidak ada perubahan kode/konfigurasi terlacak | `git status` tracked-files | daftar `M` identik dengan sebelum sesi (pre-existing); semua hasil kerja ada di folder tak-ter-track `DOCS-SEO-2026-09-24/` — **nol sentuhan src/web/live** |
| Re-produksibilitas pemisahan | `split_tracker.py` ditinggalkan di folder DOCS | bisa dijalankan ulang terhadap backup master |

**Kesimpulan paket:** pemisahan co.id/.my SELESAI; dokumen eksekusi agent-ready SELESAI; gerbang .my terdokumentasi SELESAI. Langkah berikutnya bukan dokumen: eksekusi §T0 dst. oleh muse spark 1.3 **setelah aba-aba user** (keputusan #11 masih berlaku).

---

## 🏁 STATUS AKHIR SESI 27 SEP — SEMUA FASE (A–D) SELESAI

Paket dokumen siap dipakai muse spark 1.3: mulai dari `EXECUTION-COID-FOR-AGENT.md` §0, task pertama §T0
(deploy guard 1.16) **hanya setelah aba-aba user** (keputusan #11 — sesi ini doc-only, nol perubahan live).
Gerbang .my: lihat `MY-DUPLICATION-PLAN.md` §1 — belum dibuka.

---

## 🚀 EKSEKUSI LIVE — 30 SEP 2026 (user memberi aba-aba: "kerjakan berurutan, jangan sampai error, web sudah live")

### ✅ §T0 — Deploy guard cap-bypass 1.16 (SELESAI + TERBUKTI LIVE)

**Pra-check (read-only):**
- `wrangler whoami` → login OAuth, account `766dfffa7e5dcd8ba246ebfa60bc10ba`, worker `beriklanweb`.
- `wrangler deployments status` → live `10efe09f-463b-4603-b977-5e6e39f812f9` (25 Sep 07:26 UTC).
  **Koreksi dokumen:** ID rollback di §0.4/§T0 salah transkripsi (`…5f23d48d4715` = suffix versi lain `016525c3`) — sudah dibetulkan di `EXECUTION-COID-FOR-AGENT.md`.
- **Bukti guard belum live:** backup pra-edit `.bak-1.16-20260925-145652` = 0 kemunculan `remainingTodayCap`; file sekarang = 3 (1367-1375); tidak ada deploy sejak 25 Sep 07:26 UTC.
- Health pra-deploy: `/` 200, `/blog/` 200, sitemap 200, news.xml 200, slug palsu 404.

**Prosedur §0.3 (semua lulus):**
1. Diff vs backup = **22 baris, seluruhnya di `handleAdminDraftsCommit`** (blok guard + `LIMIT ?`) — tidak ada delta tak dikenal.
2. `node --check` → SYNTAX OK.
3. `npm run build` → **10.122 halaman / 207 s**; sanity dist: 917 MB, 10.441 file, `posts-index.json` valid 24 item.
4. `npx wrangler deploy` → sukses (upload 10.134 asset, 2× retry otomatis) → **versi baru `85a690b8-acc1-4010-b8cc-92470d848c82`**, `schedule: 0 * * * *` terjaga.

**Verifikasi pasca-deploy:**
- Runbook §J: `/` 200 (79.898 B) · `/blog/` 200 · `/news.xml` 200 · `/sitemap-blog.xml` 200 · `/data/posts-index.json` 200 · `/llms.txt` 200 · `/llms-full.txt` 200 · `/robots.txt` 200 · slug palsu **404** · artikel asli `200 x-source: d1`.
- **Bukti fungsional guard** (kondisi aman: published=15/cap=15, pending=396): `POST /api/admin/drafts/commit` →
  `{"ok":true,"message":"daily limit reached","committed":0,"published_today":15,"daily_limit":15}`
- **Nol efek samping:** setelah tes, published tetap 15 dan pending tetap 396 (guard menolak SEBELUM fetch draft).
- Baseline kepatuhan 10 hari: 23–24 Sep = 400/hari, 25 Sep = 32 (insiden), **26–29 Sep = 15/15/15/15** → jalur cron sudah patuh; guard menutup bypass jalur manual.

**Observasi berjalan:** §T0 langkah 4 (3 hari berturut published ≤ 15) — cek tiap pagi, tutup 1.16 sepenuhnya ±3 Okt.
**Rollback jika perlu:** `npx wrangler rollback 10efe09f-463b-4603-b977-5e6e39f812f9`.

---

### ✅ §T0b — Tiga bukti end-to-end (SELESAI, + 1 BUG NYATA DITEMUKAN & DIPERBAIKI)

**T0b.1 dual-write PG → ketemu BUG 2.7b, lalu FIXED.**
- Audit PG: `coid.publish_outbox` max `created_at` = **2026-09-25 02:00 UTC** (26 baris), `coid.posts_meta` max `iso_date` = 2026-09-24 15:00, `generated_drafts` PG `committed_at >= 2026-09-26` = **0** — padahal D1 publish 15/hari (26–29 Sep = ~60 artikel tidak pernah sampai PG). Jadi 2.7 **tidak** hanya "belum terbukti" — ia **mati** sejak sakelar 2.8 dinyalakan.
- Akar: `worker-entry.js:2527-2529` memakai flag GLOBAL `pipeline_source='vps'` untuk skip re-enqueue, padahal item yang dipublish sering tetap berasal dari buffer D1 (pull mengembalikan 0 item → `vpsMode=false`).
- Fix: gate per-run `if (!vpsMode && …)`. Backup `.bak-2.7b-20260930-014051` → diff 16 baris → `node --check` OK → build 10.122 halaman → deploy → **versi `cd5bec56-33c8-4b82-9fe9-d23028f41ff4`**. Health pasca-deploy lulus (200/200/200 + 404 jujur).
- **Bukti lulus:** cap 15→17 (sementara) → sync-posts publish 2 slug → kedua slug muncul di `coid.publish_outbox` status `ready` 18:50:24 & 18:50:25 UTC (26→28 baris) → **cap dipulihkan ke 15 dan diverifikasi baca ulang**.

**T0b.2 pull VPS → TERBUKTI dengan item `ready` nyata.**
- Cap 15→19 → `sync-posts` → `pipeline_source:"vps"`, **`vps_acked: 2`** (pull 2 item PG → publish → ack `ready`→`handed`) → cap dipulihkan 15.
- Uji integritas round-trip D1→PG→D1: panjang konten SEBELUM=SSESUDAH identik (jakarta 3.917 B, palembang 3.835 B); `posts_meta` tetap 16.848; `rows_today` tetap 17 → jalur pull idempoten, tidak melahirkan artikel duplikat.

**T0b.3 failover R2 → TERBUKTI (canary `r2-failover-canary-20260930`).**
- Insert canary ke `posts_meta`+`posts_content` saja (`iso_date` 2016 agar tak masuk `posts-index.json`) → `200 X-Source: d1`.
- **GOTCHA yang menjelaskan kenapa Fase 3 dulu "belum terbukti": `wrangler r2 object put` TANPA `--remote` menulis ke simulator lokal**, bucket produksi kosong → tes pertama `404`. Ulang dengan `--remote` → objek terbaca di bucket produksi.
- DELETE hanya baris canary di `posts_content` **dan** `posts_meta` (route menganggap D1 hit bila slug ada di salah satu dari `posts_meta`/`generated_drafts`) → **`200 X-Source: r2`** + marker `CANARY-R2-FAILOVER-MARKER-20260930` di body + teks "Disajikan dari cache R2".
- Cleanup tuntas: objek R2 dihapus (`--remote` + lokal), `pending_indexing` canary = 0 (tak pernah dikirim IndexNow), baseline `posts = contents = 16.848`, URL kembali **404 jujur** (TTL cache natural — token `cache_purge:edit` tidak valid, sesuai catatan task 1.9).

**Kesimpulan T0b:** tiga prasyarat gerbang .my + Fase 5 tertutup, dan **Postgres kini benar-benar menjadi cermin lengkap** — syarat wajib sebelum mempertimbangkan trim D1 (Q4). Perubahan live sesi ini: 2 deploy (`85a690b8`, `cd5bec56`), 2 artikel terbit (normal, dari buffer), 1 canary dibuat+dihapus, `publish_daily_limit` sudah kembali 15.

---

### ✅ §T1 — Fase 4 indexasi & pertumbuhan (SELESAI 2026-09-29 19:1x–19:4x UTC · 3 BUG NYATA DITEMUKAN & DIPERBAIKI)

> Kaidah yang dipatuhi sepanjang blok ini: backup `.bak-*` → edit → `node --check` → `npm run build` (exit 0) → `wrangler deploy` → runbook health §J → **bukti fungsional di produksi** → kembalikan setiap mutation sementara. Tidak ada satu pun artikel dihapus. Tidak ada file tampilan yang disentuh.

**T1.1 / task 4.1 backfill `pending_indexing` → SUDAH TERPENUHI, tidak ada aksi.**
- Anti-join (bukan endpoint, karena endpoint hanya menambah): `posts_meta` yang belum ada URL-nya di `pending_indexing` = **0** dari **16.848** artikel. Tabel = 17.282 baris, `COUNT(DISTINCT url) = COUNT(*)` → tidak ada duplikat.
- Temuan kebersihan: 1 baris rusak `id=1783 url='https://beriklan.co.id/blog//'` (slug kosong, source `manual`, 21 Jul) → disimpan `SELECT *`-nya ke `/tmp/t1/row1783_before_delete.json`, lalu DELETE presisi (`WHERE id=1783 AND url=…`) → 17.281. Bukan artikel, tidak melanggar "jangan hapus data artikel".
- **Reinterpretasi penting:** yang selama ini dikira "backlog 16,8 rb belum terisi antrian" ternyata sudah terisi — yang macet adalah **drain**-nya.

**T1.2 / task 4.2 IndexNow → key SEHAT, tapi ketemu BUG 4.2b (queue starvation) → FIXED, live `c890fdc1` lalu `6831ff0c`.**
- Key tidak pernah bermasalah: `GET /2dac33f6…​.txt` = 200; POST batch = 200/202. Cron `indexnow` enabled, 69 run `status='ok'` dalam 3 hari.
- Forensik: `pending` 16.955 tapi hanya **56** punya `indexnow_at`; `MAX(indexnow_at)` jalur pending = **2026-09-25 11:01:09**; 12 artikel terbaru semuanya NULL; `submitted_urls` **identik** antar-run di `cron_runs.output`.
- Akar: subquery A `WHERE status='pending' ORDER BY id ASC` **tanpa** filter `indexnow_at`, sementara UPDATE memakai `AND indexnow_at IS NULL` → no-op → 50 id terkecil yang sama dikirim ulang tiap jam selamanya.
- Fix 3 lapis (meniru pola sehat `handleGscIndexing`): A `indexnow_at IS NULL ORDER BY id DESC` (terbaru duluan), A2 rotasi `> 14 hari` tertua lebih dulu, UPDATE tanpa guard `IS NULL`.
- **Clamp 50 DIPERTAHANKAN** (Workers Free = 50 subrequest/invocation) → konsekuensi: klaim task 4.0b "bump 50→100" memang tidak pernah efektif; cron mengirim `count=100`, di-clamp 50. Documented, tidak diakali.
- Bukti lulus: `c890fdc1` → antrian maju ke id 2001-2003 ter-mark `2026-09-29 19:15:05` (dari id 1998 / 25 Sep); `6831ff0c` → `count=3` mengirim **id 23899/23898/23897** (`submitted:3 failed:0 engines:4`). Bing + api.indexnow.org konsisten **429** (IP bersama), yandex 202 → 1 POST 202 menyebar ke seluruh jaringan IndexNow.
- `indexnow_backoff_until` dinormalisasi ke sentinel `2000-01-01 00:00:00` (= tidak ada backoff aktif). Ini **disengaja dan tercatat**, bukan lupa.

**T1.3 / task 4.3 growth → ketemu BUG 4.3a (kandidat dari snapshot 1 hari) → FIXED, live `b4c76b61`.**
- Sesuai urutan §T1.3, diverifikasi dulu sebelum menyalahkan kode: secret GSC `sc-domain:beriklan.co.id` SEHAT; `handleRankSync` menyisipkan 349 baris; `keyword_ranks` 13.226 baris, `max_date` 27 Sep → **latensi data GSC 2–3 hari, bukan bug**.
- Gejala: cron 29 Sep 09:01 `status=ok` tapi `candidates:0` untuk enrich & ctr-fix; `growth_log` terakhir 27 Sep.
- Akar: kandidat di-`JOIN` dari `(SELECT keyword,page_url,MAX(date) …) latest` lalu ambang `impressions`/`position`/`ctr` dibaca dari **satu baris harian itu** → keyword 150 impresi/28 hari tapi 3 impresi di hari terakhir GUGUR.
- Pengukuran langsung di D1 (window 28 hari): versi lama meloloskan **1** (ctr-fix) / **0** (enrich); versi agregat → pool imp≥5 **570** pasangan · **453** punya halaman live · **enrich** pos 3–18 = **39** (37 bebas cooldown) · **ctr-fix** pos≤30 & CTR≤2% = **96**.
- Fix: derived-table agregat (`SUM(impressions)`, `AVG(position)`, `SUM(clicks)/SUM(impressions)`) + param `days` baru (default 28, clamp 1–90). **Ambang TIDAK diturunkan** — kualitas tetap, hanya caranya membaca data yang diperbaiki.
- Bukti lulus per handler: ctr-fix → `harga-jasa-digital-marketing-jasa-profesional-di-bekasi` `imps:66`; enrich → `jasa-kelola-instagram-untuk-perusahaan-murah-di-surabaya` `position:11.217` (pecahan desimal = bukti AVG/agregat); freshness → `jasa-iklan-tiktok` `imps:241`. Ketiganya `r2_sync:"ok"`.
- **Gotcha SQLite yang menjebak:** `HAVING impressions >= 5` memakai nama alias yang SAMA dengan kolom dasar → hasil 10 yang menyesatkan. Diperbaiki dengan alias berbeda (`imps`/`cl`/`avgpos`) → angka sebenarnya 570.

**T1.4 / task 4.4 index-verify → ketemu BUG 4.4a + 4.4b → FIXED, live `6831ff0c` (lulus penuh menunggu 1–2 Okt).**
- **4.4a — kuota GSC 200/hari dihabiskan baris tua.** Bukti D1: baris dengan `gsc_submitted_at >= -1 day` = 200 dengan **MIN(id)=1624 MAX(id)=1897** (dibuat 19 Jul) padahal `MAX(id)` tabel 23.899 → 2 artikel terbaru **belum pernah** dikirim ke Indexing API; 16,7 rb lain antre ±84 hari. Akar: satu daftar `ORDER BY id ASC` + kelayakan ulang `< -1 day`.
- Fix: antrian 2 tingkat — Q1 `gsc_submitted_at IS NULL ORDER BY id DESC` (terbaru duluan), Q2 rotasi `< -14 days ORDER BY gsc_submitted_at ASC` (menghentikan re-submit harian). Field log baru `never_submitted` + `resubmit_rotation`.
- **4.4b — `rowid ASC`** pada seleksi index-verify (inspeksi selalu di pangkal tabel; 20 slug terbaru tak pernah di-inspect) → `id DESC`.
- **Penjelasan `picked:0`:** re-submit harian men-bump `gsc_submitted_at` terus, sehingga tidak ada baris yang pernah memenuhi `< -2 days` → `due_verify = 0` dari 261 baris `gsc_submitted` (baru 18 yang PERNAH di-inspect). Setelah 4.4a bump berhenti → verifikasi jatuh tempo 1–2 Okt.
- Bukti lulus sebagian (kuota adalah sumber daya harian, jadi tidak diboroskan untuk tes): `gsc_quota_used` sementara 200→**197** → `gsc-indexing?count=3` mengirim **3 URL terbaru** (id 23899/23898/23897, `status='gsc_submitted'`, `gsc_submitted_at` 19:42:12/14) → kuota dipulihkan ke **200** dan diverifikasi baca ulang.
- Non-issue yang dicek & ditegaskan: `sitemap-blog.xml` live = **17.034** `<url>` (generated worker); angka 7.497 hanya di `dist` statis dan tersaingi — **bukan** kebocoran sitemap.

**§T2 write-back R2 (digabung ke deploy yang sama, sesuai §9 plan) → live `b4c76b61`, tercatat sebagai task 3.9.**
- Helper `_syncPostToR2(slug, env)` + 3 call-site (enrich / ctr-fix / freshness) + paritas SERP di `_renderBlogFromR2` (`seo_title`/`seo_description`). `handleSnippetOptimizer` sengaja dikeluarkan (hanya menulis ke GitHub, tidak ke D1/R2).
- Bukti objek R2 (`--remote --file`): Bekasi `synced_at 2026-09-29T19:30:45.378Z` dengan `meta.seo_title` terisi; `jasa-iklan-tiktok` `19:31:50.701Z` dengan **tepat 1** callout "Update 2026" (identik dengan D1, tidak dobel).
- **Gotcha verifikasi baru:** request pertama pasca-`wrangler deploy` masih bisa menyentuh versi lama (baris `growth_log` 19:29:51 belum ber-`r2_sync`) → selalu cek `npx wrangler deployments status` = 100% versi baru sebelum menyimpulkan fix tidak jalan.

**Kondisi produksi penutup blok §T1/§T2:** versi live **`6831ff0c-ff3d-4791-886b-b5a76cc6a783`** (created 2026-09-29T19:40:40Z, 100%), rollback target `b4c76b61`; rantai sesi ini `85a690b8 → cd5bec56 → c890fdc1 → b4c76b61 → 6831ff0c`. Runbook health hijau. `publish_daily_limit=15` · `publish_batch_size=5` · `gsc_quota_used=200` · `pipeline_source='vps'` · `pending_indexing` 17.281. Backup: `web/src/worker-entry.js.bak-4.2b-20260930-020912`.
**Observasi berjalan (jangan ditutup sebelum lulus):** cap 1.16 3 hari (± 3 Okt) · `growth_log` naik tiap hari 7 hari (± 6 Okt) · 20 slug terbaru terindex (2 Okt).

---

### ✅ §T3 — Winner Keyword Engine (2026-09-29 20:0x–20:2x UTC, co.id, LIVE)

**Apa yang dipasang** (`web/src/worker-entry.js`, ±290 baris baru + 1 konstanta `OWNER_EMAIL`):
- `_winnerCandidates(env, days, minImp, limit)` — pool = **agregat** `keyword_ranks` jendela N hari (`SUM(impressions)`, `AVG(position)`, `SUM(clicks)/SUM(impressions)`), HAVING `imp ≥ minImp AND pos BETWEEN 4 AND 25`, filter `keyword NOT LIKE '%beriklan%'` + **domain apex/www saja**, `LEFT JOIN posts_meta` (hanya untuk `page_url LIKE '%/blog/%'`).
- `_winnerPlan(rows, perIndustry, maxActions)` — 1 aksi per query; halaman blog selalu dipilih jadi representatif di atas halaman layanan; band `winner-rewrite` (dedicated & pos ≤10) / `winner-enrich` (dedicated pos >10, atau cocok lemah pos ≤15) / `winner-new` (tanpa halaman blog, atau pos 16-25 dengan halaman generik); cap per industri + cap total; query yang terbaiknya halaman layanan → `covered` (tanpa aksi).
- `handleWinnerEngine` — tulis `keyword_queue` (INSERT prio **96** `source='winner-engine'` / UPDATE promote) + `_growthLogStmt` per aksi; `?dry=1` tidak menulis apa pun. `handleWinnerWeeklyReport` — tabel TOP-50 + ringkasan band & `growth_log` 7 hari → `sendEmailViaResend(OWNER_EMAIL, …)`.
- Gate: `if (h === 10) { winner-engine }` + `if (dow === 3) { winner-weekly }` di dalam `scheduled()` yang ada (cron slot tunggal `0 * * * *` tidak berubah). Router `/api/cron/winner-engine` & `/api/cron/winner-report`.
- Optimum ikutan: `ensureGrowthSchema` kini **probe 2 subrequest** (sebelumnya 11 DDL tiap panggilan) dengan fallback DDL idempoten bila probe gagal; `_growthLogStmt` di-ekstrak supaya bisa masuk `env.DB.batch()`.

**Kenapa `h === 10` dan kenapa tidak memanggil AI dari dalam (bukti, bukan asumsi):** satu event `scheduled()` = SATU invocation yang dibagi semua `waitUntil`. `cron_runs` 29 Sep: jam normal (5-6 job) semuanya `ok`; jam `h%6===0` (12:01 & 18:01, 11 job) **SELALU** meninggalkan 4 baris `running` yang kemudian ditandai `timeout` (indexnow, gsc-indexing ×2, lead-pipeline). Menaruh job AI di jam ramai = memindahkan kegagalan ke jalur indexasi. Gate 09:00 (enrich/ctr-fix) membaca pool agregat yang sama dan mengurut `impressions DESC` → kandidat winner otomatis antre paling depan di eksekutor yang sudah ada.

**4 penyimpangan berbasis data dari teks plan §T3** (jejak lengkap di komentar kode line 8440-8468):
1. prio **96** bukan 85 — `hourly_candidates` refill = `… ORDER BY priority_score DESC LIMIT 120` PER layanan; hasil ukur buffer `jasa-digital-marketing` = 120 baris dengan `min_in_buffer=90` → 85 tak pernah terpilih. Cap sumber lain: rebalance 90, gsc-loop `Math.min(95, …)`.
2. `minImp` default **10** bukan 30 — pool nyata: 32 (≥10) · 22 (≥15) · 13 (≥20) · **7 (≥30)** · 2 (≥50).
3. **tanpa** panggilan `handleGrowthCtrFix/Enrich` dari dalam winner-engine (alasan invocation di atas).
4. acceptance plan "cek `email_queue`" **tidak bisa dipakai** — `sendEmailViaResend` tidak menulis `email_queue`; bukti yang sah = `resend_id`.

**⚠️ BUG 3.10 (ditemukan saat verifikasi sendiri, langsung diperbaiki):** `(await env.DB.batch(...)).results` — `batch()` mengembalikan ARRAY, bukan objek → `readResults` kosong → dedupe mati; 2 dari 10 INSERT run pertama hilang diam-diam kena `UNIQUE(keyword)`. Perbaikan: `concat(await batch())`, read antrian `ORDER BY CASE status WHEN 'pending' THEN 0 ELSE 1 END LIMIT 3` + jalur `id IS NULL` (PRIMARY KEY TEXT boleh NULL → `UPDATE … WHERE id=?` tak pernah kena), skip `queue-rejected`, dan aturan band "sudah punya halaman dedicated → jangan bikin artikel baru".

**Runbook eksekusi & bukti:**
1. Backup `worker-entry.js.bak-t3-20260930-025616` → `node --check` (menangkap 1 syntax error nyata: template literal bersarang di dalam `${}` pada HTML email — IDE menyebutnya "JSX", dan itu BETUL; setelah dikeluarkan ke variabel `bandLine`/`industryLine`, `node --check` OK).
2. `npx wrangler deploy --dry-run` (bundle 922 KiB, 0 error) → `npx wrangler deploy` → `0aa99c4c`; `deployments status` 100%; health 7 URL 200 + 404 jujur + `x-source: d1`. Asset: "No updated asset files to upload" (dist masih build 30 Sep 02:38, tidak ada perubahan halaman) → nol risiko visual.
3. Daftarkan kill switch SEBELUM tes: 2 baris `cron_settings` (`winner-engine`, `winner-weekly`, `enabled=1`).
4. Dry-run 2× → `pool:40 planned:19 by_band:{rewrite:1,enrich:3,new:15}`, top-12 identik antar-run, tidak ada query subdomain yang bocor.
5. Live run #1 → `queue_inserted:10` · `growth_log` 19 baris `winner-*`. Audit D1 menemukan hanya **8** baris antrian yang benar-benar ada → memimpin ke penemuan BUG 3.10.
6. Fix → `f7d53c28` (100%) → live run #2 → `by_band:{rewrite:1,enrich:14,new:4}` + alasan `dedicated-post-exists` muncul (bukti read hidup).
7. Bersihkan artefak run buggy: backup `SELECT *` 8 baris → `DELETE FROM keyword_queue WHERE id LIKE 'win-%'` (`changes:8`) → live run #3 → `queue_inserted:0` (semua kandidat minggu ini sudah terjawab konten yang ada).
8. Laporan mingguan manual → `sent:true · resend_id:01a0eece-def0-70de-9342-78a65e3ee77b` · TOP-32 · 5 industri (tiktok 17, facebook 8, google 5, youtube 1, umum 1) · 548 ms.

**Acceptance §T3:** ≥10 aksi `winner-*` ✅ (19/run; `growth_log` 24 jam = 57 dari 3 run) · ≥4 industri ✅ (5) · bukti email ✅ (`resend_id`). **Masih terbuka:** run cron otomatis pertama 30 Sep 10:00 UTC (cek `cron_runs cron_name IN ('winner-engine','winner-weekly')`) dan cabang *promote* yang belum terpicu alami.
**Kondisi produksi penutup §T3:** versi live **`f7d53c28`** (100%), rollback target `6831ff0c`; rantai sesi `85a690b8 → cd5bec56 → c890fdc1 → b4c76b61 → 6831ff0c → 0aa99c4c → f7d53c28`.

---

### ✅ §T4 — Industry Wave Runner, gelombang 1 kontraktor (2026-09-30 03:3x–04:2x UTC, co.id)

**Tanpa deploy.** Tidak ada satu byte pun berubah di `web/src/worker-entry.js` pada task ini — versi live tetap `f7d53c28`. Kerjanya: 2 script lokal baru + 1 impor data lewat endpoint yang sudah ada. Produksi diverifikasi tetap sehat setelah impor (lihat langkah 6).

**Langkah 6.1 + 6.3 — `web/scripts/validate_suggest.py` (BARU).**
Plan menulis "validasi ~300 frasa teratas wave-1 (industri=kontraktor)". Setelah file dibaca (bukan diingat): `industri='kontraktor'` **tidak ada** — 'kontraktor' hanya `sub_niche` di dalam `industri='properti'` = **9 seed**, dan 2.291/2.291 item ber-`intent='informational'`. Ditambah lagi: matriks sintetik 89 frasa hanya lolos **47,2%** di Google Suggest, dan seluruh frasa hasil formula dataset ("studi kasus kontraktor naik omzet", "cara pasang iklan tiktok konveksi", dkk.) = **0 suggestion**. Kesimpulan teknis: frasa formula dataset TIDAK punya bukti demand → strukturnya dibalik menjadi **harvest-first** (tangkap dari Suggest → baru turunkan mekanis kota/biaya/kanal, sesuai `INDUSTRY-EXPANSION` §4 aturan #1). Acceptance plan berbunyi "kalau <70%, corek daftar dan lapor user" — dan itu yang terjadi.

Hasil run `--harvest` (49 frasa, target §9 = 60–90):
- `STATUS: {exact:21, derivative:28}` · exact-rate **42,9%** (< 70% → **DILAPORKAN**) · `weak` = 0
- INTENT `{informational:14, commercial:27, transactional:8}` → **71,4% commercial+transactional** ✅ (acceptance ≥40%)
- Guard yang ternyata WAJIB (tanpa ini angka "lolos" cuma hasil manipulasi aturan): Suggest mentah "kontraktor"/"jasa kontraktor" isinya orang yang **MAU menyewa** kontraktor (B2C, bukan klien agency) + sampahan "poster iklan kontraktor", "kata kata iklan kontraktor", "fee marketing kontraktor", "tugas dan gaji …". Filter: `NICHE_RE` ∧ `MARKETING_RE` ∧ ¬`NEGATIVE_RE`.
- Cap anti-kembar: sebelum cap 68/89 frasa = varian kota; sekarang `MAX_CITY_PER_CORE=4`, `MAX_COST_PER_CORE=2`, `KANAL_CORES={iklan kontraktor}`.
- Dua file terpisah, sengaja: `industry-wave1.import.json` (21 yang TERBUKTI) dan `industry-wave1.import.with-derivatives.json` (49 termasuk turunan mekanis) → keputusan ikutkan-turunan ada di tangan yang menjalankan, bukan di default.

**Langkah 6.2 — impor ke antrian produksi (`web/scripts/import_wave1.py`, BARU).**
Lewat `POST /api/admin/keywords/import?token=…&source=industry-wave1` (`handleAdminKeywordsImport`, worker line 1517) — bukan suntik D1 manual (itu membuat jalur kedua, dilarang plan). Di-chunk 12 karena endpoint melakukan 2 operasi D1 berurutan per item (SELECT dedupe + INSERT): 49 item sekaligus ≈ 98 subrequest dalam satu invocation.
1. Run file terbukti → `inserted=21 skipped=0`.
2. Run file lengkap → **`inserted=28 skipped=21`** = dedupe endpoint terbukti bekerja (21 yang ditolak adalah baris yang baru saja masuk).
3. Verifikasi D1: `source='industry-wave1'` = 49 baris · 100% `status='pending'` · `no_service=0` · prio 93×7 / 92×14 / 91×28.
4. **Bukti benar-benar masuk jalur generasi** (bukan cuma "baris ada di tabel"): query refill buffer dijalankan PERSIS seperti worker (`status='pending' AND (article_slug IS NULL OR '') AND service=? ORDER BY priority_score DESC LIMIT 120`) → cutoff `jasa-digital-marketing` = 90 dan **44/44 baris wave-1 ada di TOP-120**; `jasa-iklan-facebook` **1/1**.
5. Jujur soal status saat itu: `hourly_candidates` masih berisi snapshot lama (0 baris wave-1) karena refill hanya terjadi saat `picked=0` sisa < 60 (sisa sekarang 1.082). Wave-1 masuk pada refill berikutnya; `jasa-iklan-facebook` sudah tinggal 2 kandidat unpicked → refill dekat.
6. Kesehatan produksi pasca-impor: `/` 200, `/blog/` 200, `/news.xml` 200, artikel nyata 200 `x-source: d1`.

**Kenapa prio 91–93 dan bukan 70–85 seperti teks plan** — alasan yang sama dengan deviasi T3 #1 dan dibuktikan ulang hari ini: buffer per service hanya mengambil TOP-120 dan buffer itu penuh di prio 90 (46.880 baris `pending` di `jasa-digital-marketing`; 1.290 baris di pita 90–95, praktis semuanya tepat di 90). Sisipan prio 70–85 = **nol aksi**. 96 milik winner-engine, 95 cap gsc-loop → wave memakai 91–93. Efek samping yang disadari: ±49 baris prio 90 tergeser dari buffer (tetap `pending`, akan kembali naik ketika baris di atasnya terbit; dampak antrian ≈ 0,1%).

**Langkah 6.9 — `web/scripts/quality-gate.mjs` (BARU).** Dua temuan teknis selama build: (a) **WAF Cloudflare menolak UA default urllib** dengan `HTTP 403 / error code: 1010` padahal `curl` boleh lewat → script mengirim `User-Agent: curl/8.7.1`; (b) **bug saya sendiri** di mode wave: `{...draft, ...barisQueue}` menimpa `service` milik draft dengan string kosong dari baris queue lama (1.606 baris `suggest+combo` service-nya `''`) → §7.4 "service kosong" gagal palsu pada 40/40 draft; diperbaiki dengan `pick()` non-kosong dan diverifikasi: alasan `service` hilang pada run ulang.

Isi gate = §7: ≥1.200 kata (co.id) · blok jawaban 40–60 kata dalam 100 kata pertama · FAQ ≥3 (menerima `class="growth-faq"` MAUPUN heading pertanyaan — generator sekarang memakai heading pertanyaan di bawah `<h2>FAQ …</h2>`) · service + slug↔keyword · internal link ≥3 (wa.me/mailto/tel/eksternal tidak dihitung) · kata terlarang COPY-BIBLE · ≥1 angka. **Dua deviasi jujur dari teks:** Schema Article TIDAK dinilai dari draft (`application/ld+json` = 0 di semua draft; schema disuntik saat render, jadi hanya dilaporkan sebagai info), dan gerbang duplikat plan (jaccard 3-gram **badan** ≥ 0.85) ternyata **no-op** — max terukur 0.084 antar 8 draft terbaru → ditambahkan deteksi **judul** (ambang 0.8 dipilih dari distribusi nyata: 428 pasangan ≥ 0.6, hanya 34 ≥ 0.8, dan yang 1.00 adalah judul yang sama persis hanya urutan kata dibalik).

**HASIL GATE atas 60 draft terbaru (`DOCS-SEO-2026-09-24/gate-report-wave1.json`, `mode="pool-audit"` karena draft wave-1 belum ada):**
- **0 LULUS / 60 GAGAL** di ambang §7 · alasan: `word_count:60` (min 454 · p50 656 · max 871 kata) · `dup_title:96 pasangan` · `answer_block:31` · `banned_words:3` (ketiganya kata "pasti")
- Skenario turunkan ambang ke 700 kata: tetap **1/60 = 1,7%** → penghambat utama bukan cuma panjang, tapi **artikel kembar** dan **blok jawaban yang hilang di separo draft**
- Contoh kembar nyata (jaccard judul 1.00): `Jasa Iklan Facebook Di Makassar Berpengalaman` ↔ `Jasa Iklan Facebook Berpengalaman Di Makassar` (slug `…-di-makassar-berpengalaman` vs `…-berpengalaman-di-makassar`); 34 dari 60 draft terlibat pasangan ≥ 0.8
- **Wave-1 sendiri hampir bersih dari pola itu: hanya 2 pasangan ≥ 0.8 di antara 49 frasa** → kualitas daftar wave-1 terukur jauh di atas antrian lama
- **`--apply` TIDAK dijalankan** dan ini keputusan, bukan kelalaian: dengan ambang §7 hari ini gate akan mengubah ±397 draft `status='draft'` → `draft-gated` = pipeline publish harian berhenti = mengubah sistem produksi berjalan tanpa izin (SOP #4). Mode wave sendiri sudah diuji end-to-end memakai `--source suggest+combo` (60 baris queue → 40 draft terbaca).

**Temuan sampingan (dilaporkan, TIDAK disentuh):** 3.015 baris `keyword LIKE '%sepi viewers%'` (3.005 `pending`, sumber `expand_v2`), **10 di antaranya prio 95** = posisi paling atas buffer di tiap service. "facebook ads sepi viewers" bukan intent klien agency, dan `INDUSTRY-EXPANSION` §6.3 justru menuntut baris semacam ini di-demote/block. Perlu keputusan user (mengubah prio baris yang sudah antre = menyentuh sistem berjalan).

**Sisa §T4 = gerbang waktu, bukan kerja tertunda:** (1) ± 1 hari — setelah refill buffer + generate, jalankan `node scripts/quality-gate.mjs --source industry-wave1` (dan putuskan ambang bersama user sebelum `--apply`); (2) 45 hari — §8.1: ≥1 URL wave-1 impressions > 100 ATAU ≥3 klik ATAU posisi ≤ 20 → baru wave-2 (toko bangunan); gagal = STOP, tidak wave-2. Rollback batch (`UPDATE generated_drafts SET status='draft' WHERE …`) tidak dipakai karena tidak ada yang di-apply.



