#!/usr/bin/env python3
"""
Generate src/data/posts-meta.json (lightweight metadata) dari src/data/posts.json (4MB full content).

Output shape (per post):
  {
    "slug", "title", "excerpt", "date", "iso_date", "category",
    "readTime", "liveUrl", "tags", "featured", "word_count", "has_images"
  }

Used untuk build-time lookup (BlogFilter.svelte) tanpa parse full HTML content.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
POSTS_FULL = ROOT / "src/data/posts.json"
POSTS_META = ROOT / "src/data/posts-meta.json"

def strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html).strip()

def count_words(text: str) -> int:
    return len(text.split())

def main():
    if not POSTS_FULL.exists():
        print(f"ERROR: {POSTS_FULL} not found")
        return
    posts = json.loads(POSTS_FULL.read_text())
    print(f"Loaded {len(posts)} posts from {POSTS_FULL.name}")

    meta = []
    for p in posts:
        content = p.get("content", "")
        word_count = count_words(strip_html(content))
        has_images = bool(re.search(r"<img", content))
        meta.append({
            "slug": p.get("slug"),
            "title": p.get("title"),
            "excerpt": p.get("excerpt"),
            "date": p.get("date"),
            "iso_date": p.get("iso_date"),
            "category": p.get("category"),
            "readTime": p.get("readTime"),
            "liveUrl": p.get("liveUrl", ""),
            "tags": (p.get("tags") or [])[:8],
            "featured": p.get("featured", False),
            "word_count": word_count,
            "has_images": has_images,
        })

    POSTS_META.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    size = POSTS_META.stat().st_size
    print(f"Wrote {POSTS_META.name}: {len(meta)} posts, {size:,} bytes")
    avg_words = sum(m["word_count"] for m in meta) // len(meta)
    print(f"  avg words per post: {avg_words}")

if __name__ == "__main__":
    main()
