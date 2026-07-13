// Minimal Worker entry — serves static assets from dist/ via ASSETS binding.
// Any request that doesn't match a Worker route returns the static file.
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    try {
      // Try to serve from assets directory
      return await env.ASSETS.fetch(request);
    } catch (e) {
      // Fallback for routes that don't have static files
      return new Response('Not Found', { status: 404 });
    }
  },
};
