<script>
    import { fade, fly, slide } from 'svelte/transition';
    import { onMount } from 'svelte';

    let activeStep = 1;
    let autoPlayInterval;

    // DATA MARKETING (Cerita Fiktif untuk Calon User)
    const steps = [
        { id: 1, title: "1. Hubungkan WhatsApp", desc: "Tidak perlu verifikasi ribet. Cukup scan QR Code, dan nomor WhatsApp toko Kaka langsung aktif di dashboard." },
        { id: 2, title: "2. Upload Otak AI", desc: "Punya file PDF daftar harga atau katalog produk? Upload saja. AI langsung 'menelan' semua info itu dalam hitungan detik." },
        { id: 3, title: "3. Auto Labeling", desc: "AI otomatis membedakan: Mana chat 'Cuma Tanya' (Cold) dan mana chat 'Siap Transfer' (Hot)." },
        { id: 4, title: "4. AI Handling", desc: "Lihat bagaimana AI melayani pelanggan dengan ramah, menjawab stok, hingga memberikan totalan harga." },
        { id: 5, title: "5. Pantau Profit", desc: "Tinggal cek dashboard. Lihat grafik penjualan naik karena tidak ada lagi chat yang terlewat." }
    ];

    const nextStep = () => { activeStep = activeStep < 5 ? activeStep + 1 : 1; };
    const startAutoPlay = () => { autoPlayInterval = setInterval(nextStep, 6000); }; // Slide tiap 6 detik
    const stopAutoPlay = () => clearInterval(autoPlayInterval);

    onMount(() => {
        startAutoPlay();
        return () => stopAutoPlay();
    });
</script>

