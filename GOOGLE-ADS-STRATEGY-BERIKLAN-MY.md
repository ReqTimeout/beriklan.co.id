# 🎯 STRATEGI GOOGLE ADS — BERIKLAN.MY (Malaysia)

> **Dokumen operasional siap copy-paste ke Google Ads.**
> Disusun dari data riset nyata: 6.155 keyword hasil mining pasar MY (Google Autocomplete + expansion),
> benchmark CPC Malaysia 2026, dan harga layanan beriklan.my (RM).
> Landing page: `https://beriklan.my/` · Konversi: WhatsApp click (sudah terpasang).

---

## ⚠️ 0. REALITA BUDGET — BACA DULU SEBELUM APAPUN

**Budget Anda: Rp 30.000/hari ≈ RM 8,70/hari ≈ USD 1,85/hari** (kurs ±1 MYR = Rp 3.450).

Ini **sangat kecil** untuk pasar Malaysia. Data benchmark CPC Malaysia 2026 (sumber: 2Stallions):

| Kategori industri | CPC rata-rata (RM) | Cost/Lead (RM) |
|---|---|---|
| Business Services / B2B (← kategori kita: "agency") | **RM 3,00 – 6,00** | RM 100 – 200 |
| Education | RM 2,50 – 5,50 | RM 60 – 150 |
| E-commerce & Retail | RM 0,80 – 2,50 | RM 10 – 60 |
| F&B / Restoran | RM 0,80 – 2,00 | RM 15 – 40 |
| **Keyword Bahasa Melayu (BM)** | **jauh lebih murah** (persaingan rendah) | — |

**Konsekuensi angka:**
- Kalau bid di keyword head "*google ads agency malaysia*" (CPC ±RM 4–6) → budget RM 8,70 hanya dapat **±1,5–2 klik/hari**. Tidak cukup untuk belajar/optimasi.
- Kalau fokus keyword **BM long-tail** (CPC ±RM 0,60–1,50) → dapat **±5–12 klik/hari**. **Ini satu-satunya jalan realistis di budget ini.**

**Aturan "10x CPC" Google:** budget harian ideal ≥ 10× CPC. Dengan RM 8,70/hari → **target CPC ≤ RM 0,87** (ideal) atau **cap CPC RM 1,50** (maksimal dipaksakan). Artinya **Fase 1 wajib keyword termurah + intent tertinggi saja** — bukan semua layanan.

> **Keputusan strategi:** Dokumen ini menyusun struktur **SEMUA 11 layanan** (agar siap), tapi **aktivasi bertahap**. Fase 1 hanya 1 campaign / 2 ad group termurah. Sisanya aktif saat budget naik.

---

## 1. RINGKASAN EKSEKUTIF

| Item | Keputusan |
|---|---|
| Jenis campaign Fase 1 | **Search** (bukan PMax/Display — Search = intent tertinggi, kontrol penuh) |
| Bahasa Fase 1 | **Bahasa Melayu (BM)** — CPC lebih murah, persaingan rendah (rekomendasi resmi Google utk MY) |
| Bid strategy Fase 1 | **Manual CPC** + Enhanced CPC OFF → **Maximize Clicks dengan Max CPC cap RM 1,50** |
| Target lokasi | Klang Valley dulu (KL, PJ, Shah Alam, Subang, Klang) — daya beli tertinggi |
| Match type | **Phrase** (utama) + **Exact** (keyword juara) — HINDARI Broad di budget kecil |
| Konversi | WhatsApp click (AW-18065868782) — **sudah live** |
| Nilai konversi | Rp 1.000/konversi (lihat §10 — catatan penting soal ROAS) |
| Deliverable ad | RSA: **15 headline + 4 deskripsi** per ad group, mengandung keyword ad group |

---

## 2. SUMBER DATA (biar tidak salah)

1. **Keyword mining MY** — `keyword-queue.json` (6.155 keyword, 298k total expanded), difilter `source = suggest_my` (= keyword yang BENAR muncul di Google Autocomplete Malaysia = permintaan nyata) dan intent `transactional`/`commercial`.
2. **Benchmark CPC Malaysia 2026** — 2Stallions Google Ads Cost Guide MY.
3. **Harga layanan** — `services.json` beriklan.my (RM 990–2.990 untuk paket ads management).
4. **Kota + tier** — `cities.json` (26 kota MY, tier 1–3).

> ⚠️ **Catatan volume:** angka *search volume* eksak hanya bisa dikonfirmasi di **Google Keyword Planner** (login akun Ads Anda → Tools → Keyword Planner → paste keyword di §12). Keyword di dokumen ini sudah **terkurasi dari data autocomplete nyata** (artinya ada orang mencarinya), tapi verifikasi volume+CPC final di Keyword Planner sebelum set bid.

