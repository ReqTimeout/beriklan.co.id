<script>
    import { onMount } from 'svelte';
    import { Target, MessageCircle, TrendingUp, Users, Sparkles, Heart, Video, Search, BarChart3, CheckCircle2 } from 'lucide-svelte';

    let mounted = false;
    let pulseIndex = 0;
    let leadCount = 0;
    let channels = [
        { id: 1, Icon: Target, label: 'Meta Ads', color: '#1877f2', x: 15, y: 30, leads: 142 },
        { id: 2, Icon: Video, label: 'TikTok Ads', color: '#000', x: 75, y: 30, leads: 98 },
        { id: 3, Icon: Search, label: 'Google Ads', color: '#ea4335', x: 15, y: 65, leads: 124 },
        { id: 4, Icon: Video, label: 'YouTube Ads', color: '#ff0000', x: 75, y: 65, leads: 67 },
    ];

    onMount(() => {
        mounted = true;
        const start = performance.now();
        function tick(now) {
            const t = Math.min((now - start) / 2000, 1);
            const ease = 1 - Math.pow(1 - t, 3);
            leadCount = Math.round(431 * ease);
            if (t < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);

        const pulse = setInterval(() => {
            pulseIndex = (pulseIndex + 1) % channels.length;
        }, 1800);
        return () => clearInterval(pulse);
    });

    function totalLeads() {
        return channels.reduce((sum, c) => sum + c.leads, 0);
    }
</script>

<div class="relative w-full max-w-lg mx-auto aspect-square {mounted ? 'is-mounted' : ''}">
    <!-- Glow backdrop -->
    <div class="absolute -inset-10 pointer-events-none" aria-hidden="true">
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[480px] h-[480px] bg-gradient-to-br from-accent/15 via-teal/12 to-purple-500/10 rounded-full" style="filter: blur(48px);"></div>
    </div>

    <!-- Card -->
    <div class="hv-card relative w-full h-full bg-white rounded-2xl shadow-pop border border-gray-100 overflow-hidden">
        <div class="flex items-center gap-1.5 px-4 py-2.5 bg-soft border-b border-gray-100">
            <span class="w-2.5 h-2.5 rounded-full bg-red-400"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-yellow-400"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-green-400"></span>
            <span class="ml-3 text-[10px] font-mono text-muted flex items-center gap-1.5">
                <BarChart3 class="w-3 h-3" />
                Omnichannel Report · November 2026
            </span>
        </div>

        <!-- Map area -->
        <div class="relative w-full h-[calc(100%-40px)] p-4">
            <!-- Connection lines -->
            <svg class="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 100 100" preserveAspectRatio="none">
                <!-- Lines from each channel to center -->
                {#each channels as ch, i}
                    <line x1={ch.x} y1={ch.y} x2="50" y2="50"
                        stroke={ch.color}
                        stroke-width="0.8"
                        stroke-dasharray="3 2"
                        opacity="0.3"
                        class="conn-line"
                        style="animation: dashFlow 2s linear infinite {i * 0.3}s;"
                    />
                {/each}
            </svg>

            <!-- Center hub -->
            <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20">
                <div class="relative">
                    <div class="w-20 h-20 rounded-full bg-gradient-to-br from-ink via-primary-2 to-ink flex flex-col items-center justify-center shadow-pop">
                        <Sparkles class="w-5 h-5 text-accent" />
                        <p class="text-[8px] font-bold text-white uppercase tracking-wider mt-0.5">Beriklan</p>
                    </div>
                    <!-- Pulse rings -->
                    <span class="absolute inset-0 rounded-full border-2 border-accent/40 pulse-ring"></span>
                    <span class="absolute inset-0 rounded-full border-2 border-accent/30 pulse-ring" style="animation-delay: 1s;"></span>
                </div>
            </div>

            <!-- Channel nodes -->
            {#each channels as ch, i}
                <div class="absolute z-10 channel-node" style="left: {ch.x}%; top: {ch.y}%; transform: translate(-50%, -50%);">
                    <div class="relative">
                        <div class="w-14 h-14 rounded-2xl flex items-center justify-center shadow-lg border-2 border-white" style="background: {ch.color};">
                            <svelte:component this={ch.Icon} size="20" strokeWidth="2.5" color="white" />
                        </div>
                        {#if pulseIndex === i}
                            <span class="absolute inset-0 rounded-2xl border-2 pulse-ring-node" style="border-color: {ch.color};"></span>
                        {/if}
                        <div class="absolute top-full left-1/2 -translate-x-1/2 mt-1.5 px-2 py-0.5 bg-white rounded shadow-md whitespace-nowrap">
                            <p class="text-[9px] font-bold text-ink leading-tight">{ch.label}</p>
                            <p class="text-[8px] text-muted leading-tight">{ch.leads} leads</p>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    </div>

    <!-- FLOATING: Total leads -->
    <div class="hv-float-1 absolute -left-2 md:-left-12 top-12 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-48 hidden md:block">
        <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-accent/15 flex items-center justify-center">
                <Users class="w-4 h-4 text-accent" />
            </div>
            <div>
                <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Total Leads</p>
                <p class="text-base font-display font-extrabold text-ink leading-tight">{leadCount}<span class="text-[9px] text-muted font-bold ml-0.5">/bulan</span></p>
            </div>
        </div>
    </div>

    <!-- FLOATING: ROAS -->
    <div class="hv-float-2 absolute -right-2 md:-right-12 top-4 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-44 hidden md:block">
        <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Rata-rata ROAS</p>
        <p class="text-2xl font-display font-extrabold text-ink mt-1">4.6<span class="text-sm text-muted">x</span></p>
        <div class="mt-2 h-1.5 bg-soft rounded-full overflow-hidden">
            <div class="h-full bg-gradient-to-r from-accent via-accent-2 to-orange-500 rounded-full" style="width: 92%;"></div>
        </div>
    </div>

    <!-- FLOATING: Synergy -->
    <div class="hv-float-3 absolute -right-2 md:-right-10 bottom-4 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-52 hidden lg:flex items-center gap-2">
        <div class="w-9 h-9 rounded-full bg-gradient-to-br from-teal to-blue-500 flex items-center justify-center shrink-0">
            <CheckCircle2 class="w-4 h-4 text-white" />
        </div>
        <div class="min-w-0">
            <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Sinergi</p>
            <p class="text-base font-display font-extrabold text-ink leading-tight">Semua kanal</p>
        </div>
        <span class="live-dot relative w-1.5 h-1.5 rounded-full bg-green ml-auto anim-pulse"></span>
    </div>
</div>

<style>
    .hv-card { opacity: 0; transform: scale(0.95); }
    .is-mounted .hv-card { animation: cardIn 0.7s cubic-bezier(0.22, 1, 0.36, 1) forwards; }
    @keyframes cardIn { to { opacity: 1; transform: scale(1); } }

    .pulse-ring {
        animation: pulseOut 2s ease-out infinite;
    }
    @keyframes pulseOut {
        0% { transform: scale(1); opacity: 0.6; }
        100% { transform: scale(1.6); opacity: 0; }
    }

    .pulse-ring-node {
        animation: pulseNodeOut 1.5s ease-out infinite;
    }
    @keyframes pulseNodeOut {
        0% { transform: scale(1); opacity: 0.8; }
        100% { transform: scale(1.5); opacity: 0; }
    }

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

    @keyframes dashFlow {
        from { stroke-dashoffset: 0; }
        to { stroke-dashoffset: -10; }
    }

    .hv-float-1 { animation: floatNotif 6s ease-in-out infinite 0.3s; }
    .hv-float-2 { animation: floatNotif 6s ease-in-out infinite 1.3s; }
    .hv-float-3 { animation: floatNotif 6s ease-in-out infinite 2.1s; }
    @keyframes floatNotif {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }

    @media (prefers-reduced-motion: reduce) {
        .hv-card, .is-mounted .hv-card { animation: none; opacity: 1; transform: none; }
        .pulse-ring, .pulse-ring-node, .hv-float-1, .hv-float-2, .hv-float-3, .anim-pulse, .live-dot::after { animation: none; }
    }
</style>
