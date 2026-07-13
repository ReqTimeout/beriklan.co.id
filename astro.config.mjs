import { defineConfig } from 'astro/config';
import svelte from '@astrojs/svelte';
import tailwind from '@astrojs/tailwind'; // <--- Pastikan baris ini ada
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://beriklan.co.id',
  integrations: [
    svelte(),
    tailwind(),
    sitemap({
      filter: (page) => !page.includes('/blog/') || /\/(blog\/[^/]+)\/?$/.test(page),
      changefreq: 'weekly',
      priority: 0.7,
      lastmod: new Date(),
    }),
  ],
});