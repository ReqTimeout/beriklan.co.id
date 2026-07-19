#!/usr/bin/env python3
"""
Add FAQ + Breadcrumb + Service schema to all service pages.
Generic Q&A per service type.
"""
import re
from pathlib import Path

BASE = Path("/Users/maabook/Desktop/beriklan.co.id/web/src/pages")

# Service FAQ templates (5 questions per service)
SERVICE_FAQ = {
    "jasa-digital-marketing": [
        ("Berapa harga jasa digital marketing di Beriklan?", "Mulai dari Rp 2,5 juta per bulan. Paket sudah termasuk strategi, setup campaign multi-platform, dan laporan mingguan. Tidak ada kontrak minimum."),
        ("Apa saja yang termasuk dalam layanan digital marketing?", "Setup campaign Facebook Ads, Instagram Ads, Google Ads, TikTok Ads. Optimasi mingguan, A/B testing creative, retargeting, dan laporan transparan."),
        ("Berapa lama setup digital marketing?", "Setup awal 3-5 hari kerja. Campaign live dalam 1 minggu pertama. Optimasi rutin mingguan setelah launch."),
        ("Apakah tim Beriklan bersertifikat?", "Ya, tim kami Meta Business Partner dan Google Partner bersertifikat. Akses langsung ke platform support."),
        ("Bagaimana cara tracking hasil digital marketing?", "Kami setup GTM + GA4 + Meta Pixel di website. Anda bisa akses real-time dashboard + laporan mingguan via WhatsApp."),
    ],
    "jasa-iklan-facebook": [
        ("Berapa biaya iklan Facebook Ads?", "Mulai dari Rp 1.750.000 per 30 hari (Standart) dan Rp 3.750.000 (Business). Sudah termasuk ad spend, setup, dan optimasi."),
        ("Apa bedanya paket Standart dan Business?", "Standart untuk 1-2 campaign sederhana. Business untuk multiple campaigns, advanced targeting, A/B testing, dan laporan detail."),
        ("Berapa lama hasil Facebook Ads?", "Iklan muncul 24 jam setelah setup. Lead pertama masuk minggu pertama. Optimal di bulan ke-2."),
        ("Beriklan Certified Meta Business Partner?", "Ya, tim kami Meta Business Partner bersertifikat dengan akses langsung ke support Meta."),
        ("Bagaimana tracking leads dari Facebook Ads?", "Meta Pixel di website + WhatsApp click tracking. Dashboard Meta Ads Manager + laporan mingguan."),
    ],
    "jasa-iklan-google": [
        ("Berapa biaya Google Ads?", "Mulai dari Rp 1 juta ad spend. Biaya jasa terpisah. Audit akun gratis 15 menit untuk estimate."),
        ("Iklan muncul di mana saja?", "Google Search, Search Partners, Display Network, YouTube, dan Gmail. Targeting keyword presisi."),
        ("Berapa lama Google Ads bisa live?", "Setup 1-3 hari kerja. Iklan muncul setelah proses review Google (1-24 jam setelah submit)."),
        ("Apakah Beriklan Google Partner?", "Ya, tim kami Google Partner dengan akses langsung ke support Google dan beta features."),
        ("Bagaimana tracking conversion Google Ads?", "Google Tag Manager + GA4 + Conversion Tracking. Anda bisa lihat real-time dashboard."),
    ],
    "jasa-iklan-instagram": [
        ("Berapa biaya Instagram Ads?", "Mulai dari Rp 1.750.000 per 30 hari. Sudah termasuk setup story ads, reels ads, feed ads, dan optimasi."),
        ("Format iklan apa saja?", "Story Ads, Reels Ads, Feed Ads, Explore Ads, Shop Ads. Semua format Instagram tersedia."),
        ("Target audience Instagram Ads yang ideal?", "Bisa custom interest, lookalike audience dari customer database, atau interest-based (fashion, beauty, fitness, dll)."),
        ("Apakah Instagram Ads efektif untuk UMKM?", "Sangat efektif. Instagram 80% pengguna Indonesia aktif di platform. Cocok untuk fashion, F&B, beauty, jasa profesional."),
        ("Berapa lama hasil Instagram Ads?", "Story Ads mulai tayang 24 jam. Reels Ads bisa viral dalam 1-2 minggu. Lead optimal di bulan ke-2."),
    ],
    "jasa-iklan-tiktok": [
        ("Berapa biaya TikTok Ads?", "Mulai dari Rp 1.750.000 per 30 hari. Sudah termasuk setup Spark Ads, In-Feed Ads, dan optimasi."),
        ("Format TikTok Ads apa saja?", "In-Feed Ads (muncul di FYP), Spark Ads (boost organic content), TopView Ads (premium)."),
        ("Siapa target audience TikTok Ads?", "Gen Z (18-25) dan Milenial (26-35). 70% pengguna TikTok Indonesia di rentang usia ini. Cocok untuk F&B, fashion, beauty, entertainment."),
        ("Apakah TikTok Ads untuk B2B?", "Bisa, tapi kurang efektif. Untuk B2B lebih cocok LinkedIn Ads atau Google Ads. TikTok optimal untuk B2C."),
        ("Berapa lama setup TikTok Ads?", "Setup 1-3 hari. Video ads mulai tayang 24-48 jam setelah approval. Spark Ads bisa langsung boost dari organic."),
    ],
    "jasa-iklan-youtube": [
        ("Berapa biaya YouTube Ads?", "Mulai dari Rp 1.750.000 per 30 hari. Sudah termasuk setup TrueView, Bumper Ads, dan optimasi."),
        ("Format YouTube Ads apa saja?", "TrueView In-Stream (skippable setelah 5 detik), Bumper Ads (6 detik non-skippable), Discovery Ads (muncul di YouTube home)."),
        ("Apakah YouTube Ads untuk brand awareness?", "Sangat efektif. YouTube punya reach 50jt+ user Indonesia per bulan. Cocok untuk brand awareness + consideration."),
        ("Berapa lama setup YouTube Ads?", "Setup 2-5 hari (perlu video assets). Iklan live setelah approval YouTube (1-3 hari)."),
        ("YouTube Ads cocok untuk industri apa?", "Semua industri. Terutama efektif untuk FMCG, tech, education, financial services, automotive."),
    ],
    "jasa-kelola-instagram": [
        ("Berapa harga jasa kelola Instagram?", "Mulai dari Rp 1.500.000 per bulan. Sudah termasuk 12-15 post, story harian, reels mingguan, dan laporan."),
        ("Berapa post per minggu?", "3-5 post feed, 5-7 story per hari, 1-2 reels per minggu. Sesuai paket dan target audiens."),
        ("Apakah tim Beriklan handle caption + hashtag?", "Ya, kami handle content calendar, copywriting caption, hashtag strategy, dan visual design."),
        ("Berapa lama sampai results terlihat?", "Engagement rate naik dalam 1-2 bulan. Follower growth konsisten di bulan ke-2. Optimal di bulan ke-3."),
        ("Apakah ada laporan bulanan?", "Ya, IG Insight report bulanan: reach, impressions, engagement rate, follower growth, dan rekomendasi bulan depan."),
    ],
    "jasa-kelola-tiktok": [
        ("Berapa harga jasa kelola TikTok?", "Mulai dari Rp 1.500.000 per bulan. Sudah termasuk content creation, posting rutin, dan community management."),
        ("Berapa video per minggu?", "3-5 video pendek per minggu + 1-2 live streaming. Plus daily trend monitoring dan reply komentar."),
        ("Bagaimana cara bikin konten yang viral?", "Tim kami monitor trending sounds, formats, dan topics. Kombinasikan dengan brand message untuk reach organik + paid boost."),
        ("Apakah handle live streaming?", "Ya, bisa. Include dalam paket Business. Setup peralatan + script +主持人 untuk live session 1-2 jam."),
        ("Berapa lama sampai viral?", "Tergantung niche. Beberapa video bisa viral dalam minggu pertama. Rata-rata akun baru FYP dalam 2-3 bulan."),
    ],
    "jasa-pembuatan-website": [
        ("Berapa harga buat website?", "Mulai dari Rp 1.500.000 (company profile) dan Rp 3.500.000 (e-commerce basic). Custom design, mobile responsive, SEO ready."),
        ("Berapa lama pengerjaan website?", "Company profile: 7-14 hari kerja. E-commerce: 14-21 hari kerja. Custom: 21-30 hari kerja (tergantung kompleksitas)."),
        ("Apakah termasuk domain + hosting?", "Ya, free domain .com/.id + hosting 1 tahun untuk paket Standart+. Setelah itu renewal Rp 350.000/tahun."),
        ("CMS apa yang dipakai?", "WordPress (paling user-friendly untuk client update sendiri) atau Laravel (untuk custom logic). Diskusi dulu untuk pilih yang sesuai."),
        ("Apakah termasuk SEO optimization?", "Ya, semua website kami SEO-friendly: meta tags, schema markup, sitemap, fast loading, mobile responsive."),
    ],
    "jasa-pembuatan-landing-page": [
        ("Berapa harga landing page?", "Mulai dari Rp 1.000.000 (single page) atau Rp 1.500.000 (paket landing page + Google Ads setup)."),
        ("Berapa lama pengerjaan?", "3-5 hari kerja untuk landing page sederhana. 7-10 hari untuk yang kompleks dengan copywriting dan A/B testing."),
        ("Apakah termasuk copywriting?", "Ya, copywriter kami yang handle headline, body text, dan CTA. Anda tinggal review dan approve."),
        ("Apakah ada A/B testing?", "Bisa. Setup 2-3 variasi headline/CTA, lalu test mana yang convert lebih tinggi."),
        ("Apakah bisa integrasi dengan WhatsApp?", "Ya, default semua landing page kami ada WhatsApp button yang langsung chat ke nomor bisnis Anda."),
    ],
}

