#!/usr/bin/env python3
"""
gen_city_service_pages.py — create 10 dynamic `{service}/[city].astro` routes
for Beriklan.my. Each route pre-renders one page per Malaysian city (25) via
getStaticPaths, embedding the SEO body from CityContentBlock + pricing + FAQ.

Total pages produced at build: 10 services x 25 cities = 250.

Idempotent: overwrites the generated [city].astro files each run.
"""
import os

ROOT = os.path.expanduser("~/Desktop/beriklan.my")
PAGES = os.path.join(ROOT, "web/src/pages")

# slug -> (label, pageSlug, priceRange, serviceType, eyebrowCtx)
META = {
    "facebook-ads-management": ("Facebook Ads Management", "Facebook Ads", "RM 990 - RM 2,990", "Facebook Ads", "Meta Business Partner"),
    "instagram-ads-management": ("Instagram Ads Management", "Instagram Ads", "RM 990 - RM 2,990", "Instagram Ads", "Meta Business Partner"),
    "tiktok-ads-management": ("TikTok Ads Management", "TikTok Ads", "RM 790 - RM 1,990", "TikTok Ads", "TikTok Marketing"),
    "google-ads-management": ("Google Ads Management", "Google Ads", "RM 990 - RM 2,790", "Google Ads", "Google Partner"),
    "youtube-ads-management": ("YouTube Ads Management", "YouTube Ads", "RM 890 - RM 2,490", "YouTube Ads", "Google Partner"),
    "instagram-management": ("Instagram Management", "Instagram Management", "RM 1,290 - Custom", "Social Media Management", "Content & Community"),
    "tiktok-management": ("TikTok Management", "TikTok Management", "RM 990 - RM 2,490", "Social Media Management", "Content & Community"),
    "website-development": ("Website Development", "Website", "RM 1,499 - RM 6,999", "Web Development", "Custom & CMS"),
    "landing-page-design": ("Landing Page Design", "Landing Page", "RM 1,299 - Custom", "Landing Page Design", "Landing Page + Google Ads"),
    "digital-marketing-agency": ("Digital Marketing", "Digital Marketing", "Custom", "Digital Marketing", "Multi-Channel"),
}

