#!/usr/bin/env python3
"""
Build rank match profile — scrape top 10 Google SERP untuk keyword,
extract content profile (word count, H2/H3 counts, entities, density, schema, FAQ, table),
aggregate ke target profile per keyword.

Output: src/data/rank_match_profiles.json

Sources:
- Google scrape (free, rate-limited ~100 query/hari sebelum kena CAPTCHA)
- Serper.dev (optional, free 50 search/bln)
- Google CSE JSON API (optional, free 100/hari, butuh API key)

Default pakai Google scrape fallback ke Bing.

Usage:
    python3 scripts/seo/build_rank_match.py --keyword "jasa iklan facebook jakarta"
    python3 scripts/seo/build_rank_match.py --pilot 5 keywords.json
    python3 scripts/seo/build_rank_match.py --batch-batch batch1 --limit 10
    python3 scripts/seo/build_rank_match.py --query "google_cse" --key CSB_KEY
"""

import argparse
import json
import re
import sys
import time
import random
from collections import Counter
from pathlib import Path
from typing import Any, Optional
from urllib.parse import unquote, urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).parent.parent.parent
OUTPUT_FILE = ROOT / "src/data/rank_match_profiles.json"

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]

# Indonesian stopwords for entity extraction
STOPWORDS_ID = set([
    "yang", "dan", "di", "dari", "untuk", "dengan", "pada", "ini", "itu",
    "atau", "tidak", "juga", "ada", "oleh", "telah", "akan", "dapat",
    "anda", "kami", "kita", "mereka", "dia", "beliau", "ia", "kamu",
    "saya", "tapi", "namun", "maka", "sehingga", "karena", "kalau",
    "jika", "bila", "ketika", "saat", "waktu", "kala", "semasa",
    "sangat", "sekali", "amat", "begitu", "demikian", "begini",
    "semua", "seluruh", "selama", "antara", "diantara", "lewat",
    "melalui", "menurut", "terhadap", "atas", "bawah", "depan",
    "belakang", "samping", "dekat", "jauh", "dalam", "luar",
    "banyak", "sedikit", "beberapa", "tiap", "setiap", "masing",
    "harus", "perlu", "mau", "ingin", "hendak", "sudah", "belum",
])

STOPWORDS_ID_DOMAIN = set([
    "jasa", "iklan", "facebook", "instagram", "google", "tiktok",
    "youtube", "ads", "digital", "marketing", "agency", "harga",
    "biaya", "cara", "tips", "trik", "cara", "info", "berita",
])


# ---------- Google SERP scraping ----------

def scrape_google_serp(keyword: str, num: int = 10) -> list[dict[str, str]]:
    """Scrape top `num` Google organic results untuk `keyword`.
    Returns list of {url, title, snippet}."""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
    }
    url = f"https://www.google.com/search?q={requests.utils.quote(keyword)}&hl=id&gl=id&num={num}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            print(f"  Google returned {r.status_code}, falling back to Bing")
            return scrape_bing_serp(keyword, num)
    except Exception as e:
        print(f"  Google scrape error: {e}")
        return scrape_bing_serp(keyword, num)

    soup = BeautifulSoup(r.text, "html.parser")
    results = []

    # Try multiple selectors (Google rotates)
    for selector in [
        "div.g",  # classic
        "div.Gx5Zad",  # 2024+
        "div.tF2Cxc",  # 2024+
    ]:
        items = soup.select(selector)
        if items:
            for item in items[:num]:
                link_tag = item.select_one("a[href]")
                title_tag = item.select_one("h3")
                snippet_tag = item.select_one(".VwiC3b, .BNeawe, .yXgCKe")
                if link_tag and title_tag:
                    href = link_tag.get("href", "")
                    if href.startswith("/url?q="):
                        href = href.split("/url?q=")[1].split("&")[0]
                    try:
                        href = unquote(href)
                    except Exception:
                        pass
                    if href.startswith("http"):
                        results.append({
                            "url": href,
                            "title": title_tag.get_text(strip=True),
                            "snippet": snippet_tag.get_text(strip=True) if snippet_tag else "",
                        })
                if len(results) >= num:
                    break
            break

    if not results:
        print(f"  No results from Google selectors, trying Bing")
        return scrape_bing_serp(keyword, num)

    return results


