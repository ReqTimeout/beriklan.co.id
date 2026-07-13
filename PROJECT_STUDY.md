# Haloka Landing - Project Study Notes

Dokumen ini adalah ringkasan hasil pelajari project saat ini sebagai baseline sebelum perubahan fitur.

## Scope Kerja (Disepakati)

- Fokus awal: pelajari project dulu.
- Tidak melakukan perubahan kode atau desain tanpa instruksi lanjutan.
- Semua update berikutnya mengacu ke dokumen ini agar perubahan tetap terarah.

## Tech Stack

- Framework: Astro 5
- UI Components: Svelte 5
- Styling: Tailwind CSS
- Language mode: ESM (type: module)

## Script Utama

- Dev: `npm run dev`
- Build: `npm run build`
- Preview: `npm run preview`

## Struktur Aplikasi (Ringkas)

- Entry page: `src/pages/index.astro`
- Global layout + SEO + GTM: `src/layouts/Layout.astro`
- Global styles: `src/styles/global.css`

Komponen landing utama yang dirender berurutan di entry page:

- `Navbar.svelte`
- `StickyCTA.svelte`
- Hero section + `ChatSimulator.svelte`
- `TrustBadges.svelte`
- `PainPoints.svelte`
- `Features.svelte`
- `InteractiveTutorial.svelte`
- `SocialProof.svelte`
- `PricingInteractive.svelte`
- `FinalCTA.svelte`
- `Faq.svelte`
- Footer

## Ringkasan Fitur yang Sudah Ada

- Hero dengan CTA trial + simulasi chat visual.
- Narasi pain points dan value proposition.
- Showcase fitur (brain/SOP upload, CRM cold-warm-hot, auto follow-up, booking/calendar).
- Interactive tutorial end-to-end (setup -> chat -> label intent -> dashboard revenue).
- Pricing interaktif bulanan/tahunan + dynamic link ke register.
- Social proof, trust badge, FAQ, sticky CTA, final CTA.
- SEO dan tracking sudah dipasang di layout (meta, OG, Twitter card, schema, GTM).

## Catatan Teknis Penting

- CTA register menggunakan base URL: `https://platform.haloka.id/register?...`.
- Beberapa konten README masih template Astro default dan belum merepresentasikan implementasi aktual.
- Tampilan sangat visual-heavy (animasi, blur, gradient), jadi perubahan performa perlu diuji di mobile.

## Guardrail Saat Update Fitur (Agar Aman)

- Jangan ubah urutan section utama tanpa instruksi.
- Jangan ubah copywriting besar-besaran tanpa approval.
- Jangan ubah struktur tracking/SEO di layout tanpa kebutuhan jelas.
- Prioritaskan edit minimal pada komponen target, hindari efek domino lintas komponen.

## Rekomendasi Alur Kerja Perubahan Berikutnya

1. Tentukan komponen target dan tujuan bisnisnya.
2. Ubah hanya file terkait target.
3. Jalankan validasi local (`npm run dev`, cek UI desktop + mobile).
4. Ringkas perubahan dalam format: apa diubah, kenapa, dampaknya.

---

Status dokumen: baseline awal setelah sync repository.