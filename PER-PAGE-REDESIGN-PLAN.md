# PER-PAGE REDESIGN PLAN — beriklan.co.id
## Inventory Live Site × Copy SEO × Pricing Aktual × Animasi Svelte (pola Haloka)

> **Versi:** 1.0 · 2026-07-11  
> **Sumber audit:** Live `https://www.beriklan.co.id` (home, 10 money pages, order, footer nav)  
> **Stack animasi:** Svelte 5 islands (seperti Haloka) — konteks diganti per layanan  
> **Pricing:** **Ikuti harga & fitur yang sudah live di web** (bukan invent dari COPY-BIBLE lama)  
> **Tone copy:** Marketing profesional, SEO-friendly, Bahasa Indonesia formal-measureed (“Anda/kami”)

Dokumen ini melengkapi `PREMIUM-REDESIGN-PLAN.md` dengan **detail per halaman**.

---

## A. AUDIT LIVE SITE — MENU & LAYANAN

### A.1 Global chrome (setiap page)

| Elemen | Live sekarang | Redesign |
|---|---|---|
| Top bar | Socio.id link, WA `+62.81.1919.328`, email `info@beriklan.co.id` | Pertahankan kontak; WA primary CTA |
| Logo | WP logo image | `logoweb.webp` + text lockup |
| Menu | “Menu” hamburger generik + **Inquiry → `/order`** | Mega-menu + Inquiry |
| Footer col 1 | About | About + alamat Bandung |
| Footer col 2 Social Ads | TikTok Ads, FB Ads, IG Ads, Kelola TikTok, Kelola IG | Sama + link benar semua |
| Footer col 3 Google Ads | Google Search, YouTube, Website, Landing Page | + Digital Marketing umbrella |
| Footer | Subscribe email, © Beriklan, WhatsApp widget | Sama + form newsletter + sticky WA |
| Alamat (order) | Jl. Arcamanik Endah No.76, Sukamiskin, Arcamanik, Bandung 40293 | Cantum di kontak + schema LocalBusiness |
| WA link | `bit.ly/BeriklanWhatsApp` / `api.whatsapp.com/send?phone=62811919328` | Unified deep-link builder |

### A.2 Sitemap navigasi redesain (mirror live + rapi)

```
Header
├── Beranda                    /
├── Layanan ▾
│   ├── Digital Marketing      /jasa-digital-marketing     (umbrella)
│   ├── Facebook Ads           /jasa-iklan-facebook
│   ├── Instagram Ads          /jasa-iklan-instagram
│   ├── TikTok Ads             /jasa-iklan-tiktok
│   ├── Google Ads             /jasa-iklan-google
│   ├── YouTube Ads            /jasa-iklan-youtube
│   ├── Kelola Instagram       /jasa-kelola-instagram
│   ├── Kelola TikTok          /jasa-kelola-tiktok
│   ├── Pembuatan Website      /jasa-pembuatan-website
│   └── Landing Page           /jasa-pembuatan-landing-page
├── Blog                       /blog
├── Inquiry / Order            /order          [CTA button]
└── WhatsApp                   sticky + header

Footer (+ extra)
├── Tentang                    /tentang        (baru, dari about footer)
├── Kontak                     /kontak         (baru, mirror order contacts)
└── Socio.id                   external partner
```

### A.3 Money pages (core — URL **dipertahankan**)

| # | URL live | H1/topic live | Pricing live (wajib diikuti) |
|---|---|---|---|
| 1 | `/` | Digital Agency / jasa digital marketing | — (teaser ke layanan) |
| 2 | `/jasa-digital-marketing` | Meningkatkan bisnis dengan jasa digital marketing | CTA konsultasi (no fixed tiers di live) |
| 3 | `/jasa-iklan-facebook` | Jasa iklan Facebook | **Standart Rp 1.750.000** · **Business Rp 3.750.000** /bln |
| 4 | `/jasa-iklan-instagram` | Jasa iklan Instagram | **Standart Rp 1.750.000** · **Business Rp 3.750.000** /bln |
| 5 | `/jasa-iklan-tiktok` | Jasa/pasang iklan TikTok | **Basic 1jt (7hr)** · **Standart 1,6jt (14hr)** · **Business 3,75jt (30hr)** |
| 6 | `/jasa-iklan-google` | Jasa iklan Google / Search | **Basic 1,75jt** · **Standart 3,75jt** · **Business 6jt** /bln |
| 7 | `/jasa-iklan-youtube` | Jasa iklan YouTube | **Basic 1,25jt (14hr)** · **Starter 2,5jt** · **Standart 3,75jt** · **Business 4,75jt** |
| 8 | `/jasa-kelola-instagram` | Jasa kelola Instagram | **Basic 2,5jt** · **Standart 3,5jt** · **Business Call us** |
| 9 | `/jasa-kelola-tiktok` | Jasa kelola TikTok | **TikTok Shop 1,5jt** · **Basic Content 3jt** · **Business Content 4jt** |
| 10 | `/jasa-pembuatan-website` | Jasa pembuatan website | **Basic Rp 999.000/th** · Professional Call · Business Call |
| 11 | `/jasa-pembuatan-landing-page` | Landing Page + Google Ads promo | **Paket promo Rp 1.999.000** (LP + 1 bln Google Ads) |
| 12 | `/order` | Inquiry / pasang iklan | Form + contact cards |
| 13 | `/blog` | Latest blogs | Index + posts |

### A.4 Fitur paket LIVE (detail — source of truth pricing)

#### Facebook Ads (`/jasa-iklan-facebook`)

| | Standart | Business |
|---|---|---|
| Harga | **Rp 1.750.000** | **Rp 3.750.000** |
| Periode | 30 hari tayang | 30 hari tayang |
| Estimasi jangkauan | 3.000–9.000 audience/hari | 4.000–15.000 audience/hari |
| Placement | Semua penempatan Facebook | Semua penempatan Facebook |
| Kreatif | 2 iklan (10 foto atau 1 video) | 3 iklan (10 foto atau 1 video) |
| Lainnya | Iklan dapat diganti | Iklan dapat diganti |

#### Instagram Ads — **sama struktur harga FB**

| | Standart | Business |
|---|---|---|
| Harga | **Rp 1.750.000** | **Rp 3.750.000** |
| Periode | 30 hari | 30 hari |
| Jangkauan | 3.000–9.000 /hari | 4.000–15.000 /hari |
| Placement | Semua penempatan Instagram | Semua Instagram |
| Kreatif | 2 iklan (10 foto / 1 video) | 3 iklan (10 foto / 1 video) |

#### TikTok Ads

| | Basic | Standart | Business |
|---|---|---|---|
| Harga | **Rp 1.000.000** | **Rp 1.600.000** | **Rp 3.750.000** |
| Goal | Brand awareness | Traffic | Traffic & lead |
| Durasi | 7 hari | 14 hari | 30 hari |
| Estimasi views | 15.000–30.000 | 20.000–50.000 | 50.000–75.000 |
| Iklan | 1 post TikTok | 1 post | 3 posts |
| Lainnya | Bisa diganti | Bisa diganti | Lead/klik/konversi |

#### Google Ads

| | Basic | Standart | Business |
|---|---|---|---|
| Harga | **Rp 1.750.000** | **Rp 3.750.000** | **Rp 6.000.000** |
| Budget harian | Rp 50.000 | Rp 100.000 | Rp 175.000 |
| Kata kunci | 10 | 15 | 20 |
| Include | Analisis keyword + report bulanan | sama | sama |

#### YouTube Ads

| | Basic | Starter | Standart | Business |
|---|---|---|---|---|
| Harga | **Rp 1.250.000** | **Rp 2.500.000** | **Rp 3.750.000** | **Rp 4.750.000** |
| Durasi | 14 hari | 30 hari | 30 hari | 30 hari |
| Estimasi | 35.000 tayangan | 75.000 tayangan | ~10.000 views | 50.000 tayangan + ~8.000 views |
| Format | Non-skippable 6–15 dtk | Non-skippable | Skippable | Skippable + non-skippable |

#### Kelola Instagram

| | Basic | Standart | Business |
|---|---|---|---|
| Harga | **Rp 2.500.000** | **Rp 3.500.000** | **Call us** |
| Konten | 15 design feed (tanpa video) | 20 design + 2 short video | Custom |
| Story | 5 | 10 | Custom |
| Lainnya | Konsep, timeline, copy, posting, report | + 15 foto produk*, report | Call us |

#### Kelola TikTok

| | TikTok Shop | Basic Content | Business Content |
|---|---|---|---|
| Harga | **Rp 1.500.000** | **Rp 3.000.000** | **Rp 4.000.000** |
| Deliverable | Upload 30 produk, edit foto, 1× ads 7hr, affiliate, optimasi followers, report | 15 video (5 edukasi + 5 entertainment + 5 review), riset musik, copy, konsep, report | 30 video (10+10+10), full package |

#### Website

| | Basic (Starter) | Professional (Corporate) | Business (E-commerce) |
|---|---|---|---|
| Harga | **Rp 999.000 / 1 tahun** | **Call us / 1 tahun** | **Call us / 1 tahun** |
| Halaman | 1 landing | 5 halaman | 25 halaman |
| Email | 1 | 5 | 25 |
| Revisi | 1× | 2× | 3× |
| SEO | Basic | Basic | Basic |
| Extra | — | — | Payment & shipping gateways |

#### Landing Page promo

| Paket | Harga | Include |
|---|---|---|
| **Landing Page + Google Ads** | **Rp 1.999.000** | 1 LP, 1 bulan Google Ads, copy, form kontak, integrasi ads, tracking & analisis |

> **Catatan implementasi:** Pricing cards = data hardcode `src/lib/data/pricing.ts` disalin 1:1 dari tabel di atas. Label paket (Standart/Business) **dipertahankan** agar familiar klien existing. Copy boleh dipoles; **angka harga tidak diganti** tanpa approval.

---

## B. POLA HALOKA → ADAPTASI BERIKLAN (per section)

Haloka memakai **Svelte island per section** dengan `client:visible` / `client:load`.  
Beriklan **menyalin pola**, ganti konteks demo.

| Pola Haloka | Komponen Svelte generic | Adaptasi konteks |
|---|---|---|
| Hero demo product | `HeroDemo.svelte` | Dashboard ads / feed mock / search SERP / video player / site builder — **beda per page** |
| Sticky CTA | `StickyCta.svelte` | “Konsultasi WA” + harga mulai Rp X |
| Trust badges | `TrustStrip.svelte` | Partner Meta/Google + alamat Bandung |
| Pain drama | `PainCards.svelte` | Pain per platform |
| Interactive calc | `*Calculator.svelte` | Estimasi jangkauan / CPC / views (opsional) |
| Features bento | `FeatureGrid` (Astro) + `TiltCard` | Fitur targeting / deliverable |
| How it works | `ProcessSteps.svelte` | 4 langkah onboarding |
| Social proof | `TestimonialSlider.svelte` | Testimoni (live: Arin, Ulfia, Witia di LP/web) |
| Pricing interactive | `PricingCards.svelte` | Toggle highlight tier; CTA → WA prefilled paket |
| FAQ | `FaqAccordion.svelte` | FAQ keyword-rich |
| Final CTA | `FinalCta.svelte` | Urgency profesional (bukan “limited fake”) |

**Hydration policy (lebih hemat dari Haloka):**
- `client:load` → Navbar, StickyCta
- `client:visible` → HeroDemo, PricingCards, Faq, ProcessSteps, Calculator
- Sisanya `.astro` static

---

## C. TEMPLATE UNIVERSAL SERVICE PAGE

Setiap money service page memakai **11 section** berikut.  
Isi copy + animasi diganti per layanan di §D.

| # | Section ID | Component | Animasi Svelte (Haloka-style) |
|---|---|---|---|
| 0 | nav | Navbar | Mobile drawer spring; mega-menu fade |
| 1 | hero | ServiceHero + **HeroDemo** | Demo context-specific; headline TextReveal; CTA shimmer |
| 2 | trust | TrustStrip | Logo marquee CSS + NumberTicker micro-stats |
| 3 | why | WhyPlatform | 3 pain/benefit cards ScrollReveal stagger |
| 4 | features | FeatureGrid | TiltCard 6 fitur; icon SVG draw-on-view |
| 5 | how | ProcessSteps | Stepper interactive (active step highlight) |
| 6 | pricing | PricingCards | Card scale on select; price NumberTicker; CTA magnetic |
| 7 | proof | Testimonials | Auto marquee dual-row atau slider |
| 8 | faq | FaqAccordion | Height spring expand (seperti Haloka Faq) |
| 9 | related | RelatedServices | Static cards + hover lift |
| 10 | final | FinalCta + StickyCta | Gradient mesh pulse; sticky bar after 40% scroll |

