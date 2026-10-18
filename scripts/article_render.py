#!/usr/bin/env python3
"""
article_render.py — Deterministic (NO-LLM) article renderer for Beriklan.

Fixes the empty-{city} bug and produces high-variety, locally-relevant HTML
by injecting REAL local data (cities.json local_facts, local-faqs.json,
paa-questions.json) and rotating 15-20 template skeletons + section order
deterministically by slug hash.

Used by:
  - gen_articles.py   (new generation from keyword-queue)
  - patch_drafts.py   (in-place patch of broken batch_direct_* drafts)

Public API:
  detect_city(slug, keyword) -> dict|None
  detect_service(slug, keyword) -> dict
  render_article(slug, keyword, city=None, service=None, publish_iso=None) -> dict
"""
import os, re, json, hashlib
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "web" / "src" / "data"

WIB = timezone(timedelta(hours=7))
WA = 'https://wa.me/62811919328'
CTA = f'Hubungi kami via WhatsApp <a href="{WA}" target="_blank" rel="noopener noreferrer">Beriklan</a> untuk konsultasi'

# ---------------------------------------------------------------------------
# Data loading (lazy, cached)
# ---------------------------------------------------------------------------
_CACHE = {}

def _load(name):
    if name in _CACHE:
        return _CACHE[name]
    p = DATA / name
    try:
        _CACHE[name] = json.load(open(p, encoding="utf-8"))
    except Exception:
        _CACHE[name] = None
    return _CACHE[name]

def _cities():
    if "_cindex" in _CACHE:
        return _CACHE["_cindex"]
    idx = {}
    data = _load("cities.json") or []
    for c in data:
        idx[c["slug"]] = c
        for a in c.get("alt_names", []):
            idx.setdefault(a.lower(), c)
    # longest-first token list for detection
    _CACHE["_cindex"] = idx
    _CACHE["_ctokens"] = sorted(set(list(idx.keys())), key=len, reverse=True)
    return idx

def _services():
    if "_sindex" in _CACHE:
        return _CACHE["_sindex"]
    idx = {}
    for s in (_load("services.json") or []):
        idx[s["slug"]] = s
    _CACHE["_sindex"] = idx
    return idx

def _local_faq_index():
    if "_lfidx" in _CACHE:
        return _CACHE["_lfidx"]
    idx = {}
    for f in (_load("local-faqs.json") or []):
        key = (f.get("city_slug"), f.get("service_slug"))
        idx.setdefault(key, []).append({"q": f.get("question", ""), "a": f.get("answer", "")})
    _CACHE["_lfidx"] = idx
    return idx

def _paa_index():
    return _load("paa-questions.json") or {}

# ---------------------------------------------------------------------------
# Pricing per service (fee manajemen / 30 hari, di luar ad spend)
# ---------------------------------------------------------------------------
PRICING = {
    "jasa-iklan-facebook": [("Standart", "1.750.000"), ("Business", "3.750.000")],
    "jasa-iklan-instagram": [("Standart", "1.750.000"), ("Business", "3.750.000")],
    "jasa-iklan-tiktok": [("Starter", "1.000.000"), ("Growth", "1.600.000"), ("Business", "3.750.000")],
    "jasa-iklan-google": [("Standart", "1.750.000"), ("Business", "3.750.000"), ("Enterprise", "6.000.000")],
    "jasa-iklan-youtube": [("Basic", "1.250.000"), ("Growth", "2.500.000"), ("Business", "3.750.000"), ("Premium", "4.750.000")],
    "jasa-kelola-instagram": [("Basic", "2.500.000"), ("Pro", "3.500.000")],
    "jasa-kelola-tiktok": [("Basic", "1.500.000"), ("Growth", "3.000.000"), ("Pro", "4.000.000")],
    "jasa-pembuatan-website": [("Landing", "999.000"), ("Company Profile", "2.500.000")],
    "jasa-pembuatan-landing-page": [("Basic", "1.999.000"), ("Konversi + Ads", "3.500.000")],
    "jasa-digital-marketing": [("Konsultasi", "Custom"), ("Growth Package", "Custom")],
}

