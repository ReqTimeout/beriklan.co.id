<script>
    import { onMount } from 'svelte';
    import { Heart, MessageCircle, Share2, Music2, Plus, MoreHorizontal } from 'lucide-svelte';

    let mounted = false;
    let viewCount = 0;
    let likes = 0;
    let comments = 0;
    let shares = 0;
    let heartBurst = false;
    let captionProgress = 0;

    const captions = [
        'POV: kulit kamu cerah dalam 7 hari ✨',
        'Tips skincare yang BENER-BENER works',
        'Review jujur treatment facial viral',
        'Rahasia glowing tanpa ribet',
    ];

    onMount(() => {
        mounted = true;
        // Animated counters
        const target = { views: 47, likes: 3200, comments: 184, shares: 92 };
        const duration = 2000;
        const start = performance.now();
        function tick(now) {
            const t = Math.min((now - start) / duration, 1);
            const ease = 1 - Math.pow(1 - t, 3);
            viewCount = Math.round(target.views * ease);
            likes = Math.round(target.likes * ease);
            comments = Math.round(target.comments * ease);
            shares = Math.round(target.shares * ease);
            if (t < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);

        // Caption kinetic animation
        const captionInterval = setInterval(() => {
            captionProgress = (captionProgress + 1) % captions.length;
        }, 3000);
        return () => clearInterval(captionInterval);
    });

    function triggerDoubleTap() {
        if (!heartBurst) {
            heartBurst = true;
            likes++;
            setTimeout(() => heartBurst = false, 1000);
        }
    }
</script>

<div class="relative w-full max-w-sm mx-auto {mounted ? 'is-mounted' : ''}">
    <!-- Glow backdrop -->
    <div class="absolute -inset-10 pointer-events-none" aria-hidden="true">
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[480px] h-[480px] bg-gradient-to-br from-pink-500/15 via-cyan-400/12 to-purple-500/12 rounded-full" style="filter: blur(48px);"></div>
    </div>

    <!-- Phone frame TikTok style -->
    <div class="phone-frame relative mx-auto bg-black rounded-[2.5rem] p-2.5 shadow-pop" style="width: 300px;">
        <div class="phone-screen relative rounded-[2rem] overflow-hidden" style="height: 580px; background: linear-gradient(180deg, #0a0a14 0%, #1a1a2e 50%, #0a0a14 100%);">
            <!-- Notch -->
            <div class="absolute top-0 left-1/2 -translate-x-1/2 w-24 h-5 bg-black rounded-b-2xl z-30"></div>

            <!-- Status bar -->
            <div class="absolute top-1 left-0 right-0 px-5 flex items-center justify-between text-[9px] font-bold text-white z-20">
                <span>9:41</span>
                <span class="flex items-center gap-1">
                    <span>●●●</span>
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 3C7.5 3 3.5 5.5 1 9c2.5 3.5 6.5 6 11 6s8.5-2.5 11-6c-2.5-3.5-6.5-6-11-6zm0 9a3 3 0 110-6 3 3 0 010 6z"/></svg>
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M15.67 4H14V2h-4v2H8.33C7.6 4 7 4.6 7 5.33v15.33C7 21.4 7.6 22 8.33 22h7.33c.74 0 1.34-.6 1.34-1.33V5.33C17 4.6 16.4 4 15.67 4z"/></svg>
                </span>
            </div>

            <!-- Top bar with creator info + sound wave -->
            <div class="absolute top-7 left-0 right-0 px-3 z-20 flex items-center justify-between">
                <div class="flex items-center gap-1.5">
                    <span class="text-white text-[10px] font-bold">Following</span>
                    <span class="text-white text-[10px] font-bold border-l border-white/30 pl-1.5 relative">
                        <span class="text-pink-500">|</span> For You
                    </span>
                </div>
                <MoreHorizontal class="w-4 h-4 text-white" />
            </div>

            <!-- Main video area (decorative) -->
            <div class="absolute inset-0 pt-14 pb-16 px-1">
                <div class="w-full h-full bg-gradient-to-br from-cyan-400 via-pink-400 to-purple-500 relative overflow-hidden">
                    <div class="absolute inset-0 opacity-30">
                        <div class="absolute inset-0 bg-grid"></div>
                    </div>
                    <!-- Subject overlay (face/silhouette icon) -->
                    <div class="absolute inset-0 flex items-center justify-center">
                        <div class="relative">
                            <div class="w-28 h-28 rounded-full bg-white/30 backdrop-blur-sm flex items-center justify-center anim-float shadow-2xl">
                                <span class="text-5xl">💃</span>
                            </div>
                            <div class="absolute -top-1 -right-1 w-8 h-8 rounded-full bg-yellow-300 flex items-center justify-center text-ink font-bold text-[9px] shadow-md anim-pop">
                                FYP
                            </div>
                        </div>
                    </div>

                    <!-- Tap target -->
                    <button type="button" class="absolute inset-0 z-10" on:click={triggerDoubleTap} aria-label="Like"></button>
                    {#if heartBurst}
                        <div class="heart-pop absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20">
                            <Heart class="w-16 h-16 text-white drop-shadow-2xl" fill="white" />
                        </div>
                    {/if}

                    <!-- Sound wave indicator bottom -->
                    <div class="absolute bottom-2 left-2 right-16 flex items-center gap-1.5 z-10">
                        <div class="sound-wave flex items-center gap-0.5">
                            {#each Array(5) as _, i}
                                <span class="w-0.5 bg-white rounded-full sound-bar" style="height: {4 + i * 2}px; animation-delay: {i * 0.1}s;"></span>
                            {/each}
                        </div>
                        <div class="flex items-center gap-1 bg-black/40 backdrop-blur-sm rounded-full px-2 py-0.5">
                            <Music2 class="w-2.5 h-2.5 text-white" />
                            <span class="text-[8px] font-bold text-white">Suara Original - beautyloka</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right sidebar (TikTok-style) -->
            <div class="absolute bottom-12 right-2 flex flex-col gap-3 items-center z-20">
                <button type="button" class="flex flex-col items-center" on:click={triggerDoubleTap}>
                    <div class="w-10 h-10 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center border border-white/20">
                        <Heart class="w-5 h-5 text-white" fill={heartBurst ? '#ec4899' : 'none'} stroke={heartBurst ? '#ec4899' : 'currentColor'} />
                    </div>
                    <span class="text-[9px] font-bold text-white mt-1 drop-shadow">{likes > 1000 ? (likes / 1000).toFixed(1) + 'K' : likes}</span>
                </button>
                <button class="flex flex-col items-center">
                    <div class="w-10 h-10 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center border border-white/20">
                        <MessageCircle class="w-5 h-5 text-white" />
                    </div>
                    <span class="text-[9px] font-bold text-white mt-1 drop-shadow">{comments}</span>
                </button>
                <button class="flex flex-col items-center">
                    <div class="w-10 h-10 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center border border-white/20">
                        <Share2 class="w-5 h-5 text-white" />
                    </div>
                    <span class="text-[9px] font-bold text-white mt-1 drop-shadow">{shares}</span>
                </button>
                <!-- Spinning album disc -->
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-pink-500 to-cyan-400 p-0.5 mt-1 spin-slow">
                    <div class="w-full h-full rounded-full bg-black flex items-center justify-center text-[8px] font-bold text-white">♪</div>
                </div>
            </div>

            <!-- Bottom info area -->
            <div class="absolute bottom-2 left-3 right-16 z-10 pr-2">
                <p class="text-[11px] font-bold text-white drop-shadow-lg">@skincareloka</p>
                <p class="text-[10px] text-white/90 drop-shadow mt-0.5 leading-tight" style="transition: opacity 0.4s ease;">
                    {captions[captionProgress]}
                </p>
                <p class="text-[9px] text-white/70 mt-1 drop-shadow">#skincare #glowing #viral</p>
            </div>
        </div>
    </div>

    <!-- FLOATING: Views counter -->
    <div class="hv-float-1 absolute -left-2 md:-left-12 top-20 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-52 hidden md:block">
        <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-pink-100 flex items-center justify-center text-pink-500 text-lg">🔥</div>
            <div>
                <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Estimasi Views</p>
                <p class="text-base font-display font-extrabold text-ink leading-tight">{viewCount}K–75K<span class="text-[9px] text-muted font-bold ml-1">/kampanye</span></p>
            </div>
        </div>
    </div>

    <!-- FLOATING: Sound wave card -->
    <div class="hv-float-2 absolute -right-2 md:-right-12 top-8 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-48 hidden md:block">
        <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Original Sound</p>
        <div class="flex items-center gap-2 mt-1">
            <Music2 class="w-4 h-4 text-ink" />
            <div class="sound-wave-mini flex items-center gap-0.5 flex-1 h-6">
                {#each Array(12) as _, i}
                    <span class="w-0.5 bg-ink rounded-full sound-bar-mini" style="height: {6 + (i % 4) * 4}px; animation-delay: {i * 0.08}s;"></span>
                {/each}
            </div>
        </div>
        <p class="text-[10px] font-bold text-ink mt-1.5">beautyloka · 47K video</p>
    </div>

    <!-- FLOATING: FYP badge -->
    <div class="hv-float-3 absolute -right-2 md:-right-10 bottom-16 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-48 hidden lg:flex items-center gap-2">
        <div class="w-9 h-9 rounded-full bg-gradient-to-br from-pink-500 to-cyan-400 flex items-center justify-center text-white text-base shrink-0 anim-pulse">✨</div>
        <div class="min-w-0">
            <p class="text-[9px] uppercase tracking-wider text-muted font-bold">For You Page</p>
            <p class="text-base font-display font-extrabold text-ink leading-tight">Reached!</p>
        </div>
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

    .spin-slow { animation: spin 6s linear infinite; }
    @keyframes spin {
        from { transform: rotate(0); }
        to { transform: rotate(360deg); }
    }

    .sound-bar { animation: soundBar 0.8s ease-in-out infinite alternate; }
    @keyframes soundBar {
        from { transform: scaleY(0.5); }
        to { transform: scaleY(1.4); }
    }
    .sound-bar-mini { animation: soundBarMini 0.6s ease-in-out infinite alternate; }
    @keyframes soundBarMini {
        from { transform: scaleY(0.6); }
        to { transform: scaleY(1.2); }
    }

    .bg-grid {
        background-image: radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0);
        background-size: 16px 16px;
    }

    @media (prefers-reduced-motion: reduce) {
        .phone-frame, .is-mounted .phone-frame, .spin-slow, .sound-bar, .sound-bar-mini { animation: none; }
        .hv-float-1, .hv-float-2, .hv-float-3, .anim-float, .anim-pop, .anim-pulse { animation: none; }
        .heart-pop { animation: none; }
    }
</style>
