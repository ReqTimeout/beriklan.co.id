<script>
    import { Filter, X, Calendar, Clock, ArrowRight } from 'lucide-svelte';
    import { onMount } from 'svelte';

    let activeCategory = 'all';
    let allPosts = [];
    let loaded = false;

    onMount(async () => {
        try {
            const res = await fetch('/data/posts-index.json');
            if (res.ok) {
                const data = await res.json();
                // Take 24 most recent for the blog index
                allPosts = data.slice(0, 24);
                loaded = true;
            }
        } catch (e) {
            console.warn('Failed to load posts:', e);
            loaded = true;
        }
    });

    const categories = [
        { id: 'all', label: 'Semua Topik' },
        { id: 'meta', label: 'Facebook & Instagram' },
        { id: 'tiktok', label: 'TikTok' },
        { id: 'google', label: 'Google Ads' },
        { id: 'youtube', label: 'YouTube' },
        { id: 'strategy', label: 'Strategi' },
        { id: 'case-study', label: 'Studi Kasus' },
    ];

    $: filteredPosts = activeCategory === 'all' ? allPosts : allPosts.filter(p => p.category === activeCategory);
    $: featuredPosts = filteredPosts.filter(p => p.featured);
    $: gridPosts = filteredPosts.filter(p => !p.featured);
</script>

<div>
    <!-- Filter chips -->
    <div class="mb-10">
        <div class="flex items-center gap-2 mb-3">
            <Filter class="w-4 h-4 text-muted" />
            <span class="text-xs font-bold uppercase tracking-wider text-muted">Filter Topik:</span>
        </div>
        <div class="flex flex-wrap gap-2">
            {#each categories as cat}
                <button
                    type="button"
                    on:click={() => activeCategory = cat.id}
                    class="px-4 py-2 rounded-full text-xs font-bold transition-all {activeCategory === cat.id ? 'bg-ink text-white' : 'bg-white text-ink border border-gray-200 hover:border-ink'}"
                >
                    {cat.label}
                </button>
            {/each}
        </div>
    </div>

    <!-- Featured posts -->
    {#if featuredPosts.length > 0}
        <div class="mb-10">
            <h3 class="text-xs font-bold uppercase tracking-wider text-muted mb-4">Featured</h3>
            <div class="grid md:grid-cols-3 gap-5 reveal-stagger">
                {#each featuredPosts as post}
                    <a href="/blog/{post.slug}" class="featured-card group">
                        <div class="featured-thumb">
                            {#if post.featuredImage}
                                <img src={post.featuredImage} alt={post.title} class="absolute inset-0 w-full h-full object-cover" loading="lazy" />
                                <div class="absolute inset-0 bg-gradient-to-t from-ink/40 via-transparent to-transparent"></div>
                            {:else}
                                <div class="absolute inset-0 bg-gradient-to-br from-primary-2/30 via-accent/20 to-teal/30"></div>
                            {/if}
                            <span class="absolute top-3 left-3 px-2 py-1 bg-accent text-ink text-[10px] font-bold uppercase tracking-wider rounded">Featured</span>
                        </div>
                        <div class="p-5">
                            <div class="flex items-center gap-3 text-[10px] text-muted mb-2">
                                <span class="flex items-center gap-1"><Calendar class="w-3 h-3" /> {post.date}</span>
                                <span class="flex items-center gap-1"><Clock class="w-3 h-3" /> {post.readTime}</span>
                            </div>
                            <h4 class="font-display font-extrabold text-lg text-ink leading-tight mb-2 group-hover:text-accent transition-colors line-clamp-2">{post.title}</h4>
                            <p class="text-xs text-muted leading-relaxed line-clamp-2">{post.excerpt}</p>
                            <span class="mt-3 inline-flex items-center gap-1 text-xs font-bold text-ink group-hover:text-accent transition-colors">
                                Baca selengkapnya <ArrowRight class="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                            </span>
                        </div>
                    </a>
                {/each}
            </div>
        </div>
    {/if}

    <!-- Grid posts -->
    {#if gridPosts.length > 0}
        <div>
            <h3 class="text-xs font-bold uppercase tracking-wider text-muted mb-4">Artikel Lainnya</h3>
            <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5 reveal-stagger">
                {#each gridPosts as post}
                    <a href="/blog/{post.slug}" class="grid-card group">
                        {#if post.featuredImage}
                            <div class="grid-thumb">
                                <img src={post.featuredImage} alt={post.title} class="absolute inset-0 w-full h-full object-cover" loading="lazy" />
                            </div>
                        {/if}
                        <div class="p-5">
                            <span class="inline-block px-2 py-0.5 bg-soft text-ink text-[10px] font-bold uppercase tracking-wider rounded mb-3">{categories.find(c => c.id === post.category)?.label}</span>
                            <h4 class="font-display font-bold text-base text-ink leading-tight mb-2 group-hover:text-accent transition-colors line-clamp-2">{post.title}</h4>
                            <p class="text-xs text-muted leading-relaxed line-clamp-3">{post.excerpt}</p>
                            <div class="flex items-center gap-3 mt-3 text-[10px] text-muted">
                                <span class="flex items-center gap-1"><Calendar class="w-3 h-3" /> {post.date}</span>
                                <span class="flex items-center gap-1"><Clock class="w-3 h-3" /> {post.readTime}</span>
                            </div>
                        </div>
                    </a>
                {/each}
            </div>
        </div>
    {:else if filteredPosts.length === 0}
        <div class="text-center py-12">
            <p class="text-muted">Tidak ada artikel dalam topik ini. Coba topik lain.</p>
        </div>
    {/if}
</div>

<style>
    .featured-card {
        background: white;
        border: 1px solid #f1f3f8;
        border-radius: 1.25rem;
        overflow: hidden;
        transition: all 0.3s ease;
        display: block;
    }
    .featured-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px -8px rgba(15,30,61,0.15);
        border-color: #f59e0b;
    }
    .featured-thumb {
        position: relative;
        aspect-ratio: 16/9;
        overflow: hidden;
    }
    .featured-thumb::after {
        content: '';
        position: absolute; inset: 0;
        background: linear-gradient(180deg, transparent 60%, rgba(0,0,0,0.05) 100%);
    }

    .grid-card {
        background: white;
        border: 1px solid #f1f3f8;
        border-radius: 1.25rem;
        overflow: hidden;
        transition: all 0.3s ease;
        display: block;
    }
    .grid-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px -8px rgba(15,30,61,0.15);
        border-color: #f59e0b;
    }
    .grid-thumb {
        position: relative;
        aspect-ratio: 16/9;
        overflow: hidden;
    }
    .grid-thumb img {
        transition: transform 0.4s cubic-bezier(0.22, 1, 0.36, 1);
    }
    .grid-card:hover .grid-thumb img {
        transform: scale(1.04);
    }

    .line-clamp-2 {
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .line-clamp-3 {
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
</style>