SERVICE_KEYWORDS = [
    ("jasa-pembuatan-landing-page", ["landing page", "landing-page", "landingpage"]),
    ("jasa-pembuatan-website", ["website", "web design", "web company", "company profile"]),
    ("jasa-kelola-instagram", ["kelola instagram", "kelola ig", "admin instagram", "manage instagram"]),
    ("jasa-kelola-tiktok", ["kelola tiktok", "admin tiktok", "manage tiktok"]),
    ("jasa-iklan-facebook", ["facebook", "fb ads", "meta ads", "fb-ads"]),
    ("jasa-iklan-instagram", ["instagram", "ig ads"]),
    ("jasa-iklan-tiktok", ["tiktok ads", "tiktok", "spark ads"]),
    ("jasa-iklan-youtube", ["youtube", "video ads", "bumper"]),
    ("jasa-iklan-google", ["google", "adwords", "sem", "search ads", "google ads"]),
    ("jasa-digital-marketing", ["digital marketing", "pemasaran digital", "agency digital"]),
]

# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

def detect_city(slug, keyword=""):
    idx = _cities()
    tokens = _CACHE.get("_ctokens", [])
    hay = "-" + (slug or "").lower().replace(" ", "-") + "-"
    for tok in tokens:
        t = tok.lower().replace(" ", "-")
        if f"-{t}-" in hay:
            return idx[tok]
    # fallback: after " di "
    kw = (keyword or "").lower()
    if " di " in kw:
        tail = kw.split(" di ")[-1].strip().split(" ")[0]
        if tail in idx:
            return idx[tail]
    return None

def detect_service(slug, keyword=""):
    sidx = _services()
    text = ((slug or "") + " " + (keyword or "")).lower().replace("-", " ")
    for sslug, kws in SERVICE_KEYWORDS:
        for kw in kws:
            if kw in text:
                return sidx.get(sslug, {"slug": sslug, "name": sslug.replace("jasa-", "Jasa ").replace("-", " ").title()})
    # default
    return sidx.get("jasa-digital-marketing", {"slug": "jasa-digital-marketing", "name": "Jasa Digital Marketing"})

def _seed(slug):
    return int(hashlib.md5((slug or "x").encode("utf-8")).hexdigest(), 16)

def _pick(seed, options, salt=0):
    return options[(seed + salt) % len(options)]

def _title_from_keyword(keyword):
    kw = (keyword or "").strip()
    kw = re.sub(r"\s+", " ", kw)
    return kw[:1].upper() + kw[1:] if kw else "Layanan Digital Marketing"

# ---------------------------------------------------------------------------
# Content blocks (each returns HTML; variants chosen by seed)
# ---------------------------------------------------------------------------

def _b_intro(seed, ctx):
    s, city, fact = ctx["sname"], ctx["cname"], ctx["fact"]
    loc = f" di {city}" if city else " di Indonesia"
    v = [
        f"<p>Menjalankan <strong>{s}</strong>{loc} membutuhkan strategi pemasaran digital yang terukur dan berbasis data. {fact} Sejak 2016, Beriklan membantu bisnis meningkatkan penjualan melalui campaign yang efektif dan transparan.</p>",
        f"<p>Bagi pelaku usaha{loc}, memilih mitra <strong>{s}</strong> yang tepat menentukan apakah anggaran iklan menghasilkan dampak nyata. {fact} Tim Beriklan mengelola campaign secara akunabel dengan laporan mingguan.</p>",
        f"<p><strong>{s}</strong>{loc} kini menjadi kebutuhan bisnis yang ingin tumbuh secara konsisten. {fact} Beriklan hadir dengan pendekatan end-to-end: dari riset, eksekusi, hingga optimasi berbasis data.</p>",
        f"<p>Persaingan digital{loc} makin ketat. {fact} Lewat <strong>{s}</strong> yang terstruktur, Beriklan membantu Anda menjangkau audience yang tepat dengan biaya yang efisien dan hasil yang bisa dipertanggungjawabkan.</p>",
        f"<p>Ingin hasil iklan yang terukur{loc}? {fact} Layanan <strong>{s}</strong> dari Beriklan menggabungkan pengalaman 9 tahun dengan strategi berbasis data untuk memaksimalkan setiap rupiah anggaran.</p>",
        f"<p>Artikel ini membahas bagaimana <strong>{s}</strong> dapat mendorong pertumbuhan bisnis{loc} secara berkelanjutan. {fact} Beriklan menekankan transparansi penuh: akses akun dan laporan mingguan.</p>",
    ]
    return _pick(seed, v, 1)

