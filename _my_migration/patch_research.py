#!/usr/bin/env python3
"""F1-7d: Malaysia research report — new research-data.js, new page, footer link, remove old page."""
import io, os

DATA = "/Users/maabook/Desktop/beriklan.my/web/src/data/"
PAGES = "/Users/maabook/Desktop/beriklan.my/web/src/pages/"
COMP = "/Users/maabook/Desktop/beriklan.my/web/src/components/"

RD = '''export const report = {
  year: 2026,
  title: 'Malaysia Digital Advertising Report 2026',
  url: '/research/malaysia-digital-advertising-report-2026/',
  lastUpdated: '21 Jul 2026',

  hero: {
    headline: 'USD 1.41 Billion: Malaysia Digital Ad Spend 2026',
    subhead:
      'Steady growth driven by near-universal internet penetration, social commerce and ever-rising video consumption.',
  },

  executiveSummary: [
    { label: 'Digital Ad Spend 2026', value: 1410, suffix: 'M', unit: 'USD', source: 'Statista Advertising Outlook' },
    { label: 'Internet Users', value: 34, suffix: 'M', unit: '', source: 'DataReportal 2025' },
    { label: 'Social Media Users', value: 29, suffix: 'M', unit: '', source: 'We Are Social 2025' },
    { label: 'Daily Time on Social', value: 168, suffix: ' Min', unit: '', source: 'We Are Social 2025' },
  ],

  marketSize: {
    current: { year: 2026, value: 1.41, unit: 'USD Billion' },
    forecast: { year: 2030, value: 1.83, unit: 'USD Billion' },
    cagr: 6.7,
    source: 'Statista Digital Advertising Outlook — Malaysia (estimates)',
    data: [
      { year: 2020, value: 0.75 },
      { year: 2021, value: 0.85 },
      { year: 2022, value: 0.95 },
      { year: 2023, value: 1.08 },
      { year: 2024, value: 1.2 },
      { year: 2025, value: 1.31 },
      { year: 2026, value: 1.41 },
      { year: 2030, value: 1.83 },
    ],
  },

  formatShare: [
    { label: 'Video', percentage: 32.5, color: 'var(--color-accent)' },
    { label: 'Search', percentage: 27.8, color: 'var(--color-primary-2)' },
    { label: 'Display/Banner', percentage: 24.5, color: 'var(--color-teal)' },
    { label: 'Social Media (non-video)', percentage: 15.2, color: 'var(--color-green)' },
  ],

  deviceShare: [
    { label: 'Mobile', percentage: 71.2, color: 'var(--color-accent)' },
    { label: 'Desktop/Laptop', percentage: 23.3, color: 'var(--color-primary-2)' },
    { label: 'Connected TV', percentage: 5.5, color: 'var(--color-teal)' },
  ],

  platformUsers: [
    { name: 'WhatsApp', users: 29.4, color: '#25D366' },
    { name: 'TikTok', users: 24.8, color: '#000000' },
    { name: 'YouTube', users: 24.1, color: '#FF0000' },
    { name: 'Facebook', users: 22.4, color: '#1877F2' },
    { name: 'Instagram', users: 15.4, color: '#E4405F' },
  ],

  dailyEngagement: [
    { platform: 'TikTok', dailyMinutes: 95, color: '#000000' },
    { platform: 'WhatsApp', dailyMinutes: 90, color: '#25D366' },
    { platform: 'Instagram', dailyMinutes: 45, color: '#E4405F' },
    { platform: 'Facebook', dailyMinutes: 40, color: '#1877F2' },
    { platform: 'YouTube', dailyMinutes: 35, color: '#FF0000' },
  ],

  brandDiscovery: [
    { channel: 'Search Engine', percentage: 36.8 },
    { channel: 'Social Media Ads', percentage: 34.2 },
    { channel: 'Social Comments/UGC', percentage: 29.5 },
    { channel: 'TV/Offline', percentage: 25.3 },
    { channel: 'Word of Mouth', percentage: 23.1 },
  ],

  digitalGrowth: {
    dentsuGrowth: 4.8,
    digitalGrowth: '9-11%',
    oohGrowth: '6.0%',
    tvGrowth: '2-4%',
    source: 'GroupM This Year Next Year 2025 (estimates)',
    budgetShift: 6,
  },

  socialCommerce: {
    value: 3.5,
    unit: 'USD Billion',
    share: 22,
    growth: 24,
    source: 'e-Conomy SEA 2025 (estimates)',
  },

  trends: [
    {
      title: 'Video First',
      desc: 'Video accounts for roughly a third of digital ad spend and the majority of social media consumption in Malaysia.',
      source: 'Statista / We Are Social 2025',
    },
    {
      title: 'AI in Advertising',
      desc: 'AI adoption for creative localisation and dynamic creative optimisation is accelerating fast across Malaysian advertisers.',
      source: 'We Are Social 2025 / DataReportal',
    },
    {
      title: 'Social Commerce',
      desc: 'Social commerce is estimated around USD 3.5 billion — roughly 22% of Malaysian e-commerce, growing about 24% per year. TikTok Shop leads the charge.',
      source: 'e-Conomy SEA 2025 (estimates)',
    },
    {
      title: 'Data Protection',
      desc: "Malaysia's PDPA amendments (in force 2025) introduce stricter obligations, pushing platforms to strengthen consent flows and first-party data strategies.",
      source: 'PDPA Amendment Act 2024',
    },
    {
      title: 'Connected TV',
      desc: 'OTT streaming keeps expanding across Malaysian households, opening up fast-growing CTV advertising inventory.',
      source: 'Statista 2025 (estimates)',
    },
  ],

  challenges: [
    {
      title: 'Ad Fraud & Brand Safety',
      desc: 'Concerns over ad fraud and brand safety are driving adoption of contextual verification tools.',
    },
    {
      title: 'Platform Fragmentation',
      desc: 'Users spread their time across many platforms every month — making efficient budget allocation harder.',
    },
    {
      title: 'Regulatory Compliance',
      desc: 'The amended PDPA and fast-changing platform policies demand continuous adaptation of data strategy.',
    },
    {
      title: 'Talent Gap',
      desc: 'Demand for competent performance marketers far outstrips the supply of qualified talent.',
    },
  ],

  methodology: {
    sources: [
      {
        name: 'Statista',
        url: 'https://www.statista.com/outlook/dmo/digital-advertising/malaysia',
        desc: 'Digital Advertising Outlook — Malaysia',
      },
      {
        name: 'We Are Social & Meltwater',
        url: 'https://wearesocial.com/',
        desc: 'Digital 2025: Malaysia Report',
      },
      {
        name: 'DataReportal',
        url: 'https://datareportal.com/reports/digital-2025-malaysia',
        desc: 'Digital 2025: Malaysia — Global Digital Insights',
      },
      {
        name: 'GroupM',
        url: 'https://www.groupm.com/',
        desc: 'This Year Next Year — Global Mid-Year Forecast',
      },
      {
        name: 'Google, Temasek & Bain',
        url: 'https://economysea.withgoogle.com/',
        desc: 'e-Conomy SEA Report',
      },
      {
        name: 'MCMC',
        desc: 'Malaysian Communications and Multimedia Commission — Internet Users Survey',
      },
    ],
    notes:
      'This data is a compilation of publicly available industry reports. Several figures are projections or estimates from the respective sources. Beriklan Digital Agency does not claim this data as primary research — it is curated and synthesised for convenient industry reference.',
  },

  faqs: [
    {
      q: 'How big is Malaysia digital ad spend in 2026?',
      a: "Malaysia's digital advertising spend is estimated at around USD 1.41 billion in 2026, projected to reach roughly USD 1.83 billion by 2030 (about 6.7% CAGR).",
    },
    {
      q: 'Which digital ad platforms are most popular in Malaysia?',
      a: 'By estimated monthly active users: WhatsApp (~29.4 million), TikTok (~24.8 million), YouTube (~24.1 million), Facebook (~22.4 million) and Instagram (~15.4 million).',
    },
    {
      q: 'How much time do Malaysians spend on social media?',
      a: 'On average around 2 hours 48 minutes per day, spread across multiple platforms. TikTok leads daily engagement time.',
    },
    {
      q: 'What role does social media play in brand discovery in Malaysia?',
      a: 'Roughly a third of consumers discover new brands through social media ads — nearly matching search engines. Social media is now a primary brand-research channel for Malaysian users.',
    },
    {
      q: 'What are the key digital advertising trends in Malaysia for 2026?',
      a: 'Five main trends: (1) Video-first content, (2) AI in advertising — creative localisation & DCO, (3) Social commerce led by TikTok Shop, (4) Data protection — the amended PDPA, (5) Connected TV growth.',
    },
  ],
}
'''

