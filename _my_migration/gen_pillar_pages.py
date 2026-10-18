#!/usr/bin/env python3
"""
gen_pillar_pages.py — build 10 pillar guide pages for Beriklan.my.

For each of the 10 MY services it emits `{service}/pilar/index.astro`, a
topical-authority "complete guide" hub that the existing service pages already
link to via `pillarHref="/{service}/pilar/"`.

Differences vs the Indonesian original:
  * English copy, MYR, Malaysia market context.
  * NO blog "top posts" section (beriklan.my has 0 blog posts) — skipped.
  * NO LocalSchema component (beriklan.my doesn't have it) — uses Layout's
    built-in `service` / `faq` / `breadcrumb` schema props instead.
  * Cities come from the real MY cities.json; related services from
    related-services.json; tiers + FAQs from services.json.
  * Only globally-available animation classes (reveal / reveal-stagger) are used.

Also (re)writes web/src/data/pillar-config.json as the source of truth for the
pillar title / intro / clusters / stats.

Idempotent: overwrites pillar-config.json and the 10 generated astro files.
"""
import json
import os

ROOT = os.path.expanduser("~/Desktop/beriklan.my")
DATA = os.path.join(ROOT, "web/src/data")
PAGES = os.path.join(ROOT, "web/src/pages")

# slug -> (display name, priceRange, serviceType, pillarLabel)
META = {
    "facebook-ads-management": ("Facebook Ads", "RM 990 - RM 2,990", "Facebook Ads", "Complete Facebook Ads Guide"),
    "instagram-ads-management": ("Instagram Ads", "RM 990 - RM 2,990", "Instagram Ads", "Complete Instagram Ads Guide"),
    "tiktok-ads-management": ("TikTok Ads", "RM 790 - RM 1,990", "TikTok Ads", "Complete TikTok Ads Guide"),
    "google-ads-management": ("Google Ads", "RM 990 - RM 2,790", "Google Ads", "Complete Google Ads Guide"),
    "youtube-ads-management": ("YouTube Ads", "RM 890 - RM 2,490", "YouTube Ads", "Complete YouTube Ads Guide"),
    "instagram-management": ("Instagram Management", "RM 1,290 - Custom", "Social Media Management", "Complete Instagram Management Guide"),
    "tiktok-management": ("TikTok Management", "RM 990 - RM 2,490", "Social Media Management", "Complete TikTok Management Guide"),
    "website-development": ("Website Development", "RM 1,499 - RM 6,999", "Web Development", "Complete Website Development Guide"),
    "landing-page-design": ("Landing Page Design", "RM 1,299 - Custom", "Landing Page Design", "Complete Landing Page Guide"),
    "digital-marketing-agency": ("Digital Marketing", "Custom", "Digital Marketing", "Complete Digital Marketing Guide"),
}

