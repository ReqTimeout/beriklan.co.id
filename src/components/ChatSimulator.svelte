<script>
  import { onMount } from 'svelte';
  import { fly, fade } from 'svelte/transition';

  let messages = [];
  let isTyping = false;

  // SKENARIO BARU: Lebih Natural, Jeda Cukup, Ending Closing
  const chatScenario = [
    { type: 'user', text: 'Halo Ka, mau curhat. Iklan jalan terus, lead banyak masuk, tapi kok closing dikit banget ya? 😔', delay: 500 },
    
    { type: 'typing', delay: 1500 }, // Jeda ngetik agak lama biar natural
    { type: 'bot', text: 'Halo Juragan! 👋 Biasanya itu karena telat balas Ka. Customer zaman now kalau gak dibalas 5 menit, langsung pindah ke toko sebelah.', delay: 2000 },
    
    { type: 'user', text: 'Nah itu dia.. Admin saya kewalahan kalau chat lagi membludak. Suka lupa follow-up juga, akhirnya customer ghosting.', delay: 4500 }, // Jeda baca user agak lama
    
    { type: 'typing', delay: 1500 },
    { type: 'bot', text: 'Sayang banget boncos di iklan dong? 😅', delay: 1000 },
    
    { type: 'typing', delay: 1200 },
    { type: 'bot', text: 'Pakai Haloka aja Ka. AI-nya bisa handle ribuan chat sekaligus 24 jam + otomatis "kejar" customer yang ghosting sampai jadi closing.', delay: 4000 },
    
    { type: 'user', text: 'Wah serius bisa gitu? Tapi saya gaptek, takut mahal dan ribet..', delay: 5000 },
    
    { type: 'typing', delay: 1500 },
    { type: 'bot', text: 'Gak perlu bayar dulu Ka. Mending ambil akses **Trial Gratis 7 Hari** sekarang. Setting cuma 5 menit kok.', delay: 2500 },
    
    // ENDING BARU: USER DEAL -> BOT REASSURANCE
    { type: 'user', text: 'Oke deh sy coba daftar ya Ka. Penasaran juga pengen nyoba.', delay: 4000 },
    
    { type: 'typing', delay: 1500 },
    { type: 'bot', text: 'Siap! Keputusan tepat Juragan. 🔥', delay: 1000 },
    { type: 'bot', text: 'Nanti Kaka cukup pantau Dashboard saja sambil santai. Biarkan Haloka yang bikin bisnis Kaka jalan otomatis 24 jam. 🚀', delay: 3000 }
  ];

  onMount(() => {
    let timeline = 0;
    chatScenario.forEach((step) => {
      timeline += step.delay;
      setTimeout(() => {
        if (step.type === 'typing') {
          isTyping = true;
          scrollToBottom();
        } else {
          isTyping = false;
          messages = [...messages, step];
          scrollToBottom();
        }
      }, timeline);
    });
  });

  const scrollToBottom = () => {
    setTimeout(() => {
      const chatBox = document.getElementById('chat-scroll-area');
      if(chatBox) chatBox.scrollTop = chatBox.scrollHeight;
    }, 100);
  };
</script>

<div class="relative mx-auto border-gray-900 bg-gray-900 border-[12px] rounded-[2.5rem] h-[650px] w-[340px] shadow-2xl shadow-blue-900/40 flex flex-col overflow-hidden transform hover:scale-105 transition-transform duration-500 ease-out">
    <div class="bg-[#075e54] p-4 pt-8 text-white flex items-center gap-3 shadow-md z-20 relative">
        <div class="relative">
            <div class="w-10 h-10 rounded-full bg-white flex items-center justify-center text-[#075e54] font-bold text-lg border-2 border-white/20">H</div>
            <div class="absolute bottom-0 right-0 w-3 h-3 bg-green-400 rounded-full border-2 border-[#075e54] animate-pulse"></div>
        </div>
        <div>
            <h3 class="font-display font-bold text-base tracking-wide">Haloka Support</h3>
            <p class="text-[10px] text-green-100 flex items-center gap-1">
                <span class="inline-block w-1.5 h-1.5 rounded-full bg-green-400"></span> Online 24 Jam
            </p>
        </div>
    </div>

    <div id="chat-scroll-area" class="flex-1 bg-[#ece5dd] p-4 overflow-y-auto space-y-4 pb-20 scroll-smooth relative">
        <div class="absolute inset-0 opacity-[0.06] bg-[url('/whatsapp.svg')] bg-repeat space-y-10 pointer-events-none grayscale"></div>

        <div class="text-center mb-4">
            <span class="bg-[#dcf8c6] text-gray-600 text-[10px] px-3 py-1 rounded shadow-sm font-medium">Hari Ini</span>
        </div>

        {#each messages as msg}
            <div 
                in:fly="{{ y: 10, duration: 400 }}" 
                class="flex {msg.type === 'user' ? 'justify-end' : 'justify-start'} relative z-10"
            >
                <div class="max-w-[85%] rounded-xl p-3 text-sm shadow-sm leading-relaxed 
                    {msg.type === 'user' 
                        ? 'bg-[#d9fdd3] text-gray-800 rounded-tr-none' 
                        : 'bg-white text-gray-800 rounded-tl-none border border-gray-100'}"
                >
                    {@html msg.text}
                    <div class="text-[9px] text-gray-400 text-right mt-1 opacity-70">
                        Just now <span class={msg.type === 'user' ? 'text-blue-500 font-bold' : ''}>{msg.type === 'user' ? '✓✓' : ''}</span>
                    </div>
                </div>
            </div>
        {/each}

        {#if isTyping}
            <div in:fade class="flex justify-start relative z-10">
                <div class="bg-white rounded-xl rounded-tl-none p-4 shadow-sm border border-gray-100 w-16">
                    <div class="flex gap-1.5 justify-center">
                        <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></div>
                        <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                        <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                    </div>
                </div>
            </div>
        {/if}
    </div>

    <div class="absolute bottom-0 left-0 w-full bg-[#f0f0f0] p-3 flex items-center gap-2 z-20">
        <div class="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-400">➕</div>
        <div class="flex-1 bg-white rounded-full h-10 px-4 text-sm flex items-center text-gray-400 border border-gray-200 shadow-inner">
            Mau coba Trial dong...
        </div>
        <div class="w-10 h-10 rounded-full bg-[#075e54] flex items-center justify-center text-white shadow-lg hover:bg-[#128c7e] transition">
            ➤
        </div>
    </div>
</div>