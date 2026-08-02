# PLAN — Automated Prospecting & Email Marketing System

> **Tujuan:** Generate leads setiap hari otomatis via scraper → email campaign → Google Ads.
> **Mulai:** 22 Juli 2026
> **Status:** 🔴 Belum dimulai

---

## Arsitektur

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Scraper Scripts │───▶│  Email Campaign  │───▶│  Google Ads API  │
│  (Python)        │    │  (Worker + Brevo)│    │  (Customer Match)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
       │                       │                       │
       ▼                       ▼                       ▼
   CSV / D1              D1 tables              Google Ads UI
                          + Cron send            + PMax Campaign
```

### Komponen

| Komponen | Bahasa | Infra | Biaya |
|----------|--------|-------|-------|
| Scraper Indonetwork | Python | Local/Mac | Gratis |
| Scraper Google Business | Python | Local/Mac | Gratis (Places API free tier) |
| Scraper Shopee | Python | Local/Mac | Gratis |
| Email Campaign System | JS | Cloudflare Worker + D1 | Gratis |
| Email Sending | REST API | **Brevo (Sendinblue)** | **Free: 300 email/hari** |
| Google Ads API | Python | Local/Mac | Gratis (existing API key) |

---

## Phase 1: Email Campaign System (Worker)

### Tables Baru di D1

```sql
-- Template email dengan HTML
CREATE TABLE email_templates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  subject TEXT NOT NULL,
  html_body TEXT NOT NULL,
  category TEXT, -- promo, newsletter, followup
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Campaign: 1 campaign = 1 template + 1 target list
CREATE TABLE campaigns (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  template_id INTEGER REFERENCES email_templates(id),
  target TEXT, -- 'all', 'corporate', 'ukm', or custom list name
  status TEXT DEFAULT 'draft', -- draft, sending, done, paused
  total_recipients INTEGER DEFAULT 0,
  sent_count INTEGER DEFAULT 0,
  open_count INTEGER DEFAULT 0,
  click_count INTEGER DEFAULT 0,
  scheduled_at TEXT,
  sent_at TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Queue pengiriman per email
CREATE TABLE email_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  campaign_id INTEGER REFERENCES campaigns(id),
  email TEXT NOT NULL,
  name TEXT,
  status TEXT DEFAULT 'pending', -- pending, sent, failed, bounced
  error TEXT,
  sent_at TEXT,
  opened_at TEXT,
  clicked_at TEXT,
  tracking_id TEXT UNIQUE -- unique ID untuk tracking pixel
);

-- List dari hasil scraper (bisa di-import ke campaign)
CREATE TABLE lead_lists (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL, -- misal 'indonetwork-manufaktur-bandung'
  source TEXT, -- 'indonetwork', 'google_business', 'shopee', 'database'
  total INTEGER DEFAULT 0,
  imported_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE lead_contacts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  list_id INTEGER REFERENCES lead_lists(id),
  email TEXT,
  phone TEXT,
  name TEXT,
  company TEXT,
  website TEXT,
  city TEXT,
  category TEXT,
  extra JSON -- data tambahan (rating, produk, dll)
);
```

### Endpoint Baru di Worker

```
GET  /api/email/templates           — List template
POST /api/email/templates           — Create template
GET  /api/email/templates/:id       — Preview template
POST /api/email/campaigns           — Create campaign
POST /api/email/campaigns/:id/send  — Start sending
GET  /api/email/campaigns           — List campaign + stats
GET  /api/email/campaigns/:id       — Detail campaign
GET  /api/email/track/open.gif?id=X — Tracking pixel (1x1)
GET  /api/email/track/click?id=X&url= — Click redirect
GET  /api/email/lists               — Lead list manager
POST /api/email/lists/import        — Import CSV ke lead_lists
POST /api/email/unsubscribe         — Existing (re-use)
```

### Template System

Email templates dalam HTML dengan design brand beriklan.co.id:

```html
<!-- Template structure -->
<table width="100%" style="max-width:600px;margin:auto;font-family:Inter,sans-serif;">
  <!-- Header: Logo Beriklan -->
  <tr><td style="padding:24px 0;text-align:center;">
    <img src="https://beriklan.co.id/logoweb.webp" height="40" alt="Beriklan">
  </td></tr>

  <!-- Hero: Judul + CTA -->
  <tr><td style="background:#0f1e3d;border-radius:16px;padding:32px;text-align:center;">
    <h1 style="color:#fff;font-size:24px;margin:0 0 12px;">{{ title }}</h1>
    <p style="color:#94a3b8;margin:0 0 20px;">{{ subtitle }}</p>
    <a href="{{ cta_url }}" style="display:inline-block;background:#f59e0b;color:#0f1e3d;padding:12px 32px;border-radius:100px;font-weight:700;text-decoration:none;">
      {{ cta_text }}
    </a>
  </td></tr>

  <!-- Body sections -->
  <tr><td style="padding:24px 0;">
    {{ body_html }}
  </td></tr>

  <!-- Footer -->
  <tr><td style="padding:24px 0;border-top:1px solid #e2e8f0;font-size:12px;color:#94a3b8;text-align:center;">
    <p>Beriklan Digital Agency · Jl. Arcamanik Endah No.76, Bandung 40195</p>
    <p><a href="{{ unsubscribe_url }}" style="color:#94a3b8;">Berhenti berlangganan</a></p>
  </td></tr>
