<script>
    import { onMount } from 'svelte';
    import { MessageCircle, X, Phone, Mail, ArrowRight } from 'lucide-svelte';

    let visible = false;
    let isOpen = false;
    let dismissed = false;
    let unread = true;
    let rafId = null;
    let isMobile = false;

    const waLink = "https://wa.me/62811919328?text=Halo%20Beriklan%2C%20saya%20ingin%20mendiskusikan%20strategi%20campaign%20iklan%20untuk%20bisnis%20saya";
    const phoneLink = "tel:+62811919328";
    const mailLink = "mailto:info@beriklan.co.id?subject=Konsultasi%20Iklan";

    onMount(() => {
        const checkMobile = () => {
            isMobile = window.innerWidth < 768;
        };
        checkMobile();

        const handleScroll = () => {
            if (rafId) return;
            rafId = requestAnimationFrame(() => {
                visible = window.scrollY > 500;
                rafId = null;
            });
        };
        window.addEventListener('scroll', handleScroll, { passive: true });
        window.addEventListener('resize', checkMobile, { passive: true });
        handleScroll();
        return () => {
            window.removeEventListener('scroll', handleScroll);
            window.removeEventListener('resize', checkMobile);
            if (rafId) cancelAnimationFrame(rafId);
        };
    });

    function toggle() {
        isOpen = !isOpen;
        if (isOpen) unread = false;
    }

    function closeAll() {
        isOpen = false;
    }

    function dismiss() {
        dismissed = true;
        isOpen = false;
    }
</script>

