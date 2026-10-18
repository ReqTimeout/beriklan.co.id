# MY-DUPLICATION-PLAN.md — `.my` Menduplikasi 100% Sistem co.id
### Dicatat 27 September 2026 — berlaku SETELAH gerbang `beriklan.co.id` *running well* dibuka (keputusan user #10)

> **PRINSIP INTI (perintah user, 27 Sep):** `.my` harus mengikuti SEMUA sistem co.id.
> Yang boleh berbeda HANYA: **bahasa (EN-MY), keyword/riset pasar Malaysia, dan teknis khas .my**
> (di §3 file ini). Selain itu = salin apa adanya, termasuk task T0–T7 di
> `EXECUTION-COID-FOR-AGENT.md` yang dikerjakan SETELAH 27 Sep — setiap sistem baru di co.id
> wajib dicatat di §4 "re-sync log" sebelum gerbang .my dibuka.

---

## 1. Gerbang pembuka (jangan mulai tanpa ini)

1. co.id lolos 6 syarat *running well* (`TASKTRACKER-COID.md` §URUTAN EKSEKUSI butir 5)
   **PLUS** 3 bukti `§T0b` (2.7, 2.8, failover R2) dan `§T2` (write-back R2) terpasang —
   karena sistem yang diduplikasi adalah sistem HASIL perbaikan itu.
2. Pernyataan "mulai .my" eksplisit dari user. Sebelum itu: semua `TASKTRACKER-MY.md` ⏸️.

## 2. Daftar sistem yang diduplikasi (state co.id per 27 Sep → wajib ada di .my)

| Sistem co.id | Ref | Duplikasi di .my |
|---|---|---|
| Publish cap 15/hari + batch 5 via `cron_settings` (kolom `cron`!) | 1.1 | setting `.my` namanya `daily_publish_limit` (40→15) + seed kode baris ~2023 (`let dailyLimit = 50;`) — JANGAN pakai nama kolom salah |
| Guard anti-bypass cap di drafts/commit | T0 (1.16) | porting guard identik |
| Query D1 index-perfect (pending_indexing 2-query, LIKE dihapus, LIMIT 50 posts-index) | 1.4a-d | salin pola yang sama ke `worker-entry.js` .my |
| Migration array index (doc-only) | 1.4e | audit index .my vs kode; tambahkan yang hilang |
| Kuota GSC satu sumber (kolom `value`, UTC) | 1.12 | identik |
| news.xml 48h/1000 URL, llms.txt/llms-full | 1.9, T5.2 | identik + bahasa EN-MY |
| Postgres source of truth (`comy.*` schema SUDAH ADA di `seopipe`) | Fase 2 | backfill NDJSON keyset seperti 2.1-2.5; verifikasi 3-arah |
| Dual-write PG + sakelar VPS pull (`domain=my`) | 2.7/2.8 + T0b | pipeline sudah multi-domain (`INDEXNOW_KEY_COMY` ada di .env VPS); verifikasi end-to-end dulu sebelum klaim |
| R2 content store prefix `my/blog/<slug>.json` + dual-read + kill-switch `USE_R2` | Fase 3 + T2 | identik; JANGAN hapus posts_content D1 .my sebelum failover canary terbukti |
| Token rotation pola `${env.ADMIN_TOKEN}` | 3.8c | wajib (worker .my masih hardcode token di baris 696 — task 0.7) |
| Winner Keyword Engine | T3 | identik; keyword_ranks properti `sc-domain:beriklan.my` (data lebih tipis: baseline 16 klik/2.195 imp — mulai threshold lebih rendah lagi) |
| Industry Wave Runner | T4 | wave yang sama tapi **bahasa Inggris-Malaysia**: validasi Suggest `hl=en&gl=my`; dataset baru (bukan `industry-keywords.json` ID) — riset dulu (construction, hardware/store bahan, textile/garment, housing — padanan EN) |
| LLM Visibility (ai_crawler_log, llms per industri, SearXNG geo probe domain .my) | T5 | identik; probe query EN-MY |
| Freshness at scale | T6 | identik |
| Monitoring F8 (health email KPI, auto-pause D1, probe 5-menit, AGENTS/DEPLOY-OPS docs) | T7.8 | identik; probe target `beriklan.my` |

## 3. DELTA teknis khas `.my` (satu-satunya yang boleh berbeda — dari audit §13.2/§6.6 + `plan.my.md`)

