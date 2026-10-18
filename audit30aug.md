 AUDIT SISTEM SEO OTOMATIS BERIKLAN.CO.ID
✅ Yang Sudah Baik
Item	Status
D1-first render blog	200 OK, 7.027 slug di luar static build tetap ter-render (contoh: /blog/apa-itu-facebook-ads-di-bandung/)
sitemap-blog.xml	Live, valid, 14.523 URL
Growth loop (enrich/ctr-fix/freshness/gsc-loop)	Jalan, terbukti via growth_log (2 post ter-enrich manual + FAQ)
Publish dari buffer	Jalan (12.527 committed, 397 draft pending, limit 600/hari)
Schema post, AdSense, tag pages	OK (Article, FAQPage, BreadcrumbList; ca-pub-4438… 9 ref; tag 200)
🔴 P0 — Sitemap Pipeline RUSAK (akar masalah utama)
1. 6 sitemap di robots.txt, 5 di antaranya 404 (sitemap-static/city/tag/pillar.xml, news.xml). Live hanya sitemap_index.xml (Astro), post/page-sitemap.xml, sitemap-blog.xml.
2. Root cause ditemukan: scripts/build_sitemaps.py menghitung DIST sebagai <root>/web/dist padahal script kini tinggal di web/scripts/ → path jadi web/scripts/web/dist → error "dist/ not found" → sitemap tak pernah ikut deploy.
3. Worker /sitemap.xml fetch asset sitemap-index.xml (hyphen) yang tak ada → 301 → 404.
4. Kaskade: handlePingSitemap (line 7814-7820) submit 5 sitemap 404 ke GSC → semua 400 → cron gsc-indexing failed 42x/2 hari → retry queue 235 pending + 3 dead. GSC jadi tidak punya sitemap valid yang ter-submit.
5. handleNewsSitemap hilang dari worker current (hanya ada di .bak-20260827-005334).
🔴 P0 — Kuota GSC Indexing API Google ≠ tracking kita
Live test barusan: sisi worker quota_used 55/200, tapi Google balas 429 "Publish requests per day". Reset window Google ≠ hari WIB → self-quota 200/hari overestimate; drain efektif jauh lebih kecil. Ditambah: API resmi Google hanya untuk JobPosting/BroadcastEvent — submit blog post biasa mungkin diabaikan Google. Backlog 14.408 pending (input 300-600/hari) tidak akan habis lewat jalur ini.
🟠 P1
Generator artikel mati: cron hourly enabled=0. ZEN_FREE_MODELS (line 4176) masih berisi model mati: big-pickle/mimo-v2.5-free 429, x-preview-f-free/hy3-free 401. Hidup: nemotron-3.5-lightning-free, nemotron-3-ultra-free (lambat), gpt-oss-20b (Groq, OK).
Cron stuck: banyak status "running" auto-timeout >2 jam (gsc-indexing 40, sync-posts 19, indexnow 18, email-send 15 / 2 hari); retry queue 258 pending.
🟡 P2
Kualitas konten: rata-rata 3.887 chars (~550 kata) untuk 14.337 post AI → risiko scaled-content-abuse. Distribusi timpang: jasa-iklan-tiktok 70% (10.139), 827 tanpa service, landing-page cuma 26.
Traffic tipis: ~2.200 impresi + ~13 klik / 2 minggu. Keyword layanan posisi 30-98.
id.beriklan.co.id (WordPress PHP legacy) masih live dan justru jadi halaman peringkat terbaik ("pasang iklan gratis" pos 6-8) — kanibalisasi terhadap domain utama. Keputusan bisnis: 301/migrasi/kill.
robots.txt kontradiktif: Disallow Amazonbot/Bytespider/CCBot/ClaudeBot tapi ada section Allow untuk bot yang sama.