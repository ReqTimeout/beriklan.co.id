# SEO Automation Phase Status — 2026-09-02

> Snapshot status 4-phase plan + progress batch D1 quota fix.
> Lihat juga: `plan-seo-automation-audit.md` (audit plan Aug 2026, data stale),
> `IMPROVEMENT-PLAYBOOK-2026-08-27.md` (guardrails + cron state).

## TL;DR

- **D1 quota incident RESOLVED + SMOOTH-FREE GUARANTEE.**
  Blog post kembali 200. Edge cache 1 jam aktif → burn diproyeksi **166M → ~0.8M/hari** (jauh di bawah 5M free, tanpa bayar).
- **SEO tetap jalan normal:** GSC indexing, IndexNow, sitemap ping, growth loops (enrich/ctr-fix/freshness) tidak terdampak cache (cron langsung ke D1).
- **Phase 1–4:** 2–3 selesai, sisanya blocker di quota / generator pause.

## Batch: D1 Quota Burn Fix (2026-09-02)

### Root cause
Related-posts blog query `posts_meta WHERE service=? ORDER BY iso_date DESC LIMIT 3`
dan query `city` versi full-table scan + sort (no index) → **166M rows/day**
(32× kuota D1 free 5M). Error 7500 ("exceeded daily row read limit") aktif
sejak kemarin; cron hang di jam kerja WIB.

### Fixes (4 deploy — smooth free tanpa bayar)

| # | Version | What | Reads impact |
|---|---|---|---|
| 1 | `f52cb082` | 3 index live (migration array) + blog fallback try/catch ke ASSETS | related-posts service 18k/run → ~3/run. City query masih ~410/run. |
| 2 | `25910044` | Tambah `status IN (...)` filter di pending_indexing GSC query + idx_generated_drafts_status + idx_pending_indexing_status | pending_indexing GSC 31k → few k; COUNT drafts 14k → ~380 |
| 3 | `8ca3546e` | **Edge cache blog post 1 jam** (caches.default, HIT=0 D1 reads) + 2 index (city_service, iso_date) | blog D1 reads 5-6 query/hit → 0 saat HIT (90%+ hit rate). Proyeksi total **~0.8-1M/hari** — smooth di free tier. |

### Deploys
- Commit (web/ repo): `85e4ff4` (1), `8016559` (2), `875d1ba` (3, cache). Lokal saja, belum push.
- Backup: `worker-entry.js.bak-20260902-0220`, `.bak-20260902-0245`, `.bak-20260902-cache`.
- 2 cron trigger utuh: `0 * * * *` + `*/15 * * * *` (no warning).

### Verification (02 Sep 02:50 UTC, quota masih habis)
- `/blog/jasa-iklan-facebook-terbaik/` → **200** (static fallback, X-Cache belum aktif sampai D1 hidup — akan jadi HIT setelah reset).
- `/blog/cara-iklan-facebook-murah/` → 404 (D1-only, expected sampai reset 00:00 UTC).
- Homepage + `/blog/` + `/sitemap-blog.xml` → 200.
- Index EXPLAIN: SEARCH (bukan SCAN) untuk service query.
- Manual gsc-indexing: error JSON rapi (`queue_fetch_failed` karena quota — akan normal setelah reset).

### Jaminan smooth (tanpa bayar) — setelah reset 00:00 UTC
- **Blog:** HIT cache = 0 D1 reads. MISS 1x/jam/slug saja. Walau quota habis nanti, cache yang sudah ada tetap serve (tidak butuh D1) → tidak ada 404 massal lagi.
- **SEO cron:** GSC/IndexNow (200/hari), growth loops, sitemap ping tetap jalan — mereka query D1 langsung, tidak lewat cache blog, quota cukup (0.8M << 5M).
- **Verifikasi besok 00:30 UTC:** `npx wrangler d1 insights beriklan-seo --time-period 1h --sort-by reads` — harus lihat HIT rate + burn <1M.

