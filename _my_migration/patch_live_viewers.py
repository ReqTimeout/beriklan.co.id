#!/usr/bin/env python3
"""F1-7 pass 2: 6 live-viewer pages -> English + MYR pricing.
- Regenerates tiers/features/steps/faqs arrays wholesale (regex block replace).
- Replaces the duplicated <Layout ...>>> block with a clean single English block.
- Translates body strings via exact pairs (tolerant, audited).
Prices per plan §1.4: std RM 5/10/19/35/49/75 ; Shopee RM 7/13/25/45/65/99.
"""
import re, sys

PAGES = "/Users/maabook/Desktop/beriklan.my/web/src/pages/"

STD = ['5', '10', '19', '35', '49', '75']
SHP = ['7', '13', '25', '45', '65', '99']
NOTE_STD = ['price per live session', 'RM 0.20/viewer/hour', 'RM 0.19/viewer/hour',
            'RM 0.18/viewer/hour', 'RM 0.16/viewer/hour', 'RM 0.15/viewer/hour']
NOTE_SHP = ['price per live session', 'RM 0.26/viewer/hour', 'RM 0.25/viewer/hour',
            'RM 0.23/viewer/hour', 'RM 0.22/viewer/hour', 'RM 0.20/viewer/hour']


def build_tiers(plat, prices, notes):
    rows = [
        "    { name: 'Warm-up', priceLabel: '%s', duration: '20 viewers / 1 hour live', tagline: 'Perfect for warming up before your main live so the algorithm notices you from the start.', features: ['20 real active viewers', 'Gradual join over 5\u201315 minutes', 'Multi-platform (%s + others)', 'Great for short or test lives', 'Zero risk to your %s account'], priceNote: '%s', disclaimer: 'Real accounts, no bots.' }," % (prices[0], plat, plat, notes[0]),
        "    { name: 'Starter', priceLabel: '%s', duration: '50 viewers / 1 hour live', tagline: 'For regular lives that need an early boost so the %s algorithm notices you.', features: ['50 real active viewers', 'Gradual join over 5\u201315 minutes', 'Multi-platform across all channels', 'Great for new sellers & streamers', 'Real accounts, no flags from %s'], priceNote: '%s', disclaimer: 'The most popular pick among %s sellers.', highlight: true }," % (prices[1], plat, plat, notes[1], plat),
        "    { name: 'Basic', priceLabel: '%s', duration: '100 viewers / 1 hour live', tagline: 'The sweet spot for %s sellers who want to boost ranking & conversion.', features: ['100 real viewers staying the whole live', 'Natural gradual join', 'Multi-platform across all channels', 'Great for %s sellers', 'Boosts algorithm distribution'], priceNote: '%s', disclaimer: 'Ideal for weekly lives.' }," % (prices[2], plat, plat, notes[2]),
        "    { name: 'Pro', priceLabel: '%s', duration: '200 viewers / 1 hour live', tagline: 'For new product launches & live events that need wide distribution.', features: ['200 real active viewers', 'Natural gradual join', 'Multi-platform across all channels', 'Great for launches & events', 'Boosts organic distribution'], priceNote: '%s', disclaimer: 'Special discount on repeat orders.' }," % (prices[3], notes[3]),
        "    { name: 'Business', priceLabel: '%s', duration: '300 viewers / 1 hour live', tagline: 'For brands and stores running live commerce on %s every day.', features: ['300 real active viewers', 'Natural gradual join', 'Multi-platform across all channels', 'Great for daily live commerce', 'Priority support + account manager'], priceNote: '%s', disclaimer: 'Ideal for weekly bundles.' }," % (prices[4], plat, notes[4]),
        "    { name: 'Premium', priceLabel: '%s', duration: '500 viewers / 1 hour live', tagline: 'For major %s launch events or viral pushes with high viewer targets.', features: ['500 real active viewers', 'Natural gradual join', 'Multi-platform across all channels', 'Great for viral launches', '24/7 support + flexible rescheduling'], priceNote: '%s', disclaimer: 'For 500+ viewers or monthly packages, custom pricing.' }," % (prices[5], plat, notes[5]),
    ]
    return "const tiers = [\n" + "\n".join(rows) + "\n];"


def build_faqs(plat, key='q', val='a'):
    items = [
        ("Are the viewers bots or real %s accounts?" % plat,
         "Real %s accounts, no automation. They are active users who stay for the full live duration. Natural interaction, no flags from the %s algorithm." % (plat, plat)),
        ("Is it safe for my %s account?" % plat,
         "Completely safe. Viewers never spam likes/comments that could trigger a shadow ban. Nothing happens from your account. Over 1,200 lives without a single issue."),
        ("How soon do viewers appear after my live starts?",
         "5\u201315 minutes after your live begins. Never all at once \u2014 gradual, just like a normal live."),
        ("Does it help the %s algorithm?" % plat,
         "Yes. The %s algorithm prioritises lives with active viewers. Boosting viewers can expand distribution up to 5x wider, especially for first lives or product launches." % plat),
        ("Can I order more than 500 viewers, or weekly/monthly packages?",
         "Yes. For 500+ viewers or daily/weekly packages on a fixed schedule, chat with us on WhatsApp first for the best rate. Recurring 2\u20133x weekly streams get 10\u201315% off."),
        ("Do viewers stay for the whole live?",
         "Yes. Our viewers stay for the duration you order. A 1-hour live means viewers stay 1 hour. No one suddenly leaves mid-live."),
        ("What if %s flags my account after ordering?" % plat,
         "It has never happened. Our viewers interact naturally \u2014 likes, comments and shares follow normal account patterns. There is no bot pattern for %s to detect." % plat),
    ]
    return items


