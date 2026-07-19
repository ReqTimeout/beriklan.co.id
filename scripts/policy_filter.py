"""
AdSense Prohibited Content Pre-Publish Filter — SHARED blocklist for JS Worker + Python scripts.

AdSense prohibits:
- Adult content
- Violence/gore
- Drugs (illegal)
- Copyright infringement (cracks, pirated, free downloads of paid content)
- Misleading health/financial claims (guaranteed ROI, 100% success, "pasti untung")
- Hacking/cracking
- Counterfeit goods (fake branded)
- Weapons/firearms
- Tobacco
- Hate speech / discrimination
- Shocking content (gore, accidents for shock value)
- Misinformation (medical, political, civic)
- Clickbait / misleading
- Deceptive practices (fake forms, hidden charges)

Each entry has: category, keywords (lowercase), severity (block=hard reject, warn=flag for review).

USAGE in Worker (JS):
  import { checkPolicyViolation } from './policy_filter.js';
  const result = checkPolicyViolation(text);
  if (result.violation && result.severity === 'block') { reject; }
  if (result.violation && result.severity === 'warn')  { log; allow; }

USAGE in Python:
  from policy_filter import check_policy_violation
  result = check_policy_violation(text)
  if result['violation'] and result['severity'] == 'block': reject
"""

POLICY_BLOCKLIST = {
    "adult": {
        "severity": "block",
        "description": "Adult/sexual content prohibited by AdSense",
        "keywords": [
            "sex", "porn", "pornografi", "porno", "nude", "naked", "telanjang",
            "bugil", "bokep", "ngentot", "kentot", "ewe", "coli",
            "xxx", "vcs", "full frontal", "milf", "creampie",
        ],
    },
    "violence": {
        "severity": "block",
        "description": "Violent/gore content prohibited",
        "keywords": [
            "bunuh", "bantai", "bantai-bantai", "bom bunuh diri", "teror bom",
            "pembantaian", "genosida", "kekerasan seksual", "pedofil", "pedofilia",
            "senjata api", "senjata tajam", "bom rakitan",
        ],
    },
    "drugs": {
        "severity": "block",
        "description": "Illegal drugs prohibited",
        "keywords": [
            "narkoba", "sabu-sabu", "sabu", "ganja", "ekstasi", "putaw",
            "heroin", "kokain", "methamphetamine", "pembuatan sabu",
            "cara membuat sabu", "cara buat ekstasi", "jual sabu",
        ],
    },
    "weapons": {
        "severity": "block",
        "description": "Weapons/firearms (sales/instructions)",
        "keywords": [
            "jual senjata api", "jual pistol", "jual bom", "merakit bom",
            "beli senjata ilegal", "senjata ilegal",
        ],
    },
    "tobacco": {
        "severity": "block",
        "description": "Tobacco sales prohibited",
        "keywords": [
            "jual rokok ilegal", "rokok tanpa cukai", "rokok palsu",
            "rokop tanpa pita cukai", "rokok tanpa pajak",
        ],
    },
    "copyright": {
        "severity": "block",
        "description": "Copyright infringement (cracks/pirated)",
        "keywords": [
            "download gratis", "crack software", "software crack", "crack aplikasi",
            "aplikasi crack", "serial number", "bajakan", "pirated",
            "full version gratis", "premium gratis", "lifetime premium",
            "nulled", "patch", "keygen", "mod apk unlimited", "mod apk premium",
            "cheat engine",
        ],
    },
    "hacking": {
        "severity": "block",
        "description": "Hacking/cracking instructions",
        "keywords": [
            "hack facebook", "hack instagram", "hack wa", "hack whatsapp",
            "hack wifi", "hack pulsa", "hack token listrik", "hack dana",
            "hack mobile legends", "hack ml", "hack free fire", "hack ff",
            "phishing", "carding", "carder", "bukti transfer palsu",
            "fake transfer", "fake payment", "stripe chargeback",
        ],
    },
    "counterfeit": {
        "severity": "block",
        "description": "Counterfeit/fake branded goods",
        "keywords": [
            "nike kw super", "adidas kw super", "taylor made kw", "iphone kw",
            "iphone palsu", "iphone super copy", "tas branded palsu",
            "jam rolex kw", "tissot kw", "hublot kw",
        ],
    },
    "misleading_financial": {
        "severity": "block",
        "description": "Misleading financial/health guarantees (AdSense policy)",
        "keywords": [
            "pasti untung", "pasti kaya", "100% closing", "100% profit",
            "100% sukses", "dijamin roi", "tanpa rugi", "tanpa risiko 100%",
            "dijamin profit", "garansi 100% profit", "pasti berhasil",
            "anti rugi", "anti bangkrut", "no loss", "guaranteed profit",
            "guaranteed roi", "100% guaranteed", "risk free profit",
            "income guarantee", "100% success rate",
        ],
    },
    "misleading_health": {
        "severity": "block",
        "description": "Unverified medical/health claims",
        "keywords": [
            "obat kuat", "obat kuat oles", "obat kuat minum", "kuat tahan lama",
            "permanen dalam 1 hari", "sembuh total", "diabetes sembuh total",
            "kanker sembuh", "aids sembuh", "tumor sembuh tanpa operasi",
        ],
    },
    "hate_speech": {
        "severity": "block",
        "description": "Hate speech / discrimination",
        "keywords": [
            "bunuh semua", "bantai semua", "ras inferior", "ras superior",
            "agama tertentu harus", "kelompok etnis harus", "suku tertentu harus",
        ],
    },
    "shocking": {
        "severity": "block",
        "description": "Shocking content for shock value",
        "keywords": [
            "kecelakaan mengerikan", "mayat hidup", "zombie", "kanibal",
            "pembunuhan sadis", "foto mayat", "video mayat",
        ],
    },
    "clickbait": {
        "severity": "warn",
        "description": "Clickbait / misleading (flag for review, usually allow)",
        "keywords": [
            "anda tidak akan percaya", "dokter ini tercengang", "rahasia yang disembunyikan",
            "mereka tidak ingin anda tahu", "100% akan membuat anda kaya",
            "1 trik yang membuat anda",
        ],
    },
    "beriklan_specific": {
        "severity": "warn",
        "description": "Internal: claims that conflict with brand voice (beriklan.co.id policy)",
        "keywords": [
            # Our own internal rule: never claim specific fake metrics
            "rating 4.9", "rating 4.8", "rating 5.0",
            "50+ klien aktif", "100+ klien", "100+ bisnis",
            "roi 10x", "roi 20x", "roi 50x",
            "closing 100%", "omset 100jt dalam",
        ],
    },
}


