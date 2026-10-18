#!/usr/bin/env python3
"""
watch_limits.py — Monitor bulk_generate_all.py for rate limits.

Watch the error log and main log. If a rate limit is detected:
- Print a clear alert
- Optionally play a macOS sound notification
- Auto-stop the process so it can be resumed after the limit resets

Usage:
  python3 scripts/watch_limits.py            # watch only (no auto-stop)
  python3 scripts/watch_limits.py --autostop # stop process on rate limit
"""
import argparse, subprocess, sys, time
from pathlib import Path

ERR_LOG = "/tmp/bulk_generate_err.log"
MAIN_LOG = "/tmp/bulk_generate.log"
PID_FILE = "/tmp/bulk_generate.pid"

RATE_PATTERNS = [
    "FreeUsageLimit",
    "rate_limit",
    "rate limit",
    "429",
    "quota",
    "insufficient",
]

def notify(title, message, sound="Glass"):
    """macOS notification"""
    try:
        subprocess.run([
            "osascript", "-e",
            f'display notification "{message}" with title "{title}" sound name "{sound}"'
        ], check=False, capture_output=True)
    except: pass

def get_progress():
    """Read progress file"""
    pfile = Path("/Users/maabook/Desktop/beriklan.co.id/drafts/_progress.json")
    if pfile.exists():
        try:
            import json
            d = json.load(open(pfile))
            return len(d.get("processed_slugs", []))
        except: return 0
    return 0

def is_running():
    """Check if process is still running"""
    try:
        pf = Path(PID_FILE)
        if not pf.exists(): return False, None
        pid = int(pf.read_text().strip())
        r = subprocess.run(["ps", "-p", str(pid)], capture_output=True, text=True)
        if str(pid) in r.stdout: return True, pid
    except: pass
    return False, None

def tail_file(path, lines=50):
    try:
        r = subprocess.run(["tail", "-n", str(lines), path], capture_output=True, text=True)
        return r.stdout
    except: return ""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--autostop", action="store_true",
                       help="Auto-stop the process when rate limit detected")
    parser.add_argument("--interval", type=int, default=30, help="Check interval in seconds")
    args = parser.parse_args()

    print("╔════════════════════════════════════════╗")
    print("║  Beriklan Bulk Generator — Watcher     ║")
    print("╚════════════════════════════════════════╝")
    print(f"Watching: {ERR_LOG} and {MAIN_LOG}")
    print(f"Auto-stop: {args.autostop}")
    print(f"Check interval: {args.interval}s")
    print()

    last_err_size = 0
    last_main_size = 0
    last_progress = 0
    last_check = time.time()
    rate_limit_count = 0

    while True:
        running, pid = is_running()
        if not running:
            print(f"[{time.strftime('%H:%M:%S')}] Process not running (waiting to be restarted)")
            time.sleep(args.interval)
            continue

        # Check error log for new rate limit lines
        err_path = Path(ERR_LOG)
        if err_path.exists():
            try:
                size = err_path.stat().st_size
                if size > last_err_size:
                    with open(ERR_LOG) as f:
                        f.seek(last_err_size)
                        new_lines = f.read()
                    last_err_size = size
                    for pat in RATE_PATTERNS:
                        if pat.lower() in new_lines.lower():
                            rate_limit_count += 1
                            print(f"\n⚠⚠⚠ RATE LIMIT DETECTED ⚠⚠⚠", flush=True)
                            print(f"Pattern: {pat}", flush=True)
                            print(f"New error lines:\n{new_lines[-500:]}", flush=True)
                            notify("Beriklan — Rate Limit",
                                  f"OpenCode Zen free limit hit! {rate_limit_count}x today. Process will stop.")
                            if args.autostop:
                                print(f"Auto-stopping process (PID {pid})...", flush=True)
                                try:
                                    subprocess.run(["kill", str(pid)], check=False)
                                    time.sleep(2)
                                    subprocess.run(["kill", "-9", str(pid)], check=False)
                                except: pass
                                notify("Beriklan — Stopped",
                                      f"Process stopped. Resume in 9 hours with: cd ~/Desktop/beriklan.co.id && python3 scripts/bulk_generate_all.py")
                                return
                            break
            except: pass

        # Periodic status update
        now = time.time()
        if now - last_check >= 60:
            last_check = now
            prog = get_progress()
            delta = prog - last_progress
            last_progress = prog
            tail = tail_file(MAIN_LOG, 3).strip().replace("\n", " | ")
            print(f"[{time.strftime('%H:%M:%S')}] PID {pid} | Done: {prog:,} ({delta:+d} since 1m) | Last: {tail[:80]}", flush=True)

        time.sleep(args.interval)

if __name__ == "__main__":
    main()