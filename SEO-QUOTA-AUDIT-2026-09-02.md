# SEO + CF Quota Audit & Action Plan — 2026-09-02

> Audit snapshot 2 domain (`beriklan.co.id` Indonesia, `beriklan.my` Malaysia)
> mencakup SEO state, bug, gap, dan strategi optimasi CF Workers free tier.
> Pelengkap: `PHASE-STATUS-2026-09-02.md` (D1 quota fix history).

---

## TL;DR

**Status aman:**
- `beriklan.co.id` 200 di semua endpoint penting. Blog index kembali live.
- `beriklan.my` homepage + sitemap + blog index 200. Blog artikel ada 457 URL di sitemap-blog.

**Bug/risiko utama:**
1. **`beriklan.my/blog/` kosong** — `BlogFilter.svelte` fetch `/data/posts-index.json` → `[]` → 0 kartu artikel. Page 2 dari static build OK. Sudah ada fix di `beriklanweb` (posts-index fallback ASSETS) — **belum ter-deploy di `beriklanmy` Worker**.
2. **`beriklan.my/blog/<slug>/` HTTP 500** untuk semua slug AI-generated (3 sample test). Kemungkinan D1 quota / exception di worker `beriklanmy` (bukan `beriklanweb`).
3. **D1 free quota 5M reads/hari account-wide** — dipakai BOTH `beriklan-seo` + `beriklan-my-seo`. Burn hari ini (Sep 2) tembus lagi ~03:30 UTC padahal fix sudah jalan → ada burner yang belum ke-handle.
4. **Missing sitemaps di `beriklan.my`**: `sitemap-harga.xml` 404, `sitemap-blog-pagination.xml` 404, `sitemap-services.xml` 404. Co.id punya 7+ sitemap, my cuma 5.
5. **`beriklan.my` schema JSON-LD `addressLocality` salah** — nilai `"Bandung"` (kota Indonesia) untuk agency Malaysia. Bug SEO + AEO.

**Rekomendasi prioritas (urutan dampak/cepat):**
1. Sync posts-index fallback fix ke `beriklanmy` Worker (restore blog index Malaysia).
2. Investigate `beriklan.my/blog/<slug>/` 500 — perlu source code `beriklanmy` (tidak di repo ini).
3. GSC submit sitemaps untuk `beriklan.my` + tambah `sitemap-harga.xml` agar lengkap.
4. Perbaiki schema `addressLocality Malaysia` di `beriklan.my`.
5. Workers Paid ($5/mo) — opsional, jika burn >5M/hari setelah semua optimasi.

---

## Audit Detail

### A. `beriklan.co.id` (Indonesia)

| Endpoint | Status | Catatan |
|---|---|---|
| `/` | 200 | Title + Schema (ProfessionalService + Organization) ✅ |
| `/blog/` | 200 | 24 post via static fallback (sudah fixed 02 Sep) ✅ |
| `/blog/<static-slug>/` | 200 | ASSETS fallback OK ✅ |
| `/blog/<D1-only-slug>/` | 200/404 | Cache 1 jam setelah quota reset; sebelumnya 500 ✅ |
| `/data/posts-index.json` | 200 | 24 post (static fallback). D1 dead → static; D1 alive → 10k+ post |
| `/sitemap.xml` | 200 | alias → `sitemap-index.xml` |
| `/sitemap-index.xml` | 200 | 7 child: static, services, city, pillar, harga, blog, blog-pagination |
| `/sitemap-blog.xml` | 200 | Empty `<urlset/>` — D1 dynamic, post belum populate (lihat catatan) |
| `/news.xml` | 200 | News sitemap |
| `/llms-full.txt` | 200 | AI-friendly content index |
| `/robots.txt` | 200 | AI crawlers Allow + Sitemap decl ✅ |

