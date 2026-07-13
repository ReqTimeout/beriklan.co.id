<script>
    import { onMount } from 'svelte';
    import { Coffee, Microscope, Rocket, TrendingUp } from 'lucide-svelte';

    let visible = false;

    const steps = [
        {
            num: '01',
            Icon: Coffee,
            title: 'Konsultasi',
            duration: '1 hari',
            body: 'Diskusi gratis 15-30 menit untuk pahami bisnis dan target Anda. Kami di sini untuk dengerin, bukan langsung jualan.',
            deliverables: ['Business profile review', 'Goal mapping', 'Budget recommendation'],
        },
        {
            num: '02',
            Icon: Microscope,
            title: 'Riset & Strategi',
            duration: '3-5 hari',
            body: 'Riset audiens dan siapkan dokumen strategi yang bisa Anda review. Bonus: kami share competitor analysis juga.',
            deliverables: ['Audience persona', 'Competitor analysis', 'Strategic roadmap'],
        },
        {
            num: '03',
            Icon: Rocket,
            title: 'Setup & Launch',
            duration: '5-7 hari',
            body: 'Setup akun iklan, creative, dan tracking. Lalu jalan dengan budget terukur — bisa mulai dari Rp 500rb untuk testing.',
            deliverables: ['Campaign setup', 'Creative production', 'Pixel & tracking'],
        },
        {
            num: '04',
            Icon: TrendingUp,
            title: 'Optimasi & Report',
            duration: 'Ongoing',
            body: 'Optimasi mingguan, laporan bulanan, plus call review 30 menit. Anda gak perlu mikir, kami yang update.',
            deliverables: ['Weekly optimization', 'Monthly report', 'Review call 30 min'],
        },
    ];

    onMount(() => {
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                visible = true;
                observer.disconnect();
            }
        }, { threshold: 0.1 });
        const el = document.getElementById('process');
        if (el) observer.observe(el);
        setTimeout(() => { visible = true; }, 1200);
    });
</script>

<section id="process" class="py-20 md:py-28 bg-white relative overflow-hidden">
    <div class="container mx-auto px-6">
        <div class="text-center max-w-2xl mx-auto mb-16">
            <p class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-accent mb-4">
                <span class="w-8 h-px bg-accent"></span>
                Proses
                <span class="w-8 h-px bg-accent"></span>
            </p>
            <h2 class="font-display font-extrabold text-3xl md:text-5xl text-ink leading-[1.15] tracking-tight">
                4 langkah simpel,
                <span class="block mt-2 text-accent">hasil terukur.</span>
            </h2>
        </div>

        <div class="relative max-w-5xl mx-auto">
            <!-- Connector line (desktop) -->
            <div class="hidden md:block absolute top-12 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-gray-200 to-transparent">
                <div class="h-full bg-gradient-to-r from-accent to-accent-2 origin-left transition-transform duration-1500"
                    style="transform: scaleX({visible ? 1 : 0});"></div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-4 gap-6 md:gap-4">
                {#each steps as step, i}
                    <div class="relative text-center md:text-left"
                        class:opacity-0={!visible}
                        class:translate-y-8={!visible}
                        style="transition-delay: {i * 200}ms; transition-duration: 700ms;">
                        <!-- Step circle -->
                        <div class="relative mx-auto md:mx-0 w-24 h-24 rounded-full bg-gradient-to-br from-accent to-accent-2 flex items-center justify-center text-white shadow-lg mb-5 group hover:scale-110 hover:rotate-6 transition-all duration-500 cursor-default">
                            <svelte:component this={step.Icon} size="36" strokeWidth="2" />
                            <div class="absolute -top-1 -right-1 w-8 h-8 bg-ink text-white rounded-full flex items-center justify-center text-xs font-bold border-2 border-white">{step.num}</div>
                        </div>

                        <!-- Vertical connector (mobile) -->
                        {#if i < steps.length - 1}
                            <div class="md:hidden w-0.5 h-8 bg-gradient-to-b from-accent to-transparent mx-auto my-2"></div>
                        {/if}

                        <div class="inline-flex items-center gap-1 px-2.5 py-1 bg-accent/10 text-accent text-[10px] font-bold uppercase tracking-wider rounded-full mb-2">
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                            {step.duration}
                        </div>
                        <h3 class="font-display font-bold text-lg text-ink mb-2">{step.title}</h3>
                        <p class="text-muted text-sm leading-relaxed mb-3">{step.body}</p>
                        <ul class="space-y-1 text-xs text-muted">
                            {#each step.deliverables as d}
                                <li class="flex items-start gap-1.5 md:justify-start justify-center">
                                    <svg class="w-3 h-3 text-accent mt-0.5 shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                                    <span>{d}</span>
                                </li>
                            {/each}
                        </ul>
                    </div>
                {/each}
            </div>
        </div>

        <!-- CTA bottom -->
        <div class="text-center mt-14">
            <a href="https://wa.me/62811919328?text=Halo%20Beriklan%2C%20saya%20mau%20konsultasi%20gratis" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-ink text-white px-6 py-3 rounded-full font-bold text-sm hover:bg-accent hover:text-ink transition shadow-md hover:shadow-lg">
                Mulai dari Step 1 Sekarang
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg>
            </a>
        </div>
    </div>
</section>
