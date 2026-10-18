#!/usr/bin/env python3
"""
expand_massive_my_v2.py — F3b wave 2 for beriklan.my.

Adds on top of expand_massive_my.py:
  W1  extra L3 EN/MS templates (service x industry x city)      ~+96k
  W2  live-viewer deep layer: seller segments x modifiers x cities (EN+MS)
      — live viewers are the differentiator; .co.id's equivalent had 22k
  W3  service x industry x year

Same rules: bilingual EN/MS, no Lazada/Tokopedia/foreign geo, live services
use buying modifiers only. Dedupes against existing queue. Idempotent.
"""
import json
import os
import re
from datetime import datetime, timezone

ROOT = os.path.expanduser("~/Desktop/beriklan.my")
QUEUE_PATH = os.path.join(ROOT, "web/src/data/keyword-queue.json")
CITIES_PATH = os.path.join(ROOT, "web/src/data/cities.json")
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

BANNED = ("lazada", "tokopedia", "indonesia", "jakarta", "bandung", "surabaya",
          "india", "customer service", "hotline", "support number")

cities_raw = json.load(open(CITIES_PATH))
CITIES = [c["name"].lower() for c in cities_raw if not c.get("is_international")]

AGENCY_SERVICES = [
    ("facebook-ads-management", ["facebook ads services", "facebook advertising"], ["iklan facebook"]),
    ("instagram-ads-management", ["instagram ads services", "instagram advertising"], ["iklan instagram"]),
    ("tiktok-ads-management", ["tiktok ads services", "tiktok advertising"], ["iklan tiktok"]),
    ("google-ads-management", ["google ads services", "google ads management"], ["iklan google"]),
    ("youtube-ads-management", ["youtube ads services", "youtube advertising"], ["iklan youtube"]),
    ("instagram-management", ["instagram management services", "social media management instagram"], ["urus instagram"]),
    ("tiktok-management", ["tiktok management services", "tiktok content management"], ["urus tiktok"]),
    ("website-development", ["website development", "web design services"], ["buat website"]),
    ("landing-page-design", ["landing page design", "landing page services"], ["buat landing page"]),
    ("digital-marketing-agency", ["digital marketing agency", "digital marketing services"], ["agensi pemasaran digital"]),
]

LIVE_SERVICES = [
    ("tiktok-live-viewers", "tiktok live viewers", "tiktok live", ["penonton live tiktok"]),
    ("instagram-live-viewers", "instagram live viewers", "instagram live", ["penonton live instagram"]),
    ("shopee-live-viewers", "shopee live viewers", "shopee live", ["penonton live shopee"]),
    ("youtube-live-viewers", "youtube live viewers", "youtube live stream", ["penonton live youtube"]),
    ("twitch-live-viewers", "twitch live viewers", "twitch stream", ["penonton live twitch"]),
    ("live-stream-viewers", "live stream viewers", "live streaming", ["penonton live streaming"]),
]

