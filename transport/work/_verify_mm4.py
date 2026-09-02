# -*- coding: utf-8 -*-
import os, glob, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
book = os.path.join(ROOT, "transport", "wiki", "tiddlers", "1 核心补充书籍", "MM4怪物图鉴4")
# 产物 tid 数（排除插图目录）
tids = []
for p in glob.glob(os.path.join(book, "**", "*.tid"), recursive=True):
    if "\\插图\\" in p.replace("/", "\\"):
        continue
    tids.append(p)
print("产物 tid 数(不含插图):", len(tids))
# 插图 jpg + meta
ill = os.path.join(book, "插图")
jpgs = [f for f in os.listdir(ill) if f.lower().endswith(".jpg")] if os.path.isdir(ill) else []
miss_meta = [f for f in jpgs if not os.path.isfile(os.path.join(ill, f + ".meta"))]
print("插图 jpg:", len(jpgs), " 缺meta:", len(miss_meta))
# 标题 h5 数量抽样
import collections
h5 = 0
for p in tids:
    h5 += open(p, encoding="utf-8").read().count("<h5>")
print("h5 总数:", h5)
