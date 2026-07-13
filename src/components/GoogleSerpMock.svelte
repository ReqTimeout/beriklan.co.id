<script>
    import { onMount } from 'svelte';
    import { Search, MapPin, Phone, Star, Sparkles } from 'lucide-svelte';

    let mounted = false;
    let displayedQuery = '';
    let typingIdx = 0;
    const fullQuery = 'klinik gigi terbaik bandung';
    let visibleResults = 0;
    let positionTicker = 0;

    onMount(() => {
        mounted = true;

        // Typewriter effect on query
        const typeInterval = setInterval(() => {
            if (typingIdx < fullQuery.length) {
                displayedQuery = fullQuery.slice(0, typingIdx + 1);
                typingIdx++;
            } else {
                clearInterval(typeInterval);
            }
        }, 120);

        // Reveal ads sequentially
        const revealTimer = setTimeout(() => {
            const reveal = () => {
                if (visibleResults < 3) {
                    visibleResults++;
                    setTimeout(reveal, 700);
                }
            };
            reveal();
        }, 1500);

        // Position ticker
        const posTimer = setInterval(() => {
            positionTicker = Math.min(positionTicker + 1, 3);
        }, 600);

        return () => {
            clearInterval(typeInterval);
            clearTimeout(revealTimer);
            clearInterval(posTimer);
        };
    });
</script>

