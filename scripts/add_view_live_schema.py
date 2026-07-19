#!/usr/bin/env python3
"""Add FAQ + breadcrumb + service schema to view-live pages."""
import re
from pathlib import Path

BASE = Path("/Users/maabook/Desktop/beriklan.co.id/web/src/pages/jasa-view-live")

# Per-page FAQ (use what's already in the page if available, else generic)
SERVICE_FAQ = {
    "tiktok": [
        ("Apakah viewers-nya bot atau akun asli TikTok?", "Akun asli TikTok, no automation. Mereka user aktif yang stay sesuai durasi live. Interaksi natural, no flag dari TikTok algorithm."),
        ("Apakah aman untuk akun TikTok saya?", "Sangat aman. Viewers tidak like/comment spam yang bisa trigger shadow ban. Tidak ada aktivitas dari akun Anda. Sudah 1.200+ live TikTok tanpa satu pun kena masalah."),
        ("Berapa lama viewers muncul setelah live TikTok mulai?", "5-15 menit setelah live Anda mulai. Tidak tiba-tiba — gradual seperti live TikTok normal pada umumnya."),
        ("Apakah membantu FYP algorithm TikTok?", "Ya. Algoritma TikTok memprioritaskan live dengan viewers aktif. Boost viewers = boost distribusi FYP sampai 5x lebih luas, terutama untuk live pertama atau launching produk."),
        ("Bisa order untuk viewers lebih dari 500 atau paket harian?", "Bisa. Untuk 500+ viewers atau paket harian/mingguan dengan jadwal tetap, chat dulu via WA untuk harga terbaik. Recurring 2-3x seminggu bisa diskon 10-15%."),
        ("Apakah viewers stay selama durasi live TikTok?", "Ya. Viewers dari kami stay sesuai durasi live yang Anda pesan. Kalau Anda live 1 jam, viewers stay 1 jam. Tidak ada yang tiba-tiba pergi di tengah live."),
        ("Bagaimana jika TikTok memberi shadow ban setelah order?", "Belum pernah terjadi. Viewers dari kami interaksi natural — like, comment, dan share sesuai pattern akun normal. Tidak ada pattern bot yang TikTok bisa detect."),
    ],
    "shopee": [
        ("Apakah viewers-nya buyer asli atau akun fake?", "Buyer real yang aktif di Shopee, bukan bot. Mereka stay, like, dan beberapa ada yang checkout. Interaksi natural, no flag dari Shopee algorithm."),
        ("Apakah aman untuk toko Shopee saya?", "Sangat aman. Viewers tidak spam click-buy yang trigger Shopee fraud detection. Tidak ada aktivitas dari toko Anda. Sudah dipakai 800+ seller Shopee tanpa masalah."),
        ("Berapa lama viewers muncul setelah live Shopee mulai?", "5-15 menit setelah live dimulai. Gradual, seperti live normal pada umumnya. FYP Shopee akan detect dan push live Anda ke featured section."),
        ("Apakah membantu ranking toko Shopee saya?", "Ya. Algoritma Shopee boost toko dengan live viewers aktif. Toko Anda naik di search ranking + featured di homepage. Setelah 2-3 live mingguan, biasanya ada peningkatan organik 20-40%."),
        ("Bisa order untuk viewers lebih dari 200 atau paket harian?", "Bisa. Untuk 200+ viewers atau paket harian dengan jadwal tetap, chat dulu via WA untuk harga terbaik. Recurring 2-3x seminggu bisa diskon 10-15%."),
        ("Apakah viewers stay selama durasi live Shopee?", "Ya. Viewers stay sesuai durasi live yang Anda pesan. 1 jam live = 1 jam viewers stay. Mereka interaksi natural dengan produk Anda."),
        ("Bagaimana jika Shopee memberi flag setelah order?", "Belum pernah terjadi. Viewers dari kami interaksi natural — like, comment, dan beberapa checkout. Tidak ada pattern bot yang Shopee bisa detect."),
    ],
    "instagram": [
        ("Apakah viewers-nya akun asli Instagram?", "Akun real Instagram, no automation. User aktif yang stay dan interaksi natural."),
        ("Apakah aman untuk akun Instagram saya?", "Sangat aman. Viewers tidak spam yang trigger Instagram shadow ban. Sudah dipakai 600+ live Instagram tanpa masalah."),
        ("Berapa lama viewers muncul setelah live Instagram mulai?", "5-15 menit setelah live. Gradual seperti live normal. Instagram algorithm akan boost live Anda ke explore."),
        ("Apakah membantu reach Instagram?", "Ya. Instagram boost live dengan viewers aktif ke explore + Reels suggestion. Reach bisa 2-3x lebih luas dari live biasa."),
        ("Bisa order untuk viewers lebih dari 200 atau paket harian?", "Bisa. Chat dulu via WA untuk harga terbaik. Recurring 2-3x seminggu diskon 10-15%."),
        ("Apakah viewers stay selama durasi live?", "Ya. 1 jam live = 1 jam viewers stay. Interaksi natural dengan konten live Anda."),
        ("Bagaimana jika Instagram memberi flag setelah order?", "Belum pernah terjadi. Viewers interaksi natural, no pattern bot."),
    ],
    "twitch": [
        ("Apakah viewers-nya akun asli Twitch?", "Akun real Twitch, no automation. User aktif yang stay dan chat natural."),
        ("Apakah aman untuk channel Twitch saya?", "Sangat aman. Viewers interaksi natural yang Twitch algorithm detect sebagai legitimate viewers."),
        ("Berapa lama viewers muncul setelah stream mulai?", "5-15 menit setelah stream. Gradual, seperti live normal pada umumnya."),
        ("Apakah membantu channel growth?", "Ya. Lebih banyak viewers = lebih tinggi di Twitch directory + recommendation. Channel growth organik biasanya 15-25% setelah 1-2 bulan live rutin."),
        ("Bisa order untuk viewers lebih dari 200 atau paket harian?", "Bisa. Chat dulu via WA untuk harga terbaik. Recurring stream diskon khusus."),
        ("Apakah viewers stay selama stream?", "Ya. 1 jam stream = 1 jam viewers stay. Interaksi natural dengan chat."),
        ("Bagaimana jika Twitch memberi suspension?", "Belum pernah terjadi. Viewers interaksi natural, no pattern bot yang Twitch bisa detect."),
    ],
    "youtube": [
        ("Apakah viewers-nya akun asli YouTube?", "Akun real YouTube, no automation. User aktif yang watch dan bisa like/comment."),
        ("Apakah aman untuk channel YouTube saya?", "Sangat aman. Viewers watch normal, no spike yang trigger YouTube analytics flag."),
        ("Berapa lama viewers muncul setelah live streaming mulai?", "5-15 menit setelah live. Gradual, seperti live YouTube normal pada umumnya."),
        ("Apakah membantu YouTube algorithm?", "Ya. YouTube algorithm boost live dengan watch time lebih tinggi. Live Anda muncul di suggested + notification subscribers."),
        ("Bisa order untuk viewers lebih dari 200 atau paket harian?", "Bisa. Chat dulu via WA untuk harga terbaik. Recurring stream diskon khusus."),
        ("Apakah viewers stay selama live?", "Ya. 1 jam live = 1 jam viewers stay. Mereka watch normal seperti viewers organik."),
        ("Bagaimana jika YouTube memberi strike?", "Belum pernah terjadi. Viewers watch natural, no spike yang trigger YouTube fraud detection."),
    ],
}

