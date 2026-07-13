// WordPress-style sitemap index (mimics Yoast SEO structure)
// Lists: post-sitemap.xml + page-sitemap.xml + sitemap-index.xml
const SITE = 'https://beriklan.co.id';

export function GET() {
    const today = new Date().toISOString().slice(0, 10);
    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="//beriklan.co.id/sitemap.xsl"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <sitemap>
        <loc>${SITE}/post-sitemap.xml</loc>
        <lastmod>${today}</lastmod>
    </sitemap>
    <sitemap>
        <loc>${SITE}/page-sitemap.xml</loc>
        <lastmod>${today}</lastmod>
    </sitemap>
    <sitemap>
        <loc>${SITE}/sitemap-index.xml</loc>
        <lastmod>${today}</lastmod>
    </sitemap>
</sitemapindex>`;
    return new Response(xml, {
        headers: {
            'Content-Type': 'application/xml; charset=utf-8',
            'Cache-Control': 'public, max-age=3600',
        },
    });
}
