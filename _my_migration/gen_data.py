#!/usr/bin/env python3
"""F1-9: regenerate paa-questions.json (new English slug keys + MYR) and
testimonials.json (Malaysian English version) for beriklan.my.

paa-questions.json was keyed by OLD Indonesian slugs (jasa-iklan-facebook...)
while PAASection.astro now receives NEW slugs (facebook-ads-management...),
so every PAA section rendered empty. This rewrites the file with the new keys.
Prices are kept consistent with web/src/data/services.json.
"""
import json

DATA = "/Users/maabook/Desktop/beriklan.my/web/src/data/"

# ---------------------------------------------------------------- helpers ---
def common_paid(name, plat, fee_from, fee_top, budget_low, budget_rec):
    """Shared Q&As for paid-ads management services."""
    return [
        {"q": f"How much does {name} cost in Malaysia?",
         "a": f"Beriklan's {name.lower()} packages start from {fee_from}/month and go up to {fee_top} for the most complete plan. The fee covers strategy, setup, creative direction, daily optimisation and weekly reporting. Ad spend is paid separately to {plat}, directly from your own account."},
        {"q": f"What is a reasonable monthly ad budget for {plat} in Malaysia?",
         "a": f"For most Malaysian SMEs we recommend starting with {budget_low} to {budget_rec} per month in ad spend. This gives the algorithm enough data to optimise within 2–4 weeks. We help you scale the budget only after the numbers prove the campaign is profitable."},
        {"q": "Is the ad budget included in the management fee?",
         "a": f"No. The management fee covers our work — strategy, setup, creatives, optimisation and reporting. Your ad budget is paid directly to {plat} through your own ad account, so you keep full ownership and can see every ringgit of spend."},
        {"q": "Is there a minimum contract or lock-in period?",
         "a": "No long-term lock-in. All packages run in 30-day cycles and you can pause or stop at the end of any cycle. Most clients stay for years because the results make sense — not because a contract forces them to."},
        {"q": f"How long before I see results from {name.lower()}?",
         "a": "Initial data comes in within the first 7 days, and the learning phase typically stabilises in 2–4 weeks. By the end of the first 30-day cycle you will have a clear picture of cost per result, and we use that data to scale what works."},
        {"q": "What reports will I receive?",
         "a": "A weekly report every Monday in plain language — spend, results, cost per result and what we are changing next — plus a real-time dashboard you can open any time. No jargon-filled PDFs that nobody reads."},
        {"q": "Who owns the ad account and the data?",
         "a": "You do. We work inside your own ad account with partner access, so all campaign history, pixels, audiences and billing stay under your control. If we ever part ways, everything remains yours."},
        {"q": "Do you serve businesses outside Kuala Lumpur?",
         "a": "Yes. We manage campaigns for clients across Malaysia — KL, Selangor, Penang, Johor Bahru, East Malaysia — and everything runs remotely via WhatsApp, video calls and a shared dashboard, so location is never a barrier."},
    ]

def common_organic(name, plat, fee_from, fee_top):
    """Shared Q&As for organic management services."""
    return [
        {"q": f"How much does {name.lower()} cost in Malaysia?",
         "a": f"Beriklan's {name.lower()} packages start from {fee_from}/month, with the most complete plan at {fee_top}. The fee covers content planning, production, captions, scheduling, community management and monthly performance reports."},
        {"q": "Is there a minimum contract?",
         "a": "No long-term lock-in. Packages run in 30-day cycles. We do recommend at least 3 months, because organic growth compounds — but that is a recommendation based on data, not a contractual obligation."},
        {"q": f"Who creates the content — you or my team?",
         "a": f"We do. Our team plans the monthly calendar, writes the hooks and captions, and produces the designs or edits the videos. You review and approve everything before it goes live on {plat}, and we can also repurpose raw footage from your side."},
        {"q": "What reports will I receive?",
         "a": "A monthly performance report covering follower growth, reach, engagement rate and top-performing content — plus a content calendar for the month ahead so you always know what is being published and why."},
        {"q": "Do you serve businesses outside Kuala Lumpur?",
         "a": "Yes. Clients across Malaysia work with us fully remotely — content approvals happen via WhatsApp and a shared calendar, and video raw materials can be shot on a phone following our simple shot list."},
    ]

# ----------------------------------------------------------------- PAA data ---
paa = {}

