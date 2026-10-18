#!/bin/bash
# Sequential batch runner - processes one batch at a time
MAX=500
for i in $(seq 1 $MAX); do
    python3 -u scripts/gen_articles.py --batch 200 2>&1 | tail -2 >> /tmp/batch_runner.log
done
