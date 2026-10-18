#!/usr/bin/env python3
"""F1-8 batch 6: BudgetCalculator + ROICalculator + ROASCalculator + OrderWizard + BlogFilter -> English + MYR."""
import sys

BASE = "/Users/maabook/Desktop/beriklan.my/web/src/components/"

FILES = {
    "BudgetCalculator.svelte": [
        ("let monthlyTarget = 50000000;", "let monthlyTarget = 50000;"),
        ("platforms = []; goal = null; monthlyTarget = 50000000; step = 0;",
         "platforms = []; goal = null; monthlyTarget = 50000; step = 0;"),
        ("desc: 'Target audiens presisi' },", "desc: 'Precise audience targeting' },"),
        ("{ id: 'leads', label: 'Leads / Inquiry', desc: 'Target: leads via WhatsApp, form, telepon', multiplier: 0.25 },",
         "{ id: 'leads', label: 'Leads / Enquiries', desc: 'Target: leads via WhatsApp, form, phone', multiplier: 0.25 },"),
        ("{ id: 'sales', label: 'Penjualan Online', desc: 'Target: transaksi e-commerce langsung', multiplier: 0.30 },",
         "{ id: 'sales', label: 'Online Sales', desc: 'Target: direct e-commerce transactions', multiplier: 0.30 },"),
        ("{ id: 'awareness', label: 'Brand Awareness', desc: 'Target: reach dan impressions luas', multiplier: 0.20 },",
         "{ id: 'awareness', label: 'Brand Awareness', desc: 'Target: broad reach and impressions', multiplier: 0.20 },"),
        ("{ id: 'traffic', label: 'Traffic Website', desc: 'Target: kunjungan ke landing page', multiplier: 0.15 },",
         "{ id: 'traffic', label: 'Website Traffic', desc: 'Target: visits to your landing page', multiplier: 0.15 },"),
        ("""        { value: 10000000, label: 'Rp 10 juta' },
        { value: 25000000, label: 'Rp 25 juta' },
        { value: 50000000, label: 'Rp 50 juta' },
        { value: 100000000, label: 'Rp 100 juta' },
        { value: 250000000, label: 'Rp 250 juta' },
        { value: 500000000, label: 'Rp 500 juta' },
        { value: 1000000000, label: 'Rp 1 miliar' },""",
         """        { value: 10000, label: 'RM 10k' },
        { value: 25000, label: 'RM 25k' },
        { value: 50000, label: 'RM 50k' },
        { value: 100000, label: 'RM 100k' },
        { value: 250000, label: 'RM 250k' },
        { value: 500000, label: 'RM 500k' },
        { value: 1000000, label: 'RM 1 million' },"""),
        ("""        if (val >= 1000000000) return 'Rp ' + (val / 1000000000).toFixed(1) + ' miliar';
        if (val >= 1000000) return 'Rp ' + (val / 1000000).toFixed(val >= 100000000 ? 0 : 1) + ' juta';
        return 'Rp ' + val.toLocaleString('id-ID');""",
         """        if (val >= 1000000) return 'RM ' + (val / 1000000).toFixed(1) + ' million';
        if (val >= 1000) return 'RM ' + (val / 1000).toFixed(val >= 100000 ? 0 : 1) + 'k';
        return 'RM ' + val.toLocaleString('en-MY');"""),
        ("""        const min = Math.round(raw * 0.8 / 100000) * 100000;
        const max = Math.round(raw * 1.2 / 100000) * 100000;""",
         """        const min = Math.round(raw * 0.8 / 100) * 100;
        const max = Math.round(raw * 1.2 / 100) * 100;"""),
        ("""        if (max <= 3000000) managementFee = 'Rp 1.000.000 - 1.750.000';
        else if (max <= 10000000) managementFee = 'Rp 1.750.000 - 3.750.000';
        else managementFee = 'Rp 3.750.000 - 6.000.000';""",
         """        if (max <= 3000) managementFee = 'RM 990 - 1,490';
        else if (max <= 10000) managementFee = 'RM 1,490 - 2,490';
        else managementFee = 'RM 2,490 - 3,990';"""),
        ("if (platformCount > 2) tips.push('Fokus ke 1-2 platform dengan performa terbaik dulu sebelum ekspansi ke platform lain.');",
         "if (platformCount > 2) tips.push('Focus on the 1-2 best-performing platforms first before expanding to others.');"),
        ("tips.push('Facebook Ads umumnya platform terbaik untuk leads/WhatsApp di Indonesia.');",
         "tips.push('Facebook Ads is generally the best platform for leads/WhatsApp in Malaysia.');"),
        ("tips.push('Google Ads sangat efektif untuk direct sales karena menangkap high-intent traffic.');",
         "tips.push('Google Ads is highly effective for direct sales because it captures high-intent traffic.');"),
        ("tips.push('TikTok punya CPM termurah untuk awareness campaign.');",
         "tips.push('TikTok has the cheapest CPM for awareness campaigns.');"),
        ("`Halo Beriklan, saya baru selesai kalkulasi budget iklan. Saya butuh budget iklan sekitar ${result.budgetRange} untuk ${platforms.length} platform. Mohon info lebih lanjut.`",
         "`Hello Beriklan, I just calculated my ad budget. I need an ad budget of around ${result.budgetRange} for ${platforms.length} platform(s). Please share more details.`"),
        ("                    Kalkulator Budget Iklan\n", "                    Ad Budget Calculator\n"),
        ("Berapa budget iklan yang<br/>", "What is the right ad budget<br/>"),
        ("<span class=\"text-accent\">tepat untuk bisnis Anda?</span>", "<span class=\"text-accent\">for your business?</span>"),
        ("Jawab 3 pertanyaan sederhana, dapatkan estimasi budget iklan + biaya management yang sesuai.",
         "Answer 3 simple questions to get an estimated ad budget + a matching management fee."),
        (">Pilih platform iklan</h3>", ">Choose your ad platforms</h3>"),
        ("Pilih satu atau lebih platform yang ingin Anda gunakan.", "Select one or more platforms you want to use."),
        (">Pilih minimal 1 platform</span>", ">Select at least 1 platform</span>"),
        ("                                    Lanjut\n", "                                    Next\n"),
        (">Apa tujuan utama campaign Anda?</h3>", ">What is your main campaign goal?</h3>"),
        ("Pilih satu tujuan yang paling prioritas.", "Pick the single highest-priority goal."),
        (">Klik salah satu opsi</span>", ">Click one of the options</span>"),
        ("                                    Kembali\n", "                                    Back\n", True),
        (">Target omzet bulanan?</h3>", ">Monthly revenue target?</h3>"),
        ("Perkirakan pendapatan yang ingin Anda capai per bulan dari iklan.",
         "Estimate the monthly revenue you want to reach from ads."),
        (">Target omzet bulanan</p>", ">Monthly revenue target</p>"),
        ("<span>Rp 10 jt</span>", "<span>RM 10k</span>"),
        ("<span>Rp 1 M</span>", "<span>RM 1M</span>"),
        ("                                    Hitung Budget\n", "                                    Calculate Budget\n"),
        ("                                Kalkulasi selesai\n", "                                Calculation complete\n"),
        ("Estimasi budget iklan (ad spend) per bulan:", "Estimated ad budget (ad spend) per month:"),
        ("+ biaya management: {result.managementFee}/bln", "+ management fee: {result.managementFee}/month"),
        (">💡 Tips untuk Anda:</p>", ">💡 Tips for you:</p>"),
        ("                                Diskusi via WhatsApp\n", "                                Discuss via WhatsApp\n"),
        (">Hitung Ulang</button>", ">Recalculate</button>"),
    ],
    "ROICalculator.svelte": [
        ("""    let adSpend = 5000000;
    let productionCost = 2000000;
    let managementFee = 1750000;
    let totalRevenue = 20000000;""",
         """    let adSpend = 5000;
    let productionCost = 2000;
    let managementFee = 1490;
    let totalRevenue = 20000;"""),
        ("rating: roi >= 100 ? 'baik' : roi >= 0 ? 'cukup' : 'rugi',",
         "rating: roi >= 100 ? 'good' : roi >= 0 ? 'fair' : 'loss',"),
        ("label: roi >= 100 ? 'Menguntungkan' : roi >= 0 ? 'Balik Modal' : 'Rugi',",
         "label: roi >= 100 ? 'Profitable' : roi >= 0 ? 'Break-even' : 'Loss',"),
        ("return 'Rp ' + val.toLocaleString('id-ID');", "return 'RM ' + val.toLocaleString('en-MY');"),
        (">Kalkulator ROI</h3>", ">ROI Calculator</h3>"),
        ("Return on Investment — hitung keuntungan bersih campaign Anda.",
         "Return on Investment — calculate your campaign's net profit."),
        (">Budget Iklan (Ad Spend)</label>", ">Ad Budget (Ad Spend)</label>"),
        (">Biaya Produksi Kreatif</label>", ">Creative Production Cost</label>"),
        (">Rp</span>", ">RM</span>", True),
        ("min=\"0\" step=\"100000\"", "min=\"0\" step=\"100\"", True),
        ("{#if result.rating === 'baik'}🟢{:else if result.rating === 'cukup'}🟡{:else}🔴{/if}",
         "{#if result.rating === 'good'}🟢{:else if result.rating === 'fair'}🟡{:else}🔴{/if}"),
        (">Total Biaya</p>", ">Total Cost</p>"),
        (">Keuntungan Bersih</p>", ">Net Profit</p>"),
        ("{#if result.rating === 'rugi'}", "{#if result.rating === 'loss'}"),
        ("{:else if result.rating === 'cukup'}", "{:else if result.rating === 'fair'}"),
        ("<p>💡 ROI negatif berarti total biaya melebihi revenue. Evaluasi struktur biaya atau optimasi campaign.</p>",
         "<p>💡 Negative ROI means total costs exceed revenue. Review your cost structure or optimise the campaign.</p>"),
        ("<p>💡 ROI 0-100% berarti balik modal dengan margin tipis. Fokus ke efisiensi biaya dan scale yang sudah bekerja.</p>",
         "<p>💡 ROI of 0-100% means break-even with thin margins. Focus on cost efficiency and scale what already works.</p>"),
        ("<p>✅ ROI di atas 100% menguntungkan. Pertimbangkan scale budget untuk hasil lebih besar.</p>",
         "<p>✅ ROI above 100% is profitable. Consider scaling your budget for bigger results.</p>"),
        ("Masukkan data biaya dan revenue untuk menghitung ROI.",
         "Enter your cost and revenue figures to calculate ROI."),
        ("Halo%20Beriklan%2C%20saya%20ingin%20konsultasi%20ROI%20campaign%20saya.",
         "Hello%20Beriklan%2C%20I%27d%20like%20to%20discuss%20my%20campaign%20ROI."),
        ("Konsultasi ROI dengan Tim Beriklan →", "Discuss ROI with the Beriklan Team →"),
    ],
    "ROASCalculator.svelte": [
        ("""    let adSpend = 5000000;
    let revenue = 15000000;""",
         """    let adSpend = 5000;
    let revenue = 15000;"""),
        ("rating: roas >= 4 ? 'baik' : roas >= 2 ? 'cukup' : 'perlu-optimasi',",
         "rating: roas >= 4 ? 'good' : roas >= 2 ? 'fair' : 'needs-work',"),
        ("label: roas >= 4 ? 'Baik' : roas >= 2 ? 'Cukup' : 'Perlu Optimasi',",
         "label: roas >= 4 ? 'Good' : roas >= 2 ? 'Fair' : 'Needs Optimisation',"),
        ("return 'Rp ' + val.toLocaleString('id-ID');", "return 'RM ' + val.toLocaleString('en-MY');"),
        (">Kalkulator ROAS</h3>", ">ROAS Calculator</h3>"),
        ("Return on Ad Spend — hitung efektivitas belanja iklan Anda.",
         "Return on Ad Spend — measure how effective your ad spend is."),
        (">Total Belanja Iklan</label>", ">Total Ad Spend</label>"),
        (">Total Pendapatan dari Iklan</label>", ">Total Revenue from Ads</label>"),
        (">Rp</span>", ">RM</span>", True),
        ("min=\"0\" step=\"100000\"", "min=\"0\" step=\"100\"", True),
        (">ROAS Anda</p>", ">Your ROAS</p>"),
        ("{#if result.rating === 'baik'}🟢{:else if result.rating === 'cukup'}🟡{:else}🔴{/if}",
         "{#if result.rating === 'good'}🟢{:else if result.rating === 'fair'}🟡{:else}🔴{/if}"),
        ("<span>Referensi: 4x+ = Baik</span>", "<span>Benchmark: 4x+ = Good</span>"),
        ("{result.rating === 'baik' ? 'bg-green-500' : result.rating === 'cukup' ? 'bg-accent' : 'bg-red-500'}",
         "{result.rating === 'good' ? 'bg-green-500' : result.rating === 'fair' ? 'bg-accent' : 'bg-red-500'}"),
        ("{#if result.rating === 'perlu-optimasi'}", "{#if result.rating === 'needs-work'}"),
        ("{:else if result.rating === 'cukup'}", "{:else if result.rating === 'fair'}"),
        ("<p>💡 ROAS di bawah 2x menandakan campaign perlu evaluasi — targeting, creative, atau landing page mungkin perlu disesuaikan.</p>",
         "<p>💡 ROAS below 2x means the campaign needs a review — targeting, creative or the landing page may need adjusting.</p>"),
        ("<p>💡 ROAS 2-4x cukup baik. Optimasi lanjutan bisa mendorong ke 4x+.</p>",
         "<p>💡 ROAS of 2-4x is decent. Further optimisation can push it to 4x+.</p>"),
        ("<p>✅ ROAS di atas 4x sangat baik. Pertimbangkan scaling budget untuk hasil lebih besar.</p>",
         "<p>✅ ROAS above 4x is excellent. Consider scaling your budget for bigger results.</p>"),
        ("Masukkan angka belanja iklan dan pendapatan untuk melihat ROAS.",
         "Enter your ad spend and revenue figures to see your ROAS."),
        ("Halo%20Beriklan%2C%20saya%20ingin%20konsultasi%20ROAS%20campaign%20saya.",
         "Hello%20Beriklan%2C%20I%27d%20like%20to%20discuss%20my%20campaign%20ROAS."),
        ("Konsultasi ROAS dengan Tim Beriklan →", "Discuss ROAS with the Beriklan Team →"),
    ],
    "OrderWizard.svelte": [
        ("{ id: 'fb', label: 'Facebook Ads', desc: 'Iklan tertarget', emoji: '📘' },",
         "{ id: 'fb', label: 'Facebook Ads', desc: 'Targeted advertising', emoji: '📘' },"),
        ("{ id: 'gads', label: 'Google Search Ads', desc: 'Tangkap intent tinggi', emoji: '🔍' },",
         "{ id: 'gads', label: 'Google Search Ads', desc: 'Capture high intent', emoji: '🔍' },"),
        ("{ id: 'kelola-ig', label: 'Kelola Instagram', desc: 'Manajemen konten', emoji: '📲' },",
         "{ id: 'kelola-ig', label: 'Instagram Management', desc: 'Content management', emoji: '📲' },"),
        ("{ id: 'kelola-tt', label: 'Kelola TikTok', desc: 'Manajemen video pendek', emoji: '🎤' },",
         "{ id: 'kelola-tt', label: 'TikTok Management', desc: 'Short-video management', emoji: '🎤' },"),
        ("{ id: 'web', label: 'Pembuatan Website', desc: 'Profesional, multi-halaman', emoji: '🌐' },",
         "{ id: 'web', label: 'Website Development', desc: 'Professional, multi-page', emoji: '🌐' },"),
        ("{ id: 'lp', label: 'Landing Page + Ads', desc: 'Paket promo 1.999rb', emoji: '🚀' },",
         "{ id: 'lp', label: 'Landing Page + Ads', desc: 'Promo bundle RM 1,299', emoji: '🚀' },"),
        ("{ id: 'starter', label: 'Di bawah Rp 3 juta', desc: 'Untuk testing awal' },",
         "{ id: 'starter', label: 'Under RM 1,500', desc: 'For early testing' },"),
        ("{ id: 'mid', label: 'Rp 3-10 juta', desc: 'Untuk campaign aktif' },",
         "{ id: 'mid', label: 'RM 1,500 - 5,000', desc: 'For active campaigns' },"),
        ("{ id: 'pro', label: 'Rp 10-25 juta', desc: 'Untuk scale up' },",
         "{ id: 'pro', label: 'RM 5,000 - 12,000', desc: 'For scaling up' },"),
        ("{ id: 'enterprise', label: 'Di atas Rp 25 juta', desc: 'Untuk multi-channel' },",
         "{ id: 'enterprise', label: 'Above RM 12,000', desc: 'For multi-channel' },"),
        ("{ id: 'unsure', label: 'Belum yakin', desc: 'Mari berdiskusi dulu' },",
         "{ id: 'unsure', label: 'Not sure yet', desc: 'Let us discuss first' },"),
        ("currency: 'IDR'", "currency: 'MYR'"),
        ("""            `Halo Beriklan, saya tertarik untuk diskusi:\\n\\n` +
            `Layanan: ${serviceNames}\\n` +
            `Budget: ${budgetLabel}\\n` +
            `Bisnis: ${business.name}\\n` +
            `Kontak: ${business.contact}\\n` +
            (business.notes ? `Catatan: ${business.notes}` : '')""",
         """            `Hello Beriklan, I would like to discuss:\\n\\n` +
            `Services: ${serviceNames}\\n` +
            `Budget: ${budgetLabel}\\n` +
            `Business: ${business.name}\\n` +
            `Contact: ${business.contact}\\n` +
            (business.notes ? `Notes: ${business.notes}` : '')"""),
        (">Layanan apa yang Anda butuhkan?</h3>", ">Which services do you need?</h3>"),
        ("Pilih satu atau lebih. Anda dapat diskusi detail di sesi konsultasi.",
         "Select one or more. You can discuss the details in your consultation session."),
        (">Berapa budget yang Anda persiapkan?</h3>", ">What budget have you prepared?</h3>"),
        ("Termasuk ad spend (budget iklan) + biaya jasa. Belum yakin? Pilih \"Belum yakin\".",
         "Including ad spend + service fees. Not sure? Choose \"Not sure yet\"."),
        (">Ceritakan sedikit tentang bisnis Anda</h3>", ">Tell us a little about your business</h3>"),
        ("Data ini membantu kami menyiapkan rekomendasi yang relevan untuk Anda.",
         "This helps us prepare recommendations that are relevant to you."),
        (">Nama bisnis / brand</label>", ">Business / brand name</label>"),
        ("placeholder=\"contoh: Beauty Studio Bandung\"", "placeholder=\"e.g. Beauty Studio KL\""),
        (">Nomor WhatsApp / email</label>", ">WhatsApp number / email</label>"),
        ("placeholder=\"contoh: 0812-3456-7890 atau info@bisnis.com\"",
         "placeholder=\"e.g. 012-345 6789 or info@business.com\""),
        (">Catatan tambahan <span class=\"text-muted font-normal\">(opsional)</span></label>",
         ">Additional notes <span class=\"text-muted font-normal\">(optional)</span></label>"),
        ("placeholder=\"Misalnya: target market, tantangan saat ini, atau pertanyaan spesifik...\"",
         "placeholder=\"e.g. target market, current challenges, or specific questions...\""),
        ("<ArrowLeft class=\"w-4 h-4\" /> Kembali", "<ArrowLeft class=\"w-4 h-4\" /> Back"),
        ("Lanjut <ArrowRight class=\"w-4 h-4\" />", "Next <ArrowRight class=\"w-4 h-4\" />"),
        ("<MessageCircle class=\"w-4 h-4\" /> Kirim via WhatsApp", "<MessageCircle class=\"w-4 h-4\" /> Send via WhatsApp"),
    ],
    "BlogFilter.svelte": [
        ("'facebook-ads-management': 'Iklan Facebook',", "'facebook-ads-management': 'Facebook Ads',"),
        ("'instagram-ads-management': 'Iklan Instagram',", "'instagram-ads-management': 'Instagram Ads',"),
        ("'tiktok-ads-management': 'Iklan TikTok',", "'tiktok-ads-management': 'TikTok Ads',"),
        ("'google-ads-management': 'Iklan Google Ads',", "'google-ads-management': 'Google Ads',"),
        ("'youtube-ads-management': 'Iklan YouTube',", "'youtube-ads-management': 'YouTube Ads',"),
        ("'instagram-management': 'Kelola Instagram',", "'instagram-management': 'Instagram Management',"),
        ("'tiktok-management': 'Kelola TikTok',", "'tiktok-management': 'TikTok Management',"),
        ("'website-development': 'Pembuatan Website',", "'website-development': 'Website Development',"),
        ("pillarHref: `/${service}/pilar/`,", "pillarHref: `/${service}/pillar/`,"),
        ("{ id: 'all', label: 'Semua Topik' },", "{ id: 'all', label: 'All Topics' },"),
        ("{ id: 'strategy', label: 'Strategi' },", "{ id: 'strategy', label: 'Strategy' },"),
        ("{ id: 'case-study', label: 'Studi Kasus' },", "{ id: 'case-study', label: 'Case Studies' },"),
        ("Kembali ke Panduan {clusterMeta.serviceName}", "Back to the {clusterMeta.serviceName} Guide"),
        ("{clusterPosts.length} artikel terkait {clusterMeta.serviceName.toLowerCase()}. Semua dibahas dari pengalaman mengelola campaign sejak 2016.",
         "{clusterPosts.length} articles related to {clusterMeta.serviceName.toLowerCase()}. All written from hands-on experience managing campaigns since 2016."),
        ("Baca selengkapnya", "Read more", True),
        ("Belum ada artikel khusus untuk cluster ini. Kembali ke panduan untuk topik lain.",
         "No articles for this cluster yet. Head back to the guide for other topics."),
        ("Lihat Panduan Lengkap {clusterMeta.serviceName}", "View the Full {clusterMeta.serviceName} Guide"),
        (">Filter Topik:</span>", ">Filter by Topic:</span>"),
        (">Artikel Lainnya</h3>", ">More Articles</h3>"),
        ("Tidak ada artikel dalam topik ini. Coba topik lain.", "No articles in this topic. Try another one."),
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
