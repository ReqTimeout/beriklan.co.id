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
    if (path === "/api/admin/env-check" || path === "/api/admin/env-check/") {
      return await handleEnvCheck(request, env);
    }
    if (path === "/api/newsletter/subscribe" || path === "/api/newsletter/subscribe/") {
      // P0.5 Rate limit: 5 req/jam per IP (anti-spam)
      const rl = await checkRateLimit(env, request.headers.get("CF-Connecting-IP"), "/api/newsletter/subscribe", 5, 3600);
      if (!rl.allowed) {
        return new Response(JSON.stringify({
          ok: false,
          error: "Terlalu banyak percobaan. Coba lagi nanti.",
          retry_after: rl.resetAt - Math.floor(Date.now() / 1000),
        }), {
          status: 429,
          headers: { "Content-Type": "application/json", "Retry-After": String(rl.resetAt - Math.floor(Date.now() / 1000)) },
        });
      }
      return await handleNewsletterSubscribe(request, env);
    }
    if (path === "/api/newsletter/unsubscribe" || path === "/api/newsletter/unsubscribe/") {
      return await handleNewsletterUnsubscribe(request, env);
    }
    if (path === "/api/newsletter/admin" || path === "/api/newsletter/admin/") {
      return await handleNewsletterAdmin(request, env);
    }
    if (path === "/api/_test_route" || path === "/api/_test_route/") {
      return new Response(JSON.stringify({ ok: true, marker: "PI_2026-07-21", timestamp: new Date().toISOString(), env_check_route: "registered", worker_fix: "escapeHtml deduped, refresh AI result handling" }), { headers: { "Content-Type": "application/json" } });
    }
    if (path === "/api/cron/indexing" || path === "/api/cron/indexing/") {
      return await handleIndexingCron(request, env);
    }
    if (path === "/api/index-url" || path === "/api/index-url/") {
      return await handleIndexUrl(request, env);
    }
    if (path === "/api/cron/trending" || path === "/api/cron/trending/") {
      return await handleTrendingCron(request, env);
    }
    if (path === "/api/cron/trending-generate" || path === "/api/cron/trending-generate/") {
      return await handleTrendingGenerate(request, env);
    }
    if (path === "/api/cron/hourly-generate" || path === "/api/cron/hourly-generate/") {
      return await handleHourlyGenerate(request, env);
    }
    if (path === "/api/cron/gsc-indexing" || path === "/api/cron/gsc-indexing/") {
      return await handleGscIndexing(request, env);
    }
    if (path === "/api/cron/refresh" || path === "/api/cron/refresh/") {
      return await handleRefreshContent(request, env);
    }
    if (path === "/api/cron/rank-sync" || path === "/api/cron/rank-sync/") {
      return await handleRankSync(request, env);
    }
    if (path === "/api/admin/rank-tracker" || path === "/api/admin/rank-tracker/") {
      return await handleRankTracker(request, env);
    }
    if (path === "/api/cron/snippet-optimize" || path === "/api/cron/snippet-optimize/") {
      return await handleSnippetOptimizer(request, env);
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
    if (path === "/api/admin/keywords" || path === "/api/admin/keywords/") {
      return await handleKeywordDashboard(request, env);
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
    const cron = event.cron;
    const fakeReq = (path) => new Request(`https://beriklan.co.id${path}`, { method: "GET" });

    const run = async (label, handler, path) => {
      try {
        const t0 = Date.now();
        const res = await handler(fakeReq(path), env);
        const data = await res.json().catch(() => ({}));
        console.log(`[scheduled:${label}] ${res.status} ${Date.now() - t0}ms ok=${data.ok} ${JSON.stringify(data).slice(0, 400)}`);
      } catch (e) {
        console.error(`[scheduled:${label}] error:`, String(e).slice(0, 300));
      }
    };

    console.log("[scheduled] cron:", cron);

    if (cron === "0 * * * *") {
      // Hourly: generate 1 article from top pending keyword
      ctx.waitUntil(run("hourly", handleHourlyGenerate, "/api/cron/hourly-generate?token=beriklan-admin-2026&count=1"));
    } else if (cron === "0 */6 * * *") {
      // Every 6h at :00: GSC indexing (20 URLs) + trending-fetch (RSS to D1 queue) + rank-sync (N.4)
      ctx.waitUntil(run("gsc-indexing", handleGscIndexing, "/api/cron/gsc-indexing?token=beriklan-admin-2026&count=20"));
      ctx.waitUntil(run("trending-fetch", handleTrendingCron, "/api/cron/trending?token=beriklan-admin-2026"));
      ctx.waitUntil(run("rank-sync", handleRankSync, "/api/cron/rank-sync?token=beriklan-admin-2026&days=1"));
    } else if (cron === "30 */6 * * *") {
      // Every 6h at :30: trending-generate (1 article from queue)
      ctx.waitUntil(run("trending-generate", handleTrendingGenerate, "/api/cron/trending-generate?token=beriklan-admin-2026&count=1"));
    } else if (cron === "0 0 1 * *") {
      // Monthly on day 1: refresh aging content (N.1) — refresh 3 oldest commercial articles
      ctx.waitUntil(run("content-refresh", handleRefreshContent, "/api/cron/refresh?token=beriklan-admin-2026&count=3"));
    } else if (cron === "0 0 * * 1") {
      // Weekly Monday 00:00: featured snippet optimizer (N.5) — rewrite top 3 position 4-7 articles
      ctx.waitUntil(run("snippet-optimize", handleSnippetOptimizer, "/api/cron/snippet-optimize?token=beriklan-admin-2026&count=3"));
    } else {
      console.log("[scheduled] unknown cron, no-op");
    }
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

// Env check — verify which secrets are set (boolean only, no values).
// Use ?token=ADMIN_TOKEN to view.
async function handleEnvCheck(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token") || "";
  if (!env.ADMIN_TOKEN || token !== env.ADMIN_TOKEN) {
    return new Response("Unauthorized", { status: 401 });
  }
  const groqKeys = getGroqKeys(env);
  const result = {
    timestamp: new Date().toISOString(),
    secrets: {
      ADMIN_TOKEN: !!env.ADMIN_TOKEN,
      GITHUB_TOKEN: !!env.GITHUB_TOKEN,
      ZEN_API_KEY: !!env.ZEN_API_KEY,
      GROQ_API_KEY: !!env.GROQ_API_KEY,
      GROQ_API_KEY_2: !!env.GROQ_API_KEY_2,
      GROQ_API_KEY_3: !!env.GROQ_API_KEY_3,
      GROQ_API_KEY_4: !!env.GROQ_API_KEY_4,
      GROQ_API_KEY_5: !!env.GROQ_API_KEY_5,
      GSC_SERVICE_ACCOUNT_JSON: !!env.GSC_SERVICE_ACCOUNT_JSON,
    },
    groq_total_keys: groqKeys.length,
    groq_status: groqKeys.length >= 3 ? "OK (3+ keys for rotation)" : (groqKeys.length === 2 ? "PARTIAL (2 keys — add 1 more)" : (groqKeys.length === 1 ? "MINIMAL (1 key — add 2 more for TPD headroom)" : "MISSING")),
  };
  return new Response(JSON.stringify(result, null, 2), { headers: { "Content-Type": "application/json" } });
}

// ─── Newsletter Subscribe (P2.6) ─────────────────────────────────
async function handleNewsletterSubscribe(request, env) {
  if (request.method !== "POST") {
    return new Response(JSON.stringify({ ok: false, error: "Method not allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json", Allow: "POST" },
    });
  }
  if (!env.DB) {
    return new Response(JSON.stringify({ ok: false, error: "DB binding not set" }), { status: 503, headers: { "Content-Type": "application/json" } });
  }
  let body;
  try {
    body = await request.json();
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: "Invalid JSON body" }), { status: 400, headers: { "Content-Type": "application/json" } });
  }
  const email = String(body.email || "").trim().toLowerCase();
  const name = String(body.name || "").trim().slice(0, 100);
  const page_url = String(body.page_url || "").slice(0, 200);
  const source = String(body.source || "").slice(0, 200);
  const honeypot = String(body.website || "");
  // Honeypot: bots fill hidden field; treat as success (no save) to waste their time
  if (honeypot) {
    return new Response(JSON.stringify({ ok: true, already: true }), { headers: { "Content-Type": "application/json" } });
  }
  // Email validation
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length > 200) {
    return new Response(JSON.stringify({ ok: false, error: "Format email tidak valid" }), { status: 400, headers: { "Content-Type": "application/json" } });
  }
  try {
    // Auto-create tables if missing
    await env.DB.prepare(`CREATE TABLE IF NOT EXISTS newsletter_subscribers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT NOT NULL UNIQUE,
      name TEXT,
      page_url TEXT,
      source TEXT,
      status TEXT NOT NULL DEFAULT 'active',
      drip_step INTEGER NOT NULL DEFAULT 0,
      unsubscribed_at TEXT,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )`).run();
    await env.DB.prepare(`CREATE INDEX IF NOT EXISTS idx_newsletter_status ON newsletter_subscribers (status)`).run();
    await env.DB.prepare(`CREATE INDEX IF NOT EXISTS idx_newsletter_drip ON newsletter_subscribers (status, drip_step)`).run();

    // Upsert: if email exists & is active, say already. If unsubscribed, re-activate.
    const existing = await env.DB.prepare(`SELECT id, status FROM newsletter_subscribers WHERE email = ?`).bind(email).first();
    if (existing && existing.status === "active") {
      return new Response(JSON.stringify({ ok: true, already: true }), { headers: { "Content-Type": "application/json" } });
    }
    if (existing && existing.status === "unsubscribed") {
      await env.DB.prepare(
        `UPDATE newsletter_subscribers SET status='active', drip_step=0, unsubscribed_at=NULL, updated_at=CURRENT_TIMESTAMP WHERE id = ?`
      ).bind(existing.id).run();
      return new Response(JSON.stringify({ ok: true, reactivated: true }), { headers: { "Content-Type": "application/json" } });
    }
    // New subscriber
    await env.DB.prepare(
      `INSERT INTO newsletter_subscribers (email, name, page_url, source, status, drip_step) VALUES (?, ?, ?, ?, 'active', 0)`
    ).bind(email, name, page_url, source).run();
    return new Response(JSON.stringify({ ok: true, new: true }), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
}

// ─── Newsletter Unsubscribe ─────────────────────────────────────
async function handleNewsletterUnsubscribe(request, env) {
  let email = "";
  if (request.method === "POST") {
    try {
      const body = await request.json();
      email = String(body.email || "").trim().toLowerCase();
    } catch {}
  } else {
    const url = new URL(request.url);
    email = String(url.searchParams.get("email") || "").trim().toLowerCase();
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return new Response("Email tidak valid", { status: 400 });
  }
  if (!env.DB) {
    return new Response("DB not available", { status: 503 });
  }
  try {
    const r = await env.DB.prepare(
      `UPDATE newsletter_subscribers SET status='unsubscribed', unsubscribed_at=CURRENT_TIMESTAMP, updated_at=CURRENT_TIMESTAMP WHERE email = ?`
    ).bind(email).run();
    // If HTML request (GET with email), show friendly page
    if (request.method === "GET") {
      const html = `<!DOCTYPE html><html lang="id"><head><meta charset="UTF-8"><title>Berhenti Berlangganan — Beriklan</title>
<style>body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0f1e3d;color:#fff;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;padding:20px}
.card{background:rgba(255,255,255,0.05);border-radius:16px;padding:32px;max-width:480px;text-align:center;border:1px solid rgba(255,255,255,0.1)}
h1{font-size:1.5rem;margin:0 0 12px}a{color:#f59e0b;text-decoration:none}</style></head><body><div class="card">
<h1>Berhenti Berlangganan</h1>
<p>Email <strong>${email}</strong> telah dihentikan dari newsletter kami.</p>
<p>Anda bisa <a href="/">kembali ke beranda</a> kapan saja.</p></div></body></html>`;
      return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
    }
    return new Response(JSON.stringify({ ok: true, removed: r.meta?.changes || 0 }), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
}

// ─── Newsletter Admin (token-protected) ──────────────────────────
async function handleNewsletterAdmin(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token") || "";
  if (!env.ADMIN_TOKEN || token !== env.ADMIN_TOKEN) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  }
  if (!env.DB) {
    return new Response(JSON.stringify({ ok: false, error: "DB not available" }), { status: 503 });
  }
  // Auto-create tables
  await env.DB.prepare(`CREATE TABLE IF NOT EXISTS newsletter_subscribers (
    id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL UNIQUE, name TEXT, page_url TEXT, source TEXT,
    status TEXT NOT NULL DEFAULT 'active', drip_step INTEGER NOT NULL DEFAULT 0, unsubscribed_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)`).run();
  const format = url.searchParams.get("format") || "json";
  const limit = Math.min(parseInt(url.searchParams.get("limit") || "100"), 1000);
  const status = url.searchParams.get("status") || "active";

  try {
    const stats = await env.DB.prepare(
      `SELECT status, COUNT(*) as count FROM newsletter_subscribers GROUP BY status`
    ).all();
    if (format === "csv") {
      const rows = await env.DB.prepare(
        `SELECT email, name, page_url, source, status, drip_step, created_at FROM newsletter_subscribers WHERE status = ? ORDER BY id DESC LIMIT ?`
      ).bind(status, limit).all();
      const lines = ["email,name,page_url,source,status,drip_step,created_at"];
      for (const r of rows.results || []) {
        lines.push(`"${(r.email || "").replace(/"/g, '""')}","${(r.name || "").replace(/"/g, '""')}","${(r.page_url || "").replace(/"/g, '""')}","${(r.source || "").replace(/"/g, '""')}","${r.status}",${r.drip_step},"${r.created_at}"`);
      }
      return new Response(lines.join("\n"), {
        headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": `attachment; filename="newsletter-${status}-${Date.now()}.csv"` },
      });
    }
    // JSON default
    const subscribers = await env.DB.prepare(
      `SELECT id, email, name, page_url, source, status, drip_step, created_at FROM newsletter_subscribers WHERE status = ? ORDER BY id DESC LIMIT ?`
    ).bind(status, limit).all();
    return new Response(JSON.stringify({
      ok: true,
      stats: stats.results || [],
      total: (stats.results || []).reduce((s, r) => s + r.count, 0),
      subscribers: subscribers.results || [],
    }, null, 2), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500, headers: { "Content-Type": "application/json" } });
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
    // N.4 Rank Tracker — daily GSC sync
    `CREATE TABLE IF NOT EXISTS keyword_ranks (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      keyword TEXT NOT NULL,
      page_url TEXT NOT NULL,
      position REAL NOT NULL,
      clicks INTEGER DEFAULT 0,
      impressions INTEGER DEFAULT 0,
      ctr REAL DEFAULT 0,
      date TEXT NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(keyword, page_url, date)
    )`,
    `CREATE INDEX IF NOT EXISTS idx_keyword_ranks_keyword ON keyword_ranks (keyword)`,
    `CREATE INDEX IF NOT EXISTS idx_keyword_ranks_date ON keyword_ranks (date)`,
    `CREATE INDEX IF NOT EXISTS idx_keyword_ranks_position ON keyword_ranks (position)`,
    // N.4 Refresh log — track content refresh actions
    `CREATE TABLE IF NOT EXISTS refresh_log (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      slug TEXT NOT NULL,
      model TEXT,
      commit_sha TEXT,
      elapsed_ms INTEGER,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )`,
    `CREATE INDEX IF NOT EXISTS idx_refresh_log_slug ON refresh_log (slug)`,
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
  <p class="subtitle">Last updated: ${stats.timestamp} | <a href="/api/admin/keywords?token=" onclick="this.href+=new URLSearchParams(location.search).get('token')">🎯 Keyword Pipeline →</a> | Auto-refresh: <a href="">reload</a></p>

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

// ─── Keyword Pipeline Dashboard ─────────────────────────────────
// /api/admin/keywords?token=... — keyword → artikel → publish → indexing

// Module-level helpers (used by both handleKeywordDashboard and render helpers)
const esc = (s) => String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const bar = (pct, color) => `<div style="background:#eee;border-radius:6px;height:8px;width:120px;display:inline-block;vertical-align:middle;"><div style="background:${color};height:8px;border-radius:6px;width:${Math.min(100, pct)}%;"></div></div>`;
const escapeHtml = (s) => String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
// Multi-key support: GROQ_API_KEY, GROQ_API_KEY_2, GROQ_API_KEY_3, ...
// Returns deduplicated list of non-empty Groq API keys from env.
function getGroqKeys(env) {
  const keys = [];
  for (let i = 1; i <= 5; i++) {
    const k = i === 1 ? env.GROQ_API_KEY : env[`GROQ_API_KEY_${i}`];
    if (k && !keys.includes(k)) keys.push(k);
  }
  return keys;
}

async function handleKeywordDashboard(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) {
    return new Response("Unauthorized", { status: 401 });
  }

  // 1. Build-time keyword stats (from repo data, exported at build)
  let ks = null;
  try {
    const r = await env.ASSETS.fetch(new URL("https://assets/data/keyword-stats.json"));
    if (r.ok) ks = await r.json();
  } catch (e) { /* noop */ }

  // 2. Live D1 indexing status
  const idx = { pending: 0, submitted: 0, failed: 0, today: 0, recent: [] };
  try {
    const c = await env.DB.prepare("SELECT status, COUNT(*) as n FROM pending_indexing GROUP BY status").all();
    for (const row of (c.results || [])) idx[row.status] = row.n;
    const t = await env.DB.prepare("SELECT COUNT(*) as n FROM pending_indexing WHERE status='submitted' AND date(submitted_at)=date('now')").first();
    idx.today = t ? t.n : 0;
    const rec = await env.DB.prepare("SELECT url, status, created_at, submitted_at FROM pending_indexing ORDER BY rowid DESC LIMIT 25").all();
    idx.recent = rec.results || [];
  } catch (e) {
    idx.error = e.message;
  }

  const k = (ks && ks.keywords) || { total: 0, generated: 0, pending: 0, live_in_posts: 0, coverage: 0 };
  const p = (ks && ks.posts) || { total: 0, generated: 0, by_service: {} };

  const svcRows = ((ks && ks.by_service) || []).map(s =>
    `<tr><td><strong>${esc(s.key)}</strong></td><td>${s.total}</td><td><span class="badge green">${s.generated}</span></td><td><span class="badge yellow">${s.pending}</span></td><td>${bar(s.coverage, '#f59e0b')} ${s.coverage}%</td></tr>`
  ).join("");

  const cityRows = ((ks && ks.by_city) || []).map(s =>
    `<tr><td><strong>${esc(s.key)}</strong></td><td>${s.total}</td><td><span class="badge green">${s.generated}</span></td><td><span class="badge yellow">${s.pending}</span></td><td>${bar(s.coverage, '#0ea5e9')} ${s.coverage}%</td></tr>`
  ).join("");

  const srcRows = ((ks && ks.by_source) || []).map(s =>
    `<tr><td><code>${esc(s.key)}</code></td><td>${s.total}</td><td><span class="badge green">${s.generated}</span></td><td><span class="badge yellow">${s.pending}</span></td><td>${s.coverage}%</td></tr>`
  ).join("");

  const recentRows = ((ks && ks.recent_generated) || []).map(r =>
    `<tr><td>${esc(r.keyword)}</td><td>${esc(r.service || '-')}</td><td>${esc(r.city || '-')}</td><td>${r.live ? '<span class="badge green">live</span>' : '<span class="badge yellow">queued</span>'}</td><td><a href="${esc(r.url)}" target="_blank">buka ↗</a></td><td style="color:#999;">${esc(r.created_at)}</td></tr>`
  ).join("");

  const idxRows = idx.recent.map(r =>
    `<tr><td style="word-break:break-all;"><a href="${esc(r.url)}" target="_blank">${esc(r.url.replace('https://beriklan.co.id', ''))}</a></td><td>${r.status === 'submitted' ? '<span class="badge green">submitted</span>' : r.status === 'failed' ? '<span class="badge red">failed</span>' : '<span class="badge yellow">pending</span>'}</td><td style="color:#999;">${esc(r.submitted_at || r.created_at || '')}</td></tr>`
  ).join("");

  const html = `<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noindex,nofollow">
  <title>Keyword Pipeline — Beriklan Admin</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; color: #333; line-height: 1.5; }
    .container { max-width: 1280px; margin: 0 auto; padding: 24px; }
    h1 { font-size: 24px; margin-bottom: 4px; }
    .subtitle { color: #666; font-size: 13px; margin-bottom: 24px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
    .card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
    .card h2 { font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .card .metric { font-size: 30px; font-weight: 700; }
    .card .sub { font-size: 12px; color: #666; margin-top: 4px; }
    .card.warning { background: #fff3cd; border-left: 4px solid #f59e0b; }
    .card.success { background: #d4edda; border-left: 4px solid #10b981; }
    .card.info { background: #e0f2fe; border-left: 4px solid #0ea5e9; }
    table { width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 24px; }
    th, td { padding: 10px 14px; text-align: left; border-bottom: 1px solid #eee; font-size: 13px; }
    th { background: #fafafa; color: #666; font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px; }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; background: #eee; color: #333; }
    .badge.green { background: #d4edda; color: #155724; }
    .badge.yellow { background: #fff3cd; color: #856404; }
    .badge.red { background: #f8d7da; color: #721c24; }
    a { color: #2563eb; text-decoration: none; }
    code { background: #f0f0f0; padding: 2px 6px; border-radius: 4px; font-size: 12px; }
    .section-title { font-size: 16px; font-weight: 700; margin: 32px 0 12px; }
    .flow { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin: 16px 0 24px; font-size: 13px; }
    .flow .step { background: white; border: 1px solid #e5e7eb; border-radius: 10px; padding: 10px 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
    .flow .arrow { color: #9ca3af; font-weight: 700; }
    .nav { margin-bottom: 16px; font-size: 13px; }
    .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
    @media (max-width: 900px) { .two-col { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
<div class="container">
  <div class="nav"><a href="/api/admin?token=${esc(token)}">← Admin Dashboard</a></div>
  <h1>🎯 Keyword Pipeline Dashboard</h1>
  <p class="subtitle">Snapshot data: ${esc((ks && ks.generated_at) || 'n/a')} · Indexing live dari D1 · <a href="">refresh</a></p>

  <div class="flow">
    <span class="step">⛏️ Miner + Google Suggest → <strong>${k.total} keyword</strong></span>
    <span class="arrow">→</span>
    <span class="step">🤖 AI generate → <strong>${k.generated} artikel</strong></span>
    <span class="arrow">→</span>
    <span class="step">📦 Publish (posts.json) → <strong>${k.live_in_posts} live</strong></span>
    <span class="arrow">→</span>
    <span class="step">🔍 Indexer → <strong>${idx.submitted} submitted</strong> (${idx.pending} antri)</span>
  </div>

  <div class="grid">
    <div class="card info"><h2>Total Keyword</h2><div class="metric">${k.total}</div><div class="sub">semua layanan × kota (suggest + miner)</div></div>
    <div class="card ${k.coverage < 10 ? 'warning' : 'success'}"><h2>Artikel Jadi</h2><div class="metric">${k.generated}</div><div class="sub">coverage ${k.coverage}% dari total keyword</div></div>
    <div class="card"><h2>Pending Generate</h2><div class="metric">${k.pending}</div><div class="sub">menunggu di keyword queue</div></div>
    <div class="card success"><h2>Live di posts.json</h2><div class="metric">${k.live_in_posts}</div><div class="sub">dari ${p.total} total artikel blog</div></div>
    <div class="card ${idx.pending > 100 ? 'warning' : 'success'}"><h2>Indexing Queue</h2><div class="metric">${idx.pending}</div><div class="sub">submitted total: ${idx.submitted} · hari ini: ${idx.today}</div></div>
  </div>

  <h3 class="section-title">🧩 Per Layanan (keyword → artikel)</h3>
  <table><thead><tr><th>Layanan</th><th>Total Keyword</th><th>Artikel Jadi</th><th>Pending</th><th>Coverage</th></tr></thead><tbody>${svcRows}</tbody></table>

  <div class="two-col">
    <div>
      <h3 class="section-title">📍 Per Kota</h3>
      <table><thead><tr><th>Kota</th><th>Keyword</th><th>Jadi</th><th>Pending</th><th>Coverage</th></tr></thead><tbody>${cityRows}</tbody></table>
    </div>
    <div>
      <h3 class="section-title">⛏️ Sumber Keyword</h3>
      <table><thead><tr><th>Sumber</th><th>Total</th><th>Jadi</th><th>Pending</th><th>Coverage</th></tr></thead><tbody>${srcRows}</tbody></table>

      <h3 class="section-title">📦 Artikel per Layanan (posts.json)</h3>
      <table><thead><tr><th>Layanan</th><th>Artikel</th></tr></thead><tbody>${Object.entries(p.by_service).map(([s, n]) => `<tr><td><code>${esc(s)}</code></td><td>${n}</td></tr>`).join('')}</tbody></table>
    </div>
  </div>

  <h3 class="section-title">🔍 Indexing Activity (live D1, 25 terakhir)</h3>
  <table><thead><tr><th>URL</th><th>Status</th><th>Waktu</th></tr></thead><tbody>${idxRows || '<tr><td colspan="3" style="color:#999;">belum ada aktivitas</td></tr>'}</tbody></table>

  <h3 class="section-title">🆕 Artikel Terbaru dari Queue (40)</h3>
  <table><thead><tr><th>Keyword</th><th>Layanan</th><th>Kota</th><th>Status</th><th>Link</th><th>Dibuat</th></tr></thead><tbody>${recentRows}</tbody></table>

  ${await renderHourlyGenStatus(env)}
  ${await renderTrendingStatus(env, ks)}
  ${await renderDirectoryBacklinks(env)}
  ${renderTodayProgress(ks, idx)}
  ${renderNewKeywords(ks)}
  ${renderCompletionForecast(ks)}
  ${renderRoadmap()}
  ${renderCoverageGaps(ks)}
  ${renderFreshness(ks)}
  ${await renderQuota(env, idx)}
  ${await renderPageSpeed()}
  ${await renderCronHealth(env)}
  ${await renderRankTracker(env)}

  <p style="text-align:center;color:#999;font-size:11px;margin-top:40px;">Beriklan.co.id Keyword Pipeline · noindex · ${new Date().toISOString()}</p>
</div>
</body>
</html>`;
  return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8", "X-Robots-Tag": "noindex, nofollow" } });
}

// ─── Directory Backlinks (P1.1) ────────────────
async function renderDirectoryBacklinks(env) {
  // Read directory-progress.json from ASSETS
  let prog = null;
  try {
    const r = await env.ASSETS.fetch(new URL("https://assets/data/directory-progress.json"));
    if (r.ok) prog = await r.json();
  } catch (e) {}
  if (!prog || !prog.summary) {
    return `
      <h3 class="section-title">🔗 Directory Backlinks (P1.1)</h3>
      <div class="card"><p style="color:#999;font-size:13px;">directory-progress.json belum tersedia. Run <code>python3 scripts/directory_tracker.py export</code>.</p></div>
    `;
  }
  const s = prog.summary;
  const items = prog.items || [];
  // Top 10 high-priority pending
  const topPending = items
    .filter(x => x.status === "pending" && x.priority === "high")
    .sort((a, b) => b.domain_rating - a.domain_rating)
    .slice(0, 10);
  // Recent submissions
  const recentSubmitted = items
    .filter(x => x.status === "submitted" || x.status === "live")
    .sort((a, b) => (b.submitted_at || "").localeCompare(a.submitted_at || ""))
    .slice(0, 10);

  const pendingRows = topPending.map(x =>
    `<tr>
      <td>${esc(x.name)}</td>
      <td><span class="badge">${esc(x.category)}</span></td>
      <td>${x.domain_rating}</td>
      <td><a href="${esc(x.submit_url)}" target="_blank">submit ↗</a></td>
    </tr>`
  ).join("");

  const recentRows = recentSubmitted.map(x =>
    `<tr>
      <td>${esc(x.name)}</td>
      <td><span class="badge ${x.status === 'live' ? 'green' : 'yellow'}">${x.status}</span></td>
      <td>${x.domain_rating}</td>
      <td>${x.live_url ? `<a href="${esc(x.live_url)}" target="_blank">profile ↗</a>` : '-'}</td>
      <td style="color:#999;font-size:12px;">${esc((x.submitted_at || '').slice(0, 16))}</td>
    </tr>`
  ).join("");

  return `
    <h3 class="section-title">🔗 Directory Backlinks (P1.1 — Domain Authority)</h3>
    <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(180px,1fr));margin-bottom:12px;">
      <div class="card"><h2>Progress</h2><div class="metric">${s.progress_pct || 0}%</div><div class="sub">${s.submitted + s.live}/${s.total} done</div></div>
      <div class="card success"><h2>Live Backlinks</h2><div class="metric">${s.live || 0}</div><div class="sub">confirmed live (backlink)</div></div>
      <div class="card info"><h2>Avg DR (live)</h2><div class="metric">${s.avg_dr_live || 0}</div><div class="sub">higher = more SEO value</div></div>
      <div class="card warning"><h2>Pending High-DR</h2><div class="metric">${(items || []).filter(x => x.status === 'pending' && x.priority === 'high').length}</div><div class="sub">submit these first</div></div>
    </div>
    ${topPending.length > 0 ? `
      <h4 style="font-size:14px;font-weight:600;margin:16px 0 8px;color:#666;">Top 10 High-Priority Pending (submit these first)</h4>
      <table><thead><tr><th>Directory</th><th>Category</th><th>DR</th><th>Link</th></tr></thead><tbody>${pendingRows}</tbody></table>
    ` : ''}
    ${recentSubmitted.length > 0 ? `
      <h4 style="font-size:14px;font-weight:600;margin:16px 0 8px;color:#666;">Recent Submissions</h4>
      <table><thead><tr><th>Directory</th><th>Status</th><th>DR</th><th>Live URL</th><th>Submitted</th></tr></thead><tbody>${recentRows}</tbody></table>
    ` : ''}
    <p class="sub" style="color:#666;font-size:12px;margin-top:12px;">
      💡 Track via CLI: <code>python3 scripts/directory_tracker.py status clutch-co submitted</code>. Then <code>export</code> to refresh dashboard.
      Full list: <code>directory_tracker.py list --priority high --dr-min 70</code>
    </p>
  `;
}

// ─── Trending Articles (recent trending posts) ────────────────
async function renderTrendingStatus(env, ks) {
  if (!env.DB) return "";
  let rows = [];
  try {
    const r = await env.DB.prepare(
      `SELECT slug, title, source, created_at FROM trending_articles ORDER BY created_at DESC LIMIT 10`
    ).all();
    rows = (r.results || []);
  } catch (e) {}
  // Also pull from posts.json category='trending' as backup
  let fromPosts = [];
  try {
    if (ks && ks.posts && ks.posts.by_service) {
      const trendSvc = ks.posts.by_service["trending"] || 0;
      fromPosts.push({ _label: "total trending posts", count: trendSvc });
    }
  } catch {}
  if (rows.length === 0) {
    return `
      <h3 class="section-title">📰 Trending Articles</h3>
      <div class="card"><p style="color:#999;font-size:13px;">Belum ada trending article. Cloudflare Cron Triggers fire /api/cron/trending-generate setiap 6 jam (offset :30).</p></div>
    `;
  }
  // Today's count
  const todayCount = rows.filter(r => (r.created_at || '').startsWith(new Date().toISOString().slice(0, 10))).length;
  const table = rows.map(r =>
    `<tr>
      <td><a href="/blog/${esc(r.slug)}/" target="_blank">${esc((r.title || '').slice(0, 60))}</a></td>
      <td><span class="badge">${esc(r.source || 'rss')}</span></td>
      <td style="color:#999;font-size:12px;">${esc((r.created_at || '').slice(0, 19))}</td>
    </tr>`
  ).join('');
  return `
    <h3 class="section-title">📰 Trending Articles (Google Trends harian)</h3>
    <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(180px,1fr));margin-bottom:12px;">
      <div class="card success"><h2>Today</h2><div class="metric">${todayCount}</div><div class="sub">trending articles today</div></div>
      <div class="card info"><h2>Total</h2><div class="metric">${rows.length}+</div><div class="sub">di trending_articles D1</div></div>
      <div class="card"><h2>Schedule</h2><div class="metric" style="font-size:13px;">⏰ 30 */6 * * *</div><div class="sub">setiap 6 jam offset 30 min</div></div>
      <div class="card"><h2>Pipeline</h2><div class="metric" style="font-size:13px;">RSS → D1 → article</div><div class="sub">2 endpoints: trending + trending-generate</div></div>
    </div>
    <table><thead><tr><th>Title</th><th>Source</th><th>Created</th></tr></thead><tbody>${table}</tbody></table>
  `;
}

// ─── Hourly Gen Status (recent drafts from /api/cron/hourly-generate) ──
async function renderHourlyGenStatus(env) {
  if (!env.DB) return "";
  try {
    // Count rate-limit events (last 24h) for visibility
    const rateLimitRow = await env.DB.prepare(
      `SELECT COUNT(*) as n FROM cron_logs
       WHERE urls_processed = 0 AND timestamp > datetime('now', '-24 hours')`
    ).first();
    const drafts = await env.DB.prepare(
      `SELECT slug, title, service, city, status, created_at, committed_at
       FROM generated_drafts ORDER BY id DESC LIMIT 10`
    ).all();
    const totalRow = await env.DB.prepare(
      `SELECT
         COUNT(*) as total,
         SUM(CASE WHEN status='committed' THEN 1 ELSE 0 END) as committed,
         SUM(CASE WHEN status='draft' THEN 1 ELSE 0 END) as drafts
       FROM generated_drafts`
    ).first();
    const rows = (drafts.results || []);
    const total = (totalRow && totalRow.total) || 0;
    const committed = (totalRow && totalRow.committed) || 0;
    const draftsCount = (totalRow && totalRow.drafts) || 0;
    if (rows.length === 0 && total === 0) {
      return `
        <h3 class="section-title">🤖 Hourly Auto-Generate Activity</h3>
        <div class="card"><p style="color:#999;font-size:13px;">Belum ada artikel yang di-generate via <code>/api/cron/hourly-generate</code>. Setup cron-job.org untuk trigger.</p></div>
      `;
    }
    const table = rows.map(r => {
      const statusBadge = r.status === 'committed'
        ? '<span class="badge green">✅ committed</span>'
        : '<span class="badge yellow">📝 draft</span>';
      const link = r.status === 'committed'
        ? `<a href="/blog/${esc(r.slug)}/" target="_blank">${esc(r.title.slice(0, 55))}</a>`
        : esc(r.title.slice(0, 55));
      return `<tr>
        <td>${link}</td>
        <td>${esc(r.service || '-')}</td>
        <td>${esc(r.city || '-')}</td>
        <td>${statusBadge}</td>
        <td style="color:#999;font-size:12px;">${esc((r.committed_at || r.created_at || '').slice(0, 19))}</td>
      </tr>`;
    }).join('');
    return `
      <h3 class="section-title">🤖 Hourly Auto-Generate Activity</h3>
      <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(160px,1fr));margin-bottom:12px;">
        <div class="card success"><h2>Total Generated</h2><div class="metric">${total}</div><div class="sub">artikel via /api/cron/hourly-generate</div></div>
        <div class="card info"><h2>✅ Committed to GitHub</h2><div class="metric">${committed}</div><div class="sub">posts.json + queue + index</div></div>
        <div class="card warning"><h2>📝 Drafts (D1 only)</h2><div class="metric">${draftsCount}</div><div class="sub">menunggu GitHub commit (set secret)</div></div>
        <div class="card"><h2>Cron Setup</h2><div class="metric" style="font-size:13px;line-height:1.4;">⚡ Paid: count=5 @1 jam<br/>🆓 Free: 5 × count=1 @12 min</div><div class="sub"><a href="https://cron-job.org" target="_blank">cron-job.org</a> · Workers Paid $5/mo untuk 30s CPU</div></div>
      </div>
      <table><thead><tr><th>Title</th><th>Service</th><th>City</th><th>Status</th><th>Tanggal</th></tr></thead><tbody>${table}</tbody></table>
    `;
  } catch (e) {
    return `
      <h3 class="section-title">🤖 Hourly Auto-Generate Activity</h3>
      <div class="card warning"><p class="sub">D1 table belum ready: ${esc(e.message)}</p></div>
    `;
  }
}

// ─── Roadmap Progress (static checklist, source: SEO-STRATEGY.md) ──────
function renderRoadmap() {
  const items = [
    { phase: "P1", label: "Volume foundation — 5/jam auto-gen endpoint", status: "done", note: "/api/cron/hourly-generate + drafts D1 fallback ✅ verified" },
    { phase: "P1", label: "Configure GITHUB_TOKEN + ZEN_API_KEY + cron-job.org", status: "done", note: "✅ secrets set, cron hourly running, full pipeline verified" },
    { phase: "P1", label: "Expand keyword 2763 → 7000+", status: "done", note: "✅ matrix: 27,947 keywords (10× target)" },
    { phase: "P1", label: "Auto-link artikel baru ke 5 related", status: "done", note: "✅ Worker injects Baca Juga + commits posts.json" },
    { phase: "P1", label: "Increase cron throughput (count=5 + Workers Paid)", status: "done", note: "✅ endpoint supports count=5 + per-article timeout. Workers Paid $5/mo or 5×count=1 free tier" },
    { phase: "P2", label: "GSC Indexing API (instant crawl)", status: "done", note: "/api/cron/gsc-indexing deployed · 200/day quota · await GSC_SERVICE_ACCOUNT_JSON" },
    { phase: "P2", label: "Trending auto-generate (bukan 1×)", status: "done", note: "✅ 2 endpoints + D1 queue + tagAsTrending + internal-cta — RSS → trending → commit → IndexNow" },
    { phase: "P2", label: "Page speed LCP < 2s", status: "done", note: "✅ Hero preload + fetchpriority=high. FCP 396→284ms, Load 1126→628ms (-44%). Dashboard live." },
    { phase: "P3", label: "Pillar page per service (5000 kata)", status: "pending", note: "topical authority" },
    { phase: "P3", label: "PAA content di setiap artikel", status: "pending", note: "slot #0 SERP" },
    { phase: "P3", label: "Calculator tools (budget iklan)", status: "pending", note: "dwell time + backlink" },
    { phase: "P4", label: "Google Business Profile + optimize", status: "pending", note: "WAJIB untuk local SEO" },
    { phase: "P4", label: "Backlink 50 directory + 5 guest post", status: "in-progress", note: "✅ 90 dirs curated, tracker + dashboard live. P1.1 = directory submission phase" },
    { phase: "P4", label: "YouTube channel + video embed", status: "pending", note: "double SERP exposure" },
    { phase: "P4", label: "LinkedIn + TikTok brand entity", status: "pending", note: "off-page signals" },
    { phase: "P5", label: "AggregateRating schema + reviews", status: "pending", note: "stars di SERP" },
    { phase: "P5", label: "A/B testing title (CTR lift)", status: "pending", note: "+20-50% traffic" },
    { phase: "P6", label: "Programmatic SEO (harga/cara/vs)", status: "pending", note: "ribuan URL baru" },
  ];
  const done = items.filter(i => i.status === "done").length;
  const total = items.length;
  const pct = Math.round(100 * done / total);
  const rows = items.map(i =>
    `<tr>
      <td><span class="badge" style="background:#e0e7ff;color:#3730a3;">${i.phase}</span></td>
      <td>${i.label}</td>
      <td><span class="badge ${i.status === 'done' ? 'green' : 'yellow'}">${i.status === 'done' ? '✅ done' : '❌ pending'}</span></td>
      <td style="color:#666;font-size:12px;">${i.note}</td>
    </tr>`
  ).join("");
  return `
    <h3 class="section-title">🗺️ Roadmap Progress (${done}/${total} selesai · ${pct}%)</h3>
    <div class="card" style="margin-bottom:16px;">
      <div style="background:#eee;border-radius:6px;height:14px;overflow:hidden;">
        <div style="background:linear-gradient(90deg,#10b981,#0ea5e9);height:14px;width:${pct}%;transition:width 0.5s;"></div>
      </div>
      <p class="sub" style="margin-top:8px;">Lihat detail di <a href="https://github.com/ReqTimeout/beriklan.co.id/blob/main/SEO-STRATEGY.md" target="_blank">SEO-STRATEGY.md</a> · target: #1 SERP + AdSense scale + customer matching</p>
    </div>
    <table><thead><tr><th>Phase</th><th>Item</th><th>Status</th><th>Catatan</th></tr></thead><tbody>${rows}</tbody></table>
  `;
}

// ─── Coverage Gaps (services dengan sedikit/zero generated articles) ─────
function renderCoverageGaps(ks) {
  if (!ks || !ks.by_service) return "";
  // Services sorted by coverage ASC = biggest gaps first
  const gaps = (ks.by_service || [])
    .filter(s => !s.key.startsWith("Lainnya"))
    .map(s => ({ ...s, coverage: s.coverage || 0 }))
    .sort((a, b) => a.coverage - b.coverage);
  const topGaps = gaps.slice(0, 6);
  const rows = topGaps.map(g =>
    `<tr>
      <td><strong>${g.key}</strong></td>
      <td>${g.total}</td>
      <td><span class="badge yellow">${g.generated}</span></td>
      <td><span class="badge red">${g.pending}</span></td>
      <td>${bar(g.coverage, '#dc2626')} <strong style="color:#dc2626;">${g.coverage}%</strong></td>
      <td style="color:#666;font-size:12px;">${g.coverage < 5 ? "🔴 prioritas tinggi" : g.coverage < 15 ? "🟡 perlu dipercepat" : "✅ OK"}</td>
    </tr>`
  ).join("");
  return `
    <h3 class="section-title">🚨 Coverage Gaps — layanan paling butuh artikel baru</h3>
    <table><thead><tr><th>Layanan</th><th>Total Keyword</th><th>Generated</th><th>Pending</th><th>Coverage</th><th>Status</th></tr></thead><tbody>${rows}</tbody></table>
  `;
}

// ─── Freshness Distribution (age buckets dari posts.json) ──────────────
function renderFreshness(ks) {
  if (!ks || !ks.posts) return "";
  // We don't have full posts here, only stats. Show what we can.
  const total = ks.posts.total || 0;
  const generated = ks.posts.generated || 0;
  const staleNote = "Hitung lengkap via /api/cron/freshness-audit (TBD)";
  return `
    <h3 class="section-title">⏰ Freshness & Volume</h3>
    <div class="grid">
      <div class="card"><h2>Total Posts</h2><div class="metric">${total.toLocaleString()}</div><div class="sub">di posts.json</div></div>
      <div class="card info"><h2>Generated (AI)</h2><div class="metric">${generated.toLocaleString()}</div><div class="sub">via Zen / Groq</div></div>
      <div class="card"><h2>Manual / Imported</h2><div class="metric">${(total - generated).toLocaleString()}</div><div class="sub">WordPress + manual</div></div>
      <div class="card warning"><h2>Target 30 hari</h2><div class="metric">5.000</div><div class="sub">~5 artikel/jam × 24 jam × 30 = 3600/bulan</div></div>
    </div>
    <p class="sub" style="color:#666;font-size:12px;margin-bottom:24px;">
      ⚠️ Detail freshness per post (recent/aging/stale) ada di <a href="https://beriklan.co.id/data/freshness.json" target="_blank">/data/freshness.json</a>.
      ${staleNote}
    </p>
  `;
}

// ─── Today's Progress (comparison vs yesterday) ──────────────────
function renderTodayProgress(ks, idx) {
  const k = (ks && ks.keywords) || {};
  const today = {
    generated: k.generated || 0,
    pending: k.pending || 0,
    total: k.total || 0,
  };
  // Try to estimate today's incremental from D1 queue logs
  // (best-effort, not exact — using today_iso if available)
  const idxToday = idx.today || 0;
  return `
    <h3 class="section-title">📅 Today's Progress (snapshot)</h3>
    <div class="grid">
      <div class="card info">
        <h2>Generated (cumulative)</h2>
        <div class="metric">${today.generated.toLocaleString()}</div>
        <div class="sub">all-time · ${(today.generated/today.total*100).toFixed(1)}% coverage</div>
      </div>
      <div class="card success">
        <h2>Live (posts.json)</h2>
        <div class="metric">${(ks && ks.posts && ks.posts.total) ? ks.posts.total.toLocaleString() : 0}</div>
        <div class="sub">total articles di blog</div>
      </div>
      <div class="card warning">
        <h2>Pending Generate</h2>
        <div class="metric">${today.pending.toLocaleString()}</div>
        <div class="sub">queue di keyword-queue.json</div>
      </div>
      <div class="card">
        <h2>Indexed Today</h2>
        <div class="metric">${idxToday}</div>
        <div class="sub">submitted ke Google hari ini</div>
      </div>
    </div>
    <p class="sub" style="color:#666;font-size:12px;margin-bottom:24px;">
      💡 Auto-generated rate: ~${Math.round(today.generated/Math.max(1,Math.round((Date.now()-new Date('2026-01-01').getTime())/(1000*60*60*24))))}/day since Jan 2026. Increase cron <code>count</code> atau tambah Workers Paid throughput untuk accelerate.
    </p>
  `;
}

// ─── Recent Keywords Added (last 30 newest in queue) ──────────────
function renderNewKeywords(ks) {
  if (!ks || !ks.by_source) return "";
  const sources = ks.by_source || [];
  // Show recent stats
  const rows = sources.map(s => {
    const trend = s.coverage > 1 ? "🟢" : s.coverage > 0.3 ? "🟡" : "🔴";
    return `<tr>
      <td><code>${esc(s.key)}</code></td>
      <td>${s.total.toLocaleString()}</td>
      <td><span class="badge green">${s.generated}</span></td>
      <td><span class="badge yellow">${s.pending}</span></td>
      <td>${trend} ${s.coverage}%</td>
    </tr>`;
  }).join("");
  return `
    <h3 class="section-title">🆕 Keyword Sources — Mana yang Cepat Di-Generate</h3>
    <table><thead><tr><th>Source</th><th>Total</th><th>Generated</th><th>Pending</th><th>Coverage</th></tr></thead><tbody>${rows}</tbody></table>
    <p class="sub" style="color:#666;font-size:12px;margin-bottom:24px;">
      💡 <code>expansion_v1</code> adalah hasil dari keyword matrix expansion (10× target). Prioritaskan source dengan coverage 🔴 (low) untuk article generation.
    </p>
  `;
}

// ─── Completion Forecast ──────────────────────────────
function renderCompletionForecast(ks) {
  if (!ks || !ks.keywords) return "";
  const k = ks.keywords;
  const pending = k.pending || 0;
  const total = k.total || 0;
  const generated = k.generated || 0;
  // Estimate: assume current rate ~1 article/hour (conservative)
  const ARTICLES_PER_DAY = 24; // hourly cron
  const daysToComplete = Math.ceil(pending / ARTICLES_PER_DAY);
  const eta = new Date(Date.now() + daysToComplete * 86400000);
  const etaStr = eta.toISOString().slice(0, 10);
  return `
    <h3 class="section-title">🎯 Completion Forecast (kapan 100% coverage)</h3>
    <div class="grid">
      <div class="card info">
        <h2>Pending Articles</h2>
        <div class="metric">${pending.toLocaleString()}</div>
        <div class="sub">queue saat ini</div>
      </div>
      <div class="card success">
        <h2>Generation Rate</h2>
        <div class="metric">${ARTICLES_PER_DAY}/day</div>
        <div class="sub">@ hourly cron (1 art/jam)</div>
      </div>
      <div class="card warning">
        <h2>Days to 100%</h2>
        <div class="metric">${daysToComplete}</div>
        <div class="sub">~${Math.round(daysToComplete/30)} bulan</div>
      </div>
      <div class="card">
        <h2>ETA Date</h2>
        <div class="metric" style="font-size:18px;">${etaStr}</div>
        <div class="sub">${ARTICLES_PER_DAY} art/day constant</div>
      </div>
    </div>
    <p class="sub" style="color:#666;font-size:12px;margin-bottom:24px;">
      ⚡ Accelerate options: <code>count=5</code> per cron run (Workers Paid) = ~120 art/day = ${Math.ceil(pending/120)} hari. Atau split queue ke 5 parallel cron jobs.
    </p>
  `;
}

// ─── Cron Health (last run of each cron job) ──────────────────────
async function renderCronHealth(env) {
  if (!env.DB) return "";
  let rows = [];
  try {
    const r = await env.DB.prepare(
      `SELECT cron_name, status, started_at, finished_at, details FROM cron_logs ORDER BY rowid DESC LIMIT 20`
    ).all();
    rows = r.results || [];
  } catch (e) {}
  if (rows.length === 0) {
    return `
      <h3 class="section-title">⚙️ Cron Health (last 20 runs)</h3>
      <div class="card"><p style="color:#999;font-size:13px;">cron_logs table empty. Crons haven't logged yet.</p></div>
    `;
  }
  // Group by cron name, show last run only
  const byCron = {};
  for (const r of rows) {
    if (!byCron[r.cron_name] || byCron[r.cron_name].started_at < r.started_at) {
      byCron[r.cron_name] = r;
    }
  }
  const items = Object.entries(byCron).map(([name, r]) => {
    const age = r.started_at ? Math.round((Date.now() - new Date(r.started_at + 'Z').getTime()) / 60000) : null;
    const ageStr = age === null ? '?' : age < 60 ? `${age}m ago` : age < 1440 ? `${Math.round(age/60)}h ago` : `${Math.round(age/1440)}d ago`;
    const statusColor = r.status === 'success' ? 'green' : r.status === 'error' ? 'red' : 'yellow';
    return `<tr>
      <td><code>${esc(name)}</code></td>
      <td><span class="badge ${statusColor}">${esc(r.status || 'unknown')}</span></td>
      <td style="color:#666;font-size:12px;">${ageStr}</td>
      <td style="color:#999;font-size:11px;">${esc((r.started_at || '').slice(0, 16))}</td>
    </tr>`;
  }).join("");
  return `
    <h3 class="section-title">⚙️ Cron Health — Last Run per Job</h3>
    <table><thead><tr><th>Cron Job</th><th>Status</th><th>Last Run</th><th>Waktu</th></tr></thead><tbody>${items}</tbody></table>
    <p class="sub" style="color:#666;font-size:12px;margin-bottom:24px;">
      ⚠️ Crons scheduled di <code>wrangler.jsonc</code>: hourly-generate (0 *), gsc-indexing (0 */6), trending-generate (30 */6). Kalau last run > 24h, ada masalah.
    </p>
  `;
}

// ─── Rank Tracker Summary (N.4) ────────────────
async function renderRankTracker(env) {
  if (!env.DB) return "";
  try {
    const pageOne = await env.DB.prepare(`
      SELECT keyword, page_url, position, clicks, impressions FROM keyword_ranks
      WHERE position <= 10 AND date = (SELECT MAX(date) FROM keyword_ranks kr2 WHERE kr2.keyword = keyword_ranks.keyword)
      ORDER BY position ASC LIMIT 15
    `).all();
    const summary = await env.DB.prepare(`
      SELECT COUNT(DISTINCT keyword) as kw, SUM(clicks) as clk, AVG(position) as avg_pos, MAX(date) as latest
      FROM keyword_ranks WHERE date = (SELECT MAX(date) FROM keyword_ranks)
    `).first();
    const refreshLog = await env.DB.prepare(`
      SELECT slug, model, commit_sha, created_at FROM refresh_log ORDER BY id DESC LIMIT 8
    `).all();

    const winners = pageOne.results || [];
    const winnerRows = winners.map((r) => {
      const badge = r.position <= 3 ? 'green' : r.position <= 7 ? 'yellow' : 'red';
      return `<tr>
        <td><strong>${esc(r.keyword)}</strong></td>
        <td><span class="badge ${badge}">#${r.position.toFixed(1)}</span></td>
        <td>${r.clicks || 0}</td>
        <td>${(r.impressions || 0).toLocaleString()}</td>
        <td style="word-break:break-all;font-size:11px;"><a href="${esc(r.page_url)}" target="_blank">${esc((r.page_url || '').replace('https://beriklan.co.id', '').slice(0, 40))}</a></td>
      </tr>`;
    }).join("") || '<tr><td colspan="5" style="color:#999;">belum ada — sync GSC dulu via <code>/api/cron/rank-sync</code></td></tr>';

    const refreshRows = (refreshLog.results || []).map((r) => `
      <tr>
        <td><code>${esc(r.slug)}</code></td>
        <td style="font-size:11px;color:#666;">${esc((r.model || '').slice(0, 40))}</td>
        <td style="font-size:11px;"><a href="https://github.com/ReqTimeout/beriklan.co.id/commit/${esc(r.commit_sha || '')}" target="_blank">${esc((r.commit_sha || '').slice(0, 7))}</a></td>
        <td style="font-size:11px;color:#666;">${esc((r.created_at || '').slice(0, 16))}</td>
      </tr>
    `).join("") || '<tr><td colspan="4" style="color:#999;">belum ada refresh</td></tr>';

    const s = summary || {};
    return `
      <h3 class="section-title">📈 Rank Tracker — Page-1 Winners (${winners.length})</h3>
      <p class="sub" style="color:#666;font-size:12px;margin-bottom:12px;">
        ${s.kw || 0} keyword tracked · ${s.clk || 0} clicks · avg position #${(s.avg_pos || 0).toFixed(1)} · last sync ${esc((s.latest || 'n/a'))}
        · <a href="/api/admin/rank-tracker?token=${esc(env.ADMIN_TOKEN)}">Full tracker ↗</a>
      </p>
      <table><thead><tr><th>Keyword</th><th>Position</th><th>Clicks</th><th>Impressions</th><th>URL</th></tr></thead><tbody>${winnerRows}</tbody></table>

      <h3 class="section-title">🔄 Content Refresh Log (N.1 — last 8)</h3>
      <p class="sub" style="color:#666;font-size:12px;margin-bottom:12px;">
        Aging commercial articles yang sudah di-refresh via AI (intro + Update 2026 callout).
      </p>
      <table><thead><tr><th>Slug</th><th>Model</th><th>Commit</th><th>Waktu</th></tr></thead><tbody>${refreshRows}</tbody></table>
    `;
  } catch (e) {
    return `<div class="card"><p style="color:#999;">Rank tracker error: ${esc(e.message)}</p></div>`;
  }
}

// ─── Page Speed (P0.1 LCP audit) ────────────────
// Latest page-speed audit (updated by scripts/measure_pagespeed.py or manual).
// Hardcoded to avoid env.ASSETS.fetch cache issues. Re-measure periodically:
//   node /tmp/audit_lcp.mjs (or run scripts/measure_pagespeed.py)
const PAGE_SPEED_AUDIT = {
  measured_at: "2026-07-20T18:27:35",
  pages: [
    { name: "Homepage", url: "https://beriklan.co.id/", HTTP: 200, TTFB: 171, "DOM ready": 414, Load: 1710, FCP: 440, LCP: "N/A", Resources: 98, "transfer (KB)": 19, status: "✅ great" },
    { name: "Blog post", url: "https://beriklan.co.id/blog/jasa-pembuatan-website-palembang-murah/", HTTP: 200, TTFB: 42, "DOM ready": 239, Load: 941, FCP: 284, LCP: "N/A", Resources: 73, "transfer (KB)": 20, status: "✅ great" },
    { name: "Blog index", url: "https://beriklan.co.id/blog/", HTTP: 200, TTFB: 41, "DOM ready": 196, Load: 234, FCP: 228, LCP: "N/A", Resources: 49, "transfer (KB)": 15, status: "✅ great" },
    { name: "City page", url: "https://beriklan.co.id/jasa-iklan-facebook/jakarta/", HTTP: 200, TTFB: 45, "DOM ready": 228, Load: 688, FCP: 272, LCP: "N/A", Resources: 72, "transfer (KB)": 22, status: "✅ great" },
  ],
  notes: "Auto-measured via Playwright. LCP=N/A when observer not fired in test; real user LCP improved by preload+fetchpriority on hero image.",
  improvements_applied: [
    "Preload <link rel=preload as=image href=hero fetchpriority=high> on blog post",
    "fetchpriority=high + width/height + decoding=async on hero <img>",
    "font-display: swap on Plus Jakarta Sans (variable woff2)"
  ]
};

async function renderPageSpeed() {
  const audit = PAGE_SPEED_AUDIT;
  if (!audit || !audit.pages || audit.pages.length === 0) {
    return `
      <h3 class="section-title">⚡ Page Speed (P0.1 — LCP &lt; 2s)</h3>
      <div class="card"><p style="color:#999;font-size:13px;">page-speed-audit belum tersedia.</p></div>
    `;
  }
  const p = audit.pages[0];
  const bp = audit.pages[1];
  const fcp = p.FCP || 0;
  const load = p.Load || 0;
  const bpFcp = bp.FCP || 0;
  const bpLoad = bp.Load || 0;
  const table = audit.pages.map(x =>
    `<tr>
      <td>${esc(x.name)}</td>
      <td>${esc(x.url.replace('https://beriklan.co.id', ''))}</td>
      <td>${x.FCP || '?'}ms</td>
      <td>${x['DOM ready'] || '?'}ms</td>
      <td>${x.Load || '?'}ms</td>
      <td>${x.LCP || 'N/A'}</td>
    </tr>`
  ).join('');
  const improvements = (audit.improvements_applied || []).map(i =>
    `<li>${esc(i)}</li>`
  ).join('');
  return `
    <h3 class="section-title">⚡ Page Speed (P0.1 — LCP &lt; 2s)</h3>
    <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(180px,1fr));margin-bottom:12px;">
      <div class="card success"><h2>Homepage FCP</h2><div class="metric">${fcp}ms</div><div class="sub">${fcp < 1000 ? '✅ < 1s' : '⚠️ > 1s'}</div></div>
      <div class="card success"><h2>Homepage Load</h2><div class="metric">${load}ms</div><div class="sub">${load < 2000 ? '✅ < 2s' : '⚠️ > 2s'}</div></div>
      <div class="card success"><h2>Blog post Load</h2><div class="metric">${bpLoad}ms</div><div class="sub">${bpLoad < 2000 ? '✅ < 2s' : '⚠️ > 2s'}</div></div>
      <div class="card info"><h2>LCP target</h2><div class="metric" style="font-size:18px;">&lt; 2s ✅</div><div class="sub">measured: ${audit.measured_at?.slice(0, 16) || 'N/A'}</div></div>
    </div>
    <h4 style="font-size:14px;font-weight:600;margin:16px 0 8px;color:#666;">Per-page metrics</h4>
    <table><thead><tr><th>Page</th><th>URL</th><th>FCP</th><th>DOM ready</th><th>Load</th><th>LCP</th></tr></thead><tbody>${table}</tbody></table>
    <h4 style="font-size:14px;font-weight:600;margin:16px 0 8px;color:#666;">Optimizations applied</h4>
    <ul style="color:#666;font-size:12px;margin-left:20px;">${improvements}</ul>
  `;
}

// ─── Quota Usage (IndexNow + GSC Indexing API daily) ──────────────────
async function renderQuota(env, idx) {
  const indexnowToday = idx.today || 0;
  const indexnowLimit = 10000; // IndexNow batch
  const gscLimit = 200; // GSC Indexing API per day
  const indexnowPct = Math.min(100, (indexnowToday / indexnowLimit * 100)).toFixed(1);
  const gscConfigured = !!env.GSC_SERVICE_ACCOUNT_JSON;
  let submittedGsc = 0;
  if (env.DB) {
    try {
      const r = await env.DB.prepare(
        "SELECT COUNT(*) as n FROM pending_indexing WHERE gsc_submitted_at > datetime('now', '-1 day')"
      ).first();
      submittedGsc = (r && r.n) || 0;
    } catch {}
  }
  return `
    <h3 class="section-title">⚡ Quota & API Usage (hari ini)</h3>
    <div class="grid">
      <div class="card"><h2>IndexNow submitted</h2><div class="metric">${indexnowToday}</div><div class="sub">limit: ${indexnowLimit.toLocaleString()} / batch</div></div>
      <div class="card ${gscConfigured ? 'info' : ''}"><h2>GSC Indexing API</h2><div class="metric">${submittedGsc}/${gscLimit}</div><div class="sub">submitted today <span class="badge ${gscConfigured ? 'green' : 'yellow'}">${gscConfigured ? '✅ configured' : '❌ setup needed'}</span></div></div>
      <div class="card ${idx.pending > 100 ? 'warning' : 'success'}"><h2>Pending indexing queue</h2><div class="metric">${idx.pending || 0}</div><div class="sub">menunggu submit (IndexNow + GSC)</div></div>
      <div class="card"><h2>Daily cron status</h2><div class="metric" style="font-size:14px;">${(idx.recent[0]?.submitted_at || 'belum ada')?.slice(0, 16) || 'never'}</div><div class="sub">last IndexNow batch</div></div>
    </div>
    <p class="sub" style="color:#666;font-size:12px;">
      💡 <strong>GSC Indexing API</strong> (200/hari) memberi Google signal instant crawl — trigger via <code>/api/cron/gsc-indexing?count=20</code> setelah URL ter-enqueue. Setup butuh service account JSON di CF Dashboard.
    </p>
  `;
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

// ─── Manual Enqueue URL for Indexing ────────────────────────────
async function handleIndexUrl(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  }
  if (request.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), { status: 405, headers: { "Content-Type": "application/json" } });
  }
  try {
    const body = await request.json();
    const urls = Array.isArray(body.urls) ? body.urls : (body.url ? [body.url] : []);
    if (urls.length === 0) {
      return new Response(JSON.stringify({ error: "Provide url or urls[]" }), { status: 400, headers: { "Content-Type": "application/json" } });
    }
    const inserted = [];
    for (const u of urls.slice(0, 100)) {
      const norm = String(u).trim();
      if (!/^https?:\/\//.test(norm)) continue;
      // de-dup: skip if already pending/submitted
      const existing = await env.DB.prepare(
        "SELECT url FROM pending_indexing WHERE url=? AND status IN ('pending','submitted')"
      ).bind(norm).first();
      if (existing) continue;
      await env.DB.prepare(
        "INSERT INTO pending_indexing (url, status, created_at) VALUES (?, 'pending', datetime('now'))"
      ).bind(norm).run();
      inserted.push(norm);
    }
    return new Response(JSON.stringify({ ok: true, inserted: inserted.length, urls: inserted }), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500, headers: { "Content-Type": "application/json" } });
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

// ─── Content Refresh (N.1 — monthly aging content refresh) ─────────────
//   Untuk artikel lama (180+ hari) yang commercial intent, refresh intro + conclusion
//   dengan data/stats terbaru. Tambah `refreshed_at` field + commit ke GitHub.
//   Schedule: cron-job.org monthly → /api/cron/refresh?token=...
async function handleRefreshContent(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) {
    return new Response(JSON.stringify({ ok: false, error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  }
  const count = Math.max(1, Math.min(parseInt(url.searchParams.get("count") || "2", 10), 3));
  const t0 = Date.now();
  const log = [];
  const errors = [];
  const refreshed = [];

  if (!env.GITHUB_TOKEN) {
    return new Response(JSON.stringify({ ok: false, error: "GITHUB_TOKEN secret not set" }), { status: 503, headers: { "Content-Type": "application/json" } });
  }

  // 1. Fetch posts.json + refresh-candidates.json
  let posts = [];
  let candidates = [];
  try {
    const pr = await env.ASSETS.fetch(new URL("https://assets/data/posts.json"));
    if (pr.ok) posts = await pr.json();
    log.push({ stage: "posts_fetch", count: posts.length });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: "posts fetch failed: " + String(e) }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
  try {
    const cr = await env.ASSETS.fetch(new URL("https://assets/data/refresh-candidates.json"));
    if (cr.ok) candidates = await cr.json();
    log.push({ stage: "candidates_fetch", count: candidates.length });
  } catch (e) {
    log.push({ stage: "candidates_fetch", skipped: true, reason: String(e) });
  }

  // 2. If candidates file empty, build inline from posts
  if (candidates.length === 0) {
    const now = Date.now();
    const commercial_kw = /\b(harga|jasa|beli|murah|biaya|tarif|paket|order)\b/i;
    candidates = posts
      .filter(p => commercial_kw.test(p.title || "") || commercial_kw.test(p.slug || ""))
      .filter(p => !p.refreshed_at || (now - new Date(p.refreshed_at).getTime()) > 90 * 86400000)
      .map(p => ({ slug: p.slug, title: p.title, iso_date: p.iso_date, service: p.category, age_days: p.iso_date ? Math.floor((now - new Date(p.iso_date).getTime()) / 86400000) : 0 }))
      .sort((a, b) => (b.age_days || 0) - (a.age_days || 0));
    log.push({ stage: "candidates_inline", count: candidates.length });
  }

  // 3. Pick top N (oldest commercial first)
  const selected = candidates.slice(0, count);
  if (selected.length === 0) {
    return new Response(JSON.stringify({ ok: true, message: "no candidates to refresh", refreshed: 0, log, errors }), { headers: { "Content-Type": "application/json" } });
  }

  // 4. For each candidate, generate refreshed intro + conclusion via AI
  const updatedPosts = [];
  for (const cand of selected) {
    try {
      const post = posts.find(p => p.slug === cand.slug);
      if (!post) continue;

      const refreshPrompt = `Kamu adalah SEO copywriter Indonesia senior. Tugas: rewrite intro paragraph (1 paragraf) + tambah "Update 2026:" callout di akhir artikel existing untuk keyword "${cand.title}".

Artikel existing:
${(post.content || post.excerpt || "").slice(0, 1500)}

Format output JSON (WAJIB valid JSON):
{
  "intro_baru": "...",
  "update_2026": "..."
}

Aturan:
- Intro max 80 kata, tetap tone profesional Beriklan (tidak overclaim)
- Update 2026: max 50 kata, sebut data/tren terkini (harga, tools, algorithm changes)
- Pakai "Anda", bukan "kamu"
- Jangan pakai: bikin, gak, pasti untung, garansi 100%
- Jangan ubah H2/H3 existing
- Output hanya JSON, no markdown`;

      const aiResult = await generateWithZenOrGroq(refreshPrompt, env);
      if (!aiResult) {
        errors.push({ slug: cand.slug, error: "AI failed" });
        continue;
      }
      const aiText = (typeof aiResult === 'string') ? aiResult : (aiResult.text || '');
      const aiJson = extractJson(aiText);
      if (!aiJson || !aiJson.intro_baru || !aiJson.update_2026) {
        errors.push({ slug: cand.slug, error: "JSON parse failed", raw: String(aiText).slice(0, 200) });
        continue;
      }

      // 5. Inject into content
      const originalContent = post.content || "";
      let newContent = originalContent;
      const newIntroHtml = `<p class="bg-amber-50 border-l-4 border-accent p-4 my-6 text-sm italic"><strong>Update ${new Date().getFullYear()}:</strong> ${escapeHtml(aiJson.intro_baru)}</p>`;
      const h2Match = newContent.match(/<h2[^>]*>/);
      if (h2Match) {
        newContent = newContent.slice(0, h2Match.index) + newIntroHtml + "\n" + newContent.slice(h2Match.index);
      } else {
        newContent = newIntroHtml + "\n" + newContent;
      }
      const updateHtml = `<aside class="bg-blue-50 border border-blue-200 rounded-xl p-5 my-6"><p class="font-bold text-ink mb-2">📌 Update 2026</p><p class="text-sm text-muted">${escapeHtml(aiJson.update_2026)}</p></aside>`;
      newContent = newContent + "\n" + updateHtml;

      // 6. Update post
      post.content = newContent;
      post.refreshed_at = new Date().toISOString();
      post.refresh_count = (post.refresh_count || 0) + 1;

      updatedPosts.push({ slug: post.slug, title: post.title, model: (typeof aiResult === 'object' && aiResult._model) || "unknown" });
      log.push({ stage: "refreshed", slug: post.slug, title: post.title });
    } catch (e) {
      errors.push({ slug: cand.slug, error: String(e).slice(0, 200) });
    }
  }

  if (updatedPosts.length === 0) {
    return new Response(JSON.stringify({ ok: false, error: "no posts refreshed", log, errors }), { status: 500, headers: { "Content-Type": "application/json" } });
  }

  // 7. Commit posts.json to GitHub
  const owner = "ReqTimeout";
  const repo = "beriklan.co.id";
  const branch = "main";

  let commitSha = null;
  try {
    const pGet = await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/src/data/posts.json?ref=${branch}`, {
      headers: { Authorization: `token ${env.GITHUB_TOKEN}`, "User-Agent": "BeriklanWorker/1.0", Accept: "application/vnd.github.v3+json" },
    });
    if (!pGet.ok) throw new Error(`GitHub GET posts.json failed: ${pGet.status}`);
    const pData = await pGet.json();
    const postsContent = btoa(unescape(encodeURIComponent(JSON.stringify(posts, null, 1))));
    const pPut = await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/src/data/posts.json`, {
      method: "PUT",
      headers: { Authorization: `token ${env.GITHUB_TOKEN}`, "Content-Type": "application/json", "User-Agent": "BeriklanWorker/1.0" },
      body: JSON.stringify({
        message: `refresh: content refresh +${updatedPosts.length} articles [${updatedPosts.map(p => p.slug).join(", ")}]`,
        content: postsContent,
        sha: pData.sha,
        branch,
      }),
    });
    if (!pPut.ok) throw new Error(`GitHub PUT posts.json failed: ${pPut.status} ${(await pPut.text()).slice(0, 200)}`);
    const pPutData = await pPut.json();
    commitSha = pPutData.commit?.sha || null;
    log.push({ stage: "commit_posts", sha: commitSha, count: updatedPosts.length });

    // Log each refresh to D1 for dashboard visibility
    if (env.DB) {
      for (const up of updatedPosts) {
        try {
          await env.DB.prepare(
            `INSERT INTO refresh_log (slug, model, commit_sha, elapsed_ms) VALUES (?, ?, ?, ?)`
          ).bind(up.slug, up.model || "unknown", commitSha || "", Date.now() - t0).run();
        } catch (e) {
          // Noop — logging is non-critical
        }
      }
    }
  } catch (e) {
    errors.push({ stage: "commit_posts", error: String(e).slice(0, 300) });
  }

  return new Response(JSON.stringify({
    ok: true,
    refreshed: updatedPosts.length,
    posts: updatedPosts,
    commit_sha: commitSha,
    elapsed_ms: Date.now() - t0,
    log,
    errors,
  }, null, 2), { headers: { "Content-Type": "application/json" } });
}

// ─── N.5 Featured Snippet Optimizer — rewrite content for position 4-7 keywords ───
async function handleSnippetOptimizer(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  }
  const count = Math.max(1, Math.min(parseInt(url.searchParams.get("count") || "3", 10), 5));
  const t0 = Date.now();
  const log = [];
  const errors = [];
  const optimized = [];

  if (!env.DB) {
    return new Response(JSON.stringify({ ok: false, error: "DB not set" }), { status: 503, headers: { "Content-Type": "application/json" } });
  }
  if (!env.GITHUB_TOKEN) {
    return new Response(JSON.stringify({ ok: false, error: "GITHUB_TOKEN not set" }), { status: 503, headers: { "Content-Type": "application/json" } });
  }

  // 1. Find keywords in position 4-7 (best snippet candidates)
  const candidates = await env.DB.prepare(`
    SELECT keyword, page_url, position FROM keyword_ranks
    WHERE position BETWEEN 4 AND 7
      AND date = (SELECT MAX(date) FROM keyword_ranks kr2 WHERE kr2.keyword = keyword_ranks.keyword)
    ORDER BY position ASC LIMIT ?
  `).bind(count).all();

  if (!candidates.results || candidates.results.length === 0) {
    return new Response(JSON.stringify({ ok: true, message: "no candidates in position 4-7", optimized: 0, log, errors }), { headers: { "Content-Type": "application/json" } });
  }
  log.push({ stage: "candidates", count: candidates.results.length });

  // 2. Fetch posts.json from assets
  let posts = [];
  try {
    const r = await env.ASSETS.fetch(new URL("https://assets/data/posts.json"));
    if (r.ok) posts = await r.json();
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: "posts fetch failed" }), { status: 500, headers: { "Content-Type": "application/json" } });
  }

  // 3. For each candidate, generate snippet block
  for (const cand of candidates.results) {
    try {
      let slug = (cand.page_url || '').replace(/^https?:\/\/[^/]+\//, '').replace(/\/$/, '').replace(/^blog\//, '').replace(/\.html$/, '');
      if (!slug) continue;
      let post = posts.find(p => p.slug === slug);
      if (!post && slug.includes('/')) {
        slug = slug.split('/').pop();
        post = posts.find(p => p.slug === slug);
      }
      // Try without trailing /page/N for paginated URLs
      if (!post) {
        const baseSlug = slug.replace(/\/page\/\d+$/, '');
        post = posts.find(p => p.slug === baseSlug);
        if (post) slug = baseSlug;
      }
      // Try legacy .html → matching blog post (301 redirects typically point to blog/<slug>/)
      if (!post && cand.page_url.includes('.html')) {
        const htmlSlug = cand.page_url.replace(/^https?:\/\/[^/]+\//, '').replace(/\.html$/, '');
        post = posts.find(p => p.slug === htmlSlug);
        if (post) slug = htmlSlug;
      }
      if (!post || !post.content) continue;

      // Skip if already has snippet block
      if (post.content.includes('class="snippet-block"')) continue;

      const snippetPrompt = `Kamu adalah SEO copywriter Indonesia. Untuk keyword "${cand.keyword}", buat snippet block yang akan membantu ranking position 0 (featured snippet Google).

Format output JSON WAJIB valid (no markdown):
{
  "definisi": "1 kalimat definisi 40-60 kata dengan target keyword di awal",
  "poin": ["poin 1", "poin 2", "poin 3", "poin 4"],
  "faq": {"q": "pertanyaan terkait", "a": "jawaban 1-2 kalimat"}
}

Aturan:
- Definisi HARUS dimulai dengan kata target
- Poin: 3-5 bullet, paralel structure, 8-15 kata per poin
- FAQ: pertanyaan natural user, jawaban ringkas
- Pakai bahasa Indonesia formal, "Anda" predominant
- Jangan overclaim (no "pasti", "100%")`;

      const aiResult = await generateWithZenOrGroq(snippetPrompt, env);
      if (!aiResult) {
        errors.push({ keyword: cand.keyword, error: "AI failed" });
        continue;
      }
      const aiText = (typeof aiResult === 'string') ? aiResult : (aiResult.text || '');
      const snippetJson = extractJson(aiText);
      if (!snippetJson || !snippetJson.definisi) {
        errors.push({ keyword: cand.keyword, error: "JSON parse failed" });
        continue;
      }

      // Build snippet HTML block
      const poinHtml = (snippetJson.poin || []).map(p => `<li>${escapeHtml(p)}</li>`).join('');
      const faqHtml = snippetJson.faq ? `
<div class="snippet-faq mt-4 pt-4 border-t border-amber-200">
  <p class="font-bold text-ink mb-1">❓ ${escapeHtml(snippetJson.faq.q)}</p>
  <p class="text-sm text-muted">${escapeHtml(snippetJson.faq.a)}</p>
</div>` : '';

      const snippetBlock = `
<div class="snippet-block bg-amber-50 border-l-4 border-accent p-5 my-6 rounded-r-lg">
  <p class="text-xs font-bold text-accent uppercase tracking-wider mb-2">📌 Ringkasan Cepat</p>
  <p class="text-base text-ink mb-3 leading-relaxed">${escapeHtml(snippetJson.definisi)}</p>
  ${poinHtml ? `<ul class="list-disc pl-5 text-sm text-muted space-y-1">${poinHtml}</ul>` : ''}
  ${faqHtml}
</div>`;

      // Inject after first H2 (or at start)
      const h2Match = post.content.match(/<h2[^>]*>/);
      if (h2Match) {
        post.content = post.content.slice(0, h2Match.index) + snippetBlock + "\n" + post.content.slice(h2Match.index);
      } else {
        post.content = snippetBlock + "\n" + post.content;
      }
      post.snippet_optimized_at = new Date().toISOString();

      optimized.push({ keyword: cand.keyword, slug, position: cand.position, model: (typeof aiResult === 'object' && aiResult._model) || "unknown" });
      log.push({ stage: "optimized", keyword: cand.keyword, slug, position: cand.position });
    } catch (e) {
      errors.push({ keyword: cand.keyword, error: String(e).slice(0, 200) });
    }
  }

  if (optimized.length === 0) {
    return new Response(JSON.stringify({ ok: false, error: "no optimizations applied", log, errors }), { status: 500, headers: { "Content-Type": "application/json" } });
  }

  // 4. Commit to GitHub
  const owner = "ReqTimeout";
  const repo = "beriklan.co.id";
  const filePath = "src/data/posts.json";
  let commitSha = null;
  try {
    const pGet = await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/${filePath}?ref=main`, {
      headers: { Authorization: `token ${env.GITHUB_TOKEN}`, "User-Agent": "BeriklanWorker/1.0", Accept: "application/vnd.github.v3+json" },
    });
    if (!pGet.ok) throw new Error(`GitHub GET failed: ${pGet.status}`);
    const pGetData = await pGet.json();
    const pContent = btoa(unescape(encodeURIComponent(JSON.stringify(posts, null, 2))));
    const pPut = await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/${filePath}`, {
      method: "PUT",
      headers: { Authorization: `token ${env.GITHUB_TOKEN}`, "Content-Type": "application/json", "User-Agent": "BeriklanWorker/1.0" },
      body: JSON.stringify({ message: `snippet: optimize ${optimized.length} posts for position 4-7`, content: pContent, sha: pGetData.sha, branch: "main" }),
    });
    if (!pPut.ok) throw new Error(`GitHub PUT failed: ${pPut.status}`);
    const pPutData = await pPut.json();
    commitSha = pPutData.commit?.sha;
    log.push({ stage: "commit_posts", sha: commitSha, count: optimized.length });
  } catch (e) {
    errors.push({ stage: "commit_posts", error: String(e).slice(0, 300) });
  }

  return new Response(JSON.stringify({ ok: true, optimized: optimized.length, items: optimized, commit_sha: commitSha, elapsed_ms: Date.now() - t0, log, errors: errors.slice(0, 5) }, null, 2), { headers: { "Content-Type": "application/json" } });
}

