# plan.my.md — Rencana Implementasi beriklan.my

> ## ⏸️ DITUNDA — JANGAN DIEKSEKUSI SEKARANG (keputusan user, 24 Sep 2026)
> **`beriklan.co.id` dikerjakan lebih dulu sampai selesai dan terbukti *running well*.**
> Semua task `.my` berstatus DEFERRED di `TASKTRACKER-SEO-MASTER.md`. Dokumen ini **bahan baca/review saja**:
> dilarang menjalankan perintah di dalamnya (D1, secret, cron, deploy, edit worker) sampai user membuka
> fase `.my` secara eksplisit. Gerbang pembukanya ada di tracker §URUTAN EKSEKUSI butir 5.
>
> **Pengecualian yang sudah selesai:** backup D1 `.my` (tracker 0.2 ✅) — itu pengaman, bukan perubahan live.
> **Kalau ada masalah mendesak di `.my`** (kuota/error/situs down): catat di tracker, lapor user, tunggu izin.

> **Acuan bukti:** `SEO-AUDIT-2026-09-24.md` (§2.2, §3.1, §5.2, §6.4, **§6.6 pipeline `.my`**, §9.5, §10, §13.2, §13.3).
> **Tracker eksekusi:** `TASKTRACKER-SEO-MASTER.md`.
> **Cakupan:** backend/SEO/infrastruktur `beriklan.my`. **BUKAN** perubahan visual.
> **Repo lokal:** `/Volumes/macmini/Desktop/beriklan.my` (terpisah dari repo co.id).
> **Koreksi 24 Sep:** setting publish `.my` bernama **`daily_publish_limit`** (nilai `40`, di kolom `cron`) —
> **bukan** `publish_daily_limit` seperti co.id. Detail + bukti: §1.7 dan audit §6.6.

---

## A. Perbedaan mendasar .my vs co.id (baca sebelum eksekusi)

| Aspek | co.id | .my | Konsekuensi |
|---|---|---|---|
| Bahasa konten | Indonesia | **Inggris** (`Layout.astro:50` → `lang="en"`) | riset keyword `hl=en&gl=my`; jangan terjemahkan pola co.id |
| URL blog live | **16.872** | **1.337** | static-first layak secara jumlah file |
| Data tersedia | `posts.json` 34,7 MB | `posts.json` **6.060 entri / 32,5 MB** | ~4.723 entri belum pernah jadi URL |
| `run_worker_first` | `["/*"]` | **20 path eksplisit** | route/halaman baru **wajib** didaftarkan, jika tidak worker di-bypass |
| `triggers` cron | 2 cron di jsonc | **tidak ada** di jsonc (dipasang manual via API) | setelah tiap deploy: PUT `[{"cron":"0 * * * *"}]` |
| `GSC_SITE_URL` | secret salah (`www`) | **tidak ada secret** → default kode `sc-domain:beriklan.my` (benar) | jangan "memperbaiki" yang sudah benar |
| `INDEXNOW_KEY` | default benar | **tidak ada** → fallback ke key co.id (bug) | set secret |
| Groq fallback AI | 3 key | **tidak ada** | tambahkan ≥1 key agar tidak single-point pada Zen |
| Email marketing | aktif (Resend 100/hari) | **dimatikan** (belum ada list) | jangan mengaktifkan tanpa permintaan user |
| Bucket R2 | `idberiklan` | `myberiklan` (binding `QUEUE`) | siap pakai |
| Proyek Pages | `beriklanweb` (aktif) | `beriklanmy` (dibuat, **custom domain belum attach**) | deploy uji `bd213542.beriklanmy.pages.dev` |
| Aset terkuat | subdomain `id.beriklan.co.id` (74 klik) | **`/tiktok-live-viewers/`** (impressions tertinggi) | gandakan pola "tool gratis + artikel pendukung" |
| Nomor WhatsApp | `wa.me/62811919328` | **sama, 14.543×** (nomor Indonesia di domain MY) | konfirmasi ke user sebelum diubah |

