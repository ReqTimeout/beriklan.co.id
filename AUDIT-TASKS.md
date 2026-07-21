# Audit & Tasks Tracker — Beriklan.co.id

> Single source of truth untuk semua task improvement yang sedang berjalan.
> Created: 21 Jul 2026

## Quick Status

| # | Task | Status | Priority | ETA |
|---|------|--------|----------|-----|
| 1 | **BUG FIX**: Script rendering after `</html>` on city/blog pages | ✅ DONE | HIGH | - |
| 2 | Audit `/api/admin/keywords` dashboard | 📋 See findings | MEDIUM | - |
| 3 | Audit meta title + description di semua service pages | 📋 TODO | HIGH | 1 hari |
| 4 | Tambah view-live ke Footer Layanan + programmatic SEO | 📋 TODO | HIGH | 2 jam |
| 5 | Riset keyword view-live + generate artikel | 📋 TODO | HIGH | 1 hari |
| 6 | Internal + external links di harga-iklan pages | 📋 TODO | MEDIUM | 2 jam |
| 7 | N.1 Auto-refresh aging content | 📋 TODO | MEDIUM | 1 hari |
| 8 | N.8 Cluster auto-link to pillar | 📋 TODO | MEDIUM | 2 jam |
| 9 | Adsense revenue investigation | 📋 TODO | LOW | - |
| 10 | Email promo strategy | 📋 TODO | LOW | - |

---

## 1. BUG FIX: Script after `</html>`

**Issue:**
- Di city pages (`/jasa-iklan-facebook/bandung/`) dan blog pages, ada `<script type="module">` yang render SETELAH `</html>`
- Browser memparse ini sebagai content di luar HTML tree → bisa muncul sebagai text atau error
- Cause: di `Layout.astro`, script reveal observer ditulis setelah `</html>` (line 662+) + ada `<style is:global>` setelahnya

**Fix Applied:**
- Script reveal observer dipindah ke dalam `<body>` sebelum `</body>` (line 417)
- `<style is:global>` masih di luar tapi Astro handle hoisting dengan benar (cek dist)

**Verify:**
```bash
curl -s https://beriklan.co.id/blog/ | grep -o "</html>[^<]*<"
# Output: hanya match text "moved here", bukan actual HTML
```

---

## 2. /api/admin/keywords Dashboard Audit

**Findings:** Dashboard SUDAH jalan dan comprehensive. Stats saat ini (live):
- Total keyword: 27.947
- Artikel jadi: 76 (coverage 0.3%)
- Pending generate: 27.871
- Live di posts.json: 114 / 2.048
- Indexing queue: 220 (submitted 353, hari ini 0)
- Hourly auto-generate: 14 total (12 committed, 2 drafts)
- Trending: 2 hari ini

**Sections present:**
- Total keyword, artikel jadi, pending generate, live count, indexing queue
- Per Layanan breakdown
- Per Kota breakdown (Jakarta, Bandung, Surabaya, dll)
- Sumber keyword (expansion_v1, suggest+combo, miner)
- Indexing activity (25 terakhir)
- Artikel terbaru dari queue (40)
- Hourly auto-generate activity
- Trending articles

**Gap yang user rasakan:**
- "progress hariannya ga keliatan" → perlu section "Today's Progress" (date comparison)
- "keyword barunya apa" → belum ada section recent added keywords
- "yang sudah dan belum" → coverage sudah ada, tapi perlu "completion forecast" (berdasarkan rate generate, kapan 100%)

**Improvement Plan:**
1. Tambah section "📅 Today's Progress" dengan comparison vs yesterday
2. Tambah section "🆕 Recent Keywords Added" (last 50)
3. Tambah section "🎯 Completion Forecast" (days to 100% at current rate)
4. Tambah health check indicator untuk cron jobs (last run timestamps)
5. Periksa apakah trending cron jalan (cron `30 */6 * * *`)

