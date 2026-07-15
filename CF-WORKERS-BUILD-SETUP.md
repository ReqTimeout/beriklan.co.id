# CF Workers Build Integration — Setup Guide

> Auto-deploy setiap push ke GitHub. Tidak butuh wrangler deploy manual.

---

## Kenapa perlu setup ini?

Saat ini, deploy harus manual dengan `npx wrangler deploy`. Setup CF Workers Build
memungkinkan push ke GitHub → CF otomatis build + deploy. Hemat waktu dan mengurangi
kesalahan manusia.

---

## Step-by-step Setup (5-10 menit)

### 1. Buka CF Dashboard

Pergi ke: https://dash.cloudflare.com → **Workers & Pages** → klik worker **`beriklanweb`**

### 2. Pilih tab Settings

Klik tab **Settings** di top navigation worker.

### 3. Scroll ke bagian "Build"

Cari section **"Build"** atau **"Deploys"** → klik **"Connect GitHub"** (atau "+ Add" jika sudah pernah connect).

### 4. Authorize GitHub

- Pilih **"GitHub"** sebagai provider
- Klik **"Connect GitHub"** → akan redirect ke github.com
- Authorize CF GitHub App (`cloudflare-workers-and-pages`)
- Pilih akun **ReqTimeout**
- Pilih **All repositories** atau specific: **beriklan.co.id**
- Klik **"Install & Authorize"**

### 5. Configure Build

Setelah authorize, kembali ke CF Dashboard. Pilih:
- **Repository:** `ReqTimeout/beriklan.co.id`
- **Branch:** `main`
- **Build command:**
  ```bash
  npm install && npm run build
  ```
- **Build output directory:** `dist`
- **Deploy command:** (kosongkan, default auto-deploy)
- **Compatibility date:** (biarkan auto, atau set `2026-01-01`)
- **Compatibility flags:** (kosongkan)

### 6. Save & Test

- Klik **"Save and Deploy"**
- Tunggu ~2-3 menit untuk first build
- Cek tab **Deploys** di worker → akan ada entry baru dengan status success

---

## Verifikasi

Setelah setup, setiap push ke `main` di GitHub akan auto-deploy dalam ~2-3 menit.

Test:
1. Push perubahan kecil ke repo
2. Buka CF Dashboard → Workers → `beriklanweb` → tab **Deploys**
3. Akan muncul entry baru dengan commit hash
4. Cek live URL: `https://beriklan.co.id/path`

---

## Troubleshooting

| Problem | Solusi |
|---------|--------|
| "No compatible build" error | Pastikan build command benar: `npm install && npm run build` |
| Build fails with "Cannot find module" | Cek Node version di CF — set ke 20+ di settings |
| Deploy succeeds tapi assets tidak update | Hard refresh browser (Ctrl+Shift+R) — CF cache |
| GitHub push tidak trigger build | Pastikan webhook aktif di GitHub repo settings → Webhooks |
| Worker tidak ada di tab Builds | Worker harus tipe **Workers** (bukan Pages) — saat ini `beriklanweb` adalah Workers ✅ |

---

## Alternative Path (jika dashboard tidak bisa)

Kalau CF Workers Build tidak bisa di-setup (misal token limit atau restricted account),
fallback ke **local wrangler deploy** dengan script automation:

```bash
# Di Mac user, tambahkan ke crontab:
*/5 * * * * cd /Users/maabook/Desktop/beriklan.co.id && \
  git pull && cd web && \
  npm install --silent && npm run build 2>&1 && \
  CLOUDFLARE_API_TOKEN="cfut_LRmk..." \
  CLOUDFLARE_ACCOUNT_ID="766dfffa7e5dcd8ba246ebfa60bc10ba" \
  npx wrangler deploy
```

Setup:
1. `crontab -e`
2. Tambah line di atas
3. Save → auto-deploy setiap 5 menit kalau ada perubahan Git

---

## Status saat ini (15 Jul 2026)

| Item | Status |
|------|--------|
| Account-scoped CF token `cfut_LR...` | ✅ Ready |
| GH Secret `CLOUDFLARE_API_TOKEN` | ✅ Set |
| GH Secret `CLOUDFLARE_ACCOUNT_ID` | ✅ Set |
| `web/.github/workflows/00-deploy.yml` | ✅ Configured |
| GH Action runs | ❌ Runner unavailable (3s instant failure) |
| CF Workers Build integration | ⏳ **Need user manual setup** (5-10 min) |
| Local `wrangler deploy` | ✅ Working (manual) |
| Last deploy | `c1dcba11-c24b-4a53-aaee-6bd2bd2ad1a8` |