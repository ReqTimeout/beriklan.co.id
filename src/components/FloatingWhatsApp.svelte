<script>
    import { onMount } from 'svelte';
    import { fly, fade, scale } from 'svelte/transition';
    import { MessageCircle, X, Phone, Mail, Clock } from 'lucide-svelte';

    const phoneNumber = '62811919328';
    const defaultMessage = 'Halo Beriklan, saya ingin berdiskusi mengenai kebutuhan iklan digital bisnis saya.';
    const waLink = `https://wa.me/${phoneNumber}?text=${encodeURIComponent(defaultMessage)}`;
    const phoneLink = 'tel:+62811919328';
    const mailLink = 'mailto:info@beriklan.co.id?subject=Konsultasi%20Iklan%20Digital';

    let visible = false;
    let isOpen = false;
    let labelExpanded = true;
    let isMobile = false;
    let hideOnScroll = false;

    onMount(() => {
        const checkMobile = () => {
            isMobile = window.innerWidth < 768;
        };
        checkMobile();
        // Show after 1.5s
        const t = setTimeout(() => { visible = true; }, 1500);
        // Auto-collapse label di mobile setelah 4 detik
        const collapse = setTimeout(() => { labelExpanded = false; }, 4000);

        // Auto-hide FAB saat user scroll banyak (mobile only) untuk tidak menutupi konten
        let lastY = 0;
        let rafId = null;
        const onScroll = () => {
            if (!isMobile || rafId) return;
            rafId = requestAnimationFrame(() => {
                const y = window.scrollY;
                const next = y > lastY + 50 && y > 800;
                if (next !== hideOnScroll) hideOnScroll = next;
                lastY = y;
                rafId = null;
            });
        };
        window.addEventListener('scroll', onScroll, { passive: true });

        const handleResize = () => checkMobile();
        window.addEventListener('resize', handleResize, { passive: true });

        return () => {
            clearTimeout(t);
            clearTimeout(collapse);
            if (rafId) cancelAnimationFrame(rafId);
            window.removeEventListener('resize', handleResize);
            window.removeEventListener('scroll', onScroll);
        };
    });

    function toggleOpen() {
        isOpen = !isOpen;
        if (isOpen) labelExpanded = false;
    }
</script>

