#!/usr/bin/env python3
"""
Generate SEO articles from src/data/keyword-queue.json (mined untapped keywords).

Reads top-N keywords by priority_score, derives service+city+intent from the
keyword text, generates a real Indonesian article via Groq (llama-3.1-8b),
appends to src/data/posts.json, refreshes posts-index.json, and pushes to GitHub.

Usage:
  python3 scripts/gen_from_queue.py --limit 20
  python3 scripts/gen_from_queue.py --limit 50 --workers 4
"""
import argparse
import base64
import json
import os
import re
import sys
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(WEB)
QUEUE = os.path.join(WEB, "src", "data", "keyword-queue.json")
POSTS = os.path.join(WEB, "src", "data", "posts.json")
INDEX = os.path.join(WEB, "public", "data", "posts-index.json")

ZEN_KEY = open(os.path.expanduser("~/.beriklan/zen-key")).read().strip()
ZEN_URL = "https://opencode.ai/zen/v1/chat/completions"
MODEL = "deepseek-v4-flash-free"

GH_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
GH_OWNER = "ReqTimeout"
GH_REPO = "beriklan.co.id"

SERVICE_NAMES = {
    "jasa-iklan-facebook": "Jasa Iklan Facebook Ads",
    "jasa-iklan-instagram": "Jasa Iklan Instagram",
    "jasa-iklan-tiktok": "Jasa Iklan TikTok Ads",
    "jasa-iklan-google": "Jasa Iklan Google Ads",
    "jasa-iklan-youtube": "Jasa Iklan YouTube",
    "jasa-kelola-instagram": "Jasa Kelola Instagram",
    "jasa-kelola-tiktok": "Jasa Kelola TikTok",
    "jasa-pembuatan-website": "Jasa Pembuatan Website",
    "jasa-pembuatan-landing-page": "Jasa Pembuatan Landing Page",
    "jasa-digital-marketing": "Jasa Digital Marketing",
}
CITY_LIST = ["jakarta", "bandung", "surabaya", "yogyakarta", "semarang", "medan",
             "makassar", "denpasar", "balikpapan", "bekasi", "depok", "tangerang",
             "bogor", "malang", "batam", "palembang", "bandar lampung", "pekanbaru"]

INTENT_LABEL = {
    "transactional": "jasa",
    "informational": "panduan",
    "commercial": "rekomendasi",
    "navigational": "info",
}


def classify(kw):
    k = kw.lower()
    svc = "jasa-digital-marketing"
    if "facebook" in k or "meta" in k:
        svc = "jasa-iklan-facebook"
    elif "instagram" in k and "kelola" in k:
        svc = "jasa-kelola-instagram"
    elif "instagram" in k:
        svc = "jasa-iklan-instagram"
    elif "tiktok" in k and "kelola" in k:
        svc = "jasa-kelola-tiktok"
    elif "tiktok" in k:
        svc = "jasa-iklan-tiktok"
    elif "youtube" in k:
        svc = "jasa-iklan-youtube"
    elif "google" in k or "ads" in k or "search" in k:
        svc = "jasa-iklan-google"
    elif "landing" in k:
        svc = "jasa-pembuatan-landing-page"
    elif "website" in k or "web" in k:
        svc = "jasa-pembuatan-website"
    city = ""
    for c in CITY_LIST:
        if c in k:
            city = c
            break
    intent = "transactional"
    if any(w in k for w in ["cara", "panduan", "tips", "apa", "bagaimana"]):
        intent = "informational"
    elif any(w in k for w in ["terbaik", "rekomendasi", "review", "murah"]):
        intent = "commercial"
    return svc, city, intent


