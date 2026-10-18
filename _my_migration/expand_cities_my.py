#!/usr/bin/env python3
"""Expand beriklan.my cities.json from 15 -> 25 MY cities.

Adds the 10 cities named in plan F2-1 with curated, truthful local_facts
(English). Idempotent: skips cities whose slug already exists. Writes back
in the same 2-space-indented JSON shape.
"""
import json
import os

ROOT = os.path.expanduser("~/Desktop/beriklan.my")
CITIES = os.path.join(ROOT, "web/src/data/cities.json")

NEW = [
    {
        "slug": "alor-setar", "name": "Alor Setar", "alt_names": [], "province": "Kedah",
        "tier": 3, "country": "MY", "lat": 6.1248, "lng": 100.3678, "umkm_count": 22000,
        "local_facts": [
            "Kedah's state capital and administrative centre",
            "Agriculture, rice trade and government services anchor the local economy",
            "Growing online retail adoption among northern-region SMEs",
        ],
        "is_international": False,
    },
    {
        "slug": "kota-bharu", "name": "Kota Bharu", "alt_names": [], "province": "Kelantan",
        "tier": 3, "country": "MY", "lat": 6.1254, "lng": 102.2381, "umkm_count": 28000,
        "local_facts": [
            "Kelantan's cultural and commercial capital on the East Coast",
            "Vibrant traditional retail, textiles and food trade",
            "Strong home-based and social-commerce seller community",
        ],
        "is_international": False,
    },
    {
        "slug": "kuala-terengganu", "name": "Kuala Terengganu", "alt_names": [], "province": "Terengganu",
        "tier": 3, "country": "MY", "lat": 5.3302, "lng": 103.1408, "umkm_count": 24000,
        "local_facts": [
            "Terengganu's coastal state capital",
            "Tourism, handicraft and F&B businesses drive local commerce",
            "Rising demand for digital marketing among East Coast SMEs",
        ],
        "is_international": False,
    },
    {
        "slug": "miri", "name": "Miri", "alt_names": [], "province": "Sarawak",
        "tier": 3, "country": "MY", "lat": 4.3999, "lng": 113.9914, "umkm_count": 26000,
        "local_facts": [
            "Sarawak's northern resort city and oil-and-gas hub",
            "Services, tourism and retail support a diverse SME base",
            "Cross-border trade activity with neighbouring Brunei",
        ],
        "is_international": False,
    },
    {
        "slug": "sandakan", "name": "Sandakan", "alt_names": [], "province": "Sabah",
        "tier": 3, "country": "MY", "lat": 5.8402, "lng": 118.1179, "umkm_count": 20000,
        "local_facts": [
            "Sabah's second-largest city and East Coast commercial centre",
            "Trade, agriculture and eco-tourism shape local business",
            "Expanding internet access is lifting online retail adoption",
        ],
        "is_international": False,
    },
    {
        "slug": "tawau", "name": "Tawau", "alt_names": [], "province": "Sabah",
        "tier": 3, "country": "MY", "lat": 4.2448, "lng": 117.8912, "umkm_count": 19000,
        "local_facts": [
            "Southeastern Sabah trade town near the Indonesian border",
            "Agriculture, plantation and cross-border commerce dominate",
            "Growing SME interest in social-media selling",
        ],
        "is_international": False,
    },
    {
        "slug": "iskandar-puteri", "name": "Iskandar Puteri", "alt_names": ["Nusajaya"], "province": "Johor",
        "tier": 2, "country": "MY", "lat": 1.4260, "lng": 103.6295, "umkm_count": 32000,
        "local_facts": [
            "Fast-growing township within the Iskandar Malaysia economic corridor",
            "Property, education and services attract cross-border investment",
            "Young, digitally active population close to Singapore",
        ],
        "is_international": False,
    },
    {
        "slug": "batu-pahat", "name": "Batu Pahat", "alt_names": [], "province": "Johor",
        "tier": 3, "country": "MY", "lat": 1.8548, "lng": 102.9325, "umkm_count": 27000,
        "local_facts": [
            "Established commercial town in western Johor",
            "Strong textile, manufacturing and retail SME base",
            "Active local entrepreneur and e-commerce seller community",
        ],
        "is_international": False,
    },
    {
        "slug": "sibu", "name": "Sibu", "alt_names": [], "province": "Sarawak",
        "tier": 3, "country": "MY", "lat": 2.2874, "lng": 111.8305, "umkm_count": 23000,
        "local_facts": [
            "Central Sarawak river-port and trading town",
            "Timber trade, retail and F&B underpin the local economy",
            "Rising digital adoption among family-run businesses",
        ],
        "is_international": False,
    },
    {
        "slug": "langkawi", "name": "Langkawi", "alt_names": [], "province": "Kedah",
        "tier": 3, "country": "MY", "lat": 6.3500, "lng": 99.8000, "umkm_count": 12000,
        "local_facts": [
            "Duty-free island and one of Malaysia's top tourism destinations",
            "Hospitality, tours and retail dominate the local economy",
            "Highly seasonal demand tied to domestic and international tourism",
        ],
        "is_international": False,
    },
]


def main():
    cities = json.load(open(CITIES, encoding="utf-8"))
    have = {c["slug"] for c in cities}
    added = 0
    for c in NEW:
        if c["slug"] in have:
            continue
        cities.append(c)
        added += 1
    assert len(cities) == 25, f"expected 25 cities, got {len(cities)}"
    json.dump(cities, open(CITIES, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(CITIES, "a").write("\n")
    print(f"Added {added} cities. Total now: {len(cities)}")
    print("Slugs:", ", ".join(c["slug"] for c in cities))


if __name__ == "__main__":
    main()
