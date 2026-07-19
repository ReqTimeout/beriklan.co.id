#!/usr/bin/env python3
"""
gen_city_content.py — generate truthful city-content.json entries for the
missing Indonesian city x service combinations (jakarta, makassar, sidoarjo).

Uses ONLY real data from src/data/cities.json (city name, province, umkm_count,
local_facts). No fabricated growth percentages or case studies. The generated
HTML follows the same H2/H3/ul structure as the existing AI-written entries so
CityContentBlock renders it correctly (TOC, callout, related links).

This is additive: it only fills keys that are MISSING. Existing entries are kept.

Usage:
  python3 scripts/gen_city_content.py            # fill missing, write city-content.json
  python3 scripts/gen_city_content.py --dry      # print what would be added
"""
import argparse
import json
import os
import re

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CITIES = os.path.join(WEB, "src/data/cities.json")
CONTENT = os.path.join(WEB, "src/data/city-content.json")

SERVICES = [
    "jasa-digital-marketing", "jasa-iklan-facebook", "jasa-iklan-instagram",
    "jasa-iklan-tiktok", "jasa-iklan-google", "jasa-iklan-youtube",
    "jasa-kelola-instagram", "jasa-kelola-tiktok",
    "jasa-pembuatan-website", "jasa-pembuatan-landing-page",
]

SERVICE_LABEL = {
    "jasa-digital-marketing": "Digital Marketing",
    "jasa-iklan-facebook": "Iklan Facebook",
    "jasa-iklan-instagram": "Iklan Instagram",
    "jasa-iklan-tiktok": "Iklan TikTok",
    "jasa-iklan-google": "Iklan Google Ads",
    "jasa-iklan-youtube": "Iklan YouTube",
    "jasa-kelola-instagram": "Kelola Instagram",
    "jasa-kelola-tiktok": "Kelola TikTok",
    "jasa-pembuatan-website": "Pembuatan Website",
    "jasa-pembuatan-landing-page": "Pembuatan Landing Page",
}

AD_SERVICES = {
    "jasa-iklan-facebook", "jasa-iklan-instagram", "jasa-iklan-tiktok",
    "jasa-iklan-google", "jasa-iklan-youtube",
}
ORGANIC_SERVICES = {"jasa-kelola-instagram", "jasa-kelola-tiktok"}
BUILD_SERVICES = {"jasa-pembuatan-website", "jasa-pembuatan-landing-page"}


def esc(s: str) -> str:
    return s


