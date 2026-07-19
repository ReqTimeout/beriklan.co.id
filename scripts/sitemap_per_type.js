#!/usr/bin/env node
/**
 * Custom per-content-type sitemap generator.
 *
 * Generates:
 *   /sitemap-index.xml          — points to all sub-sitemaps
 *   /sitemap-blog.xml           — /blog/[slug] only
 *   /sitemap-city.xml           — /jasa-XXX/[city] only
 *   /sitemap-pillar.xml         — /jasa-XXX/pillar only
 *   /sitemap-static.xml         — /, /blog, /order, /privacy-policy, /terms-of-service, root service pages
 *
 * Run after `npm run build` to REPLACE the default Astro sitemap.
 *
 * Usage:
 *   node scripts/sitemap_per_type.js
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const WEB = path.dirname(__dirname);
const DIST = path.join(WEB, "dist");
const SITE = "https://beriklan.co.id";

const TODAY = new Date().toISOString();

function listFiles(dir, ext = ".html") {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir).filter(f => f.endsWith(ext));
}

function listDirs(dir) {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir).filter(f => fs.statSync(path.join(dir, f)).isDirectory());
}

function urlEntry(loc, lastmod = TODAY, changefreq = "weekly", priority = 0.7) {
  return `  <url>\n    <loc>${loc}</loc>\n    <lastmod>${lastmod}</lastmod>\n    <changefreq>${changefreq}</changefreq>\n    <priority>${priority.toFixed(1)}</priority>\n  </url>`;
}

function sitemapXml(entries) {
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${entries.join("\n")}\n</urlset>\n`;
}

function sitemapIndex(sitemaps) {
  return `<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${sitemaps.map(s => `  <sitemap>\n    <loc>${s.loc}</loc>\n    <lastmod>${s.lastmod}</lastmod>\n  </sitemap>`).join("\n")}\n</sitemapindex>\n`;
}

// 1. Static pages
const staticPages = [
  { path: "/", priority: 1.0, changefreq: "daily" },
  { path: "/blog/", priority: 0.9, changefreq: "daily" },
  { path: "/order/", priority: 0.8, changefreq: "monthly" },
  { path: "/privacy-policy/", priority: 0.3, changefreq: "yearly" },
  { path: "/terms-of-service/", priority: 0.3, changefreq: "yearly" },
  { path: "/jasa-digital-marketing/", priority: 0.9, changefreq: "weekly" },
  { path: "/jasa-iklan-facebook/", priority: 0.9, changefreq: "weekly" },
  { path: "/jasa-iklan-instagram/", priority: 0.9, changefreq: "weekly" },
  { path: "/jasa-iklan-tiktok/", priority: 0.9, changefreq: "weekly" },
  { path: "/jasa-iklan-google/", priority: 0.9, changefreq: "weekly" },
  { path: "/jasa-iklan-youtube/", priority: 0.9, changefreq: "weekly" },
  { path: "/jasa-kelola-instagram/", priority: 0.9, changefreq: "weekly" },
  { path: "/jasa-kelola-tiktok/", priority: 0.9, changefreq: "weekly" },
  { path: "/jasa-pembuatan-website/", priority: 0.9, changefreq: "weekly" },
  { path: "/jasa-pembuatan-landing-page/", priority: 0.9, changefreq: "weekly" },
];
const staticEntries = staticPages.map(p => urlEntry(`${SITE}${p.path}`, TODAY, p.changefreq, p.priority));
fs.writeFileSync(path.join(DIST, "sitemap-static.xml"), sitemapXml(staticEntries));
console.log(`[sitemap-static] ${staticPages.length} URLs`);

// 2. Blog posts (read posts.json once, then map by slug)
let postsMap = new Map();
try {
  const posts = JSON.parse(fs.readFileSync(path.join(WEB, "src/data/posts.json"), "utf-8"));
  for (const p of posts) {
    if (p.slug) postsMap.set(p.slug, p);
  }
} catch (e) {
  console.error("[warn] could not read posts.json:", e.message);
}
const blogDir = path.join(DIST, "blog");
const blogSlugs = listDirs(blogDir);
const blogEntries = [];
for (const slug of blogSlugs) {
  if (!fs.existsSync(path.join(blogDir, slug, "index.html"))) continue;
  const p = postsMap.get(slug);
  const lastmod = p?.iso_date ? new Date(p.iso_date).toISOString() : TODAY;
  blogEntries.push(urlEntry(`${SITE}/blog/${slug}/`, lastmod, "weekly", 0.8));
}
fs.writeFileSync(path.join(DIST, "sitemap-blog.xml"), sitemapXml(blogEntries));
console.log(`[sitemap-blog] ${blogEntries.length} URLs`);

// 3. City pages (walk only the 11 known service dirs)
const KNOWN_SERVICES = [
  "jasa-digital-marketing",
  "jasa-iklan-facebook",
  "jasa-iklan-instagram",
  "jasa-iklan-tiktok",
  "jasa-iklan-google",
  "jasa-iklan-youtube",
  "jasa-kelola-instagram",
  "jasa-kelola-tiktok",
  "jasa-pembuatan-website",
  "jasa-pembuatan-landing-page",
  "jasa-view-live",
];
const cityEntries = [];
for (const svc of KNOWN_SERVICES) {
  const svcDir = path.join(DIST, svc);
  if (!fs.existsSync(svcDir) || !fs.statSync(svcDir).isDirectory()) continue;
  const cities = listDirs(svcDir);
  for (const city of cities) {
    if (city === "pilar") continue;
    const indexPath = path.join(svcDir, city, "index.html");
    if (!fs.existsSync(indexPath)) continue;
    cityEntries.push(urlEntry(`${SITE}/${svc}/${city}/`, TODAY, "weekly", 0.85));
  }
}
fs.writeFileSync(path.join(DIST, "sitemap-city.xml"), sitemapXml(cityEntries));
console.log(`[sitemap-city] ${cityEntries.length} URLs`);

// 4. Pillar pages
const pillarEntries = [];
for (const svc of KNOWN_SERVICES) {
  const pillarPath = path.join(DIST, svc, "pilar", "index.html");
  if (fs.existsSync(pillarPath)) {
    pillarEntries.push(urlEntry(`${SITE}/${svc}/pilar/`, TODAY, "weekly", 0.9));
  }
}
fs.writeFileSync(path.join(DIST, "sitemap-pillar.xml"), sitemapXml(pillarEntries));
console.log(`[sitemap-pillar] ${pillarEntries.length} URLs`);

// 5. Tag pages: ALL Excel keywords (4952) — each keyword has dedicated /blog/tag/{slug}/ page
//    Source: src/data/keyword-to-posts.json (from build_keyword_map.py)
let keywordMap = {};
try {
  keywordMap = JSON.parse(fs.readFileSync(path.join(WEB, "src/data/keyword-to-posts.json"), "utf-8"));
} catch (e) {
  console.error("[warn] keyword-to-posts.json not found:", e.message);
}
const tagEntries = [];
for (const [slug, info] of Object.entries(keywordMap)) {
  const lastmod = TODAY;
  const priority = info.has_posts ? 0.65 : 0.4;
  const changefreq = info.has_posts ? "weekly" : "monthly";
  tagEntries.push(urlEntry(`${SITE}/blog/tag/${slug}/`, lastmod, changefreq, priority));
}
// Split if needed (Google limits sitemap to 50K URLs; 4952 is fine)
fs.writeFileSync(path.join(DIST, "sitemap-tag.xml"), sitemapXml(tagEntries));
console.log(`[sitemap-tag] ${tagEntries.length} URLs (from ${Object.keys(keywordMap).length} keywords)`);

// 6. Sitemap index
const indexXml = sitemapIndex([
  { loc: `${SITE}/sitemap-static.xml`, lastmod: TODAY },
  { loc: `${SITE}/sitemap-pillar.xml`, lastmod: TODAY },
  { loc: `${SITE}/sitemap-city.xml`, lastmod: TODAY },
  { loc: `${SITE}/sitemap-tag.xml`, lastmod: TODAY },
  { loc: `${SITE}/sitemap-blog.xml`, lastmod: TODAY },
]);
fs.writeFileSync(path.join(DIST, "sitemap-index.xml"), indexXml);
console.log(`[sitemap-index] 5 sub-sitemaps`);

// 6. Replace old sitemap
const oldSitemap0 = path.join(DIST, "sitemap-0.xml");
if (fs.existsSync(oldSitemap0)) {
  fs.unlinkSync(oldSitemap0);
  console.log(`[cleanup] removed dist/sitemap-0.xml`);
}
const oldSitemapIndex = path.join(DIST, "sitemap_index.xml");
if (fs.existsSync(oldSitemapIndex)) {
  fs.unlinkSync(oldSitemapIndex);
  console.log(`[cleanup] removed dist/sitemap_index.xml`);
}

console.log(`\n[total] ${staticPages.length} static + ${blogEntries.length} blog + ${cityEntries.length} city + ${pillarEntries.length} pillar + ${tagEntries.length} tag`);
