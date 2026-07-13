<script>
    import { onMount } from 'svelte';
    import { Wallet, Target, TrendingUp, Zap, Check, MessageCircle, CircleDollarSign } from 'lucide-svelte';

    let mounted = false;
    onMount(() => { mounted = true; });

    // Animated counters
    let roas = 0;
    let spend = 0;
    let conv = 0;
    let revenue = 0;
    let cpa = 0;

    onMount(() => {
        const target = { roas: 4.2, spend: 12, conv: 387, revenue: 50.4, cpa: 31 };
        const duration = 1800;
        const start = performance.now();
        function tick(now) {
            const t = Math.min((now - start) / duration, 1);
            const ease = 1 - Math.pow(1 - t, 3);
            roas = +(target.roas * ease).toFixed(2);
            spend = Math.round(target.spend * ease);
            conv = Math.round(target.conv * ease);
            revenue = +(target.revenue * ease).toFixed(1);
            cpa = Math.round(target.cpa * ease);
            if (t < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    });

    const tickerItems = [
        { Icon: Check, color: 'green', text: 'Order #387 • Rp 487.000', sub: 'dari Meta Ads' },
        { Icon: TrendingUp, color: 'amber', text: 'ROAS naik ke 5.1x', sub: 'TikTok Ads' },
        { Icon: MessageCircle, color: 'sky', text: 'Lead baru masuk', sub: 'Google Search Ads' },
        { Icon: Target, color: 'green', text: 'CPA turun 23%', sub: 'IG Ads minggu ini' },
    ];
</script>

<div class="relative w-full max-w-lg mx-auto">
    <!-- Glow backdrop -->
    <div class="absolute -inset-10 pointer-events-none perf-gpu" aria-hidden="true">
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-br from-accent/15 via-amber-200/8 to-teal/12 rounded-full" style="filter: blur(48px);"></div>
    </div>

    <!-- Main card: dashboard mockup -->
    <div class="hv-card relative bg-white rounded-2xl shadow-pop border border-gray-100 overflow-hidden">
        <!-- Window chrome -->
        <div class="flex items-center gap-1.5 px-4 py-3 bg-soft border-b border-gray-100">
            <span class="w-2.5 h-2.5 rounded-full bg-red-400"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-yellow-400"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-green-400"></span>
            <span class="ml-3 text-[10px] font-mono text-muted flex items-center gap-1.5">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
                ads.beriklan.co.id/dashboard
            </span>
            <span class="ml-auto flex items-center gap-1 text-[9px] text-green font-bold">
                <span class="live-dot relative w-1.5 h-1.5 rounded-full bg-green"></span>
                LIVE
            </span>
        </div>

        <div class="p-5 md:p-6 space-y-4">
            <!-- Top: period + status -->
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-[10px] uppercase tracking-wider text-muted font-bold">Campaign Performance</p>
                    <p class="text-base font-bold text-ink mt-0.5">November 2026</p>
                </div>
                <div class="flex items-center gap-1 bg-green/10 text-green text-[10px] font-bold px-2 py-1 rounded-full badge-pop">
                    <svg class="w-2.5 h-2.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clip-rule="evenodd"/></svg>
                    +24%
                </div>
            </div>

            <!-- ROAS highlight -->
            <div class="roas-block bg-gradient-to-br from-ink via-primary-2 to-ink rounded-xl p-5 text-white relative overflow-hidden">
                <div class="absolute -right-6 -top-6 w-28 h-28 bg-accent/20 rounded-full pointer-events-none perf-gpu" style="filter: blur(20px);"></div>
                <div class="absolute -left-4 -bottom-4 w-20 h-20 bg-teal/15 rounded-full pointer-events-none"></div>
                <div class="relative">
                    <p class="text-[10px] uppercase tracking-wider text-white/50 font-bold">Return on Ad Spend</p>
                    <div class="flex items-baseline gap-2 mt-1">
                        <span class="roas-num text-6xl font-display font-extrabold tracking-tight text-accent">{roas}</span>
                        <span class="text-2xl font-display font-extrabold text-accent">x</span>
                    </div>

                    <div class="mt-4 grid grid-cols-7 gap-1 h-12 items-end">
                        {#each [40, 55, 48, 70, 65, 85, 95] as h, i}
                            <div class="bar flex-1 bg-gradient-to-t from-accent/60 to-accent rounded-sm bar-anim" style="height: {h}%; opacity: {0.4 + i * 0.08}; animation-delay: {i * 80}ms;"></div>
                        {/each}
                    </div>

                    <p class="text-[10px] text-white/60 mt-2">
                        Naik dari <span class="text-accent font-bold">3.1x</span> bulan lalu
                    </p>
                </div>
            </div>

            <!-- 4 metric cards -->
            <div class="grid grid-cols-4 gap-2">
                <div class="bg-soft rounded-lg p-2.5 metric-card">
                    <div class="w-5 h-5 rounded bg-blue-100 text-blue-600 flex items-center justify-center mb-1.5"><Wallet size="12" strokeWidth="2.5" /></div>
                    <p class="text-[8px] text-muted uppercase font-bold leading-tight">Spend</p>
                    <p class="text-sm font-extrabold text-ink mt-0.5">Rp{spend}jt</p>
                </div>
                <div class="bg-soft rounded-lg p-2.5 metric-card">
                    <div class="w-5 h-5 rounded bg-purple-100 text-purple-600 flex items-center justify-center mb-1.5"><Target size="12" strokeWidth="2.5" /></div>
                    <p class="text-[8px] text-muted uppercase font-bold leading-tight">Conv.</p>
                    <p class="text-sm font-extrabold text-ink mt-0.5">{conv}</p>
                </div>
                <div class="bg-soft rounded-lg p-2.5 metric-card">
                    <div class="w-5 h-5 rounded bg-green-100 text-green-600 flex items-center justify-center mb-1.5"><TrendingUp size="12" strokeWidth="2.5" /></div>
                    <p class="text-[8px] text-muted uppercase font-bold leading-tight">Revenue</p>
                    <p class="text-sm font-extrabold text-green mt-0.5">{revenue}jt</p>
                </div>
                <div class="bg-soft rounded-lg p-2.5 metric-card">
                    <div class="w-5 h-5 rounded bg-amber-100 text-amber-600 flex items-center justify-center mb-1.5"><Zap size="12" strokeWidth="2.5" /></div>
                    <p class="text-[8px] text-muted uppercase font-bold leading-tight">CPA</p>
                    <p class="text-sm font-extrabold text-ink mt-0.5">Rp{cpa}k</p>
                </div>
            </div>

            <!-- 7-day trend -->
            <div class="bg-soft rounded-lg p-4">
                <div class="flex items-center justify-between mb-3">
                    <p class="text-[10px] text-muted font-bold uppercase">7-day trend</p>
                    <div class="flex items-center gap-3 text-[9px]">
                        <span class="flex items-center gap-1"><span class="w-2 h-0.5 bg-ink"></span>Spend</span>
                        <span class="flex items-center gap-1"><span class="w-2 h-0.5 bg-accent"></span>ROAS</span>
                    </div>
                </div>
                <svg viewBox="0 0 200 50" class="w-full h-14" preserveAspectRatio="none">
                    <line x1="0" y1="25" x2="200" y2="25" stroke="#e5e7eb" stroke-width="0.5" stroke-dasharray="2 3"/>
                    <defs>
                        <linearGradient id="roasGrad" x1="0" x2="0" y1="0" y2="1">
                            <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.3"/>
                            <stop offset="100%" stop-color="#f59e0b" stop-opacity="0"/>
                        </linearGradient>
                    </defs>
                    <polygon points="0,38 28,35 56,30 84,28 112,22 140,18 168,14 200,8 200,50 0,50" fill="url(#roasGrad)"/>
                    <polyline points="0,30 28,28 56,32 84,26 112,29 140,22 168,24 200,18" fill="none" stroke="#0f1e3d" stroke-width="1.5" stroke-linecap="round"/>
                    <polyline points="0,38 28,35 56,30 84,28 112,22 140,18 168,14 200,8" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" class="trend-line"/>
                    <circle cx="200" cy="8" r="3" fill="#f59e0b">
                        <animate attributeName="r" values="3;5;3" dur="2s" repeatCount="indefinite"/>
                    </circle>
                    <circle cx="200" cy="8" r="6" fill="#f59e0b" opacity="0.3">
                        <animate attributeName="r" values="6;10;6" dur="2s" repeatCount="indefinite"/>
                        <animate attributeName="opacity" values="0.3;0;0.3" dur="2s" repeatCount="indefinite"/>
                    </circle>
                </svg>
            </div>
        </div>
    </div>

    <!-- Floating notifications -->
    {#if mounted}
        <div class="hv-float hv-float-1 absolute -left-3 md:-left-12 bottom-8 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-56 hidden sm:flex items-start gap-2" style="animation: floatNotif 5s ease-in-out infinite 1s;">
            <div class="w-8 h-8 rounded-full bg-green/10 flex items-center justify-center shrink-0">
                <svg class="w-4 h-4 text-green" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
            </div>
            <div class="flex-1 min-w-0">
                <p class="text-[10px] font-bold text-ink">Conversion baru</p>
                <p class="text-[10px] text-muted truncate">Order #387 • Rp 487.000</p>
                <p class="text-[9px] text-green font-bold mt-0.5 flex items-center gap-1">
                    <span class="w-1.5 h-1.5 rounded-full bg-green"></span> dari Meta Ads
                </p>
            </div>
        </div>
    {/if}

    {#if mounted}
        <div class="hv-float hv-float-2 absolute -right-3 md:-right-12 top-12 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-52 hidden md:flex items-start gap-2" style="animation: floatNotif 6s ease-in-out infinite 2s;">
            <div class="w-8 h-8 rounded-full bg-accent/10 text-accent flex items-center justify-center shrink-0">
                <TrendingUp size="16" strokeWidth="2.5" />
            </div>
            <div class="flex-1 min-w-0">
                <p class="text-[10px] font-bold text-ink">ROAS update</p>
                <p class="text-[10px] text-muted truncate">TikTok naik ke 5.1x</p>
                <p class="text-[9px] text-accent font-bold mt-0.5">+18% minggu ini</p>
            </div>
        </div>
    {/if}

    {#if mounted}
        <div class="hv-float hv-float-3 absolute -right-2 md:-right-6 bottom-32 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-48 hidden lg:flex items-center gap-2" style="animation: floatNotif 7s ease-in-out infinite 3s;">
            <div class="w-7 h-7 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center shrink-0">
                <Target size="14" strokeWidth="2.5" />
            </div>
            <div class="flex-1 min-w-0">
                <p class="text-[10px] font-bold text-ink">CPA turun 23%</p>
                <p class="text-[9px] text-muted">IG Ads optimization</p>
            </div>
        </div>
    {/if}
</div>

<style>
    .hv-card { transition: box-shadow 0.4s ease; }
    .hv-card:hover { box-shadow: 0 24px 60px -12px rgba(15, 30, 61, 0.25); }

    .roas-block { animation: roas-glow 4s ease-in-out infinite; }
    @keyframes roas-glow {
        0%, 100% { box-shadow: 0 0 30px rgba(245, 158, 11, 0.1); }
        50% { box-shadow: 0 0 50px rgba(245, 158, 11, 0.2); }
    }

    .roas-num {
        animation: count-fade 1.8s ease;
    }
    @keyframes count-fade {
        from { opacity: 0; transform: scale(0.9); }
        to { opacity: 1; transform: scale(1); }
    }

    .bar-anim {
        transform-origin: bottom;
        animation: bar-grow 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
    }
    @keyframes bar-grow {
        from { transform: scaleY(0); opacity: 0.4; }
        to { transform: scaleY(1); }
    }

    .metric-card { transition: transform 0.2s ease, background 0.2s ease; }
    .metric-card:hover { transform: translateY(-2px); background: #fff7e6; }

    .live-dot::after {
        content: ""; position: absolute; inset: -2px;
        border-radius: 9999px;
        background: rgba(16, 185, 129, 0.4);
        animation: live-ping 1.8s ease-in-out infinite;
    }
    @keyframes live-ping {
        0%, 100% { opacity: 0; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(2); }
    }

    .badge-pop { animation: badge-pop 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) 1.2s both; }
    @keyframes badge-pop { from { transform: scale(0); opacity: 0; } to { transform: scale(1); opacity: 1; } }

    .trend-line {
        stroke-dasharray: 200;
        stroke-dashoffset: 200;
        animation: draw-trend 2s cubic-bezier(0.22, 1, 0.36, 1) 0.6s forwards;
    }
    @keyframes draw-trend { to { stroke-dashoffset: 0; } }

    .hv-float {
        animation: floatNotif 5s ease-in-out infinite;
    }
    @keyframes floatNotif {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }
</style>
