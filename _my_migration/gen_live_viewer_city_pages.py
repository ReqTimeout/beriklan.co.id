#!/usr/bin/env python3
"""
gen_live_viewer_city_pages.py — F2-4: per-city live-viewer pages for Beriklan.my.

Creates `{platform}-live-viewers/[city].astro` dynamic routes for the 5 live
platforms, pre-rendering one page per TIER-1 Malaysian city (from cities.json:
Kuala Lumpur, Petaling Jaya, Shah Alam, Johor Bahru, Penang) = 25 pages.

Pricing/FAQ parity is guaranteed by extracting the `const tiers = [...]` and
`const faqs = [...]` blocks VERBATIM from each existing platform page
(web/src/pages/{platform}-live-viewers.astro) — no duplicated price tables.

City copy is truthful: only uses cities.json data (name, state, sme count via
`umkm_count`, English `local_facts`) rendered inline in the template.

Idempotent: overwrites the generated [city].astro files each run.
"""
import os
import re

ROOT = os.path.expanduser("~/Desktop/beriklan.my")
PAGES = os.path.join(ROOT, "web/src/pages")

# platform slug-prefix -> (label, priceRange, highlightIndex)
PLATFORMS = {
    "tiktok": ("TikTok", "RM 5 - RM 75"),
    "instagram": ("Instagram", "RM 5 - RM 75"),
    "shopee": ("Shopee", "RM 7 - RM 99"),
    "youtube": ("YouTube", "RM 5 - RM 75"),
    "twitch": ("Twitch", "RM 5 - RM 75"),
}


def extract_block(src: str, marker: str) -> str:
    """Return the full `const X = [ ... ];` block starting at `marker`."""
    start = src.index(marker)
    end = src.index("\n];", start)
    return src[start:end + len("\n];")]


