#!/usr/bin/env python3
"""
bulk_generate_all.py — Massive local article generator in DRAFT mode.

Reads keyword-queue.json (27K keywords), generates articles via ZEN API,
saves to drafts/ locally. Skips existing live post slugs.

Usage:
  python3 scripts/bulk_generate_all.py --batch 20 --workers 5
  python3 scripts/bulk_generate_all.py --resume
  python3 scripts/bulk_generate_all.py --limit 100
"""
import argparse, json, os, re, sys, time, requests, threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = os.path.join(WEB, "web", "src", "data", "keyword-queue.json")
LIVE_POSTS = os.path.join(WEB, "web", "src", "data", "posts.json")
DRAFTS_DIR = os.path.join(WEB, "drafts")
PROGRESS_FILE = os.path.join(DRAFTS_DIR, "_progress.json")
ZEN_KEY_PATH = os.path.expanduser("~/.beriklan/zen-key")

ZEN_URL = "https://opencode.ai/zen/v1/chat/completions"
# Multi-model rotation. Each model has independent rate limit on free tier.
MODELS = ["deepseek-v4-flash-free", "nemotron-3-ultra-free"]
MAX_WORKERS = 5
ERR_LOG = "/tmp/bulk_generate_err.log"

# Per-model lockout timestamps (epoch seconds). If a model hits rate limit,
# it's locked out for LOCKOUT_S seconds.
model_lockout = {m: 0 for m in MODELS}
model_lock = threading.Lock()
LOCKOUT_S = 15  # seconds to wait before retrying a rate-limited model

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
    "jasa-view-live": "Jasa View Live",
}

SERVICE_PATHS = {
    "jasa-iklan-facebook": "jasa-iklan-facebook",
    "jasa-iklan-instagram": "jasa-iklan-instagram",
    "jasa-iklan-tiktok": "jasa-iklan-tiktok",
    "jasa-iklan-google": "jasa-iklan-google",
    "jasa-iklan-youtube": "jasa-iklan-youtube",
    "jasa-kelola-instagram": "jasa-kelola-instagram",
    "jasa-kelola-tiktok": "jasa-kelola-tiktok",
    "jasa-pembuatan-website": "jasa-pembuatan-website",
    "jasa-pembuatan-landing-page": "jasa-pembuatan-landing-page",
    "jasa-digital-marketing": "jasa-digital-marketing",
    "jasa-view-live": "jasa-view-live",
}

def read_zen_key():
    try:
        return open(ZEN_KEY_PATH).read().strip()
    except:
        print("ERROR: Zen API key not found at", ZEN_KEY_PATH)
        sys.exit(1)

def get_model(attempt=0):
    """Return a model that's not currently locked out. Rotate through MODELS."""
    now = time.time()
    with model_lock:
        for m in MODELS:
            if model_lockout[m] < now:
                return m
    # All models locked out — pick the soonest-to-unlock one
    with model_lock:
        return min(MODELS, key=lambda m: model_lockout[m])

def lock_model(model, seconds=LOCKOUT_S):
    with model_lock:
        model_lockout[model] = time.time() + seconds

def load_live_slugs():
    try:
        posts = json.load(open(LIVE_POSTS))
        return set(x.get("slug") for x in posts)
    except:
        return set()

def build_prompt(kw, svc_name, city, svc_key):
    loc = city.capitalize() if city else "ID"
    svc_path = SERVICE_PATHS.get(svc_key, svc_key)
    ilink = f"https://beriklan.co.id/{svc_path}/"
    
    platform = svc_name.lower()
    if "google" in platform: elink = "https://ads.google.com/intl/id_id/home/"
    elif "facebook" in platform or "instagram" in platform: elink = "https://www.facebook.com/business/ads"
    elif "tiktok" in platform: elink = "https://ads.tiktok.com/"
    elif "youtube" in platform: elink = "https://www.youtube.com/ads/"
    else: elink = "https://beriklan.co.id/"
    
    return f"""Buat artikel HTML 400 kata untuk: {kw}
Layanan: {svc_name}. Lokasi: {loc}.

<h2>Pendahuluan</h2> definisi {kw} 1 paragraf
<h2>Manfaat</h2> 3 poin <ul>
<h2>Cara Kerja</h2> 3 langkah <ol>
<h2>Biaya</h2> "Mulai Rp500rb"
<h2>FAQ</h2> 3 <h3>+<p>
<h2>Kesimpulan</h2> 1 paragraf + WA

Wajib: 2x link {ilink}, 1x <a href="{elink}" rel=nofollow>
Penulis: Tim Beriklan
Formal Indo. Jangan: bikin,gak,nggak,pasti,garansi
Output HANYA HTML dari <h2>."""

