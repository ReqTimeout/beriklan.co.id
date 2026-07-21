<script>
    import { onMount } from 'svelte';
    import { fly } from 'svelte/transition';

    let step = 0;
    let direction = 1;
    let platforms = [];
    let goal = null;
    let monthlyTarget = 50000000;
    let targetIdx = 3;

    function setTarget(e) {
        targetIdx = parseInt(e.target.value);
        monthlyTarget = targetOptions[targetIdx].value;
    }

    const allPlatforms = [
        { id: 'facebook', label: 'Facebook Ads', emoji: '📘', desc: 'Target audiens presisi' },
        { id: 'instagram', label: 'Instagram Ads', emoji: '📸', desc: 'Visual + Reels discovery' },
        { id: 'tiktok', label: 'TikTok Ads', emoji: '🎵', desc: 'FYP + Spark Ads viral' },
        { id: 'google', label: 'Google Ads', emoji: '🔍', desc: 'Search high-intent traffic' },
        { id: 'youtube', label: 'YouTube Ads', emoji: '▶️', desc: 'Video + bumper awareness' },
    ];

    const goals = [
        { id: 'leads', label: 'Leads / Inquiry', desc: 'Target: leads via WhatsApp, form, telepon', multiplier: 0.25 },
        { id: 'sales', label: 'Penjualan Online', desc: 'Target: transaksi e-commerce langsung', multiplier: 0.30 },
        { id: 'awareness', label: 'Brand Awareness', desc: 'Target: reach dan impressions luas', multiplier: 0.20 },
        { id: 'traffic', label: 'Traffic Website', desc: 'Target: kunjungan ke landing page', multiplier: 0.15 },
    ];

    const targetOptions = [
        { value: 10000000, label: 'Rp 10 juta' },
        { value: 25000000, label: 'Rp 25 juta' },
        { value: 50000000, label: 'Rp 50 juta' },
        { value: 100000000, label: 'Rp 100 juta' },
        { value: 250000000, label: 'Rp 250 juta' },
        { value: 500000000, label: 'Rp 500 juta' },
        { value: 1000000000, label: 'Rp 1 miliar' },
    ];

    function togglePlatform(id) {
        if (platforms.includes(id)) {
            platforms = platforms.filter(p => p !== id);
        } else {
            platforms = [...platforms, id];
        }
    }

    function formatCurrency(val) {
        if (val >= 1000000000) return 'Rp ' + (val / 1000000000).toFixed(1) + ' miliar';
        if (val >= 1000000) return 'Rp ' + (val / 1000000).toFixed(val >= 100000000 ? 0 : 1) + ' juta';
        return 'Rp ' + val.toLocaleString('id-ID');
    }

    function getResult() {
        const baseMultiplier = goals.find(g => g.id === goal)?.multiplier || 0.25;
        const platformCount = platforms.length || 1;
        const platformFactor = 1 + (platformCount - 1) * 0.15;
        const raw = monthlyTarget * baseMultiplier * platformFactor;

        const min = Math.round(raw * 0.8 / 100000) * 100000;
        const max = Math.round(raw * 1.2 / 100000) * 100000;

        let managementFee;
        if (max <= 3000000) managementFee = 'Rp 1.000.000 - 1.750.000';
        else if (max <= 10000000) managementFee = 'Rp 1.750.000 - 3.750.000';
        else managementFee = 'Rp 3.750.000 - 6.000.000';

        let tips = [];
        if (platformCount > 2) tips.push('Fokus ke 1-2 platform dengan performa terbaik dulu sebelum ekspansi ke platform lain.');
        if (goal === 'leads' && !platforms.includes('facebook')) tips.push('Facebook Ads umumnya platform terbaik untuk leads/WhatsApp di Indonesia.');
        if (goal === 'sales' && !platforms.includes('google')) tips.push('Google Ads sangat efektif untuk direct sales karena menangkap high-intent traffic.');
        if (goal === 'awareness' && !platforms.includes('tiktok')) tips.push('TikTok punya CPM termurah untuk awareness campaign.');

        return { budgetRange: `${formatCurrency(min)} - ${formatCurrency(max)}`, managementFee, tips, min, max };
    }

    $: result = step >= 3 ? getResult() : null;
    $: progress = step >= 3 ? 100 : (step / 3) * 100;
    $: canNext = (step === 0 && platforms.length > 0) || (step === 1 && goal) || (step === 2);
    $: selectedTarget = targetOptions[targetIdx];

    function next() {
        if (canNext) { direction = 1; if (step < 3) step++; }
    }

    function prev() {
        if (step > 0) { direction = -1; step--; }
    }

    function reset() {
        platforms = []; goal = null; monthlyTarget = 50000000; step = 0;
    }

    const baseWa = 'https://wa.me/62811919328';
    function waResult() {
        const msg = encodeURIComponent(
            `Halo Beriklan, saya baru selesai kalkulasi budget iklan. Saya butuh budget iklan sekitar ${result.budgetRange} untuk ${platforms.length} platform. Mohon info lebih lanjut.`
        );
        return `${baseWa}?text=${msg}`;
    }
