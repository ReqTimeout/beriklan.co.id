# AGENTS.md — Beriklan.co.id Design & Engineering Playbook

> Comprehensive guide for coding agents (Codex, OpenCode, Cursor, Claude Code, dll)
> yang akan melanjutkan pengembangan website ini. Dokumen ini adalah **single source of truth**
> untuk design system, copywriting pakem, SEO playbook, dan engineering conventions.

---

## 📋 DAFTAR ISI

1. [Project Overview](#1-project-overview)
2. [Tech Stack & Conventions](#2-tech-stack--conventions)
3. [Design System (Token & Komponen)](#3-design-system-token--komponen)
4. [Copywriting Pakem (Bahasa Indonesia Marketing Pro)](#4-copywriting-pakem-bahasa-indonesia-marketing-pro)
5. [SEO Playbook (Eyebrow, Title, Meta, Schema)](#5-seo-playbook)
6. [Struktur File & Routing](#6-struktur-file--routing)
7. [Blog System (WordPress Import & Dynamic Route)](#7-blog-system)
8. [Floating Components (CTA, WhatsApp, Menu)](#8-floating-components)
9. [Hydration Error — Cara Hindari](#9-hydration-error--cara-hindari)
10. [Animations & Micro-interactions](#10-animations--micro-interactions)
11. [Responsive Rules (Mobile-first)](#11-responsive-rules)
12. [Performance Budget](#12-performance-budget)
13. [Common Tasks — Recipes](#13-common-tasks--recipes)
14. [Banned / Hindari](#14-banned--hindari)
15. [Cara Jalankan & Test](#15-cara-jalankan--test)

---

## 1. PROJECT OVERVIEW

**Beriklan.co.id** — Agency performance marketing Indonesia berbasis Bandung.
Mengelola campaign iklan Meta, Google, TikTok, YouTube, dan Landing Page sejak 2016.

**Domain:** `beriklan.co.id` (canonical: `https://beriklan.co.id/`)
**Owner:** Beriklan Digital Agency (admin@3smedianet.com)
**Tujuan:** Lead generation via WhatsApp, brand authority, SEO long-tail traffic
**Target market:** UMKM & bisnis menengah Indonesia, budget iklan Rp 5jt–50jt/bulan

### Voice & Positioning
- **Bukan** agency yang sekadar "pasang iklan"
- **Senior Performance Marketing Partner** — konsultasi strategis, eksekusi terukur
- Hasil bisa dipertanggungjawabkan (dashboard & laporan mingguan)
- Akses penuh ke akun Meta/Google/TikTok klien

---

## 2. TECH STACK & CONVENTIONS

| Layer | Stack | Notes |
|-------|-------|-------|
| Framework | **Astro 5.17** | Static site + island hydration |
| Interactivity | **Svelte 5** | Component untuk elemen interaktif |
| Styling | **Tailwind CSS v3** | Plus custom CSS di `<style>` per-component |
| Animations | **CSS + IntersectionObserver** | NO GSAP/Lottie/framer-motion |
| Icons | **lucide-svelte** | Konsisten di seluruh project |
| Fonts | **Plus Jakarta Sans Variable** | Preloaded dari `/fonts/` |
| WhatsApp | Direct `wa.me/62811919328` link | `?text=` dengan URI-encoded message |
| Deploy target | Cloudflare Pages (atau static host) | Output: `dist/` |

### Directory Structure
```
web/
├── public/
│   ├── data/posts-index.json     # Blog metadata (lightweight, ~14KB)
│   ├── logoweb.webp              # Logo (footer & nav)
│   ├── fonts/                    # Plus Jakarta Sans woff2
│   └── og-image.png
├── src/
│   ├── components/               # Svelte components (interactive)
│   ├── data/posts.json           # Full blog data (build-time, 4MB)
│   ├── layouts/Layout.astro      # HTML shell + global styles + scripts
│   ├── pages/                    # Astro routes
│   │   ├── index.astro
│   │   ├── blog.astro            # Blog index
│   │   ├── blog/[slug].astro     # Dynamic blog post (827 slugs)
│   │   ├── jasa-*.astro          # 10 service pages
│   │   └── order.astro
│   └── styles/global.css         # Tailwind base/components/utilities
└── astro.config.mjs
```

### Command Cheatsheet
```bash
# Dev server (port 4321)
cd web && npm run dev

# Build static site
cd web && npm run build

# Preview build
cd web && npm run preview

# Clear Vite cache (kalau ada hydration error aneh)
rm -rf web/node_modules/.vite web/.astro
```

---

## 3. DESIGN SYSTEM (Token & Komponen)

### 3.1 Brand Colors (Tailwind Config)

```js
// tailwind.config — semantic names
primary:    '#0f1e3d'  // Ink / brand dark (CTA, headlines)
primary-2:  '#1a2f5c'  // Secondary dark
accent:     '#f59e0b'  // Amber / CTA accent (high-convert)
accent-2:   '#fb923c'  // Orange (gradients)
teal:       '#0ea5e9'  // Secondary accent
green:      '#10b981'  // Success / live status
soft:       '#f7f8fb'  // Light bg (cards on white)
beige:      '#fdf6e8'  // Warm bg
ink:        '#0b1426'  // Deepest text
muted:      '#6b7280'  // Secondary text
```

### 3.2 Typography Scale

| Element | Class | Use |
|---------|-------|-----|
| Hero H1 | `text-4xl md:text-5xl lg:text-[2.75rem] xl:text-6xl font-display font-extrabold` | Home hero |
| Service H1 | `text-4xl md:text-5xl lg:text-[2.6rem] xl:text-[2.9rem] font-display font-extrabold` | Service pages |
| Section H2 | `text-3xl md:text-5xl font-display font-extrabold` | Section titles |
| H3 (card) | `text-lg md:text-xl font-display font-bold` | Card titles |
| Body | `text-base md:text-lg text-muted leading-relaxed` | Paragraphs |
| Eyebrow | `text-xs font-bold uppercase tracking-[0.2em] text-accent` | Section labels |
| Hero eyebrow | `text-xs font-semibold tracking-wider uppercase` (in `.hero-eyebrow` pill) | Above H1 |
| Tag pill | `text-[10px] font-bold uppercase tracking-wider` | Featured/Category badges |
| Price (large) | `text-[34px] md:text-[40px] font-display font-extrabold tabular-nums` | Pricing |
| Button | `font-bold text-sm` | CTAs |

**Font family:**
- Display: `font-display` → Plus Jakarta Sans
- Body: `font-sans` → Inter (loaded as fallback)

### 3.3 Spacing & Radius

```
Section padding:    py-20 md:py-28
Container:          container mx-auto px-6
Card padding:       p-6 md:p-8 (or p-7 md:p-8 for PricingCards)
Card radius:        rounded-2xl (default)
Button radius:      rounded-full (pill shape)
```

### 3.4 Shadow Tokens

```css
shadow-soft:    0 1px 2px rgba(15,30,61,0.04), 0 4px 12px rgba(15,30,61,0.04)
shadow-pop:     0 12px 32px rgba(15,30,61,0.10), 0 4px 8px rgba(15,30,61,0.06)
shadow-lg:      0 14px 30px rgba(245,158,11,0.45)  // CTA glow
```

### 3.5 Component Inventory (Reuse, jangan duplikasi)

| Component | File | Purpose |
|-----------|------|---------|
| `Navbar.svelte` | `src/components/` | Top nav + mobile menu |
| `StickyCTA.svelte` | `src/components/` | Desktop panel + mobile bottom sheet (muncul setelah scroll > 500) |
| `FloatingWhatsApp.svelte` | `src/components/` | Mobile FAB → bottom sheet (3 channel) |
| `Footer.svelte` | `src/components/` | Footer dengan alamat Arcamanik |
| `HeroVisual.svelte` | `src/components/` | Dashboard mock (homepage) |
| `PainPoints.svelte` | `src/components/` | 3 pola gagal — homepage |
| `AuditTool.svelte` | `src/components/` | 4-step wizard — homepage |
| `Method.svelte` | `src/components/` | 3 fase kerja — homepage |
| `Services.svelte` | `src/components/` | Grid layanan — homepage |
| `Stats.svelte` | `src/components/` | 4 angka utama |
| `Testimonials.svelte` | `src/components/` | Marquee + featured cards |
| `Faq.svelte` / `FaqAccordion.svelte` | `src/components/` | FAQ accordion |
| `PricingCards.svelte` | `src/components/` | Pricing tiers (1/2/3/4 col) |
| `PricingInteractive.svelte` | `src/components/` | Interactive slider — optional |
| `FinalCTA.svelte` | `src/components/` | Final dark CTA (belum dipakai, pakai inline di index) |
| `FeatureGrid.svelte` | `src/components/` | Feature icons grid |
| `StepGrid.svelte` | `src/components/` | Step cards |
| `RelatedServices.svelte` | `src/components/` | Related service links |
| `BlogFilter.svelte` | `src/components/` | Blog list with filter (fetches JSON) |
| `OrderWizard.svelte` | `src/components/` | Inquiry form |

---

## 4. COPYWRITING PAKEM (Bahasa Indonesia Marketing Pro)

### 4.1 Tone of Voice

- **Persona:** "Senior Performance Marketing Partner" — bukan sales, bukan konsultan kaku
- **Formal-measured** Indonesia dengan industry terms English (ROAS, CPA, funnel) — **always explained on first use**
- **"Anda"** predominant. **"kamu"** hanya di hero opening atau pain section untuk 1 warm moment
- **"kami"** (bukan "kita") untuk konsistensi agency voice
- **No slang**, no "gak", "bikin", "handle iklan", "abal-abal"

### 4.2 Banned Words (JANGAN)

| ❌ Jangan | ✅ Ganti |
|----------|----------|
| "bikin", "gak", "nggak" | "buat", "tidak" |
| "handle iklan" | "mengelola campaign" |
| "pasti", "garansi 100%" | "terukur", "transparan" |
| "50+ bisnis" (fake) | "9 tahun mengelola campaign" |
| "Rating 4.8/5" (fake) | Hapus, atau ganti dengan trust signal nyata |
| "ROAS 4.2x" (kami klaim) | Hanya di dalam mock ad/visual demo |
| "tanpa komitmen" | "tanpa kontrak minimum" |
| "minimum contract" | "kontrak minimum" |
| "subscribe newsletter" | "berlangganan update" |
| "Available · Bandung" (status) | "Tim online · Bandung" |
| "Jl. Contoh No. 123" | "Jl. Arcamanik Endah No.76 — Bandung 40195" |

### 4.3 Power Words (Boleh Dipakai)

`terukur`, `transparan`, `teruji`, `real-time`, `end-to-end`, `prioritas`, `terbukti`,
`spesifik`, `konsisten`, `akunabel`, `independen`, `berbasis data`, `sesuai objective`,
`campaign live`, `dashboard real-time`, `laporan mingguan`, `bahasa manusia`

### 4.4 Copywriting Formulas (per Section)

#### Hero H1 (3 baris, animasi cascade)
```html
<span class="anim-fade-up">Jasa Iklan [Platform]</span><br/>
<span class="anim-fade-up" style="animation-delay: 80ms;">
    yang [Benefit Utama] <span class="text-accent">[Visual Cue].</span>
</span><br/>
<span class="anim-fade-up" style="animation-delay: 160ms;">
    Kami [Authority Cue].
</span>
```

#### Hero Subcopy (max 3 kalimat, bold 1-2 kata)
```
Dari ratusan audit campaign yang kami lakukan, tiga hal paling sering menjadi
akar masalah: **targeting melebar**, **creative tidak selaras** dengan audience,
atau **landing page yang tidak konversi**. Kami mendiagnosa dulu, baru merumuskan
strategi prioritas yang terukur.
```

#### Eyebrow (di atas H1, SEO-targeted — LIHAT SEO PLAYBOOK §5.2)

#### Pain Point Card
Format: Tag → Title (quoted) → Body
```
Tag: "Wasted Spend" / "No Clarity" / "Wrong Channel"
Title: '"Budget keluar, closing tidak bergerak"'
Body: 1-2 kalimat penjelasan dengan observasi pasar.
```

#### Method Step
```
[Minggu X] → Title 1 kata → Subtitle (action verb) → 3 bullet output
```

#### Trust Pill (3 items, max 4 kata per pill)
- "9 th pengalaman"
- "Respon 1 jam"
- "Sertifikasi Meta & Google"

#### Final CTA (3 elemen)
1. **Status badge:** "Tim online · respon dalam 1 jam (jam kerja)"
2. **Headline:** Action-oriented, asymmetric
   - "Beri kami tangkapan layar **Ads Manager Anda.**"
3. **Subcopy:** Apa yang akan mereka dapat
4. **Bullet trust:** 3 kepastian

### 4.5 WhatsApp CTA Convention

```js
const baseWa = 'https://wa.me/62811919328';
const msg = encodeURIComponent(
    `Halo Beriklan, saya tertarik dengan paket ${tier.name} (${pageSlug}) — Rp ${tier.priceLabel}. Mohon info lebih lanjut.`
);
return `${baseWa}?text=${msg}`;
```

**Aturan:**
- Selalu sertakan konteks (paket/layanan/topik)
- Bahasa sopan, tidak memaksa
- Minta info lebih lanjut (bukan "beli sekarang")

---

## 5. SEO PLAYBOOK

### 5.1 Title Hierarchy (per page)

| Page | Title Pattern |
|------|---------------|
| Homepage | `Jasa Digital Marketing Indonesia · Sejak 2016 \| Beriklan` |
| Service | `Jasa [Service] [Benefit] \| [Differentiator] — Beriklan` |
| Blog post | `[Post Title] — Blog Beriklan.co.id` |
| Blog index | `Blog Digital Marketing — Tips, Panduan & Studi Kasus \| Beriklan` |

### 5.2 Hero Eyebrow (SEO-targeted, NO prices)

Pattern: `[Primary Keyword] · [Secondary Keyword] · [Context]`

| File | Eyebrow |
|------|---------|
| `index.astro` | `Performance Agency · Bandung · Sejak 2016` |
| `jasa-digital-marketing.astro` | `Jasa Digital Marketing · Multi-Channel · Bandung` |
| `jasa-iklan-facebook.astro` | `Jasa Iklan Facebook Ads · Meta Business Partner` |
| `jasa-iklan-instagram.astro` | `Jasa Iklan Instagram · Reach & Engagement` |
| `jasa-iklan-tiktok.astro` | `Jasa Iklan TikTok Ads · Spark & FYP` |
| `jasa-iklan-google.astro` | `Jasa Iklan Google Ads · Search, Display & YouTube` |
| `jasa-iklan-youtube.astro` | `Jasa Iklan YouTube · Video Ads & Awareness` |
| `jasa-kelola-instagram.astro` | `Jasa Kelola Instagram · Konten & Community` |
| `jasa-kelola-tiktok.astro` | `Jasa Kelola TikTok · Konten Video Rutin` |
| `jasa-pembuatan-website.astro` | `Jasa Pembuatan Website Profesional · Custom & CMS` |
| `jasa-pembuatan-landing-page.astro` | `Landing Page + Google Ads · Paket Konversi` |
| `order.astro` | `Inquiry & Order · WhatsApp atau Email` |
| `blog.astro` | `Blog · Belajar Digital Marketing Indonesia` |

**Aturan:**
- Eyebrow HARUS berisi primary keyword + supporting keyword (SEO)
- JANGAN ada harga (pricing ada di section Pricing)
- Maksimal 60 karakter
- Format title case (uppercase via CSS)
- Selalu sertakan konteks brand atau lokasi

### 5.3 H1 → Subcopy → CTA Pattern

- **H1:** Primary keyword di 8 kata pertama
- **Subcopy:** 2-3 kalimat, sebutkan masalah + solusi + cara kerja
- **CTA primary:** WhatsApp dengan konteks spesifik
- **CTA secondary:** Scroll ke section pricing/features

### 5.4 Meta Description (per page)

```
[Judul utama]. [1 kalimat value prop]. [CTA].
```

Contoh:
```
"Jasa iklan Facebook Ads dengan targeting presisi dan creative yang teruji.
Tim bersertifikasi Meta Business Partner sejak 2016. Sesi konsultasi awal 15 menit — gratis."
```

### 5.5 Schema Markup (JSON-LD)

Setiap halaman punya:
1. **Organization** (di Layout.astro)
2. **ProfessionalService** (di Layout.astro)
3. **BreadcrumbList** (di setiap page)
4. **Article** (di blog post — generated otomatis dari frontmatter)
5. **FAQPage** (opsional, untuk halaman dengan FAQ)

### 5.6 Sitemap & Robots

- `public/robots.txt`: allow all, point ke sitemap
- `public/sitemap.xml`: generated otomatis via `@astrojs/sitemap`

---

## 6. STRUKTUR FILE & ROUTING

### 6.1 Page Map

```
/                                → Home (index.astro)
/jasa-digital-marketing/         → Multi-channel service
/jasa-iklan-facebook/            → Meta Ads service
/jasa-iklan-instagram/           → IG Ads service
/jasa-iklan-tiktok/              → TikTok Ads service
/jasa-iklan-google/              → Google Ads service
/jasa-iklan-youtube/             → YouTube Ads service
/jasa-kelola-instagram/          → Organic IG management
/jasa-kelola-tiktok/             → Organic TikTok management
/jasa-pembuatan-website/         → Website dev
/jasa-pembuatan-landing-page/    → Landing page + ads bundle
/order/                          → Inquiry form (OrderWizard)
/blog/                           → Blog index (24 posts)
/blog/[slug]/                    → Blog post (827 dynamic routes)
```

### 6.2 Permalinks (PENTING)

Permalinks HARUS match dengan live web (untuk SEO continuity):

| Source | Astro route |
|--------|-------------|
| `https://beriklan.co.id/jasa-iklan-facebook/` | `/jasa-iklan-facebook/` |
| `https://beriklan.co.id/jasa-iklan-facebook-terbaik.html` | `/blog/jasa-iklan-facebook-terbaik/` |
| `https://beriklan.co.id/?p=546` | `/blog/jasa-iklan-facebook-terbaik/` |

Gunakan plugin `@astrojs/sitemap` untuk auto-generate XML sitemap.

---

## 7. BLOG SYSTEM

### 7.1 Arsitektur

1. **WordPress XML export** → di-parse jadi `src/data/posts.json`
2. **Build-time:** Astro `[slug].astro` route generate 827 static pages
3. **Runtime:** BlogFilter fetch `/data/posts-index.json` (lightweight, 14KB) untuk tampilkan 24 post terbaru

### 7.2 Re-import dari WordPress

```bash
# 1. Export XML dari WordPress admin (Tools → Export)
# 2. Letakkan di /Users/maabook/Desktop/beriklan.co.id/jasadigitalmarketing.WordPress.YYYY-MM-DD.xml
# 3. Jalankan parser:
python3 /tmp/parse_wp.py
# (sesuaikan XML_PATH di script jika nama file berbeda)

# 4. Generate lightweight index:
python3 -c "
import json
data = json.load(open('web/src/data/posts.json'))
light = [{'slug':p['slug'],'title':p['title'],'excerpt':p['excerpt'],
          'date':p['date'],'iso_date':p['iso_date'],'category':p['category'],
          'readTime':p['readTime'],'featured':p['featured'],'tags':p['tags'][:5]}
         for p in data[:24]]
open('web/public/data/posts-index.json','w').write(json.dumps(light, ensure_ascii=False, indent=2))
"
```

### 7.3 Parser Logic (di `parse_wp.py`)

- Filter hanya `post_type="post"` dan `status="publish"`
- Skip posts dengan content < 200 karakter (low quality)
- Filter keyword non-DM (ada 16 posts alat-lab yang di-skip)
- Hitung read time: `words / 200` (Bahasa Indonesia reading speed)
- Classify ke 6 kategori berdasarkan slug + tags:
  - `meta` → facebook, instagram, meta-ads
  - `tiktok` → tiktok, fyp, spark
  - `google` → google, adwords, search, seo, keyword
  - `youtube` → youtube, video-ads, bumper
  - `case-study` → studi-kasus, roas, kisah
  - `strategy` → default

### 7.4 Single Post Page (`[slug].astro`)

Generate otomatis dari `posts.json` via `getStaticPaths()`.
Setiap post punya:
- Breadcrumb (Beranda › Blog › [Kategori])
- Category pill (orange)
- Title (H1)
- Metadata bar (tanggal, read time, author)
- Article body (HTML sanitized, formatted via `.prose` class)
- Tags chips
- Inline CTA card (WhatsApp)
- Related posts (3 dari kategori sama)

**Schema.org Article** JSON-LD di setiap post (headline, datePublished, author, dll).

---

## 8. FLOATING COMPONENTS

### 8.1 Navbar (`Navbar.svelte`)

```svelte
<!-- Desktop: dropdown hover dengan scheduleClose (150ms delay) -->
<!-- Mobile: hamburger → full-screen accordion -->
<!-- Trust strip: 9 th, Respon 1 jam, Sertifikasi Meta & Google -->
<!-- Live status: "Tim online · siap merespon" -->
```

**Mobile menu structure (penting):**
1. Logo (footer logo, invert white)
2. Close button (top-right, white pill)
3. Hero block: status badge + headline "Mau scale up penjualan via iklan?" + 3 trust pills
4. Nav groups (accordion): Paid Ads (with "PALING DICARI" badge), Social Media, Website & Landing Page
5. Top-level singles: Digital Marketing, Blog
6. Quick contact: Telepon
7. WhatsApp CTA (orange, big)

### 8.2 StickyCTA (`StickyCTA.svelte`)

- **Muncul setelah scroll > 500px**
- **Desktop:** Always-expanded 280px panel (WhatsApp + Telepon + Email + close)
- **Mobile:** Collapsed FAB → tap opens bottom sheet
- WA pulse ring animation

### 8.3 FloatingWhatsApp (`FloatingWhatsApp.svelte`)

- **Mobile:** FAB hijau → tap opens polished bottom sheet dengan avatar + 3 channel
- **Desktop:** FAB hijau + label "Diskusi via WhatsApp" (auto-hide setelah 5.5s)
- Auto-hide pada scroll > 800px (mobile) agar tidak menutupi konten
- "1" badge merah (notifikasi)
- Header sheet: "Konsultan Beriklan" + "Respon 1 jam · jam kerja"

---

## 9. HYDRATION ERROR — CARA HINDARI

**Wajib: `client:only="svelte"` untuk SEMUA Svelte component.**

```astro
<!-- ❌ JANGAN -->
<Navbar client:visible />

<!-- ✅ BENAR -->
<Navbar client:only="svelte" />
```

**Alasan:**
- Svelte 5 + lucide-svelte sering throw `Illegal invocation` atau `hydration_mismatch`
- `client:only` skip SSR total — render fresh di browser
- Bundle lebih besar sedikit, tapi reliability lebih tinggi

**Kecuali:** Kalau component benar-benar static (no JS, no animation), boleh pakai
`client:visible` atau bahkan SSR biasa.

### Kalau Masih Ada Hydration Error:
1. **Clear Vite cache:** `rm -rf web/node_modules/.vite web/.astro`
2. **Restart dev server:** `kill <pid>; npm run dev`
3. **Hard refresh browser:** `Cmd+Shift+R`
4. **Inspect error stack:** lihat file & line number di `.svelte`/`.astro`

---

## 10. ANIMATIONS & MICRO-INTERACTIONS

### 10.1 Sistem Reveal (existing, di Layout.astro)

```css
.reveal { opacity: 0; transform: translateY(20px); transition: 0.7s; }
.reveal.revealed { opacity: 1; transform: translateY(0); }

.reveal-stagger > * { opacity: 0; transform: translateY(16px); transition: 0.6s; }
.reveal-stagger.revealed > * { opacity: 1; transform: translateY(0); }
/* + nth-child delays: 0, 80, 160, 240, 320, 400ms */
```

Triggered by IntersectionObserver (threshold 0.1, rootMargin -60px) di Layout.astro.

### 10.2 Hero Cascade Animations

```html
<span class="anim-fade-up">Line 1</span><br/>
<span class="anim-fade-up" style="animation-delay: 80ms;">Line 2</span><br/>
<span class="anim-fade-up" style="animation-delay: 160ms;">Line 3</span>
```

### 10.3 Hover Micro-interactions (Cards)

```css
.pricing-card:hover { transform: translateY(-4px); }
.service-card:hover { transform: translateY(-4px); border-color: ...; }
.dd-item:hover .dd-dot { transform: scale(1.6); }
```

### 10.4 Pulse / Live Indicators

```html
<span class="relative flex h-2 w-2">
    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
    <span class="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
</span>
```

### 10.5 CTA Shine (button)

```css
.btn-shine { position: relative; overflow: hidden; }
.btn-shine::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
  background: linear-gradient(110deg, transparent 30%, rgba(255,255,255,0.5) 50%, transparent 70%);
  transition: left 0.6s ease; }
.btn-shine:hover::before { left: 100%; }
```

### 10.6 WhatsApp Pulse Ring

```css
.wa-pulse-ring { position: absolute; border-radius: 9999px;
  background: rgba(37, 211, 102, 0.45);
  animation: wa-ping 2.2s cubic-bezier(0, 0, 0.2, 1) infinite; }
@keyframes wa-ping { 0% { transform: scale(1); opacity: 0.6; }
  80%, 100% { transform: scale(1.9); opacity: 0; } }
```

### 10.7 Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
    /* Disable all animations */
}
```

---

## 11. RESPONSIVE RULES (Mobile-first)

### 11.1 Breakpoints

| Name | Min-width | Use |
|------|-----------|-----|
| (base) | 0 | Mobile-first default |
| `sm:` | 640px | Small tablet |
| `md:` | 768px | Tablet |
| `lg:` | 1024px | Desktop |
| `xl:` | 1280px | Wide desktop |

### 11.2 Mobile-Specific Rules

- **Tombol minimum tap target:** 44x44px
- **Font minimum body:** 14px (text-sm)
- **Section padding:** `py-16 md:py-20` atau `py-20 md:py-28`
- **Hero:** single-column di mobile, 2-column di `lg:`
- **Floating components:** hanya di mobile, atau beda treatment di desktop
- **Mobile menu:** full-screen overlay, accordion groups

### 11.3 Testing Viewports

```js
// Always test di 3 viewport:
const viewports = [
    { width: 390, height: 844 },   // iPhone 14
    { width: 768, height: 1024 },  // iPad
    { width: 1440, height: 900 },  // Desktop
];
```

---

## 12. PERFORMANCE BUDGET

- **Initial JS:** < 200KB gzipped (per page)
- **LCP:** < 2.5s
- **CLS:** < 0.1
- **FID:** < 100ms
- **Fonts:** Preload Plus Jakarta Sans woff2
- **Images:** Always `<img loading="lazy">` kecuali hero (eager)
- **Largest Contentful Paint candidate:** Selalu hero H1 atau HeroVisual

### Lazy Loading Svelte Components
```astro
<Navbar client:only="svelte" />  <!-- not lazy, but client:only skip SSR -->
<HeavyVisual client:visible />   <!-- lazy when visible -->
```

---

## 13. COMMON TASKS — RECIPES

### 13.1 Tambah Service Page Baru

```bash
# 1. Copy template
cp src/pages/jasa-iklan-facebook.astro src/pages/jasa-iklan-google-bisnis.astro

# 2. Update di file baru:
#    - Title meta
#    - Eyebrow text
#    - H1 (primary keyword di awal)
#    - Tiers pricing
#    - Features, steps, FAQs
#    - Internal links (RelatedServices)

# 3. Update Layout.astro canonical
# 4. Test di localhost:4321/jasa-iklan-google-bisnis/
```

### 13.2 Tambah Blog Post Manual

```bash
# 1. Append ke web/src/data/posts.json:
{
    "slug": "artikel-baru",
    "title": "Judul Artikel",
    "excerpt": "Ringkasan 150-180 karakter.",
    "content": "<p>HTML content...</p>",
    "date": "13 Jul 2026",
    "iso_date": "2026-07-13T10:00:00",
    "category": "strategy",
    "readTime": "5 min",
    "liveUrl": "",
    "tags": ["tag1", "tag2"],
    "featured": false
}

# 2. Append ke web/public/data/posts-index.json (ringan, tanpa content)

# 3. Test di /blog/artikel-baru/
```

### 13.3 Update Copy di Semua Page

```bash
# Pakai grep dulu untuk lihat semua occurrences
grep -rn "lama copy ini" src/

# Replace global (verify dulu)
find src/ -name "*.astro" -o -name "*.svelte" | xargs sed -i '' 's/lama/baru/g'
```

### 13.4 Audit Hydration Errors

```bash
# 1. Clear cache
rm -rf web/node_modules/.vite web/.astro

# 2. Restart dev
kill $(lsof -ti:4321); cd web && npm run dev &

# 3. Playwright test all pages
cat > /tmp/audit.mjs << 'EOF'
import { chromium } from 'playwright';
const browser = await chromium.launch();
const urls = ['/', '/jasa-digital-marketing/', '/jasa-iklan-facebook/',
    '/jasa-iklan-instagram/', '/jasa-iklan-tiktok/', '/jasa-iklan-google/',
    '/jasa-iklan-youtube/', '/jasa-kelola-instagram/', '/jasa-kelola-tiktok/',
    '/jasa-pembuatan-website/', '/jasa-pembuatan-landing-page/',
    '/order/', '/blog/'];
for (const url of urls) {
    const ctx = await browser.newContext();
    const page = await ctx.newPage();
    const errs = [];
    page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    page.on('pageerror', e => errs.push(e.message));
    await page.goto('http://localhost:4321' + url, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2500);
    const hyd = errs.filter(e => /hydrat|Failed to hydrate|Illegal/.test(e));
    console.log(url, hyd.length === 0 ? 'OK' : 'ERR:' + hyd.length);
    await ctx.close();
}
await browser.close();
EOF
node /tmp/audit.mjs
```

### 13.5 Capture Screenshots untuk QA

```js
// /tmp/qa.mjs
import { chromium } from 'playwright';
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await ctx.newPage();
await page.goto('http://localhost:4321/?cb=' + Date.now(), { waitUntil: 'networkidle' });
await page.waitForTimeout(2500);
// Scroll all
const h = await page.evaluate(() => document.body.scrollHeight);
for (let y = 0; y < h; y += 600) {
    await page.evaluate(_y => window.scrollTo(0, _y), y);
    await page.waitForTimeout(150);
}
await page.evaluate(() => window.scrollTo(0, 0));
await page.waitForTimeout(500);
await page.screenshot({ path: '/tmp/qa-full.png', fullPage: true });
await browser.close();
```

---

## 14. BANNED / HINDARI

### 14.1 Library/Framework
- ❌ React, Vue, jQuery
- ❌ GSAP, Framer Motion, Lottie (overkill)
- ❌ Bootstrap, Material UI
- ❌ Berat analytics scripts (Hotjar berat, fullstory)

### 14.2 Pattern
- ❌ `client:visible` / `client:idle` untuk komponen berat (gunakan `client:only`)
- ❌ Inline styles untuk hal yang berulang (gunakan Tailwind class)
- ❌ Hardcoded warna di component (selalu pakai token dari config)
- ❌ English slang di copy ("bikin", "gak", etc.)
- ❌ Over-promise: "100% closing", "pasti untung", "tanpa risiko"
- ❌ Fake social proof: "50+ klien aktif", "Rating 4.8/5", "ROAS 4.2x" (kami klaim)

### 14.3 CSS Anti-pattern
- ❌ `!important` (kecuali utility override)
- ❌ Inline `<style>` panjang di .astro (pakai `<style is:global>` atau component)
- ❌ Magic numbers tanpa token

---

## 15. CARA JALANKAN & TEST

### Setup
```bash
cd /Users/maabook/Desktop/beriklan.co.id/web
npm install
npm run dev  # localhost:4321
```

### Build
```bash
npm run build
npm run preview
```

### Quick QA Workflow
```bash
# 1. Clear cache & restart
rm -rf web/node_modules/.vite web/.astro
kill $(lsof -ti:4321) 2>/dev/null
cd web && nohup npm run dev </dev/null >/tmp/astro-dev.log 2>&1 &
disown

# 2. Verify server up
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:4321/

# 3. Run hydration audit (script di §13.4)
node /tmp/audit.mjs

# 4. Capture screenshots
node /tmp/qa.mjs

# 5. Verify visually (buka /tmp/qa-full.png)
```

### Production Deploy (Cloudflare Pages)
```bash
npm run build
# Upload dist/ ke Cloudflare Pages
# Set env: NODE_VERSION=20, OUTPUT_DIR=dist
```

---

## 📞 CONTACT & ESCALATION

- **Klien:** Beriklan Digital Agency
- **Email:** info@beriklan.co.id
- **WhatsApp:** +62 81.1919.328
- **Alamat:** Jl. Arcamanik Endah No.76, Bandung 40195

Untuk pertanyaan design system atau copywriting baru, **SELALU rujuk ke `COPY-BIBLE.md`**
dan `PER-PAGE-REDESIGN-PLAN.md` di root project.

---

## 🚀 DEPLOYMENT KE CLOUDFLARE — PENTING!

**Sebelum kerja deployment apa pun, BACA file `DEPLOY_OPERATIONS.md` di root project & GitHub!**

Lokasi file:
- Lokal: `/Users/maabook/Desktop/beriklan.co.id/beriklan.co.id/DEPLOY_OPERATIONS.md`
- GitHub: https://github.com/ReqTimeout/beriklan.co.id/blob/main/DEPLOY_OPERATIONS.md

Isi file tersebut:
- Account ID, Zone ID, API token (zone-scoped)
- Workers project state (`beriklanweb` script + zone-level Workers Routes)
- Endpoint API yang WORKS vs yang TIDAK works dengan token ini
- Gotchas: jangan taruh `410` di `_redirects`, field name `script` bukan `script_name`
- Workflow lengkap: push GitHub → CF auto-build → verify via curl
- Recovery steps kalau deploy rusak

**JANGAN PERNAH:**
- Deploy via `wrangler deploy` dari terminal (token zone-scope, gak cukup)
- Minta token baru ke user sebelum test endpoint yang ada
- Lempar balik ke user — kalau ada akses, EKSEKUSI sendiri via API

**Yang bisa dilakukan via API sekarang:**
- Update DNS records (semua subdomain + apex + www)
- Add/remove Workers Routes (`/zones/{id}/workers/routes`)
- Read semua zone info
- Push code ke GitHub (pakai GH PAT yang ada)
- Verify live via curl

---

**Versi dokumen:** 1.2
**Update terakhir:** 13 Juli 2026 (added deployment section + DEPLOY_OPERATIONS.md)
**Maintainer:** Beriklan Digital Agency + Codex AI
