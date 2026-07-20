<script>
    import { Filter, X, Calendar, Clock, ArrowRight, ArrowLeft } from 'lucide-svelte';
    import { onMount } from 'svelte';
    import { getFeaturedImage } from '../utils/featured_image.js';

    let activeCategory = 'all';
    let allPosts = [];
    let loaded = false;
    let rootEl;

    // Cluster mode: when visited via /blog/?tag=<T>&service=<S> (pillar cluster links)
    let clusterMode = false;
    let clusterMeta = null;   // { tag, service, title, desc, pillarHref, serviceName }
    let clusterPosts = [];

    const SERVICE_NAME = {
        'jasa-digital-marketing': 'Digital Marketing',
        'jasa-iklan-facebook': 'Iklan Facebook',
        'jasa-iklan-instagram': 'Iklan Instagram',
        'jasa-iklan-tiktok': 'Iklan TikTok',
        'jasa-iklan-google': 'Iklan Google Ads',
        'jasa-iklan-youtube': 'Iklan YouTube',
        'jasa-kelola-instagram': 'Kelola Instagram',
        'jasa-kelola-tiktok': 'Kelola TikTok',
        'jasa-pembuatan-website': 'Pembuatan Website',
        'jasa-pembuatan-landing-page': 'Landing Page',
    };

    function getImage(post) {
        return getFeaturedImage(post);
    }
    function imgFallback(slug) {
        return `https://picsum.photos/seed/beriklan-f-${slug}/600/400`;
    }
    function onImgError(e, slug) {
        e.target.onerror = null;
        e.target.src = imgFallback(slug);
    }

    onMount(async () => {
        try {
            // Detect pillar cluster params
            const params = new URLSearchParams(window.location.search);
            const tag = params.get('tag');
            const service = params.get('service');
            if (tag && service) {
                const res = await fetch('/data/clusters.json');
                if (res.ok) {
                    const clusters = await res.json();
                    const cd = clusters[service] && clusters[service][tag];
                    if (cd) {
                        clusterMode = true;
                        clusterMeta = {
                            tag, service,
                            title: cd.title || tag,
                            desc: cd.desc || '',
                            serviceName: SERVICE_NAME[service] || service,
                            pillarHref: `/${service}/pilar/`,
                        };
                        clusterPosts = cd.posts || [];
                        loaded = true;
                        return;
                    }
                }
            }
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
        // In-component reveal observer (BlogFilter is client:only, so the global
        // observer in Layout.astro never sees these elements at page load).
        if (typeof IntersectionObserver !== 'undefined') {
            document.documentElement.classList.add('js-reveal-ready');
            const setup = () => {
                const els = (rootEl ? rootEl.querySelectorAll('.reveal-stagger') : document.querySelectorAll('.reveal-stagger'));
                if (!els.length) return;
                const io = new IntersectionObserver((entries) => {
                    for (const e of entries) {
                        if (e.isIntersecting) {
                            e.target.classList.add('revealed');
                            io.unobserve(e.target);
                        }
                    }
                }, { threshold: 0.05, rootMargin: '0px 0px -40px 0px' });
                els.forEach(el => io.observe(el));
            };
            requestAnimationFrame(setup);
            // Safety net: reveal everything after 1.2s in case observer never fires
            setTimeout(() => {
                const els = (rootEl ? rootEl.querySelectorAll('.reveal-stagger') : document.querySelectorAll('.reveal-stagger'));
                els.forEach(el => el.classList.add('revealed'));
            }, 1200);
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
    {#if clusterMode && clusterMeta}
        <!-- ====================== CLUSTER VIEW (pillar cluster) ====================== -->
        <a href={clusterMeta.pillarHref} class="inline-flex items-center gap-1.5 text-sm font-bold text-muted hover:text-accent transition-colors mb-6">
            <ArrowLeft class="w-4 h-4" />
            Kembali ke Panduan {clusterMeta.serviceName}
        </a>
        <div class="mb-2 inline-flex items-center gap-2 px-3 py-1.5 bg-accent/10 text-accent text-[11px] font-bold uppercase tracking-wider rounded-full">
            Cluster · {clusterMeta.serviceName}
        </div>
        <h1 class="font-display font-extrabold text-3xl md:text-4xl text-ink leading-[1.1] tracking-tight mb-3">
            {clusterMeta.title}
        </h1>
        {#if clusterMeta.desc}
            <p class="text-base md:text-lg text-muted leading-relaxed max-w-2xl mb-3">{clusterMeta.desc}</p>
        {/if}
        <p class="text-sm text-muted mb-8">
            {clusterPosts.length} artikel terkait {clusterMeta.serviceName.toLowerCase()}. Semua dibahas dari pengalaman mengelola campaign sejak 2016.
        </p>

        {#if clusterPosts.length > 0}
            <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5 reveal-stagger" data-reveal-stagger>
                {#each clusterPosts as post, i}
                    <a href={`/blog/${post.slug}`} class="grid-card group" style={`animation-delay:${i * 60}ms;`}>
                        <div class="p-6">
                            <div class="flex items-center gap-3 text-[10px] text-muted mb-2">
                                <span class="flex items-center gap-1"><Calendar class="w-3 h-3" /> {post.date}</span>
                                <span class="flex items-center gap-1"><Clock class="w-3 h-3" /> {post.readTime}</span>
                            </div>
                            <h4 class="font-display font-bold text-base text-ink mb-2 leading-snug group-hover:text-accent transition-colors line-clamp-2">{post.title}</h4>
                            <p class="text-xs text-muted leading-relaxed line-clamp-3">{post.excerpt}</p>
                            <span class="mt-4 inline-flex items-center gap-1.5 text-xs font-bold text-ink group-hover:text-accent transition-colors">
                                Baca selengkapnya
                                <ArrowRight class="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                            </span>
                        </div>
                    </a>
                {/each}
            </div>
        {:else}
            <div class="text-center py-12 border border-dashed border-gray-200 rounded-2xl">
                <p class="text-muted">Belum ada artikel khusus untuk cluster ini. Kembali ke panduan untuk topik lain.</p>
            </div>
        {/if}

        <div class="mt-12 text-center">
            <a href={clusterMeta.pillarHref} class="group inline-flex items-center justify-center gap-2 bg-ink text-white px-7 py-3.5 rounded-full font-bold shadow-pop hover:shadow-lg transition-all">
                <span class="flex items-center gap-2">
                    Lihat Panduan Lengkap {clusterMeta.serviceName}
                    <ArrowRight class="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </span>
            </a>
        </div>
    {:else}
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
                    onclick={() => activeCategory = cat.id}
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
            <div class="grid md:grid-cols-3 gap-5 reveal-stagger" data-reveal-stagger>
                {#each featuredPosts as post}
                    <a href="/blog/{post.slug}" class="featured-card group">
                        <div class="featured-thumb">
                            <img src={getImage(post)} alt={post.title} class="absolute inset-0 w-full h-full object-cover" loading="lazy" onerror={(e) => onImgError(e, post.slug)} />
                            <div class="absolute inset-0 bg-gradient-to-t from-ink/40 via-transparent to-transparent"></div>
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
<div bind:this={rootEl}>
            <h3 class="text-xs font-bold uppercase tracking-wider text-muted mb-4">Artikel Lainnya</h3>
                    <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5 reveal-stagger" data-reveal-stagger>
                        {#each gridPosts as post}
                            <a href="/blog/{post.slug}" class="grid-card group">
                                <div class="grid-thumb">
                                    <img src={getImage(post)} alt={post.title} class="absolute inset-0 w-full h-full object-cover" loading="lazy" onerror={(e) => onImgError(e, post.slug)} />
                                </div>
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
    <!-- /clusterMode else -->
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
