# 🎯 Panduan Setup Google Ads — Fokus 3 Layanan (Lengkap)
**Beriklan.co.id** · Jasa Pembuatan Website · Jasa Iklan Google · Jasa View Live

> Semua setting di bawah ini tinggal **copy-paste** langsung ke Google Ads UI.
> Tidak perlu import CSV. Buka **ads.google.com** → login akun → ikuti step per step.
> Keyword diambil dari **Google Suggest real-time** (18–19 Juli 2026).

---

## 📋 STEP 0 — Persiapan Sebelum Buat Campaign

1. Login ke **https://ads.google.com**
2. Pastikan Conversion Action sudah ada:
   - Buka **Tools & Settings** (icon kunci pas) → **Conversions**
   - Pastikan ada: `WhatsApp Click` (value Rp 15.000) & `Form Submit` (value Rp 30.000)
   - Jika belum ada, harus pasang GTM `GTM-MJXSNCSD` di website dulu
3. Catat ID untuk nanti:
   - Google Ads ID: `AW-18065868782`
   - Conversion label: `vE_kCPvn-tEcEO6PvaZD`

---

## 💰 STEP 1 — Strategi Budget & Bidding

### Budget Harian (Total Rp 30.000/hari)

| Campaign | Budget Harian | Bid Strategy Awal | Max CPC Cap | Bid Strategy Lanjutan |
|----------|---------------|-------------------|-------------|-----------------------|
| Beriklan_Search_Website | Rp 12.000 | Maximize Clicks | Rp 3.000 | Target CPA (setelah 30 conv) |
| Beriklan_Search_GoogleAds | Rp 12.000 | Maximize Clicks | Rp 3.500 | Target CPA (setelah 30 conv) |
| Beriklan_Search_ViewLive | Rp 6.000 | Maximize Clicks | Rp 2.000 | Target CPA (setelah 30 conv) |

**Cara set bidding:**
1. Saat buat campaign → **Bidding** → pilih **"Clicks"** (Maximize Clicks)
2. Centang **"Set a maximum cost per click bid limit"** → isi angka Max CPC di atas
3. Setelah 30+ conversion → ganti ke **"Conversions"** → **"Target CPA"** → isi Rp 15.000

---

## 🔧 STEP 2 — Campaign 1: Jasa Pembuatan Website

**Cara:** `+ New Campaign` → Goal: **Sales / Leads** → Type: **Search** → Standard

### Pengaturan Campaign:
```
Campaign name:        Beriklan_Search_Website
Campaign type:        Search
Networks:             ✅ Search Network only (uncheck Display)
Budget:               Rp 12.000 / day
Bid strategy:         Maximize Clicks (cap Rp 3.000)
Start date:           Today
End date:             None
Languages:            Indonesian
Locations:            Indonesia (lihat STEP 5)
```

### Ad Group 1: Exact Match (High Intent)
**Name:** `AG_Website_Exact`

Copy-paste keyword (satu per baris, dengan tanda `[ ]`):
```
[jasa pembuatan website]
[jasa pembuatan website profesional]
[jasa pembuatan website murah]
[jasa pembuatan website company profile]
[jasa pembuatan website ecommerce]
[jasa pembuatan website toko online]
[jasa pembuatan website seo friendly]
[jasa pembuatan website landing page]
[buat website profesional]
[website company profile jasa]
[pembuatan website umkm]
[jasa pembuatan website dan hosting]
[jasa pembuatan website dan seo]
[jasa pembuatan website murah profesional]
[jasa pembuatan website wordpress]
[jasa pembuatan website custom]
[jasa pembuatan website online shop]
[jasa pembuatan website berita]
[jasa pembuatan website desa]
[jasa pembuatan website sekolah]
```

### Ad Group 2: Phrase Match (Medium Intent)
**Name:** `AG_Website_Phrase`

```
"jasa pembuatan website"
"jasa pembuatan website bandung"
"jasa pembuatan website jakarta"
"jasa pembuatan website surabaya"
"jasa pembuatan website jogja"
"jasa pembuatan website bali"
"jasa pembuatan website medan"
"jasa pembuatan website makassar"
"jasa pembuatan website semarang"
"jasa pembuatan website bogor"
"jasa pembuatan website depok"
"jasa pembuatan website tangerang"
"jasa pembuatan website bekasi"
"jasa pembuatan website murah"
"jasa pembuatan website profesional"
"jasa pembuatan website dan hosting"
"jasa pembuatan website dan seo"
"jasa pembuatan website landing page"
"jasa pembuatan website company profile"
"harga jasa pembuatan website"
"jasa pembuatan website terdekat"
"jasa pembuatan website cepat"
"jasa pembuatan website umkm"
"jasa pembuatan website toko online"
"jasa pembuatan website ecommerce"
```

