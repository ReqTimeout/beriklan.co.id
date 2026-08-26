# SEO & Growth System Replication Blueprint
**Audience:** Coding agent (Codex / OpenCode / Claude Code) yang akan menduplikasi sistem SEO + growth loop ini di domain baru.
**Domain asli:** `beriklan.co.id` (since 2016, performance marketing agency ID)
**Stack:** Astro static site + Cloudflare Worker + D1 + R2 + GitHub mirror
**Last updated:** 26 Agustus 2026 (v2.1 — mirror gate, AI provider rotasi, AEO/AI-search indexing)
**Author:** Beriklan Digital Agency + Codex AI

---

## 0. QUICK START (5 menit)

```bash
# 1. Clone repo
git clone https://github.com/<your-org>/<your-domain>.git
cd <your-domain>

# 2. Install & setup Worker
cd web
npm install
npx wrangler login

# 3. Edit wrangler.jsonc:
#    - name: "yourdomain-worker"
#    - main: "src/worker-entry.js"
#    - d1_databases.database_id: <D1 ID>
#    - r2_buckets.bucket_name: <R2 bucket>
#    - vars.ADMIN_TOKEN: <random-string>
#    - assets.run_worker_first: ["/*"]  ← WAJIB (lihat §6)
#    - triggers.crons: ["0 * * * *", "*/15 * * * *"]
# 4. Build static
npm run build

# 5. Deploy
CLOUDFLARE_API_TOKEN="..." CLOUDFLARE_ACCOUNT_ID="..." npx wrangler deploy

# 6. Tambah 5 cron schedule (lihat §7 — free limit CF = 5 trigger per account)
curl -X PUT "https://api.cloudflare.com/client/v4/accounts/<ACC>/workers/scripts/<name>/schedules" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '[{"cron":"0 * * * *"},{"cron":"*/15 * * * *"},{"cron":"30 6 * * *"},{"cron":"0 7 * * *"},{"cron":"0 3 * * 1"}]'
```

Kalau stuck di langkah manapun → scroll ke § yang relevan.

---

## 1. ARSITEKTUR OVERVIEW

```
┌─ STATIC (Astro 5)
│  src/pages/         → 12 service pages + blog index + dynamic blog [slug]
│  src/data/posts.json → 4MB blog metadata, build-time
│  src/components/    → Svelte 5 interactive (Navbar, StickyCTA, OrderWizard)
│  src/layouts/       → Layout.astro: global styles, schema.org JSON-LD, analytics
│
├─ ASSETS (Astro build → dist/)
│  /index.html        → Static homepage
│  /blog/[slug]/index.html → 827 blog pages (pre-rendered)
│  /sitemap-*.xml     → Auto-generated (@astrojs/sitemap)
│  /data/posts-index.json → 14KB lightweight blog metadata (runtime fetch)
│
├─ CLOUDFLARE WORKER (src/worker-entry.js, ~14K lines)
│  ├─ D1 (beriklan-seo) — keyword_queue, generated_drafts, posts_meta,
│  │   posts_content, growth_log, keyword_ranks, pending_indexing,
│  │   email_queue, campaigns, email_templates, lead_pipeline, …
│  ├─ R2 (idberiklan) — publish-queue/queue_NNNNN.ndjson shards (78 file × 500KB)
│  ├─ Cloudflare AI binding (optional, fallback AI provider)
│  ├─ Workers Routes: zone-level binding ke domain + www + api/*
│  ├─ Custom Domain: beriklan.co.id (auto-attached via wrangler.jsonc routes)
│  └─ Cron: 5 trigger max per CF account (lihat §7 time-gating)
│
├─ AI PROVIDER CHAIN (rotasi otomatis, fallback chain)
│  L1. Zen FREE models (6 model stealth + NVIDIA trial): zero cost
│      big-pickle, x-preview-f-free, mimo-v2.5-free, hy3-free,
│      nemotron-3.5-lightning-free, nemotron-3-ultra-free
│  L2. Groq pay-per-token (jika L1 habis / 429)
│      openai/gpt-oss-20b (cheapest, cepat), openai/gpt-oss-120b,
│      qwen/qwen3.6-27b
│  L3. Cloudflare Workers AI binding (env.AI, llama-3.1-8b, optional)
│
└─ INDEXING LAYER
   ├─ GSC Indexing API (200 URL/hari) — URL_UPDATED ping
   ├─ IndexNow (50 URL/batch) — instant submit Bing/Yandex/Naver
   ├─ Bing Webmaster API — sitemap submit
   └─ Sitemap ping (search engines notify on publish)
```

---

## 2. TECH STACK PERSIS

| Layer | Stack | Versi | Kenapa |
|-------|-------|-------|--------|
| Static site | Astro | 5.17 | Partial hydration, super cepat, Svelte islands |
| Interactivity | Svelte 5 | 5.49 | `client:only="svelte"` (anti hydration mismatch) |
| CSS | Tailwind | 3.4 | Custom theme (brand colors) + scoped `<style>` per-component |
| Icons | lucide-svelte | 1.0 | Konsisten dengan copy deck |
| Serverless | Cloudflare Workers | Free tier | 100K req/hari, 5 cron max |
| Database | Cloudflare D1 (SQLite) | Free | 5GB storage, 5M row read/hari |
| Object storage | Cloudflare R2 | Free | 10GB, 1M read/hari (untuk queue shards) |
| Deploy | wrangler | 4.x | `wrangler deploy` manual via token (no GitHub Actions) |
| AI | OpenCode Zen FREE + Groq | live | Lihat §10 |
| Email | Resend | Free 100/hari | Transactional + marketing |
| Tracking | GSC + IndexNow | live | Lihat §11 |

**JANGAN pakai:** React, Vue, jQuery, GSAP, Framer Motion, Lottie (overkill), Bootstrap, Material UI, Hotjar (berat).

---

## 3. KEY FILE PATHS

```
web/
├── astro.config.mjs              ← Astro + Svelte + Tailwind + sitemap plugin
├── tailwind.config.cjs           ← Brand colors, typography scale
├── package.json
├── wrangler.jsonc                ← Worker config (D1, R2, AI, vars, triggers)
├── public/
│   ├── data/posts-index.json     ← Blog metadata ringan (14KB), runtime
│   ├── data/keyword-research*.json ← Riset keyword import (lokal, ignored git)
│   ├── logoweb.webp
│   ├── og-image.png              ← 1200×630 default OG
│   ├── fonts/                    ← Plus Jakarta Sans woff2 (preload)
│   └── robots.txt                ← Allow all + sitemap reference
├── src/
│   ├── pages/
│   │   ├── index.astro           ← Homepage
│   │   ├── blog.astro            ← Blog index (fetch posts-index.json)
│   │   ├── blog/[slug].astro     ← Dynamic blog post (827 slugs)
│   │   ├── jasa-*.astro          ← 10 service pages
│   │   └── order.astro           ← Inquiry form
│   ├── components/               ← Svelte 5 (Navbar, StickyCTA, …)
│   ├── data/posts.json           ← Full blog data (4MB, build-time, ignored git)
│   ├── layouts/Layout.astro      ← HTML shell + global styles + JSON-LD
│   ├── policies/privacy.astro
│   └── styles/global.css         ← Tailwind base + design tokens
├── src/worker-entry.js           ← Cloudflare Worker (API, cron, AI, growth)
└── dist/                         ← Build output (ignored git; deploy to CF)
```

**Catatan path krusial:** `src/worker-entry.js` ada DUA versi di repo ini:
- `/web/src/worker-entry.js` ← yang dipakai wrangler deploy (RELATIF thd wrangler.jsonc)
- `/src/worker-entry.js` ← repo root, dipakai beberapa script lokal
Pastikan edit di `/web/src/worker-entry.js` agar deploy efektif.

---

## 4. ENV VARIABLES & SECRETS

### wrangler.jsonc → `vars` (public, non-secret)
```jsonc
"vars": {
  "ADMIN_TOKEN": "<random 24-char>",   // e.g. "beriklan-admin-2026"
  "SITE_URL": "https://yourdomain.com"
}
```

### Worker secrets (via `wrangler secret put NAME` atau CF API)
| Secret | Wajib | Sumber | Quota |
|--------|-------|--------|-------|
| `DB` | YES | auto dari `d1_databases` binding | D1 free |
| `QUEUE` | YES | auto dari `r2_buckets` binding | R2 free |
| `AI` | optional | auto dari `ai` binding | Workers AI free 10K/hari |
| `ADMIN_TOKEN` | YES | vars (lihat atas) | – |
| `GITHUB_TOKEN` | YES | GH PAT scope `repo` | untuk static mirror sync |
| `GSC_SERVICE_ACCOUNT_JSON` | YES untuk indexing | GSC service account JSON | 200 URL/hari quota |
| `GSC_SITE_URL` | YES | `https://yourdomain.com/` (URL-prefix) atau `sc-domain:yourdomain.com` | – |
| `RESEND_API_KEY` | YES untuk email | resend.com | 100/hari |
| `ZEN_API_KEY` | YES untuk AI | opencode.ai/auth | free tier |
| `GROQ_API_KEY` (×1-5) | YES fallback AI | console.groq.com | pay-per-token |
| `GOOGLE_PLACES_API_KEY` | optional | GCP console | untuk scraper |
| `META_CAPI_ACCESS_TOKEN` | optional | Meta Business | untuk CAPI |
| `TIKTOK_EVENTS_API_TOKEN` | optional | TikTok Events API | untuk CAPI |

### Setup secrets via CLI
```bash
echo "ghp_xxxxxxxxxxxxxxxxx" | npx wrangler secret put GITHUB_TOKEN
echo '{"type":"service_account","project_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n..."}' | npx wrangler secret put GSC_SERVICE_ACCOUNT_JSON
echo "https://yourdomain.com/" | npx wrangler secret put GSC_SITE_URL
echo "re_xxxxxxxxx" | npx wrangler secret put RESEND_API_KEY
echo "sk-zen-xxxxxxxx" | npx wrangler secret put ZEN_API_KEY
echo "gsk_xxxxxxxxx" | npx wrangler secret put GROQ_API_KEY
```

