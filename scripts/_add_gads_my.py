#!/usr/bin/env python3
"""Add Google Ads conversion tracking (AW-18065868782) for WhatsApp clicks on beriklan.my.
- Adds gtag config for the Ads account + enhanced conversions flag.
- Adds gtag_report_conversion() helper (matches Google's snippet).
- Auto-fires a conversion (value 1000 IDR) on every WhatsApp link/button click.
Patches BOTH the static Layout.astro and the dynamic worker-entry.js fallback prefix.
"""
import sys

MY = "/Users/maabook/Desktop/beriklan.my/web"
AW = "AW-18065868782"
SEND_TO = "AW-18065868782/2EboCKa6odkcEO6PvaZD"

# ---- worker JS to append inside the single-quoted `gtm` string.
# MUST contain NO single quotes and NO backslashes (embedded in single-quoted JS literal).
ADD_WORKER = (
    'gtag("config","' + AW + '",{allow_enhanced_conversions:true});'
    'function gtag_report_conversion(url){var cb=function(){if(typeof(url)!="undefined"){window.location=url;}};'
    'gtag("event","conversion",{send_to:"' + SEND_TO + '",value:1000.0,currency:"IDR",event_callback:cb});return false;}'
    'document.addEventListener("click",function(e){var t=e.target;'
    'while(t&&t!==document.body){if(t.tagName==="A"||t.tagName==="BUTTON")break;t=t.parentElement;}'
    'if(!t||t===document.body)return;'
    'var href=((t.href||(t.getAttribute&&t.getAttribute("href"))||"")+"").toLowerCase();'
    'if(href.indexOf("wa.me/")===-1&&href.indexOf("whatsapp")===-1)return;'
    'try{gtag("event","conversion",{send_to:"' + SEND_TO + '",value:1000.0,currency:"IDR",transport_type:"beacon"});}catch(err){}'
    '},true);'
)


def patch(path, anchor, new, label):
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()
    if AW in txt:
        print("[SKIP] %s: already contains %s" % (label, AW))
        return
    n = txt.count(anchor)
    if n != 1:
        print("[FAIL] %s: expected 1 occurrence of anchor, found %d. Aborting." % (label, n))
        sys.exit(1)
    txt = txt.replace(anchor, new, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(txt)
    print("[OK]  %s: patched" % label)


# ===== 1) worker-entry.js gtm string =====
worker = MY + "/src/worker-entry.js"
w_anchor = r"gtag(\'config\',\'G-PBQF8MMN40\');" + "'"
w_new = r"gtag(\'config\',\'G-PBQF8MMN40\');" + ADD_WORKER + "'"
patch(worker, w_anchor, w_new, "worker-entry.js gtm")

# ===== 2) Layout.astro — add AW config into GA4 block =====
layout = MY + "/src/layouts/Layout.astro"
l_anchor_a = "gtag('config', 'G-PBQF8MMN40');"
l_new_a = (
    "gtag('config', 'G-PBQF8MMN40');\n"
    "\t\t\tgtag('config', '" + AW + "', { 'allow_enhanced_conversions': true });"
)

# ===== 3) Layout.astro — add dedicated Ads conversion script block =====
conversion_block = (
    "<!-- End Google tag -->\n\n"
    "\t\t<!-- Google Ads conversion (WhatsApp click) - " + AW + " -->\n"
    "\t\t<script is:inline>\n"
    "\t\t\tfunction gtag_report_conversion(url) {\n"
    "\t\t\t\tvar callback = function () { if (typeof(url) != 'undefined') { window.location = url; } };\n"
    "\t\t\t\tgtag('event', 'conversion', { 'send_to': '" + SEND_TO + "', 'value': 1000.0, 'currency': 'IDR', 'event_callback': callback });\n"
    "\t\t\t\treturn false;\n"
    "\t\t\t}\n"
    "\t\t\tdocument.addEventListener('click', function (e) {\n"
    "\t\t\t\tvar t = e.target;\n"
    "\t\t\t\twhile (t && t !== document.body) { if (t.tagName === 'A' || t.tagName === 'BUTTON') break; t = t.parentElement; }\n"
    "\t\t\t\tif (!t || t === document.body) return;\n"
    "\t\t\t\tvar href = ((t.href || (t.getAttribute && t.getAttribute('href')) || '') + '').toLowerCase();\n"
    "\t\t\t\tif (href.indexOf('wa.me/') === -1 && href.indexOf('whatsapp') === -1) return;\n"
    "\t\t\t\ttry { gtag('event', 'conversion', { 'send_to': '" + SEND_TO + "', 'value': 1000.0, 'currency': 'IDR', 'transport_type': 'beacon' }); } catch (err) {}\n"
    "\t\t\t}, true);\n"
    "\t\t</script>\n"
    "\t\t<!-- End Google Ads conversion -->"
)
l_anchor_b = "<!-- End Google tag -->"

# Apply both Layout edits (guarded by AW-not-present check inside patch()).
with open(layout, "r", encoding="utf-8") as f:
    ltxt = f.read()
if AW in ltxt:
    print("[SKIP] Layout.astro: already contains %s" % AW)
else:
    if ltxt.count(l_anchor_a) != 1:
        print("[FAIL] Layout.astro: anchor A count != 1"); sys.exit(1)
    if ltxt.count(l_anchor_b) != 1:
        print("[FAIL] Layout.astro: anchor B count != 1"); sys.exit(1)
    ltxt = ltxt.replace(l_anchor_a, l_new_a, 1)
    ltxt = ltxt.replace(l_anchor_b, conversion_block, 1)
    with open(layout, "w", encoding="utf-8") as f:
        f.write(ltxt)
    print("[OK]  Layout.astro: patched (AW config + conversion block)")

print("DONE")