---

## 3. Meta Title + Description Audit

**Pattern requirement:**
- Primary keyword di 8 kata pertama
- Marketing pro Bahasa Indonesia
- FOMO + meyakinkan
- 150-160 char untuk title, 150-160 untuk description

**Pages to audit:**
- 10 service pages (`jasa-iklan-facebook`, `jasa-iklan-instagram`, `jasa-iklan-tiktok`, `jasa-iklan-google`, `jasa-iklan-youtube`, `jasa-kelola-instagram`, `jasa-kelola-tiktok`, `jasa-pembuatan-website`, `jasa-pembuatan-landing-page`, `jasa-digital-marketing`)
- 250 city pages (10 services × 25 cities)
- 827 blog posts (auto-generated)
- 3 calculator pages
- 1 research page
- Pillar pages (10)

**Action:** Re-write each `<title>` dan `<meta description>` di:
- `src/pages/jasa-*.astro` (root pages)
- `src/pages/jasa-*/[city].astro` (city pages)
- Tinggalkan blog posts (auto-generated, generic enough)

**Snippet optimization:**
- Tambah `keywords` meta tag (kalau belum ada di semua pages)
- Verify OG title + description match page title

---

## 4. View-Live Missing dari Footer Layanan + Programmatic SEO

**Issue:**
- View-Live punya 4.112 keywords (terbesar ke-2 setelah Website)
- Hanya 9 artikel + 2 service roots (footer link?)
- Footer Layanan hanya punya 6 paid-ads + 1 landing page = 7 links
- View-Live TIDAK ADA di Footer Layanan
- Programmatic SEO view-live hanya ada di `/jasa-view-live/{platform}/{city}/` (130 pages) — BELUM DITAMBAHKAN ke Footer Harga/Tools

**Plan:**
1. Tambah view-live links ke Footer Layanan (TikTok Live, Shopee Live, YouTube Live, Instagram Live, Twitch Live)
2. Tambah programmatic SEO entry point:
   - Buat `/harga-view-live/` atau
   - Link dari Footer "Harga" ke `/jasa-view-live/bandung/` dll
3. SEO prioritize view-live (low competition opportunity)

---

## 5. View-Live Keyword Research + Artikel Generation

**Current state:**
- 4.112 keywords in queue
- 9 articles generated
- 4.103 pending
- Coverage: 0.2% (lowest among services with content)