**Schema tiap service page:** `Service` + `Offer` (per tier) + `FAQPage` + `BreadcrumbList`.

---

## D. DETAIL PER HALAMAN

---

### D.0 GLOBAL — Navbar + Footer + Widgets

**Navbar copy**
- Primary CTA: `Inquiry` → `/order`
- Secondary: `Chat WhatsApp`
- Mega-menu groups:
  - **Paid Ads:** Facebook, Instagram, TikTok, Google, YouTube  
  - **Organic:** Kelola Instagram, Kelola TikTok  
  - **Build:** Website, Landing Page  
  - **Full service:** Digital Marketing  

**Svelte**
- `Navbar.svelte` — scroll compact, mobile sheet, mega panel
- `WhatsAppFloat.svelte` — pulse ring (Haloka sticky vibe)
- `StickyCta.svelte` — muncul >40% scroll; text dinamis per page (`Mulai dari Rp 1.750.000` dll.)

**Footer SEO links:** semua 10 layanan + blog + order + socio.id

---

### D.1 HOMEPAGE `/`

**SEO**
| Field | Copy |
|---|---|
| Title | `Jasa Digital Marketing Indonesia \| Beriklan Digital Agency` |
| Meta | `Jasa digital marketing untuk Facebook Ads, Instagram, TikTok, Google Ads, YouTube, kelola sosial media, dan website. Konsultasi gratis — Bandung, Indonesia.` |
| H1 | `Jasa Digital Marketing yang Menumbuhkan Prospek, Bukan Hanya Impresi` |
| Primary KW | jasa digital marketing, digital agency Indonesia |

**Sections + copy (marketing pro)**

1. **Hero**  
   - Eyebrow: `Beriklan Digital Agency · Bandung`  
   - H1: di atas  
   - Sub: `Kami merancang dan menjalankan campaign multi-platform — Meta, Google, TikTok, dan YouTube — agar bisnis Anda menjangkau audiens yang tepat dan mengonversi ke WhatsApp, telepon, atau penjualan.`  
   - CTA primary: `Konsultasi Gratis via WhatsApp`  
   - CTA secondary: `Lihat Layanan`  
   - **HeroDemo (Svelte):** Ads Command Center — multi-channel spend bars + “lead masuk” toast (analog ChatSimulator Haloka)

2. **Trust** — Partner Meta/Google visual, alamat Bandung, “Inquiry 24 jam kerja”

3. **Layanan highlight (6 kartu live home)**  
   Facebook Ads · Google Search · GDN (link ke Google Ads) · Website · Instagram · TikTok · Social Media Mgmt ·  
   Short blurb dari live home, dipoles SEO.

4. **Pain (3)**  
   - Budget iklan jalan tanpa konversi jelas  
   - Sulit pilih channel yang cocok  
   - Tidak ada reporting yang bisa ditindaklanjuti  

5. **Proses 4 langkah** — Konsultasi → Setup → Tayang → Optimasi & laporan

6. **Pricing teaser** — “Paket mulai dari”  
   - Meta Ads dari **Rp 1.750.000**/bln  
   - Google Ads dari **Rp 1.750.000**/bln  
   - TikTok Ads dari **Rp 1.000.000**  
   - Website dari **Rp 999.000**/th  
   - Landing Page promo **Rp 1.999.000**  
   Link ke masing-masing service (bukan invent tier Starter 2,5jt)

7. **Blog latest** — 3–6 posts

8. **Final CTA** — `Siap pasang iklan atau bangun aset digital?` → Order + WA

**Animasi Svelte**
| Section | Komponen | Perilaku |
|---|---|---|
| Hero | `HeroCommandCenter.svelte` | NumberTicker ROAS/leads; sparkline; toast notifikasi |
| Stats | `NumberTicker` | Count-up (jangan hardcode 0 seperti live sekarang) |
| Services | `TiltCard` | 3D tilt ringan desktop |
| Process | `ProcessSteps` | Active step progress |
| Pricing teaser | `PricingPeek` | Hover glow card |
| FAQ (opsional) | `FaqAccordion` | Spring height |
| Sticky | `StickyCta` | Slide-up mobile |

---

### D.2 `/jasa-digital-marketing` (Umbrella)

**SEO**
| Field | Copy |
|---|---|
| Title | `Jasa Digital Marketing Profesional \| Strategi Multi-Channel — Beriklan` |
| Meta | `Jasa digital marketing end-to-end: Meta Ads, Google Ads, TikTok, YouTube, kelola sosial media, website & landing page. Tim berpengalaman di Bandung.` |
| H1 | `Jasa Digital Marketing untuk Meningkatkan Kehadiran Online dan Konversi Bisnis Anda` |
| Primary KW | jasa digital marketing |

**Sections**
1. Hero — H1 di atas; sub dari live (“era digital… jangkauan bisnis”) dipoles  
2. **Service map 8 kartu** (live page structure): FB · IG · TikTok · Google · YouTube · SMM · Website · Konsultasi  
3. Value prop — monitoring & pengukuran campaign  
4. Process full-funnel  
5. Pricing index (tabel ringkas semua paket mulai)  
6. FAQ digital marketing  
7. CTA WA + Order  

**HeroDemo Svelte:** `OmnichannelMap.svelte` — animasi channel nodes (Meta/Google/TikTok/YT/Web) mengalir ke “Konversi WA/Telpon/Email”

**Copy kartu layanan (SEO short)**
- Iklan Facebook — Maksimalkan visibilitas & prospek dengan targeting presisi  
- Iklan Instagram — Eksposur merek + jangkauan pelanggan potensial  
- Iklan TikTok — Kampanye kreatif untuk audiens yang lebih luas  
- Google Ads — Raih peringkat berbayar di pencarian yang relevan  
- YouTube Ads — Perluas pasar lewat video yang tertarget  
- Social Media Management — Kredibilitas merek lewat konten konsisten  
- Website — Aset digital yang merepresentasikan brand  
- Konsultasi — Diskusi campaign via WhatsApp  

---

### D.3 `/jasa-iklan-facebook`

**SEO**
| Field | Copy |
|---|---|
| Title | `Jasa Iklan Facebook Ads Indonesia \| Paket dari Rp 1.750.000 — Beriklan` |
| Meta | `Jasa iklan Facebook profesional: targeting interest, remarketing, lead & chat WhatsApp. Paket Standart Rp 1.750.000 dan Business Rp 3.750.000 per 30 hari.` |
| H1 | `Jasa Iklan Facebook yang Menjangkau Audiens Tepat dan Mendorong Chat WhatsApp` |
| Primary KW | jasa iklan facebook, iklan facebook, facebook ads |

**Sections + copy inti**
1. **Hero** — Kenapa Facebook (live: 1,5M+ MAU Indonesia context) + CTA `Beriklan di Facebook`  
2. **6 fitur targeting (dari live):** Interaksi Audience · Interest (100+) · Remarketing List · Wilayah · Lead Database · Chat WhatsApp  
3. **How:** Brief → Setup Ads Manager → Creative → Launch 30 hari → Optimasi & ganti iklan  
4. **Pricing** — Standart / Business **persis live**  
5. **FAQ** contoh:  
   - Apakah harga termasuk budget iklan? *(jelaskan transparansi: sesuaikan kebijakan bisnis aktual di copy final)*  
   - Bisa ganti kreatif di tengah bulan? Ya, sesuai paket  
   - Minimal berapa lama? 30 hari tayang  
6. Related: IG Ads, Kelola IG, Landing Page  

**HeroDemo Svelte:** `MetaAdsPreview.svelte`  
- Mock feed FB + sidebar targeting (usia, kota, interest chips animasi)  
- Counter “Audience estimate” tween  
- CTA button shimmer  

**PricingCards Svelte:** highlight Business default; onSelect → WA message  
`Halo, saya minat paket Facebook Ads [Standart/Business] Rp …`

---

### D.4 `/jasa-iklan-instagram`

**SEO**
| Title | `Jasa Iklan Instagram Ads \| Paket Rp 1.750.000 & Rp 3.750.000 — Beriklan` |
| Meta | `Jasa iklan Instagram: Stories, Feed, Reels placement. 60% user temukan produk baru di IG. Paket 30 hari mulai Rp 1.750.000.` |
| H1 | `Jasa Iklan Instagram untuk Menemukan Pelanggan Baru lewat Konten Visual` |
| KW | jasa iklan instagram, iklan instagram |

**Copy hero (pro):**  
`Setiap hari ratusan juta orang menggunakan Instagram untuk mencari inspirasi dan produk. Kami membantu bisnis Anda menayangkan iklan yang tertarget — agar impresi berubah menjadi kunjungan profil, DM, atau chat WhatsApp.`

**Fitur:** mirror FB 6 cards (placement Instagram)  
**Pricing:** Standart 1,75jt · Business 3,75jt (live)

**HeroDemo Svelte:** `InstagramAdMock.svelte`  
- Phone frame: Feed → Story → Reels swap (auto every 3s, Haloka chat-step vibe)  
- Double-tap heart micro-anim  
- “60% discover products” stat callout  

---

### D.5 `/jasa-iklan-tiktok`

**SEO**
| Title | `Jasa Iklan TikTok Ads \| Mulai Rp 1.000.000 — Views & Lead` |
| Meta | `Pasang iklan TikTok: brand awareness, traffic, dan lead. Paket 7 hari Rp 1jt, 14 hari Rp 1,6jt, 30 hari Rp 3,75jt. Estimasi hingga 75.000 views.` |
| H1 | `Jasa Iklan TikTok untuk Menjangkau Audiens dengan Konten yang Menghibur dan Mengonversi` |
| KW | jasa iklan tiktok, pasang iklan tiktok, tiktok ads |

**Pricing live (3 tier)** — Basic / Standart / Business  
**Fitur live:** Iklan efektif · Interest · Remarketing · Wilayah · Lead · Chat WA  

**HeroDemo Svelte:** `TikTokForYouMock.svelte`  
- Vertical phone, swipe video cards  
- View counter NumberTicker  
- Sound-wave / caption kinetic (muted autoplay mock)  
- Badge “FYP style”  

**PricingCards:** 3 kolom; recommended = Business (lead)

---

### D.6 `/jasa-iklan-google`

**SEO**
| Title | `Jasa Iklan Google Ads & Search Ads \| Paket dari Rp 1.750.000` |
| Meta | `Jasa Google Ads: keyword research, search ads, remarketing. Basic Rp 1,75jt (budget harian 50rb), Standart Rp 3,75jt, Business Rp 6jt. Tampil saat prospek mencari Anda.` |
| H1 | `Jasa Iklan Google: Muncul di Halaman Pencarian Saat Pelanggan Siap Membeli` |
| KW | jasa iklan google, google ads, jasa google ads |

**Sections**
1. Hero — “Sudahkah di halaman 1 Google?” (live hook, dipoles)  
2. Fitur: Analisis Keywords · Kota Audience · Remarketing (+ sebut GDN di body sebagai retargeting)  
3. Pricing 3 tier **dengan budget harian** (fitur pembeda penting)  
4. FAQ keyword-rich: CPC, Quality Score edukasi singkat, beda Search vs Display  
5. Related: Landing Page promo bundle, Website, YouTube  

**HeroDemo Svelte:** `GoogleSerpMock.svelte`  
- Animasi SERP: query typewriter → ads block #1 highlight brand  
- Keyword chips fly-in  
- “Budget harian” mini gauge  

**Copy pricing labels (pro, angka fixed):**
- Basic — Cocok testing keyword & validasi demand  
- Standart — Skala traffic search harian  
- Business — Volume keyword & budget lebih agresif  

---

### D.7 `/jasa-iklan-youtube`

**SEO**
| Title | `Jasa Iklan YouTube Ads \| Bumper, Skippable & Non-Skippable` |
| Meta | `Jasa YouTube Ads: brand awareness & views. Paket dari Rp 1.250.000 (14 hari) hingga Business Rp 4.750.000. Format skippable, non-skippable, bumper.` |
| H1 | `Jasa Iklan YouTube untuk Membangun Brand Awareness lewat Video yang Tertarget` |
| KW | jasa iklan youtube, youtube ads |

**Sections live → redesign**
- Jenis audience YouTube (~1,9M global context — sampaikan hati-hati / gunakan “miliaran penonton global”)  
- Goals: Brand Awareness · Views & Traffic · Targeted Audience  
- Format edukasi: Skippable in-stream · Bumper · Non-skippable  
- Pricing 4 tier live  

