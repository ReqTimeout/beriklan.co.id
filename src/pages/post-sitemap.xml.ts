// WordPress-style post sitemap (Yoast: post-sitemap.xml)
// Lists all blog posts from posts.json
import posts from '../data/posts.json';

const SITE = 'https://beriklan.co.id';

export function GET() {
    // Sort newest first
    const sorted = [...posts].sort((a, b) =>
        (b.iso_date || '').localeCompare(a.iso_date || '')
    );

    const urls = sorted.map(p => {
        const lastmod = p.iso_date ? p.iso_date.slice(0, 10) : new Date().toISOString().slice(0, 10);
        return `    <url>
        <loc>${SITE}/blog/${p.slug}/</loc>
        <lastmod>${lastmod}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>`;
    }).join('\n');

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
