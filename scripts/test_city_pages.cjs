// Batch test all 252 city pages
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = "https://www.beriklan.co.id";

// Get all city URLs from filesystem
function getCityUrls() {
  const base = "/Users/maabook/Desktop/beriklan.co.id/web/src/pages";
  const services = fs.readdirSync(base).filter(d => d.startsWith("jasa-") && fs.statSync(`${base}/${d}`).isDirectory());
  const urls = [];
  for (const svc of services) {
    // Skip pilar subdir
    if (svc.endsWith("pilar")) continue;
    const cities = fs.readdirSync(`${base}/${svc}`).filter(c => fs.statSync(`${base}/${svc}/${c}`).isDirectory() && c !== "pilar");
    for (const city of cities) {
      urls.push(`${BASE_URL}/${svc}/${city}/`);
    }
  }
  return urls;
}

async function testUrl(page, url) {
  const issues = [];
  try {
    const resp = await page.goto(url, { waitUntil: "domcontentloaded", timeout: 15000 });
    if (!resp || resp.status() !== 200) {
      return { url, status: resp ? resp.status() : "no_resp", issues: ["HTTP not 200"] };
    }

    // Check if page is real city page (has city-content-block) or 404 fallback
    const cityBlock = await page.$(".city-content-block");
    if (!cityBlock) {
      return { url, status: "404_fallback", issues: ["no city-content-block (404 fallback?)"] };
    }

    const meta = await page.$(".city-content-block .text-xs");
    if (!meta) issues.push("meta_bar_missing");

    const faq = await page.$(".faq-item");
    if (!faq) issues.push("no_faq");

    // Testimonial check — only required for tier-1 cities (bandung, jakarta, surabaya, etc.)
    const tst = await page.$(".tst-card, .tst-featured, .tst-mini");
    const urlParts = url.split("/");
    const cityName = urlParts[urlParts.length - 2];
    const tier1Cities = ['bandung', 'jakarta', 'surabaya', 'medan', 'makassar', 'semarang'];
    if (!tst && tier1Cities.includes(cityName)) {
      issues.push("no_testimonial (tier-1 city)");
    }

    const html = await page.content();
    if (!html.includes('"@type":"FAQPage"')) issues.push("no_faq_schema");
    if (!html.includes('"@type":"BreadcrumbList"')) issues.push("no_breadcrumb_schema");
    if (!html.includes('"@type":"Service"')) issues.push("no_service_schema");

    return { url, status: 200, issues };
  } catch (e) {
    return { url, status: "error", issues: [String(e).slice(0, 80)] };
  }
}

(async () => {
  const urls = getCityUrls();
  console.log(`Testing ${urls.length} city URLs...`);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });

  const results = [];
  for (let i = 0; i < urls.length; i++) {
    const page = await context.newPage();
    try {
      const result = await testUrl(page, urls[i]);
      results.push(result);
      if ((i + 1) % 30 === 0) {
        process.stdout.write(`  ${i+1}/${urls.length} done\n`);
      }
    } finally {
      await page.close();
    }
  }

  await browser.close();

  console.log("\n" + "=".repeat(70));
  console.log(`Total: ${results.length}`);
  console.log(`OK: ${results.filter(r => !r.issues).length}`);
  console.log(`With issues: ${results.filter(r => r.issues.length > 0).length}`);
  console.log(`Errors: ${results.filter(r => r.status === "error").length}`);

  const issueCounts = {};
  for (const r of results) {
    for (const issue of r.issues) {
      issueCounts[issue] = (issueCounts[issue] || 0) + 1;
    }
  }
  console.log("\nIssue breakdown:");
  for (const [issue, count] of Object.entries(issueCounts).sort((a, b) => b[1] - a[1])) {
    console.log(`  ${String(count).padStart(3)}x ${issue}`);
  }

  console.log("\nFirst 10 pages with most issues:");
  const sorted = results.filter(r => r.issues.length > 0).sort((a, b) => b.issues.length - a.issues.length);
  for (const r of sorted.slice(0, 10)) {
    console.log(`  ${r.url.replace(BASE_URL, "")}: ${r.issues.join(", ")}`);
  }

  // Save report
  fs.writeFileSync("/tmp/city_test_report.json", JSON.stringify(results, null, 2));
  console.log(`\nFull report: /tmp/city_test_report.json`);
})();