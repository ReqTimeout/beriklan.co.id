<script>
    import { onMount } from 'svelte';

    let container;
    let mouseX = 0;
    let mouseY = 0;
    
    // Link Register
    const regBase = "https://platform.haloka.id/register?billing_type=monthly";

    // Logic untuk Mouse Spotlight
    const handleMouseMove = (e) => {
        if (!container) return;
        const rect = container.getBoundingClientRect();
        mouseX = e.clientX - rect.left;
        mouseY = e.clientY - rect.top;
        
        // Update CSS variables secara realtime
        container.style.setProperty('--mouse-x', `${mouseX}px`);
        container.style.setProperty('--mouse-y', `${mouseY}px`);
    };

    onMount(() => {
        // Efek tambahan: Grid berkedip acak (Simulasi Data Processing)
        const gridCells = document.querySelectorAll('.grid-cell');
        setInterval(() => {
            const randomCell = gridCells[Math.floor(Math.random() * gridCells.length)];
            if(randomCell) {
                randomCell.classList.add('active');
                setTimeout(() => randomCell.classList.remove('active'), 2000); // Nyala 2 detik lalu mati
            }
        }, 100);
    });
</script>

<section 
    id="final-cta" 
    bind:this={container}
    on:mousemove={handleMouseMove}
    class="relative py-32 overflow-hidden bg-[#020617] text-white isolate font-sans group"
>
    
    <div class="absolute inset-0 z-0 pointer-events-none">
        
        <div class="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-20"></div>
        
        <div 
            class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
            style="background: radial-gradient(600px circle at var(--mouse-x) var(--mouse-y), rgba(37, 211, 102, 0.15), transparent 40%);"
        ></div>

        <div class="absolute inset-0 grid grid-cols-[repeat(auto-fill,minmax(4rem,1fr))] grid-rows-[repeat(auto-fill,minmax(4rem,1fr))] opacity-30">
            {#each Array(40) as _}
                <div class="grid-cell w-full h-full border border-transparent transition-colors duration-1000"></div>
            {/each}
        </div>
    </div>

    <div class="container mx-auto px-6 text-center relative z-10">
        
        <div class="max-w-4xl mx-auto space-y-8">
            
            <div class="inline-flex items-center gap-2 px-4 py-1.5 bg-red-900/30 border border-red-500/50 text-red-400 rounded-full text-xs font-bold uppercase tracking-widest mb-4 shadow-[0_0_15px_rgba(239,68,68,0.2)]">
                <span class="w-2 h-2 rounded-full bg-red-500 animate-ping"></span>
                <span class="w-2 h-2 rounded-full bg-red-500 absolute"></span>
                Warning: Kompetitor Sudah Pakai Haloka AI
            </div>

            <h2 class="font-display font-black text-4xl md:text-6xl leading-tight drop-shadow-2xl">
                5 Menit Telat Balas,<br>
                <span class="text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-400">Rejeki Diambil Orang.</span>
            </h2>
            
            <p class="text-gray-400 text-lg md:text-xl leading-relaxed font-light max-w-2xl mx-auto border-l-4 border-gray-800 pl-6 text-left md:text-center md:border-none md:pl-0">
                Pelanggan tidak suka menunggu. Saat admin Anda sibuk mengetik manual, kompetitor Anda yang pakai Haloka AI sudah <strong class="text-white border-b border-green-500">Closing Duluan</strong> detik ini juga.
            </p>

            <div class="pt-10 flex flex-col md:flex-row items-center justify-center gap-6">
                <a href={regBase} class="group relative inline-flex items-center justify-center gap-3 bg-[#25d366] text-white px-10 py-5 rounded-full font-bold text-xl shadow-[0_0_20px_rgba(37,211,102,0.4)] hover:shadow-[0_0_50px_rgba(37,211,102,0.8)] hover:scale-105 transition-all duration-300 ring-4 ring-[#25d366]/20 z-20 overflow-hidden">
                    <div class="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full group-hover:animate-shine"></div>
                    <span class="text-2xl">⚡</span>
                    <span class="relative">Otomatiskan Chat Sekarang</span>
                </a>
                
                <a href="#demo" class="text-gray-500 hover:text-white font-medium transition flex items-center gap-2 group/link">
                    <span class="group-hover/link:-rotate-180 transition-transform duration-500">↺</span> Saya mau lihat simulasi lagi
                </a>
            </div>

            <div class="mt-16 pt-8 border-t border-white/5 grid grid-cols-2 md:grid-cols-4 gap-8 text-center opacity-70">
                <div>
                    <div class="text-3xl font-black text-white mb-1">24/7</div>
                    <div class="text-[10px] text-gray-400 uppercase tracking-widest">Non-Stop Service</div>
                </div>
                <div>
                    <div class="text-3xl font-black text-white mb-1">0s</div>
                    <div class="text-[10px] text-gray-400 uppercase tracking-widest">Response Time</div>
                </div>
                <div>
                    <div class="text-3xl font-black text-white mb-1">100%</div>
                    <div class="text-[10px] text-gray-400 uppercase tracking-widest">No Missed Chat</div>
                </div>
                <div>
                    <div class="text-3xl font-black text-white mb-1">Auto</div>
                    <div class="text-[10px] text-gray-400 uppercase tracking-widest">Follow-up Engine</div>
                </div>
            </div>

        </div>
    </div>

</section>

<style>
    /* Animasi Kilau Tombol */
    @keyframes shine {
        100% { transform: translateX(100%); }
    }
    .animate-shine {
        animation: shine 0.8s;
    }

    /* Cell Grid yang Menyala */
    .grid-cell.active {
        background-color: rgba(37, 211, 102, 0.1);
        border: 1px solid rgba(37, 211, 102, 0.3);
        box-shadow: 0 0 10px rgba(37, 211, 102, 0.2);
    }
</style>