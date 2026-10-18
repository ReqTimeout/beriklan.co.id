# HANDOFF — PERPINDAHAN WORKSPACE + SISA KERJA
**Ditulis:** 30 Sep 2026 ±08:00 WIB, sebelum proses copy berjalan selesai
**Alasan:** workspace dipindah dari `/Volumes/macmini/Desktop/beriklan.co.id` → `/Volumes/miniex/Users/maabook/web-project/beriklan.co.id`. Copy lama, jadi semua state + sisa kerja ditulis di sini supaya agent berikutnya bisa lanjut tanpa mengulang investigasi.

> **ATURAN POKOK TETAP SAMA** — `AGENTS.md` SOP darurat menang di atas segalanya: jangan sentuh file tampilan (`Layout.astro`, komponen Svelte, CSS), jangan deploy tanpa build+verifikasi lolos, produksi rusak = rollback seketika, jangan ubah sistem berjalan di luar permintaan, setiap ✅ wajib bukti output tool.

---

## 0. Yang berubah karena pindah path

| Hal | Nilai baru |
|---|---|
| Root repo | `/Volumes/miniex/Users/maabook/web-project/beriklan.co.id` |
| Path KANONIKAL (selalu dari sini) | `<root>/web/` → `web/src/worker-entry.js`, `web/wrangler.jsonc`, `web/dist`, `web/scripts/` |
| copies STALE (jangan diedit) | `src/`, `wrangler.jsonc`, `package.json` di root repo |
| Admin token | `<root>/.env.admin` → key `ADMIN_TOKEN` (`set -a; . ./.env.admin`; JANGAN pernah dicetak) |
|artifact sementara | `/tmp/t5/*`, `/tmp/t4/*` — **hilang saat reboot**, jangan bergantung padanya (re-generate kalau perlu) |

**Perintah verifikasi pertama kali setelah pindah (wajib, jangan langsung edit):**
```bash
cd /Volumes/miniex/Users/maabook/web-project/beriklan.co.id
ls web/src/worker-entry.js web/wrangler.jsonc .env.admin DOCS-SEO-2026-09-24
wc -l -c web/src/worker-entry.js          # HARUS ±16.216 baris / 879.188 B (versi LIVE a2ddc246)
python3 - <<'PY'
b=open('web/src/worker-entry.js','rb').read()
bad=[(i,hex(c)) for i,c in enumerate(b) if c<9 or (11<=c<=12 and False) or (14<=c<=31)]
print("control bytes:",len(bad),bad[:5])
PY
node --check web/src/worker-entry.js && echo "SYNTAX OK"
```
Kalau `worker-entry.js` hasilnya **bukan** 16.216 baris / ada control byte / syntax error → copy belum selesai atau korup: **jangan deploy**, ulangi copy dari sumber, laporkan. (Bug lama proyek ini: `\b` di regex berubah jadi byte `0x08` lewat SearchReplace — cek khusus baris `AI_BOT_RE`.)

---

## 1. State produksi SAAT INI (terverifikasi, jangan ditebak ulang)

