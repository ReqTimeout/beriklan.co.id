<script>
    export let title = 'Tech Stack';
    export let subtitle = 'Teknologi yang kami pakai untuk membangun beriklan.co.id — dan yang kami rekomendasikan untuk klien.';
    export let mode = 'light'; // 'light' | 'dark'
</script>

<section class="py-20 md:py-28 {mode === 'dark' ? 'bg-ink text-white' : 'bg-soft'} relative overflow-hidden">
    <div class="container mx-auto px-6 relative">
        <div class="text-center max-w-2xl mx-auto mb-14 reveal">
            <p class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] {mode === 'dark' ? 'text-accent' : 'text-accent'}">
                <span class="w-8 h-px bg-accent"></span>
                {title}
                <span class="w-8 h-px bg-accent"></span>
            </p>
            <h2 class="font-display font-extrabold text-3xl md:text-5xl {mode === 'dark' ? 'text-white' : 'text-ink'} leading-[1.1] tracking-tight mt-3">
                Tools yang kami <span class="text-accent">percaya & gunakan</span>
            </h2>
            <p class="mt-4 {mode === 'dark' ? 'text-white/70' : 'text-muted'} max-w-2xl mx-auto text-base leading-relaxed">
                {subtitle}
            </p>
        </div>

        <!-- Frontend & Framework -->
        <div class="mb-10 reveal">
            <p class="text-[11px] font-bold uppercase tracking-[0.2em] {mode === 'dark' ? 'text-white/40' : 'text-muted'} mb-4 text-center">Frontend & Framework</p>
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 max-w-4xl mx-auto">
                {#each [
                    { name: 'Astro', slug: 'astro', note: 'Static site generator' },
                    { name: 'Svelte', slug: 'svelte', note: 'Islands interactivity' },
                    { name: 'Tailwind CSS', slug: 'tailwindcss', note: 'Utility-first styling' },
                    { name: 'TypeScript', slug: 'typescript', note: 'Type-safe code' },
                ] as tech}
                    <div class="tech-card group">
                        <div class="tech-icon">
                            <img src="/tech/{tech.slug}.svg" alt="{tech.name} logo" loading="lazy" width="40" height="40" class="tech-svg" />
                        </div>
                        <div class="tech-info">
                            <p class="tech-name">{tech.name}</p>
                            <p class="tech-note">{tech.note}</p>
                        </div>
                    </div>
                {/each}
            </div>
        </div>

        <!-- Hosting & Deployment -->
        <div class="mb-10 reveal">
            <p class="text-[11px] font-bold uppercase tracking-[0.2em] {mode === 'dark' ? 'text-white/40' : 'text-muted'} mb-4 text-center">Hosting & Deployment</p>
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-3 gap-3 max-w-3xl mx-auto">
                {#each [
                    { name: 'Cloudflare', slug: 'cloudflare', note: 'Edge network global' },
                    { name: 'GitHub', slug: 'github', note: 'Source control + CI/CD' },
                    { name: 'Render', slug: 'render', note: 'Alternatif deployment' },
                ] as tech}
                    <div class="tech-card group">
                        <div class="tech-icon">
                            <img src="/tech/{tech.slug}.svg" alt="{tech.name} logo" loading="lazy" width="40" height="40" class="tech-svg" />
                        </div>
                        <div class="tech-info">
                            <p class="tech-name">{tech.name}</p>
                            <p class="tech-note">{tech.note}</p>
                        </div>
                    </div>
                {/each}
            </div>
        </div>

        <!-- CMS / Content -->
        <div class="mb-10 reveal">
            <p class="text-[11px] font-bold uppercase tracking-[0.2em] {mode === 'dark' ? 'text-white/40' : 'text-muted'} mb-4 text-center">CMS & Content</p>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-4xl mx-auto">
                {#each [
                    { name: 'WordPress', slug: 'wordpress', note: 'Legacy import (blog)' },
                    { name: 'Sanity', slug: 'sanity', note: 'Headless CMS modern' },
                    { name: 'Webflow', slug: 'webflow', note: 'Visual no-code' },
                    { name: 'Shopify', slug: 'shopify', note: 'E-commerce' },
                ] as tech}
                    <div class="tech-card group">
                        <div class="tech-icon">
                            <img src="/tech/{tech.slug}.svg" alt="{tech.name} logo" loading="lazy" width="40" height="40" class="tech-svg" />
                        </div>
                        <div class="tech-info">
                            <p class="tech-name">{tech.name}</p>
                            <p class="tech-note">{tech.note}</p>
                        </div>
                    </div>
                {/each}
            </div>
        </div>

        <!-- Analytics & Tools -->
        <div class="reveal">
            <p class="text-[11px] font-bold uppercase tracking-[0.2em] {mode === 'dark' ? 'text-white/40' : 'text-muted'} mb-4 text-center">Analytics & Workflow</p>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-4xl mx-auto">
                {#each [
                    { name: 'Google', slug: 'google', note: 'Search Console + Analytics' },
                    { name: 'Figma', slug: 'figma', note: 'Design + prototype' },
                    { name: 'Git', slug: 'git', note: 'Version control' },
                    { name: 'Font Awesome', slug: 'fontawesome', note: 'Icon library' },
                ] as tech}
                    <div class="tech-card group">
                        <div class="tech-icon">
                            <img src="/tech/{tech.slug}.svg" alt="{tech.name} logo" loading="lazy" width="40" height="40" class="tech-svg" />
                        </div>
                        <div class="tech-info">
                            <p class="tech-name">{tech.name}</p>
                            <p class="tech-note">{tech.note}</p>
                        </div>
                    </div>
                {/each}
            </div>
        </div>

        <p class="mt-10 text-center {mode === 'dark' ? 'text-white/50' : 'text-muted'} text-sm">
            Stack di atas dipilih berdasarkan kebutuhan, skalabilitas, dan biaya operasional klien. Tidak ada markup teknologi — hanya yang terbukti.
        </p>
    </div>
</section>

<style>
    .tech-card {
        display: flex;
        align-items: center;
        gap: 0.875rem;
        padding: 0.875rem 1rem;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 0.875rem;
        transition: all 0.25s ease;
    }
    :global([class*='bg-soft']) .tech-card {
        background: white;
        border-color: #f1f3f8;
    }
    .tech-card:hover {
        transform: translateY(-2px);
        border-color: rgba(245, 158, 11, 0.4);
        box-shadow: 0 10px 30px -10px rgba(15, 30, 61, 0.15);
    }
    :global([class*='bg-soft']) .tech-card:hover {
        border-color: #f59e0b;
    }
    .tech-icon {
        flex-shrink: 0;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.6);
        border-radius: 0.625rem;
        padding: 0.375rem;
    }
    :global(.bg-ink) .tech-icon {
        background: rgba(255, 255, 255, 0.08);
    }
    .tech-svg {
        width: 100%;
        height: 100%;
        object-fit: contain;
        filter: invert(1);
    }
    :global([class*='bg-soft']) .tech-svg {
        filter: none;
    }
    .tech-info { min-width: 0; flex: 1; }
    .tech-name {
        font-family: 'Plus Jakarta Sans Variable', sans-serif;
        font-weight: 700;
        font-size: 0.875rem;
        color: white;
        line-height: 1.2;
    }
    :global([class*='bg-soft']) .tech-name {
        color: #0b1426;
    }
    .tech-note {
        font-size: 0.6875rem;
        color: rgba(255, 255, 255, 0.5);
        margin-top: 0.125rem;
    }
    :global([class*='bg-soft']) .tech-note {
        color: #5b6478;
    }
</style>
