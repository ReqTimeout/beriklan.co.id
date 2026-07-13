const { chromium } = require('playwright');
const platforms = [
    { name: 'TikTok', slug: 'tiktok' },
    { name: 'Shopee', slug: 'shopee' },
    { name: 'YouTube', slug: 'youtube' },
    { name: 'Instagram', slug: 'instagram' },
    { name: 'Twitch', slug: 'twitch' }
];
const vps = [
    { name: 'DESKTOP', w: 1440, h: 900, mobile: false },
    { name: 'MOBILE', w: 390, h: 844, mobile: true }
];
(async () => {
    const b = await chromium.launch();
    console.log('PLATFORM | VP | H1 | TIERS | FEAT | FAQ | LOGO | COPY');
    console.log('---|---|---|---|---|---|---|---|---');
    for (const v of vps) {
        for (const p of platforms) {
            const ctx = await b.newContext({ viewport: {width: v.w, height: v.h}, isMobile: v.mobile, hasTouch: v.mobile});
            const dp = await ctx.newPage();
            await dp.goto('https://www.beriklan.co.id/jasa-view-live/' + p.slug + '/?v3=' + Date.now(), {waitUntil: 'load'});
            await dp.waitForTimeout(2500);
            const a = await dp.evaluate(() => {
                const h1 = document.querySelector('h1');
                const subcopy = document.querySelector('.hero-sub');
                return {
                    h1: h1?.textContent?.replace(/\s+/g, ' ').trim()?.substring(0, 70),
                    tiers: document.querySelectorAll('.pricing-card').length,
                    feats: document.querySelectorAll('.feature-card').length,
                    faq: document.querySelectorAll('.faq-item').length,
                    logo: !!document.querySelector("img[src*='tiktok.svg'], img[src*='shopee.svg'], img[src*='youtube.svg'], img[src*='instagram.svg'], img[src*='twitch.svg']"),
                    subcopyStart: subcopy?.textContent?.replace(/\s+/g, ' ').trim()?.substring(0, 80),
                };
            });
            const status = (a.tiers === 6 && a.feats >= 5 && a.faq >= 5 && a.logo) ? 'OK' : 'FAIL';
            console.log(p.name + ' | ' + v.name + ' | ' + a.h1 + ' | ' + a.tiers + ' | ' + a.feats + ' | ' + a.faq + ' | ' + (a.logo?'YES':'NO') + ' | ' + status);
            await dp.screenshot({path: '/tmp/' + p.slug + '-' + v.name.toLowerCase() + '.png'});
            await ctx.close();
        }
    }
    await b.close();
})();