**HeroDemo Svelte:** `YouTubePlayerMock.svelte`  
- Fake player: bumper 6s countdown skip button state  
- Progress bar + impression counter  
- Format tabs: Bumper | Skippable | Non-skippable (interactive)  

---

### D.8 `/jasa-kelola-instagram`

**SEO**
| Title | `Jasa Kelola Instagram Bisnis \| Konten, Story & Report — dari Rp 2.500.000` |
| Meta | `Jasa kelola Instagram: 15–20 desain feed, story, copywriting, posting & laporan bulanan. Basic Rp 2,5jt, Standart Rp 3,5jt (termasuk short video).` |
| H1 | `Jasa Kelola Instagram: Konten Konsisten, Interaksi Aktif, Brand yang Lebih Dipercaya` |
| KW | jasa kelola instagram, jasa admin instagram |

**Deliverable copy (pro)**
- Social Media Manager — strategi, posting, interaksi  
- Content Creator — design feed bertema bulanan  
- Video Creator — short & campaign video (paket Standart+)  

**Pricing live:** Basic 2,5jt · Standart 3,5jt · Business Call us  

**HeroDemo Svelte:** `IgGridPlanner.svelte`  
- 3×3 feed grid animasi slot-in  
- Calendar timeline “content plan”  
- Story ring progress  

---

### D.9 `/jasa-kelola-tiktok`

**SEO**
| Title | `Jasa Kelola TikTok & TikTok Shop \| Konten Video dari Rp 1.500.000` |
| Meta | `Jasa kelola TikTok: TikTok Shop Rp 1,5jt, 15 video Rp 3jt, 30 video Rp 4jt. Edukasi, entertainment, review produk + report bulanan.` |
| H1 | `Jasa Kelola TikTok untuk Brand Awareness dan Konten yang Siap Tayang Rutin` |
| KW | jasa kelola tiktok, jasa admin tiktok, tiktok shop |

**Pricing live 3 tier** — sebut mix: edukasi / entertainment viral / review produk  

**HeroDemo Svelte:** `TikTokContentStudio.svelte`  
- Timeline 15/30 konten checklist animasi  
- Music note riset  
- Toggle Shop vs Content plan  

---

### D.10 `/jasa-pembuatan-website`

**SEO**
| Title | `Jasa Pembuatan Website Profesional Murah \| Mulai Rp 999.000 / Tahun` |
| Meta | `Jasa pembuatan website: landing starter Rp 999.000/tahun, corporate 5 halaman, e-commerce terintegrasi payment & shipping. Design responsif & SEO basic.` |
| H1 | `Jasa Pembuatan Website Profesional — Murah, Responsif, dan Siap Dipromosikan` |
| KW | jasa pembuatan website, jasa buat website |

**Sections live → redesign**
1. Hero + dual CTA Layanan / Contact  
2. Why: Design terbaru & responsif · Kelola mudah · SEO friendly  
3. Upsell SEO “sudah punya website belum #1?”  
4. **4 langkah:** Website → Optimization → Campaign → Konversi (live)  
5. Custom fitur CTA  
6. **Pricing** Basic 999rb / Professional Call / Business Call  
7. Testimonials Arin, Ulfia, Witia (live)  

**HeroDemo Svelte:** `WebsiteBuilderPreview.svelte`  
- Browser chrome: sections assemble (hero, about, CTA)  
- Device toggle mobile/desktop  
- Lighthouse-ish score tick-up (visual only)  

---

### D.11 `/jasa-pembuatan-landing-page`

**SEO**
| Title | `Jasa Pembuatan Landing Page + Google Ads \| Rp 1.999.000` |
| Meta | `Paket landing page + 1 bulan Google Ads hanya Rp 1.999.000: 1 halaman konversi, copy, form, tracking, dan kampanye Google Ads.` |
| H1 | `Tingkatkan Konversi dengan Landing Page + Google Ads — Paket Rp 1.999.000` |
| KW | jasa pembuatan landing page, landing page google ads |

**Why package (live):**
- Desain LP menarik & responsif  
- Kampanye Google Ads efektif  
- Teknologi terkini  

**Paket Promo deliverables (live):**  
1 LP · 1 bulan Google Ads · copy · form · integrasi · pelacakan  

**HeroDemo Svelte:** `LandingPlusAds.svelte`  
- Split view: LP mock kiri + Google ad preview kanan  
- Arrow animasi “klik iklan → form submit”  
- Price badge NumberTicker ke 1.999.000  

**PricingCards:** single featured package (bukan 3 tier) + CTA Order WA  

---

### D.12 `/order` (Inquiry)

**SEO**
| Title | `Inquiry & Order Jasa Digital Marketing — Beriklan` |
| Meta | `Kirim kebutuhan campaign Anda. Hubungi tim Beriklan: WhatsApp 0811-919-328, email info@beriklan.co.id, atau kunjungi kantor Bandung.` |
| H1 | `Pasang Iklan atau Mulai Proyek Digital — Kirim Inquiry Anda` |

**Sections**
1. Hero short  
2. **Contact cards (live):**  
   - Phone/WA: 081 1919 328  
   - Email: info@beriklan.co.id  
   - Address: Jl. Arcamanik Endah No.76, Sukamiskin, Arcamanik, Bandung 40293  
3. **Multi-step form Svelte** (improve Haloka-style interactive, bukan form WP kosong):  
   - Step 1: Jenis layanan (chips: FB/IG/TikTok/Google/YT/Kelola/Web/LP)  
   - Step 2: Budget / paket interest  
   - Step 3: Data bisnis + WA  
   - Success → ConfettiBurst + redirect WA prefilled  
4. Map embed optional  
5. FAQ singkat  

**Svelte:** `OrderWizard.svelte` — multi-step seperti flow Haloka pricing → register, tapi ke WA/email.

---

### D.13 `/blog`

**SEO:** `Blog Digital Marketing — Tips Iklan, Google Ads, Meta & TikTok | Beriklan`  
**Sections:** Hero · Filter kategori · Featured · Grid · Pagination  
**Svelte:** `BlogFilter.svelte` client:idle (chip filter only)

---

### D.14 Halaman baru (disarankan, bukan live menu utama)

| URL | Tujuan | Priority |
|---|---|---|
| `/tentang` | Trust, alamat, pengalaman | P1 |
| `/kontak` | Mirror order contacts + form | P1 |
| `/privacy` `/terms` | Legal | P1 sebelum launch |

Local SEO pages (ratusan) → fase terpisah; money pages di atas dulu.

### D.15 `/paket` (Pricing Index — Konversi Mid-Funnel)

**Tujuan:** Aggregator semua paket untuk visitor yang sudah kompare 2-3 layanan. Decision-stage.

**SEO**

| Field | Copy |
|---|---|
| Title | `Daftar Paket Digital Marketing Lengkap \| Beriklan` |
| Meta | `Lihat semua paket jasa digital marketing Beriklan: Facebook Ads, Instagram, TikTok, Google, YouTube, kelola sosial media, website & landing page. Pilih paket sesuai budget dan goals bisnis.` |
| H1 | `Paket Digital Marketing untuk Setiap Tahap Pertumbuhan Bisnis Anda` |
| Primary KW | paket digital marketing, harga iklan |

**Sections (custom — bukan template service)**

1. **Hero ringkas** — H1 + sub (1 paragraf) + trust badges + CTA `Konsultasi Gratis`
2. **Tab / sticky filter** — `Paid Ads · Social Management · Website & LP · Bundling` (Svelte filter, default `Paid Ads`)
3. **Pricing matrix lengkap** — setiap service collapsed card (accordion) dengan ringkasan tier + `Lihat detail →` ke halaman service. Hemat scroll, hindari 10× pricing cards.
4. **Bundling rekomendasi** (Svelte Bento):
   - **Starter Brand** — LP + Google Ads (Rp 1,999,000)
   - **Lead Gen Meta** — FB Ads + IG Ads (Rp 3,500,000)
   - **Omnichannel Scale** — Meta + Google + TikTok Ads (custom quote)
5. **Comparison table** — `DIY · Freelancer · Beriklan` (5 baris: support, reporting, ad spend min, fee struktur, dedicated AM)
6. **FAQ pricing** (8 Q) — keyword-rich: beda ad spend vs management fee, bisa upgrade paket, refund policy, ad spend siapa yang bayar
7. **Mid CTA** — `Belum yakin? Audit 15 menit gratis via WhatsApp`
8. **Related blog posts** — 3 post pricing-related

**HeroDemo Svelte:** `PricingMatrixInteractive.svelte` — bukan HeroDemo demo produk; ini filter matrix island (tab + accordion).

**Schema:** `Service` + `OfferCatalog` (multiple `Offer` di-nest) + `FAQPage` + `BreadcrumbList`

**Acceptance:**
- [ ] Tab filter visible immediately, default Paid Ads expanded
- [ ] Mobile: tab horizontal scroll, accordion collapse default
- [ ] CTA tiap tier → WA prefill sesuai paket
- [ ] Bundle cards highlight 1 (Starter Brand promo)
- [ ] Internal link ke tiap service page dari accordion header

---

### D.16 `/studi-kasus` + `/studi-kasus/[slug]`

**Tujuan:** Social proof tertinggi. Anonymized case study (izin klien) — fokus proses + hasil numerik.

**SEO list page**

| Field | Copy |
|---|---|
| Title | `Studi Kasus Digital Marketing \| Hasil Klien Beriklan` |
| Meta | `Pelajari strategi dan hasil kampanye digital marketing klien Beriklan: ROAS 4.2×, CPL -38%, follower growth 240%. Studi kasus industri F&B, fashion, edukasi, properti.` |
| H1 | `Studi Kasus Klien Beriklan — Strategi yang Menghasilkan` |
| Primary KW | studi kasus digital marketing, hasil iklan |

**Sections list page**

1. **Hero** — H1 + sub + filter industri chips (`F&B`, `Fashion`, `Edukasi`, `Properti`, `Jasa`, `Kecantikan`)
2. **Highlight case (1 featured)** — full bleed card: klien nama+industri, challenge, hasil headline, `Baca studi kasus →`
3. **Grid 6-9 case** — card: industri, judul singkat (campaign), headline metric (contoh `ROAS 6.2× dalam 60 hari`), CTA
4. **Mid CTA** — `Mau hasil seperti klien kami? Konsultasi gratis`
5. **FAQ singkat** (3 Q) — “Apakah nama klien asli?”, “Berapa minimal budget untuk dapat hasil serupa?”

**SEO single page** (`/studi-kasus/{slug}`)

| Field | Copy |
|---|---|
| Title | `{Hasil Utama} — Studi Kasus {Industri} {Klien} \| Beriklan` |
| H1 | `{Challenge headline} — Bagaimana {Klien} {Hasil}` |
| Schema | `Article` + `BreadcrumbList` (tidak `CaseStudy` karena belum schema.org resmi) |

**Sections single page**

1. **Hero** — Industri badge + judul H1 + 3 hero stats (contoh: ROAS 6.2×, CPL turun 42%, Scale 3× dalam 60 hari)
2. **Klien ringkas** (mini-card): nama/alias, industri, lokasi, durasi kerja sama, budget range
3. **Challenge** — Pain spesifik, 2-3 paragraf, dengan angka baseline
4. **Strategy** — 3-5 langkah apa yang kami kerjakan (numbered, dengan visual)
5. **Eksekusi** — Creative sample (mock image), audience setup, A/B test hasil, optimasi
6. **Hasil** — Dashboard mock (Svelte `CaseStudyDashboard.svelte` — NumberTicker + chart SVG), breakdown per bulan
7. **Testimoni klien** — 1 quote ringkas + nama + jabatan
8. **Related cases** — 3 dari industri sama atau layanan sama
9. **Final CTA** — `Mulai campaign seperti {Klien}`

**Svelte component:** `CaseStudyDashboard.svelte` — mini dashboard animasi dengan 3-4 metric ticker + bar chart.

**Data source:** `src/content/case-studies/*.mdx` (Content Collections). Frontmatter:

```yaml
---
slug: 'fb-ads-roas-6x-fashion-brand'
client: 'Klien A (anonim)'
industry: 'fashion'
service: 'jasa-iklan-facebook'
duration: '60 hari'
budgetRange: 'Rp 5-10jt/bln (ad spend)'
heroStats:
  - { label: 'ROAS', value: '6.2×' }
  - { label: 'CPL turun', value: '-42%' }
  - { label: 'Scale', value: '3× dalam 60 hari' }
challenge: 'ROAS stagnan 1.8× selama 4 bulan...'
strategy: ['Riset ulang audience...', 'Refresh creative...']
results: [...]
testimonial: { quote: '...', name: 'Marketing Lead Klien A' }
publishedAt: 2026-06-15
noindex: false
---
```