paa["facebook-ads-management"] = common_paid(
    "Facebook Ads management", "Meta", "RM 990", "RM 2,990", "RM 1,500", "RM 5,000") + [
    {"q": "Is Facebook Ads still effective in Malaysia in 2026?",
     "a": "Yes. Facebook remains one of Malaysia's largest ad platforms with over 20 million users, and it is still the most cost-efficient channel for lead generation and local awareness — especially for F&B, services, property and retail businesses targeting Malaysians aged 25 and above."},
    {"q": "What is the difference between boosting a post and Facebook Ads management?",
     "a": "Boosting only pushes a single post with basic targeting. Proper Facebook Ads management uses Meta Ads Manager: full-funnel campaign structure, pixel and conversion tracking, custom and lookalike audiences, A/B-tested creatives and continuous optimisation — which is where real ROAS comes from."},
]

paa["instagram-ads-management"] = common_paid(
    "Instagram Ads management", "Meta", "RM 990", "RM 2,990", "RM 1,500", "RM 5,000") + [
    {"q": "Which businesses get the best results from Instagram Ads in Malaysia?",
     "a": "Visual-first businesses perform best: beauty and skincare, fashion, F&B, fitness, travel and lifestyle services. Instagram's Malaysian audience skews 18–40, so brands targeting younger urban consumers in KL, Penang and JB typically see the strongest engagement and conversion rates."},
    {"q": "Do I need good creatives before running Instagram Ads?",
     "a": "Creative quality is the biggest performance lever on Instagram, but you do not need an expensive production house. We provide creative direction, hooks and copy, and can turn simple phone-shot footage into scroll-stopping Reels and story ads that convert."},
]

paa["tiktok-ads-management"] = common_paid(
    "TikTok Ads management", "TikTok", "RM 790", "RM 1,990", "RM 1,000", "RM 3,000") + [
    {"q": "Is TikTok Ads cheaper than Facebook Ads in Malaysia?",
     "a": "Generally yes — TikTok CPMs in Malaysia are still lower than Meta's, so reach is cheaper. Conversion costs depend on your offer and creative, but for impulse-friendly products under RM 200, TikTok often delivers the lowest cost per purchase of any platform."},
    {"q": "What is Spark Ads and why does it matter?",
     "a": "Spark Ads lets you boost organic TikTok posts — yours or a creator's — as native ads that keep all likes, comments and shares. They consistently outperform standard in-feed ads because they look and feel like real content, not advertising."},
]

paa["google-ads-management"] = common_paid(
    "Google Ads management", "Google", "RM 990", "RM 2,790", "RM 1,500", "RM 5,000") + [
    {"q": "What is the difference between Google Ads and SEO?",
     "a": "Google Ads puts you at the top of search results immediately and you pay per click; SEO builds free rankings over 6–12 months. They complement each other: Ads captures demand today while SEO compounds. For fast, measurable leads, Google Ads is the starting point."},
    {"q": "Which Google Ads campaign types do you manage?",
     "a": "Search, Performance Max, Display, Shopping and YouTube campaigns. For most Malaysian service businesses we start with Search — capturing people actively looking for what you sell — then layer in Performance Max or remarketing once conversion data builds up."},
]

paa["youtube-ads-management"] = common_paid(
    "YouTube Ads management", "Google", "RM 890", "RM 2,490", "RM 1,000", "RM 3,000") + [
    {"q": "How much does it cost to advertise on YouTube in Malaysia?",
     "a": "YouTube views in Malaysia typically cost between RM 0.03 and RM 0.15 per view depending on targeting and format. With a RM 1,000–3,000 monthly budget you can realistically reach tens of thousands of relevant viewers, making it one of the cheapest awareness channels available."},
    {"q": "Do I need a professionally produced video to run YouTube Ads?",
     "a": "No. A clear 15–30 second video shot on a phone with a strong hook in the first 5 seconds often outperforms polished TV-style commercials. We provide the script structure and hook formulas, and can guide simple production remotely."},
]

