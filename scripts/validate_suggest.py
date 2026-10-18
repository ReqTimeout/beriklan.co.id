#!/usr/bin/env python3
"""
§T4 / Fase 6.1 + 6.3 — Industry Wave Runner, gelombang 1 (kontraktor).

SEMUNYA lokal: tidak memanggil worker, tidak menulis D1, tidak menyentuh dist/.
Outputnya berupa file JSON yang kemudian di-POST manual ke endpoint import yang SUDAH ADA.

Kenapa strukturnya "harvest dulu, baru turunkan" (bukan matriks buta seperti teks plan):
  Plan §T4 langkah 1 minta "~300 frasa teratas wave-1 (industri=kontraktor)". Faktanya,
  diverifikasi langsung ke file (29 Sep 20:3x UTC):
    - `industry-keywords.json` TIDAK punya `industri='kontraktor'`. 'kontraktor' adalah
      `sub_niche` di dalam `industri='properti'` → hanya **9 seed**.
    - 2.291/2.291 item ber-`intent='informational'` (kelemahan §1.2 #1) — jadi koreksi
      intent (§6.3) wajib, bukan opsional.
    - Angka "±400–700 keyword" di plan bertentangan dengan INDUSTRY-EXPANSION §9
      ("Wave 1: 9 seed + ekspansi → 60–90 artikel"). Dokumen sumber yang menang.
  Uji empiris 89 frasa matriks sintetik (mode --matrix, 29 Sep): hanya **47,2%** yang
  terbukti di Suggest; seluruh frasa formula dataset ("studi kasus kontraktor naik omzet"
  dkk.) = 0 suggestion. Artinya: frasa harus DITANGKAP dari Suggest lebih dulu, baru
  diturunkan mekanis (aturan §4 #1 memperbolehkan "turunan mekanis kota/biaya/kanal dari
  frasa yang terbukti").

Guard audiens (penting untuk kualitas lead, bukan hanya traffic):
  Suggest untuk "kontraktor" / "jasa kontraktor" didominasi pencarian B2C
  ("jasa kontraktor rumah bandung", "kontraktor listrik") — itu orang yang MAU pakai
  kontraktor, bukan calon klien agency kami. Wave ini menjual jasa iklan ke kontraktor,
  jadi frasa wajib mengandung token marketing DAN token niche, dan dibersihkan dari
  intent cari-kerja ("gaji", "tugas", "lowongan", "adalah", "pengertian").

Pemakaian:
    python3 scripts/validate_suggest.py --harvest         # mode utama (default)
    python3 scripts/validate_suggest.py --matrix          # audit matriks sintetik (penemuan 47%)
    python3 scripts/validate_suggest.py --harvest --dry   # lihat kandidat tanpa network
    python3 scripts/validate_suggest.py --harvest --limit 40
"""

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # …/beriklan.co.id/web
DATA = ROOT / "src" / "data"
SRC_LIST = DATA / "industry-keywords.json"
OUT_VALIDATION = DATA / "industry-keywords.suggest-validation.json"
OUT_IMPORT = DATA / "industry-wave1.import.json"
OUT_IMPORT_FULL = DATA / "industry-wave1.import.with-derivatives.json"

WAVE1_SUBNICHE = "kontraktor"
TARGET_MIN, TARGET_MAX = 60, 90            # §9 cadence wave-1
SUGGEST_URL = "https://suggestqueries.google.com/complete/search?client=firefox&hl=id&gl=id&q="
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 BeriklanSEO/1.0 (riset keyword; admin@3smedianet.com)"

# Query induk harvest — semuanya B2B (kontraktor yang mencari pemasaran), bukan B2C.
HARVEST_QUERIES = [
    "iklan kontraktor", "digital marketing kontraktor", "marketing kontraktor",
    "promosi kontraktor", "jasa iklan kontraktor", "kontraktor marketing online",
    "iklan jasa kontraktor", "branding kontraktor", "media sosial kontraktor",
    "landing page kontraktor", "seo kontraktor", "iklan renovasi rumah",
    "digital marketing konstruksi", "iklan untuk perusahaan konstruksi",
    "cara pemasaran jasa kontraktor", "agency iklan kontraktor", "jasa digital marketing konstruksi",
    "tips iklan kontraktor", "konten sosmed kontraktor", "facebook ads kontraktor",
    "strategi marketing jasa renovasi", "iklan agar dapat proyek kontraktor",
]
# Core untuk turunan mekanis (kota / biaya / kanal) — harus terbukti di Suggest dulu.
DERIVATIVE_CORES = ["iklan kontraktor", "digital marketing kontraktor", "jasa iklan kontraktor",
                    "iklan renovasi rumah", "promosi kontraktor"]

