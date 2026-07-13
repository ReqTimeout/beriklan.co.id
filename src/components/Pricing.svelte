<script>
    import { Star } from 'lucide-svelte';

    let billingCycle = 'monthly'; // or 'yearly'

    const tiers = [
        {
            name: 'Starter',
            tag: 'Untuk UMKM baru mulai testing',
            monthlyPrice: '2.500.000',
            yearlyPrice: '2.000.000',
            suffix: '/ bulan',
            cta: 'Mulai Starter',
            featured: false,
            features: [
                '1 platform iklan (Meta atau Google)',
                '2 campaign aktif',
                'Laporan mingguan via WhatsApp',
                '1x call review bulanan',
                'Setup Meta Pixel gratis',
            ],
            accent: 'from-blue-500 to-cyan-500',
        },
        {
            name: 'Growth',
            tag: 'Paling populer — sudah PMF, siap scale',
            monthlyPrice: '5.000.000',
            yearlyPrice: '4.000.000',
            suffix: '/ bulan',
            cta: 'Pilih Growth',
            featured: true,
            features: [
                '2 platform iklan (Meta + Google, atau Meta + TikTok)',
                '4 campaign aktif',
                'Landing page support',
                'Laporan mingguan + dashboard',
                '2x call review bulanan',
                'A/B testing rutin',
                'Creative refresh tiap bulan',
            ],
            accent: 'from-accent to-orange-600',
        },
        {
            name: 'Scale',
            tag: 'Untuk bisnis 50jt+ budget iklan',
            monthlyPrice: '10.000.000+',
            yearlyPrice: '8.000.000+',
            suffix: '/ bulan',
            cta: 'Konsultasi Custom',
            featured: false,
            features: [
                'Full funnel (awareness → conversion → retention)',
                'Multi-platform (Meta, Google, TikTok, YouTube)',
                'Creative production in-house',
                'Dedicated account manager',
                'Weekly review + monthly strategic call',
                'Custom dashboard & reporting',
                'Priority support 24/7',
            ],
            accent: 'from-purple-500 to-pink-500',
        },
    ];
</script>

<section id="harga" class="py-20 md:py-28 bg-white relative overflow-hidden">
    <div class="absolute inset-0 opacity-30 pointer-events-none">
        <div class="absolute top-32 left-1/4 w-72 h-72 bg-accent/5 rounded-full blur-3xl"></div>
    </div>

    <div class="container mx-auto px-6 relative">
        <div class="text-center max-w-2xl mx-auto mb-10">
            <p class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-accent mb-4">
                <span class="w-8 h-px bg-accent"></span>
                Harga
                <span class="w-8 h-px bg-accent"></span>
            </p>
            <h2 class="font-display font-extrabold text-3xl md:text-5xl text-ink leading-[1.15] tracking-tight">
                Transparan. Tanpa hidden fee.
                <span class="block mt-2 text-accent">Pilih paket yang pas.</span>
            </h2>
            <p class="mt-5 text-muted text-base md:text-lg leading-relaxed">
                Minimum contract 1 bulan. Bisa cancel kapan saja. Custom sesuai kebutuhan.
            </p>
        </div>

        <!-- Billing toggle -->
        <div class="flex items-center justify-center gap-3 mb-12">
            <button
                type="button"
                on:click={() => billingCycle = 'monthly'}
                class="px-5 py-2 rounded-full text-sm font-bold transition-all {billingCycle === 'monthly' ? 'bg-ink text-white shadow-md' : 'bg-soft text-muted hover:text-ink'}"
            >
                Bulanan
            </button>
            <button
                type="button"
                on:click={() => billingCycle = 'yearly'}
                class="px-5 py-2 rounded-full text-sm font-bold transition-all flex items-center gap-2 {billingCycle === 'yearly' ? 'bg-ink text-white shadow-md' : 'bg-soft text-muted hover:text-ink'}"
            >
                Tahunan
                <span class="text-[10px] bg-green text-white px-2 py-0.5 rounded-full">Hemat 20%</span>
            </button>
        </div>

        <!-- Tier cards -->
        <div class="grid md:grid-cols-3 gap-5 lg:gap-6 max-w-6xl mx-auto">
            {#each tiers as tier, i}
                <div class="relative rounded-3xl p-7 md:p-8 border transition-all duration-500 hover:-translate-y-2
                    {tier.featured ? 'bg-gradient-to-br from-ink to-primary-2 text-white border-accent shadow-pop scale-100 md:scale-105 z-10' : 'bg-white border-gray-100 shadow-soft hover:shadow-pop'}"
                >
                    {#if tier.featured}
                        <div class="absolute -top-3 left-1/2 -translate-x-1/2 bg-accent text-ink text-[10px] font-bold uppercase tracking-wider px-4 py-1.5 rounded-full shadow-md flex items-center gap-1.5">
                            <Star size="12" strokeWidth="2.5" fill="currentColor" />
                            Paling Populer
                        </div>
                    {/if}

                    <div class="mb-6">
                        <h3 class="font-display font-extrabold text-2xl mb-2 {tier.featured ? 'text-white' : 'text-ink'}">{tier.name}</h3>
                        <p class="text-xs {tier.featured ? 'text-white/70' : 'text-muted'}">{tier.tag}</p>
                    </div>

                    <!-- Price -->
                    <div class="mb-6 pb-6 border-b {tier.featured ? 'border-white/10' : 'border-gray-100'}">
                        <div class="flex items-baseline gap-1 flex-wrap">
                            <span class="text-xs font-bold {tier.featured ? 'text-white/60' : 'text-muted'}">Rp</span>
                            <span class="text-4xl md:text-5xl font-display font-extrabold tracking-tight {tier.featured ? 'text-accent' : 'text-ink'}">
                                {billingCycle === 'monthly' ? tier.monthlyPrice : tier.yearlyPrice}
                            </span>
                        </div>
                        <p class="text-xs {tier.featured ? 'text-white/50' : 'text-muted'} mt-1">{tier.suffix}</p>
                    </div>

                    <!-- Features -->
                    <ul class="space-y-3 mb-8">
                        {#each tier.features as f}
                            <li class="flex items-start gap-2 text-sm {tier.featured ? 'text-white/85' : 'text-muted'}">
                                <span class="w-5 h-5 rounded-full {tier.featured ? 'bg-accent/20 text-accent' : 'bg-accent/10 text-accent'} flex items-center justify-center shrink-0 mt-0.5">
                                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                                </span>
                                <span>{f}</span>
                            </li>
                        {/each}
                    </ul>

                    <!-- CTA -->
                    <a
                        href="/jasa-digital-marketing"
                        target="_blank"
                        rel="noopener"
                        class="block w-full text-center py-3 rounded-full font-bold text-sm transition-all
                        {tier.featured ? 'bg-accent text-ink hover:bg-accent-2 hover:shadow-lg' : 'bg-ink text-white hover:bg-accent hover:text-ink'}"
                    >
                        {tier.cta}
                    </a>
                </div>
            {/each}
        </div>

        <!-- Custom note -->
        <p class="text-center text-sm text-muted mt-10">
            Mau lihat detail layanan lengkap atau paket custom? 
            <a href="/jasa-digital-marketing" class="text-accent font-bold hover:underline">Lihat detail layanan →</a>
        </p>
    </div>
</section>
