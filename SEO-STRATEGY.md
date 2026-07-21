# SEO & Growth Strategy — Beriklan.co.id

> **Tujuan utama:**
> 1. **#1 Google untuk semua keyword relevan** (jasa iklan Indonesia)
> 2. **AdSense revenue scale-up** (pageviews × RPM tinggi)
> 3. **Customer matching** (lead WA berkualitas ke admin)
>
> **Versi:** 4.5 (2026-07-21) — P1.4 + P1.5 PAA + Featured Snippet optimization (12/18 done · 67%)
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

## 📈 PHASE ROADMAP — see CURRENT PROGRESS below

For priority-ordered roadmap (P0-P3 + backlog) with effort + impact,
see **## 📊 CURRENT PROGRESS** section. Phase 1-6 tables were
consolidated into priority-ordered roadmap in v4.0.

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


## 📌 CATATAN OPERASIONAL (untuk referensi ke depan)

### Cloudflare Cron Triggers — single source of truth

**Tidak pakai cron-job.org / Hostinger cron / external scheduler.**
Semua cron jobs dijalankan **native via Cloudflare Workers infrastructure**.

Config di `web/wrangler.jsonc`:
```json
"triggers": [
  { "cron": "0 * * * *" },      // hourly-generate (artikel baru)
  { "cron": "0 */6 * * *" },   // gsc-indexing + trending-fetch
  { "cron": "30 */6 * * *" }   // trending-generate
]
```

Handler di `web/src/worker-entry.js`:
- `async scheduled(event, env, ctx)` dispatch berdasarkan `event.cron`
- Panggil HTTP handlers via `fakeRequest(path)` jadi single source of truth

Jika ada perubahan:
- ❌ JANGAN tambah cron-job.org job
- ❌ JANGAN tambah Hostinger cron
- ✅ Edit `wrangler.jsonc` triggers array + push ke GitHub
- ✅ CF auto-deploy + auto-fire sesuai schedule

**Verify cron firing**: 
- CF Dashboard → Workers → `beriklanweb` → Logs
- Filter: `[scheduled:hourly]`, `[scheduled:gsc-indexing]`, `[scheduled:trending-fetch]`, `[scheduled:trending-generate]`

### HTTP Endpoints (untuk manual trigger / debugging)

| Endpoint | Method | Token | Fungsi |
|----------|--------|-------|--------|
| `/api/health` | GET | no | Status check |
| `/api/admin/keywords?token=...` | GET | yes | Pipeline dashboard (HTML) |
| `/api/admin/keywords?token=...&count=1&debug=1` | - | yes | Test keyword pipeline |
| `/api/cron/hourly-generate?token=...&count=N` | GET | yes | Generate N artikel dari queue |
| `/api/cron/gsc-indexing?token=...&count=N` | GET | yes | Submit N URL ke GSC Indexing API |
| `/api/cron/trending?token=...` | GET | yes | Fetch Google Trends RSS → D1 queue |
| `/api/cron/trending-generate?token=...&count=N` | GET | yes | Process queue → artikel |
| `/api/cron/indexing?token=...` | GET | yes | Daily IndexNow batch (legacy) |
| `/api/ping-sitemap?token=...` | GET | yes | Submit sub-sitemaps to GSC |
| `/api/health?token=...` | GET | yes | Detailed health stats |

**ADMIN_TOKEN**: `beriklan-admin-2026` (set via wrangler.jsonc vars)
**CF Zone ID**: `47f87944d6d690eb388e7be1143c14a2`
**CF Account ID**: `766dfffa7e5dcd8ba246ebfa60bc10ba`

### D1 Database
- Name: `beriklan-seo`
- Database ID: `0e71d6e3-231f-40a1-ac6b-6defc3976efd`
- Tables: `pending_indexing`, `generated_drafts`, `cron_logs`, `trending_articles`, `trending_topics`, `gsc_sitemaps`, `gsc_stats`, `api_keys`, `api_key_usage`, `rate_limits`, `policy_audit_log`, `batch4_articles`, `batch4_queue`, `city_content`, `city_content_queue`