**Acceptance:**
- [ ] Min 3 case studies sebelum launch (F&B, Fashion, Jasa)
- [ ] Semua angka harus bisa di-backup internal; bila ragu, gunakan range
- [ ] Tidak sebut nama klien tanpa izin eksplisit; default alias (Klien A/B/C)
- [ ] Mobile: hero stat stack vertical, dashboard scroll horizontal

---

### D.17 `/tentang` (About / Trust)

**Tujuan:** Establish credibility. Senior Performance Marketing Partner persona. Bukan brochure kosong.

**SEO**

| Field | Copy |
|---|---|
| Title | `Tentang Beriklan — Digital Marketing Agency Bandung Sejak 2018` |
| Meta | `Beriklan adalah digital marketing agency di Bandung. 8+ tahun mengelola iklan Meta, Google, TikTok, YouTube untuk 60+ klien. Tim bersertifikat Meta & Google Partner.` |
| H1 | `Tentang Beriklan — Tim di Balik Kampanye yang Menghasilkan` |
| Primary KW | tentang beriklan, digital agency bandung |

**Sections**

1. **Hero ringkas** — H1 + 1 paragraf (visi) + stats band (8 tahun, 60+ klien, 50+ brand, Rp 50M+ ad spend managed)
2. **Visi & misi** (2-column) — bukan generic; spesifik ke measurable growth
3. **Cerita Beriklan** (timeline) — 2018 mulai, 2020 ekspansi Meta, 2022 Google Partner, 2024 TikTok, 2026 sekarang. Horizontal timeline Svelte (desktop) / vertical accordion (mobile)
4. **Tim & expertise** — 3-4 foto anggota tim (consent), role, certification (Meta Blueprint, Google Ads Cert, TikTok Academy). Bisa pakai inisial + role jika tidak ada foto.
5. **Nilai kerja** — 5 prinsip (Data-driven, Transparent reporting, No hidden fee, Senior handle all, Long-term partnership) — bukan bullet kosong; setiap nilai 1 paragraf + contoh konkret.
6. **Partner & sertifikasi** — Logo Meta Business Partner, Google Partner, TikTok Academy, dll. Marquee strip.
7. **Klien highlight** — 12-20 logo klien (anonim OK) marquee.
8. **Final CTA** — `Bekerja sama dengan tim yang sama yang mengelola campaign Anda. Konsultasi gratis.`

**Svelte:** `Timeline.svelte` — horizontal scroll (desktop) + vertical accordion (mobile). Reduced-motion fallback.

**Schema:** `Organization` + `AboutPage` + `BreadcrumbList`

**Acceptance:**
- [ ] Stats band angka aktual (8 th, 60+ klien) — verify internal sebelum tulis
- [ ] Tim foto consent check; gunakan inisial jika belum
- [ ] Timeline: setiap milestone 1 paragraf, tidak generic
- [ ] Mobile: timeline jadi accordion

---

### D.18 `/kontak` (Contact Mirror)

**Tujuan:** Mirror `/order` tapi lebih simple — untuk visitor yang sudah yakin ingin kontak langsung (tidak perlu multi-step form).

**SEO**

| Field | Copy |
|---|---|
| Title | `Kontak Beriklan — WhatsApp, Email, Kantor Bandung` |
| Meta | `Hubungi tim Beriklan: WhatsApp 0811-919-328, email info@beriklan.co.id, atau kunjungi kantor di Jl. Arcamanik Endah No.76, Bandung. Respon dalam 1 jam kerja.` |
| H1 | `Kontak Beriklan — Kami Responsif, Tidak Ribet` |
| Primary KW | kontak beriklan, alamat beriklan bandung |

**Sections**

1. **Hero ringkas** — H1 + respon time badge (`Respon <1 jam kerja`) + micro-proof (60+ klien aktif, 8 tahun)
2. **Contact cards 3** (klik-to-action):
   - **WhatsApp** — `0811-919-328` + CTA `Chat Sekarang` (icon pulse)
   - **Email** — `info@beriklan.co.id` + CTA `Kirim Email`
   - **Kantor** — Alamat lengkap + CTA `Buka Maps`
3. **Simple form** (BUKAN multi-step wizard — single-page, 4 field):
   - Nama, Email, WhatsApp, Pesan
   - Submit → Astro Action + WA prefill fallback
   - Honeypot + Turnstile
4. **Map embed** — Google Maps iframe kantor Bandung (lazy load)
5. **Jam operasional** — `Senin-Jumat 09.00-18.00 WIB · Sabtu 10.00-14.00 · Minggu off`
6. **FAQ singkat** (3 Q) — respon time, bisa ketemu offline, luar Bandung bisa remote

**Schema:** `ContactPage` + `LocalBusiness` (dengan `openingHoursSpecification`)

**Acceptance:**
- [ ] Map iframe `loading="lazy"`
- [ ] Form ≤ 4 field visible, validasi inline
- [ ] WA card primary visual (lebih besar dari email/kantor)
- [ ] Mobile: stack cards, map full-width di bawah

---

### D.19 `/audit` (Free 7Q Audit Tool — Lead Magnet)

**Tujuan:** Lead magnet utama COPY-BIBLE §11. User isi 7 pertanyaan → dapat skor + tips instan + CTA konsultasi.

**SEO**

| Field | Copy |
|---|---|
| Title | `Audit Iklan Digital Marketing Gratis 15 Menit \| Beriklan` |
| Meta | `Dapatkan audit campaign digital marketing gratis: cek kualitas Meta Ads, Google Ads, TikTok, SEO, dan tracking. Skor + rekomendasi actionable dalam 15 menit.` |
| H1 | `Audit Kampanye Digital Marketing Anda — Gratis, 15 Menit` |
| Primary KW | audit digital marketing gratis, cek iklan |

**Sections — single page wizard**

1. **Hero** — H1 + sub (`Tanpa login. Tanpa data pribadi sensitif. Dapat rekomendasi instan.`) + trust badges
2. **Wizard 7Q Svelte** (`AuditWizard.svelte`) — single page stepper, 1 Q per step:
   1. Platform iklan utama? (chips: FB / IG / TikTok / Google / YouTube / Multiple)
   2. Budget ad spend per bulan? (range: <Rp 1jt / 1-3jt / 3-10jt / >10jt)
   3. Berapa lama iklan sudah jalan? (<1 bln / 1-3 bln / 3-6 bln / >6 bln)
   4. Tujuan utama? (Awareness / Traffic / Leads / Penjualan langsung)
   5. Sudah punya Pixel/Analytics? (Ya, yakin / Ada tapi belum yakin / Belum)
   6. ROAS/CPA terakhir yang Anda tahu? (free input numeric)
   7. Apa tantangan terbesar? (textarea, max 300 char)
3. **Submit → Result page (same route)** — skor 0-100 per kategori (4 kategori: Targeting, Creative, Tracking, Optimasi) + recommendation list (Svelte `AuditResult.svelte`)
4. **CTA lead capture setelah hasil** — `Mau kami audit manual gratis? Kirim WhatsApp dengan hasil ini`
5. **FAQ audit** (4 Q) — “Apakah data saya aman?”, “Berapa lama?”, “Apa bedanya dengan konsultasi?”

**Svelte:**
- `AuditWizard.svelte` — stepper dengan progress bar, validasi per step, animasi slide horizontal
- `AuditResult.svelte` — score breakdown radar chart SVG + recommendation list + WA prefill

**Tracking events:**
- `audit_start` (timestamp)
- `audit_step_complete` (step number)
- `audit_submit` (final, with answers hash)
- `audit_lead_capture` (WA click from result)

**Acceptance:**
- [ ] Wizard skip-safe (jawaban kosong OK di Q terakhir)
- [ ] Hasil deterministik (same input = same output) — score logic di `lib/audit-scoring.ts`
- [ ] Mobile: full-screen step, swipe next/back
- [ ] Reduced motion: skip slide, langsung replace

---

### D.20 `/privacy`, `/terms`, `/404`

**`/privacy`**
- Standar UU PDP Indonesia + cookie policy
- Section: data yang dikumpulkan, tujuan, retensi, hak user, kontak DP
- Schema: `WebPage`
- Generated dari MDX dengan placeholder; finalisasi oleh legal sebelum launch

**`/terms`**
- Syarat layanan: scope kerja, pembayaran, revisi, termination, liability
- Schema: `WebPage`
- Generated dari MDX dengan placeholder

**`/404`**
- Branded illustration (SVG line art) + headline `Halaman tidak ditemukan`
- Search bar (suggest ke blog/paket)
- 4 link konversi: Beranda · Paket · Blog · Order
- Tone: ringan, tidak generic

**Acceptance:**
- [ ] Privacy + Terms **wajib** sebelum launch production
- [ ] 404 dengan brand voice, bukan Apache default

---

## E. COPYWRITING RULES (SEO + marketing pro)

1. **Primary keyword di:** title, H1, 1× paragraf pertama, 1× subheading, meta description.  
2. **Hindari keyword stuffing** seperti live (ulang “jasa X” 10×) — max natural 1–2% density.  
3. **Bahasa:** Anda / kami; kalimat ≤ 25 kata rata-rata; 1 ide per paragraf.  
4. **Proof:** jangkauan/views = “estimasi” (sudah ada di live — pertahankan disclaimer `*estimasi`).  
5. **CTA:** action + benefit: `Diskusikan paket Facebook Ads Standart` bukan “Klik di sini”.  
6. **Internal link:** tiap service → 2–3 related + umbrella digital marketing + order.  
7. **Pricing mention di meta** untuk money pages (sudah terbukti CTR) — angka = live.  
8. **Jangan** janji ROAS pasti; gunakan “membantu meningkatkan peluang konversi / jangkauan”.

### E.1 CTA library (WA prefill templates)

```
Halo Beriklan, saya ingin konsultasi *{LAYANAN}* paket *{PAKET}* (*{HARGA}*).
Bisnis: {nama}
Kota: {kota}
```

---

## F. ANIMASI SVELTE — MATRIX LENGKAP

| Komponen file | Dipakai di | Interaksi |
|---|---|---|
| `Navbar.svelte` | Global | Scroll shrink, mega-menu, mobile spring |
| `StickyCta.svelte` | Global | Show after scroll; dynamic price label |
| `WhatsAppFloat.svelte` | Global | Pulse; open chat |
| `HeroCommandCenter.svelte` | Home | Multi-channel dashboard |
| `OmnichannelMap.svelte` | Digital marketing | Node flow |
| `MetaAdsPreview.svelte` | FB | Targeting UI mock |
| `InstagramAdMock.svelte` | IG | Format cycle |
| `TikTokForYouMock.svelte` | TikTok Ads | Vertical swipe + views |
| `GoogleSerpMock.svelte` | Google | SERP typewriter |
| `YouTubePlayerMock.svelte` | YouTube | Format tabs + player |
| `IgGridPlanner.svelte` | Kelola IG | Feed grid plan |
| `TikTokContentStudio.svelte` | Kelola TikTok | Content batch |
| `WebsiteBuilderPreview.svelte` | Website | Assemble sections |
| `LandingPlusAds.svelte` | LP | Split LP + Ads |
| `PricingCards.svelte` | All services w/ price | Select tier, magnetic CTA |
| `ProcessSteps.svelte` | Most pages | Step progress |
| `FaqAccordion.svelte` | Most pages | Expand spring |
| `TestimonialSlider.svelte` | Web, LP, home | Autoplay pause on hover |
| `NumberTicker.svelte` | Stats / prices | tweened |
| `TiltCard.svelte` | Feature grids | Desktop tilt |
| `OrderWizard.svelte` | Order | Multi-step + confetti |
| `TextReveal.svelte` | Heroes | Word/line reveal optional |
| `ScrollReveal.svelte` | Sections | IO + fly/fade |

**Haloka parity checklist**
- [x] Section = interactive island where it educates  
- [x] Sticky CTA  
- [x] Pricing interactive  
- [x] FAQ accordion  
- [x] Hero “product demo” not stock photo only  
- [x] `client:visible` below fold  
- [ ] **Not** copy-paste green WhatsApp brand — use Beriklan blue/ink system  

---

## G. DATA FILE IMPLEMENTASI

