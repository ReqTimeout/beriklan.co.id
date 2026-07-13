<script>
    import { onMount } from 'svelte';
    import { fade, fly, scale } from 'svelte/transition';

    // --- STATE & DATA ---
    let screen = 'setup'; // setup, chat, dashboard
    let cursor = { x: 50, y: 50, clicking: false };
    
    // Popup Coachmark
    let popup = { show: false, text: '', position: 'bottom' }; 
    
    // Chat Data
    let messages = [];
    let chatLabel = 'COLD';
    let labelColor = 'bg-blue-100 text-blue-600 border-blue-200';
    let typingText = "";
    let isAiThinking = false;

    // Dashboard Data
    let revenue = 0;
    let stats = { chat: 0, cold: 0, medium: 0, hot: 0 };
    let showFinalCTA = false;
    let isClickingCTA = false;

    // --- UTILITIES ---
    const wait = (ms) => new Promise(r => setTimeout(r, ms));
    
    const moveCursor = async (x, y, duration = 1200) => { // Gerakan lebih lambat (1.2s)
        cursor.x = x;
        cursor.y = y;
        await wait(duration);
    };

    const showPopup = async (text, pos = 'bottom') => {
        popup.text = text;
        popup.position = pos;
        popup.show = true;
        await wait(4000); // Waktu baca diperlama (4 detik)
        popup.show = false;
    };

    const click = async () => {
        cursor.clicking = true;
        await wait(200);
        cursor.clicking = false;
        await wait(500);
    };

    // Efek mengetik Haloka AI
    const aiTypes = async (text) => {
        isAiThinking = true;
        await wait(1000); 
        isAiThinking = false;
        
        for (let i = 0; i < text.length; i++) {
            typingText += text[i];
            await wait(30); 
        }
        await wait(500);
        
        messages = [...messages, { 
            text: typingText, 
            sender: 'ai', 
            time: 'Just now',
            type: 'text' 
        }];
        typingText = "";
        scrollChat();
    };

    const sendImage = async (imgName) => {
        isAiThinking = true;
        await wait(1500);
        isAiThinking = false;
        messages = [...messages, { 
            text: imgName, 
            sender: 'ai', 
            time: 'Just now',
            type: 'image' 
        }];
        scrollChat();
    };

    const userReply = (text) => {
        messages = [...messages, { text, sender: 'user', time: 'Just now', type: 'text' }];
        scrollChat();
    };

    const scrollChat = () => {
        setTimeout(() => {
            const el = document.getElementById('chat-container');
            if(el) el.scrollTop = el.scrollHeight;
        }, 100);
    };

    const animateDashboard = async () => {
        const duration = 3000; // Animasi angka lebih pelan biar dramatis
        const endRev = 45200000;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const ease = 1 - Math.pow(2, -10 * progress); 
            
            revenue = Math.floor(ease * endRev);
            stats.chat = Math.floor(ease * 1240);
            stats.cold = Math.floor(ease * 450);
            stats.medium = Math.floor(ease * 520);
            stats.hot = Math.floor(ease * 270);

            if (progress < 1) requestAnimationFrame(animate);
            else showFinalCTA = true;
        };
        requestAnimationFrame(animate);
    };

    // --- SCENARIO SCRIPT ---
    const playScenario = async () => {
        while(true) {
            // RESET
            screen = 'setup';
            messages = [];
            chatLabel = 'COLD';
            labelColor = 'bg-blue-100 text-blue-600 border-blue-200';
            revenue = 0;
            showFinalCTA = false;
            isClickingCTA = false;
            stats = { chat: 0, cold: 0, medium: 0, hot: 0 };
            
            // --- SCENE 1: SETUP ---
            await wait(1000);
            await moveCursor(30, 35);
            await showPopup("1. Masukkan Instruksi Haloka AI: 'Bantu closing gamis'", 'bottom');
            
            // Simulasi klik input
            cursor.clicking = true; await wait(200); cursor.clicking = false;
            
            await moveCursor(20, 70); 
            await showPopup("2. Pilih Produk yang boleh dijual otomatis", 'top');
            await click(); 
            await wait(1500);

            // --- SCENE 2: CHAT START ---
            screen = 'chat';
            await moveCursor(95, 80); // Kursor parkir jauh biar gak ganggu chat
            
            await wait(800);
            userReply("Ada produk gamis? Ukuran M?");
            await showPopup("Chat Masuk! Label awal otomatis: COLD (Biru)", 'top');
            
            await sendImage("Gamis Maroon Syar'i");
            await aiTypes("Ada Ka, ini Gamis Maroon model Aisyah size M. Cantik banget."); // No emoji berlebihan
            await wait(2000);

            // --- SCENE 3: MEDIUM ---
            userReply("Iya benar berapa ka");
            
            // Label Change
            chatLabel = 'MEDIUM';
            labelColor = 'bg-orange-100 text-orange-600 border-orange-200';
            await showPopup("User tanya harga > Label berubah jadi MEDIUM (Oranye)", 'top');
            
            await aiTypes("Harganya Rp 185.000 saja Ka.");
            await wait(2000);

            // --- SCENE 4: SHIPPING ---
            userReply("Kalau ke jakarta ongkirnya berapa ya ka?");
            await aiTypes("Ke Jakarta 14rb Ka. Mau diorder sekarang biar ikut shipping hari ini?");
            await wait(2000);

            // --- SCENE 5: HOT (CLOSING) ---
            userReply("Ok tf kemana");
            
            chatLabel = 'HOT 🔥';
            labelColor = 'bg-red-600 text-white shadow-lg shadow-red-500/50 scale-110';
            await showPopup("DEAL! Label otomatis jadi HOT (Merah)", 'bottom');
            
            await aiTypes("Siap! Silakan transfer ke BCA 123456 Haloka Fashion ya Ka. Ditunggu buktinya 🙏");
            await wait(2500);

            // --- SCENE 6: DASHBOARD & REVENUE ---
            screen = 'dashboard';
            await moveCursor(90, 10); // Kursor minggir ke pojok atas
            await wait(500);
            await animateDashboard();
            
            // Tunggu CTA Muncul
            await wait(3500); 
            
            // --- SCENE 7: CTA CLICK ANIMATION ---
            // Kursor bergerak ke tombol CTA
            await moveCursor(50, 85); 
            
            // Simulasi Klik Tombol
            isClickingCTA = true;
            cursor.clicking = true;
            await wait(300);
            cursor.clicking = false;
            await wait(500);
            isClickingCTA = false;

            // Wait before restart
            await wait(6000);
        }
    };

    onMount(() => {
        playScenario();
    });

    const formatIDR = (num) => new Intl.NumberFormat('id-ID').format(num);
