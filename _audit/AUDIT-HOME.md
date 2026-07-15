# Beriklan.co.id — Home Page Audit

**Tanggal:** 2026-07-12
**Auditor:** Mavis
**Scope:** `http://localhost:4321/` (dev) + `http://127.0.0.1:4322/` (prod build)
**Status:** 90% bagus, 4 critical issue yang harus fix sebelum push ke user

---

## TL;DR — Yang harus fix duluan

| # | Severity | Issue | Fix effort |
|---|----------|-------|------------|
| 1 | 🔴 Critical | Sticky navbar ketutup top bar saat scroll | 15 min |
| 2 | 🔴 Critical | Typo Mandarin di AuditTool copy | 1 min |
| 3 | 🟡 High | Stats angka animasi dari 0 (tampak broken) | 10 min |
| 4 | 🟡 High | Web fonts via Google Fonts (blocking) | 30 min |
| 5 | 🟢 Med | 236KB unused assets di dist (logo.png, favicon.*) | 2 min |
| 6 | 🟢 Med | Hero copy masih bisa lebih "standout" | 30 min |
| 7 | 🟢 Low | Emoji as UI icons (anti-preference Bos) | 2 jam |

---

## 1. 🔴 STICKY NAVBAR BUG (Confirmed)

**Symptom:** Saat user scroll, top bar (header info) tetap nempel di `top:0 z-[60]`, tapi Navbar `fixed md:top-0 top-9` — saat `isScrolled=true` Navbar pindah ke `top:0` tapi top bar masih nutup dia. Hasil: menu navigasi setengah ke-cut.

**Screenshot bukti:**
- `d-prod-scrolled-100.png` — menu "Website, Digital Marketing, Social Media, News, Pasang Iklan Gratis" + button "INQUIRY" cuma keliatan setengah huruf.
- `d-scroll-300.png`, `d-scroll-1200.png`, `d-scroll-2000.png`, `d-scroll-3500.png` — sama, sepanjang scroll halaman.

**Root cause:**
```svelte
<!-- Top bar — fixed top-0 z-60, tidak bergerak -->
<div class="bg-primary ... fixed top-0 w-full z-[60] hidden md:block">

<!-- Navbar — md:top-9 saat awal, md:top-0 saat scroll -->
<nav class="fixed {isScrolled ? 'md:top-0' : 'md:top-9'} top-0 w-full z-50 ...">
```

z-50 (Navbar) vs z-[60] (Top bar) — top bar selalu di atas, Navbar naik ke top-0 tapi ketutup.

**Fix (rekomendasi):** Top bar slide up saat scroll, Navbar ambil alih.

```svelte
<!-- Top bar: hide saat scroll -->
<div class="bg-primary ... fixed top-0 w-full z-[60] hidden md:block transition-transform duration-300"
     class:-translate-y-full={isScrolled}>

<!-- Navbar: tetap di md:top-0 sticky, raise shadow lebih jelas saat scroll -->
<nav class="fixed md:top-0 top-0 w-full z-50 transition-all duration-300 
            {isScrolled ? 'bg-white shadow-md py-3' : 'bg-white md:bg-white/80 md:backdrop-blur-sm py-4 md:py-5'}">
```

Plus tambah `padding-top` ke `<body>` atau hero agar tidak lompat saat top bar hilang. Current `pt-36 md:pt-44` di hero sudah ada buffer, jadi smooth.

**Effort:** 15 menit (1 file: `Navbar.svelte`)

---

## 2. 🔴 TYPO MANDARIN DI COPY

**File:** `src/components/AuditTool.svelte` baris 87

```js
else if (budget === '5-15') { 
    pkg = 'Growth'; 
    price = '5.000.000'; 
    reasoning.push('Sudah找到了 product-market fit, siap untuk scale-up.');  // ← BUG
    matchScore = 96; 
}
```

`找到了` = bahasa Mandarin ("ditemukan"). Sangat terlihat di UI setelah user selesai audit dan dapat rekomendasi "Growth" — langsung menurunkan trust.

**Fix:** Ganti ke Bahasa Indonesia natural. Contoh:
```js
reasoning.push('Sudah dapat product-market fit, siap untuk scale-up.');
```

**Effort:** 1 menit

---

## 3. 🟡 STATS COUNTER ANIMATION (UX issue)

**File:** `src/components/Stats.svelte`

Counter animasi dari 0 → 50/5M+/8Tahun/92% saat section masuk viewport. Masalahnya: animation 2 detik dengan cubic ease, jadi **di 800-1500ms pertama, user lihat angka random** seperti 23+, Rp 2M+, 4 Tahun, 45% — semua setengah-setengah. Trust langsung drop.

