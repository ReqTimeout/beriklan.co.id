#!/usr/bin/env python3
"""Targeted expansion: cocok untuk, spesialis, partner, view-live platform×segment"""
import json, os, re

WEB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web')
QUEUE = os.path.join(WEB, "src", "data", "keyword-queue.json")
CITIES = ["jakarta","bandung","surabaya","yogyakarta","semarang","medan","makassar",
          "denpasar","bekasi","depok","tangerang","bogor","malang","batam",
          "palembang","pekanbaru","sidoarjo","solo","padang","manado",
          "pontianak","banjarmasin","lampung","jambi","cimahi","balikpapan"]

INDUSTRIES = [
    ("e-commerce","e-commerce",["e-commerce","online shop","toko online","marketplace"]),
    ("properti","properti",["properti","real estate","developer","perumahan"]),
    ("pendidikan","pendidikan",["pendidikan","edutech","sekolah","kursus","bimbel","les"]),
    ("kesehatan","kesehatan",["kesehatan","klinik","rumah sakit","dokter","bidan"]),
    ("fnb","fnb",["fnb","restoran","makanan","kuliner","kafe","cafe"]),
    ("fashion","fashion",["fashion","busana","pakaian","butik","distro"]),
    ("beauty","beauty",["beauty","kosmetik","skincare","makeup","perawatan"]),
    ("travel","travel",["travel","hotel","wisata","hospitality","villa"]),
    ("otomotif","otomotif",["otomotif","mobil","motor","bengkel","dealer","showroom"]),
    ("jasa-profesional","jasa profesional",["jasa profesional","konsultan","b2b","advokat","notaris","akuntan"]),
]

SERVICES = [
    ("jasa-digital-marketing","Jasa Digital Marketing","jasa digital marketing"),
    ("jasa-iklan-facebook","Jasa Iklan Facebook","jasa iklan facebook"),
    ("jasa-iklan-instagram","Jasa Iklan Instagram","jasa iklan instagram"),
    ("jasa-iklan-tiktok","Jasa Iklan TikTok","jasa iklan tiktok"),
    ("jasa-iklan-google","Jasa Iklan Google","jasa iklan google"),
    ("jasa-iklan-youtube","Jasa Iklan YouTube","jasa iklan youtube"),
    ("jasa-kelola-instagram","Jasa Kelola Instagram","jasa kelola instagram"),
    ("jasa-kelola-tiktok","Jasa Kelola TikTok","jasa kelola tiktok"),
    ("jasa-pembuatan-website","Jasa Pembuatan Website","jasa pembuatan website"),
    ("jasa-pembuatan-landing-page","Jasa Pembuatan Landing Page","jasa landing page"),
    ("jasa-view-live","Jasa View Live","jasa view live"),
]

VL_PLATFORMS = ["tiktok","instagram","shopee","youtube","facebook","twitch"]
VL_SEGMENTS = ["seller","fashion","beauty","fnb","kuliner","gaming","streamer","event","launching","affiliate","creator"]

def slugify(text):
    s = text.lower(); s = re.sub(r"[^a-z0-9\s-]","",s); s = re.sub(r"\s+","-",s).strip("-"); return s

def score(kw):
    base=40
    if any(m in kw for m in ["murah","harga","biaya","paket"]): base+=20
    if any(c in kw for c in CITIES): base+=10
    return min(base,100)