---

## 3. STRUKTUR AKUN (Campaign → Ad Group → Keyword)

Naming convention: `[MY] [Network] [Layanan] [Bahasa]`

```
AKUN: beriklan.my (AW-18065868782)
│
├── CAMPAIGN 1  [MY] Search - Paid Ads Core - BM        ← FASE 1 (AKTIF SEKARANG)
│     ├── AG: Facebook Ads (BM)
│     └── AG: Google Ads (BM)
│
├── CAMPAIGN 2  [MY] Search - Paid Ads Expand - BM/EN   ← FASE 2
│     ├── AG: TikTok Ads
│     ├── AG: Instagram Ads
│     └── AG: YouTube Ads
│
├── CAMPAIGN 3  [MY] Search - Web & Landing - BM/EN     ← FASE 2
│     ├── AG: Website Development
│     └── AG: Landing Page Design
│
├── CAMPAIGN 4  [MY] Search - Digital Marketing - EN    ← FASE 3 (head term mahal)
│     └── AG: Digital Marketing Agency
│
├── CAMPAIGN 5  [MY] Search - Social Management - EN     ← FASE 3
│     ├── AG: Instagram Management
│     └── AG: TikTok Management
│
└── CAMPAIGN 6  [MY] Search - Live Viewers - EN          ← FASE 3 (niche)
      └── AG: Live Stream Viewers (YT/TikTok/Shopee/IG/Twitch)
```

**Kenapa dipisah per campaign?** Budget & bid diatur di level campaign. Memisah = Anda kontrol penuh ke mana Rp 30.000 mengalir (semua ke Fase 1 dulu). Ad group hanya untuk relevansi keyword→iklan (Quality Score).

---

## 4. RENCANA AKTIVASI BERTAHAP (sesuai kenaikan budget)

| Fase | Budget harian | Yang diaktifkan | Target |
|---|---|---|---|
| **FASE 1** (sekarang) | **RM 8,70 (Rp 30rb)** | Campaign 1 saja: Facebook Ads + Google Ads (BM, phrase/exact murah) | Dapat 3–8 klik/hari, kumpulkan 15–30 konversi utk data |
| **FASE 2** | RM 30–50/hari | + Campaign 2 & 3 (TikTok, IG, YouTube Ads, Website, Landing Page) | Perluas layanan, tambah keyword EN |
| **FASE 3** | RM 80–150/hari | + Campaign 4,5,6 (Digital Marketing head term, Management, Live Viewers) + PMax | Dominasi + Smart Bidding (tCPA/tROAS) |

**Trigger naik fase:** naik ke Fase 2 hanya setelah Campaign 1 stabil (CTR > 4%, ada ≥ 15 konversi, CPA terukur). Jangan lebar sebelum sempit terbukti.

---

## 5. BID STRATEGY (detail)

### Fase 1 (budget kecil — WAJIB begini):
- **Strategy:** `Maximize clicks` **DENGAN** "Maximum CPC bid limit" = **RM 1,50**.
  - Kenapa bukan Maximize Conversions / tCPA? → Smart Bidding butuh ≥ 15–30 konversi/bulan + budget ≥ 10× CPC untuk belajar. Di RM 8,70/hari algoritma "kelaparan data" → boros. **Manual/Max-clicks-capped lebih hemat & terkontrol.**
- **Max CPC cap RM 1,50** memaksa Google hanya ambil klik murah → stretch budget jadi 5–8 klik/hari.
- Matikan **"Search partners"** dan **"Display Network"** (opsi di campaign) → kualitas trafik lebih tinggi, hemat.

### Fase 2:
- Naikkan cap ke RM 2,50. Boleh mulai `Maximize conversions` SETELAH ada ≥ 30 konversi historis.

### Fase 3:
- `Target CPA` (set = 0,7× CPA aktual Anda) atau `Target ROAS` (setelah nilai konversi realistis diisi — lihat §10).

---

## 6. TARGET LOKASI (GEO) + BID ADJUSTMENT

Sumber `cities.json` — prioritas berdasarkan daya beli & kepadatan SME.

### Fase 1 — Klang Valley saja (konsentrasi budget):
```
Kuala Lumpur, Petaling Jaya, Shah Alam, Subang Jaya, Klang (+ radius 20km dari KL)
```
Setting lokasi: **"Presence: People in or regularly in your targeted locations"** (BUKAN "interest") — supaya hanya orang yang benar-benar di Malaysia, bukan yang sekadar "tertarik".

### Fase 2 — tambah Tier 1 lain:
```
+ Johor Bahru, Penang (Georgetown)
```

