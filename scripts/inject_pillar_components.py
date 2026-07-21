#!/usr/bin/env python3
"""Inject StatsBand + ComparisonTable + AuthorBio into all service pages (except FB which is done)."""
import re
from pathlib import Path

PAGES = [
    ("jasa-digital-marketing.astro", "Digital Marketing"),
    ("jasa-iklan-google.astro", "Iklan Google"),
    ("jasa-iklan-instagram.astro", "Iklan Instagram"),
    ("jasa-iklan-tiktok.astro", "Iklan TikTok"),
    ("jasa-iklan-youtube.astro", "Iklan YouTube"),
    ("jasa-kelola-instagram.astro", "Kelola Instagram"),
    ("jasa-kelola-tiktok.astro", "Kelola TikTok"),
    ("jasa-pembuatan-landing-page.astro", "Landing Page"),
    ("jasa-pembuatan-website.astro", "Pembuatan Website"),
]

PAGES_DIR = Path("src/pages")

# Service-specific overrides
SVC_NAME_OVERRIDES = {
    "jasa-digital-marketing.astro": "Digital Marketing",
    "jasa-iklan-google.astro": "Iklan Google",
    "jasa-iklan-instagram.astro": "Iklan Instagram",
    "jasa-iklan-tiktok.astro": "Iklan TikTok",
    "jasa-iklan-youtube.astro": "Iklan YouTube",
    "jasa-kelola-instagram.astro": "Instagram",
    "jasa-kelola-tiktok.astro": "TikTok",
    "jasa-pembuatan-landing-page.astro": "Landing Page",
    "jasa-pembuatan-website.astro": "Website",
}

for filename, _ in PAGES:
    filepath = PAGES_DIR / filename
    content = filepath.read_text()
    svc = SVC_NAME_OVERRIDES.get(filename, "Layanan")

    # 1. Add imports after StepGrid import
    import_marker = "import StepGrid from '../components/StepGrid.svelte';"
    if import_marker not in content:
        print(f"SKIP {filename}: import marker not found")
        continue
    if "StatsBand.astro" in content:
        print(f"SKIP {filename}: already has StatsBand")
        continue

    new_imports = (
        "import StepGrid from '../components/StepGrid.svelte';\n"
        "import StatsBand from '../components/StatsBand.astro';\n"
        "import ComparisonTable from '../components/ComparisonTable.astro';\n"
        "import AuthorBio from '../components/AuthorBio.astro';"
    )
    content = content.replace(import_marker, new_imports, 1)

    # 2. Insert StatsBand after "WHY FACEBOOK ADS" comment
    # Pattern: <!-- ====================== WHY ... ====================== -->
    why_pattern = r"(    <!-- ={10,} WHY [^=]+ ={10,} -->)"
    if re.search(why_pattern, content):
        content = re.sub(
            why_pattern,
            r"    <!-- ====================== STATS BAND ====================== -->\n    <StatsBand />\n\n\1",
            content,
            count=1,
        )

    # 3. Insert ComparisonTable after </section> closing pricing, before "STATS / TRUST" comment
    # Pattern: </section>\n\n    <!-- ====================== STATS / TRUST ====================== -->
    pricing_pattern = r"(</section>)\n\n(    <!-- ={10,} STATS / TRUST ={10,} -->)"
    if re.search(pricing_pattern, content):
        content = re.sub(
            pricing_pattern,
            rf"\1\n\n    <!-- ====================== COMPARISON TABLE ====================== -->\n    <ComparisonTable serviceName=\"{svc}\" />\n\n\2",
            content,
            count=1,
        )

    # 4. Insert AuthorBio before <RelatedServices
    related_pattern = r"(<RelatedServices)"
    if re.search(related_pattern, content):
        content = re.sub(
            related_pattern,
            r"    <!-- ====================== AUTHOR BIO (E-E-A-T) ====================== -->\n    <AuthorBio />\n\n\1",
            content,
            count=1,
        )

    filepath.write_text(content)
    print(f"OK {filename}: svc={svc}")

print("\nDone.")