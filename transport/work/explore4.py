# -*- coding: utf-8 -*-
import csv, os, sys, re, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths as P

ROOT = P.ROOT
BOOKS = [
    r"4 阵营和位面\BoED崇善之书",
    r"4 阵营和位面\FC1深渊堕群",
    r"4 阵营和位面\FC2九狱君王",
    r"4 阵营和位面\PlH位面手册",
]

# 1. mapping count
mapcsv = os.path.join(ROOT, "transport", "work", "final_mapping.csv")
rows = list(csv.DictReader(open(mapcsv, encoding="utf-8-sig")))
print("=== mapping count (final_mapping.csv) ===")
for b in BOOKS:
    c = sum(1 for r in rows if r["源文件相对路径"].replace("/", "\\").startswith(b))
    print(f"  {b}: {c}")

# also check hhc_mapping.csv
hhccsv = os.path.join(ROOT, "transport", "work", "hhc_mapping.csv")
if os.path.isfile(hhccsv):
    hrows = list(csv.DictReader(open(hhccsv, encoding="utf-8-sig")))
    print("=== hhc mapping count ===")
    for b in BOOKS:
        c = sum(1 for r in hrows if (r["源文件相对路径"] or "").replace("/", "\\").startswith(b))
        print(f"  {b}: {c}")

# 2. walk + noise scan
NOISE = ["DND3R-FEEDBACK", "StartFragment", "<o:p>", "mso-spacerun", "<script", "<style", ".css", "var ", "function("]
for b in BOOKS:
    sd = os.path.join(ROOT, b)
    htms = []
    for root, dirs, fs in os.walk(sd):
        for x in fs:
            if x.lower().endswith((".htm", ".html")):
                htms.append(os.path.relpath(os.path.join(root, x), sd).replace("/", "\\"))
    htms.sort()
    print(f"\n=== {b} : {len(htms)} htm ===")
    for h in htms[:20]:
        print("   ", h)
    if len(htms) > 20:
        print(f"   ... (+{len(htms)-20} more)")
    cnt = collections.Counter()
    scanned = htms[:150]
    for h in scanned:
        raw = open(os.path.join(sd, h), "rb").read(300000)
        for m in NOISE:
            if m.encode() in raw:
                cnt[m] += 1
    print(f"  noise hits (scanned {len(scanned)}): {dict(cnt)}")
