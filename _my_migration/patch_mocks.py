#!/usr/bin/env python3
"""F1-8 batch 7: mock/visual components -> English + Malaysian localization."""
import sys

BASE = "/Users/maabook/Desktop/beriklan.my/web/src/components/"

FILES = {
    "GoogleSerpMock.svelte": [
        ("const fullQuery = 'klinik gigi terbaik bandung';", "const fullQuery = 'best dental clinic kuala lumpur';"),
        (">CARI</button>", ">Search</button>"),
        ("Sekitar 1.230.000 hasil (0,42 detik)", "About 1,230,000 results (0.42 seconds)"),
        ("<span class=\"ad-badge\">Iklan</span>", "<span class=\"ad-badge\">Ad</span>", True),
        ("Klinik Gigi Bandung · Rating 4.8 · Booking Online 24 Jam", "KL Dental Clinic · Rating 4.8 · 24-Hour Online Booking"),
        ("klinikgigibandung.id/booking", "kldentalclinic.com.my/booking"),
        ("Dokter gigi berpengalaman 12 tahun. Perawatan saluran akar, behel, veneer, dan scaling. Konsultasi pertama. Lokasi strategis di Bandung.",
         "Dentists with 12 years of experience. Root canal treatment, braces, veneers and scaling. First consultation FREE. Strategic location in Kuala Lumpur."),
        ("+62 22-...", "+60 3-..."),
        ("<span class=\"text-[9px] text-muted\">klinikgigi-bdg.com</span>", "<span class=\"text-[9px] text-muted\">dentalcare-kl.com</span>"),
        ("Promo Scaling Gigi Hanya Rp 199rb · Klinik Gigi Berstandar", "Teeth Scaling Promo Only RM 99 · Certified Dental Clinic"),
        ("klinikgigi-bdg.com/promo", "dentalcare-kl.com/promo"),
        ("Diskon 60% untuk scaling + hubungi kami. Dokter profesional dengan alat modern. Booking via WhatsApp hari ini.",
         "60% off scaling + a consultation. Professional dentists with modern equipment. Book via WhatsApp today."),
        ("<span class=\"text-[9px] text-muted\">dokterspesialis-gigi.id</span>", "<span class=\"text-[9px] text-muted\">braces-specialist.com.my</span>"),
        ("Behel Gigi Premium · Cicilan 0% · 24 Cabang di Indonesia", "Premium Braces · 0% Instalment · 24 Branches in Malaysia"),
        ("dokterspesialis-gigi.id/behel", "braces-specialist.com.my/braces"),
        ("Hubungi kami untuk pasang behel. Hasil terukur dengan teknologi 3D scan. Lokasi strategis di pusat kota Bandung.",
         "Free braces consultation. Measurable results with 3D scan technology. Strategic location in central Kuala Lumpur."),
        (">Posisi Rata-rata</p>", ">Average Position</p>"),
        ("di halaman pertama Google", "on page one of Google"),
        (">Kata Kunci</p>", ">Keywords</p>"),
        ("ml-1\">aktif</span>", "ml-1\">active</span>"),
        (">Pencarian/Bulan</p>", ">Searches/Month</p>"),
    ],
    "InstagramAdMock.svelte": [
        (">Promo Hari Ini</p>", ">Today's Promo</p>"),
        ("Glow Up<br/>Skin Anda", "Glow Up<br/>Your Skin"),
        (">Klik untuk booking</p>", ">Tap to book</p>"),
        ("Rutin 7 hari, kulit cerah nyata ✨", "7-day routine, visibly brighter skin ✨"),
        ("60% pengguna temukan produk baru", "60% of users discover new products"),
        (">Estimasi Views</p>", ">Estimated Views</p>"),
        ("{views.toLocaleString('id-ID')}", "{views.toLocaleString('en-MY')}"),
        (">DM Masuk</p>", ">Incoming DMs</p>"),
        ("ml-0.5\">hari ini</span>", "ml-0.5\">today</span>"),
    ],
    "MetaAdsPreview.svelte": [
        ("{ Icon: MapPin, label: 'Bandung, Jakarta, Surabaya', color: 'bg-teal/15 text-teal' },",
         "{ Icon: MapPin, label: 'Kuala Lumpur, Penang, Johor Bahru', color: 'bg-teal/15 text-teal' },"),
        ("{ Icon: Sparkles, label: 'Minat: Skincare & Beauty', color: 'bg-pink-100 text-pink-600' },",
         "{ Icon: Sparkles, label: 'Interests: Skincare & Beauty', color: 'bg-pink-100 text-pink-600' },"),
        ("{ Icon: ThumbsUp, label: 'Remarketing: 30 hari', color: 'bg-green/15 text-green' },",
         "{ Icon: ThumbsUp, label: 'Remarketing: 30 days', color: 'bg-green/15 text-green' },"),
        ("<p class=\"text-sm font-bold text-ink\">Beauty Studio Bandung</p>", "<p class=\"text-sm font-bold text-ink\">Beauty Studio KL</p>"),
        ("rounded uppercase tracking-wider\">Iklan</span>", "rounded uppercase tracking-wider\">Ad</span>"),
        ("Kulit kusam dan bruntusan? Treatment <strong class=\"text-ink\">Glow Facial</strong> hanya <strong class=\"text-accent\">Rp 249rb</strong> untuk konsultasi pertama. Booking via WhatsApp &mdash; slot terbatas tiap minggunya.",
         "Dull, bumpy skin? <strong class=\"text-ink\">Glow Facial</strong> treatment for only <strong class=\"text-accent\">RM 149</strong> on your first visit. Book via WhatsApp &mdash; limited slots each week."),
        ("Klinik Kecantikan &middot; Bandung", "Beauty Clinic &middot; Kuala Lumpur"),
        ("<span class=\"relative z-10\">Konsultasi via WhatsApp</span>", "<span class=\"relative z-10\">Book via WhatsApp</span>"),
        ("<span class=\"ml-2\">2,4 rb</span>", "<span class=\"ml-2\">2.4K</span>"),
        ("<span>187 komentar &middot; 43 kali dibagikan</span>", "<span>187 comments &middot; 43 shares</span>"),
        ("group-hover:scale-110 transition\" /> Suka", "group-hover:scale-110 transition\" /> Like"),
        ("group-hover:scale-110 transition\" /> Komentar", "group-hover:scale-110 transition\" /> Comment"),
        ("group-hover:scale-110 transition\" /> Bagikan", "group-hover:scale-110 transition\" /> Share"),
        (">Target Audiens</p>", ">Target Audience</p>"),
        ("Live &middot; 5 set aktif", "Live &middot; 5 active sets"),
        (">Estimasi Jangkauan</p>", ">Estimated Reach</p>"),
        (">orang / hari</p>", ">people / day</p>"),
        (">Pesan Masuk</p>", ">Incoming Messages</p>"),
        ("ml-0.5\">chat</span> hari ini</p>", "ml-0.5\">chats</span> today</p>"),
    ],
    "TikTokForYouMock.svelte": [
        ("'POV: kulit kamu cerah dalam 7 hari ✨',", "'POV: your skin gets brighter in 7 days ✨',"),
        ("'Tips skincare yang BENER-BENER works',", "'Skincare tips that ACTUALLY work',"),
        ("'Review jujur treatment facial viral',", "'Honest review of the viral facial treatment',"),
        ("'Rahasia glowing tanpa ribet',", "'The no-fuss secret to glowing skin',"),
        ("Suara Original - beautyloka", "Original Sound - beautyloka"),
        (">Estimasi Views</p>", ">Estimated Views</p>"),
        ("ml-1\">/kampanye</span>", "ml-1\">/campaign</span>"),
    ],
    "YouTubePlayerMock.svelte": [
        ("return n.toLocaleString('id-ID');", "return n.toLocaleString('en-MY');"),
        ("Lewati iklan →", "Skip Ad →"),
        ("Iklan · 6 detik", "Ad · 6 seconds"),
        ("Skincare Lokal yang Bikin Kulit Cerah dalam 7 Hari", "Local Skincare that Brightens Your Skin in 7 Days"),
        ("<span>2 hari lalu</span>", "<span>2 days ago</span>"),
        ("w-3.5 h-3.5\" /> 2,4K", "w-3.5 h-3.5\" /> 2.4K"),
        ("                    Bagikan\n", "                    Share\n"),
        (">Estimasi Tayangan</p>", ">Estimated Views</p>"),
        (">Rata-rata Watch Time</p>", ">Avg. Watch Time</p>"),
    ],
    "InstagramCalendarMock.svelte": [
        ("const days = ['S', 'S', 'R', 'K', 'J', 'S', 'M'];", "const days = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];"),
        (">konten</p>", ">posts</p>"),
        (">/bulan</p>", ">/month</p>"),
        (">vs bln lalu</p>", ">vs last month</p>"),
        (">Tutorial Skincare</p>", ">Skincare Tutorial</p>"),
    ],
    "OmnichannelMap.svelte": [
        ("ml-0.5\">/bulan</span>", "ml-0.5\">/month</span>"),
        (">Rata-rata ROAS</p>", ">Average ROAS</p>"),
        (">Sinergi</p>", ">Synergy</p>"),
        (">Semua kanal</p>", ">All channels</p>"),
    ],
    "TechStack.svelte": [
        ("export let subtitle = 'Teknologi yang kami pakai untuk membangun beriklan.my — dan yang kami rekomendasikan untuk klien.';",
         "export let subtitle = 'The technology we use to build beriklan.my — and what we recommend to clients.';"),
        ("Tools yang kami <span class=\"text-accent\">percaya & gunakan</span>",
         "Tools we <span class=\"text-accent\">trust & use</span>"),
        ("Stack di atas dipilih berdasarkan kebutuhan, skalabilitas, dan biaya operasional klien. Tidak ada markup teknologi — hanya yang terbukti.",
         "The stack above is chosen based on client needs, scalability and running costs. No technology markup — only what is proven."),
    ],
    "SiteBuilderMock.svelte": [
        ("<span class=\"font-mono\">bisnisanda.com</span>", "<span class=\"font-mono\">yourbusiness.com.my</span>"),
        ("ml-1\">halaman</span>", "ml-1\">pages</span>"),
    ],
    "Pricing.svelte": [
        ("<section id=\"harga\"", "<section id=\"pricing\""),
    ],
    "Footer.svelte": [
        ("const harga = [", "const pricing = ["),
        ("{#each harga as item}", "{#each pricing as item}"),
    ],
    "FloatingWhatsApp.svelte": [
        ("// Auto-hide FAB saat user scroll banyak (mobile only) untuk tidak menutupi konten",
         "// Auto-hide the FAB after heavy scrolling (mobile only) so it never covers content"),
    ],
    "CookieConsent.astro": [
        (" * - Emit event untuk activate AdSense kalau advertising consent",
         " * - Emits an event to activate AdSense when advertising consent is given"),
    ],
}

failed = False
for fname, pairs in FILES.items():
    fp = BASE + fname
    txt = open(fp, encoding="utf-8").read()
    missing = [p[0] for p in pairs if p[0] not in txt]
    if missing:
        failed = True
        print(f"[MISSING] {fname}:")
        for m in missing:
            print("  --", m[:100].replace("\n", "\\n"))
        continue
    n = 0
    for p in pairs:
        a, b = p[0], p[1]
        replace_all = len(p) > 2 and p[2]
        cnt = txt.count(a)
        if cnt > 1 and not replace_all:
            print(f"[WARN] {fname}: {cnt}x occurrence, replacing first only: {a[:70]!r}")
        if replace_all:
            txt = txt.replace(a, b)
            n += cnt
        else:
            txt = txt.replace(a, b, 1)
            n += 1
    open(fp, "w", encoding="utf-8").write(txt)
    print(f"[OK] {fname}: {n} replacements")

sys.exit(1 if failed else 0)
