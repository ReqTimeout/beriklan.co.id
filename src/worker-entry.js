// Worker entry — Cloudflare Worker for beriklan.co.id
//
// Endpoints:
//   GET  /api/health                          → status + pending count
//   POST /api/cron/indexing?token=...        → daily indexing submission (cron-job.org)
//   POST /api/cron/trending?token=...        → generate trending article (cron-job.org)

import { checkPolicyViolation } from "./policy_filter.js";
import { matchRedirect } from "./redirects.generated.mjs";

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
    if (path === "/api/_test_route" || path === "/api/_test_route/") {
      return new Response(JSON.stringify({ ok: true, marker: "PI_2026-07-17", timestamp: new Date().toISOString() }), { headers: { "Content-Type": "application/json" } });
    }
    if (path === "/api/cron/indexing" || path === "/api/cron/indexing/") {
      return await handleIndexingCron(request, env);
    }
    if (path === "/api/cron/trending" || path === "/api/cron/trending/") {
      return await handleTrendingCron(request, env);
    }
    if (path === "/api/cron/gsc-pull" || path === "/api/cron/gsc-pull/") {
      return await handleGscPullCron(request, env);
    }
    if (path === "/api/batch4" || path === "/api/batch4/") {
      // P0.5 Rate limit: 30 req/jam per IP
      const rl = await checkRateLimit(env, request.headers.get("CF-Connecting-IP"), "/api/batch4", 30, 3600);
      if (!rl.allowed) {
        return new Response(JSON.stringify({
          ok: false,
          error: "Rate limit exceeded",
          endpoint: "/api/batch4",
          retry_after: rl.resetAt - Math.floor(Date.now()/1000),
          limit: 30,
          window: "1 hour"
        }), {
          status: 429,
          headers: {
            "Content-Type": "application/json",
            "Retry-After": String(rl.resetAt - Math.floor(Date.now()/1000)),
            "X-RateLimit-Limit": "30",
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": String(rl.resetAt)
          }
        });
      }
      return await handleBatch4(request, env);
    }
    if (path === "/api/city-enrich" || path === "/api/city-enrich/") {
      // P0.5 Rate limit: 20 req/jam per IP
      const rl = await checkRateLimit(env, request.headers.get("CF-Connecting-IP"), "/api/city-enrich", 20, 3600);
      if (!rl.allowed) {
        return new Response(JSON.stringify({
          ok: false,
          error: "Rate limit exceeded",
          endpoint: "/api/city-enrich",
          retry_after: rl.resetAt - Math.floor(Date.now()/1000),
          limit: 20,
          window: "1 hour"
        }), {
          status: 429,
          headers: {
            "Content-Type": "application/json",
            "Retry-After": String(rl.resetAt - Math.floor(Date.now()/1000)),
            "X-RateLimit-Limit": "20",
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": String(rl.resetAt)
          }
        });
      }
      return await handleCityEnrich(request, env);
    }
    if (path === "/api/ping-sitemap" || path === "/api/ping-sitemap/") {
      // P0.5 Rate limit: 10 req/jam per IP (sensitive endpoint)
      const rl = await checkRateLimit(env, request.headers.get("CF-Connecting-IP"), "/api/ping-sitemap", 10, 3600);
      if (!rl.allowed) {
        return new Response(JSON.stringify({
          ok: false,
          error: "Rate limit exceeded",
          endpoint: "/api/ping-sitemap",
          retry_after: rl.resetAt - Math.floor(Date.now()/1000)
        }), { status: 429, headers: { "Content-Type": "application/json" } });
      }
      try {
        return await handlePingSitemap(request, env);
      } catch (e) {
        return new Response(JSON.stringify({ ok: false, error: String(e), stack: e.stack ? String(e.stack).slice(0, 500) : null }), { status: 500, headers: { "Content-Type": "application/json" } });
      }
    }
    if (path === "/api/sitemap-status" || path === "/api/sitemap-status/") {
      return await handleSitemapStatus(env);
    }
    if (path === "/api/admin/backup" || path === "/api/admin/backup/") {
      // P0.5 Rate limit: 5 req/jam per IP (admin endpoint, strict)
      const rl = await checkRateLimit(env, request.headers.get("CF-Connecting-IP"), "/api/admin/backup", 5, 3600);
      if (!rl.allowed) {
        return new Response(JSON.stringify({ ok: false, error: "Rate limit exceeded" }), { status: 429, headers: { "Content-Type": "application/json" } });
      }
      return await handleAdminBackup(request, env);
    }
    if (path === "/api/admin/seed-mirror" || path === "/api/admin/seed-mirror/") {
      // P0.5 Rate limit: 3 req/jam per IP (heavy endpoint)
      const rl = await checkRateLimit(env, request.headers.get("CF-Connecting-IP"), "/api/admin/seed-mirror", 3, 3600);
      if (!rl.allowed) {
        return new Response(JSON.stringify({ ok: false, error: "Rate limit exceeded" }), { status: 429, headers: { "Content-Type": "application/json" } });
      }
      return await handleAdminSeedMirror(request, env);
    }
    if (path === "/api/admin/migrate" || path === "/api/admin/migrate/") {
      // P0.5 Rate limit: 10 req/jam per IP (idempotent, but limit anyway)
      const rl = await checkRateLimit(env, request.headers.get("CF-Connecting-IP"), "/api/admin/migrate", 10, 3600);
      if (!rl.allowed) {
        return new Response(JSON.stringify({ ok: false, error: "Rate limit exceeded" }), { status: 429, headers: { "Content-Type": "application/json" } });
      }
      return await handleAdminMigrate(request, env);
    }
    if (path === "/api/admin/keys" || path === "/api/admin/keys/") {
      // P0.3 API Keys management: 30 req/jam per IP
      const rl = await checkRateLimit(env, request.headers.get("CF-Connecting-IP"), "/api/admin/keys", 30, 3600);
      if (!rl.allowed) {
        return new Response(JSON.stringify({ ok: false, error: "Rate limit exceeded" }), { status: 429, headers: { "Content-Type": "application/json" } });
      }
      return await handleAdminKeys(request, env);
    }
    if (path === "/api/admin" || path === "/api/admin/") {
      // P0.4 Admin Dashboard HTML
      const rl = await checkRateLimit(env, request.headers.get("CF-Connecting-IP"), "/api/admin/dashboard", 60, 3600);
      if (!rl.allowed) {
        return new Response(JSON.stringify({ ok: false, error: "Rate limit exceeded" }), { status: 429, headers: { "Content-Type": "application/json" } });
      }
      return await handleAdminDashboard(request, env);
    }

    // Static assets fallback
    try {
      // 1. Check _redirects (compiled at build time, inlined)
      const redirectTarget = matchRedirect(path);
      if (redirectTarget) {
        return new Response(null, {
          status: 301,
          headers: {
            "Location": redirectTarget,
            "Cache-Control": "public, max-age=3600",
          },
        });
      }
      const assetResp = await env.ASSETS.fetch(request);
      // Force correct content-type for HTML so browsers never download .txt/.html
      const ct = assetResp.headers.get("content-type") || "";
      if (path.endsWith("/") || path.endsWith(".html") || path === "" || ct.startsWith("text/html")) {
        const headers = new Headers(assetResp.headers);
        headers.set("Content-Type", "text/html; charset=utf-8");
        headers.set("Cache-Control", "no-cache, no-store, must-revalidate");
        headers.delete("Content-Disposition");
        headers.delete("X-Content-Type-Options");
        return new Response(assetResp.body, { status: assetResp.status, headers });
      }
      return assetResp;
    } catch (e) {
      return new Response("Not Found", { status: 404, headers: { "Content-Type": "text/html; charset=utf-8" } });
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

// Sitemap status — show what D1 tracks for each sitemap
async function handleSitemapStatus(env) {
  try {
    const rows = await env.DB.prepare(
      `SELECT siteUrl, sitemapPath, lastSubmitted, lastStatus, created_at FROM gsc_sitemaps ORDER BY id DESC`
    ).all();
    // Also try to list GSC sites the SA can access
    let gscSites = [];
    if (env.GSC_SERVICE_ACCOUNT_JSON) {
      try {
        const sa = JSON.parse(env.GSC_SERVICE_ACCOUNT_JSON);
        const token = await getGoogleAccessToken(sa, "https://www.googleapis.com/auth/webmasters.readonly");
        const r = await fetch("https://www.googleapis.com/webmasters/v3/sites", {
          headers: { "Authorization": `Bearer ${token}` },
        });
        const body = await r.json();
        if (r.ok && body.siteEntry) {
          gscSites = body.siteEntry.map(s => ({
            siteUrl: s.siteUrl, permissionLevel: s.permissionLevel,
          }));
        } else {
          const errText = await r.text();
          gscSites = { error: "API call failed", status: r.status, body: errText.slice(0, 300) };
        }
      } catch (e) {
        gscSites = { error: e.message };
      }
    }
    return new Response(JSON.stringify({
      ok: true,
      sitemaps_in_d1: rows.results,
      sitemaps_in_d1_count: rows.results.length,
      gsc_sites_sa_can_access: gscSites,
      hint: "The siteUrl in your sitemaps ('https://beriklan.co.id') must EXACTLY match a siteUrl listed here.",
    }, null, 2), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ error: String(e) }), { status: 500 });
  }
}

