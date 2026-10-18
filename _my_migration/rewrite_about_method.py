#!/usr/bin/env python3
"""F1-7c: full English rewrite of about-us.astro and methodology.astro."""
import io

PAGES = "/Users/maabook/Desktop/beriklan.my/web/src/pages/"

ABOUT = '''---
import Layout from '../layouts/Layout.astro';
import Navbar from '../components/Navbar.svelte';
import Footer from '../components/Footer.svelte';
import StickyCTA from '../components/StickyCTA.svelte';
import { MapPin, Phone, Mail, MessageCircle, Clock, Award, Users, Calendar, Sparkles } from 'lucide-svelte';

const waLink = "https://wa.me/62811919328?text=Hi%20Beriklan%2C%20I%27d%20like%20to%20get%20to%20know%20the%20team%20and%20learn%20more%20about%20Beriklan.";
const phoneLink = "tel:+62811919328";
const mailLink = "mailto:info@beriklan.my?subject=Digital%20Marketing%20Consultation";

const schemaOrg = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Beriklan Digital Agency",
    "url": "https://beriklan.my/",
    "logo": "https://beriklan.my/logoweb.webp",
    "foundingDate": "2016-01-01",
    "founders": [
        { "@type": "Person", "name": "Beriklan Team" }
    ],
    "contactPoint": {
        "@type": "ContactPoint",
        "telephone": "+62-81-1919-328",
        "contactType": "customer service",
        "areaServed": "MY",
        "availableLanguage": ["English", "Malay", "Indonesian"]
    },
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "Jl. Arcamanik Endah No.76",
        "addressLocality": "Bandung",
        "postalCode": "40195",
        "addressCountry": "ID"
    },
    "sameAs": [
        "https://www.facebook.com/beriklan",
        "https://www.instagram.com/beriklan.my",
        "https://www.linkedin.com/company/beriklan"
    ],
    "award": ["Meta Business Partner", "Google Partner", "TikTok Marketing Partner"]
};

const schemaPerson = {
    "@context": "https://schema.org",
    "@type": "Person",
    "name": "Beriklan Team",
    "jobTitle": "Performance Marketing Lead",
    "worksFor": { "@type": "Organization", "name": "Beriklan Digital Agency" },
    "url": "https://beriklan.my/about-us/"
};
---

<Layout
    title="About Beriklan.my — Performance Marketing Team Since 2016 | Beriklan"
    description="Beriklan Digital Agency, established 2016, manages Meta, Google, TikTok and YouTube ad campaigns for SMEs & mid-sized businesses in Malaysia. Meta & Google Partner certified team."
    canonical="https://beriklan.my/about-us/"
    schema="organization"
>
    <Navbar client:only="svelte" />
    <StickyCTA client:only="svelte" />

    <!-- HERO -->
    <header class="hero relative pt-28 md:pt-44 pb-16 md:pb-24 overflow-hidden bg-gradient-to-br from-white via-soft to-beige">
        <div class="absolute inset-0 opacity-[0.4] pointer-events-none hero-grid"></div>
        <div class="abs-blob abs-blob-1"></div>
        <div class="abs-blob abs-blob-2"></div>
        <div class="container mx-auto px-6 text-center max-w-3xl relative z-10">
            <div class="hero-eyebrow inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 text-ink font-semibold rounded-full text-xs tracking-wider uppercase shadow-sm mb-6">
                <span class="relative flex h-2 w-2">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
                </span>
                About Us · Since 2016
            </div>
            <h1 class="font-display font-extrabold text-4xl md:text-5xl lg:text-6xl text-ink leading-[1.05] tracking-tight mb-6 anim-fade-up">
                Beriklan — Not Just an<br/>
                <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-2 to-accent">Ad Vendor, but Your Partner</span><br/>
                in Performance Strategy.
            </h1>
            <p class="text-base md:text-lg text-muted leading-relaxed mb-8 anim-fade-up" style="animation-delay: 120ms;">
                Since 2016 we have helped SMEs & mid-sized businesses run hundreds of
                digital ad campaigns — Meta, Google, TikTok, YouTube. Not the kind of
                agency that hides your accounts. We give you full access, a real-time
                dashboard, and reports you can hold us accountable to.
            </p>
        </div>
    </header>

    <!-- QUICK STATS -->
    <section class="py-12 md:py-16 bg-white">
        <div class="container mx-auto px-6">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-5 max-w-5xl mx-auto reveal-stagger">
                <div class="text-center p-6 bg-gradient-to-br from-soft to-white rounded-2xl border border-gray-100">
                    <p class="font-display font-extrabold text-3xl md:text-4xl text-primary mb-1">9</p>
                    <p class="text-xs text-muted uppercase tracking-wider font-bold">Years of Experience</p>
                </div>
                <div class="text-center p-6 bg-gradient-to-br from-soft to-white rounded-2xl border border-gray-100">
                    <p class="font-display font-extrabold text-3xl md:text-4xl text-primary mb-1">100+</p>
                    <p class="text-xs text-muted uppercase tracking-wider font-bold">Campaigns Managed</p>
                </div>
                <div class="text-center p-6 bg-gradient-to-br from-soft to-white rounded-2xl border border-gray-100">
                    <p class="font-display font-extrabold text-3xl md:text-4xl text-primary mb-1">3</p>
                    <p class="text-xs text-muted uppercase tracking-wider font-bold">Partner Certifications</p>
                </div>
                <div class="text-center p-6 bg-gradient-to-br from-soft to-white rounded-2xl border border-gray-100">
                    <p class="font-display font-extrabold text-3xl md:text-4xl text-primary mb-1">1 hr</p>
                    <p class="text-xs text-muted uppercase tracking-wider font-bold">WhatsApp Response</p>
                </div>
            </div>
        </div>
    </section>

    <!-- STORY / MISSION / VISION -->
    <section class="py-20 md:py-28 bg-gradient-to-br from-soft via-white to-beige">
        <div class="container mx-auto px-6 max-w-5xl">
            <div class="text-center mb-16">
                <p class="text-xs font-bold uppercase tracking-[0.2em] text-accent mb-3">The Beriklan Story</p>
                <h2 class="font-display font-extrabold text-3xl md:text-5xl text-ink">
                    It Starts with an Audit, and Ends in a Partnership
                </h2>
            </div>
            <div class="grid md:grid-cols-2 gap-12 reveal-stagger">
                <div class="bg-white rounded-2xl p-8 shadow-soft border border-gray-100">
                    <p class="text-xs font-bold uppercase tracking-[0.2em] text-accent mb-3">Mission</p>
                    <h3 class="font-display font-bold text-xl text-ink mb-4">Bringing Measurable Digital Advertising to Malaysian SMEs</h3>
                    <p class="text-muted leading-relaxed">
                        Most SMEs fail at digital advertising for three reasons: targeting spread
                        too wide, creative that misses the audience, or a landing page that does
                        not convert. Beriklan exists to diagnose those three problems first — and
                        only then build a measurable strategy for your business.
                    </p>
                </div>
                <div class="bg-white rounded-2xl p-8 shadow-soft border border-gray-100">
                    <p class="text-xs font-bold uppercase tracking-[0.2em] text-accent mb-3">Vision</p>
                    <h3 class="font-display font-bold text-xl text-ink mb-4">A Senior Performance Partner, Not an Execution Vendor</h3>
                    <p class="text-muted leading-relaxed">
                        We position ourselves as a "Senior Performance Marketing Partner" — not a
                        vendor that simply runs ads. Every client gets strategic guidance, a
                        real-time dashboard, and actionable weekly reports. You know exactly
                        where every ringgit of ad spend goes.
                    </p>
                </div>
            </div>
        </div>
    </section>

    <!-- TIMELINE / MILESTONES -->
    <section class="py-20 md:py-28 bg-white">
        <div class="container mx-auto px-6 max-w-4xl">
            <div class="text-center mb-16">
                <p class="text-xs font-bold uppercase tracking-[0.2em] text-accent mb-3">The Journey</p>
                <h2 class="font-display font-extrabold text-3xl md:text-5xl text-ink">
                    9 Years of Managing Campaigns
                </h2>
            </div>
            <ol class="timeline-list">
                <li class="timeline-item">
                    <span class="timeline-year">2016</span>
                    <p class="timeline-text">Started managing Facebook Ads campaigns for small businesses.</p>
                </li>
                <li class="timeline-item">
                    <span class="timeline-year">2018</span>
                    <p class="timeline-text">Expanded into Instagram Ads and Google Ads (Search & Display).</p>
                </li>
                <li class="timeline-item">
                    <span class="timeline-year">2020</span>
                    <p class="timeline-text">Achieved Meta Business Partner status. Became a full-service agency.</p>
                </li>
                <li class="timeline-item">
                    <span class="timeline-year">2022</span>
                    <p class="timeline-text">Added YouTube Ads & organic Instagram/TikTok management services.</p>
                </li>
                <li class="timeline-item">
                    <span class="timeline-year">2024</span>
                    <p class="timeline-text">Google Partner + TikTok Marketing Partner.</p>
                </li>
                <li class="timeline-item">
                    <span class="timeline-year">2026</span>
                    <p class="timeline-text">Launched Beriklan.my to serve businesses across Malaysia.</p>
                </li>
            </ol>
        </div>
    </section>

    <!-- CERTIFICATIONS / CREDENTIALS -->
    <section class="py-20 md:py-28 bg-gradient-to-br from-primary to-primary-2 text-white">
        <div class="container mx-auto px-6 max-w-5xl">
            <div class="text-center mb-12">
                <p class="text-xs font-bold uppercase tracking-[0.2em] text-accent mb-3">Credentials</p>
                <h2 class="font-display font-extrabold text-3xl md:text-5xl text-white">
                    Certified, Officially Recognised
                </h2>
                <p class="text-base text-white/70 mt-4 max-w-2xl mx-auto">
                    Official partner status from the major ad platforms — not vanity certificates.
                    You can verify each one directly in the partner directories.
                </p>
            </div>
            <div class="grid md:grid-cols-3 gap-5 reveal-stagger">
                <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
                    <Award class="w-8 h-8 text-accent mb-3" />
                    <p class="font-display font-bold text-lg text-white">Meta Business Partner</p>
                    <p class="text-sm text-white/70 mt-2">Verify us in the Meta partner directory.</p>
                </div>
                <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
                    <Award class="w-8 h-8 text-accent mb-3" />
                    <p class="font-display font-bold text-lg text-white">Google Partner</p>
                    <p class="text-sm text-white/70 mt-2">Search, Display, YouTube Ads certified.</p>
                </div>
                <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
                    <Award class="w-8 h-8 text-accent mb-3" />
                    <p class="font-display font-bold text-lg text-white">TikTok Marketing Partner</p>
                    <p class="text-sm text-white/70 mt-2">Official TikTok Ads Manager access.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- CTA -->
    <section class="py-16 md:py-20 bg-gradient-to-br from-primary to-primary-2 text-white text-center">
        <div class="container mx-auto px-6 max-w-2xl relative z-10">
            <p class="text-xs font-bold uppercase tracking-[0.2em] text-accent mb-3">15-Minute Chat · Free of Charge</p>
            <h2 class="font-display font-extrabold text-3xl md:text-4xl text-white">
                Want to Find Out Whether Beriklan<br/>Is the Right Fit for Your Business?
            </h2>
            <p class="text-base text-white/80 mt-4">
                Contact us via WhatsApp — our team is online and replies within 1 hour during business hours.
            </p>
            <a href={waLink} target="_blank" rel="noopener" class="inline-flex items-center gap-2 mt-8 bg-accent text-white px-7 py-3.5 rounded-full font-bold shadow-lg hover:bg-amber-600 transition btn-shine">
                <MessageCircle class="w-4 h-4" />
                Chat With the Beriklan Team
            </a>
        </div>
    </section>

    <Footer client:only="svelte" />
</Layout>

<style>
    .timeline-list {
        position: relative;
        padding-left: 80px;
    }
    .timeline-list::before {
        content: '';
        position: absolute;
        left: 60px;
        top: 0;
        bottom: 0;
        width: 2px;
        background: linear-gradient(to bottom, #f59e0b, #f59e0b33);
    }
    .timeline-item {
        position: relative;
        padding: 1rem 0;
    }
    .timeline-item::before {
        content: '';
        position: absolute;
        left: -28px;
        top: 1.5rem;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: #f59e0b;
        box-shadow: 0 0 0 4px white;
    }
    .timeline-year {
        position: absolute;
        left: -80px;
        top: 0.9rem;
        font-weight: 800;
        font-size: 0.95rem;
        color: #f59e0b;
        width: 50px;
        text-align: right;
    }
    .timeline-text {
        color: #4b5563;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    @media (max-width: 768px) {
        .timeline-list { padding-left: 60px; }
        .timeline-list::before { left: 30px; }
        .timeline-item::before { left: -32px; }
        .timeline-year { left: -60px; }
    }
</style>

<script type="application/ld+json" set:html={JSON.stringify(schemaOrg)} />
<script type="application/ld+json" set:html={JSON.stringify(schemaPerson)} />
'''

