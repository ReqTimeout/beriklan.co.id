# PREMIUM REDESIGN PLAN — beriklan.co.id
## Haloka Tech Foundation × Improved for Performance Marketing Agency

| Field | Value |
|---|---|
| **Versi** | 1.0 · 2026-07-11 |
| **Status** | PLANNING — belum production |
| **Constraint deploy** | Local first. Domain `beriklan.co.id` **tidak live** sampai design di-approve |
| **Reference tech** | `haloka-landing` (Astro 5 + Svelte 5 + Tailwind) |
| **Source of truth copy** | `COPY-BIBLE.md` (voice) + **`PER-PAGE-REDESIGN-PLAN.md`** (SEO copy & section plan per page) |
| **Source of truth pricing** | **Harga live di beriklan.co.id** (bukan invent tier 2,5jt/5jt) — lihat `PER-PAGE-REDESIGN-PLAN.md` §A.4 |
| **Source of truth SEO URL** | `url_classification.csv` (~843 URL) |
| **WP export** | `jasadigitalmarketing.WordPress.2026-06-23.xml` (~1.599 post items, 90MB) |
| **Per-page blueprint** | `PER-PAGE-REDESIGN-PLAN.md` |

---

## 0. EXECUTIVE SUMMARY

### 0.1 Apa yang kita kerjakan

Redesign total **beriklan.co.id** dari WordPress marketing site lama menjadi **modern performance marketing agency site** dengan:

1. **Tech stack disalin dari Haloka** (Astro + Svelte islands + Tailwind) — terbukti cepat, interaktif, dan nyaman di-maintain.
2. **Diperbaiki & diperluas** untuk konteks agency multi-layanan (bukan single-product SaaS seperti Haloka).
3. **SEO-first migration** dari ~800+ URL existing tanpa bunuh ranking.
4. **Voice corporate** ("Senior Performance Marketing Partner") dari `COPY-BIBLE.md`.
5. **Local only** sampai Anda approve design.

### 0.2 Kenapa Haloka jadi foundation (bukan Next.js / WordPress lagi)

| Aspek | WordPress sekarang | Haloka pattern | Keputusan untuk Beriklan |
|---|---|---|---|
| Speed / Core Web Vitals | Berat, plugin bloat | Zero-JS by default + islands | **Pakai Haloka pattern** |
| Interaktif hero | Static image | Svelte islands (`client:visible`) | **Copy + improve** (Ads Dashboard, bukan Chat) |
| Multi-page SEO | Banyak page tapi thin | Landing 1 page | **Improve**: multi-route + Content Collections |
| Content ops | WP admin | Hardcoded di components | **Improve**: MDX + Sanity optional |
| Deploy | cPanel / mixed | Static + nginx | **Cloudflare Pages** (staging) → production setelah approve |
| Bundle JS | 300KB+ | Ringan per-island | Target **< 100KB** homepage |

### 0.3 Positioning bisnis (lock ini dulu)

| Item | Lock |
|---|---|
| **Brand** | Beriklan Digital Agency |
| **Persona** | Senior Performance Marketing Partner (8+ tahun, 50+ brand) |
| **Offer inti** | Jasa digital marketing terukur: Meta Ads, Google Ads, TikTok, YouTube, social management, website/LP |
| **Promise** | Sistem pertumbuhan terukur (ROAS/CPA), akses dashboard penuh, tanpa hidden fee |
| **Primary CTA** | Konsultasi gratis 15 menit (WhatsApp + form) |
| **Secondary CTA** | Lihat layanan / Lihat paket |
| **Geo** | Indonesia (HQ Bandung), local SEO multi-kota |
| **Differentiator vs Haloka** | Agency services multi-platform + proof + blog authority — **bukan** SaaS trial |

### 0.4 Apa yang SUDAH ADA (jangan buang)

| Asset | Lokasi | Dipakai untuk |
|---|---|---|
| Full copy homepage + 10 service + about + contact + blog | `COPY-BIBLE.md` | Semua page copy |
| URL migration matrix | `url_classification.csv` | Redirect / rewrite / 410 / local SEO |
| WP WXR export | `*.xml` | Blog migration → MDX |
| SEO auto-pilot playbook | `SEO-PLAYBOOK.md` | IndexNow, freshness, worker cron |
| Scaffold Astro+Svelte (partial) | `~/Pictures/beriklan-web/beriklan-site` | Base code — **pindah/merge ke workspace ini** |
| Plan desain v2/v3 | `~/Pictures/beriklan-web/REDESIGN-*.md` | Visual direction (PULSE) |
| Logo | `logoweb.webp` | Brand mark |
| Haloka reference | `~/Desktop/haloka-landing/haloka-landing` | Pattern UI/UX islands |
| Sanity project | `account.md` (project `beriklan` / `2pdculh3`) | CMS opsional phase 2 |
| Cloudflare account | `account.md` | Pages + Worker (staging only dulu) |

> ⚠️ **Security note:** `account.md` berisi API token plaintext. **Jangan commit ke git.** Rotate token Cloudflare + Sanity sebelum push public. Simpan di `.env` / secrets manager.

---

## 1. ANALISIS REFERENSI: HALOKA (apa yang di-copy)

### 1.1 Stack Haloka (as-is)

