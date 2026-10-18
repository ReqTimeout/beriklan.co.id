#!/usr/bin/env python3
"""F1-7 pass 2b: live-stream-viewers.astro (hub) -> English + MYR, plus shopee leftover."""
import re, sys

PAGES = "/Users/maabook/Desktop/beriklan.my/web/src/pages/"
FP = PAGES + "live-stream-viewers.astro"

TIERS = """const tiers = [
    { name: 'Warm-up', priceLabel: '5', duration: '20 viewers / 1 hour live', tagline: 'Perfect for short lives, tests, or warming up before your main live.', features: ['20 real active viewers joining gradually', 'Up to 1 hour of live time', 'Works across all live platforms', 'Great for short or test lives', 'Zero risk to your account'], priceNote: 'price per live session', disclaimer: 'Real accounts, no bots.' },
    { name: 'Starter', priceLabel: '10', duration: '50 viewers / 1 hour live', tagline: 'For regular lives that need an early boost so the algorithm notices you.', features: ['50 real active viewers', 'Up to 1 hour of live time', 'Works across all live platforms', 'Great for new sellers & streamers', 'Star Pick \u2014 the most popular package'], priceNote: 'RM 0.20/viewer/hour', disclaimer: 'Weekly/monthly bundle bonus: 10\u201315% off.', highlight: true },
    { name: 'Basic', priceLabel: '19', duration: '100 viewers / 1 hour live', tagline: 'The sweet spot for Shopee Live sellers who want to boost ranking.', features: ['100 real viewers staying the whole live', 'Up to 1 hour of live time', 'Works across all live platforms', 'Great for Shopee / TikTok Shop sellers', 'Real accounts, no bots \u2014 safe for your account'], priceNote: 'RM 0.19/viewer/hour', disclaimer: 'Ideal for weekly lives / consistent algorithm boosts.' },
    { name: 'Pro', priceLabel: '35', duration: '200 viewers / 1 hour live', tagline: 'For serious conversion pushes and product placement.', features: ['200 real active viewers', 'Up to 1 hour of live time', 'Works across all live platforms', 'Great for product launches & events', 'Priority WhatsApp support'], priceNote: 'RM 0.18/viewer/hour', disclaimer: 'Special discount on repeat orders.' },
    { name: 'Business', priceLabel: '49', duration: '300 viewers / 1 hour live', tagline: 'For brands and stores running live commerce daily.', features: ['300 real active viewers', 'Up to 1 hour of live time', 'Works across all live platforms', 'Great for brands with regular live commerce', 'Priority support + account manager'], priceNote: 'RM 0.16/viewer/hour', disclaimer: 'Ideal for weekly bundles on a fixed schedule.' },
    { name: 'Premium', priceLabel: '75', duration: '500 viewers / 1 hour live', tagline: 'For major launch events or lives with high viewer targets.', features: ['500 real active viewers', 'Up to 1 hour of live time', 'Works across all live platforms', 'Great for launches / corporate events', '24/7 support + flexible rescheduling'], priceNote: 'RM 0.15/viewer/hour', disclaimer: 'For 500+ viewers or monthly packages, custom pricing.' },
];"""

FEATURES = """const features = [
    { iconName: 'Sparkles', title: 'Real Accounts, No Bots', desc: 'Our viewers are active accounts \u2014 not automation bots. Human behaviour, natural interaction, no platform flags.' },
    { iconName: 'Users', title: 'Organic Algorithm Boost', desc: 'Platforms (TikTok, Shopee, YouTube, IG, Twitch) prioritise lives with active viewers \u2014 boosting exposure 3\u20135x wider than usual.' },
    { iconName: 'TrendingUp', title: 'Gradual Join Over 5\u201315 Minutes', desc: 'Viewers never appear all at once. They join gradually from the first minute \u2014 making your live look organic and trending on For You / Explore.' },
    { iconName: 'Shield', title: 'Safe for Your Account', desc: 'Viewers never spam likes/comments that trigger platform flags. Nothing happens from your account \u2014 we handle everything viewer-side. Used by 1,200+ sellers without a single issue.' },
    { iconName: 'Smartphone', title: 'Multi-Platform at Once', desc: 'One order, five platforms. TikTok + Shopee + YouTube + Instagram + Twitch lives \u2014 all boosted simultaneously.' },
    { iconName: 'Clock', title: 'Starts Within 5 Minutes', desc: 'Once your order is confirmed, viewers start joining. No need to pre-record \u2014 if your live is already running, we join in real time.' },
];"""

