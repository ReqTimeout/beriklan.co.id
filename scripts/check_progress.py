#!/usr/bin/env python3
"""Monitor progress of bulk_generate_all.py"""
import json, os, glob, time
from datetime import datetime, timedelta

DRAFTS = "/Users/maabook/Desktop/beriklan.co.id/drafts"
PROGRESS = os.path.join(DRAFTS, "_progress.json")
QUEUE = "/Users/maabook/Desktop/beriklan.co.id/web/src/data/keyword-queue.json"
LOG = "/tmp/bulk_generate.log"

# Check if running
running = False
pid = None
try:
    import subprocess
    r = subprocess.run(["pgrep", "-f", "bulk_generate_all"], capture_output=True, text=True)
    if r.stdout.strip():
        running = True
        pid = r.stdout.strip().split("\n")[0]
except: pass

# Read progress
done = 0
total = 0
if os.path.exists(PROGRESS):
    with open(PROGRESS) as f:
        p = json.load(f)
        done = len(p.get("processed_slugs", []))

if os.path.exists(QUEUE):
    q = json.load(open(QUEUE))
    total = len(q)

# Read last log lines
log_tail = ""
if os.path.exists(LOG):
    with open(LOG) as f:
        lines = f.readlines()
        log_tail = "".join(lines[-6:])

# Count draft files
draft_files = sorted(glob.glob(os.path.join(DRAFTS, "batch_*.json")))
last_batch = draft_files[-1] if draft_files else ""
last_batch_size = 0
if last_batch:
    try:
        last_batch_size = len(json.load(open(last_batch)))
    except: pass

# Estimate rate from last 3 batches
rate = 0
if len(draft_files) >= 2:
    recent = draft_files[-3:]
    t0 = os.path.getmtime(recent[0])
    t1 = os.path.getmtime(recent[-1])
    delta_h = (t1 - t0) / 3600
    if delta_h > 0:
        rate = (len(recent) * last_batch_size) / delta_h

eta_h = (total - done) / rate if rate > 0 else 0
eta_date = (datetime.now() + timedelta(hours=eta_h)).strftime("%a %d %b %H:%M") if eta_h > 0 else "-"

pct = round(done / total * 100, 1) if total > 0 else 0

# Show errors
errs = 0
err_log = "/tmp/bulk_generate_err.log"
if os.path.exists(err_log):
    errs = len(open(err_log).read().strip().split("\n"))

print(f"""
╔══════════════════════════════════════╗
║  Beriklan Bulk Generator — Monitor   ║
╚══════════════════════════════════════╝

Status:   {"● RUNNING" if running else "○ STOPPED"} {"(PID: "+pid+")" if pid else ""}
Progress: {done:,} / {total:,} ({pct}%)
Throughput: {rate:,.0f} artikel/jam
ETA:      {timedelta(hours=eta_h) if eta_h else "-"} ({eta_date})
Batches:  {len(draft_files)} file
Errors:   {errs}

Last log:
{log_tail.strip()}
""".strip())