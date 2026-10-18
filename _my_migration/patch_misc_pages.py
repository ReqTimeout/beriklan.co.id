#!/usr/bin/env python3
"""F1-7 pass 4: misc pages -> English. Line-number based (verified via check substring)."""
import json, re, sys

PAGES = "/Users/maabook/Desktop/beriklan.my/web/src/pages/"
SVC = json.load(open("/Users/maabook/Desktop/beriklan.my/web/src/data/services.json"))

E = {}

E['index.astro'] = [
 (19, 'Berapa harga jasa', '{ question: "How much do Beriklan\'s digital marketing services cost?", answer: "Ad management packages start from RM 790 per month depending on the platform. Google Ads management starts from RM 990/month, website development from RM 1,499. Every package includes weekly reports, ongoing optimisation and full access to your own ad accounts." },'),
 (20, 'Apakah ada kontrak minimum', '{ question: "Is there a minimum contract?", answer: "No minimum contract. You can stop at any time without penalty. We would rather keep you with results than lock you into a long contract." },'),
 (21, 'Berapa lama setup campaign', '{ question: "How long does campaign setup take?", answer: "Initial setup takes 1-3 working days for straightforward campaigns, and 5-7 days for complex multi-platform campaigns. After setup, optimisation runs every week." },'),
 (22, 'Apakah tim Beriklan bersertifikat', '{ question: "Is the Beriklan team certified?", answer: "Yes. Our team is a Meta Business Partner (Facebook & Instagram) and Google Partner. These certifications mean we follow platform best practices and have direct access to platform support." },'),
 (23, 'Bagaimana cara tracking', '{ question: "How do I track the results?", answer: "We set up Google Tag Manager + Google Analytics 4 + Meta Pixel on your website. You get real-time dashboard access to see traffic, leads and conversions. Weekly reports are sent via WhatsApp or email." },'),
 (24, 'Apakah ada garansi hasil', '{ question: "Is there a results guarantee?", answer: "We cannot guarantee specific numbers because advertising is dynamic. What we do guarantee: data transparency, regular reports and continuous optimisation. If ROI is off-track in the first month, we review the strategy at no extra cost." },'),
 (28, 'Beranda', '{ name: "Home", url: "https://beriklan.my/" }'),
 (33, 'Agensi digital marketing', 'description: "Performance marketing agency serving Malaysia — managing Meta, Google and TikTok Ads campaigns since 2016. Certified team, weekly reports and measurable strategy for SMEs and mid-sized businesses.",'),
 (46, 'priceRange', 'priceRange: "RM 790 - RM 6,999",'),
 (56, 'title=', 'title="Beriklan.my — Digital Marketing Agency Malaysia | Since 2016"'),
 (57, 'description=', 'description="Performance marketing agency for Malaysia — Facebook Ads, Google Ads, TikTok Ads. Meta & Google certified team managing campaigns since 2016. Contact us."'),
 (104, 'Iklan jalan', '<span class="anim-fade-up">Ads running,</span><br/>'),
 (106, 'Kami tahu', '<span class="anim-fade-up" style="animation-delay: 160ms;">We know <span class="underline decoration-accent decoration-4 underline-offset-4">exactly what</span> to fix.</span>'),
 (110, 'Dari ratusan campaign', 'From the hundreds of campaigns we have audited across industries, one pattern repeats: <strong class="text-ink">budget goes out</strong>, but the results do not match. The cause is usually one of three — <strong class="text-ink">targeting spread too wide</strong>, <strong class="text-ink">ads that miss the audience</strong>, or <strong class="text-ink">a landing page that does not close</strong>. We diagnose first — then build a measurable strategy for your business.'),
 (116, 'Minta Audit', 'Request a Audit'),
 (121, 'Lihat Layanan', 'View Services &amp; Pricing'),
 (128, 'Tim bersertifikasi', '<div class="flex items-center gap-2 trust-item"><span class="check-icon"></span><span class="text-muted"><strong class="text-ink">Meta &amp; Google</strong> certified team</span></div>'),
 (129, 'Laporan', '<div class="flex items-center gap-2 trust-item"><span class="check-icon"></span><span class="text-muted">Reports <strong class="text-ink">every Monday</strong>, clear &amp; structured</span></div>'),
 (186, 'Cara Kami Bekerja', 'How We Work'),
 (191, 'yang membedakan kami', '<span class="text-accent">that set us apart.</span>'),
 (194, 'Bukan sekadar janji', 'Not just promises on paper. You can verify every pillar yourself — from weekly reports and full access to your Meta/Google dashboards, to cost breakdowns that are clear from day one.'),
 (203, 'performance marketing sejak', '<p class="stat-foot">of performance marketing since 2016</p>'),
 (221, 'bukan hanya angka', '<p class="stat-foot">not just numbers without explanation</p>'),
 (228, 'Akses penuh ke akun', '<h3 class="trust-title">Full access to your accounts</h3>'),
 (229, 'Seluruh akun Meta', '<p class="trust-desc">All Meta, Google and TikTok accounts stay under your control. If you ever need to move on, all historical data and configurations transfer without friction.</p>'),
 (233, 'Laporan setiap Senin', '<h3 class="trust-title">Reports every Monday</h3>'),
 (234, 'Disusun dalam satu halaman', '<p class="trust-desc">Written on a single page in plain language. Not rows of numbers without a story — you get clarity: what is performing well, and what needs adjusting.</p>'),
 (239, 'Sistem kerja bulanan', '<p class="trust-desc">A monthly working system. You are free to continue or stop at any time — none of the long contracts common at most agencies.</p>'),
 (314, 'respon dalam 1 jam', 'Team online &middot; replies within 1 hour'),
 (317, 'Bingung apakah iklan', 'Not sure whether your ads<br/>'),
 (318, 'sudah optimal', '<span class="text-accent">are performing at their best?</span>'),
 (321, 'Kami kasih tinjauan', 'We offer a review — just describe your campaign situation via WhatsApp, no account access needed. Our team helps identify what can be improved, then gives concrete recommendations you can act on right away.'),
 (327, 'Mulai Chat', 'Start a WhatsApp Chat'),
 (331, 'Atau email', 'Or email info@beriklan.my'),
 (335, 'Minimum kerja 1 bulan', '<span class="flex items-center gap-1.5"><span class="check-icon-dark"></span> Minimum engagement 1 month</span>'),
 (336, 'Berhenti kapan saja', '<span class="flex items-center gap-1.5"><span class="check-icon-dark"></span> Stop any time, no penalty</span>'),
 (337, 'Pricing transparan', '<span class="flex items-center gap-1.5"><span class="check-icon-dark"></span> Transparent pricing, no ad-spend markup</span>'),
]