**Aturan main §A di `plan.co.id.md` berlaku penuh di sini** (no deploy tanpa izin, build gagal = STOP,
no DELETE sebelum Fase 4, backup `.bak-<ts>`, catat `version_id`, rollback bukan fix-forward,
jangan tambah cron ke jsonc, `EXPLAIN QUERY PLAN` wajib SEARCH, placeholder untuk rahasia).

---

## B. FASE 0 — Stabilisasi & pengaman

### 0.1 Backup D1 .my
```bash
cd /Volumes/macmini/Desktop/beriklan.my/web
ts=$(date +%Y%m%d)
mkdir -p ../backup
npx wrangler d1 export beriklan-my-seo --remote --output "../backup/beriklan-my-seo-$ts.sql"
ls -lh "../backup/beriklan-my-seo-$ts.sql" && grep -c 'INSERT INTO' "../backup/beriklan-my-seo-$ts.sql"
```

### 0.2 Baseline yang dijaga
```bash
cd /Volumes/macmini/Desktop/beriklan.my/web
for q in "SELECT COUNT(*) FROM posts_meta" "SELECT COUNT(*) FROM posts_content" \
         "SELECT status, COUNT(*) FROM keyword_queue GROUP BY status"; do
  npx wrangler d1 execute beriklan-my-seo --remote --command "$q"
done
curl -s https://beriklan.my/sitemap-blog.xml | grep -c '<loc>'      # baseline 1.337
python3 -c "import json;print(len(json.load(open('src/data/posts.json'))))"   # baseline 6.060
```

### 0.3 Perbaiki rsync repo ke VPS (prasyarat mutlak)
Kondisi: `/opt/migration/repo-my/web/src/pages` = **0 file** → build .my di VPS menghasilkan 0 halaman blog.
```bash
cd /Volumes/macmini/Desktop/beriklan.my
rsync -avz --partial --progress \
  --exclude 'node_modules' --exclude 'dist' --exclude '.astro' --exclude '.git' --exclude 'backup' \
  web/ root@130.254.47.93:/opt/migration/repo-my/web/
ssh root@130.254.47.93 'cd /opt/migration/repo-my/web && \
  echo "src_files=$(find src -type f | wc -l)" && \
  echo "pages_files=$(find src/pages -type f | wc -l)" && \
  ls src/pages/blog/ && wc -c src/worker-entry.js'
```
**Exit:** `pages_files` > 50, `src/pages/blog/[slug].astro` ada, `worker-entry.js` ±809.512 B.
> `--delete` **sengaja tidak dipakai** di .my sampai isi VPS dipastikan bukan satu-satunya salinan.

### 0.4 Buktikan build .my di VPS
```bash
ssh root@130.254.47.93 'cd /opt/migration/repo-my/web && rm -rf dist node_modules/.vite .astro && \
  npm ci && npm run build 2>&1 | tail -25 && \
  echo "blog_dirs=$(find dist/blog -maxdepth 1 -type d | wc -l)" && du -sh dist && \
  find dist -type f | wc -l'
```
**Exit:** build sukses, `blog_dirs` ≈ 1.337 (atau lebih bila Fase 1.5 sudah dijalankan),
total file **jauh di bawah 20.000**.

### 0.5 Rapikan rahasia .my
```bash
cd /Volumes/macmini/Desktop/beriklan.my/web
printf '%s' "$ADMIN_TOKEN_MY_BARU"   | npx wrangler secret put ADMIN_TOKEN
printf '%s' "$INDEXNOW_KEY_MY"       | npx wrangler secret put INDEXNOW_KEY
printf '%s' "$GROQ_API_KEY"          | npx wrangler secret put GROQ_API_KEY
npx wrangler secret list
```
- `INDEXNOW_KEY_MY` = `2f22c16be9437a90ad2285a4af043e10` (nama file key yang **sudah** dilayani di root .my).
- Setelah `ADMIN_TOKEN` jadi secret, hapus `"ADMIN_TOKEN"` dari `vars` di `wrangler.jsonc`
  **dan** ganti token hardcoded di `src/worker-entry.js:696`.