### Setup secrets via CF API (token-based, batch)
```bash
TOKEN="cfut_..."
ACC="..."
SCRIPT="yourdomain-worker"

# Script ini PUT secret text (NB: secret VALUES harus di-encode base64)
put_secret() {
  curl -s -X PUT "https://api.cloudflare.com/client/v4/accounts/$ACC/workers/scripts/$SCRIPT/secrets/$1" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    --data-raw "{\"name\":\"$1\",\"type\":\"secret_text\",\"secret\":\"$2\"}"
}

put_secret GITHUB_TOKEN "ghp_xxxxxxxxx"
put_secret GSC_SITE_URL "https://yourdomain.com/"
# dst
```

---

## 5. DATABASE SCHEMA (D1)

Semua tabel dibuat via `CREATE TABLE IF NOT EXISTS` di handler `handleAdminMigrate` (idempotent, bisa dipanggil manual via `/api/admin/migrate?token=...`). Schema di bawah sudah final production-ready.

### 5.1 Core content pipeline
```sql
-- Keyword queue: target pencarian yang akan dibuat artikelnya
CREATE TABLE IF NOT EXISTS keyword_queue (
  id TEXT PRIMARY KEY,             -- "imp-jasa-live-bandung-a8z3q" format
  keyword TEXT NOT NULL,
  keyword_normalized TEXT NOT NULL, -- lowercased + trim + collapsed space
  source TEXT,                     -- "gsc-impression" | "curated_import" | "trending" | "seed"
  seed TEXT,
  discovered_at TEXT DEFAULT (datetime('now')),
  status TEXT DEFAULT 'pending',   -- pending | generating | generated | published | rejected
  article_slug TEXT,               -- FK ke posts_content (jika sudah jadi)
  service TEXT,                    -- "jasa-view-live" | "jasa-iklan-tiktok" | ...
  city TEXT,                       -- "bandung" | null (national)
  intent TEXT,                     -- commercial | transactional | informational | navigational
  priority_score INTEGER DEFAULT 50,
  indexed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_kw_status ON keyword_queue (status);
CREATE INDEX IF NOT EXISTS idx_kw_service ON keyword_queue (service);
CREATE INDEX IF NOT EXISTS idx_kw_norm ON keyword_queue (keyword_normalized);

-- Generated drafts: artikel yang sudah di-generate AI, belum live
CREATE TABLE IF NOT EXISTS generated_drafts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  content TEXT,                    -- HTML body 3000-9000 chars
  service TEXT,
  city TEXT,
  source TEXT,                     -- "r2-queue" | "trending" | "keyword-import" | "growth-enrich"
  status TEXT DEFAULT 'draft',     -- draft | committed | rejected
  intent TEXT,
  priority_score INTEGER DEFAULT 50,
  created_at TEXT DEFAULT (datetime('now')),
  committed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_drafts_status ON generated_drafts (status);

-- Posts metadata (untuk URL serving, SEO)
CREATE TABLE IF NOT EXISTS posts_meta (
  slug TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  excerpt TEXT,                    -- 150-180 char
  date TEXT,                       -- "13 Jul 2026"
  iso_date TEXT,                   -- ISO 8601 UTC
  category TEXT,                   -- "meta" | "tiktok" | "google" | "youtube" | "case-study" | "strategy"
  readTime TEXT,                   -- "5 min"
  tags TEXT,                       -- JSON array
  service TEXT,
  city TEXT,
  featured INTEGER DEFAULT 0,
  generated INTEGER DEFAULT 0,
  iso_updated TEXT,
  -- Growth overrides (renderer pakai ini kalau ada)
  seo_title TEXT,                  -- ≤60 char, untuk SERP
  seo_description TEXT,            -- ≤155 char, untuk SERP
  enriched_at TEXT,                -- growth-enrich cooldown 21 hari
  ctr_fixed_at TEXT,               -- growth-ctr-fix cooldown 30 hari
  refreshed_at TEXT                -- growth-freshness cooldown 90 hari
);

-- Posts content (body HTML, lazy load)
CREATE TABLE IF NOT EXISTS posts_content (
  slug TEXT PRIMARY KEY,
  content TEXT
);
```

### 5.2 Growth system
```sql
-- Audit trail untuk semua growth action
CREATE TABLE IF NOT EXISTS growth_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  action TEXT NOT NULL,            -- "gsc-loop" | "enrich" | "ctr-fix" | "freshness"
  slug TEXT,
  keyword TEXT,
  position REAL,
  ctr REAL,
  impressions INTEGER,
  static_page INTEGER DEFAULT 1,
  before_json TEXT,
  after_json TEXT,
  ai_model TEXT,
  error TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_growth_action ON growth_log (action, created_at);

-- Snapshot ranking GSC untuk deteksi "perlu di-enrich/ctr-fix"
CREATE TABLE IF NOT EXISTS keyword_ranks (
  keyword TEXT,
  page TEXT,
  position REAL,
  clicks INTEGER,
  impressions INTEGER,
  ctr REAL,
  snapshot_date TEXT,
  PRIMARY KEY (keyword, page, snapshot_date)
);
```

### 5.3 Indexing queue
```sql
-- Antrean URL yang akan di-submit ke GSC + IndexNow
CREATE TABLE IF NOT EXISTS pending_indexing (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  url TEXT UNIQUE NOT NULL,
  type TEXT DEFAULT 'URL_UPDATED',
  source TEXT,                    -- "publish" | "growth" | "manual" | "sync-cascade"
  submitted_gs INTEGER DEFAULT 0, -- 0/1 flag
  submitted_idx INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now')),
  submitted_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_idx_pending ON pending_indexing (submitted_gs, submitted_idx);

-- Audit log submit GSC (untuk rate-limit 200/hari)
CREATE TABLE IF NOT EXISTS indexing_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  url TEXT,
  type TEXT,
  status INTEGER,
  response TEXT,
  submitted_at TEXT DEFAULT (datetime('now'))
);

-- Cron run history + auto-retry
CREATE TABLE IF NOT EXISTS cron_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cron_name TEXT NOT NULL,
  started_at TEXT,
  finished_at TEXT,
  ok INTEGER,
  error TEXT,
  log_json TEXT
);

CREATE TABLE IF NOT EXISTS cron_retry_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cron_name TEXT NOT NULL,
  payload TEXT,
  attempts INTEGER DEFAULT 0,
  next_run_at TEXT,
  last_error TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

-- Track successful sends + failures
CREATE TABLE IF NOT EXISTS email_send_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  to_email TEXT,
  campaign_id INTEGER,
  status TEXT,                     -- sent | failed | bounced
  resend_id TEXT,
  error TEXT,
  sent_at TEXT DEFAULT (datetime('now'))
);

-- Cron config (publish limits, toggle on/off)
CREATE TABLE IF NOT EXISTS cron_settings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  cron TEXT,                       -- cron expression or value
  value TEXT,                      -- alternative storage
  enabled INTEGER DEFAULT 1,
  label TEXT
);

-- Seed values:
INSERT OR IGNORE INTO cron_settings (name, cron, value, enabled, label) VALUES
  ('publish_daily_limit', '300', null, 1, 'Publish harian max (ramp-up 600)'),
  ('publish_batch_size', '30', null, 1, 'Publish per jam'),
  ('gsc_quota_date', null, '2026-08-26', 1, 'Tanggal quota GSC Indexing'),
  ('gsc_quota_used', null, '0', 1, 'Pemakaian GSC hari ini'),
  ('queue_cursor', null, null, 1, 'R2 publish queue cursor');
```

### 5.4 Email system
```sql
CREATE TABLE IF NOT EXISTS campaigns (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  service TEXT,
  template_id INTEGER,
  list_id INTEGER,
  target_count INTEGER DEFAULT 0,
  status TEXT DEFAULT 'sending',   -- draft | sending | done | paused
  subject TEXT,
  total_recipients INTEGER DEFAULT 0,
  sent_count INTEGER DEFAULT 0,
  open_count INTEGER DEFAULT 0,
  click_count INTEGER DEFAULT 0,
  failed_count INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now')),
  sent_at TEXT
);

CREATE TABLE IF NOT EXISTS email_templates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  category TEXT,                   -- service | followup
  subject TEXT,
  html_body TEXT
);

CREATE TABLE IF NOT EXISTS email_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  campaign_id INTEGER,
  email TEXT NOT NULL,
  name TEXT,
  status TEXT DEFAULT 'pending',   -- pending | sent | failed
  tracking_id TEXT UNIQUE,
  subject_override TEXT,           -- AI personalization per-recipient
  opener TEXT,                     -- AI opener per-recipient
  error TEXT,
  sent_at TEXT,
  opened_at TEXT,
  clicked_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_eq_status ON email_queue (status);
CREATE INDEX IF NOT EXISTS idx_eq_campaign ON email_queue (campaign_id);
CREATE INDEX IF NOT EXISTS idx_eq_tracking ON email_queue (tracking_id);
```

### 5.5 Lead pipeline & WA tracking
```sql
CREATE TABLE IF NOT EXISTS lead_contacts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT,
  phone TEXT,
  name TEXT,
  company TEXT,
  city TEXT,
  category TEXT,
  website TEXT,
  source TEXT,
  source_id TEXT,                  -- dedupe per source
  created_at TEXT DEFAULT (datetime('now'))
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_lead_dedupe ON lead_contacts (email, source, source_id);

CREATE TABLE IF NOT EXISTS lead_pipeline (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  contact_id INTEGER,
  email TEXT,
  phone TEXT,
  name TEXT,
  company TEXT,
  city TEXT,
  category TEXT,
  website TEXT,
  service TEXT,
  score INTEGER,
  status TEXT,                     -- matched | personalized | queued | sent | failed | wa_only
  ai_subject TEXT,
  ai_opener TEXT,
  campaign_id INTEGER,
  wa_link TEXT,
  matched_at TEXT
);

CREATE TABLE IF NOT EXISTS wa_clicks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  page_location TEXT,
  service_slug TEXT,
  package_name TEXT,
  package_price TEXT,
  cta_label TEXT,
  cta_location TEXT,
  link_url TEXT,
  referrer TEXT,
  user_agent TEXT,
  ip_hash TEXT,
  session_id TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_wa_clicks_created ON wa_clicks (created_at);
CREATE INDEX IF NOT EXISTS idx_wa_clicks_service ON wa_clicks (service_slug);
CREATE INDEX IF NOT EXISTS idx_wa_clicks_session ON wa_clicks (session_id);

CREATE TABLE IF NOT EXISTS wa_followups (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL,
  name TEXT,
  service TEXT,
  package_name TEXT,
  page_location TEXT,
  session_id TEXT,
  status TEXT DEFAULT 'pending',   -- pending | queued | sent
  sent_at TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_wf_email_status ON wa_followups (email, status);
```

