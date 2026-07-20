#!/usr/bin/env python3
"""
expand_keywords.py — Mass-expand keyword queue via intent matrix.

Current: 2763 keywords (suggest + miner). Target: 7000+ via:
  service × city × intent_modifier × year × action_verb explosion

Combinations generated:
- service × city (x26) × modifier (x6)  = 11 × 26 × 6 = 1.716 base
- + question prefixes ("cara", "apa itu", "bagaimana")  = +~600
- + year ("2026", "2027")  = +~700
- + vs comparisons (Beriklan vs X)  = +~50
- + pain point ("gagal", "tidak closing")  = +~150

Dedupe against existing keywords (slug-based).
"""
import json
import os
import re
from itertools import product

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = os.path.join(WEB, "src", "data", "keyword-queue.json")

SERVICES = [
    ("jasa-digital-marketing", "Jasa Digital Marketing", ["jasa digital marketing"]),
    ("jasa-iklan-facebook", "Jasa Iklan Facebook", ["jasa iklan facebook", "iklan facebook"]),
    ("jasa-iklan-instagram", "Jasa Iklan Instagram", ["jasa iklan instagram", "iklan instagram"]),
    ("jasa-iklan-tiktok", "Jasa Iklan TikTok", ["jasa iklan tiktok", "iklan tiktok"]),
    ("jasa-iklan-google", "Jasa Iklan Google", ["jasa iklan google", "iklan google"]),
    ("jasa-iklan-youtube", "Jasa Iklan YouTube", ["jasa iklan youtube", "iklan youtube"]),
    ("jasa-kelola-instagram", "Jasa Kelola Instagram", ["jasa kelola instagram", "kelola instagram"]),
    ("jasa-kelola-tiktok", "Jasa Kelola TikTok", ["jasa kelola tiktok", "kelola tiktok"]),
    ("jasa-pembuatan-website", "Jasa Pembuatan Website", ["jasa pembuatan website", "pembuatan website"]),
    ("jasa-pembuatan-landing-page", "Jasa Pembuatan Landing Page", ["jasa landing page", "landing page"]),
    ("jasa-view-live", "Jasa View Live", ["view live", "viewers live"]),
]

CITIES = ["jakarta", "bandung", "surabaya", "yogyakarta", "semarang", "medan", "makassar",
          "denpasar", "bekasi", "depok", "tangerang", "bogor", "malang", "batam",
          "palembang", "pekanbaru", "sidoarjo", "solo", "padang", "manado",
          "pontianak", "banjarmasin", "lampung", "jambi", "cimahi", "balikpapan"]

# Intent modifiers — prepend/append to base keyword
COMMERCIAL = ["murah", "harga", "biaya", "tarif", "paket", "promo"]
QUALITY = ["terbaik", "profesional", "berpengalaman", "terpercaya"]
ACTION = ["cara", "tips", "tutorial", "langkah", "strategi"]
QUESTION = ["apa itu", "bagaimana", "kenapa", "berapa biaya"]
YEAR = ["2026", "2027"]
PAINPOINT = ["gagal", "tidak closing", "roas rendah", "boncos"]

# Service-specific modifier patterns
SERVICE_MODIFIERS = {
    "jasa-digital-marketing": ["umkm", "toko online", "skala kecil", "bisnis menengah", "startup", "b2b"],
    "jasa-iklan-facebook": ["meta ads", "fb ads", "untuk toko online", "untuk umkm", "leadgen"],
    "jasa-iklan-instagram": ["ig ads", "reels ads", "untuk fashion", "untuk beauty", "untuk fnb"],
    "jasa-iklan-tiktok": ["tiktok ads", "spark ads", "untuk produk", "live shopping"],
    "jasa-iklan-google": ["google ads", "search ads", "pmax", "performance max", "untuk jasa", "untuk toko"],
    "jasa-iklan-youtube": ["youtube ads", "video ads", "bumper ads", "trueview"],
    "jasa-kelola-instagram": ["konten harian", "feed aesthetic", "story aktif", "engagement naik"],
    "jasa-kelola-tiktok": ["konten video", "fyp strategy", "live streaming"],
    "jasa-pembuatan-website": ["company profile", "toko online", "landing page", "wordpress", "custom", "murah", "umkm"],
    "jasa-pembuatan-landing-page": ["high converting", "untuk google ads", "a/b testing"],
    "jasa-view-live": ["tiktok live", "instagram live", "shopee live", "youtube live"],
}

VIEW_LIVE_PLATFORMS = ["tiktok", "instagram", "shopee", "youtube", "twitch"]


def slugify(text):
    s = text.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    return s


def score_keyword(kw):
    """Priority score: commercial intent > informational > generic."""
    base = 30
    if any(m in kw for m in ["murah", "harga", "biaya", "tarif", "paket"]):
        base += 25
    if any(m in kw for m in ["2026", "2027", "terbaru"]):
        base += 15
    if any(m in kw for m in ["cara", "tips", "tutorial", "bagaimana"]):
        base += 15
    if any(m in kw for m in ["terbaik", "profesional", "berpengalaman"]):
        base += 10
    if "di " in kw and any(c in kw for c in CITIES):
        base += 10  # local intent
    if "untuk " in kw:
        base += 5  # target audience
    return min(base, 100)