# English pillar content (Malaysia market context, truthful/defensible figures).
PILLAR = {
    "facebook-ads-management": {
        "title": "The Complete Guide to Facebook Ads for Malaysian Businesses",
        "intro": "Facebook remains one of the most effective paid channels for reaching Malaysian audiences, with well over 20 million users nationwide. Learn targeting strategy, ad formats, budget optimisation and how to measure real ROI.",
        "clusters": [
            {"tag": "Targeting", "title": "Reaching the Right Audience", "desc": "Interests, behaviours, lookalike and custom audiences to find prospects with precision."},
            {"tag": "Creative", "title": "Ad Creative That Performs", "desc": "Image vs video formats, copywriting formulas and the creative patterns that drive the most engagement."},
            {"tag": "Optimisation", "title": "Improving ROAS Over Time", "desc": "A/B testing, scaling, retargeting and how the Meta Pixel supports data-driven decisions."},
            {"tag": "Budget", "title": "Managing Ad Spend Efficiently", "desc": "How much minimum budget you need, when to scale up and how to avoid wasted spend."},
            {"tag": "Conversion", "title": "From Likes to WhatsApp Chats", "desc": "Turning interactions into qualified leads and measurable closings."},
        ],
        "stats": [
            {"num": "22M+", "label": "Facebook users in Malaysia"},
            {"num": "Since 2016", "label": "Managing Meta campaigns"},
            {"num": "Weekly", "label": "Plain-language reporting"},
            {"num": "100%", "label": "Full ad account access"},
        ],
    },
    "instagram-ads-management": {
        "title": "Instagram Ads Strategy for Malaysian Brands",
        "intro": "Instagram is a visual-first platform with strong engagement among younger Malaysians. Learn how to use Reels, Stories, Feed and Shopping ads to build your brand and convert an audience.",
        "clusters": [
            {"tag": "Visual", "title": "Best Visual Ad Formats", "desc": "Reels vs Stories vs Feed — when to use each format for different objectives."},
            {"tag": "Audience", "title": "Young & Premium Audiences", "desc": "Reaching 18–34 year olds with premium interests, lifestyle and visual content consumption."},
            {"tag": "Creative", "title": "Production Value Without a Studio", "desc": "Tips for producing Instagram-grade content with a smartphone, a ring light and templates."},
            {"tag": "Shopping", "title": "Instagram Shopping Integration", "desc": "Tag products in organic posts and ads, plus in-app checkout for e-commerce."},
            {"tag": "Creator", "title": "Creator Collabs & Paid Ads", "desc": "Using user-generated content and creator partnerships for social proof."},
        ],
        "stats": [
            {"num": "15M+", "label": "Instagram users in Malaysia"},
            {"num": "Reels", "label": "Highest organic reach format"},
            {"num": "Weekly", "label": "Plain-language reporting"},
            {"num": "100%", "label": "Full ad account access"},
        ],
    },
    "tiktok-ads-management": {
        "title": "TikTok Ads for Businesses That Want to Go Viral",
        "intro": "TikTok is one of the fastest-growing platforms in Malaysia, reaching tens of millions of adults. The For You feed gives strong organic exposure — learn how to build native content and Spark Ads that perform.",
        "clusters": [
            {"tag": "FYP", "title": "Understanding the For You Algorithm", "desc": "The 3-second hook, the retention curve and the signals the algorithm uses to push content to the FYP."},
            {"tag": "Spark", "title": "Spark Ads vs In-Feed Ads", "desc": "Using organic content as paid ads — the most authentic and cost-efficient format."},
            {"tag": "Creator", "title": "Working With TikTok Creators", "desc": "Finding, briefing and measuring UGC for campaigns — including disclosure compliance."},
            {"tag": "Trend", "title": "Riding Trends & Sounds", "desc": "How to follow trending audio and hashtags without losing your brand identity."},
            {"tag": "Conversion", "title": "TikTok Shop & Lead Ads", "desc": "Turning viewers into customers through in-app checkout or lead generation."},
        ],
        "stats": [
            {"num": "28M+", "label": "TikTok adult reach in Malaysia"},
            {"num": "Spark Ads", "label": "Authentic native format"},
            {"num": "Weekly", "label": "Plain-language reporting"},
            {"num": "100%", "label": "Full ad account access"},
        ],
    },
    "google-ads-management": {
        "title": "Google Ads for Capturing High-Intent Buyers",
        "intro": "Google Ads captures audiences who are actively searching for your product or service — not just scrolling. Learn Search, Display, YouTube and Performance Max to dominate the first page.",
        "clusters": [
            {"tag": "Search", "title": "Search Ads for High Intent", "desc": "Keyword research, match types and copywriting for text ads in search results."},
            {"tag": "Display", "title": "Display Network for Awareness", "desc": "Banner ads across millions of websites — great for retargeting and brand exposure."},
            {"tag": "YouTube", "title": "YouTube Ads for Video Marketing", "desc": "Skippable in-stream, bumper and discovery ads to reach a premium audience."},
            {"tag": "PMax", "title": "Performance Max Optimisation", "desc": "Google's automated campaign that combines all inventory — it needs specific setup."},
            {"tag": "Conversion", "title": "Tracking & Attribution", "desc": "Google Tag, GA4, the conversion API and how to measure accurate ROI across devices."},
        ],
        "stats": [
            {"num": "95%+", "label": "Search market share in Malaysia"},
            {"num": "High Intent", "label": "Reaches active searchers"},
            {"num": "Weekly", "label": "Plain-language reporting"},
            {"num": "100%", "label": "Full ad account access"},
        ],
    },
    "youtube-ads-management": {
        "title": "YouTube Ads for Brand Awareness & Video Marketing",
        "intro": "YouTube is Malaysia's largest video platform, reaching well over 20 million viewers. Learn the ad formats (skippable, bumper, Shorts), targeting and how to make video that holds attention.",
        "clusters": [
            {"tag": "Format", "title": "YouTube Ad Formats", "desc": "Skippable in-stream (5s skip), bumper (6s non-skip), discovery ads and YouTube Shorts."},
            {"tag": "Targeting", "title": "Premium Malaysian Audiences", "desc": "Reaching professionals, gamers and 25–54 year olds with strong purchasing power."},
            {"tag": "Production", "title": "Video Ad Production", "desc": "A hook in 5 seconds, 15–30 second storytelling and a CTA that doesn't feel like a hard sell."},
            {"tag": "Performance", "title": "View-Through & Click-Through", "desc": "Understanding the two key YouTube Ads metrics and how to optimise both."},
            {"tag": "Channel", "title": "YouTube Channel Strategy", "desc": "Building an organic channel alongside paid ads for compounding growth."},
        ],
        "stats": [
            {"num": "24M+", "label": "YouTube users in Malaysia"},
            {"num": "Video", "label": "Awareness at scale"},
            {"num": "Weekly", "label": "Plain-language reporting"},
            {"num": "100%", "label": "Full ad account access"},
        ],
    },
    "instagram-management": {
        "title": "Professional Instagram Management for a Consistent Brand",
        "intro": "Organic Instagram remains one of the most effective brand-building channels. Learn content strategy, hashtags, Reels, community management and how to sustain a healthy engagement rate.",
        "clusters": [
            {"tag": "Content", "title": "Content Calendar & Planning", "desc": "A 30-day content framework, pillar content and when to post for maximum reach."},
            {"tag": "Reels", "title": "Reels for Organic Reach", "desc": "Reels formats that reach far without needing to go viral — the algorithm supports every niche."},
            {"tag": "Hashtag", "title": "Hashtag Strategy 2026", "desc": "Moving from 30 hashtags to 3–5 relevant ones — why it's better for reach."},
            {"tag": "Community", "title": "DM & Comment Management", "desc": "Response templates, follow-up flows and converting DMs into WhatsApp or checkout."},
            {"tag": "Analytics", "title": "Reading Instagram Insights", "desc": "Which metrics matter: reach, saves and shares — not just likes."},
        ],
        "stats": [
            {"num": "12-20", "label": "Optimal posts per month"},
            {"num": "Organic", "label": "Brand building without ad spend"},
            {"num": "Monthly", "label": "Reports with actionable insights"},
            {"num": "Since 2016", "label": "Managing social accounts"},
        ],
    },
    "tiktok-management": {
        "title": "TikTok Management for Consistently Engaging Content",
        "intro": "Organic TikTok delivers the best ROI when done consistently. Learn how to produce a steady stream of videos, ride trending sounds and grow an account naturally.",
        "clusters": [
            {"tag": "Video", "title": "Batch Production Workflow", "desc": "Shoot one day for a month of content — scripts, hooks and editing templates."},
            {"tag": "Hook", "title": "The Decisive First 3 Seconds", "desc": "Hook patterns that stop the swipe — the 'POV', 'stop scrolling' and story-opening formulas."},
            {"tag": "Sound", "title": "Trending Sounds & Audio", "desc": "How to spot trending sounds early and ride the wave without looking forced."},
            {"tag": "Community", "title": "Comment & Stitch Strategy", "desc": "Building community with reply videos, stitches and duets that convert followers."},
            {"tag": "Monetise", "title": "Affiliate & TikTok Shop", "desc": "Turning a following into revenue through affiliate content and TikTok Shop."},
        ],
        "stats": [
            {"num": "Consistent", "label": "Regular video cadence"},
            {"num": "Organic", "label": "Growth without ad spend"},
            {"num": "Monthly", "label": "Reports with actionable insights"},
            {"num": "Since 2016", "label": "Managing social accounts"},
        ],
    },
    "website-development": {
        "title": "A Guide to Building a Professional Website for Malaysian SMEs",
        "intro": "Your website is your digital storefront, open 24/7. Learn the difference between company profiles, e-commerce and landing pages, and which platform fits your budget and business scale.",
        "clusters": [
            {"tag": "Company Profile", "title": "Company Profile Websites", "desc": "5–7 pages to present your brand, services, portfolio and contact details professionally."},
            {"tag": "E-commerce", "title": "Online Stores & E-commerce", "desc": "WooCommerce, Shopify and custom builds — the features you need and a realistic budget."},
            {"tag": "Landing Page", "title": "Landing Pages for Campaigns", "desc": "Single-page, conversion-focused builds for Meta or Google Ads traffic."},
            {"tag": "Custom", "title": "Web Apps & Custom Systems", "desc": "Booking systems, admin dashboards and internal tools — when to go custom vs off-the-shelf."},
            {"tag": "Maintenance", "title": "Maintenance & Security", "desc": "SSL, backups, CMS updates and security patches — the annual running costs."},
        ],
        "stats": [
            {"num": "RM 1.5K+", "label": "Starting website price"},
            {"num": "Mobile-first", "label": "Responsive on every device"},
            {"num": "SEO-ready", "label": "Built to be found on Google"},
            {"num": "Since 2016", "label": "Building for Malaysian SMEs"},
        ],
    },
    "landing-page-design": {
        "title": "Landing Pages for a High Conversion Rate",
        "intro": "A good landing page can double or multiply the ROI of your ads. Learn the structure, copy and visual elements that produce strong conversion rates.",
        "clusters": [
            {"tag": "Structure", "title": "High-Converting Page Structure", "desc": "Hook → Problem → Solution → Proof → CTA — the pattern that drives strong conversion."},
            {"tag": "Copy", "title": "Copywriting for Landing Pages", "desc": "Headline formulas, subheadings, social proof and CTA copy that isn't generic."},
            {"tag": "Speed", "title": "PageSpeed & Core Web Vitals", "desc": "LCP < 2.5s, CLS < 0.1, INP < 200ms — why they're critical for ad performance."},
            {"tag": "Tracking", "title": "Conversion Tracking Setup", "desc": "Meta Pixel, Google Tag and the conversion API — the right setup for clean data."},
            {"tag": "Testing", "title": "A/B Testing for Landing Pages", "desc": "What to test first: the headline, the CTA, the hero image or the form fields."},
        ],
        "stats": [
            {"num": "RM 1.3K+", "label": "Starting landing page price"},
            {"num": "1 page", "label": "Focused single conversion"},
            {"num": "Ad-ready", "label": "Tuned for Meta & Google Ads"},
            {"num": "Since 2016", "label": "Building conversion pages"},
        ],
    },
    "digital-marketing-agency": {
        "title": "360° Digital Marketing for Business Growth",
        "intro": "Digital marketing is more than running ads — it's an integrated strategy across paid ads, SEO, content, social media and analytics. Learn how to build a system that's sustainable.",
        "clusters": [
            {"tag": "Strategy", "title": "Digital Marketing Strategy", "desc": "Business audit, customer journey mapping, channel selection and KPI setting."},
            {"tag": "Paid Ads", "title": "Multi-Channel Paid Advertising", "desc": "Meta, Google, TikTok, YouTube — when and how to combine them."},
            {"tag": "SEO", "title": "Search Engine Optimisation", "desc": "On-page, off-page, technical SEO and content strategy for organic traffic."},
            {"tag": "Content", "title": "Content Marketing", "desc": "Blog, video and infographics — pillar content that generates leads."},
            {"tag": "Analytics", "title": "Analytics & Reporting", "desc": "GA4, attribution models, KPI dashboards and reading data to make decisions."},
        ],
        "stats": [
            {"num": "Multi-channel", "label": "Meta, Google, TikTok & more"},
            {"num": "Integrated", "label": "Channels reinforce each other"},
            {"num": "Weekly", "label": "Transparent reporting"},
            {"num": "Since 2016", "label": "Running growth campaigns"},
        ],
    },
}


