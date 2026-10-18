#!/usr/bin/env python3
"""F1-9 + F1-10: services.json -> English + MYR pricing (research-based, plan §1.4)."""
import json

OUT = "/Users/maabook/Desktop/beriklan.my/web/src/data/services.json"

def faq_set(svc, low, high, setup="1–3 working days"):
    return [
        {"q": f"How much does {svc} cost at Beriklan?",
         "a": f"Packages start from RM {low}/month and go up to RM {high} for our most complete plan with full campaign management. Ad spend (media budget) is paid separately to the platform. Contact us for a consultation."},
        {"q": f"How long does it take to set up a {svc} campaign?",
         "a": f"Initial setup takes {setup}, including audience research, creative preparation and tracking configuration. Your campaign goes live shortly after you approve the strategy."},
        {"q": "Is the ad budget included in the package price?",
         "a": "No. The package covers strategy, setup, creative direction, optimisation and reporting. Your ad budget is paid directly to the ad platform through your own account — you keep full ownership and transparency."},
        {"q": "Is there a minimum contract?",
         "a": "No long-term lock-in. Packages run in 30-day cycles and you can pause or stop at the end of any cycle. Most clients stay because the numbers make sense, not because of a contract."},
        {"q": "What reporting will I receive?",
         "a": "A weekly report in plain language every Monday — spend, results, cost per result and what we are changing next — plus real-time dashboard access so you can verify everything yourself."},
    ]

def steps(platform):
    return [
        {"num": "01", "tag": "WEEK 1", "title": "Brief & Research",
         "desc": f"A 30-minute discussion to understand your product, target market and goals. We map the {platform} targeting strategy that fits."},
        {"num": "02", "tag": "WEEK 1-2", "title": "Setup & Creative",
         "desc": "We prepare the ad account, tracking pixels and ad materials (images, video, copy). You approve, we execute."},
        {"num": "03", "tag": "WEEK 2+", "title": "30-Day Launch",
         "desc": f"Your ads run for a full 30 days across {platform} placements. You receive a report every Monday morning."},
        {"num": "04", "tag": "ONGOING", "title": "Optimise & Rotate",
         "desc": "We monitor performance daily. Underperforming ads are replaced; winners are scaled up."},
    ]

def tier(name, price, duration, tagline, features, highlight=False, note=None, disc=None):
    t = {"name": name, "priceLabel": price, "duration": duration, "tagline": tagline, "features": features}
    if highlight: t["highlight"] = True
    t["priceNote"] = note or "per month, excludes ad spend"
    t["disclaimer"] = disc or "Ad budget is paid directly to the platform via your own account."
    return t

BASE_ADS_FEAT = lambda plat, reach: [
    f"Estimated reach {reach} per day",
    f"Delivery across all {plat} placements",
    "Ad creatives prepared and rotated for you",
    "Ads can be replaced mid-cycle",
    "Weekly report in plain language",
    "Real-time dashboard access",
]

services = []

services.append({
    "slug": "facebook-ads-management", "name": "Facebook Ads Management", "category": "paid-ads", "order": 1, "active": True,
    "description": "Professional Facebook Ads management by Beriklan. Meta-certified team, reply within 1 hour during business hours, weekly reports and a real-time dashboard.",
    "faqs": faq_set("Facebook Ads management", "990", "2,990"),
    "why_features": [
        {"icon": "🎯", "title": "Precise Targeting", "desc": "Over 100 interest, behaviour and demographic categories that can be combined. We select the mix that best matches your audience in Malaysia."},
        {"icon": "📊", "title": "Numbers You Can Read", "desc": "The Meta dashboard shows exactly who saw, clicked and enquired — and you can verify everything yourself at any time."},
        {"icon": "💬", "title": "Direct WhatsApp Chats", "desc": "Meta's built-in call-to-action sends clicks straight to WhatsApp — closing the gap between 'interested' and 'talking to you'."},
    ],
    "how_steps": steps("Facebook"),
    "city_intro_template": "",
    "tiers": [
        tier("Starter", "990", "30-day campaign", "For businesses starting consistent, targeted Facebook advertising.", BASE_ADS_FEAT("Facebook", "3,000–9,000 people")),
        tier("Business", "1,990", "30-day campaign", "For businesses ready to scale with more creatives and deeper optimisation.", BASE_ADS_FEAT("Facebook", "8,000–20,000 people") + ["A/B testing across audiences and creatives"], highlight=True),
        tier("Premium", "2,990", "30-day campaign", "Full-funnel management with retargeting and conversion optimisation.", BASE_ADS_FEAT("Facebook", "15,000–40,000 people") + ["Retargeting & lookalike audiences", "Dedicated account strategist"]),
    ],
})

