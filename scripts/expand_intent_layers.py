#!/usr/bin/env python3
"""
expand_intent_layers.py — Targeted expansion for Comparison + Pain layers.
"""
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

SERVICES_INFO = {
    "jasa-digital-marketing": ["jasa digital marketing", "digital marketing", "jasa marketing"],
    "jasa-iklan-facebook": ["jasa iklan facebook", "iklan facebook", "facebook ads"],
    "jasa-iklan-instagram": ["jasa iklan instagram", "iklan instagram", "instagram ads"],
    "jasa-iklan-tiktok": ["jasa iklan tiktok", "iklan tiktok", "tiktok ads"],
    "jasa-iklan-google": ["jasa iklan google", "iklan google", "google ads"],
    "jasa-iklan-youtube": ["jasa iklan youtube", "iklan youtube", "youtube ads"],
    "jasa-kelola-instagram": ["jasa kelola instagram", "kelola instagram"],
    "jasa-kelola-tiktok": ["jasa kelola tiktok", "kelola tiktok"],
    "jasa-pembuatan-website": ["jasa pembuatan website", "pembuatan website", "jasa buat website"],
    "jasa-pembuatan-landing-page": ["jasa landing page", "landing page"],
    "jasa-view-live": ["jasa view live", "view live", "viewers live"],
}

def slugify(text):
    s = text.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    return s

def score(kw):
    base = 40
    if any(m in kw for m in ["murah","harga","biaya","paket"]): base += 20
    if any(m in kw for m in ["cara","tips","bagaimana"]): base += 10
    if any(m in kw for m in ["boncos","gagal","rugi","sepi","tidak closing"]): base += 15
    if any(c in kw for c in CITIES): base += 10
    return min(base, 100)