### Fase 3 — seluruh Malaysia + bid adjustment:
| Kota / area | Bid adjustment | Alasan |
|---|---|---|
| Kuala Lumpur, Petaling Jaya | **+15%** | Daya beli & konversi tertinggi |
| Johor Bahru, Penang | +10% | Hub bisnis, lintas-batas SG |
| Shah Alam, Subang, Klang | 0% (baseline) | Volume SME besar |
| Kota Tier 3 (Kuantan, Kota Bharu, dll) | **−20%** | Konversi lebih rendah |
| Luar Malaysia | **Exclude** | Buang trafik tidak relevan |

---

## 7. JADWAL TAYANG (AD SCHEDULE / DAYPARTING)

Klien B2B/SME cari agency saat **jam kerja**. Di budget kecil, matikan jam sepi = hemat.

### Fase 1 (hemat maksimal):
```
Isnin–Jumaat  : 08:00 – 22:00   (aktif)
Sabtu         : 09:00 – 18:00   (aktif)
Ahad          : OFF             (matikan — konversi B2B rendah)
```
### Bid adjustment jam (Fase 3, setelah ada data):
| Slot | Adjustment |
|---|---|
| Isnin–Jumaat 09:00–12:00 & 14:00–17:00 (jam prime B2B) | +15% |
| Malam 20:00–22:00 | +10% |
| 22:00–08:00 | −50% atau OFF |

> Zona waktu: set akun ke **(GMT+8) Kuala Lumpur**.

---

## 8. ALOKASI BUDGET FASE 1 (Rp 30.000 = RM 8,70/hari)

Semua budget ke **Campaign 1** dulu. Google izinkan set 1 budget/campaign; 2 ad group berbagi budget campaign.

| Campaign | Budget harian | Catatan |
|---|---|---|
| **Campaign 1 — Paid Ads Core (BM)** | **RM 8,70 / Rp 30.000** | Facebook Ads + Google Ads ad group |
| Semua campaign lain | **RM 0 (Paused)** | Aktif di Fase 2/3 |

> Google boleh membelanjakan **hingga 2× budget harian** di hari tertentu, tapi tak akan lebih dari **30,4 × budget harian** per bulan (≈ RM 264/bulan ≈ Rp 912.000). Aman.

Pembagian internal (via prioritas bid, bukan budget terpisah):
- Prioritaskan ad group dengan intent tertinggi. Awasi 2 minggu → pause ad group yang CPC-nya tembus RM 1,50 tanpa konversi.

---


## 9. DETAIL PER AD GROUP (keyword + match type + RSA)

**Format keyword Google Ads:**
- `"phrase match"` → tanda petik. Iklan tampil untuk pencarian yang mengandung makna frasa. **(pakai ini utama)**
- `[exact match]` → kurung siku. Hanya pencarian sama/sangat mirip. **(untuk keyword juara + kontrol CPC)**
- `broad match` → tanpa tanda. **JANGAN dipakai di Fase 1** (boros).

**Aturan RSA (Responsive Search Ad) Google:** max **15 headline (≤30 aksara)** + **4 deskripsi (≤90 aksara)**. Setiap ad group WAJIB punya keyword utama di ≥ 3 headline. Final URL = landing page layanan. Sematkan (pin) headline #1 = nama layanan agar selalu tampil.

---

### 🟢 FASE 1 · CAMPAIGN 1 — Paid Ads Core (BM)

#### ▶ AD GROUP 1.1 — Facebook Ads (BM)
**Final URL:** `https://beriklan.my/facebook-ads-management/`
**Display path:** `/facebook-ads/malaysia`

**Keyword — Phrase (copy-paste):**
```
"harga iklan facebook"
"harga iklan fb"
"harga iklan facebook ads"
"harga pasang iklan facebook"
"harga jasa iklan fb ads"
"pakej iklan facebook"
"iklan facebook malaysia"
"facebook ads malaysia"
"buat iklan facebook malaysia"
"agensi iklan facebook"
```
**Keyword — Exact (copy-paste):**
```
[facebook ads agency malaysia]
[facebook advertising agency malaysia]
[facebook ads malaysia price]
[harga iklan facebook malaysia]
[meta ads agency malaysia]
```
**Negative keyword ad group:** `percuma, free, course, kursus, tutorial, cara buat, sendiri, akaun agency, job, kerja, gaji, salary, download`

