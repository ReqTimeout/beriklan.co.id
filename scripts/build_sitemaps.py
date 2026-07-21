"""
Build per-content-type sitemaps for beriklan.co.id
==================================================
Replaces the auto-generated sitemap from @astrojs/sitemap plugin with
a hand-crafted split that maps to SEO strategy:

  1. sitemap-static.xml     - homepage, blog index, order, privacy, terms
  2. sitemap-services.xml   - 10 main service pages (/jasa-*/)
  3. sitemap-city.xml       - 250+ city service pages
  4. sitemap-pillar.xml     - 10 cluster/pillar hub pages
  5. sitemap-blog.xml       - 1966 blog posts
  6. sitemap-blog-pagination.xml - 81 paginated blog archive pages
  7. sitemap-blog-tag.xml   - 4952 tag archive pages
  + sitemap-index.xml that references all of the above

lastmod is content-driven:
  - blog posts: posts[i].iso_date (publish date) -> falls back to freshness.json last_reviewed
  - city/pages: build-time lastmod (acceptable per Google)

Reads dist/ to enumerate URLs (post-build). Idempotent.
"""
import os, re, sys, json, datetime, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, 'web')
DIST = os.path.join(WEB, 'dist')
SITE = 'https://beriklan.co.id'

if not os.path.isdir(DIST):
    print('ERROR: dist/ not found. Run `npm run build` first.')
    sys.exit(1)

NOW = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')

# Load posts for lastmod (real publish date)
posts_path = os.path.join(WEB, 'src/data/posts.json')
posts = []
if os.path.exists(posts_path):
    posts = json.load(open(posts_path))

post_iso = {}
for p in posts:
    iso = p.get('iso_date')
    if iso:
        # strip if it has timezone offset
        post_iso[p['slug']] = iso

def load_freshness():
    f = os.path.join(WEB, 'public/data/freshness.json')
    if not os.path.exists(f):
        return {}
    return json.load(open(f))

freshness = load_freshness()
slug_lastmod = {}
for slug, iso in post_iso.items():
    slug_lastmod[slug] = iso
for slug, info in freshness.items():
    if isinstance(info, dict):
        lr = info.get('last_reviewed')
        if lr and (slug not in slug_lastmod or lr > slug_lastmod[slug]):
            slug_lastmod[slug] = lr

# Enumerate URLs by walking dist/
def collect_url_dirs():
    """Return set of URL paths (relative, trailing slash) that exist in dist/."""
    urls = set()
    # Top-level index.html -> /
    if os.path.exists(os.path.join(DIST, 'index.html')):
        urls.add('/')
    for path, dirs, files in os.walk(DIST):
        rel = os.path.relpath(path, DIST)
        if rel == '.':
            continue
        if 'index.html' in files:
            url = '/' + rel.replace(os.sep, '/') + '/'
            urls.add(url)
    return urls

all_urls = collect_url_dirs()

# Categorize
def is_static(u):
    # Root + blog index + order + legal + calculator tools
    return u in ('/', '/blog/', '/order/', '/privacy-policy/', '/terms-of-service/') or re.match(r'^/kalkulator-[\w-]+/$', u) is not None

def is_service(u):
    # /jasa-*/ but not /jasa-*/something
    if re.match(r'^/jasa-[\w-]+/$', u):
        return True
    return False

def is_city(u):
    # /jasa-*/[city]/  OR  /jasa-*/[city]/pilar/ (no - the pillar ends in /pilar/)
    if re.match(r'^/jasa-[\w-]+/[\w-]+/$', u):
        return True
    return False

def is_pillar(u):
    return re.match(r'^/jasa-[\w-]+/pilar/$', u) is not None

def is_harga(u):
    # /harga-iklan-facebook/bandung/ etc.
    return re.match(r'^/harga-iklan-[\w-]+/[\w-]+/$', u) is not None

def is_blog_pagination(u):
    return re.match(r'^/blog/page/\d+/$', u) is not None

def is_blog_tag(u):
    return re.match(r'^/blog/tag/[\w-]+/$', u) is not None

def is_blog_post(u):
    # /blog/[slug]/  but not /blog/page/, /blog/tag/, /blog/index
    if not re.match(r'^/blog/[\w-]+/$', u):
        return False
    sub = u.rstrip('/').split('/')[-1]
    if sub in ('page', 'tag', 'category'):
        return False
    # exclude index pages with no slug
    if u in ('/blog/',):
        return False
    return True

