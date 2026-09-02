# -*- coding: utf-8 -*-
"""扫描 XPH 产物的 Word 噪音分布，评估是否需要专项清洗。"""
import _paths as P
import collections
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

PREFIX = "1 核心补充书籍\\XPH扩展灵能手册"
XPH = os.path.join(P.WIKI_TIDDLERS, PREFIX)

MARKERS = {
    "o:p非空": re.compile(r"<o:p[^>]*>(?!\s*</o:p>)", re.I),
    "StartFrag": re.compile(r"<!--\s*StartFragment", re.I),
    "断裂span": re.compile(r"<span\s*\n", re.I),
    "font": re.compile(r"<font", re.I),
    "mso-": re.compile(r"mso-", re.I),
}


def body_of(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    return "\n".join(lines[5:])


files = []
for dirpath, dirnames, filenames in os.walk(XPH):
    dirnames.sort()
    for f in sorted(filenames):
        if f.lower().endswith(".tid"):
            files.append(os.path.relpath(os.path.join(dirpath, f), XPH))

print(f"总计 {len(files)} 个 tid\n")
cols = list(MARKERS)
header = f"{'子目录':10s} {'文件':>4s} " + " ".join(f"{k:>10s}" for k in cols) + f"{'均nbsp':>8s}"
print(header)
print("-" * len(header))

by_dir = collections.defaultdict(list)
for rel in files:
    d = rel.split(os.sep)[0] if os.sep in rel else "."
    by_dir[d].append(rel)

total = collections.Counter()
for d in sorted(by_dir):
    rels = by_dir[d]
    cnt = collections.Counter()
    nb = 0
    for rel in rels:
        b = body_of(os.path.join(XPH, rel))
        for k in cols:
            if MARKERS[k].search(b):
                cnt[k] += 1
                total[k] += 1
        nb += b.count("&nbsp;")
    print(f"{d:10s} {len(rels):4d} " + " ".join(f"{cnt[k]:10d}" for k in cols)
          + f"{nb // max(1, len(rels)):8d}")

print("-" * len(header))
print(f"{'合计(文件数)':10s} {len(files):4d} " + " ".join(f"{total[k]:10d}" for k in cols))

print("\n=== 噪音最重文件 top12（按噪音出现总次数）===")
rows = []
for rel in files:
    b = body_of(os.path.join(XPH, rel))
    s = sum(len(MARKERS[k].findall(b)) for k in cols)
    rows.append((s, rel))
rows.sort(reverse=True)
for s, rel in rows[:12]:
    print(f"   {s:6d}  {rel}")