def generate():
    queue = json.load(open(QUEUE))
    seen_slugs={q["slug"] for q in queue}
    seen_kw={q["keyword_normalized"] for q in queue}
    new=[]

    def add(kw_text,svc,ind=None,city=None):
        kw_norm=re.sub(r"\s+"," ",kw_text.lower().strip())
        slug=slugify(kw_norm)
        if not slug or slug in seen_slugs or kw_norm in seen_kw: return
        seen_slugs.add(slug); seen_kw.add(kw_norm)
        new.append({"keyword":kw_text.title() if kw_text[0].islower() else kw_text,
            "keyword_normalized":kw_norm,"slug":slug,"has_post":False,
            "priority_score":score(kw_norm),"source":"industri_cocok",
            "status":"pending","rank":0,"created_at":"2026-07-24T12:00:00+00:00",
            "service":svc,"city":city,"industry":ind})

    # ─── PASS A: "cocok untuk" patterns (natural section chips) ───
    for svc_slug,_,svc_short in SERVICES:
        base=svc_short
        for ind_id,_,aliases in INDUSTRIES:
            alias=aliases[0]
            # 1. "cocok untuk {industri}"
            add(f"{base} cocok untuk {alias}",svc_slug,ind_id)
            add(f"{base} cocok untuk bisnis {alias}",svc_slug,ind_id)
            # 2. "spesialis {service} {industri}"
            add(f"spesialis {base} {alias}",svc_slug,ind_id)
            add(f"{base} spesialis {alias}",svc_slug,ind_id)
            # 3. "partner {service} untuk {industri}"
            add(f"partner {base} untuk {alias}",svc_slug,ind_id)
            add(f"{base} partner {alias}",svc_slug,ind_id)
            # 4. "rekomendasi {service} untuk {industri}"
            add(f"rekomendasi {base} untuk {alias}",svc_slug,ind_id)
            # 5. "solusi {service} untuk {industri}"
            add(f"solusi {base} untuk bisnis {alias}",svc_slug,ind_id)
            # 6. ALL with cities
            for city in CITIES:
                add(f"{base} cocok untuk {alias} di {city}",svc_slug,ind_id,city)
                add(f"spesialis {base} {alias} di {city}",svc_slug,ind_id,city)
                add(f"partner {base} untuk {alias} di {city}",svc_slug,ind_id,city)
                add(f"rekomendasi {base} untuk {alias} di {city}",svc_slug,ind_id,city)
                add(f"solusi {base} untuk bisnis {alias} di {city}",svc_slug,ind_id,city)

    # ─── PASS B: "untuk {industri}" with ALL industry aliases ───
    for svc_slug,_,svc_short in SERVICES:
        for ind_id,_,aliases in INDUSTRIES:
            for alias in aliases:  # ALL aliases, not just first
                for fmt in [
                    f"{svc_short} untuk {alias}",
                    f"jasa {svc_short} {alias}",
                    f"{svc_short} bagi pelaku {alias}",
                    f"{svc_short} untuk bisnis {alias}",
                ]:
                    add(fmt,svc_slug,ind_id)
                    for city in CITIES:
                        add(f"{fmt} di {city}",svc_slug,ind_id,city)

    # ─── PASS C: View Live — platform × segment × city ───
    for plat in VL_PLATFORMS:
        for seg in VL_SEGMENTS:
            for city in CITIES:
                patterns=[
                    f"jasa view live {plat} untuk {seg} di {city}",
                    f"view live {plat} {seg} di {city}",
                    f"beli view {plat} untuk {seg} di {city}",
                    f"paket view live {plat} {seg} di {city}",
                ]
                for p in patterns:
                    add(p,"jasa-view-live",seg,city)

    # Also "untuk seller shopee" / "untuk affiliate" type patterns
    for seg in VL_SEGMENTS:
        for plat in VL_PLATFORMS:
            for city in CITIES:
                patterns=[
                    f"jasa view live untuk {seg} {plat} di {city}",
                    f"boost live {plat} untuk {seg} di {city}",
                ]
                for p in patterns:
                    add(p,"jasa-view-live",seg,city)

    # ─── PASS D: Section chip keywords: "industri/segmen: [list]" ───
    # For service pages "Cocok untuk industri/segmen: e-commerce, fashion, fnb"
    svc_industri_map = {
        "jasa-iklan-facebook": ["e-commerce","fashion","fnb","properti","kesehatan","otomotif","jasa-profesional"],
        "jasa-iklan-instagram": ["fashion","beauty","fnb","travel","e-commerce"],
        "jasa-iklan-tiktok": ["fashion","beauty","fnb","e-commerce","pendidikan"],
        "jasa-iklan-google": ["properti","kesehatan","jasa-profesional","otomotif","pendidikan","travel"],
        "jasa-iklan-youtube": ["otomotif","properti","pendidikan","travel","fnb"],
        "jasa-kelola-instagram": ["fashion","beauty","fnb","kesehatan","travel"],
        "jasa-kelola-tiktok": ["fashion","beauty","fnb","e-commerce","pendidikan"],
        "jasa-pembuatan-website": ["e-commerce","properti","pendidikan","kesehatan","fnb","jasa-profesional"],
        "jasa-pembuatan-landing-page": ["e-commerce","properti","pendidikan","kesehatan","jasa-profesional"],
        "jasa-view-live": ["e-commerce","fashion","fnb"],
        "jasa-digital-marketing": [x[0] for x in INDUSTRIES],
    }
    for svc_slug,_,svc_short in SERVICES:
        matched = svc_industri_map.get(svc_slug,[])
        ind_names = []
        for ind_id,ind_name,_ in INDUSTRIES:
            if ind_id in matched:
                ind_names.append(ind_name)
        if ind_names:
            chips = ", ".join(ind_names)
            add(f"{svc_short} cocok untuk industri {chips}",svc_slug)
            add(f"industri yang cocok untuk {svc_short}: {chips}",svc_slug)
            for city in CITIES:
                add(f"{svc_short} cocok untuk industri {chips} di {city}",svc_slug,city=city)

    print(f"Existing: {len(queue)}")
    print(f"New generated: {len(new)}")
    if new:
        queue.extend(new)
        json.dump(queue,open(QUEUE,"w"),ensure_ascii=False,indent=2)
    print(f"Total: {len(queue)}")

    from collections import Counter
    src=Counter(x["source"] for x in new)
    print(f"Sources: {dict(src)}")

if __name__=="__main__":
    generate()