```ts
// src/lib/data/pricing.ts  — SOURCE OF TRUTH = live site
export const pricing = {
  facebookAds: {
    currency: 'IDR',
    periodLabel: '30 hari',
    tiers: [
      {
        id: 'standart',
        name: 'Standart',
        price: 1_750_000,
        features: [
          '30 hari tayang',
          'Estimasi jangkauan 3.000–9.000 audience/hari',
          'Semua penempatan Facebook',
          '2 iklan (10 foto atau 1 video)',
          'Iklan dapat diganti',
        ],
      },
      {
        id: 'business',
        name: 'Business',
        price: 3_750_000,
        features: [
          '30 hari tayang',
          'Estimasi jangkauan 4.000–15.000 audience/hari',
          'Semua penempatan Facebook',
          '3 iklan (10 foto atau 1 video)',
          'Iklan dapat diganti',
        ],
        highlight: true,
      },
    ],
  },
  // ... instagramAds, tiktokAds, googleAds, youtubeAds,
  // kelolaInstagram, kelolaTiktok, website, landingPage
} as const;
```

Sama untuk `services.ts` (slug, menu group, heroDemo component name, SEO fields).

---

## H. PRIORITAS BUILD PER HALAMAN

| Priority | Page | Alasan |
|---|---|---|
| P0 | Home + Navbar/Footer/Sticky | First impression + nav |
| P0 | Facebook Ads + Google Ads | Traffic/money keywords |
| P0 | Order | Conversion |
| P1 | Instagram, TikTok Ads | Paket lengkap |
| P1 | YouTube, Landing Page promo | Pricing jelas |
| P1 | Website | Paket 999rb entry |
| P1 | Kelola IG + Kelola TikTok | Organic revenue |
| P1 | Digital Marketing umbrella | Pillar SEO |
| P2 | Blog index template | Content hub |
| P2 | Tentang / Kontak | Trust |

---

## I. ACCEPTANCE PER PAGE

Untuk **setiap** money page:
- [ ] Title/meta/H1 unik + keyword utama  
- [ ] Pricing **angka & fitur = live**  
- [ ] Minimal 1 HeroDemo Svelte kontekstual  
- [ ] PricingCards Svelte + WA prefill paket  
- [ ] FAQ ≥ 4 (schema FAQPage)  
- [ ] Internal links ≥ 3  
- [ ] Mobile sticky CTA  
- [ ] Lighthouse mobile ≥ 90  
- [ ] Tidak ada counter “0” palsu seperti home live  

---

## J. RINGKASAN KOREKSI DARI PLAN SEBELUMNYA

| Plan lama (kurang) | Koreksi di dokumen ini |
|---|---|
| Pricing invent (2,5jt / 5jt / 10jt) | **Pakai harga live** (1,75jt Meta, 1jt TikTok, 999rb web, 1,999jt LP, dll.) |
| Belum audit menu live | **Full inventory footer + services + order** |
| Copy generik / Haloka tone | **SEO title/meta/H1 + marketing pro per page** |
| Animasi generic | **HeroDemo unik per layanan** (SERP, FYP, feed IG, YT player, dll.) |
| Satu template flat | **11-section template + matrix komponen Svelte** |

---

*Dokumen ini wajib diikuti saat implementasi page-by-page. Update `pricing.ts` hanya jika bisnis mengubah harga di operasional — sinkronkan kembali ke web.*

---

## K. MOBILE HIGH-CONVERT (wajib di semua page)

> Mayoritas traffic Indonesia = mobile. Sticky + form + CTA harus **dirancang mobile-first**, bukan desktop yang di-compress.

### K.1 Prinsip

| Prinsip | Implementasi |
|---|---|
| Thumb zone | Primary CTA di bottom sticky; secondary di header minimal |
| One job per screen | Hero mobile: H1 + 1 sub + 2 CTA max; demo collapsible / di bawah fold |
| Friction low | WA 1-tap; form max 1 field per step di mobile |
| Trust above CTA | Micro-proof (respon <1 jam, paket mulai Rp X) di sticky bar |
| Safe area | `pb-safe` + `viewport-fit=cover` (iPhone home indicator) |
| No hover-only | Semua interaksi tap; mega menu = bottom sheet mobile |
| Tap target | min 44×44px; gap antar CTA ≥ 8px |
| Speed | HeroDemo `client:visible`; reduce motion on low-end |

### K.2 Chrome mobile

1. **Top nav compact** (h-14): logo + hamburger + WA icon  
2. **Mobile menu** = full-screen sheet (Svelte): Layanan grouped + Inquiry big CTA  
3. **Sticky bottom bar** (setelah 20% scroll, hide saat scroll down cepat optional):  
   - Left: harga mulai / label page (`Mulai Rp 1.750.000`)  
   - Primary: `Konsultasi` → `/order` atau WA  
   - Green: WA icon always  
4. **WhatsApp float** desktop only (md+); mobile pakai sticky agar tidak dobel  
5. **Padding bottom content** `pb-24 md:pb-0` supaya tidak ketutup sticky  

### K.3 Hero mobile layout

```
[eyebrow]
[H1 2-3 baris, text-3xl–4xl]
[sub 2 baris max]
[Primary CTA full-width]
[Secondary text link]
[trust micro row]
[HeroDemo — height capped 280–320px, scale down]
```

### K.4 Pricing mobile

- Stack vertical cards (bukan 3-col)  
- Recommended tier expanded default  
- CTA full-width per card  
- Sticky bar sync ke selected tier (Svelte state via custom event / store)

### K.5 Form order mobile

- Stepper progress dots  
- Large inputs (h-12)  
- Keyboard `type=tel` untuk WA  
- Submit = buka WA prefilled (primary) + optional email backup  

### K.6 Acceptance mobile convert

- [ ] Lighthouse mobile Perf ≥ 90  
- [ ] Sticky CTA visible < 2 scroll gestures  
- [ ] WA reachable in 1 tap from any depth  
- [ ] No horizontal scroll  
- [ ] Form completable one-handed  

---

## L. BLOG SINGLE PAGE — SANITY CMS

### L.1 Keputusan

| Layer | Tool |
|---|---|
| Blog list + single | **Sanity** (project `beriklan`, id `2pdculh3`) |
| Service/pricing pages | Hardcode / MDX dulu (stabil SEO) |
| Studio | `sanity` folder atau sanity.io hosted |

### L.2 Schema `post`

```ts
{
  name: 'post',
  type: 'document',
  fields: [
    { name: 'title', type: 'string' },
    { name: 'slug', type: 'slug', options: { source: 'title' } },
    { name: 'excerpt', type: 'text' },
    { name: 'mainImage', type: 'image', options: { hotspot: true } },
    { name: 'body', type: 'array', of: [{ type: 'block' }, { type: 'image' }] },
    { name: 'categories', type: 'array', of: [{ type: 'string' }] },
    { name: 'publishedAt', type: 'datetime' },
    { name: 'updatedAt', type: 'datetime' },
    { name: 'seoTitle', type: 'string' },
    { name: 'seoDescription', type: 'text' },
    { name: 'noindex', type: 'boolean' },
  ]
}
```

### L.3 Routes

| Route | Data |
|---|---|
| `/blog` | `*[_type=="post"]\|order(publishedAt desc)` |
| `/blog/[slug]` | `*[_type=="post" && slug.current==$slug][0]` |
| `/blog/kategori/[cat]` | filter categories |

### L.4 Blog single layout (high-convert)

1. Breadcrumb  
2. Title + date + category  
3. Hero image  
4. **Portable Text** body (`@portabletext/to-html` atau custom)  
5. **Inline CTA mid-article** (setelah ~40% scroll / after 2nd H2): Konsultasi layanan  
6. Related posts (3) dari Sanity  
7. Sticky mobile CTA tetap  
8. JSON-LD `BlogPosting`  

### L.5 Env

```
PUBLIC_SANITY_PROJECT_ID=2pdculh3
PUBLIC_SANITY_DATASET=production
SANITY_API_READ_TOKEN=   # server/build only, optional if dataset public
```

### L.6 Build

- SSG: fetch Sanity at build (`getStaticPaths`)  
- Revalidate: webhook Sanity → CF Pages rebuild (fase 2)  
- Fallback empty state jika API fail  

---

## N. JSON-LD SCHEMA SNIPPETS (per page type)

Semua schema dibuild via helper di `src/lib/seo.ts` agar konsisten. Letakkan di `<head>` per page via `<JsonLd>` component.

### N.1 Homepage

```ts
{
  '@context': 'https://schema.org',
  '@graph': [
    buildOrganization(),
    buildWebSite({
      name: 'Beriklan',
      url: SITE_URL,
      potentialAction: {
        '@type': 'SearchAction',
        target: `${SITE_URL}/blog?q={search_term}`,
        'query-input': 'required name=search_term',
      },
    }),
    buildFAQPage(FAQ_HOME),
  ],
}
```

### N.2 Service Page (contoh FB Ads)

```ts
{
  '@context': 'https://schema.org',
  '@graph': [
    buildOrganization(),
    {
      '@type': 'Service',
      serviceType: 'Jasa Iklan Facebook',
      provider: { '@id': `${SITE_URL}#organization` },
      areaServed: { '@type': 'Country', name: 'Indonesia' },
      description: SERVICE_FACEBOOK.description,
      offers: SERVICE_FACEBOOK.pricingTiers.map(tier => ({
        '@type': 'Offer',
        name: tier.name,
        price: tier.price,
        priceCurrency: 'IDR',
        description: tier.features.join('; '),
        availability: 'https://schema.org/InStock',
        url: `${SITE_URL}/jasa-iklan-facebook#${tier.name.toLowerCase()}`,
      })),
    },
    buildFAQPage(SERVICE_FACEBOOK.faqs),
    buildBreadcrumb([
      { name: 'Beranda', url: SITE_URL },
      { name: 'Layanan', url: `${SITE_URL}/jasa-digital-marketing` },
      { name: 'Facebook Ads', url: `${SITE_URL}/jasa-iklan-facebook` },
    ]),
  ],
}
```

### N.3 Blog Post

```ts
{
  '@context': 'https://schema.org',
  '@graph': [
    buildOrganization(),
    {
      '@type': 'BlogPosting',
      headline: post.title,
      description: post.excerpt,
      image: post.mainImage,
      datePublished: post.publishedAt,
      dateModified: post.updatedAt ?? post.publishedAt,
      author: { '@type': 'Organization', name: 'Beriklan' },
      publisher: {
        '@type': 'Organization',
        name: 'Beriklan',
        logo: { '@type': 'ImageObject', url: `${SITE_URL}/logoweb.webp` },
      },
      mainEntityOfPage: `${SITE_URL}/blog/${post.slug}`,
    },
    buildBreadcrumb([
      { name: 'Beranda', url: SITE_URL },
      { name: 'Blog', url: `${SITE_URL}/blog` },
      { name: post.title, url: `${SITE_URL}/blog/${post.slug}` },
    ]),
  ],
}
```

### N.4 Case Study Single Page

```ts
{
  '@context': 'https://schema.org',
  '@graph': [
    buildOrganization(),
    {
      '@type': 'Article',
      headline: case.title,
      description: case.summary,
      image: case.ogImage,
      datePublished: case.publishedAt,
      author: { '@type': 'Organization', name: 'Beriklan' },
      about: { '@type': 'Service', name: case.service },
    },
    buildBreadcrumb([
      { name: 'Beranda', url: SITE_URL },
      { name: 'Studi Kasus', url: `${SITE_URL}/studi-kasus` },
      { name: case.title, url: `${SITE_URL}/studi-kasus/${case.slug}` },
    ]),
  ],
}
```

### N.5 Local Business (Kontak page)

```ts
{
  '@context': 'https://schema.org',
  '@type': 'LocalBusiness',
  '@id': `${SITE_URL}#business`,
  name: 'Beriklan Digital Agency',
  image: `${SITE_URL}/logoweb.webp`,
  url: SITE_URL,
  telephone: '+62-811-919-328',
  email: 'info@beriklan.co.id',
  priceRange: 'Rp',
  address: {
    '@type': 'PostalAddress',
    streetAddress: 'Jl. Arcamanik Endah No.76',
    addressLocality: 'Bandung',
    addressRegion: 'Jawa Barat',
    postalCode: '40293',
    addressCountry: 'ID',
  },
  openingHoursSpecification: [
    { '@type': 'OpeningHoursSpecification', dayOfWeek: ['Monday','Tuesday','Wednesday','Thursday','Friday'], opens: '09:00', closes: '18:00' },
    { '@type': 'OpeningHoursSpecification', dayOfWeek: 'Saturday', opens: '10:00', closes: '14:00' },
  ],
  sameAs: [
    'https://www.instagram.com/beriklan.co.id',
    'https://www.facebook.com/beriklan.co.id',
    'https://www.tiktok.com/@beriklan.co.id',
  ],
}
```

**Acceptance:** Validasi 5 sample page via [Google Rich Results Test](https://search.google.com/test/rich-results) sebelum launch.

---

## O. ANALYTICS EVENTS SPEC

Semua event di-fire via `lib/analytics.ts` (wrapper GA4 + PostHog optional). Naming convention: `{category}_{action}` snake_case.

### O.1 Event catalog

| Event | Lokasi | Properties | Kapan |
|---|---|---|---|
| `cta_click` | Semua page | `location` (section id), `label` (text), `destination` (wa/order/blog) | Klik CTA primary/secondary |
| `wa_click` | Global | `location`, `source` (sticky/float/inline) | Klik WA link |
| `form_start` | `/order`, `/kontak`, `/audit` | `form_name`, `step` (1) | First input focus |
| `form_step` | `/order`, `/audit` | `form_name`, `step`, `direction` (next/back) | Step transition |
| `form_submit` | Semua form | `form_name`, `value` (paket/layanan if any) | Submit success |
| `form_abandon` | `/order`, `/audit` | `form_name`, `step`, `duration_sec` | User leave page mid-form (beforeunload) |
| `pricing_tier_select` | Service pages, `/paket` | `service_slug`, `tier_name`, `tier_price` | Click tier CTA |
| `service_card_click` | Home, `/jasa-digital-marketing` | `from_page`, `target_service` | Click service card |
| `faq_open` | Semua page | `page`, `question_index` | Expand FAQ |
| `audit_submit` | `/audit` | `answers_hash`, `score` (jika computed) | Submit audit |
| `audit_lead_capture` | `/audit` result | `score_band` (low/mid/high) | WA click from result |
| `blog_post_read` | Blog single | `slug`, `scroll_depth_pct`, `duration_sec` | Reach 80% scroll + leave |
| `case_study_click` | `/studi-kasus` | `case_slug`, `from_featured` (bool) | Click case card |
| `phone_click` | `/kontak` | `source` (card/sticky) | Click phone number |
| `email_click` | `/kontak` | `source` | Click email |
| `map_open` | `/kontak` | `source` | Click map |
| `theme_toggle` | Global | `from`, `to` | Toggle dark mode |

### O.2 Conversion funnel (pinned events)

```
home → service_view → pricing_tier_select → form_start → form_submit → wa_click
       ↓                ↓                       ↓
       faq_open         case_study_click        form_abandon
