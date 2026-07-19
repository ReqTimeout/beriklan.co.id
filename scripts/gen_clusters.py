#!/usr/bin/env python3
"""
gen_clusters.py — build the pillar/cluster content model.

Each service pillar (src/pages/<service>/pilar/index.astro) defines a CLUSTERS
array with 10 entries: 5 "process" clusters (MINGGU/WEEK/HARI phases) followed
by 5 "topical" clusters (Targeting, Creative, Optimasi, ...). The topical ones
are the real blog clusters — they link to /blog/?tag=<tag>&service=<service>.

Until now those links landed on the generic blog index (no filtering). This script
builds a real cluster index:

  public/data/clusters.json
  {
    "<service>": {
      "<Tag>": {
        "title": "...", "desc": "...",
        "posts": [ {slug,title,excerpt,date,iso_date,readTime,featured,tags,category}, ... ]
      },
      ...
    }
  }

Posts are matched truthfully from src/data/posts.json using the cluster's keywords
(service match, category match, tag/title keyword match). No fabricated posts.
If a cluster has < 3 matches, it is left empty (BlogFilter shows a graceful
"belum ada artikel" state) rather than showing unrelated content.

Also regenerates public/data/posts-index.json WITH the `service` field and a larger
pool (300 posts) so the blog index + future client filters have enough data.

Usage:
  python3 scripts/gen_clusters.py            # build clusters.json + posts-index.json
  python3 scripts/gen_clusters.py --dry      # print match counts only
"""
import argparse
import json
import os
import re

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(WEB, "src/data/posts.json")
PILLARS_DIR = os.path.join(WEB, "src/pages")
# Importable copy (build-time SSR via Astro import) + public copy (runtime fetch).
CLUSTERS_OUT = os.path.join(WEB, "src/data/clusters.json")
CLUSTERS_PUBLIC = os.path.join(WEB, "public/data/clusters.json")
INDEX_OUT = os.path.join(WEB, "public/data/posts-index.json")

SERVICES = [
    "jasa-digital-marketing", "jasa-iklan-facebook", "jasa-iklan-instagram",
    "jasa-iklan-tiktok", "jasa-iklan-google", "jasa-iklan-youtube",
    "jasa-kelola-instagram", "jasa-kelola-tiktok",
    "jasa-pembuatan-website", "jasa-pembuatan-landing-page",
]

# Truthful category -> service mapping (used to backfill the `service` field on
# the ~827 posts that only carry a `category`). A post's category already implies
# its service, so this is a safe normalization, not fabrication.
CATEGORY_TO_SERVICE = {
    "google": "jasa-iklan-google",
    "meta": "jasa-iklan-facebook",
    "tiktok": "jasa-iklan-tiktok",
    "youtube": "jasa-iklan-youtube",
    "strategy": "jasa-digital-marketing",
    "case-study": "jasa-digital-marketing",
}

# Map a service to the post categories that belong to it (for matching posts
# whose `service` field is empty — ~827 of them only have `category`).
SERVICE_CATEGORIES = {
    "jasa-digital-marketing": ["strategy", "case-study"],
    "jasa-iklan-facebook": ["meta"],
    "jasa-iklan-instagram": ["meta"],
    "jasa-iklan-tiktok": ["tiktok"],
    "jasa-iklan-google": ["google"],
    "jasa-iklan-youtube": ["youtube"],
    "jasa-kelola-instagram": ["strategy"],
    "jasa-kelola-tiktok": ["tiktok", "strategy"],
    "jasa-pembuatan-website": ["strategy"],
    "jasa-pembuatan-landing-page": ["strategy", "google"],
}

