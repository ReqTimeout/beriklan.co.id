# 🎯 SEO Plan: Beriklan.co.id — Dominasi Google #1 Semua Layanan × Semua Kota

> **Target:** No.1 di Google untuk semua keyword "jasa [layanan] [kota]" di 30+ kota Indonesia. Maksimal AdSense revenue. Auto-indexing 24/7.
>
> **Tanggal:** 13 Juli 2026
> **Status:** Production live di `beriklan.co.id` (Cloudflare Workers)
> **Update berkala:** Setiap milestone selesai

---

## 0. EXECUTIVE SUMMARY

| Komponen | Status Saat Ini | Target | Timeline |
|----------|----------------|--------|----------|
| Domain authority (DA) | ~5 (estimasi) | 25+ dalam 6 bln | Continuous |
| Indexed pages | 827 blog + ~15 service | 1000+ (blog + 300+ city pages) | 90 hari |
| Keywords ranked page-1 | 0 (estimasi) | 50+ dalam 3 bln, 200+ dalam 6 bln | 90-180 hari |
| Monthly organic traffic | ? (belum diukur) | 50K visitors/bulan di Q3 | 90 hari |
| AdSense revenue | 0 saat ini (fresh) | Rp 5-15jt/bulan di Q3 | 60-180 hari |
| Auto-indexing | Manual | Fully automated 24/7 | 14 hari |

**ROI Project:** AdSense Rp 10jt/bln × 12 = Rp 120jt/tahun. Plus leads dari organic traffic (estimated value Rp 50-200jt/tahun).

---

## 1. CURRENT STATE AUDIT (dari pengamatan live)

### 1.1 Yang SUDAH jalan ✅

| Item | Status | Lokasi |
|------|--------|--------|
| Static site live | ✅ 840 pages built | `beriklanweb.3smedianet.workers.dev` + `beriklan.co.id` |
| Blog 827 posts imported | ✅ All rendered | `web/src/data/posts.json` |
| Featured image fallback | ✅ Unsplash per category | `BlogFilter.svelte` |
| Sitemap (multiple) | ✅ 4 types | `sitemap_index.xml`, `post-sitemap.xml`, `page-sitemap.xml`, `sitemap-index.xml` |
| SEO meta tags (page-specific) | ✅ After recent fix | All 13+ pages have proper title/desc/canonical |
| Schema markup | ✅ 2 types | ProfessionalService + Organization per page |
| AdSense integration | ✅ Blog post only | 2 ad slots per post |
| SEO verification files | ✅ 4 files | ads.txt, yandex, google×2, BingSiteAuth |
| Favicon | ✅ Multi-format | favicon.ico, apple-touch-icon, og-image |

### 1.2 Yang BELUM ada ❌

| Item | Status | Impact |
|------|--------|--------|
| **Per-city landing pages** | ❌ Belum ada | High — biggest growth opportunity |
| **Pillar/cluster content model** | ❌ Belum ada | High — Google rewards topical authority |
| **Schema LocalBusiness per city** | ❌ Belum ada | Medium-High |
| **Schema Service per service** | ❌ Belum ada | Medium |
| **Schema FAQ per page** | ❌ Belum ada | Medium |
| **Breadcrumb navigation** | ❌ Sebagian | Medium |
| **Author/Expert E-E-A-T signals** | ❌ Tidak ada | High (YMYL pages) |
| **LocalBusiness NAP consistency** | ❌ Belum dioptimasi | High |
| **Sitemap per content type** | ❌ Hanya 4 (perlu 6-7) | Low |
| **Topical clustering** | ❌ Belum ada | High |
| **Hreflang (EN/ID)** | ❌ Belum | Low (saat ini ID only) |
| **Canonical chains (paginated)** | ❌ Belum | Low-Medium |
| **Content freshness engine** | ❌ Belum (manual only) | High |
| **Internal link optimizer** | ❌ Belum | High |
| **IndexNow auto-submit** | ❌ Manual | High |
| **Rank tracker** | ❌ Belum | Medium |
| **GSC monitoring** | ❌ Belum setup | High |
| **Schema.org HowTo** | ❌ Belum | Low |
| **AggregateRating review schema** | ❌ Belum | Medium |
| **VideoObject schema** | ❌ Belum (kami ada video mockup) | Low |

### 1.3 Cloudflare Free Tier Limit (sudah dipatuhi)

| Resource | Limit | Current Usage | Headroom |
|----------|-------|---------------|----------|
| Worker requests/day | 100,000 | ~50/day | 99.95% |
| Worker CPU/invocation | 30s | ~5s | OK |
| Cron triggers | **2 max** | 0 (akan pakai 2) | Tight |
| Worker Analytics events/day | 100,000 | 0 | OK |
| R2 storage | 10GB | 0 | OK |
| Pages builds/month | 500 | ~5 | OK |
| KV reads/day | 100,000 | 0 | OK |
| DNS records | Unlimited | 25 | OK |

**Critical:** Hanya 2 cron triggers. Semua logic date-based di-handle di dalam Worker, bukan trigger terpisah.

---

## 2. GAP ANALYSIS — Apa yang Menghalangi No.1 di Google