**Headlines (15):**
```
Agensi Iklan Facebook MY
Harga Iklan FB Berpatutan
Pakej Dari RM990 Sebulan
Pasukan Meta Certified
Iklan Facebook Yang Menjual
Sasaran Tepat Kos Rendah
Lapor Prestasi Mingguan
Dashboard Masa Nyata
Balas Dalam 1 Jam
Tiada Kontrak Terikat
Uruskan Kempen FB Anda
Naikkan Jualan Bisnes
Dapatkan Sebut Harga
WhatsApp Kami Sekarang
Beriklan.my Sejak 2016
```
**Descriptions (4):**
```
Pengurusan iklan Facebook oleh pasukan Meta-certified. Lapor mingguan + dashboard.
Harga berpatutan dari RM990 sebulan. Sasaran tepat, hasil boleh diukur setiap masa.
Tiada kontrak terikat. Balas dalam 1 jam waktu bekerja. Hubungi kami untuk sebut harga.
Dari audit hingga kempen live, kami uruskan semua. WhatsApp kami untuk sebut harga.
```

---

#### ▶ AD GROUP 1.2 — Google Ads (BM)
**Final URL:** `https://beriklan.my/google-ads-management/`
**Display path:** `/google-ads/malaysia`

**Keyword — Phrase:**
```
"harga iklan google"
"harga iklan google ads"
"harga pasang iklan google"
"harga iklan google maps"
"pakej google ads"
"iklan google malaysia"
"agensi google ads"
"kelola google ads"
```
**Keyword — Exact:**
```
[google ads agency malaysia]
[google ads agency in malaysia]
[ppc agency malaysia]
[google ads management pricing]
[google ads agency price]
```
**Negative keyword ad group:** `percuma, free, course, kursus, tutorial, cara, sendiri, job, jobs, gaji, salary, how to start, sijil, certification`

**Headlines (15):**
```
Agensi Google Ads Malaysia
Harga Google Ads Berpatutan
Google Ads Yang Menjual
Muncul Di Carian Google
Pakej PPC Untuk SME
Kelola Kempen Google Ads
Sasaran Kata Kunci Tepat
Lapor Prestasi Mingguan
Dashboard Masa Nyata
Balas Dalam 1 Jam
Tiada Kontrak Terikat
Pasukan Bersijil Google
Dapatkan Sebut Harga
Naikkan Lead & Jualan
WhatsApp Kami Sekarang
```
**Descriptions (4):**
```
Pengurusan Google Ads (Search, Maps, YouTube) oleh pasukan bersijil Google.
Muncul tepat bila pelanggan mencari. Harga jelas, lapor mingguan, dashboard nyata.
Tiada kontrak terikat. Balas dalam 1 jam waktu bekerja. Hubungi untuk sebut harga.
Kata kunci disasar tepat untuk kurangkan kos seklik. WhatsApp untuk sebut harga.
```

---

### 🟡 FASE 2 · CAMPAIGN 2 — Paid Ads Expand (BM/EN)

#### ▶ AD GROUP 2.1 — TikTok Ads
**Final URL:** `https://beriklan.my/tiktok-ads-management/`

**Keyword — Phrase:**
```
"harga iklan tiktok"
"harga iklan tiktok ads"
"harga iklan berbayar di tiktok"
"harga iklan tiktok shop"
"iklan tiktok malaysia"
"tiktok ads malaysia"
"pakej iklan tiktok"
"agensi tiktok ads"
```
**Keyword — Exact:**
```
[tiktok ads agency malaysia]
[tiktok marketing agency malaysia]
[tiktok advertising cost in malaysia]
```
**Negative:** `percuma, free, coin, koin, follower, beli follower, download, cara, tutorial, sound, lagu`

**Headlines (15):**
```
Agensi Iklan TikTok MY
Harga Iklan TikTok Jelas
Iklan TikTok Yang Viral
Naik FYP & Jualan Naik
Pakej TikTok Ads SME
Spark Ads & TikTok Shop
Sasaran Tepat Kos Rendah
Lapor Prestasi Mingguan
Dashboard Masa Nyata
Balas Dalam 1 Jam
Tiada Kontrak Terikat
Kelola Kempen TikTok
Dapatkan Sebut Harga
WhatsApp Kami Sekarang
Beriklan.my Sejak 2016
```
**Descriptions (4):**
```
Pengurusan iklan TikTok — Spark Ads & TikTok Shop. Sasaran tepat, hasil terukur.
Harga jelas dari RM990 sebulan. Lapor mingguan + akses dashboard masa nyata.
Tiada kontrak terikat. Balas dalam 1 jam waktu bekerja. Hubungi untuk sebut harga.
Kreatif video yang menjual, dioptimum harian. WhatsApp kami untuk sebut harga.
```

---

#### ▶ AD GROUP 2.2 — Instagram Ads
**Final URL:** `https://beriklan.my/instagram-ads-management/`

**Keyword — Phrase:**
```
"harga iklan instagram"
"harga iklan instagram ads"
"harga boost iklan instagram"
"iklan instagram malaysia"
"iklan instagram murah"
"pakej iklan instagram"
"agensi iklan instagram"
```
**Keyword — Exact:**
```
[harga iklan di instagram malaysia]
[instagram ad price malaysia]
[instagram ads price in malaysia]
[instagram ads agency malaysia]
```
**Negative:** `percuma, free, follower, beli follower, cara, tutorial, download, story viewer`

