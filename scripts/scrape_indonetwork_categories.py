#!/usr/bin/env python3
"""
Scrape Indonetwork Categories — Build Indonesian Industry Map
=============================================================

Indonetwork.co.id adalah B2B directory Indonesia dengan 3M+ members.
Tapi halaman kategori di-render via JavaScript, sehingga static scrape
tidak dapat list kategori secara langsung.

Pendekatan hybrid:
  1. Static scrape (jika ada halaman kategori statis)
  2. Pakai URL pattern yang sudah dikenal dari search engines
  3. Pakai manual curated industry list (KLUI/KBLI-based)
  4. Verify dengan existing keywords.json (1,478 keyword)

Output: web/src/data/industry-categories.json
  {
    "fashion": {
      "label": "Fashion & Lifestyle",
      "slug": "fashion",
      "service_primary": "jasa-iklan-instagram",
      "service_secondary": ["jasa-kelola-instagram", "jasa-iklan-facebook"],
      "kbli": ["14101", "14102", ...],
      "indonetwork_categories": ["pakaian-wanita", "pakaian-pria", ...],
      "sub_niches": ["toko hijab", "brand fashion", "dropshipper", ...],
      "search_volume_band": "high",
      "lead_quality": "⭐⭐⭐⭐⭐"
    }
  }

Usage:
  python3 scripts/scrape_indonetwork_categories.py            # generate from curated + keywords
  python3 scripts/scrape_indonetwork_categories.py --live    # attempt live scrape (best-effort)
"""
import os, sys, json, re, time, argparse, urllib.request, urllib.error, urllib.parse
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / 'web'
OUT = WEB / 'src' / 'data' / 'industry-categories.json'
KEYWORDS_JSON = WEB / 'src' / 'data' / 'keywords.json'


# =============================================================================
# CURATED INDUSTRY LIST (KBLI/ KLUI based + Indonetwork URL patterns)
# =============================================================================
# Mapping industri → sub-niche → search keywords
# Berangkat dari struktur direktori bisnis Indonesia + keyword patterns