### Ad Group 3: Broad Match (Discovery)
**Name:** `AG_Website_Broad`

```
jasa pembuatan website
buat website bisnis
website profil perusahaan
toko online murah
jasa web developer indonesia
company profile profesional
landing page conversion
jasa pembuatan website seo friendly
jasa pembuatan website online shop
jasa pembuatan website custom
website untuk bisnis
website untuk umkm
```

### Ad Copy (Responsive Search Ad) — Copy ke semua Ad Group:
**Final URL:** `https://beriklan.co.id/jasa-pembuatan-website/`
**Path 1:** `jasa-website`  **Path 2:** `harga`

**Headlines (paste 15):**
```
Jasa Pembuatan Website
Mulai Rp 999.000
Free Domain + Hosting 1 Thn
Selesai 7-14 Hari
SEO Optimized Built-in
Tim Senior 9 Tahun
Konsultasi Gratis 15 Menit
Garansi 30 Hari
CMS WordPress Include
Mobile Responsive
Company Profile Profesional
E-commerce Ready
Landing Page Cepat
Custom Design Premium
SEO Ready & Cepat
```

**Descriptions (paste 4):**
```
Website profesional: company profile, e-commerce, landing page. SEO ready + free domain hosting 1 tahun.
Mulai Rp 999rb. Selesai 7-14 hari. Garansi 30 hari. Konsultasi gratis via WhatsApp.
Tim berpengalaman 9 tahun. Akses penuh, revisi included. Berhenti? Tidak ada kontrak.
Website SEO friendly, mobile responsive, loading cepat. Free SSL + email profesional.
```

---

## 🔧 STEP 3 — Campaign 2: Jasa Iklan Google

**Cara:** `+ New Campaign` → Search → Standard

### Pengaturan Campaign:
```
Campaign name:        Beriklan_Search_GoogleAds
Campaign type:        Search
Networks:             ✅ Search Network only
Budget:               Rp 12.000 / day
Bid strategy:         Maximize Clicks (cap Rp 3.500)
Languages:            Indonesian
Locations:            Indonesia
```

### Ad Group 1: Exact Match
**Name:** `AG_GoogleAds_Exact`

```
[jasa iklan google]
[jasa iklan google ads]
[jasa google ads]
[jasa ads google]
[jasa iklan google profesional]
[jasa iklan google terbaik]
[jasa iklan google murah]
[jasa iklan google tertarget]
[google ads indonesia]
[kelola google ads]
[setting iklan google]
[jasa pasang iklan google]
[jasa bikin iklan google]
[jasa iklan google ads profesional]
[jasa iklan google ads murah]
[jasa iklan google ads terbaik]
[jasa iklan google maps]
[jasa iklan google tertarget]
```

### Ad Group 2: Phrase Match
**Name:** `AG_GoogleAds_Phrase`

```
"jasa iklan google"
"jasa iklan google ads"
"jasa iklan google jakarta"
"jasa iklan google bandung"
"jasa iklan google bali"
"jasa iklan google jogja"
"jasa iklan google surabaya"
"jasa iklan google medan"
"jasa iklan google makassar"
"jasa iklan google semarang"
"jasa iklan google depok"
"jasa iklan google bogor"
"jasa iklan google ads murah"
"jasa iklan google maps"
"jasa iklan google profesional"
"google ads specialist indonesia"
"kelola google ads"
"pasang iklan google"
"google ads untuk umkm"
"jasa iklan google tertarget"
```

### Ad Group 3: Broad Match
**Name:** `AG_GoogleAds_Broad`

```
jasa iklan google
google ads management
google search ads indonesia
iklan produk di google
google ads untuk umkm
google ads agency jakarta
jasa pasang iklan google
iklan di halaman pertama google
jasa iklan google tertarget
google ads untuk bisnis
```

### Ad Copy (Responsive Search Ad):
**Final URL:** `https://beriklan.co.id/jasa-iklan-google/`
**Path 1:** `google-ads`  **Path 2:** `paket`

**Headlines (paste 15):**
```
Jasa Iklan Google Ads
Muncul Halaman 1 Google
Mulai Rp 1,75 Juta
Hanya Bayar per Klik
Google Partner Certified
Audit Akun Gratis
Konsultasi 15 Menit
Optimasi Harian
Laporan Mingguan
Tanpa Kontrak
Google Ads Certified
Target Kata Kunci Akurat
ROI Terukur & Transparan
Akses Penuh ke Akun
Setup Tracking Lengkap
```

