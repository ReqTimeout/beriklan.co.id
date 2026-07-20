#!/usr/bin/env python3
"""
directory_tracker.py — Track backlink submissions for P1.1.

State stored in web/data/directory-progress.json with structure:
{
  "summary": {"total": 90, "submitted": 0, "live": 0, "rejected": 0, "pending": 90},
  "items": [
    {"id": "clutch-co", "status": "pending", "submitted_at": null, "live_url": null,
     "notes": ""},
    ...
  ]
}

CLI usage:
  python3 scripts/directory_tracker.py list                # show all
  python3 scripts/directory_tracker.py list --status pending
  python3 scripts/directory_tracker.py status clutch-co submitted
  python3 scripts/directory_tracker.py status clutch-co live --url https://clutch.co/profile/beriklan
  python3 scripts/directory_tracker.py status clutch-co rejected
  python3 scripts/directory_tracker.py reset
  python3 scripts/directory_tracker.py export               # write progress JSON for dashboard
  python3 scripts/directory_tracker.py priority             # show high-priority first
"""
import argparse
import json
import os
import sys
from datetime import datetime

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRS = os.path.join(WEB, "scripts", "directories.json")
PROG = os.path.join(WEB, "data", "directory-progress.json")
PUB_PROG = os.path.join(WEB, "public", "data", "directory-progress.json")

STATUSES = ["pending", "submitted", "live", "rejected"]


def load_dirs():
    return json.load(open(DIRS))


def load_progress():
    if not os.path.exists(PROG):
        return init_progress()
    return json.load(open(PROG))


def save_progress(prog):
    os.makedirs(os.path.dirname(PROG), exist_ok=True)
    os.makedirs(os.path.dirname(PUB_PROG), exist_ok=True)
    json.dump(prog, open(PROG, "w"), ensure_ascii=False, indent=2)
    json.dump(prog, open(PUB_PROG, "w"), ensure_ascii=False, indent=2)


def init_progress():
    dirs = load_dirs()
    items = [{
        "id": d["id"],
        "name": d["name"],
        "url": d["url"],
        "submit_url": d["submit_url"],
        "category": d["category"],
        "country": d["country"],
        "domain_rating": d.get("domain_rating", 0),
        "priority": d.get("priority", "medium"),
        "status": "pending",
        "submitted_at": None,
        "live_url": None,
        "notes": d.get("notes", ""),
    } for d in dirs]
    return compute_summary({"items": items})


def compute_summary(prog):
    items = prog["items"]
    counts = {"total": len(items)}
    for s in STATUSES:
        counts[s] = sum(1 for x in items if x.get("status") == s)
    avg_dr_live = sum(x["domain_rating"] for x in items if x.get("status") == "live") / max(counts["live"], 1)
    counts["avg_dr_live"] = round(avg_dr_live, 1)
    counts["progress_pct"] = round(100 * (counts["submitted"] + counts["live"]) / counts["total"], 1)
    counts["updated_at"] = datetime.now().isoformat(timespec="seconds")
    prog["summary"] = counts
    return prog


def cmd_list(args):
    prog = load_progress()
    items = prog["items"]
    if args.status:
        items = [x for x in items if x.get("status") == args.status]
    if args.priority:
        items = [x for x in items if x.get("priority") == args.priority]
    if args.dr_min:
        items = [x for x in items if x.get("domain_rating", 0) >= args.dr_min]
    items.sort(key=lambda x: ({"high": 0, "medium": 1, "low": 2}[x["priority"]], -x["domain_rating"]))
    print(f"\n{'STATUS':12s} {'PRIO':8s} {'DR':4s} {'COUNTRY':12s} {'NAME':35s} {'URL':50s}")
    print("-" * 130)
    for x in items:
        print(f"{x['status']:12s} {x['priority']:8s} {x['domain_rating']:4d} {x['country']:12s} {x['name']:35s} {x.get('live_url') or x['url']:50s}")
    s = prog["summary"]
    print(f"\nSummary: total={s['total']} submitted={s['submitted']} live={s['live']} pending={s['pending']} rejected={s['rejected']}")
    print(f"Progress: {s['progress_pct']}% | Avg DR (live): {s['avg_dr_live']}")


def cmd_status(args):
    prog = load_progress()
    item = next((x for x in prog["items"] if x["id"] == args.id), None)
    if not item:
        print(f"❌ Directory '{args.id}' not found. Available:")
        for x in prog["items"][:10]:
            print(f"  {x['id']}")
        return 1
    if args.status_value == "live":
        if not args.url:
            print(f"❌ 'live' status requires --url <live_profile_url>")
            return 1
        item["live_url"] = args.url
    item["status"] = args.status_value
    item["submitted_at"] = datetime.now().isoformat(timespec="seconds") if args.status_value != "pending" else None
    if args.note:
        item["notes"] = (item.get("notes", "") + " | " + args.note).strip(" |")
    prog = compute_summary(prog)
    save_progress(prog)
    print(f"✅ {item['name']} → status={item['status']}" + (f", live_url={item['live_url']}" if item['live_url'] else ""))
    print(f"   Summary now: submitted={prog['summary']['submitted']} live={prog['summary']['live']} pending={prog['summary']['pending']}")


def cmd_reset(args):
    if not args.yes:
        ans = input("Reset all progress to pending? [y/N] ")
        if ans.lower() != "y":
            print("aborted")
            return
    prog = init_progress()
    save_progress(prog)
    print(f"✅ Reset to all pending ({len(prog['items'])} directories)")


def cmd_export(args):
    prog = load_progress()
    prog = compute_summary(prog)
    save_progress(prog)
    print(f"✅ Exported to {PUB_PROG}")
    s = prog["summary"]
    print(f"   {s['progress_pct']}% complete ({s['submitted']+s['live']}/{s['total']})")


def main():
    ap = argparse.ArgumentParser(description="Directory backlink tracker")
    sub = ap.add_subparsers(dest="cmd")

    p_list = sub.add_parser("list", help="list all directories")
    p_list.add_argument("--status", choices=STATUSES)
    p_list.add_argument("--priority", choices=["high", "medium", "low"])
    p_list.add_argument("--dr-min", type=int, help="filter by min domain rating")

    p_status = sub.add_parser("status", help="update directory status")
    p_status.add_argument("id", help="directory id (e.g. clutch-co)")
    p_status.add_argument("status_value", choices=STATUSES, help="new status")
    p_status.add_argument("--url", help="live profile URL (required for 'live')")
    p_status.add_argument("--note", help="append note")

    p_reset = sub.add_parser("reset", help="reset all to pending")
    p_reset.add_argument("--yes", "-y", action="store_true")

    p_export = sub.add_parser("export", help="export progress to dashboard JSON")

    args = ap.parse_args()
    if args.cmd == "list":
        cmd_list(args)
    elif args.cmd == "status":
        cmd_status(args)
    elif args.cmd == "reset":
        cmd_reset(args)
    elif args.cmd == "export":
        cmd_export(args)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()