### 2.1 Missing: Per-City Landing Pages

**Saat ini:** 10 service pages (tingkat nasional, generic)
**Target:** 10 services × 30+ kota = 300+ landing pages hyperlocal

**Contoh URL structure:**
```
/jasa-iklan-facebook/                     (national — current)
/jasa-iklan-facebook/jakarta/             (new)
/jasa-iklan-facebook/bandung/             (new)
/jasa-iklan-facebook/surabaya/            (new)
...
```

Setiap city page:
- Unique intro mentioning local landmarks, demographics
- Local case study / testimonial
- Map of service area
- Pricing same as national (rate card)
- Local trust signals (e.g., "Melayani Jakarta sejak 2016")
- Schema: LocalBusiness + Service + FAQ

**Volume calculation:**
- 10 services × 30 cities = 300 pages
- 10 service hubs × 30 cities = 30 city pages (jakarta/agency-iklan-facebook-jakarta, etc.)
- 30 city hubs with all services
- Total: ~360 new pages

### 2.2 Missing: Topical Authority / Pillar-Cluster Model

**Current state:** Blog posts are mostly independent. No clear topical clusters.

**Target structure:**
```
PILLAR 1: Facebook Ads (pillar-page)
├── Cluster: Targeting
│   ├── Blog post 1
│   ├── Blog post 2
│   └── Blog post 3
├── Cluster: Creative
│   ├── Blog post 1
│   └── ...
├── Cluster: Optimization
└── Cluster: Case Studies

PILLAR 2: Google Ads
... (same structure)

PILLAR 3-N: Same for each service
```

**Implementation:**
- Add 1 pillar page per service (`/jasa-iklan-facebook/pilar/`)
- Group existing blog posts into clusters
- Internal link from blog → pillar → city pages

### 2.3 Missing: E-E-A-T Signals (Google YMYL)

**E-E-A-T** = Experience, Expertise, Authoritativeness, Trustworthiness

For digital marketing agency (financial advice YMYL-adjacent), E-E-A-T is critical for ranking.

**Add:**
- "About Tim Beriklan" page with credentials, certifications, years
- Author bio on each blog post (real team members or specific personas)
- "Press / Media" page listing features
- "Klien & Testimoni" with real metrics
- "Metodologi" page describing our process
- Awards/certifications (Meta Business Partner, Google Partner, etc.)

### 2.4 Missing: AdSense Revenue Optimization

**Current AdSense setup:** Basic in-content ad on blog post only
**Target:** Multi-placement, high-CTR, auto ads enabled

**Strategy:**
1. Enable AdSense Auto Ads (let Google optimize)
2. Add 4-5 manual ad slots per blog post:
   - Above-fold banner (728×90)
   - In-content after intro paragraph
   - Mid-content (between h2 sections)
   - Sidebar matched content
   - After-content
3. Heatmap-based placement optimization
4. Anchor ad on long-form content
5. Vignette ad for sticky bottom

### 2.5 Missing: IndexNow (24-hour indexing)

**Current:** Manual submission only (none automated)
**Target:** New URLs indexed within hours of publish

**IndexNow support:**
- Bing (global)
- Yandex (Russia, but indexes for RU traffic)
- Seznam (Czech)
- Naver (Korea)
- IndexNow.org (Microsoft, picks up Bing automatically)

**Submit strategy:**
- All new blog posts within 5 minutes of publish
- All new city pages within 5 minutes
- Update existing posts → re-submit (priority tier)

---

## 3. ARCHITECTURE

```
┌──────────────────────────────────────────────────────────────────┐
│                  STATIC SITE (CF Workers)                        │
│  ─────────────────────────────────────────────────────────────  │
│  - Astro 5 + Svelte 5 + Tailwind                              │
│  - 800+ pages: blog, service, city, pillar                      │
│  - Built from GitHub repo main branch                          │
│  - Deployed via `beriklanweb.3smedianet.workers.dev`          │
└──────────────────────────────────────────────────────────────────┘
                              ↑
              build trigger (push to main)
                              │
┌──────────────────────────────────────────────────────────────────┐
│                       GitHub                                     │
│  ─────────────────────────────────────────────────────────────  │
│  Repo: github.com/ReqTimeout/beriklan.co.id                    │
│  - source code (web/src)                                        │
│  - data files (web/src/data)                                    │
│  - scripts/ (Python automation)                                  │
│  - workflows/ (CF Worker deploy config)                          │
└──────────────────────────────────────────────────────────────────┘
              ↓                            ↑
   (push data updates)             (CF API call)
              │                            │
              ↓                            │
┌──────────────────────────────────────────────────────────────────┐
│              AUTOMATION (3 layers)                                │
│  ─────────────────────────────────────────────────────────────  │
│                                                                    │
│  1. Cloudflare Worker Cron (beriklancoid) — 2 triggers max      │
│     ├─ 06:00 UTC: freshness + IndexNow + Sunday link rotation   │
│     └─ 18:00 UTC: freshness + IndexNow + 1st/15th keyword gen  │
│                                                                    │
│  2. Hostinger Cron (cron.daily) — secondary backup              │
│     └─ curl https://beriklancoid.3smedianet.workers.dev/trigger │
│                                                                    │
│  3. Manual triggers (admin only)                                │
│     └─ Dashboard URL: ...workers.dev/dashboard                  │
└──────────────────────────────────────────────────────────────────┘
                              ↓
              ┌───────────────────────────────┐
              ↓                               ↓
    ┌──────────────────┐         ┌──────────────────────┐
    │ IndexNow engines │         │ Google Search Console │
    │ - Bing           │         │ - Rank data           │
    │ - Yandex         │         │ - Indexing status     │
    │ - Sezam          │         │ - Coverage            │
    │ - Naver          │         └──────────────────────┘
    └──────────────────┘
```

