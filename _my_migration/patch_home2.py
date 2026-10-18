#!/usr/bin/env python3
"""F1-8 batch 5: AuditTool + Testimonials -> English + MYR + Malaysian personas."""
import sys

BASE = "/Users/maabook/Desktop/beriklan.my/web/src/components/"

FILES = {
    "AuditTool.svelte": [
        ("{ id: '<5', Icon: Sprout, label: '< Rp 5jt', sub: 'Testing awal' },",
         "{ id: '<5', Icon: Sprout, label: '< RM 2k', sub: 'Early testing' },"),
        ("{ id: '5-15', Icon: Leaf, label: 'Rp 5–15jt', sub: 'Sudah berjalan' },",
         "{ id: '5-15', Icon: Leaf, label: 'RM 2–5k', sub: 'Already running' },"),
        ("{ id: '15-50', Icon: TreePine, label: 'Rp 15–50jt', sub: 'Siap scale' },",
         "{ id: '15-50', Icon: TreePine, label: 'RM 5–15k', sub: 'Ready to scale' },"),
        ("{ id: '50+', Icon: Rocket, label: 'Rp 50jt+', sub: 'Enterprise' },",
         "{ id: '50+', Icon: Rocket, label: 'RM 15k+', sub: 'Enterprise' },"),
        ("{ id: '<3', Icon: Timer, label: '< 3 bulan', sub: 'Baru mulai' },",
         "{ id: '<3', Icon: Timer, label: '< 3 months', sub: 'Just started' },"),
        ("{ id: '3-6', Icon: Calendar, label: '3–6 bulan', sub: 'Cari validasi' },",
         "{ id: '3-6', Icon: Calendar, label: '3–6 months', sub: 'Seeking validation' },"),
        ("{ id: '6-12', Icon: CalendarDays, label: '6–12 bulan', sub: 'Sudah PMF' },",
         "{ id: '6-12', Icon: CalendarDays, label: '6–12 months', sub: 'Found PMF' },"),
        ("{ id: '12+', Icon: Trophy, label: '> 1 tahun', sub: 'Mapan, optimasi' },",
         "{ id: '12+', Icon: Trophy, label: '> 1 year', sub: 'Established, optimising' },"),
        ("{ id: 'leads', Icon: Phone, label: 'Leads / Inquiry', sub: 'Penjualan via chat/call' },",
         "{ id: 'leads', Icon: Phone, label: 'Leads / Enquiries', sub: 'Sales via chat/call' },"),
        ("{ id: 'sales', Icon: ShoppingCart, label: 'Direct Sales', sub: 'Transaksi langsung' },",
         "{ id: 'sales', Icon: ShoppingCart, label: 'Direct Sales', sub: 'Direct transactions' },"),
        ("{ id: 'awareness', Icon: MegaphoneIcon, label: 'Brand Awareness', sub: 'Jangkauan luas' },",
         "{ id: 'awareness', Icon: MegaphoneIcon, label: 'Brand Awareness', sub: 'Broad reach' },"),
        ("{ id: 'traffic', Icon: Globe, label: 'Website Traffic', sub: 'Kunjungan organik' },",
         "{ id: 'traffic', Icon: Globe, label: 'Website Traffic', sub: 'Organic visits' },"),
        ("{ key: 'platform', title: 'Platform iklan mana yang jadi fokus utama?', sub: 'Pilih yang paling dominan di campaign Anda saat ini.', data: platforms },",
         "{ key: 'platform', title: 'Which ad platform is your main focus?', sub: 'Pick the most dominant one in your current campaigns.', data: platforms },"),
        ("{ key: 'budget', title: 'Berapa budget iklan yang Anda alokasikan per bulan?', sub: 'Termasuk ad spend + biaya agency (kalau ada).', data: budgets },",
         "{ key: 'budget', title: 'How much ad budget do you allocate per month?', sub: 'Including ad spend + agency fees (if any).', data: budgets },"),
        ("{ key: 'duration', title: 'Sudah berapa lama Anda jalanin iklan digital?', sub: 'Termasuk yang Anda kelola sendiri atau pakai agency lain.', data: durations },",
         "{ key: 'duration', title: 'How long have you been running digital ads?', sub: 'Including self-managed or with another agency.', data: durations },"),
        ("{ key: 'goal', title: 'Apa objective utama campaign Anda?', sub: 'Fokus goal yang paling ingin dicapai 6 bulan ke depan.', data: goals },",
         "{ key: 'goal', title: 'What is your main campaign objective?', sub: 'The goal you most want to reach in the next 6 months.', data: goals },"),
        ("let price = '2.500.000';", "let price = '990';"),
        ("if (budget === '<5') { pkg = 'Starter'; price = '2.500.000'; reasoning.push('Cocok untuk tahap testing awal.'); matchScore = 92; }",
         "if (budget === '<5') { pkg = 'Starter'; price = '990'; reasoning.push('A good fit for the early testing stage.'); matchScore = 92; }"),
        ("else if (budget === '5-15') { pkg = 'Growth'; price = '5.000.000'; reasoning.push('Sudah menemukan product-market fit, siap untuk scale-up.'); matchScore = 96; }",
         "else if (budget === '5-15') { pkg = 'Growth'; price = '1,990'; reasoning.push('You have found product-market fit and are ready to scale up.'); matchScore = 96; }"),
        ("else if (budget === '15-50') { pkg = 'Scale'; price = '10.000.000+'; reasoning.push('Budget besar butuh full funnel management.'); matchScore = 98; }",
         "else if (budget === '15-50') { pkg = 'Scale'; price = '2,990+'; reasoning.push('A bigger budget needs full-funnel management.'); matchScore = 98; }"),
        ("else { pkg = 'Scale'; price = 'Custom'; reasoning.push('Custom retainer — dedicated team untuk hasil maksimal.'); matchScore = 99; }",
         "else { pkg = 'Scale'; price = 'Custom'; reasoning.push('Custom retainer — a dedicated team for maximum results.'); matchScore = 99; }"),
        ("if (duration === '<3' && goal === 'awareness') reasoning.push('Fokus ke creative testing di awal untuk find winning formula.');",
         "if (duration === '<3' && goal === 'awareness') reasoning.push('Focus on creative testing early to find the winning formula.');"),
        ("if (duration === '12+' && goal === 'sales') reasoning.push('Tinggal refine — optimasi CPA + scale yang sudah jalan.');",
         "if (duration === '12+' && goal === 'sales') reasoning.push('Just refine — optimise CPA and scale what already works.');"),
        ("if (platform === 'multi') reasoning.push('Multi-platform perlu creative variant per channel.');",
         "if (platform === 'multi') reasoning.push('Multi-platform requires creative variants per channel.');"),
        ("if (platform === 'tiktok' && goal === 'leads') reasoning.push('TikTok cocok untuk top funnel, perlu pairing Meta untuk retargeting.');",
         "if (platform === 'tiktok' && goal === 'leads') reasoning.push('TikTok works for top of funnel; pair it with Meta for retargeting.');"),
        ("                AI Audit · 60 detik\n", "                AI Audit · 60 seconds\n"),
        ("Jawab 4 pertanyaan,\n", "Answer 4 questions,\n"),
        ("<span class=\"block mt-2 text-accent\">kami rekomendasikan paket Anda.</span>",
         "<span class=\"block mt-2 text-accent\">we recommend your package.</span>"),
        ("Bukan kuis tanpa isi — Anda akan memperoleh estimasi paket + range harga yang cocok untuk situasi Anda saat ini.",
         "Not an empty quiz — you get a package estimate + a price range that fits your current situation."),
        ("{Math.round(progress)}% selesai", "{Math.round(progress)}% done"),
        ("                                Kembali\n", "                                Back\n"),
        (">Klik salah satu opsi untuk lanjut</span>", ">Click an option to continue</span>"),
        ("Audit selesai · Match score {recommendation.matchScore}%",
         "Audit complete · Match score {recommendation.matchScore}%"),
        (">Berdasarkan jawaban Anda, kami rekomendasikan:</p>", ">Based on your answers, we recommend:</p>"),
        (">Paket {recommendation.pkg}</h3>", ">{recommendation.pkg} Package</h3>"),
        ("Estimasi biaya: <span class=\"font-bold text-white\">Rp {recommendation.price}</span> / bulan",
         "Estimated fee: <span class=\"font-bold text-white\">RM {recommendation.price}</span> / month"),
        (">💡 Kenapa paket ini:</p>", ">💡 Why this package:</p>"),
        ("Halo%20Beriklan%2C%20saya%20baru%20selesai%20audit%20dan%20direkomendasikan%20paket%20{recommendation.pkg}",
         "Hello%20Beriklan%2C%20I%20just%20completed%20the%20audit%20and%20was%20recommended%20the%20{recommendation.pkg}%20package"),
        ("                            Diskusi Paket Ini\n", "                            Discuss This Package\n"),
        ("                            Ulangi Audit\n", "                            Restart Audit\n"),
        ("🔒 Data Anda aman — tidak disimpan, hanya untuk rekomendasi langsung.",
         "🔒 Your data is safe — nothing is stored, it is only used for this recommendation."),
    ],
    "Testimonials.svelte": [
        ("quote: 'Kami sempat mengelola iklan sendiri hampir setahun. Hasilnya naik turun dan menyita waktu tim internal. Setelah bekerja sama dengan Beriklan, ROAS meningkat dari 1.8x menjadi 4.5x dalam empat bulan. Yang paling kami apresiasi: laporan disusun dengan bahasa yang jelas dan setiap perubahan dapat kami pahami.',",
         "quote: 'We managed our own ads for almost a year. Results were up and down and it drained our internal team. After working with Beriklan, ROAS improved from 1.8x to 4.5x in four months. What we appreciate most: reports are written in plain language and we understand every change made.',"),
        ("name: 'Andini Pratiwi',", "name: 'Nurul Aisyah',"),
        ("biz: 'Brand Skincare, Bandung',", "biz: 'Skincare Brand, Kuala Lumpur',"),
        ("metricLabel: 'dalam 4 bulan',", "metricLabel: 'in 4 months',"),
        ("quote: 'Awalnya kami skeptis menggandeng agensi, namun setelah dua bulan pertama, akhirnya kami memahami perbedaannya. Yang paling terasa: setiap Senin pagi selalu ada laporan dalam bahasa yang mudah dipahami — bukan hanya deretan angka CPM dan CTR, tetapi apa yang perlu diubah dan mengapa.',",
         "quote: 'We were sceptical about hiring an agency at first, but after the first two months we finally understood the difference. What stands out: every Monday morning there is a report in plain language — not just rows of CPM and CTR numbers, but what needs to change and why.',"),
        ("name: 'Rizky Maulana',", "name: 'Amirul Hakim',"),
        ("biz: 'Klinik Kecantikan, Jakarta',", "biz: 'Aesthetic Clinic, Petaling Jaya',"),
        ("metric: 'Lead konsisten 3x lipat',", "metric: 'Leads consistently 3x',"),
        ("metricLabel: 'dari bulan ke-2',", "metricLabel: 'from month 2',"),
        ("industry: 'Klinik',", "industry: 'Clinic',"),
        ("quote: 'Kampanye TikTok Ads dari Beriklan berhasil menembus FYP secara organik. Dari nol pengikut menjadi 12.000 dalam dua bulan, dengan rasio closing 8% per video. Proses kreatif dilakukan secara kolaboratif, bukan sekadar posting rutin.',",
         "quote: 'Beriklan\\'s TikTok Ads campaigns broke into the FYP organically. From zero followers to 12,000 in two months, with an 8% closing rate per video. The creative process is collaborative, not just routine posting.',"),
        ("name: 'Bayu Adhi',", "name: 'Tan Wei Jian',"),
        ("biz: 'Edutech, Jakarta',", "biz: 'Edutech, Kuala Lumpur',"),
        ("metric: '0 → 12K pengikut',", "metric: '0 → 12K followers',"),
        ("metricLabel: 'closing 8% / video',", "metricLabel: '8% closing / video',"),
        ("quote: 'Sebagai pemilik brand F&B, saya biasanya tidak terlalu memperhatikan aspek marketing. Setelah Tim Beriklan menyampaikan laporan dengan bahasa yang mudah dipahami, baru saya sadari bahwa biaya yang sebelumnya kami keluarkan untuk agensi lain ternyata hanya menaikkan CPM tanpa hasil yang terukur. Saat ini ROI setiap bulan positif.',",
         "quote: 'As an F&B brand owner, I never paid much attention to marketing. Once the Beriklan team delivered reports in plain language, I realised our previous agency spend was only inflating CPM with no measurable results. Now our ROI is positive every month.',"),
        ("name: 'Hendro Wibowo',", "name: 'Faizal Rahman',"),
        ("biz: 'Restoran Lokal, Jabodetabek',", "biz: 'Local Restaurant, Klang Valley',"),
        ("metric: 'ROI positif',", "metric: 'Positive ROI',"),
        ("metricLabel: 'tiap bulan sejak Q2',", "metricLabel: 'every month since Q2',"),
        ("quote: 'Karakteristik funnel B2B berbeda signifikan dari FMCG. Beriklan memahami hal ini dan menyusun strategi yang relevan, tanpa pendekatan copy-paste dari kampanye ritel. qualified leads kami naik 180% di Q3. Investasi yang sebanding dengan hasilnya.',",
         "quote: 'B2B funnels behave very differently from FMCG. Beriklan understands this and built a relevant strategy, without copy-pasting retail campaign playbooks. Our qualified leads grew 180% in Q3. An investment that matched its returns.',"),
        ("name: 'Sarah Nathania',", "name: 'Michelle Lim',"),
        ("biz: 'SaaS B2B, Jakarta',", "biz: 'B2B SaaS, Kuala Lumpur',"),
        ("metricLabel: 'di Q3 2025',", "metricLabel: 'in Q3 2025',"),
        ("quote: 'Tim Beriklan mengelola akun Instagram secara menyeluruh — mulai dari penulisan skrip, penyuntingan, penjadwalan posting, hingga balasan DM. Kami hanya menerima laporan hasil. Dalam tiga bulan pertama, penjualan dari Instagram naik tiga kali lipat. Sangat membantu untuk bisnis yang sedang dalam tahap ekspansi.',",
         "quote: 'The Beriklan team manages our Instagram end-to-end — scriptwriting, editing, post scheduling, right through to DM replies. We just receive the results report. In the first three months, Instagram sales tripled. A huge help for a business in expansion mode.',"),
        ("name: 'Aulia Rahma',", "name: 'Siti Zulaikha',"),
        ("biz: 'Brand Fashion, Surabaya',", "biz: 'Fashion Brand, Johor Bahru',"),
        ("metric: 'Penjualan IG naik 3x',", "metric: 'IG sales up 3x',"),
        ("metricLabel: 'dalam 3 bulan',", "metricLabel: 'in 3 months',"),
        ("\"https://wa.me/62811919328?text=Halo%20Beriklan%2C%20saya%20ingin%20konsultasi%20mengenai%20campaign%20iklan%20saya\"",
         "\"https://wa.me/62811919328?text=Hello%20Beriklan%2C%20I%27d%20like%20to%20discuss%20my%20ad%20campaigns\""),
        ("                Studi Kasus & Testimoni\n", "                Case Studies & Testimonials\n"),
        ("Pengalaman mereka yang telah<br/>", "Stories from businesses that<br/>"),
        ("<span class=\"text-accent\">bekerja sama dengan Tim Beriklan.</span>",
         "<span class=\"text-accent\">have worked with the Beriklan team.</span>"),
        ("Setiap testimoni disertai nama, industri, serta data yang terukur. Anda dapat melakukan verifikasi langsung kepada klien kami bila diperlukan.",
         "Every testimonial includes a name, industry and measurable data. You can verify directly with our clients if needed."),
        ("aria-label={isPaused ? 'Lanjutkan rotasi' : 'Jeda rotasi'}",
         "aria-label={isPaused ? 'Resume rotation' : 'Pause rotation'}"),
        ("{isPaused ? 'Lanjut' : 'Jeda'}", "{isPaused ? 'Resume' : 'Pause'}"),
        ('aria-label="Lihat testimoni {i + 1}"', 'aria-label="View testimonial {i + 1}"'),
        ('aria-label="Lihat testimoni dari {t.name}"', 'aria-label="View testimonial from {t.name}"'),
        ("Saatnya giliran Anda. <span class=\"text-ink font-semibold not-italic\">Mari kita telaah campaign Anda secara mendalam.</span>",
         "Your turn next. <span class=\"text-ink font-semibold not-italic\">Let's take a deep look at your campaigns.</span>"),
        ("                Jadwalkan Konsultasi\n", "                Book a Consultation\n"),
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
            print("  MISSING:", repr(m[:100]))
        continue
    for p in pairs:
        a, b = p[0], p[1]
        if txt.count(a) > 1:
            print(f"  WARN {fname}: '{a[:60]}' occurs {txt.count(a)}x")
        txt = txt.replace(a, b, 1)
    open(fp, "w", encoding="utf-8").write(txt)
    print(f"{fname} OK — {len(pairs)} replacements")

sys.exit(1 if failed else 0)
