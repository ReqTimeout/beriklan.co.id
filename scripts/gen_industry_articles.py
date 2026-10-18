#!/usr/bin/env python3
"""
Generate Industry Articles — Tutorial/Informational content per industri
=========================================================================

Pipeline:
  1. Baca industry-keywords.json (2,291 keyword informasi)
  2. Filter berdasarkan tier (S/A) dan industri priority
  3. Generate artikel via ZEN API (free tier)
  4. Simpan ke drafts/ (LOCAL — tidak auto-publish)
  5. Quality check sebelum simpan

Template per formula:
  - cara-pasang: "Cara X untuk Y" (how-to, 1500 kata)
  - tips: "Tips X untuk Y" (listicle, 1200 kata)
  - panduan: "Panduan X untuk Y" (definitive, 3000 kata)
  - comparison: "X vs Y untuk Z" (comparison, 1800 kata)
  - studi-kasus: "Studi kasus X" (case study, 1500 kata)

Output: drafts/industry_{slug}.json — siap di-import ke publish queue

Usage:
  python3 scripts/gen_industry_articles.py --industri fashion --tier S --limit 5
  python3 scripts/gen_industry_articles.py --all --tier S --limit 50
  python3 scripts/gen_industry_articles.py --dry-run
"""
import os, sys, json, re, time, argparse, requests
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
DRAFTS_DIR = ROOT / 'drafts'
INDUSTRY_KW_FILE = ROOT / 'web/src/data/industry-keywords.json'
SERVICES_FILE = ROOT / 'web/src/data/services.json'
ZEN_KEY_PATH = Path.home() / '.beriklan' / 'zen-key'

ZEN_URL = "https://opencode.ai/zen/v1/chat/completions"
MODELS = ["deepseek-v4-flash-free", "nemotron-3-ultra-free"]

# Service labels untuk prompt
SERVICE_LABELS = {
    'jasa-iklan-facebook': 'Jasa Iklan Facebook',
    'jasa-iklan-instagram': 'Jasa Iklan Instagram',
    'jasa-iklan-tiktok': 'Jasa Iklan TikTok',
    'jasa-iklan-google': 'Jasa Iklan Google',
    'jasa-iklan-youtube': 'Jasa Iklan YouTube',
    'jasa-digital-marketing': 'Jasa Digital Marketing',
    'jasa-pembuatan-website': 'Jasa Pembuatan Website',
    'jasa-pembuatan-landing-page': 'Jasa Landing Page',
    'jasa-kelola-instagram': 'Jasa Kelola Instagram',
    'jasa-kelola-tiktok': 'Jasa Kelola TikTok',
    'jasa-view-live': 'Jasa View Live',
}

INDUSTRY_LABELS = {
    'fashion': 'fashion / hijab / beauty',
    'fnB': 'FnB / kuliner / resto / kafe',
    'kesehatan': 'klinik / kecantikan / kesehatan',
    'properti': 'properti / real estate / perumahan',
    'pendidikan': 'pendidikan / kursus / bootcamp',
    'jasa_b2b': 'jasa profesional / B2B',
    'manufaktur': 'manufaktur / distributor / grosir',
    'otomotif': 'otomotif / showroom / dealer',
    'travel': 'travel / hotel / tour',
}


# ============================================================================
# PROMPT TEMPLATES per FORMULA
# ============================================================================