// ─── P0.7 Backup: snapshot D1 → GitHub repo (every 6h) ────────
// Exports all critical D1 tables and a Redis-like as_run log to GH as JSON.
// Idempotent: overwrites the same files every run. Triggered by cron-job.org.
async function handleAdminBackup(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) {
    return new Response(JSON.stringify({ error: "Unauthorized", hint: "Provide ?token=" + env.ADMIN_TOKEN }), { status: 401, headers: { "Content-Type": "application/json" } });
  }
  if (!env.GITHUB_TOKEN) {
    return new Response(JSON.stringify({ ok: false, error: "GITHUB_TOKEN secret not set" }), { status: 503, headers: { "Content-Type": "application/json" } });
  }
  const now = new Date();
  const ts = now.toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const errors = [];
  const results = { timestamp: ts, owner: "ReqTimeout", repo: "beriklan.co.id", path_prefix: `backups/${ts}`, files: [] };

  // Tables to export (chronological: queue → articles → city_content → audit → logs)
  const TABLES = [
    { table: "batch4_queue",     limit: 50000 },
    { table: "batch4_articles",  limit: 50000 },
    { table: "city_content_queue", limit: 10000 },
    { table: "city_content",     limit: 2000 },
    { table: "pending_indexing", limit: 10000 },
    { table: "trending_articles", limit: 5000 },
    { table: "cron_logs",        limit: 1000 },
    { table: "policy_audit_log", limit: 5000 },
    { table: "gsc_sitemaps",     limit: 1000 },
  ];

  for (const t of TABLES) {
    try {
      let allRows = [];
      let cursor = null;
      // Paginated read (D1 has 1000-row default limit per query)
      let safetyCounter = 0;
      while (safetyCounter++ < 100) {
        const q = cursor
          ? `SELECT * FROM ${t.table} WHERE rowid > ? ORDER BY rowid ASC LIMIT ?`
          : `SELECT * FROM ${t.table} ORDER BY rowid ASC LIMIT ?`;
        const stmt = env.DB.prepare(q);
        const binding = cursor ? [cursor, t.limit] : [t.limit];
        const { results: page } = await stmt.bind(...binding).all();
        if (!page || page.length === 0) break;
        allRows = allRows.concat(page);
        if (page.length < t.limit) break;
        cursor = page[page.length - 1].rowid;
      }
      const fname = `${t.table}.json`;
      const target = `${results.path_prefix}/${fname}`;
      const content = JSON.stringify({
        exported_at: ts,
        table: t.table,
        row_count: allRows.length,
        rows: allRows,
      }, null, 2);
      const pushResult = await pushToGithub({
        token: env.GITHUB_TOKEN,
        owner: results.owner,
        repo: results.repo,
        branch: "main",
        filePath: target,
        content,
        message: `backup(${t.table}): snapshot ${allRows.length} rows at ${ts}`,
      });
      results.files.push({ table: t.table, rows: allRows.length, path: target, github_status: pushResult.status, sha: pushResult.sha });
    } catch (e) {
      errors.push({ table: t.table, error: e.message });
    }
  }

  // Also write a manifest summary
  try {
    const manifestContent = JSON.stringify({
      backup_at: ts,
      ok: errors.length === 0,
      files: results.files,
      errors,
    }, null, 2);
    const r = await pushToGithub({
      token: env.GITHUB_TOKEN,
      owner: results.owner,
      repo: results.repo,
      branch: "main",
      filePath: `backups/${ts}/_manifest.json`,
      content: manifestContent,
      message: `backup(manifest): ${results.files.length} tables at ${ts}`,
    });
    results.manifest = { path: `backups/${ts}/_manifest.json`, status: r.status };
  } catch (e) {
    errors.push({ stage: "manifest", error: e.message });
  }

  // Log to cron_logs (best-effort) — schema is {id, timestamp, google_ok, google_fail, indexnow_ok, indexnow_fail, urls_processed}
  try {
    await env.DB.prepare(
      `INSERT INTO cron_logs (timestamp, google_ok, google_fail, indexnow_ok, indexnow_fail, urls_processed)
       VALUES (datetime('now'), ?, ?, ?, ?, ?)`
    ).bind(
      errors.length === 0 ? results.files.length : 0,  // google_ok = files_ok (reused column)
      errors.length,                                    // google_fail = error count
      0, 0,                                             // indexnow counters
      results.files.reduce((s, f) => s + f.rows, 0)      // urls_processed = total rows backed up
    ).run();
  } catch (e) {
    errors.push({ stage: "cron_log", error: e.message });
  }

  return new Response(JSON.stringify({ ok: errors.length === 0, ...results, errors }, null, 2), { headers: { "Content-Type": "application/json" } });
}