**Statistik sitemap `beriklan.co.id`:**
- `sitemap-static.xml`: 30+ URL
- `sitemap-services.xml`: 10 service page
- `sitemap-harga.xml`: **120 URL** ✅
- `sitemap-city.xml`: **385 URL** ✅
- `sitemap-pillar.xml`: 10 pillar
- `sitemap-blog-pagination.xml`: **312 URL** ✅
- `sitemap-blog.xml`: **0 URL** ❌ — D1 dynamic empty

**Gap:** `sitemap-blog.xml` kosong padahal ada 10k+ post di D1. Static `sitemap-blog-pagination.xml` punya 312 dari 827 static. Sitemap blog dynamic harusnya pakai cache 1 jam juga (seperti posts-index).

**robots.txt co.id:** AI crawlers (GPTBot, ChatGPT-User, ClaudeBot, anthropic-ai, PerplexityBot, Google-Extended, CCBot, Applebot-Extended, Bytespider, meta-externalagent, Amazonbot) semua `Allow: /` + Disallow `/api/`. **Excellent untuk AEO (Answer Engine Optimization)**.

---

### B. `beriklan.my` (Malaysia) — BANYAK MASALAH

| Endpoint | Status | Catatan |
|---|---|---|
| `/` | 200 | Title Malaysia ✅, tapi **Schema `addressLocality: "Bandung"` BUG** ❌ |
| `/blog/` | 200 | **BlogFilter fetch posts-index `[]` → 0 kartu** ❌ |
| `/blog/page/2/` | 200 | Has grid-card, articles rendered (static build) ✅ |
| `/blog/<slug>/` (AI generated) | **500** | Untuk `best-digital-marketing-agency-malaysia`, `harga-iklan-google-untuk-restoran-2026`, dll ❌ |
| `/blog/<static-slug>/` | ? | Tidak test (mungkin OK dari static) |
| `/data/posts-index.json` | 200 | `[]` ❌ — perlu fallback static |
| `/sitemap.xml` | **404** ❌ | co.id punya, my tidak |
| `/sitemap-index.xml` | 200 | 5 child: static, pillar, city, tag, blog |
| `/sitemap-blog.xml` | 200 | **457 URL** ✅ (dari D1) |
| `/sitemap-blog-pagination.xml` | **404** ❌ |
| `/sitemap-harga.xml` | **404** ❌ |
| `/sitemap-services.xml` | **404** ❌ |
| `/sitemap-static.xml` | 200 | 25 URL ✅ |
| `/sitemap-pillar.xml` | 200 | 10 pillar ✅ |
| `/sitemap-city.xml` | 200 | 21+ kota Malaysia ✅ |
| `/news.xml` | 200 | News sitemap ✅ |
| `/llms-full.txt` | 200 | ✅ |
| `/robots.txt` | 200 | Sama dengan co.id (AI Allow) ✅ |

**Statistik sitemap `beriklan.my`:**
- `sitemap-static.xml`: 25 URL
- `sitemap-pillar.xml`: 10
- `sitemap-city.xml`: 21+ kota (kuala lumpur, johor, penang, ipoh, kuching, dll)
- `sitemap-tag.xml`: kosong ❌
- `sitemap-blog.xml`: **457 URL** ✅ (blog sudah dipublish banyak)
- Missing: `sitemap-harga.xml`, `sitemap-services.xml`, `sitemap-blog-pagination.xml`, `sitemap.xml` alias

**DB `beriklan-my-seo` (id `9339554e-c00a-4b8c-96cf-2ccbf69a6e20`):**
- `keyword_queue`: 35,864 keywords (lebih sedikit dari co.id 391k)
- 51 tabel — schema lengkap (articles, posts_meta, posts_content, generated_drafts, pending_indexing, dll)
- Skema `articles` (co.id tidak punya tabel ini): `id, slug, title, keyword_id, word_count, h2_count, h3_count, faq_count, keyword_density, quality_score, status, generated_at, published_at, model_used, prompt_version`
- Kemungkinan my pakai flow generate berbeda (quality metrics dulu baru publish)

