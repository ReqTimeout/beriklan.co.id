<script>
    // DATA TESTIMONI
    const testimonials = [
        { name: "Juragan Gamis", role: "Owner Fashion Muslim", text: "Gila sih, barusan nyoba upload katalog PDF setebal 50 halaman, hitungan detik langsung paham?! 🤯 Hemat gaji admin jutaan ini mah!", type: "wow", stars: 5 },
        { name: "Koh Michael", role: "Distributor Gadget", text: "Akhirnya nemu yang bisa bales cepet DAN natural. Gak kaku kayak robot sebelah. Customer saya gak akan sadar ini AI.", type: "quality", stars: 5 },
        { name: "Ibu Dewi Skincare", role: "Agen Kosmetik", text: "Ya ampun, fitur Auto Follow-up nya juara! Tadi ada customer ghosting 3 jam, disapa AI langsung transfer donk. Ngeri! 🤑", type: "money", stars: 5 },
        { name: "Mas Tio Travel", role: "Jasa Open Trip", text: "Booking calendar-nya ngebantu banget buat bisnis jasa kayak saya. Gak pusing lagi cek jadwal kosong manual. Mantap Haloka!", type: "feature", stars: 5 },
        { name: "Toko Mas Berkah", role: "Pedagang Emas", text: "Awalnya ragu, tapi pas liat demonya aman anti-banned, langsung gas daftar waiting list. Gak mau ketinggalan teknologi.", type: "trust", stars: 5 },
        { name: "Sista Nana", role: "Reseller Baju Anak", text: "Gajinya cuma 20rb/hari? Serius min? Ini mah lebih murah daripada jajan boba saya sehari 😂 Fix langganan tahunan.", type: "price", stars: 5 },
        { name: "Pak Budi Herbal", role: "Agen Propolis", text: "Fitur CRM yang misahin Cold/Hot lead itu cerdas banget. Sales saya jadi fokus ngejar yang pasti-pasti aja. Efisien.", type: "feature", stars: 5 },
        { name: "Kang Ojek Online", role: "Sampingan Jualan Pulsa", text: "Saya gaptek parah, tapi kok ini gampang banget ya? Tinggal upload file doang. Haloka penyelamat kaum gaptek nih.", type: "ease", stars: 5 },
        { name: "Cici Online Shop", role: "Importir Barang China", text: "Admin saya sering banget izin sakit pas lagi rame. Pake ini kayaknya bakal bebas drama deh. Can't wait to try! 😍", type: "pain", stars: 5 },
        { name: "Bang Jago Kopi", role: "Owner Coffee Shop", text: "Bisa handle booking meja otomatis gak min? Kalau bisa, saya langsung bungkus paket tahunan buat 3 cabang.", type: "demand", stars: 5 }
    ];


    function getCardAccents(type) {
        switch(type) {
            case 'wow': return 'shadow-purple-100 hover:shadow-purple-200 hover:border-purple-200';
            case 'money': return 'shadow-green-100 hover:shadow-green-200 hover:border-green-200';
            case 'price': return 'shadow-orange-100 hover:shadow-orange-200 hover:border-orange-200';
            case 'pain': return 'shadow-red-100 hover:shadow-red-200 hover:border-red-200';
            default: return 'shadow-blue-100 hover:shadow-blue-200 hover:border-blue-200';
        }
    }
</script>