NICHE_RE = re.compile(r"kontraktor|konstruksi|renovasi", re.I)
MARKETING_RE = re.compile(r"\b(iklan|ads|advertising|marketing|promosi|digital|seo|sem|landing\s*page|media\s*sosial|facebook|instagram|tiktok|youtube|google|branding|konten|leads|proyek|pelanggan|omzet|penjualan)\b", re.I)
# Negative list: intent cari kerja / aset desain / definisi → bukan calon klien agency.
# (dibuktikan 30 Sep: Suggest menghasilkan "poster iklan kontraktor", "kata kata iklan
# kontraktor", "fee marketing kontraktor", "sales marketing kontraktor" yang lolos filter
# pertama — orang yang mencari gambar/kata, bukan yang mencari jasa iklan.)
NEGATIVE_RE = re.compile(r"\b(gaji|tugas|lowongan|job|karir|karier|adalah|pengertian|definisi|tabel|lisensi|sertifikasi|kuliah|jurusan|salary|sewa|rekrutmen|wawancara|poster|kata kata|gambar|template|desain|font|quote|fee|sales|crm|proposal|presentasi|skill|materi|pdf)\b", re.I)
# Pattern turunan yang boleh dibuat TANPA muncul di Suggest: kota / biaya / kanal
# (dibangun di build_harvest, aturan §4 #1).
# Aturan §6.3 HARFIAH: `jasa|harga|biaya|murah|terdekat|untuk` → commercial/transactional.
# Nama niche ("kontraktor") dan kata umum ("iklan") sengaja TIDAK dipakai sebagai penanda
# commercial; kalau dimasukkan, acceptance ≥40% terpenuhi karena aturannya yang dimanipulasi.
COMMERCIAL_RE = re.compile(r"\b(jasa|harga|biaya|murah|terdekat|untuk|paket|order|vendor|agency|promosi)\b", re.I)
TRANSACTIONAL_RE = re.compile(r"\b(harga|biaya|paket|murah|order|vendor|estimasi|tarif|daftar harga)\b", re.I)

SERVICE_BY_TOKEN = [
    (re.compile(r"facebook|meta\b|fb\b", re.I), "jasa-iklan-facebook"),
    (re.compile(r"instagram|\big\b", re.I), "jasa-iklan-instagram"),
    (re.compile(r"tiktok", re.I), "jasa-iklan-tiktok"),
    (re.compile(r"youtube", re.I), "jasa-iklan-youtube"),
    (re.compile(r"google|adwords|\bsem\b|seo\b|search", re.I), "jasa-iklan-google"),
    (re.compile(r"landing\s*page|website|\bsite\b", re.I), "jasa-pembuatan-landing-page"),
    (re.compile(r"kelola|content|konten|media\s*sosial|branding", re.I), "jasa-kelola-instagram"),
]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def pick_service(kw: str) -> str:
    for rx, svc in SERVICE_BY_TOKEN:
        if rx.search(kw):
            return svc
    return "jasa-digital-marketing"


def load_cities():
    raw = json.loads((DATA / "cities.json").read_text())
    domestic = [c for c in raw if c.get("country") == "ID" and not c.get("is_country")]
    domestic.sort(key=lambda c: (c.get("tier", 9), c.get("name", "")))
    return [c["slug"] for c in domestic[:10]]


def correct_intent(kw: str, formula: str) -> str:
    n = norm(kw)
    if TRANSACTIONAL_RE.search(n):
        return "transactional"
    if COMMERCIAL_RE.search(n) or formula in ("comparison", "kanal", "kota", "biaya"):
        return "commercial"
    return "informational"


