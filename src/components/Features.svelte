<script>
    import { onMount } from 'svelte';
    import { fade, fly } from 'svelte/transition';

    let observer;
    
    // STATE UNTUK ANIMASI CRM (Cold/Warm/Hot)
    let crmState = 0; // 0=Cold, 1=Warm, 2=Hot
    const crmData = [
        { label: 'COLD', color: 'bg-blue-100 text-blue-600', border: 'border-blue-200', chat: '"Harganya berapa gan? Mahal gak?"', intent: 'Checking Price' },
        { label: 'WARM', color: 'bg-orange-100 text-orange-600', border: 'border-orange-200', chat: '"Ongkir ke Jakarta berapa? Ada diskon?"', intent: 'Interested' },
        { label: 'HOT 🔥', color: 'bg-red-500 text-white shadow-lg shadow-red-500/30', border: 'border-red-200', chat: '"Oke gan, saya transfer sekarang ya. Kirim norek."', intent: 'Ready to Buy' }
    ];

    onMount(() => {
        // Observer untuk scroll reveal
        observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.remove('opacity-0', 'translate-y-10');
                    entry.target.classList.add('opacity-100', 'translate-y-0');
                    observer.unobserve(entry.target); 
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.animate-on-scroll').forEach((el) => observer.observe(el));

        // Interval untuk ganti status CRM
        const interval = setInterval(() => {
            crmState = (crmState + 1) % 3;
        }, 3000); // Ganti tiap 3 detik

        return () => clearInterval(interval);
    });
</script>