```
Astro 5.x
├── @astrojs/svelte  → interactive islands
├── @astrojs/tailwind
├── Svelte 5
├── Tailwind 3 (theme extend di tailwind.config.mjs)
└── TypeScript
```

**Struktur:**
```
src/
├── pages/index.astro          # single landing page
├── layouts/Layout.astro       # SEO meta + JSON-LD + fonts
├── components/*.svelte        # ALL sections = Svelte islands
├── styles/global.css
└── assets/
```

**Homepage section order (Haloka):**
1. `Navbar` (`client:load`)
2. `StickyCTA` (`client:idle`)
3. Hero (static Astro + `ChatSimulator client:visible`)
4. `TrustBadges`
5. `PainPoints` (animated drama + ROI calculator embedded)
6. `Features`
7. `InteractiveTutorial` (storytelling steps)
8. `SocialProof`
9. `PricingInteractive`
10. `FinalCTA`
11. `Faq`
12. Footer (minimal)

**UX patterns yang bagus di Haloka:**
- Hero 2-kolom: copy kiri + **live product demo** kanan
- Gradient mesh + `animate-gradient` background
- Badge live pulse ("Solusi 2026")
- Primary CTA shimmer + secondary low-friction
- Pain section yang **visual + interactive** (bukan cuma text card)
- Pricing yang **reactive** (slider → recommended package)
- Sticky mobile CTA
- JSON-LD Organization + SoftwareApplication
- Bahasa Indonesia natural, fokus conversion

**Kelemahan Haloka untuk context Beriklan (yang harus di-improve):**
| Gap Haloka | Improve untuk Beriklan |
|---|---|
| Single-page only | Multi-page: 10 layanan + blog + kota + about + paket |
| Semua section full Svelte (lebih banyak JS) | Static `.astro` default; Svelte **hanya** island interaktif |
| Font Google (FOUT risk) | Self-host Geist + Instrument Serif |
| Tailwind v3 config | Tailwind v4 `@theme` tokens |
| Copy playful "Kaka/Juragan" | Corporate voice "Anda/kami" (COPY-BIBLE) |
| Product = WhatsApp AI SaaS | Services = performance ads agency |
| Demo = ChatSimulator | Demo = **Live Ads Command Center** (SVG dashboard) |
| Pricing 3 SaaS packages | Hybrid: retainer monthly + project (website/LP) |
| Minimal SEO surface | Full SEO: service pages, blog, local/kota, schema matrix |
| No blog | Blog dari WP migration + freshness engine |
| No form multi-step | Order form 5-step + WhatsApp deep-link |
| No CMS | Content Collections + Sanity optional |

### 1.2 Pattern island hydration (COPY ini)

```astro
<!-- Critical above-the-fold: client:load -->
<Navbar client:load />

<!-- Near-fold interactive: client:idle -->
<StickyCTA client:idle />

<!-- Below-fold: client:visible (lazy hydrate) -->
<PainPoints client:visible />
<PricingCalculator client:visible />
```

**Aturan Beriklan (lebih ketat dari Haloka):**
- Default component = **`.astro` static** (0 KB JS)
- `.svelte` hanya jika butuh state, animation spring, form, atau live demo
- Max 4–6 hydrated islands di homepage
- Sisanya pure CSS animation / View Transitions

---

## 2. VISI PRODUK BERIKLAN (bukan clone Haloka visual)

### 2.1 One-liner

> Website agency performance marketing yang **menunjukkan sistem kerja** (dashboard, funnel, ROAS) — bukan cuma bilang "kami jago".

### 2.2 Design direction: "Pulse Command" (gabungan plan v2 + v3)

| Layer | Arah |
|---|---|
| **Mood** | Confident, measured, premium — bukan playful SaaS chatty |
| **Typography** | Instrument Serif (display moments) + Geist (UI/body) + Geist Mono (metrics) |
| **Color** | Paper `#FAFAF7` / Ink `#0A0A0F` + Brand `#0040FF` + accents per channel (Meta violet, TikTok magenta, Google blue, YouTube red-orange) |
| **Hero signature** | Animated SVG **Ads Command Center** (ROAS ticker, campaign cards, funnel bars) — analog ChatSimulator Haloka |
| **Motion** | Spring physics Svelte + View Transitions; hormati `prefers-reduced-motion` |
| **Density** | Editorial + data (magazine × dashboard) |

### 2.3 Category color system (service pages)

| Category | Services | Accent |
|---|---|---|
| `paid-ads` | FB, IG, TikTok, Google, YouTube | Brand blue `#2563EB` / per-platform tint |
| `organic` | Kelola IG, Kelola TikTok | Violet `#8B5CF6` |
| `build` | Website, Landing Page | Orange `#F97316` |
| `umbrella` | Digital Marketing | Sky `#0EA5E9` |

---

## 3. TECH STACK FINAL (Haloka + improvements)

```jsonc
{
  "framework": "Astro 5+ (SSG default; hybrid SSR only if needed for forms)",
  "ui_islands": "Svelte 5 (runes)",
  "styling": "Tailwind CSS v4 (@theme di CSS)",
  "content": "Astro Content Collections (MDX + Zod)",
  "cms_optional": "Sanity (project beriklan / 2pdculh3) — phase 2",
  "forms": "Astro Actions + WhatsApp deep-link fallback",
  "images": "astro:assets + sharp",
  "seo": "@astrojs/sitemap + custom JSON-LD + IndexNow Worker",
  "analytics": "GA4 + optional PostHog (events CTA/form)",
  "deploy_staging": "Cloudflare Pages (preview URL)",
  "deploy_prod": "Hanya setelah approval design (beriklan.co.id)",
  "package_manager": "pnpm",
  "node": ">= 22"
}
```