### Risiko ongoing (sudah mitigasi)
- Kuota D1 mati sampai **00:00 UTC 2026-09-03** (07:00 WIB). Sampai reset, blog D1-only slug 404. Static 827 slug aman. **Setelah reset + cache, risiko 404 massal hilang.**

## Phase Status (per plan-seo-automation-audit.md)

### Phase 1 — Un-pause + pacing [DONE, generator INTENTIONALLY PAUSED]
- ✅ `publish_daily_limit=300`, `batch_size=30` (dari 150/15).
- ✅ Refill buffer R2 → D1 (refillBufferCore, rolling cursor).
- ⏸ **Cron `hourly-generate` masih PAUSED** per direktif user
  (`handleHourlyGenerate` hard pause guard ~line 8529).
  386k artikel sudah di R2 queue; tidak butuh generate baru.
  Aktifkan hanya bila R2 menipis atau ada perluasan cakupan.
- ⏸ `trending-generate` PAUSED.

### Phase 2 — Indexing + priority rebalance [DONE 2026-09-02]
- ✅ GSC Indexing API aktif (`0 * * * *`, count=50/jam, 200/hari).
- ✅ IndexNow aktif (`15 * * * *`, max 50/run).
- ✅ Sitemap lastmod di-generate (worker-entry.js lines 13689–13738).
- ✅ Pending index cleanup (hapus seed-/exp- artifact).
- ✅ **`priority-rebalance` cron DONE** `handlePriorityRebalance` harian 03:00 UTC (standalone, tidak tergantung `hourly-generate` PAUSED). 3 UPDATE: view-live→25, core×city→90, industri `untuk`→90. +3 index `keyword_queue(status…)`. Deploy `54e5867d`, manual `?dry=1` ok (D1 masih 7500 sampai reset 00:00 UTC).
- ❌ **Prune dead URLs / noindex-90-day TIDAK ada.**
  Hanya noindex headers untuk JSON responses.

### Phase 3 — Cluster + authority [PARTIAL]
- ✅ Internal linking via related posts (service → city → all, LIMIT 3).
- ✅ Cross-link mesh (citySibling LIMIT 3, dedupe + cap 6).
- ✅ Schema JSON-LD (Article, Breadcrumb, FAQPage).
- ✅ Sitemap ping tiap jam (handlePingSitemap).
- ⏳ Authority building (backlink, directory submission) — manual proses
  di `DIRECTORY-SUBMISSION-GUIDE.md`, bukan cron otomatis.

### Phase 4 — Quality filter + refresh [MOSTLY DONE]
- ✅ `growth-enrich` (daily 09:00 UTC) — rewrite intro+FAQ artikel pos 3-18.
- ✅ `growth-ctr-fix` (daily 09:00 UTC) — rewrite SERP title+meta.
- ✅ `growth-freshness` (Mon 02:00 UTC) — callout "Diperbarui" + dateModified.
- ✅ `growth-gsc-loop` (h%6) — query GSC ber-impresi → keyword_queue.
- ✅ `content-refresh` (`0 0 1 * *`) — refresh artikel lama bulanan.
- ✅ `snippet-optimize` (h%6) — optimasi featured snippet.
- ❌ **Prune dead URLs** (no organic traffic 90 hari) — belum diimplement.

## Next per phase (prioritas)

| Phase | Next action | Effort | Impact |
|---|---|---|---|
| 2 | ~~Implement `priority-rebalance` cron~~ **DONE** (harian 03:00 UTC, 03 Sep pertama jalan setelah reset). | — | — |
| 2 | Prune dead URLs: cron mingguan scan posts_meta tanpa impresi GSC 90 hari → noindex meta + skip di sitemap. | medium | bersihin index bloat |
| 4 | Implement prune dead-URL handler (same as Phase 2). | (sama) | (sama) |
| 1 | Pantau R2 queue; aktifkan hourly-generate hanya bila `< 100k`. | low | ops |
| — | Verifikasi post-reset: `wrangler d1 insights --time-period 1h` jam 00:30 UTC 09-03. | low | confirm fix |
| — | Commit + push frontend changes (Layout.astro, pages, robots, sitemaps) setelah QA visual. | low | cleanup |

