<script>
    import { onMount } from 'svelte';
    import { MessagesSquare, Hammer, TrendingUp, ArrowRight } from 'lucide-svelte';

    let visible = false;

    const steps = [
        {
            num: '01',
            Icon: MessagesSquare,
            title: 'Diagnosa',
            headline: 'Kami dengar dulu. Baru action.',
            desc: 'Kick-off 30 menit — kami gali goal, budget, audience, hambatan, plus apa yang sudah Anda coba. Output: brief eksekusi yang jadi pegangan tim.',
            tag: 'MINGGU 1',
            deliverable: 'Brief Strategi',
            deliverables: ['Audit akun lama', 'Persona & mapping', 'Channel decision'],
        },
        {
            num: '02',
            Icon: Hammer,
            title: 'Eksekusi',
            headline: 'Bangun, launch, monitor.',
            desc: 'Copy, visual, video, setup tracking — semuanya paralel. Campaign live di minggu ke-2. Anda tetap approve tiap milestone, kami eksekusi.',
            tag: 'MINGGU 2',
            deliverable: 'Campaign Live',
            deliverables: ['Creative siap tayang', 'Pixel & tracking oke', 'A/B test aktif'],
        },
        {
            num: '03',
            Icon: TrendingUp,
            title: 'Optimasi',
            headline: 'Pantau ketat. Iterasi cepat.',
            desc: 'Review mingguan dari data — bukan asumsi. Yang performanya di bawah standar, kami ganti. Yang jalan, kami scale. Anda cukup approve summary.',
            tag: 'MINGGU 3+',
            deliverable: 'Scale-up',
            deliverables: ['Report bahasa yang mudah dipahami', 'Pivot cepat', 'Scaling winner'],
        },
    ];

    onMount(() => {
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                visible = true;
                observer.disconnect();
            }
        }, { threshold: 0.1 });
        const el = document.getElementById('method');
        if (el) observer.observe(el);
        setTimeout(() => { visible = true; }, 800);
    });
</script>

