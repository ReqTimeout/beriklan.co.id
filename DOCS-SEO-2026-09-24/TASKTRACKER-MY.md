# TASKTRACKER-MY.md — Tracker `beriklan.my` (SEMUA ⏸️ DEFERRED)

> **Dipisah dari:** `TASKTRACKER-SEO-MASTER.md` (27 Sep 2026)
> **ATURAN GERBANG (keputusan user #10):** tidak satu pun task di file ini boleh dikerjakan
> sebelum `beriklan.co.id` selesai dan terbukti *running well* (definisi 6 syarat di
> `TASKTRACKER-COID.md` §URUTAN EKSEKUSI butir 5). Dilarang mengerjakan `.my` "sekalian".
> **Prinsip duplikasi:** `.my` mengikuti SEMUA sistem co.id (Postgres SoT, R2 dual-read, winner engine,
> wave runner, LLM suite, freshness, monitoring). Yang berbeda hanya **bahasa (EN-MY), keyword pasar
> Malaysia, dan teknis khas .my** — lihat `MY-DUPLICATION-PLAN.md`.
> **Bug khas .my (audit §13.2):** `INDEXNOW_KEY` fallback ke key co.id · `normalizePhoneForWa` prefix harus `60` ·
> `sitemap-tag.xml` 0 URL · cron `.my` hanya via PUT API `[{"cron":"0 * * * *"}]` setelah tiap deploy ·
> `run_worker_first` 20 path eksplisit (tiap route baru wajib ditambah) · tanpa secret `GSC_SITE_URL` ·
> token hardcoded worker:696.
> **Status tracker lama:** baris `.my` murni di bawah + 35 task `both`/`co.id dulu` di `TASKTRACKER-COID.md`
> WAJIB direplikasi ke `.my` setelah gerbang terbuka: 0.3, 0.4, 0.6, 0.8, 1.1, 2.1, 2.2, 2.4, 2.5, 2.7, 2.8, 3.1, 3.2, 3.3, 3.4, 3.5, 3.7, 3.8a, 3.8b, 3.8c, 4.1, 4.2, 4.4, 5.0, 5.1, 5.2, 5.4, 5.5, 5.6, 6.1, 6.4, 6.7, 6.8, 7.4, 7.5, 8.2, 8.3, 8.4

## LEGENDA
⬜ BELUM · 🔄 IN PROGRESS · ✅ SELESAI (terverifikasi) · ⚠️ BLOCKED (butuh akses/keputusan user) ·
🔴 ROLLBACK · ⏸️ DEFERRED

## BASELINE (dikunci 24 Sep 2026 dari 0.3; detail di audit §15)
| KPI | co.id | .my |
|---|---|---|
| Clicks 28 hari (`sc-domain`) | 159 | 16 |
| Impressions 28 hari | 12.923 | 2.195 |
| URL blog live (sitemap) | **16.872** = posts_meta 16.686 + committed drafts 186 | 1.337 |
| `posts_meta` = `posts_content` | 16.686 | 1.337 |
| `generated_drafts` (committed + draft + pending) | 14.877 + 475 | 1.337 + 993 + 63.007 = **65.337** |
| URL blog di static `dist/` | 7.499 | build VPS invalid |
| URL hanya-D1 (rawan soft-404) | 9.373 (16.872 − 7.499) | 0 |
| D1 rows read/hari (top-6) | 5.360.539 | — |
| Publish/hari | 400 (23 Sep) | **40 tepat** (stabil 17–24 Sep) |
| `pending_indexing` (baris) | **17.026** (pending 16.754 · gsc_submitted 264 · indexed 8) — **bukan** 3,8 jt | 1.795 |
| Keyword pending | 377.832 *(ukur ulang sore: 377.757 — antrian hidup, wajar bergeser)* | 35.864 |
| `growth_log` ctr-fix | 0 | — |

---

## PEMETAAN FASE (tracker ini vs dokumen plan)

Tracker menyisipkan satu fase tambahan (**Fase 4 — Indexasi & Pertumbuhan**) sehingga penomorannya
bergeser dari `plan.*`. Gunakan tabel ini supaya tidak salah rujuk:

| Tracker (dokumen ini) | `plan.co.id.md` | `plan.my.md` | Isi |
|---|---|---|---|
| Fase 0 | §B Fase 0 | §B Fase 0 | Stabilisasi & pengaman |
| Fase 1 | §C Fase 1 | §C Fase 1 | Hentikan pendarahan |
| Fase 2 | §D Fase 2 | §D Fase 2 | Postgres = source of truth |
| Fase 3 | §E Fase 3 | §E Fase 3 | R2 + dual-read worker |
| **Fase 4** | *(dipecah dari §F/§G)* | *(dipecah dari §F/§G)* | **Indexasi & pertumbuhan** |
| Fase 5 | §F Fase 4 | §F Fase 4 | Rampingkan D1 (butuh izin user) |
| Fase 6 | §G Fase 5 | §G Fase 5 | Ekspansi industri |
| Fase 7 | §H Fase 6 | §H Fase 6 | GEO / LLM keyless |
| Fase 8 | §I Fase 7 | §I Fase 7 | Monitoring & serah terima |

Bila ada konflik instruksi: **tracker ini yang menang** untuk urutan eksekusi,
`plan.*` yang menang untuk detail perintah, `SEO-AUDIT-2026-09-24.md` yang menang untuk fakta/angka.

---

## URUTAN EKSEKUSI — KUNCI 24 SEPTEMBER 2026 (keputusan user)

> **`beriklan.co.id` dikerjakan LEBIH DULU, fase demi fase, sampai semuanya selesai dan terbukti
> *running well*. Baru setelah itu `beriklan.my` disentuh.**

Aturan turunan yang mengikat semua pekerjaan berikutnya:

1. **Semua baris ber-Domain `.my`** di tracker ini berstatus ⏸️ **DEFERRED**. Jangan dieksekusi,
   jangan di-deploy, jangan diubah konfigurasinya — termasuk perubahan yang terlihat sepele
   (secret, cron, `run_worker_first`, normalisasi nomor, sitemap `.my`).
2. **Baris ber-Domain `both`** dieksekusi **hanya untuk co.id** (ditandai `co.id dulu · .my ⏸️`).
   Bagian `.my`-nya dikerjakan belakangan sebagai satu batch terpisah setelah co.id dinyatakan stabil.
3. **Pengecualian yang sudah selesai dan tidak diulang:** 0.2 (backup D1 `.my`) ✅ — backup tetap ada,
   itu pengaman, bukan perubahan live.
4. **Infrastruktur VPS/Postgres (0.9, 0.11, 0.13) tetap jalan** karena dipakai co.id lebih dulu;
   `repo-my` / build `.my` di VPS (0.10, 0.12) ditunda.
5. **Definisi "running well" untuk co.id** (gerbang sebelum menyentuh `.my`) — semua harus ✅ terverifikasi
   dengan output perintah nyata:
   - Fase 0 co.id selesai (0.1, 0.3–0.6, 0.8, 0.9, 0.11, 0.13).
   - Publish cap 15/hari berlaku dan stabil **≥ 3 hari** (`cron_runs` `sync-posts` → `daily_limit: 15`,
     terbit ≤ 15/hari, 0 duplikat, `queue_cursor` maju normal).
   - Beban D1 turun: `d1 insights` 1 jam < 200 rb rows, tidak ada error 7500 / quota lock.
   - Growth loop menghasilkan sesuatu: `growth_log` bertambah setelah `GSC_SITE_URL` diperbaiki.
   - Situs sehat: `/` 200, slug D1-only 200 artikel asli, slug palsu 404, sitemap 200,
     tidak ada soft-404, tidak ada asset desync.
   - Backup + `version_id` rollback masih tercatat dan valid.
6. **Dilarang "sekalian" mengerjakan `.my`** walau satu perintah, walau sedang memegang konteks `.my`.
   Bila ada temuan mendesak di `.my` (mis. kuota/error), **catat di tracker sebagai temuan, lapor user,
   tunggu izin** — jangan langsung eksekusi.

---

## FASE 0 — STABILISASI & PENGAMAN (prasyarat semua fase lain)

| # | Task | Domain | Status | Verifikasi | Rollback |
|---|---|---|---|---|---|
| 0.2 | Backup D1 penuh `beriklan-my-seo` | .my | ✅ **2026-09-24** | `backup/beriklan-my-seo-20260924.sql` = **344.648.587 B, 108.757 INSERT, 48 tabel**. Top: generated_drafts 65.337 · keyword_queue 35.864 · pending_indexing 1.795 · trending_topics 1.338 · **posts_meta 1.337 = posts_content 1.337 = sitemap live 1.337** (✅ cocok, tidak ada selisih seperti co.id). Tambahan: `backup/` ditambahkan ke `.gitignore` .my (sebelumnya tidak di-ignore → backup 329 MB rawan ikut commit). | T/A |
| 0.7 | Hapus token hardcoded di worker `.my:696` | .my | ⏸️ **DEFERRED** (co.id dulu) | `grep -n "token=" src/worker-entry.js` tidak lagi memuat nilai token literal (harus `env.ADMIN_TOKEN`) | restore `.bak` |
| 0.10 | **Perbaiki rsync repo → VPS** (`/opt/migration/repo-my`) | .my | ⏸️ **DEFERRED** (co.id dulu) | `find src/pages -type f \ | wc -l` > 50 | rsync ulang |
| 0.12 | **Buktikan build Astro di VPS (.my)** | .my | ⏸️ **DEFERRED** (co.id dulu) | idem, ≈ 1.337 dir blog | T/A |

**Exit Fase 0:** 0.1–0.13 ✅. **0.9–0.12 adalah pembatal klaim lama** (audit §9.5):

### TEMUAN VPS 24 SEPTEMBER 2026 (terverifikasi, menggantikan klaim lama)

### 🛠️ REBUILD + REDEPLOY DARURAT 24 Sep 22:50–22:57 UTC

Penyebab: `dist/` folder kosong (0 file) sejak build sebelumnya; deploy `6f8b3dfd` upload 0 asset → `/` & `/blog/` 404 (ASSET DESYNC total, bukan stale).

**Tindakan:**
1. **Backup** `wrangler.jsonc` → `wrangler.jsonc.bak-fix-dist-20260924-225206`
2. **Cleanup Fase 0.6 (rampung)**: `vars: {}` di wrangler.jsonc (ADMIN_TOKEN hanya via Cloudflare secret; sebelumnya masih ada `vars.ADMIN_TOKEN`, redundancy ringan tapi bukan best practice)
3. **Rebuild lokal**: `cd web && npm run build` → 10.096 URL (8 static + 10 services + 385 city + 10 pillar + 120 harga + 7.497 blog + 312 blog-pagination + 1.754 blog-tag), 10.122 halaman, 165,04 s
4. **Redeploy**: `cd web && npx wrangler deploy` → upload **10.133 dari 10.133 assets** (307 cache-hit), 214,62 s → **version `202bb9ba-224b-4fb0-88b6-741364a6e315`**

**Verifikasi live (semua ✅):**
| Endpoint | HTTP | bytes | Catatan |
|---|---|---|---|
| `/` | 200 | 79.898 | identik baseline 0.6 |
| `/blog/` | 200 | 73.439 | blog index |
| `/blog/digital-consultant-bekasi/` | 200 | 97.375 | D1-rendered post |
| `/jasa-iklan-facebook/` | 200 | 166.634 | service page (301 dari `/jasa-iklan-facebook`) |
| `/data/posts-index.json` | 200 | 8.390.496 | TODO 1.11 (pangkas < 200 KB) |
| `/sitemap-blog.xml` | 200 | 3.511.214 | sitemap generator output |
| `/api/cron/indexnow?count=5` | 200 | 967 | new 2-query path ✅ |
| `/api/cron/gsc-indexing?count=2` | 200 | — | new LIKE-less path ✅ |

**Bundle size** upload: 887,82 KiB / gzip 175,04 KiB (termasuk service worker + 10.133 asset).
**Schedules** aktif: hanya `0 * * * *` + `*/15 * * * *` (crons `30 6 * * *` / `0 7 * * *` / `0 3 * * 1` sudah tidak ada di wrangler.jsonc → 5 slot jadi 2 terpakai, sesuai Fase 0 konsolidasi).
**Binding** tampil: `DB, QUEUE, AI, ASSETS` (ADMIN_TOKEN tidak ditampilkan = ada di secret ✓).

**Pelajaran:** setiap `wrangler deploy` HARUS didahului `npm run build` di `web/`. Sebelum 0.6 lalu belum tentu sama (deploy CF otomatis rebuild + upload via GitHub). Sekarang pakai mode manual via CLI = HARUS build lokal dulu.

| Fakta | Bukti |
|---|---|
| VPS = `smm`, Ubuntu, kernel 6.8.0-88-generic, `130.254.47.93` (IPv6 `2607:adc0:5::215`) | `hostname; uname -a` |
| **Pipeline SEO beriklan HIDUP** sebagai app Coolify, bukan compose standalone | `curl 127.0.0.1:18743/` → `{"ok":true,"service":"seo-pipeline","version":"0.1.0"}`; container `igsbaxpsvuhopghoutiit2kk-085951037002` Up 9 days |
| Compose `/opt/seo-pipeline/docker-compose.yml` ada tapi container-nya **Exited(137)** sejak 15 Sep 06:15 UTC (`OOMKilled=false`) — digantikan deploy Coolify | `docker inspect seo-pipeline-app-1` |
| Postgres 16.15 = container `vonbh1dpbrfzlrm26lwvdain`, DB/user `seopipe`, schema `public/coid/comy/shared` | `psql -tAc "SELECT version()"` |
| Tabel sebelum 0.13: `coid.keyword_queue`(10), `coid.publish_outbox`(19), `comy.*`, `shared.job_runs`(333), `shared.sync_state`(1), `shared.geo_mentions`(0) | `pg_stat_user_tables` |
| Job pipeline yang ada: `distribute`, `earned-media`, `freshness`, `geo-monitor`, `news-ping`, `runner`, `lib` | `ls /opt/seo-pipeline/app/jobs/` |
| Log terakhir app (sebelum mati): news-ping OK — `beriklan.co.id: 5010 urls seen, 10 fresh<36h`, IndexNow bing+api 200 | `docker logs seo-pipeline-app-1` |
| `.env` pipeline berisi: `POSTGRES_PASSWORD, PIPELINE_TOKEN, DATABASE_URL, DEBUG_IP, INDEXNOW_KEY_COID, INDEXNOW_KEY_COMY, TZ` (nilai tidak dibaca) | `sed -E 's/=.*/=<redacted>/'` |
| **RAM ketat**: 3.915 MB total, free 404 MB, **swap 1.442/2.047 MB terpakai**, disk 145G (terpakai 29G) | `free -m; df -h /` |
| **Project lain di VPS — DILARANG DISENTUH**: `sgb-dashboard`, `mailserver`, `mailu`, `coolify*`, app Coolify `nqsjafrei6k8…`, `xeamhqvjpz9x…`, `h99bx9ps0h…`, `awesome_goldwasser`, mysql `lmzgomlezarhl…`, `rebicrj57r3a…` | `docker ps -a` |
| `/opt/migration/repo-coid` (543 MB) & `repo-my` (1,1 GB) = salinan repo lama, `package.json` bernama `haloka-landing` (sama seperti repo lokal — nama lama, bukan kontaminasi) | `cat .../web/package.json` |
sebelumnya tercatat "build VPS OK" padahal `repo-coid/web/src` = 0 file.

---

## FASE 1 — HENTIKAN PENDARAHAN (1 deploy/domain, risiko rendah)

| # | Task | Domain | Status | Verifikasi | Rollback |
|---|---|---|---|---|---|
| 1.3 | Konfirmasi `.my` tetap tanpa secret `GSC_SITE_URL` (default kode sudah benar) | .my | ⏸️ **DEFERRED** (co.id dulu) | `wrangler secret list` tanpa `GSC_SITE_URL` | T/A |
| 1.5 | Set `INDEXNOW_KEY` .my + hapus fallback ke key co.id | .my | ⏸️ **DEFERRED** (co.id dulu) | `/api/cron/indexnow` → `submitted > 0` | hapus secret |
| 1.6 | Fix `normalizePhoneForWa` → prefix `60` | .my | ⏸️ **DEFERRED** (co.id dulu) | uji fungsi dengan `0123456789` → `60123456789` | restore `.bak` |
| 1.7 | Keputusan nomor CTA .my (`wa.me/62811919328` ×14.543) | .my | ✅ **DIPUTUSKAN 24 Sep** | Keputusan user: **tetap nomor Indonesia** (satu pintu untuk semua pasar) → **tidak ada** penggantian massal. Yang tetap harus dikerjakan hanya 1.6 (normalisasi nomor MY milik *pengunjung*, bukan nomor CTA). | T/A |
| 1.10 | Fix `sitemap-tag.xml` .my (0 URL) | .my | ⏸️ **DEFERRED** (co.id dulu) | `grep -c '<loc>'` > 0 | restore `.bak` |
| 1.13 | PUT cron `.my` setelah deploy (`[{"cron":"0 * * * *"}]`) | .my | ⏸️ **DEFERRED** (co.id dulu) | `GET .../schedules` menampilkan cron | PUT `[]` |

**Exit Fase 2:** hitung 3-arah cocok · **tidak ada** baris D1 yang dihapus · dual-write stabil 3 hari.

---

## FASE 3 — R2 CONTENT STORE + DUAL-READ WORKER

| # | Task | Domain | Status | Verifikasi | Rollback |
|---|---|---|---|---|---|
| 3.6 | `.my`: pastikan `/blog/*` tetap di `run_worker_first` | .my | ⏸️ **DEFERRED** (co.id dulu) | 20 path tercetak; `/blog/*` ada | restore jsonc |

**Exit Fase 3:** 0 soft-404 · jumlah artikel live ≥ baseline · serve tidak menyentuh D1 · kill-switch teruji.

> **FASE 3 SELESAI — 2026-09-25 06:10 UTC (beriklan.co.id)**: 16.819 posts uploaded ke R2 (`coid/blog/<slug>.json` 71.7 MB), dual-read worker `R2 → D1 → static → 404 jujur`, kill-switch `USE_R2` teruji, token rotation selesai + refactor `${env.ADMIN_TOKEN}` template literal (next rotasi = 1 command), 50/50 slug random 200, bogus 404, semua cron internal OK. **Pindah ke Fase 4 (co.id) + replikasi sistem ke beriklan.my.** Panduan replikasi: `MY-MIGRATION-GUIDE.md`.

---

## FASE 4 — INDEXASI & PERTUMBUHAN (bukan volume)

| # | Task | Domain | Status | Verifikasi | Rollback |
|---|---|---|---|---|---|
| 4.5 | Audit 4.723 entri `posts.json` .my yang belum jadi URL (saring kualitas, rilis bertahap ≤ 300) | .my | ⏸️ **DEFERRED** (co.id dulu) | jumlah URL live naik bertahap; 0 soft-404 | rollback build |

**Exit Fase 5:** D1 rows read/hari < 500.000 · 0 error 7500 selama 7 hari · jumlah artikel live tidak berubah.

---

## FASE 6 — EKSPANSI INDUSTRI (`INDUSTRY-EXPANSION.md`)

| # | Task | Domain | Status | Verifikasi | Rollback |
|---|---|---|---|---|---|
| 6.6 | Wave 1 .my — Construction/contractor (EN) | .my | ⏸️ **DEFERRED** (co.id dulu) | idem + `run_worker_first` diperbarui bila ada path baru | unpublish batch |