INDUSTRIES = {
    "fashion": {
        "label": "Fashion & Lifestyle",
        "icon": "👗",
        "service_primary": "jasa-iklan-instagram",
        "service_secondary": ["jasa-kelola-instagram", "jasa-iklan-facebook", "jasa-iklan-tiktok"],
        "indonetwork_categories": [
            "pakaian-wanita", "pakaian-pria", "baju-muslim-wanita", "baju-muslim-pria",
            "kaos-dan-atasan-wanita", "kaos-dan-atasan-pria", "aksesoris-fashion",
            "tas-wanita", "sepatu-wanita", "sepatu-pria", "jam-tangan",
            "fashion-anak", "busana-muslim", "gamis", "hijab", "jilbab",
        ],
        "sub_niches": [
            "toko hijab", "brand fashion lokal", "brand skincare", "brand kosmetik",
            "dropshipper baju", "reseller fashion", "brand pakaian muslim",
            "konveksi", "butik online", "fashion thrift", "preloved",
        ],
        "products": ["baju", "kemeja", "kaos", "celana", "rok", "dress", "gamis", "hijab", "jilbab", "mukena", "sarung", "sepatu", "tas", "jam tangan"],
        "search_volume_band": "very_high",
        "lead_quality": "⭐⭐⭐⭐⭐",
        "pain_points": [
            "foto produk kurang menarik", "tidak punya strategi konten",
            "ROAS Facebook/Instagram Ads rendah", "followers sepi",
            "tidak tahu Meta Pixel", "competitor harga lebih murah tapi laku",
        ],
    },
    "fnB": {
        "label": "Food & Beverage / Kuliner",
        "icon": "🍔",
        "service_primary": "jasa-iklan-tiktok",
        "service_secondary": ["jasa-iklan-facebook", "jasa-digital-marketing", "jasa-iklan-instagram"],
        "indonetwork_categories": [
            "makanan-dan-minuman", "makanan-ringan", "kue-dan-roti", "kopi-dan-teh",
            "makanan-sehat", "snack", "kerupuk", "bumbu-dan-bahan-masakan",
            "minuman", "jus", "es-krim", "catering", "restoran", "rumah-makan",
            "warung", "kafe", "kantin",
        ],
        "sub_niches": [
            "kafe / coffee shop", "restoran", "warung makan", "catering kantor",
            "snack kiloan", "kue ulang tahun", "roti & pastry", "brand minuman kekinian",
            "franchise F&B", "brand makanan viral", "frozen food", "sambal kemasan",
        ],
        "products": ["kopi", "teh", "jus", "roti", "kue", "snack", "kerupuk", "sambal", "bumbu", "ayam", "nasi box", "catering"],
        "search_volume_band": "very_high",
        "lead_quality": "⭐⭐⭐⭐⭐",
        "pain_points": [
            "resto sepi pengunjung", "GoFood/GrabFood order sepi", "rating Google Maps rendah",
            "konten TikTok kurang menarik", "iklan F&B mahal tapi closing sedikit",
            "tidak bisa viralkan menu baru",
        ],
    },
    "kesehatan": {
        "label": "Kesehatan / Klinik / Kecantikan",
        "icon": "🏥",
        "service_primary": "jasa-iklan-instagram",
        "service_secondary": ["jasa-iklan-facebook", "jasa-kelola-instagram", "jasa-pembuatan-landing-page"],
        "indonetwork_categories": [
            "alat-kesehatan", "obat-obatan", "suplemen-kesehatan", "klinik",
            "kecantikan", "salon", "spa", "skincare", "kosmetik", "perawatan-kulit",
            "dokter", "klinik-gigi", "klinik-kecantikan", "rumah-sakit",
            "alat-medis", "peralatan-kesehatan",
        ],
        "sub_niches": [
            "klinik kecantikan", "klinik gigi", "klinik estetika", "botox & filler",
            "skincare brand", "salon rambut", "barbershop", "nail art", "spa",
            "dokter praktik", "rumah sakit", "bidan praktik", "klinik hewan",
            "brand obat herbal", "suplemen fitness",
        ],
        "products": ["skincare", "serum", "moisturizer", "sunscreen", "masker wajah", "lipstik", "foundation", "alat medis", "obat", "vitamin"],
        "search_volume_band": "high",
        "lead_quality": "⭐⭐⭐⭐⭐",
        "pain_points": [
            "klinik sepi pasien", "tidak percaya diri edukasi medis",
            "budget iklan tinggi tapi closing sedikit", "Meta Pixel kurang optimal",
            "kompetitor punya lebih banyak review",
        ],
    },
    "properti": {
        "label": "Properti / Real Estate",
        "icon": "🏠",
        "service_primary": "jasa-iklan-google",
        "service_secondary": ["jasa-iklan-facebook", "jasa-pembuatan-landing-page", "jasa-pembuatan-website"],
        "indonetwork_categories": [
            "properti", "perumahan", "rumah-dijual", "apartemen", "villa",
            "ruko", "tanah", "kavling", "developer", "real-estate",
            "properti-komersial", "gudang", "pabrik", "kantor",
        ],
        "sub_niches": [
            "developer perumahan", "agen properti", "marketing properti",
            "showrum", "kantor pemasaran", "properti komersial",
            "kontraktor", "arsitek", "interior designer",
        ],
        "products": ["rumah", "apartemen", "ruko", "villa", "tanah", "kavling", "ruang kantor", "gudang"],
        "search_volume_band": "very_high",
        "lead_quality": "⭐⭐⭐⭐⭐",
        "pain_points": [
            "lead qualified susah", "budget iklan tinggi tapi closing sedikit",
            "kompetitor banyak", "Meta Pixel tidak nyangkut", "landing page konversi rendah",
        ],
    },
    "pendidikan": {
        "label": "Pendidikan / Kursus / Bootcamp",
        "icon": "🎓",
        "service_primary": "jasa-iklan-facebook",
        "service_secondary": ["jasa-pembuatan-landing-page", "jasa-iklan-tiktok", "jasa-iklan-google"],
        "indonetwork_categories": [
            "pendidikan", "kursus", "pelatihan", "bimbingan-belajar", "bimbel",
            "sekolah", "universitas", "bootcamp", "edukasi", "les-private",
            "bahasa-inggris", "komputer", "desain",
        ],
        "sub_niches": [
            "bootcamp programming", "kursus bahasa Inggris", "les privat",
            "kursus online", "webinar berbayar", "training korporat",
            "edukasi anak", "PAUD/TK", "bimbel masuk PTN",
        ],
        "products": ["kelas online", "bootcamp", "kursus bahasa", "les privat", "webinar", "sertifikasi"],
        "search_volume_band": "high",
        "lead_quality": "⭐⭐⭐⭐",
        "pain_points": [
            "cost per lead terlalu tinggi", "penerimaan学员 sedikit",
            "konten edukasi kurang menarik", "Meta Pixel belum di-setup",
            "kompetitor punya webinar funnel lebih baik",
        ],
    },
    "jasa_b2b": {
        "label": "Jasa / B2B / Profesional",
        "icon": "💼",
        "service_primary": "jasa-iklan-google",
        "service_secondary": ["jasa-iklan-facebook", "jasa-pembuatan-website", "jasa-pembuatan-landing-page"],
        "indonetwork_categories": [
            "jasa", "konsultan", "layanan-profesional", "konsultan-it",
            "konsultan-pemasaran", "konsultan-hukum", "konsultan-bisnis",
            "keuangan", "akunting", "audit", "pajak", "legal",
            "periklanan", "agensi",
        ],
        "sub_niches": [
            "konsultan IT", "konsultan hukum", "konsultan pajak", "konsultan HR",
            "jasa software house", "agensi digital", "jasa audit",
            "virtual assistant", "freelance",
        ],
        "products": ["konsultasi", "software", "aplikasi", "layanan profesional", "audit", "legal opinion"],
        "search_volume_band": "medium",
        "lead_quality": "⭐⭐⭐⭐⭐",
        "pain_points": [
            "B2B lead susah dapat", "decision maker susah di-target",
            "tidak tahu Meta Pixel untuk B2B", "tidak bisa nurture long funnel",
            "tidak punya CRM",
        ],
    },
    "manufaktur": {
        "label": "Manufaktur / Distributor / B2B Wholesale",
        "icon": "🏭",
        "service_primary": "jasa-iklan-google",
        "service_secondary": ["jasa-pembuatan-website", "jasa-pembuatan-landing-page", "jasa-iklan-facebook"],
        "indonetwork_categories": [
            "manufaktur", "pabrik", "distributor", "grosir", "supplier",
            "bahan-baku", "produk-setengah-jadi", "komponen",
        ],
        "sub_niches": [
            "pabrik makanan", "pabrik minuman", "pabrik tekstil",
            "pabrik plastik", "pabrik logam", "konveksi",
            "distributor ATK", "distributor bahan bangunan",
            "eksportir", "importir",
        ],
        "products": ["bahan baku", "produk jadi", "komponen", "paket grosir"],
        "search_volume_band": "medium",
        "lead_quality": "⭐⭐⭐⭐",
        "pain_points": [
            "B2B susah digital marketing", "tidak tahu Google Ads untuk B2B",
            "MOQ tinggi tapi closing susah", "ekspor tidak ada yang handle",
            "tidak ada inquiry form",
        ],
    },
    "otomotif": {
        "label": "Otomotif / Showroom / Dealer",
        "icon": "�",
        "service_primary": "jasa-iklan-facebook",
        "service_secondary": ["jasa-iklan-google", "jasa-iklan-tiktok"],
        "indonetwork_categories": [
            "otomotif", "mobil", "motor", "sparepart", "bengkel",
            "showroom", "dealer", "aksesoris-mobil", "aksesoris-motor",
            "ban", "oli",
        ],
        "sub_niches": [
            "showroom mobil baru", "showroom mobil bekas", "dealer motor",
            "bengkel resmi", "bengkel umum", "sparepart shop",
            "aksesoris mobil", "modifikasi mobil",
        ],
        "products": ["mobil", "motor", "sparepart", "ban", "oli", "aksesoris"],
        "search_volume_band": "high",
        "lead_quality": "⭐⭐⭐",
        "pain_points": [
            "leads sepi", "kompetitor besar", "budget iklan tinggi",
            "tidak bisa follow up leads tepat waktu", "test drive booking rendah",
        ],
    },
    "travel": {
        "label": "Travel / Tourism / Hotel",
        "icon": "✈️",
        "service_primary": "jasa-iklan-tiktok",
        "service_secondary": ["jasa-iklan-facebook", "jasa-iklan-google"],
        "indonetwork_categories": [
            "travel", "tour", "liburan", "hotel", "penginapan",
            "villa", "homestay", "tour-operator", "tiket-pesawat",
            "tour-haji", "tour-umrah",
        ],
        "sub_niches": [
            "tour domestik", "tour internasional", "umrah & haji",
            "homestay", "villa", "hotel butik", "guest house",
            "rental mobil", "paket honeymoon",
        ],
        "products": ["paket tour", "tiket pesawat", "hotel", "villa", "homestay", "rental"],
        "search_volume_band": "high",
        "lead_quality": "⭐⭐⭐",
        "pain_points": [
            "pemesanan sepi", "seasonal demand", "kompetitor banyak",
            "Meta Pixel untuk travel susah", "ROAS TikTok rendah",
        ],
    },
}


