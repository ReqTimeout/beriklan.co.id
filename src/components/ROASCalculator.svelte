<script>
    let adSpend = 5000000;
    let revenue = 15000000;
    let result = null;

    $: if (adSpend > 0 && revenue > 0) {
        const roas = revenue / adSpend;
        result = {
            value: roas.toFixed(2),
            rating: roas >= 4 ? 'baik' : roas >= 2 ? 'cukup' : 'perlu-optimasi',
            label: roas >= 4 ? 'Baik' : roas >= 2 ? 'Cukup' : 'Perlu Optimasi',
            color: roas >= 4 ? 'text-green-400' : roas >= 2 ? 'text-accent' : 'text-red-400',
            bg: roas >= 4 ? 'bg-green-500/20' : roas >= 2 ? 'bg-accent/20' : 'bg-red-500/20',
            bar: Math.min(roas / 8 * 100, 100),
        };
    } else {
        result = null;
    }

    function formatCurrency(val) {
        return 'Rp ' + val.toLocaleString('id-ID');
    }
</script>

<div class="bg-white border border-gray-100 rounded-2xl p-6 md:p-8 shadow-soft">
    <h3 class="font-display font-bold text-lg md:text-xl text-ink mb-1">Kalkulator ROAS</h3>
    <p class="text-sm text-muted mb-6">Return on Ad Spend — hitung efektivitas belanja iklan Anda.</p>

    <div class="grid md:grid-cols-2 gap-6 mb-6">
        <div>
            <label class="text-xs font-bold text-ink uppercase tracking-wider mb-2 block">Total Belanja Iklan</label>
            <div class="relative">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-sm font-bold text-muted">Rp</span>
                <input type="number" bind:value={adSpend} min="0" step="100000"
                    class="w-full pl-10 pr-4 py-3.5 bg-soft border border-gray-200 rounded-xl text-ink font-bold text-lg focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition" />
            </div>
        </div>
        <div>
            <label class="text-xs font-bold text-ink uppercase tracking-wider mb-2 block">Total Pendapatan dari Iklan</label>
            <div class="relative">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-sm font-bold text-muted">Rp</span>
                <input type="number" bind:value={revenue} min="0" step="100000"
                    class="w-full pl-10 pr-4 py-3.5 bg-soft border border-gray-200 rounded-xl text-ink font-bold text-lg focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition" />
            </div>
        </div>
    </div>

    {#if result}
        <div class="bg-ink rounded-2xl p-6 text-center">
            <p class="text-white/50 text-xs font-bold uppercase tracking-wider mb-1">ROAS Anda</p>
            <p class="font-display font-extrabold text-5xl md:text-6xl text-white">{result.value}x</p>
            <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-bold mt-3 {result.bg} {result.color}">
                {#if result.rating === 'baik'}🟢{:else if result.rating === 'cukup'}🟡{:else}🔴{/if}
                {result.label}
            </div>

            <div class="mt-5 bg-white/5 rounded-xl p-4">
                <div class="flex justify-between text-xs text-white/50 mb-2">
                    <span>0</span>
                    <span>Referensi: 4x+ = Baik</span>
                    <span>8x+</span>
                </div>
                <div class="h-2 bg-white/10 rounded-full overflow-hidden">
                    <div class="h-full rounded-full transition-all duration-700 {result.rating === 'baik' ? 'bg-green-500' : result.rating === 'cukup' ? 'bg-accent' : 'bg-red-500'}" style="width: {result.bar}%"></div>
                </div>
            </div>

            <div class="mt-4 text-left text-xs text-white/60 space-y-1">
                {#if result.rating === 'perlu-optimasi'}
                    <p>💡 ROAS di bawah 2x menandakan campaign perlu evaluasi — targeting, creative, atau landing page mungkin perlu disesuaikan.</p>
                {:else if result.rating === 'cukup'}
                    <p>💡 ROAS 2-4x cukup baik. Optimasi lanjutan bisa mendorong ke 4x+.</p>
                {:else}
                    <p>✅ ROAS di atas 4x sangat baik. Pertimbangkan scaling budget untuk hasil lebih besar.</p>
                {/if}
            </div>
        </div>
    {:else}
        <div class="bg-soft rounded-2xl p-6 text-center">
            <p class="text-muted text-sm">Masukkan angka belanja iklan dan pendapatan untuk melihat ROAS.</p>
        </div>
    {/if}

    <div class="mt-4 text-center">
        <a href="https://wa.me/62811919328?text=Halo%20Beriklan%2C%20saya%20ingin%20konsultasi%20ROAS%20campaign%20saya." target="_blank" rel="noopener" class="inline-flex items-center gap-2 text-sm font-bold text-accent hover:text-ink transition-colors">
            Konsultasi ROAS dengan Tim Beriklan →
        </a>
    </div>
</div>
