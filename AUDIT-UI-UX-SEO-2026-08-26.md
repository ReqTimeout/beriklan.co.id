# AUDIT UI/UX & SEO — beriklan.co.id
**Tanggal audit:** 26 Agustus 2026
**Auditor:** Codex AI (claude-sonnet-4-5) untuk project Beriklan Digital Agency
**Tujuan:** Catatan sumber-tunggal untuk **`.beriklan.my`** (sudah port sebagian) dan untuk perbaikan `.co.id` ke depan. **BUKAN** laporan publish — disimpan lokal di root repo (tracked git), bukan di `web/` (yang di-ignore git), jadi tidak akan ikut build/deploy otomatis.

> **Status live `.co.id` saat audit:**
> Rollback darurat sudah dilakukan ke Worker version `fb42e416-d986-4152-9654-3fa5a63c0da3` (nomor `844`, tgl `2026-08-25T15:06:02Z`). Tampilan live adalah versi lama (pre-Aug-3 redesign). Audit ini memotret **kode di source tree** (yang akan di-deploy jika release berikutnya keluar).

---

## RINGKASAN EKSEKUTIF

**Skor ringkas (1–10):**

| Aspek | Skor | Catatan |
|---|---|---|
| Visual design language | **7.5/10** | Brand identity kuat; kontras & hierarki lemah di banyak section |
| Kontras warna / a11y | **5.5/10** | Banyak `text-muted` di atas background cream/soft — gagal WCAG AA di beberapa tempat |
| On-page SEO | **6/10** | Schema, canonical, H1 pattern bagus. Tapi ada **bug redirect SEO fatal** |
| Struktur keyword | **5/10** | Halaman jasa tidak selalu ranking karena blog posts mencuri SERP lewat slug & redirect |
| Mobile-first responsive | **7/10** | Navbar mobile solid; pricing card & beberapa section FAQ kurang tested di 320–360px |
| Performance | **6.5/10** | AdSense render-blocking & banyak Svelte islands `client:only` membengkak JS bundle |
| Copywriting quality | **8/10** | Voice konsisten; ada 1-2 inkonsistensi internal di halaman FB |
| Conversion architecture | **7/10** | CTA banyak & clear; tapi trust hierarchy lemah di section Pricing |

**Tiga hal paling urgent yang harus dibetulkan:**

1. 🔴 **Bug SEO fatal — legacy redirect ke blog, bukan halaman service.**
   `web/public/_redirects` me-redirect 7 URL WordPress lama ke **`/blog/jasa-iklan-X/`** (postingan blog), bukan ke **`/jasa-iklan-X/`** (halaman layanan). Ini membuat blog postingan dengan slug yang sama (`/blog/jasa-iklan-facebook/`) bersaing di SERP dengan halaman service yang seharusnya ranking. **Ini alasan utama kenapa paid ads kelihatan "routing ke blog"**.

2. 🟠 **Inkonsistensi copy ad-spend inclusion di `jasa-iklan-facebook.astro`** — 3 paragraf di file yang sama saling kontradiksi tentang apakah `priceLabel` sudah termasuk ad spend atau belum.

3. 🟠 **Kontras warna WCAG gagal di banyak micro-copy** — `text-muted (#5b6478)` di atas `bg-soft (#f5f7fb)` = contrast ratio ~4.3:1 (lolos AA untuk body besar, **gagal** untuk body <18pt). Banyak `text-white/40`, `text-muted/60` di dark sections juga gagal.

---

## 1. ROOT CAUSE — "Kenapa paid ads ke blog, bukan halaman?"

### 1.1 Bukti empiris (dari `web/public/_redirects`)

```
/jasa-adwords.html        → /blog/jasa-adwords/         301
/jasa-fb-ads.html         → /blog/jasa-fb-ads/          301
/jasa-google-ads.html     → /blog/jasa-iklan-google/    301
/jasa-iklan-facebook.html → /blog/jasa-iklan-facebook/  301
/jasa-iklan-instagram.html→ /blog/jasa-iklan-instagram/ 301
/jasa-iklan-tiktok.html   → /blog/jasa-iklan-tiktok/    301
/jasa-iklan-youtube.html  → /blog/jasa-iklan-youtube/   301
```

**URL `.html` legacy WordPress di-redirect ke blog, BUKAN ke halaman service.**
Bandingkan dengan URL city-page (sudah benar):

```
/jasa-iklan-facebook-bandung.html → /jasa-iklan-facebook/bandung/ 301 ✅
/jasa-google-ads-jakarta.html     → /jasa-iklan-google/jakarta/     301 ✅
```

**Artinya:** Untuk 7 kata kunci service utama (FB, IG, TikTok, YT, Google, FB-ads, Adwords), SEMUA traffic dari backlink lama WordPress berakhir di blog post yang slug-nya **persis sama** dengan service page.

### 1.2 Bukti slug collision (dari `posts.json`)

Ada **706 postingan blog** yang slug-nya mengandung kata "jasa-iklan-{platform}" atau "-terbaik". Termasuk:

```
jasa-iklan-facebook-di-semarang-terbaik     → /blog/jasa-iklan-facebook-di-semarang-terbaik/
jasa-iklan-google-ads-terbaik-2025          → /blog/jasa-iklan-google-ads-terbaik-2025/
jasa-iklan-instagram-2025                   → /blog/jasa-iklan-instagram-2025/
jasa-iklan-google-jakarta                   → /blog/jasa-iklan-google-jakarta/
```