---

## 4. CITY DOMINATION STRATEGY

### 4.1 Target Cities (30+)

**Tier 1 (Prioritas 1):** Jakarta, Bandung, Surabaya, Medan, Makassar
**Tier 2:** Semarang, Yogyakarta, Bogor, Tangerang, Bekasi, Depok
**Tier 3:** Palembang, Pekanbaru, Banjarmasin, Pontianak, Samarinda, Denpasar, Malang, Solo
**Tier 4:** Padang, Manado, Kupang, Jayapura, Ambon, Mataram, Yogyakarta, Cirebon, Tasikmalaya, Serang, Cilegon

### 4.2 URL Structure

**Existing (national):**
- `/jasa-iklan-facebook/`
- `/jasa-iklan-google/`
- etc.

**New (city-level):**
- `/jasa-iklan-facebook/jakarta/`
- `/jasa-iklan-facebook/bandung/`
- `/jasa-google-ads/jakarta/`
- etc.

**City hub (all services in one city):**
- `/jasa-iklan/jakarta/` (lists all 10 services for Jakarta)
- `/jasa-iklan/bandung/`
- etc.

### 4.3 Content Template (per city)

Each city page has these sections:

```markdown
# [Service] di [City] | [Brand]

Meta description: 150-160 chars with city + service + benefit

## Mengapa Bisnis di [City] Butuh [Service]
(Local market context: 2-3 specific facts about the city,
e.g., "Jakarta sebagai pusat bisnis Indonesia dengan 12jt+ UMKM aktif")

## Tantangan [Service] di Pasar [City]
(Local pain points: 2-3 specific to the city)

## Solusi Kami untuk [City]
- 2-3 service benefits
- Local case study or testimonial

## Paket & Harga [Service] [City]
(Pricing table — same as national)

## Area Layanan [Service] di [City]
- Daftar kecamatan/kawasan yang dilayani
- Map embed (optional)

## Klien Kami dari [City]
- 2-3 local testimonials (or generic with city mention)

## FAQ [Service] [City]
- 4-5 questions specific to local context

## CTA: Konsultasi Gratis
- WhatsApp button
```

### 4.4 Data File: `web/src/data/cities.json`

```json
[
  {
    "slug": "jakarta",
    "name": "Jakarta",
    "province": "DKI Jakarta",
    "tier": 1,
    "population": 10562088,
    "umkmCount": 350000,
    "neighborhoods": ["jakarta-selatan", "jakarta-pusat", "jakarta-utara", "jakarta-barat", "jakarta-timur"],
    "localFact1": "Jakarta sebagai pusat bisnis Indonesia dengan konsentrasi UMKM tertinggi",
    "localFact2": "70% brand lokal Jakarta aktif di Meta dan Google Ads",
    "lat": -6.2088,
    "lng": 106.8456
  },
  ...
]
```

### 4.5 Page Generator: `scripts/generate_city_pages.py`

Output: 300+ new `.astro` files → commit → push → CF auto-build

---

## 5. AUTOMATED SEO FEATURES (detail)

### 5.1 Content Freshness Engine

**File:** `scripts/seo/freshness.py`

**Schedule:** CF Worker cron 2x/day (06:00 + 18:00 UTC)

**Cara kerja:**
1. Load `posts-meta.json` (5MB, ringan untuk CF Worker)
2. Pilih 20 artikel random per cycle
3. Update `date` ke hari ini
4. Inject updated timestamp + minor content refresh:
   - 1 testimonial dari pool (perkota acak)
   - 1 FAQ dari pool
   - "Diperbarui: [tanggal]" annotation
5. Commit + push ke GitHub
6. Submit IndexNow untuk 20 URL yang di-refresh

**Cost:** 2 CF cron triggers max — sudah pakai 2 (06:00 + 18:00)

### 5.2 Internal Link Optimizer

**File:** `scripts/seo/rotate_internal_links.py`

**Schedule:** Mingguan (Sunday) di dalam cron 06:00 UTC

**Cara kerja:**
1. Build keyword index dari semua post
2. Group posts by topic cluster
3. Untuk setiap post, inject 4-6 link ke post lain dari cluster BUKAN yang sama dengan seed sebelumnya
4. Format link: `<a href="/blog/related-slug/">related title</a>`
5. Tempatkan di paragraf ke-5 (configurable)
6. Generate "Baca Juga" section di akhir post

**Expected impact:** Google sees internal link graph connecting all content → better crawl coverage + authority flow

