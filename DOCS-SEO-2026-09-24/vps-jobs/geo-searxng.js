// §T5.4 GEO monitor KEYLESS (Fase 7.1–7.3 + 7.6) — "terindex & dikutip di AI/search
// tanpa API key". Probe hasil mesin pencarian lewat SearXNG lokal (container
// `searxng`, loopback 127.0.0.1:8888, formats: html+json) lalu catat:
//   • apakah domain kita muncul, di posisi berapa (rank)
//   • kompetitor yang muncul (untuk alert "disitasi tanpa kita")
//   • status 'unknown' bila engine tidak mengembalikan hasil sama sekali
//     (spec 7.3: jangan catat 'absent' untuk kegagalan engine)
// Menyimpan di shared.geo_mentions (tabel yang sama dengan geo-monitor.js).
//
// DEVIASI/FACT dari plan (dicatat di TASKTRACKER §T5):
//   1. `week` terisi TANGGAL (YYYY-MM-DD), bukan nomor minggu — ini sudah konvensi
//      geo-monitor.js yang ada (`const week = new Date().toISOString().slice(0,10)`),
//      jadi probe harian konsisten, tidak perlu ubah tabel.
//   2. provider = 'searxng:<domain>' (mis. 'searxng:beriklan.co.id'). WAJIB: constraint
//      unik tabel adalah (week, provider, prompt_idx) TANPA domain — kalau provider
//      hanya 'searxng', baris domain kedua menimpa baris domain pertama (bug nyata
//      ditemukan saat smoke test 2026-09-30: 6 insert → 3 row).
//   3. Kolom tambahan (day, engine, status, our_rank, results_total, domain) dibuat
//      idempoten di bawah — nullable, aman untuk job lama.
//
// Cara jalan:
//   node jobs/geo-searxng.js --max=120            (CLI sekali jalan, untuk test/cron)
//   runGeoSearxng({ maxQueries: 120 })             (di-import runner.js / server.js)
import { pool, sleep, jobStart, jobEnd, telegram } from './lib.js';

const SEARX = process.env.SEARXNG_URL || 'http://127.0.0.1:8888/search';
const DOMAINS = (process.env.GEO_DOMAINS || 'beriklan.co.id,beriklan.my')
  .split(',').map(s => s.trim().toLowerCase()).filter(Boolean);
const COMPETITORS = (process.env.COMPETITORS_CSV ||
  'ToffeeDev,Whello,Arfadia,Redcomm Asia,Lion & Lion,Fishermen,Niagahoster,Batfy')
  .split(',').map(s => s.trim().toLowerCase()).filter(Boolean);
const MAX_CAP = 200;                 // spec: ≤200 query/hari
const ENGINE_SET = process.env.GEO_ENGINES || 'google,duckduckgo,brave,startpage';
const UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36';

// 20 query komersial inti (§T5.4: "20 query komersial inti") — dasar stabil kalau
// sumber GSC/queue kosong, dan selalu ikut di-probe setiap hari.
const CORE_QUERIES = [
  'jasa iklan facebook bandung', 'jasa google ads indonesia', 'jasa iklan tiktok agency',
  'jasa digital marketing bandung', 'agency digital marketing terbaik indonesia',
  'jasa pembuatan landing page', 'jasa kelola instagram bisnis', 'jasa iklan youtube ads',
  'biaya jasa iklan facebook per bulan', 'agency facebook ads untuk umkm',
  'jasa iklan instagram bandung', 'performance marketing agency bandung',
  'jasa digital marketing untuk umkm', 'cara memilih agency iklan online',
  'jasa tiktok ads agency indonesia', 'jasa google ads bandung',
  'agency instagram management terbaik', 'jasa pembuatan website untuk iklan',
  'iklan facebook yang efektif untuk toko online', 'jasa manajemen iklan digital',
];

function resultUrl(r) {
  if (typeof r.url === 'string' && r.url) return r.url;
  const p = r.parsed_url;
  if (Array.isArray(p)) return 'https://' + String(p[1] || '') + String(p[2] || '');
  return '';
}

// Rank = posisi 1-based pada daftar hasil SearXNG (sudah di-rank agregasi engine).
function findRank(results, needle) {
  for (let i = 0; i < results.length; i++) {
    const u = resultUrl(results[i]).toLowerCase();
    if (u && u.indexOf(needle) >= 0) return i + 1;
  }
  return null;
}