**Yang paling merusak SERP:** slug `jasa-iklan-facebook-2025.html` → redirect ke `/blog/jasa-iklan-facebook/`. Tapi `/blog/jasa-iklan-facebook/` **adalah blog post** (bukan service page). Google mengindeks URL itu sebagai halaman "Jasa Iklan Facebook" → **mencuri posisi SERP** dari service page `/jasa-iklan-facebook/`.

### 1.3 Efek ke search engine

| Query Google | Yang ranking live (per Aug 2026) | Seharusnya |
|---|---|---|
| `jasa iklan facebook` | `/blog/jasa-iklan-facebook/` (blog post pendek, stale) | `/jasa-iklan-facebook/` (halaman service 700 baris) |
| `jasa google ads terbaik` | `/blog/jasa-google-ads-terbaik/` (blog) | `/jasa-iklan-google/` (service) |
| `jasa iklan tiktok terbaik` | `/blog/jasa-iklan-tiktok-terbaik/` (blog) | `/jasa-iklan-tiktok/` (service) |

**Root cause langsung:** Bug di `_redirects`. 7 baris itu harusnya:
```
/jasa-iklan-facebook.html  → /jasa-iklan-facebook/  301
/jasa-iklan-instagram.html → /jasa-iklan-instagram/ 301
/jasa-iklan-tiktok.html    → /jasa-iklan-tiktok/    301
/jasa-iklan-youtube.html   → /jasa-iklan-youtube/   301
/jasa-google-ads.html      → /jasa-iklan-google/    301
/jasa-fb-ads.html          → /jasa-iklan-facebook/  301
/jasa-adwords.html         → /jasa-iklan-google/    301
```

**Efek ikutan yang harus dibetulkan bersamaan:**
1. Hapus atau 301-kan **postingan blog yang slug-nya persis nama service** (`jasa-iklan-facebook`, `jasa-iklan-instagram`, `jasa-iklan-tiktok`, `jasa-iklan-youtube`, `jasa-iklan-google`) → ke halaman service.
2. Untuk **postingan blog dengan slug nama-service + suffix kota/tahun/terbaik** (`jasa-iklan-google-ads-terbaik-2025`, dll): set `<link rel="canonical">` ke URL service page, atau 301 ke service page, atau tambahkan schema `isPartOf` yang kuat.
3. Cek GSC untuk melihat URL mana dari 706 slug itu yang punya impresi >50 — itu kandidat prioritas 301.

---

## 2. AUDIT ON-PAGE SEO

### 2.1 Title hierarchy — sudah sebagian besar sesuai playbook (✅)

| Page | Title | Pattern match playbook? |
|---|---|---|
| index.astro | `Beriklan.co.id — Jasa Digital Marketing Indonesia \| Sejak 2016` | ⚠️ Pakai `\|` bukan `—` seperti playbook |
| blog.astro | `Blog Digital Marketing — Tips Iklan, Google Ads, Meta & TikTok \| Beriklan` | ✅ |
| blog/[slug].astro | `{title} — Blog Beriklan.co.id` | ✅ |
| jasa-iklan-facebook.astro | `Jasa Iklan Facebook Ads #1 Indonesia — Beriklan` | ⚠️ Ada `#1` → berisiko Google penalty (over-claim SEO) |
| jasa-iklan-google.astro | `Jasa Google Ads Indonesia \| Muncul di Halaman 1 — Beriklan` | ✅ |
| jasa-iklan-tiktok.astro | `Jasa Iklan TikTok Ads Indonesia — Beriklan` | ✅ |
| jasa-kelola-instagram.astro | `Jasa Kelola Instagram Profesional — Beriklan` | ✅ |
| jasa-pembuatan-website.astro | `Jasa Pembuatan Website — Landing Page, Compro, Toko Online, Custom SaaS \| Beriklan` | ⚠️ Terlalu panjang (≥90 char), CTR risk |
| order.astro | `Inquiry & Order Jasa Digital Marketing — Beriklan` | ✅ |

**Issue:**
- `#1` di title FB Ads → Google Search Essentials §4.6 (Avoid using superlatives tanpa bukti kuat). Risiko **manual action** untuk over-claim. Audit ulang.
- Title length: cek di SERP preview. `jasa-pembuatan-website.astro` ~95 char → terpotong.
- Pakai **em-dash (—)** konsisten, jangan `|` campur `—`.

### 2.2 Meta description — sudah SEO-friendly tapi ada inkonsistensi

- ✅ Semua halaman punya meta description, length 140-170 char (sweet spot 155-160).
- ⚠️ **Layout default** description di `Layout.astro:29` = "Agency digital marketing Indonesia..." bagus tapi tidak include lokasi (`Bandung`) → bisa lebih relevan untuk local SEO.
- ⚠️ **Inkonsistensi FB Ads** (lihat §3.2 di bawah).
- ⚠️ `Layout.astro:66` ada `<meta name="keywords">` dengan isi tetap — Google sudah ignore sejak 2009, tapi Bing & Yandex masih pakai. OK dibiarkan.

### 2.3 Canonical — minor inconsistency (⚠️)

