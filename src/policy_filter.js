// AdSense Prohibited Content Pre-Publish Filter
// Mirrors scripts/policy_filter.py — KEEP IN SYNC

// Word-boundary check for short keywords (avoids false positives)
function wordBoundary(textLower, kw) {
  const escaped = kw.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const re = new RegExp("\\b" + escaped + "\\b");
  return re.test(textLower);
}

export function checkPolicyViolation(text) {
  if (!text) {
    return { violation: false, category: null, keyword: null, severity: null, description: null, matches: [] };
  }
  const textLower = text.toLowerCase();
  const matches = [];
  for (const [category, rule] of Object.entries(POLICY_BLOCKLIST)) {
    for (const kw of rule.keywords) {
      let hit = false;
      if (kw.length <= 4) {
        hit = wordBoundary(textLower, kw);
      } else {
        hit = textLower.includes(kw);
      }
      if (hit) {
        matches.push({ category, keyword: kw, severity: rule.severity, description: rule.description });
      }
    }
  }
  if (matches.length === 0) {
    return { violation: false, category: null, keyword: null, severity: null, description: null, matches: [] };
  }
  const primary = matches.find(m => m.severity === "block") || matches[0];
  return {
    violation: true,
    category: primary.category,
    keyword: primary.keyword,
    severity: primary.severity,
    description: primary.description,
    matches,
  };
}

export const POLICY_BLOCKLIST = {
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
            "rating 4.9", "rating 4.8", "rating 5.0",
            "50+ klien aktif", "100+ klien", "100+ bisnis",
            "roi 10x", "roi 20x", "roi 50x",
            "closing 100%", "omset 100jt dalam",
        ],
    },
};