async function searxQuery(q) {
  const url = `${SEARX}?format=json&language=id&engines=${encodeURIComponent(ENGINE_SET)}&safesearch=1&q=${encodeURIComponent(q)}`;
  const r = await fetch(url, { headers: { 'User-Agent': UA }, signal: AbortSignal.timeout(25000) });
  if (!r.ok) throw new Error(`searxng http=${r.status}`);
  const j = await r.json();
  return {
    results: Array.isArray(j.results) ? j.results : [],
    unresponsive: Array.isArray(j.unresponses) ? j.unresponses.map(u => u.engine) : [],
  };
}

// Sumber query: TOP GSC (impressions) + TOP commercial queue + 20 core queries.
async function collectQueries(nGsc, nQueue) {
  const out = [];
  const seen = new Set();
  const push = (q, src) => {
    const k = String(q || '').trim().toLowerCase();
    if (!k || k.length < 8 || k.length > 60 || seen.has(k)) return;
    seen.add(k); out.push({ q: k, src });
  };
  try {
    const { rows } = await pool.query(
      `SELECT keyword FROM coid.keyword_ranks
        WHERE date = (SELECT max(date) FROM coid.keyword_ranks)
          AND length(keyword) BETWEEN 8 AND 60
        GROUP BY keyword ORDER BY sum(impressions) DESC NULLS LAST LIMIT $1`, [nGsc]);
    rows.forEach(r => push(r.keyword, 'gsc'));
  } catch (e) { console.log('[geo-searxng] gsc source skip:', String(e).slice(0, 80)); }
  try {
    const { rows } = await pool.query(
      `SELECT keyword FROM coid.keyword_queue
        WHERE status = 'pending' AND intent IN ('commercial','transactional')
          AND length(keyword) BETWEEN 8 AND 60
        GROUP BY keyword ORDER BY max(priority_score) DESC NULLS LAST LIMIT $1`, [nQueue]);
    rows.forEach(r => push(r.keyword, 'queue'));
  } catch (e) { console.log('[geo-searxng] queue source skip:', String(e).slice(0, 80)); }
  CORE_QUERIES.forEach(q => push(q, 'core'));
  return out;
}

async function ensureSchema() {
  await pool.query(`CREATE TABLE IF NOT EXISTS shared.geo_mentions (
    id BIGSERIAL PRIMARY KEY, week TEXT NOT NULL, provider TEXT NOT NULL,
    prompt_idx INT NOT NULL, prompt TEXT NOT NULL, answer_excerpt TEXT DEFAULT '',
    beriklan_mentioned BOOLEAN DEFAULT false, competitor_hits JSONB DEFAULT '[]',
    sentiment TEXT DEFAULT 'neutral', created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (week, provider, prompt_idx))`);
  await pool.query(`ALTER TABLE shared.geo_mentions
    ADD COLUMN IF NOT EXISTS day TEXT,
    ADD COLUMN IF NOT EXISTS engine TEXT,
    ADD COLUMN IF NOT EXISTS status TEXT,
    ADD COLUMN IF NOT EXISTS our_rank INT,
    ADD COLUMN IF NOT EXISTS results_total INT,
    ADD COLUMN IF NOT EXISTS domain TEXT`);
  await pool.query(`CREATE INDEX IF NOT EXISTS geo_mentions_day_provider_idx ON shared.geo_mentions (day, provider)`);
}

