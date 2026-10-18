#!/usr/bin/env python3
"""Sweep v2: remove the misleading "free/gratis 15-menit consultation" marketing
CLAIM across beriklan.co.id + beriklan.my — grammar-correct.

DESIGN (learned from v1 defects):
- CTA buttons / headings / eyebrows  -> "Hubungi Kami" / "Contact Us".
- Full sentences / subcopy           -> clean full sentence ("Hubungi kami untuk
                                        konsultasi via WhatsApp." / "Contact us ...").
- Prose / FAQ / meta body            -> DROP the "gratis"/"free"/"15 menit"/"tanpa biaya"
                                        qualifier only (never inject "hubungi kami"
                                        mid-sentence — that broke grammar in v1).
- Exact-string replacements only, ordered longest / most-specific first.
- Skips keyword/SEO data blobs, published post data, URL-slug data, staging drafts,
  and the competitor-ad SERP mock (illustrative, not our promise).
- Preserves SEO topic "percuma vs berbayar" (free vs paid ads) and one-off blog
  content examples ("Free braces consultation", etc.) because those exact strings
  are not in the pair list.
Usage: python3 _sweep_konsultasi.py [dry|apply]
"""
import os, sys

MODE = sys.argv[1] if len(sys.argv) > 1 else "dry"

ROOTS = [
    "/Users/maabook/Desktop/beriklan.co.id",
    "/Users/maabook/Desktop/beriklan.my",
]