<div class="w-full overflow-hidden leading-[0] rotate-180 relative z-20 -mb-1 bg-gray-50">
    <svg data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 120" preserveAspectRatio="none" class="relative block w-[calc(100%+1.3px)] h-[60px] fill-[#f8fbff]">
        <path d="M321.39,56.44c58-10.79,114.16-30.13,172-41.86,82.39-16.72,168.19-17.73,250.45-.39C823.78,31,906.67,72,985.66,92.83c70.05,18.48,146.53,26.09,214.34,3V0H0V27.35A600.21,600.21,0,0,0,321.39,56.44Z"></path>
    </svg>
</div>

<section id="fitur" class="py-12 md:pb-24 md:pt-16 bg-gradient-to-b from-[#f8fbff] to-white overflow-hidden relative min-h-screen">
    
    <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-100/40 rounded-full blur-[100px] -z-10 translate-x-1/2"></div>
    <div class="absolute bottom-0 left-0 w-[500px] h-[500px] bg-red-100/40 rounded-full blur-[100px] -z-10 -translate-x-1/2"></div>

    <div class="container mx-auto px-6 space-y-16 md:space-y-32 relative z-10">
        
        <div class="absolute inset-0 hidden md:block pointer-events-none -z-10">
            <svg class="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                <path 
                    d="M 25 10 C 50 10, 50 35, 75 35 C 50 35, 50 60, 25 60 C 50 60, 50 85, 75 85" 
                    fill="none" 
                    stroke="url(#gradientLine)" 
                    stroke-width="0.3" 
                    stroke-dasharray="2 2"
                    class="connector-line"
                />
                
                <defs>
                    <linearGradient id="gradientLine" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.2" /> <stop offset="50%" stop-color="#ef4444" stop-opacity="0.3" /> <stop offset="100%" stop-color="#a855f7" stop-opacity="0.3" /> </linearGradient>
                </defs>
            </svg>
        </div>

        <div class="grid md:grid-cols-2 gap-8 md:gap-16 items-center">
            <div class="relative group animate-on-scroll opacity-0 translate-y-10 transition-all duration-1000 ease-out">
                <div class="absolute inset-0 bg-blue-200/40 rounded-[2.5rem] blur-3xl -z-10 group-hover:bg-blue-300/50 transition duration-500 transform group-hover:scale-105"></div>
                <div class="bg-white rounded-[2.5rem] p-8 shadow-xl shadow-blue-900/5 border border-white/50 relative overflow-hidden transform transition duration-500 hover:-translate-y-2 hover:rotate-1">
                    <div class="flex justify-between items-center mb-6">
                        <span class="text-[10px] font-bold tracking-[0.2em] text-gray-400 uppercase flex items-center gap-2">
                            <span class="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></span> Haloka Brain Engine
                        </span>
                        <div class="flex gap-1.5"><div class="w-2.5 h-2.5 rounded-full bg-red-400"></div><div class="w-2.5 h-2.5 rounded-full bg-yellow-400"></div><div class="w-2.5 h-2.5 rounded-full bg-green-400"></div></div>
                    </div>
                    <div class="bg-[#f8fafc] rounded-xl p-5 mb-6 font-mono text-xs leading-relaxed border border-gray-100 text-blue-900 shadow-inner">
                        <p class="mb-2 flex items-center"><span class="text-gray-400 mr-2">$</span> Uploading: <span class="font-bold text-blue-600 ml-1">SOP_Toko_2026.pdf</span></p>
                        <div class="w-full bg-gray-200 rounded-full h-1.5 mb-2 overflow-hidden relative"><div class="loading-bar bg-blue-500 h-1.5 rounded-full absolute top-0 left-0"></div></div>
                        <p class="flex items-center"><span class="text-gray-400 mr-2">></span> Status: <span class="text-green-600 font-bold ml-1 bg-green-50 px-1 rounded">Processing Knowledge...</span></p>
                    </div>
                    <div class="flex gap-3 items-start">
                        <div class="text-2xl">💡</div>
                        <p class="text-sm text-gray-500 italic leading-relaxed bg-yellow-50/50 p-3 rounded-lg border border-yellow-100">"Haloka sekarang paham bahwa untuk pengiriman ke Papua wajib pakai JNE dan ada biaya packing kayu."</p>
                    </div>
                </div>
            </div>
            <div class="space-y-4 md:space-y-6 animate-on-scroll opacity-0 translate-y-10 transition-all duration-1000 ease-out delay-200">
                <h3 class="font-display font-bold text-3xl md:text-4xl text-primary leading-tight">
                    Lupakan Training Manual.<br>
                    <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-700 to-cyan-600">Upload SOP, Langsung Paham.</span>
                </h3>
                <p class="text-base md:text-lg text-gray-600 leading-relaxed font-light">
                    Tidak perlu menghabiskan waktu berhari-hari untuk mengajarkan produk ke karyawan baru. Di Haloka, Anda cukup <strong>Upload Dokumen PDF/Word</strong> berisi info produk. AI akan membacanya dan menguasai detail produk Anda dalam hitungan detik.
                </p>
            </div>
        </div>

        <div class="grid md:grid-cols-2 gap-8 md:gap-16 items-center">
            <div class="space-y-4 md:space-y-6 order-2 md:order-1 animate-on-scroll opacity-0 translate-y-10 transition-all duration-1000 ease-out">
                <h3 class="font-display font-bold text-3xl md:text-4xl text-primary leading-tight">
                    CRM Otomatis:<br>
                    <span class="text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-red-500">Pemisah "Halu" dan "Cuan".</span>
                </h3>
                <p class="text-base md:text-lg text-gray-600 leading-relaxed font-light">
                    Haloka tidak hanya membalas, tapi juga <strong>Menganalisa Niat Pembeli</strong>. Sistem akan otomatis melabeli pelanggan: Siapa yang cuma "Price Police" (Cold), dan siapa yang "Siap Transfer" (Hot). Sales Anda tinggal panen yang matang saja.
                </p>
            </div>

            <div class="relative group order-1 md:order-2 animate-on-scroll opacity-0 translate-y-10 transition-all duration-1000 ease-out delay-200">
                <div class="absolute inset-0 bg-gray-100 rounded-[2.5rem] blur-3xl -z-10 transition duration-500"></div>
                <div class="bg-white rounded-[2.5rem] p-8 shadow-xl border border-white/50 relative min-h-[280px]">
                    {#key crmState}
                        <div in:fade={{ duration: 300 }} class="absolute inset-0 p-8 flex flex-col justify-center">
                            <div class="flex items-center gap-4 mb-6 p-3 rounded-2xl border {crmData[crmState].border} bg-opacity-10 transition-all">
                                <div class="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-lg">👤</div>
                                <div class="flex-1">
                                    <div class="text-xs font-bold text-gray-500 uppercase tracking-wide">Status Pelanggan</div>
                                    <div class="h-2 w-20 bg-gray-100 rounded mt-1"></div>
                                </div>
                                <span class="{crmData[crmState].color} text-[10px] font-bold px-3 py-1.5 rounded-full transition-all duration-500 transform scale-105">
                                    {crmData[crmState].label}
                                </span>
                            </div>
                            <div class="bg-[#f8fafc] p-5 rounded-2xl rounded-tr-none border border-gray-100 relative shadow-sm">
                                <p class="text-sm text-gray-700 leading-relaxed font-medium italic">
                                    {crmData[crmState].chat}
                                </p>
                                <div class="absolute -bottom-3 -right-2 bg-white text-gray-500 text-[9px] px-2 py-1 rounded-full border shadow-sm">
                                    AI Logic: {crmData[crmState].intent}
                                </div>
                            </div>
                            {#if crmState === 2}
                                <div in:fly={{ y: 20 }} class="flex justify-end mt-4">
                                    <button class="flex items-center gap-2 bg-green-600 text-white text-xs font-bold px-4 py-2 rounded-lg shadow-lg hover:bg-green-700 transition-all animate-bounce">
                                        <span>💰</span> Auto Send Invoice
                                    </button>
                                </div>
                            {/if}
                        </div>
                    {/key}
                </div>
            </div>
        </div>

        <div class="grid md:grid-cols-2 gap-8 md:gap-16 items-center">
            <div class="relative group animate-on-scroll opacity-0 translate-y-10 transition-all duration-1000 ease-out">
                <div class="absolute inset-0 bg-yellow-200/40 rounded-[2.5rem] blur-3xl -z-10 group-hover:bg-yellow-300/50 transition duration-500"></div>
                <div class="bg-white rounded-[2.5rem] p-8 shadow-xl border border-white/50 relative overflow-hidden">
                    <div class="flex justify-between items-center mb-8 border-b border-gray-100 pb-4">
                        <span class="text-xs font-bold text-gray-400 uppercase">Auto Follow-Up Engine</span>
                        <span class="bg-yellow-100 text-yellow-700 text-[10px] px-2 py-1 rounded font-bold">Active</span>
                    </div>
                    <div class="relative pl-6 border-l-2 border-gray-100 space-y-8">
                        <div class="relative">
                            <div class="absolute -left-[31px] top-0 w-4 h-4 bg-gray-200 rounded-full border-2 border-white"></div>
                            <div class="text-xs text-gray-400 mb-1">10:00 AM</div>
                            <div class="bg-gray-50 p-3 rounded-lg text-xs text-gray-600 italic">"Harga gamisnya berapa kak?"</div>
                        </div>
                        <div class="relative py-2">
                            <div class="flex items-center gap-2 text-[10px] text-orange-500 bg-orange-50 w-fit px-2 py-1 rounded">
                                <span class="animate-spin">⏳</span> Menunggu 6 Jam tanpa balasan...
                            </div>
                        </div>
                        <div class="relative">
                            <div class="absolute -left-[31px] top-0 w-4 h-4 bg-green-500 rounded-full border-2 border-white shadow-lg shadow-green-500/30"></div>
                            <div class="text-xs text-green-600 font-bold mb-1 flex items-center gap-1">
                                16:00 PM <span class="bg-green-100 text-[9px] px-1 rounded">Sent by AI</span>
                            </div>
                            <div class="bg-[#dcf8c6] p-3 rounded-lg text-xs text-gray-800 shadow-sm transform transition hover:scale-105">
                                "Halo Ka, stok gamis maroon tinggal 2 pcs nih. Jadi diamankan sekarang? 😊"
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="space-y-4 md:space-y-6 animate-on-scroll opacity-0 translate-y-10 transition-all duration-1000 ease-out delay-200">
                <h3 class="font-display font-bold text-3xl md:text-4xl text-primary leading-tight">
                    Jangan Biarkan<br>
                    <span class="text-transparent bg-clip-text bg-gradient-to-r from-yellow-500 to-orange-600">Pelanggan Ghosting.</span>
                </h3>
                <p class="text-base md:text-lg text-gray-600 leading-relaxed font-light">
                    Sering di-PHP pelanggan? Haloka punya fitur <strong>Auto Follow-Up</strong>. Jika pelanggan diam (tidak membalas) selama beberapa jam, AI akan otomatis menyapa kembali dengan pesan persuasif agar mereka jadi beli.
                </p>
                <ul class="space-y-2 text-sm text-gray-500">
                    <li class="flex items-center gap-2">✅ Atur jeda waktu (misal: 1 jam, 24 jam)</li>
                    <li class="flex items-center gap-2">✅ Pesan personal, tidak terlihat seperti bot</li>
                    <li class="flex items-center gap-2">✅ Otomatis berhenti jika user membalas</li>
                </ul>
            </div>
        </div>

        <div class="grid md:grid-cols-2 gap-8 md:gap-16 items-center">
            <div class="space-y-4 md:space-y-6 order-2 md:order-1 animate-on-scroll opacity-0 translate-y-10 transition-all duration-1000 ease-out">
                <h3 class="font-display font-bold text-3xl md:text-4xl text-primary leading-tight">
                    Asisten Pribadi<br>
                    <span class="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-500">Pencatat Jadwal.</span>
                </h3>
                <p class="text-base md:text-lg text-gray-600 leading-relaxed font-light">
                    Bisnis jasa, klinik, atau rental? Haloka AI bisa otomatis mendeteksi permintaan booking dari chat dan langsung memasukkannya ke <strong>Google Calendar</strong> atau sistem booking internal Anda.
                </p>
            </div>

            <div class="relative group order-1 md:order-2 animate-on-scroll opacity-0 translate-y-10 transition-all duration-1000 ease-out delay-200">
                <div class="absolute inset-0 bg-purple-200/40 rounded-[2.5rem] blur-3xl -z-10 group-hover:bg-purple-300/50 transition duration-500"></div>
                <div class="bg-white rounded-[2.5rem] p-8 shadow-xl border border-white/50 relative overflow-hidden flex flex-col gap-4">
                    <div class="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm flex items-start gap-3">
                        <div class="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center text-xs">U</div>
                        <div class="text-xs text-gray-600 bg-gray-50 p-2 rounded-lg flex-1">
                            "Min, mau booking service AC untuk <span class="font-bold text-purple-600 bg-purple-50 px-1 rounded">Besok Jam 10 Pagi</span> ya."
                        </div>
                    </div>
                    <div class="flex justify-center">
                        <div class="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center text-purple-600 animate-bounce">⬇</div>
                    </div>
                    <div class="bg-white border-l-4 border-purple-500 rounded-lg p-4 shadow-md transform transition hover:scale-105">
                        <div class="flex justify-between items-start">
                            <div>
                                <div class="text-[10px] font-bold text-gray-400 uppercase">New Event Created</div>
                                <div class="text-lg font-bold text-gray-800">Service AC - Pak Budi</div>
                                <div class="text-sm text-purple-600 font-medium flex items-center gap-1 mt-1">
                                    <span>📅</span> Besok, 10:00 - 11:00 WIB
                                </div>
                            </div>
                            <div class="bg-green-100 text-green-700 text-[9px] font-bold px-2 py-1 rounded">Confirmed</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

    </div>
</section>

<style>
    /* Animasi Loading Bar Infinite */
    .loading-bar {
        width: 0%;
        animation: progress 2s infinite ease-in-out;
    }

    /* Animasi Flow pada Garis Konektor */
    .connector-line {
        animation: flow 20s linear infinite;
    }

    @keyframes progress {
        0% { width: 0%; transform: translateX(-100%); opacity: 0; }
        50% { width: 70%; opacity: 1; }
        100% { width: 100%; transform: translateX(100%); opacity: 0; }
    }

    @keyframes flow {
        from { stroke-dashoffset: 100; }
        to { stroke-dashoffset: 0; }
    }
</style>