buckets = {
    'static': [],
    'services': [],
    'city': [],
    'pillar': [],
    'harga': [],
    'blog': [],
    'blog-pagination': [],
    'blog-tag': [],
}

for u in sorted(all_urls):
    if is_static(u):
        buckets['static'].append(u)
    elif is_pillar(u):
        buckets['pillar'].append(u)
    elif is_harga(u):
        buckets['harga'].append(u)
    elif is_city(u):
        buckets['city'].append(u)
    elif is_service(u):
        buckets['services'].append(u)
    elif is_blog_pagination(u):
        buckets['blog-pagination'].append(u)
    elif is_blog_tag(u):
        buckets['blog-tag'].append(u)
    elif is_blog_post(u):
        buckets['blog'].append(u)

def slug_from_blog_post(u):
    return u.rstrip('/').split('/')[-1]

def xml_escape(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace("'", '&apos;').replace('"', '&quot;'))

def lastmod_for(u, key):
    if key == 'blog':
        slug = slug_from_blog_post(u)
        lm = slug_lastmod.get(slug, NOW)
        return lm
    return NOW

PRIORITY = {
    'static': '1.0',
    'services': '0.9',
    'pillar': '0.8',
    'city': '0.7',
    'harga': '0.7',
    'blog': '0.6',
    'blog-pagination': '0.4',
    'blog-tag': '0.3',
}

CHANGEFREQ = {
    'static': 'daily',
    'services': 'weekly',
    'pillar': 'weekly',
    'city': 'weekly',
    'harga': 'weekly',
    'blog': 'monthly',
    'blog-pagination': 'daily',
    'blog-tag': 'weekly',
}

def build_sitemap_xml(urls, key):
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        lm = lastmod_for(u, key)
        parts.append('  <url>')
        parts.append(f'    <loc>{xml_escape(SITE + u)}</loc>')
        parts.append(f'    <lastmod>{lm}</lastmod>')
        parts.append(f'    <changefreq>{CHANGEFREQ[key]}</changefreq>')
        parts.append(f'    <priority>{PRIORITY[key]}</priority>')
        parts.append('  </url>')
    parts.append('</urlset>')
    return '\n'.join(parts) + '\n'

def build_index_xml():
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    order = ['static', 'services', 'city', 'pillar', 'harga', 'blog', 'blog-pagination', 'blog-tag']
    for k in order:
        if buckets[k]:
            parts.append('  <sitemap>')
            parts.append(f'    <loc>{xml_escape(SITE + f"/sitemap-{k}.xml")}</loc>')
            parts.append(f'    <lastmod>{NOW}</lastmod>')
            parts.append('  </sitemap>')
    parts.append('</sitemapindex>')
    return '\n'.join(parts) + '\n'

# Write
print('=== URL categorization ===')
total = 0
for k, urls in buckets.items():
    print(f'  {k:18s}: {len(urls):5d}')
    total += len(urls)
print(f'  {"TOTAL":18s}: {total:5d}')
print()

# Write all sitemaps
written = []
for k, urls in buckets.items():
    if not urls:
        continue
    path = os.path.join(DIST, f'sitemap-{k}.xml')
    with open(path, 'w') as f:
        f.write(build_sitemap_xml(urls, k))
    written.append((k, len(urls), path))

# Write sitemap-index.xml
index_path = os.path.join(DIST, 'sitemap-index.xml')
with open(index_path, 'w') as f:
    f.write(build_index_xml())

# Write a fallback sitemap.xml (some tools check this name)
sitemap_xml_path = os.path.join(DIST, 'sitemap.xml')
with open(sitemap_xml_path, 'w') as f:
    f.write(build_index_xml())

print('=== Written ===')
for k, n, p in written:
    print(f'  sitemap-{k}.xml: {n} URLs')
print(f'  sitemap-index.xml: {len(written)} sitemaps referenced')
print(f'  sitemap.xml: alias of sitemap-index.xml')

# Remove old default @astrojs/sitemap output (sitemap-0.xml, sitemap-tag.xml, etc.)
for legacy in ['sitemap-0.xml', 'sitemap-tag.xml']:
    p = os.path.join(DIST, legacy)
    if os.path.exists(p):
        os.remove(p)
        print(f'  removed legacy {legacy}')