### 5.3 IndexNow Multi-Engine Submitter

**File:** `scripts/seo/auto_index.py`

**Schedule:** setiap kali freshness/rotation commit

**Engines (all 4):**
- Bing: `https://www.bing.com/indexnow`
- Yandex: `https://yandex.com/indexnow`
- Seznam: `https://search.seznam.cz/indexnow`
- Naver: `https://searchadvisor.naver.com/indexnow`

**Submit logic:**
1. Read diff between current `index_log.json` and `posts-meta.json`
2. Submit new + updated URLs (max 10,000 per request)
3. Log submission result
4. Retry failed submissions (next cron cycle)

### 5.4 Rank Tracker (Google Search Console API)

**File:** `scripts/seo/rank_tracker.py`

**Setup required (one-time):**
1. Google Cloud Service Account + GSC API access
2. Save `gsc-credentials.json` (gitignored)
3. Share GSC property with service account email

**Schedule:** Weekly (Monday 00:00 UTC)

**Output:** Report to dashboard + email notification
- Top 50 keywords ranked
- Articles with rank drop (priority for refresh)
- Articles with impressions but 0 CTR (title/description issues)
- New queries that should become blog posts

### 5.5 City Page Generator

**File:** `scripts/seo/generate_city_pages.py`

**Trigger:** Manual (admin runs once, generates 300+ pages)

**Cara kerja:**
1. Read `cities.json` (30 cities × 10 services = 300 combos)
2. For each combo: generate `web/src/pages/jasa-[service]/[city].astro` from template
2. Inject city-specific data (population, UMKM count, local facts)
3. Auto-generate unique content snippets per city (avoid duplicate content penalty)
4. Add internal links to other cities (link to nearby cities in same service)

**Estimated output:** 300+ city pages + 30 city hub pages

### 5.6 Schema Generator

**File:** `scripts/seo/inject_schema.py`

**Trigger:** Build-time (runs in CF Pages build)

**Schema types to add per page type:**
- Home: LocalBusiness (primary), Organization, WebSite (with SearchAction)
- Service: Service, FAQPage (if FAQ exists)
- City: LocalBusiness, Service, FAQPage
- Blog post: Article, BreadcrumbList, Person (author)
- About: Organization, Person (team)
- Contact: LocalBusiness (with full address, hours, geo)

### 5.7 Content Generator (template-based)

**File:** `scripts/seo/generate_article.py`

**Trigger:** 1st & 15th of month (date-based)

**Cara kerja:**
1. Check `article_tracker.json` for `status: "pending"` keywords
2. Pick 2-3 pending keywords
3. Generate article using template + city/keyword data
4. Mark as `status: "generated"` in tracker
5. Push to GitHub via API

**Template strategy:** Each service has 5-7 article templates. Rotate to avoid duplicate content.

**Volume:** 4-6 new articles per month = 50-70 per year

---

## 6. FILES TO CREATE

### 6.1 Data files

| File | Purpose | Size |
|------|---------|------|
| `web/src/data/cities.json` | 30+ city data with local facts | ~10KB |
| `web/src/data/posts-meta.json` | Blog metadata only (no content) | ~5MB |
| `web/src/data/services.json` | Service metadata (descriptions, FAQs, testimonials) | ~30KB |
| `web/src/data/testimonials.json` | Pool of 50+ testimonials | ~20KB |
| `web/src/data/local-faqs.json` | Local SEO FAQ per city | ~15KB |
| `article_tracker.json` | Keyword tracking + generation status | ~1MB |
| `article_log.json` | Generated article history | ~500KB |
| `index_log.json` | IndexNow submission history | ~200KB |

### 6.2 CF Worker

| File | Purpose |
|------|---------|
| `seo-cron-worker/src/index.js` | Cron trigger (freshness, IndexNow, link rotation) |
| `seo-cron-worker/wrangler.toml` | Worker config + 2 cron triggers |
| `seo-cron-worker/src/dashboard.js` | Real-time dashboard route |

### 6.3 Python scripts (`scripts/seo/`)

| File | Purpose | Schedule |
|------|---------|----------|
| `freshness.py` | Refresh blog posts | 2x/day |
| `rotate_internal_links.py` | Cross-link optimization | Weekly |
| `auto_index.py` | IndexNow multi-engine | Every commit |
| `generate_city_pages.py` | Create 300+ city pages | Once (manual) |
| `generate_article.py` | Template content gen | 2x/month |
| `inject_schema.py` | JSON-LD schema inject | Build-time |
| `rank_tracker.py` | GSC rank monitoring | Weekly |
| `sitemap_splitter.py` | Multiple sitemaps by type | Every build |

### 6.4 Astro page templates

| File | Purpose |
|------|---------|
| `web/src/pages/jasa-[service]/[city].astro` | City-specific service page (10 × 30 = 300 files) |
| `web/src/pages/jasa-[service]/index.astro` | National service page (existing, update with city links) |
| `web/src/pages/wilayah/[city].astro` | City hub page (lists all services) |
| `web/src/components/CityNav.astro` | City navigation menu (in city pages) |
| `web/src/components/LocalSchema.astro` | LocalBusiness schema component |