TEMPLATE = r'''---
import Layout from '../../layouts/Layout.astro';
import Navbar from '../../components/Navbar.svelte';
import StickyCTA from '../../components/StickyCTA.svelte';
import Footer from '../../components/Footer.svelte';
import PricingCards from '../../components/PricingCards.svelte';
import FaqAccordion from '../../components/FaqAccordion.svelte';
import cities from '../../data/cities.json';

const PLATFORM = '__PLATFORM__';
const SERVICE_SLUG = '__SERVICE_SLUG__';
const PRICE_RANGE = '__PRICERANGE__';

__TIERS_BLOCK__

__FAQS_BLOCK__

export function getStaticPaths() {
    const tier1 = cities.filter(c => !c.is_international && c.tier === 1);
    return tier1.map(city => ({ params: { city: city.slug }, props: { city } }));
}

const { city } = Astro.props;
const cityName = city.name;
const state = city.province || 'Malaysia';
const sme = city.umkm_count || 0;
const facts = (city.local_facts || []).join('. ');
const otherCities = cities.filter(c => !c.is_international && c.tier === 1 && c.slug !== city.slug);

const canonical = `https://beriklan.my/${SERVICE_SLUG}/${city.slug}/`;
const title = `${PLATFORM} Live Viewers in ${cityName} — Real Viewers | Beriklan`;
const description = `Boost your ${PLATFORM} live sessions in ${cityName}, Malaysia with real active viewers. Gradual join, no bots, WhatsApp support. Packages from ${PRICE_RANGE.split(' - ')[0]} per session.`;
const waLink = `https://wa.me/62811919328?text=${encodeURIComponent(`Hi Beriklan, I'm interested in ${PLATFORM} live viewers for my live sessions in ${cityName}. Please share packages and pricing.`)}`;
---

<Layout
    title={title}
    description={description}
    canonical={canonical}
    breadcrumb={[
        { name: "Home", url: "https://beriklan.my/" },
        { name: `${PLATFORM} Live Viewers`, url: `https://beriklan.my/${SERVICE_SLUG}/` },
        { name: cityName, url: canonical }
    ]}
    faq={faqs.map(f => ({ question: f.q, answer: f.a }))}
    service={{
        name: `${PLATFORM} Live Viewers in ${cityName}`,
        description: `Real active viewers for ${PLATFORM} live sessions in ${cityName}, ${state}. Gradual join, no bots, per-session pricing.`,
        url: canonical,
        priceRange: PRICE_RANGE,
        serviceType: `${PLATFORM} Live Viewers`,
        areaServed: cityName,
        provider: { name: "Beriklan.my", url: "https://beriklan.my" }
    }}
>
    <Navbar client:only="svelte" />
    <StickyCTA client:only="svelte" />

    <!-- ====================== HERO ====================== -->
    <header class="relative pt-28 md:pt-44 pb-14 md:pb-16 overflow-hidden bg-gradient-to-br from-white via-soft to-beige">
        <div class="container mx-auto px-6 relative z-10 text-center max-w-3xl">
            <nav class="text-xs text-muted mb-6 flex items-center justify-center gap-1.5">
                <a href="/" class="hover:text-accent transition">Home</a>
                <span class="text-muted/40">›</span>
                <a href={`/${SERVICE_SLUG}/`} class="hover:text-accent transition">{PLATFORM} Live Viewers</a>
                <span class="text-muted/40">›</span>
                <span class="text-ink font-semibold">{cityName}</span>
            </nav>
            <div class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-full text-xs font-semibold tracking-wider uppercase shadow-sm mb-5">
                <span class="relative flex h-2 w-2">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-green"></span>
                </span>
                {PLATFORM} Live Viewers · {cityName}
            </div>
            <h1 class="font-display font-extrabold text-4xl md:text-5xl lg:text-[2.6rem] xl:text-[2.9rem] text-ink leading-[1.05] tracking-tight">
                {PLATFORM} Live Viewers in <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-2 to-accent">{cityName}</span>
            </h1>
            <p class="mt-5 text-base md:text-lg text-muted leading-relaxed max-w-2xl mx-auto">
                Real active viewers joining gradually during your {PLATFORM} live sessions — so the algorithm notices you early and pushes your live to a wider {cityName} audience. No bots, per-session pricing, WhatsApp support.
            </p>
            <div class="mt-8 flex flex-col sm:flex-row gap-3 justify-center">
                <a href={waLink} target="_blank" rel="noopener" class="inline-flex items-center justify-center gap-2 bg-ink text-white px-7 py-4 rounded-full font-bold shadow-lg hover:shadow-pop transition-all">
                    Chat on WhatsApp
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
                </a>
                <a href="#pricing" class="inline-flex items-center justify-center gap-2 px-7 py-4 rounded-full font-bold border border-gray-200 bg-white hover:border-ink transition-all">
                    View Packages
                </a>
            </div>
        </div>
    </header>

    <!-- ====================== LOCAL CONTEXT ====================== -->
    <section class="py-14 md:py-20 bg-white">
        <div class="container mx-auto px-6 max-w-3xl">
            <h2 class="font-display font-extrabold text-2xl md:text-3xl text-ink mb-5">
                Why Live Selling Works in {cityName}
            </h2>
            <p class="text-base md:text-lg text-muted leading-relaxed mb-4">
                {cityName}, {state}, {sme > 0 ? `is home to an estimated ${sme.toLocaleString('en-MY')} SMEs` : 'has an active SME ecosystem'}.
                {facts && ` ${facts}.`}
            </p>
            <p class="text-base md:text-lg text-muted leading-relaxed">
                For sellers and creators in {cityName}, the first minutes of a {PLATFORM} live decide how far the platform distributes it. A live that starts with active viewers signals demand to the algorithm — our real viewers join gradually so growth looks natural, and the boost is priced per session, not a monthly lock-in.
            </p>
            <ul class="mt-6 space-y-3">
                <li class="flex items-start gap-3 text-muted"><span class="mt-1 w-5 h-5 shrink-0 rounded-full bg-green/10 text-green flex items-center justify-center text-xs font-bold">✓</span> Real accounts, no bots — zero risk to your {PLATFORM} account</li>
                <li class="flex items-start gap-3 text-muted"><span class="mt-1 w-5 h-5 shrink-0 rounded-full bg-green/10 text-green flex items-center justify-center text-xs font-bold">✓</span> Gradual join over 5–15 minutes so the pattern looks organic</li>
                <li class="flex items-start gap-3 text-muted"><span class="mt-1 w-5 h-5 shrink-0 rounded-full bg-green/10 text-green flex items-center justify-center text-xs font-bold">✓</span> Schedule via WhatsApp — we go live when you go live</li>
            </ul>
        </div>
    </section>

    <!-- ====================== PRICING ====================== -->
    <section id="pricing" class="py-20 md:py-28 bg-gradient-to-br from-soft via-white to-beige">
        <div class="container mx-auto px-6">
            <div class="text-center max-w-2xl mx-auto mb-12">
                <h2 class="font-display font-extrabold text-3xl md:text-5xl text-ink leading-[1.1] tracking-tight">
                    {PLATFORM} Live Viewer Packages in {cityName}
                </h2>
                <p class="mt-4 text-muted max-w-xl mx-auto">Per-session pricing. Pick a package that matches your live schedule — no monthly commitment.</p>
            </div>
            <PricingCards tiers={tiers} pageSlug={`${PLATFORM} Live Viewers`} highlightIndex={1} columns={3} client:only="svelte" />
        </div>
    </section>

    <!-- ====================== FAQ ====================== -->
    <section class="py-20 md:py-28 bg-soft">
        <div class="container mx-auto px-6 max-w-2xl">
            <h2 class="font-display font-extrabold text-2xl md:text-3xl text-ink mb-8 text-center">{PLATFORM} Live Viewers FAQs</h2>
            <FaqAccordion items={faqs} client:visible />
        </div>
    </section>

    <!-- ====================== OTHER CITIES + PLATFORMS ====================== -->
    <section class="py-14 md:py-20 bg-white">
        <div class="container mx-auto px-6 max-w-4xl">
            <h2 class="font-display font-bold text-xl md:text-2xl text-ink mb-6 text-center">{PLATFORM} Live Viewers in Other Cities</h2>
            <div class="flex flex-wrap justify-center gap-3 mb-10">
                {otherCities.map((c) => (
                    <a href={`/${SERVICE_SLUG}/${c.slug}/`} class="px-4 py-2.5 bg-white border border-gray-100 rounded-xl hover:border-accent/30 hover:shadow-sm transition text-sm font-semibold text-ink hover:text-accent">
                        {c.name}
                    </a>
                ))}
                <a href={`/${SERVICE_SLUG}/`} class="px-4 py-2.5 bg-soft border border-gray-100 rounded-xl hover:border-accent/30 transition text-sm font-semibold text-muted hover:text-accent">
                    All Malaysia →
                </a>
            </div>
            <h2 class="font-display font-bold text-xl md:text-2xl text-ink mb-6 text-center">Other Platforms in {cityName}</h2>
            <div class="flex flex-wrap justify-center gap-3">
                __OTHER_PLATFORM_LINKS__
                <a href="/live-stream-viewers/" class="px-4 py-2.5 bg-soft border border-gray-100 rounded-xl hover:border-accent/30 transition text-sm font-semibold text-muted hover:text-accent">
                    All Platforms →
                </a>
            </div>
        </div>
    </section>

    <!-- ====================== FINAL CTA ====================== -->
    <section class="py-20 md:py-28 bg-gradient-to-br from-ink via-primary-2 to-ink text-white text-center">
        <div class="container mx-auto px-6 max-w-2xl">
            <h2 class="font-display font-extrabold text-3xl md:text-5xl leading-[1.1] tracking-tight mb-4">
                Going live<br/>
                <span class="text-accent">in {cityName}?</span>
            </h2>
            <p class="text-white/60 text-base mb-8">Tell us your live schedule on WhatsApp and we'll have viewers ready when you start.</p>
            <a href={waLink} target="_blank" rel="noopener" class="inline-flex items-center justify-center gap-2 bg-accent text-ink px-8 py-4 rounded-full font-bold shadow-lg hover:shadow-pop transition-all">
                Book Viewers for Your Next Live
            </a>
        </div>
    </section>

    <Footer />
</Layout>
'''