# Service metadata
SERVICE_META = {
    "jasa-digital-marketing": {"name": "Jasa Digital Marketing", "price": "Rp 2.500.000 - Rp 10.000.000", "type": "Digital Marketing"},
    "jasa-iklan-facebook": {"name": "Jasa Iklan Facebook Ads", "price": "Rp 1.750.000 - Rp 3.750.000", "type": "Facebook Ads"},
    "jasa-iklan-google": {"name": "Jasa Iklan Google Ads", "price": "Rp 1.000.000 - Rp 5.000.000", "type": "Google Ads"},
    "jasa-iklan-instagram": {"name": "Jasa Iklan Instagram", "price": "Rp 1.750.000 - Rp 3.750.000", "type": "Instagram Ads"},
    "jasa-iklan-tiktok": {"name": "Jasa Iklan TikTok", "price": "Rp 1.750.000 - Rp 3.750.000", "type": "TikTok Ads"},
    "jasa-iklan-youtube": {"name": "Jasa Iklan YouTube", "price": "Rp 1.750.000 - Rp 3.750.000", "type": "YouTube Ads"},
    "jasa-kelola-instagram": {"name": "Jasa Kelola Instagram", "price": "Rp 1.500.000 - Rp 3.000.000", "type": "Instagram Management"},
    "jasa-kelola-tiktok": {"name": "Jasa Kelola TikTok", "price": "Rp 1.500.000 - Rp 3.000.000", "type": "TikTok Management"},
    "jasa-pembuatan-website": {"name": "Jasa Pembuatan Website", "price": "Rp 1.500.000 - Rp 5.000.000", "type": "Web Development"},
    "jasa-pembuatan-landing-page": {"name": "Jasa Pembuatan Landing Page", "price": "Rp 1.000.000 - Rp 1.500.000", "type": "Landing Page"},
}

