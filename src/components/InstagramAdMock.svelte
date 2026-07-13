<script>
    import { onMount } from 'svelte';
    import { Heart, MessageCircle, Send, Bookmark, MoreHorizontal, Volume2, VolumeX, Sparkles } from 'lucide-svelte';

    let mounted = false;
    let formatIndex = 0; // 0 = Feed, 1 = Story, 2 = Reels
    let formatLabels = ['Feed', 'Story', 'Reels'];
    let heartPopped = false;
    let likes = 1247;
    let views = 8432;

    const formats = ['feed', 'story', 'reels'];

    onMount(() => {
        mounted = true;
        // Auto-cycle format
        const interval = setInterval(() => {
            formatIndex = (formatIndex + 1) % 3;
        }, 3500);
        return () => clearInterval(interval);
    });

    function triggerDoubleTap() {
        if (!heartPopped) {
            heartPopped = true;
            likes++;
            setTimeout(() => heartPopped = false, 1000);
        }
    }
</script>

<div class="relative w-full max-w-sm mx-auto {mounted ? 'is-mounted' : ''}">
    <!-- Glow backdrop -->
    <div class="absolute -inset-10 pointer-events-none" aria-hidden="true">
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[480px] h-[480px] bg-gradient-to-br from-pink-500/15 via-purple-500/12 to-orange-400/12 rounded-full" style="filter: blur(48px);"></div>
    </div>

    <!-- Phone frame -->
    <div class="phone-frame relative mx-auto bg-ink rounded-[2.5rem] p-2.5 shadow-pop" style="width: 300px;">
        <div class="phone-screen relative bg-white rounded-[2rem] overflow-hidden" style="height: 580px;">
            <!-- Notch -->
            <div class="absolute top-0 left-1/2 -translate-x-1/2 w-24 h-5 bg-ink rounded-b-2xl z-30"></div>

            <!-- Status bar -->
            <div class="absolute top-1 left-0 right-0 px-5 flex items-center justify-between text-[9px] font-bold text-ink z-20">
                <span>9:41</span>
                <span class="flex items-center gap-1">
                    <span>●●●</span>
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 3C7.5 3 3.5 5.5 1 9c2.5 3.5 6.5 6 11 6s8.5-2.5 11-6c-2.5-3.5-6.5-6-11-6zm0 9a3 3 0 110-6 3 3 0 010 6z"/></svg>
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M15.67 4H14V2h-4v2H8.33C7.6 4 7 4.6 7 5.33v15.33C7 21.4 7.6 22 8.33 22h7.33c.74 0 1.34-.6 1.34-1.33V5.33C17 4.6 16.4 4 15.67 4z"/></svg>
                </span>
            </div>

            <!-- Header bar (different per format) -->
            <div class="absolute top-7 left-0 right-0 px-3 z-20 flex items-center justify-between" style="transition: all 0.3s ease;">
                {#if formats[formatIndex] === 'story' || formats[formatIndex] === 'reels'}
                    <div class="flex items-center gap-2">
                        <div class="w-7 h-7 rounded-full bg-gradient-to-br from-pink-500 via-red-500 to-yellow-500 p-[2px]">
                            <div class="w-full h-full rounded-full bg-white p-[1px]">
                                <div class="w-full h-full rounded-full bg-gradient-to-br from-accent to-orange-500 flex items-center justify-center text-white text-[10px] font-bold">SK</div>
                            </div>
                        </div>
                        <div>
                            <p class="text-white text-[11px] font-bold leading-tight drop-shadow-lg">skincareloka</p>
                            <p class="text-white/80 text-[9px] leading-tight">Sponsored</p>
                        </div>
                    </div>
                    <MoreHorizontal class="w-4 h-4 text-white drop-shadow-lg" />
                {:else}
                    <div class="flex items-center gap-2">
                        <div class="w-7 h-7 rounded-full bg-gradient-to-br from-pink-500 via-red-500 to-yellow-500 p-[2px]">
                            <div class="w-full h-full rounded-full bg-white p-[1px]">
                                <div class="w-full h-full rounded-full bg-gradient-to-br from-accent to-orange-500 flex items-center justify-center text-white text-[10px] font-bold">SK</div>
                            </div>
                        </div>
                        <div>
                            <p class="text-ink text-[11px] font-bold leading-tight">skincareloka</p>
                            <p class="text-muted text-[9px] leading-tight">Sponsored</p>
                        </div>
                    </div>
                    <MoreHorizontal class="w-4 h-4 text-ink" />
                {/if}
            </div>

            <!-- Content area (swap per format) -->
            <div class="relative w-full h-full">
                {#if formats[formatIndex] === 'feed'}
                    <!-- Feed format: square post -->
                    <div class="absolute inset-0 pt-14 pb-16 px-1">
                        <div class="w-full h-full bg-gradient-to-br from-pink-100 via-amber-50 to-orange-100 relative overflow-hidden">
                            <div class="absolute inset-0 bg-grid opacity-30"></div>
                            <div class="absolute inset-0 flex items-center justify-center">
                                <div class="relative">
                                    <div class="w-20 h-20 rounded-full bg-white/70 backdrop-blur-sm flex items-center justify-center anim-float shadow-lg">
                                        <span class="text-3xl">✨</span>
                                    </div>
                                    <div class="absolute -top-1 -right-1 w-7 h-7 rounded-full bg-accent flex items-center justify-center text-white font-bold text-[9px] shadow-md anim-pop">NEW</div>
                                </div>
                            </div>
                            <!-- Tap target -->
                            <button type="button" class="absolute inset-0 z-10" on:click={triggerDoubleTap} aria-label="Like"></button>
                            {#if heartPopped}
                                <div class="heart-pop absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20">
                                    <Heart class="w-16 h-16 text-white drop-shadow-2xl" fill="white" />
                                </div>
                            {/if}
                        </div>
                    </div>
                {:else if formats[formatIndex] === 'story'}
                    <!-- Story format: full vertical with CTA -->
                    <div class="absolute inset-0 pt-14 pb-16 px-1">
                        <div class="w-full h-full bg-gradient-to-br from-purple-300 via-pink-200 to-rose-300 relative overflow-hidden">
                            <div class="absolute inset-0 bg-grid opacity-30"></div>
                            <div class="absolute inset-0 flex flex-col items-center justify-center p-4 text-center">
                                <p class="text-[10px] font-bold uppercase tracking-wider text-white drop-shadow-lg mb-1">Promo Hari Ini</p>
                                <p class="text-xl font-display font-extrabold text-white leading-tight drop-shadow-2xl">Glow Up<br/>Skin Anda</p>
                                <p class="text-xs text-white/90 mt-2 drop-shadow-lg">Klik untuk booking</p>
                                <button class="mt-4 bg-white text-ink text-xs font-bold px-5 py-2 rounded-full shadow-lg btn-shine-accent">BOOKING →</button>
                            </div>
                            <!-- Progress bars (story-style) -->
                            <div class="absolute top-3 left-2 right-2 flex gap-1">
                                <div class="h-0.5 flex-1 bg-white/30 rounded-full overflow-hidden">
                                    <div class="h-full bg-white rounded-full" style="width: 65%;"></div>
                                </div>
                                <div class="h-0.5 flex-1 bg-white/30 rounded-full"></div>
                                <div class="h-0.5 flex-1 bg-white/30 rounded-full"></div>
                            </div>
                        </div>
                    </div>
                {:else}
                    <!-- Reels format: vertical video with overlays -->
                    <div class="absolute inset-0 pt-14 pb-16 px-1">
                        <div class="w-full h-full bg-gradient-to-b from-rose-300 via-pink-200 to-amber-200 relative overflow-hidden">
                            <div class="absolute inset-0 bg-grid opacity-30"></div>
                            <div class="absolute inset-0 flex items-center justify-center">
                                <div class="w-24 h-24 rounded-full bg-white/50 backdrop-blur-sm flex items-center justify-center anim-float shadow-lg">
                                    <span class="text-4xl">💄</span>
                                </div>
                            </div>
                            <!-- Right sidebar icons -->
                            <div class="absolute bottom-12 right-3 flex flex-col gap-3 items-center z-10">
                                <button type="button" class="flex flex-col items-center" on:click={triggerDoubleTap}>
                                    <div class="w-9 h-9 rounded-full bg-white/30 backdrop-blur-sm flex items-center justify-center">
                                        <Heart class="w-5 h-5 text-white" fill={heartPopped ? 'currentColor' : 'none'} />
                                    </div>
                                    <span class="text-[9px] font-bold text-white mt-1 drop-shadow">{likes}</span>
                                </button>
                                <button class="flex flex-col items-center">
                                    <div class="w-9 h-9 rounded-full bg-white/30 backdrop-blur-sm flex items-center justify-center">
                                        <MessageCircle class="w-5 h-5 text-white" />
                                    </div>
                                    <span class="text-[9px] font-bold text-white mt-1 drop-shadow">42</span>
                                </button>
                                <button class="flex flex-col items-center">
                                    <div class="w-9 h-9 rounded-full bg-white/30 backdrop-blur-sm flex items-center justify-center">
                                        <Send class="w-5 h-5 text-white" />
                                    </div>
                                    <span class="text-[9px] font-bold text-white mt-1 drop-shadow">18</span>
                                </button>
                                <button class="flex flex-col items-center">
                                    <div class="w-9 h-9 rounded-full bg-white/30 backdrop-blur-sm flex items-center justify-center">
                                        <Bookmark class="w-5 h-5 text-white" />
                                    </div>
                                </button>
                            </div>
                            <!-- Caption overlay bottom -->
                            <div class="absolute bottom-3 left-3 right-16 z-10">
                                <p class="text-[11px] font-bold text-white drop-shadow-lg">@skincareloka</p>
                                <p class="text-[10px] text-white/90 drop-shadow mt-0.5">Rutin 7 hari, kulit cerah nyata ✨</p>
                                <div class="flex items-center gap-1 mt-1">
                                    <Sparkles class="w-3 h-3 text-yellow-300" />
                                    <span class="text-[9px] font-bold text-white drop-shadow">Original audio</span>
                                </div>
                            </div>
                            <!-- Mute icon top-right -->
                            <button class="absolute top-3 right-3 w-7 h-7 rounded-full bg-black/40 backdrop-blur-sm flex items-center justify-center">
                                <VolumeX class="w-3.5 h-3.5 text-white" />
                            </button>
                        </div>
                    </div>
                {/if}
            </div>

            <!-- Format indicator (bottom) -->
            <div class="absolute bottom-1 left-1/2 -translate-x-1/2 flex items-center gap-1.5 bg-black/60 backdrop-blur-sm px-3 py-1 rounded-full z-30">
                {#each formatLabels as label, i}
                    <span class="text-[9px] font-bold transition-colors {formatIndex === i ? 'text-accent' : 'text-white/50'}">{label}</span>
                    {#if i < formatLabels.length - 1}
                        <span class="w-0.5 h-0.5 bg-white/30 rounded-full"></span>
                    {/if}
                {/each}
            </div>
        </div>
        <!-- Phone home indicator -->
        <div class="absolute bottom-1 left-1/2 -translate-x-1/2 w-24 h-1 bg-white/30 rounded-full"></div>
    </div>

    <!-- FLOATING: Stat callout -->
    <div class="hv-float-1 absolute -left-2 md:-left-12 top-16 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-52 hidden md:block">
        <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-pink-100 flex items-center justify-center">
                <Sparkles class="w-4 h-4 text-pink-500" />
            </div>
            <div>
                <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Discover</p>
                <p class="text-xs font-bold text-ink">60% pengguna temukan produk baru</p>
            </div>
        </div>
    </div>

    <!-- FLOATING: Reach counter -->
    <div class="hv-float-2 absolute -right-2 md:-right-10 top-8 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-44 hidden md:block">
        <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Estimasi Views</p>
        <p class="text-2xl font-display font-extrabold text-ink mt-1">{views.toLocaleString('id-ID')}</p>
        <div class="mt-2 h-1.5 bg-soft rounded-full overflow-hidden">
            <div class="h-full bg-gradient-to-r from-pink-500 via-red-500 to-orange-500 rounded-full" style="width: 78%;"></div>
        </div>
    </div>

    <!-- FLOATING: DM count -->
    <div class="hv-float-3 absolute -right-2 md:-right-12 bottom-12 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-48 hidden lg:flex items-center gap-2">
        <div class="w-9 h-9 rounded-full bg-gradient-to-br from-pink-500 to-purple-500 flex items-center justify-center shrink-0">
            <MessageCircle class="w-4 h-4 text-white" fill="currentColor" />
        </div>
        <div class="min-w-0">
            <p class="text-[9px] uppercase tracking-wider text-muted font-bold">DM Masuk</p>
            <p class="text-base font-display font-extrabold text-ink leading-tight">+{Math.floor(likes / 25)}<span class="text-xs text-muted font-bold ml-0.5">hari ini</span></p>
        </div>
        <span class="live-dot relative w-1.5 h-1.5 rounded-full bg-pink-500 ml-auto anim-pulse"></span>
    </div>
</div>

<style>
    .phone-frame { animation: phoneIn 0.7s cubic-bezier(0.22, 1, 0.36, 1) backwards; }
    @keyframes phoneIn {
        from { opacity: 0; transform: translateY(20px) scale(0.95); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    .is-mounted .phone-frame { animation-delay: 0.1s; }

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

    .anim-pop { animation: pop 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) 1.5s backwards; }
    @keyframes pop {
        0% { transform: scale(0); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }

    .heart-pop { animation: heartPop 0.9s ease-out forwards; pointer-events: none; }
    @keyframes heartPop {
        0% { transform: translate(-50%, -50%) scale(0); opacity: 0; }
        25% { transform: translate(-50%, -50%) scale(1.3); opacity: 1; }
        50% { transform: translate(-50%, -50%) scale(0.9); opacity: 1; }
        100% { transform: translate(-50%, -50%) scale(1); opacity: 0; }
    }

    .hv-float-1 { animation: floatNotif 6s ease-in-out infinite 0.3s; }
    .hv-float-2 { animation: floatNotif 6s ease-in-out infinite 1.3s; }
    .hv-float-3 { animation: floatNotif 6s ease-in-out infinite 2.1s; }
    @keyframes floatNotif {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }

    .anim-float { animation: floatY 7s ease-in-out infinite; }
    @keyframes floatY {
        0%, 100% { transform: translateY(0) rotate(0); }
        50% { transform: translateY(-12px) rotate(3deg); }
    }

    .btn-shine-accent { position: relative; overflow: hidden; }
    .btn-shine-accent::after {
        content: ''; position: absolute; inset: 0;
        background: linear-gradient(110deg, transparent 25%, rgba(255,255,255,0.5) 50%, transparent 75%);
        transform: translateX(-100%);
        animation: shine 3s linear infinite;
    }
    @keyframes shine {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(150%); }
    }

    .bg-grid {
        background-image: radial-gradient(circle at 1px 1px, rgba(15,30,61,0.06) 1px, transparent 0);
        background-size: 16px 16px;
    }

    @media (prefers-reduced-motion: reduce) {
        .phone-frame, .is-mounted .phone-frame { animation: none; opacity: 1; }
        .hv-float-1, .hv-float-2, .hv-float-3, .anim-float, .anim-pop, .anim-pulse, .live-dot::after, .btn-shine-accent::after, .heart-pop { animation: none; }
    }
</style>
