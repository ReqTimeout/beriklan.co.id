#!/usr/bin/env python3
"""
Generate city pages for the 3 missing services (jasa-kelola-instagram,
jasa-kelola-tiktok, jasa-pembuatan-website) × 24 cities = 72 pages.

Uses jasa-iklan-google/medan/index.astro as a template (same design),
substitutes per-service data (tiers, why_features, how_steps, faqs, page
title/description) and per-city data (name, slug, local_facts, WA text).
City AI content reuses the existing city-content.json entry (rendered
via set:html={cityContentMap[...]}) so we don't re-generate.

Usage:
  python3 scripts/gen_missing_city_pages.py            # generate all 72
  python3 scripts/gen_missing_city_pages.py --dry     # just print plan
"""
import argparse
import json
import os
import re
import sys

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(WEB, "src/pages/jasa-iklan-google/medan/index.astro")
CITIES = os.path.join(WEB, "src/data/cities.json")
CONTENT = os.path.join(WEB, "src/data/city-content.json")

# 24 cities — real Indonesian cities. International (brunei, kuala-lumpur, malaysia,
# singapore, singapura) are excluded intentionally (foreign/duplicate markets).
CITIES_USE = [
    "aceh", "bali", "bandung", "batam", "bekasi", "bogor", "cimahi",
    "denpasar", "depok", "jakarta", "jogja", "lampung", "lombok", "makassar",
    "malang", "medan", "padang", "palembang", "pontianak", "semarang",
    "sidoarjo", "solo", "surabaya", "tangerang", "yogyakarta",
]  # 25 cities
assert len(CITIES_USE) == 25

# All 10 services — the generator skips pages that already exist, so re-running
# safely fills only the missing city x service combinations (e.g. jakarta/makassar/
# sidoarjo across services that didn't have them yet).
MISSING_SERVICES = [
    "jasa-digital-marketing", "jasa-iklan-facebook", "jasa-iklan-instagram",
    "jasa-iklan-tiktok", "jasa-iklan-google", "jasa-iklan-youtube",
    "jasa-kelola-instagram", "jasa-kelola-tiktok",
    "jasa-pembuatan-website", "jasa-pembuatan-landing-page",
]

