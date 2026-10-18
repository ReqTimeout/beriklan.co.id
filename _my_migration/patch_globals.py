#!/usr/bin/env python3
"""F1-8 batch 2: global components -> English (Navbar, Footer, StickyCTA, FloatingWhatsApp, CookieConsent)."""
import sys

BASE = "/Users/maabook/Desktop/beriklan.my/web/src/components/"

ID_FLAG_BLOCK = """                <a href="#" aria-label="Bahasa Indonesia" title="Bahasa Indonesia" class="hover:opacity-80 transition flex items-center gap-1">
                    <svg viewBox="0 0 18 12" class="w-[18px] h-[12px] rounded-sm overflow-hidden" aria-hidden="true">
                        <rect width="18" height="6" fill="#ce1126"/>
                        <rect y="6" width="18" height="6" fill="#ffffff"/>
                    </svg>
                    <span class="text-white/90">ID</span>
                </a>
"""

FILES = {
    "Navbar.svelte": [
        ("desc: '120jt+ pengguna aktif ID'", "desc: '24M+ active users in MY'"),
        ("desc: 'Jangkauan FYP organik'", "desc: 'Organic FYP reach'"),
        ("desc: 'Tangkap intent tinggi'", "desc: 'Capture high intent'"),
        ("{ label: 'Kelola Instagram', href: '/instagram-management', desc: 'Feed rapi & story aktif' }",
         "{ label: 'Instagram Management', href: '/instagram-management', desc: 'Polished feed & active Stories' }"),
        ("{ label: 'Kelola TikTok', href: '/tiktok-management', desc: '30 video / bulan' }",
         "{ label: 'TikTok Management', href: '/tiktok-management', desc: 'Up to 20 videos / month' }"),
        ("{ label: 'Pembuatan Website', href: '/website-development', desc: 'Mulai Rp 999rb / tahun' }",
         "{ label: 'Website Development', href: '/website-development', desc: 'From RM 1,499 one-time' }"),
        ("{ label: 'Landing Page + Ads', href: '/landing-page-design', desc: 'Bundle Rp 1.999.000' }",
         "{ label: 'Landing Page + Ads', href: '/landing-page-design', desc: 'Bundle RM 1,299' }"),
        ("{ label: 'Lihat Semua Platform', href: '/live-stream-viewers', desc: 'Perbandingan harga & fitur' }",
         "{ label: 'View All Platforms', href: '/live-stream-viewers', desc: 'Compare prices & features' }"),
        ("desc: 'Boost direktori'", "desc: 'Boost directory ranking'"),
        ("desc: 'Balas chat 24/7 otomatis'", "desc: 'Automated 24/7 chat replies'"),
        ("'Halo Beriklan, saya ingin berdiskusi mengenai kebutuhan iklan digital bisnis saya.'",
         "'Hello Beriklan, I would like to discuss digital advertising for my business.'"),
        (ID_FLAG_BLOCK, ""),
        ('<span class="hidden sm:inline">Konsultasi</span>', '<span class="hidden sm:inline">Consultation</span>'),
        ('aria-label="Buka menu navigasi"', 'aria-label="Open navigation menu"'),
        ('aria-label="Tutup menu"', 'aria-label="Close menu"'),
        ("Tim online &middot; siap merespon", "Team online &middot; ready to respond"),
        ("Mau scale up<br/>", "Ready to scale<br/>"),
        ('<span class="text-accent">penjualan via iklan?</span>', '<span class="text-accent">sales with paid ads?</span>'),
        ("Pilih layanan di bawah, atau langsung terhubung lewat WhatsApp untuk diskusi singkat 15 menit.",
         "Pick a service below, or connect on WhatsApp for a quick 15-minute chat."),
        ("<span>9 th pengalaman</span>", "<span>9 yrs experience</span>"),
        ("<span>Respon 1 jam</span>", "<span>1-hour response</span>"),
        ("<span>Sertifikasi Meta &amp; Google</span>", "<span>Meta &amp; Google certified</span>"),
        ('<span class="popular-pill">Paling dicari</span>', '<span class="popular-pill">Most popular</span>'),
        ("{group.items.length} layanan", "{group.items.length} services"),
        ("'Halaman lengkap'", "'Full page'"),
        (">Hubungi langsung</p>", ">Contact us directly</p>"),
        (">Telepon langsung</span>", ">Call us directly</span>"),
        ("Diskusi via WhatsApp", "Chat on WhatsApp"),
        ("Respon dalam 1 jam · jam kerja", "Replies within 1 hour · business hours"),
        ("                    Respon 1 jam\n", "                    1-hour response\n"),
        ("© 2026 Bandung", "© 2026 Beriklan.my"),
        ('alt="Beriklan.co.id"', 'alt="Beriklan.my"', True),
    ],
    "Footer.svelte": [
        ("{ label: 'Kalkulator Budget', href: '/ad-budget-calculator' }", "{ label: 'Budget Calculator', href: '/ad-budget-calculator' }"),
        ("{ label: 'Kalkulator ROAS', href: '/roas-calculator' }", "{ label: 'ROAS Calculator', href: '/roas-calculator' }"),
        ("{ label: 'Kalkulator ROI', href: '/roi-calculator' }", "{ label: 'ROI Calculator', href: '/roi-calculator' }"),
        ("{ label: 'Riset Industri', href: '/research/laporan-industri-iklan-digital-indonesia-2026' }",
         "{ label: 'Industry Research', href: '/research/laporan-industri-iklan-digital-indonesia-2026' }"),
        ("{ label: 'Tentang Kami', href: '/about-us' }", "{ label: 'About Us', href: '/about-us' }"),
        ("{ label: 'Metodologi', href: '/methodology' }", "{ label: 'Methodology', href: '/methodology' }"),
        ("{ label: 'Kontak', href: '/contact' }", "{ label: 'Contact', href: '/contact' }"),
        ("-cost/bandung'", "-cost/kuala-lumpur'", True),
        ("{ label: 'Buzzer Live', href: '/tiktok-live-viewers/bandung' }", "{ label: 'Live Viewers', href: '/tiktok-live-viewers' }"),
        ("Siap merumuskan strategi<br/>yang selaras dengan bisnis Anda?", "Ready to build a strategy<br/>that fits your business?"),
        ("Hubungi kami untuk konsultasi via WhatsApp. Tim kami akan merespons dalam waktu 1 jam pada jam kerja.",
         "A consultation on WhatsApp. Our team responds within 1 hour during business hours."),
        ("Halo%20Beriklan%2C%20saya%20mau%20konsultasi", "Hello%20Beriklan%2C%20I%27d%20like%20a%20consultation"),
        ("Update Bulanan dari Tim Beriklan", "Monthly Updates from the Beriklan Team"),
        ("Tips iklan Meta, Google, TikTok, YouTube + data industri. Dikirim 1× sebulan. Tanpa spam, berhenti kapan saja.",
         "Meta, Google, TikTok and YouTube ads tips + industry data. Sent once a month. No spam, unsubscribe anytime."),
        ('placeholder="Nama (opsional)"', 'placeholder="Name (optional)"'),
        ('placeholder="email@bisnis.com"', 'placeholder="email@business.com"'),
        ("                            Daftar\n", "                            Subscribe\n"),
        ("Kami kirim 1 update/bulan. Berhenti kapan saja.", "One update per month. Unsubscribe anytime."),
        ('alt="Beriklan.co.id"', 'alt="Beriklan.my"'),
        ("Agency performance marketing yang berbasis di Bandung. Mulai dari riset, eksekusi, hingga optimasi — kamielola secara end-to-end agar Anda fokus pada bisnis.",
         "A performance marketing agency serving Malaysia. From research to execution and optimisation — managed end-to-end so you can focus on your business."),
        (">Layanan</h4>", ">Services</h4>"),
        (">Harga</h4>", ">Pricing</h4>"),
        (">Perusahaan</h4>", ">Company</h4>"),
        ("&copy; {year} Beriklan.co.id.", "&copy; {year} Beriklan.my."),
    ],
    "StickyCTA.svelte": [
        ("Halo%20Beriklan%2C%20saya%20ingin%20mendiskusikan%20strategi%20campaign%20iklan%20untuk%20bisnis%20saya",
         "Hello%20Beriklan%2C%20I%27d%20like%20to%20discuss%20an%20ad%20campaign%20strategy%20for%20my%20business"),
        ("subject=Konsultasi%20Iklan", "subject=Advertising%20Consultation"),
        ('aria-label="Tutup menu"', 'aria-label="Close menu"'),
        ('aria-label="Tutup"', 'aria-label="Close"'),
        ("Konsultan Beriklan", "Beriklan Consultant", True),
        ("Merespons dalam 1 jam · jam kerja", "Replies within 1 hour · business hours"),
        ("Konsultasi via WhatsApp", "consultation · free"),
        (">Telepon Langsung</p>", ">Call Us</p>"),
        (">Diskusi mendalam</p>", ">For deeper discussion</p>"),
        (">Kirim Email</p>", ">Send an Email</p>"),
        (">Brief terstruktur</p>", ">Send a structured brief</p>"),
        ("Sembunyikan sementara", "Hide for now"),
        ('aria-label="Sembunyikan panel"', 'aria-label="Hide panel"'),
        ("Respon 1 jam · jam kerja", "1-hour response · business hours"),
        ("Konsultasi", "consultation"),
        (">Telepon langsung</p>", ">Direct phone line</p>"),
        (">Email detail</p>", ">For detailed enquiries</p>"),
        ("aria-label={isOpen ? 'Tutup menu kontak' : 'Buka menu kontak'}", "aria-label={isOpen ? 'Close contact menu' : 'Open contact menu'}"),
        ('aria-label="Buka panel kontak"', 'aria-label="Open contact panel"'),
    ],
    "FloatingWhatsApp.svelte": [
        ("'Halo Beriklan, saya ingin berdiskusi mengenai kebutuhan iklan digital bisnis saya.'",
         "'Hello Beriklan, I would like to discuss digital advertising for my business.'"),
        ("subject=Konsultasi%20Iklan%20Digital", "subject=Digital%20Advertising%20Consultation"),
        ('aria-label="Tutup menu chat"', 'aria-label="Close chat menu"'),
        ("Konsultan Beriklan", "Beriklan Consultant"),
        ("Respon dalam 1 jam &middot; jam kerja", "Replies within 1 hour &middot; business hours"),
        ('aria-label="Tutup menu"', 'aria-label="Close menu"'),
        ('title="Tutup"', 'title="Close"'),
        (">Respon paling cepat</span>", ">Fastest response</span>"),
        (">Rekomendasi</span>", ">Recommended</span>"),
        (">Telepon langsung</span>", ">Direct phone line</span>"),
        (">Untuk pertanyaan detail</span>", ">For detailed enquiries</span>"),
        ('aria-label="Buka menu chat WhatsApp"', 'aria-label="Open WhatsApp chat menu"'),
        ("Chat sekarang", "Chat now"),
        ("Diskusi via WhatsApp", "Chat on WhatsApp"),
    ],
    "CookieConsent.astro": [
        ("UU PDP + GDPR compliant", "PDPA + GDPR compliant"),
        ("Kami Pakai Cookie — Setuju?", "We Use Cookies — OK?"),
        ("""Kami menggunakan cookie untuk iklan (AdSense), analitik, dan personalisasi.
        Data diproses sesuai <a href="/privacy-policy/" class="cookie-link">Kebijakan Privasi</a>.
        Setuju atau kelola preferensi Anda.""",
         """We use cookies for advertising (AdSense), analytics and personalisation.
        Data is processed according to our <a href="/privacy-policy/" class="cookie-link">Privacy Policy</a>.
        Accept all or manage your preferences."""),
        ("Setuju Semua", "Accept All"),
        (">\n        Tolak\n      </button>", ">\n        Reject\n      </button>"),
        (">\n        Kelola\n      </button>", ">\n        Manage\n      </button>"),
        ("Pengaturan Cookie", "Cookie Settings"),
        ("<span><strong>Wajib</strong> · Untuk fitur dasar (autentikasi, keamanan)</span>",
         "<span><strong>Necessary</strong> · Core site features (authentication, security)</span>"),
        ("<span><strong>Analitik</strong> · Untuk memahami penggunaan situs</span>",
         "<span><strong>Analytics</strong> · To understand how the site is used</span>"),
        ("<span><strong>Iklan (AdSense)</strong> · Untuk personalisasi iklan Google AdSense</span>",
         "<span><strong>Advertising (AdSense)</strong> · Google AdSense ad personalisation</span>"),
        ("Simpan Preferensi", "Save Preferences"),
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
                print(f"  WARN {fname}: '{a[:60]}' occurs {txt.count(a)}x, replacing all")
            txt = txt.replace(a, b)
    open(fp, "w", encoding="utf-8").write(txt)
    print(f"{fname} OK — {len(pairs)} replacements")

sys.exit(1 if failed else 0)