</table>
```

### Sending Logic

```javascript
// Worker cron: every 15 minutes (3,18,33,48 * * * *)
async function handleEmailQueue(env) {
  // 1. Ambil 50 email dari queue WHERE status='pending' LIMIT 50
  // 2. Kirim via Brevo API: POST https://api.brevo.com/v3/smtp/email
  // 3. Update status: sent / failed
  // 4. Log ke email_logs
  // Rate limit: 300/day Brevo = ~12-15/jam = ~4 per 15 menit
  // Safety: jangan kirim > 300 dalam 24 jam
}
```

### Cron Schedule untuk Email

| Cron | Action | Rate |
|------|--------|------|
| `3,18,33,48 * * * *` | Send email queue | ~4 per run = ~16/jam |
| `0 8 * * 1-5` | Kirim promo ke list baru | Weekdays only |

---

## Phase 2: Indonetwork Scraper (Python)

### Target

Indonetwork punya ~500rb perusahaan Indonesia terdaftar. Kita scrape:
- Yang punya email publik
- Yang TIDAK punya website (target jasa pembuatan website)
- Yang bergerak di bidang: manufaktur, distributor, jasa, retail, properti, dll

### Approach

```python
# Tidak pakai Selenium/Playwright — cukup requests + BeautifulSoup
# Indonetwork anti-scraping minimal (B2B directory)

BASE_URL = "https://www.indonetwork.co.id"

def get_categories():
    # Ambil daftar kategori dari halaman utama
    # Return: [{'name': 'Manufaktur', 'url': '/category/manufaktur'}, ...]

def get_company_list(category_url, page=1):
    # Ambil halaman kategori → dapat company cards
    # Return: [{'name': 'PT ABC', 'url': '/company/pt-abc', 'city': 'Bandung'}, ...]

def get_company_detail(company_url):
    # Ambil halaman company → dapat email, phone, website
    # Return: {'email': '...', 'phone': '...', 'website': '...', 'products': [...]}

def scrape_category(category, max_pages=50):
    # Loop pages → kumpulin companies
    # Filter: yang punya email
    # Output: CSV
```

### Output

```csv
source,name,email,phone,website,city,category,products
indonetwork,PT ABC,info@abc.com,0812-3456-7890,,Bandung,Manufaktur,"produk1, produk2"
indonetwork,CV XYZ,admin@xyz.com,022-123456,https://xyz.com,Jakarta,Distributor,""
```

### Auto-Import Pipeline

```
Scraper selesai → CSV generated → POST ke /api/email/lists/import
                    → Masuk ke lead_lists + lead_contacts
                    → Siap dijadikan campaign
```

### Kategori yang Akan Di-scrape (Prioritas)

| Prioritas | Kategori | Jumlah Estimasi | Relevansi |
|-----------|----------|----------------|-----------|
| 🥇 | Manufaktur | ~50.000 | Tinggi (butuh website + iklan) |
| 🥇 | Distributor | ~30.000 | Tinggi |
| 🥇 | Jasa (service) | ~40.000 | Tinggi |
| 🥇 | Properti / Developer | ~15.000 | Tinggi (kompetitif) |
| 🥈 | Retail / Toko | ~25.000 | Sedang |
| 🥈 | Makanan & Minuman | ~20.000 | Sedang |
| 🥈 | Fashion | ~15.000 | Sedang (banyak UMKM tanpa website) |
| 🥉 | Otomotif | ~10.000 | Rendah |
| 🥉 | Elektronik | ~10.000 | Rendah |

Target: **minimal 200 lead valid/hari** (yang punya email publik).

---

## Phase 3: Google Business Scraper (Python + Places API)

### Approach

```python
import requests

