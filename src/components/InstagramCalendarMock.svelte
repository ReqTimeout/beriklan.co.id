<script>
    import { onMount } from 'svelte';
    import { Calendar, Image, Video, Heart, MessageCircle, BarChart3, TrendingUp, Users } from 'lucide-svelte';

    let mounted = false;
    let postsCount = 0;
    let engagement = 0;

    const days = ['S', 'S', 'R', 'K', 'J', 'S', 'M'];
    // Mock: some days have posts (orange), others empty
    const postsMap = {
        0: [{ type: 'image' }, { type: 'story' }],
        1: [{ type: 'video' }],
        2: [{ type: 'image' }, { type: 'image' }, { type: 'story' }],
        3: [],
        4: [{ type: 'video' }, { type: 'story' }],
        5: [{ type: 'image' }, { type: 'image' }],
        6: [{ type: 'story' }, { type: 'image' }],
    };

    onMount(() => {
        mounted = true;
        const target = { posts: 35, engagement: 4800 };
        const start = performance.now();
        function tick(now) {
            const t = Math.min((now - start) / 1800, 1);
            const ease = 1 - Math.pow(1 - t, 3);
            postsCount = Math.round(target.posts * ease);
            engagement = Math.round(target.engagement * ease);
            if (t < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    });

    function formatNumber(n) {
        if (n >= 1000) return (n / 1000).toFixed(1).replace('.0', '') + 'K';
        return n.toLocaleString('id-ID');
    }
</script>

<div class="relative w-full max-w-lg mx-auto {mounted ? 'is-mounted' : ''}">
    <!-- Glow backdrop -->
    <div class="absolute -inset-10 pointer-events-none" aria-hidden="true">
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[480px] h-[480px] bg-gradient-to-br from-pink-500/15 via-purple-500/12 to-orange-400/12 rounded-full" style="filter: blur(48px);"></div>
    </div>

    <!-- Calendar card -->
    <div class="hv-card relative bg-white rounded-2xl shadow-pop border border-gray-100 overflow-hidden">
        <div class="flex items-center gap-1.5 px-4 py-2.5 bg-soft border-b border-gray-100">
            <span class="w-2.5 h-2.5 rounded-full bg-red-400"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-yellow-400"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-green-400"></span>
            <span class="ml-3 text-[10px] font-mono text-muted flex items-center gap-1.5">
                <Calendar class="w-3 h-3" />
                Content Calendar · November 2026
            </span>
        </div>

        <div class="p-4 md:p-5 space-y-4">
            <!-- Header -->
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-[10px] uppercase tracking-wider text-muted font-bold">Monthly Output</p>
                    <p class="text-base font-bold text-ink mt-0.5">November 2026</p>
                </div>
                <div class="flex items-center gap-1 bg-green/10 text-green text-[10px] font-bold px-2 py-1 rounded-full">
                    <span class="live-dot relative w-1.5 h-1.5 rounded-full bg-green"></span>
                    ACTIVE
                </div>
            </div>

            <!-- Calendar grid -->
            <div class="border border-gray-100 rounded-xl overflow-hidden">
                <div class="grid grid-cols-7 bg-soft border-b border-gray-100">
                    {#each days as day}
                        <div class="text-center text-[10px] font-bold text-muted uppercase tracking-wider py-2">{day}</div>
                    {/each}
                </div>
                <div class="grid grid-cols-7 gap-px bg-gray-100">
                    {#each Array(7) as _, dayIdx}
                        <div class="bg-white min-h-[44px] p-1 flex flex-col gap-0.5">
                            <span class="text-[10px] font-bold text-muted">{dayIdx + 1}</span>
                            <div class="flex flex-wrap gap-0.5 mt-auto">
                                {#each postsMap[dayIdx] || [] as post}
                                    {#if post.type === 'image'}
                                        <span class="w-3 h-3 rounded-sm bg-gradient-to-br from-accent to-orange-500" title="Image post"></span>
                                    {:else if post.type === 'video'}
                                        <span class="w-3 h-3 rounded-sm bg-gradient-to-br from-pink-500 to-red-500" title="Video/Reels"></span>
                                    {:else if post.type === 'story'}
                                        <span class="w-3 h-3 rounded-full bg-gradient-to-br from-purple-500 to-pink-500" title="Story"></span>
                                    {/if}
                                {/each}
                            </div>
                        </div>
                    {/each}
                </div>
            </div>

            <!-- Legend -->
            <div class="flex items-center gap-4 text-[10px] text-muted">
                <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-sm bg-gradient-to-br from-accent to-orange-500"></span> Image</span>
                <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-sm bg-gradient-to-br from-pink-500 to-red-500"></span> Video/Reels</span>
                <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-gradient-to-br from-purple-500 to-pink-500"></span> Story</span>
            </div>

            <!-- Stats row -->
            <div class="grid grid-cols-3 gap-2 pt-3 border-t border-gray-100">
                <div class="text-center">
                    <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Total</p>
                    <p class="text-lg font-display font-extrabold text-ink leading-none mt-1">{postsCount}</p>
                    <p class="text-[9px] text-muted">konten</p>
                </div>
                <div class="text-center">
                    <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Engagement</p>
                    <p class="text-lg font-display font-extrabold text-ink leading-none mt-1">{formatNumber(engagement)}</p>
                    <p class="text-[9px] text-muted">/bulan</p>
                </div>
                <div class="text-center">
                    <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Reach</p>
                    <p class="text-lg font-display font-extrabold text-green leading-none mt-1">+24%</p>
                    <p class="text-[9px] text-muted">vs bln lalu</p>
                </div>
            </div>
        </div>
    </div>

    <!-- FLOATING: Followers growth -->
    <div class="hv-float-1 absolute -left-2 md:-left-12 top-16 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-52 hidden md:block">
        <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-pink-100 flex items-center justify-center">
                <Users class="w-4 h-4 text-pink-500" />
            </div>
            <div>
                <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Followers</p>
                <p class="text-base font-display font-extrabold text-ink leading-tight">12.4K <span class="text-[10px] text-green">↑ 18%</span></p>
            </div>
        </div>
    </div>

    <!-- FLOATING: Engagement rate -->
    <div class="hv-float-2 absolute -right-2 md:-right-10 top-8 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-48 hidden md:block">
        <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Avg. Engagement</p>
        <p class="text-2xl font-display font-extrabold text-ink mt-1">6.8<span class="text-sm text-muted">%</span></p>
        <div class="mt-2 h-1.5 bg-soft rounded-full overflow-hidden">
            <div class="h-full bg-gradient-to-r from-pink-500 via-red-500 to-orange-500 rounded-full" style="width: 68%;"></div>
        </div>
    </div>

    <!-- FLOATING: Top post -->
    <div class="hv-float-3 absolute -right-2 md:-right-12 bottom-12 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-52 hidden lg:flex items-center gap-2">
        <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-pink-400 via-red-400 to-orange-400 flex items-center justify-center shrink-0">
            <span class="text-xl">📸</span>
        </div>
        <div class="min-w-0">
            <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Top Post</p>
            <p class="text-[11px] font-bold text-ink leading-tight">Tutorial Skincare</p>
            <p class="text-[9px] text-muted">2,3K likes · 187 saves</p>
        </div>
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

    .hv-float-1 { animation: floatNotif 6s ease-in-out infinite 0.3s; }
    .hv-float-2 { animation: floatNotif 6s ease-in-out infinite 1.3s; }
    .hv-float-3 { animation: floatNotif 6s ease-in-out infinite 2.1s; }
    @keyframes floatNotif {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }

    @media (prefers-reduced-motion: reduce) {
        .hv-card, .is-mounted .hv-card { animation: none; opacity: 1; transform: none; }
        .hv-float-1, .hv-float-2, .hv-float-3, .live-dot::after { animation: none; }
    }
</style>
