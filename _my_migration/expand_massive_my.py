#!/usr/bin/env python3
"""
expand_massive_my.py — F3b: combinatorial keyword expansion for beriklan.my.

Mirrors .co.id's expansion stack (expand_massive_v4 + expand_intent_layers) but
for Malaysia: 16 services x 25 MY cities x ~35 local industries x bilingual
(English + Bahasa Melayu) intent templates.

Layers:
  L1  service x city                (EN + MS)
  L2  service x industry            (EN + MS)
  L3  service x industry x city     (EN + MS)  <- volume driver
  L4  comparison pairs (x vs y) x industry (x city)
  L5  live-viewer buying-intent layer (platforms x cities x segments)
  L6  question/year layer on service bases

Rules (from mining correctness requirements):
  - BOTH English and Malay — Malay is a primary MY search language
  - NO Lazada/Tokopedia, no foreign geo (indonesia/jakarta/india...)
  - live-viewer services use buying modifiers (cheap/instant/real/safe/price/buy),
    not agency-hire modifiers
Appends to web/src/data/keyword-queue.json, dedupes by keyword_normalized.
Idempotent: re-running dedupes against existing entries.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

ROOT = os.path.expanduser("~/Desktop/beriklan.my")
QUEUE_PATH = os.path.join(ROOT, "web/src/data/keyword-queue.json")
CITIES_PATH = os.path.join(ROOT, "web/src/data/cities.json")

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

BANNED = ("lazada", "tokopedia", "indonesia", "jakarta", "bandung", "surabaya",
          "india", "customer service", "hotline", "support number")

# ---------------------------------------------------------------- dimensions
cities_raw = json.load(open(CITIES_PATH))
CITIES = [c["name"].lower() for c in cities_raw if not c.get("is_international")]

# (slug, [EN phrases], [MS phrases])  — agency-type services
AGENCY_SERVICES = [
    ("facebook-ads-management", ["facebook ads services", "facebook advertising"],
     ["iklan facebook", "iklan fb"]),
    ("instagram-ads-management", ["instagram ads services", "instagram advertising"],
     ["iklan instagram"]),
    ("tiktok-ads-management", ["tiktok ads services", "tiktok advertising"],
     ["iklan tiktok"]),
    ("google-ads-management", ["google ads services", "google ads management"],
     ["iklan google"]),
    ("youtube-ads-management", ["youtube ads services", "youtube advertising"],
     ["iklan youtube"]),
    ("instagram-management", ["instagram management services", "social media management instagram"],
     ["urus instagram", "pengurusan instagram"]),
    ("tiktok-management", ["tiktok management services", "tiktok content management"],
     ["urus tiktok", "pengurusan tiktok"]),
    ("website-development", ["website development", "web design services"],
     ["buat website", "bina laman web"]),
    ("landing-page-design", ["landing page design", "landing page services"],
     ["buat landing page", "landing page murah"]),
    ("digital-marketing-agency", ["digital marketing agency", "digital marketing services"],
     ["agensi pemasaran digital", "pemasaran digital"]),
]

# (slug, EN platform label, MS phrases)
LIVE_SERVICES = [
    ("tiktok-live-viewers", "tiktok live viewers", ["penonton live tiktok", "viewers live tiktok"]),
    ("instagram-live-viewers", "instagram live viewers", ["penonton live instagram"]),
    ("shopee-live-viewers", "shopee live viewers", ["penonton live shopee", "viewers shopee live"]),
    ("youtube-live-viewers", "youtube live viewers", ["penonton live youtube"]),
    ("twitch-live-viewers", "twitch live viewers", ["penonton live twitch"]),
    ("live-stream-viewers", "live stream viewers", ["penonton live streaming"]),
]

# (key, [EN aliases], [MS aliases])
INDUSTRIES = [
    ("fnb", ["f&b business", "restaurant", "cafe", "food business"], ["restoran", "kafe", "bisnes makanan"]),
    ("halal-food", ["halal food business", "halal restaurant"], ["makanan halal"]),
    ("property", ["property", "real estate", "property developer"], ["hartanah", "ejen hartanah"]),
    ("ecommerce", ["ecommerce", "online store", "online shop"], ["kedai online", "bisnes online"]),
    ("education", ["education", "tuition centre", "training centre"], ["pusat tuisyen", "pendidikan"]),
    ("healthcare", ["healthcare", "clinic", "dental clinic"], ["klinik", "klinik gigi"]),
    ("beauty", ["beauty salon", "skincare brand", "spa"], ["salon kecantikan", "produk kecantikan"]),
    ("fashion", ["fashion brand", "boutique", "clothing brand"], ["butik", "jenama fesyen"]),
    ("travel", ["travel agency", "hotel", "homestay"], ["agensi pelancongan", "homestay"]),
    ("automotive", ["car dealer", "car workshop", "automotive business"], ["kedai kereta", "bengkel kereta"]),
    ("professional-services", ["law firm", "accounting firm", "consulting firm"], ["firma guaman", "firma akaun"]),
    ("fitness", ["gym", "fitness studio"], ["pusat kecergasan"]),
    ("home-services", ["renovation company", "aircond service", "cleaning service"], ["syarikat renovasi", "servis aircond"]),
    ("logistics", ["logistics company", "courier service"], ["syarikat logistik"]),
    ("retail", ["retail store", "grocery store"], ["kedai runcit"]),
    ("electronics", ["electronics store", "gadget store"], ["kedai gadget"]),
    ("jewellery", ["jewellery store", "gold shop"], ["kedai emas"]),
    ("furniture", ["furniture store", "home decor store"], ["kedai perabot"]),
    ("insurance", ["insurance agent", "takaful agent"], ["ejen takaful", "ejen insurans"]),
    ("wedding", ["wedding planner", "event management"], ["perancang perkahwinan", "pengurusan majlis"]),
    ("photography", ["photography studio", "photographer"], ["jurugambar"]),
    ("pets", ["pet shop", "pet grooming"], ["kedai haiwan"]),
    ("childcare", ["kindergarten", "childcare centre"], ["tadika", "taska"]),
    ("agriculture", ["agriculture business", "durian farm"], ["bisnes pertanian", "kebun durian"]),
    ("manufacturing", ["manufacturer", "factory"], ["kilang"]),
    ("islamic-products", ["muslimah fashion", "islamic products"], ["fesyen muslimah", "produk muslimah"]),
    ("beverage", ["bubble tea shop", "coffee shop"], ["kedai kopi"]),
    ("bakery", ["bakery", "cake shop"], ["kedai kek"]),
    ("optical", ["optical shop"], ["kedai cermin mata"]),
    ("pharmacy", ["pharmacy"], ["farmasi"]),
    ("tech", ["tech startup", "software company"], ["syarikat perisian"]),
    ("finance", ["financial advisor", "money lender"], ["penasihat kewangan"]),
    ("supplements", ["health supplements brand"], ["produk kesihatan"]),
    ("skincare-msme", ["small business", "sme"], ["perniagaan kecil", "usahawan"]),
    ("dropship", ["dropship business", "reseller business"], ["bisnes dropship", "ejen dropship"]),
]

# comparison pairs (EN phrase a, EN phrase b, MS a, MS b, service attributed)
COMPARISONS = [
    ("facebook ads", "google ads", "iklan facebook", "iklan google", "facebook-ads-management"),
    ("facebook ads", "instagram ads", "iklan facebook", "iklan instagram", "facebook-ads-management"),
    ("facebook ads", "tiktok ads", "iklan facebook", "iklan tiktok", "tiktok-ads-management"),
    ("google ads", "tiktok ads", "iklan google", "iklan tiktok", "google-ads-management"),
    ("google ads", "youtube ads", "iklan google", "iklan youtube", "youtube-ads-management"),
    ("instagram ads", "tiktok ads", "iklan instagram", "iklan tiktok", "instagram-ads-management"),
    ("tiktok ads", "youtube ads", "iklan tiktok", "iklan youtube", "tiktok-ads-management"),
    ("google ads", "seo", "iklan google", "seo", "google-ads-management"),
    ("facebook ads", "seo", "iklan facebook", "seo", "facebook-ads-management"),
    ("instagram management", "tiktok management", "urus instagram", "urus tiktok", "instagram-management"),
    ("website", "landing page", "website", "landing page", "landing-page-design"),
    ("digital marketing agency", "in-house marketing", "agensi pemasaran", "pemasaran sendiri", "digital-marketing-agency"),
]

YEARS = ["2026", "2027"]

# ---------------------------------------------------------------- helpers
def norm(kw):
    return re.sub(r"\s+", " ", kw.strip().lower())

def slugify(text):
    s = re.sub(r"[^a-z0-9\s-]", "", text.lower())
    return re.sub(r"\s+", "-", s).strip("-")[:80]

def score(kw):
    base = 30
    if any(m in kw for m in ("price", "cost", "cheap", "affordable", "package", "promo",
                             "harga", "kos", "murah", "pakej", "buy", "beli")): base += 25
    if any(y in kw for y in YEARS): base += 12
    if any(m in kw for m in ("how ", "what ", "which ", "berapa", "macam mana", "adakah")): base += 15
    if any(m in kw for m in ("best", "top", "trusted", "professional", "terbaik", "dipercayai")): base += 10
    if any(c in kw for c in CITIES): base += 10
    if " for " in kw or " untuk " in kw: base += 5
    return min(base, 100)

def intent_of(kw):
    if any(m in kw for m in ("buy", "beli", "price", "harga", "kos", "cost", "cheap",
                             "murah", "pakej", "package", "promo")): return "transactional"
    if any(m in kw for m in (" vs ", " or ", " atau ", "which is better", "mana lebih",
                             "difference", "perbezaan")): return "comparison"
    if any(m in kw for m in ("how ", "what ", "why ", "berapa", "macam mana", "cara ")): return "informational"
    return "commercial"

def mk(kw, service, source, language, city=None, industry=None):
    kw = re.sub(r"\s+", " ", kw).strip()
    return {
        "keyword": kw,
        "keyword_normalized": norm(kw),
        "slug": slugify(kw),
        "has_post": False,
        "priority_score": score(norm(kw)),
        "source": source,
        "status": "pending",
        "rank": None,
        "created_at": NOW,
        "service": service,
        "city": city,
        "industry": industry,
        "intent": intent_of(norm(kw)),
        "language": language,
        "country": "my",
    }

# ---------------------------------------------------------------- layers
def generate():
    out = []
    add = out.append

    # ---- L1: service x city ----
    for slug, ens, mss in AGENCY_SERVICES:
        for s in ens:
            for c in CITIES:
                for t in (f"{s} {c}", f"{s} in {c}", f"best {s} {c}", f"{s} {c} price",
                          f"affordable {s} {c}", f"{s} near me {c}", f"top {s} in {c}",
                          f"{s} company {c}", f"trusted {s} {c}", f"cheap {s} {c}"):
                    add(mk(t, slug, "expansion_l2_en", "en", city=c))
        for s in mss:
            for c in CITIES:
                for t in (f"{s} {c}", f"harga {s} {c}", f"pakej {s} {c}", f"{s} murah {c}",
                          f"agensi {s} {c}", f"khidmat {s} {c}", f"{s} terbaik {c}"):
                    add(mk(t, slug, "expansion_l2_ms", "ms", city=c))

    # ---- L2: service x industry ----
    for slug, ens, mss in AGENCY_SERVICES:
        s = ens[0]; sm = mss[0]
        for _key, i_ens, i_mss in INDUSTRIES:
            for ind in i_ens:
                for t in (f"{s} for {ind}", f"best {s} for {ind}", f"{s} for {ind} malaysia",
                          f"affordable {s} for {ind}", f"how much does {s} cost for {ind}",
                          f"is {s} worth it for {ind}", f"{s} package for {ind}",
                          f"{s} for {ind} price"):
                    add(mk(t, slug, "expansion_l2_en", "en", industry=_key))
            for ind in i_mss:
                for t in (f"{sm} untuk {ind}", f"harga {sm} untuk {ind}",
                          f"pakej {sm} untuk {ind}", f"{sm} murah untuk {ind}"):
                    add(mk(t, slug, "expansion_l2_ms", "ms", industry=_key))

    # ---- L3: service x industry x city (volume driver) ----
    for slug, ens, mss in AGENCY_SERVICES:
        s = ens[0]; s2 = ens[1] if len(ens) > 1 else ens[0]
        sm = mss[0]
        for _key, i_ens, i_mss in INDUSTRIES:
            ind = i_ens[0]; ind2 = i_ens[1] if len(i_ens) > 1 else i_ens[0]
            indm = i_mss[0]
            for c in CITIES:
                for t in (f"{s} for {ind} in {c}", f"{s} for {ind} {c}",
                          f"best {s} for {ind} in {c}", f"{s2} for {ind2} in {c}",
                          f"affordable {s} for {ind} {c}", f"{s} for {ind} in {c} price",
                          f"{s} package for {ind} {c}", f"how much {s} for {ind} in {c}",
                          f"top {s} for {ind2} {c}", f"cheap {s2} for {ind} {c}",
                          f"{s} for {ind} near {c}", f"trusted {s} for {ind} in {c}"):
                    add(mk(t, slug, "expansion_l3_en", "en", city=c, industry=_key))
                for t in (f"{sm} untuk {indm} di {c}", f"harga {sm} untuk {indm} {c}",
                          f"pakej {sm} {indm} {c}", f"{sm} murah untuk {indm} di {c}",
                          f"agensi {sm} untuk {indm} {c}"):
                    add(mk(t, slug, "expansion_l3_ms", "ms", city=c, industry=_key))

    # ---- L4: comparisons ----
    for a, b, am, bm, svc in COMPARISONS:
        for t in (f"{a} vs {b}", f"{a} or {b}", f"which is better {a} or {b}",
                  f"difference between {a} and {b}", f"{a} vs {b} malaysia",
                  f"{a} vs {b} which is cheaper", f"{a} vs {b} for small business"):
            add(mk(t, svc, "expansion_l4_en", "en"))
        for t in (f"{am} atau {bm}", f"{am} vs {bm}", f"mana lebih baik {am} atau {bm}",
                  f"perbezaan {am} dan {bm}"):
            add(mk(t, svc, "expansion_l4_ms", "ms"))
        for _key, i_ens, i_mss in INDUSTRIES:
            ind = i_ens[0]; indm = i_mss[0]
            for t in (f"{a} vs {b} for {ind}", f"{a} or {b} for {ind}",
                      f"which is better {a} or {b} for {ind}"):
                add(mk(t, svc, "expansion_l4_en", "en", industry=_key))
            add(mk(f"{am} atau {bm} untuk {indm}", svc, "expansion_l4_ms", "ms", industry=_key))
            for c in CITIES:
                add(mk(f"{a} vs {b} for {ind} in {c}", svc, "expansion_l4_en", "en", city=c, industry=_key))
                add(mk(f"{a} or {b} for {ind} {c}", svc, "expansion_l4_en", "en", city=c, industry=_key))

    # ---- L5: live-viewer buying layer ----
    SEGMENTS_EN = ["live seller", "online seller", "streamer", "live commerce", "small business"]
    SEGMENTS_MS = ["penjual live", "peniaga online", "streamer"]
    for slug, en, mss in LIVE_SERVICES:
        for t in (f"buy {en}", f"buy {en} malaysia", f"cheap {en}", f"cheap {en} malaysia",
                  f"{en} price", f"{en} price malaysia", f"real {en}", f"{en} no bots",
                  f"instant {en}", f"{en} package", f"is buying {en} safe",
                  f"how to increase {en.replace(' viewers',' viewer count')}",
                  f"{en} trial", f"best site to buy {en}", f"{en} per session price"):
            add(mk(t, slug, "expansion_l5_en", "en"))
        for seg in SEGMENTS_EN:
            for t in (f"{en} for {seg}", f"buy {en} for {seg}", f"cheap {en} for {seg}"):
                add(mk(t, slug, "expansion_l5_en", "en"))
        for c in CITIES:
            for t in (f"buy {en} {c}", f"{en} {c}", f"cheap {en} {c}", f"{en} price {c}",
                      f"real {en} {c}"):
                add(mk(t, slug, "expansion_l5_en", "en", city=c))
        for s in mss:
            for t in (f"beli {s}", f"{s} murah", f"harga {s}", f"tambah {s}",
                      f"{s} selamat", f"pakej {s}", f"beli {s} malaysia"):
                add(mk(t, slug, "expansion_l5_ms", "ms"))
            for seg in SEGMENTS_MS:
                add(mk(f"{s} untuk {seg}", slug, "expansion_l5_ms", "ms"))
            for c in CITIES:
                add(mk(f"beli {s} {c}", slug, "expansion_l5_ms", "ms", city=c))
                add(mk(f"{s} murah {c}", slug, "expansion_l5_ms", "ms", city=c))

    # ---- L6: question + year layers on service bases ----
    for slug, ens, mss in AGENCY_SERVICES:
        s = ens[0]; sm = mss[0]
        for y in YEARS:
            for t in (f"{s} malaysia {y}", f"best {s} {y}", f"{s} price {y}",
                      f"{s} cost malaysia {y}", f"{s} trends {y}"):
                add(mk(t, slug, "expansion_l6_en", "en"))
            add(mk(f"harga {sm} {y}", slug, "expansion_l6_ms", "ms"))
            add(mk(f"{sm} terbaik {y}", slug, "expansion_l6_ms", "ms"))
            for c in CITIES:
                add(mk(f"{s} {c} {y}", slug, "expansion_l6_en", "en", city=c))
        for t in (f"how to choose {s} in malaysia", f"how much does {s} cost in malaysia",
                  f"what does a {s.replace(' services','')} agency do",
                  f"is it worth hiring {s}", f"why hire {s}", f"when to hire {s}",
                  f"{s} for beginners", f"questions to ask {s} agency"):
            add(mk(t, slug, "expansion_l6_en", "en"))
        for t in (f"berapa kos {sm} di malaysia", f"macam mana pilih {sm}",
                  f"adakah {sm} berbaloi"):
            add(mk(t, slug, "expansion_l6_ms", "ms"))

    return out


def main():
    queue = json.load(open(QUEUE_PATH))
    existing = {x["keyword_normalized"] for x in queue}
    print(f"Existing queue: {len(queue)}")

    gen = generate()
    print(f"Generated raw: {len(gen)}")

    seen = set()
    added = []
    for k in gen:
        n = k["keyword_normalized"]
        if n in existing or n in seen:
            continue
        if any(b in n for b in BANNED):
            continue
        seen.add(n)
        added.append(k)

    queue.extend(added)
    with open(QUEUE_PATH, "w") as f:
        json.dump(queue, f, ensure_ascii=False, indent=1)

    from collections import Counter
    print(f"New unique added: {len(added)}")
    print(f"Queue total now: {len(queue)}")
    print("\nBy source (new):")
    for s, c in Counter(x["source"] for x in added).most_common():
        print(f"  {s}: {c}")
    print("\nBy service (total):")
    for s, c in Counter(x["service"] for x in queue).most_common():
        print(f"  {s}: {c}")
    print("\nBy language (total):")
    for s, c in Counter(x.get("language") for x in queue).most_common():
        print(f"  {s}: {c}")


if __name__ == "__main__":
    main()