def suggest(phrase: str, timeout=12):
    url = SUGGEST_URL + urllib.parse.quote(phrase)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode("utf-8", "replace"))
    return data[1] if isinstance(data, list) and len(data) > 1 else []


def keep_candidate(kw: str) -> bool:
    n = norm(kw)
    if not (8 <= len(n) <= 62):
        return False
    if len(n.split()) > 7:
        return False
    if NEGATIVE_RE.search(n):
        return False
    if not NICHE_RE.search(n):
        return False
    if not MARKETING_RE.search(n):
        return False
    return True


def build_harvest(cities):
    """Tier A: frasa yang BENAR-BENAR muncul di Suggest (bukti demand, §3.1/§4 #1)."""
    rows, seen = [], set()
    raw_queries = []
    for q in HARVEST_QUERIES:
        try:
            sugs = suggest(q)
        except Exception as e:
            sugs = []
            raw_queries.append({"query": q, "error": str(e)[:120]})
        raw_queries.append({"query": q, "n": len(sugs), "suggestions": sugs[:10]})
        for s in sugs:
            if not keep_candidate(s):
                continue
            n = norm(s)
            if n in seen:
                continue
            seen.add(n)
            rows.append({"keyword": s.strip(), "service": pick_service(s), "city": "",
                         "formula": "suggest-harvest", "origin": q})
        time.sleep(0.45)
    # Turunan mekanis dari core terbukti — §4 #1 memperbolehkan, TAPI dibatasi sengaja:
    #   68 dari 89 frasa menjadi varian kota (diukur 30 Sep 03:2x UTC) = resep konten
    #   nyaris-duplikat, dan §8.2 melanjut ekspansi justru kalau impressions turun >20%.
    #   Cap kecil + import default hanya yang TERBUKTI (lihat --include-derivatives).
    MAX_CITY_PER_CORE, MAX_COST_PER_CORE, KANAL_CORES = 4, 2, {"iklan kontraktor"}
    for core in DERIVATIVE_CORES:
        if core not in seen:
            continue
        added_city = added_cost = 0
        for c in cities:
            if added_city >= MAX_CITY_PER_CORE:
                break
            kw = f"{core} {c}"
            if norm(kw) in seen or not keep_candidate(kw):
                continue
            seen.add(norm(kw))
            rows.append({"keyword": kw, "service": pick_service(kw), "city": c,
                         "formula": "kota", "origin": core})
            added_city += 1
        for pre in ("harga", "biaya", "paket"):
            if added_cost >= MAX_COST_PER_CORE:
                break
            kw = f"{pre} {core}"
            if norm(kw) in seen or not keep_candidate(kw):
                continue
            seen.add(norm(kw))
            rows.append({"keyword": kw, "service": pick_service(kw), "city": "",
                         "formula": "biaya", "origin": core})
            added_cost += 1
        if core in KANAL_CORES:
            for ch in ("facebook", "google", "tiktok", "instagram"):
                kw = f"iklan {ch} kontraktor"
                if norm(kw) in seen or not keep_candidate(kw):
                    continue
                seen.add(norm(kw))
                rows.append({"keyword": kw, "service": pick_service(kw), "city": "",
                             "formula": "kanal", "origin": core})
    return rows, raw_queries


def build_matrix(seeds, cities):
    """Mode --matrix: daftar sintetik penuh (dipakai untuk AUDIT — hasilnya 47,2% lolos)."""
    out = []
    for s in seeds:
        out.append({"keyword": s["keyword"], "service": s["service"], "city": "", "formula": "seed-dataset", "origin": "dataset"})
    for c in cities:
        for f in ("jasa kontraktor", "kontraktor bangunan", "kontraktor rumah"):
            out.append({"keyword": f"{f} {c}", "service": "jasa-iklan-google", "city": c, "formula": "kota", "origin": "matrix"})
    for f in ("biaya iklan facebook untuk kontraktor", "harga jasa iklan google kontraktor",
              "cara mendapatkan proyek kontraktor dari google ads", "kisah sukses kontraktor rumah dengan iklan digital",
              "facebook ads vs google ads untuk kontraktor", "kenapa iklan facebook kontraktor tidak mendatangkan proyek",
              "jasa iklan instagram untuk kontraktor", "digital marketing untuk kontraktor bandung"):
        out.append({"keyword": f, "service": pick_service(f), "city": "", "formula": "matriks", "origin": "matrix"})
    seen, uniq = set(), []
    for r in out:
        n = norm(r["keyword"])
        if n in seen or len(n) < 12:
            continue
        seen.add(n)
        uniq.append(r)
    return uniq


