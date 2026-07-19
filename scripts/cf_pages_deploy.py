#!/usr/bin/env python3
"""Deploy beriklanweb static dist to Cloudflare Pages.
Uses account-scoped CF API token via wrangler CLI.

Pipeline:
  1. Verify dist/ exists (run `npm run build` first)
  2. Run scripts/build_sitemaps.py (per-type sitemaps with real lastmod)
  3. Deploy web/dist to Cloudflare Pages
  4. After deploy, run scripts/indexnow_submit.py --sitemap --since 7
     (IndexNow batch-submits URLs modified in last 7 days to Bing/Seznam/Naver)

Usage:
  CLOUDFLARE_API_TOKEN=cfut_... python3 scripts/cf_pages_deploy.py
or:
  python3 scripts/cf_pages_deploy.py
(token read from .env or hardcoded)

Set SKIP_INDEXNOW=1 to bypass step 4 (e.g. local dry-run).
"""
import os, subprocess, sys, time, urllib.request

UA = "Mozilla/5.0 (compatible; BeriklanBot/1.0; +https://beriklan.co.id/)"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN") or "cfut_REDACTED"
PROJECT = "beriklanweb"
SITE = "https://www.beriklan.co.id"

env = os.environ.copy()
env["CLOUDFLARE_API_TOKEN"] = TOKEN


def run_step(name, cmd, cwd=None):
    print(f"\n=== {name} ===")
    print(f"Running: {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=cwd, env=env)
    if r.returncode != 0:
        print(f"FAIL {name} exit {r.returncode}")
        sys.exit(r.returncode)
    print(f"OK {name}")


# Step 1: build sitemaps
run_step(
    "Build sitemaps",
    ["python3", "scripts/build_sitemaps.py"],
    cwd=ROOT,
)

# Step 2: deploy
cmd = [
    "npx", "wrangler", "pages", "deploy", "dist",
    f"--project-name={PROJECT}",
    "--branch=main",
    "--commit-dirty=true",
]
print(f"\n=== Deploy ===\nRunning: {' '.join(cmd)}")
r = subprocess.run(cmd, cwd="web", env=env)
if r.returncode != 0:
    sys.exit(r.returncode)
print("OK Deploy")

# Step 3 + 4: verify INDEXNOW_KEY live, then submit
if not os.environ.get("SKIP_INDEXNOW"):
    print(f"\n=== Verify IndexNow key file is live ===")
    key_path = os.path.join(ROOT, "web/public/INDEXNOW_KEY.txt")
    if os.path.exists(key_path):
        expected_key = open(key_path).read().strip()
        url = f"{SITE}/INDEXNOW_KEY.txt"
        verified = False
        for attempt in range(20):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    live = resp.read().decode().strip()
                    if live == expected_key:
                        print(f"OK key file matches at {url} (attempt {attempt+1})")
                        verified = True
                        break
                    else:
                        print(f"WARN attempt {attempt+1}/20: key mismatch got '{live}'")
            except Exception as e:
                print(f"WARN attempt {attempt+1}/20: fetch failed: {e}")
            time.sleep(5)
        if not verified:
            print("WARN IndexNow key unreachable after 100s. Submission may 403.")

        run_step(
            "IndexNow submit",
            ["python3", "scripts/indexnow_submit.py", "--sitemap", "--since", "7"],
            cwd=ROOT,
        )
    else:
        print("WARN no INDEXNOW_KEY.txt, skipping submission")
else:
    print("\n(SKIP_INDEXNOW=1 -- skipping)")
