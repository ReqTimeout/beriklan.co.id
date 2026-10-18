#!/usr/bin/env python3
"""
Keyword Miner — Beriklan.my (Malaysian market)
===============================================
Port of beriklan.co.id keyword_miner.py + expand_massive_v4.py, adapted per plan Fase 3:
  F3-1  Google Suggest with &hl=en&gl=my (English results, Malaysia geo)
  F3-2  English SERVICES seeds + live-commerce/marketplace seeds (differentiator)
  F3-3  CITIES = 15 MY cities + modifiers: malaysia, kl, near me, selangor
  F3-4  International layer (gl=sg) with LOWER priority_score
  F3-5  English policy filter (ban "guaranteed #1", "cheapest" claim keywords)
  F3-6  Target ±5,000 validated MY keywords

Strategies:
  1. Google Suggest live mining (hl=en&gl=my) — real Malaysian autocomplete demand
  2. Combinatorial English expansion — services x industries x intent patterns x cities
  3. International layer — singapore/southeast asia suffixes (priority_score -15)

Output (same schema as .co.id keyword-queue.json — downstream compatible):
  web/src/data/keyword-queue.json        ranked queue
  web/src/data/keyword-queue-stats.json  mining summary
  web/public/data/keyword-queue.json     public copy (dashboard)

Usage:
  python3 scripts/keyword_miner.py             # full run (Suggest + expansion)
  python3 scripts/keyword_miner.py --no-suggest # expansion only (offline)
  python3 scripts/keyword_miner.py --dry-run    # preview only
"""
import os, sys, json, re, time, argparse, urllib.request, urllib.parse
from datetime import datetime, timezone

# Resolve project root: works both from beriklan.my/scripts/ and _my_migration/
_here = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(_here) == '_my_migration':
    ROOT = os.path.expanduser('~/Desktop/beriklan.my')
else:
    ROOT = os.path.dirname(_here)
WEB = os.path.join(ROOT, 'web')
QUEUE_OUT = os.path.join(WEB, 'src/data/keyword-queue.json')
STATS_OUT = os.path.join(WEB, 'src/data/keyword-queue-stats.json')
PUBLIC_QUEUE_OUT = os.path.join(WEB, 'public/data/keyword-queue.json')
CITIES_JSON = os.path.join(WEB, 'src/data/cities.json')

NOW = datetime.now(timezone.utc).isoformat()

# ─── Services (slugs match beriklan.my page routes) ────────────────────────
# (slug, primary seed, [extra suggest seeds])
SERVICES = [
    ('facebook-ads-management', 'facebook ads agency', [
        'facebook advertising services', 'meta ads agency', 'facebook ads management',
        'fb ads agency', 'facebook marketing agency']),
    ('instagram-ads-management', 'instagram ads agency', [
        'instagram advertising services', 'instagram ads management', 'ig ads agency']),
    ('tiktok-ads-management', 'tiktok ads agency', [
        'tiktok advertising services', 'tiktok ads management', 'tiktok marketing agency']),
    ('google-ads-management', 'google ads agency', [
        'google ads management', 'ppc management', 'sem agency', 'google adwords agency',
        'ppc agency', 'search engine marketing services']),
    ('youtube-ads-management', 'youtube ads agency', [
        'youtube advertising services', 'video ads agency', 'youtube marketing agency']),
    ('instagram-management', 'instagram management services', [
        'social media management instagram', 'instagram account management',
        'instagram content management']),
    ('tiktok-management', 'tiktok management services', [
        'tiktok account management', 'tiktok content creation services']),
    ('website-development', 'website design malaysia', [
        'web design services', 'website development company', 'web designer',
        'ecommerce website design', 'company website design']),
    ('landing-page-design', 'landing page design', [
        'landing page design services', 'sales page design', 'landing page agency']),
    ('digital-marketing-agency', 'digital marketing agency', [
        'digital marketing services', 'online marketing agency', 'performance marketing agency',
        'social media marketing agency', 'digital advertising agency']),
    # Live-commerce & marketplace seeds — key differentiator (plan F3-2)
    ('tiktok-live-viewers', 'tiktok live viewers', [
        'buy tiktok live views', 'tiktok live viewers booster', 'boost tiktok live',
        'increase tiktok live viewers', 'tiktok live selling']),
    ('shopee-live-viewers', 'shopee live viewers', [
        'boost shopee live', 'shopee live views', 'shopee live selling',
        'shopee live selling tips', 'increase shopee live viewers']),
    ('instagram-live-viewers', 'instagram live viewers', [
        'buy instagram live views', 'boost instagram live', 'increase instagram live viewers']),
    ('youtube-live-viewers', 'youtube live viewers', [
        'buy youtube live views', 'boost youtube live stream', 'youtube live stream viewers']),
    ('twitch-live-viewers', 'twitch viewers', [
        'buy twitch viewers', 'twitch live viewers', 'boost twitch stream']),
    ('live-stream-viewers', 'live stream boost malaysia', [
        'live selling malaysia', 'live commerce malaysia', 'live streaming service malaysia',
        'live stream marketing', 'live host service malaysia']),
]