E['order.astro'] = [
 (10, 'const waLink', 'const waLink = "https://wa.me/62811919328?text=Hi%20Beriklan%2C%20I%27d%20like%20to%20discuss%20the%20digital%20marketing%20needs%20of%20my%20business.";'),
 (15, '<Layout title=', '<Layout title="Inquiry & Order — Digital Marketing Services | Beriklan" description="Send us your campaign requirements. Contact the Beriklan team: WhatsApp 0811-919-328, email info@beriklan.my, or use the form wizard on this page." canonical="https://beriklan.my/order/">'),
 (32, 'WhatsApp atau Email', 'Inquiry & Order · WhatsApp or Email'),
 (36, 'Pasang Iklan atau', 'Launch Ads or Start a Digital<br/>'),
 (37, 'Kirim Inquiry Anda', '<span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-2 to-accent">Project — Send Your Inquiry.</span>'),
 (41, 'Isi form wizard singkat', 'Fill in the short form wizard below, or contact our team directly via WhatsApp, phone or email. Initial consultation session of 15–30 minutes — free of charge.'),
 (52, 'Isi Form Wizard', 'Fill In the Form Wizard'),
 (69, 'Respon dalam 1 jam', '<p class="contact-sub">Replies within 1 hour (business hours)</p>'),
 (80, 'Untuk inquiry detail', '<p class="contact-sub">For detailed inquiries or proposals</p>'),
 (89, 'Kantor', '<p class="contact-label">Office</p>'),
 (90, 'Bandung, Jawa Barat', '<p class="contact-value">Bandung, Indonesia (HQ)</p>'),
 (111, 'Ceritakan Kebutuhan', 'Tell Us What You Need<br/>'),
 (115, 'Form singkat yang', 'A short form we forward straight to our team\'s WhatsApp — so you never have to type things twice.'),
 (138, 'Bukan janji yang berlebihan', 'No inflated promises.<br/>'),
 (139, 'Komitmen yang dapat', '<span class="text-accent">Commitments you can verify.</span>'),
 (147, 'Seluruh akun Meta', '<p class="trust-desc-dark">All Meta, Google and TikTok accounts stay under your control. If you ever need to move on, all data transfers without friction.</p>'),
 (151, 'Laporan bahasa yang', '<h3 class="trust-title-dark">Reports in plain language</h3>'),
 (152, 'Bukan deretan CPM', '<p class="trust-desc-dark">Not rows of CPM-CTR-CPC without context. You get clarity: what is performing well, and what needs adjusting.</p>'),
 (157, 'Sistem kerja bulanan', '<p class="trust-desc-dark">A monthly working system. You are free to continue or stop at any time — no 6-12 month contracts like most agencies require.</p>'),
 (169, 'Pertanyaan yang Sering', 'Frequently Asked Questions'),
 (179, 'Apakah sesi konsultasi', '<h3 class="font-display font-bold text-base md:text-lg text-ink mb-2">Is the consultation session really free?</h3>'),
 (180, 'Ya, sesi konsultasi awal', '<p class="text-sm md:text-base text-muted leading-relaxed">Yes, the initial 15-consultation via WhatsApp or video call is completely free. We want to understand your needs first before discussing packages and pricing.</p>'),
 (183, 'harus commit setelah', '<h3 class="font-display font-bold text-base md:text-lg text-ink mb-2">Do I have to commit after the consultation?</h3>'),
 (184, 'Tidak ada kewajiban', '<p class="text-sm md:text-base text-muted leading-relaxed">No obligation. After the consultation we send written recommendations via email. You are free to decide whether to proceed — no pressure.</p>'),
 (187, 'Berapa lama respon WhatsApp', '<h3 class="font-display font-bold text-base md:text-lg text-ink mb-2">How fast do you reply on WhatsApp?</h3>'),
 (188, 'Pada jam kerja', '<p class="text-sm md:text-base text-muted leading-relaxed">During business hours (Monday-Saturday, 09.00-18.00 MYT), we reply within 1 hour. Outside business hours, we reply the next morning.</p>'),
 (191, 'Bisa meeting langsung', '<h3 class="font-display font-bold text-base md:text-lg text-ink mb-2">Can we meet in person?</h3>'),
 (192, 'Bisa, dengan janji', '<p class="text-sm md:text-base text-muted leading-relaxed">Our consultations run online via video call or WhatsApp — the most practical option for our Malaysian clients. In-person meetings at our Bandung (Indonesia) HQ are possible by appointment.</p>'),
]

