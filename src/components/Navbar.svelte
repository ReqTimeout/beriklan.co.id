<script>
    import { onMount, tick } from "svelte";
    import { Menu, X, ArrowRight, MessageCircle, Phone, Mail, ChevronDown, Sparkles } from 'lucide-svelte';

    let isScrolled = false;
    let isMenuOpen = false;
    let openSection = ''; // mobile accordion
    let openDesktop = ''; // desktop dropdown
    let rafId = null;
    let closeTimeout = null;

    const paidAds = [
        { label: 'Facebook Ads', href: '/jasa-iklan-facebook', desc: '120jt+ pengguna aktif ID' },
        { label: 'Instagram Ads', href: '/jasa-iklan-instagram', desc: 'Visual storytelling' },
        { label: 'TikTok Ads', href: '/jasa-iklan-tiktok', desc: 'Jangkauan FYP organik' },
        { label: 'Google Search Ads', href: '/jasa-iklan-google', desc: 'Tangkap intent tinggi' },
        { label: 'YouTube Ads', href: '/jasa-iklan-youtube', desc: 'Brand awareness video' },
    ];

    const organic = [
        { label: 'Kelola Instagram', href: '/jasa-kelola-instagram', desc: 'Feed rapi & story aktif' },
        { label: 'Kelola TikTok', href: '/jasa-kelola-tiktok', desc: '30 video / bulan' },
    ];

    const build = [
        { label: 'Pembuatan Website', href: '/jasa-pembuatan-website', desc: 'Mulai Rp 999rb / tahun' },
        { label: 'Landing Page + Ads', href: '/jasa-pembuatan-landing-page', desc: 'Bundle Rp 1.999.000' },
    ];

    const navGroups = [
        { key: 'paid', label: 'Paid Ads', Icon: Sparkles, items: paidAds, accent: 'from-amber-500 to-orange-500', popular: true },
        { key: 'organic', label: 'Social Media', Icon: MessageCircle, items: organic, accent: 'from-cyan-500 to-teal-500' },
        { key: 'build', label: 'Website & Landing Page', Icon: ArrowRight, items: build, accent: 'from-violet-500 to-purple-500' },
    ];

    const navSingles = [
        { label: 'Digital Marketing', href: '/jasa-digital-marketing' },
        { label: 'Blog', href: '/blog' },
    ];

    const waNumber = '62811919328';
    const waText = encodeURIComponent('Halo Beriklan, saya ingin berdiskusi mengenai kebutuhan iklan digital bisnis saya.');
    const waLink = `https://wa.me/${waNumber}?text=${waText}`;

    onMount(() => {
        const handleScroll = () => {
            if (rafId) return;
            rafId = requestAnimationFrame(() => {
                isScrolled = window.scrollY > 20;
                rafId = null;
            });
        };
        window.addEventListener('scroll', handleScroll, { passive: true });
        handleScroll();
        return () => {
            window.removeEventListener('scroll', handleScroll);
            if (rafId) cancelAnimationFrame(rafId);
            if (closeTimeout) clearTimeout(closeTimeout);
        };
    });

    function closeAll() {
        openSection = '';
        openDesktop = '';
        if (isMenuOpen) {
            isMenuOpen = false;
            if (typeof document !== 'undefined') document.body.style.overflow = '';
        }
    }

    async function toggleSection(key) {
        openSection = openSection === key ? '' : key;
        await tick();
    }

    function openDesktopDropdown(key) {
        if (closeTimeout) clearTimeout(closeTimeout);
        openDesktop = key;
    }
    function scheduleClose() {
        if (closeTimeout) clearTimeout(closeTimeout);
        closeTimeout = setTimeout(() => { openDesktop = ''; }, 150);
    }

    function toggleMobileMenu() {
        isMenuOpen = !isMenuOpen;
        if (typeof document !== 'undefined') {
            document.body.style.overflow = isMenuOpen ? 'hidden' : '';
        }
    }
