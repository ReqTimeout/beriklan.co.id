#!/usr/bin/env python3
"""Fase 4 patch #2 — sisa lokalisasi worker MY:
- refreshPrompt (content-refresh) -> English
- buildCityPrompt (city-enrich) -> English Malaysia
- CITY_FOCUS -> English, CITY_NAME_MAP + KW_CITIES -> kota Malaysia
- B4_INTENT -> English words
- public/cities.json (dibaca loadCities via ASSETS) -> data MY dari src/data/cities.json
"""
import json, os, shutil, sys

ROOT = os.path.expanduser("~/Desktop/beriklan.my/web")
WORKER = os.path.join(ROOT, "src/worker-entry.js")

src = open(WORKER).read()
report = []

def splice(start_marker, end_marker, new_text, label, include_end=False):
    global src
    i = src.find(start_marker)
    if i < 0:
        print(f"FAIL [{label}] start not found: {start_marker[:80]!r}"); sys.exit(1)
    j = src.find(end_marker, i + len(start_marker))
    if j < 0:
        print(f"FAIL [{label}] end not found: {end_marker[:80]!r}"); sys.exit(1)
    if include_end:
        j += len(end_marker)
    src = src[:i] + new_text + src[j:]
    report.append(f"{label}: spliced")

def rep(old, new, label):
    global src
    n = src.count(old)
    if n < 1:
        print(f"FAIL [{label}] not found: {old[:80]!r}"); sys.exit(1)
    src = src.replace(old, new)
    report.append(f"{label}: {n}x")

# 1. refreshPrompt -> English (JSON keys intro_baru/update_2026 dipertahankan — dipakai kode)
splice('const refreshPrompt = `Kamu adalah SEO copywriter Indonesia senior.',
       '- Output hanya JSON, no markdown`;',
'''const refreshPrompt = `You are a senior SEO copywriter for the Malaysian market. Task: rewrite the intro paragraph (1 paragraph) + add an "Update 2026:" callout at the end of this existing article for the keyword "${cand.title}".

Existing article:
${(post.content || post.excerpt || "").slice(0, 1500)}

Output format (MUST be valid JSON):
{
  "intro_baru": "...",
  "update_2026": "..."
}

Rules:
- New intro max 80 words, keep the professional Beriklan tone (no overclaiming)
- Update 2026: max 50 words, mention current data/trends (pricing in RM, tools, algorithm changes)
- Address the reader as "you"
- Never write "guaranteed profit" or "100% guarantee"
- Do not change existing H2/H3 headings
- Output JSON only, no markdown`;''', "refresh-prompt", include_end=True)

# 2. CITY_FOCUS -> English service focus (slug MY)
splice("const CITY_FOCUS = {", "};",
'''const CITY_FOCUS = {
  "digital-marketing-agency": "full-service digital marketing (Meta Ads + Google Ads + TikTok Ads + organic content + landing pages + analytics)",
  "facebook-ads-management": "Facebook & Instagram advertising (Meta Ads Manager, pixel, retargeting, lookalike audiences)",
  "google-ads-management": "Google Ads management (Search, Display, YouTube, keyword targeting, conversion tracking)",
  "instagram-ads-management": "Instagram advertising (Reels, Story, Feed, Explore, shop integration, creator collaboration)",
  "tiktok-ads-management": "TikTok advertising (Spark Ads, In-Feed, TopView, FYP targeting, creator marketplace)",
  "youtube-ads-management": "YouTube advertising (TrueView In-Stream, Bumper, Shorts Ads, channel placement)",
  "instagram-management": "organic Instagram management (content calendar, reels production, community management, account growth)",
  "tiktok-management": "organic TikTok management (script writing, consistent video production, FYP optimisation, comment management)",
  "landing-page-design": "landing page design (custom design, fast loading, mobile-optimised, A/B testing ready, Meta/Google pixel integration)",
  "website-development": "professional website development (company profile, online store, custom CMS, SEO-friendly, mobile responsive)",
};''', "city-focus", include_end=True)

# 3. CITY_NAME_MAP -> kota Malaysia
splice("const CITY_NAME_MAP = {", "};",
'''const CITY_NAME_MAP = {
  "kuala-lumpur": "Kuala Lumpur", "petaling-jaya": "Petaling Jaya", "shah-alam": "Shah Alam",
  "subang-jaya": "Subang Jaya", "johor-bahru": "Johor Bahru", penang: "Penang / George Town",
  ipoh: "Ipoh", melaka: "Melaka", seremban: "Seremban", "kota-kinabalu": "Kota Kinabalu",
  kuching: "Kuching", klang: "Klang", putrajaya: "Putrajaya", cyberjaya: "Cyberjaya",
  kuantan: "Kuantan", "alor-setar": "Alor Setar", "kota-bharu": "Kota Bharu",
  "kuala-terengganu": "Kuala Terengganu", miri: "Miri", sandakan: "Sandakan", tawau: "Tawau",
  "iskandar-puteri": "Iskandar Puteri", "batu-pahat": "Batu Pahat", sibu: "Sibu", langkawi: "Langkawi",
};''', "city-name-map", include_end=True)

