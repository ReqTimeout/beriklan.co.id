// Worker entry — serves static assets from dist/ via ASSETS binding,
// with explicit fallbacks for verification files.
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // IndexNow key file — served directly to bypass assets binding issues
    const INDEXNOW_KEY = "2dac33f6303f4041b9ec7e2f2910ea80";
    if (path === `/${INDEXNOW_KEY}.txt`) {
      return new Response(INDEXNOW_KEY, {
        headers: {
          "Content-Type": "text/plain; charset=utf-8",
          "Cache-Control": "public, max-age=86400",
        },
      });
    }

    // Force fresh rebuild — bumped 2026-07-15 to include pillar pages
    console.log(`[worker] serving: ${path}`);

    // Try static assets
    try {
      return await env.ASSETS.fetch(request);
    } catch (e) {
      return new Response("Not Found", { status: 404 });
    }
  },
};
