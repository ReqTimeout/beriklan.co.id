#!/usr/bin/env python3
"""
Internal Link Optimizer — build-time enrichment of blog post content.

Strategy (safe, careful):
- For each post, link the FIRST occurrence of a relevant service/pillar keyword
  found in paragraph text to the corresponding service or pillar page.
- Max 2 links per post. Only keywords that match the post's own `service`
  or `category` relevance are used (topical relevance -> no spam).
- Never touch text inside existing tags/attributes/headings. Only <p> text.
- Skips a post if it already has internal links (idempotent).
"""
import json
import re
from pathlib import Path

BASE = Path("/Users/maabook/Desktop/beriklan.co.id/web")
POSTS = BASE / "src/data/posts.json"

# Service slug -> (display keyword variants, pillar url)
SERVICE_MAP = {
    "jasa-digital-marketing": {
        "url": "/jasa-digital-marketing/",
        "pillar": "/jasa-digital-marketing/pilar/",
        "keywords": ["digital marketing", "digital marketing company", "digital consultant", "konsultan digital", "agen digital", "agency digital"],
    },
    "jasa-iklan-facebook": {
        "url": "/jasa-iklan-facebook/",
        "pillar": "/jasa-iklan-facebook/pilar/",
        "keywords": ["facebook ads", "iklan facebook", "facebook", "meta ads", "iklan meta"],
    },
    "jasa-iklan-instagram": {
        "url": "/jasa-iklan-instagram/",
        "pillar": "/jasa-iklan-instagram/pilar/",
        "keywords": ["instagram ads", "iklan instagram", "instagram"],
    },
    "jasa-iklan-tiktok": {
        "url": "/jasa-iklan-tiktok/",
        "pillar": "/jasa-iklan-tiktok/pilar/",
        "keywords": ["tiktok ads", "iklan tiktok", "tiktok"],
    },
    "jasa-iklan-google": {
        "url": "/jasa-iklan-google/",
        "pillar": "/jasa-iklan-google/pilar/",
        "keywords": ["google ads", "iklan google", "sem", "search engine marketing", "google adwords"],
    },
    "jasa-iklan-youtube": {
        "url": "/jasa-iklan-youtube/",
        "pillar": "/jasa-iklan-youtube/pilar/",
        "keywords": ["youtube ads", "iklan youtube", "video ads", "youtube"],
    },
    "jasa-kelola-instagram": {
        "url": "/jasa-kelola-instagram/",
        "pillar": "/jasa-kelola-instagram/pilar/",
        "keywords": ["kelola instagram", "manajemen instagram", "instagram organik"],
    },
    "jasa-kelola-tiktok": {
        "url": "/jasa-kelola-tiktok/",
        "pillar": "/jasa-kelola-tiktok/pilar/",
        "keywords": ["kelola tiktok", "manajemen tiktok", "tiktok organik"],
    },
    "jasa-pembuatan-website": {
        "url": "/jasa-pembuatan-website/",
        "pillar": "/jasa-pembuatan-website/pilar/",
        "keywords": ["pembuatan website", "jasa website", "website"],
    },
    "jasa-pembuatan-landing-page": {
        "url": "/jasa-pembuatan-landing-page/",
        "pillar": "/jasa-pembuatan-landing-page/pilar/",
        "keywords": ["landing page", "pembuatan landing page"],
    },
}

MAX_LINKS_PER_POST = 2

def link_first_occurrence(text, keyword, url):
    """Wrap the first standalone occurrence of `keyword` (case-insensitive, word-bounded)
    in an <a> tag, but ONLY inside <p> paragraph text (never headings/attributes/existing links)."""
    pattern = re.compile(r'(?<![\w/"])' + re.escape(keyword) + r'(?![\w"])', re.IGNORECASE)
    # Only search within <p>...</p> blocks
    for pm in re.finditer(r'<p\b[^>]*>(.*?)</p>', text, re.DOTALL):
        p_start, p_end = pm.start(1), pm.end(1)
        para = pm.group(1)
        m = pattern.search(para)
        if not m:
            continue
        s, e = m.start(), m.end()
        abs_s = p_start + s
        abs_e = p_start + e
        # Guard: not already inside an <a>
        last_a_open = para.rfind('<a', 0, s)
        last_a_close = para.rfind('</a>', 0, s)
        if last_a_open != -1 and (last_a_close == -1 or last_a_open > last_a_close):
            continue
        replacement = f'<a href="{url}" class="ilink">{m.group(0)}</a>'
        new_para = para[:s] + replacement + para[e:]
        text = text[:p_start] + new_para + text[p_end:]
        return text, True
    return text, False

def optimize_post(post):
    content = post.get("content", "")
    if not content:
        return post, 0
    # Idempotency: skip if already has internal links
    if 'href="/' in content or 'href="/jasa' in content:
        return post, 0
    service = post.get("service")
    category = post.get("category")
    # Determine candidate keywords based on post's service (topical relevance)
    candidates = []
    if service and service in SERVICE_MAP:
        candidates.append((SERVICE_MAP[service]["keywords"], SERVICE_MAP[service]["url"]))
        # also link to pillar of same service occasionally (use pillar as 2nd link)
    # For strategy/case-study categories without a direct service, fall back to digital-marketing
    if not candidates and category in ("strategy", "case-study"):
        candidates.append((SERVICE_MAP["jasa-digital-marketing"]["keywords"], SERVICE_MAP["jasa-digital-marketing"]["url"]))
    if not candidates:
        return post, 0

    links_added = 0
    for keywords, url in candidates:
        if links_added >= MAX_LINKS_PER_POST:
            break
        for kw in keywords:
            content, done = link_first_occurrence(content, kw, url)
            if done:
                links_added += 1
                break  # one link per candidate group
    post["content"] = content
    return post, links_added

def main():
    import sys
    dry = "--dry" in sys.argv
    data = json.load(open(POSTS))
    total_links = 0
    updated = 0
    for p in data:
        p, n = optimize_post(p)
        if n > 0:
            updated += 1
            total_links += n
    print(f"{'[DRY] ' if dry else ''}Posts updated: {updated}, total links added: {total_links}")
    if not dry:
        json.dump(data, open(POSTS, "w"), ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
