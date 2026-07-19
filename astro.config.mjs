import { defineConfig } from 'astro/config';
import svelte from '@astrojs/svelte';
import tailwind from '@astrojs/tailwind'; // <--- Pastikan baris ini ada

// Sitemaps are now generated post-build by scripts/build_sitemaps.py
// (per content-type, with proper lastmod from posts.json + freshness.json)
// @astrojs/sitemap removed: it couldn't produce 7-type split with content-aware lastmod.

// https://astro.build/config
export default defineConfig({
  site: 'https://beriklan.co.id',
  integrations: [
    svelte(),
    tailwind(),
  ],
});