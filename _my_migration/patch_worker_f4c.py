#!/usr/bin/env python3
"""F4-fix: tambah /api/cron/tick — HTTP trigger untuk hourly cron bundle.
Alasan: akun CF free sudah pakai 5/5 cron trigger (beriklan-app 3 + beriklanweb 2),
jadi cron `beriklanmy` tidak bisa attach. Endpoint ini dipanggil cron-job.org tiap jam.
"""
import sys

PATH = "/Users/maabook/Desktop/beriklan.my/web/src/worker-entry.js"
src = open(PATH).read()

ANCHOR = '''    if (path === "/api/cron/indexing" || path === "/api/cron/indexing/") {'''
NEW = '''    if (path === "/api/cron/tick" || path === "/api/cron/tick/") {
      // Fallback trigger via cron-job.org — akun CF free sudah penuh 5 cron trigger.
      // Menjalankan bundle hourly yang sama persis dengan scheduled("0 * * * *").
      const token = url.searchParams.get("token") || "";
      if (token !== env.ADMIN_TOKEN) return new Response("Unauthorized", { status: 401 });
      await this.scheduled({ cron: "0 * * * *", scheduledTime: Date.now() }, env, ctx);
      return new Response(JSON.stringify({ ok: true, dispatched: "hourly cron bundle", timestamp: new Date().toISOString() }), { headers: { "Content-Type": "application/json" } });
    }
    if (path === "/api/cron/indexing" || path === "/api/cron/indexing/") {'''

if "/api/cron/tick" in src:
    print("already patched — skip")
    sys.exit(0)
n = src.count(ANCHOR)
if n != 1:
    print(f"FAIL anchor count {n}")
    sys.exit(1)
src = src.replace(ANCHOR, NEW, 1)
open(PATH, "w").write(src)
print("tick endpoint added, OK")