# Per-service content (tiers, why, how, faqs) — copy-paste quality, real data
SERVICE_DATA = {
    "jasa-kelola-instagram": {
        "name": "Jasa Kelola Instagram",
        "category": "organic",
        "eyebrow": "Manajemen Instagram · Bandung · Sejak 2016",
        "tiers": [
            {"name": "Starter", "priceLabel": "2.500.000", "duration": "30 hari", "tagline": "Untuk akun baru yang butuh ritme posting dan identitas visual konsisten.", "features": ["12 posting + 30 story/bulan", "Content calendar bulanan", "Copywriting original Bahasa Indonesia", "Design graphic custom (template branded)", "Hashtag research & optimization", "Laporan bulanan via WhatsApp"], "priceNote": "belum termasuk ad spend boost opsional", "disclaimer": "Minimum 3 bulan untuk hasil optimal."},
            {"name": "Growth", "priceLabel": "4.500.000", "duration": "30 hari", "highlight": True, "tagline": "Untuk akun aktif yang ingin naik follower dan engagement rate signifikan.", "features": ["16 posting + 60 story/bulan", "4 reels editing + captioning", "Community management (reply DM + comment)", "Monthly analytics & strategy review", "Kolaborasi micro-influencer lokal (opsional)", "Laporan mingguan via WhatsApp"], "priceNote": "belum termasuk ad spend boost opsional", "disclaimer": "Minimum 3 bulan."},
            {"name": "Premium", "priceLabel": "7.500.000", "duration": "30 hari", "tagline": "Untuk brand yang butuh produksi konten full-service + brand building.", "features": ["20 posting + 90 story + 8 reels/bulan", "Full production: 2× shooting on-location/bulan", "Dedicated content manager", "Brand guidelines update", "Ads creative support untuk tim paid ads", "Laporan mingguan + review bulanan video call"], "priceNote": "belum termasuk ad spend", "disclaimer": "Minimum 3 bulan."},
        ],
        "why_features": [
            {"icon": "🎨", "title": "Konsistensi Visual", "desc": "Feed Instagram Anda terlihat profesional dan kohesif, membangun trust audiens lokal yang scroll cepat di mobile."},
            {"icon": "📈", "title": "Pertumbuhan Organik", "desc": "Follower dan engagement tumbuh dari konten yang relevan, bukan dari beli followers. Audiens berkualitas untuk conversion."},
            {"icon": "💬", "title": "Komunitas Aktif", "desc": "DM dan comment dijawab dengan tone of voice brand — bukan template. Membangun hubungan yang menghasilkan closing."},
        ],
        "how_steps": [
            {"num": "01", "tag": "MINGGU 1", "title": "Brief & Audit", "desc": "Diskusi 60 menit untuk memahami brand voice, target audience lokal, dan objective (engagement vs conversion)."},
            {"num": "02", "tag": "MINGGU 2", "title": "Content Plan", "desc": "Susun content calendar 30 hari: tema mingguan, jenis konten, caption, hashtag strategy, dan asset brief."},
            {"num": "03", "tag": "MINGGU 3+", "title": "Eksekusi & Post", "desc": "Posting sesuai jadwal, reply DM/comment dalam 2 jam kerja, monitor performa harian."},
            {"num": "04", "tag": "BULANAN", "title": "Review & Pivot", "desc": "Laporan bulanan dengan insight actionable. Adjust strategi untuk bulan berikutnya."},
        ],
        "faqs": [
            {"q": "Berapa biaya Jasa Kelola Instagram bulanan?", "a": "Paket mulai Rp 2,5jt/bulan untuk 12 posting + 30 story. Paket Growth Rp 4,5jt include reels dan community management. Paket Premium Rp 7,5jt include produksi on-location."},
            {"q": "Berapa posting per minggu?", "a": "Tergantung paket: 3-5 posting/minggu untuk akun reguler, 4-5 posting/minggu untuk akun aktif Growth. Kami sesuaikan dengan ritme niche Anda."},
            {"q": "Apakah konten original?", "a": "Ya. Copywriting original Bahasa Indonesia, design kustom sesuai brand guidelines, foto/video dari stock library gratis atau shooting opsional berbayar."},
            {"q": "Bagaimana laporan bulanan?", "a": "Laporan via WhatsApp/email setiap awal bulan dengan metric reach, engagement, follower growth, top-performing content, dan rekomendasi strategi bulan depan."},
            {"q": "Berapa lama kontrak minimum?", "a": "Minimum 3 bulan untuk hasil optimal (Instagram adalah marathon, bukan sprint). Setelah 3 bulan, evaluasi bulanan dengan opsi break dengan notice 30 hari."},
        ],
    },
    "jasa-kelola-tiktok": {
        "name": "Jasa Kelola TikTok",
        "category": "organic",
        "eyebrow": "Manajemen TikTok · Bandung · Sejak 2016",
        "tiers": [
            {"name": "Starter", "priceLabel": "2.500.000", "duration": "30 hari", "tagline": "Untuk akun baru yang ingin mulai viral di FYP dengan konten yang relevan.", "features": ["12 video pendek (15-30 detik)", "Script writing + hashtag research", "Editing dengan caption & sound trending", "Posting 3-4×/minggu", "Laporan bulanan via WhatsApp"], "priceNote": "belum termasuk talent fee / shooting on-location", "disclaimer": "Minimum 3 bulan."},
            {"name": "Growth", "priceLabel": "4.500.000", "duration": "30 hari", "highlight": True, "tagline": "Untuk akun aktif yang target masuk FYP dan membangun komunitas organik.", "features": ["16 video pendek + 4× live session", "Riset trending sound + format mingguan", "Reply komentar + DM community management", "Kolaborasi dengan kreator lokal (opsional)", "Laporan mingguan dengan insight performa"], "priceNote": "belum termasuk talent fee opsional", "disclaimer": "Minimum 3 bulan."},
            {"name": "Premium", "priceLabel": "7.500.000", "duration": "30 hari", "tagline": "Untuk brand yang butuh full production team + strategi TikTok end-to-end.", "features": ["20 video + 8× live session + shooting on-location 2×/bulan", "Dedicated content strategist", "TikTok Shop integration (opsional)", "Ads creative support", "Laporan mingguan + review bulanan video call"], "priceNote": "belum termasuk ad spend Spark Ads", "disclaimer": "Minimum 3 bulan."},
        ],
        "why_features": [
            {"icon": "🎬", "title": "FYP-First Content", "desc": "Konten dioptimasi untuk algoritma FYP TikTok: hook 3 detik, sound trending, dan pattern yang memicu watch-time."},
            {"icon": "📊", "title": "Data-Driven Iteration", "desc": "Setiap video diukur (view, watch-time, share). Yang perform, di-boost. Yang tidak, di-recycle menjadi konten baru."},
            {"icon": "🤝", "title": "Authentic Brand Voice", "desc": "TikTok audiens benci konten corporate. Kami bantu brand Anda terdengar manusia, bukan iklan berjalan."},
        ],
        "how_steps": [
            {"num": "01", "tag": "MINGGU 1", "title": "Onboarding & Riset", "desc": "Analisis akun existing, kompetitor, dan trending topics di niche. Tentukan content pillars (3-5 tema inti)."},
            {"num": "02", "tag": "MINGGU 2", "title": "Produksi Batch", "desc": "Shooting batch 8-12 video sekaligus (efisien). Edit + caption + sound selection."},
            {"num": "03", "tag": "MINGGU 3+", "title": "Posting & Optimize", "desc": "Posting 3-5×/minggu di jam prime (11.00-13.00 & 19.00-22.00 WIB). Monitor performa 24 jam pertama."},
            {"num": "04", "tag": "BULANAN", "title": "Review & Scale", "desc": "Identifikasi 3-5 video top performer. Buat pattern/template serupa untuk double down di bulan depan."},
        ],
        "faqs": [
            {"q": "Berapa biaya Jasa Kelola TikTok bulanan?", "a": "Paket mulai Rp 2,5jt/bulan untuk 12 video pendek. Paket Growth Rp 4,5jt include live session dan community management. Premium Rp 7,5jt include produksi on-location."},
            {"q": "Berapa video per minggu?", "a": "3-5 video per minggu tergantung paket. Untuk akun baru, kami rekomendasikan 3×/minggu konsisten selama 60 hari pertama untuk melatih algoritma."},
            {"q": "Apakah perlu tampil di depan kamera?", "a": "Tidak wajib. Kami bisa produksi konten tanpa wajah (text-on-screen, B-roll, voiceover, atau AI avatar). Tapi konten dengan wajah asli biasanya perform 2-3× lebih baik."},
            {"q": "Bagaimana laporan bulanan?", "a": "Laporan via WhatsApp/email setiap awal bulan: total views, watch-time rata-rata, top 5 video, follower growth, dan rekomendasi strategi bulan depan."},
            {"q": "Berapa lama sampai viral?", "a": "Tidak ada jaminan viral. Tapi dengan ritme posting konsisten + pattern yang teruji, mayoritas akun kami mencapai 100K+ views/bulan di bulan ke-2 atau ke-3."},
        ],
    },
    "jasa-pembuatan-website": {
        "name": "Jasa Pembuatan Website",
        "category": "build",
        "eyebrow": "Pembuatan Website · Custom & CMS · Bandung",
        "tiers": [
            {"name": "Landing Page", "priceLabel": "3.000.000", "duration": "5-7 hari kerja", "tagline": "Untuk campaign Meta/Google Ads atau promo spesifik yang butuh halaman konversi dedicated.", "features": ["1 halaman custom (mobile responsive)", "Form integrasi WhatsApp + Email", "Meta Pixel + Google Tag setup", "SSL + domain .co.id/.id (1 tahun)", "Loading speed < 3 detik", "Revisi 2×"], "priceNote": "include domain + hosting 1 tahun", "disclaimer": "Sekali bayar, source code menjadi milik Anda."},
            {"name": "Company Profile", "priceLabel": "8.000.000", "duration": "14-21 hari kerja", "highlight": True, "tagline": "Untuk bisnis yang butuh website profesional multi-halaman dengan CMS untuk update rutin.", "features": ["5-7 halaman (Home, About, Services, Blog, Contact)", "CMS WordPress / Headless", "Design custom sesuai brand", "SEO on-page dasar (title, meta, schema)", "Blog integration (untuk content marketing)", "Training update website (2 jam)", "Revisi 3×"], "priceNote": "include domain + hosting 1 tahun", "disclaimer": "Maintenance bulanan opsional Rp 500rb."},
            {"name": "Toko Online", "priceLabel": "18.000.000", "duration": "21-30 hari kerja", "tagline": "Untuk bisnis yang butuh e-commerce lengkap dengan payment gateway dan shipping integration.", "features": ["Katalog produk unlimited", "Payment gateway (Midtrans/Xendit)", "Shipping API (JNE/J&T/SiCepat)", "Admin dashboard untuk order management", "Customer account + order tracking", "Integrasi Meta Pixel + Google Analytics", "Training tim (4 jam)", "Revisi 3× + support 30 hari"], "priceNote": "include domain + hosting 1 tahun, tidak termasuk payment gateway fee", "disclaimer": "Maintenance bulanan opsional Rp 1jt."},
        ],
        "why_features": [
            {"icon": "🎯", "title": "Conversion-First", "desc": "Website yang kami bangun dirancang untuk konversi: tombol CTA jelas, loading cepat, mobile responsive, dan tracking akurat."},
            {"icon": "⚡", "title": "Performance Optimal", "desc": "PageSpeed score 90+ di mobile, hosting managed Indonesia (latency rendah), SSL + CDN gratis."},
            {"icon": "🔧", "title": "Mudah Update", "desc": "CMS WordPress atau Headless CMS (konten marketing friendly). Anda update sendiri tanpa harus hubungi developer."},
        ],
        "how_steps": [
            {"num": "01", "tag": "MINGGU 1", "title": "Brief & Wireframe", "desc": "Diskusi 90 menit: tujuan website, target audience, halaman yang dibutuhkan, dan referensi design."},
            {"num": "02", "tag": "MINGGU 2-3", "title": "Design & Build", "desc": "Mockup design → approval → development. CMS setup, integrasi payment/tracking, dan content population."},
            {"num": "03", "tag": "MINGGU 3-4", "title": "Testing & Launch", "desc": "Cross-browser testing, mobile testing, speed test, security audit. Launch + monitoring 7 hari pertama."},
            {"num": "04", "tag": "ONGOING", "title": "Support & Maintenance", "desc": "Support teknis via WhatsApp. Maintenance opsional: update konten, security patch, backup bulanan."},
        ],
        "faqs": [
            {"q": "Berapa biaya Jasa Pembuatan Website?", "a": "Landing page mulai Rp 3jt, company profile Rp 8jt, toko online Rp 18jt. Custom (multi-bahasa, membership, dll) di-quote terpisah."},
            {"q": "Berapa lama pengerjaan?", "a": "Landing page 5-7 hari, company profile 14-21 hari, toko online 21-30 hari. Revisi 2-3× included sebelum launch."},
            {"q": "Apakah include domain dan hosting?", "a": "Ya, include 1 tahun. Domain .co.id/.id/.com. Hosting managed Indonesia (SSD, SSL gratis, CDN, backup harian)."},
            {"q": "Maintenance setelah launch?", "a": "Opsional. Landing page tidak perlu maintenance. Company profile Rp 500rb/bulan. Toko online Rp 1jt/bulan. Include update konten, security patch, backup."},
            {"q": "CMS atau static?", "a": "Tergantung: untuk update rutin (blog, news) pakai WordPress atau Headless CMS. Untuk performance maksimal (landing page campaign) pakai static (Astro/Next.js)."},
        ],
    },
}