- Jangan menulis nilai secret ke dokumen/repo.

---

## C. FASE 1 — Quick wins .my (1× deploy, risiko rendah)

### 1.1 Fix IndexNow (bug paling berdampak untuk indexasi .my)
Bukti: `src/worker-entry.js` **13124** dan **13174** memakai fallback key co.id karena `INDEXNOW_KEY` tidak ada.
```bash
cd /Volumes/macmini/Desktop/beriklan.my/web
grep -n "INDEXNOW_KEY" src/worker-entry.js
```
Ubah fallback menjadi **gagal terang-terangan**, bukan diam-diam pakai key domain lain:
```js
const key = env.INDEXNOW_KEY;
if (!key) return { submitted: 0, error: "INDEXNOW_KEY not set" };
```
Lalu set secret (§B.0.5) dan uji:
```bash
curl -s "https://beriklan.my/api/cron/indexnow?token=$ADMIN_TOKEN&count=5" | head -c 400
```
**Exit:** respons tidak lagi merujuk key co.id; `submitted > 0`.

### 1.2 Fix normalisasi nomor WhatsApp Malaysia
`normalizePhoneForWa` di **baris 14231** memakai logika prefix `62` (Indonesia).

**Penting — bedakan dua hal (keputusan user 24 Sep 2026):**
- **Nomor CTA situs** (`wa.me/62811919328`, 14.543×) → **TETAP**, jangan diganti. Satu pintu untuk semua pasar.
- **Nomor milik pengunjung/lead** yang dinormalisasi fungsi ini (mis. dari form, data scrape, link WA per-kontak)
  → **harus** dinormalisasi ke prefix Malaysia `60`, sebab nomor `0123456789` milik orang Malaysia
  tidak akan tersambung bila ditulis `62…`.

```bash
grep -n "normalizePhoneForWa" -A 25 src/worker-entry.js | sed -n '1,40p'
```
Aturan yang benar untuk .my:
- `0123456789` → `60123456789`
- `+60123456789` / `60123456789` → `60123456789`
- nomor yang sudah berawalan `62` **jangan** diubah otomatis — biarkan apa adanya (konsisten dengan
  keputusan CTA satu pintu).
Uji unit cepat sebelum deploy:
```bash
node -e 'const s=require("fs").readFileSync("src/worker-entry.js","utf8");
const m=s.match(/function normalizePhoneForWa[\s\S]{0,600}/); console.log(m[0]);'
```

### 1.3 Nomor CTA .my — ✅ DIPUTUSKAN (24 Sep 2026): TETAP nomor Indonesia
Temuan audit: `wa.me/62811919328` muncul **14.543 kali** di `web/src`.

**Keputusan user:** memang satu pintu untuk semua pasar → **tidak ada tindakan**, dan
**dilarang** melakukan penggantian massal. Item ini ditutup.

Yang tetap berlaku hanya §C.1.2 (normalisasi nomor milik *pengunjung*, bukan nomor CTA).
Bila di kemudian hari user mengubah keputusan, prosedur penggantiannya:
```bash
cd /Volumes/macmini/Desktop/beriklan.my
grep -rl "62811919328" web/src | wc -l          # hitung file terdampak
# ganti bertahap per-direktori, verifikasi build setelah tiap langkah, BUKAN sed buta seluruh repo
```

### 1.4 Perbaiki `sitemap-tag.xml` yang kosong
Fakta: `https://beriklan.my/sitemap-tag.xml` = **111 B / 0 URL**, padahal `src/pages/blog/tag/` ada.
```bash
ls src/pages/blog/tag/
grep -rn "sitemap-tag" src/ astro.config.mjs | head
```
Kemungkinan penyebab: route tag tidak punya `getStaticPaths` yang menghasilkan entri, atau nama file
route tidak cocok dengan URL yang di-deklarasikan di `sitemap.xml`. Perbaiki sumber datanya
(tag harus diambil dari korpus `posts.json`), bukan dengan menambal XML-nya.