# ─── Malaysian cities (must match cities.json slugs) ────────────────────────
CITY_NAMES = {
    'kuala-lumpur': 'kuala lumpur', 'petaling-jaya': 'petaling jaya',
    'shah-alam': 'shah alam', 'subang-jaya': 'subang jaya',
    'johor-bahru': 'johor bahru', 'penang': 'penang', 'ipoh': 'ipoh',
    'melaka': 'melaka', 'seremban': 'seremban', 'kota-kinabalu': 'kota kinabalu',
    'kuching': 'kuching', 'klang': 'klang', 'putrajaya': 'putrajaya',
    'cyberjaya': 'cyberjaya', 'kuantan': 'kuantan',
}
TIER1_CITIES = ['kuala lumpur', 'kl', 'petaling jaya', 'johor bahru', 'penang', 'shah alam']
GEO_MODIFIERS = ['malaysia', 'kl', 'selangor', 'near me']  # plan F3-3

# ─── Malaysian industries (SME/e-commerce context) ─────────────────────────
INDUSTRIES = [
    ('e-commerce', ['e-commerce', 'online store', 'online business']),
    ('property', ['property', 'real estate', 'property developer']),
    ('education', ['education', 'tuition centre', 'training centre']),
    ('healthcare', ['clinic', 'healthcare', 'dental clinic', 'aesthetic clinic']),
    ('fnb', ['restaurant', 'f&b', 'cafe', 'food business']),
    ('fashion', ['fashion brand', 'clothing brand', 'boutique']),
    ('beauty', ['beauty salon', 'skincare brand', 'cosmetics brand']),
    ('travel', ['hotel', 'travel agency', 'homestay']),
    ('automotive', ['car dealer', 'automotive', 'car workshop']),
    ('professional-services', ['law firm', 'accounting firm', 'consultancy']),
    ('halal', ['halal products', 'halal food business', 'muslimah fashion']),
]

# ─── Intent modifiers English (plan F3.1) ───────────────────────────────────
INTENT_PREFIX = ['best', 'top', 'affordable', 'hire', 'professional', 'trusted']
INTENT_SUFFIX = ['price', 'pricing', 'cost', 'packages', 'for sme', 'for small business',
                 'freelance vs agency', 'services', '2026']
# Live-viewer boosting: buying a service, NOT an agency-hire decision → restricted set
LIVE_INTENT_PREFIX = ['best', 'cheap', 'affordable', 'real', 'instant', 'safe']
LIVE_INTENT_SUFFIX = ['price', 'pricing', 'cost', 'packages', 'service', 'cheap', '2026']
QUESTION_TEMPLATES = [
    'how much does {kw} cost in malaysia',
    'how much is {kw} in malaysia',
    'is {kw} worth it',
    'why hire {kw}',
    'what is {kw}',
    'how to choose {kw} in malaysia',
]

# International layer (plan F3-4) — lower priority
INTL_SUFFIX = ['singapore', 'southeast asia']