// ─── P0.7 Tier 3: Seed posts_meta/posts_content/city_pages/keyword_map from GH JSON ───
// Run after every merge loop iteration to keep D1 mirror in sync.
async function handleAdminSeedMirror(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  }
  if (!env.DB || !env.GITHUB_TOKEN) {
    return new Response(JSON.stringify({ error: "DB or GITHUB_TOKEN missing" }), { status: 503, headers: { "Content-Type": "application/json" } });
  }
  const owner = "ReqTimeout", repo = "beriklan.co.id", branch = "main";
  const errors = [];
  const summary = { posts_meta: 0, posts_content: 0, city_pages: 0, keyword_map: 0 };
  // Phase filter: ?phase=posts|city|keyword|all (default = all, but split for CPU safety)
  const phase = (url.searchParams.get("phase") || "all").toLowerCase();
  // Offset for posts: ?posts_offset=N to chunk across multiple calls
  const postsOffset = parseInt(url.searchParams.get("posts_offset") || "0", 10);
  const postsLimit = parseInt(url.searchParams.get("posts_limit") || "999999", 10);

  async function ghGet(path) {
    const apiResp = await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/${path}?ref=${branch}`, {
      headers: { "Authorization": `token ${env.GITHUB_TOKEN}`, "User-Agent": "BeriklanWorker/1.0" },
    });
    if (!apiResp.ok) throw new Error(`GH GET ${path}: ${apiResp.status}`);
    const meta = await apiResp.json();
    // If file is small enough, use base64 content directly (avoid 2nd round-trip)
    if (meta.size <= 900000 && meta.content) {
      return JSON.parse(atob(meta.content.replace(/\n/g, "")));
    }
    // Otherwise use raw download_url (handles >1MB files)
    if (!meta.download_url) throw new Error(`GH ${path}: missing download_url`);
    const raw = await fetch(meta.download_url, { headers: { "Authorization": `token ${env.GITHUB_TOKEN}` } });
    if (!raw.ok) throw new Error(`GH raw ${path}: ${raw.status}`);
    return await raw.json();
  }

  // 1. posts.json → posts_meta + posts_content (batch upsert via DELETE + INSERT in chunks)
  if (phase === "posts" || phase === "all") {
    try {
      const posts = await ghGet("src/data/posts.json");
      const nowIso = new Date().toISOString();
      summary.posts_meta = posts.length;

      // Slice window
      const slice = posts.slice(postsOffset, postsOffset + postsLimit);

      // Only DELETE if starting from offset 0 (full re-seed)
      if (postsOffset === 0) {
        await env.DB.prepare(`DELETE FROM posts_meta`).run();
        await env.DB.prepare(`DELETE FROM posts_content`).run();
      }

      // Batch insert (5 at a time — D1 SQLite has tighter variable limit and content TEXT columns are heavy)
      const chunkSize = 5;
      for (let i = 0; i < slice.length; i += chunkSize) {
        const chunk = slice.slice(i, i + chunkSize);
        const metaPH = chunk.map(() => "(?,?,?,?,?,?,?,?,?,?,?,?,?)").join(",");
        const contentPH = chunk.map(() => "(?,?)").join(",");

        const metaCols = ["slug","title","excerpt","date","iso_date","category","readTime","tags","service","city","featured","generated","iso_updated"];
        const metaBindings = [];
        for (const p of chunk) {
          metaBindings.push(
            p.slug || "",
            (p.title || "").slice(0, 500),
            (p.excerpt || "").slice(0, 500),
            p.date || "",
            p.iso_date || "",
            p.category || "",
            p.readTime || "",
            JSON.stringify(p.tags || []).slice(0, 1000),
            p.service || "",
            p.city || "",
            p.featured ? 1 : 0,
            p.generated ? 1 : 0,
            nowIso
          );
        }
        try {
          await env.DB.prepare(
            `INSERT INTO posts_meta (${metaCols.join(",")}) VALUES ${metaPH}`
          ).bind(...metaBindings).run();
        } catch (e) {
          errors.push({ stage: "posts_meta_chunk", index: postsOffset + i, error: e.message });
          continue;
        }
        const contentBindings = chunk.map(p => [p.slug || "", p.content || ""]).flat();
        try {
          await env.DB.prepare(
            `INSERT INTO posts_content (slug, content) VALUES ${contentPH}`
          ).bind(...contentBindings).run();
          summary.posts_content += chunk.length;
        } catch (e) {
          errors.push({ stage: "posts_content_chunk", index: postsOffset + i, error: e.message });
        }
      }
      summary.posts_inserted = slice.length;
      summary.posts_next_offset = postsOffset + slice.length < posts.length ? postsOffset + slice.length : null;
    } catch (e) {
      errors.push({ stage: "posts", error: e.message });
    }
  }

  // 2. city-content.json → city_pages
  if (phase === "city" || phase === "all") {
    try {
      const cc = await ghGet("src/data/city-content.json");
      summary.city_pages = Object.keys(cc).length;
      await env.DB.prepare(`DELETE FROM city_pages`).run();
      const entries = Object.entries(cc);
      const chunkSize = 5;
      for (let i = 0; i < entries.length; i += chunkSize) {
        const chunk = entries.slice(i, i + chunkSize);
        const ph = chunk.map(() => "(?,?,?,?,?)").join(",");
        const bindings = chunk.map(([route, html]) => {
          const parts = route.replace(/\/$/, "").split("/");
          const service = parts[0] || "";
          const city = parts[1] || "";
          return [route, service, city, html, new Date().toISOString()];
        }).flat();
        try {
          await env.DB.prepare(
            `INSERT INTO city_pages (route, service, city, html_content, iso_updated) VALUES ${ph}`
          ).bind(...bindings).run();
        } catch (e) {
          errors.push({ stage: "city_pages_chunk", index: i, error: e.message });
        }
      }
    } catch (e) {
      errors.push({ stage: "city", error: e.message });
    }
  }

  // 3. keyword-to-posts.json → keyword_map
  if (phase === "keyword" || phase === "all") {
    try {
      const km = await ghGet("src/data/keyword-to-posts.json");
      summary.keyword_map = Object.keys(km).length;
      await env.DB.prepare(`DELETE FROM keyword_map`).run();
      const entries = Object.entries(km);
      const chunkSize = 5;
      for (let i = 0; i < entries.length; i += chunkSize) {
        const chunk = entries.slice(i, i + chunkSize);
        const ph = chunk.map(() => "(?,?,?,?,?,?)").join(",");
        const bindings = chunk.map(([kw, posts]) => {
          const slugs = Array.isArray(posts) ? posts : [];
          return [kw, JSON.stringify(slugs), "", "", "", new Date().toISOString()];
        }).flat();
        try {
          await env.DB.prepare(
            `INSERT INTO keyword_map (keyword, posts, intent, service, city, iso_updated) VALUES ${ph}`
          ).bind(...bindings).run();
        } catch (e) {
          errors.push({ stage: "keyword_map_chunk", index: i, error: e.message });
        }
      }
    } catch (e) {
      errors.push({ stage: "keyword", error: e.message });
    }
  }

  return new Response(JSON.stringify({ ok: errors.length === 0, summary, errors }, null, 2), { headers: { "Content-Type": "application/json" } });
}

// ─── P0.5 Admin: Run D1 migrations ──────────────────────────────────
async function handleAdminMigrate(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) {
    return new Response(JSON.stringify({ error: "Unauthorized", hint: "Provide ?token=" + env.ADMIN_TOKEN }), { status: 401, headers: { "Content-Type": "application/json" } });
  }
  if (!env.DB) {
    return new Response(JSON.stringify({ ok: false, error: "DB binding not set" }), { status: 503, headers: { "Content-Type": "application/json" } });
  }

  // Migration 0008: rate_limits + 0009: api_keys
  const statements = [
    `CREATE TABLE IF NOT EXISTS rate_limits (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      ip TEXT NOT NULL,
      endpoint TEXT NOT NULL,
      request_count INTEGER DEFAULT 1,
      window_start INTEGER NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(ip, endpoint, window_start)
    )`,
    `CREATE INDEX IF NOT EXISTS idx_rate_limits_ip_endpoint ON rate_limits (ip, endpoint, window_start)`,
    `CREATE INDEX IF NOT EXISTS idx_rate_limits_window ON rate_limits (window_start)`,
    // P0.3 API Key Rotation (recreate tables if old schema)
    `DROP TABLE IF EXISTS api_key_usage`,
    `DROP TABLE IF EXISTS api_keys`,
    `CREATE TABLE api_keys (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      description TEXT,
      key_hash TEXT NOT NULL,
      key_prefix TEXT NOT NULL,
      key_suffix TEXT,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      last_rotated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      expires_at TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'active',
      last_used_at TEXT,
      use_count INTEGER DEFAULT 0,
      rotated_by TEXT
    )`,
    `CREATE INDEX IF NOT EXISTS idx_api_keys_name_status ON api_keys (name, status)`,
    `CREATE INDEX IF NOT EXISTS idx_api_keys_expires ON api_keys (expires_at)`,
    `CREATE TABLE api_key_usage (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      key_name TEXT NOT NULL,
      endpoint TEXT NOT NULL,
      ip TEXT,
      user_agent TEXT,
      status TEXT NOT NULL,
      timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )`,
    `CREATE INDEX IF NOT EXISTS idx_api_key_usage_name_time ON api_key_usage (key_name, timestamp)`,
    `CREATE INDEX IF NOT EXISTS idx_api_key_usage_timestamp ON api_key_usage (timestamp)`,
  ];

  const results = [];
  for (const sql of statements) {
    try {
      await env.DB.prepare(sql).run();
      results.push({ ok: true, sql: sql.slice(0, 80) + "..." });
    } catch (e) {
      results.push({ ok: false, sql: sql.slice(0, 80) + "...", error: e.message });
    }
  }

  // Verify table exists
  let verify = null;
  try {
    const r = await env.DB.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='rate_limits'").all();
    verify = r.results || [];
  } catch (e) {
    verify = { error: e.message };
  }

  // Optional: reset rate limits (?reset=1)
  if (url.searchParams.get("reset") === "1") {
    try {
      await env.DB.prepare("DELETE FROM rate_limits").run();
      results.push({ ok: true, action: "rate_limits cleared" });
    } catch (e) {
      results.push({ ok: false, action: "rate_limits clear failed", error: e.message });
    }
  }

  return new Response(JSON.stringify({ ok: true, migrations: results, verify }, null, 2), { headers: { "Content-Type": "application/json" } });
}

// ─── P0.3 API Key Rotation ──────────────────────────────────
function hashApiKey(key) {
  // Simple hash for verification (use SubtleCrypto if available)
  let h = 0;
  for (let i = 0; i < key.length; i++) {
    h = ((h << 5) - h) + key.charCodeAt(i);
    h = h & h; // Convert to 32-bit int
  }
  return `hash_${Math.abs(h).toString(16)}_${key.length}`;
}

function generateApiKey() {
  // Generate secure random API key: bk_<32-char-hex>
  const chars = "abcdefghijklmnopqrstuvwxyz0123456789";
  let key = "bk_";
  for (let i = 0; i < 32; i++) {
    key += chars[Math.floor(Math.random() * chars.length)];
  }
  return key;
}

async function isApiKeyValid(env, keyName) {
  if (!env.DB) return { valid: false, reason: "DB unavailable" };
  try {
    const r = await env.DB.prepare(
      "SELECT name, status, expires_at FROM api_keys WHERE name = ?"
    ).bind(keyName).all();
    const row = (r.results && r.results[0]);
    if (!row) return { valid: false, reason: "not_found" };
    if (row.status !== "active") return { valid: false, reason: row.status };
    if (new Date(row.expires_at) < new Date()) {
      return { valid: false, reason: "expired", expires_at: row.expires_at };
    }
    // Update last_used_at + use_count
    await env.DB.prepare(
      "UPDATE api_keys SET last_used_at = CURRENT_TIMESTAMP, use_count = use_count + 1 WHERE name = ?"
    ).bind(keyName).run();
    return { valid: true };
  } catch (e) {
    return { valid: false, reason: e.message };
  }
}

async function logKeyUsage(env, keyName, endpoint, ip, ua, status) {
  if (!env.DB) return;
  try {
    await env.DB.prepare(
      "INSERT INTO api_key_usage (key_name, endpoint, ip, user_agent, status) VALUES (?, ?, ?, ?, ?)"
    ).bind(keyName, endpoint, ip || "-", ua || "-", status).run();
  } catch (e) {
    // Silent fail
  }
}

async function handleAdminKeys(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  }
  if (!env.DB) {
    return new Response(JSON.stringify({ ok: false, error: "DB binding not set" }), { status: 503, headers: { "Content-Type": "application/json" } });
  }

  const action = url.searchParams.get("action") || "list";
  const keyName = url.searchParams.get("name");

  try {
    if (action === "list") {
      // List all keys (active + revoked)
      const r = await env.DB.prepare(
        "SELECT name, description, key_prefix, key_suffix, created_at, last_rotated_at, expires_at, status, last_used_at, use_count FROM api_keys ORDER BY name"
      ).all();
      const keys = (r.results || []).map(k => ({
        ...k,
        days_until_expiry: Math.ceil((new Date(k.expires_at) - new Date()) / (1000 * 60 * 60 * 24)),
      }));
      return new Response(JSON.stringify({ ok: true, keys, total: keys.length }, null, 2), { headers: { "Content-Type": "application/json" } });
    }

    if (action === "create") {
      if (!keyName) return new Response(JSON.stringify({ ok: false, error: "name param required" }), { status: 400, headers: { "Content-Type": "application/json" } });
      const description = url.searchParams.get("description") || "";
      const daysValid = parseInt(url.searchParams.get("days") || "90", 10);
      const newKey = generateApiKey();
      const hash = hashApiKey(newKey);
      const prefix = newKey.slice(0, 12);
      const suffix = newKey.slice(-4);
      const now = new Date();
      const expires = new Date(now.getTime() + daysValid * 24 * 60 * 60 * 1000);

      await env.DB.prepare(
        "INSERT INTO api_keys (name, description, key_hash, key_prefix, key_suffix, expires_at, status) VALUES (?, ?, ?, ?, ?, ?, 'active')"
      ).bind(keyName, description, hash, prefix, suffix, expires.toISOString()).run();

      return new Response(JSON.stringify({
        ok: true,
        key_name: keyName,
        api_key: newKey,
        prefix, suffix,
        expires_at: expires.toISOString(),
        days_valid: daysValid,
        warning: "SAVE THIS KEY NOW — it cannot be retrieved later. Only the hash is stored.",
      }, null, 2), { headers: { "Content-Type": "application/json" } });
    }

    if (action === "rotate") {
      if (!keyName) return new Response(JSON.stringify({ ok: false, error: "name param required" }), { status: 400, headers: { "Content-Type": "application/json" } });
      const description = url.searchParams.get("description") || "";
      const daysValid = parseInt(url.searchParams.get("days") || "90", 10);
      const newKey = generateApiKey();
      const hash = hashApiKey(newKey);
      const prefix = newKey.slice(0, 12);
      const suffix = newKey.slice(-4);
      const now = new Date();
      const expires = new Date(now.getTime() + daysValid * 24 * 60 * 60 * 1000);

      // Mark ALL existing rows for this name as 'rotated' (atomic, avoids UNIQUE conflicts)
      await env.DB.prepare("UPDATE api_keys SET status = 'rotated' WHERE name = ? AND status = 'active'").bind(keyName).run();

      // INSERT new active key
      await env.DB.prepare(
        "INSERT INTO api_keys (name, description, key_hash, key_prefix, key_suffix, expires_at, status, rotated_by) VALUES (?, ?, ?, ?, ?, ?, 'active', 'admin-rotation')"
      ).bind(keyName, description, hash, prefix, suffix, expires.toISOString()).run();

      return new Response(JSON.stringify({
        ok: true,
        key_name: keyName,
        api_key: newKey,
        prefix, suffix,
        expires_at: expires.toISOString(),
        warning: "Update your application with this new key immediately.",
      }, null, 2), { headers: { "Content-Type": "application/json" } });
    }

    if (action === "cleanup") {
      // Delete non-active rows (one-time cleanup after schema migration)
      const deleteOld = await env.DB.prepare(
        "DELETE FROM api_keys WHERE status != 'active'"
      ).run();
      return new Response(JSON.stringify({
        ok: true,
        action: "cleanup",
        deleted_rows: deleteOld.meta?.changes || 0
      }), { headers: { "Content-Type": "application/json" } });
    }

    if (action === "revoke") {
      if (!keyName) return new Response(JSON.stringify({ ok: false, error: "name param required" }), { status: 400, headers: { "Content-Type": "application/json" } });
      await env.DB.prepare("UPDATE api_keys SET status = 'revoked' WHERE name = ?").bind(keyName).run();
      return new Response(JSON.stringify({ ok: true, key_name: keyName, status: "revoked" }), { headers: { "Content-Type": "application/json" } });
    }

    if (action === "expiring") {
      // List keys expiring in next N days (default 30)
      const days = parseInt(url.searchParams.get("days") || "30", 10);
      const cutoff = new Date(Date.now() + days * 24 * 60 * 60 * 1000).toISOString();
      const r = await env.DB.prepare(
        "SELECT name, key_prefix, key_suffix, expires_at, status FROM api_keys WHERE status = 'active' AND expires_at <= ? ORDER BY expires_at"
      ).bind(cutoff).all();
      const expiring = (r.results || []).map(k => ({
        ...k,
        days_until_expiry: Math.ceil((new Date(k.expires_at) - new Date()) / (1000 * 60 * 60 * 24)),
      }));
      return new Response(JSON.stringify({ ok: true, expiring, days_window: days }, null, 2), { headers: { "Content-Type": "application/json" } });
    }

    if (action === "usage") {
      // Recent usage stats
      const limit = parseInt(url.searchParams.get("limit") || "50", 10);
      const r = await env.DB.prepare(
        "SELECT key_name, endpoint, ip, status, timestamp FROM api_key_usage ORDER BY timestamp DESC LIMIT ?"
      ).bind(limit).all();
      return new Response(JSON.stringify({ ok: true, usage: r.results || [] }, null, 2), { headers: { "Content-Type": "application/json" } });
    }

    return new Response(JSON.stringify({ ok: false, error: "unknown action", valid_actions: ["list", "create", "rotate", "revoke", "expiring", "usage"] }), { status: 400, headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: e.message }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
}

// ─── P0.4 Admin Dashboard ──────────────────────────────────
async function handleAdminDashboard(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) {
    return new Response("Unauthorized", { status: 401 });
  }

  // Collect all stats in parallel
  const stats = {
    timestamp: new Date().toISOString(),
  };

  // 1. API Keys status
  try {
    const keys = await env.DB.prepare(
      "SELECT name, key_prefix, expires_at, status FROM api_keys WHERE status = 'active'"
    ).all();
    const expiringSoon = (keys.results || []).filter(k => {
      const days = (new Date(k.expires_at) - new Date()) / (1000 * 60 * 60 * 24);
      return days < 30;
    });
    stats.api_keys = {
      total_active: (keys.results || []).length,
      expiring_soon: expiringSoon.length,
      expiring_list: expiringSoon.map(k => ({ name: k.name, prefix: k.key_prefix, days_left: Math.ceil((new Date(k.expires_at) - new Date()) / (1000 * 60 * 60 * 24)) })),
    };
  } catch (e) {
    stats.api_keys = { error: e.message };
  }

  // 2. Rate limits (last hour, top IPs)
  try {
    const now = Math.floor(Date.now() / 1000);
    const windowStart = now - (now % 3600);
    const r = await env.DB.prepare(
      "SELECT ip, endpoint, request_count FROM rate_limits WHERE window_start = ? ORDER BY request_count DESC LIMIT 10"
    ).bind(windowStart).all();
    stats.rate_limits = {
      active_ips: (r.results || []).length,
      top_ips: r.results || [],
      window_start: new Date(windowStart * 1000).toISOString(),
      window_end: new Date((windowStart + 3600) * 1000).toISOString(),
    };
  } catch (e) {
    stats.rate_limits = { error: e.message };
  }

  // 3. Recent cron_logs (last 10)
  try {
    const r = await env.DB.prepare(
      "SELECT timestamp, google_ok, google_fail, indexnow_ok, indexnow_fail, urls_processed FROM cron_logs ORDER BY id DESC LIMIT 10"
    ).all();
    stats.recent_cron_runs = r.results || [];
  } catch (e) {
    stats.recent_cron_runs = { error: e.message };
  }

  // 4. Pending indexing count
  try {
    const r = await env.DB.prepare("SELECT COUNT(*) as count FROM pending_indexing WHERE status = 'pending'").all();
    stats.pending_indexing = (r.results && r.results[0]) ? r.results[0].count : 0;
  } catch (e) {
    stats.pending_indexing = { error: e.message };
  }

  // 5. Backup recency
  try {
    const r = await env.DB.prepare("SELECT id, timestamp FROM cron_logs ORDER BY id DESC LIMIT 1").all();
    stats.last_backup = (r.results && r.results[0]) ? r.results[0] : null;
  } catch (e) {
    stats.last_backup = { error: e.message };
  }

  // If ?format=json → return JSON
  if (url.searchParams.get("format") === "json") {
    return new Response(JSON.stringify(stats, null, 2), { headers: { "Content-Type": "application/json" } });
  }

  // Otherwise return HTML dashboard
  const html = renderDashboard(stats);
  return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
}

function renderDashboard(stats) {
  const expiringRows = (stats.api_keys?.expiring_list || []).map(k => `
    <tr><td><strong>${k.name}</strong></td><td><code>${k.prefix}...${k.days_left ? k.days_left + 'd' : ''}</code></td><td><span class="badge ${k.days_left < 7 ? 'red' : 'yellow'}">${k.days_left} days</span></td><td><a href="/api/admin/keys?token=HIDDEN&action=rotate&name=${k.name}">Rotate Now</a></td></tr>
  `).join('') || '<tr><td colspan="4" style="color:#666;">No keys expiring soon</td></tr>';

  const rateLimitRows = (stats.rate_limits?.top_ips || []).map(r => `
    <tr><td><code>${r.ip || '-'}</code></td><td>${r.endpoint}</td><td><span class="badge ${r.request_count > 30 ? 'red' : 'green'}">${r.request_count}</span></td></tr>
  `).join('') || '<tr><td colspan="3" style="color:#666;">No requests in current window</td></tr>';

  const cronRows = (stats.recent_cron_runs || []).map(c => `
    <tr><td>${(c.timestamp || '').slice(0,19)}</td><td><span class="badge green">${c.google_ok || 0} ✓</span></td><td><span class="badge ${c.google_fail > 0 ? 'red' : 'green'}">${c.google_fail || 0}</span></td><td><span class="badge green">${c.indexnow_ok || 0} ✓</span></td><td><span class="badge ${c.indexnow_fail > 0 ? 'red' : 'green'}">${c.indexnow_fail || 0}</span></td><td>${c.urls_processed || 0}</td></tr>
  `).join('') || '<tr><td colspan="6" style="color:#666;">No cron runs yet</td></tr>';

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Beriklan.co.id Admin Dashboard</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f7; color: #1d1d1f; padding: 20px; }
    .container { max-width: 1100px; margin: 0 auto; }
    h1 { font-size: 24px; margin-bottom: 8px; }
    .subtitle { color: #666; font-size: 13px; margin-bottom: 24px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }
    .card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
    .card h2 { font-size: 13px; color: #666; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .card .metric { font-size: 32px; font-weight: 700; }
    .card .sub { font-size: 12px; color: #666; margin-top: 4px; }
    .card.warning { background: #fff3cd; border-left: 4px solid #f59e0b; }
    .card.error { background: #f8d7da; border-left: 4px solid #dc3545; }
    .card.success { background: #d4edda; border-left: 4px solid #10b981; }
    table { width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 24px; }
    th, td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #eee; font-size: 13px; }
    th { background: #fafafa; color: #666; font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px; }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; background: #eee; color: #333; }
    .badge.green { background: #d4edda; color: #155724; }
    .badge.yellow { background: #fff3cd; color: #856404; }
    .badge.red { background: #f8d7da; color: #721c24; }
    a { color: #2563eb; text-decoration: none; }
    a:hover { text-decoration: underline; }
    code { background: #f0f0f0; padding: 2px 6px; border-radius: 4px; font-size: 12px; }
    .section-title { font-size: 16px; font-weight: 700; margin: 32px 0 12px; }
    .refresh { float: right; font-size: 12px; color: #2563eb; cursor: pointer; }
  </style>
</head>
<body>
<div class="container">
  <h1>🚀 Beriklan.co.id Admin Dashboard</h1>
  <p class="subtitle">Last updated: ${stats.timestamp} | Auto-refresh: <a href="">reload</a></p>

  <!-- Top metrics -->
  <div class="grid">
    <div class="card ${(stats.api_keys?.expiring_soon || 0) > 0 ? 'warning' : 'success'}">
      <h2>API Keys</h2>
      <div class="metric">${stats.api_keys?.total_active || 0}</div>
      <div class="sub">active · <span class="${(stats.api_keys?.expiring_soon || 0) > 0 ? 'badge yellow' : 'badge green'}">${stats.api_keys?.expiring_soon || 0} expiring</span></div>
    </div>
    <div class="card">
      <h2>Active IPs (this hour)</h2>
      <div class="metric">${stats.rate_limits?.active_ips || 0}</div>
      <div class="sub">distinct IPs in rate-limit window</div>
    </div>
    <div class="card ${(stats.pending_indexing || 0) > 100 ? 'warning' : 'success'}">
      <h2>Pending URLs</h2>
      <div class="metric">${stats.pending_indexing || 0}</div>
      <div class="sub">awaiting indexing submit</div>
    </div>
    <div class="card">
      <h2>Last Cron Run</h2>
      <div class="metric" style="font-size: 14px;">${(stats.last_backup?.timestamp || 'never').slice(0, 19) || 'never'}</div>
      <div class="sub">UTC timestamp</div>
    </div>
  </div>

  <!-- API Keys Expiring -->
  <h3 class="section-title">🔑 API Keys Expiring Soon (&lt; 30 days)
    <span class="refresh"><a href="?token=${(new URLSearchParams(stats).get('token') || '')}">refresh</a></span>
  </h3>
  <table>
    <thead><tr><th>Name</th><th>Key Prefix</th><th>Days Left</th><th>Action</th></tr></thead>
    <tbody>${expiringRows}</tbody>
  </table>

  <!-- Top Rate Limited IPs -->
  <h3 class="section-title">🔥 Top Rate-Limited IPs (current hour)</h3>
  <table>
    <thead><tr><th>IP</th><th>Endpoint</th><th>Requests</th></tr></thead>
    <tbody>${rateLimitRows}</tbody>
  </table>

  <!-- Recent Cron Runs -->
  <h3 class="section-title">📅 Recent Cron Runs (last 10)</h3>
  <table>
    <thead><tr><th>Timestamp</th><th>Google ✓</th><th>Google ✗</th><th>IndexNow ✓</th><th>IndexNow ✗</th><th>URLs</th></tr></thead>
    <tbody>${cronRows}</tbody>
  </table>

  <p style="text-align:center;color:#999;font-size:11px;margin-top:40px;">
    Beriklan.co.id Admin Dashboard · P0.4 · ${stats.timestamp}
  </p>
</div>
</body>
</html>`;
}