def _replace_balanced(text: str, marker: str, replacement: str) -> str:
    """Replace from `marker` to its matching closing bracket.

    Handles nested {} and [] correctly. Returns text with the first match replaced.
    Detects the opening bracket from the char immediately after the marker.
    """
    idx = text.find(marker)
    if idx == -1:
        return text
    start = idx + len(marker)
    # skip whitespace to find the opening bracket
    i = start
    while i < len(text) and text[i] in " \t":
        i += 1
    if i >= len(text) or text[i] not in "{[":
        return text
    open_ch = text[i]
    close_ch = "}" if open_ch == "{" else "]"
    depth = 1
    j = i + 1
    while j < len(text) and depth > 0:
        c = text[j]
        if c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
        j += 1
    if depth != 0:
        return text
    end = j
    return text[:idx] + replacement + text[end:]


def build_city_page(template_text: str, city: dict, service_slug: str) -> str:
    """Build a city page by substituting the template's city/service data."""
    svc = SERVICE_DATA[service_slug]
    text = template_text
    # 1. city
    text = _replace_balanced(text, "const city = ", "const city = " + json.dumps(city, ensure_ascii=False))
    # 2. service
    new_service_obj = {
        "slug": service_slug,
        "name": svc["name"],
        "category": svc["category"],
        "description": svc["name"] + " dari Beriklan (Bandung, sejak 2016). Tim online respon 1 jam, laporan rutin, konsultasi awal 15 menit gratis.",
        "faqs": svc["faqs"],
        "active": True,
        "order": {"jasa-kelola-instagram": 6, "jasa-kelola-tiktok": 7, "jasa-pembuatan-website": 8}[service_slug],
        "tiers": svc["tiers"],
        "why_features": svc["why_features"],
        "how_steps": svc["how_steps"],
        "city_intro_template": "",
        "testimonials": [],
    }
    text = _replace_balanced(text, "const service = ", "const service = " + json.dumps(new_service_obj, ensure_ascii=False))
    # 3. tiers / faqs / whyFeatures / howSteps
    text = _replace_balanced(text, "const tiers = ", "const tiers = " + json.dumps(svc["tiers"], ensure_ascii=False))
    text = _replace_balanced(text, "const faqs = ", "const faqs = " + json.dumps(svc["faqs"], ensure_ascii=False))
    text = _replace_balanced(text, "const whyFeatures = ", "const whyFeatures = " + json.dumps(svc["why_features"], ensure_ascii=False))
    text = _replace_balanced(text, "const howSteps = ", "const howSteps = " + json.dumps(svc["how_steps"], ensure_ascii=False))
    # 4. title/description/canonical
    name = city["name"]
    text = re.sub(
        r'title="Jasa Iklan Google di [A-Za-z]+ —[^"]+"',
        f'title="{svc["name"]} di {name} — Paket Profesional | Beriklan"',
        text,
    )
    text = re.sub(
        r'description="Jasa Iklan Google di [A-Za-z]+ —[^"]+"',
        f'description="{svc["name"]} di {name} dari agensi Beriklan (Bandung, sejak 2016). Konsultasi awal 15 menit gratis."',
        text,
    )
    text = re.sub(
        r'canonical="https://beriklan\.co\.id/jasa-iklan-google/[^"]+/"',
        f'canonical="https://beriklan.co.id/{service_slug}/{city["slug"]}/"',
        text,
    )
    # 5. Replace WhatsApp context and city name
    text = text.replace("Jasa Iklan Google", svc["name"])
    text = text.replace("di Medan", f"di {name}")
    # 6. PricingCards pageSlug
    text = re.sub(
        r'pageSlug="Jasa Iklan Google di [A-Za-z]+"',
        f'pageSlug="{svc["name"]} di {name}"',
        text,
    )
    # 6b. Replace hardcoded FaqAccordion items with the `faqs` variable
    # Pattern: <FaqAccordion items={[ ... ]} client:visible />
    # Outer {} is JSX prop, [...] is the array. Replace the whole {...} with {faqs}.
    fa = re.search(r'<FaqAccordion items=\{', text)
    if fa:
        # we already consumed "<FaqAccordion items={". find the matching }.
        # but inside {...} there's an array with []. we need to skip past the matching }.
        # depth = 1 because we're inside the { after items=
        # we need to handle both { and [ as nestable openers within (but } is the only closer for our outer {)
        depth = 1
        i = fa.end()  # position right after the {
        while i < len(text) and depth > 0:
            c = text[i]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
            i += 1
        end = i  # past the matching }
        # Now text[fa.start():end] is `<FaqAccordion items={[...]}`. Replace with `<FaqAccordion items={faqs}`.
        text = text[:fa.start()] + '<FaqAccordion items={faqs}' + text[end:]
    # 7. set:html cityContentMap key
    text = re.sub(
        r'cityContentMap\["jasa-iklan-google/[a-z-]+/"\]',
        f'cityContentMap["{service_slug}/{city["slug"]}/"]',
        text,
    )
    return text