# ─── Bahasa Melayu layer (Malaysian market is bilingual EN/BM) ──────────────
# Malay service terms per slug (grammatically correct MY search phrasing).
# 'agency'-type services take agensi/khidmat; live-viewer services take penonton.
MALAY_NAMES = {
    'facebook-ads-management': ['iklan facebook', 'iklan fb'],
    'instagram-ads-management': ['iklan instagram'],
    'tiktok-ads-management': ['iklan tiktok'],
    'google-ads-management': ['iklan google'],
    'youtube-ads-management': ['iklan youtube'],
    'instagram-management': ['pengurusan instagram', 'urus akaun instagram'],
    'tiktok-management': ['pengurusan tiktok', 'urus akaun tiktok'],
    'website-development': ['buat laman web', 'reka bentuk laman web', 'bina website'],
    'landing-page-design': ['reka bentuk landing page', 'buat landing page'],
    'digital-marketing-agency': ['pemasaran digital', 'agensi pemasaran digital'],
    'tiktok-live-viewers': ['penonton tiktok live', 'tambah viewers tiktok live'],
    'shopee-live-viewers': ['penonton shopee live', 'tambah penonton shopee live'],
    'instagram-live-viewers': ['penonton instagram live'],
    'youtube-live-viewers': ['penonton youtube live'],
    'twitch-live-viewers': ['penonton twitch'],
    'live-stream-viewers': ['tambah penonton live', 'khidmat live streaming'],
}
# Malay commercial patterns for agency-type services ({s} = malay service term)
MALAY_AGENCY_PATTERNS = [
    '{s} malaysia', 'agensi {s}', 'agensi {s} malaysia', 'khidmat {s}',
    'harga {s}', 'harga {s} malaysia', 'kos {s}', 'pakej {s}', 'pakej {s} malaysia',
    '{s} murah', '{s} terbaik', '{s} terbaik malaysia', '{s} profesional',
    'syarikat {s}', 'buat {s}', 'cara buat {s}',
]
# Malay patterns for live-viewer boosting services
MALAY_LIVE_PATTERNS = [
    '{s}', '{s} malaysia', 'cara {s}', 'cara tambah {s}', 'beli {s}',
    'khidmat {s}', 'harga {s}', '{s} murah', 'boost {s}',
]
MALAY_CITY_NAMES = ['kuala lumpur', 'petaling jaya', 'johor bahru', 'penang', 'shah alam']

# ─── Policy filter (English context per plan F3-5) ──────────────────────────
EXCLUDE = re.compile(
    r'\b(porn|sex|nude|casino|gambling|judi|slot|hack|crack|cheat|free download|'
    r'bokep|onlyfans|bitcoin|crypto trading|escort|drugs|weapon|'
    r'guaranteed\s*#?\s*1|guarantee\s*#?\s*1|cheapest|100%\s*guaranteed|scam)\b',
    re.IGNORECASE,
)
# Foreign-geo noise from Suggest (not our market — filter out)
FOREIGN_GEO = re.compile(
    r'\b(india|kannur|kerala|mumbai|delhi|philippines|manila|nigeria|lagos|'
    r'pakistan|karachi|dhaka|bangladesh|vietnam|hanoi|thailand|bangkok|'
    r'indonesia|jakarta|surabaya|bandung|dubai|uae|london|uk\b|usa|new york|'
    r'australia|sydney)\b',
    re.IGNORECASE,
)
# Out-of-scope services / navigational junk (we do NOT offer Lazada/Tokopedia work;
# drop people looking for a platform's own support hotline/CS — not our customers)
EXCLUDE_SCOPE = re.compile(
    r'\b(lazada|tokopedia|shopee)\b.*\b(customer service|hotline|support|seller center|'
    r'seller centre|contact number|phone number|helpline|complaint|refund|return)\b'
    r'|\b(customer service|hotline|helpline|contact number|phone number|call center|call centre)\b'
    r'|\b(lazada|tokopedia)\b',
    re.IGNORECASE,
)
# NOTE: Malay-language keywords are INTENTIONALLY KEPT — Bahasa Melayu is a primary
# search language for the Malaysian market (bilingual EN/BM). No non-English filter.


def slugify(text):
    s = text.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'\s+', '-', s)
    return re.sub(r'-+', '-', s).strip('-')


def normalize(s):
    return re.sub(r'\s+', ' ', s.strip().lower())


