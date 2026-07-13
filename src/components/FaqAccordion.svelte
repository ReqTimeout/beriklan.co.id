<script>
    import { slide } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';

    export let items = [];

    let openIdx = -1;
    function toggle(i) {
        openIdx = openIdx === i ? -1 : i;
    }
</script>

<div class="reveal-stagger max-w-3xl mx-auto space-y-3">
    {#each items as item, i}
        <div class="faq-item bg-white border border-gray-100 rounded-xl overflow-hidden shadow-soft transition-all duration-300 hover:shadow-pop hover:border-accent/30">
            <button
                type="button"
                on:click={() => toggle(i)}
                class="w-full text-left px-5 md:px-6 py-5 flex items-center justify-between gap-4 group"
                aria-expanded={openIdx === i}
            >
                <span class="font-display font-bold text-base md:text-lg text-ink group-hover:text-accent transition-colors leading-snug">
                    {item.q}
                </span>
                <span class="faq-toggle shrink-0 w-8 h-8 rounded-full bg-soft flex items-center justify-center group-hover:bg-accent group-hover:text-ink transition-all">
                    <svg class="w-4 h-4 transition-transform duration-300" class:rotate-45={openIdx === i} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"/>
                    </svg>
                </span>
            </button>
            {#if openIdx === i}
                <div transition:slide={{ duration: 250, easing: quintOut }}>
                    <div class="px-5 md:px-6 pb-5 pt-0 text-muted leading-relaxed text-sm md:text-base border-t border-gray-50">
                        <p class="pt-4">{item.a}</p>
                    </div>
                </div>
            {/if}
        </div>
    {/each}
</div>

<style>
    @media (prefers-reduced-motion: reduce) {
        :global(.faq-item) { transition: none; }
    }
</style>
