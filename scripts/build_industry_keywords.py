#!/usr/bin/env python3
"""
Build Industry Keywords — Generate keyword informasi per industri
=================================================================

Generate ~1,200 keyword informasi baru per industri dengan 5 formula:

  Formula 1: "Cara [verb] [platform] untuk [industri/sub-niche]"
  Formula 2: "Tips [goal] [platform] [industri]"
  Formula 3: "[Platform] untuk [industri] — Panduan Lengkap"
  Formula 4: "Apa bedanya [X] vs [Y] untuk [industri]"
  Formula 5: "Studi kasus [industri] [goal]"

Output: web/src/data/industry-keywords.json
  [{
    "keyword": "cara iklan instagram untuk toko hijab",
    "keyword_normalized": "cara-iklan-instagram-untuk-toko-hijab",
    "slug": "cara-iklan-instagram-untuk-toko-hijab",
    "industri": "fashion",
    "sub_niche": "toko hijab",
    "service": "jasa-iklan-instagram",
    "formula": "cara-pasang",
    "intent": "informational",
    "tier": "A",
    "score": 87,
    "source": "generated-v1",
  }]

Usage:
  python3 scripts/build_industry_keywords.py --industri fashion --limit 50
  python3 scripts/build_industry_keywords.py --all --out web/src/data/industry-keywords.json
"""
import os, sys, json, re, argparse
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / 'web'

# Load industry categories
INDUSTRY_CATEGORIES_FILE = WEB / 'src' / 'data' / 'industry-categories.json'
SERVICES_FILE = WEB / 'src' / 'data' / 'services.json'

# ============================================================================
# CONFIGURATION
# ============================================================================

# Verbs untuk formula "Cara X untuk Y"
VERBS_CARA = [
    'pasang', 'buat', 'setup', 'mulai', 'jalankan', 'aktifkan',
    'menggunakan', 'memanfaatkan', 'memasang', 'menyetel',
]

# Goals untuk formula "Tips X"
GOALS_TIPS = [
    'naikkan omzet', 'tambah followers', 'dapat leads berkualitas',
    'naikkan ROAS', 'turunkan biaya iklan', 'tingkatkan conversion',
    'viralkan', 'trafik organik', 'engagement tinggi',
    'closing cepat', 'leads konsisten', 'optimasi budget',
    'naikkan penjualan', 'brand awareness', 'jangkau audience baru',
]

# Platforms (semua 10 layanan Beriklan)
PLATFORMS = {
    'jasa-iklan-facebook': {
        'label': 'Facebook Ads',
        'short': 'Facebook',
        'aliases': ['FB Ads', 'Meta Ads', 'Facebook', 'iklan FB'],
        'intent_match': ['conversion', 'awareness', 'leads'],
    },
    'jasa-iklan-instagram': {
        'label': 'Instagram Ads',
        'short': 'Instagram',
        'aliases': ['IG Ads', 'Instagram', 'iklan IG'],
        'intent_match': ['visual', 'engagement', 'conversion'],
    },
    'jasa-iklan-tiktok': {
        'label': 'TikTok Ads',
        'short': 'TikTok',
        'aliases': ['TikTok', 'iklan TikTok', 'Spark Ads'],
        'intent_match': ['viral', 'awareness', 'leads'],
    },
    'jasa-iklan-google': {
        'label': 'Google Ads',
        'short': 'Google',
        'aliases': ['Google Ads', 'Google AdWords', 'iklan Google'],
        'intent_match': ['search', 'leads', 'high-intent'],
    },
    'jasa-iklan-youtube': {
        'label': 'YouTube Ads',
        'short': 'YouTube',
        'aliases': ['YouTube', 'video ads'],
        'intent_match': ['awareness', 'video'],
    },
    'jasa-digital-marketing': {
        'label': 'Digital Marketing',
        'short': 'DM',
        'aliases': ['DM', 'digital marketing'],
        'intent_match': ['general', 'strategy'],
    },
}

