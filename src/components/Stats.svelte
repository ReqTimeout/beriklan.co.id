<script>
    import { onMount } from 'svelte';
    import { Handshake, Wallet, Zap, Clock, TrendingUp } from 'lucide-svelte';

    // Klaim yang aman, terukur, dan tidak over-promise
    const stats = [
        {
            value: 9,
            suffix: ' tahun',
            label: 'Pengalaman tim',
            sub: 'performance marketing',
            Icon: Clock,
            color: 'amber',
        },
        {
            value: 12,
            suffix: '+',
            label: 'Sektor industri',
            sub: 'F&B, klinik, SaaS, retail',
            Icon: Handshake,
            color: 'teal',
        },
        {
            value: 7,
            suffix: '',
            label: 'Channel terkelola',
            sub: 'Meta, Google, TikTok, YouTube',
            Icon: TrendingUp,
            color: 'amber',
        },
        {
            value: 24,
            suffix: '/7',
            label: 'Monitoring campaign',
            sub: 'dashboard real-time',
            Icon: Zap,
            color: 'teal',
        },
    ];

    let counters = stats.map((s) => {
        const baseline = 0.7;
        if (s.decimals) return +(s.value * baseline).toFixed(s.decimals);
        return Math.round(s.value * baseline);
    });
    let visible = false;
    let hasAnimated = false;

    const colorMap = {
        amber: { ring: 'ring-accent/30', glow: 'bg-accent/20', text: 'text-accent' },
        teal: { ring: 'ring-teal/30', glow: 'bg-teal/20', text: 'text-teal' },
    };

    function runCounter() {
        if (hasAnimated) return;
        hasAnimated = true;
        visible = true;
        const start = performance.now();
        const duration = 1600;
        const baseline = 0.7;
        function tick(now) {
            const t = Math.min((now - start) / duration, 1);
            const ease = 1 - Math.pow(1 - t, 3);
            const factor = baseline + (1 - baseline) * ease;
            counters = stats.map((s) => {
                const v = s.value * factor;
                return s.decimals ? +v.toFixed(s.decimals) : Math.round(v);
            });
            if (t < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    }

    onMount(() => {
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                runCounter();
                observer.disconnect();
            }
        }, { threshold: 0.1 });
        const el = document.getElementById('stats');
        if (el) observer.observe(el);
        setTimeout(runCounter, 800);
    });
</script>

<section id="stats" class="py-16 md:py-20 bg-soft relative overflow-hidden">
    <div class="container mx-auto px-6 relative">
        <!-- Header -->
        <div class="text-center max-w-xl mx-auto mb-10 reveal">
            <p class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-accent mb-3">
                <span class="w-6 h-px bg-accent"></span>
                Singkatnya
                <span class="w-6 h-px bg-accent"></span>
            </p>
            <h2 class="font-display font-extrabold text-2xl md:text-3xl text-ink leading-tight">
                Empat angka yang paling sering ditanyakan calon klien.
            </h2>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 max-w-5xl mx-auto reveal-stagger">
            {#each stats as stat, i}
                {@const c = colorMap[stat.color]}
                <div
                    class="group relative bg-white rounded-2xl p-5 md:p-6 border border-gray-100 hover:border-accent/40 hover:-translate-y-0.5 transition-all duration-300 shadow-soft hover:shadow-pop"
                    style="transition-delay: {i * 100}ms;"
                >
                    <!-- Subtle color glow on hover -->
                    <div class="absolute -top-8 -right-8 w-24 h-24 {c.glow} rounded-full blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

                    <div class="relative">
                        <!-- Icon + value -->
                        <div class="flex items-center justify-between mb-3">
                            <div class="w-9 h-9 rounded-lg bg-{stat.color === 'amber' ? 'accent' : 'teal'}/10 {c.text} flex items-center justify-center">
                                <svelte:component this={stat.Icon} size="18" strokeWidth="2" />
                            </div>
                        </div>

                        <div class="flex items-baseline gap-0.5">
                            <span class="text-3xl md:text-4xl font-display font-extrabold text-ink tracking-tight tabular-nums">
                                {counters[i]}
                            </span>
                            <span class="text-lg md:text-xl font-display font-extrabold {c.text}">{stat.suffix}</span>
                        </div>
                        <p class="font-bold text-ink text-sm mt-2 leading-tight">{stat.label}</p>
                        <p class="text-muted text-[11px] mt-0.5">{stat.sub}</p>
                    </div>
                </div>
            {/each}
        </div>

        <!-- Subtle footnote -->
        <p class="text-center text-[11px] text-muted/70 mt-6">
            * Data internal berdasarkan portfolio pengelolaan campaign sejak 2016.
        </p>
    </div>
</section>
