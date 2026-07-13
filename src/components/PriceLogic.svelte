<script>
    import { tweened } from 'svelte/motion';
    import { cubicOut } from 'svelte/easing';

    // State Awal
    let chatsPerDay = 100;
    
    // LOGIKA BEBAN KERJA
    $: workloadHours = Math.ceil((chatsPerDay * 5) / 60); 
    
    // Status Bahaya
    $: isSafe = workloadHours <= 4;
    $: isWarning = workloadHours > 4 && workloadHours <= 8;
    $: isCritical = workloadHours > 8;

    // Emoji & Warna
    $: currentEmoji = isSafe ? '🙂' : (isWarning ? '😓' : '🤯');
    $: barColor = isSafe ? 'bg-emerald-500' : (isWarning ? 'bg-orange-500' : 'bg-red-500');

    // LOGIKA PAKET (Hardcoded Gradient Classes)
    let pkgThemeClass = '';
    let pkgName = '';
    let pkgPriceMonth = 0;

    $: if (chatsPerDay < 50) {
        pkgName = 'Paket Sapa';
        pkgPriceMonth = 699000;
        pkgThemeClass = 'bg-gradient-to-br from-emerald-600 to-teal-800 shadow-emerald-500/40 border-emerald-400/50'; 
    } else if (chatsPerDay < 500) {
        pkgName = 'Paket Sobat';
        pkgPriceMonth = 1599000;
        pkgThemeClass = 'bg-gradient-to-br from-blue-700 to-indigo-800 shadow-blue-600/40 border-blue-400/50'; 
    } else {
        pkgName = 'Paket Juragan';
        pkgPriceMonth = 3999000;
        pkgThemeClass = 'bg-gradient-to-br from-purple-700 to-violet-900 shadow-purple-600/40 border-purple-400/50'; 
    }

    // Hitung Harga Per Hari
    $: pricePerDay = Math.ceil(pkgPriceMonth / 30);

    // Animasi Angka
    const animatedHours = tweened(0, { duration: 500, easing: cubicOut });
    const animatedDaily = tweened(0, { duration: 500, easing: cubicOut });
    
    $: animatedHours.set(workloadHours);
    $: animatedDaily.set(pricePerDay);

    // ID Paket untuk Scroll
    $: recPackageId = chatsPerDay < 50 ? 'haloka_sapa' : (chatsPerDay < 500 ? 'haloka_sobat' : 'haloka_juragan');

    const formatRupiah = (num) => new Intl.NumberFormat('id-ID', { maximumFractionDigits: 0 }).format(num);

    function scrollToRecommendation() {
        const targetElement = document.getElementById(recPackageId);
        if (targetElement) {
            targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            targetElement.classList.add('highlight-target');
            setTimeout(() => targetElement.classList.remove('highlight-target'), 2000);
        } else {
            window.location.href = '#pricing';
        }
    }
</script>

