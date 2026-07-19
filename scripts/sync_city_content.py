#!/usr/bin/env python3
"""
Sync D1 city_content → src/data/city-content.json
Used by the merge loop after enrichment completes.

Usage:
  python3 scripts/sync_city_content.py
"""
import json
import os
import subprocess
import sys

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(WEB, "src/data/city-content.json")


def d1_query(sql):
    r = subprocess.run(
        ["npx", "wrangler", "d1", "execute", "beriklan-seo", "--remote", "--command", sql],
        cwd=WEB, capture_output=True, text=True,
    )
    return r.stdout


def d1_json(sql):
    out = d1_query(sql)
    s = out.find("[")
    e = out.rfind("]")
    if s == -1 or e == -1:
        return []
    try:
        arr = json.loads(out[s:e+1])
        return arr[0].get("results", []) if isinstance(arr, list) and arr else []
    except Exception:
        return []


def main():
    rows = d1_json("SELECT route, content FROM city_content")
    if not rows:
        print("No D1 city_content rows.")
        return
    content = {}
    if os.path.exists(CONTENT):
        content = json.load(open(CONTENT))
    for r in rows:
        content[r["route"]] = r["content"]
    json.dump(content, open(CONTENT, "w"), ensure_ascii=False, indent=1)
    print(f"Synced {len(rows)} D1 rows → {CONTENT} (total {len(content)} entries)")


if __name__ == "__main__":
    main()