### 5.6 Audit & anti-spam
```sql
CREATE TABLE IF NOT EXISTS policy_audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT,
  source TEXT,
  category TEXT,
  keyword TEXT,
  severity TEXT,
  action TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS rate_limit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ip TEXT,
  endpoint TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_rl_ip_endpoint ON rate_limit_log (ip, endpoint, created_at);
```

---

## 6. WORKER ROUTING & ASSETS

### 6.1 wrangler.jsonc — run_worker_first (KRUSIAL!)

```jsonc
"assets": {
  "binding": "ASSETS",
  "directory": "dist",
  "run_worker_first": ["/*"]   ← WAJIB pakai ["/*"] bukan ["/blog/*"]
}
```

**Gotcha (sudah pernah jadi bug):** Kalau `run_worker_first` cuma `["/blog/*"]`, asset-first mem-bypass Worker untuk static HTML lain → 301 `www→apex` gagal → FAQ growth enrichment tidak pernah sampai ke `/blog/<slug>/` yang di static build. SOLUSI: pakai `["/*"]`.

### 6.2 Route registration di Worker

Setiap endpoint punya pola `path === "/api/..."` atau `path.startsWith("/api/...")`. Lalu fallback ke `env.ASSETS.fetch(request)` untuk static files. Pola krusial:

```javascript
// src/worker-entry.js (skeleton)
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    const token = url.searchParams.get("token");
    
    // 1. Auth-required admin endpoints (letakkan di awal untuk early-return)
    if (token !== env.ADMIN_TOKEN) return new Response("Unauthorized", { status: 401 });
    if (path === "/api/admin/...") return await handleXxx(request, env);
    
    // 2. Public endpoints
    if (path === "/api/newsletter/subscribe") return await handleSubscribe(request, env);
    if (path === "/llms.txt") return await handleLlmsTxt(request, env);
    
    // 3. Cron triggers (dipanggil oleh CF cron schedule)
    if (path === "/api/cron/hourly-generate") return await handleHourlyGenerate(request, env);
    
    // 4. Static asset fallback (untuk blog, sitemap, dll)
    return env.ASSETS.fetch(request);
  },
  
  async scheduled(event, env, ctx) {
    // Time-gated cron jobs (lihat §7)
    const cron = event.cron;
    if (cron === "0 * * * *") {
      await handleHourlyBlock(env, ctx);  // batch of growth jobs
    }
    if (cron === "*/15 * * * *") {
      await handleCronSendEmail(request, env);
    }
  }
}
```

### 6.3 GitHub mirror (static build)

Worker `handleAdminSyncPosts` punya **mirror gate** (`?mirror=1`) untuk sync `posts_meta` + `posts_content` ke `src/data/posts.json` di GitHub → trigger CF Pages auto-build (kalau di-setup). Default lean run TIDAK sync ke GitHub (hemat CPU Workers Free).

---

## 7. CRON JOBS — 5 slot limit

Cloudflare free tier = **5 cron triggers MAX per account** (bukan per-script). Berikut slot final beriklanweb:

```
Slot 1: 0 * * * *       (hourly block + time-gated growth)
Slot 2: */15 * * * *    (email-send)
Slot 3: 30 6 * * *      (scrape-indonetwork)
Slot 4: 0 7 * * *       (scrape-google-places)
Slot 5: 0 3 * * 1       (snippet-optimize, Monday only)
```

**Time-gating di dalam `scheduled()` handler** (lihat `worker-entry.js`):
```javascript
async scheduled(event, env, ctx) {
  const cron = event.cron;
  if (cron === "0 * * * *") {
    const h = new Date().getUTCHours();
    const d = new Date().getUTCDay();
    
    // Every hour
    ctx.waitUntil(handleHourlyGenerate(env));
    ctx.waitUntil(handleIndexNowCron(env));
    ctx.waitUntil(handleGscIndexingCron(env));
    ctx.waitUntil(handleSitemapPing(env));
    
    // Every 6 hours (h % 6 === 0)
    if (h % 6 === 0) {
      ctx.waitUntil(handleGrowthGscLoop(env));
    }
    
    // Daily 09:00 UTC
    if (h === 9) {
      ctx.waitUntil(handleGrowthEnrich(env));
      ctx.waitUntil(handleGrowthCtrFix(env));
    }
    
    // Monday 02:00 UTC
    if (d === 1 && h === 2) {
      ctx.waitUntil(handleGrowthFreshness(env));
    }
  }
  if (cron === "*/15 * * * *") ctx.waitUntil(handleCronSendEmail(env));
  if (cron === "30 6 * * *") ctx.waitUntil(handleScrapeIndonetwork(env));
  if (cron === "0 7 * * *") ctx.waitUntil(handleScrapeGooglePlaces(env));
  if (cron === "0 3 * * 1") ctx.waitUntil(handleSnippetOptimizer(env));
}
```

**Gotcha penting:** PUT schedules API butuh body **array mentah** `[{"cron":"..."}]`, BUKAN `{"schedules":[...]}` (error 10026). Error 10072 = cap 5 tercapai.

---

## 8. KEYWORD GENERATION (Riset + Import)

### 8.1 Source data
Riset keyword disimpan di `web/public/data/keyword-research-v2.json` (local only, ignored git). Format JSON array of objects:

```json
[
  {
    "keyword": "jasa host live facebook live",
    "service": "jasa-view-live",
    "city": "bandung",
    "intent": "commercial",
    "priority": 85
  },
  ...
]
```

### 8.2 Import via endpoint (NO build/deploy needed)

```bash
TOKEN="beriklan-admin-2026"

# Single keyword
curl -X POST "https://yourdomain.com/api/admin/keywords/import?token=$TOKEN&source=curated_research_v2" \
  -H "Content-Type: application/json" \
  -d '[
    {"keyword":"jasa live streaming tiktok jakarta","service":"jasa-view-live","city":"jakarta","intent":"commercial","priority":85},
    {"keyword":"jasa pembuatan website toko online","service":"jasa-pembuatan-website","intent":"transactional","priority":75}
  ]'

# Atau envelope
curl -X POST "https://yourdomain.com/api/admin/keywords/import?token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"keywords": [...]}'
```

Response: `{ok: true, inserted: N, skipped: M, sample_inserted: [...], sample_errors: [...]}`

### 8.3 Auto-discover via GSC impression loop
`growth-gsc-loop` (cron `0 */6 jam`):
1. Query GSC `dimensions=[query,page]` window 14 hari
2. Filter: query komersial (`impressions ≥ 20`, position 3-30)
3. Cocokkan dengan existing posts_meta (existing page → skip)
4. Yang TIDAK punya halaman layak → insert ke `keyword_queue` dengan `source='gsc-impression'`, `priority = min(100, 40 + imps/5)`

```bash
MANUAL="https://yourdomain.com/api/cron/growth/gsc-loop?token=$TOKEN&days=14&minImp=20&maxQueue=10"
curl -s "$MANUAL" | jq '.queued, .rows, .relevant'
```

### 8.4 Filter & quality control

**Skip keyword OFF-TOPIC** (via `policy_filter.js`):
- Block list: judi, slot, togel, fashion, kuliner, kesehatan, pendidikan, hewan, lowongan, crypto, sepak bola, game online, konstruksi.
- Severity: `block` (reject), `warn` (log but allow).

**Skip keyword TIDAK ADA VOLUME** (priority_score < 30 atau no search volume):
- Hapus dari queue manual via admin endpoint.

---

## 9. ARTICLE GENERATION (AI pipeline)

### 9.1 AI provider rotasi (PENTING! Model free selalu berubah)

Diverifikasi 2026-08-26 via opencode.ai/docs/zen + Groq /v1/models:
- `deepseek-v4-flash-free` SUDAH DIHAPUS dari Zen
- `llama-3.3-70b-versatile` SUDAH DIHAPUS dari Groq

**Struktur rotasi (lihat konstanta di worker-entry.js):**

```javascript
// L1. Zen FREE (zero cost, 6 model rotasi)
const ZEN_FREE_MODELS = [
  "big-pickle",                  // stealth, free
  "x-preview-f-free",            // stealth Ox Alpha, zero-retention
  "mimo-v2.5-free",              // stealth, free
  "hy3-free",                    // stealth, free
  "nemotron-3.5-lightning-free", // NVIDIA trial, fast
  "nemotron-3-ultra-free",       // NVIDIA trial, slow but capable
];
const ZEN_ENDPOINT = "https://opencode.ai/zen/v1/chat/completions";

// L2. Groq pay-per-token (rotasi 3 model + N API key)
const GROQ_CHAT_MODELS = [
  "openai/gpt-oss-20b",   // cheapest, 1000 t/s
  "openai/gpt-oss-120b",  // 500 t/s, larger
  "qwen/qwen3.6-27b",     // fallback
];
const GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions";

// Multi-key rotation: GROQ_API_KEY, GROQ_API_KEY_2, ..., GROQ_API_KEY_5
```

### 9.2 Generic `generateWithZenOrGroq` helper

