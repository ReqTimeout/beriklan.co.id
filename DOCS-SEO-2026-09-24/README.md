# DOCS-SEO-2026-09-24 — Paket Dokumen Audit & Rencana SEO

> **Dibuat:** 24 September 2026 · **Revisi terakhir:** 27 Sep (pemisahan tracker per domain — `TASKTRACKER-COID.md` / `TASKTRACKER-MY.md`, lihat `LOG-EKSEKUSI-PLAN.md`)
> **Status:** co.id Fase 0–2 selesai (rekap: `../REKAP-COID.md`) · sisanya **menunggu aba-aba user**
> **Cakupan:** `beriklan.co.id` + `beriklan.my` + VPS `130.254.47.93` + Cloudflare (Worker/D1/R2/Pages)
> **Aturan path:** semua path repo di dalam dokumen ini relatif terhadap **root repo**
> (`/Volumes/macmini/Desktop/beriklan.co.id`), yaitu satu level di atas folder ini.

---

## ⚠️ Dua hal yang wajib dibaca sebelum menyentuh apa pun

**1. Urutan eksekusi (keputusan user, 24 Sep):**
> **`beriklan.co.id` DULU, fase demi fase, sampai selesai dan terbukti *running well*. Baru `beriklan.my`.**
> Semua task `.my` = ⏸️ DEFERRED. Task ber-domain `both` dikerjakan sisi co.id saja.
> Dilarang mengerjakan `.my` "sekalian", walau satu perintah.
> Gerbang "running well" (6 syarat terukur) ada di `TASKTRACKER-SEO-MASTER.md` §URUTAN EKSEKUSI butir 5.

**2. Dokumen harus clear dulu (keputusan user, 24 Sep):**
> Tidak ada perubahan live (D1, secret, cron, deploy) sampai user menyatakan dokumen sudah jelas
> dan memberi aba-aba mulai. Fase 0.1–0.5 yang sudah jalan bersifat **pengaman/backup/catatan**,
> bukan perubahan perilaku situs.

**3. Koreksi besar atas pemahaman pipeline (24 Sep):** generate artikel terjadi **di lokal**, bukan di Worker.
Worker hanya mengisi buffer dari antrian R2 lalu mempublish harian. Detail + bukti: audit **§6.5** (co.id)
dan **§6.6** (`.my` + sakelar VPS yang belum menyala). Dokumen lama/`AGENTS.md` yang menyebut
"cron hourly generate 3 artikel/jam" **sudah tidak berlaku** (`cron_settings.hourly` = AUTO-PAUSED).

---

## Urutan baca (untuk review)

| # | File | Baca untuk | Ukuran |
|---|---|---|---|
| 1 | **`SEO-AUDIT-2026-09-24.md`** | Fakta & bukti. Semua angka dari tool call nyata. Mulai §0 (7 temuan) → **§6.5/§6.6 (pipeline sebenarnya)** → §8 (beban D1) → §15 (baseline KPI). | 54,6 KB / 20 seksi |
| 2 | **`TASKTRACKER-COID.md`** | Tracker eksekusi **co.id saja** (76 task, riwayat + bukti). `TASKTRACKER-SEO-MASTER.md` sekarang hanya pointer. | 68,8 KB |
| 2b | **`TASKTRACKER-MY.md`** | Tracker **`.my` — semua ⏸️ DEFERRED** (13 task murni + daftar 35 task `both` wajib direplikasi pasca-gerbang). | 14,2 KB |
| 2c | **`EXECUTION-COID-FOR-AGENT.md`** | Dokumen kerja super-detail untuk coding agent lain (muse spark 1.3): §0 aturan, T0 deploy guard 1.16, T0b tutup gap verifikasi 2.7/2.8/R2, T1 Fase 4, T2 bug write-back R2, T3–T6 tool baru (winner keyword, wave runner, LLM visibility, freshness), T7 Fase 5–8. | baru |
| 2d | **`MY-DUPLICATION-PLAN.md`** | Catatan: `.my` duplikat 100% sistem co.id; beda bahasa + keyword pasar Malaysia + teknis §13.2. | baru |
| 2e | **`LOG-EKSEKUSI-PLAN.md`** | Catatan pekerjaan per fase (kapan apa diverifikasi, bukti output). | baru |
| 3 | **`plan.co.id.md`** | Cara eksekusi co.id: Fase 0–7, perintah siap tempel, exit criteria, runbook verifikasi & rollback. **§C.1.1 sudah dikoreksi** (nama kolom `cron`, seed kode baris 3734–3737). | 35,5 KB |
| 4 | **`plan.my.md`** | Cara eksekusi `.my` (**ditunda**): perbedaan pasar EN/MY, IndexNow, normalisasi nomor `60`, `run_worker_first`, cron manual. **§1.7 sudah dikoreksi** (nama setting `daily_publish_limit`, bukan `publish_daily_limit`). | 24,5 KB |
| 5 | **`INDUSTRY-EXPANSION.md`** | Ekspansi vertikal: 2.291 keyword terpetakan, wave 1–4, gerbang kualitas & validasi. Semua masuk lewat `/blog/*`. | 18,8 KB |
| — | `../REKAP-COID.md` | **Baseline status lintas-fase co.id terbaru** (27 Sep): apa yang hidup, apa yang belum terbukti, keputusan yang menunggu user. | 5,4 KB |
| — | `arsip/TASKTRACKER-MIGRATION-VPS.md` | **Riwayat saja — jangan dieksekusi.** Berisi klaim "build VPS OK" yang terbukti salah (audit §9.5). | 13,3 KB |

