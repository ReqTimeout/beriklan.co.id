#!/usr/bin/env python3
"""F1-8 batch 3: shared service-page components -> English."""
import sys

BASE = "/Users/maabook/Desktop/beriklan.my/web/src/components/"

FILES = {
    "RelatedServices.svelte": [
        ("export let title = 'Layanan yang sering dipilih bersamaan';",
         "export let title = 'Services often chosen together';"),
        ("export let subtitle = 'Bisnis yang efektif biasanya menjalankan iklan di 2-3 kanal sekaligus agar saling menguatkan.';",
         "export let subtitle = 'Effective businesses usually run ads on 2-3 channels at once so they reinforce each other.';"),
        ("export let pillarLabel = 'Panduan Lengkap';", "export let pillarLabel = 'Complete Guide';"),
        ("                Saling Melengkapi\n", "                Better Together\n"),
        ("                            Lihat detail\n", "                            View details\n"),
        (">Strategi, format iklan, optimasi budget, dan cara ukur ROI — dibahas tuntas.</p>",
         ">Strategy, ad formats, budget optimisation and how to measure ROI — covered in depth.</p>"),
        ("                                Baca panduan\n", "                                Read the guide\n"),
    ],
    "StatsBand.astro": [
        ("// StatsBand.astro — 3 angka utama untuk E-E-A-T dan trust signal.",
         "// StatsBand.astro — 3 key numbers for E-E-A-T and trust signals."),
        ("{ value: '9', unit: 'tahun', label: 'Mengelola campaign iklan digital sejak 2016' },",
         "{ value: '9', unit: 'years', label: 'Managing digital ad campaigns since 2016' },"),
        ("{ value: '250+', unit: 'audit', label: 'Campaign yang pernah kami review & optimize' },",
         "{ value: '250+', unit: 'audits', label: 'Campaigns we have reviewed & optimised' },"),
        ("{ value: '<24', unit: 'jam', label: 'Respon WhatsApp di jam kerja (Senin–Sabtu)' },",
         "{ value: '<24', unit: 'hrs', label: 'WhatsApp response during business hours (Mon–Sat)' },"),
    ],
    "PAASection.astro": [
        ('aria-label="Pertanyaan yang Sering Diajukan"', 'aria-label="Frequently Asked Questions"'),
        (">Pertanyaan yang Sering Diajukan</h2>", ">Frequently Asked Questions</h2>"),
        (">Jawaban langsung untuk pertanyaan yang paling sering ditanyakan calon klien kami.</p>",
         ">Direct answers to the questions our prospective clients ask most often.</p>"),
        ('Pertanyaan Anda belum terjawab? <a href="#konsultasi" class="text-accent font-semibold hover:underline">Diskusi via WhatsApp →</a>',
         'Still have a question? <a href="#konsultasi" class="text-accent font-semibold hover:underline">Chat on WhatsApp →</a>'),
    ],
    "AuthorBio.astro": [
        ('// Shows "Tim Beriklan" credentials + facts.', '// Shows "Beriklan Team" credentials + facts.'),
        ('aria-label="Tentang Tim Beriklan"', 'aria-label="About the Beriklan Team"'),
        (">Ditulis oleh</p>", ">Written by</p>"),
        (">Tim Beriklan</h2>", ">The Beriklan Team</h2>"),
        ("""Tim performance marketing yang mengelola campaign iklan Meta, Google, TikTok, dan YouTube sejak 2016.
                    Berpengalaman menangani lebih dari 250 audit campaign untuk UMKM dan bisnis menengah di Indonesia —
                    dari retail, F&B, hingga jasa profesional. Pendekatan kami berbasis data: diagnosa dulu, baru susun strategi.""",
         """A performance marketing team managing Meta, Google, TikTok and YouTube ad campaigns since 2016.
                    Experienced across more than 250 campaign audits for SMEs and mid-sized businesses —
                    from retail and F&B to professional services. Our approach is data-driven: diagnose first, then build the strategy."""),
        (">9 tahun pengalaman</span>", ">9 years of experience</span>"),
        (">Sertifikasi Meta & Google</span>", ">Meta & Google certified</span>"),
        (">250+ campaign diaudit</span>", ">250+ campaigns audited</span>"),
        (">Akses penuh akun klien</span>", ">Clients keep full account access</span>"),
    ],
    "ComparisonTable.astro": [
        ("// ComparisonTable.astro — Beriklan vs Kelola Sendiri comparison.",
         "// ComparisonTable.astro — Beriklan vs DIY comparison."),
        ("const { serviceName = 'Iklan' } = Astro.props;", "const { serviceName = 'Ads' } = Astro.props;"),
        ("feature: 'Setup akun iklan + pixel tracking',", "feature: 'Ad account setup + pixel tracking',"),
        ("diy: 'Risiko salah konversi event, pixel tidak merekam data',",
         "diy: 'Risk of wrong conversion events, pixel not recording data',"),
        ("agency: 'Setup sesuai best practice Meta/Google/TikTok, pixel terverifikasi sebelum launch'",
         "agency: 'Setup follows Meta/Google/TikTok best practice, pixel verified before launch'"),
        ("feature: 'Riset audiens & targeting',", "feature: 'Audience research & targeting',"),
        ("diy: 'Targeting melebar, budget habis tanpa hasil',",
         "diy: 'Targeting too broad, budget spent with no results',"),
        ("agency: 'Interest + lookalike + retargeting berlapis, berdasarkan riset audiens spesifik industri'",
         "agency: 'Layered interest + lookalike + retargeting, based on industry-specific audience research'"),
        ("feature: 'Pembuatan iklan (copy + creative)',", "feature: 'Ad production (copy + creative)',"),
        ("diy: 'Iklan terasa generic, tidak stand-out di feed',",
         "diy: 'Ads feel generic and fail to stand out in the feed',"),
        ("agency: '10+ variasi creative per periode, copy disesuaikan dengan pain point audiens'",
         "agency: '10+ creative variations per period, copy tailored to audience pain points'"),
        ("feature: 'Optimasi harian',", "feature: 'Daily optimisation',"),
        ("diy: 'Cek mingguan, tidak tahu kapan harus pause atau scale',",
         "diy: 'Weekly check-ins, unsure when to pause or scale',"),
        ("agency: 'Monitoring harian, bid adjustment, creative refresh sesuai data real-time'",
         "agency: 'Daily monitoring, bid adjustments, creative refresh based on real-time data'"),
        ("feature: 'Pelaporan & transparansi',", "feature: 'Reporting & transparency',"),
        ("diy: 'Lihat di Ads Manager tanpa interpretasi',",
         "diy: 'Raw Ads Manager numbers without interpretation',"),
        ("agency: 'Laporan mingguan bahasa manusia + review bulanan via video call'",
         "agency: 'Weekly plain-language reports + monthly review via video call'"),
        ("feature: 'Akses akun iklan',", "feature: 'Ad account access',"),
        ("diy: 'Penuh (tapi Anda sendiri yang pegang)',", "diy: 'Full (but you run everything yourself)',"),
        ("agency: 'Penuh — Anda tetap owner, kami yang kelola'",
         "agency: 'Full — you remain the owner, we manage it'"),
        ("feature: 'Waktu Anda',", "feature: 'Your time',"),
        ("diy: '5-10 jam/minggu belajar + eksekusi',", "diy: '5-10 hrs/week learning + executing',"),
        ("agency: 'Fokus bisnis, kami yang handle iklan'",
         "agency: 'Focus on your business, we manage the campaigns'"),
        ('aria-label="Perbandingan Beriklan vs Kelola Sendiri"', 'aria-label="Beriklan vs DIY Comparison"'),
        (">Perbandingan Jujur</p>", ">An Honest Comparison</p>"),
        (">Kelola {serviceName} Sendiri vs Beriklan</h2>", ">DIY {serviceName} vs Beriklan</h2>"),
        ("""Tidak ada jawaban benar atau salah — hanya berbeda prioritas waktu, budget, dan target hasil.
                Berikut perbandingan apa yang Anda dapatkan di masing-masing opsi.""",
         """There is no right or wrong answer — only different priorities in time, budget and target outcomes.
                Here is what you get with each option."""),
        (">Aspek</th>", ">Aspect</th>"),
        (">Kelola Sendiri</th>", ">Do It Yourself</th>"),
        (">Dengan Beriklan</th>", ">With Beriklan</th>"),
        ("""Bukan untuk meyakinkan Anda — ini keputusan bisnis yang harus Anda buat sendiri.
            Jika Anda punya waktu 5-10 jam/minggu untuk belajar Meta/Google Ads dan nyaman eksperimen, kelola sendiri sah-sah saja.
            Jika ingin hasil terukur tanpa harus belajar platform, kami siap diskusi.""",
         """This is not about convincing you — it is a business decision only you can make.
            If you have 5-10 hours a week to learn Meta/Google Ads and enjoy experimenting, DIY is perfectly fine.
            If you want measurable results without learning the platforms, we are happy to talk."""),
    ],
}

failed = False
for fname, pairs in FILES.items():
    fp = BASE + fname
    txt = open(fp, encoding="utf-8").read()
    missing = [p[0] for p in pairs if p[0] not in txt]
    if missing:
        failed = True
        print(f"== {fname}: {len(missing)} MISSING ==")
        for m in missing:
            print("  MISSING:", repr(m[:90]))
        continue
    for p in pairs:
        a, b = p[0], p[1]
        if len(p) > 2 and p[2]:
            txt = txt.replace(a, b)
        else:
            if txt.count(a) > 1:
                print(f"  WARN {fname}: '{a[:60]}' occurs {txt.count(a)}x")
            txt = txt.replace(a, b, 1)
    open(fp, "w", encoding="utf-8").write(txt)
    print(f"{fname} OK — {len(pairs)} replacements")

sys.exit(1 if failed else 0)