def check_policy_violation(text: str) -> dict:
    """Check text against AdSense prohibited content blocklist.

    Returns:
        {
            "violation": bool,
            "category": str | None,
            "keyword": str | None,
            "severity": "block" | "warn" | None,
            "description": str | None,
            "matches": list[dict],  # all matches, not just first
        }
    """
    if not text:
        return {"violation": False, "category": None, "keyword": None, "severity": None, "description": None, "matches": []}
    text_lower = text.lower()
    matches = []
    for category, rule in POLICY_BLOCKLIST.items():
        for kw in rule["keywords"]:
            # word-boundary check to avoid false positives
            # e.g. "sex" should not match "seksual" (but we WANT it to match since
            # "seksual" itself is adult-content adjacent). So use simple substring
            # but be careful with very short keywords.
            if len(kw) <= 4:
                # short keyword: must be word-bounded
                import re
                pattern = r"\b" + re.escape(kw) + r"\b"
                if re.search(pattern, text_lower):
                    matches.append({
                        "category": category,
                        "keyword": kw,
                        "severity": rule["severity"],
                        "description": rule["description"],
                    })
            else:
                # long keyword: substring is fine
                if kw in text_lower:
                    matches.append({
                        "category": category,
                        "keyword": kw,
                        "severity": rule["severity"],
                        "description": rule["description"],
                    })
    if not matches:
        return {"violation": False, "category": None, "keyword": None, "severity": None, "description": None, "matches": []}
    # any match → violation (block or warn). severity tells caller how to act.
    has_block = any(m["severity"] == "block" for m in matches)
    # Pick the highest-severity match for the top-level fields
    primary = next((m for m in matches if m["severity"] == "block"), matches[0])
    return {
        "violation": True,  # any match is a violation; severity tells caller
        "category": primary["category"],
        "keyword": primary["keyword"],
        "severity": primary["severity"],
        "description": primary["description"],
        "matches": matches,
    }


# Self-test when run directly
if __name__ == "__main__":
    test_cases = [
        # Negative (should pass)
        ("Cara iklan Facebook untuk UMKM Bandung", False),
        ("Strategi Meta Ads untuk bisnis skincare lokal", False),
        ("Tips optimasi Google Ads budget Rp 5 juta", False),
        ("Cara membuat landing page yang convert", False),
        ("Pelatihan digital marketing untuk pemula", False),
        ("SEO lokal untuk restoran di Medan", False),
        # Borderline (warn but allow) - beriklan specific
        ("Rating 4.9 dari 5 klien", True),  # warn
        # Positive (should block)
        ("Cara hack Facebook gratis tanpa software", True),
        ("Download software crack premium full version", True),
        ("Cara membuat bom rakitan dari bahan rumah", True),
        ("Jual nike kw super murah", True),
        ("Pasti untung 100% tanpa risiko", True),
        ("Hack mobile legends unlimited diamond", True),
        ("Sabu-sabu harga murah", True),
    ]
    passed = 0
    failed = 0
    for text, should_violate in test_cases:
        result = check_policy_violation(text)
        actual = result["violation"]
        ok = actual == should_violate
        status = "OK" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
        if not ok or result["violation"]:
            print(f"  [{status}] '{text[:60]}' violation={actual} expected={should_violate}")
            if result["violation"]:
                print(f"    → category={result['category']} keyword={result['keyword']} severity={result['severity']}")
    print(f"\nResults: {passed} passed, {failed} failed (out of {len(test_cases)})")
