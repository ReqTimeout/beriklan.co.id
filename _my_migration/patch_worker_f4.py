#!/usr/bin/env python3
"""Fase 4 — patch worker-entry.js + wrangler.jsonc untuk beriklan.my.

F4-0  rename worker -> beriklanmy + custom domain routes (anti-timpa .co.id)
F4-1  domain/token/IndexNow key/GSC sc-domain/timezone MYT
F4-2  hapus submitToGscCore + submitToIndexNowCore -> submitIndexNowBatch
F4-3  llms.txt English (services MY, RM)
F4-4  drip 50/hari (override via cron_settings), email-send nonaktif
F4-6  /api/admin/keywords/list (daftar keyword per service + filter + search)
F4-7  kolom GSC clicks/impressions per service group
F4-8  /api/admin/posts?format=json
F4-9  tombol Inspect now (URL Inspection on-demand)
F4-10 IndexNow real-time on publish (sync-posts)
F4-11 RSS feed /rss.xml
F4-12 internal linking 3 cluster + 1 pillar per artikel baru
Plus: prompt AI generator -> English (Malaysia, RM)
"""
import json, os, re, sys

ROOT = os.path.expanduser("~/Desktop/beriklan.my/web")
WORKER = os.path.join(ROOT, "src/worker-entry.js")
WRANGLER = os.path.join(ROOT, "wrangler.jsonc")

NEW_KEY = "2f22c16be9437a90ad2285a4af043e10"
OLD_KEY = "2dac33f6303f4041b9ec7e2f2910ea80"

src = open(WORKER).read()
report = []

def rep(old, new, min_n=1, max_n=None, label=""):
    global src
    n = src.count(old)
    if n < min_n:
        print(f"FAIL [{label}] anchor not found ({n} < {min_n}): {old[:90]!r}")
        sys.exit(1)
    if max_n is not None and n > max_n:
        print(f"FAIL [{label}] too many matches ({n} > {max_n}): {old[:90]!r}")
        sys.exit(1)
    src = src.replace(old, new)
    report.append(f"{label}: {n}x")

def splice(start_marker, end_marker, new_text, label, include_end=False):
    """Replace text from start_marker up to (excl/incl) end_marker."""
    global src
    i = src.find(start_marker)
    if i < 0:
        print(f"FAIL [{label}] start marker not found: {start_marker[:80]!r}")
        sys.exit(1)
    j = src.find(end_marker, i + len(start_marker))
    if j < 0:
        print(f"FAIL [{label}] end marker not found: {end_marker[:80]!r}")
        sys.exit(1)
    if include_end:
        j += len(end_marker)
    src = src[:i] + new_text + src[j:]
    report.append(f"{label}: spliced {j-i} chars")

# ══════════ F4-1: domain / token / key / timezone ══════════
rep("https://www.beriklan.co.id", "https://beriklan.my", 1, None, "F4-1 www-url")
rep("www.beriklan.co.id", "beriklan.my", 0 if "www.beriklan.co.id" not in src else 1, None, "F4-1 www-host") if "www.beriklan.co.id" in src else None
rep("Beriklan.co.id", "Beriklan.my", 1, None, "F4-1 Beriklan-cap")
rep("beriklan.co.id", "beriklan.my", 1, None, "F4-1 domain")
# GitHub repo name (jangan ikut jadi beriklan.my)
rep('repo = "beriklan.my"', 'repo = "beriklanmy"', 2, None, "F4-1 gh-repo")
rep('repo: "beriklan.my"', 'repo: "beriklanmy"', 1, None, "F4-1 gh-repo2")
rep("github.com/ReqTimeout/beriklan.my", "github.com/ReqTimeout/beriklanmy", 1, None, "F4-1 gh-link")
rep("beriklan-admin-2026", "beriklan-my-admin-2026", 10, None, "F4-1 token")
rep(OLD_KEY, NEW_KEY, 5, None, "F4-1 indexnow-key")
rep("7 * 3600 * 1000", "8 * 3600 * 1000", 3, 3, "F4-1 tz-offset")
rep("Asia/Jakarta", "Asia/Kuala_Lumpur", 1, None, "F4-1 tz-name")
src2 = re.sub(r"\bWIB\b", "MYT", src); report.append(f"F4-1 WIB->MYT: {len(re.findall(chr(92)+'bWIB'+chr(92)+'b', src))}x"); src = src2
rep('env.GSC_SITE_URL || "https://beriklan.my/"', 'env.GSC_SITE_URL || "sc-domain:beriklan.my"', 1, 2, "F4-1 gsc-fallback")
rep('encodeURIComponent("https://beriklan.my/")', 'encodeURIComponent("sc-domain:beriklan.my")', 1, 3, "F4-1 gsc-site-enc")
rep('worker: "beriklanweb"', 'worker: "beriklanmy"', 1, 2, "F4-1 worker-name")
rep("p.city || 'Indonesia'", "p.city || 'Malaysia'", 1, 2, "F4-1 tag-country")
rep("'id-ID'", "'en-MY'", 1, None, "F4-1 locale")