```

**Acceptance:** Dashboard GA4 conversion path di-set up Phase 6 sebelum launch; checklist event firing di PR review.

---

## P. ASSET & IMAGE PLAN

### P.1 Brand assets (sekarang tersedia)

| Asset | Lokasi | Status |
|---|---|---|
| `logoweb.webp` | `public/logoweb.webp` | ✅ Ada |
| Favicon SVG | `public/favicon.svg` | Perlu dibuat (Astro default ok) |
| OG default (1200×630) | `public/og-default.png` | ❌ Perlu buat (Satori endpoint) |

### P.2 Hero mock per page (perlu dibuat)

Mock adalah **SVG/canvas component**, bukan foto. Dibuat sebagai Svelte component.

| Page | Mock component | Style |
|---|---|---|
| `/` | `HeroScene.svelte` (Ads Command Center) | Dashboard SVG, sudah konsep |
| `/jasa-digital-marketing` | `OmnichannelMap.svelte` | Node graph animasi |
| `/jasa-iklan-facebook` | `MetaAdsPreview.svelte` | Mock feed + targeting sidebar |
| `/jasa-iklan-instagram` | `InstagramAdMock.svelte` | Phone frame, format cycle |
| `/jasa-iklan-tiktok` | `TikTokForYouMock.svelte` | Vertical swipe FYP |
| `/jasa-iklan-google` | `GoogleSerpMock.svelte` | SERP typewriter + ads |
| `/jasa-iklan-youtube` | `YouTubePlayerMock.svelte` | Player + format tabs |
| `/jasa-kelola-instagram` | `IgGridPlanner.svelte` | Feed grid 3×3 + calendar |
| `/jasa-kelola-tiktok` | `TikTokContentStudio.svelte` | Timeline batch |
| `/jasa-pembuatan-website` | `WebsiteBuilderPreview.svelte` | Browser chrome assemble |
| `/jasa-pembuatan-landing-page` | `LandingPlusAds.svelte` | Split LP + Ads mock |
| `/paket` | `PricingMatrixInteractive.svelte` | Filter matrix (no hero mock) |
| `/studi-kasus/[slug]` | `CaseStudyDashboard.svelte` | Dashboard per case |
| `/audit` | `AuditWizard.svelte` + `AuditResult.svelte` | Wizard + radar |

**Workflow:** Buat di Figma → export SVG → encode di Svelte. Tidak pakai foto stock kecuali `/tentang` (tim foto).

### P.3 Photo (perlu untuk `/tentang`)

| Foto | Sumber | Consent |
|---|---|---|
| Tim 3-4 orang | Photoshoot internal / Canva placeholder | Wajib izin tertulis |
| Klien logo (12-20 marquee) | Minta izin tertulis; default inisial + industri | Wajib izin tertulis |
| Hero homepage | Tidak ada (pakai dashboard mock) | — |
| Case study eksekusi | Anonymized mock; bukan screenshot dashboard klien | Aman |
| Office Bandung | Foto eksterior/interior kantor (opsional, jika branding butuh) | Foto sendiri |

**Acceptance:** Semua foto di-`consent-check` sebelum publish. Default fallback: inisial SVG avatar (bukan stock face).

### P.4 OG Image strategy

- Default OG: `public/og-default.png` (1200×630) — brand mark + tagline
- Per-service: dynamic `/og/[service-slug].png` via Satori (P1 post-launch)
- Per-blog: dynamic `/og/[...blog-slug].png` via Satori
- OG image dims + size budget ≤ 200KB

---

## Q. WHATSAPP PREFILL TEMPLATE LIBRARY

Semua CTA WA link dibangun via `lib/whatsapp.ts → buildWaLink(message)`. Template di bawah adalah **base text** yang di-encode ke URL parameter.

### Q.1 Generic consultation

```
Halo Beriklan, saya ingin konsultasi gratis untuk digital marketing.

Bisnis: {nama bisnis}
Kota: {kota}
Layanan yang diminati: {layanan}
```

### Q.2 Per-paket (pricing tier CTA)

**Facebook Ads Standart:**
```
Halo Beriklan, saya tertarik paket *Facebook Ads Standart* (Rp 1.750.000/bln).
Mohon info lebih lanjut dan cara mulai.
```

**Facebook Ads Business:**
```
Halo Beriklan, saya tertarik paket *Facebook Ads Business* (Rp 3.750.000/bln).
Brief bisnis saya: [saya akan ceritakan di chat].
```

### Q.3 Per-layanan (service card CTA)

```
Halo Beriklan, saya tertarik dengan *{layanan}*.
Bisa diskusi kebutuhan dan estimasi budget?
```

### Q.4 Audit result follow-up

```
Halo Beriklan, saya baru saja isi audit gratis di website.
Hasil saya: skor {skor}/100, tantangan utama: {tantangan}.
Bisa konsultasi 15 menit?
```

### Q.5 Bundling

**Starter Brand (LP + Google Ads):**
```
Halo Beriklan, saya tertarik paket *Starter Brand* — Landing Page + Google Ads (Rp 1.999.000).
Brief: [industri/kota]
```

### Q.6 Order form submission

```
Halo, saya baru submit form Order di website.
Detail:
- Nama: {nama}
- Bisnis: {bisnis}
- Layanan: {layanan}
- Budget: {budget}
Mohon follow up. Terima kasih.
```

### Q.7 Generic landing dari `/kontak`

```
Halo, saya ingin bertanya via halaman Kontak website Beriklan.
Pertanyaan: [saya akan jelaskan di chat]
```

**Acceptance:** Template tersimpan di `lib/whatsapp-templates.ts` sebagai constants; unit test minimal 1 per template.

---

## R. INTERNAL LINK MATRIX

Aturan: setiap service page link ke **2-3 related service + 1 umbrella + 1 order/blog**. Matrix di bawah untuk visualisasi.

### R.1 Service-to-service

| Service → | FB Ads | IG Ads | TikTok Ads | Google Ads | YouTube Ads | Kelola IG | Kelola TikTok | Website | LP | DM |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| **FB Ads** | — | ● | ● | ● | | ● | | | ● | ● |
| **IG Ads** | ● | — | ● | ● | | ● | | | ● | ● |
| **TikTok Ads** | ● | ● | — | ● | | | ● | | | ● |
| **Google Ads** | ● | ● | | — | ● | | | ● | ● | ● |
| **YouTube Ads** | | | | ● | — | | | | | ● |
| **Kelola IG** | ● | ● | ● | | | — | ● | | | ● |
| **Kelola TikTok** | | | ● | | | ● | — | | | ● |
| **Website** | ● | ● | | ● | | | | — | ● | ● |
| **LP** | | | | ● | | | | ● | — | ● |
| **DM (umbrella)** | ● | ● | ● | ● | ● | ● | ● | ● | ● | — |

● = link dari page baris ke page kolom di section `Related Services`.

### R.2 Hub-and-spoke (digital marketing pillar)

```
/jasa-digital-marketing (pillar)
   ↳ /jasa-iklan-facebook
   ↳ /jasa-iklan-instagram
   ↳ /jasa-iklan-tiktok
   ↳ /jasa-iklan-google
   ↳ /jasa-iklan-youtube
   ↳ /jasa-kelola-instagram
   ↳ /jasa-kelola-tiktok
   ↳ /jasa-pembuatan-website
   ↳ /jasa-pembuatan-landing-page