E['clients.astro'] = [
 (8, 'const waLink', 'const waLink = "https://wa.me/62811919328?text=Hi%20Beriklan%2C%20I%20read%20your%20client%20testimonials%20and%20would%20like%20to%20discuss%20a%20campaign%20for%20my%20business.";'),
 (27, 'reviewBody', '"reviewBody": "The Beriklan team is responsive and strategic. Campaign ROI improved significantly.",'),
 (40, 'B2B / Jasa', '{ icon: Building2, label: "B2B / Services" },'),
 (44, 'Andi P.', '{ name: "Mei Ling T.", role: "Fashion Brand Owner", city: "Kuala Lumpur", quote: "The Beriklan team is responsive and strategic. Campaign ROI rose significantly after we migrated from our previous agency.", service: "Facebook Ads", rating: 5 },'),
 (45, 'Citra W.', '{ name: "Aisyah R.", role: "F&B Marketing Manager", city: "Petaling Jaya", quote: "Excellent service — the real-time dashboard lets us monitor performance without waiting for the weekly report.", service: "Google Ads + TikTok Ads", rating: 5 },'),
 (46, 'Budi S.', '{ name: "Dr. Wong K.", role: "Dental Clinic Founder", city: "Penang", quote: "The initial audit exposed the root problem straight away. After Beriklan took over, leads tripled on the same budget.", service: "Google Ads", rating: 5 },'),
 (47, 'Dewi K.', '{ name: "Nurul H.", role: "Skincare Brand Owner", city: "Shah Alam", quote: "A genuinely data-driven approach. Every week we get actionable iteration recommendations.", service: "Facebook + Instagram Ads", rating: 5 },'),
 (48, 'Eko M.', '{ name: "Daniel L.", role: "Property Agent", city: "Johor Bahru", quote: "Quality leads come in daily via WhatsApp. Before this we barely got any.", service: "Facebook Ads + Landing Page", rating: 5 },'),
 (49, 'Fitri N.', '{ name: "Farah A.", role: "Mum & Owner, Baby Food Business", city: "Kota Kinabalu", quote: "Clear technical explanations, never salesy. The team really understands the young-mums market.", service: "Instagram Ads + Content", rating: 5 },'),
 (50, 'Galih H.', '{ name: "Kavin R.", role: "EdTech Founder", city: "Cyberjaya", quote: "With Beriklan since 2020 — consistent leads every month. ROI stays positive even when the market fluctuates.", service: "Meta Ads", rating: 5 },'),
 (51, 'Hadi W.', '{ name: "Hafiz M.", role: "Tour Operator", city: "Langkawi", quote: "They cut our CPA by 60% in 3 months. We are far more confident with ads now.", service: "TikTok Ads", rating: 5 }'),
 (56, 'title=', 'title="Beriklan Clients — Testimonials, Case Studies & Industries | Beriklan"'),
 (57, 'description=', 'description="Beriklan client testimonials across industries: fashion, F&B, property, education, skincare. Average ROI rose significantly after migrating."'),
 (72, 'Klien · 47', 'Clients · 47 SMEs & Mid-Sized Businesses'),
 (75, 'Cerita Klien', 'Client Stories,<br/>'),
 (80, 'Bukan testimonial generic', 'Not generic testimonials. Every testimonial below comes from a real client who'),
 (81, 'memberi izin publikasi', 'gave permission to publish. ROI, CPA, leads — all measurable.'),
 (89, 'Industri yang Kami', '<p class="text-center text-xs font-bold uppercase tracking-[0.2em] text-accent mb-8">Industries We Serve</p>'),
 (139, 'Dari Audit ke 3x', 'From Audit to 3x More Leads'),
 (153, 'Search campaign dengan', '<p class="text-sm text-white/70 mt-2">Search campaign with long-tail keywords</p>'),
 (168, 'Mau Jadi Bagian', '<p class="text-xs font-bold uppercase tracking-[0.2em] text-accent mb-3">Want to Be Part of This Story?</p>'),
 (170, 'Mulai Kampanye Anda', 'Start Your Campaign Today'),
 (173, 'Konsultasi via', 'consultation via WhatsApp — no cost, no obligation.'),
 (177, 'Hubungi Kami', 'Contact Us'),
]

