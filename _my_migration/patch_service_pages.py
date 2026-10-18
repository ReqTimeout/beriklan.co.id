#!/usr/bin/env python3
"""F1-7 pass 3: 10 service pages -> English + MYR.
- tiers/faqs regenerated from services.json (already English+MYR from F1-9)
- duplicated <Layout ...>> block replaced with clean English block
- body leftovers translated via exact pairs + line-prefix replacement
"""
import json, re, sys

PAGES = "/Users/maabook/Desktop/beriklan.my/web/src/pages/"
SVC = json.load(open("/Users/maabook/Desktop/beriklan.my/web/src/data/services.json"))
BYSLUG = {s['slug']: s for s in SVC}

def esc(s):
    return s.replace("\\", "\\\\").replace("'", "\\'")

def js_tiers(svc):
    rows = []
    for i, t in enumerate(svc['tiers']):
        feats = ", ".join("'%s'" % esc(f) for f in t['features'])
        row = ("    { name: '%s', priceLabel: '%s', duration: '%s', tagline: '%s', features: [%s], priceNote: '%s', disclaimer: '%s'%s },"
               % (esc(t['name']), esc(t['priceLabel']), esc(t.get('duration', 'per month')), esc(t['tagline']),
                  feats, esc(t.get('priceNote', '')), esc(t.get('disclaimer', '')),
                  ", highlight: true" if i == 1 else ""))
        rows.append(row)
    return "const tiers = [\n" + "\n".join(rows) + "\n];"

def js_faqs(svc):
    rows = ["    { q: '%s', a: '%s' }," % (esc(f['q']), esc(f['a'])) for f in svc['faqs']]
    return "const faqs = [\n" + "\n".join(rows) + "\n];"

def layout_block(cfg, svc):
    faq_rows = ",\n".join("        { question: '%s', answer: '%s' }" % (esc(f['q']), esc(f['a'])) for f in svc['faqs'])
    return (
        '<Layout\n'
        '    title="%s"\n' % cfg['title']
        + '    description="%s"\n' % cfg['desc']
        + '    canonical="https://beriklan.my/%s/"\n' % svc['slug']
        + '    faq={[\n' + faq_rows + '\n    ]}\n'
        + '    breadcrumb={[\n'
        + '        { name: "Home", url: "https://beriklan.my/" },\n'
        + '        { name: "%s", url: "https://beriklan.my/%s/" }\n' % (svc['name'], svc['slug'])
        + '    ]}\n'
        + '    service={{\n'
        + '        name: "%s",\n' % svc['name']
        + '        description: "%s",\n' % svc['description'].replace('"', '\\"')
        + '        url: "https://beriklan.my/%s/",\n' % svc['slug']
        + '        priceRange: "%s",\n' % cfg['price_range']
        + '        serviceType: "%s",\n' % cfg['service_type']
        + '        areaServed: "Malaysia",\n'
        + '        provider: { name: "Beriklan.my", url: "https://beriklan.my" }\n'
        + '    }}\n'
        + '>\n'
    )

# tolerant global pairs (no MISS report)
TOLERANT = [
    ('pageSlug="Iklan Facebook"', 'pageSlug="Facebook Ads"'),
    ('pageSlug="Iklan Instagram"', 'pageSlug="Instagram Ads"'),
    ('pageSlug="Iklan TikTok"', 'pageSlug="TikTok Ads"'),
    ('pageSlug="Iklan Google"', 'pageSlug="Google Ads"'),
    ('pageSlug="Iklan YouTube"', 'pageSlug="YouTube Ads"'),
    ('pageSlug="Kelola Instagram"', 'pageSlug="Instagram Management"'),
    ('pageSlug="Kelola TikTok"', 'pageSlug="TikTok Management"'),
    ('pageSlug="Pembuatan Website"', 'pageSlug="Website Development"'),
    ('serviceName="Iklan Facebook"', 'serviceName="Facebook Ads"'),
    ('serviceName="Iklan Instagram"', 'serviceName="Instagram Ads"'),
    ('serviceName="Iklan TikTok"', 'serviceName="TikTok Ads"'),
    ('serviceName="Iklan Google"', 'serviceName="Google Ads"'),
    ('serviceName="Iklan YouTube"', 'serviceName="YouTube Ads"'),
]