with io.open(PAGES + 'about-us.astro', 'w', encoding='utf-8') as f:
    f.write(ABOUT)
print('WROTE about-us.astro (%d lines)' % ABOUT.count('\n'))

METHOD = '''---
import Layout from '../layouts/Layout.astro';
import Navbar from '../components/Navbar.svelte';
import Footer from '../components/Footer.svelte';
import StickyCTA from '../components/StickyCTA.svelte';
import { MessageCircle, Search, Pencil, Rocket, Check, ArrowRight } from 'lucide-svelte';

const waLink = "https://wa.me/62811919328?text=Hi%20Beriklan%2C%20I%27m%20interested%20in%20your%20methodology.%20I%27d%20like%20an%20initial%20consultation.";

const schema = {
    "@context": "https://schema.org",
    "@type": "HowTo",
    "name": "The Beriklan Methodology — How Our Performance Marketing Works",
    "description": "Beriklan's 3-phase process: Diagnose, Strategise, Execute. From initial audit to campaign go-live with weekly reports.",
    "step": [
        {
            "@type": "HowToStep",
            "position": 1,
            "name": "Diagnose — Campaign & Business Audit",
            "text": "Initial 15-consultation. We audit your ad accounts, pixel tracking, landing page and sales funnel. We identify the root problems + potential."
        },
        {
            "@type": "HowToStep",
            "position": 2,
            "name": "Strategise — Plan the Campaign",
            "text": "Audience, competitor and keyword research. We define the objective, budget allocation, channel mix and timeline. Presented as a strategy document for your approval."
        },
        {
            "@type": "HowToStep",
            "position": 3,
            "name": "Execute — Launch & Optimise",
            "text": "Campaign, creative and landing page setup. Launch within 1-3 days. Weekly data-driven optimisation. Reports via WhatsApp + a real-time dashboard."
        }
    ]
};
---

<Layout
    title="Beriklan Methodology — Our 3-Phase Performance Marketing Process | Beriklan"
    description="How Beriklan works: Diagnose → Strategise → Execute. initial audit, measurable strategy, and execution with accountable weekly reports."
    canonical="https://beriklan.my/methodology/"
>
    <Navbar client:only="svelte" />
    <StickyCTA client:only="svelte" />

    <!-- HERO -->
    <header class="hero relative pt-28 md:pt-44 pb-16 md:pb-20 overflow-hidden bg-gradient-to-br from-white via-soft to-beige">
        <div class="abs-blob abs-blob-1"></div>
        <div class="container mx-auto px-6 text-center max-w-3xl relative z-10">
            <div class="hero-eyebrow inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 text-ink font-semibold rounded-full text-xs tracking-wider uppercase shadow-sm mb-6">
                Methodology · 3 Phases · Since 2016
            </div>
            <h1 class="font-display font-extrabold text-4xl md:text-5xl lg:text-6xl text-ink leading-[1.05] tracking-tight mb-6 anim-fade-up">
                A Way of Working that Is <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-2 to-accent">Measured,</span><br/>
                Not Trial and Error.
            </h1>
            <p class="text-base md:text-lg text-muted leading-relaxed anim-fade-up" style="animation-delay: 120ms;">
                Three phases proven since 2016 — from initial audit to a measurable campaign
                with reports you can hold us accountable to.
            </p>
        </div>
    </header>

    <!-- METHODOLOGY TIMELINE -->
    <section class="py-20 md:py-28 bg-gradient-to-br from-soft via-white to-beige">
        <div class="container mx-auto px-6 max-w-5xl">

            <!-- PHASE 1 -->
            <div class="grid md:grid-cols-12 gap-8 mb-16 reveal-stagger">
                <div class="md:col-span-3 flex md:flex-col items-start gap-4 md:gap-2">
                    <span class="phase-num">01</span>
                    <div>
                        <p class="phase-label">Week 1</p>
                        <p class="phase-icon-label"><Search class="w-4 h-4" /> Diagnose</p>
                    </div>
                </div>
                <div class="md:col-span-9 bg-white rounded-2xl p-8 shadow-soft border border-gray-100">
                    <h2 class="font-display font-extrabold text-2xl md:text-3xl text-ink mb-4">Diagnose · Audit & Identify</h2>
                    <p class="text-muted leading-relaxed mb-5">
                        Before shaping any strategy, we audit first. An initial 15-30 minute
                        consultation via WhatsApp or Zoom to understand your business. Then we
                        send a written audit that covers:
                    </p>
                    <ul class="space-y-2 mb-5">
                        <li class="flex gap-3"><Check class="w-5 h-5 text-green flex-shrink-0 mt-0.5" /><span>Audit of your previous ad account (if any) — what worked, what died</span></li>
                        <li class="flex gap-3"><Check class="w-5 h-5 text-green flex-shrink-0 mt-0.5" /><span>Pixel tracking & conversion audit</span></li>
                        <li class="flex gap-3"><Check class="w-5 h-5 text-green flex-shrink-0 mt-0.5" /><span>Landing page audit — converting or bouncing</span></li>
                        <li class="flex gap-3"><Check class="w-5 h-5 text-green flex-shrink-0 mt-0.5" /><span>Competitor analysis & market positioning</span></li>
                        <li class="flex gap-3"><Check class="w-5 h-5 text-green flex-shrink-0 mt-0.5" /><span>Budget estimate & realistic ROI projection</span></li>
                    </ul>
                    <p class="text-sm text-muted"><strong>Deliverable:</strong> Audit document + strategy recommendations + budget estimate.</p>
                </div>
            </div>

            <!-- PHASE 2 -->
            <div class="grid md:grid-cols-12 gap-8 mb-16 reveal-stagger">
                <div class="md:col-span-3 flex md:flex-col items-start gap-4 md:gap-2">
                    <span class="phase-num">02</span>
                    <div>
                        <p class="phase-label">Week 1-2</p>
                        <p class="phase-icon-label"><Pencil class="w-4 h-4" /> Strategise</p>
                    </div>
                </div>
                <div class="md:col-span-9 bg-white rounded-2xl p-8 shadow-soft border border-gray-100">
                    <h2 class="font-display font-extrabold text-2xl md:text-3xl text-ink mb-4">Strategise · Plan the Campaign</h2>
                    <p class="text-muted leading-relaxed mb-5">
                        After the audit, we build a measurable strategy. You approve it before
                        any execution — no hidden decisions.
                    </p>
                    <ul class="space-y-2 mb-5">
                        <li class="flex gap-3"><Check class="w-5 h-5 text-green flex-shrink-0 mt-0.5" /><span>Audience research — demographics, interests, behaviours, lookalikes</span></li>
                        <li class="flex gap-3"><Check class="w-5 h-5 text-green flex-shrink-0 mt-0.5" /><span>Channel mix — Meta, Google, TikTok, YouTube per objective</span></li>
                        <li class="flex gap-3"><Check class="w-5 h-5 text-green flex-shrink-0 mt-0.5" /><span>Budget allocation — daily vs total, scale-up plan</span></li>
                        <li class="flex gap-3"><Check class="w-5 h-5 text-green flex-shrink-0 mt-0.5" /><span>Creative brief — format, messaging, hook, CTA</span></li>
                        <li class="flex gap-3"><Check class="w-5 h-5 text-green flex-shrink-0 mt-0.5" /><span>Tracking plan — pixel, events, conversion API</span></li>
                    </ul>
                    <p class="text-sm text-muted"><strong>Deliverable:</strong> A strategy document for you to review + approve.</p>
                </div>
            </div>

            <!-- PHASE 3 -->
            <div class="grid md:grid-cols-12 gap-8 mb-16 reveal-stagger">
                <div class="md:col-span-3 flex md:flex-col items-start gap-4 md:gap-2">
                    <span class="phase-num">03</span>
                    <div>
                        <p class="phase-label">Week 2+</p>
                        <p class="phase-icon-label"><Rocket class="w-4 h-4" /> Execute</p>
                    </div>
                </div>
                <div class="md:col-span-9 bg-gradient-to-br from-primary to-primary-2 text-white rounded-2xl p-8 shadow-pop">
                    <h2 class="font-display font-extrabold text-2xl md:text-3xl text-white mb-4">Execute · Launch & Optimise</h2>
                    <p class="text-white/80 leading-relaxed mb-5">
                        The campaign goes live. You get full access to every ad account — nothing
                        hidden away like some agencies do. We run weekly optimisation based on
                        real-time data.
                    </p>
                    <ul class="space-y-2 mb-5">
                        <li class="flex gap-3"><Check class="w-5 h-5 text-accent flex-shrink-0 mt-0.5" /><span>Campaign + creative + landing page setup (in parallel)</span></li>
                        <li class="flex gap-3"><Check class="w-5 h-5 text-accent flex-shrink-0 mt-0.5" /><span>Launch within 1-3 days of strategy approval</span></li>
                        <li class="flex gap-3"><Check class="w-5 h-5 text-accent flex-shrink-0 mt-0.5" /><span>Weekly A/B testing — creative, audience, copy</span></li>
                        <li class="flex gap-3"><Check class="w-5 h-5 text-accent flex-shrink-0 mt-0.5" /><span>Budget optimisation — scale what performs, pause what dies</span></li>
                        <li class="flex gap-3"><Check class="w-5 h-5 text-accent flex-shrink-0 mt-0.5" /><span>Weekly reports via WhatsApp + a 24/7 real-time dashboard</span></li>
                    </ul>
                    <p class="text-sm text-white/70"><strong>Deliverable:</strong> Live campaign + weekly reports + measured iteration.</p>
                </div>
            </div>

        </div>
    </section>

    <!-- DELIVERABLES SUMMARY -->
    <section class="py-16 bg-white">
        <div class="container mx-auto px-6 max-w-4xl">
            <div class="text-center mb-12">
                <p class="text-xs font-bold uppercase tracking-[0.2em] text-accent mb-3">What You Get</p>
                <h2 class="font-display font-extrabold text-3xl md:text-4xl text-ink">
                    7 Deliverables in Total
                </h2>
            </div>
            <div class="grid md:grid-cols-2 gap-4">
                {[
                    {t: "Audit Document", d: "Account condition analysis + written recommendations"},
                    {t: "Campaign Strategy", d: "Channel mix + budget + audience + creative brief"},
                    {t: "Account & Pixel Setup", d: "Ads platform configuration + tracking pixel"},
                    {t: "Creative Production", d: "Copywriting + design brief (production optional)"},
                    {t: "Landing Page", d: "Single conversion-ready page (optional)"},
                    {t: "Weekly Reports", d: "Performance + iteration recommendations via WhatsApp"},
                    {t: "Real-Time Dashboard", d: "Monitor everything yourself via ad account access"}
                ].map(d => (
                    <div class="flex items-start gap-3 p-4 bg-soft rounded-xl">
                        <Check class="w-5 h-5 text-green flex-shrink-0 mt-0.5" />
                        <div>
                            <p class="font-bold text-ink">{d.t}</p>
                            <p class="text-sm text-muted">{d.d}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    </section>

    <!-- CTA -->
    <section class="py-16 md:py-20 bg-gradient-to-br from-primary to-primary-2 text-white text-center">
        <div class="container mx-auto px-6 max-w-2xl relative z-10">
            <p class="text-xs font-bold uppercase tracking-[0.2em] text-accent mb-3">Start with Phase 1 (Free)</p>
            <h2 class="font-display font-extrabold text-3xl md:text-4xl text-white">
                Want to Know What Is Really Holding Your Campaign Back?
            </h2>
            <a href={waLink} target="_blank" rel="noopener" class="inline-flex items-center gap-2 mt-8 bg-accent text-white px-7 py-3.5 rounded-full font-bold shadow-lg hover:bg-amber-600 transition btn-shine">
                <MessageCircle class="w-4 h-4" />
                Consultation · Free
            </a>
        </div>
    </section>

    <Footer client:only="svelte" />
</Layout>

<script type="application/ld+json" set:html={JSON.stringify(schema)} />

<style>
    .phase-num {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 800;
        font-size: 4rem;
        line-height: 1;
        background: linear-gradient(135deg, #0f1e3d, #f59e0b);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }
    .phase-label {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #6b7280;
    }
    .phase-icon-label {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        margin-top: 0.5rem;
        color: #f59e0b;
        font-weight: 700;
        font-size: 0.95rem;
    }
</style>
'''

with io.open(PAGES + 'methodology.astro', 'w', encoding='utf-8') as f:
    f.write(METHOD)
print('WROTE methodology.astro (%d lines)' % METHOD.count('\n'))
print('DONE about + methodology')
