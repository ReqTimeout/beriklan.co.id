# SEO & Growth Strategy — Beriklan.co.id

> **Tujuan utama:**
> 1. **#1 Google untuk semua keyword relevan** (jasa iklan Indonesia)
> 2. **AdSense revenue scale-up** (pageviews × RPM tinggi)
> 3. **Customer matching** (lead WA berkualitas ke admin)
>
> **Versi:** 3.0 (2026-07-20) — audit ulang dengan 7 gap baru ditemukan
> **Maintainer:** Beriklan Digital Agency + AI coding agent
> **Update terakhir:** Lihat git log `SEO-STRATEGY.md`

---

## 📊 STATUS LEGEND

- ✅ **Done** — implemented + live + verified
- 🔄 **In progress** — partially implemented
- ❌ **Pending** — belum implementasi
- 🚀 **Quick win** — high impact, low effort (≤4 jam)
- 🎯 **Strategic** — critical untuk goal utama
- 💡 **Nice-to-have** — nice tapi bukan blocker

---

## 🏗️ ARSITEKTUR PIPELINE (BIG PICTURE)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        CONTENT GENERATION PIPELINE                       │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐             │
│  │ KEYWORD     │───▶│ ARTICLE      │───▶│ POSTS.JSON      │             │
│  │ SOURCES     │    │ GENERATION   │    │ (2027+ posts)   │             │
│  ├─────────────┤    ├──────────────┤    └─────────────────┘             │
│  │ • Suggest   │    │ • Zen AI     │             │                      │
│  │ • Trends    │    │ • Groq (fb)  │             ▼                      │
│  │ • PAA       │    │ • Batch4     │    ┌─────────────────┐             │
│  │ • Competitor│    │ • Trending   │    │ D1 PENDING_     │             │
│  │ • Manual    │    └──────────────┘    │ INDEXING        │             │
│  └─────────────┘                        └─────────────────┘             │
│         │                                       │                        │
│         ▼                                       ▼                        │
│  ┌──────────────────────────┐         ┌─────────────────┐              │
│  │ keyword-queue.json       │         │ INDEXNOW + GSC  │              │
│  │ 2763 → target 7000+      │         │ submit URLs     │              │
│  └──────────────────────────┘         └─────────────────┘              │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

**Target throughput:** 5 artikel/jam × 24 jam = 120/hari = 3600/bulan = 43.800/tahun

---

## 📈 PHASE ROADMAP — 6 BULAN KE #1

### PHASE 1 (Minggu 1-2): **VOLUME FOUNDATION** ✅ ~80% done

| # | Item | Status | Effort | Impact |
|---|------|--------|--------|--------|
| 1.1 | Keyword queue 2763 (Suggest + miner) | ✅ Done | - | Coverage dasar |
| 1.2 | 1200+ artikel via Zen deepseek-v4-flash-free | ✅ Done | - | Konten awal |
| 1.3 | `/api/index-url` enqueue auto-post | ✅ Done | - | Auto IndexNow |
| 1.4 | 1.200 artikel retrofitted dengan internal-cta | ✅ Done | - | Money page link juice |
| 1.5 | 130 per-city view-live pages (5×26) | ✅ Done | - | Local SEO coverage |
| 1.6 | 3.250 cross-city internal links | ✅ Done | - | Crawl discovery |
| 1.7 | Clamp future dates (freshness jujur) | ✅ Done | - | Trust signal |
| 1.8 | Favicon orange "b" + cache-buster | ✅ Done | - | Brand recall |
| 1.9 | Blog index mobile cards reveal fix | ✅ Done | - | UX |
| 1.10 | `/api/admin/keywords` pipeline dashboard | ✅ Done | - | Visibility |
| 1.11 | AdSense loader di blog + city pages | ✅ Done | - | Revenue |
| 1.12 | **❌ Pending: `/api/cron/hourly-generate`** | ❌ Pending | 🚀 2 jam | 5 artikel/jam otomatis |
| 1.13 | **❌ Pending: keyword expansion ke 7000+** | ❌ Pending | 🚀 1 jam | Coverage 2.5× |

