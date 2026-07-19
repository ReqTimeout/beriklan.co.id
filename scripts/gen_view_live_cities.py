#!/usr/bin/env python3
"""
Generate per-city pages for jasa-view-live (5 platforms x top cities).

Clones src/pages/jasa-view-live/{platform}/index.astro as template,
then per city:
- title: "... di {City}"
- description: mention city
- canonical: /jasa-view-live/{platform}/{city}/
- H1: add " di {City}" to first span
- waLink: add city context
- Adds LocalSchema-ish city context paragraph after hero sub (minimal)

Usage:
  python3 scripts/gen_view_live_cities.py            # generate all
  python3 scripts/gen_view_live_cities.py --dry      # print plan only
"""
import argparse
import json
import os
import re

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(WEB, "src/pages/jasa-view-live")

PLATFORMS = {
    "tiktok": "TikTok",
    "instagram": "Instagram",
    "youtube": "YouTube",
    "shopee": "Shopee",
    "twitch": "Twitch",
}

CITIES = [
    ("jakarta", "Jakarta"), ("bandung", "Bandung"), ("surabaya", "Surabaya"),
    ("yogyakarta", "Yogyakarta"), ("semarang", "Semarang"), ("medan", "Medan"),
    ("makassar", "Makassar"), ("denpasar", "Denpasar"), ("bekasi", "Bekasi"),
    ("depok", "Depok"), ("tangerang", "Tangerang"), ("bogor", "Bogor"),
    ("malang", "Malang"), ("batam", "Batam"), ("palembang", "Palembang"),
    ("pekanbaru", "Pekanbaru"), ("sidoarjo", "Sidoarjo"), ("solo", "Solo"),
    ("padang", "Padang"), ("manado", "Manado"), ("pontianak", "Pontianak"),
    ("banjarmasin", "Banjarmasin"), ("lampung", "Lampung"), ("jambi", "Jambi"),
    ("cimahi", "Cimahi"), ("balikpapan", "Balikpapan"),
]


def generate(platform, plat_name, city_slug, city_name, template):
    src = template

    # 1) Title tag
    src = re.sub(
        r'title="Jasa View Live ' + re.escape(plat_name) + r' \| ([^"]+)"',
        f'title="Jasa View Live {plat_name} di {city_name} | \\1"',
        src, count=1,
    )

    # 2) Meta description — inject city after "TikTok " / platform name first occurrence inside description
    def desc_repl(m):
        return f'description="Boost viewers live streaming {plat_name} di {city_name} agar FYP algorithm notice live Anda. Real account, no bot, aman. Mulai Rp 12.000."'
    src = re.sub(r'description="[^"]*"', desc_repl, src, count=1)

    # 3) Canonical
    src = src.replace(
        f'canonical="https://beriklan.co.id/jasa-view-live/{platform}/"',
        f'canonical="https://beriklan.co.id/jasa-view-live/{platform}/{city_slug}/"',
        1,
    )

    # 4) waLink — add city mention
    src = re.sub(
        r'const waLink = "https://wa\.me/62811919328\?text=[^"]+"',
        f'const waLink = "https://wa.me/62811919328?text=Halo%20Beriklan%2C%20saya%20tertarik%20dengan%20jasa%20view%20live%20{plat_name}%20di%20{city_name}.%20Mohon%20info%20paket%20dan%20harga."',
        src, count=1,
    )

    # 5) H1 first span — append " di {City}" style: inject city into first anim-fade-up span
    src = re.sub(
        r'(<span class="anim-fade-up">)([^<]+)(</span>)',
        lambda m: m.group(1) + m.group(2).rstrip() + f" — {city_name}" + m.group(3),
        src, count=1,
    )

    # 6) Hero subcopy: append local sentence
    src = re.sub(
        r"(tanpa flag, tanpa bot, tanpa risiko shadow ban\.)",
        f"\\1 Untuk seller dan streamer di {city_name}, tim kami standby support lokal Bahasa Indonesia.",
        src, count=1,
    )

    # Fix relative import depth (city pages are 1 level deeper)
    src = src.replace("from '../../../", "from '../../../../")
    return src


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    created = 0
    for platform, plat_name in PLATFORMS.items():
        tpl_path = os.path.join(PAGES, platform, "index.astro")
        if not os.path.exists(tpl_path):
            print(f"  ! skip {platform}: template missing")
            continue
        template = open(tpl_path).read()

        for city_slug, city_name in CITIES:
            out_dir = os.path.join(PAGES, platform, city_slug)
            out_path = os.path.join(out_dir, "index.astro")
            if os.path.exists(out_path):
                continue
            if args.dry:
                print(f"  would create /jasa-view-live/{platform}/{city_slug}/")
                continue
            os.makedirs(out_dir, exist_ok=True)
            content = generate(platform, plat_name, city_slug, city_name, template)
            open(out_path, "w").write(content)
            created += 1

    print(f"Created {created} city pages" if not args.dry else "dry-run done")


if __name__ == "__main__":
    main()