<div class="relative w-full max-w-lg mx-auto {mounted ? 'is-mounted' : ''}">
    <!-- Glow backdrop -->
    <div class="absolute -inset-10 pointer-events-none" aria-hidden="true">
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[480px] h-[480px] bg-gradient-to-br from-blue-500/15 via-teal/12 to-accent/12 rounded-full" style="filter: blur(48px);"></div>
    </div>

    <!-- Browser window -->
    <div class="hv-card relative bg-white rounded-2xl shadow-pop border border-gray-100 overflow-hidden">
        <!-- Browser chrome -->
        <div class="flex items-center gap-1.5 px-4 py-2.5 bg-soft border-b border-gray-100">
            <span class="w-2.5 h-2.5 rounded-full bg-red-400"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-yellow-400"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-green-400"></span>
            <div class="ml-3 flex-1 bg-white rounded-md px-3 py-1 text-[10px] text-muted flex items-center gap-1.5 border border-gray-200">
                <svg class="w-3 h-3 text-green" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 1a4 4 0 00-4 4v3H5a3 3 0 00-3 3v7a3 3 0 003 3h10a3 3 0 003-3v-7a3 3 0 00-3-3h-1V5a4 4 0 00-4-4zm2 7V5a2 2 0 10-4 0v3h4z" clip-rule="evenodd"/></svg>
                <span class="font-mono">google.com/search</span>
            </div>
            <span class="ml-auto flex items-center gap-1 text-[9px] text-green font-bold">
                <span class="live-dot relative w-1.5 h-1.5 rounded-full bg-green"></span>
                LIVE
            </span>
        </div>

        <!-- Google search bar -->
        <div class="px-4 pt-4 pb-2 border-b border-gray-100">
            <div class="flex items-center gap-2 bg-soft rounded-full px-4 py-2.5 border border-gray-200 focus-within:border-blue-400 transition-colors">
                <Search class="w-4 h-4 text-muted shrink-0" />
                <span class="text-sm text-ink flex-1 truncate">{displayedQuery}<span class="cursor-blink">|</span></span>
                <button class="text-[9px] font-bold text-blue-600 hover:text-blue-700">CARI</button>
            </div>
        </div>

        <!-- Results area -->
        <div class="p-4 md:p-5 space-y-3 min-h-[280px]">
            <p class="text-[10px] text-muted">Sekitar 1.230.000 hasil (0,42 detik)</p>

            <!-- Ads block -->
            {#if visibleResults >= 1}
                <div class="ad-result">
                    <div class="flex items-start gap-1.5 mb-1">
                        <span class="ad-badge">Iklan</span>
                        <span class="text-[9px] text-muted">ads.google.com</span>
                    </div>
                    <h3 class="ad-title">Klinik Gigi Bandung · Rating 4.8 · Booking Online 24 Jam</h3>
                    <p class="ad-url">klinikgigibandung.id/booking</p>
                    <p class="ad-desc">Dokter gigi berpengalaman 12 tahun. Perawatan saluran akar, behel, veneer, dan scaling. Konsultasi pertama GRATIS. Lokasi strategis di Bandung.</p>
                    <div class="flex items-center gap-3 mt-1.5 text-[10px]">
                        <span class="flex items-center gap-1 text-accent">
                            <Star class="w-3 h-3 fill-current" />
                            <Star class="w-3 h-3 fill-current" />
                            <Star class="w-3 h-3 fill-current" />
                            <Star class="w-3 h-3 fill-current" />
                            <Star class="w-3 h-3 fill-current" />
                            <span class="text-ink font-bold ml-0.5">4.8</span>
                        </span>
                        <span class="flex items-center gap-1 text-muted"><Phone class="w-2.5 h-2.5" /> +62 22-...</span>
                        <span class="flex items-center gap-1 text-muted"><MapPin class="w-2.5 h-2.5" /> 0,8 km</span>
                    </div>
                </div>
            {/if}

            {#if visibleResults >= 2}
                <div class="ad-result" style="animation-delay: 100ms;">
                    <div class="flex items-start gap-1.5 mb-1">
                        <span class="ad-badge">Iklan</span>
                        <span class="text-[9px] text-muted">klinikgigi-bdg.com</span>
                    </div>
                    <h3 class="ad-title">Promo Scaling Gigi Hanya Rp 199rb · Klinik Gigi Berstandar</h3>
                    <p class="ad-url">klinikgigi-bdg.com/promo</p>
                    <p class="ad-desc">Diskon 60% untuk scaling + konsultasi gratis. Dokter profesional dengan alat modern. Booking via WhatsApp hari ini.</p>
                </div>
            {/if}

            {#if visibleResults >= 3}
                <div class="ad-result" style="animation-delay: 200ms;">
                    <div class="flex items-start gap-1.5 mb-1">
                        <span class="ad-badge">Iklan</span>
                        <span class="text-[9px] text-muted">dokterspesialis-gigi.id</span>
                    </div>
                    <h3 class="ad-title">Behel Gigi Premium · Cicilan 0% · 24 Cabang di Indonesia</h3>
                    <p class="ad-url">dokterspesialis-gigi.id/behel</p>
                    <p class="ad-desc">Konsultasi gratis untuk pasang behel. Hasil terukur dengan teknologi 3D scan. Lokasi strategis di pusat kota Bandung.</p>
                </div>
            {/if}
        </div>
    </div>

    <!-- FLOATING: Position rank -->
    <div class="hv-float-1 absolute -left-2 md:-left-12 top-20 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-52 hidden md:block">
        <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Posisi Rata-rata</p>
        <p class="text-2xl font-display font-extrabold text-ink mt-1">#{positionTicker}<span class="text-sm text-muted">–#2</span></p>
        <p class="text-[10px] text-muted mt-0.5">di halaman pertama Google</p>
        <div class="mt-2 h-1.5 bg-soft rounded-full overflow-hidden">
            <div class="h-full bg-gradient-to-r from-blue-500 via-teal to-green rounded-full" style="width: {Math.min((positionTicker / 3) * 100, 95)}%; transition: width 0.4s ease;"></div>
        </div>
    </div>

    <!-- FLOATING: Keywords count -->
    <div class="hv-float-2 absolute -right-2 md:-right-12 top-8 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-44 hidden md:block">
        <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                <Sparkles class="w-4 h-4 text-blue-600" />
            </div>
            <div>
                <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Kata Kunci</p>
                <p class="text-base font-display font-extrabold text-ink leading-tight">15–20<span class="text-[9px] text-muted font-bold ml-1">aktif</span></p>
            </div>
        </div>
    </div>

    <!-- FLOATING: Search count -->
    <div class="hv-float-3 absolute -right-2 md:-right-10 bottom-16 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-48 hidden lg:flex items-center gap-2">
        <div class="w-9 h-9 rounded-full bg-teal/15 flex items-center justify-center shrink-0">
            <Search class="w-4 h-4 text-teal" />
        </div>
        <div class="min-w-0">
            <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Pencarian/Bulan</p>
            <p class="text-base font-display font-extrabold text-ink leading-tight">1.2K<span class="text-xs text-muted font-bold ml-0.5">search</span></p>
        </div>
        <span class="live-dot relative w-1.5 h-1.5 rounded-full bg-teal ml-auto anim-pulse"></span>
    </div>
</div>

<style>
    .hv-card { opacity: 0; transform: translateY(20px); }
    .is-mounted .hv-card { animation: cardIn 0.7s cubic-bezier(0.22, 1, 0.36, 1) forwards; }
    @keyframes cardIn { to { opacity: 1; transform: translateY(0); } }

    .live-dot::after {
        content: ''; position: absolute; inset: 0; border-radius: 9999px;
        background: currentColor;
        animation: ping 1.5s ease-out infinite;
    }
    @keyframes ping {
        0% { transform: scale(1); opacity: 0.7; }
        80%, 100% { transform: scale(2.4); opacity: 0; }
    }

    .anim-pulse { animation: pulse 2s ease-in-out infinite; }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(1.15); }
    }

    .cursor-blink { animation: blink 1s steps(2) infinite; }
    @keyframes blink {
        50% { opacity: 0; }
    }

    .ad-result {
        padding: 0.6rem 0;
        border-bottom: 1px solid #f1f3f8;
        opacity: 0;
        transform: translateY(8px);
        animation: adIn 0.5s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    }
    .ad-result:last-child { border-bottom: none; }
    @keyframes adIn { to { opacity: 1; transform: translateY(0); } }

    .ad-badge {
        background: #fef3c7;
        color: #92400e;
        font-size: 9px;
        font-weight: 700;
        padding: 1px 6px;
        border-radius: 3px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .ad-title {
        font-size: 14px;
        font-weight: 600;
        color: #1a0dab;
        line-height: 1.3;
        margin: 2px 0;
    }
    .ad-result:hover .ad-title { text-decoration: underline; }

    .ad-url {
        font-size: 10px;
        color: #006621;
        line-height: 1;
        margin-bottom: 3px;
    }

    .ad-desc {
        font-size: 11px;
        color: #4d5156;
        line-height: 1.45;
    }

    .hv-float-1 { animation: floatNotif 6s ease-in-out infinite 0.4s; }
    .hv-float-2 { animation: floatNotif 6s ease-in-out infinite 1.4s; }
    .hv-float-3 { animation: floatNotif 6s ease-in-out infinite 2.2s; }
    @keyframes floatNotif {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }

    @media (prefers-reduced-motion: reduce) {
        .hv-card, .is-mounted .hv-card { animation: none; opacity: 1; transform: none; }
        .hv-float-1, .hv-float-2, .hv-float-3, .anim-pulse, .live-dot::after, .cursor-blink { animation: none; }
        .ad-result { animation: none; opacity: 1; transform: none; }
    }
</style>
