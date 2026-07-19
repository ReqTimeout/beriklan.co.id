#!/usr/bin/env python3
"""
Merge Batch 4 articles from D1 (batch4_articles) into posts.json + posts-index.json,
commit to GitHub, and report count.

Usage:
  python3 merge_batch4.py          # merge all pending D1 articles
  python3 merge_batch4.py --dry    # just count, don't commit
"""
import argparse
import base64
import json
import os
import subprocess
import sys

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(WEB, "src", "data", "posts.json")
INDEX = os.path.join(WEB, "public", "data", "posts-index.json")

GH_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
GH_OWNER = "ReqTimeout"
GH_REPO = "beriklan.co.id"


def d1_query(sql):
    r = subprocess.run(
        ["npx", "wrangler", "d1", "execute", "beriklan-seo", "--remote", "--command", sql],
        capture_output=True, text=True,
    )
    return r.stdout


def d1_json(sql):
    """Extract JSON results from wrangler d1 output."""
    out = d1_query(sql)
    start = out.find("[")
    end = out.rfind("]")
    if start == -1 or end == -1:
        return []
    try:
        arr = json.loads(out[start:end + 1])
        return arr[0].get("results", []) if isinstance(arr, list) and arr else []
    except Exception:
        return []


def github_get(path):
    import requests
    r = requests.get(
        f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}/contents/{path}",
        headers={"Authorization": f"token {GH_TOKEN}", "User-Agent": "merge"}, timeout=30,
    )
    return r


def github_put(path, content, message, sha):
    import requests
    body = {"message": message, "content": content, "branch": "main"}
    if sha:
        body["sha"] = sha
    r = requests.put(
        f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}/contents/{path}",
        headers={"Authorization": f"token {GH_TOKEN}", "Content-Type": "application/json", "User-Agent": "merge"},
        json=body, timeout=30,
    )
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    # Pull pending articles from D1
    rows = d1_json("SELECT slug, data FROM batch4_articles")
    if not rows:
        print("No articles in D1 batch4_articles.")
        return
    print(f"Found {len(rows)} articles in D1.")

    posts_local = json.load(open(POSTS))
    existing = set(p["slug"] for p in posts_local)
    new_posts = []
    for r in rows:
        try:
            p = json.loads(r["data"])
        except Exception:
            continue
        if p["slug"] in existing:
            continue
        new_posts.append(p)

    print(f"New (not in posts.json): {len(new_posts)}")
    if not new_posts:
        return

    if args.dry:
        print("DRY RUN — no commit.")
        return

    posts_local.extend(new_posts)
    posts_local.sort(key=lambda p: p.get("iso_date", ""), reverse=True)
    content = json.dumps(posts_local, ensure_ascii=False, indent=2)
    b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    r = github_get("src/data/posts.json")
    sha = r.json().get("sha") if r.ok else None
    rp = github_put("src/data/posts.json", b64, f"feat(batch4): merge {len(new_posts)} articles from D1", sha)
    print(f"posts.json push: ok={rp.ok} ({len(posts_local)} total)")

    # Update index
    idx_rows = github_get("public/data/posts-index.json")
    if idx_rows.ok:
        idx = json.loads(base64.b64decode(idx_rows.json()["content"]).decode("utf-8"))
        new_idx = [{
            "slug": p["slug"], "title": p["title"], "excerpt": p["excerpt"],
            "date": p["date"], "iso_date": p["iso_date"], "category": p["category"],
            "readTime": p["readTime"], "featured": False, "tags": p["tags"],
        } for p in new_posts]
        merged = (new_idx + idx)[:24]
        idx_b64 = base64.b64encode(json.dumps(merged, ensure_ascii=False, indent=2).encode()).decode()
        github_put("public/data/posts-index.json", idx_b64, f"feat(batch4): update index {len(new_posts)}", idx_rows.json().get("sha"))

    # Save locally
    json.dump(posts_local, open(POSTS, "w"), ensure_ascii=False, indent=2)
    print("Local posts.json updated.")


if __name__ == "__main__":
    main()
