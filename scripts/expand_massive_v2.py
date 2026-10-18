#!/usr/bin/env python3
"""
expand_massive_v2.py — Phase 1 massive keyword expansion.
Generates 20+ new keyword patterns per (service, industry, city) that
DO NOT overlap with existing expansion_v1 or industri_v1 patterns.
"""

import json, os, re

WEB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web')
QUEUE = os.path.join(WEB, "src", "data", "keyword-queue.json")

SERVICES = [
    ("jasa-digital-marketing", "Jasa Digital Marketing", ["jasa digital marketing", "digital marketing", "jasa marketing"]),
    ("jasa-iklan-facebook", "Jasa Iklan Facebook", ["jasa iklan facebook", "iklan facebook", "facebook ads"]),
    ("jasa-iklan-instagram", "Jasa Iklan Instagram", ["jasa iklan instagram", "iklan instagram", "instagram ads"]),
    ("jasa-iklan-tiktok", "Jasa Iklan TikTok", ["jasa iklan tiktok", "iklan tiktok", "tiktok ads"]),
    ("jasa-iklan-google", "Jasa Iklan Google", ["jasa iklan google", "iklan google", "google ads"]),
    ("jasa-iklan-youtube", "Jasa Iklan YouTube", ["jasa iklan youtube", "iklan youtube", "youtube ads"]),
    ("jasa-kelola-instagram", "Jasa Kelola Instagram", ["jasa kelola instagram", "kelola instagram"]),
    ("jasa-kelola-tiktok", "Jasa Kelola TikTok", ["jasa kelola tiktok", "kelola tiktok"]),
    ("jasa-pembuatan-website", "Jasa Pembuatan Website", ["jasa pembuatan website", "pembuatan website", "jasa buat website"]),
    ("jasa-pembuatan-landing-page", "Jasa Pembuatan Landing Page", ["jasa landing page", "landing page"]),
    ("jasa-view-live", "Jasa View Live", ["view live", "viewers live", "jasa view"]),
]

CITIES = ["jakarta","bandung","surabaya","yogyakarta","semarang","medan","makassar",
          "denpasar","bekasi","depok","tangerang","bogor","malang","batam",
          "palembang","pekanbaru","sidoarjo","solo","padang","manado",
          "pontianak","banjarmasin","lampung","jambi","cimahi","balikpapan"]

INDUSTRIES = [
    ("e-commerce", "E-Commerce", ["e-commerce","online shop","toko online"]),
    ("properti", "Properti", ["properti","real estate"]),
    ("pendidikan", "Pendidikan", ["pendidikan","edutech","sekolah","kursus"]),
    ("kesehatan", "Kesehatan", ["kesehatan","klinik","rumah sakit"]),
    ("fnb", "F&B", ["fnb","restoran","makanan","kuliner"]),
    ("fashion", "Fashion", ["fashion","busana","pakaian"]),
    ("travel", "Travel", ["travel","hotel","wisata","hospitality"]),
    ("otomotif", "Otomotif", ["otomotif","mobil","motor","bengkel"]),
    ("jasa-profesional", "Jasa Profesional", ["jasa profesional","konsultan","b2b"]),
]

SERVICE_INDUSTRY_MATCH = {
    "jasa-digital-marketing": None,
    "jasa-iklan-facebook": ["e-commerce","fashion","fnb","properti","kesehatan","otomotif","jasa-profesional"],
    "jasa-iklan-instagram": ["fashion","fnb","travel","e-commerce","kesehatan"],
    "jasa-iklan-tiktok": ["fashion","fnb","e-commerce","pendidikan"],
    "jasa-iklan-google": ["properti","kesehatan","jasa-profesional","otomotif","pendidikan","travel"],
    "jasa-iklan-youtube": ["otomotif","properti","pendidikan","travel","fnb"],
    "jasa-kelola-instagram": ["fashion","fnb","kesehatan","travel","e-commerce"],
    "jasa-kelola-tiktok": ["fashion","fnb","e-commerce","pendidikan"],
    "jasa-pembuatan-website": None,
    "jasa-pembuatan-landing-page": ["e-commerce","properti","pendidikan","kesehatan","jasa-profesional","fnb"],
    "jasa-view-live": ["e-commerce","fashion","fnb","pendidikan"],
}

def slugify(text):
    s = text.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    return s