CFG = {
 'facebook-ads-management': dict(
    title='Facebook Ads Management Malaysia | Meta-Certified Team \u2014 Beriklan',
    desc='Facebook Ads that generate leads & sales, not just impressions. Precise targeting, proven creative, measurable ROAS. Managing Meta Ads since 2016. Contact us.',
    price_range='RM 990 - RM 2,990', service_type='Facebook Ads',
    wa='Hi%20Beriklan%2C%20I%27m%20interested%20in%20Facebook%20Ads%20management.%20Please%20share%20packages%20and%20pricing.',
    pairs=[
      ('Jasa Iklan Facebook Ads · Meta Business Partner', 'Facebook Ads Management · Meta Business Partner'),
      ('>Jasa Iklan Facebook</span>', '>Facebook Ads Management</span>'),
      ('>yang Menjangkau Audiens Tepat,<', '>That Reaches the Right Audience,<'),
      ('>Mendorong Chat WhatsApp.<', '>and Drives WhatsApp Chats.<'),
      ('Kenapa Facebook Ads', 'Why Facebook Ads'),
      ('Bukan sekadar jangkauan,<br/>', 'Not just reach,<br/>'),
      ('<span class="text-accent">tapi penargetan yang presisi.</span>', '<span class="text-accent">but precision targeting.</span>'),
      ('<h3 class="why-title">Data yang Terbaca</h3>', '<h3 class="why-title">Data You Can Read</h3>'),
      ('pillarLabel="Panduan Lengkap Iklan Facebook"', 'pillarLabel="Complete Facebook Ads Guide"'),
    ],
    lines=[
      ('<strong class="text-ink">120 juta lebih</strong>',
       '<strong class="text-ink">Millions</strong> of Malaysians log in to Facebook &amp; Instagram every day \u2014 your future customers among them. But simply appearing in front of them is not enough. What matters is who you reach, with what message, and where they finally take action. We handle all of it \u2014 from audience research and copy that speaks, to measured weekly optimisation.'),
      ('Banyak bisnis sudah mencoba Facebook Ads',
       'Many businesses have tried Facebook Ads with underwhelming results. The cause is usually not the platform \u2014 it is targeting, creative and placement that are out of sync with the audience.'),
      ('<p class="why-desc">Lebih dari 100 kategori minat',
       '<p class="why-desc">More than 100 interest, behaviour and demographic categories that can be combined. We pick the mix that best matches your audience\u2019s character.</p>'),
      ('<p class="why-desc">Dashboard Meta menampilkan data detail',
       '<p class="why-desc">The Meta dashboard shows detailed data on who viewed, clicked and enquired \u2014 all of it verifiable by you.</p>'),
      ('<p class="why-desc">Tombol Call-to-Action bawaan Meta',
       '<p class="why-desc">Meta\u2019s built-in call-to-action buttons send clicks straight to WhatsApp \u2014 shortening the distance from \u201cinterested\u201d to \u201cin conversation\u201d.</p>'),
      ('Angka di bawah adalah biaya jasa pengelolaan',
       'The numbers below are campaign management fees. Meta ad spend is paid directly by you \u2014 no markup, no hidden costs.'),
      ('Bukan sekadar pasang iklan. Kami menyusun strategi yang selaras dengan karakter bisnis',
       'More than just running ads. We build a strategy aligned with the character of your business \u2014 so every ringgit you invest works at its best.'),
    ]),
 'instagram-ads-management': dict(
    title='Instagram Ads Management Malaysia | Reach & Engagement \u2014 Beriklan',
    desc='Targeted Instagram ads across Feed, Stories and Reels that turn impressions into DMs and WhatsApp chats. Meta-certified team, weekly reports. Contact us.',
    price_range='RM 990 - RM 2,990', service_type='Instagram Ads',
    wa='Hi%20Beriklan%2C%20I%27m%20interested%20in%20Instagram%20Ads%20management.%20Please%20share%20packages%20and%20pricing.',
    pairs=[
      ('Jasa Iklan Instagram · Reach & Engagement', 'Instagram Ads Management · Reach & Engagement'),
      ('>Jasa Iklan Instagram</span>', '>Instagram Ads Management</span>'),
      ('>untuk Menemukan Pelanggan Baru<', '>to Find New Customers<'),
      ('>Lewat Konten Visual.<', '>Through Visual Content.<'),
      ('Kenapa Instagram Ads', 'Why Instagram Ads'),
      ('Bukan sekadar konten visual,<br/>', 'Not just visual content,<br/>'),
      ('<span class="text-accent">tapi penargetan yang selaras audiens.</span>', '<span class="text-accent">but targeting aligned with your audience.</span>'),
      ('pillarLabel="Panduan Lengkap Iklan Instagram"', 'pillarLabel="Complete Instagram Ads Guide"'),
    ],
    lines=[
      ('Setiap hari ratusan juta orang menggunakan Instagram',
       'Hundreds of millions of people use Instagram every day to discover inspiration and new products. We help your business run targeted ads across Feed, Stories and Reels \u2014 turning impressions into profile visits, DMs or WhatsApp chats.'),
      ('Banyak bisnis sudah mencoba Instagram Ads',
       'Many businesses have tried Instagram Ads with underwhelming results. The cause is usually not the platform \u2014 it is targeting, placement formats and visuals that clash with how Instagram audiences behave.'),
      ('<p class="why-desc">Instagram didominasi audiens usia 18-34',
       '<p class="why-desc">Instagram is dominated by 18\u201334 year olds actively hunting for new products. The right targeting reaches them in the exploration phase \u2014 before they pick a competitor.</p>'),
      ('<p class="why-desc">Dashboard Meta menampilkan data tentang siapa',
       '<p class="why-desc">The Meta dashboard shows who viewed, clicked and engaged \u2014 all verifiable by you, including audience location, age and interests.</p>'),
      ('<p class="why-desc">CTA bawaan Meta mengirim klik',
       '<p class="why-desc">Meta\u2019s built-in CTAs send clicks straight to Instagram Direct Messages or WhatsApp \u2014 shortening the distance from \u201cinterested\u201d to \u201cin conversation\u201d.</p>'),
      ('Bukan sekadar pasang iklan Instagram.',
       'More than just running Instagram ads. We build a strategy aligned with your brand and audience \u2014 so every ringgit you invest produces measurable engagement.'),
    ]),
 'tiktok-ads-management': dict(
    title='TikTok Ads Management Malaysia | Spark Ads & FYP \u2014 Beriklan',
    desc='TikTok ads built for the FYP algorithm \u2014 short videos that turn views into leads. Managed end-to-end with weekly reports. From RM 790/month. Contact us.',
    price_range='RM 790 - RM 1,990', service_type='TikTok Ads',
    wa='Hi%20Beriklan%2C%20I%27m%20interested%20in%20TikTok%20Ads%20management.%20Please%20share%20packages%20and%20pricing.',
    pairs=[
      ('Jasa Iklan TikTok Ads · Spark & FYP', 'TikTok Ads Management · Spark & FYP'),
      ('>Jasa Iklan TikTok</span>', '>TikTok Ads Management</span>'),
      ('>untuk Menjangkau Audiens<', '>to Reach Your Audience<'),
      ('>dengan Konten yang Menghibur.<', '>With Entertaining Content.<'),
      ('Kenapa TikTok Ads', 'Why TikTok Ads'),
      ('Bukan sekadar video viral,<br/>', 'Not just viral videos,<br/>'),
      ('<span class="text-accent">tapi penargetan yang menghasilkan leads.</span>', '<span class="text-accent">but targeting that generates leads.</span>'),
      ('<h3 class="why-title">Penargetan FYP yang Tepat</h3>', '<h3 class="why-title">Precise FYP Targeting</h3>'),
      ('pillarLabel="Panduan Lengkap Iklan Tiktok"', 'pillarLabel="Complete TikTok Ads Guide"'),
    ],
    lines=[
      ('TikTok menjadi kanal penemuan produk',
       'TikTok is Malaysia\u2019s fastest-growing product discovery channel. We help your business create targeted short-video ads \u2014 turning views into followers, profile visits, or WhatsApp chats ready to talk.'),
      ('Banyak bisnis sudah mencoba TikTok Ads',
       'Many businesses have tried TikTok Ads with underwhelming results. The usual causes: videos not optimised for the FYP algorithm, or targeting so broad the views never hit potential buyers.'),
      ('<p class="why-desc">Algoritma TikTok For You Page membaca',
       '<p class="why-desc">TikTok\u2019s For You Page algorithm reads user interests, behaviour and interaction patterns. We tune the parameters so your ads reach people genuinely likely to be interested \u2014 not random viewers.</p>'),
      ('<p class="why-desc">Dashboard iklan TikTok menampilkan views',
       '<p class="why-desc">TikTok\u2019s ads dashboard shows views, watch time and engagement in real time. Check video performance any time \u2014 we adjust strategy based on the data.</p>'),
      ('<p class="why-desc">Tombol Call-to-Action bawaan TikTok',
       '<p class="why-desc">TikTok\u2019s built-in call-to-action button can link straight to WhatsApp. From viewer to chat \u2014 all in one smooth flow.</p>'),
      ('Bukan sekadar membuat video viral.',
       'More than just chasing viral videos. We build a strategy aligned with your brand and the TikTok algorithm \u2014 so every view you earn can become a lead or a conversion.'),
    ]),
 'google-ads-management': dict(
    title='Google Ads Management Malaysia | Search, Display & YouTube \u2014 Beriklan',
    desc='Google Ads managed by a certified team: keyword strategy, controlled bids and conversion tracking. Reach people actively searching. From RM 990/month. Contact us.',
    price_range='RM 990 - RM 2,790', service_type='Google Ads',
    wa='Hi%20Beriklan%2C%20I%27m%20interested%20in%20Google%20Ads%20management.%20Please%20share%20packages%20and%20pricing.',
    pairs=[
      ('Jasa Iklan Google Ads · Search, Display & YouTube', 'Google Ads Management · Search, Display & YouTube'),
      ('>Jasa Iklan Google</span>', '>Google Ads Management</span>'),
      ('>Tangkap Intent Tinggi<', '>to Capture High Intent<'),
      ('>Saat Mereka Mencari.<', '>Right When They Search.<'),
      ('Kenapa Google Ads', 'Why Google Ads'),
      ('Bukan sekadar muncul di Google,<br/>', 'Not just showing up on Google,<br/>'),
      ('<span class="text-accent">tapi kata kunci yang mendatangkan pelanggan.</span>', '<span class="text-accent">but keywords that bring in customers.</span>'),
      ('pillarLabel="Panduan Lengkap Iklan Google"', 'pillarLabel="Complete Google Ads Guide"'),
    ],
    lines=[
      ('Google Search Ads menjangkau orang yang sedang',
       'Google Search Ads reach people <strong class="text-ink">actively searching</strong> for your product or service \u2014 not people idly scrolling. Your ad appears on page one with controlled bids. We manage the keyword strategy, copy and landing page.'),
      ('Google Ads berbeda dari platform sosial',
       'Google Ads differs from social platforms: here, the people seeing your ad are actively searching for a similar product or service. The power \u2014 and the challenge: every keyword must be chosen carefully, because the wrong bids can drain your budget with nothing to show.'),
      ('<p class="why-desc">Google Ads menjangkau orang yang secara aktif',
       '<p class="why-desc">Google Ads reaches people actively searching \u2014 not scrolling. They already have the need; your ad simply appears at the right moment.</p>'),
      ('<p class="why-desc">Anda tentukan budget harian',
       '<p class="why-desc">You set the daily budget. Google only charges when there is a qualified click. No spend beyond the budget you set.</p>'),
      ('<p class="why-desc">Google Ads dapat diarahkan ke klik website',
       '<p class="why-desc">Google Ads can drive website clicks, WhatsApp chats, phone calls or store visits. Whatever your objective, we set up the conversion tracking.</p>'),
      ('Bukan sekadar menawar kata kunci.',
       'More than just bidding on keywords. We build a strategy aligned with your business objective \u2014 branding, lead generation or direct sales \u2014 so every click you pay for can become a customer.'),
    ]),
 'youtube-ads-management': dict(
    title='YouTube Ads Management Malaysia | Video Ads & Awareness \u2014 Beriklan',
    desc='Targeted YouTube video ads that build brand awareness and trust. Format strategy, precise targeting, weekly reports. From RM 890/month. Contact us.',
    price_range='RM 890 - RM 2,490', service_type='YouTube Ads',
    wa='Hi%20Beriklan%2C%20I%27m%20interested%20in%20YouTube%20Ads%20management.%20Please%20share%20packages%20and%20pricing.',
    pairs=[
      ('Jasa Iklan YouTube · Video Ads & Awareness', 'YouTube Ads Management · Video Ads & Awareness'),
      ('>Jasa Iklan YouTube</span>', '>YouTube Ads Management</span>'),
      ('>Bangun Brand Awareness<', '>to Build Brand Awareness<'),
      ('>Lewat Video.<', '>Through Video.<'),
      ('Kenapa YouTube Ads', 'Why YouTube Ads'),
      ('Bukan sekadar tayang di YouTube,<br/>', 'Not just airing on YouTube,<br/>'),
      ('<span class="text-accent">tapi video yang membangun brand dan trust.</span>', '<span class="text-accent">but video that builds brand and trust.</span>'),
      ('<h3 class="why-title">Brand Awareness yang Terukur</h3>', '<h3 class="why-title">Measurable Brand Awareness</h3>'),
      ('pillarLabel="Panduan Lengkap Iklan Youtube"', 'pillarLabel="Complete YouTube Ads Guide"'),
    ],
    lines=[
      ('YouTube adalah platform video terbesar',
       'YouTube is Malaysia\u2019s biggest video platform, with millions of active viewers every day. We help your business run targeted video ads \u2014 so your message is seen by the right audience, on the right channels, at the right moment.'),
      ('YouTube adalah platform pencarian terbesar kedua',
       'YouTube is the world\u2019s second-largest search platform after Google \u2014 especially for educational and review content. Your video ad plays before, during or after the videos your audience watches. Video\u2019s strength: it explains product value in 15\u201330 seconds far more persuasively than text.'),
      ('<p class="why-desc">YouTube Ads memungkinkan targeting',
       '<p class="why-desc">YouTube Ads allow targeting by interest and demographics, right down to placement on specific channels. We pick the combination that fits your business.</p>'),
      ('<p class="why-desc">Dashboard iklan YouTube menampilkan views',
       '<p class="why-desc">The YouTube ads dashboard shows views, watch time and brand lift. You can see whether your video is watched to the end or skipped at second five.</p>'),
      ('<p class="why-desc">Pilih format: skippable',
       '<p class="why-desc">Pick a format: skippable, non-skippable, 6-second bumper or in-feed. Each has its own strengths depending on your objective.</p>'),
      ('Bukan sekadar menayangkan video.',
       'More than just airing videos. We build a strategy aligned with your objective \u2014 building brand awareness, introducing a new product, or driving viewers to a specific action.'),
    ]),
 'instagram-management': dict(
    title='Instagram Management Malaysia | Content & Community \u2014 Beriklan',
    desc='End-to-end Instagram management: concept, design, copy, scheduling and monthly reports. Keep your brand alive while you run the business. From RM 1,290/month.',
    price_range='RM 1,290 - RM 1,990', service_type='Social Media Management',
    wa='Hi%20Beriklan%2C%20I%27m%20interested%20in%20Instagram%20account%20management.%20Please%20share%20packages%20and%20pricing.',
    pairs=[
      ('Jasa Kelola Instagram · Konten & Community', 'Instagram Management · Content & Community'),
      ('>Jasa Kelola Instagram</span>', '>Instagram Management</span>'),
      ('>Konsistensi Konten,<', '>Consistent Content,<'),
      ('>Pertumbuhan yang Terukur.<', '>Measurable Growth.<'),
      ('Kenapa Kelola Instagram', 'Why Instagram Management'),
      ('Bukan sekadar posting rutin,<br/>', 'Not just routine posting,<br/>'),
      ('<span class="text-accent">tapi konten yang terukur dan selaras brand.</span>', '<span class="text-accent">but measurable, on-brand content.</span>'),
      ('<h3 class="why-title">Desain Feed yang Konsisten</h3>', '<h3 class="why-title">A Consistent Feed Design</h3>'),
      ('<h3 class="why-title">Report yang Detail</h3>', '<h3 class="why-title">Detailed Reporting</h3>'),
      ('pillarLabel="Panduan Lengkap Kelola Instagram"', 'pillarLabel="Complete Instagram Management Guide"'),
    ],
    lines=[
      ('Instagram yang aktif dan tertata membutuhkan',
       'An active, well-curated Instagram takes time and consistency. Our team manages your Instagram account end-to-end \u2014 concept, copy, design, scheduling and weekly reports. You focus on the business; we keep the brand alive.'),
      ('Instagram adalah platform di mana keputusan pembelian',
       'Instagram is where many purchase decisions happen \u2014 especially for consumer products. But running an account consistently takes time: design, copy, scheduling, follower engagement and performance monitoring. Our team takes all of that over, with output you can verify any time.'),
      ('<p class="why-desc">Kami menjaga feed Instagram',
       '<p class="why-desc">We keep your Instagram feed curated with a consistent brand aesthetic. Every post goes through visual curation before publishing.</p>'),
      ('<p class="why-desc">Laporan bulanan disusun',
       '<p class="why-desc">Monthly reports written in plain language: which posts performed, which need iteration, and recommendations for next month.</p>'),
      ('<p class="why-desc">Tim kami mengelola balasan DM',
       '<p class="why-desc">Our team manages DM replies and comments to keep engagement active. Fast responses in the comments boost organic reach.</p>'),
      ('Bukan sekadar menjaga akun tetap aktif.',
       'More than keeping the account alive. We build a content strategy aligned with your brand and audience behaviour \u2014 so every post can become a meaningful point of engagement.'),
    ]),
 'tiktok-management': dict(
    title='TikTok Management Malaysia | Consistent Video Content \u2014 Beriklan',
    desc='End-to-end TikTok management: trend research, video production, editing and engagement. Content built for the FYP algorithm. From RM 990/month.',
    price_range='RM 990 - RM 2,490', service_type='Social Media Management',
    wa='Hi%20Beriklan%2C%20I%27m%20interested%20in%20TikTok%20account%20management.%20Please%20share%20packages%20and%20pricing.',
    pairs=[
      ('Jasa Kelola TikTok · Konten Video Rutin', 'TikTok Management · Consistent Video Content'),
      ('>Jasa Kelola TikTok</span>', '>TikTok Management</span>'),
      ('>Konten Berkualitas,<', '>Quality Content,<'),
      ('>Followers Bertumbuh.<', '>Growing Followers.<'),
      ('Kenapa Kelola TikTok', 'Why TikTok Management'),
      ('Bukan sekadar video banyak,<br/>', 'Not just lots of videos,<br/>'),
      ('<span class="text-accent">tapi konten yang relevan dan algoritmis.</span>', '<span class="text-accent">but relevant, algorithm-friendly content.</span>'),
      ('<h3 class="why-title">Format yang Tepat</h3>', '<h3 class="why-title">The Right Format</h3>'),
      ('pillarLabel="Panduan Lengkap Kelola Tiktok"', 'pillarLabel="Complete TikTok Management Guide"'),
    ],
    lines=[
      ('TikTok membutuhkan konten yang konsisten',
       'TikTok demands consistent content that works with the FYP algorithm. Our team manages your TikTok account end-to-end \u2014 music research, concepts, video production, editing and engagement optimisation. You focus on the product; we keep the brand heard.'),
      ('TikTok berbeda dari platform lain',
       'TikTok is different: the FYP algorithm decides who sees your videos \u2014 not just your followers. Content has to hook within the first 3 seconds and match trending patterns. We research the music, sounds and formats that work with the algorithm, without losing your brand\u2019s essence.'),
      ('<p class="why-desc">Kami riset musik, sound',
       '<p class="why-desc">We research trending music, sounds and hashtags to raise the odds of your videos hitting the right audience\u2019s FYP.</p>'),
      ('<p class="why-desc">Edukasi, entertainment, atau review',
       '<p class="why-desc">Education, entertainment or reviews \u2014 each format plays a different role. We mix all three so your audience never gets bored and the algorithm stays interested.</p>'),
      ('<p class="why-desc">Tim kami merespons komentar',
       '<p class="why-desc">Our team replies to comments in a consistent brand tone. A lively comment section builds trust and sends positive signals to the algorithm.</p>'),
      ('Bukan sekadar membuat video banyak.',
       'More than churning out videos. We build a content strategy aligned with the TikTok algorithm and your brand \u2014 so every video has a shot at going viral or reaching new audiences.'),
    ]),
 'website-development': dict(
    title='Website Development Malaysia | Fast, SEO-Ready & Custom \u2014 Beriklan',
    desc='Professional website development: fast loading, mobile responsive, SEO-ready and conversion-focused. Starter sites from RM 1,499. Contact us.',
    price_range='RM 1,499 - RM 6,999', service_type='Web Development',
    wa='Hi%20Beriklan%2C%20I%27m%20interested%20in%20website%20development.%20Please%20share%20packages%20and%20pricing.',
    pairs=[
      ('Jasa Pembuatan Website Profesional · Custom & CMS', 'Professional Website Development · Custom & CMS'),
      ('>Jasa Pembuatan Website</span>', '>Website Development</span>'),
      ('>Profesional, Cepat,<', '>Professional, Fast,<'),
      ('>Siap Menarik Pelanggan.<', '>Ready to Win Customers.<'),
      ('Kenapa Jasa Website', 'Why Our Websites'),
      ('Bukan sekadar website yang terlihat bagus,<br/>', 'Not just a good-looking website,<br/>'),
      ('<span class="text-accent">tapi website yang menghasilkan leads.</span>', '<span class="text-accent">but a website that generates leads.</span>'),
      ('<h3 class="why-title">Responsive Semua Device</h3>', '<h3 class="why-title">Responsive on Every Device</h3>'),
      ('pillarLabel="Panduan Lengkap Pembuatan Website"', 'pillarLabel="Complete Website Development Guide"'),
    ],
    lines=[
      ('Website yang baik bukan sekadar tampil',
       'A good website does more than look the part \u2014 it must load fast, stay responsive on every device, be easy to find on Google, and be conversion-ready. We build your website with modern technology and industry standards.'),
      ('Website yang baik adalah pondasi digital',
       'A good website is a business\u2019s digital foundation: the hub of every online activity \u2014 the landing spot for ads, the verification point for customers, the product catalogue for transactions. We build to modern standards: fast load, SEO-ready, mobile responsive and conversion-focused.'),
      ('<p class="why-desc">Website dioptimasi untuk kecepatan dan mesin pencari',
       '<p class="why-desc">Optimised for speed and search engines. Page speed under 3 seconds and solid SEO structure come as standard.</p>'),
      ('<p class="why-desc">Website tampil sempurna di desktop',
       '<p class="why-desc">Your website renders perfectly on desktop, tablet and mobile. Over 70% of Malaysian traffic is mobile \u2014 this is a necessity, not an option.</p>'),
      ('<p class="why-desc">SSL certificate, backup rutin',
       '<p class="why-desc">SSL certificate, routine backups and uptime monitoring. Your website stays safe from common threats and always reachable by customers.</p>'),
      ('Bukan sekadar website yang cantik.',
       'More than a pretty website. We build to industry standards that generate leads and grow trust \u2014 so every visit can become a customer.'),
    ]),
 'landing-page-design': dict(
    title='Landing Page + Google Ads Malaysia | Conversion Bundle \u2014 Beriklan',
    desc='One professional landing page + one month of managed Google Ads. Leads from day one, full conversion tracking. From RM 1,299. Contact us.',
    price_range='RM 1,299 - RM 2,999', service_type='Landing Page & Google Ads',
    wa='Hi%20Beriklan%2C%20I%27m%20interested%20in%20the%20Landing%20Page%20%2B%20Google%20Ads%20bundle.%20Please%20share%20packages%20and%20pricing.',
    pairs=[
      ('Landing Page + Google Ads · Paket Konversi', 'Landing Page + Google Ads · Conversion Bundle'),
      ('>Langsung Dapat Leads<', '>Start Getting Leads<'),
      ('>dari Hari Pertama.<', '>From Day One.<'),
      ('Kenapa Paket Ini', 'Why This Bundle'),
      ('Bukan sekadar landing page dan iklan,<br/>', 'Not just a landing page and ads,<br/>'),
      ('<span class="text-accent">tapi sistem yang menghasilkan leads dari hari pertama.</span>', '<span class="text-accent">but a system that generates leads from day one.</span>'),
      ('<h3 class="why-title">Tracking Lengkap</h3>', '<h3 class="why-title">Full Tracking</h3>'),
      ('pillarLabel="Panduan Lengkap Pembuatan Landing Page"', 'pillarLabel="Complete Landing Page Guide"'),
    ],
    lines=[
      ('Paket promo khusus untuk Anda',
       'A special bundle for anyone who wants customers straight from the internet: 1 professional landing page + 1 month of Google Ads. We build the page, write the copy and run the ads \u2014 you just receive the leads.'),
      ('Paket ini dirancang untuk satu outcome',
       'This bundle is designed for one specific outcome: leads arriving in your WhatsApp or inbox. A conversion-focused landing page, proven copy, plus Google Ads targeted with keyword research. No technical setup headaches \u2014 our team handles everything.'),
      ('<p class="why-desc">Landing page dioptimasi untuk kecepatan',
       '<p class="why-desc">The landing page is optimised for speed and conversion. Proven copywriting, clear CTAs and a simple form for visitors ready to talk.</p>'),
      ('<p class="why-desc">Google Ads menjangkau orang yang sedang aktif',
       '<p class="why-desc">Google Ads reaches people actively searching \u2014 intent is already high. We research keywords and set targeting relevant to your business.</p>'),
      ('<p class="why-desc">Conversion tracking ter-setup',
       '<p class="why-desc">Conversion tracking is set up from day one. You can see exactly which keywords generate leads, and what each lead costs.</p>'),
      ('Bukan sekadar landing page dan iklan. Kami bangun sistem',
       'Not just a landing page and ads. We build a system that generates leads from day one \u2014 so every click becomes a potential new customer.'),
    ]),
 'digital-marketing-agency': dict(
    title='Digital Marketing Agency Malaysia | Multi-Channel Growth \u2014 Beriklan',
    desc='Multi-channel digital marketing: Facebook, Instagram, Google, TikTok, YouTube ads and landing pages, integrated for measurable growth. growth audit to start.',
    price_range='Custom', service_type='Digital Marketing',
    wa='Hi%20Beriklan%2C%20I%27m%20interested%20in%20your%20digital%20marketing%20services.%20Please%20share%20packages%20and%20pricing.',
    pairs=[
      ('Jasa Digital Marketing · Multi-Channel · Bandung', 'Digital Marketing Agency · Multi-Channel · Malaysia'),
      ('>Jasa Digital Marketing</span>', '>Digital Marketing<'+'/span>'),
      ('>Meningkatkan Bisnis Anda<', '>That Grows Your Business<'),
      ('>Lewat Saluran yang Tepat.<', '>Through the Right Channels.<'),
      ('Kenapa Pendekatan Kami', 'Why Our Approach'),
      ('Bukan sekadar menayangkan iklan di banyak tempat,<br/>', 'Not just running ads everywhere,<br/>'),
      ('<span class="text-accent">tapi mengintegrasikan kanal untuk hasil yang optimal.</span>', '<span class="text-accent">but integrating channels for optimal results.</span>'),
      ('<h3 class="why-title">Laporan Terpadu</h3>', '<h3 class="why-title">Unified Reporting</h3>'),
      ('pillarLabel="Panduan Lengkap Digital Marketing"', 'pillarLabel="Complete Digital Marketing Guide"'),
    ],
    lines=[
      ('Kami mengelola iklan Facebook, Instagram, Google',
       'We manage Facebook, Instagram, Google, TikTok and YouTube ads plus landing pages to bring in new customers, measurably. Every ringgit you invest is monitored closely, with reports you can actually understand.'),
      ('Digital marketing bukan hanya soal pasang iklan',
       'Digital marketing is not just about running ads on many platforms. What matters more is integrating every channel so they reinforce each other: Facebook Ads for awareness, Google Ads for high intent, landing pages for conversion, and so on. Our team manages that integration end-to-end.'),
      ('<p class="why-desc">Setiap kanal punya peran spesifik',
       '<p class="why-desc">Every channel has a specific role in the funnel. We manage the integration so the audience journey from awareness to conversion feels seamless.</p>'),
      ('<p class="why-desc">Laporan lintas kanal dalam satu dokumen',
       '<p class="why-desc">Cross-channel reporting in a single document: which channels perform, which need iteration, and how they contribute to each other.</p>'),
      ('<p class="why-desc">Tidak perlu koordinasikan banyak agency',
       '<p class="why-desc">No juggling multiple agencies. Our team has a specialist for every channel \u2014 all integrated in a single workflow.</p>'),
      ('Bukan sekadar pasang iklan di banyak platform.',
       'More than running ads on many platforms. We build a strategy that integrates every channel for optimal results \u2014 so your digital marketing investment produces measurable business growth.'),
    ]),
}


