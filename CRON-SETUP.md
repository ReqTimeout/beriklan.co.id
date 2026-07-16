# CF Worker Cron Setup — cron-job.org (External Cloud Cron)

## Kenapa pakai cron-job.org?

CF Workers free plan limit: **5 cron triggers per account** (sudah dipakai semua).
GH Actions: **runner unavailable** (3 detik instant failure).

**Solusi:** cron-job.org — free external cron service (cloud-only, no local).

URL: https://cron-job.org  
Free tier: 50 cron jobs.

---

## Setup (5 menit)

### 1. Sign up

- Buka https://cron-job.org
- Klik "Register" → email + password
- Verify email

### 2. Create Cron Job

- Klik "Create Cron Job"
- **Title:** `Beriklan Daily Indexing`
- **Address:**
```
https://www.beriklan.co.id/api/cron/indexing
```
- **Schedule:** `0 6 * * *` (06:00 UTC = 13:00 WIB = after Google quota reset)
  - Gunakan UI picker "Every day at 06:00"
- **Request method:** `POST`
- **Headers (optional):**
  - `User-Agent: CronJobBot/1.0`
- **Save**

### 3. Manual Test

Click "Run now" di dashboard cron-job.org. Verify:
```bash
curl -X POST "https://www.beriklan.co.id/api/cron/indexing"
# Returns: { "error": "Unauthorized", "hint": "Provide ?token=beriklan-admin-2026" }
```

Kalau pakai token, akan run cron:
```bash
curl -X POST "https://www.beriklan.co.id/api/cron/indexing?token=beriklan-admin-2026"
# Returns: { "ok": true, "google_ok": N, "indexnow_engines": 2, ... }
```

### 4. Verify Result Daily

- Buka dashboard cron-job.org → history tab
- Lihat job sudah executed daily
- Cek `/api/health` endpoint: `pending_count` akan turun dari 541 ke 0

---

## Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Status + pending count |
| `/api/cron/indexing?token=beriklan-admin-2026` | POST | Trigger daily indexing |

---

## What it does

Daily:
1. Reads up to 200 pending URLs dari D1 (`pending_indexing` table)
2. Submits ke **Google Indexing API** (quota 200/day, will queue)
3. Submits ke **IndexNow** (Bing + Seznam + Naver)
4. Logs result ke `cron_logs` table
5. Updates status `submitted` untuk URLs yang berhasil

---

## Known Issues

1. **Google JWT signing fails** in CF Worker (need RSA-PSS debugging)
   - Workaround: IndexNow submission tetap berjalan
   - Google akan tetap crawl via IndexNow → Bing → Google
2. **Seznam/Naver 422** — URL validation issue (sedang diteliti)

---

## Monitoring

- Dashboard: https://cron-job.org → history
- CF Worker logs: https://dash.cloudflare.com → Workers → beriklanweb → Logs
- D1 queries: `wrangler d1 execute beriklan-seo --remote --command "SELECT * FROM cron_logs ORDER BY timestamp DESC LIMIT 5"`
