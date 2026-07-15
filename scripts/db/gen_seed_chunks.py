#!/usr/bin/env python3
"""Generate per-chunk SQL INSERT files untuk seed keywords ke D1 via Wrangler file mode."""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
KEYWORDS = json.loads((ROOT / "src/data/keywords.json").read_text())
OUT_DIR = Path(__file__).parent / "chunks"
OUT_DIR.mkdir(exist_ok=True)

def esc(v):
    if v is None: return "NULL"
    if isinstance(v, (int, float)): return str(v)
    s = str(v).replace("\\", "\\\\").replace("'", "''")
    return f"'{s}'"

def main():
    values_list = []
    for i, k in enumerate(KEYWORDS):
        kid = f"kw_{k['keyword_normalized'][:30].replace(' ', '_').replace('-', '_')}_{i}"
        row = "(" + ",".join([
            esc(kid),
            esc(k["keyword"]),
            esc(k["keyword_normalized"]),
            esc(k.get("source")),
            esc(k.get("keyword", "")[:50]),
            esc("2026-07-14T00:00:00Z"),
            esc("pending"),
            str(k.get("priority_score") or 50),
            esc(k.get("intent")),
            esc(k.get("service")),
            esc(k.get("city")),
            str(k.get("estimated_volume")) if k.get("estimated_volume") is not None else "NULL",
            esc(json.dumps(k) if k else None),
        ]) + ")"
        values_list.append(row)

    chunk_size = 200
    chunks = []
    for i in range(0, len(values_list), chunk_size):
        chunk_sql = (
            "INSERT OR REPLACE INTO keyword_queue "
            "(id, keyword, keyword_normalized, source, seed, discovered_at, status, priority_score, intent, service, city, estimated_volume, rank_match_profile) VALUES\n"
            + ",\n".join(values_list[i:i+chunk_size]) + ";"
        )
        chunks.append(chunk_sql)

    for i, c in enumerate(chunks, 1):
        f = OUT_DIR / f"chunk_{i:02d}.sql"
        f.write_text(c)
        print(f"  {f.name}: {len(c):,} bytes, {len(values_list[(i-1)*chunk_size:i*chunk_size])} rows")

    print(f"\nTotal: {len(chunks)} chunks for {len(values_list)} keywords")

if __name__ == "__main__":
    main()
