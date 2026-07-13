<script>
    import { onMount, tick } from 'svelte';
    import { fly, fade } from 'svelte/transition';
    import { Megaphone, Search, Music2, Layers, Sprout, Leaf, TreePine, Rocket, Timer, Calendar, CalendarDays, Trophy, Phone, ShoppingCart, Megaphone as MegaphoneIcon, Globe } from 'lucide-svelte';

    let visible = false;
    let currentStep = 0;
    let direction = 1;
    let answers = {
        platform: null,
        budget: null,
        duration: null,
        goal: null,
    };

    const platforms = [
        { id: 'meta', Icon: Megaphone, label: 'Meta Ads', sub: 'Facebook + Instagram' },
        { id: 'google', Icon: Search, label: 'Google Ads', sub: 'Search + YouTube' },
        { id: 'tiktok', Icon: Music2, label: 'TikTok Ads', sub: 'FYP + Spark' },
        { id: 'multi', Icon: Layers, label: 'Multi-platform', sub: '2+ platforms' },
    ];

    const budgets = [
        { id: '<5', Icon: Sprout, label: '< Rp 5jt', sub: 'Testing awal' },
        { id: '5-15', Icon: Leaf, label: 'Rp 5–15jt', sub: 'Sudah berjalan' },
        { id: '15-50', Icon: TreePine, label: 'Rp 15–50jt', sub: 'Siap scale' },
        { id: '50+', Icon: Rocket, label: 'Rp 50jt+', sub: 'Enterprise' },
    ];

    const durations = [
        { id: '<3', Icon: Timer, label: '< 3 bulan', sub: 'Baru mulai' },
        { id: '3-6', Icon: Calendar, label: '3–6 bulan', sub: 'Cari validasi' },
        { id: '6-12', Icon: CalendarDays, label: '6–12 bulan', sub: 'Sudah PMF' },
        { id: '12+', Icon: Trophy, label: '> 1 tahun', sub: 'Mapan, optimasi' },
    ];

    const goals = [
        { id: 'leads', Icon: Phone, label: 'Leads / Inquiry', sub: 'Penjualan via chat/call' },
        { id: 'sales', Icon: ShoppingCart, label: 'Direct Sales', sub: 'Transaksi langsung' },
        { id: 'awareness', Icon: MegaphoneIcon, label: 'Brand Awareness', sub: 'Jangkauan luas' },
        { id: 'traffic', Icon: Globe, label: 'Website Traffic', sub: 'Kunjungan organik' },
    ];

    const questions = [
        { key: 'platform', title: 'Platform iklan mana yang jadi fokus utama?', sub: 'Pilih yang paling dominan di campaign Anda saat ini.', data: platforms },
        { key: 'budget', title: 'Berapa budget iklan yang Anda alokasikan per bulan?', sub: 'Termasuk ad spend + biaya agency (kalau ada).', data: budgets },
        { key: 'duration', title: 'Sudah berapa lama Anda jalanin iklan digital?', sub: 'Termasuk yang Anda kelola sendiri atau pakai agency lain.', data: durations },
        { key: 'goal', title: 'Apa objective utama campaign Anda?', sub: 'Fokus goal yang paling ingin dicapai 6 bulan ke depan.', data: goals },
    ];

    // Recommendation matrix — heuristic
    function getRecommendation() {
        const { platform, budget, duration, goal } = answers;
        let pkg = 'Starter';
        let price = '2.500.000';
        let matchScore = 95;
        let reasoning = [];

        if (budget === '<5') { pkg = 'Starter'; price = '2.500.000'; reasoning.push('Cocok untuk tahap testing awal.'); matchScore = 92; }
        else if (budget === '5-15') { pkg = 'Growth'; price = '5.000.000'; reasoning.push('Sudah menemukan product-market fit, siap untuk scale-up.'); matchScore = 96; }
        else if (budget === '15-50') { pkg = 'Scale'; price = '10.000.000+'; reasoning.push('Budget besar butuh full funnel management.'); matchScore = 98; }
        else { pkg = 'Scale'; price = 'Custom'; reasoning.push('Custom retainer — dedicated team untuk hasil maksimal.'); matchScore = 99; }

        if (duration === '<3' && goal === 'awareness') reasoning.push('Fokus ke creative testing di awal untuk find winning formula.');
        if (duration === '12+' && goal === 'sales') reasoning.push('Tinggal refine — optimasi CPA + scale yang sudah jalan.');
        if (platform === 'multi') reasoning.push('Multi-platform perlu creative variant per channel.');
        if (platform === 'tiktok' && goal === 'leads') reasoning.push('TikTok cocok untuk top funnel, perlu pairing Meta untuk retargeting.');

        return { pkg, price, matchScore, reasoning };
    }

    function selectOption(key, optId) {
        answers[key] = optId;
        direction = 1;
        if (currentStep < questions.length - 1) {
            setTimeout(() => {
                currentStep += 1;
            }, 350);
        } else {
            setTimeout(() => {
                currentStep = questions.length;
            }, 350);
        }
    }

    function back() {
        if (currentStep > 0) {
            direction = -1;
            currentStep -= 1;
            answers[questions[currentStep].key] = null;
        }
    }

    function reset() {
        answers = { platform: null, budget: null, duration: null, goal: null };
        currentStep = 0;
        direction = 1;
    }

    $: done = currentStep >= questions.length;
    $: recommendation = done ? getRecommendation() : null;
    $: progress = done ? 100 : (currentStep / questions.length) * 100;

    onMount(() => {
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                visible = true;
                observer.disconnect();
            }
        }, { threshold: 0.1 });
        const el = document.getElementById('audit');
        if (el) observer.observe(el);
        setTimeout(() => { visible = true; }, 1200);
    });