**Why view-live is priority:**
- Low competition in Google ID (most agencies don't target this)
- High commercial intent (businesses want viewers fast)
- Trending topic (live streaming booming post-TikTok Shop)
- Already has 2 service root pages (`/jasa-view-live/`, `/jasa-view-live/{platform}/`)

**Plan:**
1. Audit existing view-live keywords (`expansion_v1`, `miner`)
2. Mine new keywords via:
   - Google Suggest: "jasa viewers", "jasa penonton live", "live tiktok", etc.
   - Competitor scraping: top-ranking view-live sites
   - Platform-specific: TikTok Live, Shopee Live, YouTube Live, IG Live, Twitch
3. Re-prioritize queue: prioritize view-live keywords
4. Generate 50 view-live articles (jeda cron job untuk sementara atau boost priority)

---

## 6. Internal + External Links di Harga-Iklan Pages

**Current state:**
- 120 harga pages built (`/harga-iklan-{platform}/{city}/`)
- Content minimal (only pricing tiers from services.json + city text + FAQ + CTA)
- Tidak ada internal link ke service root atau blog posts
- Tidak ada external reference (data sources)

**Plan:**
1. Add section "Artikel Terkait" dengan 3-5 blog posts dari same platform + city
2. Add section "Pelajari Lebih" dengan link ke pillar page
3. Add "Data dari" section di footer halaman dengan link ke source (e.g., "Mordor Intelligence 2026")
4. Add related-services sidebar (kelola instagram jika harga instagram)

**Indexing:**
- 120 harga pages = batch submit to GSC Indexing API
- Run `/api/cron/gsc-indexing?count=120` after deploy
- Verify semua 120 ada di sitemap-city.xml

---

## 7. N.1 Auto-Refresh Aging Content

**Problem:**
- Artikel lama (2024-2025) punya ranking bagus tapi tidak di-update
- Google freshness signal akan turun → ranking turun

**Plan:**
1. Identify articles older than 6 months with declining impressions (via GSC data)
2. Auto-refresh top 100 articles:
   - Re-write intro + conclusion
   - Update stats + dates
   - Add new section if relevant
3. Schedule: cron monthly (1st of month) → run batch refresh
4. Track in `updated_at` field di posts.json

---

## 8. N.8 Cluster Articles Auto-Link to Pillar

**Problem:**
- 827 blog posts di 11 clusters (meta, tiktok, google, youtube, case-study, strategy, etc.)
- Pillar pages (`/jasa-*/pilar/`) seharusnya link ke top articles di cluster
- Tapi cluster auto-link belum implemented

**Plan:**
1. Build `cluster_linker.py`:
   - Load all posts
   - Group by service/category
   - Find pillar pages
   - For each pillar, find top 10 posts by GSC clicks
   - Inject "Artikel Terkait" section ke pillar
2. Also inject reverse links: dari blog post, link ke pillar
3. Run monthly to update

---

## 9. Adsense Revenue Investigation

**Current state:** Rp 100/day despite many articles
**Likely causes:**
- RPM rendah (Indonesian traffic ~$0.50-1 RPM vs US $5-10)
- Ad placement suboptimal
- Low CTR (ads di bad positions)
- Traffic quality (mostly bot/Indonesia low CPM)
- AdSense account baru (no optimization history)

**Plan:**
1. Check AdSense dashboard for actual RPM/CTR/impressions
2. Audit ad placements:
   - Above-the-fold ad?
   - In-content ad (mid-article)?
   - Sidebar ad?
3. Implement lazy loading untuk ads
4. Try auto ads vs manual units
5. Consider affiliate marketing (more profitable in ID)

---

## 10. Email Promo Strategy

**Current assets:**
- Newsletter D1 table (just deployed)
- Customer emails (existing in D1 via /api/order or contact form?)

**Idea 1: Newsletter Promo (Low cost)**
- Send 1 promo email/bulan via Brevo/MailerLite (free tier)
- Segment by interest (pilih platform saat sign up)
- Design pakai Mailchimp/MailerLite template builder (no coding)

**Idea 2: WhatsApp Broadcast (Most effective in ID)**
- Collect WA dari order form
- Use WA Business API untuk broadcast (official)
- Or manual broadcast via WA Web (low effort)

**Idea 3: Push ke existing services (Free)**
- Bikin promo banner di homepage (limited time)
- Add promo CTA di exit-intent popup
- Use existing newsletter untuk announce promo

**Recommendation:**
- Combine: Email (capture intent) + WA (high engagement in ID)
- Frequency: 1× / bulan per channel
- Content: 1 educational + 1 promo (60/40)

---

## Implementation Order (recommended)

1. **TODAY** (bug fix + quick wins):
   - ✅ Bug fix (Layout.astro script placement)
   - Improve /api/admin/keywords dashboard (add 3 sections)
   - Add view-live links to Footer

2. **WEEK 1**:
   - Meta title + description audit (rewrite 10 service pages)
   - Internal links di harga-iklan pages (build script)
   - Index 120 harga pages to GSC

3. **WEEK 2**:
   - View-live keyword research + 50 article generation
   - Cluster auto-link script (N.8)
   - Auto-refresh aging content system (N.1)

4. **ONGOING**:
   - Adsense optimization
   - Email promo strategy execution

---

**Maintained by:** Beriklan Digital Agency + AI coding agent
**Last update:** 21 Jul 2026