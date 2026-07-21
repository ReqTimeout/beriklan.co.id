export const report = {
  year: 2026,
  title: 'Laporan Industri Iklan Digital Indonesia 2026',
  url: '/riset/laporan-industri-iklan-digital-indonesia-2026/',
  lastUpdated: '21 Jul 2026',

  hero: {
    headline: 'USD 3,41 Miliar: Belanja Iklan Digital Indonesia 2026',
    subhead:
      'Pertumbuhan 5,70% CAGR didorong oleh penetrasi smartphone, social commerce, dan konsumsi video yang terus meningkat.',
  },

  executiveSummary: [
    { label: 'Belanja Iklan Digital 2026', value: 'USD 3,41 M', suffix: '', source: 'Mordor Intelligence' },
    { label: 'Pengguna Internet', value: '230', suffix: 'Juta', source: 'We Are Social 2026' },
    { label: 'Pengguna Medsos', value: '180', suffix: 'Juta', source: 'We Are Social 2026' },
    { label: 'Waktu di Medsos/Hari', value: '3,1', suffix: 'Jam', source: 'We Are Social 2026' },
  ],

  marketSize: {
    current: { year: 2026, value: 3.41, unit: 'USD Miliar' },
    forecast: { year: 2031, value: 4.51, unit: 'USD Miliar' },
    cagr: 5.7,
    source: 'Mordor Intelligence — Indonesia Digital Advertising Market Report 2026',
    data: [
      { year: 2020, value: 2.1 },
      { year: 2021, value: 2.35 },
      { year: 2022, value: 2.6 },
      { year: 2023, value: 2.85 },
      { year: 2024, value: 3.05 },
      { year: 2025, value: 3.23 },
      { year: 2026, value: 3.41 },
      { year: 2031, value: 4.51 },
    ],
  },

  formatShare: [
    { label: 'Video', percentage: 34.02, color: 'var(--color-accent)' },
    { label: 'Display/Banner', percentage: 28.5, color: 'var(--color-teal)' },
    { label: 'Search', percentage: 22.3, color: 'var(--color-primary-2)' },
    { label: 'Social Media (non-video)', percentage: 15.18, color: 'var(--color-green)' },
  ],

  deviceShare: [
    { label: 'Mobile', percentage: 68.1, color: 'var(--color-accent)' },
    { label: 'Desktop/Laptop', percentage: 25.4, color: 'var(--color-primary-2)' },
    { label: 'Connected TV', percentage: 6.5, color: 'var(--color-teal)' },
  ],

  platformUsers: [
    { name: 'WhatsApp', users: 187.4, color: '#25D366' },
    { name: 'Instagram', users: 160.2, color: '#E4405F' },
    { name: 'TikTok', users: 137.8, color: '#000000' },
    { name: 'Facebook', users: 132.5, color: '#1877F2' },
    { name: 'YouTube', users: 128.7, color: '#FF0000' },
  ],

  dailyEngagement: [
    { platform: 'TikTok', dailyMinutes: 113, color: '#000000' },
    { platform: 'WhatsApp', dailyMinutes: 112, color: '#25D366' },
    { platform: 'Instagram', dailyMinutes: 48, color: '#E4405F' },
    { platform: 'Facebook', dailyMinutes: 35, color: '#1877F2' },
    { platform: 'YouTube', dailyMinutes: 30, color: '#FF0000' },
  ],

  brandDiscovery: [
    { channel: 'Search Engine', percentage: 38.3 },
    { channel: 'Social Media Ads', percentage: 37.3 },
    { channel: 'Social Comments/UGC', percentage: 32.6 },
    { channel: 'TV/Offline', percentage: 24.1 },
    { channel: 'Word of Mouth', percentage: 21.8 },
  ],

  digitalGrowth: {
    dentsuGrowth: 5.1,
    digitalGrowth: '10-12%',
    oohGrowth: '7.0%',
    tvGrowth: '3-5%',
    source: 'Dentsu Digital Advertising Market Report 2025',
    budgetShift: 7,
  },

  socialCommerce: {
    value: 14.8,
    unit: 'USD Miliar',
    share: 27,
    growth: 34,
    source: 'Hashmeta / e-Conomy SEA 2025',
  },

  trends: [
    {
      title: 'Video First',
      desc: 'Video menyumbang 34,02% belanja iklan digital dan 78% total konsumsi media sosial.',
      source: 'Mordor Intelligence / Hashmeta 2025',
    },
    {
      title: 'AI dalam Periklanan',
      desc: 'Adopsi AI untuk creative localization dan dynamic creative optimization semakin masif. 37% Gen Z menggunakan ChatGPT pada Q2 2025.',
      source: 'We Are Social 2026 / DataReportal',
    },
    {
      title: 'Social Commerce',
      desc: 'Social commerce mencapai USD 14,8 Miliar — 27% total e-commerce Indonesia, tumbuh 34% per tahun.',
      source: 'Hashmeta / e-Conomy SEA 2025',
    },
    {
      title: 'Perlindungan Data',
      desc: 'UU PDP Indonesia memberlakukan denda berbasis revenue, mendorong platform memperkuat consent flow dan strategi first-party data.',
      source: 'Mordor Intelligence 2026',
    },
    {
      title: 'Connected TV',
      desc: 'OTT viewers mencapai 83 juta pengguna dengan 3,5 miliar jam streaming bulanan. CTV advertising tumbuh 6,72% CAGR.',
      source: 'Mordor Intelligence 2026',
    },
  ],

  challenges: [
    {
      title: 'Ad Fraud & Brand Safety',
      desc: 'Kekhawatiran terhadap ad fraud dan brand safety mendorong adopsi contextual verification tools.',
    },
    {
      title: 'Fragmentasi Platform',
      desc: 'Pengguna tersebar di rata-rata 7,7 platform per bulan — menyulitkan alokasi budget yang efisien.',
    },
    {
      title: 'Kepatuhan Regulasi',
      desc: 'UU PDP dan kebijakan platform yang berubah cepat membutuhkan adaptasi strategi data yang kontinu.',
    },
    {
      title: 'Kesenjangan Talenta',
      desc: 'Permintaan akan performance marketer yang kompeten jauh melampaui pasokan talenta berkualitas.',
    },
  ],

  methodology: {
    sources: [
      {
        name: 'Mordor Intelligence',
        url: 'https://www.mordorintelligence.com/industry-reports/indonesia-digital-advertising-market',
        desc: 'Indonesia Digital Advertising Market Report 2026-2031',
      },
      {
        name: 'We Are Social & Meltwater',
        url: 'https://wearesocial.com/id/blog/2025/11/digital-2026-top-digital-and-social-media-trends-in-indonesia/',
        desc: 'Digital 2026: Indonesia Report',
      },
      {
        name: 'DataReportal',
        url: 'https://datareportal.com/reports/digital-2026-indonesia',
        desc: 'Digital 2026: Indonesia — Global Digital Insights',
      },
      {
        name: 'Dentsu Indonesia',
        url: 'https://www.dentsu.com/id/en/insights/our-blog/dentsu-digital-advertising-market-report-2025',
        desc: 'Digital Advertising Market Report 2025',
      },
      {
        name: 'Hashmeta',
        url: 'https://hashmeta.com/blog/social-media-landscape-indonesia-key-stats-platforms-you-need-to-know/',
        desc: 'Social Media Landscape Indonesia 2025',
      },
      {
        name: 'APJII',
        desc: 'Survei Penetrasi Internet Indonesia 2025',
      },
    ],
    notes:
      'Data merupakan kompilasi dari laporan industri yang tersedia untuk publik. Beberapa angka merupakan proyeksi atau estimasi dari masing-masing sumber. Beriklan Digital Agency tidak mengklaim data ini sebagai riset primer, melainkan sebagai kurasi dan sintesis untuk kemudahan referensi industri.',
  },

  faqs: [
    {
      q: 'Berapa besar belanja iklan digital Indonesia tahun 2026?',
      a: 'Belanja iklan digital Indonesia diperkirakan mencapai USD 3,41 miliar pada 2026, dengan proyeksi mencapai USD 4,51 miliar pada 2031 (CAGR 5,70%).',
    },
    {
      q: 'Platform iklan digital apa yang paling populer di Indonesia?',
      a: 'Berdasarkan jumlah pengguna aktif bulanan: WhatsApp (187,4 juta), Instagram (160,2 juta), TikTok (137,8 juta), Facebook (132,5 juta), dan YouTube (128,7 juta).',
    },
    {
      q: 'Berapa lama orang Indonesia menghabiskan waktu di media sosial?',
      a: 'Rata-rata 3 jam 7 menit per hari, tersebar di 7,7 platform setiap bulan. TikTok memimpin dengan 1 jam 53 menit per hari.',
    },
    {
      q: 'Bagaimana peran media sosial dalam brand discovery di Indonesia?',
      a: '37,3% konsumen menemukan merek baru melalui iklan media sosial, hampir menyamai search engine (38,3%). Tiga dari lima pengguna menjadikan media sosial sebagai kanal utama riset merek.',
    },
    {
      q: 'Apa tren utama industri iklan digital Indonesia 2026?',
      a: 'Lima tren utama: (1) Video-first — 78% konsumsi media sosial, (2) AI dalam iklan — creative localization & DCO, (3) Social commerce — USD 14,8 Miliar, (4) Regulasi data — UU PDP, (5) Connected TV — 83 juta viewers OTT.',
    },
  ],
}
