<script>
    export let items = [];
</script>

<div class="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-5 reveal-stagger">
    {#each items as item, i}
        <div class="step-card group" style="animation-delay: {i * 100}ms;">
            <div class="flex items-center justify-between mb-4">
                <span class="text-[10px] font-bold uppercase tracking-widest text-muted">{item.num}</span>
                <span class="text-[9px] font-bold uppercase tracking-wider text-accent bg-accent/10 px-2 py-0.5 rounded-full">{item.tag}</span>
            </div>
            <h3 class="font-display font-extrabold text-lg text-ink mb-2">{item.title}</h3>
            <p class="text-sm text-muted leading-relaxed">{item.desc}</p>
        </div>
    {/each}
</div>

<style>
    .step-card {
        background: white;
        border-radius: 1.25rem;
        padding: 1.5rem;
        border: 1px solid #f1f3f8;
        transition: all 0.3s ease;
    }
    .step-card:hover {
        border-color: #f59e0b;
        transform: translateY(-4px);
        box-shadow: 0 12px 40px -8px rgba(15,30,61,0.15);
    }
</style>
