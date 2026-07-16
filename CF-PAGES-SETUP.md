# CF Pages Setup — Auto-Deploy dari GitHub Push

> Goal: setiap push ke GitHub → CF auto-build + deploy. Tidak perlu wrangler local.

---

## Kenapa CF Pages?

Saat ini deployment masih manual via `wrangler deploy`. Workflow cloud-only butuh push ke GitHub → auto-deploy.

**CF Pages Build** (free tier):
- Direct connection ke GitHub repo
- Auto-build setiap push
- Auto-deploy static + workers (kalau pakai `_worker.js`)
- Free unlimited static deploy

---

## Setup (10 menit, one-time di dashboard)

### 1. Buka Cloudflare Dashboard

Pergi ke: https://dash.cloudflare.com → **Workers & Pages** → **Create** → **Pages** tab

### 2. Connect GitHub

Klik **"Connect to Git"** → pilih **GitHub** → authorize **cloudflare** GitHub App:
- Repository: `ReqTimeout/beriklan.co.id`
- Branch: `main`

### 3. Build Configuration

- **Build command:**
  ```bash
  cd web && npm install && npm run build
  ```
- **Build output directory:** `dist`
- **Root directory (advanced):** `web`
- **Environment variables:**
  - `NODE_VERSION=20`
  - `CI=true`
  - `PUBLIC_URL=https://beriklan.co.id` (optional)
- **Compatibility flags:**
  - `nodejs_compat`

### 4. Save and Deploy

Klik **"Save and Deploy"** → tunggu ~3-5 menit untuk first build.

### 5. Custom Domain (Optional)

Setelah first deploy berhasil:
- **Settings** → **Triggers** → **Custom Domains** → **Set up a custom domain**
- Masukkan `beriklan.co.id` dan `www.beriklan.co.id`
- CF otomatis setup DNS records

⚠️ **Note:** Beriklan.co.id saat ini di-serve oleh worker `beriklanweb`. Mengganti ke Pages perlu:
- Pages URL di-set ke `beriklan.co.id`
- Worker `beriklanweb` route dihapus (kalau mau Pages handle semua)
- ATAU keep keduanya: Pages untuk static, worker untuk `/api/*` endpoints

Pilihan paling sederhana: **Pages handles static + API routes via `_worker.js`** (Pages Workers).

---

## Arsitektur Final (Pure Cloud)

```
[cron-job.org]
      ↓ daily 02:00 UTC
[CF Worker /api/cron/trending]
      ↓
   Fetch trending RSS → filter → pick
      ↓
   Generate article via Groq API (Workers AI quota habis pakai Groq)
      ↓
   Commit to GitHub via API
      ↓
[CF Pages] auto-detect push
      ↓
   npm install → npm run build → wrangler assets
      ↓
[Cloudflare Edge] → https://beriklan.co.id
```

### Daily ops (zero local involvement)

1. ⏰ 02:00 UTC: cron-job.org hits `/api/cron/trending`
2. 🤖 Worker generates article + commits to GitHub
3. 🚀 CF Pages auto-builds (1-3 menit)
4. 🌍 New article live at `https://www.beriklan.co.id/blog/{slug}/`
5. 📡 Indexer similar cron submits ke Bing/Seznam/Naver
6. 📊 Real-time metrics di `/api/health`

### Bulk indexing (separate cron)

Sudah ada `/api/cron/indexing` — setup cron-job.org cron kedua:
- Schedule: daily 06:00 UTC (after Google quota reset at midnight Pacific)
- URL: `https://www.beriklan.co.id/api/cron/indexing?token=...`

---

## After CF Pages connected, runbook for daily ops

| Task | Owner | How |
|------|-------|-----|
| Add new service page | user | Edit `web/src/pages/jasa-*/index.astro`, push to main |
| Update copy | user | Edit, commit, push |
| Daily trending article | auto | cron-job.org → Worker → GitHub → Pages |
| Bulk indexing | auto | cron-job.org → Worker → IndexNow |
| Staging test | user | Run `npm run build` locally first |
| Rollback | manual | `git revert <bad-commit> && git push` (CF Pages auto-rolls-back) |
| Force rebuild | manual | Trigger deploy di CF Pages dashboard |

---

## Plan.md Status (after CF Pages)

| Day | Status |
|-----|--------|
| 1-5 | ✅ 100% (Foundation + bulk articles) |
| 6 | ✅ 90% (Google Indexing submission) |
| 7 | ✅ 100% (Cron trigger + endpoints) |
| 7+ Pillar | ✅ 100% |
| 8 Trending | ✅ 100% (cloud pipeline via Groq + Worker) |
| CF Pages setup | ⏳ User to do (10 min, one-time) |

After CF Pages connected, EVERYTHING is cloud. Zero local scripts needed.
