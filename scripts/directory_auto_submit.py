#!/usr/bin/env python3
"""
directory_auto_submit.py — Generate ready-to-paste submission packets for each directory.

Usage:
  python3 scripts/directory_auto_submit.py
  python3 scripts/directory_auto_submit.py --start 1 --end 10
  python3 scripts/directory_auto_submit.py --high-priority-only

For each pending directory, generates a markdown file with:
  - All info needed to fill out the submission form
  - Pre-written description (varied per category to avoid duplicate content flags)
  - Direct link to the submit page
  - DR + category for prioritization

Output: web/scripts/submissions/<directory_id>.md
"""
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
DATA_FILE = ROOT / "data" / "directory-progress.json"
OUT_DIR = ROOT / "scripts" / "submissions"

# Standard agency profile
PROFILE = {
    "company_name": "Beriklan Digital Agency",
    "tagline": "Senior Performance Marketing Partner — Sejak 2016",
    "founded": "2016",
    "employees": "10-50",
    "location": "Jl. Arcamanik Endah No.76, Bandung 40195, Indonesia",
    "website": "https://beriklan.co.id",
    "email": "info@beriklan.co.id",
    "phone": "+62 81.1919.328",
    "min_project": "Rp 5.000.000",
    "hourly_rate": "Rp 250.000 - Rp 500.000 / jam",
    "services": [
        "Jasa Iklan Facebook Ads",
        "Jasa Iklan Instagram Ads",
        "Jasa Iklan TikTok Ads",
        "Jasa Iklan Google Ads (Search, Display, YouTube)",
        "Jasa Iklan YouTube",
        "Jasa Kelola Instagram & TikTok",
        "Jasa Pembuatan Website & Landing Page",
        "Jasa SEO",
    ],
    "industries": [
        "E-commerce / Toko Online",
        "Properti / Real Estate",
        "Pendidikan / Edutech",
        "Kesehatan / Klinik",
        "F&B / Restoran",
        "Fashion / Apparel",
        "Travel & Hospitality",
        "Otomotif",
        "Jasa Profesional (Konsultan, Legal)",
    ],
    "clients": "UMKM & bisnis menengah Indonesia (budget Rp 5jt - 50jt / bulan)",
    "case_study_1": "https://beriklan.co.id/blog/jasa-iklan-facebook/",
    "case_study_2": "https://beriklan.co.id/riset/laporan-industri-iklan-digital-indonesia-2026/",
}