def load_existing_keywords():
    """Load existing keywords.json to verify industry mentions."""
    if not KEYWORDS_JSON.exists():
        return []
    return json.load(open(KEYWORDS_JSON))


def detect_industry_from_keyword(keyword):
    """Detect which industry a keyword belongs to."""
    kw = keyword.lower()
    matches = []
    for ind_id, ind_data in INDUSTRIES.items():
        score = 0
        # Check sub_niches
        for niche in ind_data['sub_niches']:
            if niche.lower() in kw:
                score += 3
        # Check products
        for prod in ind_data['products']:
            if prod.lower() in kw:
                score += 2
        # Check indonetwork categories
        for cat in ind_data['indonetwork_categories']:
            if cat.replace('-', ' ') in kw:
                score += 1
        if score > 0:
            matches.append((ind_id, score))
    return sorted(matches, key=lambda x: -x[1])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true', help='Attempt live scrape (best-effort)')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    print('=' * 70)
    print('INDUSTRY CATEGORIES BUILDER — Indonetwork Hybrid')
    print('=' * 70)

    # 1. Load existing keywords
    keywords = load_existing_keywords()
    print(f'\n[1/4] Loaded {len(keywords)} existing keywords')

    # 2. For each industry, count keyword matches
    print(f'\n[2/4] Matching keywords to industries...')
    industry_keyword_map = defaultdict(list)
    for kw in keywords:
        matches = detect_industry_from_keyword(kw.get('keyword_normalized') or kw.get('keyword', ''))
        for ind_id, score in matches[:1]:  # best match only
            industry_keyword_map[ind_id].append({
                'keyword': kw.get('keyword'),
                'volume': kw.get('volume', 0),
                'intent': kw.get('intent'),
                'score': score,
            })

    # 3. Sort by volume and pick top 30 per industry
    industry_summary = {}
    for ind_id, ind_data in INDUSTRIES.items():
        matched = industry_keyword_map.get(ind_id, [])
        matched_sorted = sorted(matched, key=lambda x: -(x.get('volume') or 0))[:30]
        total_vol = sum((m.get('volume') or 0) for m in matched)

        industry_summary[ind_id] = {
            **ind_data,
            'id': ind_id,
            'existing_keyword_count': len(matched),
            'total_existing_volume': total_vol,
            'top_existing_keywords': [m['keyword'] for m in matched_sorted[:10]],
        }

        if args.verbose:
            print(f'  {ind_id:<15} ({len(matched):>3} kw, vol={total_vol:>5}): {ind_data["label"]}')

    # 4. Optional: try live scrape (best-effort)
    if args.live:
        print(f'\n[3/4] Attempting live scrape (best-effort)...')
        try:
            # Try fetching indonetwork main page to get category links
            url = 'https://www.indonetwork.co.id/'
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; BeriklanBot/1.0)'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode('utf-8', errors='ignore')

            # Extract category URLs (best-effort regex)
            cat_urls = re.findall(r'href=["\']([^"\']*?/k/[^"\']+?)["\']', html)
            print(f'  Found {len(cat_urls)} potential category URLs (best-effort)')
        except Exception as e:
            print(f'  Live scrape skipped: {e}')

    # 5. Write output
    print(f'\n[4/4] Writing output to {OUT}')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(industry_summary, f, ensure_ascii=False, indent=2)

    print(f'\n✅ Generated industry-categories.json')
    print(f'   Industries: {len(industry_summary)}')
    total_sub = sum(len(d['sub_niches']) for d in industry_summary.values())
    total_cat = sum(len(d['indonetwork_categories']) for d in industry_summary.values())
    print(f'   Total sub-niches: {total_sub}')
    print(f'   Total Indonetwork categories: {total_cat}')
    print(f'   Total existing keyword matches: {sum(d["existing_keyword_count"] for d in industry_summary.values())}')

    return industry_summary


if __name__ == '__main__':
    main()
