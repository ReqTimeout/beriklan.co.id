<script>
    import { onMount } from 'svelte';
    import { Globe, Layers, Mail, ShoppingCart, Smartphone, Zap, Eye, Search, Lock } from 'lucide-svelte';

    let mounted = false;
    let deviceIndex = 0;
    const devices = ['desktop', 'tablet', 'mobile'];

    onMount(() => {
        mounted = true;
        const interval = setInterval(() => {
            deviceIndex = (deviceIndex + 1) % 3;
        }, 3500);
        return () => clearInterval(interval);
    });

    function getDeviceClass() {
        if (devices[deviceIndex] === 'mobile') return 'w-32 h-56';
        if (devices[deviceIndex] === 'tablet') return 'w-56 h-72';
        return 'w-full max-w-md h-72';
    }
</script>

<div class="relative w-full max-w-lg mx-auto {mounted ? 'is-mounted' : ''}">
    <!-- Glow backdrop -->
    <div class="absolute -inset-10 pointer-events-none" aria-hidden="true">
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[480px] h-[480px] bg-gradient-to-br from-blue-500/15 via-teal/12 to-accent/10 rounded-full" style="filter: blur(48px);"></div>
    </div>

    <!-- Browser frame -->
    <div class="hv-card relative bg-white rounded-2xl shadow-pop border border-gray-100 overflow-hidden">
        <!-- Window chrome -->
        <div class="flex items-center gap-1.5 px-4 py-2.5 bg-soft border-b border-gray-100">
            <span class="w-2.5 h-2.5 rounded-full bg-red-400"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-yellow-400"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-green-400"></span>
            <div class="ml-3 flex-1 bg-white rounded-md px-3 py-1 text-[10px] text-muted flex items-center gap-1.5 border border-gray-200 max-w-xs">
                <Lock class="w-2.5 h-2.5 text-green" />
                <span class="font-mono">bisnisanda.com</span>
            </div>
            <!-- Device toggle -->
            <div class="flex items-center gap-1 bg-white border border-gray-200 rounded-md p-0.5">
                <button class="w-5 h-5 rounded flex items-center justify-center transition-colors {deviceIndex === 0 ? 'bg-ink text-white' : 'text-muted hover:bg-soft'}" aria-label="Desktop">
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M21 2H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h7v2H8v2h8v-2h-2v-2h7c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H3V4h18v12z"/></svg>
                </button>
                <button class="w-5 h-5 rounded flex items-center justify-center transition-colors {deviceIndex === 1 ? 'bg-ink text-white' : 'text-muted hover:bg-soft'}" aria-label="Tablet">
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M19 1H5c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V3c0-1.1-.9-2-2-2zm0 18H5V3h14v16z"/></svg>
                </button>
                <button class="w-5 h-5 rounded flex items-center justify-center transition-colors {deviceIndex === 2 ? 'bg-ink text-white' : 'text-muted hover:bg-soft'}" aria-label="Mobile">
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M17 1H7c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-2-2-2zm0 18H7V5h10v14z"/></svg>
                </button>
            </div>
        </div>

        <!-- Site preview with device frame -->
        <div class="bg-soft p-6 flex items-center justify-center min-h-[260px]">
            <div class="device-frame transition-all duration-500 {getDeviceClass()}">
                <div class="w-full h-full bg-white rounded-lg shadow-lg border-2 border-gray-800 overflow-hidden flex flex-col">
                    <!-- Mini browser bar -->
                    <div class="bg-gray-100 px-2 py-1.5 flex items-center gap-1 border-b">
                        <span class="w-1.5 h-1.5 rounded-full bg-red-400"></span>
                        <span class="w-1.5 h-1.5 rounded-full bg-yellow-400"></span>
                        <span class="w-1.5 h-1.5 rounded-full bg-green-400"></span>
                    </div>
                    <!-- Site content -->
                    <div class="flex-1 bg-white overflow-hidden">
                        <!-- Navbar mini -->
                        <div class="px-3 py-2 border-b border-gray-100 flex items-center justify-between">
                            <div class="w-12 h-2 bg-ink rounded"></div>
                            <div class="flex gap-1">
                                <span class="w-4 h-1 bg-gray-300 rounded"></span>
                                <span class="w-4 h-1 bg-gray-300 rounded"></span>
                                <span class="w-4 h-1 bg-gray-300 rounded"></span>
                            </div>
                        </div>
                        <!-- Hero -->
                        <div class="px-3 py-3 bg-gradient-to-br from-soft to-beige">
                            <div class="w-3/4 h-2 bg-ink rounded mb-1.5"></div>
                            <div class="w-1/2 h-2 bg-accent rounded mb-2"></div>
                            <div class="w-full h-1 bg-gray-300 rounded mb-1"></div>
                            <div class="w-5/6 h-1 bg-gray-300 rounded mb-2"></div>
                            <div class="flex gap-1">
                                <div class="w-12 h-3 bg-ink rounded"></div>
                                <div class="w-10 h-3 bg-white border border-gray-200 rounded"></div>
                            </div>
                        </div>
                        <!-- Features row -->
                        <div class="px-3 py-2 grid grid-cols-3 gap-1">
                            <div class="aspect-square bg-soft rounded p-1 flex flex-col items-center justify-center">
                                <div class="w-3 h-3 rounded-full bg-accent/30 mb-0.5"></div>
                                <div class="w-6 h-0.5 bg-gray-300 rounded"></div>
                            </div>
                            <div class="aspect-square bg-soft rounded p-1 flex flex-col items-center justify-center">
                                <div class="w-3 h-3 rounded-full bg-teal/30 mb-0.5"></div>
                                <div class="w-6 h-0.5 bg-gray-300 rounded"></div>
                            </div>
                            <div class="aspect-square bg-soft rounded p-1 flex flex-col items-center justify-center">
                                <div class="w-3 h-3 rounded-full bg-green/30 mb-0.5"></div>
                                <div class="w-6 h-0.5 bg-gray-300 rounded"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Bottom: features tags -->
        <div class="px-4 py-3 bg-white border-t border-gray-100 flex items-center gap-2 flex-wrap">
            <span class="text-[9px] font-bold text-ink bg-soft px-2 py-1 rounded flex items-center gap-1">
                <Smartphone class="w-2.5 h-2.5" /> Responsive
            </span>
            <span class="text-[9px] font-bold text-ink bg-soft px-2 py-1 rounded flex items-center gap-1">
                <Zap class="w-2.5 h-2.5" /> Fast Load
            </span>
            <span class="text-[9px] font-bold text-ink bg-soft px-2 py-1 rounded flex items-center gap-1">
                <Search class="w-2.5 h-2.5" /> SEO Ready
            </span>
            <span class="text-[9px] font-bold text-ink bg-soft px-2 py-1 rounded flex items-center gap-1">
                <Lock class="w-2.5 h-2.5" /> SSL
            </span>
        </div>
    </div>

    <!-- FLOATING: Pages count -->
    <div class="hv-float-1 absolute -left-2 md:-left-12 top-16 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-52 hidden md:block">
        <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                <Layers class="w-4 h-4 text-blue-600" />
            </div>
            <div>
                <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Halaman</p>
                <p class="text-base font-display font-extrabold text-ink leading-tight">1–25<span class="text-[9px] text-muted font-bold ml-1">halaman</span></p>
            </div>
        </div>
    </div>

    <!-- FLOATING: Email account -->
    <div class="hv-float-2 absolute -right-2 md:-right-10 top-8 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-48 hidden md:block">
        <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-teal/15 flex items-center justify-center">
                <Mail class="w-4 h-4 text-teal" />
            </div>
            <div>
                <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Email</p>
                <p class="text-base font-display font-extrabold text-ink leading-tight">1–25<span class="text-[9px] text-muted font-bold ml-1">akun</span></p>
            </div>
        </div>
    </div>

    <!-- FLOATING: Performance -->
    <div class="hv-float-3 absolute -right-2 md:-right-12 bottom-12 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-48 hidden lg:flex items-center gap-2">
        <div class="w-9 h-9 rounded-full bg-green/15 flex items-center justify-center shrink-0">
            <Zap class="w-4 h-4 text-green" />
        </div>
        <div class="min-w-0">
            <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Performance</p>
            <p class="text-base font-display font-extrabold text-ink leading-tight">95<span class="text-[9px] text-muted font-bold ml-0.5">/100</span></p>
        </div>
        <span class="live-dot relative w-1.5 h-1.5 rounded-full bg-green ml-auto anim-pulse"></span>
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

    .hv-float-1 { animation: floatNotif 6s ease-in-out infinite 0.3s; }
    .hv-float-2 { animation: floatNotif 6s ease-in-out infinite 1.3s; }
    .hv-float-3 { animation: floatNotif 6s ease-in-out infinite 2.1s; }
    @keyframes floatNotif {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }

    @media (prefers-reduced-motion: reduce) {
        .hv-card, .is-mounted .hv-card { animation: none; opacity: 1; transform: none; }
        .hv-float-1, .hv-float-2, .hv-float-3, .anim-pulse, .live-dot::after { animation: none; }
    }
</style>
