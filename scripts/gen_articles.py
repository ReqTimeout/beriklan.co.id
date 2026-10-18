#!/usr/bin/env python3
"""Batch article generator from keyword queue — no external API.
Replaces placeholder keywords with unique article content per slug.
CTA uses "Hubungi kami" (no "hubungi kami untuk konsultasi").
"""
import os, sys, json, re, argparse
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/Users/maabook/Desktop/beriklan.co.id")
QUEUE = ROOT / "web/src/data/keyword-queue.json"
LIVE = ROOT / "web/src/data/posts.json"
DRAFT_DIR = ROOT / "drafts"
PROGRESS = DRAFT_DIR / "_progress_direct.json"

CTA = "Hubungi kami via WhatsApp <a href=\"https://wa.me/62811919328\" target=\"_blank\" rel=\"noopener noreferrer\">WhatsApp Beriklan</a>"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from article_render import render_article

def article_for(kw_entry):
    """Delegate to the shared NO-LLM renderer (fixes empty-city bug + variety)."""
    svc = kw_entry.get("service")
    return render_article(
        kw_entry.get("slug", ""),
        kw_entry.get("keyword", ""),
        service={"slug": svc} if svc else None,
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, default=24)
    args = parser.parse_args()

    q = json.load(open(QUEUE))
    if isinstance(q, dict) and "keywords" in q: q = q["keywords"]
    elif isinstance(q, dict): q = [{"keyword": k, **v} for k, v in q.items()]

    live_slugs = set()
    if LIVE.exists():
        lv = json.load(open(LIVE))
        if isinstance(lv, list): live_slugs = {p.get("slug") for p in lv if p.get("slug")}

    done = set()
    if PROGRESS.exists(): done = set(json.load(open(PROGRESS)).get("slugs", []))

    pending = [k for k in q if k.get("slug") and k.get("status") in ("pending", None, "") and not k.get("has_post") and k["slug"] not in live_slugs and k["slug"] not in done]
    print(f"Queue:{len(q)} Live:{len(live_slugs)} Done:{len(done)} Pending:{len(pending)}", flush=True)
    if not pending: print("All done!", flush=True); return

    DRAFT_DIR.mkdir(exist_ok=True)
    batch = pending[:args.batch]
    results = []
    for k in batch:
        try:
            art = article_for(k)
            results.append(art); done.add(k["slug"])
        except Exception as e:
            open("/tmp/gen_articles_err.log", "a").write(f"{k.get('slug')}: {e}\n")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bf = DRAFT_DIR / f"batch_direct_{ts}.json"
    json.dump({"batch": "direct_v1", "timestamp": ts, "count": len(results), "articles": results}, open(bf, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"slugs": list(done), "updated": datetime.now(timezone.utc).isoformat()}, open(PROGRESS, "w"), ensure_ascii=False, indent=2)

    for a in results: print(f"  {a['slug']} ({a['word_count']}w)", flush=True)
    print(f"Batch saved: {len(results)} -> {bf.name}. Total done: {len(done)}.", flush=True)

if __name__ == "__main__": main()