#!/usr/bin/env python3
"""Reset stale Indonesian-derived data files to empty (regenerated for MY in later phases)."""
import io

WEB = "/Users/maabook/Desktop/beriklan.my/web/"

RESET = {
    'src/data/city-content.json': '{}',
    'src/data/clusters.json': '{}',
    'src/data/keyword-to-posts.json': '{}',
    'src/data/keywords.json': '[]',
    'src/data/per_city.json': '[]',
    'src/data/posts-meta.json': '[]',
    'src/data/refresh-candidates.json': '[]',
    'src/data/keyword-stats.json': '{}',
    'src/data/keyword-queue-stats.json': '{}',
    'src/data/pillar-config.json': '{}',
    'public/data/clusters.json': '{}',
    'public/data/keyword-queue.json': '[]',
    'public/data/keyword-stats.json': '{}',
}

for rel, empty in RESET.items():
    with io.open(WEB + rel, 'w', encoding='utf-8') as f:
        f.write(empty + '\n')
    print('RESET %s -> %s' % (rel, empty))

print('DONE data reset')
