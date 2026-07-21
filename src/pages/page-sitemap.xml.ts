// WordPress-style page sitemap (Yoast: page-sitemap.xml)
// Lists all static pages: homepage + service pages + blog index
const SITE = 'https://beriklan.co.id';
const TODAY = new Date().toISOString().slice(0, 10);

const pages = [
    { path: '/', priority: '1.0', changefreq: 'weekly' },
    { path: '/blog/', priority: '0.9', changefreq: 'daily' },
    { path: '/order/', priority: '0.8', changefreq: 'monthly' },
    { path: '/jasa-digital-marketing/', priority: '0.9', changefreq: 'monthly' },
    { path: '/jasa-iklan-facebook/', priority: '0.9', changefreq: 'monthly' },
    { path: '/jasa-iklan-instagram/', priority: '0.9', changefreq: 'monthly' },
    { path: '/jasa-iklan-tiktok/', priority: '0.9', changefreq: 'monthly' },
    { path: '/jasa-iklan-google/', priority: '0.9', changefreq: 'monthly' },
    { path: '/jasa-iklan-youtube/', priority: '0.9', changefreq: 'monthly' },
    { path: '/jasa-kelola-instagram/', priority: '0.9', changefreq: 'monthly' },
    { path: '/jasa-kelola-tiktok/', priority: '0.9', changefreq: 'monthly' },
    { path: '/jasa-pembuatan-website/', priority: '0.9', changefreq: 'monthly' },
    { path: '/jasa-pembuatan-landing-page/', priority: '0.9', changefreq: 'monthly' },
    { path: '/kalkulator-budget-iklan/', priority: '0.8', changefreq: 'monthly' },
    { path: '/kalkulator-roas/', priority: '0.8', changefreq: 'monthly' },
    { path: '/kalkulator-roi/', priority: '0.8', changefreq: 'monthly' },
];

export function GET() {
    const urls = pages.map(p => `    <url>
        <loc>${SITE}${p.path}</loc>
        <lastmod>${TODAY}</lastmod>
        <changefreq>${p.changefreq}</changefreq>
        <priority>${p.priority}</priority>
    </url>`).join('\n');

    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="//beriklan.co.id/sitemap.xsl"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>`;
    return new Response(xml, {
        headers: {
            'Content-Type': 'application/xml; charset=utf-8',
            'Cache-Control': 'public, max-age=3600',
        },
    });
}