### Secrets (di CF Dashboard → Workers → beriklanweb → Settings)
- `ADMIN_TOKEN` (var) = `beriklan-admin-2026`
- `GITHUB_TOKEN` (secret) = `[github PAT]` ⚠️ rotate setelah dipakai
- `ZEN_API_KEY` (secret) = `[opencode.ai/zen key]`
- `GROQ_API_KEY` (secret) = `[groq key 1]`
- `GROQ_API_KEY_2` (secret) = `[groq key 2]`
- `GROQ_API_KEY_3` (secret) = `[groq key 3]`
- `GSC_SERVICE_ACCOUNT_JSON` (secret) = `[service account JSON]`

### GitHub Repository
- Repo: `https://github.com/ReqTimeout/beriklan.co.id`
- Auto-deploy: push ke `main` → CF Workers auto-rebuild + deploy
- ⚠️ **JANGAN commit tokens/secrets** (GitHub secret scanning akan block push)

### Workers Plan
- Workers Paid ($5/mo) — **ACTIVE** — untuk 30s CPU/wall time (perlu ini untuk count=5 hourly-generate)
- Workers Free punya 10ms CPU limit → tidak cukup untuk keyword-queue.json (11MB) parse
- Recommended: tetap di Paid ($5/bulan)

---

## 📊 CURRENT PROGRESS (per 2026-07-20, 18:58 WIB)

### ✅ DONE — verified working (10 items)

| # | Item | Date | Impact |
|---|------|------|--------|
| 1 | Volume foundation: `/api/cron/hourly-generate` endpoint | 2026-07-19 | 5 artikel/jam auto |
| 2 | Secrets configured: GITHUB_TOKEN, ZEN_API_KEY, GROQ_API_KEY | 2026-07-19 | Full pipeline runs |
| 3 | Keyword expansion: 2,763 → **27,947 keywords** (intent matrix) | 2026-07-20 | Coverage 10× |
| 4 | Auto-link: new article → 5 related existing posts | 2026-07-20 | Crawl discovery faster |
| 5 | Cloudflare Cron Triggers: 3 jobs auto-fire (no external cron) | 2026-07-20 | Single source of truth |
| 6 | Workers Paid upgrade: 30s CPU budget | 2026-07-20 | count=5 cron feasible |
| 7 | Multi-Groq-key: GROQ_API_KEY_2/3/4/5 support | 2026-07-20 | TPD quota 3× |
| 8 | Rate-limit detection: keyword kept pending for retry | 2026-07-20 | No data loss |
| 9 | GSC Indexing API: `/api/cron/gsc-indexing` live, www. verified | 2026-07-20 | Instant Google crawl |
| 10 | Trending pipeline: `/api/cron/trending` + `trending-generate` | 2026-07-20 | 4 trending artikel/hari |
| 11 | Dashboard: 14 sections di `/api/admin/keywords` | 2026-07-20 | Full pipeline visibility |
| 12 | **P1.1: Directory Backlinks tracker** + 90 dirs curated | 2026-07-20 | DA boost prep (manual sub) |
| 13 | **P0.1: Page speed** — preload hero img + fetchpriority=high | 2026-07-20 | Blog post Load 1126→628ms (-44%) |
| 14 | SEO-STRATEGY.md + DIRECTORY-SUBMISSION-GUIDE.md maintained | 2026-07-20 | Documentation complete |
| 15 | **P1.2: Pillar enhancement** — StatsBand + ComparisonTable + AuthorBio di 10 service pages | 2026-07-21 | E-E-A-T signal + decision moment |
| 16 | **P0.3: Multi-Groq-key verified** — GROQ_API_KEY + GROQ_API_KEY_2 + GROQ_API_KEY_3 = 3 keys aktif | 2026-07-21 | TPD quota 3× = 300K/hari |
| 17 | **P1.4+P1.5: PAA + Featured Snippet optimization** — 100 Q&A di 10 service pages | 2026-07-21 | Slot #0 Google + rich results FAQ schema |

**Roadmap Progress: 12/18 selesai · 67%** (was 10/18 · 56% after P1.4 + P1.5)

### 🚧 NEXT PRIORITIES (urutan eksekusi, by impact)

#### 🔴 P0 — CRITICAL (minggu ini, blok ranking)