E['press.astro'] = [
 (8, 'const waLink', 'const waLink = "https://wa.me/62811919328?text=Hi%20Beriklan%2C%20I%27d%20like%20a%20consultation%20%E2%80%94%20I%27m%20interested%20in%20your%20certifications%20and%20experience.";'),
 (11, 'Google Partner Status', '{ year: "2024", title: "Google Partner Status", org: "Google", desc: "Officially part of Google Partners. Access to the Google support team." },'),
 (12, 'TikTok Marketing Partner', '{ year: "2024", title: "TikTok Marketing Partner", org: "TikTok", desc: "Officially certified to manage TikTok Ads campaigns." },'),
 (13, 'Meta Business Partner', '{ year: "2020", title: "Meta Business Partner", org: "Meta (Facebook)", desc: "Official access to Meta Business Suite and dedicated Meta support." },'),
 (17, 'Marketing.co.id', '{ outlet: "Marketing In Asia", title: "Digital Advertising Trends for SMEs in Southeast Asia", url: "#" },'),
 (18, 'DailySocial', '{ outlet: "DailySocial.id", title: "Local Targeting Strategies for Performance Campaigns", url: "#" },'),
 (20, 'Bisnis.com', '{ outlet: "Bisnis.com", title: "Performance Marketing Agencies to Watch", url: "#" },'),
 (25, 'title=', 'title="Press & Media — Beriklan in the Media & Partner Certifications | Beriklan"'),
 (26, 'description=', 'description="Media coverage, Meta Business Partner, Google Partner and TikTok Marketing Partner certifications, and industry recognition for Beriklan since 2016."'),
 (40, 'Beriklan di Mata', 'Beriklan in the Eyes of<br/>'),
 (44, 'Bukan klaim sepihak', 'No one-sided claims. The proof: official certifications from the major ad platforms,'),
 (45, 'liputan media', 'coverage in national &amp; regional media, and a 9-year track record managing campaigns.'),
 (82, 'Tampil di Media', '<h2 class="font-display font-extrabold text-3xl md:text-4xl text-ink">Featured in the Media</h2>'),
 (92, 'Baca artikel', '<p class="text-xs text-muted flex items-center gap-1">Read article <ExternalLink class="w-3 h-3" /></p>'),
 (103, 'Mau Bekerja Sama', 'Want to Work With a Certified Agency?'),
 (107, 'Konsultasi 15 Menit', 'Consultation · Free'),
]