</script>

<section class="py-20 bg-[#0f172a] overflow-hidden relative font-sans">
    
    <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-[#25d366]/10 rounded-full blur-[120px]"></div>

    <div class="container mx-auto px-4 relative z-10">
        
        <div class="text-center mb-10">
            <h2 class="font-display font-bold text-3xl md:text-5xl text-white mb-4">Haloka in Action</h2>
            <p class="text-gray-400">Lihat bagaimana Haloka AI melakukan closing otomatis.</p>
        </div>

        <div class="max-w-4xl mx-auto bg-gray-800 rounded-2xl p-2 shadow-2xl border border-gray-700 relative ring-4 ring-gray-800/50">
            
            <div class="bg-gray-900 rounded-t-xl p-3 flex items-center gap-4 border-b border-gray-800">
                <div class="flex gap-2">
                    <div class="w-3 h-3 rounded-full bg-red-500"></div>
                    <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <div class="w-3 h-3 rounded-full bg-green-500"></div>
                </div>
                <div class="bg-gray-800 px-3 py-1 rounded text-[10px] text-gray-400 font-mono">platform.haloka.id</div>
            </div>

            <div class="relative bg-gray-50 h-[550px] w-full overflow-hidden rounded-b-xl cursor-none select-none">
                
                {#if screen === 'setup'}
                    <div in:fade class="absolute inset-0 bg-white p-8">
                        <h3 class="font-bold text-2xl text-primary mb-6">AI Agent Setup</h3>
                        
                        <div class="mb-6">
                            <label class="text-xs font-bold text-gray-500 uppercase">Instruksi Haloka AI</label>
                            <div class="w-full h-24 bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm text-gray-700 mt-2 relative">
                                Role: CS Haloka Fashion.<br>
                                Task: Bantu closing produk gamis, ramah, dan informatif.<br>
                                <span class="animate-pulse">|</span>
                                <div class="absolute inset-0 border-2 border-blue-400 rounded-lg opacity-0 {cursor.clicking ? 'opacity-100' : ''} transition-opacity"></div>
                            </div>
                        </div>

                        <div>
                            <label class="text-xs font-bold text-gray-500 uppercase">Pilih Produk</label>
                            <div class="mt-2 space-y-2">
                                <div class="flex items-center gap-3 p-3 border rounded-lg bg-green-50 border-green-200 transition-all transform {cursor.clicking ? 'scale-[0.98]' : ''}">
                                    <div class="w-5 h-5 bg-[#25d366] rounded flex items-center justify-center text-white text-xs">✓</div>
                                    <div class="w-10 h-10 bg-red-100 rounded-md flex items-center justify-center text-[10px] font-bold text-red-500">IMG</div>
                                    <div class="text-sm font-bold text-gray-700">Gamis Maroon Aisyah</div>
                                    <div class="ml-auto text-sm font-bold text-green-600">Rp 185.000</div>
                                </div>
                            </div>
                        </div>
                    </div>
                {/if}

                {#if screen === 'chat'}
                    <div in:fade class="absolute inset-0 bg-[#efe7dd] flex flex-col">
                        <div class="bg-white p-3 flex items-center justify-between shadow-sm z-10">
                            <div class="flex items-center gap-3">
                                <div class="w-10 h-10 bg-pink-500 rounded-full flex items-center justify-center text-white font-bold">RC</div>
                                <div>
                                    <div class="font-bold text-gray-800 text-sm">Rina Customer</div>
                                    <div class="text-[10px] text-[#25d366]">Online</div>
                                </div>
                            </div>
                            <div class="{labelColor} px-3 py-1 rounded-full text-[10px] font-bold border transition-all duration-500">
                                {chatLabel} LEAD
                            </div>
                        </div>

                        <div id="chat-container" class="flex-1 p-4 space-y-4 overflow-y-auto scroll-smooth">
                            {#each messages as msg}
                                <div class="flex {msg.sender === 'user' ? 'justify-start' : 'justify-end'} animate-fade-in-up">
                                    <div class="max-w-[75%] shadow-sm text-xs rounded-lg p-2.5 relative 
                                        {msg.sender === 'user' ? 'bg-white text-gray-800 rounded-tl-none' : 'bg-[#dcf8c6] text-gray-800 rounded-tr-none'}">
                                        
                                        {#if msg.type === 'image'}
                                            <div class="mb-2 rounded overflow-hidden">
                                                <div class="w-48 h-32 bg-red-100 flex items-center justify-center text-red-400 font-bold">
                                                    📸 FOTO GAMIS
                                                </div>
                                            </div>
                                        {/if}
                                        
                                        {msg.text}
                                        <div class="text-[9px] text-gray-400 text-right mt-1 opacity-70">
                                            {msg.time} • {msg.sender === 'ai' ? 'Haloka AI' : 'User'}
                                        </div>
                                    </div>
                                </div>
                            {/each}

                            {#if isAiThinking}
                                <div class="flex justify-end">
                                    <div class="bg-white px-3 py-2 rounded-lg rounded-tr-none shadow-sm text-xs text-gray-400 italic">
                                        Haloka AI sedang mengetik...
                                    </div>
                                </div>
                            {/if}
                        </div>

                        <div class="bg-white p-3 flex gap-2 items-center">
                            <div class="flex-1 bg-gray-100 h-10 rounded-full px-4 flex items-center text-xs text-gray-600">
                                {typingText}<span class="animate-pulse ml-1">|</span>
                            </div>
                            <div class="w-10 h-10 bg-[#25d366] rounded-full flex items-center justify-center text-white shadow">➤</div>
                        </div>
                    </div>
                {/if}

                {#if screen === 'dashboard'}
                    <div in:fade class="absolute inset-0 bg-gray-50 p-6 flex flex-col">
                        <h3 class="font-bold text-xl text-primary mb-4">Live Dashboard</h3>
                        
                        <div class="grid grid-cols-4 gap-3 mb-6">
                            <div class="bg-white p-3 rounded-lg shadow-sm border-l-4 border-blue-500">
                                <div class="text-[9px] text-gray-400 font-bold">TOTAL CHAT</div>
                                <div class="text-xl font-bold text-gray-800">{stats.chat}</div>
                            </div>
                            <div class="bg-white p-3 rounded-lg shadow-sm border-l-4 border-blue-200">
                                <div class="text-[9px] text-gray-400 font-bold">COLD</div>
                                <div class="text-xl font-bold text-blue-400">{stats.cold}</div>
                            </div>
                            <div class="bg-white p-3 rounded-lg shadow-sm border-l-4 border-orange-400">
                                <div class="text-[9px] text-gray-400 font-bold">MEDIUM</div>
                                <div class="text-xl font-bold text-orange-500">{stats.medium}</div>
                            </div>
                            <div class="bg-white p-3 rounded-lg shadow-sm border-l-4 border-red-500">
                                <div class="text-[9px] text-gray-400 font-bold">HOT (DEAL)</div>
                                <div class="text-xl font-bold text-red-600">{stats.hot}</div>
                            </div>
                        </div>

                        <div class="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 text-center flex-1 flex flex-col justify-start items-center relative overflow-hidden">
                            <div class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">Total Revenue Hari Ini</div>
                            
                            <div class="text-5xl md:text-6xl font-display font-black text-[#25d366] tracking-tighter z-10">
                                <span class="text-3xl text-gray-300 align-top mr-1">Rp</span>
                                {formatIDR(revenue)}
                            </div>
                            
                            <div class="flex items-end gap-2 h-32 mt-auto w-full justify-center opacity-30 pb-20">
                                <div class="w-8 bg-[#25d366] h-[20%] rounded-t"></div>
                                <div class="w-8 bg-[#25d366] h-[40%] rounded-t"></div>
                                <div class="w-8 bg-[#25d366] h-[30%] rounded-t"></div>
                                <div class="w-8 bg-[#25d366] h-[60%] rounded-t"></div>
                                <div class="w-8 bg-[#25d366] h-[50%] rounded-t"></div>
                                <div class="w-8 bg-[#25d366] h-[90%] rounded-t animate-pulse"></div>
                            </div>
                            
                            {#if showFinalCTA}
                                <div in:fly={{ y: 50, duration: 600 }} class="absolute bottom-10 left-0 w-full flex justify-center z-50 pointer-events-auto">
                                    <a 
                                        href="https://platform.haloka.id/register?billing_type=monthly" 
                                        target="_blank"
                                        class="bg-[#25d366] text-white px-10 py-4 rounded-full font-bold text-lg shadow-2xl hover:bg-[#128c7e] transition-all flex items-center gap-2 transform {isClickingCTA ? 'scale-90 ring-4 ring-green-300' : 'scale-100 hover:scale-105'} border-2 border-white/20"
                                    >
                                        <span>🚀</span> Mulai Trial Gratis 7 Hari
                                    </a>
                                </div>
                            {/if}
                        </div>
                    </div>
                {/if}

                {#if popup.show}
                    <div transition:fade class="absolute z-50 left-1/2 -translate-x-1/2 bg-white text-gray-800 px-5 py-3 rounded-lg text-sm font-bold shadow-2xl border-l-4 border-[#25d366] whitespace-nowrap"
                         style="{popup.position === 'top' ? 'top: 30px' : 'bottom: 30px'}">
                        {popup.text}
                    </div>
                {/if}

                <div class="absolute z-[60] transition-all duration-300 ease-out pointer-events-none drop-shadow-xl"
                     style="left: {cursor.x}%; top: {cursor.y}%;">
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                        <path d="M11.6 27.8C11.6 27.8 8.6 28.2 7.4 25.4C6.2 22.6 1.4 12.6 0.6 10.6C-0.2 8.6 -0.6 6.2 2.6 5.4C5.8 4.6 12.6 2.6 16.6 1.8C20.6 1 23.4 1.4 23.4 3.8C23.4 6.2 18.6 17.8 17.4 20.6C16.2 23.4 14.6 27 14.6 27" fill="white" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    {#if cursor.clicking}
                        <div class="absolute -top-3 -left-3 w-14 h-14 bg-white/30 rounded-full animate-ping"></div>
                    {/if}
                </div>

            </div>
        </div>
    </div>
</section>

<style>
    @keyframes fade-in-up { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    .animate-fade-in-up { animation: fade-in-up 0.3s ease-out forwards; }
</style>