def priority_score(kw, source):
    """Heuristic 0-100. Higher = more valuable for beriklan.my."""
    k = kw.lower()
    s = 40
    if 'malaysia' in k: s += 12
    if any(c in k for c in TIER1_CITIES): s += 8
    if any(w in k for w in ['agency', 'services', 'management', 'company']): s += 10
    # Malay commercial equivalents — weight on par with English
    if any(w in k for w in ['agensi', 'khidmat', 'syarikat', 'pengurusan']): s += 10
    if any(w in k for w in ['price', 'pricing', 'cost', 'how much', 'packages', 'rate',
                            'harga', 'kos', 'pakej']): s += 8
    if any(w in k for w in ['best', 'top', 'affordable', 'hire', 'trusted',
                            'terbaik', 'murah', 'profesional']): s += 6
    if any(w in k for w in ['sme', 'small business']): s += 5
    if any(w in k for w in ['live viewers', 'live views', 'shopee live', 'tiktok live',
                            'live selling', 'live commerce', 'live stream']): s += 8
    if any(w in k for w in ['2026', '2027']): s += 4
    if any(w in k for w in ['how to', 'what is', 'why ', 'is it']): s += 3
    if source == 'suggest_my': s += 6          # real autocomplete demand
    if any(w in k for w in INTL_SUFFIX): s -= 15  # intl layer lower (F3-4)
    if len(kw) > 65: s -= 10
    if len(kw) < 10: s -= 5
    return min(100, max(0, s))


def infer_intent(kw):
    k = kw.lower()
    if any(w in k for w in ['how much', 'price', 'pricing', 'cost', 'packages', 'hire', 'buy ',
                            'harga', 'kos', 'pakej', 'beli']):
        return 'transactional'
    if any(w in k for w in ['how to', 'what is', 'why ', 'is it', 'tips', 'guide', 'vs ', 'cara ']):
        return 'informational'
    return 'commercial'


# Malay function/marker words to tag keyword language
_MALAY_MARKER = re.compile(
    r'\b(agensi|khidmat|harga|kos|pakej|murah|terbaik|profesional|syarikat|buat|bina|'
    r'cara|beli|tambah|penonton|pengurusan|urus|akaun|laman|reka|bentuk|iklan)\b',
    re.IGNORECASE,
)


def detect_language(kw):
    """Tag as 'ms' (Bahasa Melayu) or 'en'. Both are valid for the MY market."""
    return 'ms' if _MALAY_MARKER.search(kw) else 'en'


def google_suggest(query, max_results=8, gl='my'):
    try:
        url = ('http://suggestqueries.google.com/complete/search?client=firefox'
               f'&hl=en&gl={gl}&q=' + urllib.parse.quote(query))
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        })
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            return data[1][:max_results] if len(data) > 1 else []
    except Exception:
        return []


def build_suggest_tasks(intl=False):
    """(query, service_slug, gl) tuples for parallel Suggest mining."""
    tasks = []
    for slug, primary, extras in SERVICES:
        seeds = [primary] + extras
        for seed in seeds:
            tasks.append((seed, slug, 'my'))
            tasks.append((f'{seed} malaysia', slug, 'my'))
        # geo variants only on primary seed (limit query volume)
        for geo in ['kl', 'selangor', 'near me']:
            tasks.append((f'{primary} {geo}', slug, 'my'))
        for city in ['kuala lumpur', 'penang', 'johor bahru', 'petaling jaya']:
            tasks.append((f'{primary} {city}', slug, 'my'))
        # intent probes
        tasks.append((f'best {primary}', slug, 'my'))
        tasks.append((f'{primary} price', slug, 'my'))
        tasks.append((f'how much {primary}', slug, 'my'))
        # Bahasa Melayu probes — discover real Malay long-tails from Suggest
        for mname in MALAY_NAMES.get(slug, []):
            tasks.append((mname, slug, 'my'))
            tasks.append((f'harga {mname}', slug, 'my'))
            tasks.append((f'{mname} malaysia', slug, 'my'))
        if intl:
            tasks.append((f'{primary} singapore', slug, 'sg'))
    return tasks


def mine_suggest(intl=False):
    from concurrent.futures import ThreadPoolExecutor, as_completed
    tasks = build_suggest_tasks(intl)
    print(f'  Launching {len(tasks)} Suggest queries (hl=en&gl=my, 10 workers)...', file=sys.stderr)
    results = []  # (keyword, service_slug, source)
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(google_suggest, q, 8, gl): (q, slug, gl)
                   for q, slug, gl in tasks}
        done = 0
        for f in as_completed(futures):
            q, slug, gl = futures[f]
            done += 1
            for s in f.result():
                s = s.strip()
                if not (5 < len(s) < 80):
                    continue
                if EXCLUDE.search(s) or FOREIGN_GEO.search(s) or EXCLUDE_SCOPE.search(s):
                    continue
                src = 'suggest_my' if gl == 'my' else 'suggest_intl'
                results.append((s, slug, src))
            if done % 50 == 0:
                print(f'   ...{done}/{len(tasks)} queries, {len(results)} raw', file=sys.stderr)
    return results