def faqs_js(plat):
    rows = ["    { q: '%s', a: '%s' }," % (q.replace("'", "\\'"), a.replace("'", "\\'")) for q, a in build_faqs(plat)]
    return "const faqs = [\n" + "\n".join(rows) + "\n];"


def layout_faq_js(items, indent="            "):
    rows = ["%s{ question: '%s', answer: '%s' }," % (indent, q.replace("'", "\\'"), a.replace("'", "\\'")) for q, a in items]
    out = "\n".join(rows)
    return out[:-1]  # drop trailing comma


def build_layout(c):
    faq_block = layout_faq_js(build_faqs(c['plat']))
    return (
        '<Layout title="%s" description="%s" canonical="https://beriklan.my/%s/"\n' % (c['title'], c['desc'], c['slug'])
        + '    faq={[\n' + faq_block + '\n        ]}\n'
        + '    breadcrumb={[\n'
        + '        { name: "Home", url: "https://beriklan.my/" },\n'
        + '        { name: "Live Stream Viewers", url: "https://beriklan.my/live-stream-viewers/" },\n'
        + '        { name: "%s", url: "https://beriklan.my/%s/" }\n' % (c['svc'], c['slug'])
        + '    ]}\n'
        + '    service={{\n'
        + '        name: "%s",\n' % c['svc']
        + '        description: "Live streaming viewer service for %s Live. Real accounts, no bots, safe for your account. From RM %s for 20 viewers.",\n' % (c['plat'], c['p'][0])
        + '        url: "https://beriklan.my/%s/",\n' % c['slug']
        + '        priceRange: "RM %s - RM %s",\n' % (c['p'][0], c['p'][5])
        + '        serviceType: "Live Viewers Service",\n'
        + '        areaServed: "Malaysia",\n'
        + '        provider: { name: "Beriklan.my", url: "https://beriklan.my" }\n'
        + '    }}\n'
        + '>\n'
    )


def build_features(plat, first):
    common = [
        "    { iconName: 'Users', title: 'Real Active Accounts', desc: 'Our viewers are active %s accounts \u2014 not bots. They stay, watch and interact naturally with your live content.' }," % plat,
        "    { iconName: 'TrendingUp', title: 'Gradual Join Over 5\u201315 Minutes', desc: 'Viewers never appear all at once. They join gradually from the first minute \u2014 so the algorithm sees your live as genuinely trending.' },",
        "    { iconName: 'Shield', title: 'Safe for Your %s Account', desc: 'Our viewers never spam likes/comments that trigger flags. Nothing happens from your account. Used on 1,200+ lives without a single issue.' }," % plat,
        "    { iconName: 'Smartphone', title: 'Joins %s Live + Others', desc: 'Order for %s Live, and viewers can also stay on other platforms streaming at the same time. Multi-platform, one order.' }," % (plat, plat),
        "    { iconName: 'Clock', title: 'Starts Within 5 Minutes', desc: 'Once your order is confirmed, viewers start joining. Live already running? We join in real time \u2014 no need to restart.' },",
    ]
    return "const features = [\n" + first + "\n" + "\n".join(common) + "\n];"


def build_steps(plat):
    rows = [
        "    { num: '01', tag: 'DAY OF', title: 'Send Your %s Live Details', desc: 'Share your %s username + live date/time. Orders are confirmed within 30 minutes of complete details.' }," % (plat, plat),
        "    { num: '02', tag: 'LIVE DAY', title: 'Payment & Preparation', desc: 'Transfer via bank or e-wallet (DuitNow/TNG). Invoice sent immediately. 50% deposit available for larger packages.' },",
        "    { num: '03', tag: 'LIVE', title: 'Viewers Join Your Stream', desc: 'When your %s Live starts, viewers join gradually over 5\u201315 minutes. The algorithm notices your live as trending.' }," % plat,
        "    { num: '04', tag: 'POST-LIVE', title: 'Review & Recurring', desc: 'After the live ends, we review performance. Want a regular 2\u20133x weekly schedule? 10\u201315% off recurring packages.' },",
    ]
    return "const steps = [\n" + "\n".join(rows) + "\n];"


