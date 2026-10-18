#!/usr/bin/env python3
"""Expand View Live TikTok & Shopee — murah/harga/promo massive + Google Suggest"""
import json, os, re, urllib.request, urllib.parse, time

WEB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web')
QUEUE = os.path.join(WEB, "src", "data", "keyword-queue.json")

CITIES = ["jakarta","bandung","surabaya","yogyakarta","semarang","medan","makassar",
          "denpasar","bekasi","depok","tangerang","bogor","malang","batam",
          "palembang","pekanbaru","sidoarjo","solo","padang","manado",
          "pontianak","banjarmasin","lampung","jambi","cimahi","balikpapan"]

def slugify(text):
    s = text.lower(); s = re.sub(r"[^a-z0-9\s-]","",s); s = re.sub(r"\s+","-",s).strip("-"); return s

def google_suggest(query):
    url = f"https://suggestqueries.google.com/complete/search?output=firefox&hl=id&gl=id&q={urllib.parse.quote(query)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode("utf-8"))
        return data[1] if len(data) > 1 else []
    except: return []

def generate():
    queue = json.load(open(QUEUE))
    seen_slugs={q["slug"] for q in queue}
    seen_kw={q["keyword_normalized"] for q in queue}
    new=[]
    suggest_added=set()

    def add(kw_text,ind=None,city=None,source="viewlive_murah",priority=45):
        kw_norm=re.sub(r"\s+"," ",kw_text.lower().strip())
        slug=slugify(kw_norm)
        if not slug or slug in seen_slugs or kw_norm in seen_kw: return
        seen_slugs.add(slug); seen_kw.add(kw_norm)
        new.append({"keyword":kw_text.title() if kw_text[0].islower() else kw_text,
            "keyword_normalized":kw_norm,"slug":slug,"has_post":False,
            "priority_score":priority,"source":source,
            "status":"pending","rank":0,"created_at":"2026-07-24T12:00:00+00:00",
            "service":"jasa-view-live","city":city,"industry":ind})

    # ─── PASS A: TikTok — 100+ patterns × all cities ───
    # Commercial intent variations
    modifiers = ["murah","termurah","paling murah","murah banget","murah meriah",
                  "harga murah","harga terjangkau","harga promo","harga spesial",
                  "biaya murah","biaya terjangkau","paket murah","paket hemat",
                  "paket promo","paket termurah","promo","diskon","murah dan cepat",
                  "bergaransi","resmi","terpercaya","legal","cepat","instant"]

    for mod in modifiers:
        for city in CITIES:
            # "jasa view tiktok murah di jakarta"
            kw1 = f"jasa view live tiktok {mod} di {city}"
            kw2 = f"view live tiktok {mod} di {city}"
            kw3 = f"jasa view tiktok {mod} di {city}"
            kw4 = f"beli view tiktok {mod} di {city}"
            add(kw1); add(kw2); add(kw3); add(kw4)

    # Additional TikTok patterns
    for city in CITIES:
        extras_tiktok = [
            f"jasa viewers tiktok murah di {city}",
            f"tambah penonton tiktok live di {city}",
            f"jual viewers tiktok di {city}",
            f"beli viewers tiktok live di {city}",
            f"tiktok live viewers murah di {city}",
            f"jasa live streaming tiktok murah di {city}",
            f"tambah viewers tiktok murah di {city}",
            f"jasa boost live tiktok di {city}",
            f"order view tiktok di {city}",
            f"paket viewers tiktok live di {city}",
            f"harga jasa view tiktok di {city}",
            f"biaya view live tiktok di {city}",
            f"tarif view tiktok di {city}",
            f"jasa view tiktok live terpercaya di {city}",
            f"viewers tiktok indonesia murah di {city}",
        ]
        for ex in extras_tiktok:
            add(ex)

    # ─── PASS B: Shopee — same treatment ───
    for mod in modifiers:
        for city in CITIES:
            kw1 = f"jasa view live shopee {mod} di {city}"
            kw2 = f"view live shopee {mod} di {city}"
            kw3 = f"jasa view shopee {mod} di {city}"
            kw4 = f"beli view shopee {mod} di {city}"
            add(kw1); add(kw2); add(kw3); add(kw4)

    for city in CITIES:
        extras_shopee = [
            f"jasa viewers shopee murah di {city}",
            f"tambah penonton shopee live di {city}",
            f"jual viewers shopee di {city}",
            f"beli viewers shopee live di {city}",
            f"shopee live viewers murah di {city}",
            f"jasa live streaming shopee murah di {city}",
            f"tambah viewers shopee murah di {city}",
            f"jasa boost live shopee di {city}",
            f"order view shopee di {city}",
            f"paket viewers shopee live di {city}",
            f"harga jasa view shopee di {city}",
            f"biaya view live shopee di {city}",
            f"tarif view shopee di {city}",
            f"jasa view shopee live terpercaya di {city}",
            f"viewers shopee indonesia murah di {city}",
        ]
        for ex in extras_shopee:
            add(ex)

    # ─── PASS C: Without city (broader) + "indonesia" ───
    for mod in modifiers:
        for plat in ["tiktok","shopee"]:
            add(f"jasa view live {plat} {mod}")
            add(f"view live {plat} {mod}")
            add(f"beli view {plat} {mod}")
            add(f"jasa view {plat} {mod} indonesia")
            add(f"view {plat} {mod} indonesia")

    # ─── PASS D: Google Suggest ───
    suggest_seeds = [
        "jasa view tiktok murah", "beli viewers tiktok", "tiktok viewers murah",
        "jasa view shopee murah", "beli viewers shopee", "shopee live viewers",
        "tambah viewers tiktok", "jasa live tiktok", "viewers tiktok 2026",
        "jual viewers tiktok", "jasa view live tiktok di", "beli view tiktok di",
        "harga view tiktok", "paket view tiktok", "jasa view tiktok terpercaya",
        "jasa view shopee live", "shopee live tonton", "beli viewers shopee murah",
        "jasa tambah penonton shopee live", "harga jasa view shopee",
    ]
    for seed in suggest_seeds:
        sug = google_suggest(seed)
        for s in sug:
            kw_norm = s.lower().strip()
            if kw_norm in seen_kw or kw_norm in suggest_added: continue
            suggest_added.add(kw_norm)
            # Determine city if present
            city = None
            for c in CITIES:
                if c in kw_norm:
                    city = c
                    break
            add(s, city=city, source="google_suggest_viewlive", priority=50)
        time.sleep(1.2)

    print(f"Existing: {len(queue)}")
    print(f"New generated: {len(new)}")
    if new:
        queue.extend(new)
        json.dump(queue,open(QUEUE,"w"),ensure_ascii=False,indent=2)
    print(f"Total: {len(queue)}")

    # Stats
    tt = sum(1 for x in new if 'tiktok' in x.get('keyword_normalized',''))
    sp = sum(1 for x in new if 'shopee' in x.get('keyword_normalized',''))
    mu = sum(1 for x in new if 'murah' in x.get('keyword_normalized',''))
    print(f"\nStats: TikTok={tt:,} Shopee={sp:,} With 'murah'={mu:,} Google Suggest={len(suggest_added):,}")

if __name__=="__main__":
    generate()