**Headlines (15):**
```
Agensi Iklan Instagram MY
Harga Iklan IG Berpatutan
Iklan Instagram Menjual
Reach & Engagement Naik
Pakej Iklan IG Untuk SME
Sasaran Tepat Kos Rendah
Kreatif IG Yang Menarik
Lapor Prestasi Mingguan
Dashboard Masa Nyata
Balas Dalam 1 Jam
Tiada Kontrak Terikat
Kelola Kempen Instagram
Dapatkan Sebut Harga
WhatsApp Kami Sekarang
Beriklan.my Sejak 2016
```
**Descriptions (4):**
```
Pengurusan iklan Instagram oleh pasukan Meta-certified. Reach & engagement terukur.
Harga berpatutan dari RM990 sebulan. Sasaran tepat, lapor mingguan + dashboard.
Tiada kontrak terikat. Balas dalam 1 jam waktu bekerja. Hubungi untuk sebut harga.
Kreatif Feed, Story & Reels yang menjual. WhatsApp kami untuk sebut harga.
```

---

#### ▶ AD GROUP 2.3 — YouTube Ads
**Final URL:** `https://beriklan.my/youtube-ads-management/`

**Keyword — Phrase:**
```
"harga iklan youtube"
"harga iklan youtube ads"
"harga pasang iklan youtube"
"iklan youtube malaysia"
"pakej iklan youtube"
"agensi iklan youtube"
```
**Keyword — Exact:**
```
[youtube ads agency]
[youtube advertising agency]
[best youtube ads agency]
```
**Negative:** `block, blocker, skip, remove, percuma, free, adsense, cara, download, premium`

**Headlines (15):**
```
Agensi Iklan YouTube MY
Harga Iklan YouTube Jelas
Video Ads Yang Diingati
Jangkau Penonton Tepat
Pakej YouTube Ads SME
Awareness & Lead Naik
Sasaran Tepat Kos Rendah
Lapor Prestasi Mingguan
Dashboard Masa Nyata
Balas Dalam 1 Jam
Tiada Kontrak Terikat
Kelola Kempen YouTube
Dapatkan Sebut Harga
WhatsApp Kami Sekarang
Beriklan.my Sejak 2016
```
**Descriptions (4):**
```
Pengurusan iklan YouTube — video ads yang jangkau audiens tepat di Malaysia.
Harga jelas dari RM990 sebulan. Lapor mingguan + akses dashboard masa nyata.
Tiada kontrak terikat. Balas dalam 1 jam waktu bekerja. Hubungi untuk sebut harga.
Dari skrip ke penerbitan kempen, kami uruskan. WhatsApp untuk sebut harga.
```

---

### 🟡 FASE 2 · CAMPAIGN 3 — Web & Landing (BM/EN)

#### ▶ AD GROUP 3.1 — Website Development
**Final URL:** `https://beriklan.my/website-development/`

**Keyword — Phrase:**
```
"harga buat website"
"harga buat website malaysia"
"web design malaysia price"
"website design malaysia price"
"web design company malaysia"
"website development company malaysia"
"web design services malaysia"
"buat website company profile"
```
**Keyword — Exact:**
```
[best web design company malaysia]
[web design company malaysia]
[website development cost in malaysia]
[harga buat website malaysia]
[sme web design company malaysia]
```
**Negative:** `percuma, free, template, wix, blogspot, sendiri, tutorial, course, kursus, job, salary, gaji, hosting sahaja`

**Headlines (15):**
```
Web Design Company Malaysia
Harga Buat Website Jelas
Website Profesional SME
Laju, Mesra Mobile & SEO
Company Profile & Toko
Reka Website Yang Menjual
Siap Ikut Jadual
Sokongan Selepas Siap
Balas Dalam 1 Jam
Harga Berpatutan
Pasukan Berpengalaman
Portfolio Boleh Dilihat
Dapatkan Sebut Harga
WhatsApp Kami Sekarang
Beriklan.my Sejak 2016
```
**Descriptions (4):**
```
Reka & bina website profesional untuk SME Malaysia. Laju, mesra mobile & SEO.
Harga jelas ikut keperluan. Company profile, e-dagang atau tempahan online.
Siap ikut jadual dengan sokongan selepas siap. Balas dalam 1 jam waktu bekerja.
Website yang direka untuk menukar pelawat jadi lead. WhatsApp untuk sebut harga.
```

---

#### ▶ AD GROUP 3.2 — Landing Page Design
**Final URL:** `https://beriklan.my/landing-page-design/`