### PHASE 2 (Minggu 3-4): **CRAWL & INDEX SPEED**

| # | Item | Status | Effort | Impact |
|---|------|--------|--------|--------|
| 2.1 | IndexNow submit per artikel baru | 🔄 Partial | 🚀 30m | Crawl minutes |
| 2.2 | GSC Sitemap refresh harian | ✅ Done | - | Index coverage |
| 2.3 | **❌ Pending: GSC Indexing API (instant request)** | ❌ Pending | 🚀 1 jam | Crawl hours, not days |
| 2.4 | **❌ Pending: Auto-link artikel baru ke 3-5 related posts** | ❌ Pending | 🚀 1 jam | Crawl discovery |
| 2.5 | Sitemap split 7 jenis | ✅ Done | - | Crawl budget efisien |
| 2.6 | Mobile responsive + overflow fix | ✅ Done | - | Mobile UX |
| 2.7 | **❌ Pending: Page speed audit + LCP < 2s** | ❌ Pending | 🎯 1 hari | Ranking signal |
| 2.8 | **❌ Pending: Trending auto-generate (bukan 1×/cron)** | ❌ Pending | 🚀 4 jam | Google Trends harian → artikel |
| 2.9 | **❌ Pending: Hub pages / pillar clusters per service** | ❌ Pending | 🎯 2 hari | Topical authority |

### PHASE 3 (Bulan 2): **TOPICAL AUTHORITY & SNIPPETS**

| # | Item | Status | Effort | Impact |
|---|------|--------|--------|--------|
| 3.1 | Service pages + FAQ schema | ✅ Done | - | Featured snippet |
| 3.2 | BreadcrumbList schema | ✅ Done | - | Rich snippet |
| 3.3 | Article schema | ✅ Done | - | News ranking |
| 3.4 | **❌ Pending: People Also Ask (PAA) content di setiap artikel** | ❌ Pending | 🎯 3 hari | Slot #0 Google |
| 3.5 | **❌ Pending: Featured snippet optimization (numbered list, table, definisi)** | ❌ Pending | 🎯 2 hari | Snippet ranking |
| 3.6 | **❌ Pending: Pillar page per service (panduan lengkap 5000+ kata)** | ❌ Pending | 🎯 3 hari | Authority signal |
| 3.7 | **❌ Pending: Cluster articles auto-link ke pillar** | ❌ Pending | 🚀 2 jam | Internal SEO juice |
| 3.8 | **❌ Pending: Original research / data survey** | ❌ Pending | 🎯 1 minggu | Backlink magnet |
| 3.9 | **❌ Pending: Calculator tools (budget iklan, ROAS, dll)** | ❌ Pending | 🎯 1 minggu | Dwell time + backlinks |

### PHASE 4 (Bulan 3): **OFF-PAGE & BRAND**

| # | Item | Status | Effort | Impact |
|---|------|--------|--------|--------|
| 4.1 | **❌ Pending: Google Business Profile setup + optimize** | ❌ Pending | 🎯 1 hari | **Local SEO WAJIB** |
| 4.2 | **❌ Pending: Backlink strategy — 50 directory submissions** | ❌ Pending | 🎯 3 hari | Domain authority |
| 4.3 | **❌ Pending: Guest posts 5 situs DR>50** | ❌ Pending | 🎯 2 minggu | Authority naik |
| 4.4 | **❌ Pending: YouTube channel (video embed di setiap artikel)** | ❌ Pending | 🎯 1 minggu | Double SERP exposure |
| 4.5 | **❌ Pending: TikTok account (cross-post short video)** | ❌ Pending | 🎯 1 minggu | Brand entity |
| 4.6 | **❌ Pending: LinkedIn company page + thought leadership** | ❌ Pending | 🎀 2 hari | B2B leads |
| 4.7 | **❌ Pending: HARO / journalist outreach untuk backlink** | ❌ Pending | 🎯 ongoing | DR boost |
| 4.8 | **❌ Pending: Podcast appearance (3-5 episode)** | ❌ Pending | 💡 1 bulan | Brand awareness |