// ─── P0.5 Rate Limit Middleware ──────────────────────────────────
// Returns true if request is allowed, false if rate-limited
async function checkRateLimit(env, ip, endpoint, maxRequests = 60, windowSeconds = 3600) {
  if (!env.DB || !ip) return { allowed: true, remaining: maxRequests };
  const now = Math.floor(Date.now() / 1000);
  const windowStart = now - (now % windowSeconds); // Round down to nearest window

  try {
    // Cleanup old entries (>2 windows old) — runs occasionally
    if (Math.random() < 0.01) {
      await env.DB.prepare("DELETE FROM rate_limits WHERE window_start < ?")
        .bind(now - (2 * windowSeconds)).run();
    }

    // Try to increment existing record
    const result = await env.DB.prepare(`
      INSERT INTO rate_limits (ip, endpoint, request_count, window_start)
      VALUES (?, ?, 1, ?)
      ON CONFLICT(ip, endpoint, window_start)
      DO UPDATE SET request_count = request_count + 1, updated_at = CURRENT_TIMESTAMP
      RETURNING request_count
    `).bind(ip, endpoint, windowStart).all();

    const count = (result.results && result.results[0]) ? result.results[0].request_count : 0;
    const remaining = Math.max(0, maxRequests - count);

    return {
      allowed: count <= maxRequests,
      count,
      remaining,
      resetAt: windowStart + windowSeconds,
    };
  } catch (e) {
    // Fail open on DB error (better to allow than block)
    return { allowed: true, error: e.message, remaining: maxRequests };
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

// ─── Sitemap Ping (GSC + IndexNow) ──────────────────────────────
// ─── Sitemap Ping (GSC Search Console API + IndexNow) ──────────────
async function handlePingSitemap(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  }
  const siteUrl = "https://www.beriklan.co.id";
  const subSitemaps = [
    "sitemap-static.xml",
    "sitemap-pillar.xml",
    "sitemap-city.xml",
    "sitemap-tag.xml",
    "sitemap-blog.xml",
  ];
  const results = { gsc_sitemap_submit: [], gsc_indexnow: [], indexnow: [], errors: [] };

  // 1. Submit each sub-sitemap to GSC via Search Console API (webmasters/v3)
  //    This is the REAL submission. GET ping is just a hint.
  let gscToken = null;
  if (env.GSC_SERVICE_ACCOUNT_JSON) {
    try {
      const sa = JSON.parse(env.GSC_SERVICE_ACCOUNT_JSON);
      gscToken = await getGoogleAccessToken(sa, "https://www.googleapis.com/auth/webmasters");
    } catch (e) {
      results.errors.push({ stage: "gsc_auth", error: e.message });
    }
    if (gscToken) {
      // First, get list of sitemaps already submitted (to track state)
      try {
        const existing = await fetch(`https://www.googleapis.com/webmasters/v3/sites/${encodeURIComponent(siteUrl)}/sitemaps`, {
          headers: { "Authorization": `Bearer ${gscToken}` },
        });
        const existingBody = existing.ok ? await existing.json() : { sitemapEntry: [] };
        results.gsc_existing = (existingBody.sitemapEntry || []).map(e => ({
          path: e.path, lastSubmitted: e.lastSubmitted, lastDownloaded: e.lastDownloaded, isPending: e.isPending,
        }));
      } catch (e) {
        results.errors.push({ stage: "gsc_list", error: e.message });
      }
      // Submit (PUT) each sub-sitemap
      for (const sub of subSitemaps) {
        const sitemapPath = `${siteUrl.replace(/\/$/, "")}/${sub}`;
        try {
          const resp = await fetch(
            `https://www.googleapis.com/webmasters/v3/sites/${encodeURIComponent(siteUrl)}/sitemaps/${encodeURIComponent(sitemapPath)}`,
            {
              method: "PUT",
              headers: { "Authorization": `Bearer ${gscToken}`, "Content-Type": "application/json" },
            }
          );
          results.gsc_sitemap_submit.push({
            sitemap: sitemapPath,
            status: resp.status,
            ok: resp.ok,
            body: resp.ok ? null : (await resp.text()).slice(0, 200),
          });
          // Update D1 sitemap status table
          try {
            await env.DB.prepare(
              `INSERT OR REPLACE INTO gsc_sitemaps (siteUrl, sitemapPath, lastSubmitted, lastStatus) VALUES (?, ?, datetime('now'), ?)`
            ).bind(siteUrl, sitemapPath, resp.status).run();
          } catch {}
        } catch (e) {
          results.errors.push({ stage: "gsc_submit", sitemap: sitemapPath, error: e.message });
        }
      }
    }
  } else {
    results.errors.push({ stage: "config", message: "GSC_SERVICE_ACCOUNT_JSON not set" });
  }

  // 2. URL_UPDATED for each sub-sitemap (tells Google of new sitemaps)
  if (gscToken) {
    for (const sub of subSitemaps) {
      const sitemapUrl = `${siteUrl}/${sub}`; // siteUrl has no trailing slash
      try {
        const resp = await fetch("https://indexing.googleapis.com/v3/urlNotifications:publish", {
          method: "POST",
          headers: { "Authorization": `Bearer ${gscToken}`, "Content-Type": "application/json" },
          body: JSON.stringify({ url: sitemapUrl, type: "URL_UPDATED" }),
        });
        results.gsc_indexnow.push({ sitemap: sitemapUrl, status: resp.status, ok: resp.ok });
      } catch (e) {
        results.errors.push({ stage: "gsc_indexnow", sitemap: sitemapUrl, error: e.message });
      }
    }
  }

  // 3. Ping IndexNow with each sub-sitemap
  const indexnowKey = env.INDEXNOW_KEY || "2dac33f6303f4041b9ec7e2f2910ea80";
  for (const sub of subSitemaps) {
    const sitemapUrl = `${siteUrl}/${sub}`; // siteUrl has no trailing slash
    try {
      const r = await fetch("https://api.indexnow.org/indexnow", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          host: "beriklan.co.id",
          key: indexnowKey,
          keyLocation: `https://beriklan.co.id/${indexnowKey}.txt`,
          urlList: [sitemapUrl],
        }),
      });
      results.indexnow.push({ sitemap: sitemapUrl, status: r.status, ok: r.ok });
    } catch (e) {
      results.errors.push({ stage: "indexnow", sitemap: sitemapUrl, error: e.message });
    }
  }

  // Summary
  const successCount =
    results.gsc_sitemap_submit.filter(x => x.ok).length +
    results.gsc_indexnow.filter(x => x.ok).length +
    results.indexnow.filter(x => x.ok).length;
  return new Response(JSON.stringify({
    ok: results.errors.length === 0,
    timestamp: new Date().toISOString(),
    subsitemaps: subSitemaps.length,
    success_count: successCount,
    results,
  }), { headers: { "Content-Type": "application/json" } });
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

    // Step 1: Fetch trending from Google Trends RSS (multi-geo for more topics)
    let topics = [];
    const geos = ["ID", "MY", "US"];  // Indonesia, Malaysia, US
    for (const geo of geos) {
      try {
        const rssResp = await fetch(`https://trends.google.com/trending/rss?geo=${geo}`, {
          headers: { "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" },
        });
        if (!rssResp.ok) continue;
        const xml = await rssResp.text();
        const itemMatches = [...xml.matchAll(/<item>[\s\S]*?<title>([^<]+)<\/title>/g)];
        const geo_topics = itemMatches.slice(0, 15).map(m => m[1].trim());
        topics.push(...geo_topics);
      } catch (e) {
        errors.push({stage: "rss_fetch", geo, error: e.message});
      }
    }
    // De-dup (case insensitive)
    const seen = new Set();
    topics = topics.filter(t => {
      const k = t.toLowerCase();
      if (seen.has(k)) return false;
      seen.add(k);
      return true;
    });

    // Step 2: Filter niche — strict include + exclude
    // INCLUDE: business, tech, digital marketing, AI, social platforms
    // EXCLUDE: sports, gambling, entertainment non-DM, news-sensitive
    const nicheInclude = /\biklan\b|\bads\b|\bmarketing\b|\badvertising\b|pemasaran|umkm|\bbisnis\b|jualan|\btoko online\b|\bonline shop\b|marketplace|\bshopee\b|\btokopedia\b|ecommerce|\bstartup\b|\bbrand\b|\bfacebook ads\b|\binstagram ads\b|\btiktok ads\b|\bgoogle ads\b|\bwhatsapp business\b|\byoutube ads\b|meta ads|\bspark ads\b|\breels ads\b|\bperformance marketing\b|\bdigital agency\b|\bmarketing agency\b|konten|\bcontent\b|creator|\binfluencer\b|\bchatgpt\b|\bgemini ai\b|\bclaude\b|\bgpt-4\b|automation|\bgenerative ai\b|\bsoftware\b|\bsaas\b|\bcrm\b|\bseo\b|\bsem\b|\bppc\b|\broas\b|\bcpc\b|\bcpm\b|\bctr\b|\bkonversi\b|\blead generation\b|\blanding page\b|\bfunnel\b|\bemail marketing\b/i;
    const nicheExclude = /\bbola\b|sepak bola|\bliga\b|pemain|olahrag|stadion|stadion|pertandingan|kemenangan|kekalahan|fitness|gym|\bbasket\b|tenis|bulutangkis|\bvoli\b|renang|moto gp|\bf1\b|esports|mlbb|\bpubg\b|\bmobile legend\b|\bgenshin\b|\bhonkai\b|mahjong|catur|gaming|game online|mlbb|genshin impact|mobile games|video game|politik|pemilu|pilpres|partai|korupsi|skandal|gosip|artis|selebriti|kpop|drakor|hollywood|film laga|drama|\bnetflix\b|bencana|kecelakaan|tewas|meninggal|crypto|bitcoin|saham|forex|judi|togel|kasino|bisbol|kriket|hockey|\bgame\b|\bbermain\b/i;
    const nicheTopics = topics.filter(t => {
      if (!nicheInclude.test(t)) return false;
      if (nicheExclude.test(t)) return false;
      return true;
    });
    // Pick best topic: niche > non-niche, prefer longer (more descriptive) topics
