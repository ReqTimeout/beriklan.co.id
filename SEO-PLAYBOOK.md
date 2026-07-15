# SEO Auto-Pilot Playbook

> Panduan step-by-step untuk mengimplementasikan sistem SEO otomatis pada website lain.
> Sistem ini dirancang untuk: **content freshness, auto-indexing, internal linking, dan mass content generation** — semuanya dalam batas free tier.

---

## ⚠️ Real Status (ForYouTour Implementation)

| Komponen | Status | Real | Notes |
|----------|--------|------|-------|
| **Freshness Engine** | ✅ Aktif | Worker cron 2x/hari, update 20 artikel random | Date update di posts-meta.json via GitHub API |
| **Link Rotator** | ✅ Aktif | Worker cron Minggu (date-based), 50 artikel | Swap Baca Juga HTML di posts.json 94MB |
| **Content Generator** | ✅ Aktif | Worker cron tgl 1 & 15 (date-based), 2 keyword pending | Append artikel template ke posts.json + mark generated |
| **IndexNow Bing** | ✅ Aktif | 11K URL submitted, expected "failed" karena duplicate | URL sudah pernah submit = normal |
| **IndexNow Seznam** | ✅ Aktif | 11K URL submitted, semua success | Engine kedua |
| **IndexNow Naver** | ✅ Aktif | 11K URL submitted | Engine Korea |
| **Sitemap Ping** | ✅ Aktif | Google/Bing/Yandex setiap cron run | |
| **Rank Tracker** | ❌ Belum | Butuh GSC API setup + service account | Skeleton di `scripts/rank_tracker.py` |
| **Dashboard** | ✅ Aktif | `https://foryoutour-seo-cron.3smedianet.workers.dev/dashboard` | Real-time data dari GH API + sitemap live |

### Cron Schedule (Cloudflare Free plan: max 2 triggers)

```
0 6  * * *    UTC   → freshness + IndexNow + (Sunday) link rotation
0 18 * * *    UTC   → freshness + IndexNow + (1st & 15th) keyword gen
```

Date-based logic (Sunday, 1st, 15th) di-handle di dalam Worker code, bukan trigger terpisah — karena Cloudflare Free plan hanya support 2 cron triggers.

### Cloudflare Free Plan Limits

- 100k Worker requests/day ✅ (kita pakai ~10/hari)
- 30s CPU per scheduled event ✅ (kita pakai ~5s)
- **Max 2 cron triggers** (Free plan limit, bukan 3)
- Workers Analytics Engine: 100k events/day (jika pakai)

---

## Daftar Isi

