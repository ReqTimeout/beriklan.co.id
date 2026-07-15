#!/bin/bash
# Auto-deploy script — runs as cron, deploys to CF Workers when new commits detected
# This is the FALLBACK when CF Workers Build (Dashboard) isn't set up yet
#
# Setup:
#   1. Save CF token to: ~/.beriklan/cf-token (chmod 600)
#   2. Save CF account ID: ~/.beriklan/cf-account-id
#   3. chmod +x ~/.beriklan/auto-deploy.sh
#   4. Add to crontab:
#      */5 * * * * /Users/maabook/.beriklan/auto-deploy.sh >> /tmp/beriklan-deploy.log 2>&1

set -e

REPO_DIR="/Users/maabook/Desktop/beriklan.co.id"
LOG_PREFIX="[auto-deploy $(date '+%Y-%m-%d %H:%M:%S')]"
LOCK_FILE="/tmp/beriklan-deploy.lock"
LAST_DEPLOYED_FILE="$REPO_DIR/.last-deployed-sha"
SECRETS_DIR="${BERIKLAN_SECRETS_DIR:-$HOME/.beriklan}"
CF_TOKEN_FILE="$SECRETS_DIR/cf-token"
CF_ACCOUNT_FILE="$SECRETS_DIR/cf-account-id"

# Read secrets from file (not hardcoded)
if [ -f "$CF_TOKEN_FILE" ]; then
    CF_TOKEN=$(cat "$CF_TOKEN_FILE")
else
    CF_TOKEN="${CF_TOKEN:-}"
fi
if [ -f "$CF_ACCOUNT_FILE" ]; then
    CF_ACCOUNT=$(cat "$CF_ACCOUNT_FILE")
else
    CF_ACCOUNT="${CF_ACCOUNT:-766dfffa7e5dcd8ba246ebfa60bc10ba}"
fi

if [ -z "$CF_TOKEN" ]; then
    echo "$LOG_PREFIX ❌ CF_TOKEN not set (file: $CF_TOKEN_FILE or env)"
    exit 1
fi

# Prevent concurrent runs
if [ -f "$LOCK_FILE" ]; then
    echo "$LOG_PREFIX ⚠️  Lock file exists, skipping (already running)"
    exit 0
fi
echo "$LOCK_FILE created" > "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

cd "$REPO_DIR" || exit 1

echo "$LOG_PREFIX Starting auto-deploy check..."

# Fetch latest from origin
git fetch origin main --quiet 2>&1 || {
    echo "$LOG_PREFIX ❌ git fetch failed"
    exit 1
}

LOCAL_SHA=$(git rev-parse HEAD)
REMOTE_SHA=$(git rev-parse origin/main)

if [ "$LOCAL_SHA" = "$REMOTE_SHA" ]; then
    echo "$LOG_PREFIX ✓ Local up-to-date ($LOCAL_SHA), no deploy needed"
    exit 0
fi

echo "$LOG_PREFIX 🔄 New commits: $LOCAL_SHA → $REMOTE_SHA"

if [ -f "$LAST_DEPLOYED_FILE" ] && [ "$(cat $LAST_DEPLOYED_FILE)" = "$REMOTE_SHA" ]; then
    echo "$LOG_PREFIX ✓ Already deployed $REMOTE_SHA, skipping"
    exit 0
fi

# Pull latest (rebase handles divergent branches)
git pull --rebase origin main --quiet 2>&1 || {
    echo "$LOG_PREFIX ❌ git pull failed - trying fetch + reset"
    git fetch origin main --quiet
    git reset --hard origin/main --quiet 2>&1 || {
        echo "$LOG_PREFIX ❌ git reset failed"
        exit 1
    }
}

cd "$REPO_DIR/web"
echo "$LOG_PREFIX 📦 Installing deps..."
npm install --silent --no-audit --no-fund 2>&1 | tail -3

echo "$LOG_PREFIX 🔨 Building..."
npm run build 2>&1 | tail -3

echo "$LOG_PREFIX 🚀 Deploying to CF Workers..."
DEPLOY_OUTPUT=$(export CF_TOKEN="$CF_TOKEN" CF_ACCOUNT="$CF_ACCOUNT" && npx wrangler deploy 2>&1)
DEPLOY_EXIT=$?

echo "$DEPLOY_OUTPUT" | tail -10

if [ $DEPLOY_EXIT -eq 0 ]; then
    echo "$REMOTE_SHA" > "$LAST_DEPLOYED_FILE"
    echo "$LOG_PREFIX ✅ Deploy success — saved SHA $REMOTE_SHA"

    echo "$LOG_PREFIX 🗑️  Purging CF cache..."
    curl -s -X POST "https://api.cloudflare.com/client/v4/zones/47f87944d6d690eb388e7be1143c14a2/purge_cache" \
        -H "Authorization: Bearer $CF_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"purge_everything":true}' | head -c 200
    echo ""
else
    echo "$LOG_PREFIX ❌ Deploy failed (exit $DEPLOY_EXIT)"
    exit 1
fi

echo "$LOG_PREFIX Done"
