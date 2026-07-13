<script>
    import { onMount } from 'svelte';
    import { Heart, MessageCircle, Share2, Users, MapPin, Sparkles, ThumbsUp, Eye } from 'lucide-svelte';

    let mounted = false;
    let reach = 0;
    let messages = 0;
    let visibleChips = 0;

    onMount(() => {
        mounted = true;
        const target = { reach: 12, messages: 47 };
        const duration = 1800;
        const start = performance.now();
        function tick(now) {
            const t = Math.min((now - start) / duration, 1);
            const ease = 1 - Math.pow(1 - t, 3);
            reach = Math.round(target.reach * ease);
            messages = Math.round(target.messages * ease);
            if (t < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);

        for (let i = 0; i < 5; i++) {
            setTimeout(() => { visibleChips = i + 1; }, 600 + i * 220);
        }
    });

    const targeting = [
        { Icon: Users, label: 'Usia 25-44', color: 'bg-accent/15 text-accent' },
        { Icon: MapPin, label: 'Bandung, Jakarta, Surabaya', color: 'bg-teal/15 text-teal' },
        { Icon: Sparkles, label: 'Minat: Skincare & Beauty', color: 'bg-pink-100 text-pink-600' },
        { Icon: ThumbsUp, label: 'Remarketing: 30 hari', color: 'bg-green/15 text-green' },
        { Icon: Eye, label: 'Interest: 100+', color: 'bg-purple-100 text-purple-600' },
    ];
</script>

<div class="relative w-full max-w-lg mx-auto {mounted ? 'is-mounted' : ''}">
    <div class="absolute -inset-10 pointer-events-none" aria-hidden="true">
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[480px] h-[480px] bg-gradient-to-br from-blue-500/15 via-accent/10 to-teal/12 rounded-full" style="filter: blur(48px);"></div>
    </div>

    <div class="hv-card relative bg-white rounded-2xl shadow-pop border border-gray-100 overflow-hidden">
        <div class="flex items-center gap-1.5 px-4 py-2.5 bg-soft border-b border-gray-100">
            <span class="w-2.5 h-2.5 rounded-full bg-red-400"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-yellow-400"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-green-400"></span>
            <span class="ml-3 text-[10px] font-mono text-muted flex items-center gap-1.5">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
                facebook.com/ads/manager
            </span>
            <span class="ml-auto flex items-center gap-1 text-[9px] text-green font-bold">
                <span class="live-dot relative w-1.5 h-1.5 rounded-full bg-green"></span>
                LIVE
            </span>
        </div>

        <div class="p-4 md:p-5 space-y-4">
            <div class="flex items-start gap-3">
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-accent to-orange-500 flex items-center justify-center text-white font-bold text-sm shrink-0">BS</div>
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-1.5 flex-wrap">
                        <p class="text-sm font-bold text-ink">Beauty Studio Bandung</p>
                        <svg class="w-3.5 h-3.5 text-blue-500" fill="currentColor" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
                    </div>
                    <p class="text-[11px] text-muted mt-0.5">Sponsored &middot; Global</p>
                </div>
                <span class="text-[10px] font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded uppercase tracking-wider">Iklan</span>
            </div>

            <p class="text-sm text-ink leading-relaxed">
                Kulit kusam dan bruntusan? Treatment <strong class="text-ink">Glow Facial</strong> hanya <strong class="text-accent">Rp 249rb</strong> untuk konsultasi pertama. Booking via WhatsApp &mdash; slot terbatas tiap minggunya.
            </p>

            <div class="relative rounded-xl overflow-hidden aspect-[1.91/1] bg-gradient-to-br from-pink-200 via-amber-100 to-orange-200">
                <div class="absolute inset-0 bg-grid opacity-30"></div>
                <div class="absolute inset-0 flex items-center justify-center">
                    <div class="relative">
                        <div class="w-24 h-24 md:w-32 md:h-32 rounded-full bg-white/60 backdrop-blur-sm flex items-center justify-center anim-float shadow-lg">
                            <span class="text-4xl md:text-5xl">&#10024;</span>
                        </div>
                        <div class="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-accent flex items-center justify-center text-white font-bold text-[10px] shadow-md anim-pop">
                            &minus;40%
                        </div>
                    </div>
                </div>
                <div class="absolute bottom-3 left-3 right-3 flex items-center justify-between">
                    <div class="bg-white/95 backdrop-blur-sm rounded-lg px-3 py-1.5 shadow-md">
                        <p class="text-[9px] font-bold text-ink uppercase tracking-wider">Beauty Studio</p>
                        <p class="text-[10px] text-muted">Klinik Kecantikan &middot; Bandung</p>
                    </div>
                    <div class="cta-shine relative bg-white rounded-lg px-4 py-2 font-bold text-ink text-xs shadow-md">
                        <span class="relative z-10">Konsultasi via WhatsApp</span>
                    </div>
                </div>
            </div>

            <div class="flex items-center justify-between text-[11px] text-muted pt-1">
                <div class="flex items-center -space-x-1">
                    <span class="w-4 h-4 rounded-full bg-blue-500 flex items-center justify-center ring-2 ring-white"><svg class="w-2.5 h-2.5 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M14 9V5a3 3 0 00-3-3l-4 9v11h11.28a2 2 0 002-1.7l1.38-9a2 2 0 00-2-2.3zM7 22H4a2 2 0 01-2-2v-7a2 2 0 012-2h3"/></svg></span>
                    <span class="w-4 h-4 rounded-full bg-red-500 flex items-center justify-center ring-2 ring-white"><Heart class="w-2.5 h-2.5 text-white" fill="currentColor" /></span>
                    <span class="ml-2">2,4 rb</span>
                </div>
                <span>187 komentar &middot; 43 kali dibagikan</span>
            </div>

            <div class="flex items-center justify-around pt-3 border-t border-gray-100 text-[11px] font-bold text-muted">
                <button class="flex items-center gap-1.5 hover:text-blue-600 transition group">
                    <ThumbsUp class="w-4 h-4 group-hover:scale-110 transition" /> Suka
                </button>
                <button class="flex items-center gap-1.5 hover:text-blue-600 transition group">
                    <MessageCircle class="w-4 h-4 group-hover:scale-110 transition" /> Komentar
                </button>
                <button class="flex items-center gap-1.5 hover:text-blue-600 transition group">
                    <Share2 class="w-4 h-4 group-hover:scale-110 transition" /> Bagikan
                </button>
            </div>
        </div>
    </div>

    <div class="hv-float hv-float-1 absolute -left-3 md:-left-10 top-10 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-60 hidden md:block">
        <div class="flex items-center gap-2 mb-2">
            <div class="w-7 h-7 rounded-lg bg-blue-50 flex items-center justify-center">
                <Users class="w-3.5 h-3.5 text-blue-600" />
            </div>
            <div>
                <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Target Audiens</p>
                <p class="text-xs font-bold text-ink">Live &middot; 5 set aktif</p>
            </div>
        </div>
        <div class="space-y-1.5">
            {#each targeting as item, i}
                <div class="target-chip flex items-center gap-2 p-1.5 rounded-lg {item.color}" style="opacity: {visibleChips > i ? 1 : 0}; transform: translateX({visibleChips > i ? 0 : -8}px); transition: opacity 0.4s ease, transform 0.4s cubic-bezier(0.22, 1, 0.36, 1);">
                    <svelte:component this={item.Icon} class="w-3 h-3 shrink-0" />
                    <span class="text-[10px] font-bold leading-tight">{item.label}</span>
                </div>
            {/each}
        </div>
    </div>

    <div class="hv-float hv-float-2 absolute -right-3 md:-right-8 top-4 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-52 hidden md:block">
        <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Estimasi Jangkauan</p>
        <p class="text-2xl font-display font-extrabold text-ink mt-1">{reach}<span class="text-sm font-bold text-muted">K</span><span class="text-base text-muted">&ndash;15K</span></p>
        <p class="text-[10px] text-muted mt-0.5">orang / hari</p>
        <div class="mt-2 h-1.5 bg-soft rounded-full overflow-hidden">
            <div class="h-full bg-gradient-to-r from-accent to-orange-500 rounded-full" style="width: 72%;"></div>
        </div>
    </div>

    <div class="hv-float hv-float-3 absolute -right-2 md:-right-6 bottom-4 bg-white rounded-xl shadow-pop border border-gray-100 p-3 w-56 hidden lg:flex items-center gap-2">
        <div class="w-9 h-9 rounded-full bg-green/15 flex items-center justify-center shrink-0">
            <MessageCircle class="w-4 h-4 text-green" fill="currentColor" />
        </div>
        <div class="min-w-0">
            <p class="text-[9px] uppercase tracking-wider text-muted font-bold">Pesan Masuk</p>
            <p class="text-base font-display font-extrabold text-ink leading-tight">{messages}<span class="text-xs text-muted font-bold ml-0.5">chat</span> hari ini</p>
        </div>
        <span class="live-dot relative w-1.5 h-1.5 rounded-full bg-green ml-auto anim-pulse"></span>
    </div>
</div>

<style>
    .hv-card { opacity: 0; transform: translateY(20px); }
    .is-mounted .hv-card { animation: cardIn 0.7s cubic-bezier(0.22, 1, 0.36, 1) forwards; }
    @keyframes cardIn { to { opacity: 1; transform: translateY(0); } }

    .bg-grid {
        background-image: radial-gradient(circle at 1px 1px, rgba(15,30,61,0.06) 1px, transparent 0);
        background-size: 16px 16px;
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

    .anim-pop { animation: pop 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) 1.2s backwards; }
    @keyframes pop {
        0% { transform: scale(0); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }

    .hv-float { animation: floatNotif 6s ease-in-out infinite; }
    .hv-float-1 { animation-delay: 0.4s; }
    .hv-float-2 { animation-delay: 1.4s; }
    .hv-float-3 { animation-delay: 2.2s; }
    @keyframes floatNotif {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }

    .cta-shine::after {
        content: ''; position: absolute; inset: 0;
        background: linear-gradient(110deg, transparent 25%, rgba(255,255,255,0.5) 50%, transparent 75%);
        transform: translateX(-100%);
        animation: shine 3s linear infinite;
    }
    @keyframes shine {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(150%); }
    }

    .anim-float { animation: floatY 7s ease-in-out infinite; }
    @keyframes floatY {
        0%, 100% { transform: translateY(0) rotate(0); }
        50% { transform: translateY(-12px) rotate(3deg); }
    }

    @media (prefers-reduced-motion: reduce) {
        .hv-card, .is-mounted .hv-card { animation: none; opacity: 1; transform: none; }
        .hv-float, .anim-float, .anim-pop, .anim-pulse, .live-dot::after, .cta-shine::after { animation: none; }
    }
</style>