services.append({
    "slug": "instagram-ads-management", "name": "Instagram Ads Management", "category": "paid-ads", "order": 2, "active": True,
    "description": "Instagram Ads management focused on reach, engagement and enquiries. Meta-certified team managing campaigns since 2016.",
    "faqs": faq_set("Instagram Ads management", "990", "2,990"),
    "why_features": [
        {"icon": "📸", "title": "Visual-First Creative", "desc": "Feed, Stories and Reels formats prepared to match how Malaysians actually scroll — thumb-stopping in the first second."},
        {"icon": "🎯", "title": "Interest & Behaviour Targeting", "desc": "We combine Meta's targeting signals to reach the people most likely to buy, not just to like."},
        {"icon": "💬", "title": "DM & WhatsApp Funnels", "desc": "Click-to-message campaigns that turn views into conversations you can close."},
    ],
    "how_steps": steps("Instagram"),
    "city_intro_template": "",
    "tiers": [
        tier("Starter", "990", "30-day campaign", "Consistent, targeted Instagram presence for growing brands.", BASE_ADS_FEAT("Instagram", "3,000–9,000 people")),
        tier("Business", "1,990", "30-day campaign", "Scale reach and engagement with more formats and testing.", BASE_ADS_FEAT("Instagram", "8,000–20,000 people") + ["Stories & Reels ad formats included"], highlight=True),
        tier("Premium", "2,990", "30-day campaign", "Full-funnel Instagram: awareness, retargeting, conversion.", BASE_ADS_FEAT("Instagram", "15,000–40,000 people") + ["Retargeting & lookalike audiences", "Dedicated account strategist"]),
    ],
})

services.append({
    "slug": "tiktok-ads-management", "name": "TikTok Ads Management", "category": "paid-ads", "order": 3, "active": True,
    "description": "TikTok Ads management — Spark Ads, In-Feed and TikTok Shop campaigns for the Malaysian market.",
    "faqs": faq_set("TikTok Ads management", "790", "1,990"),
    "why_features": [
        {"icon": "🔥", "title": "Native, Not 'Ad-Looking'", "desc": "TikTok rewards content that feels organic. We build Spark Ads from content that already earns watch time."},
        {"icon": "🛍", "title": "TikTok Shop Ready", "desc": "Campaigns wired to TikTok Shop Malaysia — from FYP view to checkout without leaving the app."},
        {"icon": "📈", "title": "Fast Iteration", "desc": "Creative fatigue hits fast on TikTok. We rotate and test hooks weekly to keep costs down."},
    ],
    "how_steps": steps("TikTok"),
    "city_intro_template": "",
    "tiers": [
        tier("Basic", "790", "30-day campaign", "Entry plan to validate TikTok as a channel for your business.", BASE_ADS_FEAT("TikTok", "4,000–12,000 people")[:5]),
        tier("Standard", "1,290", "30-day campaign", "Consistent TikTok presence with Spark Ads and weekly creative rotation.", BASE_ADS_FEAT("TikTok", "10,000–25,000 people")[:5] + ["Spark Ads from your organic content"], highlight=True),
        tier("Business", "1,990", "30-day campaign", "Aggressive growth with TikTok Shop integration and retargeting.", BASE_ADS_FEAT("TikTok", "20,000–50,000 people") + ["TikTok Shop campaign integration"]),
    ],
})