# -------------------- per-platform config --------------------
CFG = {
    'tiktok': dict(
        file='tiktok-live-viewers.astro', plat='TikTok', slug='tiktok-live-viewers',
        svc='TikTok Live Viewers', p=STD, notes=NOTE_STD,
        title='TikTok Live Viewers Malaysia | Boost the FYP Algorithm \u2014 Beriklan',
        desc='Boost your TikTok Live viewer count so the FYP algorithm notices your stream. Real accounts, no bots, safe for your TikTok account. From RM 5 for 20 viewers.',
        wa='Hi%20Beriklan%2C%20I%27m%20interested%20in%20TikTok%20Live%20viewers.%20Please%20share%20packages%20and%20pricing.',
        feat_first="    { iconName: 'Sparkles', title: 'Boost the FYP Algorithm', desc: 'TikTok\u2019s For You Page prioritises lives with active viewers. Boost viewers = boost FYP distribution up to 5x wider than usual.' },",
        pairs=[
            ('Jasa View Live TikTok · Boost FYP Algorithm', 'TikTok Live Viewers · Boost the FYP Algorithm'),
            ('Live TikTok Sepi,', 'Your TikTok Live Is Quiet,'),
            ('FYP Tidak Mau Angkat.', 'The FYP Won\u2019t Pick It Up.'),
            ('— Algoritma Butuh Viewers.', '\u2014 The Algorithm Needs Viewers.'),
            ('TikTok For You Page memprioritaskan live dengan viewers aktif. 100+ viewers = 5x lebih besar jangkauan FYP. Viewer riil dari kami join gradual sejak menit pertama — bikin algoritma TikTok notice live Anda, tanpa flag, tanpa bot, tanpa risiko shadow ban.',
             'TikTok\u2019s For You Page prioritises lives with active viewers. 100+ viewers = up to 5x wider FYP reach. Our real viewers join gradually from the very first minute \u2014 getting the TikTok algorithm to notice your live, with no flags, no bots and no shadow-ban risk.'),
            ('fyp masuk nih 🔥', 'we made it to fyp 🔥'),
            ('produk ready ga kak?', 'is the product ready?'),
            ('Algoritma FYP TikTok satu hal:<br/>', 'TikTok\u2019s FYP algorithm knows one thing:<br/>'),
            ('>live yang ramai = distribusi luas.<', '>busy lives get wide distribution.<'),
            ('TikTok For You Page memprioritaskan live dengan viewers aktif. Live dengan 100+ viewers naik 5x lebih sering di FYP dibanding live dengan 20 viewers. Viewer riil dari kami membantu TikTok algorithm notice live Anda — tanpa flag, tanpa shadow ban.',
             'TikTok\u2019s For You Page prioritises lives with active viewers. Lives with 100+ viewers surface 5x more often on the FYP than lives with 20. Our real viewers help the TikTok algorithm notice your live \u2014 no flags, no shadow bans.'),
            ('<p class="tiktok-why-desc">TikTok memprioritaskan live dengan viewers aktif. Boost viewers = boost distribusi FYP sampai 5x lebih luas dari biasanya.</p>',
             '<p class="tiktok-why-desc">TikTok prioritises lives with active viewers. Boost viewers = boost FYP distribution up to 5x wider than usual.</p>'),
            ('<h3 class="tiktok-why-title">Aman dari Shadow Ban</h3>', '<h3 class="tiktok-why-title">Safe from Shadow Bans</h3>'),
            ('<p class="tiktok-why-desc">Viewers dari kami interaksi natural — like, comment, share sesuai pattern akun normal. Tidak ada pattern bot yang TikTok bisa detect.</p>',
             '<p class="tiktok-why-desc">Our viewers interact naturally \u2014 likes, comments and shares follow normal account patterns. No bot pattern for TikTok to detect.</p>'),
            ('<h3 class="tiktok-why-title">Cocok untuk Live Shopping</h3>', '<h3 class="tiktok-why-title">Perfect for Live Shopping</h3>'),
            ('<p class="tiktok-why-desc">TikTok Shop integration: viewers aktif lihat produk lebih lama, conversion naik 3-4x dibanding live sepi.</p>',
             '<p class="tiktok-why-desc">TikTok Shop integration: active viewers watch products longer, lifting conversion 3\u20134x versus a quiet live.</p>'),
            ('rata-rata distribusi For You', 'average For You distribution'),
            ('bg-clip-text text-transparent">live TikTok.</span>', 'bg-clip-text text-transparent">TikTok lives boosted.</span>'),
            ('<span class="text-accent">live TikTok.</span>', '<span class="text-accent">TikTok lives.</span>'),
            ('<h3 class="tiktok-trust-title">Aman untuk akun TikTok</h3>', '<h3 class="tiktok-trust-title">Safe for your TikTok account</h3>'),
            ('<p class="tiktok-trust-desc">Viewers dari kami akun riil aktif. Interaksi natural, no flag. 1.200+ live TikTok tanpa satu pun kena shadow ban.</p>',
             '<p class="tiktok-trust-desc">Our viewers are real, active accounts. Natural interaction, no flags. 1,200+ TikTok lives without a single shadow ban.</p>'),
            ('<h3 class="tiktok-trust-title">Masuk gradual 5-15 menit</h3>', '<h3 class="tiktok-trust-title">Gradual join over 5\u201315 minutes</h3>'),
            ('<p class="tiktok-trust-desc">Viewers join gradual sejak menit pertama live. Tidak tiba-tiba, tidak mencurigakan — FYP notice natural trending.</p>',
             '<p class="tiktok-trust-desc">Viewers join gradually from the first minute of your live. Never sudden, never suspicious \u2014 the FYP sees natural trending.</p>'),
            ('<h3 class="tiktok-trust-title">Tanpa minimum order</h3>', '<h3 class="tiktok-trust-title">No minimum order</h3>'),
            ('<p class="tiktok-trust-desc">Order per sesi, bayar per order. Bebas order sesuai jadwal live TikTok Anda. Diskon 10-15% untuk paket berulang.</p>',
             '<p class="tiktok-trust-desc">Order per session, pay per order. Book whenever your TikTok live schedule needs it. 10\u201315% off recurring packages.</p>'),
            ('Live TikTok berikutnya<br/>', 'Your next TikTok live,<br/>'),
            ('>langsung trending di FYP.<', '>trending on the FYP right away.<'),
        ],
    ),
    'shopee': dict(
        file='shopee-live-viewers.astro', plat='Shopee', slug='shopee-live-viewers',
        svc='Shopee Live Viewers', p=SHP, notes=NOTE_SHP,
        title='Shopee Live Viewers Malaysia | Boost Live Shopping \u2014 Beriklan',
        desc='Boost your Shopee Live viewer count so the Shopee algorithm notices your stream. Real accounts, no bots, safe for your Shopee store. From RM 7 for 20 viewers.',
        wa='Hi%20Beriklan%2C%20I%27m%20interested%20in%20Shopee%20Live%20viewers.%20Please%20share%20packages%20and%20pricing.',
        feat_first="    { iconName: 'Sparkles', title: 'Boost Live Shopping', desc: 'The Shopee Live algorithm prioritises lives with active viewers. Boost viewers = boost live ranking & search.' },",
        pairs=[
            ('Jasa View Live Shopee · Boost Live Shopping', 'Shopee Live Viewers · Boost Live Shopping'),
            ('Live Shopee Sepi,', 'Your Shopee Live Is Quiet,'),
            ('Produk Tidak Naik di Feed.', 'Products Aren\u2019t Rising in the Feed.'),
            ('— Live Shopping Butuh Viewers.', '\u2014 Live Shopping Needs Viewers.'),
            ('Shopee memprioritaskan live dengan viewers aktif. 100+ viewers = 5x lebih besar jangkauan. Viewer riil dari kami join gradual sejak menit pertama — bikin algorithm Shopee notice live Anda, tanpa flag, tanpa bot, tanpa risiko shadow ban.',
             'Shopee prioritises lives with active viewers. 100+ viewers = up to 5x wider reach. Our real viewers join gradually from the very first minute \u2014 getting the Shopee algorithm to notice your live, with no flags, no bots and no shadow-ban risk.'),
            ('keren live nya 🔥', 'awesome live 🔥'),
            ('stok ready ga kak?', 'is stock ready?'),
            ('Apa algoritma Shopee Live satu hal:<br/>', 'The Shopee Live algorithm knows one thing:<br/>'),
            ('>banyak viewers = ranking naik.<', '>more viewers = higher ranking.<'),
            ('Shopee memprioritaskan live dengan viewers aktif. Live dengan 100+ viewers muncul lebih sering di rekomendasi — conversion naik 3-4x dibanding live sepi.',
             'Shopee prioritises lives with active viewers. Lives with 100+ viewers appear far more often in recommendations \u2014 lifting conversion 3\u20134x versus a quiet live.'),
            ('<p class="shopee-why-desc">Shopee Live memprioritaskan live dengan viewers aktif. Boost viewers = boost ranking live & search.</p>',
             '<p class="shopee-why-desc">Shopee Live prioritises lives with active viewers. Boost viewers = boost live ranking & search.</p>'),
            ('<h3 class="shopee-why-title">Aman untuk Toko</h3>', '<h3 class="shopee-why-title">Safe for Your Store</h3>'),
            ('<p class="shopee-why-desc">Viewers dari kami akun Shopee aktif. Tidak add-to-cart spam. Tidak ada aktivitas dari akun toko. 1.200+ live tanpa satu pun kena masalah.</p>',
             '<p class="shopee-why-desc">Our viewers are active Shopee accounts. No add-to-cart spam. No activity from your store account. 1,200+ lives without a single issue.</p>'),
            ('<h3 class="shopee-why-title">Cocok untuk Live Shopping</h3>', '<h3 class="shopee-why-title">Perfect for Live Shopping</h3>'),
            ('<p class="shopee-why-desc">Viewers aktif lihat produk lebih lama, conversion naik 3-4x dibanding live sepi. Cocok untuk flash sale, launching, dan live rutin.</p>',
             '<p class="shopee-why-desc">Active viewers watch products longer, lifting conversion 3\u20134x versus a quiet live. Great for flash sales, launches and regular lives.</p>'),
            ('rata-rata feed Shopee', 'average Shopee feed'),
            ('bg-clip-text text-transparent">live Shopee.</span>', 'bg-clip-text text-transparent">Shopee lives boosted.</span>'),
            ('<span class="text-accent">live Shopee.</span>', '<span class="text-accent">Shopee lives.</span>'),
            ('<h3 class="shopee-trust-title">Aman untuk toko Shopee</h3>', '<h3 class="shopee-trust-title">Safe for your Shopee store</h3>'),
            ('<p class="shopee-trust-desc">Viewers dari kami akun riil aktif. Interaksi natural, no flag. 1.200+ live Shopee tanpa satu pun kena shadow ban.</p>',
             '<p class="shopee-trust-desc">Our viewers are real, active accounts. Natural interaction, no flags. 1,200+ Shopee lives without a single shadow ban.</p>'),
            ('<h3 class="shopee-trust-title">Masuk gradual 5-15 menit</h3>', '<h3 class="shopee-trust-title">Gradual join over 5\u201315 minutes</h3>'),
            ('<p class="shopee-trust-desc">Viewers join gradual sejak menit pertama live. Tidak tiba-tiba, tidak mencurigakan — Shopee notice natural trending.</p>',
             '<p class="shopee-trust-desc">Viewers join gradually from the first minute of your live. Never sudden, never suspicious \u2014 Shopee sees natural trending.</p>'),
            ('<h3 class="shopee-trust-title">Tanpa minimum order</h3>', '<h3 class="shopee-trust-title">No minimum order</h3>'),
            ('<p class="shopee-trust-desc">Order per sesi, bayar per order. Bebas order sesuai jadwal live Shopee Anda. Diskon 10-15% untuk paket berulang.</p>',
             '<p class="shopee-trust-desc">Order per session, pay per order. Book whenever your Shopee live schedule needs it. 10\u201315% off recurring packages.</p>'),
            ('Live Shopee berikutnya<br/>', 'Your next Shopee live,<br/>'),
            ('>naik ranking di feed.<', '>climbing the feed rankings.<'),
        ],
    ),
    'instagram': dict(
        file='instagram-live-viewers.astro', plat='Instagram', slug='instagram-live-viewers',
        svc='Instagram Live Viewers', p=STD, notes=NOTE_STD,
        title='Instagram Live Viewers Malaysia | Boost IG Reach \u2014 Beriklan',
        desc='Boost your Instagram Live viewer count so the IG algorithm notices your stream. Real accounts, no bots, safe for your Instagram account. From RM 5 for 20 viewers.',
        wa='Hi%20Beriklan%2C%20I%27m%20interested%20in%20Instagram%20Live%20viewers.%20Please%20share%20packages%20and%20pricing.',
        feat_first="    { iconName: 'Sparkles', title: 'Boost IG Reach', desc: 'Instagram recommends lives with active viewers. Boost viewers = boost reach on Explore & Reels.' },",
        pairs=[
            ('Jasa View Live Instagram · Boost IG Reach', 'Instagram Live Viewers · Boost IG Reach'),
            ('Live Instagram Sepi,', 'Your Instagram Live Is Quiet,'),
            ('Reach Tidak Naik.', 'Reach Isn\u2019t Growing.'),
            ('— Algorithm Butuh Viewers.', '\u2014 The Algorithm Needs Viewers.'),
            ('Instagram memprioritaskan live dengan viewers aktif. 100+ viewers = 5x lebih besar jangkauan. Viewer riil dari kami join gradual sejak menit pertama — bikin algorithm Instagram notice live Anda, tanpa flag, tanpa bot, tanpa risiko shadow ban.',
             'Instagram prioritises lives with active viewers. 100+ viewers = up to 5x wider reach. Our real viewers join gradually from the very first minute \u2014 getting the Instagram algorithm to notice your live, with no flags, no bots and no shadow-ban risk.'),
            ('live IG mantap! 💜', 'awesome IG live! 💜'),
            ('diskonn berapa kak?', 'how much is the discount?'),
            ('reels cocok ga kak?', 'will this work for reels?'),
            ('Apa algoritma IG satu hal:<br/>', 'The IG algorithm knows one thing:<br/>'),
            ('>banyak viewers = reach lebih luas.<', '>more viewers = wider reach.<'),
            ('IG memprioritaskan live dengan viewers aktif. Live dengan 100+ viewers muncul 4x lebih sering di Explore & Reels dibanding live sepi.',
             'IG prioritises lives with active viewers. Lives with 100+ viewers appear 4x more often on Explore & Reels than quiet lives.'),
            ('<p class="instagram-why-desc">Instagram merekomendasikan live dengan viewers aktif. Boost viewers = boost reach di Explore & Reels.</p>',
             '<p class="instagram-why-desc">Instagram recommends lives with active viewers. Boost viewers = boost reach on Explore & Reels.</p>'),
            ('<h3 class="instagram-why-title">Aman untuk Akun</h3>', '<h3 class="instagram-why-title">Safe for Your Account</h3>'),
            ('<p class="instagram-why-desc">Viewers dari kami akun IG aktif. Tidak like spam. Tidak ada aktivitas dari akun Anda. 1.200+ live IG tanpa masalah.</p>',
             '<p class="instagram-why-desc">Our viewers are active IG accounts. No like spam. No activity from your account. 1,200+ IG lives without issues.</p>'),
            ('<h3 class="instagram-why-title">Cocok untuk IG Shopping</h3>', '<h3 class="instagram-why-title">Perfect for IG Shopping</h3>'),
            ('rata-rata Explore', 'average on Explore'),
            ('rata-rata IG live', 'average IG live'),
            ('bg-clip-text text-transparent">live Instagram.</span>', 'bg-clip-text text-transparent">Instagram lives boosted.</span>'),
            ('<span class="text-accent">live Instagram.</span>', '<span class="text-accent">Instagram lives.</span>'),
            ('<h3 class="instagram-trust-title">Aman untuk akun IG</h3>', '<h3 class="instagram-trust-title">Safe for your IG account</h3>'),
            ('<p class="instagram-trust-desc">Viewers dari kami akun riil aktif. Interaksi natural, no flag. 1.200+ live Instagram tanpa satu pun kena shadow ban.</p>',
             '<p class="instagram-trust-desc">Our viewers are real, active accounts. Natural interaction, no flags. 1,200+ Instagram lives without a single shadow ban.</p>'),
            ('<h3 class="instagram-trust-title">Masuk gradual 5-15 menit</h3>', '<h3 class="instagram-trust-title">Gradual join over 5\u201315 minutes</h3>'),
            ('<p class="instagram-trust-desc">Viewers join gradual sejak menit pertama live. Tidak tiba-tiba, tidak mencurigakan — IG notice natural trending.</p>',
             '<p class="instagram-trust-desc">Viewers join gradually from the first minute of your live. Never sudden, never suspicious \u2014 IG sees natural trending.</p>'),
            ('<h3 class="instagram-trust-title">Tanpa minimum order</h3>', '<h3 class="instagram-trust-title">No minimum order</h3>'),
            ('<p class="instagram-trust-desc">Order per sesi, bayar per order. Bebas order sesuai jadwal live Instagram Anda. Diskon 10-15% untuk paket berulang.</p>',
             '<p class="instagram-trust-desc">Order per session, pay per order. Book whenever your Instagram live schedule needs it. 10\u201315% off recurring packages.</p>'),
            ('Live Instagram berikutnya<br/>', 'Your next Instagram live,<br/>'),
            ('>naik reach & Reels.<', '>growing reach &amp; Reels.<'),
        ],
    ),
    'youtube': dict(
        file='youtube-live-viewers.astro', plat='YouTube', slug='youtube-live-viewers',
        svc='YouTube Live Viewers', p=STD, notes=NOTE_STD,
        title='YouTube Live Viewers Malaysia | Boost Recommendations \u2014 Beriklan',
        desc='Boost your YouTube Live viewer count so the YouTube algorithm notices your stream. Real accounts, no bots, safe for your channel. From RM 5 for 20 viewers.',
        wa='Hi%20Beriklan%2C%20I%27m%20interested%20in%20YouTube%20Live%20viewers.%20Please%20share%20packages%20and%20pricing.',
        feat_first="    { iconName: 'Sparkles', title: 'Boost YT Recommendations', desc: 'YouTube recommends lives with active viewers. Boost viewers = boost distribution in YT recommendations.' },",
        pairs=[
            ('Jasa View Live YouTube · Boost Rekomendasi', 'YouTube Live Viewers · Boost Recommendations'),
            ('Live YouTube Sepi,', 'Your YouTube Live Is Quiet,'),
            ('Rekomendasi Tidak Datang.', 'Recommendations Aren\u2019t Coming.'),
            ('YouTube memprioritaskan live dengan viewers aktif. 100+ viewers = 5x lebih besar jangkauan. Viewer riil dari kami join gradual sejak menit pertama — bikin algorithm YouTube notice live Anda, tanpa flag, tanpa bot, tanpa risiko shadow ban.',
             'YouTube prioritises lives with active viewers. 100+ viewers = up to 5x wider reach. Our real viewers join gradually from the very first minute \u2014 getting the YouTube algorithm to notice your live, with no flags, no bots and no shadow-ban risk.'),
            ('stream mantap! 🔥', 'great stream! 🔥'),
            ('>mantap kak<', '>nice one<'),
            ('>sub dong<', '>subbed!<'),
            ('>Rekomendasi YT<', '>YT Recommendations<'),
            ('Apa algoritma YouTube satu hal:<br/>', 'The YouTube algorithm knows one thing:<br/>'),
            ('>banyak viewers = watch time tinggi.<', '>more viewers = higher watch time.<'),
            ('YouTube merekomendasikan live berdasarkan watch time & concurrent viewers. Live dengan 100+ viewers aktif muncul 3x lebih sering di rekomendasi & suggested videos.',
             'YouTube recommends lives based on watch time & concurrent viewers. Lives with 100+ active viewers appear 3x more often in recommendations & suggested videos.'),
            ('<p class="youtube-why-desc">YouTube merekomendasikan live dengan viewers aktif. Boost viewers = boost distribusi di rekomendasi YT.</p>',
             '<p class="youtube-why-desc">YouTube recommends lives with active viewers. Boost viewers = boost distribution in YT recommendations.</p>'),
            ('<h3 class="youtube-why-title">Aman untuk Channel</h3>', '<h3 class="youtube-why-title">Safe for Your Channel</h3>'),
            ('<p class="youtube-why-desc">Viewers dari kami akun YT aktif. Tidak like spam. Tidak ada aktivitas dari akun channel. 1.200+ live tanpa masalah.</p>',
             '<p class="youtube-why-desc">Our viewers are active YT accounts. No like spam. No activity from your channel account. 1,200+ lives without issues.</p>'),
            ('<h3 class="youtube-why-title">Cocok untuk Live Commerce</h3>', '<h3 class="youtube-why-title">Perfect for Live Commerce</h3>'),
            ('rata-rata YT recommended', 'average YT recommended'),
            ('rata-rata YT live', 'average YT live'),
            ('bg-clip-text text-transparent">live YouTube.</span>', 'bg-clip-text text-transparent">YouTube lives boosted.</span>'),
            ('<span class="text-accent">live YouTube.</span>', '<span class="text-accent">YouTube lives.</span>'),
            ('<h3 class="youtube-trust-title">Aman untuk channel YouTube</h3>', '<h3 class="youtube-trust-title">Safe for your YouTube channel</h3>'),
            ('<p class="youtube-trust-desc">Viewers dari kami akun riil aktif. Interaksi natural, no flag. 1.200+ live YouTube tanpa satu pun kena shadow ban.</p>',
             '<p class="youtube-trust-desc">Our viewers are real, active accounts. Natural interaction, no flags. 1,200+ YouTube lives without a single shadow ban.</p>'),
            ('<h3 class="youtube-trust-title">Masuk gradual 5-15 menit</h3>', '<h3 class="youtube-trust-title">Gradual join over 5\u201315 minutes</h3>'),
            ('<p class="youtube-trust-desc">Viewers join gradual sejak menit pertama live. Tidak tiba-tiba, tidak mencurigakan — rekomendasi YT notice natural trending.</p>',
             '<p class="youtube-trust-desc">Viewers join gradually from the first minute of your live. Never sudden, never suspicious \u2014 YT recommendations see natural trending.</p>'),
            ('<h3 class="youtube-trust-title">Tanpa minimum order</h3>', '<h3 class="youtube-trust-title">No minimum order</h3>'),
            ('<p class="youtube-trust-desc">Order per sesi, bayar per order. Bebas order sesuai jadwal live YouTube Anda. Diskon 10-15% untuk paket berulang.</p>',
             '<p class="youtube-trust-desc">Order per session, pay per order. Book whenever your YouTube live schedule needs it. 10\u201315% off recurring packages.</p>'),
            ('Live YouTube berikutnya<br/>', 'Your next YouTube live,<br/>'),
            ('>naik watch time & rekomendasi.<', '>lifting watch time &amp; recommendations.<'),
        ],
    ),
    'twitch': dict(
        file='twitch-live-viewers.astro', plat='Twitch', slug='twitch-live-viewers',
        svc='Twitch Live Viewers', p=STD, notes=NOTE_STD,
        title='Twitch Live Viewers Malaysia | Boost Concurrent Viewers \u2014 Beriklan',
        desc='Boost your Twitch concurrent viewer count so the Twitch algorithm notices your stream. Real accounts, no bots, safe for your channel. From RM 5 for 20 viewers.',
        wa='Hi%20Beriklan%2C%20I%27m%20interested%20in%20Twitch%20Live%20viewers.%20Please%20share%20packages%20and%20pricing.',
        feat_first="    { iconName: 'Sparkles', title: 'Boost Directory Visibility', desc: 'Twitch recommends streams with active viewers. Boost viewers = boost distribution in the Twitch directory.' },",
        pairs=[
            ('Jasa View Live Twitch · Boost Rekomendasi', 'Twitch Live Viewers · Boost Recommendations'),
            ('Live Twitch Sepi,', 'Your Twitch Stream Is Quiet,'),
            ('Discover Tidak Rekomendasi.', 'Discovery Isn\u2019t Recommending You.'),
            ('— Butuh Viewers Aktif.', '\u2014 You Need Active Viewers.'),
            ('Twitch memprioritaskan live dengan viewers aktif. 100+ viewers = 5x lebih besar jangkauan. Viewer riil dari kami join gradual sejak menit pertama — bikin algorithm Twitch notice live Anda, tanpa flag, tanpa bot, tanpa risiko shadow ban.',
             'Twitch prioritises streams with active viewers. 100+ viewers = up to 5x wider reach. Our real viewers join gradually from the very first minute \u2014 getting the Twitch algorithm to notice your stream, with no flags, no bots and no shadow-ban risk.'),
            ('stream mantap bro!', 'great stream bro!'),
            ('Kek pov 7 bro', 'poggers bro'),
            ('>folowed!<', '>followed!<'),
            ('Apa algoritma Twitch satu hal:<br/>', 'The Twitch algorithm knows one thing:<br/>'),
            ('>banyak viewers = muncul di direktori.<', '>more viewers = directory visibility.<'),
            ('Twitch memprioritaskan live dengan viewers aktif. Live dengan 100+ viewers muncul 4x lebih sering di rekomendasi dibanding live dengan 20 viewers.',
             'Twitch prioritises streams with active viewers. Streams with 100+ viewers appear 4x more often in recommendations than streams with 20.'),
            ('<p class="twitch-why-desc">Twitch merekomendasikan live dengan viewers aktif. Boost viewers = boost distribusi di direktori Twitch.</p>',
             '<p class="twitch-why-desc">Twitch recommends streams with active viewers. Boost viewers = boost distribution in the Twitch directory.</p>'),
            ('<h3 class="twitch-why-title">Aman untuk Channel</h3>', '<h3 class="twitch-why-title">Safe for Your Channel</h3>'),
            ('<p class="twitch-why-desc">Viewers dari kami akun Twitch aktif. Tidak spam chat. Tidak ada aktivitas dari akun channel. 1.200+ live tanpa masalah.</p>',
             '<p class="twitch-why-desc">Our viewers are active Twitch accounts. No chat spam. No activity from your channel account. 1,200+ streams without issues.</p>'),
            ('<h3 class="twitch-why-title">Cocok untuk Semua Genre</h3>', '<h3 class="twitch-why-title">Great for Every Genre</h3>'),
            ('<p class="twitch-why-desc">Cocok untuk gaming, just chatting, music, art, atau IRL stream. Viewer real account stay & engage.</p>',
             '<p class="twitch-why-desc">Works for gaming, just chatting, music, art or IRL streams. Real-account viewers stay &amp; engage.</p>'),
            ('rata-rata Twitch live', 'average Twitch live'),
            ('rata-rata Twitch', 'average on Twitch'),
            ('bg-clip-text text-transparent">live Twitch.</span>', 'bg-clip-text text-transparent">Twitch streams boosted.</span>'),
            ('<span class="text-accent">live Twitch.</span>', '<span class="text-accent">Twitch streams.</span>'),
            ('<h3 class="twitch-trust-title">Aman untuk channel Twitch</h3>', '<h3 class="twitch-trust-title">Safe for your Twitch channel</h3>'),
            ('<p class="twitch-trust-desc">Viewers dari kami akun riil aktif. Interaksi natural, no flag. 1.200+ live Twitch tanpa satu pun kena shadow ban.</p>',
             '<p class="twitch-trust-desc">Our viewers are real, active accounts. Natural interaction, no flags. 1,200+ Twitch streams without a single shadow ban.</p>'),
            ('<h3 class="twitch-trust-title">Masuk gradual 5-15 menit</h3>', '<h3 class="twitch-trust-title">Gradual join over 5\u201315 minutes</h3>'),
            ('<p class="twitch-trust-desc">Viewers join gradual sejak menit pertama stream. Tidak tiba-tiba, tidak mencurigakan — direktori Twitch notice natural trending.</p>',
             '<p class="twitch-trust-desc">Viewers join gradually from the first minute of your stream. Never sudden, never suspicious \u2014 the Twitch directory sees natural trending.</p>'),
            ('<h3 class="twitch-trust-title">Tanpa minimum order</h3>', '<h3 class="twitch-trust-title">No minimum order</h3>'),
            ('<p class="twitch-trust-desc">Order per sesi, bayar per order. Bebas order sesuai jadwal live Twitch Anda. Diskon 10-15% untuk paket berulang.</p>',
             '<p class="twitch-trust-desc">Order per session, pay per order. Book whenever your Twitch schedule needs it. 10\u201315% off recurring packages.</p>'),
            ('Live Twitch berikutnya<br/>', 'Your next Twitch stream,<br/>'),
            ('>naik di direktori.<', '>rising in the directory.<'),
        ],
    ),
}