paa["digital-marketing-agency"] = [
    {"q": "How much does it cost to hire a digital marketing agency in Malaysia?",
     "a": "Malaysian agencies typically charge RM 1,500–8,000 per month depending on scope. Beriklan works differently: we start with a audit, then quote a custom retainer based on the channels you actually need — most multi-channel clients invest RM 2,000–5,000 per month in management fees."},
    {"q": "What does a digital marketing agency actually do?",
     "a": "A performance-focused agency plans your channel strategy, runs and optimises your ad campaigns, manages content, tracks every conversion and reports results in plain language. The goal is simple: turn your marketing budget into measurable revenue, not vanity metrics."},
    {"q": "How do I choose the right digital marketing agency in Malaysia?",
     "a": "Look for three things: transparent reporting with real numbers, direct access to your own ad accounts, and no long-term lock-in contracts. If an agency hides the ad account, hides the data or needs a 12-month contract to keep you — walk away."},
    {"q": "Should I hire an agency or build an in-house team?",
     "a": "An in-house marketer in Malaysia costs RM 4,000–8,000 per month for one person's skill set. An agency gives you a full team — strategist, media buyer, designer, copywriter — for a similar or lower cost, plus cross-industry data an individual hire cannot match."},
    {"q": "Which digital marketing channels work best in Malaysia?",
     "a": "It depends on the business: Meta (Facebook and Instagram) for local leads and retail, Google Search for high-intent services, TikTok for products under RM 200 and younger audiences, and YouTube for awareness. We audit first, then recommend only the channels the data supports."},
    {"q": "Is there a minimum contract?",
     "a": "No long-term lock-in. Engagements run in 30-day cycles, and you can adjust the channel mix or stop at the end of any cycle. We believe results — not contracts — should be the reason clients stay."},
    {"q": "What reports will I receive?",
     "a": "A single consolidated weekly report across all channels — spend, results, cost per result and next actions — plus a real-time dashboard. One report, plain language, every Monday."},
    {"q": "Who owns the ad accounts and data?",
     "a": "You do. All ad accounts, pixels, audiences and creative assets are set up under your business's ownership with Beriklan added as a partner. If we ever part ways, every asset and every byte of data stays with you."},
    {"q": "Do you work with small businesses or only large brands?",
     "a": "Both. Most of our clients are Malaysian SMEs spending RM 1,500–15,000 per month on ads. Our packages are structured so a growing business can start lean on one channel and scale into multi-channel as revenue grows."},
    {"q": "Do you serve businesses outside Kuala Lumpur?",
     "a": "Yes. We work with clients across Malaysia and the region entirely remotely — onboarding, strategy calls and reporting all happen online, so you get the same service whether you are in KL, Penang, JB, Kota Kinabalu or Kuching."},
]

paa["instagram-management"] = common_organic(
    "Instagram Management", "Instagram", "RM 1,290", "RM 1,990 (with custom plans above that)") + [
    {"q": "How many posts per month do I get?",
     "a": "Our packages range from 12 to 20 pieces of content per month — a strategic mix of feed posts, Reels and Stories. The exact mix is set in your monthly calendar based on what the data shows is growing your reach and engagement."},
    {"q": "How long does it take to grow an Instagram account organically?",
     "a": "Meaningful growth typically shows within 2–3 months of consistent, strategy-led posting. Reels are the fastest lever for reach in Malaysia right now; engagement and follower quality compound from there. Anyone promising thousands of followers in a week is selling bots."},
    {"q": "Do you reply to comments and DMs?",
     "a": "Community management is included in our higher-tier packages — we respond to comments and route sales enquiries to your team via WhatsApp. On the starter package we provide response templates and flag important conversations for you."},
    {"q": "Can you combine Instagram management with paid ads?",
     "a": "Yes, and it is the most effective setup: organic content builds trust and social proof while a small ad budget amplifies the best-performing posts. Many clients bundle Instagram management with Meta ads for a complete funnel."},
    {"q": "Will my account be safe? Do you need my password?",
     "a": "We work through Meta Business Suite partner access wherever possible, so you never need to hand over your password. Your account, followers and data remain fully yours at all times."},
]

paa["tiktok-management"] = common_organic(
    "TikTok Management", "TikTok", "RM 990", "RM 2,490 (20 videos per month)") + [
    {"q": "How many TikTok videos do I get per month?",
     "a": "Packages range from 8 to 20 edited videos per month. The top tier at RM 2,490 includes 20 videos — enough for near-daily posting, which is the consistency level the TikTok algorithm rewards most in Malaysia."},
    {"q": "How do I get on the FYP (For You Page) in Malaysia?",
     "a": "The FYP rewards watch time and completion rate, not follower count. That means strong hooks in the first 2 seconds, native-style editing, trending sounds used early and consistent posting. Our editors build every video around these signals."},
    {"q": "Do I need to appear on camera?",
     "a": "It helps but is not mandatory. We build content systems around faceless formats too — product demos, voiceovers, text-led storytelling and trends. If you or a team member can front the camera, we script everything so filming takes minutes."},
    {"q": "Can TikTok content really drive sales, not just views?",
     "a": "Yes — Malaysia is one of TikTok Shop's strongest markets globally. We structure content to move viewers from entertainment to action: hook, value, soft pitch, and a clear next step to your TikTok Shop, WhatsApp or website."},
    {"q": "Can you combine TikTok management with TikTok Ads?",
     "a": "Yes, and it compounds: organic videos identify winning angles for free, then Spark Ads amplify the proven winners. Clients who bundle management with ads typically reach profitable scale faster than with either alone."},
]