**Worker `beriklanmy` (id berbeda, last mod 2026-08-27):**
- Tidak ada source code di repo ini (`beriklan.co.id/web/src/worker-entry.js` HANYA untuk `beriklanweb`)
- Routes tidak bisa di-query via API (token zone-scope co.id only)
- Sudah ada 1 cron trigger (`0 * * * *`)

**Schema bug di beriklan.my:**
```json
"address":{"@type":"PostalAddress","addressCountry":"ID","addressLocality":"Bandung"...}
```
→ Untuk agency Malaysia, harusnya `"addressCountry":"MY","addressLocality":"Kuala Lumpur"` (atau kota Malaysia lain). Mungkin carry-over dari template co.id.

---

## C. CF Free Tier Quota — Burn Analysis

### Limit harian per akun (5M D1 rows read/day)
- **Hari ini (2026-09-02)** quota burned LAGI ~03:30 UTC padahal fix sudah live (post-fix blog cache deploy `8ca3546e` jam 02:24 UTC). Hanya ~70 menit window dengan fix aktif sebelum quota mati.
- Worker `wrangler d1 execute beriklan-seo "SELECT 1"` jam 03:14 UTC masih ok → quota reset berhasil di 00:00 UTC.
- Beberapa query audit saya (PRAGMA table_info, COUNT(*) di tabel besar) menambah burn rate.

### Burner sources (sisa setelah fix 02 Sep, post-cache 1 jam)
1. **`/api/cron/gsc-indexing` 4.5×/jam** — query `pending_indexing` 31k rows/run (sudah ditambah `status IN` filter di deploy `25910044` jadi ~few k). Tapi masih hefty.
2. **`handleBlogSitemap` 2×/jam** — `SELECT slug, iso_date FROM posts_meta ORDER BY iso_date DESC` full table scan 11k+ rows. (Belum ada cache.)
3. **`handlePostsIndex` 4.5×/jam** — query `posts_meta ORDER BY iso_date` full scan + `generated_drafts` full scan. (Sudah ada fallback static di catch.)
4. **`bonusGrowthCtrFix`/`growth-freshness`/`content-refresh`** — query berbagai tabel besar.
5. **Audit queries hari ini dari terminal** — `wrangler d1 execute ... PRAGMA table_info(articles)` + multiple COUNT(*) → menambah burn.

### Free Tier Limits Recap
| Resource | Free Limit | Catatan |
|---|---|---|
| D1 reads | **5M rows/day** | **SHARED antara beriklan-seo + beriklan-my-seo + 5 DB lain** |
| D1 writes | 100k rows/day | Aman (cuma 380 draft/hari max) |
| D1 storage | 5 GB total | Aman |
| Workers requests | 100k/day | Aman |
| Workers CPU time | 10ms (Free) | Risiko kalau ada query lambat |
| R2 reads | 10M/月 | Aman |
| R2 writes | 1M/月 | Aman |
| Email (Resend) | 100/hari | Cron 25/batch × 4 = 100 max |
| GSC Indexing | 200/hari | `gsc-indexing` count=50/jam × 24 = 1200/hari MAX → worker batasi quota 200 |
| IndexNow | unlimited (CF API) | ✅ |

**Solusi burn D1:**
- Cache 1 jam di `handleBlogSitemap` (blog cache sudah done, sitemap belum).
- Cache 1 jam di `handlePostsIndex` (post-fix).
- Per-worker DB split: saat ini co.id & my **SHARE quota 5M**. Pisahkan akun CF atau upgrade ke Paid ($5/bulan → 25M/DB) untuk headroom.
- Prioritas-tinggi: **fix `beriklanmy` worker tidak ikut co.id quota burn**. Co.id worker saat ini akses `beriklan-my-seo` DB juga? Perlu dicek — jika ya, **fix `beriklanmy` blog posts-index/500 akan REDUCE total burn signifikan**.

---

## D. Bug List (Prioritas)

### 🔴 P0 — Segera