def make_faq_block(faq_list):
    lines = ["faq={["]
    for i, (q, a) in enumerate(faq_list):
        # Escape single quotes in JSON
        q_esc = q.replace("'", "\\'")
        a_esc = a.replace("'", "\\'")
        sep = "," if i < len(faq_list) - 1 else ""
        lines.append(f"        {{ question: '{q_esc}', answer: '{a_esc}' }}{sep}")
    lines.append("    ]}")
    return "\n    ".join(lines)


def make_breadcrumb_block(slug):
    name = SERVICE_META[slug]['name']
    return """breadcrumb={[
        { name: "Beranda", url: "https://www.beriklan.co.id/" },
        { name: \"""" + name + """\", url: \"https://www.beriklan.co.id/""" + slug + """/\" }
    ]}"""


def make_service_block(slug):
    meta = SERVICE_META[slug]
    name = meta['name']
    price = meta['price']
    stype = meta['type']
    return """service={{
        name: \"""" + name + """\",
        description: \"Jasa """ + name + """ profesional dari Beriklan.co.id. Tim bersertifikat, strategi terukur, laporan mingguan, dan optimasi rutin untuk UMKM & bisnis menengah di Indonesia.\",
        url: \"https://www.beriklan.co.id/""" + slug + """/\",
        priceRange: \"""" + price + """\",
        serviceType: \"""" + stype + """\",
        areaServed: \"Indonesia\",
        provider: { name: \"Beriklan.co.id\", url: \"https://www.beriklan.co.id\" }
    }}"""