| Komponen | State |
|---|---|
| Worker `beriklanweb` (akun `766dfffa7e5dcd8ba246ebfa60bc10ba`) | **LIVE `a2ddc246-2a00-43fe-b009-f3dd5dc30c9a`** = T5.1+T5.2+T5.3 |
| Rollback target stabil sebelumnya | `f7d53c28-6dfc-41b0-96bc-81b4435cb9f7` (T3 winner engine) |
| Health runbook | `/` 200 · `/data/posts-index.json` 200 · `/api/health` 200 · `/llms.txt` 200 (27.825 B) · `/llms-full.txt` 200 (137.857 B, 300 baris `URL:`) · `/sitemap-blog.xml` 200 · `/news.xml` 200 · slug palsu 404 |
| D1 `beriklan-seo` (`0e71d6e3-231f-40a1-ac6b-6defc3976efd`) | `ai_crawler_log` ada + 4 baris uji; `cron_settings` id=2654 `industry_wave_state` = `kontraktor|Kontraktor & Jasa Bangunan`; wave-1 `keyword_queue` 49 baris `pending` prio 91–93 |
| Postgres VPS skema `shared.geo_mentions` | Kolom tambahan (day, engine, status, our_rank, results_total, domain) + index sudah dibuat. **3 baris sampah `provider='searxng'` masih ada → harus dihapus** |
| SearXNG VPS | Container `searxng` jalan, `127.0.0.1:8888` (dalam container `searxng:8080` di network `coolify`), 120 MB/300 MB, JSON search terbukti (beriklan.co.id rank 3 utk "jasa iklan facebook bandung") |
| Task tracker | `DOCS-SEO-2026-09-24/TASKTRACKER-COID.md` + `LOG-EKSEKUSI-PLAN.md` — **§T5 BELUM dicatat di keduanya** (lihat §3) |

**Selesai + terbukti live:** T0 (guard cap 1.16), T0b (3 bukti dual-write/pull VPS/R2 failover), T1 (Fase 4 indexasi 4.1–4.4), T2 (write-back R2), T3 (Winner Keyword Engine), T4 (Industry Wave Runner + quality gate), T5.1–T5.3.
**Sisa:** T5.4 (butiran di §2), pencatatan T5 (§3), T6 (§4), T7 (§5), gerbang observasi (§6), temuan yang menunggu keputusan user (§7).

---

## 2. T5.4 — SISA KERJA (urutan persis, semua sudah dipetakan)

File kanonik job: **`DOCS-SEO-2026-09-24/vps-jobs/geo-searxng.js`** (versi TERPERBAIKI, 11.378 B).
Bug yang sudah diperbaiki di file lokal tapi **belum dikirim ke VPS**: `UNIQUE (week, provider, prompt_idx)` di `shared.geo_mentions` TIDAK menyertakan `domain`, jadi upsert domain kedua menimpa metrik domain pertama. Fix: `provider = 'searxng:' + dom`, binds `$1…$13`, filter tren `provider LIKE 'searxng:%'`.

SSH VPS: `ssh -o BatchMode=yes -o ConnectTimeout=15 root@130.254.47.93`
⚠️ macOS **tidak punya** `timeout` — pakai `-o ConnectTimeout`.