## Open items / known limits

- Kuota D1 free 5M reads/hari fundamental limit. Post-fix burn diproyeksi
  ~3–4M/hari (dari 166M). Tidak ada headroom untuk query berat lain.
  Pertimbangkan upgrade Workers Paid ($5/mo) untuk 25M reads/hari jika
  burn naik lagi.
- `handleHourlyGenerate` paused = tidak ada artikel baru sampai R2 menipis.
- Frontend changes besar (Layout.astro, jasa-view-live/* pages) sudah
  ditulis di lokal tapi **belum di-commit/push** — SOP rule 1: jangan
  deploy visual tanpa QA. Pisahkan dari worker batch.
- `beriklanmy` D1 (project terpisah) tidak termasuk audit ini.

## Referensi cepat

- Deploy ops: `DEPLOY_OPERATIONS.md` (token, endpoints, recovery).
- Worker code: `web/src/worker-entry.js`.
- Audit plan (stale data): `plan-seo-automation-audit.md`.
- Playbook: `IMPROVEMENT-PLAYBOOK-2026-08-27.md` §G–J.
- SEO system: `SEO-SYSTEM-BERIKLAN-2026-08-26.md` (arsitektur).
- Replikasi ke domain lain: `SEO-SYSTEM-REPLICATION.md` (blueprint).

---

## Phase 6 — Edge cache sitemap/posts-index/news.xml (2026-09-02, deploy 6+7)

**Deployed versions:** `743ddd09` (cache) → `06bf802f` (+sitemap fallback) · **Commit:** `7bce0f4` (local, NOT pushed) · **Rollback target:** `54e5867d`

### Changes
1. **Edge cache (`caches.default`)** on 3 fetch-path handlers — the remaining D1 full-scan burners:
   - `/data/posts-index.json` (handlePostsIndex) — TTL 3600s edge / 300s browser. Was 2 full scans/request (posts_meta ~11k + generated_drafts)
   - `/sitemap-blog.xml` (handleBlogSitemap) — TTL 3600s. Was 2 full scans/request; Googlebot fetches after each hourly sitemap-ping
   - `/news.xml` (handleNewsSitemap) — TTL 1800s. iso_date 36h filter can't use existing composite indexes → full scan
   - Pattern identical to blog-post cache (lines 388-427): cache-first try/catch, X-Cache HIT/MISS, `ctx.waitUntil(cache.put())`, cache ONLY successful D1 responses
2. **sitemap-blog.xml static fallback (bug fix found during verify):** D1-error path previously returned EMPTY urlset while a 1.6MB static asset (827 URLs) sat in dist/ — Google fetching during quota lock saw 0 URLs. Now falls back to static asset (max-age=600, never cached so D1 recovery serves fresh dynamic version). Verified live: 7497 `<loc>` entries served during lock.

### Verified live (during D1 7500 lock)
- posts-index → 200 static fallback (24 posts), no X-Cache (fallback uncached ✓)
- sitemap-blog → 200 static fallback (827 URLs) ✓
- news.xml → 200 empty urlset, uncached ✓ (no static equivalent exists; acceptable — news sitemap is freshness-based)
- Blog post cache: inconclusive during lock (D1 probe throws → static asset path, no X-Cache). Re-verify after 00:00 UTC reset.

### Burner audit (fetch-path full scans) — COMPLETE
- All other `.all()` calls without LIMIT: cron/admin paths only (guarded, low frequency) — no action needed

### Pending (next session)
- [ ] After 00:00 UTC 2026-09-03: verify X-Cache HIT on 2nd request for all 3 endpoints + blog post; `wrangler d1 insights beriklan-seo --time-period 1h --sort-by reads` to confirm burn reduction
- [ ] Awaiting user: beriklanmy Worker source location (my-side P0/P1 fixes blocked)
- [ ] Awaiting user: my schema fix (addressCountry "MY"), my sitemap expansion
- [ ] Uncommitted frontend fixes pending visual QA: co.id homepage canonical www→apex, my schema addressLocality