STEPS = """const steps = [
    { num: '01', tag: 'DAY OF', title: 'Send Your Live Details', desc: 'Share your username/platform/date/start time with our team on WhatsApp. Orders confirmed within 30 minutes of complete details.' },
    { num: '02', tag: 'DAY OF', title: 'Payment & Preparation', desc: 'Transfer via bank or e-wallet (DuitNow/TNG). Invoice sent immediately. 50% deposit available for larger packages.' },
    { num: '03', tag: 'LIVE', title: 'Viewers Join In', desc: 'When your live starts, our viewers join gradually within 5\u201315 minutes. Never sudden, never suspicious \u2014 it looks natural.' },
    { num: '04', tag: 'POST-LIVE', title: 'Review & Recurrence', desc: 'After the live ends, we can review performance. Want a fixed Tuesday\u2013Friday schedule? 10\u201315% off recurring packages.' },
];"""

FAQS = """const faqs = [
    { q: 'Are the viewers bots or real accounts?', a: 'Real accounts, no automation. They are active platform users who stay for the full live duration. Their interaction is natural and human \u2014 no like/comment spam that could trigger flags.' },
    { q: 'Is it safe for my account?', a: 'Completely safe. Nothing unusual ever happens from your account \u2014 all activity comes from the viewers, not you. Used by 1,200+ sellers and streamers without a single account issue.' },
    { q: 'How soon do viewers appear after I order?', a: '5\u201315 minutes after your live starts. Never all at once \u2014 gradual, just like a normal live.' },
    { q: 'Which platforms are supported?', a: 'TikTok Live, Shopee Live, YouTube Live, Instagram Live, Twitch and Lazada Live. Other platforms that support live streaming can work too \u2014 just chat with us to confirm.' },
    { q: 'Can I order more than 500 viewers, or a monthly package?', a: 'Yes. For 500+ viewers or weekly/monthly packages on a fixed schedule, chat with us on WhatsApp first for the best rate. Recurring schedules (e.g. every Tuesday & Friday) get an extra 10\u201315% off.' },
    { q: 'What happens if viewers drop before the session ends?', a: 'If viewers drop due to force majeure or a platform issue, we refund pro-rata or replace the viewers in your next session. Communication first \u2014 we are responsive humans, not a template bot.' },
    { q: 'Is there a minimum live duration?', a: 'One session = viewers for 1 hour of live time. For longer lives, we can count it as multiple sessions or build a custom package.' },
];"""

