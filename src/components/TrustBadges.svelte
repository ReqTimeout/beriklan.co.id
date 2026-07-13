<script>
    import { onMount } from 'svelte';
    
    // Data Fitur
    const features = [
        { icon: '🔒', title: '256-bit Encryption', desc: 'Data Pelanggan Aman', color: 'bg-green-100 text-green-600' },
        { icon: '⚡', title: '99.9% Uptime SLA', desc: 'Server Anti Down', color: 'bg-blue-100 text-blue-600' },
        { icon: '🛡️', title: 'Smart Safety Guard', desc: 'Proteksi End-to-End', color: 'bg-orange-100 text-orange-600' },
        { icon: '🧠', title: 'Advanced AI Brain', desc: 'Interaksi Natural', color: 'bg-purple-100 text-purple-600' }
    ];

    let visible = false;

    onMount(() => {
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                visible = true;
                observer.disconnect();
            }
        });
        const section = document.getElementById('trust-badges');
        if (section) observer.observe(section);
    });
</script>

<section id="trust-badges" class="py-10 md:py-16 bg-white border-b border-gray-100 relative overflow-hidden">
    
    <div class="absolute inset-0 opacity-40 pointer-events-none">
        <div class="absolute -left-10 top-1/2 w-32 h-32 bg-blue-50 rounded-full blur-3xl"></div>
        <div class="absolute -right-10 top-1/2 w-32 h-32 bg-green-50 rounded-full blur-3xl"></div>
    </div>

    <div class="container mx-auto px-4 md:px-6 text-center relative z-10">
        
        <p class="text-[10px] md:text-xs font-bold text-gray-400 uppercase tracking-[0.2em] mb-8 md:mb-10 animate-pulse">
            Dibangun dengan Standar Enterprise
        </p>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-8 max-w-5xl mx-auto">
            
            {#each features as item, i}
                <div 
                    class="group p-4 rounded-2xl transition-all duration-300 hover:bg-gray-50 hover:shadow-lg border border-transparent hover:border-gray-100 cursor-default transform translate-y-4 opacity-0"
                    class:animate-enter={visible}
                    style="animation-delay: {i * 100}ms; animation-fill-mode: forwards;"
                >
                    <div class="flex flex-col items-center gap-3">
                        <div class="w-12 h-12 {item.color} rounded-2xl flex items-center justify-center text-2xl shadow-sm group-hover:scale-110 group-hover:rotate-3 transition-transform duration-300">
                            {item.icon}
                        </div>
                        
                        <div class="flex flex-col">
                            <span class="font-bold text-gray-900 text-xs md:text-sm mb-0.5 group-hover:text-blue-600 transition-colors">
                                {item.title}
                            </span>
                            <span class="text-[10px] text-gray-400 group-hover:text-gray-500">
                                {item.desc}
                            </span>
                        </div>
                    </div>
                </div>
            {/each}

        </div>
    </div>
</section>

<style>
    @keyframes enterUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-enter {
        animation: enterUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }
</style>