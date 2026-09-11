# -*- coding: utf-8 -*-
import csv, os, sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths as P

ROOT = P.ROOT
BOOKS = [
    r"4 阵营和位面\BoED崇善之书",
    r"4 阵营和位面\FC1深渊堕群",
    r"4 阵营和位面\FC2九狱君王",
    r"4 阵营和位面\PlH位面手册",
]
WIKI = os.path.join(ROOT, "transport", "wiki", "tiddlers")

rows = list(csv.DictReader(open(os.path.join(ROOT, "transport", "work", "final_mapping.csv"), encoding="utf-8-sig")))
for b in BOOKS:
    sub = [r for r in rows if r["源文件相对路径"].replace("/", "\\").startswith(b)]
    print(f"\n=== {b} ({len(sub)}) ===")
    for r in sub[:6]:
        print("   ", r["源文件相对路径"], "=>", r["Tiddler标题"], "|", r["标签"])
    roots = [r for r in sub if r["源文件相对路径"].replace("/", "\\").count("\\") == 2]
    print("   root-level:", [(r["源文件相对路径"], r["Tiddler标题"]) for r in roots])
    c = Counter(r["Tiddler标题"] for r in sub)
    dups = [k for k, v in c.items() if v > 1]
    if dups:
        print("   DUP TITLES:", dups[:10])
    # 是否已有 tid
    existing = 0
    for r in sub:
        tidrel = os.path.splitext(r["源文件相对路径"])[0] + ".tid"
        if os.path.isfile(os.path.join(WIKI, tidrel)):
            existing += 1
    print(f"   already-converted tids: {existing}/{len(sub)}")