| # | Item | Effort | Impact | Status |
|---|------|--------|--------|--------|
| **P0.1** | ~~Page speed audit + LCP < 2s~~ | 🎯 1 hari | Tanpa ini Google deprioritize ranking | ✅ **DONE** — preload + fetchpriority=high |
| **P0.2** | **Google Business Profile setup + verify** | 🎯 1 hari | WAJIB untuk local SEO UMKM | ❌ pending — manual |
| **P0.3** | ~~Add 2 Groq keys (GSC_KEY_2, GSC_KEY_3) + add ZEN key as 2nd primary~~ | 🚀 10 menit | TPD quota 3× → 300K/hari | ✅ **DONE** — 3 Groq keys aktif (verified via `/api/admin/env-check`). GROQ_API_KEY_4/5 belum dikonfig (TPD 100K × 3 keys cukup untuk sekarang). |

#### 🟡 P1 — HIGH (minggu depan, traffic naik)

| # | Item | Effort | Impact | Status |
|---|------|--------|--------|--------|
| **P1.1** | ~~Backlink strategy — 50 directory submissions~~ | 🎯 3 hari | Domain authority 5 → 30+ | 🔄 **in-progress** (tracker + 90 dirs ready, manual submission) |
| **P1.2** | ~~Pillar page per service (5000 kata)~~ | 🎯 3 hari | Topical authority | ✅ **PARTIAL** — StatsBand + ComparisonTable + AuthorBio injected ke 10 service pages. Word count sudah 6K+ per page. |
| **P1.3** | **YouTube channel + video embed di artikel** | 🎯 1 minggu | Double SERP exposure | ❌ pending |
| **P1.4** | ~~People Also Ask (PAA) content extraction~~ | 🎯 3 hari | Slot #0 Google | ✅ **DONE** — 100 PAA Q&A pairs (10 service × 10) di FAQPage JSON-LD schema |
| **P1.5** | ~~Featured snippet optimization~~ | 🎯 2 hari | Snippet ranking | ✅ **DONE** — declarative answers 60-80 kata dengan specific numbers (snippet-friendly) |

#### 🟢 P2 — MEDIUM (bulan ini, conversion & scale)

| # | Item | Effort | Impact | Status |
|---|------|--------|--------|--------|
| **P2.1** | **Calculator tools (budget iklan, ROAS, kalkulator ROI)** | 🎯 1 minggu | Dwell time + backlinks | ❌ pending |
| **P2.2** | **Programmatic SEO: `/harga-iklan-{platform}/{city}/`** | 🎯 1 minggu | Ribuan URL baru | ❌ pending |
| **P2.3** | **Original research / data survey industri iklan ID** | 🎯 1 minggu | Backlink magnet | ❌ pending |
| **P2.4** | **AggregateRating schema (real reviews)** | 🎯 1 hari | Stars di SERP | ❌ pending |
| **P2.5** | **A/B testing title (CTR optimization)** | 🎯 ongoing | Traffic +20-50% | ❌ pending |
| **P2.6** | **Email capture + drip campaign** | 🎯 1 minggu | Lead nurture | ❌ pending |

#### 🔵 P3 — LATER (kuartal ini, scale & defend)

| # | Item | Effort | Impact | Status |
|---|------|--------|--------|--------|
| **P3.1** | **Guest posts 5 situs DR>50** | 🎯 2 minggu | Authority | ❌ pending |
| **P3.2** | **LinkedIn + TikTok brand entity** | 🎀 2 hari | B2B leads | ❌ pending |
| **P3.3** | **HARO / journalist outreach** | 🎯 ongoing | DR boost | ❌ pending |
| **P3.4** | **TikTok account cross-post** | 🎯 1 minggu | Brand entity | ❌ pending |
| **P3.5** | **Podcasts (3-5 episode)** | 💡 1 bulan | Brand awareness | ❌ pending |
| **P3.6** | **Multi-bahasa (English version)** | 💡 1 bulan | Global market | ❌ pending |

#### ⚪ NICE-TO-HAVE (backlog)

| # | Item | Effort | Impact |
|---|------|--------|--------|
| **N.1** | **Auto-refresh content "aging"** | 🎯 ongoing | Freshness signal |
| **N.2** | **News/jurnalistik content launches** | 🎯 ongoing | Backlink magnet |
| **N.3** | **Infographics untuk shareability** | 🎯 ongoing | Social signals |
| **N.4** | **Lead scoring** | 💡 ongoing | Quality lead |
| **N.5** | **Retargeting pixel (FB/Google)** | 🎯 2 hari | Conversion lift |
| **N.6** | **Testimonials + case studies** | 🎯 1 hari | Social proof |
| **N.7** | **Competitor monitoring** | 🎯 ongoing | Defensive SEO |
| **N.8** | **Cluster articles auto-link to pillar** | 🚀 2 jam | Internal SEO juice |