PROMPT_TEMPLATES = {
    'cara-pasang': """Tulis artikel tutorial Bahasa Indonesia untuk UMKM Indonesia.

Topik: "{keyword}"
Industri target: {industri_label}
Platform iklan: {service_label}

REQUIREMENTS:
- H1: harus persis sama dengan topik di atas (atau sangat mirip)
- 1500-2000 kata
- Structure:
  * Intro 200 kata (apa masalah UMKM di industri {industri_label} saat ini + mengapa perlu iklan)
  * 5-7 step detail dengan sub-heading H2 (Step 1, Step 2, dst)
  * Tiap step: 200-300 kata dengan contoh konkret
  * Tips insider di akhir (100-150 kata)
  * FAQ 3 pertanyaan spesifik (pertanyaan + jawaban 50-80 kata)
- Tone: senior performance marketer yang menjelaskan ke pemula, formal tapi tidak kaku
- Bahasa: Indonesia marketing-friendly, istilah English (ROAS, CPA, pixel) dijelaskan saat pertama muncul
- Hindari: kata "gak", "bikin", "pasti", "garansi 100%", kalimat clickbait
- Internal link 1-2 ke {service_label}: <a href="/{service_slug}/">...</a>
- WhatsApp CTA di akhir: Hubungi tim Beriklan di wa.me/62811919328
- Format HTML: H2, H3, P, UL/OL. Tidak perlu DOCTYPE/HTML.
- Tidak perlu meta description atau schema markup (handled by pipeline).

Output HANYA HTML content (no intro text, no explanation, no markdown wrapper).
""",

    'tips': """Tulis artikel tips Bahasa Indonesia untuk UMKM Indonesia.

Topik: "{keyword}"
Industri target: {industri_label}
Platform iklan: {service_label}

REQUIREMENTS:
- H1: harus persis sama dengan topik di atas
- 1200-1500 kata
- Structure:
  * Intro 150 kata (konteks kenapa tips ini penting)
  * 7-10 tips numbered (H2 untuk tiap tips: "1. ..." atau list)
  * Tiap tips: 1 paragraf + 1 contoh konkret di industri {industri_label}
  * Closing 100 kata: rangkuman + CTA
- Tone: praktis, actionable, langsung to the point
- Bahasa: Indonesia marketing-friendly
- Hindari: kata generik, clickbait, klaim berlebihan
- Internal link ke {service_label}: <a href="/{service_slug}/">...</a>
- WhatsApp CTA di akhir: Hubungi tim Beriklan di wa.me/62811919328
- Format HTML: H2, P, UL. Tidak perlu wrapper.

Output HANYA HTML content.
""",

    'panduan': """Tulis artikel panduan komprehensif Bahasa Indonesia untuk UMKM Indonesia.

Topik: "{keyword}"
Industri target: {industri_label}
Platform iklan: {service_label}

REQUIREMENTS:
- H1: harus persis sama dengan topik
- 2500-3500 kata (panduan lengkap)
- Structure:
  * Intro 200 kata
  * Daftar isi (TOC sederhana dengan anchor link)
  * 5-7 section panjang (H2), tiap section 300-500 kata
  * Comparison table di salah satu section (Meta vs TikTok, dll — yang relevan)
  * Real case study 1 (anonim tapi spesifik, ada angka)
  * FAQ 5 pertanyaan
- Tone: comprehensive, definitive guide, expert
- Bahasa: Indonesia profesional
- Internal link 2-3 ke {service_label}: <a href="/{service_slug}/">...</a>
- WhatsApp CTA di akhir
- Format HTML: H2, H3, P, TABLE, UL/OL

Output HANYA HTML content.
""",

    'comparison': """Tulis artikel perbandingan Bahasa Indonesia untuk UMKM Indonesia.

Topik: "{keyword}"
Industri target: {industri_label}

REQUIREMENTS:
- H1: harus persis sama dengan topik
- 1500-2000 kata
- Structure:
  * Intro 150 kata (kenapa perbandingan ini penting untuk UMKM di {industri_label})
  * Side-by-side comparison table (minimal 8 rows: harga, targeting, audience, ROI, dll)
  * Kelebihan dan kekurangan masing-masing (2 section H2)
  * Use case terbaik untuk masing-masing
  * Rekomendasi final 200 kata: kapan pilih yang mana
- Tone: balanced, fair comparison, expert analysis
- Bahasa: Indonesia marketing-friendly
- Internal link ke layanan terkait di Beriklan (Facebook Ads, TikTok Ads, dll): <a href="/jasa-iklan-{platform}/">...</a>
- WhatsApp CTA di akhir
- Format HTML: H2, TABLE, P, UL

Output HANYA HTML content.
""",

    'studi-kasus': """Tulis artikel studi kasus Bahasa Indonesia (anonymized client story).

Topik: "{keyword}"
Industri target: {industri_label}
Platform iklan: {service_label}

REQUIREMENTS:
- H1: harus persis sama dengan topik
- 1200-1800 kata
- Structure:
  * Intro 150 kata (konteks industri + kenapa studi kasus ini menarik)
  * Background klien (anonim: "Brand A", "Klien X", dll — BUKAN nama asli)
  * Masalah yang dihadapi (200 kata)
  * Strategi yang diterapkan oleh tim Beriklan (400 kata)
  * Hasil dengan angka spesifik (300 kata: ROAS, leads, growth %, dll)
  * Pelajaran & takeaways (200 kata)
  * CTA: "Mau hasil serupa untuk bisnis Anda? Diskusi via WhatsApp..."
- Tone: storytelling, data-driven, professional
- Internal link ke {service_label}: <a href="/{service_slug}/">...</a>
- WhatsApp CTA di akhir dengan ajakan spesifik
- Format HTML: H2, H3, P, UL dengan bullet angka hasil

Output HANYA HTML content.
""",
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def slugify(text):
    s = re.sub(r'[^a-z0-9\s-]', '', text.lower())
    s = re.sub(r'\s+', '-', s).strip('-')
    return s[:80]


def detect_city(keyword):
    """Detect city from keyword."""
    cities = ['jakarta', 'bandung', 'surabaya', 'medan', 'semarang', 'makassar',
              'palembang', 'tangerang', 'depok', 'bekasi', 'bogor', 'batam',
              'yogyakarta', 'malang', 'solo', 'denpasar', 'pekanbaru', 'padang',
              'pontianak', 'banjarmasin', 'manado', 'sidoarjo', 'cimahi', 'lampung']
    kw = keyword.lower()
    for city in cities:
        if f'di {city}' in kw or f' {city} ' in kw:
            return city
    return None


def word_count(html):
    """Count words in HTML content."""
    text = re.sub(r'<[^>]+>', ' ', html)
    return len(re.findall(r'\w+', text))


def call_zen(prompt, model="deepseek-v4-flash-free", max_retries=3):
    """Call ZEN API with retry + model rotation."""
    api_key = ZEN_KEY_PATH.read_text().strip() if ZEN_KEY_PATH.exists() else None
    if not api_key:
        return None, 'No ZEN API key'

    models_to_try = [model] + [m for m in MODELS if m != model]

    for try_model in models_to_try:
        for attempt in range(max_retries):
            try:
                r = requests.post(ZEN_URL,
                    headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                    json={
                        'model': try_model,
                        'messages': [{'role': 'user', 'content': prompt}],
                        'temperature': 0.7,
                        'max_tokens': 3000,  # reduce from 4000 to avoid rate limits
                    },
                    timeout=120,
                )
                if r.status_code == 200:
                    data = r.json()
                    content = data['choices'][0]['message']['content']
                    if content and len(content.strip()) > 100:
                        return content, None
                    # Empty content — retry with same model
                    if attempt < max_retries - 1:
                        time.sleep(3)
                        continue
                    # Try next model
                    break
                elif r.status_code == 429:
                    # Rate limited — wait then retry
                    if attempt < max_retries - 1:
                        time.sleep(10 * (attempt + 1))
                        continue
                    break  # try next model
                else:
                    if attempt < max_retries - 1:
                        time.sleep(3)
                        continue
                    break
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                break
    return None, 'All ZEN models failed after retries'


def qc_article(html, keyword, min_words=600):
    """Quality check: minimal word count + has structure."""
    wc = word_count(html)
    has_h2 = '<h2' in html.lower()
    has_internal_link = 'beriklan.co.id' in html.lower() or '/jasa-' in html.lower() or '/blog/' in html.lower()
    has_cta = 'wa.me' in html.lower() or 'whatsapp' in html.lower()
    issues = []
    if wc < min_words:
        issues.append(f'word_count too low ({wc})')
    if not has_h2:
        issues.append('no H2')
    if not has_cta:
        issues.append('no CTA')
    return len(issues) == 0, issues


def generate_article(keyword_data, model="deepseek-v4-flash-free"):
    """Generate single article."""
    kw = keyword_data['keyword']
    formula = keyword_data['formula']
    service = keyword_data['service']
    industri = keyword_data.get('industri', '')

    template = PROMPT_TEMPLATES.get(formula, PROMPT_TEMPLATES['cara-pasang'])
    prompt = template.format(
        keyword=kw,
        industri_label=INDUSTRY_LABELS.get(industri, industri),
        service_label=SERVICE_LABELS.get(service, service),
        service_slug=service,
    )

    content, err = call_zen(prompt, model)
    if err:
        return None, err

    # QC
    ok, issues = qc_article(content, kw)
    if not ok:
        return None, f'QC failed: {", ".join(issues)}'

    # Build article record
    city = detect_city(kw)
    slug = slugify(kw)

    return {
        'slug': slug,
        'title': kw.title() if not kw[0].isupper() else kw,
        'excerpt': (re.sub(r'<[^>]+>', ' ', content)[:200] + '...').strip(),
        'content': content,
        'date': '',
        'iso_date': '',
        'category': 'strategy' if formula != 'studi-kasus' else 'case-study',
        'readTime': f"{max(3, word_count(content) // 200)} min",
        'tags': [service, industri, formula, city] if city else [service, industri, formula],
        'featured': False,
        'generated': True,
        'service': service,
        'city': city,
        'industri': industri,
        'formula': formula,
        'keyword_source': 'industry-keywords-v1',
        'tier': keyword_data.get('tier', 'B'),
        'score': keyword_data.get('score', 0),
        'word_count': word_count(content),
        'status': 'pending',
        'publish_rank': 100,  # high priority
    }, None


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--industri', type=str, help='Specific industry')
    parser.add_argument('--tier', type=str, default='S', choices=['S', 'A', 'B', 'C'])
    parser.add_argument('--limit', type=int, default=5, help='Limit per industri')
    parser.add_argument('--all', action='store_true', help='Process all keywords')
    parser.add_argument('--dry-run', action='store_true', help='Preview only, no API call')
    parser.add_argument('--model', type=str, default='deepseek-v4-flash-free')
    args = parser.parse_args()

    print('=' * 70)
    print('GEN INDUSTRY ARTICLES')
    print('=' * 70)

    if not INDUSTRY_KW_FILE.exists():
        print(f'❌ Run build_industry_keywords.py first!')
        sys.exit(1)

    all_kws = json.load(open(INDUSTRY_KW_FILE))

    # Filter
    if args.industri:
        all_kws = [k for k in all_kws if k.get('industri') == args.industri]
    if args.tier:
        all_kws = [k for k in all_kws if k.get('tier') == args.tier]

    # Sort by score
    all_kws.sort(key=lambda x: -(x.get('score') or 0))

    if args.limit:
        all_kws = all_kws[:args.limit]

    print(f'\nGenerating {len(all_kws)} articles (industri={args.industri or "all"}, tier={args.tier})')

    if args.dry_run:
        print('DRY RUN — would generate:')
        for k in all_kws:
            print(f'  [{k["tier"]}|{k["score"]}] {k["keyword"]} → {SERVICE_LABELS.get(k["service"], "?")}')
        return

    DRAFTS_DIR.mkdir(exist_ok=True)

    success = 0
    failed = 0
    results = []

    for idx, kw_data in enumerate(all_kws):
        print(f'\n[{idx+1}/{len(all_kws)}] Generating: {kw_data["keyword"][:60]}...')
        article, err = generate_article(kw_data, model=args.model)
        if err:
            print(f'  ❌ {err}')
            failed += 1
        else:
            print(f'  ✅ {article["word_count"]} kata, slug={article["slug"]}')
            results.append(article)
            success += 1

        # Save incremental
        if results and (idx+1) % 5 == 0:
            out_file = DRAFTS_DIR / f'industry_batch_{int(time.time())}.json'
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

        time.sleep(1)  # polite throttle

    # Final save
    if results:
        out_file = DRAFTS_DIR / f'industry_{args.industri or "all"}_{args.tier}.json'
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f'\n✅ Saved {len(results)} articles to {out_file}')

    print(f'\n' + '=' * 70)
    print(f'RESULT: success={success}, failed={failed}')


if __name__ == '__main__':
    main()
