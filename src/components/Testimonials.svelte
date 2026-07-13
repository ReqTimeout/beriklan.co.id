<script>
    import { onMount } from 'svelte';
    import { Quote, Star, ArrowRight, Pause, Play } from 'lucide-svelte';

    const baseTestimonials = [
        {
            quote: 'Kami sempat mengelola iklan sendiri hampir setahun. Hasilnya naik turun dan menyita waktu tim internal. Setelah bekerja sama dengan Beriklan, ROAS meningkat dari 1.8x menjadi 4.5x dalam empat bulan. Yang paling kami apresiasi: laporan disusun dengan bahasa yang jelas dan setiap perubahan dapat kami pahami.',
            name: 'Andini Pratiwi',
            role: 'Owner',
            biz: 'Brand Skincare, Bandung',
            metric: 'ROAS 1.8x → 4.5x',
            metricLabel: 'dalam 4 bulan',
            avatar: '🧴',
            accent: 'from-amber-500 to-orange-500',
            industry: 'Skincare',
        },
        {
            quote: 'Awalnya kami skeptis menggandeng agensi, namun setelah dua bulan pertama, akhirnya kami memahami perbedaannya. Yang paling terasa: setiap Senin pagi selalu ada laporan dalam bahasa yang mudah dipahami — bukan hanya deretan angka CPM dan CTR, tetapi apa yang perlu diubah dan mengapa.',
            name: 'Rizky Maulana',
            role: 'Marketing Manager',
            biz: 'Klinik Kecantikan, Jakarta',
            metric: 'Lead konsisten 3x lipat',
            metricLabel: 'dari bulan ke-2',
            avatar: '💆',
            accent: 'from-pink-500 to-rose-500',
            industry: 'Klinik',
        },
        {
            quote: 'Kampanye TikTok Ads dari Beriklan berhasil menembus FYP secara organik. Dari nol pengikut menjadi 12.000 dalam dua bulan, dengan rasio closing 8% per video. Proses kreatif dilakukan secara kolaboratif, bukan sekadar posting rutin.',
            name: 'Bayu Adhi',
            role: 'Founder',
            biz: 'Edutech, Jakarta',
            metric: '0 → 12K pengikut',
            metricLabel: 'closing 8% / video',
            avatar: '🎓',
            accent: 'from-cyan-500 to-teal-500',
            industry: 'Edutech',
        },
        {
            quote: 'Sebagai pemilik brand F&B, saya biasanya tidak terlalu memperhatikan aspek marketing. Setelah Tim Beriklan menyampaikan laporan dengan bahasa yang mudah dipahami, baru saya sadari bahwa biaya yang sebelumnya kami keluarkan untuk agensi lain ternyata hanya menaikkan CPM tanpa hasil yang terukur. Saat ini ROI setiap bulan positif.',
            name: 'Hendro Wibowo',
            role: 'Owner',
            biz: 'Restoran Lokal, Jabodetabek',
            metric: 'ROI positif',
            metricLabel: 'tiap bulan sejak Q2',
            avatar: '🍜',
            accent: 'from-purple-500 to-pink-500',
            industry: 'F&B',
        },
        {
            quote: 'Karakteristik funnel B2B berbeda signifikan dari FMCG. Beriklan memahami hal ini dan menyusun strategi yang relevan, tanpa pendekatan copy-paste dari kampanye ritel. qualified leads kami naik 180% di Q3. Investasi yang sebanding dengan hasilnya.',
            name: 'Sarah Nathania',
            role: 'Head of Growth',
            biz: 'SaaS B2B, Jakarta',
            metric: 'Qualified leads +180%',
            metricLabel: 'di Q3 2025',
            avatar: '💼',
            accent: 'from-blue-500 to-indigo-500',
            industry: 'SaaS B2B',
        },
        {
            quote: 'Tim Beriklan mengelola akun Instagram secara menyeluruh — mulai dari penulisan skrip, penyuntingan, penjadwalan posting, hingga balasan DM. Kami hanya menerima laporan hasil. Dalam tiga bulan pertama, penjualan dari Instagram naik tiga kali lipat. Sangat membantu untuk bisnis yang sedang dalam tahap ekspansi.',
            name: 'Aulia Rahma',
            role: 'Owner',
            biz: 'Brand Fashion, Surabaya',
            metric: 'Penjualan IG naik 3x',
            metricLabel: 'dalam 3 bulan',
            avatar: '👗',
            accent: 'from-rose-500 to-red-500',
            industry: 'Fashion',
        },
    ];

    let visibleIdx = 0;
    let interval;
    let isPaused = false;
    let mounted = false;

    onMount(() => {
        mounted = true;
        startAuto();
        return () => stopAuto();
    });

    function startAuto() {
        if (interval) return;
        interval = setInterval(() => {
            if (!isPaused) visibleIdx = (visibleIdx + 1) % baseTestimonials.length;
        }, 5500);
    }
    function stopAuto() {
        if (interval) { clearInterval(interval); interval = null; }
    }
    function setIdx(i) {
        visibleIdx = i;
    }
    function togglePause() {
        isPaused = !isPaused;
    }

    const waLink = "https://wa.me/62811919328?text=Halo%20Beriklan%2C%20saya%20ingin%20konsultasi%20mengenai%20campaign%20iklan%20saya";