**Keyword — Phrase:**
```
"harga buat landing page"
"harga jasa pembuatan landing page"
"landing page design malaysia"
"landing page agency malaysia"
"landing page design services"
"buat landing page murah"
```
**Keyword — Exact:**
```
[landing page agency malaysia]
[landing page design malaysia]
[landing page design cost]
```
**Negative:** `free, percuma, template, builder, wix, tutorial, course, sendiri`

**Headlines (15):**
```
Landing Page + Google Ads
Harga Landing Page Jelas
Landing Page Konversi
Direka Untuk Menukar Lead
Laju & Mesra Mobile
Pakej Landing + Iklan
Siap Dalam Beberapa Hari
A/B Test Untuk Hasil
Balas Dalam 1 Jam
Harga Berpatutan
Dapatkan Sebut Harga
Naikkan Kadar Konversi
WhatsApp Kami Sekarang
Reka Bijak Berdasar Data
Beriklan.my Sejak 2016
```
**Descriptions (4):**
```
Reka landing page yang menukar pelawat jadi lead. Laju, mesra mobile, jelas.
Pakej landing page + Google Ads. Siap dalam beberapa hari, sedia untuk kempen.
Direka berdasarkan data konversi, bukan tekaan. Balas dalam 1 jam waktu bekerja.
Harga berpatutan & jelas. WhatsApp kami untuk sebut harga & lihat contoh kerja.
```

---


### 🔴 FASE 3 · CAMPAIGN 4 — Digital Marketing Agency (EN, head term mahal)

> ⚠️ CPC head term ini **RM 3–6**. Hanya aktifkan bila budget ≥ RM 80/hari. Di sini pakai match ketat + negative agresif.

#### ▶ AD GROUP 4.1 — Digital Marketing Agency
**Final URL:** `https://beriklan.my/digital-marketing-agency/`

**Keyword — Phrase:**
```
"digital marketing agency malaysia"
"digital marketing services malaysia"
"social media marketing agency malaysia"
"performance marketing agency malaysia"
"online marketing agency malaysia"
"digital marketing company malaysia"
```
**Keyword — Exact:**
```
[best digital marketing agency malaysia]
[top digital marketing agency malaysia]
[digital marketing agency kuala lumpur]
[digital marketing agency price]
```
**Negative (agresif):** `course, kursus, class, tutorial, job, jobs, career, salary, gaji, internship, intern, free, how to start, certification, sijil, university, degree, diploma, syllabus, reddit, meaning`

**Headlines (15):**
```
Digital Marketing Agency MY
Top Agency In Malaysia
Grow Sales With Data
Meta & Google Certified
Multi-Channel Campaigns
Weekly Reports, No Jargon
Real-Time Dashboard
Reply Within 1 Hour
No Lock-In Contract
Performance Marketing MY
From Audit To Launch
Results You Can Measure
Trusted Since 2016
Get A Quote Today
WhatsApp Us Now
```
**Descriptions (4):**
```
Performance marketing agency in Malaysia. Meta & Google certified, since 2016.
Multi-channel campaigns managed end-to-end. Weekly reports and a real-time dashboard.
No lock-in contract. We reply within 1 hour during business hours. Get a quote today.
We diagnose first, then build a measurable plan. WhatsApp us for a quote today.
```

---

### 🔴 FASE 3 · CAMPAIGN 5 — Social Management (EN)

#### ▶ AD GROUP 5.1 — Instagram Management
**Final URL:** `https://beriklan.my/instagram-management/`

**Keyword — Phrase:**
```
"instagram management services"
"instagram account management services"
"instagram content management"
"social media management instagram"
```
**Keyword — Exact:**
```
[best instagram management services]
[instagram management services]
[instagram management service cost]
```
**Negative:** `tool, app, software, job, jobs, salary, free, login, intern, course, template, how to`

**Headlines (15):**
```
Instagram Management MY
IG Account Management
Content That Converts
Grow Your IG Presence
Feed, Story & Reels
Monthly Content Plan
Community Management
Reply Within 1 Hour
No Lock-In Contract
Reports Every Week
Done-For-You Content
Grow Followers & Sales
Get A Quote Today
WhatsApp Us Now
Beriklan.my Since 2016
```
**Descriptions (4):**
```
Full Instagram management — content, scheduling and community, done for you.
Consistent Feed, Story and Reels that grow your presence and drive enquiries.
No lock-in contract. Weekly reports and reply within 1 hour on business days.
A monthly content plan tailored to your brand. WhatsApp us for a quote today.
```

---

#### ▶ AD GROUP 5.2 — TikTok Management
**Final URL:** `https://beriklan.my/tiktok-management/`