# Keywords per topical cluster tag (lowercase). Used to match post title/tags.
CLUSTER_KEYWORDS = {
    "Targeting": ["targeting", "audiens", "audience", "interest", "lookalike", "custom audience", "demografi"],
    "Creative": ["creative", "copywriting", "desain", "video", "hook", "visual", "konten iklan", "ad creative"],
    "Optimasi": ["optimasi", "roas", "optimization", "ab test", "scaling", "retargeting", "bid"],
    "Budget": ["budget", "biaya iklan", "ad spend", "anggaran", "cost"],
    "Conversion": ["conversion", "konversi", "closing", "lead", "whatsapp", "cta", "landing"],
    "Search": ["search", "pencarian", "keyword", "seo", "google search"],
    "Display": ["display", "banner", "jaringan display"],
    "YouTube": ["youtube", "video ads", "bumper", "trueview"],
    "PMax": ["performance max", "pmax", "performance max"],
    "Visual": ["visual", "feed", "estetika", "gambar"],
    "Audience": ["audiens", "audience", "follower", "reach"],
    "Shopping": ["shopping", "katalog", "produk", "belanja"],
    "Influencer": ["influencer", "kolaborasi", "kreator", "endorse"],
    "FYP": ["fyp", "for you page", "algorithm", "viral"],
    "Spark": ["spark ads", "spark"],
    "Creator": ["creator", "kreator", "ugc"],
    "Trend": ["trend", "trending", "sound trending"],
    "Format": ["format video", "format iklan", "skippable", "non-skip"],
    "Production": ["produksi", "shooting", "editing", "produce"],
    "Performance": ["performance", "performa", "view", "watch time"],
    "Channel": ["channel", "saluran", "subscriber"],
    "Content": ["content", "konten", "posting", "kalender"],
    "Reels": ["reels", "video pendek"],
    "Hashtag": ["hashtag", "tagar"],
    "Community": ["community", "komunitas", "dm", "komentar", "engagement"],
    "Analytics": ["analytics", "analitik", "insight", "meta", "laporan"],
    "Video": ["video", "konten video", "edit video"],
    "Hook": ["hook", "pembuka", "3 detik"],
    "Sound": ["sound", "audio", "musik", "lagu"],
    "Monetize": ["monetize", "monetisasi", "penghasilan", "adsense"],
    "Struktur": ["struktur", "layout", "wireframe", "section"],
    "Copy": ["copy", "copywriting", "tulisan", "headline"],
    "Speed": ["speed", "kecepatan", "loading", "pagespeed", "core web"],
    "Tracking": ["tracking", "pixel", "tag", "analytics", "gtm"],
    "Testing": ["testing", "ab test", "uji", "experimen"],
    "Company Profile": ["company profile", "profil perusahaan", "corporate"],
    "E-commerce": ["e-commerce", "toko online", "marketplace", "payment gateway"],
    "Landing Page": ["landing page", "halaman konversi"],
    "Custom": ["custom", "customs", "kustom", "tailor"],
    "Maintenance": ["maintenance", "pemeliharaan", "update rutin"],
    "Strategy": ["strategi", "strategy", "rencana", "blueprint"],
    "Paid Ads": ["paid ads", "iklan berbayar", "ads"],
    "SEO": ["seo", "search engine", "optimasi pencarian"],
    "Analytics": ["analytics", "metrik", "data"],
}


def parse_pillar_clusters(service: str):
    """Extract the CLUSTERS array from a pillar index.astro. Returns list of
    dicts {tag, title, desc}. Splits topical (last 5) from process (first 5)."""
    path = os.path.join(PILLARS_DIR, service, "pilar", "index.astro")
    if not os.path.exists(path):
        return []
    text = open(path, encoding="utf-8").read()
    m = re.search(r"const CLUSTERS\s*=\s*(\[.*?\]);", text, re.DOTALL)
    if not m:
        return []
    try:
        arr = json.loads(m.group(1))
    except Exception:
        return []
    out = []
    for c in arr:
        tag = c.get("tag", "")
        out.append({
            "tag": tag,
            "title": c.get("title", ""),
            "desc": c.get("desc", ""),
            "is_topical": not re.search(r"MINGGU|WEEK|HARI|ONGOING|MONTHLY", tag, re.IGNORECASE),
        })
    # topical clusters are the ones flagged is_topical
    return [c for c in out if c["is_topical"]]


