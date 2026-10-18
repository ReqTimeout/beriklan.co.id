#!/usr/bin/env python3
"""Fase 1 mekanis untuk beriklan.my:
1. Hapus ~390 halaman kota Indonesia (regenerate di Fase 2 dgn kota MY)
2. Rename route ke slug English (flat untuk live viewers)
3. Update semua referensi slug + domain di src & scripts
4. Timezone WIB -> MYT, Tokopedia -> Lazada
"""
import os, re, shutil, sys

ROOT = "/Users/maabook/Desktop/beriklan.my"
WEB = os.path.join(ROOT, "web")
PAGES = os.path.join(WEB, "src", "pages")

# ── 1. Hapus halaman kota ID (static generated) ─────────────────────────────
SERVICE_DIRS = [
    "jasa-digital-marketing", "jasa-iklan-facebook", "jasa-iklan-google",
    "jasa-iklan-instagram", "jasa-iklan-tiktok", "jasa-iklan-youtube",
    "jasa-kelola-instagram", "jasa-kelola-tiktok",
    "jasa-pembuatan-landing-page", "jasa-pembuatan-website",
]
removed = 0
for d in SERVICE_DIRS:
    p = os.path.join(PAGES, d)
    if os.path.isdir(p):
        removed += sum(len(fs) for _, _, fs in os.walk(p))
        shutil.rmtree(p)

# view-live: simpan index.astro per platform, hapus subdir kota
VL = os.path.join(PAGES, "jasa-view-live")
platform_files = {}  # platform -> path index.astro content saved
if os.path.isdir(VL):
    # overview
    ov = os.path.join(VL, "index.astro")
    if os.path.exists(ov):
        platform_files["live-stream-viewers"] = open(ov, encoding="utf-8").read()
    for plat in ["tiktok", "shopee", "instagram", "youtube", "twitch"]:
        pf = os.path.join(VL, plat, "index.astro")
        if os.path.exists(pf):
            platform_files[f"{plat}-live-viewers"] = open(pf, encoding="utf-8").read()
    removed += sum(len(fs) for _, _, fs in os.walk(VL)) - len(platform_files)
    shutil.rmtree(VL)

# tulis flat: /live-stream-viewers.astro, /tiktok-live-viewers.astro dst.
# path import berubah dari ../../ (atau ../../../) ke ../ karena pindah ke root pages
for slug, content in platform_files.items():
    content = content.replace("../../../", "\x00TMP\x00").replace("../../", "../").replace("\x00TMP\x00", "../")
    with open(os.path.join(PAGES, f"{slug}.astro"), "w", encoding="utf-8") as f:
        f.write(content)

print(f"[1] halaman kota ID dihapus: ~{removed} file; live-viewer flat: {sorted(platform_files)}")

# ── 2. Rename route root .astro + dir harga-iklan ───────────────────────────
RENAME_FILES = {
    "jasa-digital-marketing.astro": "digital-marketing-agency.astro",
    "jasa-iklan-facebook.astro": "facebook-ads-management.astro",
    "jasa-iklan-instagram.astro": "instagram-ads-management.astro",
    "jasa-iklan-google.astro": "google-ads-management.astro",
    "jasa-iklan-tiktok.astro": "tiktok-ads-management.astro",
    "jasa-iklan-youtube.astro": "youtube-ads-management.astro",
    "jasa-kelola-instagram.astro": "instagram-management.astro",
    "jasa-kelola-tiktok.astro": "tiktok-management.astro",
    "jasa-pembuatan-website.astro": "website-development.astro",
    "jasa-pembuatan-landing-page.astro": "landing-page-design.astro",
    "kalkulator-budget-iklan.astro": "ad-budget-calculator.astro",
    "kalkulator-roas.astro": "roas-calculator.astro",
    "kalkulator-roi.astro": "roi-calculator.astro",
    "tentang-kami.astro": "about-us.astro",
    "kontak.astro": "contact.astro",
    "metodologi.astro": "methodology.astro",
    "klien.astro": "clients.astro",
}
for old, new in RENAME_FILES.items():
    op = os.path.join(PAGES, old)
    if os.path.exists(op):
        os.rename(op, os.path.join(PAGES, new))
RENAME_DIRS = {
    "harga-iklan-facebook": "facebook-ads-cost",
    "harga-iklan-google": "google-ads-cost",
    "harga-iklan-instagram": "instagram-ads-cost",
    "harga-iklan-tiktok": "tiktok-ads-cost",
    "harga-iklan-youtube": "youtube-ads-cost",
    "riset": "research",
}
for old, new in RENAME_DIRS.items():
    op = os.path.join(PAGES, old)
    if os.path.isdir(op):
        os.rename(op, os.path.join(PAGES, new))
print("[2] rename route selesai:", sorted(os.listdir(PAGES)))