### 1.5 Naikkan `news.xml` .my bila perlu
`.my` sudah mengirim **1.000 URL** di `news.xml` — lebih sehat dari co.id.
Yang harus dipastikan: semua URL itu terbit < 48 jam. Bila tidak, Google News akan mengabaikannya.
```bash
curl -s https://beriklan.my/news.xml | grep -o '<publication_date>[^<]*' | sort -r | head -5
```

### 1.6 Manfaatkan 4.723 entri `posts.json` yang belum jadi URL
Ini konten yang **sudah ada**, bukan generate AI baru — tapi tetap tidak boleh dirilis sekaligus.
1. Saring dulu berdasarkan kualitas: `content` ≥ 1.500 karakter, punya `title` dan `iso_date`.
2. Hitung berapa yang lolos saringan; laporkan ke user sebelum menaikkan jumlah URL live.
3. Rilis bertahap lewat sitemap + IndexNow, maksimal **±300 URL/baris waktu** agar tidak menyerupai spike.
4. Perhatikan cap Pages: 1.337 + 4.723 = ~6.060 halaman blog → masih aman terhadap cap 20.000 file,
   **tetapi** `find dist -type f | wc -l` wajib dicek ulang setelah build (§B.0.4).

### 1.7 Turunkan laju publish .my (40/hari → 10–15/hari)

**⚠️ Nama setting `.my` BERBEDA dari co.id** — jangan pakai nama co.id.

| Domain | Nama row di `cron_settings` | Nilai | Kolom |
|---|---|---|---|
| co.id | `publish_daily_limit` | `600` | `cron` |
| co.id | `publish_batch_size` | `25` | `cron` |
| **.my** | **`daily_publish_limit`** | **`40`** | **`cron`** |
| .my | *(tidak ada setting batch)* | `min(50, sisa)` | di kode |

Mekanisme `.my` (terverifikasi 24 Sep):
```
lokal : scripts/gen_articles.py + article_render.py + pack_llm_drafts.py
        → drafts_patched/queue_00000.ndjson (19 MB, written: 3.295, 1 shard)
R2    : publish-queue/queue_NNNNN.ndjson (binding QUEUE, worker baris 1777/1818/1906/1921)
worker: refill buffer → generated_drafts (status='draft'), cursor queue_cursor={"shard":0,"line":1971}
worker: cron sync-posts → dailyLimit = cron_settings.daily_publish_limit (default kode 50, baris 2023)
        batchSize = Math.min(50, dailyLimit - publishedToday)
        publish dari generated_drafts WHERE status='draft' ORDER BY id ASC LIMIT batchSize
```
Kondisi nyata (bukti run `2026-09-24 12:00:08`):
```json
{"ok":true,"message":"No drafts to publish (limit reached or all published)",
 "total_drafts":993,"published_today":40,"daily_limit":40,"batch_size":0,
 "buffer_refilled":0,"buffer_count":993}
```
`generated_drafts`: committed **1.337** (= `posts_meta`), draft **993** (buffer), pending **63.007**.
Publish stabil **40/hari** 8 hari berturut-turut (17–24 Sep) → pipeline sehat, hanya keran-nya besar.

**Perintah (butuh persetujuan user — mengubah perilaku live):**
```bash
cd /Volumes/macmini/Desktop/beriklan.my/web
npx wrangler d1 execute beriklan-my-seo --remote --command \
 "SELECT name, cron FROM cron_settings WHERE name='daily_publish_limit';"          # bukti: 40
npx wrangler d1 execute beriklan-my-seo --remote --command \
 "UPDATE cron_settings SET cron='15' WHERE name='daily_publish_limit';"            # keran 15/hari
```
Samakan default kode agar tidak balik ke 50 saat row hilang (baris **2023**: `let dailyLimit = 50;` → `15`).
Tidak perlu menyentuh batch — `Math.min(50, sisa)` otomatis menyesuaikan.

