#!/usr/bin/env python3
"""Inject PAASection into all 10 service pages after FaqAccordion."""
import re
from pathlib import Path

# (filename, service_slug, canonical_url)
PAGES = [
    ("jasa-digital-marketing.astro", "jasa-digital-marketing", "https://beriklan.co.id/jasa-digital-marketing/"),
    ("jasa-iklan-facebook.astro", "jasa-iklan-facebook", "https://beriklan.co.id/jasa-iklan-facebook/"),
    ("jasa-iklan-google.astro", "jasa-iklan-google", "https://beriklan.co.id/jasa-iklan-google/"),
    ("jasa-iklan-instagram.astro", "jasa-iklan-instagram", "https://beriklan.co.id/jasa-iklan-instagram/"),
    ("jasa-iklan-tiktok.astro", "jasa-iklan-tiktok", "https://beriklan.co.id/jasa-iklan-tiktok/"),
    ("jasa-iklan-youtube.astro", "jasa-iklan-youtube", "https://beriklan.co.id/jasa-iklan-youtube/"),
    ("jasa-kelola-instagram.astro", "jasa-kelola-instagram", "https://beriklan.co.id/jasa-kelola-instagram/"),
    ("jasa-kelola-tiktok.astro", "jasa-kelola-tiktok", "https://beriklan.co.id/jasa-kelola-tiktok/"),
    ("jasa-pembuatan-landing-page.astro", "jasa-pembuatan-landing-page", "https://beriklan.co.id/jasa-pembuatan-landing-page/"),
    ("jasa-pembuatan-website.astro", "jasa-pembuatan-website", "https://beriklan.co.id/jasa-pembuatan-website/"),
]

PAGES_DIR = Path("src/pages")

for filename, service_slug, canonical_url in PAGES:
    filepath = PAGES_DIR / filename
    content = filepath.read_text()

    # Skip if already injected
    if "<PAASection" in content:
        print(f"SKIP {filename}: already has PAASection")
        continue

    # 1. Add import after FaqAccordion import
    import_marker = "import FaqAccordion from '../components/FaqAccordion.svelte';"
    if import_marker not in content:
        print(f"SKIP {filename}: FaqAccordion import not found")
        continue

    new_imports = (
        "import FaqAccordion from '../components/FaqAccordion.svelte';\n"
        "import PAASection from '../components/PAASection.astro';"
    )
    content = content.replace(import_marker, new_imports, 1)

    # 2. Insert PAASection after </section> closing FAQ section
    # Pattern: <FaqAccordion items={faqs} client:visible /> </div> </section>
    # Insert PAASection before <RelatedServices
    related_pattern = r"(<RelatedServices)"
    if not re.search(related_pattern, content):
        print(f"SKIP {filename}: RelatedServices not found")
        continue

    paa_block = (
        f"\n    <!-- ====================== PAA (People Also Ask) ====================== -->\n"
        f"    <PAASection service=\"{service_slug}\" pageUrl=\"{canonical_url}\" />\n\n    "
    )
    content = re.sub(related_pattern, paa_block + r"\1", content, count=1)

    filepath.write_text(content)
    print(f"OK {filename} → service={service_slug}")

print("\nDone.")
