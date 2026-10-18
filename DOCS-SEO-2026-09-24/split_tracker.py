#!/usr/bin/env python3
"""Satu-off: pisahkan TASKTRACKER-SEO-MASTER.md menjadi baris co.id vs .my.
Klasifikasi per baris tabel `| # | Task | Domain | ...` berdasarkan kolom Domain.
Output: /tmp-like file di folder ini (.split-coid-rows.md / .split-my-rows.md)
+ report jumlah ID per output supaya tidak ada task hilang."""
import re, sys, os

SRC = os.path.join(os.path.dirname(__file__), "TASKTRACKER-SEO-MASTER.md")
OUT_COID = os.path.join(os.path.dirname(__file__), ".split-coid-rows.md")
OUT_MY = os.path.join(os.path.dirname(__file__), ".split-my-rows.md")

row_re = re.compile(r"^\|\s*([0-9]+\.[0-9]+[a-e]?)\s*\|")

def domain_of(cells):
    return cells[3].strip() if len(cells) > 3 else ""

def status_of(cells):
    return cells[4] if len(cells) > 4 else ""

sections = []  # (header_lines, rows) — kita group per heading
cur_header, cur_rows = [], []
with open(SRC, encoding="utf-8") as f:
    lines = f.readlines()

for ln in lines:
    m = row_re.match(ln)
    if m:
        cells = [c for c in ln.rstrip("\n").split("|")]
        d = domain_of(cells)
        is_my_only = (d == ".my") or ("DEFERRED" in status_of(cells) and "co.id" not in d)
        (cur_rows.append((ln, "my" if is_my_only else "coid")))
    else:
        if cur_rows:
            sections.append((cur_header, cur_rows)); cur_header, cur_rows = [], []
        cur_header.append(ln)
if cur_rows:
    sections.append((cur_header, cur_rows))

def emit(keep, outpath):
    ids = []
    with open(outpath, "w", encoding="utf-8") as o:
        for header, rows in sections:
            kept = [r for r in rows if r[1] == keep]
            if not kept:
                continue
            o.writelines(header)
            # print hanya baris `---` separator terakhir bila section ikut (header sudah termasuk judul)
            for line, tag in rows:
                if tag == keep:
                    o.write(line)
                    ids.append(row_re.match(line).group(1))
    return ids

coid_ids = emit("coid", OUT_COID)
my_ids = emit("my", OUT_MY)

all_ids = [i for h, rs in sections for r, _ in rs if (i := row_re.match(r).group(1))]
print("TOTAL rows di master :", len(all_ids))
print("co.id rows           :", len(coid_ids))
print(".my rows             :", len(my_ids))
print("hilang (harus 0)     :", set(all_ids) - set(coid_ids) - set(my_ids))
print("overlap (both dapat) :", sorted(set(coid_ids) & set(my_ids)))
print("--- MY IDS ---"); print(", ".join(my_ids))
