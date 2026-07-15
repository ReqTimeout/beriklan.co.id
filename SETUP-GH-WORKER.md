# Setup GitHub PAT + Worker v2 (0 Server, 0 Billing)

> Cloudflare Worker otomatis modify `posts-meta.json` via GitHub API.
> Tidak perlu GitHub Actions, tidak perlu SSH/cPanel Hostinger.
> Hanya butuh GitHub PAT + Cloudflare Worker (keduanya free).

---

## Cara Kerja

```
Cron: 06:00 & 18:00 UTC
        ↓
Cloudflare Worker
   ├─ Fetch sitemap → IndexNow (Bing + Seznam)
   ├─ Ping Google/Bing/Yandex
   └─ GitHub API: GET posts-meta.json → update 20 random date → PUT back
        ↓
GitHub trigger Cloudflare Pages deploy (auto)
```

---

## Step 1: Bikin GitHub Personal Access Token (PAT)

1. Buka **https://github.com/settings/tokens/new**
2. Isi:
   - **Token name**: `foroutour-seo-cron`
   - **Expiration**: `No expiration` (atau 1 tahun)
   - **Scopes**: centang **`repo`** (Full control of private repositories)
3. Klik **Generate token**
4. **Copy token** (muncul sekali, gak akan muncul lagi)

Format token: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## Step 2: Set Token di Worker

```bash
cd ~/Desktop/foryoutour/cloudflare-cron

# Set GH_TOKEN sebagai secret (encrypted di Cloudflare)
echo "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" | npx wrangler secret put GH_TOKEN

# Verify
npx wrangler secret list
```

---

## Step 3: Deploy Worker Baru

```bash
npx wrangler deploy
```

Output:
```
Uploaded foryoutour-seo-cron (1.50 sec)
Deployed foryoutour-seo-cron triggers (1.20 sec)
  https://foryoutour-seo-cron.3smedianet.workers.dev
  schedule: 0 6 * * *
  schedule: 0 18 * * *
```

---

## Step 4: Test Manual

```bash
# Trigger via fetch
curl https://foryoutour-seo-cron.3smedianet.workers.dev | python3 -m json.tool
```

Expected output (bagian `tasks`):
```json
{
  "task": "Posts-meta Freshness (20 articles)",
  "updated": 20,
  "date": "2026-07-08",
  "commit": "abc1234",
  "indexnow": 20
}
```

Kalau `updated: 0` dan `error: "GH_TOKEN missing"` → token belum di-set. Ulangi Step 2.

---

## Yang Terjadi Tiap Cron Run

| Aksi | Lokasi | Tujuan |
|------|--------|--------|
| Fetch semua URL dari sitemap | Worker | IndexNow batch |
| Submit ke Bing + Seznam | IndexNow API | Indexing cepat |
| Ping Google/Bing/Yandex | HTTP GET | Beri tahu sitemap update |
| **GET posts-meta.json** | GitHub API | Read 5MB metadata |
| **Update date 20 artikel** | Worker | Freshness signal |
| **PUT posts-meta.json** | GitHub API | Commit balik |
| **Cloudflare Pages auto-deploy** | Cloudflare | Update sitemap lastmod |

Total: **2 run/hari × 30 hari = 60 GitHub API calls** dari 5000/hour limit ✅

---

## Triggers

| Cron | Waktu (UTC) | Aksi |
|------|-------------|------|
| `0 6 * * *` | 06:00 UTC | IndexNow + ping + freshness 20 articles |
| `0 18 * * *` | 18:00 UTC | IndexNow + ping + freshness 20 articles |

**Net effect**: 40 artikel di-fresh per hari, 2x ping per hari, 1 commit per run.

---

## Token Security

- Token disimpan di **Cloudflare Workers Secrets** (encrypted at rest)
- Tidak ada di `wrangler.toml` atau git
- Hanya bisa dilihat via `wrangler secret list`
- Untuk rotate: bikin PAT baru, update secret

```bash
# Rotate token
echo "ghp_NEW_TOKEN_HERE" | npx wrangler secret put GH_TOKEN
npx wrangler deploy
```

---

## FAQ

### Q: Kenapa `posts-meta.json` bukan `posts.json`?
A: posts.json 94 MB → base64 encode + decode + JSON parse di Worker makan waktu lama. posts-meta.json cuma 5 MB → Worker selesai dalam <5 detik.

### Q: Kenapa cuma update date, bukan swap content?
A: posts-meta.json tidak punya field `content`. Untuk swap enrichment, perlu modify posts.json (94 MB) — terlalu besar untuk Worker. Pakai `python3 scripts/freshness.py` di Mac (atau via cPanel cron) untuk swap content.

### Q: Apa cukup update date aja untuk freshness signal?
A: Google liat `<lastmod>` di sitemap. Update date = trigger re-crawl. Plus IndexNow batch = hampir real-time indexing.

### Q: Bisa ditambah rotate links & keyword research?
A: Butuh modify posts.json (94 MB). Worker punya CPU limit 30s untuk scheduled event. Mungkin muat, tapi risky. Lebih aman handle di Mac/cPanel.

---

## Uninstall

```bash
# Hapus secret
npx wrangler secret delete GH_TOKEN

# Hapus worker
npx wrangler delete
```

---

## Monitoring

Cek log worker di Cloudflare dashboard:
- https://dash.cloudflare.com → Workers & Pages → foryoutour-seo-cron → Logs

Atau trigger manual dan lihat response:
```bash
curl https://foryoutour-seo-cron.3smedianet.workers.dev | python3 -m json.tool
```