---

## Isi paket dalam 1 paragraf

Situs punya **16.872 URL blog** (= `posts_meta` 16.686 + `generated_drafts` committed 186; selisih ini
terpecahkan di Fase 0.3) tetapi hanya **159 klik/28 hari**, dan **47% klik** justru datang dari subdomain
classifieds `id.beriklan.co.id`. Artikel baru masih *"unknown to Google"*. Beban D1 **5,36 juta rows
read/hari** = **107% kuota free tier**, dan **68,5%-nya** dari 3 query `pending_indexing` — **46,3%** dari **satu** query ber-`OR`
yang scan penuh berulang, padahal tabelnya cuma **17.026 baris** (angka "3,8 juta" di dokumen lama
**salah**, sudah dikoreksi). Growth loop **jalan tiap hari tapi mandul**: `cron_runs` mencatat
`growth-enrich`/`ctr-fix` `ok`, namun `growth_log` berhenti di 30 Agu karena `GSC_SITE_URL` menunjuk
properti `www` (527 impresi) bukan `sc-domain` (12.923). Migrasi ke Cloudflare Pages **static tidak layak**
untuk co.id: **9.373 URL** hanya ada di D1 dan Pages melempar **soft-404**, sementara cap 20.000 file
sudah terpakai 10.178. Karena itu arsitektur target = **R2 (content) + Postgres VPS (factory) +
Worker tipis (edge)**, D1 hanya untuk operasional kecil.

## Keputusan yang sudah dikunci user

1. Tidak ada artikel yang dihapus — migrasi = memindah, bukan membersihkan.
2. Publish **10–15 artikel berkualitas/hari** (bukan 400–600/hari).
3. Pindah dari D1 tanpa kehilangan satu artikel pun.
4. Urutan industri: kontraktor → toko bangunan/bahan bangunan → tekstil (konveksi/garmen) → perumahan.
5. Pengukuran GEO/LLM **keyless** (SearXNG self-hosted, tanpa API berbayar).
6. Tulis dokumen lengkap dulu sebelum eksekusi.
7. Visual/UI tidak disentuh; deploy hanya dengan persetujuan eksplisit.
8. Nomor CTA `.my` **tetap `+62 811-919-328`** (satu pintu) — dilarang penggantian massal 14.543 kemunculan.
9. **Tidak ada route baru di luar `/blog/*`** — semua konten ekspansi masuk sebagai artikel blog.
10. **co.id DULU sampai *running well*, baru `.my`** — semua task `.my` deferred.
11. **Dokumen harus clear dulu** — tidak ada perubahan live tanpa aba-aba user.

## Yang masih menunggu keputusan user

| # | Pertanyaan | Status | Memblokir |
|---|---|---|---|
| Q3 | `run_worker_first` `.my`: pertahankan 20 path eksplisit atau sederhanakan jadi `["/*"]`? | ⏸️ ditunda (fase `.my`) | Fase 3 `.my` |
| Q4 | Persetujuan `DELETE` data D1 (setelah verifikasi hitung 3-arah) | ⬜ terbuka | Fase 5 |
| Q5 | 4.723 entri `posts.json` `.my` boleh dirilis bertahap jadi URL? | ⏸️ ditunda (fase `.my`) | Fase 4 `.my` |
| Q6 | Kapan eksekusi boleh dilanjutkan (0.1–0.5 co.id sudah ✅/🔄) | ⚠️ **menunggu aba-aba** | semua fase |
| Q7 | `trending-generate` `.my` masih `enabled=1` — pause atau biarkan? | ⏸️ ditunda (fase `.my`) | Fase 1.7 `.my` |
| Q8 | Cap publish 15/hari: kedua domain sekaligus atau co.id dulu? | ✅ **terjawab**: co.id dulu | — |

## Keamanan dokumen

Tidak ada rahasia plaintext di paket ini. Yang ada hanya **prefix ter-mask** dari key Groq lama
(8 karakter pertama) sebagai penanda untuk revoke — bukan key yang bisa dipakai. Semua perintah memakai
placeholder (`$ADMIN_TOKEN`, `$PIPELINE_TOKEN`, `$CF_API_TOKEN`, `$VPS_PASS`, `$GROQ_API_KEY`);
daftar lengkapnya di `plan.co.id.md` §L.

**Tindakan yang masih harus dilakukan user:** revoke key Groq lama ber-prefix `gsk_FNRab69U…` di
dashboard Groq (key baru sudah terpasang sebagai secret `GROQ_API_KEY`).
**Tindakan Fase 0 berikutnya (butuh aba-aba):** 0.6 `ADMIN_TOKEN` → secret · 0.8 pastikan SA JSON GSC
ter-ignore · 0.9/0.11 rsync + bukti build co.id di VPS · 0.13 skema Postgres.