# www -> non-www redirect (canonical non-www)
rep('''    const hostname = url.hostname || request.headers.get("Host") || "";
''', '''    const hostname = url.hostname || request.headers.get("Host") || "";

    // Force non-www — canonical beriklan.my
    if (hostname === "www.beriklan.my") {
      url.hostname = "beriklan.my";
      return Response.redirect(url.toString(), 301);
    }
''', 1, 1, "F4-1 www-redirect")

# ══════════ F4-2 + F4-10: legacy core -> submitIndexNowBatch ══════════
splice("// ─── Core: Submit URL ke GSC Indexing API (batasi 200/hari, auto-retry 429) ──",
       "// ─── Admin: Sync posts_meta",
       '''// ─── Core: IndexNow real-time submit (F4-10) — host WAJIB match urlList, multi-endpoint ──
async function submitIndexNowBatch(env, urls) {
  if (!urls.length) return { submitted: 0 };
  const payload = JSON.stringify({
    host: "beriklan.my",
    key: "''' + NEW_KEY + '''",
    keyLocation: "https://beriklan.my/''' + NEW_KEY + '''.txt",
    urlList: urls.slice(0, 100),
  });
  for (const ep of ["https://www.bing.com/indexnow", "https://api.indexnow.org/indexnow", "https://yandex.com/indexnow"]) {
    try {
      const resp = await fetch(ep, { method: "POST", headers: { "Content-Type": "application/json; charset=utf-8" }, body: payload });
      if (resp.ok || resp.status === 202) return { submitted: urls.slice(0, 100).length, endpoint: ep };
    } catch {}
  }
  return { submitted: 0, error: "all_endpoints_failed" };
}


''', "F4-2 remove-legacy")

rep('''    // C. Submit new URLs to GSC Indexing API (max 200/hari, auto-retry 429)
    let gsc = { submitted: 0 };
    if (safeDrafts.length > 0 && env.GSC_SERVICE_ACCOUNT_JSON) {
      const gscUrls = safeDrafts.map(d => `https://beriklan.my/blog/${d.slug}/`);
      gsc = await submitToGscCore(env, gscUrls);
    }

    // D. Submit to IndexNow (hindari rate limit, backoff otomatis)
    let indexnow = { submitted: 0 };
    if (safeDrafts.length > 0) {
      const inUrls = safeDrafts.map(d => `https://beriklan.my/blog/${d.slug}/`);
      indexnow = await submitToIndexNowCore(env, inUrls);
    }''',
'''    // C. GSC submission ditangani cron gsc-indexing via pending_indexing (step 6 di atas)
    const gsc = { submitted: 0, via: "pending_indexing_queue" };

    // D. F4-10: IndexNow real-time on publish — submit batch langsung, tidak tunggu cron
    let indexnow = { submitted: 0 };
    if (safeDrafts.length > 0) {
      const inUrls = safeDrafts.map(d => `https://beriklan.my/blog/${d.slug}/`);
      indexnow = await submitIndexNowBatch(env, inUrls);
    }''', 1, 1, "F4-2 syncposts-cd")

# ══════════ F4-4: drip 50/hari + email-send off ══════════
rep('''    // Daily limit = 200/hari (match GSC Indexing API quota). batch = 50 per cron trigger.
    let dailyLimit = 200;''',
'''    // Daily limit: domain baru mulai 50/hari, naikkan bertahap ke 200 via cron_settings 'daily_publish_limit'
    let dailyLimit = 50;
    try {
      const dl = await env.DB.prepare("SELECT cron FROM cron_settings WHERE name='daily_publish_limit'").first();
      if (dl?.cron && parseInt(dl.cron) > 0) dailyLimit = parseInt(dl.cron);
    } catch {}''', 1, 1, "F4-4 drip50")

rep('''    const cronMap = {
      "*/15 * * * *":  { cronName: "email-send", handler: handleCronSendEmail, path: "/api/cron/email/send?token=beriklan-my-admin-2026" },
    };''',
'''    const cronMap = {
      // F4-4: email-send dinonaktifkan untuk beriklan.my sampai ada list subscriber MY
    };''', 1, 1, "F4-4 email-off")

