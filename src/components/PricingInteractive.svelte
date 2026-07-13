<script>
    import { fade, fly } from 'svelte/transition';
    
    // State: false = Bulanan, true = Tahunan
    let isYearly = false;
    
    // Link base untuk register
    const regBase = "https://platform.haloka.id/register?billing_type=";

    // DATA PAKET REAL
    const packages = [
        {
            id: 'haloka_sapa',
            name: 'Haloka Sapa',
            priceMonthly: 699000,
            desc: 'Solusi hemat untuk toko online yang baru merintis. Sapa setiap pelanggan 24 jam non-stop.',
            features: [
                '1 Platform (WhatsApp)',
                '1 AI Agent',
                '1 Human Agent',
                '2.000 Balasan AI / Bulan',
                'Max 10 Produk & AI Learning',
                'Unlimited Chat & Inbox',
                'Haloka Calendar',
                'Auto Follow Up'
            ],
            isPopular: false,
            colorClass: 'border-gray-100 hover:border-gray-300 hover:shadow-xl'
        },
        {
            id: 'haloka_sobat',
            name: 'Haloka Sobat',
            priceMonthly: 1599000,
            desc: 'Sobat terbaik admin Anda. Prioritas respon lebih cepat & handle ribuan chat otomatis.',
            features: [
                '3 Platform (WhatsApp)',
                '2 AI Agent',
                '3 Human Agent',
                '5.000 Balasan AI / Bulan',
                'Max 30 Produk & AI Learning',
                'Unlimited Chat & Inbox',
                'Prioritas Respon Cepat',
                'Image & Voice Note Reply'
            ],
            isPopular: true, 
            colorClass: 'border-blue-500 shadow-2xl shadow-blue-500/20 ring-1 ring-blue-500 transform scale-105 z-10'
        },
        {
            id: 'haloka_juragan',
            name: 'Haloka Juragan',
            priceMonthly: 3999000,
            desc: 'Full Power Automation. Kapasitas besar untuk brand yang ingin menggantikan biaya tim CS shift.',
            features: [
                '3 Platform (WhatsApp)',
                '2 AI Agent + 3 Human Agent',
                '5.000 Balasan AI / Bulan',
                'Max 30 Produk & AI Learning',
                'Unlimited Chat, Inbox, Reply',
                'Haloka Calendar & Booking',
                'Auto Follow Up & Broadcast',
                'Full Support'
            ],
            isPopular: false,
            colorClass: 'border-orange-200 hover:border-orange-400 bg-orange-50/10'
        }
    ];

    // Formatter Rupiah
    const formatIDR = (num) => new Intl.NumberFormat('id-ID', { maximumFractionDigits: 0 }).format(num);
</script>