def score_keyword(kw):
    base = 30
    if any(m in kw for m in ["murah","harga","biaya","tarif","paket","promo","diskon"]): base += 25
    if any(m in kw for m in ["2026","2027","terbaru"]): base += 15
    if any(m in kw for m in ["cara","tips","tutorial","bagaimana","belajar"]): base += 15
    if any(m in kw for m in ["terbaik","profesional","berpengalaman","rekomendasi"]): base += 10
    if any(c in kw for c in CITIES): base += 10
    if "untuk" in kw: base += 5
    return min(base, 100)

def generate():
    queue = json.load(open(QUEUE))
    existing_slugs = {q["slug"] for q in queue}
    existing_kw = {q["keyword_normalized"] for q in queue}
    new = []
    seen_slugs = set(existing_slugs)
    seen_kw = set(existing_kw)

    def add(kw_text, svc_slug, ind_id=None, city=None, score_bonus=0):
        kw_norm = re.sub(r"\s+", " ", kw_text.lower().strip())
        slug = slugify(kw_norm)
        if not slug or slug in seen_slugs or kw_norm in seen_kw:
            return
        seen_slugs.add(slug)
        seen_kw.add(kw_norm)
        new.append({
            "keyword": kw_text.title() if kw_text[0].islower() else kw_text,
            "keyword_normalized": kw_norm,
            "slug": slug,
            "has_post": False,
            "priority_score": score_keyword(kw_norm) + score_bonus,
            "source": "expansion_v2",
            "status": "pending", "rank": 0,
            "created_at": "2026-07-24T12:00:00+00:00",
            "service": svc_slug,
            "city": city,
            "industry": ind_id,
        })

    # ──────────────────────────────────────────────────────────
    # PATTERN SET A: Industry × Service × City (20 new patterns)
    # ──────────────────────────────────────────────────────────
    for svc_slug, svc_name, base_names in SERVICES:
        svc_short = base_names[0]
        matched = SERVICE_INDUSTRY_MATCH.get(svc_slug)
        for ind_id, ind_name, ind_aliases in INDUSTRIES:
            if matched is not None and ind_id not in matched:
                continue
            alias = ind_aliases[0]
            alias2 = ind_aliases[-1] if len(ind_aliases) > 1 else alias

            # New patterns with industry (no city)
            patterns_no_city = [
                f"layanan {svc_short} untuk {alias}",
                f"solusi {svc_short} untuk bisnis {alias}",
                f"konsultan {svc_short} {alias}",
                f"rekomendasi {svc_short} untuk {alias}",
                f"manfaat {svc_short} untuk {alias}",
                f"kelebihan {svc_short} untuk {alias}",
                f"strategi {svc_short} untuk {alias}",
                f"tips memilih {svc_short} untuk {alias}",
                f"cara memulai {svc_short} untuk {alias}",
                f"biaya {svc_short} {alias} per bulan",
                f"investasi {svc_short} untuk {alias}",
                f"{alias} butuh {svc_short}",
                f"{svc_short} bagi pelaku {alias}",
                f"{svc_short} untuk bisnis {alias} online",
                f"{svc_short} {alias} terpercaya",
                f"testimoni {svc_short} {alias}",
                f"portofolio {svc_short} untuk {alias}",
                f"apa itu {svc_short} untuk {alias}",
                f"bagaimana cara {svc_short} {alias}",
                f"{svc_short} {alias} 2026",
            ]
            # Service-specific
            if svc_slug in ["jasa-pembuatan-website", "jasa-pembuatan-landing-page"]:
                patterns_no_city.append(f"jasa buatkan {svc_short} untuk {alias}")
                patterns_no_city.append(f"desain {svc_short} untuk {alias}")
            if svc_slug in ["jasa-iklan-facebook", "jasa-iklan-instagram", "jasa-iklan-tiktok", "jasa-iklan-google"]:
                patterns_no_city.append(f"{alias} management")
                patterns_no_city.append(f"kelola iklan {alias}")

            for pat in patterns_no_city:
                add(pat, svc_slug, ind_id)

            # Industry patterns WITH city
            for city in CITIES:
                patterns_with_city = [
                    f"layanan {svc_short} untuk {alias} di {city}",
                    f"konsultan {svc_short} {alias} di {city}",
                    f"rekomendasi {svc_short} untuk {alias} di {city}",
                    f"biaya {svc_short} {alias} di {city}",
                    f"strategi {svc_short} untuk {alias} di {city}",
                    f"{alias} butuh {svc_short} di {city}",
                    f"{svc_short} untuk bisnis {alias} di {city}",
                    f"{svc_short} {alias} terpercaya di {city}",
                    f"testimoni {svc_short} {alias} di {city}",
                    f"apa itu {svc_short} untuk {alias} di {city}",
                    f"berapa biaya {svc_short} untuk {alias} di {city}",
                    f"{svc_short} {alias} 2026 di {city}",
                ]
                for pat in patterns_with_city:
                    add(pat, svc_slug, ind_id, city)

    # ──────────────────────────────────────────────────────────
    # PATTERN SET B: New question patterns per service (all cities)
    # ──────────────────────────────────────────────────────────
    for svc_slug, svc_name, base_names in SERVICES:
        svc_short = base_names[0]
        for city in CITIES:
            questions = [
                f"apa itu {svc_short}",
                f"bagaimana cara kerja {svc_short}",
                f"berapa harga {svc_short}",
                f"berapa biaya sewa {svc_short}",
                f"gratis konsultasi {svc_short}",
                f"belajar {svc_short} untuk pemula",
                f"tutorial {svc_short}",
                f"rekomendasi {svc_short} terpercaya",
                f"cara daftar {svc_short}",
                f"apa saja layanan {svc_short}",
                f"keuntungan pakai {svc_short}",
                f"apakah {svc_short} efektif",
                f"kapan waktu tepat pakai {svc_short}",
                f"perbedaan {svc_short} dengan iklan biasa",
            ]
            for q in questions:
                add(q, svc_slug, city=city)
                # Also with city appended
                add(f"{q} di {city}", svc_slug, city=city)

    # ──────────────────────────────────────────────────────────
    # PATTERN SET C: Pain + Industry combinations
    # ──────────────────────────────────────────────────────────
    for svc_slug, svc_name, base_names in SERVICES:
        svc_short = base_names[0]
        matched = SERVICE_INDUSTRY_MATCH.get(svc_slug)
        for ind_id, ind_name, ind_aliases in INDUSTRIES:
            if matched is not None and ind_id not in matched:
                continue
            alias = ind_aliases[0]
            pains = [
                f"{svc_short} untuk {alias} gagal",
                f"{svc_short} untuk {alias} mahal",
                f"{alias} boncos pakai {svc_short}",
                f"roas rendah {svc_short} {alias}",
                f"{svc_short} {alias} tidak konversi",
                f"budget {svc_short} {alias} terbuang",
                f"{alias} rugi pakai {svc_short}",
                f"kesalahan {svc_short} untuk {alias}",
            ]
            for p in pains:
                add(p, svc_slug, ind_id)
                for city in CITIES[:10]:
                    add(f"{p} di {city}", svc_slug, ind_id, city)

    # ──────────────────────────────────────────────────────────
    # PATTERN SET D: Comparison × Industry
    # ──────────────────────────────────────────────────────────
    compare_pairs = [
        ("facebook ads", "google ads", "jasa-iklan-facebook", "jasa-iklan-google"),
        ("instagram ads", "tiktok ads", "jasa-iklan-instagram", "jasa-iklan-tiktok"),
        ("google ads", "youtube ads", "jasa-iklan-google", "jasa-iklan-youtube"),
        ("kelola instagram", "kelola tiktok", "jasa-kelola-instagram", "jasa-kelola-tiktok"),
        ("facebook ads", "instagram ads", "jasa-iklan-facebook", "jasa-iklan-instagram"),
        ("tiktok ads", "youtube ads", "jasa-iklan-tiktok", "jasa-iklan-youtube"),
        ("website", "landing page", "jasa-pembuatan-website", "jasa-pembuatan-landing-page"),
    ]
    compare_phrases = [
        "{a} vs {b} untuk {ind}",
        "{a} atau {b} untuk bisnis {ind}",
        "perbedaan {a} dan {b} untuk {ind}",
        "mana lebih baik {a} atau {b} untuk {ind}",
        "rekomendasi {a} atau {b} untuk {ind}",
    ]
    for a, b, svc_a, svc_b in compare_pairs:
        for fmt in compare_phrases:
            for ind_id, ind_name, ind_aliases in INDUSTRIES:
                alias = ind_aliases[0]
                kw = fmt.replace("{a}", a).replace("{b}", b).replace("{ind}", alias)
                add(kw, svc_a, ind_id)
                for city in CITIES[:10]:
                    kw2 = f"{kw} di {city}"
                    add(kw2, svc_a, ind_id, city)

    # ──────────────────────────────────────────────────────────
    # PATTERN SET E: "Untuk" variations — audience targeting
    # ──────────────────────────────────────────────────────────
    audiences = ["umkm", "startup", "toko online", "bisnis kecil", "perusahaan",
                  "brand lokal", "online shop", "usaha rumahan", "reseller", "dropshipper"]
    for svc_slug, svc_name, base_names in SERVICES:
        svc_short = base_names[0]
        for aud in audiences:
            patterns = [
                f"{svc_short} untuk {aud}",
                f"{svc_short} untuk {aud} murah",
                f"{svc_short} bagi pelaku {aud}",
                f"rekomendasi {svc_short} untuk {aud}",
                f"biaya {svc_short} untuk {aud}",
            ]
            for pat in patterns:
                add(pat, svc_slug)
                for city in CITIES[:10]:
                    add(f"{pat} di {city}", svc_slug, city=city)

    # ──────────────────────────────────────────────────────────
    # PATTERN SET F: Year + urgency variants
    # ──────────────────────────────────────────────────────────
    for svc_slug, svc_name, base_names in SERVICES:
        svc_short = base_names[0]
        for year in ["2025", "2026", "2027"]:
            patterns = [
                f"{svc_short} {year}",
                f"harga {svc_short} {year}",
                f"paket {svc_short} {year}",
                f"{svc_short} terbaru {year}",
                f"rekomendasi {svc_short} {year}",
                f"update {svc_short} {year}",
            ]
            for pat in patterns:
                add(pat, svc_slug)
                for city in CITIES:
                    add(f"{pat} di {city}", svc_slug, city=city)

    # ──────────────────────────────────────────────────────────
    # PATTERN SET G: Service-specific niche expansions
    # ──────────────────────────────────────────────────────────
    # Digital marketing — EXTRA (umbrella service, should have most)
    dm_svc = "jasa-digital-marketing"
    dm_extra = [
        "jasa digital marketing untuk bisnis online",
        "jasa digital marketing full service",
        "jasa digital marketing 360",
        "jasa digital marketing omni channel",
        "jasa digital marketing all in one",
        "jasa digital marketing terintegrasi",
        "jasa digital marketing end to end",
        "digital marketing agency indonesia",
        "performance marketing agency indonesia",
        "jasa digital marketing bergaransi",
        "jasa digital marketing dengan laporan mingguan",
        "konsultan digital marketing bersertifikat",
        "digital marketing partner terpercaya",
        "jasa digital marketing respon cepat",
        "senior performance marketing partner",
    ]
    for kw in dm_extra:
        add(kw, dm_svc)
        for city in CITIES:
            add(f"{kw} di {city}", dm_svc, city=city)

    # View-live — platform + city specific extra
    platforms = ["tiktok", "instagram", "shopee", "youtube", "twitch", "facebook"]
    for plat in platforms:
        for city in CITIES:
            extras = [
                f"jual view {plat} di {city}",
                f"beli view {plat} di {city}",
                f"tambah viewer {plat} di {city}",
                f"paket view {plat} di {city}",
                f"view {plat} murah di {city}",
                f"jasa live {plat} di {city}",
                f"boost live {plat} di {city}",
            ]
            for ex in extras:
                add(ex, "jasa-view-live", city=city)

    # ──────────────────────────────────────────────────────────
    # REPORT
    # ──────────────────────────────────────────────────────────
    print(f"Existing: {len(queue)}")
    print(f"New generated: {len(new)}")
    print(f"After expansion: {len(queue) + len(new)}")

    if new:
        queue.extend(new)
        json.dump(queue, open(QUEUE, "w"), ensure_ascii=False, indent=2)
        print(f"Saved to {QUEUE}")

    from collections import Counter
    new_by_svc = Counter(x.get("service") for x in new)
    print("\nNew keywords by service:")
    for s, c in new_by_svc.most_common():
        print(f"  {s}: {c}")

    new_by_ind = Counter(x.get("industry") for x in new if x.get("industry"))
    print("\nNew keywords with industry:")
    for s, c in new_by_ind.most_common():
        print(f"  {s}: {c}")

if __name__ == "__main__":
    generate()