### PHASE 5 (Bulan 4-5): **CONVERSION OPTIMIZATION**

| # | Item | Status | Effort | Impact |
|---|------|--------|--------|--------|
| 5.1 | WA CTA dengan konteks (template per tier) | ✅ Done | - | Lead quality |
| 5.2 | Pricing transparency di setiap service page | ✅ Done | - | Trust |
| 5.3 | Testimonials + case studies | 🔄 Partial | 🎯 1 hari | Social proof |
| 5.4 | **❌ Pending: AggregateRating schema (real reviews)** | ❌ Pending | 🎯 1 hari | Stars di SERP |
| 5.5 | **❌ Pending: A/B testing title (CTR optimization)** | ❌ Pending | 🎯 ongoing | Traffic +20-50% |
| 5.6 | **❌ Pending: Email capture + drip campaign** | ❌ Pending | 🎯 1 minggu | Lead nurture |
| 5.7 | **❌ Pending: Lead scoring (which keyword → which customer quality)** | ❌ Pending | 💡 ongoing | Quality lead |
| 5.8 | **❌ Pending: Retargeting pixel (FB/Google) untuk non-converter** | ❌ Pending | 🎯 2 hari | Conversion lift |

### PHASE 6 (Bulan 6+): **SCALE & DEFEND**

| # | Item | Status | Effort | Impact |
|---|------|--------|--------|--------|
| 6.1 | **❌ Pending: Programmatic SEO — `/harga-iklan-{platform}/`** | ❌ Pending | 🎯 1 minggu | Ribuan URL baru |
| 6.2 | **❌ Pending: Programmatic SEO — `/cara-pasang-iklan/{platform}/{city}/`** | ❌ Pending | 🎯 1 minggu | Question keyword coverage |
| 6.3 | **❌ Pending: Programmatic SEO — `/beriklan-vs-{competitor}/`** | ❌ Pending | 🎯 1 minggu | Comparison intent |
| 6.4 | **❌ Pending: Multi-bahasa (English version)** | ❌ Pending | 💡 1 bulan | Global market |
| 6.5 | **❌ Pending: Competitor monitoring (track their ranking)** | ❌ Pending | 🎯 ongoing | Defensive SEO |
| 6.6 | **❌ Pending: Auto-refresh content yang "aging"** | 🔄 Partial | 🎯 ongoing | Freshness signal |
| 6.7 | **❌ Pending: News/jurnalistik content (case study launches)** | ❌ Pending | 🎯 ongoing | Backlink magnet |
| 6.8 | **❌ Pending: Infographics untuk shareability** | ❌ Pending | 🎯 ongoing | Social signals |

---

## 🎯 KEYWORD STRATEGY — DEEP DIVE

### Sumber Keyword (5 layers)

| Layer | Status | Volume | Quality | Freshness |
|-------|--------|--------|---------|-----------|
| **Google Suggest** (seed × city × modifier) | ✅ Done | 1613 | ⭐⭐⭐⭐ | Bulanan |
| **Keyword Miner** (broad scraping) | ✅ Done | 1150 | ⭐⭐⭐ | Bulanan |
| **Google Trends daily** | 🔄 Partial | ~60/hari | ⭐⭐⭐⭐⭐ | Harian |
| **People Also Ask (PAA)** | ❌ Pending | ~500/layanan | ⭐⭐⭐⭐⭐ | Bulanan |
| **Competitor SERP mining** | ❌ Pending | ~300/layanan | ⭐⭐⭐⭐ | Bulanan |

### Intent Matrix (untuk expansion 2763 → 7000+)