services.append({
    "slug": "google-ads-management", "name": "Google Ads Management", "category": "paid-ads", "order": 4, "active": True,
    "description": "Google Ads management — Search, Display and YouTube. Capture Malaysians who are already searching for what you sell.",
    "faqs": faq_set("Google Ads management", "990", "2,790"),
    "why_features": [
        {"icon": "🔍", "title": "High-Intent Traffic", "desc": "Search ads reach people at the exact moment they are looking for your product or service — the warmest traffic money can buy."},
        {"icon": "🧮", "title": "Keyword Economics", "desc": "We build keyword lists around buying intent and negative-match the waste, so budget goes to clicks that can convert."},
        {"icon": "📊", "title": "Conversion Tracking Done Right", "desc": "Calls, WhatsApp clicks and form fills tracked properly, so decisions are based on results — not guesses."},
    ],
    "how_steps": steps("Google"),
    "city_intro_template": "",
    "tiers": [
        tier("Basic", "990", "30-day campaign", "Search campaign for one core service or product line.", ["Keyword & competitor research", "Search campaign setup and management", "Ad copywriting (multiple variants)", "Negative keyword management", "Conversion tracking setup", "Weekly plain-language report", "Real-time dashboard access"]),
        tier("Standard", "1,790", "30-day campaign", "Search + Display for stronger coverage across the funnel.", ["Everything in Basic", "Display remarketing campaigns", "Landing page recommendations", "A/B ad testing", "Bi-weekly optimisation sprints", "Weekly plain-language report"], highlight=True),
        tier("Business", "2,790", "30-day campaign", "Full Google stack: Search, Display and YouTube with dedicated strategy.", ["Everything in Standard", "YouTube video campaigns", "Advanced audience layering", "Quarterly strategy review", "Dedicated account strategist", "Priority support (reply within 1 hour)", "Weekly plain-language report"]),
    ],
})

services.append({
    "slug": "youtube-ads-management", "name": "YouTube Ads Management", "category": "paid-ads", "order": 5, "active": True,
    "description": "YouTube Ads management — video campaigns for awareness and conversion across Malaysia.",
    "faqs": faq_set("YouTube Ads management", "890", "2,490"),
    "why_features": [
        {"icon": "🎬", "title": "Video That Earns Attention", "desc": "Skippable in-stream, bumper and Shorts formats matched to your objective — awareness, consideration or action."},
        {"icon": "🎯", "title": "Audience Precision", "desc": "Target by search history, interests, life events and custom intent — YouTube inherits Google's targeting depth."},
        {"icon": "💰", "title": "Pay for Attention Only", "desc": "With skippable ads, you only pay when viewers actually watch — cost-efficient awareness at scale."},
    ],
    "how_steps": steps("YouTube"),
    "city_intro_template": "",
    "tiers": [
        tier("Basic", "890", "30-day campaign", "Entry video campaign to test YouTube for your brand.", ["Campaign setup & audience research", "1 video format (in-stream or Shorts)", "Basic conversion tracking", "Weekly plain-language report", "Real-time dashboard access"]),
        tier("Starter", "1,490", "30-day campaign", "Broader reach with multiple formats and audience testing.", ["Everything in Basic", "2 video formats running in parallel", "Audience A/B testing", "Remarketing audience building", "Weekly plain-language report"]),
        tier("Standard", "1,990", "30-day campaign", "Structured awareness-to-action funnel on YouTube.", ["Everything in Starter", "Full-funnel campaign structure", "Custom intent audiences", "Landing page recommendations", "Weekly plain-language report"], highlight=True),
        tier("Business", "2,490", "30-day campaign", "Complete YouTube programme with dedicated strategy.", ["Everything in Standard", "Creative direction & script input", "Advanced measurement setup", "Quarterly strategy review", "Dedicated account strategist", "Priority support"]),
    ],
})

services.append({
    "slug": "instagram-management", "name": "Instagram Management", "category": "organic", "order": 6, "active": True,
    "description": "Organic Instagram management — content, community and consistency for brands in Malaysia.",
    "faqs": faq_set("Instagram management", "1,290", "1,990", setup="5–7 working days for the first content calendar"),
    "why_features": [
        {"icon": "📅", "title": "Consistent Publishing", "desc": "A planned content calendar executed on schedule — feed, Stories and Reels — so your brand stays visible without you chasing it."},
        {"icon": "🎨", "title": "On-Brand Design", "desc": "Templates and visual direction that keep your grid professional and recognisable."},
        {"icon": "🤝", "title": "Community Care", "desc": "Comments and DMs handled with your tone of voice, business hours coverage."},
    ],
    "how_steps": [
        {"num": "01", "tag": "WEEK 1", "title": "Brand & Audience Audit", "desc": "We review your profile, competitors and audience to define content pillars that fit your goals."},
        {"num": "02", "tag": "WEEK 1-2", "title": "Content Calendar", "desc": "A monthly calendar of posts, Stories and Reels for your approval before anything goes live."},
        {"num": "03", "tag": "WEEK 2+", "title": "Publish & Engage", "desc": "We publish on schedule and manage comments and DMs during business hours."},
        {"num": "04", "tag": "MONTHLY", "title": "Review & Refine", "desc": "Monthly performance review — what grew, what didn't, and what changes next month."},
    ],
    "city_intro_template": "",
    "tiers": [
        tier("Basic", "1,290", "per month", "Steady, professional presence for growing brands.", ["12 feed posts per month", "8 Stories per month", "Content calendar with approval flow", "Caption copywriting in English/BM", "Monthly performance report"], note="per month"),
        tier("Standard", "1,990", "per month", "Full content engine with Reels and community management.", ["16 feed posts per month", "12 Stories + 4 Reels per month", "Community management (comments & DMs)", "Hashtag & trend research", "Monthly strategy call", "Monthly performance report"], highlight=True, note="per month"),
        tier("Business", "Custom", "per month", "Tailored scope for multi-brand or high-volume accounts.", ["Custom content volume", "Dedicated content strategist", "Photo/video production coordination", "Influencer collaboration support", "Weekly reporting"], note="tailored quote"),
    ],
})