# ══════════ F4-3: llms.txt English ══════════
splice("const body = `# Beriklan.my", "`;",
'''const body = `# Beriklan.my

> Performance marketing agency for Malaysian businesses. We manage Facebook/Instagram (Meta) Ads, Google Ads, TikTok Ads and YouTube Ads campaigns, build websites and landing pages, and provide live stream viewer boosting for TikTok, Instagram, Shopee, YouTube and Twitch. Transparent weekly reporting, real-time dashboard, pricing in Ringgit Malaysia (RM).

Contact: WhatsApp +62 811-919-328 · https://beriklan.my/order/

## Main Services

- [Digital Marketing Agency](https://beriklan.my/digital-marketing-agency/): Full-service multi-channel campaign management (Meta, Google, TikTok)
- [Facebook Ads Management](https://beriklan.my/facebook-ads-management/): Meta Ads with precise targeting
- [Instagram Ads Management](https://beriklan.my/instagram-ads-management/): Reach & engagement campaigns
- [Google Ads Management](https://beriklan.my/google-ads-management/): Search, Display & YouTube
- [TikTok Ads Management](https://beriklan.my/tiktok-ads-management/): Spark Ads & FYP targeting
- [YouTube Ads Management](https://beriklan.my/youtube-ads-management/): Video ads & awareness
- [Instagram Management](https://beriklan.my/instagram-management/): Content & community management
- [TikTok Management](https://beriklan.my/tiktok-management/): Consistent short-video content
- [Website Development](https://beriklan.my/website-development/): Professional custom & CMS websites
- [Landing Page Design](https://beriklan.my/landing-page-design/): Landing page + Google Ads conversion bundle
- [TikTok Live Viewers](https://beriklan.my/tiktok-live-viewers/): TikTok LIVE viewer packages from RM 5
- [Instagram Live Viewers](https://beriklan.my/instagram-live-viewers/): Instagram LIVE viewer packages
- [Shopee Live Viewers](https://beriklan.my/shopee-live-viewers/): Shopee LIVE viewers for sellers
- [YouTube Live Viewers](https://beriklan.my/youtube-live-viewers/): YouTube live stream viewers
- [Twitch Live Viewers](https://beriklan.my/twitch-live-viewers/): Twitch viewer packages

## Tools & Research

- [Ad Budget Calculator](https://beriklan.my/ad-budget-calculator/): Plan your monthly ad spend
- [ROAS Calculator](https://beriklan.my/roas-calculator/): Measure return on ad spend
- [Malaysia Digital Advertising Report 2026](https://beriklan.my/research/malaysia-digital-advertising-report-2026/): Industry benchmarks & CPM/CPC data

## Blog & Guides

- [Blog](https://beriklan.my/blog/): Digital marketing tips, guides & case studies for Malaysia
- [Sitemap](https://beriklan.my/sitemap_index.xml): Full list of pages

## Latest Articles

${recentList}
`;''', "F4-3 llms-english", include_end=True)

# ══════════ Routes: rss.xml + keywords/list ══════════
rep('''    if (path === "/llms.txt") {
      return await handleLlmsTxt(request, env);
    }''',
'''    if (path === "/llms.txt") {
      return await handleLlmsTxt(request, env);
    }
    if (path === "/rss.xml") {
      return await handleRssFeed(request, env);
    }''', 1, 1, "F4-11 rss-route")

rep('''    if (path === "/api/admin/keywords" || path === "/api/admin/keywords/") {''',
'''    if (path === "/api/admin/keywords/list" || path === "/api/admin/keywords/list/") {
      return await handleKeywordListDashboard(request, env);
    }
    if (path === "/api/admin/keywords" || path === "/api/admin/keywords/") {''', 1, 1, "F4-6 list-route")

# ══════════ F4-8: /api/admin/posts?format=json ══════════
rep('''  const totalPosts = totalRes?.n || 0;''',
'''  const totalPosts = totalRes?.n || 0;

  // F4-8: JSON output untuk monitoring programatik
  if ((url.searchParams.get("format") || "") === "json") {
    const idxByStatus = {};
    for (const r of (idxRes.results || [])) idxByStatus[r.status] = (idxByStatus[r.status] || 0) + 1;
    return new Response(JSON.stringify({
      ok: true,
      total_posts: totalPosts,
      indexing: idxByStatus,
      posts: (postsRes.results || []).slice(0, 200).map(p => ({ slug: p.slug, title: p.title, service: p.service, city: p.city, iso_date: p.iso_date })),
    }), { headers: { "Content-Type": "application/json" } });
  }''', 1, 1, "F4-8 posts-json")

# ══════════ F4-9: Inspect now ══════════
rep('''    let slug = "", bulk = false;
    try {
      const body = await request.formData();
      slug = body.get("slug") || "";
      bulk = body.get("resubmit_all") === "1" || slug === "__all__";''',
'''    let slug = "", bulk = false, inspectSlug = "";
    try {
      const body = await request.formData();
      slug = body.get("slug") || "";
      inspectSlug = body.get("inspect_slug") || "";
      bulk = body.get("resubmit_all") === "1" || slug === "__all__";''', 1, 1, "F4-9 form-parse")

