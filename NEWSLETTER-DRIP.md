# Newsletter Drip Campaign — Plan

> Status: **Infrastructure ready, sending requires email service integration**

## Overview

P2.6 deliverable: collect email subscribers + run a 3-email drip campaign.

**What's live:**
- `NewsletterSignup.svelte` — form in Footer
- `/api/newsletter/subscribe` — POST endpoint, saves to D1
- `/api/newsletter/unsubscribe` — POST/GET, removes from D1 + friendly HTML page
- `/api/newsletter/admin?token=...` — stats + CSV export
- D1 table `newsletter_subscribers` (auto-created)

**What's missing:**
- Email sending service (Brevo/MailerLite/Cloudflare Email)
- Drip scheduling logic (cron + email service integration)

---

## D1 Schema

```sql
CREATE TABLE newsletter_subscribers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  name TEXT,
  page_url TEXT,         -- where they signed up
  source TEXT,           -- referrer
  status TEXT NOT NULL DEFAULT 'active',  -- active | unsubscribed | bounced
  drip_step INTEGER NOT NULL DEFAULT 0,   -- 0..3 (sequence progress)
  unsubscribed_at TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_newsletter_status ON newsletter_subscribers (status);
CREATE INDEX idx_newsletter_drip ON newsletter_subscribers (status, drip_step);
```

---

## Drip Campaign Sequence (3 emails)

| Step | Trigger | Delay | Subject | Goal |
|------|---------|-------|---------|------|
| **Email 1** | Subscribe (drip_step: 0 → 1) | immediate | "Selamat datang di komunitas iklan Beriklan" | Konfirmasi + value |
| **Email 2** | After Email 1 | +3 days | "3 kesalahan umum iklan Meta di Indonesia" | Nurture + soft CTA |
| **Email 3** | After Email 2 | +7 days | "Studi kasus: ROAS 4,8× untuk klien fashion" | Case study + WhatsApp CTA |

### Email 1 — Welcome (Day 0)

**Subject:** Selamat datang di komunitas iklan Beriklan
**Body:**
```
Halo {name},

Terima kasih sudah bergabung. Kami kirim 1 update/bulan berisi:
- Tips eksekusi iklan dari 9 tahun pengalaman
- Data industri digital marketing Indonesia
- Studi kasus klien kami

Paling penting dari pengalaman kami: iklan yang berhasil bukan soal
budget terbesar — tapi soal konsistensi eksekusi + creative yang
selaras dengan audience Anda.

Kalau ada pertanyaan, balas email ini atau langsung chat WhatsApp:
wa.me/62811919328

Salam,
Tim Beriklan
```

### Email 2 — Common Mistakes (Day 3)

**Subject:** 3 kesalahan umum iklan Meta di Indonesia
**Body:**
```
Halo {name},

Setelah audit 250+ campaign, ada 3 pola yang paling sering muncul:

1. **Targeting melebar** — Interest stacking 20+ interest = audience
   quality rendah. Solusi: 2-3 interest bertumpuk, layered dengan
   behavior signal.

2. **Creative tidak selaras** — Visual menarik tapi copy tidak match
   intent audience. Solusi: Pisahkan creative per funnel stage.

3. **Landing page lambat** — 50% traffic hilang di 3 detik pertama.
   Solusi: Mobile-first, hapus slider, single CTA di atas fold.

Mau kami audit campaign Anda? Hubungi kami:
[wa.me/62811919328]

— Tim Beriklan
```

### Email 3 — Case Study (Day 7)

**Subject:** Studi kasus: ROAS 4,8× untuk klien fashion
**Body:**
```
Halo {name},

Cerita singkat dari klien fashion e-commerce kami (April 2025):

- Budget: Rp 8jt/bulan (Meta Ads)
- ROAS: 4,8× (rata-rata 3 bulan)
- Waktu setup: 14 hari
- Penjualan: 247 orders/bulan (was 38)

3 hal yang mereka ubah:
1. Creative dipecah 4 variant per funnel stage (TOF/MOF/BOF)
2. Landing page diganti dari homepage ke product-specific
3. Iklan dimatikan setiap jam 23.00-07.00 (audience tidak aktif)

Pelajaran: optimasi bukan soal naikkan budget, tapi soal
menghilangkan yang tidak konversi.

Mau strategi serupa untuk bisnis Anda?
[Diskusi via WhatsApp → wa.me/62811919328]

— Tim Beriklan
```

---

## Email Service Integration Options

### Option A: Brevo (recommended, free tier)
- Free: 300 emails/day (cukup untuk drip campaign kecil-menengah)
- Transactional + Marketing API
- DKIM/SPF otomatis

Steps:
1. Buat akun di brevo.com
2. Verify domain `beriklan.co.id` (tambah DNS records)
3. Buat API key di Settings → API
4. Set CF Worker secret `BREVO_API_KEY`
5. Implement `sendBrevoEmail(to, subject, body)` di worker
6. Cron trigger: `/api/newsletter/send-drip` — runs daily at 10am
7. Logic: SELECT subscribers WHERE drip_step IN (0,1,2) AND status='active' AND last_sent_at + interval cocok → send + UPDATE drip_step

### Option B: Cloudflare Email Service (advanced)
- Zero cost after setup
- Requires DKIM/SPF setup di CF dashboard
- Need Email Workers binding
- More setup but no third-party

### Option C: Mailchimp / MailerLite
- Mailchimp: free 500 contacts, expensive after
- MailerLite: free 1K subscribers
- Both have good APIs

---

## Implementation Roadmap

- [x] Form + D1 storage (P2.6 infra)
- [ ] Choose email service (Brevo recommended)
- [ ] Add `BREVO_API_KEY` to CF Worker secrets
- [ ] Implement `sendBrevoEmail()` worker function
- [ ] Build `/api/newsletter/send-drip` endpoint with cron
- [ ] Test with real subscriber end-to-end
- [ ] Document cadence in CF cron triggers (wrangler.jsonc)

---

## Admin Commands

```bash
# View subscribers (JSON)
curl "https://beriklan.co.id/api/newsletter/admin?token=ADMIN_TOKEN"

# Export active subscribers (CSV)
curl "https://beriklan.co.id/api/newsletter/admin?token=ADMIN_TOKEN&format=csv&status=active" -o newsletter.csv

# Manual unsubscribe
curl "https://beriklan.co.id/api/newsletter/unsubscribe?email=user@example.com"
```

---

## Compliance

- **GDPR / UU PDP**: Setiap email harus ada link unsubscribe. Form sudah include consent text.
- **Unsubscribe**: Setiap email blast harus include `?email=` link.
- **Data retention**: Subscribers yang unsubscribe disimpan (status field) untuk audit trail. Bisa di-DROP setelah 30 hari via cron cleanup.

---

**Maintainer:** Beriklan Digital Agency
**Created:** 21 Jul 2026 (P2.6)