<section class="py-24 bg-[#f8fafc] overflow-hidden relative">
    
    <div class="absolute inset-0 opacity-[0.02] pointer-events-none mix-blend-multiply" style="background-image: url('https://www.transparenttextures.com/patterns/cubes.png');"></div>

    <div class="container mx-auto px-6 relative z-10">
        
        <div class="text-center max-w-3xl mx-auto mb-16">
            <span class="inline-block py-1 px-3 rounded-full bg-blue-100 text-blue-700 font-bold tracking-widest uppercase text-[10px] mb-4 shadow-sm">
                ✨ Community Feedback
            </span>
            <h2 class="font-display font-black text-3xl md:text-5xl text-gray-900 mb-6 leading-tight">
                Kesan Pertama <br>
                <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-500">Berkenalan dengan Haloka</span>
            </h2>
            <p class="text-gray-500 text-lg">
                Pendapat para pemilik bisnis yang ingin meningkatkan standar pelayanan pelanggan ke level berikutnya.
            </p>
        </div>

        <div class="relative h-[650px] overflow-hidden before:absolute before:top-0 before:left-0 before:w-full before:h-48 before:bg-gradient-to-b before:from-[#f8fafc] before:to-transparent before:z-10 after:absolute after:bottom-0 after:left-0 after:w-full after:h-48 after:bg-gradient-to-t after:from-[#f8fafc] after:to-transparent after:z-10">
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 h-full">
                
                <div class="space-y-6 animate-scroll-up hover:pause">
                    {#each [...testimonials, ...testimonials] as item}
                        <div class="group relative bg-white/80 backdrop-blur-sm p-7 rounded-3xl border border-white/60 shadow-[0_8px_30px_rgb(0,0,0,0.04)] transition-all duration-500 hover:scale-[1.02] hover:shadow-[0_20px_40px_rgb(0,0,0,0.08)] hover:z-20 {getCardAccents(item.type)}">
                            <div class="flex gap-0.5 text-yellow-400 mb-4 text-sm filter drop-shadow-sm">
                                {#each Array(item.stars) as _}<span>⭐</span>{/each}
                            </div>
                            <p class="text-gray-700 leading-relaxed mb-6 font-medium relative z-10">"{item.text}"</p>
                            <div class="flex items-center gap-4">
                                <div class="w-12 h-12 rounded-full bg-gradient-to-tr from-gray-50 to-white border border-gray-100 shadow-sm flex items-center justify-center text-lg font-bold text-gray-600">
                                    {item.name.charAt(0)}
                                </div>
                                <div>
                                    <div class="font-bold text-gray-900 text-[15px]">{item.name}</div>
                                    <div class="text-xs text-primary/60 font-bold uppercase tracking-wider mt-0.5">{item.role}</div>
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>

                <div class="space-y-6 animate-scroll-down hover:pause hidden md:block" style="animation-duration: 140s;">
                    {#each [...testimonials.reverse(), ...testimonials] as item}
                         <div class="group relative bg-white/80 backdrop-blur-sm p-7 rounded-3xl border border-white/60 shadow-[0_8px_30px_rgb(0,0,0,0.04)] transition-all duration-500 hover:scale-[1.02] hover:shadow-[0_20px_40px_rgb(0,0,0,0.08)] hover:z-20 {getCardAccents(item.type)}">
                            <div class="flex gap-0.5 text-yellow-400 mb-4 text-sm filter drop-shadow-sm">
                                {#each Array(item.stars) as _}<span>⭐</span>{/each}
                            </div>
                            <p class="text-gray-700 leading-relaxed mb-6 font-medium relative z-10">"{item.text}"</p>
                            <div class="flex items-center gap-4">
                                <div class="w-12 h-12 rounded-full bg-gradient-to-tr from-gray-50 to-white border border-gray-100 shadow-sm flex items-center justify-center text-lg font-bold text-gray-600">
                                    {item.name.charAt(0)}
                                </div>
                                <div>
                                    <div class="font-bold text-gray-900 text-[15px]">{item.name}</div>
                                    <div class="text-xs text-primary/60 font-bold uppercase tracking-wider mt-0.5">{item.role}</div>
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>

                <div class="space-y-6 animate-scroll-up hover:pause hidden md:block" style="animation-duration: 100s;">
                    {#each [...testimonials.sort(() => Math.random() - 0.5), ...testimonials] as item}
                        <div class="group relative bg-white/80 backdrop-blur-sm p-7 rounded-3xl border border-white/60 shadow-[0_8px_30px_rgb(0,0,0,0.04)] transition-all duration-500 hover:scale-[1.02] hover:shadow-[0_20px_40px_rgb(0,0,0,0.08)] hover:z-20 {getCardAccents(item.type)}">
                            <div class="flex gap-0.5 text-yellow-400 mb-4 text-sm filter drop-shadow-sm">
                                {#each Array(item.stars) as _}<span>⭐</span>{/each}
                            </div>
                            <p class="text-gray-700 leading-relaxed mb-6 font-medium relative z-10">"{item.text}"</p>
                            <div class="flex items-center gap-4">
                                <div class="w-12 h-12 rounded-full bg-gradient-to-tr from-gray-50 to-white border border-gray-100 shadow-sm flex items-center justify-center text-lg font-bold text-gray-600">
                                    {item.name.charAt(0)}
                                </div>
                                <div>
                                    <div class="font-bold text-gray-900 text-[15px]">{item.name}</div>
                                    <div class="text-xs text-primary/60 font-bold uppercase tracking-wider mt-0.5">{item.role}</div>
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>

            </div>
        </div>

    </div>
</section>

<style>
    @keyframes scroll-up {
        0% { transform: translateY(0); }
        100% { transform: translateY(-50%); }
    }
    @keyframes scroll-down {
        0% { transform: translateY(-50%); }
        100% { transform: translateY(0); }
    }

    /* REVISI KECEPATAN: Diperlambat signifikan (120s, 140s, 100s) */
    .animate-scroll-up { animation: scroll-up 120s linear infinite; }
    .animate-scroll-down { animation: scroll-down 120s linear infinite; }
    
    .hover\:pause:hover {
        animation-play-state: paused;
    }
</style>