def clone_service_page(service_slug: str, city: dict) -> str:
    """For services whose data is not in SERVICE_DATA, clone an existing
    same-service city page and swap the city name/slug/content-key."""
    # Prefer an existing page of this same service to inherit its real tiers/faqs.
    svc_dir = os.path.join(WEB, "src/pages", service_slug)
    src_city = None
    for cand in ["jakarta", "makassar", "bandung", "medan", "surabaya"]:
        if os.path.exists(os.path.join(svc_dir, cand, "index.astro")):
            src_city = cand
            break
    if not src_city:
        # fall back to the google template + SERVICE_DATA if available
        return ""
    src_text = open(os.path.join(svc_dir, src_city, "index.astro"), encoding="utf-8").read()
    name = city["name"]
    slug = city["slug"]
    # swap cityContentMap key
    src_text = re.sub(
        r'cityContentMap\["' + re.escape(service_slug) + r'/[a-z-]+/"\]',
        f'cityContentMap["{service_slug}/{slug}/"]',
        src_text,
    )
    # swap visible city name occurrences (capitalized source city name)
    src_city_name = city_name_for(src_city)
    if src_city_name:
        src_text = src_text.replace(src_city_name, name)
    # swap canonical/slug in URL path
    src_text = re.sub(
        r'canonical="https://beriklan\.co\.id/' + re.escape(service_slug) + r'/[a-z-]+/"',
        f'canonical="https://beriklan.co.id/{service_slug}/{slug}/"',
        src_text,
    )
    return src_text


