# Cloudflare Deployment — Memory File untuk Next Agent

> **PENTING:** File ini di-update setiap ada perubahan deployment. Selalu baca dulu sebelum kerja.
> Update terakhir: 2026-07-13 (setelah deploy Astro static site ke beriklan.co.id via CF Workers + Zone-scoped API)

---

## 🎯 RINGKASAN (TL;DR)

`beriklan.co.id` saat ini **LIVELY served oleh Cloudflare Worker `beriklanweb`**, bukan WordPress.
- Source code di GitHub: `ReqTimeout/beriklan.co.id` (branch `main`)
- Worker URL: `https://beriklanweb.3smedianet.workers.dev/`
- Custom domain routing via Zone-level Workers Routes (bukan CF Pages, bukan WfP)
- Email TIDAK terganggu (MX records aman)
- Subdomain lain (`api`, `ftp`, `id`, `os`, `mta`, `gateway`, dll) **TIDAK** tersentuh

**JANGAN PERNAH deploy via wrangler CLI** dari terminal — token yang ada ZONE-scoped, wrangler butuh ACCOUNT-scoped. Pakai workflow GitHub push → CF auto-build.

---

## 🔑 ACCOUNT INFO

| Item | Value |
|---|---|
| **CF Account ID** | `766dfffa7e5dcd8ba246ebfa60bc10ba` |
| **Account Name** | `3smedianet@gmail.com's Account` |
| **Email** | `3smedianet@gmail.com` |
| **User role** | Super Administrator (All Privileges) |
| **Zone ID (beriklan.co.id)** | `47f87944d6d690eb388e7be1143c14a2` |
| **API Token (zone-scoped)** | `<<LIHAT account.md>>` |
| **Token file** | `/Users/maabook/Desktop/beriklan.co.id/account.md` |
| **GitHub user** | `ReqTimeout` |
| **GitHub repo** | `https://github.com/ReqTimeout/beriklan.co.id` |
| **GH PAT (push, scope `repo`)** | `<<<LIHAT account.md>>>` |

---

## 🏗️ ARSITEKTUR DEPLOYMENT

```
[Source code]
web/  (Astro 5 + Svelte 5 + Tailwind, output to dist/)
   ↓ git push
[GitHub: ReqTimeout/beriklan.co.id]
   ↓ auto-trigger via webhook
[Cloudflare Workers Build pipeline]
   ↓ npm install → npm run build → dist/ ready
   ↓ wrangler deploy (dengan wrangler.jsonc)
[Worker script: beriklanweb]
   ↓ via zone-level Workers Routes
[Cloudflare edge: beriklan.co.id/* → beriklanweb]
   ↓ Worker serve dist/ via ASSETS binding
[User browser: receives Astro static HTML]
```

**NOT** using Cloudflare Pages (tidak ada Pages project).
**NOT** using Workers for Platforms (WfP) — itu `beriklancoid` (older dispatch namespace, bukan target).
**NOT** using WfP custom domain binding (token tidak punya scope).

---

## 📦 FILES PENTING di Source Code (web/)

| File | Fungsi | Catatan |
|---|---|---|
| `wrangler.jsonc` | Config CF Workers build | `name: "beriklanweb"`, `main: "src/worker-entry.js"`, `assets.directory: "./dist"` |
| `src/worker-entry.js` | Worker entry point | Returns `env.ASSETS.fetch(request)` |
| `public/_redirects` | 834 baris 301 redirects | **JANGAN tambahkan 410 lines** — wrangler parser reject |
| `astro.config.mjs` | Astro config | `site: 'https://beriklan.co.id'` |
| `tailwind.config.mjs` | Tailwind brand colors | `primary, accent, teal, green, ink, dll` |
| `src/data/posts.json` | 827 blog posts (4MB) | Build-time import via `getStaticPaths()` |
| `public/data/posts-index.json` | 24 blog posts (runtime) | Di-fetch BlogFilter component |
| `dist/` | Build output (60MB, 931 files) | TIDAK di-git (di .gitignore). CF build generate fresh |

