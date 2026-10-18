# INDUSTRY-EXPANSION

> **Status eksekusi (24 Sep):** rencana ini untuk **`beriklan.co.id` dulu** (keputusan user — `.my` ditunda),
> dan **belum boleh dijalankan**: semua dokumen harus clear dulu + tunggu aba-aba user.
> Wave 1 baru mulai setelah Fase 0–1 co.id selesai dan cap publish 15/hari stabil ≥ 3 hari.
> Semua URL baru masuk lewat `/blog/*` (tidak ada route baru — keputusan #9)..md — Ekspansi Vertikal Industri (co.id + .my)

> **Acuan bukti:** `SEO-AUDIT-2026-09-24.md` §6 (antrian keyword), §11 (coverage industri).
> **Rencana induk:** `plan.co.id.md` Fase 5 · `plan.my.md` Fase 5 · tracker: `TASKTRACKER-SEO-MASTER.md`.
> **Bahasa konten:** co.id = Indonesia (pakem `../COPY-BIBLE.md`); .my = Inggris (`lang="en"`, pasar MY).

---

## 1. Inventaris bahan baku (dihitung langsung dari file, bukan perkiraan)

### 1.1 `web/src/data/industry-keywords.json` — **2.291 keyword, BELUM pernah di-import**
Field per item: `keyword, slug, industri, sub_niche, service, formula, intent, score, tier`

**Per industri (9):**
| industri | jumlah |
|---|---|
| kesehatan | 375 |
| fnB | 300 |
| fashion | 275 |
| manufaktur | 241 |
| properti | 225 |
| pendidikan | 225 |
| jasa_b2b | 225 |
| travel | 225 |
| otomotif | 200 |
| **total** | **2.291** |

**Per `service`:** jasa-iklan-facebook 701 · jasa-iklan-google 544 · jasa-iklan-instagram 443 ·
jasa-iklan-tiktok 365 · jasa-kelola-instagram 87 · jasa-pembuatan-landing-page 76 · jasa-pembuatan-website 75.

**Per `formula`:** studi-kasus 819 · tips 701 · cara-pasang 576 · panduan 181 · comparison 14.
**Per `tier`:** A 1.757 · S 534. **`score`:** min 68, maks 83, rata-rata 73,2 (hanya 69 item ≥ 80).

### 1.2 ⚠️ Tiga kelemahan dataset ini (harus dikoreksi sebelum dipakai)
| # | Masalah | Bukti | Tindakan |
|---|---|---|---|
| 1 | **`intent` = `informational` untuk 100% (2.291/2.291)** | hitung `intent` | artikel informasional tidak menghasilkan lead. Campur dengan keyword komersial/transaksional dari §1.3 dan hasil Suggest |
| 2 | **Cakupan 4 wave target sangat tipis** | kontraktor 9 · distributor bahan bangunan 23 · pabrik tekstil 43 · konveksi 9 · developer perumahan 43 = **127 keyword** (5,5% dataset) | wave 1–4 butuh ekspansi manual (Suggest + pola §4) |
| 3 | Frasa lemah ikut terbawa | dataset memakai `material`/`garmen`/`kain`/`benang` = **0 item**; yang ada `distributor bahan bangunan`, `pabrik tekstil` | gunakan frasa yang terbukti muncul di Suggest (§3), bukan frasa di file apa adanya |

### 1.3 `web/public/data/keyword-research-v2.json` — 583 keyword (sebagian sudah di-import)
Field: `keyword, service, city, intent, priority`. Per service: jasa-view-live 153 · jasa-pembuatan-website 149 ·
9 service × 33 · jasa-pembuatan-landing-page 17. Riwayat import: **359 inserted / 224 skipped** (dedupe).

### 1.4 `web/src/data/clusters.json` — 10 service × 5 cluster = **50 cluster, tidak terpakai**
Struktur: `{ "<service>": { "<ClusterName>": { title, desc, posts:[{slug,title,excerpt}] } } }`.
Service yang sudah punya cluster: jasa-digital-marketing, jasa-iklan-facebook/instagram/tiktok/google/youtube,
jasa-kelola-instagram/tiktok, jasa-pembuatan-website/landing-page.
**Belum ada cluster untuk 9 industri di §1.1** → harus dibuat (§5).

### 1.5 Antrian aktif co.id (D1) — 377.882 pending *(snapshot 24 Sep pagi; baseline terkunci 377.832, total 391.482 — antrian hidup sehingga bergeser tiap hari, lihat audit §6.2)*
Prioritas teratas saat ini adalah keyword bernilai rendah (`jasa viewers instagram aceh profesional`,
`digital marketing sepi viewers`) dengan `service` **kosong**. Antrian ini **bukan** sumber ekspansi industri;
ia harus di-re-skoring (§6) dan dipindah ke Postgres (`plan.co.id.md` Fase 2).

---

## 2. Keputusan urutan wave (sudah disetujui user)

| Wave | Vertikal | Frasa yang dipakai | Sumber keyword awal |
|---|---|---|---|
| **1** | Kontraktor | `kontraktor` (+ `kontraktor <kota>`, `jasa kontraktor`) | 9 (dataset) + ekspansi Suggest |
| **2** | Toko material/bangunan | **`toko bangunan`**, `bahan bangunan` — *bukan* `material bangunan` | 23 (dataset, sub_niche `distributor bahan bangunan`) + Suggest |
| **3** | Pabrik/tekstil | **`konveksi`**, `garmen`, `kain`, `benang`, `pabrik tekstil` — *bukan* `pabrik kain`/`supplier benang` | 43 + 9 (dataset) + Suggest |
| **4** | Perumahan | **`perumahan`**, `agen properti` — *bukan* `developer properti` | 43 (dataset, sub_niche `developer perumahan`) + 225 industri properti |
| 5+ | Lihat §3.3 | — | dataset 9 industri |

Aturan: **wave N+1 tidak dimulai sebelum wave N lolos gerbang §8.**

---

## 3. Riset demand — cara membuktikan frasa sebelum dipakai

### 3.1 co.id (Bahasa Indonesia)
```bash
probe() { # $1 = query
  curl -s "https://suggestqueries.google.com/complete/search?client=firefox&hl=id&gl=id&q=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$1")" \
  | python3 -c "import json,sys;d=json.load(sys.stdin);print(f'{d[0]:38s} → {len(d[1])}');[print('    ',x) for x in d[1][:10]]"
  sleep 2
}
for q in "jasa kontraktor" "kontraktor bandung" "iklan untuk kontraktor" "toko bangunan" \
         "bahan bangunan" "konveksi" "garmen" "kain" "benang" "perumahan" "agen properti"; do probe "$q"; done
```

### 3.2 .my (English, market Malaysia)
```bash
probeMY() {
  curl -s "https://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=my&q=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$1")" \
  | python3 -c "import json,sys;d=json.load(sys.stdin);print(f'{d[0]:44s} → {len(d[1])}');[print('    ',x) for x in d[1][:10]]"
  sleep 2
}
for q in "construction company malaysia" "contractor kl" "building materials supplier malaysia" \
         "hardware store malaysia" "garment manufacturer malaysia" "custom tshirt printing malaysia" \
         "property agent malaysia" "new launch property malaysia"; do probeMY "$q"; done
```
> Frasa .my di atas **hipotesis**. Hanya pakai yang benar-benar muncul di output.
> Pelajaran dari pasar ID: `toko bangunan` menang atas `material bangunan`, `perumahan` menang atas
> `developer properti`. Pola serupa sangat mungkin terjadi di MY (mis. `hardware store` vs `building material shop`).

### 3.3 Vertikal tambahan yang layak (dipetakan ke dataset yang SUDAH ada)
| Peluang | Sudah tersedia di `industry-keywords.json` |
|---|---|
| klinik / apotek / skincare | **kesehatan 375** |
| restoran / katering / frozen food | **fnB 300** |
| bengkel / spare part / showroom | **otomotif 200** |
| bimbel / kursus / sekolah | **pendidikan 225** |
| umroh / travel / hotel | **travel 225** |
| ekspedisi / cctv / solar panel / percetakan | **jasa_b2b 225** |
| furniture / tekstil / pabrik | **manufaktur 241** |
| toko hijab / distro / brand fashion | **fashion 275** |

Artinya: setelah wave 1–4, **2.291 keyword sudah terpetakan ke 9 industri** tanpa riset baru —
cukup dikoreksi intent-nya (§1.2 #1).

---

## 4. Cara memperbanyak keyword per wave (pola yang bisa di-generate)

Untuk tiap sub_niche (mis. `kontraktor`), bangun matriks:

| Pola | Template | Contoh | Nilai |
|---|---|---|---|
| Kota | `<frasa> <kota>` | `jasa kontraktor Surabaya` | tinggi (local intent) |
| Biaya | `biaya <frasa>` / `<frasa> harga` | `biaya promosi kontraktor` | tinggi |
| Studi kasus | `kisah sukses <sub_niche> dengan iklan digital` | sudah ada polanya di dataset (formula `studi-kasus`, 819 item) | sedang–tinggi |
| Cara | `cara <aksi> untuk <sub_niche>` | `cara mendapatkan proyek kontraktor dari Google Ads` | sedang |
| Perbandingan | `<channel A> vs <channel B> untuk <sub_niche>` | hanya 14 item `comparison` di dataset → **peluang** | tinggi (bottom-funnel) |
| Masalah | `kenapa iklan <sub_niche> tidak menghasilkan` | — | sedang |
| Kanal | `<sub_niche> + facebook/google/tiktok/instagram ads` | selaras distribusi `service` §1.1 | tinggi |

Aturan kualitas keyword sebelum masuk antrian:
1. Frasa **terbukti** muncul di Suggest, atau merupakan turunan mekanis (kota/biaya/kanal) dari frasa yang terbukti.
2. `intent` diisi jujur: `informational` / `commercial` / `transactional`. **Minimal 40% wave harus commercial/transactional.**
3. `service` **wajib terisi** (salah satu dari 10 service co.id) — keyword ber-`service` kosong tidak boleh publish.
4. `city` terisi bila pola kota; gunakan daftar kota yang sudah ada di `sitemap-city.xml` (385 URL co.id, 275 .my).
5. Dedupe by `keyword_normalized` (lowercase + trim + collapse spasi).

---

## 5. Arsitektur halaman & topical cluster

### 5.1 Pola yang sudah terbukti ada di repo
`clusters.json` memakai struktur **1 service → 5 cluster → N post**. Perluas pola yang sama ke industri:
```
industri (mis. kontraktor)
├── 1 pillar page        → /blog/panduan-digital-marketing-kontraktor/   (3.000+ kata)
├── 8–12 supporting      → /blog/<slug dari formula studi-kasus|cara|biaya|comparison>/
└── link ke halaman layanan yang SUDAH ADA → /jasa-digital-marketing/ atau /jasa-iklan-google/
    (dilarang membuat halaman `jasa-*` atau route baru apa pun — lihat §5.3)
```

### 5.2 Aturan internal link (wajib, karena ini yang belum ada di ±16,8 rb artikel lama — 16.872 URL live)
- Pillar → semua supporting (anchor deskriptif, bukan "klik di sini").
- Tiap supporting → pillar + minimal 2 supporting lain dalam cluster yang sama.
- Tiap supporting → 1 halaman service yang relevan (`service` di metadata keyword).
- Jangan membuat jaringan link yang hanya menunjuk ke artikel baru; sisipkan 1–2 link ke artikel lama
  yang se-topik agar otoritas mengalir dua arah.

### 5.3 ✅ DIPUTUSKAN (24 Sep 2026): TIDAK ada route baru di luar `/blog/*`
User menolak pembuatan halaman seperti `/industri/kontraktor/`. **Semua** konten wave 1–4 (dan seterusnya)
masuk sebagai **artikel blog** di jalur yang sudah ada.

Alasan teknis yang memperkuat keputusan ini:
- di .my setiap path dinamis baru harus ditambahkan manual ke `run_worker_first` (20 path eksplisit) —
  lupa satu = worker di-bypass dan halaman jatuh ke asset statis;
- di co.id menambah jumlah file Pages (`10.178 / 20.000` sudah terpakai);
- route baru biasanya menyeret perubahan navigasi = menyentuh visual (dilarang SOP).

Konsekuensi yang harus dipatuhi saat eksekusi:
1. Struktur cluster (§5.1) diwujudkan **sepenuhnya lewat slug + internal link**, bukan lewat direktori route baru.
2. "Pillar page" = artikel blog berslug jelas (mis. `/blog/panduan-digital-marketing-kontraktor/`),
   bukan halaman route khusus.
3. Link ke halaman layanan memakai 10 route `jasa-*` yang **sudah ada**; jangan membuat `jasa-*` baru
   tanpa izin terpisah (itu perubahan visual + navigasi).
4. Karena tidak ada hub route, keterkaitan industri dijaga lewat:
   - kategori/tag pada artikel (`sitemap-blog-tag.xml` co.id sudah ada; `sitemap-tag.xml` .my harus diperbaiki dulu — `plan.my.md` §C.1.4),
   - blok "Artikel terkait dalam cluster ini" di dalam konten artikel.

---

## 6. Pipeline import → antrian → publish

### 6.1 Tujuan import = **Postgres**, bukan D1
Antrian besar (377.882 baris) adalah penyebab beban D1 (`plan.co.id.md` §C.1.3, audit §8).
Import baru masuk ke Postgres `keyword_queue` setelah Fase 2 selesai.

### 6.2 Konversi `industry-keywords.json` → baris antrian
```bash
cd /Volumes/macmini/Desktop/beriklan.co.id/web/src/data
python3 - <<'PY'
import json, re, collections
d = json.load(open('industry-keywords.json'))
def norm(s): return re.sub(r'\s+', ' ', (s or '').strip().lower())
WAVE = {'kontraktor':1, 'distributor bahan bangunan':2, 'pabrik tekstil':3,
        'konveksi':3, 'developer perumahan':4}
out, seen = [], set()
for x in d:
    n = norm(x['keyword'])
    if n in seen or not x.get('service'):   # service kosong = tolak (aturan §4 #3)
        continue
    seen.add(n)
    out.append({
        "keyword": x['keyword'], "keyword_normalized": n, "slug": x['slug'],
        "service": x['service'], "city": "", "industri": x['industri'],
        "sub_niche": x['sub_niche'], "formula": x['formula'],
        "intent": "commercial" if x['formula'] in ('comparison','cara-pasang') else x['intent'],
        "tier": x['tier'], "score": x['score'],
        "wave": WAVE.get(x['sub_niche'], 0),          # 0 = wave 5+
        "priority": x['score'] + (20 if WAVE.get(x['sub_niche']) else 0),
    })
json.dump(out, open('/tmp/industry-queue.json','w'), ensure_ascii=False, indent=1)
print("total", len(out))
print("per wave", collections.Counter(o['wave'] for o in out))
print("per intent", collections.Counter(o['intent'] for o in out))
PY
```
Output `/tmp/industry-queue.json` lalu dimuat ke Postgres (`\copy` atau endpoint import yang sudah
diarahkan ke Postgres). **Jangan** memanggil `POST /api/admin/keywords/import` sebelum endpoint itu
menulis ke Postgres — kalau tidak, 2.291 baris akan membebani D1 lagi.

### 6.3 Re-skoring antrian lama (377.882 baris)
Skor baru = fungsi dari demand nyata, bukan dari kemudahan generate:
```
priority_baru =
    35 × (impression GSC untuk keyword/serupa, ternormalisasi 0–1)
  + 25 × (muncul di Google Suggest: 1/0)
  + 20 × (intent: transactional 1.0 / commercial 0.7 / informational 0.3)
  + 10 × (service terisi: 1/0)
  + 10 × (masuk cluster industri wave aktif: 1/0)
```
Baris dengan `service` kosong → status `blocked`, bukan `pending`. Ini langsung menyingkirkan
keyword sampah seperti `jasa viewers instagram aceh profesional` dari jalur publish.

---

## 7. Gerbang kualitas per artikel (semua wave, kedua domain)

Sebuah artikel **tidak boleh** publish bila:
1. Panjang konten < 1.200 kata (co.id) / < 900 kata (.my).
2. Tidak ada blok jawaban ringkas 40–60 kata di 100 kata pertama (yang paling sering dikutip mesin/LLM).
3. Tidak ada FAQ spesifik-query dengan heading yang persis sama dengan query (`growth-enrich` sudah
   memakai pola class `growth-faq` — ikuti, jangan buat pola kedua).
4. `service` kosong atau slug tidak cocok dengan `keyword_normalized`.
5. Internal link < 3.
6. Memakai kata terlarang `../COPY-BIBLE.md`: "bikin/gak/nggak", "pasti", "garansi 100%",
   "tanpa risiko", atau klaim sosial proof fiktif ("50+ klien aktif", "Rating 4.8/5", "ROAS 4.2x").
   Ganti dengan: terukur, transparan, teruji, berbasis data, 9 tahun mengelola campaign.
7. Schema `Article` tidak lengkap (`headline`, `datePublished`, `dateModified`, `author`).
8. Untuk .my: konten bukan Bahasa Inggris, atau nomor WhatsApp belum dinormalisasi ke `60`
   (`plan.my.md` §C.1.2).

Verifikasi otomatis sebelum publish (jalan di pipeline VPS):
```bash
ssh root@130.254.47.93 'cd /opt/migration/seo-pipeline && node scripts/quality-gate.mjs --domain coid --batch 15'
```
Script `quality-gate.mjs` harus menolak dan mencatat alasan ke `generated_drafts.status='rejected'`,
bukan diam-diam meloloskan.

---

## 8. Gerbang validasi wave & kriteria henti

### 8.1 Gerbang lanjut wave
Wave N dinyatakan berhasil dan wave N+1 boleh dimulai bila **dalam 45 hari** setelah artikel wave N terbit:
- ≥ 1 URL wave N dengan impressions > 100 di GSC, **atau**
- ≥ 3 klik dari URL wave N, **atau**
- ≥ 1 URL wave N masuk posisi ≤ 20 untuk keyword target.

Ukur dengan:
```bash
SA=/Volumes/macmini/Desktop/beriklan.co.id/cool-component-463913-b7-fa49902b181d.json
TOK=$(gcloud auth activate-service-account --key-file="$SA" && gcloud auth print-access-token)
curl -s -X POST "https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Aberiklan.co.id/searchAnalytics/query" \
  -H "Authorization: Bearer $TOK" -H 'Content-Type: application/json' \
  -d '{"startDate":"<TGL_AWAL>","endDate":"<TGL_AKHIR>","dimensions":["page"],"rowLimit":250}' \
  | python3 -c "import json,sys;d=json.load(sys.stdin);rows=d.get('rows',[]);
w=[r for r in rows if any(k in r['keys'][0] for k in ('kontraktor','bangunan','tekstil','konveksi','perumahan'))];
print(len(w),'URL wave terdeteksi');[print(r['keys'][0],r['impressions'],r['clicks']) for r in w[:15]]"
```

### 8.2 Kriteria henti (stop seluruh ekspansi)
- Soft-404 terdeteksi lagi (harus 0).
- D1 rows read > 3.000.000/hari atau muncul error 7500.
- Impressions domain turun > 20% selama 30 hari setelah wave dimulai (indikasi konten tipis menekan situs).
- Artikel baru menumpuk "unknown to Google" > 90% setelah 30 hari → hentikan publish, perbaiki indexasi dulu.

---

## 9. Matematika cadence (supaya tidak mengulangi spike 400/hari)

| Parameter | Nilai |
|---|---|
| Cap publish | **15/hari** (`publish_daily_limit=15`, `publish_batch_size=5`) |
| Kapasitas/bulan | ~450 artikel |
| Wave 1 (kontraktor) | 9 seed + ekspansi kota/kanal → target 60–90 artikel |
| Wave 2 (toko bangunan) | 23 seed + ekspansi → 80–120 artikel |
| Wave 3 (tekstil/konveksi) | 52 seed + ekspansi → 100–150 artikel |
| Wave 4 (perumahan/properti) | 225 seed industri properti → 150–225 artikel (dipilih by score) |
| Sisa 9 industri (§3.3) | 2.291 keyword → ±5 bulan pada cadence 15/hari |
| Kuota indexasi | GSC Indexing API 200/hari; IndexNow terbatas → 15 URL/hari **sangat** aman |

Kesimpulan: dengan cap 15/hari, seluruh dataset industri habis dalam ±5 bulan **tanpa** perlu
generate keyword baru — dan kuota indexasi selalu cukup.

---

## 10. Schema & sinyal entitas

Sudah ada dan harus dipertahankan: `Organization` + `ProfessionalService` (di `Layout.astro`),
`BreadcrumbList` (tiap halaman), `Article` (tiap post), `FAQPage` (opsional).

Untuk artikel industri, lengkapi `Article` dengan:
- `about` → nama industri (`"@type":"Thing","name":"Kontraktor"`),
- `mentions` → layanan yang relevan (`"@type":"Service"`),
- `dateModified` **jujur** (hanya bila memang diperbarui — pola `growth-freshness` sudah benar:
  `datePublished` tidak diubah),
- `author` konsisten + `publisher` dengan logo.

Jangan memakai tipe entitas bisnis milik klien (`GeneralContractor`, `HardwareStore`, `RealEstateAgent`)
pada artikel kita — itu menyatakan kita adalah bisnis tersebut. Cukup `Service`/`Thing`/`Article`.

Konsistensi NAP (nama, alamat `Jl. Arcamanik Endah No.76, Bandung 40195`, telepon) dan `sameAs`
harus identik di co.id, .my, dan `id.beriklan.co.id` — ini yang paling memengaruhi kelayakan dikutip LLM.

---

## 11. Kekhususan .my

1. Konten **Bahasa Inggris** dengan istilah pasar Malaysia (`lang="en"` sudah benar di `Layout.astro:50`).
2. Mulai dari aset terbukti: `/tiktok-live-viewers/` + 5 halaman viewers lain + 3 kalkulator.
   Cluster .my sebaiknya **tool-centric**: 1 tool → 8–12 artikel pendukung.
3. Manfaatkan **4.723 entri `posts.json` yang belum jadi URL** sebelum generate apa pun (§1.4 audit,
   `plan.my.md` §C.1.6) — konten sudah ada, tinggal disaring kualitasnya dan dirilis bertahap.
4. Setiap halaman baru di luar `/blog/*` wajib ditambahkan ke `run_worker_first` (20 path eksplisit).
5. Setelah deploy, PUT cron `[{"cron":"0 * * * *"}]` — jsonc .my tidak punya `triggers`.

---

## 12. Definition of done (ekspansi industri)

- [ ] `industry-keywords.json` (2.291) ter-import ke **Postgres** dengan `service` terisi dan `intent` terkoreksi
- [ ] Antrian lama di-re-skoring; baris ber-`service` kosong berstatus `blocked`
- [ ] `clusters.json` diperluas: ≥ 1 cluster per wave (pillar + 8–12 supporting)
- [ ] Wave 1 (kontraktor) live, 100% URL = 200, 0 soft-404, terkirim IndexNow + GSC
- [ ] Gerbang kualitas §7 dijalankan otomatis dan menolak draft di bawah standar
- [ ] Cap publish 15/hari tidak pernah dilanggar selama wave berjalan
- [ ] Gerbang §8.1 terpenuhi sebelum wave berikutnya dimulai
- [ ] .my: konten EN, cluster tool-centric, `run_worker_first` lengkap

<!--END-->