# ── 3. Update referensi slug + domain + timezone + Tokopedia ────────────────
# urutan: path spesifik dulu, baru token pendek
SLUG_MAP = [
    ("jasa-view-live/tiktok", "tiktok-live-viewers"),
    ("jasa-view-live/shopee", "shopee-live-viewers"),
    ("jasa-view-live/instagram", "instagram-live-viewers"),
    ("jasa-view-live/youtube", "youtube-live-viewers"),
    ("jasa-view-live/twitch", "twitch-live-viewers"),
    ("jasa-view-live", "live-stream-viewers"),
    ("jasa-pembuatan-landing-page", "landing-page-design"),
    ("jasa-pembuatan-website", "website-development"),
    ("jasa-digital-marketing", "digital-marketing-agency"),
    ("jasa-kelola-instagram", "instagram-management"),
    ("jasa-kelola-tiktok", "tiktok-management"),
    ("jasa-iklan-facebook", "facebook-ads-management"),
    ("jasa-iklan-instagram", "instagram-ads-management"),
    ("jasa-iklan-google", "google-ads-management"),
    ("jasa-iklan-tiktok", "tiktok-ads-management"),
    ("jasa-iklan-youtube", "youtube-ads-management"),
    ("harga-iklan-facebook", "facebook-ads-cost"),
    ("harga-iklan-google", "google-ads-cost"),
    ("harga-iklan-instagram", "instagram-ads-cost"),
    ("harga-iklan-tiktok", "tiktok-ads-cost"),
    ("harga-iklan-youtube", "youtube-ads-cost"),
    ("kalkulator-budget-iklan", "ad-budget-calculator"),
    ("kalkulator-roas", "roas-calculator"),
    ("kalkulator-roi", "roi-calculator"),
    ("tentang-kami", "about-us"),
]
# slug pendek ambigu: hanya ganti dalam konteks path /xxx/ atau /xxx"
SHORT_SLUGS = [("kontak", "contact"), ("klien", "clients"), ("metodologi", "methodology"), ("riset", "research")]

DOMAIN_MAP = [
    ("https://www.beriklan.co.id", "https://beriklan.my"),
    ("https://beriklan.co.id", "https://beriklan.my"),
    ("www.beriklan.co.id", "beriklan.my"),
    ("beriklan.co.id", "beriklan.my"),
]
MISC_MAP = [
    ("Tokopedia", "Lazada"), ("tokopedia", "lazada"),
    ("Asia/Jakarta", "Asia/Kuala_Lumpur"),
    ("7 * 3600 * 1000", "8 * 3600 * 1000"),
    ("7*3600*1000", "8*3600*1000"),
    ("hours=7", "hours=8"),
    ("WIB", "MYT"),
]

EXTS = {".astro", ".svelte", ".js", ".mjs", ".cjs", ".ts", ".json", ".jsonc", ".py", ".md", ".txt", ".xml", ".html", ".css"}
SKIP_FILES = {"worker-entry.js"}  # worker = Fase 4
SKIP_DIRS = {"node_modules", ".git", "dist", ".astro", ".wrangler", "__pycache__", "backups", "_audit", "functions", "data"}
# data/ (JSON besar ID) di-skip KECUALI file inti yang dipakai build:
DATA_KEEP = {"cities.json", "services.json", "related-services.json", "pillar-config.json", "research-data.js"}

changed = 0
targets = [os.path.join(WEB, "src"), os.path.join(WEB, "scripts"), os.path.join(ROOT, "scripts"), os.path.join(WEB, "public")]
extra_files = [os.path.join(WEB, "astro.config.mjs"), os.path.join(WEB, "package.json"), os.path.join(WEB, "wrangler.jsonc")]

def process(fp):
    global changed
    try:
        txt = open(fp, encoding="utf-8").read()
    except (UnicodeDecodeError, IsADirectoryError):
        return
    orig = txt
    for a, b in SLUG_MAP:
        txt = txt.replace(a, b)
    for a, b in SHORT_SLUGS:
        txt = re.sub(r"/" + a + r"(?=[/\"'\s)#?])", "/" + b, txt)
        txt = re.sub(r"(['\"])" + a + r"\1", r"\g<1>" + b + r"\g<1>", txt)
    for a, b in DOMAIN_MAP:
        txt = txt.replace(a, b)
    for a, b in MISC_MAP:
        txt = txt.replace(a, b)
    if txt != orig:
        open(fp, "w", encoding="utf-8").write(txt)
        changed += 1

for base in targets:
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS or (os.path.basename(dirpath) == "src" and d == "data")]
        in_src_data = os.path.normpath(dirpath) == os.path.normpath(os.path.join(WEB, "src", "data"))
        for fn in filenames:
            if fn in SKIP_FILES:
                continue
            if os.path.splitext(fn)[1] not in EXTS:
                continue
            if in_src_data and fn not in DATA_KEEP:
                continue
            process(os.path.join(dirpath, fn))
for fp in extra_files:
    if os.path.exists(fp):
        process(fp)

print(f"[3] file terupdate referensi: {changed}")
print("SELESAI")