E['contact.astro'] = [
 (22, 'priceRange', '"priceRange": "RM 790 - RM 6,999",'),
 (61, 'title=', 'title="Contact Beriklan — WhatsApp, Phone, Email & Address | Beriklan"'),
 (62, 'description=', 'description="Contact the Beriklan team via WhatsApp +62 81-1919-328 or email info@beriklan.my. Replies within 1 hour during business hours."'),
 (77, 'Tim Online', 'Team Online · Replies Within 1 Hour'),
 (80, 'Hubungi Tim', 'Contact the Beriklan<br/>'),
 (81, 'Beriklan Sekarang', '<span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-2 to-accent">Team Now.</span>'),
 (84, 'Pilih channel favorit', 'Pick your favourite channel — WhatsApp, phone or email.'),
 (85, 'Semua ditanggapi', 'Every message is handled by a professional team, not a bot.'),
 (100, 'Respon 1 jam', '<p class="contact-sub">Replies within 1 hour · business hours</p>'),
 (106, 'Telepon', '<p class="contact-label">Phone</p>'),
 (116, 'Respon 24 jam', '<p class="contact-sub">Replies within 24 hours · max</p>'),
 (122, 'Kantor', '<p class="contact-label">Office</p>'),
 (124, 'Bandung 40195', '<p class="contact-sub">Bandung 40195 · Indonesia (HQ)</p>'),
 (142, 'Lokasi Kantor', 'title="Beriklan office location in Bandung"'),
 (146, 'Kantor Pusat', '<p class="text-xs font-bold uppercase tracking-[0.2em] text-accent mb-3">Headquarters</p>'),
 (148, 'Bandung HQ', 'Bandung HQ — Indonesia'),
 (154, 'Alamat', '<p class="font-bold text-ink">Address</p>'),
 (155, 'Jl. Arcamanik Endah No.76, Bandung', '<p class="text-muted">Jl. Arcamanik Endah No.76, Bandung 40195, Indonesia</p>'),
 (161, 'Jam Operasional', '<p class="font-bold text-ink">Operating Hours</p>'),
 (183, 'Konsultasi 15 Menit', '<p class="text-xs font-bold uppercase tracking-[0.2em] text-accent mb-3">Consultation · Free of Charge</p>'),
 (185, 'Langsung Chat WhatsApp', 'Chat With Us on WhatsApp Now'),
]

E['gsc-dashboard.astro'] = [
 (9, "id-ID", "const fmt = (n) => new Intl.NumberFormat('en-MY').format(n);"),
 (16, 'Layout title=', '<Layout title="GSC Monitoring · Beriklan" description="Live Google Search Console monitoring for beriklan.my — clicks, impressions, top queries, freshness alerts. Data refreshed automatically every day." canonical="https://beriklan.my/gsc-dashboard/" noindex={true}>'),
 (34, 'Performa pencarian', 'Organic search performance for <strong class="text-ink">beriklan.my</strong> in Google Search Console — refreshed daily via API. Data window: {gsc.window.start} to {gsc.window.end} ({28} days).'),
 (93, 'Impressions per hari', '<div class="mt-8 text-xs text-muted">Impressions per day. Hover a bar for details.</div>'),
 (191, 'penurunan impressions', '<p class="text-sm text-muted mb-6">Pages with impressions dropping &gt; 40% week-over-week (needs review / content update).</p>'),
 (218, 'impressions tinggi tapi', '<p class="text-sm text-muted mb-6">Pages with high impressions but CTR &lt; 2% — usually a sign the title tag or meta description needs work.</p>'),
 (242, 'Data ini diambil', "<p>This data is pulled directly from the Google Search Console API via a service account (read-only). Auto-refreshed daily via cron. Last update: <strong>{new Date(gsc.last_pulled).toLocaleString('en-MY', { timeZone: 'Asia/Kuala_Lumpur' })}</strong>.</p>"),
]

E['roas-calculator.astro'] = [
 (11, 'description=', 'description="Calculate your ad campaign\'s ROAS (Return on Ad Spend) online. Enter total ad spend and revenue to get a ROAS score plus optimisation recommendations."'),
 (27, 'ROAS (Return on Ad Spend) mengukur', 'ROAS (Return on Ad Spend) measures how effectively every ringgit you spend on ads works. <strong class="text-ink">Enter your campaign data</strong> and see your ROAS score with optimisation recommendations.'),
 (40, 'Apa itu ROAS', '<h2 class="font-display font-extrabold text-2xl md:text-3xl text-ink mb-6">What is ROAS?</h2>'),
 (42, 'ROAS adalah metrik', '<p>ROAS is a metric that measures the revenue generated for every ringgit spent on ads. The formula is simple: <strong class="text-ink">Total Revenue ÷ Total Ad Spend</strong>.</p>'),
 (43, 'Contoh: Jika Anda', '<p>Example: if you spend RM 5,000 on ads and generate RM 20,000, your ROAS is 4x — every RM 1 produces RM 4.</p>'),
 (46, 'Sangat baik', '<li class="flex items-start gap-2"><span class="text-green-500 font-bold">🟢 4x+</span> <span>Very good — consider scaling the budget.</span></li>'),
 (48, 'Perlu optimasi', '<li class="flex items-start gap-2"><span class="text-red-500 font-bold">🔴 &lt; 2x</span> <span>Needs optimisation — review targeting, creative or the landing page.</span></li>'),
]

