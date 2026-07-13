<script>
    import { slide } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';

    const faqs = [
        {
            q: 'Berapa minimum anggaran untuk memulai?',
            a: 'Minimum Rp 500.000 per bulan untuk ad spend, ditambah biaya jasa sesuai paket yang dipilih. Angka ini memadai untuk membaca data awal dalam 2–4 minggu. Untuk hasil yang lebih stabil dan berkelanjutan, kami umumnya merekomendasikan mulai dari Rp 3–5 juta per bulan.'
        },
        {
            q: 'Berapa lama hingga hasil mulai terlihat?',
            a: 'Secara realistis: 2–4 minggu untuk membaca data awal, 1–3 bulan untuk menemukan pola yang stabil. Durasi bervariasi tergantung industri, platform, dan besaran anggaran. Kami tidak menjanjikan hasil instan — yang menjadi komitmen kami: optimasi konsisten berbasis data nyata, bukan asumsi.'
        },
        {
            q: 'Apa bedanya dengan agency lain?',
            a: 'Tiga hal: (1) Anda pegang akun Meta/Google/TikTok — kami hanya yang manage; (2) laporan bahasa yang mudah dipahami, bukan jargon CPM-CTR-CPC tanpa konteks; (3) tidak ada lock 6-12 bulan — bulanan saja, Anda bebas pindah kapan saja.'
        },
        {
            q: 'Perlu siapkan apa saja?',
            a: 'Cukup business profile singkat Anda + akses ke akun iklan (kalau sudah ada). Kalau belum ada, kami setup dari nol — Meta Pixel, Google Tag, TikTok Pixel, semuanya diurus.'
        },
        {
            q: 'Apakah paket dapat disesuaikan?',
            a: 'Ya, dapat disesuaikan. Rekomendasi kami umumnya disusun berdasarkan besaran anggaran iklan dan objective utama — apakah untuk membangun branding atau mengarahkan pada konversi. Untuk kebutuhan yang tidak lazim, kami akan berdiskusi secara personal terlebih dahulu, tanpa biaya.'
        },
        {
            q: 'Berapa lama dari konsultasi pertama sampai iklan tayang?',
            a: 'Rata-rata 7–14 hari setelah brief Anda kami terima. Termasuk persiapan akun iklan, materi iklan (foto, video, copy), dan pixel tracking. Untuk paket yang materinya sudah siap, biasanya lebih cepat.'
        },
        {
            q: 'Bagaimana jika hasil tidak sesuai target?',
            a: 'Kami melakukan evaluasi terbuka pada bulan kedua dan ketiga. Apabila pendekatan kami terbukti tidak sesuai dengan karakter bisnis Anda, kami akan merekomendasikan pergantian strategi atau pengembalian sebagian biaya. Kasus ini jarang terjadi — namun kami transparan mengenai kemungkinan tersebut sejak awal.'
        },
        {
            q: 'Kenapa tidak kasih guaranteed ROAS?',
            a: 'Karena ROAS tergantung banyak faktor di luar kuasa kami (produk, harga, funnel, landing page). Yang kami jamin: effort maksimal + optimasi berdasarkan data + laporan yang jujur. Bukan sulap.'
        },
    ];

    let openIdx = -1;
    function toggle(i) {
        openIdx = openIdx === i ? -1 : i;
    }
</script>

<div class="reveal-stagger max-w-3xl mx-auto space-y-3">
    {#each faqs as item, i}
        <div class="faq-item bg-white border border-gray-100 rounded-xl overflow-hidden shadow-soft transition-all duration-300 hover:shadow-pop hover:border-accent/30">
            <button
                type="button"
                on:click={() => toggle(i)}
                class="w-full text-left px-6 py-5 flex items-center justify-between gap-4 group"
                aria-expanded={openIdx === i}
            >
                <span class="font-display font-bold text-base md:text-lg text-ink group-hover:text-accent transition-colors leading-snug">
                    {item.q}
                </span>
                <span class="faq-toggle shrink-0 w-8 h-8 rounded-full bg-soft flex items-center justify-center group-hover:bg-accent group-hover:text-ink transition-all">
                    <svg class="w-4 h-4 transition-transform duration-300" class:rotate-45={openIdx === i} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"/>
                    </svg>
                </span>
            </button>
            {#if openIdx === i}
                <div transition:slide={{ duration: 250, easing: quintOut }}>
                    <div class="px-6 pb-5 pt-0 text-muted leading-relaxed text-sm md:text-base border-t border-gray-50">
                        <p class="pt-4">{item.a}</p>
                    </div>
                </div>
            {/if}
        </div>
    {/each}
</div>

<style>
    .faq-item-enter {
        opacity: 0;
        transform: translateY(14px);
        animation: faqIn 0.5s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    }
    @keyframes faqIn {
        to { opacity: 1; transform: translateY(0); }
    }
    @media (prefers-reduced-motion: reduce) {
        .faq-item-enter { animation: none; opacity: 1; transform: none; }
    }
</style>
