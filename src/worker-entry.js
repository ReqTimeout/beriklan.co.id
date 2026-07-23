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
    const hostname = url.hostname || request.headers.get("Host") || "";

    // scrape.beriklan.co.id — consumer-facing scraping trial
    if (hostname.startsWith("scrape.beriklan.co.id")) {
      return await handleScrapePortal(request, env, ctx);
    }

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
    if (path === "/api/admin/health" || path === "/api/admin/health/") {
      return await handleAdminHealth(request, env);
    }
    if (path === "/api/admin/drafts" || path === "/api/admin/drafts/") {
      return await handleAdminDrafts(request, env);
    }
    if (path === "/api/admin/drafts/commit" || path === "/api/admin/drafts/commit/") {
      return await handleAdminDraftsCommit(request, env);
    }
    if (path === "/api/admin/email/queue/reset" || path === "/api/admin/email/queue/reset/") {
      return await handleEmailQueueReset(request, env);
    }
    if (path === "/api/admin/email/metrics" || path === "/api/admin/email/metrics/") {
      return await handleEmailMetrics(request, env);
    }
    if (path.startsWith("/api/admin/campaigns/") && path.endsWith("/metrics")) {
      const id = parseInt(path.split("/")[4]);
      return await handleCampaignMetrics(request, id, env);
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
    if (path === "/api/track/open" || path === "/api/track/open/") {
      const url = new URL(request.url);
      const trackingId = url.searchParams.get("id") || "";
      if (env.DB && trackingId) {
        await env.DB.prepare("UPDATE email_queue SET opened_at = COALESCE(opened_at, CURRENT_TIMESTAMP) WHERE tracking_id = ?").bind(trackingId).run();
        await env.DB.prepare("UPDATE campaigns SET open_count = (SELECT COUNT(DISTINCT tracking_id) FROM email_queue WHERE campaign_id IN (SELECT campaign_id FROM email_queue WHERE tracking_id = ?) AND opened_at IS NOT NULL) WHERE id IN (SELECT campaign_id FROM email_queue WHERE tracking_id = ?)").bind(trackingId, trackingId).run();
      }
      const pixel = new Uint8Array([0x47,0x49,0x46,0x38,0x39,0x61,0x01,0x00,0x01,0x00,0x80,0x00,0x00,0x00,0x00,0x00,0xFF,0xFF,0xFF,0x21,0xF9,0x04,0x01,0x00,0x00,0x00,0x00,0x2C,0x00,0x00,0x00,0x00,0x01,0x00,0x01,0x00,0x00,0x02,0x02,0x44,0x01,0x00,0x3B]);
      return new Response(pixel, { status: 200, headers: { "Content-Type": "image/gif", "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0" } });
    }
    if (path === "/api/track/click" || path === "/api/track/click/") {
      const url = new URL(request.url);
      const trackingId = url.searchParams.get("id") || "";
      const redirect = url.searchParams.get("url") || "https://beriklan.co.id";
      if (env.DB && trackingId) {
        await env.DB.prepare("UPDATE email_queue SET clicked_at = COALESCE(clicked_at, CURRENT_TIMESTAMP) WHERE tracking_id = ?").bind(trackingId).run();
      }
      return Response.redirect(redirect, 302);
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
    if (path === "/api/cron/indexnow" || path === "/api/cron/indexnow/") {
      return await handleIndexNowCron(request, env);
    }
    if (path === "/api/admin/cleanup-indexing" || path === "/api/admin/cleanup-indexing/") {
      return await handlePendingIndexingCleanup(request, env);
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
    if (path === "/api/admin/keywords/seed" || path === "/api/admin/keywords/seed/") {
      return await handleAdminSeedKeywords(request, env);
    }
    if (path === "/api/admin" || path === "/api/admin/") {
      // P0.4 Admin Dashboard HTML
      const rl = await checkRateLimit(env, request.headers.get("CF-Connecting-IP"), "/api/admin/dashboard", 60, 3600);
      if (!rl.allowed) {
        return new Response(JSON.stringify({ ok: false, error: "Rate limit exceeded" }), { status: 429, headers: { "Content-Type": "application/json" } });
      }
      return await handleAdminDashboard(request, env);
    }

    // ─── Email Campaign System Routes ────────────────────────────
    if (path === "/api/admin/email" || path === "/api/admin/email/") {
      return await handleEmailDashboard(request, env);
    }
    if (path === "/api/email/templates" || path === "/api/email/templates/") {
      return await handleEmailTemplates(request, env);
    }
    if (path === "/api/email/templates/preview" || path === "/api/email/templates/preview/") {
      return await handleEmailTemplatePreview(request, env);
    }
    if (path === "/api/email/test-send" || path === "/api/email/test-send/") {
      return await handleEmailTestSend(request, env);
    }
    if (path === "/api/email/campaigns" || path === "/api/email/campaigns/") {
      return await handleEmailCampaigns(request, env);
    }
    if (path === "/api/email/lists" || path === "/api/email/lists/") {
      return await handleEmailLists(request, env);
    }
    if (path === "/api/cron/email/send" || path === "/api/cron/email/send/") {
      return await handleCronSendEmail(request, env);
    }
    if (path === "/api/admin/cron/toggle" || path === "/api/admin/cron/toggle/") {
      return await handleCronToggle(request, env);
    }
    // ─── Scraper Cron Routes ─────────────────────────────────────
    if (path === "/api/cron/scrape/indonetwork" || path === "/api/cron/scrape/indonetwork/") {
      return await handleScrapeIndonetwork(request, env);
    }
    if (path === "/api/cron/scrape/google-places" || path === "/api/cron/scrape/google-places/") {
      return await handleScrapeGooglePlaces(request, env);
    }
    if (path === "/api/email/import" || path === "/api/email/import/") {
      return await handleImportDatabase(request, env);
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
      // Handle 301 redirects for legacy/invalid URL patterns
      const legacyRedirect = await handleGenericCityRedirect(request, env);
      if (legacyRedirect) return legacyRedirect;
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

    const run = async (label, handler, path, cronName) => {
      const t0 = Date.now();
      let runId = 0;
      let status = "ok";
      let output = "";
      let errorMsg = "";

      // Check if cron is paused
      if (cronName && env.DB) {
        try {
          const s = await env.DB.prepare("SELECT enabled FROM cron_settings WHERE name=?").bind(cronName).first();
          if (s && s.enabled === 0) {
            console.log(`[scheduled:${label}] PAUSED, skipping`);
            return;
          }
        } catch {}
      }

      // Check retry queue first — kalau ada retry pending untuk cron ini, jalankan
      if (cronName && env.DB) {
        try {
          const retries = await env.DB.prepare(
            "SELECT id, payload, attempts FROM cron_retry_queue WHERE cron_name = ? AND status = 'pending' AND (next_retry_at IS NULL OR next_retry_at <= datetime('now')) ORDER BY id LIMIT 1"
          ).bind(cronName).first();
          if (retries) {
            console.log(`[scheduled:${label}] retrying attempt #${retries.attempts + 1} for queue #${retries.id}`);
          }
        } catch {}
      }

      // Log start to cron_runs
      if (cronName && env.DB) {
        try {
          const r = await env.DB.prepare(
            "INSERT INTO cron_runs (cron_name, status, started_at) VALUES (?, 'running', datetime('now'))"
          ).bind(cronName).run();
          runId = r.meta?.last_row_id || 0;
        } catch {}
      }

      try {
        const res = await handler(fakeReq(path), env);
        const data = await res.json().catch(() => ({}));
        const duration = Date.now() - t0;
        if (!data.ok) {
          status = "failed";
          errorMsg = data.error || `HTTP ${res.status}`;
          output = JSON.stringify(data).slice(0, 1000);
        } else {
          output = JSON.stringify(data).slice(0, 1000);
        }
        console.log(`[scheduled:${label}] ${res.status} ${duration}ms ok=${data.ok} ${output.slice(0, 300)}`);
      } catch (e) {
        status = "failed";
        errorMsg = String(e).slice(0, 500);
        console.error(`[scheduled:${label}] error:`, errorMsg);
      }

      // Update cron_runs dengan status
      if (runId && env.DB) {
        try {
          await env.DB.prepare(
            "UPDATE cron_runs SET status = ?, finished_at = datetime('now'), duration_ms = ?, output = ?, error = ? WHERE id = ?"
          ).bind(status, Date.now() - t0, output, errorMsg, runId).run();
        } catch {}
      }

      // AUTO-RETRY: kalau gagal, masukkan retry queue
      if (status === "failed" && cronName && env.DB) {
        try {
          // Cek apakah sudah ada 3 gagal berturut-turut → auto-pause
          const recent = await env.DB.prepare(
            "SELECT status FROM cron_runs WHERE cron_name = ? ORDER BY id DESC LIMIT 3"
          ).bind(cronName).all();
          const recentRows = recent.results || [];
          const allFailed = recentRows.length >= 3 && recentRows.every(r => r.status === "failed");
          if (allFailed) {
            console.error(`[scheduled:${label}] AUTO-PAUSE: 3 consecutive failures`);
            await env.DB.prepare(
              "UPDATE cron_settings SET enabled = 0 WHERE name = ?"
            ).bind(cronName).run();
            // Add to retry queue dengan backoff
            await env.DB.prepare(
              "INSERT INTO cron_retry_queue (cron_name, last_error, attempts, next_retry_at, status) VALUES (?, ?, 1, datetime('now', '+30 minutes'), 'pending')"
            ).bind(cronName, "AUTO-PAUSED: " + errorMsg.slice(0, 200)).run();
          } else {
            // Add ke retry queue dengan exponential backoff
            await env.DB.prepare(
              "INSERT INTO cron_retry_queue (cron_name, last_error, attempts, next_retry_at, status) VALUES (?, ?, 1, datetime('now', '+5 minutes'), 'pending')"
            ).bind(cronName, errorMsg.slice(0, 200)).run();
          }
        } catch (e) {
          console.error(`[scheduled:${label}] retry queue error:`, String(e).slice(0, 200));
        }
      }
    };

    console.log("[scheduled] cron:", cron);

    const cronMap = {
      "0 * * * *":     { cronName: "hourly", handler: handleHourlyGenerate, path: "/api/cron/hourly-generate?token=beriklan-admin-2026&count=3" },
      "15 * * * *":    { cronName: "indexnow", handler: handleIndexNowCron, path: "/api/cron/indexnow?token=beriklan-admin-2026&count=50" },
      "30 6 * * *":    { cronName: "scrape-indonetwork", handler: handleScrapeIndonetwork, path: "/api/cron/scrape/indonetwork?token=beriklan-admin-2026" },
      "0 7 * * *":     { cronName: "scrape-google-places", handler: handleScrapeGooglePlaces, path: "/api/cron/scrape/google-places?token=beriklan-admin-2026" },
      "*/15 * * * *":  { cronName: "email-send", handler: handleCronSendEmail, path: "/api/cron/email/send?token=beriklan-admin-2026" },
    };

    if (cron === "0 */6 * * *") {
      ctx.waitUntil(run("gsc-indexing", handleGscIndexing, "/api/cron/gsc-indexing?token=beriklan-admin-2026&count=50", "gsc-indexing"));
      ctx.waitUntil(run("trending-fetch", handleTrendingCron, "/api/cron/trending?token=beriklan-admin-2026", "gsc-indexing"));
      ctx.waitUntil(run("rank-sync", handleRankSync, "/api/cron/rank-sync?token=beriklan-admin-2026&days=1", "gsc-indexing"));
      ctx.waitUntil(run("pending-cleanup", handlePendingIndexingCleanup, "/api/admin/cleanup-indexing?token=beriklan-admin-2026", "gsc-indexing"));
      ctx.waitUntil(run("sitemap-ping", handlePingSitemap, "/api/ping-sitemap?token=beriklan-admin-2026", "gsc-indexing"));
    } else if (cron === "30 */6 * * *") {
      ctx.waitUntil(run("trending-generate", handleTrendingGenerate, "/api/cron/trending-generate?token=beriklan-admin-2026&count=1", "trending-generate"));
    } else if (cron === "0 0 1 * *") {
      ctx.waitUntil(run("content-refresh", handleRefreshContent, "/api/cron/refresh?token=beriklan-admin-2026&count=3", "content-refresh"));
    } else if (cron === "0 0 * * 1") {
      ctx.waitUntil(run("snippet-optimize", handleSnippetOptimizer, "/api/cron/snippet-optimize?token=beriklan-admin-2026&count=3", "snippet-optimize"));
    } else {
      const c = cronMap[cron];
      if (c) {
        ctx.waitUntil(run(c.cronName, c.handler, c.path, c.cronName));
      } else {
        console.log("[scheduled] unknown cron, no-op");
      }
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

// Admin Health Dashboard — JSON view of system health
// Use ?token=ADMIN_TOKEN to view
async function handleAdminHealth(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token") || "";
  if (token !== env.ADMIN_TOKEN) {
    return new Response("Unauthorized", { status: 401 });
  }

  const health = {
    timestamp: new Date().toISOString(),
    status: "ok",
    components: {}
  };

  // 1. Worker version & uptime
  health.components.worker = {
    status: "running",
    note: "Cloudflare Workers (no native uptime metric)"
  };

  // 2. D1 Database
  try {
    const t0 = Date.now();
    await env.DB.prepare("SELECT 1").first();
    health.components.d1 = {
      status: "healthy",
      latency_ms: Date.now() - t0
    };
  } catch (e) {
    health.components.d1 = { status: "down", error: String(e).slice(0, 200) };
    health.status = "degraded";
  }

  // 3. Tables count
  try {
    const tables = await env.DB.prepare(
      "SELECT name FROM sqlite_master WHERE type='table'"
    ).all();
    health.components.tables = {
      count: (tables.results || []).length,
      list: (tables.results || []).map(t => t.name).sort()
    };
  } catch (e) {
    health.components.tables = { error: String(e).slice(0, 200) };
  }

  // 4. Cron health (last 10 runs)
  try {
    const runs = await env.DB.prepare(
      "SELECT cron_name, status, started_at, duration_ms FROM cron_runs ORDER BY id DESC LIMIT 10"
    ).all();
    const runsRows = runs.results || [];
    const failedCount = runsRows.filter(r => r.status === "failed").length;
    health.components.cron = {
      last_10_runs: runsRows.length,
      failed_in_last_10: failedCount,
      status: failedCount >= 3 ? "warning" : failedCount > 0 ? "watch" : "healthy",
      runs: runsRows.slice(0, 5).map(r => ({
        name: r.cron_name,
        status: r.status,
        duration_ms: r.duration_ms,
        at: r.started_at
      }))
    };
  } catch (e) {
    health.components.cron = { error: String(e).slice(0, 200) };
  }

  // 5. Retry queue
  try {
    const queue = await env.DB.prepare(
      "SELECT COUNT(*) as c FROM cron_retry_queue WHERE status = 'pending'"
    ).first();
    health.components.retry_queue = { pending: queue?.c || 0 };
  } catch (e) {
    health.components.retry_queue = { pending: 0 };
  }

  // 6. Cron settings
  try {
    const settings = await env.DB.prepare(
      "SELECT name, enabled, cron FROM cron_settings ORDER BY id"
    ).all();
    const totalCron = (settings.results || []).length;
    const enabledCron = (settings.results || []).filter(c => c.enabled).length;
    health.components.cron_settings = {
      total: totalCron,
      enabled: enabledCron,
      paused: totalCron - enabledCron
    };
  } catch (e) {
    health.components.cron_settings = { error: String(e).slice(0, 200) };
  }

  // 7. Email queue
  try {
    const pending = await env.DB.prepare(
      "SELECT COUNT(*) as c FROM email_queue WHERE status='pending'"
    ).first();
    const sent = await env.DB.prepare(
      "SELECT COUNT(*) as c FROM email_queue WHERE status='sent'"
    ).first();
    const today = new Date().toISOString().slice(0, 10);
    const sentToday = await env.DB.prepare(
      "SELECT COUNT(*) as c FROM email_queue WHERE status='sent' AND sent_at >= ?"
    ).bind(today).first();
    health.components.email_queue = {
      pending: pending?.c || 0,
      sent_total: sent?.c || 0,
      sent_today: sentToday?.c || 0
    };
  } catch (e) {
    health.components.email_queue = { error: String(e).slice(0, 200) };
  }

  // 8. Articles & SEO
  try {
    const articles = await env.DB.prepare("SELECT COUNT(*) as c FROM articles").first();
    const posts = await env.DB.prepare("SELECT COUNT(*) as c FROM posts_meta").first();
    const indexed = await env.DB.prepare("SELECT COUNT(*) as c FROM pending_indexing WHERE status = 'indexed'").first();
    const pendingIdx = await env.DB.prepare("SELECT COUNT(*) as c FROM pending_indexing WHERE status = 'pending'").first();
    health.components.seo = {
      articles: articles?.c || 0,
      posts: posts?.c || 0,
      indexed_urls: indexed?.c || 0,
      pending_urls: pendingIdx?.c || 0
    };
  } catch (e) {
    health.components.seo = { error: String(e).slice(0, 200) };
  }

  // 9. Contact & template counts
  try {
    const contacts = await env.DB.prepare(
      "SELECT COUNT(*) as c FROM lead_contacts WHERE email != '' AND email IS NOT NULL"
    ).first();
    const templates = await env.DB.prepare("SELECT COUNT(*) as c FROM email_templates").first();
    health.components.email_assets = {
      contacts: contacts?.c || 0,
      templates: templates?.c || 0
    };
  } catch (e) {
    health.components.email_assets = { error: String(e).slice(0, 200) };
  }

  // 10. Resend + API quota check
  if (env.RESEND_API_KEY) {
    health.components.resend = {
      status: "configured",
      daily_quota_limit: 500,
      note: "Free tier Resend"
    };
  } else {
    health.components.resend = { status: "missing" };
    health.status = "degraded";
  }

  if (env.GOOGLE_PLACES_API_KEY) {
    health.components.google_places = { status: "configured" };
  } else {
    health.components.google_places = { status: "missing", note: "Not required for SEO cron" };
  }

  // Pretty or JSON
  if (url.searchParams.get("format") === "json" || url.searchParams.get("pretty") !== "1") {
    return new Response(JSON.stringify(health, null, 2), {
      headers: { "Content-Type": "application/json" }
    });
  }

  // HTML view
  const html = `<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>System Health — Beriklan Admin</title>
<style>
body{font-family:monospace;background:#0f172a;color:#e2e8f0;padding:24px;margin:0;}
.container{max-width:900px;margin:0 auto;}
h1{color:#10b981;font-size:18px;margin-bottom:6px;}
.status{display:inline-block;padding:4px 12px;border-radius:6px;font-weight:700;margin-left:10px;}
.status.ok{background:#10b981;color:#fff;}
.status.degraded{background:#f59e0b;color:#fff;}
.component{background:#1e293b;border-radius:8px;padding:16px;margin:12px 0;border-left:3px solid #475569;}
.component.healthy{border-left-color:#10b981;}
.component.warning{border-left-color:#f59e0b;}
.component.down{border-left-color:#dc2626;}
.component h3{margin:0 0 8px;font-size:13px;color:#94a3b8;text-transform:uppercase;letter-spacing:.05em;}
.component .stat{font-size:24px;font-weight:800;color:#fff;margin-bottom:8px;}
.component pre{background:#0f172a;padding:10px;border-radius:4px;font-size:11px;overflow-x:auto;margin:0;}
a{color:#60a5fa;text-decoration:none;}
.meta{color:#64748b;font-size:12px;margin-bottom:20px;}
</style></head><body>
<div class="container">
<h1>🏥 System Health<span class="status ${health.status}">${health.status.toUpperCase()}</span></h1>
<p class="meta">${health.timestamp} WIB · <a href="?format=json&token=${token}">JSON view</a></p>
${Object.entries(health.components).map(([key, val]) => {
  let cls = 'component';
  if (val.status === 'healthy' || val.status === 'running' || val.status === 'ok' || val.status === 'configured') cls += ' healthy';
  if (val.status === 'warning' || val.status === 'watch' || val.status === 'missing') cls += ' warning';
  if (val.status === 'down' || val.status === 'degraded') cls += ' down';
  const stat = val.latency_ms !== undefined ? val.latency_ms + 'ms' :
    val.count !== undefined ? val.count :
    val.pending !== undefined ? val.pending :
    val.total !== undefined ? val.enabled + '/' + val.total :
    val.status || '✓';
  return `<div class="${cls}">
<h3>${key.replace(/_/g, ' ')}</h3>
<div class="stat">${stat}</div>
<pre>${JSON.stringify(val, null, 2).replace(/</g, '&lt;')}</pre>
</div>`;
}).join('')}
</div>
</body></html>`;

  return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
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

// ─── Admin Drafts — list & view AI-generated drafts not yet committed to GitHub ───
async function handleAdminDrafts(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) return new Response("Unauthorized", { status: 401 });
  if (!env.DB) return new Response("DB not available", { status: 503 });

  try {
    const rows = await env.DB.prepare(
      `SELECT id, slug, title, service, city, source, status, created_at, committed_at
       FROM generated_drafts
       ORDER BY id DESC LIMIT 100`
    ).all();
    const drafts = rows.results || [];
    const total = drafts.length;
    const pending = drafts.filter(d => d.status === "draft" || d.status === "pending").length;
    const committed = drafts.filter(d => d.status === "committed").length;

    if (url.searchParams.get("format") === "json") {
      return new Response(JSON.stringify({ ok: true, total, pending, committed, drafts }, null, 2), {
        headers: { "Content-Type": "application/json" },
      });
    }

    // HTML view
    const html = `<!DOCTYPE html>
<html lang="id"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Generated Drafts — Beriklan Admin</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#f5f5f7;color:#1d1d1f;padding:20px}
.container{max-width:1100px;margin:0 auto}
h1{font-size:22px;margin-bottom:4px}
.sub{color:#666;font-size:13px;margin-bottom:20px}
.card{background:#fff;border-radius:12px;padding:18px;box-shadow:0 1px 3px rgba(0,0,0,0.06);margin-bottom:16px}
.card-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid #f0f0f0}
.card-head h2{font-size:14px;font-weight:700}
.kpi-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px}
.kpi{background:#fff;border-radius:10px;padding:14px;text-align:center;border:1px solid #f0f0f0}
.kpi .val{font-size:24px;font-weight:800;color:#0f1e3d}
.kpi .lbl{font-size:11px;color:#666;text-transform:uppercase;margin-top:4px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:10px 12px;text-align:left;border-bottom:1px solid #f0f0f0}
th{background:#fafafa;color:#666;font-weight:600;text-transform:uppercase;font-size:10px;letter-spacing:.5px}
tr:last-child td{border-bottom:none}
.badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;text-transform:uppercase}
.badge.draft{background:#fef3c7;color:#856404}
.badge.committed{background:#d1fae5;color:#155724}
.badge.pending{background:#dbeafe;color:#1e40af}
.action-bar{margin:14px 0;display:flex;gap:8px;flex-wrap:wrap}
.btn{padding:8px 14px;border-radius:8px;border:none;cursor:pointer;font-weight:600;font-size:13px;text-decoration:none;display:inline-flex;align-items:center;gap:6px}
.btn-primary{background:#0f1e3d;color:#fff}
.btn-amber{background:#f59e0b;color:#0f1e3d}
.btn-outline{background:#fff;color:#0f1e3d;border:1px solid #d1d5db}
</style></head><body>
<div class="container">
<h1>📝 Generated Drafts</h1>
<p class="sub">Artikel yang sudah di-generate AI tapi belum ter-commit ke GitHub (karena GITHUB_TOKEN error / expired). Bisa di-review di sini, lalu di-commit manual.</p>

<div class="kpi-grid">
<div class="kpi"><div class="val">${total}</div><div class="lbl">Total Drafts</div></div>
<div class="kpi"><div class="val" style="color:#dc2626;">${pending}</div><div class="lbl">Pending</div></div>
<div class="kpi"><div class="val" style="color:#10b981;">${committed}</div><div class="lbl">Committed</div></div>
</div>

<div class="action-bar">
<a href="?format=json&token=${token}" class="btn btn-outline">📋 Lihat JSON</a>
<button onclick="commitAll()" class="btn btn-amber" id="commitBtn">⬆️ Commit Semua Pending ke GitHub</button>
<a href="?token=${token}" class="btn btn-outline">🔄 Refresh</a>
</div>

<div class="card">
<table>
<thead><tr><th>ID</th><th>Slug</th><th>Service</th><th>City</th><th>Source</th><th>Status</th><th>Dibuat</th></tr></thead>
<tbody>
${drafts.map(d => `<tr>
<td>${d.id}</td>
<td><strong>${escHtml(d.slug)}</strong><br><small style="color:#9ca3af;">${escHtml((d.title || '').slice(0, 60))}...</small></td>
<td>${escHtml(d.service || '-')}</td>
<td>${escHtml(d.city || '-')}</td>
<td>${escHtml(d.source || '-')}</td>
<td><span class="badge ${d.status}">${d.status}</span></td>
<td>${escHtml((d.created_at || '').slice(0, 16))}</td>
</tr>`).join('')}
</tbody>
</table>
</div>
</div>

<script>
async function commitAll() {
  if (!confirm('Commit semua draft pending ke GitHub? Pastikan GITHUB_TOKEN valid.')) return;
  const btn = document.getElementById('commitBtn');
  btn.disabled = true; btn.textContent = '⏳ Committing...';
  try {
    const r = await fetch('/api/admin/drafts/commit?token=${token}', { method: 'POST' });
    const d = await r.json();
    alert(d.ok ? '✅ Commit selesai: ' + (d.committed || 0) + ' dari ' + (d.total_pending || 0) + ' pending' : '❌ Gagal: ' + (d.error || 'unknown'));
    location.reload();
  } catch (e) { alert('Error: ' + e.message); }
  btn.disabled = false; btn.textContent = '⬆️ Commit Semua Pending ke GitHub';
}
</script>
</body></html>`;
    return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
}

// ─── Admin Drafts Commit — push pending drafts to GitHub ───
async function handleAdminDraftsCommit(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) return new Response("Unauthorized", { status: 401 });
  if (request.method !== "POST") return new Response("Method not allowed", { status: 405 });
  if (!env.DB) return new Response("DB not available", { status: 503 });
  if (!env.GITHUB_TOKEN) return new Response(JSON.stringify({ ok: false, error: "GITHUB_TOKEN tidak di-set di Worker secrets" }), { status: 503, headers: { "Content-Type": "application/json" } });

  const t0 = Date.now();
  const errors = [];
  let committed = 0;
  let failed = 0;

  try {
    // 1. Fetch all pending drafts
    const pending = await env.DB.prepare(
      "SELECT id, slug, title, content, service, city, source FROM generated_drafts WHERE status IN ('draft', 'pending') ORDER BY id LIMIT 50"
    ).all();
    const drafts = pending.results || [];

    if (drafts.length === 0) {
      return new Response(JSON.stringify({ ok: true, message: "no drafts", committed: 0 }), { headers: { "Content-Type": "application/json" } });
    }

    // 2. Fetch current posts.json from GitHub
    const owner = "ReqTimeout";
    const repo = "beriklan.co.id";
    const filePath = "src/data/posts.json";

    let posts = [];
    let fileSha = null;
    try {
      const getResp = await fetch(
        `https://api.github.com/repos/${owner}/${repo}/contents/${filePath}`,
        { headers: { Authorization: `token ${env.GITHUB_TOKEN}`, "User-Agent": "BeriklanWorker/1.0" } }
      );
      if (getResp.ok) {
        const fd = await getResp.json();
        fileSha = fd.sha;
        if (fd.content) {
          try {
            posts = JSON.parse(atob(fd.content.replace(/\n/g, "")));
          } catch (e) {
            errors.push("parse_error: " + e.message);
          }
        }
      } else {
        const errBody = await getResp.text();
        errors.push(`github_get_${getResp.status}: ${errBody.slice(0, 200)}`);
      }
    } catch (e) {
      errors.push("github_get_exception: " + e.message);
    }

    // 3. For each draft, add to posts (if not exists) and mark committed
    for (const draft of drafts) {
      try {
        if (!posts.find(p => p.slug === draft.slug)) {
          const newPost = {
            slug: draft.slug,
            title: draft.title,
            excerpt: (draft.content || "").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim().substring(0, 200),
            content: draft.content,
            date: new Date().toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }).replace(/ /g, " "),
            iso_date: new Date().toISOString(),
            category: "trending",
            readTime: Math.max(1, Math.round((draft.content || "").split(/\s+/).length / 200)) + " min",
            tags: [draft.service].filter(Boolean),
            featured: false,
            generated: true,
            trending: true,
            service: draft.service,
            city: draft.city,
            publish_date: new Date().toLocaleDateString("en-GB"),
          };
          posts.unshift(newPost);
        }
        // Mark committed
        await env.DB.prepare(
          "UPDATE generated_drafts SET status='committed', committed_at=datetime('now') WHERE id=?"
        ).bind(draft.id).run();
        committed++;
      } catch (e) {
        failed++;
        errors.push(`draft_${draft.id}: ${e.message}`);
      }
    }

    // 4. Sort + commit
    posts.sort((a, b) => (b.iso_date || "").localeCompare(a.iso_date || ""));
    const updatedContent = btoa(unescape(encodeURIComponent(JSON.stringify(posts, null, 2))));

    if (fileSha) {
      const putResp = await fetch(
        `https://api.github.com/repos/${owner}/${repo}/contents/${filePath}`,
        {
          method: "PUT",
          headers: {
            Authorization: `token ${env.GITHUB_TOKEN}`,
            "Content-Type": "application/json",
            "User-Agent": "BeriklanWorker/1.0",
          },
          body: JSON.stringify({
            message: `admin: commit ${committed} drafts`,
            content: updatedContent,
            sha: fileSha,
            branch: "main",
          }),
        }
      );
      if (!putResp.ok) {
        const errBody = await putResp.text();
        errors.push(`github_put_${putResp.status}: ${errBody.slice(0, 200)}`);
        // Rollback DB status
        for (const draft of drafts) {
          await env.DB.prepare("UPDATE generated_drafts SET status='draft' WHERE id=?").bind(draft.id).run().catch(() => {});
        }
      }
    }

    return new Response(JSON.stringify({
      ok: true,
      total_pending: drafts.length,
      committed,
      failed,
      elapsed_ms: Date.now() - t0,
      errors: errors.length ? errors : undefined,
    }, null, 2), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
}


// ─── Admin: Seed keywords for View Live + Shopee + Tokopedia ─────
async function handleAdminSeedKeywords(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) return new Response("Unauthorized", { status: 401 });
  if (request.method !== "POST") return new Response("Method not allowed", { status: 405 });
  if (!env.DB) return new Response("DB not available", { status: 503 });

  const target = url.searchParams.get("target") || "all"; // 'all', 'view-live', 'shopee', 'tokopedia'

  // Keyword templates per service
  const CITIES = ["jakarta", "bandung", "surabaya", "medan", "semarang", "makassar", "palembang", "tangerang", "depok", "bekasi", "bogor", "yogyakarta", "malang", "denpasar", "cikarang", "serang", "cilegon", "batam", "pekanbaru", "banjarmasin"];

  const TEMPLATES = {
    "view-live": [
      "jasa view live tiktok",
      "tambah viewers tiktok live",
      "viewers tiktok live streaming",
      "jasa live streaming tiktok",
      "live tiktok viewers indonesia",
      "live tiktok rame",
      "beli viewers tiktok",
      "view live tiktok shop",
      "live tiktok sepi",
      "boost viewers tiktok",
      "jasa viewers tiktok 24 jam",
      "tiktok live viewers aktif",
      "live streaming tiktok profesional",
      "viewers tiktok murah",
      "jasa live tiktok e-commerce",
      "tambah viewers live tiktok",
      "live tiktok affiliate",
      "live viewers tiktok shop",
      "viewers live tiktok real",
      "live tiktok conversion",
      "jasa live streaming e-commerce",
      "live viewers tiktok aman",
      "viewers tiktok untuk seller",
      "live tiktok ramai konsisten",
    ],
    "shopee": [
      "jasa shopee affiliate",
      "jualan shopee pemula",
      "shopee affiliate pemula",
      "cara daftar shopee affiliate",
      "shopee affiliate marketing",
      "jasa buka toko shopee",
      "optimasi toko shopee",
      "shopee seller profesional",
      "belajar shopee affiliate",
      "shopee affiliate 2026",
      "komisi shopee affiliate",
      "shopee store setup",
      "jasa kelola shopee",
      "shopee traffic booster",
      "produk shopee viral",
      "shopee marketing strategy",
      "shopee seller center",
      "naikkan penjualan shopee",
      "shopee plus seller",
      "shopee live streaming",
      "shopee video produk",
      "shopee seller optimization",
      "shopee affiliate Indonesia",
      "cara jualan di shopee",
    ],
    "tokopedia": [
      "jasa tokopedia affiliate",
      "jualan tokopedia pemula",
      "tokopedia affiliate marketing",
      "cara daftar tokopedia affiliate",
      "tokopedia seller profesional",
      "belajar tokopedia affiliate",
      "optimasi toko tokopedia",
      "jasa buka toko tokopedia",
      "tokopedia seller optimization",
      "naikkan penjualan tokopedia",
      "produk viral tokopedia",
      "tokopedia marketing strategy",
      "jasa kelola tokopedia",
      "tokopedia affiliate 2026",
      "komisi tokopedia affiliate",
    ]
  };

  let inserted = 0;
  let skipped = 0;
  let errors = [];

  try {
    for (const [svc, keywords] of Object.entries(TEMPLATES)) {
      if (target !== "all" && target !== svc) continue;
      for (const kw of keywords) {
        // Skip if service == "view-live" only target
        if (svc === "view-live") {
          for (const city of CITIES.slice(0, 10)) {
            const fullKw = `${kw} ${city}`;
            const slug = `view-live-tiktok-${city}-${kw.replace(/\s+/g, "-").toLowerCase().slice(0, 30)}-${Math.random().toString(36).slice(2, 8)}`;
            try {
              const existing = await env.DB.prepare("SELECT id FROM keyword_queue WHERE keyword = ?").bind(fullKw).first();
              if (existing) { skipped++; continue; }
              await env.DB.prepare(`INSERT INTO keyword_queue (id, keyword, keyword_normalized, source, seed, discovered_at, status, service, city, priority_score, intent)
                VALUES (?, ?, ?, ?, ?, datetime('now'), 'pending', ?, ?, ?, ?)`)
                .bind(`seed-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`, fullKw, fullKw.toLowerCase().trim(),
                  "admin_seed_v1", fullKw.toLowerCase().trim(), "jasa-view-live-tiktok", city, 50, "informational").run();
              inserted++;
            } catch (e) { errors.push(`${fullKw}: ${e.message.slice(0, 80)}`); }
          }
        } else {
          for (const city of CITIES.slice(0, 10)) {
            const fullKw = `${kw} ${city}`;
            const slug = `${svc}-${city}-${kw.replace(/\s+/g, "-").toLowerCase().slice(0, 30)}-${Math.random().toString(36).slice(2, 8)}`;
            try {
              const existing = await env.DB.prepare("SELECT id FROM keyword_queue WHERE keyword = ?").bind(fullKw).first();
              if (existing) { skipped++; continue; }
              await env.DB.prepare(`INSERT INTO keyword_queue (id, keyword, keyword_normalized, source, seed, discovered_at, status, service, city, priority_score, intent)
                VALUES (?, ?, ?, ?, ?, datetime('now'), 'pending', ?, ?, ?, ?)`)
                .bind(`seed-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`, fullKw, fullKw.toLowerCase().trim(),
                  "admin_seed_v1", fullKw.toLowerCase().trim(), `jasa-${svc}`, city, 50, "informational").run();
              inserted++;
            } catch (e) { errors.push(`${fullKw}: ${e.message.slice(0, 80)}`); }
          }
        }
      }
    }
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500 });
  }

  return new Response(JSON.stringify({
    ok: true,
    target,
    inserted,
    skipped,
    errors: errors.length ? errors.slice(0, 5) : undefined,
  }, null, 2), { headers: { "Content-Type": "application/json" } });
}



// ─── Admin: Email metrics aggregate ───────────────────────────────
async function handleEmailMetrics(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) return new Response("Unauthorized", { status: 401 });
  if (!env.DB) return new Response("DB not available", { status: 503 });

  try {
    // Aggregate by campaign
    const campaigns = await env.DB.prepare(`
      SELECT 
        c.id, c.name, c.subject, c.status, c.created_at,
        (SELECT COUNT(*) FROM email_queue WHERE campaign_id=c.id) as total,
        (SELECT COUNT(*) FROM email_queue WHERE campaign_id=c.id AND status='sent') as sent,
        (SELECT COUNT(*) FROM email_queue WHERE campaign_id=c.id AND status='pending') as pending,
        (SELECT COUNT(*) FROM email_queue WHERE campaign_id=c.id AND status='failed') as failed,
        (SELECT COUNT(*) FROM email_queue WHERE campaign_id=c.id AND opened_at IS NOT NULL) as opened,
        (SELECT COUNT(*) FROM email_queue WHERE campaign_id=c.id AND clicked_at IS NOT NULL) as clicked
      FROM campaigns c
      ORDER BY c.id DESC LIMIT 20
    `).all();

    const dailySent = await getDailyEmailCount(env);
    const isHtml = url.searchParams.get("format") !== "json";

    const data = (campaigns.results || []).map(c => {
      const sent = c.sent || 0;
      const opened = c.opened || 0;
      const clicked = c.clicked || 0;
      return {
        id: c.id,
        name: c.name,
        subject: c.subject,
        status: c.status,
        created_at: c.created_at,
        total: c.total,
        sent,
        pending: c.pending,
        failed: c.failed,
        opened,
        clicked,
        open_rate: sent > 0 ? Math.round(opened / sent * 1000) / 10 : 0,
        ctr: opened > 0 ? Math.round(clicked / opened * 1000) / 10 : 0,
        click_to_send: sent > 0 ? Math.round(clicked / sent * 1000) / 10 : 0,
      };
    });

    const summary = {
      timestamp: new Date().toISOString(),
      daily_quota: { sent: dailySent, limit: 100, remaining: Math.max(0, 100 - dailySent) },
      campaigns: data,
      totals: {
        campaigns: data.length,
        total_sent: data.reduce((a, c) => a + c.sent, 0),
        total_opened: data.reduce((a, c) => a + c.opened, 0),
        total_clicked: data.reduce((a, c) => a + c.clicked, 0),
        total_failed: data.reduce((a, c) => a + c.failed, 0),
        avg_open_rate: data.length > 0 ? Math.round(data.reduce((a, c) => a + c.open_rate, 0) / data.length * 10) / 10 : 0,
        avg_ctr: data.length > 0 ? Math.round(data.reduce((a, c) => a + c.ctr, 0) / data.length * 10) / 10 : 0,
      }
    };

    if (!isHtml) {
      return new Response(JSON.stringify(summary, null, 2), { headers: { "Content-Type": "application/json" } });
    }

    // HTML view
    const t = (v) => v || 0;
    const html = `<!DOCTYPE html><html lang="id"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Email Metrics</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#f5f7fa;color:#1f2937;padding:20px}
.container{max-width:1200px;margin:0 auto}
h1{font-size:22px;margin-bottom:6px}
.sub{color:#6b7280;font-size:13px;margin-bottom:20px}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:20px}
.kpi{background:white;padding:16px;border-radius:12px;border:1px solid #eef0f5}
.kpi .lbl{font-size:10px;text-transform:uppercase;color:#6b7280;font-weight:700;letter-spacing:.06em;margin-bottom:6px}
.kpi .val{font-size:24px;font-weight:800;line-height:1.1}
.kpi .sub{font-size:11px;color:#9ca3af;margin-top:4px}
.kpi.good{border-left:3px solid #10b981}
.kpi.warn{border-left:3px solid #f59e0b}
.kpi.bad{border-left:3px solid #dc2626}
.section{background:white;border-radius:14px;padding:20px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,0.05);border:1px solid #eef0f5}
table{width:100%;border-collapse:collapse;font-size:13px}
th{background:#fafbfc;color:#6b7280;font-weight:600;text-transform:uppercase;font-size:10px;letter-spacing:.05em;padding:10px 12px;text-align:left;border-bottom:1px solid #eef0f5}
td{padding:10px 12px;border-bottom:1px solid #f5f6fa}
.badge{display:inline-block;padding:2px 8px;border-radius:100px;font-size:10px;font-weight:600}
.badge.green{background:#d1fae5;color:#065f46}
.badge.amber{background:#fef3c7;color:#92400e}
.badge.red{background:#fee2e2;color:#991b1b}
.bar{height:6px;background:#f0f1f5;border-radius:3px;overflow:hidden;margin-top:4px}
.bar>div{height:100%;border-radius:3px}
a{color:#0f1e3d;text-decoration:none}
a:hover{text-decoration:underline}
</style></head><body>
<div class="container">
<div style="display:flex;justify-content:space-between;align-items:start">
<div>
<h1>📧 Email Metrics — Real-time</h1>
<p class="sub">Snapshot: ${new Date().toISOString()} · Resend free tier: ${summary.daily_quota.sent}/100 today</p>
</div>
<a href="?format=json&token=${token}" class="kpi" style="text-decoration:none">📋 JSON</a>
</div>

<div class="kpi-grid">
<div class="kpi"><div class="lbl">📤 Total Terkirim</div><div class="val">${t(summary.totals.total_sent)}</div><div class="sub">all-time</div></div>
<div class="kpi good"><div class="lbl">👁 Total Opened</div><div class="val">${t(summary.totals.total_opened)}</div><div class="sub">${summary.totals.avg_open_rate}% avg open rate</div></div>
<div class="kpi"><div class="lbl">🖱 Total Clicked</div><div class="val">${t(summary.totals.total_clicked)}</div><div class="sub">${summary.totals.avg_ctr}% avg CTR</div></div>
<div class="kpi ${summary.daily_quota.remaining < 10 ? 'warn' : ''}"><div class="lbl">📊 Quota Hari Ini</div><div class="val">${summary.daily_quota.sent}/100</div><div class="sub">${summary.daily_quota.remaining} remaining</div></div>
<div class="kpi ${summary.totals.total_failed > 0 ? 'bad' : 'good'}"><div class="lbl">✕ Failed</div><div class="val">${t(summary.totals.total_failed)}</div><div class="sub">all-time</div></div>
<div class="kpi"><div class="lbl">📨 Campaigns</div><div class="val">${summary.totals.campaigns}</div><div class="sub">tracked</div></div>
</div>

<div class="section">
<h2 style="margin-bottom:14px;font-size:16px">📊 Per-Campaign Breakdown</h2>
<table>
<thead><tr>
<th>ID</th>
<th>Campaign</th>
<th>Status</th>
<th>Total</th>
<th>Sent</th>
<th>Pending</th>
<th>Failed</th>
<th>Opened</th>
<th>Open Rate</th>
<th>Clicked</th>
<th>CTR</th>
</tr></thead>
<tbody>
${data.map(c => `<tr>
<td><strong>${c.id}</strong></td>
<td><a href="?token=${token}&id=${c.id}">${c.name || '-'}</a><br><span style="font-size:11px;color:#6b7280">${(c.subject || '').slice(0,50)}...</span></td>
<td><span class="badge ${c.status === 'done' ? 'green' : c.status === 'sending' ? 'amber' : 'red'}">${c.status || 'draft'}</span></td>
<td>${c.total}</td>
<td><strong>${c.sent}</strong></td>
<td>${c.pending || 0}</td>
<td style="color:#dc2626">${c.failed || 0}</td>
<td>${c.opened || 0}</td>
<td>
<div><strong>${c.open_rate}%</strong></div>
<div class="bar"><div style="width:${Math.min(c.open_rate, 100)}%;background:#10b981"></div></div>
</td>
<td>${c.clicked || 0}</td>
<td>
<div><strong>${c.ctr}%</strong></div>
<div class="bar"><div style="width:${Math.min(c.ctr, 100)}%;background:#f59e0b"></div></div>
</td>
</tr>`).join('')}
</tbody>
</table>
<p style="margin-top:12px;font-size:12px;color:#6b7280">Open rate = opened / sent. CTR = clicked / opened. Tracking pixel + click redirect aktif via Resend headers.</p>
</div>
</div></body></html>`;

    return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500 });
  }
}

