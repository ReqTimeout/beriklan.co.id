#!/usr/bin/env python3
"""
Bulk generate city-service landing pages via CF Workers AI (free tier).

Workflow:
1. Load keywords (1478 from Excel) × cities (28) → derive combos from per_city.json
2. For each combo (city, service):
   - Build prompt with city facts + service description + testimonial rotation
   - Call CF Workers AI via https://beriklan.co.id/api/llm/chat
   - Quality gate: word count, FAQ count, density, AdSense policy
   - If pass: write src/pages/jasa-{service}/{city}/index.astro
   - If fail: log to manual_review, retry once with adjusted prompt
3. Track in D1 keyword_queue + articles

Usage:
    python3 scripts/seo/bulk_generate.py --pilot 5 --dry-run
    python3 scripts/seo/bulk_generate.py --pilot 5 --generate
    python3 scripts/seo/bulk_generate.py --batch city-facebook --generate
    python3 scripts/seo/bulk_generate.py --batch city-all  # 28 × 7 services = 196 pages
"""

import argparse
import json
import os
import random
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

import requests
from typing import Optional, List, Dict

ROOT = Path(__file__).parent.parent.parent
PAGES_DIR = ROOT / "src/pages"
PAGES_DIR_WEB = ROOT.parent / "web/src/pages"
KEYWORDS = json.loads((ROOT / "src/data/keywords.json").read_text())
CITIES = json.loads((ROOT / "src/data/cities.json").read_text())
SERVICES = json.loads((ROOT / "src/data/services.json").read_text())
TESTIMONIALS = json.loads((ROOT / "src/data/testimonials.json").read_text())
PER_CITY = json.loads((ROOT / "src/data/per_city.json").read_text())
LOCAL_FAQS = json.loads((ROOT / "src/data/local-faqs.json").read_text())

# CF Workers AI endpoint via Worker (no API key needed, free 10K req/hari)
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://beriklan.co.id")
LLM_MODEL = os.getenv("LLM_MODEL", "@cf/meta/llama-3.3-70b-instruct-fp8-fast")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "beriklan-admin-2026")

# AdSense policy blocklist (P0/§48.2 — auto-reject if matched)
POLICY_BLOCKLIST = {
    "adult": ["sex", "porn", "naked", "telanjang", "bugil"],
    "violence": ["kill", "bantai", "bom", "senjata", "teror"],
    "drugs": ["narkoba", "sabu", "ganja", "ekstasi"],
    "copyright": ["download gratis", "crack", "bajakan", "pirated"],
    "misleading": ["pasti untung", "100% closing", "dijamin roi", "tanpa risiko"],
    "hacking": ["hack", "crack", "cheat", "exploit", "carding"],
    "counterfeit": ["fake brand", "replika original", "kw super"]
}

# Editorial style — banned phrases (P0)
BANNED_PHRASES = [
    "Dalam dunia digital", "Penting untuk diketahui", "Demikian artikel",
    "Semoga bermanfaat", "Sebagai kesimpulan", "Kesimpulannya",
    "Dewasa ini", "Pada era digital", "Tak dapat dipungkiri",
]

# Pricing tiers (consistent with platform pages)
PRICING_TIERS = [
    {"name": "Paket Pemanasan", "viewers": "20 viewers", "price_label": "12K", "wa_text": "Paket Pemanasan"},
    {"name": "Paket Starter", "viewers": "50 viewers", "price_label": "25K", "wa_text": "Paket Starter"},
    {"name": "Paket Basic", "viewers": "100 viewers", "price_label": "45K", "wa_text": "Paket Basic"},
    {"name": "Paket Pro", "viewers": "200 viewers", "price_label": "80K", "wa_text": "Paket Pro"},
    {"name": "Paket Bisnis", "viewers": "300 viewers", "price_label": "115K", "wa_text": "Paket Bisnis"},
    {"name": "Paket Premium", "viewers": "500 viewers", "price_label": "175K", "wa_text": "Paket Premium"},
]


def get_service(slug: str) -> Optional[dict]:
    return next((s for s in SERVICES if s["slug"] == slug), None)