API_KEY = "YOUR_GOOGLE_PLACES_API_KEY"

def search_businesses(query, location):
    # GET https://maps.googleapis.com/maps/api/place/textsearch/json
    #   ?query={query}+{location}
    #   &key={API_KEY}
    # Parse results → filter yang TIDAK punya website
    # Return: [{'name': '...', 'address': '...', 'phone': '...', 'rating': '...'}]

def get_business_details(place_id):
    # GET https://maps.googleapis.com/maps/api/place/details/json
    #   ?place_id={place_id}
    #   &fields=name,formatted_phone_number,website,formatted_address,rating
    #   &key={API_KEY}
    # Return detailed info
```

### Query yang Akan Digunakan

```
"jasa manufaktur bandung"
"toko bangunan jakarta"
"distributor makanan surabaya"
"fashion retail bandung"
"properti developer jakarta"
"rumah makan medan"
"toko elektronik solo"
...
```

Target: **50 query × 20 hasil = 1.000 bisnis/hari**, filter yang tanpa website = ~300-400 lead.

### Output

```csv
source,name,address,phone,rating,has_website
google_business,Toko Bangunan ABC,Jl. Merdeka No.1 Bandung,0812-3456-7890,4.2,FALSE
google_business,CV Manufaktur XYZ,Jl. Sudirman Jakarta,021-123456,3.8,TRUE
```

---

## Phase 4: Shopee Scraper (Python)

### Approach

```python
# Shopee punya public API endpoint:
# GET https://shopee.co.id/api/v2/search_items/
#   ?by=relevance&keyword={category}&limit=50&newest={offset}
#
# Dari hasil search → ambil shopid → detail seller:
# GET https://shopee.co.id/api/v2/shop/get?shopid={shopid}

# Yang dicari: seller dengan product_count < 10 atau rating rendah
# → Indikasi butuh bantuan digital marketing
```

### Target Seller

```
- Seller dengan < 10 produk (jarang update)
- Seller dengan rating < 4.0 (perlu optimasi)
- Seller baru (< 30 hari) (perlu promosi)
- Kategori: fashion, elektronik, rumah tangga, makanan
```

### Output

```csv
source,shop_name,email,product_count,rating,created,location
shopee,Toko Murah Jaya,,5,3.2,2026-06-01,Bandung
```

**Catatan:** Shopee TIDAK menampilkan email seller publik. Scraper Shopee lebih untuk **riset segmen** — dapat nama toko + kategori + lokasi → cari email-nya via Indonetwork atau Google.

---

## Phase 5: Google Ads API — Customer Match + PMax

### Approach

```python
from google.ads.googleads.client import GoogleAdsClient

client = GoogleAdsClient.load_from_storage("google-ads.yaml")

def create_customer_match_audience(email_list, audience_name):
    # 1. Hash semua email dengan SHA-256
    # 2. Buat Customer Match user list via Google Ads API
    # 3. Upload hashed emails
    # 4. Link ke campaign Display/PMax

def create_pmax_campaign(audience_id, budget_daily=50000):
    # Buat Performance Max campaign
    # Target: Customer Match audience
    # Budget: Rp 50.000/hari (test)
