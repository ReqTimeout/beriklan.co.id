# REKAP .co.id — Sudah vs Belum

> **Tanggal:** 25 September 2026 (±15:00 WIB / 08:00 UTC)
> **Worker live:** `10efe09f-463b-4603-b977-5f23d48d4715` · cron: `0 * * * *` (1 slot)
> **Jawaban singkat:** TIDAK, belum semua. Yang hidup & sehat: publish, indexing, email (mulai besok), growth. Yang belum: Fase 3 penuh, 2.7/2.8 verifikasi end-to-end, Fase 4–8, + 1 fix menunggu persetujuan deploy.

**⚠️ Hindari salah baca:** "Seri 4.0" (4.0a–4.0e = recovery pasca-refactor, SUDAH live) BUKAN "Fase 4" (Indexasi & Pertumbuhan, BELUM mulai).

---

## 1. STATUS PER FASE

| Fase | Status | Ringkasan |
|---|---|---|
| 0 Stabilisasi | ✅ 7/9 (0.5 ⏸️, 0.11 🚫) | Selesai. 0.5 deprioritized (key lama tak ditemukan), 0.11 cancelled (fallback built-in) |
| 1 Pendarahan | ✅ 15/16 + 🟡 1.16 | Hampir selesai. Sisa 1.16 monitoring + 1 fix cap-bypass BELUM DEPLOY |
| 2 Postgres | ✅ 6/8 (kode 8/8) | Backfill done. 2.7/2.8: kode + gate AKTIF, verifikasi end-to-end belum ada |
| 3 R2 dual-read | 🟡 partial | Fallback code + backfill ada. Belum pernah terbukti fire saat D1 down |
| 4 Indexasi | ⬜ 0% | Belum mulai sebagai fase (baru insidental via 4.0b) |
| 5 Trim D1 | ⬜ 0% | Butuh persetujuan user (Q4) |
| 6 Industri | ⬜ 0% | Wave 1 kontraktor tertunda (Q5 untuk .my) |
| 7 GEO | ⬜ 0% | SearXNG keyless belum setup |
| 8 Monitoring | ⬜ 0% | Serah terima belum |

---

## 2. SUDAH ✅ (dengan bukti)

### Fase 0
- 0.1, 0.3, 0.4, 0.6 (vars cleanup — ADMIN_TOKEN hanya via secret), 0.8, 0.9 (re-scope), 0.13

### Fase 1
- **1.1** cap publish 15/hari + batch 5 (live; TAPI lihat §3 temuan 25 Sep — cap jebol via jalur manual)
- **1.2** growth loop aktif (GSC secret return 993–3.556 rows, 24 Sep)
- **1.4a–e** lima sub-fix (cap, index, LIMIT 50 → 8,3 MB jadi 24,9 KB, dst.)
- **1.8** queue hoist, **1.9** news.xml 825 URL, **1.11** BlogFilter mapping, **1.14** runbook verifikasi, **1.15** Zen/Groq fix
- **1.12** satukan kuota GSC (live 25 Sep 00:32; kode masih ada line 2099/9896 pasca-4.0)
- **Seri 4.0a–e** (25 Sep): email-send pindah ke time-gate `m%15===0`, IndexNow 50→100, email queue cleanup (DELETE 1.152 corrupt), growth thresholds turun → ctr-fix `fixed=3` di run pertama

### Fase 2
- **2.0–2.6**: schema audit, NDJSON export, backfill 7/7 tabel byte-identical, re-skoring (2.990 `service=''` → rejected)

### Operasional hari ini (observasi 25 Sep)
- Publish: 32 artikel (pipeline HIDUP)
- IndexNow: batch 100/firing per jam
- Email: cron resumed, mulai kirim besok 00:00 UTC (quota 95/100 hari ini)
- Growth: enrich + ctr-fix + gsc-loop return kandidat (tidak lagi 0)
- Draft buffer: 349 (aman, ~23 hari pada cap 15)

---

## 3. BELUM ⬜ / 🟡 (dengan apa yang kurang)

### 🟡 1.16 — monitoring + 1 FIX MENUNGGU DEPLOY
- **Temuan 25 Sep:** publish 32 vs cap 15. Akar: `POST /api/admin/drafts/commit` (`handleAdminDraftsCommit`) commit `LIMIT 50` **tanpa cek cap**.
- **Fix sudah ditulis** (guard `remainingTodayCap`, backup `worker-entry.js.bak-1.16-20260925-145652`, `node -c` OK) — **BELUM DEPLOY, butuh persetujuan eksplisit**.
- Definisi 1.16 di-rewrite (terminologi lama `queue_cursor`/shard kedaluwarsa).

### ⬜ 2.7 dual-write PG — kode + gate AKTIF, belum terverifikasi
- Kode ada (line 2522: enqueue ke `coid.publish_outbox` via pipeline). Gate `pipeline_source=vps` AKTIF di D1 + secret `PIPELINE_API_URL`/`PIPELINE_TOKEN` terpasang.
- **Kurang:** bukti 1 artikel lewat jalur VPS end-to-end (pull → publish → ack). Fallback D1 aman jika VPS kosong.

### ⬜ 2.8 sakelar VPS pull — sama seperti 2.7
- Kode hybrid pull ada (line 2265–2296, timeout 18s + ack idempotent). Gate sama.
- **Kurang:** verifikasi yang sama. Rollback = 1 query (`UPDATE cron_settings SET cron='d1' WHERE name='pipeline_source'`).

### 🟡 Fase 3 R2 dual-read — code + data ada, belum terbukti
- `_renderBlogFromR2` (line 15280) + kill-switch `USE_R2` + backfill 16.819 posts ada.
- **Kurang:** belum pernah fire saat D1 down (simulasi atau insiden nyata). Tanpa itu = single point of failure di D1.

### ⬜ Fase 4–8 — belum mulai
- **4 Indexasi:** strategi submit (GSC 200/hari, IndexNow, index-verify 300/hari) jalan insidental, belum jadi fase terkelola.
- **5 Trim D1:** butuh persetujuan DELETE (Q4 terbuka).
- **6 Industri:** wave kontraktor via `/blog/*` (Q5 terbuka untuk .my).
- **7 GEO:** SearXNG keyless belum ada.
- **8 Monitoring:** serah terima + alerting belum.

---

## 4. BUTUH KEPUTUSAN USER

| # | Keputusan | Blocking |
|---|---|---|
| D1 | Deploy fix cap-bypass 1.16? (kode siap, syntax OK) | cap 15/hari tetap jebol tiap ada yang tekan Commit |
| Q3 | `run_worker_first` .my: 20 path vs `["/*"]`? | Fase 3.6 .my |
| Q4 | Persetujuan DELETE data D1? | Fase 5 |
| Q5 | 4.723 entri `posts.json` .my dirilis bertahap? | Fase 4.5/6 .my |
| Q7 | `trending-generate` .my (`enabled=1`) dibiarkan atau di-pause? | Fase 1.7 .my (nanti) |

---

## 5. FILE TERKAIT

- Tracker: `DOCS-SEO-2026-09-24/TASKTRACKER-SEO-MASTER.md` (baris 1.16 = definisi baru + forensik)
- Dashboard: `DASHBOARD-URLS.md` (token baru `7ff57542…`, token lama 401)
- Migrasi .my: `MY-MIGRATION-GUIDE.md` (§4.9–4.13 lessons dari seri 4.0)
- Kode: `web/src/worker-entry.js` (15.346 baris; backup `.bak-1.16-20260925-145652`)

---

**Maintainer:** Beriklan Digital Agency + Codex AI
**Versi:** 1.0 (2026-09-25)
