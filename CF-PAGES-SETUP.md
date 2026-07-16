# CF Pages Setup — Status (15 Jul 2026)

## Current State

| Resource | Status | URL |
|----------|--------|-----|
| **CF Pages project** | ✅ Created (Direct Upload mode) | `beriklanweb.pages.dev` |
| **Pages subdomain** | ✅ Active | https://beriklanweb.pages.dev |
| **Pages deploys** | ✅ Working (1 production deploy) | https://d6120e8d.beriklanweb.pages.dev |
| **Production site** | ✅ Worker (unchanged) | https://www.beriklan.co.id |
| **GitHub connection** | ❌ Pending user (5 min OAuth flow) | - |
| **Custom domain** | ❌ Pending (DNS CNAME issue with apex) | - |

## What works NOW (no user action needed)

- `https://beriklanweb.pages.dev/` → serves latest beriklan.co.id build
- `/jasa-iklan-facebook/`, `/blog/xi-jinping/`, etc. → all 200 OK
- Pages project accepts direct upload via `wrangler pages deploy`

## What needs user action (5 min)

### Setup GitHub connection (so push auto-deploys)

1. Buka https://dash.cloudflare.com → **Workers & Pages** → klik **beriklanweb** project
2. Klik **Settings** tab → **Builds** section
3. Klik **"Connect to Git"** → **GitHub**
4. Authorize **cloudflare** GitHub App
5. Pilih:
   - Repository: `ReqTimeout/beriklan.co.id`
   - Branch: `main`
6. **Save and Deploy** (first deploy: ~3-5 min)

### Future: migrate production from Worker to Pages

⚠️ **NOT recommended now.** The WordPress origin on Hostinger redirects beriklan.co.id to www subdomain (still 301 redirect with `x-redirect-by: WordPress` header). This indicates origin routing setup that needs cleanup.

For now: keep both — Worker serves production, Pages serves preview/backup.

If user wants to migrate fully:
1. Contact Hostinger support to remove WordPress redirect
2. Or set up CF Pages custom domain with apex handling
3. Switch DNS records (A record apex → CF Pages IP)

## Cloud-only Architecture (current)

```
[cron-job.org]
  ├─ daily 02:00 UTC → /api/cron/trending (Worker endpoint)
  │   └─ Groq LLM → GitHub commit → Pages rebuild → Pages serve
  └─ daily 06:00 UTC → /api/cron/indexing (Worker endpoint)
      └─ IndexNow submission → D1 tracking
```

All happening on Cloudflare infra + GitHub + Groq API. No local scripts needed (except initial wrangler deploy).

## Commands user can use

| Action | Command |
|--------|---------|
| Manual deploy to Pages | `cd web && npx wrangler pages deploy dist --project-name beriklanweb` |
| List deployments | `npx wrangler pages deployment list --project-name beriklanweb` |
| Check status | `curl https://beriklanweb.pages.dev/api/health` |
| Test trending endpoint | `curl -X POST "https://beriklanweb.pages.dev/api/cron/trending?token=beriklan-admin-2026"` |

## Recommendation

1. **Connect GitHub to Pages** (5 min, dashboard step) — auto-deploy every push
2. **Set up cron-job.org** (5 min) — daily trending + indexing automation
3. **Keep worker for production** — Pages as backup/preview until proper migration
4. **Plan production migration** as future task (needs Hostinger origin cleanup)

After steps 1+2: 100% cloud, zero local involvement.