def _b_why(seed, ctx):
    s, city = ctx["sname"], ctx["cname"]
    if not city:
        head = f"Mengapa Strategi {s} Penting untuk Bisnis Anda"
        body = "Pasar Indonesia sangat beragam, mulai dari UMKM tradisional hingga bisnis digital native. Tanpa strategi yang tepat, anggaran mudah terbuang untuk audience yang tidak relevan."
    else:
        facts = ctx["facts"]
        extra = (" " + facts[1]) if len(facts) > 1 else ""
        head = f"Mengapa Bisnis di {city} Perlu {s}"
        body = f"{city} memiliki karakteristik pasar yang khas.{extra} Audience terdiri dari campuran UMKM, brand lokal, dan konsumen yang melek teknologi, sehingga potensi reach sangat besar bila targeting dilakukan dengan presisi."
    return f"<h2>{head}</h2><p>{body}</p>"

def _b_problems(seed, ctx):
    v = [
        "<h2>Masalah yang Paling Sering Kami Temui</h2><p>Dari ratusan audit campaign, tiga akar masalah paling umum adalah <strong>targeting terlalu luas</strong> yang membakar budget, <strong>creative tidak selaras</strong> dengan audience, dan <strong>landing page yang tidak dioptimalkan</strong> untuk konversi.</p>",
        "<h2>Kesalahan Umum yang Membuat Iklan Boncos</h2><ul><li><strong>Targeting melebar</strong> — menjangkau orang yang tidak relevan.</li><li><strong>Creative monoton</strong> — tidak ada variasi untuk A/B testing.</li><li><strong>Tidak ada tracking</strong> — keputusan diambil tanpa data.</li></ul>",
        "<h2>Kenapa Banyak Campaign Gagal</h2><p>Kegagalan jarang disebabkan platform, melainkan eksekusi: objective tidak jelas, budget disebar rata tanpa prioritas, dan optimasi yang tidak konsisten. Beriklan memperbaiki ketiganya sejak awal.</p>",
    ]
    return _pick(seed, v, 2)

def _b_steps(seed, ctx):
    v = [
        "<h2>Langkah-Langkah Campaign yang Efektif</h2><ol><li><strong>Audit &amp; Riset</strong> — memetakan audience, kompetitor, dan performa historis.</li><li><strong>Strategi</strong> — menentukan objective, alokasi budget, dan timeline realistis.</li><li><strong>Creative</strong> — produksi materi sesuai branding dengan copy Bahasa Indonesia natural.</li><li><strong>Launch &amp; Monitor</strong> — kampanye berjalan dengan optimasi harian.</li><li><strong>Laporan Mingguan</strong> — dashboard ROAS, CPA, CTR, dan CPC.</li></ol>",
        "<h2>Cara Kerja Kami</h2><p>Kami bekerja dalam fase yang jelas: <strong>Minggu 1</strong> brief &amp; riset, <strong>Minggu 1-2</strong> setup akun dan produksi kreatif, <strong>Minggu 2+</strong> launch 30 hari dengan laporan mingguan, lalu <strong>optimasi berkelanjutan</strong> — iklan yang perform di-scale, yang lemah diganti.</p>",
        "<h2>Alur Pengerjaan yang Terstruktur</h2><ol><li>Diagnosa masalah &amp; peluang.</li><li>Rumuskan strategi prioritas.</li><li>Eksekusi campaign + tracking.</li><li>Evaluasi mingguan &amp; iterasi.</li></ol>",
    ]
    return _pick(seed, v, 3)

