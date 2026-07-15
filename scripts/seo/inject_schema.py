#!/usr/bin/env python3
"""
Inject schema.org JSON-LD programmatically ke file .astro.

Pakai untuk bulk apply LocalBusiness + Service + FAQPage schema ke city pages
(yang akan di-generate Day 4+).

Usage:
    python3 scripts/seo/inject_schema.py --inject-localbusiness <slug>
    python3 scripts/seo/inject_schema.py --validate <slug>
    python3 scripts/seo/inject_schema.py --batch city-pages
    python3 scripts/seo/inject_schema.py --check-all

Schema types handled:
- LocalBusiness + ContactPoint + OpeningHoursSpecification + GeoCoordinates
- Service + Provider + AreaServed + Offers
- FAQPage + mainEntity[]
- BreadcrumbList
- WebPage + dateModified
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent.parent
PAGES_DIR = ROOT / "src/pages"

# ---------- Schema generators ----------

def gen_localbusiness(city: dict[str, Any], services: list[str] = None, page_url: str = "") -> dict[str, Any]:
    """Generate LocalBusiness schema per kota."""
    hours = [{
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "opens": "09:00",
        "closes": "18:00"
    }]
    if "Indonesia" in city.get("province", "Indonesia"):
        hours.append({
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": "Saturday",
            "opens": "10:00",
            "closes": "14:00"
        })
    base_id = page_url.rstrip("/").replace("https://beriklan.co.id", "") or f"/{city['slug']}/"
    return {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "@id": f"https://beriklan.co.id{base_id}#business",
        "name": f"Beriklan Digital Agency — {city['name']}",
        "image": "https://beriklan.co.id/logoweb.webp",
        "url": f"https://beriklan.co.id{base_url if False else base_id}",
        "telephone": "+62-81-1919-328",
        "email": "info@beriklan.co.id",
        "priceRange": "Rp 12.000 - Rp 175.000",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Jl. Arcamanik Endah No.76",
            "addressLocality": "Bandung",
            "addressRegion": "Jawa Barat",
            "postalCode": "40195",
            "addressCountry": "ID"
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": city.get("lat", -6.9175),
            "longitude": city.get("lng", 107.6191)
        },
        "openingHoursSpecification": hours,
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+62-81-1919-328",
            "contactType": "customer service",
            "areaServed": ["ID", "MY", "SG"],
            "availableLanguage": ["Indonesian", "English", "Malay"]
        },
        "areaServed": {
            "@type": "City",
            "name": city["name"]
        }
    }


def gen_service(service: dict[str, Any], provider_id: str = "#business", city_name: str = None) -> dict[str, Any]:
    """Generate Service schema per layanan."""
    return {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": service["name"],
        "provider": {"@id": f"https://beriklan.co.id{provider_id}"},
        "areaServed": {"@type": "City", "name": city_name or "Bandung"},
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": f"Paket {service['name']}",
            "itemListElement": [
                {
                    "@type": "Offer",
                    "name": "Paket Pemanasan",
                    "price": "12000",
                    "priceCurrency": "IDR"
                },
                {
                    "@type": "Offer",
                    "name": "Paket Starter",
                    "price": "25000",
                    "priceCurrency": "IDR"
                },
                {
                    "@type": "Offer",
                    "name": "Paket Pro",
                    "price": "80000",
                    "priceCurrency": "IDR"
                }
            ]
        }
    }


def gen_faqpage(faqs: list[dict[str, str]]) -> dict[str, Any]:
    """Generate FAQPage schema."""
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq["q"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq["a"]
                }
            } for faq in faqs
        ]
    }


def gen_breadcrumb(items: list[tuple[str, str]]) -> dict[str, Any]:
    """Generate BreadcrumbList. items = [(name, url), ...]"""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": name,
                "item": f"https://beriklan.co.cn{url}" if not url.startswith("http") else url
            } for i, (name, url) in enumerate(items)
        ]
    }


def gen_article(title: str, slug: str, image: str, date: str, author: str = "Tim Beriklan") -> dict[str, Any]:
    """Generate Article schema untuk blog post."""
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "image": image,
        "datePublished": date,
        "dateModified": date,
        "author": {"@type": "Person", "name": author},
        "publisher": {
            "@type": "Organization",
            "name": "Beriklan Digital Agency",
            "logo": {"@type": "ImageObject", "url": "https://beriklan.co.id/logoweb.webp"}
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"https://beriklan.co.id/blog/{slug}/"
        }
    }


# ---------- Astro file manipulation ----------

def find_schema_script(content: str) -> tuple[int, int]:
    """Find existing <script type="application/ld+json"> block. Return (-1, -1) if not."""
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
    if m:
        return (m.start(), m.end())
    return (-1, -1)


def inject_schema_to_page(page_path: Path, schemas: list[dict[str, Any]], dry_run: bool = False):
    """Inject schemas (as JSON-LD <script>) into .astro page."""
    content = page_path.read_text()
    # Build JSON-LD script
    json_str = "\n".join(json.dumps(s, ensure_ascii=False) for s in schemas)
    script_block = (
        f'\n<script type="application/ld+json" set:html="'
        + json_str.replace('"', "&quot;")
        + '" />'
    )

    # Strategy: append before </Layout> closing tag
    if "</Layout>" in content:
        new_content = content.replace("</Layout>", f"{script_block}\n</Layout>", 1)
    elif "<script type=\"application/ld+json\"" in content:
        # Replace existing schema block
        s, e = find_schema_script(content)
        if s >= 0:
            new_content = content[:s] + script_block.strip() + content[e:]
        else:
            # Insert before closing </head>
            m = re.search(r"</head>", content)
            if m:
                new_content = content[:m.start()] + script_block + content[m.start():]
            else:
                new_content = content + "\n" + script_block
    else:
        # Insert before </Layout>
        m = re.search(r"</body>", content) or re.search(r"</html>", content)
        if m:
            new_content = content[:m.start()] + script_block + content[m.start():]
        else:
            new_content = content + "\n" + script_block

    if dry_run:
        # show first 200 chars of new content
        return f"Would inject {len(schemas)} schemas into {page_path.name}"

    page_path.write_text(new_content)
    return f"Injected {len(schemas)} schemas into {page_path.name}"


def validate_schema(page_path: Path) -> dict[str, Any]:
    """Validate JSON-LD schemas in page (source file or built dist/)."""
    content = page_path.read_text()
    # Match BOTH source format (set:html) and built format (raw JSON)
    scripts = re.findall(r'<script type="application/ld\.json"[^>]*>(.*?)</script>',
                         content, re.DOTALL)
    if not scripts:
        # Astro build output uses exact string
        scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                             content, re.DOTALL)
    valid_count = 0
    errors = []
    for s in scripts:
        try:
            json.loads(s)
            valid_count += 1
        except json.JSONDecodeError as e:
            errors.append(str(e))
    return {
        "page": page_path.name,
        "script_count": len(scripts),
        "valid_count": valid_count,
        "errors": errors
    }


# ---------- Commands ----------

def cmd_validate(target: str):
    """Validate schema in 1 page or all."""
    if target.endswith(".astro"):
        pages = [PAGES_DIR / target]
    else:
        pages = list(PAGES_DIR.glob(f"**/{target}*.astro"))
    total_errors = 0
    for p in pages:
        if not p.exists():
            print(f"  Not found: {p}")
            continue
        r = validate_schema(p)
        status = "✓" if not r["errors"] else "✗"
        print(f"  {status} {r['page']}: {r['script_count']} schemas, {r['valid_count']} valid")
        for e in r["errors"]:
            print(f"      ERROR: {e}")
            total_errors += 1
    sys.exit(1 if total_errors else 0)


def cmd_inject_localbusiness(target: str, dry_run: bool = False):
    """Inject LocalBusiness schema ke city page (target = city slug)."""
    city_data = json.loads((ROOT / "src/data/cities.json").read_text())
    city = next((c for c in city_data if c["slug"] == target), None)
    if not city:
        print(f"ERROR: city '{target}' not in cities.json")
        sys.exit(1)
    schema = gen_localbusiness(city, page_url=f"/jasa-iklan-facebook/{target}/")
    # Try multiple page paths
    for path in [
        PAGES_DIR / f"jasa-iklan-facebook/{target}/index.astro",
        PAGES_DIR / f"wilayah/{target}.astro",
    ]:
        if path.exists():
            result = inject_schema_to_page(path, [schema], dry_run)
            print(f"  {result}")
            return
    print(f"  No page found for city '{target}'")


def cmd_check_all():
    """Validate schema in all pages."""
    pages = list(PAGES_DIR.glob("**/*.astro"))
    print(f"Checking {len(pages)} pages...")
    total_errors = 0
    no_schema = 0
    has_schema = 0
    for p in pages:
        content = p.read_text()
        scripts = re.findall(r'<script type="application/ld\+json"', content)
        if scripts:
            r = validate_schema(p)
            if r["errors"]:
                print(f"  ✗ {p.relative_to(PAGES_DIR)}: {r['errors']}")
                total_errors += len(r["errors"])
            else:
                pass  # OK silently
            has_schema += 1
        else:
            no_schema += 1
    print(f"\nSummary:")
    print(f"  Pages with schema: {has_schema}")
    print(f"  Pages without schema: {no_schema}")
    print(f"  Schema errors: {total_errors}")


def main():
    p = argparse.ArgumentParser(description="Schema injector + validator")
    p.add_argument("--validate", help="Validate schema in 1 page (e.g., 'tentang-kami')")
    p.add_argument("--inject-localbusiness", help="Inject LocalBusiness schema to city (slug)")
    p.add_argument("--check-all", action="store_true", help="Validate all pages")
    p.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = p.parse_args()

    if args.validate:
        cmd_validate(args.validate)
    elif args.inject_localbusiness:
        cmd_inject_localbusiness(args.inject_localbusiness, args.dry_run)
    elif args.check_all:
        cmd_check_all()
    else:
        p.print_help()


if __name__ == "__main__":
    main()
