#!/usr/bin/env python3
"""
Batch 4 generator — Beriklan.co.id
Reads remaining keywords from Master_Keyword_Plan_Beriklan.xlsx "All Keywords (4952)" sheet,
generates SEO articles via Groq (llama-3.3-70b-versatile), appends to posts.json,
updates posts-index.json, and commits to GitHub in chunks.

Usage:
  python3 batch4_generate.py --limit 10         # dry-run small batch
  python3 batch4_generate.py --limit 200        # first 200
  python3 batch4_generate.py                    # all remaining
"""
import argparse
import base64
import json
import os
import openpyxl
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(WEB)
XLSX = os.path.join(ROOT, "data", "Master_Keyword_Plan_Beriklan.xlsx")
POSTS = os.path.join(WEB, "src", "data", "posts.json")
INDEX = os.path.join(WEB, "public", "data", "posts-index.json")

ZEN_KEY = open(os.path.expanduser("~/.beriklan/zen-key")).read().strip()
GROQ_URL = "https://opencode.ai/zen/v1/chat/completions"
MODEL = "deepseek-v4-flash-free"

GH_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
GH_OWNER = "ReqTimeout"
GH_REPO = "beriklan.co.id"

# Service slug -> display name (from Excel "Services & Seeds")
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

INTENT_LABEL = {
    "transactional": "jasa",
    "informational": "panduan",
    "navigational": "info",
    "commercial": "rekomendasi",
}


def load_remaining():
    posts = json.load(open(POSTS))
    existing = set(p["slug"] for p in posts)
    wb = openpyxl.load_workbook(XLSX, read_only=True)
    ws = wb["All Keywords (4952)"]
    rows = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        no, kw, svc, city, intent, slug = r[0], r[1], r[2], r[3], r[4], r[5]
        if not slug:
            continue
        slug = str(slug).strip()
        if slug in existing:
            continue
        rows.append({
            "no": no, "keyword": kw, "service": svc,
            "city": city, "intent": intent, "slug": slug,
        })
    return rows


def build_prompt(kw, svc_name, city, intent):
    intent_word = INTENT_LABEL.get(intent, "panduan")
    return (
        f"Tulis artikel SEO Bahasa Indonesia untuk topik: \"{kw}\".\n"
        f"Konteks: layanan {svc_name}, lokasi {city}, tipe konten {intent_word}.\n"
        f"Tone: profesional, terukur, senior performance marketing partner. Bahasa formal Indonesia.\n"
        f"Format: HTML langsung mulai dari <h2>. Struktur:\n"
        f"1. <h2>Pendahuluan</h2> — 1 paragraf kontekstual tentang {kw} di {city}\n"
        f"2. <h2>Cara Kerja & Langkah Praktis</h2> — <ul> dengan 4 langkah konkret\n"
        f"3. <h2>Yang Perlu Dihindari</h2> — 2-3 poin <ul>\n"
        f"4. <h2>Pertanyaan yang Sering Diajukan</h2> — 3x <h3> + <p> (FAQ relevan lokal {city})\n"
        f"5. <h2>Kesimpulan</h2> — 1 paragraf + CTA WhatsApp sopan\n"
        f"Target 500-650 kata. Sertakan nama kota {city} dan layanan {svc_name} secara natural.\n"
        f"JANGAN pakai kata: bikin, gak, nggak, pasti untung, garansi 100%, abal-abal, dll.\n"
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
                GROQ_URL,
                headers={"Authorization": f"Bearer {ZEN_KEY}", "Content-Type": "application/json"},
                json=payload, timeout=60,
            )
            if r.status_code == 200:
                msg = r.json()["choices"][0]["message"]
                text = (msg.get("content") or "").strip()
                if not text and msg.get("reasoning_content"):
                    text = msg["reasoning_content"].strip()
                return text or None
            if r.status_code == 429:
                import time
                time_sleep = 15 * (attempt + 1)
                time.sleep(time_sleep)
                continue
        except Exception:
            import time
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


def make_post(row):
    kw = row["keyword"]
    svc = row["service"]
    city = row["city"] or ""
    svc_name = SERVICE_NAMES.get(svc, svc)
    title = " ".join(w.capitalize() for w in kw.split())
    prompt = build_prompt(kw, svc_name, city, row["intent"])
    raw = call_groq(prompt)
    if not raw:
        return None
    content = clean_html(raw)
    if not content.startswith("<h2>"):
        content = "<h2>" + title + "</h2>\n" + content
    excerpt = content.replace("<", " <").replace(">", "> ").replace("\n", " ")
    excerpt = " ".join(excerpt.split())
    excerpt = excerpt[:180] + ("..." if len(excerpt) > 180 else "")
    now = datetime.now()
    date_str = now.strftime("%d %b %Y")
    iso = now.isoformat()
    words = len(content.split())
    return {
        "slug": row["slug"],
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
        "city": city,
        "liveUrl": None,
        "publish_date": date_str,
    }


def github_get(path):
    r = requests.get(
        f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}/contents/{path}",
        headers={"Authorization": f"token {GH_TOKEN}", "User-Agent": "batch4"},
        timeout=30,
    )
    return r


def github_put(path, content, message, sha=None):
    body = {"message": message, "content": content, "branch": "main"}
    if sha:
        body["sha"] = sha
    r = requests.put(
        f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}/contents/{path}",
        headers={"Authorization": f"token {GH_TOKEN}", "Content-Type": "application/json", "User-Agent": "batch4"},
        json=body, timeout=30,
    )
    return r


def push_posts(posts_local, new_posts, chunk_idx):
    # Update local posts.json
    posts_local.extend(new_posts)
    posts_local.sort(key=lambda p: p.get("iso_date", ""), reverse=True)
    content = json.dumps(posts_local, ensure_ascii=False, indent=2)
    b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    # Get current sha
    r = github_get("src/data/posts.json")
    sha = r.json().get("sha") if r.ok else None
    rp = github_put("src/data/posts.json", b64, f"feat(batch4): add {len(new_posts)} articles (chunk {chunk_idx})", sha)
    return rp.ok, len(posts_local)


def main():
    import time
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--chunk", type=int, default=100)
    args = ap.parse_args()

    rows = load_remaining()
    if args.limit:
        rows = rows[:args.limit]
    print(f"Remaining keywords to generate: {len(rows)}")

    posts_local = json.load(open(POSTS))
    new_posts = []
    done = 0
    chunk_idx = 0

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
                done += 1
                if done % 25 == 0:
                    print(f"  generated {done}/{len(rows)}")
            # Flush chunk
            if len(new_posts) >= args.chunk:
                chunk_idx += 1
                ok, total = push_posts(posts_local, new_posts, chunk_idx)
                print(f"  PUSHED chunk {chunk_idx}: {len(new_posts)} articles, total={total}, ok={ok}")
                new_posts = []

    # Flush remainder
    if new_posts:
        chunk_idx += 1
        ok, total = push_posts(posts_local, new_posts, chunk_idx)
        print(f"  PUSHED final chunk {chunk_idx}: {len(new_posts)} articles, total={total}, ok={ok}")

    # Update local file
    json.dump(posts_local, open(POSTS, "w"), ensure_ascii=False, indent=2)
    print(f"DONE. Total posts: {len(posts_local)}")


if __name__ == "__main__":
    main()
