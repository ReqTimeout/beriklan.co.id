const { chromium } = require('playwright');

(async () => {
  const b = await chromium.launch();
  console.log('=== 5 PLATFORM PAGES — VISUAL + CONTENT AUDIT (desktop 1440x900) ===');
  const platforms = [
    { name: 'TikTok', slug: 'tiktok' },
    { name: 'Shopee', slug: 'shopee' },
    { name: 'YouTube', slug: 'youtube' },
    { name: 'Instagram', slug: 'instagram' },
    { name: 'Twitch', slug: 'twitch' },
  ];
  for (const p of platforms) {
    const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
    const dp = await ctx.newPage();
    await dp.goto('https://www.beriklan.co.id/jasa-view-live/' + p.slug + '/?v=' + Date.now(), { waitUntil: 'load' });
    await dp.waitForTimeout(3500);
    const a = await dp.evaluate(() => {
      const eyebrow = document.querySelector('.hero-eyebrow')?.textContent?.replace(/\s+/g, ' ').trim();
      const h1 = document.querySelector('h1')?.textContent?.replace(/\s+/g, ' ').trim();
      const subcopy = document.querySelector('.hero-sub')?.textContent?.replace(/\s+/g, ' ').trim();
      const tierNames = Array.from(document.querySelectorAll('.pricing-card .tier-name, [class*="tier-name"]')).map(el => el.textContent?.trim()).filter(Boolean).slice(0, 6);
      const cta = document.querySelector('a[href*="wa.me"]')?.textContent?.trim();
      const trustItems = Array.from(document.querySelectorAll('.hero-trust .trust-item span:nth-child(2)')).map(el => el.textContent?.trim()).filter(Boolean);
      const stats = Array.from(document.querySelectorAll('[class*="stat-num"]')).map(el => el.textContent?.trim()).filter(Boolean).slice(0, 4);
      const logoSrc = document.querySelector('img[src*=".svg"]')?.getAttribute('src');
      const heroClass = document.querySelector('header')?.className?.match(/from-\S+/)?.[0];
      return { eyebrow, h1, subcopy, tierNames, cta, trustItems, stats, logoSrc, heroClass };
    });
    console.log('\n[' + p.name + ']');
    console.log('  bg: ' + a.heroClass);
    console.log('  H1: ' + a.h1);
    console.log('  subcopy: ' + (a.subcopy?.substring(0, 130) || '(missing)') + '...');
    console.log('  Tiers: ' + (a.tierNames?.join(', ') || '(missing)'));
    console.log('  Stats: ' + (a.stats?.join(' / ') || '(missing)'));
    console.log('  Trust: ' + (a.trustItems?.slice(0, 3).join(' | ') || '(missing)'));
    console.log('  CTA: ' + a.cta);
    console.log('  Logo: ' + a.logoSrc);
    await dp.screenshot({ path: '/tmp/' + p.slug + '-audit.png', clip: { x: 0, y: 0, width: 1440, height: 900 } });
    await ctx.close();
  }
  await b.close();
})();