def process_file(filepath):
    """Add FAQ + breadcrumb + service props to Layout call in service page."""
    slug = filepath.stem  # e.g., jasa-iklan-facebook
    if slug not in SERVICE_FAQ:
        return False, "no FAQ template"

    content = filepath.read_text()

    # Find the <Layout ...> opening tag (may span multiple lines)
    # We need to add faq, breadcrumb, service props before the closing > of Layout

    # Try both canonical variants
    slug_pattern = None
    for prefix in ["https://www.beriklan.co.id", "https://beriklan.co.id"]:
        candidate = f'canonical="{prefix}/{slug}/"'
        if candidate in content:
            slug_pattern = candidate
            break

    if not slug_pattern:
        return False, f"no canonical for {slug} found"

    # Find the closing > of the Layout tag
    # Look for the line with canonical and find the next > on that line or within a few
    idx = content.find(slug_pattern)
    if idx == -1:
        return False, "no match"

    # Find the next ">" after the Layout tag opens
    # The Layout tag opens with <Layout and contains various props
    # Find the next > that closes the Layout opening tag
    # We can be naive and look for ">" after the canonical match
    search_start = idx + len(slug_pattern)
    # Skip to the end of line or find next >
    end_idx = content.find(">", search_start)
    if end_idx == -1:
        return False, "no closing > found"

    # Check if it's a self-closing tag
    next_char = content[end_idx - 1] if end_idx > 0 else ""
    if next_char == "/":
        # Self-closing, replace with multi-line
        before = content[:end_idx]
        after = content[end_idx:]
        # Construct the new content
        new_props = f"\n    {make_faq_block(SERVICE_FAQ[slug])}\n    {make_breadcrumb_block(slug)}\n    {make_service_block(slug)}\n>"
        new_content = before + new_props + after
    else:
        # Multi-line tag, find the closing > of opening
        before = content[:end_idx]
        after = content[end_idx:]
        new_props = f"\n    {make_faq_block(SERVICE_FAQ[slug])}\n    {make_breadcrumb_block(slug)}\n    {make_service_block(slug)}\n>"
        new_content = before + new_props + after

    filepath.write_text(new_content)
    return True, "updated"


# Process all service pages
for service_file in sorted(BASE.glob("jasa-*.astro")):
    if "pilar" in service_file.name:
        continue
    ok, msg = process_file(service_file)
    status = "✅" if ok else "⏭️"
    print(f"  {status} {service_file.name}: {msg}", flush=True)

print()
print("✅ Done. Build & deploy next.")
# Force print at end
print(f"\n=== Total files: {sum(1 for _ in BASE.glob('jasa-*.astro'))} ===")
print(f"=== With FAQ: {sum(1 for f in BASE.glob('jasa-*.astro') if 'faq={' in f.read_text())} ===")