```bash
# 2.1 Kirim file yang sudah diperbaiki (dari root repo baru)
scp DOCS-SEO-2026-09-24/vps-jobs/geo-searxng.js root@130.254.47.93:/opt/seo-pipeline/app/jobs/geo-searxng.js

# 2.2 Bersihkan 3 baris sampah hasil smoke test
ssh root@130.254.47.93 'docker exec -i vonbh1dpbrfzlrm26lwvdain psql -U seopipe -d seopipe -c "DELETE FROM shared.geo_mentions WHERE '"'"'provider = '"'"''"'"'searxng'"'"''"'"'";"'
# → lebih aman: tulis SQL ke file lokal lalu:  ssh root@… 'docker exec -i vonbh1dpbrfzlrm26lwvdain psql -U seopipe -d seopipe' < cleanup.sql
# Cek: SELECT provider, domain, count(*) FROM shared.geo_mentions WHERE provider LIKE 'searxng%' GROUP BY 1,2;

# 2.3 Copy ke container runtime + syntax check di dalam container
ssh root@130.254.47.93 'docker cp /opt/seo-pipeline/app/jobs/geo-searxng.js igsbaxpsvuhopghoutiit2kk-085951037002:/srv/jobs/geo-searxng.js && docker exec igsbaxpsvuhopghoutiit2kk-085951037002 node --check /srv/jobs/geo-searxng.js'

# 2.4 Smoke test 100 query (delay 2–3,5 dtk/query ≈ 4–6 menit; jalan-kan dengan nohup/background)
ssh root@130.254.47.93 'docker exec -e SEARXNG_URL=http://searxng:8080/search igsbaxpsvuhopghoutiit2kk-085951037002 node /srv/jobs/geo-searxng.js --max=100 --no-notify'
# VALIDASI WAJIB (bukti, bukan asumsi): jumlah baris baru = 2 × jumlah query (dua domain),
# provider berpasangan `searxng:beriklan.co.id` & `searxng:beriklan.my`, status ∈ present|absent|unknown,
# dan metrik kedua domain TIDAK saling menimpa.

# 2.5 Cron sementara di HOST (karena runner.js yang sudah di-patch baru aktif setelah app Coolify di-rebuild/restart
#     — DAN ITU BUTUH IZIN USER, jangan restart sendiri). Tambahkan 1 baris ke crontab root:
#     40 3 * * * docker exec -e SEARXNG_URL=http://searxng:8080/search igsbaxpsvuhopghoutiit2kk-085951037002 node /srv/jobs/geo-searxng.js --max=120 >> /var/log/geo-searxng.log 2>&1
#     (cek dulu `crontab -l` — JANGAN menimpa, hanya append; simpan salinan crontab lama sebelum edit)
```
Konteks VPS yang sudah diverifikasi (jangan pakai asumsi lama di dokumen lain):
- `/opt/migration/seo-pipeline` **TIDAK ADA**. Direktori nyata: `/opt/seo-pipeline` (compose project-nya **Exited**, `seo-pipeline-app-1` mati dengan code 137 = OOM).
- Runtime LIVE = container Coolify `igsbaxpsvuhopghoutiit2kk-085951037002` (wd `/srv`, `node server.js`, node v20.20.2, cap 256 MB, network `coolify`). Ada duplikat legacy `awesome_goldwasser` (restart=no) yang menjalankan cron yang sama.
- PG LIVE = container `vonbh1dpbrfzlrm26lwvdain` (db/user/password `seopipe`), skema `coid` / `comy` / `shared`.
- `runner.js` VPS sudah di-patch aditif (backup `/opt/seo-pipeline/app/jobs/runner.js.bak-t54-20260930-003731`): import L7, cabang `runOnce` L18, `cron.schedule('40 3 * * *', … maxQueries:120)` L30. `node --check` OK. Catatan kecil: string error `unknown_job` masih menyebut 4 job lama.
- `geo-monitor.js` yang ada selalu log "skipped (no API key)" → **0 data GEO**, itu sebabnya probe keyless SearXNG dibuat.
- RAM: total 3.915 MB, **available ±1.989 MB** (angka 404 MB di plan sudah usang). Disk bebas 119 G, 2 CPU.

---

## 3. Pencatatan T5 di tracker + LOG (WAJIB sebelum mulai T6)

Belum dilakukan. Isi yang harus ditulis (bahan sudah ada di §1 dan §2):

