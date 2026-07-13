<script>
    import { onMount, onDestroy } from 'svelte';
    import { Play, Volume2, Settings, Maximize, Eye, ThumbsUp, Clock } from 'lucide-svelte';

    let mounted = false;
    let countdown = 6;
    let interval;
    let views = 0;
    let watchTime = 0;

    onMount(() => {
        mounted = true;
        // Countdown timer
        interval = setInterval(() => {
            if (countdown > 0) countdown--;
        }, 1000);

        // Animated counters
        const start = performance.now();
        function tick(now) {
            const t = Math.min((now - start) / 2200, 1);
            const ease = 1 - Math.pow(1 - t, 3);
            views = Math.round(45000 * ease);
            watchTime = Math.round(28 * ease);
            if (t < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    });

    onDestroy(() => {
        if (interval) clearInterval(interval);
    });

    function formatNumber(n) {
        if (n >= 1000) return (n / 1000).toFixed(1).replace('.0', '') + 'K';
        return n.toLocaleString('id-ID');
    }
</script>

<div class="relative w-full max-w-lg mx-auto {mounted ? 'is-mounted' : ''}">
    <!-- Glow backdrop -->
    <div class="absolute -inset-10 pointer-events-none" aria-hidden="true">
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[480px] h-[480px] bg-gradient-to-br from-red-500/15 via-accent/12 to-pink-500/10 rounded-full" style="filter: blur(48px);"></div>
    </div>

    <!-- Player card -->
    <div class="hv-card relative bg-white rounded-2xl shadow-pop border border-gray-100 overflow-hidden">
        <!-- Window chrome -->
        <div class="flex items-center gap-1.5 px-4 py-2.5 bg-soft border-b border-gray-100">
            <span class="w-2.5 h-2.5 rounded-full bg-red-400"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-yellow-400"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-green-400"></span>
            <span class="ml-3 text-[10px] font-mono text-muted flex items-center gap-1.5">
                <svg class="w-3 h-3 text-red-600" fill="currentColor" viewBox="0 0 24 24"><path d="M21.582 6.186a2.506 2.506 0 00-1.768-1.768C18.254 4 12 4 12 4s-6.254 0-7.814.418a2.506 2.506 0 00-1.768 1.768C2 7.746 2 12 2 12s0 4.254.418 5.814a2.506 2.506 0 001.768 1.768C5.746 20 12 20 12 20s6.254 0 7.814-.418a2.506 2.506 0 001.768-1.768C22 16.254 22 12 22 12s0-4.254-.418-5.814zM10 15.464V8.536L16 12l-6 3.464z"/></svg>
                youtube.com/watch
            </span>
            <span class="ml-auto px-2 py-0.5 bg-red-600 text-white text-[9px] font-bold rounded">AD</span>
        </div>

        <!-- Video area -->
        <div class="relative aspect-video bg-gradient-to-br from-amber-200 via-orange-300 to-red-300 overflow-hidden">
            <!-- Pattern overlay -->
            <div class="absolute inset-0 bg-grid opacity-30"></div>

            <!-- Countdown timer (bumper) -->
            {#if countdown > 0}
                <div class="absolute top-3 right-3 px-3 py-1 bg-black/70 backdrop-blur-sm rounded-full flex items-center gap-1.5">
                    <Clock class="w-3 h-3 text-white" />
                    <span class="text-xs font-bold text-white">{countdown}s</span>
                </div>
            {/if}

            <!-- Skip button -->
            <button class="absolute bottom-3 right-3 px-3 py-1.5 bg-black/80 backdrop-blur-sm rounded text-[10px] font-bold text-white hover:bg-black transition-colors">
                Lewati iklan →
            </button>

            <!-- Center play -->
            <div class="absolute inset-0 flex items-center justify-center">
                <div class="w-16 h-16 rounded-full bg-white/90 backdrop-blur-sm flex items-center justify-center shadow-2xl anim-float">
                    <Play class="w-7 h-7 text-ink ml-1" fill="currentColor" />
                </div>
            </div>

            <!-- Bottom progress bar -->
            <div class="absolute bottom-0 left-0 right-0 h-1 bg-black/30">
                <div class="h-full bg-red-600 rounded-r" style="width: {Math.max(0, 100 - countdown * 16)}%; transition: width 1s linear;"></div>
            </div>

            <!-- Ad label -->
            <div class="absolute top-3 left-3 px-2 py-1 bg-black/70 backdrop-blur-sm rounded text-[9px] font-bold text-white uppercase tracking-wider">
                Iklan · 6 detik
            </div>
        </div>

        <!-- Video info -->
        <div class="p-4 space-y-3">
            <div>
                <h3 class="font-display font-bold text-base text-ink leading-tight">Skincare Lokal yang Bikin Kulit Cerah dalam 7 Hari</h3>
                <div class="flex items-center gap-3 mt-1.5 text-[11px] text-muted">
                    <span>Brand Beauty Official</span>
                    <span>·</span>
                    <span class="flex items-center gap-1"><Eye class="w-3 h-3" /> {formatNumber(views)} views</span>
                    <span>·</span>
                    <span>2 hari lalu</span>
                </div>
            </div>
            <div class="flex items-center gap-2">
                <button class="flex items-center gap-1.5 px-3 py-1.5 bg-soft hover:bg-ink hover:text-white rounded-full text-xs font-bold transition-colors">
                    <ThumbsUp class="w-3.5 h-3.5" /> 2,4K
                </button>
                <button class="px-3 py-1.5 bg-soft hover:bg-ink hover:text-white rounded-full text-xs font-bold transition-colors">
                    Bagikan
                </button>
                <button class="ml-auto w-8 h-8 rounded-full bg-soft hover:bg-ink hover:text-white flex items-center justify-center transition-colors">
                    <Settings class="w-3.5 h-3.5" />
                </button>
            </div>
        </div>
    </div>

    <!-- FLOATING: Views count -->
    <div class="hv-float-1 absolute -left-2 md:-left-12 top-20 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-52 hidden md:block">
        <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center">
                <Eye class="w-4 h-4 text-red-600" />
            </div>
            <div>
                <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Estimasi Tayangan</p>
                <p class="text-base font-display font-extrabold text-ink leading-tight">35K–75K</p>
            </div>
        </div>
    </div>

    <!-- FLOATING: Watch time -->
    <div class="hv-float-2 absolute -right-2 md:-right-12 top-8 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-44 hidden md:block">
        <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Rata-rata Watch Time</p>
        <p class="text-2xl font-display font-extrabold text-ink mt-1">{watchTime}<span class="text-sm text-muted">s</span></p>
        <div class="mt-2 h-1.5 bg-soft rounded-full overflow-hidden">
            <div class="h-full bg-gradient-to-r from-red-500 to-orange-500 rounded-full" style="width: {Math.min((watchTime / 30) * 100, 95)}%; transition: width 0.4s ease;"></div>
        </div>
    </div>

    <!-- FLOATING: TrueView badge -->
    <div class="hv-float-3 absolute -right-2 md:-right-10 bottom-16 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-48 hidden lg:flex items-center gap-2">
        <div class="w-9 h-9 rounded-full bg-red-100 flex items-center justify-center shrink-0">
            <Play class="w-4 h-4 text-red-600" fill="currentColor" />
        </div>
        <div class="min-w-0">
            <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Format</p>
            <p class="text-base font-display font-extrabold text-ink leading-tight">Skippable</p>
        </div>
        <span class="live-dot relative w-1.5 h-1.5 rounded-full bg-red-500 ml-auto anim-pulse"></span>
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

    .anim-float { animation: floatY 7s ease-in-out infinite; }
    @keyframes floatY {
        0%, 100% { transform: translateY(0) rotate(0); }
        50% { transform: translateY(-12px) rotate(3deg); }
    }

    .hv-float-1 { animation: floatNotif 6s ease-in-out infinite 0.3s; }
    .hv-float-2 { animation: floatNotif 6s ease-in-out infinite 1.3s; }
    .hv-float-3 { animation: floatNotif 6s ease-in-out infinite 2.1s; }
    @keyframes floatNotif {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }

    .bg-grid {
        background-image: radial-gradient(circle at 1px 1px, rgba(15,30,61,0.08) 1px, transparent 0);
        background-size: 16px 16px;
    }

    @media (prefers-reduced-motion: reduce) {
        .hv-card, .is-mounted .hv-card { animation: none; opacity: 1; transform: none; }
        .hv-float-1, .hv-float-2, .hv-float-3, .anim-float, .anim-pulse, .live-dot::after { animation: none; }
    }
</style>
