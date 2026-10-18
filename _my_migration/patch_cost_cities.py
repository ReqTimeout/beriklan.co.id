#!/usr/bin/env python3
"""F1-7d: Malaysian cities.json + rewrite 5 *-ads-cost/[city].astro templates in English/MYR."""
import io, json

DATA = "/Users/maabook/Desktop/beriklan.my/web/src/data/"
PAGES = "/Users/maabook/Desktop/beriklan.my/web/src/pages/"

CITIES = [
  {"slug":"kuala-lumpur","name":"Kuala Lumpur","alt_names":["KL"],"province":"Federal Territory of Kuala Lumpur","tier":1,"country":"MY","lat":3.1390,"lng":101.6869,"umkm_count":200000,"local_facts":["Malaysia's capital and largest commercial hub","Home to the highest concentration of SMEs and startups in the country","Strong demand across F&B, retail, property and professional services"],"is_international":False},
  {"slug":"petaling-jaya","name":"Petaling Jaya","alt_names":["PJ"],"province":"Selangor","tier":1,"country":"MY","lat":3.1073,"lng":101.6067,"umkm_count":80000,"local_facts":["Major satellite city in the Klang Valley","Dense mix of corporate offices, retail and F&B businesses","Highly competitive digital advertising market"],"is_international":False},
  {"slug":"shah-alam","name":"Shah Alam","alt_names":[],"province":"Selangor","tier":1,"country":"MY","lat":3.0733,"lng":101.5185,"umkm_count":70000,"local_facts":["State capital of Selangor","Strong manufacturing and industrial SME base","Growing e-commerce and services sector"],"is_international":False},
  {"slug":"subang-jaya","name":"Subang Jaya","alt_names":["USJ"],"province":"Selangor","tier":2,"country":"MY","lat":3.0567,"lng":101.5851,"umkm_count":50000,"local_facts":["Large residential and commercial township in the Klang Valley","Young, digitally active population with several universities nearby","Vibrant F&B and lifestyle business scene"],"is_international":False},
  {"slug":"johor-bahru","name":"Johor Bahru","alt_names":["JB"],"province":"Johor","tier":1,"country":"MY","lat":1.4927,"lng":103.7414,"umkm_count":90000,"local_facts":["Southern gateway city bordering Singapore","Cross-border retail, property and services demand","Fast-growing e-commerce and logistics hub"],"is_international":False},
  {"slug":"penang","name":"Penang","alt_names":["George Town","Pulau Pinang"],"province":"Penang","tier":1,"country":"MY","lat":5.4141,"lng":100.3288,"umkm_count":85000,"local_facts":["Major northern commercial and tourism hub","Strong F&B, hospitality and manufacturing sectors","George Town is a UNESCO World Heritage tourist magnet"],"is_international":False},
  {"slug":"ipoh","name":"Ipoh","alt_names":[],"province":"Perak","tier":2,"country":"MY","lat":4.5975,"lng":101.0901,"umkm_count":45000,"local_facts":["Perak's state capital with a growing tourism economy","Famous food scene driving strong F&B business activity","Rising demand for digital marketing among local SMEs"],"is_international":False},
  {"slug":"melaka","name":"Melaka","alt_names":["Malacca"],"province":"Melaka","tier":2,"country":"MY","lat":2.1896,"lng":102.2501,"umkm_count":40000,"local_facts":["UNESCO World Heritage city with heavy tourist traffic","Tourism, hospitality and retail dominate the local economy","Weekend crowds from KL and Singapore boost local businesses"],"is_international":False},
  {"slug":"seremban","name":"Seremban","alt_names":[],"province":"Negeri Sembilan","tier":2,"country":"MY","lat":2.7297,"lng":101.9381,"umkm_count":30000,"local_facts":["State capital of Negeri Sembilan within commuting reach of KL","Growing residential townships expanding the consumer base","Local services and F&B lead SME activity"],"is_international":False},
  {"slug":"kota-kinabalu","name":"Kota Kinabalu","alt_names":["KK"],"province":"Sabah","tier":2,"country":"MY","lat":5.9804,"lng":116.0735,"umkm_count":35000,"local_facts":["Sabah's capital and East Malaysia's tourism gateway","Strong tourism, hospitality and travel services sector","Rapidly growing digital adoption among local businesses"],"is_international":False},
  {"slug":"kuching","name":"Kuching","alt_names":[],"province":"Sarawak","tier":2,"country":"MY","lat":1.5533,"lng":110.3592,"umkm_count":35000,"local_facts":["Sarawak's capital and largest city","Diverse economy spanning tourism, F&B and services","State digital economy initiatives accelerating online adoption"],"is_international":False},
  {"slug":"klang","name":"Klang","alt_names":[],"province":"Selangor","tier":2,"country":"MY","lat":3.0449,"lng":101.4456,"umkm_count":45000,"local_facts":["Home to Port Klang, Malaysia's busiest port","Strong trading, logistics and wholesale business base","Famous Bak Kut Teh food scene supports a dense F&B market"],"is_international":False},
  {"slug":"putrajaya","name":"Putrajaya","alt_names":[],"province":"Federal Territory of Putrajaya","tier":3,"country":"MY","lat":2.9264,"lng":101.6964,"umkm_count":8000,"local_facts":["Malaysia's federal administrative capital","Stable government-employee consumer base","Services and F&B businesses serve a high-income population"],"is_international":False},
  {"slug":"cyberjaya","name":"Cyberjaya","alt_names":[],"province":"Selangor","tier":3,"country":"MY","lat":2.9188,"lng":101.6520,"umkm_count":10000,"local_facts":["Malaysia's tech hub with a high concentration of startups","Digitally savvy workforce and student population","Strong demand for SaaS, edtech and B2B marketing"],"is_international":False},
  {"slug":"kuantan","name":"Kuantan","alt_names":[],"province":"Pahang","tier":3,"country":"MY","lat":3.8077,"lng":103.3260,"umkm_count":25000,"local_facts":["Pahang's state capital on the East Coast","Regional trade and services centre for the East Coast corridor","Growing online retail adoption among local SMEs"],"is_international":False},
]