**`DOCS-SEO-2026-09-24/TASKTRACKER-COID.md`** — tandai §T5:
- **T5.1 AI crawler tracker** ✅ LIVE `a2ddc246`: guard di fetch (regex `AI_BOT_RE`, dikecualikan jalur fetch `/api/*` dll), 1 baris per `(bot, day, slug)` via dedupe, non-blocking (`ctx.waitUntil`); DDL `ai_crawler_log` + 2 index di array `handleAdminMigrate` **tanpa** bump `MIGRATION_VERSION` (bump = re-run UPDATE LIKE ≈745k reads → D1 lock); endpoint `GET /api/admin/ai-crawlers?token=&days=14&format=csv` (401 tanpa token; 200+catatan bila tabel belum ada); kartu `aiCrawlerCard` di dashboard + `stats.ai_crawlers`; baris "Crawler AI 7 hari" di email health 00:00 UTC. Bukti: UA GPTBot/Claude-Web/PerplexityBot → 3 baris, request ulang ter-dedupe (0 baris baru), Googlebot & Chrome TIDAK tercatat.
- **T5.2 llms.txt / llms-full.txt** ✅: blok `### <Industri>` dari `_llmsIndustryBlock(env)` (satu query OR `title LIKE ? OR slug LIKE ?` + memo 6 jam per isolate, karena `posts_meta` 16.848 baris dan LIKE = full scan); `**Last-Updated:**`; link `sitemap-blog.xml` + `news.xml`; llms-full 100→**300** artikel + guard `body.length > 920000`. Industri tanpa artikel terbit → teks jujur "_Panduan untuk industri ini sedang kami susun — belum ada artikel terbit._" (wave-1 belum terbit di `posts_meta`). Bukti: llms.txt 27.825 B berisi `### Kontraktor & Jasa Bangunan`; llms-full 137.857 B / 300 `URL:`.
- **T5.3 Schema entitas** ✅ TANPA menyentuh `Layout.astro`: `ARTICLE_SERVICE_ENTITY` (11 layanan) + `_articleEntities(meta)` → Article `about` (Service `@id` + City `containedInPlace`) & `mentions` (ItemList tags+category); `sameAs` 4 URL sosial nyata (IG/FB/LinkedIn/TikTok) + telepon asli `+62811919328` di `_fallbackPrefix` **dan** `_injectPageExtras`. Penting: shell HTML live berasal dari `_getBlogTpl` (ASSETS), `_fallbackPrefix` hanya dipakai bila ASSETS gagal — karena itu perbaikan harus di `_injectPageExtras` (call-site satu-satunya ±L16035). Bukti: halaman artikel `x-source: d1` → 8 blok JSON-LD terparse, telepon benar, Organization `sameAs` baru, Article `about`/`mentions` ada.
- **T5.4** ✅/⏳ sesuai hasil §2.

**`DOCS-SEO-2026-09-24/LOG-EKSEKUSI-PLAN.md`** — tambahkan segmen §T5 dengan: versi live baru + rollback id, metode uji (ekstraksi sumber → unit test di `/tmp/t5/*.mjs`), semua deviasi jujur (lihat §7), dan bug yang ditemukan sendiri lewat bukti (smoke test klaim `stored: 6` padahal PG 3 baris → bug provider/domain).

Jangan lupa update kotak status di `README.md` (urutan baca) bila ada item baru.

---

## 4. T6 — Freshness at scale (BELUM DISENTUH sama sekali)

Mulai dari `EXECUTION-COID-FOR-AGENT.md` §T6 (baca verbatim dulu, jangan dari ingatan). Yang sudah diketahui sebagai prasyarat:
1. Sumber fakta umur artikel = `posts_meta.iso_date` (index `idx_posts_meta_iso` tersedia) dan `generated_drafts`.
2. Generator artikel saat ini **tidak** menulis `updated`/`lastmod` yang naik — cek dulu apakah `freshness` yang dilaporkan tracker (T1.3 `growth_log`, `snippet-optimize`) sudah cukup atau perlu job refresh terpisah.
3. Jangan menambah slot cron baru — satu-satunya slot CF `0 * * * *` tetap utuh; pola proyek: time-gate di dalam `handleCron` (`h === N` / `m % K === 0`), seperti winner-engine di `h === 10`.
4. Pertahankan anggaran D1: 5M reads/hari share account-wide — setiap query baru wajib pakai index atau dibatasi `LIMIT` + memo.

---

## 5. T7 — Fase 5 (gerbang Q4) + Fase 8 monitoring

Setelah T6. Gerbangnya berbasis data observasi (§6) — jangan dipaksakan lewat tanggal.

---

## 6. GERBANG OBSERVASI (bukan kerja, tinggal cek pada tanggalnya)