def get_city(slug: str) -> Optional[dict]:
    return next((c for c in CITIES if c["slug"] == slug), None)


def get_testimonial(city_slug: str, service_slug: str) -> dict:
    matches = [t for t in TESTIMONIALS if t.get("city_slug") == city_slug]
    if matches:
        t = random.choice(matches)
    else:
        t = random.choice(TESTIMONIALS)
    return t


def get_local_faqs(city_slug: str, service_slug: str) -> list:
    matches = [f for f in LOCAL_FAQS if f.get("city_slug") == city_slug and f.get("service_slug") == service_slug]
    return matches[:7]


def build_prompt(city: dict, service: dict, word_target: int = 800) -> str:
    """Build LLM prompt for city-service page intro/content."""
    local_facts = "\n".join(f"- {f}" for f in city.get("local_facts", []))
    faqs_seed = "\n".join(f"Q: {f['question']}\nA: {f['answer']}" for f in get_local_faqs(city["slug"], service["slug"])[:5])

    prompt = f"""Kamu adalah copywriter SEO senior untuk Beriklan.co.id. Tulis konten Bahasa Indonesia untuk halaman layanan.

TARGET KEYWORD: "{service['name']} {city['name']}"
TUJUAN: Halaman ini akan diindeks Google untuk search "{service['name']} {city['name']}". Konten harus:
1. UNIK & BERMANFAAT — bukan generic text-spinning
2. FACTUAL — sebut data kota spesifik, UMKM count, contoh bisnis nyata (jangan mengarang nomor yang tidak masuk akal)
3. TONE profesional Senior Performance Marketing Partner, bukan salesy
4. LARANG pakai frasa: "Dalam dunia", "Penting untuk", "Demikian", "Semoga bermanfaat", "Kesimpulannya"

FAKTA KOTA {city['name'].upper()}:
{local_facts}

DESKRIPSI LAYANAN {service['name']}:
{service['description']}

FAQ SEED (gunakannya sebagai referensi tapi parafrase):
{faqs_seed}

STRUKTUR OUTPUT (HTML langsung, tanpa markdown wrapper):
1. <h2>Mengapa Bisnis di {city['name']} Butuh {service['name']}</h2>
   <p>(2-3 paragraf, total 150-180 kata. WAJIB ada 1 angka spesifik + 1 contoh konkret)</p>

2. <h2>Tantangan {service['name']} di Pasar {city['name']}</h2>
   <p>(2 paragraf, 120-140 kata. Tantangan spesifik sesuai konteks kota)</p>

3. <h2>Solusi Beriklan untuk {service['name']} di {city['name']}</h2>
   <p>Solusi dalam paragraf (100-120 kata) + daftar bullet 4-5 poin keuntungan</p>

4. <h2>Layanan Lain yang Relevan di {city['name']}</h2>
   <p>(1 paragraf 80 kata tentang upsell ke layanan terkait)</p>

5. <h2>FAQ {service['name']} {city['name']}</h2>
   <div>5 FAQ dengan format <h3>Question?</h3><p>Answer...</p></div>

KATA TOTAL: {word_target-100}-{word_target+100} kata (tidak termasuk HTML tags)

PENTING: Output HANYA HTML body content (paragraf, list, h2, h3). Jangan sertakan <section>, <article>, <!DOCTYPE>, atau tag meta apapun.
"""

    return prompt


def call_llm(prompt: str, model: str = None, max_tokens: int = 2200, max_retries: int = 3) -> dict:
    """Call CF Workers AI via Worker proxy."""
    url = f"{LLM_BASE_URL}/api/llm/chat"
    m = model or LLM_MODEL
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.post(url,
                             json={
                                 "model": m,
                                 "messages": [{"role": "user", "content": prompt}],
                                 "max_tokens": max_tokens,
                                 "temperature": 0.7
                             },
                             timeout=120)
            if r.status_code == 200:
                data = r.json()
                content = data.get("content", "")
                if content:
                    return {"ok": True, "content": content, "model": m, "usage": data.get("usage", {})}
                print(f"  attempt {attempt}: empty content")
            else:
                print(f"  attempt {attempt}: HTTP {r.status_code} - {r.text[:200]}")
        except Exception as e:
            print(f"  attempt {attempt}: exception {type(e).__name__}: {e}")
        if attempt < max_retries:
            time.sleep(2 ** attempt)
    return {"ok": False, "content": "", "error": "all retries failed"}


