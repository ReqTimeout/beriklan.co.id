// src/worker-entry.js
var worker_entry_default = {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    try {
      return await env.ASSETS.fetch(request);
    } catch (e) {
      return new Response("Not Found", { status: 404 });
    }
  }
};
export {
  worker_entry_default as default
};
//# sourceMappingURL=worker-entry.js.map
