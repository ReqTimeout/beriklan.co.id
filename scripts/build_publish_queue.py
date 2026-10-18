#!/usr/bin/env python3
"""
build_publish_queue.py — Build the FINAL publish queue (NO-LLM) ready for D1.

Strategy (per locked plan):
  - Tier A: existing high-quality LLM drafts (drafts/batch_0*.json) preserved AS-IS,
            published FIRST (best variety up front).
  - Tier B: ALL remaining keywords from keyword-queue.json re-rendered deterministically
            via article_render (fixes empty-city bug + high variety, no duplicates).
  - Skips anything already live (web/src/data/posts.json).
  - Every record passes qc(); failures are logged & excluded.
  - Dates are LEFT BLANK on purpose — the Worker stamps WIB at actual publish moment
    (fixes the future-date bug). Each record carries publish_rank for ordering.

Output: drafts_patched/queue_*.ndjson  +  drafts_patched/manifest.json

Usage:
  python3 scripts/build_publish_queue.py [--limit N] [--shard-size 5000]
"""
import os, sys, json, glob, argparse
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import article_render as AR
from article_render import render_article, qc, detect_city, detect_service, sanitize_content

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "web" / "src" / "data"
DRAFTS = ROOT / "drafts"
OUT = ROOT / "drafts_patched"


def load_live_slugs():
    try:
        posts = json.load(open(DATA / "posts.json", encoding="utf-8"))
        return {p.get("slug") for p in posts if p.get("slug")}
    except Exception:
        return set()


def enrich_tier_a(a):
    """Ensure a good LLM draft has the full publish schema; keep its content."""
    slug = a.get("slug", "")
    kw = a.get("keyword") or a.get("title") or slug.replace("-", " ")
    if not a.get("service"):
        a["service"] = detect_service(slug, kw).get("slug", "jasa-digital-marketing")
    if not a.get("city"):
        c = detect_city(slug, kw)
        a["city"] = c.get("slug") if c else ""
    if not a.get("tags"):
        a["tags"] = [t for t in [a["service"].replace("jasa-", ""), a.get("city"), "jasa-iklan"] if t]
    a.setdefault("category", "strategy")
    if not a.get("word_count"):
        import re
        a["word_count"] = len(re.findall(r"\w+", re.sub(r"<[^>]+>", " ", a.get("content", ""))))
    # blank dates -> worker stamps at publish
    a["date"] = ""
    a["iso_date"] = ""
    a["status"] = "pending"
    a["tier"] = "A"
    return a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="cap total records (0=all)")
    ap.add_argument("--shard-size", type=int, default=5000)
    args = ap.parse_args()

    OUT.mkdir(exist_ok=True)
    live = load_live_slugs()
    print(f"Live slugs: {len(live)}", flush=True)

    seen = set(live)
    tier_a = []
    for f in sorted(glob.glob(str(DRAFTS / "batch_0*.json"))):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        arts = d.get("articles", d) if isinstance(d, dict) else d
        for a in arts:
            sg = a.get("slug")
            if not sg or sg in seen:
                continue
            seen.add(sg)
            tier_a.append(enrich_tier_a(dict(a)))
    print(f"Tier A (good LLM): {len(tier_a)}", flush=True)

    # Tier B ordering list from keyword-queue (light)
    queue = json.load(open(DATA / "keyword-queue.json", encoding="utf-8"))
    tier_b = []
    for e in queue:
        sg = e.get("slug")
        if not sg or sg in seen:
            continue
        seen.add(sg)
        tier_b.append((sg, e.get("keyword") or sg.replace("-", " "),
                       e.get("service"), int(e.get("priority_score") or 0)))
    tier_b.sort(key=lambda x: x[3], reverse=True)
    print(f"Tier B (to re-render): {len(tier_b)}", flush=True)

    # write shards
    total_target = len(tier_a) + len(tier_b)
    if args.limit:
        total_target = min(total_target, args.limit)

    rank = 0
    written = 0
    qc_fail = Counter()
    shard_idx = 0
    shard = []
    shard_files = []

    def flush_shard():
        nonlocal shard_idx, shard
        if not shard:
            return
        fn = OUT / f"queue_{shard_idx:05d}.ndjson"
        with open(fn, "w", encoding="utf-8") as fh:
            for rec in shard:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        shard_files.append(fn.name)
        shard_idx += 1
        shard = []

    def emit(rec):
        nonlocal rank, written, shard
        # sanitize: strip full-document wrappers / scripts / H1 to keep set:html safe
        if rec.get("content"):
            import re as _re
            rec["content"] = sanitize_content(rec["content"])
            rec["word_count"] = len(_re.findall(r"\w+", _re.sub(r"<[^>]+>", " ", rec["content"])))
        ok, reason = qc(rec)
        if not ok:
            qc_fail[reason] += 1
            return
        rec["publish_rank"] = rank
        rank += 1
        shard.append(rec)
        written += 1
        if len(shard) >= args.shard_size:
            flush_shard()

    # Tier A first
    for a in tier_a:
        if args.limit and written >= args.limit:
            break
        emit(a)

    # Tier B
    for sg, kw, svc, _pri in tier_b:
        if args.limit and written >= args.limit:
            break
        rec = render_article(sg, kw, service={"slug": svc} if svc else None)
        rec["date"] = ""
        rec["iso_date"] = ""
        rec["status"] = "pending"
        rec["tier"] = "B"
        emit(rec)

    flush_shard()

    manifest = {
        "generated_by": "build_publish_queue.py",
        "live_existing": len(live),
        "tier_a": len(tier_a),
        "tier_b_candidates": len(tier_b),
        "written": written,
        "qc_failed": sum(qc_fail.values()),
        "qc_fail_reasons": dict(qc_fail),
        "shards": shard_files,
        "shard_size": args.shard_size,
    }
    json.dump(manifest, open(OUT / "manifest.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(json.dumps(manifest, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