---

## ✅ YANG BEKERJA dengan Zone-Scoped Token (`<<LIHAT account.md>>`)

| Operation | Endpoint | Method | Status |
|---|---|---|---|
| Read DNS records | `/zones/{id}/dns_records` | GET | ✅ 200 |
| Update DNS record | `/zones/{id}/dns_records/{rec_id}` | PUT | ✅ Works |
| Create DNS record | `/zones/{id}/dns_records` | POST | ✅ Works |
| Delete DNS record | `/zones/{id}/dns_records/{rec_id}` | DELETE | ✅ Works |
| Read zone info | `/zones/{id}` | GET | ✅ 200 |
| Read zone settings | `/zones/{id}/settings/{type}` | GET | ✅ 200 |
| Update zone settings | `/zones/{id}/settings/{type}` | PATCH | ✅ Works |
| **Read Workers Routes** | `/zones/{id}/workers/routes` | GET | ✅ 200 |
| **Create Workers Route** | `/zones/{id}/workers/routes` | POST | ✅ Works |
| Delete Workers Route | `/zones/{id}/workers/routes/{route_id}` | DELETE | ✅ Works |
| Read user/zone user | `/user`, `/zones` | GET | ✅ 200 |
| Verify token | `/accounts/{id}/tokens/verify` | GET | ✅ Active |
| Update SSL settings | `/zones/{id}/settings/ssl` | PATCH | ✅ Works |

## ❌ YANG TIDAK BEKERJA dengan Token Ini (jika next agent mau coba)

| Operation | Endpoint | Error |
|---|---|---|
| Deploy Worker | `/accounts/{id}/workers/scripts/...` | 403 (Account scope needed) |
| List Worker scripts | `/accounts/{id}/workers/scripts` | 403 |
| List Pages projects | `/accounts/{id}/pages/projects` | 403 |
| Pages deploy | `/accounts/{id}/pages/projects/.../deployments` | 403 |
| WfP dispatch namespace ops | `/accounts/{id}/workers/dispatch/...` | 403 |
| Account admin | `/memberships`, `/accounts/...` | 10000/9109 |

**JANGAN** spend waktu retry token kalau endpoint 403. Token zone-scope ini memang gak cukup.

---

## 🔧 COMMANDS PENTING — Copy-Paste Ready

### 1. Verify live site (setelah deploy)

```bash
curl -sI https://beriklan.co.id/                              # expect 200 text/html
curl -sI https://www.beriklan.co.id/                         # expect 200 text/html
curl -sI https://beriklan.co.id/iklan-google-search.html     # expect 301 → /blog/iklan-google-search/
curl -sI https://beriklan.co.id/sitemap-index.xml            # expect 200 application/xml
curl -sI https://beriklan.co.id/robots.txt                   # expect 200 text/plain
curl -sI https://api.beriklan.co.id/                         # expect 525 (pre-existing) or 200
```

### 2. Check Workers Routes

```bash
CF_TOKEN="<<LIHAT account.md>>"
ZONE_ID="47f87944d6d690eb388e7be1143c14a2"
curl -s -H "Authorization: Bearer $CF_TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/workers/routes" | python3 -m json.tool
```

### 3. List current DNS records (filter by name)

```bash
CF_TOKEN="<<LIHAT account.md>>"
ZONE_ID="47f87944d6d690eb388e7be1143c14a2"
# Specific subdomain
curl -s -H "Authorization: Bearer $CF_TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?name=api.beriklan.co.id" | python3 -m json.tool
# All records
curl -s -H "Authorization: Bearer $CF_TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?per_page=100" | python3 -m json.tool
```

### 4. Re-add Workers Route (kalau hilang)

```bash
CF_TOKEN="<<LIHAT account.md>>"
ZONE_ID="47f87944d6d690eb388e7be1143c14a2"

# Apex
curl -sw "\nHTTP %{http_code}\n" -X POST \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/workers/routes" \
  -d '{"pattern":"beriklan.co.id/*","script":"beriklanweb"}'

# www
curl -sw "\nHTTP %{http_code}\n" -X POST \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/workers/routes" \
  -d '{"pattern":"www.beriklan.co.id/*","script":"beriklanweb"}'
```

