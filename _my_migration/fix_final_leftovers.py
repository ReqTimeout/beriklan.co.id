#!/usr/bin/env python3
"""Final leftovers: contact line, gsc-dashboard locale, gsc-stats.json placeholder for beriklan.my."""
import io, json

WEB = "/Users/maabook/Desktop/beriklan.my/web/"

# 1. contact.astro Indonesian line
fp = WEB + 'src/pages/contact.astro'
s = io.open(fp, encoding='utf-8').read()
s = s.replace('Untuk inquiry kilat — balas dalam 1 jam (jam kerja)',
              'For urgent inquiries — replies within 1 hour (business hours)')
io.open(fp, 'w', encoding='utf-8').write(s)
print('PATCHED contact.astro')

# 2. gsc-dashboard.astro locale id-ID -> en-MY
fp = WEB + 'src/pages/gsc-dashboard.astro'
s = io.open(fp, encoding='utf-8').read()
s2 = s.replace("toLocaleString('id-ID'", "toLocaleString('en-MY'")
io.open(fp, 'w', encoding='utf-8').write(s2)
print('PATCHED gsc-dashboard.astro locale: %s' % (s != s2))

# 3. gsc-stats.json — zeroed placeholder for beriklan.my (refilled by GSC cron later)
gsc = {
    "last_pulled": "2026-07-21T00:00:00Z",
    "site": "https://beriklan.my/",
    "window": {"start": "2026-06-23", "end": "2026-07-21"},
    "totals": {"clicks": 0, "impressions": 0, "ctr": 0, "position": 0},
    "top_pages": [],
    "top_queries": [],
    "by_country": [],
    "by_device": [],
    "daily": [],
    "freshness_alerts": [],
    "low_ctr": [],
}
with io.open(WEB + 'public/data/gsc-stats.json', 'w', encoding='utf-8') as f:
    json.dump(gsc, f, ensure_ascii=False, indent=2)
print('RESET gsc-stats.json (beriklan.my placeholder)')

print('DONE final leftovers')