### 3.1 Integrasi yang ditambah (di luar Haloka)

| Fitur | Implementasi | Prioritas |
|---|---|---|
| Multi-page routing | Astro file-based pages | P0 |
| Blog + migration | WXR → MDX script | P0 |
| Redirect matrix | `public/_redirects` / CF rules dari CSV | P0 |
| Local SEO kota | Programmatic `/jasa-*-{kota}` atau `/kota/{slug}` | P1 |
| Audit lead magnet | Multi-step form 7Q (COPY-BIBLE §11) | P1 |
| Sanity CMS | Optional editor non-dev | P2 |
| SEO Worker cron | Freshness + IndexNow (dari SEO-PLAYBOOK) | P1 post-launch |
| Turnstile | Protect form bots | P1 |
| OG image | Satori endpoint `/og/[...slug].png` | P1 |

### 3.2 Yang TIDAK kita bawa dari plan Next.js / Agency OS lama

- ❌ Next.js App Router sebagai frontend public site
- ❌ Headless WordPress runtime (cukup one-shot export)
- ❌ Three.js / R3F (berat; diganti pure SVG)
- ❌ Direct connection ke `agency.db` (leads via form webhook saja)
- ❌ Live production DNS cutover sebelum approval

---

## 4. INFORMATION ARCHITECTURE

### 4.1 Site map (core)

```
/                                 Homepage
/jasa-digital-marketing           Umbrella service
/jasa-iklan-facebook
/jasa-iklan-instagram
/jasa-iklan-tiktok
/jasa-iklan-google
/jasa-iklan-youtube
/jasa-kelola-instagram
/jasa-kelola-tiktok
/jasa-pembuatan-website
/jasa-pembuatan-landing-page
/paket                            Pricing full
/order                            Multi-step order / inquiry
/tentang
/kontak
/studi-kasus                      List
/studi-kasus/[slug]
/blog                             Index + filter
/blog/[...slug]                   Preserve legacy paths where possible
/blog/kategori/[category]
/blog/page/[page]
/kamus                            Glossary (COPY-BIBLE §10) — P2
/audit                            Free audit tool (COPY-BIBLE §11) — P1
/kota/[kota]                      Local hub — P1
/jasa-[service]-[kota]            Programmatic local — P1 (dari KEEP_LOCAL)
/privacy, /terms                  Legal
/404
/rss.xml
/sitemap-index.xml
```

### 4.2 URL migration strategy (dari `url_classification.csv`)

| Status | Count (approx) | Action |
|---|---:|---|
| `KEEP_LOCAL` | ~408 | Build programmatic local pages ATAU 301 ke hub kota + canonical cluster |
| `REWRITE` | ~372 | Migrate content → `/blog/{slug}` + 301 dari `.html` lama |
| `MERGE` | ~50 | 301 ke canonical (hapus year-variant 2025 dll.) |
| `REMOVE_410` | ~13 | Soft-delete irrelevant (core drill / lab equipment) → **410 Gone** |

**Rules:**
1. Service money pages (`/jasa-iklan-*`) **tetap path sama** (tanpa `.html`).
2. Blog: prefer clean `/blog/slug` + 301 dari `/{slug}.html`.
3. Generate `_redirects` otomatis dari CSV via script `scripts/generate-redirects.ts`.
4. Setelah cutover: submit sitemap + IndexNow; monitor GSC coverage 30 hari.

### 4.3 Primary conversion paths

```
Awareness (blog/local SEO)
    → Service page
        → /paket OR /order OR WhatsApp
            → Lead di CRM/email/WA
                → Konsultasi 15 menit
```

Secondary:
```
Homepage → Audit tool → Thank you + WA → Sales
```

---

## 5. HOMEPAGE BLUEPRINT (Haloka structure × Beriklan content)

Mirip **urutan psikologis** Haloka, beda **konten & demo**.

| # | Section | Pattern Haloka | Implementasi Beriklan | Island? |
|---|---|---|---|---|
| 0 | Navbar | sticky + CTA | Logo + Layanan mega + Paket + Blog + CTA | Svelte `client:load` (mobile menu) |
| 1 | Sticky CTA | mobile bar | "Konsultasi Gratis" → WA | Svelte `client:idle` |
| 2 | Hero | copy + ChatSimulator | copy COPY-BIBLE §4.1 + **HeroScene Ads Dashboard** | Dashboard Svelte `client:visible` |
| 3 | Trust strip | badges | Logo client + partner Meta/Google + stats micro | Astro + CSS marquee |
| 4 | Pain | PainPoints drama | 3 pain cards §4.2 + optional **Ad Waste Calculator** | Calculator Svelte |
| 5 | Method | Features | Bento 6-step §4.3 | Astro + ScrollReveal |
| 6 | Services | — (Haloka product) | 9–10 service cards §4.4 | Astro + TiltCard optional |
| 7 | How it works | InteractiveTutorial | Process 4 steps §4.6 horizontal/stepper | Svelte `client:visible` |
| 8 | Social proof | SocialProof | Testimonial marquee §4.7 + case highlight | Astro |
| 9 | Stats | — | NumberTicker 4 metrics §4.5 | Svelte |
| 10 | Pricing | PricingInteractive | 3 tiers teaser §4.8 + link `/paket` | Svelte calculator optional |
| 11 | FAQ | Faq | §4.9 accordion | Svelte |
| 12 | Final CTA | FinalCTA | §4.10 magnetic CTA | Astro + MagneticButton |
| 13 | Footer | minimal | Full: services, blog, legal, newsletter | Astro |

