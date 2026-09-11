# -*- coding: utf-8 -*-
"""定位 6/7/9 转换中 tid 路径冲突（不同源映射到同一 .tid 文件）。"""
import csv
import os
from collections import defaultdict

FMP = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/work/final_mapping.csv"
WIKI = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/wiki/tiddlers"
SER = ["6 种族书", "7 扩展全新体系", "9 世设"]

tid_paths = defaultdict(list)
with open(FMP, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        src = r["源文件相对路径"]
        if src.split("\\")[0] not in SER:
            continue
        tid = os.path.splitext(src)[0] + ".tid"
        tid_paths[tid].append(src)

collisions = {k: v for k, v in tid_paths.items() if len(v) > 1}
print("tid 路径冲突数:", len(collisions))
for k, v in collisions.items():
    print("COLLIDE tid:", k)
    for s in v:
        print("   源:", s)

# 实际 tid 文件数
n = 0
for ser in SER:
    for _, _, fs in os.walk(os.path.join(WIKI, ser)):
        n += sum(1 for x in fs if x.endswith(".tid"))
print("实际 tid 文件数:", n)
