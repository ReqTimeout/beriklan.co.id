// Worker entry — Cloudflare Worker for beriklan.co.id
//
// Features:
//   1. Static asset serving via ASSETS binding
//   2. IndexNow key file
//   3. Manual cron endpoints (called by external cron service)
//      - GET /api/health
//      - POST /api/cron/indexing?token=... (manual trigger by cron-job.org)

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

    // Endpoints
    if (path === "/api/health" || path === "/api/health/") {
      return await handleHealth(env);
    }
    if (path === "/api/cron/indexing" || path === "/api/cron/indexing/") {
      return await handleIndexingCron(request, env);
    }

    // Static assets fallback
    try {
      return await env.ASSETS.fetch(request);
    } catch (e) {
      return new Response("Not Found", { status: 404 });
    }
  },

  async scheduled(event, env, ctx) {
    console.log("[scheduled] disabled (use /api/cron/indexing endpoint)");
    return;
  },
};

async function handleHealth(env) {
  try {
    const pending = await getPendingCount(env);
    return new Response(JSON.stringify({
      status: "ok",
      worker: "beriklanweb",
      pending_count: pending,
      timestamp: new Date().toISOString(),
    }), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ error: String(e) }), { status: 500 });
  }
}

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
      stack: e.stack?.split("\n").slice(0, 5).join("\n"),
    }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
}

async function getPendingCount(env) {
  try {
    const { results } = await env.DB.prepare(
      `SELECT COUNT(*) as n FROM pending_indexing WHERE status='pending'`
    ).all();
    return results[0]?.n || 0;
  } catch (e) {
    return -1;
  }
}

async function runIndexingPipeline(env, debug = false) {
  const INDEXNOW_KEY = "2dac33f6303f4041b9ec7e2f2910ea80";
  const errors = [];

  // 1. Get pending URLs from D1
  let pending = [];
  try {
    const { results } = await env.DB.prepare(
      `SELECT url FROM pending_indexing
       WHERE status = 'pending'
       ORDER BY created_at ASC
       LIMIT 200`
    ).all();
    pending = results.map(r => r.url);
  } catch (e) {
    errors.push({stage: "d1_query", error: e.message});
  }

  if (pending.length === 0) {
    return { google_ok: 0, google_fail: 0, indexnow_engines: 0, urls: 0, errors, had_errors: errors.length > 0 };
  }

  let google_ok = 0, google_fail = 0, indexnow_engines = 0;

  // 2. Submit to Google Indexing API (if secret set)
  if (env.GSC_SERVICE_ACCOUNT_JSON) {
    let token = null;
    try {
      const sa = JSON.parse(env.GSC_SERVICE_ACCOUNT_JSON);
      token = await getGoogleAccessToken(sa);
    } catch (e) {
      errors.push({stage: "google_auth", error: e.message});
    }

    if (token) {
      for (const url of pending) {
        try {
          const resp = await fetch("https://indexing.googleapis.com/v3/urlNotifications:publish", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${token}`,
              "Content-Type": "application/json",
            },
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
            errors.push({stage: "google_quota", message: "Daily quota hit"});
            break;
          } else {
            google_fail++;
            const body = await resp.text();
            errors.push({stage: "google_publish", url, status: resp.status, body: body.slice(0, 200)});
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

  // 3. IndexNow submission
  try {
    const urlList = pending.map(u => u.replace("://beriklan.co.id", "://www.beriklan.co.id"));
    const payload = {
      host: "beriklan.co.id",
      key: INDEXNOW_KEY,
      keyLocation: `https://www.beriklan.co.id/${INDEXNOW_KEY}.txt`,
      urlList,
    };
    const engines = [
      "https://api.indexnow.org/indexnow",
      "https://www.bing.com/indexnow",
    ];
    for (const ep of engines) {
      try {
        const resp = await fetch(ep, {
          method: "POST",
          headers: { "Content-Type": "application/json; charset=utf-8" },
          body: JSON.stringify(payload),
        });
        if (resp.ok || resp.status === 202) indexnow_engines++;
      } catch (e) {
        errors.push({stage: "indexnow", engine: ep, error: e.message});
      }
    }
  } catch (e) {
    errors.push({stage: "indexnow_outer", error: e.message});
  }

  // 4. Log
  try {
    await env.DB.prepare(
      `INSERT INTO cron_logs (timestamp, google_ok, google_fail, indexnow_ok, indexnow_fail, urls_processed)
       VALUES (datetime('now'), ?, ?, ?, 0, ?)`
    ).bind(google_ok, google_fail, indexnow_engines, pending.length).run();
  } catch (e) {}

  return {
    google_ok, google_fail, indexnow_engines, urls: pending.length,
    errors: debug ? errors : undefined,
    had_errors: errors.length > 0,
  };
}

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

  const headerB64 = base64urlEncode(JSON.stringify(header));
  const claimB64 = base64urlEncode(JSON.stringify(claim));
  const signatureInput = `${headerB64}.${claimB64}`;

  const privateKey = await importPrivateKey(sa.private_key);
  const signatureBuf = await crypto.subtle.sign(
    { name: "RSASSA-PKCS1-v1_5" }, privateKey,
    new TextEncoder().encode(signatureInput)
  );
  const signatureB64 = base64urlEncode(arrayBufferToBase64(signatureBuf));
  const jwt = `${signatureInput}.${signatureB64}`;

  const resp = await fetch(sa.token_uri, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${jwt}`,
  });
  if (!resp.ok) {
    const body = await resp.text();
    throw new Error(`Token exchange failed: ${resp.status} - ${body.slice(0, 200)}`);
  }
  const data = await resp.json();
  return data.access_token;
}

async function importPrivateKey(pem) {
  const b64 = pem
    .replace(/-----BEGIN PRIVATE KEY-----/, "")
    .replace(/-----END PRIVATE KEY-----/, "")
    .replace(/\s+/g, "");
  const binary = base64ToArrayBuffer(b64);
  return await crypto.subtle.importKey(
    "pkcs8", binary,
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false, ["sign"]
  );
}

function base64urlEncode(str) {
  let b64 = typeof str === "string" ? btoa(str) : arrayBufferToBase64(str);
  return b64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function arrayBufferToBase64(buf) {
  const bytes = new Uint8Array(buf);
  let binary = "";
  for (const b of bytes) binary += String.fromCharCode(b);
  return btoa(binary);
}

function base64ToArrayBuffer(b64) {
  const binary = atob(b64);
  const buf = new ArrayBuffer(binary.length);
  const view = new Uint8Array(buf);
  for (let i = 0; i < binary.length; i++) view[i] = binary.charCodeAt(i);
  return buf;
}