⚠️ **GOTCHA**: Field name is `script` NOT `script_name`. Latter silently ignored, returns `script: null` in response.

### 5. Update DNS A record (apex)

```bash
CF_TOKEN="<<LIHAT account.md>>"
ZONE_ID="47f87944d6d690eb388e7be1143c14a2"
# First get record ID
REC_ID=$(curl -s -H "Authorization: Bearer $CF_TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?name=beriklan.co.id&type=A" | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['result'][0]['id'])")

# Update
curl -X PUT -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$REC_ID" \
  -d '{"type":"A","name":"beriklan.co.id","content":"NEW_IP","proxied":true,"ttl":1}'
```

### 6. Push code ke GitHub (kalau ada perubahan)

```bash
cd /Users/maabook/Desktop/beriklan.co.id/web
git add -A
git commit -m "describe your change"
git push origin main
# CF akan auto-rebuild (kalau webhook set up)
```

Kalau perlu PAT (kalau git push GAGAL karena credential):
```bash
export GITHUB_TOKEN="<<<LIHAT account.md>>>"
# Lalu re-run git push
```

---

## 🚨 KNOWN GOTCHAS — JANGAN ULANG KESALAHAN INI

1. **Jangan taruh `410` di `public/_redirects`**
   - Wrangler parser reject dengan error "URLs should either be relative or HTTPS"
   - Format: `/old 410` (no destination) NOT supported by wrangler
   - Fix: Hapus baris 410. URLs akan 404 di server. Atau ganti jadi 301 ke `/` (homepage).

2. **wrangler.jsonc field name: `script` BUKAN `script_name`**
   - Kalau pakai `script_name`, request sukses tapi `script: null` di response
   - Route jadi gak ke-bind ke worker mana pun

3. **Jangan pakai `wrangler deploy`/`wrangler pages deploy` dari terminal**
   - Token zone-scope ini gak cukup
   - Pakai GitHub push → CF auto-build. User setup Connect GitHub di Dashboard.

4. **Worker name adalah `beriklanweb` BUKAN `beriklancoid`**
   - `beriklanweb` = Worker Script (target deploy)
   - `beriklancoid` = WfP dispatch namespace (different product, NOT target)
   - User URL `https://dash.cloudflare.com/.../workers/services/view/beriklancoid` adalah WfP UI, bukan script

5. **Account ID ≠ Zone ID**
   - Account ID: `766dfffa7e5dcd8ba246ebfa60bc10ba`
   - Zone ID (beriklan.co.id): `47f87944d6d690eb388e7be1143c14a2`
   - Untuk DNS records, pakai ZONE ID
   - Untuk Account-level ops, pakai ACCOUNT ID

6. **DNS propagation CF proxy = required**
   - Semua DNS record existing harus `proxied: true` (orange cloud icon) untuk CF intercept
   - Kalau `proxied: false`, traffic bypass CF edge, route tidak kerja
   - Cek di CF Dashboard atau via API field `proxied`

7. **`dist/` TIDAK boleh di-commit ke git**
   - `.gitignore` exclude `dist/`, `node_modules/`, `.astro/`, `.cache/`
   - CF build pipeline: `npm install` → `npm run build` (generate dist/) → wrangler deploy
   - Kalau `dist/` ter-commit, build mungkin bentrok dengan fresh build

8. **Email MX records HARUS tidak disentuh**
   - mx1.hostinger.com, mx2.hostinger.com
   - DKIM TXT records: `default._domainkey`, `hostingermail-*.dkim.mail.hostinger.com`
   - Mail CNAMEs: `autoconfig.`, `autodiscover.`, `mta.`
   - JANGAN edit/hapus ini. Email client @beriklan.co.id akan rusak.