def build_prompt(kw, svc_name, city, intent):
    intent_word = INTENT_LABEL.get(intent, "panduan")
    loc = city.capitalize() if city else "Indonesia"
    return (
        f"Tulis artikel SEO Bahasa Indonesia untuk topik: \"{kw}\".\n"
        f"Konteks: layanan {svc_name}, lokasi {loc}, tipe konten {intent_word}.\n"
        f"Tone: profesional, terukur, senior performance marketing partner. Bahasa formal Indonesia.\n"
        f"Format: HTML langsung mulai dari <h2>. Struktur:\n"
        f"1. <h2>Pendahuluan</h2> — 1 paragraf kontekstual tentang {kw}{' di ' + loc if city else ''}\n"
        f"2. <h2>Cara Kerja & Langkah Praktis</h2> — <ul> dengan 4 langkah konkret\n"
        f"3. <h2>Yang Perlu Dihindari</h2> — 2-3 poin <ul>\n"
        f"4. <h2>Pertanyaan yang Sering Diajukan</h2> — 3x <h3> + <p> (FAQ relevan lokal {loc})\n"
        f"5. <h2>Kesimpulan</h2> — 1 paragraf + CTA WhatsApp sopan ke Beriklan\n"
        f"Target 500-650 kata. Sertakan nama lokasi {loc} dan layanan {svc_name} secara natural.\n"
        f"JANGAN pakai kata: bikin, gak, nggak, pasti untung, garansi 100%, abal-abal.\n"
        f"Output HANYA body HTML, tanpa markdown, mulai dari <h2>."
    )


def call_groq(prompt, max_retries=5):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1800,
        "temperature": 0.7,
        "thinking": {"type": "disabled"},
    }
    for attempt in range(max_retries):
        try:
            r = requests.post(
                ZEN_URL,
                headers={"Authorization": f"Bearer {ZEN_KEY}", "Content-Type": "application/json"},
                json=payload, timeout=60,
            )
            if r.status_code == 200:
                msg = r.json()["choices"][0]["message"]
                text = (msg.get("content") or "").strip()
                if not text and msg.get("reasoning_content"):
                    # Some reasoning models echo answer inside reasoning_content
                    text = msg["reasoning_content"].strip()
                return text or None
            if r.status_code == 429:
                time.sleep(15 * (attempt + 1))
                continue
        except Exception:
            time.sleep(5)
    return None


def clean_html(html):
    h = html.strip()
    if h.startswith("```html"):
        h = h[7:]
    if h.startswith("```"):
        h = h[3:]
    if h.endswith("```"):
        h = h[:-3]
    return h.strip()


def make_post(item):
    kw = item["keyword"]
    slug = item["slug"]
    svc, city, intent = classify(kw)
    svc_name = SERVICE_NAMES.get(svc, svc)
    title = " ".join(w.capitalize() for w in kw.split())
    prompt = build_prompt(kw, svc_name, city, intent)
    raw = call_groq(prompt)
    if not raw:
        return None
    content = clean_html(raw)
    if not content.startswith("<h2>"):
        content = "<h2>" + title + "</h2>\n" + content
    # Internal-link CTA block (money pages) — reuse retrofit builder
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from retrofit_internal_links import build_block
    content = content.rstrip() + "\n" + build_block({"service": svc, "city": city, "title": title})
    excerpt = content.replace("<", " <").replace(">", "> ").replace("\n", " ")
    excerpt = " ".join(excerpt.split())
    excerpt = excerpt[:180] + ("..." if len(excerpt) > 180 else "")
    now = datetime.now()
    date_str = now.strftime("%d %b %Y")
    iso = now.isoformat()
    words = len(content.split())
    return {
        "slug": slug,
        "title": title,
        "excerpt": excerpt,
        "content": content,
        "date": date_str,
        "iso_date": iso,
        "category": "strategy",
        "readTime": f"{max(2, round(words / 200))} min",
        "tags": [t for t in kw.lower().split() if len(t) > 3][:5],
        "featured": False,
        "generated": True,
        "service": svc,
        "city": city or None,
        "liveUrl": None,
        "publish_date": date_str,
    }


def github_get(path):
    r = requests.get(
        f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}/contents/{path}",
        headers={"Authorization": f"token {GH_TOKEN}", "User-Agent": "gen_queue"},
        timeout=30,
    )
    return r