def html_to_markdown_for_quality(html_content: str) -> str:
    """Strip HTML for quality metrics."""
    text = re.sub(r"<[^>]+>", " ", html_content)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def quality_check(html_content: str, city: dict, service: dict) -> dict:
    """Run quality gate: word count, FAQ count, policy, banned phrases, density."""
    text = html_to_markdown_for_quality(html_content)
    words = text.split()
    word_count = len(words)

    # FAQ count (h3 with ?)
    faq_count = len(re.findall(r"<h3[^>]*>[^<]*\?[^<]*</h3>", html_content, re.IGNORECASE))

    # H2 count
    h2_count = len(re.findall(r"<h2[^>]*>", html_content))

    # Keyword density: count occurrences of service_name OR city_name words
    # (more lenient than exact phrase match — accommodates "Jasa Iklan Facebook di Bandung")
    service_words = re.findall(r"\b\w+\b", service['name'].lower())
    city_words = re.findall(r"\b\w+\b", city['name'].lower())
    text_lower = text.lower()
    # count words occurring together with at most 1 word gap
    keyphrase_hits = 0
    if service_words and city_words:
        sw = r"\s+(?:\w+\s+)?" + r"\s+".join(re.escape(w) for w in service_words)
        cwm = r"\s+".join(re.escape(w) for w in city_words)
        pattern = sw + r"\s+" + cwm
        keyphrase_hits = len(re.findall(pattern, text_lower))
        # also count word-level co-occurrence (city + service words in same paragraph)
        city_mentions = text_lower.count(city['name'].lower())
        service_mentions = text_lower.count(service['name'].lower())
        cooccurrence = min(city_mentions, service_mentions)
    else:
        cooccurrence = 0
    density = ((keyphrase_hits + cooccurrence * 0.3) / max(word_count, 1)) * 100

    # AdSense policy blocklist
    policy_violations = []
    for category, kws in POLICY_BLOCKLIST.items():
        for kw in kws:
            if kw in text_lower:
                policy_violations.append({"category": category, "keyword": kw})

    # Banned phrases (style)
    style_violations = []
    for phrase in BANNED_PHRASES:
        if phrase.lower() in text_lower:
            style_violations.append(phrase)

    return {
        "word_count": word_count,
        "faq_count": faq_count,
        "h2_count": h2_count,
        "density": round(density, 2),
        "policy_violations": policy_violations,
        "style_violations": style_violations,
        "passed": (
            word_count >= 500 and
            word_count <= 1500 and
            faq_count >= 4 and
            h2_count >= 4 and
            density >= 0.3 and
            len(policy_violations) == 0
        )
    }