```javascript
async function generateWithZenOrGroq(prompt, env, maxTokens = 600) {
  // L1. Zen — rotate across 6 models
  if (env.ZEN_API_KEY) {
    for (const zmodel of ZEN_FREE_MODELS) {
      try {
        const r = await fetch(ZEN_ENDPOINT, {
          method: "POST",
          headers: { Authorization: `Bearer ${env.ZEN_API_KEY}`, "Content-Type": "application/json", "User-Agent": "BeriklanWorker/1.0" },
          body: JSON.stringify({
            model: zmodel,
            messages: [{ role: "user", content: prompt }],
            max_tokens: maxTokens,
            thinking: { type: "disabled" },   // required for stealth models
          }),
        });
        if (r.ok) {
          const text = (await r.json()).choices?.[0]?.message?.content || "";
          if (text && text.length > 30) return { _model: `zen/${zmodel}`, text };
        }
      } catch (e) {}
    }
  }
  // L2. Groq — rotate keys × models
  const groqKeys = getGroqKeys(env);
  for (let i = 0; i < groqKeys.length; i++) {
    for (const model of GROQ_CHAT_MODELS) {
      try {
        const body = {
          model,
          messages: [{ role: "user", content: prompt }],
          max_tokens: Math.max(maxTokens, model.startsWith("openai/gpt-oss") ? 2048 : maxTokens),
          temperature: 0.7,
        };
        if (model.startsWith("openai/gpt-oss")) body.reasoning_effort = "low";
        const r = await fetch(GROQ_ENDPOINT, {
          method: "POST",
          headers: { Authorization: `Bearer ${groqKeys[i]}`, "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        if (r.ok) {
          const text = (await r.json()).choices?.[0]?.message?.content || "";
          if (text && text.length > 30) return { _model: `groq/${model} (groq#${i+1})`, text };
        }
      } catch (e) {}
    }
  }
  return null;  // all exhausted
}
```

### 9.3 Generation prompt template (Bahasa Indonesia, agency niche)

```javascript
const prompt = `Tulis artikel SEO Bahasa Indonesia untuk topik: "${keyword}". 
Konteks: layanan ${service}, lokasi ${city}, tipe ${intent}.
Tone profesional, terukur, formal-measured. Format HTML mulai dari <h2>.

Struktur WAJIB (850-1300 kata total):
- <h2>Pendahuluan</h2>: 1 paragraf (konteks lokal)
- <h2>Cara Kerja & Langkah Praktis</h2>: <ul> 4-5 langkah
- <h2>Yang Perlu Dihindari</h2>: <ul> 3 anti-pattern
- <h2>Pertanyaan yang Sering Diajukan</h2>: 3× <h3>+<p> (FAQ lokal)
- <h2>Kesimpulan</h2>: 1 paragraf + CTA WhatsApp (wa.me/62811919328)

ATURAN KERAS:
- Pakai "Anda" (bukan "kamu"), "kami" (bukan "kita")
- WAJIB sebut "${city}" minimal 2× di paragraf natural
- JANGAN pakai: bikin, gak, nggak, pasti untung, garansi 100%, semacam, di mana
- JANGAN over-promise angka
- WAJIB sertakan internal link ke https://${domain}/${service}/ minimal 2×
- WAJIB sertakan CTA WhatsApp dengan text URI-encoded

Output: HANYA HTML body, mulai dari <h2>. Tidak ada markdown fences.`;
```

### 9.4 Self-check sebelum publish

```javascript
function validateDraft(draft, keyword, city) {
  const minLen = 3000;
  const maxLen = 10000;
  const errs = [];
  if (draft.length < minLen) errs.push("too_short");
  if (draft.length > maxLen) errs.push("too_long");
  if (!/^<h2>/.test(draft.trim())) errs.push("h2_missing");
  if (city && !draft.toLowerCase().includes(city.toLowerCase())) errs.push("city_missing");
  if ((draft.match(/<h2>/g) || []).length < 4) errs.push("structure_incomplete");
  if (/bikin|gak|nggak|pasti untung|garansi 100%/.test(draft)) errs.push("banned_word");
  return errs.length === 0 ? { ok: true } : { ok: false, errs };
}
```

### 9.5 Mirror gate (Workers Free CPU limit)

`handleAdminSyncPosts` ada query param `mirror`:
- default / `?mirror=0`: **lean** — publish D1 + auto-index, TIDAK fetch/merge/PUT 40MB posts.json ke GitHub. Aman di CPU free.
- `?mirror=1`: **full** — sync posts_meta + posts_content ke `src/data/posts.json` GitHub. BERAT, risiko 1102.

Cron `0 * * * *` pakai lean. Full mirror dipanggil manual saat perlu rebuild static Astro.

---

## 10. INDEXING (GSC + IndexNow + Bing + Sitemap)

### 10.1 GSC Indexing API — `URL_UPDATED` publish

Quota: **200 URL/hari** (Google Search Console Indexing API). Auto-tracked via `gsc_quota_used` di `cron_settings`.

```javascript
async function submitToGscCore(env, urls) {
  if (!env.GSC_SERVICE_ACCOUNT_JSON) return { submitted: 0, error: "no GSC secret" };
  const today = new Date().toISOString().slice(0, 10);
  // Quota check
  const quotaR = await env.DB.prepare("SELECT value FROM cron_settings WHERE name='gsc_quota_date'").first();
  const quotaDate = quotaR?.value || '';
  let used = 0;
  if (quotaDate === today) {
    const usedR = await env.DB.prepare("SELECT value FROM cron_settings WHERE name='gsc_quota_used'").first();
    used = parseInt(usedR?.value || '0');
  } else {
    await env.DB.batch([
      env.DB.prepare("INSERT INTO cron_settings (name, cron, value) VALUES ('gsc_quota_date', '1', ?) ON CONFLICT(name) DO UPDATE SET value=?").bind(today, today),
      env.DB.prepare("INSERT INTO cron_settings (name, cron, value) VALUES ('gsc_quota_used', '1', '0') ON CONFLICT(name) DO UPDATE SET value='0'"),
    ]);
  }
  const maxSubmit = Math.min(urls.length, Math.max(0, 200 - used));
  if (maxSubmit === 0) return { submitted: 0, error: "quota_exhausted" };
  
  const sa = JSON.parse(env.GSC_SERVICE_ACCOUNT_JSON);
  const accessToken = await getGoogleAccessToken(sa, "https://www.googleapis.com/auth/indexing");
  
  let submitted = 0;
  for (const pageUrl of urls.slice(0, maxSubmit)) {
    const r = await fetch("https://indexing.googleapis.com/v3/urlNotifications:publish", {
      method: "POST",
      headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json" },
      body: JSON.stringify({ url: pageUrl, type: "URL_UPDATED" }),
    });
    if (r.ok) {
      submitted++;
      await env.DB.batch([
        env.DB.prepare("INSERT INTO indexing_log (url, type, status) VALUES (?, 'URL_UPDATED', 200)").bind(pageUrl),
        env.DB.prepare("UPDATE pending_indexing SET submitted_gs=1, submitted_at=datetime('now') WHERE url=?").bind(pageUrl),
      ]);
    } else if (r.status === 429) {
      // set backoff
      return { submitted, error: "rate_limited_429" };
    }
  }
  // Update quota
  await env.DB.prepare("UPDATE cron_settings SET value=? WHERE name='gsc_quota_used'").bind(String(used + submitted)).run();
  return { submitted };
}
```

### 10.2 IndexNow (Bing, Yandex, Naver)

Quota: **10K URL/hari** per IndexNow key, tapi praktiskan batasi 50/batch.

```javascript
async function submitToIndexNow(urls, env) {
  if (!urls.length) return { submitted: 0 };
  const host = new URL(urls[0]).hostname;
  const key = env.INDEXNOW_KEY || "beriklan-indexnow-2026";
  const keyLoc = `https://${host}/${key}.txt`;
  
  const body = { host, key, keyLocation: keyLoc, urlList: urls.slice(0, 50) };
  const r = await fetch("https://api.indexnow.org/indexnow", {
    method: "POST",
    headers: { "Content-Type": "application/json; charset=utf-8" },
    body: JSON.stringify(body),
  });
  // 200 OK = queued, 202 = received, 429 = backoff
  return { submitted: urls.slice(0, 50).length, status: r.status };
}
```

### 10.3 Bing Webmaster API (sitemap submit)

```javascript
const bingToken = env.BING_WEBMASTER_API_KEY;
const r = await fetch(`https://ssl.bing.com/ping?sitemap=${encodeURIComponent(sitemapUrl)}`);
```

### 10.4 Sitemap ping

```javascript
const engines = [
  `https://www.google.com/ping?sitemap=${sitemapUrl}`,
  `https://www.bing.com/ping?sitemap=${sitemapUrl}`,
  // Yandex, Baidu opsional
];
for (const url of engines) await fetch(url);  // fire-and-forget
```

### 10.5 End-to-end indexing flow (setiap publish)

```
publish_posts (D1 commit)
  ↓
insert_urls_to_pending_indexing
  ↓ (cron hourly)
cron-indexing:
  ├─ submit pending_indexing → GSC (200/hari cap)
  ├─ submit pending_indexing → IndexNow (50/batch)
  ├─ sitemap ping (kirim semua sub-sitemap)
  └─ log ke indexing_log + cron_runs