---

## 7. INFRASTRUCTURE

### 7.1 Components

| Service | Purpose | Cost |
|---------|---------|------|
| **Cloudflare Workers** | Cron trigger (2x/day), Dashboard | Free tier |
| **Cloudflare Pages / Workers Assets** | Static site hosting | Free tier |
| **GitHub** | Source code + data files | Free (private repo) |
| **Google Search Console** | Rank data + index status | Free |
| **IndexNow (Bing/Yandex/Seznam/Naver)** | Fast indexing | Free |
| **Google AdSense** | Ad serving | Revenue share |
| **Hostinger shared hosting** | Cron backup, legacy WP if needed | Already paid |

### 7.2 CF Worker Cron Schedule (within 2 trigger limit)

```toml
[triggers]
crons = ["0 6 * * *", "0 18 * * *"]  # 06:00 UTC, 18:00 UTC
```

**06:00 UTC cycle:**
- Freshness: 20 random posts (idempotent)
- IndexNow: submit all URLs updated in last 24h
- Link rotation: if Sunday
- Ping sitemaps: always

**18:00 UTC cycle:**
- Freshness: another 20 random posts
- IndexNow: same
- Keyword gen: if 1st or 15th

### 7.3 Hostinger Cron (backup)

```bash
# /etc/cron.d/beriklan-seo (Hostinger)
0 12 * * * cd /home/user/beriklan && curl -X POST https://beriklancoid.3smedianet.workers.dev/trigger?key=... > /dev/null 2>&1
```

This calls the CF Worker endpoint as secondary trigger.

### 7.4 Daily Data Flow

```
06:00 UTC:
  CF Worker cron → API call to GitHub:
    1. Read posts-meta.json
    2. Pick 20 random posts
    3. Update date + inject content
    4. Write to posts.json
    5. git commit + push
  → CF Pages auto-build (GitHub webhook)
  → New dist/ generated
  → IndexNow API (Bing, Yandex, etc.)
  
Result: Blog 20 posts updated daily, Google sees fresh content
```

---

## 8. KEYWORD UNIVERSE & CONTENT CLUSTERS

### 8.1 Pillar Pages (10 services)

| Pillar | URL | Target Keywords |
|--------|-----|-----------------|
| Jasa Iklan Facebook | `/jasa-iklan-facebook/` | "jasa iklan facebook", "iklan fb", "fb ads agency" |
| Jasa Iklan Instagram | `/jasa-iklan-instagram/` | "jasa iklan instagram", "ig ads" |
| Jasa Iklan TikTok | `/jasa-iklan-tiktok/` | "jasa iklan tiktok", "tiktok ads" |
| Jasa Iklan Google | `/jasa-iklan-google/` | "jasa iklan google", "google ads agency" |
| Jasa Iklan YouTube | `/jasa-iklan-youtube/` | "jasa iklan youtube" |
| Jasa Kelola Instagram | `/jasa-kelola-instagram/` | "jasa kelola instagram", "social media management" |
| Jasa Kelola TikTok | `/jasa-kelola-tiktok/` | "jasa kelola tiktok" |
| Jasa Pembuatan Website | `/jasa-pembuatan-website/` | "jasa buat website", "jasa website" |
| Jasa Pembuatan Landing Page | `/jasa-pembuatan-landing-page/` | "jasa landing page" |
| Jasa Digital Marketing | `/jasa-digital-marketing/` | "jasa digital marketing" |

### 8.2 City Keyword Variants (per pillar)

For each pillar, 30 city variants:
- "jasa iklan facebook jakarta"
- "jasa iklan facebook surabaya"
- "agensi facebook ads bandung"
- "konsultan fb ads jogja"
- etc.

### 8.3 Total Keyword Targets

- 10 services × 30 cities = 300 city page targets
- 10 services + city pages = 310 pillar/target pages
- 827 blog posts (existing) = 827 long-tail targets
- 4-6 new articles/month = 50-70 new long-tail targets/year

**Total addressable keyword universe:** 1200+ unique keyword targets

---

## 9. ADSENSE OPTIMIZATION PLAN

### 9.1 Ad Placement Strategy

For each blog post (827 + new):

| Position | Ad Type | Size | Expected CTR |
|----------|---------|------|--------------|
| Above content (banner) | Display | 728×90 (responsive) | 0.5-1.0% |
| After intro paragraph | In-article | Fluid | 1.0-2.0% |
| Mid-content (after 2nd h2) | In-article | Fluid | 0.8-1.5% |
| Before conclusion | In-article | Fluid | 1.0-2.0% |
| After content | Display | 336×280 | 0.5-1.0% |
| Anchor (left side, desktop) | Anchor | Auto | 0.3-0.8% |
| Vignette (sticky bottom) | Vignette | Auto | 0.3-0.5% |

### 9.2 AdSense Auto Ads

Enable in AdSense dashboard:
- Display ads
- In-page ads
- Matched content (related articles)
- Anchor ads
- Vignette ads
- Auto optimize

### 9.3 Expected Revenue Calculation