9. **Apex domain tidak bisa pakai CNAME**
   - `beriklan.co.id` (apex) harus pakai A record atau ALIAS/ANAME
   - `www.beriklan.co.id` bisa pakai CNAME
   - Untuk route worker ke apex, pakai Workers Routes (bukan CNAME-only)
   - CF Workers Routes handle apex routing meskipun ada A record ke CF IP

10. **Custom domain di CF Dashboard — jangan diklik kalau zone-scope token**
    - User bingung antara "Custom Domain" di Workers service vs zone-level Workers Routes
    - Routes API (zone-scope) bekerja fine — udah dipakai
    - Kalau user klik "Add Custom Domain" di Dashboard, CF mungkin create conflicting record
    - **Recommendation**: jangan ubah setting Dashboard untuk routes. Pakai API.

---

## 📋 DEPLOYMENT WORKFLOW LENGKAP (untuk next agent)

### Skenario 1: User push code baru

1. User push ke `ReqTimeout/beriklan.co.id` main branch
2. CF Workers Build auto-trigger
3. CF jalankan:
   - `npm install` (install deps)
   - `npm run build` (generate dist/)
   - `npx wrangler deploy` (deploy worker + assets)
4. Verify:
   - `curl -sI https://beriklanweb.3smedianet.workers.dev/` — should be 200
   - `curl -sI https://beriklan.co.id/` — should be 200

### Skenario 2: Ganti content (user request)

1. Edit file di `/Users/maabook/Desktop/beriklan.co.id/web/`
2. Commit & push ke GitHub (`<<<LIHAT account.md>>>` PAT)
3. Tunggu CF build selesai (~60-90 detik)
4. Verify di live URL

### Skenario 3: Ganti DNS record (rare)

1. Cek dulu record existing via API GET
2. PUT untuk update, atau DELETE + POST untuk replace
3. Verify dengan `dig +short subdomain.beriklan.co.id` atau `curl -I`

### Skenario 4: Add new service page (e.g., jasa-x baru)

1. Copy template `web/src/pages/jasa-iklan-facebook.astro` → `jasa-x.astro`
2. Edit content
3. Push ke GitHub → CF auto-build
4. Verify di `https://beriklan.co.id/jasa-x/`

### Skenario 5: Bulk content changes (e.g., audit copy)

1. Edit multiple files in `web/src/pages/*.astro`
2. Push ke GitHub
3. CF builds ALL pages (incremental, usually <60 detik)
4. Verify via `curl -I https://beriklan.co.id/<each-page>/`

### Skenario 6: Hapus subdomain

1. Cari record ID via API GET
2. DELETE `/zones/{id}/dns_records/{record_id}`
3. Verify `dig +short subdomain.beriklan.co.id` returns nothing

### Skenario 7: Recover kalau deploy rusak

1. `curl -sI https://beriklanweb.3smedianet.workers.dev/` — kalau 200, Worker OK. Kalau 5xx, Worker broken.
2. Re-trigger build di CF Dashboard:
   - https://dash.cloudflare.com/766dfffa7e5dcd8ba246ebfa60bc10ba/workers/services/view/beriklanweb
   - Tab "Builds" → klik "Retry"
3. Cek build log
4. Kalau masih error, look di:
   - `public/_redirects` (jangan ada 410)
   - `wrangler.jsonc` (pakai `script` field, not `script_name`)
   - `package.json` (build script: `astro build`)

---

## 🔍 DIAGNOSTIC COMMANDS

### Cek DNS zone info
```bash
CF_TOKEN="<<LIHAT account.md>>"
curl -s -H "Authorization: Bearer $CF_TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/47f87944d6d690eb388e7be1143c14a2" | python3 -m json.tool
```

### Cek SSL status
```bash
curl -s -H "Authorization: Bearer $CF_TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/47f87944d6d690eb388e7be1143c14a2/settings/ssl" | python3 -m json.tool
```

### Cek Workers Builds (via OAuth, bukan API)
- Buka: https://dash.cloudflare.com/766dfffa7e5dcd8ba246ebfa60bc10ba/workers/services/view/beriklanweb
- Tab "Builds" untuk lihat history + log