```
INTENT MODIFIERS:
┌─────────────────┬──────────────────────────────────────────┐
│ COMMERCIAL      │ harga, biaya, tarif, murah, paket, promo │
│ QUALITY         │ terbaik, profesional, berpengalaman,    │
│                 │ terpercaya, no 1, top                    │
│ ACTION          │ cara, tips, tutorial, langkah, strategi  │
│ QUESTION        │ apa itu, bagaimana, kenapa, berapa       │
│ COMPARISON      │ vs, atau, bedanya, perbandingan          │
│ YEAR            │ 2026, 2027, update terbaru               │
│ PAIN POINT      │ gagal, tidak berhasil, kenapa turun      │
└─────────────────┴──────────────────────────────────────────┘

Per service × 26 kota × 6 modifier × ~3 long-tail = ~5000 keywords baru
+ 1500 trending/seasonal = TARGET 7000+
```

### Long-tail yang di-miss saat ini

- ❌ "cara optimasi ROAS Meta Ads untuk UMKM"
- ❌ "berapa biaya iklan TikTok per hari 2026"
- ❌ "jasa iklan Facebook terbaik untuk toko online"
- ❌ "apa bedanya Meta Advantage+ vs manual campaign"
- ❌ "tips landing page conversion rate tinggi"

---

## 📊 INDEXING STRATEGY — DEEP DIVE

### Pipeline Saat Ini

```
New post → push posts.json → GitHub → CF build → live
                                              ↓
                                    POST /api/index-url (gen_from_queue auto)
                                              ↓
                                    D1 pending_indexing
                                              ↓
                                    Daily cron /api/cron/indexing
                                              ↓
                                    IndexNow submit (18/hari)
```

### Gap: Crawl Discovery Lambat

**Problem:** Artikel baru hanya di-discover Google via sitemap refresh (daily). Butuh **backlink internal real-time** agar Googlebot langsung menemukan.

**Fix: Auto-link artikel baru ke 3-5 related posts**

```python
# Pseudo-code di gen_from_queue.py (atau new endpoint)
def auto_link_new_post(new_post):
    # Cari 5 post related by:
    # - Same service
    # - Same city (if any)
    # - Same category
    # Append link di content: <p>Baca juga: [judul 1], [judul 2], ...</p>
```

**Impact:** Googlebot menemukan artikel baru dalam jam, bukan hari.

### Gap: GSC Indexing API Belum Dipakai

**Indexing API** (bukan IndexNow) — Google-specific endpoint untuk request instant crawl:
- Endpoint: `https://indexing.googleapis.com/v3/urlNotifications:publish`
- Quota: 200 req/day (free)
- Setup: GSC service account JSON

**Fix: Tambah handler `/api/cron/gsc-indexing`**

```js
// Untuk setiap pending_indexing row, panggil GSC Indexing API
// URL_PUBLISHED notification → Google crawl dalam minutes
```

### Pipeline Target (post-fix)

```
New post → push → CF live
                 ↓
       POST /api/cron/gsc-indexing (instant GSC API request)
                 +
       POST /api/index-url (instant IndexNow)
                 +
       auto-link ke 5 related posts (internal discovery)
                 ↓
       Google crawl dalam 5-15 menit
```

---

## 🚀 "5 ARTIKEL/JAM" WORKFLOW (CONCRETE)

### Endpoint Design

```http
GET /api/cron/hourly-generate?token=beriklan-admin-2026&count=5
```

### Implementation

```javascript
// src/worker-entry.js
async function handleHourlyGenerate(request, env) {
    // 1. Token check
    // 2. Load keyword-queue.json from ASSETS
    // 3. Pick top `count` pending keywords by priority_score
    // 4. For each, call Zen → fallback Groq → fallback static
    // 5. Build posts.json payload (full updated array)
    // 6. PUT to GitHub API: /src/data/posts.json
    // 7. PUT to GitHub API: /public/data/posts-index.json
    // 8. POST /api/index-url with new URLs
    // 9. Return JSON: { generated, slugs, models, errors }
}
```