ERR_LOG = "/tmp/bulk_generate_err.log"

def log_err(keyword, slug, reason):
    line = f"[{datetime.now().isoformat()}] {slug}: {reason}"
    with open(ERR_LOG, "a") as f:
        f.write(line + "\n")
    print(f"  ⚠ ERROR: {slug} — {reason}", file=sys.stderr)

def call_zen(prompt, zen_key, timeout=90):
    """Try models in rotation; lock out rate-limited ones."""
    last_err = None
    for attempt in range(4):
        model = get_model(attempt)
        try:
            r = requests.post(ZEN_URL,
                headers={"Authorization": f"Bearer {zen_key}", "Content-Type": "application/json"},
                json={"model": model, "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": 1500, "temperature": 0.6, "thinking": {"type": "disabled"}},
                timeout=timeout)
            if r.status_code == 200:
                try:
                    data = r.json()
                except:
                    last_err = "json parse fail"
                    continue
                if data.get("error"):
                    err_type = data["error"].get("type", "")
                    if "FreeUsageLimit" in err_type or "rate_limit" in err_type or "insufficient" in str(data["error"]).lower():
                        lock_model(model, LOCKOUT_S)
                        last_err = f"{model}: {err_type}"
                        continue
                    last_err = f"{model}: {data['error'].get('message','')[:100]}"
                    continue
                text = (data.get("choices", [{}])[0].get("message", {}).get("content", "") or "").strip()
                if len(text) > 300:
                    return text
                # Sometimes content is in reasoning_content
                text2 = (data.get("choices", [{}])[0].get("message", {}).get("reasoning_content", "") or "").strip()
                if len(text2) > 300:
                    return text2
                last_err = f"{model}: too short ({len(text)})"
                continue
            elif r.status_code == 429:
                lock_model(model, LOCKOUT_S)
                last_err = f"{model}: 429"
                continue
            else:
                last_err = f"{model}: HTTP {r.status_code}"
                time.sleep(1)
        except Exception as e:
            last_err = f"{model}: {str(e)[:100]}"
            time.sleep(1)
    return None

def clean_html(html):
    h = html.strip()
    for pfx in ["```html", "```"]:
        if h.startswith(pfx): h = h[len(pfx):]
    if h.endswith("```"): h = h[:-3]
    return h.strip()