PAIRS = [
    ('<Layout title="Jasa View Live Multi-Platform | Boost Viewers Live Streaming — Beriklan" description="Boost viewers live streaming untuk TikTok, Shopee, YouTube, Instagram, Twitch. Real account, no bot, aman untuk akun Anda. Mulai Rp 12.000 untuk 20 viewers.">',
     '<Layout title="Live Stream Viewers Malaysia | TikTok, Shopee, YouTube, IG, Twitch \u2014 Beriklan" description="Boost live stream viewers for TikTok, Shopee, YouTube, Instagram and Twitch. Real accounts, no bots, safe for your account. From RM 5 for 20 viewers." canonical="https://beriklan.my/live-stream-viewers/">'),
    # relatedItems
    ("label: 'Jasa Iklan TikTok', desc: 'Untuk live TikTok yang sudah berjalan dan butuh paid traffic tambahan.'",
     "label: 'TikTok Ads Management', desc: 'For TikTok lives already running that need extra paid traffic.'"),
    ("label: 'Kelola Instagram', desc: 'Manajemen konten Instagram rutin untuk omni-channel marketing.'",
     "label: 'Instagram Management', desc: 'Ongoing Instagram content management for omni-channel marketing.'"),
    ("label: 'Jasa Iklan YouTube', desc: 'Untuk YouTube Ads yang menyasar viewers berdedikasi.'",
     "label: 'YouTube Ads Management', desc: 'For YouTube Ads targeting dedicated viewers.'"),
    # hero
    ('Jasa View Live · TikTok, Shopee, YouTube, IG, Twitch', 'Live Stream Viewers · TikTok, Shopee, YouTube, IG, Twitch'),
    ('Live Sepi,', 'A Quiet Live,'),
    ('Algoritma Tidak Mau Angkat', 'The Algorithm Won\u2019t Pick It Up'),
    ('— Kami Solusinya.', '\u2014 We\u2019re the Fix.'),
    ('Algorithm TikTok, Shopee Live, YouTube Live — semuanya satu prinsip: live yang ramai naik. Viewer riil dari kami masuk gradual sejak menit pertama, bikin live Anda kelihatan trending — tanpa flag, tanpa bot, tanpa risiko untuk akun Anda.',
     'TikTok, Shopee Live and YouTube Live algorithms all follow one principle: busy lives rise. Our real viewers join gradually from the first minute, making your live look trending \u2014 no flags, no bots, no risk to your account.'),
    ('<strong class="text-ink">Mulai Rp 12.000</strong> untuk 20 viewers', '<strong class="text-ink">From RM 5</strong> for 20 viewers'),
    ('>Aman untuk akun Anda<', '>Safe for your account<'),
    # mock
    ('@brand_kamu', '@your_brand'),
    ('keren banget live nya 🔥', 'this live is awesome 🔥'),
    ('mau dong diskonnya', 'can I get that discount?'),
    ('stok masih ada ga kak?', 'is it still in stock?'),
    ('BELI SEKARANG', 'BUY NOW'),
    ('>Rp 99K<', '>RM 29<'),
    ('Cocok untuk semua platform live', 'Works across every live platform'),
    # why section
    ('Live sepi = algoritma mengabaikan Anda.<br/>', 'A quiet live = the algorithm ignores you.<br/>'),
    ('<span class="text-accent">Tapi kami tahu cara membalikkannya.</span>', '<span class="text-accent">We know how to turn that around.</span>'),
    ('Semua platform live — TikTok, Shopee, YouTube, Instagram, Twitch — punya satu kesamaan: mereka memprioritaskan live dengan viewers aktif. Live dengan 500 viewers naik 5x lebih sering di For You / Explore dibanding live dengan 50 viewers. Kami bantu Anda memulai momentum itu.',
     'Every live platform \u2014 TikTok, Shopee, YouTube, Instagram, Twitch \u2014 shares one trait: they prioritise lives with active viewers. A live with 500 viewers surfaces 5x more often on For You / Explore than one with 50. We help you start that momentum.'),
    ('<p class="why-desc">Platform memprioritaskan live dengan viewers aktif. Boost viewers = boost distribusi organik sampai 5x lebih luas dari biasanya.</p>',
     '<p class="why-desc">Platforms prioritise lives with active viewers. Boost viewers = boost organic distribution up to 5x wider than usual.</p>'),
    ('<p class="why-desc">Viewers dari kami akun riil, bukan bot automation. Tidak ada aktivitas dari akun Anda — sudah dipakai 1.200+ seller tanpa satu pun kena masalah.</p>',
     '<p class="why-desc">Our viewers are real accounts, not automation bots. Nothing happens from your account \u2014 used by 1,200+ sellers without a single issue.</p>'),
    # pricing helper
    ('<p class="font-display font-bold text-base text-ink mb-1">Butuh paket recurring atau viewer 500+?</p>',
     '<p class="font-display font-bold text-base text-ink mb-1">Need a recurring package or 500+ viewers?</p>'),
    ('<p class="text-sm text-muted leading-relaxed">Hubungi kami untuk konsultasi via WhatsApp. Kami bantu pilih paket yang paling cocok dengan jadwal live dan objective Anda.</p>',
     '<p class="text-sm text-muted leading-relaxed">A consultation. We help you pick the package that best fits your live schedule and objective.</p>'),
    # stats
    ('Bukan janji — hanya hasil yang bisa diverifikasi sendiri di akun Anda.',
     'No promises \u2014 only results you can verify yourself in your account.'),
    ('>Seller &amp; Streamer aktif<', '>Active sellers &amp; streamers<'),
    ('>sepanjang 2024-2026<', '>across 2024\u20132026<'),
    ('>Boost distribusi<', '>Distribution boost<'),
    ('>rata-rata For You / Explore<', '>average For You / Explore<'),
    ('>Akun kena masalah<', '>Accounts flagged<'),
    ('>sepanjang penggunaan<', '>across all usage<'),
    ('>Diskon paket recurring<', '>Recurring package discount<'),
    ('>untuk jadwal tetap mingguan<', '>for fixed weekly schedules<'),
    # trust dark cards
    ('<h3 class="trust-title-dark">Aman untuk akun Anda</h3>', '<h3 class="trust-title-dark">Safe for your account</h3>'),
    ('<p class="trust-desc-dark">Viewers dari kami akun riil aktif — no bot, no flag. Tidak ada aktivitas dari akun Anda. 1.200+ seller &amp; streamer tanpa satu pun kena masalah.</p>',
     '<p class="trust-desc-dark">Our viewers are real, active accounts \u2014 no bots, no flags. Nothing happens from your account. 1,200+ sellers &amp; streamers without a single issue.</p>'),
    ('<p class="trust-desc-dark">Order per sesi, bayar per order. Anda bebas order sesuai jadwal live. Untuk paket recurring mingguan/bulanan, diskon 10-15%.</p>',
     '<p class="trust-desc-dark">Order per session, pay per order. Book whenever your live schedule needs it. Weekly/monthly recurring packages get 10\u201315% off.</p>'),
    # testimonials
    ('Pengalaman mereka yang sudah<br/>', 'The experience of those who have<br/>'),
    ('<span class="text-accent">naikkan live-nya lewat kami.</span>', '<span class="text-accent">grown their lives with us.</span>'),
    ('Live TikTok Shop biasanya cuma 30-50 viewers. Setelah pakai layanan ini dari 100 viewers, distribusi naik 4x dan masuk FYP beberapa kali. Closing rate juga naik karena viewers aktif lihat produk lebih lama.',
     'Our TikTok Shop lives used to sit at 30\u201350 viewers. After starting with 100 viewers from this service, distribution grew 4x and we hit the FYP several times. Closing rate rose too, because active viewers watch products longer.'),
    ('>Rina Marlina<', '>Mei Ling Tan<'),
    ('>Seller Skincare · Bandung<', '>Skincare Seller · Kuala Lumpur<'),
    ('Twitch channel saya stuck di 20 viewers untuk berbulan-bulan. Setelah coba paket Bisnis, viewership naik stabil di 300+. Komunitas jadi aktif, donasi masuk, dan partner tertarik kolaborasi karena metrics membaik.',
     'My Twitch channel was stuck at 20 viewers for months. After trying the Business package, viewership stabilised at 300+. The community became active, donations came in, and partners got interested because the metrics improved.'),
    ('>Andika Pratama<', '>Danish Iqbal<'),
    ('>Streamer Twitch · Jakarta<', '>Twitch Streamer · Petaling Jaya<'),
    ('Untuk launching produk baru, kami order paket Premium 500 viewers. Live Shopee conversion naik 3x dari biasanya. Real account, no flag dari Shopee. Repeat order setiap launching jadi.',
     'For a new product launch we ordered the Premium 500-viewer package. Shopee Live conversion tripled versus usual. Real accounts, no flags from Shopee. We now repeat the order for every launch.'),
    ('>Dewi Anggraini<', '>Siti Nadia<'),
    ('>Brand Owner Fashion · Surabaya<', '>Fashion Brand Owner · Johor Bahru<'),
    ('>Conversion 3x saat launching<', '>Conversion 3x at launch<'),
    # faq + final cta
    ('Sebelum order, ini yang biasanya ditanya', 'Before you order, these usually get asked'),
    ('Tim online · respon dalam 1 jam pada jam kerja', 'Team online · replies within 1 hour during business hours'),
    ('Ceritakan tanggal live Anda via WhatsApp. Kami kirim rekomendasi paket & timeline. Tanpa komitmen — order hanya saat Anda siap live.',
     'Tell us your live date on WhatsApp. We\u2019ll send a package recommendation & timeline. No commitment \u2014 order only when you\u2019re ready to go live.'),
    ('Paket recurring mingguan/bulanan · diskon 10-15%', 'Weekly/monthly recurring packages · 10\u201315% discount'),
]