def line_replace(text, prefix, new_stripped):
    """Replace whole line(s) whose stripped content starts with prefix."""
    lines = text.split('\n')
    hit = 0
    for i, l in enumerate(lines):
        if l.strip().startswith(prefix):
            indent = l[:len(l) - len(l.lstrip())]
            lines[i] = indent + new_stripped
            hit += 1
    return '\n'.join(lines), hit


def main():
    total = 0
    for slug, cfg in CFG.items():
        svc = BYSLUG[slug]
        fp = PAGES + slug + '.astro'
        s = open(fp, encoding='utf-8').read()

        # waLink
        s, n = re.subn(r'const waLink = "https://wa\.me/\d+\?text=[^"]*";',
                       'const waLink = "https://wa.me/62811919328?text=%s";' % cfg['wa'], s, count=1)
        if n != 1: print('[%s] FATAL waLink' % slug); sys.exit(1)

        # tiers + faqs wholesale
        s, n = re.subn(r'const tiers = \[.*?\n\];', js_tiers(svc), s, count=1, flags=re.S)
        if n != 1: print('[%s] FATAL tiers' % slug); sys.exit(1)
        s, n = re.subn(r'const faqs = \[.*?\n\];', js_faqs(svc), s, count=1, flags=re.S)
        if n != 1: print('[%s] FATAL faqs' % slug); sys.exit(1)

        # Layout block (up to line of >>)
        s, n = re.subn(r'<Layout\b.*?\n>+\n', layout_block(cfg, svc), s, count=1, flags=re.S)
        if n != 1: print('[%s] FATAL layout' % slug); sys.exit(1)

        # PricingCards columns -> number of tiers
        s = re.sub(r'(<PricingCards[^\n]*?columns=\{)\d+(\})', r'\g<1>%d\g<2>' % len(svc['tiers']), s)

        # exact pairs
        for a, b in cfg['pairs']:
            if a in s:
                s = s.replace(a, b); total += 1
            else:
                print('[%s] MISS pair: %s' % (slug, a[:70]))

        # line-prefix replacements
        for prefix, new in cfg['lines']:
            s, hit = line_replace(s, prefix, new)
            if hit == 0:
                print('[%s] MISS line: %s' % (slug, prefix[:70]))
            total += hit

        # tolerant global pairs
        for a, b in TOLERANT:
            if a in s: s = s.replace(a, b); total += 1

        open(fp, 'w', encoding='utf-8').write(s)
        print('[%s] done' % slug)
    print('ALL DONE, %d body hits' % total)


if __name__ == '__main__':
    main()