TEMPLATE = r'''---
import Layout from '../../../layouts/Layout.astro';
import Navbar from '../../../components/Navbar.svelte';
import StickyCTA from '../../../components/StickyCTA.svelte';
import Footer from '../../../components/Footer.svelte';
import RelatedServices from '../../../components/RelatedServices.svelte';
import { MessageCircle, ArrowRight, BookOpen } from 'lucide-svelte';

const SERVICE_SLUG = __SLUG__;
const SERVICE_NAME = __NAME__;
const PILLAR_TITLE = __TITLE__;
const PILLAR_INTRO = __INTRO__;
const PRICE_RANGE = __PRICERANGE__;
const SERVICE_TYPE = __SERVICETYPE__;
const STATS = __STATS__;
const CLUSTERS = __CLUSTERS__;
const FAQS = __FAQS__;
const TIERS = __TIERS__;
const CITIES = __CITIES__;
const RELATED_ITEMS = __RELATED__;

const canonical = `https://beriklan.my/${SERVICE_SLUG}/pilar/`;
const waLink = `https://wa.me/62811919328?text=${encodeURIComponent(`Hi Beriklan, I'm interested in ${SERVICE_NAME}. Please share more details.`)}`;
---

<Layout
    title={`${PILLAR_TITLE} | Complete Guide | Beriklan`}
    description={PILLAR_INTRO.slice(0, 160)}
    canonical={canonical}
    breadcrumb={[
        { name: "Home", url: "https://beriklan.my/" },
        { name: SERVICE_NAME, url: `https://beriklan.my/${SERVICE_SLUG}/` },
        { name: "Complete Guide", url: canonical }
    ]}
    faq={FAQS.map(f => ({ question: f.q, answer: f.a }))}
    service={{
        name: PILLAR_TITLE,
        description: PILLAR_INTRO.slice(0, 200),
        url: canonical,
        priceRange: PRICE_RANGE,
        serviceType: SERVICE_TYPE,
        areaServed: "Malaysia",
        provider: { name: "Beriklan.my", url: "https://beriklan.my" }
    }}
>
    <Navbar client:only="svelte" />
    <StickyCTA client:only="svelte" />

    <!-- ====================== HERO ====================== -->
    <header class="relative pt-28 md:pt-40 pb-16 md:pb-20 overflow-hidden bg-gradient-to-br from-white via-soft to-beige">
        <div class="container mx-auto px-6 max-w-4xl relative z-10">
            <nav class="text-xs text-muted mb-6 flex items-center gap-1.5">
                <a href="/" class="hover:text-accent transition">Home</a>
                <span class="text-muted/40">›</span>
                <a href={`/${SERVICE_SLUG}/`} class="hover:text-accent transition">{SERVICE_NAME}</a>
                <span class="text-muted/40">›</span>
                <span class="text-ink font-semibold">Complete Guide</span>
            </nav>

            <div class="mb-5">
                <span class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-accent text-ink text-[11px] font-bold uppercase tracking-wider rounded-full">
                    <BookOpen class="w-3 h-3" />
                    Complete Guide
                </span>
            </div>

            <h1 class="font-display font-extrabold text-3xl md:text-4xl lg:text-5xl text-ink leading-[1.1] tracking-tight mb-6">
                {PILLAR_TITLE}
            </h1>

            <p class="text-base md:text-lg text-muted leading-relaxed mb-8">
                {PILLAR_INTRO}
            </p>

            <div class="flex flex-wrap gap-3">
                <a href={waLink} target="_blank" rel="noopener" class="inline-flex items-center gap-2 px-6 py-3 bg-accent hover:bg-accent/90 text-ink font-bold text-sm rounded-full shadow-pop transition">
                    <MessageCircle class="w-4 h-4" />
                    Contact Us
                </a>
                <a href={`/${SERVICE_SLUG}/`} class="inline-flex items-center gap-2 px-6 py-3 border-2 border-primary text-primary hover:bg-primary hover:text-white font-bold text-sm rounded-full transition">
                    View Packages & Pricing
                    <ArrowRight class="w-4 h-4" />
                </a>
            </div>
        </div>
    </header>

    <!-- ====================== STATS ====================== -->
    <section class="py-12 md:py-16 bg-white border-y border-gray-100">
        <div class="container mx-auto px-6">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
                {STATS.map((stat) => (
                    <div class="text-center reveal">
                        <div class="text-2xl md:text-4xl font-display font-extrabold text-primary mb-1 tabular-nums">{stat.num}</div>
                        <div class="text-xs md:text-sm text-muted leading-snug">{stat.label}</div>
                    </div>
                ))}
            </div>
        </div>
    </section>

    <!-- ====================== CLUSTERS ====================== -->
    <section class="py-16 md:py-20">
        <div class="container mx-auto px-6 max-w-5xl">
            <div class="text-center mb-12 reveal">
                <span class="text-xs font-bold uppercase tracking-[0.2em] text-accent">Topical Clusters</span>
                <h2 class="text-3xl md:text-4xl font-display font-extrabold text-ink mt-3 mb-4">
                    5 Key {SERVICE_NAME} Topics
                </h2>
                <p class="text-base md:text-lg text-muted max-w-2xl mx-auto">
                    The core areas we work through with every client — from strategy to measurable results.
                </p>
            </div>

            <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-5 reveal-stagger">
                {CLUSTERS.map((cluster) => (
                    <div class="p-6 bg-white rounded-2xl border border-gray-100 hover:border-accent/30 hover:shadow-pop transition-all duration-300">
                        <div class="inline-flex items-center gap-1.5 px-3 py-1 bg-accent/10 text-accent text-[10px] font-bold uppercase tracking-wider rounded-full mb-4">
                            {cluster.tag}
                        </div>
                        <h3 class="text-lg font-display font-bold text-ink mb-2 leading-snug">{cluster.title}</h3>
                        <p class="text-sm text-muted leading-relaxed">{cluster.desc}</p>
                    </div>
                ))}
            </div>
        </div>
    </section>

    <!-- ====================== CITIES ====================== -->
    <section class="py-16 md:py-20 bg-soft">
        <div class="container mx-auto px-6 max-w-5xl">
            <div class="text-center mb-10 reveal">
                <span class="text-xs font-bold uppercase tracking-[0.2em] text-accent">Coverage Area</span>
                <h2 class="text-3xl md:text-4xl font-display font-extrabold text-ink mt-3 mb-4">
                    Available in {CITIES.length}+ Malaysian Cities
                </h2>
                <p class="text-base md:text-lg text-muted max-w-2xl mx-auto">
                    {SERVICE_NAME} for SMEs and businesses in your city. Every city page has local context: audience, SME landscape and regional trust signals.
                </p>
            </div>

            <div class="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 reveal-stagger">
                {CITIES.map((c) => (
                    <a href={`/${SERVICE_SLUG}/${c.slug}/`} class="text-center px-3 py-3 bg-white border border-gray-100 rounded-xl hover:border-accent/30 hover:shadow-sm transition text-sm font-semibold text-ink hover:text-accent">
                        {c.name}
                    </a>
                ))}
            </div>
        </div>
    </section>

    <!-- ====================== FAQ ====================== -->
    {FAQS.length > 0 && (
    <section class="py-16 md:py-20 bg-white">
        <div class="container mx-auto px-6 max-w-3xl">
            <div class="text-center mb-10 reveal">
                <span class="text-xs font-bold uppercase tracking-[0.2em] text-accent">FAQ</span>
                <h2 class="text-3xl md:text-4xl font-display font-extrabold text-ink mt-3">
                    Frequently Asked Questions
                </h2>
            </div>

            <div class="space-y-4 reveal-stagger">
                {FAQS.map((faq) => (
                    <details class="group bg-soft rounded-2xl border border-gray-100 overflow-hidden">
                        <summary class="flex items-center justify-between gap-4 px-6 py-4 cursor-pointer font-display font-bold text-ink hover:text-accent transition">
                            <span class="text-base md:text-lg">{faq.q}</span>
                            <span class="shrink-0 w-8 h-8 rounded-full bg-white border border-gray-200 flex items-center justify-center group-open:rotate-45 transition-transform text-lg">+</span>
                        </summary>
                        <div class="px-6 pb-5 text-muted leading-relaxed text-sm md:text-base">
                            {faq.a}
                        </div>
                    </details>
                ))}
            </div>
        </div>
    </section>
    )}

    <!-- ====================== RELATED SERVICES ====================== -->
    <RelatedServices
        client:visible
        items={RELATED_ITEMS}
        title="Combine With Other Channels"
        subtitle="Effective businesses usually run ads on 2-3 channels at once so they reinforce each other."
    />

    <!-- ====================== FINAL CTA ====================== -->
    <section class="py-20 md:py-28 bg-gradient-to-br from-primary via-primary-2 to-primary text-white relative overflow-hidden">
        <div class="container mx-auto px-6 max-w-3xl text-center relative z-10">
            <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur text-white text-xs font-bold uppercase tracking-wider rounded-full mb-6">
                Team online · replies within 1 hour
            </div>
            <h2 class="font-display font-extrabold text-3xl md:text-4xl lg:text-5xl mb-6 leading-tight">
                Ready to Improve Your {SERVICE_NAME} Performance?
            </h2>
            <p class="text-base md:text-lg text-white/80 leading-relaxed mb-8 max-w-2xl mx-auto">
                A consultation — no commitment. We discuss your goals, then map out a measurable {SERVICE_NAME} strategy.
            </p>
            <div class="flex flex-wrap gap-3 justify-center">
                <a href={waLink} target="_blank" rel="noopener" class="inline-flex items-center gap-2 px-7 py-4 bg-accent hover:bg-accent/90 text-ink font-bold text-sm md:text-base rounded-full shadow-lg transition">
                    <MessageCircle class="w-5 h-5" />
                    Chat on WhatsApp
                </a>
                <a href={`/${SERVICE_SLUG}/`} class="inline-flex items-center gap-2 px-7 py-4 bg-white/10 hover:bg-white/20 backdrop-blur text-white font-bold text-sm md:text-base rounded-full border border-white/20 transition">
                    View Packages & Pricing
                    <ArrowRight class="w-4 h-4" />
                </a>
            </div>
        </div>
    </section>

    <Footer />
</Layout>
'''