rep('''    } catch { return new Response(JSON.stringify({ ok: false, error: "invalid form" }), { headers: { "Content-Type": "application/json" } }); }''',
'''    } catch { return new Response(JSON.stringify({ ok: false, error: "invalid form" }), { headers: { "Content-Type": "application/json" } }); }

    // F4-9: Inspect now — URL Inspection API on-demand (potong antrian verify)
    if (inspectSlug) {
      if (!env.GSC_SERVICE_ACCOUNT_JSON) return new Response(JSON.stringify({ ok: false, error: "no GSC secret" }), { headers: { "Content-Type": "application/json" } });
      try {
        const sa = JSON.parse(env.GSC_SERVICE_ACCOUNT_JSON);
        const accessToken = await getGoogleAccessToken(sa, "https://www.googleapis.com/auth/webmasters.readonly");
        const pageUrl = `https://beriklan.my/blog/${inspectSlug}/`;
        const r = await fetch("https://searchconsole.googleapis.com/v1/urlInspection/index:inspect", {
          method: "POST",
          headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json" },
          body: JSON.stringify({ inspectionUrl: pageUrl, siteUrl: env.GSC_SITE_URL || "sc-domain:beriklan.my", languageCode: "en-US" }),
        });
        if (!r.ok) return new Response(JSON.stringify({ ok: false, error: `inspect_http_${r.status}`, body: (await r.text().catch(() => "")).slice(0, 200) }), { headers: { "Content-Type": "application/json" } });
        const data = await r.json();
        const isr = data?.inspectionResult?.indexStatusResult || {};
        const cov = isr.coverageState || "unknown";
        const isIndexed = isr.verdict === "PASS";
        await env.DB.prepare(
          isIndexed
            ? "UPDATE pending_indexing SET status='indexed', index_state=?, index_checked_at=datetime('now') WHERE url=?"
            : "UPDATE pending_indexing SET index_state=?, index_checked_at=datetime('now') WHERE url=?"
        ).bind(cov, pageUrl).run();
        return new Response(JSON.stringify({ ok: true, url: pageUrl, verdict: isr.verdict || "unknown", coverage: cov, indexed: isIndexed }), { headers: { "Content-Type": "application/json" } });
      } catch (e) {
        return new Response(JSON.stringify({ ok: false, error: String(e).slice(0, 200) }), { headers: { "Content-Type": "application/json" } });
      }
    }''', 1, 1, "F4-9 inspect-branch")

rep('''<td>${st !== "indexed" ? `<form method="POST" style="display:inline"><input type="hidden" name="slug" value="${esc(p.slug)}"><button class="btn-outline">↻</button></form>` : ""}</td>''',
'''<td>${st !== "indexed" ? `<form method="POST" style="display:inline"><input type="hidden" name="slug" value="${esc(p.slug)}"><button class="btn-outline">↻</button></form>` : ""}<form method="POST" style="display:inline;margin-left:4px"><input type="hidden" name="inspect_slug" value="${esc(p.slug)}"><button class="btn-outline" title="Inspect now — URL Inspection API on-demand">🔍</button></form></td>''', 1, 1, "F4-9 inspect-btn")

rep('''<a href="/api/admin/keywords?token=${token}" class="nav">🎯 Keyword Pipeline</a>''',
'''<a href="/api/admin/keywords?token=${token}" class="nav">🎯 Keyword Pipeline</a>
<a href="/api/admin/keywords/list?token=${token}" class="nav">📋 Keyword List</a>''', 1, 1, "F4-6 nav-link")

# ══════════ F4-12: internal linking injection ══════════
rep('''     // Add new drafts as posts
     for (const draft of safeDrafts) {
       if (!merged.has(draft.slug)) {''',
'''     // Add new drafts as posts (F4-12: inject internal links — 3 artikel cluster + 1 pillar)
     for (const draft of safeDrafts) {
       draft.content = await appendInternalLinks(env, draft);
       if (!merged.has(draft.slug)) {''', 1, 1, "F4-12 inject")

# ══════════ Prompt AI -> English (Malaysia) ══════════
rep('''`Tulis artikel SEO Bahasa Indonesia untuk trending topic: "${chosen}". Tone: profesional, terukur. Format HTML langsung mulai dari <h2>. Include section: Pendahuluan, Cara Praktis, FAQ (3 pertanyaan + jawaban), CTA WhatsApp. Target 500-700 kata. JANGAN pakai kata: bikin, gak, nggak, pasti untung, garansi 100%, dalam dunia, semacam, di mana. Output HANYA body HTML. Mulai dari <h2>.`''',
'''`Write an SEO article in English for the trending topic: "${chosen}", targeting Malaysian business owners. Tone: professional, measured. Output HTML starting directly with <h2>. Include sections: Introduction, Practical Steps, FAQ (3 questions + answers), WhatsApp CTA. Target 500-700 words. Use RM (Ringgit Malaysia) for any prices. NEVER promise guaranteed results or use "100% guarantee". Output ONLY the HTML body. Start with <h2>.`''', 1, 1, "AI trending-prompt")

rep('''  const intent = /\\b(harga|biaya|tarif|murah|paket)\\b/i.test(kw) ? "commercial"
    : /\\b(cara|tips|tutorial|langkah|strategi)\\b/i.test(kw) ? "informational"
    : /\\b(apa itu|bagaimana|kenapa|berapa)\\b/i.test(kw) ? "question"
    : "consideration";''',
'''  const intent = /\\b(harga|biaya|murah|paket|price|cost|pricing|cheap|package|rates?)\\b/i.test(kw) ? "commercial"
    : /\\b(cara|tips|tutorial|strategi|how to|guide|strategy|steps?)\\b/i.test(kw) ? "informational"
    : /\\b(apa itu|bagaimana|berapa|what is|why|how much|is it worth)\\b/i.test(kw) ? "question"
    : "consideration";''', 1, 1, "AI intent-regex")

