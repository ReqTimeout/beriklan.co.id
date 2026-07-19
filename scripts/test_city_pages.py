#!/usr/bin/env python3
"""
Batch test all 242 city pages for:
- HTTP 200 response
- FAQ schema present
- BreadcrumbList schema present
- Testimonial cards rendered (not empty)
- Meta bar visible
"""
import asyncio
import re
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "https://www.beriklan.co.id"

# Get all city URLs
def get_city_urls():
    urls = []
    base = Path("/Users/maabook/Desktop/beriklan.co.id/web/src/pages")
    for city_dir in sorted(base.glob("jasa-*/")):
        service = city_dir.name.rstrip("/")
        # Skip pillar dir
        if service.endswith("/pilar") or service == "pilar":
            continue
        for city_file in sorted(city_dir.glob("*/index.astro")):
            city = city_file.parent.name
            urls.append(f"{BASE_URL}/{service}/{city}/")
    return urls

async def test_url(page, url):
    """Test one URL for all key issues."""
    issues = []
    try:
        resp = await page.goto(url, waitUntil="domcontentloaded", timeout=15000)
        if not resp or resp.status != 200:
            return {"url": url, "status": resp.status if resp else "no_resp", "issues": ["HTTP not 200"]}

        # Check meta bar
        meta = await page.query_selector(".city-content-block .text-xs")
        if not meta:
            issues.append("meta bar missing")

        # Check FAQ section
        faq = await page.query_selector(".faq-item")
        if not faq:
            issues.append("no FAQ items")

        # Check testimonials (only on service pages that have them)
        tst = await page.query_selector(".tst-card")
        if not tst:
            issues.append("no testimonial cards (CSS broken?)")

        # Check schema markup
        html = await page.content()
        if '"@type":"FAQPage"' not in html:
            issues.append("FAQPage schema missing")
        if '"@type":"BreadcrumbList"' not in html:
            issues.append("BreadcrumbList missing")
        if '"@type":"Service"' not in html:
            issues.append("Service schema missing")

        return {"url": url, "status": 200, "issues": issues}
    except Exception as e:
        return {"url": url, "status": "error", "issues": [str(e)[:80]]}

async def main():
    urls = get_city_urls()
    print(f"Testing {len(urls)} city URLs...")

    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})

        for i, url in enumerate(urls):
            page = await context.new_page()
            try:
                result = await test_url(page, url)
                results.append(result)
                # Progress
                if (i + 1) % 20 == 0:
                    print(f"  {i+1}/{len(urls)} done...")
            finally:
                await page.close()

        await browser.close()

    # Summary
    print(f"\n{'='*70}")
    print(f"Total: {len(results)}")
    print(f"OK: {sum(1 for r in results if not r['issues'])}")
    print(f"With issues: {sum(1 for r in results if r['issues'])}")
    print(f"Errors: {sum(1 for r in results if r['status'] == 'error')}")

    # Show issues breakdown
    issue_counts = {}
    for r in results:
        for issue in r['issues']:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
    print(f"\nIssue breakdown:")
    for issue, count in sorted(issue_counts.items(), key=lambda x: -x[1]):
        print(f"  {count:3}× {issue}")

    # Show first 5 pages with most issues
    print(f"\nFirst 10 pages with most issues:")
    for r in sorted(results, key=lambda x: -len(x['issues']))[:10]:
        if r['issues']:
            print(f"  {r['url'].replace(BASE_URL, '')}: {', '.join(r['issues'])}")

    return results

if __name__ == "__main__":
    asyncio.run(main())