# 4. buildCityPrompt -> English Malaysia
splice('  return `Kamu copywriter senior untuk agency Beriklan.my (Bandung, sejak 2016).',
       '8. E-E-A-T: Tunjukkan expertise (audit channel, pixel, attribution, geo-targeting) tanpa over-claim.`;',
'''  return `You are a senior copywriter for Beriklan.my, a performance marketing agency serving Malaysian businesses.
Write a short HTML article (500-700 words) in English for a ${focus} landing page targeting ${name}, Malaysia.

Use these local facts about the city (when relevant): ${facts}

STRICT RULES:
1. LANGUAGE: professional English, address the reader as "you", use "we" for the agency. No slang, no marketing emoji.
2. NEVER fabricate numbers: do not write "50+ clients", "4.9 rating", "10x ROAS", or specific testimonials. Focus on observations and how we work.
3. You may mention macro data (internet penetration, e-commerce growth, population) ONLY when plausible for ${name}. When unsure, do NOT quote specific figures.
4. PERSONA: "Senior Performance Marketing Partner" — consultative, never over-promising.
5. STRUCTURE (follow exactly):

<h2>Why Businesses in ${name} Need ${focus.split(" (")[0].replace(/(^|\\s)(\\w)/g, (m, a, b) => a + b.toUpperCase())}</h2>
<p>3-4 sentences of context on why ${name} is a relevant market. Mention dominant industries, consumer behaviour, and why digital channels matter.</p>

<h2>Common Challenges & Mistakes in ${name}</h2>
<p>2-3 sentences of city-specific observations (competition, audience behaviour, knowledge gaps).</p>
<ul>
<li>Bullet 1: a concrete mistake / challenge (3-6 words)</li>
<li>Bullet 2</li>
<li>Bullet 3</li>
<li>Bullet 4</li>
</ul>

<h2>How the Beriklan Team Works for Businesses in ${name}</h2>
<p>1-2 sentence lead.</p>
<ul>
<li><strong>Local Research & Strategy:</strong> 1 sentence on research specific to ${name}.</li>
<li><strong>Setup & Execution:</strong> 1 sentence on technical channel setup.</li>
<li><strong>Optimisation & Reporting:</strong> 1 sentence on the optimisation cycle and reporting.</li>
<li><strong>Long-term Collaboration:</strong> 1 sentence on partnership commitment.</li>
</ul>

<h2>Frequently Asked Questions</h2>
<h3>How much does it cost for a business in ${name}?</h3>
<p>2-3 sentence answer: management fee from RM 800/month + ad spend paid separately to the platform. No guaranteed revenue figures.</p>
<h3>How long until ads go live?</h3>
<p>1 sentence: 3-7 working days after account access is granted.</p>
<h3>Do you have a local team in ${name}?</h3>
<p>1 sentence: the Beriklan team manages campaigns remotely for businesses across Malaysia, with online meetings as needed.</p>
<h3>How do reporting and account access work?</h3>
<p>1 sentence: weekly plain-language reports + full client-side access to Meta/Google/TikTok accounts.</p>

6. OUTPUT: HTML body only (h2/h3/p/ul/li/strong), no <html>, no markdown fences.
7. CITY FOCUS: mention "${name}" naturally at least 6-8 times across the article.
8. E-E-A-T: show expertise (channel audits, pixel, attribution, geo-targeting) without over-claiming.`;''', "city-prompt", include_end=True)

# 5. KW_CITIES -> kota MY (dipakai extractCity untuk klasifikasi keyword)
splice('const KW_CITIES = [', '];',
'''const KW_CITIES = ["kuala lumpur","petaling jaya","shah alam","subang jaya","johor bahru","penang","george town","ipoh","melaka","malacca","seremban","kota kinabalu","kuching","klang","putrajaya","cyberjaya","kuantan","alor setar","kota bharu","kuala terengganu","miri","sandakan","tawau","iskandar puteri","batu pahat","sibu","langkawi","selangor","sabah","sarawak"];''', "kw-cities", include_end=True)

# 6. B4_INTENT -> English
rep('const B4_INTENT = { transactional: "jasa", informational: "panduan", navigational: "info", commercial: "rekomendasi" };',
    'const B4_INTENT = { transactional: "service", informational: "guide", navigational: "info", commercial: "comparison" };',
    "b4-intent")

open(WORKER, "w").write(src)

# 7. public/cities.json -> data MY (loadCities di worker baca file ini via ASSETS)
src_cities = os.path.join(ROOT, "src/data/cities.json")
pub_cities = os.path.join(ROOT, "public/cities.json")
data = json.load(open(src_cities))
assert any(c["slug"] == "kuala-lumpur" for c in data) and not any(c["slug"] == "bandung" for c in data)
shutil.copyfile(src_cities, pub_cities)
report.append(f"public/cities.json: replaced with {len(data)} MY cities")

print("\n".join(report))
print("OK")
