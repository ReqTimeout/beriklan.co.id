# Beriklan.co.id

Performance marketing agency website — Astro 5 static site.

## Deploy Stack
- **Frontend**: Astro 5 + Svelte 5 islands + Tailwind CSS v3
- **Host**: Cloudflare Pages (recommended)
- **Build**: `npm run build` → `dist/`
- **Node**: 20+

## Cloudflare Pages Setup (Recommended)
1. Cloudflare Dashboard → Pages → project `beriklan` → Settings → Builds → Connect GitHub
2. Select repo `ReqTimeout/beriklan.co.id`
3. Build command: `npm run build`
4. Build output dir: `dist`
5. Environment variable: `NODE_VERSION` = `20`
6. Save → auto-deploy on every push to `main`

## Manual Upload
If GitHub integration not desired:
- Cloudflare Dashboard → Pages → `beriklan` → Deployments → Create deployment → Upload
- Drag folder `dist/` (built locally via `npm run build`)

## 301 Redirects (SEO continuity)
`public/_redirects` is auto-bundled into `dist/_redirects` at build time.
843 redirects from old WordPress URLs (`.html`) → new `/blog/<slug>/` paths.
13 irrelevant topics return HTTP 410 Gone.

## Sitemap
- `dist/sitemap-index.xml` → lists `dist/sitemap-0.xml`
- `dist/sitemap-0.xml` contains all 840 URLs
- `dist/robots.txt` references the sitemap