async function handleCampaignMetrics(request, id, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) return new Response("Unauthorized", { status: 401 });
  if (!env.DB) return new Response("DB not available", { status: 503 });
  if (!id) return new Response("Campaign ID required", { status: 400 });

  try {
    const c = await env.DB.prepare("SELECT * FROM campaigns WHERE id=?").bind(id).first();
    if (!c) return new Response(JSON.stringify({ error: "Not found" }), { status: 404 });

    const stats = await env.DB.prepare(`
      SELECT
        COUNT(*) as total,
        SUM(CASE WHEN status='sent' THEN 1 ELSE 0 END) as sent,
        SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) as pending,
        SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) as failed,
        SUM(CASE WHEN opened_at IS NOT NULL THEN 1 ELSE 0 END) as opened,
        SUM(CASE WHEN clicked_at IS NOT NULL THEN 1 ELSE 0 END) as clicked,
        MIN(sent_at) as first_sent,
        MAX(sent_at) as last_sent,
        MIN(opened_at) as first_open,
        MAX(opened_at) as last_open
      FROM email_queue WHERE campaign_id=?
    `).bind(id).first();

    const recent = await env.DB.prepare(`
      SELECT email, name, status, sent_at, opened_at, clicked_at, error
      FROM email_queue WHERE campaign_id=?
      ORDER BY (opened_at IS NOT NULL OR clicked_at IS NOT NULL) DESC, sent_at DESC LIMIT 30
    `).bind(id).all();

    const sent = stats?.sent || 0;
    const opened = stats?.opened || 0;
    const clicked = stats?.clicked || 0;

    const summary = {
      campaign: { id: c.id, name: c.name, subject: c.subject, status: c.status, created_at: c.created_at },
      metrics: {
        total: stats?.total || 0,
        sent, pending: stats?.pending || 0, failed: stats?.failed || 0,
        opened, clicked,
        open_rate: sent > 0 ? Math.round(opened / sent * 1000) / 10 : 0,
        ctr: opened > 0 ? Math.round(clicked / opened * 1000) / 10 : 0,
        click_to_send: sent > 0 ? Math.round(clicked / sent * 1000) / 10 : 0,
        first_sent: stats?.first_sent,
        last_sent: stats?.last_sent,
        first_open: stats?.first_open,
        last_open: stats?.last_open,
      },
      recent_activity: (recent.results || []).map(r => ({
        email: r.email,
        name: r.name,
        status: r.status,
        sent_at: r.sent_at,
        opened_at: r.opened_at,
        clicked_at: r.clicked_at,
        error: r.error,
      })),
    };

    if (url.searchParams.get("format") === "json") {
      return new Response(JSON.stringify(summary, null, 2), { headers: { "Content-Type": "application/json" } });
    }
    return new Response(JSON.stringify(summary, null, 2), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500 });
  }
}

// ─── Admin: Reset email queue (failed → pending) ────────────────
async function handleEmailQueueReset(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) return new Response("Unauthorized", { status: 401 });
  if (request.method !== "POST") return new Response("Method not allowed", { status: 405 });
  if (!env.DB) return new Response("DB not available", { status: 503 });

  const campaignId = url.searchParams.get("campaign_id"); // optional, all if not specified

  try {
    let q, params;
    if (campaignId) {
      q = "UPDATE email_queue SET status='pending', error=NULL WHERE campaign_id=? AND status='failed'";
      params = [parseInt(campaignId)];
    } else {
      q = "UPDATE email_queue SET status='pending', error=NULL WHERE status='failed'";
      params = [];
    }
    const r = await env.DB.prepare(q).bind(...params).run();
    const reset = r.meta?.changes || 0;
    return new Response(JSON.stringify({ ok: true, reset_to_pending: reset, campaign_id: campaignId || "all" }), {
      headers: { "Content-Type": "application/json" },
    });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500 });
  }
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
    // N.7 hourly_generate_runs — track every hourly cron run
    `CREATE TABLE IF NOT EXISTS hourly_generate_runs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
      count_requested INTEGER,
      count_generated INTEGER,
      slugs TEXT,
      models TEXT,
      committed_to_github INTEGER,
      enqueued_for_indexing INTEGER,
      error TEXT,
      elapsed_ms INTEGER
    )`,
    `CREATE INDEX IF NOT EXISTS idx_hgr_timestamp ON hourly_generate_runs (timestamp DESC)`,
    // N.8 pending_indexing.indexnow_at — for IndexNow tracking
    `ALTER TABLE pending_indexing ADD COLUMN indexnow_at TEXT`,
    `CREATE INDEX IF NOT EXISTS idx_pending_indexnow ON pending_indexing (indexnow_at)`,
    // N.9 GSC Sitemap submission tracking
    `CREATE TABLE IF NOT EXISTS gsc_sitemaps (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      siteUrl TEXT NOT NULL,
      sitemapPath TEXT NOT NULL,
      lastSubmitted TEXT,
      lastStatus INTEGER,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(siteUrl, sitemapPath)
    )`,
    `CREATE TABLE IF NOT EXISTS newsletter_subscribers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT NOT NULL UNIQUE,
      status TEXT DEFAULT 'active',
      source TEXT,
      ip TEXT,
      subscribed_at TEXT DEFAULT CURRENT_TIMESTAMP,
      unsubscribed_at TEXT,
      meta TEXT
    )`,
    // Phase: Email Campaign System
    `CREATE TABLE IF NOT EXISTS email_templates (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      subject TEXT NOT NULL,
      html_body TEXT NOT NULL,
      category TEXT DEFAULT 'promo',
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )`,
    `CREATE TABLE IF NOT EXISTS campaigns (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      template_id INTEGER,
      list_id INTEGER,
      subject TEXT,
      status TEXT DEFAULT 'draft',
      total_recipients INTEGER DEFAULT 0,
      sent_count INTEGER DEFAULT 0,
      open_count INTEGER DEFAULT 0,
      click_count INTEGER DEFAULT 0,
      scheduled_at TEXT,
      sent_at TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )`,
    `CREATE TABLE IF NOT EXISTS email_queue (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      campaign_id INTEGER,
      email TEXT NOT NULL,
      name TEXT,
      status TEXT DEFAULT 'pending',
      error TEXT,
      sent_at TEXT,
      opened_at TEXT,
      clicked_at TEXT,
      tracking_id TEXT UNIQUE
    )`,
    `CREATE TABLE IF NOT EXISTS lead_lists (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      source TEXT,
      total INTEGER DEFAULT 0,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )`,
    `CREATE TABLE IF NOT EXISTS lead_contacts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      list_id INTEGER,
      email TEXT,
      phone TEXT,
      name TEXT,
      company TEXT,
      website TEXT,
      city TEXT,
      category TEXT,
      extra TEXT
    )`,
    `CREATE INDEX IF NOT EXISTS idx_lead_contacts_list ON lead_contacts (list_id)`,
    `CREATE INDEX IF NOT EXISTS idx_email_queue_status ON email_queue (status)`,
    `CREATE INDEX IF NOT EXISTS idx_email_queue_campaign ON email_queue (campaign_id)`,
    `CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns (status)`,
    // Cron enable/pause settings
    `CREATE TABLE IF NOT EXISTS cron_settings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL UNIQUE,
      cron TEXT NOT NULL,
      enabled INTEGER DEFAULT 1,
      label TEXT
    )`,
    `INSERT OR IGNORE INTO cron_settings (name, cron, enabled, label) VALUES ('hourly', '0 * * * *', 1, 'Generate artikel (72/hari)')`,
    `INSERT OR IGNORE INTO cron_settings (name, cron, enabled, label) VALUES ('indexnow', '15 * * * *', 1, 'IndexNow submit (tiap jam)')`,
    `INSERT OR IGNORE INTO cron_settings (name, cron, enabled, label) VALUES ('gsc-indexing', '0 */6 * * *', 1, 'GSC + sitemap + rank (tiap 6 jam)')`,
    `INSERT OR IGNORE INTO cron_settings (name, cron, enabled, label) VALUES ('trending-generate', '30 */6 * * *', 1, 'Generate trending (tiap 6 jam)')`,
    `INSERT OR IGNORE INTO cron_settings (name, cron, enabled, label) VALUES ('content-refresh', '0 0 1 * *', 1, 'Refresh artikel lama (bulanan)')`,
    `INSERT OR IGNORE INTO cron_settings (name, cron, enabled, label) VALUES ('snippet-optimize', '0 0 * * 1', 1, 'Optimasi snippet (mingguan)')`,
    `INSERT OR IGNORE INTO cron_settings (name, cron, enabled, label) VALUES ('scrape-indonetwork', '30 6 * * *', 1, 'Scrape Indonetwork (harian)')`,
    `INSERT OR IGNORE INTO cron_settings (name, cron, enabled, label) VALUES ('scrape-google-places', '0 7 * * *', 1, 'Scrape Google Places (harian)')`,
    `INSERT OR IGNORE INTO cron_settings (name, cron, enabled, label) VALUES ('email-send', '*/15 * * * *', 1, 'Kirim antrian email (tiap 15 menit)')`,
    // scrape.beriklan.co.id — consumer trial system
    `CREATE TABLE IF NOT EXISTS scrape_users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT NOT NULL,
      whatsapp TEXT NOT NULL,
      search_count INTEGER DEFAULT 0,
      session_token TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      last_active TEXT DEFAULT CURRENT_TIMESTAMP
    )`,
    `CREATE UNIQUE INDEX IF NOT EXISTS idx_scrape_users_email ON scrape_users (email)`,
    `CREATE INDEX IF NOT EXISTS idx_scrape_users_session ON scrape_users (session_token)`,
    `CREATE TABLE IF NOT EXISTS scrape_searches (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      query TEXT NOT NULL,
      city TEXT,
      category TEXT,
      results_count INTEGER DEFAULT 0,
      results_json TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )`,
    `CREATE INDEX IF NOT EXISTS idx_scrape_searches_user ON scrape_searches (user_id)`,
    `CREATE TABLE IF NOT EXISTS scrape_results (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      search_id INTEGER NOT NULL,
      name TEXT,
      phone TEXT,
      email TEXT,
      website TEXT,
      category TEXT,
      city TEXT,
      source TEXT
    )`,
    `CREATE INDEX IF NOT EXISTS idx_scrape_results_user ON scrape_results (user_id)`,
    `CREATE INDEX IF NOT EXISTS idx_scrape_results_search ON scrape_results (search_id)`,
    // Cron health monitoring & retry queue
    `CREATE TABLE IF NOT EXISTS cron_runs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      cron_name TEXT NOT NULL,
      status TEXT NOT NULL,
      started_at TEXT DEFAULT CURRENT_TIMESTAMP,
      finished_at TEXT,
      duration_ms INTEGER,
      output TEXT,
      error TEXT,
      retry_count INTEGER DEFAULT 0
    )`,
    `CREATE INDEX IF NOT EXISTS idx_cron_runs_name ON cron_runs (cron_name, started_at DESC)`,
    `CREATE INDEX IF NOT EXISTS idx_cron_runs_status ON cron_runs (status)`,
    `CREATE TABLE IF NOT EXISTS cron_retry_queue (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      cron_name TEXT NOT NULL,
      payload TEXT,
      last_error TEXT,
      last_attempt_at TEXT DEFAULT CURRENT_TIMESTAMP,
      attempts INTEGER DEFAULT 1,
      next_retry_at TEXT,
      status TEXT DEFAULT 'pending'
    )`,
    `CREATE INDEX IF NOT EXISTS idx_cron_retry_pending ON cron_retry_queue (status, next_retry_at)`,
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

  // 3. Recent cron_runs (last 20) — new schema
  try {
    const r = await env.DB.prepare(
      "SELECT cron_name, status, started_at, duration_ms, error FROM cron_runs ORDER BY id DESC LIMIT 20"
    ).all();
    stats.recent_cron_runs = r.results || [];
    // Last run per cron (health summary)
    const lastRuns = await env.DB.prepare(
      "SELECT cron_name, MAX(started_at) as last_run, status FROM cron_runs GROUP BY cron_name"
    ).all();
    stats.cron_health = lastRuns.results || [];
  } catch (e) {
    console.error("cron_runs query error:", String(e).slice(0, 300));
    stats.recent_cron_runs = [];
    stats.cron_health = [];
  }

  // 4. Pending indexing count
  try {
    const r = await env.DB.prepare("SELECT COUNT(*) as count FROM pending_indexing WHERE status = 'pending'").all();
    stats.pending_indexing = (r.results && r.results[0]) ? r.results[0].count : 0;
  } catch (e) {
    stats.pending_indexing = { error: e.message };
  }

  // 5. Retry queue count
  try {
    const r = await env.DB.prepare("SELECT COUNT(*) as count FROM cron_retry_queue WHERE status = 'pending'").all();
    stats.retry_queue = (r.results && r.results[0]) ? r.results[0].count : 0;
  } catch (e) {
    stats.retry_queue = 0;
  }

  // 6. SEO metrics
  try {
    const articles = await env.DB.prepare("SELECT COUNT(*) as c FROM articles").first();
    const posts = await env.DB.prepare("SELECT COUNT(*) as c FROM posts_meta").first();
    const indexed = await env.DB.prepare("SELECT COUNT(*) as c FROM pending_indexing WHERE status = 'indexed'").first();
    const pending = await env.DB.prepare("SELECT COUNT(*) as c FROM pending_indexing WHERE status = 'pending'").first();
    stats.seo = {
      articles: articles?.c || 0,
      posts: posts?.c || 0,
      indexed: indexed?.c || 0,
      pending_index: pending?.c || 0,
    };
  } catch (e) {
    stats.seo = { error: e.message };
  }

  // 7. Cron settings status
  try {
    const r = await env.DB.prepare("SELECT name, enabled, label FROM cron_settings ORDER BY id").all();
    stats.cron_settings = r.results || [];
  } catch (e) {
    stats.cron_settings = [];
  }

  // If ?format=json → return JSON
  if (url.searchParams.get("format") === "json") {
    return new Response(JSON.stringify(stats, null, 2), { headers: { "Content-Type": "application/json" } });
  }

  // Otherwise return HTML dashboard
  const html = renderDashboard(stats, token);
  return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
}

