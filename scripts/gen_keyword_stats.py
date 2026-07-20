#!/usr/bin/env python3
"""
Aggregate keyword-queue.json + posts.json -> public/data/keyword-stats.json

Runs at build time (hooked in package.json build). Output is consumed by
worker endpoint /api/admin/keywords (token-protected dashboard) which merges
this static snapshot with live D1 indexing status.

Covers:
- totals: keywords, generated (has article), pending, coverage %
- per-service: total / generated / pending / coverage
- per-city: total / generated / pending / coverage
- per-source: miner vs suggest+combo
- recent generated keywords (by created_at desc)
- posts totals: count, by service (generated posts carry `service`/`city`)
"""
import json
import os
import re
from collections import defaultdict
from datetime import datetime

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = os.path.join(WEB, "src", "data", "keyword-queue.json")
POSTS = os.path.join(WEB, "src", "data", "posts.json")
OUT = os.path.join(WEB, "public", "data", "keyword-stats.json")

SERVICES = [
    ("jasa-digital-marketing", "Jasa Digital Marketing",
     ["jasa digital marketing", "digital marketing", "internet marketing",
      "digital agency", "search engine marketers", "search engine marketing",
      "agency digital", "konsultan marketing"]),
    ("jasa-iklan-facebook", "Jasa Iklan Facebook",
     ["jasa iklan facebook", "iklan facebook", "facebook ads", "jasa fb ads",
      "iklan fb", "fb ads"]),
    ("jasa-iklan-instagram", "Jasa Iklan Instagram",
     ["jasa iklan instagram", "iklan instagram", "instagram ads", "jasa ig ads",
      "iklan ig", "ig ads"]),
    ("jasa-iklan-tiktok", "Jasa Iklan TikTok",
     ["jasa iklan tiktok", "iklan tiktok", "tiktok ads"]),
    ("jasa-iklan-google", "Jasa Iklan Google",
     ["jasa iklan google", "iklan google", "google ads", "google adwords",
      "iklan adwords", "jasa adwords"]),
    ("jasa-iklan-youtube", "Jasa Iklan YouTube",
     ["jasa iklan youtube", "iklan youtube", "youtube ads"]),
    ("jasa-kelola-instagram", "Jasa Kelola Instagram",
     ["jasa kelola instagram", "kelola instagram", "jasa manage instagram",
      "jasa admin instagram", "admin instagram"]),
    ("jasa-kelola-tiktok", "Jasa Kelola TikTok",
     ["jasa kelola tiktok", "kelola tiktok", "jasa manage tiktok",
      "jasa admin tiktok", "admin tiktok"]),
    ("jasa-pembuatan-website", "Jasa Pembuatan Website",
     ["jasa pembuatan website", "jasa buat website", "pembuatan website", "jasa website",
      "jasa pembuat website", "jasa bikin website", "jasa pembuat web", "jasa bikin web",
      "jasa buat web", "jasa web", "bikin website", "buat website", "pembuat website",
      "jasa situs", "website murah", "web murah", "desain website", "jasa desain web",
      "web site", "pembuat web", "pembuatan web", "situs web", "membuat web",
      "tampilan web", "tampilan website", "desain web", "situs website", "web umkm",
      "bikin web", "buat web"]),
    ("jasa-pembuatan-landing-page", "Jasa Pembuatan Landing Page",
     ["landing page", "landingpage"]),
    ("jasa-view-live", "Jasa View Live",
     ["view live", "viewers live", "penonton live", "view live tiktok", "view live instagram",
      "view live youtube", "view live shopee", "view live twitch", "viewers tiktok",
      "viewers instagram", "viewers youtube", "jasa viewers", "jasa penonton",
      "view tiktok", "view instagram", "tambah viewers", "naikin viewers"]),
]

CITIES = [
    ("jakarta", "Jakarta"), ("bandung", "Bandung"), ("surabaya", "Surabaya"),
    ("yogyakarta", "Yogyakarta"), ("jogja", "Yogyakarta"), ("semarang", "Semarang"),
    ("medan", "Medan"), ("makassar", "Makassar"), ("denpasar", "Denpasar"),
    ("bali", "Bali"), ("bekasi", "Bekasi"), ("depok", "Depok"),
    ("tangerang", "Tangerang"), ("bogor", "Bogor"), ("malang", "Malang"),
    ("batam", "Batam"), ("palembang", "Palembang"), ("pekanbaru", "Pekanbaru"),
    ("sidoarjo", "Sidoarjo"), ("solo", "Solo"), ("surakarta", "Solo"),
    ("padang", "Padang"), ("manado", "Manado"), ("pontianak", "Pontianak"),
    ("banjarmasin", "Banjarmasin"), ("lampung", "Lampung"), ("jambi", "Jambi"),
    ("cimahi", "Cimahi"), ("balikpapan", "Balikpapan"), ("samarinda", "Samarinda"),
]