### Zen API call (dari existing pattern)

```js
const payload = {
    model: "deepseek-v4-flash-free",
    messages: [{ role: "user", content: prompt }],
    max_tokens: 4000,
    thinking: { type: "disabled" }
};
```

### Trigger

```
cron-job.org:
  - Trigger: every hour
  - URL: https://beriklan.co.id/api/cron/hourly-generate?token=...&count=5
  - Timeout: 240s (untuk 5 artikel × ~30-60s)
```

### Cost Analysis

| | Free tier limit | Our usage |
|--|--|--|
| Zen deepseek-v4-flash-free | unlimited (free) | 120/hari = 3600/bulan |
| Groq llama-3.3-70b | 30 req/min | fallback only |
| GitHub API | 5000 req/hr | 6/hr (commit + index + sitemap) |
| CF Worker CPU | 50ms/request + 30s max | ~2-5 min total |
| IndexNow | 10K URL/batch | ~120/hari |

**All within free tiers.** No operational cost.

---

## 💰 REVENUE PROJECTION

### Current state (Jul 2026)
- 2027 posts × ~5 pageviews/bulan average = ~10K pageviews
- AdSense RPM digital marketing niche: $2-5/1000
- Est. AdSense: $20-50/bulan

### Target 3 bulan (Okt 2026)
- 5000+ posts (with hourly generation)
- ~50K pageviews/bulan
- Est. AdSense: $100-250/bulan

### Target 6 bulan (Jan 2027)
- 12000+ posts + backlink strategy + PAA coverage
- ~200K pageviews/bulan
- Est. AdSense: $400-1000/bulan
- Plus WA leads: ~50-200 qualified leads/bulan (customer matching)

### Customer matching quality

| Source | Expected quality | Volume |
|--------|------------------|--------|
| Blog SEO organic | ⭐⭐⭐⭐⭐ high intent | 30-100/bulan (target) |
| Direct WA (returning) | ⭐⭐⭐⭐⭐ | 10-30/bulan |
| Google Ads (jika diaktifkan) | ⭐⭐⭐⭐ | varies |
| Social media (post YouTube/TikTok) | ⭐⭐⭐ | varies |

**Big leverage:** SEO traffic converts 5-10× better than social/ads untuk high-ticket services.

---

## 📊 DASHBOARD ENHANCEMENT — `/api/admin/keywords`

**Current sections (existing):**
- ✅ Ringkasan pipeline + cards (total/gen/pending/live)
- ✅ Per layanan / kota / source breakdown
- ✅ Recent generated
- ✅ Indexing activity (live D1)

**New sections to add (pending):**

| Section | Data source | Why |
|---------|-------------|-----|
| **Hourly generation status** | D1 `generation_logs` | Track 5/hari target |
| **GSC performance (28d)** | D1 `gsc_stats` (via gsc-pull) | Real ranking data |
| **Backlink status** | New `backlinks.json` | Off-page SEO progress |
| **Trending topics today** | D1 `trending_topics` | What's hot now |
| **Article freshness distribution** | posts.json stats | How many stale |
| **Internal link density per post** | New compute | SEO health |
| **Roadmap progress checklist** | Static config | Visual progress |
| **Coverage gaps** | keyword-queue × posts.json | Missing content |
| **Recent indexing status (live)** | D1 `pending_indexing` | Already there ✓ |
| **GSC Indexing API quota usage** | Worker var | 200/day limit |

---

## 🎯 SUCCESS METRICS (KPIs)

### 30-day targets

| Metric | Current | Target | Why |
|--------|---------|--------|-----|
| Posts published | 2.027 | 5.000 | Volume = coverage |
| Keyword coverage | 60 generated | 1.500 | 25× more topics |
| Indexing latency | 24-48h (cron) | 5-15 min | GSC Indexing API |
| Organic traffic | ~10K/mo | 50K/mo | Topical authority |
| Indexed pages | ~1.800 | 4.500 | Better crawl |
| Backlinks | 0 | 50+ | DR boost |