def scrape_bing_serp(keyword: str, num: int = 10) -> list[dict[str, str]]:
    """Fallback scrape top results from Bing."""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html",
    }
    url = f"https://www.bing.com/search?q={requests.utils.quote(keyword)}&count={num}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        print(f"  Bing scrape error: {e}")
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    results = []
    for li in soup.select("li.b_algo")[:num]:
        link_tag = li.select_one("h2 a")
        snippet_tag = li.select_one(".b_caption p, .b_snippet")
        if link_tag:
            results.append({
                "url": link_tag.get("href", ""),
                "title": link_tag.get_text(strip=True),
                "snippet": snippet_tag.get_text(strip=True) if snippet_tag else "",
            })
    return results


# ---------- Content analysis ----------

def analyze_content(url: str) -> Optional[dict[str, Any]]:
    """Fetch URL, extract content profile."""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "id-ID,id;q=0.9",
    }
    try:
        r = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
        if r.status_code != 200:
            return None
        if "text/html" not in r.headers.get("content-type", ""):
            return None
    except Exception as e:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    # Remove non-content
    for tag in soup(["script", "style", "nav", "footer", "aside", "iframe"]):
        tag.decompose()

    # Count headings
    h2_count = len(soup.find_all("h2"))
    h3_count = len(soup.find_all("h3"))
    img_count = len(soup.find_all("img"))

    # Has FAQ (look for common patterns)
    text_lower = soup.get_text().lower()
    has_faq = bool(re.search(r"\bfaq\b|pertanyaan umum|questions? and answers", text_lower))
    has_table = bool(soup.find("table"))
    has_list = bool(soup.find("ul")) or bool(soup.find("ol"))

    # Schema detection in script tags
    page_text = r.text
    has_schema_article = '"@type":"Article"' in page_text or '"@type": "Article"' in page_text
    has_schema_faq = '"@type":"FAQPage"' in page_text or '"@type": "FAQPage"' in page_text
    has_schema_breadcrumb = '"@type":"BreadcrumbList"' in page_text
    has_schema_organization = '"@type":"Organization"' in page_text

    # Get main content text
    main = soup.find("main") or soup.find("article") or soup.find("div[role=main]") or soup
    text = main.get_text(separator=" ", strip=True)
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)

    # Entity extraction (simple)
    words_lower = [w.lower() for w in words if len(w) > 3]
    filtered = [w for w in words_lower if w not in STOPWORDS_ID and w not in STOPWORDS_ID_DOMAIN]
    entities = [w for w, _ in Counter(filtered).most_common(20)]

    # Internal/external link count
    domain = urlparse(url).netloc
    links = soup.find_all("a[href]")
    internal_links = sum(1 for l in links if domain in l.get("href", "") or l.get("href", "").startswith("/"))
    external_links = sum(1 for l in links if l.get("href", "").startswith("http") and domain not in l.get("href", ""))

    return {
        "url": url,
        "domain": domain,
        "word_count": word_count,
        "h2_count": h2_count,
        "h3_count": h3_count,
        "img_count": img_count,
        "internal_links": internal_links,
        "external_links": external_links,
        "has_faq": has_faq,
        "has_table": has_table,
        "has_list": has_list,
        "has_schema_article": has_schema_article,
        "has_schema_faq": has_schema_faq,
        "has_schema_breadcrumb": has_schema_breadcrumb,
        "has_schema_organization": has_schema_organization,
        "entities": entities,
    }


# ---------- Profile aggregation ----------