<section id="method" class="py-20 md:py-28 bg-white relative overflow-hidden">
    <div class="absolute inset-0 opacity-30 pointer-events-none method-dots"></div>

    <!-- Decorative curved dashed arrow -->
    <svg class="absolute top-24 left-8 w-32 h-12 opacity-50 hidden md:block" viewBox="0 0 120 40" aria-hidden="true">
        <path d="M5,30 Q60,0 110,30" stroke="#f59e0b" stroke-width="1.5" fill="none" stroke-dasharray="4 5"/>
        <polygon points="110,30 102,22 102,38" fill="#f59e0b"/>
    </svg>
    <svg class="absolute bottom-32 right-8 w-24 h-12 opacity-50 hidden md:block" viewBox="0 0 100 40" aria-hidden="true">
        <path d="M5,10 Q50,40 95,10" stroke="#0ea5e9" stroke-width="1.5" fill="none" stroke-dasharray="4 5"/>
    </svg>

    <div class="container mx-auto px-6 relative">
        <div class="max-w-2xl mx-auto text-center mb-14 reveal">
            <p class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-accent">
                <span class="w-6 h-px bg-accent"></span>
                Cara Kerja · Tiga Tahap Terstruktur
                <span class="w-6 h-px bg-accent"></span>
            </p>
            <h2 class="font-display font-extrabold text-3xl md:text-5xl text-ink leading-[1.1] tracking-tight mt-3">
                Dari keraguan awal,<br/>
                <span class="text-accent">menuju sistem iklan yang terukur.</span>
            </h2>
            <p class="mt-4 text-muted text-base">
                Tidak ada janji berlebihan. Tidak ada proses yang tidak transparan. Setiap minggu, Anda mengetahui secara persis apa yang sedang kami kerjakan dan alasan di baliknya.
            </p>
        </div>

        <div class="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 relative reveal-stagger">
            <!-- Connector line -->
            <div class="hidden md:block absolute top-[88px] left-[16.67%] right-[16.67%] h-px z-0 method-line"></div>

            {#each steps as step, i}
                <div
                    class="method-card group relative bg-white rounded-2xl p-6 md:p-7 border border-gray-100 hover:border-accent/40 transition-all duration-300 z-10"
                    style="transition-delay: {i * 130}ms;"
                >
                    <!-- Top: number + tag -->
                    <div class="flex items-center justify-between mb-5">
                        <span class="text-[10px] font-bold uppercase tracking-widest text-muted">{step.num}</span>
                        <span class="text-[9px] font-bold uppercase tracking-wider text-accent bg-accent/10 px-2 py-0.5 rounded-full">
                            {step.tag}
                        </span>
                    </div>

                    <!-- Icon -->
                    <div class="method-icon w-14 h-14 rounded-2xl bg-ink text-white flex items-center justify-center mb-5 transition-all duration-300">
                        <svelte:component this={step.Icon} size="26" strokeWidth="2" />
                    </div>

                    <h3 class="font-display font-extrabold text-xl text-ink mb-1">{step.title}</h3>
                    <p class="text-sm font-bold text-accent mb-3">{step.headline}</p>
                    <p class="text-sm text-muted leading-relaxed mb-5">{step.desc}</p>

                    <!-- Deliverable items list -->
                    <ul class="space-y-1.5 mb-5">
                        {#each step.deliverables as d, j}
                            <li class="method-list-item flex items-start gap-2 text-xs text-muted">
                                <svg class="w-3.5 h-3.5 text-accent mt-0.5 shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                                <span>{d}</span>
                            </li>
                        {/each}
                    </ul>

                    <!-- Deliverable pill -->
                    <div class="flex items-center justify-between pt-4 border-t border-gray-100">
                        <span class="text-[10px] uppercase tracking-wider font-bold text-muted">Output minggu ini</span>
                        <span class="text-xs font-bold text-ink inline-flex items-center gap-1 method-pill">
                            {step.deliverable}
                            <ArrowRight class="w-3 h-3 text-accent method-arrow" />
                        </span>
                    </div>
                </div>
            {/each}
        </div>

        <!-- Bottom CTA -->
        <div class="mt-14 text-center">
            <a href="https://wa.me/62811919328?text=Halo%20Beriklan%2C%20saya%20mau%20konsultasi%20gratis" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-ink text-white px-7 py-3.5 rounded-full font-bold text-sm hover:bg-accent hover:text-ink transition-all shadow-md group anim-fade-up btn-shine" style="animation-delay: 600ms;">
                <span class="relative z-10 flex items-center gap-2">
                    Tanya Detail di WhatsApp
                    <ArrowRight class="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </span>
            </a>
        </div>
    </div>
</section>

<style>
    .method-card {
        transition: opacity 0.6s cubic-bezier(0.22, 1, 0.36, 1),
                    transform 0.6s cubic-bezier(0.22, 1, 0.36, 1),
                    box-shadow 0.3s ease,
                    border-color 0.3s ease;
    }
    .method-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px -8px rgba(15, 30, 61, 0.15);
    }
    .method-card:hover .method-icon {
        background: #f59e0b;
        transform: rotate(-6deg) scale(1.05);
    }
    .method-card:hover .method-pill { color: #f59e0b; }
    .method-card:hover .method-arrow { transform: translateX(4px); }

    .method-line {
        background: linear-gradient(90deg, transparent 0%, #f59e0b 50%, transparent 100%);
        background-size: 200% 100%;
        animation: line-flow 3s linear infinite;
    }
    @keyframes line-flow {
        from { background-position: 100% 0; }
        to { background-position: -100% 0; }
    }

    .method-dots {
        background-image: radial-gradient(circle at 2px 2px, rgba(15,30,61,0.05) 1px, transparent 0);
        background-size: 32px 32px;
    }

    .method-list-item {
        opacity: 0;
        animation: fadeUp 0.5s ease forwards;
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateX(-6px); }
        to { opacity: 1; transform: translateX(0); }
    }

    .btn-shine { position: relative; overflow: hidden; }
    .btn-shine::after {
        content: ""; position: absolute; inset: 0;
        background: linear-gradient(110deg, transparent 25%, rgba(255,255,255,0.18) 50%, transparent 75%);
        transform: translateX(-100%);
        transition: transform 0.6s ease;
    }
    .btn-shine:hover::after { transform: translateX(100%); }
</style>
