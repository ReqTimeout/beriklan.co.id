#!/usr/bin/env node
// §T4 / Fase 6.9 — Quality gate artikel (INDUSTRY-EXPANSION.md §7 + plan §T4 langkah 5).
//
// LOKAL: membaca D1 lewat `wrangler d1 execute --remote` (hanya SELECT), tidak
// menyentuh worker, dist/, atau file tampilan. Write terjadi HANYA kalau `--apply`
// dipakai bersama `--source` (mode report = default, sengaja).
//
// Kenapa default-nya report-only — diukur 30 Sep terhadap 8 draft terbaru di D1:
//   panjang konten 454–727 kata, rata-rata pool `status='draft'` = 4.359 karakter
//   (~700 kata). Ambang §7 co.id = 1.200 kata → 8/8 GAGAL. Kalau `--apply`
//   dijalankan pada pool hari ini, ±397 draft berubah jadi 'draft-gated' dan
//   pipeline publish harian berhenti = mengubah sistem produksi berjalan tanpa
//   izin user (dilarang AGENTS.md SOP #4). Jadi: gate dibangun + diukur dulu,
//   keputusan ambang/naik-panjang ada di tangan user.
//
// Checks (sesuai §7, dengan 2 deviasi yang dibuktikan di bawah):
//   1. kata >= MIN_WORDS (coid 1200 / my 900)
//   2. blok jawaban 40–60 kata di 100 kata pertama (di generator hari ini
//      heading-nya "QUICK ANSWER" — 49 kata, LOLOS; dikenali juga "jawaban")
//   3. FAQ >= 3 Q&A; pola `class="growth-faq"` DIKENAL TAPI draft generator memakai
//      heading pertanyaan di bawah <h2>FAQ …</h2> — keduanya diterima (§7.3)
//   4. service terisi + slug nyambung ke keyword (butuh baris keyword_queue)
//   5. internal link >= 3 (kecuali wa.me/mailto/tel/eksternal)
//   6. kata terlarang COPY-BIBLE
//   7. minimal 1 angka/statistik
//   8. duplikat: jaccard 3-gram >= 0.85 (plan) + penemuan sendiri: judul
//      permutation (jasa-iklan-facebook-di-makassar-terbaik vs -terbaik-di-makassar)
//      TIDAK terdeteksi jaccard body (max 0.084) → ditambah jaccard token judul >= 0.6
//   9. Schema Article: TIDAK dinilai dari draft — `application/ld+json` = 0 di semua
//      draft karena schema disuntik saat render (worker/Layout). Dilaporkan sebagai
//      info, bukan failure.
//
// Pemakaian:
//   node scripts/quality-gate.mjs                                  # pool 40 draft terbaru, report-only
//   node scripts/quality-gate.mjs --source industry-wave1          # hanya draft wave-1
//   node scripts/quality-gate.mjs --source industry-wave1 --apply  # tulis status='draft-gated'
//   node scripts/quality-gate.mjs --batch 60 --out /tmp/gate.json

import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url))); // …/web
const MIN_WORDS = { coid: 1200, my: 900 };               // §7.1
const ANSWER_MIN = 40, ANSWER_MAX = 60;                   // §7.2
const FAQ_MIN = 3;                                        // §7.3
const LINKS_MIN = 3;                                      // §7.5
const JACCARD_BODY = 0.85;                                // plan §T4.5
// JACCARD_TITLE diturunkan dari DISTRIBUSI, bukan tebak-tebakan. Audit 40 draft
// terbaru (30 Sep): 428 pasangan di atas 0.6, tapi hanya 34 pasangan di atas 0.8 —
// dan yang 1.00 adalah judul yang SAMA persis, hanya urutan kata dipertukarkan
// ("Jasa Iklan Facebook Di Makassar Berpengalaman" vs "…Berpengalaman Di Makassar").
// 0.8 = garis "ini artikel kembar", 0.6 = hanya "satu topik" (terlalu longgar).
const JACCARD_TITLE = Number(process.env.GATE_DUP_TITLE || 0.8);
const BANNED = [ // §7.6 / COPY-BIBLE §4.2
  /\bbikin\b/i, /\bgak\b/i, /\bnggak\b/i, /\bhandle iklan\b/i,
  /\bpasti\b/i, /garansi\s*100\s*%/i, /tanpa\s*risiko/i,
  /50\+?\s*klien/i, /rating\s*4\.8/i, /ROAS\s*4\.2x/i,
];