### 90-day targets

| Metric | Target |
|--------|--------|
| Domain Rating (Ahrefs) | 30+ (dari ~5) |
| Top 3 SERP untuk "jasa iklan [platform]" | 8/11 platform |
| AdSense monthly | $400-1000 |
| WA leads/month | 50-200 |
| Customer conversion rate | 10-20% dari leads |

### 180-day targets

| Metric | Target |
|--------|--------|
| Posts | 15.000+ |
| Keywords ranked | 5.000+ |
| Monthly organic traffic | 200K-500K |
| AdSense monthly | $1000-3000 |
| WA leads/month | 200-500 |
| #1 SERP untuk brand queries | All |

---

## 🔥 HONEST GAPS — WHAT I'M NOT COVERING WELL

1. **Local SEO / Google Maps ranking** — critical untuk UMKM Indonesia yang cari "jasa iklan [kota]"
2. **YouTube SEO** — video rank di Google SERP, double exposure
3. **Brand entity building** — Google lebih rank brand yang punya presence multi-platform
4. **E-E-A-T** — Experience, Expertise, Authority, Trust signals (Author bio, About, certifications)
5. **Backlink quality vs quantity** — 1 backlink DR>80 lebih baik dari 1000 backlink spam
6. **Content decay monitoring** — artikel lama yang rank-nya turun perlu refresh
7. **Mobile-first indexing** — Google pakai mobile version untuk ranking, perlu extra attention
8. **Crawl budget optimization** — untuk domain besar (10K+ pages), penting

---

## 📋 NEXT IMPLEMENTATION ORDER (RECOMMENDED)

### This week
1. `/api/cron/hourly-generate` endpoint (2 jam) — **volume foundation**
2. Expand keyword-queue 2763 → 7000+ (1 jam) — **coverage**
3. Auto-link new posts to 5 related (1 jam) — **crawl speed**
4. GSC Indexing API handler (1 jam) — **instant indexing**

### Next week
5. PAA content extraction + inject ke artikel existing (2 hari)
6. Page speed audit + optimization (1 hari)
7. GBP setup + verification (1 hari)

### Month 1
8. Backlink strategy execution (50 directory + 5 guest posts)
9. YouTube channel + first 10 videos
10. Pillar pages per service (5 halaman × 3000 kata)

### Month 2-3
11. Programmatic SEO pages (ribuan URL baru)
12. Original research / data survey
13. Calculator tools

---

## 📚 REFERENCES

- `web/scripts/gen_keyword_stats.py` — keyword stats generator (build-time)
- `web/scripts/gen_from_queue.py` — article generator (Zen + Groq fallback)
- `web/scripts/retrofit_internal_links.py` — internal link retrofit
- `web/scripts/freshness_engine.py` — content freshness layer
- `web/scripts/clamp_future_dates.py` — date clamp safety net
- `web/src/worker-entry.js` — Worker routes + endpoints
- `web/src/components/BlogFilter.svelte` — blog index (client:only)
- `web/src/pages/blog/[slug].astro` — single post template
- `/api/admin/keywords?token=beriklan-admin-2026` — pipeline dashboard
- `/api/admin/keywords/roadmap` — roadmap progress (TBD)

---

## ✍️ VERSION HISTORY

- **v3.0 (2026-07-20):** Audit ulang dengan 7 gap baru (GBP, YouTube, E-E-A-T, programmatic, research, multimedia, brand)
- **v2.0 (2026-07-19):** Tier 1 selesai (volume foundation + dashboard)
- **v1.0 (2026-07-15):** Initial strategy document

---

> **Disclaimer:** Ini bukan silver bullet. SEO butuh waktu (3-6 bulan untuk results meaningful). Yang penting: eksekusi konsisten + ukur progress + iterate berdasarkan data. Jangan skip tahap backlink & local SEO — itu yang bikin ranking bertahan lama.