# Shared body pairs applied to all 5 platform pages (platform-templated where needed)
def shared_pairs(plat, p0):
    return [
        ('const waLink = "https://wa.me/62811919328?text=Halo%20Beriklan',  # prefix only marker; replaced fully below
         None),
    ]


def apply(txt, pairs, hits, fname):
    for old, new in pairs:
        c = txt.count(old)
        if c:
            txt = txt.replace(old, new)
            hits.append((fname, old[:60], c))
        else:
            hits.append((fname, 'MISS: ' + old[:60], 0))
    return txt


def main():
    total = 0
    misses = []
    for key, c in CFG.items():
        fp = PAGES + c['file']
        txt = open(fp, encoding='utf-8').read()
        orig = txt

        # 1. waLink
        txt = re.sub(r'const waLink = "https://wa\.me/62811919328\?text=[^"]*";',
                     'const waLink = "https://wa.me/62811919328?text=%s";' % c['wa'], txt)

        # 2. data arrays wholesale
        for pat, repl in [
            (r'const tiers = \[.*?\n\];', build_tiers(c['plat'], c['p'], c['notes'])),
            (r'const features = \[.*?\n\];', build_features(c['plat'], c['feat_first'])),
            (r'const steps = \[.*?\n\];', build_steps(c['plat'])),
            (r'const faqs = \[.*?\n\];', faqs_js(c['plat'])),
        ]:
            new_txt, n = re.subn(pat, lambda m: repl, txt, count=1, flags=re.S)
            if n != 1:
                print('FATAL: block %s not replaced in %s' % (pat[:20], c['file'])); sys.exit(1)
            txt = new_txt

        # 3. Layout block (kills duplicate props + >>> bug)
        new_txt, n = re.subn(r'<Layout title="Jasa View Live[^"]*".*?\n>+\n',
                             lambda m: build_layout(c), txt, count=1, flags=re.S)
        if n != 1:
            print('FATAL: Layout block not replaced in %s' % c['file']); sys.exit(1)
        txt = new_txt

        # 4. platform-templated common pairs
        common = [
            ('Order Viewers %s' % c['plat'], 'Order %s Viewers' % c['plat']),
            ('<strong class="text-white">Mulai Rp 12.000</strong> untuk 20 viewers',
             '<strong class="text-white">From RM %s</strong> for 20 viewers' % c['p'][0]),
            ('Optimal untuk %s' % c['plat'], 'Optimised for %s' % c['plat']),
            ('Kenapa View Live %s' % c['plat'], 'Why %s Live Viewers' % c['plat']),
            ('6 Keunggulan Layanan', '6 Service Advantages'),
            ('Dari order sampai FYP trending,<br/>', 'From order to trending,<br/>'),
            ('>kurang dari 30 menit.<', '>in under 30 minutes.<'),
            ('>sampai launching akbar.<', '>to a full-scale launch.<'),
            ('pageSlug="View Live %s"' % c['plat'], 'pageSlug="%s Live Viewers"' % c['plat']),
            ('>Bukti Nyata', '>Real Proof'),
            ('Sudah 1.200+<br/>', 'Over 1,200<br/>'),
            ('>Diskon rutin<', '>Recurring discount<'),
            ('>paket mingguan<', '>weekly packages<'),
            ('>sepanjang penggunaan<', '>across all usage<'),
            ('Pertanyaan tentang<br/>', 'Questions about<br/>'),
            ('>Sebelum order<', '>Before you order<'),
            ('Tim online · respon dalam 1 jam pada jam kerja', 'Team online · replies within 1 hour during business hours'),
            ('Ceritakan tanggal live %s Anda via WhatsApp. Kami kirim rekomendasi paket & timeline. Tanpa komitmen — order hanya saat Anda siap live.' % c['plat'],
             'Tell us your %s live date on WhatsApp. We\u2019ll send a package recommendation & timeline. No commitment \u2014 order only when you\u2019re ready to go live.' % c['plat']),
            ('kak ini diskon berapa?', 'how much is the discount?'),
            ('>Rp 99K<', '>RM 29<'),
            ('TAP UNTUK BELI', 'TAP TO BUY'),
            ("label: 'Jasa View Live Multi-Platform', desc: 'Satu order, semua platform live.'",
             "label: 'Multi-Platform Live Viewers', desc: 'One order, every live platform.'"),
        ]
        hits = []
        txt = apply(txt, common + c['pairs'], hits, c['file'])
        for f, s, n in hits:
            if n == 0 and not s.startswith('MISS: kak ini diskon') and 'TAP UNTUK' not in s:
                misses.append((f, s))

        if txt != orig:
            open(fp, 'w', encoding='utf-8').write(txt)
            n_rep = sum(h[2] for h in hits)
            print('%s: arrays+layout replaced, %d string hits' % (c['file'], n_rep))
            total += n_rep

    print('TOTAL string hits:', total)
    if misses:
        print('\n--- MISSES (check manually) ---')
        for f, s in misses:
            print(f, '|', s)


if __name__ == '__main__':
    main()