```

---

## 11. GROWTH LOOP (GSC feedback)

Empat loop menutup siklus `publish → rank → belajar → perbaiki`. SEMUA menulis langsung ke D1 (`posts_meta` + `posts_content`), efek live tanpa build/deploy.

### 11.1 `growth-gsc-loop` (tiap 6 jam, time-gate `h % 6 === 0`)
- Query GSC `dimensions=[query,page]` window 14 hari
- Filter: query komersial imps ≥ 20 tanpa halaman blog layak
- Insert ke `keyword_queue` source `gsc-impression`, priority `40 + imps/5`
- Dedupe by `keyword_normalized`

```bash
TOKEN="beriklan-admin-2026"
curl -s "https://beriklan.co.id/api/cron/growth/gsc-loop?token=$TOKEN&days=14&minImp=20&maxQueue=5" | jq .
```

### 11.2 `growth-enrich` (harian 09:00 UTC)
- Snapshot `keyword_ranks`: artikel posisi 3-18
- Rewrite paragraf pembuka (`<p class="growth-intro">`) + FAQ spesifik-query (`<h3 class="growth-faq">`) di `posts_content`
- Cooldown 21 hari per slug (`posts_meta.enriched_at`)

```bash
curl -s "https://beriklan.co.id/api/cron/growth/enrich?token=$TOKEN&count=10&minImp=50&posMin=3&posMax=18" | jq .
```

### 11.3 `growth-ctr-fix` (harian 09:00 UTC)
- Snapshot `keyword_ranks`: artikel imps ≥ 50 & CTR ≤ 2% & position ≤ 30
- Rewrite SERP `seo_title` (≤60 char) + `seo_description` (≤155 char) di `posts_meta`
- Renderer pakai override ini untuk `<title>` + og + meta description (H1 tidak berubah — supaya tidak double-render)
- Cooldown 30 hari (`posts_meta.ctr_fixed_at`)

```bash
curl -s "https://beriklan.co.id/api/cron/growth/ctr-fix?token=$TOKEN&count=20&minImp=50&maxCtr=0.02" | jq .
```

### 11.4 `growth-freshness` (Senin 02:00 UTC, time-gate `dow === 1 && h === 2`)
- Artikel >90 hari dengan imps > 0
- Sisipkan callout "Diperbarui {tahun}" + bullets baru setelah paragraf pertama (`<div class="freshness-update">`)
- Set `posts_meta.refreshed_at` → badge "Diperbarui" di render + `dateModified` schema (JUJUR, `datePublished` TIDAK diubah)

```bash
curl -s "https://beriklan.co.id/api/cron/growth/freshness?token=$TOKEN&count=20&ageDays=90" | jq .
```

### 11.5 Audit trail — `growth_log`
Setiap aksi growth simpan: action, slug, keyword, position, ctr, impressions, before_json, after_json, ai_model, error. Check via:

```bash
curl -s "https://beriklan.co.id/api/admin/growth-log?token=$TOKEN&action=enrich&limit=20" | jq .
```

---

## 12. EMAIL SYSTEM (campaign + auto follow-up)

### 12.1 Setup

1. Daftar di resend.com → buat API key `re_...` → simpan di `RESEND_API_KEY` secret
2. Verify domain `beriklan.co.id` di Resend dashboard
3. Setup DNS records (SPF + DKIM + DMARC)

### 12.2 Quota
**Resend free tier = 100 email/hari** (reset 00:00 UTC). Cron `email-send` jalan tiap 15 menit.

### 12.3 `handleCronSendEmail` (per-campaign rotation)

**Bug yang sudah diperbaiki (2026-08-26):** cron lama pilih `oldest pending GLOBAL` → campaign besar (12k pending) monopoli kuota harian, campaign kecil (3.5k) STARVED forever.

**Fix baru: per-campaign fair rotation:**
```javascript
// Hitung active campaign dengan pending emails
const activeCampaigns = await env.DB.prepare(`
  SELECT id, name,
    (SELECT COUNT(*) FROM email_queue WHERE campaign_id=c.id AND status='pending') AS pending
  FROM campaigns c
  WHERE c.status IN ('sending','draft')
    AND (SELECT COUNT(*) FROM email_queue WHERE campaign_id=c.id AND status='pending') > 0
  ORDER BY (SELECT MIN(id) FROM email_queue WHERE campaign_id=c.id AND status='pending') ASC
`).all();

// Distribute remainingToday secara proporsional
const perCampaign = Math.max(1, Math.floor(remainingToday / activeCampaigns.length));
const batchSize = Math.min(remainingToday, activeCampaigns.length * perCampaign);

// Round-robin fetch batch per active campaign (oldest-first per campaign)
const batch = [];
for (const camp of activeCampaigns) {
  if (batch.length >= batchSize) break;
  const take = Math.min(perCampaign, batchSize - batch.length);
  const rows = await env.DB.prepare(
    "SELECT q.*, c.name as campaign_name FROM email_queue q LEFT JOIN campaigns c ON q.campaign_id=c.id WHERE q.status='pending' AND q.campaign_id=? ORDER BY q.id ASC LIMIT ?"
  ).bind(camp.id, take).all();
  batch.push(...rows);
}
```

### 12.4 Daily Resend quota guard

```javascript
const DAILY_LIMIT = 100;
const SAFETY_BUFFER = 5;  // reserve untuk alert-email + retry queue
if (dailySent >= DAILY_LIMIT - SAFETY_BUFFER) {
  return { ok: true, skipped: true, reason: `Daily Resend limit reached (${dailySent}/${DAILY_LIMIT})...`, reset_at: "besok 00:00 UTC" };
}
```

### 12.5 Per-recipient personalization (lead pipeline)

Subject + opener di-override per recipient dari `lead_pipeline`:
```javascript
const effectiveSubject = item.subject_override || tmpl.subject;
if (item.opener) {
  bodyHtml = bodyHtml.replace(/\{\{opener\}\}/g, `<p>${item.opener}</p>`);
}
```

### 12.6 Auto-retry failed

```javascript
const sentAfterPending = dailySent + sent;
if (sentAfterPending < DAILY_LIMIT - 10) {
  const failedToRetry = await env.DB.prepare(
    "SELECT id FROM email_queue WHERE status='failed' AND (error IS NULL OR error NOT LIKE '%rate%exceed%') AND (sent_at IS NULL OR sent_at < datetime('now', '-1 hour')) ORDER BY id ASC LIMIT 10"
  ).bind(...);
  // reset → pending
}
```

### 12.7 Tracking pixel + click redirect

```
GET /api/track/open?id={tracking_id}  → 1×1 GIF + UPDATE opened_at
GET /api/track/click?id={tracking_id}&url={target} → 302 redirect + UPDATE clicked_at
```

Cookie `bk_wa_session` + service/package disimpan saat klik WA → kalau user subscribe newsletter setelah klik WA, otomatis dapat email follow-up (`category='followup'`, dedupe 14 hari).

---

## 13. LEAD PIPELINE (akuisisi klien otomatis)

### 13.1 Flow (cron `lead-pipeline`, `0 */6 * * *`)
1. **Match & score** — `matchLeadService()` cocokkan `category/company/name/website` ke 10 `LEAD_SERVICE_RULES`. Fallback `Jasa Digital Marketing`. `scoreLead()` = email 40 + phone 20 + website 15 + city 10 + company 15.
2. **AI personalisasi** — `personalizeLead()` panggil `generateWithZenOrGroq` → SUBJECT (≤90 char) + OPENER (≤220 char). Batch ≤40/run, delay 250ms.
3. **Auto-campaign** — group lead `matched` per service → buat/get campaign `Auto Pipeline: {service}` (template di-lookup by service name) → queue ke `email_queue` (max 50/service/run) dengan `subject_override` + `opener`.
4. **WA fallback** — `buildWaLink()` untuk lead ber-phone (tanpa email) → `https://wa.me/...?text=` template.

### 13.2 Endpoint

```bash
TOKEN="beriklan-admin-2026"
curl -s "https://beriklan.co.id/api/cron/leads/process?token=$TOKEN&limit=100&ai=15&campaign=1" | jq .
curl -s "https://beriklan.co.id/api/admin/leads?token=$TOKEN" | jq .
```

---

## 14. SEO ON-PAGE — MAXIMIZE AI-INDEXING (Google AI Overview, ChatGPT, Perplexity, Gemini)

### 14.1 Schema.org JSON-LD (WAJIB)

Setiap page punya JSON-LD structured data. Tiga blok utama:

**a) Organization (di `Layout.astro`, setiap halaman):**
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Beriklan Digital Agency",
  "url": "https://beriklan.co.id",
  "logo": "https://beriklan.co.id/logoweb.webp",
  "description": "Senior performance marketing partner sejak 2016",
  "foundingDate": "2016",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Jl. Arcamanik Endah No.76",
    "addressLocality": "Bandung",
    "postalCode": "40195",
    "addressCountry": "ID"
  },
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+62-81-1919-328",
    "contactType": "customer service",
    "areaServed": "ID",
    "availableLanguage": ["Indonesian", "English"]
  },
  "sameAs": [
    "https://www.facebook.com/beriklan.id",
    "https://www.instagram.com/beriklan.id",
    "https://www.tiktok.com/@beriklan.id"
  ],
  "knowsAbout": [
    "Digital Marketing", "Facebook Ads", "Instagram Ads",
    "TikTok Ads", "Google Ads", "YouTube Ads", "SEO",
    "Landing Page Optimization", "Performance Marketing"
  ]
}
</script>
```

**b) ProfessionalService (di service pages):**
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ProfessionalService",
  "name": "Jasa Iklan Facebook Ads",
  "image": "https://beriklan.co.id/og-image.png",
  "url": "https://beriklan.co.id/jasa-iklan-facebook/",
  "telephone": "+62-81-1919-328",
  "priceRange": "Rp 5.000.000 - Rp 50.000.000",
  "address": { "@type": "PostalAddress", "addressLocality": "Bandung", "addressCountry": "ID" },
  "areaServed": { "@type": "Country", "name": "Indonesia" },
  "serviceType": "Facebook Ads Management",
  "provider": { "@type": "Organization", "name": "Beriklan Digital Agency" },
  "hasOfferCatalog": {
    "@type": "OfferCatalog",
    "name": "Paket Facebook Ads",
    "itemListElement": [
      {
        "@type": "Offer",
        "name": "Paket Starter",
        "price": "5000000",
        "priceCurrency": "IDR",
        "itemOffered": { "@type": "Service", "name": "Facebook Ads Setup Bulanan" }
      }
    ]
  },
  "aggregateRating": null   // JANGAN fake rating — HAPUS
}
</script>
```

**c) BreadcrumbList (setiap page):**
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Beranda", "item": "https://beriklan.co.id/" },
    { "@type": "ListItem", "position": 2, "name": "Jasa", "item": "https://beriklan.co.id/jasa-digital-marketing/" },
    { "@type": "ListItem", "position": 3, "name": "Jasa Iklan Facebook" }
  ]
}
</script>
```

**d) Article (blog post, generated dari frontmatter):**
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Cara Pasang Iklan Facebook untuk Pemula 2026",
  "image": "https://beriklan.co.id/og-image.png",
  "datePublished": "2026-07-13T10:00:00+07:00",
  "dateModified": "2026-08-20T15:00:00+07:00",   ← updated via growth-freshness
  "author": {
    "@type": "Person",
    "name": "Tim Beriklan",
    "url": "https://beriklan.co.id/about/"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Beriklan Digital Agency",
    "logo": { "@type": "ImageObject", "url": "https://beriklan.co.id/logoweb.webp" }
  },
  "mainEntityOfPage": { "@type": "WebPage", "@id": "https://beriklan.co.id/blog/jasa-iklan-facebook-pemula/" },
  "articleSection": "strategy",
  "keywords": "facebook ads, jasa iklan facebook, beriklan",
  "inLanguage": "id-ID"
}
</script>
```