TEMPLATE = r'''---
import Layout from '../../layouts/Layout.astro';
import Navbar from '../../components/Navbar.svelte';
import StickyCTA from '../../components/StickyCTA.svelte';
import Footer from '../../components/Footer.svelte';
import PricingCards from '../../components/PricingCards.svelte';
import FaqAccordion from '../../components/FaqAccordion.svelte';
import CityContentBlock from '../../components/CityContentBlock.astro';
import cities from '../../data/cities.json';
import services from '../../data/services.json';

const SERVICE_SLUG = '__SLUG__';
const SERVICE_LABEL = '__LABEL__';
const PAGE_SLUG = '__PAGESLUG__';
const PRICE_RANGE = '__PRICERANGE__';
const SERVICE_TYPE = '__SERVICETYPE__';
const EYEBROW_CTX = '__EYEBROW__';

export function getStaticPaths() {
    const malaysianCities = cities.filter(c => !c.is_international);
    return malaysianCities.map(city => ({ params: { city: city.slug }, props: { city } }));
}

const service = services.find(s => s.slug === SERVICE_SLUG);
const { city } = Astro.props;
const tiers = service?.tiers || [];
const faqs = (service?.faqs || []).slice(0, 5);
const highlightIndex = tiers.findIndex(t => t.highlight);

const cityName = city.name;
const state = city.province || 'Malaysia';
const slug = city.slug;
const route = `${SERVICE_SLUG}/${slug}/`;
const canonical = `https://beriklan.my/${route}`;
const title = `${SERVICE_LABEL} in ${cityName} — Certified Team | Beriklan`;
const description = `Professional ${SERVICE_LABEL} for businesses in ${cityName}, Malaysia. Certified team since 2016, weekly reports and a real-time dashboard. Contact us.`;
const waLink = `https://wa.me/62811919328?text=${encodeURIComponent(`Hi Beriklan, I'm interested in ${SERVICE_LABEL} for my business in ${cityName}. Please share more details.`)}`;
---

<Layout
    title={title}
    description={description}
    canonical={canonical}
    breadcrumb={[
        { name: "Home", url: "https://beriklan.my/" },
        { name: SERVICE_LABEL, url: `https://beriklan.my/${SERVICE_SLUG}/` },
        { name: cityName, url: canonical }
    ]}
    service={{
        name: `${SERVICE_LABEL} in ${cityName}`,
        description: `Professional ${SERVICE_LABEL} in ${cityName}, ${state}. Certified team, weekly reports and full account access.`,
        url: canonical,
        priceRange: PRICE_RANGE,
        serviceType: SERVICE_TYPE,
        areaServed: cityName,
        provider: { name: "Beriklan.my", url: "https://beriklan.my" }
    }}
>
    <Navbar client:only="svelte" />
    <StickyCTA client:only="svelte" />

    <!-- ====================== HERO ====================== -->
    <header class="relative pt-28 md:pt-44 pb-14 md:pb-16 overflow-hidden bg-gradient-to-br from-white via-soft to-beige">
        <div class="container mx-auto px-6 relative z-10 text-center max-w-3xl">
            <div class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-full text-xs font-semibold tracking-wider uppercase shadow-sm mb-5">
                <span class="relative flex h-2 w-2">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
                </span>
                {SERVICE_LABEL} · {cityName}
            </div>
            <h1 class="font-display font-extrabold text-4xl md:text-5xl lg:text-[2.6rem] xl:text-[2.9rem] text-ink leading-[1.05] tracking-tight">
                {SERVICE_LABEL} in <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-2 to-accent">{cityName}</span>
            </h1>
            <p class="mt-5 text-base md:text-lg text-muted leading-relaxed max-w-2xl mx-auto">
                Measurable {SERVICE_LABEL.toLowerCase()} for businesses in {cityName}. {EYEBROW_CTX} · certified team · weekly reports written in plain language. We research your local audience, execute with intent and optimise every week.
            </p>
            <div class="mt-8 flex flex-col sm:flex-row gap-3 justify-center">
                <a href={waLink} target="_blank" rel="noopener" class="inline-flex items-center justify-center gap-2 bg-ink text-white px-7 py-4 rounded-full font-bold shadow-lg hover:shadow-pop transition-all">
                    Chat on WhatsApp
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
                </a>
                {tiers.length > 0 && (
                    <a href="#pricing" class="inline-flex items-center justify-center gap-2 px-7 py-4 rounded-full font-bold border border-gray-200 bg-white hover:border-ink transition-all">
                        View Packages
                    </a>
                )}
            </div>
        </div>
    </header>

    <!-- ====================== SEO CITY CONTENT ====================== -->
    <section class="bg-white pb-8">
        <CityContentBlock route={route} cityName={cityName} serviceName={SERVICE_LABEL} />
    </section>

    <!-- ====================== PRICING ====================== -->
    {tiers.length > 0 && (
        <section id="pricing" class="py-20 md:py-28 bg-gradient-to-br from-soft via-white to-beige">
            <div class="container mx-auto px-6">
                <div class="text-center max-w-2xl mx-auto mb-12">
                    <h2 class="font-display font-extrabold text-3xl md:text-5xl text-ink leading-[1.1] tracking-tight">
                        {SERVICE_LABEL} Packages in {cityName}
                    </h2>
                    <p class="mt-4 text-muted max-w-xl mx-auto">Transparent management fees. Where applicable, your ad spend is paid directly to the platform — no markup.</p>
                </div>
                <PricingCards tiers={tiers} pageSlug={PAGE_SLUG} highlightIndex={highlightIndex} client:only="svelte" />
            </div>
        </section>
    )}

    <!-- ====================== FAQ ====================== -->
    {faqs.length > 0 && (
        <section class="py-20 md:py-28 bg-soft">
            <div class="container mx-auto px-6 max-w-2xl">
                <h2 class="font-display font-extrabold text-2xl md:text-3xl text-ink mb-8 text-center">{SERVICE_LABEL} FAQs</h2>
                <FaqAccordion items={faqs} client:visible />
            </div>
        </section>
    )}

    <!-- ====================== FINAL CTA ====================== -->
    <section class="py-20 md:py-28 bg-gradient-to-br from-ink via-primary-2 to-ink text-white text-center">
        <div class="container mx-auto px-6 max-w-2xl">
            <h2 class="font-display font-extrabold text-3xl md:text-5xl leading-[1.1] tracking-tight mb-4">
                Ready to grow<br/>
                <span class="text-accent">in {cityName}?</span>
            </h2>
            <p class="text-white/60 text-base mb-8">Our team supports you from research and setup through to ongoing optimisation.</p>
            <a href={waLink} target="_blank" rel="noopener" class="inline-flex items-center justify-center gap-2 bg-accent text-ink px-8 py-4 rounded-full font-bold shadow-lg hover:shadow-pop transition-all">
                Get a Contact Us
            </a>
        </div>
    </section>

    <Footer />
</Layout>
'''


def main():
    written = 0
    for slug, (label, page_slug, price_range, service_type, eyebrow) in META.items():
        out_dir = os.path.join(PAGES, slug)
        os.makedirs(out_dir, exist_ok=True)
        out = os.path.join(out_dir, "[city].astro")
        body = (
            TEMPLATE
            .replace("__SLUG__", slug)
            .replace("__LABEL__", label)
            .replace("__PAGESLUG__", page_slug)
            .replace("__PRICERANGE__", price_range)
            .replace("__SERVICETYPE__", service_type)
            .replace("__EYEBROW__", eyebrow)
        )
        with open(out, "w", encoding="utf-8") as f:
            f.write(body)
        written += 1
        print(f"  wrote {slug}/[city].astro")
    print(f"Done. {written} dynamic routes -> {written * 25} pages at build.")


if __name__ == "__main__":
    main()
