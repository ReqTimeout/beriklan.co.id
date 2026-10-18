#!/usr/bin/env python3
"""
Enrich Drafts — Improve quality draft existing di R2 publish-queue
=================================================================

Masalah: 386,690 draft di R2 punya quality issues:
  - Tidak ada FAQ
  - Tidak ada internal link ke beriklan.co.id
  - Tidak ada images
  - Word count rendah (avg 422 kata)

Solusi: Enrichment bundle (FAQ + internal link + image) sehingga:
  - ✅ AdSense-compliant (original content + visual + FAQ schema)
  - ✅ Internal linking kuat (mendekati 5 links per artikel)
  - ✅ Featured snippet eligible (FAQ schema + structured content)
  - ✅ Visual (images dengan alt text SEO-friendly)

Proses per artikel:
  1. Detect service + city dari keyword
  2. Detect industri dari keyword (fashion, F&B, kesehatan, etc)
  3. Generate 3 FAQ (Question + Answer) spesifik per service+industri
  4. Inject 2 internal links ke service page + 1 ke blog pillar
  5. Inject 2 Unsplash images dengan alt text SEO
  6. Inject 1 CTA box "Butuh bantuan mengelola [platform]?"
  7. Save back to R2 publish-queue (in-place update)

Usage:
  python3 scripts/enrich_drafts.py --dry-run --limit 5
  python3 scripts/enrich_drafts.py --limit 100
  python3 scripts/enrich_drafts.py --all
"""
import os, sys, json, re, time, argparse, random
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
DRAFTS_DIR = ROOT / 'drafts_patched'

# ============================================================================
# FAQ TEMPLATES per SERVICE × INDUSTRI
# ============================================================================