**Assumptions:**
- 50K monthly pageviews (achievable in 6 months with city pages)
- Average RPM: Rp 25,000-50,000 (Indonesian market, ads on digital marketing topics)
- Click-through rate: 2%
- Revenue: 50,000 × Rp 30,000 / 1000 = **Rp 1.5M/month from pageviews alone**

With optimization:
- 100K monthly pageviews in 9 months
- RPM: Rp 35,000 (mid-roll)
- CTR: 2.5%
- Revenue: 100,000 × Rp 35,000 / 1000 = **Rp 3.5M/month**

**Year 1 target: Rp 30-50M total**

---

## 10. SCHEMA MARKUP PLAN

### 10.1 Schema by Page Type

| Page Type | Schema Types |
|-----------|---------------|
| Home | `LocalBusiness` + `Organization` + `WebSite` (with `SearchAction`) + `BreadcrumbList` |
| Service national | `Service` + `FAQPage` + `BreadcrumbList` |
| Service city | `LocalBusiness` (per city) + `Service` + `FAQPage` + `BreadcrumbList` + `AggregateRating` |
| City hub | `LocalBusiness` + `BreadcrumbList` |
| Blog post | `Article` + `BreadcrumbList` + `Person` (author) + `FAQPage` (if FAQ in content) |
| About | `Organization` + `Person[]` (team) |
| Contact | `LocalBusiness` (full NAP + hours + geo) |

### 10.2 Example: Service + City Page Schema

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "LocalBusiness",
      "@id": "https://beriklan.co.id/jasa-iklan-facebook/jakarta/#business",
      "name": "Beriklan.co.id Jakarta",
      "address": {
        "@type": "PostalAddress",
        "addressLocality": "Jakarta",
        "addressRegion": "DKI Jakarta",
        "addressCountry": "ID"
      },
      "geo": {
        "@type": "GeoCoordinates",
        "latitude": -6.2088,
        "longitude": 106.8456
      },
      "openingHoursSpecification": [...],
      "telephone": "+62-811-919-328"
    },
    {
      "@type": "Service",
      "serviceType": "Facebook Ads Management",
      "provider": {"@id": "https://beriklan.co.id/jasa-iklan-facebook/jakarta/#business"},
      "areaServed": {"@type": "City", "name": "Jakarta"},
      "offers": {"@type": "Offer", "priceCurrency": "IDR", "price": "1750000"}
    },
    {
      "@type": "FAQPage",
      "mainEntity": [...]
    }
  ]
}
```

---

## 11. INTERNAL LINKING STRATEGY

### 11.1 Hub & Spoke Model

```
                    [PILLAR: Jasa Iklan Facebook]
                                |
            ┌───────────────────┼───────────────────┐
            |                   |                   |
    [Cluster: Targeting] [Cluster: Creative] [Cluster: Optimization]
            |                   |                   |
        Blog post 1         Blog post 2         Blog post 3
        Blog post 4         Blog post 5         Blog post 6
            |                   |                   |
            └───────────────────┴───────────────────┘
                                ↓
        [CITY PAGE: Jakarta / Bandung / Surabaya]
        Each city links to all clusters in same service