<section class="py-24 bg-white relative overflow-hidden">
    
    <div class="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div class="absolute top-[10%] right-[5%] w-[500px] h-[500px] bg-blue-50 rounded-full blur-3xl opacity-40 mix-blend-multiply"></div>
        <div class="absolute bottom-[10%] left-[5%] w-[500px] h-[500px] bg-green-50 rounded-full blur-3xl opacity-40 mix-blend-multiply"></div>
    </div>

    <div class="max-w-7xl mx-auto px-4 relative z-10">
        
        <div class="text-center max-w-3xl mx-auto mb-16">
            <h2 class="font-display font-black text-3xl md:text-5xl text-gray-900 mb-6">
                Investasi Cerdas untuk<br>
                <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-500">Pertumbuhan Bisnis</span>
            </h2>
            <p class="text-gray-500 text-lg">
                Pilih kapasitas yang sesuai dengan volume chat dan target omzet Kaka. Upgrade kapan saja saat bisnis makin besar.
            </p>
        </div>

        <div class="flex justify-center items-center mb-20 select-none">
            <div 
                class="relative bg-gray-200 p-1.5 rounded-full flex items-center cursor-pointer shadow-inner transition-colors duration-500 w-[260px] h-[56px] 
                {isYearly ? 'ring-2 ring-green-400 bg-green-100' : ''}" 
                on:click={() => isYearly = !isYearly}
            >
                
                <div class="absolute top-1.5 bottom-1.5 w-[calc(50%-6px)] rounded-full shadow-md transition-all duration-500 ease-[cubic-bezier(0.25,1,0.5,1)] transform
                    {isYearly ? 'translate-x-[100%] bg-green-600' : 'translate-x-0 bg-white'}">
                </div>

                <div class="relative z-10 w-1/2 text-center text-sm font-bold transition-colors duration-300 
                    {isYearly ? 'text-gray-500' : 'text-gray-900'}">
                    Bulanan
                </div>

                <div class="relative z-10 w-1/2 text-center text-sm font-bold transition-colors duration-300 flex items-center justify-center gap-2
                    {isYearly ? 'text-white' : 'text-gray-500'}">
                    Tahunan
                </div>
            </div>
            
            <div class="absolute mt-16 transition-all duration-300 {isYearly ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-2'}">
                <span class="bg-red-100 text-red-600 text-[10px] px-3 py-1 rounded-full border border-red-200 animate-pulse font-extrabold shadow-sm">
                    🔥 Hemat 17%
                </span>
            </div>
        </div>

        <div class="grid md:grid-cols-3 gap-8 items-start">
            {#each packages as pkg}
                <div id={pkg.id} class="relative bg-white rounded-[2rem] p-8 transition-all duration-500 flex flex-col h-full group border-2 {pkg.colorClass}">
                    
                    {#if pkg.isPopular}
                        <div class="absolute -top-5 left-1/2 -translate-x-1/2 bg-gradient-to-r from-blue-600 to-blue-500 text-white px-6 py-1.5 rounded-full text-xs font-bold shadow-lg tracking-wide ring-4 ring-white z-20">
                            ✨ PALING DIMINATI
                        </div>
                    {/if}

                    <div class="text-center mb-6 pt-2">
                        <h3 class="font-display font-bold text-2xl text-gray-900 mb-3">{pkg.name}</h3>
                        <p class="text-xs text-gray-500 leading-relaxed min-h-[40px] px-2 font-medium">{pkg.desc}</p>
                    </div>

                    <div class="text-center mb-8 pb-8 border-b border-dashed border-gray-200 relative h-28 flex items-center justify-center">
                        {#key isYearly}
                            <div in:fly={{ y: 20, duration: 300 }} class="absolute w-full">
                                <div class="flex items-start justify-center text-gray-900 font-bold">
                                    <span class="text-lg mt-2 mr-1 text-gray-400">Rp</span>
                                    <span class="text-5xl tracking-tight">
                                        {isYearly ? formatIDR(pkg.priceMonthly * 12 * 0.83) : formatIDR(pkg.priceMonthly)}
                                    </span>
                                </div>
                                <div class="text-xs text-gray-400 mt-2 font-bold uppercase tracking-wider">
                                    {isYearly ? '/tahun (Bayar sekaligus)' : '/bulan'}
                                </div>
                                {#if isYearly}
                                    <div class="mt-2">
                                        <span class="text-[10px] text-green-700 font-bold bg-green-100 px-3 py-1 rounded-full">
                                            Jatuhnya Rp {formatIDR(pkg.priceMonthly * 0.83)}/bln
                                        </span>
                                    </div>
                                {/if}
                            </div>
                        {/key}
                    </div>

                    <ul class="space-y-4 mb-10 text-sm text-gray-600 flex-1 px-2">
                        {#each pkg.features as feat}
                            <li class="flex items-start gap-3 group-hover:text-gray-900 transition-colors">
                                <div class="w-5 h-5 rounded-full bg-blue-50 flex-shrink-0 flex items-center justify-center text-blue-600 font-bold text-xs mt-0.5">
                                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg>
                                </div>
                                <span class="leading-snug">{feat}</span>
                            </li>
                        {/each}
                    </ul>

                    {#if pkg.id === 'haloka_sapa'}
                        <div class="flex flex-col items-center justify-center mb-2 animate-bounce-slow">
                            <span class="text-[11px] font-bold text-green-600 mb-1">Ambil Trial Gratis Sekarang</span>
                            <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
                            </svg>
                        </div>
                    {/if}

                    <a 
                        href="{regBase}{isYearly ? 'yearly' : 'monthly'}&package={pkg.id}" 
                        class="block w-full text-center py-4 rounded-xl font-bold transition-all duration-300 transform active:scale-[0.98] shadow-sm
                        {pkg.isPopular 
                            ? 'bg-blue-600 text-white shadow-lg shadow-blue-200 hover:bg-blue-700 hover:shadow-blue-300' 
                            : 'bg-white border-2 border-gray-200 text-gray-600 hover:border-blue-600 hover:text-blue-600'}"
                    >
                        {pkg.id === 'haloka_sapa' ? 'Coba Gratis 7 Hari' : `Pilih ${pkg.name}`}
                    </a>
                    
                </div>
            {/each}
        </div>
        
        <div class="mt-20 text-center border-t border-gray-100 pt-8">
            <p class="text-gray-500 text-sm">
                Butuh kuota lebih besar atau Custom Integration? 
                <a href="https://wa.me/62811919328" class="text-blue-600 font-bold hover:text-blue-800 transition-colors ml-1">Hubungi Tim Enterprise</a>
            </p>
        </div>

    </div>
</section>

<style>
    /* Custom bounce yang lebih halus/slow dibanding default Tailwind */
    @keyframes bounce-slow {
        0%, 100% {
            transform: translateY(-15%);
            animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
        }
        50% {
            transform: translateY(0);
            animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
        }
    }
    .animate-bounce-slow {
        animation: bounce-slow 2s infinite;
    }
</style>