function arg(name, def = null) {
  const i = process.argv.indexOf(`--${name}`);
  if (i === -1) return def;
  const next = process.argv[i + 1];
  return !next || next.startsWith("--") ? true : next;
}
const DOMAIN = String(arg("domain", "coid"));
const SOURCE = arg("source", null);
const BATCH = Number(arg("batch", 40));
const APPLY = Boolean(arg("apply", false));
const OUT = String(arg("out", path.join(ROOT, "src", "data", `gate-report-${SOURCE || "pool"}.json`)));
const MINW = Number(arg("min-words", MIN_WORDS[DOMAIN] || MIN_WORDS.coid));
const DUP_TITLE = Number(arg("dup-title", JACCARD_TITLE));

function d1(sql) {
  const raw = execFileSync("npx", ["wrangler", "d1", "execute", "beriklan-seo", "--remote", "--json", "--command", sql],
    { cwd: ROOT, encoding: "utf8", maxBuffer: 512 * 1024 * 1024 });
  const start = raw.indexOf("[");
  if (start === -1) throw new Error(`wrangler output tak dikenali: ${raw.slice(0, 200)}`);
  const parsed = JSON.parse(raw.slice(start));
  const first = Array.isArray(parsed) ? parsed[0] : parsed;
  if (first?.error) throw new Error(`D1 error: ${first.error.text || JSON.stringify(first.error).slice(0, 200)}`);
  return first.results || [];
}

const strip = (h) => (h || "").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
const ngram = (toks, n = 3) => { const s = new Set(); for (let i = 0; i + n <= toks.length; i++) s.add(toks.slice(i, i + n).join(" ")); return s; };
const jaccard = (a, b) => { const u = new Set([...a, ...b]); return u.size ? [...a].filter((x) => b.has(x)).length / u.size : 0; };
const toks = (s) => s.toLowerCase().replace(/[^a-z0-9\s]/g, " ").split(/\s+/).filter(Boolean);

function blocks(html) {
  const out = [];
  const re = /<(h[1-4])([^>]*)>(.*?)<\/\1>|<p([^>]*)>(.*?)<\/p>/gs;
  let m;
  while ((m = re.exec(html))) {
    if (m[1]) out.push({ type: m[1].toLowerCase(), attrs: m[2] || "", text: strip(m[3]) });
    else out.push({ type: "p", attrs: m[4] || "", text: strip(m[5]) });
  }
  return out;
}

