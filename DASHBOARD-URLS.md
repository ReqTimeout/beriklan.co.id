# Admin Dashboard URLs — Beriklan

> **Bookmark file.** Token lama `beriklan-admin-2026` sudah di-rotate pada 25 September 2026
> (bagian dari refactor `${env.ADMIN_TOKEN}` Fix #1). SEMUA URL di bawah pakai token baru.

**Update terakhir:** 2026-09-25

---

## 🔑 TOKEN AKTIF

| Domain | Token | Status |
|---|---|---|
| `beriklan.co.id` | `<ADMIN_TOKEN>` | ✅ aktif (rotated 25 Sep) |
| `beriklan.my` | _(belum di-set — Fase 3.6 .my belum dieksekusi)_ | ⏸️ deferred |

Token tersimpan di `/Volumes/macmini/Desktop/beriklan.co.id/.env.admin` (chmod 600).

---

## 📊 `beriklan.co.id` — DASHBOARD UTAMA

### Overview & Pipeline
- **Dashboard utama** (semua tab): https://beriklan.co.id/api/admin/email?token=<ADMIN_TOKEN>
  - Tab `overview` (default) — antrian email, cron heartbeat, daily quota
  - Tab `leads` — lead pipeline (match + AI personalisasi + auto-campaign)
  - Tab `wa` — WhatsApp click tracker + follow-up
- **Keywords queue**: https://beriklan.co.id/api/admin/keywords?token=<ADMIN_TOKEN>
- **Posts (artikel)**: https://beriklan.co.id/api/admin/posts?token=<ADMIN_TOKEN>
  - Filter by slug: `&slug=jasa-iklan-facebook-terbaik`
  - Filter by status: `&status=published`

### Growth System (FASE 4 — Indexasi & Pertumbuhan)
- **Growth log**: https://beriklan.co.id/api/admin/growth-log?token=<ADMIN_TOKEN>
  - Filter by action: `&action=enrich`
  - Filter by slug: `&slug=jasa-iklan-facebook-terbaik`
- **WA clicks tracker**: https://beriklan.co.id/api/admin/wa?token=<ADMIN_TOKEN>
- **Drafts**: https://beriklan.co.id/api/admin/drafts?token=<ADMIN_TOKEN>
- **AI test probe**: https://beriklan.co.id/api/admin/ai-test?token=<ADMIN_TOKEN>
  - List model: `&models=1`

---

## ⚙️ `beriklan.co.id` — CRON ENDPOINTS (manual trigger)

### Indexing & Submission
- **IndexNow** (default 100 URL/jam): https://beriklan.co.id/api/cron/indexnow?token=<ADMIN_TOKEN>
  - Custom count: `&count=50`
- **GSC Indexing** (submit sitemap + GSC): https://beriklan.co.id/api/cron/gsc/indexing?token=<ADMIN_TOKEN>
- **Index cascade** (backfill pending_indexing): https://beriklan.co.id/api/cron/index-cascade?token=<ADMIN_TOKEN>&count=200
  - Dry run: `&dry=1`

### Content & Growth
- **Hourly** (generate artikel AI, publish, indexing): https://beriklan.co.id/api/cron/hourly?token=<ADMIN_TOKEN>
- **Email send** (batch 25, max 4×/hari): https://beriklan.co.id/api/cron/email/send?token=<ADMIN_TOKEN>
- **Growth enrich** (minImp=5): https://beriklan.co.id/api/cron/growth/enrich?token=<ADMIN_TOKEN>&count=3&minImp=5
- **Growth CTR fix** (minImp=5): https://beriklan.co.id/api/cron/growth/ctr-fix?token=<ADMIN_TOKEN>&count=3&minImp=5
- **Growth GSC loop** (minImp=10 maxQueue=15): https://beriklan.co.id/api/cron/growth/gsc-loop?token=<ADMIN_TOKEN>&days=14&minImp=10&maxQueue=15
- **Growth freshness** (Senin 02 UTC): https://beriklan.co.id/api/cron/growth/freshness?token=<ADMIN_TOKEN>&count=2

### Lead Pipeline
- **Lead pipeline** (match + AI + campaign): https://beriklan.co.id/api/cron/leads/process?token=<ADMIN_TOKEN>&limit=100&ai=15&campaign=1

### Migration / Sync (HATI-HATI, berat)
- **Sync posts (lean)**: https://beriklan.co.id/api/admin/sync/posts?token=<ADMIN_TOKEN>
- **Sync posts (full mirror, berat)**: https://beriklan.co.id/api/admin/sync/posts?token=<ADMIN_TOKEN>&mirror=1
- **Bulk keyword import**: POST ke `/api/admin/keywords/import?token=<ADMIN_TOKEN>&source=curated_research_v2`

---

## 📊 `beriklan.my` — DASHBOARD _(⏸️ DEFERRED)_

URL di bawah PLACEHOLDER — token belum di-set sampai Fase 3.6 .my dibuka:

- https://beriklan.my/api/admin/email?token=_GANTI_DENGAN_TOKEN_MY_
- https://beriklan.my/api/admin/keywords?token=_GANTI_DENGAN_TOKEN_MY_
- https://beriklan.my/api/admin/growth-log?token=_GANTI_DENGAN_TOKEN_MY_
- https://beriklan.my/api/cron/gsc/indexing?token=_GANTI_DENGAN_TOKEN_MY_

Lihat `MY-MIGRATION-GUIDE.md` untuk setup lengkap.

---

## 🛠️ CARA ROTASI TOKEN (untuk next time)

```bash
# 1. Generate token baru (48 char hex)
NEW=$(openssl rand -hex 24)

# 2. Set di Cloudflare secret
cd /Volumes/macmini/Desktop/beriklan.co.id/web
npx wrangler secret put ADMIN_TOKEN
# Paste $NEW, Enter

# 3. Update .env.admin
echo "ADMIN_TOKEN=$NEW" >> /Volumes/macmini/Desktop/beriklan.co.id/.env.admin
chmod 600 /Volumes/macmini/Desktop/beriklan.co.id/.env.admin

# 4. Verify
curl -s -o /dev/null -w "%{http_code}\n" "https://beriklan.co.id/api/admin/email?token=$NEW&tab=overview"
# Expected: 200

# 5. Update DASHBOARD-URLS.md ini dengan token baru

# 6. Revoke token lama (jika sebelumnya di-expose)
```

---

## ⚠️ JANGAN

- ❌ Commit token baru ke git
- ❌ Share URL dashboard publik (token = full admin access)
- ❌ Pakai token lama `beriklan-admin-2026` (sudah di-rotate, return 401)
- ❌ Edit `wrangler.jsonc` vars untuk ADMIN_TOKEN (harus via `wrangler secret`)
- ❌ Pakai `run_worker_first: ["/*"]` jika grow-freshness/job sensitif lain ada path tertentu (co.id OK karena path apa saja aman)

---

**Maintainer:** Beriklan Digital Agency + Codex AI
**Versi:** 1.0 (2026-09-25)