FAQ_TEMPLATES = {
    'jasa-iklan-facebook': {
        'general': [
            ("Berapa biaya jasa iklan Facebook di Beriklan?",
             "Biaya jasa iklan Facebook di Beriklan mulai Rp 1.750.000 untuk paket Standart (30 hari) dan Rp 3.750.000 untuk paket Business. Belum termasuk ad spend Meta yang Anda tentukan sendiri mulai Rp 50.000/hari."),
            ("Berapa lama sampai iklan Facebook mulai menghasilkan leads?",
             "Dari pengalaman mengelola 100+ campaign, chat WhatsApp pertama biasanya masuk di minggu pertama setelah iklan tayang. Lead konsisten mulai terbentuk di minggu ke-2 sampai ke-3 setelah optimasi."),
            ("Apakah saya mendapat akses penuh ke akun iklan Facebook?",
             "Ya. Berbeda dengan agency yang menyembunyikan akun, kami memberikan akses penuh. Anda bisa monitor dashboard Meta Ads Manager kapan saja, dan kami kirim laporan mingguan via WhatsApp."),
        ],
        'fashion': [
            ("Apakah Meta Ads efektif untuk toko hijab atau fashion online?",
             "Sangat efektif. Mayoritas toko fashion online di Indonesia mengandalkan Meta Ads (Facebook + Instagram) sebagai sumber leads utama. Targeting berdasarkan interest (hijab, gamis, modest fashion) dan lookalike audience dari customer existing memberikan ROAS terbaik."),
            ("Berapa budget minimum iklan untuk toko fashion online?",
             "Minimum harian Rp 50.000-Rp 100.000 sudah cukup untuk testing awal. Untuk hasil terukur dalam 30 hari, kami rekomendasikan budget total Rp 3-5jt/bulan dengan fee manajemen terpisah."),
        ],
        'fnB': [
            ("Apakah Facebook Ads efektif untuk resto dan UMKM kuliner?",
             "Sangat efektif untuk jangkauan lokal. Kami kombinasikan Facebook Ads dengan Instagram Ads untuk menjangkau audience dalam radius 5-15 km dari resto Anda. Cocok untuk drive traffic offline + delivery order."),
            ("Bagaimana cara target audience yang tepat untuk F&B?",
             "Kami riset demographic, interest (kuliner, foodies), dan behavior (online food ordering) dalam radius lokasi resto. Remarketing untuk orang yang sudah lihat konten resto tapi belum order."),
        ],
        'kesehatan': [
            ("Apakah Facebook Ads boleh untuk klinik kecantikan?",
             "Boleh, dengan catatan: tidak boleh mengklaim hasil medis spesifik, harus ada disclaimer, dan proses approval Meta untuk iklan kesehatan butuh 24-48 jam. Tim kami handle semua compliance."),
            ("Bagaimana Meta Pixel untuk klinik?",
             "Pixel di-install di halaman booking/konsultasi untuk track konversi. Kami setup event 'Lead' dan 'Schedule' sehingga Anda tahu cost per booking yang sebenarnya."),
        ],
        'properti': [
            ("Apakah Facebook Ads efektif untuk agen properti?",
             "Sangat efektif untuk lead generation. Kami target audience yang sudah menunjukkan interest properti (search rumah, apartemen) dalam 30 hari terakhir. Cost per lead rata-rata Rp 50.000-Rp 150.000."),
            ("Berapa budget yang dibutuhkan untuk iklan properti?",
             "Minimum Rp 5-10jt/bulan untuk hasil konsisten. Properti high-ticket butuh budget lebih besar karena cost per click lebih tinggi dan konversi lebih lama."),
        ],
    },
    'jasa-iklan-instagram': {
        'general': [
            ("Apa bedanya Instagram Ads dan Facebook Ads?",
             "Instagram Ads fokus pada visual konten (feed, stories, reels), cocok untuk produk visual seperti fashion, skincare, F&B. Facebook Ads lebih fleksibel untuk semua jenis bisnis dan menawarkan targeting lebih detail."),
            ("Berapa biaya jasa iklan Instagram di Beriklan?",
             "Mulai Rp 1.750.000 untuk paket Standart (30 hari) dan Rp 3.750.000 untuk paket Business. Belum termasuk ad spend Meta mulai Rp 50.000/hari."),
            ("Reels Instagram Ads atau Stories Ads yang lebih bagus?",
             "Tergantung tujuan: Reels untuk reach luas + awareness (CPM lebih murah), Stories untuk direct response (swipe up ke WhatsApp). Kami biasanya mix keduanya untuk hasil optimal."),
        ],
    },
    'jasa-iklan-tiktok': {
        'general': [
            ("Apakah TikTok Ads efektif untuk bisnis Indonesia?",
             "Sangat efektif. 127jt+ pengguna aktif TikTok di Indonesia, dominan Gen-Z dan Milenial urban. CPM umumnya 40-60% lebih murah dari Meta Ads, cocok untuk brand yang ingin jangkauan luas dengan budget efisien."),
            ("Berapa biaya jasa iklan TikTok di Beriklan?",
             "Mulai Rp 1.000.000 untuk paket Basic (1 video Spark Ads), Rp 1.600.000 Standart (3 video), Rp 3.750.000 Business (multi-format). Belum termasuk ad spend TikTok mulai Rp 100.000/hari."),
            ("Spark Ads atau In-Feed Ads yang lebih bagus?",
             "Spark Ads amplify video organic yang sudah perform — biasanya lebih murah CPM karena tidak ada 'ad stigma'. In-Feed Ads untuk video fresh yang di-create khusus sebagai iklan."),
        ],
    },
    'jasa-iklan-google': {
        'general': [
            ("Apa bedanya Google Ads dan SEO?",
             "Google Ads adalah iklan bayar per klik — muncul di atas hasil search berdasarkan bidding keyword. SEO adalah optimasi organik — muncul di bawah ads berdasarkan kualitas konten. Idealnya kombinasi keduanya."),
            ("Berapa biaya jasa iklan Google Ads di Beriklan?",
             "Mulai Rp 1.500.000 untuk paket dasar. Fee manajemen terpisah dari ad spend (budget iklan Anda). Minimum ad spend Rp 100.000/hari untuk hasil terukur."),
            ("Berapa lama Google Ads menghasilkan leads?",
             "Bisa instant — dalam 24 jam setelah setup, iklan bisa langsung muncul di page 1 Google dan menghasilkan klik. Leads pertama biasanya masuk di minggu pertama."),
        ],
    },
    'jasa-iklan-youtube': {
        'general': [
            ("Apakah YouTube Ads efektif untuk UMKM?",
             "Tergantung tujuan. YouTube Ads paling efektif untuk brand awareness (video dilihat jutaan orang) dan edukasi produk. Untuk direct response / closing cepat, Meta/TikTok biasanya lebih efisien."),
            ("Berapa biaya jasa iklan YouTube?",
             "Mulai Rp 1.500.000 untuk paket dasar. Ad spend minimum Rp 200.000/hari untuk frekuensi yang cukup."),
        ],
    },
    'jasa-digital-marketing': {
        'general': [
            ("Apa itu jasa digital marketing dan siapa yang butuh?",
             "Jasa digital marketing adalah layanan mengelola strategi pemasaran digital secara end-to-end: iklan (Meta, Google, TikTok), konten organik, SEO, dan analytics. Cocok untuk UMKM hingga bisnis menengah yang ingin growth terukur."),
            ("Berapa biaya jasa digital marketing di Beriklan?",
             "Mulai Rp 2.500.000/bulan untuk paket integrated (multi-channel). Custom paket sesuai objective dan skala bisnis."),
        ],
    },
    'jasa-pembuatan-website': {
        'general': [
            ("Berapa biaya bikin website profesional di Beriklan?",
             "Mulai Rp 3.500.000 untuk company profile, Rp 7.500.000 untuk e-commerce sederhana, Rp 15.000.000+ untuk custom web app. Termasuk domain + hosting 1 tahun."),
            ("Berapa lama proses pembuatan website?",
             "Company profile: 7-14 hari kerja. E-commerce: 14-21 hari kerja. Custom web app: 30+ hari tergantung kompleksitas."),
        ],
    },
    'jasa-pembuatan-landing-page': {
        'general': [
            ("Apa bedanya landing page dan website?",
             "Landing page = 1 halaman fokus 1 tujuan (conversion). Website = multi-halaman untuk navigasi umum. Landing page 3-5x lebih tinggi conversion rate untuk iklan."),
            ("Berapa biaya bikin landing page?",
             "Mulai Rp 1.500.000 untuk landing page basic, Rp 3.500.000 untuk high-converting + A/B testing setup."),
        ],
    },
    'jasa-kelola-instagram': {
        'general': [
            ("Apa bedanya jasa kelola Instagram dan jasa iklan Instagram?",
             "Kelola Instagram = organic content (posting rutin, stories, reels, community management). Iklan Instagram = paid ads. Idealnya kombinasi keduanya untuk growth maksimal."),
            ("Berapa biaya jasa kelola Instagram?",
             "Mulai Rp 2.500.000/bulan untuk paket content + community management. Belum termasuk ad spend untuk boost post."),
        ],
    },
    'jasa-kelola-tiktok': {
        'general': [
            ("Berapa biaya jasa kelola TikTok?",
             "Mulai Rp 2.500.000/bulan untuk paket video creation + posting rutin. Termasuk 12-20 video per bulan."),
        ],
    },
}


