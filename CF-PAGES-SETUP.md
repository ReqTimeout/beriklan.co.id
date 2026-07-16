# CF Pages Setup — Pure Cloud Auto-Deploy

> **Status:** CF Pages project sudah dibuat via API: `beriklanweb` (subdomain: `beriklanweb.pages.dev`)
> 
> **Yang perlu user lakukan (5 menit):** Connect GitHub di dashboard

---

## Status Setup

| Step | Status |
|------|--------|
| CF Pages project created | ✅ API done (id: `90af4056-5aca-439b-a85d-dc32d89e779c`) |
| Build command configured | ✅ `cd web && npm install && npm run build` |
| Output dir configured | ✅ `dist` |
| Root dir configured | ✅ `web` |
| Build caching | ✅ enabled |
| **GitHub connection** | ❌ **Need user (5 min)** |
| Custom domain `beriklan.co.id` | ❌ Optional, can be set after |

---

## Setup (5 menit, one-time di dashboard)

### 1. Buka CF Pages Dashboard

- https://dash.cloudflare.com → **Workers & Pages** → **Pages** tab
- Cari project `beriklanweb` (sudah ada dari API)
- Klik project

### 2. Connect GitHub

Klik **"Connect to Git"** button:
- Pilih **GitHub**
- Authorize **cloudflare** GitHub App
- Pilih:
  - **Repository:** `ReqTimeout/beriklan.co.id`
  - **Production branch:** `main`
  - **Build command:** `cd web && npm install && npm run build` (pre-filled)
  - **Build output directory:** `dist` (pre-filled)
  - **Root directory:** `web` (pre-filled)
- Klik **"Save and Deploy"**

### 3. First Deploy

Tunggu ~3-5 menit untuk first build. Status akan berubah ke **Success** atau **Failed** (check logs if failed).

### 4. Set Custom Domain (Optional)

Setelah first build OK:
- **Custom domains** tab → **Set up a custom domain**
- Add `beriklan.co.id` dan `www.beriklan.co.id`
- CF auto-setup DNS

⚠️ **Conflict with existing worker:** `beriklan.co.id` saat ini served by `beriklanweb` worker. Untuk migrasi ke Pages:
- Setup Pages custom domain **first** (bisa coexist via DNS priority)
- Hapus Worker route setelah Pages live (settings → workers → beriklanweb → routes)

### 5. Continuous Deploy (after connect)

Setiap push ke `main` → CF Pages auto-builds (~1-3 menit) → deployed ke `beriklanweb.pages.dev` (atau custom domain)

---

## Architecture (Final, Pure Cloud)

```
[cron-job.org]                          ← your browser UI, free 50 cron jobs
      ↓ daily 02:00 UTC
[CF Worker /api/cron/trending]          ← deployed, auto-runs
      ↓
1. Fetch Google Trends RSS (3 geos)
2. Filter niche DM topics
3. Generate article via Groq API (free, no quota)
4. Commit to GitHub via API
5. Update D1
      ↓
[GitHub receives push]
      ↓
[CF Pages auto-builds on push]          ← after step 2-3 above
      ↓
[Cloudflare Edge] → https://beriklan.co.id/blog/{slug}/
```

Parallel cron (06:00 UTC):
```
[cron-job.org] → /api/cron/indexing
              → submits to Bing/Seznam/Naver
              → D1 tracks 541 pending URLs
```

---

## cron-job.org Setup (5 min)

After CF Pages connected, setup 2 cron jobs at https://cron-job.org:

### Cron 1: Trending Article
- **Title:** `Beriklan Daily Trending`
- **URL:** `https://www.beriklan.co.id/api/cron/trending?token=beriklan-admin-2026`
- **Method:** POST
- **Schedule:** Daily 02:00 UTC (= 09:00 WIB)

### Cron 2: Bulk Indexing
- **Title:** `Beriklan Daily Indexing`
- **URL:** `https://www.beriklan.co.id/api/cron/indexing?token=beriklan-admin-2026`
- **Method:** POST
- **Schedule:** Daily 06:00 UTC (= 13:00 WIB, after Google quota reset)

---

## After Everything Connected

Zero local involvement. Every day:
1. ⏰ 02:00 UTC: cron-job.org → `/api/cron/trending` → Groq generates article → commits to GitHub
2. 🚀 02:01 UTC: CF Pages auto-builds → article live
3. ⏰ 06:00 UTC: cron-job.org → `/api/cron/indexing` → submits 200 URLs to Bing/Seznam/Naver
4. 📊 24/7: `/api/health` shows pending_count trending down daily

### Monitoring

- `https://www.beriklan.co.id/api/health` → JSON status (live)
- CF Pages dashboard → deploys tab
- cron-job.org dashboard → history
- D1 queries: `wrangler d1 execute beriklan-seo --remote --command "SELECT * FROM cron_logs ORDER BY timestamp DESC LIMIT 5"`