| Gerbang | Cek | Sejak / Kapan |
|---|---|---|
| Cap harian 1.16 | `grep` nilai cap di `worker-entry.js` + bandingkan publish/hari | 3 Okt |
| 20 slug terindex | `GET /api/cron/index-verify?token=…&count=20` → hitung `indexed` | 2 Okt |
| Growth 7 hari | `SELECT * FROM growth_log ORDER BY day DESC LIMIT 40` | 6 Okt |
| Winner cron jalan | baris `cron_runs` `name='winner-engine'` per hari sejak 30 Sep | 1 Okt |
| T5.4 GEO | `shared.geo_mentions` `provider LIKE 'searxng:%'` bertambah tiap hari | +3 hari setelah §2 selesai |

---

## 7. TEMUAN YANG MENUNGGU KEPUTUSAN USER (jangan dieksekusi sendiri — SOP #4)

1. **Telepon placeholder masih live di halaman statis.** `/`, `/jasa-iklan-*/`, `/blog/` masih menampilkan `+62-22-XXXXXXX` karena sumbernya `src/layouts/Layout.astro:119` (repo ROOT = stale) yang ter-bake ke `web/dist`. Perbaikan = edit `.astro` (file tampilan → SOP #1) + `npm run build` + deploy aset. **Butuh izin eksplisit.**
2. **Quality gate T4 lulus 0/60** di ambang §7 (1/60 @700 kata). Penghambat: `word_count` 60 baris, `dup_title` 96 pasangan (jaccard judul ≥0.8), `answer_block` 31, `banned_words` 3 ("pasti"). `--apply` **tidak** dijalankan (akan membekukan pipeline publish). Perlu keputusan ambang.
3. **3.015 baris `keyword LIKE '%sepi viewers%'`** (10 di prio 95 = paling atas buffer tiap service) — bukan intent klien; demote/block = menyentuh sistem berjalan.
4. **Dua instance pipeline hidup bersamaan** (`igsbaxpsvuhopghoutiit2kk-…` + legacy `awesome_goldwasser`) → baris `news-ping`/`distribute` dobel. `seo-pipeline-app-1` Exited 137 (OOM, restart=no). Perlu keputusan: cleanup container legacy / naikkan RAM.
5. **Wave-1 tidak ter-mirror ke PG**: `coid.keyword_queue WHERE source='industry-wave1'` = 0 (padahal D1 = 49). Cek arah dual-write untuk sumber baru.
6. **In-app cron `geo-searxng` belum aktif** sampai app Coolify di-rebuild/restart (restart = menyentuh sistem berjalan → izin user). Sementara pakai host-cron §2.5.

---

## 8. Resep deploy worker (jangan pakai varian lain)

```bash
cd <root>/web
set -a; . ../.env.admin; set +a
# 1) catat versi sebelum deploy (rollback target)
npx wrangler deployments list --script beriklanweb | head -5
# 2) verifikasi file (control byte + syntax) seperti §0
# 3) dry-run
npx wrangler deploy --dry-run
# 4) deploy HANYA bila dry-run bersih
npx wrangler deploy
# 5) health runbook (loop `curl -sI`, JANGAN pakai nama variabel `$path` — reserved zsh)
# 6) simpan version_id baru di tracker
# GAGAL di mana pun = STOP. Produksi rusak = `npx wrangler rollback <version-id>` seketika.
```
Catatan aset desync (gejala: `/` & static 404 tapi `/blog/<slug>/` & `/api/*` 200) → fix: `cd web && npx wrangler deploy` (re-sync manifest), lihat `DEPLOY_OPERATIONS.md`.

---

## 9. TL;DR untuk agent berikutnya

1. Verifikasi copy selesai (§0). 2. Selesaikan T5.4 (§2). 3. Catat T5 di tracker + LOG (§3). 4. T6 (§4) → T7 (§5). 5. Cek gerbang observasi sesuai tanggal (§6). 6. Hal-hal di §7 **jangan** dikerjakan tanpa persetujuan user. Produksi sekarang sehat di `a2ddc246`; rollback aman ke `f7d53c28`.
