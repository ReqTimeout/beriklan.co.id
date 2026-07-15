// Worker entry — serves static assets + handles admin API routes
// Bindings: ASSETS (static), DB (D1 sqlite), AI (Cloudflare Workers AI)

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Admin-Token",
};

function json(data, init = {}) {
  return new Response(JSON.stringify(data, null, 2), {
    ...init,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      ...CORS_HEADERS,
      ...(init.headers || {}),
    },
  });
}

function notFound(msg = "Not Found") {
  return json({ error: msg }, { status: 404 });
}

function unauthorized(msg = "Unauthorized") {
  return json({ error: msg }, { status: 401 });
}

// ---------- /api/llm/chat — Cloudflare Workers AI proxy ----------
async function handleLLMChat(request, env) {
  if (request.method !== "POST") {
    return json({ error: "Method not allowed. Use POST." }, { status: 405 });
  }
  try {
    const body = await request.json();
    const messages = body.messages || [];
    if (!Array.isArray(messages) || messages.length === 0) {
      return json({ error: "messages array required" }, { status: 400 });
    }
    // Default model: Llama 3 8B Instruct (free via CF Workers AI)
    const model = body.model || "@cf/meta/llama-3-8b-instruct";

    const response = await env.AI.run(model, {
      messages,
      max_tokens: body.max_tokens || 2048,
      temperature: body.temperature ?? 0.7,
      top_p: body.top_p ?? 0.9,
    });

    return json({
      content: response.response || "",
      model_used: model,
      usage: response.usage || {},
    });
  } catch (e) {
    return json({ error: String(e), message: e.message }, { status: 500 });
  }
}

// ---------- /api/db/query — D1 proxy for Python scripts ----------
async function handleDBQuery(request, env, ctx) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token") || request.headers.get("X-Admin-Token");
  if (token !== (env.ADMIN_TOKEN || "beriklan-admin-2026")) {
    return unauthorized("Bad admin token");
  }
  if (request.method !== "POST") {
    return json({ error: "Method not allowed. Use POST." }, { status: 405 });
  }
  try {
    const body = await request.json();
    const sql = body.sql;
    const params = body.params || [];
    if (!sql) return json({ error: "sql required" }, { status: 400 });

    let result;
    if (sql.trim().toUpperCase().startsWith("SELECT") || sql.trim().toUpperCase().startsWith("PRAGMA")) {
      result = await env.DB.prepare(sql).bind(...params).all();
    } else {
      result = await env.DB.prepare(sql).bind(...params).run();
    }
    return json({ success: true, result });
  } catch (e) {
    return json({ error: String(e), message: e.message }, { status: 500 });
  }
}

// ---------- /api/db/stats — KPI for admin dashboard ----------
async function handleDBStats(request, env) {
  try {
    const counts = {};
    const tables = ["keyword_queue", "articles", "rank_snapshots", "index_log",
                   "trending_log", "audit_log", "automation_health", "settings",
                   "api_keys", "conversion_log", "manual_review", "request_queue", "blocklist"];
    for (const t of tables) {
      try {
        const r = await env.DB.prepare(`SELECT COUNT(*) as n FROM ${t}`).first();
        counts[t] = r.n;
      } catch (e) {
        counts[t] = "error";
      }
    }
    return json({ timestamp: new Date().toISOString(), counts });
  } catch (e) {
    return json({ error: String(e) }, { status: 500 });
  }
}

// ---------- Main fetch handler ----------
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    try {
      // CORS preflight
      if (request.method === "OPTIONS") {
        return new Response(null, { status: 204, headers: CORS_HEADERS });
      }

      // API routes
      if (url.pathname === "/api/llm/chat") return handleLLMChat(request, env);
      if (url.pathname === "/api/db/query") return handleDBQuery(request, env, ctx);
      if (url.pathname === "/api/db/stats") return handleDBStats(request, env);

      // Static assets from dist/
      return await env.ASSETS.fetch(request);
    } catch (e) {
      return new Response("Not Found", { status: 404 });
    }
  },
};