**e) FAQPage (FAQ section — penting untuk AI Overview):**
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Berapa biaya pasang iklan Facebook di Beriklan?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Paket mulai Rp 5.000.000/bulan untuk setup + manajemen..."
      }
    },
    ...3-5 FAQ
  ]
}
</script>
```

### 14.2 Meta tags (Title, Description, OG, Twitter)

Pattern setiap page:
```html
<!-- Primary -->
<title>Jasa Iklan Facebook Ads Targeting Presisi | Meta Business Partner — Beriklan</title>
<meta name="description" content="Jasa iklan Facebook Ads dengan targeting presisi dan creative teruji. Tim bersertifikasi Meta Business Partner sejak 2016. Sesi konsultasi via WhatsApp.">
<link rel="canonical" href="https://beriklan.co.id/jasa-iklan-facebook/">

<!-- Open Graph -->
<meta property="og:type" content="website">
<meta property="og:title" content="Jasa Iklan Facebook Ads Targeting Presisi | Beriklan">
<meta property="og:description" content="...">
<meta property="og:url" content="https://beriklan.co.id/jasa-iklan-facebook/">
<meta property="og:image" content="https://beriklan.co.id/og-image.png">
<meta property="og:locale" content="id_ID">
<meta property="og:site_name" content="Beriklan Digital Agency">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="...">
<meta name="twitter:description" content="...">
<meta name="twitter:image" content="https://beriklan.co.id/og-image.png">
```

**Override `growth-ctr-fix`:** kalau CTR ≤ 2%, ganti `seo_title` (≤60) + `seo_description` (≤155) di `posts_meta`. Renderer pakai override untuk `<title>` + meta description (BUKAN ganti H1 — supaya UX tetap).

### 14.3 `llms.txt` (BARU! Penting untuk AI indexing)

Buat `public/llms.txt` (AI-crawler friendly summary). Worker route `handleLlmsTxt`:

```
# Beriklan.co.id

> Senior performance marketing partner sejak 2016. Mengelola campaign iklan Meta, Google, TikTok, YouTube, dan Landing Page untuk UMKM & bisnis menengah Indonesia.

