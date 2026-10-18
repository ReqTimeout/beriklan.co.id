#!/usr/bin/env python3
"""
gen_city_content_my.py — generate truthful city-content.json entries for
Beriklan.my (English copy, Malaysia SME context, MYR).

Ported from beriklan.co.id/scripts/gen_city_content.py. Uses ONLY real data
from web/src/data/cities.json (city name, state/province, sme count via
`umkm_count`, and English `local_facts`). No fabricated growth percentages or
case studies. Generated HTML follows the same H2/H3/ul structure the ID version
uses so CityContentBlock renders it correctly (TOC, callout, related links).

Additive & idempotent: only fills keys that are MISSING.

Usage:
  python3 gen_city_content_my.py            # fill missing, write city-content.json
  python3 gen_city_content_my.py --dry      # print what would be added
"""
import argparse
import json
import os

ROOT = os.path.expanduser("~/Desktop/beriklan.my")
CITIES = os.path.join(ROOT, "web/src/data/cities.json")
CONTENT = os.path.join(ROOT, "web/src/data/city-content.json")

SERVICES = [
    "facebook-ads-management", "instagram-ads-management", "tiktok-ads-management",
    "google-ads-management", "youtube-ads-management",
    "instagram-management", "tiktok-management",
    "website-development", "landing-page-design",
    "digital-marketing-agency",
]

SERVICE_LABEL = {
    "facebook-ads-management": "Facebook Ads",
    "instagram-ads-management": "Instagram Ads",
    "tiktok-ads-management": "TikTok Ads",
    "google-ads-management": "Google Ads",
    "youtube-ads-management": "YouTube Ads",
    "instagram-management": "Instagram Management",
    "tiktok-management": "TikTok Management",
    "website-development": "Website Development",
    "landing-page-design": "Landing Page Design",
    "digital-marketing-agency": "Digital Marketing",
}

AD_SERVICES = {
    "facebook-ads-management", "instagram-ads-management", "tiktok-ads-management",
    "google-ads-management", "youtube-ads-management",
}
ORGANIC_SERVICES = {"instagram-management", "tiktok-management"}
BUILD_SERVICES = {"website-development", "landing-page-design"}