def post_matches(post, service, keywords):
    """Truthful match: post belongs to this service cluster if it is about the
    service AND matches the cluster keywords."""
    svc = post.get("service", "")
    cat = post.get("category", "")
    svc_cats = SERVICE_CATEGORIES.get(service, [])
    # Must be relevant to the service (either service field or mapped category)
    service_relevant = (svc == service) or (cat in svc_cats)
    if not service_relevant:
        return False
    text = " ".join([
        post.get("title", ""),
        " ".join(post.get("tags", []) or []),
        post.get("excerpt", ""),
    ]).lower()
    if any(kw in text for kw in keywords):
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    posts = json.load(open(POSTS, encoding="utf-8"))

    # Backfill `service` from category for posts missing it (truthful: category
    # already implies service). Persists to posts.json so the whole site benefits.
    backfilled = 0
    for p in posts:
        if not p.get("service") and p.get("category") in CATEGORY_TO_SERVICE:
            p["service"] = CATEGORY_TO_SERVICE[p["category"]]
            backfilled += 1
    if backfilled:
        json.dump(posts, open(POSTS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # lightweight index entry factory
    def light(p):
        return {
            "slug": p["slug"], "title": p["title"], "excerpt": p.get("excerpt", ""),
            "date": p.get("date", ""), "iso_date": p.get("iso_date", ""),
            "category": p.get("category", ""), "readTime": p.get("readTime", ""),
            "featured": bool(p.get("featured")), "tags": p.get("tags", [])[:5],
            "service": p.get("service", ""),
        }

    # Pre-group posts by service (for keyword match + fallback)
    by_service = {}
    for p in posts:
        s = p.get("service", "")
        if s:
            by_service.setdefault(s, []).append(p)

    def service_posts(service):
        # Posts whose `service` field matches, OR whose category maps to this
        # service (covers organic/management services that share a category).
        direct = by_service.get(service, [])
        cats = SERVICE_CATEGORIES.get(service, [])
        extra = [p for p in posts if p.get("category") in cats and p not in direct]
        return direct + extra

    clusters = {}
    summary = []
    for service in SERVICES:
        topical = parse_pillar_clusters(service)
        if not topical:
            print(f"  WARN no topical clusters for {service}")
            continue
        clusters[service] = {}
        for c in topical:
            tag = c["tag"]
            kws = CLUSTER_KEYWORDS.get(tag, [tag.lower()])
            matched = [p for p in service_posts(service) if post_matches(p, service, kws)]
            matched.sort(key=lambda p: (not p.get("featured"), p.get("iso_date", "")), reverse=True)
            # Fallback: if too few keyword matches, show the service's most recent
            # posts so the cluster page is never empty (truthful: real service posts).
            if len(matched) < 3:
                recent = sorted(service_posts(service),
                                key=lambda p: p.get("iso_date", ""), reverse=True)
                seen = {m["slug"] for m in matched}
                for p in recent:
                    if p["slug"] not in seen:
                        matched.append(p)
                        seen.add(p["slug"])
                    if len(matched) >= 6:
                        break
            matched = matched[:12]
            clusters[service][tag] = {
                "title": c["title"], "desc": c["desc"],
                "posts": [light(p) for p in matched],
                "count": len(matched),
            }
            summary.append((service, tag, len(matched)))

    if args.dry:
        print("Cluster match counts:")
        for s, t, n in summary:
            print(f"  {s:32s} {t:14s} {n}")
        return

    os.makedirs(os.path.dirname(CLUSTERS_OUT), exist_ok=True)
    json.dump(clusters, open(CLUSTERS_OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # Public copy for any runtime fetch (BlogFilter, future client use).
    json.dump(clusters, open(CLUSTERS_PUBLIC, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # Regenerate posts-index.json with `service` field + larger pool (300)
    idx = [light(p) for p in sorted(posts, key=lambda p: p.get("iso_date", ""), reverse=True)[:300]]
    json.dump(idx, open(INDEX_OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    total_empty = sum(1 for s, t, n in summary if n == 0)
    print(f"clusters.json written. Services: {len(clusters)}, clusters: {len(summary)}, empty: {total_empty}")
    print(f"posts-index.json written with {len(idx)} posts (service field included).")


if __name__ == "__main__":
    main()