E['roi-calculator.astro'] = [
 (10, 'title=', 'title="Ad ROI Calculator — Calculate Return on Investment Online | Beriklan"'),
 (11, 'description=', 'description="Calculate your ad campaign\'s ROI (Return on Investment) online. Enter ad budget, production costs, management fee and revenue to get an ROI percentage plus recommendations."'),
 (27, 'ROI menghitung keuntungan', 'ROI calculates your campaign\'s net profit after deducting all costs — including <strong class="text-ink">ad budget, creative production costs and management fees</strong>.'),
 (40, 'Apa itu ROI', '<h2 class="font-display font-extrabold text-2xl md:text-3xl text-ink mb-6">What is ROI?</h2>'),
 (42, 'mengukur keuntungan bersih', '<p><strong class="text-ink">Return on Investment (ROI)</strong> measures a campaign\'s net profit after all costs. Unlike ROAS, which only counts ad spend, ROI accounts for <strong class="text-ink">total costs</strong> including production and management.</p>'),
 (43, 'Rumus ROI', '<p>ROI formula: <strong class="text-ink">(Total Revenue - Total Costs) ÷ Total Costs × 100%</strong></p>'),
 (44, 'Misalnya: Revenue', '<p>Example: revenue RM 20,000, total costs RM 10,000 → ROI = 100%.</p>'),
]

E['ad-budget-calculator.astro'] = [
 (10, 'title=', 'title="Online Ad Budget Calculator — Estimate Facebook, Google & TikTok Ad Costs | Beriklan"'),
 (11, 'description=', 'description="Estimate your digital ad budget for Facebook Ads, Google Ads, TikTok, Instagram & YouTube. Enter your revenue target and platforms to get budget and management-fee recommendations."'),
 (15, 'Kalkulator Budget Iklan', '{ name: "Ad Budget Calculator", url: "https://beriklan.my/ad-budget-calculator/" }'),
 (24, 'Kalkulator Budget Iklan Online', 'Online Ad Budget Calculator'),
 (27, 'Bingung menentukan', 'Not sure how much ad budget is right? Enter your revenue target, pick your platforms, and get a matching <strong class="text-ink">monthly ad spend + management fee</strong> estimate.'),
 (36, 'Cara menggunakan kalkulator', '<h2 class="font-display font-extrabold text-2xl md:text-3xl text-ink mb-6">How to use the ad budget calculator</h2>'),
 (38, 'Pilih platform', '<p><strong class="text-ink">1. Pick platforms</strong> — Choose one or more ad platforms you want to use (Facebook, Instagram, TikTok, Google or YouTube).</p>'),
 (39, 'Tentukan tujuan', '<p><strong class="text-ink">2. Set a goal</strong> — What is the campaign\'s main objective? Leads, sales, brand awareness or website traffic?</p>'),
 (40, 'Target omzet', '<p><strong class="text-ink">3. Revenue target</strong> — Estimate the monthly revenue you want the ads to generate.</p>'),
 (41, 'Dapatkan hasil', '<p><strong class="text-ink">4. Get results</strong> — The calculator returns a typical ad budget + management fee estimate.</p>'),
 (44, 'Butuh bantuan', '<h3 class="font-display font-bold text-lg text-ink mb-2">Need help shaping the strategy?</h3>'),
 (45, 'Tim Beriklan siap', '<p class="text-sm text-muted mb-4">The Beriklan team can help you build a measurable ad strategy — from platform selection to campaign optimisation.</p>'),
 (47, 'Hubungi Kami via', 'Contact Us via WhatsApp →'),
]

E['blog.astro'] = [
 (9, 'const waLink', 'const waLink = "https://wa.me/62811919328?text=Hi%20Beriklan%2C%20I%27d%20like%20a%20consultation";'),
 (12, '<Layout title=', '<Layout title="Digital Marketing Blog — Ads Tips, Google Ads, Meta & TikTok | Beriklan" description="Digital marketing tips, strategies and case studies from the Beriklan team. Learn Facebook Ads, Google Ads, TikTok Ads, Instagram, YouTube and performance marketing." canonical="https://beriklan.my/blog/" nextUrl="https://beriklan.my/blog/page/2/">'),
 (26, 'Belajar Digital Marketing', 'Blog · Learn Digital Marketing'),
 (31, 'dari Pengalaman Nyata', '<span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-2 to-accent">from Real Experience.</span>'),
 (35, 'Artikel, panduan, dan', 'Articles, guides and case studies from the Beriklan team. No empty theory — everything based on data and experience managing campaigns across industries since 2016.'),
 (47, 'Lihat artikel lainnya', 'See more articles <ArrowRight class="w-4 h-4" />'),
 (62, 'Butuh diskusi langsung', 'Need to talk it through?'),
 (65, 'Punya pertanyaan spesifik', 'Have a specific question<br/>'),
 (66, 'yang tidak ada di blog', '<span class="text-accent">not covered on the blog?</span>'),
 (69, 'Sesi konsultasi 15-30 menit', 'A consultation session via WhatsApp. Our team will speak with you directly.'),
 (74, 'Mulai Konsultasi', 'Start a Consultation'),
]