**Runway antrian (penting untuk perencanaan generasi lokal):**
sisa shard ≈ 3.295 − 1.971 = **1.324** + buffer **993** = **±2.317 draft**.
- pada 40/hari → habis ±**58 hari**
- pada 15/hari → habis ±**154 hari**

Artinya `.my` **tidak** butuh generasi baru dalam waktu dekat; turunkan keran dulu, lalu jadwalkan
`build_publish_queue.py`/`pack_llm_drafts.py` lokal menjelang runway habis (tracking: tracker item 1.16).

**Keputusan terbuka (tanya user):** `cron_settings.trending-generate` di `.my` masih **`enabled=1`**
("Generate trending tiap 6 jam") padahal co.id sudah dimatikan. Ini satu-satunya jalur generate AI
yang masih hidup di produksi `.my`. Opsi: (a) biarkan, (b) pause supaya semua konten lewat jalur
queue lokal yang ter-QC seperti co.id. Jangan diubah tanpa jawaban user.

**Verifikasi:**
```bash
npx wrangler d1 execute beriklan-my-seo --remote --command \
 "SELECT started_at, substr(output,1,140) FROM cron_runs WHERE cron_name='sync-posts' ORDER BY id DESC LIMIT 3;"
npx wrangler d1 execute beriklan-my-seo --remote --command \
 "SELECT date(iso_date) d, COUNT(*) n FROM posts_meta WHERE iso_date>='2026-09-24' GROUP BY d ORDER BY d DESC;"
```
**Exit:** `daily_limit: 15` di output sync-posts · terbit ≤15/hari · `queue_cursor` maju normal · 0 duplikat.

### 1.8 Deploy & verifikasi Fase 1 .my
```bash
cd /Volumes/macmini/Desktop/beriklan.my/web
npm run build && npx wrangler deploy
# WAJIB setelah deploy: cron .my tidak ada di jsonc → pasang manual
curl -s -X PUT "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/workers/scripts/beriklanmy/schedules" \
  -H "Authorization: Bearer $CF_API_TOKEN" -H 'Content-Type: application/json' \
  -d '[{"cron":"0 * * * *"}]'
```
Verifikasi:
```bash
curl -s -o /dev/null -w "home %{http_code}\n" https://beriklan.my/
curl -s -o /dev/null -w "blog %{http_code}\n" https://beriklan.my/blog/
curl -s -o /dev/null -w "tool %{http_code}\n" https://beriklan.my/tiktok-live-viewers/
curl -s https://beriklan.my/sitemap-blog.xml | grep -c '<loc>'
curl -s https://beriklan.my/sitemap-tag.xml | grep -c '<loc>'
curl -s -D - -o /dev/null "https://beriklan.my/data/posts-index.json" | grep -i x-cache
npx wrangler d1 insights beriklan-my-seo --time-period 1h --sort-by reads --limit 5 --json
```
**Exit Criteria Fase 1 .my:**
- [ ] IndexNow memakai key .my, `submitted > 0`
- [ ] `normalizePhoneForWa` menghasilkan prefix `60` untuk nomor lokal MY
- [ ] `sitemap-tag.xml` > 0 URL
- [ ] cron .my terpasang kembali (`GET .../schedules` menampilkan `0 * * * *`)
- [ ] publish ≤ 15/hari
- [ ] 1.337 URL blog tetap 200 (tidak ada yang hilang)
- [ ] 0 error 500 baru di runtime log

---

## D. FASE 2 — Postgres VPS untuk .my

Skema **identik** dengan `plan.co.id.md` §D.2.1, tetapi di database `.my` pada instance Postgres yang sama
(pisahkan lewat nama database atau skema, jangan campur baris co.id dan .my).

```bash
ssh root@130.254.47.93 'docker exec -i <POSTGRES_CONTAINER> psql -U <PG_USER> -d <PG_DB_MY>' < sql/001_schema.sql
```
Tambahkan kolom penanda pasar bila memakai satu database bersama:
```sql
ALTER TABLE posts_meta ADD COLUMN IF NOT EXISTS market TEXT NOT NULL DEFAULT 'my';
```