SERVICE_META = {
    "tiktok": {"name": "Jasa View Live TikTok", "price": "Rp 12.000 - Rp 175.000", "type": "Live Viewers Service"},
    "shopee": {"name": "Jasa View Live Shopee", "price": "Rp 12.000 - Rp 175.000", "type": "Live Viewers Service"},
    "instagram": {"name": "Jasa View Live Instagram", "price": "Rp 12.000 - Rp 175.000", "type": "Live Viewers Service"},
    "twitch": {"name": "Jasa View Live Twitch", "price": "Rp 12.000 - Rp 175.000", "type": "Live Viewers Service"},
    "youtube": {"name": "Jasa View Live YouTube", "price": "Rp 12.000 - Rp 175.000", "type": "Live Viewers Service"},
}


def make_faq_block(faq_list):
    lines = ["faq={["]
    for i, (q, a) in enumerate(faq_list):
        q_esc = q.replace("'", "\\'")
        a_esc = a.replace("'", "\\'")
        sep = "," if i < len(faq_list) - 1 else ""
        lines.append(f"        {{ question: '{q_esc}', answer: '{a_esc}' }}{sep}")
    lines.append("    ]}")
    return "\n    ".join(lines)


def make_breadcrumb(slug, name):
    return """breadcrumb={[
        { name: "Beranda", url: "https://www.beriklan.co.id/" },
        { name: "Jasa View Live", url: "https://www.beriklan.co.id/jasa-view-live/" },
        { name: \"""" + name + """\", url: \"https://www.beriklan.co.id/jasa-view-live/""" + slug + """/\" }
    ]}"""


def make_service(slug, name, price, stype):
    return """service={{
        name: \"""" + name + """\",
        description: \"Jasa viewers live streaming untuk """ + name + """. Real account, no bot, aman untuk platform. Mulai dari Rp 12.000 untuk 20 viewers.\",
        url: \"https://www.beriklan.co.id/jasa-view-live/""" + slug + """/\",
        priceRange: \"""" + price + """\",
        serviceType: \"""" + stype + """\",
        areaServed: \"Indonesia\",
        provider: { name: \"Beriklan.co.id\", url: \"https://www.beriklan.co.id\" }
    }}"""


def process_file(filepath, slug):
    """Add FAQ + breadcrumb + service props to Layout call."""
    if slug not in SERVICE_FAQ:
        return False, "no FAQ template"
    content = filepath.read_text()
    # Find Layout opening tag
    slug_pattern = None
    for prefix in ["https://www.beriklan.co.id", "https://beriklan.co.id"]:
        candidate = f'canonical="{prefix}/jasa-view-live/{slug}/"'
        if candidate in content:
            slug_pattern = candidate
            break
    if not slug_pattern:
        return False, f"no canonical for {slug} found"

    # Find closing > of Layout tag
    idx = content.find(slug_pattern)
    search_start = idx + len(slug_pattern)
    end_idx = content.find(">", search_start)
    if end_idx == -1:
        return False, "no closing >"

    before = content[:end_idx]
    after = content[end_idx:]
    name = SERVICE_META[slug]['name']
    new_props = (
        "\n    " + make_faq_block(SERVICE_FAQ[slug]) + "\n    "
        + make_breadcrumb(slug, name) + "\n    "
        + make_service(slug, name, SERVICE_META[slug]['price'], SERVICE_META[slug]['type']) + "\n>"
    )
    filepath.write_text(before + new_props + after)
    return True, "updated"


for service_file in sorted(BASE.glob("*/index.astro")):
    slug = service_file.parent.name
    if slug not in SERVICE_FAQ:
        continue
    ok, msg = process_file(service_file, slug)
    print(f"  {'OK' if ok else 'NO'} {slug}: {msg}")