### 5.1 Hero — signature upgrade dari Haloka ChatSimulator

**`HeroScene.svelte` = Live Ads Command Center**

Panel animasi berisi:
1. Header: "Campaign Live · Meta + Google"
2. ROAS big number ticker (e.g. 4.2x)
3. Mini funnel: Impression → Click → Lead → Closing
4. 3 campaign rows (status green, spend, CPA)
5. Sparkline SVG naik
6. Toast notif: "Budget reallocated · CPA −18%"

**Kenapa ini pas:** Haloka show product (chat). Beriklan show **expertise system** (performance ops). User langsung "ngeh" ini agency yang ngerti data.

### 5.2 Pain calculator (improve dari Haloka chat-load calculator)

Slider: **Ad spend bulanan** → estimasi waste jika ROAS 1.2x vs 4x  
Output: "Potensi efisiensi Rp X / bulan" + CTA konsultasi.

---

## 6. SERVICE PAGE TEMPLATE (10 pages)

### 6.1 Section order (uniform shell)

| Slot | Section | Source copy |
|---|---|---|
| S1 | Hero (H1 keyword + proof + CTA) | COPY-BIBLE §5.x |
| S2 | Pain (3 cards) | §5.x |
| S3 | Solution / What's included | §5.x |
| S4 | Process (4–5 steps) | §5.x |
| S5 | Features / deliverables grid | §5.x |
| S6 | Results band (metrics) | §5.x + stats.ts |
| S7 | Pricing snapshot (tiers) | §5.x / pricing.ts |
| S8 | Case study block | studi-kasus or anonymized |
| S9 | Comparison (DIY vs us / vs typical agency) | §5.x |
| S10 | FAQ + Related services + Final CTA | §5.x |

### 6.2 Data model (`content/services/*.mdx` atau `lib/data/services.ts`)

```ts
{
  slug: 'jasa-iklan-facebook',
  category: 'paid-ads',
  title, tagline, description, longDescription,
  startingPrice, bullets, pains, process, features,
  results, pricingTiers, faqs, related: string[],
  targetKeyword, secondaryKeywords: string[]
}
```

### 6.3 JSON-LD per service page

- `Service` + `Offer`
- `FAQPage`
- `BreadcrumbList`
- `Organization` (global layout)

---

## 7. FILE STRUCTURE TARGET

Workspace: `/Users/maabook/Desktop/beriklan.co.id/web/` (atau clone `webberiklan` ke sini)

```
web/
├── package.json
├── pnpm-lock.yaml
├── astro.config.mjs
├── svelte.config.js
├── tsconfig.json
├── public/
│   ├── favicon.svg
│   ├── logoweb.webp
│   ├── fonts/                 # self-hosted if not using fontsource
│   ├── _redirects             # generated from CSV
│   ├── robots.txt
│   └── llms.txt               # optional
├── scripts/
│   ├── wxr-to-mdx.ts          # WP → MDX
│   ├── generate-redirects.ts  # CSV → _redirects
│   ├── classify-url-report.ts
│   └── og-image.ts
├── src/
│   ├── content.config.ts
│   ├── content/
│   │   ├── blog/**/*.mdx
│   │   ├── services/**/*.mdx
│   │   └── case-studies/**/*.mdx
│   ├── styles/
│   │   ├── global.css         # @theme tokens
│   │   ├── prose.css
│   │   └── animations.css
│   ├── lib/
│   │   ├── cn.ts
│   │   ├── motion.ts
│   │   ├── seo.ts
│   │   ├── whatsapp.ts
│   │   ├── analytics.ts
│   │   ├── internal-links.ts
│   │   └── data/
│   │       ├── services.ts
│   │       ├── pricing.ts
│   │       ├── faqs.ts
│   │       ├── testimonials.ts
│   │       └── stats.ts
│   ├── actions/
│   │   ├── order.ts
│   │   ├── contact.ts
│   │   ├── audit.ts
│   │   └── newsletter.ts
│   ├── components/
│   │   ├── astro/             # static
│   │   ├── svelte/            # islands
│   │   │   ├── animations/
│   │   │   ├── sections/
│   │   │   ├── forms/
│   │   │   └── widgets/
│   │   └── icons/
│   ├── layouts/
│   │   ├── BaseLayout.astro
│   │   ├── PageLayout.astro
│   │   ├── ServiceLayout.astro
│   │   └── BlogLayout.astro
│   └── pages/                 # routes §4.1
└── workers/                   # Cloudflare SEO cron (post-launch)
    └── seo-cron/
```