def build_html(city: dict, service: str) -> str:
    name = city["name"]
    prov = city.get("province") or "Indonesia"
    umkm = city.get("umkm_count") or 0
    facts = city.get("local_facts") or []
    label = SERVICE_LABEL[service]

    # Truthful opening sentence — uses real umkm_count and local_facts only.
    umkm_txt = f"tercatat memiliki sekitar {umkm:,} UMKM" if umkm else "memiliki ekosistem UMKM yang aktif"
    fact_line = ""
    if facts:
        fact_line = " " + " ".join(facts) + "."

    if service == "jasa-digital-marketing":
        h1 = f"Mengapa Bisnis di {name} Butuh Layanan Digital Marketing Terpadu"
        opening = (
            f"{name}, {prov}, {umkm_txt}.{fact_line} "
            f"Dengan banyaknya pelaku usaha lokal, bisnis yang mengelola campaign secara "
            f"terukur di berbagai kanal (Meta, Google, TikTok, YouTube) memiliki keunggulan "
            f"bersaing dalam menjangkau audiens yang tepat."
        )
        work_items = [
            ("Audit & Strategi:", f"Kami memetakan kondisi bisnis di {name} dan menyusun prioritas kanal berdasarkan objective."),
            ("Eksekusi Multi-Kanal:", "Pengelolaan iklan berjalan terkoordinasi agar saling menguatkan, bukan berjalan sendiri-sendiri."),
            ("Optimasi & Laporan:", "Performa dipantau rutin dengan laporan mingguan yang transparan dan dapat dipertanggungjawabkan."),
            ("Iterasi Berkelanjutan:", "Strategi disesuaikan tiap periode berdasarkan data, bukan asumsi."),
        ]
    elif service in AD_SERVICES:
        plat = label.replace("Iklan ", "")
        h1 = f"Mengapa Bisnis di {name} Butuh {label}"
        opening = (
            f"{name}, {prov}, {umkm_txt}.{fact_line} "
            f"Iklan {plat} memungkinkan bisnis lokal menjangkau audiens yang relevan dengan "
            f"targeting presisi, sehingga budget iklan bekerja lebih efisien untuk menghasilkan "
            f"lead dan penjualan yang terukur."
        )
        work_items = [
            ("Riset & Strategi Lokal:", f"Kami melakukan riset spesifik untuk pasar {name} — perilaku audiens, kompetitor, dan keyword relevan."),
            ("Setup & Eksekusi:", f"Pengaturan campaign {plat} dilakukan dengan target audiens, budget, dan creative yang selaras."),
            ("Optimasi & Pelaporan:", "Performa dioptimasi rutin dan dilaporkan secara transparan (mingguan)."),
            ("Kolaborasi Jangka Panjang:", "Kami bekerja bersama bisnis Anda agar iklan tetap efektif seiring perubahan pasar."),
        ]
    elif service in ORGANIC_SERVICES:
        plat = label.replace("Kelola ", "")
        h1 = f"Mengapa Bisnis di {name} Butuh Jasa {label}"
        opening = (
            f"{name}, {prov}, {umkm_txt}.{fact_line} "
            f"Manajemen {plat} yang konsisten membantu bisnis lokal membangun kehadiran organik, "
            f"engagement audiens yang berkualitas, dan trust jangka panjang tanpa bergantung penuh pada ad spend."
        )
        work_items = [
            ("Brief & Audit:", f"Diskusi untuk memahami brand voice dan objective bisnis di {name}."),
            ("Content Plan:", "Penyusunan content calendar, caption, dan asset sesuai ritme niche Anda."),
            ("Eksekusi & Community:", "Posting terjadwal, serta reply DM/comment dengan tone of voice brand."),
            ("Review & Pivot:", "Laporan berkala dengan insight actionable untuk penyesuaian strategi."),
        ]
    else:  # build
        prod = "website profesional" if service == "jasa-pembuatan-website" else "landing page konversi"
        h1 = f"Mengapa Bisnis di {name} Butuh Jasa {label}"
        opening = (
            f"{name}, {prov}, {umkm_txt}.{fact_line} "
            f"{prod.title()} menjadi fondasi penting untuk bisnis yang ingin tampil kredibel di "
            f"mesin pencari dan mengonversi trafik iklan menjadi pelanggan secara konsisten."
        )
        work_items = [
            ("Brief & Wireframe:", f"Diskusi tujuan dan struktur {prod} untuk bisnis di {name}."),
            ("Design & Build:", "Pengembangan dengan desain custom, mobile responsive, dan tracking terpasang."),
            ("Testing & Launch:", "Uji lintas peramban, kecepatan, dan keamanan sebelum peluncuran."),
            ("Support:", "Bantuan teknis dan pembaruan konten secara berkala."),
        ]

    # Common challenges (generic, honest — no fabricated specifics)
    challenges = [
        f"Bisnis di {name} sering kesulitan menyusun strategi iklan yang terukur dan konsisten.",
        "Targeting yang melebar membuat budget iklan tidak efisien menghasilkan konversi.",
        "Creative yang tidak selaras dengan audiens lokal menurunkan tingkat keterlibatan.",
        "Tanpa laporan rutin, sulit mengetahui channel mana yang benar-benar menghasilkan ROI.",
    ]

    work_html = "\n".join(
        f"<li><strong>{t}</strong> {d}</li>" for t, d in work_items
    )
    chal_html = "\n".join(f"<li>{c}</li>" for c in challenges)

    faq = (
        f"<h3>Berapa biaya layanan {label} di {name}?</h3>\n"
        f"<p>Biaya disesuaikan dengan paket dan ruang lingkup kebutuhan bisnis Anda di {name}. "
        f"Konsultasi awal 15 menit kami sediakan gratis untuk menentukan rekomendasi yang tepat.</p>\n"
        f"<h3>Apakah cocok untuk UMKM di {name}?</h3>\n"
        f"<p>Ya. Dengan ekosistem UMKM yang aktif di {name}, layanan ini dirancang agar bisnis "
        f"dengan budget menengah dapat menjalankan campaign yang terukur dan transparan.</p>\n"
        f"<h3>Bagaimana proses onboarding?</h3>\n"
        f"<p>Dimulai dengan audit singkat, penyusunan strategi, lalu eksekusi dan pelaporan rutin "
        f"sesuai kesepakatan.</p>"
    )

    html = (
        f"<h2>{h1}</h2>\n"
        f"<p>{opening}</p>\n\n"
        f"<h2>Tantangan & Kesalahan Umum di {name}</h2>\n"
        f"<p>Banyak bisnis lokal menghadapi hambatan serupa dalam memaksimalkan pemasaran digital. "
        f"Berikut beberapa di antaranya:</p>\n"
        f"<ul>\n{chal_html}\n</ul>\n\n"
        f"<h2>Cara Kerja Tim Beriklan untuk Bisnis di {name}</h2>\n"
        f"<p>Untuk membantu bisnis di {name}, tim kami bekerja dengan pendekatan berbasis data dan transparan:</p>\n"
        f"<ul>\n{work_html}\n</ul>\n\n"
        f"<h2>Pertanyaan yang Sering Diajukan</h2>\n"
        f"{faq}\n"
    )
    return html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    cities = json.load(open(CITIES, encoding="utf-8"))
    city_by_slug = {c["slug"]: c for c in cities}
    content = json.load(open(CONTENT, encoding="utf-8"))

    # Cities to fill (real Indonesian cities missing from the 23-city list)
    FILL = ["jakarta", "makassar", "sidoarjo"]

    plan = []
    for city_slug in FILL:
        city = city_by_slug.get(city_slug)
        if not city:
            print(f"SKIP city not in cities.json: {city_slug}")
            continue
        for svc in SERVICES:
            key = f"{svc}/{city_slug}/"
            if key in content:
                continue
            plan.append((svc, city_slug, key))

    print(f"Missing entries to generate: {len(plan)}")
    if args.dry:
        for svc, city_slug, key in plan[:6]:
            print(f"  would add: {key}")
        return

    for svc, city_slug, key in plan:
        content[key] = build_html(city_by_slug[city_slug], svc)

    json.dump(content, open(CONTENT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Wrote {len(plan)} new entries to city-content.json")


if __name__ == "__main__":
    main()