def generate():
    queue = json.load(open(QUEUE))
    seen_slugs = {q["slug"] for q in queue}
    seen_kw = {q["keyword_normalized"] for q in queue}
    new = []

    def add(kw_text, svc_slug, ind_id=None, city=None, industry=None):
        kw_norm = re.sub(r"\s+", " ", kw_text.lower().strip())
        slug = slugify(kw_norm)
        if not slug or slug in seen_slugs or kw_norm in seen_kw:
            return
        seen_slugs.add(slug); seen_kw.add(kw_norm)
        new.append({
            "keyword": kw_text.title() if kw_text[0].islower() else kw_text,
            "keyword_normalized": kw_norm, "slug": slug, "has_post": False,
            "priority_score": score(kw_norm),
            "source": "intent_layer", "status": "pending", "rank": 0,
            "created_at": "2026-07-24T12:00:00+00:00",
            "service": svc_slug, "city": city, "industry": ind_id or industry,
        })

    # ════════════════════════════════════════════════════════════
    # PASS 1: COMPARISON — MASSIVE EXPANSION
    # ════════════════════════════════════════════════════════════

    # 1a) Service vs Service comparisons (15 pairs × 4 formats × cities × industries)
    compare_pairs = [
        ("facebook ads", "google ads", "jasa-iklan-facebook", "jasa-iklan-google"),
        ("facebook ads", "instagram ads", "jasa-iklan-facebook", "jasa-iklan-instagram"),
        ("facebook ads", "tiktok ads", "jasa-iklan-facebook", "jasa-iklan-tiktok"),
        ("instagram ads", "tiktok ads", "jasa-iklan-instagram", "jasa-iklan-tiktok"),
        ("google ads", "youtube ads", "jasa-iklan-google", "jasa-iklan-youtube"),
        ("google ads", "facebook ads", "jasa-iklan-google", "jasa-iklan-facebook"),
        ("google ads", "tiktok ads", "jasa-iklan-google", "jasa-iklan-tiktok"),
        ("tiktok ads", "youtube ads", "jasa-iklan-tiktok", "jasa-iklan-youtube"),
        ("instagram ads", "youtube ads", "jasa-iklan-instagram", "jasa-iklan-youtube"),  # NEW
        ("kelola instagram", "kelola tiktok", "jasa-kelola-instagram", "jasa-kelola-tiktok"),
        ("website", "landing page", "jasa-pembuatan-website", "jasa-pembuatan-landing-page"),
        ("google ads", "instagram ads", "jasa-iklan-google", "jasa-iklan-instagram"),
        ("facebook ads", "youtube ads", "jasa-iklan-facebook", "jasa-iklan-youtube"),
        ("digital marketing", "facebook ads", "jasa-digital-marketing", "jasa-iklan-facebook"),
        ("digital marketing", "google ads", "jasa-digital-marketing", "jasa-iklan-google"),
        ("digital marketing", "tiktok ads", "jasa-digital-marketing", "jasa-iklan-tiktok"),
        ("digital marketing", "instagram ads", "jasa-digital-marketing", "jasa-iklan-instagram"),
        ("digital marketing", "youtube ads", "jasa-digital-marketing", "jasa-iklan-youtube"),
        ("iklan facebook", "iklan google", "jasa-iklan-facebook", "jasa-iklan-google"),
        ("iklan facebook", "iklan instagram", "jasa-iklan-facebook", "jasa-iklan-instagram"),
    ]

    compare_formats = [
        "{a} vs {b}",
        "{a} atau {b}",
        "perbedaan {a} dan {b}",
        "mana lebih baik {a} atau {b}",
        "kelebihan {a} dan {b}",
        "review {a} vs {b}",
        "harga {a} vs {b}",
        "mana yang lebih murah {a} atau {b}",
        "cara pilih {a} atau {b}",
        "rekomendasi {a} atau {b}",
        "untung rugi {a} dan {b}",
        "perbandingan {a} dan {b}",
        "mana tepat {a} atau {b}",
        "cocok bisnis {a} atau {b}",
    ]

    for a, b, svc_a, svc_b in compare_pairs:
        for fmt in compare_formats:
            kw = fmt.replace("{a}", a).replace("{b}", b)
            add(kw, svc_a)
            # With industries
            for ind_id, _, aliases in INDUSTRIES:
                kw_ind = f"{fmt.replace('{a}', a).replace('{b}', b)} untuk {aliases[0]}"
                add(kw_ind, svc_a, ind_id)
            # With cities
            for city in CITIES:
                kw_city = f"{kw} di {city}"
                add(kw_city, svc_a, city=city)
                for ind_id, _, aliases in INDUSTRIES:
                    kw_ind_city = f"{fmt.replace('{a}', a).replace('{b}', b)} untuk {aliases[0]} di {city}"
                    add(kw_ind_city, svc_a, ind_id, city)

    # 1b) Service vs Competitor platforms
    competitors = ["tokopedia", "shopee", "lazada", "blibli", "tiktok shop"]
    for svc_slug, base_names in SERVICES_INFO.items():
        for comp in competitors:
            base = base_names[0]
            formats = [
                f"{base} vs {comp}",
                f"{base} atau {comp}",
                f"perbedaan {base} dan {comp}",
                f"mana lebih baik {base} atau {comp}",
                f"{comp} vs {base}",
            ]
            for fmt in formats:
                add(fmt, svc_slug)
                for city in CITIES:
                    add(f"{fmt} di {city}", svc_slug, city=city)

    # 1c) Agency/competitor comparisons
    agency_comps = ["3s medianet", "aptana", "sorotnamedia", "banyumedia", "digital agency lain"]
    for svc_slug, base_names in SERVICES_INFO.items():
        base = base_names[0]
        for comp in agency_comps:
            formats = [
                f"{base} vs {comp}",
                f"{base} atau {comp}",
                f"perbedaan {base} dan {comp}",
            ]
            for fmt in formats:
                add(fmt, svc_slug)
                for city in CITIES:
                    add(f"{fmt} di {city}", svc_slug, city=city)

    # ════════════════════════════════════════════════════════════
    # PASS 2: PAIN-POINT — MASSIVE EXPANSION
    # ════════════════════════════════════════════════════════════
    pain_templates = [
        # Cost-related
        "{svc} boncos",
        "{svc} mahal",
        "{svc} rugi",
        "budget {svc} terbuang",
        "biaya {svc} tidak sebanding",
        "sayang uang {svc}",
        "modal {svc} habis",
        # Performance-related
        "{svc} tidak closing",
        "{svc} gagal",
        "{svc} tidak efektif",
        "{svc} tidak konversi",
        "roas rendah {svc}",
        "target {svc} meleset",
        "{svc} hasil minimal",
        "{svc} zonk",
        "{svc} mengecewakan",
        "{svc} percuma",
        "{svc} tidak sesuai harapan",
        "{svc} gagal terus",
        # Audience-related
        "{svc} sepi viewers",
        "engagement {svc} rendah",
        "{svc} sepi peminat",
        "traffic {svc} sedikit",
        "like dikit {svc}",
        # Strategy-related
        "salah strategi {svc}",
        "bingung pilih {svc}",
        "capek {svc} gak ada hasil",
        "salah target {svc}",
        "creative {svc} jelek",
    ]

    for svc_slug, base_names in SERVICES_INFO.items():
        svc_short = base_names[0]
        for pain in pain_templates:
            kw = pain.replace("{svc}", svc_short)
            # Without city/industry
            add(kw, svc_slug)
            # With city
            for city in CITIES:
                add(f"{kw} di {city}", svc_slug, city=city)
            # With industry
            for ind_id, _, aliases in INDUSTRIES:
                kw_ind = pain.replace("{svc}", f"{svc_short} {aliases[0]}")
                add(kw_ind, svc_slug, ind_id)
                for city in CITIES:
                    add(f"{pain.replace('{svc}', f'{svc_short} {aliases[0]}')} di {city}", svc_slug, ind_id, city)

    # ── REPORT ──
    print(f"Existing: {len(queue)}")
    print(f"New generated: {len(new)}")
    print(f"After expansion: {len(queue) + len(new)}")

    if new:
        queue.extend(new)
        json.dump(queue, open(QUEUE, "w"), ensure_ascii=False, indent=2)
        print(f"Saved to {QUEUE}")

    from collections import Counter
    new_by_svc = Counter(x.get("service") for x in new)
    print("\nNew per service:")
    for s,c in new_by_svc.most_common():
        print(f"  {s}: {c}")

if __name__ == "__main__":
    generate()