splice("const prompt = `Kamu adalah SEO copywriter Indonesia senior",
       "Tidak ada markdown fences.`;",
'''const prompt = `You are a senior SEO copywriter for Beriklan.my (https://beriklan.my), a performance marketing agency serving Malaysian businesses.

Task: write an SEO blog article in English for the keyword: "${kw}"
Intent: ${intent}
Service: ${svcName}${city ? ` · City: ${city}` : ""}

Article structure (HTML, start with <h2>, never <h1>):
1. Introduction (why this topic matters for Malaysian businesses, 1 paragraph)
2. Main sections with sub-headings (<h3>) + bullet lists + a table where relevant
3. FAQ (3-4 questions, 1-2 sentence answers)
4. WhatsApp CTA with this link: <a href="https://wa.me/62811919328?text=Hi%20Beriklan%2C%20I%27m%20interested%20in%20${encodeURIComponent(svcName)}${city ? `%20in%20${encodeURIComponent(city)}` : ""}">Chat with us on WhatsApp →</a>

Copy rules:
- Professional, measured, confident tone. Address the reader as "you".
- Never promise guaranteed results, never write "100% guarantee" or fabricated client numbers.
- Length: 700-1000 words.
- Use concrete data (%, RM, specific examples) where relevant — all prices in Ringgit Malaysia (RM).
- Brand voice: senior performance marketing partner, not a salesperson.
- 2-3 internal links to https://beriklan.my/${svc}/ and /${svc}/${city}/ (when city is given).

STRICT TOPIC RULES (MANDATORY):
- The article must ONLY cover advertising services, digital marketing, Meta/Facebook/Instagram/TikTok/Google/YouTube Ads,
  SEO, website development, landing pages, social media management, live stream viewer services, and related performance marketing topics.
- STRICTLY FORBIDDEN: gambling, online slots, lottery, poker, casino, fashion/clothing products, food recipes,
  health/disease, education/schools, pets, job vacancies, cryptocurrency, football, online games, construction,
  or anything outside digital marketing.
- If the keyword looks off-topic, still write it from a digital marketing angle (e.g. "website for schools" →
  website development for education institutions as a marketing asset). NEVER leave the performance marketing niche.

Output: HTML body only, starting with <h2>. No markdown fences.`;''', "AI main-prompt", include_end=True)

splice("const snippetPrompt = `Kamu adalah SEO copywriter Indonesia.",
       '- Jangan overclaim (no "pasti", "100%")`;',
'''const snippetPrompt = `You are an SEO copywriter for the Malaysian market. For the keyword "${cand.keyword}", create a snippet block that helps win Google position 0 (featured snippet).

Output MUST be valid JSON (no markdown):
{
  "definisi": "one 40-60 word definition sentence in English starting with the target keyword",
  "poin": ["point 1", "point 2", "point 3", "point 4"],
  "faq": {"q": "a related natural question", "a": "1-2 sentence answer"}
}

Rules:
- The definition MUST start with the target keyword
- Points: 3-5 bullets, parallel structure, 8-15 words each
- FAQ: natural user question, concise answer
- Formal English, address the reader as "you", prices in RM
- No overclaiming (no "guaranteed", "100%")`;''', "AI snippet-prompt", include_end=True)

rep('''`Tulis artikel SEO Bahasa Indonesia untuk topik: "${q.keyword}". Konteks: layanan ${svcName}, lokasi ${city}, tipe ${intentWord}. Tone profesional, terukur. Format HTML mulai dari <h2>. Struktur: <h2>Pendahuluan</h2> (1 paragraf tentang ${q.keyword} di ${city}), <h2>Cara Kerja & Langkah Praktis</h2> (<ul> 4 langkah), <h2>Yang Perlu Dihindari</h2> (<ul>), <h2>Pertanyaan yang Sering Diajukan</h2> (3x <h3>+<p> FAQ lokal ${city}), <h2>Kesimpulan</h2> (1 paragraf + CTA WhatsApp). Target 400-550 kata. Sebut ${city} dan ${svcName} natural. JANGAN pakai: bikin, gak, nggak, pasti untung, garansi 100%. Output HANYA HTML mulai <h2>.`''',
'''`Write an SEO article in English for the topic: "${q.keyword}". Context: service ${svcName}, location ${city}, type ${intentWord}. Professional, measured tone. HTML format starting with <h2>. Structure: <h2>Introduction</h2> (1 paragraph about ${q.keyword} in ${city}), <h2>How It Works & Practical Steps</h2> (<ul> 4 steps), <h2>What to Avoid</h2> (<ul>), <h2>Frequently Asked Questions</h2> (3x <h3>+<p> local ${city} FAQ), <h2>Conclusion</h2> (1 paragraph + WhatsApp CTA). Target 400-550 words. Mention ${city} and ${svcName} naturally. Prices in RM. NEVER promise guaranteed results. Output ONLY HTML starting with <h2>.`''', 1, 1, "AI batch4-prompt")

rep("Ringkasan Cepat", "Quick Summary", 1, 3, "AI snippet-label")