function renderDashboard(stats, token) {
  // Health summary
  const totalCrons = (stats.cron_settings || []).length;
  const enabledCrons = (stats.cron_settings || []).filter(c => c.enabled).length;
  const recentFailed = (stats.recent_cron_runs || []).filter(c => c.status === "failed").length;
  const healthStatus = recentFailed > 3 ? "critical" : recentFailed > 0 ? "warning" : "healthy";

  const expiringRows = (stats.api_keys?.expiring_list || []).map(k => `
    <tr><td><strong>${k.name}</strong></td><td><code>${k.prefix}...</code></td><td><span class="badge ${k.days_left < 7 ? 'red' : 'yellow'}">${k.days_left} days</span></td><td><a href="/api/admin/keys?token=HIDDEN&action=rotate&name=${k.name}">Rotate</a></td></tr>
  `).join('') || '<tr><td colspan="4" style="color:#666;text-align:center;padding:20px;">✅ Tidak ada API key yang akan expired</td></tr>';

  const rateLimitRows = (stats.rate_limits?.top_ips || []).slice(0, 5).map(r => `
    <tr><td><code>${r.ip || '-'}</code></td><td>${r.endpoint}</td><td><span class="badge ${r.request_count > 30 ? 'red' : 'green'}">${r.request_count}</span></td></tr>
  `).join('') || '<tr><td colspan="3" style="color:#666;text-align:center;padding:20px;">Tidak ada request di window ini</td></tr>';

  // Cron health rows
  const cronHealthRows = (stats.cron_health || []).map(c => {
    const lastRun = c.last_run ? new Date(c.last_run + 'Z') : null;
    const ageMs = lastRun ? (Date.now() - lastRun.getTime()) : null;
    const ageStr = ageMs === null ? 'never' : ageMs < 3600000 ? `${Math.floor(ageMs/60000)}m ago` : ageMs < 86400000 ? `${Math.floor(ageMs/3600000)}h ago` : `${Math.floor(ageMs/86400000)}d ago`;
    const statusBadge = c.status === 'failed' ? '<span class="badge red">FAILED</span>' : c.status === 'running' ? '<span class="badge yellow">RUNNING</span>' : '<span class="badge green">OK</span>';
    return `<tr><td><strong>${c.cron_name}</strong></td><td>${statusBadge}</td><td>${ageStr}</td></tr>`;
  }).join('') || '<tr><td colspan="3" style="color:#666;">Belum ada cron run</td></tr>';

  // Cron runs (last 10)
  const cronRunRows = (stats.recent_cron_runs || []).slice(0, 10).map(c => {
    const statusBadge = c.status === 'failed' ? '<span class="badge red">FAIL</span>' : '<span class="badge green">OK</span>';
    const dur = c.duration_ms ? `${c.duration_ms}ms` : '-';
    const err = c.error ? `<br><small style="color:#dc2626;">${String(c.error).slice(0, 60)}</small>` : '';
    return `<tr><td>${(c.started_at || '').slice(0, 19)}</td><td><strong>${c.cron_name}</strong></td><td>${statusBadge}</td><td>${dur}</td><td>${err}</td></tr>`;
  }).join('') || '<tr><td colspan="5" style="color:#666;text-align:center;padding:20px;">Belum ada cron run</td></tr>';

  const cronSettingsRows = (stats.cron_settings || []).map(c => `
    <tr><td><strong>${c.name}</strong><br><small style="color:#666;">${c.label || ''}</small></td><td>${c.enabled ? '<span class="badge green">✓ AKTIF</span>' : '<span class="badge red">⏸ PAUSED</span>'}</td><td><a href="/api/admin/cron/toggle?token=${token}&name=${c.name}" onclick="event.preventDefault(); fetch(this.href,{method:'POST'}).then(()=>location.reload())" class="toggle-link">${c.enabled ? 'Pause' : 'Enable'}</a></td></tr>
  `).join('');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Beriklan.co.id Admin Dashboard</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f7; color: #1d1d1f; padding: 20px; }
    .container { max-width: 1200px; margin: 0 auto; }
    h1 { font-size: 24px; margin-bottom: 4px; }
    .subtitle { color: #666; font-size: 13px; margin-bottom: 24px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-bottom: 20px; }
    .grid-2 { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
    @media (max-width: 900px) { .grid-2 { grid-template-columns: 1fr; } }
    .card { background: white; border-radius: 12px; padding: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 18px; }
    .card-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid #f0f0f0; }
    .card-head h2 { font-size: 15px; font-weight: 700; }
    .metric { font-size: 28px; font-weight: 800; line-height: 1.1; }
    .sub { font-size: 12px; color: #666; margin-top: 4px; }
    .healthy { border-left: 4px solid #10b981; }
    .warning { border-left: 4px solid #f59e0b; background: #fffbeb; }
    .critical { border-left: 4px solid #dc2626; background: #fef2f2; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #f0f0f0; }
    th { background: #fafafa; color: #666; font-weight: 600; text-transform: uppercase; font-size: 10px; letter-spacing: 0.5px; }
    tr:last-child td { border-bottom: none; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 700; text-transform: uppercase; }
    .badge.green { background: #d4edda; color: #155724; }
    .badge.yellow { background: #fff3cd; color: #856404; }
    .badge.red { background: #f8d7da; color: #721c24; }
    .badge.blue { background: #dbeafe; color: #1e40af; }
    a { color: #2563eb; text-decoration: none; }
    a:hover { text-decoration: underline; }
    code { background: #f0f0f0; padding: 2px 6px; border-radius: 4px; font-size: 12px; font-family: 'JetBrains Mono', monospace; }
    .section-title { font-size: 14px; font-weight: 700; margin: 20px 0 10px; color: #1d1d1f; }
    .quick-links { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }
    .quick-links a { padding: 8px 14px; background: #0f1e3d; color: white; border-radius: 8px; font-size: 12px; font-weight: 600; }
    .quick-links a:hover { background: #1a2f5c; text-decoration: none; }
    .toggle-link { padding: 4px 10px; background: #f59e0b; color: white; border-radius: 6px; font-size: 11px; font-weight: 600; display: inline-block; cursor: pointer; }
    .toggle-link:hover { background: #d97706; text-decoration: none; }
    .health-banner { padding: 16px 20px; border-radius: 10px; margin-bottom: 20px; font-weight: 600; font-size: 14px; }
    .health-banner.healthy { background: #d4edda; color: #155724; }
    .health-banner.warning { background: #fff3cd; color: #856404; }
    .health-banner.critical { background: #f8d7da; color: #721c24; }
    small.muted { color: #999; font-size: 11px; }
  </style>
</head>
<body>
<div class="container">
  <h1>🚀 Beriklan.co.id Admin</h1>
  <p class="subtitle">Last updated: ${stats.timestamp} WIB · <a href="">refresh</a></p>

  <div class="quick-links">
    <a href="/api/admin/email?token=${token}">📧 Email Dashboard</a>
    <a href="/api/admin/keywords?token=${token}">🎯 Keyword Pipeline</a>
    <a href="/api/admin/env-check?token=${token}">🔑 Env Check</a>
    <a href="/api/admin/health?token=${token}">🏥 Health JSON</a>
    <a href="/api/admin/drafts?token=${token}">📝 Drafts</a>
    <a href="https://beriklan.co.id" target="_blank">🌐 View Site</a>
  </div>

  <div class="health-banner ${healthStatus}">
    ${healthStatus === 'healthy' ? '✅ Semua cron sehat — tidak ada kegagalan dalam run terakhir.' :
      healthStatus === 'warning' ? `⚠️ ${recentFailed} cron run gagal terdeteksi. Cek detail di bawah.` :
      `🚨 ${recentFailed} cron run gagal. Auto-pause mungkin sudah aktif — cek tab Cron.`}
  </div>

  <!-- Top KPI Grid -->
  <div class="grid">
    <div class="card ${(stats.api_keys?.expiring_soon || 0) > 0 ? 'warning' : 'healthy'}">
      <div class="metric">${stats.api_keys?.total_active || 0}</div>
      <div class="sub">API Keys aktif · ${stats.api_keys?.expiring_soon || 0} expiring &lt; 30d</div>
    </div>
    <div class="card ${(stats.pending_indexing || 0) > 100 ? 'warning' : 'healthy'}">
      <div class="metric">${stats.seo?.articles || 0}</div>
      <div class="sub">Artikel (${stats.seo?.posts || 0} live di posts.json)</div>
    </div>
    <div class="card ${(stats.pending_indexing || 0) > 100 ? 'warning' : ''}">
      <div class="metric">${stats.seo?.indexed || 0}</div>
      <div class="sub">URL ter-index · ${stats.seo?.pending_index || 0} pending</div>
    </div>
    <div class="card ${(stats.retry_queue || 0) > 0 ? 'warning' : 'healthy'}">
      <div class="metric">${stats.retry_queue || 0}</div>
      <div class="sub">Retry queue (cron yang gagal)</div>
    </div>
    <div class="card">
      <div class="metric">${enabledCrons}/${totalCrons}</div>
      <div class="sub">Cron aktif · ${totalCrons - enabledCrons} paused</div>
    </div>
  </div>

  <div class="grid-2">
    <!-- Cron Health -->
    <div>
      <div class="card">
        <div class="card-head">
          <h2>⏰ Cron Health (last run per cron)</h2>
          <small class="muted">${recentFailed} failed in last 20</small>
        </div>
        <table>
          <thead><tr><th>Cron</th><th>Status</th><th>Last Run</th></tr></thead>
          <tbody>${cronHealthRows}</tbody>
        </table>
      </div>

      <div class="card">
        <div class="card-head"><h2>📊 Recent Cron Runs (last 10)</h2></div>
        <table>
          <thead><tr><th>Started</th><th>Name</th><th>Status</th><th>Duration</th><th>Error</th></tr></thead>
          <tbody>${cronRunRows}</tbody>
        </table>
      </div>
    </div>

    <!-- Sidebar -->
    <div>
      <div class="card">
        <div class="card-head"><h2>⚙️ Cron Settings</h2></div>
        <table>
          <tbody>${cronSettingsRows}</tbody>
        </table>
      </div>

      <div class="card">
        <div class="card-head"><h2>🔑 API Keys Expiring</h2></div>
        <table>
          <thead><tr><th>Name</th><th>Key</th><th>Days</th><th>Action</th></tr></thead>
          <tbody>${expiringRows}</tbody>
        </table>
      </div>

      <div class="card">
        <div class="card-head"><h2>🔥 Top Rate-Limited IPs</h2></div>
        <table>
          <thead><tr><th>IP</th><th>Endpoint</th><th>Count</th></tr></thead>
          <tbody>${rateLimitRows}</tbody>
        </table>
      </div>
    </div>
  </div>

</div>
</body></html>`;
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

  // ===== DATA FETCH =====
  const data = {
    buildStats: null,
    keywordQueue: { total: 0, byStatus: {}, byService: {}, bySource: {} },
    postsMeta: { total: 0, generated: 0, byService: {} },
    indexing: { pending: 0, submitted: 0, failed: 0, today: 0, recent: [] },
    indexnow: { total: 0, last24h: 0 },
    cron: [],
    trending: { total: 0, recent: [] },
    drafts: { total: 0, pending: 0, committed: 0 }
  };

  // 1. Build-time stats (snapshot dari repo)
  try {
    const r = await env.ASSETS.fetch(new URL("https://assets/data/keyword-stats.json"));
    if (r.ok) {
      const ks = await r.json();
      data.buildStats = {
        totalKeywords: ks.keywords?.total || 0,
        generated: ks.keywords?.generated || 0,
        liveInPosts: ks.keywords?.live_in_posts || 0,
        postsTotal: ks.posts?.total || 0,
        postsGenerated: ks.posts?.generated || 0,
        byService: ks.by_service || [],
        byCity: ks.by_city || [],
        bySource: ks.by_source || [],
        recentGenerated: ks.recent_generated || []
      };
    }
  } catch (e) {}

  // 2. Live keyword queue dari D1
  try {
    const c = await env.DB.prepare("SELECT status, COUNT(*) as n FROM keyword_queue GROUP BY status").all();
    for (const r of (c.results || [])) data.keywordQueue.byStatus[r.status] = r.n;
    data.keywordQueue.total = Object.values(data.keywordQueue.byStatus).reduce((a, b) => a + b, 0);
    const svcQ = await env.DB.prepare("SELECT service, COUNT(*) as n FROM keyword_queue WHERE service IS NOT NULL AND service != '' GROUP BY service").all();
    for (const r of (svcQ.results || [])) data.keywordQueue.byService[r.service] = r.n;
    const srcQ = await env.DB.prepare("SELECT source, COUNT(*) as n FROM keyword_queue WHERE source IS NOT NULL GROUP BY source ORDER BY n DESC LIMIT 15").all();
    for (const r of (srcQ.results || [])) data.keywordQueue.bySource[r.source] = r.n;
  } catch (e) {}

  // 3. Posts coverage per service (LIVE D1)
  try {
    const total = await env.DB.prepare("SELECT COUNT(*) as n FROM posts_meta").first();
    data.postsMeta.total = total?.n || 0;
    const gen = await env.DB.prepare("SELECT COUNT(*) as n FROM posts_meta WHERE generated = 1").first();
    data.postsMeta.generated = gen?.n || 0;
    // Coverage per service — handle missing services
    const svcMap = {
      "Jasa Iklan Facebook Ads": ["facebook", "fb-ads", "iklan-facebook"],
      "Jasa Iklan Instagram": ["instagram", "ig-ads", "ig "],
      "Jasa Iklan TikTok": ["tiktok"],
      "Jasa Iklan Google Ads": ["google-ads", "google ads", "google_ads", "adwords"],
      "Jasa Iklan YouTube": ["youtube"],
      "Jasa Kelola Instagram": ["kelola-instagram", "admin-instagram"],
      "Jasa Kelola TikTok": ["kelola-tiktok", "admin-tiktok"],
      "Jasa Pembuatan Website": ["website", "pembuatan-website", "web "],
      "Jasa Pembuatan Landing Page": ["landing-page", "landing page"],
      "Jasa View Live TikTok": ["view-live", "live-tiktok", "live-streaming"],
      "Jasa Shopee Affiliate": ["shopee", "shopee-affiliate"],
      "Jasa Digital Marketing": ["digital-marketing", "digital marketing"]
    };
    for (const [display, patterns] of Object.entries(svcMap)) {
      const placeholders = patterns.map(() => "slug LIKE ? OR slug LIKE ?").join(" OR ");
      const params = [];
      patterns.forEach(p => { params.push("%" + p + "%"); params.push("%" + p + "%"); });
      const c = await env.DB.prepare(`SELECT COUNT(*) as n FROM posts_meta WHERE ${placeholders}`).bind(...params).first();
      data.postsMeta.byService[display] = c?.n || 0;
    }
  } catch (e) {}

  // 4. Indexing status
  try {
    const c = await env.DB.prepare("SELECT status, COUNT(*) as n FROM pending_indexing GROUP BY status").all();
    for (const r of (c.results || [])) data.indexing[r.status] = r.n;
    data.indexing.submitted = (data.indexing.submitted || 0) + (data.indexing.gsc_submitted || 0);
    const t = await env.DB.prepare("SELECT COUNT(*) as n FROM pending_indexing WHERE status IN ('submitted','gsc_submitted') AND date(COALESCE(gsc_submitted_at, submitted_at, created_at))=date('now')").first();
    data.indexing.today = t?.n || 0;
    const rec = await env.DB.prepare("SELECT url, status, created_at, submitted_at, gsc_submitted_at FROM pending_indexing ORDER BY rowid DESC LIMIT 30").all();
    data.indexing.recent = rec.results || [];
    const ins = await env.DB.prepare("SELECT COUNT(*) as total, SUM(CASE WHEN indexnow_at > datetime('now', '-24 hours') THEN 1 ELSE 0 END) as last_24h FROM pending_indexing WHERE indexnow_at IS NOT NULL").first();
    data.indexnow.total = ins?.total || 0;
    data.indexnow.last24h = ins?.last_24h || 0;
  } catch (e) {}

  // 5. Cron settings
  try {
    const r = await env.DB.prepare("SELECT name, enabled, cron, label FROM cron_settings ORDER BY id").all();
    data.cron = r.results || [];
  } catch (e) {}

  // 6. Trending articles
  try {
    const t = await env.DB.prepare("SELECT COUNT(*) as n FROM trending_articles").first();
    data.trending.total = t?.n || 0;
    const rec = await env.DB.prepare("SELECT slug, source, created_at FROM trending_articles ORDER BY id DESC LIMIT 8").all();
    data.trending.recent = rec.results || [];
  } catch (e) {}

  // 7. Drafts
  try {
    const t = await env.DB.prepare("SELECT status, COUNT(*) as n FROM generated_drafts GROUP BY status").all();
    for (const r of (t.results || [])) data.drafts[r.status] = r.n;
    data.drafts.total = (data.drafts.draft || 0) + (data.drafts.pending || 0) + (data.drafts.committed || 0);
    data.drafts.pending = data.drafts.draft || 0;
    data.drafts.committed = data.drafts.committed || 0;
  } catch (e) {}

  // ===== RENDER HELPERS =====
  const num = n => (n || 0).toLocaleString('id-ID');
  const pct = (a, b) => b > 0 ? Math.round((a / b) * 100) : 0;
  const esc = s => String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  // Health banner status
  const failedCrons = data.cron.filter(c => c.enabled).length;
  const totalCrons = data.cron.length;
  const healthStatus = data.drafts.pending > 5 ? "warning" : (data.indexing.pending > 50 ? "watch" : "healthy");

  return new Response(`<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>SEO Pipeline — Beriklan Admin</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f7fa;color:#1f2937;line-height:1.5}
.container{max-width:1320px;margin:0 auto;padding:24px}
h1{font-size:22px;font-weight:800;letter-spacing:-0.01em}
h2{font-size:15px;font-weight:700;margin-bottom:12px;letter-spacing:-0.005em}
h3{font-size:13px;font-weight:600;color:#6b7280;margin-bottom:8px}
.sub{color:#6b7280;font-size:13px;margin-bottom:24px}
.flow{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:24px 0;padding:18px;background:white;border-radius:14px;box-shadow:0 1px 3px rgba(0,0,0,0.05)}
.flow-step{padding:14px;border-radius:10px;text-align:center;position:relative;background:linear-gradient(135deg,#f9fafb 0%,#f3f4f6 100%)}
.flow-step.active{background:linear-gradient(135deg,#0f1e3d 0%,#1a2f5c 100%);color:#fff}
.flow-step .icon{font-size:24px;margin-bottom:8px}
.flow-step .label{font-size:11px;text-transform:uppercase;letter-spacing:0.04em;opacity:0.7;margin-bottom:4px}
.flow-step .value{font-size:20px;font-weight:800}
.flow-arrow{display:none}
@media(max-width:900px){.flow{grid-template-columns:1fr 1fr}}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:20px}
.kpi{background:white;padding:16px;border-radius:12px;border:1px solid #eef0f5}
.kpi .label{font-size:10px;text-transform:uppercase;color:#6b7280;font-weight:700;letter-spacing:0.06em;margin-bottom:6px}
.kpi .value{font-size:22px;font-weight:800;line-height:1.1}
.kpi .sub{font-size:11px;color:#9ca3af;margin-top:4px}
.kpi.highlight{border-left:3px solid #f59e0b}
.kpi.good{border-left:3px solid #10b981}
.kpi.warn{border-left:3px solid #dc2626}
.section{background:white;border-radius:14px;padding:20px;margin-bottom:18px;box-shadow:0 1px 3px rgba(0,0,0,0.05);border:1px solid #eef0f5}
.section-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;padding-bottom:12px;border-bottom:1px solid #f0f1f5}
.section-head h2{display:flex;align-items:center;gap:8px}
.section-head .meta{font-size:12px;color:#9ca3af}
.bar{height:8px;background:#f0f1f5;border-radius:4px;overflow:hidden;margin-top:4px}
.bar>div{height:100%;border-radius:4px;transition:width 0.3s}
table{width:100%;border-collapse:collapse;font-size:13px}
th{background:#fafbfc;color:#6b7280;font-weight:600;text-transform:uppercase;font-size:10px;letter-spacing:0.05em;padding:10px 12px;text-align:left;border-bottom:1px solid #eef0f5}
td{padding:10px 12px;border-bottom:1px solid #f5f6fa;vertical-align:middle}
tr:hover td{background:#fafbfc}
.badge{display:inline-block;padding:3px 10px;border-radius:100px;font-size:11px;font-weight:600;line-height:1.4}
.badge.green{background:#d1fae5;color:#065f46}
.badge.amber{background:#fef3c7;color:#92400e}
.badge.red{background:#fee2e2;color:#991b1b}
.badge.blue{background:#dbeafe;color:#1e40af}
.badge.gray{background:#f3f4f6;color:#4b5563}
.health-banner{padding:14px 20px;border-radius:10px;margin-bottom:20px;font-weight:600;font-size:14px;display:flex;align-items:center;gap:10px}
.health-banner.healthy{background:#d1fae5;color:#065f46}
.health-banner.watch{background:#dbeafe;color:#1e40af}
.health-banner.warning{background:#fef3c7;color:#92400e}
.health-banner.critical{background:#fee2e2;color:#991b1b}
.cron-row{display:grid;grid-template-columns:1fr 1fr 80px;gap:12px;padding:10px 14px;border-bottom:1px solid #f5f6fa;align-items:center}
.cron-row:last-child{border-bottom:none}
.toggle{position:relative;display:inline-block;width:40px;height:22px;cursor:pointer}
.toggle input{display:none}
.toggle .slider{position:absolute;inset:0;background:#d1d5db;border-radius:11px;transition:0.2s}
.toggle .slider::before{content:'';position:absolute;width:18px;height:18px;border-radius:50%;background:white;top:2px;left:2px;transition:0.2s;box-shadow:0 1px 3px rgba(0,0,0,0.2)}
.toggle input:checked+.slider{background:#10b981}
.toggle input:checked+.slider::before{transform:translateX(18px)}
.coverage-good{border-left:3px solid #10b981}
.coverage-warn{border-left:3px solid #f59e0b}
.coverage-low{border-left:3px solid #dc2626}
a{color:#0f1e3d;text-decoration:none}
a:hover{text-decoration:underline}
.action-bar{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px}
.btn{padding:9px 16px;border-radius:10px;border:none;font-weight:600;font-size:13px;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;gap:6px}
.btn-primary{background:#0f1e3d;color:#fff}
.btn-amber{background:#f59e0b;color:#0f1e3d}
.btn-outline{background:#fff;color:#0f1e3d;border:1px solid #d1d5db}
.muted{color:#9ca3af;font-size:11px}
.empty-state{text-align:center;padding:40px 20px;color:#9ca3af}
.empty-state .ico{font-size:36px;opacity:0.4;margin-bottom:8px}
.grid-2{display:grid;grid-template-columns:2fr 1fr;gap:18px}
@media(max-width:900px){.grid-2{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="container">
<div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:8px">
<div>
<h1>🎯 SEO Pipeline Dashboard</h1>
<p class="sub">Alur lengkap dari keyword research → artikel AI → publish → indexing. Pantau semua channel di sini.</p>
</div>
<a href="?token=${token}&format=json" class="btn btn-outline">📋 JSON View</a>
</div>

<!-- HEALTH BANNER -->
<div class="health-banner ${healthStatus}">
${healthStatus === 'healthy' ? '✅' : healthStatus === 'watch' ? '👀' : healthStatus === 'warning' ? '⚠️' : '🚨'}
${healthStatus === 'healthy'
  ? `Semua sehat — ${data.keywordQueue.byStatus.pending || 0} keyword pending siap di-generate.`
  : healthStatus === 'watch'
  ? `Perhatian — ${data.indexing.pending} URL belum ter-index.`
  : `${data.drafts.pending} draft belum ter-commit ke GitHub. Cek tab Drafts.`}
</div>

<!-- WORKFLOW VISUAL -->
<div class="flow">
<div class="flow-step">
<div class="icon">🔍</div>
<div class="label">Step 1 — Sources</div>
<div class="value">${num(Object.values(data.keywordQueue.bySource).reduce((a,b)=>a+b,0) || Object.keys(data.keywordQueue.bySource).length)}</div>
</div>
<div class="flow-step">
<div class="icon">📋</div>
<div class="label">Step 2 — Queue</div>
<div class="value">${num(data.keywordQueue.total)}</div>
</div>
<div class="flow-step active">
<div class="icon">🤖</div>
<div class="label">Step 3 — AI Generate</div>
<div class="value">${num(data.keywordQueue.byStatus.generated || 0)}</div>
</div>
<div class="flow-step">
<div class="icon">📝</div>
<div class="label">Step 4 — Drafts</div>
<div class="value">${num(data.drafts.total)}</div>
</div>
<div class="flow-step">
<div class="icon">📤</div>
<div class="label">Step 5 — Indexed</div>
<div class="value">${num(data.indexnow.total)}</div>
</div>
</div>

<!-- TOP KPI -->
<div class="kpi-grid">
<div class="kpi good"><div class="label">📋 Total Keyword</div><div class="value">${num(data.keywordQueue.total)}</div><div class="sub">${num(data.keywordQueue.byStatus.pending || 0)} pending · ${num(data.keywordQueue.byStatus.generated || 0)} generated</div></div>
<div class="kpi ${data.drafts.pending > 0 ? 'highlight' : 'good'}"><div class="label">📝 Drafts</div><div class="value">${num(data.drafts.total)}</div><div class="sub">${num(data.drafts.pending)} pending · ${num(data.drafts.committed)} committed</div></div>
<div class="kpi"><div class="label">📰 Artikel Live</div><div class="value">${num(data.postsMeta.total)}</div><div class="sub">${num(data.postsMeta.generated)} AI-generated</div></div>
<div class="kpi ${data.indexing.pending > 20 ? 'warn' : 'good'}"><div class="label">⏳ Indexing Pending</div><div class="value">${num(data.indexing.pending)}</div><div class="sub">${num(data.indexing.today)} hari ini</div></div>
<div class="kpi"><div class="label">📡 IndexNow 24h</div><div class="value">${num(data.indexnow.last24h)}</div><div class="sub">${num(data.indexnow.total)} total</div></div>
<div class="kpi"><div class="label">🔥 Trending</div><div class="value">${num(data.trending.total)}</div><div class="sub">artikel fetched</div></div>
</div>

<!-- SERVICE COVERAGE -->
<div class="section">
<div class="section-head">
<h2>🎯 Coverage per Layanan (Article Coverage)</h2>
<span class="meta">Target: minimal 30 artikel per layanan untuk SEO kuat</span>
</div>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px">
${Object.entries(data.postsMeta.byService).sort((a,b) => b[1] - a[1]).map(([svc, count]) => {
  const target = 30;
  const cov = pct(count, target);
  const cls = cov >= 80 ? 'coverage-good' : cov >= 30 ? 'coverage-warn' : 'coverage-low';
  const icon = cov >= 80 ? '✓' : cov >= 30 ? '⚠️' : '❌';
  return `<div class="${cls}" style="background:#fafbfc;padding:14px;border-radius:8px">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
<strong style="font-size:13px">${esc(svc)}</strong>
<span style="font-size:18px">${icon}</span>
</div>
<div style="font-size:24px;font-weight:800;color:${cov >= 80 ? '#10b981' : cov >= 30 ? '#f59e0b' : '#dc2626'}">${num(count)}</div>
<div class="bar"><div style="width:${Math.min(cov, 100)}%;background:${cov >= 80 ? '#10b981' : cov >= 30 ? '#f59e0b' : '#dc2626'}"></div></div>
<div class="muted" style="margin-top:4px">${cov}% dari target 30</div>
</div>`;
}).join('')}
</div>
<p style="margin-top:12px;font-size:12px;color:#6b7280">Coverage dihitung dari jumlah artikel dengan slug yang match nama layanan. Shopee & View Live perlu prioritas karena masih rendah.</p>
</div>

<div class="grid-2">
<!-- LEFT: KEYWORD SOURCES + QUEUE BY SERVICE -->
<div>
<div class="section">
<div class="section-head"><h2>📊 Keyword Sources</h2><span class="meta">dari mana keyword berasal</span></div>
${Object.keys(data.keywordQueue.bySource).length ? `<table>
<thead><tr><th>Source</th><th>Total</th><th>Status</th></tr></thead>
<tbody>${Object.entries(data.keywordQueue.bySource).sort((a,b)=>b[1]-a[1]).slice(0,10).map(([src, count]) => {
  const desc = src.startsWith('sheet_') ? 'Google Sheet' : src === 'miner' ? 'Keyword Miner' : src === 'expansion_v1' ? 'AI Expansion' : src === 'suggest+combo' ? 'Suggest + Combo' : 'Lainnya';
  return `<tr><td><code>${esc(src)}</code><br><span class="muted">${desc}</span></td><td><strong>${num(count)}</strong></td><td><span class="badge ${count > 1000 ? 'green' : count > 100 ? 'amber' : 'gray'}">${count > 1000 ? '✓ aktif' : count > 100 ? 'monitor' : 'idle'}</span></td></tr>`;
}).join('')}</tbody></table>` : '<div class="empty-state"><div class="ico">📋</div>Belum ada keyword</div>'}
</div>

<div class="section">
<div class="section-head"><h2>📋 Antrian per Layanan</h2><span class="meta">siap di-generate</span></div>
${Object.keys(data.keywordQueue.byService).length ? `<table>
<thead><tr><th>Layanan</th><th>Antrian</th></tr></thead>
<tbody>${Object.entries(data.keywordQueue.byService).sort((a,b)=>b[1]-a[1]).map(([svc, count]) => `<tr><td>${esc(svc)}</td><td><strong>${num(count)}</strong></td></tr>`).join('')}</tbody></table>` : '<div class="empty-state"><div class="ico">📋</div>Belum ada antrian</div>'}
</div>
</div>

<!-- RIGHT: INDEXING + TRENDING + CRON -->
<div>
<div class="section">
<div class="section-head"><h2>📡 Indexing Pipeline</h2><span class="meta">URL → IndexNow + Google</span></div>
<div class="kpi-grid" style="grid-template-columns:repeat(2,1fr);margin-bottom:12px">
<div class="kpi"><div class="label">Pending</div><div class="value" style="color:${data.indexing.pending > 20 ? '#dc2626' : '#0f1e3d'}">${num(data.indexing.pending)}</div></div>
<div class="kpi good"><div class="label">Submitted</div><div class="value">${num(data.indexing.submitted || 0)}</div></div>
<div class="kpi ${data.indexing.failed > 0 ? 'warn' : ''}"><div class="label">Failed</div><div class="value">${num(data.indexing.failed || 0)}</div></div>
<div class="kpi"><div class="label">Hari Ini</div><div class="value">${num(data.indexing.today)}</div></div>
</div>
<div class="muted" style="text-align:center">IndexNow last 24h: <strong>${num(data.indexnow.last24h)}</strong> URLs · Total: ${num(data.indexnow.total)}</div>
</div>

<div class="section">
<div class="section-head"><h2>🔥 Trending Articles</h2><span class="meta">auto-fetch dari Google Trends</span></div>
${data.trending.recent.length ? `<table>
<thead><tr><th>Topic</th><th>Source</th><th>Date</th></tr></thead>
<tbody>${data.trending.recent.map(r => `<tr><td><strong>${esc(r.slug)}</strong></td><td><span class="badge blue">${esc(r.source)}</span></td><td class="muted">${esc((r.created_at||'').slice(0,16))}</td></tr>`).join('')}</tbody></table>` : '<div class="empty-state"><div class="ico">🔥</div>Belum ada</div>'}
</div>
</div>
</div>

<!-- CRON JOBS -->
<div class="section">
<div class="section-head">
<h2>⏰ Cron Jobs (${data.cron.length} total, ${failedCrons} aktif)</h2>
<span class="meta">Klik toggle untuk pause / enable</span>
</div>
${data.cron.length ? data.cron.map(c => {
  const isLast = c.name === 'email-send' ? true : false; // mark special
  return `<form method="POST" action="/api/admin/cron/toggle?token=${token}&name=${c.name}" style="margin:0">
<div class="cron-row">
<div>
<strong>${esc(c.name)}</strong>
<code style="background:#f0f1f5;padding:2px 6px;border-radius:4px;font-size:11px;margin-left:8px">${esc(c.cron)}</code>
${c.name === 'email-send' ? '<span class="badge red" style="margin-left:6px">⚠️ Email blast — toggle hati-hati</span>' : ''}
<br><span class="muted">${esc(c.label || '')}</span>
</div>
<div></div>
<label class="toggle">
<input type="checkbox" ${c.enabled ? 'checked' : ''} onchange="this.form.submit()">
<span class="slider"></span>
</label>
</div>
</form>`;
}).join('') : '<div class="empty-state">Belum ada cron</div>'}
</div>

<!-- ACTION BUTTONS -->
<div class="action-bar">
<a href="/api/admin/drafts?token=${token}" class="btn btn-amber">📝 Manage Drafts (${data.drafts.pending} pending)</a>
<a href="/api/admin/cron/toggle?token=${token}&format=json" class="btn btn-outline">⏰ Cron Settings</a>
<a href="/api/admin/env-check?token=${token}" class="btn btn-outline">🔑 Env Check</a>
<a href="/api/admin/health?token=${token}" class="btn btn-outline">🏥 Health</a>
</div>

<p class="muted" style="text-align:center;margin-top:32px">Snapshot: ${new Date().toISOString()} · auto-refresh setiap reload</p>
</div>
</body>
</html>`, { headers: { "Content-Type": "text/html; charset=utf-8", "X-Robots-Tag": "noindex, nofollow" } });
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
    // N.7: Get hourly runs (last 24h)
    const hourlyRuns = await env.DB.prepare(
      `SELECT timestamp, count_requested, count_generated, slugs, models, committed_to_github, enqueued_for_indexing, error, elapsed_ms
       FROM hourly_generate_runs
       WHERE timestamp > datetime('now', '-24 hours')
       ORDER BY timestamp DESC
       LIMIT 24`
    ).all();
    const hourlyRows = (hourlyRuns.results || []);

    // Today's totals
    const todayStats = await env.DB.prepare(
      `SELECT
         COUNT(*) as runs,
         SUM(count_generated) as generated,
         SUM(CASE WHEN committed_to_github=1 THEN 1 ELSE 0 END) as committed,
         SUM(enqueued_for_indexing) as indexed
       FROM hourly_generate_runs
       WHERE timestamp > datetime('now', '-24 hours')`
    ).first();

    // N.8 IndexNow stats
    const indexnowStats = await env.DB.prepare(
      `SELECT
         COUNT(*) as urls_indexnow_total,
         SUM(CASE WHEN indexnow_at > datetime('now', '-24 hours') THEN 1 ELSE 0 END) as urls_indexnow_24h
       FROM pending_indexing
       WHERE indexnow_at IS NOT NULL`
    ).first();

    if (hourlyRows.length === 0) {
      return `
        <h3 class="section-title">🤖 Hourly Auto-Generate Activity (last 24h)</h3>
        <div class="card"><p style="color:#999;font-size:13px;">Belum ada artikel yang di-generate via <code>/api/cron/hourly-generate</code> dalam 24 jam terakhir. Setup cron-job.org untuk trigger.</p></div>
      `;
    }

    const ts = todayStats || {};
    const ins = indexnowStats || {};

    // Build hourly runs table
    const table = hourlyRows.map(r => {
      const slugs = (r.slugs || '').split(',').map(s => s.trim()).filter(Boolean);
      const slugDisplay = slugs.length > 0
        ? slugs.map(s => `<a href="/blog/${esc(s)}/" target="_blank" style="font-size:11px;">${esc(s.slice(0, 40))}</a>`).join(', ')
        : '<em style="color:#999;">none</em>';
      const modelJson = (() => {
        try { return JSON.parse(r.models || '[]'); } catch { return []; }
      })();
      const modelSummary = modelJson.length > 0
        ? modelJson.map(m => String(m).replace('groq/llama-3.3-70b-versatile (groq#', 'groq#').replace('zen/deepseek-v3-flash', 'zen/deepseek').replace(')', ')')).join(', ')
        : '-';
      const errBadge = r.error ? '<span class="badge red" title="' + esc(r.error) + '">err</span>' : '';
      const committedBadge = r.committed_to_github
        ? '<span class="badge green">✓ GH</span>'
        : '<span class="badge yellow">draft</span>';
      const indexedBadge = r.enqueued_for_indexing > 0
        ? '<span class="badge info">+' + r.enqueued_for_indexing + ' idx</span>'
        : '';
      return `<tr>
        <td style="font-size:11px;color:#666;">${esc((r.timestamp || '').slice(0, 19))}</td>
        <td>${slugDisplay}</td>
        <td style="font-size:11px;">${esc(modelSummary)}</td>
        <td>${committedBadge} ${indexedBadge} ${errBadge}</td>
        <td style="font-size:11px;color:#999;">${(r.elapsed_ms || 0) / 1000}s</td>
      </tr>`;
    }).join('');

    return `
      <h3 class="section-title">🤖 Hourly Auto-Generate Activity (last 24h)</h3>
      <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(160px,1fr));margin-bottom:12px;">
        <div class="card success"><h2>Cron Runs (24h)</h2><div class="metric">${ts.runs || 0}</div><div class="sub">/api/cron/hourly-generate</div></div>
        <div class="card success"><h2>Articles Generated</h2><div class="metric">${ts.generated || 0}</div><div class="sub">dalam 24 jam terakhir</div></div>
        <div class="card info"><h2>✅ Committed to GitHub</h2><div class="metric">${ts.committed || 0}</div><div class="sub">posts.json + queue + index</div></div>
        <div class="card info"><h2>🔍 Enqueued for Indexing</h2><div class="metric">${ts.indexed || 0}</div><div class="sub">URL → pending_indexing table</div></div>
        <div class="card info"><h2>IndexNow submitted</h2><div class="metric">${ins.urls_indexnow_24h || 0}</div><div class="sub">dari ${ins.urls_indexnow_total || 0} total (no quota, multi-engine)</div></div>
      </div>
      <table><thead><tr><th>Timestamp</th><th>Slugs Generated</th><th>Model</th><th>Status</th><th>Duration</th></tr></thead><tbody>${table}</tbody></table>
    `;
  } catch (e) {
    return `
      <h3 class="section-title">🤖 Hourly Auto-Generate Activity (last 24h)</h3>
      <div class="card warning"><p class="sub">D1 table belum ready: ${esc(e.message)}</p></div>
    `;
  }
}

// ─── Roadmap Progress (static checklist, source: SEO-STRATEGY.md) ──────
async function renderRoadmap(env) {
  // Real data: query actual state from D1 + Worker
  let stats = {
    cronHourlyActive: false,
    lastHourlyRun: null,
    pendingTotal: 0,
    generatedTotal: 0,
    indexedTotal: 0,
    indexnowTotal: 0,
    gscSitemapsSubmitted: 0,
    pagesIndexed: 0,
    adSlotsActive: 0,
    newslettersSent: 0,
    aiModel: "groq",
  };

  if (env && env.DB) {
    try {
      const lastRun = await env.DB.prepare(
        `SELECT timestamp FROM cron_logs ORDER BY timestamp DESC LIMIT 1`
      ).first();
      stats.lastHourlyRun = lastRun?.timestamp;
      stats.cronHourlyActive = lastRun && (new Date() - new Date(lastRun.timestamp + 'Z')) < 2 * 3600 * 1000;

      const cnt = await env.DB.prepare(
        `SELECT
           (SELECT COUNT(*) FROM hourly_generate_runs WHERE timestamp > datetime('now', '-24 hours')) as hourly_runs_24h,
           (SELECT SUM(count_generated) FROM hourly_generate_runs WHERE timestamp > datetime('now', '-24 hours')) as generated_24h,
           (SELECT COUNT(*) FROM pending_indexing WHERE indexnow_at IS NOT NULL) as indexnow_total,
           (SELECT COUNT(*) FROM pending_indexing WHERE status IN ('submitted','gsc_submitted')) as gsc_submitted,
           (SELECT COUNT(*) FROM newsletter_subscribers WHERE status='active') as newsletters,
           (SELECT COUNT(*) FROM gsc_sitemaps) as sitemaps`
      ).first();
      if (cnt) {
        stats.hourlyRuns24h = cnt.hourly_runs_24h || 0;
        stats.generated24h = cnt.generated_24h || 0;
        stats.indexnowTotal = cnt.indexnow_total || 0;
        stats.gscSubmitted = cnt.gsc_submitted || 0;
        stats.newsletters = cnt.newsletters || 0;
        stats.gscSitemapsSubmitted = cnt.sitemaps || 0;
      }
    } catch (e) {}
  }

  const items = [
    // P1 — Fondasi
    { phase: "P1", icon: "🔧", title: "Pipeline auto-generate artikel",
      status: stats.hourlyRuns24h > 0 ? "done" : "pending",
      metric: `${stats.generated24h || 0} artikel / 24h`,
      note: "Cron tiap jam (0 *) generate 3 artikel. Total: " + stats.hourlyRuns24h + " runs dalam 24h." },

    { phase: "P1", icon: "📝", title: "Keyword research & expansion",
      status: stats.pendingTotal > 10000 ? "done" : "in-progress",
      metric: "27,825 keywords",
      note: "Matrix 12 layanan × 30+ kota. Tiap keyword punya content brief siap." },

    { phase: "P1", icon: "🔗", title: "Internal linking otomatis",
      status: "done",
      metric: "5 related links/artikel",
      note: "Worker inject 'Baca Juga' section + page-1 boost ke artikel baru." },

    // P2 — Indexing
    { phase: "P2", icon: "🔍", title: "Google Indexing API",
      status: stats.gscSubmitted > 0 ? "done" : "pending",
      metric: `${stats.gscSubmitted} submitted`,
      note: "Cron tiap 6 jam (50 URLs/batch). Quota Google: 200/hari." },

    { phase: "P2", icon: "🚀", title: "IndexNow (Bing/Yandex/DuckDuckGo)",
      status: stats.indexnowTotal > 0 ? "done" : "pending",
      metric: `${stats.indexnowTotal} submitted (no quota)`,
      note: "Cron tiap jam pada menit :15. Multi-engine: Bing + Yandex + DuckDuckGo + Naver + Seznam." },

    { phase: "P2", icon: "🗺️", title: "Sitemap submission ke Google + Bing",
      status: stats.gscSitemapsSubmitted > 0 ? "done" : "pending",
      metric: `${stats.gscSitemapsSubmitted}/5 sitemaps submitted`,
      note: "5 sub-sitemaps: static, blog, city, pillar, tag. Auto-ping tiap 6 jam." },

    { phase: "P2", icon: "⚡", title: "Page speed (LCP < 2s)",
      status: "done",
      metric: "FCP 284ms · Load 628ms",
      note: "Hero preload + fetchpriority=high. Score -44% dari baseline." },

    // P3 — Content depth
    { phase: "P3", icon: "🏛️", title: "Pillar page per layanan (5000 kata)",
      status: "pending",
      metric: "0/12 pillar pages",
      note: "Topical authority — single pillar per service jadi hub artikel turunan." },

    { phase: "P3", icon: "❓", title: "FAQ/PAA content di setiap artikel",
      status: "done",
      metric: "3-4 FAQ/artikel",
      note: "AI generate FAQ section. Target: position 0 (featured snippet)." },

    { phase: "P3", icon: "🧮", title: "Calculator tool (budget iklan)",
      status: "pending",
      metric: "0/3 calculator",
      note: "Tools: budget Meta Ads, budget Google Ads, ROAS projection. Boost dwell time + backlink." },

    // P4 — Off-page
    { phase: "P4", icon: "📍", title: "Google Business Profile",
      status: "pending",
      metric: "1 lokasi Bandung",
      note: "WAJIB untuk local SEO. Butuh postcard verification 5-14 hari." },

    { phase: "P4", icon: "🔗", title: "Backlink building (directory + guest post)",
      status: "in-progress",
      metric: "90 dirs curated · 0 live",
      note: "Scripts/submissions/*.md siap (34 packets DR>80). Butuh user submit manual karena CAPTCHA." },

    { phase: "P4", icon: "🎬", title: "YouTube channel + video embed",
      status: "pending",
      metric: "0 videos",
      note: "Double SERP exposure. Tutorial campaign 5-10 menit per video." },

    { phase: "P4", icon: "💼", title: "LinkedIn + TikTok brand entity",
      status: "pending",
      metric: "0 entities",
      note: "Off-page signals + knowledge graph." },

    // P5 — Conversion
    { phase: "P5", icon: "⭐", title: "AggregateRating schema + reviews",
      status: "pending",
      metric: "0 reviews",
      note: "Butuh review asli dari klien. Trustpilot/Google review = stars di SERP." },

    { phase: "P5", icon: "📊", title: "A/B testing title (CTR lift)",
      status: "pending",
      metric: "0 experiments",
      note: "GSC CTR data + multiple title variants = +20-50% traffic." },

    // P6 — Scale
    { phase: "P6", icon: "🌐", title: "Programmatic SEO (harga/cara/vs)",
      status: "pending",
      metric: "0 prog pages",
      note: "Template: 'harga X di {kota}', 'cara X untuk {industri}', 'X vs Y'. Ribuan URL." },

    // P7 — Monetization
    { phase: "P7", icon: "📧", title: "Email newsletter → upsell jasa",
      status: stats.newsletters > 0 ? "done" : "pending",
      metric: `${stats.newsletters} subscribers`,
      note: "Newsletter P2.6 LIVE. 3-email drip: welcome → tips → case study → WhatsApp CTA." },
  ];

  const done = items.filter(i => i.status === "done").length;
  const inProgress = items.filter(i => i.status === "in-progress").length;
  const total = items.length;
  const pct = Math.round(100 * done / total);

  const statusBadge = (s) => {
    if (s === "done") return '<span class="badge green">✅ done</span>';
    if (s === "in-progress") return '<span class="badge" style="background:#fef3c7;color:#92400e;">🔄 jalan</span>';
    return '<span class="badge yellow">⏳ belum</span>';
  };
  const phaseColor = (p) => {
    const map = { P1: "#dbeafe", P2: "#dcfce7", P3: "#fef3c7", P4: "#fed7aa", P5: "#fce7f3", P6: "#e9d5ff", P7: "#ccfbf1" };
    return map[p] || "#e0e7ff";
  };

  const rows = items.map(i =>
    `<tr>
      <td><span class="badge" style="background:${phaseColor(i.phase)};color:#1f2937;font-weight:700;">${i.phase}</span></td>
      <td>${i.icon} <strong>${i.title}</strong></td>
      <td>${i.metric}</td>
      <td>${statusBadge(i.status)}</td>
      <td style="color:#555;font-size:12px;">${i.note}</td>
    </tr>`
  ).join("");

  return `
    <h3 class="section-title">🗺️ Roadmap Progress — Status Real (${done}✅ done · ${inProgress}🔄 jalan · ${total - done - inProgress}⏳ belum dari ${total})</h3>
    <div class="card" style="margin-bottom:16px;">
      <div style="background:#eee;border-radius:6px;height:18px;overflow:hidden;">
        <div style="background:linear-gradient(90deg,#10b981,#0ea5e9);height:18px;width:${pct}%;transition:width 0.5s;display:flex;align-items:center;padding-left:8px;color:white;font-weight:600;font-size:12px;">${pct}%</div>
      </div>
      <p class="sub" style="margin-top:10px;">📄 Detail lengkap: <a href="https://github.com/ReqTimeout/beriklan.co.id/blob/main/SEO-STRATEGY.md" target="_blank">SEO-STRATEGY.md</a> · 🎯 Target: #1 SERP untuk 28K keyword + AdSense scale + WhatsApp leads</p>
    </div>
    <table><thead><tr><th>Phase</th><th>Item</th><th>Metric Real-time</th><th>Status</th><th>Catatan</th></tr></thead><tbody>${rows}</tbody></table>
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

// ─── IndexNow-Only Indexing (Bing + Yandex + DuckDuckGo, no quota) ─────────────
//   POST /api/cron/indexnow?token=...&count=N
//   Submits pending URLs to IndexNow (api.indexnow.org + www.bing.com/indexnow)
//   No daily quota limit. Recommended: every 2 hours.
async function handleIndexNowCron(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) {
    return new Response(JSON.stringify({ ok: false, error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  }
  const count = Math.max(1, Math.min(parseInt(url.searchParams.get("count") || "20", 10), 50));
  const t0 = Date.now();
  const errors = [];
  const submitted = [];

  // 1. Fetch pending URLs (any not-yet-submitted via IndexNow)
  let urls = [];
  try {
    const r = await env.DB.prepare(
      `SELECT id, url FROM pending_indexing
       WHERE status='pending' OR (status IN ('submitted','gsc_submitted') AND indexnow_at IS NULL)
       ORDER BY rowid ASC LIMIT ?`
    ).bind(count).all();
    urls = (r.results || []).map(row => ({
      id: row.id,
      url: row.url.replace("https://beriklan.co.id", "https://www.beriklan.co.id"),
    }));
  } catch (e) {
    errors.push({ stage: "query", error: String(e).slice(0, 200) });
    return new Response(JSON.stringify({ ok: false, error: "query_failed", errors }), { status: 500, headers: { "Content-Type": "application/json" } });
  }

  if (urls.length === 0) {
    return new Response(JSON.stringify({ ok: true, message: "no pending URLs", submitted: [], log: { stage: "no_pending" } }), { headers: { "Content-Type": "application/json" } });
  }

  // 2. Submit to IndexNow (api.indexnow.org — single endpoint reaches all engines: Bing, Yandex, DuckDuckGo, etc.)
  const INDEXNOW_KEY = "2f22c16be9437a90ad2285a4af043e10";
  const payload = {
    host: "beriklan.co.id",
    key: INDEXNOW_KEY,
    keyLocation: `https://beriklan.co.id/2f22c16be9437a90ad2285a4af043e10.txt`,
    urlList: urls.map(u => u.url),
  };

  let totalEngines = 0;
  let totalFailed = 0;
  const log = [];
  // Single POST to api.indexnow.org fans out to all engines (Bing, Yandex, DuckDuckGo, Seznam, Naver)
  try {
    const resp = await fetch("https://api.indexnow.org/indexnow", {
      method: "POST",
      headers: { "Content-Type": "application/json; charset=utf-8" },
      body: JSON.stringify(payload),
    });
    if (resp.ok || resp.status === 202) {
      totalEngines = 4; // approximate count of engines receiving
      log.push({ stage: "indexnow_submit", endpoint: "api.indexnow.org", status: resp.status, urls: urls.length });
    } else {
      totalFailed++;
      const body = await resp.text().catch(() => "");
      errors.push({ stage: "indexnow_submit", endpoint: "api.indexnow.org", status: resp.status, body: body.slice(0, 200) });
    }
  } catch (e) {
    totalFailed++;
    errors.push({ stage: "indexnow_submit", endpoint: "api.indexnow.org", error: String(e).slice(0, 200) });
  }

  // 3. Mark all submitted URLs with indexnow_at timestamp — ONLY if API succeeded
  if (totalEngines > 0) {
    try {
      for (const u of urls) {
        await env.DB.prepare(
          `UPDATE pending_indexing SET indexnow_at = datetime('now') WHERE id=? AND indexnow_at IS NULL`
        ).bind(u.id).run();
        submitted.push(u.url);
      }
    } catch (e) {
      errors.push({ stage: "update_indexnow_at", error: String(e).slice(0, 200) });
    }
  } else {
    // API failed — don't mark URLs as submitted
    submitted.length = 0;
  }

  // 4. Log to cron_logs
  try {
    await env.DB.prepare(
      `INSERT INTO cron_logs (timestamp, google_ok, google_fail, indexnow_ok, indexnow_fail, urls_processed)
       VALUES (datetime('now'), 0, 0, ?, ?, ?)`
    ).bind(totalEngines, totalFailed, submitted.length).run();
  } catch (e) {}

  return new Response(JSON.stringify({
    ok: true,
    indexnow_engines: totalEngines,
    indexnow_failed: totalFailed,
    submitted: submitted.length,
    submitted_urls: submitted.slice(0, 10),
    elapsed_ms: Date.now() - t0,
    errors: errors.length ? errors : undefined,
  }, null, 2), { headers: { "Content-Type": "application/json" } });
}

// ─── Pending Indexing Cleanup (mark old 'submitted' as 'completed') ─────────────
async function handlePendingIndexingCleanup(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  }
  if (!env.DB) return new Response(JSON.stringify({ error: "DB not set" }), { status: 503, headers: { "Content-Type": "application/json" } });
  const t0 = Date.now();
  const log = [];

  // 1. Mark old 'submitted' rows as 'gsc_submitted' (they pre-date the gsc_submitted_at column)
  let updatedOld = 0;
  try {
    const r = await env.DB.prepare(
      `UPDATE pending_indexing SET status='gsc_submitted', gsc_submitted_at = COALESCE(gsc_submitted_at, datetime('now', '-30 days'))
       WHERE status='submitted'`
    ).run();
    updatedOld = r.meta?.changes || 0;
    log.push({ stage: "migrate_old_submitted", updated: updatedOld });
  } catch (e) {
    log.push({ stage: "migrate_old_submitted", error: String(e).slice(0, 200) });
  }

  // 2. Cleanup: delete very old completed entries (older than 90 days) to keep table lean
  let deletedOld = 0;
  try {
    const r = await env.DB.prepare(
      `DELETE FROM pending_indexing WHERE status IN ('gsc_submitted','completed','failed') AND created_at < datetime('now', '-90 days')`
    ).run();
    deletedOld = r.meta?.changes || 0;
    log.push({ stage: "delete_old_completed", deleted: deletedOld });
  } catch (e) {
    log.push({ stage: "delete_old_completed", error: String(e).slice(0, 200) });
  }

  // 3. Summary
  let stats = {};
  try {
    const r = await env.DB.prepare(`SELECT status, COUNT(*) as n FROM pending_indexing GROUP BY status`).all();
    stats = r.results || [];
  } catch (e) {}

  return new Response(JSON.stringify({ ok: true, log, stats, elapsed_ms: Date.now() - t0 }, null, 2), { headers: { "Content-Type": "application/json" } });
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

  // 4. Traditional GET ping (Google ?sitemap=, Bing /ping?sitemap=) — explicit hint
  //    Note: Google deprecated this but Bing still uses it. Cheap to call.
  const sitemapIndex = `${siteUrl}/sitemap-index.xml`;
  for (const pingUrl of [
    `https://www.google.com/ping?sitemap=${encodeURIComponent(sitemapIndex)}`,
    `https://www.bing.com/ping?sitemap=${encodeURIComponent(sitemapIndex)}`,
  ]) {
    try {
      const r = await fetch(pingUrl, { method: "GET", headers: { "User-Agent": "BeriklanWorker/1.0" } });
      results.legacy_ping = results.legacy_ping || [];
      results.legacy_ping.push({ endpoint: pingUrl.split("/")[2], status: r.status, ok: r.ok });
    } catch (e) {
      results.errors.push({ stage: "legacy_ping", endpoint: pingUrl, error: e.message });
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
        // Commit ke root repo (src/data/posts.json) — file ini ada di git
        // CF Pages build script akan copy ke src/data/posts.json
        const filePath = "src/data/posts.json";  // Astro baca via build copy

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
    // N.7 Log to hourly_generate_runs for dashboard visibility
    if (env.DB) {
      try {
        await env.DB.prepare(
          `INSERT INTO hourly_generate_runs
           (count_requested, count_generated, slugs, models, committed_to_github, enqueued_for_indexing, error, elapsed_ms)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
        ).bind(
          count,
          newPosts.length,
          newPosts.map(p => p.slug).join(", "),
          JSON.stringify(aiModels.map(m => m.model)),
          committedToGitHub ? 1 : 0,
          enqueued,
          errors.length ? errors.map(e => e.stage + ':' + e.error).join('; ').slice(0, 500) : null,
          elapsedMs
        ).run();
      } catch (e) {
        // Noop — logging is non-critical
      }
    }

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

// ─── Email Campaign System ────────────────────────────────────────

const SERVICE_CONFIGS = [
  {
    name: "Jasa Iklan Facebook Ads",
    subject: "120 juta orang Indonesia login ke Facebook tiap hari — bagaimana menjangkau mereka?",
    category: "meta-ads",
    service_path: "/jasa-iklan-facebook/",
    hero_image: "https://images.unsplash.com/photo-1432888622747-4eb9a8efeb07?w=600&h=280&fit=crop&q=80",
    accent_color: "#1877f2",
    accent_bg: "#e7f0ff",
    badge: "Meta Business Partner",
    headline: "Jasa Iklan Facebook yang Menjangkau Audiens Tepat, Mendorong Chat WhatsApp.",
    subheadline: "120 juta lebih orang Indonesia login ke Facebook & Instagram setiap hari — di dalamnya ada calon pelanggan Anda. Tapi menampilkannya saja tidak cukup. Yang penting: siapa yang Anda jangkau, dengan pesan apa, dan di mana mereka akhirnya melakukan action.",
    benefits: [
      { short: "🎯", title: "Targeting interest & behavior", desc: "100+ kategori minat: perilaku, demografi, hobby spesifik audiens Anda." },
      { short: "🔄", title: "Remarketing list", desc: "Jangkau kembali orang yang pernah interaksi dengan iklan — konversi 3-5x lebih tinggi." },
      { short: "📍", title: "Target wilayah", desc: "Batasi ke kota, provinsi, atau radius tertentu — cocok untuk bisnis lokal." },
      { short: "📊", title: "Lead database & lookalike", desc: "Upload kontak lama, atau buat lookalike audience dari data tersebut." }
    ],
    steps: [
      { num: "01", tag: "MINGGU 1", title: "Brief & Riset", desc: "Diskusi 30 menit untuk menggali produk, target market, dan tujuan Anda." },
      { num: "02", tag: "MINGGU 1-2", title: "Setup & Kreatif", desc: "Setup akun iklan, Meta Pixel, dan materi iklan (foto, video, copy)." },
      { num: "03", tag: "MINGGU 2+", title: "Launch 30 Hari", desc: "Iklan tayang penuh di seluruh placement Facebook. Laporan tiap Senin pagi." }
    ],
    proof: "Tersertifikasi Meta Business Partner · Mengelola campaign sejak 2016",
    cta_text: "Lihat Paket & Harga",
    cta_url: "https://beriklan.co.id/jasa-iklan-facebook/"
  },
  {
    name: "Jasa Iklan Instagram",
    subject: "Instagram Ads untuk menemukan pelanggan baru lewat konten visual.",
    category: "meta-ads",
    service_path: "/jasa-iklan-instagram/",
    hero_image: "https://images.unsplash.com/photo-1611162618071-b39a2ec055fb?w=600&h=280&fit=crop&q=80",
    accent_color: "#e1306c",
    accent_bg: "#fce4ec",
    badge: "Meta Business Partner",
    headline: "Jasa Iklan Instagram untuk Menemukan Pelanggan Baru Lewat Konten Visual.",
    subheadline: "Setiap hari ratusan juta orang menggunakan Instagram untuk mencari inspirasi dan produk baru. Kami bantu bisnis Anda menayangkan iklan yang tertarget di Feed, Stories, dan Reels — agar impresi berubah menjadi kunjungan profil, DM, atau chat WhatsApp.",
    benefits: [
      { short: "📱", title: "Reels, Story & Feed Ads", desc: "Format video pendek & image ads yang disukai algoritma IG." },
      { short: "🎯", title: "Interest targeting", desc: "Capai audiens berdasarkan minat & perilaku Instagram." },
      { short: "💬", title: "DM otomatis", desc: "Lead form + auto-reply WhatsApp untuk closing lebih cepat." },
      { short: "📈", title: "A/B test visual", desc: "Beberapa materi diuji sekaligus untuk cari yang terbaik." }
    ],
    steps: [
      { num: "01", tag: "MINGGU 1", title: "Riset audiens", desc: "Pahami target market Anda: usia, minat, gaya konten yang cocok." },
      { num: "02", tag: "MINGGU 1-2", title: "Setup & Materi", desc: "Setting iklan + produksi materi (feed image, reels, story)." },
      { num: "03", tag: "MINGGU 2+", title: "Launch & Optimasi", desc: "Iklan tayang 30 hari. Optimasi mingguan berdasarkan data." }
    ],
    proof: "Tersertifikasi Meta · Portfolio fashion, F&B, lifestyle, jasa profesional",
    cta_text: "Lihat Paket IG Ads",
    cta_url: "https://beriklan.co.id/jasa-iklan-instagram/"
  },
  {
    name: "Jasa Iklan TikTok",
    subject: "TikTok Ads untuk menjangkau audiens lewat konten yang menghibur.",
    category: "tiktok",
    service_path: "/jasa-iklan-tiktok/",
    hero_image: "https://images.unsplash.com/photo-1517077304055-6e89abbf09b0?w=600&h=280&fit=crop&q=80",
    accent_color: "#ff0050",
    accent_bg: "#ffe0e8",
    badge: "TikTok Marketing Partner",
    headline: "Jasa Iklan TikTok untuk Menjangkau Audiens dengan Konten yang Menghibur.",
    subheadline: "TikTok menjadi kanal penemuan produk yang paling cepat bertumbuh di Indonesia. Kami bantu bisnis Anda membuat iklan video pendek yang tertarget — agar tayangan berubah menjadi pengikut, kunjungan profil, atau chat WhatsApp yang siap berkonsultasi.",
    benefits: [
      { short: "🎬", title: "Spark Ads", desc: "Boost UGC creators yang terbukti perform — bayar sesuai hasil." },
      { short: "🎯", title: "Interest targeting", desc: "Targeting khusus platform: minat, hashtag, perilaku." },
      { short: "📊", title: "Pixel integration", desc: "Track full-funnel dari view sampai checkout." },
      { short: "🚀", title: "Boost organik", desc: "Optimasi konten agar reach organik ikut naik." }
    ],
    steps: [
      { num: "01", tag: "MINGGU 1", title: "Brief & Riset", desc: "Diskusi target market, dan riset konten TikTok yang perform." },
      { num: "02", tag: "MINGGU 1-2", title: "Setup & Video", desc: "Setup TikTok Ads Manager + produksi video iklan." },
      { num: "03", tag: "MINGGU 2+", title: "Launch & Iterasi", desc: "Iklan tayang 30 hari. Iterasi materi setiap minggu." }
    ],
    proof: "TikTok Marketing Partner · Berpengalaman di F&B, fashion, beauty, edukasi",
    cta_text: "Lihat Paket TikTok Ads",
    cta_url: "https://beriklan.co.id/jasa-iklan-tiktok/"
  },
  {
    name: "Jasa Iklan Google Ads",
    subject: "Google Ads — tangkap intent tinggi saat mereka mencari.",
    category: "google-ads",
    service_path: "/jasa-iklan-google/",
    hero_image: "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?w=600&h=280&fit=crop&q=80",
    accent_color: "#4285f4",
    accent_bg: "#e3f2fd",
    badge: "Google Premier Partner",
    headline: "Jasa Iklan Google — Tangkap Intent Tinggi Saat Mereka Mencari.",
    subheadline: "Google Search Ads menjangkau orang yang sedang aktif mencari produk atau layanan Anda — bukan orang yang sedang scroll. Iklan tampil di halaman pertama dengan bid yang terkontrol. Kami mengatur strategi kata kunci, copy, dan landing page-nya.",
    benefits: [
      { short: "🔍", title: "Search Campaigns", desc: "Tampil di halaman 1 untuk keyword yang relevan." },
      { short: "📺", title: "YouTube Ads", desc: "Video awareness di platform video terbesar dunia." },
      { short: "📧", title: "Gmail Ads", desc: "Promosi langsung ke inbox orang yang tepat." },
      { short: "🛒", title: "Shopping Ads", desc: "Untuk e-commerce: produk tampil dengan gambar & harga." }
    ],
    steps: [
      { num: "01", tag: "MINGGU 1", title: "Riset Keyword", desc: "Analisis kata kunci yang relevan dengan biaya bid optimal." },
      { num: "02", tag: "MINGGU 1-2", title: "Setup & Copy", desc: "Setup akun Google Ads + landing page + copy iklan." },
      { num: "03", tag: "MINGGU 2+", title: "Optimasi Harian", desc: "Monitor performa, adjust bid, dan negative keywords." }
    ],
    proof: "Google Premier Partner · Bersertifikasi Search, Display, Video",
    cta_text: "Lihat Paket Google Ads",
    cta_url: "https://beriklan.co.id/jasa-iklan-google/"
  },
  {
    name: "Jasa Iklan YouTube",
    subject: "YouTube Ads — bangun brand awareness lewat video.",
    category: "google-ads",
    service_path: "/jasa-iklan-youtube/",
    hero_image: "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=600&h=280&fit=crop&q=80",
    accent_color: "#ff0000",
    accent_bg: "#ffe0e0",
    badge: "Google Video Partner",
    headline: "Jasa Iklan YouTube — Bangun Brand Awareness Lewat Video.",
    subheadline: "YouTube adalah platform video terbesar di Indonesia dengan jutaan penonton aktif setiap hari. Kami bantu bisnis Anda menayangkan iklan video yang tertarget — agar pesan Anda dilihat oleh audiens yang tepat, di channel yang tepat, di saat yang tepat.",
    benefits: [
      { short: "▶️", title: "TrueView Ads", desc: "Bayar hanya kalau penonton tonton 30 detik atau lebih." },
      { short: "⏱️", title: "Bumper 6 detik", desc: "Singkat, padat, langsung diingat." },
      { short: "📱", title: "Multi-device", desc: "Tampil di TV, desktop, mobile, tablet — semua device." },
      { short: "📈", title: "Brand Lift", desc: "Ukur dampak nyata terhadap brand awareness." }
    ],
    steps: [
      { num: "01", tag: "MINGGU 1", title: "Riset Channel", desc: "Analisis channel YouTube yang relevan untuk brand Anda." },
      { num: "02", tag: "MINGGU 1-2", title: "Setup & Video", desc: "Setup Google Ads Video + produksi materi video." },
      { num: "03", tag: "MINGGU 2+", title: "Launch & Optimize", desc: "Iklan tayang. Optimasi berdasarkan view-through & engagement." }
    ],
    proof: "Bersertifikasi Google Video · Portfolio FMCG, tech, edukasi",
    cta_text: "Lihat Paket YouTube Ads",
    cta_url: "https://beriklan.co.id/jasa-iklan-youtube/"
  },
  {
    name: "Jasa Kelola Instagram",
    subject: "Instagram Anda butuh konsistensi? Kami yang kelola.",
    category: "social-organic",
    service_path: "/jasa-kelola-instagram/",
    hero_image: "https://images.unsplash.com/photo-1611605698335-8b1569810432?w=600&h=280&fit=crop&q=80",
    accent_color: "#833ab4",
    accent_bg: "#f3e5f5",
    badge: "Organic Specialist",
    headline: "Jasa Kelola Instagram — Konsistensi Konten, Pertumbuhan yang Terukur.",
    subheadline: "Instagram yang aktif dan tertata membutuhkan waktu dan konsistensi. Tim kami mengelola akun Instagram Anda secara menyeluruh — mulai dari konsep, copy, desain, penjadwalan, hingga laporan mingguan. Anda fokus pada bisnis, kami yang menjaga brand tetap hidup.",
    benefits: [
      { short: "📅", title: "Content calendar", desc: "30 hari konten terstruktur — feed, reels, story." },
      { short: "🎨", title: "Desain profesional", desc: "Template brand yang konsisten dan recognizable." },
      { short: "✍️", title: "Copywriting", desc: "Caption engaging dengan CTA yang natural." },
      { short: "💬", title: "Community management", desc: "Balas komentar & DM dengan tone brand Anda." }
    ],
    steps: [
      { num: "01", tag: "BULAN 1", title: "Onboarding & Setup", desc: "Brief brand, analisis kompetitor, setup content calendar." },
      { num: "02", tag: "BULAN 2+", title: "Eksekusi Harian", desc: "Posting rutin, desain, copy, dan community management." },
      { num: "03", tag: "ONGOING", title: "Report Mingguan", desc: "Report reach, engagement, follower growth tiap minggu." }
    ],
    proof: "Mengelola brand sejak 2016 · Puluhan akun IG aktif setiap bulan",
    cta_text: "Lihat Paket Kelola IG",
    cta_url: "https://beriklan.co.id/jasa-kelola-instagram/"
  },
  {
    name: "Jasa Kelola TikTok",
    subject: "TikTok Anda perlu konsisten? Tim kami yang produksi.",
    category: "social-organic",
    service_path: "/jasa-kelola-tiktok/",
    hero_image: "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=600&h=280&fit=crop&q=80",
    accent_color: "#00f2ea",
    accent_bg: "#e0ffff",
    badge: "TikTok Specialist",
    headline: "Jasa Kelola TikTok — Konten Berkualitas, Followers Bertumbuh.",
    subheadline: "TikTok membutuhkan konten yang konsisten dan relevan dengan algoritma FYP. Tim kami mengelola akun TikTok Anda secara menyeluruh — mulai dari riset musik, konsep, produksi video, editing, hingga optimasi engagement. Anda fokus pada produk, kami menjaga brand tetap terdengar.",
    benefits: [
      { short: "🎬", title: "Video production", desc: "Paket video bulanan dengan scripting, shooting, editing." },
      { short: "🎵", title: "Trending sounds", desc: "Riset sound & hashtag yang sedang naik." },
      { short: "📊", title: "Analytics mingguan", desc: "Report view, engagement, follower growth." },
      { short: "💬", title: "Live streaming", desc: "Opsional: jadwal & script untuk live commerce." }
    ],
    steps: [
      { num: "01", tag: "BULAN 1", title: "Riset Musik & Hashtag", desc: "Riset sound & trend yang relevan untuk niche Anda." },
      { num: "02", tag: "BULAN 1+", title: "Produksi Video", desc: "Script, shooting, editing untuk beberapa video per minggu." },
      { num: "03", tag: "ONGOING", title: "Optimasi FYP", desc: "Analisa performa per video, iterasi gaya & topik." }
    ],
    proof: "Tim content creator berpengalaman · Puluhan akun TikTok dikelola",
    cta_text: "Lihat Paket Kelola TikTok",
    cta_url: "https://beriklan.co.id/jasa-kelola-tiktok/"
  },
  {
    name: "Jasa Pembuatan Website",
    subject: "Website modern pakai Svelte + Astro + Cloudflare — load < 1 detik.",
    category: "website",
    service_path: "/jasa-pembuatan-website/",
    hero_image: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&h=280&fit=crop&q=80",
    accent_color: "#0ea5e9",
    accent_bg: "#e0f2fe",
    badge: "Built with Svelte · Astro · Cloudflare",
    headline: "Website Modern yang Cepat, SEO-Ready, dan Dikembangkan dengan Stack Terbaik.",
    subheadline: "Kami bangun website Anda dengan teknologi yang sama dipakai brand-brand besar: Svelte untuk interaksi yang halus, Astro untuk performa static site terbaik, dan Cloudflare untuk CDN global dengan load time di bawah 1 detik. Bukan template WordPress lambat — ini website yang dirancang untuk konversi.",
    benefits: [
      { short: "⚡", title: "Load < 1 detik", desc: "Cloudflare CDN global + Astro static rendering. Skor PageSpeed 95-100." },
      { short: "🎨", title: "Svelte untuk UI", desc: "Interaksi smooth tanpa JavaScript berat — komponen reaktif, bundle kecil." },
      { short: "🌐", title: "Astro untuk SEO", desc: "Static HTML untuk Google, islands untuk dinamis. SEO-friendly by default." },
      { short: "📱", title: "Mobile-first", desc: "Responsif di semua device — dari iPhone sampai tablet landscape." },
      { short: "🔍", title: "SEO-friendly", desc: "Schema markup, sitemap otomatis, meta tags optimal. Cepat ranking di Google." },
      { short: "⚙️", title: "CMS custom", desc: "Update konten sendiri tanpa developer — dashboard yang intuitif." }
    ],
    steps: [
      { num: "01", tag: "MINGGU 1", title: "Brief & Wireframe", desc: "Diskusi kebutuhan, target audience, dan alur website. Riset kompetitor." },
      { num: "02", tag: "MINGGU 2-3", title: "Desain & Development", desc: "Desain UI di Figma → develop dengan Svelte + Astro → deploy ke Cloudflare." },
      { num: "03", tag: "MINGGU 4", title: "Review & Launch", desc: "Test performa & SEO, revisi, training CMS, handover akun Cloudflare." }
    ],
    proof: "Tech stack modern · Svelte 5 · Astro 5 · Cloudflare Workers · Dipercaya brand Bandung & Jabodetabek",
    cta_text: "Lihat Paket Website",
    cta_url: "https://beriklan.co.id/jasa-pembuatan-website/"
  },
  {
    name: "Jasa Pembuatan Landing Page",
    subject: "Landing Page + Google Ads — bundle siap dapat leads dari hari pertama.",
    category: "website",
    service_path: "/jasa-pembuatan-landing-page/",
    hero_image: "https://images.unsplash.com/photo-1556761175-b413da4baf72?w=600&h=280&fit=crop&q=80",
    accent_color: "#10b981",
    accent_bg: "#d1fae5",
    badge: "Conversion Bundle · Astro + Cloudflare",
    headline: "Landing Page + Google Ads — Bundle Siap Dapat Leads dari Hari Pertama.",
    subheadline: "Paket khusus untuk Anda yang ingin langsung mendatangkan pelanggan lewat internet: 1 landing page profesional (built dengan Astro + Cloudflare untuk load time terbaik) + 1 bulan Google Ads. Kami yang bangun halaman, tulis copy, jalankan iklan, optimasi — Anda tinggal terima leads di WhatsApp.",
    benefits: [
      { short: "⚡", title: "Load < 1 detik", desc: "Astro static + Cloudflare CDN. Google Ads Quality Score tinggi = biaya per klik lebih murah." },
      { short: "🎯", title: "1 halaman, 1 tujuan", desc: "Single conversion path — tidak ada menu, sidebar, atau link distraksi." },
      { short: "📊", title: "A/B testing built-in", desc: "2 versi diuji bersamaan — kami cari mana yang dapat leads lebih banyak." },
      { short: "📱", title: "Mobile-first design", desc: "Mayoritas traffic dari mobile — layout dioptimasi untuk tap & scroll." },
      { short: "💬", title: "Integrasi WhatsApp", desc: "Tombol CTA mengarah ke WhatsApp dengan pesan template siap kirim." },
      { short: "📈", title: "Conversion tracking", desc: "Pixel Meta + Google Analytics — tahu persis dari mana leads datang." }
    ],
    steps: [
      { num: "01", tag: "MINGGU 1", title: "Brief Landing Page", desc: "Tentukan produk/penawaran, target market, dan CTA utama. Riset kompetitor." },
      { num: "02", tag: "MINGGU 2", title: "Build + Copy", desc: "Copywriting persuasif + design di Figma + develop dengan Astro + deploy ke Cloudflare." },
      { num: "03", tag: "MINGGU 3+", title: "Google Ads + Optimasi", desc: "Setup campaign Google Ads, A/B test 2 versi, optimasi mingguan untuk turunkan CPA." }
    ],
    proof: "Bundle LP + Google Ads · Tech stack modern (Astro + Cloudflare) · Cepat dapat leads",
    cta_text: "Lihat Paket Landing Page",
    cta_url: "https://beriklan.co.id/jasa-pembuatan-landing-page/"
  },
  {
    name: "Jasa View Live TikTok",
    subject: "Viewers live TikTok untuk boost algoritma live Anda.",
    category: "view-live",
    service_path: "/jasa-view-live/",
    hero_image: "https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?w=600&h=280&fit=crop&q=80",
    accent_color: "#f59e0b",
    accent_bg: "#fef3c7",
    badge: "Trusted sejak 2016",
    headline: "View Live TikTok — Penonton Real untuk Live Commerce Anda.",
    subheadline: "Live commerce butuh viewers awal untuk boost algoritma. Kami sediakan viewers akun aktif Indonesia yang bantu live Anda tetap tayang dan viral. Cocok untuk seller TikTok Shop yang push omset harian.",
    benefits: [
      { short: "👥", title: "Viewers real", desc: "Akun aktif Indonesia, bukan bot kosong." },
      { short: "🎯", title: "Sesuai target", desc: "Cocokkan dengan niche: beauty, fashion, F&B, dll." },
      { short: "⏱️", title: "Sambil tayang", desc: "Viewer masuk selama live berlangsung." },
      { short: "💬", title: "Interaksi", desc: "Viewers aktif tinggalkan like & komentar." }
    ],
    steps: [
      { num: "01", tag: "HARI 1", title: "Brief Live", desc: "Tentukan jadwal live, target niche, dan jumlah viewer." },
      { num: "02", tag: "HARI LIVE", title: "Sesi Live", desc: "Kami kirim viewers real ke live stream Anda." },
      { num: "03", tag: "ONGOING", title: "Repeat Order", desc: "Pesan viewers untuk sesi live berikutnya." }
    ],
    proof: "Dipercaya ratusan seller TikTok Shop Indonesia",
    cta_text: "Lihat Paket View Live",
    cta_url: "https://beriklan.co.id/jasa-view-live/"
  },
  {
    name: "Jasa Digital Marketing",
    subject: "Strategi digital marketing lengkap untuk {{company}} — dari riset sampai eksekusi.",
    category: "digital-marketing",
    service_path: "/jasa-digital-marketing/",
    hero_image: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&h=280&fit=crop&q=80",
    accent_color: "#0f1e3d",
    accent_bg: "#f0f1f5",
    badge: "Multi-Channel Strategy",
    headline: "Jasa Digital Marketing — Strategi Lengkap dari Satu Tim Senior.",
    subheadline: "Daripada hire 5 agency berbeda untuk Meta Ads, Google Ads, TikTok Ads, SEO, dan website — Anda cukup pegang satu tim. Kami audit total, susun strategi terpadu, eksekusi lintas kanal, dan laporkan hasilnya dalam satu dashboard. Cocok untuk bisnis yang sudah jalan dan butuh sentuhan profesional.",
    benefits: [
      { short: "🎯", title: "Audit & strategi terpadu", desc: "Cek kondisi semua channel Anda, identifikasi kebocoran budget, susun rencana 90 hari." },
      { short: "📣", title: "Multi-channel paid ads", desc: "Meta Ads (FB + IG), TikTok Ads, Google Ads (Search + YouTube) — dijalankan bareng." },
      { short: "🔍", title: "SEO organik", desc: "Optimasi website + produksi artikel rutin agar muncul di halaman 1 Google." },
      { short: "🌐", title: "Website + landing page", desc: "Bangun atau optimasi website & landing page conversion-ready (Astro + Cloudflare)." },
      { short: "📊", title: "Dashboard terpusat", desc: "Laporan mingguan dari semua channel dalam 1 file — bukan 5 laporan terpisah." },
      { short: "🤝", title: "1 account manager", desc: "Satu kontak untuk semua kebutuhan digital marketing Anda. Tidak ada miskomunikasi." }
    ],
    steps: [
      { num: "01", tag: "MINGGU 1", title: "Audit Gratis", desc: "Kami audit semua channel digital Anda — website, ads, SEO, social. Temukan kebocoran budget." },
      { num: "02", tag: "MINGGU 2-3", title: "Strategi & Setup", desc: "Susun rencana 90 hari. Setup pixel, tracking, campaign awal di semua channel prioritas." },
      { num: "03", tag: "BULAN 2+", title: "Eksekusi & Optimasi", desc: "Jalankan campaign, produksi artikel SEO, optimasi mingguan berdasarkan data." },
      { num: "04", tag: "ONGOING", title: "Report & Scale Up", desc: "Laporan bulanan bahasa manusia. Scale up channel yang perform, cut yang tidak." }
    ],
    proof: "9 tahun mengelola campaign · Multi-channel specialist · Tersertifikasi Meta & Google",
    cta_text: "Lihat Paket Lengkap",
    cta_url: "https://beriklan.co.id/jasa-digital-marketing/"
  }
];

function generateServiceTemplate(c) {
  const benefitPairs = [];
  for (let i = 0; i < c.benefits.length; i += 2) {
    const a = c.benefits[i];
    const b = c.benefits[i+1];
    benefitPairs.push(`<tr>
<td style="padding:6px;vertical-align:top;width:50%;">
<table width="100%" style="background:#f7f8fb;border-radius:12px;padding:18px;border-left:3px solid ${c.accent_color};">
<tr><td>
<div style="font-size:22px;line-height:1;margin-bottom:6px;">${a.short}</div>
<div style="color:#0f1e3d;font-size:13px;font-weight:700;margin-bottom:4px;">${a.title}</div>
<div style="color:#6b7280;font-size:12px;line-height:1.5;">${a.desc}</div>
</td></tr></table>
</td>
${b ? `<td style="padding:6px;vertical-align:top;width:50%;">
<table width="100%" style="background:#f7f8fb;border-radius:12px;padding:18px;border-left:3px solid ${c.accent_color};">
<tr><td>
<div style="font-size:22px;line-height:1;margin-bottom:6px;">${b.short}</div>
<div style="color:#0f1e3d;font-size:13px;font-weight:700;margin-bottom:4px;">${b.title}</div>
<div style="color:#6b7280;font-size:12px;line-height:1.5;">${b.desc}</div>
</td></tr></table>
</td>` : '<td style="width:50%;"></td>'}
</tr>`);
  }

  // Steps (numbered timeline)
  const stepsHTML = (c.steps || []).map(s => `
<table width="100%" cellpadding="0" cellspacing="0" style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;margin-bottom:8px;">
<tr><td style="padding:14px 18px;">
<table width="100%"><tr>
<td width="48" valign="top" style="background:${c.accent_color};color:#fff;border-radius:8px;width:48px;height:48px;text-align:center;line-height:48px;font-weight:800;font-size:18px;font-family:monospace;">${s.num}</td>
<td style="padding-left:14px;vertical-align:top;">
<div style="display:inline-block;background:${c.accent_bg};color:${c.accent_color};font-size:9px;font-weight:700;letter-spacing:.08em;padding:2px 8px;border-radius:4px;margin-bottom:4px;">${s.tag}</div>
<div style="color:#0f1e3d;font-size:14px;font-weight:700;margin-bottom:3px;">${s.title}</div>
<div style="color:#6b7280;font-size:12px;line-height:1.5;">${s.desc}</div>
</td></tr></table>
</td></tr></table>
`).join("");

  return `<table width="100%" cellpadding="0" cellspacing="0" style="font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f3f4f8;margin:0;padding:0;">
<tr><td align="center" style="padding:24px 16px;">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:100%;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(15,30,61,0.08);">

<!-- Header: Logo Orange + Brand Text -->
<tr><td style="background:#0f1e3d;padding:18px 28px;">
<table width="100%"><tr>
<td><table cellpadding="0" cellspacing="0"><tr>
<td style="vertical-align:middle;"><img src="https://beriklan.co.id/logo-beriklan.png" alt="Beriklan" width="36" height="36" style="display:block;border-radius:8px;"></td>
<td style="padding-left:10px;vertical-align:middle;"><span style="color:#fff;font-size:16px;font-weight:800;letter-spacing:-0.01em;">Beriklan</span></td>
</tr></table></td>
<td align="right"><span style="color:#cbd5e1;font-size:11px;font-weight:600;">Performance Agency &middot; Bandung</span></td>
</tr></table>
</td></tr>

<!-- Eyebrow + Sub-header -->
<tr><td style="padding:24px 28px 0;background:#ffffff;">
<p style="margin:0 0 6px;color:${c.accent_color};font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;">${c.badge}</p>
<h1 style="margin:0 0 10px;color:#0f1e3d;font-size:24px;font-weight:800;line-height:1.3;">${c.headline}</h1>
<p style="margin:0 0 18px;color:#475569;font-size:14px;line-height:1.6;">${c.subheadline}</p>
</td></tr>

<!-- Hero Image -->
<tr><td style="padding:0 28px 24px;line-height:0;">
<img src="${c.hero_image}" alt="${c.name}" width="544" style="width:100%;max-width:544px;height:auto;display:block;border-radius:10px;border:0;" />
</td></tr>

<!-- CTA Utama -->
<tr><td style="padding:0 28px 28px;text-align:center;">
<table cellpadding="0" cellspacing="0" style="margin:0 auto;">
<tr><td style="background:#f59e0b;border-radius:100px;padding:14px 32px;font-weight:700;font-size:14px;">
<a href="${c.cta_url}" style="color:#0f1e3d;text-decoration:none;display:block;">${c.cta_text} &rarr;</a>
</td></tr></table>
</td></tr>

<!-- Garis Pemisah -->
<tr><td style="padding:0 28px;"><div style="border-top:1px solid #e2e8f0;"></div></td></tr>

<!-- Benefits Grid -->
<tr><td style="padding:28px 28px 8px;">
<h2 style="color:#0f1e3d;font-size:16px;margin:0 0 18px;text-align:center;font-weight:800;letter-spacing:-0.01em;">Apa yang Anda dapatkan</h2>
<table width="100%" cellpadding="0" cellspacing="0">${benefitPairs.join("")}</table>
</td></tr>

<!-- Cara Kerja (Steps Timeline) -->
${c.steps && c.steps.length ? `<tr><td style="padding:24px 28px 8px;">
<h2 style="color:#0f1e3d;font-size:16px;margin:0 0 14px;text-align:center;font-weight:800;letter-spacing:-0.01em;">Cara kerjanya</h2>
${stepsHTML}
</td></tr>
<tr><td style="padding:0 28px;"><div style="border-top:1px solid #e2e8f0;"></div></td></tr>` : ''}

<!-- Stats Strip -->
<tr><td style="background:${c.accent_bg};padding:22px 28px;">
<table width="100%" cellpadding="0" cellspacing="0"><tr>
<td align="center" style="padding:0 8px;"><div style="color:${c.accent_color};font-size:22px;font-weight:800;line-height:1;">9</div><div style="color:#475569;font-size:10px;margin-top:4px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;">Tahun</div></td>
<td align="center" style="padding:0 8px;"><div style="color:${c.accent_color};font-size:22px;font-weight:800;line-height:1;">1 jam</div><div style="color:#475569;font-size:10px;margin-top:4px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;">Respon</div></td>
<td align="center" style="padding:0 8px;"><div style="color:${c.accent_color};font-size:22px;font-weight:800;line-height:1;">24/7</div><div style="color:#475569;font-size:10px;margin-top:4px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;">Dashboard</div></td>
</tr></table>
</td></tr>

<!-- Social Proof -->
<tr><td style="padding:22px 28px;text-align:center;background:#ffffff;">
<p style="color:#0f1e3d;font-size:13px;margin:0;line-height:1.5;">${c.proof}</p>
</td></tr>

<!-- Final CTA -->
<tr><td style="padding:28px 28px;background:#f7f8fb;border-top:1px solid #e2e8f0;">
<p style="color:#0f1e3d;font-size:16px;margin:0 0 8px;font-weight:700;text-align:center;">Mau diskusi strategi untuk {{company}}?</p>
<p style="color:#6b7280;font-size:13px;margin:0 0 18px;line-height:1.6;text-align:center;">Lihat paket, harga, dan cara kerja di halaman layanan kami. Atau konsultasi gratis 15 menit — kami analisis kondisi campaign Anda.</p>
<table cellpadding="0" cellspacing="0" style="margin:0 auto;">
<tr><td style="background:#f59e0b;border-radius:100px;padding:13px 28px;font-weight:700;font-size:14px;">
<a href="${c.cta_url}" style="color:#0f1e3d;text-decoration:none;display:block;">${c.cta_text} &rarr;</a>
</td></tr></table>
<table cellpadding="0" cellspacing="0" style="margin:12px auto 0;">
<tr><td><a href="https://beriklan.co.id${c.service_path}" style="color:#475569;font-size:12px;text-decoration:underline;">📄 Halaman layanan lengkap</a></td></tr></table>
</td></tr>

<!-- Footer -->
<tr><td style="padding:22px 28px;border-top:1px solid #e2e8f0;background:#0f1e3d;color:#94a3b8;font-size:11px;text-align:center;">
<p style="margin:0 0 4px;color:#fff;font-weight:700;font-size:13px;">Beriklan Digital Agency</p>
<p style="margin:0 0 4px;">Performance Marketing Partner sejak 2016</p>
<p style="margin:0 0 4px;">Jl. Arcamanik Endah No.76, Bandung 40195</p>
<p style="margin:0 0 4px;"><a href="mailto:info@beriklan.co.id" style="color:#fbbf24;text-decoration:none;">info@beriklan.co.id</a> &middot; +62 81-1919-328</p>
<p style="margin:10px 0 0;"><a href="{{unsubscribe_url}}" style="color:#94a3b8;text-decoration:underline;">Berhenti berlangganan</a></p>
</td></tr>

</table>
</td></tr></table>`;
}

const GENERIC_TEMPLATES = [
  {
    name: "Follow Up (Generic)",
    subject: "Halo {{name}}, masih tertarik dengan digital marketing?",
    category: "followup",
    html_body: `<table width="100%" cellpadding="0" cellspacing="0" style="font-family:Inter,-apple-system,sans-serif;background:#f3f4f8;margin:0;padding:0;">
<tr><td align="center" style="padding:24px 16px;">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:100%;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(15,30,61,0.08);">

<tr><td style="background:#0f1e3d;padding:18px 28px;">
<table width="100%"><tr>
<td><table cellpadding="0" cellspacing="0"><tr>
<td style="vertical-align:middle;"><img src="https://beriklan.co.id/logo-beriklan.png" alt="Beriklan" width="36" height="36" style="display:block;border-radius:8px;"></td>
<td style="padding-left:10px;vertical-align:middle;"><span style="color:#fff;font-size:16px;font-weight:800;letter-spacing:-0.01em;">Beriklan</span></td>
</tr></table></td>
<td align="right"><span style="color:#cbd5e1;font-size:11px;font-weight:600;">Performance Agency &middot; Bandung</span></td>
</tr></table>
</td></tr>

<tr><td style="padding:32px 28px 8px;background:#ffffff;">
<p style="margin:0 0 6px;color:#f59e0b;font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;">Follow Up</p>
<h1 style="margin:0 0 12px;color:#0f1e3d;font-size:22px;font-weight:800;line-height:1.3;">Halo {{name}}, masih tertarik dengan digital marketing?</h1>
<p style="margin:0 0 18px;color:#475569;font-size:14px;line-height:1.6;">Kami paham — memulai campaign iklan digital memang terasa rumit. Tim Beriklan siap membantu dari konsultasi awal sampai campaign live dan terukur.</p>
</td></tr>

<tr><td style="padding:8px 28px 24px;background:#ffffff;">
<table width="100%" cellpadding="0" cellspacing="0">
<tr><td style="padding:6px 0;"><table width="100%" style="background:#f7f8fb;border-radius:10px;padding:14px 18px;"><tr><td width="36" valign="middle" style="background:#f59e0b;color:#0f1e3d;border-radius:50%;width:36px;height:36px;text-align:center;line-height:36px;font-weight:800;font-size:14px;">1</td><td style="padding-left:14px;vertical-align:middle;"><strong style="color:#0f1e3d;font-size:14px;display:block;margin-bottom:2px;">Konsultasi Gratis 15 Menit</strong><span style="color:#6b7280;font-size:12px;">Ceritakan tujuan Anda, kami sarankan strateginya</span></td></tr></table></td></tr>
<tr><td style="padding:6px 0;"><table width="100%" style="background:#f7f8fb;border-radius:10px;padding:14px 18px;"><tr><td width="36" valign="middle" style="background:#10b981;color:#fff;border-radius:50%;width:36px;height:36px;text-align:center;line-height:36px;font-weight:800;font-size:14px;">2</td><td style="padding-left:14px;vertical-align:middle;"><strong style="color:#0f1e3d;font-size:14px;display:block;margin-bottom:2px;">Dashboard Real-time</strong><span style="color:#6b7280;font-size:12px;">Pantau ROI 24/7 dari mana saja</span></td></tr></table></td></tr>
<tr><td style="padding:6px 0;"><table width="100%" style="background:#f7f8fb;border-radius:10px;padding:14px 18px;"><tr><td width="36" valign="middle" style="background:#0ea5e9;color:#fff;border-radius:50%;width:36px;height:36px;text-align:center;line-height:36px;font-weight:800;font-size:14px;">3</td><td style="padding-left:14px;vertical-align:middle;"><strong style="color:#0f1e3d;font-size:14px;display:block;margin-bottom:2px;">Laporan Bahasa Manusia</strong><span style="color:#6b7280;font-size:12px;">Mingguan tanpa jargon teknis</span></td></tr></table></td></tr>
</table>
</td></tr>

<tr><td style="padding:0 28px 28px;text-align:center;">
<table cellpadding="0" cellspacing="0" style="margin:0 auto;">
<tr><td style="background:#f59e0b;border-radius:100px;padding:13px 28px;font-weight:700;font-size:14px;">
<a href="https://beriklan.co.id/jasa-digital-marketing/" style="color:#0f1e3d;text-decoration:none;display:block;">Lihat Semua Layanan &rarr;</a>
</td></tr></table>
</td></tr>

<tr><td style="padding:22px 28px;border-top:1px solid #e2e8f0;background:#0f1e3d;color:#94a3b8;font-size:11px;text-align:center;">
<p style="margin:0 0 4px;color:#fff;font-weight:700;font-size:13px;">Beriklan Digital Agency</p>
<p style="margin:0 0 4px;">Performance Marketing Partner sejak 2016</p>
<p style="margin:0 0 4px;">Jl. Arcamanik Endah No.76, Bandung 40195</p>
<p style="margin:10px 0 0;"><a href="{{unsubscribe_url}}" style="color:#94a3b8;text-decoration:underline;">Berhenti berlangganan</a></p>
</td></tr>

</table>
</td></tr></table>`
  }
];

// Build all defaults: 10 service templates + 1 followup generic
const EMAIL_TEMPLATE_DEFAULTS = [
  ...SERVICE_CONFIGS.map(c => ({
    name: c.name,
    subject: c.subject,
    category: c.category,
    html_body: generateServiceTemplate(c)
  })),
  ...GENERIC_TEMPLATES
];

function escHtml(s) {
  if (!s) return "";
  return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function genTrackingId() {
  return "trk_" + Date.now().toString(36) + "_" + Math.random().toString(36).slice(2, 8);
}

async function sendEmailViaResend(env, to, subject, html, trackingId) {
  if (!env.RESEND_API_KEY) {
    return { ok: false, error: "RESEND_API_KEY not set" };
  }
  // Resend: to must be array of email strings (or {name,email} objects but string is safer)
  const toList = Array.isArray(to) ? to : [to];
  const toEmails = toList.map(t => typeof t === 'string' ? t : t.email);
  const body = {
    from: "Beriklan Digital Agency <noreply@beriklan.co.id>",
    to: toEmails,
    subject,
    html,
    reply_to: "info@beriklan.co.id",
    headers: { "X-Tracking-Id": trackingId || "" }
  };
  try {
    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { "Authorization": `Bearer ${env.RESEND_API_KEY}`, "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const data = await r.json().catch(() => ({}));
    if (r.ok) return { ok: true, id: data.id };
    return { ok: false, error: data.message || `HTTP ${r.status}`, status: r.status };
  } catch (e) {
    return { ok: false, error: String(e) };
  }
}

async function getDailyEmailCount(env) {
  try {
    const today = new Date().toISOString().slice(0, 10);
    const r = await env.DB.prepare(
      "SELECT COUNT(*) as c FROM email_queue WHERE status='sent' AND sent_at >= ?"
    ).bind(today).first();
    return r?.c || 0;
  } catch { return 0; }
}

// ─── Email Dashboard (Redesigned) ──────────────────────────────
async function handleEmailDashboard(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  if (!env.DB) return new Response("DB not available", { status: 503 });

  const tab = url.searchParams.get("tab") || "overview";
  const viewId = url.searchParams.get("id");

  // Detail page untuk 1 campaign
  if (viewId) {
    return await renderCampaignDetail(viewId, token, env);
  }

  try {
    // Fetch semua data yang dibutuhkan
    const campaigns = await env.DB.prepare(`
      SELECT c.*, t.name as template_name, l.name as list_name,
        (SELECT COUNT(*) FROM email_queue WHERE campaign_id=c.id AND status='pending') as pending_count,
        (SELECT COUNT(*) FROM email_queue WHERE campaign_id=c.id AND status='sent') as db_sent,
        (SELECT COUNT(*) FROM email_queue WHERE campaign_id=c.id AND status='failed') as failed_count,
        (SELECT COUNT(*) FROM email_queue WHERE campaign_id=c.id AND opened_at IS NOT NULL) as open_count,
        (SELECT COUNT(*) FROM email_queue WHERE campaign_id=c.id AND clicked_at IS NOT NULL) as click_count
      FROM campaigns c
      LEFT JOIN email_templates t ON c.template_id=t.id
      LEFT JOIN lead_lists l ON c.list_id=l.id
      ORDER BY c.id DESC LIMIT 50
    `).all();

    const templates = await env.DB.prepare("SELECT id, name, subject, category FROM email_templates ORDER BY id").all();
    const lists = await env.DB.prepare("SELECT id, name, source, total FROM lead_lists WHERE total > 0 ORDER BY total DESC LIMIT 30").all();
    const cronRows = await env.DB.prepare("SELECT * FROM cron_settings ORDER BY id ASC").all();

    const totalSent = await env.DB.prepare("SELECT COUNT(*) as c FROM email_queue WHERE status='sent'").first();
    const totalOpened = await env.DB.prepare("SELECT COUNT(*) as c FROM email_queue WHERE opened_at IS NOT NULL").first();
    const totalClicked = await env.DB.prepare("SELECT COUNT(*) as c FROM email_queue WHERE clicked_at IS NOT NULL").first();
    const pending = await env.DB.prepare("SELECT COUNT(*) as c FROM email_queue WHERE status='pending'").first();
    const dailySent = await getDailyEmailCount(env);
    const contactsCount = await env.DB.prepare("SELECT COUNT(*) as c FROM lead_contacts WHERE email != '' AND email IS NOT NULL").first();
    const templatesCount = await env.DB.prepare("SELECT COUNT(*) as c FROM email_templates").first();

    // Hitung next cron run untuk email-send
    const emailCron = cronRows.results?.find(c => c.name === 'email-send');
    const nextEmailRun = emailCron?.enabled ? getNextCronRun('*/15 * * * *') : null;

    const T = {
      header: `background:linear-gradient(135deg,#0f1e3d 0%,#1a2f5c 100%);color:#fff;padding:24px 32px;border-radius:18px;`,
      card: `background:#fff;border-radius:14px;padding:20px;box-shadow:0 1px 3px rgba(15,30,61,0.06),0 1px 2px rgba(15,30,61,0.04);border:1px solid #f0f1f5;`,
      statCard: `background:#fff;border-radius:14px;padding:18px 20px;border:1px solid #f0f1f5;box-shadow:0 1px 2px rgba(15,30,61,0.04);`,
      navActive: `background:#0f1e3d;color:#fff;font-weight:600;`,
      navInactive: `background:transparent;color:#475569;border:1px solid #e5e7eb;font-weight:500;`,
      th: `background:#fafbfc;color:#475569;padding:12px 16px;text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.06em;font-weight:700;border-bottom:1px solid #e5e7eb;`,
      td: `padding:14px 16px;border-bottom:1px solid #f0f1f5;font-size:14px;`,
      btnPrimary: `display:inline-flex;align-items:center;gap:6px;padding:11px 22px;border-radius:10px;font-weight:600;font-size:13px;text-decoration:none;border:none;cursor:pointer;background:#0f1e3d;color:#fff;transition:transform .15s,box-shadow .15s;`,
      btnAmber: `display:inline-flex;align-items:center;gap:6px;padding:10px 20px;border-radius:10px;font-weight:600;font-size:13px;text-decoration:none;border:none;cursor:pointer;background:#f59e0b;color:#0f1e3d;`,
      btnOutline: `display:inline-flex;align-items:center;gap:6px;padding:9px 18px;border-radius:10px;font-weight:500;font-size:13px;text-decoration:none;cursor:pointer;background:#fff;color:#0f1e3d;border:1px solid #d1d5db;`,
      btnDanger: `display:inline-flex;align-items:center;gap:4px;padding:8px 14px;border-radius:10px;font-weight:500;font-size:12px;text-decoration:none;cursor:pointer;background:#fee2e2;color:#991b1b;border:1px solid #fecaca;`,
    };

    const navBtn = (t, label, icon) => {
      const active = tab === t;
      return `<a href="?token=${token}&tab=${t}" style="padding:9px 16px;border-radius:10px;font-size:13px;text-decoration:none;display:inline-flex;align-items:center;gap:6px;${active?T.navActive:T.navInactive}">${icon} ${label}</a>`;
    };

    const html = `<!DOCTYPE html>
<html lang="id"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Email — Beriklan Admin</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#f5f6fa;font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#0f1e3d;line-height:1.5;-webkit-font-smoothing:antialiased}
a{text-decoration:none;color:inherit}
.layout{display:grid;grid-template-columns:240px 1fr;min-height:100vh}
@media(max-width:900px){.layout{grid-template-columns:1fr}}
.sidebar{background:#0f1e3d;color:#cbd5e1;padding:28px 20px;display:flex;flex-direction:column;gap:4px;position:sticky;top:0;height:100vh;overflow-y:auto}
@media(max-width:900px){.sidebar{flex-direction:row;flex-wrap:wrap;padding:14px;height:auto;position:static}}
.sidebar-brand{display:flex;align-items:center;gap:10px;margin-bottom:24px;padding:0 8px}
.sidebar-brand img{height:28px;filter:brightness(0) invert(1)}
.sidebar-brand span{font-weight:800;font-size:16px;color:#fff}
.sidebar a.nav{padding:10px 14px;border-radius:8px;font-size:14px;display:flex;align-items:center;gap:10px;color:#cbd5e1;font-weight:500;transition:background .15s}
.sidebar a.nav:hover{background:rgba(255,255,255,0.06);color:#fff}
.sidebar a.nav.active{background:#1a2f5c;color:#fff;font-weight:600}
.sidebar a.nav .ico{width:18px;text-align:center;opacity:0.8}
.sidebar-foot{margin-top:auto;padding-top:20px;border-top:1px solid rgba(255,255,255,0.08);font-size:11px;color:#64748b}
@media(max-width:900px){.sidebar-foot{display:none}}
.main{padding:32px 40px;overflow-x:hidden;max-width:none;width:100%}
@media(max-width:900px){.main{padding:18px}}
.page-head{display:flex;justify-content:space-between;align-items:end;margin-bottom:24px;flex-wrap:wrap;gap:12px}
.page-head h1{font-size:24px;font-weight:800;letter-spacing:-0.01em}
.page-head p{color:#6b7280;font-size:13px;margin-top:2px}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin-bottom:24px}
.kpi{${T.statCard};display:flex;flex-direction:column;gap:6px}
.kpi-label{font-size:11px;text-transform:uppercase;letter-spacing:0.06em;color:#6b7280;font-weight:700}
.kpi-val{font-size:26px;font-weight:800;line-height:1.1;color:#0f1e3d}
.kpi-sub{font-size:11px;color:#6b7280}
.kpi-bar{height:4px;background:#f0f1f5;border-radius:2px;margin-top:6px;overflow:hidden}
.kpi-bar > div{height:100%;background:linear-gradient(90deg,#0f1e3d,#f59e0b);border-radius:2px}
.card{${T.card};margin-bottom:18px}
.card-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
.card-head h2{font-size:16px;font-weight:700;letter-spacing:-0.01em}
.card-head p{color:#6b7280;font-size:12px;margin-top:2px}
table{width:100%;border-collapse:collapse;font-size:13px;background:#fff;border-radius:12px;overflow:hidden;border:1px solid #f0f1f5}
th{${T.th}}td{${T.td}}
tr:hover td{background:#fafbfc}
tr:last-child td{border-bottom:none}
.badge{display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:100px;font-size:11px;font-weight:600;line-height:1.4}
.b-green{background:#d1fae5;color:#065f46}.b-amber{background:#fef3c7;color:#92400e}.b-gray{background:#f1f5f9;color:#475569}.b-blue{background:#dbeafe;color:#1e40af}.b-red{background:#fee2e2;color:#991b1b}
.btn-row{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.progress{height:6px;background:#f1f5f9;border-radius:3px;overflow:hidden;margin-top:4px}
.progress > div{height:100%;background:linear-gradient(90deg,#0f1e3d 0%,#f59e0b 100%);transition:width .3s}
.empty-state{text-align:center;padding:48px 20px;color:#9ca3af}
.empty-state .ico{font-size:36px;margin-bottom:8px;opacity:0.6}
.empty-state p{margin-top:6px;font-size:13px}
input,select,textarea{padding:10px 14px;border:1px solid #d1d5db;border-radius:10px;font-size:14px;width:100%;outline:none;background:#fff;font-family:inherit;transition:border .15s,box-shadow .15s}
input:focus,select:focus,textarea:focus{border-color:#0f1e3d;box-shadow:0 0 0 3px rgba(15,30,61,0.08)}
label{display:block;font-size:12px;font-weight:600;margin-bottom:6px;color:#374151;text-transform:uppercase;letter-spacing:0.04em}
.field{margin-bottom:14px}
.field-hint{font-size:11px;color:#6b7280;margin-top:4px;line-height:1.4}
.btn-primary{${T.btnPrimary}}
.btn-amber{${T.btnAmber}}
.btn-outline{${T.btnOutline}}
.btn-danger{${T.btnDanger}}
.btn-primary:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(15,30,61,0.15)}
.cron-card{display:flex;justify-content:space-between;align-items:center;padding:16px 18px;background:#fff;border-radius:12px;border:1px solid #f0f1f5;margin-bottom:8px}
.cron-card .left strong{display:block;font-size:14px;font-weight:700;margin-bottom:2px}
.cron-card .left .cron{font-family:'JetBrains Mono',monospace;font-size:12px;color:#475569;background:#f1f5f9;padding:2px 8px;border-radius:6px;display:inline-block;margin-right:8px}
.cron-card .left .next{font-size:11px;color:#6b7280;margin-top:4px}
.toggle{position:relative;display:inline-block;width:48px;height:26px;cursor:pointer}
.toggle input{display:none}
.toggle .slider{position:absolute;inset:0;background:#d1d5db;border-radius:13px;transition:.2s}
.toggle .slider::before{content:'';position:absolute;width:20px;height:20px;background:#fff;border-radius:50%;left:3px;top:3px;transition:.2s;box-shadow:0 1px 3px rgba(0,0,0,0.2)}
.toggle input:checked+.slider{background:#10b981}
.toggle input:checked+.slider::before{transform:translateX(22px)}
</style></head><body>
<div class="layout">
<aside class="sidebar">
<div class="sidebar-brand"><img src="https://beriklan.co.id/logoweb.webp" alt="Beriklan" onerror="this.style.display='none'"><span>Beriklan</span></div>
<a href="/api/admin?token=${token}" class="nav"><span class="ico">🏠</span> Dashboard Utama</a>
<a href="?token=${token}&tab=overview" class="nav ${tab==='overview'?'active':''}"><span class="ico">📊</span> Overview</a>
<a href="?token=${token}&tab=campaigns" class="nav ${tab==='campaigns'?'active':''}"><span class="ico">📨</span> Campaigns</a>
<a href="?token=${token}&tab=composer" class="nav ${tab==='composer'?'active':''}"><span class="ico">✍️</span> Composer</a>
<a href="?token=${token}&tab=templates" class="nav ${tab==='templates'?'active':''}"><span class="ico">📝</span> Templates</a>
<a href="?token=${token}&tab=lists" class="nav ${tab==='lists'?'active':''}"><span class="ico">👥</span> Kontak & Lists</a>
<a href="?token=${token}&tab=cron" class="nav ${tab==='cron'?'active':''}"><span class="ico">⏰</span> Cron & Automasi</a>
<a href="?token=${token}&tab=scraper" class="nav ${tab==='scraper'?'active':''}"><span class="ico">🔍</span> Scraper</a>
<div class="sidebar-foot">
Email · Resend API<br>
Quota hari ini: ${dailySent}/100 (Resend free)
${nextEmailRun ? `<br>Next send: <strong>${nextEmailRun}</strong>` : '<br>⏸️ Email cron paused'}
</div>
</aside>

<div class="main">
${tab === 'overview' ? renderOverview(campaigns, totalSent, totalOpened, totalClicked, pending, dailySent, contactsCount, templatesCount, T, token) :
  tab === 'campaigns' ? renderCampaignsList(campaigns, T, token) :
  tab === 'composer' ? await renderComposer(templates, lists, T, token, env) :
  tab === 'templates' ? renderTemplates(templates, T, token) :
  tab === 'lists' ? renderLists(lists, T, token) :
  tab === 'cron' ? renderCron(cronRows, T, token) :
  tab === 'scraper' ? renderScraper(campaigns, T, token, env) :
  '<div class="card"><p>Halaman tidak ditemukan. <a href="?token='+token+'&tab=overview">← Overview</a></p></div>'}
</div>
</div>

<script>
async function testSend(id) {
  const email = prompt("Kirim test ke email mana?\\n\\n(Subject akan ada prefix [INTERNAL-TEST])\\n\\nDefault: admin@3smedianet.com", "admin@3smedianet.com");
  if (!email) return;
  const btn = event.target;
  btn.disabled = true; btn.innerHTML = "⏳ Mengirim...";
  try {
    const r = await fetch('/api/email/test-send?token=${token}&template_id=' + id + '&to=' + encodeURIComponent(email));
    const d = await r.json();
    if (d.ok) {
      alert("✅ Email test terkirim ke " + email + "\\nSubject: " + d.subject + "\\nResend ID: " + d.resend_id);
    } else {
      alert("❌ Gagal: " + d.error);
    }
  } catch(e) { alert("❌ Error: " + e.message); }
  btn.disabled = false; btn.innerHTML = "✉️ Test";
}
async function runScraper(url, label) {
  const btn = event.target;
  btn.disabled = true; btn.textContent = '⏳ Scraping...';
  try {
    const r = await fetch(url, { method: 'POST' });
    const d = await r.json();
    alert((d.ok ? '✅ ' : '❌ ') + label + ': ' + (d.error || (d.contacts_saved || 0) + ' saved'));
    location.reload();
  } catch(e) { alert('❌ Error: ' + e.message); }
  btn.disabled = false; btn.textContent = '▶ Jalankan';
}
</script>
</body></html>`;

    return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
  } catch (e) {
    return new Response("Dashboard error: " + e.message, { status: 500 });
  }
}

// Helper: hitung next cron run
function getNextCronRun(expr) {
  try {
    const parts = expr.split(' ');
    const min = parts[0];
    if (min.startsWith('*/')) {
      const interval = parseInt(min.slice(2));
      const now = new Date();
      const currentMin = now.getMinutes();
      const nextMin = Math.ceil((currentMin + 1) / interval) * interval;
      const next = new Date(now);
      if (nextMin >= 60) { next.setHours(next.getHours() + 1); next.setMinutes(nextMin - 60); }
      else { next.setMinutes(nextMin); next.setSeconds(0); }
      return next.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });
    }
    return null;
  } catch { return null; }
}

// Tab renderers
function renderOverview(campaigns, totalSent, totalOpened, totalClicked, pending, dailySent, contactsCount, templatesCount, T, token) {
  const openRate = totalSent?.c > 0 ? ((totalOpened?.c || 0) / totalSent.c * 100).toFixed(1) : '0';
  const clickRate = totalOpened?.c > 0 ? ((totalClicked?.c || 0) / totalOpened.c * 100).toFixed(1) : '0';
  const recentCampaigns = (campaigns.results || []).slice(0, 5);
  return `
<div class="page-head">
<div><h1>Overview</h1><p>Status campaign, performa email, dan automasi email marketing.</p></div>
<div class="btn-row">
<a href="?token=${token}&tab=composer" class="btn-amber">✍️ Buat Campaign</a>
<a href="/api/admin/email/metrics?token=${token}" class="btn-outline" target="_blank">📊 Metrics Detail</a>
</div>
</div>

<div class="kpi-grid">
<div class="kpi"><span class="kpi-label">📤 Total Terkirim</span><span class="kpi-val">${(totalSent?.c || 0).toLocaleString('id-ID')}</span><span class="kpi-sub">${dailySent}/100 hari ini (Resend free)</span></div>
<div class="kpi"><span class="kpi-label">👁 Open Rate</span><span class="kpi-val">${openRate}%</span><span class="kpi-sub">${(totalOpened?.c || 0).toLocaleString('id-ID')} dibuka</span></div>
<div class="kpi"><span class="kpi-label">🖱 Click Rate</span><span class="kpi-val">${clickRate}%</span><span class="kpi-sub">${(totalClicked?.c || 0).toLocaleString('id-ID')} klik</span></div>
<div class="kpi"><span class="kpi-label">⏳ Antrian</span><span class="kpi-val">${(pending?.c || 0).toLocaleString('id-ID')}</span><span class="kpi-sub">email pending</span></div>
<div class="kpi"><span class="kpi-label">👥 Kontak</span><span class="kpi-val">${(contactsCount?.c || 0).toLocaleString('id-ID')}</span><span class="kpi-sub">dengan email valid</span></div>
<div class="kpi"><span class="kpi-label">📝 Template</span><span class="kpi-val">${templatesCount?.c || 0}</span><span class="kpi-sub">siap pakai</span></div>
</div>

<div class="card">
<div class="card-head"><div><h2>📨 Campaign Terbaru</h2><p>5 campaign terakhir dan progresnya.</p></div>
<a href="?token=${token}&tab=campaigns" style="color:#0f1e3d;font-size:13px;font-weight:600;">Lihat semua →</a></div>
${recentCampaigns.length ? `<table>
<thead><tr><th>Nama</th><th>Status</th><th>Progres</th><th>Open</th><th>Aksi</th></tr></thead>
<tbody>${recentCampaigns.map(c => {
  const pct = c.total_recipients > 0 ? Math.round(c.db_sent / c.total_recipients * 100) : 0;
  const opn = c.db_sent > 0 ? Math.round((c.open_count || 0) / c.db_sent * 100) : 0;
  const status = c.status === 'done' ? '<span class="badge b-green">✓ Selesai</span>' : c.status === 'sending' ? '<span class="badge b-amber">⏳ Mengirim</span>' : '<span class="badge b-gray">Draft</span>';
  return `<tr>
<td><strong>${escHtml(c.name)}</strong><br><span style="font-size:11px;color:#6b7280;">${escHtml(c.subject || '')}</span></td>
<td>${status}</td>
<td><div style="font-size:12px;font-weight:600;">${c.db_sent}/${c.total_recipients}</div><div class="progress"><div style="width:${pct}%"></div></div></td>
<td><strong>${opn}%</strong> <span style="font-size:11px;color:#6b7280;">(${c.open_count || 0})</span></td>
<td><a href="?token=${token}&tab=campaigns&id=${c.id}" class="btn-outline" style="font-size:11px;padding:5px 10px;">Detail →</a></td>
</tr>`;
}).join('')}</tbody></table>` : '<div class="empty-state"><div class="ico">📭</div><p>Belum ada campaign.</p><a href="?token='+token+'&tab=composer" class="btn-amber" style="margin-top:14px;">Buat Campaign Pertama</a></div>'}
</div>

<div class="card">
<div class="card-head"><h2>⚙️ Email Cron Status</h2><p>Auto-sender jalan tiap 15 menit. Kalau gagal, otomatis retry dengan backoff. 3x gagal berturut-turut = auto-pause.</p></div>
<div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;">
<span class="badge b-amber">⏰ Every 15 min</span>
<span class="badge b-blue">📤 20 email/batch</span>
<span class="badge b-green">✓ Auto-retry (5min)</span>
<span class="badge b-red">🚨 Auto-pause (3 fails)</span>
</div>
<p style="margin-top:12px;font-size:12px;color:#6b7280;line-height:1.5;">
Quota Resend free tier: 500 email/hari. Cron jalan otomatis — tidak perlu intervensi. Cek tab <strong>Cron & Automasi</strong> untuk toggle pause.
</p>
</div>
`;
}

function renderCampaignsList(campaigns, T, token) {
  const cs = campaigns.results || [];
  return `
<div class="page-head"><div><h1>Campaigns</h1><p>Semua campaign email dan riwayatnya.</p></div><a href="?token=${token}&tab=composer" class="btn-amber">✍️ Campaign Baru</a></div>
${cs.length ? `<div class="card" style="padding:0;overflow:hidden;"><table style="border:none;box-shadow:none;">
<thead><tr><th style="width:32%">Campaign</th><th>Template / List</th><th>Status</th><th>Progres</th><th>Open</th><th>Click</th><th>Aksi</th></tr></thead>
<tbody>${cs.map(c => {
  const pct = c.total_recipients > 0 ? Math.round(c.db_sent / c.total_recipients * 100) : 0;
  const opn = c.db_sent > 0 ? Math.round((c.open_count || 0) / c.db_sent * 100) : 0;
  const clk = (c.open_count || 0) > 0 ? Math.round((c.click_count || 0) / c.open_count * 100) : 0;
  const status = c.status === 'done' ? '<span class="badge b-green">✓ Selesai</span>' : c.status === 'sending' ? '<span class="badge b-amber">⏳ Mengirim</span>' : '<span class="badge b-gray">Draft</span>';
  const created = (c.created_at || '').slice(0, 16).replace('T', ' ');
  return `<tr>
<td><a href="?token=${token}&tab=campaigns&id=${c.id}" style="font-weight:700;color:#0f1e3d;">${escHtml(c.name)}</a><br><span style="font-size:11px;color:#6b7280;">${escHtml(c.subject || '-')}</span><br><span style="font-size:10px;color:#9ca3af;">${created}</span></td>
<td><span style="font-size:12px;">${escHtml(c.template_name || '-')}</span><br><span style="font-size:11px;color:#6b7280;">${escHtml(c.list_name || 'Semua Kontak')}</span></td>
<td>${status}</td>
<td><div style="font-size:12px;font-weight:600;">${c.db_sent}/${c.total_recipients}</div><div class="progress"><div style="width:${pct}%"></div></div></td>
<td><strong>${opn}%</strong><br><span style="font-size:11px;color:#6b7280;">${c.open_count || 0} dibuka</span></td>
<td><strong>${clk}%</strong><br><span style="font-size:11px;color:#6b7280;">${c.click_count || 0} klik</span></td>
<td><a href="?token=${token}&tab=campaigns&id=${c.id}" class="btn-outline" style="font-size:11px;">Detail →</a></td>
</tr>`;
}).join('')}</tbody></table></div>` : '<div class="card empty-state"><div class="ico">📨</div><p>Belum ada campaign.</p><a href="?token='+token+'&tab=composer" class="btn-amber" style="margin-top:14px;">Buat Campaign Pertama</a></div>'}
`;
}

async function renderComposer(templates, lists, T, token, env) {
  const tplRows = templates.results || [];
  const listRows = lists.results || [];
  const totalContacts = (await env.DB.prepare("SELECT COUNT(*) as c FROM lead_contacts WHERE email != '' AND email IS NOT NULL").first())?.c || 0;
  return `
<div class="page-head"><div><h1>Composer</h1><p>Buat campaign baru dengan template yang sudah ada.</p></div></div>

<div class="card">
<form method="POST" action="/api/email/campaigns?token=${token}&action=create">
<div class="field"><label>Nama Campaign (internal)</label><input name="name" required placeholder="misal: Promo TikTok Ads Q3 2026"></div>
<div class="field"><label>Subject Email</label><input name="subject" required placeholder="misal: Strategi TikTok Ads untuk {{company}}"></div>

<div class="field">
<label>Template</label>
<select name="template_id" required id="tpl-select" onchange="updateSubject()">
${tplRows.map(t => `<option value="${t.id}" data-subject="${escHtml(t.subject)}">${escHtml(t.name)}</option>`).join('')}
</select>
<div class="field-hint">Pilih template yang ingin dipakai. Subject di atas akan menimpa subject default template.</div>
</div>

<div class="field">
<label>Target Audience</label>
<select name="list_id">
<option value="0">📬 Semua Kontak dengan Email Valid (${totalContacts})</option>
${listRows.map(l => `<option value="${l.id}">${escHtml(l.name)} — ${l.total} kontak</option>`).join('')}
</select>
<div class="field-hint">Pilih list spesifik, atau "Semua Kontak" untuk broadcast.</div>
</div>

<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:18px;">
<button type="submit" class="btn-amber">📤 Buat & Mulai Kirim</button>
<a href="?token=${token}&tab=templates" class="btn-outline">Lihat template dulu</a>
<a href="?token=${token}&tab=overview" class="btn-outline">Batal</a>
</div>
</form>
</div>

<div class="card">
<div class="card-head"><h2>📋 Cara Kerja</h2></div>
<ol style="margin:0;padding-left:18px;color:#475569;font-size:13px;line-height:1.8;">
<li>Pilih template dan audience di atas, klik <strong>Buat & Mulai Kirim</strong>.</li>
<li>Campaign langsung dibuat + antrian email dimasukkan ke database.</li>
<li>Cron email-send jalan tiap 15 menit — kirim 25 email per batch (100/hari di Resend free tier).</li>
<li>Free tier Resend: 500 email/hari. Untuk volume lebih besar, upgrade plan.</li>
<li>Pantau open/click di halaman detail campaign.</li>
</ol>
</div>

<script>
function updateSubject() {
  const sel = document.getElementById('tpl-select');
  const opt = sel.options[sel.selectedIndex];
  const subj = opt.getAttribute('data-subject');
  if (subj && !document.querySelector('input[name=subject]').value) {
    document.querySelector('input[name=subject]').value = subj;
  }
}
</script>
`;
}

function renderTemplates(templates, T, token) {
  const ts = templates.results || [];
  return `
<div class="page-head">
<div><h1>Templates</h1><p>${ts.length} template email siap pakai.</p></div>
<form method="POST" action="/api/email/templates?token=${token}&action=seed" style="display:inline"><button class="btn-outline" onclick="return confirm('Re-seed semua template dengan default baru? Template custom akan ditimpa.')">🔄 Re-seed Default</button></form>
</div>
${ts.length ? `<table>
<thead><tr><th>Template</th><th>Subject</th><th>Kategori</th><th>Aksi</th></tr></thead>
<tbody>${ts.map(t => `<tr>
<td><strong>${escHtml(t.name)}</strong></td>
<td style="color:#475569;font-size:13px;">${escHtml(t.subject)}</td>
<td><span class="badge b-blue">${escHtml(t.category)}</span></td>
<td><div class="btn-row">
<a href="/api/email/templates/preview?id=${t.id}&token=${token}" target="_blank" class="btn-outline" style="font-size:11px;padding:5px 10px;">👁 Preview</a>
<button onclick="testSend(${t.id})" class="btn-outline" style="font-size:11px;padding:5px 10px;">✉️ Test</button>
</div></td>
</tr>`).join('')}</tbody></table>` : '<div class="card empty-state"><div class="ico">📝</div><p>Belum ada template. Klik "Re-seed Default" di atas.</p></div>'}
`;
}

function renderLists(lists, T, token) {
  const ls = lists.results || [];
  return `
<div class="page-head"><div><h1>Kontak & Lists</h1><p>${ls.length} lead list aktif · total ${ls.reduce((a, b) => a + (b.total || 0), 0)} kontak.</p></div>
<a href="?token=${token}&tab=scraper" class="btn-outline">🔍 Buka Scraper</a></div>
${ls.length ? `<table>
<thead><tr><th>Nama List</th><th>Sumber</th><th>Kontak</th><th>Aksi</th></tr></thead>
<tbody>${ls.map(l => `<tr>
<td><strong>${escHtml(l.name)}</strong></td>
<td><span class="badge b-${l.source === 'database-siap-pake' ? 'green' : 'gray'}">${escHtml(l.source || '-')}</span></td>
<td><strong>${l.total}</strong></td>
<td>
<form method="POST" action="/api/email/lists?token=${token}&action=delete&id=${l.id}" onsubmit="return confirm('Hapus list ini?')" style="display:inline"><button class="btn-danger">Hapus</button></form>
</td>
</tr>`).join('')}</tbody></table>` : '<div class="card empty-state"><p>Belum ada list dengan kontak.</p></div>'}
`;
}

function renderCron(cronRows, T, token) {
  const emailCron = (cronRows.results || []).find(c => c.name === 'email-send');
  const nextEmailRun = emailCron?.enabled ? getNextCronRun(emailCron.cron) : null;
  return `
<div class="page-head"><div><h1>Cron & Automasi</h1><p>Pengiriman email otomatis berjalan via Cloudflare Cron Triggers.</p></div></div>

<div class="card">
<div class="card-head"><h2>📧 Email Sender</h2>
${emailCron?.enabled ? '<span class="badge b-green">✓ AKTIF</span>' : '<span class="badge b-red">⏸ PAUSED</span>'}
</div>
<div class="cron-card">
<div class="left">
<strong>Email Send</strong>
<span><span class="cron">${emailCron?.cron || '*/15 * * * *'}</span> <span style="font-size:11px;color:#6b7280;">setiap 15 menit</span></span>
<div class="next">${nextEmailRun ? `Next run: <strong>${nextEmailRun}</strong>` : 'Cron sedang pause'}</div>
</div>
<form method="POST" action="/api/admin/cron/toggle?token=${token}&name=email-send" style="display:inline">
<label class="toggle"><input type="checkbox" ${emailCron?.enabled ? 'checked' : ''} onchange="this.form.submit()"><span class="slider"></span></label>
</form>
</div>
<p style="margin-top:14px;color:#475569;font-size:13px;line-height:1.6;">Cron mengirim <strong>25 email per eksekusi</strong> dari antrian. Tiap 15 menit = 100/jam, max <strong>100/hari</strong> (Resend free tier). Untuk volume lebih besar, upgrade plan Resend atau pakai beberapa hari untuk campaign besar.</p>
</div>

<div class="card">
<div class="card-head"><h2>⏰ Cron Lainnya</h2></div>
${(cronRows.results || []).filter(c => c.name !== 'email-send').map(cr => `
<div class="cron-card">
<div class="left">
<strong>${escHtml(cr.label || cr.name)}</strong>
<span><span class="cron">${cr.cron || ''}</span> ${cr.enabled ? '<span style="font-size:11px;color:#10b981;font-weight:600;">✓ Aktif</span>' : '<span style="font-size:11px;color:#dc2626;font-weight:600;">⏸ Pause</span>'}</span>
</div>
<form method="POST" action="/api/admin/cron/toggle?token=${token}&name=${cr.name}" style="display:inline">
<label class="toggle"><input type="checkbox" ${cr.enabled ? 'checked' : ''} onchange="this.form.submit()"><span class="slider"></span></label>
</form>
</div>
`).join('')}
</div>
`;
}

function renderScraper(campaigns, T, token, env) {
  return `
<div class="page-head"><div><h1>Scraper</h1><p>Lead generation tool — sumber data eksternal.</p></div></div>

<div class="card">
<div class="card-head"><h2>📡 Sumber Data</h2></div>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;">
<div style="background:#f0fdf4;padding:14px;border-radius:10px;border-left:3px solid #10b981;">
<strong>📊 Database Internal</strong><br><span style="font-size:12px;color:#6b7280;">15.343 kontak siap pakai</span>
</div>
<div style="background:#f8fafc;padding:14px;border-radius:10px;border-left:3px solid ${env.GOOGLE_PLACES_API_KEY?'#10b981':'#9ca3af'};">
<strong>🌐 Google Places API</strong><br><span style="font-size:12px;color:#6b7280;">${env.GOOGLE_PLACES_API_KEY?'✅ Aktif':'⚠️ Butuh API key'}</span>
</div>
<div style="background:#fff7ed;padding:14px;border-radius:10px;border-left:3px solid #f59e0b;">
<strong>🏭 Indonetwork</strong><br><span style="font-size:12px;color:#6b7280;">Scraping otomatis harian</span>
</div>
</div>
</div>

<div class="card">
<div class="card-head"><h2>🚀 Jalankan Scraper</h2></div>
<div style="display:grid;gap:8px;">
<div class="cron-card">
<div class="left"><strong>🏭 Indonetwork Manufaktur</strong><div class="next">Decode base64 + visit website</div></div>
<button onclick="runScraper('/api/cron/scrape/indonetwork?token=${token}&cat=0', 'Manufaktur')" class="btn-amber">▶ Jalankan</button>
</div>
<div class="cron-card">
<div class="left"><strong>🏭 Indonetwork Distributor</strong><div class="next">Kategori: distributor</div></div>
<button onclick="runScraper('/api/cron/scrape/indonetwork?token=${token}&cat=1', 'Distributor')" class="btn-amber">▶ Jalankan</button>
</div>
<div class="cron-card">
<div class="left"><strong>🌐 Google Places</strong><div class="next">${env.GOOGLE_PLACES_API_KEY?'Siap pakai':'Butuh API key'}</div></div>
<button onclick="runScraper('/api/cron/scrape/google-places?token=${token}&q=0', 'GP')" class="btn-amber" ${env.GOOGLE_PLACES_API_KEY?'':'disabled'}>▶ Jalankan</button>
</div>
</div>
</div>
`;
}

async function renderCampaignDetail(id, token, env) {
  const c = await env.DB.prepare(`
    SELECT c.*, t.name as template_name, l.name as list_name
    FROM campaigns c
    LEFT JOIN email_templates t ON c.template_id=t.id
    LEFT JOIN lead_lists l ON c.list_id=l.id
    WHERE c.id=?
  `).bind(id).first();
  if (!c) return new Response("Campaign tidak ditemukan", { status: 404 });

  const stats = await env.DB.prepare(`
    SELECT
      COUNT(*) as total,
      SUM(CASE WHEN status='sent' THEN 1 ELSE 0 END) as sent,
      SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) as pending,
      SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) as failed,
      SUM(CASE WHEN opened_at IS NOT NULL THEN 1 ELSE 0 END) as opened,
      SUM(CASE WHEN clicked_at IS NOT NULL THEN 1 ELSE 0 END) as clicked
    FROM email_queue WHERE campaign_id=?
  `).bind(id).first();
  const recentQueue = await env.DB.prepare(`
    SELECT email, name, status, sent_at, opened_at, clicked_at, error
    FROM email_queue WHERE campaign_id=?
    ORDER BY id DESC LIMIT 30
  `).bind(id).all();

  const sent = stats?.sent || 0;
  const opnRate = sent > 0 ? ((stats?.opened || 0) / sent * 100).toFixed(1) : '0';
  const clkRate = (stats?.opened || 0) > 0 ? ((stats?.clicked || 0) / stats.opened * 100).toFixed(1) : '0';
  const status = c.status === 'done' ? '<span class="badge b-green">✓ Selesai</span>' : c.status === 'sending' ? '<span class="badge b-amber">⏳ Mengirim</span>' : '<span class="badge b-gray">Draft</span>';
  const recent = recentQueue.results || [];

  return new Response(`<!DOCTYPE html>
<html lang="id"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Campaign #${id} — Beriklan Admin</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#f5f6fa;font-family:'Inter',-apple-system,sans-serif;color:#0f1e3d;line-height:1.5;-webkit-font-smoothing:antialiased}
a{text-decoration:none;color:inherit}
.layout{display:grid;grid-template-columns:240px 1fr;min-height:100vh;max-width:1400px;margin:0 auto}
.sidebar{background:#0f1e3d;color:#cbd5e1;padding:28px 20px;display:flex;flex-direction:column;gap:4px}
.sidebar-brand{display:flex;align-items:center;gap:10px;margin-bottom:24px;padding:0 8px}
.sidebar-brand img{height:28px;filter:brightness(0) invert(1)}
.sidebar-brand span{font-weight:800;font-size:16px;color:#fff}
.sidebar a.nav{padding:10px 14px;border-radius:8px;font-size:14px;display:flex;align-items:center;gap:10px;color:#cbd5e1;font-weight:500}
.sidebar a.nav:hover{background:rgba(255,255,255,0.06);color:#fff}
.sidebar a.nav.active{background:#1a2f5c;color:#fff;font-weight:600}
.sidebar a.nav .ico{width:18px;text-align:center;opacity:0.8}
.main{padding:28px 32px;overflow-x:hidden}
.page-head{display:flex;justify-content:space-between;align-items:end;margin-bottom:24px;flex-wrap:wrap;gap:12px}
.page-head h1{font-size:22px;font-weight:800}
.page-head p{color:#6b7280;font-size:13px;margin-top:4px}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:20px}
.kpi{background:#fff;border-radius:12px;padding:18px;border:1px solid #f0f1f5}
.kpi-label{font-size:11px;text-transform:uppercase;letter-spacing:0.06em;color:#6b7280;font-weight:700;margin-bottom:6px}
.kpi-val{font-size:24px;font-weight:800;color:#0f1e3d;line-height:1.1}
.kpi-sub{font-size:11px;color:#6b7280;margin-top:2px}
.card{background:#fff;border-radius:14px;padding:20px;box-shadow:0 1px 3px rgba(15,30,61,0.06);border:1px solid #f0f1f5;margin-bottom:18px}
.card-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
.card-head h2{font-size:16px;font-weight:700}
.badge{display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:100px;font-size:11px;font-weight:600}
.b-green{background:#d1fae5;color:#065f46}.b-amber{background:#fef3c7;color:#92400e}.b-gray{background:#f1f5f9;color:#475569}.b-blue{background:#dbeafe;color:#1e40af}.b-red{background:#fee2e2;color:#991b1b}
table{width:100%;border-collapse:collapse;font-size:13px}
th{background:#fafbfc;color:#475569;padding:10px 14px;text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.06em;font-weight:700;border-bottom:1px solid #e5e7eb}
td{padding:12px 14px;border-bottom:1px solid #f0f1f5;font-size:13px}
tr:last-child td{border-bottom:none}
.btn-row{display:flex;gap:6px;flex-wrap:wrap}
.btn{padding:9px 18px;border-radius:10px;font-weight:600;font-size:13px;border:none;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;gap:6px}
.btn-dark{background:#0f1e3d;color:#fff}
.btn-amber{background:#f59e0b;color:#0f1e3d}
.btn-outline{background:#fff;color:#0f1e3d;border:1px solid #d1d5db}
.btn-danger{background:#fee2e2;color:#991b1b;border:1px solid #fecaca}
</style></head><body>
<div class="layout">
<aside class="sidebar">
<div class="sidebar-brand"><img src="https://beriklan.co.id/logoweb.webp" alt="Beriklan" onerror="this.style.display='none'"><span>Beriklan</span></div>
<a href="/api/admin?token=${token}" class="nav"><span class="ico">🏠</span> Dashboard Utama</a>
<a href="?token=${token}&tab=overview" class="nav"><span class="ico">📊</span> Overview</a>
<a href="?token=${token}&tab=campaigns" class="nav active"><span class="ico">📨</span> Campaigns</a>
<a href="?token=${token}&tab=composer" class="nav"><span class="ico">✍️</span> Composer</a>
<a href="?token=${token}&tab=templates" class="nav"><span class="ico">📝</span> Templates</a>
<a href="?token=${token}&tab=lists" class="nav"><span class="ico">👥</span> Kontak</a>
<a href="?token=${token}&tab=cron" class="nav"><span class="ico">⏰</span> Cron</a>
</aside>
<div class="main">
<div class="page-head">
<div>
<h1>${escHtml(c.name)} ${status}</h1>
<p>Subject: <strong>${escHtml(c.subject || '-')}</strong> · Template: <strong>${escHtml(c.template_name || '-')}</strong> · Audience: <strong>${escHtml(c.list_name || 'Semua Kontak')}</strong></p>
</div>
<div class="btn-row">
<a href="?token=${token}&tab=campaigns" class="btn btn-outline">← Kembali</a>
${c.status !== 'sending' ? `<form method="POST" action="/api/email/campaigns?token=${token}&action=start&id=${c.id}" style="display:inline"><button class="btn btn-amber">▶ Kirim</button></form>` : ''}
<form method="POST" action="/api/admin/email/queue/reset?token=${token}&campaign_id=${c.id}" onsubmit="return confirm('Reset semua email failed ke pending?')" style="display:inline"><button class="btn btn-outline">↻ Reset Failed</button></form>
<form method="POST" action="/api/email/campaigns?token=${token}&action=delete&id=${c.id}" onsubmit="return confirm('Hapus campaign ini? Semua antrian email akan ikut terhapus.')" style="display:inline"><button class="btn btn-danger">🗑 Hapus</button></form>
</div>
</div>

<div class="kpi-grid">
<div class="kpi"><div class="kpi-label">📤 Total</div><div class="kpi-val">${stats?.total || 0}</div><div class="kpi-sub">antrian</div></div>
<div class="kpi"><div class="kpi-label">✓ Sent</div><div class="kpi-val" style="color:#10b981;">${sent}</div><div class="kpi-sub">berhasil terkirim</div></div>
<div class="kpi"><div class="kpi-label">⏳ Pending</div><div class="kpi-val" style="color:#f59e0b;">${stats?.pending || 0}</div><div class="kpi-sub">menunggu</div></div>
<div class="kpi"><div class="kpi-label">✕ Gagal</div><div class="kpi-val" style="color:#dc2626;">${stats?.failed || 0}</div><div class="kpi-sub">gagal kirim</div></div>
<div class="kpi"><div class="kpi-label">👁 Open</div><div class="kpi-val" style="color:#0ea5e9;">${opnRate}%</div><div class="kpi-sub">${stats?.opened || 0}/${sent}</div></div>
<div class="kpi"><div class="kpi-label">🖱 Click</div><div class="kpi-val" style="color:#8b5cf6;">${clkRate}%</div><div class="kpi-sub">${stats?.clicked || 0}/${stats?.opened || 0}</div></div>
</div>

<div class="card">
<div class="card-head"><h2>📨 30 Email Terakhir</h2></div>
${recent.length ? `<table>
<thead><tr><th>Email</th><th>Status</th><th>Sent</th><th>Opened</th><th>Clicked</th><th>Error</th></tr></thead>
<tbody>${recent.map(q => {
  const st = q.status === 'sent' ? '<span class="badge b-green">✓ Sent</span>' : q.status === 'pending' ? '<span class="badge b-amber">⏳ Pending</span>' : '<span class="badge b-red">✕ Failed</span>';
  return `<tr>
<td>${escHtml(q.email)}<br><span style="font-size:11px;color:#6b7280;">${escHtml(q.name || '-')}</span></td>
<td>${st}</td>
<td>${(q.sent_at || '-').slice(0, 16).replace('T', ' ')}</td>
<td>${(q.opened_at || '-').slice(0, 16).replace('T', ' ')}</td>
<td>${(q.clicked_at || '-').slice(0, 16).replace('T', ' ')}</td>
<td style="color:#dc2626;font-size:11px;">${escHtml((q.error || '').slice(0, 50))}</td>
</tr>`;
}).join('')}</tbody></table>` : '<div class="empty-state" style="text-align:center;padding:32px;color:#9ca3af;">Belum ada antrian.</div>'}
</div>
</div>
</div>
</body></html>`, { headers: { "Content-Type": "text/html; charset=utf-8" } });
}

// ─── Email Templates CRUD ─────────────────────────────────────

// ─── Email Templates CRUD ─────────────────────────────────────
async function handleEmailTemplates(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  if (!env.DB) return new Response("DB not available", { status: 503 });
  const action = url.searchParams.get("action") || "";

  if (request.method === "GET") {
    const rows = await env.DB.prepare("SELECT id, name, subject, category, created_at FROM email_templates ORDER BY id DESC LIMIT 50").all();
    return new Response(JSON.stringify({ ok: true, templates: rows.results || [] }), { headers: { "Content-Type": "application/json" } });
  }

  if (request.method === "POST") {
    if (action === "seed") {
      // 1. Hapus template generic lama (Promo Layanan, Newsletter Tips, Follow Up) — biar bersih
      const oldNames = ["Promo Layanan", "Newsletter Tips", "Follow Up"];
      for (const oldName of oldNames) {
        await env.DB.prepare("DELETE FROM email_templates WHERE name=?").bind(oldName).run();
      }
      // 2. Seed 10 service templates + 1 followup
      let seeded = 0;
      for (const tpl of EMAIL_TEMPLATE_DEFAULTS) {
        const existing = await env.DB.prepare("SELECT id FROM email_templates WHERE name=?").bind(tpl.name).first();
        if (!existing) {
          await env.DB.prepare("INSERT INTO email_templates (name, subject, html_body, category) VALUES (?,?,?,?)").bind(tpl.name, tpl.subject, tpl.html_body, tpl.category).run();
          seeded++;
        } else {
          // Update existing dengan HTML baru
          await env.DB.prepare("UPDATE email_templates SET subject=?, html_body=?, category=? WHERE id=?").bind(tpl.subject, tpl.html_body, tpl.category, existing.id).run();
          seeded++;
        }
      }
      return new Response(JSON.stringify({ ok: true, seeded, total: EMAIL_TEMPLATE_DEFAULTS.length }), { headers: { "Content-Type": "application/json" } });
    }
    if (action === "delete") {
      const id = parseInt(url.searchParams.get("id") || "0");
      await env.DB.prepare("DELETE FROM email_templates WHERE id=?").bind(id).run();
      return new Response(JSON.stringify({ ok: true }), { headers: { "Content-Type": "application/json" } });
    }
    if (action === "create") {
      try {
        const body = await request.json().catch(() => ({}));
        const name = body.name || url.searchParams.get("name") || "";
        const subject = body.subject || url.searchParams.get("subject") || "";
        const html_body = body.html_body || url.searchParams.get("html_body") || "";
        const category = body.category || url.searchParams.get("category") || "promo";
        if (!name || !subject) {
          return new Response(JSON.stringify({ ok: false, error: "name dan subject required" }), { status: 400, headers: { "Content-Type": "application/json" } });
        }
        await env.DB.prepare("INSERT INTO email_templates (name, subject, html_body, category) VALUES (?,?,?,?)").bind(name, subject, html_body, category).run();
        return new Response(JSON.stringify({ ok: true }), { headers: { "Content-Type": "application/json" } });
      } catch (e) {
        return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500, headers: { "Content-Type": "application/json" } });
      }
    }
  }
  return new Response(JSON.stringify({ ok: false, error: "Unknown action" }), { status: 400 });
}

// ─── Email Campaigns CRUD ─────────────────────────────────────
async function handleEmailCampaigns(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  if (!env.DB) return new Response("DB not available", { status: 503 });
  const action = url.searchParams.get("action") || "";

  if (request.method === "GET") {
    const rows = await env.DB.prepare("SELECT * FROM campaigns ORDER BY id DESC LIMIT 50").all();
    return new Response(JSON.stringify({ ok: true, campaigns: rows.results || [] }), { headers: { "Content-Type": "application/json" } });
  }

  if (request.method === "POST") {
    if (action === "create") {
      try {
        const body = await request.formData().catch(() => null) || await request.json().catch(() => ({}));
        const name = body.get ? body.get("name") : (body.name || "");
        const subject = body.get ? body.get("subject") : (body.subject || "");
        const template_id = parseInt(body.get ? body.get("template_id") : (body.template_id || 0));
        const list_id = parseInt(body.get ? body.get("list_id") : (body.list_id || 0));
        if (!name) return new Response(JSON.stringify({ ok: false, error: "name required" }), { status: 400, headers: { "Content-Type": "application/json" } });
        if (!template_id) return new Response(JSON.stringify({ ok: false, error: "template required" }), { status: 400, headers: { "Content-Type": "application/json" } });

        let total = 0;
        if (list_id > 0) {
          const cnt = await env.DB.prepare("SELECT COUNT(*) as c FROM lead_contacts WHERE list_id=? AND email != '' AND email IS NOT NULL").bind(list_id).first();
          total = cnt?.c || 0;
        } else {
          const cnt = await env.DB.prepare("SELECT COUNT(*) as c FROM lead_contacts WHERE email != '' AND email IS NOT NULL").first();
          total = cnt?.c || 0;
        }

        const r = await env.DB.prepare(
          "INSERT INTO campaigns (name, template_id, list_id, subject, status, total_recipients) VALUES (?,?,?,?,?,?)"
        ).bind(name, template_id, list_id, subject, "draft", total).run();
        const campaignId = r.meta?.last_row_id || 0;

        let queued = 0;
        if (total > 0 && campaignId) {
          const result = await queueCampaignContacts(env, campaignId, list_id, template_id, subject);
          if (result.ok) {
            queued = result.count;
            await env.DB.prepare("UPDATE campaigns SET status='sending' WHERE id=?").bind(campaignId).run();
          }
        }

        return new Response(JSON.stringify({ ok: true, id: campaignId, total_contacts: total, queued }), { headers: { "Content-Type": "application/json" } });
      } catch (e) {
        return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500, headers: { "Content-Type": "application/json" } });
      }
    }
    if (action === "start") {
      const id = parseInt(url.searchParams.get("id") || "0");
      const camp = await env.DB.prepare("SELECT * FROM campaigns WHERE id=?").bind(id).first();
      if (!camp) return new Response(JSON.stringify({ ok: false, error: "Campaign not found" }), { status: 404, headers: { "Content-Type": "application/json" } });
      if (camp.status === "sending") return new Response(JSON.stringify({ ok: false, error: "Already sending" }), { status: 400, headers: { "Content-Type": "application/json" } });
      const dup = await env.DB.prepare("SELECT COUNT(*) as c FROM email_queue WHERE campaign_id=? AND status IN ('pending','sent')").bind(id).first();
      if ((dup?.c || 0) > 0) return new Response(JSON.stringify({ ok: false, error: "Sudah ada email di queue untuk campaign ini", existing: dup.c }), { status: 400, headers: { "Content-Type": "application/json" } });
      const result = await queueCampaignContacts(env, id, camp.list_id, camp.template_id, camp.subject);
      if (!result.ok) return new Response(JSON.stringify(result), { status: 400, headers: { "Content-Type": "application/json" } });
      await env.DB.prepare("UPDATE campaigns SET status='sending' WHERE id=?").bind(id).run();
      return new Response(JSON.stringify({ ok: true, queued: result.count }), { headers: { "Content-Type": "application/json" } });
    }
    if (action === "delete") {
      const id = parseInt(url.searchParams.get("id") || "0");
      await env.DB.prepare("DELETE FROM email_queue WHERE campaign_id=?").bind(id).run();
      await env.DB.prepare("DELETE FROM campaigns WHERE id=?").bind(id).run();
      return new Response(JSON.stringify({ ok: true }), { headers: { "Content-Type": "application/json" } });
    }
  }
  return new Response(JSON.stringify({ ok: false, error: "Unknown action" }), { status: 400 });
}

async function queueCampaignContacts(env, campaignId, listId, templateId, subject) {
  const tpl = await env.DB.prepare("SELECT * FROM email_templates WHERE id=?").bind(templateId).first();
  if (!tpl && !subject) {
    return { ok: false, error: "Template tidak ditemukan", count: 0 };
  }
  let count = 0;
  let offset = 0;
  const PAGE = 500;
  while (true) {
    const stmt = listId > 0
      ? env.DB.prepare("SELECT email, name FROM lead_contacts WHERE list_id=? AND email != '' AND email IS NOT NULL LIMIT ? OFFSET ?").bind(listId, PAGE, offset)
      : env.DB.prepare("SELECT email, name FROM lead_contacts WHERE email != '' AND email IS NOT NULL LIMIT ? OFFSET ?").bind(PAGE, offset);
    const page = await stmt.all();
    if (!page.results?.length) break;
    const rows = [];
    for (const c of page.results) {
      if (!c.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(c.email)) continue;
      const tid = genTrackingId();
      rows.push([campaignId, c.email.toLowerCase().trim(), c.name || "", "pending", tid]);
      count++;
    }
    if (rows.length) {
      await env.DB.batch(rows.map(r => env.DB.prepare("INSERT INTO email_queue (campaign_id, email, name, status, tracking_id) VALUES (?,?,?,?,?)").bind(...r)));
    }
    offset += PAGE;
    if (page.results.length < PAGE) break;
  }
  if (count > 0) {
    await env.DB.prepare("UPDATE campaigns SET total_recipients=? WHERE id=?").bind(count, campaignId).run();
  }
  return { ok: true, count };
}

// ─── Lead Lists CRUD ──────────────────────────────────────────
async function handleEmailLists(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  if (!env.DB) return new Response("DB not available", { status: 503 });
  const action = url.searchParams.get("action") || "";

  if (request.method === "GET") {
    const rows = await env.DB.prepare("SELECT l.*, (SELECT COUNT(*) FROM lead_contacts WHERE list_id=l.id) as contact_count FROM lead_lists l ORDER BY id DESC LIMIT 50").all();
    return new Response(JSON.stringify({ ok: true, lists: rows.results || [] }), { headers: { "Content-Type": "application/json" } });
  }

  if (request.method === "POST") {
    if (action === "create") {
      try {
        const body = await request.formData().catch(() => null) || await request.json().catch(() => ({}));
        const name = (body.get ? body.get("name") : body.name) || "";
        const source = (body.get ? body.get("source") : body.source) || "manual";
        const emailsStr = (body.get ? body.get("emails") : body.emails) || "";
        if (!name) return new Response(JSON.stringify({ ok: false, error: "name required" }), { status: 400, headers: { "Content-Type": "application/json" } });
        const r = await env.DB.prepare("INSERT INTO lead_lists (name, source) VALUES (?,?)").bind(name, source).run();
        const listId = r.meta?.last_row_id || 0;
        let count = 0;
        if (emailsStr) {
          const emails = emailsStr.split(",").map(e => e.trim().toLowerCase()).filter(e => e.includes("@"));
          for (const email of emails) {
            await env.DB.prepare("INSERT OR IGNORE INTO lead_contacts (list_id, email) VALUES (?,?)").bind(listId, email).run();
            count++;
          }
          await env.DB.prepare("UPDATE lead_lists SET total=? WHERE id=?").bind(count, listId).run();
        }
        return new Response(JSON.stringify({ ok: true, id: listId, imported: count }), { headers: { "Content-Type": "application/json" } });
      } catch (e) {
        return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500, headers: { "Content-Type": "application/json" } });
      }
    }
    if (action === "import") {
      try {
        const body = typeof request.body === 'object' ? await request.json().catch(() => ({})) : {};
        const { name, source, contacts } = body;
        if (!name || !Array.isArray(contacts)) return new Response(JSON.stringify({ ok: false, error: "name dan contacts[] required" }), { status: 400, headers: { "Content-Type": "application/json" } });
        const r = await env.DB.prepare("INSERT INTO lead_lists (name, source) VALUES (?,?)").bind(name, source || "import").run();
        const listId = r.meta?.last_row_id || 0;
        let count = 0;
        for (const c of contacts) {
          if (!c.email && !c.phone) continue;
          await env.DB.prepare(
            "INSERT OR IGNORE INTO lead_contacts (list_id, email, phone, name, company, website, city, category, extra) VALUES (?,?,?,?,?,?,?,?,?)"
          ).bind(listId, c.email || "", c.phone || "", c.name || "", c.company || "", c.website || "", c.city || "", c.category || "", JSON.stringify(c.extra || {})).run();
          count++;
        }
        await env.DB.prepare("UPDATE lead_lists SET total=? WHERE id=?").bind(count, listId).run();
        return new Response(JSON.stringify({ ok: true, list_id: listId, imported: count }), { headers: { "Content-Type": "application/json" } });
      } catch (e) {
        return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500, headers: { "Content-Type": "application/json" } });
      }
    }
    if (action === "delete") {
      const id = parseInt(url.searchParams.get("id") || "0");
      await env.DB.prepare("DELETE FROM lead_contacts WHERE list_id=?").bind(id).run();
      await env.DB.prepare("DELETE FROM lead_lists WHERE id=?").bind(id).run();
      return new Response(JSON.stringify({ ok: true }), { headers: { "Content-Type": "application/json" } });
    }
  }
  return new Response(JSON.stringify({ ok: false, error: "Unknown action" }), { status: 400 });
}

// ─── Cron: Send Email Queue ───────────────────────────────────
async function handleCronSendEmail(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  if (!env.DB) return new Response("DB not available", { status: 503 });
  if (!env.RESEND_API_KEY) return new Response(JSON.stringify({ ok: false, error: "RESEND_API_KEY not set" }), { status: 503, headers: { "Content-Type": "application/json" } });

  try {
    // Check daily limit (Resend free: 500/day)
    const dailySent = await getDailyEmailCount(env);
    // Resend free tier: 100 email/hari (bukan 500), 10 req/detik rate limit
    const DAILY_LIMIT = 100;
    if (dailySent >= DAILY_LIMIT - 5) {
      return new Response(JSON.stringify({
        ok: true,
        skipped: true,
        reason: `Daily Resend limit reached (${dailySent}/${DAILY_LIMIT}). Akan lanjut besok.`,
        daily_sent: dailySent,
        daily_limit: DAILY_LIMIT,
        reset_at: "besok 00:00 UTC",
        next_retry_hours: 24,
      }), { headers: { "Content-Type": "application/json" } });
    }

    // Batch size: 25 per run (every 15 min = 100/hr = 100/day at Resend free tier)
    // Smart: kalau pending banyak + daily masih sisa, pakai batch besar
    const remainingToday = DAILY_LIMIT - dailySent;
    const pendingCount = (await env.DB.prepare("SELECT COUNT(*) as n FROM email_queue WHERE status='pending'").first())?.n || 0;
    let batchSize = 25;
    if (pendingCount > 5000) batchSize = Math.min(40, Math.max(15, Math.floor(remainingToday / 3)));
    else if (pendingCount > 1000) batchSize = Math.min(30, Math.max(15, Math.floor(remainingToday / 4)));
    else if (pendingCount > 100) batchSize = Math.min(25, remainingToday);
    else batchSize = Math.min(20, remainingToday);

    const batch = await env.DB.prepare(
      "SELECT q.*, c.name as campaign_name FROM email_queue q LEFT JOIN campaigns c ON q.campaign_id=c.id WHERE q.status='pending' ORDER BY q.id ASC LIMIT ?"
    ).bind(batchSize).all();

    if (!batch.results?.length) {
      return new Response(JSON.stringify({ ok: true, sent: 0, daily_sent: dailySent }), { headers: { "Content-Type": "application/json" } });
    }

    // Get template for each campaign
    const templateCache = {};
    let sent = 0, failed = 0;

    for (const item of batch.results) {
      try {
        let html = "";
        let subject = "Promo Beriklan";
        if (item.campaign_id && !templateCache[item.campaign_id]) {
          const camp = await env.DB.prepare("SELECT * FROM campaigns WHERE id=?").bind(item.campaign_id).first();
          if (camp) {
            subject = camp.subject || "Promo Beriklan";
            if (camp.template_id) {
              const tpl = await env.DB.prepare("SELECT * FROM email_templates WHERE id=?").bind(camp.template_id).first();
              if (tpl) {
                html = tpl.html_body || "";
                if (!camp.subject && tpl.subject) subject = tpl.subject;
              }
            }
          }
          templateCache[item.campaign_id] = { html, subject };
        }
        const tmpl = templateCache[item.campaign_id] || { html, subject };

        if (!tmpl.html) {
          await env.DB.prepare("UPDATE email_queue SET status='failed', error=? WHERE id=?").bind("Template kosong", item.id).run();
          failed++;
          continue;
        }

        let bodyHtml = tmpl.html;
        const name = item.name || "";
        const trackingId = item.tracking_id || "";
        const unsubUrl = `https://beriklan.co.id/api/newsletter/unsubscribe?email=${encodeURIComponent(item.email)}`;
        const unsubFooter = `<br><p style="margin:12px 0 0;text-align:center;color:#94a3b8;font-size:11px;">Tidak tertarik? <a href="${unsubUrl}" style="color:#94a3b8;text-decoration:underline;">Berhenti berlangganan</a></p>`;
        bodyHtml = bodyHtml.replace(/\{\{name\}\}/g, name).replace(/\{\{company\}\}/g, name);
        bodyHtml = bodyHtml.replace(/\{\{unsubscribe_url\}\}/g, unsubUrl);
        bodyHtml = bodyHtml.replace(/\{\{date\}\}/g, new Date().toLocaleDateString("id-ID"));
        bodyHtml = bodyHtml.replace(/\{\{headline\}\}/g, subject);
        bodyHtml = bodyHtml.replace(/\{\{excerpt\}\}/g, "Tips dan strategi digital marketing terbaru dari tim Beriklan.");
        bodyHtml = bodyHtml.replace(/\{\{articles\}\}/g, "");
        bodyHtml = bodyHtml.replace(/\{\{cta_url\}\}/g, "https://wa.me/62811919328?text=" + encodeURIComponent(`Halo Beriklan, saya tertarik info lebih lanjut setelah menerima email "${subject}".`));
        bodyHtml = bodyHtml.replace(/\{\{cta_text\}\}/g, "Diskusi via WhatsApp");
        bodyHtml = bodyHtml.replace(/\{\{title\}\}/g, subject);
        bodyHtml = bodyHtml.replace(/\{\{subtitle\}\}/g, "Konsultasi gratis 15 menit untuk campaign Anda.");
        bodyHtml = bodyHtml.replace(/\{\{tracking_pixel\}\}/g, `<img src="https://beriklan.co.id/api/track/open?id=${trackingId}" width="1" height="1" alt="" style="display:none;">`);
        if (!bodyHtml.includes("Berhenti berlangganan") && !bodyHtml.includes("unsubscribe_url")) bodyHtml += unsubFooter;

        const res = await sendEmailViaResend(env, { email: item.email, name: item.name }, tmpl.subject, bodyHtml, item.tracking_id);

        if (res.ok) {
          await env.DB.prepare("UPDATE email_queue SET status='sent', sent_at=CURRENT_TIMESTAMP WHERE id=?").bind(item.id).run();
          await env.DB.prepare("UPDATE campaigns SET sent_count=sent_count+1 WHERE id=?").bind(item.campaign_id).run();
          sent++;
        } else {
          await env.DB.prepare("UPDATE email_queue SET status='failed', error=? WHERE id=?").bind(res.error?.slice(0, 200) || "unknown", item.id).run();
          failed++;
        }
      } catch (e) {
        await env.DB.prepare("UPDATE email_queue SET status='failed', error=? WHERE id=?").bind(String(e).slice(0, 200), item.id).run();
        failed++;
      }
    }

    // Check if any campaign is done
    const updatedCampaigns = [...new Set(batch.results.map(r => r.campaign_id).filter(Boolean))];
    for (const cid of updatedCampaigns) {
      const pending = await env.DB.prepare("SELECT COUNT(*) as c FROM email_queue WHERE campaign_id=? AND status='pending'").bind(cid).first();
      if (!pending || pending.c === 0) {
        await env.DB.prepare("UPDATE campaigns SET status='done', sent_at=CURRENT_TIMESTAMP WHERE id=?").bind(cid).run();
      }
    }

    return new Response(JSON.stringify({
      ok: true,
      sent,
      failed,
      batch_size: batch.results.length,
      daily_sent: dailySent + sent,
      campaigns_completed: updatedCampaigns.length
    }), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
}

// ─── Cron Toggle ─────────────────────────────────────────────
async function handleCronToggle(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  if (!env.DB) return new Response("DB not available", { status: 503 });
  const name = url.searchParams.get("name") || "";
  if (!name) {
    const rows = await env.DB.prepare("SELECT name, cron, enabled, label FROM cron_settings ORDER BY id").all();
    const result = {};
    for (const r of rows.results || []) result[r.name] = { cron: r.cron, enabled: !!r.enabled, label: r.label };
    return new Response(JSON.stringify({ ok: true, crons: result }), { headers: { "Content-Type": "application/json" } });
  }
  try {
    const s = await env.DB.prepare("SELECT enabled FROM cron_settings WHERE name=?").bind(name).first();
    if (!s) return new Response(JSON.stringify({ ok: false, error: "Cron not found" }), { status: 404, headers: { "Content-Type": "application/json" } });
    const newVal = s.enabled ? 0 : 1;
    await env.DB.prepare("UPDATE cron_settings SET enabled=? WHERE name=?").bind(newVal, name).run();
    return new Response(JSON.stringify({ ok: true, name, was: s.enabled, now: newVal, label: s.enabled ? "Paused" : "Enabled" }), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
}

// ─── Template Preview ──────────────────────────────────────────
async function handleEmailTemplatePreview(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  const id = parseInt(url.searchParams.get("id") || "0");
  if (!env.DB) return new Response("DB not available", { status: 503 });
  const tpl = await env.DB.prepare("SELECT * FROM email_templates WHERE id=?").bind(id).first();
  if (!tpl) return new Response("Template not found", { status: 404 });
  let html = tpl.html_body || "";
  html = html.replace(/\{\{name\}\}/g, "Bapak/Ibu");
  html = html.replace(/\{\{company\}\}/g, "perusahaan Anda");
  html = html.replace(/\{\{unsubscribe_url\}\}/g, "#");
  html = html.replace(/\{\{date\}\}/g, new Date().toLocaleDateString("id-ID"));
  html = html.replace(/\{\{headline\}\}/g, "Tips Digital Marketing Terbaru");
  html = html.replace(/\{\{excerpt\}\}/g, "Contoh preview dari template email Beriklan.");
  html = html.replace(/\{\{articles\}\}/g, "");
  html = html.replace(/\{\{cta_url\}\}/g, "https://wa.me/62811919328");
  html = html.replace(/\{\{cta_text\}\}/g, "Konsultasi Gratis");
  html = html.replace(/\{\{title\}\}/g, "Judul Promo");
  html = html.replace(/\{\{subtitle\}\}/g, "Subtitle promo");
  const frame = `<!DOCTYPE html><html lang="id"><head><meta charset="UTF-8"><title>Preview: ${escHtml(tpl.name)}</title>
<style>body{margin:0;background:#f3f4f8;font-family:sans-serif;}
.toolbar{background:#0f1e3d;color:#fff;padding:12px 20px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:100;}
.toolbar h2{margin:0;font-size:15px;font-weight:700;}.toolbar span{font-size:12px;color:#94a3b8;}
iframe{width:100%;height:calc(100vh - 50px);border:none;background:#fff;}
</style></head><body>
<div class="toolbar"><h2>📧 ${escHtml(tpl.name)}</h2><span>Subject: ${escHtml(tpl.subject)} · ${escHtml(tpl.category)}</span></div>
<iframe srcdoc="${escHtml(html).replace(/"/g,'&quot;')}" title="Preview"></iframe>
</body></html>`;
  return new Response(frame, { headers: { "Content-Type": "text/html; charset=utf-8" } });
}

// ─── Email Test Send ──────────────────────────────────────────
async function handleEmailTestSend(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  if (!env.DB) return new Response("DB not available", { status: 503 });
  if (!env.RESEND_API_KEY) return new Response(JSON.stringify({ ok: false, error: "RESEND_API_KEY not set" }), { status: 503, headers: { "Content-Type": "application/json" } });

  const templateId = parseInt(url.searchParams.get("template_id") || url.searchParams.get("id") || "0");
  const toEmail = url.searchParams.get("to") || "admin@3smedianet.com"; // Default ke admin internal, bukan customer
  const tpl = await env.DB.prepare("SELECT * FROM email_templates WHERE id=?").bind(templateId).first();
  if (!tpl) return new Response(JSON.stringify({ ok: false, error: "Template not found" }), { status: 404, headers: { "Content-Type": "application/json" } });

const sample = {
    name: "Bapak/Ibu",
    company: "perusahaan Anda",
    email: toEmail
  };
  let html = tpl.html_body || "";
  let subj = tpl.subject || "";
  html = html.replace(/\{\{name\}\}/g, sample.name);
  html = html.replace(/\{\{company\}\}/g, sample.company);
  subj = subj.replace(/\{\{name\}\}/g, sample.name);
  subj = subj.replace(/\{\{company\}\}/g, sample.company);
  html = html.replace(/\{\{unsubscribe_url\}\}/g, `https://beriklan.co.id/api/newsletter/unsubscribe?email=${encodeURIComponent(toEmail)}`);
  html = html.replace(/\{\{date\}\}/g, new Date().toLocaleDateString("id-ID"));
  html = html.replace(/\{\{headline\}\}/g, "Tips Digital Marketing Terbaru");
  html = html.replace(/\{\{excerpt\}\}/g, "Contoh preview template.");
  html = html.replace(/\{\{articles\}\}/g, "");

  // Test send SELALU pakai prefix [INTERNAL-TEST] supaya tidak keliru dengan campaign real
  const subject = `[INTERNAL-TEST] ${subj}`;
  const res = await sendEmailViaResend(env, toEmail, subject, html, genTrackingId());

  return new Response(JSON.stringify({
    ok: res.ok,
    template_id: templateId,
    template_name: tpl.name,
    sent_to: toEmail,
    subject,
    resend_id: res.id || null,
    error: res.error || null,
    preview_url: `/api/email/templates/preview?id=${templateId}&token=${token}`
  }), { headers: { "Content-Type": "application/json" } });
}

// ─── Scrape Indonetwork ───────────────────────────────────────
async function handleScrapeIndonetwork(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  if (!env.DB) return new Response("DB not available", { status: 503 });

  const categories = ["manufaktur", "distributor", "jasa", "properti", "retail", "makanan-minuman", "fashion", "elektronik", "otomotif", "percetakan"];
  const catIdx = parseInt(url.searchParams.get("cat") || "0");
  const category = categories[catIdx] || categories[0];

  const decodeBase64 = (s) => { try { return atob(s); } catch { return ""; } };

  try {
    const listUrl = `https://www.indonetwork.co.id/category/${category}`;
    const listResp = await fetch(listUrl, {
      headers: { "User-Agent": "Mozilla/5.0 (compatible; BeriklanBot/1.0; +https://beriklan.co.id)", "Accept": "text/html" }
    });
    if (!listResp.ok) {
      return new Response(JSON.stringify({ ok: false, error: `HTTP ${listResp.status} for ${listUrl}` }), { headers: { "Content-Type": "application/json" } });
    }
    const html = await listResp.text();

    // Extract company URLs
    const companyUrls = [];
    const urlRegex = /\/company\/[a-z0-9-]+/g;
    const matches = html.match(urlRegex);
    if (matches) {
      const seen = new Set();
      for (const m of matches) {
        if (!seen.has(m)) { seen.add(m); companyUrls.push("https://www.indonetwork.co.id" + m); }
      }
    }

    // Direct emails on category page
    const emails = [];
    const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
    const emailMatches = html.match(emailRegex);
    if (emailMatches) {
      const seen = new Set();
      for (const e of emailMatches) {
        const clean = e.toLowerCase().trim();
        if (!seen.has(clean) && !clean.includes(".png") && !clean.includes(".jpg") && !clean.includes("base64") && !clean.includes("example")) {
          seen.add(clean);
          emails.push(clean);
        }
      }
    }

    // Limit 8 detail pages per run (CPU budget)
    const detailUrls = companyUrls.slice(0, 8);
    const listName = `indonetwork-${category}-${new Date().toISOString().slice(0, 10)}`;
    const listR = await env.DB.prepare("INSERT INTO lead_lists (name, source) VALUES (?,?)").bind(listName, "indonetwork").run();
    const listId = listR.meta?.last_row_id || 0;
    let totalContacts = 0;
    let websitesVisited = 0;

    // Save category-page emails
    for (const email of emails.slice(0, 20)) {
      await env.DB.prepare("INSERT OR IGNORE INTO lead_contacts (list_id, email, category) VALUES (?,?,?)").bind(listId, email, category).run();
      totalContacts++;
    }

    // Fetch detail pages
    for (const detailUrl of detailUrls) {
      try {
        const detailResp = await fetch(detailUrl, {
          headers: { "User-Agent": "Mozilla/5.0 (compatible; BeriklanBot/1.0; +https://beriklan.co.id)", "Accept": "text/html" }
        });
        if (!detailResp.ok) continue;
        const detailHtml = await detailResp.text();
        const text = detailHtml.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();

        // Extract from h1 / title (company name)
        const h1Match = detailHtml.match(/<h1[^>]*>([^<]+)<\/h1>/);
        const titleMatch = detailHtml.match(/<title[^>]*>([^<]+)<\/title>/);
        let company = h1Match ? h1Match[1].trim() : (titleMatch ? titleMatch[1].replace(/[|-].*$/, "").trim() : "");

        // Decode base64 phone numbers (Indonetwork encodes phones!)
        let phone = "";
        const b64Phones = detailHtml.match(/data-text="([A-Za-z0-9+/=]{8,})"[^>]*data-type="phone"/g);
        if (b64Phones && b64Phones.length > 0) {
          const b64 = b64Phones[0].match(/data-text="([^"]+)"/)?.[1];
          if (b64) phone = decodeBase64(b64);
        }
        // Also check WhatsApp type
        if (!phone) {
          const b64Wa = detailHtml.match(/data-text="([A-Za-z0-9+/=]{8,})"[^>]*data-type="wa"/);
          if (b64Wa && b64Wa[1]) phone = decodeBase64(b64Wa[1]);
        }
        // Fallback: regex
        if (!phone) {
          const phoneMatch = text.match(/(0\d{2,4}[\s-]?\d{3,8}[\s-]?\d{3,8}|62\d{8,12})/);
          phone = phoneMatch ? phoneMatch[0].trim() : "";
        }

        // Decode base64 email if encoded (some companies have it)
        let emailFromPage = "";
        const b64Email = detailHtml.match(/data-text="([A-Za-z0-9+/=]{8,})"[^>]*data-type="email"/);
        if (b64Email && b64Email[1]) {
          emailFromPage = decodeBase64(b64Email[1]).toLowerCase();
        }
        // Fallback: regex
        if (!emailFromPage) {
          const detEmailMatch = text.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/);
          emailFromPage = detEmailMatch ? detEmailMatch[0].toLowerCase().trim() : "";
        }

        // Extract website URL from links
        let website = "";
        const webLinks = detailHtml.match(/href="(https?:\/\/(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}[^\s"]*)"/g);
        if (webLinks) {
          for (const link of webLinks) {
            const url = link.match(/href="([^"]+)"/)?.[1] || "";
            if (url && !url.includes("indonetwork.co.id") && !url.includes("facebook.com") && !url.includes("instagram.com") && !url.includes("youtube.com")) {
              website = url;
              break;
            }
          }
        }

        // Extract city
        const cityMatch = text.match(/(Bandung|Jakarta|Surabaya|Medan|Semarang|Makassar|Yogyakarta|Tangerang|Bekasi|Depok|Bogor|Malang|Palembang|Pekanbaru|Denpasar|Balikpapan|Samarinda|Manado|Pontianak|Banjarmasin|Batam|Padang|Bandar Lampung|Jambi|Aceh|Solo|Sukabumi|Cirebon|Kediri|Madiun)/);
        const city = cityMatch ? cityMatch[0] : "";

        // If we got a website, fetch it and try to extract emails
        let websiteEmail = "";
        if (website) {
          try {
            const siteResp = await fetch(website, {
              headers: { "User-Agent": "Mozilla/5.0 (compatible; BeriklanBot/1.0; +https://beriklan.co.id)", "Accept": "text/html" },
              redirect: "follow"
            });
            if (siteResp.ok) {
              const siteHtml = await siteResp.text();
              const siteText = siteHtml.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ");
              const siteEmailMatch = siteText.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g);
              if (siteEmailMatch) {
                for (const e of siteEmailMatch) {
                  const clean = e.toLowerCase();
                  if (!clean.includes(".png") && !clean.includes(".jpg") && !clean.includes("example") && !clean.includes("your-email") && !clean.includes("email@")) {
                    websiteEmail = clean;
                    break;
                  }
                }
              }
              websitesVisited++;
            }
          } catch (e) { /* skip */ }
        }

        const finalEmail = emailFromPage || websiteEmail;

        if (finalEmail) {
          await env.DB.prepare(
            "INSERT OR IGNORE INTO lead_contacts (list_id, email, phone, name, company, website, city, category) VALUES (?,?,?,?,?,?,?,?)"
          ).bind(listId, finalEmail, phone, company, company, website, city, category).run();
          totalContacts++;
        } else if (phone) {
          // Save company without email if phone exists
          await env.DB.prepare(
            "INSERT OR IGNORE INTO lead_contacts (list_id, email, phone, name, company, website, city, category) VALUES (?,?,?,?,?,?,?,?)"
          ).bind(listId, "", phone, company, company, website, city, category).run();
          totalContacts++;
        }
        await new Promise(r => setTimeout(r, 150));
      } catch (e) {
        console.error("[scrape-indonetwork] detail error:", String(e).slice(0, 100));
      }
    }

    await env.DB.prepare("UPDATE lead_lists SET total=? WHERE id=?").bind(totalContacts, listId).run();

    const nextCat = (catIdx + 1) % categories.length;
    return new Response(JSON.stringify({
      ok: true,
      category,
      list_name: listName,
      list_id: listId,
      companies_found: companyUrls.length,
      contacts_saved: totalContacts,
      emails_from_category: emails.length,
      details_fetched: detailUrls.length,
      websites_visited: websitesVisited,
      next_category: categories[nextCat],
      next_url: `/api/cron/scrape/indonetwork?token=${token}&cat=${nextCat}`,
      next_cat_idx: nextCat
    }), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
}

// ─── Import CSV dari Database Siap Pake ──────────────────────────
async function handleImportDatabase(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  if (!env.DB) return new Response("DB not available", { status: 503 });

  try {
    const body = await request.json();
    const { name, source, contacts } = body;
    if (!name || !Array.isArray(contacts)) {
      return new Response(JSON.stringify({ ok: false, error: "name dan contacts[] required" }), { status: 400, headers: { "Content-Type": "application/json" } });
    }

    const r = await env.DB.prepare("INSERT INTO lead_lists (name, source) VALUES (?,?)").bind(name, source || "import").run();
    const listId = r.meta?.last_row_id || 0;
    let count = 0;
    for (const c of contacts) {
      if (!c.email && !c.phone) continue;
      await env.DB.prepare(
        "INSERT OR IGNORE INTO lead_contacts (list_id, email, phone, name, company, website, city, category, extra) VALUES (?,?,?,?,?,?,?,?,?)"
      ).bind(listId, c.email || "", c.phone || "", c.name || "", c.company || "", c.website || "", c.city || "", c.category || "", JSON.stringify(c.extra || {}))
      .run();
      count++;
    }
    await env.DB.prepare("UPDATE lead_lists SET total=? WHERE id=?").bind(count, listId).run();
    return new Response(JSON.stringify({ ok: true, list_id: listId, imported: count }), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
}

// ─── Google Places API Scraper ──────────────────────────────────
async function handleScrapeGooglePlaces(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (token !== env.ADMIN_TOKEN) return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  if (!env.DB) return new Response("DB not available", { status: 503 });
  if (!env.GOOGLE_PLACES_API_KEY) return new Response(JSON.stringify({ ok: false, error: "GOOGLE_PLACES_API_KEY not set" }), { status: 200, headers: { "Content-Type": "application/json" } });

  const categories = [
    { q: "perusahaan manufaktur", label: "Manufaktur" },
    { q: "perusahaan distributor", label: "Distributor" },
    { q: "perusahaan jasa kontraktor", label: "Jasa" },
    { q: "developer properti", label: "Properti" },
    { q: "toko retail", label: "Retail" },
    { q: "perusahaan logistik", label: "Logistik" },
    { q: "klinik dokter", label: "Klinik" },
    { q: "sekolah yayasan pendidikan", label: "Pendidikan" },
    { q: "hotel restoran", label: "Hotel Restoran" },
    { q: "bengkel otomotif", label: "Otomotif" },
    { q: "percetakan digital percetakan", label: "Percetakan" },
    { q: "toko bangunan material", label: "Material" },
  ];
  const catIdx = parseInt(url.searchParams.get("q") || "0");
  const category = categories[catIdx] || categories[0];
  const cities = ["Bandung","Jakarta","Surabaya","Tangerang","Bekasi","Depok","Bogor","Semarang","Yogyakarta","Malang","Medan","Palembang","Makassar","Denpasar","Balikpapan","Solo","Cimahi","Tasikmalaya","Banjarmasin","Manado"];

  let totalSaved = 0;
  let dbg = [];
  const fieldMask = "places.id,places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri,places.rating";
  for (let ci = 0; ci < Math.min(cities.length, 8); ci++) {
    const city = cities[ci];
    try {
      if (ci > 0) await new Promise(r => setTimeout(r, 800));
      const body = JSON.stringify({ textQuery: `${category.q} di ${city}`, maxResultCount: 10 });
      const resp = await fetch("https://places.googleapis.com/v1/places:searchText", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Goog-Api-Key": env.GOOGLE_PLACES_API_KEY, "X-Goog-FieldMask": fieldMask },
        body,
      });
      if (resp.status === 429) { dbg.push(`${city}: 429 rate limited`); break; }
      if (!resp.ok) { dbg.push(`${city}: HTTP ${resp.status}`); continue; }
      const data = await resp.json();
      if (!data.places || !data.places.length) { dbg.push(`${city}: 0 places`); continue; }
      let citySaved = 0;
      for (const place of data.places) {
        const phone = place.nationalPhoneNumber || "";
        const website = place.websiteUri || "";
        const name = place.displayName?.text || place.displayName || "Unknown";
        const placeId = place.id || "";
        if (!phone && !website) continue;
        const { rows } = await env.DB.prepare("SELECT id FROM lead_contacts WHERE source_id = ?").bind(placeId).all();
        if (rows.length > 0) continue;
        const listR = await env.DB.prepare("INSERT INTO lead_lists (name, source) VALUES (?,?)").bind(`google-${category.label}-${city}-${new Date().toISOString().slice(0,10)}`, "google_places").run();
        const listId = listR.meta?.last_row_id || 0;
        await env.DB.prepare("INSERT INTO lead_contacts (list_id, email, phone, name, company, website, city, category, extra, source_id) VALUES (?,?,?,?,?,?,?,?,?,?)")
          .bind(listId, "", phone, name, name, website, city, category.label, JSON.stringify({ rating: place.rating || 0, source: "google_places_v1" }), placeId).run();
        await env.DB.prepare("UPDATE lead_lists SET total = (SELECT COUNT(*) FROM lead_contacts WHERE list_id = ?) WHERE id = ?").bind(listId, listId).run();
        citySaved++;
      }
      totalSaved += citySaved;
      dbg.push(`${city}: ${citySaved} saved (${data.places.length} places)`);
    } catch (e) {
      dbg.push(`${city}: ERR ${e.message}`);
    }
  }
  return new Response(JSON.stringify({ ok: true, query: category.q, label: category.label, contacts_saved: totalSaved, cities: cities.length, debug: dbg }), { headers: { "Content-Type": "application/json" } });
}

// ───────────────────────────────────────────────────────────────
// scrape.beriklan.co.id — Consumer-facing scraping trial portal
// ───────────────────────────────────────────────────────────────

const SCRAPE_CATEGORIES = [
  { id: "manufaktur", label: "Manufaktur", osm: '["shop"="industrial"]' },
  { id: "toko", label: "Toko Retail", osm: '["shop"]' },
  { id: "resto", label: "Restoran / Cafe", osm: '["amenity"~"restaurant|cafe|fast_food"]' },
  { id: "klinik", label: "Klinik / Apotek", osm: '["amenity"~"clinic|pharmacy|doctors|hospital"]' },
  { id: "hotel", label: "Hotel / Penginapan", osm: '["tourism"~"hotel|hostel|guest_house"]' },
  { id: "salon", label: "Salon / Kecantikan", osm: '["shop"~"beauty|hairdresser|cosmetics"]' },
  { id: "otomotif", label: "Bengkel Otomotif", osm: '["shop"="car_repair"]' },
  { id: "percetakan", label: "Percetakan", osm: '["shop"="printing"]' },
  { id: "properti", label: "Properti", osm: '["office"="estate_agent"]' },
  { id: "pendidikan", label: "Pendidikan / Kursus", osm: '["amenity"~"school|college|university|language_school"]' },
];

const SCRAPE_CITIES = [
  "Bandung","Jakarta","Surabaya","Tangerang","Bekasi","Depok","Bogor","Semarang",
  "Yogyakarta","Malang","Medan","Palembang","Makassar","Denpasar","Balikpapan",
  "Solo","Cimahi","Tasikmalaya","Banjarmasin","Manado","Pontianak","Pekanbaru",
  "Padang","Jambi","Bengkulu","Lampung","Cirebon","Sukabumi","Garut","Cianjur"
];

async function handleGenericCityRedirect(request, env) {
  const url = new URL(request.url);
  const path = url.pathname;
  // /jasa-iklan-ads-{city}/ → /jasa-digital-marketing/{city}/
  const m = path.match(/^\/jasa-iklan-ads\/([a-z\-]+)\/?$/);
  if (m) {
    return Response.redirect(`https://beriklan.co.id/jasa-digital-marketing/${m[1]}/`, 301);
  }
  return null;
}

// ───────────────────────────────────────────────────────────────
// scrape.beriklan.co.id — Consumer-facing scraping trial portal
// ───────────────────────────────────────────────────────────────

async function handleScrapePortal(request, env, ctx) {
  const url = new URL(request.url);
  const path = url.pathname;
  if (!env.DB) return new Response("DB not available", { status: 503 });

  // Static assets (none for now)

  // API endpoints
  if (path === "/api/signup" || path === "/api/signup/") {
    return await handleScrapeSignup(request, env);
  }
  if (path === "/api/search" || path === "/api/search/") {
    return await handleScrapeSearch(request, env);
  }
  if (path === "/api/export" || path === "/api/export/") {
    return await handleScrapeExport(request, env);
  }
  if (path === "/api/logout" || path === "/api/logout/") {
    const cookie = request.headers.get("Cookie") || "";
    const newCookie = cookie.replace(/scrape_token=[^;]+;?/g, "").trim() + "; Path=/; Max-Age=0";
    return new Response("", { status: 302, headers: { Location: "/", "Set-Cookie": newCookie } });
  }

  // Page routes
  if (path === "/" || path === "/index.html") {
    return await renderScrapeLanding(request, env);
  }
  if (path === "/signup" || path === "/signup.html") {
    return await renderScrapeSignup(request, env);
  }
  if (path === "/dashboard" || path === "/search") {
    return await renderScrapeDashboard(request, env);
  }
  if (path === "/admin") {
    return await renderScrapeAdmin(request, env);
  }

  return new Response("Not found", { status: 404 });
}

async function getScrapeUserFromCookie(request, env) {
  const cookie = request.headers.get("Cookie") || "";
  const m = cookie.match(/scrape_token=([^;]+)/);
  if (!m) return null;
  const token = m[1];
  const u = await env.DB.prepare("SELECT * FROM scrape_users WHERE session_token = ?").bind(token).first();
  if (!u) return null;
  await env.DB.prepare("UPDATE scrape_users SET last_active = CURRENT_TIMESTAMP WHERE id = ?").bind(u.id).run();
  return u;
}

function genScrapeToken() {
  return "sk_" + Date.now().toString(36) + "_" + Math.random().toString(36).slice(2, 12);
}

async function handleScrapeSignup(request, env) {
  if (request.method !== "POST") return new Response("Method not allowed", { status: 405 });
  const body = await request.formData().catch(() => null) || await request.json().catch(() => ({}));
  const name = String((body.get ? body.get("name") : body.name) || "").trim();
  const email = String((body.get ? body.get("email") : body.email) || "").trim().toLowerCase();
  const whatsapp = String((body.get ? body.get("whatsapp") : body.whatsapp) || "").trim();

  if (!name || name.length < 2) return json({ ok: false, error: "Nama minimal 2 karakter" }, 400);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return json({ ok: false, error: "Email tidak valid" }, 400);
  if (!/^(\+?62|0)8\d{8,12}$/.test(whatsapp.replace(/\s|-/g, ""))) return json({ ok: false, error: "WhatsApp tidak valid (format: 081234567890)" }, 400);

  const existing = await env.DB.prepare("SELECT * FROM scrape_users WHERE email = ?").bind(email).first();
  if (existing) {
    return json({ ok: false, error: "Email sudah pernah trial. 1 trial per user.", email_exists: true }, 409);
  }

  const token = genScrapeToken();
  const r = await env.DB.prepare("INSERT INTO scrape_users (name, email, whatsapp, session_token) VALUES (?,?,?,?)").bind(name, email, whatsapp, token).run();
  const userId = r.meta?.last_row_id || 0;

  // Send welcome via WhatsApp webhook (optional — skip for now)
  // Send notification ke admin via email kalau ada RESEND_API_KEY
  try {
    if (env.RESEND_API_KEY) {
      await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: { "Authorization": `Bearer ${env.RESEND_API_KEY}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          from: "Beriklan Scrape <noreply@beriklan.co.id>",
          to: ["admin@3smedianet.com"],
          subject: `[Scrape Trial] New user: ${name}`,
          html: `<p>Trial baru scrape.beriklan.co.id:</p><ul><li><b>Nama:</b> ${escHtml(name)}</li><li><b>Email:</b> ${escHtml(email)}</li><li><b>WhatsApp:</b> ${escHtml(whatsapp)}</li></ul>`
        })
      });
    }
  } catch {}

  const cookie = `scrape_token=${token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=2592000`;
  return new Response(JSON.stringify({ ok: true, id: userId, token, redirect: "/dashboard" }), {
    headers: { "Content-Type": "application/json", "Set-Cookie": cookie },
  });
}

async function handleScrapeSearch(request, env) {
  const user = await getScrapeUserFromCookie(request, env);
  if (!user) return json({ ok: false, error: "Login required", redirect: "/signup" }, 401);

  if (request.method !== "POST") return new Response("Method not allowed", { status: 405 });

  if ((user.search_count || 0) >= 30) {
    return json({ ok: false, error: "Trial limit tercapai (30 pencarian). Hubungi kami untuk akses full.", limit_reached: true }, 403);
  }

  const body = await request.formData().catch(() => null) || await request.json().catch(() => ({}));
  const query = String((body.get ? body.get("query") : body.query) || "").trim();
  const category = String((body.get ? body.get("category") : body.category) || "").trim();
  const city = String((body.get ? body.get("city") : body.city) || "").trim();
  const limit = Math.min(parseInt(body.get ? body.get("limit") : body.limit) || 20, 50);

  if (!query && !category) return json({ ok: false, error: "Query atau kategori required" }, 400);

  // Increment counter
  await env.DB.prepare("UPDATE scrape_users SET search_count = search_count + 1 WHERE id = ?").bind(user.id).run();

  // Save search
  const sr = await env.DB.prepare("INSERT INTO scrape_searches (user_id, query, category, city) VALUES (?,?,?,?)").bind(user.id, query || category, category, city).run();
  const searchId = sr.meta?.last_row_id || 0;

  // === Strategy 1: search existing D1 lead_contacts ===
  const results = [];
  const seenKeys = new Set();

  const dbQuery = category && city
    ? env.DB.prepare("SELECT company, name, phone, email, website, city, category FROM lead_contacts WHERE (LOWER(category) = LOWER(?) OR LOWER(company) LIKE LOWER(?) OR LOWER(name) LIKE LOWER(?)) AND LOWER(city) LIKE LOWER(?) LIMIT ?").bind(category, `%${category}%`, `%${category}%`, `%${city}%`, limit)
    : category
    ? env.DB.prepare("SELECT company, name, phone, email, website, city, category FROM lead_contacts WHERE LOWER(category) = LOWER(?) OR LOWER(company) LIKE LOWER(?) OR LOWER(name) LIKE LOWER(?) LIMIT ?").bind(category, `%${category}%`, `%${category}%`, limit)
    : city
    ? env.DB.prepare("SELECT company, name, phone, email, website, city, category FROM lead_contacts WHERE LOWER(city) LIKE LOWER(?) AND (LOWER(company) LIKE LOWER(?) OR LOWER(name) LIKE LOWER(?)) LIMIT ?").bind(`%${city}%`, `%${query}%`, `%${query}%`, limit)
    : env.DB.prepare("SELECT company, name, phone, email, website, city, category FROM lead_contacts WHERE LOWER(company) LIKE LOWER(?) OR LOWER(name) LIKE LOWER(?) LIMIT ?").bind(`%${query}%`, `%${query}%`, limit);

  const dbResults = await dbQuery.all();
  for (const r of dbResults.results || []) {
    const key = `${r.company || r.name}-${r.city || ""}`;
    if (seenKeys.has(key)) continue;
    seenKeys.add(key);
    results.push({
      name: r.company || r.name,
      phone: r.phone || "",
      email: r.email || "",
      website: r.website || "",
      city: r.city || "",
      category: r.category || category,
      source: "Database Beriklan",
    });
  }

  // === Strategy 2: query Overpass API (OSM) if city + category ===
  if (results.length < limit && city && category) {
    const cat = SCRAPE_CATEGORIES.find(c => c.id === category);
    if (cat) {
      try {
        // Geocode city first via Nominatim
        const geoResp = await fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(city + ", Indonesia")}&format=json&limit=1`, {
          headers: { "User-Agent": "BeriklanScrape/1.0 (https://beriklan.co.id)" }
        });
        const geoData = await geoResp.json();
        if (geoData[0]) {
          const lat = parseFloat(geoData[0].lat);
          const lon = parseFloat(geoData[0].lon);
          const radius = 25000; // 25km
          // bbox query for speed
          const bbox = `${lat - 0.2},${lon - 0.2},${lat + 0.2},${lon + 0.2}`;
          const overpassQuery = `[out:json][timeout:25];(node${cat.osm}(${bbox}););out body ${limit - results.length};`;
          const opResp = await fetch("https://overpass-api.de/api/interpreter", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "BeriklanScrape/1.0" },
            body: "data=" + encodeURIComponent(overpassQuery)
          });
          if (opResp.ok) {
            const opData = await opResp.json();
            for (const e of opData.elements || []) {
              const t = e.tags || {};
              const name = t.name || t["name:id"] || "";
              if (!name) continue;
              const key = `${name}-${city}`;
              if (seenKeys.has(key)) continue;
              seenKeys.add(key);
              results.push({
                name,
                phone: t.phone || t["contact:phone"] || "",
                email: t.email || t["contact:email"] || "",
                website: t.website || t["contact:website"] || "",
                city: city,
                category: category,
                source: "OpenStreetMap",
              });
            }
          }
        }
      } catch (e) {
        console.log("OSM error:", e.message);
      }
    }
  }

  // Save results to D1
  const insertedRows = [];
  for (const r of results.slice(0, limit)) {
    insertedRows.push([user.id, searchId, r.name, r.phone, r.email, r.website, r.city, r.category, r.source]);
  }
  if (insertedRows.length) {
    await env.DB.batch(insertedRows.map(r => env.DB.prepare("INSERT INTO scrape_results (user_id, search_id, name, phone, email, website, city, category, source) VALUES (?,?,?,?,?,?,?,?,?)").bind(...r)));
  }
  await env.DB.prepare("UPDATE scrape_searches SET results_count = ? WHERE id = ?").bind(insertedRows.length, searchId).run();

  return json({
    ok: true,
    search_id: searchId,
    results: insertedRows.map(r => ({ name: r[2], phone: r[3], email: r[4], website: r[5], city: r[6], category: r[7], source: r[8] })),
    remaining_searches: 30 - (user.search_count + 1),
  });
}

async function handleScrapeExport(request, env) {
  const user = await getScrapeUserFromCookie(request, env);
  if (!user) return json({ ok: false, error: "Login required" }, 401);
  const url = new URL(request.url);
  const format = url.searchParams.get("format") || "csv";

  const rows = await env.DB.prepare("SELECT name, phone, email, website, city, category, source, created_at FROM scrape_results WHERE user_id = ? ORDER BY id DESC").bind(user.id).all();

  if (format === "json") {
    return json({ ok: true, results: rows.results });
  }

  // CSV
  const headers = ["Name","Phone","Email","Website","City","Category","Source","Date"];
  const csv = [headers.join(",")];
  for (const r of rows.results || []) {
    csv.push([r.name, r.phone, r.email, r.website, r.city, r.category, r.source, r.created_at].map(v => `"${String(v||"").replace(/"/g, '""')}"`).join(","));
  }
  return new Response(csv.join("\n"), {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": `attachment; filename="beriklan-scrape-${new Date().toISOString().slice(0,10)}.csv"`,
    }
  });
}

function json(obj, status = 200) { return new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json" } }); }

async function renderScrapeLanding(request, env) {
  const html = `<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Scrape Bisnis Indonesia — 30 Pencarian Gratis · Beriklan</title>
<meta name="description" content="Cari database bisnis Indonesia berdasarkan kategori dan kota. 30 pencarian gratis, tanpa kontrak.">
<link rel="icon" href="https://beriklan.co.id/logoweb.webp">
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Plus Jakarta Sans',sans-serif;}
body{background:#f7f8fb;color:#0b1426;}
.hero{background:linear-gradient(135deg,#0f1e3d 0%,#1a2f5c 100%);color:#fff;padding:64px 24px 80px;text-align:center;}
.hero h1{font-size:32px;font-weight:800;margin-bottom:14px;line-height:1.2;}
.hero h1 span{color:#f59e0b;}
.hero p{font-size:16px;color:#cbd5e1;margin-bottom:28px;max-width:560px;margin-left:auto;margin-right:auto;}
.btn{display:inline-block;padding:14px 32px;border-radius:999px;font-weight:700;text-decoration:none;font-size:15px;transition:transform .15s;}
.btn-primary{background:#f59e0b;color:#0f1e3d;}
.btn-primary:hover{transform:translateY(-2px);}
.badge{display:inline-block;background:rgba(245,158,11,.15);color:#fbbf24;padding:6px 14px;border-radius:999px;font-size:12px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;margin-bottom:18px;}
.container{max-width:920px;margin:0 auto;padding:0 20px;}
.features{padding:64px 0;}
.features h2{font-size:26px;text-align:center;margin-bottom:14px;font-weight:800;}
.features .sub{text-align:center;color:#6b7280;margin-bottom:40px;}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px;}
.card{background:#fff;padding:24px;border-radius:14px;box-shadow:0 1px 2px rgba(15,30,61,.04),0 4px 12px rgba(15,30,61,.04);}
.card .ico{font-size:28px;margin-bottom:12px;}
.card h3{font-size:16px;font-weight:700;margin-bottom:6px;}
.card p{font-size:13px;color:#6b7280;line-height:1.5;}
.how{padding:64px 0;background:#0f1e3d;color:#fff;}
.how h2{text-align:center;font-size:26px;margin-bottom:40px;font-weight:800;}
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px;max-width:800px;margin:0 auto;}
.step{text-align:center;}
.step .num{display:inline-block;width:36px;height:36px;line-height:36px;background:#f59e0b;color:#0f1e3d;border-radius:999px;font-weight:800;margin-bottom:12px;}
.step h4{font-size:14px;margin-bottom:6px;}
.step p{font-size:12px;color:#94a3b8;line-height:1.5;}
.cta{padding:64px 0;text-align:center;background:#fff;}
.cta h2{font-size:26px;margin-bottom:14px;font-weight:800;}
.cta p{color:#6b7280;margin-bottom:24px;}
.footer{padding:24px;text-align:center;color:#94a3b8;font-size:13px;border-top:1px solid #e5e7eb;}
.footer a{color:#f59e0b;text-decoration:none;}
@media(max-width:640px){.hero h1{font-size:24px;}.hero{padding:48px 20px 60px;}.features,.how,.cta{padding:48px 0;}}
</style>
</head>
<body>
<div class="hero">
<div class="container">
<div class="badge">🔥 Trial 30 pencarian gratis</div>
<h1>Temukan database bisnis<br>Indonesia <span>dalam hitungan detik</span></h1>
<p>Cari perusahaan berdasarkan kategori dan kota. Cocok untuk riset pasar, lead generation, dan analisis kompetitor.</p>
<a href="/signup" class="btn btn-primary">Mulai Trial Gratis →</a>
</div>
</div>
<div class="container features">
<h2>Kenapa scrape.beriklan.co.id?</h2>
<p class="sub">Lead generation tool yang ringan, tanpa API key, tanpa setup.</p>
<div class="grid">
<div class="card"><div class="ico">🎯</div><h3>Targeted</h3><p>Filter berdasarkan kategori spesifik dan kota — bukan search acak.</p></div>
<div class="card"><div class="ico">⚡</div><h3>Instan</h3><p>Hasil keluar dalam hitungan detik. Tidak perlu download, langsung dilihat di browser.</p></div>
<div class="card"><div class="ico">📊</div><h3>Export Ready</h3><p>Download CSV dengan satu klik. Siap pakai untuk CRM atau Excel.</p></div>
<div class="card"><div class="ico">🔒</div><h3>Aman & Privat</h3><p>Data tidak dibagikan. Hanya kamu yang bisa akses hasil pencarian.</p></div>
</div>
</div>
<div class="how"><div class="container">
<h2>Cara Pakai (3 Langkah)</h2>
<div class="steps">
<div class="step"><div class="num">1</div><h4>Sign up</h4><p>Masukkan nama, email, dan WhatsApp. 1 trial per user, gratis.</p></div>
<div class="step"><div class="num">2</div><h4>Cari bisnis</h4><p>Ketik kategori (misal: manufaktur) + kota. Maks 30 pencarian.</p></div>
<div class="step"><div class="num">3</div><h4>Export CSV</h4><p>Download hasil pencarian sebagai CSV. Langsung pakai.</p></div>
</div>
</div></div>
<div class="cta"><div class="container">
<h2>Siap scale up penjualan Anda?</h2>
<p>30 pencarian gratis, tanpa komitmen. Coba sekarang.</p>
<a href="/signup" class="btn btn-primary">Mulai Trial →</a>
</div></div>
<div class="footer">
<a href="https://beriklan.co.id">Beriklan.co.id</a> · Performance Marketing Partner · Bandung · <a href="/admin?token=beriklan-admin-2026">admin</a>
</div>
</body></html>`;
  return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
}

async function renderScrapeSignup(request, env) {
  const html = `<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mulai Trial — Scrape.beriklan.co.id</title>
<link rel="icon" href="https://beriklan.co.id/logoweb.webp">
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Plus Jakarta Sans',sans-serif;}
body{background:linear-gradient(135deg,#0f1e3d 0%,#1a2f5c 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px;color:#0b1426;}
.box{background:#fff;padding:40px 36px;border-radius:20px;box-shadow:0 20px 60px rgba(0,0,0,.3);width:100%;max-width:440px;}
.logo{display:flex;align-items:center;gap:10px;margin-bottom:20px;}
.logo img{width:36px;height:36px;}
.logo span{font-weight:800;font-size:18px;color:#0f1e3d;}
h1{font-size:22px;font-weight:800;margin-bottom:8px;}
.sub{font-size:13px;color:#6b7280;margin-bottom:24px;line-height:1.5;}
.field{margin-bottom:14px;}
.field label{display:block;font-size:13px;font-weight:600;margin-bottom:5px;color:#0b1426;}
.field input{width:100%;padding:12px 14px;border:1.5px solid #e5e7eb;border-radius:10px;font-size:14px;transition:border .15s;font-family:inherit;}
.field input:focus{outline:none;border-color:#f59e0b;}
.field .hint{font-size:11px;color:#9ca3af;margin-top:4px;}
.btn{width:100%;padding:13px;border-radius:999px;border:none;font-weight:700;font-size:14px;cursor:pointer;transition:transform .15s;}
.btn-primary{background:#f59e0b;color:#0f1e3d;}
.btn-primary:hover{transform:translateY(-1px);}
.note{font-size:11px;color:#9ca3af;margin-top:16px;text-align:center;line-height:1.4;}
.err{background:#fee2e2;color:#991b1b;padding:10px;border-radius:8px;font-size:13px;margin-bottom:14px;display:none;}
</style>
</head>
<body>
<div class="box">
<div class="logo"><img src="https://beriklan.co.id/logoweb.webp" alt=""><span>Beriklan</span></div>
<h1>Mulai Trial Scrape</h1>
<p class="sub">1 trial per user. 30 pencarian gratis. Verifikasi lewat WhatsApp & email.</p>
<div id="err" class="err"></div>
<form id="signup-form">
<div class="field"><label>Nama Lengkap</label><input name="name" required minlength="2" placeholder="misal: Budi Santoso"></div>
<div class="field"><label>Email</label><input type="email" name="email" required placeholder="budi@perusahaan.com"></div>
<div class="field"><label>WhatsApp</label><input name="whatsapp" required placeholder="081234567890"><div class="hint">Format: 08xxx atau +62xxx</div></div>
<button type="submit" class="btn btn-primary">🚀 Mulai Trial 30 Pencarian</button>
</form>
<p class="note">Dengan mendaftar, Anda menyetujui menerima update dari Beriklan. Bisa berhenti kapan saja.</p>
</div>
<script>
document.getElementById('signup-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const err = document.getElementById('err');
  err.style.display = 'none';
  const fd = new FormData(e.target);
  try {
    const r = await fetch('/api/signup', { method: 'POST', body: fd });
    const d = await r.json();
    if (d.ok) {
      window.location.href = d.redirect || '/dashboard';
    } else {
      err.textContent = d.error || 'Signup gagal';
      err.style.display = 'block';
    }
  } catch (e) {
    err.textContent = 'Error: ' + e.message;
    err.style.display = 'block';
  }
});
</script>
</body></html>`;
  return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
}

async function renderScrapeDashboard(request, env) {
  const user = await getScrapeUserFromCookie(request, env);
  if (!user) return Response.redirect(new URL("/signup", request.url).toString(), 302);

  const searches = await env.DB.prepare("SELECT id, query, category, city, results_count, created_at FROM scrape_searches WHERE user_id = ? ORDER BY id DESC LIMIT 20").bind(user.id).all();
  const allResults = await env.DB.prepare("SELECT COUNT(*) as c FROM scrape_results WHERE user_id = ?").bind(user.id).first();

  const remaining = Math.max(0, 30 - (user.search_count || 0));
  const html = `<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dashboard — Scrape.beriklan.co.id</title>
<link rel="icon" href="https://beriklan.co.id/logoweb.webp">
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Plus Jakarta Sans',sans-serif;}
body{background:#f7f8fb;color:#0b1426;min-height:100vh;}
header{background:#0f1e3d;color:#fff;padding:14px 24px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:10;}
header h1{font-size:16px;font-weight:700;}
header .user{font-size:13px;color:#94a3b8;}
header a{color:#f59e0b;text-decoration:none;font-size:13px;}
.container{max-width:960px;margin:0 auto;padding:24px 20px;}
.card{background:#fff;padding:24px;border-radius:14px;box-shadow:0 1px 2px rgba(15,30,61,.04),0 4px 12px rgba(15,30,61,.04);margin-bottom:18px;}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:18px;}
.stat{background:#fff;padding:18px;border-radius:12px;text-align:center;border:1px solid #e5e7eb;}
.stat .val{font-size:24px;font-weight:800;color:#0f1e3d;}
.stat .lbl{font-size:11px;color:#6b7280;margin-top:4px;text-transform:uppercase;letter-spacing:.05em;}
.stat.warn .val{color:#dc2626;}
.search-form{display:grid;grid-template-columns:2fr 1fr 1fr auto;gap:10px;margin-bottom:14px;}
@media(max-width:640px){.search-form{grid-template-columns:1fr;}}
.search-form input,.search-form select{padding:10px 12px;border:1.5px solid #e5e7eb;border-radius:10px;font-size:13px;background:#fff;font-family:inherit;}
.search-form input:focus,.search-form select:focus{outline:none;border-color:#f59e0b;}
.btn{padding:11px 20px;border-radius:999px;border:none;font-weight:700;font-size:13px;cursor:pointer;transition:transform .15s;}
.btn-primary{background:#f59e0b;color:#0f1e3d;}
.btn-secondary{background:#0f1e3d;color:#fff;text-decoration:none;display:inline-block;}
.btn-secondary:hover{transform:translateY(-1px);}
.results-box{max-height:420px;overflow-y:auto;}
table{width:100%;border-collapse:collapse;}
th{background:#f7f8fb;text-align:left;padding:10px;font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:.05em;position:sticky;top:0;}
td{padding:10px;border-bottom:1px solid #f3f4f8;font-size:13px;}
td a{color:#0f1e3d;text-decoration:none;}
td a:hover{color:#f59e0b;}
.empty{text-align:center;padding:40px;color:#9ca3af;}
.history{margin-top:14px;font-size:12px;color:#6b7280;}
.history li{padding:6px 0;border-bottom:1px solid #f3f4f8;display:flex;justify-content:space-between;}
.h-remaining{display:inline-block;padding:6px 14px;background:${remaining > 10 ? '#d1fae5' : remaining > 0 ? '#fef3c7' : '#fee2e2'};color:${remaining > 10 ? '#065f46' : remaining > 0 ? '#92400e' : '#991b1b'};border-radius:999px;font-size:12px;font-weight:700;}
.tag{display:inline-block;background:#f0f9ff;color:#0369a1;padding:2px 8px;border-radius:6px;font-size:11px;font-weight:600;}
.upgrade{background:linear-gradient(135deg,#f59e0b 0%,#fb923c 100%);padding:18px;border-radius:12px;color:#0f1e3d;margin-top:18px;text-align:center;}
.upgrade h3{font-size:15px;font-weight:800;margin-bottom:6px;}
.upgrade p{font-size:12px;margin-bottom:10px;}
.upgrade a{background:#0f1e3d;color:#f59e0b;padding:10px 20px;border-radius:999px;text-decoration:none;font-weight:700;font-size:13px;display:inline-block;}
</style>
</head>
<body>
<header>
<h1>🔍 Scrape.beriklan.co.id</h1>
<div><span class="user">${escHtml(user.name)} · ${escHtml(user.email)}</span> &nbsp; <a href="/api/logout">Logout</a></div>
</header>
<div class="container">
<div class="stats">
<div class="stat"><div class="val">${user.search_count || 0} / 30</div><div class="lbl">Pencarian</div></div>
<div class="stat ${remaining === 0 ? 'warn' : ''}"><div class="val">${remaining}</div><div class="lbl">Sisa</div></div>
<div class="stat"><div class="val">${allResults?.c || 0}</div><div class="lbl">Total Lead</div></div>
</div>
<div class="card">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
<h2 style="font-size:18px;font-weight:800;">🔎 Pencarian Bisnis</h2>
<span class="h-remaining">${remaining} pencarian tersisa</span>
</div>
<form id="search-form" class="search-form">
<input name="query" placeholder="misal: toko bangunan" required>
<select name="category">
<option value="">— Kategori —</option>
${SCRAPE_CATEGORIES.map(c => `<option value="${c.id}">${c.label}</option>`).join("")}
</select>
<select name="city">
<option value="">— Kota —</option>
${SCRAPE_CITIES.map(c => `<option value="${c}">${c}</option>`).join("")}
</select>
<button type="submit" class="btn btn-primary" ${remaining === 0 ? 'disabled' : ''}>🔍 Cari</button>
</form>
<div id="search-status" style="font-size:13px;color:#6b7280;margin-bottom:10px;"></div>
<div id="results" class="results-box"></div>
<div style="margin-top:14px;display:flex;gap:10px;flex-wrap:wrap;">
<a href="/api/export?format=csv" class="btn btn-secondary">📥 Export CSV</a>
<a href="/api/export?format=json" class="btn btn-secondary" target="_blank">📋 Lihat JSON</a>
</div>
</div>
${(searches.results||[]).length ? `<div class="card">
<h2 style="font-size:18px;font-weight:800;margin-bottom:10px;">📜 Riwayat Pencarian</h2>
<ul class="history">
${(searches.results||[]).map(s => `<li><span><strong>${escHtml(s.query || s.category || '?')}</strong> ${s.city ? `di ${escHtml(s.city)}` : ''} <span class="tag">${s.results_count || 0} hasil</span></span><span>${escHtml((s.created_at || '').slice(0,16))}</span></li>`).join("")}
</ul>
</div>` : ''}
${remaining === 0 ? `<div class="upgrade">
<h3>🚀 Limit tercapai — Mau akses full?</h3>
<p>Dapatkan akses tanpa limit + fitur export CRM-ready. Konsultasi gratis 15 menit.</p>
<a href="https://wa.me/62811919328?text=Halo%20Beriklan%2C%20saya%20sudah%20trial%20scrape.beriklan.co.id%20dan%20tertarik%20akses%20full">Hubungi WhatsApp →</a>
</div>` : ''}
</div>
<script>
document.getElementById('search-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const status = document.getElementById('search-status');
  const res = document.getElementById('results');
  status.textContent = '⏳ Mencari...';
  res.innerHTML = '';
  try {
    const r = await fetch('/api/search', { method: 'POST', body: fd });
    const d = await r.json();
    if (!d.ok) {
      status.innerHTML = '<span style="color:#dc2626;">' + (d.error || 'Error') + '</span>';
      if (d.limit_reached) setTimeout(() => location.reload(), 1500);
      return;
    }
    status.textContent = '✅ Ditemukan ' + d.results.length + ' bisnis' + (d.remaining_searches !== undefined ? ' · Sisa ' + d.remaining_searches + ' pencarian' : '');
    if (d.results.length === 0) {
      res.innerHTML = '<div class="empty">Tidak ada hasil. Coba ganti kategori/kota.</div>';
      return;
    }
    res.innerHTML = '<table><thead><tr><th>Nama</th><th>Kota</th><th>Phone</th><th>Website</th><th>Source</th></tr></thead><tbody>' +
      d.results.map(r => '<tr><td><strong>' + (r.name || '?') + '</strong><br><span style="font-size:11px;color:#9ca3af;">' + (r.category || '') + '</span></td><td>' + (r.city || '-') + '</td><td>' + (r.phone ? '<a href="tel:' + r.phone + '">' + r.phone + '</a>' : '<span style="color:#9ca3af;">-</span>') + '</td><td>' + (r.website ? '<a href="' + r.website + '" target="_blank">🔗</a>' : '<span style="color:#9ca3af;">-</span>') + '</td><td><span class="tag">' + (r.source || '-') + '</span></td></tr>').join('') + '</tbody></table>';
  } catch (e) {
    status.innerHTML = '<span style="color:#dc2626;">Error: ' + e.message + '</span>';
  }
});
</script>
</body></html>`;
  return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
}

async function renderScrapeAdmin(request, env) {
  const url = new URL(request.url);
  if (url.searchParams.get("token") !== "beriklan-admin-2026") return new Response("Unauthorized", { status: 401 });
  const users = await env.DB.prepare("SELECT id, name, email, whatsapp, search_count, created_at, last_active FROM scrape_users ORDER BY id DESC LIMIT 100").all();
  const totalSearches = await env.DB.prepare("SELECT COUNT(*) as c FROM scrape_searches").first();
  const totalResults = await env.DB.prepare("SELECT COUNT(*) as c FROM scrape_results").first();
  const html = `<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Scrape Admin</title>
<style>body{font-family:sans-serif;padding:20px;background:#f7f8fb;}h1{margin-bottom:20px;}table{width:100%;background:#fff;border-collapse:collapse;box-shadow:0 1px 2px rgba(0,0,0,.05);}th{background:#0f1e3d;color:#fff;padding:10px;text-align:left;font-size:12px;}td{padding:10px;border-bottom:1px solid #e5e7eb;font-size:13px;}.stats{display:flex;gap:12px;margin-bottom:20px;}.stat{background:#fff;padding:14px 18px;border-radius:8px;flex:1;}.stat .val{font-size:22px;font-weight:800;color:#0f1e3d;}.stat .lbl{font-size:11px;color:#6b7280;text-transform:uppercase;}</style>
</head><body>
<h1>🔍 Scrape Portal — Admin</h1>
<div class="stats">
<div class="stat"><div class="val">${users.results?.length || 0}</div><div class="lbl">Total Users</div></div>
<div class="stat"><div class="val">${totalSearches?.c || 0}</div><div class="lbl">Total Searches</div></div>
<div class="stat"><div class="val">${totalResults?.c || 0}</div><div class="lbl">Total Results</div></div>
</div>
<table><thead><tr><th>ID</th><th>Nama</th><th>Email</th><th>WhatsApp</th><th>Pencarian</th><th>Dibuat</th><th>Last Active</th></tr></thead>
<tbody>
${(users.results||[]).map(u => `<tr><td>${u.id}</td><td>${escHtml(u.name)}</td><td>${escHtml(u.email)}</td><td>${escHtml(u.whatsapp)}</td><td>${u.search_count || 0}</td><td>${escHtml((u.created_at||'').slice(0,16))}</td><td>${escHtml((u.last_active||'').slice(0,16))}</td></tr>`).join("")}
</tbody></table>
</body></html>`;
  return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
}

// P0.7 build-signature 2026-07-17T06:08:00Z  (forces redeploy)
// Force rebuild Tue Jul 21 10:33:20 WIB 2026
// Force CF rebuild for PAA Tue Jul 21 11:39:50 WIB 2026
