#!/usr/bin/env python3
"""F1-8 batch 4: homepage components part 1 -> English (HeroVisual, PainPoints, Method, Services + index anchor)."""
import sys

BASE = "/Users/maabook/Desktop/beriklan.my/web/src/"

FILES = {
    "components/HeroVisual.svelte": [
        ("{ Icon: Check, color: 'green', text: 'Order #387 • Rp 487.000', sub: 'dari Meta Ads' },",
         "{ Icon: Check, color: 'green', text: 'Order #387 • RM 487', sub: 'from Meta Ads' },"),
        ("{ Icon: TrendingUp, color: 'amber', text: 'ROAS naik ke 5.1x', sub: 'TikTok Ads' },",
         "{ Icon: TrendingUp, color: 'amber', text: 'ROAS up to 5.1x', sub: 'TikTok Ads' },"),
        ("{ Icon: MessageCircle, color: 'sky', text: 'Lead baru masuk', sub: 'Google Search Ads' },",
         "{ Icon: MessageCircle, color: 'sky', text: 'New lead received', sub: 'Google Search Ads' },"),
        ("{ Icon: Target, color: 'green', text: 'CPA turun 23%', sub: 'IG Ads minggu ini' },",
         "{ Icon: Target, color: 'green', text: 'CPA down 23%', sub: 'IG Ads this week' },"),
        ("Naik dari <span class=\"text-accent font-bold\">3.1x</span> bulan lalu",
         "Up from <span class=\"text-accent font-bold\">3.1x</span> last month"),
        (">Rp{spend}jt</p>", ">RM{spend}k</p>"),
        (">{revenue}jt</p>", ">RM{revenue}k</p>"),
        (">Rp{cpa}k</p>", ">RM{cpa}</p>"),
        (">Conversion baru</p>", ">New conversion</p>"),
        (">Order #387 • Rp 487.000</p>", ">Order #387 • RM 487</p>"),
        ("dari Meta Ads\n", "from Meta Ads\n"),
        (">TikTok naik ke 5.1x</p>", ">TikTok up to 5.1x</p>"),
        (">+18% minggu ini</p>", ">+18% this week</p>"),
        (">CPA turun 23%</p>", ">CPA down 23%</p>"),
    ],
    "components/PainPoints.svelte": [
        ("title: 'Budget keluar, closing tidak bergerak',", "title: 'Budget going out, sales not moving',"),
        ("body: 'Budget keluar tiap hari. Closing stagnan. Biasanya targeting melebar atau creative tidak selaras dengan audience — baru terasa dampaknya setelah sebulan berjalan.',",
         "body: 'Ad spend goes out every day, yet sales stay flat. Usually the targeting is too broad or the creative is misaligned with the audience — and you only feel it after a month has passed.',"),
        ("title: 'Laporan rutin, tanpa arahan strategis',", "title: 'Routine reports, no strategic direction',"),
        ("body: 'Agency mengirim laporan CPM-CTR-CPC setiap minggu. Anda bingung membaca angka-angka ini. Tidak ada konteks, tidak ada rekomendasi konkret — hanya pajangan metrik.',",
         "body: 'Your agency sends CPM-CTR-CPC reports every week. The numbers are confusing. No context, no concrete recommendations — just a display of metrics.',"),
        ("title: 'Bimbang menentukan platform',", "title: 'Unsure which platform to choose',"),
        ("body: 'Meta dulu? Atau Google? TikTok? Tiap platform punya karakter audience yang berbeda. Salah pilih = buang waktu 3–6 bulan dan budget terkuras tanpa hasil terukur.',",
         "body: 'Meta first? Or Google? TikTok? Each platform has a different audience character. The wrong pick means 3–6 months wasted and a drained budget with no measurable results.',"),
        ("                Tanda-Tanda Bisnis Anda Perlu Kami\n", "                Signs Your Business Needs Us\n"),
        ("Tiga pola yang membuat<br/>", "Three patterns that keep<br/>"),
        ("<span class=\"text-accent\">performa iklan Anda stagnan.</span>",
         "<span class=\"text-accent\">your ad performance stagnant.</span>"),
        ("Jika salah satu terasa dekat dengan kondisi bisnis Anda saat ini, Anda tidak sendirian. Situasi seperti ini umumnya terjadi pada bisnis yang belum pernah ditangani tim yang memahami funnel secara utuh.",
         "If one of these feels close to home, you are not alone. These situations usually happen to businesses that have never been handled by a team that understands the full funnel."),
        ("                            Solusinya?\n", "                            The solution?\n"),
        ("Ketiganya dapat ditangani dalam <span class=\"text-accent\">30–90 hari</span> dengan sistem yang terukur.",
         "All three can be addressed within <span class=\"text-accent\">30–90 days</span> with a measurable system."),
    ],
    "components/Method.svelte": [
        ("title: 'Diagnosa',", "title: 'Diagnose',"),
        ("headline: 'Kami dengar dulu. Baru action.',", "headline: 'We listen first. Then act.',"),
        ("desc: 'Kick-off 30 menit — kami gali goal, budget, audience, hambatan, plus apa yang sudah Anda coba. Output: brief eksekusi yang jadi pegangan tim.',",
         "desc: 'A 30-minute kick-off — we dig into goals, budget, audience, blockers, plus what you have already tried. Output: an execution brief the team works from.',"),
        ("tag: 'MINGGU 1',", "tag: 'WEEK 1',"),
        ("deliverable: 'Brief Strategi',", "deliverable: 'Strategy Brief',"),
        ("deliverables: ['Audit akun lama', 'Persona & mapping', 'Channel decision'],",
         "deliverables: ['Existing account audit', 'Persona & mapping', 'Channel decision'],"),
        ("title: 'Eksekusi',", "title: 'Execute',"),
        ("headline: 'Bangun, launch, monitor.',", "headline: 'Build, launch, monitor.',"),
        ("desc: 'Copy, visual, video, setup tracking — semuanya paralel. Campaign live di minggu ke-2. Anda tetap approve tiap milestone, kami eksekusi.',",
         "desc: 'Copy, visuals, video, tracking setup — all in parallel. Campaigns go live in week 2. You approve every milestone, we execute.',"),
        ("tag: 'MINGGU 2',", "tag: 'WEEK 2',"),
        ("deliverables: ['Creative siap tayang', 'Pixel & tracking oke', 'A/B test aktif'],",
         "deliverables: ['Creatives ready to run', 'Pixel & tracking verified', 'A/B tests active'],"),
        ("title: 'Optimasi',", "title: 'Optimise',"),
        ("headline: 'Pantau ketat. Iterasi cepat.',", "headline: 'Monitor closely. Iterate fast.',"),
        ("desc: 'Review mingguan dari data — bukan asumsi. Yang performanya di bawah standar, kami ganti. Yang jalan, kami scale. Anda cukup approve summary.',",
         "desc: 'Weekly reviews driven by data — not assumptions. Underperformers get replaced. Winners get scaled. You just approve the summary.',"),
        ("tag: 'MINGGU 3+',", "tag: 'WEEK 3+',"),
        ("deliverables: ['Report bahasa yang mudah dipahami', 'Pivot cepat', 'Scaling winner'],",
         "deliverables: ['Plain-language reports', 'Fast pivots', 'Scaling the winners'],"),
        ("                Cara Kerja · Tiga Tahap Terstruktur\n", "                How We Work · Three Structured Phases\n"),
        ("Dari keraguan awal,<br/>", "From early doubts<br/>"),
        ("<span class=\"text-accent\">menuju sistem iklan yang terukur.</span>",
         "<span class=\"text-accent\">to a measurable advertising system.</span>"),
        ("Tidak ada janji berlebihan. Tidak ada proses yang tidak transparan. Setiap minggu, Anda mengetahui secara persis apa yang sedang kami kerjakan dan alasan di baliknya.",
         "No inflated promises. No opaque processes. Every week, you know exactly what we are working on and why."),
        (">Output minggu ini</span>", ">This week's output</span>"),
        ("Halo%20Beriklan%2C%20saya%20mau%20konsultasi", "Hello%20Beriklan%2C%20I%27d%20like%20a%20consultation"),
        ("                    Tanya Detail di WhatsApp\n", "                    Ask Us on WhatsApp\n"),
    ],
    "components/Services.svelte": [
        ("\"https://wa.me/62811919328?text=Halo%20Beriklan%2C%20saya%20mau%20konsultasi\"",
         "\"https://wa.me/62811919328?text=Hello%20Beriklan%2C%20I%27d%20like%20a%20consultation\""),
        ("{ id: 'all', label: 'Semua', count: 9 },", "{ id: 'all', label: 'All', count: 9 },"),
        ("{ id: 'ads', label: 'Iklan', count: 5 },", "{ id: 'ads', label: 'Ads', count: 5 },"),
        ("{ id: 'social', label: 'Sosmed', count: 2 },", "{ id: 'social', label: 'Social', count: 2 },"),
        ("promise: 'Jangkau 120jt+ user Indonesia — disaring by interest, behavior, sampai ke customer Anda yang paling mirip.',",
         "promise: 'Reach 24M+ users in Malaysia — filtered by interest, behaviour, right down to lookalikes of your best customers.',"),
        ("metricLabel: 'ROAS median',", "metricLabel: 'Median ROAS',"),
        ("promise: 'Reels & story yang dirancang untuk menarik perhatian di tiga detik pertama. Cocok untuk brand visual dan F&B — di mana keputusan beli terjadi dalam hitungan menit.',",
         "promise: 'Reels & Stories designed to grab attention in the first three seconds. Ideal for visual brands and F&B — where buying decisions happen in minutes.',"),
        ("features: ['Reels ads', 'Story interaktif', 'Shopping tag', 'Branded content'],",
         "features: ['Reels ads', 'Interactive Stories', 'Shopping tags', 'Branded content'],"),
        ("metricLabel: 'CTR rerata',", "metricLabel: 'Avg CTR',"),
        ("promise: 'Konten native yang dirancang untuk masuk FYP secara organik. Bukan sekadar viral kosong — format yang kami produksi ditujukan untuk menggerakkan audiens hingga ke tahap closing.',",
         "promise: 'Native content built to land on the FYP organically. Not empty virality — the formats we produce are designed to move audiences all the way to a sale.',"),
        ("metric: 'ratusan',\n            metricLabel: 'Closing/bulan',",
         "metric: '100s',\n            metricLabel: 'Sales/month',"),
        ("promise: 'Tangkap buyer yang lagi googling produk/jasa Anda. Intent tinggi = closing lebih cepat, value per lead lebih tinggi.',",
         "promise: 'Capture buyers already googling your product or service. High intent = faster closes and higher value per lead.',"),
        ("metric: 'Rp 1.2rb',\n            metricLabel: 'CPC rerata',",
         "metric: 'RM 0.8',\n            metricLabel: 'Avg CPC',"),
        ("promise: 'Video 6 detik atau in-stream yang memorable. Brand recall yang awet — bukan cuma awareness sebulan.',",
         "promise: 'Memorable 6-second bumpers or in-stream video. Brand recall that lasts — not just a month of awareness.',"),
        ("features: ['In-stream skippable', 'Bumper 6 detik', 'Discovery', 'YouTube Shorts'],",
         "features: ['In-stream skippable', '6-second bumpers', 'Discovery', 'YouTube Shorts'],"),
        ("metricLabel: 'View rate rerata',", "metricLabel: 'Avg view rate',"),
        ("promise: 'Halaman satu-layar yang dirancang untuk mengarahkan kunjungan menjadi chat atau order. Copywriting persuasif dengan A/B test yang sudah disiapkan sejak hari pertama.',",
         "promise: 'A single-screen page built to turn visits into chats or orders. Persuasive copywriting with A/B tests prepared from day one.',"),
        ("features: ['Copywriting persuasif', 'A/B test ready', 'Mobile-first', 'Pixel integrated'],",
         "features: ['Persuasive copywriting', 'A/B test ready', 'Mobile-first', 'Pixel integrated'],"),
        ("metric: '< 2s',\n            metricLabel: 'Waktu muat',", "metric: '< 2s',\n            metricLabel: 'Load time',"),
        ("promise: 'Bukan template pasaran. Custom design, fast load, SEO-ready dari hari pertama — layak jadi \"rumah digital\" bisnis Anda.',",
         "promise: 'Not an off-the-shelf template. Custom design, fast load, SEO-ready from day one — a proper digital home for your business.',"),
        ("features: ['Custom design', 'CMS integrasi', 'SEO on-page', 'Mobile-perfect'],",
         "features: ['Custom design', 'CMS integration', 'On-page SEO', 'Mobile-perfect'],"),
        ("metric: '< 3s',\n            metricLabel: 'Waktu muat',", "metric: '< 3s',\n            metricLabel: 'Load time',"),
        ("title: 'Kelola TikTok',", "title: 'TikTok Management',"),
        ("promise: '30 konten/bulan, dari script sampai report. Anda approve konsep, kami eksekusi. Cocok untuk tim yang tidak sempat.',",
         "promise: 'Up to 20 videos/month, from script to report. You approve the concepts, we execute. Perfect for teams with no time to spare.',"),
        ("features: ['Scriptwriting', 'Edit profesional', 'Posting schedule', 'Monthly report'],",
         "features: ['Scriptwriting', 'Professional editing', 'Posting schedule', 'Monthly report'],"),
        ("metric: '30',\n            metricLabel: 'Konten/bln',",
         "metric: '20',\n            metricLabel: 'Videos/mo',"),
        ("title: 'Kelola Instagram',", "title: 'Instagram Management',"),
        ("promise: 'Feed aesthetic, story aktif, DM dibalas. Sales ngalir tanpa Anda supervise harian — Anda fokus bisnis.',",
         "promise: 'A polished feed, active Stories, DMs answered. Sales keep flowing without daily supervision — you focus on the business.',"),
        ("features: ['Feed aesthetic', 'Story aktif', 'Reels rutin', 'DM response'],",
         "features: ['Polished feed', 'Active Stories', 'Regular Reels', 'DM responses'],"),
        ("metric: 'ratusan',\n            metricLabel: 'Engagement/bulan',",
         "metric: '100s',\n            metricLabel: 'Engagements/mo',"),
        ("document.getElementById('layanan');", "document.getElementById('services');"),
        ('<section id="layanan"', '<section id="services"'),
        (">LAYANAN</text>", ">SERVICES</text>"),
        ("                9 Layanan, Satu Mind\n", "                9 Services, One Mind\n"),
        ("Semua kebutuhan performance<br/>", "Everything performance<br/>"),
        ("<span class=\"text-accent\">marketing, di satu tempat.</span>",
         "<span class=\"text-accent\">marketing, in one place.</span>"),
        ("Tidak perlu koordinasi 3 vendor berbeda. Iklan, landing page, social media — semua disusun sebagai satu sistem yang saling menguatkan.",
         "No need to coordinate 3 different vendors. Ads, landing pages, social media — all built as one system that reinforces itself."),
        ("Butuh rekomendasi atau ingin mendiskusikan anggaran?",
         "Need a recommendation or want to discuss budget?"),
        ("                    Hubungi kami via WhatsApp\n", "                    Consultation on WhatsApp\n"),
    ],
    "pages/index.astro": [
        ('<a href="#layanan"', '<a href="#services"'),
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
        if len(p) > 2 and p[2]:
            txt = txt.replace(a, b)
        else:
            if txt.count(a) > 1:
                print(f"  WARN {fname}: '{a[:60]}' occurs {txt.count(a)}x")
            txt = txt.replace(a, b, 1)
    open(fp, "w", encoding="utf-8").write(txt)
    print(f"{fname} OK — {len(pairs)} replacements")

sys.exit(1 if failed else 0)