# ══════════ Append handlers baru (sebelum trailing comments) ══════════
NEW_HANDLERS = '''
// ─── F4-12: Internal linking — 3 artikel satu cluster + 1 pillar page per artikel baru ──
const PILLAR_PAGES = {
  "facebook-ads-management": "/facebook-ads-management/",
  "google-ads-management": "/google-ads-management/",
  "instagram-ads-management": "/instagram-ads-management/",
  "tiktok-ads-management": "/tiktok-ads-management/",
  "youtube-ads-management": "/youtube-ads-management/",
  "instagram-management": "/instagram-management/",
  "tiktok-management": "/tiktok-management/",
  "website-development": "/website-development/",
  "landing-page-design": "/landing-page-design/",
  "digital-marketing-agency": "/digital-marketing-agency/",
  "tiktok-live-viewers": "/tiktok-live-viewers/",
  "instagram-live-viewers": "/instagram-live-viewers/",
  "shopee-live-viewers": "/shopee-live-viewers/",
  "youtube-live-viewers": "/youtube-live-viewers/",
  "twitch-live-viewers": "/twitch-live-viewers/",
  "live-stream-viewers": "/live-stream-viewers/",
};

async function appendInternalLinks(env, draft) {
  try {
    if (!draft.content || draft.content.includes('class="related-reading"')) return draft.content;
    const rel = await env.DB.prepare(
      "SELECT slug, title FROM posts_meta WHERE service = ? AND slug != ? ORDER BY iso_date DESC LIMIT 3"
    ).bind(draft.service || "", draft.slug).all();
    const items = (rel.results || []).map(r =>
      `<li><a href="/blog/${r.slug}/">${String(r.title || r.slug).replace(/</g, "&lt;")}</a></li>`
    );
    const pillar = PILLAR_PAGES[draft.service] || "/digital-marketing-agency/";
    const svcLabel = (draft.service || "digital marketing").replace(/-/g, " ");
    items.push(`<li><a href="${pillar}">Explore our ${svcLabel} service</a></li>`);
    return draft.content + `\\n<div class="related-reading"><h3>Related reading</h3><ul>${items.join("")}</ul></div>`;
  } catch { return draft.content; }
}

// ─── F4-11: RSS feed /rss.xml — 50 post terbaru (Google/Bing polling mempercepat discovery) ──
async function handleRssFeed(request, env) {
  const escXml = (s) => String(s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  try {
    const r = await env.DB.prepare("SELECT slug, title, excerpt, iso_date FROM posts_meta ORDER BY iso_date DESC LIMIT 50").all();
    const items = (r.results || []).map(p => {
      const pub = p.iso_date ? new Date(p.iso_date).toUTCString() : new Date().toUTCString();
      return `  <item>\\n    <title>${escXml(p.title || p.slug)}</title>\\n    <link>https://beriklan.my/blog/${p.slug}/</link>\\n    <guid>https://beriklan.my/blog/${p.slug}/</guid>\\n    <pubDate>${pub}</pubDate>\\n    <description>${escXml(String(p.excerpt || "").slice(0, 300))}</description>\\n  </item>`;
    }).join("\\n");
    const xml = `<?xml version="1.0" encoding="UTF-8"?>\\n<rss version="2.0"><channel>\\n  <title>Beriklan.my — Digital Marketing Malaysia</title>\\n  <link>https://beriklan.my/blog/</link>\\n  <description>Digital marketing guides, ad cost benchmarks and case studies for Malaysian businesses.</description>\\n  <language>en-my</language>\\n  <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>\\n${items}\\n</channel></rss>`;
    return new Response(xml, { headers: { "Content-Type": "application/rss+xml; charset=utf-8", "Cache-Control": "public, max-age=3600" } });
  } catch (e) {
    return new Response(`<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Beriklan.my</title><link>https://beriklan.my/</link><description>temporarily unavailable</description></channel></rss>`, { headers: { "Content-Type": "application/rss+xml; charset=utf-8" } });
  }
}

// ─── F4-6/F4-7: Keyword list per service — status, filter, search box + GSC clicks/impressions ──
async function handleKeywordListDashboard(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token") || "";
  if (token !== env.ADMIN_TOKEN) return new Response("Unauthorized", { status: 401 });
  const esc = (s) => String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  const svc = (url.searchParams.get("service") || "").slice(0, 60);
  const st = (url.searchParams.get("status") || "").slice(0, 30);
  const q = (url.searchParams.get("q") || "").slice(0, 80);
  const page = Math.max(1, parseInt(url.searchParams.get("page") || "1") || 1);
  const PER = 100;

  const tryAll = async (sql, binds = []) => { try { return (await env.DB.prepare(sql).bind(...binds).all()).results || []; } catch { return []; } };
  const tryFirst = async (sql, binds = []) => { try { return await env.DB.prepare(sql).bind(...binds).first(); } catch { return null; } };

  const conds = [], params = [];
  if (svc) { conds.push("service = ?"); params.push(svc); }
  if (st) { conds.push("status = ?"); params.push(st); }
  if (q) { conds.push("keyword LIKE ?"); params.push(`%${q}%`); }
  const where = conds.length ? "WHERE " + conds.join(" AND ") : "";

  const [rows, svcAgg, total, kwMap, svcGsc, kwGsc] = await Promise.all([
    tryAll(`SELECT keyword, keyword_normalized, service, city, status, intent, priority_score, source FROM keyword_queue ${where} ORDER BY priority_score DESC, keyword ASC LIMIT ${PER} OFFSET ${(page - 1) * PER}`, params),
    tryAll("SELECT service, COUNT(*) n, SUM(CASE WHEN status='generated' THEN 1 ELSE 0 END) gen, SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) pend FROM keyword_queue GROUP BY service ORDER BY n DESC"),
    tryFirst(`SELECT COUNT(*) n FROM keyword_queue ${where}`, params),
    tryAll("SELECT keyword, posts FROM keyword_map LIMIT 5000"),
    tryAll("SELECT kq.service svc, SUM(kr.clicks) clicks, SUM(kr.impressions) impressions FROM keyword_ranks kr JOIN keyword_queue kq ON kq.keyword_normalized = LOWER(kr.keyword) WHERE kr.date >= date('now','-28 day') GROUP BY kq.service"),
    tryAll("SELECT LOWER(keyword) k, SUM(clicks) clicks, SUM(impressions) impressions, MIN(position) best_pos FROM keyword_ranks WHERE date >= date('now','-28 day') GROUP BY LOWER(keyword) LIMIT 5000"),
  ]);
  const totalN = total?.n || 0;
  const pages = Math.max(1, Math.ceil(totalN / PER));

  // keyword -> slug artikel (dari keyword_map)
  const kwSlug = {};
  for (const m of kwMap) {
    try { const s = JSON.parse(m.posts || "[]"); if (s.length) kwSlug[String(m.keyword).toLowerCase()] = s[0]; } catch {}
  }
  // keyword -> GSC metrics 28 hari
  const gscByKw = {};
  for (const g of kwGsc) gscByKw[g.k] = g;
  const gscBySvc = {};
  for (const g of svcGsc) gscBySvc[g.svc] = g;

  const stBadge = (s) => s === "generated" ? '<span class="badge b-green">✓ generated</span>'
    : s === "rejected" ? '<span class="badge b-gray">✗ rejected</span>'
    : '<span class="badge b-amber">⏳ pending</span>';

  const qs = (extra) => {
    const p = new URLSearchParams({ token });
    if (svc) p.set("service", svc);
    if (st) p.set("status", st);
    if (q) p.set("q", q);
    for (const [k, v] of Object.entries(extra || {})) p.set(k, String(v));
    return "?" + p.toString();
  };

  const html = `<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Keyword List — Beriklan Admin</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#f5f6fa;font-family:Inter,sans-serif;color:#0f1e3d;line-height:1.5;padding:28px}
h1{font-size:22px;font-weight:800;margin-bottom:4px}
.sub{color:#6b7280;font-size:13px;margin-bottom:18px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px;margin-bottom:18px}
.svc-card{background:#fff;border:1px solid #f0f1f5;border-radius:10px;padding:12px 14px;font-size:12px;cursor:pointer;display:block;color:inherit;text-decoration:none}
.svc-card:hover{border-color:#f59e0b}
.svc-card.active{border-color:#0f1e3d;background:#0f1e3d;color:#fff}
.svc-card b{display:block;font-size:13px;margin-bottom:2px}
.filters{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
.filters input,.filters select{padding:8px 12px;border:1px solid #d1d5db;border-radius:8px;font-size:13px}
.filters button{padding:8px 16px;border-radius:8px;background:#0f1e3d;color:#fff;border:none;font-weight:600;font-size:13px;cursor:pointer}
table{width:100%;border-collapse:collapse;font-size:12px;background:#fff;border-radius:10px;overflow:hidden;border:1px solid #f0f1f5}
th{background:#fafbfc;color:#475569;padding:10px 12px;text-align:left;font-size:10px;text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid #e5e7eb}
td{padding:9px 12px;border-bottom:1px solid #f0f1f5}
tr:hover td{background:#fafbfc}
.badge{display:inline-flex;padding:2px 8px;border-radius:100px;font-size:10px;font-weight:600}
.b-green{background:#d1fae5;color:#065f46}.b-amber{background:#fef3c7;color:#92400e}.b-gray{background:#f1f5f9;color:#475569}
.pager{margin-top:14px;display:flex;gap:8px;font-size:13px}
.pager a{padding:6px 12px;background:#fff;border:1px solid #d1d5db;border-radius:8px;color:#0f1e3d;text-decoration:none}
a.back{font-size:12px;color:#6b7280;text-decoration:none}
</style></head><body>
<p style="margin-bottom:10px"><a class="back" href="/api/admin/posts?token=${token}">← Posts Dashboard</a> · <a class="back" href="/api/admin/keywords?token=${token}">Pipeline Aggregate</a></p>
<h1>🎯 Keyword List per Service</h1>
<p class="sub">${totalN.toLocaleString("en-MY")} keywords match · GSC clicks/impressions = 28 hari terakhir (rank-sync)</p>

<div class="grid">
${svcAgg.map(s => {
  const g = gscBySvc[s.service] || {};
  return `<a class="svc-card${svc === s.service ? " active" : ""}" href="${qs({ service: s.service, page: 1 })}"><b>${esc(s.service || "(none)")}</b>${s.n} kw · ${s.gen} generated · ${s.pend} pending<br>GSC 28d: ${g.clicks || 0} clicks · ${g.impressions || 0} impr</a>`;
}).join("")}
</div>

<form class="filters" method="GET">
<input type="hidden" name="token" value="${token}">
<input type="text" name="q" placeholder="Search keyword…" value="${esc(q)}">
<select name="service"><option value="">All services</option>${svcAgg.map(s => `<option value="${esc(s.service)}"${svc === s.service ? " selected" : ""}>${esc(s.service)}</option>`).join("")}</select>
<select name="status"><option value="">All status</option>${["pending", "generated", "rejected"].map(s => `<option value="${s}"${st === s ? " selected" : ""}>${s}</option>`).join("")}</select>
<button type="submit">Filter</button>
${svc || st || q ? `<a href="${"?token=" + token}" style="padding:8px 12px;font-size:13px;color:#6b7280">reset</a>` : ""}
</form>

<table><thead><tr><th>Keyword</th><th>Service</th><th>City</th><th>Intent</th><th>Score</th><th>Status</th><th>Article</th><th>Clicks 28d</th><th>Impr 28d</th><th>Best Pos</th></tr></thead>
<tbody>${rows.map(r => {
  const g = gscByKw[String(r.keyword_normalized || r.keyword).toLowerCase()] || {};
  const slug = kwSlug[String(r.keyword).toLowerCase()];
  return `<tr>
<td style="font-weight:600">${esc(r.keyword)}</td>
<td style="color:#475569">${esc(r.service || "-")}</td>
<td style="color:#475569">${esc(r.city || "-")}</td>
<td>${esc(r.intent || "-")}</td>
<td>${r.priority_score || 0}</td>
<td>${stBadge(r.status)}</td>
<td>${slug ? `<a href="/blog/${esc(slug)}/" target="_blank" style="color:#0ea5e9">/${esc(slug).slice(0, 40)}…</a>` : "-"}</td>
<td>${g.clicks || 0}</td>
<td>${g.impressions || 0}</td>
<td>${g.best_pos ? Number(g.best_pos).toFixed(1) : "-"}</td>
</tr>`;
}).join("")}</tbody></table>

<div class="pager">
${page > 1 ? `<a href="${qs({ page: page - 1 })}">← Prev</a>` : ""}
<span style="padding:6px 4px;color:#6b7280">Page ${page} / ${pages}</span>
${page < pages ? `<a href="${qs({ page: page + 1 })}">Next →</a>` : ""}
</div>
</body></html>`;
  return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
}

'''
i = src.find("\n// Force rebuild")
if i < 0:
    src += NEW_HANDLERS
    report.append("append-handlers: at EOF")