**Fix (rekomendasi):** Start dari baseline 70-80% supaya animasi ke angka final kelihatan "filling up" bukan "growing from nothing". Atau fade in angka final tanpa counter, biar tidak misleading.

```js
// Option A: start dari baseline
const baseline = 0.7;
counters = stats.map((s) => Math.round(s.value * (baseline + (1 - baseline) * ease)));

// Option B: langsung show final
counters = stats.map((s) => s.value);
// + animasi count-up visual pakai transform/opacity saja
```

**Effort:** 10 menit

---

## 4. 🟡 GOOGLE FONTS BLOCKING (Performance)

**File:** `src/layouts/Layout.astro` baris 102-104

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```

**Metrics impact (production):**
- FCP: 424ms
- 20.5KB blocking CSS (Google Fonts stylesheet)
- 26.6KB woff (font) dari fonts.gstatic.com
- 1 third-party request (privacy/CWV penalty)

**Plus inkonsistensi dengan brand spec Bos:**
> Typography: Instrument Serif italic (display) + Geist (heading) + Inter (body) + Geist Mono (data) — all self-hosted

Project sekarang pakai **Plus Jakarta Sans + Inter** (bukan Instrument Serif + Geist) + dari **Google Fonts** (bukan self-hosted). Dua-duanya meleset dari spec.

**Fix (rekomendasi):** 
- **Quick win:** Self-host Plus Jakarta Sans + Inter pakai `@fontsource/plus-jakarta-sans` & `@fontsource/inter` via npm, drop Google Fonts `<link>`. Zero layout shift, no third-party, faster.
- **Strategic:** Migrate ke Instrument Serif (display) + Geist (heading) + Inter (body) sesuai spec. Lebih premium feel.

Effort quick win: 30 menit (npm install + replace 1 link tag).
Effort strategic: 1-2 jam (download fonts, configure, redesign display typography).

---

## 5. 🟢 UNUSED ASSETS DI DIST (Wasted bandwidth)

**Build output:** 692KB total, **236KB (34%) unused.**

File yang di-dist tapi tidak pernah di-reference di HTML/JS:
```
dist/logo.png       132 KB   ← tidak ada yg reference
dist/favicon.png     33 KB   ← tidak ada yg reference
dist/favicon.svg   0.7 KB   ← tidak ada yg reference
dist/favicon.ico   0.7 KB   ← tidak ada yg reference
dist/whatsapp.svg    1 KB   ← tidak ada yg reference
```

Source: `public/` (di-copy mentah ke dist/ via Astro). Yang dipakai: cuma `logoweb.webp` (4.7KB) di `<img src>` di Navbar & Footer + favicon.

**Fix:** Hapus dari `public/`:
```bash
rm /Users/maabook/Desktop/beriklan.co.id/web/public/logo.png \
   /Users/maabook/Desktop/beriklan.co.id/web/public/favicon.ico \
   /Users/maabook/Desktop/beriklan.co.id/web/public/favicon.png \
   /Users/maabook/Desktop/beriklan.co.id/web/public/favicon.svg \
   /Users/maabook/Desktop/beriklan.co.id/web/public/whatsapp.svg
