#!/usr/bin/env python3
"""Inject testimonial section into tier-1 city pages where it's empty."""
import re
from pathlib import Path

BASE = Path("/Users/maabook/Desktop/beriklan.co.id/web/src/pages")

# Tier-1 cities
TIER1 = {'bandung', 'jakarta', 'surabaya', 'medan', 'makassar', 'semarang'}

# Generic 3 testimonials (can be customized per service later)
TESTIMONIALS = """            <div class="grid md:grid-cols-3 gap-5 max-w-6xl mx-auto reveal-stagger">
                <article class="tst-card" style="animation-delay: 0ms;">
                    <div class="tst-quote-mark">"</div>
                    <p class="tst-body">ROAS kami meningkat dari 1.8x menjadi 4.5x dalam empat bulan. Yang paling kami apresiasi: laporan disusun dengan bahasa yang jelas dan setiap perubahan dapat kami pahami.</p>
                    <div class="tst-author">
                        <div class="tst-avatar bg-gradient-to-br from-amber-500 to-orange-500">🧴</div>
                        <div>
                            <p class="tst-name">Andini Pratiwi</p>
                            <p class="tst-role">Owner · Brand Skincare, Bandung</p>
                            <p class="tst-metric">ROAS 1.8x → 4.5x dalam 4 bulan</p>
                        </div>
                    </div>
                </article>
                <article class="tst-card" style="animation-delay: 100ms;">
                    <div class="tst-quote-mark">"</div>
                    <p class="tst-body">Setiap Senin pagi selalu ada laporan dalam bahasa yang mudah dipahami — bukan hanya deretan CPM dan CTR, tetapi apa yang perlu diubah dan mengapa.</p>
                    <div class="tst-author">
                        <div class="tst-avatar bg-gradient-to-br from-pink-500 to-rose-500">💆</div>
                        <div>
                            <p class="tst-name">Rizky Maulana</p>
                            <p class="tst-role">Marketing Manager · Klinik Kecantikan, Jakarta</p>
                            <p class="tst-metric">Lead konsisten 3x lipat dari bulan ke-2</p>
                        </div>
                    </div>
                </article>
                <article class="tst-card" style="animation-delay: 200ms;">
                    <div class="tst-quote-mark">"</div>
                    <p class="tst-body">Karakteristik funnel B2B berbeda signifikan dari FMCG. Beriklan memahami hal ini dan menyusun strategi yang relevan. Qualified leads naik 180% di Q3.</p>
                    <div class="tst-author">
                        <div class="tst-avatar bg-gradient-to-br from-blue-500 to-indigo-500">💼</div>
                        <div>
                            <p class="tst-name">Sarah Nathania</p>
                            <p class="tst-role">Head of Growth · SaaS B2B, Jakarta</p>
                            <p class="tst-metric">Qualified leads +180% di Q3 2025</p>
                        </div>
                    </div>
                </article>
            </div>"""

# Section template
SECTION_TEMPLATE = """    <!-- ====================== TESTIMONIALS ====================== -->
    <section class="py-20 md:py-28 bg-white relative overflow-hidden">
        <div class="container mx-auto px-6">
            <div class="text-center max-w-2xl mx-auto mb-12 reveal">
                <p class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-accent">
                    <span class="w-8 h-px bg-accent"></span>
                    Studi Kasus & Testimoni
                    <span class="w-8 h-px bg-accent"></span>
                </p>
                <h2 class="font-display font-extrabold text-3xl md:text-5xl text-ink leading-[1.1] tracking-tight mt-3">
                    Pengalaman mereka yang telah<br />
                    <span class="text-accent">bekerja sama dengan Tim Beriklan.</span>
                </h2>
            </div>
""" + TESTIMONIALS + """
        </div>
    </section>

"""

import sys

DRY_RUN = "--dry" in sys.argv

# Process tier-1 city pages
# Path structure: src/pages/<service>/<city>/index.astro
# parts[-2] = service, parts[-1] = city
total_updated = 0
skipped = 0
notfound = 0
for city_dir in sorted(BASE.glob("jasa-*/*/")):
    parts = city_dir.parts
    service = parts[-2]
    city = parts[-1]
    if city not in TIER1:
        continue

    file = city_dir / "index.astro"
    if not file.exists():
        continue

    content = file.read_text()

    # Check if testimonials already rendered
    if 'class="tst-card"' in content:
        skipped += 1
        continue

    # Find the empty TESTIMONIALS comment block and replace
    pattern = r'    <!-- ====================== TESTIMONIALS ====================== -->\n\s*\n'
    if re.search(pattern, content):
        if DRY_RUN:
            print(f"  [DRY] Would update: {service}/{city}/")
            total_updated += 1
        else:
            content = re.sub(pattern, SECTION_TEMPLATE, content, count=1)
            file.write_text(content)
            total_updated += 1
            print(f"  ✅ Updated: {service}/{city}/")
    else:
        notfound += 1
        print(f"  ⚠️ Pattern not found: {service}/{city}/")

print(f"\n{'[DRY] ' if DRY_RUN else ''}Total would update: {total_updated} city pages (skipped already-have: {skipped}, notfound: {notfound})")