def _b_targeting(seed, ctx):
    city = ctx["cname"] or "wilayah target"
    v = [
        f"<h3>Targeting untuk Pasar {city}</h3><p>Kami menggunakan radius targeting dari pusat {city} beserta area sekitarnya dengan demografi serupa. Interest targeting difokuskan pada topik relevan industri lokal, dan lookalike audience dibangun dari data pelanggan yang sudah ada.</p>",
        f"<h3>Strategi Audience di {city}</h3><p>Kombinasi <strong>geo-targeting</strong>, <strong>interest</strong>, dan <strong>custom audience</strong> memastikan iklan hanya tampil ke orang yang berpotensi membeli — bukan sekadar mengejar impresi murah.</p>",
    ]
    return _pick(seed, v, 4)

def _b_pricing(seed, ctx):
    sslug, s, city = ctx["sslug"], ctx["sname"], ctx["cname"]
    tiers = PRICING.get(sslug, [("Custom", "Custom")])
    loc = f" di {city}" if city else ""
    rows = "".join(
        f"<tr><td>{n}</td><td>{'Rp ' + p if p != 'Custom' else 'Custom'}</td></tr>" for n, p in tiers
    )
    return (f"<h2>Berapa Biaya {s}{loc}</h2>"
            f"<p>Biaya bervariasi sesuai kompleksitas campaign dan objective. Berikut gambaran paket (fee manajemen / 30 hari, <strong>belum termasuk ad spend</strong>):</p>"
            f"<table><thead><tr><th>Paket</th><th>Fee / bulan</th></tr></thead><tbody>{rows}</tbody></table>"
            f"<p>Setiap paket mencakup <strong>akses penuh ke akun</strong> dan <strong>laporan mingguan</strong> transparan. Tanpa kontrak minimum.</p>")

def _b_advantages(seed, ctx):
    return ("<h2>Keunggulan Beriklan</h2><ul>"
            "<li><strong>9 tahun pengalaman</strong> mengelola campaign lintas platform.</li>"
            "<li><strong>Respon 1 jam</strong> pada jam kerja.</li>"
            "<li><strong>Akses penuh ke akun klien</strong> — transparansi penuh.</li>"
            "<li><strong>Bersertifikasi Meta &amp; Google</strong> — best practice terbaru.</li>"
            "</ul>")

def _b_faq(seed, ctx):
    faqs = ctx["faqs"]
    if not faqs:
        return ""
    n = 2 + (seed % 2)  # 2 or 3
    chosen = faqs[:n]
    items = "".join(f"<h3>{f['q']}</h3><p>{f['a']}</p>" for f in chosen if f.get("q") and f.get("a"))
    return f"<h2>Pertanyaan yang Sering Diajukan</h2>{items}" if items else ""

def _b_conclusion(seed, ctx):
    s, city = ctx["sname"], ctx["cname"]
    loc = f" di {city}" if city else ""
    v = [
        f"<h2>Kesimpulan</h2><p>Memilih mitra <strong>{s}</strong> yang tepat menentukan hasil iklan digital Anda{loc}. Beriklan menggabungkan pengalaman dengan pendekatan terukur, transparan, dan berbasis data. {CTA}.</p>",
        f"<h2>Mulai Sekarang</h2><p>Siap meningkatkan performa iklan{loc}? {CTA} — sesi awal untuk membahas objective dan strategi prioritas Anda.</p>",
    ]
    return _pick(seed, v, 5)

def _b_measure(seed, ctx):
    s, city = ctx["sname"], ctx["cname"]
    loc = f" di {city}" if city else ""
    v = [
        (f"<h2>Cara Mengukur Keberhasilan Campaign</h2><p>Iklan yang baik adalah iklan yang bisa diukur. Untuk {s}{loc}, kami memantau metrik inti: <strong>ROAS</strong> (Return on Ad Spend) untuk efisiensi belanja, <strong>CPA</strong> (Cost per Acquisition) untuk biaya per konversi, serta <strong>CTR</strong> dan <strong>CPC</strong> untuk kualitas kreatif. Semua tersaji dalam dashboard real-time sehingga keputusan diambil berdasarkan data, bukan asumsi.</p>"),
        (f"<h2>Laporan &amp; Transparansi</h2><p>Setiap klien{loc} menerima laporan mingguan yang mudah dipahami: ringkasan performa, insight audience, dan rekomendasi langkah berikutnya. Anda tetap memegang <strong>akses penuh ke akun iklan</strong> sehingga tidak ada angka yang disembunyikan. Inilah yang membedakan {s} profesional dari sekadar 'pasang iklan'.</p>"),
    ]
    return _pick(seed, v, 7)


