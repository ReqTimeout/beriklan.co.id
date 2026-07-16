// Worker entry — Cloudflare Worker for beriklan.co.id
//
// Endpoints:
//   GET  /api/health                          → status + pending count
//   POST /api/cron/indexing?token=...        → daily indexing submission (cron-job.org)
//   POST /api/cron/trending?token=...        → generate trending article (cron-job.org)

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // IndexNow key file
    if (path === "/2dac33f6303f4041b9ec7e2f2910ea80.txt") {
      return new Response("2dac33f6303f4041b9ec7e2f2910ea80", {
        headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "public, max-age=86400" },
      });
    }

    // API endpoints
    if (path === "/api/health" || path === "/api/health/") {
      return await handleHealth(env);
    }
    if (path === "/api/cron/indexing" || path === "/api/cron/indexing/") {
      return await handleIndexingCron(request, env);
    }
    if (path === "/api/cron/trending" || path === "/api/cron/trending/") {
      return await handleTrendingCron(request, env);
    }

    // Static assets fallback
    try {
      return await env.ASSETS.fetch(request);
    } catch (e) {
      return new Response("Not Found", { status: 404 });
    }
  },

  async scheduled(event, env, ctx) {
    console.log("[scheduled] disabled — use /api/cron/* endpoints with cron-job.org");
    return;
  },
};

// ─── Health ─────────────────────────────────────────────────────
async function handleHealth(env) {
  try {
    const pending = await getPendingCount(env);
    const trending = await getTrendingCount(env);
    return new Response(JSON.stringify({
      status: "ok",
      worker: "beriklanweb",
      pending_count: pending,
      trending_articles: trending,
      timestamp: new Date().toISOString(),
    }), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ error: String(e) }), { status: 500 });
  }
}