with io.open(DATA + 'cities.json', 'w', encoding='utf-8') as f:
    json.dump(CITIES, f, ensure_ascii=False, indent=2)
print('WROTE cities.json (%d cities)' % len(CITIES))

TEMPLATE = '''---
import Layout from '../../layouts/Layout.astro';
import Navbar from '../../components/Navbar.svelte';
import StickyCTA from '../../components/StickyCTA.svelte';
import PricingCards from '../../components/PricingCards.svelte';
import FaqAccordion from '../../components/FaqAccordion.svelte';
import Footer from '../../components/Footer.svelte';

import cities from '../../data/cities.json';
import services from '../../data/services.json';

export function getStaticPaths() {
    const malaysianCities = cities.filter(c => !c.is_international);
    return malaysianCities.map(city => ({
        params: { city: city.slug },
        props: { city },
    }));
}

const service = services.find(s => s.slug === '@@SLUG@@');

const { city } = Astro.props;
const tiers = service?.tiers || [];
const faqs = service?.faqs?.slice(0, 4) || [];

const cityName = city.name;
const slug = city.slug;
const title = `@@LABEL@@ Cost in ${cityName} — Pricing & Packages 2026 | Beriklan`;
const description = `See @@LABEL@@ management pricing in ${cityName}, Malaysia. From @@START@@ per 30 days. Certified team, weekly reports. Consultation via WhatsApp.`;
const canonical = `https://beriklan.my/@@COSTDIR@@/${slug}/`;
const waLink = `https://wa.me/62811919328?text=Hi%20Beriklan%2C%20I%27m%20interested%20in%20your%20@@WAENC@@%20packages%20in%20${encodeURIComponent(cityName)}.%20Please%20share%20more%20details.`;
---

<Layout
    title={title}
    description={description}
    canonical={canonical}
    breadcrumb={[
        { name: "Home", url: "https://beriklan.my/" },
        { name: "@@LABEL@@ Cost", url: "https://beriklan.my/@@COSTDIR@@/" },
        { name: cityName, url: canonical }
    ]}
    service={{
        name: `@@LABEL@@ Services in ${cityName}`,
        description: `Professional @@LABEL@@ management in ${cityName}, Malaysia. Certified team. Weekly reports, full account access.`,
        url: canonical,
        priceRange: "@@START@@ - @@TOP@@",
        serviceType: "@@LABEL@@",
        areaServed: cityName,
        provider: { name: "Beriklan.my", url: "https://beriklan.my" }
    }}
>
    <Navbar client:only="svelte" />
    <StickyCTA client:only="svelte" />

    <header class="relative pt-28 md:pt-44 pb-16 md:pb-20 overflow-hidden bg-gradient-to-br from-white via-soft to-beige">
        <div class="container mx-auto px-6 relative z-10 text-center max-w-3xl mx-auto">
            <div class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-full text-xs font-semibold tracking-wider uppercase shadow-sm mb-5">
                <span class="relative flex h-2 w-2">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
                </span>
                @@LABEL@@ Cost · {cityName}
            </div>
            <h1 class="font-display font-extrabold text-4xl md:text-5xl lg:text-[2.6rem] xl:text-[2.9rem] text-ink leading-[1.05] tracking-tight">
                @@LABEL@@ Cost in {cityName}
            </h1>
            <p class="mt-5 text-base md:text-lg text-muted leading-relaxed max-w-2xl mx-auto">
                Check @@LABEL@@ management pricing and packages in {cityName}. Starting from <strong class="text-ink">@@START@@</strong> per 30 days for the @@STARTTIER@@ package — including campaign setup, optimisation and weekly reports.
            </p>
            <div class="mt-8 flex flex-col sm:flex-row gap-3 justify-center">
                <a href={waLink} target="_blank" rel="noopener" class="inline-flex items-center justify-center gap-2 bg-ink text-white px-7 py-4 rounded-full font-bold shadow-lg hover:shadow-pop transition-all">
                    Consult via WhatsApp
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
                </a>
                <a href="#pricing" class="inline-flex items-center justify-center gap-2 px-7 py-4 rounded-full font-bold border border-gray-200 bg-white hover:border-ink transition-all">
                    View Packages
                </a>
            </div>
        </div>
    </header>

    <section id="pricing" class="py-20 md:py-28 bg-gradient-to-br from-soft via-white to-beige">
        <div class="container mx-auto px-6">
            <div class="text-center max-w-2xl mx-auto mb-12">
                <h2 class="font-display font-extrabold text-3xl md:text-5xl text-ink leading-[1.1] tracking-tight">
                    @@LABEL@@ Packages in {cityName}
                </h2>
                <p class="mt-4 text-muted max-w-xl mx-auto">Campaign management fees. Your ad spend is paid directly to the platform — no markup.</p>
            </div>
            <PricingCards tiers={tiers} pageSlug="@@LABEL@@" highlightIndex={tiers.findIndex(t => t.highlight)} client:only="svelte" />
        </div>
    </section>

    <section class="py-20 md:py-28 bg-white">
        <div class="container mx-auto px-6 max-w-3xl">
            <h2 class="font-display font-extrabold text-2xl md:text-3xl text-ink mb-6">@@LABEL@@ Cost in {cityName}</h2>
            <div class="space-y-4 text-muted text-base leading-relaxed">
                <p>@@LABEL@@ management fees in {cityName} from Beriklan start at <strong class="text-ink">@@START@@ per 30 days</strong> for the @@STARTTIER@@ package, up to @@TOP@@ for the top-tier package. These figures are the management fee — ad spend is paid separately, straight to the platform, by the client.</p>
                <p>For businesses in {cityName}, we offer a measurable approach with <strong class="text-ink">precise targeting</strong>, creative tailored to your local audience, and weekly reports written in plain language.</p>
            </div>
            <div class="mt-8 p-6 bg-beige rounded-2xl">
                <h3 class="font-display font-bold text-lg text-ink mb-2">Contact Us</h3>
                <p class="text-sm text-muted mb-4">Discuss your business's @@LABEL@@ needs in {cityName} with our team.</p>
                <a href={waLink} target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-ink text-white px-6 py-3 rounded-full font-bold text-sm hover:bg-primary-2 transition">
                    Start a WhatsApp Consultation →
                </a>
            </div>
        </div>
    </section>

    <section class="py-20 md:py-28 bg-soft">
        <div class="container mx-auto px-6 max-w-2xl">
            <h2 class="font-display font-extrabold text-2xl md:text-3xl text-ink mb-8 text-center">@@LABEL@@ Pricing FAQs</h2>
            <FaqAccordion items={faqs} client:visible />
        </div>
    </section>

    <section class="py-20 md:py-28 bg-gradient-to-br from-ink via-primary-2 to-ink text-white text-center">
        <div class="container mx-auto px-6 max-w-2xl">
            <h2 class="font-display font-extrabold text-3xl md:text-5xl leading-[1.1] tracking-tight mb-4">
                Ready to launch @@LABEL@@<br/>
                <span class="text-accent">in {cityName}?</span>
            </h2>
            <p class="text-white/60 text-base mb-8">Our team supports you from research and setup through to campaign optimisation.</p>
            <a href={waLink} target="_blank" rel="noopener" class="inline-flex items-center justify-center gap-2 bg-accent text-ink px-8 py-4 rounded-full font-bold shadow-lg hover:shadow-pop transition-all">
                Get a Consultation Now
            </a>
        </div>
    </section>

    <section class="py-16 md:py-20 bg-soft">
        <div class="container mx-auto px-6 max-w-4xl">
            <h2 class="font-display font-extrabold text-2xl md:text-3xl text-ink mb-6">Learn More</h2>
            <div class="grid md:grid-cols-3 gap-5">
                <a href="/@@SLUG@@/" class="block bg-white rounded-xl p-5 border border-gray-200 hover:border-accent hover:shadow-soft transition">
                    <span class="text-xs font-bold uppercase tracking-wider text-accent">Service</span>
                    <h3 class="font-bold text-ink mt-2">@@LABEL@@ Services</h3>
                    <p class="text-sm text-muted mt-1">Full service details: targeting, creative and optimisation.</p>
                </a>
                <a href="/blog/" class="block bg-white rounded-xl p-5 border border-gray-200 hover:border-accent hover:shadow-soft transition">
                    <span class="text-xs font-bold uppercase tracking-wider text-accent">Blog</span>
                    <h3 class="font-bold text-ink mt-2">Digital Marketing Guides</h3>
                    <p class="text-sm text-muted mt-1">Strategy articles, tips and case studies from the Beriklan team.</p>
                </a>
                <a href="/research/malaysia-digital-advertising-report-2026/" class="block bg-white rounded-xl p-5 border border-gray-200 hover:border-accent hover:shadow-soft transition">
                    <span class="text-xs font-bold uppercase tracking-wider text-accent">Research</span>
                    <h3 class="font-bold text-ink mt-2">Malaysia Digital Advertising Report 2026</h3>
                    <p class="text-sm text-muted mt-1">Market data, platform landscape and the trends shaping 2026.</p>
                </a>
            </div>
            <div class="mt-8 p-5 bg-white rounded-xl border border-gray-200">
                <p class="text-xs font-bold uppercase tracking-wider text-muted mb-3">External References</p>
                <div class="flex flex-wrap gap-x-6 gap-y-2 text-sm">
@@EXT@@
                </div>
            </div>
        </div>
    </section>

    <Footer />
</Layout>
'''