**Descriptions (paste 4):**
```
Google Ads bersertifikat. Halaman 1 Google. Bayar per klik. Akses penuh akun.
Mulai Rp 1,75 jt/bln + ad spend. Optimasi harian + laporan mingguan. Audit gratis.
Tim certified Google. Target kata kunci akurat. ROI terukur. Berhenti kapan saja.
Setup conversion tracking + Google Analytics. Optimasi bidding otomatis cerdas.
```

---

## 🔧 STEP 4 — Campaign 3: Jasa View Live

**Cara:** `+ New Campaign` → Search → Standard

### Pengaturan Campaign:
```
Campaign name:        Beriklan_Search_ViewLive
Campaign type:        Search
Networks:             ✅ Search Network only
Budget:               Rp 6.000 / day
Bid strategy:         Maximize Clicks (cap Rp 2.000)
Languages:            Indonesian
Locations:            Indonesia
```

> ⚠️ **CATATAN PENTING:** Di ad copy **JANGAN** tulis "TikTok" atau "Shopee" (melanggar ToS Google Ads).
> Gunakan istilah generik: "Video Views", "Live Streaming Boost", "Viewer Real".

### Ad Group 1: Video Views (TikTok)
**Name:** `AG_ViewLive_TikTok`

```
[jasa view live tiktok]
[jasa tambah view live tiktok]
[jasa tambah view live]
[boost viewer live tiktok]
[boost views live tiktok]
[jasa view live streaming]
[jasa view live streaming youtube]
"jasa view live"
"tambah viewer live"
"boost views live"
"jasa penambah viewer"
"live streaming views"
"penambah view video"
"cara boost viewer live tiktok"
"jasa view streaming"
```

### Ad Group 2: Marketplace Live (Shopee)
**Name:** `AG_ViewLive_Shopee`

```
[jasa view live shopee]
[boost live shopee]
"jasa view live shopee"
"boost live shopping"
"viewer live marketplace"
"live gmv boost"
"live gmv viewer boost"
"jasa view live marketplace"
```

### Ad Copy (Responsive Search Ad):
**Final URL:** `https://beriklan.co.id/jasa-view-live/`
**Path 1:** `view-live`  **Path 2:** `harga`

**Headlines (paste 15):**
```
Jasa View Live Streaming
Boost Viewer Real
Mulai Rp 12.000
Aman untuk Akun
Proses 5-15 Menit
Garansi 100%
Support 24/7
Konsultasi Gratis
Video Views Pro
Live Boost
Viewer Real Account
Algoritma Notice Live
Boost Distribusi Live
Multi-Platform Support
Untuk Kreator & Seller
```

**Descriptions (paste 4):**
```
Viewers real account, no bot. Aman untuk live streaming Anda. Mulai Rp 12rb.
Boost live views gradual 5-15 menit. Algoritma notice live Anda. Garansi 100%.
Untuk kreator & seller. Multi-platform. Chat WA untuk order sekarang.
Viewers masuk natural, stay selama live. Tidak trigger shadow ban.
```

---

## 📍 STEP 5 — Geo-Targeting (Untuk Semua Campaign)

**Cara:** Campaign → Settings → Locations → **Edit locations**

1. Search & add: `Indonesia`
2. Lalu klik campaign → **Location options (advanced)** → pilih:
   - ✅ "Presence or interest: People in or who show interest in your targeted locations"

**Bid adjustments per kota:**
- Buka campaign → **Ad Group** → pilih ad group → **Settings** → **Location** → bid modifier:

| Kota | Bid Modifier |
|------|--------------|
| Jakarta, Bandung, Surabaya, Medan, Makassar, Semarang | `+50%` |
| Bekasi, Bogor, Depok, Tangerang, Yogyakarta, Denpasar, Palembang, Malang | `0%` (default) |
| Aceh, Batam, Cimahi, Lampung, Lombok, Padang, Pontianak, Solo | `-30%` |

---

## 👥 STEP 6 — Audience Targeting (Observation)

**Cara:** Campaign → **Audiences** → tab **Edit audiences** → pilih **Observation**

Tempelkan ini:
- **In-market:** Business services, Advertising & Marketing, Web Design
- **Affinity:** Business owners, Entrepreneurs, Marketing professionals
- **Life events:** Recently started business, Expanding business
- **Demographics:** Age 25–55, All genders, Income Top 25–50%

---

## ⏰ STEP 7 — Ad Schedule

**Cara:** Campaign → **Ad schedule** → `+ Add schedule`

- Set: **Every day, 08:00 – 24:00**
- Lalu klik **Bid adjustments** → set:
  - 08:00–22:00 → `+0%` (default)
  - 22:00–08:00 → `-20%`