// ─── Daily Indexing Submission ──────────────────────────────────
async function handleIndexingCron(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  const debug = url.searchParams.get("debug") === "1";

  if (token !== env.ADMIN_TOKEN) {
    return new Response(JSON.stringify({
      error: "Unauthorized",
      hint: "Provide ?token=" + env.ADMIN_TOKEN,
    }), { status: 401, headers: { "Content-Type": "application/json" } });
  }

  try {
    const result = await runIndexingPipeline(env, debug);
    return new Response(JSON.stringify({
      ok: true,
      timestamp: new Date().toISOString(),
      ...result,
    }), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({
      ok: false,
      error: String(e),
    }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
}

// ─── Trending Article Generation ────────────────────────────────
// Updated 2026-07-16: use repo-root path for posts.json

async function handleTrendingCron(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  const debug = url.searchParams.get("debug") === "1";

  if (token !== env.ADMIN_TOKEN) {
    return new Response(JSON.stringify({
      error: "Unauthorized",
      hint: "Provide ?token=" + env.ADMIN_TOKEN,
    }), { status: 401, headers: { "Content-Type": "application/json" } });
  }

  const errors = [];
  try {
    await ensureTrendingTables(env);

    // Step 1: Fetch trending from Google Trends RSS
    let topics = [];
    try {
      const rssResp = await fetch("https://trends.google.com/trending/rss?geo=ID", {
        headers: { "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" },
      });
      const xml = await rssResp.text();
      const itemMatches = [...xml.matchAll(/<item>[\s\S]*?<title>([^<]+)<\/title>/g)];
      topics = itemMatches.slice(0, 10).map(m => m[1].trim());
    } catch (e) {
      errors.push({stage: "rss_fetch", error: e.message});
    }

    // Step 2: Filter niche
    const nicheRegex = /iklan|ads|marketing|digital|umkm|bisnis|facebook|instagram|tiktok|google|whatsapp|youtube|konten|content|chatgpt|gemini|ai|meta ai|spark ads|ads manager/i;
    const nicheTopics = topics.filter(t => nicheRegex.test(t));
    // Pick best topic: niche > non-niche, prefer longer (more descriptive) topics
let pool = nicheTopics.filter(t => t.length > 5);
if (pool.length === 0) pool = topics.filter(t => t.length > 5);
const chosen = pool[0] || "Digital Marketing Trends Indonesia";

    // Step 3: Generate article via Groq API (free tier, no daily limit)
    let article = null;
    let ai_used_model = null;
    const groqModels = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"];
    for (const model of groqModels) {
      if (article && article.length > 500) break;
      if (!env.GROQ_API_KEY) {
        errors.push({stage: "ai_config", message: "GROQ_API_KEY secret not set"});
        break;
      }
      try {
        const groqResp = await fetch("https://api.groq.com/openai/v1/chat/completions", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${env.GROQ_API_KEY}`,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
          },
          body: JSON.stringify({
            model,
            messages: [{
              role: "user",
              content: `Tulis artikel SEO Bahasa Indonesia untuk trending topic: "${chosen}". Tone: profesional, terukur. Format HTML langsung mulai dari <h2>. Include section: Pendahuluan, Cara Praktis, FAQ (3 pertanyaan + jawaban), CTA WhatsApp. Target 500-700 kata. JANGAN pakai kata: bikin, gak, nggak, pasti untung, garansi 100%, dalam dunia, semacam, di mana. Output HANYA body HTML. Mulai dari <h2>.`
            }],
            max_tokens: 4000,
            temperature: 0.7,
          }),
        });
        if (groqResp.ok) {
          const data = await groqResp.json();
          const content = data.choices?.[0]?.message?.content || "";
          // Strip markdown fences if present
          let cleaned = content.trim();
          if (cleaned.startsWith("```html")) cleaned = cleaned.slice(7);
          if (cleaned.startsWith("```")) cleaned = cleaned.slice(3);
          if (cleaned.endsWith("```")) cleaned = cleaned.slice(0, -3);
          article = cleaned.trim();
          ai_used_model = model;
        } else {
          const body = await groqResp.text();
          errors.push({stage: "groq_api", model, status: groqResp.status, body: body.substring(0, 200)});
        }
      } catch (e) {
        errors.push({stage: "groq_try", model, error: e.message});
      }
    }

    if (!article) {
      return new Response(JSON.stringify({
        ok: false,
        message: "AI generation failed - no models worked",
        chosen_topic: chosen,
        errors,
      }), { status: 500, headers: { "Content-Type": "application/json" } });
    }

    // Step 4: Save to D1
    const slug = chosen.toLowerCase()
      .replace(/[^a-z0-9\s-]/g, "")
      .replace(/\s+/g, "-")
      .substring(0, 80)
      .replace(/^-+|-+$/g, "");
    const title = chosen.replace(/\b\w/g, l => l.toUpperCase());
    const now = new Date().toISOString();

    let savedId = null;
    try {
      const result = await env.DB.prepare(
        `INSERT INTO trending_articles (slug, title, content, source, created_at)
         VALUES (?, ?, ?, ?, ?)
         ON CONFLICT(slug) DO UPDATE SET content = excluded.content, title = excluded.title, created_at = excluded.created_at
         RETURNING id`
      ).bind(slug, title, article, "workers_ai", now).run();
      savedId = result?.meta?.last_row_id || null;
    } catch (e) {
      errors.push({stage: "d1_save", error: e.message});
    }

    // Step 5: Commit to GitHub (triggers CF Pages auto-deploy when connected)
    let commitSha = null;
    if (env.GITHUB_TOKEN) {
      try {
        const owner = "ReqTimeout";
        const repo = "beriklan.co.id";
        const filePath = "src/data/posts.json";  // Repo root path

        // Get current file + sha
        const getResp = await fetch(
          `https://api.github.com/repos/${owner}/${repo}/contents/${filePath}`,
          { headers: { "Authorization": `token ${env.GITHUB_TOKEN}`, "User-Agent": "BeriklanWorker/1.0" } }
        );
        if (!getResp.ok) {
          errors.push({stage: "github_get", status: getResp.status, body: (await getResp.text()).substring(0, 200) });
        } else {
          const rawBody = await getResp.text();
          let fileData = {};
          try { fileData = JSON.parse(rawBody); } catch (e) {
            errors.push({stage: "github_parse", error: "Invalid JSON", body: rawBody.substring(0, 200)});
          }
          let currentContent = "";
          if (fileData.content) {
            currentContent = atob(fileData.content.replace(/\n/g, ""));
          } else if (fileData.download_url) {
            const dlResp = await fetch(fileData.download_url, {
              headers: { "Authorization": `token ${env.GITHUB_TOKEN}` }
            });
            if (dlResp.ok) currentContent = await dlResp.text();
            else errors.push({stage: "dl_fetch", status: dlResp.status});
          } else {
            errors.push({stage: "github_no_content", keys: Object.keys(fileData), size: fileData.size});
          }
          if (!currentContent) {
            errors.push({stage: "github_empty", message: "Empty file content"});
          }
          const posts = JSON.parse(currentContent || "[]");

          // Add if not exists
          if (!posts.find(p => p.slug === slug)) {
            const dateStr = new Date().toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }).replace(/ /g, " ");
            const excerpt = article.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim().substring(0, 200);
            const newPost = {
              slug,
              title,
              excerpt,
              content: article,
              date: dateStr,
              iso_date: now,
              category: "trending",
              readTime: Math.max(1, Math.round(article.split(/\s+/).length / 200)) + " min",
              tags: chosen.toLowerCase().split(/\s+/).slice(0, 5),
              featured: false,
              generated: true,
              trending: true,
              service: "jasa-digital-marketing",
              city: null,
              liveUrl: null,
              publish_date: dateStr,
            };
            posts.unshift(newPost);
            // Re-sort by iso_date desc to ensure newest always at top
            posts.sort((a, b) => (b.iso_date || "").localeCompare(a.iso_date || ""));

            const updatedContent = btoa(unescape(encodeURIComponent(JSON.stringify(posts, null, 2))));

            const commitResp = await fetch(
              `https://api.github.com/repos/${owner}/${repo}/contents/${filePath}`,
              {
                method: "PUT",
                headers: {
                  "Authorization": `token ${env.GITHUB_TOKEN}`,
                  "Content-Type": "application/json",
                  "User-Agent": "BeriklanWorker/1.0",
                },
                body: JSON.stringify({
                  message: `trending: AI-generated article '${slug}'`,
                  content: updatedContent,
                  sha: fileData.sha,
                  branch: "main",
                }),
              }
            );
            if (commitResp.ok) {
              const data = await commitResp.json();
              commitSha = data.commit?.sha?.substring(0, 7);

              // Also commit posts-index.json update (top 24 most recent)
              try {
                const indexEntry = {
                  slug, title, excerpt: newPost.excerpt, date: dateStr,
                  iso_date: now, category: "trending", readTime: newPost.readTime,
                  featured: false, tags: newPost.tags,
                };
                const indexData = [indexEntry, ...posts.filter(p => p.slug !== slug)]
                  .slice(0, 24)
                  .map(p => ({
                    slug: p.slug, title: p.title, excerpt: p.excerpt,
                    date: p.date, iso_date: p.iso_date, category: p.category,
                    readTime: p.readTime, featured: p.featured, tags: p.tags,
                  }));

                // Get current index sha
                const indexGet = await fetch(
                  `https://api.github.com/repos/${owner}/${repo}/contents/public/data/posts-index.json`,
                  { headers: { "Authorization": `token ${env.GITHUB_TOKEN}` } }
                );
                let indexSha = "";
                if (indexGet.ok) {
                  const idxData = await indexGet.json();
                  indexSha = idxData.sha;
                }

                const indexContent = btoa(unescape(encodeURIComponent(JSON.stringify(indexData, null, 2))));
                const indexCommit = await fetch(
                  `https://api.github.com/repos/${owner}/${repo}/contents/public/data/posts-index.json`,
                  {
                    method: "PUT",
                    headers: {
                      "Authorization": `token ${env.GITHUB_TOKEN}`,
                      "Content-Type": "application/json",
                      "User-Agent": "BeriklanWorker/1.0",
                    },
                    body: JSON.stringify({
                      message: `trending: update posts-index for '${slug}'`,
                      content: indexContent,
                      sha: indexSha,
                      branch: "main",
                    }),
                  }
                );
                if (!indexCommit.ok) {
                  errors.push({stage: "github_index", status: indexCommit.status,
                                body: (await indexCommit.text()).substring(0, 200) });
                }
              } catch (e) {
                errors.push({stage: "github_index_overall", error: e.message});
              }
            } else {
              errors.push({stage: "github_commit", status: commitResp.status, body: (await commitResp.text()).substring(0, 200) });
            }
          }
        }
      } catch (e) {
        errors.push({stage: "github_overall", error: e.message});
      }
    } else {
      errors.push({stage: "config", message: "GITHUB_TOKEN secret not set"});
    }

    return new Response(JSON.stringify({
      ok: true,
      timestamp: now,
      topic: chosen,
      slug,
      article_length: article.length,
      ai_model: ai_used_model,
      db_id: savedId,
      commit_sha: commitSha,
      url: `https://www.beriklan.co.id/blog/${slug}/`,
      errors: debug || errors.length > 0 ? errors : undefined,
      had_errors: errors.length > 0,
    }), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({
      ok: false,
      error: String(e),
      stack: e.stack?.split("\n").slice(0, 5).join("\n"),
    }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
}

// ─── Database helpers ──────────────────────────────────────────
async function getPendingCount(env) {
  try {
    const { results } = await env.DB.prepare(
      `SELECT COUNT(*) as n FROM pending_indexing WHERE status='pending'`
    ).all();
    return results[0]?.n || 0;
  } catch (e) { return -1; }
}

async function getTrendingCount(env) {
  try {
    const { results } = await env.DB.prepare(
      `SELECT COUNT(*) as n FROM trending_articles`
    ).all();
    return results[0]?.n || 0;
  } catch (e) { return -1; }
}

async function ensureTrendingTables(env) {
  try {
    await env.DB.prepare(
      `CREATE TABLE IF NOT EXISTS trending_articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT NOT NULL UNIQUE,
        title TEXT NOT NULL,
        content TEXT,
        source TEXT DEFAULT 'workers_ai',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )`
    ).run();
  } catch (e) {}
}

// ─── Indexing Pipeline (shared with /api/cron/indexing) ────────
async function runIndexingPipeline(env, debug = false) {
  const INDEXNOW_KEY = "2dac33f6303f4041b9ec7e2f2910ea80";
  const errors = [];

  let pending = [];
  try {
    const { results } = await env.DB.prepare(
      `SELECT url FROM pending_indexing WHERE status='pending' ORDER BY created_at ASC LIMIT 200`
    ).all();
    pending = results.map(r => r.url);
  } catch (e) { errors.push({stage: "d1_query", error: e.message}); }

  if (pending.length === 0) {
    return { google_ok: 0, google_fail: 0, indexnow_engines: 0, urls: 0, errors, had_errors: errors.length > 0 };
  }

  let google_ok = 0, google_fail = 0, indexnow_engines = 0;

  // Google Indexing API (JWT)
  if (env.GSC_SERVICE_ACCOUNT_JSON) {
    let token = null;
    try {
      const sa = JSON.parse(env.GSC_SERVICE_ACCOUNT_JSON);
      token = await getGoogleAccessToken(sa);
    } catch (e) { errors.push({stage: "google_auth", error: e.message}); }

    if (token) {
      for (const url of pending) {
        try {
          const resp = await fetch("https://indexing.googleapis.com/v3/urlNotifications:publish", {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" },
            body: JSON.stringify({ url, type: "URL_UPDATED" }),
          });
          if (resp.ok) {
            google_ok++;
            try {
              await env.DB.prepare(
                `UPDATE pending_indexing SET status='submitted', submitted_at=datetime('now') WHERE url=?`
              ).bind(url).run();
            } catch (e) {}
          } else if (resp.status === 429) {
            google_fail++;
            break;
          } else {
            google_fail++;
            errors.push({stage: "google_publish", status: resp.status, url});
          }
        } catch (e) {
          google_fail++;
          errors.push({stage: "google_url", url, error: e.message});
        }
      }
    }
  } else {
    errors.push({stage: "config", message: "GSC_SERVICE_ACCOUNT_JSON secret not set"});
  }

  // IndexNow
  try {
    const urlList = pending.map(u => u.replace("://beriklan.co.id", "://www.beriklan.co.id"));
    const payload = {
      host: "beriklan.co.id",
      key: INDEXNOW_KEY,
      keyLocation: `https://www.beriklan.co.id/${INDEXNOW_KEY}.txt`,
      urlList,
    };
    for (const ep of ["https://api.indexnow.org/indexnow", "https://www.bing.com/indexnow"]) {
      try {
        const resp = await fetch(ep, {
          method: "POST",
          headers: { "Content-Type": "application/json; charset=utf-8" },
          body: JSON.stringify(payload),
        });
        if (resp.ok || resp.status === 202) indexnow_engines++;
      } catch (e) { errors.push({stage: "indexnow", engine: ep, error: e.message}); }
    }
  } catch (e) { errors.push({stage: "indexnow_outer", error: e.message}); }

  // Log
  try {
    await env.DB.prepare(
      `INSERT INTO cron_logs (timestamp, google_ok, google_fail, indexnow_ok, indexnow_fail, urls_processed)
       VALUES (datetime('now'), ?, ?, ?, 0, ?)`
    ).bind(google_ok, google_fail, indexnow_engines, pending.length).run();
  } catch (e) {}

  return {
    google_ok, google_fail, indexnow_engines, urls: pending.length,
    errors: debug ? errors : errors.length > 0 ? errors : undefined,
    had_errors: errors.length > 0,
  };
}

// ─── Google JWT auth (RSASSA-PKCS1-v1_5) ────────────────────
async function getGoogleAccessToken(sa) {
  const header = { alg: "RS256", typ: "JWT" };
  const now = Math.floor(Date.now() / 1000);
  const claim = {
    iss: sa.client_email,
    scope: "https://www.googleapis.com/auth/indexing",
    aud: sa.token_uri,
    iat: now,
    exp: now + 3600,
  };
  const headerB64 = b64u(JSON.stringify(header));
  const claimB64 = b64u(JSON.stringify(claim));
  const input = `${headerB64}.${claimB64}`;

  const keyData = pkcs8Bytes(sa.private_key);
  const privateKey = await crypto.subtle.importKey(
    "pkcs8", keyData,
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false, ["sign"]
  );
  const sig = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", privateKey, new TextEncoder().encode(input));
  const jwt = `${input}.${b64u(ab2b64(sig))}`;

  const resp = await fetch(sa.token_uri, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${jwt}`,
  });
  if (!resp.ok) {
    const body = await resp.text();
    throw new Error(`Token exchange failed: ${resp.status} - ${body.substring(0, 200)}`);
  }
  const data = await resp.json();
  return data.access_token;
}

// ─── Helpers ──────────────────────────────────────────────────
function b64u(s) {
  const b64 = typeof s === "string" ? btoa(s) : ab2b64(s);
  return b64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function ab2b64(buf) {
  const bytes = new Uint8Array(buf);
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin);
}

function pkcs8Bytes(pem) {
  const b64 = pem
    .replace(/-----BEGIN PRIVATE KEY-----/, "")
    .replace(/-----END PRIVATE KEY-----/, "")
    .replace(/\s+/g, "");
  const bin = atob(b64);
  const buf = new ArrayBuffer(bin.length);
  const view = new Uint8Array(buf);
  for (let i = 0; i < bin.length; i++) view[i] = bin.charCodeAt(i);
  return buf;
}