Backfill memakai pola keyset yang sama (`plan.co.id.md` §D.2.2) dengan perintah
`npx wrangler d1 execute beriklan-my-seo --remote --json`.

**Exit Criteria Fase 2 .my:**
- [ ] `posts_meta` Postgres == D1 .my
- [ ] `posts_content` Postgres == D1 .my
- [ ] sampling 20 slug: konten identik
- [ ] tidak ada baris D1 .my yang dihapus/diubah

---

## E. FASE 3 — Jalur serve .my: hybrid (statis untuk halaman inti, R2-first untuk blog)

### E.1 Kenapa hybrid, bukan full-static
| Opsi | Kelebihan | Masalah |
|---|---|---|
| Full static (semua 6.060 halaman di `dist`) | termurah, tercepat, tanpa D1 | setiap artikel baru butuh **rebuild + redeploy**; publish 10–15/hari = 1 deploy/hari minimum |
| Full dynamic (R2/D1 untuk semua) | publish tanpa deploy | halaman marketing/tool ikut dinamis, padahal isinya stabil |
| **Hybrid (dipilih)** | halaman jasa/tool statis & cepat; blog dinamis dari R2 | butuh disiplin mendaftarkan path baru di `run_worker_first` |

### E.2 Layout R2 .my (bucket `myberiklan`, binding `QUEUE`)
```
blog/<slug>.json
manifest/posts.json
sitemap/blog-1.xml        # 1.337 URL muat dalam 1 file; chunk bila > 10.000
```

### E.3 Dual-read worker .my (pola sama dengan co.id §E.3.3)
```
USE_R2=0 → skip R2
R2.get(`blog/${slug}.json`) → render (X-Source: r2)
D1 posts_meta/posts_content → render (X-Source: d1)
static dist/                → serve
tidak ada di mana pun       → 404 JUJUR (bukan homepage)
```
```bash
cd /Volumes/macmini/Desktop/beriklan.my/web
grep -n "posts_content\|X-Source\|X-Cache" src/worker-entry.js | head -30
printf '1' | npx wrangler secret put USE_R2   # kill-switch siap pakai
```

### E.4 Disiplin `run_worker_first` (jebakan khusus .my)
Daftar saat ini = **20 path eksplisit**. `/blog/*` sudah termasuk, jadi artikel baru aman.
Yang **wajib ditambahkan manual**: halaman dinamis baru di luar `/blog/*`.
> Catatan keputusan user 24 Sep 2026: route baru di luar `/blog/*` **tidak boleh dibuat**
> (`INDUSTRY-EXPANSION.md` §5.3), jadi poin ini praktis tidak terpakai selama keputusan itu berlaku.
> Tetap dicatat karena kalau suatu saat ada izin route baru, melupakan langkah ini = worker di-bypass.
```bash
python3 - <<'PY'
import re
t=open('wrangler.jsonc').read()
m=re.search(r'"run_worker_first":\s*\[(.*?)\]', t, re.S)
items=[x.strip().strip('"') for x in m.group(1).split(',') if x.strip()]
print(len(items)); [print(' -',i) for i in items]
PY
```
Bila halaman dinamis baru tidak didaftarkan, asset statis yang menang → worker tidak pernah jalan →
enrichment/FAQ/schema dinamis tidak muncul (gejala yang sama seperti insiden co.id di ../AGENTS.md).

Pertimbangkan menyederhanakan menjadi `["/*"]` seperti co.id **hanya jika** user menyetujui perubahan
perilaku routing (ini mengubah jalur serve, bukan visual).

### E.5 Verifikasi Fase 3 .my
```bash
while read -r u; do
  printf "%s %s\n" "$(curl -s -o /dev/null -w '%{http_code}' "$u")" \
    "$(curl -s -D - -o /dev/null "$u" | grep -i x-source || echo '-')"
done < <(curl -s https://beriklan.my/sitemap-blog.xml | grep -o '<loc>[^<]*' | sed 's|<loc>||' | tail -50) \
  | sort | uniq -c
curl -s -o /dev/null -w "bogus %{http_code}\n" https://beriklan.my/blog/this-slug-does-not-exist-xyz/
```
**Exit:** 50/50 sampel = 200 dengan `X-Source: r2`; slug ngawur = 404; jumlah URL live ≥ 1.337.