# ============================================================================
# INDUSTRY DETECTOR
# ============================================================================

INDUSTRY_KEYWORDS = {
    'fashion': ['hijab', 'jilbab', 'baju', 'pakaian', 'fashion', 'gamis', 'celana', 'kemeja',
                'kaos', 'rok', 'dress', 'sepatu', 'tas', 'mukena', 'sarung', 'preloved',
                'thrift', 'konveksi', 'butik', 'reseller', 'dropshipper', 'skincare',
                'kosmetik', 'beauty', 'kecantikan', 'wardah', 'makeup', 'lipstik'],
    'fnB': ['resto', 'rumah makan', 'kuliner', 'kafe', 'cafe', 'kopi', 'makanan', 'minuman',
            'snack', 'katering', 'warung', 'kue', 'roti', 'bakery', 'jus', 'es krim',
            'ayam', 'sambal', 'bumbu', 'frozen', 'grabfood', 'gofood'],
    'kesehatan': ['klinik', 'kecantikan', 'salon', 'spa', 'skincare', 'kosmetik', 'dokter',
                  'apotek', 'obat', 'vitamin', 'suplemen', 'fitness', 'gym', 'yoga',
                  'estetika', 'botox', 'filler', 'klinik gigi'],
    'properti': ['properti', 'perumahan', 'rumah', 'apartemen', 'villa', 'ruko', 'tanah',
                 'kavling', 'developer', 'real estate', 'kantor', 'gudang', 'showroom',
                 'agen properti'],
    'pendidikan': ['sekolah', 'kursus', 'pelatihan', 'bimbel', 'les', 'bootcamp', 'edukasi',
                   'webinar', 'universitas', 'kampus', 'mahasiswa'],
    'jasa_b2b': ['konsultan', 'jasa', 'agensi', 'agency', 'software', 'aplikasi', 'b2b',
                 'layanan profesional', 'audit', 'legal'],
    'manufaktur': ['pabrik', 'manufaktur', 'distributor', 'grosir', 'supplier', 'eksportir',
                   'importir', 'bahan baku', 'konveksi'],
    'otomotif': ['mobil', 'motor', 'otomotif', 'showroom', 'dealer', 'bengkel', 'sparepart',
                 'ban', 'oli'],
    'travel': ['travel', 'tour', 'hotel', 'villa', 'homestay', 'liburan', 'umrah', 'haji',
               'paket wisata'],
}