</script>

<section class="py-20 md:py-28 bg-gradient-to-br from-ink via-primary-2 to-ink text-white relative overflow-hidden">
    <div class="absolute inset-0 pointer-events-none" style="background: radial-gradient(circle at 15% 25%, rgba(245, 158, 11, 0.12) 0%, transparent 40%), radial-gradient(circle at 85% 75%, rgba(14, 165, 233, 0.10) 0%, transparent 40%);"></div>

    <div class="container mx-auto px-6 relative">
        <div class="max-w-2xl mx-auto">
            <div class="text-center mb-10">
                <p class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-accent mb-4">
                    <span class="w-8 h-px bg-accent"></span>
                    Kalkulator Budget Iklan
                    <span class="w-8 h-px bg-accent"></span>
                </p>
                <h2 class="font-display font-extrabold text-3xl md:text-5xl leading-[1.15] tracking-tight">
                    Berapa budget iklan yang<br/>
                    <span class="text-accent">tepat untuk bisnis Anda?</span>
                </h2>
                <p class="mt-4 text-white/60 text-sm md:text-base">Jawab 3 pertanyaan sederhana, dapatkan estimasi budget iklan + biaya management yang sesuai.</p>
            </div>

            <div class="mb-8">
                <div class="flex items-center justify-between mb-2 text-xs text-white/60">
                    <span>Step {Math.min(step + 1, 3)} / 3</span>
                    <span>{Math.round(progress)}%</span>
                </div>
                <div class="h-1.5 bg-white/10 rounded-full overflow-hidden">
                    <div class="h-full bg-gradient-to-r from-accent to-orange-400 rounded-full transition-all duration-700" style="width: {progress}%"></div>
                </div>
            </div>

            <div class="bg-white/5 backdrop-blur-md border border-white/10 rounded-3xl p-6 md:p-10 min-h-[420px] flex flex-col">
                {#if step === 0}
                    {#key step}
                        <div class="flex-1 flex flex-col" in:fly={{ y: 20, duration: 400 }}>
                            <h3 class="font-display font-bold text-xl md:text-2xl mb-2">Pilih platform iklan</h3>
                            <p class="text-white/50 text-sm mb-6">Pilih satu atau lebih platform yang ingin Anda gunakan.</p>
                            <div class="grid grid-cols-2 md:grid-cols-3 gap-3 flex-1">
                                {#each allPlatforms as p}
                                    <button type="button" on:click={() => togglePlatform(p.id)}
                                        class="relative bg-white/5 hover:bg-accent hover:text-ink border-2 {platforms.includes(p.id) ? 'border-accent bg-accent/10' : 'border-white/10'} rounded-2xl p-4 md:p-5 transition-all duration-300 hover:-translate-y-1 text-left">
                                        <div class="text-2xl mb-2">{p.emoji}</div>
                                        <div class="font-bold text-sm md:text-base">{p.label}</div>
                                        <div class="text-[10px] md:text-xs opacity-60 mt-1">{p.desc}</div>
                                        {#if platforms.includes(p.id)}
                                            <div class="absolute top-2 right-2 w-5 h-5 bg-accent rounded-full flex items-center justify-center">
                                                <svg class="w-3 h-3 text-ink" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                                            </div>
                                        {/if}
                                    </button>
                                {/each}
                            </div>
                            <div class="flex justify-between items-center mt-6 pt-6 border-t border-white/10">
                                <span class="text-xs text-white/40">Pilih minimal 1 platform</span>
                                <button type="button" on:click={next} disabled={!canNext}
                                    class="px-6 py-3 bg-accent text-ink rounded-full font-bold text-sm hover:bg-accent-2 transition disabled:opacity-40 disabled:cursor-not-allowed">
                                    Lanjut
                                </button>
                            </div>
                        </div>
                    {/key}
                {:else if step === 1}
                    {#key step}
                        <div class="flex-1 flex flex-col" in:fly={{ y: 20, duration: 400 }}>
                            <h3 class="font-display font-bold text-xl md:text-2xl mb-2">Apa tujuan utama campaign Anda?</h3>
                            <p class="text-white/50 text-sm mb-6">Pilih satu tujuan yang paling prioritas.</p>
                            <div class="grid grid-cols-2 gap-3 flex-1">
                                {#each goals as g}
                                    <button type="button" on:click={() => { goal = g.id; setTimeout(next, 400); }}
                                        class="relative bg-white/5 hover:bg-accent hover:text-ink border-2 {goal === g.id ? 'border-accent bg-accent/10' : 'border-white/10'} rounded-2xl p-4 md:p-5 transition-all duration-300 hover:-translate-y-1 text-left">
                                        <div class="font-bold text-sm md:text-base mb-1">{g.label}</div>
                                        <div class="text-[10px] md:text-xs opacity-60">{g.desc}</div>
                                        {#if goal === g.id}
                                            <div class="absolute top-2 right-2 w-5 h-5 bg-accent rounded-full flex items-center justify-center">
                                                <svg class="w-3 h-3 text-ink" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                                            </div>
                                        {/if}
                                    </button>
                                {/each}
                            </div>
                            <div class="flex justify-between items-center mt-6 pt-6 border-t border-white/10">
                                <button type="button" on:click={prev} class="text-sm text-white/60 hover:text-white transition flex items-center gap-1">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
                                    Kembali
                                </button>
                                <span class="text-xs text-white/40">Klik salah satu opsi</span>
                            </div>
                        </div>
                    {/key}
                {:else if step === 2}
                    {#key step}
                        <div class="flex-1 flex flex-col" in:fly={{ y: 20, duration: 400 }}>
                            <h3 class="font-display font-bold text-xl md:text-2xl mb-2">Target omzet bulanan?</h3>
                            <p class="text-white/50 text-sm mb-6">Perkirakan pendapatan yang ingin Anda capai per bulan dari iklan.</p>
                            <div class="flex-1 flex flex-col justify-center">
                                <div class="text-center mb-8">
                                    <p class="text-4xl md:text-5xl font-display font-extrabold text-accent">{selectedTarget?.label || formatCurrency(monthlyTarget)}</p>
                                    <p class="text-white/40 text-sm mt-2">Target omzet bulanan</p>
                                </div>
                                <input type="range" min="0" max="6" step="1" bind:value={targetIdx}
                                    on:input={setTarget}
                                    class="w-full h-2 bg-white/10 rounded-full appearance-none cursor-pointer accent-accent" />
                                <div class="flex justify-between text-[10px] text-white/40 mt-2">
                                    <span>Rp 10 jt</span>
                                    <span>Rp 1 M</span>
                                </div>
                            </div>
                            <div class="flex justify-between items-center mt-6 pt-6 border-t border-white/10">
                                <button type="button" on:click={prev} class="text-sm text-white/60 hover:text-white transition flex items-center gap-1">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
                                    Kembali
                                </button>
                                <button type="button" on:click={next} class="px-6 py-3 bg-accent text-ink rounded-full font-bold text-sm hover:bg-accent-2 transition">
                                    Hitung Budget
                                </button>
                            </div>
                        </div>
                    {/key}
                {:else}
                    <div in:fly={{ y: 30, duration: 600 }}>
                        <div class="text-center mb-6">
                            <div class="inline-flex items-center gap-2 px-4 py-2 bg-green-500/20 text-green-300 rounded-full text-xs font-bold mb-4">
                                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>
                                Kalkulasi selesai
                            </div>
                            <p class="text-white/60 text-sm mb-2">Estimasi budget iklan (ad spend) per bulan:</p>
                            <h3 class="font-display font-extrabold text-3xl md:text-4xl text-accent mb-2">{result.budgetRange}</h3>
                            <p class="text-white/50 text-xs">+ biaya management: {result.managementFee}/bln</p>
                        </div>

                        <div class="bg-white/5 border border-white/10 rounded-2xl p-5 mb-6">
                            <p class="text-xs font-bold uppercase tracking-wider text-accent mb-3">💡 Tips untuk Anda:</p>
                            <ul class="space-y-2">
                                {#each result.tips as tip}
                                    <li class="flex items-start gap-2 text-sm text-white/80">
                                        <svg class="w-4 h-4 text-accent mt-0.5 shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                                        <span>{tip}</span>
                                    </li>
                                {/each}
                            </ul>
                        </div>

                        <div class="flex flex-col sm:flex-row gap-3">
                            <a href={waResult()} target="_blank" rel="noopener" class="flex-1 inline-flex items-center justify-center gap-2 bg-accent text-ink px-6 py-3 rounded-full font-bold hover:bg-accent-2 hover:shadow-pop transition-all">
                                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448L.057 24z"/></svg>
                                Diskusi via WhatsApp
                            </a>
                            <button type="button" on:click={reset} class="px-6 py-3 rounded-full font-bold border border-white/20 text-white hover:bg-white/5 transition">Hitung Ulang</button>
                        </div>
                    </div>
                {/if}
            </div>
        </div>
    </div>
</section>