# Description variations (avoid duplicate content)
DESCRIPTIONS = [
    # Long form (350 words)
    """Beriklan Digital Agency adalah agensi performance marketing senior berbasis Bandung yang berdiri sejak 2016. Kami membantu UMKM dan bisnis menengah Indonesia tumbuh melalui iklan digital yang terukur dan transparan — fokus pada Meta Ads (Facebook & Instagram), TikTok Ads, Google Ads (Search, Display & YouTube), YouTube Ads, SEO, dan pembuatan website & landing page.

Berbeda dari agensi yang sekadar "pasang iklan", kami bekerja seperti partner: audit campaign dulu, identifikasi akar masalah, baru susun strategi prioritas. Setiap campaign memiliki dashboard real-time yang bisa diakses klien, laporan mingguan, dan akses penuh ke akun Meta/Google/TikTok. Tidak ada black-box.

Tim kami bersertifikasi Meta Business Partner dan Google Partner, dengan pengalaman mengelola ratusan campaign dari e-commerce, properti, edutech, F&B, hingga jasa profesional. Bahasa manusia, transparansi penuh, dan hasil yang bisa dipertanggungjawabkan.

Klien kami biasanya mulai dari audit campaign gratis (15 menit via WhatsApp), lalu paket implementasi mulai Rp 5.000.000 / bulan. Respon 1 jam (jam kerja), tim online setiap hari, dan konsultan berpengalaman yang bisa menjelaskan strategi dalam bahasa sederhana — bukan jargon.""",

    # Medium form (200 words)
    """Beriklan.co.id adalah agensi digital marketing Indonesia yang fokus pada iklan berbayar (Facebook, Instagram, TikTok, Google, YouTube Ads) plus SEO dan web development. Berdiri sejak 2016 di Bandung, kami mengelola campaign untuk UMKM dan bisnis menengah dengan budget Rp 5jt–50jt/bulan.

Pendekatan kami berbasis data: audit dulu, baru eksekusi. Setiap campaign punya dashboard real-time, laporan mingguan, dan akses penuh ke akun iklan klien — tanpa black-box. Tim bersertifikasi Meta & Google Partner.

Layanan utama: Jasa Iklan Facebook Ads, Jasa Iklan Instagram, Jasa Iklan TikTok, Jasa Iklan Google Ads, SEO, Pembuatan Website & Landing Page. Klien dari e-commerce, properti, F&B, edutech, hingga jasa profesional.

Mulai dari konsultasi gratis 15 menit via WhatsApp. Respon 1 jam (jam kerja), tim online setiap hari.""",

    # Short form (100 words)
    """Agensi performance marketing Indonesia sejak 2016. Spesialis Meta Ads, TikTok Ads, Google Ads, YouTube Ads, SEO, dan web development. Berbasis Bandung, melayani UMKM dan bisnis menengah Indonesia. Pendekatan audit-first, transparan, dashboard real-time. Tim bersertifikasi Meta & Google Partner. Konsultasi awal gratis 15 menit via WhatsApp.""",
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=None)
    parser.add_argument("--high-priority-only", action="store_true")
    parser.add_argument("--category", type=str, help="Filter by category")
    args = parser.parse_args()

    data = json.loads(DATA_FILE.read_text())
    items = data.get("items", [])
    pending = [i for i in items if i.get("status") == "pending"]

    if args.high_priority_only:
        pending = [i for i in pending if i.get("priority") == "high"]
    if args.category:
        pending = [i for i in pending if i.get("category") == args.category]

    pending.sort(key=lambda x: -x.get("domain_rating", 0))

    start = args.start
    end = args.end if args.end else len(pending)
    pending = pending[start:end]

    print(f"Generating {len(pending)} submission packets...")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for idx, item in enumerate(pending):
        dr = item.get("domain_rating", 0)
        cat = item.get("category", "digital-marketing")
        # Pick description based on idx (rotate)
        desc = DESCRIPTIONS[idx % len(DESCRIPTIONS)]

        # Build markdown packet
        md = f"""# Submission Packet: {item['name']}

**Generated**: {datetime.now().isoformat(timespec='seconds')}
**Category**: {cat}
**Domain Rating**: {dr}
**Country**: {item.get('country', 'global')}

---

## 🚀 Direct Submit Link

**[{item['submit_url']}]({item['submit_url']})**

---

## 📋 Pre-filled Info (copy-paste ready)

### Company Name
```
{PROFILE['company_name']}
```

### Tagline (short)
```
{PROFILE['tagline']}
```

### Website
```
{PROFILE['website']}
```

### Founded
```
{PROFILE['founded']}
```

### Employees
```
{PROFILE['employees']}
```

### Location
```
{PROFILE['location']}
```

### Email
```
{PROFILE['email']}
```

### Phone / WhatsApp
```
{PROFILE['phone']}
```

### Min Project Size
```
{PROFILE['min_project']}
```

### Hourly Rate (if asked)
```
{PROFILE['hourly_rate']}
```

---

## 📝 Description (variation #{idx % len(DESCRIPTIONS) + 1})

```
{desc}
```

---

## 🎯 Services (multi-select)

```
""" + "\n".join(f"- {s}" for s in PROFILE['services']) + f"""
```

## 🏢 Industries Served

```
""" + "\n".join(f"- {s}" for s in PROFILE['industries']) + f"""
```

## 👥 Typical Clients
```
{PROFILE['clients']}
```

---

## 📸 Portfolio / Case Studies (link these)

- **Primary case study**: {PROFILE['case_study_1']}
- **Industry research**: {PROFILE['case_study_2']}

---

## 💡 Tips for submission

- Use the variation # chosen (don't repeat same description across directories)
- After submit, mark in `data/directory-progress.json`:
  ```json
  "status": "submitted",
  "submitted_at": "{datetime.now().isoformat(timespec='minutes')}",
  "live_url": "<check after 7-14 days>"
  ```
- If 410/404/error on submit page, mark `"status": "dead"` with notes

---

## 📝 Notes (optional)
{item.get('notes', '')}
"""

        out_path = OUT_DIR / f"{item['id']}.md"
        out_path.write_text(md)
        print(f"  ✓ {item['id']:30s} DR={dr:>3} → {out_path.name}")

    print(f"\n✓ Done. {len(pending)} packets in {OUT_DIR}")
    print("\nNext steps:")
    print(f"  1. Open each .md in {OUT_DIR}/")
    print(f"  2. Click the Submit URL, fill out the form (info is ready to copy)")
    print(f"  3. After submission, update status in data/directory-progress.json")
    print(f"  4. Run: python3 scripts/directory_tracker.py sync")

if __name__ == "__main__":
    main()