def build_page_html(city: dict, service: dict, content_html: str, testimonial: dict, tiers: list, faqs: list) -> str:
    """Build complete Astro page source."""
    slug_path = f"jasa-{service['slug'].replace('jasa-', '').replace('jasa-', '')}/{city['slug']}/index"
    # service slug actual mapping
    if "landing-page" in service['slug']:
        page_slug = "jasa-pembuatan-landing-page"
    else:
        page_slug = service['slug']

    testimonial_html = ""
    if testimonial:
        testimonial_html = (
            '<article class="bg-white rounded-2xl p-7 shadow-soft border border-gray-100">'
            f'<p class="italic text-muted leading-relaxed mb-4">"{testimonial.get("quote","")}"</p>'
            '<div class="border-t border-gray-100 pt-3">'
            f'<p class="font-bold text-ink">{testimonial.get("name","")}</p>'
            f'<p class="text-xs text-muted">{testimonial.get("role","")} · {testimonial.get("city","")}</p>'
            '</div></article>'
        )

    pricing_cards = "\n".join([
        (
            '<div class="bg-white rounded-2xl p-6 shadow-soft border border-gray-100">'
            f'<p class="text-xs font-bold uppercase tracking-wider text-accent mb-2">{t["name"]}</p>'
            f'<p class="font-display font-extrabold text-2xl text-primary mb-2">Rp {t["price_label"]}</p>'
            f'<p class="text-sm text-muted mb-4">{t["viewers"]}</p>'
            f'<a href="https://wa.me/62811919328?text=Halo%20Beriklan%2C%20saya%20tertarik%20{t["name"].replace(" ", "%20")}%20untuk%20{service["name"].replace(" ", "%20")}%20{city["name"].replace(" ", "%20")}" target="_blank" rel="noopener" class="block text-center bg-accent text-white px-4 py-2.5 rounded-full font-bold text-sm hover:bg-amber-600 transition">Pilih Paket</a>'
            '</div>'
        )
        for t in tiers
    ])

    related_services_html = "\n".join([
        f'<a href="/jasa-{s["slug"]}/{city["slug"]}/" class="text-accent hover:underline">{s["name"]} di {city["name"]}</a>'
        for s in SERVICES if s['slug'] != service['slug']
    ])

    testimonial_section = ""
    if testimonial:
        testimonial_section = (
            '<section class="py-20 md:py-28 bg-gradient-to-br from-soft via-white to-beige">'
            '<div class="container mx-auto px-6 max-w-3xl">'
            f'<p class="text-xs font-bold uppercase tracking-[0.2em] text-accent mb-3 text-center">Klien dari {city["name"]}</p>'
            '<h2 class="font-display font-extrabold text-2xl md:text-3xl text-ink mb-8 text-center">Kata Mereka Setelah Bekerja Sama</h2>'
            f'{testimonial_html}'
            '</div></section>'
        )

    # JSON-stringified for use in JSX attribute context (NOT Python repr)
    city_js = json.dumps(city, ensure_ascii=False)        # {"slug": "jakarta", ...}
    service_js = json.dumps(service, ensure_ascii=False)
    testimonial_js = json.dumps(testimonial, ensure_ascii=False)
    faqs_js = json.dumps(faqs, ensure_ascii=False)
    # Boolean to lowercase
    service_js = service_js.replace(": true", ": true").replace(": false", ": false")  # noop for safety

    canonical = f"https://beriklan.co.id/{service['slug']}/{city['slug']}/"
    desc = f"{service['name']} di {city['name']} dari tim Meta & Google Partner sejak 2016. Konsultasi 15 menit gratis."
    wa_link = (
        f"https://wa.me/62811919328?text=Halo%20Beriklan%2C%20saya%20tertarik%20"
        f"{service['name']}%20di%20{city['name']}.%20Mau%20konsultasi%20awal."
    )

    # Python 3.9 compatible: precompute strings for f-string interpolation
    service_slug_for_url = f"{service['slug']}/{city['slug']}/"

    # Pre-compute breadcrumb URLs (avoid Python 3.9 f-string backtick limitation)
    bc0 = "/"
    bc1 = f"/{service['slug']}/"
    bc2 = f"/{service['slug']}/{city['slug']}/"
    breadcrumb_array = (
        '[["Beranda", "/"], '
        f'["{service["name"]}", "{bc1}"], '
        f'["{city["name"]}", "{bc2}"]]'
    )

    page = f"""---
import Layout from '../../../layouts/Layout.astro';
import Navbar from '../../../components/Navbar.svelte';
import Footer from '../../../components/Footer.svelte';
import StickyCTA from '../../../components/StickyCTA.svelte';
import LocalSchema from '../../../components/LocalSchema.astro';
import {{ MessageCircle, Sparkles, ArrowRight }} from 'lucide-svelte';

const city = {city_js};
const service = {service_js};
const testimonial = {testimonial_js};
const faqs = {faqs_js};
---

<Layout
    title="{service['name']} di {city['name']} — Konsultasi Gratis | Beriklan"
    description="{desc}"
    canonical="{canonical}"
>
    <Navbar client:only="svelte" />
    <StickyCTA client:only="svelte" />

    <!-- HERO -->
    <header class="hero relative pt-28 md:pt-44 pb-12 md:pb-16 overflow-hidden bg-gradient-to-br from-white via-soft to-beige">
        <div class="abs-blob abs-blob-1"></div>
        <div class="container mx-auto px-6 text-center max-w-3xl relative z-10">
            <div class="hero-eyebrow inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 text-ink font-semibold rounded-full text-xs tracking-wider uppercase shadow-sm mb-6">
                <span class="relative flex h-2 w-2">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
                </span>
                {service['name']} di {city['name']} · Tim Online
            </div>
            <h1 class="font-display font-extrabold text-3xl md:text-5xl lg:text-6xl text-ink leading-[1.05] tracking-tight mb-6 anim-fade-up">
                {service['name']}<br/>
                <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-2 to-accent">di {city['name']}.</span>
            </h1>
            <p class="text-base md:text-lg text-muted leading-relaxed mb-8 anim-fade-up" style="animation-delay: 120ms;">
                Tim Beriklan (Meta & Google Partner sejak 2016) mengelola campaign {service['name']} untuk UMKM & bisnis menengah di {city['name']}. Akses penuh ke akun iklan, dashboard real-time, laporan mingguan.
            </p>
            <a href={wa_link} target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-accent text-white px-7 py-3.5 rounded-full font-bold shadow-lg hover:bg-amber-600 transition btn-shine anim-fade-up" style="animation-delay: 240ms;">
                <MessageCircle class="w-4 h-4" />
                Konsultasi 15 Menit Gratis
            </a>
        </div>
    </header>

    <!-- AI-GENERATED CONTENT -->
    <section class="py-20 md:py-28 bg-gradient-to-br from-soft via-white to-beige">
        <div class="container mx-auto px-6 max-w-3xl prose-content">
            {content_html}
        </div>
    </section>

    <!-- PRICING -->
    <section class="py-20 md:py-28 bg-white">
        <div class="container mx-auto px-6 max-w-6xl">
            <div class="text-center mb-12">
                <p class="text-xs font-bold uppercase tracking-[0.2em] text-accent mb-3">Paket Harga</p>
                <h2 class="font-display font-extrabold text-3xl md:text-5xl text-ink">
                    {service['name']} {city['name']}
                </h2>
                <p class="text-muted mt-3">Pilih paket sesuai skala campaign Anda. Semua paket sudah include pendampingan.</p>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 reveal-stagger">
{pricing_cards}
            </div>
        </div>
    </section>
{testimonial_section}
    <!-- RELATED SERVICES -->
    <section class="py-12 bg-white border-t border-gray-100">
        <div class="container mx-auto px-6 max-w-4xl">
            <p class="text-xs font-bold uppercase tracking-[0.2em] text-accent mb-3 text-center">Layanan Lain di {city['name']}</p>
            <p class="text-center text-sm text-muted">
                {related_services_html}
            </p>
        </div>
    </section>

    <!-- FINAL CTA -->
    <section class="py-16 md:py-20 bg-gradient-to-br from-primary to-primary-2 text-white text-center">
        <div class="container mx-auto px-6 max-w-2xl relative z-10">
            <p class="text-xs font-bold uppercase tracking-[0.2em] text-accent mb-3">Mulai dari {city['name']}</p>
            <h2 class="font-display font-extrabold text-3xl md:text-4xl text-white">
                Diskusi {service['name']} untuk Bisnis Anda
            </h2>
            <a href={wa_link} target="_blank" rel="noopener" class="inline-flex items-center gap-2 mt-8 bg-accent text-white px-7 py-3.5 rounded-full font-bold shadow-lg hover:bg-amber-600 transition btn-shine">
                <MessageCircle class="w-4 h-4" />
                Konsultasi via WhatsApp
            </a>
        </div>
    </section>

    <Footer client:only="svelte" />

    <LocalSchema
        type="city-service"
        city={{{city_js}}}
        service={{{service_js}}}
        faqs={{{faqs_js}}}
        pageUrl="/{service_slug_for_url}"
        breadcrumbs={{{breadcrumb_array}}}
    />
</Layout>

<style is:global>
    .prose-content h2 {{ margin-top: 2.5rem; margin-bottom: 1rem; font-size: 1.5rem; font-weight: 800; color: #0b1426; font-family: 'Plus Jakarta Sans', sans-serif; }}
    .prose-content h2:first-child {{ margin-top: 0; }}
    .prose-content h3 {{ margin-top: 1.5rem; margin-bottom: 0.5rem; font-size: 1.1rem; font-weight: 700; color: #0b1426; font-family: 'Plus Jakarta Sans', sans-serif; }}
    .prose-content p {{ margin: 1rem 0; line-height: 1.75; color: #4b5563; }}
    .prose-content ul {{ margin: 1rem 0; padding-left: 1.5rem; }}
    .prose-content ul li {{ margin-bottom: 0.5rem; color: #4b5563; line-height: 1.65; }}
    .prose-content strong {{ color: #0b1426; }}
</style>
"""
    return page


