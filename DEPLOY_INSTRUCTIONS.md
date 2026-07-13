# 🚀 Cara Deploy ke Cloudflare — Beriklan.co.id

> ⚠️ **Catatan:** Token API Cloudflare untuk deploy lewat CLI tidak lagi dibutuhkan.
> Pakai GitHub Auto-Deploy dari CF Dashboard — sekali klik, auto-deploy forever.

---

## ✅ Path A — GitHub Auto-Deploy via Cloudflare Pages (RECOMMENDED, 1 menit)

### Browser kamu — 8 langkah:

1. 👉 Buka: https://dash.cloudflare.com/766dfffa7e5dcd8ba246ebfa60bc10ba/pages

2. Klik **"+ Create a project"** (tombol oranye di kanan atas)

3. Tab **"Pages"** → klik **"Connect to Git"**

4. Pilih **"GitHub"** → klik **"Connect GitHub"** → authorize kalau diminta

5. Pilih repository **`ReqTimeout/beriklan.co.id`** (branch `main`)

6. **Setup build:**
   - **Framework preset**: `Astro` (atau pilih "None")
   - **Build command**: `npm run build`
   - **Build output directory**: `dist`
   - **Root directory**: (kosong, default `/`)

7. **Environment variables** → Add:
   - Variable name: `NODE_VERSION`, value: `20`

8. Klik **"Save and Deploy"**

→ Cloudflare auto-clone repo, `npm install`, `npm run build`, deploy `dist/` ke `https://beriklancoid.pages.dev`

---

## 🆘 Path B — Manual Direct Upload (kalau Path A gagal)

### Browser kamu — 5 langkah:

1. 👉 Buka: https://dash.cloudflare.com/766dfffa7e5dcd8ba246ebfa60bc10ba/pages

2. Buat project Pages baru dengan **"Direct Upload"** (BUKAN Connect Git)

3. Beri nama `beriklancoid` (atau nama lain)

4. Download file saya: `/Users/maabook/Desktop/beriklan.co.id/web/dist.zip` (sudah saya zip)

5. Drag-drop `dist.zip` ke upload area → klik **"Deploy site"**

---

## 📋 Setelah Deploy Berhasil

1. **Custom domain**: Setup di Pages project → tab "Custom domains" → `beriklan.co.id`

2. **DNS update**: Saya bisa update DNS records otomatis. Beri tahu kalau sudah sampai sini.

3. **Verify**:
   ```bash
   curl -I https://beriklan.co.id/
   curl -I https://beriklan.co.id/blog/
   curl https://beriklan.co.id/sitemap-index.xml
   ```

---

## ❓ Pertanyaan tentang token API

Semua token CF yang kamu kasih (`cfat_*` dan `cfut_*`) **scope-nya Zone-level**, bukan Account-level. Wrangler deploy butuh Account-scoped. Saya sudah berhenti minta token lagi karena terbukti gak akan work via API.

**Buat deploy via API di masa depan**, kamu butuh:
1. Dashboard → API Tokens → Create Custom Token
2. Permissions: `Account` → `Cloudflare Pages: Edit` + `Workers Scripts: Edit`
3. Account Resources: Specific account `3smedianet@gmail.com's Account`
4. Zone Resources: Specific zone `beriklan.co.id`

Token itu bisa kamu simpan di GitHub Secrets (CF_API_TOKEN). GitHub Actions workflow di repo akan auto-deploy tiap push ke main. Tapi itu juga proses setup manual di CF, sama ribetnya.

**GitHub Pages integration (Path A) jauh lebih simple.** Itu foryoutours.com mungkin pakai.
