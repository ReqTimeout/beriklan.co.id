#!/usr/bin/env python3
"""F1-2: Layout.astro -> English + schema Malaysia (exact replacements, fail loud)."""
FP = "/Users/maabook/Desktop/beriklan.my/web/src/layouts/Layout.astro"
txt = open(FP, encoding="utf-8").read()

PAIRS = [
    # defaults
    ("title = 'Beriklan.co.id — Jasa Digital Marketing Indonesia | Sejak 2016',",
     "title = 'Beriklan.my — Digital Marketing Agency Malaysia | Since 2016',"),
    ("description = 'Agency digital marketing Indonesia — Facebook Ads, Google Ads, TikTok Ads, YouTube, Landing Page. Tim bersertifikasi Meta & Google, berpengalaman mengelola campaign sejak 2016. Hubungi kami untuk konsultasi via WhatsApp.',",
     "description = 'Performance marketing agency serving Malaysia — Facebook Ads, Google Ads, TikTok Ads, YouTube and landing pages. Meta & Google certified team managing campaigns since 2016. Contact us.',"),
    # html lang + meta
    ('<html lang="id" class="scroll-smooth">', '<html lang="en" class="scroll-smooth">'),
    ('<meta name="keywords" content="jasa digital marketing, agency digital marketing indonesia, facebook ads, google ads, tiktok ads, instagram ads, landing page, jasa iklan, agency iklan" />',
     '<meta name="keywords" content="digital marketing agency malaysia, facebook ads agency, google ads agency, tiktok ads agency, ppc management malaysia, landing page design, live stream viewers" />'),
    ('<meta name="language" content="Indonesian" />', '<meta name="language" content="English" />'),
    ('<meta name="author" content="Beriklan.co.id" />', '<meta name="author" content="Beriklan.my" />'),
    ('<meta property="og:site_name" content="Beriklan.co.id" />', '<meta property="og:site_name" content="Beriklan.my" />'),
    ('<meta property="og:locale" content="id_ID" />', '<meta property="og:locale" content="en_MY" />'),
    # ProfessionalService schema
    ("name: 'Beriklan.co.id',\n\t\t\t\tdescription: 'Agency digital marketing Indonesia — Facebook Ads, Google Ads, TikTok Ads, Landing Page, dan social media management.',",
     "name: 'Beriklan.my',\n\t\t\t\tdescription: 'Performance marketing agency serving Malaysia — Facebook Ads, Google Ads, TikTok Ads, landing pages and social media management.',"),
    ("priceRange: 'Rp 2.500.000 - Rp 10.000.000',", "priceRange: 'RM 790 - RM 6,999',"),
    ("areaServed: { '@type': 'Country', 'name': 'Indonesia' },", "areaServed: { '@type': 'Country', 'name': 'Malaysia' },"),
    # Organization schema
    ("name: 'Beriklan.co.id',\n\t\t\t\turl: 'https://beriklan.my',",
     "name: 'Beriklan.my',\n\t\t\t\turl: 'https://beriklan.my',"),
    ("description: 'Agency performance marketing Indonesia berbasis di Bandung — mengelola campaign sejak 2016.',",
     "description: 'Performance marketing agency serving Malaysia — managing paid media campaigns since 2016.',"),
    # newsletter strings
    ("status.textContent = 'Terima kasih!';", "status.textContent = 'Thank you!';"),
    ("status.textContent = 'Format email tidak valid.';", "status.textContent = 'Invalid email format.';"),
    ("status.textContent = data.already ? 'Anda sudah terdaftar.' : 'Terima kasih! Update akan kami kirim via email.';",
     "status.textContent = data.already ? 'You are already subscribed.' : 'Thank you! We will send updates to your email.';"),
    ("status.textContent = data.error || 'Gagal. Coba lagi.';", "status.textContent = data.error || 'Failed. Please try again.';"),
    ("status.textContent = 'Gagal menghubungi server.';", "status.textContent = 'Could not reach the server.';"),
    ("btn.textContent = 'Daftar';", "btn.textContent = 'Subscribe';"),
]

missing = [a for a, _ in PAIRS if a not in txt]
if missing:
    for m in missing:
        print("MISSING:", m[:100])
    raise SystemExit(1)
for a, b in PAIRS:
    txt = txt.replace(a, b)
open(FP, "w", encoding="utf-8").write(txt)
print("Layout.astro OK —", len(PAIRS), "replacements")