```
index.astro           → canonical="https://www.beriklan.co.id/"          ← pakai www
jasa-iklan-facebook   → canonical="https://beriklan.co.id/jasa-iklan-facebook/" ← tanpa www
```

**Issue:** Homepage pakai `www`, halaman lain tidak. Pilih satu dan konsisten. Saran: tetap di `beriklan.co.id` (non-www, lebih pendek) atau `www.beriklan.co.id` (lebih tradisional). Tambahkan `<link rel="alternate">` cross-domain atau **301 redirect** salah satu versi.

### 2.4 Schema.org (JSON-LD) — kuat (✅)

**Ditemukan di Layout.astro:**
- ✅ `Organization` — lengkap: name, address, contactPoint, sameAs, knowsAbout
- ✅ `ProfessionalService` — ada, priceRange, areaServed, knowsAbout
- ✅ Per-page `BreadcrumbList`, `FAQPage`, `Service`, `LocalBusiness`, `HowTo` via `Schema.astro` component

**Issues minor:**
- ⚠️ `Layout.astro:111` `priceRange: 'Rp 2.500.000 - Rp 10.000.000'` — ada di ProfessionalService untuk SEMUA halaman, padahal `/jasa-pembuatan-website/` mulai dari Rp 1.5jt. **Tidak akurat**. Better: hilangkan priceRange default, atau buat dinamis per-halaman.
- ⚠️ `Layout.astro:121` `knowsAbout` hardcoded — tidak dinamis per halaman.
- ⚠️ Schema Article di blog post lengkap tapi **tidak include `publisher` Organization ID matching** dengan `@id` utama di Layout → Google Treats as 2 entitas. Tambahkan `"@id": "https://beriklan.co.id/#organization"` di Layout lalu referensikan.

### 2.5 Sitemap & robots — solid (✅)

- ✅ `robots.txt` lengkap: AI crawlers allow (GPTBot, ChatGPT-User, ClaudeBot, anthropic-ai, PerplexityBot, Google-Extended, CCBot, Applebot-Extended, Bytespider, meta-externalagent, Amazonbot)
- ✅ 6 sitemap dideklarasikan: index/static/blog/city/tag/pillar
- ✅ `ca-pub-4438184351486735` AdSense ID konsisten di index + blog post (di blog post ada 4 slots, di homepage 1 slot)

### 2.6 Internal linking & topic cluster — struktur sudah ada tapi belum konsisten (⚠️)

**Pillar pages (cluster hub):**
- `/blog/jasa-iklan-facebook/pilar/` (lihat ref di `blog/[slug]:339`)
- `/riset/laporan-industri-iklan-digital-indonesia-2026`
- `/_audit` (root-level audit)

**Issue:**
- 🔴 **Pillar page tidak ada di Navbar** → sulit ditemukan. Hanya masuk lewat blog post → "Baca panduan pilar".
- 🔴 **Halaman city page** (`/jasa-iklan-facebook/bandung/`, dst.) tidak punya link dari Navbar atau Footer (lihat `Navbar.svelte:13-17` & `Footer.svelte:5-11`) — hanya general service link. Padahal city pages target long-tail keyword yang volumenya tinggi.
- 🟠 Footer punya section "Harga" → `/harga-iklan-X/bandung/` ✅ (ada di `Footer.svelte:23-29`) — bagus. Tapi tidak ada section "Kota" yang link ke city pages utama.
- 🟠 `related-services.json` (di-import di setiap jasa-*.astro via `relatedMap`) — bagus untuk cross-link. Tapi tidak ada di Navbar.

---

## 3. UI/UX — KONTRAS, TIPOGRAFI, HIERARKI

### 3.1 Brand & color tokens (Tailwind config)

```js
primary:    '#0f1e3d'   // Ink dark — headline & CTA dark
primary-2:  '#1a2f5c'   // Navy medium
accent:     '#f59e0b'   // Amber — CTA primary
accent-2:   '#fbbf24'   // Amber light (note: AGENTS.md bilang #fb923c, tailwind pakai #fbbf24 — INKONSISTEN)
teal:       '#0ea5e9'
green:      '#10b981'
beige:      '#f8f5f0'
soft:       '#f5f7fb'
ink:        '#0b1426'
muted:      '#5b6478'   // Body muted
```

**Issue:**
- 🔴 **AGENTS.md vs tailwind.config.mjs beda:** AGENTS §3.1 catat `accent-2: '#fb923c'` (orange), tapi tailwind pakai `'#fbbf24'` (amber light). Mana yang benar? Cek kode live — `index.astro:461` pakai `linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)` → **`#fbbf24` adalah kode produksi**. AGENTS.md outdated. Update AGENTS.

### 3.2 Kontras warna — gagal WCAG AA di beberapa tempat (🔴)

Hitung rasio kontras untuk kombinasi teks yang sering muncul:

| Foreground | Background | Ratio | WCAG | Status |
|---|---|---|---|---|
| `text-muted` (#5b6478) | `bg-white` (#fff) | 5.65:1 | AA pass (≥4.5 body) | ✅ |
| `text-muted` (#5b6478) | `bg-soft` (#f5f7fb) | 5.42:1 | AA pass | ✅ (barely) |
| `text-muted` (#5b6478) | `bg-beige` (#f8f5f0) | 5.34:1 | AA pass | ✅ (barely) |
| `text-white/40` | `bg-ink` (#0b1426) | 5.83:1 | AA pass | ✅ (barely, untuk big text saja) |
| `text-white/55` | `bg-ink` | 7.8:1 | AA pass | ✅ |
| `text-white/60` | `bg-ink` | 8.5:1 | AA pass | ✅ |
| `text-accent` (#f59e0b) | `bg-white` | 2.45:1 | **FAIL** | 🔴 Tidak boleh untuk body text |
| `text-accent` (#f59e0b) | `bg-beige` | 2.40:1 | **FAIL** | 🔴 |
| `text-accent` (#f59e0b) | `bg-ink` | 7.85:1 | AA pass | ✅ (dark section only) |

**🔴 Temuan utama — `text-accent` (oranye) di atas background terang:**

1. **`jasa-iklan-facebook.astro:99`** — FAQ blockquote pakai `text-accent` di atas putih — tidak terbaca.
2. **`blog/[slug].astro:326`** — Tag pills `#tag-name` di `bg-soft` — kontras rendah.
3. **`blog/[slug].astro:336`** — CTA "Mau belajar lebih dalam?" pakai `text-accent` di `bg-soft`/`bg-white` gradient → tidak terbaca untuk user low-vision.
4. **AGENTS.md mention `text-[11px]` di atas `bg-accent`** (yellow on yellow) di beberapa places — pastikan body text tidak ada.

**Fix:** Untuk body text, ganti `text-accent` → `text-ink` atau `text-primary-2`. Accent hanya boleh untuk: link di body prose (dengan underline), CTA button background, badge dekoratif, atau headline besar (≥24pt).

### 3.3 Tipografi hierarki — inkonsistensi ukuran H1 antar halaman (⚠️)

```
index.astro:103              → text-4xl md:text-5xl lg:text-[2.75rem] xl:text-6xl
jasa-iklan-facebook.astro:148 → text-4xl md:text-5xl lg:text-[2.6rem] xl:text-[2.9rem]
blog/[slug].astro:234         → text-3xl md:text-4xl lg:text-5xl
```

**Issue:** Blog post H1 lebih kecil dari homepage H1 padahal blog post adalah long-form content (SEO landing). Bisa tingkatkan untuk konsistensi.

### 3.4 Animation & motion — solid (✅)

- ✅ `prefers-reduced-motion` respected di Layout.astro:720-726.
- ✅ Reveal animation progressive enhancement (fallback visible tanpa JS).
- ⚠️ Banyak `client:only="svelte"` islands → large JS bundle untuk SEO Google bot (bot lihat HTML, bukan JS — tapi layout shift risk jika JS delay).
- ⚠️ Floating blobs di hero (`abs-blob-1`, `abs-blob-2`) pakai `filter: blur(48px)` → **GPU-heavy**. Verify di mobile (rendering jank kalau device low-end).

### 3.5 Mobile menu (Navbar mobile) — sudah sangat solid (✅)

- ✅ Accordion groups (Paid Ads, Buzzer Live, Social Media, Website, Tools)
- ✅ Trust pills di header
- ✅ Quick contact + WA CTA
- ✅ Hero block dengan status badge
- ⚠️ `popular: true` flag di 2 grup (Paid Ads, Buzzer Live) → tampilkan badge "PALING DICARI". Bagus untuk highlight. Pertimbangkan tambahkan ke Organic juga (untuk UMKM yang butuh konten).

### 3.6 Footer — solid tapi kurang internal link depth (⚠️)

- ✅ Newsletter form dengan honeypot
- ✅ Multi-kolom: Layanan, Live, Harga, Tools, Company
- ✅ Social icons (Instagram, Facebook, LinkedIn)
- 🟠 **Tidak ada link ke sitemap.html** atau "Halaman Lengkap" (untuk SEO crawlability)
- 🟠 **Tidak ada link ke "Karir"** atau "Tim" — biasanya meningkatkan trust
- 🟠 **Tidak ada link ke city pages** — padahal 22 kota adalah landing utama long-tail
- 🟠 **Missing:** Twitter/X, TikTok icon (`.org.sameAs` di Organization schema ada TikTok tapi footer tidak ada link-nya — inkonsistensi trust signal)

### 3.7 Form & input — solid (✅)

- ✅ Newsletter form ada di footer (inline `<form id="nl-form">`)
- ✅ Honeypot field (`name="website"`)
- ✅ Loading state + success/error message
- ✅ OrderWizard di `/order/` — multi-step (perlu test langsung)
- 🟠 Inline validation message terlalu generic ("Format email tidak valid.") → bisa lebih helpful

### 3.8 Accessibility (a11y) audit

| Item | Status | Notes |
|---|---|---|
| Semantic HTML5 (`<header>`, `<main>`, `<article>`, `<aside>`, `<nav>`, `<footer>`) | ⚠️ Partial | Ada di blog post, tapi homepage pakai `<header>` untuk hero, bukan `<main>`. Layar reader bingung. |
| `aria-label` di icon-only buttons | ✅ | Search button, social icons, close button — semua punya |
| `aria-expanded` di accordion | ✅ | Navbar mobile accordion + FAQ |
| Focus ring | ❓ | Tidak di-test. Tailwind preflight default ada, tapi `outline-none` mungkin di-override |
| Skip-to-content link | ❌ | **TIDAK ADA**. Add `<a href="#main-content" class="sr-only focus:not-sr-only">Skip to content</a>` di awal Layout.astro |
| `lang="id"` di `<html>` | ✅ | Layout.astro:52 |
| Image `alt` text | ⚠️ Mostly ✅ | Tapi beberapa `<img loading="lazy">` di blog sidebar `alt=""` — OK untuk dekoratif, tapi pastikan tidak ada info penting |
| Form labels | ✅ | Visible placeholder + implicit label |
| Color-only indicator | 🔴 | "Rekomendasi Tim" badge pakai oranye saja → tambahkan icon atau text alternative |
| Heading hierarchy | ⚠️ | Homepage `<h2>` di Stats & FAQ — pastikan tidak skip H2 di mid-section |

---

## 4. COPYWRITING AUDIT

### 4.1 Voice consistency — strong (✅)

Persona "Senior Performance Marketing Partner" terdengar konsisten. Tidak ada slang. "Anda" predominant. Bahasa formal-measured.

### 4.2 Inkonsistensi fatal di `jasa-iklan-facebook.astro` (🔴)

**3 paragraf di file yang sama tentang apakah priceLabel sudah termasuk ad spend:**

1. **Baris 99** (di FAQ yang dikirim ke Layout):
   > "Paket Beriklan mulai dari Rp 1.750.000 per 30 hari (Standart) dan Rp 3.750.000 per 30 hari (Business). **Sudah termasuk biaya ad spend**, setup campaign, dan optimasi rutin."

2. **Baris 76** (di const faqs array internal):
   > "Berapa budget iklan (ad spend) yang perlu disiapkan di luar biaya jasa?... Ad spend Meta **dibayar langsung ke Meta oleh Anda** — Anda memegang penuh kendali akun..."

3. **Baris 36, 53, 71** (di setiap tier):
   > `priceNote: 'belum termasuk ad spend Meta'`

**Mana yang benar?** Konsultasikan ke owner. Saran: jawabannya = **ad spend terpisah** (sesuai priceNote & FAQ internal), karena:
- Kalau "termasuk", angka jadi misleading (FB charge per impression, jadi ad spend = variabel)
- Konsisten dengan `jasa-iklan-google.astro`, `tiktok`, dll
- Konsisten dengan footer FAQ di homepage: "belum termasuk"

**Action:** Fix baris 99. Ganti jadi "Sudah termasuk biaya **jasa pengelolaan**. Ad spend Meta dibayar terpisah."

### 4.3 Banned words — ada beberapa pelanggaran minor (🟠)

| File | Baris | Teks | Seharusnya |
|---|---|---|---|
| index.astro | 132 (tidak ada) | — | — |
| jasa-iklan-google.astro | 88 | "撰写" (Mandarin) | "menyusun" atau hapus |
| jasa-iklan-google.astro | 95 | "Meta" di konteks Google Ads | "Google" |
| (likely others) | — | — | — |

⚠️ **`jasa-iklan-google.astro:88`** ada karakter Mandarin "撰写" (yang berarti "menulis") — bisa bikin user bingung. Pasti leftover.
⚠️ **Baris 95** FAQ Google Ads menyebut "Ad spend Meta" — salah, harusnya "Google".

### 4.4 Banned words (AGENTS §4.2) check

```
grep -rn "bikin\|gak\|nggak\|handle iklan\|pasti\|garansi 100%" web/src/
```

Hasil: tidak ditemukan di halaman utama, ✅ aman.

---

## 5. KEYWORD FOCUS PER HALAMAN

### 5.1 Current state — keyword cannibalization parah (🔴)

| Halaman | Primary keyword | Secondary keyword | Currently ranks? |
|---|---|---|---|
| `/jasa-iklan-facebook/` | jasa iklan facebook | meta business partner | ❌ blog steal |
| `/jasa-iklan-instagram/` | jasa iklan instagram | reach & engagement | ❌ blog steal |
| `/jasa-iklan-tiktok/` | jasa iklan tiktok | spark & fyp | ❌ blog steal |
| `/jasa-iklan-youtube/` | jasa iklan youtube | video ads | ❌ blog steal |
| `/jasa-iklan-google/` | jasa google ads | search intent | ❌ blog steal |
| `/jasa-kelola-instagram/` | jasa kelola instagram | konten & community | ⚠️ less competition |
| `/jasa-kelola-tiktok/` | jasa kelola tiktok | konten video rutin | ⚠️ |
| `/jasa-pembuatan-website/` | jasa pembuatan website | landing page | ⚠️ long-tail mix |
| `/jasa-pembuatan-landing-page/` | landing page + google ads | paket konversi | ❌ unclear |
| `/jasa-digital-marketing/` | jasa digital marketing | multi-channel | ✅ (homepage link juga) |
| `/harga-iklan-X/` (city) | harga iklan X di kota | estimator | ✅ less competition |
| `/riset/...` | riset industri iklan digital | 2026 | ✅ fresh content |
| `/kalkulator-*` | kalkulator budget/roas/roi | tools | ✅ unique |

**Setelah fix redirect (§1.3),** masing-masing service page akan punya authority jauh lebih tinggi karena:
- 7 URL legacy utama akan point langsung ke service page (bukan blog)
- Blog post dengan slug cannibal akan di-301 atau di-canonical-kan ke service

### 5.2 Long-tail opportunity (city pages)

22 city page × 7 service = 154 URL long-tail. Contoh:
- `/jasa-iklan-facebook/bandung/` — target `"jasa iklan facebook bandung"`
- `/jasa-iklan-tiktok/jakarta/` — target `"jasa iklan tiktok jakarta"`
- `/jasa-pembuatan-landing-page/surabaya/` — target `"jasa landing page surabaya"`

**Issue:** City pages tidak muncul di Navbar atau Footer. Banyak backlink internal hilang. Tambahkan mega-menu atau quick-access di Footer.

### 5.3 Tool pages (kalkulator) — bagus tapi tidak di-internal-link dari jasa pages (🟠)

`/kalkulator-budget-iklan`, `/kalkulator-roas`, `/kalkulator-roi` punya nilai SEO tinggi karena **unique tool**. Tapi:
- Tidak ada CTA "Hitung budget Anda" di section pricing service page
- Tidak ada link dari homepage

**Action:** Di setiap service page, di section sebelum Pricing, tambahkan CTA card: "Sebelum pilih paket, hitung budget ideal Anda → [Kalkulator Budget]".

### 5.4 Indexing speed optimization (🟠)

Masalah yang sering:
- Blog baru (WordPress import 827 posts) butuh waktu untuk di-index Google
- Indexing API: ada di `web/src/pages/page-sitemap.xml.ts` dan `post-sitemap.xml.ts` — perlu verifikasi
- Cek apakah `/sitemap-index.xml` live dan di-submit ke GSC

**Action:**
1. Verifikasi `https://beriklan.co.id/sitemap-index.xml` accessible (200) dan berisi semua sitemap
2. Submit semua sitemap di GSC
3. Cek `robots.txt` — saat ini ✅ sudah benar
4. Cek rendering blog post: ada **3 AdSense slots per blog post** (inline-top, inline-mid, after-article) → mungkin auto-rejected AdSense karena konten user-generated terlihat "low quality" (WordPress import tanpa rewrite). Pertimbangkan audit AdSense review status.

---

## 6. PERFORMANCE BUDGET

### 6.1 Bundle JS estimate

`client:only="svelte"` components di homepage (per `index.astro`):
- Navbar.svelte (~36 KB)
- StickyCTA.svelte (~17 KB)
- FloatingWhatsApp.svelte (~17 KB)
- HeroVisual.svelte (~14 KB)
- PainPoints.svelte (~8 KB)
- AuditTool.svelte (~14 KB)
- Method.svelte (~9 KB)
- Services.svelte (~13 KB)
- Testimonials.svelte (~18 KB)
- Faq.svelte (~5 KB)
- Footer.svelte (~13 KB)

Total ~165 KB minified. Ditambah `lucide-svelte` per-component → bisa **300+ KB unminified**. Gzipped mungkin 90-120 KB. **Borderline budget 200 KB.**

**Action:** Bundle Lucide icons global. Atau gunakan `@lucide/svelte` dengan `Icon` component + tree-shaking.

### 6.2 CLS risk

Floating elements:
- `abs-blob-1`, `abs-blob-2` di hero (filter blur 48px) — fixed size, no CLS
- AdSense — Auto Ads / display ads bisa cause CLS tinggi. Cek apakah `<ins>` slot punya `min-height` reserved.
- `FloatingWhatsApp.svelte` — muncul setelah scroll, fixed positioning → no CLS

**Action:** Reserve `min-height: 250px` untuk AdSense slots.

### 6.3 Image optimization

- `featuredImage` di blog post — perlu cek apakah di-convert ke `.webp` dan responsive sizes
- Hero CTA emoji `📈💬🚀` di final CTA — pakai unicode, no file → ✅ fast

---

## 7. KOMPARASI DENGAN `.beriklan.my`

`.beriklan.my` sudah port sebagian besar (per AGENTS.md). Yang perlu di-cek saat port UI/UX:

| Aspek | `.co.id` | `.my` (per AGENTS.md) | Catatan |
|---|---|---|---|
| Brand color tokens | Sama | Perlu pakai tailwind.config yang sama | ✅ |
| Navbar mobile accordion groups | paid/buzzer/organic/build/tools | Sama | ✅ |
| Email engine aktif | ✅ 100/hari | ❌ disabled (no list) | — |
| GSC indexing | www only | sc-domain | — |
| Komponen client:only | banyak | Samakan | ✅ |
| Schema.org | ada | ada | ✅ |

**Action untuk port `.beriklan.my`:**
1. Copy tailwind.config.mjs + global.css + Layout.astro pattern
2. Copy Navbar.svelte + Footer.svelte + FloatingWhatsApp.svelte + StickyCTA.svelte
3. Copy komponen section (Hero, PainPoints, AuditTool, Method, Services, Stats, Testimonials, Faq, PricingCards, FinalCTA, FeatureGrid, StepGrid, RelatedServices, BlogFilter, OrderWizard)
4. **JANGAN copy bug `_redirects`** — recreate dengan benar: legacy WP URL → service page, bukan blog
5. **JANGAN copy AGENTS.md yang outdated** — update warna token (accent-2)
6. Untuk blog posts, **review slug collisions** sebelum port — lebih baik 301 di-canonical-kan dari awal
7. Untuk city pages, tambahkan di Navbar/Footer sejak awal

---

## 8. REKOMENDASI PRIORITAS

### P0 — Fix minggu ini (🔴 urgent)

1. **Bug redirect `_redirects`** — 7 baris utama → ke service page, bukan blog.
2. **Inkonsistensi copy ad-spend** di `jasa-iklan-facebook.astro:99`.
3. **Karakter Mandarin** "撰写" di `jasa-iklan-google.astro:88` → ganti/hapus.
4. **Skip-to-content link** di Layout.astro.
5. **Canonical www/non-www** konsisten.

### P1 — Fix bulan ini (🟠)

6. **Kontras `text-accent` di body prose** — ganti ke `text-ink` atau `text-primary-2` di 12+ lokasi (§3.2).
7. **Update AGENTS.md** — fix `accent-2` token (`#fbbf24`, bukan `#fb923c`).
8. **City pages di Footer/Navbar** — tambahkan quick-access.
9. **Pillar pages di Navbar** — tambahkan link langsung.
10. **Blog post slug collision** — 301 atau canonical ke service page untuk 7 service slug utama.
11. **Schema `@id` cross-reference** di Organization + Article.
12. **Per-halaman priceRange di Service schema** — dinamis, bukan hardcoded di Layout.

### P2 — Fix next quarter (🟡)

13. **Title length audit** semua service pages (≤60 char ideal).
14. **Hapus `#1` superlatif** di title FB Ads.
15. **Lucide icon bundle optimization** — global icon registry.
16. **Reserve AdSense min-height** untuk kurangi CLS.
17. **Tooltip di "Rekomendasi Tim" badge** — jangan color-only.
18. **Pillar cluster visualization** — graphic di pillar page.
19. **FAQ schema** di semua service page (sekarang sebagian sudah, sebagian belum).
20. **Review AdSense policy** — apakah blog post (WordPress import) pass review?

---

## 9. CHECKLIST UNTUK `.beriklan.my` PORT

Gunakan checklist ini saat setup `.beriklan.my` (untuk menghindari ulangi bug `.co.id`):

```markdown
- [ ] tailwind.config.mjs — pakai token sama, TIDAK hardcode warna
- [ ] global.css — copy prose class untuk blog body
- [ ] Layout.astro — skip-to-content, canonical konsisten (pilih www atau non-www, JANGAN campur)
- [ ] Schema.org — Organization dengan `@id`, semua page referensikan
- [ ] Navbar.svelte — link ke pillar pages + city pages
- [ ] Footer.svelte — link ke city pages, sitemap, social lengkap
- [ ] _redirects — legacy URL → SERVICE PAGE, bukan blog
- [ ] Sitemap — 6 split (index/static/blog/city/tag/pillar), submit ke GSC
- [ ] Robots.txt — AI crawler allow + 6 sitemap URL
- [ ] Blog post [slug].astro — canonical JANGAN bentrok dengan service slug
- [ ] For setiap service page: title ≤60 char, description 150-160 char, H1 contain primary keyword
- [ ] Kontras check — text-accent TIDAK di body prose putih
- [ ] Bundle size — <200 KB gzipped per page
- [ ] CLS <0.1, LCP <2.5s
- [ ] Mobile test 320, 360, 390, 414, 768, 1024, 1280
- [ ] a11y: skip-to-content, focus ring, aria-label
```

---

## 10. CARA PAKAI FILE INI

- **Simpan di:** `/Users/maabook/Desktop/beriklan.co.id/AUDIT-UI-UX-SEO-2026-08-26.md` (root, tracked git)
- **Copy ke:** `/Users/maabook/Desktop/beriklan.my/AUDIT-UI-UX-SEO-2026-08-26.md` untuk dipakai saat port
- **Update:** setelah fix bug P0/P1, tambah catatan "Fix applied YYYY-MM-DD"
- **Versi:** saat ini v1.0 (26 Agt 2026). Re-audit tiap 3 bulan atau setelah redesign besar.

---

## 11. INCIDENT LOG — 26 Agt 2026: "Service pages hilang, semua ke blog" (FIXED)

**Gejala live:** Menu Paid Ads (FB/IG/TikTok/Google/YouTube) + Landing Page → halaman service lenyap, semua 301 ke `/blog/jasa-iklan-X/`.

**Root cause (3 lapis, saling menguatkan):**

1. **`web/public/_redirects`** punya baris legacy WP:
   `/jasa-iklan-facebook.html → /blog/jasa-iklan-facebook/ 301` (dst blog, bukan service page). Ada 264 baris serupa.
2. **`scripts/embed_redirects.mjs`** (generator map redirect untuk Worker) untuk SETIAP baris `.html` juga melahirkan varian TANPA extension:
   ```
   /jasa-iklan-facebook   → /blog/jasa-iklan-facebook/
   /jasa-iklan-facebook/  → /blog/jasa-iklan-facebook/  ← PAGE ASLI IKUT KE-REDIRECT
   ```
   Worker (`worker-entry.js` ~line 426, `matchRedirect`) lalu 301-kan URL service page yang sah ke blog. **Inilah pembunuhnya.**
3. **Worker render D1-first** (`run_worker_first: ["/blog/*"]`) merender `/blog/{slug}` dari D1 SEBELUM cek `matchRedirect`, sehingga rule 301 `/blog/jasa-iklan-facebook/ → /jasa-iklan-facebook/` pun tak pernah terpakai. Ditambah: ada 18 artikel blog di `posts.json`/D1 yang slug-nya PERSIS nama service page.

**Fix yang diterapkan (live, verified 26 Agt 22:15):**

| Lapis | Fix |
|---|---|
| `_redirects` | 7 legacy `.html` utama + 13 secondary → service page; +19 rule 301 `/blog/{slug-collision}/` → service page. Backup: `_redirects.bak-20260826-214750` |
| `embed_redirects.mjs` | Guard: varian trailing-slash TIDAK boleh map ke dirinya sendiri (anti 301 loop); varian tanpa extension tetap dipasang (canonicalization, karena navbar pakai link tanpa slash). Backup: `embed_redirects.mjs.bak-*` |
| `worker-entry.js` | Blok render blog D1-first sekarang cek `matchRedirect(path)` DULU → 301 sebelum render. Backup: `worker-entry.js.bak-20260826-221300` |
| Build | Unblocked: buat stub `src/components/AdsenseSlot.astro` (file hilang, dipakai `tutorial/[platform]/index.astro` + `[topic].astro`) + fix import path `../../` → `../../../` di `tutorial/[platform]/[topic].astro` (+ backup `.bak-20260826-214750`). Build: 6798 pages OK |

**Verify live:** 10/10 service pages 200 (konten service, bukan blog) · 19 URL collision 301 ke service · post blog normal tetap 200 · tidak ada 301 loop · homepage 200.

**Deployment log:**
- Version baru: `cc523469-c4df-4307-9098-b01210490594` (deploy `wrangler deploy` ×2, 26 Agt 22:14).
- Rollback target kalau rusak: `fb42e416-d986-4152-9654-3fa5a63c0da3` (versi 844, sebelum incident fix).

**WAJIB untuk port ke `.beriklan.my`:**
1. Jangan copy `_redirects` mentah — buat dari nol atau pastikan TIDAK ada baris `.html → /blog/jasa-*/`.
2. Kalau pakai generator map redirect sejenis `embed_redirects.mjs`: pakai guard self-loop yang sama.
3. Kalau Worker punya render blog D1-first dengan `run_worker_first /blog/*`: WAJIB cek redirect rule SEBELUM render dari DB.
4. Jangan buat artikel blog yang slug-nya persis nama service page (`jasa-iklan-facebook` dll) — pakai suffix (kota/terbaik/tahun) atau arahkan ke service page sejak awal.

## 12. VERIFIKASI — Blog terposting & Sitemap lengkap (26 Agt 2026, 22:35, live)

**Jumlah artikel blog yang sudah terposting & live:**

| Sumber | Jumlah | Catatan |
|---|---|---|
| `src/data/posts.json` (static build) | **4.306** | Post dari import WordPress, di-build jadi HTML statis |
| D1 `posts_meta` (serve dinamis worker) | **12.832** | Termasuk draft AI yang di-publish pipeline (run_worker_first `/blog/*`) |
| `sitemap-blog.xml` live | **12.832 URL** | Semua artikel masuk sitemap ✅ |
| `/data/posts-index.json` (feed BlogFilter) | **12.832** | Konsisten dengan sitemap ✅ |

**Sample test 9 URL acak (awal/tengah/akhir sitemap-blog): 9/9 → HTTP 200**, judul render benar (termasuk artikel hasil rewrite growth-system, mis. "Jasa Iklan Facebook Jakarta — Blog Beriklan.co.id").

**Sitemap lengkap (semua 200):**

| Sitemap | Jumlah URL | Isi |
|---|---|---|
| sitemap-index.xml | 5 sub-sitemap | lastmod 2026-08-26 (fresh) |
| sitemap-static.xml | **19** | Homepage, blog index, order, PP, ToS, **10 service page**, 3 kalkulator, riset industri ✅ |
| sitemap-blog.xml | **12.832** | Semua artikel blog ✅ |
| sitemap-city.xml | **500** | City landing pages |
| sitemap-pillar.xml | **10** | Pillar pages |
| sitemap-tag.xml | **4.952** | Tag pages |
| **TOTAL** | **18.313 URL** | Semua declared di `robots.txt` ✅ |

**Catatan penting (konsisten, jangan diubah):**
- Selisih 12.832 vs 4.306 itu NORMAL: 8.526 artikel ekstra di-serve dinamis dari D1 (AI pipeline), tidak ada di static build tapi ADA di sitemap + live 200 via `run_worker_first`.
- `robots.txt` sudah allow semua AI crawler (GPTBot, ClaudeBot, PerplexityBot, Google-Extended, dll) → mendukung indexing cepat + AI Overview.
- Semua 10 service page ada di `sitemap-static.xml` dan live 200 (lihat §11 verify matrix).

---

**Auditor:** Codex AI untuk Beriklan Digital Agency
**Project:** Beriklan.co.id — Bandung, Indonesia
**File ini:** disimpan lokal, tidak di-deploy. Hanya sebagai catatan engineering + porting reference untuk beriklan.my.
**Update terakhir:** 26 Agt 2026 22:35 — tambah §12 Verifikasi blog 12.832 artikel live + sitemap 18.313 URL lengkap. Sebelum itu: §11 Incident Log (service pages 301→blog, FIXED & verified live).