# Ordered: most-specific first so shorter substrings don't clobber longer ones.
PAIRS = [
    # ================= INDONESIAN — specific full sentences =================
    ("Sesi konsultasi awal 15\u201330 menit \u2014 tanpa biaya.",
     "Hubungi kami untuk konsultasi via WhatsApp."),                       # order.astro:41
    ("Apakah sesi konsultasi benar-benar gratis?",
     "Bagaimana sesi konsultasi awal berjalan?"),                          # order.astro:179
    ("Ya, sesi konsultasi awal 15-30 menit via WhatsApp atau video call sepenuhnya gratis.",
     "Sesi konsultasi awal dilakukan via WhatsApp atau video call."),      # order.astro:180
    ("Sesi konsultasi awal 15 menit.",
     "Hubungi kami untuk konsultasi via WhatsApp."),                       # Layout.astro:28
    ("Sesi konsultasi awal selama 15 menit melalui WhatsApp \u2014 tanpa biaya.",
     "Hubungi kami untuk konsultasi via WhatsApp."),                       # Footer.svelte:60
    ("Sesi konsultasi 15 menit gratis.",
     "Hubungi kami untuk konsultasi via WhatsApp."),                       # service subcopy
    ("Sesi konsultasi 15 menit \u00b7 tanpa biaya",
     "Konsultasi via WhatsApp"),                                           # service footer subtext
    ("Diskusi gratis 15-30 menit via WhatsApp.",
     "Diskusi via WhatsApp."),                                             # blog [slug]:316
    ("Diskusi 15 menit via WhatsApp.",
     "Diskusi via WhatsApp."),                                             # CityContentBlock:195
    ("Konsultasi awal 15-30 menit via",
     "Konsultasi awal via"),                                               # metodologi:80
    ("Konsultasi awal 15-30 menit.",
     "Konsultasi awal."),                                                  # metodologi:20
    ("Konsultasi 15 menit via WhatsApp \u2014 tanpa biaya, tanpa kewajiban.",
     "Konsultasi via WhatsApp \u2014 tanpa kewajiban."),                   # klien:173
    ("Konsultasi awal 15 menit via WhatsApp",
     "Konsultasi via WhatsApp"),                                           # tentang-kami:227
    ("Konsultasi strategi gratis 15 menit.",
     "Hubungi kami untuk konsultasi."),                                    # service meta variant
    ("Konsultasi awal 15 menit kami sediakan gratis untuk menentukan",
     "Konsultasi awal kami sediakan untuk menentukan"),                    # gen_city_content template (44 pages)
    ("audit campaign gratis (15 menit via WhatsApp)",
     "audit campaign via WhatsApp"),                                       # directory_auto_submit
    ("Mau kami audit campaign Anda? 15 menit gratis:",
     "Mau kami audit campaign Anda? Hubungi kami:"),                       # NEWSLETTER-DRIP:93
    ("Diskusi 15 menit gratis", "Diskusi via WhatsApp"),                   # NEWSLETTER-DRIP:122
    ("Audit Iklan Digital Marketing Gratis 15 Menit",
     "Audit Iklan Digital Marketing"),                                     # PER-PAGE-REDESIGN-PLAN:775 (doc)
    ("Digital Marketing Anda \u2014 Gratis, 15 Menit",
     "Digital Marketing Anda"),                                            # PER-PAGE-REDESIGN-PLAN:777 (doc)

    # ================= INDONESIAN — headings / eyebrows / buttons =================
    ("Diskusi Gratis 15 Menit", "Hubungi Kami"),                           # blog CTA heading (astro + worker)
    ("Minta Audit Gratis 15 Menit", "Minta Audit via WhatsApp"),           # index:116
    ("Konsultasi 15 Menit \u00b7 Tanpa Biaya", "Hubungi Kami"),            # kontak:183
    ("Diskusi 15 Menit \u00b7 Tanpa Biaya", "Hubungi Kami"),               # tentang-kami:222
    ("Konsultasi 15 Menit \u00b7 Gratis", "Hubungi Kami"),                 # metodologi:191, press:107
    ("Konsultasi 15 Menit Gratis", "Hubungi Kami"),
    ("Konsultasi Gratis 15 Menit", "Hubungi Kami"),
    ("Konsultasi gratis 15 menit.", "Hubungi kami untuk konsultasi."),      # rank_match_profiles meta template (reversed order)
    ("Konsultasi gratis 15 menit", "Hubungi kami untuk konsultasi"),        # safety (no dot)
    ("Diskusi gratis 15-30 menit untuk", "Diskusi untuk"),                  # ProcessTimeline:13

    # ================= INDONESIAN — "gratis 15 menit" prose =================
    ("tinjauan gratis 15 menit", "tinjauan singkat"),                      # index:321

    # ================= INDONESIAN — "konsultasi ... 15 menit gratis" =================
    ("konsultasi awal 15 menit gratis", "konsultasi via WhatsApp"),        # FAQ (after "Hubungi kami untuk ")
    ("Konsultasi awal 15 menit gratis", "Hubungi kami untuk konsultasi"),  # meta desc standalone
    ("konsultasi awal 15 menit, gratis", "konsultasi via WhatsApp"),       # comma variant
    ("konsultasi awal 15 menit \u2014 gratis", "konsultasi via WhatsApp"), # em-dash variant
    ("Konsultasi awal 15 menit \u2014 gratis", "Hubungi kami untuk konsultasi"),
    ("Konsultasi 15 menit gratis.", "Hubungi kami untuk konsultasi."),
    ("Konsultasi 15 menit gratis", "Hubungi kami untuk konsultasi"),
    ("konsultasi 15 menit gratis", "hubungi kami untuk konsultasi"),
    ("Konsultasi 15 menit tanpa biaya", "Hubungi kami untuk konsultasi"),  # google desc (no dot)
    ("konsultasi 15-30 menit gratis", "konsultasi via WhatsApp"),

    # ================= INDONESIAN — "15 menit · tanpa biaya" subtitles =================
    ("Konsultasi 15 menit \u00b7 tanpa biaya", "Konsultasi via WhatsApp"), # StickyCTA:119
    ("konsultasi 15 menit \u00b7 tanpa biaya", "konsultasi via WhatsApp"),

    # ================= INDONESIAN — bare "15 menit" subtitle (after all above) =================
    ("Konsultasi 15 menit", "Konsultasi"),                                 # StickyCTA:197
    ("konsultasi 15 menit", "konsultasi"),                                 # .my worker inline prose (lowercase bare)

    # ================= INDONESIAN — "gratis via WhatsApp" CTAs =================
    ("Konsultasi Gratis via WhatsApp", "Hubungi Kami via WhatsApp"),
    ("Konsultasi gratis via WhatsApp", "Hubungi kami via WhatsApp"),       # Services:245
    ("Diskusi gratis via WhatsApp", "Hubungi kami via WhatsApp"),          # CityContentBlock:176

    # ================= INDONESIAN — city sentence =================
    ("Konsultasi gratis untuk bisnis di", "Konsultasi untuk bisnis di"),   # CityContentBlock:194

    # ================= INDONESIAN — "Konsultasi awal gratis" (DM FAQ) =================
    ("Konsultasi awal gratis", "Konsultasi awal"),
    ("konsultasi awal gratis", "konsultasi awal"),

    # ================= INDONESIAN — misc gratis qualifiers =================
    ("Konsultasi pertama GRATIS", "Konsultasi pertama"),
    ("Konsultasi awal biasanya gratis", "Konsultasi awal"),
    ("Audit awal gratis", "Audit awal"),                                   # metodologi:40
    ("Konsultasi strategi gratis", "Konsultasi strategi"),
    ("konsultasi strategi ulang gratis", "konsultasi strategi ulang"),
    ("konsultasi kebutuhan gratis", "konsultasi kebutuhan"),
    ("Audit 15 menit gratis", "Audit"),
    ("Audit Iklan Gratis", "Audit Iklan"),
    ("Audit Akun Gratis", "Audit Akun"),
    ("audit manual gratis", "audit manual"),
    ("Audit akun gratis", "Audit akun"),
    ("audit akun gratis", "audit akun"),

    # ================= INDONESIAN — URL-encoded =================
    ("konsultasi%20gratis", "konsultasi"),

    # ================= INDONESIAN — generic gratis-drop fallback (LAST) =================
    ("Konsultasi Gratis", "Hubungi Kami"),                                 # standalone title-case button
    ("Konsultasi gratis", "Konsultasi"),
    ("konsultasi gratis", "konsultasi"),
    ("Audit Gratis", "Audit"),
    ("Audit gratis", "Audit"),
    ("audit gratis", "audit"),

    # ================= ENGLISH (.my) — specific first =================
    ("free 15-minute initial consultation", "consultation"),
    ("Free 15-minute initial consultation", "Contact us"),
    ("Free 15-Minute Consultation", "Contact Us"),
    ("free 15-30 minute consultation", "consultation"),
    ("free 15-minute consultation", "consultation"),
    ("Free 15-minute consultation", "Contact us"),
    ("Free 15-Minute Discussion", "Contact Us"),                          # .my blog CTA heading
    ("free 15-minute review", "review"),                                  # .my index:321
    ("Free 15-minute review", "Review"),
    ("free, no-obligation consultation", "no-obligation consultation"),
    ("free initial consultation", "initial consultation"),
    ("Free initial consultation", "Initial consultation"),
    ("15-minute consultation", "consultation"),
    ("15-Minute Consultation", "Consultation"),
    ("30-minute consultation", "consultation"),
    ("30 minute consultation", "consultation"),
    ("30-Minute Consultation", "Consultation"),
    ("free%20consultation", "consultation"),
    ("Free Consultation", "Contact Us"),
    ("Free consultation", "Consultation"),
    ("free consultation", "consultation"),
    ("Free growth audit", "growth audit"),
    ("Free initial audit", "initial audit"),
    ("Free 15-Minute Audit", "Audit"),
    ("free audit", "audit"),
    ("Free audit", "Audit"),

    # ================= MALAY (.my) — drop trailing "percuma" (never touch "percuma vs berbayar") =================
    ("konsultasi atau ujian percuma", "konsultasi atau ujian"),
    ("konsultasi percuma", "konsultasi"),
    ("Konsultasi percuma", "Konsultasi"),
    ("mesyuarat percuma", "mesyuarat"),
    ("mesyuaran percuma", "mesyuaran"),
    ("mesyuarah percuma", "mesyuarah"),
    ("nasihat percuma", "nasihat"),
    ("rundingan percuma", "rundingan"),
    ("perbincangan percuma", "perbincangan"),
    ("penilaian percuma", "penilaian"),
    ("kutipan percuma", "kutipan"),
    ("belanjawan percuma", "belanjawan"),
    ("bajet percuma", "bajet"),
]