---

## F. FASE 4 — Rampingkan D1 .my

Sama seperti `plan.co.id.md` §F: backup ulang → hitung 3-arah → **minta persetujuan user** →
hapus bertahap (backlog `pending_indexing` lebih dulu, `posts_content` paling akhir) →
jangan pernah `DROP TABLE`.

---

## G. FASE 5 — Ekspansi industri .my (pasar Malaysia, bahasa Inggris)

### G.1 Aturan wajib: validasi frasa sebelum seeding
Jangan menerjemahkan frasa Indonesia. Jalankan Suggest dengan `hl=en&gl=my` dan pakai **hanya** frasa
yang benar-benar muncul:
```bash
for q in "construction company malaysia" "contractor kl" "building materials supplier malaysia" \
         "hardware store malaysia" "garment manufacturer malaysia" "custom tshirt printing malaysia" \
         "property agent malaysia" "new launch property malaysia" "renovation contractor malaysia"; do
  curl -s "https://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=my&q=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$q")" \
    | python3 -c "import json,sys;d=json.load(sys.stdin);print(d[0],'->',len(d[1]));[print('   ',x) for x in d[1][:8]]"
  sleep 2
done
```
Istilah di atas adalah **hipotesis yang harus divalidasi**, bukan fakta hasil riset.
Contoh perbedaan yang sudah terbukti di pasar ID (audit §11.2): `toko bangunan` menang atas
`material bangunan`. Padanan MY kemungkinan `hardware store` / `building materials supplier` —
tetap harus dibuktikan oleh output perintah di atas sebelum dipakai.

### G.2 Urutan wave .my
1. **Construction / contractor** (padanan wave 1 co.id).
2. **Building materials / hardware**.
3. **Garment & textile** (konveksi/garmen).
4. **Property / housing**.
5. Wave tambahan hanya setelah wave sebelumnya menunjukkan impresi nyata di `sc-domain:beriklan.my`.

### G.3 Gandakan aset yang sudah terbukti
`/tiktok-live-viewers/` adalah halaman .my dengan impresi tertinggi. Pola yang layak digandakan:
**tool gratis + halaman pendukung + artikel cluster**. Kandidat tool berikutnya (sudah ada route-nya di
`src/pages/`): `live-stream-viewers`, `shopee-live-viewers`, `youtube-live-viewers`,
`twitch-live-viewers`, `instagram-live-viewers`, `ad-budget-calculator`, `roas-calculator`, `roi-calculator`.
Pastikan semuanya terdaftar di `run_worker_first` (saat ini 6 halaman viewers sudah masuk).

### G.4 Gerbang validasi
Wave berikutnya tidak dimulai sebelum wave aktif punya ≥ 1 URL dengan impressions > 100 di GSC .my.

---

## H. FASE 6 — GEO keyless untuk .my

Sama dengan `plan.co.id.md` §H (SearXNG self-hosted di VPS, ≤ 200 query/hari total **untuk kedua domain**,
jitter, cache, kegagalan = `unknown`). Perbedaan .my:
- `language=en-MY`, `gl=my`.
- 50 query dialokasikan untuk .my: 20 komersial EN, 20 industri wave aktif, 10 brand/tool.
- Simpan ke `geo_probes` dengan `domain='beriklan.my'`.
- `llms.txt` (28,8 KB) dan `llms-full.txt` (35,8 KB) .my sudah live → perbarui saat wave industri masuk.

---

## I. FASE 7 — Monitoring .my

1. **Setelah setiap deploy**: verifikasi cron terpasang (§C.1.8). Ini kegagalan paling sunyi di .my —
   jsonc tidak punya `triggers`, jadi deploy tanpa PUT schedules = semua job mati tanpa error.