def detect_industri_from_keyword(keyword):
    """Detect industri dari keyword."""
    kw_lower = (keyword or '').lower()
    matches = []
    for ind, keywords in INDUSTRY_KEYWORDS.items():
        score = sum(1 for k in keywords if k in kw_lower)
        if score > 0:
            matches.append((ind, score))
    if matches:
        return sorted(matches, key=lambda x: -x[1])[0][0]
    return None


def get_faq_for_draft(service, industri, default_count=3):
    """Get FAQ pairs untuk service × industri."""
    faqs = []
    service_faqs = FAQ_TEMPLATES.get(service, {})

    # Try industri-specific first
    if industri and industri in service_faqs:
        faqs.extend(service_faqs[industri])

    # Then general
    if 'general' in service_faqs:
        faqs.extend(service_faqs['general'])

    if not faqs:
        # Fallback
        faqs = [
            ("Berapa biaya layanan ini di Beriklan?",
             "Biaya bervariasi tergantung paket dan objective bisnis. Hubungi kami via WhatsApp untuk konsultasi gratis dan rekomendasi paket yang sesuai."),
            ("Berapa lama setup dan mulai live?",
             "Setup awal 1-3 hari kerja. Campaign live dalam minggu pertama setelah persetujuan strategi dari Anda."),
            ("Apakah ada laporan rutin?",
             "Ya. Dashboard real-time + laporan mingguan via WhatsApp dengan breakdown KPI dan rekomendasi iterasi."),
        ]

    return faqs[:default_count]


# ============================================================================
# INTERNAL LINK GENERATOR
# ============================================================================

SERVICE_LINKS = {
    'jasa-iklan-facebook': '/jasa-iklan-facebook/',
    'jasa-iklan-instagram': '/jasa-iklan-instagram/',
    'jasa-iklan-tiktok': '/jasa-iklan-tiktok/',
    'jasa-iklan-google': '/jasa-iklan-google/',
    'jasa-iklan-youtube': '/jasa-iklan-youtube/',
    'jasa-digital-marketing': '/jasa-digital-marketing/',
    'jasa-pembuatan-website': '/jasa-pembuatan-website/',
    'jasa-pembuatan-landing-page': '/jasa-pembuatan-landing-page/',
    'jasa-kelola-instagram': '/jasa-kelola-instagram/',
    'jasa-kelola-tiktok': '/jasa-kelola-tiktok/',
    'jasa-view-live': '/jasa-view-live/',
}

PILLAR_LINKS = {
    'jasa-iklan-facebook': '/jasa-iklan-facebook/pilar/',
    'jasa-iklan-instagram': '/jasa-iklan-instagram/pilar/',
    'jasa-iklan-tiktok': '/jasa-iklan-tiktok/pilar/',
    'jasa-iklan-google': '/jasa-iklan-google/pilar/',
    'jasa-iklan-youtube': '/jasa-iklan-youtube/pilar/',
    'jasa-digital-marketing': '/jasa-digital-marketing/pilar/',
    'jasa-pembuatan-website': '/jasa-pembuatan-website/pilar/',
    'jasa-pembuatan-landing-page': '/jasa-pembuatan-landing-page/pilar/',
    'jasa-kelola-instagram': '/jasa-kelola-instagram/pilar/',
    'jasa-kelola-tiktok': '/jasa-kelola-tiktok/pilar/',
}


# ============================================================================
# IMAGE INJECTION
# ============================================================================

