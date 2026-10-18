#!/usr/bin/env bash
# run.sh — Start or resume the bulk article generator in background.
# Usage: ./run.sh [workers] [batch]
#   workers default: 12
#   batch default: 48

WORKERS=${1:-12}
BATCH=${2:-48}
LOG=/tmp/bulk_generate.log
PIDFILE=/tmp/bulk_generate.pid

# Stop any existing instance
if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Stopping existing process (PID $PID)..."
        kill "$PID" 2>/dev/null
        sleep 3
    fi
fi

# Start fresh (script auto-loads _progress.json for resume)
cd "$(dirname "$0")/.."
nohup python3 -u scripts/bulk_generate_all.py --batch "$BATCH" --workers "$WORKERS" > "$LOG" 2>&1 &
PID=$!
echo "$PID" > "$PIDFILE"
echo "Started: PID $PID, workers=$WORKERS, batch=$BATCH"
echo "Log: $LOG"
echo "Monitor: python3 scripts/check_progress.py"
echo "Stop: kill \$(cat $PIDFILE) or pkill -f bulk_generate_all"