**Bootstrap strategy:** copy/merge dari `~/Pictures/beriklan-web/beriklan-site` (sudah partial Phase 1) + pattern island dari Haloka, **bukan** scaffold dari nol.

---

## 8. DESIGN SYSTEM (tokens)

### 8.1 Color (Tailwind v4 `@theme`)

```css
@theme {
  --color-ink: #0A0A0F;
  --color-ink-muted: #5C5C66;
  --color-paper: #FAFAF7;
  --color-paper-soft: #F2F2EC;
  --color-line: #E5E5DD;

  --color-brand-500: #0040FF;
  --color-brand-glow: #4D7BFF;
  --color-acid: #C8FF1F;      /* success / growth */
  --color-flame: #FF5E1A;
  --color-magenta: #FF2D87;   /* TikTok vibe */
  --color-violet: #6E2EFF;
  --color-cyan: #00D4FF;

  --font-sans: "Geist", system-ui, sans-serif;
  --font-display: "Instrument Serif", Georgia, serif;
  --font-mono: "Geist Mono", ui-monospace, monospace;
}
```

### 8.2 Type scale

| Token | Size | Use |
|---|---|---|
| `text-mega` | clamp(6rem, 16vw, 14rem) | Signature moment only (1 per page max) |
| `text-display-hero` | clamp(3rem, 7vw, 5.5rem) | H1 homepage |
| `text-display-service` | clamp(2.5rem, 5vw, 4rem) | H1 service |
| `text-h2` | clamp(1.75rem, 3.5vw, 3rem) | Section titles |
| `text-body` | 1.0625–1.125rem | Body |

### 8.3 Motion tokens

Dari plan Astro-Svelte: springs `gentle/snappy/bouncy`, durations micro→reveal, easings outExpo.  
**Rule:** animasi harus **cerita** (ticker = we measure; funnel = we optimize), bukan dekorasi.

### 8.4 Component inventory (build priority)

**P0 animations:** MagneticButton, ScrollReveal, NumberTicker, TextReveal, TiltCard, Marquee  
**P0 widgets:** Navbar, Footer, WhatsAppFloat, StickyMobileCta, Faq accordion  
**P0 sections:** HeroScene, PainCalculator, ServiceGrid, ProcessStepper, PricingTeaser, FinalCta  
**P1:** ThemeToggle, OrderForm multi-step, PricingCalculator full, CaseStudy cards  
**P2:** CursorBlob, ConfettiBurst, horizontal process scroll, Kamus UI  

---

## 9. COPY & BRAND VOICE (lock)

Sumber: `COPY-BIBLE.md`

| Rule | Detail |
|---|---|
| Persona | Senior Performance Marketing Partner |
| Pronoun | **Anda** predominan; "kamu" max 1 warm moment di hero/pain |
| Kami | agency voice (bukan "kita") |
| Metrics | ROAS, CPA, CTR — explain first use |
| Banned | "elevate", "synergy", "game-changer", emoji spam, guarantee ROAS palsu |
| CTA primary | Konsultasi Gratis 15 Menit |
| Proof | 50+ klien, 8 tahun, avg ROAS ~4.2–4.5x (internal data — jujur, no fake) |

**Action:** Saat implementasi, copy di components **harus** di-pull dari COPY-BIBLE, bukan improvisasi casual ala Haloka.

---

## 10. SEO ARCHITECTURE

### 10.1 On-page

- Unique `title` ≤ 60 char, `description` ≤ 155
- Canonical absolute `https://beriklan.co.id{path}`
- OG 1200×630 per template
- H1 tunggal; heading hierarchy valid
- Internal link matrix: home ↔ services ↔ blog pillars ↔ kota hubs
- Image: WebP/AVIF, width/height, descriptive alt

### 10.2 Schema matrix

| Page type | Schema |
|---|---|
| Global | Organization, WebSite, SearchAction (optional) |
| Home | Organization + FAQPage |
| Service | Service, Offer, FAQPage, BreadcrumbList |
| Blog post | BlogPosting, BreadcrumbList |
| Case study | Article or CreativeWork |
| Local hub | LocalBusiness / Service area |
| FAQ sections | FAQPage |

### 10.3 Blog migration (Phase 5)

1. Parse WXR (90MB) → filter `post` publish only
2. Map categories/tags
3. Download images → `public/media/` or R2
4. Convert HTML → MDX, strip shortcodes
5. Frontmatter: title, slug, date, dateModified, excerpt, categories, wpLegacyUrl, noindex?
6. Quality gate: drop/noindex thin content, spam, irrelevant (align REMOVE_410 topics)
7. Redirects: old URL → new
8. Pagination + category archives

**Estimate effort:** script 1–2 hari + manual QA top 50 traffic posts (butuh GSC export).

### 10.4 Post-launch SEO automation (dari SEO-PLAYBOOK)

- Cloudflare Worker cron 2×/hari: IndexNow + sitemap ping
- Optional freshness engine (hati-hati: jangan manipulasi tanggal agresif di money pages)
- Rank tracker later (GSC API)

---

## 11. FORMS, LEADS, INTEGRATIONS

| Form | Fields | Backend |
|---|---|---|
| Contact | nama, WA, email, pesan | Astro Action → email (Resend/CF Email) + optional webhook |
| Order multi-step | bisnis, platform, budget, goal, kontak | Action + WA prefill message |
| Newsletter | email | Action / Mail provider |
| Audit 7Q | pertanyaan COPY-BIBLE §11 | Action → thank-you + scored tips |

