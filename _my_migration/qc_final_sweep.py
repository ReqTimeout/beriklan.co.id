#!/usr/bin/env python3
"""QC sweep: fix remaining Indonesian leftovers + remove orphaned ID-market files."""
import io, os

SRC = "/Users/maabook/Desktop/beriklan.my/web/src/"

def patch(rel, pairs):
    fp = SRC + rel
    s = io.open(fp, encoding='utf-8').read()
    orig = s
    for old, new in pairs:
        if old not in s:
            print('  !! NOT FOUND in %s: %r' % (rel, old[:70]))
            continue
        s = s.replace(old, new)
    if s != orig:
        io.open(fp, 'w', encoding='utf-8').write(s)
        print('PATCHED %s' % rel)

patch('pages/index.astro', [
    ("text=Halo%20Beriklan%2C%20saya%20ingin%20audit%20campaign%20iklan%20saya",
     "text=Hello%20Beriklan%2C%20I%27d%20like%20an%20audit%20of%20my%20ad%20campaigns"),
    ("Performance Agency · Sejak 2016", "Performance Agency · Since 2016"),
    ('tetapi <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-2 to-accent">closing sepi.</span>',
     'but <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-2 to-accent">sales stay quiet.</span>'),
    ("Tanpa kontrak minimum", "No lock-in contract"),
])

patch('pages/ad-budget-calculator.astro', [
    ("text=Halo%20Beriklan%2C%20saya%20butuh%20bantuan%20menentukan%20strategi%20iklan%20setelah%20menggunakan%20kalkulator%20budget.",
     "text=Hello%20Beriklan%2C%20I%20need%20help%20shaping%20my%20ad%20strategy%20after%20using%20the%20budget%20calculator."),
])

patch('pages/contact.astro', [
    ("text=Halo%20Beriklan%2C%20saya%20ingin%20berkonsultasi%20mengenai%20campaign%20digital%20marketing.",
     "text=Hello%20Beriklan%2C%20I%27d%20like%20to%20discuss%20my%20digital%20marketing%20campaigns."),
    ("Senin–Jumat: 09.00–18.00 MYT", "Monday–Friday: 09.00–18.00 MYT"),
    ("Sabtu: 10.00–14.00 MYT", "Saturday: 10.00–14.00 MYT"),
    ("Minggu & hari libur: tutup (respon WhatsApp tertunda)",
     "Sundays & public holidays: closed (WhatsApp replies may be delayed)"),
])

patch('pages/live-stream-viewers.astro', [
    ('Live berikutnya tidak<br/>\n                    <span class="text-accent">perlu sepi.</span>',
     'Your next live doesn\u2019t<br/>\n                    <span class="text-accent">have to be quiet.</span>'),
])

patch('pages/blog/tag/[tag].astro', [
    ("Mau diskusi spesifik soal {keyword.toLowerCase()}?",
     "Want to talk specifically about {keyword.toLowerCase()}?"),
])

patch('pages/shopee-live-viewers.astro', [("BELI SEKARANG", "BUY NOW")])
patch('pages/instagram-live-viewers.astro', [("BELI SEKARANG", "BUY NOW")])

patch('pages/blog/[slug].astro', [
    ('// "slug-yang-direfresh": "2026-07-15T10:00:00",',
     '// "refreshed-slug": "2026-07-15T10:00:00",'),
])

# Remove orphaned Indonesian-market files (no importers left)
for rel in ['components/CityContentBlock.astro', 'components/LocalSchema.astro', 'data/local-faqs.json']:
    fp = SRC + rel
    if os.path.exists(fp):
        os.remove(fp)
        print('REMOVED %s' % rel)

print('DONE qc sweep')
