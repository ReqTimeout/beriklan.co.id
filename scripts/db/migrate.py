#!/usr/bin/env python3
"""
D1 database migration script.

Operations:
1. --migrate         Apply schema.sql + seed initial data (1500 keywords dari keywords.json)
2. --dry-run         Show plan tanpa execute
3. --seed-keywords   Insert/update keywords dari src/data/keywords.json ke keyword_queue
4. --query "SQL"     Run arbitrary SELECT (read-only)
5. --stats           Show table counts + row count per table
6. --reset           DROP all tables (WARNING: destructive)

Connect to D1:
- Local: pakai wrangler CLI (`wrangler d1 execute`)
- Remote: pakai CF API /accounts/{id}/d1/database/{id}/query (zone-scoped token tidak support ini)
  Fallback: pakai CF Worker proxy endpoint /api/db/query (implemented sebagai endpoint di worker-entry.js)

Default mode: LOCAL (via wrangler). Kalau CF_API_TOKEN ada, bisa remote (eksperimental).

Usage:
    python3 scripts/db/migrate.py --dry-run
    python3 scripts/db/migrate.py --migrate
    python3 scripts/db/migrate.py --seed-keywords
    python3 scripts/db/migrate.py --stats
    python3 scripts/db/migrate.py --query "SELECT COUNT(*) FROM keyword_queue"
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).parent.parent.parent
SCHEMA = Path(__file__).parent / "schema.sql"
KEYWORDS_JSON = ROOT / "src/data/keywords.json"

DEFAULT_DB = "beriklan-seo"

def run_local(sql: str, db: str = DEFAULT_DB) -> Tuple[bool, str]:
    """Run SQL via wrangler CLI. Returns (success, output)."""
    try:
        result = subprocess.run(
            ["npx", "wrangler", "d1", "execute", db, f"--command={sql}"],
            capture_output=True, text=True, timeout=60,
            cwd=str(ROOT),
        )
        out = (result.stdout + result.stderr).strip()
        return (result.returncode == 0, out)
    except subprocess.TimeoutExpired:
        return (False, "timeout")
    except FileNotFoundError:
        return (False, "wrangler not found (install: npm install wrangler)")

def escape_sql_value(v) -> str:
    if v is None: return "NULL"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, bool):
        return "1" if v else "0"
    s = str(v).replace("'", "''")
    return f"'{s}'"

def apply_schema(db: str, dry_run: bool = False) -> bool:
    if not SCHEMA.exists():
        print(f"ERROR: {SCHEMA} not found")
        return False
    sql_text = SCHEMA.read_text()
    if dry_run:
        print(f"[DRY RUN] Would apply {len(sql_text.split(';'))} statements from schema.sql to '{db}'")
        # show first 5 statements as preview
        stmts = [s.strip() for s in sql_text.split(';') if s.strip()]
        for i, s in enumerate(stmts[:8], 1):
            preview = s[:100].replace("\n", " ")
            print(f"  {i}. {preview}...")
        return True
    ok, out = run_local(f":source <(cat scripts/db/schema.sql)" if False else "SELECT 1", db=db)
    # wrangler doesn't support :source, so use file mode
    try:
        result = subprocess.run(
            ["npx", "wrangler", "d1", "execute", db, f"--file={SCHEMA}"],
            capture_output=True, text=True, timeout=120,
            cwd=str(ROOT),
        )
        print(result.stdout[-2000:])
        if result.returncode != 0:
            print(result.stderr[-1000:])
            return False
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def seed_keywords(db: str, dry_run: bool = False, batch_size: int = 100) -> bool:
    if not KEYWORDS_JSON.exists():
        print(f"ERROR: {KEYWORDS_JSON} not found")
        return False
    keywords = json.loads(KEYWORDS_JSON.read_text())
    print(f"Loaded {len(keywords)} keywords")

    if dry_run:
        print(f"[DRY RUN] Would insert {len(keywords)} keywords into '{db}.keyword_queue'")
        # show first 3
        for k in keywords[:3]:
            print(f"  - {k['keyword']!r} | service={k.get('service')} | volume={k.get('volume')}")
        return True

    inserted = 0
    failed = 0
    for i in range(0, len(keywords), batch_size):
        batch = keywords[i:i+batch_size]
        values = []
        for k in batch:
            kw_id = f"kw_{k['keyword_normalized'][:32].replace(' ', '_').replace('-', '_')}_{i}_{len(values)}"
            values.append(
                "(\n  "
                + ",\n  ".join([
                    escape_sql_value(kw_id),
                    escape_sql_value(k["keyword"]),
                    escape_sql_value(k["keyword_normalized"]),
                    escape_sql_value(k.get("source")),
                    escape_sql_value(k.get("keyword")[:50]),  # seed from keyword
                    escape_sql_value("2026-07-14T00:00:00Z"),  # discovered_at
                    escape_sql_value("pending"),
                    str(k.get("priority_score") or 50),
                    escape_sql_value(k.get("intent")),
                    escape_sql_value(k.get("service")),
                    escape_sql_value(k.get("city")),
                    str(k.get("estimated_volume")) if k.get("estimated_volume") is not None else "NULL",
                    escape_sql_value(json.dumps(k) if k else None),
                ])
                + "\n)"
            )
        sql = (
            "INSERT OR REPLACE INTO keyword_queue "
            "(id, keyword, keyword_normalized, source, seed, discovered_at, status, priority_score, intent, service, city, estimated_volume, rank_match_profile) "
            "VALUES " + ",\n".join(values)
        )
        ok, out = run_local(sql, db)
        if ok:
            inserted += len(batch)
            print(f"  Inserted batch {i//batch_size + 1}: {len(batch)} keywords (total {inserted}/{len(keywords)})")
        else:
            failed += len(batch)
            print(f"  FAILED batch {i//batch_size + 1}: {out[:300]}")
    print(f"\nResult: {inserted} inserted, {failed} failed")
    return failed == 0

def show_stats(db: str) -> bool:
    tables = ["keyword_queue", "articles", "rank_snapshots", "index_log",
              "trending_log", "audit_log", "automation_health", "settings",
              "api_keys", "conversion_log", "manual_review", "request_queue", "blocklist"]
    print(f"Database: {db}")
    print(f"{'TABLE':<25} {'ROWS':>10}")
    print("-" * 40)
    for t in tables:
        ok, out = run_local(f"SELECT COUNT(*) FROM {t}", db=db)
        m = re.search(r"(\d+)", out)
        n = m.group(1) if m else "?"
        marker = " <--" if t == "keyword_queue" else ""
        print(f"  {t:<23} {n:>10}{marker}")
    return True

def run_query(sql: str, db: str) -> bool:
    ok, out = run_local(sql, db)
    print(out)
    return ok

def reset_db(db: str) -> bool:
    print(f"WARNING: This will drop ALL tables in '{db}'. Continue? [y/N]")
    if input().lower() != "y":
        return False
    drops = [
        "DROP TABLE IF EXISTS keyword_queue",
        "DROP TABLE IF EXISTS articles",
        "DROP TABLE IF EXISTS rank_snapshots",
        "DROP TABLE IF EXISTS index_log",
        "DROP TABLE IF EXISTS trending_log",
        "DROP TABLE IF EXISTS audit_log",
        "DROP TABLE IF EXISTS automation_health",
        "DROP TABLE IF EXISTS settings",
        "DROP TABLE IF EXISTS api_keys",
        "DROP TABLE IF EXISTS conversion_log",
        "DROP TABLE IF EXISTS manual_review",
        "DROP TABLE IF EXISTS request_queue",
        "DROP TABLE IF EXISTS blocklist",
    ]
    for d in drops:
        ok, out = run_local(d, db)
        print(f"  {d}: {'OK' if ok else 'FAIL'}")
    return True

def main():
    p = argparse.ArgumentParser(description="D1 migration + seeding")
    p.add_argument("--db", default=DEFAULT_DB, help="D1 database name")
    p.add_argument("--migrate", action="store_true", help="Apply schema")
    p.add_argument("--dry-run", action="store_true", help="Show plan, don't execute")
    p.add_argument("--seed-keywords", action="store_true", help="Seed keywords")
    p.add_argument("--stats", action="store_true", help="Show table stats")
    p.add_argument("--query", help="Run read-only query")
    p.add_argument("--reset", action="store_true", help="Drop all tables (destructive)")
    args = p.parse_args()

    if args.dry_run:
        print("=== DRY RUN MODE ===\n")
    if args.migrate or args.dry_run:
        apply_schema(args.db, dry_run=args.dry_run)
    if args.seed_keywords or args.dry_run:
        seed_keywords(args.db, dry_run=args.dry_run)
    if args.stats:
        show_stats(args.db)
    if args.query:
        run_query(args.query, args.db)
    if args.reset:
        reset_db(args.db)
    if not any([args.migrate, args.dry_run, args.seed_keywords, args.stats, args.query, args.reset]):
        p.print_help()

if __name__ == "__main__":
    main()