def expand_combinatorial():
    """v4-style English expansion: services x patterns x industries x cities."""
    out = []  # (keyword, service_slug, source, city_slug, industry)

    for slug, primary, extras in SERVICES:
        is_live = 'live' in slug or slug == 'live-stream-viewers'
        seeds = [primary] + extras[:2]
        pats = []  # (text, city_slug, industry)

        for seed in seeds:
            # Geo-neutral base: strip 'malaysia' from seeds that already carry it
            # (avoids awkward double-geo like 'live selling malaysia kuala lumpur')
            base = re.sub(r'\s*\bmalaysia\b\s*', ' ', seed).strip()
            # Core geo patterns
            pats.append((f'{base} malaysia', None, None))
            for geo in GEO_MODIFIERS:
                pats.append((f'{base} {geo}', None, None))
            # Intent prefix/suffix (restricted set for live-viewer boosting)
            pre_set = LIVE_INTENT_PREFIX if is_live else INTENT_PREFIX
            suf_set = LIVE_INTENT_SUFFIX if is_live else INTENT_SUFFIX
            for pre in pre_set:
                pats.append((f'{pre} {base} malaysia', None, None))
                pats.append((f'{pre} {base} in kl', None, None))
            for suf in suf_set:
                pats.append((f'{base} {suf} malaysia', None, None))
                pats.append((f'{seed} {suf}', None, None))
            # Questions
            for tpl in QUESTION_TEMPLATES:
                pats.append((tpl.format(kw=base), None, None))
            # Cities — every seed x every city
            for cslug, cname in CITY_NAMES.items():
                pats.append((f'{base} {cname}', cslug, None))
                pats.append((f'{base} in {cname}', cslug, None))
            for cname in ['kuala lumpur', 'penang', 'johor bahru']:
                cslug = {'kuala lumpur': 'kuala-lumpur', 'penang': 'penang',
                         'johor bahru': 'johor-bahru'}[cname]
                pats.append((f'best {base} in {cname}', cslug, None))
                pats.append((f'{base} {cname} price', cslug, None))
            # International layer (F3-4)
            for suf in INTL_SUFFIX:
                pats.append((f'{base} {suf}', None, None))

        # Industries (skip for live-viewer boosting — not industry-targeted)
        if not is_live:
            for ind_id, aliases in INDUSTRIES:
                for alias in aliases[:2]:
                    pats.append((f'{primary} for {alias}', None, ind_id))
                    pats.append((f'{primary} for {alias} malaysia', None, ind_id))
                    pats.append((f'best {primary} for {alias}', None, ind_id))

        # ── Service-specific deep patterns ──
        deep = []
        if slug == 'facebook-ads-management':
            deep = ['meta ads for small business malaysia', 'facebook ads cost malaysia',
                    'facebook ads course vs agency malaysia', 'facebook lead generation malaysia',
                    'facebook retargeting ads malaysia', 'fb ads specialist malaysia',
                    'facebook ads for online sellers malaysia', 'meta business partner malaysia']
        elif slug == 'instagram-ads-management':
            deep = ['instagram reels ads malaysia', 'instagram story ads malaysia',
                    'instagram shopping ads malaysia', 'instagram ads cost malaysia',
                    'ig ads for online boutique malaysia']
        elif slug == 'tiktok-ads-management':
            deep = ['tiktok shop ads malaysia', 'spark ads malaysia', 'tiktok ads cost malaysia',
                    'tiktok shop seller malaysia', 'tiktok affiliate marketing malaysia',
                    'tiktok ads for ecommerce malaysia', 'fyp marketing malaysia']
        elif slug == 'google-ads-management':
            deep = ['google search ads malaysia', 'performance max malaysia',
                    'google shopping ads malaysia', 'google display ads malaysia',
                    'google ads cost malaysia', 'sem services malaysia',
                    'google local ads malaysia', 'ppc for lead generation malaysia']
        elif slug == 'youtube-ads-management':
            deep = ['youtube video ads malaysia', 'youtube bumper ads malaysia',
                    'youtube ads cost malaysia', 'video marketing agency malaysia',
                    'youtube brand awareness campaign malaysia']
        elif slug == 'instagram-management':
            deep = ['instagram content calendar service', 'instagram growth service malaysia',
                    'social media manager malaysia', 'instagram posting service malaysia',
                    'instagram engagement service malaysia']
        elif slug == 'tiktok-management':
            deep = ['tiktok content creator service malaysia', 'tiktok growth service malaysia',
                    'tiktok video editing service malaysia', 'ugc creator malaysia']
        elif slug == 'website-development':
            deep = ['ecommerce website malaysia', 'company profile website malaysia',
                    'wordpress developer malaysia', 'website maintenance malaysia',
                    'business website price malaysia', 'shopify developer malaysia',
                    'seo friendly website design malaysia', 'corporate website design malaysia']
        elif slug == 'landing-page-design':
            deep = ['high converting landing page malaysia', 'sales funnel design malaysia',
                    'landing page for google ads malaysia', 'landing page with whatsapp button',
                    'lead generation landing page malaysia']
        elif slug == 'digital-marketing-agency':
            deep = ['digital marketing for sme malaysia', 'marketing agency for startups malaysia',
                    'full service digital agency malaysia', 'digital marketing consultant malaysia',
                    'online advertising services malaysia', 'digital marketing packages malaysia',
                    'boutique marketing agency kl', 'b2b digital marketing malaysia']
        elif slug == 'tiktok-live-viewers':
            deep = ['tiktok live viewers malaysia', 'buy tiktok live views malaysia',
                    'tiktok live boost service', 'tiktok live selling boost malaysia',
                    'increase tiktok live audience', 'tiktok live engagement service']
        elif slug == 'shopee-live-viewers':
            deep = ['shopee live viewers malaysia', 'boost shopee live malaysia',
                    'shopee live streaming service', 'shopee live selling malaysia',
                    'increase shopee live audience malaysia']
        elif slug == 'instagram-live-viewers':
            deep = ['instagram live viewers malaysia', 'boost ig live views',
                    'instagram live audience boost']
        elif slug == 'youtube-live-viewers':
            deep = ['youtube live viewers malaysia', 'boost youtube live stream views',
                    'youtube live concurrent viewers']
        elif slug == 'twitch-live-viewers':
            deep = ['twitch viewers malaysia', 'boost twitch live stream',
                    'twitch channel growth service']
        elif slug == 'live-stream-viewers':
            deep = ['live commerce agency malaysia', 'live selling service malaysia',
                    'live stream shopping malaysia', 'live host training malaysia',
                    'live stream production malaysia']
        for d in deep:
            pats.append((d, None, None))
            pats.append((f'{d} price', None, None))

        for text, cslug, ind in pats:
            out.append((text, slug, 'expansion_my', cslug, ind))

        # ── Bahasa Melayu expansion (controlled, grammatically correct) ──
        malay_pats = MALAY_LIVE_PATTERNS if is_live else MALAY_AGENCY_PATTERNS
        for mname in MALAY_NAMES.get(slug, []):
            for tpl in malay_pats:
                out.append((tpl.format(s=mname), slug, 'expansion_ms', None, None))
            # Malay + tier-1 city
            for cname in MALAY_CITY_NAMES:
                cslug = cname.replace(' ', '-')
                out.append((f'{mname} {cname}', slug, 'expansion_ms', cslug, None))
                if not is_live:
                    out.append((f'agensi {mname} {cname}', slug, 'expansion_ms', cslug, None))
    return out