```

Setiap spoke link balik ke pillar (`Digital Marketing` breadcrumb atau CTA section).

### R.3 Footer universal links

```
Footer col 1: Tentang · Kontak · Blog · Studi Kasus
Footer col 2: Facebook · Instagram · TikTok · Google · YouTube (5 paid ads)
Footer col 3: Kelola IG · Kelola TikTok · Website · Landing Page (organic + build)
Footer col 4: Paket · Order · Privasi · Syarat
```

**Acceptance:** Matrix di atas di-encode sebagai helper `getRelatedServices(slug)` di `lib/internal-links.ts`; tidak hardcode di component.

---

## S. TESTIMONIAL & STATS DATA LIBRARY

Data aktual (siap pakai) untuk komponen `TestimonialSlider` dan `NumberTicker`. Placeholder di sini; **verify angka sebelum publish**.

### S.1 Stats band (homepage + service pages)

| Metric | Value | Source | Catatan |
|---|---|---|---|
| Klien aktif | 60+ | Internal CRM | Update Q1 2026 |
| Tahun pengalaman | 8 | Berdiri 2018 | Fixed |
| Total klien sepanjang masa | 80+ | Internal CRM | Estimate |
| Ad spend terkelola | Rp 50M+ / bulan | Internal | Avg bulanan, range lebih lebar |
| ROAS rata-rata | 4.2× | Internal dashboard 2025 | Range 3.5×-5.2× per industri |
| CPL turun rata-rata | -38% | Internal before/after 6 bln | Aggregate |
| Follower growth avg | +240% | Internal kelola IG klien | 6-bln cohort |
| Respon time | <1 jam kerja | Internal SLA | Weekdays |

### S.2 Testimoni (siap copy)

> "ROAS kami naik dari 1.8× ke 5.2× dalam 90 hari setelah pindah ke Beriklan. Yang paling kerasa: laporan mingguan mereka detail banget, kami bisa lihat exact angka dan next step."
> — **Andi P., Owner Brand Fashion** (alias)

> "Awalnya coba 1 paket kecil buat testing. Sekarang 4 channel jalan bareng. Mereka yang suggest kombinasi, kami tinggal eksekusi."
> — **Maya S., Marketing Lead F&B Chain** (alias)

> "Bukan cuma jalanin iklan, mereka beneran paham funnel. Time to lead dari 7 hari jadi 2 hari."
> — **Reza H., Founder SaaS EduTech** (alias)

> "Tim-nya responsif. Kalau ada update Meta, mereka langsung adjust, gak nunggu akhir bulan."
> — **Linda W., Owner Klinik Kecantikan** (alias)

> "Pindah dari freelancer ke Beriklan itu game changer. Konsistensi kualitas iklan naik, dan biaya turun 22%."
> — **Budi T., Marketing Manager Properti** (alias)

> "Suka banget sama dashboard-nya. Bisa cek real-time, gak perlu nunggu laporan."
> — **Sari N., Owner Brand Kecantikan** (alias)

### S.3 Klien logo (marquee)

Gunakan placeholder logo dari industri yang relevan (fashion, F&B, edukasi, properti, kecantikan, jasa). Consent check sebelum publish; default gunakan **industri badge** bukan logo asli jika belum izin.

Industri yang sudah ada nama (live WP export) bisa dipakai sebagai referensi sosiografis tanpa sebut nama klien.

**Acceptance:**
- [ ] Testimonial: 6 quotes dengan izin tertulis; default pakai alias
- [ ] Stats angka: verify dengan data internal sebelum publish
- [ ] Klien logo: 12-20 dengan izin; fallback industri badge

---

## T. IMPLEMENTATION ORDER — PHASED BREAKDOWN

> Refactor dari §M. Setiap phase punya **gate eksplisit** (deliverable + review checkpoint). Critical path = Phase 0 → 1 → 2 (design approval) → 3 → 4 → 5 → 6 → 7.
> Pola Haloka dipertahankan: **static-first, Svelte hanya island interaktif**.

---

### 🔷 PHASE 0 — Setup & Audit Sinkronisasi (hari 1)

> **Tujuan:** Repo jalan, data konsisten, secrets aman. **Tanpa ini, semua kerjaan Phase 1+ akan salah nomor.**

#### Hari 1 (full day)

**Pagi (4 jam) — Data sinkronisasi (BLOCKER #1)**

- [ ] Buat `src/lib/data/pricing.ts` dengan 9 service × tier LIVE per §A.4
  - Source of truth: angka live `beriklan.co.id`, BUKAN invent 1,5jt/3jt/5jt
  - Format: `export const pricing = { facebookAds: { currency: 'IDR', tiers: [...] } }`
- [ ] Rewrite `src/lib/data/services.ts` entry `'jasa-iklan-facebook'`:
  - Ganti `pricingTiers` dari `Starter/Growth/Scale` → `Standart/Business`
  - Update harga `1.500.000 → 1.750.000`, `3.000.000 → 3.750.000`
  - Update fitur sesuai §A.4 (30 hari tayang, estimasi jangkauan, placement, jumlah iklan)
- [ ] Verifikasi tidak ada service lain yang masih pakai angka invent (grep `1\.500\.000|3\.000\.000|5\.000\.000`)
- [ ] Commit: `chore(data): sync pricing.ts with live site`

**Siang (4 jam) — Environment & scaffold**

- [ ] Verify `web/` ada dan dependencies terinstall (`pnpm install`)
- [ ] Buat `.env` dari `.env.example`:
  ```
  PUBLIC_SITE_URL=http://localhost:4321
  PUBLIC_WA_NUMBER=62811919328
  PUBLIC_SANITY_PROJECT_ID=2pdculh3
  PUBLIC_SANITY_DATASET=production
  ```
- [ ] Rotate token Cloudflare + Sanity dari `account.md` (PENTING — token plaintext)
- [ ] Test `pnpm dev` jalan tanpa error
- [ ] Tambah `.env` ke `.gitignore` (kalau belum)
- [ ] Commit: `chore: env setup + secrets rotated`

**Gate Phase 0:**
- ✅ `pnpm dev` jalan, http://localhost:4321 accessible
- ✅ `pricing.ts` angka = live (cek manual 9 service)
- ✅ `services.ts` Facebook entry = Standart/Business
- ✅ Secrets tidak di-git
- ✅ Review bersama user: angka pricing disetujui

---

### 🔷 PHASE 1 — Design System & Layout Shell (hari 2-4)

> **Tujuan:** Foundation visual + chrome global jadi. Homepage belum, tapi semua building block siap.

#### Hari 2 — Design tokens + motion

- [ ] `src/styles/global.css` → Tailwind v4 `@theme` per §8.1 (color palette, type scale, motion)
- [ ] Self-host Geist + Instrument Serif (cek `@fontsource-variable/geist` di package.json — sudah ada)
- [ ] `src/lib/motion.ts` → spring configs `gentle/snappy/bouncy`, easings
- [ ] `src/lib/cn.ts` (utility class merge) — cek sudah ada
- [ ] Dark mode class strategy di `global.css` (light-first, optional toggle)
- [ ] Commit: `feat(design): tokens + motion + fonts`

#### Hari 3 — Icon set + data files

- [ ] 14 icon SVG di `src/components/icons/` (Facebook, Instagram, TikTok, Google, YouTube, target, chart, funnel, document, sparkle, grid, dll.)
- [ ] `ServiceIcon.astro` wrapper (cek sudah ada, extend kalau kurang)
- [ ] Hardcode data files:
  - `src/lib/data/stats.ts` (8 metrics per §S.1)
  - `src/lib/data/testimonials.ts` (6 quotes per §S.2)
  - `src/lib/data/faqs.ts` (FAQ_HOME + per-service FAQ arrays)
- [ ] `src/lib/internal-links.ts` → `ROUTES.services.facebookAds` dll. (cek sudah ada, extend semua 10 service)
- [ ] `src/lib/whatsapp.ts` → `buildWaLink(message)` + 7 templates dari §Q
- [ ] Commit: `feat(data): stats + testimonials + icons + wa-templates`

#### Hari 4 — Layout shell + SEO helpers

- [ ] `BaseLayout.astro` — `<head>`, meta, fonts, OG tags, View Transitions
- [ ] `PageLayout.astro` — wrap content, container size options
- [ ] `JsonLd.astro` — render JSON-LD scripts (helper per §N)
- [ ] `src/lib/seo.ts` → builders: `buildOrganization()`, `buildWebSite()`, `buildFAQPage()`, `buildBreadcrumb()`, `buildService()`, `buildLocalBusiness()`
- [ ] `Section.astro` primitive (cek sudah ada, extend variants: hero/feature/cta/footer)
- [ ] `robots.txt` + sitemap config (Astro sitemap integration — cek sudah ada)
- [ ] Commit: `feat(layout): base + page + seo helpers`

**Gate Phase 1:**
- ✅ `/dev/ui` atau empty page render dengan token design system
- ✅ Lighthouse empty page > 90
- ✅ Semua icon SVG render
- ✅ Semua data file terimport tanpa error

---

### 🔷 PHASE 2 — Global Chrome Mobile-First (hari 5-6)

> **Tujuan:** Sticky CTA, Navbar, WA float jalan mobile-first. Fondasi konversi.

#### Hari 5 — Navbar + Footer

- [ ] `src/components/svelte/widgets/Navbar.svelte` (`client:load`)
  - Logo kiri, hamburger kanan (mobile), mega-menu hover (desktop)
  - Mobile sheet full-screen dengan grouped nav (Paid Ads · Organic · Build · Full)
  - Scroll shrink behavior (height shrink + bg blur)
  - Primary CTA `Inquiry` → `/order`
- [ ] `src/components/astro/Footer.astro` — 4 kolom per §R.3 + newsletter mini-form
- [ ] Responsive test: 375 / 768 / 1280
- [ ] Commit: `feat(nav): navbar mega-menu + footer`

#### Hari 6 — Sticky CTA + WhatsApp

- [ ] `src/components/svelte/widgets/StickyMobileCta.svelte` (`client:idle`)
  - Hidden > 40% scroll down
  - Dynamic price label per page (`Mulai Rp 1.750.000` dll.)
  - Left: price · Primary: `Konsultasi` · Right: WA icon
  - Mobile only (md:hidden); desktop hide
- [ ] `src/components/svelte/widgets/WhatsAppFloat.svelte` — desktop only (md:block)
  - Pulse ring animation
  - Click → WA prefill generic consultation §Q.1
- [ ] `src/components/svelte/widgets/ThemeToggle.svelte` (optional, light-first default)
- [ ] Safe area CSS: `pb-safe` utility + `viewport-fit=cover`
- [ ] Responsive test mobile (375 width critical)
- [ ] Commit: `feat(widgets): sticky-cta + wa-float + theme-toggle`

**Gate Phase 2:**
- ✅ Navbar mobile sheet open/close smooth
- ✅ Sticky CTA muncul setelah scroll >40% di mobile
- ✅ WA float visible desktop only
- ✅ Footer 4 kolom + newsletter

---

### 🔷 PHASE 3 — Homepage (hari 7-10) ← **DESIGN APPROVAL GATE**

> **Tujuan:** Homepage lengkap sebagai design system proof + first impression. **Tidak lanjut mass build tanpa approve.**

#### Hari 7 — Hero + Trust + Pain

- [ ] `src/components/svelte/sections/HeroScene.svelte` (`client:visible`)
  - **Ads Command Center** dashboard SVG:
    - Header strip: `Campaign Live · Meta + Google` dengan live dot
    - ROAS big number ticker (4.2×)
    - Mini funnel 4-step: Impression → Click → Lead → Closing
    - 3 campaign rows: status, spend, CPA (tween animation)
    - Sparkline SVG naik
    - Toast notif: "Budget reallocated · CPA −18%"
- [ ] `src/pages/index.astro` section 1-3 (Hero + Trust + Pain) per §D.1
  - Hero copy: H1 `Dari 0 ke ribuan chat WhatsApp per bulan.`
  - Subheadline + dual CTA (WA primary + Lihat Layanan secondary)
  - Eyebrow badge live pulse
- [ ] Commit: `feat(home): hero + trust + pain`

#### Hari 8 — Method + Services + Process + Stats

- [ ] Section 4-7 homepage:
  - Bento 6-step method (Astro + ScrollReveal)
  - Service grid 10 (per §D.1)
  - Process 4 steps horizontal (Svelte stepper)
  - NumberTicker stats band (8 metrics per §S.1)
- [ ] TiltCard untuk service cards (desktop only)
- [ ] Commit: `feat(home): method + services + process + stats`

#### Hari 9 — Social + Pricing + FAQ + Final CTA

- [ ] Section 8-12 homepage:
  - Testimonial marquee (6 quotes per §S.2)
  - Pricing teaser 3 paket highlight (Meta/Google/TikTok)
  - FAQ accordion (5-6 Q, SEO-rich)
  - Final CTA magnetic
- [ ] StickyMobileCta integrated with homepage
- [ ] Commit: `feat(home): social + pricing + faq + cta`

#### Hari 10 — Homepage polish + review

- [ ] Reduced motion pass (audit semua Svelte island, respect `prefers-reduced-motion`)
- [ ] Responsive QA (375/768/1280/1440)
- [ ] Lighthouse mobile ≥ 95, desktop ≥ 98
- [ ] JSON-LD valid (Organization + FAQPage)
- [ ] **Demo ke user untuk design approval**
- [ ] Catatan revisi → commit: `polish(home): responsive + a11y + perf`

**🔴 GATE PHASE 3 — Tidak boleh lanjut Phase 4 sebelum approve:**
- ✅ User lihat demo `localhost:4321` approve visual direction
- ✅ Lighthouse mobile ≥ 95
- ✅ Total JS homepage < 100KB gzipped
- ✅ A11y keyboard nav + focus visible
- ✅ NumberTicker real (bukan 0 palsu)

---

### 🔷 PHASE 4 — Service Pages Mass Build (hari 11-16)

> **Setelah approve.** 10 service pages paralel 2 track.

#### Track B — Paid Ads (hari 11-14, 4 hari)

Pola yang sama untuk tiap page, hanya copy + HeroDemo yang beda:

| Hari | Page | HeroDemo | Komponen unik |
|---|---|---|---|
| 11 | `/jasa-iklan-facebook` | `MetaAdsPreview.svelte` | Targeting UI mock + sidebar interest chips |
| 12 | `/jasa-iklan-instagram` | `InstagramAdMock.svelte` | Phone frame Feed → Story → Reels cycle |
| 13 | `/jasa-iklan-tiktok` | `TikTokForYouMock.svelte` | Vertical swipe FYP + view ticker |
| 14 pagi | `/jasa-iklan-google` | `GoogleSerpMock.svelte` | SERP typewriter + ads highlight |
| 14 siang | `/jasa-iklan-youtube` | `YouTubePlayerMock.svelte` | Player mock + format tabs |

**Per-page checklist (ulang 5x):**
- [ ] H1 + meta unique (per §D.3-7)
- [ ] 6 fitur (template service §C slot 4)
- [ ] PricingCards Svelte dengan pricing LIVE §A.4
- [ ] FAQ accordion ≥ 4 Q
- [ ] Related services (3 link, per matrix §R.1)
- [ ] Internal link ke `/order` + `/jasa-digital-marketing`
- [ ] Schema `Service` + `Offer` + `FAQPage` (snippet §N.2)
- [ ] CTA `Konsultasi paket [nama]` → WA prefill §Q.2
- [ ] StickyCta update price label

#### Track C — Organic + Build + Umbrella (hari 14-16, 2.5 hari)

| Hari | Page | HeroDemo |
|---|---|---|
| 14 sore | `/jasa-digital-marketing` (umbrella) | `OmnichannelMap.svelte` |
| 15 | `/jasa-kelola-instagram` + `/jasa-kelola-tiktok` | `IgGridPlanner.svelte` + `TikTokContentStudio.svelte` |
| 16 | `/jasa-pembuatan-website` + `/jasa-pembuatan-landing-page` | `WebsiteBuilderPreview.svelte` + `LandingPlusAds.svelte` |

**Gate Phase 4:**
- ✅ 10 service pages live local
- ✅ Pricing semua angka = LIVE §A.4
- ✅ Cross-link matrix §R.1 implemented (no orphan)
- ✅ Schema valid 10/10

---

### 🔷 PHASE 5 — Conversion & Trust Pages (hari 17-19)

> **Setelah service pages ok.** Halaman lead capture + trust.

#### Hari 17 — `/order` (Multi-step Wizard) — TRACK A priority

- [ ] `src/components/svelte/forms/OrderWizard.svelte`
  - Step 1: Jenis layanan (chips 8 + custom)
  - Step 2: Budget range (chips 4)
  - Step 3: Bisnis + WA (form)
  - Step 4: Review + submit
- [ ] Astro Action `src/actions/order.ts` → email + WA prefill §Q.6
- [ ] Honeypot + Turnstile (kalau env ready)
- [ ] Success state: confetti + redirect WA
- [ ] `/order` page section 1-5 per §D.12

#### Hari 18 — `/kontak` + `/tentang` + `/404` — TRACK A lanjut

- [ ] `/kontak` per §D.18 (contact cards + simple form + map embed)
- [ ] `/tentang` per §D.17 (timeline Svelte + tim + partner marquee)
- [ ] `/404` branded (line art SVG + headline + 4 link)
- [ ] Schema `LocalBusiness` di `/kontak`

#### Hari 19 — `/paket` (Pricing Aggregator) — TRACK D

- [ ] `/paket` per §D.15
  - Sticky tab filter Svelte (`Paid Ads · Social · Website · Bundling`)
  - Accordion matrix 9 service × tier
  - 3 bundle cards (Starter Brand / Lead Gen Meta / Omnichannel)
  - Comparison table (DIY · Freelancer · Beriklan)
  - 8 FAQ pricing
- [ ] Schema `Service` + `OfferCatalog`

**Gate Phase 5:**
- ✅ `/order` wizard flow 4 step works
- ✅ `/kontak` form submit + map visible
- ✅ `/tentang` timeline responsive
- ✅ `/paket` tab filter + accordion smooth

---

### 🔷 PHASE 6 — Content Hub (hari 20-22)

> **Blog + Studi Kasus + Audit Lead Magnet.**

#### Hari 20 — Blog + Sanity client — TRACK F

- [ ] `src/lib/sanity.ts` — client setup (project `2pdculh3`)
- [ ] `src/pages/blog/index.astro` — fetch posts + filter kategori
- [ ] `src/pages/blog/[...slug].astro` — single post + PortableText render
- [ ] `src/pages/blog/kategori/[category].astro` — filter by category
- [ ] Schema `BlogPosting` per §N.3
- [ ] Inline CTA mid-article (Svelte island)
- [ ] Related posts (3)

#### Hari 21 — `/studi-kasus` + 3 case studies — TRACK E

- [ ] `/studi-kasus` index per §D.16 list page
- [ ] `/studi-kasus/[slug]` single template
- [ ] `CaseStudyDashboard.svelte` Svelte (mini dashboard animasi)
- [ ] 3 MDX case studies (industri: F&B, Fashion, Jasa)
  - Frontmatter per §D.16 spec
  - Verify angka internal sebelum publish
- [ ] Schema `Article` per §N.4

#### Hari 22 — `/audit` 7Q Wizard — TRACK G

- [ ] `AuditWizard.svelte` per §D.19
  - 7 step, single-page stepper
  - Progress bar + animasi slide
  - Reduced motion fallback
- [ ] `AuditResult.svelte` — radar chart SVG + recommendation list
- [ ] `lib/audit-scoring.ts` — score logic (4 kategori: Targeting/Creative/Tracking/Optimasi)
- [ ] Tracking events: `audit_start` / `audit_step_complete` / `audit_submit` / `audit_lead_capture`
- [ ] Privacy + Terms stubs `/privacy` `/terms` — TRACK H

**Gate Phase 6:**
- ✅ Blog 1 sample post render
- ✅ 3 case studies publish-ready
- ✅ Audit wizard skor deterministik (same input = same output)
- ✅ Privacy + Terms live (placeholder OK)

---

### 🔷 PHASE 7 — Performance, A11y, SEO Hardening (hari 23-25)

> **Polishing sebelum staging.** Semua harus pass sebelum deploy preview.

#### Hari 23 — Performance

- [ ] Bundle visualizer (`pnpm build` + analyze)
- [ ] Island audit: pastikan < 6 hydrated islands per page
- [ ] Image pass: `astro:assets` + `loading="lazy"` below fold
- [ ] Font subset check (max 2 family)
- [ ] Target: homepage JS < 100KB gz
- [ ] Lighthouse mobile ≥ 95 (homepage + 3 service sample)

#### Hari 24 — A11y + SEO

- [ ] Keyboard navigation test (tab order, focus visible, skip-to-content)
- [ ] Contrast check (WCAG AA, color tokens)
- [ ] ARIA labels di icon-only buttons (WA, theme toggle)
- [ ] `prefers-reduced-motion` audit semua Svelte island
- [ ] Schema validasi via Google Rich Results Test (5 sample: home + 3 service + 1 blog)
- [ ] Internal link matrix §R validate (no orphan via Screaming Frog atau curl sitemap)

#### Hari 25 — Analytics + tracking QA

- [ ] `src/lib/analytics.ts` GA4 wrapper implement
- [ ] 17 events firing per spec §O.1 (test di console + GA4 DebugView)
- [ ] Conversion funnel path di-setup GA4
- [ ] Custom dimensions: `service_slug`, `tier_name`, `form_name`
- [ ] Privacy consent banner (kalau pakai GA4 + cookies)

**Gate Phase 7:**
- ✅ Lighthouse mobile ≥ 95 di semua money pages
- ✅ A11y score ≥ 95
- ✅ Schema valid 5/5 sample
- ✅ Internal link matrix no orphan
- ✅ Analytics events firing confirmed

---

### 🔷 PHASE 8 — Staging Deploy & Final Approval (hari 26-27)

> **Deploy preview, BUKAN apex domain.** User review, lalu approve untuk production.

#### Hari 26 — Deploy Cloudflare Pages preview

- [ ] `web/wrangler.toml` (atau `pages.toml`) setup
- [ ] Connect Cloudflare Pages ke repo `webberiklan` (atau push manual)
- [ ] Set env vars di CF Pages dashboard (PUBLIC_* + Sanity token)
- [ ] First deploy + verify SSL + custom preview subdomain (contoh: `staging-beriklan.pages.dev`)
- [ ] Test semua route di staging URL

#### Hari 27 — Final review

- [ ] User buka staging URL di desktop + mobile
- [ ] Click-through semua CTA (WA prefill benar, form submit works)
- [ ] Cek OG image di Facebook debugger + Twitter card validator
- [ ] Cek redirect dari URL lama (sample 10 URL dari `url_classification.csv`)
- [ ] Catatan revisi final → commit → re-deploy
- [ ] **🔴 GATE: User tulis approval sebelum Phase 9**

**Gate Phase 8:**
- ✅ Staging URL accessible, SSL valid
- ✅ User approve tertulis (email/chat)
- ✅ Semua CTA + form working
- ✅ Redirect matrix sample tested

---

### 🔷 PHASE 9 — Production Cutover (hari 28-29, **HANYA setelah Phase 8 approve**)

> **Highest risk phase.** Jangan rush.

#### Hari 28 — DNS + redirects

- [ ] Freeze WP writes (kalau masih sync)
- [ ] Lower DNS TTL 24 jam sebelumnya (kalau domain sudah live di tempat lain)
- [ ] Setup `_redirects` di `public/` dari CSV (`scripts/generate-redirects.ts`)
- [ ] Point `beriklan.co.id` ke Cloudflare Pages (DNS)
- [ ] Verify SSL auto-issue
- [ ] Verify www → apex atau sebaliknya

#### Hari 29 — SEO + monitoring

- [ ] GSC property verify
- [ ] Submit sitemap
- [ ] IndexNow batch submit (top 50 URL)
- [ ] Monitor 48 jam:
  - 404 spike?
  - Form submission works?
  - Core Web Vitals real-user?
  - WA click events firing?
- [ ] Enable SEO Worker cron (dari SEO-PLAYBOOK) — hati-hati tahap awal

**Gate Phase 9 (Production Live):**
- ✅ `beriklan.co.id` serve dari Cloudflare Pages
- ✅ SSL valid + redirect chain benar
- ✅ GSC + sitemap submitted
- ✅ 48 jam monitoring: no critical issue

---

## 📋 QUICK ANSWER: Apa yang Dikerjakan DI AWAL

### Hari 1 — HARI INI (5 langkah wajib)

1. **🔴 Sinkronkan `pricing.ts`** — buat file baru dari §A.4 LIVE (angka 1.750.000, 3.750.000, dll.)
2. **🔴 Rewrite `services.ts` entry Facebook** — Standart/Business, harga LIVE, fitur LIVE
3. **🟡 Setup `.env`** — site URL, WA number, Sanity project ID
4. **🟡 Verify `pnpm dev` jalan** — http://localhost:4321 accessible
5. **🟢 Commit + branch** — `feature/redesign-v2` dari main

### Hari 2-4 — Design System Foundation

- Tokens (Tailwind v4 `@theme`)
- Fonts (Geist + Instrument Serif)
- Motion library (`lib/motion.ts`)
- Icon set 14 SVG
- Data files (stats, testimonials, FAQs)
- Layout shell (BaseLayout, PageLayout, JsonLd)

### Hari 5-6 — Global Chrome Mobile

- Navbar (mega-menu desktop, sheet mobile)
- StickyCta (mobile-only, dynamic price)
- WhatsAppFloat (desktop-only)
- Footer 4 kolom + newsletter

### Hari 7-10 — Homepage (DESIGN APPROVAL GATE)

- HeroScene Ads Command Center
- 12 sections per §D.1
- Testimoni + Pricing teaser + FAQ + Final CTA
- Lighthouse mobile ≥ 95
- **🔴 DEMO KE USER UNTUK APPROVE**

### Setelah approve → mass build (Phase 4-9)

Detail per track di atas.

---

## ❌ LARANGAN (Don't Do List)

- ❌ **Jangan mulai 9 money pages sekaligus sebelum homepage approve**
- ❌ **Jangan tulis service copy tanpa `pricing.ts` sudah sinkron LIVE**
- ❌ **Jangan deploy production sebelum staging approved**
- ❌ **Jangan skip event spec §O** — retrofit analytics mahal
- ❌ **Jangan skip internal link matrix §R** — orphan pages = rugi SEO
- ❌ **Jangan pakai angka invent (1,5jt / 3jt / 5jt)** di copy manapun — ini blocker
- ❌ **Jangan hardcode harga di component** — selalu via `pricing.ts`
- ❌ **Jangan skip `prefers-reduced-motion`** — accessibility blocker
- ❌ **Jangan lupa Turnstile / honeypot di form** — spam protection
- ❌ **Jangan lupa consent foto tim + klien** — legal risk

---

## 📊 TIMELINE RINGKAS

| Phase | Scope | Hari | Gate |
|---|---|---:|---|
| **0** | Setup + data sync | 1 | Repo jalan, pricing match |
| **1** | Design system + layout shell | 2-4 | Token foundation ready |
| **2** | Global chrome mobile | 5-6 | Sticky CTA jalan |
| **3** | Homepage | 7-10 | **🔴 Design approval** |
| **4** | 10 service pages | 11-16 | Semua money pages live |
| **5** | Order + Kontak + Tentang + 404 + Paket | 17-19 | Lead capture works |
| **6** | Blog + Studi Kasus + Audit + Privacy | 20-22 | Content hub ready |
| **7** | Perf + A11y + SEO + Analytics | 23-25 | Lighthouse ≥ 95 |
| **8** | Staging deploy + final review | 26-27 | **🔴 User approval** |
| **9** | Production cutover | 28-29 | **🔴 Domain live** |

**Total: 22-29 hari kerja** (tergantung paralel track setelah Phase 3).

---
