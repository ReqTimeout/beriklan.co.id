#!/usr/bin/env python3
"""
Enrich city-content.json with unique per-city/service content via Groq llama-3.3-70b.

Uses cities.json local_facts as ground truth so content is locally accurate.
Single-threaded (avoids Groq rate-limit) — ~6-8 min for 129 entries.

Usage:
  python3 scripts/enrich_city_content.py            # process all missing entries
  python3 scripts/enrich_city_content.py --all      # regenerate ALL 129
  python3 scripts/enrich_city_content.py --only <route>  # single entry
"""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CITIES = os.path.join(WEB, "src", "data", "cities.json")
CONTENT = os.path.join(WEB, "src", "data", "city-content.json")
KEY_PATH = os.path.expanduser("~/.beriklan/groq-key")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

SERVICE_FOCUS = {
    "jasa-digital-marketing": "layanan full-service digital marketing (Meta Ads + Google Ads + TikTok Ads + organic content + landing page + analytics)",
    "jasa-iklan-facebook": "iklan Facebook & Instagram (Meta Ads Manager, pixel, retargeting, lookalike audience)",
    "jasa-iklan-google": "iklan Google Ads (Search, Display, YouTube via Google Ads, keyword targeting, conversion tracking)",
    "jasa-iklan-instagram": "iklan Instagram (Reels, Story, Feed, Explore, shop integration, creator collaboration)",
    "jasa-iklan-tiktok": "iklan TikTok (Spark Ads, In-Feed, TopView, FYP targeting, creator marketplace)",
    "jasa-iklan-youtube": "iklan YouTube (TrueView In-Stream, Bumper, Shorts Ads, channel placement)",
    "jasa-kelola-instagram": "manajemen Instagram organik (content calendar, reels production, community management, IG growth)",
    "jasa-kelola-tiktok": "manajemen TikTok organik (script writing, video production rutin, FYP optimization, comment management)",
    "jasa-pembuatan-landing-page": "pembuatan landing page (custom design, fast loading, mobile-optimized, A/B testing ready, integrasi Meta/Google Pixel)",
    "jasa-pembuatan-website": "pembuatan website profesional (company profile, toko online, custom CMS, SEO-friendly, mobile responsive)",
}

# City context: maps slug → display name for prompt (some slugs differ)
CITY_DISPLAY = {
    "aceh": "Banda Aceh", "bali": "Denpasar / Bali", "bandung": "Bandung",
    "batam": "Batam", "bekasi": "Bekasi", "bogor": "Bogor", "cimahi": "Cimahi",
    "denpasar": "Denpasar", "depok": "Depok", "jogja": "Yogyakarta",
    "lampung": "Bandar Lampung", "lombok": "Mataram / Lombok", "malang": "Malang",
    "medan": "Medan", "padang": "Padang", "palembang": "Palembang",
    "pontianak": "Pontianak", "semarang": "Semarang", "sidoarjo": "Sidoarjo",
    "solo": "Solo / Surakarta", "surabaya": "Surabaya", "tangerang": "Tangerang",
    "yogyakarta": "Yogyakarta",
}