2. Probe eksternal 5 menit: `/`, `/blog/`, `/tiktok-live-viewers/`, `/sitemap-blog.xml`, `/sitemap-tag.xml`.
3. Email kesehatan harian .my **tidak** diaktifkan (belum ada list) — jangan menyalakannya tanpa permintaan user.
4. Pantau `d1 insights beriklan-my-seo` mingguan; kuota D1 **dibagi per account** dengan co.id dan 5 DB lain.

---

## J. Runbook verifikasi .my (setelah setiap deploy)

```bash
for p in "" blog/ tiktok-live-viewers/ ad-budget-calculator/ sitemap.xml sitemap-blog.xml \
         sitemap-tag.xml news.xml llms.txt data/posts-index.json about-us; do
  curl -s -o /dev/null -w "%{http_code} /$p\n" "https://beriklan.my/$p"
done
curl -s -o /dev/null -w "bogus %{http_code}\n" https://beriklan.my/blog/this-slug-does-not-exist-xyz/
curl -s -D - -o /dev/null "https://beriklan.my/data/posts-index.json" | grep -i x-cache
curl -s -D - -o /dev/null "https://beriklan.my/data/posts-index.json" | grep -i x-cache
curl -s "https://beriklan.my/api/admin/email?token=$ADMIN_TOKEN&tab=overview" | head -c 200
cd /Volumes/macmini/Desktop/beriklan.my/web && npx wrangler d1 insights beriklan-my-seo \
  --time-period 1h --sort-by reads --limit 5 --json
# cron hidup?
curl -s "https://beriklan.my/api/cron/hourly?token=$ADMIN_TOKEN" | head -c 300
curl -s -H "Authorization: Bearer $CF_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/workers/scripts/beriklanmy/schedules"
```
Catatan: `/about-us` saat ini **307** — pastikan target redirect-nya memang kanonis yang diinginkan,
bukan redirect tak sengaja.

## K. Runbook rollback .my
```bash
cd /Volumes/macmini/Desktop/beriklan.my/web
npx wrangler deployments list | head -10
npx wrangler rollback <version-id>
printf '0' | npx wrangler secret put USE_R2
# setelah rollback: PUT schedules lagi (§C.1.8)
```

## L. Target terukur .my

| KPI | Baseline | 30 hari | 90 hari |
|---|---|---|---|
| Clicks 28 hari (`sc-domain:beriklan.my`) | 16 | > 30 | > 80 |
| Impressions 28 hari | 2.195 | > 3.500 | > 7.000 |
| URL blog live | 1.337 | ≥ 1.337 | ≥ 3.000 (dari 4.723 entri yang belum terpakai) |
| Publish/hari | **40 tepat** (`daily_publish_limit=40`) | 10–15 | 10–15 |
| `sitemap-tag.xml` | 0 URL | > 0 | > 0 |
| IndexNow submit | gagal (key salah) | sukses | sukses |
| Soft-404 | belum diukur penuh | 0 | 0 |
| Cron terpasang pasca-deploy | manual, rawan lupa | otomatis terverifikasi | otomatis terverifikasi |

## M. Definition of done (.my)

- [ ] Fase 0–4 selesai dengan bukti output di tracker
- [ ] Build Astro di VPS benar-benar menghasilkan halaman blog (bukan hasil rsync)
- [ ] IndexNow memakai key .my sendiri
- [ ] Nomor WhatsApp MY dinormalisasi ke `60`
- [x] Keputusan nomor CTA .my: **tetap `+62 811-919-328`** (satu pintu) — diputuskan user 24 Sep 2026, tidak ada penggantian massal
- [ ] `sitemap-tag.xml` berisi URL
- [ ] Blog dilayani R2-first dengan kill-switch dan 404 jujur
- [ ] `run_worker_first` mencakup semua halaman dinamis baru
- [ ] Cron .my terpasang setelah setiap deploy (terverifikasi via API)
- [ ] Wave 1 industri MY live dan terindex
- [ ] Tidak ada rahasia plaintext di repo/dokumen

<!--END-->