## Layanan Utama
- [Jasa Iklan Facebook Ads](https://beriklan.co.id/jasa-iklan-facebook/): Targeting presisi, Meta Business Partner certified.
- [Jasa Iklan TikTok Ads](https://beriklan.co.id/jasa-iklan-tiktok/): Spark & FYP optimization.
- [Jasa Iklan Google Ads](https://beriklan.co.id/jasa-iklan-google/): Search, Display & YouTube.
- [Jasa Pembuatan Landing Page](https://beriklan.co.id/jasa-pembuatan-landing-page/): Konversi tinggi, bundle Google Ads.
- [Jasa Digital Marketing](https://beriklan.co.id/jasa-digital-marketing/): Multi-channel integrated.

## Kontak
- WhatsApp: https://wa.me/62811919328
- Email: info@beriklan.co.id
- Alamat: Jl. Arcamanik Endah No.76, Bandung 40195

## Blog & Resource
- [Blog](https://beriklan.co.id/blog/): 800+ artikel digital marketing Indonesia.
```

**Optional `llms-full.txt`** (extended version, 100+ KB structured): list semua blog post dengan title + excerpt + tags. AI LLM akan ingest ini untuk jawaban pertanyaan relevan.

### 14.4 `robots.txt`

```txt
User-agent: *
Allow: /
Disallow: /api/

User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: CCBot
Allow: /

User-agent: anthropic-ai
Allow: /

Sitemap: https://beriklan.co.id/sitemap-index.xml
```

### 14.5 Heading hierarchy (H1 → H2 → H3)

- **H1** WAJIB 1 per page, dengan primary keyword di 8 kata pertama
- **H2** section titles (3-6 per page), natural bahasa
- **H3** subsection + FAQ (WAJIB structured sebagai `<h3>` + `<p>` pair, BUKAN bullet)

### 14.6 Content depth

- Min **3000 karakter** per artikel (audit threshold: `thin_count` < 200)
- Setiap artikel: 4-6 section (`Pendahuluan`, `Cara Kerja`, `Yang Perlu Dihindari`, `FAQ`, `Kesimpulan`)
- **Avg target 4000-5000 karakter** untuk SEO bagus
- WAJIB sebut **kota + service** di paragraf natural minimal 2×
- WAJIB **internal link** ke pillar page (`/jasa-{service}/`) minimal 2×
- WAJIB **CTA WhatsApp** di akhir (URI-encoded message)

### 14.7 FAQ khusus AI Overview (AEO — Answer Engine Optimization)

Pattern pertanyaan yang SANGAT disukai AI Overview:
1. **"Berapa biaya X?"** — jawaban: range harga + 3 tier
2. **"Bagaimana cara X?"** — jawaban: 4-5 langkah praktis
3. **"Apa bedanya X vs Y?"** — jawaban: comparison table
4. **"Apakah X aman/efektif?"** — jawaban: transparansi + studi kasus
5. **"Kapan waktu terbaik X?"** — jawaban: timing spesifik + reasoning

Format FAQ (WAJIB dipakai agar AI extract):
```html
<h3>Berapa biaya pasang iklan Facebook di Beriklan?</h3>
<p>Paket mulai Rp 5.000.000/bulan untuk setup Meta Business Suite + 1 campaign...</p>

<h3>Berapa lama sampai iklan tayang?</h3>
<p>Setelah akun Meta Ads Anda diberikan akses, campaign bisa tayang dalam 1-3 jam...</p>
```

### 14.8 `dateModified` jujur

`growth-freshness` UPDATE `posts_meta.refreshed_at` → renderer pakai ini untuk `dateModified` schema. **JANGAN pernah ubah `datePublished`** (tidak jujur). Audit trail di `growth_log` lengkap.

### 14.9 Performance signals (Core Web Vitals)

- **LCP** < 2.5s → pakai `<img loading="eager">` untuk hero, lazy untuk sisanya
- **CLS** < 0.1 → set width/height semua img, font preload
- **FID/INP** < 100ms → `client:only="svelte"` (anti hydration mismatch)
- Total JS < 200KB gzipped per page

---

## 15. COMMON GOTCHAS (jangan ulangi kesalahan)

| # | Masalah | Fix |
|---|---------|-----|
| 1 | `client:visible` untuk Svelte → hydration mismatch | Wajib `client:only="svelte"` |
| 2 | `run_worker_first` cuma `["/blog/*"]` → 301 bypassed | Pakai `["/*"]` |
| 3 | D1 `all()` returns `{results:[]}` (plural), `.result` tidak ada | Selalu baca `.results` |
| 4 | `renderX` async di dashboard interpolation | WAJIB `await renderX(...)` |
| 5 | Schedules PUT body `{"schedules":[...]}` | Wajib array mentah `[{"cron":"..."}]` |
| 6 | 5 cron limit CF free account | Time-gate di `scheduled()` handler |
| 7 | Error 1102 CPU ceiling | Refill buffer capped 500/run + batch 200 (lihat §9.5) |
| 8 | R2 shard 40MB → load all → memory blow | 1 shard per run + cursor advancement |
| 9 | `ai-text` markdown fences (` ```html ... ``` ) | Strip `^```html` + `^``` + ```$` |
| 10 | gpt-oss reasoning_tokens makan budget | Set `reasoning_effort: "low"` + `max_tokens ≥ 2048` |
| 11 | GPT/Llama 3.x sudah dihapus dari Groq | Pakai `openai/gpt-oss-20b/120b` + `qwen/qwen3.6-27b` |
| 12 | `deepseek-v4-flash-free` sudah dihapus dari Zen | Rotate 6 Zen free models di §9.1 |
| 13 | Daily email quota overshoot | SAFETY_BUFFER = 5 + per-campaign rotation §12.3 |
| 14 | Template literal bersarang di HTML dashboard | Pakai helper function, hindari `\`${var}\`` di dalam template |
| 15 | Worker upload tapi route 404 | Cek `wrangler.jsonc main` path (RELATIVE to wrangler dir). Ada 2 file `worker-entry.js`? |

---

## 16. CHECKLIST REPLIKASI (satu per satu)

```bash
□ 1. Clone/fork repo, cd ke web/
□ 2. Edit wrangler.jsonc: name, main, d1, r2, vars, triggers.crons, assets.run_worker_first
□ 3. npm install
□ 4. Build static: npm run build → dist/ terbentuk
□ 5. Buat D1 database: npx wrangler d1 create <db-name>
□ 6. Buat R2 bucket: npx wrangler r2 bucket create <bucket-name>
□ 7. Set secrets: wrangler secret put (lihat §4)
□ 8. Deploy: CLOUDFLARE_API_TOKEN=... CLOUDFLARE_ACCOUNT_ID=... npx wrangler deploy
□ 9. Setup routes: PUT schedules (5 cron, array mentah)
□ 10. Verifikasi: curl health-check + curl /api/admin/ai-test
□ 11. Migrasi D1 schema: POST /api/admin/migrate?token=...
□ 12. Setup GSC Indexing API:
     - GCP service account JSON
     - Tambah ke GSC property sebagai Owner
     - Set GSC_SITE_URL secret
□ 13. Setup Resend: daftar, verify domain, set RESEND_API_KEY
□ 14. Setup IndexNow: generate key, simpan di /<key>.txt, tambahkan ke robots.txt
□ 15. Setup Sitemap: @astrojs/sitemap plugin di astro.config.mjs
□ 16. Setup llms.txt: taruh di public/, route handler
□ 17. Setup robots.txt: allow AI crawlers (GPTBot, ClaudeBot, dll)
□ 18. Import keyword riset: POST /api/admin/keywords/import?token=...
□ 19. Tunggu cron hourly jalan 1×, verify D1 published: SELECT COUNT(*) FROM posts_meta WHERE generated=1
□ 20. Monitor 24 jam:
     - curl /api/admin/sync/posts (lean mode, no 1102)
     - curl /api/admin/email?tab=overview (quota 100/hari)
     - curl /api/admin/growth-log (enrich/ctr-fix/freshness jalan)
     - curl /api/cron/rank-sync&days=14 (GSC rank snapshot)
```

---

## 17. QUICK RECIPES (copy-paste)

### 17.1 Tambah service page baru
```bash
cp src/pages/jasa-iklan-facebook.astro src/pages/jasa-iklan-{nama}.astro
# Edit: title meta, eyebrow, H1, pricing tiers, features, FAQ, internal links
npm run build
npx wrangler deploy
```

### 17.2 Tambah blog post manual
```bash
# Append ke web/src/data/posts.json (atau D1 posts_meta + posts_content)
# Test di /blog/{slug}/
```

### 17.3 Trigger cron manual
```bash
TOKEN="your-admin-token"
BASE="https://yourdomain.com"
curl -s "$BASE/api/cron/hourly-generate?token=$TOKEN" | jq .
curl -s "$BASE/api/cron/email/send?token=$TOKEN" | jq .
curl -s "$BASE/api/cron/growth/gsc-loop?token=$TOKEN&days=14" | jq .
curl -s "$BASE/api/cron/growth/enrich?token=$TOKEN&count=10" | jq .
curl -s "$BASE/api/cron/growth/ctr-fix?token=$TOKEN&count=20" | jq .
curl -s "$BASE/api/cron/growth/freshness?token=$TOKEN&count=20&ageDays=90" | jq .
```

### 17.4 Capture screenshots QA
```javascript
// /tmp/qa.mjs
import { chromium } from 'playwright';
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await ctx.newPage();
for (const url of ['/', '/jasa-iklan-facebook/', '/jasa-iklan-tiktok/', '/order/', '/blog/']) {
  await page.goto('https://beriklan.co.id' + url + '?cb=' + Date.now(), { waitUntil: 'networkidle' });
  await page.waitForTimeout(2500);
  await page.screenshot({ path: `/tmp/qa-${url.replace(/\//g, '_') || 'home'}.png`, fullPage: true });
}
await browser.close();
```

---

## 18. AI-INDEXING SPECIFIC CHECKLIST

Untuk memastikan artikel Anda di-crawl & di-cite oleh Google AI Overview, ChatGPT, Perplexity, Gemini, Claude:

### 18.1 Schema.org wajib valid
```bash
# Test schema validity
curl -s "https://beriklan.co.id/jasa-iklan-facebook/" | grep -o 'application/ld+json' | wc -l
# Minimal harus ada 3 JSON-LD blocks: Organization, BreadcrumbList, ProfessionalService/Article
```

### 18.2 Heading hierarchy clean
```bash
# Pastikan 1 H1 per page, tidak ada skip level
curl -s "https://beriklan.co.id/blog/{slug}/" | grep -oE '<h[1-6]' | sort | uniq -c
```

### 18.3 FAQ format AI-friendly
- WAJIB `<h3>` + `<p>` pair (bukan bullet)
- WAJIB sebut pertanyaan lengkap (bukan "Tanya 1:")
- WAJIB jawab dengan 1-3 kalimat pendek langsung

### 18.4 `llms.txt` & `llms-full.txt`
Taruh di root:
- `/llms.txt` (~5-10 KB ringkasan)
- `/llms-full.txt` (50-100 KB, structured semua artikel + service)

### 18.5 robots.txt allow AI crawlers
Wajib allow:
- `GPTBot` (OpenAI)
- `ChatGPT-User` (OpenAI real-time)
- `ClaudeBot` + `anthropic-ai` (Anthropic)
- `PerplexityBot` (Perplexity)
- `Google-Extended` (Google Gemini + AI Overview)
- `CCBot` (Common Crawl, training data)
- `Applebot-Extended` (Apple Intelligence)

### 18.6 Schema.org FAQPage untuk service pages
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Berapa biaya pasang iklan Facebook di Beriklan?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Paket mulai Rp 5.000.000 per bulan untuk setup Meta Business Suite dan satu campaign. Paket Profesional Rp 12.000.000 per bulan untuk multi-campaign. Paket Premium Rp 25.000.000 per bulan untuk full-funnel Meta + Instagram + WhatsApp."
      }
    }
  ]
}
</script>
```

### 18.7 Content freshness signal
- Update artikel setiap 90 hari (`growth-freshness`)
- `dateModified` schema diupdate JUJUR (jangan ubah `datePublished`)
- Audit trail di `growth_log`

### 18.8 Track AI referrals
Tambah ke `Layout.astro` analytics snippet:
```javascript
// Track referrer dari AI tools
if (document.referrer.includes('chat.openai.com') ||
    document.referrer.includes('claude.ai') ||
    document.referrer.includes('perplexity.ai') ||
    document.referrer.includes('gemini.google.com') ||
    document.referrer.includes('bard.google.com')) {
  navigator.sendBeacon('/api/track/ai-referral', JSON.stringify({
    referrer: document.referrer,
    page: location.pathname,
    timestamp: Date.now()
  }));
}
```

Simpan di `ai_referrals` D1 table → audit channel AI mana yang kirim traffic.

---

## 19. ENDPOINT INVENTORY (salin & adaptasi)

### 19.1 Cron jobs (CF schedule)
| Cron | Endpoint | Fungsi |
|------|----------|--------|
| `0 * * * *` | `/api/cron/hourly-generate` | Generate 3 artikel AI dari queue |
| `0 * * * *` | `/api/cron/indexnow` | Submit batch 50 URL ke IndexNow |
| `0 * * * *` | `/api/cron/gsc-indexing` | Submit batch 30 URL ke GSC Indexing |
| `0 * * * *` | `/api/cron/sitemap-ping` | Ping search engines sitemap |
| `0 * * * *` | `/api/cron/growth/gsc-loop` | Tiap 6 jam: cari keyword opportunity dari GSC |
| `0 * * * *` | `/api/cron/growth/enrich` | Harian 09:00: rewrite paragraf + FAQ artikel |
| `0 * * * *` | `/api/cron/growth/ctr-fix` | Harian 09:00: rewrite SERP meta |
| `0 * * * *` | `/api/cron/growth/freshness` | Senin 02:00: callout update artikel |
| `*/15 * * * *` | `/api/cron/email/send` | Kirim email queue (per-campaign rotation) |
| `30 6 * * *` | `/api/cron/scrape-indonetwork` | Scrape lead database Indonesia |
| `0 7 * * *` | `/api/cron/scrape-google-places` | Scrape Google Places |
| `0 3 * * 1` | `/api/cron/snippet-optimize` | Optimize meta snippet mingguan |
| `0 */6 * * *` | `/api/cron/leads/process` | Pipeline lead: match + AI personalize + auto-campaign |

### 19.2 Admin endpoints (perlu `token` query param)
| Endpoint | Fungsi |
|----------|--------|
| `GET /api/admin/ai-test` | Probe Zen free models + Groq keys |
| `GET /api/admin/sync/posts?mirror=0\|1` | Trigger publish (lean atau full mirror) |
| `GET /api/admin/email?tab=overview\|campaigns\|wa\|leads` | Dashboard email |
| `GET /api/admin/drafts?format=json` | List draft + status |
| `GET /api/admin/audit/content` | Audit artikel tipis (< 3000 char) |
| `GET /api/admin/growth-log?action=enrich&limit=20` | Audit growth trail |
| `GET /api/admin/keywords/list?status=pending&service=jasa-view-live` | List keyword queue |
| `POST /api/admin/keywords/import` | Bulk import keyword |
| `GET /api/admin/gsc-whoami` | Verify GSC service account |
| `POST /api/admin/email/queue/reset?campaign_id=N` | Reset failed → pending |
| `GET /api/admin/wa` | WA click stats |

### 19.3 Public endpoints
| Endpoint | Fungsi |
|----------|--------|
| `GET /api/track/open?id={tid}` | 1×1 pixel + UPDATE opened_at |
| `GET /api/track/click?id={tid}&url={target}` | 302 redirect + UPDATE clicked_at |
| `POST /api/newsletter/subscribe` | Subscribe newsletter (rate limit 5/jam) |
| `GET /api/newsletter/unsubscribe?email=...` | Unsubscribe |
| `GET /llms.txt` | AI-crawler friendly site summary |
| `GET /sitemap-index.xml` | Sitemap index |

---

## 20. DEPLOY OPS

### 20.1 Manual deploy (rekomendasi)

```bash
# Di repo root
cd web
npm run build
\
CLOUDFLARE_API_TOKEN="cfut_xxx..." \
CLOUDFLARE_ACCOUNT_ID="xxx..." \
npx wrangler deploy

# Re-PUT 5 cron schedules (setelah deploy, wrangler bisa reset schedules)
TOKEN="cfut_xxx..."; ACC="xxx..."
curl -s -X PUT "https://api.cloudflare.com/client/v4/accounts/$ACC/workers/scripts/<name>/schedules" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '[{"cron":"0 * * * *"},{"cron":"*/15 * * * *"},{"cron":"30 6 * * *"},{"cron":"0 7 * * *"},{"cron":"0 3 * * 1"}]'
```

### 20.2 Verify live
```bash
curl -s -o /dev/null -w "HTTP %{http_code}\n" "https://yourdomain.com/"
curl -s "https://yourdomain.com/api/admin/ai-test?token=$TOKEN" | jq '.results | length'
curl -s "https://yourdomain.com/api/admin/sync/posts?token=$TOKEN" | jq '.mode, .d1_published, .elapsed_ms'
```

### 20.3 Recovery (kalau deploy rusak)
1. `rm -rf web/.wrangler web/node_modules/.vite web/.astro`
2. `kill $(lsof -ti:4321)`
3. Re-deploy
4. Hard refresh browser (`Cmd+Shift+R`)
5. Kalau Worker 500: cek Cloudflare dashboard → Logs → cari error message
6. Kalau ada bug di `worker-entry.js`: rollback via CF dashboard → Deployments → Rollback

---

## 21. MONITORING & DEBUGGING

### 21.1 Health checks harian
```bash
TOKEN="beriklan-admin-2026"
BASE="https://beriklan.co.id"

# 1. Home page
curl -s -o /dev/null -w "Home: %{http_code}\n" "$BASE/"

# 2. Sitemap
curl -s -o /dev/null -w "Sitemap: %{http_code}\n" "$BASE/sitemap-index.xml"

# 3. AI test (semua model)
curl -s "$BASE/api/admin/ai-test?token=$TOKEN" | jq '.results[] | {provider, status, ok}'

# 4. Publish status
curl -s "$BASE/api/admin/sync/posts?token=$TOKEN" | jq '{mode, d1_published, total_drafts_pending, published_today, daily_limit}'

# 5. Email quota
curl -s "$BASE/api/admin/email?token=$TOKEN&tab=overview" | grep -oE 'class="kpi-val">[^<]*' | head

# 6. Growth log
curl -s "$BASE/api/admin/growth-log?token=$TOKEN&limit=5" | jq '.log[] | {action, slug, error, created_at}'

# 7. GSC rank
curl -s "$BASE/api/cron/rank-sync?token=$TOKEN&days=14" | jq '{rows, elapsed_ms}'

# 8. Keyword queue stats
curl -s "$BASE/api/admin/keywords/list?token=$TOKEN&limit=1" | jq '{total, page, perPage}'
```

### 21.2 Audit trail lengkap (semua cron run)
```bash
curl -s "$BASE/api/admin/cron/runs?token=$TOKEN&limit=20" | jq '.runs[] | {cron_name, started_at, ok, error}'
```

### 21.3 Failure modes & recovery

| Symptom | Check | Fix |
|---------|-------|-----|
| Email `Skipped: Daily Resend limit` | OK normal | Tunggu besok 00:00 UTC |
| Sync-posts error 1102 | Workers Free CPU | Gunakan mirror gate `?mirror=0` (lean) |
| GSC Indexing 0 submit | Quota habis (200/hari) | Tunggu besok + lower `daily_limit` |
| Growth enrich 0 candidate | Filter terlalu ketat | Lower `minImp`, expand `posMax` |
| AI generation all-fail | ZEN_API_KEY + GROQ_API_KEY* missing | Set via `wrangler secret put` |
| Email queue stuck 12k pending | Per-campaign rotation bug | Update ke version terbaru (mirror gate fix) |
| AI Crawler tidak bisa akses | robots.txt block | Allow `GPTBot`, `ClaudeBot`, dll |

---

## 22. TIMELINE & ROADMAP

### 22.1 Done (as of 2026-08-26)
- ✅ Static Astro site (12 service pages, 827 blog posts)
- ✅ CF Worker dengan D1 + R2 + AI binding
- ✅ 5 cron schedule aktif (beriklanweb full)
- ✅ Email campaign (Resend 100/hari)
- ✅ Indexing pipeline (GSC 200/hari + IndexNow 50/batch)
- ✅ Growth loop (gsc-loop, enrich, ctr-fix, freshness)
- ✅ Lead pipeline (match + AI personalize + auto-campaign)
- ✅ WA click tracker + auto follow-up
- ✅ AI provider rotation (Zen 6 free + Groq 3 model)
- ✅ Mirror gate fix (sync-posts 1102 → solved)
- ✅ Email per-campaign rotation (QuotaMonopoly bug → fixed)
- ✅ llms.txt + AI-friendly schema.org
- ✅ AEO FAQPage structure

### 22.2 Next (Q3 2026)
- ⏳ GA4 + Plausible integration (replace any heavy analytics)
- ⏳ Self-host OpenCode Zen-style proxy (?)
- ⏳ A/B test landing pages via URL params + GSC segment
- ⏳ Multi-language (English version untuk cross-border)
- ⏳ Multi-region D1 (US + EU) untuk latency
- ⏳ AI-referral tracker di `ai_referrals` table
- ⏳ Auto-update `posts.json` GitHub mirror setiap 24 jam via cron

### 22.3 Ideas
- Podcast transcription → blog posts pipeline
- YouTube video → article pipeline (transcript + AI structure)
- Newsletter digest mingguan dari top 5 artikel
- Auto-detect broken link + alert
- Content pruning: artikel < 100 imp/month → archive
- Structured expert reviews (E-E-A-T signal)

---

## 23. APPENDIX A — Glossary

| Istilah | Definisi |
|--------|----------|
| **AEO** | Answer Engine Optimization — optimasi untuk AI Overview, ChatGPT, Perplexity |
| **CTA** | Call-to-Action (WhatsApp button, contact form) |
| **CLS** | Cumulative Layout Shift (Core Web Vital) |
| **CWV** | Core Web Vitals (LCP, CLS, INP/FID) |
| **E-E-A-T** | Experience, Expertise, Authoritativeness, Trustworthiness (Google quality signal) |
| **D1** | Cloudflare SQLite-based serverless database |
| **D1-first** | Render content dari D1 first, fallback ke static asset kalau tidak ada |
| **GSC** | Google Search Console |
| **JSDoc** | JavaScript documentation format |
| **MIME** | Multipurpose Internet Mail Extensions (email format) |
| **Mirror gate** | Query param `?mirror=1` untuk full sync posts.json ke GitHub, vs lean default |
| **Mirror sync** | Sync `posts_meta` + `posts_content` dari D1 ke `src/data/posts.json` di GitHub |
| **NPMI** | New Posts per Month Index (growth metric) |
| **OG** | Open Graph (Facebook meta tags) |
| **PAA** | People Also Ask (Google SERP feature) |
| **Pacing** | Publish rate per jam/hari (controlled via cron_settings) |
| **Resend** | Email API service (alternatif SendGrid, Mailgun) |
| **R2** | Cloudflare S3-compatible object storage |
| **SA** | Service Account (GCP JSON credential) |
| **SA360** | Google Search Ads 360 |
| **SERP** | Search Engine Results Page |
| **TPD** | Tokens Per Day (Groq rate limit) |
| **TPM** | Tokens Per Minute |
| **URL-prefix** | GSC property type (`https://www.domain.com/path/*`) |
| **sc-domain** | GSC property type (`sc-domain:domain.com`, includes semua subdomain) |
| **Workers Free** | Cloudflare free tier (100K req/hari, 10ms CPU/req) |
| **Workers Paid** | 30s CPU limit + 1M req/month gratis + $0.50/M requests |
| **WORM** | Write Once Read Many (R2 compliance mode) |

---

## 24. APPENDIX B — Source code reference

Lokasi file di repo ini:
- `web/src/worker-entry.js` — 14K lines, semua handler + AI + cron + DB schema migration
- `web/src/components/*.svelte` — Svelte 5 components
- `web/src/layouts/Layout.astro` — global shell + JSON-LD Organization + analytics
- `web/src/pages/*.astro` — 12 service + 1 blog index + dynamic `[slug]`
- `web/tailwind.config.cjs` — brand colors + typography scale
- `web/wrangler.jsonc` — Worker config + binding + triggers.crons
- `web/astro.config.mjs` — Astro + Svelte + Tailwind + sitemap
- `web/public/llms.txt` — AI-crawler summary
- `web/public/robots.txt` — AI crawler allow list + sitemap
- `web/public/data/posts-index.json` — runtime blog metadata (14KB)

Referensi live:
- Production: https://beriklan.co.id
- Workers.dev: https://beriklanweb.3smedianet.workers.dev
- Admin: https://beriklan.co.id/api/admin?token=…
- AI test: https://beriklan.co.id/api/admin/ai-test?token=…
- Growth log: https://beriklan.co.id/api/admin/growth-log?token=…

---

## 26. STATUS REPLIKASI —DOMAIN AKTIF

Blueprint ini sudah berjalan di **dua domain** (satu account Cloudflare, berbagi
kuota cron 5 trigger/account):

| Domain | Worker | D1 | Cron slot | Catatan |
|---|---|---|---|---|
| `beriklan.co.id` | `beriklanweb` | D1 utama | `0 * * * *` + `*/15 * * * *` | Full system aktif |
| `beriklan.my` | `beriklanmy` | `beriklan-my-seo` | `0 * * * *` | Growth + lead + indexing aktif, **email DIMATIKAN** (belum ada list) |

**Porting beriklan.my selesai 2026-08-26** (commit `44a5470` di repo `beriklan.my`):
- Growth loop (`gsc-loop`/`enrich`/`ctr-fix`/`freshness`) + tabel `growth_log` ✅
- Bulk `keywords/import` ✅
- `/llms-full.txt` dinamis ✅
- Mirror-gate `sync/posts` (lean default, `?mirror=1` full) ✅
- Lead pipeline (match + score + AI personalisasi + WA link), cron `campaign=0` ✅
- `robots.txt` allow AI crawlers ✅
- AI provider Zen-only + Groq fallback registry (Groq key belum dipasang) ✅

**Yang belum di beriklan.my:**
- Per-campaign email rotation (tidak perlu — email dimatikan)
- GROQ_API_KEY secret (fallback Zen rate-limit)
- GSC: SA `beriklanmy@cool-component-463913-b7` **sudah bisa akses** domain
  property `sc-domain:beriklan.my` (gsc-loop narik 119 rows ✅). Property
  URL-prefix (`https://beriklan.my/`) tidak ada di GSC — semua query pakai
  `env.GSC_SITE_URL` = domain property. `rank-sync` juga sudah bekerja via domain property.

**Konsolidasi cron 2 domain (3 dari 5 slot terpakai):**
- `beriklanweb`: `0 * * * *` (hourly, semua job time-gate) + `*/15 * * * *` (email-send).
- `beriklanmy`: `0 * * * *` (hourly, semua job time-gate; scrape-indonetwork h==6 UTC,
  scrape-google-places h==7 UTC, growth-enrich/ctr-fix h==9 UTC, freshness Senin 02:00 UTC).
- Slot khusus `30 6 * * *` / `0 7 * * *` / `0 3 * * 1` sudah dilepas dari `beriklanweb`
  (digabung ke time-gate hourly) supaya cap 5 trigger/account cukup untuk 2 domain.
- Setelah `wrangler deploy` schedules bisa ke-reset sesuai `wrangler.jsonc` →
  re-PUT manual via API (body array mentah) jika perlu.

---

**Versi dokumen:** 2.2
**Update terakhir:** 26 Agustus 2026 (replication status 2 domain + konsolidasi cron 3 slot)
**Maintainer:** Beriklan Digital Agency + Codex AI
**Lisensi:** Bebas disalin & adaptasi untuk project sendiri.