INDUSTRIES = [
    ("fnb", ["f&b business", "restaurant"], ["restoran"]),
    ("halal-food", ["halal food business", "halal restaurant"], ["makanan halal"]),
    ("property", ["property", "real estate"], ["hartanah"]),
    ("ecommerce", ["ecommerce", "online store"], ["kedai online"]),
    ("education", ["education", "tuition centre"], ["pusat tuisyen"]),
    ("healthcare", ["healthcare", "clinic"], ["klinik"]),
    ("beauty", ["beauty salon", "skincare brand"], ["salon kecantikan"]),
    ("fashion", ["fashion brand", "boutique"], ["butik"]),
    ("travel", ["travel agency", "hotel"], ["agensi pelancongan"]),
    ("automotive", ["car dealer", "car workshop"], ["kedai kereta"]),
    ("professional-services", ["law firm", "accounting firm"], ["firma guaman"]),
    ("fitness", ["gym", "fitness studio"], ["pusat kecergasan"]),
    ("home-services", ["renovation company", "cleaning service"], ["syarikat renovasi"]),
    ("logistics", ["logistics company", "courier service"], ["syarikat logistik"]),
    ("retail", ["retail store", "grocery store"], ["kedai runcit"]),
    ("electronics", ["electronics store", "gadget store"], ["kedai gadget"]),
    ("jewellery", ["jewellery store", "gold shop"], ["kedai emas"]),
    ("furniture", ["furniture store", "home decor store"], ["kedai perabot"]),
    ("insurance", ["insurance agent", "takaful agent"], ["ejen takaful"]),
    ("wedding", ["wedding planner", "event management"], ["perancang perkahwinan"]),
    ("photography", ["photography studio", "photographer"], ["jurugambar"]),
    ("pets", ["pet shop", "pet grooming"], ["kedai haiwan"]),
    ("childcare", ["kindergarten", "childcare centre"], ["tadika"]),
    ("agriculture", ["agriculture business", "durian farm"], ["bisnes pertanian"]),
    ("manufacturing", ["manufacturer", "factory"], ["kilang"]),
    ("islamic-products", ["muslimah fashion", "islamic products"], ["fesyen muslimah"]),
    ("beverage", ["bubble tea shop", "coffee shop"], ["kedai kopi"]),
    ("bakery", ["bakery", "cake shop"], ["kedai kek"]),
    ("optical", ["optical shop"], ["kedai cermin mata"]),
    ("pharmacy", ["pharmacy"], ["farmasi"]),
    ("tech", ["tech startup", "software company"], ["syarikat perisian"]),
    ("finance", ["financial advisor", "money lender"], ["penasihat kewangan"]),
    ("supplements", ["health supplements brand"], ["produk kesihatan"]),
    ("skincare-msme", ["small business", "sme"], ["perniagaan kecil"]),
    ("dropship", ["dropship business", "reseller business"], ["bisnes dropship"]),
]

# live-selling seller segments (what people sell on live)
SELLER_SEGMENTS_EN = [
    "fashion seller", "food seller", "gadget seller", "skincare seller",
    "hijab seller", "thrift seller", "jewellery seller", "toy seller",
    "home product seller", "preloved seller", "online boutique", "small seller",
]
SELLER_SEGMENTS_MS = [
    "penjual baju", "penjual makanan", "penjual gadget", "penjual skincare",
    "penjual tudung", "penjual bundle", "peniaga kecil", "penjual online",
]
LIVE_MODIFIERS_EN = [
    "buy", "cheap", "affordable", "instant", "real", "safe", "trusted",
    "best", "fast delivery", "no bots", "trial", "per session",
]
YEARS = ["2026", "2027"]


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
    if any(m in kw for m in (" vs ", " atau ", "which is better", "mana lebih",
                             "difference", "perbezaan")): return "comparison"
    if any(m in kw for m in ("how ", "what ", "why ", "berapa", "macam mana", "cara ")): return "informational"
    return "commercial"

def mk(kw, service, source, language, city=None, industry=None):
    kw = re.sub(r"\s+", " ", kw).strip()
    return {
        "keyword": kw, "keyword_normalized": norm(kw), "slug": slugify(kw),
        "has_post": False, "priority_score": score(norm(kw)), "source": source,
        "status": "pending", "rank": None, "created_at": NOW, "service": service,
        "city": city, "industry": industry, "intent": intent_of(norm(kw)),
        "language": language, "country": "my",
    }