</script>

<section id="testimonials" class="py-20 md:py-28 bg-soft relative overflow-hidden">
    <!-- Decorative animated quote marks in background -->
    <div class="absolute -left-12 top-12 text-[180px] font-display font-black text-accent/[0.04] leading-none select-none pointer-events-none hidden lg:block" aria-hidden="true">"</div>
    <div class="absolute -right-12 bottom-12 text-[180px] font-display font-black text-accent/[0.04] leading-none select-none pointer-events-none hidden lg:block" aria-hidden="true">"</div>

    <div class="container mx-auto px-6 relative">
        <!-- Header -->
        <div class="text-center max-w-2xl mx-auto mb-12 reveal">
            <p class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-accent">
                <span class="w-8 h-px bg-accent"></span>
                Studi Kasus & Testimoni
                <span class="w-8 h-px bg-accent"></span>
            </p>
            <h2 class="font-display font-extrabold text-3xl md:text-5xl text-ink leading-[1.1] tracking-tight mt-3">
                Pengalaman mereka yang telah<br/>
                <span class="text-accent">bekerja sama dengan Tim Beriklan.</span>
            </h2>
            <p class="mt-4 text-muted max-w-xl mx-auto text-base leading-relaxed">
                Setiap testimoni disertai nama, industri, serta data yang terukur. Anda dapat melakukan verifikasi langsung kepada klien kami bila diperlukan.
            </p>
        </div>

        <!-- Marquee row 1 (always moving) -->
        <div class="mb-6 overflow-hidden marquee-row relative">
            <div class="flex gap-3 marquee-track" style="animation: marquee-left 40s linear infinite;">
                {#each [...baseTestimonials, ...baseTestimonials] as t, i}
                    <div class="marquee-card shrink-0 bg-white border border-gray-100 rounded-xl px-4 py-3 shadow-soft hover:shadow-pop hover:border-accent/30 transition-all">
                        <div class="flex items-center gap-2">
                            <div class="w-9 h-9 rounded-full bg-gradient-to-br {t.accent} flex items-center justify-center text-base shrink-0">{t.avatar}</div>
                            <div class="min-w-0">
                                <p class="text-xs font-bold text-ink truncate">{t.name}</p>
                                <p class="text-[10px] text-muted truncate">{t.industry} · {t.biz.split(',')[0]}</p>
                            </div>
                            <div class="text-right shrink-0 ml-3 pl-3 border-l border-gray-100">
                                <p class="text-[11px] font-extrabold text-accent whitespace-nowrap">{t.metric}</p>
                            </div>
                        </div>
                    </div>
                {/each}
            </div>
        </div>

        <!-- Featured testimonial (auto-rotates with pause on hover) -->
        <div
            class="max-w-4xl mx-auto mb-8"
            on:mouseenter={() => isPaused = true}
            on:mouseleave={() => isPaused = false}
        >
            {#key visibleIdx}
                {@const t = baseTestimonials[visibleIdx]}
                <article class="tst-featured bg-white rounded-2xl p-6 md:p-10 shadow-pop border border-gray-100 relative overflow-hidden">
                    <div class="absolute -top-20 -right-20 w-60 h-60 bg-gradient-to-br {t.accent} opacity-[0.08] rounded-full blur-3xl pointer-events-none"></div>
                    <div class="absolute -bottom-16 -left-16 w-48 h-48 bg-accent/10 rounded-full blur-3xl pointer-events-none"></div>
                    <div class="relative">
                        <div class="flex items-start justify-between gap-4 mb-5">
                            <div class="flex items-center gap-3">
                                <div class="quote-bubble w-12 h-12 rounded-2xl bg-gradient-to-br {t.accent} flex items-center justify-center text-white shadow-pop">
                                    <Quote class="w-5 h-5" fill="currentColor" />
                                </div>
                                <div class="flex items-center gap-0.5">
                                    {#each [1,2,3,4,5] as _}
                                        <svg class="w-4 h-4 text-accent star-twinkle" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
                                    {/each}
                                </div>
                            </div>
                            <!-- Pause toggle -->
                            <button
                                type="button"
                                on:click={togglePause}
                                aria-label={isPaused ? 'Lanjutkan rotasi' : 'Jeda rotasi'}
                                class="hidden md:flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-muted hover:text-accent transition px-2 py-1 rounded-full border border-gray-200 hover:border-accent"
                            >
                                {#if isPaused}
                                    <Play class="w-3 h-3" fill="currentColor" />
                                {:else}
                                    <Pause class="w-3 h-3" fill="currentColor" />
                                {/if}
                                {isPaused ? 'Lanjut' : 'Jeda'}
                            </button>
                        </div>
                        <p class="text-ink text-base md:text-lg leading-relaxed mb-7 relative">
                            <span class="text-accent text-3xl font-display font-extrabold leading-none mr-1 align-top">"</span>{t.quote}<span class="text-accent text-3xl font-display font-extrabold leading-none ml-1 align-bottom">"</span>
                        </p>
                        <div class="flex items-center gap-4 pt-5 border-t border-gray-100">
                            <div class="w-14 h-14 rounded-full bg-gradient-to-br {t.accent} flex items-center justify-center text-2xl shrink-0 ring-4 ring-white shadow-pop">{t.avatar}</div>
                            <div class="flex-1 min-w-0">
                                <p class="font-bold text-ink text-base">{t.name}</p>
                                <p class="text-xs text-muted mt-0.5">{t.role} · {t.biz}</p>
                            </div>
                            <div class="text-right shrink-0 hidden sm:block metric-badge bg-gradient-to-br {t.accent} text-white px-4 py-2.5 rounded-xl">
                                <p class="text-base font-extrabold leading-tight">{t.metric}</p>
                                <p class="text-[10px] opacity-90 leading-tight mt-0.5">{t.metricLabel}</p>
                            </div>
                        </div>
                    </div>
                </article>
            {/key}

            <!-- Progress bar showing auto-rotate progress -->
            <div class="mt-4 max-w-4xl mx-auto h-1 bg-gray-200 rounded-full overflow-hidden">
                <div class="h-full bg-gradient-to-r from-accent via-orange-400 to-accent progress-bar {isPaused ? 'paused' : ''}" style="animation: progress-fill 5.5s linear infinite;"></div>
            </div>
        </div>

        <!-- Pager dots -->
        <div class="flex items-center justify-center gap-2 mb-12">
            {#each baseTestimonials as _, i}
                <button
                    type="button"
                    on:click={() => setIdx(i)}
                    aria-label="Lihat testimoni {i + 1}"
                    class="pager-dot transition-all duration-300 rounded-full {visibleIdx === i ? 'w-10 bg-accent' : 'w-2 bg-gray-300 hover:bg-gray-400'}"
                    style="height: 8px;"
                ></button>
            {/each}
        </div>

        <!-- Compact mini-cards row (clickable, hover preview) -->
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 max-w-6xl mx-auto reveal-stagger">
            {#each baseTestimonials as t, i}
                <button
                    type="button"
                    on:click={() => setIdx(i)}
                    aria-label="Lihat testimoni dari {t.name}"
                    class="tst-mini group bg-white border rounded-xl p-3 text-left transition-all duration-300 hover:shadow-pop hover:-translate-y-1 {visibleIdx === i ? 'border-accent shadow-pop ring-2 ring-accent/20' : 'border-gray-100'}"
                >
                    <div class="flex items-center gap-2 mb-2">
                        <div class="w-9 h-9 rounded-full bg-gradient-to-br {t.accent} flex items-center justify-center text-base shrink-0">{t.avatar}</div>
                        <div class="min-w-0">
                            <p class="text-xs font-bold text-ink truncate">{t.name.split(' ')[0]}</p>
                            <p class="text-[10px] text-muted truncate">{t.industry}</p>
                        </div>
                    </div>
                    <p class="text-xs font-extrabold text-accent leading-tight">{t.metric}</p>
                </button>
            {/each}
        </div>

        <div class="mt-12 text-center">
            <p class="text-muted italic mb-4 reveal">
                Saatnya giliran Anda. <span class="text-ink font-semibold not-italic">Mari kita telaah campaign Anda secara mendalam.</span>
            </p>
            <a href={waLink} target="_blank" rel="noopener" class="reveal inline-flex items-center gap-2 bg-ink text-white px-7 py-3.5 rounded-full font-bold text-sm hover:bg-accent hover:text-ink transition shadow-md group">
                Jadwalkan Konsultasi
                <ArrowRight class="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </a>
        </div>
    </div>
</section>

<style>
    .tst-featured {
        animation: tst-enter 0.55s cubic-bezier(0.22, 1, 0.36, 1);
    }
    @keyframes tst-enter {
        from { opacity: 0; transform: translateY(14px) scale(0.985); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }

    .tst-mini {
        transition: border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease, background-color 0.3s ease;
    }
    .tst-mini:active { transform: scale(0.97); }

    /* Stagger fade-in for mini cards */
    .tst-mini { opacity: 0; animation: mini-in 0.45s cubic-bezier(0.22, 1, 0.36, 1) forwards; }
    .tst-mini:nth-child(1) { animation-delay: 0.05s; }
    .tst-mini:nth-child(2) { animation-delay: 0.10s; }
    .tst-mini:nth-child(3) { animation-delay: 0.15s; }
    .tst-mini:nth-child(4) { animation-delay: 0.20s; }
    .tst-mini:nth-child(5) { animation-delay: 0.25s; }
    .tst-mini:nth-child(6) { animation-delay: 0.30s; }
    @keyframes mini-in {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Pager dot pulse */
    .pager-dot {
        transition: width 0.35s cubic-bezier(0.22, 1, 0.36, 1), background-color 0.25s ease, transform 0.25s ease;
    }
    .pager-dot:hover { transform: scaleY(1.4); }

    /* Quote bubble subtle pulse */
    .quote-bubble {
        animation: bubble-in 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    @keyframes bubble-in {
        from { opacity: 0; transform: scale(0.5) rotate(-12deg); }
        to { opacity: 1; transform: scale(1) rotate(0); }
    }

    /* Stars twinkle on featured enter */
    .star-twinkle {
        animation: star-twinkle 1.5s ease 0.4s backwards;
    }
    @keyframes star-twinkle {
        0% { opacity: 0; transform: scale(0.5) rotate(-30deg); }
        60% { opacity: 1; transform: scale(1.2) rotate(8deg); }
        100% { opacity: 1; transform: scale(1) rotate(0); }
    }

    /* Metric badge hover */
    .metric-badge {
        transition: transform 0.3s ease;
    }
    .tst-featured:hover .metric-badge {
        transform: scale(1.06);
    }

    /* Marquee */
    .marquee-row::before,
    .marquee-row::after {
        content: '';
        position: absolute;
        top: 0; bottom: 0;
        width: 60px;
        z-index: 2;
        pointer-events: none;
    }
    .marquee-row::before {
        left: 0;
        background: linear-gradient(90deg, #f8f5f0 0%, transparent 100%);
    }
    .marquee-row::after {
        right: 0;
        background: linear-gradient(-90deg, #f8f5f0 0%, transparent 100%);
    }
    @keyframes marquee-left {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }
    .marquee-card { transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease; }
    .marquee-card:hover {
        transform: translateY(-2px);
    }

    /* Progress bar */
    @keyframes progress-fill {
        from { transform: scaleX(0); transform-origin: left; }
        to { transform: scaleX(1); transform-origin: left; }
    }
    .progress-bar { transform-origin: left; }
    .progress-bar.paused { animation-play-state: paused !important; }

    @media (prefers-reduced-motion: reduce) {
        .tst-featured, .tst-mini, .marquee-track, .progress-bar, .star-twinkle, .quote-bubble { animation: none !important; opacity: 1; transform: none; }
    }
</style>