**Fallback always:** deep-link WhatsApp `https://bit.ly/BeriklanWhatsApp` / `0811-919-328` dengan prefilled text.

**Bot protection:** Cloudflare Turnstile on forms.

**Analytics events:**
- `cta_click` (location, label)
- `form_start` / `form_step` / `form_submit`
- `wa_click`
- `service_card_click`
- `pricing_tier_select`

---

## 12. PERFORMANCE & A11Y TARGETS

| Metric | Target |
|---|---|
| Lighthouse Perf mobile | ≥ 95 |
| Lighthouse desktop | ≥ 98 |
| LCP | < 1.5s (4G mid) |
| CLS | < 0.05 |
| INP | < 200ms |
| Total JS homepage | < 100KB gzipped |
| Lighthouse A11y | ≥ 95 |
| Reduced motion | full support |

**Budget rules:**
- No Three.js
- Fonts: max 2 families, subset weights
- Hero video: avoid; SVG only
- Images: lazy below fold; priority LCP image only

---

## 13. DEPLOYMENT & ENVIRONMENT

### 13.1 Stages

| Stage | URL | When |
|---|---|---|
| Local | `http://localhost:4321` | Development continuously |
| Preview | Cloudflare Pages preview (`*.pages.dev`) | After Phase 2 homepage polish |
| Staging custom (optional) | `staging.beriklan.co.id` | After Phase 4 |
| Production | `beriklan.co.id` | **Hanya setelah written approval design** |

### 13.2 Local workflow

```bash
cd web
pnpm install
pnpm dev          # http://localhost:4321
pnpm build && pnpm preview
```

### 13.3 Env vars (never commit)

```
PUBLIC_SITE_URL=http://localhost:4321
PUBLIC_WA_NUMBER=62811919328
PUBLIC_GA_ID=
TURNSTILE_SITE_KEY=
TURNSTILE_SECRET_KEY=
SANITY_PROJECT_ID=2pdculh3
SANITY_DATASET=production
SANITY_API_TOKEN=   # server only
RESEND_API_KEY=     # or form webhook
```

### 13.4 DNS cutover checklist (later)

1. Freeze WP writes
2. Final redirect file
3. Lower TTL 24h before
4. Point CF Pages / proxy
5. Verify SSL, www → apex or reverse
6. Submit sitemap GSC
7. IndexNow batch
8. Monitor 404 & rankings 14 hari

---

## 14. PHASED ROADMAP (detail harian)

> Total estimasi: **18–22 hari kerja** (1 engineer full-time).  
> Parallel: copy QA + design review bisa overlap.

### PHASE 0 — Align & setup (0.5 hari)

**Goals:** Lock scope, clean secrets, scaffold repo.

- [ ] Approve positioning §0.3 + design direction §2
- [ ] Rotate tokens di `account.md`; pindah ke `.env`
- [ ] Init/clone `webberiklan` ke `beriklan.co.id/web`
- [ ] Merge scaffold dari `beriklan-site` (Pictures)
- [ ] `pnpm dev` hijau
- [ ] Document decision log di README

**Exit:** Dev server jalan, git remote set, secrets aman.

---

### PHASE 1 — Foundation (2–3 hari)

**Goals:** Design system + layout shell + SEO utils.

**Hari 1 — Scaffold harden**
- [ ] Astro config: site URL, integrations (svelte, mdx, sitemap, tailwind v4)
- [ ] Path aliases `@components`, `@lib`, `@layouts`
- [ ] `global.css` tokens + dark mode class strategy
- [ ] Fonts Geist + Instrument Serif
- [ ] `BaseLayout` + `PageLayout` + View Transitions
- [ ] `Navbar` + `Footer` + `Section` + `Container`

**Hari 2 — Motion + icons + data**
- [ ] `lib/motion.ts`, `lib/cn.ts`, `lib/whatsapp.ts`, `lib/seo.ts`
- [ ] Animation islands P0
- [ ] Service icons SVG set (10+)
- [ ] Hardcoded data: `services.ts`, `stats.ts`, `pricing.ts`, `faqs.ts`, `testimonials.ts`
- [ ] `JsonLd.astro` helpers

**Hari 3 — Actions + content schema**
- [ ] `content.config.ts` Zod schemas
- [ ] Astro Actions stubs (order, contact, newsletter)
- [ ] `robots.txt`, empty sitemap verify
- [ ] Story-less design QA page `/dev/ui` (optional) menampilkan tokens + components

**Exit checkpoint:** `/` shell renders with design tokens; Lighthouse skeleton > 90 empty.

---

### PHASE 2 — Homepage (3 hari) ← **design approval gate utama**

**Hari 4 — Hero + Trust + Pain**
- [ ] HeroScene Ads Command Center (SVG live)
- [ ] Copy §4.1 (adjust corporate register)
- [ ] Trust strip + marquee
- [ ] Pain 3 cards + Ad Waste Calculator

**Hari 5 — Method + Services + Process + Stats**
- [ ] Bento 6-step
- [ ] Service grid 9–10
- [ ] Process 4 steps
- [ ] NumberTicker stats band

