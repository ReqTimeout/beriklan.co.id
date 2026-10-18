#!/usr/bin/env python3
"""
bulk_generate_or.py — Bulk article generator using OpenRouter free models.

Generates Indonesian SEO articles from keyword queue using OpenRouter free models
(primarily nvidia/nemotron-3-ultra-550b-a55b:free).

Usage:
  python3 scripts/bulk_generate_or.py --batch 24 --workers 4
"""
import os, sys, json, time, argparse, urllib.request, urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from datetime import datetime

# Config
KEY = open(os.path.expanduser("~/.beriklan/openrouter-key")).read().strip()
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
ROOT = Path("/Users/maabook/Desktop/beriklan.co.id")
QUEUE_FILE = ROOT / "web/src/data/keyword-queue.json"
LIVE_FILE = ROOT / "web/src/data/posts.json"
DRAFT_DIR = ROOT / "drafts"
PROGRESS_FILE = DRAFT_DIR / "_progress.json"
ERR_LOG = "/tmp/bulk_generate_or_err.log"

MODELS = ["nvidia/nemotron-3-ultra-550b-a55b:free"]

# Compressed Indonesian SEO article prompt
PROMPT_TMPL = '''Anda copywriter SEO senior Indonesia. Tulis artikel HTML 400-500 kata untuk keyword: "{kw}".

ATURAN:
- 1 H1 (variasi, BUKAN copy paste keyword), 4-6 H2, 2-3 H3, 1-2 bullet list, 1 tabel markdown OK
- 2 link internal ke https://beriklan.co.id/ (pakai <a href>), 1 link eksternal nofollow
- Bahasa Indonesia formal marketing pro, "Anda", kalimat aktif, paragraf 2-4 kalimat
- Akhiri dengan CTA WhatsApp https://wa.me/62811919328
- HTML valid, tanpa emoji, tanpa <html>/<body>, langsung <h1>...<p>...
- Hindari: "gak", "bikin", "pasti untung", "garansi", "100%"

OUTPUT: hanya HTML, tidak ada penjelasan.'''

# Globals for progress tracking
progress_lock = Lock()
processed_slugs = set()
queue = []
batch_num = 0
total_done = 0
total_fail = 0
model_stats = {m: {"ok": 0, "fail": 0, "lockout_until": 0} for m in MODELS}
model_lock = Lock()

def load_progress():
    """Load processed slugs from progress file."""
    global processed_slugs
    if PROGRESS_FILE.exists():
        try:
            d = json.load(open(PROGRESS_FILE))
            processed_slugs = set(d.get("processed_slugs", []))
            print(f"Resumed: {len(processed_slugs)} already processed")
        except: pass

def save_progress():
    """Save progress atomically."""
    PROGRESS_FILE.parent.mkdir(exist_ok=True)
    tmp = PROGRESS_FILE.with_suffix(".tmp")
    with progress_lock:
        json.dump({
            "processed_slugs": list(processed_slugs),
            "total_done": total_done,
            "total_fail": total_fail,
            "updated": datetime.now().isoformat()
        }, open(tmp, "w"))
    tmp.replace(PROGRESS_FILE)

def get_model():
    """Get a model that is not in lockout."""
    now = time.time()
    with model_lock:
        for m in MODELS:
            if model_stats[m]["lockout_until"] < now:
                return m
    return None

def lockout_model(model, seconds=15):
    with model_lock:
        model_stats[model]["lockout_until"] = time.time() + seconds

def log_err(msg):
    with open(ERR_LOG, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def call_model(model, prompt, max_retries=3):
    """Call model, return (success, content, error_msg, time)."""
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000,
        "temperature": 0.7,
        "stream": False,
    }).encode()
    req = urllib.request.Request(ENDPOINT, data=body, headers={
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "HTTP-Referer": "https://beriklan.co.id",
    })

    for attempt in range(max_retries):
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.loads(r.read())
            dt = time.time() - t0
            if "error" in d:
                err = d["error"]
                err_code = err.get("code")
                if err_code == 429 or "rate" in str(err).lower():
                    with model_lock:
                        model_stats[model]["fail"] += 1
                    return False, None, f"429 rate limit", dt
                return False, None, f"{err_code}: {err.get('message', '')[:200]}", dt
            choice = d.get("choices", [{}])[0]
            content = (choice.get("message", {}).get("content") or "").strip()
            if not content or len(content) < 300:
                return False, None, f"content too short ({len(content)} chars)", dt
            with model_lock:
                model_stats[model]["ok"] += 1
            return True, content, None, dt
        except urllib.error.HTTPError as e:
            dt = time.time() - t0
            if e.code == 429:
                with model_lock:
                    model_stats[model]["fail"] += 1
                time.sleep(2 + attempt * 3)
                continue
            try: body_text = e.read().decode()[:200]
            except: body_text = str(e)
            return False, None, f"HTTP {e.code}: {body_text}", dt
        except Exception as e:
            dt = time.time() - t0
            time.sleep(1)
            if attempt == max_retries - 1:
                return False, None, f"Exception: {e}", dt
    return False, None, "max retries", 0