| # | Domain | Bug | Impact |
|---|---|---|---|
| B1 | `beriklan.my` | `/blog/` kosong (BlogFilter fetch `[]`) | Malaysia users tidak lihat artikel → bounce tinggi, SEO CTR turun |
| B2 | `beriklan.my` | `/blog/<slug>/` HTTP 500 untuk AI-generated posts | 457 URL sitemap-blog.xml → 0 reachable. SEO disaster: sitemap promises URL yang 500. |
| B3 | `beriklan.my` | Schema `addressLocality: "Bandung" addressCountry: "ID"` untuk agency Malaysia | AEO/Local SEO rusak. Google Knowledge Graph bingung. |

### 🟡 P1 — Minggu ini

| # | Domain | Bug | Impact |
|---|---|---|---|
| B4 | `beriklan.my` | `sitemap.xml` alias 404 (co.id ada, my tidak) | Tool SEO crawlers expecting `/sitemap.xml` dapat 404 |
| B5 | `beriklan.my` | Missing `sitemap-harga.xml`, `sitemap-services.xml`, `sitemap-blog-pagination.xml` | SEO coverage loss untuk halaman harga/services Malaysia |
| B6 | `beriklan.co.id` | `sitemap-blog.xml` 0 URL (D1 dead saat crawl) | Schema: sitemap di robots.txt reference sitemap-blog.xml tapi empty → Google complain di GSC |
| B7 | Both | D1 quota 5M/hari SHARED antara 2 DB | Burn beriklanmy akhirnya bunuh co.id service juga |

### 🟢 P2 — Backlog

| # | Domain | Improvement | Impact |
|---|---|---|---|
| B8 | `beriklan.co.id` | Cache `handleBlogSitemap` 1 jam | Hemat ~250k D1 reads/hari |
| B9 | Both | Cache `/news.xml` 1 jam | Hemat ~50k reads |
| B10 | `beriklan.my` | Track apakah schema `telephone: "+62811919328"` (ID number) benar | AEO inconsistency |

---

## E. Strategic Improvements (Next 30 Hari)

### Tier 1 — Quick wins (≤1 hari effort)

1. **Fix B1 + B2 beriklan.my blog** — duplicate logic `handlePostsIndex` fallback ASSETS + try/catch di `renderBlogPost`. BUT perlu source code `beriklanmy` worker (tidak di repo).
   - **Action:** minta user share worker code atau create new repo `beriklan.my-worker` mirror dari `beriklanweb`.
2. **Fix B3 schema Malaysia** — edit template halaman beriklan.my (di Astro `src/layouts/Layout.astro` atau page-level), ganti `Bandung` → `Kuala Lumpur`, `ID` → `MY`, `+62` WA → `+60` (atau biarkan karena WA Indonesia melayani pasar MY juga, tapi address harus fix).
3. **Cache `handleBlogSitemap` 1 jam** — mirip blog cache. Tambah di `web/src/worker-entry.js`.

### Tier 2 — Cross-Domain Sync (1-3 hari)

4. **Replicate `beriklanweb` → `beriklanmy`** untuk endpoint yang sama: posts-index fallback, blog fallback try/catch, sitemap cache, edge cache 1 jam. **Single source of truth** pattern.
5. **Tambah `sitemap-harga.xml` beriklan.my** — co.id punya 120 URL, my 0. Pattern sama: `/{service}/{city}/` untuk 10 service × 21 kota = 210 URL.
6. **Tambah `sitemap.xml` alias untuk my** — copy pattern dari co.id `worker-entry.js:441-459`.
7. **Add news sitemap submission to Bing Webmaster** untuk kedua domain (co.id & my).

### Tier 3 — Quota & Scale (3-7 hari)

8. **Pisahkan D1 account quota**: co.id di CF account A, my di account B. Atau upgrade Workers Paid $5/bulan untuk 25M reads/hari.
9. **Tambah cache `caches.default` di `handleBlogSitemap` + `handlePostsIndex`** (sudah done co.id posts-index, sisanya my + sitemap).
10. **Investigate why burn quota masih ~3-4M/hari** setelah fix — mungkin ada endpoint lain yang hidden burner.

