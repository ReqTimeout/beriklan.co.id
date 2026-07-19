#!/usr/bin/env python3
"""
freshness_engine.py — Beriklan.co.id content freshness layer (build-time, idempotent)

What it does (NO fabricated dates):
  1. Computes post age from iso_date (relative to --now, default today).
  2. Adds deterministic, truthful fields to every post in src/data/posts.json:
       - last_reviewed : ISO timestamp. Equals publish iso_date unless the slug is
                         present in the curated REFRESHED_SLUGS allowlist (posts we
                         actually re-edited), in which case it uses the allowlist date.
       - freshness     : one of 'recent' (<=12mo), 'aging' (12-24mo), 'stale' (>24mo).
       - refresh_priority : 0 (none) .. 3 (high) — operational queue score for the
                            review backlog, based on category value + length + featured.
  3. Emits public/data/freshness.json — aggregate stats + the top-N review queue,
     so a future worker/dashboard can consume staleness without parsing 4MB posts.json.
  4. Prints a short report to stdout.

It NEVER invents a "reviewed on" date for content we have not touched. The visible
site only shows "Diperbarui" when a post is in REFRESHED_SLUGS. Everything else shows
the honest publish date. This keeps us compliant with the no-fake-claims rule.

Usage:
  python3 scripts/freshness_engine.py [--now YYYY-MM-DD] [--queue N]
"""
import json, os, sys, argparse, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, "src/data/posts.json")
OUT_JSON = os.path.join(ROOT, "public/data/freshness.json")

# Posts we have ACTUALLY re-edited get a truthful last_reviewed date.
# Start empty. Add a slug here ONLY after the content is genuinely refreshed,
# with the real edit date. (Do not fabricate.)
REFRESHED_SLUGS = {
    # "contoh-artikel-segar": "2026-07-15T10:00:00",
}

# Category business value weights (higher = more worth keeping fresh).
CAT_WEIGHT = {
    "google": 3, "meta": 3, "tiktok": 3, "youtube": 2,
    "strategy": 2, "case-study": 3, "trending": 1,
}

MONTH_DAYS = 30.44

def months_between(a: datetime.datetime, b: datetime.datetime) -> float:
    return (b - a).days / MONTH_DAYS

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--now", default=datetime.date.today().isoformat())
    ap.add_argument("--queue", type=int, default=50)
    args = ap.parse_args()

    now = datetime.datetime.fromisoformat(args.now + "T00:00:00")
    with open(POSTS, encoding="utf-8") as f:
        posts = json.load(f)

    buckets = {"recent": 0, "aging": 0, "stale": 0}
    queue = []
    touched = 0

    for p in posts:
        iso = p.get("iso_date") or p.get("publish_date") or p.get("date")
        try:
            pub = datetime.datetime.fromisoformat(iso)
        except Exception:
            pub = now
        age_mo = months_between(pub, now)

        if age_mo <= 12:
            fresh = "recent"
        elif age_mo <= 24:
            fresh = "aging"
        else:
            fresh = "stale"
        buckets[fresh] += 1

        # Truthful last_reviewed
        if p["slug"] in REFRESHED_SLUGS:
            last_reviewed = REFRESHED_SLUGS[p["slug"]]
            actually_refreshed = True
        else:
            last_reviewed = p.get("iso_date")
            actually_refreshed = False

        # Operational priority for the review backlog (0..3)
        cat = p.get("category", "strategy")
        w = CAT_WEIGHT.get(cat, 2)
        length = len(p.get("content", ""))
        feat = 1 if p.get("featured") else 0
        if fresh == "stale":
            base = 2
        elif fresh == "aging":
            base = 1
        else:
            base = 0
        priority = min(3, base + (1 if w >= 3 else 0) + (1 if length > 1200 else 0) + feat)
        p["last_reviewed"] = last_reviewed
        p["freshness"] = fresh
        p["refresh_priority"] = priority
        if actually_refreshed:
            touched += 1

        if fresh == "stale":
            queue.append({
                "slug": p["slug"],
                "title": p.get("title", ""),
                "category": cat,
                "age_months": round(age_mo, 1),
                "priority": priority,
                "refreshed": actually_refreshed,
            })

    # Sort queue by priority desc, then age desc, then length
    queue.sort(key=lambda x: (-x["priority"], -x["age_months"]))
    top = queue[: args.queue]

    with open(POSTS, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=1)

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    report = {
        "generated_at": now.isoformat(),
        "total_posts": len(posts),
        "buckets": buckets,
        "stale_pct": round(buckets["stale"] / len(posts) * 100, 1),
        "refreshed_count": touched,
        "review_queue_size": len(queue),
        "top_queue": top,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Freshness engine complete.")
    print(f"  Total posts      : {len(posts)}")
    print(f"  recent (<=12mo)  : {buckets['recent']}")
    print(f"  aging  (12-24mo) : {buckets['aging']}")
    print(f"  stale  (>24mo)   : {buckets['stale']} ({report['stale_pct']}%)")
    print(f"  refreshed (real) : {touched}")
    print(f"  review queue     : {len(queue)} stale posts")
    print(f"  wrote {OUT_JSON}")

if __name__ == "__main__":
    main()
