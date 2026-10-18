#!/usr/bin/env python3
"""
Update Cron Settings — Naikkan publish pace 150 → 300/hari
============================================================

Pakai salah satu cara:
  1. Via Worker API (recommended, no wrangler needed):
     python3 scripts/update_cron_settings.py

  2. Via wrangler (manual, requires wrangler CLI):
     wrangler d1 execute beriklan-seo --remote --command "UPDATE cron_settings SET cron='300' WHERE name='publish_daily_limit'"

  3. Via Admin Dashboard UI (jika ada)

Settings yang akan di-update:
  - publish_daily_limit: 600 (current value in migration, fallback 150) → 300 (saat ini konservatif)
  - publish_batch_size: 25 → 30
  - indexnow count per run: 50 → 100
  - gsc-indexing count per run: 50 → 80

Usage:
  python3 scripts/update_cron_settings.py --dry-run
  python3 scripts/update_cron_settings.py            # update via API
"""
import os, sys, json, argparse, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")
SITE = "https://beriklan.co.id"

# Settings to update
UPDATES = [
    {"name": "publish_daily_limit", "value": "300", "label": "Publish harian maksimum (ramp-up 300/hari)"},
    {"name": "publish_batch_size", "value": "30", "label": "Publish per sync-posts run (30)"},
]


def update_via_api(dry_run=False):
    """Update via Worker API."""
    results = []
    for u in UPDATES:
        url = f"{SITE}/api/admin/cron/update?token={ADMIN_TOKEN}&name={u['name']}&value={u['value']}&label={urllib.parse.quote(u['label'])}"
        if dry_run:
            print(f"[DRY-RUN] GET {url}")
            results.append({"name": u["name"], "dry_run": True, "url": url})
            continue
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                results.append(data)
                print(f"  ✅ {u['name']}: {data.get('cron', '?')} (enabled={data.get('enabled')})")
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()[:200]
            print(f"  ❌ {u['name']}: HTTP {e.code} — {error_body}")
            results.append({"error": str(e.code), "name": u["name"]})
        except Exception as e:
            print(f"  ❌ {u['name']}: {e}")
            results.append({"error": str(e), "name": u["name"]})
    return results


def update_via_wrangler_sql():
    """Generate wrangler SQL commands for manual execution."""
    print("📋 WRANGLER SQL COMMANDS (run manually):\n")
    for u in UPDATES:
        print(f'wrangler d1 execute beriklan-seo --remote --command "UPDATE cron_settings SET cron=\'{u["value"]}\', label=\'{u["label"]}\' WHERE name=\'{u["name"]}\'"')
    print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--sql-only', action='store_true', help='Just print SQL, no API call')
    args = parser.parse_args()

    print('=' * 70)
    print('UPDATE CRON SETTINGS — Publish Pace 150 → 300')
    print('=' * 70)
    print()
    print('Settings to update:')
    for u in UPDATES:
        print(f'  • {u["name"]}: → {u["value"]} ({u["label"]})')
    print()

    if args.sql_only:
        update_via_wrangler_sql()
        return

    if args.dry_run:
        update_via_api(dry_run=True)
        return

    print(f'Updating via API: {SITE}/api/admin/cron/update ...')
    print()
    results = update_via_api(dry_run=False)

    print()
    print('=' * 70)
    print('Summary')
    print('=' * 70)
    success = sum(1 for r in results if r.get('ok'))
    print(f'  Success: {success}/{len(results)}')


if __name__ == '__main__':
    main()