### Tier 4 — Long-term (7+ hari)

11. **Workers Paid $5/bulan** untuk `beriklanmy` saja (co.id sudah cukup dengan optimasi). Budget headroom = 5× quota (25M vs 5M).
12. **R2 list pagination** untuk blog katalog (kalau >10k post, query `SELECT slug FROM posts_meta ORDER BY iso_date DESC LIMIT N OFFSET M` tetap scan index). Switch ke keyset pagination (`WHERE iso_date < ?`).
13. **Monitor CF Workers analytics** untuk quota burn trend (butuh token dengan `analytics:read` scope).

---

## F. Decision Required dari User

Sebelum eksekusi, butuh klarifikasi:

1. **Source code `beriklanmy` Worker** — di mana? (Repo berbeda? File bundle `.wasm`? Outsource?)
   - Kalau perlu dibuat ulang → effort tinggi (1-2 hari) untuk replikasi `beriklanweb` patterns.
   - Kalau sudah ada → bisa langsung patch B1+B2+B3.

2. **Workers Paid?** — Setuju upgrade `beriklanmy` $5/bulan untuk pisah quota + headroom? Co.id tetap free (sudah smooth dengan cache).

3. **Schema Malaysia fix** — Kantor Malaysia ada di mana? Kalau tidak ada, boleh tetap Bandung tapi field `addressCountry: "MY"` + `addressLocality: kota MY` tetap harus fix untuk konsistensi SEO.

4. **Sitemap expansion beriklan.my** — Setuju generate `sitemap-harga.xml` (210 URL service×kota) + `sitemap-services.xml` + `sitemap.xml` alias? Effort ~1-2 jam kalau template co.id di-replicate.

5. **Prune/noindex sudah di-cancel** per instruksi sebelumnya. Confirm: prioritas sekarang = fix blog my + schema fix + sitemap completeness + quota optimization.

---

## G. Quick Reference

### File lokal yang relevan
- `/Users/maabook/Desktop/beriklan.co.id/web/src/worker-entry.js` — `beriklanweb` Worker (LINE 14213 renderBlogPost, LINE 14270 related posts, LINE 9226 pending_indexing GSC, LINE 9221 priority-rebalance, LINE 13726 handlePostsIndex)
- `/Users/maabook/Desktop/beriklan.co.id/web/wrangler.jsonc` — Worker `beriklanweb`, DB `beriklan-seo`, R2 `idberiklan`
- `/Users/maabook/Desktop/beriklan.co.id/PHASE-STATUS-2026-09-02.md` — history fix 02 Sep
- `/Users/maabook/Desktop/beriklan.co.id/account.md` — CF token + zone IDs

### CF Account Info
- Account ID: `766dfffa7e5dcd8ba246ebfa60bc10ba`
- Zone co.id: `766dfffa7e5dcd8ba246ebfa60bc10ba` (sama dengan account)
- Zone my: `87d49193c05be0dc83a8b71a82468763`
- D1 co.id: `0e71d6e3-231f-40a1-ac6b-6defc3976efd` (name `beriklan-seo`)
- D1 my: `9339554e-c00a-4b8c-96cf-2ccbf69a6e20` (name `beriklan-my-seo`)
- Workers: `beriklanweb` (modified 2026-09-02), `beriklanmy` (modified 2026-08-27)

### Audit Methodology
- HTTP curl ke semua endpoint penting (homepage, blog index, post, sitemap, robots.txt)
- D1 schema inspection via `wrangler d1 execute ... PRAGMA table_info` + COUNT (jumlah reads masih aman saat audit ~03:30 UTC sebelum quota 7500 lock)
- CF API call (auth limited to zone co.id; routes/api untuk zone my & worker details gagal 10000 auth)
- Compare struktur co.id vs my: schema, sitemap, robots, blog content