**Keyword — Phrase:**
```
"tiktok account management services"
"tiktok management services"
"tiktok content creation services"
"tiktok shop management services"
```
**Keyword — Exact:**
```
[tiktok management services]
[tiktok account management agency]
```
**Negative:** `job, jobs, salary, login, intern, free, course, how to, tool, app`

**Headlines (15):**
```
TikTok Management MY
TikTok Account Manager
Content That Goes Viral
Grow Your TikTok Page
Regular Video Content
TikTok Shop Management
Monthly Content Plan
Reply Within 1 Hour
No Lock-In Contract
Reports Every Week
Done-For-You Videos
Grow Views & Sales
Get A Quote Today
WhatsApp Us Now
Beriklan.my Since 2016
```
**Descriptions (4):**
```
Full TikTok management — regular video content and page growth, done for you.
Content built to hit the FYP and turn views into enquiries and sales.
No lock-in contract. Weekly reports and reply within 1 hour on business days.
TikTok Shop management available. WhatsApp us for a quote and content plan.
```

---

### 🔴 FASE 3 · CAMPAIGN 6 — Live Viewers (EN, niche)

#### ▶ AD GROUP 6.1 — Live Stream Viewers
**Final URL:** `https://beriklan.my/live-stream-viewers/`

**Keyword — Phrase:**
```
"youtube live viewers malaysia"
"tiktok live viewers malaysia"
"shopee live viewers"
"boost youtube live stream"
"buy youtube live views"
"live stream viewers"
```
**Keyword — Exact:**
```
[youtube live viewers malaysia]
[buy youtube live viewers malaysia]
[tiktok live viewers malaysia]
```
**Negative:** `free, bot, gratis, percuma, record, world record, count, hack, apk, cara`

**Headlines (15):**
```
Live Stream Viewers MY
Boost Your Live Stream
YouTube Live Viewers
TikTok Live Viewers
Shopee Live Viewers
More Live Engagement
Real-Time Delivery
Affordable Packages
Reply Within 1 Hour
Safe & Reliable
Flexible Package Sizes
Boost Live Sales
Get A Quote Today
WhatsApp Us Now
Beriklan.my Since 2016
```
**Descriptions (4):**
```
Boost viewers on your YouTube, TikTok, Shopee, IG or Twitch live streams.
Affordable packages with real-time delivery. Reply within 1 hour on business days.
Flexible package sizes to fit any budget or campaign. WhatsApp us for pricing.
More live viewers to lift engagement and live-sales momentum. Message us today.
```

---

## 10. KONVERSI, ROAS & ENHANCED CONVERSIONS

**Status:** Tag konversi **sudah terpasang & live** di seluruh beriklan.my.
- Conversion action: **AW-18065868782 / label `2EboCKa6odkcEO6PvaZD`**
- Trigger: **setiap klik ke link WhatsApp** (statis & blog dinamis)
- Nilai: **Rp 1.000 / IDR** · Enhanced conversions: **ON** (on-page `allow_enhanced_conversions:true`)

### Yang WAJIB diset di UI Google Ads (Tools → Conversions):
1. **Category:** pilih **"Contact"** atau **"Submit lead form"**.
2. **Value:** **"Use the same value" = 1000** (karena semua klik WA bernilai sama).
3. **Count:** **"One"** (BUKAN "Every") — supaya 5 klik dari 1 orang = 1 konversi, bukan 5. Wajib untuk lead generation.
4. **Enhanced conversions:** aktifkan di UI → pilih method **"Google tag"** (sudah terpasang di web). Setuju terms EC.
5. **Attribution model:** "Data-driven" (default) atau "Last click".
6. **Conversion window:** 30 hari (default oke).

### ⚠️ Catatan ROAS (PENTING — baca):
- Nilai **Rp 1.000** hanya **simbolik** (untuk menghitung *jumlah* konversi & bandingkan relatif). **ROAS jadi tidak bermakna** kalau nilai tidak mencerminkan nilai lead sebenarnya.
- **Untuk ROAS nyata:** ganti nilai konversi jadi **nilai lead sebenar** = *nilai purata deal × kadar closing*. Contoh: paket RM 990 × closing 20% = **RM 198** nilai per lead. Ini membuat Target ROAS (Fase 3) benar-benar berfungsi.
- **Cek mata wang akun:** Billing → Settings. Jika akun berdenominasi **MYR** tapi konversi dikirim **IDR**, Google konversi otomatis (Rp1.000 ≈ RM0,06 → terlalu kecil). **Selaraskan:** ubah nilai/mata wang konversi agar sama dengan mata wang akun. (Saya boleh ubah nilai/currency di kod bila Anda tetapkan angka nyata.)

---

## 11. MASTER NEGATIVE KEYWORD LIST (account-level, copy-paste)