def expand():
    queue = json.load(open(QUEUE))
    existing_slugs = {q["slug"] for q in queue}
    existing_keywords_normalized = {q["keyword_normalized"] for q in queue}
    new_added = []
    seen_slugs = set(existing_slugs)
    seen_kw = set(existing_keywords_normalized)

    # 1) service × city × intent_modifier explosion
    for svc_slug, svc_name, base_names in SERVICES:
        service_modifiers = SERVICE_MODIFIERS.get(svc_slug, [])
        for city in CITIES:
            for base_name in base_names:
                # Base: "{base_name} di {city}"
                kws = [f"{base_name} di {city}"]
                # With each modifier (commercial + quality + service-specific)
                for mod in (COMMERCIAL + QUALITY + service_modifiers):
                    kws.append(f"{base_name} {mod} di {city}")
                    kws.append(f"{base_name} di {city} {mod}")
                # With action verbs
                for act in ACTION:
                    kws.append(f"{act} {base_name} di {city}")
                # With question
                for q in QUESTION:
                    kws.append(f"{q} {base_name} di {city}")
                # With year
                for y in YEAR:
                    kws.append(f"{base_name} di {city} {y}")
                    kws.append(f"harga {base_name} di {city} {y}")
                # Without city (broader coverage)
                for mod in COMMERCIAL + QUALITY:
                    kws.append(f"{base_name} {mod}")

                for kw in kws:
                    kw_norm = re.sub(r"\s+", " ", kw.lower().strip())
                    slug = slugify(kw)
                    if not slug or slug in seen_slugs or kw_norm in seen_kw:
                        continue
                    seen_slugs.add(slug)
                    seen_kw.add(kw_norm)
                    new_added.append({
                        "keyword": kw.title() if kw[0].islower() else kw,
                        "keyword_normalized": kw_norm,
                        "slug": slug,
                        "has_post": False,
                        "priority_score": score_keyword(kw_norm),
                        "source": "expansion_v1",
                        "status": "pending",
                        "rank": 0,
                        "created_at": "2026-07-20T12:00:00+00:00",
                        "service": svc_slug,
                        "city": city,
                    })

    # 2) View-live platform explosion
    for platform in VIEW_LIVE_PLATFORMS:
        for city in CITIES:
            for mod in COMMERCIAL + QUALITY:
                kw = f"view live {platform} {mod} di {city}"
                kw_norm = kw.lower()
                slug = slugify(kw)
                if slug in seen_slugs or kw_norm in seen_kw:
                    continue
                seen_slugs.add(slug)
                seen_kw.add(kw_norm)
                new_added.append({
                    "keyword": kw.title(),
                    "keyword_normalized": kw_norm,
                    "slug": slug,
                    "has_post": False,
                    "priority_score": score_keyword(kw_norm),
                    "source": "expansion_v1",
                    "status": "pending",
                    "rank": 0,
                    "created_at": "2026-07-20T12:00:00+00:00",
                    "service": "jasa-view-live",
                    "city": city,
                })

    # 3) Cross-service "vs" comparisons (top 5 competitors by traffic)
    competitors = ["tokopedia", "shopee", "lazada", "blibli", "tiktok shop"]
    for svc_slug, svc_name, _ in SERVICES[:6]:
        for comp in competitors:
            kw = f"{svc_name} vs {comp}"
            kw_norm = kw.lower()
            slug = slugify(kw)
            if slug in seen_slugs or kw_norm in seen_kw:
                continue
            seen_slugs.add(slug)
            seen_kw.add(kw_norm)
            new_added.append({
                "keyword": kw,
                "keyword_normalized": kw_norm,
                "slug": slug,
                "has_post": False,
                "priority_score": 65,
                "source": "expansion_v1",
                "status": "pending",
                "rank": 0,
                "created_at": "2026-07-20T12:00:00+00:00",
                "service": svc_slug,
                "city": None,
            })

    # 4) Pain-point queries
    for svc_slug, svc_name, base_names in SERVICES:
        for base_name in base_names[:1]:
            for pain in PAINPOINT:
                for city in CITIES[:5]:  # top 5 cities
                    kw = f"{base_name} {pain} di {city}"
                    kw_norm = kw.lower()
                    slug = slugify(kw)
                    if slug in seen_slugs or kw_norm in seen_kw:
                        continue
                    seen_slugs.add(slug)
                    seen_kw.add(kw_norm)
                    new_added.append({
                        "keyword": kw.title(),
                        "keyword_normalized": kw_norm,
                        "slug": slug,
                        "has_post": False,
                        "priority_score": 70,
                        "source": "expansion_v1",
                        "status": "pending",
                        "rank": 0,
                        "created_at": "2026-07-20T12:00:00+00:00",
                        "service": svc_slug,
                        "city": city,
                    })

    print(f"Existing: {len(queue)}")
    print(f"New generated: {len(new_added)}")
    print(f"After expansion: {len(queue) + len(new_added)}")

    if new_added:
        queue.extend(new_added)
        json.dump(queue, open(QUEUE, "w"), ensure_ascii=False, indent=2)
        print(f"Saved to {QUEUE}")

    # Stats per service
    from collections import Counter
    new_by_svc = Counter(x.get("service") for x in new_added)
    print("\nNew keywords by service:")
    for s, c in new_by_svc.most_common():
        print(f"  {s}: {c}")


if __name__ == "__main__":
    expand()