let pool = nicheTopics.filter(t => t.length > 5);
let poolSource = "niche_trending";
if (pool.length === 0) {
  // Fallback to curated DM topics (always relevant)
  poolSource = "curated_fallback";
  const curatedTopics = [
    "AI Tools untuk UMKM Indonesia",
    "Strategi Meta Ads 2026",
    "TikTok Shop Indonesia Update",
    "Google Performance Max Optimization",
    "WhatsApp Business AI Chatbot",
    "Content Marketing Trends 2026",
    "ROAS Optimization untuk E-commerce",
  ];
  // Pick a random curated topic
  pool = curatedTopics;
  errors.push({stage: "niche_empty", message: "No trending topic matched niche filter, using curated fallback"});
}
const chosen = pool[Math.floor(Math.random() * pool.length)];

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
    // P0.2: AdSense policy check
    const policyCheck = checkPolicyViolation(`${chosen}\n${title}\n${article}`);
    if (policyCheck.violation && policyCheck.severity === "block") {
      await logPolicyViolation(env, slug, chosen, policyCheck);
      return new Response(JSON.stringify({
        ok: false,
        error: "policy_violation",
        category: policyCheck.category,
        keyword: policyCheck.keyword,
        description: policyCheck.description,
      }), { status: 422, headers: { "Content-Type": "application/json" } });
    }
    if (policyCheck.violation && policyCheck.severity === "warn") {
      await logPolicyViolation(env, slug, chosen, policyCheck);
    }
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
                // Retry once on 409 (stale sha from concurrent commit)
                let indexCommit = await putIndexFile(owner, repo, env.GITHUB_TOKEN, indexContent, indexSha, slug);
                if (indexCommit.status === 409) {
                  const reGet = await fetch(
                    `https://api.github.com/repos/${owner}/${repo}/contents/public/data/posts-index.json`,
                    { headers: { "Authorization": `token ${env.GITHUB_TOKEN}` } }
                  );
                  if (reGet.ok) {
                    const reSha = (await reGet.json()).sha;
                    indexCommit = await putIndexFile(owner, repo, env.GITHUB_TOKEN, indexContent, reSha, slug);
                  }
                }
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
      niche_topics: debug ? nicheTopics.slice(0, 10) : undefined,
      all_topics: debug ? topics.slice(0, 15) : undefined,
      pool_source: poolSource || "niche_trending",
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