def generate():
    out = []
    add = out.append

    # ---- W1: extra L3 templates ----
    for slug, ens, mss in AGENCY_SERVICES:
        s = ens[0]; s2 = ens[1] if len(ens) > 1 else ens[0]
        sm = mss[0]
        for _key, i_ens, i_mss in INDUSTRIES:
            ind = i_ens[0]; ind2 = i_ens[1] if len(i_ens) > 1 else i_ens[0]
            indm = i_mss[0]
            for c in CITIES:
                for t in (f"{s} agency for {ind} in {c}", f"hire {s} for {ind} in {c}",
                          f"{s} consultant for {ind} {c}", f"{s} for {ind} companies in {c}",
                          f"recommended {s} for {ind} {c}", f"{s2} for {ind} startups {c}",
                          f"{s} for {ind} price list {c}", f"{s2} quotation for {ind2} {c}"):
                    add(mk(t, slug, "expansion_w1_en", "en", city=c, industry=_key))
                for t in (f"khidmat {sm} {indm} {c}", f"{sm} untuk {indm} murah {c}",
                          f"upah {sm} untuk {indm} di {c}"):
                    add(mk(t, slug, "expansion_w1_ms", "ms", city=c, industry=_key))

    # ---- W2: live-viewer deep layer ----
    for slug, en, alt, mss in LIVE_SERVICES:
        # modifiers x cities
        for c in CITIES:
            for m in LIVE_MODIFIERS_EN:
                add(mk(f"{m} {en} {c}", slug, "expansion_w2_en", "en", city=c))
            for t in (f"where to buy {en} in {c}", f"{en} service {c}",
                      f"{en} malaysia {c}", f"boost {alt} viewers {c}",
                      f"increase {alt} viewers {c}", f"{en} {c} price"):
                add(mk(t, slug, "expansion_w2_en", "en", city=c))
        # seller segments (x city for top combos)
        for seg in SELLER_SEGMENTS_EN:
            for t in (f"{en} for {seg}", f"buy {en} for {seg}", f"cheap {en} for {seg}",
                      f"{en} for {seg} malaysia", f"boost {alt} for {seg}",
                      f"how many viewers needed for {alt} {seg}"):
                add(mk(t, slug, "expansion_w2_en", "en"))
            for c in CITIES:
                add(mk(f"{en} for {seg} {c}", slug, "expansion_w2_en", "en", city=c))
        # generic buying long-tails
        for t in (f"how to get more viewers on {alt}", f"why is my {alt} not getting viewers",
                  f"how to boost {alt} algorithm", f"{alt} viewer bot vs real viewers",
                  f"does buying {en} work", f"{en} review malaysia",
                  f"{en} price per hour", f"{en} monthly package",
                  f"legit {en} provider malaysia", f"{en} for beginners"):
            add(mk(t, slug, "expansion_w2_en", "en"))
        for y in YEARS:
            add(mk(f"buy {en} malaysia {y}", slug, "expansion_w2_en", "en"))
            add(mk(f"{en} price {y}", slug, "expansion_w2_en", "en"))
        # MS layer
        for s in mss:
            for c in CITIES:
                for t in (f"beli {s} murah {c}", f"harga {s} {c}", f"tambah {s} {c}",
                          f"{s} paling murah {c}"):
                    add(mk(t, slug, "expansion_w2_ms", "ms", city=c))
            for seg in SELLER_SEGMENTS_MS:
                add(mk(f"{s} untuk {seg}", slug, "expansion_w2_ms", "ms"))
                add(mk(f"beli {s} untuk {seg}", slug, "expansion_w2_ms", "ms"))
            for t in (f"macam mana tambah {s}", f"cara naikkan {s}", f"{s} berbaloi ke",
                      f"{s} paling murah malaysia", f"pakej {s} bulanan", f"{s} percuma vs berbayar"):
                add(mk(t, slug, "expansion_w2_ms", "ms"))

    # ---- W3: service x industry x year ----
    for slug, ens, mss in AGENCY_SERVICES:
        s = ens[0]; sm = mss[0]
        for _key, i_ens, i_mss in INDUSTRIES:
            ind = i_ens[0]; indm = i_mss[0]
            for y in YEARS:
                add(mk(f"{s} for {ind} {y}", slug, "expansion_w3_en", "en", industry=_key))
                add(mk(f"best {s} for {ind} {y}", slug, "expansion_w3_en", "en", industry=_key))
                add(mk(f"harga {sm} untuk {indm} {y}", slug, "expansion_w3_ms", "ms", industry=_key))

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
        if n in existing or n in seen or any(b in n for b in BANNED):
            continue
        seen.add(n)
        added.append(k)

    queue.extend(added)
    with open(QUEUE_PATH, "w") as f:
        json.dump(queue, f, ensure_ascii=False, indent=1)

    from collections import Counter
    print(f"New unique added: {len(added)}")
    print(f"Queue total now: {len(queue)}")
    live_total = sum(1 for x in queue if x["service"].endswith("live-viewers") or x["service"] == "live-stream-viewers")
    print(f"Live-viewer keywords total: {live_total}")
    print("\nBy language (total):")
    for s, c in Counter(x.get("language") for x in queue).most_common():
        print(f"  {s}: {c}")


if __name__ == "__main__":
    main()