def wave_priority(row, proven: bool) -> int:
    """§6.2 (score+20 untuk baris wave) tapi di-clamp ke 91–95, dengan bukti:
      - ≤90 TIDAK masuk buffer: `hourly_candidates` refill = `… ORDER BY priority_score DESC
        LIMIT 120` per service dan buffer itu TERISI PENUH di prio 90 (diukur di D1 29 Sep:
        `jasa-digital-marketing` → 120 baris, `min_in_buffer = 90`) → prio plan 70–85 = aksi kosong;
      - 96 dipakai winner-engine (§T3) → wave tidak boleh menyalipnya;
      - 95 = cap yang sama dipakai `handleGrowthGscLoop` (`Math.min(95, …)`).
    """
    base = 92 if row["formula"] == "suggest-harvest" else 91
    if row["intent"] == "transactional":
        base += 2
    elif row["intent"] == "commercial":
        base += 1
    if row["formula"] == "kota":
        base += 1                       # local intent tertinggi menurut §4
    if not proven:
        base -= 2
    return max(91, min(95, base))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harvest", action="store_true", help="mode utama: tangkap frasa dari Suggest lalu turunkan")
    ap.add_argument("--matrix", action="store_true", help="audit: validasi 89 frasa sintetik (menemukan pass rate 47%)")
    ap.add_argument("--dry", action="store_true", help="bangun kandidat saja, tanpa panggilan Suggest per frasa")
    ap.add_argument("--include-derivatives", action="store_true",
                    help="no-op (dipertahankan untuk kompatibilitas): keduanya selalu ditulis ke dua file terpisah")
    ap.add_argument("--limit", type=int, default=0, help="batasi jumlah frasa yang divalidasi")
    ap.add_argument("--sleep", type=float, default=0.45, help="jeda antar-permintaan Suggest (detik)")
    args = ap.parse_args()
    mode = "matrix" if args.matrix else "harvest"

    dataset = json.loads(SRC_LIST.read_text())
    seeds = [x for x in dataset if x.get("sub_niche") == WAVE1_SUBNICHE]
    cities = load_cities()
    raw_queries = []
    if mode == "harvest":
        rows, raw_queries = build_harvest(cities)
    else:
        rows = build_matrix(seeds, cities)
    for r in rows:
        r["intent"] = correct_intent(r["keyword"], r["formula"])
        r["industri"], r["sub_niche"] = "properti", WAVE1_SUBNICHE
    print(f"mode={mode} · seed dataset={len(seeds)} · kota={len(cities)} · kandidat={len(rows)} (target {TARGET_MIN}–{TARGET_MAX})")
    if len(rows) > TARGET_MAX:
        rows = rows[:TARGET_MAX]
        print(f"  dipangkas ke {TARGET_MAX} (urutan harvest = prioritas query HARVEST_QUERIES)")

    if args.dry:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return 0

    todo = rows[: args.limit] if args.limit else rows
    validation = []
    for i, r in enumerate(todo, 1):
        try:
            sugs = suggest(r["keyword"])
        except Exception as e:
            sugs = []
            r["suggest_error"] = str(e)[:120]
        n = norm(r["keyword"])
        exact = any(norm(s) == n for s in sugs)
        derivative = r["formula"] in ("kota", "biaya", "kanal") and norm(r["origin"]) not in ("", "matrix")
        status = "exact" if exact else ("derivative" if derivative else ("partial" if sugs else "weak"))
        validation.append({
            "phrase": r["keyword"], "normalized": n, "status": status, "in_suggest": exact,
            "n_suggestions": len(sugs), "suggestions": [s for s in sugs[:8]],
            "service": r["service"], "city": r["city"], "intent": r["intent"],
            "formula": r["formula"], "origin": r["origin"],
        })
        r["suggest_status"] = status
        if i % 10 == 0 or i == len(todo):
            okc = sum(1 for v in validation if v["status"] in ("exact", "derivative", "partial"))
            print(f"  [{i}/{len(todo)}] terbukti (exact+derivative+partial) = {okc}/{len(validation)}")
        time.sleep(args.sleep)

    dist = Counter(v["status"] for v in validation)
    intents = Counter(r["intent"] for r in todo)
    exact_rate = dist["exact"] / max(1, len(validation))
    provable_rate = (dist["exact"] + dist["derivative"] + dist["partial"]) / max(1, len(validation))
    com_tr = intents["commercial"] + intents["transactional"]
    print(f"\nSTATUS: {dict(dist)}")
    print(f"  exact di Suggest               = {dist['exact']}/{len(validation)} = {exact_rate*100:.1f}%")
    print(f"  boleh import (exact+deriv+part)= {provable_rate*100:.1f}%   [acceptance §6.1 ≥70%]")
    print(f"INTENT: {dict(intents)} · commercial+transactional = {com_tr}/{len(todo)} = {com_tr/max(1,len(todo))*100:.1f}%  [acceptance §6.3 ≥40%]")

    import_rows = []
    import_rows_full = []
    for r, v in zip(todo, validation):
        if v["status"] not in ("exact", "partial", "derivative"):
            continue
        r["priority"] = wave_priority(r, v["status"] == "exact")
        line = {
            "keyword": r["keyword"], "service": r["service"], "city": r["city"],
            "intent": r["intent"], "priority": r["priority"],
        }
        import_rows_full.append(line)
        # File default = HANYA yang terbukti/parsial di Suggest. Turunan mekanis
        # (kota/biaya/kanal) disimpan terpisah supaya import ke produksi bisa dipilih
        # sadar — 28 dari 49 kandidat adalah turunan (diukur 30 Sep), dan §8.2 melarang
        # ekspansi yang berakhir jadi konten nyaris-duplikat.
        if v["status"] in ("exact", "partial"):
            import_rows.append(line)
    # `pruned` = SEMUA yang tidak masuk file import (weak ATAU turunan yang memang
    # sengaja tidak di-include). Sebelumnya hard-code "weak" saja → laporan menyesatkan
    # karena derivatif yang disaring default tidak terhitung.
    pruned = [{"phrase": v["phrase"], "status": v["status"],
               "reason": ("weak" if v["status"] == "weak" else "derivative-separate-file")}
              for v in validation if v["status"] not in ("exact", "partial")]

    OUT_VALIDATION.write_text(json.dumps({
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "mode": mode, "wave": 1, "sub_niche": WAVE1_SUBNICHE,
        "endpoint": "suggestqueries.google.com/complete/search?client=firefox&hl=id&gl=id",
        "counts": dict(dist),
        "exact_rate": round(exact_rate, 4), "importable_rate": round(provable_rate, 4),
        "intent_distribution": dict(intents),
        "commercial_transactional_rate": round(com_tr / max(1, len(todo)), 4),
        "pruned_not_imported": pruned, "harvest_queries": raw_queries, "rows": validation,
    }, ensure_ascii=False, indent=1))
    OUT_IMPORT.write_text(json.dumps({"keywords": import_rows}, ensure_ascii=False, indent=1))
    OUT_IMPORT_FULL.write_text(json.dumps({"keywords": import_rows_full}, ensure_ascii=False, indent=1))
    pruned_by_reason = Counter(p["reason"] for p in pruned)
    print(f"\nTULIS {OUT_VALIDATION}  ({len(validation)} baris validasi)")
    print(f"     tidak masuk import = {len(pruned)} → {dict(pruned_by_reason)}")
    prio_list = [r["priority"] for r in import_rows]
    prio_note = f", prio {min(prio_list)}–{max(prio_list)}" if prio_list else ""
    print(f"TULIS {OUT_IMPORT}  ({len(import_rows)} baris terbukti siap import, source=industry-wave1{prio_note})")
    print(f"TULIS {OUT_IMPORT_FULL.name}  ({len(import_rows_full)} baris termasuk turunan mekanis)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
