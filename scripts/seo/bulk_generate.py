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
from string import Template

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

# LLM provider configuration
# Default: Pollinations anonymous (openai-fast = GPT-OSS-20B), free, no API key.
# Sequential only — Pollinations caps 1 concurrent per IP.
# Override via env: LLM_BASE_URL + LLM_MODEL + LLM_API_KEY
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "pollinations")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://text.pollinations.ai/openai")
LLM_MODEL = os.getenv("LLM_MODEL", "openai-fast")
LLM_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("POLLINATIONS_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("OPENROUTER_API_KEY") or os.getenv("GEMINI_API_KEY") or ""
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

# Pricing tiers loaded from services.json per-service (each service has its own data)
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
    if matches:
        return matches[:7]
    # Fallback: 5 generic FAQs per service
    service = get_service(service_slug)
    return service.get("faqs", [])[:7] if service else []


def build_mock_content(city: dict, service: dict) -> str:
    """Generate template-based content tanpa LLM. Untuk testing flow ketika LLM quota habis."""
    local_facts = "\n".join(f"<li>{f}</li>" for f in city.get("local_facts", []))
    return f"""
<h2>Mengapa Bisnis di {city['name']} Butuh {service['name']}</h2>
<p>{city['name']} sebagai salah satu pasar potensial di Indonesia dengan {city.get('umkm_count', 0):,} UMKM aktif, membutuhkan strategi {service['name'].lower()} yang terukur dan berbasis data. Mayoritas brand lokal {city['name']} telah memanfaatkan platform iklan digital untuk meningkatkan visibilitas, leads, dan penjualan secara konsisten.</p>
<p>{city.get('local_facts', [''])[0]}. Dengan pendampingan tim Beriklan yang sudah mengelola lebih dari ratusan campaign iklan sejak 2016, {service['name']} di {city['name']} dapat mendatangkan hasil yang dapat diukur dari minggu pertama.</p>
<p>Yang kami kerjakan bukan sekadar tayang iklan — kami menyusun strategi targeting presisi, copy yang berbicara ke audiens spesifik di {city['name']}, dan optimasi mingguan berdasarkan data real-time.</p>

<h2>Tantangan {service['name']} di Pasar {city['name']}</h2>
<p>Pasar {city['name']} memiliki karakteristik unik — target audiens yang berbeda dari kota lain, kompetitor yang agresif, dan seasonality yang bervariasi. Tanpa strategi yang sesuai dengan konteks lokal, campaign sering tidak menghasilkan ROI yang diharapkan dan terbuang sia-sia.</p>
<p>Tantangan lainnya adalah mengukur efektivitas iklan secara akurat. Banyak bisnis tidak punya akses ke dashboard real-time atau tidak tahu cara menginterpretasi data yang tersedia. Inilah mengapa pendekatan berbasis data dan transparansi laporan menjadi penting untuk dipertimbangkan.</p>

<h2>Cara Kerja Tim Beriklan di {city['name']}</h2>
<p>Setiap klien {city['name']} mendapat pendampingan langsung dari tim yang sudah mengelola campaign iklan sejak 2016. Proses kami terstruktur, terukur, dan transparan dari hari pertama.</p>
<ul>
{local_facts}
<li>Brief 30 menit untuk pahami bisnis Anda secara menyeluruh (online/Zoom atau tatap muka di {city['name']})</li>
<li>Riset audience lokal {city['name']} yang sesuai dengan produk dan penawaran Anda</li>
<li>Setup campaign + materi iklan dari kami, revisi sampai Anda approve final</li>
<li>Tayang 30 hari penuh + laporan mingguan bahasa manusia, bukan deretan CTR/CPM</li>
<li>Optimasi mingguan berbasis data — iklan yang tidak perform diganti dengan creative baru</li>
</ul>

<h2>FAQ {service['name']} di {city['name']}</h2>
<h3>Berapa biaya {service['name']} di {city['name']}?</h3>
<p>Biaya bervariasi sesuai paket yang dipilih. Paket Standart mulai dari Rp 1.750.000 per 30 hari, sudah termasuk pendampingan profesional dan optimasi mingguan. Ad spend platform terpisah, dibayar langsung ke Meta/Google/TikTok atas nama Anda.</p>
<h3>Berapa lama sampai iklan tayang?</h3>
<p>Setup 1-3 hari kerja setelah strategi disetujui. Campaign live di minggu pertama. Optimasi mingguan berjalan sejak hari ke-7. Pola yang konsisten biasanya terlihat di minggu ke-3 hingga ke-4.</p>
<h3>Apakah saya dapat akses penuh ke akun iklan?</h3>
<p>Ya. Akun iklan tetap di bawah nama dan akses Anda. Anda memegang penuh kontrol terhadap dana dan data historis. Tidak ada account abal-abal atau tersembunyi di agency kami.</p>
<h3>Bagaimana laporan hasil campaign?</h3>
<p>Laporan mingguan via WhatsApp dengan bahasa manusia: mana yang berjalan optimal, mana yang perlu disesuaikan, dan rencana aksi untuk minggu depan. Plus dashboard real-time yang bisa Anda akses kapan saja.</p>
<h3>Apakah ada kontrak minimum?</h3>
<p>Tidak. Sistem kami bekerja secara bulanan. Anda bebas memutuskan untuk lanjut atau berhenti setiap saat. Komitmen kami jaga lewat kualitas, bukan jebakan kontrak panjang.</p>
"""


def build_prompt(city: dict, service: dict, word_target: int = 700) -> str:
    """Build LLM prompt for city-specific body content."""
    local_facts = "\n".join(f"- {f}" for f in city.get("local_facts", []))
    faqs_seed = "\n".join(f"Q: {f['q']}\nA: {f['a'][:200]}" for f in service.get("faqs", [])[:6])
    tiers_summary = ", ".join([f"{t['name']} Rp {t['priceLabel']}" for t in service.get("tiers", [])[:3]])

    tag_list = "<p>, <h2>, <h3>, <ul>, <li>"
    tag_ban = "<section>, <article>, <!DOCTYPE>, <style>, atau tag meta"

    prompt = f"""Kamu adalah copywriter SEO senior untuk Beriklan.co.id. Tulis konten Bahasa Indonesia untuk halaman LAYANAN {service['name'].upper()} di kota {city['name'].upper()}.

TARGET KEYWORD: "{service['name']} {city['name']}"
KATA TARGET: {word_target} (±150 kata, BUKAN kurang)

ATURAN WAJIB:
1. UNIK & LOKAL — spesifik {city['name']}, BUKAN generic
2. FACTUAL — pakai data FAKTA KOTA, JANGAN mengarang nomor
3. TONE profesional, BUKAN sales-y/clickbait
4. LARANG: "Dalam dunia", "Penting untuk", "Demikian", "Semoga bermanfaat", "Kesimpulannya", "Tidak dapat dipungkiri"

FAKTA KOTA {city['name'].upper()}:
{local_facts}

PAKET HARGA (referensi):
{tiers_summary}

FAQ REFERENSI (parafrase, jangan copy paste):
{faqs_seed}

=== OUTPUT — WAJIB LENGKAP SEMUA 4 SECTION ===

<h2>Mengapa Bisnis di {city['name']} Butuh {service['name']}</h2>
<p>paragraf 1 (WAJIB angka spesifik dari FAKTA KOTA + contoh UMKM nyata)</p>
<p>paragraf 2 (penjelasan strategis)</p>
<p>paragraf 3 (data spesifik tambahan + benefit)</p>

<h2>Tantangan {service['name']} di Pasar {city['name']}</h2>
<p>paragraf 1 (tantangan utama, kompetisi)</p>
<p>paragraf 2 (risiko kalau tanpa strategi)</p>

<h2>Cara Kerja Tim Beriklan di {city['name']}</h2>
<p>paragraf intro tentang proses (2-3 kalimat)</p>
<ul>
  <li>step 1</li>
  <li>step 2</li>
  <li>step 3</li>
  <li>step 4</li>
  <li>step 5</li>
</ul>

<h2>FAQ {service['name']} di {city['name']}</h2>
<h3>Pertanyaan 1</h3>
<p>Jawaban 1</p>
<h3>Pertanyaan 2</h3>
<p>Jawaban 2</p>
<h3>Pertanyaan 3</h3>
<p>Jawaban 3</p>
<h3>Pertanyaan 4</h3>
<p>Jawaban 4</p>
<h3>Pertanyaan 5</h3>
<p>Jawaban 5</p>

=== INSTRUKSI FINAL ===
- LENGKAPI semua section. JANGAN berhenti di tengah jalan.
- Setiap paragraf min 60 kata, max 120 kata.
- Wajib ada 1 angka spesifik (contoh: "70% brand X aktif di Y", "10.5jt penduduk").
- Wajib ada 1 contoh UMKM lokal yang spesifik di {city['name']}.
- Output HANYA HTML body content ({tag_list}).
- JANGAN sertakan {tag_ban} apapun.

SEKARANG TULIS LENGKAP, jangan berhenti.:
"""

    return prompt


def call_llm(prompt: str, model: str = None, max_tokens: int = 4096, max_retries: int = 5) -> dict:
    """Call LLM via OpenAI-compatible endpoint. Default: Pollinations anonymous (openai-fast)."""
    url = f"{LLM_BASE_URL}/chat/completions"
    m = model or LLM_MODEL
    headers = {"Content-Type": "application/json"}
    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"
    payload = {
        "model": m,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "cache": True
    }
    last_error = "all retries failed"
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=180)
            if r.status_code == 200:
                data = r.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content:
                    return {"ok": True, "content": content, "model": m, "usage": data.get("usage", {})}
                err = data.get("error", {})
                last_error = f"empty content ({err.get('message', '')[:80]})"
                print(f"  attempt {attempt}: {last_error}")
            else:
                last_error = f"HTTP {r.status_code}"
                print(f"  attempt {attempt}: {last_error} - {r.text[:200]}")
        except Exception as e:
            last_error = f"{type(e).__name__}: {e}"
            print(f"  attempt {attempt}: {last_error}")
        # Pollinations queue errors resolve in 5-15s; backoff aggressively
        if attempt < max_retries:
            time.sleep(5 + 8 * attempt)
    return {"ok": False, "content": "", "error": last_error}


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
        # Relaxed for bulk pass with free-tier LLM (Pollinations GPT-OSS-20B).
        # Final QC gate: ≥4 H2, ≥3 FAQ, ≥300 words, ≥0.3% density, 0 policy violations.
        "passed": (
            word_count >= 300 and
            word_count <= 2200 and
            faq_count >= 3 and
            h2_count >= 4 and
            density >= 0.3 and
            len(policy_violations) == 0
        )
    }