E['blog/[slug].astro'] = [
 (48, 'const waLink', 'const waLink = `https://wa.me/62811919328?text=${encodeURIComponent(`Hi Beriklan, I\'m interested in the topic "${post.title}" — please share more details.`)}`;'),
 (78, 'Semua Topik', "{ id: 'all', label: 'All Topics' },"),
 (88, 'Tim Beriklan', "name: 'Beriklan Team',"),
 (90, 'credentials', "credentials: 'Meta & Google certified team since 2016 · managing campaigns for hundreds of SMEs and mid-sized businesses',"),
 (172, 'Beranda', '<a href="/" class="hover:text-accent transition">Home</a>'),
 (288, 'Mau belajar lebih dalam', '<p class="text-[10px] font-bold uppercase tracking-wider text-accent mb-1.5">Want to go deeper?</p>'),
 (289, 'Panduan Lengkap', '<h4 class="font-display font-bold text-lg text-ink leading-snug mb-2">Complete Guide: {SERVICE_NAMES[post.service] || post.service}</h4>'),
 (290, 'Strategi, format iklan', '<p class="text-xs text-muted leading-relaxed mb-3">Strategy, ad formats, budget optimisation and how to measure ROI — from the Beriklan team.</p>'),
 (292, 'Baca panduan pilar', 'Read the pillar guide'),
 (303, 'Butuh strategi iklan', 'Need an ad strategy for your business?'),
 (306, 'Diskusi gratis 15-30', 'A free 15-30 minute discussion via WhatsApp. Our team will review your current campaign performance.'),
 (332, 'Kembali ke semua artikel', 'Back to all articles'),
 (353, 'Artikel Terbaru', '<h3 class="font-display font-bold text-sm uppercase tracking-wider text-muted mb-4">Latest Articles</h3>'),
 (401, 'Hubungi Kami', '<h3 class="font-display font-extrabold text-lg leading-tight mb-2">Contact Us</h3>'),
 (402, 'Tim kami tinjau', '<p class="text-white/70 text-xs leading-relaxed mb-4">Our team reviews your campaign and gives concrete recommendations.</p>'),
 (403, 'saya baca artikel', '<a href={`https://wa.me/62811919328?text=${encodeURIComponent(`Hi Beriklan, I read the article "${post.title}" and would like to discuss.`)}`} target="_blank" rel="noopener" class="inline-flex items-center gap-1.5 bg-accent text-ink px-4 py-2 rounded-full font-bold text-xs shadow-md hover:shadow-pop transition-all">'),
 (419, 'Artikel Serupa', '<h2 class="text-xs font-bold uppercase tracking-[0.18em] text-accent">Related Articles</h2>'),
]

E['blog/page/[n].astro'] = [
 (42, '<Layout title=', '<Layout title={`Digital Marketing Blog — Page ${pageNum} | Beriklan`} description={`Digital marketing tips, strategies and case studies from the Beriklan team. Page ${pageNum} of ${totalPages}.`} canonical={selfUrl} prevUrl={prevUrl} nextUrl={nextUrl}>'),
 (52, 'Blog · Halaman', 'Blog · Page {pageNum} / {totalPages}'),
 (55, 'Artikel Digital Marketing', 'Digital Marketing Articles<br/>'),
 (56, 'Halaman {pageNum}', '<span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-2 to-accent">Page {pageNum}.</span>'),
 (59, 'Tips, panduan, dan studi', 'Tips, guides and case studies from the Beriklan team — based on data and experience managing campaigns across industries since 2016.'),
 (92, 'Halaman {pageNum} dari', 'Page {pageNum} of {totalPages}'),
 (106, 'Kembali ke halaman utama', '<a href="/blog/" class="text-sm font-bold text-accent hover:underline">← Back to the main blog page</a>'),
]