PLATFORMS = [
  {
    'dir': 'facebook-ads-cost', 'label': 'Facebook Ads', 'slug': 'facebook-ads-management',
    'start': 'RM 990', 'top': 'RM 2,990', 'starttier': 'Starter', 'waenc': 'Facebook%20Ads',
    'ext': '                    <a href="https://www.facebook.com/business/help" target="_blank" rel="noopener nofollow" class="text-accent hover:underline">Facebook Business Help Center</a>\n                    <a href="https://business.meta.com/" target="_blank" rel="noopener nofollow" class="text-accent hover:underline">Meta Business Suite</a>',
  },
  {
    'dir': 'instagram-ads-cost', 'label': 'Instagram Ads', 'slug': 'instagram-ads-management',
    'start': 'RM 990', 'top': 'RM 2,990', 'starttier': 'Starter', 'waenc': 'Instagram%20Ads',
    'ext': '                    <a href="https://business.instagram.com/advertising" target="_blank" rel="noopener nofollow" class="text-accent hover:underline">Instagram for Business</a>\n                    <a href="https://business.meta.com/" target="_blank" rel="noopener nofollow" class="text-accent hover:underline">Meta Business Suite</a>',
  },
  {
    'dir': 'tiktok-ads-cost', 'label': 'TikTok Ads', 'slug': 'tiktok-ads-management',
    'start': 'RM 790', 'top': 'RM 1,990', 'starttier': 'Basic', 'waenc': 'TikTok%20Ads',
    'ext': '                    <a href="https://ads.tiktok.com/" target="_blank" rel="noopener nofollow" class="text-accent hover:underline">TikTok Ads Manager</a>\n                    <a href="https://ads.tiktok.com/help/" target="_blank" rel="noopener nofollow" class="text-accent hover:underline">TikTok Business Help Center</a>',
  },
  {
    'dir': 'google-ads-cost', 'label': 'Google Ads', 'slug': 'google-ads-management',
    'start': 'RM 990', 'top': 'RM 2,790', 'starttier': 'Basic', 'waenc': 'Google%20Ads',
    'ext': '                    <a href="https://support.google.com/google-ads/" target="_blank" rel="noopener nofollow" class="text-accent hover:underline">Google Ads Help</a>\n                    <a href="https://ads.google.com/" target="_blank" rel="noopener nofollow" class="text-accent hover:underline">Google Ads</a>',
  },
  {
    'dir': 'youtube-ads-cost', 'label': 'YouTube Ads', 'slug': 'youtube-ads-management',
    'start': 'RM 890', 'top': 'RM 2,490', 'starttier': 'Basic', 'waenc': 'YouTube%20Ads',
    'ext': '                    <a href="https://www.youtube.com/ads/" target="_blank" rel="noopener nofollow" class="text-accent hover:underline">YouTube Advertising</a>\n                    <a href="https://support.google.com/google-ads/" target="_blank" rel="noopener nofollow" class="text-accent hover:underline">Google Ads Help</a>',
  },
]

for p in PLATFORMS:
    out = TEMPLATE
    for token, val in [('@@LABEL@@', p['label']), ('@@SLUG@@', p['slug']), ('@@COSTDIR@@', p['dir']),
                       ('@@START@@', p['start']), ('@@TOP@@', p['top']), ('@@STARTTIER@@', p['starttier']),
                       ('@@WAENC@@', p['waenc']), ('@@EXT@@', p['ext'])]:
        out = out.replace(token, val)
    path = PAGES + p['dir'] + '/[city].astro'
    with io.open(path, 'w', encoding='utf-8') as f:
        f.write(out)
    print('WROTE %s' % path)
print('DONE cost pages')