# Comparisons untuk formula "Apa bedanya X vs Y"
COMPARISONS = [
    ('Facebook Ads', 'Google Ads'),
    ('Instagram', 'TikTok'),
    ('Meta Ads', 'TikTok Ads'),
    ('Google Ads', 'TikTok Ads'),
    ('Facebook Ads', 'TikTok Ads'),
    ('organic Instagram', 'Instagram Ads'),
    ('organic TikTok', 'TikTok Ads'),
    ('Meta Pixel', 'Google Tag Manager'),
    ('landing page', 'website'),
]

# ============================================================================
# KEYWORD GENERATION
# ============================================================================

def slugify(text):
    """Convert text to URL-safe slug."""
    s = re.sub(r'[^a-z0-9\s-]', '', text.lower())
    s = re.sub(r'\s+', '-', s).strip('-')
    return s[:80]


def score_keyword(keyword, industri, sub_niche, formula, service):
    """Score keyword 0-100 multi-factor.

    Calibration: starts at 40, formula gives 5-20 bonus,
    long-tail + specificity gives 5-15, negatives subtract.
    Tier distribution: S>=75, A>=60, B>=45, C<45.
    """
    score = 40  # base (lower start)

    kw_lower = keyword.lower()

    # Formula bonus (more conservative)
    if formula == 'studi-kasus':
        score += 18
    elif formula == 'cara-pasang':
        score += 12
    elif formula == 'panduan':
        score += 10
    elif formula == 'tips':
        score += 8
    elif formula == 'comparison':
        score += 6

    # Long-tail bonus (5+ kata = bonus)
    wc = len(keyword.split())
    if wc >= 7: score += 12
    elif wc >= 5: score += 8
    elif wc >= 4: score += 4

    # Specificity bonus (mengandung sub-niche spesifik)
    if sub_niche and sub_niche.lower() in kw_lower:
        score += 8

    # Industry-specific bonus (lebih spesifik = lebih tinggi)
    if 'toko' in kw_lower or 'brand' in kw_lower or 'klinik' in kw_lower or 'resto' in kw_lower:
        score += 5

    # Negative: too generic
    if 'jasa iklan' in kw_lower and 'untuk' not in kw_lower:
        score -= 12

    # Negative: just service name without context
    if len(keyword.split()) < 3:
        score -= 10

    return min(100, max(0, score))


def determine_tier(score):
    """Convert score to tier."""
    if score >= 75: return 'S'  # super
    if score >= 60: return 'A'  # high
    if score >= 45: return 'B'  # medium
    return 'C'  # low


def generate_formula_1_cara(industri, sub_niche, service, platform_label):
    """Formula 1: 'Cara [verb] [platform] untuk [industri/sub-niche]'"""
    keywords = []
    verbs_sample = ['pasang', 'mulai', 'buat', 'aktifkan', 'menggunakan', 'jalankan']
    for verb in verbs_sample[:4]:  # 4 verbs per sub-niche
        # With sub-niche
        kw1 = f"cara {verb} {platform_label.lower()} untuk {sub_niche}"
        keywords.append({
            'keyword': kw1,
            'slug': slugify(kw1),
            'industri': industri,
            'sub_niche': sub_niche,
            'service': service,
            'formula': 'cara-pasang',
            'intent': 'informational',
        })
        # With just industri (broader)
        kw2 = f"cara {verb} {platform_label.lower()} untuk bisnis {industri.replace('_', ' ')}"
        keywords.append({
            'keyword': kw2,
            'slug': slugify(kw2),
            'industri': industri,
            'sub_niche': None,
            'service': service,
            'formula': 'cara-pasang',
            'intent': 'informational',
        })
    return keywords


def generate_formula_2_tips(industri, sub_niche, service, platform_label):
    """Formula 2: 'Tips [goal] [platform] [industri/sub-niche]'"""
    keywords = []
    for goal in GOALS_TIPS[:6]:  # top 6 goals
        kw1 = f"tips {goal} {platform_label.lower()} {sub_niche}"
        keywords.append({
            'keyword': kw1,
            'slug': slugify(kw1),
            'industri': industri,
            'sub_niche': sub_niche,
            'service': service,
            'formula': 'tips',
            'intent': 'informational',
        })
        # 5 cara variants
        kw2 = f"5 cara {goal} {platform_label.lower()} untuk {sub_niche}"
        keywords.append({
            'keyword': kw2,
            'slug': slugify(kw2),
            'industri': industri,
            'sub_niche': sub_niche,
            'service': service,
            'formula': 'tips',
            'intent': 'informational',
        })
    return keywords