```

**Effort:** 2 menit (file deletion + verify tidak ada reference)

---

## 6. 🟢 HERO "STANDOUT" — Yang bisa di-improve

Hero saat ini **sudah premium** (navy + amber, dashboard mockup, ROAS counter, floating notifications). Tapi ada beberapa area yang bisa di-push untuk lebih "wow":

### 6.1 Eyebrow text lebih impact
Current: `DIGITAL AGENCY INDONESIA · 2016—2026`
Suggestion: tambah **social proof inline** — sesuatu yang instantly membangun trust.
```
✓ Trusted by 50+ Indonesian businesses since 2016
```
Atau: `RATED 4.8/5 ★ · 52 REVIEW · 8 TAHUN`

### 6.2 H1 sudah bagus, sub bisa lebih "punchy"
Current sub:
> Setiap campaign yang kami jalankan dimulai dari riset audiens yang serius, creative yang match, dan optimasi mingguan berdasarkan data. Hasilnya? ROAS rata-rata klien kami 4.2x — di atas rata-rata industri.

Agak panjang. Suggestion: pecah jadi benefit-led + risk-led.
> ROAS 4.2x, di atas rata-rata industri. Bukan karena jago — tapi karena **riset audiens serius, creative yang match, optimasi mingguan** dari data, bukan tebak-tebakan.

### 6.3 Trust strip lebih "specific"
Current: `50+ bisnis aktif | 8 tahun pengalaman | Rp 5M+ iklan/bulan`

Suggestion: tambah 1-2 metric lain yang lebih jarang di competitor, misal:
- "120+ juta user Indonesia reach" (untuk FB Ads)
- Atau: "97% client renewal year-on-year" (kalau ada datanya)

### 6.4 Hero visual sudah sangat kuat
Dashboard mockup + animated counter + floating notifications + 7-day trend chart — ini level premium, ga perlu banyak diubah. Mungkin 1 tweak: tambah **small annotation arrow** yang point ke angka ROAS, supaya user langsung tau "ini yang penting".

**Effort:** 30-60 menit untuk apply 6.1 + 6.2 + 6.3

---

## 7. 🟢 EMOJI AS UI ICONS (Anti-preference)

Bos profile: **"anti emoji as UI icon"** (firmly established).

Current violation (counted):
| Component | Emoji icons |
|-----------|-------------|
| `PainPoints.svelte` | 💸 📊 🤷 |
| `HeroVisual.svelte` | 💰 🎯 📈 ⚡ + 4 in floating notifs (✓ 📈 💬 🎯) |
| `AuditTool.svelte` | 📘 🔍 🎵 🎯 🌱 🌿 🌳 🚀 ⏱️ 📅 📆 🏆 📞 🛒 📢 🌐 (16!) |
| `Stats.svelte` | 🤝 💰 ⚡ 🎯 |
| `Services.svelte` | 📒 📷 🎵 🚀 🔍 ▶️ 🌐 🎬 📱 (9) |
| `Pricing.svelte` | (hanya checkmark, OK) |
| `Method.svelte` | (icon target, magnifier, palette, dll) |

Total: **~45 emoji icons** yang harus di-replace dengan custom SVG.

**Fix strategy:**
- Kalau mau cepat: pakai icon library seperti **Lucide Svelte** (`lucide-svelte`) — sudah ada tree-shaking, 1.5KB per icon
- Kalau mau premium: custom inline SVG (style konsisten dengan brand)

Effort: 1-2 jam untuk replace semua. Bisa di-defer ke phase berikutnya.

---

## Performance Snapshot (Production build)

| Metric | Value | Status |
|--------|-------|--------|
| FCP | 424ms | 🟢 Bagus |
| LCP | (n/a di test) | ? |
| DOMContentLoaded | 322ms | 🟢 Bagus |
| Total transfer | 22.3KB | 🟢 Bagus |
| Total requests | 22 | 🟢 OK |
| JS gzipped | ~75KB (17 chunks) | 🟡 Bisa di-reduce |
| CSS | 100KB (1 file) | 🟢 OK |
| Google Fonts blocking | 20.5KB CSS | 🟡 Improve |
| Unused assets | 236KB | 🔴 Remove |

**Bundle composition:**
- 17 Svelte islands hydrated. Bisa di-reduce dengan `client:visible` (lazy) atau SSR-only untuk components yang tidak butuh interactivity.

---

## Mobile (390px viewport)

| Aspek | Status | Notes |
|-------|--------|-------|
| Hero wrap | 🟢 OK | "Iklan jalan, duit masuk." wrap jadi 2 lines natural |
| H1 readability | 🟢 OK | Plus Jakarta Sans fallback Inter aman |
| Pain points | 🟢 OK | Card stack vertical, tag WASTED SPEND muat |
| Method steps | 🟢 OK | Card stack 1-col, badge "STEP 01/06" visible |
| Services grid | 🟢 OK | Tab "Semua/Performance/Social/Web" responsive, cards stack |
| Testimonials | 🟢 OK | Cards stack, tapi horizontal scroll untuk aksesi ke card 2/4 |
| Pricing | 🟢 OK | Toggle Bulanan/Tahunan, cards stack dengan "PALING POPULER" badge |
| FAQ | 🟢 OK | Accordion vertical |
| Final CTA | 🟢 OK | Centered, button full width |
| Footer | 🟢 OK | Multi-column stack |
| Sticky nav | 🟢 OK di mobile | Top bar hidden (md:block), Navbar fixed top-0 selalu visible |
| Sticky CTA bottom | 🟢 OK | Tampil setelah scroll > 800px, dismissible |

**Mobile verdict:** Tidak ada critical mobile bugs. Hero, sections, pricing, footer semua render dengan baik di 390px. Yang bisa di-improve: testimonial carousel di mobile masih horizontal-scroll (terlihat dari screenshot `m-testimonials`), mungkin bisa swipe-snap.

---

## Copy Quality (Quick scan)

### Strengths
- Bahasa Indonesia natural & conversational ("duit masuk", "gak ada yang convert", "gak match sama audience")
- Specific numbers > generic claims (50+ bisnis, 8 tahun, ROAS 4.2x, 92% retention)
- Concrete process (6 ritual method, 4-step audit)
- Risk-aware: "bukan survey abal-abal", "bukan asal launch", "optimasi bukan nyalahin algoritma"
- Bahasa Jakarta yang hidup, bukan terjemahan kaku

### Improvements
- **Bahasa campur English** di beberapa tempat tanpa italic: "testing", "PMF", "scale-up", "lead gen", "sales", "awareness", "traffic", "ROAS" — OK untuk niche digital marketing tapi bisa di-bold/italic untuk clarity
- **Plus Jakarta Sans** untuk display mungkin kurang dramatic — Instrument Serif italic untuk display akan jauh lebih premium feel
- **Action button copy** konsisten (✓ "Konsultasi Gratis 15 Menit", "Chat WhatsApp Sekarang", "Mulai Starter", "Pilih Growth")
- **FAQ copy** sudah komprehensif dan honest (acknowledging "Tergantung platform dan industri")

### Red flags
- 🇨🇳 Typo Mandarin di AuditTool (lihat issue #2)
- ⚠️ "Optimasi mingguan" di hero vs "1x call review bulanan" di pricing tier — pastikan tidak misleading

---

## Recommended Action Plan

### Phase 1: Critical Fixes (1 jam)
1. Fix sticky navbar (`Navbar.svelte`) — 15 min
2. Fix typo Mandarin (`AuditTool.svelte`) — 1 min
3. Fix stats counter animation (`Stats.svelte`) — 10 min
4. Hapus unused assets (`public/`) — 2 min
5. Verify: `npm run build && npm run preview` — 5 min

### Phase 2: Performance (1 jam)
6. Self-host fonts (npm install fontsource, replace `<link>` di Layout) — 30 min
7. Audit Svelte island hydration (banyak `client:visible` — pastikan yang butuh interaktif saja) — 30 min

### Phase 3: Polish (2-3 jam)
8. Hero copy improvements (eyebrow + sub + trust strip) — 30 min
9. Replace emoji icons dengan Lucide Svelte — 1-2 jam
10. Add `font-display: swap` optimization untuk font loading
11. Add meta `theme-color` untuk mobile browser chrome

### Phase 4: After Home Beres
12. Audit per-page: `/jasa-pembuatan-landing-page`, `/jasa-iklan-facebook`, dll (12 service pages)
13. Audit 159 location × service pages (template-based)
14. Audit blog migration (846 posts)

---

## File Inventory

```
src/
├── pages/index.astro                ← home, 333 lines, OK
├── layouts/Layout.astro             ← SEO + GTM shell, OK (kecuali fonts)
├── components/
│   ├── Navbar.svelte                ← ⚠️ sticky bug
│   ├── StickyCTA.svelte             ← OK
│   ├── HeroVisual.svelte            ← OK (very strong)
│   ├── PainPoints.svelte            ← OK (copy bagus)
│   ├── AuditTool.svelte             ← 🇨🇳 typo bug
│   ├── Method.svelte                ← OK (visual strong)
│   ├── Stats.svelte                 ← ⚠️ counter animation issue
│   ├── Services.svelte              ← OK
│   ├── ProcessTimeline.svelte       ← OK
│   ├── Testimonials.svelte          ← OK
│   ├── Pricing.svelte               ← OK
│   ├── Faq.svelte                   ← OK
│   ├── Footer.svelte                ← OK
│   ├── FloatingWhatsApp.svelte      ← OK
│   ├── HowItWorks.svelte            ← (tidak dipakai di index? perlu cek)
│   ├── InteractiveTutorial.svelte   ← (tidak dipakai di index? perlu cek)
│   ├── SocialProof.svelte           ← (tidak dipakai di index? perlu cek)
│   ├── ChatSimulator.svelte         ← (tidak dipakai di index? perlu cek)
│   ├── PriceLogic.svelte            ← (tidak dipakai? perlu cek)
│   ├── TrustBadges.svelte           ← (tidak dipakai? perlu cek)
│   ├── FinalCTA.svelte              ← (tidak dipakai di index; pakai inline di index.astro)
│   ├── Features.svelte              ← (tidak dipakai di index? perlu cek)
│   ├── PricingInteractive.svelte    ← (tidak dipakai di index? perlu cek)
│   └── Welcome.astro                ← (legacy? perlu cek)
├── assets/                          ← (kosong? perlu cek)
└── styles/global.css                ← (kosong, 22 bytes)
```

**Dead code candidates:** FinalCTA, Features, PricingInteractive, SocialProof, ChatSimulator, TrustBadges, PriceLogic, InteractiveTutorial, HowItWorks, Welcome.astro, FloatingWhatsApp — banyak yang tidak di-render di `index.astro`. Perlu audit untuk cleanup.

---

**Status dokumen:** baseline audit sebelum implementasi fix.
**Last update:** 2026-07-12