<section class="py-24 bg-gray-50 overflow-hidden" id="cara-kerja">
    <div class="container mx-auto px-6">
        
        <div class="text-center mb-16">
            <h2 class="font-display font-bold text-3xl md:text-5xl text-primary mb-4">Cara Kerja Haloka</h2>
            <p class="text-gray-500">Ubah CS manual jadi otomatis dalam 5 langkah.</p>
        </div>

        <div class="grid lg:grid-cols-2 gap-12 items-center" on:mouseenter={stopAutoPlay} on:mouseleave={startAutoPlay}>
            
            <div class="space-y-3">
                {#each steps as step}
                    <button 
                        class="w-full text-left p-5 rounded-2xl transition-all duration-300 border-l-4 relative overflow-hidden group
                        {activeStep === step.id ? 'bg-white shadow-lg border-green scale-105 z-10' : 'bg-transparent border-transparent hover:bg-white/50 opacity-60 hover:opacity-100'}"
                        on:click={() => activeStep = step.id}
                    >
                        <h3 class="font-bold text-lg {activeStep === step.id ? 'text-primary' : 'text-gray-500'}">{step.title}</h3>
                        {#if activeStep === step.id}
                            <p transition:slide class="text-sm text-gray-500 mt-2 leading-relaxed">{step.desc}</p>
                            <div class="absolute bottom-0 left-0 h-1 bg-green/20 w-full mt-4">
                                <div class="h-full bg-green w-full animate-[progress_6s_linear]"></div>
                            </div>
                        {/if}
                    </button>
                {/each}
            </div>

            <div class="relative h-[480px] w-full bg-white rounded-[2rem] shadow-2xl border border-gray-100 overflow-hidden flex flex-col">
                
                <div class="bg-white border-b border-gray-100 p-4 flex justify-between items-center shadow-sm z-20">
                    <div class="flex items-center gap-2">
                        <div class="w-8 h-8 rounded bg-green flex items-center justify-center text-white font-bold text-xs">H</div>
                        <span class="font-bold text-primary text-sm">Haloka Dashboard</span>
                    </div>
                    <div class="hidden md:block bg-gray-100 px-4 py-1.5 rounded-full text-[10px] text-gray-400 font-mono w-1/2 text-center">
                        app.haloka.id/dashboard
                    </div>
                    <div class="flex gap-1.5">
                        <div class="w-2.5 h-2.5 rounded-full bg-red-400"></div>
                        <div class="w-2.5 h-2.5 rounded-full bg-yellow-400"></div>
                        <div class="w-2.5 h-2.5 rounded-full bg-green-400"></div>
                    </div>
                </div>

                <div class="flex-1 relative bg-[#f8fafc] p-6 overflow-hidden flex items-center justify-center">

                    {#if activeStep === 1}
                        <div in:fly={{ y: 20, duration: 400 }} class="w-full max-w-sm text-center">
                            <div class="bg-white p-8 rounded-2xl shadow-lg border border-gray-100 relative">
                                <h4 class="font-bold text-primary mb-1">Hubungkan WhatsApp</h4>
                                <p class="text-xs text-gray-400 mb-6">Scan QR Code untuk mulai</p>
                                
                                <div class="w-40 h-40 bg-gray-900 mx-auto rounded-xl flex items-center justify-center relative overflow-hidden group">
                                    <div class="absolute inset-0 border-4 border-green/50 rounded-xl animate-pulse"></div>
                                    <div class="w-32 h-32 border-2 border-dashed border-white/50 rounded animate-spin-slow"></div>
                                    <span class="absolute text-white text-[10px] font-bold">Scanning...</span>
                                </div>

                                <div class="mt-6 flex items-center justify-center gap-2 text-xs text-green-600 font-bold bg-green-50 py-2 rounded-lg">
                                    <span class="w-2 h-2 rounded-full bg-green animate-pulse"></span>
                                    Status: Menunggu Koneksi
                                </div>
                            </div>
                        </div>
                    {/if}

                    {#if activeStep === 2}
                        <div in:fly={{ y: 20, duration: 400 }} class="w-full max-w-sm bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
                            <div class="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                                <span class="text-xs font-bold text-primary">AI Knowledge Base</span>
                                <span class="text-[10px] bg-blue-100 text-blue-600 px-2 py-0.5 rounded">Learning Mode</span>
                            </div>
                            
                            <div class="p-6 text-center">
                                <div class="border-2 border-dashed border-blue-200 bg-blue-50/30 rounded-xl p-8 mb-4 relative overflow-hidden">
                                    <div class="text-4xl mb-2 animate-bounce">📂</div>
                                    <div class="text-xs font-bold text-gray-600">Upload PDF/Word</div>
                                    
                                    <div class="absolute bottom-0 left-0 h-1 bg-blue-500 w-full animate-[progress_2s_ease-in-out]"></div>
                                </div>

                                <div class="bg-white border border-green-200 rounded-lg p-3 flex items-center gap-3 shadow-sm text-left">
                                    <div class="w-8 h-8 bg-red-100 rounded flex items-center justify-center text-red-500 font-bold text-[10px]">PDF</div>
                                    <div class="flex-1">
                                        <div class="text-xs font-bold text-gray-800">Katalog_Lebaran_2026.pdf</div>
                                        <div class="text-[9px] text-green-600">Selesai dipelajari (100%)</div>
                                    </div>
                                    <span class="text-green text-lg">✓</span>
                                </div>
                            </div>
                        </div>
                    {/if}

                    {#if activeStep === 3 || activeStep === 4}
                        <div in:fly={{ y: 20, duration: 400 }} class="w-full max-w-sm bg-white rounded-xl shadow-lg border border-gray-100 flex flex-col h-[400px] overflow-hidden">
                            <div class="p-3 border-b border-gray-100 flex items-center justify-between bg-white z-10">
                                <div class="flex items-center gap-3">
                                    <div class="w-9 h-9 rounded-full bg-pink-100 text-pink-500 flex items-center justify-center text-xs font-bold">RC</div>
                                    <div>
                                        <div class="text-xs font-bold text-gray-800">Rina Customer</div>
                                        <div class="text-[9px] text-gray-400">Online</div>
                                    </div>
                                </div>
                                {#if activeStep === 3}
                                    <span class="bg-gray-100 text-gray-500 text-[9px] px-2 py-1 rounded font-bold border border-gray-200">COLD LEAD</span>
                                {:else}
                                    <span class="bg-red-500 text-white text-[9px] px-2 py-1 rounded font-bold shadow-md animate-pulse">HOT LEAD 🔥</span>
                                {/if}
                            </div>

                            <div class="flex-1 p-4 bg-[#ece5dd] overflow-y-auto space-y-4 font-sans text-xs">
                                <div class="flex justify-start">
                                    <div class="bg-white text-gray-800 p-2.5 rounded-lg rounded-tl-none shadow-sm max-w-[85%]">
                                        Halo Min, Gamis model Aisyah warna Maroon size L ready gak?
                                        <span class="block text-[8px] text-gray-300 text-right mt-1">10:05</span>
                                    </div>
                                </div>

                                <div class="flex justify-end">
                                    <div class="bg-[#dcf8c6] text-gray-800 p-2.5 rounded-lg rounded-tr-none shadow-sm max-w-[90%]">
                                        Halo Ka Rina! 👋 Ready dong, stoknya tinggal dikit nih Ka. Mau aku keep-kan sekarang? 😍
                                        <span class="block text-[8px] text-gray-400 text-right mt-1 flex justify-end gap-1">10:05 ✓✓</span>
                                    </div>
                                </div>

                                {#if activeStep === 4}
                                    <div in:fly={{ y: 10 }} class="flex justify-start">
                                        <div class="bg-white text-gray-800 p-2.5 rounded-lg rounded-tl-none shadow-sm max-w-[85%]">
                                            Boleh deh Ka, kirim ke Jakarta Selatan ya. Berapa totalnya?
                                        </div>
                                    </div>
                                    
                                    <div in:fly={{ y: 10, delay: 200 }} class="flex justify-end">
                                        <div class="bg-[#dcf8c6] text-gray-800 p-3 rounded-lg rounded-tr-none shadow-sm max-w-[95%] border-l-4 border-green-500">
                                            <div class="font-bold mb-1 text-green-700">Invoice Otomatis 🧾</div>
                                            Gamis Maroon (L): Rp 185.000<br>
                                            Ongkir JNE: Rp 10.000<br>
                                            <strong>Total: Rp 195.000</strong><br><br>
                                            Silakan transfer ke BCA Haloka Fashion ya Ka! 🙏
                                        </div>
                                    </div>
                                {/if}
                            </div>
                        </div>
                    {/if}

                    {#if activeStep === 5}
                        <div in:fly={{ y: 20, duration: 400 }} class="w-full max-w-sm space-y-3">
                            <div class="grid grid-cols-2 gap-3">
                                <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                                    <div class="text-[10px] text-gray-400 mb-1 font-bold">Total Revenue</div>
                                    <div class="text-xl font-bold text-green">Rp 45.2jt</div>
                                    <div class="text-[9px] text-green-600 bg-green-50 inline-block px-1.5 py-0.5 rounded-full mt-1">↑ 24% Naik</div>
                                </div>
                                <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                                    <div class="text-[10px] text-gray-400 mb-1 font-bold">Chat Terjawab</div>
                                    <div class="text-xl font-bold text-primary">2,840</div>
                                    <div class="text-[9px] text-blue-600 bg-blue-50 inline-block px-1.5 py-0.5 rounded-full mt-1">Otomatis</div>
                                </div>
                            </div>

                            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 h-32 flex items-end justify-between px-2 gap-2 relative overflow-hidden">
                                <div class="absolute top-2 left-3 text-[10px] text-gray-400 font-bold">Grafik Penjualan</div>
                                
                                <div class="w-full bg-blue-50 rounded-t h-[30%]"></div>
                                <div class="w-full bg-blue-100 rounded-t h-[45%]"></div>
                                <div class="w-full bg-blue-200 rounded-t h-[40%]"></div>
                                <div class="w-full bg-blue-300 rounded-t h-[65%]"></div>
                                <div class="w-full bg-blue-400 rounded-t h-[55%]"></div>
                                <div class="w-full bg-green rounded-t h-[85%] shadow-lg shadow-green/20 relative group">
                                    <div class="absolute -top-8 left-1/2 -translate-x-1/2 bg-gray-800 text-white text-[9px] px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap z-10">
                                        Hari Ini
                                    </div>
                                </div>
                            </div>
                        </div>
                    {/if}

                </div>
            </div>
        </div>
    </div>
</section>

<style>
    @keyframes progress { 0% { width: 0%; } 100% { width: 100%; } }
    @keyframes spin-slow { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
</style>