services.append({
    "slug": "tiktok-management", "name": "TikTok Management", "category": "organic", "order": 7, "active": True,
    "description": "TikTok account management — routine video content and TikTok Shop operations for the Malaysian market.",
    "faqs": faq_set("TikTok management", "990", "2,490", setup="5–7 working days for the first content plan"),
    "why_features": [
        {"icon": "🎬", "title": "Routine Video Output", "desc": "Consistent short-video publishing built around hooks that earn watch time on the FYP."},
        {"icon": "🛍", "title": "TikTok Shop Operations", "desc": "Product listing hygiene, campaign hooks and content that drives in-app checkout."},
        {"icon": "📈", "title": "Trend Responsiveness", "desc": "We monitor Malaysian TikTok trends weekly and slot relevant formats into your calendar fast."},
    ],
    "how_steps": [
        {"num": "01", "tag": "WEEK 1", "title": "Account & Niche Audit", "desc": "We review your account, category and competitors to define a content angle that can win."},
        {"num": "02", "tag": "WEEK 1-2", "title": "Content Plan", "desc": "A monthly plan of video concepts and hooks for your approval."},
        {"num": "03", "tag": "WEEK 2+", "title": "Produce & Publish", "desc": "Videos edited and published on schedule, optimised for watch time."},
        {"num": "04", "tag": "MONTHLY", "title": "Review & Double Down", "desc": "Monthly review of what the algorithm rewarded — we double down on the winners."},
    ],
    "city_intro_template": "",
    "tiers": [
        tier("TikTok Shop", "990", "per month", "Shop-focused plan: listings, content hooks and campaign support.", ["TikTok Shop setup & listing optimisation", "8 shop-focused videos per month", "Campaign & voucher planning", "Monthly performance report"], note="per month"),
        tier("Basic Content", "1,690", "per month", "Consistent organic growth through routine video content.", ["12 videos per month (edited)", "Hook & script writing", "Trend monitoring & adaptation", "Community management", "Monthly performance report"], highlight=True, note="per month"),
        tier("Business Content", "2,490", "per month", "High-volume content engine with strategy support.", ["20 videos per month (edited)", "Content strategist assigned", "TikTok Shop integration", "Live session planning support", "Weekly reporting"], note="per month"),
    ],
})

