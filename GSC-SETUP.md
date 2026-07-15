# Google Search Console Setup Guide

> Setup GSC supaya fresh content ter-index lebih cepat.
> Setelah setup, script `rank_tracker.py` bisa otomatis detect artikel drop ranking.

---

## Kenapa GSC Penting?

**Tanpa GSC:**
- Google crawl kapan-kapan (minggu/bulan)
- Gak tahu keyword mana yang perform
- Gak bisa request re-indexing

**Dengan GSC:**
- Submit URL manual untuk indexing (priority)
- Liat keyword yang perform + CTR
- Deteksi artikel drop ranking
- Request re-crawl setelah update

---

## Step 1: Verifikasi Ownership

### Cara 1: HTML Tag (Recommended)

1. Buka **https://search.google.com/search-console**
2. Klik **"Add Property"** → **"URL Prefix"**
3. Masukkan: `https://www.foryoutours.com`
4. Pilih verifikasi **"HTML tag"**
5. Copy value dari meta tag (contoh: `abc123def456`)

6. Edit `src/layouts/BaseLayout.astro` line 58 (sebelum `<meta name="msvalidate..."`):

```html
<meta name="google-site-verification" content="abc123def456" />
```

7. Commit + push:
```bash
git add src/layouts/BaseLayout.astro
git commit -m "add google site verification"
git push
```

8. Tunggu Cloudflare Pages deploy (~1-2 menit)
9. Balik ke GSC → klik **"Verify"**

### Cara 2: DNS TXT Record (Alternatif)

Kalau gak mau edit file, pakai DNS:

1. Di Cloudflare DNS untuk `foryoutours.com`, tambah TXT record:
   - **Name**: `@`
   - **Content**: `google-site-verification=abc123def456`
2. Klik **"Verify"** di GSC

---

## Step 2: Submit Sitemap

1. Di GSC sidebar → **"Sitemaps"**
2. Masukkan sitemap URL: `sitemap-index.xml` (atau `sitemap.xml`)
3. Klik **"Submit"**
4. Status harus berubah ke **"Success"** dalam 1-2 hari
5. Cek jumlah URL yang ter-index: harusnya **11.219**

---

## Step 3: Setup Service Account untuk GSC API

Service account sudah ada di repo: `indexer-430015-4d1e4c0f41d9.json`

Cek email service account:
```bash
cat ~/Desktop/foryoutour/indexer-430015-4d1e4c0f41d9.json | python3 -c "import json,sys; print(json.load(sys.stdin)['client_email'])"
```

Output: `xxx@xxx.iam.gserviceaccount.com`

Tambahkan ke GSC:
1. GSC → **Settings** (gear icon) → **Users and permissions**
2. Klik **"Add user"**
3. Paste email service account
4. Pilih role: **Owner** (full access)
5. Klik **"Add"**

---

## Step 4: Setup Request Indexing

Setelah service account punya akses Owner, GSC API bisa digunakan untuk request indexing.

Install Python package:
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

Test:
```bash
python3 scripts/rank_tracker.py --report
```

Kalau berhasil, akan muncul:
```
📊 GSC Rank Report
============================================================

📉 Articles dropping (pos 5-15, >50 impressions):
  8.3 | 1203 imp | 45 clk | sewa-bus-ke-lembang
  ...
```

Kalau error "Permission denied" atau "403":
- Tunggu 5-10 menit setelah add user (propagation delay)
- Cek service account email benar

---

## Step 5: Auto Refresh Artikel Drop Ranking

Setelah GSC API jalan, tambah cron job di Worker (manual setup):

**Option A: Tambah trigger ke Worker** (gak bisa kalau sudah 2 triggers)
- Pindah rank_tracker logic ke existing 06:00 cron
- Tambah di worker.js: kalau GSC data available, auto-fresh 5 artikel yang drop

**Option B: Local cron di Mac** (recommended)
```bash
# Setup di crontab
crontab -e
# Tambah line (tiap Senin jam 07:00):
0 7 * * 1 cd ~/Desktop/foryoutour && python3 scripts/rank_tracker.py --auto-fresh
```

Atau via `launchd` (kayak yang udah disiapin):
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Weekday</key>
    <integer>1</integer>
    <key>Hour</key>
    <integer>7</integer>
</dict>
```

---

## Step 6: Monitor Performance

### Manual checks (URL di GSC):

1. **Performance** → Liat:
   - Total clicks
   - Total impressions
   - Average CTR
   - Average position

2. **URL Inspection** → Cek:
   - Status indexing per URL
   - Last crawl time
   - Canonical version

3. **Coverage** → Issues:
   - Pages with errors
   - Pages with warnings
   - Excluded pages

### Auto-monitor (via API):

Tambah ke `rank_tracker.py` schedule:
- Daily: fetch last 7 days performance
- Weekly: detect articles dropping
- Auto-fresh 5 articles with biggest drop

---

## Expected Timeline Setelah Setup

| Action | Timeline | Expected |
|--------|----------|----------|
| Verify GSC | 5 menit | "Ownership verified" |
| Submit sitemap | 1-2 hari | Status: Success, 11K URLs |
| Service account access | 5-10 menit | Can call API |
| First rank data | 1-2 hari | Performance data available |
| Article re-crawl after freshness | 1-7 hari | Google re-crawls updated date |

---

## Common Issues

### Q: "Ownership verification failed"
- Pastikan HTML tag persis sama (termasuk spasi)
- Tunggu deploy Cloudflare Pages selesai
- Coba lagi setelah 5 menit

### Q: "403 Permission denied" di API
- Service account belum di-add atau role kurang
- Pastikan role **Owner** (bukan Restricted)

### Q: "No data available" di Performance
- Data butuh waktu 1-2 hari setelah sitemap submit
- Pastikan sitemap sudah "Success" (bukan "Pending" atau "Couldn't fetch")

### Q: Articles masih belum di-index setelah 2 minggu
- Submit manual via URL Inspection: paste URL → "Request Indexing"
- Cek Coverage untuk errors
- Pastikan canonical URL benar

---

## File Reference

- `indexer-430015-4d1e4c0f41d9.json` — Service account credentials (gitignored)
- `scripts/rank_tracker.py` — GSC API client
- `src/layouts/BaseLayout.astro` — HTML tag location
- `SETUP-GH-WORKER.md` — Worker setup
- `CPANEL-SETUP.md` — cPanel Hostinger setup (alternative)