paa["website-development"] = [
    {"q": "How much does website development cost in Malaysia?",
     "a": "Beriklan's website packages start from RM 1,499 for a professional company profile, RM 3,999 for a business website with CMS, and from RM 6,999 for custom builds or e-commerce. All packages include mobile-responsive design, SSL and basic SEO setup."},
    {"q": "How long does it take to build a website?",
     "a": "A company profile site takes 2–3 weeks from brief to launch. Business sites with CMS take 3–5 weeks, and custom or e-commerce projects 6–10 weeks depending on scope. Timelines are locked in writing before the project starts."},
    {"q": "Will my website be mobile-friendly and fast?",
     "a": "Yes. Over 80% of Malaysian web traffic is mobile, so we design mobile-first and build for speed — optimised images, modern frameworks and Core Web Vitals in the green. Speed is a ranking factor and a conversion factor; we treat it as non-negotiable."},
    {"q": "Do you include SEO in website development?",
     "a": "Every build includes technical SEO fundamentals: clean structure, meta tags, schema markup, sitemap, fast load times and Google Search Console setup. Ongoing SEO content and link building are available separately if you want to grow organic traffic."},
    {"q": "Can I update the website content myself?",
     "a": "Yes. CMS-based packages let your team edit text, images, blog posts and products without touching code. We include a handover session and a short guide so updating your site takes minutes, not support tickets."},
    {"q": "Do you provide hosting and domain?",
     "a": "We can register your .com or .com.my domain and set up fast, secure hosting on your behalf — registered under your ownership, not ours. If you already have hosting, we deploy there instead. Either way, you own everything."},
    {"q": "What do I need to prepare before the project starts?",
     "a": "Just three things: your logo and brand assets, the content or bullet points for each page (we help polish the copy), and examples of websites you like. We handle structure, design, copy refinement and everything technical."},
    {"q": "Will the website be ready to run ads to?",
     "a": "Yes — every site ships with Google Analytics 4, Meta Pixel and conversion tracking pre-installed. If you plan to run Google or Meta ads, your website is ad-ready from day one, with WhatsApp click tracking included."},
    {"q": "Do you offer maintenance after launch?",
     "a": "Every project includes 30 days of free post-launch support for bug fixes and small tweaks. After that, optional monthly maintenance covers updates, backups, security and small content changes — or your team can take over fully."},
    {"q": "Do you build e-commerce websites for the Malaysian market?",
     "a": "Yes — online stores with local payment gateways (FPX, e-wallets, cards), shipping integrations and product management. We also advise on when a full store makes sense versus starting leaner with a landing page plus WhatsApp ordering."},
]

paa["landing-page-design"] = [
    {"q": "How much does a landing page cost in Malaysia?",
     "a": "Beriklan's landing page packages start from RM 1,299 — including copywriting, mobile-first design, WhatsApp integration and conversion tracking. The RM 2,999 bundle adds Google Ads setup and first-month management, so you launch page and traffic together."},
    {"q": "What is the difference between a landing page and a website?",
     "a": "A website serves many goals and audiences; a landing page has exactly one job — convert visitors from a specific ad into leads or sales. One offer, one message, one call to action. That focus is why landing pages consistently out-convert homepages for paid traffic."},
    {"q": "Why do my ads need a dedicated landing page?",
     "a": "Sending paid traffic to a generic homepage is the most common money leak we find in audits. A dedicated page that mirrors the ad's promise typically converts 2–5× better, which directly cuts your cost per lead — often more than any targeting tweak can."},
    {"q": "How long does it take to build a landing page?",
     "a": "7–10 working days from brief to live page, including copywriting, design, WhatsApp integration and tracking setup. If you take the Google Ads bundle, campaigns typically go live within 2 weeks of project start."},
    {"q": "Is copywriting included?",
     "a": "Yes — persuasion-focused copy is the core of the service, not an add-on. We research your offer and audience, then write the headline, body and call-to-action structure. You review and approve everything before design begins."},
    {"q": "Will the landing page work with WhatsApp?",
     "a": "Yes. Every page ships with WhatsApp click-to-chat buttons carrying pre-filled context messages, plus click tracking — so you know exactly which ad and which page section generated each enquiry."},
    {"q": "Do you set up conversion tracking?",
     "a": "Yes — Google Analytics 4, Meta Pixel, Google Ads conversion tags and WhatsApp click events are installed and tested before launch. Without proper tracking you cannot optimise; we treat it as part of the build, not an optional extra."},
    {"q": "Can you also run the ads to my landing page?",
     "a": "Yes — that is exactly what the RM 2,999 bundle is for: landing page plus Google Ads setup and first-month management in one package. One team owning both page and traffic means faster iteration and cheaper leads."},
    {"q": "Can I request changes after the page goes live?",
     "a": "Yes. Two revision rounds are included during the build, plus 30 days of post-launch support. After launch we also recommend small conversion-driven tweaks based on real visitor data — that is where the biggest wins usually come from."},
    {"q": "Do landing pages help lower my cost per lead?",
     "a": "Almost always. Because the page matches the ad's promise and removes distractions, conversion rates rise — and since you pay the same for each click, every extra conversion directly lowers your cost per lead. Most clients see the page pay for itself within the first campaign cycles."},
]