<section class="py-10 md:py-16 relative overflow-hidden bg-gradient-to-b from-white to-gray-100">
    
    <div class="absolute inset-0 w-full h-full overflow-hidden pointer-events-none">
        <div class="absolute inset-0 opacity-[0.03]" 
             style="background-image: radial-gradient(#444 1px, transparent 1px); background-size: 30px 30px;">
        </div>
        <div class="absolute top-0 -left-4 w-96 h-96 bg-blue-200/50 rounded-full mix-blend-multiply filter blur-[128px] opacity-40 animate-blob"></div>
        <div class="absolute top-0 -right-4 w-96 h-96 bg-purple-200/50 rounded-full mix-blend-multiply filter blur-[128px] opacity-40 animate-blob animation-delay-2000"></div>
        <div class="absolute -bottom-32 left-20 w-96 h-96 bg-green-200/50 rounded-full mix-blend-multiply filter blur-[128px] opacity-40 animate-blob animation-delay-4000"></div>
    </div>

    <div class="absolute top-0 left-0 w-full h-32 bg-gradient-to-b from-white to-transparent z-0 pointer-events-none"></div>
    
    <div class="absolute bottom-0 left-0 w-full h-32 bg-gradient-to-t from-gray-100 to-transparent z-0 pointer-events-none"></div>

    <div class="relative z-10 container mx-auto px-4 md:px-8 max-w-6xl">
        
        <div class="bg-white/70 backdrop-blur-xl rounded-[2rem] p-6 md:p-10 shadow-2xl border border-white/60 overflow-hidden">
            
            <div class="text-center mb-8">
                <span class="inline-block py-1 px-3 rounded-full bg-red-50 border border-red-100 text-red-600 text-[10px] font-bold tracking-widest uppercase mb-2 shadow-sm">
                    🔥 Reality Check Bisnis
                </span>
                <h2 class="font-display font-black text-2xl md:text-3xl text-gray-900 mb-2 leading-tight">
                    Seberapa Berat Beban Tim Anda?
                </h2>
                <p class="text-sm text-gray-500 max-w-2xl mx-auto">
                    Geser slider. Bandingkan lelahnya cara manual vs <strong>cepatnya Haloka membereskan chat.</strong>
                </p>
            </div>

            <div class="mb-8 bg-white/50 rounded-2xl p-5 md:p-8 border border-white shadow-sm relative">
                <div class="flex flex-col md:flex-row justify-between items-end mb-4 md:mb-6 gap-2">
                    <label class="font-bold text-gray-700 text-base md:text-lg flex flex-col">
                        <span>Volume Chat Harian</span>
                        <span class="text-xs text-gray-400 font-normal mt-0.5">Total chat masuk ke WA toko</span>
                    </label>
                    <div class="text-4xl md:text-5xl font-display font-black text-gray-800 tracking-tight flex items-baseline">
                        {chatsPerDay}
                        <span class="text-base md:text-lg font-sans text-gray-400 font-bold ml-2">chat</span>
                    </div>
                </div>
                
                <div class="relative w-full h-5 bg-gray-200 rounded-full shadow-inner cursor-pointer group">
                    <input 
                        type="range" min="10" max="1000" step="10" 
                        bind:value={chatsPerDay} 
                        class="absolute w-full h-full opacity-0 cursor-pointer z-20"
                    />
                    <div class="absolute h-full rounded-full z-10 transition-all duration-300 ease-out {barColor}"
                         style="width: {(chatsPerDay/1000)*100}%">
                    </div>
                    <div class="absolute h-8 w-8 bg-white border-[3px] border-gray-100 rounded-full shadow-lg z-10 top-1/2 -translate-y-1/2 transition-all duration-100 ease-out pointer-events-none transform group-hover:scale-110 flex items-center justify-center"
                         style="left: calc({(chatsPerDay/1000)*100}% - 16px)">
                         <div class="w-2.5 h-2.5 rounded-full {barColor}"></div>
                    </div>
                </div>
                <div class="flex justify-between text-[10px] md:text-xs text-gray-400 mt-2 font-mono uppercase tracking-wide font-bold">
                    <span>Sepi (10)</span>
                    <span>Normal (500)</span>
                    <span>Viral (1000)</span>
                </div>
            </div>

            <div class="grid md:grid-cols-2 gap-6 items-stretch">
                
                <div class="bg-white rounded-2xl p-6 md:p-8 border transition-all duration-500 flex flex-col justify-between shadow-sm
                    {isCritical ? 'border-red-200 ring-2 ring-red-50 shake-hard' : (isWarning ? 'border-orange-200' : 'border-gray-200')}">
                    
                    <div>
                        <div class="flex items-center gap-4 mb-4">
                            <div class="w-12 h-12 rounded-xl flex items-center justify-center text-3xl shadow-sm bg-gray-50 transition-transform duration-300 {isCritical ? 'scale-110' : ''}">
                                {currentEmoji}
                            </div>
                            <div>
                                <h3 class="font-bold text-gray-900 text-lg">Metode Manual</h3>
                                <p class="text-xs text-gray-500">Estimasi Beban Tim</p>
                            </div>
                        </div>
                        
                        <div class="space-y-1 mb-4">
                            <div class="flex justify-between items-end">
                                <span class="text-xs text-gray-500 uppercase font-bold tracking-wide">Jam Kerja Dibutuhkan</span>
                                <span class="font-bold text-2xl md:text-3xl {isCritical ? 'text-red-600' : 'text-gray-800'}">
                                    {Math.floor($animatedHours)} Jam
                                </span>
                            </div>
                            
                            <div class="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                                <div class="h-full transition-all duration-500 {barColor} {isCritical ? 'animate-pulse' : ''}" 
                                     style="width: {Math.min(($animatedHours/24)*100, 100)}%">
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="p-3 rounded-lg text-xs leading-relaxed font-medium bg-gray-50 border border-gray-100">
                        {#if isCritical}
                            <span class="text-red-600 font-bold flex items-center gap-2"><span class="text-lg">🔥</span> OVERLOAD</span>
                            <p class="mt-1 text-gray-600">Mustahil dikerjakan 1 orang. Risiko <i>burnout</i> & chat tak terbalas sangat tinggi.</p>
                        {:else if isWarning}
                            <span class="text-orange-600 font-bold flex items-center gap-2"><span class="text-lg">⚠️</span> WARNING</span>
                            <p class="mt-1 text-gray-600">Tim butuh lembur. Fokus mereka habis hanya untuk balas chat.</p>
                        {:else}
                            <span class="text-emerald-600 font-bold flex items-center gap-2"><span class="text-lg">✅</span> AMAN</span>
                            <p class="mt-1 text-gray-600">Beban kerja wajar. Pastikan tetap aman saat orderan naik.</p>
                        {/if}
                    </div>
                </div>

                <div class="rounded-2xl p-6 md:p-8 text-white shadow-xl transition-all duration-500 flex flex-col justify-between relative overflow-hidden group border {pkgThemeClass}">
                    
                    <div class="absolute top-0 -left-[100%] w-full h-full bg-gradient-to-r from-transparent via-white/10 to-transparent skew-x-12 group-hover:animate-[shimmer_2s_infinite]"></div>

                    <div class="relative z-10">
                        <div class="flex justify-between items-start mb-4">
                            <div class="flex items-center gap-3">
                                <div class="w-10 h-10 bg-white/20 backdrop-blur-md rounded-xl flex items-center justify-center text-xl shadow-inner border border-white/10">🚀</div>
                                <div>
                                    <h3 class="font-bold text-white text-lg">Solusi Haloka</h3>
                                    <p class="text-[10px] text-white/90 uppercase tracking-widest font-semibold">Unlimited 24 Jam</p>
                                </div>
                            </div>
                        </div>

                        <div class="space-y-0.5">
                            <p class="text-xs text-white/80">Rekomendasi Paket Hemat:</p>
                            <h4 class="text-2xl font-bold tracking-tight text-white">{pkgName}</h4>
                        </div>
                    </div>

                    <div class="relative z-10 mt-4 pt-4 border-t border-white/20">
                        <div class="flex items-end gap-1.5 mb-1">
                            <span class="text-sm font-medium text-white/90 mb-1.5">Hanya</span>
                            <span class="text-4xl font-mono font-bold text-white tracking-tighter shadow-sm">
                                Rp {formatRupiah($animatedDaily)}
                            </span>
                            <span class="text-sm font-medium text-white/90 mb-1.5">/hari</span>
                        </div>
                        <p class="text-[10px] text-white/70 mb-4 font-medium">
                            *Total Rp {formatRupiah(pkgPriceMonth)}/bulan
                        </p>

                        <button 
                            on:click={scrollToRecommendation}
                            class="w-full py-3 bg-white text-gray-900 rounded-xl font-bold text-sm hover:bg-gray-50 hover:scale-[1.02] transition-all shadow-lg flex items-center justify-center gap-2 group-hover:shadow-xl"
                        >
                            Ambil Paket Ini
                            <svg class="w-3 h-3 text-gray-600 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                        </button>
                    </div>
                </div>

            </div>
        </div>
    </div>
</section>

<style>
    @keyframes blob {
        0% { transform: translate(0px, 0px) scale(1); }
        33% { transform: translate(30px, -50px) scale(1.1); }
        66% { transform: translate(-20px, 20px) scale(0.9); }
        100% { transform: translate(0px, 0px) scale(1); }
    }
    .animate-blob {
        animation: blob 7s infinite;
    }
    .animation-delay-2000 {
        animation-delay: 2s;
    }
    .animation-delay-4000 {
        animation-delay: 4s;
    }

    @keyframes shake {
        0% { transform: translate(1px, 1px) rotate(0deg); }
        10% { transform: translate(-1px, -2px) rotate(-1deg); }
        20% { transform: translate(-3px, 0px) rotate(1deg); }
        30% { transform: translate(3px, 2px) rotate(0deg); }
        40% { transform: translate(1px, -1px) rotate(1deg); }
        50% { transform: translate(-1px, 2px) rotate(-1deg); }
        60% { transform: translate(-3px, 1px) rotate(0deg); }
        70% { transform: translate(3px, 1px) rotate(-1deg); }
        80% { transform: translate(-1px, -1px) rotate(1deg); }
        90% { transform: translate(1px, 2px) rotate(0deg); }
        100% { transform: translate(1px, -2px) rotate(-1deg); }
    }
    .shake-hard {
        animation: shake 0.5s;
        animation-iteration-count: 1;
    }
    
    @keyframes shimmer {
        100% { left: 150%; }
    }
</style>