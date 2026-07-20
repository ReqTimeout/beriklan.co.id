#!/usr/bin/env python3
"""
clamp_future_dates.py — fix future-dated posts so freshness reflects actual time.

Background: 642 generated posts have iso_date in Aug-Oct 2026 while current
date is Jul 20 2026. They were artificially distributed to simulate a content
calendar but now show as "future" on the site, which is misleading.

Fix: redistribute future-dated posts BACKWARDS into [today-30, today],
preserving newest-first ordering. Most-future post becomes today;
least-future post becomes today-30. Posts already <= today are untouched.

Also refreshes posts-index.json (lightweight, no content field).
"""
import json
import os
from datetime import datetime, timedelta

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(WEB, "src/data/posts.json")
INDEX = os.path.join(WEB, "public/data/posts-index.json")

SPREAD_DAYS = 30  # redistribute across this many days in the past


def main():
    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    posts = json.load(open(POSTS))

    # Identify future-dated posts
    future = [p for p in posts if p.get("iso_date", "") > now.isoformat()]
    if not future:
        print("no future-dated posts; nothing to fix")
        return

    # Sort future posts newest first (they should already be, but be explicit)
    future.sort(key=lambda p: p.get("iso_date", ""), reverse=True)
    n = len(future)

    # Redistribute: index 0 (most-future) -> today, index n-1 (least-future) -> today - SPREAD_DAYS
    updated = 0
    for i, p in enumerate(future):
        # distribute linearly with small per-post variance so days aren't all same time
        offset = int(i / max(n - 1, 1) * SPREAD_DAYS)
        new_dt = today - timedelta(days=offset, seconds=(i * 137) % 86400)
        new_iso = new_dt.isoformat()
        old_iso = p.get("iso_date", "")
        if old_iso != new_iso:
            p["iso_date"] = new_iso
            p["date"] = new_dt.strftime("%d %b %Y")
            updated += 1

    # Re-sort all posts newest first
    posts.sort(key=lambda p: p.get("iso_date", ""), reverse=True)
    json.dump(posts, open(POSTS, "w"), ensure_ascii=False, indent=2)
    print(f"clamped {updated} future posts into [today-{SPREAD_DAYS}, today]")

    # Refresh posts-index.json (24 most recent)
    idx = [{
        "slug": p["slug"], "title": p["title"], "excerpt": p.get("excerpt", ""),
        "date": p["date"], "iso_date": p["iso_date"], "category": p.get("category", "strategy"),
        "readTime": p.get("readTime", "5 min"), "featured": p.get("featured", False),
        "tags": (p.get("tags") or [])[:5],
    } for p in posts[:24]]
    json.dump(idx, open(INDEX, "w"), ensure_ascii=False, indent=2)
    print(f"refreshed posts-index.json ({len(idx)} entries)")

    # Quick verification
    remaining_future = sum(1 for p in posts if p.get("iso_date", "") > now.isoformat())
    print(f"remaining future-dated posts: {remaining_future}")


if __name__ == "__main__":
    main()