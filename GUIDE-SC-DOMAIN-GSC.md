# Panduan SC-DOMAIN untuk GSC Indexing — Beriklan.co.id

**Service Account:** `beriklan-seo-bot@lgc-indexer.iam.gserviceaccount.com` (project `lgc-indexer`)  
**Worker live:** `fdf75271-d53d-414d-b6cc-179d61cc8059`  
**Target GSC property:** `sc-domain:beriklan.co.id` (bukan `https://beriklan.co.id/`)

> Kenapa harus sc-domain? Worker publish pakai canonical `https://beriklan.co.id/blog/...` (apex) tapi GSC Indexing API + URL Inspection + sitemap ping harus cover **apex + www**. Hanya `sc-domain:beriklan.co.id` yang mencakup keduanya. Jika `GSC_SITE_URL` masih `https://beriklan.co.id/` maka submit 200/hari dan inspection 300/hari akan 403 untuk URL www dan sebaliknya.

---

## Langkah 1 — Buat Domain Property di GSC

1. Buka https://search.google.com/search-console
2. Klik **Add property** → pilih **Domain** (bukan URL prefix)
3. Masukkan `beriklan.co.id` → **Continue**
4. Google akan minta verifikasi DNS: copy TXT record `google-site-verification=xxxxx`

> Jika Domain property sudah ada (cek dropdown kiri atas GSC), lewati langkah 1-4.

## Langkah 2 — Verifikasi DNS di Cloudflare

1. Buka Cloudflare Dashboard → Zone `beriklan.co.id` (ID `47f87944d6d690eb388e7be1143c14a2`)
2. **DNS** → **Add record**
   - Type: `TXT`
   - Name: `@` (atau `beriklan.co.id`)
   - Content: `google-site-verification=xxxxx` (dari GSC)
   - TTL: Auto
3. Klik **Save**
4. Kembali ke GSC → klik **Verify**

Butuh 1-5 menit propagasi. GSC akan tulis `Ownership verified`.

> API token `cfut_wUtYNx9Ap...` yang ada sudah bisa update DNS via API jika mau otomatis — tapi via dashboard lebih cepat manual.

## Langkah 3 — Tambahkan Service Account sebagai Owner

1. Di GSC, pilih property `sc-domain:beriklan.co.id`
2. **Settings** (gerigi kiri bawah) → **Users and permissions**
3. Klik **Add user**
   - Email: `beriklan-seo-bot@lgc-indexer.iam.gserviceaccount.com`
   - Permission: **Owner** (bukan Restricted)
4. **Add**

Tanpa Owner, API akan 403 `does not have sufficient permission` dan worker `handleGscIndexing` + `handleIndexVerify` akan break + retry queue.

Verifikasi SA:

```bash
curl -s "https://beriklan.co.id/api/admin/gsc-whoami?token=beriklan-admin-2026" | jq
# harus ok + client_email sama di atas
```

## Langkah 4 — Set Secret `GSC_SITE_URL` di Worker

```bash
cd /Users/maabook/Desktop/beriklan.co.id/web
printf "sc-domain:beriklan.co.id" | CLOUDFLARE_API_TOKEN="cfut_wUtY…" npx wrangler secret put GSC_SITE_URL
```

Tunggu deploy otomatis (30 detik). Worker code sudah baca `env.GSC_SITE_URL || "https://beriklan.co.id/"` di `worker-entry.js:6902` + `worker-entry.js:9133`.

Alternatif sementara via D1 (jika secret belum propagate):

```bash
CLOUDFLARE_API_TOKEN="cfut_wUtY…" npx wrangler d1 execute beriklan-seo --remote --command "INSERT INTO cron_settings (name,cron,enabled,label) VALUES ('gsc_site_url','sc-domain:beriklan.co.id',1,'GSC domain property') ON CONFLICT(name) DO UPDATE SET cron=excluded.cron"
```

Tapi secret `GSC_SITE_URL` tetap yang dipakai `getGoogleAccessToken` — jadi secret lebih prioritas.

## Langkah 5 — Test Submit & Inspection

```bash
# 1. Test GSC Indexing (5 URL)
curl -s "https://beriklan.co.id/api/cron/gsc-indexing?token=beriklan-admin-2026&count=5&debug=1" | jq '.quota_used, .submitted_count, .log'

# Harus: quota_used <200, submitted_count 5, log[].stage auth ok
# Jika 403 → SA belum Owner di sc-domain

# 2. Test URL Inspection (1 URL)
curl -s "https://beriklan.co.id/api/cron/index-verify?token=beriklan-admin-2026&count=1&debug=1" | jq '.checked, .indexed, .quota_used'

# Harus: checked 1, indexed 0/1 (tergantung sudah terindex)
# Jika 403 → sama, SA belum Owner

# 3. Ping sitemap
curl -s "https://beriklan.co.id/api/ping-sitemap?token=beriklan-admin-2026" | jq
```

## Langkah 6 — Verifikasi di GSC Dashboard

1. GSC → `sc-domain:beriklan.co.id` → **Sitemaps**
   - Submit `https://beriklan.co.id/sitemap-index.xml` dan `https://beriklan.co.id/sitemap-blog.xml`
   - Status harus `Success` + `Discovered URLs` 12.646
2. **URL Inspection** → paste `https://beriklan.co.id/blog/biaya-jasa-digital-marketing-untuk-motor-di-makassar/` → **Test live URL** → harus `URL is on Google` setelah 2-3 hari submit

---

## Troubleshooting

| Error | Penyebab | Fix |
|-------|----------|-----|
| `403 does not have sufficient permission` | SA bukan Owner di sc-domain | Ulang Langkah 3, pastikan permission Owner, bukan User |
| `429` di index-verify | Quota 300/hari habis (WIB) | Tunggu reset 00:00 WIB, atau kurangi `count` |
| `sc-domain not found` | Property belum verified | Ulang Langkah 1-2, tunggu TXT propagate |
| `GSC_SITE_URL not set` | Secret belum ter-set | Ulang Langkah 4 + redeploy `npx wrangler deploy` |

---

## Catatan Penting

- Jangan pakai `https://www.beriklan.co.id/` untuk GSC_SITE_URL — worker sudah redirect `www → apex` (301) di `worker-entry.js:25`, jadi IndexNow key di apex sudah aman.
- Quota GSC Indexing 200/hari WIB (`worker-entry.js:9168`) + IndexNow 50/jam + verify 300/hari — semua sudah jalan di cron `0 * * * *` (`worker-entry.js:661`).
- Backfill 3.9k URL sudah dikerjakan 26 Aug (pending 8.303 → 17.644) via D1 `INSERT OR IGNORE` (lihat `AUDIT-FLOW-INDEXING-ADSENSE-2026-08-26.md:5`).