```

### 11.2 Internal Link Rules

- Every blog post links to:
  - 1 related blog post in same cluster
  - 1 related pillar page (service)
  - 1 city page (nearest city)
  - 1 city hub page (city of primary business)

- Every service page links to:
  - All city pages for that service
  - 3 most recent blog posts in that service cluster
  - Pillar cluster overview

- Every city page links to:
  - All services in same city
  - 5 closest cities (geographically)

---

## 12. KEYWORD TARGETING & CONTENT STRATEGY

### 12.1 City-specific Long-tail (5-tier)

For each city × service:
1. **Primary**: "jasa [service] [kota]"
2. **Secondary**: "[service] [kota] profesional"
3. **Tertiary**: "harga [service] [kota]"
4. **Quaternary**: "agensi [service] terbaik [kota]"
5. **Quinary**: "konsultan [service] [kota]"

Each page targets 5 keyword variants naturally.

### 12.2 Competitor Analysis (jangka panjang)

Tools needed: Ahrefs/SEMrush (paid) — or use free:
- Google Search Console (free)
- Google Trends (free)
- Bing Webmaster (free)
- Ubersuggest free trial (limited)

Track competitors:
- https://mataharimarketing.com
- https://optimaise.com
- https://niagahoster.co.id/blog
- https://www.niagahoster.co.id
- etc.

---

## 13. FILES TO CREATE — DETAILED CHECKLIST

### Phase 1: Foundation (Week 1)
- [ ] `web/src/data/cities.json` — 30+ city data
- [ ] `web/src/data/services.json` — service metadata
- [ ] `web/src/data/testimonials.json` — 50+ testimonials
- [ ] `web/src/data/local-faqs.json` — FAQ per city
- [ ] `web/src/data/posts-meta.json` — generated from posts.json
- [ ] `web/src/components/CityNav.astro`
- [ ] `web/src/components/LocalSchema.astro`
- [ ] `web/src/layouts/Layout.astro` — add props for city

### Phase 2: City Pages (Week 2-3)
- [ ] `scripts/seo/generate_city_pages.py` — generator
- [ ] `web/src/pages/jasa-iklan-facebook/[city].astro` × 30
- [ ] `web/src/pages/jasa-iklan-instagram/[city].astro` × 30
- [ ] ... (10 services × 30 cities = 300 files)
- [ ] `web/src/pages/wilayah/[city].astro` × 30 (city hub)
- [ ] `web/src/pages/jasa/index.astro` (jasa-iklan hub)

### Phase 3: Automation (Week 3-4)
- [ ] `scripts/seo/freshness.py`
- [ ] `scripts/seo/rotate_internal_links.py`
- [ ] `scripts/seo/auto_index.py`
- [ ] `scripts/seo/inject_schema.py`
- [ ] `scripts/seo/rank_tracker.py`
- [ ] `scripts/seo/generate_article.py`
- [ ] `scripts/seo/sitemap_splitter.py`
- [ ] `seo-cron-worker/src/index.js`
- [ ] `seo-cron-worker/src/dashboard.js`
- [ ] `seo-cron-worker/wrangler.toml`

### Phase 4: Schema & Pillar (Week 4-5)
- [ ] `web/src/pages/jasa-iklan-facebook/pilar/index.astro` (pillar page)
- [ ] ... (10 pillar pages)
- [ ] `web/src/pages/tentang-kami.astro` (about)
- [ ] `web/src/pages/klien.astro` (testimonial hub)
- [ ] `web/src/pages/metodologi.astro` (methodology)
- [ ] `web/src/pages/blog/[slug].astro` — add author bio + breadcrumb
- [ ] `web/src/components/Author.astro`
- [ ] `web/src/components/Breadcrumb.astro`

### Phase 5: Optimization (Week 5-6)
- [ ] AdSense Auto Ads enabled
- [ ] Manual ad placement optimization
- [ ] Page speed optimization (LCP < 2s)
- [ ] Image AVIF/WebP variants
- [ ] Critical CSS inlining

---

## 14. CRON & WORKFLOW CONFIGURATION

### 14.1 Cloudflare Worker (seo-cron)

```toml
# seo-cron-worker/wrangler.toml
name = "beriklan-seo-cron"
main = "src/index.js"
compatibility_date = "2026-01-01"

[triggers]
crons = ["0 6 * * *", "0 18 * * *"]

[vars]
SITE = "https://beriklan.co.id"
GITHUB_REPO = "ReqTimeout/beriklan.co.id"
GITHUB_TOKEN_SECRET_NAME = "GH_PUSH_TOKEN"
INDEXNOW_KEY = "..."
```

### 14.2 CF Worker `src/index.js` (sketch)

```javascript
export default {
  async scheduled(event, env, ctx) {
    const hour = new Date(event.scheduledTime).getUTCHours();
    const isSunday = new Date().getUTCDay() === 0;
    const day = new Date().getUTCDate();
    
    if (hour === 6) {
      await runFreshness(env, 20);
      if (isSunday) await runLinkRotation(env, 50);
    }
    
    if (hour === 18) {
      await runFreshness(env, 20);
      if (day === 1 || day === 15) await runKeywordGen(env, 3);
    }
    
    await runIndexNow(env);
  }
};
```

### 14.3 Hostinger Cron (backup)

```bash
# Add to Hostinger cPanel → Cron Jobs
0 12 * * * curl -fsS https://beriklancoid.3smedianet.workers.dev/backup-trigger?key=... > /dev/null
```

---

## 15. MONITORING & KPIs

### 15.1 Daily Metrics
- Indexed pages (GSC)
- New URLs submitted to IndexNow
- Freshness updates count
- Site uptime

### 15.2 Weekly Metrics
- Organic traffic (GSC)
- Top 50 keywords ranking
- AdSense revenue
- Ad CTR by placement

### 15.3 Monthly Metrics
- New content published
- City page index rate
- Backlink profile
- Domain authority growth

### 15.4 Dashboard

`https://beriklancoid.3smedianet.workers.dev/dashboard`

Shows:
- Last 30 days of organic traffic
- Top 20 keywords ranked
- IndexNow status (last 7 days)
- Recent freshness updates
- AdSense revenue
- System health

---

## 16. RISKS & MITIGATION

| Risk | Impact | Mitigation |
|------|--------|-------------|
| CF cron 2 trigger limit | High | Date-based logic in Worker code, not separate triggers |
| CF Worker 30s CPU limit | Medium | Optimized fetch, batching, lightweight operations |
| 827 posts.json = 4MB | Low (already in posts-meta.json) | Use posts-meta for routine ops |
| Hostinger cron unreliable | Medium | Use as backup only, primary = CF Worker |
| AdSense ad blindness | Low | Use native ad formats (not inserted) |
| GSC API rate limit (2k/day) | Low | Cache results, query weekly only |
| Google algorithm changes | High | Diversify traffic sources (AdSense, direct, social) |
| Duplicate content penalty | High | Unique intro per city page, varied testimonials |
| IndexNow rejected URLs | Low | Engine retries, fallback to next engine |
| GSC service account setup | Medium | One-time setup, document in README |

---

## 17. 90-DAY ROLLOUT PLAN