</script>

<!-- Top bar -->
<div class="topbar fixed top-0 w-full z-[60] bg-gradient-to-r from-primary via-primary-2 to-primary text-white text-xs hidden md:block transition-transform duration-300 {isScrolled ? '-translate-y-full' : 'translate-y-0'}">
    <div class="container mx-auto px-6 flex items-center justify-between h-9">
        <div class="flex items-center gap-2 font-semibold text-white/90">
            <span class="relative flex h-1.5 w-1.5">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
                <span class="relative inline-flex rounded-full h-1.5 w-1.5 bg-accent"></span>
            </span>
            <span class="hidden sm:inline">Tim online · respon dalam 1 jam pada jam kerja</span>
            <span class="sm:hidden">Tim online</span>
        </div>
        <div class="flex items-center gap-6 text-white/80">
            <a href="tel:+62811919328" class="flex items-center gap-1.5 hover:text-accent transition">
                <Phone class="w-3.5 h-3.5" />
                +62.81.1919.328
            </a>
            <a href="mailto:info@beriklan.co.id" class="hidden lg:flex items-center gap-1.5 hover:text-accent transition">
                info@beriklan.co.id
            </a>
        </div>
    </div>
</div>

<!-- Main nav -->
<nav class="mynav fixed {isScrolled ? 'md:top-0' : 'md:top-9'} top-0 w-full {isMenuOpen ? 'z-30' : 'z-50'} transition-all duration-300 {isScrolled ? 'bg-white/95 backdrop-blur-xl shadow-[0_4px_30px_rgba(15,30,61,0.08)] py-2 border-b border-gray-100' : 'bg-white/70 md:bg-white/60 backdrop-blur-md py-3 md:py-4'}">
    <div class="absolute bottom-0 left-0 right-0 h-px overflow-hidden">
        <div class="h-full bg-gradient-to-r from-transparent via-accent/40 to-transparent transition-opacity duration-500 {isScrolled ? 'opacity-100' : 'opacity-0'}"></div>
    </div>

    <div class="container mx-auto px-5 md:px-6 flex justify-between items-center gap-4">
        <!-- Logo -->
        <a href="/" class="flex items-center gap-2 shrink-0 group" on:click={closeAll}>
            <img
                src="/logoweb.webp"
                alt="Beriklan.co.id"
                class="h-8 md:h-9 w-auto transition-transform duration-300 group-hover:scale-105
                {isScrolled ? '' : 'brightness-0'}"
            />
            <span class="absolute -bottom-1 left-0 w-0 h-0.5 bg-accent transition-all duration-300 group-hover:w-full rounded-full"></span>
        </a>

        <!-- Desktop nav -->
        <div class="hidden lg:flex items-center gap-1">
            <a href="/jasa-digital-marketing" class="px-4 py-2 text-sm font-semibold text-primary hover:text-ink transition rounded-full hover:bg-white/50" on:click={closeAll}>
                Digital Marketing
            </a>

            {#each navGroups as group}
                <div
                    class="relative dd-trigger"
                    on:mouseenter={() => openDesktopDropdown(group.key)}
                    on:mouseleave={scheduleClose}
                    role="presentation"
                >
                    <button
                        type="button"
                        class="dd-trigger-btn px-4 py-2 text-sm font-semibold transition flex items-center gap-1 rounded-full {openDesktop === group.key ? 'bg-white text-ink shadow-sm' : 'text-primary hover:text-ink hover:bg-white/50'}"
                        aria-expanded={openDesktop === group.key}
                        aria-haspopup="true"
                    >
                        {group.label}
                        <ChevronDown class="w-3 h-3 transition-transform duration-200 {openDesktop === group.key ? 'rotate-180' : ''}" />
                    </button>

                    {#if openDesktop === group.key}
                        <div
                            class="dd-panel absolute top-full left-0 pt-3 w-[420px]"
                            on:mouseenter={() => openDesktopDropdown(group.key)}
                            on:mouseleave={scheduleClose}
                            role="presentation"
                        >
                            <div class="bg-white rounded-2xl shadow-pop border border-gray-100 p-3 relative">
                                <div class="absolute -top-1.5 left-12 w-3 h-3 bg-white border-l border-t border-gray-100 rotate-45"></div>
                                {#each group.items as item}
                                    <a
                                        href={item.href}
                                        class="dd-item flex items-start gap-3 p-3 rounded-xl hover:bg-soft transition"
                                        on:click={closeAll}
                                    >
                                        <span class="dd-dot w-1.5 h-1.5 rounded-full bg-accent mt-2 shrink-0"></span>
                                        <span class="flex-1 min-w-0">
                                            <span class="block font-bold text-sm text-ink">{item.label}</span>
                                            <span class="block text-xs text-muted mt-0.5">{item.desc}</span>
                                        </span>
                                        <ArrowRight class="dd-arrow w-3.5 h-3.5 text-muted" />
                                    </a>
                                {/each}
                            </div>
                        </div>
                    {/if}
                </div>
            {/each}

            <a href="/blog" class="px-4 py-2 text-sm font-semibold text-primary hover:text-ink transition rounded-full hover:bg-white/50" on:click={closeAll}>
                Blog
            </a>
        </div>

        <!-- Desktop CTA -->
        <div class="hidden lg:flex items-center gap-2 shrink-0">
            <a href={waLink} target="_blank" rel="noopener" class="group relative inline-flex items-center gap-2 bg-ink text-white pl-4 pr-3 py-2.5 rounded-full font-bold text-sm overflow-hidden hover:shadow-lg transition-all">
                <span class="shine absolute inset-0 bg-gradient-to-r from-accent via-accent-2 to-accent -translate-x-full group-hover:translate-x-0 transition-transform duration-500"></span>
                <span class="relative flex items-center gap-2 group-hover:text-ink transition-colors">
                    <span class="hidden sm:inline">Konsultasi</span>
                    <span class="w-7 h-7 rounded-full bg-white/10 group-hover:bg-ink/10 flex items-center justify-center transition-colors">
                        <ArrowRight class="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                    </span>
                </span>
            </a>
        </div>

        <!-- Tablet CTA -->
        <a href={waLink} target="_blank" rel="noopener" class="hidden md:flex lg:hidden items-center gap-1.5 bg-ink text-white px-3.5 py-2 rounded-full font-bold text-xs hover:bg-accent hover:text-ink transition">
            <MessageCircle class="w-3.5 h-3.5" fill="currentColor" />
            Chat
        </a>

        <!-- Mobile hamburger -->
        <button class="lg:hidden relative w-11 h-11 flex items-center justify-center rounded-full border border-gray-200 bg-white hover:border-ink hover:bg-ink hover:text-white transition-all group" on:click={toggleMobileMenu} aria-label="Buka menu navigasi">
            {#if isMenuOpen}
                <X class="w-5 h-5" />
            {:else}
                <span class="hamburger"><span></span><span></span><span></span></span>
            {/if}
        </button>
    </div>
</nav>

<!-- Mobile menu -->
<div class="mobile-menu fixed inset-0 z-[60] lg:hidden {isMenuOpen ? 'open' : ''}" aria-hidden={!isMenuOpen}>
    <div class="backdrop absolute inset-0" on:click={closeAll} role="presentation"></div>

    <div class="panel absolute inset-0 flex flex-col overflow-hidden">
        <div class="absolute top-[-120px] right-[-100px] w-[320px] h-[320px] bg-accent/30 rounded-full blur-3xl pointer-events-none"></div>
        <div class="absolute bottom-[-100px] left-[-80px] w-[280px] h-[280px] bg-teal/25 rounded-full blur-3xl pointer-events-none"></div>
        <div class="absolute inset-0 opacity-[0.04] pointer-events-none mobile-grid"></div>

        <div class="relative z-10 flex items-center justify-between px-6 pt-5 pb-3">
            <a href="/" class="flex items-center gap-2.5" on:click={closeAll}>
                <img src="/logoweb.webp" alt="Beriklan.co.id" class="h-8 w-auto brightness-0 invert" />
            </a>
            <button class="close-btn w-11 h-11 rounded-full bg-white text-ink hover:bg-accent flex items-center justify-center transition-all shadow-lg" on:click={closeAll} aria-label="Tutup menu">
                <X class="w-5 h-5" strokeWidth="2.5" />
            </button>
        </div>

        <!-- Hero block: live status, headline, trust strip -->
        <div class="relative px-6 pt-4 pb-5">
            <div class="flex items-center gap-2 mb-3 reveal-up" style="animation-delay: 60ms;">
                <span class="relative inline-flex h-2 w-2">
                    <span class="absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75 animate-ping"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-green-400"></span>
                </span>
                <span class="text-[10px] font-bold uppercase tracking-[0.18em] text-green-300/90">Tim online &middot; siap merespon</span>
            </div>
            <h2 class="font-display font-extrabold text-white text-[28px] leading-[1.05] tracking-tight reveal-up" style="animation-delay: 120ms;">
                Mau scale up<br/>
                <span class="text-accent">penjualan via iklan?</span>
            </h2>
            <p class="text-white/60 text-[13px] mt-3 leading-relaxed max-w-xs reveal-up" style="animation-delay: 180ms;">
                Pilih layanan di bawah, atau langsung terhubung lewat WhatsApp untuk diskusi singkat 15 menit.
            </p>

            <!-- Trust strip: 3 micro-pills -->
            <div class="mt-4 flex flex-wrap items-center gap-2 reveal-up" style="animation-delay: 240ms;">
                <span class="trust-pill">
                    <span class="trust-dot"></span>
                    <span>9 th pengalaman</span>
                </span>
                <span class="trust-pill">
                    <svg class="w-3 h-3 text-accent" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a 1 1 0 01-1.414 0l-4-4a 1 1 0 011.414-1.414L8 12.586l7.293-7.293a 1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                    <span>Respon 1 jam</span>
                </span>
                <span class="trust-pill">
                    <svg class="w-3 h-3 text-accent" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a 1 1 0 01-1.414 0l-4-4a 1 1 0 011.414-1.414L8 12.586l7.293-7.293a 1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                    <span>Sertifikasi Meta &amp; Google</span>
                </span>
            </div>
        </div>

        <nav class="flex-1 overflow-y-auto px-4 pb-2 relative min-h-0">
            <ul class="space-y-2">
                {#each navGroups as group, i}
                    <li class="menu-group reveal-up" style="animation-delay: {80 + i * 50}ms;">
                        <button
                            type="button"
                            class="group-btn"
                            class:active={openSection === group.key}
                            on:click={() => toggleSection(group.key)}
                            aria-expanded={openSection === group.key}
                        >
                            <span class="group-num">0{i + 1}</span>
                            <span class="flex-1 text-left">
                                <span class="group-label">
                                    {group.label}
                                    {#if group.popular}
                                        <span class="popular-pill">Paling dicari</span>
                                    {/if}
                                </span>
                                <span class="group-count">{group.items.length} layanan</span>
                            </span>
                            <span class="group-chevron">
                                <ChevronDown class="w-4 h-4" />
                            </span>
                        </button>

                        <div class="submenu {openSection === group.key ? 'open' : ''}">
                            <div class="submenu-inner">
                                {#each group.items as item, idx}
                                    <a href={item.href} class="submenu-link" style="--delay: {idx * 40}ms;" on:click={closeAll}>
                                        <span class="submenu-dot bg-gradient-to-br {group.accent}"></span>
                                        <span class="flex-1 min-w-0">
                                            <span class="submenu-name">{item.label}</span>
                                            <span class="submenu-desc">{item.desc}</span>
                                        </span>
                                        <ArrowRight class="submenu-arrow w-3.5 h-3.5 text-white/60" />
                                    </a>
                                {/each}
                            </div>
                        </div>
                    </li>
                {/each}

                {#each navSingles as single, i}
                    <li class="reveal-up" style="animation-delay: {80 + (navGroups.length + i) * 50}ms;">
                        <a href={single.href} class="group-btn" on:click={closeAll}>
                            <span class="group-num">0{navGroups.length + i + 1}</span>
                            <span class="flex-1 text-left">
                                <span class="group-label">{single.label}</span>
                                <span class="group-count">Halaman lengkap</span>
                            </span>
                            <ArrowRight class="w-4 h-4 text-white/60" />
                        </a>
                    </li>
                {/each}
            </ul>
        </nav>

        <div class="quick-contact relative px-4 pt-3 pb-3 space-y-2 shrink-0">
            <p class="text-[10px] font-bold uppercase tracking-[0.18em] text-white/40 px-2 mb-1">Hubungi langsung</p>
            <a href="tel:+62811919328" class="quick-card" on:click={closeAll}>
                <span class="quick-icon"><Phone class="w-4 h-4 text-white" /></span>
                <span class="flex-1 min-w-0">
                    <span class="block text-white font-bold text-sm leading-tight">+62 81.1919.328</span>
                    <span class="block text-white/50 text-[11px]">Telepon langsung</span>
                </span>
            </a>
        </div>

        <div class="cta-wrap relative px-4 pb-5 pt-3 border-t border-white/10 bg-gradient-to-t from-ink to-transparent shrink-0">
            <a href={waLink} target="_blank" rel="noopener" class="cta-whatsapp group">
                <span class="cta-shine"></span>
                <span class="relative flex items-center justify-center gap-2.5">
                    <span class="cta-icon">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448L.057 24z"/></svg>
                    </span>
                    <span class="flex flex-col items-start">
                        <span class="font-display font-extrabold text-[15px] leading-tight">Diskusi via WhatsApp</span>
                        <span class="text-[10px] opacity-90 leading-tight">Respon dalam 1 jam · jam kerja</span>
                    </span>
                    <ArrowRight class="w-4 h-4 ml-auto group-hover:translate-x-0.5 transition-transform" />
                </span>
            </a>
            <div class="flex items-center justify-center gap-3 mt-3 text-[10px] text-white/50">
                <span class="flex items-center gap-1">
                    <svg class="w-3 h-3 text-green-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a 1 1 0 01-1.414 0l-4-4a 1 1 0 011.414-1.414L8 12.586l7.293-7.293a 1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                    Respon 1 jam
                </span>
                <span class="w-px h-3 bg-white/20"></span>
                <span>© 2026 Bandung</span>
            </div>
        </div>
    </div>
</div>

<style>
    .hamburger { position: relative; width: 18px; height: 14px; display: inline-block; }
    .hamburger span {
        position: absolute; left: 0; width: 0%; height: 2px;
        background: #0f1e3d; border-radius: 2px;
        transition: transform 0.25s ease, top 0.25s ease, opacity 0.2s ease, width 0.3s ease;
    }
    .hamburger span:nth-child(1) { top: 0; width: 100%; }
    .hamburger span:nth-child(2) { top: 6px; width: 70%; }
    .hamburger span:nth-child(3) { top: 12px; width: 100%; }
    button:hover .hamburger span:nth-child(2) { width: 100%; }

    /* ===== Desktop dropdown ===== */
    .dd-panel {
        animation: dd-in 0.18s cubic-bezier(0.22, 1, 0.36, 1);
        transform-origin: top left;
        z-index: 70;
    }
    @keyframes dd-in {
        from { opacity: 0; transform: translateY(-6px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .dd-item .dd-dot { transition: transform 0.2s ease, background-color 0.2s ease; }
    .dd-item:hover .dd-dot { transform: scale(1.6); }
    .dd-item .dd-arrow { opacity: 0; transform: translateX(-4px); transition: opacity 0.2s ease, transform 0.2s ease; }
    .dd-item:hover .dd-arrow { opacity: 1; transform: translateX(0); }

    /* ===== MOBILE MENU ===== */
    .mobile-menu { visibility: hidden; pointer-events: none; }
    .mobile-menu.open { visibility: visible; pointer-events: auto; }

    .mobile-menu .backdrop {
        background: rgba(11, 20, 38, 0.85);
        backdrop-filter: blur(12px);
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    .mobile-menu.open .backdrop { opacity: 1; }

    .mobile-menu .panel {
        background: linear-gradient(180deg, #0b1426 0%, #0f1e3d 60%, #1a2f5c 100%);
        transform: translateY(100%);
        transition: transform 0.5s cubic-bezier(0.32, 0.72, 0, 1);
    }
    .mobile-menu.open .panel { transform: translateY(0); }

    .mobile-grid {
        background-image:
            linear-gradient(rgba(255,255,255,0.06) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.06) 1px, transparent 1px);
        background-size: 32px 32px;
    }

    .group-btn {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 14px 14px;
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.06);
        color: white;
        font-weight: 700;
        font-size: 15px;
        text-align: left;
        width: 100%;
        transition: background-color 0.2s ease, border-color 0.2s ease, transform 0.15s ease;
        position: relative;
    }
    .group-btn:hover, .group-btn:active {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 255, 255, 0.1);
    }
    .group-btn:active { transform: scale(0.985); }
    .group-btn.active {
        background: rgba(245, 158, 11, 0.12);
        border-color: rgba(245, 158, 11, 0.35);
    }

    .group-num {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 30px;
        height: 30px;
        border-radius: 9px;
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        font-size: 11px;
        font-weight: 800;
        flex-shrink: 0;
    }
    .group-btn.active .group-num {
        background: #fbbf24;
        color: #0b1426;
    }
    .group-label {
        display: block;
        color: white;
        font-weight: 700;
        font-size: 15px;
        line-height: 1.2;
    }
    .group-count {
        display: block;
        color: rgba(255, 255, 255, 0.5);
        font-size: 11px;
        font-weight: 500;
        margin-top: 1px;
    }
    .group-chevron {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 30px;
        height: 30px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.06);
        color: rgba(255, 255, 255, 0.7);
        transition: transform 0.3s ease, background-color 0.2s ease;
        flex-shrink: 0;
    }
    .group-btn.active .group-chevron {
        background: #fbbf24;
        color: #0b1426;
        transform: rotate(180deg);
    }

    .submenu {
        display: grid;
        grid-template-rows: 0fr;
        transition: grid-template-rows 0.35s cubic-bezier(0.22, 1, 0.36, 1), margin 0.3s ease;
        margin-top: 0;
    }
    .submenu.open {
        grid-template-rows: 1fr;
        margin-top: 6px;
    }
    .submenu-inner {
        overflow: hidden;
        min-height: 0;
    }
    .submenu-link {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 12px;
        margin-top: 2px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: background-color 0.18s ease, border-color 0.18s ease, transform 0.18s ease, padding-left 0.2s ease;
        opacity: 0;
        transform: translateY(-4px);
    }
    .submenu.open .submenu-link {
        opacity: 1;
        transform: translateY(0);
        transition-delay: var(--delay, 0ms);
    }
    .submenu-link:hover, .submenu-link:active {
        background: rgba(245, 158, 11, 0.1);
        border-color: rgba(245, 158, 11, 0.3);
        padding-left: 16px;
    }
    .submenu-dot {
        width: 10px;
        height: 10px;
        border-radius: 999px;
        flex-shrink: 0;
        box-shadow: 0 0 12px rgba(245, 158, 11, 0.4);
    }
    .submenu-name {
        display: block;
        color: white;
        font-weight: 600;
        font-size: 14px;
        line-height: 1.25;
    }
    .submenu-desc {
        display: block;
        color: rgba(255, 255, 255, 0.5);
        font-size: 11px;
        margin-top: 1px;
    }
    .submenu-arrow {
        opacity: 0;
        transform: translateX(-4px);
        transition: opacity 0.2s ease, transform 0.2s ease;
        flex-shrink: 0;
    }
    .submenu-link:hover .submenu-arrow,
    .submenu-link:active .submenu-arrow {
        opacity: 1;
        transform: translateX(0);
    }

    .trust-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 10px 5px 8px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 999px;
        color: rgba(255, 255, 255, 0.78);
        font-size: 10.5px;
        font-weight: 600;
        letter-spacing: 0.01em;
    }
    .trust-dot {
        width: 6px;
        height: 6px;
        border-radius: 999px;
        background: #4ade80;
        box-shadow: 0 0 8px rgba(74, 222, 128, 0.6);
    }
    .popular-pill {
        display: inline-flex;
        align-items: center;
        margin-left: 6px;
        padding: 2px 6px;
        background: linear-gradient(135deg, #f59e0b 0%, #fb923c 100%);
        color: #0b1426;
        font-size: 8.5px;
        font-weight: 800;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        border-radius: 5px;
        vertical-align: 2px;
    }
    .reveal-up {
        animation: revealUp 0.4s cubic-bezier(0.22, 1, 0.36, 1) both;
    }
    @keyframes revealUp {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .quick-contact {
        opacity: 0;
        transform: translateY(8px);
        transition: opacity 0.4s ease 0.25s, transform 0.4s cubic-bezier(0.22, 1, 0.36, 1) 0.25s;
    }
    .mobile-menu.open .quick-contact { opacity: 1; transform: translateY(0); }

    .quick-card {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 14px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.06);
        transition: background-color 0.2s ease, border-color 0.2s ease, transform 0.15s ease;
    }
    .quick-card:hover, .quick-card:active {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(245, 158, 11, 0.3);
    }
    .quick-card:active { transform: scale(0.985); }
    .quick-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 38px;
        height: 38px;
        border-radius: 10px;
        background: rgba(245, 158, 11, 0.15);
        flex-shrink: 0;
    }

    .cta-wrap {
        opacity: 0;
        transform: translateY(8px);
        transition: opacity 0.4s ease 0.35s, transform 0.4s cubic-bezier(0.22, 1, 0.36, 1) 0.35s;
    }
    .mobile-menu.open .cta-wrap { opacity: 1; transform: translateY(0); }

    .cta-whatsapp {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        padding: 14px 18px;
        border-radius: 16px;
        background: linear-gradient(135deg, #f59e0b 0%, #fb923c 100%);
        color: #0b1426;
        font-weight: 800;
        box-shadow:
            0 14px 30px -10px rgba(245, 158, 11, 0.6),
            0 0 0 1px rgba(255, 255, 255, 0.1) inset;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .cta-whatsapp:active { transform: translateY(0) scale(0.985); }

    .cta-shine {
        position: absolute;
        top: 0; left: -100%;
        width: 60%; height: 100%;
        background: linear-gradient(110deg, transparent 30%, rgba(255,255,255,0.5) 50%, transparent 70%);
        animation: cta-shine 3s ease-in-out infinite;
    }
    @keyframes cta-shine {
        0%, 100% { left: -100%; }
        50%, 80% { left: 120%; }
    }
    .cta-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: 10px;
        background: rgba(11, 20, 38, 0.18);
        flex-shrink: 0;
    }

    @media (prefers-reduced-motion: reduce) {
        .mobile-menu .panel,
        .mobile-menu .backdrop,
        .quick-contact,
        .cta-wrap,
        .reveal-up,
        .submenu-link,
        .cta-shine,
        .dd-panel { transition: none !important; animation: none !important; }
    }
</style>