INCLUDE_EXT = {".astro", ".svelte", ".js", ".ts", ".mjs", ".cjs", ".py",
               ".md", ".html", ".txt"}
# JSON is skipped by default EXCEPT content files explicitly allowed:
# NOTE: these are LIVE user-facing content blobs (FAQ answers, meta-desc
# templates) — they must be swept. Keyword/slug/analytics blobs stay skipped.
ALLOW_JSON_NAMES = {"city-content.json", "services.json",
                    "local-faqs.json", "rank_match_profiles.json"}

SKIP_DIR_PARTS = {"node_modules", "dist", ".astro", ".git", ".wrangler",
                  "backups", "drafts_patched", ".vite", ".cache"}
# Filenames to always skip (keyword/SEO/data/slug/analysis blobs, published posts):
SKIP_FILE_NAMES = {
    "posts.json", "posts-index.json", "posts-meta.json",
    "keyword-queue.json", "keyword-queue-stats.json", "keyword-stats.json",
    "keyword-to-posts.json", "keywords.json", "keyword_suggestions_expanded.json",
    "clusters.json", "gsc-stats.json", "directory-progress.json",
    "freshness.json", "page-speed-audit.json",
    "per_city.json", "paa-questions.json", "cities.json",
    "testimonials.json", "related-services.json", "pillar-config.json",
    "refresh-candidates.json", "VIEW-LIVE-KEYWORDS.json",
    # preserve competitor-ad SERP mock (illustrative, not Beriklan's claim):
    "GoogleSerpMock.svelte",
    # this sweep script itself:
    "_sweep_konsultasi.py",
}

def eligible(path):
    parts = set(path.split(os.sep))
    if parts & SKIP_DIR_PARTS:
        return False
    name = os.path.basename(path)
    if name in SKIP_FILE_NAMES:
        return False
    ext = os.path.splitext(name)[1].lower()
    if ext == ".json":
        return name in ALLOW_JSON_NAMES
    return ext in INCLUDE_EXT

def main():
    total_files = 0
    total_repl = 0
    changed = []
    for root in ROOTS:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_PARTS]
            for fn in filenames:
                fp = os.path.join(dirpath, fn)
                if not eligible(fp):
                    continue
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        txt = f.read()
                except (UnicodeDecodeError, IsADirectoryError, PermissionError):
                    continue
                orig = txt
                cnt = 0
                for find, repl in PAIRS:
                    if find in txt:
                        c = txt.count(find)
                        txt = txt.replace(find, repl)
                        cnt += c
                if cnt and txt != orig:
                    total_files += 1
                    total_repl += cnt
                    changed.append((cnt, fp))
                    if MODE == "apply":
                        with open(fp, "w", encoding="utf-8") as f:
                            f.write(txt)
    changed.sort(reverse=True)
    for cnt, fp in changed:
        print(f"{cnt:5d}  {fp}")
    print(f"\n[{MODE}] files={total_files}  replacements={total_repl}")

if __name__ == "__main__":
    main()