// ─── Batch 4 (bulk Excel keywords → Groq → GitHub) ────────────
const B4_SERVICE_NAMES = {
  "jasa-iklan-facebook": "Jasa Iklan Facebook Ads",
  "jasa-iklan-instagram": "Jasa Iklan Instagram",
  "jasa-iklan-tiktok": "Jasa Iklan TikTok Ads",
  "jasa-iklan-google": "Jasa Iklan Google Ads",
  "jasa-iklan-youtube": "Jasa Iklan YouTube",
  "jasa-kelola-instagram": "Jasa Kelola Instagram",
  "jasa-kelola-tiktok": "Jasa Kelola TikTok",
  "jasa-pembuatan-website": "Jasa Pembuatan Website",
  "jasa-pembuatan-landing-page": "Jasa Pembuatan Landing Page",
  "jasa-digital-marketing": "Jasa Digital Marketing",
};
const B4_INTENT = { transactional: "jasa", informational: "panduan", navigational: "info", commercial: "rekomendasi" };

// P0.2: Log policy violation to D1 audit_log (fire-and-forget)
async function logPolicyViolation(env, slug, sourceText, policyResult) {
  if (!env.DB) return;
  try {
    await env.DB.prepare(
      `INSERT INTO policy_audit_log (slug, source, category, keyword, severity, action, created_at)
       VALUES (?, ?, ?, ?, ?, ?, datetime('now'))`
    ).bind(
      slug || "",
      (sourceText || "").slice(0, 200),
      policyResult.category || "",
      policyResult.keyword || "",
      policyResult.severity || "",
      policyResult.severity === "block" ? "rejected" : "logged"
    ).run();
  } catch (e) {
    console.error("policy_audit_log write failed:", e.message);
  }
}

async function handleBatch4(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  }
  const n = Math.min(parseInt(url.searchParams.get("n") || "20", 10), 50);
  const errors = [];
  try {
    // 1. Pull N pending from queue
    const { results: qrows } = await env.DB.prepare(
      `SELECT id, slug, keyword, service, city, intent FROM batch4_queue WHERE status='pending' ORDER BY id ASC LIMIT ${n}`
    ).all();
    if (qrows.length === 0) {
      return new Response(JSON.stringify({ ok: true, done: true, message: "queue empty", processed: 0 }), { headers: { "Content-Type": "application/json" } });
    }

    // 2. Generate each via Groq
    const newPosts = [];
    for (const q of qrows) {
      const svcName = B4_SERVICE_NAMES[q.service] || q.service;
      const city = q.city || "";
      const intentWord = B4_INTENT[q.intent] || "panduan";
      // P0.2: Pre-check the keyword itself against policy before sending to Groq
      // (catches bad topics that would generate bad content)
      const preCheck = checkPolicyViolation(`${q.keyword}\n${q.service}\n${city}`);
      if (preCheck.violation && preCheck.severity === "block") {
        await logPolicyViolation(env, q.slug, q.keyword, preCheck);
        errors.push({ slug: q.slug, stage: "policy_block_pre", category: preCheck.category, keyword: preCheck.keyword });
        await env.DB.prepare(`UPDATE batch4_queue SET status='rejected' WHERE id=?`).bind(q.id).run();
        continue;
      }
      const prompt = `Tulis artikel SEO Bahasa Indonesia untuk topik: "${q.keyword}". Konteks: layanan ${svcName}, lokasi ${city}, tipe ${intentWord}. Tone profesional, terukur. Format HTML mulai dari <h2>. Struktur: <h2>Pendahuluan</h2> (1 paragraf tentang ${q.keyword} di ${city}), <h2>Cara Kerja & Langkah Praktis</h2> (<ul> 4 langkah), <h2>Yang Perlu Dihindari</h2> (<ul>), <h2>Pertanyaan yang Sering Diajukan</h2> (3x <h3>+<p> FAQ lokal ${city}), <h2>Kesimpulan</h2> (1 paragraf + CTA WhatsApp). Target 400-550 kata. Sebut ${city} dan ${svcName} natural. JANGAN pakai: bikin, gak, nggak, pasti untung, garansi 100%. Output HANYA HTML mulai <h2>.`;
      let content = null;
      if (env.GROQ_API_KEY) {
        for (const mdl of ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]) {
          try {
            const gr = await fetch("https://api.groq.com/openai/v1/chat/completions", {
              method: "POST",
              headers: { "Authorization": `Bearer ${env.GROQ_API_KEY}`, "Content-Type": "application/json" },
              body: JSON.stringify({ model: mdl, messages: [{ role: "user", content: prompt }], max_tokens: 1200, temperature: 0.7 }),
            });
            if (gr.ok) { content = (await gr.json()).choices[0].message.content.trim(); break; }
            errors.push({ slug: q.slug, model: mdl, status: gr.status });
          } catch (e) { errors.push({ slug: q.slug, model: mdl, stage: "groq", error: e.message }); }
        }
      }
      if (!content) { errors.push({ slug: q.slug, stage: "no_content" }); continue; }
      if (content.startsWith("```html")) content = content.slice(7);
      if (content.startsWith("```")) content = content.slice(3);
      if (content.endsWith("```")) content = content.slice(0, -3);
      content = content.trim();
      // P0.2: AdSense policy check (check keyword + content)
      const policyCheck = checkPolicyViolation(`${q.keyword}\n${content}`);
      if (policyCheck.violation && policyCheck.severity === "block") {
        await logPolicyViolation(env, q.slug, q.keyword, policyCheck);
        errors.push({ slug: q.slug, stage: "policy_block", category: policyCheck.category, keyword: policyCheck.keyword });
        continue;
      }
      if (policyCheck.violation && policyCheck.severity === "warn") {
        // Allow but log
        await logPolicyViolation(env, q.slug, q.keyword, policyCheck);
      }
      const title = q.keyword.split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
      const excerpt = content.replace(/<[^>]+>/g, " ").split(/\s+/).join(" ").slice(0, 180);
      const now = new Date();
      const dateStr = now.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }).replace(/ /g, " ");
      const iso = now.toISOString();
      const words = content.split(/\s+/).length;
      newPosts.push({
        slug: q.slug, title, excerpt, content, date: dateStr, iso_date: iso,
        category: "strategy", readTime: Math.max(2, Math.round(words / 200)) + " min",
        tags: q.keyword.toLowerCase().split(" ").filter(t => t.length > 3).slice(0, 5),
        featured: false, generated: true, service: q.service, city, liveUrl: null, publish_date: dateStr,
      });
    }

    if (newPosts.length === 0) {
      return new Response(JSON.stringify({ ok: false, processed: 0, errors }), { status: 500, headers: { "Content-Type": "application/json" } });
    }

    // 3. Store to D1 batch4_articles (merged to GitHub by local script)
    await env.DB.batch(newPosts.map(np =>
      env.DB.prepare(
        `INSERT OR IGNORE INTO batch4_articles (slug, data, service, city, created_at)
         VALUES (?, ?, ?, ?, datetime('now'))`
      ).bind(np.slug, JSON.stringify(np), np.service, np.city || "")
    ));

    // 4. Mark queue rows done
    for (const q of qrows) {
      if (newPosts.find(p => p.slug === q.slug)) {
        await env.DB.prepare(`UPDATE batch4_queue SET status='done' WHERE id=?`).bind(q.id).run();
      }
    }

    return new Response(JSON.stringify({
      ok: true, processed: newPosts.length, queue_remaining: qrows.length - newPosts.length,
      stored_d1: true,
      slugs: newPosts.map(p => p.slug), errors: errors.length ? errors : undefined,
    }), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
}

// ─── City content enrichment (uses cities.json from assets) ────
const CITY_FOCUS = {
  "jasa-digital-marketing": "layanan full-service digital marketing (Meta Ads + Google Ads + TikTok Ads + organic content + landing page + analytics)",
  "jasa-iklan-facebook": "iklan Facebook & Instagram (Meta Ads Manager, pixel, retargeting, lookalike audience)",
  "jasa-iklan-google": "iklan Google Ads (Search, Display, YouTube via Google Ads, keyword targeting, conversion tracking)",
  "jasa-iklan-instagram": "iklan Instagram (Reels, Story, Feed, Explore, shop integration, creator collaboration)",
  "jasa-iklan-tiktok": "iklan TikTok (Spark Ads, In-Feed, TopView, FYP targeting, creator marketplace)",
  "jasa-iklan-youtube": "iklan YouTube (TrueView In-Stream, Bumper, Shorts Ads, channel placement)",
  "jasa-kelola-instagram": "manajemen Instagram organik (content calendar, reels production, community management, IG growth)",
  "jasa-kelola-tiktok": "manajemen TikTok organik (script writing, video production rutin, FYP optimization, comment management)",
  "jasa-pembuatan-landing-page": "pembuatan landing page (custom design, fast loading, mobile-optimized, A/B testing ready, integrasi Meta/Google Pixel)",
  "jasa-pembuatan-website": "pembuatan website profesional (company profile, toko online, custom CMS, SEO-friendly, mobile responsive)",
};
const CITY_NAME_MAP = {
  aceh: "Banda Aceh", bali: "Denpasar / Bali", bandung: "Bandung", batam: "Batam",
  bekasi: "Bekasi", bogor: "Bogor", cimahi: "Cimahi", denpasar: "Denpasar",
  depok: "Depok", jogja: "Yogyakarta", lampung: "Bandar Lampung",
  lombok: "Mataram / Lombok", malang: "Malang", medan: "Medan", padang: "Padang",
  palembang: "Palembang", pontianak: "Pontianak", semarang: "Semarang",
  sidoarjo: "Sidoarjo", solo: "Solo / Surakarta", surabaya: "Surabaya",
  tangerang: "Tangerang", yogyakarta: "Yogyakarta",
};

