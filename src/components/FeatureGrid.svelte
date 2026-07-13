<script>
    import { Target, Repeat, MapPin, Database, Users, MessageCircle, Sparkles, TrendingUp, BarChart3, Camera, Video, Music, ShoppingBag, Smartphone, Search, Eye, Heart } from 'lucide-svelte';

    const iconMap = { Target, Repeat, MapPin, Database, Users, MessageCircle, Sparkles, TrendingUp, BarChart3, Camera, Video, Music, ShoppingBag, Smartphone, Search, Eye, Heart };

    export let items = [];
</script>

<div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5 max-w-6xl mx-auto reveal-stagger">
    {#each items as item, i}
        <div class="feature-card group" style="animation-delay: {i * 80}ms;">
            <div class="feature-icon">
                {#if iconMap[item.iconName]}
                    <svelte:component this={iconMap[item.iconName]} size="22" strokeWidth="2" />
                {/if}
            </div>
            <h3 class="feature-title">{item.title}</h3>
            <p class="feature-desc">{item.desc}</p>
        </div>
    {/each}
</div>

<style>
    .feature-card {
        background: white;
        border-radius: 1.25rem;
        padding: 1.5rem;
        border: 1px solid #f1f3f8;
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        border-color: #f59e0b;
        transform: translateY(-4px);
        box-shadow: 0 12px 40px -8px rgba(15,30,61,0.15);
    }
    .feature-card:hover .feature-icon { background: #f59e0b; color: #0b1426; transform: rotate(-6deg) scale(1.05); }
    .feature-icon {
        width: 3rem; height: 3rem;
        border-radius: 0.75rem;
        background: #0b1426;
        color: white;
        display: flex; align-items: center; justify-content: center;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .feature-title { font-family: 'Plus Jakarta Sans Variable', sans-serif; font-weight: 800; font-size: 1.0625rem; color: #0b1426; margin-bottom: 0.4rem; }
    .feature-desc { font-size: 0.875rem; color: #5b6478; line-height: 1.6; }
</style>
