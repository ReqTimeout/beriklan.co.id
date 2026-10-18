#!/usr/bin/env python3
"""
gen_seed_chunks_my_v2.py — F3c: select top-N expansion keywords and emit chunked
SQL files for D1 (beriklan-my-seo).

Selection:
  - Only NEW expansion entries (source ~ ^expansion_[lw]) — the original 5,863
    mined rows are already in D1 and must not be touched (avoid resetting status).
  - Per-service quota so all 16 services are represented; live-viewer services
    get priority weighting (differentiator). Within a service: highest
    priority_score first, tie-break: transactional > commercial > others.

Output: scripts/db/chunks_my_v2/chunk_NN.sql
  - 1000 rows per file, split into INSERT OR REPLACE statements of 50 rows each
    (~33 KB/statement) to stay under D1's SQLITE_TOOBIG limit.
"""
import json
import os
import re

ROOT = os.path.expanduser("~/Desktop/beriklan.my")
QUEUE_PATH = os.path.join(ROOT, "web/src/data/keyword-queue.json")
OUT_DIR = os.path.join(ROOT, "scripts/db/chunks_my_v2")

TOTAL_TARGET = 30000
LIVE_QUOTA = 1200      # per live-viewer service (6 services -> 7,200 if available)
INTENT_RANK = {"transactional": 0, "commercial": 1, "comparison": 2, "informational": 3}


def esc(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v).replace("\\", "\\\\").replace("'", "''")
    return f"'{s}'"


def make_id(k, i):
    base = k["keyword_normalized"][:40].replace(" ", "_").replace("-", "_")
    safe = "".join(ch for ch in base if ch.isalnum() or ch == "_")
    return f"kwx_{safe}_{i}"


def main():
    queue = json.load(open(QUEUE_PATH))
    new = [k for k in queue if re.match(r"^expansion_[lw]", k.get("source") or "")]
    print(f"Queue total: {len(queue)} | expansion pool: {len(new)}")

    by_service = {}
    for k in new:
        by_service.setdefault(k["service"], []).append(k)

    def sort_key(k):
        return (-int(k.get("priority_score") or 0), INTENT_RANK.get(k.get("intent"), 4))

    live = [s for s in by_service if s.endswith("live-viewers") or s == "live-stream-viewers"]
    agency = [s for s in by_service if s not in live]

    selected = []
    # live-viewer quota first
    for s in live:
        pool = sorted(by_service[s], key=sort_key)
        selected.extend(pool[:LIVE_QUOTA])
    # split the remainder evenly across agency services
    remaining = TOTAL_TARGET - len(selected)
    per_agency = remaining // len(agency)
    leftovers = []
    for s in agency:
        pool = sorted(by_service[s], key=sort_key)
        selected.extend(pool[:per_agency])
        leftovers.extend(pool[per_agency:per_agency + 2000])
    # top up to target from leftovers by global score
    gap = TOTAL_TARGET - len(selected)
    if gap > 0:
        selected.extend(sorted(leftovers, key=sort_key)[:gap])

    print(f"Selected for seeding: {len(selected)}")
    from collections import Counter
    for s, c in Counter(x["service"] for x in selected).most_common():
        print(f"  {s}: {c}")
    print("By language:", dict(Counter(x.get("language") for x in selected)))

    # ---- emit SQL ----
    header = (
        "INSERT OR REPLACE INTO keyword_queue "
        "(id, keyword, keyword_normalized, source, seed, discovered_at, status, "
        "priority_score, intent, service, city, estimated_volume, rank_match_profile) VALUES\n"
    )
    rows = []
    for i, k in enumerate(selected):
        rows.append("(" + ",".join([
            esc(make_id(k, i)),
            esc(k["keyword"]),
            esc(k["keyword_normalized"]),
            esc(k.get("source")),
            esc(k.get("keyword", "")[:50]),
            esc(k.get("created_at")),
            esc(k.get("status") or "pending"),
            str(k.get("priority_score") or 50),
            esc(k.get("intent")),
            esc(k.get("service")),
            esc(k.get("city")),
            "NULL",
            esc(json.dumps(k, ensure_ascii=False)),
        ]) + ")")

    os.makedirs(OUT_DIR, exist_ok=True)
    for old in os.listdir(OUT_DIR):
        if old.startswith("chunk_") and old.endswith(".sql"):
            os.remove(os.path.join(OUT_DIR, old))

    CHUNK_SIZE = 1000
    STMT_ROWS = 50
    n_files = 0
    for i in range(0, len(rows), CHUNK_SIZE):
        group = rows[i:i + CHUNK_SIZE]
        stmts = []
        for j in range(0, len(group), STMT_ROWS):
            stmts.append(header + ",\n".join(group[j:j + STMT_ROWS]) + ";")
        n_files += 1
        p = os.path.join(OUT_DIR, f"chunk_{n_files:03d}.sql")
        with open(p, "w") as f:
            f.write("\n".join(stmts))
    sizes = [os.path.getsize(os.path.join(OUT_DIR, f)) for f in sorted(os.listdir(OUT_DIR))]
    print(f"\n{n_files} chunk files -> {OUT_DIR} (max file {max(sizes):,} B)")


if __name__ == "__main__":
    main()
