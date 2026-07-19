<script>
    import { ArrowRight, BookOpen } from 'lucide-svelte';

    export let items = [];
    export let title = 'Layanan yang sering dipilih bersamaan';
    export let subtitle = 'Bisnis yang efektif biasanya menjalankan iklan di 2-3 kanal sekaligus agar saling menguatkan.';
    export let pillarHref = '';
    export let pillarLabel = 'Panduan Lengkap';
</script>

<section class="py-20 md:py-24 bg-white relative overflow-hidden">
    <div class="absolute inset-0 opacity-30 pointer-events-none" style="background-image: radial-gradient(circle at 1px 1px, rgba(15,30,61,0.05) 1px, transparent 0); background-size: 32px 32px;"></div>

    <div class="container mx-auto px-6 relative">
        <div class="text-center max-w-2xl mx-auto mb-12 reveal">
            <p class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-accent">
                <span class="w-8 h-px bg-accent"></span>
                Saling Melengkapi
                <span class="w-8 h-px bg-accent"></span>
            </p>
            <h2 class="font-display font-extrabold text-3xl md:text-4xl text-ink leading-[1.1] tracking-tight mt-3">
                {title}
            </h2>
            <p class="mt-4 text-muted max-w-xl mx-auto text-base leading-relaxed">
                {subtitle}
            </p>
        </div>

        <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5 max-w-5xl mx-auto reveal-stagger">
            {#each items as item, i}
                <a
                    href={item.href}
                    class="group relative bg-white rounded-2xl p-6 border border-gray-100 hover:border-accent/40 transition-all duration-300 hover:-translate-y-1 hover:shadow-pop overflow-hidden"
                    style="animation-delay: {i * 80}ms;"
                >
                    <div class="absolute -right-8 -top-8 w-32 h-32 bg-accent/5 rounded-full blur-2xl group-hover:bg-accent/15 transition-colors duration-500"></div>
                    <div class="relative">
                        <div class="w-12 h-12 rounded-xl bg-soft group-hover:bg-accent/15 flex items-center justify-center text-2xl mb-4 transition-colors">
                            {item.icon || '🎯'}
                        </div>
                        <h3 class="font-display font-bold text-lg text-ink mb-1.5">{item.label}</h3>
                        <p class="text-sm text-muted leading-relaxed">{item.desc}</p>
                        <div class="mt-4 inline-flex items-center gap-1.5 text-xs font-bold text-ink group-hover:text-accent transition-colors">
                            Lihat detail
                            <ArrowRight class="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                        </div>
                    </div>
                </a>
                {/each}

                {#if pillarHref}
                    <a
                        href={pillarHref}
                        class="group relative bg-gradient-to-br from-primary to-primary-2 rounded-2xl p-6 border border-white/10 hover:border-accent/40 transition-all duration-300 hover:-translate-y-1 hover:shadow-pop overflow-hidden"
                    >
                        <div class="absolute -right-8 -top-8 w-32 h-32 bg-accent/10 rounded-full blur-2xl group-hover:bg-accent/20 transition-colors duration-500"></div>
                        <div class="relative">
                            <div class="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center text-2xl mb-4 transition-colors">
                                <BookOpen class="w-6 h-6 text-white" />
                            </div>
                            <h3 class="font-display font-bold text-lg text-white mb-1.5">{pillarLabel}</h3>
                            <p class="text-sm text-white/70 leading-relaxed">Strategi, format iklan, optimasi budget, dan cara ukur ROI — dibahas tuntas.</p>
                            <div class="mt-4 inline-flex items-center gap-1.5 text-xs font-bold text-accent group-hover:text-white transition-colors">
                                Baca panduan
                                <ArrowRight class="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                            </div>
                        </div>
                    </a>
                {/if}
            </div>
        </div>
    </section>