def groq(prompt: str, key: str, max_retries: int = 4) -> str:
    """Single Groq call with retry + exponential backoff. Returns generated text."""
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1600,
        "temperature": 0.7,
    }).encode()
    req = urllib.request.Request(
        GROQ_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; enrich-city/1.0; +https://beriklan.co.id)",
        },
    )
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                data = json.loads(r.read())
            return data["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                # rate-limited — back off hard
                wait = 30 * (attempt + 1)
                time.sleep(wait)
                continue
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            raise
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            raise


def build_prompt(city: dict, service_slug: str) -> str:
    name = city["name"]
    focus = SERVICE_FOCUS.get(service_slug, "jasa digital marketing")
    facts = " | ".join(city.get("local_facts", []))
    return f"""Kamu copywriter senior untuk agency Beriklan.co.id (Bandung, sejak 2016). 
Tulis artikel HTML pendek (500-700 kata) untuk landing page {focus} di kota {name}, Indonesia.

Gunakan fakta lokal kota ini (jika relevan): {facts}

ATURAN KERAS (WAJIB DIPATUHI):
1. BAHASA: Indonesia formal, "Anda" (bukan "kamu"), "kami" (bukan "kita"). NO slang ("bikin", "gak", "nggak"). NO emoji marketing.
2. JANGAN klaim angka fiktif: jangan tulis "50+ klien", "rating 4.9", "ROAS 10x", atau testimoni spesifik. Fokus pada observasi & cara kerja.
3. Boleh sebut data makro (penetrasi internet, pertumbuhan e-commerce, populasi) HANYA jika masuk akal untuk kota {name}. Kalau ragu, JANGAN sebut angka spesifik.
4. PERSONA: "Senior Performance Marketing Partner" — bukan jualan, bukan over-promise.
5. STRUKTUR (ikuti persis, h2/h3 lowercase, paragraf 3-4 kalimat, list dengan <ul><li>):

<h2>Mengapa Bisnis di {name} Butuh {focus.split(' (')[0].title()}</h2>
<p>3-4 kalimat konteks kenapa {name} pasar relevan. Sebut industri dominan, perilaku konsumen, dan kenapa digital channel penting.</p>

<h2>Tantangan & Kesalahan Umum di {name}</h2>
<p>2-3 kalimat observasi tantangan spesifik kota (kompetisi, perilaku audience, gap pengetahuan).</p>
<ul>
<li>Bullet 1: kesalahan / tantangan konkret (3-5 kata)</li>
<li>Bullet 2</li>
<li>Bullet 3</li>
<li>Bullet 4</li>
</ul>

<h2>Cara Kerja Tim Beriklan untuk Bisnis di {name}</h2>
<p>Lead 1-2 kalimat.</p>
<ul>
<li><strong>Riset & Strategi Lokal:</strong> 1 kalimat menjelaskan riset spesifik untuk {name}.</li>
<li><strong>Setup & Eksekusi:</strong> 1 kalimat teknis setup channel.</li>
<li><strong>Optimasi & Pelaporan:</strong> 1 kalimat siklus optimasi dan laporan.</li>
<li><strong>Kolaborasi Jangka Panjang:</strong> 1 kalimat komitmen partnership.</li>
</ul>

<h2>Pertanyaan yang Sering Diajukan</h2>
<h3>Berapa biaya untuk bisnis di {name}?</h3>
<p>Jawaban 2-3 kalimat: fee manajemen dari Rp 2.5jt/bulan + ad spend terpisah ke platform. Tidak ada garansi nominal.</p>
<h3>Berapa lama setup sampai iklan tayang?</h3>
<p>1 kalimat: 3-7 hari kerja setelah akses akun diberikan.</p>
<h3>Apakah tim lokal {name}?</h3>
<p>1 kalimat: tim Beriklan berbasis Bandung, manage campaign remote + onsite sesuai kebutuhan.</p>
<h3>Bagaimana laporan & akses akun?</h3>
<p>1 kalimat: laporan mingguan bahasa manusia + akses penuh akun Meta/Google/TikTok di sisi klien.</p>

6. OUTPUT: Hanya HTML body (h2/h3/p/ul/li/strong), tanpa <html>, tanpa markdown ```. Langsung tag pembuka. Akhiri dengan paragraf penutup natural.
7. FOKUS KOTA: Minimal 6-8 penyebutan "{name}" secara natural di seluruh artikel (di heading, body, bullet).
8. E-E-A-T: Tunjukkan expertise (sebut audit channel, pixel, attribution, geo-targeting) tanpa over-claim."""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="regenerate all 129")
    ap.add_argument("--only", help="single route like jasa-iklan-facebook/medan/")
    args = ap.parse_args()

    if not os.path.exists(KEY_PATH):
        print(f"ERROR: {KEY_PATH} not found")
        sys.exit(1)
    key = open(KEY_PATH).read().strip()

    cities_list = json.load(open(CITIES))
    city_by_slug = {c["slug"]: c for c in cities_list}
    city_by_name_lower = {c["name"].lower(): c for c in cities_list}

    content = json.load(open(CONTENT)) if os.path.exists(CONTENT) else {}

    if args.only:
        routes = [args.only]
    elif args.all:
        # determine all routes from city-content keys
        routes = sorted(content.keys())
    else:
        # default: regenerate all (more useful)
        routes = sorted(content.keys())

    print(f"Total routes to process: {len(routes)}")
    ok = 0
    fail = 0
    t0 = time.time()
    for i, route in enumerate(routes, 1):
        parts = route.strip("/").split("/")
        if len(parts) < 2:
            continue
        service_slug, city_slug = parts[0], parts[1]
        # resolve city
        city = city_by_slug.get(city_slug) or city_by_name_lower.get(city_slug)
        if not city:
            # try display name
            display = CITY_DISPLAY.get(city_slug)
            if display:
                city = city_by_name_lower.get(display.lower().split("/")[0].strip())
        if not city:
            print(f"[{i}/{len(routes)}] SKIP {route} — city not found")
            fail += 1
            continue
        prompt = build_prompt(city, service_slug)
        try:
            html = groq(prompt, key)
            # strip accidental code fences
            html = html.replace("```html", "").replace("```", "").strip()
            content[route] = html
            ok += 1
            elapsed = time.time() - t0
            print(f"[{i}/{len(routes)}] OK {route}  ({elapsed:.0f}s, avg {elapsed/i:.1f}s/it)")
            # checkpoint every 10
            if ok % 10 == 0:
                json.dump(content, open(CONTENT, "w"), ensure_ascii=False, indent=1)
        except Exception as e:
            print(f"[{i}/{len(routes)}] FAIL {route}: {e}")
            fail += 1
        # throttle to ~7-8 req/min (sustained safe rate for free tier)
        time.sleep(7)
    json.dump(content, open(CONTENT, "w"), ensure_ascii=False, indent=1)
    print(f"\nDONE: ok={ok} fail={fail} total={time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
