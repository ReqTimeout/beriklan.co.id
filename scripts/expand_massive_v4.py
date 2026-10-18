#!/usr/bin/env python3
"""
expand_massive_v4.py — Generate keywords untuk ALL 11 services × ALL 10 industries.
Target: setidaknya 500+ keyword per (service, industry) pair.
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
    if "untuk" in kw or "bagi" in kw: base += 5
    return min(base, 100)

def generate():
    queue = json.load(open(QUEUE))
    seen_slugs = {q["slug"] for q in queue}
    seen_kw = {q["keyword_normalized"] for q in queue}
    new = []

    def add(kw_text, svc_slug, ind_id=None, city=None, score_bonus=0):
        kw_norm = re.sub(r"\s+", " ", kw_text.lower().strip())
        slug = slugify(kw_norm)
        if not slug or slug in seen_slugs or kw_norm in seen_kw:
            return
        seen_slugs.add(slug); seen_kw.add(kw_norm)
        new.append({
            "keyword": kw_text.title() if kw_text[0].islower() else kw_text,
            "keyword_normalized": kw_norm, "slug": slug, "has_post": False,
            "priority_score": score_keyword(kw_norm) + score_bonus,
            "source": "expansion_v4", "status": "pending", "rank": 0,
            "created_at": "2026-07-24T12:00:00+00:00",
            "service": svc_slug, "city": city, "industry": ind_id,
        })

    # ────────────────────────────────────────────────────────────────
    # Deep-dive pattern bank per industry (INDUSTRY-FIRST approach)
    # Setiap pattern akan di-generate untuk service yang relevan
    # ────────────────────────────────────────────────────────────────

    # Pattern bank: (pattern_template, [list_of_relevant_services])
    # {svc} = service short name, {ind} = industry alias, {ind2} = industry second alias

    def generate_for_service(svc_slug, svc_name, svc_short, ind_id, ind_name, aliases):
        """Generate ALL natural keyword patterns for a (service, industry) pair."""
        alias = aliases[0]
        alias2 = aliases[-1] if len(aliases) > 1 else alias

        # ── Build pattern library based on service type ──
        pats = []

        # 1. Core "service untuk industry" patterns
        pats.append(f"{svc_short} untuk {alias}")
        pats.append(f"jasa {svc_short} {alias}")
        pats.append(f"{svc_short} {alias}")

        # 2. Qualification modifiers
        for mod in ["terbaik","profesional","murah","terpercaya","bergaransi"]:
            pats.append(f"{svc_short} {alias} {mod}")
            pats.append(f"{svc_short} untuk {alias} {mod}")

        # 3. Question patterns for this pair
        pats.append(f"apa itu {svc_short} untuk {alias}")
        pats.append(f"berapa biaya {svc_short} {alias}")
        pats.append(f"bagaimana cara {svc_short} {alias}")
        pats.append(f"rekomendasi {svc_short} {alias}")
        pats.append(f"tips {svc_short} {alias}")

        # 4. "Bagi" alternative preposition
        pats.append(f"{svc_short} bagi pelaku {alias}")
        pats.append(f"{svc_short} untuk bisnis {alias}")

        # 5. Price/commercial patterns
        pats.append(f"harga {svc_short} {alias}")
        pats.append(f"paket {svc_short} {alias}")
        pats.append(f"biaya {svc_short} untuk {alias}")
        pats.append(f"promo {svc_short} {alias}")

        # 6. Year-specific
        for year in ["2025","2026","2027"]:
            pats.append(f"{svc_short} {alias} {year}")

        # ── Service-specific deep patterns ──
        if svc_slug.startswith("jasa-iklan"):
            # Paid ads services
            platform = svc_short.replace("jasa iklan ", "")
            pats.append(f"iklan {platform} untuk bisnis {alias}")
            pats.append(f"pasang iklan {platform} {alias}")
            pats.append(f"kelola iklan {platform} {alias}")
            pats.append(f"optimasi iklan {platform} {alias}")
            pats.append(f"management iklan {platform} {alias}")
            pats.append(f"targeting iklan {platform} {alias}")
            pats.append(f"paket iklan {platform} {alias}")

        if svc_slug == "jasa-iklan-facebook":
            pats.append(f"meta ads untuk {alias}")
            pats.append(f"fb ads {alias}")
            pats.append(f"facebook marketing {alias}")
            pats.append(f"bisnis {alias} pakai facebook ads")

        if svc_slug == "jasa-iklan-instagram":
            pats.append(f"instagram marketing {alias}")
            pats.append(f"ig ads {alias}")
            pats.append(f"reels {alias}")
            pats.append(f"instagram story {alias}")
            pats.append(f"bisnis {alias} di instagram")

        if svc_slug == "jasa-iklan-tiktok":
            pats.append(f"tiktok marketing {alias}")
            pats.append(f"tiktok shop {alias}")
            pats.append(f"spark ads {alias}")
            pats.append(f"fyp {alias}")
            pats.append(f"viral {alias} tiktok")

        if svc_slug == "jasa-iklan-google":
            pats.append(f"google search {alias}")
            pats.append(f"pmax {alias}")
            pats.append(f"google shopping {alias}")
            pats.append(f"google display {alias}")
            pats.append(f"performance max untuk {alias}")

        if svc_slug == "jasa-iklan-youtube":
            pats.append(f"youtube marketing {alias}")
            pats.append(f"video promosi {alias}")
            pats.append(f"iklan video {alias}")
            pats.append(f"youtube channel {alias}")
            pats.append(f"brand awareness {alias} youtube")

        if svc_slug.startswith("jasa-kelola"):
            platform = "instagram" if "instagram" in svc_slug else "tiktok"
            pats.append(f"kelola {platform} untuk {alias}")
            pats.append(f"jasa {platform} {alias}")
            pats.append(f"content {platform} {alias}")
            pats.append(f"buat konten {platform} {alias}")
            pats.append(f"jadwal posting {platform} {alias}")
            pats.append(f"manage {platform} {alias}")
            pats.append(f"social media {platform} {alias}")
            pats.append(f"growth {platform} {alias}")

        if svc_slug == "jasa-pembuatan-website":
            pats.append(f"buat website {alias}")
            pats.append(f"website toko {alias}")
            pats.append(f"website company profile {alias}")
            pats.append(f"website profil bisnis {alias}")
            pats.append(f"web {alias} profesional")
            pats.append(f"bikin website untuk {alias}")
            pats.append(f"website {alias} modern")
            pats.append(f"cms website {alias}")
            pats.append(f"website {alias} murah")

        if svc_slug == "jasa-pembuatan-landing-page":
            pats.append(f"buat landing page {alias}")
            pats.append(f"halaman penjualan {alias}")
            pats.append(f"landing page promosi {alias}")
            pats.append(f"landing page konversi {alias}")
            pats.append(f"landing page untuk produk {alias}")

        if svc_slug == "jasa-view-live":
            pats.append(f"view live {alias}")
            pats.append(f"jual view {alias}")
            pats.append(f"live streaming {alias}")
            pats.append(f"tambah viewer {alias}")
            pats.append(f"live {alias} murah")
            pats.append(f"siaran langsung {alias}")

        # ── Generate all patterns with and without city ──
        for pat in pats:
            # Without city
            add(pat, svc_slug, ind_id)
            # With ALL cities
            for city in CITIES:
                add(f"{pat} di {city}", svc_slug, ind_id, city)

    # ── Execute for ALL 11 services × ALL 10 industries ──
    total_expected = 0
    for svc_slug, svc_name, svc_short in SERVICES:
        for ind_id, ind_name, aliases in INDUSTRIES:
            generate_for_service(svc_slug, svc_name, svc_short, ind_id, ind_name, aliases)
            # Rough estimate of what was generated (per pair)
            pats_per_pair = 55  # ~55 patterns × 27 cities ≈ 1,485 max
            total_expected += pats_per_pair

    print(f"Existing: {len(queue)}")
    print(f"New generated: {len(new)}")
    print(f"After expansion: {len(queue) + len(new)}")
    print(f"Theoretical max per pair: ~55 patterns × 27 cities = ~1,485")

    if new:
        queue.extend(new)
        json.dump(queue, open(QUEUE, "w"), ensure_ascii=False, indent=2)
        print(f"Saved to {QUEUE}")

    from collections import Counter
    # Coverage report
    pairs = Counter()
    for item in new:
        svc = item.get("service")
        ind = item.get("industry")
        if svc and ind:
            pairs[(svc, ind)] += 1
    print("\n=== Newly generated per (service × industry) ===")
    ALL_INDUSTRIES = [x[0] for x in INDUSTRIES]
    all_services = [x[0] for x in SERVICES]
    print(f"{'Service':<35} ", end="")
    for ind in ALL_INDUSTRIES:
        print(f"{ind[:6]:>6}", end="")
    print("  TOTAL")
    grand_total = 0
    for svc in all_services:
        print(f"{svc:<35} ", end="")
        svc_total = 0
        for ind in ALL_INDUSTRIES:
            c = pairs.get((svc, ind), 0)
            print(f"{c:>6}", end="")
            svc_total += c
        print(f"  {svc_total}")
        grand_total += svc_total
    print(f"\nGrand total new: {grand_total}")

if __name__ == "__main__":
    generate()