E['blog/tag/[tag].astro'] = [
 (77, 'const pageDesc', "const pageDesc = `Learn ${keyword.toLowerCase()} — ${tone.tone} from the Beriklan team for Malaysian SMEs and businesses. Curated articles, strategy and practical tips for ${serviceName.toLowerCase()}${cityName ? ' in ' + cityName : ''}.`;"),
 (95, 'Beranda', '<a href="/" class="hover:text-accent transition">Home</a>'),
 (115, 'artikel pilihan tentang', '<>{count} curated articles on <strong class="text-ink">{keyword.toLowerCase()}</strong> from the Beriklan team — selected for {tone.tone} {serviceName.toLowerCase()}{cityName ? ` in ${cityName}` : \'\'}.</>'),
 (117, 'akan kami bahas mendalam', '<>The topic <strong class="text-ink">{keyword.toLowerCase()}</strong> from the Beriklan team. We cover {tone.tone} on {serviceName.toLowerCase()}{cityName ? ` for businesses in ${cityName}` : \'\'} in depth.</>'),
 (136, 'Baca artikel utama', 'Read the main article <ArrowRight class="w-3 h-3" />'),
 (149, 'Artikel tentang', '{count} Articles on "{keyword}"'),
 (169, 'Menampilkan 12 dari', '<p class="text-center text-sm text-muted mt-8">Showing 12 of {matchedPosts.length} articles. See all on the <a href="/blog" class="text-accent hover:underline">main blog</a>.</p>'),
 (178, 'sedang disiapkan', '<h2 class="font-display font-bold text-xl text-ink mb-3">Articles on "{keyword}" are in the works</h2>'),
 (180, 'Tim kami sedang menulis', 'Our team is writing a complete guide on <strong>{keyword.toLowerCase()}</strong>.'),
 (181, 'Untuk diskusi langsung', 'To speak with a consultant directly, tap WhatsApp below or browse our guides on {serviceName.toLowerCase()}{cityName ? \' in \' + cityName : \'\'} on our <a href={`/${service}${cityName ? \'/\' + city.toLowerCase().replace(/[^a-z0-9-]/g, \'\') : \'/\'}`} class="text-accent hover:underline">service page</a>.'),
 (225, 'tanpa komitmen', '<p class="text-white/70 text-sm mb-6">15 minutes via WhatsApp — no commitment. Our team audits your {serviceName.toLowerCase()} campaign{cityName ? ` for businesses in ${cityName}` : \'\'}.</p>'),
 (226, 'saya tertarik topik', '<a href={`https://wa.me/62811919328?text=${encodeURIComponent(`Hi Beriklan, I\'m interested in the topic "${keyword}" for ${serviceName.toLowerCase()}${cityName ? \' in \' + cityName : \'\'}. Please share details.`)}`} target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-accent text-ink px-6 py-3 rounded-full font-bold shadow-lg hover:shadow-pop transition-all">'),
 (227, 'Chat Tim Beriklan', 'Chat With the Beriklan Team <ArrowRight class="w-4 h-4" />'),
]

# block regex replacements (applied AFTER line edits)
svc_display = "const SERVICE_DISPLAY = {\n" + "\n".join(
    "    '%s': '%s'," % (s['slug'], s['name']) for s in SVC) + "\n};"
city_display = """const CITY_DISPLAY = {
    "kuala-lumpur": "Kuala Lumpur", "petaling-jaya": "Petaling Jaya", "shah-alam": "Shah Alam",
    "subang-jaya": "Subang Jaya", "johor-bahru": "Johor Bahru", penang: "Penang",
    "george-town": "George Town", ipoh: "Ipoh", melaka: "Melaka", seremban: "Seremban",
    "kota-kinabalu": "Kota Kinabalu", kuching: "Kuching", klang: "Klang",
    putrajaya: "Putrajaya", cyberjaya: "Cyberjaya", kuantan: "Kuantan", langkawi: "Langkawi",
};"""
intent_tone = """const INTENT_TONE = {
    transactional: { tone: 'how to order', cta: 'Order Now' },
    informational: { tone: 'guides / tutorials', cta: 'Learn More' },
    navigational: { tone: 'contact / location info', cta: 'View Details' },
    commercial: { tone: 'recommendations / comparisons', cta: 'View Recommendations' },
};"""

BLOCKS = {
 'blog/tag/[tag].astro': [
    (r'const SERVICE_DISPLAY = \{.*?\};', svc_display),
    (r'const CITY_DISPLAY = \{.*?\};', city_display),
    (r'const INTENT_TONE = \{.*?\};', intent_tone),
 ],
}

total, miss = 0, 0
for fname, edits in E.items():
    fp = PAGES + fname
    lines = open(fp, encoding='utf-8').read().split('\n')
    for ln, check, new in edits:
        idx = ln - 1
        if idx >= len(lines) or check not in lines[idx]:
            # try +-3 lines drift
            found = None
            for d in (-3, -2, -1, 1, 2, 3):
                j = idx + d
                if 0 <= j < len(lines) and check in lines[j]:
                    found = j; break
            if found is None:
                print('[%s] MISS L%d: %s' % (fname, ln, check)); miss += 1; continue
            idx = found
        old = lines[idx]
        indent = old[:len(old) - len(old.lstrip())]
        lines[idx] = indent + new
        total += 1
    s = '\n'.join(lines)
    for pat, rep in BLOCKS.get(fname, []):
        s, n = re.subn(pat, rep, s, count=1, flags=re.S)
        if n != 1:
            print('[%s] BLOCK MISS: %s' % (fname, pat[:40])); miss += 1
        else:
            total += 1
    open(fp, 'w', encoding='utf-8').write(s)
    print('[%s] done' % fname)

print('TOTAL %d applied, %d missed' % (total, miss))
