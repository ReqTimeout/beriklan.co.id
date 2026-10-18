#!/usr/bin/env python3
"""F1-7 pass 1: global shared-template strings across all .astro pages -> English/MY.
Tolerant mode: applies wherever found (shared strings are not in every file),
prints per-file replacement counts and a total per pair for audit.
"""
import glob, os, sys

PAGES = "/Users/maabook/Desktop/beriklan.my/web/src/pages/"

# (old, new) — order matters: longer strings containing shorter ones go first
PAIRS = [
    # ---- CTA buttons / labels ----
    ("Mulai Konsultasi via WhatsApp", "Start a WhatsApp Consultation"),
    ("Konsultasi via WhatsApp", "Consult on WhatsApp"),
    ("Diskusi via WhatsApp", "Chat on WhatsApp"),
    ("Lihat Paket & Harga", "View Packages & Pricing"),
    (">Paket & Harga<", ">Packages & Pricing<"),
    ("\n                    Paket & Harga\n", "\n                    Packages & Pricing\n"),
    ("\n                    Cara Kerja\n", "\n                    How It Works\n"),
    ("\n                    Studi Kasus & Testimoni\n", "\n                    Case Studies & Testimonials\n"),
    ("\n                    Mengapa Tim Ini\n", "\n                    Why This Team\n"),
    ("Tim sedang online · respons dalam 1 jam (jam kerja)", "Team online · replies within 1 hour (business hours)"),
    ("Sebelum mulai, ini biasanya yang ditanya", "Before starting, these usually get asked"),

    # ---- Section headings ----
    ("Pertanyaan yang sering muncul<br/>", "The questions that come up most<br/>"),
    ("<span class=\"text-accent\">sebelum deal pertama.</span>", "<span class=\"text-accent\">before the first deal.</span>"),
    ("Pengalaman mereka yang telah<br/>", "The experience of those who have<br/>"),
    ("<span class=\"text-accent\">bekerja sama dengan Tim Beriklan.</span>", "<span class=\"text-accent\">worked with the Beriklan team.</span>"),
    ("Empat langkah dari brief<br/>", "Four steps from brief<br/>"),
    ("<span class=\"text-accent\">menuju iklan yang tayang optimal.</span>", "<span class=\"text-accent\">to ads running at their best.</span>"),
    ("Fitur yang kami optimalkan<br/>", "The features we optimise<br/>"),
    ("<span class=\"text-accent\">di setiap campaign.</span>", "<span class=\"text-accent\">in every campaign.</span>"),
    ("Dua paket, disesuaikan dengan<br/>", "Two packages, matched to<br/>"),
    ("<span class=\"text-accent\">tujuan bisnis Anda.</span>", "<span class=\"text-accent\">your business goals.</span>"),
    ("Bukan agensi yang berjanji<br/>", "Not an agency that promises<br/>"),
    ("<span class=\"text-accent\">angka fantastis tanpa dasar.</span>", "<span class=\"text-accent\">fantastic numbers with nothing behind them.</span>"),
    ("Satu keputusan kecil hari ini,<br/>", "One small decision today,<br/>"),
    ("<span class=\"text-accent\">dampaknya terasa di kuartal depan.</span>", "<span class=\"text-accent\">the impact shows next quarter.</span>"),
    ("Kenapa layanan kami berbeda<br/>", "Why our service is different<br/>"),
    ("<span class=\"text-accent\">dari viewer bot biasa.</span>", "<span class=\"text-accent\">from ordinary bot viewers.</span>"),
    ("Enam paket, dari pemanasan<br/>", "Six packages, from warm-up<br/>"),
    ("Seluruh hasil berdasarkan data riil yang dapat Anda verifikasi sendiri. Bukan janji — hanya proses yang terukur.",
     "Every result is based on real data you can verify yourself. No promises — just a measurable process."),
    ("Dipercaya bisnis dari berbagai industri", "Trusted by businesses across industries"),

    # ---- Trust bar industries ----
    ("<span>Klinik</span>", "<span>Clinics</span>"),
    ("<span>Properti</span>", "<span>Property</span>"),

    # ---- Hero trust items ----
    ("<strong class=\"text-ink\">9 tahun</strong> mengelola campaign iklan", "<strong class=\"text-ink\">9 years</strong> managing ad campaigns"),
    ("Optimasi berbasis data, bukan tebakan", "Data-driven optimisation, not guesswork"),
    ("Laporan <strong class=\"text-ink\">setiap Senin</strong>, bahasa yang mudah dipahami", "Reports <strong class=\"text-ink\">every Monday</strong>, in plain language"),

    # ---- Trust dark cards ----
    ("<h3 class=\"trust-title-dark\">Akses penuh ke akun Anda</h3>", "<h3 class=\"trust-title-dark\">Full access to your account</h3>"),
    ("<h3 class=\"trust-title-dark\">Laporan setiap Senin pagi</h3>", "<h3 class=\"trust-title-dark\">A report every Monday morning</h3>"),
    ("<h3 class=\"trust-title-dark\">Tanpa minimum contract</h3>", "<h3 class=\"trust-title-dark\">No minimum contract</h3>"),
    ("<p class=\"trust-desc-dark\">Seluruh akun Meta Ads tetap di bawah kendali Anda. Bila sewaktu-waktu dibutuhkan, seluruh data historis dan konfigurasi berpindah tanpa hambatan.</p>",
     "<p class=\"trust-desc-dark\">Your ad account stays fully under your control. If you ever need to move on, all historical data and configurations transfer without friction.</p>"),
    ("<p class=\"trust-desc-dark\">Disusun dalam satu halaman dengan bahasa yang mudah dipahami. Bukan sekadar deretan CPM-CTR-CPC — Anda mendapat kejelasan: mana yang berjalan optimal, dan mana yang perlu disesuaikan.</p>",
     "<p class=\"trust-desc-dark\">One page, written in plain language. Not just rows of CPM-CTR-CPC — you get clarity on what is performing well and what needs adjusting.</p>"),
    ("<p class=\"trust-desc-dark\">Sistem kerja bulanan. Anda bebas memutuskan untuk lanjut atau berhenti setiap saat — tidak ada kontrak 6-12 bulan yang lazim diterapkan oleh kebanyakan agency lain.</p>",
     "<p class=\"trust-desc-dark\">We work in monthly cycles. You are free to continue or stop at any time — none of the 6\u201312 month contracts most other agencies impose.</p>"),

    # ---- Testimonials (shared trio) -> Malaysianised ----
    ("<p class=\"tst-body\">ROAS kami meningkat dari 1.8x menjadi 4.5x dalam empat bulan. Yang paling kami apresiasi: laporan disusun dengan bahasa yang jelas dan setiap perubahan dapat kami pahami.</p>",
     "<p class=\"tst-body\">Our ROAS grew from 1.8x to 4.5x in four months. What we appreciated most: reports written in clear language, with every change explained so we could understand it.</p>"),
    ("<p class=\"tst-body\">Setiap Senin pagi selalu ada laporan dalam bahasa yang mudah dipahami — bukan hanya deretan CPM dan CTR, tetapi apa yang perlu diubah dan mengapa.</p>",
     "<p class=\"tst-body\">Every Monday morning there is a report in language we actually understand — not just rows of CPM and CTR, but what needs to change and why.</p>"),
    ("<p class=\"tst-body\">Karakteristik funnel B2B berbeda signifikan dari FMCG. Beriklan memahami hal ini dan menyusun strategi yang relevan. Qualified leads naik 180% di Q3.</p>",
     "<p class=\"tst-body\">A B2B funnel behaves very differently from FMCG. Beriklan understood this and built a strategy that fit. Qualified leads grew 180% in Q3.</p>"),
    ("<p class=\"tst-name\">Andini Pratiwi</p>", "<p class=\"tst-name\">Nurul Aisyah</p>"),
    ("<p class=\"tst-role\">Owner · Brand Skincare, Bandung</p>", "<p class=\"tst-role\">Owner · Skincare Brand, Kuala Lumpur</p>"),
    ("<p class=\"tst-name\">Rizky Maulana</p>", "<p class=\"tst-name\">Amirul Hakim</p>"),
    ("<p class=\"tst-role\">Marketing Manager · Klinik Kecantikan, Jakarta</p>", "<p class=\"tst-role\">Marketing Manager · Beauty Clinic, Petaling Jaya</p>"),
    ("<p class=\"tst-name\">Sarah Nathania</p>", "<p class=\"tst-name\">Rachel Ng</p>"),
    ("<p class=\"tst-role\">Head of Growth · SaaS B2B, Jakarta</p>", "<p class=\"tst-role\">Head of Growth · B2B SaaS, Kuala Lumpur</p>"),
    ("<p class=\"tst-metric\">ROAS 1.8x → 4.5x dalam 4 bulan</p>", "<p class=\"tst-metric\">ROAS 1.8x → 4.5x in 4 months</p>"),
    ("<p class=\"tst-metric\">Lead konsisten 3x lipat dari bulan ke-2</p>", "<p class=\"tst-metric\">Consistent 3x more leads from month 2</p>"),
    ("<p class=\"tst-metric\">Qualified leads +180% di Q3 2025</p>", "<p class=\"tst-metric\">Qualified leads +180% in Q3 2025</p>"),

    # ---- Pricing helper card ----
    ("<p class=\"font-display font-bold text-base text-ink mb-1\">Tidak yakin paket mana yang sesuai?</p>",
     "<p class=\"font-display font-bold text-base text-ink mb-1\">Not sure which package fits?</p>"),
    ("<p class=\"text-sm text-muted leading-relaxed\">Hubungi kami untuk konsultasi via WhatsApp. Kami bantu pilih paket yang paling cocok dengan budget iklan dan objective campaign Anda.</p>",
     "<p class=\"text-sm text-muted leading-relaxed\">A consultation. We help you pick the package that best fits your ad budget and campaign objective.</p>"),
    ("<p class=\"text-sm text-muted leading-relaxed\">Hubungi kami untuk konsultasi via WhatsApp. Kami bantu pilih paket yang paling cocok dengan jadwal live dan target FYP Anda.</p>",
     "<p class=\"text-sm text-muted leading-relaxed\">A consultation. We help you pick the package that best fits your live schedule and FYP goals.</p>"),
    ("<p class=\"font-display font-bold text-base text-ink mb-1\">Butuh paket harian atau FYP campaign khusus?</p>",
     "<p class=\"font-display font-bold text-base text-ink mb-1\">Need a daily package or a custom FYP campaign?</p>"),
    ("<p class=\"text-white/50 text-xs mt-6\">Konsultasi via WhatsApp</p>",
     "<p class=\"text-white/50 text-xs mt-6\">consultation · free of charge</p>"),
    ("<p class=\"text-white/50 text-xs mt-6\">Paket mingguan/bulanan · diskon 10-15%</p>",
     "<p class=\"text-white/50 text-xs mt-6\">Weekly/monthly packages · 10\u201315% discount</p>"),
    ("Pilih paket sesuai objective campaign: Standart untuk jangkauan rutin, Business untuk skala lebih besar dengan remarketing aktif.",
     "Choose a package to match your campaign objective: Standard for consistent reach, Business for bigger scale with active remarketing."),
    ("Semua paket sudah termasuk viewers riil (bukan bot), gradual entry, dan support via WhatsApp. Untuk paket mingguan/bulanan atau viewer 500+, chat dulu untuk harga khusus.",
     "All packages include real viewers (not bots), gradual entry, and WhatsApp support. For weekly/monthly packages or 500+ viewers, chat with us first for custom pricing."),

    # ---- Tier fields ----
    ("disclaimer: 'Tanpa kontrak panjang. Berhenti kapan saja.',", "disclaimer: 'No long-term contract. Stop any time.',"),
    ("duration: '30 hari tayang',", "duration: '30 days running',"),
    ("priceNote: 'belum termasuk ad spend Meta',", "priceNote: 'excludes Meta ad spend',"),
    ("priceNote: 'belum termasuk ad spend Google',", "priceNote: 'excludes Google ad spend',"),
    ("priceNote: 'belum termasuk ad spend TikTok',", "priceNote: 'excludes TikTok ad spend',"),
    ("name: 'Standart',", "name: 'Standard',"),

    # ---- Shared FeatureGrid items ----
    ("{ iconName: 'Target', title: 'Targeting Interest', desc: 'Lebih dari 100 kategori minat yang dapat dikombinasikan: perilaku, demografi, hingga hobby spesifik audiens Anda.' },",
     "{ iconName: 'Target', title: 'Interest Targeting', desc: 'More than 100 interest categories that can be combined: behaviour, demographics, right down to your audience\\u2019s specific hobbies.' },"),
    ("{ iconName: 'Repeat', title: 'Remarketing List', desc: 'Menjangkau kembali orang yang pernah mengunjungi website atau berinteraksi dengan iklan sebelumnya — biasanya menghasilkan konversi 3-5x lebih tinggi.' },",
     "{ iconName: 'Repeat', title: 'Remarketing List', desc: 'Re-engage people who visited your website or interacted with previous ads \\u2014 typically converting 3\\u20135x higher.' },"),
    ("{ iconName: 'MapPin', title: 'Target Wilayah', desc: 'Batasi penayangan berdasarkan kota, provinsi, atau radius tertentu. Cocok untuk bisnis lokal di Bandung, Jabodetabek, atau kota tertentu.' },",
     "{ iconName: 'MapPin', title: 'Location Targeting', desc: 'Limit delivery by city, state or a specific radius. Ideal for local businesses in KL, the Klang Valley, Penang or any specific city.' },"),
    ("{ iconName: 'Database', title: 'Lead Database', desc: 'Unggah daftar kontak customer lama atau prospek untuk penayangan iklan khusus — atau buat lookalike audience dari data tersebut.' },",
     "{ iconName: 'Database', title: 'Lead Database', desc: 'Upload your existing customer or prospect lists for dedicated ad delivery \\u2014 or build lookalike audiences from that data.' },"),
    ("{ iconName: 'Users', title: 'Interaksi Audience', desc: 'Sasar orang yang aktif berinteraksi dengan halaman serupa di industri Anda. Lebih efisien daripada targeting minat umum.' },",
     "{ iconName: 'Users', title: 'Audience Engagement', desc: 'Target people who actively engage with similar pages in your industry. More efficient than broad interest targeting.' },"),
    ("{ iconName: 'MessageCircle', title: 'Chat WhatsApp', desc: 'Tombol Call-to-Action langsung mengarah ke WhatsApp — mempersingkat jarak dari tertarik menjadi konsultasi.' },",
     "{ iconName: 'MessageCircle', title: 'WhatsApp Chat', desc: 'Call-to-action buttons that lead straight to WhatsApp \\u2014 shortening the distance from interested to in-conversation.' },"),

    # ---- Shared StepGrid items ----
    ("{ num: '01', tag: 'MINGGU 1', title: 'Brief & Riset', desc: 'Diskusi 30 menit untuk menggali produk, target market, dan tujuan Anda. Kami susun strategi targeting yang sesuai.' },",
     "{ num: '01', tag: 'WEEK 1', title: 'Brief & Research', desc: 'A 30-minute discussion to unpack your product, target market and goals. We draft the right targeting strategy.' },"),
    ("{ num: '02', tag: 'MINGGU 1-2', title: 'Setup & Kreatif', desc: 'Kami siapkan akun iklan & Meta Pixel, dan materi iklan (foto, video, copy). Anda approve, kami eksekusi.' },",
     "{ num: '02', tag: 'WEEK 1-2', title: 'Setup & Creative', desc: 'We prepare the ad account, Meta Pixel and ad materials (photos, video, copy). You approve, we execute.' },"),
    ("{ num: '03', tag: 'MINGGU 2+', title: 'Launch 30 Hari', desc: 'Iklan tayang selama 30 hari penuh di seluruh placement Facebook. Anda menerima laporan setiap Senin pagi.' },",
     "{ num: '03', tag: 'WEEK 2+', title: '30-Day Launch', desc: 'Your ads run for a full 30 days across all Facebook placements. You receive a report every Monday morning.' },"),
    ("{ num: '04', tag: 'ONGOING', title: 'Optimasi & Ganti Iklan', desc: 'Kami monitor performa harian. Iklan yang tidak perform diganti. Yang jalan, di-scale-up.' },",
     "{ num: '04', tag: 'ONGOING', title: 'Optimise & Rotate Ads', desc: 'We monitor performance daily. Underperforming ads get replaced. What works gets scaled up.' },"),
    ("{ num: '02', tag: 'HARI H', title: 'Pembayaran & Persiapan', desc: 'Transfer via QRIS/e-wallet. Invoice langsung dikirim. DP 50% untuk paket besar tersedia.' },",
     "{ num: '02', tag: 'LIVE DAY', title: 'Payment & Preparation', desc: 'Transfer via bank or e-wallet (DuitNow/TNG). Invoice sent immediately. 50% deposit available for larger packages.' },"),
    ("{ num: '04', tag: 'POST-LIVE', title: 'Evaluasi & Recurring', desc: 'Setelah live selesai, kami evaluasi performa FYP. Mau jadwal rutin 2-3x seminggu? Diskon 10-15% untuk paket berulang.' },",
     "{ num: '04', tag: 'POST-LIVE', title: 'Review & Recurring', desc: 'After the live ends, we review FYP performance. Want a regular 2\\u20133x weekly schedule? 10\\u201315% off recurring packages.' },"),

    # ---- Shared FAQs ----
    ("{ q: 'Bisakah iklan diganti di tengah periode berjalan?', a: 'Bisa, dan ini salah satu keuntungan paket kami. Jika Creative A tidak perform, kami ganti dengan Creative B di tengah jalan. Hal yang sama pada copy, audience, atau placement yang perlu disesuaikan.' },",
     "{ q: 'Can ads be changed mid-period?', a: 'Yes \\u2014 and it is one of the advantages of our packages. If Creative A underperforms, we swap in Creative B mid-flight. The same goes for copy, audiences or placements that need adjusting.' },"),
    ("{ q: 'Apakah ada kontrak minimum?', a: 'Tidak ada. Sistem kami bekerja secara bulanan. Anda bebas memutuskan untuk lanjut atau berhenti setiap periode. Ini bentuk komitmen kami untuk menjaga kualitas kerja — bukan jebakan kontrak.' },",
     "{ q: 'Is there a minimum contract?', a: 'No. We work in monthly cycles and you are free to continue or stop at the end of any period. That is our commitment to quality of work \\u2014 not a contract trap.' },"),
    ("{ q: 'Apakah ada kontrak minimum?', a: 'Tidak ada. Sistem kerja bulanan. Anda bebas lanjut atau berhenti setiap periode. Ini bentuk komitmen kami untuk menjaga kualitas kerja — bukan jebakan kontrak.' },",
     "{ q: 'Is there a minimum contract?', a: 'No. We work monthly. You are free to continue or stop each period \\u2014 our commitment to quality of work, not a contract trap.' },"),
    ("{ q: 'Bagaimana laporan yang diberikan?', a: 'Laporan mingguan disusun dalam satu halaman dengan bahasa yang mudah dipahami — bukan sekadar deretan CPM-CTR-CPC. Anda mendapat kejelasan: mana yang berjalan optimal, mana yang perlu disesuaikan, dan rencana aksi untuk minggu depan.' },",
     "{ q: 'What reporting do you provide?', a: 'A one-page weekly report in plain language \\u2014 not just rows of CPM-CTR-CPC. You get clarity: what is performing, what needs adjusting, and the action plan for next week.' },"),
    ("{ q: 'Bisa order untuk viewers lebih dari 500 atau paket mingguan/bulanan?', a: 'Bisa. Untuk 500+ viewers atau paket harian/mingguan dengan jadwal tetap, chat dulu via WA untuk harga terbaik. Recurring 2-3x seminggu bisa diskon 10-15%.' },",
     "{ q: 'Can I order more than 500 viewers, or weekly/monthly packages?', a: 'Yes. For 500+ viewers or daily/weekly packages on a fixed schedule, chat with us on WhatsApp first for the best rate. Recurring 2\\u20133x weekly streams get 10\\u201315% off.' },"),
    ("{ question: 'Bisa order untuk viewers lebih dari 200 atau paket harian?', answer: 'Bisa. Chat dulu via WA untuk harga terbaik. Recurring stream diskon khusus.' },",
     "{ question: 'Can I order more than 200 viewers, or a daily package?', answer: 'Yes. Chat with us on WhatsApp first for the best rate. Recurring streams get special discounts.' },"),

    # ---- Related services (live viewers) ----
    ("{ icon: '🎬', label: 'Jasa View Live YouTube', desc: 'Untuk channel YouTube yang boost watch time & rekomendasi.', href: '/youtube-live-viewers' },",
     "{ icon: '🎬', label: 'YouTube Live Viewers', desc: 'For YouTube channels boosting watch time & recommendations.', href: '/youtube-live-viewers' },"),
    ("{ icon: '🛍️', label: 'Jasa View Live Shopee', desc: 'Untuk seller Shopee Live yang fokus ke konversi produk.', href: '/shopee-live-viewers' },",
     "{ icon: '🛍️', label: 'Shopee Live Viewers', desc: 'For Shopee Live sellers focused on product conversion.', href: '/shopee-live-viewers' },"),

    # ---- Breadcrumbs / misc ----
    ("{ name: \"Beranda\", url: \"https://beriklan.my/\" },", "{ name: \"Home\", url: \"https://beriklan.my/\" },"),
    ("areaServed: \"Indonesia\",", "areaServed: \"Malaysia\","),
    ("mailto:info@beriklan.my?subject=Konsultasi%20Digital%20Marketing", "mailto:info@beriklan.my?subject=Digital%20Marketing%20Consultation"),
]

files = []
for root, dirs, fnames in os.walk(PAGES):
    if "ads-cost" in root:
        continue
    for fn in fnames:
        if fn.endswith(".astro"):
            files.append(os.path.join(root, fn))

pair_hits = {i: 0 for i in range(len(PAIRS))}
for fp in sorted(files):
    txt = open(fp, encoding="utf-8").read()
    orig = txt
    n = 0
    for i, (a, b) in enumerate(PAIRS):
        c = txt.count(a)
        if c:
            txt = txt.replace(a, b)
            n += c
            pair_hits[i] += c
    if txt != orig:
        open(fp, "w", encoding="utf-8").write(txt)
        print(f"[OK] {os.path.relpath(fp, PAGES)}: {n}")

unused = [PAIRS[i][0][:70] for i, c in pair_hits.items() if c == 0]
print(f"\nTotal pairs: {len(PAIRS)}, unused: {len(unused)}")
for u in unused:
    print("  [UNUSED]", u)