```

### Flow

```
Scraper → CSV → Email hash → Upload ke Google Ads → PMax campaign live
```

### Policy Check

Google Ads Customer Match mensyaratkan:
- Data first-party (email dari orang yang sudah berinteraksi dengan bisnis Anda) **ATAU**
- Data dari mitra yang memiliki izin eksplisit

**Untuk database yang dibeli/scrape:** Risiko suspend. Tapi kalau email dari:
- Database korporat (B2B email perusahaan publik) → lebih aman
- Hasil scrape Indonetwork (email perusahaan yang sengaja dipublikasikan) → grey area
- Hasil scrape Google Business → melanggar ToS Google

**Rekomendasi:** Pakai Google Ads API untuk **sitewide PMax** dulu (retarget visitor website, bukan cold list). Customer Match dari data scraped mulai hati-hati dengan list kecil dulu.

---

## Phase 6: Integrasi & Otomatisasi

### Pipeline Lengkap

```
┌─────────────────────────────────────────────────────┐
│                    Daily Pipeline                    │
├─────────────────────────────────────────────────────┤
│                                                      │
│  06:00  Scrape Indonetwork (5 kategori)              │
│  07:00  Scrape Google Business (10 query)            │
│  08:00  Clean & deduplicate leads                    │
│  08:30  Import ke D1 (POST /api/email/lists/import)  │
│  09:00  Create campaign + start sending              │
│  09:00  Upload email list ke Google Ads API           │
│  (every 15min)  Send email queue                     │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### File Structure

```
scripts/
├── email_system/               # (di Worker, bukan folder)
│   └── (endpoints di worker-entry.js)
├── scrapers/
│   ├── indonetwork.py          # Phase 2
│   ├── google_business.py      # Phase 3
│   └── shopee_analyzer.py      # Phase 4
├── google_ads/
│   └── customer_match.py       # Phase 5
├── run_daily.sh                # Orchestrator (cron local)
└── config.py                   # API keys, limits, etc.
```

---

## Setup Yang Dibutuhkan

### Dari User

| Item | Untuk | Cara Dapat |
|------|-------|------------|
| **Brevo API Key** | Email sending (300/hari free) | Daftar di brevo.com → API → API Key |
| **Google Places API Key** | Google Business scraper | Google Cloud Console → Places API → Enable → Create Key |
| **Google Ads API Config** | Customer Match + PMax | `google-ads.yaml` (developer token + client ID + client secret + refresh token) |

### Dari Saya

| Item | Waktu | Status |
|------|-------|--------|
| Worker: email tables + endpoints | ~4 jam | 🔴 |
| Worker: Brevo integration + queue | ~3 jam | 🔴 |
| Worker: tracking pixel | ~1 jam | 🔴 |
| Scraper: Indonetwork.py | ~3 jam | 🔴 |
| Scraper: Google Business.py | ~2 jam | 🔴 |
| Scraper: Shopee analyzer.py | ~2 jam | 🔴 |
| Google Ads: Customer Match script | ~2 jam | 🔴 |
| Orchestrator: run_daily.sh | ~1 jam | 🔴 |
| Design: 3 email templates | ~2 jam | 🔴 |
| **Total** | **~20 jam** | |

---

## Roadmap

```
Minggu 1:  Worker email system + Indonetwork scraper
Minggu 2:  Google Business scraper + tracking + auto pipeline
Minggu 3:  Google Ads API integration + Shopee analyzer
Minggu 4:  Optimization + scale
```

---

## Email: Kenapa Brevo (Sendinblue)?

| Fitur | Brevo Free | Mailchimp Free | AWS SES |
|-------|-----------|---------------|---------|
| Email/hari | **300** | 500/bln total | 62.000/bln |
| API | REST ✅ | REST ✅ | SMTP/API |
| Template | ✅ HTML | ✅ Drag-drop | ❌ No |
| Tracking | ✅ Open + Click | ✅ | ✅ |
| Indonesia deliverability | ✅ Bagus | ⚠️ Sedang | ✅ Bagus |
| Setup SPF/DKIM | ✅ Auto-guide | ✅ Auto | ❌ Manual |

**Brevo** adalah pilihan terbaik untuk Indonesia:
- 300 email/hari gratis = 9.000 email/bulan
- REST API langsung bisa integrasi ke Worker (no SMTP library needed)
- Deliverability bagus untuk domain Indonesia
- Built-in unsubscribe handling

---

## Catatan

1. **Sistem SEO yang sudah jalan TIDAK disentuh** — tidak ada perubahan ke cron, article generation, sitemap, atau dashboard
2. Semua kode baru ada di: endpoint Worker baru (`/api/email/*`) + folder `scripts/scrapers/`
3. Google Ads API hanya untuk Customer Match + PMax — tidak mengubah struktur akun existing
4. Database existing (keyword_queue, dll) tidak diubah — hanya menambah tabel baru
5. Scraping dilakukan legal: hanya data publik, rate-limited, user-agent jelas