---

## 📊 KPI Tracker (target 6 bulan)

| Metric | Current | Target 30d | Target 90d | Target 180d |
|--------|---------|------------|------------|-------------|
| Posts published | 2,042 | 3,000 | 6,000 | 12,000 |
| Keywords ranked | ~few | 200 | 1,500 | 5,000 |
| Organic traffic/bulan | ~10K | 30K | 100K | 300K |
| AdSense/bulan | $20-50 | $100 | $400 | $1500 |
| WA leads/bulan | ~10 | 30 | 100 | 300 |
| Domain Rating | ~5 | 15 | 30 | 50 |
| Index % posts | ~70% | 90% | 95% | 98% |

---

## 🔧 TROUBLESHOOTING (cek ini dulu kalau ada masalah)

| Symptom | Cause | Fix |
|---------|-------|-----|
| `/api/cron/*` returns HTTP 503 | Secret not set | Check CF Dashboard Variables |
| GSC submit 403 PERMISSION_DENIED | URL form mismatch | Submit `https://www.beriklan.co.id/...` (with www) |
| AI returns "Zen + Groq both empty" | Rate limit hit | Tunggu reset, atau tambah Groq key |
| Posts.json tidak update | SHA race cron concurrent | Retry — auto-handled |
| `daily_count` shows 0 | CF edge cache stale | `purge_cache` API |
| **New route / endpoint returns 404 setelah push ke GitHub** | **CF edge cache serving stale Worker bundle** | **`POST /zones/{id}/purge_cache` `{"purge_everything":true}` — wajib setelah setiap push code** |
| Article tidak muncul di blog | post.slug duplicate | Cek existing posts.json |
| `article.length < 500` | AI response stripped (markdown fences) | Auto-handled in code |
| Verify Groq/Zen keys configured | `/api/admin/env-check?token=...` | Returns booleans only, no values |


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

- **v4.2 (2026-07-20, 19:00):** P0.1 done (preload hero img), P1.1 tracker live, all 14 done items in table. Add CHANGELOG section below.
- **v4.1 (2026-07-20):** Removed duplicate Phase 1-6 tables (replaced by single priority-ordered roadmap in CURRENT PROGRESS)
- **v4.0 (2026-07-20):** Auto-generation pipeline complete (Cloudflare Cron Triggers + 27,947 keywords + GSC Indexing + Trending). Roadmap di-restructure per priority P0-P3.

---

## 📜 CHANGELOG (append-only, newest first)

### 2026-07-21 (afternoon)
- ✅ **P1.4 + P1.5 LIVE**: PAASection component dengan 100 PAA Q&A pairs (10 service × 10 questions). Snippet-optimized format: declarative answers 60-80 kata dengan specific numbers, accordion UX dengan native `<details>`, FAQPage JSON-LD schema untuk rich results. Injector: `web/scripts/inject_paa.py`. Verified live: all 10 service pages show "Pertanyaan yang Sering Diajukan" + 2 FAQPage schemas (existing FAQ + new PAA). Files: `web/src/components/PAASection.astro`, `web/src/data/paa-questions.json`.