</script>

<section id="audit" class="py-20 md:py-28 bg-gradient-to-br from-ink via-primary-2 to-ink text-white relative overflow-hidden">
    <!-- Static radial accent (cheaper than animated blur orbs) -->
    <div class="absolute inset-0 pointer-events-none" style="background: radial-gradient(circle at 15% 25%, rgba(245, 158, 11, 0.12) 0%, transparent 40%), radial-gradient(circle at 85% 75%, rgba(14, 165, 233, 0.10) 0%, transparent 40%);"></div>
    <!-- Pattern -->
    <div class="absolute inset-0 opacity-[0.04] pointer-events-none" style="background-image: radial-gradient(circle at 2px 2px, white 1px, transparent 0); background-size: 32px 32px;"></div>

    <div class="container mx-auto px-6 relative">
        <div class="text-center max-w-2xl mx-auto mb-10">
            <p class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-accent mb-4">
                <span class="w-8 h-px bg-accent"></span>
                AI Audit · 60 detik
                <span class="w-8 h-px bg-accent"></span>
            </p>
            <h2 class="font-display font-extrabold text-3xl md:text-5xl leading-[1.15] tracking-tight">
                Jawab 4 pertanyaan,
                <span class="block mt-2 text-accent">kami rekomendasikan paket Anda.</span>
            </h2>
            <p class="mt-4 text-white/60 text-sm md:text-base">Bukan kuis tanpa isi — Anda akan memperoleh estimasi paket + range harga yang cocok untuk situasi Anda saat ini.</p>
        </div>

        <!-- Progress bar -->
        <div class="max-w-3xl mx-auto mb-8">
            <div class="flex items-center justify-between mb-2 text-xs text-white/60">
                <span>Step {!done ? currentStep + 1 : questions.length} / {questions.length}</span>
                <span>{Math.round(progress)}% selesai</span>
            </div>
            <div class="h-1.5 bg-white/10 rounded-full overflow-hidden">
                <div class="h-full bg-gradient-to-r from-accent to-orange-400 rounded-full transition-all duration-700" style="width: {progress}%"></div>
            </div>
        </div>

        <!-- Card -->
        <div class="max-w-3xl mx-auto bg-white/5 backdrop-blur-md border border-white/10 rounded-3xl p-6 md:p-10 min-h-[420px] flex flex-col">

            {#if !done}
                {#key currentStep}
                    <div class="flex-1 flex flex-col" in:fly={{ y: 20 * direction, duration: 400 }} out:fly={{ y: -20 * direction, duration: 300 }}>
                        <h3 class="font-display font-bold text-xl md:text-2xl mb-2">
                            {questions[currentStep].title}
                        </h3>
                        <p class="text-white/50 text-sm mb-6">{questions[currentStep].sub}</p>

                        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 flex-1">
                            {#each questions[currentStep].data as opt}
                                <button
                                    type="button"
                                    on:click={() => selectOption(questions[currentStep].key, opt.id)}
                                    class="group relative bg-white/5 hover:bg-accent hover:text-ink border-2 {answers[questions[currentStep].key] === opt.id ? 'border-accent bg-accent/10 text-ink' : 'border-white/10'} rounded-2xl p-4 md:p-5 transition-all duration-300 hover:-translate-y-1 hover:shadow-pop text-left"
                                >
                                    <div class="mb-3 group-hover:scale-110 transition-transform">
                                        <svelte:component this={opt.Icon} size="36" strokeWidth="2" />
                                    </div>
                                    <div class="font-bold text-sm md:text-base">{opt.label}</div>
                                    <div class="text-[10px] md:text-xs opacity-60 mt-1">{opt.sub}</div>
                                    {#if answers[questions[currentStep].key] === opt.id}
                                        <div class="absolute top-2 right-2 w-5 h-5 bg-accent rounded-full flex items-center justify-center">
                                            <svg class="w-3 h-3 text-ink" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                                        </div>
                                    {/if}
                                </button>
                            {/each}
                        </div>

                        <div class="flex items-center justify-between mt-6 pt-6 border-t border-white/10">
                            <button
                                type="button"
                                on:click={back}
                                disabled={currentStep === 0}
                                class="text-sm text-white/60 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition flex items-center gap-1"
                            >
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
                                Kembali
                            </button>
                            <span class="text-xs text-white/40">Klik salah satu opsi untuk lanjut</span>
                        </div>
                    </div>
                {/key}
            {:else}
                <div in:fly={{ y: 30, duration: 600 }}>
                    <!-- Result -->
                    <div class="text-center mb-6">
                        <div class="inline-flex items-center gap-2 px-4 py-2 bg-green-500/20 text-green-300 rounded-full text-xs font-bold mb-4">
                            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>
                            Audit selesai · Match score {recommendation.matchScore}%
                        </div>
                        <p class="text-white/60 text-sm mb-2">Berdasarkan jawaban Anda, kami rekomendasikan:</p>
                        <h3 class="font-display font-extrabold text-4xl md:text-5xl text-accent mb-2">Paket {recommendation.pkg}</h3>
                        <p class="text-white/70 text-sm">Estimasi biaya: <span class="font-bold text-white">Rp {recommendation.price}</span> / bulan</p>
                    </div>

                    <div class="bg-white/5 border border-white/10 rounded-2xl p-5 mb-6">
                        <p class="text-xs font-bold uppercase tracking-wider text-accent mb-3">💡 Kenapa paket ini:</p>
                        <ul class="space-y-2">
                            {#each recommendation.reasoning as r}
                                <li class="flex items-start gap-2 text-sm text-white/80">
                                    <svg class="w-4 h-4 text-accent mt-0.5 shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                                    <span>{r}</span>
                                </li>
                            {/each}
                        </ul>
                    </div>

                    <div class="flex flex-col sm:flex-row gap-3">
                        <a href="https://wa.me/62811919328?text=Halo%20Beriklan%2C%20saya%20baru%20selesai%20audit%20dan%20direkomendasikan%20paket%20{recommendation.pkg}" target="_blank" rel="noopener" class="flex-1 inline-flex items-center justify-center gap-2 bg-accent text-ink px-6 py-3 rounded-full font-bold hover:bg-accent-2 hover:shadow-pop transition-all">
                            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448L.057 24z"/></svg>
                            Diskusi Paket Ini
                        </a>
                        <button type="button" on:click={reset} class="px-6 py-3 rounded-full font-bold border border-white/20 text-white hover:bg-white/5 transition">
                            Ulangi Audit
                        </button>
                    </div>
                </div>
            {/if}
        </div>

        <p class="text-center text-xs text-white/40 mt-6">
            🔒 Data Anda aman — tidak disimpan, hanya untuk rekomendasi langsung.
        </p>
    </div>
</section>

<style>
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-12px); }
    }
</style>