def process_keyword(kw_entry, retries=2):
    """Process one keyword, return (success, slug, html, error)."""
    slug = kw_entry["slug"]
    prompt = PROMPT_TMPL.format(kw=kw_entry["keyword"])
    last_err = None
    for attempt in range(retries):
        model = get_model()
        if not model:
            time.sleep(2)
            continue
        ok, content, err, dt = call_model(model, prompt)
        if ok:
            return True, slug, content, model
        last_err = err
        if "429" in str(err) or "rate" in str(err).lower():
            lockout_model(model, 15)
            time.sleep(1)
    return False, slug, None, f"{last_err} after {retries} retries"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, default=24, help="Batch size per output file")
    parser.add_argument("--workers", type=int, default=4, help="Parallel workers")
    args = parser.parse_args()

    # Load queue
    print(f"Loading queue from {QUEUE_FILE}...")
    data = json.load(open(QUEUE_FILE))
    if isinstance(data, dict) and "keywords" in data:
        data = data["keywords"]
    elif isinstance(data, dict):
        # Old format: dict of slug -> data
        data = [{"slug": k, **v} for k, v in data.items()]
    print(f"Queue: {len(data)} entries")

    # Load live posts for dedup
    live_slugs = set()
    if LIVE_FILE.exists():
        live = json.load(open(LIVE_FILE))
        if isinstance(live, list):
            live_slugs = {p.get("slug") for p in live if p.get("slug")}
        print(f"Live posts: {len(live_slugs)} (will skip)")

    # Load progress
    load_progress()

    # Filter queue: must be pending + no existing post + not in live posts + not already processed
    todo = [
        k for k in data
        if k.get("slug")
        and k.get("status") in ("pending", None, "")
        and not k.get("has_post")
        and k["slug"] not in live_slugs
        and k["slug"] not in processed_slugs
    ]
    print(f"Todo: {len(todo)} keywords", flush=True)
    if not todo:
        print("Nothing to do!")
        return

    DRAFT_DIR.mkdir(exist_ok=True)
    global batch_num, total_done, total_fail

    # Stats tracking
    t_start = time.time()
    last_save = t_start
    save_interval = 30  # save every 30 seconds

    def worker(kw):
        return process_keyword(kw)

    # Process in batches
    i = 0
    while i < len(todo):
        # Get next batch
        batch = todo[i:i + args.batch]
        i += args.batch
        batch_num += 1

        t_batch = time.time()
        results = []
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = {ex.submit(worker, kw): kw for kw in batch}
            for f in as_completed(futures):
                kw = futures[f]
                try:
                    ok, slug, html, info = f.result()
                    results.append({"kw": kw, "ok": ok, "slug": slug, "html": html, "info": info})
                except Exception as e:
                    results.append({"kw": kw, "ok": False, "error": str(e)})

        # Save successful articles
        success_articles = []
        for r in results:
            if r["ok"]:
                kw = r["kw"]
                article = {
                    "slug": r["slug"],
                    "title": kw.get("title") or r["slug"].replace("-", " ").title(),
                    "keyword": kw.get("keyword", r["slug"]),
                    "content": r["html"],
                    "category": kw.get("category", "strategy"),
                    "tags": kw.get("tags", []),
                    "generated_at": datetime.now().isoformat(),
                    "model": r.get("info", "?"),
                }
                success_articles.append(article)
                processed_slugs.add(r["slug"])
                with progress_lock:
                    global total_done
                    total_done += 1
            else:
                log_err(f"{r['slug']}: {r.get('info', r.get('error', 'unknown'))}")
                with progress_lock:
                    global total_fail
                    total_fail += 1

        # Write batch file
        if success_articles:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            batch_file = DRAFT_DIR / f"batch_{batch_num:04d}_{ts}.json"
            json.dump({
                "batch": batch_num,
                "timestamp": ts,
                "count": len(success_articles),
                "articles": success_articles
            }, open(batch_file, "w"), ensure_ascii=False, indent=2)

        # Save progress
        if time.time() - last_save > save_interval:
            save_progress()
            last_save = time.time()

        # Stats
        dt = time.time() - t_batch
        rate = len(batch) / dt if dt > 0 else 0
        eta_h = (len(todo) - i) / (total_done / max(1, time.time() - t_start) * 3600) if total_done > 0 else 0
        total = total_done + total_fail
        print(f"Batch {batch_num}: {len(success_articles)} ok, {len(batch) - len(success_articles)} fail | {rate:.1f}/s | total done: {total_done} fail: {total_fail} ({total/len(todo)*100:.1f}%) | ETA: {eta_h:.1f}h", flush=True)

    # Final save
    save_progress()
    print(f"\nDone! {total_done} articles generated, {total_fail} failed")

if __name__ == "__main__":
    main()