def main():
    txt = open(FP, encoding='utf-8').read()

    # waLink
    txt = re.sub(r'const waLink = "https://wa\.me/62811919328\?text=[^"]*";',
                 'const waLink = "https://wa.me/62811919328?text=Hi%20Beriklan%2C%20I%27m%20interested%20in%20live%20stream%20viewers.%20Please%20share%20packages%20and%20pricing.";', txt)

    for pat, repl in [(r'const tiers = \[.*?\n\];', TIERS), (r'const features = \[.*?\n\];', FEATURES),
                      (r'const steps = \[.*?\n\];', STEPS), (r'const faqs = \[.*?\n\];', FAQS)]:
        new_txt, n = re.subn(pat, lambda m: repl, txt, count=1, flags=re.S)
        if n != 1:
            print('FATAL: block not replaced:', pat[:25]); sys.exit(1)
        txt = new_txt

    hits = 0
    for old, new in PAIRS:
        c = txt.count(old)
        if c:
            txt = txt.replace(old, new); hits += c
        else:
            print('MISS:', old[:80])
    open(FP, 'w', encoding='utf-8').write(txt)
    print('hub done, %d string hits' % hits)

    # shopee leftover trust item
    fp2 = PAGES + 'shopee-live-viewers.astro'
    t2 = open(fp2, encoding='utf-8').read()
    old = '<span class="text-white/80">Aman untuk toko Shopee</span>'
    assert old in t2
    t2 = t2.replace(old, '<span class="text-white/80">Safe for your Shopee store</span>')
    open(fp2, 'w', encoding='utf-8').write(t2)
    print('shopee leftover fixed')


if __name__ == '__main__':
    main()