<!-- Mobile bottom sheet -->
{#if isMobile && isOpen}
    <button
        type="button"
        class="fixed inset-0 z-[58] bg-ink/55 backdrop-blur-sm"
        aria-label="Tutup menu chat"
        on:click={toggleOpen}
        transition:fade={{ duration: 200 }}
    ></button>
    <div
        class="fixed left-3 right-3 bottom-[5.25rem] z-[60] md:hidden"
        in:fly={{ y: 24, duration: 320, delay: 60 }}
        out:fly={{ y: 24, duration: 200 }}
    >
        <div class="bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden">
            <div class="relative bg-gradient-to-br from-ink via-primary-2 to-ink px-5 py-4 text-white">
                <div class="absolute inset-0 pointer-events-none" style="background: radial-gradient(circle at 85% 20%, rgba(37,211,102,0.25) 0%, transparent 50%);"></div>
                <div class="relative flex items-center gap-3">
                    <div class="relative shrink-0">
                        <div class="w-11 h-11 rounded-full bg-gradient-to-br from-[#25d366] to-[#075e54] flex items-center justify-center shadow-lg">
                            <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 32 32"><path d="M16.001 3C9.373 3 4 8.373 4 15c0 2.385.696 4.605 1.896 6.482L4 29l7.737-1.852A11.94 11.94 0 0 0 16 27c6.627 0 12-5.373 12-12S22.628 3 16.001 3Z"/></svg>
                        </div>
                        <span class="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-400 rounded-full border-2 border-ink live-dot"></span>
                    </div>
                    <div class="min-w-0 flex-1">
                        <p class="font-display font-bold text-[15px] leading-tight">Konsultan Beriklan</p>
                        <p class="text-[11px] text-white/65 mt-0.5 flex items-center gap-1.5">
                            <Clock class="w-3 h-3" />
                            Respon dalam 1 jam &middot; jam kerja
                        </p>
                    </div>
                    <button
                        type="button"
                        on:click={toggleOpen}
                        on:pointerdown|stopPropagation
                        aria-label="Tutup menu"
                        title="Tutup"
                        class="w-11 h-11 -mr-2 rounded-full bg-white/15 hover:bg-white/30 active:bg-white/40 flex items-center justify-center transition shrink-0"
                    >
                        <X class="w-5 h-5" strokeWidth="2.5" />
                    </button>
                </div>
            </div>
            <div class="p-3 space-y-2">
                <a href={waLink} target="_blank" rel="noopener" data-cta="floating_whatsapp" data-cta-location="floating_sheet" class="quick-row">
                    <span class="quick-row-icon bg-[#25d366]/10 text-[#075e54]">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 32 32"><path d="M16.001 3C9.373 3 4 8.373 4 15c0 2.385.696 4.605 1.896 6.482L4 29l7.737-1.852A11.94 11.94 0 0 0 16 27c6.627 0 12-5.373 12-12S22.628 3 16.001 3Z"/></svg>
                    </span>
                    <span class="flex-1 min-w-0">
                        <span class="block font-bold text-ink text-sm">Chat via WhatsApp</span>
                        <span class="block text-[11px] text-muted">Respon paling cepat</span>
                    </span>
                    <span class="text-[10px] font-bold text-green-600 bg-green-50 px-2 py-1 rounded-full">Rekomendasi</span>
                </a>
                <a href={phoneLink} class="quick-row">
                    <span class="quick-row-icon bg-blue-50 text-blue-600">
                        <Phone class="w-5 h-5" />
                    </span>
                    <span class="flex-1 min-w-0">
                        <span class="block font-bold text-ink text-sm">+62 81.1919.328</span>
                        <span class="block text-[11px] text-muted">Telepon langsung</span>
                    </span>
                </a>
                <a href={mailLink} class="quick-row">
                    <span class="quick-row-icon bg-amber-50 text-amber-600">
                        <Mail class="w-5 h-5" />
                    </span>
                    <span class="flex-1 min-w-0">
                        <span class="block font-bold text-ink text-sm">info@beriklan.co.id</span>
                        <span class="block text-[11px] text-muted">Untuk pertanyaan detail</span>
                    </span>
                </a>
            </div>
        </div>
    </div>
{/if}

<!-- FAB launcher — mobile only, hide when sheet open to avoid confusion -->
{#if (!hideOnScroll || !isMobile) && isMobile && !isOpen}
<button
    type="button"
    on:click={toggleOpen}
    aria-label="Buka menu chat WhatsApp"
    class="wa-float group md:!hidden"
    class:visible
    class:is-mobile={isMobile}
>
    {#if labelExpanded && !isOpen}
        <span
            class="wa-label"
            in:fade={{ duration: 250 }}
            out:fade={{ duration: 150 }}
        >
            <span class="wa-label-dot"></span>
            {#if isMobile}
                Chat sekarang
            {:else}
                Diskusi via WhatsApp
            {/if}
        </span>
    {/if}

    <span class="wa-pulse-ring" aria-hidden="true"></span>
    <span class="wa-pulse-ring delay" aria-hidden="true"></span>

    <span class="wa-core" in:fly={{ y: 30, duration: 500 }}>
        {#if isOpen}
            <X class="w-6 h-6" strokeWidth="2.5" />
        {:else}
            <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 32 32"
                class="wa-icon"
                aria-hidden="true"
            >
                <path
                    fill="currentColor"
                    d="M16.001 3C9.373 3 4 8.373 4 15c0 2.385.696 4.605 1.896 6.482L4 29l7.737-1.852A11.94 11.94 0 0 0 16 27c6.627 0 12-5.373 12-12S22.628 3 16.001 3Zm0 21.6c-1.83 0-3.585-.5-5.118-1.448l-.367-.222-3.83.917.957-3.74-.24-.388A9.585 9.585 0 0 1 6.4 15c0-5.302 4.298-9.6 9.6-9.6 5.302 0 9.6 4.298 9.6 9.6 0 5.302-4.298 9.6-9.6 9.6Zm5.302-7.108c-.29-.146-1.72-.85-1.986-.946-.266-.097-.46-.146-.653.146-.193.29-.747.946-.916 1.14-.169.193-.338.218-.628.072-.29-.146-1.224-.451-2.332-1.438-.862-.769-1.444-1.72-1.613-2.01-.169-.29-.018-.447.127-.592.13-.13.29-.338.435-.508.145-.169.193-.29.29-.483.097-.193.048-.363-.024-.508-.072-.146-.653-1.572-.895-2.152-.236-.565-.476-.488-.653-.498-.169-.008-.363-.01-.557-.01-.193 0-.508.072-.774.363-.266.29-1.014.99-1.014 2.414 0 1.424 1.038 2.8 1.182 2.993.145.193 2.04 3.114 4.94 4.367.69.298 1.23.476 1.65.61.693.22 1.324.189 1.823.115.556-.083 1.72-.703 1.962-1.382.242-.678.242-1.26.169-1.382-.072-.121-.266-.193-.557-.339Z"
                />
            </svg>
        {/if}
        <span class="wa-badge" aria-hidden="true">1</span>
    </span>
</button>
{/if}

<style>
    /* Mobile bottom sheet quick rows */
    .quick-row {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 14px;
        border-radius: 14px;
        background: #fff;
        border: 1px solid #f1f5f9;
        transition: background-color 180ms ease, border-color 180ms ease, transform 150ms ease;
    }
    .quick-row:hover, .quick-row:active {
        background: #fafbff;
        border-color: #e2e8f0;
        transform: translateY(-1px);
    }
    .quick-row-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border-radius: 11px;
        flex-shrink: 0;
    }

    /* Live dot inside header */
    .live-dot::after {
        content: '';
        position: absolute;
        inset: -2px;
        border-radius: 999px;
        border: 2px solid rgba(74, 222, 128, 0.4);
        animation: live-ping 1.6s cubic-bezier(0,0,0.2,1) infinite;
    }
    @keyframes live-ping {
        0% { transform: scale(1); opacity: 1; }
        80%, 100% { transform: scale(1.6); opacity: 0; }
    }

    /* WhatsApp badge "1" */
    .wa-badge {
        position: absolute;
        top: -4px;
        right: -4px;
        min-width: 18px;
        height: 18px;
        padding: 0 5px;
        border-radius: 999px;
        background: #ef4444;
        color: #fff;
        font-size: 10px;
        font-weight: 800;
        line-height: 18px;
        text-align: center;
        box-shadow: 0 0 0 2px #fff;
    }

    /* Status dot inside floating label */
    .wa-label-dot {
        display: inline-block;
        width: 6px;
        height: 6px;
        border-radius: 999px;
        background: #25d366;
        box-shadow: 0 0 0 3px rgba(37, 211, 102, 0.18);
        margin-right: 8px;
        vertical-align: 1px;
    }

    .wa-float {
        position: fixed;
        right: 1.25rem;
        bottom: 1.75rem;
        z-index: 60;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        opacity: 0;
        pointer-events: none;
        transform: translateY(20px) scale(0.9);
        transition: opacity 350ms ease, transform 350ms ease;
    }

    .wa-float.visible {
        opacity: 1;
        pointer-events: auto;
        transform: translateY(0) scale(1);
    }

    /* Mobile: pill-shaped mini-CTA di atas bottom nav */
    .wa-float.is-mobile {
        right: 0.875rem;
        bottom: 0.875rem;
    }

    .wa-label {
        background: #ffffff;
        color: #0b1426;
        font-weight: 700;
        font-size: 0.8125rem;
        padding: 0.5rem 0.875rem;
        border-radius: 9999px;
        box-shadow:
            0 6px 20px rgba(11, 20, 38, 0.18),
            0 2px 6px rgba(0, 0, 0, 0.06);
        white-space: nowrap;
        border: 1px solid rgba(37, 211, 102, 0.35);
        position: relative;
    }

    .wa-label::after {
        content: '';
        position: absolute;
        right: -6px;
        top: 50%;
        transform: translateY(-50%);
        width: 0;
        height: 0;
        border-top: 6px solid transparent;
        border-bottom: 6px solid transparent;
        border-left: 6px solid #ffffff;
    }

    .wa-float.is-mobile .wa-label {
        font-size: 0.75rem;
        padding: 0.4rem 0.7rem;
    }

    @media (max-width: 480px) {
        .wa-label {
            display: none;
        }
    }

    /* ===== Core circle ===== */
    .wa-core {
        position: relative;
        width: 60px;
        height: 60px;
        border-radius: 9999px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        background: linear-gradient(135deg, #25d366 0%, #128c7e 60%, #075e54 100%);
        box-shadow:
            0 10px 30px rgba(37, 211, 102, 0.45),
            0 4px 12px rgba(7, 94, 84, 0.35),
            inset 0 1px 0 rgba(255, 255, 255, 0.25);
        transition: transform 220ms ease, box-shadow 220ms ease;
    }

    /* Desktop: lebih besar dan ada gradient ring */
    @media (min-width: 769px) {
        .wa-core {
            width: 68px;
            height: 68px;
            box-shadow:
                0 14px 36px rgba(37, 211, 102, 0.5),
                0 4px 12px rgba(7, 94, 84, 0.35),
                inset 0 1px 0 rgba(255, 255, 255, 0.3),
                0 0 0 1px rgba(255, 255, 255, 0.08);
        }
    }

    .wa-float:hover .wa-core,
    .wa-float:focus-visible .wa-core {
        transform: scale(1.08) rotate(-4deg);
        box-shadow:
            0 14px 38px rgba(37, 211, 102, 0.6),
            0 6px 14px rgba(7, 94, 84, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }

    .wa-float:active .wa-core {
        transform: scale(0.96);
    }

    .wa-icon {
        width: 30px;
        height: 30px;
    }

    @media (min-width: 769px) {
        .wa-icon {
            width: 34px;
            height: 34px;
        }
    }

    /* Pulse ring — different scale on mobile vs desktop */
    .wa-pulse-ring {
        position: absolute;
        right: 0;
        bottom: 0;
        width: 60px;
        height: 60px;
        border-radius: 9999px;
        background: rgba(37, 211, 102, 0.45);
        animation: wa-ping 2.2s cubic-bezier(0, 0, 0.2, 1) infinite;
        pointer-events: none;
    }

    @media (min-width: 769px) {
        .wa-pulse-ring {
            width: 68px;
            height: 68px;
        }
    }

    .wa-pulse-ring.delay {
        animation-delay: 1.1s;
    }

    @keyframes wa-ping {
        0% {
            transform: scale(1);
            opacity: 0.6;
        }
        80%, 100% {
            transform: scale(1.9);
            opacity: 0;
        }
    }

    .wa-float.is-open .wa-pulse-ring { animation: none; opacity: 0; }
    .wa-float.is-open .wa-core {
        background: linear-gradient(135deg, #0f1e3d 0%, #1a2f5c 100%);
    }
    .wa-float.is-open .wa-badge { display: none; }

    @media (prefers-reduced-motion: reduce) {
        .wa-pulse-ring {
            animation: none;
        }
        /* Mobile bottom sheet quick rows */
    .quick-row {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 14px;
        border-radius: 14px;
        background: #fff;
        border: 1px solid #f1f5f9;
        transition: background-color 180ms ease, border-color 180ms ease, transform 150ms ease;
    }
    .quick-row:hover, .quick-row:active {
        background: #fafbff;
        border-color: #e2e8f0;
        transform: translateY(-1px);
    }
    .quick-row-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border-radius: 11px;
        flex-shrink: 0;
    }

    /* Live dot inside header */
    .live-dot::after {
        content: '';
        position: absolute;
        inset: -2px;
        border-radius: 999px;
        border: 2px solid rgba(74, 222, 128, 0.4);
        animation: live-ping 1.6s cubic-bezier(0,0,0.2,1) infinite;
    }
    @keyframes live-ping {
        0% { transform: scale(1); opacity: 1; }
        80%, 100% { transform: scale(1.6); opacity: 0; }
    }

    /* WhatsApp badge "1" */
    .wa-badge {
        position: absolute;
        top: -4px;
        right: -4px;
        min-width: 18px;
        height: 18px;
        padding: 0 5px;
        border-radius: 999px;
        background: #ef4444;
        color: #fff;
        font-size: 10px;
        font-weight: 800;
        line-height: 18px;
        text-align: center;
        box-shadow: 0 0 0 2px #fff;
    }

    /* Status dot inside floating label */
    .wa-label-dot {
        display: inline-block;
        width: 6px;
        height: 6px;
        border-radius: 999px;
        background: #25d366;
        box-shadow: 0 0 0 3px rgba(37, 211, 102, 0.18);
        margin-right: 8px;
        vertical-align: 1px;
    }

    .wa-float {
            transition: opacity 200ms ease;
        }
    }
</style>