def generate_formula_3_panduan(industri, sub_niche, service, platform_label):
    """Formula 3: '[Platform] untuk [industri] — Panduan Lengkap'"""
    keywords = []
    # Panduan per sub-niche
    for sn in [sub_niche] + ([industri.replace('_', ' ')] if sub_niche != industri else []):
        kw1 = f"{platform_label} untuk {sn} panduan lengkap"
        keywords.append({
            'keyword': kw1,
            'slug': slugify(kw1),
            'industri': industri,
            'sub_niche': sn,
            'service': service,
            'formula': 'panduan',
            'intent': 'informational',
        })
        # Strategi
        kw2 = f"strategi {platform_label.lower()} untuk {sn}"
        keywords.append({
            'keyword': kw2,
            'slug': slugify(kw2),
            'industri': industri,
            'sub_niche': sn,
            'service': service,
            'formula': 'panduan',
            'intent': 'informational',
        })
        # Contoh
        kw3 = f"contoh {platform_label.lower()} untuk {sn}"
        keywords.append({
            'keyword': kw3,
            'slug': slugify(kw3),
            'industri': industri,
            'sub_niche': sn,
            'service': service,
            'formula': 'panduan',
            'intent': 'informational',
        })
    return keywords


def generate_formula_4_comparison(industri, sub_niche, service, platform_label):
    """Formula 4: 'Apa bedanya [X] vs [Y] untuk [industri]'"""
    keywords = []
    for x, y in COMPARISONS[:5]:
        for target in [sub_niche, industri.replace('_', ' ')]:
            if not target: continue
            kw1 = f"apa bedanya {x.lower()} vs {y.lower()} untuk {target}"
            keywords.append({
                'keyword': kw1,
                'slug': slugify(kw1),
                'industri': industri,
                'sub_niche': sub_niche,
                'service': service,
                'formula': 'comparison',
                'intent': 'informational',
            })
            # "Mana yang lebih baik"
            kw2 = f"mana yang lebih baik {x.lower()} atau {y.lower()} untuk {target}"
            keywords.append({
                'keyword': kw2,
                'slug': slugify(kw2),
                'industri': industri,
                'sub_niche': sub_niche,
                'service': service,
                'formula': 'comparison',
                'intent': 'informational',
            })
    return keywords


def generate_formula_5_case_study(industri, sub_niche, service):
    """Formula 5: 'Studi kasus [industri] [goal]'"""
    keywords = []
    goals = ['naik omzet', 'naikkan penjualan', 'trafik meledak', 'closing konsisten',
             'leads berkualitas', 'ROAS tinggi', 'viral di TikTok']
    for goal in goals:
        kw1 = f"studi kasus {sub_niche} {goal}"
        keywords.append({
            'keyword': kw1,
            'slug': slugify(kw1),
            'industri': industri,
            'sub_niche': sub_niche,
            'service': service,
            'formula': 'studi-kasus',
            'intent': 'informational',
        })
        # Success story
        kw2 = f"kisah sukses {sub_niche} dengan iklan digital"
        keywords.append({
            'keyword': kw2,
            'slug': slugify(kw2),
            'industri': industri,
            'sub_niche': sub_niche,
            'service': service,
            'formula': 'studi-kasus',
            'intent': 'informational',
        })
        # Before-after
        kw3 = f"before after {sub_niche} pakai iklan digital"
        keywords.append({
            'keyword': kw3,
            'slug': slugify(kw3),
            'industri': industri,
            'sub_niche': sub_niche,
            'service': service,
            'formula': 'studi-kasus',
            'intent': 'informational',
        })
    return keywords


