#!/usr/bin/env python3
"""
§T4 / Fase 6.2 — muat file hasil validate_suggest.py ke antrian produksi lewat
endpoint YANG SUDAH ADA: POST /api/admin/keywords/import?token=…&source=…

Kenapa lewat endpoint dan bukan `wrangler d1 execute` langsung:
  `handleAdminKeywordsImport` (web/src/worker-entry.js:1517) sudah menjamin dedupe
  (`WHERE keyword = ? OR keyword_normalized = ?`) dan mengisi `id`, `seed`,
  `discovered_at`, `status='pending'` secara konsisten dengan baris antrian lain.
  Menyuntik D1 manual berarti membuat jalur kedua (dilarang plan §T4 langkah 3).

Kenapa di-chunk:
  endpoint memuat `?token=` dari URL dan menulis 1 baris dengan 2 panggilan D1
  berurutan (SELECT dedupe + INSERT). 49 baris sekaligus = ~98 subrequest +
  overhead dalam SATU invocation worker → risiko kena batas 128 subrequest dan
  meninggalkan antrian setengah terisi. Chunk 12 = ~26 subrequest, aman.

Token TIDAK pernah dicetak. Ambil dari env ADMIN_TOKEN (di-set oleh shell dari
.env.admin, lihat header cara pakai di bawah).

Pemakaian:
    TOK=$(grep '^ADMIN_TOKEN=' .env.admin | cut -d= -f2 | tr -d ' \r\n"')
    ADMIN_TOKEN="$TOK" python3 scripts/import_wave1.py --dry
    ADMIN_TOKEN="$TOK" python3 scripts/import_wave1.py --file src/data/industry-wave1.import.json
    ADMIN_TOKEN="$TOK" python3 scripts/import_wave1.py --file src/data/industry-wave1.import.with-derivatives.json
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = os.environ.get("BERIKLAN_BASE", "https://beriklan.co.id")
DEFAULT_SOURCE = "industry-wave1"
# Cloudflare WAF memblokir UA default urllib (HTTP 403 "error code: 1010") — diukur
# 30 Sep: `curl` boleh lewat (dapat 401 dari worker), python urllib tidak.
# Jadi kirim UA yang sama seperti tool CLI.
UA = "curl/8.7.1"


def post_chunk(base, token, source, items, timeout=90):
    url = f"{base}/api/admin/keywords/import?token={urllib.parse.quote(token)}&source={urllib.parse.quote(source)}"
    body = json.dumps({"keywords": items}).encode()
    req = urllib.request.Request(url, data=body, method="POST",
                                headers={"Content-Type": "application/json", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=str(ROOT / "src" / "data" / "industry-wave1.import.json"))
    ap.add_argument("--source", default=DEFAULT_SOURCE)
    ap.add_argument("--chunk", type=int, default=12)
    ap.add_argument("--dry", action="store_true", help="cetak rencana saja, tanpa network")
    args = ap.parse_args()

    token = os.environ.get("ADMIN_TOKEN", "").strip()
    if not token and not args.dry:
        print("ADMIN_TOKEN kosong — set dari .env.admin dulu (lihat docstring).", file=sys.stderr)
        return 2

    payload = json.loads(Path(args.file).read_text())
    items = payload["keywords"] if isinstance(payload, dict) else payload
    prio = [i.get("priority", 0) for i in items]
    print(f"file={Path(args.file).name} items={len(items)} prio={min(prio)}–{max(prio)} "
          f"source={args.source} base={BASE} chunk={args.chunk}")
    if args.dry:
        for i, it in enumerate(items, 1):
            print(f"  {i:>3}. {it['priority']} {it['intent']:14s} {it['service']:28s} {it['keyword']}")
        return 0

    total_ins = total_skip = 0
    for start in range(0, len(items), args.chunk):
        chunk = items[start:start + args.chunk]
        try:
            res = post_chunk(BASE, token, args.source, chunk)
        except urllib.error.HTTPError as e:
            print(f"  chunk {start//args.chunk + 1}: HTTP {e.code} {e.read().decode()[:200]}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"  chunk {start//args.chunk + 1}: {str(e)[:200]}", file=sys.stderr)
            return 1
        total_ins += res.get("inserted", 0)
        total_skip += res.get("skipped", 0)
        errs = res.get("sample_errors") or []
        print(f"  chunk {start//args.chunk + 1:>2} ({len(chunk):>2}) → inserted={res.get('inserted')} "
              f"skipped={res.get('skipped')}" + (f" errors={errs}" if errs else ""))
    print(f"\nTOTAL inserted={total_ins} skipped(dup/kosong)={total_skip} dari {len(items)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