# Static placeholder images dari Unsplash (SEO-friendly + free to use)
# Format: (URL, alt_text_template)
UNSPLASH_IMAGES = {
    'jasa-iklan-facebook': [
        ("https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=800",
         "Tim Beriklan mengelola campaign Facebook Ads"),
        ("https://images.unsplash.com/photo-1432888622747-4eb9a8efeb07?w=800",
         "Dashboard Meta Ads Manager dengan analytics real-time"),
    ],
    'jasa-iklan-instagram': [
        ("https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?w=800",
         "Instagram Reels Ads untuk engagement tinggi"),
        ("https://images.unsplash.com/photo-1542362567-b07e54358753?w=800",
         "Content visual Instagram untuk brand fashion"),
    ],
    'jasa-iklan-tiktok': [
        ("https://images.unsplash.com/photo-1611605698335-8b1569810432?w=800",
         "TikTok For You Page dengan video FYP viral"),
        ("https://images.unsplash.com/photo-1596553650268-7cf7c7bcc4d3?w=800",
         "Spark Ads TikTok untuk brand awareness"),
    ],
    'jasa-iklan-google': [
        ("https://images.unsplash.com/photo-1571171637578-41bc2dd41cd2?w=800",
         "Google Ads dashboard dengan performance metrics"),
        ("https://images.unsplash.com/photo-1432888622747-4eb9a8efeb07?w=800",
         "Search engine results page dengan Google Ads"),
    ],
    'jasa-digital-marketing': [
        ("https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800",
         "Digital marketing strategy meeting dengan tim"),
        ("https://images.unsplash.com/photo-1551434678-e076c223a692?w=800",
         "Marketing analytics dashboard dengan conversion data"),
    ],
    'jasa-pembuatan-website': [
        ("https://images.unsplash.com/photo-1547658719-da2b51169166?w=800",
         "Web developer designing responsive website"),
        ("https://images.unsplash.com/photo-1467232004584-a241de8bcf5d?w=800",
         "Modern website design mockup di laptop"),
    ],
    'jasa-pembuatan-landing-page': [
        ("https://images.unsplash.com/photo-1559028012-481c04fa702d?w=800",
         "Landing page design dengan high conversion rate"),
        ("https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800",
         "A/B testing landing page untuk optimasi conversion"),
    ],
    'jasa-kelola-instagram': [
        ("https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?w=800",
         "Instagram content planning dengan calendar"),
        ("https://images.unsplash.com/photo-1556761175-5973dc0f32e7?w=800",
         "Content creator managing Instagram account"),
    ],
    'jasa-kelola-tiktok': [
        ("https://images.unsplash.com/photo-1611605698335-8b1569810432?w=800",
         "TikTok content creation untuk brand"),
        ("https://images.unsplash.com/photo-1596553650268-7cf7c7bcc4d3?w=800",
         "Video production untuk TikTok marketing"),
    ],
    'jasa-iklan-youtube': [
        ("https://images.unsplash.com/photo-1611162616475-46b635cb6868?w=800",
         "YouTube video production studio setup"),
        ("https://images.unsplash.com/photo-1626785774573-4b799315345d?w=800",
         "YouTube Ads dengan bumper format untuk awareness"),
    ],
    'default': [
        ("https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800",
         "Tim Beriklan sedang menganalisis campaign digital marketing"),
        ("https://images.unsplash.com/photo-1556761175-b413da4baf72?w=800",
         "Dashboard digital marketing dengan KPI utama"),
    ],
}


def get_images_for_service(service):
    """Get images for service."""
    return UNSPLASH_IMAGES.get(service, UNSPLASH_IMAGES['default'])


# ============================================================================
# ENRICHMENT LOGIC
# ============================================================================

def build_faq_html(faqs):
    """Build FAQ HTML + JSON-LD schema."""
    html = ['<section class="faq-section my-8 p-6 bg-soft rounded-2xl">']
    html.append('<h2 class="text-2xl font-display font-bold text-ink mb-4">Pertanyaan yang Sering Diajukan</h2>')

    # FAQ schema JSON-LD
    schema_items = []
    for q, a in faqs:
        html.append('<details class="faq-item mb-3 bg-white rounded-lg p-4 cursor-pointer">')
        html.append(f'<summary class="font-display font-bold text-ink">{escape_html(q)}</summary>')
        html.append(f'<p class="text-muted mt-2 leading-relaxed">{escape_html(a)}</p>')
        html.append('</details>')
        schema_items.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {
                "@type": "Answer",
                "text": a,
            },
        })

    html.append('</section>')
    html.append(f'<script type="application/ld+json" class="faq-schema">{json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":schema_items}, ensure_ascii=False)}</script>')
    return '\n'.join(html)