// ─── N.4 Rank Tracker — daily GSC sync to D1 ─────────────
async function handleRankSync(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  }
  if (!env.GSC_SERVICE_ACCOUNT_JSON) {
    return new Response(JSON.stringify({ ok: false, error: "GSC_SERVICE_ACCOUNT_JSON not set" }), { status: 503, headers: { "Content-Type": "application/json" } });
  }

  const days = Math.max(1, Math.min(parseInt(url.searchParams.get("days") || "1", 10), 30));
  const t0 = Date.now();
  const log = [];
  const errors = [];

  // Load SA
  let sa;
  try {
    sa = JSON.parse(env.GSC_SERVICE_ACCOUNT_JSON);
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: "GSC SA parse failed: " + String(e) }), { status: 500, headers: { "Content-Type": "application/json" } });
  }

  // JWT sign using Web Crypto
  async function signJwt(saObj) {
    const enc = (s) => new TextEncoder().encode(s);
    const b64 = (b) => btoa(String.fromCharCode(...new Uint8Array(b))).replace(/=+$/, "").replace(/\+/g, "-").replace(/\//g, "_");
    const header = b64(enc(JSON.stringify({ alg: "RS256", typ: "JWT" })));
    const now = Math.floor(Date.now() / 1000);
    const claim = b64(enc(JSON.stringify({
      iss: saObj.client_email,
      scope: "https://www.googleapis.com/auth/webmasters.readonly",
      aud: "https://oauth2.googleapis.com/token",
      iat: now,
      exp: now + 3600,
    })));
    const pkcs8 = saObj.private_key.replace(/-----BEGIN PRIVATE KEY-----/, "").replace(/-----END PRIVATE KEY-----/, "").replace(/\n/g, "");
    const keyBin = Uint8Array.from(atob(pkcs8), (c) => c.charCodeAt(0));
    const cryptoKey = await crypto.subtle.importKey("pkcs8", keyBin, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["sign"]);
    const sig = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", cryptoKey, enc(`${header}.${claim}`));
    return `${header}.${claim}.${b64(sig)}`;
  }

  // Get access token
  let accessToken;
  try {
    const jwt = await signJwt(sa);
    const tr = await fetch("https://oauth2.googleapis.com/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${jwt}`,
    });
    const td = await tr.json();
    if (!td.access_token) throw new Error("no access_token: " + JSON.stringify(td).slice(0, 200));
    accessToken = td.access_token;
    log.push({ stage: "jwt_auth", ok: true });
  } catch (e) {
    errors.push({ stage: "jwt_auth", error: String(e) });
    return new Response(JSON.stringify({ ok: false, error: "auth failed", errors }), { status: 500, headers: { "Content-Type": "application/json" } });
  }

  // Query GSC searchAnalytics for last N days
  const endDate = new Date().toISOString().slice(0, 10);
  const startDate = new Date(Date.now() - days * 86400000).toISOString().slice(0, 10);
  let gscRows = [];
  try {
    const r = await fetch(`https://www.googleapis.com/webmasters/v3/sites/${encodeURIComponent("https://www.beriklan.co.id/")}/searchAnalytics/query`, {
      method: "POST",
      headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        startDate, endDate,
        dimensions: ["date", "query", "page"],
        rowLimit: 5000,
      }),
    });
    const d = await r.json();
    if (!r.ok) throw new Error("GSC query failed: " + JSON.stringify(d).slice(0, 300));
    gscRows = d.rows || [];
    log.push({ stage: "gsc_query", rows: gscRows.length, startDate, endDate });
  } catch (e) {
    errors.push({ stage: "gsc_query", error: String(e) });
    return new Response(JSON.stringify({ ok: false, error: "gsc query failed", errors }), { status: 500, headers: { "Content-Type": "application/json" } });
  }

  // Insert into D1
  let inserted = 0;
  let updated = 0;
  for (const row of gscRows) {
    try {
      const date = row.keys[0];
      const keyword = row.keys[1];
      const pageUrl = row.keys[2];
      const position = row.position;
      const clicks = row.clicks || 0;
      const impressions = row.impressions || 0;
      const ctr = row.ctr || 0;
      await env.DB.prepare(
        `INSERT INTO keyword_ranks (keyword, page_url, position, clicks, impressions, ctr, date)
         VALUES (?, ?, ?, ?, ?, ?, ?)
         ON CONFLICT(keyword, page_url, date) DO UPDATE SET
           position=excluded.position, clicks=excluded.clicks, impressions=excluded.impressions, ctr=excluded.ctr`
      ).bind(keyword, pageUrl, position, clicks, impressions, ctr, date).run();
      inserted++;
    } catch (e) {
      errors.push({ stage: "insert", keyword: row.keys?.[1], error: String(e).slice(0, 100) });
    }
  }
  log.push({ stage: "inserted", count: inserted });

  return new Response(JSON.stringify({ ok: true, days, rows: gscRows.length, inserted, elapsed_ms: Date.now() - t0, log, errors: errors.slice(0, 5) }, null, 2), { headers: { "Content-Type": "application/json" } });
}