1. **Bahasa & keyword:** konten EN-MY; copywriting pattern diadaptasi (bukan terjemahan machine); riset keyword pasar Malaysia tersendiri.
2. **`normalizePhoneForWa`** (worker .my ~14231): normalisasi nomor PENGUNJUNG → prefix `60`, buang `0` depan. **Nomor CTA TETAP `+62 811-919-328`** (keputusan #8 — dilarang sentuh 14.543 kemunculan).
3. **`INDEXNOW_KEY`**: set secret .my = key milik .my sendiri (file .txt-nya sudah dilayani di root .my); hapus fallback hardcoded ke key co.id (baris ~13124/13174).
4. **Cron .my TIDAK dibaca `wrangler deploy`**: setelah SETIAP deploy wajib `PUT /accounts/{id}/workers/scripts/beriklanmy/schedules` body **array mentah** `[{"cron":"0 * * * *"}]` (gotcha 10026/10072; pelajaran 4.0a: fail 3× = auto-disable).
5. **`run_worker_first` .my = 20 path eksplisit** (bukan `["/*"]`): setiap route/path baru WAJIB ditambahkan ke daftar, kalau tidak worker di-bypass. (Q3: pertahankan 20 path atau sederhanakan `["/*"]` — **keputusan user dibutuhkan sebelum Fase 3.6**; rekomendasi dokumentasi ini: samakan ke `["/*"]` seperti co.id supaya benar-benar "duplikat sistem", tapi itu mengubah perilaku cache/redirect .my → tetap butuh restu user.)
6. **TANPA secret `GSC_SITE_URL`** di .my (fallback kode `sc-domain:beriklan.my` sudah benar — jangan ditambah secret salah).
7. **Secret `GROQ_API_KEY` belum ada di .my** → tambahkan minimal 1 (fallback AI single-point Zen free yang sudah mati — pelajaran 1.15).
8. **Nama setting publish `daily_publish_limit`** (bukan `publish_daily_limit`), tidak ada `publish_batch_size` — jangan salah nama saat porting.
9. **`trending-generate` .my masih `enabled=1`** (Q7) — satu-satunya generate AI hidup di produksi .my; putuskan pause/lanjut SAAT fase .my dibuka agar semua konten lewat queue ter-QC yang sama dengan co.id.
10. **`sitemap-tag.xml` .my = 0 URL** (task 1.10) — perbaiki saat porting.
11. **4.723 entri `posts.json` .my** (Q5) boleh dirilis bertahap ≤300/minggu setelah disaring — hanya atas izin user.
12. Backup .my 0.2 sudah ✅; `backup/` sudah di-gitignore .my.

## 4. RE-SYNC LOG (wajib diisi setiap ada sistem baru/perubahan arsitektur di co.id setelah 27 Sep)

| Tanggal | Perubahan di co.id (task ID) | Implikasi duplikasi .my | Status |
|---|---|---|---|
| 2026-09-27 | (baseline) dokumen ini dibuat; sistem co.id per `TASKTRACKER-COID.md` + `EXECUTION-COID-FOR-AGENT.md` §T0-T7 | tabel §2 = daftar lengkap | ⬜ menunggu gerbang |
| _(kosong — agent co.id WAJIB menambah baris di sini setiap menyelesaikan task yang mengubah sistem, BUKAN hanya data)_ | | | |

**Aturan pengisian:** agent yang mengerjakan co.id (muse spark 1.3) WAJIB memperbarui tabel ini di sesi yang sama dengan penyelesaian task-nya. Task yang tidak mengubah sistem (sekadar backfill/monitoring) tidak perlu dicatat.

## 5. Urutan kerja saat fase .my dibuka (cermin `EXECUTION-COID-FOR-AGENT.md`)

1. `T0'` = porting guard cap + 0.7 (hapus token hardcoded) + secret Groq + INDEXNOW_KEY sendiri → 1 deploy (dengan persetujuan) → **lalu PUT schedules** (§3.4).
2. `T0b'` = tiga bukti end-to-end versi .my (domain=my, prefix R2 `my/`, schema PG `comy`).
3. `T1'-T7'` mengikuti nomor aslinya satu-satu; DELTA §3 diterapkan di task yang bersangkutan.
4. Gerbang kualitas per wave .my sama ketatnya dengan co.id (INDUSTRY-EXPANSION §7); publish cap 15/hari.
5. Jangan pernah menyentuh project Docker lain di VPS; pipeline sudah multi-domain — verifikasi, jangan rewrite.

<!--END-->
