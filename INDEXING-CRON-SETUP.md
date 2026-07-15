# GH Actions Indexing Cron Setup

> Daily auto-submit pending URLs to Google + IndexNow.

---

## Overview

Workflow: `.github/workflows/indexing-cron.yml`

- **Schedule:** Every day at **06:00 UTC** (14:00 WIB)
- **Trigger:** Cron + manual `workflow_dispatch`
- **Quota reset:** Google Indexing API quota resets at **00:00 Pacific Time**
  - Pacific Time = UTC-8 (winter) / UTC-7 (summer)
  - 06:00 UTC = 22:00/23:00 previous day Pacific Time → quota always reset by then
- **Quota:** 200 publish/day/project → max ~200 URLs per run

---

## Required GitHub Secrets

Setup at: `https://github.com/ReqTimeout/beriklan.co.id/settings/secrets/actions`

### 1. `GSC_SERVICE_ACCOUNT_JSON` (REQUIRED)

The full content of `web/secrets/gsc-indexer.json` as a single string.

```bash
# Read and copy to clipboard
cat web/secrets/gsc-indexer.json | pbcopy  # macOS
# or
cat web/secrets/gsc-indexer.json | xclip -selection clipboard  # Linux
```

Then paste as GH Secret `GSC_SERVICE_ACCOUNT_JSON` (entire JSON content, single line OK).

### 2. `INDEXNOW_KEY` (OPTIONAL)

The IndexNow API key. Set this if you want the workflow to also submit to Bing/Seznam/Naver.

```bash
# Current key on live site
echo "2dac33f6303f4041b9ec7e2f2910ea80"
```

---

## Manual Trigger

```bash
# Via GitHub UI
gh workflow run indexing-cron.yml --repo ReqTimeout/beriklan.co.id

# Or in GitHub Actions UI: Actions tab → Daily GSC Indexing Cron → Run workflow
```

---

## What It Does

1. Checkout repo
2. Setup Python 3.11 + install `google-api-python-client`, `google-auth-httplib2`, `requests`
3. Read `GSC_SERVICE_ACCOUNT_JSON` from secrets
4. Run `python scripts/seo/gsc_indexer.py --new`
   - `--new`: only submit URLs not yet submitted to Google (based on `data/index_log.json`)
   - Quota-aware: stops Google submission if quota hit, continues IndexNow
5. Upload logs as artifact
6. Commit updated `data/index_log.json` + `data/pending_google_indexing.json`
7. Print summary to GitHub Step Summary

---

## Monitor

- **GitHub Actions:** https://github.com/ReqTimeout/beriklan.co.id/actions/workflows/indexing-cron.yml
- **Logs:** Each run uploads `/tmp/indexing-cron.log` as artifact (7-day retention)
- **Manual verify:** `python3 scripts/seo/check_coverage.py --sample 30`

---

## Adjust Schedule

To change cron time, edit `.github/workflows/indexing-cron.yml` line:

```yaml
schedule:
  - cron: '0 6 * * *'  # minute hour day month weekday (UTC)
```

Examples:
- `0 6 * * *` — Every day at 06:00 UTC
- `0 */6 * * *` — Every 6 hours
- `0 6,18 * * *` — Twice a day (06:00 and 18:00 UTC)
