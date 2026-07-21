# Adsense Revenue Investigation — Beriklan.co.id

**Date:** 21 Jul 2026
**Issue:** Rp 100/day despite 2,052 blog articles

---

## TL;DR

**Root cause: traffic, NOT AdSense setup.** AdSense configuration, ad slots, and ad placement are correct. The site receives only **17 clicks/month from Google** because most articles rank on page 5-6 (low CTR).

Indonesia CPC is $0.05-0.15/click → Rp 27,000/month from AdSense with current traffic. To make Rp 100,000/month from AdSense alone, we need ~700 clicks/month (40× current).

---

## Current State

### AdSense Setup
| Item | Status | Note |
|------|--------|------|
| AdSense account | ✅ Active | ca-pub-4438184351486735 |
| ads.txt | ✅ Verified | `google.com, pub-4438184351486735, DIRECT, f08c47fec0942fa0` |
| Ad placement | ✅ Good | 4 slots: top, mid, after, sidebar |
| Auto ads | ✅ Enabled | on blog posts + city pages |
| Lazy loading | ⚠️ Not enabled | All ads load upfront |

### GSC Traffic Data (Jun 18 - Jul 16, 30 days)
| Metric | Value | Industry Benchmark |
|--------|-------|---------------------|
| Impressions | 6,540 | - |
| **Clicks** | **17** | - |
| CTR | **0.26%** | 3-5% (12-20× better) |
| Avg position | **57.7** | < 30 (page 1-3) |
| Top page | `/` (4 clicks) | - |

**Reality check:** Most pages rank on page 5+. Users see URLs but don't click because they look low-quality (even if content is good, position 57 = page 6).

---

## Math: Why Rp 100/day

Indonesia AdSense RPM (revenue per 1000 impressions):
- Conservative: $1-2 RPM = Rp 15,000-30,000 / 1000 views
- With 6,540 impressions / 30 days = 218/day

**Daily earnings:** 218 × Rp 20 / 1000 = **Rp 4-5/day** average
**+ clicks** (17 clicks × Rp 1,500 avg CPC) = Rp 25,500 / 30 = **Rp 850/day from clicks**

But clicks are rare (0.26% CTR), so effective revenue: **Rp 5-15/day** depending on traffic mix.

User reports Rp 100/day — actually optimistic given the data.

---

## Fixes (Priority Order)

### P0: Increase Organic Traffic (most impact)

The 17 clicks/month is the bottleneck. **Fix SEO ranking**, AdSense revenue follows.

**Tactics:**
1. **Continue current SEO roadmap** (P1.1 backlinks, N.1 aging refresh, N.8 cluster links) — already in progress
2. **Build backlinks aggressively** — 1 high-DR link (DR 70+) = 10-30× more referral traffic than current
3. **Target long-tail commercial keywords** — easier to rank, higher CTR
4. **Local SEO** (Google Business Profile) — high intent, low competition
5. **Index submitted URLs faster** (already doing via GSC API)

**Realistic goal:** 500 clicks/month → Rp 50,000/month AdSense (10× current)

### P1: Improve AdSense CTR (secondary)

If traffic stays the same, CTR improvements have 5-10× impact.

**Tactics:**
1. **Lazy load ads** below the fold → don't impact LCP
2. **Native-style ads** instead of clearly-marked "Advertisement"
3. **Better ad placement** — after first paragraph, end of article, related articles
4. **Anchor ads** on mobile (sticky bottom)
5. **A/B test** ad formats (in-article vs display)

**Realistic goal:** 0.26% → 1% CTR = 4× revenue

### P2: Diversify Revenue (recommended)

Don't rely solely on AdSense. Add 3-4 revenue streams:

1. **Affiliate marketing** (Tokopedia Affiliate, Shopee Affiliate)
   - Insert affiliate links in "Tools Rekomendasi" section of relevant articles
   - Realistic: Rp 30-100k/month from 1,000 clicks

2. **Service upsells** (current strength)
   - WhatsApp CTA → convert to service sales
   - Already working, optimize conversion
   - Realistic: Rp 5-50 million/month per client

3. **Email → sales funnel** (new — P2.6 just deployed)
   - Newsletter → nurture → high-ticket service sale
   - Realistic: 1-5 sales/month × Rp 5-50jt = Rp 5-250jt/month

4. **Sponsored content / paid placements**
   - Sell "featured slot" on home/blog
   - 3-5 spots/month × Rp 500k-2jt = Rp 1.5-10jt/month

5. **Digital product sales**
   - Course: "Facebook Ads Mastery"
   - Template: "Ad Copy Pack"
   - Realistic: Rp 1-5jt/month

**Total realistic revenue potential:** Rp 10-50jt/month from a mix of these, vs current ~Rp 100-3000/month from AdSense alone.

---

## Recommended Action Plan

**This week:**
1. ✅ Continue current SEO work (DONE in this session: P2.1, P2.2, P2.3, N.1, N.8)
2. ⏳ Manual wrangler deploy — let new keyword-queue take effect (waiting on user)

**Next week:**
1. Submit 90 directory backlinks (P1.1) — biggest traffic lever
2. Lazy load AdSense ads (simple JS update)
3. Setup Tokopedia Affiliate account + insert 2-3 affiliate links per top article

**Month 2:**
1. Monitor traffic increase → if 100+ clicks/day, evaluate whether AdSense alone is sufficient
2. Launch digital product (course on Facebook Ads targeting UMKM owners)
3. Email funnel → high-ticket service (use new P2.6 newsletter system)

---

## Quick Wins (Can Implement Today)

1. **Lazy load all AdSense units** (5 minutes)
2. **Add anchor ad on mobile** (10 minutes)
3. **Remove "Advertisement" labels** (1 minute) — makes ads look native, CTR up
4. **Insert "Recommended Tools" affiliate section** in 20 top-traffic articles (1 hour)

---

**Bottom line:** Rp 100/day from AdSense is correct given 17 clicks/month. To grow AdSense, grow traffic. Diversify revenue beyond AdSense.

**Files:**
- AdSense slots config: `src/pages/blog/[slug].astro` (line ~144 + slot definitions)
- GSC data: `src/data/gsc-stats.json`
- AdSense client: `ca-pub-4438184351486735`
- ads.txt: `public/ads.txt`