### Week 1: Foundation
- Day 1-2: Create `cities.json`, `services.json`, `testimonials.json`
- Day 3-4: Build `city/[city].astro` page template
- Day 5-7: Setup `seo-cron-worker` with 2 cron triggers

### Week 2-3: City Pages
- Day 8-10: Generate first 5 cities × 10 services = 50 pages
- Day 11-14: Add remaining 25 cities × 10 services = 250 pages
- Day 15-21: City hub pages (30) + service hub updates

### Week 4: Schema & SEO Foundation
- Day 22-25: Add LocalBusiness schema per city page
- Day 26-28: Add breadcrumb navigation component
- Day 29-30: E-E-A-T pages (About, Klien, Metodologi)

### Week 5: Automation
- Day 31-33: Deploy `freshness.py` to GitHub Actions
- Day 34-36: Deploy `auto_index.py` + IndexNow integration
- Day 37-39: Deploy `rotate_internal_links.py`
- Day 40-42: Set up GSC service account for `rank_tracker.py`

### Week 6: AdSense & Optimization
- Day 43-46: Enable AdSense Auto Ads
- Day 47-49: Implement 4 manual ad slots per blog post
- Day 50-52: Page speed optimization

### Week 7-8: Monitoring & Adjustment
- Day 53-60: Monitor GSC for first indexing
- Day 61-67: Adjust content based on rank tracker data

### Week 9-12: Content Generation
- Day 68-90: Run keyword_gen + content gen monthly
- Track 50+ keywords moving up in rankings
- Submit more URLs to IndexNow

### Day 90 Milestone:
- 1000+ pages indexed in Google
- 100+ keywords ranking page-1-3
- AdSense revenue: Rp 1-3M/month
- Organic traffic: 10K-30K/month

---

## 18. QUICK START (Priority Order)

### Day 1: Foundation files
```bash
cd /Users/maabook/Desktop/beriklan.co.id/web
mkdir -p scripts/seo
# Create cities.json, services.json, testimonials.json
```

### Day 2-3: City page template + first 10 pages
```bash
# Create src/pages/jasa-iklan-facebook/[city].astro
# Create 30 cities × 10 services = 300 pages via script
python3 scripts/seo/generate_city_pages.py --initial
```

### Day 4: Deploy SEO automation
```bash
# Deploy CF Worker
cd seo-cron-worker
npx wrangler deploy
```

### Day 5: Verify
```bash
# Check worker triggers
curl https://beriklan-seo-cron.3smedianet.workers.dev/

# Check sitemap
curl https://beriklan.co.id/sitemap_index.xml
```

---

## 19. CRITICAL SUCCESS FACTORS

1. **Content quality beats quantity** — 100 kota × 10 service = 1000 pages hanya value kalau setiap page UNIK. Template-based generation dengan city-specific variation.

2. **Internal linking matrix** — Google menilai authority flow. Setiap page harus link ke 5-10 page lain secara natural.

3. **IndexNow speed** — Submit dalam 1 jam setelah publish. Kalau Google lama indeks, content loses first-mover advantage.

4. **Real local data** — Pakai data spesifik kota (population, UMKM count, local case study). Jangan generic.

5. **Schema depth** — Multi-type schema per page (LocalBusiness + Service + FAQ + Breadcrumb + Review). Google rich results prefer comprehensive markup.

6. **Mobile-first** — 75%+ traffic Indonesia dari mobile. Setiap page harus sempurna di mobile.

7. **AdSense loading** — Lazy load ads, jangan ganggu Core Web Vitals. PageSpeed < 80 = drop ranking.

---

## 20. REVENUE PROJECTION (12-Month Forecast)

| Quarter | Indexed Pages | Organic Traffic | AdSense Revenue | Notes |
|---------|---------------|-----------------|-----------------|-------|
| Q1 (Month 1-3) | 1,200 | 10K-30K visits | Rp 1-3M | Setup phase |
| Q2 (Month 4-6) | 1,500 | 30K-80K visits | Rp 5-15M | Growth phase |
| Q3 (Month 7-9) | 1,800 | 80K-150K visits | Rp 15-30M | Monetization |
| Q4 (Month 10-12) | 2,000+ | 150K-300K visits | Rp 30-60M | Mature |

**Conservative estimate (Q4):** Rp 30M/month organic AdSense
**Optimistic estimate (Q4):** Rp 60M/month
**Annual estimate:** Rp 200-500M AdSense revenue

Plus **leads from organic** (service inquiries) worth additional Rp 50-200M/year.

---

## 21. NOTES

- **Berani ambil risiko yang aman** — Algoritma Google berubah. Diversifikasi trafik: AdSense (display) + direct (WA leads) + SEO (organic) + social (FB, IG, TikTok).
- **Content = moat** — Competitor tidak akan copy 300+ city pages dengan unique content dalam 6 bulan. First mover advantage.
- **Crawl budget optimization** — sitemap segmentation + canonical chains. Google crawl prioritization.
- **White hat 100%** — Tidak ada PBN, cloaking, hidden text. Semua gray hat dilakukan di legitimate boundary (aggressive schema, comprehensive content, internal linking, technical SEO).

---

**END OF PLAN**
