#!/usr/bin/env python3
"""Add a SECOND GA4 property (G-PBQF8MMN40) alongside the existing G-7RB4G5GC1X
on beriklan.my — dual-tag. One gtag.js loader is enough; we add one extra
gtag('config', ...) call in both the static Layout and the dynamic worker template.
"""
import sys

NEW_ID = "G-PBQF8MMN40"
OLD_ID = "G-7RB4G5GC1X"

MY = "/Users/maabook/Desktop/beriklan.my/web"

def patch(path, old, new, label):
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()
    if new in txt and old not in txt:
        print(f"[SKIP] {label}: already patched")
        return
    n = txt.count(old)
    if n != 1:
        print(f"[FAIL] {label}: expected 1 occurrence of anchor, found {n}. Aborting.")
        sys.exit(1)
    txt = txt.replace(old, new, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(txt)
    print(f"[OK]  {label}: added {NEW_ID}")

# 1. Static Astro Layout (tabs indentation, 3 tabs)
layout = f"{MY}/src/layouts/Layout.astro"
old_l = f"gtag('config', '{OLD_ID}');"
new_l = f"gtag('config', '{OLD_ID}');\n\t\t\tgtag('config', '{NEW_ID}');"
patch(layout, old_l, new_l, "Layout.astro")

# 2. Dynamic worker blog template (single-quote-escaped JS string literal)
worker = f"{MY}/src/worker-entry.js"
old_w = "gtag(\\'config\\',\\'" + OLD_ID + "\\');"
new_w = old_w + "gtag(\\'config\\',\\'" + NEW_ID + "\\');"
patch(worker, old_w, new_w, "worker-entry.js")

print("DONE")