def _b_related(seed, ctx):
    links = [
        ('/jasa-digital-marketing/', 'Jasa Digital Marketing'),
        ('/jasa-iklan-google/', 'Jasa Iklan Google Ads'),
        ('/jasa-iklan-facebook/', 'Jasa Iklan Facebook'),
        ('/jasa-pembuatan-landing-page/', 'Landing Page + Google Ads'),
    ]
    a, b = _pick(seed, links, 6), _pick(seed, links, 9)
    if a == b:
        b = links[(links.index(a) + 1) % len(links)]
    return f'<p>Baca juga: <a href="{a[0]}">{a[1]}</a> dan <a href="{b[0]}">{b[1]}</a>.</p>'

# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

def _faqs_for(city_slug, sslug):
    lf = _local_faq_index().get((city_slug, sslug)) if city_slug else None
    if lf:
        return lf
    paa = _paa_index().get(sslug)
    if paa:
        return paa
    s = _services().get(sslug, {})
    return [{"q": f.get("q", ""), "a": f.get("a", "")} for f in s.get("faqs", [])]

def render_article(slug, keyword, city=None, service=None, publish_iso=None):
    seed = _seed(slug)
    cityd = city if isinstance(city, dict) else detect_city(slug, keyword)
    if isinstance(service, dict):
        base = _services().get(service.get("slug", ""), {})
        svc = {**base, **service} if base else service
    elif isinstance(service, str):
        svc = _services().get(service) or detect_service(slug, keyword)
    else:
        svc = detect_service(slug, keyword)
    sslug = svc.get("slug", "jasa-digital-marketing")
    sname = svc.get("name", "Jasa Digital Marketing")
    cname = cityd.get("name") if cityd else ""
    cslug = cityd.get("slug") if cityd else None
    facts = (cityd.get("local_facts") if cityd else []) or []
    fact = facts[0] if facts else "Pasar digital Indonesia tumbuh pesat seiring meningkatnya penetrasi internet dan mobile."

    ctx = {"sslug": sslug, "sname": sname, "cname": cname, "cslug": cslug,
           "facts": facts, "fact": fact, "faqs": _faqs_for(cslug, sslug)}

    title = _title_from_keyword(keyword) + " — Panduan Lengkap"
    parts = [_b_intro(seed, ctx)]  # NOTE: no <h1> — page renders H1 from title

    # middle blocks: order shuffled deterministically
    middle = [_b_why, _b_problems, _b_steps, _b_targeting, _b_pricing, _b_advantages, _b_measure]
    order = list(range(len(middle)))
    # deterministic shuffle
    for i in range(len(order) - 1, 0, -1):
        j = (seed // (i + 7)) % (i + 1)
        order[i], order[j] = order[j], order[i]
    for idx in order:
        parts.append(middle[idx](seed, ctx))

    fq = _b_faq(seed, ctx)
    if fq:
        parts.append(fq)
    parts.append(_b_conclusion(seed, ctx))
    parts.append(_b_related(seed, ctx))

    html = "".join(parts)
    word_count = len(re.findall(r"\w+", re.sub(r"<[^>]+>", " ", html)))

    if publish_iso is None:
        now = datetime.now(WIB)
    else:
        now = publish_iso if isinstance(publish_iso, datetime) else datetime.fromisoformat(str(publish_iso))
    iso_date = now.strftime("%Y-%m-%dT%H:%M:%S")
    date_h = now.strftime("%d %b %Y")

    # tags: rebuilt, no empty
    tags = [t for t in [sslug.replace("jasa-", ""), cslug, "jasa-iklan"] if t]

    excerpt = re.sub(r"<[^>]+>", " ", html)
    excerpt = re.sub(r"\s+", " ", excerpt).strip()[:200]

    return {
        "slug": slug,
        "title": _title_from_keyword(keyword),
        "keyword": keyword,
        "excerpt": excerpt,
        "content": html,
        "date": date_h,
        "iso_date": iso_date,
        "category": svc.get("category", "strategy") or "strategy",
        "readTime": f"{max(1, round(word_count/200))} min",
        "tags": tags,
        "service": sslug,
        "city": cslug or "",
        "featured": False,
        "generated": True,
        "source": "template_v2",
        "word_count": word_count,
    }


def sanitize_content(html):
    """Make any draft content safe to inject via set:html into the .prose body.
    Extracts <body> if a full document, strips doctype/head/script/style and H1
    (page renders its own H1 from title)."""
    if not html:
        return ""
    h = html
    m = re.search(r"<body[^>]*>(.*?)</body>", h, re.I | re.S)
    if m:
        h = m.group(1)
    h = re.sub(r"<!DOCTYPE[^>]*>", "", h, flags=re.I)
    h = re.sub(r"<head[^>]*>.*?</head>", "", h, flags=re.I | re.S)
    h = re.sub(r"<script[^>]*>.*?</script>", "", h, flags=re.I | re.S)
    h = re.sub(r"<style[^>]*>.*?</style>", "", h, flags=re.I | re.S)
    h = re.sub(r"</?(html|head|body)[^>]*>", "", h, flags=re.I)
    h = re.sub(r"<(meta|link|title|base)[^>]*>", "", h, flags=re.I)
    h = re.sub(r"<h1[^>]*>.*?</h1>", "", h, flags=re.I | re.S)
    return h.strip()


def qc(article):
    """Quality gate. Returns (ok: bool, reason: str).
    Rejects thin/broken content BEFORE it can be published."""
    if not isinstance(article, dict):
        return False, "not-dict"
    slug = article.get("slug", "")
    if not slug or not re.match(r"^[a-z0-9-]+$", slug):
        return False, "bad-slug"
    html = article.get("content", "") or ""
    if re.search(r"<!DOCTYPE|<script|<iframe", html, re.I):
        return False, "unsafe-html"
    if "<h1" in html.lower():
        return False, "h1-in-content"  # page renders H1 from title; content must not
    if not (article.get("title") or "").strip():
        return False, "no-title"
    if html.lower().count("<h2") < 2:
        return False, "too-few-h2"
    wc = article.get("word_count") or len(re.findall(r"\w+", re.sub(r"<[^>]+>", " ", html)))
    if wc < 250:
        return False, f"thin-{wc}w"
    # empty-city artifacts (the old bug): "di  " / "di </" / "di ." / "di ,"
    if re.search(r"\bdi\s{2,}", html) or re.search(r"\bdi\s*(</|[.,])", html):
        return False, "empty-city-artifact"
    tags = article.get("tags") or []
    if not tags or any((t is None or str(t).strip() == "") for t in tags):
        return False, "empty-tag"
    idt = article.get("iso_date", "")
    if idt:
        try:
            d = datetime.fromisoformat(idt.replace("Z", ""))
            if d.replace(tzinfo=None) > datetime.now(WIB).replace(tzinfo=None) + timedelta(minutes=5):
                return False, "future-date"
        except Exception:
            return False, "bad-date"
    return True, "ok"


if __name__ == "__main__":
    import sys
    for kw, sg in [("Jasa Iklan Facebook Promo Di Semarang", "iklan-facebook-promo-di-semarang"),
                   ("Jasa Landing Page Murah Di Pontianak", "jasa-landing-page-murah-di-pontianak"),
                   ("Jasa Digital Marketing Terbaik", "jasa-digital-marketing-terbaik")]:
        a = render_article(sg, kw)
        print("=" * 60)
        print(a["slug"], "| city:", a["city"], "| svc:", a["service"], "| wc:", a["word_count"], "| tags:", a["tags"])
        print(a["content"][:280].replace("\n", " "))