{#if visible && !dismissed}
    <!-- Mobile backdrop (only when expanded) -->
    {#if isOpen && isMobile}
        <button
            type="button"
            class="fixed inset-0 z-40 bg-ink/55 backdrop-blur-sm md:hidden"
            aria-label="Tutup menu"
            on:click={closeAll}
        ></button>
    {/if}

    <div class="fixed bottom-4 right-4 sm:bottom-5 sm:right-5 z-50 flex flex-col items-end gap-3 pointer-events-none">
        <!-- Expanded panel — Desktop: auto-open, always visible. Mobile: bottom sheet -->
        {#if isMobile}
            {#if isOpen}
                <div class="pointer-events-auto sticky-panel bg-white rounded-3xl shadow-2xl border border-gray-100 w-[calc(100vw-2rem)] overflow-hidden">
                    <div class="relative bg-gradient-to-br from-ink via-primary-2 to-ink px-5 py-5 text-white">
                        <div class="absolute inset-0 pointer-events-none" style="background: radial-gradient(circle at 80% 20%, rgba(245,158,11,0.25) 0%, transparent 50%);"></div>
                        <button
                            type="button"
                            on:click={closeAll}
                            aria-label="Tutup"
                            class="absolute top-3 right-3 w-9 h-9 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition"
                        >
                            <X class="w-4 h-4" />
                        </button>
                        <div class="relative flex items-center gap-3">
                            <div class="relative">
                                <div class="w-12 h-12 rounded-full bg-gradient-to-br from-accent to-orange-500 flex items-center justify-center shadow-lg">
                                    <svg class="w-6 h-6 text-ink" fill="currentColor" viewBox="0 0 24 24"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448L.057 24z"/></svg>
                                </div>
                                <span class="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-green-500 rounded-full border-2 border-ink live-dot"></span>
                            </div>
                            <div>
                                <p class="font-display font-bold text-base leading-tight">Konsultan Beriklan</p>
                                <p class="text-xs text-white/70 mt-0.5">Merespons dalam 1 jam · jam kerja</p>
                            </div>
                        </div>
                    </div>
                    <div class="px-4 py-4 space-y-2.5">
                        <a
                            href={waLink}
                            target="_blank"
                            rel="noopener"
                            class="flex items-center gap-3 p-3.5 rounded-2xl bg-ink text-white hover:bg-accent hover:text-ink transition-all group"
                        >
                            <div class="w-11 h-11 rounded-xl bg-white/10 group-hover:bg-ink/10 flex items-center justify-center shrink-0">
                                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448L.057 24z"/></svg>
                            </div>
                            <div class="flex-1 min-w-0 text-left">
                                <p class="font-display font-extrabold text-[15px] leading-tight">Chat WhatsApp</p>
                                <p class="text-[11px] opacity-70 leading-tight">Konsultasi 15 menit · tanpa biaya</p>
                            </div>
                            <ArrowRight class="w-4 h-4 opacity-70 group-hover:translate-x-0.5 transition" />
                        </a>
                        <a
                            href={phoneLink}
                            class="flex items-center gap-3 p-3 rounded-2xl border border-gray-200 hover:border-ink hover:bg-soft transition-all"
                        >
                            <div class="w-10 h-10 rounded-xl bg-soft flex items-center justify-center shrink-0">
                                <Phone class="w-4 h-4 text-ink" />
                            </div>
                            <div class="flex-1 min-w-0 text-left">
                                <p class="font-bold text-sm text-ink leading-tight">Telepon Langsung</p>
                                <p class="text-[11px] text-muted leading-tight">Diskusi mendalam</p>
                            </div>
                        </a>
                        <a
                            href={mailLink}
                            class="flex items-center gap-3 p-3 rounded-2xl border border-gray-200 hover:border-ink hover:bg-soft transition-all"
                        >
                            <div class="w-10 h-10 rounded-xl bg-soft flex items-center justify-center shrink-0">
                                <Mail class="w-4 h-4 text-ink" />
                            </div>
                            <div class="flex-1 min-w-0 text-left">
                                <p class="font-bold text-sm text-ink leading-tight">Kirim Email</p>
                                <p class="text-[11px] text-muted leading-tight">Brief terstruktur</p>
                            </div>
                        </a>
                        <div class="pt-1 border-t border-gray-100 text-center">
                            <button
                                type="button"
                                on:click={dismiss}
                                class="text-[11px] text-muted hover:text-ink transition"
                            >
                                Sembunyikan sementara
                            </button>
                        </div>
                    </div>
                </div>
            {/if}
        {:else}
            <!-- Desktop: always-expanded vertical channel panel (high-convert) -->
            <div class="pointer-events-auto sticky-panel bg-white rounded-2xl shadow-2xl border border-gray-100 w-[280px] overflow-hidden">
                <div class="relative bg-gradient-to-br from-ink via-primary-2 to-ink px-4 py-4 text-white">
                    <div class="absolute inset-0 pointer-events-none" style="background: radial-gradient(circle at 80% 20%, rgba(245,158,11,0.25) 0%, transparent 50%);"></div>
                    <button
                        type="button"
                        on:click={dismiss}
                        aria-label="Sembunyikan"
                        class="absolute top-2.5 right-2.5 w-7 h-7 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition"
                    >
                        <X class="w-3.5 h-3.5" />
                    </button>
                    <div class="relative flex items-center gap-2.5">
                        <div class="relative">
                            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-accent to-orange-500 flex items-center justify-center shadow-lg">
                                <svg class="w-5 h-5 text-ink" fill="currentColor" viewBox="0 0 24 24"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448L.057 24z"/></svg>
                            </div>
                            <span class="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 rounded-full border-2 border-ink live-dot"></span>
                        </div>
                        <div class="min-w-0">
                            <p class="font-display font-bold text-sm leading-tight">Konsultan Beriklan</p>
                            <p class="text-[10px] text-white/70 mt-0.5">Respon 1 jam · jam kerja</p>
                        </div>
                    </div>
                </div>
                <div class="p-2.5 space-y-1.5">
                    <a
                        href={waLink}
                        target="_blank"
                        rel="noopener"
                        class="flex items-center gap-2.5 p-2.5 rounded-xl bg-ink text-white hover:bg-accent hover:text-ink transition-all group"
                    >
                        <div class="w-9 h-9 rounded-lg bg-white/10 group-hover:bg-ink/10 flex items-center justify-center shrink-0">
                            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448L.057 24z"/></svg>
                        </div>
                        <div class="flex-1 min-w-0 text-left">
                            <p class="font-bold text-sm leading-tight">Chat WhatsApp</p>
                            <p class="text-[10px] opacity-70 leading-tight">Konsultasi 15 menit</p>
                        </div>
                        <ArrowRight class="w-3.5 h-3.5 opacity-70 group-hover:translate-x-0.5 transition" />
                    </a>
                    <a
                        href={phoneLink}
                        class="flex items-center gap-2.5 p-2.5 rounded-xl hover:bg-soft transition-all"
                    >
                        <div class="w-9 h-9 rounded-lg bg-soft flex items-center justify-center shrink-0">
                            <Phone class="w-4 h-4 text-ink" />
                        </div>
                        <div class="flex-1 min-w-0 text-left">
                            <p class="font-bold text-[13px] text-ink leading-tight">+62 81.1919.328</p>
                            <p class="text-[10px] text-muted leading-tight">Telepon langsung</p>
                        </div>
                    </a>
                    <a
                        href={mailLink}
                        class="flex items-center gap-2.5 p-2.5 rounded-xl hover:bg-soft transition-all"
                    >
                        <div class="w-9 h-9 rounded-lg bg-soft flex items-center justify-center shrink-0">
                            <Mail class="w-4 h-4 text-ink" />
                        </div>
                        <div class="flex-1 min-w-0 text-left">
                            <p class="font-bold text-[13px] text-ink leading-tight">info@beriklan.co.id</p>
                            <p class="text-[10px] text-muted leading-tight">Email detail</p>
                        </div>
                    </a>
                </div>
            </div>
        {/if}

        <!-- Floating launcher — only show on mobile (FAB) or as collapse toggle on desktop -->
        {#if isMobile}
            <button
                type="button"
                on:click={toggle}
                class="pointer-events-auto relative w-14 h-14 rounded-full bg-gradient-to-br from-accent to-orange-500 text-ink shadow-2xl flex items-center justify-center fab-btn group"
                aria-label="Buka menu kontak"
                aria-expanded={isOpen}
            >
                {#if !isOpen && unread}
                    <span class="absolute inset-0 rounded-full pulse-ring"></span>
                {/if}
                <span class="relative w-6 h-6">
                    {#if isOpen}
                        <X class="w-full h-full" />
                    {:else}
                        <MessageCircle class="w-full h-full group-hover:scale-110 transition-transform" fill="currentColor" />
                    {/if}
                </span>
                {#if !isOpen && unread}
                    <span class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center border-2 border-white shadow-md">1</span>
                {/if}
            </button>
        {:else}
            <!-- Desktop mini launcher: small circular toggle to re-open if dismissed -->
            <button
                type="button"
                on:click={toggle}
                class="pointer-events-auto relative w-12 h-12 rounded-full bg-gradient-to-br from-accent to-orange-500 text-ink shadow-xl flex items-center justify-center fab-btn group"
                aria-label="Sembunyikan panel kontak"
                aria-expanded={isOpen}
            >
                <span class="relative w-5 h-5">
                    {#if isOpen}
                        <X class="w-full h-full" />
                    {:else}
                        <svg class="w-full h-full" fill="currentColor" viewBox="0 0 24 24"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448L.057 24z"/></svg>
                    {/if}
                </span>
            </button>
        {/if}
    </div>
{/if}

<style>
    .fab-btn {
        transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.25s ease;
    }
    .fab-btn:hover {
        transform: scale(1.08);
        box-shadow: 0 20px 40px -8px rgba(245, 158, 11, 0.5);
    }
    .fab-btn:active {
        transform: scale(0.96);
    }

    .pulse-ring {
        background: rgba(245, 158, 11, 0.4);
        animation: pulse-out 2s ease-out infinite;
    }
    @keyframes pulse-out {
        0% { transform: scale(1); opacity: 0.6; }
        100% { transform: scale(2); opacity: 0; }
    }

    .live-dot {
        animation: live-pulse 1.8s ease-in-out infinite;
    }
    @keyframes live-pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
        50% { box-shadow: 0 0 0 6px rgba(34, 197, 94, 0); }
    }

    .sticky-panel {
        animation: panel-in 0.32s cubic-bezier(0.34, 1.56, 0.64, 1);
        transform-origin: bottom right;
    }
    @keyframes panel-in {
        from { opacity: 0; transform: translateY(16px) scale(0.95); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
</style>
