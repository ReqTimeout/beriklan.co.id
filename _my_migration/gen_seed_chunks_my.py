#!/usr/bin/env python3
"""Generate per-chunk SQL INSERT files to seed the Malaysian keyword queue into
Cloudflare D1 (beriklan-my-seo) via Wrangler file mode.

Unlike the .co.id version (which reads the legacy `keywords.json`), this reads the
mined `keyword-queue.json` (queue schema: keyword, keyword_normalized, slug,
priority_score, source, status, service, city, industry, intent, language,
country, created_at ...) produced by scripts/keyword_miner.py.

Target table: keyword_queue (see scripts/db/schema.sql). The full original record
is preserved in `rank_match_profile` as JSON so `language`/`country`/`industry`/
`slug` survive the round-trip even though they have no dedicated column.
"""
import json
import os
from pathlib import Path

# ROOT-aware: runnable from _my_migration/ (dev copy) or scripts/db/ (shipped copy)
_here = Path(__file__).resolve().parent
if _here.name == "_my_migration":
    ROOT = Path(os.path.expanduser("~/Desktop/beriklan.my"))
else:
    # shipped location: scripts/db/gen_seed_chunks.py -> ROOT is two levels up
    ROOT = _here.parent.parent

QUEUE = json.loads((ROOT / "web/src/data/keyword-queue.json").read_text())
OUT_DIR = ROOT / "scripts/db/chunks_my"
OUT_DIR.mkdir(exist_ok=True)


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
    # keep it filesystem/SQL-safe and unique via row index suffix
    safe = "".join(ch for ch in base if ch.isalnum() or ch == "_")
    return f"kw_{safe}_{i}"


def main():
    values_list = []
    seen_ids = set()
    for i, k in enumerate(QUEUE):
        kid = make_id(k, i)
        assert kid not in seen_ids, f"duplicate id {kid}"
        seen_ids.add(kid)
        row = "(" + ",".join([
            esc(kid),                                  # id (TEXT PK)
            esc(k["keyword"]),                         # keyword (UNIQUE)
            esc(k["keyword_normalized"]),              # keyword_normalized
            esc(k.get("source")),                      # source
            esc(k.get("keyword", "")[:50]),            # seed
            esc(k.get("created_at") or "2026-07-30T00:00:00Z"),  # discovered_at
            esc(k.get("status") or "pending"),         # status
            str(k.get("priority_score") or 50),        # priority_score
            esc(k.get("intent")),                      # intent
            esc(k.get("service")),                     # service
            esc(k.get("city")),                        # city
            "NULL",                                    # estimated_volume (unknown)
            esc(json.dumps(k, ensure_ascii=False)),    # rank_match_profile = full record
        ]) + ")"
        values_list.append(row)

    # Each file groups CHUNK_SIZE rows, but the rows are split into multiple INSERT
    # statements of STMT_ROWS each so no single statement trips D1's SQLITE_TOOBIG
    # limit (our rows embed the full record as JSON, ~650 bytes/row).
    CHUNK_SIZE = 200
    STMT_ROWS = 50
    header = (
        "INSERT OR REPLACE INTO keyword_queue "
        "(id, keyword, keyword_normalized, source, seed, discovered_at, status, "
        "priority_score, intent, service, city, estimated_volume, rank_match_profile) VALUES\n"
    )
    chunks = []
    for i in range(0, len(values_list), CHUNK_SIZE):
        group = values_list[i:i + CHUNK_SIZE]
        stmts = []
        for j in range(0, len(group), STMT_ROWS):
            stmts.append(header + ",\n".join(group[j:j + STMT_ROWS]) + ";")
        chunks.append("\n".join(stmts))

    # clear any stale chunks from a previous run
    for old in OUT_DIR.glob("chunk_*.sql"):
        old.unlink()

    for i, c in enumerate(chunks, 1):
        f = OUT_DIR / f"chunk_{i:02d}.sql"
        f.write_text(c)
        rows = len(values_list[(i - 1) * CHUNK_SIZE:i * CHUNK_SIZE])
        print(f"  {f.name}: {len(c):,} bytes, {rows} rows")

    print(f"\nTotal: {len(chunks)} chunks for {len(values_list)} keywords -> {OUT_DIR}")


if __name__ == "__main__":
    main()