def j(v):
    return json.dumps(v, ensure_ascii=False)


def main():
    services = {s["slug"]: s for s in json.load(open(os.path.join(DATA, "services.json"), encoding="utf-8"))}
    cities = json.load(open(os.path.join(DATA, "cities.json"), encoding="utf-8"))
    my_cities = [{"slug": c["slug"], "name": c["name"]} for c in cities if not c.get("is_international")]
    related = json.load(open(os.path.join(DATA, "related-services.json"), encoding="utf-8"))["services"]

    # (Re)write pillar-config.json as the source of truth.
    config = {}
    for slug, p in PILLAR.items():
        config[slug] = {"title": p["title"], "intro": p["intro"], "clusters": p["clusters"], "stats": p["stats"]}
    json.dump(config, open(os.path.join(DATA, "pillar-config.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"Wrote pillar-config.json ({len(config)} services)")

    written = 0
    for slug, (name, price_range, service_type, _label) in META.items():
        p = PILLAR[slug]
        svc = services.get(slug, {})
        faqs = (svc.get("faqs") or [])[:6]
        tiers = svc.get("tiers") or []
        rel_items = [{"icon": r["icon"], "label": r["label"], "desc": r["desc"], "href": "/" + r["slug"] + "/"}
                     for r in related.get(slug, [])]

        body = (
            TEMPLATE
            .replace("__SLUG__", j(slug))
            .replace("__NAME__", j(name))
            .replace("__TITLE__", j(p["title"]))
            .replace("__INTRO__", j(p["intro"]))
            .replace("__PRICERANGE__", j(price_range))
            .replace("__SERVICETYPE__", j(service_type))
            .replace("__STATS__", j(p["stats"]))
            .replace("__CLUSTERS__", j(p["clusters"]))
            .replace("__FAQS__", j(faqs))
            .replace("__TIERS__", j(tiers))
            .replace("__CITIES__", j(my_cities))
            .replace("__RELATED__", j(rel_items))
        )

        out_dir = os.path.join(PAGES, slug, "pilar")
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.astro"), "w", encoding="utf-8") as f:
            f.write(body)
        written += 1
        print(f"  wrote {slug}/pilar/index.astro  (faqs={len(faqs)}, related={len(rel_items)})")

    print(f"Done. {written} pillar pages -> {len(my_cities)} cities linked each.")


if __name__ == "__main__":
    main()