else:
    src = src[:i] + "\n" + NEW_HANDLERS + src[i:]
    report.append("append-handlers: before force-rebuild comments")

# ══════════ Final assertions ══════════
assert src.count("beriklan.co.id") == 0, "masih ada beriklan.co.id"
assert src.count(OLD_KEY) == 0, "masih ada IndexNow key lama"
assert src.count("submitToGscCore") == 0, "masih ada submitToGscCore"
assert src.count("submitToIndexNowCore") == 0, "masih ada submitToIndexNowCore"
assert src.count("7 * 3600 * 1000") == 0, "masih ada offset WIB"
assert src.count("Bahasa Indonesia untuk") == 0, "masih ada prompt Bahasa Indonesia aktif"
assert "beriklan-my-admin-2026" in src
assert "submitIndexNowBatch" in src and "handleRssFeed" in src and "handleKeywordListDashboard" in src and "appendInternalLinks" in src

open(WORKER, "w").write(src)

# ══════════ wrangler.jsonc (F4-0, F4-4) ══════════
w = open(WRANGLER).read()
assert '"name": "beriklanweb"' in w
w = w.replace('"name": "beriklanweb"', '"name": "beriklanmy"')
w = w.replace('"ADMIN_TOKEN": "beriklan-admin-2026"', '"ADMIN_TOKEN": "beriklan-my-admin-2026"')
w = w.replace('''  "main": "src/worker-entry.js",''', '''  "main": "src/worker-entry.js",
  "routes": [
    { "pattern": "beriklan.my", "custom_domain": true },
    { "pattern": "www.beriklan.my", "custom_domain": true }
  ],''')
w = w.replace('''    "crons": [
      "0 * * * *",
      "*/15 * * * *"
    ]''', '''    "crons": [
      "0 * * * *"
    ]''')
assert '"beriklanmy"' in w and '"beriklan-my-admin-2026"' in w and '"custom_domain"' in w and '*/15' not in w
open(WRANGLER, "w").write(w)
report.append("wrangler.jsonc: name=beriklanmy, token baru, routes custom_domain, cron */15 dihapus")

print("\n".join(report))
print(f"\nOK — worker {len(src.splitlines())} lines")