def main():
    written = 0
    for platform, (label, price_range) in PLATFORMS.items():
        service_slug = f"{platform}-live-viewers"
        src_path = os.path.join(PAGES, f"{service_slug}.astro")
        src = open(src_path, encoding="utf-8").read()
        tiers_block = extract_block(src, "const tiers = [")
        faqs_block = extract_block(src, "const faqs = [")

        other_links = "\n                ".join(
            f'<a href={{`/{p}-live-viewers/${{city.slug}}/`}} class="px-4 py-2.5 bg-white border border-gray-100 rounded-xl hover:border-accent/30 hover:shadow-sm transition text-sm font-semibold text-ink hover:text-accent">{pl} Live Viewers</a>'
            for p, (pl, _pr) in PLATFORMS.items() if p != platform
        )

        body = (
            TEMPLATE
            .replace("__PLATFORM__", label)
            .replace("__SERVICE_SLUG__", service_slug)
            .replace("__PRICERANGE__", price_range)
            .replace("__TIERS_BLOCK__", tiers_block)
            .replace("__FAQS_BLOCK__", faqs_block)
            .replace("__OTHER_PLATFORM_LINKS__", other_links)
        )

        out_dir = os.path.join(PAGES, service_slug)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "[city].astro"), "w", encoding="utf-8") as f:
            f.write(body)
        written += 1
        print(f"  wrote {service_slug}/[city].astro")
    print(f"Done. {written} dynamic routes -> {written * 5} tier-1 city pages at build.")


if __name__ == "__main__":
    main()