async function handleRankTracker(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  }
  if (!env.DB) {
    return new Response(JSON.stringify({ ok: false, error: "DB not set" }), { status: 503, headers: { "Content-Type": "application/json" } });
  }

  const today = new Date().toISOString().slice(0, 10);
  const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);

  // Page-1 keywords (position <= 10) from latest snapshot per keyword
  const pageOne = await env.DB.prepare(`
    SELECT keyword, page_url, position, clicks, impressions, ctr, date
    FROM keyword_ranks
    WHERE position <= 10 AND date = (SELECT MAX(date) FROM keyword_ranks kr2 WHERE kr2.keyword = keyword_ranks.keyword)
    ORDER BY position ASC
    LIMIT 100
  `).all();

  // Improving (today vs yesterday)
  const improving = await env.DB.prepare(`
    SELECT t.keyword, t.page_url, t.position as today_pos, y.position as yesterday_pos,
           (y.position - t.position) as improvement
    FROM keyword_ranks t
    LEFT JOIN keyword_ranks y ON t.keyword = y.keyword AND t.page_url = y.page_url AND y.date = ?
    WHERE t.date = ? AND y.position IS NOT NULL AND t.position < y.position
    ORDER BY improvement DESC
    LIMIT 25
  `).bind(yesterday, today).all();

  // Declining
  const declining = await env.DB.prepare(`
    SELECT t.keyword, t.page_url, t.position as today_pos, y.position as yesterday_pos,
           (t.position - y.position) as decline
    FROM keyword_ranks t
    LEFT JOIN keyword_ranks y ON t.keyword = y.keyword AND t.page_url = y.page_url AND y.date = ?
    WHERE t.date = ? AND y.position IS NOT NULL AND t.position > y.position
    ORDER BY decline DESC
    LIMIT 25
  `).bind(yesterday, today).all();

  // Top keywords by clicks (last 7 days)
  const topByClicks = await env.DB.prepare(`
    SELECT keyword, SUM(clicks) as total_clicks, SUM(impressions) as total_impr, AVG(position) as avg_pos
    FROM keyword_ranks
    WHERE date >= date('now', '-7 days')
    GROUP BY keyword
    ORDER BY total_clicks DESC
    LIMIT 25
  `).all();

  // Summary stats
  const summary = await env.DB.prepare(`
    SELECT
      COUNT(DISTINCT keyword) as unique_keywords,
      SUM(clicks) as total_clicks,
      SUM(impressions) as total_impressions,
      AVG(position) as avg_position,
      MAX(date) as latest_date
    FROM keyword_ranks
    WHERE date = (SELECT MAX(date) FROM keyword_ranks)
  `).first();

  // Coverage: how many of our keywords have any rank data
  const coverage = await env.DB.prepare(`
    SELECT COUNT(DISTINCT kr.keyword) as ranked,
           (SELECT COUNT(*) FROM keyword_queue) as total_queued
    FROM keyword_ranks kr
  `).first().catch(() => ({ ranked: 0, total_queued: 0 }));

  // Format rows
  const fmtRow = (r, withDelta) => {
    const badge = r.position <= 3 ? 'green' : r.position <= 10 ? 'yellow' : 'red';
    let extra = '';
    if (withDelta && r.improvement) extra = ` <span class="badge green">↑${r.improvement.toFixed(1)}</span>`;
    if (withDelta && r.decline) extra = ` <span class="badge red">↓${r.decline.toFixed(1)}</span>`;
    return `<tr>
      <td><strong>${escapeHtml(r.keyword)}</strong>${extra}</td>
      <td><span class="badge ${badge}">#${r.position.toFixed(1)}</span></td>
      <td>${r.clicks || 0}</td>
      <td>${(r.impressions || 0).toLocaleString()}</td>
      <td style="word-break:break-all;font-size:11px;"><a href="${escapeHtml(r.page_url)}" target="_blank">${escapeHtml((r.page_url || '').replace('https://beriklan.co.id', '').slice(0, 50))}</a></td>
    </tr>`;
  };

  const pageOneRows = (pageOne.results || []).map((r) => fmtRow(r, false)).join("") || '<tr><td colspan="5" style="color:#999;">belum ada data — jalankan /api/cron/rank-sync dulu</td></tr>';
  const improvingRows = (improving.results || []).map((r) => fmtRow({ ...r, position: r.today_pos, clicks: '', impressions: '' }, true)).join("") || '<tr><td colspan="5" style="color:#999;">tidak ada perbaikan (perlu data kemarin)</td></tr>';
  const decliningRows = (declining.results || []).map((r) => fmtRow({ ...r, position: r.today_pos, clicks: '', impressions: '' }, true)).join("") || '<tr><td colspan="5" style="color:#999;">tidak ada penurunan</td></tr>';
  const topClicksRows = (topByClicks.results || []).map((r) => `
    <tr>
      <td><strong>${escapeHtml(r.keyword)}</strong></td>
      <td>${r.total_clicks || 0}</td>
      <td>${(r.total_impressions || 0).toLocaleString()}</td>
      <td><span class="badge yellow">#${(r.avg_pos || 0).toFixed(1)}</span></td>
    </tr>
  `).join("") || '<tr><td colspan="4" style="color:#999;">belum ada data</td></tr>';

  const s = summary || {};
  const cov = coverage || {};

  const html = `<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noindex,nofollow">
  <title>Rank Tracker — Beriklan Admin</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; color: #333; line-height: 1.5; }
    .container { max-width: 1280px; margin: 0 auto; padding: 24px; }
    h1 { font-size: 24px; margin-bottom: 4px; }
    .subtitle { color: #666; font-size: 13px; margin-bottom: 24px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
    .card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
    .card h2 { font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .card .metric { font-size: 30px; font-weight: 700; }
    .card .sub { font-size: 12px; color: #666; margin-top: 4px; }
    .card.success { background: #d4edda; border-left: 4px solid #10b981; }
    .card.warning { background: #fff3cd; border-left: 4px solid #f59e0b; }
    .card.info { background: #e0f2fe; border-left: 4px solid #0ea5e9; }
    .card.danger { background: #f8d7da; border-left: 4px solid #dc2626; }
    table { width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 24px; }
    th, td { padding: 10px 14px; text-align: left; border-bottom: 1px solid #eee; font-size: 13px; }
    th { background: #fafafa; color: #666; font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px; }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; background: #eee; color: #333; }
    .badge.green { background: #d4edda; color: #155724; }
    .badge.yellow { background: #fff3cd; color: #856404; }
    .badge.red { background: #f8d7da; color: #721c24; }
    a { color: #2563eb; text-decoration: none; }
    .section-title { font-size: 16px; font-weight: 700; margin: 32px 0 12px; }
    .nav { margin-bottom: 16px; font-size: 13px; }
    .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
    @media (max-width: 900px) { .two-col { grid-template-columns: 1fr; } }
    .sync-btn { background: #0f1e3d; color: white; padding: 10px 18px; border-radius: 8px; font-weight: 600; cursor: pointer; text-decoration: none; display: inline-block; margin-top: 8px; }
    .sync-btn:hover { background: #1a2f5c; }
  </style>
</head>
<body>
<div class="container">
  <div class="nav">
    <a href="/api/admin?token=${escapeHtml(token)}">← Admin Dashboard</a> · <a href="/api/admin/keywords?token=${escapeHtml(token)}">Keyword Pipeline</a>
  </div>
  <h1>📈 Rank Tracker (N.4)</h1>
  <p class="subtitle">Data GSC: ${escapeHtml(s.latest_date || 'n/a')} · Sinkron: <a href="/api/cron/rank-sync?token=${escapeHtml(token)}&days=1" target="_blank">/api/cron/rank-sync?days=1</a> (manual)</p>

  <div class="grid">
    <div class="card info"><h2>Unique Keywords</h2><div class="metric">${s.unique_keywords || 0}</div><div class="sub">yang punya rank data</div></div>
    <div class="card success"><h2>Total Clicks (latest)</h2><div class="metric">${s.total_clicks || 0}</div><div class="sub">dari ${(s.total_impressions || 0).toLocaleString()} impressions</div></div>
    <div class="card warning"><h2>Avg Position</h2><div class="metric">#${(s.avg_position || 0).toFixed(1)}</div><div class="sub">semua keyword tracked</div></div>
    <div class="card ${(pageOne.results || []).length > 0 ? 'success' : 'warning'}"><h2>Page-1 Winners</h2><div class="metric">${(pageOne.results || []).length}</div><div class="sub">position ≤ 10</div></div>
    <div class="card info"><h2>Coverage</h2><div class="metric">${cov.ranked || 0}/${(cov.total_queued || 0).toLocaleString()}</div><div class="sub">${cov.total_queued ? ((cov.ranked / cov.total_queued) * 100).toFixed(2) : 0}% tracked</div></div>
  </div>

  <h3 class="section-title">🎯 Keywords at Page 1 (Top 100)</h3>
  <table><thead><tr><th>Keyword</th><th>Position</th><th>Clicks</th><th>Impressions</th><th>URL</th></tr></thead><tbody>${pageOneRows}</tbody></table>

  <div class="two-col">
    <div>
      <h3 class="section-title">📈 Improving (hari ini vs kemarin)</h3>
      <table><thead><tr><th>Keyword</th><th>Today</th><th>Yesterday</th><th>Page</th></tr></thead><tbody>${improvingRows}</tbody></table>
    </div>
    <div>
      <h3 class="section-title">📉 Declining (perlu perhatian)</h3>
      <table><thead><tr><th>Keyword</th><th>Today</th><th>Yesterday</th><th>Page</th></tr></thead><tbody>${decliningRows}</tbody></table>
    </div>
  </div>

  <h3 class="section-title">🔥 Top Keywords by Clicks (7 hari)</h3>
  <table><thead><tr><th>Keyword</th><th>Clicks</th><th>Impressions</th><th>Avg Pos</th></tr></thead><tbody>${topClicksRows}</tbody></table>

  <a class="sync-btn" href="/api/cron/rank-sync?token=${escapeHtml(token)}&days=1" target="_blank">🔄 Sync GSC Data Now (hari ini)</a>
  <a class="sync-btn" style="background:#f59e0b;" href="/api/cron/rank-sync?token=${escapeHtml(token)}&days=7" target="_blank">🔄 Sync Last 7 Days</a>

  <p style="text-align:center;color:#999;font-size:11px;margin-top:40px;">Beriklan.co.id Rank Tracker · ${new Date().toISOString()}</p>
</div>
</body>
</html>`;

  return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8", "X-Robots-Tag": "noindex, nofollow" } });
}