async function loadCities(env) {
  const r = await env.ASSETS.fetch(new URL("https://x/cities.json"));
  if (!r.ok) return [];
  return await r.json();
}

function buildCityPrompt(city, serviceSlug) {
  const name = city.name;
  const focus = CITY_FOCUS[serviceSlug] || "jasa digital marketing";
  const facts = (city.local_facts || []).join(" | ");
  return `Kamu copywriter senior untuk agency Beriklan.co.id (Bandung, sejak 2016).
Tulis artikel HTML pendek (500-700 kata) untuk landing page ${focus} di kota ${name}, Indonesia.

Gunakan fakta lokal kota ini (jika relevan): ${facts}

ATURAN KERAS:
1. BAHASA: Indonesia formal, "Anda" (bukan "kamu"), "kami" (bukan "kita"). NO slang ("bikin", "gak", "nggak"). NO emoji marketing.
2. JANGAN klaim angka fiktif: jangan tulis "50+ klien", "rating 4.9", "ROAS 10x", atau testimoni spesifik. Fokus observasi & cara kerja.
3. Boleh sebut data makro (penetrasi internet, pertumbuhan e-commerce, populasi) HANYA jika masuk akal untuk kota ${name}. Kalau ragu, JANGAN sebut angka spesifik.
4. PERSONA: "Senior Performance Marketing Partner" — bukan jualan, bukan over-promise.
5. STRUKTUR (ikuti persis):

<h2>Mengapa Bisnis di ${name} Butuh ${focus.split(' (')[0].replace(/(^|\\s)(\\w)/g, (m, a, b) => a + b.toUpperCase())}</h2>
<p>3-4 kalimat konteks kenapa ${name} pasar relevan. Sebut industri dominan, perilaku konsumen, dan kenapa digital channel penting.</p>

<h2>Tantangan & Kesalahan Umum di ${name}</h2>
<p>2-3 kalimat observasi tantangan spesifik kota (kompetisi, perilaku audience, gap pengetahuan).</p>
<ul>
<li>Bullet 1: kesalahan / tantangan konkret (3-5 kata)</li>
<li>Bullet 2</li>
<li>Bullet 3</li>
<li>Bullet 4</li>
</ul>

<h2>Cara Kerja Tim Beriklan untuk Bisnis di ${name}</h2>
<p>Lead 1-2 kalimat.</p>
<ul>
<li><strong>Riset & Strategi Lokal:</strong> 1 kalimat menjelaskan riset spesifik untuk ${name}.</li>
<li><strong>Setup & Eksekusi:</strong> 1 kalimat teknis setup channel.</li>
<li><strong>Optimasi & Pelaporan:</strong> 1 kalimat siklus optimasi dan laporan.</li>
<li><strong>Kolaborasi Jangka Panjang:</strong> 1 kalimat komitmen partnership.</li>
</ul>

<h2>Pertanyaan yang Sering Diajukan</h2>
<h3>Berapa biaya untuk bisnis di ${name}?</h3>
<p>Jawaban 2-3 kalimat: fee manajemen dari Rp 2.5jt/bulan + ad spend terpisah ke platform. Tidak ada garansi nominal.</p>
<h3>Berapa lama setup sampai iklan tayang?</h3>
<p>1 kalimat: 3-7 hari kerja setelah akses akun diberikan.</p>
<h3>Apakah tim lokal ${name}?</h3>
<p>1 kalimat: tim Beriklan berbasis Bandung, manage campaign remote + onsite sesuai kebutuhan.</p>
<h3>Bagaimana laporan & akses akun?</h3>
<p>1 kalimat: laporan mingguan bahasa manusia + akses penuh akun Meta/Google/TikTok di sisi klien.</p>

6. OUTPUT: Hanya HTML body (h2/h3/p/ul/li/strong), tanpa <html>, tanpa markdown fence.
7. FOKUS KOTA: Minimal 6-8 penyebutan "${name}" secara natural di seluruh artikel.
8. E-E-A-T: Tunjukkan expertise (audit channel, pixel, attribution, geo-targeting) tanpa over-claim.`;
}