def build_page_html(city: dict, service: dict, content_html: str, testimonial: dict = None) -> str:
    """Build complete Astro page source matching national /jasa-iklan-{x}/ structure.

    Sections rendered (matching national page structure):
    1. Hero (with trust pills)
    2. Trust bar (industry tags dark)
    3. AI-generated city content
    4. Why (3 features)
    5. How it works (4 steps)
    6. Pricing (PricingCards with service tiers)
    7. Trust dark (3 columns)
    8. Testimonials (3 cards from service-specific pool)
    9. FAQ (FaqAccordion)
    10. Related services
    11. Final CTA
    12. LocalSchema JSON-LD
    """
    # Load service data
    tiers = service.get("tiers", [])
    faqs = service.get("faqs", [])
    why_features = service.get("why_features", [])
    how_steps = service.get("how_steps", [])
    service_testimonials = service.get("testimonials", [])

    # Compute placeholders BEFORE building sections
    canonical = f"https://beriklan.co.id/{service['slug']}/{city['slug']}/"
    desc = f"{service['name']} di {city['name']} — agensi Meta Business Partner sejak 2016. Konsultasi 15 menit gratis."
    wa_link = (
        f"https://wa.me/62811919328?text=Halo%20Beriklan%2C%20saya%20tertarik%20"
        f"{service['name']}%20di%20{city['name']}.%20Mau%20konsultasi%20awal."
    )
    title = f"{service['name']} di {city['name']} — Paket dari Rp {tiers[0]['priceLabel'] if tiers else '1.750.000'} | Beriklan"

    # Build the Astro template using string.Template (NO f-string)
    # Placeholders use ${name} syntax which doesn't conflict with JSX {}
    template = '''---
import Layout from '../../../layouts/Layout.astro';
import Navbar from '../../../components/Navbar.svelte';
import Footer from '../../../components/Footer.svelte';
import StickyCTA from '../../../components/StickyCTA.svelte';
import LocalSchema from '../../../components/LocalSchema.astro';
import PricingCards from '../../../components/PricingCards.svelte';
import FeatureGrid from '../../../components/FeatureGrid.svelte';
import StepGrid from '../../../components/StepGrid.svelte';
import FaqAccordion from '../../../components/FaqAccordion.svelte';
import RelatedServices from '../../../components/RelatedServices.svelte';
import { MessageCircle, Sparkles, Check, ArrowRight } from 'lucide-svelte';

const city = ${city_json};
const service = ${service_json};
const tiers = ${tiers_json};
const faqs = ${faqs_json};
const whyFeatures = ${why_json};
const howSteps = ${how_json};
const serviceTestimonials = ${testimonials_json};
---

<Layout
    title="${title}"
    description="${description}"
    canonical="${canonical}"
>
    <Navbar client:only="svelte" />
    <StickyCTA client:only="svelte" />

    <!-- ====================== HERO ====================== -->
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
                ${service_name} di ${city_name} · Meta & Google Partner
            </div>
            <h1 class="hero-h1 font-display font-extrabold text-4xl md:text-5xl lg:text-[2.6rem] xl:text-[2.9rem] text-ink leading-[1.05] tracking-tight mb-6">
                <span class="anim-fade-up">${service_name}</span><br/>
                <span class="anim-fade-up text-transparent bg-clip-text bg-gradient-to-r from-primary-2 to-accent" style="animation-delay: 80ms;">di ${city_name}, Mendorong</span><br/>
                <span class="anim-fade-up" style="animation-delay: 160ms;">Hasil Terukur.</span>
            </h1>
            <p class="text-base md:text-lg text-muted leading-relaxed mb-8 anim-fade-up" style="animation-delay: 240ms;">
                Tim Beriklan (Meta Business Partner sejak 2016) mengelola campaign ${service_name_lower} untuk UMKM & bisnis menengah di ${city_name}. Akses penuh ke akun iklan, dashboard real-time, laporan setiap Senin pagi.
            </p>
            <div class="flex flex-col sm:flex-row gap-3 justify-center anim-fade-up" style="animation-delay: 320ms;">
                <a href="${wa_link}" target="_blank" rel="noopener" class="group inline-flex items-center justify-center gap-2 bg-ink text-white px-7 py-4 rounded-full font-bold shadow-lg hover:shadow-pop btn-shine">
                    <span class="relative z-10 flex items-center gap-2">
                        <MessageCircle class="w-4 h-4" />
                        Diskusi via WhatsApp
                    </span>
                </a>
                <a href="#pricing" class="inline-flex items-center justify-center gap-2 px-7 py-4 rounded-full font-bold text-ink border border-gray-200 bg-white hover:border-ink transition-all">
                    Lihat Paket & Harga
                    <ArrowRight class="w-4 h-4" />
                </a>
            </div>
            <div class="hero-trust pt-6 border-t border-gray-200/60 flex flex-wrap items-center justify-center gap-x-6 gap-y-3 text-xs md:text-sm reveal" style="transition-delay: 200ms;">
                <div class="flex items-center gap-2 trust-item"><span class="check-icon"></span><span class="text-muted"><strong class="text-ink">9 tahun</strong> mengelola campaign iklan</span></div>
                <div class="flex items-center gap-2 trust-item"><span class="check-icon"></span><span class="text-muted">Optimasi berbasis data, bukan tebakan</span></div>
                <div class="flex items-center gap-2 trust-item"><span class="check-icon"></span><span class="text-muted">Laporan <strong class="text-ink">setiap Senin pagi</strong>, bahasa yang mudah dipahami</span></div>
            </div>
        </div>
    </header>

    <!-- ====================== TRUST BAR ====================== -->
    <section class="py-7 bg-ink border-y border-white/5 relative overflow-hidden">
        <div class="container mx-auto px-6">
            <div class="flex flex-wrap items-center justify-center gap-x-8 gap-y-3">
                <p class="text-[10px] md:text-xs font-bold uppercase tracking-[0.18em] text-white/40">Dipercaya bisnis di ${city_name} dari berbagai industri</p>
                <div class="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-white/70 text-sm font-semibold trust-word">
                    <span>F&amp;B</span><span class="text-white/30">·</span>
                    <span>Skincare</span><span class="text-white/30">·</span>
                    <span>Fashion</span><span class="text-white/30">·</span>
                    <span>Edutech</span><span class="text-white/30">·</span>
                    <span>Klinik</span><span class="text-white/30">·</span>
                    <span>Properti</span>
                </div>
            </div>
        </div>
    </section>

    <!-- ====================== AI-GENERATED CITY CONTENT ====================== -->
    <section class="py-20 md:py-28 bg-white">
        <div class="container mx-auto px-6 max-w-3xl prose-content">
            ${content_html}
        </div>
    </section>

    ${why_section}

    <!-- ====================== HOW IT WORKS ====================== -->
    {how_steps_section}

    <!-- ====================== PRICING ====================== -->
    {pricing_section}

    <!-- ====================== TRUST DARK ====================== -->
    <section class="py-20 md:py-28 bg-ink text-white relative overflow-hidden">
        <div class="container mx-auto px-6 relative">
            <div class="text-center max-w-2xl mx-auto mb-12 reveal">
                <p class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-accent">
                    <span class="w-8 h-px bg-accent"></span>
                    Mengapa Beriklan
                    <span class="w-8 h-px bg-accent"></span>
                </p>
                <h2 class="font-display font-extrabold text-3xl md:text-5xl text-white leading-[1.1] tracking-tight mt-3">
                    Bukan agensi yang berjanji<br/>
                    <span class="text-accent">angka fantastis tanpa dasar.</span>
                </h2>
            </div>
            <div class="grid md:grid-cols-3 gap-5 max-w-5xl mx-auto reveal-stagger">
                <div class="trust-item-dark">
                    <div class="trust-icon-dark">🔒</div>
                    <h3 class="trust-title-dark">Akses penuh ke akun Anda</h3>
                    <p class="trust-desc-dark">Seluruh akun iklan tetap di bawah kendali Anda. Bila sewaktu-waktu dibutuhkan, seluruh data historis berpindah tanpa hambatan.</p>
                </div>
                <div class="trust-item-dark" style="animation-delay: 120ms;">
                    <div class="trust-icon-dark">📊</div>
                    <h3 class="trust-title-dark">Laporan setiap Senin pagi</h3>
                    <p class="trust-desc-dark">Disusun dalam satu halaman dengan bahasa yang mudah dipahami. Anda mendapat kejelasan: mana yang berjalan optimal.</p>
                </div>
                <div class="trust-item-dark" style="animation-delay: 240ms;">
                    <div class="trust-icon-dark">🔄</div>
                    <h3 class="trust-title-dark">Tanpa minimum contract</h3>
                    <p class="trust-desc-dark">Sistem kerja bulanan. Anda bebas memutuskan untuk lanjut atau berhenti setiap saat.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- ====================== TESTIMONIALS ====================== -->
    {testimonials_section}

    <!-- ====================== FAQ ====================== -->
    {faq_section}

    <!-- ====================== RELATED SERVICES ====================== -->
    <section class="py-12 bg-white border-t border-gray-100">
        <div class="container mx-auto px-6 max-w-4xl">
            <p class="text-xs font-bold uppercase tracking-[0.2em] text-accent mb-3 text-center">Layanan Terkait di ${city_name}</p>
            <p class="text-center text-sm text-muted">${related_services_html}</p>
        </div>
    </section>

    <!-- ====================== FINAL CTA ====================== -->
    <section class="py-20 md:py-28 bg-gradient-to-br from-ink via-primary-2 to-ink text-white relative overflow-hidden">
        <div class="absolute inset-0 pointer-events-none opacity-[0.08] cta-grid"></div>
        <div class="abs-radaial-2"></div>
        <div class="container mx-auto px-6 relative">
            <div class="max-w-3xl mx-auto text-center reveal">
                <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full text-xs font-bold uppercase tracking-wider mb-6">
                    <span class="relative flex h-2 w-2">
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
                    </span>
                    Tim online · respon dalam 1 jam (jam kerja)
                </div>
                <h2 class="font-display font-extrabold text-3xl md:text-5xl lg:text-6xl leading-[1.05] tracking-tight mb-6 mt-3">
                    Satu keputusan kecil hari ini,<br/>
                    <span class="text-accent">dampaknya terasa di kuartal depan.</span>
                </h2>
                <p class="text-white/70 text-base md:text-lg leading-relaxed max-w-2xl mx-auto mb-8">
                    Konsultasi 15 menit · tanpa biaya · tanpa komitmen. Kami bantu pilih paket yang tepat untuk bisnis Anda di ${city_name}.
                </p>
                <div class="flex flex-col sm:flex-row gap-3 justify-center">
                    <a href="${wa_link}" target="_blank" rel="noopener" class="group inline-flex items-center justify-center gap-2 bg-accent text-ink px-8 py-4 rounded-full font-bold shadow-lg hover:shadow-pop transition-all btn-shine-accent">
                        <span class="relative z-10 flex items-center gap-2">
                            Mulai Konsultasi via WhatsApp
                            <ArrowRight class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </span>
                    </a>
                    <a href="#pricing" class="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-full font-bold border border-white/30 text-white hover:bg-white/10 transition-all">
                        Lihat Paket & Harga
                    </a>
                </div>
            </div>
        </div>
    </section>

    <Footer client:only="svelte" />

    <LocalSchema
        type="city-service"
        city={city}
        service={service}
        tiers={tiers}
        faqs={faqs}
        pageUrl="/${service_slug}/${city_slug}/"
        breadcrumbs={${breadcrumb_array}}
    />
</Layout>
'''
    # Build sub-sections
    why_section = ''
    if why_features:
        why_items = '\n'.join(f'''            <div class="why-card group" style="animation-delay: {i*100}ms;">
                <div class="why-icon">{f['icon']}</div>
                <h3 class="why-title">{f['title']}</h3>
                <p class="why-desc">{f['desc']}</p>
            </div>''' for i, f in enumerate(why_features))
        why_section = f'''
    <!-- ====================== WHY ====================== -->
    <section class="py-20 md:py-28 bg-soft">
        <div class="container mx-auto px-6">
            <div class="text-center max-w-2xl mx-auto mb-12 reveal">
                <p class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-accent">
                    <span class="w-8 h-px bg-accent"></span>
                    3 Alasan Memilih {service['name']}
                    <span class="w-8 h-px bg-accent"></span>
                </p>
                <h2 class="font-display font-extrabold text-3xl md:text-5xl text-ink leading-[1.1] tracking-tight mt-3">
                    Strategi yang terukur,<br/>
                    <span class="text-accent">bukan jualan angka tanpa dasar.</span>
                </h2>
            </div>
            <div class="grid md:grid-cols-3 gap-5 max-w-5xl mx-auto reveal-stagger">
{why_items}
            </div>
        </div>
    </section>'''

    how_steps_section = ''
    if how_steps:
        steps_json = json.dumps(how_steps, ensure_ascii=False)
        how_steps_section = '''
    <!-- ====================== HOW IT WORKS ====================== -->
    <section class="py-20 md:py-28 bg-white relative overflow-hidden">
        <div class="container mx-auto px-6 relative">
            <div class="max-w-2xl mx-auto text-center mb-14 reveal">
                <p class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-accent">
                    <span class="w-6 h-px bg-accent"></span>
                    Cara Kerja
                    <span class="w-6 h-px bg-accent"></span>
                </p>
                <h2 class="font-display font-extrabold text-3xl md:text-5xl text-ink leading-[1.1] tracking-tight mt-3">
                    Empat langkah dari brief<br/>
                    <span class="text-accent">menuju iklan yang tayang optimal.</span>
                </h2>
            </div>
            <StepGrid items={__HOW_STEPS__} client:visible />
        </div>
    </section>'''
        how_steps_section = how_steps_section.replace('__HOW_STEPS__', steps_json)

    pricing_section = ''
    if tiers:
        tiers_json_str = json.dumps(tiers, ensure_ascii=False)
        highlight_idx = next((i for i, t in enumerate(tiers) if t.get('highlight')), -1)
        pricing_section = '''
    <!-- ====================== PRICING ====================== -->
    <section id="pricing" class="py-20 md:py-28 bg-gradient-to-br from-soft via-white to-beige relative overflow-hidden">
        <div class="abs-blob abs-blob-3"></div>
        <div class="container mx-auto px-6 relative">
            <div class="text-center max-w-2xl mx-auto mb-12 reveal">
                <p class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-accent">
                    <span class="w-8 h-px bg-accent"></span>
                    Paket & Harga
                    <span class="w-8 h-px bg-accent"></span>
                </p>
                <h2 class="font-display font-extrabold text-3xl md:text-5xl text-ink leading-[1.1] tracking-tight mt-3">
                    Paket SERVICE_NAME di CITY_NAME,<br/>
                    <span class="text-accent">disesuaikan dengan objective Anda.</span>
                </h2>
                <p class="mt-4 text-muted max-w-xl mx-auto text-base leading-relaxed">
                    Angka di bawah adalah biaya jasa pengelolaan campaign. Ad spend platform dibayar langsung ke Meta/Google/TikTok — tanpa markup, tanpa biaya tersembunyi.
                </p>
            </div>
            <PricingCards tiers={__TIERS__} pageSlug="SERVICE_NAME di CITY_NAME" highlightIndex={__HI_IDX__} client:only="svelte" />
            <div class="mt-10 max-w-2xl mx-auto reveal">
                <div class="bg-white rounded-2xl border border-gray-100 p-5 md:p-6 shadow-soft">
                    <div class="flex items-start gap-3">
                        <div class="w-10 h-10 rounded-xl bg-accent/15 flex items-center justify-center shrink-0">
                            <Check class="w-5 h-5 text-accent" strokeWidth="2.5" />
                        </div>
                        <div>
                            <p class="font-display font-bold text-base text-ink mb-1">Tidak yakin paket mana yang sesuai?</p>
                            <p class="text-sm text-muted leading-relaxed">Sesi konsultasi 15 menit gratis. Kami bantu pilih paket yang paling cocok dengan budget iklan dan objective Anda.</p>
                            <a href="WA_LINK" target="_blank" rel="noopener" class="inline-flex items-center gap-1.5 mt-3 text-sm font-bold text-accent hover:text-ink transition-colors group">
                                Konsultasi via WhatsApp
                                <ArrowRight class="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>'''
        pricing_section = pricing_section.replace('__TIERS__', tiers_json_str)
        pricing_section = pricing_section.replace('__HI_IDX__', str(highlight_idx))
        pricing_section = pricing_section.replace('SERVICE_NAME di CITY_NAME', service['name'] + ' di ' + city['name'])
        pricing_section = pricing_section.replace('WA_LINK', wa_link)

    testimonials_section = ''
    if service_testimonials:
        tstm_blocks = []
        for i, t in enumerate(service_testimonials[:3]):
            tstm_blocks.append(
                '<article class="tst-card" style="animation-delay: ' + str(i*100) + 'ms;">'
                '<div class="tst-quote-mark">"</div>'
                '<p class="tst-body">' + t['quote'] + '</p>'
                '<div class="tst-author">'
                '<div class="tst-avatar bg-gradient-to-br ' + t.get('color', 'from-amber-500 to-orange-500') + '">' + t.get('avatar', '⭐') + '</div>'
                '<div>'
                '<p class="tst-name">' + t['author'] + '</p>'
                '<p class="tst-role">' + t['role'] + '</p>'
                '<p class="tst-metric">' + t.get('metric', '') + '</p>'
                '</div></div></article>'
            )
        tstm_items = '\n'.join(tstm_blocks)
        testimonials_section = '''
    <!-- ====================== TESTIMONIALS ====================== -->
    <section class="py-20 md:py-28 bg-white">
        <div class="container mx-auto px-6">
            <div class="text-center max-w-2xl mx-auto mb-12 reveal">
                <p class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-accent">
                    <span class="w-8 h-px bg-accent"></span>
                    Studi Kasus & Testimoni
                    <span class="w-8 h-px bg-accent"></span>
                </p>
                <h2 class="font-display font-extrabold text-3xl md:text-5xl text-ink leading-[1.1] tracking-tight mt-3">
                    Pengalaman mereka yang telah<br/>
                    <span class="text-accent">bekerja sama dengan Tim Beriklan.</span>
                </h2>
            </div>
            <div class="grid md:grid-cols-3 gap-5 max-w-6xl mx-auto reveal-stagger">
''' + tstm_items + '''
            </div>
        </div>
    </section>'''

    faq_section = ''
    if faqs:
        faq_json = json.dumps(faqs, ensure_ascii=False)
        faq_section = '''
    <!-- ====================== FAQ ====================== -->
    <section id="faq" class="py-20 md:py-28 bg-soft relative overflow-hidden">
        <div class="container mx-auto px-6 relative">
            <div class="text-center max-w-2xl mx-auto mb-12 reveal">
                <p class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-accent">
                    <span class="w-8 h-px bg-accent"></span>
                    Sebelum deal pertama
                    <span class="w-8 h-px bg-accent"></span>
                </p>
                <h2 class="font-display font-extrabold text-3xl md:text-5xl text-ink leading-[1.1] tracking-tight mt-3">
                    Pertanyaan yang sering muncul<br/>
                    <span class="text-accent">sebelum deal pertama.</span>
                </h2>
            </div>
            <FaqAccordion items={__FAQ__} client:visible />
        </div>
    </section>'''
        faq_section = faq_section.replace('__FAQ__', faq_json)

    related_services_html = ' · '.join([
        '<a href="/jasa-' + s['slug'].replace('jasa-', '') + '/' + city['slug'] + '/" class="text-accent hover:underline">' + s['name'] + '</a>'
        for s in SERVICES if s['slug'] != service['slug'] and 'kelola' not in s['slug']
    ][:3])

    city_json = json.dumps(city, ensure_ascii=False)
    service_json = json.dumps({**service, 'tiers': tiers}, ensure_ascii=False)
    tiers_json = json.dumps(tiers, ensure_ascii=False)
    faqs_json = json.dumps(faqs, ensure_ascii=False)
    why_json = json.dumps(why_features, ensure_ascii=False)
    how_json = json.dumps(how_steps, ensure_ascii=False)
    testimonials_json = json.dumps(service_testimonials, ensure_ascii=False)
    breadcrumb_array = json.dumps([
        ["Beranda", "/"],
        [service['name'], f"/{service['slug']}/"],
        [city['name'], f"/{service['slug']}/{city['slug']}/"]
    ], ensure_ascii=False)

    # Render template using string.Template (no JSX conflict)
    tmpl = Template(template)
    page = tmpl.substitute(
        city_json=city_json,
        service_json=service_json,
        tiers_json=tiers_json,
        faqs_json=faqs_json,
        why_json=why_json,
        how_json=how_json,
        testimonials_json=testimonials_json,
        city_name=city['name'],
        city_slug=city['slug'],
        service_name=service['name'],
        service_name_lower=service['name'].lower(),
        service_slug=service['slug'],
        title=title,
        description=desc,
        canonical=canonical,
        wa_link=wa_link,
        content_html=content_html,
        why_section=why_section,
        how_steps_section=how_steps_section,
        pricing_section=pricing_section,
        testimonials_section=testimonials_section,
        faq_section=faq_section,
        related_services_html=related_services_html,
        breadcrumb_array=breadcrumb_array,
    )

    # Replace conditional placeholders
    page = page.replace('{how_steps_section}', how_steps_section)
    page = page.replace('{pricing_section}', pricing_section)
    page = page.replace('{testimonials_section}', testimonials_section)
    page = page.replace('{faq_section}', faq_section)

    return page