def city_name_for(slug: str) -> str:
    return {
        "jakarta": "Jakarta", "makassar": "Makassar", "bandung": "Bandung",
        "medan": "Medan", "surabaya": "Surabaya", "bali": "Bali",
        "yogyakarta": "Yogyakarta", "jogja": "Yogyakarta",
    }.get(slug, "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    cities_data = json.load(open(CITIES))
    city_by_slug = {c["slug"]: c for c in cities_data}
    template_text = open(TEMPLATE, encoding="utf-8").read()

    plan = []
    for slug in MISSING_SERVICES:
        for city_slug in CITIES_USE:
            plan.append((slug, city_slug))

    print(f"Plan: {len(plan)} pages")
    if args.dry:
        for p in plan[:5]:
            print("  sample:", p)
        return

    created = 0
    skipped = 0
    for service_slug, city_slug in plan:
        city = city_by_slug.get(city_slug)
        if not city:
            print(f"  SKIP city not found: {city_slug}")
            skipped += 1
            continue
        out_dir = os.path.join(WEB, "src/pages", service_slug, city_slug)
        out_path = os.path.join(out_dir, "index.astro")
        if os.path.exists(out_path):
            skipped += 1
            continue
        os.makedirs(out_dir, exist_ok=True)
        if service_slug in SERVICE_DATA:
            new_text = build_city_page(template_text, city, service_slug)
        else:
            new_text = clone_service_page(service_slug, city)
            if not new_text:
                print(f"  SKIP no clone source: {service_slug}")
                skipped += 1
                continue
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(new_text)
        created += 1
    print(f"Created: {created}, skipped (exists): {skipped}")


if __name__ == "__main__":
    main()