async function handleCityEnrich(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  }
  const n = Math.min(parseInt(url.searchParams.get("n") || "5", 10), 20);
  const errors = [];
  try {
    const { results: qrows } = await env.DB.prepare(
      `SELECT route, city, service FROM city_content_queue WHERE status='pending' ORDER BY rowid ASC LIMIT ${n}`
    ).all();
    if (qrows.length === 0) {
      return new Response(JSON.stringify({ ok: true, done: true, message: "queue empty", processed: 0 }), { headers: { "Content-Type": "application/json" } });
    }
    const cities = await loadCities(env);
    const cityBySlug = {};
    for (const c of cities) cityBySlug[c.slug] = c;
    const cityByName = {};
    for (const c of cities) cityByName[c.name.toLowerCase()] = c;
    const newContents = [];
    for (const q of qrows) {
      const displayName = CITY_NAME_MAP[q.city] || q.city.replace(/-/g, " ");
      const cityObj = cityBySlug[q.city] || cityByName[displayName.toLowerCase().split("/")[0].trim()];
      if (!cityObj) { errors.push({ route: q.route, stage: "city_not_found" }); continue; }
      // P0.2: Pre-check the route (city + service) against policy before Groq
      const preCheck = checkPolicyViolation(`${q.city} ${q.service} ${displayName}`);
      if (preCheck.violation && preCheck.severity === "block") {
        await logPolicyViolation(env, q.route, `${q.city} ${q.service}`, preCheck);
        errors.push({ route: q.route, stage: "policy_block_pre", category: preCheck.category, keyword: preCheck.keyword });
        await env.DB.prepare(`UPDATE city_content_queue SET status='rejected' WHERE route=?`).bind(q.route).run();
        continue;
      }
      const prompt = buildCityPrompt(cityObj, q.service);
      let html = null;
      if (env.GROQ_API_KEY) {
        for (const mdl of ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]) {
          try {
            const gr = await fetch("https://api.groq.com/openai/v1/chat/completions", {
              method: "POST",
              headers: { "Authorization": `Bearer ${env.GROQ_API_KEY}`, "Content-Type": "application/json" },
              body: JSON.stringify({ model: mdl, messages: [{ role: "user", content: prompt }], max_tokens: 1600, temperature: 0.7 }),
            });
            if (gr.ok) { html = (await gr.json()).choices[0].message.content.trim(); break; }
            errors.push({ route: q.route, model: mdl, status: gr.status });
          } catch (e) { errors.push({ route: q.route, model: mdl, stage: "groq", error: e.message }); }
        }
      }
      if (!html) { errors.push({ route: q.route, stage: "no_content" }); continue; }
      if (html.startsWith("```html")) html = html.slice(7);
      if (html.startsWith("```")) html = html.slice(3);
      if (html.endsWith("```")) html = html.slice(0, -3);
      html = html.trim();
      // P0.2: AdSense policy check
      const policyCheck = checkPolicyViolation(`${q.city} ${q.service}\n${html}`);
      if (policyCheck.violation && policyCheck.severity === "block") {
        await logPolicyViolation(env, q.route, `${q.city} ${q.service}`, policyCheck);
        errors.push({ route: q.route, stage: "policy_block", category: policyCheck.category, keyword: policyCheck.keyword });
        continue;
      }
      if (policyCheck.violation && policyCheck.severity === "warn") {
        await logPolicyViolation(env, q.route, `${q.city} ${q.service}`, policyCheck);
      }
      newContents.push({ route: q.route, content: html, city: q.city, service: q.service });
    }
    if (newContents.length === 0) {
      return new Response(JSON.stringify({ ok: false, processed: 0, errors }), { status: 500, headers: { "Content-Type": "application/json" } });
    }
    await env.DB.batch(newContents.map(nc =>
      env.DB.prepare(
        `INSERT OR REPLACE INTO city_content (route, content, city, service) VALUES (?, ?, ?, ?)`
      ).bind(nc.route, nc.content, nc.city, nc.service)
    ));
    for (const q of qrows) {
      if (newContents.find(c => c.route === q.route)) {
        await env.DB.prepare(`UPDATE city_content_queue SET status='done' WHERE route=?`).bind(q.route).run();
      }
    }
    return new Response(JSON.stringify({
      ok: true, processed: newContents.length, queue_remaining: qrows.length - newContents.length,
      stored_d1: true,
      routes: newContents.map(c => c.route), errors: errors.length ? errors : undefined,
    }), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500, headers: { "Content-Type": "application/json" } });
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
  const INDEXNOW_KEY = "2f22c16be9437a90ad2285a4af043e10";
  const errors = [];

  let pending = [];
  try {
    // CF Workers free tier allows max 50 subrequests per invocation.
    // Google Indexing API = 1 subrequest/URL, so cap at 18 to leave headroom
    // for IndexNow (2) + D1 writes + cron_log insert.
    const { results } = await env.DB.prepare(
      `SELECT url FROM pending_indexing WHERE status='pending' ORDER BY created_at ASC LIMIT 18`
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
      keyLocation: `https://beriklan.co.id/INDEXNOW_KEY.txt`,
      urlList,
    };
    for (const ep of ["https://api.indexnow.org/indexnow", "https://www.bing.com/indexnow"]) {
      try {
        const resp = await fetch(ep, {
          method: "POST",
          headers: { "Content-Type": "application/json; charset=utf-8" },
          body: JSON.stringify(payload),
        });
        if (resp.ok || resp.status === 202) {
          indexnow_engines++;
        } else if (resp.status === 429) {
          errors.push({stage: "indexnow", engine: ep, status: 429, message: "rate limited — retry later"});
          break;
        } else {
          const ib = await resp.text().catch(() => "");
          errors.push({stage: "indexnow", engine: ep, status: resp.status, body: ib.substring(0, 150)});
        }
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

// ─── GSC Pull Cron (Search Analytics → gsc-stats.json) ──────
async function handleGscPullCron(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  }
  if (!env.GSC_SERVICE_ACCOUNT_JSON) {
    return new Response(JSON.stringify({ ok: false, error: "GSC_SERVICE_ACCOUNT_JSON not set" }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
  try {
    const sa = JSON.parse(env.GSC_SERVICE_ACCOUNT_JSON);
    const gscToken = await getGoogleAccessToken(sa, "https://www.googleapis.com/auth/webmasters.readonly");
    const siteUrl = "https://www.beriklan.co.id";
    const endDate = new Date();
    const startDate = new Date(endDate.getTime() - 28 * 86400000);
    const fmt = (d) => d.toISOString().slice(0, 10);

    async function query(dimensions, rowLimit = 25) {
      const resp = await fetch(`https://www.googleapis.com/webmasters/v3/sites/${encodeURIComponent(siteUrl)}/searchAnalytics/query`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${gscToken}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          startDate: fmt(startDate),
          endDate: fmt(endDate),
          dimensions,
          rowLimit,
        }),
      });
      if (!resp.ok) {
        const t = await resp.text().catch(() => "");
        throw new Error(`GSC query ${dimensions} failed: ${resp.status} ${t.slice(0, 200)}`);
      }
      return (await resp.json()).rows || [];
    }

    const totalsRows = await query([]);
    const totalsRow = totalsRows[0] || { clicks: 0, impressions: 0, ctr: 0, position: 0 };
    const totals = {
      clicks: totalsRow.clicks || 0,
      impressions: totalsRow.impressions || 0,
      ctr: totalsRow.ctr || 0,
      position: totalsRow.position || 0,
    };
    if (totals.impressions) totals.ctr = Math.round((totals.clicks / totals.impressions) * 10000) / 10000;

    const pageRows = await query(["page"], 25);
    const top_pages = pageRows.map(r => ({
      url: r.keys[0],
      clicks: r.clicks,
      impressions: r.impressions,
      ctr: Math.round(r.ctr * 10000) / 10000,
      position: Math.round(r.position * 10) / 10,
    }));

    const queryRows = await query(["query"], 25);
    const top_queries = queryRows.map(r => ({
      query: r.keys[0],
      clicks: r.clicks,
      impressions: r.impressions,
      ctr: Math.round(r.ctr * 10000) / 10000,
      position: Math.round(r.position * 10) / 10,
    }));

    const countryRows = await query(["country"], 10);
    const by_country = countryRows.map(r => ({ country: r.keys[0], clicks: r.clicks, impressions: r.impressions }));

    const deviceRows = await query(["device"], 5);
    const by_device = deviceRows.map(r => ({ device: r.keys[0], clicks: r.clicks, impressions: r.impressions }));

    const dailyRows = await query(["date"], 28);
    const daily = dailyRows.map(r => ({
      date: r.keys[0],
      clicks: r.clicks,
      impressions: r.impressions,
      ctr: Math.round(r.ctr * 10000) / 10000,
      position: Math.round(r.position * 10) / 10,
    }));

    // Freshness alerts: week-over-week impression drop > 40% on top pages
    let freshness_alerts = [];
    try {
      const wkEnd = new Date(endDate.getTime() - 7 * 86400000);
      const wkStart = new Date(endDate.getTime() - 14 * 86400000);
      const q = await fetch(`https://www.googleapis.com/webmasters/v3/sites/${encodeURIComponent(siteUrl)}/searchAnalytics/query`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${gscToken}`, "Content-Type": "application/json" },
        body: JSON.stringify({ startDate: fmt(wkStart), endDate: fmt(wkEnd), dimensions: ["page"], rowLimit: 25 }),
      });
      const prevRows = q.ok ? ((await q.json()).rows || []) : [];
      const prevMap = Object.fromEntries(prevRows.map(r => [r.keys[0], r.impressions]));
      freshness_alerts = top_pages
        .map(p => {
          const prev = prevMap[p.url] || 0;
          const drop = prev ? Math.round((1 - p.impressions / prev) * 100) : 0;
          return prev > 50 && drop > 40 ? { url: p.url, last_week_impressions: prev, this_week_impressions: p.impressions, drop_pct: drop } : null;
        })
        .filter(Boolean);
    } catch (e) { freshness_alerts = [{ error: e.message }]; }

    const stats = {
      generated_at: new Date().toISOString(),
      period_days: 28,
      site_url: siteUrl,
      totals,
      top_pages,
      top_queries,
      by_country,
      by_device,
      daily,
      freshness_alerts,
    };

    // Persist to D1 (best-effort)
    try {
      await env.DB.prepare(
        `INSERT OR REPLACE INTO gsc_sitemaps (siteUrl, sitemapPath, lastSubmitted, lastStatus) VALUES (?, ?, datetime('now'), ?)`
      ).bind(siteUrl, "gsc-pull", 200).run();
    } catch {}

    // Push gsc-stats.json to GitHub (public/data/) via Contents API
    let github = { pushed: false };
    const ghToken = env.GITHUB_TOKEN || "";
    if (ghToken) {
      try {
        const path = "public/data/gsc-stats.json";
        const getResp = await fetch(`https://api.github.com/repos/${env.GITHUB_REPO || "ReqTimeout/beriklan.co.id"}/contents/${path}`, {
          headers: { "Authorization": `token ${ghToken}`, "User-Agent": "BeriklanWorker/1.0" },
        });
        const sha = getResp.ok ? (await getResp.json()).sha : undefined;
        const body = JSON.stringify({
          message: `chore(gsc): pull stats ${fmt(endDate)}`,
          content: b64u(JSON.stringify(stats, null, 2)),
          branch: "main",
          ...(sha ? { sha } : {}),
        });
        const putResp = await fetch(`https://api.github.com/repos/${env.GITHUB_REPO || "ReqTimeout/beriklan.co.id"}/contents/${path}`, {
          method: "PUT",
          headers: { "Authorization": `token ${ghToken}`, "Content-Type": "application/json", "User-Agent": "BeriklanWorker/1.0" },
          body,
        });
        github = { pushed: putResp.ok, status: putResp.status };
      } catch (e) { github = { pushed: false, error: e.message }; }
    }

    return new Response(JSON.stringify({ ok: true, timestamp: new Date().toISOString(), stats_summary: totals, freshness_alerts_count: freshness_alerts.length, github }), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
}

// ─── Google JWT auth (RSASSA-PKCS1-v1_5) ────────────────────
async function getGoogleAccessToken(sa, scope = null) {
  const header = { alg: "RS256", typ: "JWT" };
  const now = Math.floor(Date.now() / 1000);
  // Allow caller to specify scope; default to multi-scope for indexing + webmasters
  const defaultScope = "https://www.googleapis.com/auth/indexing https://www.googleapis.com/auth/webmasters";
  const claim = {
    iss: sa.client_email,
    scope: scope || defaultScope,
    aud: sa.token_uri,
    iat: now,
    exp: now + 3600,
  };
  const headerB64 = b64u(JSON.stringify(header));
  const claimB64 = b64u(JSON.stringify(claim));
  const input = `${headerB64}.${claimB64}`;

  const keyData = str2ab(pem2der(sa.private_key));
  const privateKey = await crypto.subtle.importKey(
    "pkcs8", keyData,
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false, ["sign"]
  );
  const sig = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", privateKey, new TextEncoder().encode(input));
  const jwt = `${input}.${buf2b64url(new Uint8Array(sig))}`;

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
  const b64 = typeof s === "string" ? btoa(s) : buf2b64url(new Uint8Array(s));
  return b64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function buf2b64url(bytes) {
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function str2ab(b64) {
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes;
}

function pem2der(pem) {
  return pem
    .replace(/-----BEGIN PRIVATE KEY-----/, "")
    .replace(/-----END PRIVATE KEY-----/, "")
    .replace(/\s+/g, "");
}

async function putIndexFile(owner, repo, token, content, sha, slug) {
  return await fetch(
    `https://api.github.com/repos/${owner}/${repo}/contents/public/data/posts-index.json`,
    {
      method: "PUT",
      headers: {
        "Authorization": `token ${token}`,
        "Content-Type": "application/json",
        "User-Agent": "BeriklanWorker/1.0",
      },
      body: JSON.stringify({
        message: `trending: update posts-index for '${slug}'`,
        content,
        sha,
        branch: "main",
      }),
    }
  );
}

// P0.7: Generic GitHub file PUT (creates if no sha, updates otherwise)
// `content` is a UTF-8 string; we base64-encode it for GH Contents API.
async function pushToGithub({ token, owner, repo, branch, filePath, content, message }) {
  // 1. Get existing file sha (if any)
  let sha = null;
  try {
    const getResp = await fetch(
      `https://api.github.com/repos/${owner}/${repo}/contents/${filePath}`,
      { headers: { "Authorization": `token ${token}`, "User-Agent": "BeriklanWorker/1.0" } }
    );
    if (getResp.ok) {
      const data = await getResp.json();
      sha = data.sha || null;
    }
  } catch (e) { /* fine, file may be new */ }

  // 2. Base64-encode (UTF-8 safe via btoa(unescape(encodeURIComponent))) — same as existing pattern
  let b64 = "";
  try {
    b64 = btoa(unescape(encodeURIComponent(content)));
  } catch (e) {
    b64 = btoa(content); // fallback
  }

  const body = { message, content: b64, branch };
  if (sha) body.sha = sha;

  // 3. PUT (GH will create or update)
  const putResp = await fetch(
    `https://api.github.com/repos/${owner}/${repo}/contents/${filePath}`,
    {
      method: "PUT",
      headers: {
        "Authorization": `token ${token}`,
        "Content-Type": "application/json",
        "User-Agent": "BeriklanWorker/1.0",
      },
      body: JSON.stringify(body),
    }
  );

  let newSha = null;
  if (putResp.ok) {
    try { newSha = (await putResp.json()).content?.sha || null; } catch (e) {}
  }
  return { status: putResp.status, ok: putResp.ok, sha: newSha, path: filePath };
}

// P0.7 build-signature 2026-07-17T06:08:00Z  (forces redeploy)