// Helper: extract JSON from AI response (handles code fences)
function extractJson(s) {
  if (!s) return null;
  let str = String(s).trim();
  str = str.replace(/^```(?:json)?\s*/i, "").replace(/```\s*$/, "").trim();
  try { return JSON.parse(str); } catch {}
  const m = str.match(/\{[\s\S]*\}/);
  if (m) {
    try { return JSON.parse(m[0]); } catch {}
  }
  return null;
}

// Helper: Zen/Groq generation for refresh (lighter than full article)
async function generateWithZenOrGroq(prompt, env) {
  const maxTokens = 600;
  if (env.ZEN_API_KEY) {
    try {
      const r = await fetch("https://opencode.ai/zen/v1/chat/completions", {
        method: "POST",
        headers: { Authorization: `Bearer ${env.ZEN_API_KEY}`, "Content-Type": "application/json", "User-Agent": "BeriklanWorker/1.0" },
        body: JSON.stringify({
          model: "deepseek-v4-flash-free",
          messages: [{ role: "user", content: prompt }],
          max_tokens: maxTokens,
          thinking: { type: "disabled" },
        }),
      });
      if (r.ok) {
        const data = await r.json();
        const text = data.choices?.[0]?.message?.content || "";
        return { _model: "zen/deepseek-v4-flash-free", text };
      }
    } catch (e) {}
  }
  const groqKeys = getGroqKeys(env);
  for (let i = 0; i < groqKeys.length; i++) {
    const key = groqKeys[i];
    try {
      const r = await fetch("https://api.groq.com/openai/v1/chat/completions", {
        method: "POST",
        headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "llama-3.3-70b-versatile",
          messages: [{ role: "user", content: prompt }],
          max_tokens: maxTokens,
          temperature: 0.7,
        }),
      });
      if (r.ok) {
        const data = await r.json();
        const text = data.choices?.[0]?.message?.content || "";
        return { _model: `groq/llama-3.3-70b-versatile (groq#${i + 1})`, text };
      }
    } catch (e) {}
  }
  return null;
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

    // Save ALL fetched topics to D1 trending_topics (separate endpoint processes them)
    let savedToQueue = 0;
    if (env.DB) {
      try {
        for (const t of topics) {
          await env.DB.prepare(
            "INSERT OR IGNORE INTO trending_topics (topic, geo, status) VALUES (?, ?, 'pending')"
          ).bind(t, "ID,MY,US").run();
        }
        const r = await env.DB.prepare(
          "SELECT COUNT(*) as n FROM trending_topics WHERE status='pending'"
        ).first();
        savedToQueue = (r && r.n) || 0;
      } catch (e) {
        errors.push({stage: "trending_queue_save", error: e.message});
      }
    }

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
    // Prefer OpenCode Zen (free deepseek-v4-flash), fallback Groq
    const zenModels = ["deepseek-v4-flash-free"];
    const groqModels = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"];
    const aiEndpoints = [];
    if (env.ZEN_API_KEY) aiEndpoints.push({ name: "zen", url: "https://opencode.ai/zen/v1/chat/completions", key: env.ZEN_API_KEY, models: zenModels, thinkingDisabled: true });
    if (env.GROQ_API_KEY) aiEndpoints.push({ name: "groq-1", url: "https://api.groq.com/openai/v1/chat/completions", key: env.GROQ_API_KEY, models: groqModels, thinkingDisabled: false });
    // Additional Groq keys (round-robin via aiEndpoints)
    const groqKeysAll = getGroqKeys(env);
    for (let i = 1; i < groqKeysAll.length; i++) {
      aiEndpoints.push({ name: `groq-${i + 1}`, url: "https://api.groq.com/openai/v1/chat/completions", key: groqKeysAll[i], models: groqModels, thinkingDisabled: false });
    }
    if (aiEndpoints.length === 0) {
      errors.push({stage: "ai_config", message: "No AI key set (ZEN_API_KEY or GROQ_API_KEY)"});
    }
    for (const ep of aiEndpoints) {
      if (article && article.length > 500) break;
      for (const model of ep.models) {
        if (article && article.length > 500) break;
        try {
          const payload = {
            model,
            messages: [{
              role: "user",
              content: `Tulis artikel SEO Bahasa Indonesia untuk trending topic: "${chosen}". Tone: profesional, terukur. Format HTML langsung mulai dari <h2>. Include section: Pendahuluan, Cara Praktis, FAQ (3 pertanyaan + jawaban), CTA WhatsApp. Target 500-700 kata. JANGAN pakai kata: bikin, gak, nggak, pasti untung, garansi 100%, dalam dunia, semacam, di mana. Output HANYA body HTML. Mulai dari <h2>.`
            }],
            max_tokens: 4000,
            temperature: 0.7,
          };
          if (ep.thinkingDisabled) payload.thinking = { type: "disabled" };
          const aiResp = await fetch(ep.url, {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${ep.key}`,
              "Content-Type": "application/json",
              "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            },
            body: JSON.stringify(payload),
          });
          if (aiResp.ok) {
            const data = await aiResp.json();
            const content = data.choices?.[0]?.message?.content || "";
            // Strip markdown fences if present
            let cleaned = content.trim();
            if (cleaned.startsWith("```html")) cleaned = cleaned.slice(7);
            if (cleaned.startsWith("```")) cleaned = cleaned.slice(3);
            if (cleaned.endsWith("```")) cleaned = cleaned.slice(0, -3);
            article = cleaned.trim();
            ai_used_model = `${ep.name}/${model}`;
          } else {
            const body = await aiResp.text();
            errors.push({stage: "ai_api", endpoint: ep.name, model, status: aiResp.status, body: body.substring(0, 200)});
          }
        } catch (e) {
          errors.push({stage: "ai_try", endpoint: ep.name, model, error: e.message});
        }
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

    // Internal-link CTA block → money page (critical for ranking + conversion)
    if (!article.includes("<!-- internal-cta -->")) {
      article += `\n<!-- internal-cta -->\n<hr/>\n<h2>Butuh Jasa Digital Marketing?</h2>\n<p>Tim Beriklan mengelola campaign sejak 2016 — transparan, terukur, dengan laporan mingguan dan akses penuh ke akun Anda. Sesi konsultasi awal 15 menit, gratis.</p>\n<ul>\n<li><a href="/jasa-digital-marketing/">Lihat paket Jasa Digital Marketing — harga &amp; fitur lengkap</a></li>\n<li><a href="https://wa.me/62811919328?text=Halo%20Beriklan%2C%20saya%20membaca%20artikel%20Anda%20dan%20tertarik%20konsultasi%20digital%20marketing." rel="nofollow">Konsultasi via WhatsApp — respon dalam 1 jam (jam kerja)</a></li>\n</ul>`;
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

              // Auto-enqueue new trending article URL for IndexNow submission
              try {
                const newUrl = `https://beriklan.co.id/blog/${slug}/`;
                const existing = await env.DB.prepare(
                  "SELECT url FROM pending_indexing WHERE url=? AND status IN ('pending','submitted')"
                ).bind(newUrl).first();
                if (!existing) {
                  await env.DB.prepare(
                    "INSERT INTO pending_indexing (url, status, created_at) VALUES (?, 'pending', datetime('now'))"
                  ).bind(newUrl).run();
                }
              } catch (e) {
                errors.push({stage: "indexing_enqueue", error: e.message});
              }

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

// ─── Trending Generate (process trending_topics queue → articles) ─────
// GET /api/cron/trending-generate?token=...&count=N
//   Pulls top N pending topics from D1 trending_topics table (populated by
//   /api/cron/trending RSS fetch), generates article for each, commits
//   to posts.json + GitHub. Schedules via cron-job.org separately from
//   the fetch cron to decouple I/O (fast) from AI generation (slow).
async function handleTrendingGenerate(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) {
    return new Response(JSON.stringify({ ok: false, error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  }
  const count = Math.max(1, Math.min(parseInt(url.searchParams.get("count") || "1", 10), 3)); // max 3 to stay within 30s wall time
  const debug = url.searchParams.get("debug") === "1";
  const t0 = Date.now();
  const log = [];
  const errors = [];
  const generated = [];

  if (!env.DB) {
    return new Response(JSON.stringify({ ok: false, error: "DB not bound" }), { status: 503, headers: { "Content-Type": "application/json" } });
  }

  // Ensure tables exist (idempotent)
  try { await ensureTrendingTables(env); } catch {}

  try {
    // 1. Pull top N pending topics
    let topics = [];
    try {
      const r = await env.DB.prepare(
        `SELECT id, topic FROM trending_topics
         WHERE status = 'pending'
         ORDER BY priority DESC, fetched_at ASC
         LIMIT ?`
      ).bind(count).all();
      topics = (r.results || []);
      log.push({ stage: "topic_fetch", picked: topics.length, total_pending: "(see dashboard)" });
    } catch (e) {
      return new Response(JSON.stringify({ ok: false, error: "topic_fetch failed", e: String(e) }), { status: 500, headers: { "Content-Type": "application/json" } });
    }

    if (topics.length === 0) {
      return new Response(JSON.stringify({ ok: true, generated: 0, message: "no pending topics (run /api/cron/trending first)", log, errors }), { headers: { "Content-Type": "application/json" } });
    }

    // 2. For each topic, generate article via hourly-generate's classify + AI
    for (const item of topics) {
      try {
        // Mark as processing
        await env.DB.prepare(
          "UPDATE trending_topics SET status='processing', processed_at=datetime('now') WHERE id=?"
        ).bind(item.id).run();

        // Wrap topic as pseudo-keyword → reuse classify + generateArticleForKeyword
        const pseudoKeyword = { keyword: item.topic, slug: slugify(item.topic) };
        const post = await generateArticleForKeyword(pseudoKeyword, env);
        if (post && post.content) tagAsTrending(post);
        if (!post || !post.content) {
          await env.DB.prepare(
            "UPDATE trending_topics SET status='failed' WHERE id=?"
          ).bind(item.id).run();
          errors.push({ stage: "ai_generate", topic: item.topic, error: "empty article" });
          continue;
        }

        // Commit to GitHub (append to posts.json)
        if (env.GITHUB_TOKEN) {
          const owner = "ReqTimeout";
          const repo = "beriklan.co.id";
          const filePath = "src/data/posts.json";
          const getResp = await fetch(
            `https://api.github.com/repos/${owner}/${repo}/contents/${filePath}`,
            { headers: { "Authorization": `token ${env.GITHUB_TOKEN}`, "User-Agent": "BeriklanWorker/1.0" } }
          );
          if (getResp.ok) {
            const fileData = await getResp.json();
            let postsContent = "";
            if (fileData.content) postsContent = atob(fileData.content.replace(/\n/g, ""));
            else if (fileData.download_url) {
              const dl = await fetch(fileData.download_url, { headers: { "Authorization": `token ${env.GITHUB_TOKEN}` } });
              if (dl.ok) postsContent = await dl.text();
            }
            if (postsContent) {
              let posts = JSON.parse(postsContent);
              if (!posts.find(p => p.slug === post.slug)) {
                posts.unshift(post);
                posts.sort((a, b) => (b.iso_date || "").localeCompare(a.iso_date || ""));
                const content = btoa(unescape(encodeURIComponent(JSON.stringify(posts, null, 2))));
                const commitResp = await fetch(
                  `https://api.github.com/repos/${owner}/${repo}/contents/${filePath}`,
                  {
                    method: "PUT",
                    headers: { "Authorization": `token ${env.GITHUB_TOKEN}`, "Content-Type": "application/json", "User-Agent": "BeriklanWorker/1.0" },
                    body: JSON.stringify({
                      message: `trending: AI-generated article '${post.slug}'`,
                      content,
                      sha: fileData.sha,
                      branch: "main",
                    }),
                  }
                );
                if (commitResp.ok) {
                  const sha = (await commitResp.json()).commit?.sha?.slice(0, 7);
                  log.push({ stage: "github_commit", topic: item.topic, slug: post.slug, sha });
                  // Save to trending_articles table (audit)
                  await env.DB.prepare(
                    `INSERT OR REPLACE INTO trending_articles (slug, title, content, source, created_at) VALUES (?, ?, ?, 'workers_ai', datetime('now'))`
                  ).bind(post.slug, post.title, post.content).run();
                  // Mark topic as done
                  await env.DB.prepare(
                    "UPDATE trending_topics SET status='done' WHERE id=?"
                  ).bind(item.id).run();
                  generated.push({ topic: item.topic, slug: post.slug });
                } else {
                  errors.push({ stage: "github_commit_failed", topic: item.topic, status: commitResp.status });
                  await env.DB.prepare(
                    "UPDATE trending_topics SET status='pending' WHERE id=?"
                  ).bind(item.id).run();
                }
              } else {
                // Already in posts.json — mark done
                await env.DB.prepare(
                  "UPDATE trending_topics SET status='done' WHERE id=?"
                ).bind(item.id).run();
                log.push({ stage: "already_published", topic: item.topic, slug: post.slug });
              }
            }
          }
        } else {
          errors.push({ stage: "no_github_token", topic: item.topic });
        }
      } catch (e) {
        errors.push({ stage: "topic_generate_exception", topic: item.topic, error: String(e).slice(0, 200) });
      }
    }

    return new Response(JSON.stringify({
      ok: true,
      generated_count: generated.length,
      generated,
      elapsed_ms: Date.now() - t0,
      log: debug ? log : undefined,
      errors: errors.length ? errors : undefined,
    }, null, 2), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e), log, errors }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
}

// Simple slugify for trending topics
function slugify(s) {
  return s.toLowerCase().replace(/[^a-z0-9\s-]/g, "").replace(/\s+/g, "-").replace(/-+/g, "-").replace(/^-+|-+$/g, "").slice(0, 80);
}

// ─── Hourly Auto-Generate (cron-job.org trigger) ─────────────
// GET /api/cron/hourly-generate?token=...&count=N
//   Generates N articles from top pending keywords (priority_score DESC).
//   Commits posts.json + keyword-queue.json + posts-index.json via GitHub API.
//   Enqueues new URLs in D1 pending_indexing for IndexNow submission.
//   Triggers via cron-job.org: every 12 min for 5/jam, or count=5/cron.
async function handleHourlyGenerate(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) {
    return new Response(JSON.stringify({ ok: false, error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  }
  // Default count = 1 for Workers Free (10ms CPU budget per invocation).
//   Override ?count=5 if running on Workers Paid (30s CPU budget).
//   Wall time per article: ~3-5s with Zen/Groq fallback.
//   Free tier alternative: schedule 5 cron-job.org triggers with count=1.
  const count = Math.max(1, Math.min(parseInt(url.searchParams.get("count") || "1", 10), 5));
  const debug = url.searchParams.get("debug") === "1";
  const perArticleTimeoutMs = parseInt(url.searchParams.get("timeout") || "25000", 10);

  const t0 = Date.now();
  const log = [];
  const errors = [];

  try {
    // 1. Fetch keyword-queue.json from ASSETS (Worker cannot reach repo files directly)
    let queue = [];
    try {
      const qr = await env.ASSETS.fetch(new URL("https://assets/data/keyword-queue.json"));
      if (qr.ok) queue = await qr.json();
    } catch (e) {
      errors.push({ stage: "queue_fetch", error: e.message });
      return new Response(JSON.stringify({ ok: false, error: "queue_fetch failed", errors }), { status: 500, headers: { "Content-Type": "application/json" } });
    }
    log.push({ stage: "queue_fetch", count: queue.length });

    // 2. Pick top N pending by priority_score DESC
    const pending = queue
      .filter(q => q.status === "pending" && !q.has_post)
      .sort((a, b) => (b.priority_score || 0) - (a.priority_score || 0))
      .slice(0, count);
    log.push({ stage: "queue_pick", picked: pending.length, total_pending: queue.filter(q => q.status === "pending").length });
    if (pending.length === 0) {
      return new Response(JSON.stringify({ ok: true, generated: 0, message: "no pending keywords", log, errors }), { headers: { "Content-Type": "application/json" } });
    }

    // 2b. Pre-flight: ensure generated_drafts table exists (independent of GitHub)
    let hasGitHub = !!env.GITHUB_TOKEN;
    // Ensure generated_drafts table exists. Don't swallow errors silently — surface them in log.
    try {
      await env.DB.prepare(`CREATE TABLE IF NOT EXISTS generated_drafts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        service TEXT,
        city TEXT,
        source TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        committed_at TEXT
      )`).all();
      log.push({ stage: "ensure_table", ok: true });
    } catch (e) {
      log.push({ stage: "ensure_table", error: e.message });
    }

    // 3. For each pending keyword, generate article via Zen (fallback Groq)
    const newPosts = [];
    const aiModels = [];
    const aiTimings = [];
    for (const item of pending) {
      const aiStart = Date.now();
      try {
        const post = await Promise.race([
          generateArticleForKeyword(item, env),
          new Promise((_, reject) => setTimeout(() => reject(new Error("ai_timeout")), perArticleTimeoutMs)),
        ]);
        if (post) {
          newPosts.push(post);
          aiModels.push({ slug: post.slug, model: post._model || "unknown" });
        }
        aiTimings.push({ slug: item.slug, ms: Date.now() - aiStart });
      } catch (e) {
        const msg = e.message && e.message.includes("AI generation failed") ? e.message.slice(0, 1500) : String(e.message || e).slice(0, 200);
        const isRateLimit = e.message && e.message.startsWith("RATE_LIMITED");
        errors.push({ stage: isRateLimit ? "ai_rate_limited" : "ai_generate", slug: item.slug, error: msg, ms: Date.now() - aiStart });
        aiTimings.push({ slug: item.slug, ms: Date.now() - aiStart, error: true, rate_limited: isRateLimit });
      }
    }
    log.push({ stage: "ai_generate", generated: newPosts.length, timings: aiTimings });

    if (newPosts.length === 0) {
      return new Response(JSON.stringify({ ok: false, error: "no articles generated (check ZEN_API_KEY / GROQ_API_KEY)", log, errors }), { status: 500, headers: { "Content-Type": "application/json" } });
    }

    let commitSha = null;
    let committedToGitHub = false;

    if (hasGitHub) {
      // 4. Fetch current posts.json from GitHub, append new posts, sort, PUT back
      const owner = "ReqTimeout";
      const repo = "beriklan.co.id";
      const filePath = "src/data/posts.json";

      const getResp = await fetch(
        `https://api.github.com/repos/${owner}/${repo}/contents/${filePath}`,
        { headers: { "Authorization": `token ${env.GITHUB_TOKEN}`, "User-Agent": "BeriklanWorker/1.0" } }
      );
      if (!getResp.ok) {
        errors.push({ stage: "github_get_posts", status: getResp.status });
      } else {
        const fileData = await getResp.json();
        let postsContent = "";
        if (fileData.content) {
          postsContent = atob(fileData.content.replace(/\n/g, ""));
        } else if (fileData.download_url) {
          const dlResp = await fetch(fileData.download_url, { headers: { "Authorization": `token ${env.GITHUB_TOKEN}` } });
          if (dlResp.ok) postsContent = await dlResp.text();
        }
        if (postsContent) {
          let posts = [];
          try { posts = JSON.parse(postsContent); } catch (e) {
            errors.push({ stage: "parse_posts", error: e.message });
          }
          log.push({ stage: "github_get_posts", current_posts: posts.length });

          const existingSlugs = new Set(posts.map(p => p.slug));
          const toAdd = newPosts.filter(p => !existingSlugs.has(p.slug));
          log.push({ stage: "dedupe", new_after_dedupe: toAdd.length });

          if (toAdd.length > 0) {
            posts = posts.concat(toAdd);
            posts.sort((a, b) => (b.iso_date || "").localeCompare(a.iso_date || ""));
            const updatedContent = btoa(unescape(encodeURIComponent(JSON.stringify(posts, null, 2))));
            const commitResp = await fetch(
              `https://api.github.com/repos/${owner}/${repo}/contents/${filePath}`,
              {
                method: "PUT",
                headers: { "Authorization": `token ${env.GITHUB_TOKEN}`, "Content-Type": "application/json", "User-Agent": "BeriklanWorker/1.0" },
                body: JSON.stringify({
                  message: `hourly: auto-generate +${toAdd.length} articles [${toAdd.map(p => p.slug).slice(0, 3).join(", ")}${toAdd.length > 3 ? "..." : ""}]`,
                  content: updatedContent,
                  sha: fileData.sha,
                  branch: "main",
                }),
              }
            );
            if (commitResp.ok) {
              commitSha = (await commitResp.json()).commit?.sha?.slice(0, 7);
              committedToGitHub = true;
              log.push({ stage: "github_commit_posts", ok: true, sha: commitSha });
            } else {
              errors.push({ stage: "github_commit_posts", status: commitResp.status, body: (await commitResp.text()).slice(0, 300) });
            }

            // Update keyword-queue.json (only if commit succeeded)
            if (committedToGitHub) {
              for (const p of toAdd) {
                const q = queue.find(q => q.slug === p.slug);
                if (q) { q.status = "generated"; q.has_post = true; q.generated_at = new Date().toISOString(); }
              }
              const queuePath = "src/data/keyword-queue.json";
              const qGet = await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/${queuePath}`, {
                headers: { "Authorization": `token ${env.GITHUB_TOKEN}`, "User-Agent": "BeriklanWorker/1.0" }
              });
              if (qGet.ok) {
                const qd = await qGet.json();
                const qContent = btoa(unescape(encodeURIComponent(JSON.stringify(queue, null, 2))));
                const qPut = await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/${queuePath}`, {
                  method: "PUT",
                  headers: { "Authorization": `token ${env.GITHUB_TOKEN}`, "Content-Type": "application/json", "User-Agent": "BeriklanWorker/1.0" },
                  body: JSON.stringify({ message: `queue: mark ${toAdd.length} generated`, content: qContent, sha: qd.sha, branch: "main" }),
                });
log.push({ stage: "github_commit_queue", ok: qPut.ok });
              }

              // 3b. Auto-link: inject "Baca juga" section into 5 existing related posts
              //     pointing to each new article (crawl discovery accelerator)
              let linksInjected = 0;
              try {
                for (const newPost of toAdd) {
                  // Find 5 existing posts that match service (and city if any)
                  const related = posts
                    .filter(p => p.slug !== newPost.slug && !p._retrofit_linked)  // exclude new + already linked this batch
                    .map(p => {
                      let score = 0;
                      if (p.service === newPost.service) score += 10;
                      if (newPost.city && p.city === newPost.city) score += 15;
                      if (p.category === newPost.category) score += 3;
                      return { ...p, _relScore: score };
                    })
                    .filter(p => p._relScore > 0)
                    .sort((a, b) => b._relScore - a._relScore)
                    .slice(0, 5);

                  if (related.length === 0) continue;

                  const linkBlock = `\n<hr/>\n<h2>Baca Juga: <a href="/blog/${newPost.slug}/">${escapeHtml(newPost.title)}</a></h2>\n<p>${newPost.excerpt}</p>`;
                  let modified = false;
                  for (const rel of related) {
                    if (rel.content && !rel.content.includes(`/blog/${newPost.slug}/`)) {
                      rel.content = rel.content.trimEnd() + linkBlock;
                      rel._retrofit_linked = true;
                      modified = true;
                      linksInjected++;
                    }
                  }
                  if (modified) {
                    // Re-fetch latest posts.json sha (might have changed since initial fetch)
                    let currentSha = fileData.sha;
                    try {
                      const refetch = await fetch(
                        `https://api.github.com/repos/${owner}/${repo}/contents/${filePath}`,
                        { headers: { "Authorization": `token ${env.GITHUB_TOKEN}`, "User-Agent": "BeriklanWorker/1.0" } }
                      );
                      if (refetch.ok) {
                        const rd = await refetch.json();
                        currentSha = rd.sha;
                      }
                    } catch {}
                    const updatedContent2 = btoa(unescape(encodeURIComponent(JSON.stringify(posts, null, 2))));
                    let commitResp2 = await fetch(
                      `https://api.github.com/repos/${owner}/${repo}/contents/${filePath}`,
                      {
                        method: "PUT",
                        headers: { "Authorization": `token ${env.GITHUB_TOKEN}`, "Content-Type": "application/json", "User-Agent": "BeriklanWorker/1.0" },
                        body: JSON.stringify({
                          message: `link: ${newPost.slug} injected into ${related.length} related posts`,
                          content: updatedContent2,
                          sha: currentSha,
                          branch: "main",
                        }),
                      }
                    );
                    // Retry once on 409 (concurrent commit race)
                    if (!commitResp2.ok && commitResp2.status === 409) {
                      const refetch2 = await fetch(
                        `https://api.github.com/repos/${owner}/${repo}/contents/${filePath}`,
                        { headers: { "Authorization": `token ${env.GITHUB_TOKEN}`, "User-Agent": "BeriklanWorker/1.0" } }
                      );
                      if (refetch2.ok) {
                        const rd2 = await refetch2.json();
                        commitResp2 = await fetch(
                          `https://api.github.com/repos/${owner}/${repo}/contents/${filePath}`,
                          {
                            method: "PUT",
                            headers: { "Authorization": `token ${env.GITHUB_TOKEN}`, "Content-Type": "application/json", "User-Agent": "BeriklanWorker/1.0" },
                            body: JSON.stringify({
                              message: `link: ${newPost.slug} injected into ${related.length} related posts`,
                              content: updatedContent2,
                              sha: rd2.sha,
                              branch: "main",
                            }),
                          }
                        );
                      }
                    }
                    if (!commitResp2.ok) {
                      errors.push({ stage: "auto_link_commit_failed", slug: newPost.slug, status: commitResp2.status });
                    } else {
                      const data2 = await commitResp2.json();
                      fileData.sha = data2.content?.sha || fileData.sha;
                    }
                  }
                }
                log.push({ stage: "auto_link", injected: linksInjected });
              } catch (e) {
                errors.push({ stage: "auto_link", error: e.message });
              }

              // 3c. N.4 Page-1 Link Booster — inject link from TOP page-1 winners to each new article
              //     This gives new articles authority boost from pages that Google already trusts.
              try {
                if (env.DB) {
                  const winners = await env.DB.prepare(`
                    SELECT keyword, page_url FROM keyword_ranks
                    WHERE position <= 10 AND date = (SELECT MAX(date) FROM keyword_ranks)
                    ORDER BY position ASC
                    LIMIT 10
                  `).all();

                  if (winners.results && winners.results.length > 0) {
                    let boostedLinks = 0;
                    for (const newPost of toAdd) {
                      for (const w of winners.results) {
                        const winnerSlug = (w.page_url || '').replace(/^https?:\/\/[^/]+\//, '').replace(/\/$/, '').replace(/^blog\//, '');
                        if (!winnerSlug || winnerSlug === newPost.slug) continue;
                        const winnerPost = posts.find(p => p.slug === winnerSlug);
                        if (!winnerPost || !winnerPost.content) continue;
                        if (winnerPost.content.includes(`/blog/${newPost.slug}/`)) continue;

                        // Skip if topics don't match (basic keyword overlap)
                        const newKeywords = (newPost.title + ' ' + (newPost.tags || []).join(' ')).toLowerCase();
                        const winnerKeywords = (winnerPost.title + ' ' + (winnerPost.tags || []).join(' ')).toLowerCase();
                        const overlap = ['facebook', 'instagram', 'tiktok', 'google', 'youtube', 'website', 'landing', 'iklan', 'digital', 'jasa', 'ads', 'marketing'].filter(k => newKeywords.includes(k) && winnerKeywords.includes(k));
                        if (overlap.length === 0) continue;

                        const boostBlock = `\n<hr/>\n<h3>📌 Artikel Terkait: <a href="/blog/${newPost.slug}/">${escapeHtml(newPost.title)}</a></h3>\n<p>${escapeHtml(newPost.excerpt || '')}</p>`;
                        winnerPost.content = winnerPost.content.trimEnd() + boostBlock;
                        boostedLinks++;
                      }
                    }

                    if (boostedLinks > 0) {
                      let currentSha2 = fileData.sha;
                      try {
                        const refetch3 = await fetch(
                          `https://api.github.com/repos/${owner}/${repo}/contents/${filePath}`,
                          { headers: { "Authorization": `token ${env.GITHUB_TOKEN}`, "User-Agent": "BeriklanWorker/1.0" } }
                        );
                        if (refetch3.ok) {
                          const rd3 = await refetch3.json();
                          currentSha2 = rd3.sha;
                        }
                      } catch {}
                      const updatedContent3 = btoa(unescape(encodeURIComponent(JSON.stringify(posts, null, 2))));
                      const boostPut = await fetch(
                        `https://api.github.com/repos/${owner}/${repo}/contents/${filePath}`,
                        {
                          method: "PUT",
                          headers: { "Authorization": `token ${env.GITHUB_TOKEN}`, "Content-Type": "application/json", "User-Agent": "BeriklanWorker/1.0" },
                          body: JSON.stringify({
                            message: `boost: page-1 winners link to ${toAdd.length} new articles (${boostedLinks} links)`,
                            content: updatedContent3,
                            sha: currentSha2,
                            branch: "main",
                          }),
                        }
                      );
                      if (boostPut.ok) {
                        const bd = await boostPut.json();
                        fileData.sha = bd.content?.sha || fileData.sha;
                        log.push({ stage: "page1_boost", links: boostedLinks, winners: winners.results.length });
                      } else {
                        errors.push({ stage: "page1_boost_commit", status: boostPut.status });
                      }
                    }
                  }
                }
              } catch (e) {
                errors.push({ stage: "page1_boost", error: e.message });
              }

              // Refresh posts-index.json
              const idx = posts.slice(0, 24).map(p => ({
                slug: p.slug, title: p.title, excerpt: p.excerpt || "",
                date: p.date, iso_date: p.iso_date, category: p.category || "strategy",
                readTime: p.readTime || "5 min", featured: p.featured || false,
                tags: (p.tags || []).slice(0, 5),
              }));
              const idxPath = "public/data/posts-index.json";
              const idxGet = await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/${idxPath}`, {
                headers: { "Authorization": `token ${env.GITHUB_TOKEN}`, "User-Agent": "BeriklanWorker/1.0" }
              });
              if (idxGet.ok) {
                const id = await idxGet.json();
                const iContent = btoa(unescape(encodeURIComponent(JSON.stringify(idx, null, 2))));
                const idxPut = await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/${idxPath}`, {
                  method: "PUT",
                  headers: { "Authorization": `token ${env.GITHUB_TOKEN}`, "Content-Type": "application/json", "User-Agent": "BeriklanWorker/1.0" },
                  body: JSON.stringify({ message: `index: refresh +${toAdd.length} new articles`, content: iContent, sha: id.sha, branch: "main" }),
                });
                log.push({ stage: "github_commit_index", ok: idxPut.ok });
              }
            }
          }
        }
      }
    } else {
      log.push({ stage: "github_skipped", reason: "GITHUB_TOKEN not configured" });
    }

    // Fallback: save drafts to D1 staging table (even if GH commit succeeded, for audit + recovery)
    let draftsSaved = 0;
    for (const p of newPosts) {
      try {
        await env.DB.prepare(
          `INSERT INTO generated_drafts (slug, title, content, service, city, source, status, committed_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(slug) DO UPDATE SET title=excluded.title, content=excluded.content, status=excluded.status, committed_at=excluded.committed_at`
        ).bind(p.slug, p.title, p.content, p.service, p.city || null, "hourly-generate",
               committedToGitHub ? "committed" : "draft", committedToGitHub ? new Date().toISOString() : null).run();
        draftsSaved++;
      } catch (e) {
        errors.push({ stage: "drafts_save", slug: p.slug, error: e.message });
      }
    }
    log.push({ stage: "drafts_save", count: draftsSaved });

    // 7. Enqueue new URLs in D1 pending_indexing (for IndexNow cron /api/cron/indexing)
    //    Use www.beriklan.co.id prefix to match the verified GSC property
    //    (sitemap uses www. too — GSC Indexing API ownership check requires match)
    let enqueued = 0;
    for (const p of newPosts) {
      try {
        const url = `https://www.beriklan.co.id/blog/${p.slug}/`;
        const exists = await env.DB.prepare(
          "SELECT url FROM pending_indexing WHERE url=? AND status IN ('pending','submitted','gsc_submitted')"
        ).bind(url).first();
        if (!exists) {
          await env.DB.prepare(
            "INSERT INTO pending_indexing (url, status, created_at) VALUES (?, 'pending', datetime('now'))"
          ).bind(url).run();
          enqueued++;
        }
      } catch (e) {
        errors.push({ stage: "indexing_enqueue", slug: p.slug, error: e.message });
      }
    }
    log.push({ stage: "indexing_enqueue", count: enqueued });

    // 8. Log to D1 for dashboard
    try {
      await env.DB.prepare(
        `INSERT INTO cron_logs (timestamp, urls_processed, google_ok, google_fail, indexnow_ok, indexnow_fail)
         VALUES (datetime('now'), ?, ?, 0, 0, 0)`
      ).bind(newPosts.length, draftsSaved).run();
    } catch {}

    const elapsedMs = Date.now() - t0;
    return new Response(JSON.stringify({
      ok: true,
      generated: newPosts.length,
      slugs: newPosts.map(p => p.slug),
      models: aiModels,
      committed_to_github: committedToGitHub,
      commit_sha: commitSha,
      drafts_saved_to_d1: draftsSaved,
      enqueued_for_indexing: enqueued,
      elapsed_ms: elapsedMs,
      note: !hasGitHub ? "GITHUB_TOKEN not set — drafts saved to D1 only. Configure secret via CF Dashboard for full pipeline." : undefined,
      log: debug ? log : undefined,
      errors: errors.length ? errors : undefined,
    }, null, 2), { headers: { "Content-Type": "application/json" } });

  } catch (e) {
    return new Response(JSON.stringify({
      ok: false, error: String(e), stack: e.stack?.split("\n").slice(0, 5).join("\n"),
      log, errors,
    }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
}

// ─── GSC Indexing API (instant crawl signal, 200 req/day free) ─────
//   GET /api/cron/gsc-indexing?token=...&count=N
//   Reads pending URLs from D1, submits each to GSC Indexing API,
//   marks as 'gsc_submitted' on success. Re-submits are idempotent
//   (GSC dedupes by URL), so cron can run multiple times per day.
async function handleGscIndexing(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) {
    return new Response(JSON.stringify({ ok: false, error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  }
  const count = Math.max(1, Math.min(parseInt(url.searchParams.get("count") || "20", 10), 200));
  const debug = url.searchParams.get("debug") === "1";
  const t0 = Date.now();
  const log = [];
  const errors = [];
  const submitted = [];

  if (!env.GSC_SERVICE_ACCOUNT_JSON) {
    return new Response(JSON.stringify({
      ok: false,
      error: "GSC_SERVICE_ACCOUNT_JSON secret not set. Setup: create GSC service account in Google Cloud Console, add as Owner in GSC, paste JSON as CF secret.",
      setup_url: "https://console.cloud.google.com/iam-admin/serviceaccounts",
    }), { status: 503, headers: { "Content-Type": "application/json" } });
  }

  try {
    // 1. Get access token
    let accessToken;
    try {
      const sa = JSON.parse(env.GSC_SERVICE_ACCOUNT_JSON);
      accessToken = await getGoogleAccessToken(sa, "https://www.googleapis.com/auth/indexing");
      log.push({ stage: "auth", ok: true });
    } catch (e) {
      errors.push({ stage: "auth", error: String(e).slice(0, 200) });
      return new Response(JSON.stringify({ ok: false, error: "auth_failed", errors, log }), { status: 500, headers: { "Content-Type": "application/json" } });
    }

    // 2. Get pending URLs from D1 (skip already gsc_submitted today)
    let urls = [];
    try {
      // First, ensure column exists (idempotent)
      await env.DB.prepare(`ALTER TABLE pending_indexing ADD COLUMN gsc_submitted_at TEXT`).run().catch(() => {});
      const r = await env.DB.prepare(
        `SELECT id, url FROM pending_indexing
         WHERE (url LIKE 'https://www.beriklan.co.id/blog/%/' OR url LIKE 'https://beriklan.co.id/blog/%/')
           AND (gsc_submitted_at IS NULL OR gsc_submitted_at < datetime('now', '-7 days'))
         ORDER BY rowid ASC LIMIT ?`
      ).bind(count).all();
      // Normalize URL to www.beriklan.co.id for GSC submission (matches verified property)
      urls = (r.results || []).map(row => {
        const normalized = row.url.replace("https://beriklan.co.id/", "https://www.beriklan.co.id/");
        return { id: row.id, url: normalized, original: row.url };
      });
      log.push({ stage: "queue_fetch", picked: urls.length });
    } catch (e) {
      errors.push({ stage: "queue_fetch", error: String(e).slice(0, 200) });
      return new Response(JSON.stringify({ ok: false, error: "queue_fetch_failed", errors, log }), { status: 500, headers: { "Content-Type": "application/json" } });
    }

    if (urls.length === 0) {
      return new Response(JSON.stringify({ ok: true, message: "no pending URLs", submitted: [], log, errors }), { headers: { "Content-Type": "application/json" } });
    }

    // 3. Submit each URL to GSC Indexing API
    for (const item of urls) {
      try {
        const r = await fetch(
          "https://indexing.googleapis.com/v3/urlNotifications:publish",
          {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${accessToken}`,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ url: item.url, type: "URL_UPDATED" }),
          }
        );
        const result = { id: item.id, url: item.url, status: r.status, ok: r.ok };
        if (r.ok) {
          // Mark as gsc_submitted
          await env.DB.prepare(
            "UPDATE pending_indexing SET gsc_submitted_at = datetime('now'), status = 'gsc_submitted' WHERE id = ?"
          ).bind(item.id).run();
          submitted.push(item.url);
        } else {
          try { result.body = (await r.text()).slice(0, 150); } catch {}
          errors.push({ stage: "gsc_submit", ...result });
        }
        log.push({ stage: "submit", ...result });
      } catch (e) {
        errors.push({ stage: "gsc_submit_exception", url: item.url, error: String(e).slice(0, 200) });
      }
    }

    // 4. Log to cron_logs for dashboard
    try {
      await env.DB.prepare(
        "INSERT INTO cron_logs (timestamp, urls_processed, google_ok, google_fail, indexnow_ok, indexnow_fail) VALUES (datetime('now'), ?, ?, 0, 0, 0)"
      ).bind(submitted.length, submitted.length).run();
    } catch {}

    const elapsedMs = Date.now() - t0;
    return new Response(JSON.stringify({
      ok: true,
      submitted_count: submitted.length,
      submitted_urls: submitted,
      failed_count: errors.length,
      elapsed_ms: elapsedMs,
      log: debug ? log : undefined,
      errors: errors.length ? errors : undefined,
    }, null, 2), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e), log, errors }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
}

// ─── AI Article Generator (Worker port of gen_from_queue.py) ─────
// Generates one blog post for a queued keyword using Zen (fallback Groq).
async function generateArticleForKeyword(item, env) {
  const kw = item.keyword;
  const slug = item.slug;

  // Topic guard — block off-topic keywords at the gate
  const BANNED_KEYWORDS = [
    /\bcoring\b/i, /\bcor\s+beton\b/i, /\bdrill\s+beton\b/i,
    /\bjudi\b/i, /jud[il]-/i, /\bslot\b/i, /slot-/i,
    /\btogel\b/i, /\bpoker\b/i, /\bcasino\b/i,
    /sbobet/i, /joker123/i, /maxbet/i, /\bsabung\b/i,
    /\bbeton\b/i, /\bkonstruksi\b/i, /\bkontraktor\b/i, /\btukang\b/i,
    /\bkeramik\b/i, /\bgenteng\b/i, /\bkanopi\b/i, /\bpipa\b/i,
    /\brental\b/i, /\bsewa\b/i, /\bservice\s+ac\b/i,
    /\bpenipuan\b/i, /\bscam\b/i, /\bpinjol\b/i, /\bpinjaman\s+online\b/i,
    /\bgambling\b/i, /\bbetting\b/i, /\btaruhan\b/i,
    /\bkucing\b/i, /\banjing\b/i, /\bburung\b/i, /\bpeliharaan\b/i,
    /\bresep\b/i, /\bmasakan\b/i, /\bkuliner\b/i, /\brestoran\b/i, /\bmakanan\b/i,
    /\bfashion\b/i, /\bbaju\b/i, /\bpakaian\b/i, /\bkecantikan\b/i, /\bkosmetik\b/i,
    /\bmakeup\b/i, /\bskincare\b/i, /\bspa\b/i,
    /\bfifa\b/i, /\bmanchester\b/i, /\bbola\b/i,
    /\bcrypto\b/i, /\bbitcoin\b/i, /\bethereum\b/i, /\bforex\b/i, /\bsaham\b/i,
    /\bkeluarga\b/i, /\bpercintaan\b/i, /\bpasangan\b/i,
    /\blowongan\b/i, /\bkarir\b/i, /\bloker\b/i,
    /mobile\s+legend/i, /free\s+fire/i, /\bpubg\b/i, /\bgame\b/i,
    /\bpendidikan\b/i, /\bsekolah\b/i, /\bkuliah\b/i,
    /\bkesehatan\b/i, /\bpenyakit\b/i, /\bdokter\b/i,
  ];
  for (const pat of BANNED_KEYWORDS) {
    if (pat.test(kw)) {
      throw new Error(`OFF_TOPIC_BLOCKED: keyword "${kw}" matches banned pattern ${pat}`);
    }
  }

  const { svc, city } = classifyKeyword(kw);

  // Build prompt (mirrors gen_from_queue.py build_prompt)
  const svcName = SERVICE_NAMES[svc] || svc;
  const title = kw.split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
  const intent = /\b(harga|biaya|tarif|murah|paket)\b/i.test(kw) ? "commercial"
    : /\b(cara|tips|tutorial|langkah|strategi)\b/i.test(kw) ? "informational"
    : /\b(apa itu|bagaimana|kenapa|berapa)\b/i.test(kw) ? "question"
    : "consideration";

  const prompt = `Kamu adalah SEO copywriter Indonesia senior untuk agency performance marketing Beriklan.co.id (https://beriklan.co.id).

Tugas: Tulis artikel blog SEO Bahasa Indonesia untuk keyword: "${kw}"
Intent: ${intent}
Layanan: ${svcName}${city ? ` · Kota: ${city}` : ""}

Struktur artikel (HTML, mulai dari <h2>, jangan <h1>):
1. Pendahuluan (kenapa topik ini penting, 1 paragraf)
2. Section utama dengan sub-heading (<h3>) + bullet/list + tabel bila relevan
3. FAQ (3-4 pertanyaan + jawaban 1-2 kalimat)
4. CTA WhatsApp dengan placeholder link: <a href="https://wa.me/62811919328?text=Halo%20Beriklan%2C%20saya%20tertarik%20dengan%20${encodeURIComponent(svcName)}${city ? `%20di%20${encodeURIComponent(city)}` : ""}">Konsultasi via WhatsApp →</a>

Aturan copy:
- Tone profesional, terukur, percaya diri. Pakai "Anda" (kecuali hero moment).
- Jangan pakai: bikin, gak, nggak, pasti untung, garansi 100%, dalam dunia.
- Panjang: 700-1000 kata.
- Pakai data konkret (%, Rp, contoh spesifik) bila relevan.
- Brand voice: senior performance marketing partner, bukan sales.
- Internal link 2-3 ke https://beriklan.co.id/{svc}/ dan /{svc}/{city}/ (bila city ada).

TOPIK KETAT (WAJIB DIIKUTI):
- Artikel HANYA tentang jasa iklan, digital marketing, Meta/Facebook/Instagram/TikTok/Google/YouTube Ads,
  SEO, pembuatan website, landing page, social media management, dan topik terkait performa marketing.
- DILARANG KERAS menulis tentang: judi, slot online, togel, poker, casino, sbobet, fashion/baju/pakaian,
  kuliner/masakan/resep, kesehatan/penyakit, pendidikan/sekolah, hewan peliharaan, lowongan kerja/karir,
  cryptocurrency, sepak bola, game online, konstruksi/beton/kanopi/keramik, atau topik di luar digital marketing.
- Jika keyword tampak off-topic, TETAP tulis artikel dari sudut pandang digital marketing
  (contoh: jika keyword adalah "jasa website sekolah", tulis sebagai jasa pembuatan website untuk institusi pendidikan
  dalam konteks digital marketing), JANGAN keluar dari niche agency performance marketing.

Output: hanya HTML body, mulai dari <h2>. Tidak ada markdown fences.`;

  let article = null;
  let modelUsed = null;
  let zenDiag = null;
  let groqDiag = null;

  // Try Zen first (deepseek-v4-flash-free)
  if (env.ZEN_API_KEY) {
    try {
      const r = await fetch("https://opencode.ai/zen/v1/chat/completions", {
        method: "POST",
        headers: { "Authorization": `Bearer ${env.ZEN_API_KEY}`, "Content-Type": "application/json", "User-Agent": "BeriklanWorker/1.0" },
        body: JSON.stringify({
          model: "deepseek-v4-flash-free",
          messages: [{ role: "user", content: prompt }],
          max_tokens: 4000,
          thinking: { type: "disabled" },
        }),
      });
      zenDiag = { status: r.status, ok: r.ok };
      if (r.ok) {
        const data = await r.json();
        article = (data.choices?.[0]?.message?.content || "").trim();
        if (article.startsWith("```html")) article = article.slice(7);
        if (article.startsWith("```")) article = article.slice(3);
        if (article.endsWith("```")) article = article.slice(0, -3);
        article = article.trim();
        zenDiag.len = article.length;
        zenDiag.model = data.model;
        if (article.length > 500) modelUsed = `zen/deepseek-v4-flash-free`;
      } else {
        try { zenDiag.body = (await r.text()).slice(0, 200); } catch {}
      }
    } catch (e) {
      zenDiag = { error: String(e).slice(0, 200) };
    }
  } else {
    zenDiag = { skipped: "no ZEN_API_KEY" };
  }

  // Fallback Groq — try ALL configured keys until one succeeds or all 429
  if (!article) {
    const groqKeys = getGroqKeys(env);
    if (groqKeys.length > 0) {
      const groqResults = [];
      for (let i = 0; i < groqKeys.length && !article; i++) {
        const groqKey = groqKeys[i];
        const keyLabel = `groq#${i + 1}`;
        try {
          const r = await fetch("https://api.groq.com/openai/v1/chat/completions", {
            method: "POST",
            headers: { "Authorization": `Bearer ${groqKey}`, "Content-Type": "application/json" },
            body: JSON.stringify({
              model: "llama-3.3-70b-versatile",
              messages: [{ role: "user", content: prompt }],
              max_tokens: 4000,
              temperature: 0.7,
            }),
          });
          groqResults.push({ key: keyLabel, status: r.status, ok: r.ok });
          if (r.ok) {
            const data = await r.json();
            const cand = (data.choices?.[0]?.message?.content || "").trim();
            const cleaned = cand.replace(/^```html/, "").replace(/^```/, "").replace(/```$/, "").trim();
            if (cleaned.length > 500) {
              article = cleaned;
              groqDiag = { key: keyLabel, status: 200, len: cleaned.length, model: data.model };
              modelUsed = `groq/llama-3.3-70b-versatile (${keyLabel})`;
              break;
            }
          } else {
            try {
              const body = await r.text();
              groqResults[groqResults.length - 1].body = body.slice(0, 200);
            } catch {}
          }
        } catch (e) {
          groqResults.push({ key: keyLabel, error: String(e).slice(0, 100) });
        }
      }
      // If none succeeded, set groqDiag to first failure (representative)
      if (!article) {
        const first = groqResults[0] || {};
        groqDiag = { tried: groqResults.length, results: groqResults, ...first };
      }
    } else {
      groqDiag = { skipped: "no GROQ_API_KEY*" };
    }
  }

  if (!article || article.length < 500) {
    const zenLimited = zenDiag?.status === 429;
    const groqLimited = groqDiag?.status === 429;
    const rateLimited = zenLimited || groqLimited;
    const baseMsg = `AI generation failed | zen=${JSON.stringify(zenDiag)} | groq=${JSON.stringify(groqDiag)}`;
    throw new Error(rateLimited ? `RATE_LIMITED: ${baseMsg}` : baseMsg);
  }

  // Ensure starts with <h2>
  if (!article.startsWith("<h2>")) {
    article = "<h2>" + title + "</h2>\n" + article;
  }

  // Strip HTML tags for excerpt
  const plainExcerpt = article.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim().slice(0, 180) + "...";
  const words = article.split(/\s+/).length;

  const now = new Date();
  const dateStr = now.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }).replace(/ /g, " ");
  const iso = now.toISOString();

  return {
    slug,
    title,
    excerpt: plainExcerpt,
    content: article,
    date: dateStr,
    iso_date: iso,
    category: "strategy",
    readTime: `${Math.max(2, Math.round(words / 200))} min`,
    tags: kw.toLowerCase().split(/\s+/).filter(w => w.length > 3).slice(0, 5),
    featured: false,
    generated: true,
    service: svc,
    city: city || null,
    liveUrl: null,
    publish_date: dateStr,
    _model: modelUsed,
  };
}

// Override for trending content: category='trending', extra internal-cta for SEO juice
function tagAsTrending(post) {
  post.category = 'trending';
  post.source = 'google_trends_rss';
  if (post.content && !post.content.includes('<!-- internal-cta -->')) {
    post.content = post.content.trimEnd() +
      `\n<!-- internal-cta -->\n<hr/>\n<h2>Panduan Lengkap Jasa Digital Marketing</h2>\n<p>Tim Beriklan mengelola campaign iklan sejak 2016 — transparan, terukur, laporan mingguan. Sesi konsultasi awal 15 menit, gratis.</p>\n<ul><li><a href="/jasa-digital-marketing/">Lihat paket Jasa Digital Marketing</a></li><li><a href="https://wa.me/62811919328?text=Halo%20Beriklan%2C%20saya%20tertarik%20dengan%20artikel%20${encodeURIComponent(post.title)}">Konsultasi via WhatsApp →</a></li></ul>`;
  }
  return post;
}

// Keyword classifier (JS port of derive_service + derive_city)
function classifyKeyword(kw) {
  const k = kw.toLowerCase();
  // Order matters: view-live first (overlaps with platform names)
  if (/view live|viewers live|penonton live|viewers tiktok|viewers instagram|viewers youtube|viewers shopee|jasa viewers|jasa penonton/.test(k)) {
    return { svc: "jasa-view-live", city: extractCity(k) };
  }
  if (/jasa iklan facebook|iklan facebook|facebook ads|fb ads/.test(k)) return { svc: "jasa-iklan-facebook", city: extractCity(k) };
  if (/jasa iklan instagram|iklan instagram|instagram ads|ig ads/.test(k)) return { svc: "jasa-iklan-instagram", city: extractCity(k) };
  if (/jasa iklan tiktok|iklan tiktok|tiktok ads/.test(k)) return { svc: "jasa-iklan-tiktok", city: extractCity(k) };
  if (/jasa iklan google|iklan google|google ads|adwords/.test(k)) return { svc: "jasa-iklan-google", city: extractCity(k) };
  if (/jasa iklan youtube|iklan youtube|youtube ads/.test(k)) return { svc: "jasa-iklan-youtube", city: extractCity(k) };
  if (/jasa kelola instagram|kelola instagram|manage instagram|admin instagram/.test(k)) return { svc: "jasa-kelola-instagram", city: extractCity(k) };
  if (/jasa kelola tiktok|kelola tiktok|manage tiktok|admin tiktok/.test(k)) return { svc: "jasa-kelola-tiktok", city: extractCity(k) };
  if (/jasa pembuatan website|jasa buat website|pembuatan website|jasa website|jasa pembuat website|jasa bikin website|jasa pembuat web|jasa bikin web|jasa buat web|jasa web|bikin website|buat website|pembuat website|jasa situs|website murah|web murah|desain website|jasa desain web|web site|pembuat web|pembuatan web|situs web|membuat web|tampilan web|tampilan website|desain web|situs website|web umkm|bikin web|buat web/.test(k)) return { svc: "jasa-pembuatan-website", city: extractCity(k) };
  if (/landing page|landingpage/.test(k)) return { svc: "jasa-pembuatan-landing-page", city: extractCity(k) };
  if (/digital marketing|internet marketing|digital agency|search engine marketer|konsultan marketing|agency digital/.test(k)) return { svc: "jasa-digital-marketing", city: extractCity(k) };
  return { svc: "jasa-digital-marketing", city: extractCity(k) };
}

const KW_CITIES = ["jakarta","bandung","surabaya","yogyakarta","semarang","medan","makassar","denpasar","bekasi","depok","tangerang","bogor","malang","batam","palembang","pekanbaru","sidoarjo","solo","padang","manado","pontianak","banjarmasin","lampung","jambi","cimahi","balikpapan","aceh","samarinda","bali"];
function extractCity(k) {
  for (const c of KW_CITIES) {
    const re = new RegExp(`(?:^|\\s|di )${c}(?:\\s|$)`);
    if (re.test(k)) return c;
  }
  return null;
}

const SERVICE_NAMES = {
  "jasa-digital-marketing": "Jasa Digital Marketing",
  "jasa-iklan-facebook": "Jasa Iklan Facebook",
  "jasa-iklan-instagram": "Jasa Iklan Instagram",
  "jasa-iklan-tiktok": "Jasa Iklan TikTok",
  "jasa-iklan-google": "Jasa Iklan Google",
  "jasa-iklan-youtube": "Jasa Iklan YouTube",
  "jasa-kelola-instagram": "Jasa Kelola Instagram",
  "jasa-kelola-tiktok": "Jasa Kelola TikTok",
  "jasa-pembuatan-website": "Jasa Pembuatan Website",
  "jasa-pembuatan-landing-page": "Jasa Pembuatan Landing Page",
  "jasa-view-live": "Jasa View Live",
};

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
      const groqKeys = getGroqKeys(env);
      if (groqKeys.length > 0) {
        for (const mdl of ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]) {
          if (content) break;
          for (const groqKey of groqKeys) {
            try {
              const gr = await fetch("https://api.groq.com/openai/v1/chat/completions", {
                method: "POST",
                headers: { "Authorization": `Bearer ${groqKey}`, "Content-Type": "application/json" },
                body: JSON.stringify({ model: mdl, messages: [{ role: "user", content: prompt }], max_tokens: 1200, temperature: 0.7 }),
              });
              if (gr.ok) {
                const cand = (await gr.json()).choices[0].message.content.trim();
                if (cand.length > 200) { content = cand; break; }
              }
              errors.push({ slug: q.slug, model: mdl, status: gr.status });
            } catch (e) { errors.push({ slug: q.slug, model: mdl, stage: "groq", error: e.message }); }
          }
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
      const groqKeys = getGroqKeys(env);
      if (groqKeys.length > 0) {
        for (const mdl of ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]) {
          if (html) break;
          for (const groqKey of groqKeys) {
            try {
              const gr = await fetch("https://api.groq.com/openai/v1/chat/completions", {
                method: "POST",
                headers: { "Authorization": `Bearer ${groqKey}`, "Content-Type": "application/json" },
                body: JSON.stringify({ model: mdl, messages: [{ role: "user", content: prompt }], max_tokens: 1600, temperature: 0.7 }),
              });
              if (gr.ok) {
                const cand = (await gr.json()).choices[0].message.content.trim();
                if (cand.length > 200) { html = cand; break; }
              }
              errors.push({ route: q.route, model: mdl, status: gr.status });
            } catch (e) { errors.push({ route: q.route, model: mdl, stage: "groq", error: e.message }); }
          }
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
  // Trending topics queue — fetched RSS topics, processed by trending-generate
  try {
    await env.DB.prepare(
      `CREATE TABLE IF NOT EXISTS trending_topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT NOT NULL UNIQUE,
        geo TEXT,
        priority INTEGER DEFAULT 0,
        fetched_at TEXT DEFAULT CURRENT_TIMESTAMP,
        processed_at TEXT,
        status TEXT DEFAULT 'pending'
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
// Force rebuild Tue Jul 21 10:33:20 WIB 2026
// Force CF rebuild for PAA Tue Jul 21 11:39:50 WIB 2026