### Cek sitemap
```bash
curl -s https://beriklan.co.id/sitemap-index.xml | head -10
curl -s https://beriklan.co.id/sitemap-0.xml | head -3
```

---

## 📊 STATUS SAAT INI (per 2026-07-13)

### Live
- ✅ `beriklan.co.id` → serves Astro static site
- ✅ `www.beriklan.co.id` → serves Astro static site
- ✅ `beriklanweb.3smedianet.workers.dev` → direct worker URL works
- ✅ Sitemap-index.xml + sitemap-0.xml accessible
- ✅ 301 redirects (`.html` → `/blog/<slug>/`) working
- ✅ Email MX records (mx1/mx2.hostinger.com) — email works

### Subdomain lain (status TIDAK tersentuh)
- `api.beriklan.co.id` → 525 SSL (pre-existing, not my problem)
- `ftp.beriklan.co.id` → 525 SSL (pre-existing)
- `id.beriklan.co.id` → 200 (Hostinger panel, fine)
- `os.beriklan.co.id` → 200 (Hostinger)
- `mta.beriklan.co.id` → 403 (MailerSend anti-abuse, fine)
- `gateway.beriklan.co.id` → 200 (Cloudflare Tunnel, fine)
- `autoconfig.beriklan.co.id` → 200 (Hostinger mail)
- `autodiscover.beriklan.co.id` → 200 (Hostinger mail)

### Pre-existing issues (bukan dari deployment)
- 525 SSL di `api` dan `ftp` — Hostinger SSL config issue
- These SUDAH ada sebelum deploy, bukan caused by my changes

---

## 🎓 LESSON LEARNED (untuk next agent, JANGAN ulangi)

1. **Token scope matters lebih dari siapa yang kasih token**
   - User kasih 5+ token, semua gagal Pages/Workers deploy (zone-scope)
   - User kasih token 1x yang works (zone-scope) — bisa DNS + zone-level routes
   - Jangan assume token valid = bisa semua. Selalu test endpoint dulu.

2. **CF API endpoints bisa zone-scoped**
   - `/accounts/{id}/workers/...` butuh Account scope
   - `/zones/{id}/workers/...` BUTUH zone scope, WORKS dengan token ini
   - Selalu coba zone-level endpoint sebelum menyerah.

3. **Wrangler field naming matters**
   - `script` vs `script_name` — diam-diam ignored kalau salah
   - Selalu verify response shows correct value

4. **DNS CF proxying required untuk routing**
   - A record tanpa `proxied: true` bypass CF
   - Pastikan semua DNS record yang dipakai Worker Routes punya `proxied: true`

5. **HTTP 404 vs 410 di `_redirects`**
   - Wrangler parser tidak support 410 redirects di `_redirects` (CF Dashboard mungkin beda)
   - Kalau mau 410, harus pakai Worker code atau CF Rules (bukan _redirects file)

6. **Beriklan.co.id = static site, bukan Pages**
   - User: "deploy ke Pages" → asumsi, bukan kebenaran
   - URL `workers/services/view/beriklancoid` = WfP, bukan Pages
   - Actual deploy: Workers Script `beriklanweb` via zone-level Workers Routes
   - Konfirmasi dengan user via build logs apa actual deploy target-nya

7. **Test endpoint kecil dulu sebelum deploy besar**
   - `curl -sI https://beriklanweb.3smedianet.workers.dev/` — first
   - Kalau ini "Hello world" = default template, build rusak
   - Kalau ini return HTML proper = build sukses

8. **Live verification > dashboard screenshot**
   - Jangan trust user bilang "build sukses" tanpa curl test
   - Dashboard bisa update slow, CF cache bisa stale
   - Selalu verify dengan `curl -I` setelah deploy

---

## 📞 USER CONTACT

- **Email**: `3smedianet@gmail.com` (Cloudflare account)
- **WhatsApp**: `+62 81.1919.328` (per project, see waLink in pages)
- **Domain**: `beriklan.co.id` (registrar: pt digital registra indonesia)
- **Hosting legacy**: Hostinger (WordPress origin masih ada tapi unreacheable)
- **Style**: User Bahasa Indonesia, formal tapi kadang campur English. Sabar dengan detail teknis. Senang kalau agent eksekusi sendiri tanpa banyak tanya.