def github_put(path, content, message, sha=None):
    body = {"message": message, "content": content, "branch": "main"}
    if sha:
        body["sha"] = sha
    r = requests.put(
        f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}/contents/{path}",
        headers={"Authorization": f"token {GH_TOKEN}", "Content-Type": "application/json", "User-Agent": "gen_queue"},
        json=body, timeout=30,
    )
    return r


def refresh_index(posts):
    light = [{
        "slug": p["slug"], "title": p["title"], "excerpt": p["excerpt"],
        "date": p["date"], "iso_date": p["iso_date"], "category": p["category"],
        "readTime": p["readTime"], "featured": p.get("featured", False),
        "tags": p.get("tags", [])[:5],
    } for p in posts[:24]]
    return light


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    queue = json.load(open(QUEUE))
    # Sort by priority score desc, skip already-generated slugs
    queue.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
    posts_local = json.load(open(POSTS))
    existing = set(p["slug"] for p in posts_local)
    rows = [q for q in queue if q["slug"] not in existing][:args.limit]
    print(f"Generating {len(rows)} articles from queue")

    new_posts = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(make_post, r): r for r in rows}
        for fut in as_completed(futures):
            row = futures[fut]
            try:
                post = fut.result()
            except Exception as e:
                print(f"  ERR {row['slug']}: {e}")
                post = None
            if post:
                new_posts.append(post)
                print(f"  + {post['slug']} ({post['service']})")
            else:
                print(f"  ! failed: {row['slug']}")

    if not new_posts:
        print("No articles generated.")
        return

    posts_local.extend(new_posts)
    posts_local.sort(key=lambda p: p.get("iso_date", ""), reverse=True)
    content = json.dumps(posts_local, ensure_ascii=False, indent=2)
    b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    r = github_get("src/data/posts.json")
    sha = r.json().get("sha") if r.ok else None
    rp = github_put("src/data/posts.json", b64, f"feat(queue): add {len(new_posts)} articles from keyword queue", sha)
    print(f"Pushed posts.json: ok={rp.ok}")

    # Refresh index (also push)
    idx = refresh_index(posts_local)
    idx_b64 = base64.b64encode(json.dumps(idx, ensure_ascii=False, indent=2).encode()).decode()
    ri = github_get("public/data/posts-index.json")
    idx_sha = ri.json().get("sha") if ri.ok else None
    github_put("public/data/posts-index.json", idx_b64, f"feat(queue): refresh index +{len(new_posts)}", idx_sha)

    # Mark queue items processed
    for p in new_posts:
        for q in queue:
            if q["slug"] == p["slug"]:
                q["status"] = "generated"
                q["has_post"] = True
    json.dump(queue, open(QUEUE, "w"), ensure_ascii=False, indent=2)

    json.dump(posts_local, open(POSTS, "w"), ensure_ascii=False, indent=2)
    json.dump(idx, open(INDEX, "w"), ensure_ascii=False, indent=2)
    print(f"DONE. Total posts: {len(posts_local)}")

    # Auto-enqueue new article URLs to D1 pending_indexing for IndexNow crawl
    enqueue_for_indexing(new_posts)


def enqueue_for_indexing(new_posts):
    """Push new blog post URLs to worker /api/index-url so the daily
    indexing cron auto-submits them to IndexNow/Google."""
    token = os.environ.get("ADMIN_TOKEN", "beriklan-admin-2026")
    worker_base = os.environ.get("WORKER_BASE", "https://beriklan.co.id")
    urls = [f"https://beriklan.co.id/blog/{p['slug']}/" for p in new_posts]
    if not urls:
        return
    try:
        r = requests.post(
            f"{worker_base}/api/index-url?token={token}",
            json={"urls": urls},
            timeout=20,
        )
        if r.ok:
            print(f"Enqueued {r.json().get('inserted', 0)} URLs for indexing")
        else:
            print(f"  ! index-url enqueue failed: {r.status_code} {r.text[:120]}")
    except Exception as e:
        print(f"  ! index-url enqueue error: {e}")


if __name__ == "__main__":
    main()
