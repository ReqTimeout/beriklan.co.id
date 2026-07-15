# GSC Indexer Setup (Day 6)

> Auto-submit generated article URLs ke Google + Bing + Seznam + Naver.

---

## Service Account Credentials

Service account sudah ada di:

- File: `web/secrets/gsc-indexer.json`
- Email: `beriklan-seo-bot@lgc-indexer.iam.gserviceaccount.com`
- Project: `lgc-indexer`
- Scopes: `https://www.googleapis.com/auth/indexing`

---

## Step 1: Tambah Service Account ke Google Search Console

WAJIB — tanpa ini, Google Indexing API return **403 PERMISSION_DENIED**.

1. Buka https://search.google.com/search-console (login sebagai owner beriklan.co.id)
2. Pilih property **https://beriklan.co.id/**
3. Sidebar → **Settings** (⚙️ gear icon) → **Users and permissions**
4. Klik **"Add user"**
5. Paste email: `beriklan-seo-bot@lgc-indexer.iam.gserviceaccount.com`
6. Pilih role: **Owner** (full access untuk Indexing API)
7. Klik **Add**

---

## Step 2: Test Auth Lokal

```bash
cd /Users/maabook/Desktop/beriklan.co.id
python3 scripts/seo/gsc_indexer.py --dry-run
```

Expected output:
```
============================================================
GSC Indexer — beriklan.co.id (Day 6)
============================================================
Service account: beriklan-seo-bot@lgc-indexer.iam.gserviceaccount.com
Project: lgc-indexer
Dry run — would process 738 URLs
```

Test submit 1 URL:
```bash
python3 scripts/seo/gsc_indexer.py --indexing-only --limit 1
```

Kalau **403 PERMISSION_DENIED** → langkah Step 1 belum selesai.

Kalau **200 OK** → siap submit batch.

---

## Step 3: Submit Semua Generated URLs

```bash
python3 scripts/seo/gsc_indexer.py --all
```

Submit to:
- Google Indexing API (URL_UPDATED)
- Bing IndexNow
- Seznam.cz IndexNow
- Naver IndexNow
- Sitemap ping (Yandex only — Google/Bing sudah deprecate ping endpoint)

Quota:
- Google: 200 publish/day per project
- IndexNow: 10,000 URL/request

---

## Step 4: Setup IndexNow Key (optional, untuk Bing/Seznam/Naver)

Bikin file di `web/public/<key>.txt` dengan content `<key>` itu sendiri, lalu set:

```bash
export INDEXNOW_KEY="<key>"
```

Kalau belum punya key, lewati — bagian IndexNow akan skip dengan warning.

---

## File di repo

- `scripts/seo/gsc_indexer.py` — main script
- `web/secrets/gsc-indexer.json` — credentials (gitignored, tidak ikut deploy)
- `data/index_log.json` — log submission history (auto-generated)