def main():
    p = argparse.ArgumentParser(description='Beriklan.my keyword miner (Malaysia)')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--no-suggest', action='store_true')
    p.add_argument('--no-intl', action='store_true', help='Skip international layer')
    p.add_argument('--cap', type=int, default=6500, help='Max queue size')
    args = p.parse_args()

    print('=== Beriklan.my Keyword Miner ===', file=sys.stderr)

    # Strategy 1: Google Suggest (live MY demand)
    suggest_rows = []
    if not args.no_suggest:
        print('1. Google Suggest mining (hl=en&gl=my)...', file=sys.stderr)
        suggest_rows = mine_suggest(intl=not args.no_intl)
        print(f'   {len(suggest_rows)} raw suggestions', file=sys.stderr)

    # Strategy 2: Combinatorial expansion
    print('2. Combinatorial English expansion...', file=sys.stderr)
    expansion_rows = [(kw, slug, src, c, i) for kw, slug, src, c, i in expand_combinatorial()]
    print(f'   {len(expansion_rows)} expansion patterns', file=sys.stderr)

    # Merge: suggest rows have no city/industry annotation
    all_rows = [(kw, slug, src, None, None) for kw, slug, src in suggest_rows] + expansion_rows

    # Dedupe + build queue entries
    seen, queue = set(), []
    for kw, svc, src, city, ind in all_rows:
        norm = normalize(kw)
        slug = slugify(norm)
        if not norm or not slug or norm in seen:
            continue
        if EXCLUDE.search(norm) or FOREIGN_GEO.search(norm) or EXCLUDE_SCOPE.search(norm):
            continue
        # Defensive: drop awkward double-geo ('... malaysia <city/geo> ...')
        tail = norm.split('malaysia', 1)[1] if 'malaysia' in norm else ''
        if tail and (any(c in tail for c in CITY_NAMES.values())
                     or re.search(r'\b(kl|selangor|near me|malaysia)\b', tail)):
            continue
        seen.add(norm)
        queue.append({
            'keyword': kw.strip(),
            'keyword_normalized': norm,
            'slug': slug,
            'has_post': False,
            'priority_score': priority_score(norm, src),
            'source': src,
            'status': 'pending',
            'rank': 0,
            'created_at': NOW,
            'service': svc,
            'city': city,
            'industry': ind,
            'intent': infer_intent(norm),
            'language': detect_language(norm),
            'country': 'SG' if any(w in norm for w in INTL_SUFFIX) else 'MY',
        })

    queue.sort(key=lambda x: -x['priority_score'])
    if args.cap and len(queue) > args.cap:
        queue = queue[:args.cap]
    for i, item in enumerate(queue):
        item['rank'] = i

    # Stats
    by_service = {}
    for q in queue:
        by_service[q['service']] = by_service.get(q['service'], 0) + 1
    stats = {
        'last_run': NOW,
        'market': 'MY',
        'total_raw': len(all_rows),
        'queue_size': len(queue),
        'from_suggest': sum(1 for q in queue if q['source'].startswith('suggest')),
        'from_expansion': sum(1 for q in queue if q['source'].startswith('expansion')),
        'international': sum(1 for q in queue if q['country'] != 'MY'),
        'high_priority': sum(1 for q in queue if q['priority_score'] >= 60),
        'by_language': {
            'en': sum(1 for q in queue if q['language'] == 'en'),
            'ms': sum(1 for q in queue if q['language'] == 'ms'),
        },
        'by_service': dict(sorted(by_service.items(), key=lambda x: -x[1])),
        'by_intent': {
            'transactional': sum(1 for q in queue if q['intent'] == 'transactional'),
            'commercial': sum(1 for q in queue if q['intent'] == 'commercial'),
            'informational': sum(1 for q in queue if q['intent'] == 'informational'),
        },
        'sample_top20': [{'keyword': q['keyword'], 'score': q['priority_score'],
                          'source': q['source']} for q in queue[:20]],
    }

    print(f'\n=== Queue summary ===', file=sys.stderr)
    print(f'Queue size: {stats["queue_size"]}', file=sys.stderr)
    print(f'From Suggest: {stats["from_suggest"]} | Expansion: {stats["from_expansion"]}', file=sys.stderr)
    print(f'High priority (>=60): {stats["high_priority"]}', file=sys.stderr)
    print(f'By service: {json.dumps(stats["by_service"], indent=1)}', file=sys.stderr)
    print(f'\nTop 20:', file=sys.stderr)
    for s in stats['sample_top20']:
        print(f'  [{s["score"]:3d}] ({s["source"]}) {s["keyword"]}', file=sys.stderr)

    if args.dry_run:
        print('\n[DRY RUN] Not writing.', file=sys.stderr)
        return

    for path, data in [(QUEUE_OUT, queue), (STATS_OUT, stats), (PUBLIC_QUEUE_OUT, queue)]:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f'Wrote {path}', file=sys.stderr)


if __name__ == '__main__':
    main()