def make_article(item, zen_key, live_slugs):
    kw = item["keyword"]
    slug = item.get("slug") or re.sub(r"[^a-z0-9-]", "", kw.lower().replace(" ", "-"))[:80]
    
    if slug in live_slugs:
        return None  # skip duplicate
    
    svc = item.get("service") or "jasa-digital-marketing"
    city = item.get("city") or ""
    svc_name = SERVICE_NAMES.get(svc, svc)
    
    title = " ".join(w.capitalize() for w in kw.split())
    prompt = build_prompt(kw, svc_name, city, svc)
    raw = call_zen(prompt, zen_key)
    if not raw:
        return None
    
    content = clean_html(raw)
    if not content.startswith("<h2>"):
        content = f"<h2>{title}</h2>\n" + content
    
    excerpt = re.sub(r'<[^>]+>', ' ', content).strip()
    excerpt = re.sub(r'\s+', ' ', excerpt)[:180] + "..."
    words = len(content.split())
    now = datetime.now()
    
    return {
        "slug": slug, "title": title, "excerpt": excerpt, "content": content,
        "date": now.strftime("%d %b %Y"), "iso_date": now.isoformat(),
        "category": "strategy",
        "readTime": f"{max(2, round(words/200))} min",
        "tags": [w for w in kw.lower().split() if len(w) > 3][:5],
        "featured": False, "generated": True, "service": svc,
        "city": city or None, "liveUrl": None,
        "publish_date": now.strftime("%d %b %Y"), "source": "bulk_generate",
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, default=20)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS)
    args = parser.parse_args()
    
    zen_key = read_zen_key()
    live_slugs = load_live_slugs()
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    
    processed = set()
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            processed = set(json.load(f).get("processed_slugs", []))
        print(f"Progress file found: {len(processed)} already processed")
        if not args.resume:
            print("  (use --resume to continue; running fresh will overwrite)")
    
    queue = json.load(open(QUEUE))
    pending = [x for x in queue if x.get("status") == "pending" and not x.get("has_post")]
    print(f"Queue: {len(queue)} total, {len(pending)} pending, {len(live_slugs)} live slugs")
    
    pending = [x for x in pending if x.get("slug") not in processed and x.get("slug") not in live_slugs]
    if args.limit > 0:
        pending = pending[:args.limit]
    
    print(f"To generate: {len(pending)} articles")
    if not pending:
        print("Nothing to generate. Done.")
        return
    
    total_gen = 0
    batch_num = 0
    t_start = time.time()
    consecutive_errors = 0
    
    for start in range(0, len(pending), args.batch):
        batch = pending[start:start+args.batch]
        batch_num += 1
        results = []
        err_count = 0
        
        print(f"\nBatch {batch_num}/{len(pending)//args.batch+1}: {len(batch)} articles...")
        t0 = time.time()
        
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            fut_map = {ex.submit(make_article, item, zen_key, live_slugs): item for item in batch}
            for fut in as_completed(fut_map):
                item = fut_map[fut]
                slug = item.get("slug", "?")
                kw = item.get("keyword", slug)
                try:
                    post = fut.result()
                    if post:
                        results.append(post)
                        processed.add(slug)
                        item["status"] = "generated"
                        item["has_post"] = True
                        item["generated_at"] = datetime.now().isoformat()
                    else:
                        if slug in live_slugs:
                            # duplicate — mark as processed silently
                            processed.add(slug)
                            item["status"] = "generated"
                            item["has_post"] = True
                        else:
                            err_count += 1
                            log_err(kw, slug, "API gagal atau konten terlalu pendek (None)")
                except Exception as e:
                    err_count += 1
                    log_err(kw, slug, f"exception: {str(e)[:200]}")
        
        elapsed = time.time() - t0
        total_gen += len(results)
        err_rate = err_count / len(batch) if batch else 0
        
        # Save batch file
        if results:
            batch_file = os.path.join(DRAFTS_DIR, f"batch_{batch_num:04d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(batch_file, "w") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
        
        rate = total_gen / max(time.time() - t_start, 1) * 3600
        eta_h = max(0, (len(pending) - start - len(batch))) / max(rate, 1) * 3600
        print(f"  → {len(results)} ok, {err_count} fail ({elapsed:.0f}s, {rate:.0f}/hr, ETA ~{eta_h/3600:.1f}h)")
        
        # Save progress every batch
        with open(PROGRESS_FILE, "w") as f:
            json.dump({"processed_slugs": list(processed), "last_run": datetime.now().isoformat()}, f)
        
        # Save queue every 10 batches (reduce disk I/O)
        if batch_num % 10 == 0:
            json.dump(queue, open(QUEUE, "w"), ensure_ascii=False, indent=2)
        
        # Backoff: if >50% errors, slow down
        if err_rate > 0.5:
            consecutive_errors += 1
            backoff = min(consecutive_errors * 10, 120)
            print(f"  ⏳ High error rate ({err_rate:.0%}), backing off {backoff}s...")
            time.sleep(backoff)
        else:
            consecutive_errors = 0
            if start + args.batch < len(pending):
                time.sleep(2)
    
    elapsed_total = time.time() - t_start
    print(f"\n{'='*50}")
    print(f"Complete: {total_gen} articles in {elapsed_total/3600:.1f}h")
    print(f"Speed: {total_gen/elapsed_total*3600:.0f}/hr")
    print(f"Drafts: {DRAFTS_DIR}/")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()