**Hari 6 — Social + Pricing + FAQ + CTA + polish**
- [ ] Testimonials marquee
- [ ] Pricing teaser 3 tiers
- [ ] FAQ accordion
- [ ] Final CTA + sticky WA
- [ ] Responsive QA (375 / 768 / 1280 / 1440)
- [ ] Reduced motion pass
- [ ] Lighthouse homepage

**Exit checkpoint:**  
**→ Demo local ke user. FREEZE visual direction setelah approve.**  
Tidak lanjut mass page build sebelum approval.

---

### PHASE 3 — Service pages (4 hari)

**Hari 7 — Template + 2 pages**
- [ ] `ServiceLayout` + all S1–S10 slots
- [ ] `/jasa-iklan-facebook`, `/jasa-iklan-instagram` full copy

**Hari 8 — Paid ads remaining**
- [ ] TikTok, Google, YouTube

**Hari 9 — Organic + Build + Umbrella**
- [ ] Kelola IG/TikTok, Website, LP, Digital Marketing

**Hari 10 — Cross-link + schema + QA**
- [ ] Related services
- [ ] Category accent skins
- [ ] JSON-LD validate (Rich Results test)
- [ ] Internal links from home

**Exit:** 10 money pages live di local.

---

### PHASE 4 — Static conversion pages (3 hari)

**Hari 11 — `/paket` + `/order`**
- [ ] Full pricing + comparison matrix
- [ ] Multi-step order form + success state
- [ ] WA fallback message builder

**Hari 12 — `/tentang` + `/kontak` + `/studi-kasus`**
- [ ] About timeline 8 tahun
- [ ] Contact methods + form
- [ ] Case studies list (min 3–6 entries, anonymized OK)

**Hari 13 — Utility**
- [ ] 404 branded
- [ ] Legal stubs
- [ ] Breadcrumbs global
- [ ] Optional `/audit` MVP (7 questions)

**Exit:** Full core funnel tanpa blog.

---

### PHASE 5 — Content migration & local SEO (3–4 hari)

**Hari 14 — Pipeline**
- [ ] `wxr-to-mdx.ts` run on 90MB XML
- [ ] Image extract
- [ ] Import top priority HIGH rewrites first (~20–40)

**Hari 15 — Blog UI**
- [ ] Index, filter, pagination, single template
- [ ] Inline CTA mid-article
- [ ] Related posts

**Hari 16 — Redirects + local**
- [ ] `generate-redirects.ts` dari CSV
- [ ] KEEP_LOCAL strategy decision:
  - **Option A (recommended v1):** hub `/kota/{kota}` + service links  
  - **Option B:** full programmatic page per `jasa-x-kota` (lebih banyak index, lebih banyak maintain)
- [ ] Implement Option A or B
- [ ] MERGE 301s + REMOVE_410

**Exit:** Blog readable; redirect map generated; local SEO v1.

---

### PHASE 6 — Performance, SEO hardening, staging (2 hari)

**Hari 17 — Perf**
- [ ] Bundle visualizer
- [ ] Image pass
- [ ] Font subset
- [ ] Island audit (reduce client:* if over budget)
- [ ] Lighthouse CI all key routes

**Hari 18 — Staging + monitoring prep**
- [ ] Deploy Cloudflare Pages **preview** (bukan apex domain)
- [ ] Turnstile + form e2e
- [ ] GA4 events smoke
- [ ] Checklist approval final
- [ ] Prepare cutover runbook (not execute)

**Exit:** Staging URL siap review final. Production blocked.

---

### PHASE 7 — Production cutover (1 hari, **hanya setelah approve**)

- [ ] Written approval design + content
- [ ] DNS + redirects production
- [ ] GSC property verify + sitemap
- [ ] IndexNow
- [ ] 48h watch: 404, form, Core Web Vitals
- [ ] Enable SEO worker carefully

---

## 15. DEFINITION OF DONE (acceptance)

### Functional
- [ ] Homepage 12+ sections, copy dari COPY-BIBLE
- [ ] 10 service pages unique
- [ ] `/paket`, `/order`, `/tentang`, `/kontak`, `/studi-kasus`
- [ ] Blog index + posts migrated (priority set min; full later OK)
- [ ] Forms submit + WA fallback
- [ ] Redirect matrix applied for CSV statuses
- [ ] Mobile sticky CTA + WhatsApp float

### Quality
- [ ] Perf targets §12
- [ ] A11y keyboard + contrast AA
- [ ] No console errors
- [ ] Schema valid sample 5 pages
- [ ] Dark mode optional (nice-to-have; not blocker)

### Process
- [ ] Local demo approved
- [ ] Staging approved
- [ ] Secrets not in git
- [ ] Runbook cutover documented

---

## 16. RISK REGISTER

| Risk | Impact | Mitigation |
|---|---|---|
| Ranking drop setelah cutover | High | 301 map lengkap, preserve money URLs, GSC monitor |
| Scope creep "full programmatic 400 local pages" day-1 | High | Phase 5 Option A first |
| Design reject ulang (history v1/v2) | Medium | Phase 2 hard gate; 1 hero concept + 1 alt only |
| WXR 90MB build memory | Medium | Split content, lazy collections, build on 8GB+ machine |
| Astro Actions butuh adapter | Medium | SSG + serverless action on CF; or pure client→WA |
| Fake metrics / trust damage | High | Hanya klaim yang bisa di-backup; case anonymized |
| Secrets leak | High | Rotate tokens; `.gitignore` env; never paste in plan commits |
| Over-animation mobile lag | Medium | `client:visible`, reduced motion, max islands |