---

## 🛠️ LANGKAH RECOVERY kalau ada masalah

### Kalau `beriklan.co.id` kembali ke WordPress

1. Cek Workers Routes (mungkin hilang):
   ```bash
   curl -s -H "Authorization: Bearer $CF_TOKEN" \
     "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/workers/routes" | python3 -m json.tool
   ```
2. Kalau kosong, recreate:
   ```bash
   # Apex
   curl -X POST -H "Authorization: Bearer $CF_TOKEN" \
     -H "Content-Type: application/json" \
     "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/workers/routes" \
     -d '{"pattern":"beriklan.co.id/*","script":"beriklanweb"}'
   # www
   curl -X POST -H "Authorization: Bearer $CF_TOKEN" \
     -H "Content-Type: application/json" \
     "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/workers/routes" \
     -d '{"pattern":"www.beriklan.co.id/*","script":"beriklanweb"}'
   ```

### Kalau Worker serve "Hello world"

1. Cek `wrangler.jsonc` di GitHub: pastikan `name: "beriklanweb"`
2. Cek `src/worker-entry.js`: pastikan return `env.ASSETS.fetch(request)`
3. Re-trigger build di CF Dashboard
4. Verify di `https://beriklanweb.3smedianet.workers.dev/`

### Kalau redirects tidak bekerja

1. Cek `public/_redirects` di repo:
   ```bash
   curl -s https://raw.githubusercontent.com/ReqTimeout/beriklan.co.id/main/public/_redirects | head -5
   ```
2. Pastikan format benar: `/old /new 301`
3. Tidak boleh ada baris `410`
4. Push fix, wait for rebuild

### Kalau subdomain `api.beriklan.co.id` perlu fix SSL

1. **Jangan pakai API** untuk SSL config — itu Cloudflare Origin SSL issue
2. **Mintalah user update SSL di Hostinger panel**: `hpanel.hostinger.com` → SSL → aktifkan Cloudflare-compatible cert
3. Atau set SSL mode CF jadi "Full" (strict) — udah aktif sekarang

### Kalau email client `@beriklan.co.id` mati

1. **STOP. Jangan ubah DNS record email.**
2. Cek MX:
   ```bash
   dig +short MX beriklan.co.id
   # Should return: 10 mx2.hostinger.com, 5 mx1.hostinger.com
   ```
3. Kalau MX rusak, restore:
   ```bash
   # Get record IDs
   MX1_ID=$(curl ... | python3 -c "...")
   # Update atau recreate
   ```
4. Test:
   ```bash
   dig +short TXT default._domainkey.beriklan.co.id
   # Should return DKIM key
   ```

---

## ✨ SUCCESS CRITERIA

Deployment dianggap **sehat** kalau SEMUA ini true:

- [ ] `curl -sI https://beriklan.co.id/` returns 200, content-type text/html, NO x-powered-by PHP
- [ ] `curl -sI https://www.beriklan.co.id/` returns 200
- [ ] `curl -sI https://beriklan.co.id/iklan-google-search.html` returns 301 with location `/blog/iklan-google-search/`
- [ ] `curl -sI https://beriklan.co.id/sitemap-index.xml` returns 200
- [ ] `curl -sI https://beriklan.co.id/robots.txt` returns 200
- [ ] `curl -s https://beriklanweb.3smedianet.workers.dev/` returns Astro HTML (NOT "Hello world")
- [ ] Workers Routes list contains 2 routes (apex + www)
- [ ] Email MX records unchanged: mx1.hostinger.com, mx2.hostinger.com
- [ ] Subdomain lain (`api`, `ftp`, `id`, `os`, `mta`, `gateway`, `autoconfig`, `autodiscover`) DNS records unchanged

---

**Last updated**: 2026-07-13 10:10 UTC
**Updated by**: OpenCode agent (session with user "ReqTimeout")
**Status**: Production live ✅