Buat **"Negative keyword list"** di Tools → Shared library → Negative keyword lists → beri nama `Master Negatives MY`, lalu paste semua ini. Terapkan ke SEMUA campaign.
```
free
percuma
gratis
course
courses
kursus
class
kelas
tutorial
cara
cara buat
how to
diy
sendiri
job
jobs
kerja
career
vacancy
salary
gaji
internship
intern
practicum
template
templates
download
apk
mod
crack
bot
hack
adalah
meaning
definition
wikipedia
example
contoh
sijil
certification
study
university
diploma
syllabus
login
```
> Catatan: `harga`, `cost`, `price`, `pricing`, `packages`, `agency`, `services` **JANGAN** dijadikan negative — itu justru keyword komersial kita.

---

## 12. VERIFIKASI VOLUME + CPC DI KEYWORD PLANNER (seed list)

Login Google Ads → **Tools → Planning → Keyword Planner → "Get search volume and forecasts"** → paste list di bawah → set lokasi **Malaysia**, bahasa **English + Malay**. Ini beri Anda **volume nyata + CPC low/high range** untuk finalisasi bid.
```
harga iklan facebook
facebook ads agency malaysia
harga iklan google
google ads agency malaysia
harga iklan tiktok
tiktok ads agency malaysia
harga iklan instagram malaysia
instagram ads agency malaysia
harga iklan youtube
youtube ads agency
harga buat website malaysia
web design company malaysia
harga buat landing page
landing page agency malaysia
digital marketing agency malaysia
best digital marketing agency malaysia
social media marketing agency malaysia
instagram management services
tiktok management services
youtube live viewers malaysia
```
Hasil Keyword Planner → simpan sebagai bukti volume; buang keyword volume 0; naikkan bid untuk keyword volume tinggi + CPC rendah.

---

## 13. RITME OPTIMASI (checklist)

**Harian (5 menit) — Fase 1:**
- Cek spend tak lari (max ≈ RM 8,70). Cek ada klik masuk.
- Search terms report → tambah negative untuk query tak relevan (WAJIB tiap hari di awal — ini paling banyak buang budget).

**Mingguan:**
- Pause keyword: CTR < 2% ATAU CPC > RM 1,50 tanpa konversi (30+ impresi).
- Naikkan bid keyword yang ada konversi.
- Cek Quality Score (target ≥ 7). QS rendah → perbaiki relevansi iklan/landing.
- Rotasi headline berprestasi rendah.

**Bulanan:**
- Review CPA per ad group → matikan yang termahal.
- Evaluasi naik ke Fase berikut (syarat: CTR > 4%, ≥ 15 konversi, CPA terukur).
- Tambah keyword baru dari Search terms report yang konversi.

---

## 14. QUICK SETUP — LANGKAH DI GOOGLE ADS (Fase 1)

1. **+ New Campaign** → Objective: **Leads** → Type: **Search**.
2. Uncheck **Search partners** & **Display network**.
3. Locations: **KL, Petaling Jaya, Shah Alam, Subang Jaya, Klang** → set **"Presence"**.
4. Languages: **Malay + English**.
5. Bidding: **Maximize clicks** → set **Max CPC limit RM 1,50**.
6. Budget: **RM 8,70/hari** (= Rp 30.000). Timezone **GMT+8 KL**.
7. Ad schedule: Isnin–Sabtu (lihat §7), Ahad OFF.
8. Buat **2 ad group** (Facebook Ads, Google Ads) → paste keyword + RSA dari §9.
9. Pasang **Master Negatives MY** (§11).
10. Pastikan **Conversion "WhatsApp click"** aktif & Enhanced conversions ON (§10).
11. Set **Ad rotation: Optimize**. Aktifkan **auto-apply recommendations: OFF** (kontrol manual di budget kecil).
12. **Publish** → pantau harian (§13).

---

## 15. CATATAN KEPATUHAN COPY (Google Ads policy)

- Semua headline ≤ 30 aksara, deskripsi ≤ 90 aksara (sudah dipatuhi).
- **Tiada klaim "konsultasi percuma"** — diganti "Sebut Harga / Get A Quote" agar selaras keputusan brand (klaim konsultasi gratis telah dibuang dari laman).
- Tiada superlatif tidak terbukti ("no.1", "terbaik #1"), tiada "GARANTI 100%", tiada HURUF BESAR berlebihan, tiada "!" bertindih.
- Nombor harga (RM990) hanya di headline/desc sebagai titik mula ("dari RM990") — konsisten dengan `services.json`.

---

*Disusun untuk beriklan.my · Data: keyword mining MY (suggest_my) + benchmark CPC Malaysia 2026. Verifikasi volume final di Keyword Planner sebelum go-live.*