---

## 17. WORKSTREAM MATRIX (parallelizable)

| Track | Owner focus | Depends on |
|---|---|---|
| **A. Design system + homepage** | Visual + islands | Phase 0 |
| **B. Service templates** | Content structure | A tokens + data |
| **C. Forms + lead flow** | Conversion | Layout shell |
| **D. Migration scripts** | SEO continuity | CSV + WXR |
| **E. Deploy staging** | Infra | Build green |

Recommended serial critical path: **0 → 1 → 2 (approve) → 3 → 4 → 5 → 6 → 7**.

---

## 18. IMPROVEMENT BACKLOG (post v1)

1. Sanity Studio untuk non-dev edit blog/services  
2. Kamus digital marketing (glossary SEO)  
3. Full programmatic local pages Option B  
4. Client portal deep-link (Agency OS) — stats public only  
5. Multi-language EN  
6. A/B testing hero CTA  
7. Advanced case study microsites  
8. Interactive ROAS simulator full funnel  

---

## 19. QUICK START SETELAH PLAN DI-APPROVE

```bash
# 1. Scaffold / merge ke workspace
cd /Users/maabook/Desktop/beriklan.co.id
# prefer: clone webberiklan OR copy beriklan-site
cp -R ~/Pictures/beriklan-web/beriklan-site ./web
cd web

# 2. Env
cp .env.example .env   # isi PUBLIC_* only dulu

# 3. Dev
pnpm install
pnpm dev

# 4. Buka
open http://localhost:4321
```

**Urutan eksekusi pertama setelah approve plan:**
1. Phase 0 setup  
2. Phase 1 foundation  
3. Phase 2 homepage → **minta review Anda**  
4. Baru lanjut mass pages  

---

## 20. KEPUTUSAN YANG PERLU ANDA LOCK (sebelum coding massal)

| # | Keputusan | Rekomendasi |
|---|---|---|
| 1 | Design direction: Pulse Command (paper/ink + blue) vs blue-SaaS v2 | **Pulse Command** |
| 2 | Local SEO: hub kota (A) vs full pages (B) v1 | **A** |
| 3 | CMS day-1: hardcode+MDX vs Sanity | **MDX hardcode dulu; Sanity P2** |
| 4 | Dark mode day-1? | **Optional** — light-first |
| 5 | Case study: real nama vs anonymized | **Anonymized** sampai ada izin klien |
| 6 | Primary contact: WA only vs form+WA | **Form + WA** (form for tracking) |
| 7 | Repo path: `web/` di folder ini vs Pictures | **`beriklan.co.id/web` + remote webberiklan** |

---

## 21. LAMPIRAN — MAPPING HALOKA COMPONENT → BERIKLAN

| Haloka | Beriklan equivalent | Notes |
|---|---|---|
| `Navbar.svelte` | `Navbar.astro` + mobile Svelte | Mega menu layanan |
| `ChatSimulator.svelte` | `HeroScene.svelte` | Ads dashboard, bukan chat |
| `TrustBadges.svelte` | `TrustStrip.astro` | Client + partner logos |
| `PainPoints.svelte` | `PainSection` + `AdWasteCalculator` | Corporate pain copy |
| `Features.svelte` | `MethodBento.astro` | 6-step method |
| `InteractiveTutorial.svelte` | `ProcessStepper.svelte` | 4 steps agency |
| `SocialProof.svelte` | `TestimonialMarquee.astro` | From COPY-BIBLE |
| `PricingInteractive.svelte` | `PricingTeaser.svelte` + `/paket` | Retainer model |
| `Faq.svelte` | `Faq.svelte` | Reuse pattern |
| `FinalCTA.svelte` | `FinalCta.astro` | WA + form |
| `StickyCTA.svelte` | `StickyMobileCta.svelte` | Same pattern |
| `Layout.astro` SEO | `BaseLayout.astro` | Expand multi-page meta |
| Tailwind brand green | Brand blue system | Agency not WhatsApp product |

---

## 22. RINGKASAN SATU PARAGRAF

Kita **menyalin fondasi teknis & pola conversion Haloka** (Astro + Svelte islands + Tailwind + hero interactive + sticky CTA + pricing interactivity + JSON-LD), lalu **menaikkannya ke level multi-page SEO agency site**: design system corporate Pulse Command, 10 service pages, blog migration dari WordPress, redirect matrix 800+ URL, form lead + WhatsApp, staging di Cloudflare Pages, dan **production domain dikunci sampai design di-approve**. Copy dan klaim bisnis mengikuti `COPY-BIBLE.md`; eksekusi dimulai dari foundation → homepage (gate review) → services → funnel pages → migration → staging.

---

*Dokumen ini adalah overview arsitektur & roadmap.  
**Detail per halaman (menu live, pricing aktual, copy SEO, animasi Svelte per section) → lihat `PER-PAGE-REDESIGN-PLAN.md`.**

Update status checkbox di §14 seiring eksekusi.*