---

## 🚫 STEP 8 — Negative Keywords (WAJIB)

**Cara:** **Tools & Settings** → **Negative Keywords** → **+** (Account level)

Copy-paste semua baris berikut (satu per baris):

```
gratis
free
contoh
template
tutorial
cara
belajar
lowongan
kerja
freelance
magang
download
pdf
skripsi
thesis
info loker
lowongan kerja
cara bikin
how to
belajar html
belajar css
kursus
sertifikasi gratis
contoh website
template website
download source code
freelance web developer
lowongan web developer
wordpress tutorial
belajar wordpress
cara bikin website sendiri
website sekolah gratis
website desa gratis
website gratis untuk umkm
top up game
streaming film
website judi
website slot
website togel
website porno
website dewasa
cara pasang iklan google sendiri
google ads gratis
belajar google ads
kursus google ads
sertifikasi google ads gratis
google ads voucher gratis
iklan google gratis tanpa biaya
lowongan google ads
freelance google ads
bot
palsu
fake
cara manual
script
apk
mod
cheat
view bot gratis
view palsu gratis
cara nambah view sendiri
aplikasi penambah view
web penambah view gratis
```

---

## 📈 STEP 9 — Ad Extensions (Lengkap)

**Cara:** Campaign → **Ads & extensions** → **Extensions** → `+` untuk tiap tipe

### 1. Sitelinks (4 per campaign)
| Sitelink Text | Description Line 1 | Description Line 2 | Final URL |
|---------------|-------------------|-------------------|-----------|
| Layanan Kami | Semua layanan digital marketing | Meta, Google, TikTok, Website | `/jasa-digital-marketing/` |
| Studi Kasus | Portofolio klien kami | Hasil campaign terukur | `/klien/` |
| Metodologi | Cara kerja kami | 3 fase audit & optimasi | `/metodologi/` |
| Konsultasi | Hubungi tim kami | Respon dalam 1 jam | `/kontak/` |

### 2. Callouts (6 per campaign)
```
Konsultasi 15 Menit Gratis
9 Tahun Pengalaman
Tim Bersertifikasi Meta & Google
Laporan Mingguan
Akses Penuh ke Akun
Tanpa Kontrak Minimum
```

### 3. Structured Snippets
```
Service catalog: Digital Marketing, Google Ads, Facebook Ads, TikTok Ads, Website Development, Landing Page
Type: Agency, Konsultan, Profesional
```

---

## 🚀 STEP 10 — Launch & Optimasi

### Minggu 1–2: Learning Phase
- Aktifkan ketiga campaign (toggle → Enabled)
- **JANGAN** pause apa pun (biar algoritma Google belajar)
- Cek setiap hari: impressions, clicks, CTR, CPC

### Minggu 3: Optimize
- Pause keyword dengan **0 conversion + high spend**
- Naikkan budget ke ad group dengan CPA terendah
- Ganti ad copy yang CTR < 3%

### Minggu 4+: Scale
- Naikkan budget 20–30%/minggu (hanya campaign yang convert)
- Ganti bid strategy ke **Target CPA** (isi Rp 15.000) setelah 30+ conversions
- Tambah keyword dari tab **Search Terms** (Keywords → Search terms)

---

## 📊 Target Kinerja (Benchmark)

| Metric | Website | Google Ads | View Live |
|--------|---------|-----------|-----------|
| Clicks/hari | 4–8 | 4–8 | 2–4 |
| CTR | 5–8% | 5–10% | 3–5% |
| CPC rata² | Rp 1.500–2.500 | Rp 2.000–3.500 | Rp 1.500–2.500 |
| Conv/hari | 1–2 | 1–2 | 0.5–1 |
| CPA target | Rp 15.000 | Rp 15.000 | Rp 20.000 |

---

## ✅ CHECKLIST SEBELUM GO LIVE

- [ ] 3 campaign dibuat (Website, Google Ads, View Live)
- [ ] Total budget Rp 30.000/hari
- [ ] Bid strategy: Maximize Clicks + Max CPC cap
- [ ] 8 ad group aktif
- [ ] RSA (Responsive Search Ad) di setiap ad group (15 headlines, 4 descriptions)
- [ ] Negative keywords account-level di-paste
- [ ] Geo-targeting + bid modifier kota
- [ ] Audience observation aktif
- [ ] Ad schedule 08:00–24:00
- [ ] Extensions (4 sitelink + 6 callout + 2 snippet) aktif
- [ ] Conversion tracking verify (test WA click)
- [ ] Max CPC cap di-set (3.000 / 3.500 / 2.000)