def build_html(city: dict, service: str) -> str:
    name = city["name"]
    state = city.get("province") or "Malaysia"
    sme = city.get("umkm_count") or 0
    facts = city.get("local_facts") or []
    label = SERVICE_LABEL[service]

    # Truthful opening — uses real SME count and local_facts only.
    sme_txt = f"is home to an estimated {sme:,} SMEs" if sme else "has an active SME ecosystem"
    fact_line = ""
    if facts:
        fact_line = " " + ". ".join(f.rstrip(".") for f in facts) + "."

    if service == "digital-marketing-agency":
        h1 = f"Why Businesses in {name} Need Integrated Digital Marketing"
        opening = (
            f"{name}, {state}, {sme_txt}.{fact_line} "
            f"With so many local operators competing for attention, businesses that run "
            f"measured campaigns across multiple channels (Meta, Google, TikTok, YouTube) "
            f"hold a real advantage in reaching the right audience efficiently."
        )
        work_items = [
            ("Audit & Strategy:", f"We map your business situation in {name} and prioritise channels based on your objectives."),
            ("Multi-Channel Execution:", "Campaigns are coordinated so they reinforce one another instead of running in isolation."),
            ("Optimisation & Reporting:", "Performance is tracked regularly with transparent weekly reports you can verify."),
            ("Continuous Iteration:", "Strategy is adjusted each cycle based on data, not assumptions."),
        ]
    elif service in AD_SERVICES:
        plat = label.replace(" Ads", "")
        h1 = f"Why Businesses in {name} Need {label} Management"
        opening = (
            f"{name}, {state}, {sme_txt}.{fact_line} "
            f"{label} let local businesses reach a relevant audience with precise targeting, "
            f"so your media budget works harder to generate measurable leads and sales."
        )
        work_items = [
            ("Local Research & Strategy:", f"We research the {name} market specifically — audience behaviour, competitors and relevant keywords."),
            ("Setup & Execution:", f"Your {plat} campaign is configured with aligned targeting, budget and creative."),
            ("Optimisation & Reporting:", "Performance is optimised regularly and reported transparently every week."),
            ("Long-Term Collaboration:", "We work alongside your business so ads stay effective as the market shifts."),
        ]
    elif service in ORGANIC_SERVICES:
        plat = label.replace(" Management", "")
        h1 = f"Why Businesses in {name} Need {label}"
        opening = (
            f"{name}, {state}, {sme_txt}.{fact_line} "
            f"Consistent {plat} management helps local businesses build an organic presence, "
            f"quality audience engagement and long-term trust without depending entirely on ad spend."
        )
        work_items = [
            ("Brief & Audit:", f"A discussion to understand your brand voice and business objectives in {name}."),
            ("Content Plan:", "We build a content calendar, captions and assets that suit your niche's rhythm."),
            ("Execution & Community:", "Scheduled posting, plus replying to DMs and comments in your brand's tone of voice."),
            ("Review & Pivot:", "Regular reports with actionable insights to refine the strategy."),
        ]
    else:  # build
        prod = "professional website" if service == "website-development" else "high-converting landing page"
        h1 = f"Why Businesses in {name} Need {label}"
        opening = (
            f"{name}, {state}, {sme_txt}.{fact_line} "
            f"A {prod} is a critical foundation for any business that wants to look credible in "
            f"search results and convert ad traffic into customers consistently."
        )
        work_items = [
            ("Brief & Wireframe:", f"We align on the goals and structure of your {prod} for your {name} business."),
            ("Design & Build:", "Development with custom design, mobile-responsive layout and tracking installed."),
            ("Testing & Launch:", "Cross-browser, speed and security checks before going live."),
            ("Support:", "Ongoing technical help and periodic content updates."),
        ]

    # Common challenges (generic, honest — no fabricated specifics)
    challenges = [
        f"Businesses in {name} often struggle to build a measured, consistent advertising strategy.",
        "Broad targeting means the media budget converts inefficiently.",
        "Creative that is not aligned with the local audience lowers engagement.",
        "Without regular reporting, it is hard to know which channel truly delivers ROI.",
    ]

    work_html = "\n".join(
        f"<li><strong>{t}</strong> {d}</li>" for t, d in work_items
    )
    chal_html = "\n".join(f"<li>{c}</li>" for c in challenges)

    faq = (
        f"<h3>How much does {label} cost in {name}?</h3>\n"
        f"<p>Pricing depends on the package and the scope of your business needs in {name}. "
        f"We offer a consultation to recommend the right fit — the "
        f"management fee is separate from your media budget, which is paid directly to the platform.</p>\n"
        f"<h3>Is this suitable for SMEs in {name}?</h3>\n"
        f"<p>Yes. With an active SME ecosystem in {name}, this service is designed so businesses "
        f"with a mid-range budget can run measured, transparent campaigns.</p>\n"
        f"<h3>What does onboarding look like?</h3>\n"
        f"<p>It starts with a short audit, then strategy, followed by execution and regular reporting "
        f"as agreed.</p>"
    )

    html = (
        f"<h2>{h1}</h2>\n"
        f"<p>{opening}</p>\n\n"
        f"<h2>Common Challenges & Mistakes in {name}</h2>\n"
        f"<p>Many local businesses face similar hurdles when trying to get the most from digital "
        f"marketing. Here are a few of them:</p>\n"
        f"<ul>\n{chal_html}\n</ul>\n\n"
        f"<h2>How the Beriklan Team Works for Businesses in {name}</h2>\n"
        f"<p>To support businesses in {name}, our team follows a data-driven, transparent approach:</p>\n"
        f"<ul>\n{work_html}\n</ul>\n\n"
        f"<h2>Frequently Asked Questions</h2>\n"
        f"{faq}\n"
    )
    return html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    cities = json.load(open(CITIES, encoding="utf-8"))
    city_by_slug = {c["slug"]: c for c in cities}
    my_cities = [c for c in cities if not c.get("is_international")]

    try:
        content = json.load(open(CONTENT, encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        content = {}
    if not isinstance(content, dict):
        content = {}

    plan = []
    for city in my_cities:
        for svc in SERVICES:
            key = f"{svc}/{city['slug']}/"
            if key in content:
                continue
            plan.append((svc, city["slug"], key))

    print(f"MY cities: {len(my_cities)} | services: {len(SERVICES)} | missing entries: {len(plan)}")
    if args.dry:
        for svc, city_slug, key in plan[:8]:
            print(f"  would add: {key}")
        return

    for svc, city_slug, key in plan:
        content[key] = build_html(city_by_slug[city_slug], svc)

    json.dump(content, open(CONTENT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Wrote {len(plan)} new entries. Total entries now: {len(content)}")


if __name__ == "__main__":
    main()