1. [Arsitektur & Komponen](#1-arsitektur--komponen)
2. [Prerequisites](#2-prerequisites)
3. [Setup Content Freshness Engine](#3-setup-content-freshness-engine)
4. [Setup Internal Link Rotator](#4-setup-internal-link-rotator)
5. [Setup Keyword Research & Auto-Generator](#5-setup-keyword-research--auto-generator)
6. [Setup Multi-Engine IndexNow](#6-setup-multi-engine-indexnow)
7. [Setup Rank Tracker](#7-setup-rank-tracker)
8. [GitHub Actions Unified Workflow](#8-github-actions-unified-workflow)
9. [Cloudflare Worker Cron](#9-cloudflare-worker-cron)
10. [Memory Optimization untuk Build](#10-memory-optimization-untuk-build)
11. [Files Reference](#11-files-reference)

---

## 1. Arsitektur & Komponen

```
┌─────────────────────────────────────────────────────┐
│                  GitHub Actions                      │
│  ───────────────────────────────────────────────     │
│  Setiap 4 jam: freshness.py (20 artikel random)      │
│  Hari 1 & 15:   keyword_research.py → generate.py   │
│  Minggu:        rotate_links.py                      │
│  Jam 00:00:     ping_sitemaps.py                     │
│         ↓ commit & push ↓                            │
├─────────────────────────────────────────────────────┤
│              Cloudflare Pages                        │
│  Auto-build & deploy dari push ke main               │
├─────────────────────────────────────────────────────┤
│              Cloudflare Worker                       │
│  06:00 & 18:00 UTC: IndexNow + sitemap ping          │
└─────────────────────────────────────────────────────┘
```

### Tujuan Setiap Komponen

| Komponen | Efek SEO | Mekanisme |
|----------|----------|-----------|
| **Freshness Engine** | Google melihat artikel terus diperbarui → crawl lebih sering | Update tanggal + swap testimonial/tips/FAQ tiap 4 jam |
| **Link Rotator** | Link equity menyebar ke semua artikel, bukan stuck di itu-itu aja | Hapus "Baca Juga" lama, inject link ke artikel beda tiap minggu |
| **Content Generator** | Tambah coverage keyword long-tail → target trafik organik | Kombinasi "sewa [armada] + [destinasi wisata]" → generate artikel template-based |
| **IndexNow** | Indexing dalam hitungan jam, bukan minggu | POST batch ke Bing/Seznam/Naver tiap 12 jam |
| **Rank Tracker** | Deteksi artikel turun ranking → auto-refresh | GSC API → prioritize artikel drop buat di-fresh |

---

## 2. Prerequisites

### Struktur Data yang Dibutuhkan

```
src/data/posts.json          → Array of articles, each with: slug, title, content, excerpt, date, category
article_tracker.json         → Array of keyword objects, each with: keyword, armada, status, slug, route_type, ...
```

### Format `posts.json` (setiap item):

```json
{
  "slug": "sewa-bus-ke-lembang",
  "title": "Sewa Bus ke Lembang | ForYouTour",
  "content": "<p>Full HTML content...</p>",
  "excerpt": "Short excerpt for listing...",
  "date": "2026-06-28",
  "category": "sewa-bus-pariwisata",
  "link": "https://example.com/blog/sewa-bus-ke-lembang"
}
```

### Format `article_tracker.json` (setiap item):

```json
{
  "keyword": "sewa bus ke lembang bandung",
  "armada": "Hiace / Commuter (4-15 org)",
  "location": "Lembang",
  "route_type": "WISATA_Lembang",
  "source": "KEYWORD_RESEARCH",
  "category": "sewa-bus-pariwisata",
  "slug": "sewa-bus-ke-lembang-bandung",
  "status": "pending",
  "article_title": "Sewa Bus Ke Lembang Bandung | ForYouTour",
  "url": "https://example.com/blog/sewa-bus-ke-lembang-bandung"
}
```

---

## 3. Setup Content Freshness Engine

**File:** `scripts/freshness.py`

### Cara Kerja
1. Load `posts.json`
2. Pilih N artikel random
3. Hapus semua enrichment block lama (testimonial, tips, FAQ, Baca Juga)
4. Inject enrichment baru dengan kombinasi random dari pool
5. Update `date` ke hari ini
6. Submit IndexNow untuk URL yang di-refresh
7. Update `posts-meta.json`

### Pool yang Harus Disesuaikan untuk Website Lain

```python
# Di dalam freshness.py, ubah ini:

SITE = 'https://www.your-site.com'         # Ganti domain
INDEXNOW_KEY = 'your-indexnow-key'          # Ganti key
PHONE = '0812-XXXX-XXXX'                    # Ganti no telepon
WA_LINK = 'https://wa.me/62812XXXX'         # Ganti link WA

# TESTIMONIALS — ganti dengan testimonial real site-mu
TESTIMONIALS = [
    ("Nama Pelanggan", "jenis perjalanan", "armada", "testimonial"),
    ...
]

# TIPS_POOL — ganti dengan tips relevan site-mu
TIPS_POOL = [
    "Tip 1 relevan dengan niche...",
    ...
]

# FAQ_POOL — ganti dengan FAQ real
FAQ_POOL = [
    ("Pertanyaan?", "Jawaban..."),
    ...
]
```

### HTML Selector yang Mungkin Perlu Disesuaikan

Script ini mencari dan menghapus enrichment blocks berdasarkan CSS class:

```python
# Regex untuk menghapus enrichment lama — sesuaikan class name dengan template-mu:
content = re.sub(r'<div class="bg-amber-50 border-l-4...', '', content, ...)
content = re.sub(r'<div class="bg-sky-50 rounded-2xl...', '', content, ...)
content = re.sub(r'<div class="my-8">\s*<h3 class="text-lg.*?Pertanyaan.*?</div>...', '', content, ...)
```

### Run Manual

```bash
python3 scripts/freshness.py --count 20    # 20 artikel
python3 scripts/freshness.py --all          # Semua artikel
```

---

## 4. Setup Internal Link Rotator

**File:** `scripts/rotate_links.py`

### Cara Kerja
1. Build keyword index dari semua artikel
2. Untuk setiap artikel, cari artikel related dari keyword group yang sama
3. Hapus "Baca Juga" section lama
4. Inject link ke artikel LAIN (bukan yang sama dengan sebelumnya)
5. Menggunakan `random.Random(slug + seed)` → reproducible tapi beda tiap run

### Keyword Groups — Harus Disesuaikan

```python
KEYWORD_GROUPS = {
    'group_name': ['keyword1', 'keyword2', ...],
    'lembang': ['lembang', 'floating market', 'farmhouse', ...],
    'ciwidey': ['ciwidey', 'kawah putih', 'patenggang', ...],
    ...
}
```

Sesuaikan dengan kategori/niche website target.

### HTML Output yang Dihasilkan

```html
<div class="my-8 p-5 bg-gradient-to-r from-sky-50 to-blue-50 rounded-2xl border border-sky-100">
  <h3 class="text-lg font-bold text-slate-900 mb-4">📖 Artikel Lainnya</h3>
  <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
    <a href="/blog/related-article-1" class="block bg-white p-4 ...">📄 Judul Artikel 1</a>
    <a href="/blog/related-article-2" class="block bg-white p-4 ...">📄 Judul Artikel 2</a>
  </div>
</div>
```

### Penempatan Link

Link di-inject setelah paragraf ke-7 (bisa disesuaikan):

```python
paragraphs = content.split('</p>')
if len(paragraphs) > 7:  # ← ubah angka ini
    ...
```

---

## 5. Setup Keyword Research & Auto-Generator

**File:** `scripts/keyword_research.py`

### Cara Kerja
1. Generate kombinasi keyword dari daftar destinasi × armada × route types
2. Cek duplikasi dengan existing keywords di tracker
3. Tambah keyword baru dengan `status: "pending"`
4. Panggil `generate_article.py` yang memproses pending keywords

### Yang Harus Disesuaikan

```python
SITE = 'https://www.your-site.com'

# Armada — ganti dengan produk/layanan website target
ARMADA_TYPES = [
    ("Nama Produk 1", "short-name-1"),
    ("Nama Produk 2", "short-name-2"),
]

# Destinasi/kategori — ganti dengan kategori website target
DESTINATIONS = {
    'CATEGORY_NAME': {
        'label': 'Label',
        'keywords': ['keyword1', 'keyword2', ...],
        'locations': ['Location1'],
    },
}

# Route types — sesuaikan dengan konteks bisnis
ROUTE_TYPES = ['TO_BANDUNG', 'WISATA']
```

### Template Keyword Patterns

```python
patterns = {
    'TO_BANDUNG': [
        f"sewa {armada_short} ke {kw} dari bandung",
        f"sewa {armada_short} ke {dest_label} {loc}",
        ...
    ],
    'WISATA': [
        f"sewa bus wisata ke {kw}",
        f"paket wisata {kw} naik bus",
        ...
    ],
}
```

### Generate Artikel

Script `generate_article.py` adalah **template-based content generator** (bukan AI). Setiap keyword type punya template 500+ kata dengan:
- SEO-friendly headings (h2, h3)
- Internal links ke halaman produk/layanan
- CTA dengan nomor telepon
- FAQ section
- Backlink (jika ada kerja sama)

Template di-generate dari dictionary `TEMPLATES` di dalam file. Untuk website lain, template ini HARUS ditulis ulang sesuai niche.

```python
# Di generate_article.py — ubah template untuk setiap keyword TYPE:
TEMPLATES = {
    'airport': article_airport,      # Fungsi template untuk keyword bandara
    'stasiun': article_stasiun,      # Template stasiun
    'wisata': article_wisata,        # Template wisata
    'to_bandung': article_tobandung, # Template perjalanan ke Bandung
    'from_bandung': article_frombdg, # Template dari Bandung
    'pp_route': article_pp,          # Template PP
    'stasiun_dest': article_stasiun_dest, # Template stasiun ke destinasi
}
```

### Run

```bash
# Dry-run dulu
python3 scripts/keyword_research.py --dry-run

# Generate (tambah ke tracker + generate artikel)
python3 scripts/keyword_research.py --generate

# Batch tertentu
python3 scripts/keyword_research.py --generate --batch 10
```

---

## 6. Setup Multi-Engine IndexNow

**File:** `scripts/auto_index.py`

### Cara Kerja
Submit URL ke 3 search engine yang mendukung IndexNow protocol:

| Engine | Endpoint | Coverage |
|--------|----------|----------|
| Bing | `https://www.bing.com/indexnow` | Global |
| Seznam.cz | `https://search.seznam.cz/indexnow` | Eropa (CZ/SK) |
| Naver | `https://searchadvisor.naver.com/indexnow` | Korea |

### Yang Harus Disiapkan
1. Generate IndexNow key: File teks berisi key string, simpan di `public/{key}.txt`
2. Key bisa random string (contoh: `ab06285957ab4a7eb7bcf591cfbd15b0`)
3. URL key harus bisa diakses: `https://your-site.com/{key}.txt`

### Konfigurasi

```python
SITE = 'https://www.your-site.com'         # Ganti domain
INDEXNOW_KEY = 'your-key-here'             # Ganti key
```

### Run

```bash
# Batch (hanya yang belum terkirim)
python3 scripts/auto_index.py --batch

# Semua URL
python3 scripts/auto_index.py --all
```

### Verifikasi

```bash
curl "https://ssl.bing.com/webmaster/configure/verify/IndexNow?siteUrl=https://your-site.com"
```

---

## 7. Setup Rank Tracker

**File:** `scripts/rank_tracker.py`

### Prerequisites

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Google Search Console Setup

1. **Buat Service Account** di Google Cloud Console:
   - https://console.cloud.google.com/apis/credentials
   - Create Credentials → Service Account
   - Download JSON key → simpan sebagai `indexer-430015-4d1e4c0f41d9.json`

2. **Tambah ke Google Search Console**:
   - Buka https://search.google.com/search-console
   - Settings → Users and permissions → Add user
   - Masukkan email service account (`xxx@project.iam.gserviceaccount.com`)
   - Role: **Owner** (Full) — minimal **Restricted** (Read + Indexing)

3. **Update path credentials di script**:

```python
GOOGLE_CREDENTIALS = os.path.join(BASE_DIR, 'indexer-430015-4d1e4c0f41d9.json')
```

### Run

```bash
# Lihat report artikel turun ranking
python3 scripts/rank_tracker.py --report

# Auto-refresh artikel yang drop
python3 scripts/rank_tracker.py --auto-fresh
```

### Output Report

```
📉 Articles dropping (pos 5-15, >50 impressions):
  8.3 |  1203 imp |  45 clk | sewa-bus-ke-lembang
  7.1 |   892 imp |  12 clk | paket-wisata-ciwidey
  ...

🔇 Articles with 0 clicks (>100 impressions):
  pos 12.5 |  456 imp | sewa-bus-ke-kawah-putih
  ...
```

---

## 8. GitHub Actions Unified Workflow

**File:** `.github/workflows/freshness.yml`

Workflow ini menggantikan semua cron terpisah. Cukup satu workflow yang handle semuanya.

### Schedule

| Cron | Waktu | Aksi |
|------|-------|------|
| `0 */4 * * *` | Setiap 4 jam | Refresh 20 artikel + commit |
| (di dalam bash) | Jam 00:00 UTC | Ping sitemaps |
| (di dalam bash) | Hari Minggu | Rotate links 300 artikel |
| (di dalam bash) | Tanggal 1 & 15 | Keyword research + generate |

### Budget Free Tier

- **GitHub Actions**: 2000 menit/bulan gratis
  - Workflow: ~180 run/bln × ~40 detik = ~120 menit ✅
- **Cloudflare Pages**: 500 build/bulan gratis
  - Build: ~180 push/bln ✅

### Fitur Workflow

```yaml
concurrency:
  group: seo-autopilot           # Mencegah overlap run
  cancel-in-progress: true       # Batalkan run lama jika ada yang baru
```

---

## 9. Cloudflare Worker Cron

**Folder:** `cloudflare-cron/`

### File

| File | Fungsi |
|------|--------|
| `worker.js` | Fetch sitemap → IndexNow batch → ping → link check |
| `wrangler.toml` | Konfigurasi Worker + cron triggers |

### Deploy

```bash
# Install wrangler
npm install -g wrangler

# Login (butuh akun Cloudflare)
npx wrangler login

# Deploy
cd cloudflare-cron
npx wrangler deploy
```

### Yang Harus Disesuaikan

```javascript
// Di worker.js:
const SITE = 'https://www.your-site.com';
const INDEXNOW_KEY = 'your-key-here';
const SITEMAP_URL = 'https://www.your-site.com/sitemap.xml';
```

```toml
# Di wrangler.toml:
name = "your-site-seo-cron"
[vars]
SITE = "https://www.your-site.com"
INDEXNOW_KEY = "your-key-here"
SITEMAP_URL = "https://www.your-site.com/sitemap.xml"
```

### Cron Schedule

```toml
[triggers]
crons = ["0 6 * * *", "0 18 * * *"]
```

Worker akan:
1. Fetch semua URL dari sitemap
2. Submit batch ke Bing IndexNow
3. Submit batch ke Seznam.cz IndexNow
4. Ping Google/Bing/Yandex
5. Cek 20 URL random untuk broken links

### Test

```bash
curl https://your-site-seo-cron.your-account.workers.dev
```

---

## 10. Memory Optimization untuk Build

### Masalah

Cloudflare Pages free tier punya **512 MB RAM**. Load `posts.json` (bisa 50-100 MB) langsung di config menyebabkan OOM (Out of Memory) → build gagal dengan "Aborted (core dumped)".

### Solusi: Dual JSON (Meta + Full)

Buat file metadata ringan yang hanya berisi field yang dibutuhkan saat build:

```bash
python3 -c "
import json
posts = json.load(open('src/data/posts.json'))
meta = [{k: v for k, v in p.items() if k != 'content'} for p in posts]
json.dump(meta, open('src/data/posts-meta.json', 'w'))
"
```

Hasil: `posts.json` 94 MB → `posts-meta.json` 5 MB (19× lebih kecil).

### Update Config untuk Pakai Meta

**`astro.config.mjs`:**
```js
// Before (94MB loaded):
const posts = require('./src/data/posts.json');

// After (5MB loaded):
const posts = require('./src/data/posts-meta.json');
```

**`src/pages/blog/index.astro`:**
```astro
// Before: JSON.parse(fs.readFileSync('./src/data/posts.json'))
import posts from '../../data/posts-meta.json';
```

**`src/pages/blog/[slug].astro`:**
```astro
// getStaticPaths pakai meta (ringan)
import postsMeta from '../../data/posts-meta.json';
// Konten penuh cuma di-load sekali via ESM import
import allPosts from '../../data/posts.json';
```

### Auto-Rebuild Meta di Workflow

```yaml
- name: Rebuild meta
  run: |
    python3 -c "
    import json
    posts = json.load(open('src/data/posts.json'))
    meta = [{k: v for k, v in p.items() if k != 'content'} for p in posts]
    json.dump(meta, open('src/data/posts-meta.json', 'w'))
    "
```

---

## 11. Files Reference

### Scripts

| File | Fungsi | Dependency |
|------|--------|------------|
| `scripts/freshness.py` | Refresh N artikel random + update date | `posts.json` |
| `scripts/rotate_links.py` | Rotasi internal link ke artikel beda | `posts.json` |
| `scripts/keyword_research.py` | Generate keyword baru + add ke tracker | `article_tracker.json` |
| `scripts/generate_article.py` | Generate artikel dari pending keywords | `article_tracker.json` + `posts.json` |
| `scripts/auto_index.py` | Multi-engine IndexNow batch | `article_log.json` |
| `scripts/ping_sitemaps.py` | Ping Google/Bing/Yandex daily | - |
| `scripts/rank_tracker.py` | GSC rank analysis + auto-refresh | `indexer-*-*.json` (GSC credentials) |
| `scripts/content_enrichment.py` | Inject testimonial/tips/FAQ ke artikel | `posts.json` |

### Cloudflare

| File | Fungsi |
|------|--------|
| `cloudflare-cron/worker.js` | Edge Worker: IndexNow + ping + link check |
| `cloudflare-cron/wrangler.toml` | Worker config + cron triggers |

### Config

| File | Fungsi |
|------|--------|
| `astro.config.mjs` | Astro build config + sitemap |
| `.github/workflows/freshness.yml` | Unified automation workflow |

### Data

| File | Ukuran | Fungsi |
|------|--------|--------|
| `src/data/posts.json` | 50-100 MB | Full article data + content |
| `src/data/posts-meta.json` | 3-5 MB | Metadata tanpa content (build optimization) |
| `article_tracker.json` | ~1 MB | Keyword tracker + generation status |
| `article_log.json` | ~1 MB | Log generated articles |
| `index_log.json` | ~100 KB | IndexNow submission history |
| `public/{key}.txt` | 1 KB | IndexNow verification key |

---

## 🔍 Reality Check: PLAYBOOK vs Real Implementation

Apa yang ditulis di awal PLAYBOOK ini vs yang **benar-benar berjalan** di ForYouTour setelah audit:

| Aspek | Original PLAYBOOK | Real Implementation | Alasan Perubahan |
|-------|-------------------|---------------------|-------------------|
| Cron frequency | 4 jam | **12 jam** (06 & 18 UTC) | Cloudflare Free plan max 2 triggers |
| IndexNow engines | Bing + Seznam | **Bing + Seznam + Naver** | Tambah Naver (Korea) |
| Link rotation trigger | Weekly Sunday cron terpisah | **Date-based inside daily cron** | Trigger limit |
| Keyword gen trigger | Monthly cron terpisah | **Date-based inside daily cron** | Trigger limit |
| Freshness file | posts.json (94MB) | **posts-meta.json (5MB)** | CPU time limit, posts.json terlalu besar untuk freshness |
| Link rotation file | posts.json 94MB | **posts.json 94MB** | OK, hanya jalan 1x/minggu (50 artikel) |
| Worker uses GH_TOKEN | Optional | **Required** | Repo private, GH_TOKEN wajib |
| GitHub Actions | Used for freshness | **Disabled** (billing issue) | Worker + GH API replacement |
| Dashboard | Mentioned | **Built** at `/dashboard` route | Real-time monitoring |
| Public commit access | Not considered | **Required auth via GH_TOKEN** | Repo is private |

### Lesson Learned

1. **Cloudflare Free plan limits** lebih ketat dari yang PLAYBOOK awalnya asumsikan
2. **Date-based logic** lebih fleksibel dari multiple triggers — hemat slot
3. **File size matters** — posts-meta.json (5MB) vs posts.json (94MB) adalah perbedaan signifikan
4. **Private repos** butuh GH_TOKEN untuk semua akses API
5. **Build memory** = Cloudflare Pages 512MB → posts.json 94MB bikin OOM → butuh posts-meta.json

---

## Quickstart untuk Website Baru

### Step 1: Persiapan (30 menit)

```bash
# 1. Setup data structure
mkdir -p src/data
touch src/data/posts.json          # Isi minimal 1 artikel
touch article_tracker.json          # Isi [{"keyword":"...", "status":"pending", ...}]
echo "your-indexnow-key" > public/your-indexnow-key.txt

# 2. Copy scripts
cp -r scripts/ your-project/
cp -r cloudflare-cron/ your-project/

# 3. Sesuaikan konfigurasi
#   - Ganti SITE, INDEXNOW_KEY, PHONE, WA_LINK di semua script
#   - Ganti TESTIMONIALS, TIPS_POOL, FAQ_POOL di freshness.py
#   - Ganti KEYWORD_GROUPS di rotate_links.py
#   - Ganti ARMADA_TYPES, DESTINATIONS di keyword_research.py
#   - Ganti TEMPLATES di generate_article.py (tulis ulang template konten)
#   - Ganti domain di astro.config.mjs
#   - Ganti vars di wrangler.toml
```

### Step 2: Testing (15 menit)

```bash
# Test freshness
python3 scripts/freshness.py --count 5

# Test link rotation
python3 scripts/rotate_links.py --batch 10

# Test keyword research (dry-run)
python3 scripts/keyword_research.py --dry-run

# Test IndexNow
python3 scripts/auto_index.py --batch
```

### Step 3: Deploy (30 menit)

```bash
# 1. Push ke GitHub
git add -A && git commit -m "seo setup" && git push

# 2. Setup Cloudflare Pages
#   - Connect GitHub repo
#   - Build command: npm run build
#   - Output dir: dist

# 3. Deploy Worker
cd cloudflare-cron
npx wrangler login
npx wrangler deploy
```

### Step 4: Verify (10 menit)

```bash
# Test worker
curl https://your-worker.your-account.workers.dev

# Cek GitHub Actions
#   - Buka repo → Actions → "SEO Auto-Pilot"
#   - Trigger manual untuk test

# Cek RSS feed
curl https://your-site.com/blog/rss.xml | head -20
```

---

## Catatan Penting

1. **Generator bukan AI** — `generate_article.py` menggunakan template statis. Untuk niche berbeda, template harus ditulis ulang total.
2. **Free tier limits**:
   - GitHub Actions: 2000 min/bln, 500 MB storage
   - Cloudflare Pages: 500 build/bln, 512 MB RAM
   - Cloudflare Workers: 100k req/day, 10 ms CPU/req
3. **`posts.json` growth** — Jika > 50 MB, pertimbangkan Git LFS atau split data.
4. **GSC API rate limit** — 2000 queries/day per project. `rank_tracker.py` dirancang untuk query terbatas.
5. **Bing IndexNow** — API tidak mengembalikan error untuk duplicate submission (status non-200 untuk URL yang sudah pernah dikirim). Wajar.
6. **Content enrichment pools** — Semakin besar pool (testimonial, tips, FAQ), semakin unik setiap artikel. Target minimal 30+ testimonial dan 20+ tips per kategori.
