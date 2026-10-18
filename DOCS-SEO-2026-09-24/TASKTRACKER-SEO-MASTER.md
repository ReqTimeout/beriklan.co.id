# TASKTRACKER-SEO-MASTER.md — POINTER (sudah DIPISAH per domain, 27 Sep 2026)

> File ini tidak lagi berisi task. Isi lengkap riwayat (baseline 24 Sep, Fase 0–8, temuan VPS,
> rebuild darurat 22:50, seri 4.0) tetap awet di backup:
> `TASKTRACKER-SEO-MASTER.md.bak-split-20260927-100000`.
> Pemisahan dilakukan oleh agen Qoder pada 27 Sep 2026 atas permintaan user;
> log pengerjaan: `LOG-EKSEKUSI-PLAN.md`.

## Ke mana sekarang

| Butuh | Buka |
|---|---|
| Task + status + bukti eksekusi **beriklan.co.id** | **`TASKTRACKER-COID.md`** |
| Task **beriklan.my** (semua ⏸️ DEFERRED + daftar replikasi) | **`TASKTRACKER-MY.md`** |
| Rencana kerja super-detail untuk coding agent (muse spark 1.3) — co.id | **`EXECUTION-COID-FOR-AGENT.md`** |
| Catatan duplikasi sistem co.id → .my | **`MY-DUPLICATION-PLAN.md`** |
| Status lintas-fase ringkas co.id | `../REKAP-COID.md` |
| Fakta & angka audit | `SEO-AUDIT-2026-09-24.md` |
| Detail perintah per fase | `plan.co.id.md` / `plan.my.md` |
| Ekspansi industri | `INDUSTRY-EXPANSION.md` |

## Aturan induk yang TETAK mengikat (salinan dari versi penuh)

1. **co.id DULU** sampai selesai & terbukti *running well* (6 syarat terukur ada di
   `TASKTRACKER-COID.md` §URUTAN EKSEKUSI butir 5), baru `.my`. Dilarang mengerjakan `.my` "sekalian".
2. **Dokumen clear dulu** — tidak ada perubahan live (D1, secret, cron, deploy) tanpa aba-aba user.
3. Tidak ada artikel yang dihapus — migrasi = memindah. Publish 10–15/hari, kualitas di atas volume.
4. Pindah dari D1 tanpa kehilangan satu artikel pun. `DELETE` D1 hanya setelah persetujuan tertulis (Q4).
5. Urutan industri: kontraktor → toko bangunan/bahan bangunan → tekstil (konveksi/garmen) → perumahan;
   semua konten baru masuk lewat `/blog/*` saja (tidak ada route baru).
6. GEO/LLM diukur **keyless** (SearXNG self-hosted). Nomor CTA `.my` tetap `+62 811-919-328`.
7. Visual/UI tidak disentuh; deploy hanya dengan persetujuan eksplisit; produksi rusak = rollback sekarang.

<!--EOF-->