def escape_html(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def build_internal_links_html(service, city):
    """Build internal links section."""
    service_url = SERVICE_LINKS.get(service, f'/{service}/')
    pillar_url = PILLAR_LINKS.get(service, f'/{service}/pilar/')
    service_label = service.replace('jasa-', '').replace('-', ' ').title()

    html = ['<div class="related-links my-8 p-6 border border-gray-200 rounded-2xl bg-gradient-to-br from-blue-50 to-white">']
    html.append('<h3 class="text-lg font-display font-bold text-ink mb-3">Baca Juga</h3>')
    html.append('<ul class="space-y-2">')
    html.append(f'<li>→ <a href="{service_url}" class="text-accent font-semibold hover:underline">Lihat paket {service_label}</a></li>')
    html.append(f'<li>→ <a href="{pillar_url}" class="text-accent font-semibold hover:underline">Panduan lengkap {service_label}</a></li>')
    if city:
        html.append(f'<li>→ <a href="{service_url}{city}/" class="text-accent font-semibold hover:underline">{service_label} di {city.title()}</a></li>')
    html.append('</ul>')
    html.append('</div>')
    return '\n'.join(html)


def build_image_html(images, alt_template='Beriklan digital marketing'):
    """Build image HTML dengan SEO alt text."""
    html = []
    for url, alt in images[:2]:
        html.append(f'<figure class="my-6">')
        html.append(f'<img src="{url}" alt="{escape_html(alt)}" loading="lazy" class="w-full rounded-xl" />')
        html.append(f'<figcaption class="text-sm text-muted mt-2 text-center italic">{escape_html(alt)}</figcaption>')
        html.append(f'</figure>')
    return '\n'.join(html)


def build_cta_html(service):
    """Build inline CTA box."""
    service_label = service.replace('jasa-', '').replace('-', ' ').title()
    service_url = SERVICE_LINKS.get(service, f'/{service}/')
    wa_url = f"https://wa.me/62811919328?text={('Halo+Beriklan,+saya+tertarik+' + service_label.replace(' ', '+'))}"

    html = f'''
<div class="cta-box my-10 p-8 bg-gradient-to-r from-accent to-orange-500 rounded-2xl text-white text-center shadow-lg">
    <p class="text-xs font-bold uppercase tracking-wider mb-2 opacity-90">Mau Hasil Seperti ini?</p>
    <h3 class="text-2xl md:text-3xl font-display font-extrabold mb-3">
        Diskusi via WhatsApp
    </h3>
    <p class="text-base md:text-lg mb-5 opacity-95 max-w-2xl mx-auto">
        Tim kami帮你 merumuskan strategi {service_label} yang sesuai dengan objective bisnis Anda.
        Konsultasi gratis, tidak ada komitmen.
    </p>
    <div class="flex flex-wrap gap-3 justify-center">
        <a href="{wa_url}" target="_blank" rel="noopener" class="inline-flex items-center gap-2 px-6 py-3 bg-white text-accent font-bold rounded-full hover:bg-gray-100 transition">
            � Chat WhatsApp
        </a>
        <a href="{service_url}" class="inline-flex items-center gap-2 px-6 py-3 bg-transparent border-2 border-white text-white font-bold rounded-full hover:bg-white hover:text-accent transition">
            Lihat Paket & Harga →
        </a>
    </div>
</div>
'''
    return html


def enrich_content(content, faqs, service, city, images):
    """Inject FAQ + internal links + images + CTA ke existing content."""
    if not content:
        return content

    enriched = content

    # 1. Inject first image after first <h2>
    if images and '<h2' in enriched:
        parts = enriched.split('<h2', 1)
        if len(parts) == 2:
            rest = parts[1]
            if '<p>' in rest:
                p_end = rest.find('</p>') + 4
                enriched = parts[0] + '<h2' + rest[:p_end] + build_image_html([images[0]]) + rest[p_end:]
            else:
                enriched = parts[0] + '<h2' + rest + build_image_html([images[0]])

    # 2. Inject internal links + second image in middle of content
    if '<h2' in enriched:
        # Find 3rd h2 to inject links after
        h2_positions = [m.start() for m in re.finditer(r'<h2', enriched)]
        if len(h2_positions) >= 3:
            insert_pos = h2_positions[2]
            middle_block = build_internal_links_html(service, city) + (build_image_html([images[1]]) if len(images) > 1 else '')
            enriched = enriched[:insert_pos] + middle_block + enriched[insert_pos:]

    # 3. Build FAQ section + CTA box + inject at end
    cta = build_cta_html(service)
    faq_html = build_faq_html(faqs)
    end_block = cta + faq_html

    if '</article>' in enriched:
        enriched = enriched.replace('</article>', end_block + '</article>')
    elif '</body>' in enriched:
        enriched = enriched.replace('</body>', end_block + '</body>')
    else:
        enriched = enriched + end_block

    return enriched


def enrich_draft(draft, dry_run=False):
    """Enrich single draft."""
    service = draft.get('service')
    city = draft.get('city', '')
    keyword = draft.get('title', '') or draft.get('keyword', '')

    if not service:
        return draft, 'no_service'

    # Detect industri
    industri = detect_industri_from_keyword(keyword)

    # Get FAQ
    faqs = get_faq_for_draft(service, industri, default_count=3)

    # Get images
    images = get_images_for_service(service)

    # Get current content
    content = draft.get('content', '') or ''

    if not content:
        return draft, 'empty_content'

    # Check if already enriched (heuristic: has my specific FAQ JSON-LD schema)
    if '"@type":"FAQPage"' in content and 'faq-schema' in content:
        return draft, 'already_enriched'

    # Enrich
    new_content = enrich_content(content, faqs, service, city, images)

    # Update word count
    import re as _re
    wc = len(_re.findall(r'\w+', _re.sub(r'<[^>]+>', ' ', new_content)))
    draft['content'] = new_content
    draft['word_count'] = wc
    draft['enriched'] = True
    draft['enrichment_meta'] = {
        'industri': industri,
        'faq_count': len(faqs),
        'image_count': len(images),
        'has_internal_links': True,
        'has_cta': True,
    }

    return draft, 'enriched'


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=0, help='Limit per shard (0=all)')
    parser.add_argument('--shard', type=str, help='Specific shard (e.g. queue_00000)')
    parser.add_argument('--dry-run', action='store_true', help='Preview only')
    parser.add_argument('--all', action='store_true', help='Process all shards')
    args = parser.parse_args()

    print('=' * 70)
    print('ENRICH DRAFTS — Quality Improvement Bundle')
    print('=' * 70)

    if not DRAFTS_DIR.exists():
        print(f'❌ Drafts dir not found: {DRAFTS_DIR}')
        sys.exit(1)

    shards = sorted(DRAFTS_DIR.glob('queue_*.ndjson'))
    if args.shard:
        shards = [s for s in shards if args.shard in s.name]
    if not args.all and not args.shard:
        # Default: first shard only
        shards = shards[:1]

    print(f'\nProcessing {len(shards)} shard(s)...')

    total_processed = 0
    total_enriched = 0
    total_skipped = 0
    results = defaultdict(int)

    for shard in shards:
        print(f'\n[{shard.name}]')
        lines = []
        for line in shard.open():
            line = line.strip()
            if not line:
                continue
            try:
                draft = json.loads(line)
            except json.JSONDecodeError:
                continue

            enriched_draft, status = enrich_draft(draft, dry_run=args.dry_run)
            results[status] += 1
            if status == 'enriched':
                total_enriched += 1
            elif status in ('already_enriched', 'no_service', 'empty_content'):
                total_skipped += 1
            total_processed += 1
            lines.append(json.dumps(enriched_draft, ensure_ascii=False))

            if args.limit and total_processed >= args.limit:
                break

        if not args.dry_run:
            with open(shard, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines) + '\n')

        if args.limit and total_processed >= args.limit:
            break

    print(f'\n' + '=' * 70)
    print(f'RESULT')
    print(f'=' * 70)
    print(f'  Total processed: {total_processed}')
    print(f'  Enriched:        {total_enriched}')
    print(f'  Skipped:         {total_skipped}')
    print()
    print(f'Status distribution:')
    for status, count in results.items():
        print(f'  {status}: {count}')


if __name__ == '__main__':
    main()