services.append({
    "slug": "website-development", "name": "Website Development", "category": "build", "order": 8, "active": True,
    "description": "Professional website development — fast, SEO-ready and built to convert visitors into enquiries.",
    "faqs": [
        {"q": "How much does a website cost at Beriklan?",
         "a": "Our Starter business website is RM 1,499 one-time. Corporate websites are RM 3,999 and e-commerce builds start from RM 6,999 depending on scope. All prices include design, development and launch."},
        {"q": "How long does it take to build?",
         "a": "A Starter website launches in 7–14 working days after content is ready. Corporate and e-commerce builds typically take 3–6 weeks."},
        {"q": "Is hosting and domain included?",
         "a": "First-year domain and fast cloud hosting are included in every package. Renewals are billed at cost — no hidden markup."},
        {"q": "Will my website work on mobile?",
         "a": "Yes — every build is mobile-first, tested on real devices, and optimised for Core Web Vitals so it loads fast on Malaysian mobile networks."},
        {"q": "Can you also bring traffic to the website?",
         "a": "Yes. Most clients pair a build with Google Ads or Facebook Ads management. We design the site and the campaign as one funnel, which is why our builds convert."},
    ],
    "why_features": [
        {"icon": "⚡", "title": "Fast by Default", "desc": "Static-first builds that score 90+ on PageSpeed — because slow sites lose Malaysian mobile visitors."},
        {"icon": "🔍", "title": "SEO-Ready Structure", "desc": "Clean headings, schema markup and sitemaps from day one, so Google understands your site immediately."},
        {"icon": "📞", "title": "Built to Convert", "desc": "WhatsApp CTAs, click-to-call and enquiry forms positioned where visitors actually decide."},
    ],
    "how_steps": [
        {"num": "01", "tag": "WEEK 1", "title": "Scope & Sitemap", "desc": "We define pages, structure and the action you want visitors to take."},
        {"num": "02", "tag": "WEEK 1-2", "title": "Design & Content", "desc": "Design direction and copywriting support — you approve before we build."},
        {"num": "03", "tag": "WEEK 2-3", "title": "Build & Test", "desc": "Development, mobile testing and speed optimisation."},
        {"num": "04", "tag": "LAUNCH", "title": "Launch & Handover", "desc": "Domain, hosting, analytics and a walkthrough so you own everything."},
    ],
    "city_intro_template": "",
    "tiers": [
        tier("Starter", "1,499", "7–14 working days", "A professional business website that loads fast and converts.", ["Up to 5 pages", "Mobile-first responsive design", "WhatsApp & enquiry form integration", "Basic on-page SEO", "Domain + 1 year hosting included", "Google Analytics & Search Console setup"], note="one-time", disc="Includes first-year domain and hosting."),
        tier("Corporate", "3,999", "3–4 weeks", "For established companies that need depth and polish.", ["Up to 15 pages", "Custom design system", "Blog / news module", "Advanced on-page SEO + schema markup", "Multi-language ready (EN/BM)", "Priority support after launch"], highlight=True, note="one-time", disc="Includes first-year domain and hosting."),
        tier("E-commerce", "from 6,999", "4–6 weeks", "Online store with payments, inventory and marketing hooks.", ["Product catalogue & inventory", "Local payment gateway integration", "Shipping configuration for Malaysia", "Marketing & analytics integration", "Staff training session", "Get a tailored quote"], note="from, one-time", disc="Final quote depends on catalogue size and integrations."),
    ],
})

services.append({
    "slug": "landing-page-design", "name": "Landing Page + Google Ads", "category": "build", "order": 9, "active": True,
    "description": "High-converting landing page bundled with Google Ads setup and first-month management — one funnel, one team.",
    "faqs": [
        {"q": "What exactly is included in the bundle?",
         "a": "A custom one-page landing page (design + copy + build), Google Ads account setup, conversion tracking, and the first month of campaign management — RM 1,299 all-in, excluding ad spend."},
        {"q": "How long until my campaign is live?",
         "a": "Typically 7–10 working days from brief to live campaign, including your approval rounds."},
        {"q": "Why bundle the page with the ads?",
         "a": "Because the page and the ad must tell one story. When the same team builds both, message match improves and cost per enquiry drops."},
        {"q": "Is ad spend included?",
         "a": "No — ad budget is paid directly to Google through your own account. We recommend starting from RM 1,500/month in ad spend for meaningful data."},
        {"q": "What happens after the first month?",
         "a": "You can continue with a Google Ads management plan (from RM 990/month), or keep the landing page and run it yourself — you own everything we build."},
    ],
    "why_features": [
        {"icon": "🧲", "title": "Message Match", "desc": "Ad copy and landing page written together, so visitors see exactly what they clicked for."},
        {"icon": "⚡", "title": "Speed = Conversions", "desc": "Sub-2-second load times — every extra second of loading costs you enquiries."},
        {"icon": "📊", "title": "Tracked End-to-End", "desc": "WhatsApp clicks, calls and form fills tracked from the first day, so you know your real cost per lead."},
    ],
    "how_steps": [
        {"num": "01", "tag": "DAY 1-2", "title": "Offer & Angle", "desc": "We define the offer, audience and the one action the page must drive."},
        {"num": "02", "tag": "DAY 3-6", "title": "Page Build", "desc": "Design, copy and build — reviewed and approved by you."},
        {"num": "03", "tag": "DAY 7-10", "title": "Ads Live", "desc": "Google Ads campaign configured, tracking verified, campaign launched."},
        {"num": "04", "tag": "DAY 10-30", "title": "Optimise", "desc": "First month of management included — bids, keywords and page tweaks."},
    ],
    "city_intro_template": "",
    "tiers": [
        tier("Landing Page + Google Ads", "1,299", "7–10 working days", "One high-converting page plus your first month of Google Ads — all-in.", ["Custom 1-page design & copywriting", "Mobile-first, sub-2s load time", "Google Ads setup + 1 month management", "Conversion tracking (WhatsApp, calls, forms)", "A/B headline variants", "You own the page and the ad account"], highlight=True, note="one-time bundle, excludes ad spend"),
        tier("Multi-Page Funnel", "2,999", "14–21 working days", "Multi-step funnel for higher-ticket offers.", ["Up to 4 funnel pages", "Lead magnet / opt-in integration", "Email automation hooks", "Google Ads setup + 1 month management", "Full analytics wiring", "Conversion-focused copywriting"], note="one-time bundle, excludes ad spend"),
        tier("Custom Web App", "Custom", "21–60 working days", "Calculators, portals, booking systems — scoped to your needs.", ["Custom functionality scoping", "UI/UX design", "Integration with your tools", "Staging & testing environment", "Training & documentation", "Get a tailored quote"], note="tailored quote"),
    ],
})

