#!/usr/bin/env python3
"""
Retrofit generated blog posts with contextual internal-link CTA block.

Every generated post (posts.json where generated=true) gets a block appended
linking to: service money page, city money page (if city), WhatsApp CTA.
Idempotent via marker comment <!-- internal-cta -->.

Usage: python3 scripts/retrofit_internal_links.py [--dry]
"""
import json
import os
import sys
from urllib.parse import quote

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(WEB, "src", "data", "posts.json")

MARKER = "<!-- internal-cta -->"

SERVICE_NAMES = {
    "jasa-digital-marketing": "Jasa Digital Marketing",
    "jasa-iklan-facebook": "Jasa Iklan Facebook Ads",
    "jasa-iklan-instagram": "Jasa Iklan Instagram",
    "jasa-iklan-tiktok": "Jasa Iklan TikTok Ads",
    "jasa-iklan-google": "Jasa Iklan Google Ads",
    "jasa-iklan-youtube": "Jasa Iklan YouTube Ads",
    "jasa-kelola-instagram": "Jasa Kelola Instagram",
    "jasa-kelola-tiktok": "Jasa Kelola TikTok",
    "jasa-pembuatan-website": "Jasa Pembuatan Website",
    "jasa-pembuatan-landing-page": "Jasa Pembuatan Landing Page",
    "jasa-view-live": "Jasa View Live",
}

CITY_NORM = {
    "jogja": "yogyakarta", "yogya": "yogyakarta", "bali": "denpasar",
}
CITY_TITLE = {
    "jakarta": "Jakarta", "bandung": "Bandung", "surabaya": "Surabaya",
    "yogyakarta": "Yogyakarta", "semarang": "Semarang", "medan": "Medan",
    "makassar": "Makassar", "denpasar": "Denpasar", "bekasi": "Bekasi",
    "depok": "Depok", "tangerang": "Tangerang", "bogor": "Bogor",
    "malang": "Malang", "batam": "Batam", "palembang": "Palembang",
    "pekanbaru": "Pekanbaru", "sidoarjo": "Sidoarjo", "solo": "Solo",
    "padang": "Padang", "manado": "Manado", "pontianak": "Pontianak",
    "banjarmasin": "Banjarmasin", "lampung": "Lampung", "jambi": "Jambi",
    "cimahi": "Cimahi", "balikpapan": "Balikpapan", "aceh": "Aceh",
    "samarinda": "Samarinda",
}

# cities that have actual service city pages (mirror src/pages/jasa-iklan-facebook/)
VALID_CITY_PAGES = set(CITY_TITLE.keys())


def build_block(post):
    svc = post.get("service") or "jasa-digital-marketing"
    svc_name = SERVICE_NAMES.get(svc, "Jasa Digital Marketing")
    city = (post.get("city") or "").strip().lower()
    city = CITY_NORM.get(city, city)
    city_name = CITY_TITLE.get(city)

    kw = post.get("title") or svc_name
    wa_text = quote(f"Halo Beriklan, saya membaca artikel \"{kw[:60]}\" dan tertarik dengan {svc_name}. Mohon info lebih lanjut.")
    wa = f"https://wa.me/62811919328?text={wa_text}"

    items = [f'<li><a href="/{svc}/">Lihat paket {svc_name} — harga &amp; fitur lengkap</a></li>']
    if city_name and city in VALID_CITY_PAGES:
        items.insert(0, f'<li><a href="/{svc}/{city}/">{svc_name} di {city_name} — tim lokal, respon cepat</a></li>')

    heading = f"Butuh {svc_name} di {city_name}?" if city_name else f"Butuh {svc_name}?"
    return f"""
{MARKER}
<hr/>
<h2>{heading}</h2>
<p>Tim Beriklan mengelola campaign sejak 2016 — transparan, terukur, dengan laporan mingguan dan akses penuh ke akun Anda. Sesi konsultasi awal 15 menit, gratis.</p>
<ul>
{chr(10).join(items)}
<li><a href="{wa}" rel="nofollow">Konsultasi via WhatsApp — respon dalam 1 jam (jam kerja)</a></li>
</ul>"""


def main():
    dry = "--dry" in sys.argv
    posts = json.load(open(POSTS))
    changed = 0
    for p in posts:
        if not p.get("generated"):
            continue
        content = p.get("content") or ""
        if MARKER in content:
            continue
        block = build_block(p)
        if dry:
            changed += 1
            if changed <= 3:
                print(f"--- would append to {p['slug']} ---")
                print(block[:300])
            continue
        p["content"] = content.rstrip() + "\n" + block
        changed += 1

    print(f"{'[dry] ' if dry else ''}retrofitted {changed} posts")
    if not dry and changed:
        json.dump(posts, open(POSTS, "w"), ensure_ascii=False, indent=2)
        print("posts.json saved")


if __name__ == "__main__":
    main()