with io.open(DATA + 'research-data.js', 'w', encoding='utf-8') as f:
    f.write(RD)
print('WROTE research-data.js')

# Footer link update
fp = COMP + 'Footer.svelte'
s = io.open(fp, encoding='utf-8').read()
s2 = s.replace('/research/laporan-industri-iklan-digital-indonesia-2026', '/research/malaysia-digital-advertising-report-2026')
io.open(fp, 'w', encoding='utf-8').write(s2)
print('Footer.svelte research link updated: %s' % (s != s2))

# Remove old research page
old = PAGES + 'research/laporan-industri-iklan-digital-indonesia-2026.astro'
if os.path.exists(old):
    os.remove(old)
    print('REMOVED old research page')

PAGE = '''---
import Layout from '../../layouts/Layout.astro'
import Footer from '../../components/Footer.svelte'
import Navbar from '../../components/Navbar.svelte'
import AnimatedStat from '../../components/AnimatedStat.svelte'
import { report } from '../../data/research-data.js'

const d = report
const breadcrumb = [
  { name: 'Home', url: '/' },
  { name: 'Research', url: '/research/' },
  { name: d.title, url: d.url },
]
---

<Layout
  title="Malaysia Digital Advertising Report 2026 — Latest Data & Trends | Beriklan"
  description="Comprehensive report on Malaysia's digital advertising industry 2026: USD 1.41 billion ad spend, platform landscape, video & AI trends, social commerce, and projections to 2030. Sources: Statista, We Are Social, DataReportal, GroupM."
  canonical={d.url}
  schema="auto"
  {breadcrumb}
  faq={d.faqs.map(f => ({ question: f.q, answer: f.a }))}
>
  <Navbar client:only="svelte" />
  <main class="bg-white">
    <!-- HERO -->
    <section class="bg-gradient-to-br from-primary via-primary-2 to-ink text-white overflow-hidden relative">
      <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(245,158,11,0.12),transparent_70%)]" />
      <div class="container mx-auto px-6 py-20 md:py-28 relative z-10">
        <span class="hero-eyebrow inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm text-white rounded-full px-4 py-1.5 text-[10px] md:text-xs font-bold uppercase tracking-[0.2em]">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
          </span>
          Research · Malaysia Ad Industry · {d.year}
        </span>
        <h1 class="text-4xl md:text-5xl lg:text-[2.75rem] xl:text-6xl font-display font-extrabold mt-6 leading-tight max-w-4xl">
          {d.title}
        </h1>
        <p class="text-lg md:text-xl text-white/80 mt-4 max-w-3xl leading-relaxed">
          {d.hero.subhead}
        </p>
        <div class="flex flex-wrap gap-3 mt-8">
          <a
            href="https://wa.me/62811919328?text=Hi%20Beriklan%2C%20I%27m%20interested%20in%20the%20Malaysia%20Digital%20Advertising%20Report%202026."
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-2 bg-accent hover:bg-amber-600 text-primary font-bold text-sm rounded-full px-7 py-3.5 transition-all btn-shine"
          >
            Chat on WhatsApp
          </a>
        </div>
        <p class="text-xs text-white/50 mt-4">Last updated: {d.lastUpdated}</p>
      </div>
    </section>

    <!-- EXECUTIVE SUMMARY -->
    <section class="py-16 md:py-20 bg-soft">
      <div class="container mx-auto px-6">
        <p class="eyebrow text-center">Executive Summary</p>
        <h2 class="text-3xl md:text-5xl font-display font-extrabold text-center mt-2">Key Numbers</h2>
        <p class="text-center text-muted mt-3 max-w-2xl mx-auto">
          Headline data on Malaysia's digital advertising industry in 2026, from trusted public sources.
        </p>
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8 mt-10">
          {d.executiveSummary.map(stat => (
            <AnimatedStat
              client:only="svelte"
              value={stat.value}
              suffix={stat.suffix}
              label={stat.label}
              source={stat.source}
            />
          ))}
        </div>
        <div class="flex justify-center gap-6 mt-8 text-xs text-muted flex-wrap">
          <span>📊 Sources: Statista, We Are Social, DataReportal, GroupM, MCMC</span>
        </div>
      </div>
    </section>

    <!-- TABLE OF CONTENTS -->
    <section class="py-12 md:py-16 bg-white border-b border-gray-100">
      <div class="container mx-auto px-6">
        <p class="eyebrow">Contents</p>
        <h2 class="text-3xl md:text-5xl font-display font-extrabold mt-2">Report Navigation</h2>
        <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 mt-8 max-w-3xl">
          {[
            { href: '#market-overview', label: '1. Market Overview' },
            { href: '#platform-landscape', label: '2. Platform Landscape' },
            { href: '#digital-behavior', label: '3. Digital Behaviour' },
            { href: '#trends', label: '4. Industry Trends 2026' },
            { href: '#challenges', label: '5. Challenges & Opportunities' },
            { href: '#methodology', label: '6. Methodology & Sources' },
          ].map(item => (
            <a
              href={item.href}
              class="block p-4 rounded-xl border border-gray-200 hover:border-accent hover:shadow-soft transition-all text-sm font-medium text-primary"
            >
              {item.label}
            </a>
          ))}
        </div>
      </div>
    </section>

    <!-- SECTION 1: MARKET OVERVIEW -->
    <section id="market-overview" class="py-16 md:py-24 bg-white">
      <div class="container mx-auto px-6">
        <p class="eyebrow">Market Overview</p>
        <h2 class="text-3xl md:text-5xl font-display font-extrabold mt-2">Malaysia's Digital Ad Market</h2>
        <p class="text-muted mt-3 max-w-3xl leading-relaxed">
          Malaysia's digital advertising market is estimated to reach <strong>USD 1.41 billion in 2026</strong>
          and is projected to grow to around <strong>USD 1.83 billion by 2030</strong> at roughly 6.7% CAGR.
          Growth is driven by near-universal internet penetration, social commerce integration and ever-rising video consumption.
        </p>

        <!-- Market size bar chart -->
        <div class="mt-10 bg-soft rounded-2xl p-6 md:p-8">
          <h3 class="text-lg font-display font-bold">Market Size Growth (USD Billion)</h3>
          <div class="mt-6 space-y-3">
            {d.marketSize.data.filter(row => row.year !== 2030).map(row => {
              const pct = (row.value / 1.41) * 100
              return (
                <div class="flex items-center gap-4">
                  <span class="text-sm text-muted w-12 shrink-0">{row.year}</span>
                  <div class="flex-1 h-7 bg-white rounded-full overflow-hidden">
                    <div
                      class="h-full rounded-full bg-gradient-to-r from-accent to-accent-2 transition-all duration-700"
                      style={`width: ${Math.min(pct, 100)}%`}
                    ></div>
                  </div>
                  <span class="text-sm font-bold text-primary tabular-nums w-20 text-right">USD {row.value} B</span>
                </div>
              )
            })}
            <div class="flex items-center gap-4 opacity-70">
              <span class="text-sm text-muted w-12 shrink-0">2030*</span>
              <div class="flex-1 h-7 bg-white rounded-full overflow-hidden">
                <div class="h-full rounded-full bg-gradient-to-r from-teal to-blue-500" style="width: 100%"></div>
              </div>
              <span class="text-sm font-bold text-primary tabular-nums w-20 text-right">USD 1.83 B*</span>
            </div>
          </div>
          <p class="text-xs text-muted/60 mt-4 italic">*Projection. Source: {d.marketSize.source}</p>
        </div>

        <!-- Format composition -->
        <div class="grid md:grid-cols-2 gap-6 mt-10">
          <div class="bg-soft rounded-2xl p-6 md:p-8">
            <h3 class="text-lg font-display font-bold">By Ad Format</h3>
            <div class="mt-5 space-y-4">
              {d.formatShare.map(f => (
                <div>
                  <div class="flex justify-between text-sm mb-1">
                    <span class="font-medium">{f.label}</span>
                    <span class="text-muted">{f.percentage}%</span>
                  </div>
                  <div class="h-3 bg-white rounded-full overflow-hidden">
                    <div class="h-full rounded-full transition-all duration-700" style={`width: ${f.percentage}%; background: ${f.color}`}></div>
                  </div>
                </div>
              ))}
            </div>
            <p class="text-xs text-muted/60 mt-4 italic">Source: Statista 2025 (estimates)</p>
          </div>
          <div class="bg-soft rounded-2xl p-6 md:p-8">
            <h3 class="text-lg font-display font-bold">By Device</h3>
            <div class="mt-5 space-y-4">
              {d.deviceShare.map(f => (
                <div>
                  <div class="flex justify-between text-sm mb-1">
                    <span class="font-medium">{f.label}</span>
                    <span class="text-muted">{f.percentage}%</span>
                  </div>
                  <div class="h-3 bg-white rounded-full overflow-hidden">
                    <div class="h-full rounded-full transition-all duration-700" style={`width: ${f.percentage}%; background: ${f.color}`}></div>
                  </div>
                </div>
              ))}
            </div>
            <p class="text-xs text-muted/60 mt-4 italic">Source: Statista 2025 (estimates)</p>
          </div>
        </div>

        <div class="grid sm:grid-cols-3 gap-4 mt-8">
          <div class="bg-gradient-to-br from-amber-50 to-amber-100/50 rounded-2xl p-5 text-center">
            <span class="text-3xl font-display font-extrabold text-accent tabular-nums">6.7%</span>
            <p class="text-sm text-muted mt-1">CAGR 2026-2030</p>
          </div>
          <div class="bg-gradient-to-br from-teal-50 to-teal-100/50 rounded-2xl p-5 text-center">
            <span class="text-3xl font-display font-extrabold text-teal tabular-nums">71.2%</span>
            <p class="text-sm text-muted mt-1">Spend from Mobile</p>
          </div>
          <div class="bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-2xl p-5 text-center">
            <span class="text-3xl font-display font-extrabold text-blue-600 tabular-nums">+6pp</span>
            <p class="text-sm text-muted mt-1">Shift to Digital (2023-2025)</p>
          </div>
        </div>
      </div>
    </section>

    <!-- SECTION 2: PLATFORM LANDSCAPE -->
    <section id="platform-landscape" class="py-16 md:py-24 bg-soft">
      <div class="container mx-auto px-6">
        <p class="eyebrow">Platform Landscape</p>
        <h2 class="text-3xl md:text-5xl font-display font-extrabold mt-2">The Digital Platform Landscape</h2>
        <p class="text-muted mt-3 max-w-3xl leading-relaxed">
          Malaysia has a highly fragmented social media ecosystem — users are active across
          <strong>multiple platforms every month</strong>. Below is a comparison of platforms by
          user numbers and daily engagement time.
        </p>

        <!-- Platform bar chart -->
        <div class="grid md:grid-cols-2 gap-6 mt-10">
          <div class="bg-white rounded-2xl p-6 md:p-8 shadow-soft">
            <h3 class="text-lg font-display font-bold mb-5">Monthly Active Users (Million)</h3>
            <div class="space-y-4">
              {d.platformUsers.map(p => (
                <div>
                  <div class="flex justify-between text-sm mb-1">
                    <span class="font-medium">{p.name}</span>
                    <span class="text-muted">{p.users} Million</span>
                  </div>
                  <div class="h-4 bg-soft rounded-full overflow-hidden">
                    <div
                      class="h-full rounded-full transition-all duration-700"
                      style={`width: ${(p.users / 29.4) * 100}%; background: ${p.color}`}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
            <p class="text-xs text-muted/60 mt-4 italic">Source: DataReportal, We Are Social 2025 (estimates)</p>
          </div>
          <div class="bg-white rounded-2xl p-6 md:p-8 shadow-soft">
            <h3 class="text-lg font-display font-bold mb-5">Daily Time per User (Minutes)</h3>
            <div class="space-y-4">
              {d.dailyEngagement.map(p => (
                <div>
                  <div class="flex justify-between text-sm mb-1">
                    <span class="font-medium">{p.platform}</span>
                    <span class="text-muted">{p.dailyMinutes} min/day</span>
                  </div>
                  <div class="h-4 bg-soft rounded-full overflow-hidden">
                    <div
                      class="h-full rounded-full transition-all duration-700"
                      style={`width: ${(p.dailyMinutes / 95) * 100}%; background: ${p.color}`}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
            <p class="text-xs text-muted/60 mt-4 italic">Source: We Are Social Digital 2025 (estimates)</p>
          </div>
        </div>

        <div class="bg-white rounded-2xl p-6 md:p-8 shadow-soft mt-6">
          <h3 class="text-lg font-display font-bold mb-3">Brand Discovery Channels</h3>
          <p class="text-sm text-muted mb-5">Percentage of consumers who discover brands through each channel</p>
          <div class="space-y-4">
            {d.brandDiscovery.map(b => {
              const maxDisc = Math.max(...d.brandDiscovery.map(b => b.percentage))
              return (
                <div>
                  <div class="flex justify-between text-sm mb-1">
                    <span class="font-medium">{b.channel}</span>
                    <span class="text-muted">{b.percentage}%</span>
                  </div>
                  <div class="h-3 bg-soft rounded-full overflow-hidden">
                    <div
                      class="h-full rounded-full bg-gradient-to-r from-accent to-accent-2 transition-all duration-700"
                      style={`width: ${(b.percentage / maxDisc) * 100}%`}
                    ></div>
                  </div>
                </div>
              )
            })}
          </div>
          <p class="text-xs text-muted/60 mt-4 italic">Source: We Are Social Digital 2025 (estimates)</p>
        </div>
      </div>
    </section>

    <!-- SECTION 3: DIGITAL BEHAVIOUR -->
    <section id="digital-behavior" class="py-16 md:py-24 bg-white">
      <div class="container mx-auto px-6">
        <p class="eyebrow">Digital Behaviour</p>
        <h2 class="text-3xl md:text-5xl font-display font-extrabold mt-2">How Malaysians Behave Online</h2>

        <div class="grid md:grid-cols-3 gap-6 mt-10">
          <div class="bg-soft rounded-2xl p-6 md:p-8">
            <div class="text-4xl font-display font-extrabold text-accent tabular-nums">2.8</div>
            <p class="text-sm text-muted mt-1">Hours/day on social media</p>
            <hr class="my-4 border-gray-200" />
            <p class="text-sm text-muted leading-relaxed">
              Spread across <strong>multiple platforms</strong> every month — nearly 20 hours per week.
            </p>
          </div>
          <div class="bg-soft rounded-2xl p-6 md:p-8">
            <div class="text-4xl font-display font-extrabold text-teal tabular-nums">75%</div>
            <p class="text-sm text-muted mt-1">Of social media consumption is video</p>
            <hr class="my-4 border-gray-200" />
            <p class="text-sm text-muted leading-relaxed">
              Short-form video drives roughly <strong>3x higher engagement</strong> than other formats.
            </p>
          </div>
          <div class="bg-soft rounded-2xl p-6 md:p-8">
            <div class="text-4xl font-display font-extrabold text-green tabular-nums">55%</div>
            <p class="text-sm text-muted mt-1">Use social media for brand research</p>
            <hr class="my-4 border-gray-200" />
            <p class="text-sm text-muted leading-relaxed">
              More than half of Malaysian users treat social media as a <strong>primary channel</strong> for researching brands.
            </p>
          </div>
        </div>

        <!-- Social Commerce highlight -->
        <div class="bg-gradient-to-br from-amber-50 via-white to-teal-50 rounded-2xl p-7 md:p-10 mt-8 border border-amber-100">
          <div class="grid md:grid-cols-2 gap-6 items-center">
            <div>
              <span class="text-[10px] font-bold uppercase tracking-wider text-accent">Social Commerce</span>
              <h3 class="text-2xl md:text-3xl font-display font-extrabold mt-2">
                USD 3.5 Billion in social commerce transactions
              </h3>
              <p class="text-muted mt-3 leading-relaxed">
                Social commerce now makes up an estimated <strong>22% of Malaysian e-commerce</strong>
                and grows around 24% per year. TikTok Shop, Instagram Shopping and WhatsApp Business
                are the main forces behind this transformation.
              </p>
              <p class="text-xs text-muted/60 mt-3 italic">Source: e-Conomy SEA 2025 (estimates)</p>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div class="bg-white rounded-xl p-5 text-center shadow-soft">
                <span class="text-3xl font-display font-extrabold text-accent">22%</span>
                <p class="text-xs text-muted mt-1">Of total e-commerce</p>
              </div>
              <div class="bg-white rounded-xl p-5 text-center shadow-soft">
                <span class="text-3xl font-display font-extrabold text-teal">24%</span>
                <p class="text-xs text-muted mt-1">Annual growth</p>
              </div>
              <div class="bg-white rounded-xl p-5 text-center shadow-soft">
                <span class="text-3xl font-display font-extrabold text-green">2.5x</span>
                <p class="text-xs text-muted mt-1">Engagement for localised content</p>
              </div>
              <div class="bg-white rounded-xl p-5 text-center shadow-soft">
                <span class="text-3xl font-display font-extrabold text-primary">88%</span>
                <p class="text-xs text-muted mt-1">Smartphone ownership (2025)</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- SECTION 4: TRENDS -->
    <section id="trends" class="py-16 md:py-24 bg-soft">
      <div class="container mx-auto px-6">
        <p class="eyebrow">Trends 2026</p>
        <h2 class="text-3xl md:text-5xl font-display font-extrabold mt-2">Digital Advertising Trends 2026</h2>
        <p class="text-muted mt-3 max-w-3xl leading-relaxed">
          The five main trends shaping Malaysia's digital advertising industry this year.
        </p>
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-5 mt-10">
          {d.trends.map(t => (
            <div class="bg-white rounded-2xl p-6 md:p-7 shadow-soft hover:shadow-pop transition-all duration-300 border border-transparent hover:border-accent/20">
              <div class="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center text-lg mb-4">📈</div>
              <h3 class="text-lg font-display font-bold">{t.title}</h3>
              <p class="text-sm text-muted mt-2 leading-relaxed">{t.desc}</p>
              <p class="text-[11px] text-muted/60 mt-3 italic">{t.source}</p>
            </div>
          ))}
        </div>
      </div>
    </section>

    <!-- SECTION 5: CHALLENGES -->
    <section id="challenges" class="py-16 md:py-24 bg-white">
      <div class="container mx-auto px-6">
        <p class="eyebrow">Challenges</p>
        <h2 class="text-3xl md:text-5xl font-display font-extrabold mt-2">Challenges & Opportunities</h2>
        <p class="text-muted mt-3 max-w-3xl leading-relaxed">
          The four main challenges facing advertisers and marketers in Malaysia in 2026.
        </p>
        <div class="grid md:grid-cols-2 gap-5 mt-10">
          {d.challenges.map(c => (
            <div class="bg-soft rounded-2xl p-6 md:p-7 border-l-4 border-accent">
              <h3 class="text-lg font-display font-bold">{c.title}</h3>
              <p class="text-sm text-muted mt-2 leading-relaxed">{c.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>

    <!-- SECTION 6: METHODOLOGY -->
    <section id="methodology" class="py-16 md:py-24 bg-gradient-to-br from-primary to-primary-2 text-white">
      <div class="container mx-auto px-6">
        <p class="text-xs font-bold uppercase tracking-[0.2em] text-accent">Methodology</p>
        <h2 class="text-3xl md:text-5xl font-display font-extrabold mt-2">Data Sources & Methodology</h2>
        <p class="text-white/70 mt-3 max-w-3xl leading-relaxed">
          {d.methodology.notes}
        </p>
        <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-8">
          {d.methodology.sources.map(s => (
            <div class="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10">
              <h3 class="text-sm font-bold">{s.name}</h3>
              <p class="text-xs text-white/60 mt-1">{s.desc}</p>
              {s.url && (
                <a href={s.url} target="_blank" rel="noopener noreferrer" class="text-xs text-accent hover:underline mt-2 inline-block">
                  Visit source →
                </a>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>

    <!-- FAQ -->
    <section class="py-16 md:py-24 bg-soft">
      <div class="container mx-auto px-6">
        <p class="eyebrow">FAQ</p>
        <h2 class="text-3xl md:text-5xl font-display font-extrabold mt-2">Frequently Asked Questions</h2>
        <div class="max-w-3xl mx-auto mt-8 space-y-3">
          {d.faqs.map(f => (
            <details class="bg-white rounded-xl shadow-soft group open:ring-1 open:ring-accent/20">
              <summary class="flex items-center justify-between p-5 cursor-pointer font-medium text-sm md:text-base list-none">
                {f.q}
                <svg class="w-4 h-4 shrink-0 text-muted group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </summary>
              <div class="px-5 pb-5 text-sm text-muted leading-relaxed">{f.a}</div>
            </details>
          ))}
        </div>
      </div>
    </section>

    <!-- FINAL CTA -->
    <section class="py-20 md:py-28 bg-gradient-to-br from-primary via-primary-2 to-ink text-white relative overflow-hidden">
      <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,rgba(245,158,11,0.1),transparent_60%)]" />
      <div class="container mx-auto px-6 text-center relative z-10">
        <h2 class="text-3xl md:text-5xl font-display font-extrabold">Need Help Making Sense of This Data?</h2>
        <p class="text-lg text-white/70 mt-4 max-w-2xl mx-auto leading-relaxed">
          The Beriklan team is ready to help you build a digital ad strategy that hits the mark.
          Discuss your campaign needs with our consultants — free, no pressure.
        </p>
        <div class="flex flex-wrap justify-center gap-4 mt-8">
          <a
            href="https://wa.me/62811919328?text=Hi%20Beriklan%2C%20I%27d%20like%20a%20digital%20ad%20strategy%20consultation%20after%20reading%20the%202026%20Industry%20Report."
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-2 bg-accent hover:bg-amber-600 text-primary font-bold text-sm rounded-full px-8 py-4 transition-all btn-shine"
          >
            Contact Us via WhatsApp
          </a>
          <a
            href="https://wa.me/62811919328?text=Hi%20Beriklan%2C%20I%27m%20interested%20in%20taking%20part%20in%20your%20digital%20advertising%20research."
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-2 border border-white/20 hover:bg-white/10 text-white font-bold text-sm rounded-full px-8 py-4 transition-all"
          >
            Take Part in the Research
          </a>
        </div>
      </div>
    </section>
  </main>
  <Footer client:only="svelte" />
</Layout>
'''

with io.open(PAGES + 'research/malaysia-digital-advertising-report-2026.astro', 'w', encoding='utf-8') as f:
    f.write(PAGE)
print('WROTE research/malaysia-digital-advertising-report-2026.astro')
print('DONE research')