def aggregate_profile(keyword: str, results: list[dict[str, str]]) -> dict[str, Any]:
    """Build target profile dari aggregated top 10 SERP results."""
    print(f"  Analyzing content of {len(results)} URLs...")
    profiles = []
    for i, r in enumerate(results, 1):
        print(f"    [{i}/{len(results)}] {r['url'][:80]}...", end=" ", flush=True)
        p = analyze_content(r["url"])
        if p:
            profiles.append(p)
            print(f"OK ({p['word_count']} words)")
        else:
            print("FAIL")
        time.sleep(random.uniform(1.0, 2.0))

    if not profiles:
        return {
            "keyword": keyword,
            "error": "no_content_fetched",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    # Aggregate median values for numeric fields
    def median(vals):
        if not vals: return 0
        s = sorted(vals)
        n = len(s)
        return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) // 2

    word_counts = [p["word_count"] for p in profiles if p["word_count"] > 100]
    h2_counts = [p["h2_count"] for p in profiles]
    h3_counts = [p["h3_count"] for p in profiles]
    img_counts = [p["img_count"] for p in profiles]
    int_links = [p["internal_links"] for p in profiles]

    # Aggregated entities (top across all profiles)
    all_entities = []
    for p in profiles:
        all_entities.extend(p["entities"])
    top_entities = [e for e, _ in Counter(all_entities).most_common(15)]

    # Boolean: most common
    def common_bool(field):
        vals = [p[field] for p in profiles]
        return sum(vals) >= len(vals) * 0.6

    return {
        "keyword": keyword,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sample_size": len(profiles),
        "target": {
            "word_count": median(word_counts) if word_counts else 1500,
            "h2_count": max(median(h2_counts), 3),
            "h3_count": max(median(h3_counts), 4),
            "img_count": max(median(img_counts), 1),
            "internal_links": max(median(int_links), 3),
            "must_have_faq": common_bool("has_faq"),
            "must_have_table": common_bool("has_table"),
            "must_have_list": common_bool("has_list"),
            "must_have_schema_article": common_bool("has_schema_article"),
            "must_have_schema_faq": common_bool("has_schema_faq"),
            "must_have_schema_breadcrumb": common_bool("has_schema_breadcrumb"),
            "entities": top_entities,
        },
        "competitors": [
            {
                "url": p["url"],
                "domain": p["domain"],
                "word_count": p["word_count"],
                "h2_count": p["h2_count"],
                "h3_count": p["h3_count"],
                "has_faq": p["has_faq"],
                "has_schema_faq": p["has_schema_faq"],
            } for p in profiles
        ],
    }


def save_profile(profile: dict[str, Any]):
    """Append ke rank_match_profiles.json (merge by keyword)."""
    profiles = []
    if OUTPUT_FILE.exists():
        try:
            profiles = json.loads(OUTPUT_FILE.read_text())
        except Exception:
            profiles = []
    # upsert
    existing_idx = next((i for i, p in enumerate(profiles) if p.get("keyword") == profile["keyword"]), -1)
    if existing_idx >= 0:
        profiles[existing_idx] = profile
    else:
        profiles.append(profile)
    OUTPUT_FILE.write_text(json.dumps(profiles, ensure_ascii=False, indent=2))
    print(f"  Saved profile for '{profile['keyword']}' to {OUTPUT_FILE.relative_to(ROOT)}")


def main():
    p = argparse.ArgumentParser(description="Build rank match profile dari SERP top 10")
    p.add_argument("--keyword", help="Single keyword to profile")
    p.add_argument("--pilot", type=int, default=0, help="Run first N keywords from keywords.json as pilot")
    p.add_argument("--batch", help="Batch name from keywords.json (e.g., 'services', 'city')")
    p.add_argument("--limit", type=int, default=10, help="Limit number of SERP results per keyword")
    p.add_argument("--no-fetch-content", action="store_true", help="Skip content fetch (SERP only)")
    args = p.parse_args()

    targets = []
    if args.keyword:
        targets = [args.keyword]
    elif args.pilot or args.batch:
        keywords = json.loads((ROOT / "src/data/keywords.json").read_text())
        if args.pilot:
            targets = [k["keyword"] for k in keywords[:args.pilot] if k.get("keyword")]
        elif args.batch:
            for k in keywords:
                svc = k.get("service") or ""
                if args.batch == "services" and svc and "jasa-" in svc:
                    targets.append(k["keyword"])
                elif args.batch == "meta" and "facebook" in svc.lower() + (k["keyword"] or "").lower():
                    targets.append(k["keyword"])
                elif args.batch == "google" and "google" in svc.lower() + (k["keyword"] or "").lower():
                    targets.append(k["keyword"])
                if len(targets) >= (args.pilot or 10):
                    break

    if not targets:
        print("ERROR: provide --keyword or --pilot/--batch")
        sys.exit(1)

    print(f"Building rank match profiles for {len(targets)} keywords...")
    for i, kw in enumerate(targets, 1):
        print(f"\n[{i}/{len(targets)}] Keyword: {kw}")
        results = scrape_google_serp(kw, args.limit)
        print(f"  Got {len(results)} SERP results")
        if args.no_fetch_content or not results:
            profile = {
                "keyword": kw,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "serp_results": results,
                "note": "no_content_fetched",
            }
        else:
            profile = aggregate_profile(kw, results)
        save_profile(profile)
        time.sleep(random.uniform(2.0, 5.0))

    print(f"\nDone. {len(targets)} profiles saved.")


if __name__ == "__main__":
    main()