export async function runGeoSearxng({ maxQueries = 120, notify = true } = {}) {
  const id = await jobStart('geo-searxng');
  const log = [];
  const cap = Math.max(1, Math.min(MAX_CAP, Number(maxQueries) || 120));
  try {
    await ensureSchema();
    const day = new Date().toISOString().slice(0, 10);
    const queries = (await collectQueries(Math.ceil(cap * 0.5), Math.ceil(cap * 0.4))).slice(0, cap);
    log.push(`probing ${queries.length} queries (cap ${cap}) day=${day}`);
    let stored = 0, unknown = 0, present = 0;
    const perDomain = {};
    DOMAINS.forEach(d => perDomain[d] = { present: 0, absent: 0, unknown: 0, ranks: [] });

    for (let i = 0; i < queries.length; i++) {
      const { q, src } = queries[i];
      let res = null, err = '';
      try { res = await searxQuery(q); } catch (e) { err = String(e).slice(0, 90); }
      // ≥2 s + jitter antar query (spec 7.3: hindari pemblokiran engine)
      await sleep(2000 + Math.floor(Math.random() * 1500));
      const results = res ? res.results : [];
      const top = results.slice(0, 20).map(resultUrl).filter(Boolean);
      const lowTop = top.map(u => u.toLowerCase());
      const compHits = COMPETITORS.filter(c => lowTop.some(u => u.indexOf(c.split(' ')[0].toLowerCase()) >= 0));
      // Untuk tiap domain yang dipantau → 1 baris (jadi tren .co.id dan .my tercatat).
      // provider dipisah per-domain karena constraint unik (week, provider, prompt_idx)
      // tidak menyertakan domain.
      for (const dom of DOMAINS) {
        const provider = 'searxng:' + dom;
        const rank = findRank(results, dom);
        let status;
        if (err || results.length === 0) { status = 'unknown'; unknown++; }
        else if (rank) { status = 'present'; present++; }
        else status = 'absent';
        perDomain[dom][status]++;
        if (rank) perDomain[dom].ranks.push(rank);
        await pool.query(
          `INSERT INTO shared.geo_mentions
             (week, provider, prompt_idx, prompt, answer_excerpt, beriklan_mentioned,
              competitor_hits, sentiment, day, engine, status, our_rank, results_total, domain)
           VALUES ($1,$2,$3,$4,$5,$6,$7,'neutral',$8,$9,$10,$11,$12,$13)
           ON CONFLICT (week, provider, prompt_idx) DO UPDATE SET
             prompt=EXCLUDED.prompt, answer_excerpt=EXCLUDED.answer_excerpt,
             beriklan_mentioned=EXCLUDED.beriklan_mentioned, competitor_hits=EXCLUDED.competitor_hits,
             status=EXCLUDED.status, our_rank=EXCLUDED.our_rank, results_total=EXCLUDED.results_total`,
          [day, provider, i, `${q} [${src}]`, top.slice(0, 10).join('\n'), rank !== null,
           JSON.stringify(compHits), day, ENGINE_SET, status, rank, results.length, dom]);
        stored++;
      }
    }

    // Ringkasan + tren 7 hari (7.6) — dipakai laporan mingguan T7.1.
    const summary = DOMAINS.map(dom => {
      const s = perDomain[dom];
      const measured = s.present + s.absent;
      const avgRank = s.ranks.length ? Math.round((s.ranks.reduce((a, b) => a + b, 0) / s.ranks.length) * 10) / 10 : null;
      return `${dom}: ${s.present}/${measured} tampak (${measured ? Math.round(s.present / measured * 100) : 0}%) · avg rank ${avgRank ?? '-'} · unknown ${s.unknown}`;
    });
    let trend = [];
    try {
      const { rows } = await pool.query(
        `SELECT day, domain,
                count(*) FILTER (WHERE status='present') present,
                count(*) FILTER (WHERE status='absent')  absent,
                count(*) FILTER (WHERE status='unknown') unknown,
                round(avg(our_rank) FILTER (WHERE our_rank IS NOT NULL), 1) avg_rank
           FROM shared.geo_mentions
          WHERE provider LIKE 'searxng:%' AND day >= (CURRENT_DATE - 7)
          GROUP BY day, domain ORDER BY day, domain`);
      trend = rows;
    } catch (e) { log.push('trend err: ' + String(e).slice(0, 60)); }

    log.push(`stored ${stored} rows | present ${present} | unknown ${unknown}`);
    log.push(...summary);
    if (notify) {
      await telegram('[GEO keyless/SearXNG] ' + day + '\n' + summary.join('\n'));
    }
    await jobEnd(id, 'ok', log.join(' | '));
    return { ok: true, day, stored, present, unknown, summary, trend, log };
  } catch (e) {
    await jobEnd(id, 'failed', String(e).slice(0, 300));
    return { ok: false, error: String(e).slice(0, 200), log };
  }
}

// CLI: node jobs/geo-searxng.js --max=120 --no-notify
if (import.meta.url === `file://${process.argv[1]}`) {
  const arg = (name, dflt) => {
    const m = process.argv.find(a => a.startsWith(`--${name}=`));
    return m ? m.split('=').slice(1).join('=') : dflt;
  };
  const max = parseInt(arg('max', '120'), 10);
  const notify = !process.argv.includes('--no-notify');
  const r = await runGeoSearxng({ maxQueries: max, notify });
  console.log(JSON.stringify({ ok: r.ok, day: r.day, stored: r.stored, present: r.present, unknown: r.unknown, summary: r.summary, error: r.error }, null, 2));
  process.exit(r.ok ? 0 : 1);
}