def generate_industry_keywords(industri_data, limit_per_niche=20):
    """Generate all formula keywords for one industry."""
    industri_id = industri_data['id']
    sub_niches = industri_data['sub_niches']
    service_primary = industri_data['service_primary']
    service_secondary = industri_data.get('service_secondary', [])
    all_services = [service_primary] + service_secondary

    all_keywords = []

    for sub_niche in sub_niches:
        # Use primary service for most keywords, alternate secondary
        for idx, service in enumerate(all_services[:2]):
            platform_label = PLATFORMS.get(service, {}).get('label', service.replace('jasa-', '').replace('-', ' ').title())

            # Generate each formula
            kws = []
            kws.extend(generate_formula_1_cara(industri_id, sub_niche, service, platform_label))
            kws.extend(generate_formula_2_tips(industri_id, sub_niche, service, platform_label))
            kws.extend(generate_formula_3_panduan(industri_id, sub_niche, service, platform_label))
            kws.extend(generate_formula_4_comparison(industri_id, sub_niche, service, platform_label))
            kws.extend(generate_formula_5_case_study(industri_id, sub_niche, service))

            # Add score + tier
            for kw in kws:
                kw['score'] = score_keyword(kw['keyword'], industri_id, sub_niche, kw['formula'], service)
                kw['tier'] = determine_tier(kw['score'])

            all_keywords.extend(kws)

    # Deduplicate by slug
    seen = set()
    deduped = []
    for kw in all_keywords:
        if kw['slug'] not in seen:
            seen.add(kw['slug'])
            deduped.append(kw)

    # Sort by score desc, take top
    deduped.sort(key=lambda x: -x['score'])
    return deduped[:limit_per_niche * len(sub_niches)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--industri', type=str, help='Specific industry')
    parser.add_argument('--all', action='store_true', help='All industries')
    parser.add_argument('--limit', type=int, default=20, help='Per sub-niche limit')
    parser.add_argument('--out', type=str, default='web/src/data/industry-keywords.json')
    parser.add_argument('--append', action='store_true', help='Append to existing')
    args = parser.parse_args()

    print('=' * 70)
    print('INDUSTRY KEYWORD GENERATOR')
    print('=' * 70)

    # Load industry categories
    if not INDUSTRY_CATEGORIES_FILE.exists():
        print(f'❌ Run scrape_indonetwork_categories.py first!')
        sys.exit(1)
    industries = json.load(open(INDUSTRY_CATEGORIES_FILE))

    # Determine which industries to process
    if args.industri:
        if args.industri not in industries:
            print(f'❌ Industry {args.industri} not found. Available: {list(industries.keys())}')
            sys.exit(1)
        to_process = {args.industri: industries[args.industri]}
    elif args.all:
        to_process = industries
    else:
        print('Specify --industri X or --all')
        sys.exit(1)

    # Generate keywords
    all_kws = []
    for ind_id, ind_data in to_process.items():
        print(f'\n[{ind_id}] {ind_data["label"]} ({len(ind_data["sub_niches"])} sub-niches)...')
        kws = generate_industry_keywords(ind_data, limit_per_niche=args.limit)
        all_kws.extend(kws)
        tier_counts = defaultdict(int)
        for kw in kws:
            tier_counts[kw['tier']] += 1
        print(f'  Generated: {len(kws)} keywords')
        for t in ['S', 'A', 'B', 'C']:
            print(f'    Tier {t}: {tier_counts[t]}')

    # Deduplicate global
    seen = set()
    deduped = []
    for kw in all_kws:
        if kw['slug'] not in seen:
            seen.add(kw['slug'])
            deduped.append(kw)

    # Load existing if append mode
    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if args.append and out_path.exists():
        existing = json.load(open(out_path))
        existing_slugs = {k['slug'] for k in existing}
        deduped = [k for k in deduped if k['slug'] not in existing_slugs]
        print(f'\n[Append mode] Existing: {len(existing)}, New unique: {len(deduped)}')
        existing.extend(deduped)
        final = existing
    else:
        final = deduped

    # Write
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    print(f'\n✅ Wrote {len(final)} keywords to {out_path}')
    tier_counts = defaultdict(int)
    for kw in final:
        tier_counts[kw['tier']] += 1
    print(f'   Distribution: S={tier_counts["S"]}, A={tier_counts["A"]}, B={tier_counts["B"]}, C={tier_counts["C"]}')


if __name__ == '__main__':
    main()