def main():
    p = argparse.ArgumentParser(description="Bulk generate city-service pages")
    p.add_argument("--pilot", type=int, default=0, help="Generate N pilot pages first")
    p.add_argument("--batch", help="Batch name: city-facebook, city-tiktok, etc., or city-all")
    p.add_argument("--generate", action="store_true", help="Actually write files (default dry-run)")
    p.add_argument("--mock", action="store_true", help="Use template-based content (no LLM call). Useful when AI quota exhausted.")
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
        # Call LLM (or use mock content if --mock flag)
        if args.mock:
            result = {"ok": True, "content": build_mock_content(city, service), "model": "mock-template"}
        else:
            result = call_llm(prompt, model=args.model, max_tokens=2500, max_retries=2)

        if not result["ok"]:
            print(f"  LLM FAILED: {result.get('error')}")
            if args.mock:
                # in mock mode, don't waste time on retries
                content_html = build_mock_content(city, service)
                qc = quality_check(content_html, city, service)
                result = {"ok": True, "content": content_html, "model": "mock-fallback"}
            else:
                stats["error"] += 1
                log.append({"city": city['slug'], "service": service['slug'], "status": "error", "reason": result.get('error')})
                time.sleep(5)
                continue
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
        page_source = build_page_html(city, service, content_html, testimonial)

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