function checkOne(d) {
  const html = d.content || "";
  const text = strip(html);
  const words = text.split(/\s+/).filter(Boolean).length;
  const bs = blocks(html);
  const fails = [], notes = [];

  if (words < MINW) fails.push(`word_count:${words}<${MINW}`);

  // §7.2 blok jawaban 40–60 kata dalam 100 kata pertama
  let answer = null;
  for (let i = 0; i < Math.min(bs.length, 6); i++) {
    const b = bs[i];
    if (b.type !== "p") continue;
    const wc = b.text.split(/\s+/).length;
    const before = bs.slice(0, i).reduce((n, x) => n + x.text.split(/\s+/).length, 0);
    if (wc >= ANSWER_MIN && wc <= ANSWER_MAX && before <= 100) {
      answer = { i, wc, heading: bs.slice(0, i).reverse().find((x) => /^h[1-4]$/.test(x.type))?.text || "" };
      break;
    }
  }
  if (!answer) fails.push("answer_block:tidak_ada_40-60_kata_di_100_kata_pertama");
  else if (!/quick\s*answer|jawaban|ringkas|singkat/i.test(answer.heading)) notes.push(`answer_block_heading:"${answer.heading}"`);

  // §7.3 FAQ >= 3 (heading pertanyaan ATAU class growth-faq)
  const faqIdx = bs.findIndex((b) => /^h[23]$/.test(b.type) && /faq|pertanyaan|sering\s*ditanya/i.test(b.text));
  const growthFaq = (html.match(/class="[^"]*growth-faq[^"]*"/g) || []).length;
  const qHeads = bs.filter((b) => /^h[34]$/.test(b.type) && b.text.endsWith("?"));
  const faqCount = Math.max(qHeads.length, growthFaq);
  if (faqCount < FAQ_MIN) fails.push(`faq:${faqCount}<${FAQ_MIN}`);
  if (faqIdx === -1 && growthFaq === 0 && qHeads.length === 0) fails.push("faq:block_tidak_ditemukan");

  // §7.4 service + slug↔keyword
  if (!d.service) fails.push("service:kosong");
  const kw = d.keyword ? String(d.keyword).toLowerCase() : "";
  if (kw) {
    const kt = toks(kw), st = new Set(toks((d.slug || "").replace(/-/g, " ")));
    const overlap = kt.filter((t) => st.has(t)).length / Math.max(1, kt.length);
    if (overlap < 0.5) fails.push(`slug_keyword:cocok${Math.round(overlap * 100)}%<50%`);
  } else notes.push("slug_keyword:tidak_diperiksa (tidak ada baris keyword_queue)");

  // §7.5 internal link >= 3
  const hrefs = [...html.matchAll(/<a[^>]+href="([^"]+)"/g)].map((m) => m[1]);
  const internal = hrefs.filter((h) => !/^https?:\/\/(wa\.me|api\.whatsapp|mailto)/i.test(h) && !/^tel:/i.test(h) &&
    (/^https?:\/\/(www\.)?beriklan\./i.test(h) || h.startsWith("/")));
  if (internal.length < LINKS_MIN) fails.push(`internal_links:${internal.length}<${LINKS_MIN}`);

  // §7.6 kata terlarang
  const hits = BANNED.filter((rx) => rx.test(html)).map((rx) => rx.source);
  if (hits.length) fails.push(`banned_words:${hits.join(",")}`);

  // plan §T4.5: ada angka
  if (!/\d\s*[%x]|Rp\s*\d|\b\d{2,}\b/.test(html)) fails.push("numbers:tidak_ada");

  // §7.7 schema — render-time, bukan bagian draft
  if (!/application\/ld\+json/.test(html)) notes.push("schema:article_disuntik_saat_render(bukan_di_draft)");

  return { slug: d.slug, title: d.title, service: d.service || null, city: d.city || null,
    words, answer_block: answer ? `${answer.wc} kata @blok${answer.i}` : null, faq_count: faqCount,
    internal_links: internal.length, keyword: kw || null, source_row: d.source || null,
    status: d.status || null, priority_score: d.priority_score ?? null, fails, notes };
}