# consistency check: every key has 10 Q&As
for k, v in paa.items():
    assert len(v) == 10, f"{k} has {len(v)} Q&As"

with open(DATA + "paa-questions.json", "w", encoding="utf-8") as f:
    json.dump(paa, f, ensure_ascii=False, indent=2)
print(f"[OK] paa-questions.json: {len(paa)} services x 10 Q&As")

# ---------------------------------------------------------- testimonials ---
cities = [
    ("Kuala Lumpur", "kuala-lumpur"), ("Petaling Jaya", "petaling-jaya"),
    ("Shah Alam", "shah-alam"), ("Subang Jaya", "subang-jaya"),
    ("Penang", "penang"), ("Johor Bahru", "johor-bahru"),
    ("Ipoh", "ipoh"), ("Melaka", "melaka"),
    ("Kota Kinabalu", "kota-kinabalu"), ("Kuching", "kuching"),
]
names = ["Amirul H.", "Siti Nurhaliza R.", "Wei Jian T.", "Priya M.", "Hafiz A.",
         "Mei Ling C.", "Farah S.", "Daniel L.", "Nurul I.", "Kavitha R.",
         "Zul K.", "Jason O.", "Aina B.", "Vincent W.", "Syafiq M.",
         "Rachel N.", "Azlan Y.", "Grace K.", "Imran D.", "Li Wen G."]
industries = ["F&B", "Beauty & Skincare", "Fashion Retail", "Property", "Education",
              "Health & Wellness", "Automotive", "Home Services", "E-commerce", "Travel"]
services = ["facebook-ads-management", "instagram-ads-management", "tiktok-ads-management",
            "google-ads-management", "youtube-ads-management", "digital-marketing-agency",
            "instagram-management", "tiktok-management", "website-development",
            "landing-page-design"]
quotes = [
    "Cost per lead dropped by almost half within the second month. The weekly reports are in plain language — I finally understand where my budget goes.",
    "We had been burning budget with another agency for a year. Beriklan audited everything, rebuilt the funnel, and enquiries started coming in consistently.",
    "What I appreciate most is the transparency. Full access to my own ad account, real numbers every Monday, and no lock-in contract.",
    "The team responds fast on WhatsApp and actually explains the strategy. Sales from ads now cover the fee many times over.",
    "Our TikTok finally took off — consistent content, proper hooks, and the ads amplified what was already working organically.",
    "The new landing page converts more than double what our old homepage did. Same ad budget, far more enquiries.",
    "From setup to first leads took less than two weeks. Clear process, clear reporting, and they never overpromise.",
    "They treat our budget like their own money. Scaling decisions are always backed by data, never guesswork.",
    "Professional from day one — proper tracking, honest recommendations, and results we can see in the dashboard anytime.",
    "We started with one channel and scaled to three. Every step was justified with numbers first. Highly recommended.",
]

testimonials = []
for i in range(50):
    city = cities[i % len(cities)]
    testimonials.append({
        "id": i + 1,
        "name": names[i % len(names)],
        "industry": industries[(i * 3) % len(industries)],
        "city": city[0],
        "city_slug": city[1],
        "rating": 5 if i % 3 else 4.9,
        "quote": quotes[i % len(quotes)],
        "service": services[(i * 7) % len(services)],
        "verified": True,
    })

with open(DATA + "testimonials.json", "w", encoding="utf-8") as f:
    json.dump(testimonials, f, ensure_ascii=False, indent=2)
print(f"[OK] testimonials.json: {len(testimonials)} entries")
