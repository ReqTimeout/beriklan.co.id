<script>
    import { onMount } from 'svelte';
    import { Store, Search, ShieldAlert, BarChart3, ArrowRight, Repeat } from 'lucide-svelte';

    let mounted = false;
    let activePain = 0;

    const pains = [
        {
            num: '01',
            Icon: Store,
            tag: 'Marketplace Fee Trap',
            title: '"Margin habis untuk platform fee"',
            body: 'Shopee, Tokopedia, dan marketplace lain memungut komisi 1–5% per transaksi, biaya layanan, biaya fitur promosi, dan biaya pencairan saldo. Setiap kali Anda naik brand awareness lewat iklan internal marketplace, biaya tastam terus. Anda bukan memilikikan bisnis — Anda menyewa rak milik platform.',
            stat: '2.5%+ komisi per transaksi',
            statLabel: 'rata-rata biaya marketplace Indonesia'
        },
        {
            num: '02',
            Icon: Search,
            tag: 'Invisible di Google',
            title: '"Toko Anda tidak pernah muncul di Google"',
            body: 'Halaman toko di marketplace tertutup login, captcha, dan domain marketplace — yang dirayapi Google adalah marketplace-nya, bukan toko Anda. Brand Anda tidak bisa ranking di pencarian "nama brand + produk". Setiap calon pembeli yang cari di Google pergi ke kompetitor punya website sendiri.',
            stat: '93% belanja online',
            statLabel: 'dimulai dari pencarian Google ( Behaviour Indonesia, 2025 )'
        },
        {
            num: '03',
            Icon: ShieldAlert,
            tag: 'No Data, No Authority',
            title: '"Anda tidak punya data pelanggan"',
            body: 'Marketplace menyimpan nomor HP, email, riwayat belanja, dan behavior pembeli — Anda tidak punya akses penuh. Saat ingin re-marketing via WhatsApp blast, email newsletter, atau launch produk baru, Anda harus bayar lagi ke platform untuk akses list yang seharusnya milik Anda.',
            stat: '0 akses',
            statLabel: 'ke raw data pembeli di marketplace'
        },
        {
            num: '04',
            Icon: BarChart3,
            tag: 'Algorithm Dependent',
            title: '"Bisa-bisa toko ditutup platform"',
            body: 'Algorithm marketplace mendadak turun, fitur berbayar baru, kebijakan baru yang merugikan, atau toko dibekukan tanpa alasan jelas — semua di luar kendali Anda. Bisnis yang sehat tidak boleh bergantung 100% pada satu platform. Website sendiri = aset digital permanen yang Anda kendalikan.',
            stat: '1 platform = 1 titik gagal',
            statLabel: 'risiko bisnis terhenti total bila algorithm berubah'
        },
    ];

    function selectPain(i) {
        activePain = i;
    }

    onMount(() => {
        mounted = true;
    });
</script>

<div class="relative max-w-6xl mx-auto {mounted ? 'is-mounted' : ''}">
    <!-- Tabs trigger (mobile + desktop) -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-2 md:gap-3 mb-6 md:mb-10">
        {#each pains as pain, i}
            <button
                type="button"
                on:click={() => selectPain(i)}
                class="pain-tab group text-left p-3 md:p-4 rounded-xl border-2 transition-all duration-300 {activePain === i ? 'border-accent bg-white shadow-soft' : 'border-gray-100 bg-white/60 hover:border-gray-300'}"
                aria-pressed={activePain === i}
            >
                <div class="flex items-center gap-2 mb-1.5">
                    <span class="w-7 h-7 rounded-lg flex items-center justify-center transition-colors {activePain === i ? 'bg-accent text-ink' : 'bg-soft text-muted'}">
                        <pain.Icon class="w-4 h-4" strokeWidth="2.2" />
                    </span>
                    <span class="text-[10px] font-bold uppercase tracking-wider {activePain === i ? 'text-accent' : 'text-muted'}">{pain.tag}</span>
                </div>
                <p class="text-[11px] md:text-xs font-semibold text-ink leading-tight line-clamp-2">{pain.title.replace(/"/g, '')}</p>
            </button>
        {/each}
    </div>

    <!-- Active pain detail -->
    {#key activePain}
    <div class="pain-detail grid md:grid-cols-5 gap-6 md:gap-10 items-center bg-white rounded-3xl border border-gray-100 p-6 md:p-10 shadow-soft">
        <div class="md:col-span-3 space-y-5">
            <div class="flex items-center gap-3">
                <span class="font-display font-extrabold text-[40px] md:text-[56px] leading-none text-accent/30 tabular-nums">{pains[activePain].num}</span>
                <span class="px-3 py-1 rounded-full bg-accent/10 text-accent text-[10px] font-bold uppercase tracking-wider">{pains[activePain].tag}</span>
            </div>
            <h3 class="font-display font-extrabold text-2xl md:text-[32px] text-ink leading-tight tracking-tight">
                {pains[activePain].title}
            </h3>
            <p class="text-base md:text-[17px] text-muted leading-relaxed">
                {pains[activePain].body}
            </p>
            <div class="flex items-center gap-2 pt-2 text-sm font-semibold text-ink">
                <Repeat class="w-4 h-4 text-accent" />
                <span>Sumber kontrol: <span class="text-accent">website milik Anda sendiri</span></span>
            </div>
        </div>

        <div class="md:col-span-2 pain-stat-card relative overflow-hidden rounded-2xl bg-gradient-to-br from-ink via-primary-2 to-ink p-6 md:p-8 text-white">
            <div class="absolute -top-10 -right-10 w-40 h-40 rounded-full bg-accent/20" style="filter: blur(40px);"></div>
            <div class="relative">
                <p class="text-xs font-bold uppercase tracking-[0.2em] text-white/50 mb-3">Realita Pasar</p>
                <p class="font-display font-extrabold text-3xl md:text-4xl leading-none mb-2">{pains[activePain].stat}</p>
                <p class="text-sm text-white/70 leading-relaxed">{pains[activePain].statLabel}</p>
                <div class="mt-6 pt-6 border-t border-white/10">
                    <p class="text-xs text-white/60 leading-relaxed">
                        Website sendiri = fondasi untuk lepas dari ketergantungan marketplace. Dengan SEO organik, Anda menarik pelanggan <span class="text-accent font-bold">tanpa biaya per-klik</span>, dan data pelanggan 100% di tangan Anda.
                    </p>
                </div>
            </div>
        </div>
    </div>
    {/key}
</div>

<style>
    .pain-tab { will-change: transform; }
    .pain-tab:active { transform: scale(0.98); }
    .line-clamp-2 {
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .pain-detail { animation: painIn 0.5s cubic-bezier(0.22, 1, 0.36, 1) backwards; }
    @keyframes painIn {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .pain-stat-card { will-change: transform; transition: transform 0.3s ease; }
    @media (hover: hover) {
        .pain-stat-card:hover { transform: translateY(-2px); }
    }
</style>