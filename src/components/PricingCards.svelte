<script>
    import { Check, Sparkles, MessageCircle } from 'lucide-svelte';

    export let tiers = [];
    export let pageSlug = '';
    export let highlightIndex = -1;
    export let columns = 2; // 1, 2, 3, or 4

    const baseWa = 'https://wa.me/62811919328';

    function buildWaLink(tier) {
        const msg = encodeURIComponent(
            `Halo Beriklan, saya tertarik dengan paket ${tier.name} (${pageSlug}) — Rp ${tier.priceLabel}. Mohon info lebih lanjut.`
        );
        return `${baseWa}?text=${msg}`;
    }

    // Grid classes — handles 1/2/3/4 columns cleanly
    $: gridCols = columns === 1
        ? 'grid-cols-1 max-w-xl'
        : columns === 3
        ? 'md:grid-cols-3 max-w-6xl'
        : columns === 4
        ? 'md:grid-cols-2 lg:grid-cols-4 max-w-7xl'
        : 'md:grid-cols-2 max-w-4xl';
</script>

<div class="grid gap-4 md:gap-6 {gridCols} mx-auto reveal-stagger">
    {#each tiers as tier, i}
        {@const isHighlight = i === highlightIndex || tier.highlight}
        <div
            data-tier={tier.name}
            data-price={tier.priceLabel}
            class="pricing-card relative rounded-2xl p-7 md:p-8 transition-all duration-300 border-2 {isHighlight ? 'border-accent bg-white shadow-pop md:scale-[1.02]' : 'border-gray-100 bg-white hover:border-gray-300 hover:shadow-soft'}"
        >
            {#if isHighlight}
                <div class="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-accent to-accent-2 text-ink text-[10px] font-bold uppercase tracking-widest rounded-full shadow-md flex items-center gap-1">
                    <Sparkles class="w-3 h-3" />
                    Rekomendasi Tim
                </div>
            {/if}

            <div class="flex items-baseline justify-between gap-3 mb-2">
                <h3 class="font-display font-extrabold text-[20px] md:text-[22px] leading-tight text-ink">{tier.name}</h3>
                {#if tier.duration}
                    <span class="shrink-0 text-[10px] font-bold uppercase tracking-wider text-muted bg-soft px-2 py-1 rounded-md">{tier.duration}</span>
                {/if}
            </div>

            <p class="text-[13px] md:text-sm text-muted leading-relaxed min-h-[40px]">{tier.tagline}</p>

            <div class="mt-5 mb-6 pb-6 border-b border-gray-100">
                <div class="flex items-baseline gap-1.5">
                    <span class="text-xs font-bold text-muted">Rp</span>
                    <span class="font-display font-extrabold text-[34px] md:text-[40px] text-ink leading-none tabular-nums">{tier.priceLabel}</span>
                </div>
                <p class="text-[11px] md:text-xs text-muted mt-2">{tier.priceNote || 'belum termasuk ad spend Meta'}</p>
            </div>

            <ul class="space-y-2.5 mb-7">
                {#each tier.features as feature}
                    <li class="flex items-start gap-2.5 text-[13px] md:text-sm text-ink leading-snug">
                        <span class="shrink-0 w-5 h-5 rounded-full {isHighlight ? 'bg-accent text-ink' : 'bg-soft text-accent'} flex items-center justify-center mt-0.5">
                            <Check class="w-3 h-3" strokeWidth="3" />
                        </span>
                        <span>{feature}</span>
                    </li>
                {/each}
            </ul>

            <a
                href={buildWaLink(tier)}
                target="_blank"
                rel="noopener"
                data-cta="pricing_whatsapp"
                data-package={tier.name}
                data-price={tier.priceLabel}
                data-service={pageSlug}
                data-cta-location="pricing_card"
                class="group w-full inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-full font-bold text-[13px] md:text-sm transition-all relative overflow-hidden {isHighlight ? 'bg-ink text-white hover:bg-accent hover:text-ink' : 'bg-white text-ink border-2 border-ink hover:bg-ink hover:text-white'}"
            >
                <span class="cta-shine absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity"></span>
                <span class="relative flex items-center gap-2">
                    <MessageCircle class="w-4 h-4" />
                    Diskusi via WhatsApp
                </span>
            </a>

            {#if tier.disclaimer}
                <p class="text-[10px] md:text-[11px] text-muted text-center mt-3 leading-relaxed">
                    {tier.disclaimer}
                </p>
            {/if}
        </div>
    {/each}
</div>

<style>
    .pricing-card {
        will-change: transform;
    }
    .pricing-card:hover {
        transform: translateY(-4px);
    }
    .pricing-card.is-highlight:hover {
        transform: translateY(-4px) scale(1.02);
    }
    .cta-shine {
        background: linear-gradient(110deg, transparent 25%, rgba(255,255,255,0.25) 50%, transparent 75%);
        transform: translateX(-100%);
        transition: opacity 0.3s ease;
    }
    .group:hover .cta-shine {
        animation: shine 0.8s ease forwards;
    }
    @keyframes shine {
        to { transform: translateX(100%); }
    }
    @media (prefers-reduced-motion: reduce) {
        .pricing-card, .pricing-card:hover, .pricing-card.is-highlight:hover { transform: none; }
        .group:hover .cta-shine { animation: none; }
    }
</style>