function main() {
  let rows = [];
  let waveMode = false;
  if (SOURCE) {
    const safe = String(SOURCE).replace(/'/g, "");
    const map = d1(`SELECT keyword, article_slug, service, city, priority_score FROM keyword_queue WHERE source='${safe}' AND article_slug IS NOT NULL AND article_slug<>''`);
    console.log(`draft wave (${SOURCE}) dari keyword_queue = ${map.length}`);
    if (!map.length) {
      console.log("  belum ada draft untuk source ini (refill buffer → generate → draft). Pindah ke audit pool.");
    } else {
      const slugIn = map.map((m) => `'${String(m.article_slug).replace(/'/g, "")}'`).join(",");
      const drafts = d1(`SELECT slug, title, content, service, city, source, status FROM generated_drafts WHERE slug IN (${slugIn})`);
      const byKw = new Map(map.map((m) => [m.article_slug, m]));
      // Merge HATI-HATI: baris lama keyword_queue sering `service=''` (diukur: 1.606
      // baris source='suggest+combo' service-nya kosong). Spread biasa akan MENIMPA
      // service/city milik draft dengan string kosong → §7.4 gagal palsu.
      rows = drafts.map((d) => {
        const k = byKw.get(d.slug) || {};
        const pick = (a, b) => (a && String(a).trim() ? a : (b && String(b).trim() ? b : a));
        return { ...d, ...k, service: pick(d.service, k.service), city: pick(d.city, k.city) };
      });
      waveMode = true;
    }
  }
  if (!rows.length) {
    rows = d1(`SELECT slug, title, content, service, city, source, status FROM generated_drafts WHERE status='draft' ORDER BY created_at DESC LIMIT ${BATCH}`);
    console.log(`mode AUDIT POOL: ${rows.length} draft terbaru (status='draft')`);
  } else console.log(`mode WAVE: ${rows.length} draft`);

  const results = rows.map(checkOne);   // indeks = indeks rows (dipakai untuk pass duplikat)

  // ── Duplikat antar draft dalam batch ─────────────────────────────
  //   body: jaccard 3-gram >= 0.85 (plan §T4 langkah 5). Diukur 30 Sep pada 8 draft
  //   terbaru max = 0.084 → badan artikel TIDAK duplikat walau judulnya permuted.
  //   judul: jaccard token >= 0.8 (tambahan berbasis bukti — pola nyata generator:
  //   `…-di-makassar-terbaik` vs `…-terbaik-di-makassar`; override: --dup-title / GATE_DUP_TITLE)
  const bodyG = rows.map((r) => ngram(toks(strip(r.content || "")), 3));
  const titleG = rows.map((r) => new Set(toks(r.title || "")));
  for (let i = 0; i < rows.length; i++) {
    for (let j = i + 1; j < rows.length; j++) {
      const bj = jaccard(bodyG[i], bodyG[j]);
      if (bj >= JACCARD_BODY) { results[i].fails.push(`dup_body:${bj.toFixed(2)}>=${JACCARD_BODY}↔${rows[j].slug}`); results[j].fails.push(`dup_body:${bj.toFixed(2)}>=${JACCARD_BODY}↔${rows[i].slug}`); }
      const tj = jaccard(titleG[i], titleG[j]);
      if (tj >= DUP_TITLE) { results[i].fails.push(`dup_title:${tj.toFixed(2)}>=${DUP_TITLE}↔${rows[j].slug}`); results[j].fails.push(`dup_title:${tj.toFixed(2)}>=${DUP_TITLE}↔${rows[i].slug}`); }
    }
  }

  const uniq = [];
  for (const r of results) if (!uniq.some((u) => u.slug === r.slug)) uniq.push(r);

  const passed = uniq.filter((r) => !r.fails.length);
  const failed = uniq.filter((r) => r.fails.length);
  const reasonAgg = {};
  for (const r of failed) for (const f of r.fails) { const k = f.split(":")[0]; reasonAgg[k] = (reasonAgg[k] || 0) + 1; }
  const wordCounts = uniq.map((r) => r.words).sort((a, b) => a - b);
  const report = {
    generated_at: new Date().toISOString(), domain: DOMAIN, mode: waveMode ? "wave" : "pool-audit",
    source: SOURCE || null, min_words: MINW, apply: APPLY,
    checked: uniq.length, passed: passed.length, failed: failed.length,
    pass_rate: +(passed.length / Math.max(1, uniq.length)).toFixed(4),
    reason_distribution: reasonAgg,
    thresholds: { min_words: MINW, answer_block: [ANSWER_MIN, ANSWER_MAX], faq_min: FAQ_MIN,
      links_min: LINKS_MIN, jaccard_body: JACCARD_BODY, jaccard_title: DUP_TITLE },
    words: { min: wordCounts[0] ?? null, p50: wordCounts[Math.floor(wordCounts.length / 2)] ?? null, max: wordCounts.at(-1) ?? null },
    slugs_passed: passed.map((r) => r.slug), items: uniq,
  };
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, JSON.stringify(report, null, 1));
  console.log(`\nchecked=${report.checked} passed=${report.passed} failed=${report.failed} pass_rate=${(report.pass_rate * 100).toFixed(1)}%`);
  console.log(`alasan gagal: ${JSON.stringify(reasonAgg)}`);
  console.log(`panjang kata: min=${report.words.min} p50=${report.words.p50} max=${report.words.max} (ambang ${MINW})`);
  console.log(`LAPORAN → ${OUT}`);

  if (APPLY) {
    if (!SOURCE) { console.log("\n--apply DITOLAK: tanpa --source gate akan menggating seluruh pool publish (menghentikan pipeline). Jalankan report-only."); return; }
    console.log(`\n--apply: menulis status='draft-gated' untuk ${failed.length} draft (${SOURCE})`);
    for (const r of failed) {
      d1(`UPDATE generated_drafts SET status='draft-gated' WHERE slug='${r.slug.replace(/'/g, "")}' AND status='draft'`);
      console.log(`  gated ${r.slug} → ${r.fails.join(" | ")}`.slice(0, 180));
    }
  } else console.log("\n(report-only — tidak ada baris yang diubah. Pakai --apply bersama --source untuk menulis status='draft-gated'.)");
}

main();