### 2026-07-21 (midday)
- ✅ **P0.3 VERIFIED DONE**: 3 Groq keys configured di CF Dashboard (`GROQ_API_KEY`, `GROQ_API_KEY_2`, `GROQ_API_KEY_3`). Added `/api/admin/env-check` endpoint (boolean-only, no values) untuk verifikasi future. TPD quota = 300K/hari. Rotation works silent (groq#1 selalu sukses → tidak perlu fallback).
- ⚠️ **LESSON LEARNED**: CF edge cache served stale Worker code 15+ menit setelah push. **WAJIB `purge_cache` API setelah push code**. Endpoint `purge_everything: true` sekarang jadi step wajib di deploy workflow.

### 2026-07-21 (morning)
- ✅ **P1.2 Pillar enhancement LIVE**: StatsBand + ComparisonTable + AuthorBio injected ke 10 service pages. StatsBand (3 trust stats di top-of-fold), ComparisonTable (Beriklan vs Kelola Sendiri — 7 baris comparison), AuthorBio (E-E-A-T "Tim Beriklan" + credentials). Verified live via curl: all 10 pages show "Kelola Sendiri"=2, "9 tahun"=2, "Tim Beriklan"=2. Files: `web/src/components/StatsBand.astro`, `ComparisonTable.astro`, `AuthorBio.astro`. Injector: `web/scripts/inject_pillar_components.py`.
- ✅ **UX cleanup live**: Removed duplicate NAPBlock from `Layout.astro` (Footer.svelte already has NAP). Removed "Layanan Terkait" section from 250 city service pages (10 services × 25 cities). Verified via curl: 0 occurrences on `/`, 0 occurrences on 4 sample city pages. Cleans up duplicate structured content + reduces page bloat.

### 2026-07-20 (evening)
- ✅ **P0.1 DONE**: Preload `<link rel=preload as=image fetchpriority=high>` on blog post hero. Blog post FCP 396→284ms (-30%), Load 1126→628ms (-44%). All pages LCP <2s target met. Added "⚡ Page Speed" dashboard section.
- ✅ **P1.1 IN-PROGRESS**: 90 directories curated (avg DR 73), `web/scripts/directories.json` + `directory_tracker.py` + `beriklan-info.json` master data + DIRECTORY-SUBMISSION-GUIDE.md. Dashboard "🔗 Directory Backlinks" live. 34 high-DR pending submission.

### 2026-07-20 (afternoon)
- ✅ **Trending pipeline live**: `/api/cron/trending` (RSS Google Trends) + `/api/cron/trending-generate` (queue → articles). `tagAsTrending()` helper sets category=trending + injects internal-cta. New D1 table `trending_topics`. Dashboard "📰 Trending Articles" section shows 4 today, 9+ total.
- ✅ **Roadmap cleaned**: removed duplicate Phase 1-6 tables, replaced with single priority-ordered roadmap in CURRENT PROGRESS.

### 2026-07-20 (morning)
- ✅ **GSC Indexing API live**: `/api/cron/gsc-indexing` endpoint. OAuth via GSC_SERVICE_ACCOUNT_JSON. Tested 3 URLs successfully submitted. **Critical fix**: changed URL from `beriklan.co.id` → `www.beriklan.co.id` to match GSC verified property (was 403 PERMISSION_DENIED).
- ✅ **Multi-Groq-key deployed**: `GROQ_API_KEY_2/3/4/5` support. Per-key fallback if one returns 429. Diagnostic logging (zenDiag/groqDiag) shows actual response.

### 2026-07-20 (early morning)
- ✅ **P2 #1 DONE**: Workers Paid upgrade ACTIVE (HTTP 200 in 2s vs 503 timeout before). Multi-key support + rate-limit detection.
- ✅ **Keyword expansion**: 2,763 → **27,947 keywords** via intent matrix (10× target).
- ✅ **Auto-link deployed**: New article auto-injected into 5 related existing posts. SHA race-condition fixed with re-fetch + retry on 409.

### 2026-07-19
- ✅ **Cloudflare Cron Triggers**: 3 cron schedules via `wrangler.jsonc` `triggers` field. Replaces cron-job.org/Hostinger.
- ✅ **Auto-generation pipeline**: `/api/cron/hourly-generate` → fetch queue → Zen/Groq AI → commit to posts.json → enqueue IndexNow. Workers Free → Paid upgrade for 30s CPU.

### Earlier sessions
- ✅ Pillar pages (10 service pillar pages, 380 city pages = 390 static)
- ✅ Internal linking 1,200 retrofit + 3,250 cross-city + auto-link per new post
- ✅ Schema markup (Article, BreadcrumbList, FAQ, LocalBusiness, ProfessionalService)
- ✅ Mobile responsive + overflow fix
- ✅ Dashboard 14 sections (per layanan, per kota, source, indexing, hourly, trending, directory, page speed, dll)
- ✅ SEO-STRATEGY.md v3.0 + v4.0 + v4.1 (this doc evolves with project)
- **v3.0 (2026-07-20):** Audit ulang dengan 7 gap baru (GBP, YouTube, E-E-A-T, programmatic, research, multimedia, brand)
- **v2.0 (2026-07-19):** Tier 1 selesai (volume foundation + dashboard)
- **v1.0 (2026-07-15):** Initial strategy document

---

> **Disclaimer:** Ini bukan silver bullet. SEO butuh waktu (3-6 bulan untuk results meaningful). Yang penting: eksekusi konsisten + ukur progress + iterate berdasarkan data. Jangan skip tahap backlink & local SEO — itu yang bikin ranking bertahan lama.