def derive_service(kw):
    kw = kw.lower()
    # view-live phrases first (they also contain platform names like "tiktok")
    for slug, name, patterns in reversed(SERVICES):
        for p in patterns:
            if p in kw:
                return slug, name
    return "lainnya", "Lainnya / Umum"


def derive_city(kw):
    kw = " " + kw.lower() + " "
    for slug, name in CITIES:
        if f" {slug} " in kw:
            return slug, name
    return None, None


def bucket(rows, key_fn):
    agg = defaultdict(lambda: {"total": 0, "generated": 0, "pending": 0})
    for r in rows:
        k = key_fn(r)
        if k is None:
            continue
        agg[k]["total"] += 1
        if r.get("status") == "generated" or r.get("has_post"):
            agg[k]["generated"] += 1
        else:
            agg[k]["pending"] += 1
    out = []
    for k, v in agg.items():
        cov = round(100.0 * v["generated"] / v["total"], 1) if v["total"] else 0.0
        out.append({"key": k, **v, "coverage": cov})
    out.sort(key=lambda x: (-x["total"], x["key"]))
    return out


def main():
    queue = json.load(open(QUEUE))
    posts = json.load(open(POSTS))
    post_slugs = set(p["slug"] for p in posts)

    # Enrich rows with derived service/city + truth-check against posts.json
    for r in queue:
        r["_svc_slug"], r["_svc_name"] = derive_service(r.get("keyword", ""))
        r["_city_slug"], r["_city_name"] = derive_city(r.get("keyword", ""))
        r["_live"] = r["slug"] in post_slugs

    total = len(queue)
    generated = sum(1 for r in queue if r.get("status") == "generated" or r.get("has_post"))
    live = sum(1 for r in queue if r["_live"])
    pending = total - generated

    svc = bucket(queue, lambda r: r["_svc_name"])
    city = bucket(queue, lambda r: r["_city_name"])
    src = bucket(queue, lambda r: r.get("source", "?"))

    # Recent generated
    recent = sorted(
        (r for r in queue if r.get("status") == "generated"),
        key=lambda r: r.get("created_at", ""), reverse=True,
    )[:40]
    recent_out = [{
        "keyword": r["keyword"], "slug": r["slug"],
        "service": r["_svc_name"], "city": r["_city_name"],
        "live": r["_live"], "created_at": r.get("created_at", "")[:19],
        "url": f"https://beriklan.co.id/blog/{r['slug']}/",
    } for r in recent]

    # Posts aggregation
    gen_posts = [p for p in posts if p.get("generated")]
    posts_by_service = defaultdict(int)
    for p in gen_posts:
        posts_by_service[p.get("service") or "unknown"] += 1

    stats = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "keywords": {
            "total": total, "generated": generated, "pending": pending,
            "live_in_posts": live,
            "coverage": round(100.0 * generated / total, 1) if total else 0.0,
        },
        "posts": {
            "total": len(posts),
            "generated": len(gen_posts),
            "by_service": dict(sorted(posts_by_service.items(), key=lambda x: -x[1])),
        },
        "by_service": svc,
        "by_city": city,
        "by_source": src,
        "recent_generated": recent_out,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(stats, open(OUT, "w"), ensure_ascii=False, indent=2)
    # Also expose lightweight queue to Worker via ASSETS (so /api/cron/hourly-generate can read it)
    import shutil
    queue_public = os.path.join(WEB, "public", "data", "keyword-queue.json")
    os.makedirs(os.path.dirname(queue_public), exist_ok=True)
    shutil.copy(QUEUE, queue_public)
    print(f"keyword-queue.json: {total} keywords ({generated} gen / {pending} pending), {len(posts)} posts")
    print(f"  copied -> public/data/keyword-queue.json for Worker ASSETS access")


if __name__ == "__main__":
    main()