def get_service_slug_for_url(service: dict) -> str:
    return service['slug']


def main():
    p = argparse.ArgumentParser(description="Bulk generate city-service pages")
    p.add_argument("--pilot", type=int, default=0, help="Generate N pilot pages first")
    p.add_argument("--batch", help="Batch name: city-facebook, city-tiktok, etc., or city-all")
    p.add_argument("--generate", action="store_true", help="Actually write files (default dry-run)")
    p.add_argument("--model", default=LLM_MODEL, help="LLM model to use")
    args = p.parse_args()

    # Define target combos
    combos = []

    # Get list of services to generate
    target_services = [s for s in SERVICES if "kelola" not in s['slug'] and "website" not in s['slug'] and "landing" not in s['slug']]
    # Top services for city pages: facebook, instagram, tiktok, google, youtube, digital-marketing
    city_services = ["jasa-iklan-facebook", "jasa-iklan-instagram", "jasa-iklan-tiktok", "jasa-iklan-google", "jasa-iklan-youtube", "jasa-digital-marketing", "jasa-pembuatan-landing-page"]
    target_services = [s for s in SERVICES if s['slug'] in city_services]

    if args.pilot:
        # Generate pilot: jakarta/bandung/surabaya/medan/makassar × facebook (limited by --pilot N)
        pilot_cities = ["jakarta", "bandung", "surabaya", "medan", "makassar"]
        fb_service = next(s for s in target_services if s['slug'] == 'jasa-iklan-facebook')
        combos = [(c, fb_service) for c in CITIES if c['slug'] in pilot_cities]
        combos = combos[:args.pilot]
    elif args.batch == "city-all":
        for city in CITIES:
            for service in target_services:
                if city.get("is_international"): continue  # Skip non-ID for now
                combos.append((city, service))
    elif args.batch == "city-facebook":
        fb_service = next(s for s in target_services if s['slug'] == "jasa-iklan-facebook")
        for city in CITIES:
            if city.get("is_international"): continue
            combos.append((city, fb_service))
    elif args.batch:
        # batch = "city-facebook", "city-instagram", etc
        b = args.batch.replace("city-", "")
        svc = next((s for s in target_services if b in s['slug']), None)
        if not svc:
            print(f"Service not found for batch: {args.batch}")
            sys.exit(1)
        for city in CITIES:
            if city.get("is_international"): continue
            combos.append((city, svc))
    else:
        print("Provide --pilot N or --batch city-{service} or city-all")
        sys.exit(1)

    print(f"Total combos to process: {len(combos)}")
    print(f"Model: {args.model}")
    print(f"Output mode: {'GENERATE' if args.generate else 'DRY-RUN'}")
    print()

    stats = {"success": 0, "policy_reject": 0, "low_quality_retry": 0, "error": 0}
    log = []

    for i, (city, service) in enumerate(combos, 1):
        url_path = f"/{service['slug']}/{city['slug']}/"
        out_path = PAGES_DIR / service['slug'] / city['slug'] / "index.astro"
        out_path_web = PAGES_DIR_WEB / service['slug'] / city['slug'] / "index.astro" if PAGES_DIR_WEB.exists() else None

        print(f"[{i}/{len(combos)}] {service['slug']}/{city['slug']}/")

        # Skip if already exists
        if out_path.exists() and not args.generate:
            print(f"  ALREADY EXISTS — skipping (use --generate to overwrite)")
            continue

        # Build prompt
        prompt = build_prompt(city, service)
        # Call LLM
        result = call_llm(prompt, model=args.model, max_tokens=2500, max_retries=2)

        if not result["ok"]:
            print(f"  LLM FAILED: {result.get('error')}")
            stats["error"] += 1
            log.append({"city": city['slug'], "service": service['slug'], "status": "error", "reason": result.get('error')})
            time.sleep(5)
            continue

        content_html = result["content"]

        # Quality gate
        qc = quality_check(content_html, city, service)
        print(f"  QC: words={qc['word_count']} faq={qc['faq_count']} h2={qc['h2_count']} density={qc['density']}% policy={len(qc['policy_violations'])} style={len(qc['style_violations'])}")

        if qc["policy_violations"]:
            print(f"  POLICY REJECT: {qc['policy_violations']}")
            stats["policy_reject"] += 1
            log.append({"city": city['slug'], "service": service['slug'], "status": "policy_reject", "violations": qc['policy_violations']})
            continue

        if not qc["passed"]:
            print(f"  QUALITY REJECT (will retry)")
            # 1 retry with stricter prompt
            retry_prompt = prompt + "\n\n[PENTING: Jawaban sebelumnya tidak lulus quality gate. Tolong tulis ulang DENGAN kata lebih banyak (target 800-900 kata) dan 5 FAQ dengan format yang jelas. JANGAN pakai frasa terlarang.]"
            retry_result = call_llm(retry_prompt, model=args.model, max_tokens=3000, max_retries=1)
            if retry_result["ok"]:
                content_html = retry_result["content"]
                qc = quality_check(content_html, city, service)
                if not qc["passed"]:
                    print(f"  RETRY QUALITY STILL LOW: skipping")
                    stats["low_quality_retry"] += 1
                    log.append({"city": city['slug'], "service": service['slug'], "status": "low_quality", "qc": qc})
                    continue
            else:
                stats["low_quality_retry"] += 1
                continue

        # Build page
        testimonial = get_testimonial(city['slug'], service['slug'])
        faqs = get_local_faqs(city['slug'], service['slug'])
        tiers = PRICING_TIERS[:6]
        page_source = build_page_html(city, service, content_html, testimonial, tiers, faqs)

        if args.generate:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(page_source)
            print(f"  ✓ WROTE {out_path}")
            # Also write to web/ if exists
            if out_path_web:
                out_path_web.parent.mkdir(parents=True, exist_ok=True)
                out_path_web.write_text(page_source)
            stats["success"] += 1
        else:
            print(f"  DRY-RUN: would write {out_path}")
            stats["success"] += 1  # dry-run count as success for the prompt

        log.append({
            "city": city['slug'],
            "service": service['slug'],
            "status": "ok",
            "word_count": qc["word_count"],
            "faq_count": qc["faq_count"],
            "density": qc["density"],
            "model": result['model']
        })

        # Rate limit: avoid hammer
        time.sleep(2.0)

    print(f"\n=== Done ===")
    print(f"Success/Generated: {stats['success']}")
    print(f"Policy rejected: {stats['policy_reject']}")
    print(f"Low quality (skipped): {stats['low_quality_retry']}")
    print(f"Error: {stats['error']}")

    # Save log
    log_path = ROOT / "data" / "bulk_generate_log.json"
    log_path.parent.mkdir(exist_ok=True)
    log_path.write_text(json.dumps(log, ensure_ascii=False, indent=2))
    print(f"Log saved to {log_path}")


if __name__ == "__main__":
    main()