services.append({
    "slug": "digital-marketing-agency", "name": "Digital Marketing Agency", "category": "full-service", "order": 10, "active": True,
    "description": "End-to-end digital marketing for Malaysian businesses — strategy, paid media, content and landing pages under one accountable team.",
    "faqs": [
        {"q": "What does the full-service engagement include?",
         "a": "Strategy, channel selection, campaign management across Meta/Google/TikTok, creative direction, landing pages and consolidated reporting — scoped to your goals after a consultation."},
        {"q": "How is pricing determined?",
         "a": "Full-service scope is custom-quoted based on channels, volume and targets. Book a consultation and we will propose a scope with clear deliverables and pricing."},
        {"q": "Do you replace our internal team?",
         "a": "We usually complement it. Some clients hand us everything; others keep content in-house while we run paid media. The scope is built around what you already have."},
        {"q": "How soon can we see results?",
         "a": "Paid campaigns generate data within days and meaningful optimisation within 2–4 weeks. We set expectations per channel during the consultation — no inflated promises."},
        {"q": "Is there a minimum commitment?",
         "a": "Engagements run in 30-day cycles with a quarterly strategy rhythm. No long-term lock-in — the work has to justify itself."},
    ],
    "why_features": [
        {"icon": "🧭", "title": "One Accountable Team", "desc": "Strategy, ads, content and pages in one place — no finger-pointing between vendors."},
        {"icon": "📊", "title": "Consolidated Reporting", "desc": "One dashboard, one weekly report across every channel — in plain language."},
        {"icon": "🔁", "title": "Budget Fluidity", "desc": "Budget moves to whichever channel is performing this month — because we manage them all."},
    ],
    "how_steps": [
        {"num": "01", "tag": "WEEK 1", "title": "Audit & Strategy", "desc": "We audit your current funnel and propose a channel mix with clear targets."},
        {"num": "02", "tag": "WEEK 2", "title": "Setup Sprint", "desc": "Accounts, tracking, creative and landing pages prepared in one coordinated sprint."},
        {"num": "03", "tag": "WEEK 3+", "title": "Launch & Learn", "desc": "Campaigns go live across the selected channels; early data guides quick corrections."},
        {"num": "04", "tag": "MONTHLY", "title": "Optimise & Reallocate", "desc": "Monthly review moves budget to winners and cuts what underperforms."},
    ],
    "city_intro_template": "",
    "tiers": [
        tier("Starter", "Free", "60-minute session", "A strategy consultation — walk away with a channel plan even if we never work together.", ["Funnel & ad account review", "Channel mix recommendation", "Budget allocation guidance", "Priority quick-wins list", "No obligation"], note="consultation"),
        tier("Growth", "Custom", "30-day cycles", "Multi-channel management scoped to your targets.", ["2–3 channels managed (Meta/Google/TikTok)", "Creative direction included", "Landing page optimisation", "Weekly consolidated reporting", "Monthly strategy call"], highlight=True, note="custom quote after consultation"),
        tier("Scale", "Custom", "30-day cycles", "Full-funnel programme for aggressive growth targets.", ["All channels + YouTube", "Dedicated strategist & designer", "CRO programme on pages", "Weekly strategy rhythm", "Quarterly executive review"], note="custom quote after consultation"),
    ],
})

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(services, f, ensure_ascii=False, indent=2)
print(f"services.json EN written — {len(services)} services")
for s in services:
    print(" -", s["slug"], "tiers:", [f"{t['name']}={t['priceLabel']}" for t in s["tiers"]])
